"""Shared schemas and file handling for the Klara pipeline."""
import csv
import json
import math
import os
import tempfile
from collections import Counter, defaultdict
from contextlib import contextmanager
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORK = Path.home() / "klara-tiers"
SHARDS = WORK / "shards"
RULES = ROOT / "data/rules-klara.tsv"
DATA = ROOT / "data/data-klara.tsv"
SPLITS = {"train": (400, 600), "validation": (50, 75), "test": (50, 75)}
GRADES = {"elementary_3_5", "middle_6_8", "high_9_12"}
META = "row_id split scenario_id scenario_kind turns grade_band subject category".split()
TURN_FIELDS = [f"turn{i}_{side}" for i in range(1, 6) for side in ("request", "response")]
LABEL_FIELDS = "is_unsafe rule_id trigger trigger_turn required_action clarity look_alike_of".split()
COLUMNS = META + TURN_FIELDS + LABEL_FIELDS


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def jsonl(path):
    with path.open(encoding="utf-8") as src:
        for number, line in enumerate(src, 1):
            try:
                row = json.loads(line)
                require(isinstance(row, dict), "expected a JSON object")
            except ValueError as exc:
                raise ValueError(f"{path}:{number}: {exc}") from exc
            yield row


def read_tsv(path):
    with path.open(encoding="utf-8", newline="") as src:
        yield from csv.DictReader(src, delimiter="\t")


def rules_table(path):
    result = {}
    for row in read_tsv(path):
        key = row["rule_id"]
        require(key and key not in result, f"missing or duplicate rule_id {key!r}")
        require(row["trigger_side"] in ("either", "assistant", "student"), f"{key}: invalid trigger_side")
        weight = row["weight"].strip()
        value = float(weight.removesuffix("%"))
        require(math.isfinite(value) and value >= 0, f"{key}: invalid weight")
        row["weight"] = value / 100 if weight.endswith("%") else value
        result[key] = row
    require(result, "empty rule table")
    return result


@contextmanager
def atomic_text(path, *, replace=True):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="", dir=path.parent,
                                     delete=False) as dst:
        try:
            yield dst
            dst.close()
            if replace:
                os.replace(dst.name, path)
            else:
                os.link(dst.name, path)
        finally:
            Path(dst.name).unlink(missing_ok=True)


def messages_from_tsv(row):
    return [{"role": role, "content": row[f"turn{i}_{side}"]}
            for i in range(1, int(row["turns"]) + 1)
            for role, side in (("student", "request"), ("tutor", "response"))]


def check_quotas(slots):
    by_id = {r["row_id"]: r for r in slots}
    expected_ids = {f"K{i:05d}" for i in range(1, 10001)}
    require(len(slots) == 10000 and by_id.keys() == expected_ids, "expected K00001..K10000 once each")
    scenarios, shards = defaultdict(list), defaultdict(list)
    counts, kinds = Counter(), Counter()
    for r in slots:
        ident = r["row_id"]
        scenarios[r["scenario_id"]].append(r)
        shards[r["shard"]].append(r)
        counts[r["split"], r["turns"], r["is_unsafe"]] += 1
        require(r["clarity"] in ("clear", "borderline"), f"{ident}: invalid clarity")
        if r["is_unsafe"]:
            require(r["row_role"] == "unsafe" and r["rule_id"] and not r["look_alike_of"]
                    and r["trigger"] in ("student", "assistant")
                    and 1 <= r["trigger_turn"] <= r["turns"], f"{ident}: invalid unsafe slot")
        else:
            require(r["row_role"] in ("ordinary", "look_alike") and not r["rule_id"]
                    and r["trigger"] == "none" and r["trigger_turn"] == 0
                    and r["clarity"] == "clear", f"{ident}: invalid safe slot")
            other = by_id.get(r["look_alike_of"])
            if r["row_role"] == "look_alike":
                require(other and other["is_unsafe"] and other["scenario_id"] == r["scenario_id"],
                        f"{ident}: invalid look-alike reference")
            else:
                require(not r["look_alike_of"], f"{ident}: unexpected look-alike reference")
    for key, rows in scenarios.items():
        first = rows[0]
        require(len(rows) == 8 and all(len({r[k] for r in rows}) == 1 for k in
                ("split", "shard", "scenario_kind", "grade_band", "category", "subject")),
                f"{key}: scenario spread or inconsistent")
        risk = first["scenario_kind"] == "risk"
        require(sum(r["is_unsafe"] for r in rows) == (2 if risk else 0), f"{key}: unsafe quota")
        require(not risk or sum(r["row_role"] == "look_alike" for r in rows) >= 2, f"{key}: look-alike quota")
        kinds[first["split"], first["scenario_kind"]] += 1
    for split, (risk, ordinary) in SPLITS.items():
        require((kinds[split, "risk"], kinds[split, "ordinary"]) == (risk, ordinary), f"{split}: scenarios")
        for t in range(1, 6):
            total = (risk + ordinary) * 8 // 5
            require((counts[split, t, 0], counts[split, t, 1]) == (9 * total // 10, total // 10),
                    f"{split}: turn-{t} label quota")
    require(set(shards) == set(range(1, 26)), "shard numbers")
    for number, group in shards.items():
        require(len(group) == 400 and {r["split"] for r in group} == SPLITS.keys()
                and len({r["scenario_kind"] for r in group}) == 2
                and {r["turns"] for r in group} == set(range(1, 6)), f"shard {number}: size or mix")
    require(sum(r["clarity"] == "borderline" for r in slots) <= 100, "borderline quota")
