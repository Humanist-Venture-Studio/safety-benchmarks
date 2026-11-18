"""Headless HF/GGUF tokenizer and HF/Ollama verdict-margin probe for fitted adapters."""

import argparse
import ast
import json
import subprocess
from pathlib import Path

import torch
from backends import CHAT_PROMPT, ollama_score, request_json
from common import read_tsv, require
from peft import PeftModel
from train_chat import load_base, prompt
from training import transcript
from transformers import AutoTokenizer


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--run", required=True, type=Path)
    p.add_argument("--tag", required=True)
    p.add_argument("--data", required=True, type=Path)
    p.add_argument("--endpoint", default="http://127.0.0.1:18282")
    p.add_argument(
        "--max-margin-delta",
        type=float,
        default=1.5,
        help="absolute unsafe-minus-safe logit difference",
    )
    a = p.parse_args()
    require(a.tag.startswith("klara/cand-"), "expected task candidate")
    recipe = json.loads((a.run / "chat.json").read_text())
    tok = AutoTokenizer.from_pretrained(recipe["source"])
    model = load_base(recipe["source"])
    if recipe["init_adapter"]:
        model = PeftModel.from_pretrained(
            model, recipe["init_adapter"]
        ).merge_and_unload()
    model = (
        PeftModel.from_pretrained(model, a.run / "adapter")
        .merge_and_unload()
        .to("mps")
        .eval()
    )
    sizes = set()
    for row in read_tsv(a.data):
        if row["turns"] in sizes:
            continue
        sizes.add(row["turns"])
        text = transcript(row)
        rendered = prompt(text)
        ids = tok.encode(rendered)
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
            ast.literal_eval(run.stdout.strip()) == ids,
            "HF and GGUF prompt token IDs differ",
        )
        with torch.no_grad():
            logits = (
                model(input_ids=torch.tensor([ids], device="mps"), logits_to_keep=1)
                .logits[0, -1]
                .float()
            )
            hf = (logits[recipe["ids"][1]] - logits[recipe["ids"][0]]).item()
        payload = {
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
        }
        reply = request_json(a.endpoint + "/api/chat", 120, payload)
        probability, raw = ollama_score(reply, recipe["tokens"])
        require(
            reply["prompt_eval_count"] == len(ids), "Ollama prompt token count differs"
        )
        pair = json.loads(raw)["logprobs"]
        served = pair["unsafe"] - pair["safe"]
        print(
            json.dumps(
                {
                    "turns": row["turns"],
                    "ids": len(ids),
                    "hf_margin": hf,
                    "ollama_margin": served,
                    "unsafe_probability": probability,
                    "delta": abs(hf - served),
                }
            ),
            flush=True,
        )
        require(
            abs(hf - served) <= a.max_margin_delta,
            "quantization margin delta exceeds tolerance",
        )
    require(sizes, "no probe rows")


if __name__ == "__main__":
    main()
