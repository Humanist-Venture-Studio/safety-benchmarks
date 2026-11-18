"""Measure train-to-held-out text overlap on the final dataset."""
import argparse
from collections import Counter, defaultdict
from pathlib import Path

from common import DATA, WORK, atomic_text, messages_from_tsv, read_tsv, require
from similarity import PERCENT, matches, transcript


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--data", type=Path, default=DATA)
    p.add_argument("--output", type=Path, default=WORK / "results/overlap.md")
    args = p.parse_args()
    rows = list(read_tsv(args.data))
    splits = {r["row_id"]: r["split"] for r in rows}
    require(len(splits) == len(rows) and set(splits.values()) == {"train", "validation", "test"},
            "expected unique rows and all three splits")
    docs = {r["row_id"]: transcript(messages_from_tsv(r)) for r in rows}
    affected, pairs, exact = defaultdict(set), Counter(), Counter()
    examples = []
    for a, b, score in matches(docs, lambda a, b: (splits[a] == "train") != (splits[b] == "train")):
        held = b if splits[a] == "train" else a
        split = splits[held]
        affected[split].add(held)
        pairs[split] += 1
        exact[split] += docs[a] == docs[b]
        if len(examples) < 10:
            examples.append(f"- {a} / {b} ({score:.3f})")
    with atomic_text(args.output) as out:
        print(f"# Train-to-held-out overlap\n\nCharacter five-gram Jaccard ≥ {PERCENT}%.\n", file=out)
        for split in ("validation", "test"):
            total = sum(s == split for s in splits.values())
            print(f"- {split}: {len(affected[split])}/{total} held-out rows, {pairs[split]} pairs, "
                  f"{exact[split]} exact normalized matches.", file=out)
        if examples:
            print("\nExample pairs\n\n" + "\n".join(examples), file=out)
    print(args.output.read_text(encoding="utf-8").strip())


if __name__ == "__main__":
    main()
