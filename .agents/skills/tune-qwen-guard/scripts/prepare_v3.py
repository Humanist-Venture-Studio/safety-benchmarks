"""Prepare train/validation tokens and frozen lower-layer activations for v3.

No test row is tokenized. The float16 activation cache is a training acceleration,
not a change to exported weights; its numerical error is measured on train probes.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import re
import time

from gguf import GGUFReader, dequantize
import numpy as np
import torch
from qwen_torch import hidden, final
from tune import embedding_server, ollama, BASE, VERDICTS
import v3_protocol as p

SERVER = '/Applications/Ollama.app/Contents/Resources/llama-server'


def pad(items, device, query=False):
    rows = [it['tokens'][:it['verdict'] + 1] if query else it['tokens'] for it in items]
    width = max(map(len, rows))
    return torch.tensor([r + [0] * (width - len(r)) for r in rows], device=device)


def prepare(root, out, first=20):
    out.mkdir(parents=True)
    cases, audit = p.load(root)
    # Verify provenance and near-copy groups without writing either dataset.
    from split_templates import replay, template_groups
    rows, metadata, catalog = replay(root / 'data-multi.tsv', root / 'scripts')
    groups, edges = template_groups(catalog)
    manifest = {r['request_id']: r for r in p.read(root / 'data-multi-template-split.tsv')}
    owners = {}
    for row in rows:
        rid = row['request_id']; m = metadata[rid]; assignment = manifest[rid]
        if not m['verified'] or any(m[k] != assignment[k] for k in ('arc_id', 'module_id')):
            raise ValueError('Template provenance replay differs')
        if assignment['split'] != 'excluded':
            for k in ('arc_id', 'module_id'):
                if m[k] and owners.setdefault(groups[m[k]], assignment['split']) != assignment['split']:
                    raise ValueError('Near-copy template group crosses retained splits')
    (out / 'template-audit.json').write_text(json.dumps(dict(reproduced=len(rows), templates=len(catalog),
                                                           groups=len(set(groups.values())), near_copy_edges=len(edges),
                                                           shared_groups=0), indent=2) + '\n')
    cases = [it for it in cases if it['split'] in ('train', 'validation') and not it.get('fit_excluded')]
    template = p.TEMPLATE.read_text()
    info = ollama('/api/show', {'model': BASE})
    model = Path(re.search(r'^FROM\s+([^\r\n]+)', info['modelfile'], re.M)[1].strip().strip('"'))
    items, probes = [], []
    with embedding_server(SERVER, model) as request:
        def tok(text):
            return request('/tokenize', {'content': text, 'add_special': False, 'parse_special': True})['tokens']
        words = [tok(v) for v in VERDICTS]
        ids = [v[0] for v in words]
        if len(words[0]) != 1 or len(words[1]) != 1 or len(set(ids)) != 3:
            raise ValueError('Unexpected verdict tokenization')
        seen = set()
        for n, it in enumerate(cases):
            q = p.prompt(p.turns(it['row']), it['scope'])
            text = template.replace('{{ .Prompt }}', q)
            head, query = tok(text), tok(text + 'Safety:')
            allowed = [j for j, yes in enumerate(it['mask']) if yes]
            word = p.VERDICTS[allowed[n % len(allowed)]].capitalize()
            full = tok(text + 'Safety: ' + word + '\nCategories:' + (' None' if word == 'Safe' else ''))
            if query[:len(head)] != head or full[:len(query)] != query or len(full) > 2048:
                raise ValueError('Token continuation mismatch or excessive context; never truncate')
            item = {k: it[k] for k in ('source', 'index', 'request_id', 'split', 'scope', 'mask')}
            item.update(tokens=full, end=len(head) - 1, verdict=len(query) - 1)
            items.append(item)
            probe_key = (it['source'], it['mask'][0])
            if it['split'] == 'train' and probe_key not in seen:
                probe = ollama('/api/generate', {'model': BASE, 'prompt': q, 'template': template, 'stream': False,
                                                'options': dict(p.SETTINGS, num_predict=1)})
                if probe.get('eval_count') != 1 or probe.get('context', [])[:-1] != head:
                    raise ValueError('Ollama prompt-token mismatch')
                reference = np.asarray(request('/embedding', {'content': query, 'embd_normalize': -1})[0]['embedding']).reshape(-1)
                probes.append(dict(item=n, token_count=len(head), token_sha256=__import__('hashlib').sha256(json.dumps(head).encode()).hexdigest(), reference=reference.tolist()))
                seen.add(probe_key)
            if (n + 1) % 2000 == 0:
                print('Tokenized', n + 1, '/', len(cases), flush=True)
    (out / 'tokens.json').write_text(json.dumps(dict(ids=ids, items=items, first=first, source_sha256=p.sha(model),
                                                    data=audit['hashes'], protocol_sha256=p.sha(p.__file__),
                                                    template_sha256=p.sha(p.TEMPLATE))) + '\n')
    torch.set_num_threads(6)
    device = 'mps' if torch.backends.mps.is_available() else 'cpu'
    reader = GGUFReader(model)
    meta = {k: reader.fields[k].contents() for k in reader.fields if k.startswith('qwen3.')}
    w = {t.name: torch.from_numpy(np.array(dequantize(t.data, t.tensor_type), dtype=np.float32)).to(device)
         for t in reader.tensors}
    for key, value in {'qwen3.block_count': 28, 'qwen3.embedding_length': 1024, 'qwen3.attention.head_count': 16,
                       'qwen3.attention.head_count_kv': 8, 'qwen3.rope.freq_base': 1e6}.items():
        if meta[key] != value:
            raise ValueError(f'Unsupported architecture: {key}')
    parity = []
    with torch.no_grad():
        for probe in probes:
            it = items[probe['item']]
            lower = hidden(w, pad([it], device, True), stop=first)
            exact = final(w, hidden(w, None, x=lower, start=first))[0, -1].cpu().numpy()
            cached = final(w, hidden(w, None, x=lower.half().float(), start=first))[0, -1].cpu().numpy()
            ref = np.array(probe.pop('reference'))
            cosine = float(exact @ ref / np.linalg.norm(exact) / np.linalg.norm(ref))
            matrix = w['output.weight'][ids].cpu().numpy()
            error = float(np.abs(matrix @ (exact - ref)).max())
            cache_error = float(np.abs(matrix @ (exact - cached)).max())
            if cosine < .999 or error > .2 or cache_error > .05:
                raise ValueError(f'Forward/cache parity failed: {cosine}, {error}, {cache_error}')
            parity.append(probe | dict(cosine=cosine, max_verdict_error=error, max_cache_verdict_error=cache_error))
    (out / 'parity.json').write_text(json.dumps(parity, indent=2) + '\n')
    offsets = np.cumsum([0, *[len(it['tokens']) for it in items]], dtype=np.int64)
    np.save(out / 'offsets.npy', offsets)
    cache = np.memmap(out / 'lower.f16', dtype=np.float16, mode='w+', shape=(int(offsets[-1]), 1024))
    vectors = np.empty((len(items), 1024), dtype=np.float32)
    other = np.full(len(items), np.nan, dtype=np.float32)
    anchors, anchor_other, anchor_choice = [], [], []
    order = sorted(range(len(items)), key=lambda j: len(items[j]['tokens']))
    started = time.monotonic()
    with torch.no_grad():
        for start in range(0, len(order), 12):
            inds = order[start:start + 12]; group = [items[j] for j in inds]
            lower = hidden(w, pad(group, device), stop=first)
            for i, j in enumerate(inds):
                cache[offsets[j]:offsets[j + 1]] = lower[i, :len(items[j]['tokens'])].cpu().numpy().astype(np.float16)
            x = hidden(w, None, x=lower.half().float(), start=first)
            bi = torch.arange(len(group), device=device); at = torch.tensor([it['verdict'] for it in group], device=device)
            h = final(w, x[bi, at]); vectors[inds] = h.cpu().numpy()
            val_inds = [i for i, it in enumerate(group) if it['split'] == 'validation']
            if val_inds:
                logits = h[val_inds] @ w['output.weight'].T
                logits[:, ids] = -torch.inf
                other[[inds[i] for i in val_inds]] = logits.max(-1).values.cpu().numpy()
            for i, j in enumerate(inds):
                it = items[j]
                if it['split'] != 'train' or j % 12:
                    continue
                positions = [k for k in range(it['end'], len(it['tokens'])) if k != it['verdict']]
                h = final(w, x[i, positions])
                logits = h @ w['output.weight'].T
                anchor_choice.extend(logits.argmax(-1).cpu().tolist())
                logits[:, ids] = -torch.inf
                anchor_other.extend(logits.max(-1).values.cpu().tolist())
                anchors.extend(h.cpu().numpy())
            if (start // 12 + 1) % 50 == 0:
                print('Encoded', min(start + 12, len(items)), '/', len(items), 'seconds', round(time.monotonic() - started), flush=True)
                if device == 'mps':
                    torch.mps.empty_cache()
    cache.flush()
    np.savez(out / 'features.npz', vectors=vectors, other=other, anchors=np.array(anchors),
             anchor_other=np.array(anchor_other), anchor_choice=np.array(anchor_choice))
    (out / 'source.json').write_text(json.dumps(dict(model=BASE, path=str(model), sha256=p.sha(model),
                                                    counts=dict(Counter(it['source'] + ':' + it['split'] for it in items)),
                                                    cache_bytes=cache.nbytes, first=first), indent=2) + '\n')
    print('Prepared features and cache', cache.nbytes, 'bytes', flush=True)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root', type=Path, default=Path.cwd())
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--first', type=int, default=20)
    a = ap.parse_args()
    prepare(a.root, a.out, a.first)
