# Fit and verify local Klara candidates

The [fixture preflight](PREFLIGHT.md) gives the measured serving checks, disk peaks and round budgets for each candidate. Use the MPS environment for fitting and export. The dataset and benchmark commands in the [pipeline README](README.md) work with the standard library. Native HF baselines and calibration use the tuning environment.

```sh
w=~/klara-tiers
m="$w/models"
k=scripts/klara
p="$w/env/venv/bin/python"
export NODE_PATH="$w/env/node/node_modules"
export OLLAMA_HOST=127.0.0.1:18282 OLLAMA_MODELS="$m/ollama" OLLAMA_NO_CLOUD=1
```

The prepared Mac has Python 3.12.16, MPS PyTorch, PEFT, TEI, Node and the converter. To reproduce the environment, use the pins in [requirements-tuning.txt](requirements-tuning.txt).

```sh
uv venv --python 3.12.16 "$w/env/venv"
uv pip install --python "$p" -r "$k/requirements-tuning.txt"
brew install text-embeddings-inference llama.cpp
git clone --depth 1 --branch v0.9.0 https://github.com/ggml-org/llama.cpp "$w/env/tools/llama.cpp"
npm install --save-exact --prefix "$w/env/node" @huggingface/transformers@4.3.2
```

The four downloaded HF sources are under `$m/source/{mezzo,ettin,smollm,granite}`. Each directory has a `source.json` with its upstream ID and revision. Training reads the local checkpoint. Give every fit a fresh output directory under `$m`. Run heavy commands serially, using the host gate when present. The following examples use a TSV in the section-two schema, passed as `$data`.

## Encoders

```sh
"$p" "$k/train_encoder.py" --source "$m/source/mezzo" --data "$data" --out "$m/mezzo-r1"
"$p" "$k/export_encoder.py" --hf "$m/mezzo-r1/hf" --out "$m/mezzo-r1/browser"
text-embeddings-router --model-id "$m/mezzo-r1/hf" --dtype float16 --hostname 127.0.0.1 --port 18281
# In another terminal with the same variables
"$p" "$k/parity.py" --hf "$m/mezzo-r1/hf" --data "$fixture" \
  --endpoint http://127.0.0.1:18281 --browser "$m/mezzo-r1/browser"
```

Full fitting uses both logits, weighted cross-entropy and train-only early stopping. The encoder export preserves mean pooling and the source rotary settings. TEI serves FP16. Transformers.js reads the dynamic per-channel INT8 ONNX and the same tokenizer. The parity probe compares raw logits for one transcript of each available turn count.

For the probe baseline, pass `--probe` to `train_encoder.py` and serve its fitted head with TEI. Only the output layer trains. For Mezzo’s native baseline, run the following on the same split as the probe.

```sh
"$p" "$k/benchmark.py" --backend hf-native --native mezzo --model "$m/source/mezzo" \
  --tier spark --stage native-max-sigmoid --data "$data" --split validation
```

## Chat models

Start `ollama serve` with the task-specific `OLLAMA_HOST` and `OLLAMA_MODELS` above. Use that endpoint for benchmarking, registration and verification.

```sh
"$p" "$k/train_chat.py" --tier flash --source "$m/source/granite" --data "$data" \
  --out "$m/granite-r1" --rank 8 --batch 2 --epochs 2 --lr 0.0002
"$p" "$k/export_chat.py" --run "$m/granite-r1" --tier flash --name granite --round r1 --quant Q5_K_M
"$p" "$k/verify_chat.py" --run "$m/granite-r1" --tag klara/cand-flash-granite-r1 --data "$fixture"
"$p" "$k/benchmark.py" --tier flash --model klara/cand-flash-granite-r1 \
  --endpoint http://127.0.0.1:18282 --safe-token ' safe' --unsafe-token ' unsafe' \
  --data "$data" --split validation --stage round-1
```

The trainer checks continuation token IDs at the exact verdict boundary. It fits LoRA on the full-vocabulary first-token loss, stores the two verdict spellings in `chat.json`, and saves an adapter. The exporter reloads the base, merges, embeds the training template in the GGUF, quantizes and checks decimal tier size. For a fit that pushes the losing verdict outside Ollama’s top 20, `--verdict-smoothing 0.05` assigns 95% of the training target to the observed verdict and 5% to the other. The denominator still spans the full vocabulary. The default is zero. Missing alternatives still count as scoring errors. A temporary task tag verifies import before the candidate name is registered. Existing candidate names are refused. `--register-only` retries registration of an exported GGUF.

