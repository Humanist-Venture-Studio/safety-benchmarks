"""Minimal PyTorch Qwen3 0.6B forward pass over tensors dequantized from a GGUF.

`w` maps GGUF tensor names to float tensors. Adapted from Product Fox's forward
pass and low-rank update in tune_chat_lowrank.py (pull request #8).
"""
import torch
import torch.nn.functional as F


def rms(x, weight, eps=1e-6):
    return x * torch.rsqrt(x.pow(2).mean(-1, keepdim=True) + eps) * weight


def rope(x, base=1e6):
    # x: (B, heads, T, d)
    d, T = x.shape[-1], x.shape[-2]
    inv = 1.0 / (base ** (torch.arange(0, d, 2, device=x.device, dtype=torch.float32) / d))
    angles = torch.arange(T, device=x.device, dtype=torch.float32)[:, None] * inv[None]
    cos = torch.cat((angles.cos(), angles.cos()), -1).to(x.dtype)
    sin = torch.cat((angles.sin(), angles.sin()), -1).to(x.dtype)
    x1, x2 = x[..., : d // 2], x[..., d // 2:]
    return x * cos + torch.cat((-x2, x1), -1) * sin


def block(x, w, i, mask, delta=None, heads=16, kv_heads=8, head_dim=128):
    """delta: optional dict name -> low-rank (A, B, scale) added to that weight."""
    def lin(name, v):
        full = f"blk.{i}.{name}.weight"
        out = F.linear(v, w[full])
        if delta is not None and full in delta:
            a, b, scale = delta[full]
            out = out + F.linear(F.linear(v, a), b) * scale
        return out

    B, T, _ = x.shape
    h = rms(x, w[f"blk.{i}.attn_norm.weight"])
    q = lin("attn_q", h).view(B, T, heads, head_dim).transpose(1, 2)
    k = lin("attn_k", h).view(B, T, kv_heads, head_dim).transpose(1, 2)
    v = lin("attn_v", h).view(B, T, kv_heads, head_dim).transpose(1, 2)
    q = rope(rms(q, w[f"blk.{i}.attn_q_norm.weight"]))
    k = rope(rms(k, w[f"blk.{i}.attn_k_norm.weight"]))
    k = k.repeat_interleave(heads // kv_heads, dim=1)
    v = v.repeat_interleave(heads // kv_heads, dim=1)
    a = F.scaled_dot_product_attention(q, k, v, attn_mask=mask)
    x = x + lin("attn_output", a.transpose(1, 2).reshape(B, T, heads * head_dim))
    h = rms(x, w[f"blk.{i}.ffn_norm.weight"])
    return x + lin("ffn_down", F.silu(lin("ffn_gate", h)) * lin("ffn_up", h))


def causal_mask(T, device, pad=None):
    mask = torch.ones(T, T, dtype=torch.bool, device=device).tril()
    if pad is None:
        return mask
    # pad: (B, T) True where real token; left-padding is not used, sequences are right-padded.
    return mask[None, None] & pad[:, None, None, :]


def hidden(w, ids, start=0, stop=28, x=None, delta=None, pad=None):
    if x is None:
        x = w["token_embd.weight"][ids]
    mask = causal_mask(x.shape[1], x.device, pad)
    for i in range(start, stop):
        x = block(x, w, i, mask, delta)
    return x


def final(w, x):
    return rms(x, w["output_norm.weight"])
