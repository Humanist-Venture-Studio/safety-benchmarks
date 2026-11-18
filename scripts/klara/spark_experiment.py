"""Replay a Spark experiment pass using the task's local model sources and services."""

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

SCRIPTS = Path(__file__).resolve().parent
MODELS = WORK / "models"
RUNS = MODELS / "spark-real"
LOGS = WORK / "logs/spark"
RESULTS = WORK / "results/spark"
revision = os.environ.get("KLARA_SPARK_RUN", "")
require(not revision or re.fullmatch(r"[a-z0-9-]+", revision), "invalid Spark run name")
CHAT_NAME = "smollm-real"
if revision:
    RUNS, LOGS, RESULTS = RUNS / revision, LOGS / revision, RESULTS / revision
    CHAT_NAME += "-" + revision
DATA = LOGS / "development.tsv"
PYTHON = WORK / "env/venv/bin/python"
FIXTURE = WORK / "logs/tuning-fixture.tsv"
TEI = "http://127.0.0.1:18281"
OLLAMA = "http://127.0.0.1:18282"
LICENSE = {"mezzo": "Apache-2.0", "ettin": "MIT", "smollm": "Apache-2.0"}


def record(event):
    with (LOGS / "commands.jsonl").open("a") as f:
        print(json.dumps(event), file=f)


def run(name, *args):
    cmd = list(map(str, args))
    start = time.time()
    tick = time.monotonic()
    with (LOGS / (name + ".log")).open("a") as log:
        code = subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT).returncode
    record(
        dict(
            step=name, argv=cmd, start=start, seconds=time.monotonic() - tick, code=code
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
    src = MODELS / "source" / model
    is_chat = model == "smollm"
    baseline = stage == "baseline"
    options = []
    if is_chat:
        tag = f"klara/cand-spark-{CHAT_NAME}-{stage}"
        with_service = service(name, OLLAMA, "/api/tags", "ollama", "serve")
        options = ["--backend", "ollama", "--endpoint", OLLAMA, "--model", tag]
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
                    "spark",
                    "--name",
                    CHAT_NAME,
                    "--round",
                    stage,
                    "--quant",
                    "Q8_0",
                    *(["--baseline-source", src] if baseline else []),
                )
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
        require(nbytes <= 250_000_000, "Spark size cap exceeded")
        for split in ("train-sample", "validation"):
            out = RESULTS / f"{name}-{split}-raw.tsv"
            if not out.exists():
                run(
                    name + "-" + split,
                    PYTHON,
                    SCRIPTS / "benchmark.py",
                    "--tier",
                    "spark",
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
):
    src = MODELS / "source" / model
    name = model + "-" + stage if fold is None else model + f"-fold{fold}"
    is_chat = model == "smollm"
    cmd = [
        PYTHON,
        SCRIPTS / ("train_chat.py" if is_chat else "train_encoder.py"),
        "--tier",
        "spark",
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
        4 if is_chat else 8,
        "--max-planning-rate",
        {"mezzo": 7459, "ettin": 7437, "smollm": 3156}[model],
    ]
    if is_chat:
        cmd.extend(["--rank", rank, "--verdict-smoothing", 0.05])
    else:
        cmd.extend(["--precision", "fp16"])
    if stage == "baseline":
        require(model == "ettin", "only Ettin fits a baseline head")
        cmd.append("--probe")
    if fold is not None:
        cmd.extend(["--fold", fold, "--eval-batch", 16])
    elif stage == "r2":
        cmd.extend(
            [
                "--eval-batch",
                16,
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
            cmd.extend(
                ["--init-adapter", RUNS / f"{model}-r1" / "adapter", "--q8-aware"]
            )
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
    require(DATA.is_file(), "prepare train and validation projection first")
    RESULTS.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256(DATA.read_bytes()).hexdigest()
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
    if a.action == "train":
        train(
            a.model,
            a.stage,
            a.seconds,
            a.folds,
            a.fold,
            a.lr or (2e-4 if a.model == "smollm" else 3e-5),
            a.epochs,
            a.copies,
            a.rank,
            a.weak_rules,
            a.lookalikes,
            a.positive_weight,
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
