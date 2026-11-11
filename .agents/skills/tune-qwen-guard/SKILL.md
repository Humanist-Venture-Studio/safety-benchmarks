---
name: tune-qwen-guard
description: Tune a local Qwen3Guard verdict layer on this repository's labeled request/reply pairs and evaluate the exported weights against Sileader with Ollama.
---

# Tune Qwen3Guard

Run the [README walkthrough](../../../README.md#tune-qwen3guard-on-datatsv) from the repository root. Use [scripts/tune.py](scripts/tune.py) to produce a GGUF and Modelfile in a new run directory. The source is the locally installed `sileader/qwen3guard:0.6b`. Use a fresh Humanist tag for the candidate so an existing tuned model remains available for comparison.

1. Read the TSV with its header. The label describes the **simulated assistant reply in the context of the request**. Pass only `request` and `simulated_response` to the model. Use the shared prompt and split in [scripts/benchmark.py](scripts/benchmark.py).
2. Keep both replies for a request together. The splitter also joins request IDs transitively when normalized prompts or replies repeat. Fit on `train`, select on `validation`, and reserve `test` until the candidate is fixed.
3. Run the trainer. It checks the rendered prompt against Ollama's own token IDs, fits the output weights for the first tokens of Safe, Unsafe and Controversial, and selects a regularization strength using validation logits after quantization. It copies all other GGUF bytes and carries forward the source Modelfile with a new `FROM` path.
4. Import the candidate into Ollama and evaluate **both tags** on validation. Use first-attempt CLI results to compare accuracy, unsafe replies called Safe, safe replies flagged, malformed verdicts and generation errors. Report Unsafe and Controversial counts separately even though both map to `is_safe=0`. A logit score does not check whether the model generates a complete verdict.
5. When the candidate is chosen, run the same comparison on `test` and keep the per-row TSVs. Report held-out accuracy with counts, separately from any score on the full file. If the candidate regresses, retain the baseline and describe the misses. Replacing an existing tag or publishing weights is a separate action.

## Comparing with the earlier Humanist run

For a larger weights-only experiment, reuse the same split, prompt-token check and Ollama evaluator. The earlier 45-tensor run used these additional steps.

1. Dequantize the source weights for training. Apply rank-12 low-rank updates with scale 2 to `attn_q`, `attn_v`, `attn_output` and `ffn_down` in blocks 22–27. Optimize the Safe logit against the combined probability of Unsafe and Controversial at the token after `Safety:`. Include a loss on the preceding `Safety` and `:` tokens to preserve the output format.
2. Starting from the best validation checkpoint, train updates in even-numbered blocks 12–26 and block 27. Batch both replies to each request together and add a loss that ranks the safe reply above the unsafe one. Compare checkpoints on validation. Merge the selected updates into copies of the original tensors using their original quantization types.
3. Calibrate verdict and formatting tokens on the exported model. Use the baseline’s Unsafe/Controversial judgments as a secondary signal on correctly flagged training examples. After choosing the settings, the earlier run refit the output words on training plus validation and evaluated the installed tag on all rows. Only the 624 test rows remained independent of the final fit.

The included trainer implements the smaller verdict-layer experiment. Run the CLI comparison to obtain a score for the weights it produces.

## Multi-turn conversations

For `data-multi.tsv`, use [scripts/tune_multi.py](scripts/tune_multi.py), [scripts/benchmark_multi.py](scripts/benchmark_multi.py) and [scripts/overlap_multi.py](scripts/overlap_multi.py) as the README's multi-turn section shows. They differ from the single-turn recipe in four ways.

1. The prompt renders all four turns as `Student:` and `Assistant:` lines, and the label is `consensus_rating` with three classes: `SAFE` is Safe, `FLAGGED` is Controversial and `UNSAFE` is Unsafe. Score the exact three-way match first, then Safe against flagged.
2. The split is the committed `data-multi-split.tsv`, a simple random split. The conversations are assembled from reused messages, so always report `overlap_multi.py` beside a held-out score.
3. The trainer fits each verdict row separately and adds anchors inside category names. Select on validation only, and prefer the fit that changes no anchor token: a first fit without those anchors wrote names such as `Unethical Safe`.
4. The evaluator calls Ollama's API with temperature 0. With the tag's default sampling the baseline changes its verdict on about one conversation in six, so compare tags under the same setting.
