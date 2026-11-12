# Humanist v3: mixed scope, low-rank quantization-aware tuning

Run: 2026-11-11 America/New_York, continuing into 2026-11-12 UTC. Systems Racoon fitted this model locally on an Apple M4 Max (36 GiB), Python 3.12.11, PyTorch 2.15.0 and Ollama 0.40.16. No cloud jobs, paid compute, weight publication or merge.

## Result

The validation-selected export is **experimental**: it missed 10 clear unsafe validation conversations against the predeclared limit of eight. It passed the other validation floors. The local tag is `humanist/qwen3guard:0.6b-v3-racoon-20261111-experimental`. All fitting and checkpoint selection use train/validation only. The test evaluator rejects changed data, weights, template, settings, protocol or evaluator after the freeze. The frozen GGUF SHA-256 is `a644794919068fad05a29e1db9228a6fe5c891ea12466a182325d68505e3136b`.

On the frozen test partitions, v3 scores **604/624 single-turn (96.79%)**, with 14 false-safe and six false-flag replies. Multi scores are **1,957/2,503 exact (78.19%)** and **2,020/2,503 Safe/not-Safe (80.70%)**, with 42/421 clear unsafe conversations called Safe and 147/1,570 safe conversations flagged. There were no malformed verdicts, timeouts or command errors.

V3 beats v2 on both task accuracies under the same scoped protocol and reduces multi clear-unsafe misses from 165 to 42, at the cost of ten additional safe-conversation flags (137→147). Against v2's **historical native-prompt** result, accuracy also rises and false alarms roughly halve, but clear-unsafe misses increase (33→42). That is a useful aggregate improvement with a safety tradeoff, not an unqualified replacement. I kept the experimental label and preserved every existing tag.

## What the model assesses

These are two different tasks. `data.tsv` labels the **final assistant reply in context**: a safe refusal to a dangerous request can be Safe. `data-multi.tsv`'s `consensus_rating` labels **risk anywhere in the conversation**, including the student. For example, training-only single-turn refusal pairs REQ0576/0578/0579 demonstrate why student risk cannot automatically make the reply unsafe. The multi labeling rubric includes student-originated risk even when the assistant responds safely.

I chose explicit assessment scope because one undifferentiated rubric would contradict the supplied labels. Both tasks use the identical `Student:` / `Assistant:` serialization, preserving every message and all relevant turns. The caller explicitly chooses `reply` or `conversation`; scope is task intent, not a ground-truth label. Labels, category, trigger source, ID, file name and split are absent from model input. The instructions are in `v3_protocol.SCOPES`; the common wrapper is `template-scoped.txt`.

Both scopes accept any number of complete student/assistant pairs. **Only one-turn/reply and four-turn/conversation have labeled training and evaluation here.** Accuracy for the other scope/length combinations is unestablished; the explicit instruction does not prove that the model has eliminated every correlation between length and task. No relabeling or synthetic bridge examples were introduced.

For local inference from the repository root, explicitly include the chosen scope:

```python
import os
import subprocess
import sys
sys.path.insert(0, ".agents/skills/tune-qwen-guard/scripts")
from v3_protocol import prompt

pairs = [("How can I stay focused on homework?", "Try one task at a time and take short breaks.")]
subprocess.run(
    ["ollama", "run", "humanist/qwen3guard:0.6b-v3-racoon-20261111-experimental",
     prompt(pairs, scope="reply")],
    env=dict(os.environ, OLLAMA_HOST="127.0.0.1:11434"), check=True,
)
```

Use `scope="conversation"` to assess both speakers, and supply every pair in order. A bare chat without the assessment instruction is outside the evaluated contract.

Output is `Safety: Safe`, `Safety: Unsafe` or `Safety: Controversial`, followed by a `Categories:` line. Single-turn supervision marginalizes over Unsafe and Controversial for `is_safe=0`. Multi supervision maps SAFE→Safe, UNSAFE→Unsafe and FLAGGED→Controversial. FLAGGED is consensus disagreement, an imperfect operational target for the model's ambiguity class. Category names are preserved as formatting, not independently scored labels.

## Data and ancestry

| Input | SHA-256 |
| --- | --- |
| `data.tsv` | `3cfa5780d06145c4b0bf86c63431568b13da8f7ca9a9dba203f5cecca9cc686e` |
| `data-multi.tsv` | `ca9c8022d7aea03beeddbc9d1b9ffac38877f97c3039e8c556c1891a2edefc7e` |
| `data-multi-template-split.tsv` | `5b45aed4ef5bbdcbeb34f69c775ea2fa8ebaca7482d1e089e9198f141ad7e0e3` |

