"""Compare a local Transformers.js export with saved first-attempt validation scores."""

import argparse
import csv
import hashlib
import json
import math
import random
import subprocess
import time
from pathlib import Path

from backends import softmax_unsafe
from calibrate import apply
from common import atomic_text, read_tsv, require
from results import validate_run
from training import transcript


def differences(rows, logits, spec):
    require(len(rows) == len(logits), "browser and served row counts differ")
    out = []
    for row, pair in zip(rows, logits):
        raw = softmax_unsafe(*pair)
        calibrated = apply(raw, spec)
        flag = calibrated >= spec["threshold"]
        observed = row["raw_probability"]
        out.append(
            dict(
                row_id=row["row_id"],
                served_raw=observed,
                browser_raw=raw,
                served_calibrated=row["unsafe_probability"],
                abs_raw=abs(raw - float(observed)) if observed else "",
                abs_calibrated=abs(calibrated - float(row["unsafe_probability"]))
                if observed
                else "",
                label_flip=int(flag != (row["label"] == "unsafe")) if observed else "",
                served_error=row["error"],
                browser_calibrated=calibrated,
            )
        )
    return out


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ("data", "browser", "scores", "calibration", "output"):
        p.add_argument("--" + name, type=Path, required=True)
    p.add_argument(
        "--chat", action="store_true", help="render the tuned Klara GGUF verdict prompt"
    )
    a = p.parse_args()
    started = time.monotonic()
    scored = sorted(read_tsv(a.scores), key=lambda r: r["row_id"])
    validate_run(scored)
    content = a.calibration.read_bytes()
    digest = hashlib.sha256(content).hexdigest()
    spec = json.loads(content)
    require(
        all(
            r["split"] == "validation"
            and r["calibration_sha256"] == digest
            and float(r["threshold"]) == spec["threshold"]
            and all(r[k] == v for k, v in spec["identity"].items())
            for r in scored
        ),
        "expected matching calibrated validation rows",
    )
    sample = random.Random(20261117).sample(scored, 200)
    needed = {r["row_id"] for r in sample}
    texts = {
        r["row_id"]: transcript(r)
        for r in read_tsv(a.data)
        if r["split"] == "validation" and r["row_id"] in needed
    }
    inputs = [texts[row["row_id"]] for row in sample]
    if a.chat:
        from backends import chat_prompt

        inputs = list(map(chat_prompt, inputs))
    result = subprocess.run(
        ["node", str(Path(__file__).with_name("browser_logits.cjs")), str(a.browser)],
        input=json.dumps(inputs),
        text=True,
        stdout=subprocess.PIPE,
        check=True,
    )
    rows = differences(sample, json.loads(result.stdout), spec)
    with atomic_text(a.output, replace=False) as f:
        w = csv.DictWriter(f, rows[0], delimiter="\t", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    valid = [r for r in rows if not r["served_error"]]
    summary = json.dumps(
        {
            "sample": len(rows),
            "unsafe_rows": sum(int(r["is_unsafe"]) for r in sample),
            "paired": len(valid),
            "seconds": time.monotonic() - started,
            "threshold": spec["threshold"],
            "graph_bytes": sum(p.stat().st_size for p in a.browser.glob("onnx/*.onnx")),
            "files_bytes": sum(
                p.stat().st_size for p in a.browser.rglob("*") if p.is_file()
            ),
            "flips": sum(r["label_flip"] for r in valid),
            **{
                op + "_" + key: fn([r[key] for r in valid]) if valid else None
                for key in ("abs_raw", "abs_calibrated")
                for op, fn in (
                    ("max", max),
                    ("mean", lambda v: math.fsum(v) / len(v)),
                )
            },
        },
        indent=2,
    )
    with atomic_text(a.output.with_suffix(".json"), replace=False) as f:
        f.write(summary + "\n")
    print(summary)


if __name__ == "__main__":
    main()
