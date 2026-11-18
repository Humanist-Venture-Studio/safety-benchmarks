"""Scenario-grouped fitting, costed subset selection and out-of-fold predictions."""

import argparse
import hashlib
import json
import math
import random
import time
from collections import defaultdict
from pathlib import Path

from common import DATA, WORK, messages_from_tsv, read_tsv, require

MODELS = WORK / "models"


def transcript(row):
    return json.dumps(messages_from_tsv(row), ensure_ascii=False, separators=(",", ":"))


def options(description):
    p = argparse.ArgumentParser(description=description)
    p.add_argument(
        "--source", type=Path, required=True, help="local upstream checkpoint"
    )
    p.add_argument("--data", type=Path, default=DATA)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--tier", choices=["spark", "flash", "maxx"], default="spark")
    p.add_argument("--seconds", type=float, help="optimization and early-stop budget")
    p.add_argument("--epochs", type=int, default=2)
    p.add_argument("--lr", type=float, default=3e-5)
    p.add_argument("--positive-weight", type=float, default=3)
    p.add_argument("--batch", type=int, default=4)
    p.add_argument("--seed", type=int, default=20261117)
    p.add_argument("--max-length", type=int, default=2048)
    p.add_argument(
        "--fold", type=int, help="withhold this train-only fold for OOF predictions"
    )
    p.add_argument("--folds", type=int, default=5)
    p.add_argument(
        "--oof", type=Path, nargs="+", help="one round-one OOF JSON per fold"
    )
    p.add_argument(
        "--extra-copies",
        type=int,
        default=1,
        help="extra occurrences of missed training rows",
    )
    p.add_argument("--device", choices=["cpu", "mps"], default="mps")
    return p


def prepare(a):
    import torch

    require(
        a.out.resolve().is_relative_to(MODELS.resolve()),
        "output must be under ~/klara-tiers/models",
    )
    require(
        a.batch > 0
        and a.epochs > 0
        and a.positive_weight > 0
        and a.lr > 0
        and a.max_length > 0
        and a.extra_copies >= 0,
        "invalid fit settings",
    )
    if a.seconds is None:
        a.seconds = {"spark": 1200, "flash": 5400, "maxx": 10800}[a.tier]
        if a.fold is not None:
            a.seconds /= 2 * a.folds
        elif a.oof:
            a.seconds /= 2
    require(a.seconds > 0 and a.folds >= 2, "invalid time or fold count")
    if a.fold is not None:
        require(
            not a.oof
            and not getattr(a, "init_adapter", None)
            and not getattr(a, "init_checkpoint", None),
            "OOF models must start independently from upstream weights",
        )
    a._started = time.monotonic()
    a.out.mkdir(parents=True, exist_ok=False)
    torch.manual_seed(a.seed)
    if a.device == "mps":
        require(torch.backends.mps.is_available(), "MPS unavailable")
    return sorted(
        (r for r in read_tsv(a.data) if r["split"] == "train"),
        key=lambda r: r["row_id"],
    )


def group_order(rows, seed):
    """Interleave randomized scenario strata at evenly spaced quantiles."""
    groups = defaultdict(list)
    for row in rows:
        groups[row["scenario_id"]].append(row)
    strata = defaultdict(list)
    for key, group in sorted(groups.items()):
        first = group[0]
        strata[first["scenario_kind"], first["grade_band"]].append(key)
    rng = random.Random(seed)
    ranks = []
    for keys in strata.values():
        rng.shuffle(keys)
        offset = rng.random()
        ranks.extend(((i + offset) / len(keys), key) for i, key in enumerate(keys))
    return [key for _, key in sorted(ranks)]


def partition(rows, a):
    order = group_order(rows, a.seed)
    require(
        len(order) >= 3 and len({r["row_id"] for r in rows}) == len(rows),
        "insufficient or duplicate training data",
    )
    # Assign within each stratum. Taking every kth element of an interleaved
    # order can put all ordinary scenarios in one fold and all risks in another.
    strata = defaultdict(set)
    for row in rows:
        strata[row["scenario_kind"], row["grade_band"]].add(row["scenario_id"])
    rng = random.Random(a.seed)
    loads = [0] * a.folds
    folds = {}
    for _, keys in sorted(strata.items()):
        keys = sorted(keys)
        rng.shuffle(keys)
        indices = sorted(range(a.folds), key=lambda i: (loads[i], rng.random()))
        for j, key in enumerate(keys):
            fold = indices[j % a.folds]
            folds[key] = fold
            loads[fold] += 1
    if a.fold is not None:
        require(0 <= a.fold < a.folds <= len(order), "invalid fold")
    eligible = [r for r in rows if folds[r["scenario_id"]] != a.fold]
    order = group_order(eligible, a.seed + 1)
    n = max(1, round(0.1 * len(order)))
    dev_ids = set(order[:n])
    train = [r for r in eligible if r["scenario_id"] not in dev_ids]
    dev = [r for r in eligible if r["scenario_id"] in dev_ids]
    held = [r for r in rows if folds[r["scenario_id"]] == a.fold]
    return train, dev, held, folds


