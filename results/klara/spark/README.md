# Spark on the final Klara dataset

Ettin round two is my recommendation for local serving. At the validation-fitted cutoff it missed six of 100 unsafe conversations and flagged one of 900 safe conversations. Mezzo missed eight and flagged one. There were eight disagreements, with Ettin correct on five and Mezzo on three. Mezzo had the higher AUROC (0.9978 versus 0.9945), and both encoders preserved all 200 sampled labels in Node. The two-row accuracy gap is on the same validation data used to fit the cutoffs.

The [two tables](tables.md) give the raw 0.5 and selected operating points. Each split contains 900 safe and 100 unsafe rows. The [metrics](metrics.tsv) and [pass metadata](pass-metadata.tsv) give interval estimates, calibration coefficients, deployment digests and machine times. The [data fingerprint](dataset.json) covers the final source and the train/validation projection. The test split remains sealed.

| Round two | Change in validation accuracy from round one | False positives, R1 → R2 | Missed unsafe, R1 → R2 |
|---|---:|---:|---:|
| Mezzo | +0.2 pp | 2 → 1 | 9 → 8 |
| Ettin | +0.4 pp | 5 → 1 | 6 → 6 |
| SmolLM2 | +0.6 pp | 18 → 9 | 17 → 20 |

**Mezzo.** Its two held training folds missed 101 unsafe rows and flagged 166 safe rows, including 111 look-alikes. The FP16 warm start repeated fold errors, look-alikes and weak rules A13, A1 and A10, using one epoch at 0.00001. The time budget allowed 3,192 distinct optimizer rows.

**Ettin.** Its folds missed 98 unsafe rows and flagged 91 safe rows, including 75 look-alikes. The FP16 warm start repeated fold errors, look-alikes and weak rules A11, A10 and A4, using one epoch at 0.00001 across 7,200 distinct optimizer rows. It removed four validation false positives at the selected cutoff.

**SmolLM2.** Its short training folds fitted 1,544 and 56 distinct rows and missed 787 of 800 unsafe rows. Round two repeated errors, look-alikes and weak rules A10, A11 and A12 with Q8_0-aware training, rank 12 and learning rate 0.0001. It removed nine validation false positives while missing three additional unsafe rows. The untouched model returned zero valid two-verdict probabilities across 2,000 first attempts.

The [round-two breakdowns](round2-errors.tsv) give errors and denominators by rule, speaker, turn count, clarity and safe look-alike status. [Fold diagnostics](diagnostics/) and [fitting recipes](fit-recipes.json) record how the training subset was picked. Warm starts, score calibration and machine-dependent subset budgeting are described in the [tuning guide](../../../scripts/klara/TUNING.md). The rehearsal used a different projection and timed subsets, so its comparison cannot isolate the effect of editing the conversations.

## Transformers.js under Node

The same seeded sample of 200 validation rows contained 33 unsafe conversations. All 600 paired scores produced the same label as the corresponding service at its fitted cutoff. These measurements used Node CPU inference. Browser WASM and WebGPU remain unmeasured.

| Round two | ONNX bytes | Package bytes | Raw probability absolute difference, max / mean | Calibrated difference, max / mean | Flips |
|---|---:|---:|---:|---:|---:|
| Mezzo | 137,408,929 | 140,994,584 | 0.005499 / 0.00002869 | 0.002362 / 0.00002938 | 0/200 |
| Ettin | 137,408,929 | 140,994,584 | 0.001668 / 0.00001845 | 0.001695 / 0.00001144 | 0/200 |
| SmolLM2 | 144,331,605 | 147,856,252 | 0.002258 / 0.00017311 | 0.002924 / 0.00010537 | 0/200 |

[Paired Node and service scores](browser/) and [serving parity checks](serving-parity.tsv) accompany the tables.
