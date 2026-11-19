"""First-attempt Ollama CLI evaluation of the frozen v3 scoped contract."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import csv
import json
import os
from pathlib import Path
import re
import subprocess
import time

from tune import ollama, embedding_server
from v3_export import native_template
import v3_protocol as p


def model_info(model):
    show = ollama('/api/show', {'model': model})
    definition = show['modelfile']
    source = Path(re.search(r'^FROM[ \t]+([^\r\n]+)', definition, re.M)[1].strip().strip('"'))
    quoted = re.search(r'^TEMPLATE[ \t]+(?P<quote>"""|")(?P<text>.*?)(?P=quote)[ \t]*\r?$', definition, re.M | re.S)
    if not quoted or quoted['text'].replace('\r\n', '\n') != p.TEMPLATE.read_text():
        raise ValueError('Model template differs from the specified contract')
    if show['template'] != native_template(len(show['template'].encode())):
        raise ValueError('Native Jinja template differs from the specified contract')
    for k, v in p.SETTINGS.items():
        if not re.search(rf'^PARAMETER {k}\s+{v}\s*$', definition, re.M):
            raise ValueError(f'Model setting differs: {k}')
    return dict(model=model, path=str(source), gguf_sha256=p.sha(source), template_sha256=p.sha(p.TEMPLATE),
                settings=p.SETTINGS, definition=definition)


def evaluate(root, model, split, output, workers=4, freeze=None):
    items, audit = p.load(root)
    probes = [next(it for it in items if it['source'] == source and it['split'] == 'train') for source in ('single', 'multi')]
    items = [it for it in items if it['split'] == split]
    info = model_info(model)
    provenance = dict(model=info, data=audit['hashes'], evaluator_sha256=p.sha(__file__),
                      protocol_sha256=p.sha(p.__file__), split=split, workers=workers,
                      timeout_seconds=120, attempts=1, started_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()))
    if split == 'test':
        if not freeze:
            raise ValueError('Test requires a pre-existing freeze manifest')
        f = json.loads(Path(freeze).read_text())
        for key in ('evaluator_sha256', 'protocol_sha256', 'data'):
            if provenance[key] != f[key]:
                raise ValueError(f'Frozen {key} differs')
        if info['gguf_sha256'] != f['models'][model]['gguf_sha256'] or info['template_sha256'] != f['template_sha256']:
            raise ValueError('Frozen model differs')
        if info['settings'] != f['settings']:
            raise ValueError('Frozen settings differ')
    output.parent.mkdir(parents=True, exist_ok=True)
    raw = output.with_suffix('.responses.jsonl')
    meta = output.with_suffix('.provenance.json')
    # A partial run is retained and never silently retried or overwritten.
    for path in (output, raw, meta, output.with_suffix('.summary.json')):
        if path.exists():
            raise FileExistsError(path)
    parity = []
    with embedding_server('/Applications/Ollama.app/Contents/Resources/llama-server', Path(info['path'])) as request:
        for it in probes:
            text = p.prompt(p.turns(it['row']), it['scope'])
            expected = request('/tokenize', {'content': p.TEMPLATE.read_text().replace('{{ .Prompt }}', text),
                                            'add_special': False, 'parse_special': True})['tokens']
            actual = ollama('/api/generate', {'model': model, 'prompt': text, 'stream': False,
                                              'options': dict(p.SETTINGS, num_predict=1)})
            if actual.get('eval_count') != 1 or actual.get('context', [])[:-1] != expected:
                raise ValueError('Installed model prompt token parity failed')
            parity.append(dict(scope=it['scope'], tokens=len(expected),
                               token_sha256=__import__('hashlib').sha256(json.dumps(expected).encode()).hexdigest()))
        maximum = 0
        for it in items:
            rendered = p.TEMPLATE.read_text().replace('{{ .Prompt }}', p.prompt(p.turns(it['row']), it['scope']))
            length = len(request('/tokenize', {'content': rendered, 'add_special': False, 'parse_special': True})['tokens'])
            maximum = max(maximum, length)
            if length + p.SETTINGS['num_predict'] > p.SETTINGS['num_ctx']:
                raise ValueError('Conversation would be truncated by the fixed context window')
    provenance['train_probe_parity'] = parity
    provenance['maximum_prompt_tokens'] = maximum
    meta.write_text(json.dumps(provenance, indent=2) + '\n')

    def attempt(it):
        text = p.prompt(p.turns(it['row']), it['scope'])
        start = time.monotonic()
        record = dict(source=it['source'], index=it['index'], request_id=it['request_id'],
                      prompt_sha256=__import__('hashlib').sha256(text.encode()).hexdigest())
        try:
            r = subprocess.run(['ollama', 'run', model, text], stdin=subprocess.DEVNULL,
                               capture_output=True, text=True, timeout=120,
                               env=dict(os.environ, OLLAMA_HOST='127.0.0.1:11434', OLLAMA_NOHISTORY='1'))
            record.update(stdout=r.stdout, stderr=r.stderr, returncode=r.returncode,
                          verdict=p.parse(r.stdout) if r.returncode == 0 else 'cli_error')
        except subprocess.TimeoutExpired as e:
            record.update(stdout=(e.stdout or b'').decode(errors='replace') if isinstance(e.stdout, bytes) else e.stdout or '',
                          stderr='', returncode=None, verdict='timeout')
        except OSError as e:
            record.update(stdout='', stderr=str(e), returncode=None, verdict='cli_error')
        record['seconds'] = time.monotonic() - start
        return record

    votes = []
    with output.open('x', newline='') as out, raw.open('x') as responses, ThreadPoolExecutor(workers) as pool:
        fields = ('source', 'index', 'request_id', 'split', 'scope', 'label', 'verdict', 'correct', 'correct_binary')
        writer = csv.DictWriter(out, fields, delimiter='\t', lineterminator='\n')
        writer.writeheader()
        for n, (it, record) in enumerate(zip(items, pool.map(attempt, items)), 1):
            v = record['verdict']; valid = v in p.VERDICTS
            writer.writerow(dict(source=it['source'], index=it['index'], request_id=it['request_id'], split=split,
                                 scope=it['scope'], label=it['row'].get('consensus_rating', it['row']['is_safe']),
                                 verdict=v, correct=int(valid and it['mask'][p.VERDICTS.index(v)]),
                                 correct_binary=int(valid and (v == 'safe') == it['mask'][0])))
            responses.write(json.dumps(record) + '\n'); responses.flush(); out.flush()
            votes.append(v)
            if n % 200 == 0:
                print(model, split, f'{n}/{len(items)}', flush=True)
    result = p.summary(items, votes)
    output.with_suffix('.summary.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result), flush=True)
    return result


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root', type=Path, default=Path.cwd())
    ap.add_argument('--model', required=True)
    ap.add_argument('--split', choices=('validation', 'test'), required=True)
    ap.add_argument('--output', required=True, type=Path)
    ap.add_argument('--workers', type=int, default=4)
    ap.add_argument('--freeze', type=Path)
    a = ap.parse_args()
    evaluate(a.root, a.model, a.split, a.output, a.workers, a.freeze)
