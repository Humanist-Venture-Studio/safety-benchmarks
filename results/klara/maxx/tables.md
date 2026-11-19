Final dataset SHA-256 `0ff32b946a2e83760e90ce0974c73cedff23a6b8cbd9bd766cef155744caf294`.

## train-sample

| Candidate | Pass | Calibrated cutoff | Accuracy, raw → selected | FPR, raw → selected | Missed / 100, raw → selected | Recall | Precision | AUROC | PR-AUC | Brier | Malformed | Median ms | Bytes | Licence | Unique fit rows | Machine min |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|
| phi4 | baseline | 0.5 | 2.5% → 2.5% | 0.00% → 0.00% | 100 → 100 | 0% | — | 0.8000 | 0.1667 | 0.0406 | 974 | 132.40 | 4,084,611,456 | MIT | 0 | 5.02 |
| phi4 | r1 | 0.864668 | 98.7% → 98.9% | 1.11% → 0.44% | 3 → 7 | 93% | 95.9% | 0.9969 | 0.9615 | 0.0107 | 0 | 149.20 | 4,084,610,592 | MIT | 7200 | 174.86 |
| phi4 | r2 | 0.826177 | 98.8% → 99.0% | 0.78% → 0.33% | 5 → 7 | 93% | 96.9% | 0.9981 | 0.9780 | 0.0100 | 0 | 186.90 | 4,084,610,592 | MIT | 5040 | 163.26 |
| Always safe | Reference | — | 90.0% | 0.00% | 100 | 0% | — | 0.5000 | 0.1000 | 0.1000 | 0 | — | — | — | 0 | 0 |

## validation

| Candidate | Pass | Calibrated cutoff | Accuracy, raw → selected | FPR, raw → selected | Missed / 100, raw → selected | Recall | Precision | AUROC | PR-AUC | Brier | Malformed | Median ms | Bytes | Licence | Unique fit rows | Machine min |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|
| phi4 | baseline | 0.5 | 2.5% → 2.5% | 0.00% → 0.00% | 99 → 99 | 1% | 100.0% | 0.9583 | 0.7500 | 0.0390 | 974 | 132.60 | 4,084,611,456 | MIT | 0 | 5.02 |
| phi4 | r1 | 0.864668 | 98.6% → 98.7% | 1.22% → 0.89% | 3 → 5 | 95% | 92.2% | 0.9874 | 0.9187 | 0.0125 | 0 | 185.84 | 4,084,610,592 | MIT | 7200 | 174.86 |
| phi4 | r2 | 0.826177 | 98.6% → 98.8% | 1.22% → 0.78% | 3 → 5 | 95% | 93.1% | 0.9907 | 0.9532 | 0.0115 | 0 | 187.73 | 4,084,610,592 | MIT | 5040 | 163.26 |
| Always safe | Reference | — | 90.0% | 0.00% | 100 | 0% | — | 0.5000 | 0.1000 | 0.1000 | 0 | — | — | — | 0 | 0 |

Qwen3.5-4B replaces Granite Guardian 3.3 8B, measured at 76 backward tokens/s in preflight.
