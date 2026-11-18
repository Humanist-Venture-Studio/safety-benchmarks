"""Allocate scenario groups, then shuffle exact turn and trigger-position quotas."""
import argparse
import json
import random
import re
from collections import Counter
from pathlib import Path

from common import GRADES, RULES, SHARDS, SPLITS, WORK, atomic_text, check_quotas, jsonl, require, rules_table

VOICES = ("terse", "asks follow-ups", "thinks aloud", "uses analogies", "informal", "precise")
MOODS = ("curious", "uncertain", "focused", "frustrated", "playful", "reflective")


def make_slots(seeds, rules, seed):
    rng = random.Random(seed)
    seeds = sorted(seeds, key=lambda s: s["scenario_id"])
    require(len({s["scenario_id"] for s in seeds}) == len(seeds) == 1250, "expected 1,250 unique seeds")
    pools = {"risk": [], "ordinary": []}
    for s in seeds:
        key = s["scenario_id"]
        require(re.fullmatch(r"S\d{4}", key) and s["grade_band"] in GRADES, f"{key}: invalid ID or grade")
        for field in ("subject", "category", "situation"):
            require(isinstance(s[field], str) and s[field].strip(), f"{key}: empty {field}")
        if s["kind"] == "risk":
            rule = rules[s["rule_id"]]
            require(s["trigger"] in ("student", "assistant") and rule["trigger_side"] in (s["trigger"], "either")
                    and rule["required_action"].strip(), f"{key}: incompatible rule or trigger")
            require(float(rule["weight"]) > 0, f"{key}: risk seed for a zero-weight rule")
            for field in ("unsafe_sketch", "look_alike_sketch"):
                require(isinstance(s[field], str) and s[field].strip(), f"{key}: missing {field}")
        pools[s["kind"]].append(s)
    require(len(pools["risk"]) == 500, "expected 500 risk and 750 ordinary seeds")
    shards = [[] for _ in range(25)]
    for kind_index, pool in enumerate(pools.values()):
        rng.shuffle(pool)
        start = 0
        for split, sizes in SPLITS.items():
            for i, s in enumerate(pool[start:start + sizes[kind_index]]):
                shards[i % 25].append((s, split))
            start += sizes[kind_index]
    slots = []
    for shard, group in enumerate(shards, 1):
        rng.shuffle(group)
        for s, split in group:
            first = len(slots) + 1
            for i in range(8):
                unsafe = s["kind"] == "risk" and i < 2
                similar = s["kind"] == "risk" and 2 <= i < 4
                slots.append(dict(row_id=f"K{first + i:05d}", shard=shard, split=split,
                                  scenario_id=s["scenario_id"], scenario_kind=s["kind"],
                                  row_role="unsafe" if unsafe else "look_alike" if similar else "ordinary",
                                  grade_band=s["grade_band"], subject=s["subject"], category=s["category"],
                                  is_unsafe=int(unsafe), rule_id=s["rule_id"] if unsafe else "",
                                  trigger=s["trigger"] if unsafe else "none", trigger_turn=0, clarity="clear",
                                  look_alike_of=f"K{first + i - 2:05d}" if similar else "",
                                  student_voice=rng.choice(VOICES), mood=rng.choice(MOODS)))
    for split in SPLITS:
        for unsafe in (0, 1):
            rows = [r for r in slots if r["split"] == split and r["is_unsafe"] == unsafe]
            rng.shuffle(rows)
            for i, row in enumerate(rows):
                row["turns"] = i % 5 + 1
                if unsafe:
                    row["trigger_turn"] = (i // 5) % row["turns"] + 1
            if unsafe:
                for row in rng.sample(rows, len(rows) // 10):
                    row["clarity"] = "borderline"
    check_quotas(slots)
    return slots


def write_slots(path, rows):
    content = "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows)
    if path.exists():
        require(path.read_text(encoding="utf-8") == content, f"{path}: different allocation; use a fresh directory")
        return
    with atomic_text(path) as dst:
        dst.write(content)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--seeds", type=Path, default=WORK / "seeds/seeds.jsonl")
    p.add_argument("--rules", type=Path, default=RULES)
    p.add_argument("--out-dir", type=Path, default=SHARDS)
    p.add_argument("--seed", type=int, default=20261117)
    args = p.parse_args()
    seeds = list(jsonl(args.seeds))
    rules = rules_table(args.rules)
    slots = make_slots(seeds, rules, args.seed)
    lookup = {s["scenario_id"]: s for s in seeds}
    write_slots(args.out_dir / "slots.jsonl", slots)
    for shard in range(1, 26):
        rows = []
        for slot in slots:
            if slot["shard"] == shard:
                s = lookup[slot["scenario_id"]]
                rows.append({**slot, **{k: s.get(k, "") for k in ("situation", "unsafe_sketch", "look_alike_sketch")},
                             "scenario_rule_id": s.get("rule_id", ""), "scenario_trigger": s.get("trigger", "none")})
        write_slots(args.out_dir / f"shard-{shard:02}.slots.jsonl", rows)
    counts = Counter(r["rule_id"] for r in slots if r["is_unsafe"])
    print(f"{len(slots)} slots; 25 shards; 1,000 unsafe; rule counts {dict(sorted(counts.items()))}")


if __name__ == "__main__":
    main()
