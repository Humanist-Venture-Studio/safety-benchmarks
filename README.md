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

### Single-turn low-rank candidate

On the frozen 624-row test split, the selected candidate scored **603/624 (96.63%)**. Humanist v2 scored **578/624 (92.63%)** and Sileader **513/624 (82.21%)**, with the same prompt and temperature-0 inference. The candidate is the quantization-aware stage-2 checkpoint at step 620, installed locally as `humanist/qwen3guard:0.6b-single-racoon-20261111`. It missed 12 unsafe replies (v2: 33, Sileader: 97) and flagged 9 safe ones (v2: 13, Sileader: 14). This is a fresh comparison on the established split. It does not beat the 608/624 above, which used a different protocol. [`reports/qwen3guard-single-turn-racoon.md`](reports/qwen3guard-single-turn-racoon.md) has the validation selection, hashes, artifact locations, exact reproduction chain and limits.

The recipe uses the session variables, prompt, template and split above. It fits only on `train` and selects only on `validation`.

[`tune_single_lowrank.py`](.agents/skills/tune-qwen-guard/scripts/tune_single_lowrank.py) adds rank-12 updates with scale 2 to `attn_q`, `attn_v`, `attn_output` and `ffn_down` of the original Sileader GGUF and trains on the 1,411 paired training requests (2,822 rows). Stage 1 trains blocks 22–27 for three epochs. Stage 2 keeps that update, adds blocks 12, 14, 16, 18 and 20, and trains three more epochs at half the learning rate with an extra loss that ranks each request's safe reply above its unsafe one. Both stages distil the other reply tokens from the source model so the `Safety:` and `Categories:` lines keep their format. Before training it checks the prompt tokens against Ollama and its forward pass against `llama-server`. Twice per epoch, [`quantize.py`](.agents/skills/tune-qwen-guard/scripts/quantize.py) merges the update into each tensor's original Q4_K or Q6_K type and the checkpoint is scored on validation logits. Each checkpoint that beats the stage's best so far is written to a new `stageN-stepS/` directory: a full-size GGUF, the adapter, `selected.json` and a temperature-0 Modelfile. `stage1` and `stage2` are symlinks that move to that directory only after all of its files are written, so they always name a complete checkpoint. If the trainer is interrupted mid-export, it leaves an incomplete `stageN-stepS/` behind and `stageN` keeps naming the previous checkpoint. Superseded directories keep their GGUFs, about 500 MB each, until you delete them. `--stages 1` stops after stage 1. `--stop-after-step S` ends the run after the first validation at or after step S. The learning-rate schedule stays the full one set by `--epochs`. The forward pass in [`qwen_torch.py`](.agents/skills/tune-qwen-guard/scripts/qwen_torch.py) is adapted from Product Fox's in #8 and supports only Qwen3 0.6B.

The trainer needs PyTorch on top of the packages above. The reference run used Python 3.12 with `gguf` 0.19.0, `numpy` 2.5.4, `scipy` 1.18.1 and `torch` 2.15.0. It trains on Apple-silicon MPS when available and on the CPU otherwise. The seed is fixed, but GPU kernels may not reproduce a run bit for bit.

```bash
"$py" -m pip install torch
"$py" -B "$skill/scripts/tune_single_lowrank.py" --data data.tsv --out "$run/lowrank"
ollama create "$candidate-lr1" -f "$run/lowrank/stage1/Modelfile"
ollama create "$candidate-lr2" -f "$run/lowrank/stage2/Modelfile"
```

[`evaluate_cli.py`](.agents/skills/tune-qwen-guard/scripts/evaluate_cli.py) runs `benchmark.py`'s unchanged evaluator and keeps each first reply in a `.responses.jsonl` file beside the TSV. It accepts only tags whose Modelfile sets `PARAMETER temperature 0`, so compare with a temperature-0 copy of Sileader. [`describe_results.py`](.agents/skills/tune-qwen-guard/scripts/describe_results.py) recounts the TSVs and checks each reply's verdict and category lines.

```bash
ollama show "$base" --modelfile > "$run/sileader.Modelfile"
printf '\nPARAMETER temperature 0\n' >> "$run/sileader.Modelfile"
ollama create "$candidate-base" -f "$run/sileader.Modelfile"
for model in "$candidate-base" "$candidate-lr1" "$candidate-lr2"; do
  "$py" -B "$skill/scripts/evaluate_cli.py" --data data.tsv --model "$model" \
    --split validation --output "$run/${model##*:}-validation.tsv" || break
done
"$py" -B "$skill/scripts/describe_results.py" "$run"/*-validation.tsv
```

