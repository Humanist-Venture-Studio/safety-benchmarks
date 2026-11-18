# Spark validation experiment

The training sample contains 900 safe and 100 unsafe conversations. Validation contains a separate 900 safe and 100 unsafe, with 125 whole scenarios. The experiment used a train-and-validation projection with SHA-256 `35dc6de07ac3db2bb1c66c6cf7f31cccc51c1cd5fb2c5858c1bd024c09dda223`. Test remained sealed.

**I recommend Ettin round two for TEI deployment.** It scored 990/1,000 with two false positives and eight missed unsafe rows. Mezzo round two scored 989/1,000 with the same two false positives. On their nine disagreements, Ettin was correct five times and Mezzo four. Mezzo retained all 200 TEI labels on the browser check. Ettin changed one borderline self-harm signal from unsafe to safe. All candidates and exports remain available for the owner's selection.

[Training-sample and validation tables](tables.md) give both raw and selected operating points. [Per-pass metadata](pass-metadata.tsv) gives exact cutoffs, Platt coefficients, byte counts, licences, optimizer exposures and elapsed machine minutes. [Metrics at both cutoffs](metrics.tsv) includes confusion counts, Wilson intervals for rates, AUROC, average precision and Brier score. The [round-two validation errors](round2-errors.tsv) include denominators. A rule with zero positive examples has no validation recall estimate.

Each classifier made one deployment request per row. The `*-raw.tsv` files record the uncalibrated probability at cutoff 0.5. The `*-selected.tsv` files apply a nonnegative-slope Platt fit and an accuracy-maximizing cutoff, both fitted to that pass's first-attempt validation probabilities. Tied accuracy favors fewer false positives. Training-sample results use the same frozen fit. A blank probability or label marks a malformed response and counts against accuracy. A failed unsafe row counts as missed. Average precision, AUROC and Brier use valid probabilities. These validation results include the benefit of choosing the cutoff on those same rows.

Training used seed 20261117, a scenario-grouped stop set within train, and a timer that selected a stratified set of whole training scenarios. A pass's unique fit count covers examples that entered an optimizer update. Repeated exposures, early-stop loss and the selected checkpoint are recorded in [fit recipes](fit-recipes.json). Two independent folds supplied one held-scenario prediction per training row for each candidate before round two. The folds started from the original source. Error-based repetition, weak rule families and safe look-alikes came from training predictions. Round-two time includes these auxiliary fits. Training and scoring minutes appear once per pass, repeated in the two split tables.

## Round-two fitting decisions

**Mezzo.** The raw first-round validation model falsely flagged eight look-alikes and zero ordinary rows. Independent training folds produced 72 misses and 54 false positives, including 43 look-alikes. The second epoch had raised train-only stop loss from 0.070 to 0.279, so the warm start used one FP16 epoch at 0.00001, one extra copy of the OOF errors, safe look-alikes and three weak rules (A11, A1 and A10). Validation gained three correct rows by removing three false positives at the fitted cutoff.

**Ettin.** Its training folds missed 143 unsafe rows and falsely flagged 103 safe rows, including 81 look-alikes. The second epoch had raised stop loss from 0.079 to 0.165. One FP16 epoch at 0.00001 repeated OOF errors, look-alikes and rules A4, A13 and A12. At the fitted cutoff it improved from 985 to 990 correct, recovering four additional unsafe rows and removing one false positive.

**SmolLM2.** The short-budget training folds fitted 328 and 128 unique rows, respectively, and missed all 800 unsafe OOF rows. Every rule therefore tied on miss rate. The round-two warm start used rank 12 (round one used 8), half the learning rate, Q8_0 simulation on the merged projections and shared embedding, and doubled occurrences of missed positives and their safe look-alikes in the fitting subset. A setup without the linked negatives was interrupted before any checkpoint or score and charged 65.7 seconds to the same round. The sampler drew its evidence and repeated rows from train. At the fitted cutoff, validation accuracy rose from 97.4% to 98.1% and false positives fell from 23 to 10, while missed unsafe rows rose from 3 to 9. The untouched chat baseline produced 2,000 malformed first attempts, leaving no probabilities to calibrate.

The [diagnostics](diagnostics/) give first-round raw mistakes on validation and held training scenarios. The out-of-fold probabilities come from independently trained PyTorch replicas. Two validation rule families, A5 emotion probing and A12 advertising, have zero unsafe examples.

## Browser and service verification

Both encoders used FP16 ONNX. SmolLM2 qualified for export at 0.9 percentage points below the best encoder on validation. Its ONNX stores Q8_0 blocks for the merged projections and shared embedding, and emits the two logits at the verdict boundary. The seeded comparison used the same 200 rows (167 safe, 33 unsafe) and the same validation calibration and cutoff as the corresponding service.

| Round two | ONNX bytes | Package bytes | Raw absolute difference, max / mean | Calibrated absolute difference, max / mean | Label flips |
|---|---:|---:|---:|---:|---:|
| Mezzo | 137,408,929 | 140,994,583 | 0.000266 / 0.00000226 | 0.001831 / 0.00004400 | 0/200 |
| Ettin | 137,408,929 | 140,994,583 | 0.017311 / 0.00019673 | 0.005175 / 0.00005678 | 1/200 |
| SmolLM2 | 144,331,605 | 147,856,251 | 0.001917 / 0.00009249 | 0.001524 / 0.00005817 | 1/200 |