Single-turn grouping is unchanged: 2,822 train / 462 validation / 624 test. The exact PR #8 manifest is unchanged: 5,849 train / 1,000 validation / 2,503 test, with 648 arc/module straddlers excluded. In-memory source replay reproduced all 10,000 multi rows; no dataset was regenerated on disk. The current catalog contained 780 template groups, no near-copy edges and no shared retained groups. Normalized same-role message and full-pair comparisons found zero cross-file collisions, so no additional training exclusions were needed. The checker would exclude conflicting or held-out-overlapping training rows rather than move test data.

The only external starting weights were installed `sileader/qwen3guard:0.6b`. Neither v1, v2 nor the prior single-turn model was a warm start. Later fits started from this run's own train-only exports. Validation selected checkpoints and regularization; it was never added to the fit. Test material was read for split hygiene but never tokenized into training features or used for error-driven changes.

Reusable code was recovered without changing earlier branches: PR #8 at `8094ea2204b2416b7c26b79752a5cf32eff019f8` supplies the exact manifest/template splitter; PR #9 at `aaa7a5ed46526124902732d9ca6219a7ea37d1e9` supplies the PyTorch forward and quantization helpers. PR #7 was `33d141cd3ae7419188bcf2e1c21d35643ec95a83`. This PR is self-contained against main and does not require merging those PRs first.

## Runtime contract and comparisons

All models use temperature 0, seed 0, context 2,048 and maximum output 48, baked into fresh local Modelfiles. Each row gets one actual `ollama run` CLI attempt, with a 120-second deadline and four local workers. Timeouts, command failures and malformed complete first-line verdicts count as errors; partial output is retained and never silently retried. Unsafe and Controversial stay separate in saved results. Prompt-length checks reject truncation.

The installed Ollama runtime preferred the GGUF's native Jinja chat template over a changed Modelfile Go template. This was discovered before benchmark scoring. `v3_export.py` patches a fresh copy's native template using fixed-length padding, preserving tensor offsets and other metadata. Comparator copies receive the same patch and settings with **all tensor bytes unchanged**. Actual generation token parity is checked on training probes for every evaluated model; the original tags remain untouched. These comparator scores describe the new scoped contract, not their original prompts.

The scoped wrapper weakened v2 on validation. To avoid manufacturing a win by handicapping the comparator, selection was tightened **after comparator-only validation and before any candidate fitting** with additional native-v2 floors. Original and amended plans are retained.

## Selection rule and experiments

No pooled task accuracy determines selection. A feasible candidate must achieve all of:

- Single-turn ≥439/462 and at least same-contract v2 accuracy; false-safe ≤12 and no more than v2+2.
- Multi exact ≥809/1,000 and binary ≥831/1,000, each also at least same-contract v2.
- Multi UNSAFE called Safe ≤8 and no more than v2+2; SAFE flagged ≤30 (same-contract v2+7).
- Zero failed or malformed verdict generations.

The native-v2 floor uses 809 exact from prior CLI validation, and 831 binary plus six clear-unsafe misses from its quantized validation checkpoint; those prior measurements are explicitly mixed provenance. Feasible candidates rank by multi exact, single accuracy, multi binary, then fewer severe misses. If none qualifies, minimize the largest normalized floor violation, then those tie-breakers, and label the final export experimental. This rule stayed fixed throughout fitting. The plan allowed at most three purposeful deeper fits; two were performed.

Each update receives equal total single/multi task weight. The head baseline fits three verdict rows using binary marginal single and three-way multi losses. The deeper runs train rank-12, scale-2 adapters on q/v/attention-output/FFN-down weights in blocks 20–27: 32 tensors, approximately 1.18 million adapter parameters affecting 67,108,864 original weights. All 32 had nonzero initial gradients and changed exported weights. Quantization-aware training uses the original Q4_K/Q6_K grids; exported decoded values match the training grid within 1e-7. This is substantive transformer training, not solely a final-head change.

The inspected v2 low-rank implementation trained `attn_v` and `ffn_down` in the top five blocks, selected floating-point adapter checkpoints and quantized at export; its reported gain was only 0.3 points on the old validation selection score. V3 therefore checks trainability and quantized checkpoints during fitting, expands the trainable projections, preserves task balance and evaluates separate acceptance floors. More parameters were a hypothesis to test, not evidence of a guaranteed improvement.

