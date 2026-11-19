"""Freeze a validation-selected local candidate before either historical test."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import time
import urllib.request

from evaluate_v3 import model_info
import evaluate_v3
import v3_protocol as p


def freeze(root, artifact, chosen, tag, validation_files, comparators):
    items, audit = p.load(root)
    known = {m['name'] for m in json.load(urllib.request.urlopen('http://127.0.0.1:11434/api/tags'))['models']}
    if tag in known:
        raise ValueError('Use a fresh final v3 tag')
    if any('test' in path.name for path in validation_files):
        raise ValueError('Selection evidence must be validation only')
    evidence = {}; matched_candidate = False
    for path in validation_files:
        provenance_path = path.with_name(path.name.replace('.summary.json', '.provenance.json'))
        provenance = json.loads(provenance_path.read_text())
        if provenance['split'] != 'validation' or provenance['data'] != audit['hashes']:
            raise ValueError('Validation provenance differs')
        matched_candidate |= provenance['model']['gguf_sha256'] == p.sha(chosen / 'candidate.gguf')
        evidence[str(path)] = dict(sha256=p.sha(path), provenance_sha256=p.sha(provenance_path), summary=json.loads(path.read_text()))
    if not matched_candidate:
        raise ValueError('Chosen weights lack matching CLI validation evidence')
    final_dir = artifact / 'final'
    final_dir.mkdir()
    shutil.copyfile(chosen / 'candidate.gguf', final_dir / 'candidate.gguf')
    (final_dir / 'Modelfile').write_text(p.definition('./candidate.gguf'))
    subprocess.run(['ollama', 'create', tag, '-f', str(final_dir / 'Modelfile')], check=True,
                   env=dict(os.environ, OLLAMA_HOST='127.0.0.1:11434'))
    tags = [*comparators, tag]
    models = {name: model_info(name) for name in tags}
    manifest = dict(frozen_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), chosen=str(chosen), selected_tag=tag,
                    selected_gguf_sha256=p.sha(final_dir / 'candidate.gguf'), models=models, data=audit['hashes'],
                    scope_contract=p.SCOPES, settings=p.SETTINGS, template_sha256=p.sha(p.TEMPLATE),
                    evaluator_sha256=p.sha(evaluate_v3.__file__), protocol_sha256=p.sha(p.__file__),
                    validation_evidence=evidence, selection=p.selection.__doc__,
                    historical_test_reuse='Both test partitions have been used in previous experiments. This run evaluates each once after freeze, not a newly untouched estimate.')
    with (artifact / 'freeze.json').open('x') as f:
        json.dump(manifest, f, indent=2); f.write('\n')
    print('Frozen', tag, manifest['selected_gguf_sha256'], flush=True)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root', type=Path, default=Path.cwd())
    ap.add_argument('--artifact', type=Path, required=True)
    ap.add_argument('--chosen', type=Path, required=True)
    ap.add_argument('--tag', required=True)
    ap.add_argument('--validation-summary', type=Path, action='append', required=True)
    ap.add_argument('--comparator', action='append', required=True)
    a = ap.parse_args()
    freeze(a.root, a.artifact, a.chosen, a.tag, a.validation_summary, a.comparator)
