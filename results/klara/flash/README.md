# Flash on the final Klara dataset

I recommend Qwen3Guard-Gen-0.6B round two. At the selected cutoff it scored 996/1,000 on validation, flagged one of 900 safe rows and missed three of 100 unsafe rows. Qwen3.5-2B round two also flagged one safe row and missed five unsafe rows. The two models disagreed on four rows. Qwen3Guard caught two student exploitation signals and one tutor flattery violation that Qwen3.5 missed. Qwen3.5 caught one clear personal-memory violation that Qwen3Guard missed. Qwen3Guard’s median was 31.43 ms per validation row versus 129.75 ms for Qwen3.5.

The two-row advantage is on validation data used to fit each model’s Platt calibration and cutoff. The difference is small enough that these results support retaining both candidates until selection. The test split remains sealed.

The [train-sample and validation tables](tables.md) show the raw 0.5 and selected operating points, recall, precision, AUROC, average precision, Brier score, malformed count, latency, deployment bytes, licence, training rows and machine minutes. Each split contains 900 safe and 100 unsafe conversations. The [metrics at both cutoffs](metrics.tsv), [pass metadata](pass-metadata.tsv), [retained fit recipes](fit-recipes.json) and [dataset hashes](dataset.json) accompany the per-row files. Calibration uses only valid probabilities. Malformed rows count against accuracy, and a malformed unsafe row counts as missed.

## What changed in round two

| Candidate | Held training misses / 800 | Held safe false positives, look-alike / ordinary | Weak rules repeated | Selected validation false positives, R1 → R2 | Selected validation missed unsafe, R1 → R2 |
|---|---:|---:|---|---:|---:|
| Granite Guardian 3.1 2B | 486 | 20 / 5 | S5, A2, A11 | 14 → 13 | 5 → 4 |
| Qwen3.5-2B | 218 | 104 / 20 | A4, A1, A11 | 10 → 1 | 5 → 5 |
| Qwen3Guard-Gen-0.6B | 101 | 98 / 52 | A13, A4, A1 | 5 → 1 | 7 → 3 |

**Granite.** The two short-budget replicas fitted 568 and 16 distinct rows, so their held-fold misses reflect limited exposure. The raw first-round validation model caught all 100 unsafe conversations but falsely flagged 112 safe conversations. A warm start with rank 12, half the learning rate and the Q5_K_M block grids repeated train-fold errors, weak rules and look-alikes on 1,328 distinct training rows. It gained two correct validation decisions at the selected cutoff, although AUROC fell from 0.9931 to 0.9761.

**Qwen3.5.** Safe look-alikes accounted for 104 of 124 held-fold false positives. A rank-12 residual fit on the final four full-attention V projections used the Q6_K block grids and repeated weak rules and look-alikes across 3,584 distinct optimizer rows. It removed nine validation false positives while retaining the same unsafe recall.

**Qwen3Guard.** The raw first round missed 23 validation positives at 0.5, and five training folds identified 101 missed unsafe rows and 150 false positives. Its rank-12 FP16 warm start repeated train-fold errors, weak rules and look-alikes across 7,200 distinct optimizer rows. At the selected cutoff it recovered four additional unsafe rows and removed four false positives.

All three round-two fits used learning rate 0.0001, up to two epochs and a train-only early-stop set. The two K-quant fits trained with fixed per-sub-block scales from the prior deployed artifact, then recomputed the scales during export. All chat fits used 0.05 verdict smoothing from the outset. Every tuned Flash pass returned valid first-token verdict probabilities on all 2,000 rows. [Held-fold and first-round diagnostics](diagnostics/) and [all round-two validation misses and false positives](round2-errors.tsv) give counts and denominators.

## Serving and recovery

Every tuned GGUF passed the five-length HF/GGUF token-ID, Ollama prompt-length and logit-margin checks. The largest absolute margin difference was 0.1124 rounded up. The untouched Qwen3.5 baseline returned 2,000 first attempts for which the parser could not identify a unique safe-token spelling in the top 20. Its zero contract accuracy measures the baseline under that strict parsing rule. There were no usable probabilities for calibration. [Serving checks](serving-parity.tsv)

The native guards assessed consecutive speaker prefixes under their own policies. Qwen3Guard’s conversation verdict words, counting any Unsafe first, then any Controversial, then all Safe, were 31 Unsafe, 61 Controversial and 908 Safe on the training sample. Validation had 30 Unsafe, 56 Controversial and 914 Safe. The scored native probability was the maximum per-prefix combined Unsafe and Controversial mass. The untouched F16 export contained the duplicate upstream embedding/output weights and occupied 1,509,347,456 bytes. Both tuned F16 exports occupied 1,198,178,144 bytes.

The Mac restarted after the first 252 Granite baseline training-sample results had been saved. Recovery verified those records, counted the potentially in-flight safe row K03537 as malformed and continued at the following row. Baseline machine time includes the earlier export and the 252 recorded latencies. The interrupted row’s latency field is zero because no completed measurement survived. The Granite round-two fit also encountered unsupported MPS attention dropout in a frozen block during setup. Eager attention ran with the original dropout setting. The 17-second failed setup is included in machine time. All six tuned Flash passes stayed within 90 machine minutes, including their allocated folds, export, verification and scoring.
