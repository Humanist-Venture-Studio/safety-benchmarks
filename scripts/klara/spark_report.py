"""Recount the Spark tables from saved first attempts, without rerunning inference."""

import argparse
import hashlib
import csv
import json
from collections import defaultdict
from pathlib import Path

from common import read_tsv, require
from metrics import metrics
from results import validate_run
from spark_experiment import DATA, LOGS, RESULTS, RUNS, LICENSE, TIER, source, is_chat_model

COMPACT = "row_id split is_unsafe unsafe_probability label error latency_ms".split()
STAGES = ("baseline", "r1", "r2")
SPLITS = ("train-sample", "validation")


def write(path, rows, fields=None):
    with path.open("w", encoding="utf-8", newline="") as f:
        fields = fields or list(rows[0])
        w = csv.DictWriter(
            f, fields, delimiter="\t", lineterminator="\n", extrasaction="ignore"
        )
        w.writeheader()
        w.writerows(rows)


def counts(rows):
    misses = sum(r["is_unsafe"] == "1" and r["label"] != "unsafe" for r in rows)
    fp = sum(r["is_unsafe"] == "0" and r["label"] == "unsafe" for r in rows)
    malformed = sum(bool(r["error"]) for r in rows)
    tp = sum(r["is_unsafe"] == "1" and r["label"] == "unsafe" for r in rows)
    return dict(
        correct=sum(
            not r["error"] and ((r["label"] == "unsafe") == (r["is_unsafe"] == "1"))
            for r in rows
        ),
        fp=fp,
        missed=misses,
        tp=tp,
        malformed=malformed,
    )


def diagnose(rows, meta):
    groups = defaultdict(lambda: [0, 0])
    # Preserve the denominator for families absent from the validation split.
    for m in meta.values():
        if m["rule_id"]:
            groups["rule_id", m["rule_id"]] = [0, 0]
    for r in rows:
        m = meta[r["row_id"]]
        positive = m["is_unsafe"] == "1"
        missed = (
            int(r["label"] != "unsafe") if positive else int(r["label"] == "unsafe")
        )
        dims = (
            [(k, m[k]) for k in ("rule_id", "trigger", "turns", "clarity")]
            if positive
            else [("safe_type", "look_alike" if m["look_alike_of"] else "ordinary")]
        )
        for key in dims:
            groups[key][0] += missed
            groups[key][1] += 1
    return [
        dict(dimension=k, group=v, errors=e, total=n)
        for (k, v), (e, n) in sorted(groups.items())
    ]


def fold_errors(model, meta):
    rows = []
    for path in sorted(RUNS.glob(f"{model}-fold*/oof.json")):
        for k, prob in json.loads(path.read_bytes())["predictions"].items():
            require(meta[k]["split"] == "train", "non-training OOF row")
            rows.append(dict(row_id=k, label="unsafe" if prob >= 0.5 else "safe"))
    require(len({r["row_id"] for r in rows}) == len(rows) == 8000, "incomplete OOF set")
    return diagnose(rows, meta)


