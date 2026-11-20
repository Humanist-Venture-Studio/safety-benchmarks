"""Pick a validation-only operating point from persisted predictions."""
import argparse
from collections import Counter, defaultdict
from pathlib import Path

from common import read_tsv, require
from results import validate_run


def choose(rows):
    require({r["split"] for r in rows} == {"validation"}, "threshold selection requires validation only")
    # At p >= 0 all valid rows flag. Move equal-score groups together.
    groups = defaultdict(Counter)
    for r in rows:
        if not r["error"]:
            groups[float(r["unsafe_probability"])][int(r["is_unsafe"])] += 1
    require(groups, "no valid validation scores")
    fp = sum(pair[0] for pair in groups.values())
    correct = sum(pair[1] for pair in groups.values())
    best = None
    for threshold in sorted(set(groups) | {0.0, 0.5, 1.0}):
        candidate = (correct, -fp, -abs(threshold - 0.5))
        if best is None or candidate > best[0]:
            best = candidate, threshold
        zeros, ones = groups[threshold][0], groups[threshold][1]
        fp -= zeros
        correct += zeros - ones
    return best[1], best[0][0], -best[0][1]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("results", type=Path)
    rows = list(read_tsv(p.parse_args().results))
    validate_run(rows)
    threshold, correct, fp = choose(rows)
    print(f"threshold={threshold!r} correct={correct}/{len(rows)} false_positives={fp}")


if __name__ == "__main__":
    main()
