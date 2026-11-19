"""Replay a Spark or Flash experiment pass using the task's local model sources and services."""

import argparse
import csv
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import urllib.request
from contextlib import contextmanager
from pathlib import Path

from calibrate import apply
from common import WORK, atomic_text, read_tsv, require
from results import validate_run
import tier_data

SCRIPTS = Path(__file__).resolve().parent
MODELS = WORK / "models"
TIER = os.environ.get("KLARA_EXPERIMENT_TIER", "spark")
require(TIER in ("spark", "flash"), "unknown experiment tier")
RUNS = MODELS / (TIER + "-real")
LOGS = WORK / "logs" / TIER
RESULTS = WORK / "results" / TIER
revision = os.environ.get(f"KLARA_{TIER.upper()}_RUN", "")
require(not revision or re.fullmatch(r"[a-z0-9-]+", revision), "invalid Spark run name")
CHAT_NAME = "smollm-final"
if revision:
    RUNS, LOGS, RESULTS = RUNS / revision, LOGS / revision, RESULTS / revision
    CHAT_NAME += "-" + revision
DATA = LOGS / "development.tsv"
PYTHON = WORK / "env/venv/bin/python"
FIXTURE = WORK / "logs/tuning-fixture.tsv"
TEI = "http://127.0.0.1:18281"
OLLAMA = "http://127.0.0.1:18282"
LICENSE = {"mezzo": "Apache-2.0", "ettin": "MIT", "smollm": "Apache-2.0"}


FLASH_QUANT = {"granite": "Q5_K_M", "q35-2": "Q6_K", "qguard06": "F16"}
if TIER == "flash":
    LICENSE = dict.fromkeys(FLASH_QUANT, "Apache-2.0")


def source(model):
    if model in ("q35-2", "qguard06"):
        return MODELS / "tier-proof" / model / "source"
    return MODELS / "source" / model


def is_chat_model(model):
    return model == "smollm" or model in FLASH_QUANT


def record(event):
    with (LOGS / "commands.jsonl").open("a") as f:
        print(json.dumps(event), file=f)


def run(name, *args):
    provenance = tier_data.verify(LOGS)
    cmd = list(map(str, args))
    start = time.time()
    tick = time.monotonic()
    with (LOGS / (name + ".log")).open("a") as log:
        code = subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT).returncode
    record(
        dict(
            step=name, argv=cmd, start=start, seconds=time.monotonic() - tick, code=code, **provenance
        )
    )
    require(code == 0, f"{name} exited {code}; see its log")


@contextmanager
def service(name, url, route, *cmd):
    # A fresh child owns this port for the pass. Never send traffic to a pre-existing listener.
    import socket
    from urllib.parse import urlparse

    with socket.socket() as sock:
        require(
            sock.connect_ex(("127.0.0.1", urlparse(url).port)) != 0, f"{url} in use"
        )
    with (LOGS / (name + "-service.log")).open("a") as log:
        proc = subprocess.Popen(
            list(map(str, cmd)), stdout=log, stderr=subprocess.STDOUT
        )
        try:
            for _ in range(120):
                require(proc.poll() is None, "service failed to start")
                try:
                    with urllib.request.urlopen(url + route, timeout=1) as response:
                        json.load(response)
                    break
                except OSError:
                    time.sleep(0.5)
            else:
                raise RuntimeError("service startup timeout")
            yield
        finally:
            if proc.poll() is None:
                proc.terminate()
                proc.wait(timeout=30)


def native_export(source, dest):
    import torch
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    model = AutoModelForSequenceClassification.from_pretrained(
        source, dtype=torch.float16
    )
    model.save_pretrained(dest)
    AutoTokenizer.from_pretrained(source).save_pretrained(dest)
    path = dest / "config.json"
    cfg = json.loads(path.read_text())
    cfg["num_labels"] = model.config.num_labels
    for scope, layer in (("global", "full_attention"), ("local", "sliding_attention")):
        cfg[f"{scope}_rope_theta"] = model.config.rope_parameters[layer]["rope_theta"]
    path.write_text(json.dumps(cfg, indent=2))


