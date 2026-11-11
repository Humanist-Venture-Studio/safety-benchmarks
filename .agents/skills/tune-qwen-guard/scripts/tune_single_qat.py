"""Quantization-aware variant of tune_single_lowrank.py.

Runs tune_single_lowrank.train unchanged except for two helpers. The forward
pass snaps each tuned tensor to the source GGUF's own Q4_K/Q6_K block grid and
passes the low-rank gradient straight through; export checks that quantize.py
reproduces that grid exactly. Defaults: rank 12, scale 2, two epochs per stage,
learning rate 6e-4, seed 20261112.

BASE is an installed Ollama tag fitted on train rows only, such as this
experiment's refit_head.py candidate; never a historical tag. Output, stages
and checkpoint layout are as in tune_single_lowrank.py. OUT must not exist yet.
"""
import argparse
from pathlib import Path
import re
import numpy as np
import torch
from gguf import GGUFReader, GGMLQuantizationType, dequantize
from gguf.quants import Q4_K
import tune_single_lowrank as fit
from quantize import pack

_grids={}
_hidden=fit.hidden

def grids(tensors,device):
    for name,t in tensors.items():
        if not any(name.endswith('.'+p+'.weight') for p in fit.PARTS):continue
        if int(name.split('.')[1]) not in set(range(22,28))|set(range(12,27,2)):continue
        if t.tensor_type==GGMLQuantizationType.Q4_K:
            blocks=t.data.reshape(-1,144);sc,mn=Q4_K.get_scale_min(blocks[:,4:16])
            d=np.ascontiguousarray(blocks[:,:2]).view('<f2').astype(np.float32)
            dm=np.ascontiguousarray(blocks[:,2:4]).view('<f2').astype(np.float32)
            step=np.repeat(d*sc,32,axis=-1);offset=np.repeat(dm*mn,32,axis=-1);lo,hi=0,15
        elif t.tensor_type==GGMLQuantizationType.Q6_K:
            blocks=t.data.reshape(-1,210)
            d=np.ascontiguousarray(blocks[:,208:]).view('<f2').astype(np.float32)
            sc=blocks[:,192:208].view(np.int8).astype(np.float32)
            step=np.repeat(d*sc,16,axis=-1);offset=np.zeros_like(step);lo,hi=-32,31
        else:raise ValueError('Unexpected tensor type')
        shape=tuple(reversed(t.shape.tolist()))
        _grids[name]=(torch.from_numpy(step.reshape(shape)).to(device),
                      torch.from_numpy(offset.reshape(shape)).to(device),lo,hi)

def quant(name,value):
    step,offset,lo,hi=_grids[name]
    return torch.round((value+offset)/torch.where(step==0,1,step)).clamp(lo,hi)*step-offset

def hidden(w,ids,**kwargs):
    delta=kwargs.get('delta')
    if delta:
        base=dict(w)
        with torch.no_grad():
            for name,(a,b,scale) in delta.items():
                d=scale*b@a
                # The differentiable low-rank path below supplies the STE gradient.
                base[name]=quant(name,w[name]+d)-d
        return _hidden(base,ids,**kwargs)
    return _hidden(w,ids,**kwargs)

def rounded(w,delta,tensors):
    result=dict(w);encoded={}
    for name,(a,b,scale) in delta.items():
        value=quant(name,w[name]+scale*b.detach()@a.detach())
        encoded[name]=pack(value.cpu().numpy(),tensors[name])
        actual=torch.from_numpy(np.array(dequantize(encoded[name],tensors[name].tensor_type))).to(value.device)
        if not torch.allclose(value,actual,atol=1e-7,rtol=0):raise ValueError('QAT/export grids differ')
        result[name]=actual
    return result,encoded

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--data',required=True,type=Path);p.add_argument('--out',required=True,type=Path,help='New run directory (refused if it exists)')
    p.add_argument('--base',required=True,help='Installed Ollama tag to start from (train-only candidate)')
    p.add_argument('--llama-server',default=fit.DEFAULT_SERVER,
                   help='llama.cpp server used for tokenization and the forward-parity check')
    p.add_argument('--stages',type=int,choices=(1,2),default=2,help='2 runs both stages; 1 stops after stage 1')
    p.add_argument('--epochs',type=int,default=2);p.add_argument('--batch',type=int,default=16);p.add_argument('--rank',type=int,default=12)
    p.add_argument('--scale',type=float,default=2);p.add_argument('--lr',type=float,default=6e-4);p.add_argument('--format-weight',type=float,default=.5)
    p.add_argument('--rank-weight',type=float,default=.2);p.add_argument('--seed',type=int,default=20261112)
    a=p.parse_args()
    fit.BASE=a.base
    definition=fit.ollama('/api/show',{'model':a.base})['modelfile']
    model=Path(re.search(r'^FROM\s+(.+)$',definition,re.M)[1].strip())
    reader=GGUFReader(model);tensors={t.name:t for t in reader.tensors}
    grids(tensors,'mps' if torch.backends.mps.is_available() else 'cpu')
    fit.hidden=hidden;fit.rounded=rounded
    fit.train(a)
