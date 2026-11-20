"""Compare HF token IDs and verdict margins with the separately served GGUF."""

import argparse
import ast
import hashlib
import json
import subprocess
from pathlib import Path

from backends import CHAT_PROMPT, chat_prompt, ollama_score, request_json
from common import atomic_text, read_tsv, require


def probe_inputs(path):
    from training import transcript

    samples = {}
    for row in read_tsv(path):
        if row["turns"] not in samples:
            samples[row["turns"]] = transcript(row)
    require(samples, "no probe rows")
    return samples


def reference_key(recipe, samples, run):
    # Include actual inputs as well as recipe. Prevent comparison with another fixture or adapter.
    adapters = [run / "adapter"]
    if recipe.get("init_adapter"):
        adapters.append(Path(recipe["init_adapter"]))
    digests = []
    for adapter in adapters:
        for name in ("adapter_config.json", "adapter_model.safetensors"):
            with (adapter / name).open("rb") as f:
                digests.append(hashlib.file_digest(f, "sha256").hexdigest())
    blob = json.dumps(
        [recipe, samples, chat_prompt(""), digests], sort_keys=True, ensure_ascii=False
    )
    return hashlib.sha256(blob.encode()).hexdigest()


def hf_reference(run, recipe, samples):
    import torch
    from peft import PeftModel
    from transformers import AutoTokenizer
    from train_chat import load_base

    tok = AutoTokenizer.from_pretrained(recipe["source"], local_files_only=True)
    if (run / "merged-for-conversion").is_dir():
        model = load_base(run / "merged-for-conversion")
    else:
        model = load_base(recipe["source"])
        if recipe["init_adapter"]:
            model = PeftModel.from_pretrained(
                model, recipe["init_adapter"]
            ).merge_and_unload()
        if recipe.get("fp16"):
            model.half()
        model = PeftModel.from_pretrained(model, run / "adapter").merge_and_unload()
    model.to("mps").eval()
    refs = {}
    with torch.inference_mode():
        for turns, text in samples.items():
            ids = tok.encode(chat_prompt(text))
            logits = (
                model(input_ids=torch.tensor([ids], device="mps"), logits_to_keep=1)
                .logits[0, -1]
                .float()
            )
            margin = (logits[recipe["ids"][1]] - logits[recipe["ids"][0]]).item()
            refs[turns] = {"ids": ids, "margin": margin}
    return refs


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--run", required=True, type=Path)
    p.add_argument("--tag", required=True)
    p.add_argument("--data", required=True, type=Path)
    p.add_argument("--endpoint", default="http://127.0.0.1:18282")
    p.add_argument("--max-margin-delta", type=float, default=1.5)
    stage = p.add_mutually_exclusive_group()
    stage.add_argument(
        "--save-reference",
        type=Path,
        help="capture HF results before releasing source disk/RAM",
    )
    stage.add_argument(
        "--reference",
        type=Path,
        help="use previously captured HF results for this exact fit",
    )
    a = p.parse_args()
    require(a.tag.startswith("klara/cand-"), "expected task candidate")
    recipe = json.loads((a.run / "chat.json").read_text())
    samples = probe_inputs(a.data)
    key = reference_key(recipe, samples, a.run)
    if a.reference:
        report = json.loads(a.reference.read_text())
        require(
            report["key"] == key, "HF reference differs from recipe, adapter or inputs"
        )
        refs = report["rows"]
    else:
        refs = hf_reference(a.run, recipe, samples)
        if a.save_reference:
            with atomic_text(a.save_reference, replace=False) as out:
                json.dump({"key": key, "rows": refs}, out, allow_nan=False)
            print(f"Saved {len(refs)} HF comparisons")
            return
    for turns, text in samples.items():
        rendered = chat_prompt(text)
        ref = refs[turns]
        run = subprocess.run(
            [
                "llama-tokenize",
                "--offline",
                "--ids",
                "--stdin",
                "--no-escape",
                "-m",
                str(a.run / "candidate.gguf"),
            ],
            input=rendered,
            text=True,
            capture_output=True,
            check=True,
        )
        require(
            ast.literal_eval(run.stdout.strip()) == ref["ids"],
            "HF and GGUF prompt token IDs differ",
        )
        reply = request_json(
            a.endpoint + "/api/chat",
            120,
            {
                "model": a.tag,
                "messages": [
                    {"role": "system", "content": CHAT_PROMPT},
                    {"role": "user", "content": text},
                ],
                "stream": False,
                "think": False,
                "logprobs": True,
                "top_logprobs": 20,
                "options": {"temperature": 0},
            },
        )
        evidence = compare_verdict(ref, recipe["tokens"], reply, a.max_margin_delta)
        print(json.dumps({"turns": turns, **evidence}), flush=True)


def compare_verdict(ref, tokens, reply, tolerance):
    probability, raw = ollama_score(reply, tokens)
    require(
        reply["prompt_eval_count"] == len(ref["ids"]),
        "Ollama prompt token count differs",
    )
    pair = json.loads(raw)["logprobs"]
    served = pair["unsafe"] - pair["safe"]
    delta = abs(ref["margin"] - served)
    require(
        delta <= tolerance, f"quantization margin delta {delta:.4f} exceeds {tolerance}"
    )
    return {
        "ids": len(ref["ids"]),
        "hf_margin": ref["margin"],
        "ollama_margin": served,
        "unsafe_probability": probability,
        "delta": delta,
    }


if __name__ == "__main__":
    main()
