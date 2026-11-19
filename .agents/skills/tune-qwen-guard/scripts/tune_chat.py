"""Fit Qwen3Guard's three verdict-token weights on one-turn and four-turn chats together and export a candidate."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import csv
import hashlib
import json
from pathlib import Path
import re
import shutil
import tempfile

from gguf import GGUFReader, GGMLQuantizationType, dequantize
import numpy as np
from scipy.optimize import minimize
from scipy.special import log_softmax, softmax

from benchmark_chat import VERDICTS, accepted, label, load_cases, prompt
from tune import BASE, embedding_server, ollama, q6_rows
from tune import VERDICTS as WORDS  # " Safe", " Unsafe", " Controversial": the same order as VERDICTS
from tune_multi import CATEGORIES, choices, source_choices

PENALTIES = (0.4, 0.04, 0.004, 0.0004)
DRIFTS = (0.002, 0.02, 0.2)
MIXES = (0.3, 0.5, 0.7)  # share of the loss given to the single-turn rows; each source is averaged over its rows


def anchor_word(row, i):
    """The verdict a row's format anchors are written with. A flagged single-turn row has no three-way label."""
    want = accepted(row)
    return WORDS[VERDICTS.index(want[i % len(want)])].strip()


def texts_for(tokenize, template, rows, anchor_rows):
    """Everything to encode: each row up to `Safety:`, then positions where the reply's other tokens are chosen."""
    def render(row):
        return template.replace("{{ .Prompt }}", prompt(row))

    texts = [render(row) + "Safety:" for row in rows]
    names = [tokenize(" " + name) for name in CATEGORIES]
    inside = [name[:k] for name in names for k in range(1, len(name) + 1)]
    flagged = 0
    for i, row in enumerate(anchor_rows):
        text, word = render(row), anchor_word(row, i)
        answer = text + "Safety: " + word
        texts.extend((text, text + "Safety", answer, answer + "\nCategories:"))
        texts.append(answer + "\nCategories: None" if word == "Safe" else text + "Safety: Cont")
        if word != "Safe":  # inside a category name a verdict word must not displace the next token
            opening = tokenize(answer + "\nCategories:")
            texts.extend(opening + inside[(6 * flagged + j) % len(inside)] for j in range(6))
            flagged += 1
    return texts


def encode(request, tokenize, texts, cache_file, model):
    """Final hidden state of each text (a string or a token list), reusing vectors saved for the same GGUF."""
    keys = [hashlib.sha1(json.dumps(t).encode()).hexdigest() for t in texts]
    cache = {}
    if cache_file and cache_file.exists():
        saved = np.load(cache_file)
        if "model" in saved and str(saved["model"]) != str(model):
            raise ValueError(f"{cache_file} holds hidden states of another GGUF")
        cache = dict(zip(saved["keys"].tolist(), saved["vectors"]))
    missing = [(k, t) for k, t in dict(zip(keys, texts)).items() if k not in cache]

    def embed(item):
        tokens = item[1] if isinstance(item[1], list) else tokenize(item[1])
        if len(tokens) > 2048:
            raise ValueError("Example exceeds the configured 2,048-token slot")
        vector = request("/embedding", {"content": tokens, "embd_normalize": -1})[0]["embedding"]
        return np.asarray(vector, dtype=np.float32).reshape(-1)

    with ThreadPoolExecutor(max_workers=4) as pool:
        for i, (item, vector) in enumerate(zip(missing, pool.map(embed, missing)), 1):
            cache[item[0]] = vector
            if i % 1000 == 0:
                print(f"Encoded {i}/{len(missing)} new positions", flush=True)
    if cache_file and missing:
        np.savez(cache_file, keys=np.array(list(cache)), vectors=np.stack(list(cache.values())), model=str(model))
    return np.stack([cache[k] for k in keys]).astype(np.float64)


def scores(logits, rows):
    """Verdicts by logit for one source's rows: exact (three-way where it exists) and Safe against not Safe."""
    picked = logits.argmax(axis=1)
    safe = np.array([accepted(r) == ("safe",) for r in rows])
    exact = int(sum(VERDICTS[p] in accepted(r) for p, r in zip(picked, rows)))
    called_safe = picked == 0
    recall_safe, recall_flag = (called_safe & safe).sum() / safe.sum(), (~called_safe & ~safe).sum() / (~safe).sum()
    out = {"rows": len(rows), "exact": exact, "safe_vs_not": int((called_safe == safe).sum()),
           "balanced_safe_vs_not": round(float((recall_safe + recall_flag) / 2), 4),
           "not_safe_called_safe": int((called_safe & ~safe).sum()), "not_safe_rows": int((~safe).sum()),
           "safe_flagged": int((~called_safe & safe).sum()), "safe_rows": int(safe.sum())}
    unsafe = np.array([label(r) == "UNSAFE" for r in rows])
    if unsafe.any():
        out.update(unsafe_called_safe=int((called_safe & unsafe).sum()), unsafe_rows=int(unsafe.sum()))
    return out


