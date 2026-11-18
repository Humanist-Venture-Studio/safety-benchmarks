"""Fit validation-only Platt scaling and a cutoff on exact serving probabilities."""

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

from common import atomic_text, read_tsv, require
from pick_threshold import choose
from results import validate_run

KEYS = (
    "backend",
    "model",
    "prompt_sha256",
    "safe_token",
    "unsafe_token",
    "safe_label",
    "unsafe_label",
)


def logit(p):
    p = min(1 - 1e-7, max(1e-7, p))
    return math.log(p) - math.log1p(-p)


def apply(p, spec):
    z = spec["slope"] * logit(p) + spec["intercept"]
    e = math.exp(-abs(z))
    return 1 / (1 + e) if z >= 0 else e / (1 + e)


def main():
    import numpy as np
    from scipy.optimize import minimize

    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("results", type=Path)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--calibrated-tsv", type=Path)
    a = p.parse_args()
    rows = list(read_tsv(a.results))
    validate_run(rows)
    require(
        all(
            r["split"] == "validation" and not r.get("calibration_sha256") for r in rows
        ),
        "expected original validation predictions",
    )
    valid = [r for r in rows if not r["error"]]
    x = np.array([logit(float(r["unsafe_probability"])) for r in valid])
    y = np.array([int(r["is_unsafe"]) for r in valid])
    require(set(y) == {0, 1}, "calibration needs both classes")

    def loss(v):
        z = v[0] * x + v[1]
        return np.mean(np.logaddexp(0, z) - y * z) + 1e-4 * (v[0] - 1) ** 2

    fit = minimize(loss, [1.0, 0.0], bounds=[(0.0, None), (None, None)])
    require(fit.success, "calibration failed to converge")
    spec = {
        "slope": float(fit.x[0]),
        "intercept": float(fit.x[1]),
        "fitted_on": "validation",
        "identity": {k: rows[0][k] for k in KEYS},
        "source_sha256": hashlib.sha256(a.results.read_bytes()).hexdigest(),
    }
    for r in rows:
        r["raw_probability"] = r["unsafe_probability"]
        if not r["error"]:
            r["unsafe_probability"] = apply(float(r["raw_probability"]), spec)
    spec["threshold"], correct, fp = choose(rows)
    content = json.dumps(spec, indent=2, allow_nan=False)
    with atomic_text(a.output, replace=False) as out:
        out.write(content)
    if a.calibrated_tsv:
        digest = hashlib.sha256(content.encode()).hexdigest()
        for r in rows:
            r["threshold"] = spec["threshold"]
            r["calibration_sha256"] = digest
            if not r["error"]:
                flag = r["unsafe_probability"] >= spec["threshold"]
                r["label"] = "unsafe" if flag else "safe"
                r["correct"] = int(flag == bool(int(r["is_unsafe"])))
        with atomic_text(a.calibrated_tsv, replace=False) as out:
            writer = csv.DictWriter(
                out, rows[0].keys(), delimiter="\t", lineterminator="\n"
            )
            writer.writeheader()
            writer.writerows(rows)
    print(
        f"validation cutoff={spec['threshold']} correct={correct}/{len(rows)} false_positives={fp}"
    )


if __name__ == "__main__":
    main()
