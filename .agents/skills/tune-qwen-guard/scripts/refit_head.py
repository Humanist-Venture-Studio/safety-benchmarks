"""Run the skill's verdict-layer fit (tune.py) on an installed low-rank candidate.

BASE is an installed Ollama tag, such as the tune_single_lowrank.py stage that
scored best on CLI validation. Train and validation encodings are kept beside
OUT as OUT.features.npz; no test rows are encoded. The exported Modelfile sets
temperature 0. --penalties replaces tune.fit's L2 penalties (0.4 0.04 0.004);
the fit still keeps the one that scores best on validation. Neither OUT nor its
features file may exist yet.
"""
import argparse
import functools
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
p.add_argument('--penalties',type=float,nargs='+',help="L2 penalties to compare on validation (default: tune.fit's 0.4 0.04 0.004)")
a=p.parse_args();tune.BASE=a.base
if a.penalties:tune.fit=functools.partial(tune.fit,penalties=tuple(a.penalties))
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
