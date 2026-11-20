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

### Cloud Decisions

The cloud tier sends `model`, `state` and `questions` to `POST /api/alpha/decisions` for `typesafe/jev-1.14`. The endpoint supplies probabilities directly and has no temperature control. Supply the **path** to the credential file using `--key-file` or the `KLARA_OPENROUTER_KEY_FILE` environment variable. [Decisions guide](https://openrouter.ai/docs/guides/features/decisions) · [Request and answer schema](https://openrouter.ai/docs/api/api-reference/alphadecisions/submit-a-decisions-request)

After assembling `data-klara.tsv`, run these commands from the repository root with the credential file path set. The first draws a reproducible 20-row validation sample. The second scores the whole validation split.

```sh
python3 scripts/klara/benchmark.py --tier cloud --split validation --stage prompt-v0 \
  --limit 20 --max-cost 5 --output "$HOME/klara-tiers/results/probes/cloud-v0-20.tsv"
python3 scripts/klara/benchmark.py --tier cloud --split validation --stage prompt-v0 \
  --max-cost 5 --output "$HOME/klara-tiers/results/cloud-v0-validation.tsv"
```

The default spec is [cloud-v0.json](prompts/cloud-v0.json). Pass `--prompt-file path/to/cloud-v1.json --stage prompt-v1` for another round. The spec accepts the following fields.

- `transcript` selects `"lines"` (one `student: …` or `tutor: …` per message) or `"json"` (the compact messages array). Optional `state_prefix` precedes the transcript with a blank line.
- `questions` maps each name to a Decisions question with `type`, `instructions` and type-specific `criteria`. A `noul` returns the probability of yes. A `choice` uses a map of choices to descriptions. Auxiliary `score` (ordered criteria) and `box` questions can be recorded alongside them.
- `unsafe_probability` selects the output. Use `{"from":"risk"}` for a noul or `{"from":"verdict","choice":"unsafe"}` for the specified choice's probability. For several nouls, `{"max":["rule_a","rule_b"]}` uses the largest probability and `{"noisy_or":["rule_a","rule_b"]}` computes `1 - (1 - p_a) × (1 - p_b)`.

The TSV includes the raw answers object, SHA-256 of the exact spec file bytes, reported USD cost and operating cutoff. Every requested question must have a valid answer. A failed request or malformed response counts as wrong after one attempt. The budget uses reported cost, including billed malformed answers. Before each request the scorer stops if that run has already reached `--max-cost` (default USD 5). A request can cross the limit, and a timeout can leave its cost unknown. On a budget stop, the attempted rows remain in the output's `.tsv.partial` file.

#### 50-row repeat check

Use the same assembled validation file, prompt and cutoff for both passes. Each run uses the same fixed sample. Keep probes in their own directory so they stay out of the full-split summary.

```sh
for run in 1 2; do
  python3 scripts/klara/benchmark.py --tier cloud --split validation --stage prompt-v0 \
    --limit 50 --max-cost 5 --output "$HOME/klara-tiers/results/probes/cloud-v0-repeat-$run.tsv" || exit 1
done
python3 - <<'PYTHON'
import csv
from pathlib import Path

folder = Path.home() / "klara-tiers/results/probes"
def load(run):
    with (folder / f"cloud-v0-repeat-{run}.tsv").open(encoding="utf-8", newline="") as f:
        return {r["row_id"]: r for r in csv.DictReader(f, delimiter="\t")}

a, b = load(1), load(2)
assert a.keys() == b.keys() and len(a) == 50
assert all(a[i][k] == b[i][k] for i in a for k in ("model", "prompt_sha256", "threshold"))
valid = [i for i in a if not (a[i]["error"] or b[i]["error"])]
deltas = [abs(float(a[i]["raw_probability"]) - float(b[i]["raw_probability"])) for i in valid]
print("Paired valid rows", len(valid), "of 50")
print("Exact probability matches", deltas.count(0), "of", len(valid))
print("Label matches", sum(a[i]["label"] == b[i]["label"] for i in valid), "of", len(valid))
print("Largest absolute probability difference", max(deltas, default=None))
PYTHON
```

Report both match counts and the number of valid pairs so the paper describes repeatability on the measured sample.

## Read the results

Use `--tier`, `--stage`, `--size-bytes` and `--licence` to identify each artifact. Each run makes one prediction request per row with a 120-second deadline. Ollama uses temperature zero. The TSV is flushed per row to an exclusive `.partial` file and published on completion. An interrupted run retains its partial evidence. Keep completed result TSVs together for `summarise.py`.

Every error counts against accuracy. A failed unsafe row counts as missed. FPR counts safe rows actually flagged divided by all safe rows. Precision uses valid flags. AUROC uses valid scores, with half credit for ties. Binomial rates use Wilson 95% intervals. AUROC uses a DeLong normal interval when both classes have at least two valid scores. Latency includes errors. Empty denominators display as a dash. Threshold selection maximizes validation accuracy, then minimizes false positives, then prefers a cutoff closest to 0.5 among the evaluated cutoffs. The summary recomputes each run, the always-safe reference, validation leaders and final test breakdowns from the per-row TSVs.

See [local tuning and export](TUNING.md) for native baselines, OOF resampling, post-export calibration and the TEI, Transformers.js and Ollama parity probes.

Alex selected two Maxx candidates on 19 November 2026, Phi-4-mini and Qwen3Guard-8B. Qwen3.5-4B was dropped before benchmarking. It had replaced Granite Guardian 3.3 8B after Granite measured 76 backward tokens/s in preflight.