def calibrate_pass(name):
    val = RESULTS / f"{name}-validation-raw.tsv"
    train = RESULTS / f"{name}-train-sample-raw.tsv"
    spec_path = RESULTS / f"{name}-calibration.json"
    fitted = RESULTS / f"{name}-validation.tsv"
    if not spec_path.exists():
        classes = {r["is_unsafe"] for r in read_tsv(val) if not r["error"]}
        if classes != {"0", "1"}:
            print(f"{name}: insufficient valid classes for Platt fitting", flush=True)
            return
        run(
            name + "-calibrate",
            PYTHON,
            SCRIPTS / "calibrate.py",
            val,
            "--output",
            spec_path,
            "--calibrated-tsv",
            fitted,
        )
    spec = json.loads(spec_path.read_bytes())
    dest = RESULTS / f"{name}-train-sample.tsv"
    if dest.exists():
        return
    rows = list(read_tsv(train))
    validate_run(rows)
    digest = hashlib.sha256(spec_path.read_bytes()).hexdigest()
    for r in rows:
        require(
            all(r[k] == value for k, value in spec["identity"].items()),
            "calibration mismatch",
        )
        r.update(threshold=spec["threshold"], calibration_sha256=digest)
        if not r["error"]:
            p = apply(float(r["raw_probability"]), spec)
            flag = p >= spec["threshold"]
            r.update(
                unsafe_probability=p,
                label="unsafe" if flag else "safe",
                correct=int(flag == bool(int(r["is_unsafe"]))),
            )
    with atomic_text(dest, replace=False) as out:
        writer = csv.DictWriter(
            out, rows[0].keys(), delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)
    validate_run(list(read_tsv(dest)))


def pass_run(model, stage):
    name = model + "-" + stage
    folder = RUNS / name
    src = source(model)
    is_chat = is_chat_model(model)
    baseline = stage == "baseline"
    options = []
    if is_chat:
        chat_name = CHAT_NAME if model == "smollm" else "-".join(filter(None, (model, "final", revision)))
        tag = f"klara/cand-{TIER}-{chat_name}-{stage}"
        native = {"granite": "granite", "qguard06": "qwen-guard"}.get(model) if baseline else None
        with_service = service(name, OLLAMA, "/api/tags", "ollama", "serve")
        options = ["--backend", "ollama", "--endpoint", OLLAMA, "--model", tag]
        if native:
            options.extend(["--native", native, "--native-tokenizer", src])
        if not baseline:
            options.extend(["--safe-token", " safe", "--unsafe-token", " unsafe"])
    else:
        hf = folder / "hf"
        if model == "mezzo" and baseline and not hf.exists():
            native_export(src, hf)
        with_service = service(
            name,
            TEI,
            "/info",
            "text-embeddings-router",
            "--model-id",
            hf,
            "--dtype",
            "float16",
            "--hostname",
            "127.0.0.1",
            "--port",
            "18281",
        )
        options = ["--backend", "tei", "--endpoint", TEI, "--model", hf]
        if model == "mezzo" and baseline:
            options.extend(["--native", "mezzo"])
    with with_service:
        if is_chat:
            artifact = folder / "candidate.gguf"
            if not artifact.exists():
                run(
                    name + "-export",
                    PYTHON,
                    SCRIPTS / "export_chat.py",
                    "--run",
                    folder,
                    "--tier",
                    TIER,
                    "--name",
                    chat_name,
                    "--round",
                    stage,
                    "--quant",
                    FLASH_QUANT.get(model, "Q8_0"),
                    *(["--native-baseline", native] if native else []),
                    *(["--baseline-source", src] if baseline else []),
                )
            if TIER == "flash":
                # The private Ollama store and the kept export are the same GGUF.
                # Link the verified blob so keeping nine candidates costs one copy apiece.
                digest = tier_data.digest(artifact)
                blob = MODELS / "ollama/blobs" / ("sha256-" + digest)
                require(blob.is_file() and tier_data.digest(blob) == digest,
                        "private Ollama blob differs from exported artifact")
                if not os.path.samefile(artifact, blob):
                    link = artifact.with_suffix(".verified-link")
                    os.link(blob, link)
                    link.replace(artifact)
            if not baseline:
                run(
                    name + "-verify",
                    PYTHON,
                    SCRIPTS / "verify_chat.py",
                    "--run",
                    folder,
                    "--tag",
                    tag,
                    "--data",
                    FIXTURE,
                )
        else:
            artifact = hf / "model.safetensors"
            run(
                name + "-verify",
                PYTHON,
                SCRIPTS / "parity.py",
                "--hf",
                hf,
                "--data",
                FIXTURE,
                "--endpoint",
                TEI,
            )
        nbytes = artifact.stat().st_size
        from export_chat import BOUNDS
        low, high = BOUNDS[TIER]
        require(low <= nbytes <= high, f"{TIER} deployment size out of bounds")
        for split in ("train-sample", "validation"):
            out = RESULTS / f"{name}-{split}-raw.tsv"
            if not out.exists():
                run(
                    name + "-" + split,
                    PYTHON,
                    SCRIPTS / "benchmark.py",
                    "--tier",
                    TIER,
                    "--stage",
                    name,
                    "--split",
                    split,
                    "--data",
                    DATA,
                    "--size-bytes",
                    nbytes,
                    "--licence",
                    LICENSE[model],
                    "--output",
                    out,
                    *(["--resume-interrupted"] if os.environ.get("KLARA_RESUME_INTERRUPTED") == "1"
                      and out.with_suffix(out.suffix + ".partial").exists() else []),
                    *options,
                )
    calibrate_pass(name)


