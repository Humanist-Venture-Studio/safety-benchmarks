"""Recount the four frozen winners from published scores and held-out grouping metadata."""

import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path

from common import DATA, ROOT, read_tsv, require
from metrics import metrics
from tier_data import FINAL_SHA256, digest

RESULTS = ROOT / "results/klara"
MODELS = {"spark": "ettin", "flash": "qguard06", "maxx": "qguard8", "cloud": "prompt-v1"}


def summarize(rows):
    stats = metrics(rows)
    unsafe = sum(int(r["is_unsafe"]) for r in rows)
    flags = [r for r in rows if not r["error"] and r["label"] == "unsafe"]
    tp = sum(int(r["is_unsafe"]) for r in flags)
    fp = len(flags) - tp
    safe = len(rows) - unsafe
    return dict(rows=len(rows), safe=safe, unsafe=unsafe,
                correct=sum(not r["error"] and (r["label"] == "unsafe") == bool(int(r["is_unsafe"])) for r in rows),
                accuracy=stats["accuracy"], false_positive=fp, FPR=f"{fp/safe:.2%}" if safe else "—",
                missed=unsafe - tp, precision=f"{tp/len(flags):.2%}" if flags else "—",
                AUROC=stats["AUROC"], PR_AUC=stats["PR-AUC (AP)"], Brier=stats["Brier"],
                malformed=sum(bool(r["error"]) for r in rows), median_ms=stats["median ms"])


def recount(data, folder):
    require(digest(data) == FINAL_SHA256, "unexpected final dataset")
    keys = ["row_id", "is_unsafe", "turns", "rule_id", "trigger", "clarity", "look_alike_of"]
    meta = {r["row_id"]: {k: r[k] for k in keys} for r in read_tsv(data) if r["split"] == "test"}
    require(len(meta) == 1000 and sum(int(r["is_unsafe"]) for r in meta.values()) == 100,
            "unexpected test population")
    totals, details = [], []
    for tier, model in MODELS.items():
        rows = list(read_tsv(folder / f"{tier}.tsv"))
        require(len(rows) == len(meta) and {r["row_id"] for r in rows} == set(meta), "unpaired test IDs")
        size, licence, cutoff = "", "Hosted API", 0.70
        if tier != "cloud":
            spec = json.loads((Path(__file__).with_name("calibration") / f"{tier}.json").read_bytes())
            cutoff = spec["threshold"]
            receipt = next(r for r in read_tsv(RESULTS / tier / "pass-metadata.tsv")
                           if (r["model"], r["stage"], r["split"]) == (model, "r2", "validation"))
            require(float(receipt["threshold"]) == cutoff, "cutoff differs from validation")
            size, licence = receipt["deployed_bytes"], receipt["licence"]
        groups = defaultdict(list)
        for r in rows:
            m = meta[r["row_id"]]
            require(r["split"] == "test" and m["is_unsafe"] == r["is_unsafe"], "ground truth mismatch")
            require(math.isfinite(float(r["latency_ms"])) and float(r["latency_ms"]) >= 0, "invalid latency")
            if r["error"]:
                require(not r["label"] and not r["unsafe_probability"], "invalid malformed record")
            else:
                p = float(r["unsafe_probability"])
                require(0 <= p <= 1 and r["label"] == ("unsafe" if p >= cutoff else "safe"), "wrong verdict")
            for field in ("turns", "rule_id", "trigger", "clarity"):
                groups[field, m[field] or "(none)"].append(r)
            if r["is_unsafe"] == "0":
                groups["safe_type", "look_alike" if m["look_alike_of"] else "ordinary"].append(r)
        totals.append(dict(tier=tier, **summarize(rows), deployed_bytes=size, licence=licence, cutoff=cutoff))
        for (field, value), subset in sorted(groups.items()):
            details.append(dict(tier=tier, field=field, value=value, **summarize(subset)))
    return totals, details


def write(path, rows):
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, rows[0], delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--data", type=Path, default=DATA)
    p.add_argument("--scores", type=Path, default=RESULTS / "test")
    p.add_argument("--output-dir", type=Path)
    args = p.parse_args()
    totals, groups = recount(args.data, args.scores)
    if args.output_dir:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        write(args.output_dir / "metrics.tsv", totals)
        write(args.output_dir / "breakdowns.tsv", groups)
    print("Klara test · 1,000 conversations · 95% Wilson accuracy and DeLong AUROC intervals")
    for r in totals:
        print(r["tier"], r["correct"], r["accuracy"], r["AUROC"], sep="\t")


if __name__ == "__main__":
    main()
