"""Mixed-task low-rank QAT with exported-checkpoint validation and retained state.

The frozen lower layers use a checked float16 activation cache. Top blocks use
the original Q4_K/Q6_K grids in the forward pass and straight-through low-rank
gradients. Equal numbers from each task contribute equally to each optimizer
step. Checkpoints are selected by v3_protocol.selection, never test results.
"""
import argparse
from collections import defaultdict
import json
import math
from pathlib import Path
import random
import shutil
import time

from gguf import GGUFReader, GGMLQuantizationType, dequantize
from gguf.quants import Q4_K
import numpy as np
import torch
import torch.nn.functional as F

from qwen_torch import hidden, final
from quantize import pack
import v3_protocol as p
from v3_export import patch_template

PARTS = ('attn_q', 'attn_v', 'attn_output', 'ffn_down')


def grid(t, device):
    if t.tensor_type == GGMLQuantizationType.Q4_K:
        blocks = t.data.reshape(-1, 144); sc, mn = Q4_K.get_scale_min(blocks[:, 4:16])
        d = np.ascontiguousarray(blocks[:, :2]).view('<f2').astype(np.float32)
        dm = np.ascontiguousarray(blocks[:, 2:4]).view('<f2').astype(np.float32)
        step, offset = np.repeat(d * sc, 32, -1), np.repeat(dm * mn, 32, -1)
        lo, hi = 0, 15
    elif t.tensor_type == GGMLQuantizationType.Q6_K:
        blocks = t.data.reshape(-1, 210)
        d = np.ascontiguousarray(blocks[:, 208:]).view('<f2').astype(np.float32)
        sc = blocks[:, 192:208].view(np.int8).astype(np.float32)
        step, offset = np.repeat(d * sc, 16, -1), np.zeros((len(blocks), 256), dtype=np.float32)
        lo, hi = -32, 31
    else:
        raise ValueError(f'Unsupported QAT type: {t.tensor_type}')
    shape = tuple(reversed(t.shape.tolist()))
    return (torch.from_numpy(step.reshape(shape)).to(device), torch.from_numpy(offset.reshape(shape)).to(device), lo, hi)


def quant(value, spec):
    step, offset, lo, hi = spec
    return ((value + offset) / torch.where(step == 0, 1, step)).round().clamp(lo, hi) * step - offset


def effective(w, delta, grids, straight_through=True):
    result = dict(w)
    with torch.no_grad():
        for name, (a, b, scale) in delta.items():
            update = scale * b @ a
            rounded = quant(w[name] + update, grids[name])
            # The separate low-rank path supplies the derivative of the merge.
            result[name] = rounded - update if straight_through else rounded
    return result


class Cache:
    def __init__(self, path, items, device):
        self.offsets = np.load(path / 'offsets.npy')
        self.data = np.memmap(path / 'lower.f16', mode='r', dtype=np.float16, shape=(int(self.offsets[-1]), 1024))
        self.items, self.device = items, device

    def get(self, inds, query=False):
        lengths = [self.items[j]['verdict'] + 1 if query else len(self.items[j]['tokens']) for j in inds]
        arr = np.zeros((len(inds), max(lengths), 1024), dtype=np.float32)
        for i, (j, length) in enumerate(zip(inds, lengths)):
            arr[i, :length] = self.data[self.offsets[j]:self.offsets[j] + length]
        return torch.from_numpy(arr).to(self.device)


def batches(items, source, size, rng):
    inds = [j for j, it in enumerate(items) if it['source'] == source and it['split'] == 'train']
    if source == 'single':
        groups = defaultdict(list)
        for j in inds:
            groups[items[j]['request_id']].append(j)
        units = list(groups.values())
        if any(len(g) != 2 or {items[j]['mask'][0] for j in g} != {True, False} for g in units):
            raise ValueError('Single-turn requests must retain both replies')
        width = size // 2
    else:
        units, width = [[j] for j in inds], size
    rng.shuffle(units)
    chunks = [sorted(units[k:k + width * 32], key=lambda g: max(len(items[j]['tokens']) for j in g)) for k in range(0, len(units), width * 32)]
    result = [sum(chunk[k:k + width], []) for chunk in chunks for k in range(0, len(chunk), width)]
    rng.shuffle(result)
    return result


