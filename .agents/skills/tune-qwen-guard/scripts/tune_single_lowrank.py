"""Single-turn-only, paired rank-12 fit from the installed Sileader GGUF.

Uses benchmark.py's exact prompt/split and Sileader's own template; only train
and validation rows are encoded. Stage 1 fits the last six blocks; stage 2 adds
even blocks 12..20, retains stage 1 and adds a paired ranking loss. Every
checkpoint is merged into the original quantization types (quantize.py) and
selected on quantized validation logits; each stage's best is exported to
OUT/stage1 and OUT/stage2. Finalists must separately pass benchmark.py via the
Ollama CLI (evaluate_cli.py). OUT must not exist yet.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import random
import re
import shutil
import time
from collections import defaultdict
import numpy as np
import torch
import torch.nn.functional as F
from gguf import GGUFReader, dequantize
from benchmark import load_cases, prompt
from tune import BASE, VERDICTS, embedding_server, ollama
from qwen_torch import hidden, final
from quantize import pack

BUNDLED_SERVER = Path('/Applications/Ollama.app/Contents/Resources/llama-server')
PARTS = ('attn_q', 'attn_v', 'attn_output', 'ffn_down')

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def prepare(args, model, template, cases):
    cache = args.out / 'tokens.json'
    if cache.exists(): raise FileExistsError(cache)
    result = []
    with embedding_server(args.llama_server, model) as request:
        def tok(s):
            return request('/tokenize', {'content':s,'add_special':False,'parse_special':True})['tokens']
        ids = [tok(v)[0] for v in VERDICTS]
        assert len(tok(VERDICTS[0])) == len(tok(VERDICTS[1])) == 1 and len(set(ids)) == 3
        for i,(split,row) in enumerate(cases):
            text = template.replace('{{ .Prompt }}', prompt(row))
            head, query = tok(text), tok(text+'Safety:')
            if i == 0:
                probe=ollama('/api/generate', {'model':BASE,'prompt':prompt(row),'stream':False,
                                             'options':{'num_predict':1,'temperature':0}})
                assert probe.get('eval_count') == 1 and probe.get('context',[])[:-1] == head, 'Prompt token mismatch'
                print('Ollama prompt token check passed',flush=True)
            # Binary targets do not supply a semantic Unsafe/Controversial label.
            # Both continuations are valid anchors; deterministic alternating selection.
            word = 'Safe' if row['is_safe']=='1' else ('Unsafe' if i%4<2 else 'Controversial')
            full = tok(text+'Safety: '+word+'\nCategories:' + (' None' if word=='Safe' else ''))
            assert query[:len(head)]==head and full[:len(query)]==query
            item={'split':split,'request_id':row['request_id'],'tokens':full,'end':len(head)-1,
                  'verdict':len(query)-1,'safe':row['is_safe']=='1'}
            if i < 3:
                item['reference']=np.asarray(request('/embedding',{'content':query,'embd_normalize':-1})[0]['embedding']).reshape(-1).tolist()
            result.append(item)
    cache.write_text(json.dumps({'ids':ids,'items':result}))
    return ids,result

def pad(items,device,query=False):
    rows=[it['tokens'][:it['verdict']+1] if query else it['tokens'] for it in items]
    width=max(map(len,rows))
    return torch.tensor([r+[0]*(width-len(r)) for r in rows],device=device)

def logits(w,delta,items,ids,device,batch=24):
    order=sorted(range(len(items)),key=lambda j:items[j]['verdict'])
    values=np.empty((len(items),3));stray=np.empty(len(items),bool)
    with torch.no_grad():
        for start in range(0,len(order),batch):
            inds=order[start:start+batch]; group=[items[j] for j in inds]
            x=hidden(w,pad(group,device,True),delta=delta)
            at=torch.tensor([g['verdict'] for g in group],device=device)
            out=final(w,x[torch.arange(len(group),device=device),at]) @ w['output.weight'].T
            values[inds]=out[:,ids].cpu().numpy()
            stray[inds]=(~torch.isin(out.argmax(-1),torch.tensor(ids,device=device))).cpu().numpy()
    labels=np.array([i['safe'] for i in items]); called=values.argmax(-1)==0
    margin=values[:,0]-np.logaddexp(values[:,1],values[:,2])
    return {'correct':int(((called==labels)&~stray).sum()),'rows':len(items),
            'false_safe':int((called&~labels&~stray).sum()),'false_flag':int((~called&labels&~stray).sum()),
            'stray':int(stray.sum()),'loss':float(np.logaddexp(0,margin*np.where(labels,-1,1)).mean())}

def pairs(items,rng,batch):
    groups=defaultdict(list)
    for j,it in enumerate(items):groups[it['request_id']].append(j)
    units=list(groups.values())
    if any(len(g)!=2 or {items[j]['safe'] for j in g}!={True,False} for g in units):
        raise ValueError('Expected paired safe/unsafe rows for each training request')
    rng.shuffle(units)
    chunks=[sorted(units[j:j+batch*20],key=lambda g:max(len(items[k]['tokens']) for k in g))
            for j in range(0,len(units),batch*20)]
    batches=[sum(c[j:j+batch//2],[]) for c in chunks for j in range(0,len(c),batch//2)]
    rng.shuffle(batches)
    return batches

def rounded(w,delta,tensors):
    out=dict(w); encoded={}
    for name,(a,b,scale) in delta.items():
        packed=pack((w[name]+scale*b.detach()@a.detach()).cpu().numpy(),tensors[name])
        encoded[name]=packed
        out[name]=torch.from_numpy(np.array(dequantize(packed,tensors[name].tensor_type))).to(w[name].device)
    return out,encoded

def save_export(args,stage,model,definition,tensors,packed,delta,report):
    target=args.out/f'stage{stage}'
    target.mkdir(exist_ok=True)
    gguf=target/'candidate.gguf'
    shutil.copyfile(model,gguf)
    with gguf.open('r+b') as f:
        for name,data in packed.items():
            f.seek(int(tensors[name].data_offset));f.write(data.tobytes())
    text=re.sub(r'^FROM[^\n]*', 'FROM ./candidate.gguf', definition, count=1, flags=re.M)
    text=re.sub(r'^PARAMETER temperature[^\n]*\n?', '',text,flags=re.M).rstrip()+'\nPARAMETER temperature 0\n'
    (target/'Modelfile').write_text(text)
    torch.save({n:(a.detach().cpu(),b.detach().cpu(),s) for n,(a,b,s) in delta.items()},target/'adapter.pt')
    (target/'selected.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Exported',target,gguf.stat().st_size,'sha256',digest(gguf),flush=True)

def train(args):
    args.out.mkdir()
    torch.set_num_threads(6);torch.manual_seed(args.seed);rng=random.Random(args.seed)
    device='mps' if torch.backends.mps.is_available() else 'cpu'
    definition=ollama('/api/show',{'model':BASE})['modelfile']
    model=Path(re.search(r'^FROM[ \t]+([^\r\n]+)',definition,re.M)[1].strip().strip('"'))
    quote=re.search(r'^TEMPLATE[ \t]+(?P<quote>"""|")(?P<text>.*?)(?P=quote)[ \t]*\r?$',definition,re.M|re.S)
    template=quote['text'].replace('\r\n','\n')
    assert re.findall(r'{{.*?}}',template)==['{{ .Prompt }}']
    cases=[(s,r) for s,r in load_cases(args.data) if s in ('train','validation')]
    ids,items=prepare(args,model,template,cases)
    fit=[it for it in items if it['split']=='train'];val=[it for it in items if it['split']=='validation']
    print('Train',len(fit),'validation',len(val),'max tokens',max(len(it['tokens']) for it in items),flush=True)
    reader=GGUFReader(model);tensors={t.name:t for t in reader.tensors}
    w={t.name:torch.from_numpy(np.array(dequantize(t.data,t.tensor_type),dtype=np.float32)).to(device) for t in reader.tensors}
    # This implementation is only for the checked Qwen3 0.6B architecture.
    for key,value in {'qwen3.block_count':28,'qwen3.embedding_length':1024,'qwen3.attention.head_count':16,
                      'qwen3.attention.head_count_kv':8,'qwen3.rope.freq_base':1e6}.items():
        assert reader.fields[key].contents()==value,(key,reader.fields[key].contents())
    with torch.no_grad():
        for it in items[:3]:
            h=final(w,hidden(w,pad([it],device,True)))[0,-1].cpu().numpy();ref=np.array(it['reference'])
            cosine=float(h@ref/np.linalg.norm(h)/np.linalg.norm(ref))
            print('Forward parity cosine',cosine,'verdict max error',float(np.abs(w['output.weight'][ids].cpu().numpy()@(h-ref)).max()),flush=True)
            assert cosine>0.995,'Forward pass diverges from llama-server'
    baseline=logits(w,None,val,ids,device)
    print('Baseline validation',baseline,flush=True)
    history=[{'stage':0,'step':0,**baseline}]
    delta={};start_time=time.monotonic();step=0
    for stage,blocks,epochs,lr in [(1,range(22,28),args.epochs,args.lr),
                                  (2,sorted(set(range(22,28))|set(range(12,27,2))),args.epochs,args.lr/2)]:
        for i in blocks:
            for part in PARTS:
                name=f'blk.{i}.{part}.weight'
                if name in delta:continue
                h,d=w[name].shape
                a=torch.nn.Parameter(torch.randn(args.rank,d,device=device)/math.sqrt(d));b=torch.nn.Parameter(torch.zeros(h,args.rank,device=device))
                delta[name]=(a,b,args.scale)
        params=[p for a,b,s in delta.values() for p in (a,b)]
        opt=torch.optim.AdamW(params,lr=lr,weight_decay=0.01)
        total=epochs*math.ceil(len(fit)/args.batch)
        schedule=torch.optim.lr_scheduler.OneCycleLR(opt,max_lr=lr,total_steps=total,pct_start=.1)
        first=min(blocks);best=None;best_state=None
        for epoch in range(epochs):
            batches=pairs(fit,rng,args.batch)
            for bi,group in enumerate(batches):
                batch=[fit[j] for j in group];tokens=pad(batch,device)
                with torch.no_grad():
                    lower=hidden(w,tokens,stop=first)
                    teacher=hidden(w,None,start=first,x=lower)
                tuned=hidden(w,None,start=first,x=lower,delta=delta)
                batch_i=torch.arange(len(batch),device=device);at=torch.tensor([it['verdict'] for it in batch],device=device)
                out=final(w,tuned[batch_i,at])@w['output.weight'][ids].T
                margin=out[:,0]-torch.logsumexp(out[:,1:],-1)
                safe=torch.tensor([it['safe'] for it in batch],device=device)
                loss_v=F.softplus(margin*torch.where(safe,-1.,1.)).mean()
                # Match the full vocabulary before/after the verdict; this protects
                # Safety, :, the Controversial suffix and Categories without new labels.
                rows=[];positions=[]
                for j,it in enumerate(batch):
                    for pos in range(it['end'],len(it['tokens'])):
                        if pos!=it['verdict']:rows.append(j);positions.append(pos)
                ri=torch.tensor(rows,device=device);pi=torch.tensor(positions,device=device)
                logp=F.log_softmax(final(w,tuned[ri,pi])@w['output.weight'].T,-1)
                with torch.no_grad():ref=F.log_softmax(final(w,teacher[ri,pi])@w['output.weight'].T,-1)
                loss_f=F.kl_div(logp,ref,log_target=True,reduction='batchmean')
                rank=[]
                for j in range(0,len(batch),2):
                    sign=1 if batch[j]['safe'] else -1
                    rank.append(F.softplus(1-sign*(margin[j]-margin[j+1])))
                loss_r=torch.stack(rank).mean()
                loss=loss_v+args.format_weight*loss_f+(args.rank_weight*loss_r if stage==2 else 0)
                opt.zero_grad(set_to_none=True);loss.backward();torch.nn.utils.clip_grad_norm_(params,1.0);opt.step();schedule.step();step+=1
                if step%25==0:
                    print('stage',stage,'epoch',epoch+1,'step',step,'loss',round(loss.item(),4),'verdict',round(loss_v.item(),4),
                          'format',round(loss_f.item(),4),'rank',round(loss_r.item(),4),'seconds',round(time.monotonic()-start_time),flush=True)
                if bi+1 in (math.ceil(len(batches)/2),len(batches)):
                    with torch.no_grad():
                        qw,packed=rounded(w,delta,tensors)
                        report={'stage':stage,'epoch':epoch+1,'step':step,**logits(qw,None,val,ids,device)}
                        del qw
                    history.append(report);(args.out/'history.json').write_text(json.dumps(history,indent=2)+'\n')
                    print('Quantized validation',report,flush=True)
                    key=(-report['stray'],report['correct'],-report['loss'])
                    if best is None or key>best:
                        best=key;best_state={n:(a.detach().clone(),b.detach().clone(),s) for n,(a,b,s) in delta.items()}
                        save_export(args,stage,model,definition,tensors,packed,delta,report)
                    del packed
            print('Completed stage',stage,'epoch',epoch+1,flush=True)
        with torch.no_grad():
            for name,(a,b,s) in delta.items():a.copy_(best_state[name][0]);b.copy_(best_state[name][1])
    manifest={'args':{k:str(v) if isinstance(v,Path) else v for k,v in vars(args).items()},'source_sha256':digest(model),
              'data_sha256':digest(args.data),'ids':ids,'history':history,'seconds':time.monotonic()-start_time}
    (args.out/'run.json').write_text(json.dumps(manifest,indent=2)+'\n')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--data',type=Path,required=True);p.add_argument('--out',type=Path,required=True,help='New run directory (refused if it exists)')
    p.add_argument('--llama-server',default=shutil.which('llama-server') or (str(BUNDLED_SERVER) if BUNDLED_SERVER.is_file() else 'llama-server'),
                   help='llama.cpp server used for tokenization and the forward-parity check')
    p.add_argument('--epochs',type=int,default=3);p.add_argument('--batch',type=int,default=16);p.add_argument('--rank',type=int,default=12)
    p.add_argument('--scale',type=float,default=2);p.add_argument('--lr',type=float,default=2e-4);p.add_argument('--format-weight',type=float,default=.5)
    p.add_argument('--rank-weight',type=float,default=.2);p.add_argument('--seed',type=int,default=20261111)
    train(p.parse_args())
