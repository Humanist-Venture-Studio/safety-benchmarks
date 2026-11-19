"""Merge the candidate, convert to GGUF, check size and create a fresh task-only tag."""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import uuid
from pathlib import Path

from backends import CHAT_PROMPT, request_json
from common import WORK, require
from training import MODELS

TEMPLATE = '{{range .Messages}}{{if eq .Role "system"}}System: {{.Content}}\n{{else if eq .Role "user"}}User: {{.Content}}\n{{end}}{{end}}Assistant:'
# Current Ollama uses the GGUF's embedded Jinja template ahead of the Modelfile.
JINJA = (
    '{% for message in messages %}{% if message.role == "system" %}System: {{ message.content }}\n'
    '{% elif message.role == "user" %}User: {{ message.content }}\n{% endif %}{% endfor %}Assistant:'
)
BOUNDS = {
    "spark": (0, 250_000_000),
    "flash": (1_000_000_000, 2_000_000_000),
    "maxx": (4_000_000_000, 5_000_000_000),
}


def preserve_tokenizer_metadata(source_config, staged_config):
    # Transformers 5 can save a specific GPT2Tokenizer as TokenizersBackend.
    # llama.cpp uses the original class to select Phi's BPE or SentencePiece tokenizer.
    original = json.loads(source_config.read_text())
    saved = json.loads(staged_config.read_text())
    for key in ("tokenizer_class", "add_bos_token", "add_eos_token"):
        if key in original:
            saved[key] = original[key]
    staged_config.write_text(json.dumps(saved, ensure_ascii=False, indent=2) + "\n")


def register(a, out, tag, check_tag, embedded, tok):
    modelfile = a.run / "Modelfile"
    template_line = "" if a.baseline_source else f'TEMPLATE """{TEMPLATE}"""\n'
    modelfile.write_text(
        f"FROM {out.resolve()}\n{template_line}PARAMETER num_predict 1\nPARAMETER temperature 0\n"
    )
    env = {**os.environ, "OLLAMA_HOST": a.endpoint}
    stage = f"klara/cand-verify-{uuid.uuid4().hex}"
    subprocess.run(
        ["ollama", "create", stage, "-f", str(modelfile)], env=env, check=True
    )
    try:
        saved = request_json(a.endpoint + "/api/show", 30, {"model": stage})
        if a.native_baseline:
            from ollama_native import OllamaNative
            guard = OllamaNative(a.native_baseline, a.baseline_source)
            prefix = guard.prefix([{"role": "user", "content": "What is a circle?"}])
            expected = tok.encode(prefix)
            response = request_json(a.endpoint + "/api/generate", 120, {
                "model": stage, "prompt": prefix, "raw": True, "stream": False,
                "options": {"temperature": 0, "num_predict": 1}})
            require(response["prompt_eval_count"] == len(expected),
                    "native guard template length mismatch")
        elif a.baseline_source:
            # Ollama also recognizes native ChatML as an equivalent built-in Go template.
            messages = [
                {"role": "system", "content": CHAT_PROMPT},
                {"role": "user", "content": "[]"},
            ]
            expected = tok.apply_chat_template(
                messages,
                add_generation_prompt=True,
                tokenize=True,
                return_dict=True,
                enable_thinking=False,
            )["input_ids"]
            response = request_json(
                a.endpoint + "/api/chat",
                120,
                {
                    "model": stage,
                    "messages": messages,
                    "stream": False,
                    "think": False,
                    "options": {"temperature": 0, "num_predict": 1},
                },
            )
            require(
                response["prompt_eval_count"] == len(expected),
                "native baseline template length mismatch",
            )
        else:
            require(
                saved["template"].strip() in (embedded.strip(), TEMPLATE.strip()),
                "served template differs from fitted template",
            )
        check_tag()
        subprocess.run(["ollama", "cp", stage, tag], env=env, check=True)
    finally:
        subprocess.run(["ollama", "rm", stage], env=env, check=True)


