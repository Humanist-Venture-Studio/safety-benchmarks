"""Fit a LoRA on the first verdict token of the deployed Klara prompt."""

import json
from pathlib import Path

import torch
from backends import CHAT_PROMPT
from common import require
from peft import LoraConfig, PeftModel, get_peft_model
from torch.nn import functional as F
from training import fit, options, prepare
from transformers import (
    AutoConfig,
    AutoModelForCausalLM,
    AutoModelForImageTextToText,
    AutoTokenizer,
)


# The Ollama Go template in export_chat.py emits exactly these bytes for the two harness messages.
def prompt(text):
    return f"System: {CHAT_PROMPT}\nUser: {text}\nAssistant:"


def load_base(path):
    config = AutoConfig.from_pretrained(path, local_files_only=True)
    cls = (
        AutoModelForImageTextToText
        if "ConditionalGeneration" in config.architectures[0]
        else AutoModelForCausalLM
    )
    return cls.from_pretrained(path, dtype=torch.bfloat16, local_files_only=True)


def token_pair(tok):
    prefix = prompt("[]")
    start = tok.encode(prefix, add_special_tokens=False)
    ids, words = [], []
    for label in ("safe", "unsafe"):
        for word in (" " + label, label, " " + label.title(), label.title()):
            result = tok.encode(prefix + word, add_special_tokens=False)
            if result[:-1] == start and tok.decode(result[-1:]) == word:
                ids.append(result[-1])
                words.append(word)
                break
        else:
            raise ValueError(
                f"no distinct single-token spelling of {label} after prompt"
            )
    require(ids[0] != ids[1], "verdicts share their first token")
    return ids, words


def main():
    p = options(__doc__)
    p.set_defaults(batch=1, lr=2e-4)
    p.add_argument("--rank", type=int, default=8)
    p.add_argument(
        "--init-adapter",
        type=Path,
        help="warm-start round two from the first-round adapter",
    )
    p.add_argument("--checkpointing", action="store_true")
    a = p.parse_args()
    rows = prepare(a)
    tok = AutoTokenizer.from_pretrained(a.source)
    tok.padding_side = "left"
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    ids, words = token_pair(tok)
    base = load_base(a.source)
    if a.init_adapter:
        base = PeftModel.from_pretrained(base, a.init_adapter).merge_and_unload()
    suffixes = {
        "q_proj",
        "k_proj",
        "v_proj",
        "o_proj",
        "qkv_proj",
        "gate_up_proj",
        "up_proj",
        "down_proj",
        "in_proj_qkv",
        "in_proj_z",
        "in_proj_a",
        "in_proj_b",
        "out_proj",
    }
    targets = [
        name
        for name, layer in base.named_modules()
        if isinstance(layer, torch.nn.Linear)
        and name.split(".")[-1] in suffixes
        and "visual" not in name
        and "vision" not in name
    ]
    require(targets and a.rank > 0, "no language projections or invalid rank")
    model = get_peft_model(
        base,
        LoraConfig(
            r=a.rank,
            lora_alpha=2 * a.rank,
            lora_dropout=0.0,
            target_modules=targets,
            task_type="CAUSAL_LM",
        ),
    )
    if a.checkpointing:
        model.gradient_checkpointing_enable(
            gradient_checkpointing_kwargs={"use_reentrant": False}
        )
        model.enable_input_require_grads()
    model.to(a.device)
    verdict_ids = torch.tensor(ids, device=a.device)

    def forward(x, y):
        logits = model(**x, use_cache=False, logits_to_keep=1).logits[:, -1].float()
        return logits[:, verdict_ids], F.cross_entropy(
            logits, verdict_ids[y], reduction="none"
        )

    fit(model, tok, lambda text: tok.encode(prompt(text)), forward, rows, a)
    model.save_pretrained(a.out / "adapter")
    (a.out / "chat.json").write_text(
        json.dumps(
            {
                "source": str(a.source.resolve()),
                "tokens": words,
                "ids": ids,
                "init_adapter": str(a.init_adapter.resolve())
                if a.init_adapter
                else None,
                "tier": a.tier,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
