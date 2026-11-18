"""Recheck all writer output and assemble the public dataset atomically."""
import argparse
import csv
from pathlib import Path

from check_shard import check_files
from common import COLUMNS, DATA, LABEL_FIELDS, META, RULES, SHARDS, TURN_FIELDS, atomic_text, check_quotas, jsonl, require, rules_table


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--shards", type=Path, default=SHARDS)
    p.add_argument("--rules", type=Path, default=RULES)
    p.add_argument("--output", type=Path, default=DATA)
    args = p.parse_args()
    slots = list(jsonl(args.shards / "slots.jsonl"))
    check_quotas(slots)
    rules = rules_table(args.rules)
    paths = [args.shards / f"shard-{i:02}.written.jsonl" for i in range(1, 26)]
    require(set(paths) == set(args.shards.glob("shard-*.written.jsonl")), "expected exactly 25 written shards")
    spec = {r["row_id"]: r for r in slots}
    messages, errors = check_files(paths, set(paths), spec)
    require(not errors and spec.keys() == messages.keys(), "shard checks failed")
    with atomic_text(args.output) as out:
        writer = csv.DictWriter(out, COLUMNS, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for key, slot in sorted(spec.items()):
            row = {k: slot[k] for k in META + LABEL_FIELDS if k != "required_action"}
            row.update(zip(TURN_FIELDS, (m["content"] for m in messages[key])))
            if row["is_unsafe"]:
                rule = rules[row["rule_id"]]
                require(rule["trigger_side"] in ("either", row["trigger"]) and rule["required_action"].strip(),
                        f"{key}: rule mismatch or missing required action")
                row["required_action"] = rule["required_action"]
            writer.writerow(row)
    print(f"Wrote {len(spec)} conversations to {args.output}")


if __name__ == "__main__":
    main()
