"""Finish the real-data Spark replay or run the Flash rounds on the prepared Mac."""

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from common import WORK, atomic_text, read_tsv, require
import tier_data

K = Path(__file__).resolve().parent
PUBLIC = K.parents[1] / "results/klara"
GATE = Path("/tmp/botchu-coord/gate.sh")
FLASH = {
    # Fold count, seconds per OOF fit including predictions, final fit seconds.
    "granite": (2, 1830, 1506),
    "q35-2": (2, 1284, 2568),
    "qguard06": (5, 534, 2664),
}


def invoke(script, *args, heavy=False):
    cmd = [sys.executable, str(K / script), *map(str, args)]
    if heavy and GATE.exists():
        cmd.insert(0, str(GATE))
    print("+", cmd, flush=True)
    subprocess.run(cmd, check=True)


def flash_rounds():
    from spark_experiment import LOGS, RESULTS, source

    records = LOGS / "commands.jsonl"

    def execute(action, model, stage, *args, fold=None):
        events = [json.loads(s) for s in records.read_text().splitlines()] if records.exists() else []
        if any(e.get("action") == action and e["model"] == model and
               e["stage"] == stage and e["fold"] == fold for e in events):
            return
        # Reserve the full merged and converted checkpoint while both may exist.
        used = int(subprocess.check_output(["du", "-sk", WORK]).split()[0]) * 1024
        scratch = 2 * sum(p.stat().st_size for p in source(model).glob("*.safetensors")) + 2_000_000_000
        require(used + scratch <= 50_000_000_000 and shutil.disk_usage(WORK).free >= scratch,
                f"insufficient space for {model} (used {used}, reserve {scratch})")
        invoke("spark_experiment.py", action, model, stage, *args,
               *(["--fold", fold] if fold is not None else []), heavy=True)

    for model, (folds, seconds, final_seconds) in FLASH.items():
        execute("score", model, "baseline")
        common = ["--folds", folds, "--verdict-smoothing", 0.05]
        execute("train", model, "r1", *common, "--seconds", 4770, "--epochs", 2)
        execute("score", model, "r1")
        for i in range(folds):
            execute("train", model, "r1", *common, "--seconds", seconds, "--epochs", 1, fold=i)
        diag = RESULTS / "diagnostics"
        invoke("spark_report.py", "--diagnose", model, "--out", diag)
        by_rule = [r for r in read_tsv(diag / f"{model}-oof-r1-errors.tsv")
                   if r["dimension"] == "rule_id" and int(r["total"])]
        tied = len({int(r["errors"]) / int(r["total"]) for r in by_rule}) == 1
        # Tied fold error rates supply no grounds to prefer three named families.
        weak = len(by_rule) if tied else 3
        events = [json.loads(s) for s in records.read_text().splitlines()]
        spend = sum(e["seconds"] for e in events if e.get("action") == "train"
                    and e["model"] == model and e["fold"] is not None)
        serving = next(e["seconds"] for e in events if e.get("action") == "score"
                       and e["model"] == model and e["stage"] == "r1")
        budget = min(final_seconds, int(5400 - spend - 1.1 * serving - 20))
        require(budget > 0, "no time left for the Flash residual fit")
        execute("train", model, "r2", *common, "--seconds", budget, "--weak-rules", weak,
                "--copies", 1, "--lookalikes", "--positive-weight", 3,
                "--rank", 12, "--lr", 0.0001, "--epochs", 2)
        execute("score", model, "r2")


def report(tier):
    from spark_experiment import LOGS, RESULTS, RUNS, DATA, LICENSE

    target = PUBLIC / tier
    provenance = tier_data.verify(LOGS)
    invoke("spark_report.py", "--out", target)
    (target / "dataset.json").write_bytes((LOGS / "dataset.json").read_bytes())
    tables = target / "tables.md"
    content = f'Final dataset SHA-256 `{provenance["source_sha256"]}`.\n\n' + tables.read_text()
    for dest in (RESULTS / "tables.md", tables):
        with atomic_text(dest) as out:
            out.write(content)
    checks = []
    for model in LICENSE:
        invoke("spark_report.py", "--out", target / "diagnostics", "--diagnose", model)
        for stage in ("baseline", "r1", "r2"):
            path = LOGS / f"{model}-{stage}-verify.log"
            if not path.exists():
                require(stage == "baseline" and model not in ("mezzo", "ettin"),
                        f"missing verification for {model} {stage}")
                checks.append(dict(model=model, stage=stage, observations=1,
                                   check="native prompt token count on GGUF registration", max_absolute_delta=0))
                continue
            records = [json.loads(s) for s in path.read_text().splitlines() if s.startswith("{")]
            if model in ("mezzo", "ettin"):
                record = records[-1]
                require(record["count"] == 5, "expected five TEI fixture lengths")
                kind, worst = "FP16 TEI versus PyTorch logits", record["max_abs_error"]
            else:
                records = records[-5:]
                require(len({r["turns"] for r in records}) == 5, "expected five verified Ollama lengths")
                kind, worst = "HF/GGUF IDs, served length and verdict logit margin", max(r["delta"] for r in records)
            checks.append(dict(model=model, stage=stage, observations=5, check=kind, max_absolute_delta=worst))
    from spark_report import write
    write(target / "serving-parity.tsv", checks)
    if tier != "spark":
        return
    browser = target / "browser"
    browser.mkdir(exist_ok=True)
    os.environ["NODE_PATH"] = str(WORK / "env/node/node_modules")
    for model in LICENSE:
        folder = RUNS / f"{model}-r2"
        scores = RESULTS / f"{model}-r2-validation.tsv"
        dest = RESULTS / f"{model}-r2-browser200.tsv"
        if not dest.exists():
            if not (folder / "browser/onnx").is_dir():
                if model == "smollm":
                    invoke("export_smol_browser.py", "--run", folder, "--out", folder / "browser", heavy=True)
                else:
                    invoke("export_encoder.py", "--hf", folder / "hf", "--out", folder / "browser",
                           "--dtype", "fp16", heavy=True)
            tier_data.verify(LOGS)
            invoke("browser_compare.py", "--data", DATA, "--browser", folder / "browser",
                   "--scores", scores, "--calibration", RESULTS / f"{model}-r2-calibration.json",
                   "--output", dest, *(["--chat"] if model == "smollm" else []), heavy=True)
        for path in (dest, dest.with_suffix(".json")):
            shutil.copy2(path, browser / path.name)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("action", choices=("finish-spark", "run-flash", "finish-flash"))
    a = p.parse_args()
    tier = a.action.split("-")[1]
    os.environ["KLARA_EXPERIMENT_TIER"] = tier
    from spark_experiment import LOGS
    if a.action == "run-flash":
        if not (LOGS / "dataset.json").exists():
            tier_data.prepare(LOGS)
        tier_data.verify(LOGS)
        flash_rounds()
    report(tier)


if __name__ == "__main__":
    main()