For an 8B source, use `--merge-only`. Verify the staged checkpoint before releasing the task-owned upstream copy. Then run the same export with `--consume-merged`; this reads the staged checkpoint and releases it after GGUF conversion. Account for retained sources, environment, temporary files, winners and Ollama blobs against the 50 GB limit before starting. `--checkpointing` reduces training activation memory. Flash uses Q5_K_M for Granite, Q6_K for Qwen3.5-2B and F16 for Qwen3Guard-Gen-0.6B. The maxx choices are Q4_K_S for Qwen3Guard, Q4_K_M for Granite and Q8_0 for Phi. Q8 and F16 use direct conversion. The other quantizations use a temporary floating-point GGUF.

To verify a large merge across processes, capture the Hugging Face reference while its tokenizer and weights are still available. After export, the second invocation reads only the saved comparison, the recipe, the adapter files, and the GGUF. Keep any round-one adapter used for the warm start. The probe checks every GGUF prompt ID, the served prompt length, both verdict-token log probabilities, and an absolute tolerance of 1.5 on the unsafe-minus-safe logit margin.

```sh
"$p" "$k/verify_chat.py" --run "$run" --tag "$tag" --data "$fixture" --save-reference "$run/hf-reference.json"
# After --consume-merged has registered the candidate
"$p" "$k/verify_chat.py" --run "$run" --tag "$tag" --data "$fixture" --reference "$run/hf-reference.json"
```

For a general chat **baseline**, use `export_chat.py --baseline-source PATH --run FRESH_DIR --tier TIER --name SLUG --round baseline --quant TYPE` and benchmark the result. This preserves the source chat template and uses the fixed Klara scoring prompt. For an untouched native guard use `benchmark.py --backend hf-native --native granite|qwen-guard --model LOCAL_SOURCE`. Granite scores Yes/No under its custom risk definition on the transcript. Qwen uses its native policy at each speaker boundary with the native `Safety:` prefix. Unsafe and Controversial probability mass are combined, and the highest turn score is the conversation score. A malformed verdict is an error.

## Two rounds and calibration

Each trainer reserves a scenario-grouped slice of train for early stopping. Its timed backward pilot estimates how many whole, deterministically ordered scenarios fit. A separate train-only forward pilot sets aside time for early stopping and held-fold predictions at 80% of its measured throughput. The budget includes model setup, optimization and early-stop checks. If a short backward pilot exceeds measured sustained throughput, set `--max-planning-rate` to the sustained tokens/s for that hardware and serving state. The report records the raw pilot and the rate used to select scenarios. One in-flight operation can finish beyond a deadline. Export and benchmark time are separate. `training.json` reports selected scenario IDs, examples, tokens, passes, actual optimization seconds and throughput. On macOS, use `/usr/bin/time -l` to capture the training process’s peak memory footprint in bytes. The trainer also records peak RSS and samples Metal driver allocations after backward passes. These measurements overlap. Staged chat exports write merge, conversion, quantization and registration seconds beside the recipe. Direct F16 and Q8 conversion records zero for the separate quantizer. Set `--seconds`, `--epochs`, `--lr`, `--batch` and `--positive-weight` as needed.

1. Fit round one and benchmark the exported candidate on train-sample and validation.
2. To identify resampling errors, independently fit `--fold 0 --folds 5` through `--fold 4 --folds 5` from the same upstream source in five fresh directories. Each emits predictions only for its excluded training scenarios. The default fold time is one tenth of the tier box. All five fits together receive half a round.
3. Fit round two with `--oof fold0/oof.json ... fold4/oof.json` and `--extra-copies N`. The trainer verifies the training data, source, fold membership, disjointness and complete coverage. It repeats missed training rows within its fitting partition. Warm-start with `--init-checkpoint R1/hf` for encoders or `--init-adapter R1/adapter` for chat. The final OOF-informed fit receives the other half of the box by default. Encoder `--precision fp16` uses FP16 autocast with FP32 optimizer weights. Chat LoRA uses BF16 base weights; measure the merged GGUF after quantization.
4. Fit calibration and the cutoff on the exact deployed candidate’s saved validation scores. Optional calibrated-row output permits comparison without rerunning inference.

```sh
"$p" "$k/calibrate.py" "$validation_tsv" --output "$run/calibration.json" \
  --calibrated-tsv "$results/round2-calibrated.tsv"
```

Pass `--calibration "$run/calibration.json"` to both `score.py` and `benchmark.py`. It binds the monotone log-odds fit and cutoff to the model and scoring recipe. Keep candidate tags immutable. Only the selected artifact and operating point go to test, once. PR-AUC uses non-interpolated average precision with tied probabilities grouped; Brier is the mean squared probability error. Both use valid probabilities. Every missing prediction still counts wrong for accuracy.

