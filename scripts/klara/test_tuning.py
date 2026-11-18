"""Headless selection and probability regression probes. No downloads or model runtime."""

import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from calibrate import apply
from metrics import metrics
from training import fingerprint, missed_ids, partition


class GuardTuningChecks(unittest.TestCase):
    def test_tied_pr_auc_brier_and_missing_output(self):
        rows = [
            {
                "is_unsafe": y,
                "unsafe_probability": p,
                "label": label,
                "error": error,
                "latency_ms": 1,
            }
            for y, p, label, error in [
                (1, 0.8, "unsafe", ""),
                (0, 0.8, "unsafe", ""),
                (1, 0.3, "safe", ""),
                (0, 0.1, "safe", ""),
                (1, "", "", "missing"),
            ]
        ]
        report = metrics(rows)
        self.assertEqual(report["PR-AUC (AP)"], "0.5833")
        self.assertEqual(report["Brier"], "0.2950")
        self.assertEqual(report["missed/unsafe"], "2/3")
        self.assertAlmostEqual(apply(0.25, {"slope": 1, "intercept": 0}), 0.25)

    def test_grouped_oof_rejects_leakage_and_incomplete_coverage(self):
        rows = [
            {
                "scenario_id": f"s{i}",
                "scenario_kind": ("ordinary", "risk")[i % 2],
                "grade_band": "middle",
                "row_id": f"r{i}-{j}",
                "split": "train",
                "is_unsafe": str(int(i % 2 and j == 0)),
            }
            for i in range(20)
            for j in range(2)
        ]
        a = SimpleNamespace(seed=42, folds=2, fold=None, source=Path("/fixture"))
        _, _, _, folds = partition(rows, a)
        paths = []
        with tempfile.TemporaryDirectory() as tmp:
            for i in range(2):
                a.fold = i
                train, dev, held, _ = partition(rows, a)
                fit_ids = {r["scenario_id"] for r in train + dev}
                self.assertTrue(fit_ids.isdisjoint(r["scenario_id"] for r in held))
                self.assertEqual(
                    {r["scenario_kind"] for r in held}, {"ordinary", "risk"}
                )
                self.assertFalse(
                    {r["scenario_id"] for r in train} & {r["scenario_id"] for r in dev}
                )
                doc = {
                    "source": str(a.source),
                    "train_sha256": fingerprint(rows),
                    "seed": a.seed,
                    "folds": 2,
                    "fold": i,
                    "predictions": {r["row_id"]: 0 for r in held},
                    "fit_scenarios": sorted(fit_ids),
                }
                path = Path(tmp) / f"{i}.json"
                path.write_text(json.dumps(doc))
                paths.append(path)
            a.fold = None
            self.assertEqual(
                missed_ids(paths, rows, folds, a),
                {r["row_id"] for r in rows if r["is_unsafe"] == "1"},
            )
            with self.assertRaisesRegex(ValueError, "incomplete"):
                missed_ids(paths[:1], rows, folds, a)
            doc["fit_scenarios"].append(held[0]["scenario_id"])
            path.write_text(json.dumps(doc))
            with self.assertRaisesRegex(ValueError, "leakage"):
                missed_ids(paths, rows, folds, a)


if __name__ == "__main__":
    unittest.main()
