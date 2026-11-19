"""Re-encode a trained upper-body export for train-only verdict calibration.

Reuses the unchanged lower-layer cache, with byte verification. Never reads test
tokens; the token manifest contains only training and validation items.
"""
import argparse
import json
import os
from pathlib import Path
import shutil
import time

from gguf import GGUFReader, dequantize
import numpy as np
import torch
from qwen_torch import hidden, final
from train_v3 import Cache
import v3_protocol as p


def refeature(prepared, model, out):
    out.mkdir(parents=True)
    data = json.loads((prepared / 'tokens.json').read_text())
    items, ids, first = data['items'], data['ids'], data['first']
    if any(it['split'] not in ('train', 'validation') for it in items):
        raise ValueError('Held-out tokens reached feature extraction')
    if data['protocol_sha256'] != p.sha(p.__file__) or data['template_sha256'] != p.sha(p.TEMPLATE):
        raise ValueError('Prepared contract differs')
    reader = GGUFReader(model)
    source = GGUFReader(Path(json.loads((prepared / 'source.json').read_text())['path']))
    original = {t.name: t for t in source.tensors}
    for t in reader.tensors:
        if t.name == 'token_embd.weight' or (t.name.startswith('blk.') and int(t.name.split('.')[1]) < first):
            if not np.array_equal(t.data, original[t.name].data):
                raise ValueError('Lower cache invalid for export')
    torch.set_num_threads(6)
    device = 'mps' if torch.backends.mps.is_available() else 'cpu'
    w = {t.name: torch.from_numpy(np.array(dequantize(t.data, t.tensor_type), dtype=np.float32)).to(device)
         for t in reader.tensors if t.name in ('output_norm.weight', 'output.weight') or
         (t.name.startswith('blk.') and int(t.name.split('.')[1]) >= first)}
    cache = Cache(prepared, items, device)
    vectors = np.empty((len(items), 1024), dtype=np.float32)
    other = np.full(len(items), np.nan, dtype=np.float32)
    anchors, anchor_other, anchor_choice = [], [], []
    order = sorted(range(len(items)), key=lambda j: len(items[j]['tokens']))
    start_time = time.monotonic()
    with torch.no_grad():
        for start in range(0, len(order), 12):
            inds = order[start:start + 12]; group = [items[j] for j in inds]
            x = hidden(w, None, x=cache.get(inds), start=first)
            at = torch.tensor([it['verdict'] for it in group], device=device)
            h = final(w, x[torch.arange(len(group), device=device), at])
            vectors[inds] = h.cpu().numpy()
            vi = [i for i, it in enumerate(group) if it['split'] == 'validation']
            if vi:
                logits = h[vi] @ w['output.weight'].T; logits[:, ids] = -torch.inf
                other[[inds[i] for i in vi]] = logits.max(-1).values.cpu().numpy()
            for i, j in enumerate(inds):
                it = items[j]
                if it['split'] != 'train' or j % 12:
                    continue
                positions = [k for k in range(it['end'], len(it['tokens'])) if k != it['verdict']]
                anchor = final(w, x[i, positions]); logits = anchor @ w['output.weight'].T
                anchor_choice.extend(logits.argmax(-1).cpu().tolist()); logits[:, ids] = -torch.inf
                anchor_other.extend(logits.max(-1).values.cpu().tolist()); anchors.extend(anchor.cpu().numpy())
            if (start // 12 + 1) % 100 == 0:
                print('Re-encoded', min(start + 12, len(items)), '/', len(items), 'seconds', round(time.monotonic() - start_time), flush=True)
                if device == 'mps':
                    torch.mps.empty_cache()
    np.savez(out / 'features.npz', vectors=vectors, other=other, anchors=np.array(anchors),
             anchor_other=np.array(anchor_other), anchor_choice=np.array(anchor_choice))
    shutil.copyfile(prepared / 'tokens.json', out / 'tokens.json')
    for name in ('lower.f16', 'offsets.npy'):
        (out / name).symlink_to(os.path.relpath((prepared / name).resolve(), out.resolve()))
    (out / 'source.json').write_text(json.dumps(dict(path=str(model.resolve()), sha256=p.sha(model), first=first,
                                                    lower_cache_from=str(prepared.resolve())), indent=2) + '\n')


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--prepared', type=Path, required=True)
    ap.add_argument('--model', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()
    refeature(a.prepared, a.model, a.out)
