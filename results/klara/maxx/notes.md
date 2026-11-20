# Maxx validation decision notes

At the validation-selected cutoffs, Qwen3Guard-8B rounds one and two made identical decisions on all 1,000 validation rows. Both got 990 correct, flagged 6 of 900 safe conversations, and missed 4 of 100 unsafe conversations. Phi round two got 988 correct, flagged 7 safe and missed 5 unsafe. Validation supplied both the calibration and the cutoff. The held-out test remains sealed for winner evaluation.

| Round-two evidence | Phi-4-mini | Qwen3Guard-8B |
|---|---:|---:|
| Held-scenario training predictions | 8,000 in 5 folds | 8,000 in 2 folds |
| Out-of-fold errors | 460 | 193 |
| Safe look-alikes flagged in folds | 108/800 | 68/800 |
| Other safe rows flagged in folds | 166/6,400 | 23/6,400 |
| Selected calibrated cutoff | 0.8261767844735626 | 0.01871526077324183 |
| Validation labels changed from round one | 1 | 0 |

**Phi-4-mini.** Out-of-fold predictions missed 48/74 student PII cases, 23/48 human-or-sentient claims and 14/38 eating-disorder signals. Round two repeated those weak families, look-alikes and misclassified training rows, warm-started from round one, and fitted rank-12 adapters on the last four fused QKV projections at a learning rate of 0.0001. It corrected one false positive and kept the same five validation misses.

**Qwen3Guard-8B.** Its folds missed 41/48 human-or-sentient claims, 8/32 cases of flattery and 15/60 cases of emotional manipulation. Round two repeated those families, look-alikes and misclassified training rows and fitted rank-12 residual V projections on the deployed Q4_K_S grids at 0.0001. The selected labels stayed identical, while validation PR-AUC fell from 0.9876 to 0.9852 and Brier rose from 0.0126 to 0.0129.

**Operating tradeoff.** Qwen3Guard-8B round two has the fewest classification errors, tied with its first round. Its median validation latency was 355 ms, against Phi round two's 188 ms. All four of its misses were student-triggered, including one self-harm signal. Phi caught all 24 self-harm signals but missed three assistant-triggered violations, including both personal-opinion cases. Counts by rule, trigger, turn count, clarity and safe subtype are in [round2-errors.tsv](round2-errors.tsv).

**Measurement limits.** The Phi baseline used the literal lowercase pair. On each split, 973 recognizable verdicts used a different token spelling and one lacked the configured alternative. All 974 counted wrong. Its probability metrics cover only the 26 valid responses per split. Each tuned pass returned 1,000 valid scores on each split. The baseline remains a measurement of that exact scorer contract.

**Machine time.** Phi round one's 174.86 minutes include 41 minutes 32 seconds of interrupted training recovered by restarting with a shorter fitting budget. Qwen3Guard round one took 184.14 minutes including export, verification and scoring, 4.14 minutes beyond its 180-minute end-to-end target. Cold source transfers are separate. Both round-two totals include fold fits and predictions. The R2 deployments, private tags, calibration and both rounds' adapters were retained. Rebuildable baseline and R1 exports have digest and size receipts.
