"""Verify a per-row result before reusing it for selection or reporting."""
import math

from common import require


IDENTITY = "tier backend model stage split threshold prompt_sha256 safe_token unsafe_token safe_label unsafe_label size_bytes licence".split()
FIELDS = ("row_id is_unsafe unsafe_probability label correct latency_ms raw error".split()
          + ["turns", "rule_id", "trigger", "clarity", "cost_usd"] + IDENTITY)


def validate_run(rows):
    require(rows and set(FIELDS) <= set(rows[0]), "missing per-row results or fields")
    require(len({r["row_id"] for r in rows}) == len(rows), "duplicate result row_id")
    require(len({tuple(r[k] for k in IDENTITY) for r in rows}) == 1, "mixed run metadata")
    require(len({r.get("calibration_sha256") for r in rows}) == 1, "mixed calibration")
    threshold = float(rows[0]["threshold"])
    require(0 <= threshold <= 1, "invalid threshold")
    for r in rows:
        key = r["row_id"]
        require(r["is_unsafe"] in ("0", "1"), f"{key}: bad ground truth")
        ms = float(r["latency_ms"])
        require(math.isfinite(ms) and ms >= 0, f"{key}: invalid latency")
        if r["error"]:
            require(not r["label"] and not r["unsafe_probability"] and r["correct"] == "0",
                    f"{key}: invalid error record")
        else:
            score = float(r["unsafe_probability"])
            label = "unsafe" if score >= threshold else "safe"
            correct = int((label == "unsafe") == bool(int(r["is_unsafe"])))
            require(0 <= score <= 1 and r["label"] == label and r["correct"] == str(correct),
                    f"{key}: inconsistent result")