Both flips were unsafe rows whose served probabilities equaled the selected cutoff. The Node scores fell just below it. The [paired browser probabilities](browser/) identify each row. The [service checks](serving-parity.tsv) compare PyTorch with TEI or Ollama. Node ran Transformers.js on CPU. Actual browser hardware and WASM execution remain unmeasured.

## Reproduction on the prepared Mac

Run from the repository root. Use a new run name for a replay to retain the original models, Ollama tags and first-attempt results. The snapshot selects on the split prefix before a transcript is decoded.

```sh
w="$HOME/klara-tiers"
export KLARA_SPARK_RUN=replay-01
l="$w/logs/spark/$KLARA_SPARK_RUN"
mkdir -p "$l"
LC_ALL=C rg --no-heading --no-filename --no-line-number \
  '^(row_id\tsplit\t|K[0-9]{5}\t(train|validation)\t)' "$w/data/data-klara.tsv" > "$l/development.tsv"
shasum -a 256 "$l/development.tsv"
p="$w/env/venv/bin/python"
k=scripts/klara
```

The experiment runner uses the synthetic parity fixture at `$w/logs/tuning-fixture.tsv`. If constructing a new environment, use the fixture generator at that path. The source revisions, original commands and exact selected scenario IDs are recorded with the results. The local `results/spark/fit-membership/` files identify individual optimizer rows. The timer uses the hardware's observed speed, so a timed replay can select a different subset.

Run heavy commands serially. Use the host gate when available. The following example replays Mezzo's native five-label FP16 baseline and its first full fine-tune. The scorer starts a private TEI process, verifies raw logits against PyTorch, and benchmarks each split. The chat path uses the private Ollama service and Q8_0 GGUF.

```sh
spark() {
  if test -x /tmp/botchu-coord/gate.sh; then
    /tmp/botchu-coord/gate.sh "$p" "$k/spark_experiment.py" "$@"
  else
    "$p" "$k/spark_experiment.py" "$@"
  fi
}
spark score mezzo baseline
spark train mezzo r1 --seconds 970 --epochs 2 --folds 5 --lr 0.00003
spark score mezzo r1
```

To replay all recorded training and scoring commands, start with a fresh run name and prepared projection, then run the following in place of the three example passes above.

```sh
"$p" - <<'PYTHON'
import json
import subprocess
import sys
from pathlib import Path

gate = Path("/tmp/botchu-coord/gate.sh")
prefix = [str(gate)] if gate.exists() else []
recipe = json.loads(Path("results/klara/spark/fit-recipes.json").read_bytes())
for args in recipe["spark_experiment_arguments"]:
    subprocess.run([*prefix, sys.executable, "scripts/klara/spark_experiment.py", *args], check=True)
PYTHON
```

For Ettin, fit the frozen probe with `train ettin baseline --epochs 3 --lr 0.001 --seconds 450` before scoring it. SmolLM2's baseline uses the upstream chat template and the fixed Klara prompt. For round two, run the training folds, inspect `spark_report.py --diagnose MODEL --out DIRECTORY`, then use the recorded rate, epochs, class weight and resampling options for the final fit. `browser_compare.py` uses the saved TEI or Ollama validation scores and the same 200 seeded validation IDs for each browser comparison.

To recount any public score file from a clean checkout, pass its rows to the same metrics function the benchmark uses.

```sh
PYTHONPATH=scripts/klara python3 - <<'PY'
from pathlib import Path
from common import read_tsv
from metrics import metrics

for path in sorted(Path("results/klara/spark").glob("*-validation-*.tsv")):
    print(path.name, metrics(list(read_tsv(path))))
PY
```

The Mac entered clamshell sleep during Mezzo round one's validation benchmark. Its machine-time estimate uses the sum of monotonic row latencies for that step (45.89 seconds, versus 645.09 seconds on the wall clock) and the trainer's internal active timer for its first fit. Ettin's frozen probe also crossed a logged 68-second maintenance sleep, which was deducted. Subsequent commands use monotonic timers. Browser exports and 200-row Node comparisons are timed separately from the core tuning and benchmark passes.

For the encoder browser checks in a fresh replay, use the retained round-two FP16 classifiers and calibrated score files.

```sh
export NODE_PATH="$w/env/node/node_modules"
for model in mezzo ettin; do
  dir="$w/models/spark-real/$KLARA_SPARK_RUN/$model-r2"
  res="$w/results/spark/$KLARA_SPARK_RUN"
  "$p" "$k/export_encoder.py" --hf "$dir/hf" --out "$dir/browser" --dtype fp16
  "$p" "$k/browser_compare.py" --data "$l/development.tsv" --browser "$dir/browser" \
    --scores "$res/$model-r2-validation.tsv" --calibration "$res/$model-r2-calibration.json" \
    --output "$res/$model-r2-browser200.tsv"
done
```

For the round-two SmolLM2 export and its paired comparison, set `dir="$w/models/spark-real/$KLARA_SPARK_RUN/smollm-r2"` and `res="$w/results/spark/$KLARA_SPARK_RUN"` and run these commands.

```sh
"$p" "$k/export_smol_browser.py" --run "$dir" --out "$dir/browser"
"$p" "$k/browser_compare.py" --chat --data "$l/development.tsv" --browser "$dir/browser" \
  --scores "$res/smollm-r2-validation.tsv" --calibration "$res/smollm-r2-calibration.json" \
  --output "$res/smollm-r2-browser200.tsv"
```