To calibrate the verdict rows of the stage that wins on validation, [`refit_head.py`](.agents/skills/tune-qwen-guard/scripts/refit_head.py) runs `tune.py`'s fit on that tag and writes a temperature-0 Modelfile. `--penalties` replaces the fit's L2 penalties (0.4, 0.04 and 0.004 by default). The fit still keeps whichever scores best on validation.

```bash
"$py" -B "$skill/scripts/refit_head.py" --data data.tsv --base "$candidate-lr2" --out "$run/calibrated"
ollama create "$candidate-cal" -f "$run/calibrated/Modelfile"
```

[`tune_single_qat.py`](.agents/skills/tune-qwen-guard/scripts/tune_single_qat.py) is the quantization-aware variant. It runs the same trainer from a candidate fitted only on `train`, such as the calibrated tag above. During training, each tuned tensor is snapped to the base GGUF's own Q4_K or Q6_K block grid, with the gradient passed straight through. Export checks that `quantize.py` reproduces that grid exactly. Its defaults are two epochs per stage, a learning rate of 6e-4 and seed 20261112, with the same rank, scale, stages and output layout. The reported model came from stage 1 of `tune_single_lowrank.py` (`--epochs 3 --stages 1`), then `refit_head.py`, then `tune_single_qat.py` with `--stop-after-step 620`. The report lists every command.

```bash
"$py" -B "$skill/scripts/tune_single_qat.py" --data data.tsv --base "$candidate-cal" --out "$run/qat"
ollama create "$candidate-qat2" -f "$run/qat/stage2/Modelfile"
```

Before scoring `test`, freeze the finalists in a JSON manifest, `{"dataset_sha256": "…", "models": {"<tag>": {"gguf_sha256": "…"}}}`, with the SHA-256 of `data.tsv` and of the `FROM` file in `ollama show <tag> --modelfile`. Then pass `--split test --freeze <manifest>` to `evaluate_cli.py`. Every script refuses an output path that already exists.

## Repository Contents

- `data.tsv` — Benchmark dataset containing prompts (`request`), paired safe and unsafe replies (`simulated_response`), categories, languages, and binary safety labels (`is_safe`).
- `data-multi.tsv` — 10,000 hyper-realistic four-turn student ↔ AI conversations for the same 62 categories: 7,500 safe / 2,500 unsafe (25%). Roughly half the unsafe rows are triggered by the student and half by the assistant (`trigger_source`). Unsafe coverage spans illegal acts (piracy, shoplifting, hacking, vandalism), sexually explicit content and boundary violations, substances, violence, self-harm signals, privacy, scams, and hate speech. Every row (including the original 2,000) goes through a deterministic realism pass (chat abbreviations, occasional typos, exclamation moderation), and rows are deduplicated across the whole file. See `reports/data-multi-qa.md` for composition, coverage stats, and the dataset's self-graded quality assessment (**A-**). Columns N–U hold four independent blind relabellings: `fable_*` by Product Fox (claude-fable-5-2), `gemini_*` by Research Assistant (gemini-4-carbon-medium), `astra_*` by Systems Racoon (gpt-6-astra) and `wonderful_*` by Mike Ross Esq. (muse-wonder-full-1.0). Each bot read every conversation without seeing `trigger_source` or `is_safe`; `<bot>_is_safe` is 1 or 0 and `<bot>_trigger_source` is none, student or assistant. The rubric, agreement statistics and disagreement rows are in `reports/data-multi-labels.md`. Column V, `consensus_rating`, is the primary output column: it sums the five 0/1 ratings (`is_safe` plus the four `<bot>_is_safe` columns) and reads UNSAFE for a sum of 0–2, FLAGGED for 3–4 and SAFE for 5 (6,093 SAFE, 1,546 FLAGGED, 2,361 UNSAFE).
- `scripts/gen_multi_v2.py` — Regenerates `data-multi.tsv` from the arc and module sources (`multi_safe_part1..12.py`, `multi_unsafe.py`, `multi_unsafe_extra.py`) plus the realism layer in `scripts/realism.py`. Regenerating the file drops the blind-label columns N–U and the consensus column V.
