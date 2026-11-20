# Klara fixture preflight on the M4 Max

The table uses decimal GB. Training throughput counts nonpadding tokens in optimizer steps with backward passes. RAM is the Darwin peak training-process footprint. Disk is the sampled allocation of the entire task tree during that run. Encoder model size is the FP16 TEI package. Chat sizes are the actual merged GGUFs. Q8_0 and F16 are written directly. A zero quantizer time indicates a single conversion.

| Model | Training tok/s | Peak RAM GB | Model GB | Peak task disk GB | Tokens/row | Probe result | Valid scores |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Mezzo Small | 7,459 | 4.42 | 0.140 | 26.08 | 189 | tei 0.017, transformers.js 0.240 | 32/32 |
| Ettin 68M | 7,437 | 4.41 | 0.140 | 26.29 | 189 | tei 0.007, transformers.js 0.005 | 32/32 |
| SmolLM2 135M | 3,156 | 3.73 | 0.145 | 26.29 | 277 | 5/5, Δ 0.241 | 32/32 |
| Granite Guardian 3.1 2B | 526 | 21.65 | 1.805 | 26.04 | 280 | 5/5, Δ 0.159 | 32/32 |
| Qwen3.5-2B | 649 | 13.36 | 1.556 | 23.01 | 267 | 5/5, Δ 0.197 | 32/32 |
| Qwen3Guard-0.6B | 1,338 | 8.82 | 1.198 | 18.39 | 265 | 5/5, Δ 0.331 | 32/32 |
| Phi-4-mini | 445 | 17.50 | 4.085 | 31.42 | 262 | 5/5, Δ 0.190 | 32/32 |
| Qwen3Guard-8B | 238 | 25.75 | 4.802 | 48.90 | 265 | 5/5, Δ 0.219 | 32/32 |
| Granite Guardian 3.3 8B¹ | 76 | 26.27 | 4.943 | 48.96 | 280 | 5/5, Δ 0.211 | 32/32 |
| Qwen3.5-4B | 273 | 27.15 | 4.482 | 39.14 | 267 | 5/5, Δ 0.035 | 32/32 |

## Round one

| Model | 8k backward min | Merge / convert / quant s | Score 2k min | Round 1 min² | 8k backward + export + score fits? | Fit rows in box³ |
| --- | --- | --- | --- | --- | --- | --- |
| Mezzo Small | 5.4 | 0.0 / 2.0 / 2.0 | 0.7 | 6.2 | yes | 7,200 |
| Ettin 68M | 5.4 | 0.0 / 2.3 / 0.7 | 0.7 | 5.9 | yes | 7,200 |
| SmolLM2 135M | 12.7 | 0.5 / 4.1 / 0.0 | 0.4 | 13.3 | yes | 7,200 |
| Granite Guardian 3.1 2B | 76.1 | 3.7 / 8.0 / 8.2 | 3.4 | 76.2 | yes | 5,616 |
| Qwen3.5-2B | 61.6 | 4.9 / 9.9 / 8.0 | 3.8 | 62.7 | yes | 6,984 |
| Qwen3Guard-0.6B | 29.9 | 1.0 / 4.3 / 0.0 | 0.9 | 29.3 | yes | 7,200 |
| Phi-4-mini | 89.9 | 10.6 / 30.6 / 0.0 | 4.0 | 90.2 | yes | 7,200 |
| Qwen3Guard-8B | 167.9 | 33.4 / 28.8 / 33.1 | 8.3 | 171.0 | yes | 4,472 |
| Granite Guardian 3.3 8B¹ | 528.2 | 30.6 / 27.1 / 30.7 | 9.4 | 496.7 | no | 1,560 |
| Qwen3.5-4B | 146.7 | 17.2 / 41.5 / 0.0 | 8.4 | 148.1 | yes | 5,808 |

¹ The accepted Granite-8B fit used 5% verdict smoothing with its own 5.39 GB Ollama model resident. Its earlier hard-target fit, with the isolated service idle, ran at 226.8 tok/s and returned both scores on 24/32 rows. The two runs changed both the loss and the serving state.

² At 300 processed tokens per row, round one includes 7,200 fitting rows, 800 train-only early-stop rows, setup, full export/registration and two sequential 1,000-row scores. The 8k-backward column gives the hypothetical optimizer time for all 8,000 rows. Score time scales the mean latency of 32 fixture calls to 2,000. Row lengths, padding and cache reuse can change these projections. Cold source transfers, native baselines and the one-time five-length verification are separate.

³ Projected whole-scenario optimizer rows at 20, 90 and 180 minutes for spark, flash and maxx. Reserve export and scoring time before setting the trainer’s `--seconds`. The projection applies the trainer’s 65% selection margin and caps its short pilot at measured sustained throughput with `--max-planning-rate`. The 800 early-stop rows are additional. Round-two counts include any repeated rows, so the number of distinct rows can be smaller.

## Round two

Allow the indicated minutes for each independent held-scenario fold and for the final warm start. Use the same `--folds` for the final fit. Short-budget models use two folds so each group gets one genuinely held-out error prediction. These are budget allocations. Inference uses 80% of the train-only forward pilot rate. Export and the two scores use the remainder of the tier box.

