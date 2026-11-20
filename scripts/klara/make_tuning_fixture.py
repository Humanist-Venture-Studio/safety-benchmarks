"""Write the synthetic shape-counting TSV used for local tuning and parity probes."""

import argparse
import csv
from pathlib import Path


def write_fixture(stream):
    fields = [
        "row_id",
        "scenario_id",
        "scenario_kind",
        "grade_band",
        "split",
        "turns",
        "is_unsafe",
        "rule_id",
        "trigger",
        "clarity",
    ]
    fields.extend(
        f"turn{turn}_{side}" for turn in range(1, 6) for side in ("request", "response")
    )
    writer = csv.DictWriter(stream, fields, delimiter="\t")
    writer.writeheader()
    for scenario in range(32):
        for variant in range(4):
            turns = (scenario + variant) % 5 + 1
            positive = scenario % 2 == 0 and variant < 2
            shape = "triangle" if positive else "circle"
            row = {
                "row_id": f"F{scenario:02d}-{variant}",
                "scenario_id": f"Fixture{scenario}",
                "scenario_kind": "risk" if scenario % 2 == 0 else "ordinary",
                "grade_band": "middle",
                "split": "train" if scenario < 24 else "validation",
                "turns": turns,
                "is_unsafe": int(positive),
                "rule_id": "fixture" if positive else "",
                "trigger": "student" if positive else "none",
                "clarity": "clear",
            }
            for turn in range(1, turns + 1):
                row[f"turn{turn}_request"] = (
                    f"On practice card {scenario + 1}, I see a blue {shape}. "
                    f"How do I count the objects in group {turn}?"
                )
                row[f"turn{turn}_response"] = (
                    "Use the shape key, then count the objects in that group one at a time. "
                    f"Record your answer in box {variant + 1}."
                )
            writer.writerow(row)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, help="new TSV path")
    with parser.parse_args().output.open("x", encoding="utf-8", newline="") as output:
        write_fixture(output)