Frozen lower-layer activations accelerate training. Their float16 cache measured at most 0.00142 sampled verdict-logit error; the model forward matched llama-server hidden vectors with cosine 0.999985–0.999992. Formatting-token full-vocabulary KL and safe/unsafe paired ranking constrain updates. Final output rows other than the three verdict tokens remain unchanged.

The first deeper fit used two epochs (1,464 updates), learning rate 0.0006, task batches of eight, microbatches of four, format KL 0.5 and pair ranking 0.1. Its early checkpoints overflagged harmless conversations; quantized validation selected step 1,464. Post-fit head calibration exposed poor optimizer convergence: all six original 400-iteration fits hit the limit. Cholesky preconditioning of the same objective converged the six fits in 43–175 iterations. It helped the deeper model, although the converged head alone did not outperform the original head.

The second deeper fit used the converged calibrated export, one epoch, learning rate 0.0003, microbatches of eight, format KL 1.0, normalized multi UNSAFE weight 1.5 and KL 0.5 retaining the source model's **correct training predictions**. This addresses the observed train/validation loss of useful behavior without changing labels or adding keyword rules. Checkpoints and patience were bounded; rejected configurations and their validation metrics are retained. No candidate changes were made after test freeze.

### Exported validation (actual first attempts)

| Model / candidate | Single correct | Single false-safe / false-flag | Multi exact | Multi binary | UNSAFE→Safe | SAFE flagged |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Sileader | 391/462 | 44 / 27 | 663/1000 | 766/1000 | 54/139 | 66/689 |
| V2 | 416/462 | 38 / 8 | 761/1000 | 774/1000 | 55/139 | 23/689 |
| Prior Racoon | 372/462 | 88 / 2 | 689/1000 | 689/1000 | 139/139 | 0/689 |
| Head baseline (400 iterations) | 432/462 | 12 / 18 | 812/1000 | 822/1000 | 16/139 | 25/689 |
| Head, converged | 437/462 | 9 / 16 | 804/1000 | 817/1000 | 13/139 | 22/689 |
| QAT 1 | 444/462 | 5 / 13 | 810/1000 | 832/1000 | 11/139 | 37/689 |
| QAT 1 + head (400 iterations) | 443/462 | 4 / 15 | 812/1000 | 833/1000 | 10/139 | 33/689 |
| QAT 1 + converged head | 443/462 | 4 / 15 | 818/1000 | 840/1000 | 10/139 | 25/689 |
| QAT 2, selected | 446/462 | 4 / 12 | 819/1000 | 841/1000 | 10/139 | 18/689 |

Every row in this table has zero malformed verdicts, timeouts or command errors. Selection used these actual CLI results, not just logits. QAT 2 step 300 won the predeclared fallback ranking, but missed the clear-unsafe ceiling (10 versus 8); all other validation floors passed. I stopped after the two substantive deeper fits because gains had concentrated on false alarms while the same missed-risk class persisted. No post-test search was authorized by this protocol.

The selected validation FLAGGED rows were called Safe 131/172, Controversial 24/172 and Unsafe 17/172. Of 139 consensus UNSAFE rows, 10 were called Safe: 6/63 carrying original student triggers, 0/72 assistant triggers and 4/4 originally marked `none`. Trigger metadata comes from the original dataset, not an inferred consensus trigger. This mismatch between original trigger and consensus safety is retained, not relabeled away.


## Frozen test results

Each model was evaluated once on the same 624 single-turn and 2,503 multi-turn test rows. These are the new explicit-scope protocol scores; no historical comparator cache was reused.

| Model | Single correct | Single false-safe / false-flag | Multi exact | Multi binary | UNSAFE→Safe /421 | SAFE flagged /1,570 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Sileader | 532/624 (85.26%) | 57 / 35 | 1,580/2,503 (63.12%) | 1,847/2,503 (73.79%) | 108 | 298 |
| V2 | 545/624 (87.34%) | 67 / 12 | 1,777/2,503 (70.99%) | 1,839/2,503 (73.47%) | 165 | 137 |
| Prior Racoon | 492/624 (78.85%) | 132 / 0 | 1,577/2,503 (63.00%) | 1,577/2,503 (63.00%) | 413 | 1 |
| V3 experimental | 604/624 (96.79%) | 14 / 6 | 1,957/2,503 (78.19%) | 2,020/2,503 (80.70%) | 42 | 147 |

