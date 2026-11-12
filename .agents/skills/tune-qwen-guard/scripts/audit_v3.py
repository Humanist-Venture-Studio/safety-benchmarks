"""Recount retained first attempts and verify v3's saved GGUF byte boundaries.

This does not generate predictions or fit a model. It checks existing artifacts.
"""
import argparse
from collections import Counter
import csv
import json
from pathlib import Path
import re
import urllib.request

from gguf import GGUFReader
import numpy as np
import v3_protocol as p
from v3_export import native_template


def independent_vote(record):
    if record['returncode'] != 0:
        if record['verdict'] not in ('timeout', 'cli_error'):
            raise ValueError('Failed command counted as a verdict')
        return record['verdict']
    lines = record['stdout'].strip().splitlines()
    match = re.fullmatch(r'Safety:[ \t]*(Safe|Unsafe|Controversial)[ \t]*', lines[0], re.I) if lines else None
    if not match or sum(bool(re.match(r'\s*Safety:', line, re.I)) for line in lines) != 1:
        return 'invalid'
    return match[1].lower()


def tensors_identical(source, target):
    a, b = GGUFReader(source), GGUFReader(target)
    if [(t.name, t.tensor_type, t.shape.tolist()) for t in a.tensors] != [(t.name, t.tensor_type, t.shape.tolist()) for t in b.tensors]:
        raise ValueError('GGUF tensor structure differs')
    return [x.name for x, y in zip(a.tensors, b.tensors) if not np.array_equal(x.data, y.data)]


def audit(root, artifact, output):
    items, split_audit = p.load(root)
    lookup = {(it['source'], it['index']): it for it in items}
    recount = {}
    for path in sorted((artifact / 'results').glob('*.tsv')):
        rows = p.read(path)
        provenance = json.loads(path.with_suffix('.provenance.json').read_text())
        if provenance['data'] != split_audit['hashes']:
            raise ValueError('Results data provenance differs')
        split = provenance['split']
        expected = {(it['source'], it['index']) for it in items if it['split'] == split}
        keys = [(r['source'], int(r['index'])) for r in rows]
        if len(keys) != len(expected) or set(keys) != expected:
            raise ValueError(f'Incomplete or duplicate results: {path}')
        raw_path = path.with_suffix('.responses.jsonl')
        raw = [json.loads(line) for line in raw_path.read_text().splitlines()]
        if len(raw) != len(rows):
            raise ValueError('Raw attempt count differs')
        votes, ordered = [], []
        format_errors = Counter()
        for key, row, record in zip(keys, rows, raw):
            it = lookup[key]
            if key != (record['source'], record['index']) or row['request_id'] != it['request_id'] or record['request_id'] != it['request_id']:
                raise ValueError('Result identity differs')
            label = it['row']['is_safe'] if it['source'] == 'single' else it['row']['consensus_rating']
            if (row['scope'], row['split'], row['label']) != (it['scope'], split, label):
                raise ValueError('Result target or scope differs')
            prompt_hash = __import__('hashlib').sha256(p.prompt(p.turns(it['row']), it['scope']).encode()).hexdigest()
            if prompt_hash != record['prompt_sha256']:
                raise ValueError('Evaluated prompt differs')
            vote = independent_vote(record)
            if vote != row['verdict'] or vote != record['verdict']:
                raise ValueError('Stored verdict disagrees with raw response')
            valid = vote in p.VERDICTS
            exact = valid and it['mask'][p.VERDICTS.index(vote)]
            binary = valid and (vote == 'safe') == it['mask'][0]
            if (int(row['correct']), int(row['correct_binary'])) != (int(exact), int(binary)):
                raise ValueError('Stored correctness differs')
            lines = record['stdout'].strip().splitlines()
            if valid and (len(lines) < 2 or not re.match(r'^Categories:\s*\S', lines[1])):
                format_errors[it['source']] += 1
            votes.append(vote); ordered.append(it)
        summary = p.summary(ordered, votes)
        if summary != json.loads(path.with_suffix('.summary.json').read_text()):
            raise ValueError('Reported summary differs from per-row recount')
        recount[path.name] = dict(summary=summary, category_line_syntax_errors=dict(format_errors),
                                 results_sha256=p.sha(path), responses_sha256=p.sha(raw_path))
    for name in ('base', 'v2', 'single'):
        directory = artifact / 'comparators' / name
        source = json.loads((directory / 'source.json').read_text())
        if p.sha(source['model_path']) != source['gguf_sha256'] or tensors_identical(source['model_path'], directory / 'scoped.gguf'):
            raise ValueError('Comparator weights changed')
    freeze = json.loads((artifact / 'freeze.json').read_text())
    final_path = artifact / 'final/candidate.gguf'
    if p.sha(final_path) != freeze['selected_gguf_sha256']:
        raise ValueError('Final weights changed after freeze')
    base = Path(json.loads((artifact / 'comparators/base/source.json').read_text())['model_path'])
    a, b = GGUFReader(base), GGUFReader(final_path)
    changed = tensors_identical(base, final_path)
    allowed = {f'blk.{i}.{part}.weight' for i in range(20, 28) for part in ('attn_q', 'attn_v', 'attn_output', 'ffn_down')} | {'output.weight'}
    if not set(changed) <= allowed:
        raise ValueError(f'Unexpected tensor changes: {set(changed) - allowed}')
    ids = json.loads((artifact / 'prepared/tokens.json').read_text())['ids']
    ah = next(t for t in a.tensors if t.name == 'output.weight')
    bh = next(t for t in b.tensors if t.name == 'output.weight')
    changed_rows = np.flatnonzero(np.any(ah.data != bh.data, axis=1)).tolist()
    if not set(changed_rows) <= set(ids):
        raise ValueError('Non-verdict output weights changed')
    field = b.fields['tokenizer.chat_template']
    part = field.parts[field.data[0]]
    offset = int(part.__array_interface__['data'][0] - b.data.__array_interface__['data'][0])
    if part.tobytes().decode() != native_template(part.nbytes):
        raise ValueError('Native template differs')
    intervals = sorted([(offset, offset + part.nbytes), *[(int(t.data_offset), int(t.data_offset) + t.data.nbytes) for t in a.tensors]])
    if a.data.size != b.data.size:
        raise ValueError('GGUF size differs')
    previous = 0
    for start, end in intervals + [(a.data.size, a.data.size)]:
        if not np.array_equal(a.data[previous:start], b.data[previous:start]):
            raise ValueError('Unapproved metadata or padding changed')
        previous = end
    before = {m['name']: m['digest'] for m in json.loads((artifact / 'models-before.json').read_text())['models']}
    after = {m['name']: m['digest'] for m in json.load(urllib.request.urlopen('http://127.0.0.1:11434/api/tags'))['models']}
    if any(after.get(name) != digest for name, digest in before.items()):
        raise ValueError('An existing model tag changed or disappeared')
    result = dict(recount=recount, changed_tensors=changed, changed_output_rows=changed_rows,
                  unchanged_existing_tags=before, comparator_tensors_unchanged=True,
                  metadata_change_only='tokenizer.chat_template; fixed byte length', split_audit=split_audit)
    with output.open('x') as f:
        json.dump(result, f, indent=2); f.write('\n')
    print('Artifact audit passed:', len(recount), 'result files;', len(changed), 'changed tensors; original tags intact')


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root', type=Path, default=Path.cwd())
    ap.add_argument('--artifact', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    a = ap.parse_args()
    audit(a.root, a.artifact, a.output)
