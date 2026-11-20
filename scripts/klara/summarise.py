"""Render section-six tier tables using only saved per-row result files."""
import argparse
from collections import defaultdict
from decimal import Decimal
from pathlib import Path

from common import atomic_text, read_tsv, require
from metrics import metrics
from results import validate_run


def markdown_table(rows):
    cols = list(rows[0])
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for row in rows:
        values = [str(row[k]).replace("|", "\\|").replace("\n", " ") for k in cols]
        lines.append("| " + " | ".join(values) + " |")
    return lines + [""]


def table(folder):
    references = {}
    tables = defaultdict(list)
    leaders = defaultdict(list)
    details = []
    for path in sorted(folder.glob("*.tsv")):
        rows = list(read_tsv(path))
        validate_run(rows)
        r = rows[0]
        split = r["split"]
        truth = {v["row_id"]: tuple(v[k] for k in ("is_unsafe", "turns", "rule_id", "trigger", "clarity"))
                 for v in rows}
        if split in references:
            require(truth == references[split], f"{path}: different ground truth for {split}")
        else:
            references[split] = truth
        group = (r["tier"] or "(unspecified tier)", split)
        if split == "validation":
            correct = sum(int(v["correct"]) for v in rows)
            fp = sum(v["label"] == "unsafe" and v["is_unsafe"] == "0" for v in rows)
            leaders[group[0]].append((correct, -fp, path.name))
        if split == "test":
            for field in ("turns", "rule_id", "trigger", "clarity"):
                groups = defaultdict(list)
                for v in rows:
                    groups[v[field] or "(none)"].append(v)
                for value, subset in sorted(groups.items()):
                    details.append({"source": path.name, "field": field, "value": value, **metrics(subset)})
        costs = [Decimal(v["cost_usd"]) for v in rows if v["cost_usd"]]
        spend = "—"
        if r["backend"] == "openrouter":
            spend = str(sum(costs)) if len(costs) == len(rows) else f"unknown ({len(costs)}/{len(rows)} priced)"
        tables[group].append({"model": r["model"], "stage": r["stage"], "cutoff": r["threshold"],
                              **metrics(rows), "bytes": r["size_bytes"] or "—", "licence": r["licence"] or "—",
                              "USD": spend, "source": path.name})
    require(tables, "no per-row result files")
    lines = ["# Klara tier scores", "", "Brackets give 95% intervals. Validation recall moves one point per "
             "unsafe conversation in the full benchmark. Interpret gaps below five rows cautiously.", ""]
    for (tier, split), runs in sorted(tables.items()):
        baseline = [{"is_unsafe": v[0], "label": "safe", "unsafe_probability": 0, "error": "", "latency_ms": ""}
                    for v in references[split].values()]
        runs.append({"model": "never flags", "stage": "reference", "cutoff": "—", **metrics(baseline),
                     "bytes": "—", "licence": "—", "USD": "—", "source": "same rows"})
        lines += [f"## {tier} / {split}", ""] + markdown_table(runs)
    if leaders:
        lines += ["## Validation leaders among supplied runs", ""]
        for tier, candidates in sorted(leaders.items()):
            best = max((correct, neg_fp) for correct, neg_fp, _ in candidates)
            names = sorted(name for correct, neg_fp, name in candidates if (correct, neg_fp) == best)
            lines.append(f"- {tier}: {', '.join(names)} ({best[0]} correct, {-best[1]} false positives).")
        lines.append("")
    if details:
        lines += ["## Test breakdowns", ""] + markdown_table(details)
    return "\n".join(lines)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("folder", type=Path)
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    report = table(args.folder)
    if args.output:
        with atomic_text(args.output) as out:
            out.write(report)
    else:
        print(report)


if __name__ == "__main__":
    main()
