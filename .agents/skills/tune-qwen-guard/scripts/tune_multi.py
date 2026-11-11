"""Fit Qwen3Guard's three verdict-token weights to each conversation's consensus rating and export a candidate."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import re
import shutil
import tempfile

from gguf import GGUFReader, GGMLQuantizationType, dequantize
import numpy as np
from scipy.optimize import minimize
from scipy.special import log_softmax, softmax

from benchmark_multi import TARGET, load_cases, prompt
from tune import BASE, VERDICTS, embedding_server, ollama, q6_rows

CLASSES = ("safe", "unsafe", "controversial")  # the order of VERDICTS
PENALTIES = (0.4, 0.04, 0.004, 0.0004)
DRIFTS = (0.002, 0.02, 0.2)
CATEGORIES = ("Violent", "Non-violent Illegal Acts", "Sexual Content or Sexual Acts", "PII", "Suicide & Self-Harm",
              "Unethical Acts", "Politically Sensitive Topics", "Copyright Violation", "Jailbreak")


def category_anchors(tokenize, render, anchor_rows):
    """Token lists ending inside or after a category name, where a verdict word must not displace the next token."""
    names = [tokenize(" " + name) for name in CATEGORIES]
    inside = [name[:k] for name in names for k in range(1, len(name) + 1)]
    flagged = [row for row in anchor_rows if row["consensus_rating"] != "SAFE"]
    anchors = []
    for i, row in enumerate(flagged):
        word = VERDICTS[CLASSES.index(TARGET[row["consensus_rating"]])].strip()
        opening = tokenize(render(row) + "Safety: " + word + "\nCategories:")
        anchors.extend(opening + inside[(6 * i + j) % len(inside)] for j in range(6))
    return anchors


def collect(request, template, rows, anchor_rows):
    def tokenize(text):
        return request("/tokenize", {"content": text, "add_special": False, "parse_special": True})["tokens"]

    def embed(text):
        tokens = text if isinstance(text, list) else tokenize(text)
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
    expected = tokenize(render(rows[0]))
    probe = ollama("/api/generate", {"model": BASE, "prompt": prompt(rows[0]), "stream": False,
                                    "options": {"num_predict": 1}})
    if probe.get("eval_count") != 1 or probe.get("context", [])[:-1] != expected:
        raise ValueError("Ollama's generation context differs from the rendered training input")

    texts = [render(row) + "Safety:" for row in rows]
    # Positions where the reply's other tokens are chosen. They anchor the original logits there.
    for row in anchor_rows:
        text = render(row)
        word = VERDICTS[CLASSES.index(TARGET[row["consensus_rating"]])].strip()
        answer = text + "Safety: " + word
        texts.extend((text, text + "Safety", answer, answer + "\nCategories:"))
        texts.append(answer + "\nCategories: None" if word == "Safe" else text + "Safety: Cont")
    texts.extend(category_anchors(tokenize, render, anchor_rows))
    vectors = []
    with ThreadPoolExecutor(max_workers=4) as pool:
        for i, vector in enumerate(pool.map(embed, texts), 1):
            vectors.append(vector)
            if i % 500 == 0:
                print(f"Encoded {i}/{len(texts)} examples and format anchors", flush=True)
    return np.array(ids), np.stack(vectors)


def source_choices(head, ids, vectors):
    """Per position: the token the source weights pick, and the best token and logit outside the verdict rows."""
    full = dequantize(head.data, head.tensor_type).astype(np.float32)
    picked, other, other_logit = [], [], []
    for start in range(0, len(vectors), 512):
        logits = vectors[start:start + 512].astype(np.float32) @ full.T
        picked.append(logits.argmax(axis=1))
        logits[:, ids] = -np.inf
        other.append(logits.argmax(axis=1))
        other_logit.append(logits.max(axis=1))
    return np.concatenate(picked), np.concatenate(other), np.concatenate(other_logit)


def choices(ids, rows, vectors, other, other_logit):
    """The token the whole vocabulary picks at each position once the verdict rows are replaced."""
    logits = vectors @ rows.T
    return np.where(logits.max(axis=1) > other_logit, ids[logits.argmax(axis=1)], other)


def fit(ids, weights, train, y_train, validation, y_validation, anchors, source_validation, source_anchors):
    """Softmax regression on the hidden state after `Safety:`, starting from the model's own logits."""
    n, width = train.shape
    scale = np.sqrt(train.std(axis=0).clip(0.08))
    features, drift_features = train / scale, anchors / scale
    base = train @ weights.T
    onehot = np.eye(3)[y_train]
    report, best = [], None
    for penalty in PENALTIES:
        for drift_weight in DRIFTS:
            def objective(flat):
                update = flat.reshape(3, width)
                logits = base + features @ update.T
                drift = drift_features @ update.T
                loss = (-(log_softmax(logits, axis=1) * onehot).sum(axis=1).mean() + penalty / 2 * (flat @ flat)
                        + drift_weight * (drift ** 2).sum() / len(drift))
                grad = ((softmax(logits, axis=1) - onehot).T @ features / n + penalty * update
                        + 2 * drift_weight * drift.T @ drift_features / len(drift))
                return loss, grad.ravel()

            result = minimize(objective, np.zeros(3 * width), jac=True, method="L-BFGS-B", options={"maxiter": 500})
            if not np.isfinite(result.fun) or not np.isfinite(result.x).all():
                raise ValueError("Non-finite output from optimizer")
            packed = q6_rows(weights + result.x.reshape(3, width) / scale)
            rounded = dequantize(packed, GGMLQuantizationType.Q6_K).astype(np.float64)
            logits = validation @ rounded.T
            hits = int((logits.argmax(axis=1) == y_validation).sum())
            loss = float(-log_softmax(logits, axis=1)[np.arange(len(y_validation)), y_validation].mean())
            # Format damage: a reply that would not open with a verdict, or another token of it that changes.
            stray = int((~np.isin(choices(ids, rounded, validation, *source_validation[1:]), ids)).sum())
            changed = int((choices(ids, rounded, anchors, *source_anchors[1:]) != source_anchors[0]).sum())
            report.append({"penalty": penalty, "drift_weight": drift_weight, "validation_exact": hits,
                           "validation_loss": round(loss, 4),
                           "train_exact": int(((train @ rounded.T).argmax(axis=1) == y_train).sum()),
                           "validation_first_token_not_a_verdict": stray, "anchor_tokens_changed": changed})
            print(f"Penalty {penalty}, drift weight {drift_weight}: {hits}/{len(y_validation)} validation verdicts "
                  f"by logit, loss {loss:.4f}, {changed}/{len(anchors)} anchor tokens changed", flush=True)
            # Keep the reply's format first, then pick the most accurate verdicts.
            key = (-(stray + changed), hits, -loss)
            if best is None or key > best[0]:
                best = key, report[-1], packed, rounded
    return best[1], best[2], best[3], report