Run the dependency-free checks with `python3 -m unittest discover -s scripts/klara -p test_tuning.py`. The live parity commands above require the corresponding exported weights and services. Use synthetic fixtures when preparing a deployment before the dataset is released.

The [Spark experiment](../../results/klara/spark/README.md) records the train-sample and validation results, frozen source revisions, replay arguments and browser parity measurements. For native Mezzo on TEI, `--backend tei --native mezzo` applies the producer's maximum sigmoid to the five FP16 logits. The two-label fine-tunes use the default binary softmax.

### Reproduce the final Spark and Flash runs

The real-data experiment pins both the full source bytes and a train/validation projection. The source SHA-256 is `0ff32b946a2e83760e90ce0974c73cedff23a6b8cbd9bd766cef155744caf294`. The projector hashes the complete stream and selects on the split prefix before decoding conversation text. Each fit, fold and split benchmark checks the full source and the projection. Each tier writes both digests to its local results directory.

Use a new lowercase run name to retain earlier artifacts. The following commands assume the Mac environment and sources prepared above.

```sh
w="$HOME/klara-tiers"
p="$w/env/venv/bin/python"
k=scripts/klara
export KLARA_SPARK_RUN=replay-02
"$p" "$k/tier_data.py" prepare "$w/logs/spark/$KLARA_SPARK_RUN"
```

For Spark, replay the ordered `spark_experiment_arguments` from the final tier's `fit-recipes.json`, passing each list to `spark_experiment.py`. Run heavy commands serially through the host gate when it exists. Finish with `tier_rounds.py finish-spark` to recount the two splits and compare all three Node exports. The original table appears in the task's `results/spark/tables.md` while Flash runs. Later named replays write the local table to the run's own subdirectory.

For Flash, `KLARA_FLASH_RUN=replay-02 "$p" "$k/tier_rounds.py" run-flash` prepares a fresh projection, runs all three candidates, verifies tuned GGUFs and writes both operating points. The report commands write compact results to the checkout's `results/klara/<tier>` directory. Use a checkout intended for the new results. Neither tier evaluates test.

The native Flash guards use their own tokenizer templates with Ollama raw generation. Granite uses its standard harm definition and Yes/No. Qwen3Guard uses the probability mass of Unsafe and Controversial at its native verdict position. Each guard evaluates each consecutive speaker prefix once and takes the maximum risk over the conversation. A missing verdict alternative or incomplete word makes the entire row malformed. Tuned models use the fixed Klara prompt.

Round two starts from round one, with train-only out-of-fold error weights. The K-quant models use the prior deployed GGUF for the frozen text projections and embedding. The last four full-attention V projections learn residual LoRAs under their deployed per-sub-block code ranges, scales and offsets. The final GGUF export recomputes block scales on the merged weights. This is fixed-grid quantization-aware training with floating-point accumulation. The F16 guard uses FP16 base weights and float optimizer state. The five-length service check compares the actual deployed export with the merged model.

## Maxx on the final Klara data

Run `$HOME/klara-tiers/env/venv/bin/python scripts/klara/maxx_rounds.py` from the PR checkout. The driver uses the pinned preflight source revisions, the task-only Ollama store, the machine's heavy-job lock where available, and the SHA-256-verified train/validation projection. It resumes completed passes from the command log. A partially written score file preserves first attempts. The two 1,000-row splits use the same IDs across candidates.

Phi-4-mini and Qwen3.5-4B use Q8_0. Qwen3Guard-8B uses Q4_K_S. Its native baseline evaluates each speaker under the upstream policy. The general chat baseline asks for lowercase `safe` or `unsafe` at the start of an assistant turn. The fitted template uses `Assistant:` followed by a space and the verdict. An absent alternative or a generated token outside the configured pair counts as malformed.

Round one fits class-weighted LoRA with 5% verdict smoothing. Round two warm-starts from its adapter, uses independent held-scenario training folds to identify resampling targets, and fits a rank-12 residual on the last four V projections (fused QKV on Phi). The forward pass uses decoded frozen GGUF matrices and snaps the effective trainable matrices to their round-one quantization grids. Model selection, calibration and cutoff fitting use validation. The local `results/maxx/tables.md` updates after each completed candidate.

The 50 GB allocation includes retained Spark and Flash winners. Each Maxx round-two GGUF and private tag is retained, along with both LoRA adapters, calibration and recipes. Baseline and round-one export receipts record their checked digest and size before reclaiming those intermediates. Source shards can be restored with `maxx_source.py MODEL`. Each training receipt records the exact examples, token count and rows used. Pass time includes fold fitting in round two. Pinned source transfers are separate.