def save_recipes(out, meta, commands):
    """Keep source revisions, selected groups and exact row memberships alongside the local evidence."""
    from spark_experiment import WORK

    recipes = {}
    archived = RESULTS / "fit-membership"
    archived.mkdir(exist_ok=True)
    for train_file in sorted(RUNS.glob("*/training.json")):
        folder = train_file.parent
        info = json.loads(train_file.read_bytes())
        ids_file = folder / "trained-row-ids.txt"
        if ids_file.exists():
            ids = ids_file.read_bytes()
        else:
            # The first fit predates the per-row log. Both complete passes used exactly these scenarios.
            require(
                info["oof_errors"] == 0 and info["passes"] >= 1,
                "cannot reconstruct a partially observed weighted fit",
            )
            groups = set(info["scenario_ids"])
            ids = "".join(
                k + "\n" for k in sorted(meta) if meta[k]["scenario_id"] in groups
            ).encode()
        require(
            len(ids.splitlines())
            == info.get("unique_optimizer_rows", info["selected_examples"]),
            "fit membership count mismatch",
        )
        (archived / (folder.name + ".txt")).write_bytes(ids)
        args = {k: v.replace(str(WORK), "$WORK") for k, v in info["arguments"].items()}
        recipes[folder.name] = dict(
            arguments=args,
            selected_scenarios=info["scenario_ids"],
            unique_rows=len(ids.splitlines()),
            row_ids_sha256=hashlib.sha256(ids).hexdigest(),
            optimizer_examples=info["examples"],
            tokens=info["tokens"],
            tokens_per_second=info["tokens_per_second"],
            epochs=info["epochs"],
            best_epoch=info["best_epoch"],
            weak_rules=info.get("weak_rules", []),
            repeated_lookalikes=info.get("repeat_lookalikes", False),
            oof_errors=info["oof_errors"],
            fit_seconds=info["wall_seconds"],
            oof_examples=info.get("oof_examples", 0),
            fit_and_oof_seconds=info.get("fit_and_oof_seconds", info["wall_seconds"]),
        )
    sources = {
        m: json.loads(((source(m) if (source(m) / "source.json").exists() else source(m).parent) / "source.json").read_bytes())
        for m in LICENSE
    }
    report = dict(
        source_sha256=json.loads((LOGS / "dataset.json").read_bytes())["source_sha256"],
        development_sha256=hashlib.sha256(DATA.read_bytes()).hexdigest(),
        seed=20261117,
        sources=sources,
        spark_experiment_arguments=[
            e.get("replay_args", e["argv"][1:])
            for e in sorted(
                (e for e in commands if e.get("action")), key=lambda e: e["start"]
            )
        ],
        fits=recipes,
    )
    (out / "fit-recipes.json").write_text(json.dumps(report, indent=2) + "\n")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument(
        "--diagnose",
        choices=LICENSE,
        help="write train OOF and validation R1 error counts only",
    )
    a = p.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    meta = {r["row_id"]: r for r in read_tsv(DATA)}
    if a.diagnose:
        model = a.diagnose
        for split, errors in [
            ("oof", fold_errors(model, meta)),
            (
                "validation",
                diagnose(
                    list(read_tsv(RESULTS / f"{model}-r1-validation-raw.tsv")), meta
                ),
            ),
        ]:
            write(a.out / f"{model}-{split}-r1-errors.tsv", errors)
        return

    commands = [
        json.loads(s) for s in (LOGS / "commands.jsonl").read_text().splitlines()
    ]
    report, details, miss_rows, tables = [], [], [], {}
    memberships = {}
    artifact_hashes = {}
    for split in SPLITS:
        lines = [
            "| Candidate | Pass | Calibrated cutoff | Accuracy, raw → selected | FPR, raw → selected | Missed / 100, raw → selected | Recall | Precision | AUROC | PR-AUC | Brier | Malformed | Median ms | Bytes | Licence | Unique fit rows | Machine min |",
            "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|",
        ]
        for model in LICENSE:
            for stage in STAGES:
                name = f"{model}-{stage}"
                path = RESULTS / f"{name}-{split}-raw.tsv"
                raw = list(read_tsv(path))
                validate_run(raw)
                require(
                    len(raw) == 1000 and sum(int(r["is_unsafe"]) for r in raw) == 100,
                    "wrong split balance",
                )
                keys = {r["row_id"] for r in raw}
                require(
                    keys == memberships.setdefault(split, keys),
                    "sample membership changed",
                )
                spec_path = RESULTS / f"{name}-calibration.json"
                spec = (
                    json.loads(spec_path.read_bytes()) if spec_path.exists() else None
                )
                chosen = (
                    list(read_tsv(RESULTS / f"{name}-{split}.tsv")) if spec else raw
                )
                validate_run(chosen)
                require(
                    [r["row_id"] for r in raw] == [r["row_id"] for r in chosen],
                    "paired row mismatch",
                )
                raw_counts = counts(raw)
                artifact = (
                    RUNS
                    / name
                    / (
                        "candidate.gguf"
                        if is_chat_model(model)
                        else "hf/model.safetensors"
                    )
                )
                from export_chat import BOUNDS
                lo, hi = BOUNDS[TIER]
                require(
                    lo <= artifact.stat().st_size == int(raw[0]["size_bytes"]) <= hi,
                    "retained artifact size diverged from benchmark",
                )
                if name not in artifact_hashes:
                    with artifact.open("rb") as f:
                        artifact_hashes[name] = hashlib.file_digest(
                            f, "sha256"
                        ).hexdigest()
                if split == "validation" and stage == "r2":
                    for r in diagnose(chosen, meta):
                        miss_rows.append({"model": model, **r})
                for op, rows in [("raw", raw), ("selected", chosen)]:
                    if op == "selected" and not spec:
                        continue
                    compact = a.out / f"{name}-{split}-{op}.tsv"
                    write(compact, rows, COMPACT)
                    saved = list(read_tsv(compact))
                    require(counts(saved) == counts(rows), "compact recount mismatch")
                    stats = metrics(saved)
                    details.append(
                        dict(
                            model=model,
                            stage=stage,
                            split=split,
                            operating_point=op,
                            threshold=rows[0]["threshold"],
                            **(counts(saved) | stats),
                        )
                    )
                c = counts(chosen)
                m = metrics(chosen)
                training = RUNS / name / "training.json"
                info = json.loads(training.read_bytes()) if training.exists() else {}
                unique = info.get("unique_optimizer_rows")
                if unique is None and info:
                    require(
                        info["passes"] >= 1 and info["oof_errors"] == 0,
                        "need actual unique fit row count",
                    )
                    unique = info["selected_examples"]
                timings = [
                    e
                    for e in commands
                    if e.get("action")
                    and e["model"] == model
                    and (
                        (e["stage"] == stage and e["fold"] is None)
                        or (e["fold"] is not None and stage == "r2")
                    )
                ]
                require(
                    any(e["action"] == "score" for e in timings),
                    f"missing timing for {name}",
                )
                seconds = sum(e["seconds"] for e in timings)
                seconds += sum(e["seconds"] for e in commands if e.get("code", 0) != 0
                               and e.get("step", "").startswith(name + "-"))
                seconds += sum(e["interrupted_seconds"] for e in commands if "interrupted_seconds" in e
                               and e["model"] == model and e["stage"] == stage)
                seconds += sum(
                    e["fit_setup_seconds"]
                    for e in commands
                    if "fit_setup_seconds" in e
                    and e["model"] == model
                    and e["stage"] == stage
                )
                seconds -= sum(
                    e["sleep_estimate"]
                    for e in commands
                    if "sleep_estimate" in e
                    and e["model"] == model
                    and e["stage"] == stage
                )
                if info and not any(
                    e["action"] == "train" and e["fold"] is None for e in timings
                ):
                    seconds += info["wall_seconds"]
                cutoff = spec["threshold"] if spec else None
                label = "probe" if model == "ettin" and stage == "baseline" else stage
                metric = lambda k: m[k].split(" ")[0]
                precision = (
                    f"{c['tp'] / (c['tp'] + c['fp']):.1%}" if c["tp"] + c["fp"] else "—"
                )
                fields = [
                    model,
                    label,
                    f"{cutoff:.6g}" if spec else "unavailable",
                    f"{raw_counts['correct'] / 10:.1f}% → {c['correct'] / 10:.1f}%",
                    f"{raw_counts['fp'] / 9:.2f}% → {c['fp'] / 9:.2f}%",
                    f"{raw_counts['missed']} → {c['missed']}",
                    f"{c['tp']}%",
                    precision,
                    metric("AUROC"),
                    metric("PR-AUC (AP)"),
                    metric("Brier"),
                    c["malformed"],
                    m["median ms"],
                    f"{int(raw[0]['size_bytes']):,}",
                    LICENSE[model],
                    unique or 0,
                    f"{seconds / 60:.2f}",
                ]
                if not spec:
                    for i in (3, 4, 5):
                        fields[i] = fields[i].split(" → ")[0] + " → —"
                lines.append("| " + " | ".join(map(str, fields)) + " |")
                report.append(
                    dict(
                        model=model,
                        stage=stage,
                        split=split,
                        threshold=cutoff,
                        calibration="fitted" if spec else "unavailable",
                        platt_slope=spec["slope"] if spec else None,
                        platt_intercept=spec["intercept"] if spec else None,
                        unique_fit_rows=unique or 0,
                        optimizer_examples=info.get("examples", 0),
                        fit_minutes=info.get("wall_seconds", 0) / 60,
                        pass_minutes=seconds / 60,
                        deployed_bytes=raw[0]["size_bytes"],
                        deployed_sha256=artifact_hashes[name],
                        licence=LICENSE[model],
                    )
                )
        reference = [
            dict(
                is_unsafe=r["is_unsafe"],
                label="safe",
                unsafe_probability="0",
                error="",
                latency_ms="",
            )
            for r in raw
        ]
        details.append(
            dict(
                model="always-safe",
                stage="reference",
                split=split,
                operating_point="reference",
                threshold=0.5,
                **(counts(reference) | metrics(reference)),
            )
        )
        lines.append(
            "| Always safe | Reference | — | 90.0% | 0.00% | 100 | 0% | — | 0.5000 | 0.1000 | 0.1000 | 0 | — | — | — | 0 | 0 |"
        )
        tables[split] = "\n".join(lines)
    save_recipes(a.out, meta, commands)
    write(a.out / "pass-metadata.tsv", report)
    write(a.out / "metrics.tsv", details)
    write(a.out / "round2-errors.tsv", miss_rows)
    (a.out / "tables.md").write_text(
        "\n\n".join("## " + s + "\n\n" + tables[s] for s in SPLITS) + "\n"
    )


if __name__ == "__main__":
    main()
