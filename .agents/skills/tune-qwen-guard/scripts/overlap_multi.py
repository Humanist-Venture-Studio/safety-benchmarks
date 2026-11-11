"""Measure how close each test conversation is to its nearest conversation in the 7,500 training rows."""
import argparse
import csv
from pathlib import Path
import re

import numpy as np
from scipy.sparse import csr_matrix

from benchmark_multi import TURNS, load_cases

BANDS = ((0.8, "near-duplicate (>= 0.8)"), (0.5, "heavy overlap (0.5-0.8)"), (0.2, "some overlap (0.2-0.5)"),
         (0.0, "little overlap (< 0.2)"))


def normalise(text):
    return " ".join(re.sub(r"[^a-z0-9]+", " ", text.lower()).split())


def shingles(row):
    """Word trigrams of each message, so a match means shared wording, not shared topic words."""
    found = set()
    for turn in TURNS:
        words = normalise(row[turn]).split()
        found.update(" ".join(words[i:i + 3]) for i in range(max(1, len(words) - 2)))
    return found


def band(similarity):
    return next(label for floor, label in BANDS if similarity >= floor)


def measure(data, split_file, output):
    cases = load_cases(data, split_file)
    test = [r for s, r in cases if s == "test"]
    seen = [r for s, r in cases if s != "test"]
    sets = [shingles(r) for r in test + seen]
    index = {}
    rows, cols = [], []
    for i, found in enumerate(sets):
        rows.extend([i] * len(found))
        cols.extend(index.setdefault(s, len(index)) for s in found)
    matrix = csr_matrix((np.ones(len(rows), dtype=np.float32), (rows, cols)), shape=(len(sets), len(index)))
    sizes = np.array([len(s) for s in sets], dtype=np.float32)
    shared = (matrix[:len(test)] @ matrix[len(test):].T).toarray()
    jaccard = shared / (sizes[:len(test), None] + sizes[None, len(test):] - shared)
    nearest = jaccard.argmax(axis=1)
    best = jaccard[np.arange(len(test)), nearest]
    messages = {normalise(r[t]) for r in seen for t in TURNS}
    with output.open("x", encoding="utf-8", newline="") as target:
        writer = csv.writer(target, delimiter="\t", lineterminator="\n")
        writer.writerow(("request_id", "consensus_rating", "nearest_request_id", "nearest_split",
                         "nearest_consensus_rating", "trigram_jaccard", "band", "messages_reused_verbatim"))
        split = {r["request_id"]: s for s, r in cases}
        for row, j, similarity in zip(test, nearest, best):
            other = seen[j]
            reused = sum(normalise(row[t]) in messages for t in TURNS)
            writer.writerow((row["request_id"], row["consensus_rating"], other["request_id"],
                             split[other["request_id"]], other["consensus_rating"], f"{similarity:.4f}",
                             band(similarity), reused))
    print(f"{len(test)} test rows against {len(seen)} training rows (train + validation)")
    for floor, label in BANDS:
        mask = np.array([band(s) == label for s in best])
        same = sum(test[i]["consensus_rating"] == seen[nearest[i]]["consensus_rating"] for i in np.flatnonzero(mask))
        print(f"  {label}: {int(mask.sum())} rows ({100 * mask.mean():.1f}%), nearest row has the same rating in {same}")
    print(f"  median similarity {np.median(best):.3f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=Path("data-multi.tsv"))
    parser.add_argument("--split-file", type=Path, default=Path("data-multi-split.tsv"))
    parser.add_argument("--output", type=Path, required=True, help="New per-row TSV")
    args = parser.parse_args()
    measure(args.data, args.split_file, args.output)
