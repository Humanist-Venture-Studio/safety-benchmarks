# Safety Benchmarks

The goal of this repo is to evaluate and fine-tune a lightweight safety guardrail model—specifically [`sileader/qwen3guard:0.6b`](https://ollama.com/sileader/qwen3guard:0.6b)—against our safety benchmark dataset (`data.tsv`).

Instead of relying on a massive model for basic safety classification, I want to take this small 0.6B parameter base model, see how it performs out of the box on our prompts and simulated responses, and fine-tune it to reliably flag unsafe content.

## Getting Started

To run the base model locally, you'll need [Ollama](https://ollama.com/) installed on your machine.

### 1. Download and Install Ollama

Grab the installer for your OS directly from the official site:

- **Download page:** [https://ollama.com/download](https://ollama.com/download)

Or install it from the terminal:

```bash
# macOS (via Homebrew)
brew install --cask ollama

# Linux
curl -fsSL https://ollama.com/install.sh | sh
```

Once installed, make sure the Ollama app or service is running (`ollama serve`).

### 2. Install the Base Model

Pull the [`sileader/qwen3guard:0.6b`](https://ollama.com/sileader/qwen3guard:0.6b) model using the Ollama CLI:

```bash
ollama pull sileader/qwen3guard:0.6b
```

To test it interactively in your terminal, run:

```bash
ollama run sileader/qwen3guard:0.6b
```

## Tune Qwen3Guard on data.tsv

The [tune-qwen-guard skill](.agents/skills/tune-qwen-guard/SKILL.md) fits a local Humanist candidate to the safety of the **assistant’s reply in context**. It changes three rows of the model’s output weights, one for the first token of each verdict. It exports a GGUF with the same tokenizer, quantization and prompt template as Sileader.

From this checkout in Codex, ask “Use `$tune-qwen-guard` to tune Qwen on `data.tsv` and compare the candidate with Sileader on held-out requests.” To run the same workflow yourself, use the following commands from the repository root in one Bash or Zsh session.

### Fit a candidate

Use macOS or Linux with Python 3.12, the local Ollama service on port 11434, and a recent `llama-server` from [llama.cpp](https://github.com/ggml-org/llama.cpp/tree/master/tools/server). The trainer checks `PATH` and the macOS Ollama app bundle for the server. You can also pass `--llama-server /path/to/llama-server`. Allow about 500 MB for the candidate GGUF in addition to the base model and Python environment.

```bash
export OLLAMA_HOST=127.0.0.1:11434
base=sileader/qwen3guard:0.6b
candidate="humanist/qwen3guard:tune-$(date -u +%Y%m%d-%H%M%S)"
skill=.agents/skills/tune-qwen-guard
run=$(mktemp -d)
py="$run/venv/bin/python"

ollama pull "$base"
python3.12 -m venv "$run/venv"
"$py" -m pip install "gguf==0.19.0" numpy scipy
"$py" -B "$skill/scripts/tune.py" --data data.tsv --out-dir "$run/candidate"
ollama create "$candidate" -f "$run/candidate/Modelfile"
```

The trainer reads the local base model from Ollama, checks that the training prompt tokenizes exactly as it does during generation, and writes the new weights to `$run/candidate/candidate.gguf`. Choose a persistent run directory in place of `mktemp -d` if you want to keep the GGUF and result files there.

### Measure the change

The current dataset splits into **2,822 training, 462 validation and 624 test rows**. Replies to the same request stay together, including groups connected by a repeated prompt or reply. The trainer uses validation to select the strength of the weight update. Check how both models actually respond in Ollama before evaluating your chosen candidate on the test split.

```bash
compare() {
  for model in "$base" "$candidate"; do
    "$py" "$skill/scripts/benchmark.py" --data data.tsv --model "$model" \
      --split "$1" --output "$run/${model%%/*}-$1.tsv" || return 1
  done
}
compare validation
```

Once you have selected a candidate on validation, measure its held-out accuracy.

```bash
compare test
```

Each results TSV contains the input rows, split, first-attempt classification and correctness. `Safe` matches `is_safe=1`. Both `Unsafe` and `Controversial` match `is_safe=0`. The evaluator gives each reply one 120-second attempt and counts timeouts, failed generations and unrecognized verdicts as errors. Compare missed unsafe replies (`false_safe`) and safe replies flagged (`false_flag`) alongside accuracy. Use `compare all` for a separate score that includes the development rows.

In the earlier Humanist experiment, tuning 45 tensors raised held-out accuracy from **504/624 (80.77%)** to **608/624 (97.44%)**. That experiment also tuned transformer layers. Use the TSVs from your run for the verdict-layer recipe above.

## Tune Qwen3Guard on data-multi.tsv

`humanist/qwen3guard:0.6-fable` is the same verdict-layer recipe fitted to **whole four-turn conversations**. The target is `consensus_rating`, mapped onto the model's own three verdicts: `SAFE` to Safe, `FLAGGED` to Controversial and `UNSAFE` to Unsafe. `data-multi-split.tsv` fixes a simple random split of the 10,000 conversations (seed 20261110): 6,500 train, 1,000 validation and 2,500 test.

Use the environment from the walkthrough above (`$py`, `$skill`, `$run`).

```bash
"$py" -B "$skill/scripts/tune_multi.py" --out-dir "$run/fable" --name qwen3guard-0.6-fable
ollama create humanist/qwen3guard:0.6-fable -f "$run/fable/Modelfile"

for model in sileader/qwen3guard:0.6b humanist/qwen3guard:0.6-fable; do
  "$py" -B "$skill/scripts/benchmark_multi.py" --model "$model" --split test \
    --output "$run/${model%%/*}-multi-test.tsv"
done
"$py" -B "$skill/scripts/overlap_multi.py" --output "$run/overlap-test.tsv"
```

`tune_multi.py` encodes the 7,500 training and validation conversations once (about 15 minutes on an M4 Max; pass `--features file.npz` to keep the encodings), fits the three output rows, and picks the regularization on validation. It prefers a fit that leaves every other token of the reply unchanged, so category names stay intact. `benchmark_multi.py` sends each conversation once through Ollama's API with temperature 0 and counts timeouts, API errors and replies that do not open with a verdict as wrong. Use `--sampling default` to score a tag with its own sampling. `overlap_multi.py` reports how close each test conversation is to its nearest training conversation.

On the 2,500 test conversations the tuned model matches `consensus_rating` on **2,336 (93.44%)** and Sileader on **1,576 (63.04%)**. It calls 12 of the 589 `UNSAFE` conversations Safe; Sileader calls 197 Safe. On all 10,000 conversations Sileader matches on 6,241 (62.41%).

Read the held-out score with two limits. The conversations are assembled from reused messages: 87.2% of the test messages also appear word for word in the training rows. And the gain does not carry over to `data.tsv`, where the tuned model is right on 2,763 of 3,908 single-turn rows and Sileader on 3,304. [reports/qwen3guard-fable-tune.md](reports/qwen3guard-fable-tune.md) has the method, the confusion tables and what the numbers do not show.

## One model for chats of any length (v2)

`humanist/qwen3guard:0.6-fable-v2` is one model for one-turn and four-turn chats. It was fitted on `data.tsv` and `data-multi.tsv` together, with every conversation rendered the same way: one instruction, then alternating `Student:` and `Assistant:` lines. Its test rows come from **whole story templates** that the fit never saw, and its Modelfile sets `PARAMETER temperature 0`: through plain `ollama run`, 300 probe rows got the same verdict three times out of three.

Use the environment from the first walkthrough (`$py`, `$skill`, `$run`).

```bash
"$py" -B "$skill/scripts/tune_chat.py" --out-dir "$run/fable-v2" --name qwen3guard-0.6-fable-v2 \
  --features "$run/features.npz"
ollama create humanist/qwen3guard:0.6-fable-v2 -f "$run/fable-v2/Modelfile"

for model in sileader/qwen3guard:0.6b humanist/qwen3guard:0.6-fable-v2; do
  for source in multi single; do
    "$py" -B "$skill/scripts/benchmark_chat.py" --source "$source" --model "$model" --split test \
      --output "$run/${model##*:}-$source-test.tsv"
  done
done
"$py" -B "$skill/scripts/benchmark_chat.py" --source multi --model humanist/qwen3guard:0.6-fable-v2 \
  --split validation --limit 200 --runner cli --repeats 3 --output "$run/repeats.tsv"
"$py" -B "$skill/scripts/overlap_multi.py" --split-file data-multi-template-split.tsv \
  --output "$run/overlap-template-test.tsv"
```

- **Split.** `data-multi-template-split.tsv` holds out whole templates: no safe arc and no unsafe module of the generator appears on both sides of train, validation and test. That leaves 5,849 train, 1,000 validation and 2,503 test rows; 648 rows whose arc and module fall on different sides are `excluded` and used for nothing. `python3 "$skill/scripts/split_templates.py" --data data-multi.tsv --scripts scripts --output new-split.tsv` rebuilds it byte for byte. `data.tsv` keeps the grouped split of `benchmark.py`.
- **Fit.** `tune_chat.py` refits the same three output rows as before. Multi-turn rows keep the three-way `consensus_rating` target; a single-turn row is Safe or not Safe. Each source's loss is averaged over its own rows, and the share given to single-turn rows is chosen on validation with the regularization. It prefers a fit that changes no other token of the reply.
- **Scoring.** `benchmark_chat.py` sends each row once with temperature 0 (`--runner api-greedy`, the default, so tags without a temperature are scored the same way). `--runner cli --repeats 3` uses plain `ollama run` and reports how many rows got the same verdict three times.

Scores at temperature 0, one attempt per row, the same prompt for every tag. v1 is `humanist/qwen3guard:0.6-fable`; it was fitted on most of these multi-turn test rows, so its figure there is not a held-out score.

| | Sileader | v1 | v2 |
|---|---:|---:|---:|
| Held-out multi-turn templates, exact three-way match (2,503 rows) | 1,607 (64.20%) | 2,365 (94.49%), seen in training | 1,906 (76.15%) |
| Same rows, `UNSAFE` called Safe (of 421) | 109 | 10 | 33 |
| Same rows, `SAFE` flagged (of 1,570) | 214 | 25 | 297 |
| Single-turn test rows, correct (624 rows) | 535 (85.74%) | 392 (62.82%) | 590 (94.55%) |
| Same rows, safe replies flagged (of 312) | 31 | 119 | 19 |

Read these with three limits. The held-out score is 17 points below v1's 93.44% from the random split, because no test conversation now has a near-duplicate in training (63.5% did). v2 misses far fewer unsafe conversations than Sileader but flags more safe ones on unseen four-turn story lines. And the held-out templates still come from the same generator and topics. [reports/qwen3guard-fable-v2.md](reports/qwen3guard-fable-v2.md) has the split audit, the confusion tables, the two other candidates that were tried and what the numbers do not show.

## Repository Contents

- `data.tsv` — Benchmark dataset containing prompts (`request`), paired safe and unsafe replies (`simulated_response`), categories, languages, and binary safety labels (`is_safe`).
- `data-multi.tsv` — 10,000 hyper-realistic four-turn student ↔ AI conversations for the same 62 categories: 7,500 safe / 2,500 unsafe (25%). Roughly half the unsafe rows are triggered by the student and half by the assistant (`trigger_source`). Unsafe coverage spans illegal acts (piracy, shoplifting, hacking, vandalism), sexually explicit content and boundary violations, substances, violence, self-harm signals, privacy, scams, and hate speech. Every row (including the original 2,000) goes through a deterministic realism pass (chat abbreviations, occasional typos, exclamation moderation), and rows are deduplicated across the whole file. See `reports/data-multi-qa.md` for composition, coverage stats, and the dataset's self-graded quality assessment (**A-**). Columns N–U hold four independent blind relabellings: `fable_*` by Product Fox (claude-fable-5-2), `gemini_*` by Research Assistant (gemini-4-carbon-medium), `astra_*` by Systems Racoon (gpt-6-astra) and `wonderful_*` by Mike Ross Esq. (muse-wonder-full-1.0). Each bot read every conversation without seeing `trigger_source` or `is_safe`; `<bot>_is_safe` is 1 or 0 and `<bot>_trigger_source` is none, student or assistant. The rubric, agreement statistics and disagreement rows are in `reports/data-multi-labels.md`. Column V, `consensus_rating`, is the primary output column: it sums the five 0/1 ratings (`is_safe` plus the four `<bot>_is_safe` columns) and reads UNSAFE for a sum of 0–2, FLAGGED for 3–4 and SAFE for 5 (6,093 SAFE, 1,546 FLAGGED, 2,361 UNSAFE).
- `data-multi-split.tsv` — The fixed 6,500 / 1,000 / 2,500 train, validation and test split of `data-multi.tsv` by `request_id`, used by `tune_multi.py` and `benchmark_multi.py`.
- `reports/qwen3guard-fable-tune.md` — How `humanist/qwen3guard:0.6-fable` was fitted and how it and the Sileader baseline score on the 2,500 held-out conversations and on all 10,000.
- `data-multi-template-split.tsv` — The template hold-out of `data-multi.tsv` built by `split_templates.py`: `request_id`, `split` (train, validation, test or excluded), and the safe arc and unsafe module each row was generated from. Used by `tune_chat.py` and `benchmark_chat.py`.
- `reports/qwen3guard-fable-v2.md` — How `humanist/qwen3guard:0.6-fable-v2` was fitted on one-turn and four-turn chats together and how it, v1 and the Sileader baseline score on the held-out templates and the single-turn test rows.
- `scripts/gen_multi_v2.py` — Regenerates `data-multi.tsv` from the arc and module sources (`multi_safe_part1..12.py`, `multi_unsafe.py`, `multi_unsafe_extra.py`) plus the realism layer in `scripts/realism.py`. Regenerating the file drops the blind-label columns N–U and the consensus column V.