def fit(ids, weights, train, masks, source_weight, validation, anchors, source_validation, source_anchors):
    """Softmax regression on the hidden state after `Safety:`, starting from the model's own logits.

    masks marks each row's accepted verdicts: one for a three-way label, Unsafe and Controversial together for a
    flagged single-turn row, whose loss is the summed probability of the two.
    """
    width = train.shape[1]
    scale = np.sqrt(train.std(axis=0).clip(0.08))
    features, drift_features = train / scale, anchors / scale
    base = train @ weights.T
    all_validation = np.concatenate([vectors for vectors, _ in validation.values()])
    report, best = [], None
    for mix in MIXES:
        row_weight = np.where(source_weight, mix / source_weight.sum(), (1 - mix) / (~source_weight).sum())
        for penalty in PENALTIES:
            for drift_weight in DRIFTS:
                def objective(flat):
                    update = flat.reshape(3, width)
                    logits = base + features @ update.T
                    drift = drift_features @ update.T
                    p = softmax(logits, axis=1)
                    hit = (p * masks).sum(axis=1)
                    loss = (-(row_weight * np.log(hit.clip(1e-300))).sum() + penalty / 2 * (flat @ flat)
                            + drift_weight * (drift ** 2).sum() / len(drift))
                    grad = (((p - p * masks / hit[:, None]) * row_weight[:, None]).T @ features + penalty * update
                            + 2 * drift_weight * drift.T @ drift_features / len(drift))
                    return loss, grad.ravel()

                result = minimize(objective, np.zeros(3 * width), jac=True, method="L-BFGS-B",
                                  options={"maxiter": 500})
                if not np.isfinite(result.fun) or not np.isfinite(result.x).all():
                    raise ValueError("Non-finite output from optimizer")
                packed = q6_rows(weights + result.x.reshape(3, width) / scale)
                rounded = dequantize(packed, GGMLQuantizationType.Q6_K).astype(np.float64)
                by_source = {name: scores(vectors @ rounded.T, rows) for name, (vectors, rows) in validation.items()}
                # Format damage: a reply that would not open with a verdict, or another token of it that changes.
                stray = int((~np.isin(choices(ids, rounded, all_validation, *source_validation[1:]), ids)).sum())
                changed = int((choices(ids, rounded, anchors, *source_anchors[1:]) != source_anchors[0]).sum())
                balance = float(np.mean([s["balanced_safe_vs_not"] for s in by_source.values()]))
                loss = float(np.mean([-np.log((softmax(vectors @ rounded.T, axis=1)
                                               * np.array([[v in accepted(r) for v in VERDICTS] for r in rows])
                                               ).sum(axis=1).clip(1e-300)).mean()
                                      for vectors, rows in validation.values()]))
                report.append({"single_share": mix, "penalty": penalty, "drift_weight": drift_weight,
                               "validation_balanced_safe_vs_not": round(balance, 4), "validation": by_source,
                               "validation_loss": round(loss, 4), "validation_first_token_not_a_verdict": stray,
                               "anchor_tokens_changed": changed})
                print(f"Single share {mix}, penalty {penalty}, drift {drift_weight}: balanced {balance:.4f} "
                      + ", ".join(f"{name} {s['exact']}/{s['rows']}" for name, s in by_source.items())
                      + f", {changed}/{len(anchors)} anchor tokens changed, {stray} stray", flush=True)
                # Keep the reply's format first, then the two sources' mean balanced Safe-vs-not accuracy.
                key = (-(stray + changed), round(balance, 4), by_source["multi"]["exact"], -loss)
                if best is None or key > best[0]:
                    best = key, report[-1], packed, rounded
    return best[1], best[2], best[3], report


