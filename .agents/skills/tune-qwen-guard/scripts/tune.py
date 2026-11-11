"""Fit the three Qwen3Guard verdict-token weights and export a separate Ollama candidate."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
import http.client
import json
from pathlib import Path
import re
import shutil
import socket
import subprocess
import tempfile
import time
import urllib.request

from gguf import GGUFReader, GGMLQuantizationType, dequantize
import numpy as np
from scipy.optimize import minimize
from scipy.special import expit

from benchmark import load_cases, prompt

BASE = "sileader/qwen3guard:0.6b"
OLLAMA = "http://127.0.0.1:11434"
VERDICTS = (" Safe", " Unsafe", " Controversial")


def ollama(endpoint, payload):
    request = urllib.request.Request(OLLAMA + endpoint, data=json.dumps(payload).encode(),
                                     headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=120) as response:
        return json.load(response)


@contextmanager
def embedding_server(executable, model):
    with tempfile.TemporaryDirectory(prefix="qwen-") as tmp:
        sock = str(Path(tmp, "embed.sock"))

        class LocalConnection(http.client.HTTPConnection):
            def connect(self):
                self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                self.sock.settimeout(120)
                self.sock.connect(sock)

        def request(endpoint, body=None):
            conn = LocalConnection("localhost")
            try:
                conn.request("GET" if body is None else "POST", endpoint,
                             body=None if body is None else json.dumps(body),
                             headers={"Content-Type": "application/json"})
                response = conn.getresponse()
                if response.status != 200:
                    raise RuntimeError(f"{endpoint}: {response.status} {response.read()[:500]!r}")
                return json.load(response)
            finally:
                conn.close()

        log = Path(tmp, "server.log")
        with log.open("wb") as stream:
            proc = subprocess.Popen([executable, "-m", str(model), "--embedding", "--pooling", "last",
                                     "--host", sock, "-np", "4", "-c", "8192"], stdout=stream, stderr=stream)
            try:
                deadline = time.monotonic() + 120
                while time.monotonic() < deadline:
                    if proc.poll() is not None:
                        raise RuntimeError(log.read_text(errors="replace")[-2000:])
                    try:
                        request("/health")
                        break
                    except (OSError, RuntimeError):
                        time.sleep(0.25)
                else:
                    raise RuntimeError("Timed out starting llama-server")
                yield request
            finally:
                if proc.poll() is None:
                    proc.terminate()
                    try:
                        proc.wait(10)
                    except subprocess.TimeoutExpired:
                        proc.kill()
                        proc.wait()


def q6_rows(weights):
    """Encode each 256-weight Q6_K block as low bits, high bits, 16 scales and one FP16 scale."""
    groups = weights.astype(np.float32).reshape(-1, 16, 16)
    peak = np.max(np.abs(groups), axis=2)
    block_scale = (peak.max(axis=1) / (127 * 31)).astype("<f2")
    scale = block_scale.astype(np.float32)[:, None]
    group_scale = np.rint(peak / (31 * np.where(scale == 0, 1, scale))).clip(1, 127).astype(np.int8)
    step = group_scale * scale
    codes = (32 + np.rint(groups / np.where(step == 0, 1, step)[:, :, None])).clip(0, 63).astype(np.uint8)
    lo = (codes & 15).reshape(-1, 2, 2, 64)
    hi = (codes >> 4).reshape(-1, 2, 4, 32)
    low_bits = lo[:, :, 0] | (lo[:, :, 1] << 4)
    high_bits = hi[:, :, 0] | (hi[:, :, 1] << 2) | (hi[:, :, 2] << 4) | (hi[:, :, 3] << 6)
    blocks = np.column_stack((low_bits.reshape(-1, 128), high_bits.reshape(-1, 64),
                              group_scale, block_scale.view(np.uint8).reshape(-1, 2))).astype(np.uint8)
    return blocks.reshape(len(weights), -1)


def collect(request, template, train, validation):
    def tokenize(text):
        return request("/tokenize", {"content": text, "add_special": False, "parse_special": True})["tokens"]

    def embed(text):
        tokens = tokenize(text)
        if len(tokens) > 2048:
            raise ValueError("Example exceeds the configured 2,048-token slot")
        vector = request("/embedding", {"content": tokens, "embd_normalize": -1})[0]["embedding"]
        return np.asarray(vector, dtype=np.float64).reshape(-1)

    words = [tokenize(v) for v in VERDICTS]
    ids = [word[0] for word in words]
    if len(words[0]) != 1 or len(words[1]) != 1 or len(set(ids)) != 3:
        raise ValueError("Unexpected verdict tokenization for this checkpoint")

    def render(row):
        return template.replace("{{ .Prompt }}", prompt(row))

    # Compare a training prompt token-for-token with the actual Ollama generation context.
    expected = tokenize(render(train[0]))
    probe = ollama("/api/generate", {"model": BASE, "prompt": prompt(train[0]), "stream": False,
                                    "options": {"num_predict": 1}})
    if probe.get("eval_count") != 1 or probe.get("context", [])[:-1] != expected:
        raise ValueError("Ollama's generation context differs from the rendered training input")

    texts = [render(row) + "Safety:" for row in train + validation]
    # Sample within each label because the TSV interleaves safe and unsafe replies.
    # These positions anchor the original logits; they do not provide category labels.
    for label, words in (("1", ("Safe",)), ("0", ("Unsafe", "Controversial"))):
        examples = [row for row in train if row["is_safe"] == label]
        for row in examples[::12]:
            text = render(row)
            texts.extend((text, text + "Safety"))
            for word in words:
                answer = text + "Safety: " + word
                texts.extend((answer, answer + "\nCategories:"))
            if label == "1":
                texts.append(text + "Safety: Safe\nCategories: None")
            else:
                texts.append(text + "Safety: Cont")
    vectors = []
    with ThreadPoolExecutor(max_workers=4) as pool:
        for i, vector in enumerate(pool.map(embed, texts), 1):
            vectors.append(vector)
            if i % 500 == 0:
                print(f"Encoded {i}/{len(texts)} examples and format anchors", flush=True)
    return ids, np.stack(vectors)


def fit(weights, vectors, train, validation, penalties=(0.4, 0.04, 0.004)):
    n, end = len(train), len(train) + len(validation)
    labels = np.array([1 if row["is_safe"] == "1" else -1 for row in train + validation])
    scale = np.sqrt(vectors[:n].std(axis=0).clip(0.08))
    features = vectors[:n] / scale * labels[:n, None]
    anchors = vectors[end:] / scale
    logits = vectors[:n] @ weights.T
    offset = (logits[:, 0] - logits[:, 1:].max(axis=1)) * labels[:n]
    best = None
    for penalty in penalties:
        def objective(w):
            margin = offset + features @ w
            drift = anchors @ w
            loss = np.logaddexp(0, -margin).mean() + penalty / 2 * (w @ w) + 0.002 * np.mean(drift ** 2)
            grad = -features.T @ expit(-margin) / n + penalty * w + 0.004 * anchors.T @ drift / len(drift)
            return loss, grad

        result = minimize(objective, np.zeros(weights.shape[1]), jac=True, method="L-BFGS-B",
                          options={"maxiter": 350})
        if not np.isfinite(result.fun) or not np.isfinite(result.x).all():
            raise ValueError("Non-finite output from optimizer")
        # The same update to both flagged logits preserves their relative odds before rounding.
        update = np.array([0.5, -0.5, -0.5])[:, None] * result.x / scale
        packed = q6_rows(weights + update)
        logits_val = vectors[n:end] @ dequantize(packed, GGMLQuantizationType.Q6_K).T
        margin = (logits_val[:, 0] - logits_val[:, 1:].max(axis=1)) * labels[n:]
        key = (int((margin > 0).sum()), -np.logaddexp(0, -margin).mean())
        print(f"Penalty {penalty}: {key[0]}/{len(validation)} validation verdicts by logit")
        if best is None or key > best[0]:
            best = key, packed
    return best[1]


def tune(data, out, executable):
    if out.exists():
        raise FileExistsError(f"Choose a new output directory: {out}")
    cases = load_cases(data)
    train = [r for s, r in cases if s == "train"]
    validation = [r for s, r in cases if s == "validation"]
    if not validation or {r["is_safe"] for r in train} != {"0", "1"}:
        raise ValueError("Tuning needs both training labels and a nonempty validation set")
    print(f"Train {len(train)}, validation {len(validation)}, held out {len(cases)-len(train)-len(validation)}",
          flush=True)

    modelfile = ollama("/api/show", {"model": BASE})["modelfile"]
    source = re.search(r"^FROM[ \t]+([^\r\n]+)", modelfile, re.M)
    template = re.search(r'^TEMPLATE[ \t]+(?P<quote>"""|")(?P<text>.*?)(?P=quote)[ \t]*\r?$', modelfile, re.M | re.S)
    if not source or not template:
        raise ValueError("Expected a local GGUF path and a quoted TEMPLATE in Ollama's Modelfile")
    model = Path(source[1].strip().strip('"'))
    template = template["text"].replace("\r\n", "\n")
    if re.findall(r"{{.*?}}", template) != ["{{ .Prompt }}"]:
        raise ValueError("Expected the Sileader single-prompt template")
    reader = GGUFReader(model)
    head = next((t for t in reader.tensors if t.name == "output.weight"), None)
    if head is None or head.tensor_type != GGMLQuantizationType.Q6_K:
        raise ValueError("This recipe requires Qwen3Guard's separate Q6_K output.weight")

    with embedding_server(executable, model) as request:
        ids, vectors = collect(request, template, train, validation)
    packed = fit(dequantize(head.data[ids], head.tensor_type), vectors, train, validation)
    stride = head.data.strides[0]
    if packed.shape != (3, stride):
        raise ValueError("Encoded verdict rows have the wrong size")
    out.mkdir()
    with tempfile.TemporaryDirectory(dir=out) as tmp:
        copy = Path(tmp, "candidate.gguf")
        shutil.copyfile(model, copy)
        with copy.open("r+b") as dest:
            for token, weight_row in zip(ids, packed):
                dest.seek(int(head.data_offset) + token * stride)
                dest.write(weight_row.tobytes())
        copy.rename(out / "candidate.gguf")
    definition = modelfile[:source.start(1)] + "./candidate.gguf" + modelfile[source.end(1):]
    (out / "Modelfile").write_bytes(definition.encode())
    print(f"Candidate ready in {out}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=Path("data.tsv"))
    parser.add_argument("--out-dir", required=True, type=Path, help="New candidate directory")
    bundled = Path("/Applications/Ollama.app/Contents/Resources/llama-server")
    parser.add_argument("--llama-server", default=shutil.which("llama-server") or (str(bundled) if bundled.is_file() else "llama-server"),
                        help="Path to the llama.cpp server executable")
    args = parser.parse_args()
    tune(args.data, args.out_dir, args.llama_server)
