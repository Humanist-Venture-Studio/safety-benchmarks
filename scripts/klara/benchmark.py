"""Run one first-attempt benchmark and save its inputs to the metrics."""
import argparse
import csv
import fcntl
import os
import random
import time
from pathlib import Path

from backends import TIERS, Backend, backend_args
from common import DATA, WORK, messages_from_tsv, read_tsv, require
from metrics import print_metrics
from results import FIELDS, validate_run


def selection(path, split):
    partition = "train" if split == "train-sample" else split
    rows = sorted((r for r in read_tsv(path) if r["split"] == partition), key=lambda r: r["row_id"])
    require(rows and len({r["row_id"] for r in rows}) == len(rows), "empty split or repeated row_id")
    require(all(r["is_unsafe"] in ("0", "1") for r in rows), "invalid ground truth")
    if split == "train-sample":
        rng = random.Random(20261117)
        rows = (rng.sample([r for r in rows if r["is_unsafe"] == "0"], 900)
                + rng.sample([r for r in rows if r["is_unsafe"] == "1"], 100))
        rng.shuffle(rows)
    return rows


def main():
    p = argparse.ArgumentParser(description=__doc__)
    backend_args(p)
    p.add_argument("--split", required=True, choices=("train-sample", "validation", "test"))
    p.add_argument("--data", type=Path, default=DATA)
    p.add_argument("--limit", type=int, help="score a fixed-seed subset of the selected split")
    p.add_argument("--output", type=Path)
    p.add_argument("--resume-interrupted", action="store_true",
                   help="recover a local pinned run, counting an unrecorded in-flight row as malformed")
    p.add_argument("--stage", default="baseline", help="e.g. baseline, round-1, round-2 or prompt-v1")
    p.add_argument("--size-bytes", type=int)
    p.add_argument("--licence", default="")
    a = p.parse_args()
    from tier_data import verify_input
    verify_input(a.data)
    rows = selection(a.data, a.split)
    if a.limit is not None:
        require(0 < a.limit <= len(rows), "--limit must be between 1 and the selected split size")
        rows = random.Random(20261117).sample(rows, a.limit)
    backend = Backend(a)
    tier = a.tier or next((k for k, v in TIERS.items() if v == (backend.name, backend.model)), "")
    meta = dict(tier=tier, backend=backend.name, model=backend.model, stage=a.stage, split=a.split,
                threshold=backend.threshold, prompt_sha256=backend.prompt_hash, size_bytes=a.size_bytes, licence=a.licence,
                calibration_sha256=backend.calibration_hash, safe_token=a.safe_token, unsafe_token=a.unsafe_token, safe_label=a.safe_label, unsafe_label=a.unsafe_label)
    require(a.size_bytes is None or a.size_bytes > 0, "size must be positive")
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    path = a.output or WORK / "results" / f"{backend.name}-{a.split}-{stamp}.tsv"
    path.parent.mkdir(parents=True, exist_ok=True)
    require(not path.exists(), f"{path} already exists")
    partial = path.with_suffix(path.suffix + ".partial")
    results = []
    fields = FIELDS + ["raw_probability", "calibration_sha256"]
    if a.resume_interrupted:
        require(a.backend in ("tei", "ollama") and (a.data.parent / "dataset.json").is_file(),
                "recovery needs a pinned local benchmark")
    with partial.open("r+" if a.resume_interrupted else "x", encoding="utf-8", newline="") as out:
        fcntl.flock(out, fcntl.LOCK_EX | fcntl.LOCK_NB)
        writer = csv.DictWriter(out, fields, delimiter="\t", lineterminator="\n")
        if a.resume_interrupted:
            reader = csv.DictReader(out, delimiter="\t")
            require(reader.fieldnames == fields, "partial result schema differs")
            results = list(reader)
            if results:
                validate_run(results)
            require(len(results) <= len(rows), "partial result longer than split")
            for prior, row in zip(results, rows):
                require(all(prior[k] == row[k] for k in ("row_id", "is_unsafe", "turns", "rule_id", "trigger", "clarity"))
                        and all(prior[k] == ("" if v is None else str(v)) for k, v in meta.items()),
                        "partial result differs from current model, metadata or ordered split")
            out.seek(0, os.SEEK_END)
        else:
            writer.writeheader()
        interrupted = len(results) if a.resume_interrupted else -1
        for i, r in enumerate(rows[len(results):], len(results)):
            messages = messages_from_tsv(r)
            start = time.monotonic_ns()
            if i == interrupted:
                contract, raw, error, cost = None, "", "interrupted before durable verdict", None
            else:
                contract, raw, error, cost = backend.score(messages)
            ms = (time.monotonic_ns() - start) / 1e6
            prediction = contract or {"unsafe_probability": "", "label": ""}
            correct = not error and (prediction["label"] == "unsafe") == bool(int(r["is_unsafe"]))
            record = {**meta, **{k: r[k] for k in ("row_id", "is_unsafe", "turns", "rule_id", "trigger", "clarity")},
                      **prediction, "correct": int(correct), "latency_ms": f"{ms:.3f}",
                      "raw": raw, "raw_probability": backend.raw_probability if not error else "", "error": error, "cost_usd": cost}
            writer.writerow(record)
            out.flush()
            results.append(record)
    os.link(partial, path)  # Never replace an existing run, even if another writer arrives.
    partial.unlink()
    print(path)
    if backend.name == "openrouter":
        priced = sum(r["cost_usd"] is not None for r in results)
        print(f"Reported cost USD {backend.spent} ({priced}/{len(results)} rows priced)")
    print_metrics(results)


if __name__ == "__main__":
    main()