def tune(data, split_file, out, name, executable, features):
    if out.exists():
        raise FileExistsError(f"Choose a new output directory: {out}")
    cases = load_cases(data, split_file)
    train = [r for s, r in cases if s == "train"]
    validation = [r for s, r in cases if s == "validation"]
    labels = np.array([CLASSES.index(TARGET[r["consensus_rating"]]) for r in train + validation])
    if not validation or set(labels[:len(train)]) != {0, 1, 2}:
        raise ValueError("Tuning needs all three training labels and a nonempty validation set")
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

    order = [r["request_id"] for r in train + validation]
    anchor_rows = train[::12]
    if features and features.exists():
        saved = np.load(features)
        ids, vectors = saved["ids"], saved["vectors"]
        flagged = sum(row["consensus_rating"] != "SAFE" for row in anchor_rows)
        if list(saved["request_ids"]) != order or len(vectors) != len(order) + 5 * len(anchor_rows) + 6 * flagged:
            raise ValueError(f"{features} was encoded for a different split or anchor set")
    else:
        with embedding_server(executable, model) as request:
            ids, vectors = collect(request, template, train + validation, anchor_rows)
        if features:
            np.savez(features, ids=ids, vectors=vectors, request_ids=np.array(order))
    n, end = len(train), len(train) + len(validation)
    weights = dequantize(head.data[ids], head.tensor_type).astype(np.float64)
    before = int(((vectors[n:end] @ weights.T).argmax(axis=1) == labels[n:]).sum())
    print(f"Source weights: {before}/{len(validation)} validation verdicts by logit", flush=True)
    source_validation = source_choices(head, ids, vectors[n:end])
    source_anchors = source_choices(head, ids, vectors[end:])
    chosen, packed, rounded, report = fit(ids, weights, vectors[:n], labels[:n], vectors[n:end], labels[n:],
                                          vectors[end:], source_validation, source_anchors)
    stride = head.data.strides[0]
    if packed.shape != (3, stride):
        raise ValueError("Encoded verdict rows have the wrong size")
    print(f"Selected {chosen}", flush=True)
    out.mkdir()
    with tempfile.TemporaryDirectory(dir=out) as tmp:
        copy = Path(tmp, "candidate.gguf")
        shutil.copyfile(model, copy)
        with copy.open("r+b") as dest:
            for token, weight_row in zip(ids, packed):
                dest.seek(int(head.data_offset) + int(token) * stride)
                dest.write(weight_row.tobytes())
        copy.rename(out / f"{name}.gguf")
    definition = modelfile[:source.start(1)] + f"./{name}.gguf" + modelfile[source.end(1):]
    (out / "Modelfile").write_bytes(definition.encode())
    predicted = (vectors[n:end] @ rounded.T).argmax(axis=1)
    summary = {"train": n, "validation": len(validation), "source_validation_exact": before,
               "anchor_positions": len(vectors) - end, "selected": chosen, "fits": report,
               "validation_target_to_verdict": {f"{CLASSES[t]}->{CLASSES[p]}": int(((labels[n:] == t) & (predicted == p)).sum())
                                                for t in range(3) for p in range(3)}}
    (out / "fit.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(f"Candidate ready in {out}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=Path("data-multi.tsv"))
    parser.add_argument("--split-file", type=Path, default=Path("data-multi-split.tsv"))
    parser.add_argument("--out-dir", required=True, type=Path, help="New candidate directory")
    parser.add_argument("--name", default="candidate", help="File name of the exported GGUF, without .gguf")
    parser.add_argument("--features", type=Path, help="Reuse or save the encoded hidden states (.npz)")
    bundled = Path("/Applications/Ollama.app/Contents/Resources/llama-server")
    parser.add_argument("--llama-server", default=shutil.which("llama-server") or (str(bundled) if bundled.is_file() else "llama-server"),
                        help="Path to the llama.cpp server executable")
    args = parser.parse_args()
    tune(args.data, args.split_file, args.out_dir, args.name, args.llama_server, args.features)
