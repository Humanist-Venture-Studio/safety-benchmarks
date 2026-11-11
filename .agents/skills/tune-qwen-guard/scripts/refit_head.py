"""Run the skill's unchanged verdict-layer fit on an installed low-rank candidate.

BASE is an installed Ollama tag, such as the tune_single_lowrank.py stage that
scored best on CLI validation. Train and validation encodings are kept beside
OUT as OUT.features.npz; no test rows are encoded. The exported Modelfile sets
temperature 0. Neither OUT nor its features file may exist yet.
"""
import argparse
from pathlib import Path
import re
import shutil
import numpy as np
import tune
bundled=Path('/Applications/Ollama.app/Contents/Resources/llama-server')
p=argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
p.add_argument('--data',type=Path,required=True);p.add_argument('--base',required=True,help='Installed Ollama tag to refit')
p.add_argument('--out',type=Path,required=True,help='New candidate directory (refused if it exists)')
p.add_argument('--llama-server',default=shutil.which('llama-server') or (str(bundled) if bundled.is_file() else 'llama-server'),
               help='Path to the llama.cpp server executable')
a=p.parse_args();tune.BASE=a.base
features=a.out.parent/(a.out.name+'.features.npz')
for path in (a.out,features):
    if path.exists():raise FileExistsError(f'Choose a new output: {path}')
old=tune.collect

def collect(*args,**kwargs):
    ids,vectors=old(*args,**kwargs)
    with features.open('xb') as stream:np.savez(stream,ids=ids,vectors=vectors)
    return ids,vectors

tune.collect=collect
tune.tune(a.data,a.out,a.llama_server)
p=a.out/'Modelfile';s=p.read_text()
s=re.sub(r'^PARAMETER temperature[^\n]*\n?','',s,flags=re.M)
p.write_text(s.rstrip()+'\nPARAMETER temperature 0\n')