def main():
    from peft import PeftModel
    from train_chat import load_base, token_pair
    from transformers import AutoTokenizer

    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--run",
        type=Path,
        required=True,
        help="new export folder or completed training run",
    )
    p.add_argument(
        "--baseline-source",
        type=Path,
        help="export untouched weights for a zero-shot baseline",
    )
    p.add_argument("--tier", choices=BOUNDS, required=True)
    p.add_argument("--name", required=True, help="model slug")
    p.add_argument(
        "--round", required=True, choices=["baseline", "r1", "r2", "fixture"]
    )
    p.add_argument(
        "--quant",
        required=True,
        choices=["F16", "Q8_0", "Q6_K", "Q5_K_M", "Q4_K_M", "Q4_K_S"],
    )
    p.add_argument(
        "--converter",
        type=Path,
        default=WORK / "env/tools/llama.cpp/convert_hf_to_gguf.py",
    )
    p.add_argument("--native-baseline", choices=["granite", "qwen-guard"])
    p.add_argument("--endpoint", default="http://127.0.0.1:18282")
    stages = p.add_mutually_exclusive_group()
    stages.add_argument(
        "--merge-only",
        action="store_true",
        help="save a staged HF merge before releasing source disk",
    )
    stages.add_argument(
        "--consume-merged",
        action="store_true",
        help="convert then release this run's staged HF merge",
    )
    stages.add_argument(
        "--register-only",
        action="store_true",
        help="retry import of an existing run GGUF",
    )
    a = p.parse_args()
    started = time.monotonic()
    timings = {}
    require(
        a.run.resolve().is_relative_to(MODELS.resolve())
        and re.fullmatch(r"[a-z0-9-]+", a.name),
        "invalid task output or slug",
    )
    a.run.mkdir(parents=True, exist_ok=True)
    tag = f"klara/cand-{a.tier}-{a.name}-{a.round}"

    def check_tag():
        tags = request_json(a.endpoint + "/api/tags", 30)["models"]
        require(
            all(m["name"].removesuffix(":latest") != tag for m in tags),
            f"tag already exists: {tag}",
        )

    if not a.merge_only:
        check_tag()
    if a.tier == "maxx" and a.round != "fixture":
        from maxx_space import reserve, source_weights
        bounded = True
    else:
        bounded = False
    if a.baseline_source:
        require(a.round == "baseline", "baseline tag required")
        source = a.baseline_source
        recipe = {}
    else:
        recipe = json.loads((a.run / "chat.json").read_text())
        require(recipe["tier"] == a.tier, "wrong tier")
        source = Path(recipe["source"])
    out = a.run / "candidate.gguf"
    if a.register_only:
        low, high = BOUNDS[a.tier]
        require(
            out.is_file() and low <= out.stat().st_size <= high,
            "expected tier-sized candidate.gguf",
        )
        tok = AutoTokenizer.from_pretrained(source) if a.baseline_source else None
        register(a, out, tag, check_tag, tok.chat_template if tok else JINJA, tok)
        print(tag)
        return
    require(not out.exists(), "GGUF already exists; --register-only retries import")
    prepared = a.run / "merged-for-conversion"
    if a.merge_only or a.consume_merged:
        require(not a.baseline_source, "staged merge applies to tuned weights")
    with tempfile.TemporaryDirectory(dir=a.run) as d:
        scratch = Path(d)
        hf = source if a.baseline_source else scratch / "hf"
        if a.consume_merged:
            require(
                prepared.is_dir() and not prepared.is_symlink(),
                "missing prepared merge",
            )
            hf = prepared
        tok = AutoTokenizer.from_pretrained(hf if a.consume_merged else source)
        ids, words = token_pair(tok)
        embedded = tok.chat_template if a.baseline_source else JINJA
        require(isinstance(embedded, str) and embedded, "missing source chat template")
        if not a.baseline_source:
            require(ids == recipe["ids"], "tokenizer changed since training")
            if a.consume_merged:
                require(
                    tok.chat_template == JINJA, "prepared checkpoint template mismatch"
                )
            else:
                if bounded:
                    reserve(sum(p.stat().st_size for p in source_weights(source)) + 150_000_000, "merge")
                base = load_base(source)
                if recipe.get("init_adapter"):
                    base = PeftModel.from_pretrained(
                        base, recipe["init_adapter"]
                    ).merge_and_unload()
                if recipe.get("fp16"):
                    base.half()
                merged = PeftModel.from_pretrained(
                    base, a.run / "adapter"
                ).merge_and_unload(safe_merge=True)
                merged.save_pretrained(hf)
                tok.chat_template = JINJA
                tok.save_pretrained(hf)
                if (
                    merged.config.model_type == "phi3"
                    and (source / "tokenizer_config.json").is_file()
                ):
                    preserve_tokenizer_metadata(
                        source / "tokenizer_config.json", hf / "tokenizer_config.json"
                    )
                del merged, base
            if a.merge_only:
                require(not prepared.exists(), "prepared checkpoint already exists")
                hf.rename(prepared)
                (a.run / "merge-timing.json").write_text(
                    json.dumps({"seconds": time.monotonic() - started})
                )
                print(prepared)
                return
        direct = a.quant in ("F16", "Q8_0")
        tmp = scratch / "converted.gguf"
        if bounded:
            budget = BOUNDS[a.tier][1] if direct else sum(p.stat().st_size for p in hf.glob("*.safetensors"))
            reserve(budget + 50_000_000, "conversion", evict=None if a.baseline_source else source)
        tick = time.monotonic()
        subprocess.run(
            [
                sys.executable,
                str(a.converter),
                str(hf),
                "--outfile",
                str(tmp),
                "--outtype",
                a.quant.lower() if direct else "f16",
            ],
            check=True,
        )
        timings["convert_seconds"] = time.monotonic() - tick
        timings["quantize_seconds"] = 0.0
        if not a.baseline_source:
            shutil.rmtree(hf)  # Private staging, or the explicitly consumed merge.
        if not direct:
            if bounded:
                reserve(BOUNDS[a.tier][1], "quantization", evict=source)
            tick = time.monotonic()
            quantized = scratch / "quantized.gguf"
            subprocess.run(
                ["llama-quantize", str(tmp), str(quantized), a.quant], check=True
            )
            timings["quantize_seconds"] = time.monotonic() - tick
            tmp = quantized
        size = tmp.stat().st_size
        low, high = BOUNDS[a.tier]
        require(low <= size <= high, f"GGUF size {size} outside {a.tier} bounds")
        tmp.rename(out)
    tick = time.monotonic()
    if bounded:
        reserve(out.stat().st_size + 50_000_000, "private registration", evict=source)
    register(a, out, tag, check_tag, embedded, tok)
    timings["register_seconds"] = time.monotonic() - tick
    (a.run / "export-timing.json").write_text(json.dumps(timings))
    print(json.dumps({"tag": tag, "bytes": size, "tokens": words, "ids": ids}))


if __name__ == "__main__":
    main()