def validate(w, items, originals, ids, cache, first, batch=12):
    inds = sorted([j for j, it in enumerate(items) if it['split'] == 'validation'], key=lambda j: len(items[j]['tokens']))
    votes = {}; values = {}
    with torch.no_grad():
        for start in range(0, len(inds), batch):
            group = inds[start:start + batch]
            x = hidden(w, None, x=cache.get(group, True), start=first)
            at = torch.tensor([items[j]['verdict'] for j in group], device=x.device)
            out = final(w, x[torch.arange(len(group), device=x.device), at]) @ w['output.weight'].T
            best = out.argmax(-1).cpu().tolist()
            rows = out[:, ids].cpu().numpy()
            for j, choice, row in zip(group, best, rows):
                votes[j] = p.VERDICTS[ids.index(choice)] if choice in ids else 'invalid'
                values[j] = row.tolist()
    ordered = sorted(votes)
    return p.summary([originals[j] for j in ordered], [votes[j] for j in ordered]), dict(votes=votes, logits=values)


def export(out, model, tensors, w, delta, grids, record, optimizer, scheduler, rng):
    out.mkdir()
    path = out / 'candidate.gguf'
    shutil.copyfile(model, path)
    trainability = {}
    with torch.no_grad(), path.open('r+b') as f:
        for name, (a, b, scale) in delta.items():
            update = scale * b @ a
            value = quant(w[name] + update, grids[name])
            encoded = pack(value.cpu().numpy(), tensors[name])
            actual = dequantize(encoded, tensors[name].tensor_type)
            if not np.allclose(actual, value.cpu().numpy(), atol=1e-7, rtol=0):
                raise ValueError(f'QAT/export grid mismatch: {name}')
            f.seek(int(tensors[name].data_offset)); f.write(encoded.tobytes())
            trainability[name] = dict(changed_bytes=int(np.count_nonzero(encoded != tensors[name].data)),
                                      changed_weights=int((value != w[name]).sum().item()),
                                      weights=value.numel(), update_rms=float(update.square().mean().sqrt()),
                                      relative_update_norm=float(update.norm() / w[name].norm()))
    patch_template(path)
    (out / 'Modelfile').write_text(p.definition('./candidate.gguf'))
    torch.save(dict(delta={n: (a.detach().cpu(), b.detach().cpu(), scale) for n, (a, b, scale) in delta.items()},
                    optimizer=optimizer.state_dict(), scheduler=scheduler.state_dict(),
                    python_rng=rng.getstate(), torch_rng=torch.get_rng_state()), out / 'checkpoint.pt')
    (out / 'selected.json').write_text(json.dumps(record | dict(gguf_sha256=p.sha(path), trainability=trainability), indent=2) + '\n')
    print('Exported checkpoint', out, 'changed tensors', sum(v['changed_bytes'] > 0 for v in trainability.values()), flush=True)


