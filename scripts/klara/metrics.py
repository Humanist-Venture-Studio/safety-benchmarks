"""Counts, Wilson binomial intervals and tie-correct AUROC for saved predictions."""
import math
from bisect import bisect_left, bisect_right
from collections import defaultdict
from statistics import mean, median, variance

Z = 1.959963984540054


def rate(n, total):
    if not total:
        return "—"
    p = n / total
    denom = 1 + Z * Z / total
    mid = (p + Z * Z / (2 * total)) / denom
    half = Z / denom * math.sqrt(p * (1 - p) / total + Z * Z / (4 * total * total))
    return f"{p:.1%} [{max(0, mid-half):.1%}, {min(1, mid+half):.1%}]"


def auc_interval(positive, negative):
    if not positive or not negative:
        return "—"
    positive.sort()
    negative.sort()
    # Placements award half a win for a tie. DeLong uses one placement per observation.
    wins = [(bisect_left(negative, x) + bisect_right(negative, x)) / (2 * len(negative)) for x in positive]
    auc = mean(wins)
    if min(len(positive), len(negative)) < 2:
        return f"{auc:.4f} [CI unavailable]"
    losses = [1 - (bisect_left(positive, x) + bisect_right(positive, x)) / (2 * len(positive))
              for x in negative]
    half = Z * math.sqrt(variance(wins) / len(wins) + variance(losses) / len(losses))
    return f"{auc:.4f} [{max(0, auc-half):.4f}, {min(1, auc+half):.4f}]"


def average_precision(valid):
    buckets = defaultdict(lambda: [0, 0])
    for r in valid:
        buckets[float(r["unsafe_probability"])][int(r["is_unsafe"])] += 1
    total = sum(v[1] for v in buckets.values())
    if not total:
        return "—"
    seen = hits = 0
    area = 0.
    for score in sorted(buckets, reverse=True):
        negatives, positives = buckets[score]
        hits += positives
        seen += negatives + positives
        area += (positives / total) * (hits / seen)
    return f"{area:.4f}"


def metrics(rows):
    n = len(rows)
    unsafe = sum(int(r["is_unsafe"]) for r in rows)
    valid = [r for r in rows if not r["error"]]
    tp = sum(int(r["is_unsafe"]) for r in valid if r["label"] == "unsafe")
    fp = sum(1 - int(r["is_unsafe"]) for r in valid if r["label"] == "unsafe")
    correct = sum((r["label"] == "unsafe") == bool(int(r["is_unsafe"])) for r in valid)
    scores = [[float(r["unsafe_probability"]) for r in valid if int(r["is_unsafe"]) == v] for v in (1, 0)]
    elapsed = [float(r["latency_ms"]) for r in rows if r["latency_ms"] != ""]
    return {"n": n, "accuracy": rate(correct, n), "FPR": rate(fp, n - unsafe),
            "missed/unsafe": f"{unsafe-tp}/{unsafe}", "recall": rate(tp, unsafe),
            "precision": rate(tp, tp + fp), "AUROC": auc_interval(*scores),
            "PR-AUC (AP)": average_precision(valid),
            "Brier": f"{mean((float(r['unsafe_probability'])-int(r['is_unsafe']))**2 for r in valid):.4f}" if valid else "—",
            "malformed": f"{n-len(valid)} ({rate(n-len(valid), n)})",
            "median ms": f"{median(elapsed):.2f}" if elapsed else "—"}


def print_metrics(rows):
    def show(name, group):
        print(name + "\t" + "\t".join(f"{k}={v}" for k, v in metrics(group).items()))
    show("overall", rows)
    for key in ("turns", "rule_id", "trigger", "clarity"):
        groups = defaultdict(list)
        for row in rows:
            groups[row[key] or "(none)"].append(row)
        for value, group in sorted(groups.items()):
            show(f"{key}={value}", group)