| Model | Folds | Min per fold | Final fit min | Rows per fold fit³ | Final fit rows³ |
| --- | --- | --- | --- | --- | --- |
| Mezzo Small | 5 | 1.9 | 9.6 | 576 | 7,200 |
| Ettin 68M | 5 | 1.9 | 9.6 | 1,288 | 7,200 |
| SmolLM2 135M | 2 | 7.8 | 3.7 | 480 | 968 |
| Granite Guardian 3.1 2B | 2 | 30.5 | 25.1 | 728 | 1,456 |
| Qwen3.5-2B | 2 | 21.4 | 42.8 | 536 | 3,368 |
| Qwen3Guard-0.6B | 5 | 8.9 | 44.4 | 992 | 7,200 |
| Phi-4-mini | 5 | 17.5 | 87.6 | 304 | 4,800 |
| Qwen3Guard-8B | 2 | 66.0 | 37.9 | 392 | 784 |
| Granite Guardian 3.3 8B¹ | 2 | 66.6 | 35.7 | 120 | 248 |
| Qwen3.5-4B | 2 | 42.6 | 85.2 | 304 | 2,784 |

For chat models, Δ is the maximum absolute change in the unsafe-minus-safe logit margin on the five matched prompt-ID sequences. Encoder values are maximum absolute per-logit differences from PyTorch. The serving counts are first-attempt valid probabilities. The synthetic TSV SHA-256 was `1638d9b98b51dbe6defe7c0cb0f80a0ffd021c2865e8ef3d7041d3a4b9aab577`.

## Model decisions and transfers

Use Phi-4-mini, Qwen3Guard-8B and Qwen3.5-4B for maxx. The 4B reserve sustained 272.7 tok/s with the service idle and 231.6 tok/s with its own GGUF resident. It used the same rank, batch size, optimizer and fixture in both runs. The resident run reached a 27.17 GB process footprint. Ollama reported 4.68 GB of GPU allocations at all 61 samples. This gives the reserve an advantage for a three-hour budget on a shared Mac. The Qwen3Guard-8B measurement used the running service with fixture weights unloaded.

Granite-8B remains technically deployable with 5% verdict smoothing. Its first hard-target model lost the safe alternative on eight rows. Its smoothed model returned both alternatives on all 32. With 5.39 GB resident throughout 155 samples, it trained at 75.7 tok/s despite a 223.9 tok/s pilot. Use the sustained cap for the corresponding serving state. A fixture pass establishes serving compatibility. Validation on completed conversations will decide the winners.

Qwen3Guard-0.6B F16 occupies 1,198,178,176 bytes. The upstream checkpoint stores two byte-identical 311,164,928-byte embedding/output tensors. The tied export stores them once. The flash reserve was unnecessary.

Ettin's INT8 browser graph differed from PyTorch by 0.378 on a fixture logit, above the existing 0.35 tolerance. Its FP16 graph passed at 0.0055 and the complete browser package was 140,994,583 bytes. Use `export_encoder.py --dtype fp16` for Ettin. Mezzo passed with per-channel INT8.

Cold downloads added 14.2 minutes for Phi, 33.5 for Qwen3Guard-8B and 31.3 for Granite-8B on this connection. Stage each maxx candidate independently. Capture the HF reference before releasing its upstream source. Release or re-fetch the 4B source around 8B merges. The 8B runs approached 49 GB across the entire task tree. The simultaneous-residency measurements cover an idle loaded Ollama model during backward passes. Concurrent generation was outside this probe.

With Qwen3.5-4B resident, 8,000 backward rows project to 172.7 minutes, or 182.6 with setup, export and scoring. The normal 7,200/800 split projects to 172.7 minutes. Allow about 4,896 fitting rows under the conservative selection margin.

## Repeating a chat probe

Create the original synthetic TSV at a fresh path with `python3 scripts/klara/make_tuning_fixture.py "$fixture"`. The shape names supply arbitrary class markers. Use this file for fitting, reference capture and the fixture benchmark. The preflight used 32 synthetic scenarios with four rows each, 96 train rows and 32 validation rows. Every dialogue has one to five student/tutor pairs. Each fitting pass used 88 examples after the grouped early-stop holdout. Chat fits used BF16, rank 8, learning rate 0.0002 and batch two except the two 8B fits, which used batch one. SmolLM2 ran three epochs, Granite-2B and Qwen3Guard-0.6B two, and the other chat fits one. The two encoders ran one epoch at batch four.

```sh
"$p" "$k/train_chat.py" --source "$source" --out "$run" --data "$fixture" --tier "$tier" \
  --batch "$batch" --rank 8 --lr 0.0002 --epochs "$epochs" --seconds 1200
"$p" "$k/export_chat.py" --run "$run" --tier "$tier" --name "$slug" --round fixture --quant "$quant" --merge-only
"$p" "$k/verify_chat.py" --run "$run" --tag "$tag" --data "$fixture" --save-reference "$run/hf-reference.json"
"$p" "$k/export_chat.py" --run "$run" --tier "$tier" --name "$slug" --round fixture --quant "$quant" --consume-merged
"$p" "$k/verify_chat.py" --run "$run" --tag "$tag" --data "$fixture" --reference "$run/hf-reference.json"
"$p" "$k/benchmark.py" --backend ollama --model "$tag" --tier "$tier" --safe-token ' safe' --unsafe-token ' unsafe' \
  --endpoint http://127.0.0.1:18282 --data "$fixture" --split validation --output "$results"
```

Here `tag=klara/cand-$tier-$slug-fixture`. Use `--verdict-smoothing 0.05` for the accepted Granite-8B recipe. The GGUFs used Q8_0 for SmolLM2, Phi and Qwen3.5-4B, Q5_K_M for Granite-2B, Q6_K for Qwen3.5-2B, F16 for Qwen3Guard-0.6B, Q4_K_S for Qwen3Guard-8B, and Q4_K_M for Granite-8B. Each served word included a leading space. The tokenizer and its safe/unsafe IDs are part of each run’s recipe.
