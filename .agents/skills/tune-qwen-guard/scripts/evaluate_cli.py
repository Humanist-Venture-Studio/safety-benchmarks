"""Run the unchanged benchmark evaluator and retain each first CLI response.

The wrapper records responses without changing prompts, timeouts, parsing,
retries or error accounting in benchmark.py. Responses go to OUTPUT with the
suffix .responses.jsonl; neither file may exist yet. The tag's Modelfile must
set PARAMETER temperature 0. The test split also needs a frozen manifest:
{"dataset_sha256": "...", "models": {"<tag>": {"gguf_sha256": "..."}}},
where gguf_sha256 hashes the FROM file in `ollama show <tag> --modelfile`.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import time
import benchmark

p=argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
p.add_argument('--data',required=True,type=Path);p.add_argument('--model',required=True)
p.add_argument('--split',required=True,choices=['validation','test'])
p.add_argument('--output',required=True,type=Path);p.add_argument('--freeze',type=Path,help='Frozen manifest JSON (required for test)')
a=p.parse_args()
raw=a.output.with_suffix('.responses.jsonl')
if raw.exists() or a.output.exists():raise FileExistsError(a.output)
definition=subprocess.check_output(['ollama','show',a.model,'--modelfile'],text=True)
if not re.search(r'^PARAMETER temperature\s+0(?:\.0)?\s*$',definition,re.M):
    raise ValueError('Evaluation tag must set temperature 0')
if a.split=='test':
    if not a.freeze:raise ValueError('Freeze manifest required for test')
    frozen=json.loads(a.freeze.read_text())
    if a.model not in frozen['models']:raise ValueError('Tag not in frozen manifest')
    path=Path(re.search(r'^FROM\s+(.+)$',definition,re.M)[1].strip())
    if hashlib.sha256(path.read_bytes()).hexdigest()!=frozen['models'][a.model]['gguf_sha256']:
        raise ValueError('Model changed after freeze')
    if hashlib.sha256(a.data.read_bytes()).hexdigest()!=frozen['dataset_sha256']:
        raise ValueError('Dataset changed after freeze')
run=subprocess.run;n=0;started=time.monotonic()
with raw.open('x') as stream:
    def record(command,*args,**kwargs):
        global n
        is_reply=command[:2]==['ollama','run'];t=time.monotonic()
        try:
            result=run(command,*args,**kwargs)
        except subprocess.TimeoutExpired:
            if is_reply:
                stream.write(json.dumps({'index':n,'status':'timeout','seconds':time.monotonic()-t})+'\n');stream.flush();n+=1
            raise
        if is_reply:
            stream.write(json.dumps({'index':n,'status':'ok' if result.returncode==0 else 'cli_error',
                                     'stdout':result.stdout,'seconds':time.monotonic()-t})+'\n')
            stream.flush();n+=1
            if n%50==0:print(a.model,a.split,n,'rows',round(time.monotonic()-started),'seconds',flush=True)
        return result
    benchmark.subprocess.run=record
    benchmark.evaluate(a.data,a.model,a.split,a.output)
print('Complete first-attempt responses:',raw,flush=True)