def tune(single, multi, split_file, out, name, executable, features, template_file, gguf):
    if out.exists():
        raise FileExistsError(f"Choose a new output directory: {out}")
    cases = {"single": load_cases("single", single), "multi": load_cases("multi", multi, split_file)}
    train = [r for source in cases.values() for s, r in source if s == "train"]
    held = {name_: [r for s, r in source if s == "validation"] for name_, source in cases.items()}
    is_single = np.array(["request" in r for r in train])
    masks = np.array([[v in accepted(r) for v in VERDICTS] for r in train], dtype=np.float64)
    if not all(held.values()) or not is_single.any() or is_single.all() or not masks[~is_single].any(axis=0).all():
        raise ValueError("Tuning needs both sources, all three multi-turn labels and nonempty validation sets")
    print(f"Train {int(is_single.sum())} single-turn + {int((~is_single).sum())} multi-turn, validation "
          + " + ".join(f"{len(rows)} {name_}" for name_, rows in held.items()), flush=True)

    modelfile = ollama("/api/show", {"model": BASE})["modelfile"]
    source = re.search(r"^FROM[ \t]+([^\r\n]+)", modelfile, re.M)
    quoted = re.search(r'^TEMPLATE[ \t]+(?P<quote>"""|")(?P<text>.*?)(?P=quote)[ \t]*\r?$', modelfile, re.M | re.S)
    if not source or not quoted:
        raise ValueError("Expected a local GGUF path and a quoted TEMPLATE in Ollama's Modelfile")
    model = gguf or Path(source[1].strip().strip('"'))
    template = (template_file.read_text(encoding="utf-8") if template_file else quoted["text"]).replace("\r\n", "\n")
    if re.findall(r"{{.*?}}", template) != ["{{ .Prompt }}"] or '"' in template:
        raise ValueError("Expected a single-prompt template without double quotes")
    reader = GGUFReader(model)
    head = next((t for t in reader.tensors if t.name == "output.weight"), None)
    if head is None or head.tensor_type != GGMLQuantizationType.Q6_K:
        raise ValueError("This recipe requires Qwen3Guard's separate Q6_K output.weight")

    rows = train + held["single"] + held["multi"]
    anchor_rows = train[::12]
    with embedding_server(executable, model) as request:
        def tokenize(text):
            return request("/tokenize", {"content": text, "add_special": False, "parse_special": True})["tokens"]

        words = [tokenize(v) for v in WORDS]
        ids = np.array([word[0] for word in words])
        if len(words[0]) != 1 or len(words[1]) != 1 or len(set(ids)) != 3:
            raise ValueError("Unexpected verdict tokenization for this checkpoint")
        # Compare a one-turn and a four-turn prompt token-for-token with the actual Ollama generation context.
        for row in (train[np.flatnonzero(is_single)[0]], train[np.flatnonzero(~is_single)[0]]):
            payload = {"model": BASE, "prompt": prompt(row), "stream": False, "options": {"num_predict": 1}}
            probe = ollama("/api/generate", payload | ({"template": template} if template_file else {}))
            expected = tokenize(template.replace("{{ .Prompt }}", prompt(row)))
            if probe.get("eval_count") != 1 or probe.get("context", [])[:-1] != expected:
                raise ValueError("Ollama's generation context differs from the rendered training input")
        vectors = encode(request, tokenize, texts_for(tokenize, template, rows, anchor_rows), features, model)

    n, a, end = len(train), len(train) + len(held["single"]), len(rows)
    validation = {"single": (vectors[n:a], held["single"]), "multi": (vectors[a:end], held["multi"])}
    weights = dequantize(head.data[ids], head.tensor_type).astype(np.float64)
    before = {name_: scores(v @ weights.T, r) for name_, (v, r) in validation.items()}
    print(f"Source weights by logit: {before}", flush=True)
    source_validation = source_choices(head, ids, vectors[n:end])
    source_anchors = source_choices(head, ids, vectors[end:])
    chosen, packed, rounded, report = fit(ids, weights, vectors[:n], masks, is_single, validation, vectors[end:],
                                          source_validation, source_anchors)
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
    # Sileader's Modelfile with the new weights, the template used for the fit and greedy decoding built in.
    definition = (modelfile[:source.start(1)] + f"./{name}.gguf" + modelfile[source.end(1):quoted.start("text")]
                  + template + modelfile[quoted.end("text"):].rstrip("\n") + "\nPARAMETER temperature 0\n")
    (out / "Modelfile").write_bytes(definition.encode())
    with (out / "validation.tsv").open("w", encoding="utf-8", newline="") as target:
        writer = csv.writer(target, delimiter="\t", lineterminator="\n")
        writer.writerow(("request_id", "source", "label", "source_verdict_by_logit", "verdict_by_logit"))
        for name_, (v, held_rows) in validation.items():
            for row, old, new in zip(held_rows, (v @ weights.T).argmax(axis=1), (v @ rounded.T).argmax(axis=1)):
                writer.writerow((row["request_id"], name_, label(row), VERDICTS[old], VERDICTS[new]))
    summary = {"train_single": int(is_single.sum()), "train_multi": int((~is_single).sum()),
               "source_validation": before, "anchor_positions": len(vectors) - end, "selected": chosen, "fits": report}
    (out / "fit.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(f"Candidate ready in {out}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--single", type=Path, default=Path("data.tsv"))
    parser.add_argument("--multi", type=Path, default=Path("data-multi.tsv"))
    parser.add_argument("--split-file", type=Path, default=Path("data-multi-template-split.tsv"))
    parser.add_argument("--out-dir", required=True, type=Path, help="New candidate directory")
    parser.add_argument("--name", default="candidate", help="File name of the exported GGUF, without .gguf")
    parser.add_argument("--features", type=Path, help="Reuse or save the encoded hidden states (.npz)")
    parser.add_argument("--template-file", type=Path,
                        help="Fit and export with this prompt template instead of Sileader's (must hold {{ .Prompt }})")
    parser.add_argument("--gguf", type=Path,
                        help="Fit the verdict rows of this GGUF instead of the installed base, for example one "
                             "written by tune_chat_lowrank.py")
    bundled = Path("/Applications/Ollama.app/Contents/Resources/llama-server")
    parser.add_argument("--llama-server", default=shutil.which("llama-server") or (str(bundled) if bundled.is_file() else "llama-server"),
                        help="Path to the llama.cpp server executable")
    args = parser.parse_args()
    tune(args.single, args.multi, args.split_file, args.out_dir, args.name, args.llama_server, args.features,
         args.template_file, args.gguf)
