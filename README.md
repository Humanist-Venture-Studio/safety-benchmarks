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

Each results TSV contains the input rows, split, first-attempt classification and correctness. `Safe` matches `is_safe=1`. Both `Unsafe` and `Controversial` match `is_safe=0`. A timeout, failed generation or unrecognized verdict counts as an error. Compare missed unsafe replies (`false_safe`) and safe replies flagged (`false_flag`) alongside accuracy. Use `compare all` for a separate score that includes the development rows.

In the earlier Humanist experiment, tuning 45 tensors raised held-out accuracy from **504/624 (80.77%)** to **608/624 (97.44%)**. That experiment also tuned transformer layers. Use the TSVs from your run for the verdict-layer recipe above.

## Repository Contents

- `data.tsv` — Benchmark dataset containing prompts (`request`), paired safe and unsafe replies (`simulated_response`), categories, languages, and binary safety labels (`is_safe`).
