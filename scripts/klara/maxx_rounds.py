"""Resume Maxx from completed score/fit receipts and publish tables after each candidate."""

import json
import os
import subprocess

os.environ["KLARA_EXPERIMENT_TIER"] = "maxx"
from common import atomic_text, read_tsv, require
from maxx_space import PINS, reserve, source_weights
from spark_experiment import LOGS, MODELS, OLLAMA, RESULTS, RUNS, service, source
from tier_data import digest, prepare, verify
from tier_rounds import invoke, report

# Three-hour round including the independent fold fits and final deployed evaluation.
BUDGET = {"phi4": (5, 1050, 5256), "qguard8": (2, 3960, 2274), "q35-4": (2, 2556, 5112)}


def events(model):
    path = LOGS / "commands.jsonl"
    rows = (json.loads(s) for s in path.read_text().splitlines()) if path.exists() else ()
    return [e for e in rows if e.get("model") == model and e.get("action")]


def done(model, action, stage, fold=None):
    return any((e["action"], e["stage"], e["fold"]) == (action, stage, fold) for e in events(model))


def execute(model, action, stage, *args, fold=None):
    if done(model, action, stage, fold):
        return
    verify(LOGS)
    reserve(350_000_000, f"{model} {action} {stage}")
    invoke("spark_experiment.py", action, model, stage, *args,
           *(["--fold", fold] if fold is not None else []), heavy=True)


def release_export(model, stage):
    """Keep source revision, both adapter checkpoints, and every measured R2 deployment."""
    require(stage in ("baseline", "r1") and done(model, "score", stage), "unscored intermediate")
    folder = RUNS / f"{model}-{stage}"
    artifact = folder / "candidate.gguf"
    if not artifact.exists():
        require((folder / "deployed.json").is_file(), "missing deployed-artifact receipt")
        return
    tag = f"klara/cand-maxx-{model}-final-{stage}"
    sha = digest(artifact)
    store = MODELS / "ollama"
    require(artifact.samefile(store / "blobs" / ("sha256-" + sha)), "unexpected private blob")
    with atomic_text(folder / "deployed.json") as f:
        json.dump(dict(tag=tag, bytes=artifact.stat().st_size, sha256=sha), f)
    env = dict(OLLAMA_MODELS=str(store), OLLAMA_HOST="127.0.0.1:18282", OLLAMA_NO_CLOUD="1")
    os.environ.update(env)
    with service("release-" + folder.name, OLLAMA, "/api/tags", "ollama", "serve"):
        subprocess.run(["ollama", "rm", tag], check=True)
    artifact.unlink()


def run_candidate(model):
    folds, fold_seconds, final_seconds = BUDGET[model]
    common = ["--folds", folds, "--verdict-smoothing", 0.05]
    if not done(model, "score", "baseline"):
        invoke("maxx_source.py", model, heavy=True)
        execute(model, "score", "baseline")
    release_export(model, "baseline")
    if not done(model, "train", "r1"):
        invoke("maxx_source.py", model, heavy=True)
        execute(model, "train", "r1", *common, "--seconds", 10020, "--epochs", 2)
    execute(model, "score", "r1")
    if not done(model, "train", "r2"):
        invoke("maxx_source.py", model, heavy=True)
        for i in range(folds):
            execute(model, "train", "r1", *common, "--seconds", fold_seconds, "--epochs", 1, fold=i)
        diag = RESULTS / "diagnostics"
        invoke("spark_report.py", "--diagnose", model, "--out", diag)
        by_rule = [r for r in read_tsv(diag / f"{model}-oof-r1-errors.tsv")
                   if r["dimension"] == "rule_id" and int(r["total"])]
        tied = len({int(r["errors"]) / int(r["total"]) for r in by_rule}) == 1
        times = events(model)
        fold_cost = sum(e["seconds"] for e in times if e["fold"] is not None)
        serving = next(e["seconds"] for e in times if (e["action"], e["stage"]) == ("score", "r1"))
        seconds = min(final_seconds, int(10800 - fold_cost - 1.1 * serving - 60))
        require(seconds > 0, "no time left for final fit")
        execute(model, "train", "r2", *common, "--seconds", seconds,
                "--weak-rules", len(by_rule) if tied else 3, "--copies", 1, "--lookalikes",
                "--positive-weight", 3, "--rank", 12, "--lr", 0.0001, "--epochs", 2)
    release_export(model, "r1")
    execute(model, "score", "r2")
    # Keep exact deployed R2 plus its two mergeable LoRAs. Upstream restores use the pinned revision.
    for path in source_weights(source(model)):
        require(path.is_file() and path.resolve() == path, "unexpected upstream shard")
        path.unlink()


def main():
    os.environ.update(KLARA_RESUME_INTERRUPTED="1", PYTORCH_ENABLE_MPS_FALLBACK="1")
    if not (LOGS / "dataset.json").exists():
        prepare(LOGS)
    completed = []
    for model in PINS:
        verify(LOGS)
        if not done(model, "score", "r2"):
            run_candidate(model)
        completed.append(model)
        report("maxx", completed)


if __name__ == "__main__":
    main()