def fingerprint(rows):
    return hashlib.sha256(
        json.dumps(rows, sort_keys=True, ensure_ascii=False).encode()
    ).hexdigest()


def missed_ids(paths, rows, folds, a):
    if not paths:
        return set()
    require(a.fold is None, "OOF fits must be independent first-round fits")
    found, bad = set(), set()
    signature = fingerprint(rows)
    for path in paths:
        doc = json.loads(path.read_text())
        require(
            doc["train_sha256"] == signature
            and doc["seed"] == a.seed
            and doc["folds"] == a.folds,
            "OOF training data or split mismatch",
        )
        require(doc["source"] == str(a.source.resolve()), "OOF model source mismatch")
        held = {r["row_id"]: r for r in rows if folds[r["scenario_id"]] == doc["fold"]}
        require(
            set(doc["fit_scenarios"]).isdisjoint(
                r["scenario_id"] for r in held.values()
            ),
            "OOF scenario leakage",
        )
        require(
            set(doc["predictions"]) == held.keys() and not found.intersection(held),
            "wrong OOF membership",
        )
        for key, p in doc["predictions"].items():
            require(0 <= p <= 1, "invalid OOF probability")
            if int(p >= 0.5) != int(held[key]["is_unsafe"]):
                bad.add(key)
        found.update(held)
    require(found == {r["row_id"] for r in rows}, "incomplete OOF coverage")
    return bad


