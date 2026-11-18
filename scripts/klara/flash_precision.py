"""Fit a residual LoRA with the first-round GGUF's frozen weights and K-quant grids."""

from types import MethodType

import gguf
import numpy as np
import torch
from gguf.quants import Q4_K
from torch.nn import functional as F

from common import require


def grid(tensor):
    """Return the deployed scale, offset and code range for every sub-block."""
    kind = tensor.tensor_type
    raw = tensor.data.reshape(-1, gguf.GGML_QUANT_SIZES[kind][1])
    if kind == gguf.GGMLQuantizationType.Q5_K:
        d = raw[:, :2].copy().view(np.float16).astype(np.float32)
        m = raw[:, 2:4].copy().view(np.float16).astype(np.float32)
        sc, mn = Q4_K.get_scale_min(raw[:, 4:16])
        return d * sc, -(m * mn), 0, 31
    require(kind == gguf.GGMLQuantizationType.Q6_K, f"unsupported trainable grid {kind}")
    d = raw[:, -2:].copy().view(np.float16).astype(np.float32)
    return d * raw[:, -18:-2].view(np.int8), np.zeros((1, 1), np.float16), -32, 31


def project(layer, x):
    base = layer.get_base_layer()
    merged = base.weight + layer.get_delta_weight("default").to(base.weight.dtype)
    blocks = merged.detach().float().reshape(layer.grid_scale.numel(), -1)
    scale = layer.grid_scale
    codes = ((blocks - layer.grid_offset) / torch.where(scale == 0, 1, scale)).round()
    snapped = (codes.clamp(*layer.code_range) * scale + layer.grid_offset).reshape_as(merged)
    effective = snapped.to(merged.dtype) + (merged - merged.detach())
    return F.linear(x, effective, base.bias)


@torch.no_grad()
def configure(model, gguf_path):
    from peft.tuners.lora.layer import Linear

    base = model.get_base_model()
    config = base.config.get_text_config()
    granite = config.model_type == "granite"
    arch = gguf.MODEL_ARCH.GRANITE if granite else gguf.MODEL_ARCH.QWEN35
    if not granite:
        require(config.model_type == "qwen3_5_text" and
                config.linear_num_key_heads == config.linear_num_value_heads,
                "unsupported K-quant architecture")
    names = gguf.get_tensor_name_map(arch, config.num_hidden_layers)
    reader = gguf.GGUFReader(str(gguf_path))
    tensors = {t.name: t for t in reader.tensors}
    visited = set()
    for name, layer in base.named_modules():
        if "visual" in name or "vision" in name or name.endswith(".base_layer"):
            continue
        if not isinstance(layer, (Linear, torch.nn.Linear, torch.nn.Embedding)):
            continue
        if ".lora_" in name:
            continue
        weight = layer.weight
        if id(weight) in visited:
            continue
        visited.add(id(weight))
        mapped = names.get_name(name.replace("language_model.", "") + ".weight",
                                try_suffixes=(".weight",))
        if mapped == "output.weight" and mapped not in tensors and config.tie_word_embeddings:
            mapped = "token_embd.weight"
        require(mapped in tensors, f"missing GGUF weight for {name}")
        t = tensors[mapped]
        require(tuple(reversed(t.shape)) == tuple(weight.shape), f"shape mismatch for {name}")
        if isinstance(layer, Linear):
            # V projections have identical row order in these two HF/GGUF mappings.
            require(name.endswith(".v_proj"), "residual K-quant fit expects V projections")
            scale, offset, lo, hi = grid(t)
            for field, array in (("grid_scale", scale), ("grid_offset", offset)):
                layer.register_buffer(field, torch.from_numpy(array.astype(np.float32)).to(
                    weight.device).reshape(-1, 1), persistent=False)
            layer.code_range = lo, hi
            layer.forward = MethodType(project, layer)
            continue
        # Decode in row chunks so the 248k-token embedding fits on the host.
        order = np.arange(weight.shape[0])
        if granite and name.endswith((".q_proj", ".k_proj")):
            heads = config.num_attention_heads if name.endswith(".q_proj") else config.num_key_value_heads
            order = order.reshape(heads, -1, 2).swapaxes(1, 2).reshape(-1)
        for start in range(0, len(order), 256):
            part = t.data[order[start:start + 256]]
            decoded = gguf.dequantize(part, t.tensor_type)
            weight[start:start + len(part)].copy_(torch.from_numpy(decoded.copy()))