### Historical native-v2 context (different prompt)

The [PR #8 report](https://github.com/Humanist-Venture-Studio/safety-benchmarks/blob/8094ea2204b2416b7c26b79752a5cf32eff019f8/reports/qwen3guard-fable-v2.md) supplies these original scores. This table describes the practical tradeoff across the two recipes; it does not isolate a weight-only improvement because scope instructions, wrapper and inference protocol changed.

| Metric | Native v2 historical | V3 scoped |
| --- | ---: | ---: |
| Single correct | 590/624 (94.55%) | 604/624 (96.79%) |
| Single false-safe / false-flag | 15 / 19 | 14 / 6 |
| Multi exact | 1,906/2,503 (76.15%) | 1,957/2,503 (78.19%) |
| Multi binary | 1,955/2,503 (78.11%) | 2,020/2,503 (80.70%) |
| UNSAFE called Safe | 33/421 | 42/421 |
| SAFE flagged | 297/1,570 | 147/1,570 |

The native-v2 comparison's additional clear-unsafe misses are not evenly distributed: student-triggered misses improve 22→18, assistant-triggered misses worsen 10→21, and originally untriggered consensus UNSAFE misses worsen 1→3. FLAGGED handling also worsens relative to native v2: 294 rather than 218 of 512 are called Safe. These are post-freeze descriptions, not inputs to another fitting round.

### Multi three-way counts

Rows are consensus labels; columns are actual model outputs. This includes the FLAGGED class, rather than hiding it inside binary accuracy.

| Model | Consensus | Safe | Controversial | Unsafe |
| --- | --- | ---: | ---: | ---: |
| Sileader | SAFE | 1272 | 292 | 6 |
| Sileader | FLAGGED | 250 | 260 | 2 |
| Sileader | UNSAFE | 108 | 265 | 48 |
| V2 | SAFE | 1433 | 107 | 30 |
| V2 | FLAGGED | 362 | 116 | 34 |
| V2 | UNSAFE | 165 | 28 | 228 |
| Prior Racoon | SAFE | 1569 | 1 | 0 |
| Prior Racoon | FLAGGED | 512 | 0 | 0 |
| Prior Racoon | UNSAFE | 413 | 0 | 8 |
| V3 experimental | SAFE | 1423 | 118 | 29 |
| V3 experimental | FLAGGED | 294 | 171 | 47 |
| V3 experimental | UNSAFE | 42 | 16 | 363 |

### Original trigger-source breakdown

`trigger_source` is the original author label. It can disagree with consensus safety. The three consensus UNSAFE rows with `none` remain in the score.

| Model | Original trigger | Rows | Exact | Binary | UNSAFE→Safe / UNSAFE rows |
| --- | --- | ---: | ---: | ---: | ---: |
| Sileader | student | 212 | 14 | 138 | 54 / 184 |
| Sileader | assistant | 234 | 42 | 181 | 53 / 234 |
| Sileader | none | 2057 | 1524 | 1528 | 1 / 3 |
| V2 | student | 212 | 73 | 88 | 100 / 184 |
| V2 | assistant | 234 | 158 | 171 | 63 / 234 |
| V2 | none | 2057 | 1546 | 1580 | 2 / 3 |
| Prior Racoon | student | 212 | 0 | 0 | 184 / 184 |
| Prior Racoon | assistant | 234 | 8 | 8 | 226 / 234 |
| Prior Racoon | none | 2057 | 1569 | 1569 | 3 / 3 |
| V3 experimental | student | 212 | 163 | 179 | 18 / 184 |
| V3 experimental | assistant | 234 | 205 | 213 | 21 / 234 |
| V3 experimental | none | 2057 | 1589 | 1628 | 3 / 3 |

### Output and execution counts

| Model | Task | Safe | Unsafe | Controversial | Malformed | Timeout | Command error |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Sileader | single | 334 | 93 | 197 | 0 | 0 | 0 |
| Sileader | multi | 1630 | 56 | 817 | 0 | 0 | 0 |
| V2 | single | 367 | 242 | 15 | 0 | 0 | 0 |
| V2 | multi | 1960 | 292 | 251 | 0 | 0 | 0 |
| Prior Racoon | single | 444 | 48 | 132 | 0 | 0 | 0 |
| Prior Racoon | multi | 2494 | 8 | 1 | 0 | 0 | 0 |
| V3 experimental | single | 320 | 301 | 3 | 0 | 0 | 0 |
| V3 experimental | multi | 1759 | 439 | 305 | 0 | 0 | 0 |


## Reproduction and durable artifacts

Artifacts are local at:

`/Users/alexsieke/Desktop/BOTS/systems-racoon/scratch.noindex/humanist-v3-20261111/`

This directory retains original/amended plans, environment and package versions, immutable input copies, full split assignment, template replay/parity audits, source snapshots, per-fit configurations/history, selected checkpoint weights and adapters, comparator source hashes, first-attempt raw responses, per-row TSVs, summaries, provenance, final GGUF/Modelfile and freeze manifest. Bulky activation caches and model binaries remain outside Git. The report and scripts are reviewable in this PR.

Use Python 3.12 with the versions in `requirements-frozen.txt`, local Ollama and the recent llama-server used by `prepare_v3.py`. This experiment currently uses the macOS Ollama application path for llama-server. Run heavy commands one at a time through `/tmp/botchu-coord/gate.sh run`. Set `OLLAMA_HOST=127.0.0.1:11434`. Choose a fresh artifact directory and fresh model tags; the scripts refuse to overwrite evaluation files.

The portable CLI sequence for the selected ancestry is below; variables `py`, `skill` and `run` name the interpreter, repository skill directory and fresh artifact directory. `baseline` is a same-contract v2 validation summary generated with `evaluate_v3.py`, not a test result. Comparator preparation uses `v3_export.patch_template()` on copies and `v3_protocol.definition()` for identical settings. The retained `baseline.py` records the actual comparator preparation and commands.

```bash
"$py" -B "$skill/scripts/prepare_v3.py" --out "$run/prepared"
"$py" -B "$skill/scripts/head_v3.py" --prepared "$run/prepared" --out "$run/head" --baseline "$baseline"
"$py" -B "$skill/scripts/train_v3.py" --prepared "$run/prepared" --model "$run/head/candidate.gguf" --out "$run/qat1" --baseline "$baseline"
"$py" -B "$skill/scripts/refeature_v3.py" --prepared "$run/prepared" --model "$run/qat1/step-1464/candidate.gguf" --out "$run/qat1-features"
"$py" -B "$skill/scripts/head_v3.py" --prepared "$run/qat1-features" --out "$run/qat1-calibrated-converged" --baseline "$baseline" --precondition --maxiter 1200
"$py" -B "$skill/scripts/train_v3.py" --prepared "$run/prepared" --model "$run/qat1-calibrated-converged/candidate.gguf" --out "$run/qat2" --baseline "$baseline" --epochs 1 --micro-batch 8 --lr .0003 --format-weight 1 --retain-weight .5 --unsafe-weight 1.5 --eval-every 150 --patience 3 --seed 20261114
```

The step-1464 path is the selected first-run checkpoint from this run; for a new run read its `best.json`. Install and CLI-validate candidates before selection. Run `freeze_v3.py --help` for the required validation-evidence and comparator arguments, then `evaluate_v3.py --split test --freeze "$run/freeze.json"` once per frozen model. The retained runner scripts and configs record exact paths and commands actually executed. A new training run need not reproduce identical MPS floating-point weights; hashes identify these particular exports.

Machine-readable metrics are in [qwen3guard-v3-metrics.json](qwen3guard-v3-metrics.json). `audit_v3.py` independently parses each raw first response, checks every row's frozen identity, target, prompt hash and correctness, recounts the tables, checks comparator tensors against their original sources, limits final tensor changes to the 32 projections and three verdict rows, and verifies the original local tags are unchanged. Its retained result is `recount.json`; `artifact-checksums.json` covers the durable result bundle. The author checks are this audit and `git diff --check`, followed by a fresh Tier M verification. No repository-specific merge commands or named GitHub approvers were prescribed; no new test suite was introduced.

## Limits

- Both historical test partitions have been reused in prior model experiments. This is one frozen evaluation per model on those partitions, **not a newly untouched generalization estimate**.
- Synthetic stories, template repetition and consensus disagreement limit applicability to real student chats. No external safety benchmark or live student deployment was evaluated.
- Off-diagonal scope/length combinations and semantic correctness of the Categories line were not validated. Prompt token parity and category-line syntax were checked.
- Native historical scores and new scoped scores are different protocols. In particular, the prior Racoon 603/624 uses the legacy prompt and cannot be treated as a controlled comparison to v3.
- No deployment, merge, replacement of existing tags or weight publication is part of this task.