def fit(model, tokenizer, encode, forward, rows, a):
    """forward returns class logits and the unweighted per-example training losses."""
    import torch
    from torch.nn import functional as F

    train, dev, held, folds = partition(rows, a)
    errors = missed_ids(a.oof, rows, folds, a)
    cache = {r["row_id"]: encode(transcript(r)) for r in rows}
    require(
        all(0 < len(ids) <= a.max_length for ids in cache.values()),
        "input exceeds --max-length; increase it",
    )
    params = [p for p in model.parameters() if p.requires_grad]
    optimizer = torch.optim.AdamW(params, lr=a.lr)
    rng = random.Random(a.seed)

    def batch(batch_rows):
        ids = [cache[r["row_id"]] for r in batch_rows]
        x = tokenizer.pad({"input_ids": ids}, return_tensors="pt", padding=True).to(
            a.device
        )
        y = torch.tensor([int(r["is_unsafe"]) for r in batch_rows], device=a.device)
        return forward(x, y), y, sum(map(len, ids))

    def step(group, update=True):
        (_logits, losses), y, tokens = batch(group)
        weights = torch.where(y.bool(), a.positive_weight, 1.0)
        loss = (losses * weights).mean()
        require(math.isfinite(loss.item()), "non-finite training loss")
        loss.backward()
        if update:
            torch.nn.utils.clip_grad_norm_(params, 1.0, error_if_nonfinite=True)
            optimizer.step()
        optimizer.zero_grad(set_to_none=True)
        if a.device == "mps":
            torch.mps.synchronize()
        return tokens

    model.train(not getattr(a, "probe", False))
    started = a._started
    deadline = started + a.seconds
    pilot = rng.sample(train, min(len(train), a.batch))
    require(time.monotonic() < deadline, "time box expired during setup")
    warmup_tokens = step(pilot, update=False)
    # Include clipping and optimizer cost without changing weights or optimizer history.
    optimizer.param_groups[0]["lr"] = 0.0
    sample_start = time.monotonic()
    pilot_tokens = step(pilot)
    rate = pilot_tokens / (time.monotonic() - sample_start)
    optimizer.state.clear()
    optimizer.param_groups[0]["lr"] = a.lr
    order = group_order(train, a.seed + 2)
    by_group = defaultdict(list)
    for row in train:
        by_group[row["scenario_id"]].extend(
            [row] * (1 + a.extra_copies * (row["row_id"] in errors))
        )
    # Reserve time for early stopping and device variation. Choose whole groups.
    # Reserve the held fold inference at a conservative measured-backward rate.
    train_deadline = deadline - sum(len(cache[r["row_id"]]) for r in held) / rate
    # Prefer a whole training pass when it fits; later epochs use the remaining time.
    update_deadline = train_deadline - sum(len(cache[r["row_id"]]) for r in dev) / rate
    capacity = max(0.0, update_deadline - time.monotonic()) * rate * 0.65
    selected, planned = [], 0
    for key in order:
        group = by_group[key]
        cost = sum(len(cache[r["row_id"]]) for r in group)
        if selected and planned + cost > capacity:
            break
        selected.extend(group)
        planned += cost
    require(
        time.monotonic() < update_deadline,
        "time box insufficient for pilot and OOF inference",
    )
    best, best_loss, best_epoch = None, math.inf, None
    seen, tokens, seconds, steps = 0, 0, 0.0, 0
    history = []
    for epoch in range(a.epochs):
        model.train(not getattr(a, "probe", False))
        rng.shuffle(selected)
        epoch_seen = 0
        for i in range(0, len(selected), a.batch):
            # Finish the current optimizer step before stopping.
            if time.monotonic() >= update_deadline:
                break
            group = selected[i : i + a.batch]
            tick = time.monotonic()
            tokens += step(group)
            seconds += time.monotonic() - tick
            seen += len(group)
            epoch_seen += len(group)
            steps += 1
        if not epoch_seen:
            break
        model.eval()
        losses = []
        with torch.no_grad():
            for i in range(0, len(dev), a.batch):
                if time.monotonic() >= train_deadline:
                    break
                (logits, _), y, _ = batch(dev[i : i + a.batch])
                losses.extend(
                    F.cross_entropy(logits.float(), y, reduction="none").tolist()
                )
        dev_loss = sum(losses) / len(dev) if len(losses) == len(dev) else None
        history.append(
            {"epoch": epoch + 1, "examples": epoch_seen, "dev_loss": dev_loss}
        )
        if dev_loss is None:
            break
        if dev_loss >= best_loss:
            break
        best_loss = dev_loss
        best_epoch = epoch + 1
        best = {
            k: p.detach().cpu().clone()
            for k, p in model.named_parameters()
            if p.requires_grad
        }
    require(steps, "time box exhausted before an optimizer step")
    if best is not None:
        model.load_state_dict(best, strict=False)
    report = {
        "optimizer_steps": steps,
        "examples": seen,
        "tokens": tokens,
        "optimizer_seconds": seconds,
        "tokens_per_second": tokens / seconds,
        "wall_seconds": time.monotonic() - started,
        "time_box": a.seconds,
        "warmup_examples": len(pilot),
        "warmup_tokens": warmup_tokens,
        "pilot_examples": len(pilot),
        "pilot_tokens": pilot_tokens,
        "pilot_tokens_per_second": rate,
        "scenario_ids": sorted({r["scenario_id"] for r in selected}),
        "selected_examples": len(selected),
        "available_examples": len(train),
        "selected_scenarios": len({r["scenario_id"] for r in selected}),
        "dev_scenarios": len({r["scenario_id"] for r in dev}),
        "passes": seen / len(selected),
        "full_fit_passes": seen / len(train),
        "epochs": history,
        "best_epoch": best_epoch,
        "oof_errors": len(errors),
        "arguments": {k: str(v) for k, v in vars(a).items() if not k.startswith("_")},
    }
    (a.out / "training.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report), flush=True)
    require(
        best_epoch is not None,
        "no complete train-only early-stopping evaluation inside time box",
    )
    if held:
        model.eval()
        preds = {}
        with torch.no_grad():
            for i in range(0, len(held), a.batch):
                require(
                    time.monotonic() < deadline,
                    "OOF time box expired; fold remains incomplete",
                )
                group = held[i : i + a.batch]
                (logits, _), _, _ = batch(group)
                preds.update(
                    zip(
                        (r["row_id"] for r in group),
                        logits.float().softmax(-1)[:, 1].tolist(),
                    )
                )
        report["oof_examples"] = len(preds)
        report["fit_and_oof_seconds"] = time.monotonic() - started
        (a.out / "training.json").write_text(json.dumps(report, indent=2))
        (a.out / "oof.json").write_text(
            json.dumps(
                {
                    "train_sha256": fingerprint(rows),
                    "seed": a.seed,
                    "folds": a.folds,
                    "fold": a.fold,
                    "source": str(a.source.resolve()),
                    "fit_scenarios": sorted({r["scenario_id"] for r in train + dev}),
                    "predictions": preds,
                }
            )
        )
