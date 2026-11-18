"""Fit a LoRA on the first verdict token of the deployed Klara prompt."""

import json
from pathlib import Path
from types import MethodType

import torch
from backends import chat_prompt
from common import require
from peft import LoraConfig, PeftModel, get_peft_model
from training import fit, options, prepare, verdict_loss
from transformers import (
    AutoConfig,
    AutoModelForCausalLM,
    AutoModelForImageTextToText,
    AutoTokenizer,
)


def load_base(path):
    config = AutoConfig.from_pretrained(path, local_files_only=True)
    cls = (
        AutoModelForImageTextToText
        if "ConditionalGeneration" in config.architectures[0]
        else AutoModelForCausalLM
    )
    return cls.from_pretrained(path, dtype=torch.bfloat16, local_files_only=True)


def token_pair(tok):
    prefix = chat_prompt("[]")
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


@torch.no_grad()
def q8_weights(weight):
    """GGUF Q8_0 uses a half-precision scale and 32 signed codes per block."""
    blocks = weight.float().reshape(-1, 32)
    scale = blocks.abs().amax(1, keepdim=True) / 127
    inverse = torch.where(scale > 0, scale.reciprocal(), 0)
    scaled = blocks * inverse
    magnitude = scaled.abs()
    integral = magnitude.floor()
    codes = torch.sign(scaled) * (integral + (2 * (magnitude - integral)).floor())
    return (codes * scale.half().float()).reshape(weight.shape).to(weight.dtype)


def enable_smol_q8(model):
    """Simulate the deployed merged weights, keeping the two LoRA factors trainable."""
    from torch.nn import functional as F
    from peft.tuners.lora.layer import Linear

    def projected(self, x):
        base = self.get_base_layer()
        merged = base.weight + self.get_delta_weight("default").to(base.weight.dtype)
        # The straight-through gradient is the gradient of the merged projection.
        effective = q8_weights(merged) + (merged - merged.detach())
        return F.linear(x, effective, base.bias)

    require(
        model.config.model_type == "llama" and model.config.tie_word_embeddings,
        "Spark Q8 training expects tied SmolLM2 embeddings",
    )
    model.tie_weights()
    require(
        model.get_input_embeddings().weight is model.get_output_embeddings().weight,
        "expected shared embedding and output weights",
    )
    embedding = model.get_input_embeddings().weight
    with torch.no_grad():
        embedding.copy_(q8_weights(embedding))
    for layer in model.modules():
        if isinstance(layer, Linear):
            layer.forward = MethodType(projected, layer)


def main():
    p = options(__doc__)
    p.set_defaults(batch=1, lr=2e-4)
    p.add_argument("--rank", type=int, default=8)
    p.add_argument(
        "--q8-aware",
        action="store_true",
        help="simulate Q8_0 on SmolLM2's merged projections and tied embedding during fitting",
    )
    p.add_argument(
        "--verdict-smoothing",
        type=float,
        default=0.0,
        help="fraction of target mass on the other served verdict token",
    )

    p.add_argument(
        "--init-adapter",
        type=Path,
        help="warm-start round two from the first-round adapter",
    )
    p.add_argument("--r1-gguf", type=Path, help="fit residual V adapters on the deployed K-quant grids")
    p.add_argument("--fp16", action="store_true", help="fit on the warm-started FP16 weights")
    p.add_argument("--checkpointing", action="store_true")
    a = p.parse_args()
    require(0 <= a.verdict_smoothing < 0.5, "verdict smoothing must be in [0, 0.5)")
    rows = prepare(a)
    tok = AutoTokenizer.from_pretrained(a.source)
    tok.padding_side = "left"
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    ids, words = token_pair(tok)
    base = load_base(a.source)
    if a.init_adapter:
        base = PeftModel.from_pretrained(base, a.init_adapter).merge_and_unload()
    if a.fp16:
        base.to(dtype=torch.float16)
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
    if a.r1_gguf:
        require(a.init_adapter and not a.fp16, "K-quant fitting needs a round-one adapter")
        targets = [name for name in targets if name.endswith(".v_proj")][-4:]
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
    if a.r1_gguf:
        from flash_precision import configure
        configure(model, a.r1_gguf)
    if a.q8_aware:
        enable_smol_q8(model)
    verdict_ids = torch.tensor(ids, device=a.device)

    def forward(x, y):
        logits = model(**x, use_cache=False, logits_to_keep=1).logits[:, -1].float()
        return logits[:, verdict_ids], verdict_loss(
            logits, y, verdict_ids, a.verdict_smoothing
        )

    fit(model, tok, lambda text: tok.encode(chat_prompt(text)), forward, rows, a)
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
                "q8_aware": a.q8_aware,
                "fp16": a.fp16,
                "k_quant_residual": bool(a.r1_gguf),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