def train(
    model,
    stage,
    seconds,
    folds,
    fold,
    lr,
    epochs,
    copies,
    rank,
    weak_rules,
    lookalikes,
    positive_weight,
    smoothing,
):
    src = source(model)
    name = model + "-" + stage if fold is None else model + f"-fold{fold}"
    is_chat = is_chat_model(model)
    cmd = [
        PYTHON,
        SCRIPTS / ("train_chat.py" if is_chat else "train_encoder.py"),
        "--tier",
        TIER,
        "--source",
        src,
        "--data",
        DATA,
        "--out",
        RUNS / name,
        "--seconds",
        seconds,
        "--folds",
        folds,
        "--epochs",
        epochs,
        "--lr",
        lr,
        "--positive-weight",
        positive_weight,
        "--batch",
        2 if TIER == "flash" else (4 if is_chat else 8),
        "--max-planning-rate",
        {"mezzo": 7459, "ettin": 7437, "smollm": 3156, "granite": 526, "q35-2": 649, "qguard06": 1338}[model],
    ]
    if is_chat:
        cmd.extend(["--rank", rank, "--verdict-smoothing", smoothing])
    else:
        cmd.extend(["--precision", "fp16"])
    if stage == "baseline":
        require(model == "ettin", "only Ettin fits a baseline head")
        cmd.append("--probe")
    eval_batch = 8 if TIER == "flash" else 16
    if fold is not None:
        cmd.extend(["--fold", fold, "--eval-batch", eval_batch])
    elif stage == "r2":
        cmd.extend(
            [
                "--eval-batch",
                eval_batch,
                "--oof",
                *[RUNS / f"{model}-fold{i}" / "oof.json" for i in range(folds)],
                "--extra-copies",
                copies,
                "--weak-rule-count",
                weak_rules,
            ]
        )
        if lookalikes:
            cmd.append("--repeat-lookalikes")
        if is_chat:
            previous = RUNS / f"{model}-r1"
            cmd.extend(["--init-adapter", previous / "adapter"])
            if model == "smollm":
                cmd.append("--q8-aware")
            elif model == "qguard06":
                cmd.append("--fp16")
            else:
                cmd.extend(["--r1-gguf", previous / "candidate.gguf"])
        else:
            cmd.extend(["--init-checkpoint", RUNS / f"{model}-r1" / "hf"])
    run(name + "-fit", *cmd)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("action", choices=["score", "train"])
    p.add_argument("model", choices=LICENSE)
    p.add_argument("stage", choices=["baseline", "r1", "r2"])
    p.add_argument("--seconds", type=int, default=970)
    p.add_argument("--folds", type=int, default=2)
    p.add_argument("--fold", type=int)
    p.add_argument("--lr", type=float)
    p.add_argument("--epochs", type=int, default=2)
    p.add_argument("--copies", type=int, default=1)
    p.add_argument("--rank", type=int, default=8)
    p.add_argument("--weak-rules", type=int, default=0)
    p.add_argument("--lookalikes", action="store_true")
    p.add_argument("--positive-weight", type=float, default=3)
    p.add_argument("--verdict-smoothing", type=float, default=0.05 if TIER == "spark" else 0.0)
    a = p.parse_args()
    os.environ.update(
        HF_HUB_OFFLINE="1",
        TOKENIZERS_PARALLELISM="false",
        HF_HOME=str(WORK / "env/hf-cache"),
        NODE_PATH=str(WORK / "env/node/node_modules"),
        OLLAMA_HOST="127.0.0.1:18282",
        OLLAMA_MODELS=str(MODELS / "ollama"),
        OLLAMA_NO_CLOUD="1",
    )
    provenance = tier_data.verify(LOGS)
    require(DATA.is_file(), "prepare train and validation projection first")
    RESULTS.mkdir(parents=True, exist_ok=True)
    with atomic_text(RESULTS / "dataset.json") as f:
        json.dump(provenance, f)
        f.write("\n")
    digest = provenance["development_sha256"]
    signature = LOGS / "development.sha256"
    if not signature.exists():
        with atomic_text(signature, replace=False) as f:
            f.write(digest + "\n")
    require(
        signature.read_text().strip() == digest,
        "development data changed; select a fresh KLARA_SPARK_RUN",
    )
    start = time.time()
    tick = time.monotonic()
    if a.action == "train" and a.stage == "r2" and TIER == "spark":
        # Fold costs depend on the hardware. Keep the same maximum fit allocation,
        # leaving the measured cost of exporting and scoring in the twenty minutes.
        events = [json.loads(line) for line in (LOGS / "commands.jsonl").read_text().splitlines()]
        fold_seconds = sum(e["seconds"] for e in events if e.get("action") == "train"
                           and e["model"] == a.model and e["fold"] is not None)
        serve_seconds = next(e["seconds"] for e in events if e.get("action") == "score"
                             and e["model"] == a.model and e["stage"] == "r1")
        a.seconds = min(a.seconds, int(1200 - fold_seconds - serve_seconds - 10))
        require(a.seconds > 0, "no Spark round-two fit time remaining")
        if a.model == "smollm":
            from spark_report import fold_errors
            meta = {r["row_id"]: r for r in read_tsv(DATA)}
            rules = [r for r in fold_errors(a.model, meta) if r["dimension"] == "rule_id" and r["total"]]
            if len({r["errors"] / r["total"] for r in rules}) > 1:
                a.weak_rules = 3
    if a.action == "train":
        train(
            a.model,
            a.stage,
            a.seconds,
            a.folds,
            a.fold,
            a.lr or (2e-4 if is_chat_model(a.model) else 3e-5),
            a.epochs,
            a.copies,
            a.rank,
            a.weak_rules,
            a.lookalikes,
            a.positive_weight,
            a.verdict_smoothing,
        )
    else:
        pass_run(a.model, a.stage)
    record(
        dict(
            action=a.action,
            model=a.model,
            stage=a.stage,
            fold=a.fold,
            seconds=time.monotonic() - tick,
            start=start,
            argv=sys.argv,
        )
    )


if __name__ == "__main__":
    main()
