# Klara pipeline

Run from the repository root with Python 3.10+ on macOS or Linux. All commands use the standard library. Scratch inputs and results default to `~/klara-tiers`. Each command accepts `--help`.

## Build and check the dataset

```sh
k=scripts/klara
work=~/klara-tiers
python3 "$k/build_manifest.py" --seeds "$work/seeds/seeds.jsonl" --rules rules-klara.tsv
python3 "$k/check_shard.py" "$work/shards/shard-01.written.jsonl"
python3 "$k/assemble.py" --shards "$work/shards" --output data-klara.tsv
python3 "$k/overlap.py" --data data-klara.tsv --output "$work/results/overlap.md"
```

Seed 20261117 fixes allocation. Every shard contains 40 train, five validation and five test scenarios. Each risk seed supplies two unsafe rows for its rule and two linked safe look-alikes. Set rule proportions in the seeds. The manifest prints achieved and weighted target counts. Exactly 10% of unsafe slots are borderline. Safe slots use an empty rule/action, trigger `none` and trigger turn 0.

Give each writer `shard-NN.slots.jsonl`. Return one JSON object per line with the original `row_id` and alternating student/tutor `messages` with string `role` and `content`. Echoed slot fields must match. Messages must contain 1–4,000 characters, include non-whitespace text and exclude tabs and line breaks. The opener limit is four occurrences per shard or 25 across available shards, matching on the first eight words (or the entire shorter opener).

Duplicate checks use NFKC, case folding and collapsed whitespace per message. Character five-gram set Jaccard ≥ 0.85 rejects a pair within or across shards. Partial peer files participate. Assembly repeats all checks and verifies quotas before publishing the TSV atomically. Complete the plan's human content pass before committing real rows.

## Score conversations and compare tiers

```sh
python3 "$k/score.py" --tier flash --input conversation.json
python3 "$k/benchmark.py" --tier flash --backend ollama --model klara/flash \
  --split validation --stage round-2 --output "$work/results/flash-val.tsv"
python3 "$k/pick_threshold.py" "$work/results/flash-val.tsv"
python3 "$k/summarise.py" "$work/results" --output "$work/results/tiers.md"
```

`score.py` reads a messages array or an object containing it from a file or stdin. Its JSON contract is `{"unsafe_probability": 0.07, "label": "safe"}`. The label is unsafe at or above `--threshold` (default 0.5). Apply the validation-selected cutoff to deployment and the single final test run. The fixed `train-sample` draws 900 safe and 100 unsafe training rows without replacement. Only conversation messages reach the model.

- **Ollama** serves `klara/flash` and `klara/maxx` at localhost:11434. The system prompt defines unsafe for both speakers and ends with “Reply with exactly one word: safe or unsafe.” The first generated token and its top 20 alternatives must contain both verdict scores. Default matching requires a unique complete token per verdict after trimming and case folding. For split words or ambiguous variants, set exact, distinct `--safe-token` and `--unsafe-token` strings, preserving spaces. The complete generated verdict must agree with its first token. The TSV records both tokens and log-probabilities used in the two-way softmax. [Ollama API types](https://github.com/ollama/ollama/blob/main/api/types.go)
- **TEI** serves spark at localhost:8080. Set `--model` to the deployed `/info` model ID. Label defaults are `safe` and `unsafe`. For an indexed head, supply its actual mapping, for example `--safe-label LABEL_0 --unsafe-label LABEL_1`. The adapter posts the serialized messages to `/predict` with truncation disabled and takes the softmax of two raw logits. Train the head with the same JSON serialization. [TEI prediction schema](https://github.com/huggingface/text-embeddings-inference/blob/main/router/src/http/types.rs)
- **OpenRouter** serves `typesafe/jev-1.14` at the fixed HTTPS endpoint. Supply the key file path with `--key-file` or `KLARA_OPENROUTER_KEY_FILE`. Use `--prompt-file` and `--stage prompt-v1` for a prompt variant. The adapter validates the JSON probability and label at 0.5 before applying the operating cutoff. The TSV records the prompt hash and reported cost. The plan's price probe precedes paid batches.

## Read the results

Use `--tier`, `--stage`, `--size-bytes` and `--licence` to identify each artifact. Each run makes one prediction request per row with a 120-second deadline. Chat temperature is zero. The TSV is flushed per row to an exclusive `.partial` file and published on completion. An interrupted run retains its partial evidence. Keep completed result TSVs together for `summarise.py`.

Every error counts against accuracy. A failed unsafe row counts as missed. FPR counts safe rows actually flagged divided by all safe rows. Precision uses valid flags. AUROC uses valid scores, with half credit for ties. Binomial rates use Wilson 95% intervals. AUROC uses a DeLong normal interval when both classes have at least two valid scores. Latency includes errors. Empty denominators display as a dash. Threshold selection maximizes validation accuracy, then minimizes false positives, then prefers a cutoff closest to 0.5 among the evaluated cutoffs. The summary recomputes each run, the always-safe reference, validation leaders and final test breakdowns from the per-row TSVs.

See [local tuning and export](TUNING.md) for native baselines, OOF resampling, post-export calibration and the TEI, Transformers.js and Ollama parity probes.