def train(a):
    a.out.mkdir(parents=True)
    torch.set_num_threads(6); torch.manual_seed(a.seed); rng = random.Random(a.seed)
    device = 'mps' if torch.backends.mps.is_available() else 'cpu'
    token_data = json.loads((a.prepared / 'tokens.json').read_text())
    if token_data['protocol_sha256'] != p.sha(p.__file__) or token_data['template_sha256'] != p.sha(p.TEMPLATE):
        raise ValueError('Prepared contract differs')
    items, ids, first = token_data['items'], token_data['ids'], token_data['first']
    all_items, audit = p.load(a.root)
    lookup = {(it['source'], it['index']): it for it in all_items}
    originals = [lookup[it['source'], it['index']] for it in items]
    if any(it['split'] not in ('train', 'validation') for it in items):
        raise ValueError('Test/excluded row reached training')
    cache = Cache(a.prepared, items, device)
    reader = GGUFReader(a.model); tensors = {t.name: t for t in reader.tensors}
    source = GGUFReader(Path(json.loads((a.prepared / 'source.json').read_text())['path']))
    src = {t.name: t for t in source.tensors}
    for n, t in tensors.items():
        if n == 'token_embd.weight' or (n.startswith('blk.') and int(n.split('.')[1]) < first):
            if not np.array_equal(t.data, src[n].data):
                raise ValueError('Lower-layer cache is not valid for this model')
    names = [f'blk.{i}.{part}.weight' for i in range(first, 28) for part in PARTS]
    wanted = [n for n in tensors if n in ('output_norm.weight', 'output.weight') or (n.startswith('blk.') and int(n.split('.')[1]) >= first)]
    w = {n: torch.from_numpy(np.array(dequantize(tensors[n].data, tensors[n].tensor_type), dtype=np.float32)).to(device) for n in wanted}
    grids = {n: grid(tensors[n], device) for n in names}
    for n in names:
        if not torch.allclose(quant(w[n], grids[n]), w[n], rtol=0, atol=1e-7):
            raise ValueError(f'Zero-update QAT changed source weights: {n}')
    delta = {}
    for n in names:
        h, d = w[n].shape
        delta[n] = (torch.nn.Parameter(torch.randn(a.rank, d, device=device) / math.sqrt(d)),
                    torch.nn.Parameter(torch.zeros(h, a.rank, device=device)), a.scale)
    if a.resume:
        checkpoint = torch.load(a.resume, map_location='cpu', weights_only=True)
        with torch.no_grad():
            for n, (left, right, scale) in delta.items():
                old = checkpoint['delta'][n]
                if scale != old[2]:
                    raise ValueError('Resume adapter scale differs')
                left.copy_(old[0]); right.copy_(old[1])
    params = [param for left, right, _ in delta.values() for param in (left, right)]
    optimizer = torch.optim.AdamW(params, lr=a.lr, weight_decay=a.decay)
    steps_per_epoch = math.ceil(sum(it['split'] == 'train' and it['source'] == 'multi' for it in items) / a.task_batch)
    total = a.epochs * steps_per_epoch
    scheduler = torch.optim.lr_scheduler.OneCycleLR(optimizer, max_lr=a.lr, total_steps=total, pct_start=.1)
    baseline = json.loads(a.baseline.read_text())
    class_counts = np.array([sum(it['mask'][j] for it in items if it['split'] == 'train' and it['source'] == 'multi') for j in range(3)])
    frequencies = class_counts / class_counts.sum()
    balanced_class_weights = 1 / np.sqrt(frequencies) if a.multi_class_weight else np.ones(3)
    balanced_class_weights[1] *= getattr(a, 'unsafe_weight', 1.)
    balanced_class_weights /= frequencies @ balanced_class_weights
    class_weight = torch.tensor(balanced_class_weights, dtype=torch.float32, device=device)
    config = {k: str(v) if isinstance(v, Path) else v for k, v in vars(a).items()}
    (a.out / 'config.json').write_text(json.dumps(config | dict(source_sha256=p.sha(a.model), data=audit['hashes'], total_steps=total,
                                                              trainable_parameters=sum(param.numel() for param in params)), indent=2) + '\n')
    with torch.no_grad():
        report, votes = validate(effective(w, delta, grids, False), items, originals, ids, cache, first)
    history = [dict(step=0, validation=report, selection_key=p.selection(report, baseline))]
    best_key, best_path = None, None
    print('Initial validation', json.dumps(report), flush=True)
    (a.out / 'history.json').write_text(json.dumps(history, indent=2) + '\n')
    started, step, stale = time.monotonic(), 0, 0
    stop = False
    for epoch in range(a.epochs):
        single = batches(items, 'single', a.task_batch, rng)
        multi = batches(items, 'multi', a.task_batch, rng)
        si = 0
        for group_multi in multi:
            if si == len(single):
                single = batches(items, 'single', a.task_batch, rng); si = 0
            group_single = single[si]; si += 1
            optimizer.zero_grad(set_to_none=True)
            losses = defaultdict(float)
            # Microbatches preserve single-turn pairs, with exact task-level means.
            for group in (group_single, group_multi):
                for begin in range(0, len(group), a.micro_batch):
                    inds = group[begin:begin + a.micro_batch]; batch = [items[j] for j in inds]
                    lower = cache.get(inds)
                    with torch.no_grad():
                        teacher = hidden(w, None, x=lower, start=first)
                    qw = effective(w, delta, grids)
                    tuned = hidden(qw, None, x=lower, start=first, delta=delta)
                    at = torch.tensor([it['verdict'] for it in batch], device=device)
                    verdicts = final(w, tuned[torch.arange(len(batch), device=device), at]) @ w['output.weight'][ids].T
                    mask = torch.tensor([it['mask'] for it in batch], device=device)
                    logp = F.log_softmax(verdicts, -1)
                    each = -torch.logsumexp(logp.masked_fill(~mask, -torch.inf), -1)
                    if batch[0]['source'] == 'multi':
                        # Any severity/class reweighting retains a unit mean
                        # within multi, so the two tasks still contribute equally.
                        each = each * class_weight[mask.float().argmax(-1)]
                    loss_v = each.mean()
                    loss_keep = torch.zeros((), device=device)
                    if getattr(a, 'retain_weight', 0):
                        with torch.no_grad():
                            teacher_logits = final(w, teacher[torch.arange(len(batch), device=device), at]) @ w['output.weight'][ids].T
                            teacher_logp = F.log_softmax(teacher_logits, -1)
                            correct_teacher = mask.gather(1, teacher_logits.argmax(-1, keepdim=True)).squeeze(1)
                        divergence = F.kl_div(logp, teacher_logp, log_target=True, reduction='none').sum(-1)
                        loss_keep = (divergence * correct_teacher).sum() / correct_teacher.sum().clamp_min(1)
                    rows, positions = [], []
                    for j, it in enumerate(batch):
                        for pos in range(it['end'], len(it['tokens'])):
                            if pos != it['verdict']:
                                rows.append(j); positions.append(pos)
                    ri = torch.tensor(rows, device=device); pi = torch.tensor(positions, device=device)
                    fmt = F.log_softmax(final(w, tuned[ri, pi]) @ w['output.weight'].T, -1)
                    with torch.no_grad():
                        ref = F.log_softmax(final(w, teacher[ri, pi]) @ w['output.weight'].T, -1)
                    loss_f = F.kl_div(fmt, ref, log_target=True, reduction='batchmean')
                    loss_r = torch.zeros((), device=device)
                    if batch[0]['source'] == 'single':
                        margin = verdicts[:, 0] - torch.logsumexp(verdicts[:, 1:], -1)
                        rank = []
                        for j in range(0, len(batch), 2):
                            sign = 1 if batch[j]['mask'][0] else -1
                            rank.append(F.softplus(1 - sign * (margin[j] - margin[j + 1])))
                        loss_r = torch.stack(rank).mean()
                    fraction = .5 * len(inds) / len(group)
                    loss = fraction * (loss_v + a.format_weight * loss_f + a.rank_weight * loss_r +
                                       getattr(a, 'retain_weight', 0) * loss_keep)
                    loss.backward()
                    for k, val in [('verdict', loss_v), ('format', loss_f), ('rank', loss_r), ('retain', loss_keep)]:
                        losses[k] += fraction * float(val.detach())
                    del tuned, teacher, qw, lower, fmt, ref, loss, loss_v, loss_f, loss_r, loss_keep
            grad_norm = float(torch.nn.utils.clip_grad_norm_(params, 1.0))
            if not math.isfinite(grad_norm):
                raise ValueError('Nonfinite adapter gradient')
            if step == 0:
                grad_report = {n: dict(a=float(left.grad.norm()), b=float(right.grad.norm())) for n, (left, right, _) in delta.items()}
                if any(v['b'] == 0 for v in grad_report.values()):
                    raise ValueError('An adapter receives no gradient')
                (a.out / 'initial-gradients.json').write_text(json.dumps(grad_report, indent=2) + '\n')
            optimizer.step(); scheduler.step(); step += 1
            if step % 25 == 0:
                print(json.dumps(dict(step=step, total=total, epoch=epoch + 1, losses=losses, gradient_norm=grad_norm,
                                      seconds=round(time.monotonic() - started),
                                      gpu_bytes=torch.mps.current_allocated_memory() if device == 'mps' else None)), flush=True)
                if device == 'mps':
                    torch.mps.empty_cache()
            if step % a.eval_every == 0 or step == total or (a.stop_after and step == a.stop_after):
                with torch.no_grad():
                    rounded = effective(w, delta, grids, False)
                    report, votes = validate(rounded, items, originals, ids, cache, first)
                del rounded
                key = p.selection(report, baseline)
                record = dict(step=step, epoch=epoch + 1, validation=report, selection_key=key,
                              seconds=round(time.monotonic() - started))
                history.append(record)
                (a.out / 'history.json').write_text(json.dumps(history, indent=2) + '\n')
                print('QAT validation', json.dumps(record), flush=True)
                # Preserve every improving checkpoint; no overwrite or last-step-only export.
                if best_key is None or key > best_key:
                    best_key, best_path, stale = key, a.out / f'step-{step:04d}', 0
                    export(best_path, a.model, tensors, w, delta, grids, record, optimizer, scheduler, rng)
                    (best_path / 'validation-votes.json').write_text(json.dumps(votes) + '\n')
                    (a.out / 'best.json').write_text(json.dumps(dict(path=str(best_path), **record), indent=2) + '\n')
                else:
                    stale += 1
                if a.patience and stale >= a.patience:
                    stop = True
                if device == 'mps':
                    torch.mps.empty_cache()
            if stop or (a.stop_after and step >= a.stop_after):
                stop = True
                break
        if stop:
            break
    (a.out / 'complete.json').write_text(json.dumps(dict(steps=step, best=str(best_path), seconds=time.monotonic() - started,
                                                       stopped_early=step < total), indent=2) + '\n')


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root', type=Path, default=Path.cwd())
    ap.add_argument('--prepared', type=Path, required=True)
    ap.add_argument('--model', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--baseline', type=Path, required=True)
    ap.add_argument('--epochs', type=int, default=2)
    ap.add_argument('--task-batch', type=int, default=8)
    ap.add_argument('--micro-batch', type=int, default=4)
    ap.add_argument('--rank', type=int, default=12)
    ap.add_argument('--scale', type=float, default=2.)
    ap.add_argument('--lr', type=float, default=6e-4)
    ap.add_argument('--decay', type=float, default=.01)
    ap.add_argument('--format-weight', type=float, default=.5)
    ap.add_argument('--rank-weight', type=float, default=.1)
    ap.add_argument('--eval-every', type=int, default=200)
    ap.add_argument('--patience', type=int, default=4)
    ap.add_argument('--stop-after', type=int)
    ap.add_argument('--multi-class-weight', action='store_true')
    ap.add_argument('--unsafe-weight', type=float, default=1., help='Relative multi UNSAFE cost, normalized within task')
    ap.add_argument('--retain-weight', type=float, default=0., help='KL on previously correct TRAIN verdicts; no validation targets')
    ap.add_argument('--resume', type=Path, help='Warm restart adapters from an OWN train-only checkpoint; optimizer restarts')
    ap.add_argument('--seed', type=int, default=20261113)
    train(ap.parse_args())
