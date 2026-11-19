"""Second candidate: low-rank updates to Qwen3Guard's upper blocks on the mixed chats, merged into a copy of the GGUF.

Trains rank-r updates of the Q6_K tensors `attn_v` and `ffn_down` in the top blocks so the source verdict weights
pick the right word after `Safety:`, while a distillation loss holds every other token of the reply to the source
model. Writes a GGUF that differs from the source only in those tensors; refit its verdict rows with tune_chat.py
(`--gguf`) and compare both candidates on validation.
"""
import argparse
import json
import math
from pathlib import Path
import random
import re
import shutil
import time

from gguf import GGUFReader, GGMLQuantizationType, dequantize
import numpy as np
import torch
import torch.nn.functional as F

from benchmark_chat import VERDICTS, accepted, load_cases, prompt
from tune import BASE, embedding_server, ollama, q6_rows
from tune import VERDICTS as WORDS
from tune_chat import anchor_word, scores

BLOCKS = 28
HEADS, KV_HEADS, HEAD_DIM = 16, 8, 128


def rms(x, weight, eps=1e-6):
    return x * torch.rsqrt(x.pow(2).mean(-1, keepdim=True) + eps) * weight


def rope(x, base=1e6):
    d, length = x.shape[-1], x.shape[-2]
    inv = 1.0 / (base ** (torch.arange(0, d, 2, device=x.device, dtype=torch.float32) / d))
    angles = torch.arange(length, device=x.device, dtype=torch.float32)[:, None] * inv[None]
    cos, sin = torch.cat((angles.cos(), angles.cos()), -1), torch.cat((angles.sin(), angles.sin()), -1)
    return x * cos + torch.cat((-x[..., d // 2:], x[..., : d // 2]), -1) * sin


def block(x, w, i, mask, delta=None):
    def lin(name, v):
        full = f"blk.{i}.{name}.weight"
        out = F.linear(v, w[full])
        if delta is not None and full in delta:
            a, b, scale = delta[full]
            out = out + F.linear(F.linear(v, a), b) * scale
        return out

    batch, length, _ = x.shape
    h = rms(x, w[f"blk.{i}.attn_norm.weight"])
    q = lin("attn_q", h).view(batch, length, HEADS, HEAD_DIM).transpose(1, 2)
    k = lin("attn_k", h).view(batch, length, KV_HEADS, HEAD_DIM).transpose(1, 2)
    v = lin("attn_v", h).view(batch, length, KV_HEADS, HEAD_DIM).transpose(1, 2)
    q = rope(rms(q, w[f"blk.{i}.attn_q_norm.weight"]))
    k = rope(rms(k, w[f"blk.{i}.attn_k_norm.weight"])).repeat_interleave(HEADS // KV_HEADS, dim=1)
    v = v.repeat_interleave(HEADS // KV_HEADS, dim=1)
    a = F.scaled_dot_product_attention(q, k, v, attn_mask=mask)
    x = x + lin("attn_output", a.transpose(1, 2).reshape(batch, length, HEADS * HEAD_DIM))
    h = rms(x, w[f"blk.{i}.ffn_norm.weight"])
    return x + lin("ffn_down", F.silu(lin("ffn_gate", h)) * lin("ffn_up", h))


def run(w, x, start, stop, delta=None):
    mask = torch.ones(x.shape[1], x.shape[1], dtype=torch.bool, device=x.device).tril()
    for i in range(start, stop):
        x = block(x, w, i, mask, delta)
    return x


def tokenise(executable, model, template, cases):
    """Per row: tokens through `Safety: <word>\\nCategories:`, the index of `Safety:`'s colon and of the prompt's end."""
    out = []
    with embedding_server(executable, model) as request:
        def tok(text):
            return request("/tokenize", {"content": text, "add_special": False, "parse_special": True})["tokens"]

        ids = [tok(v)[0] for v in WORDS]
        for i, (split, row) in enumerate(cases):
            text = template.replace("{{ .Prompt }}", prompt(row))
            head, query = tok(text), tok(text + "Safety:")
            full = tok(text + "Safety: " + anchor_word(row, i) + "\nCategories:")
            if query[:len(head)] != head or full[:len(query)] != query:
                raise ValueError("The reply does not tokenise as a continuation of the prompt")
            out.append({"split": split, "tokens": full, "end": len(head) - 1, "verdict": len(query) - 1,
                        "mask": [v in accepted(row) for v in VERDICTS], "single": "request" in row})
    return ids, out


def batches(items, size, rng):
    order = list(range(len(items)))
    rng.shuffle(order)
    chunks = [sorted(order[i:i + size * 40], key=lambda j: len(items[j]["tokens"])) for i in range(0, len(order), size * 40)]
    groups = [chunk[i:i + size] for chunk in chunks for i in range(0, len(chunk), size)]
    rng.shuffle(groups)
    return groups


def pad(items, device, query_only=False):
    rows = [it["tokens"][:it["verdict"] + 1] if query_only else it["tokens"] for it in items]
    width = max(map(len, rows))
    return torch.tensor([r + [0] * (width - len(r)) for r in rows], device=device)


def verdict_logits(w, delta, items, ids, first, device, size=32):
    """Logits of the three verdict words, and whether any other token outranks them, for each item."""
    order = sorted(range(len(items)), key=lambda j: items[j]["verdict"])
    logits, stray = np.zeros((len(items), 3)), np.zeros(len(items), dtype=bool)
    with torch.no_grad():
        for i in range(0, len(order), size):
            group = [items[j] for j in order[i:i + size]]
            x = run(w, run(w, w["token_embd.weight"][pad(group, device, True)], 0, first), first, BLOCKS, delta)
            at = torch.tensor([g["verdict"] for g in group], device=device)
            full = rms(x[torch.arange(len(group), device=device), at], w["output_norm.weight"]) @ w["output.weight"].T
            logits[order[i:i + size]] = full[:, ids].float().cpu().numpy()
            stray[order[i:i + size]] = (~torch.isin(full.argmax(-1), torch.tensor(ids, device=device))).cpu().numpy()
    return logits, stray


def train(args):
    if args.out_dir.exists():
        raise FileExistsError(f"Choose a new output directory: {args.out_dir}")
    torch.manual_seed(args.seed)
    rng = random.Random(args.seed)
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    cases = [c for source in ("single", "multi")
             for c in load_cases(source, args.single if source == "single" else args.multi, args.split_file)
             if c[0] in ("train", "validation")]
    modelfile = ollama("/api/show", {"model": BASE})["modelfile"]
    model = Path(re.search(r"^FROM[ \t]+([^\r\n]+)", modelfile, re.M)[1].strip().strip('"'))
    quoted = re.search(r'^TEMPLATE[ \t]+(?P<quote>"""|")(?P<text>.*?)(?P=quote)[ \t]*\r?$', modelfile, re.M | re.S)
    template = (args.template_file.read_text(encoding="utf-8") if args.template_file else quoted["text"]).replace("\r\n", "\n")
    ids, items = tokenise(args.llama_server, model, template, cases)
    rows = [row for _, row in cases]
    fit_items = [it for it in items if it["split"] == "train"]
    held = {name: [(it, row) for it, row in zip(items, rows) if it["split"] == "validation" and it["single"] == (name == "single")]
            for name in ("single", "multi")}
    n_single = sum(it["single"] for it in fit_items)
    for it in fit_items:  # each source averaged over its own rows, then mixed
        share = args.single_share / n_single if it["single"] else (1 - args.single_share) / (len(fit_items) - n_single)
        it["weight"] = share * len(fit_items)
    print(f"Train {n_single} single-turn + {len(fit_items) - n_single} multi-turn; longest {max(len(it['tokens']) for it in items)} tokens",
          flush=True)

    reader = GGUFReader(model)
    tensors = {t.name: t for t in reader.tensors}
    w = {name: torch.from_numpy(np.array(dequantize(t.data, t.tensor_type), dtype=np.float32)).to(device)
         for name, t in tensors.items()}
    first = BLOCKS - args.blocks
    names = [f"blk.{i}.{part}.weight" for i in range(first, BLOCKS) for part in ("attn_v", "ffn_down")]
    if any(tensors[name].tensor_type != GGMLQuantizationType.Q6_K for name in names):
        raise ValueError("This recipe writes Q6_K tensors only")
    delta = {}
    for name in names:
        out_width, in_width = w[name].shape
        a = torch.nn.Parameter(torch.randn(args.rank, in_width, device=device) / math.sqrt(in_width))
        b = torch.nn.Parameter(torch.zeros(out_width, args.rank, device=device))
        delta[name] = (a, b, args.scale)
    params = [p for a, b, _ in delta.values() for p in (a, b)]
    optimiser = torch.optim.AdamW(params, lr=args.lr, weight_decay=0.0)
    steps = args.epochs * math.ceil(len(fit_items) / args.batch)
    schedule = torch.optim.lr_scheduler.OneCycleLR(optimiser, max_lr=args.lr, total_steps=steps, pct_start=0.1)
    id_tensor = torch.tensor(ids, device=device)

    def validate(tag):
        report, total = {}, 0
        for name, pairs in held.items():
            logits, stray = verdict_logits(w, delta, [it for it, _ in pairs], ids, first, device)
            report[name] = scores(logits, [row for _, row in pairs]) | {"first_token_not_a_verdict": int(stray.sum())}
            total += report[name]["balanced_safe_vs_not"] / 2
        report["balanced_safe_vs_not"] = round(total, 4)
        print(f"{tag}: balanced {total:.4f} " + ", ".join(
            f"{name} {report[name]['exact']}/{report[name]['rows']} (stray {report[name]['first_token_not_a_verdict']})"
            for name in held), flush=True)
        return report

    history = [{"step": 0} | validate("source weights")]
    best = (history[0]["balanced_safe_vs_not"], 0, None)
    step, started = 0, time.monotonic()
    for epoch in range(args.epochs):
        for group in batches(fit_items, args.batch, rng):
            batch = [fit_items[j] for j in group]
            tokens = pad(batch, device)
            with torch.no_grad():
                lower = run(w, w["token_embd.weight"][tokens], 0, first)
                source = run(w, lower, first, BLOCKS)
            tuned = run(w, lower, first, BLOCKS, delta)
            loss_verdict = loss_format = 0.0
            for j, it in enumerate(batch):
                # The reply's positions: prompt end (writes `Safety`) through the token before the category.
                span = torch.arange(it["end"], len(it["tokens"]), device=device)
                logp = F.log_softmax(rms(tuned[j, span], w["output_norm.weight"]) @ w["output.weight"].T, dim=-1)
                with torch.no_grad():
                    ref = F.log_softmax(rms(source[j, span], w["output_norm.weight"]) @ w["output.weight"].T, dim=-1)
                at = it["verdict"] - it["end"]
                mask = torch.tensor(it["mask"], device=device)
                loss_verdict = loss_verdict - it["weight"] * torch.logsumexp(logp[at, id_tensor][mask], dim=0)
                keep = torch.ones(len(span), dtype=torch.bool, device=device)
                keep[at] = False
                loss_format = loss_format + F.kl_div(logp[keep], ref[keep], log_target=True, reduction="sum") / keep.sum()
            loss = (loss_verdict + args.format_weight * loss_format) / len(batch)
            optimiser.zero_grad(set_to_none=True)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(params, 1.0)
            optimiser.step()
            schedule.step()
            step += 1
            if step % 25 == 0:
                print(f"step {step}/{steps} loss {loss.item():.4f} verdict {float(loss_verdict) / len(batch):.4f} "
                      f"format {float(loss_format) / len(batch):.4f} {time.monotonic() - started:.0f}s", flush=True)
            if step % args.eval_every == 0 or step == steps:
                history.append({"step": step} | validate(f"step {step}"))
                # Choose the checkpoint on validation: no stray first tokens, then balanced Safe-vs-not accuracy.
                stray = sum(history[-1][name]["first_token_not_a_verdict"] for name in held)
                if stray == 0 and history[-1]["balanced_safe_vs_not"] > best[0]:
                    best = (history[-1]["balanced_safe_vs_not"], step,
                            {name: (a.detach().clone(), b.detach().clone()) for name, (a, b, _) in delta.items()})
    print(f"Best checkpoint: step {best[1]} with balanced {best[0]:.4f}", flush=True)
    if best[2] is None:
        raise SystemExit("No checkpoint improved on the source weights; nothing exported")

    args.out_dir.mkdir()
    target = args.out_dir / f"{args.name}.gguf"
    shutil.copyfile(model, target)
    with target.open("r+b") as dest:
        for name, (a, b) in best[2].items():
            merged = (w[name] + args.scale * b @ a).float().cpu().numpy()
            packed = q6_rows(merged)
            if packed.size != tensors[name].data.nbytes:
                raise ValueError(f"{name}: encoded size differs from the source tensor")
            dest.seek(int(tensors[name].data_offset))
            dest.write(packed.tobytes())
    summary = {"tensors": names, "rank": args.rank, "scale": args.scale, "lr": args.lr, "epochs": args.epochs,
               "batch": args.batch, "single_share": args.single_share, "format_weight": args.format_weight,
               "seed": args.seed, "selected_step": best[1], "history": history}
    (args.out_dir / "lowrank.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(f"Merged GGUF ready: {target}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--single", type=Path, default=Path("data.tsv"))
    parser.add_argument("--multi", type=Path, default=Path("data-multi.tsv"))
    parser.add_argument("--split-file", type=Path, default=Path("data-multi-template-split.tsv"))
    parser.add_argument("--out-dir", required=True, type=Path, help="New directory for the merged GGUF")
    parser.add_argument("--name", default="lowrank")
    parser.add_argument("--template-file", type=Path)
    parser.add_argument("--blocks", type=int, default=5, help="Top blocks to update (their attn_v and ffn_down are Q6_K)")
    parser.add_argument("--rank", type=int, default=12)
    parser.add_argument("--scale", type=float, default=2.0)
    parser.add_argument("--lr", type=float, default=2e-4)
    parser.add_argument("--epochs", type=int, default=2)
    parser.add_argument("--batch", type=int, default=16)
    parser.add_argument("--single-share", type=float, default=0.5)
    parser.add_argument("--format-weight", type=float, default=1.0)
    parser.add_argument("--eval-every", type=int, default=250)
    parser.add_argument("--seed", type=int, default=20261111)
    bundled = Path("/Applications/Ollama.app/Contents/Resources/llama-server")
    parser.add_argument("--llama-server", default=shutil.which("llama-server") or (str(bundled) if bundled.is_file() else "llama-server"))
    train(parser.parse_args())
