"""Re-encode an updated tensor in its original Q4_K or Q6_K type.

For each 256-weight block, pack() rounds the new weights onto the source
block's existing scales and also encodes them with fresh scales, and keeps
whichever decodes with less squared error. The result has the source tensor's
type and byte size. Byte layouts follow gguf 0.19.0's Q4_K/Q6_K decoders. This
is a NumPy encoder, not llama.cpp's importance-weighted quantization optimizer.
"""
import numpy as np
from gguf import dequantize, GGMLQuantizationType
from gguf.quants import Q4_K
from tune import q6_rows

def pack_q4(x):
    g=x.reshape(-1,8,32)
    mins=np.maximum(0,-g.min(-1))
    steps=(g.max(-1)+mins).clip(0)/15
    d=(steps.max(-1)/63).astype('<f2');dm=(mins.max(-1)/63).astype('<f2')
    sc=np.rint(steps/np.where(d==0,1,d).astype(np.float32)[:,None]).clip(0,63).astype(np.uint8)
    mn=np.rint(mins/np.where(dm==0,1,dm).astype(np.float32)[:,None]).clip(0,63).astype(np.uint8)
    scales=np.column_stack((sc[:,:4]|((sc[:,4:]>>4)<<6),mn[:,:4]|((mn[:,4:]>>4)<<6),
                            (sc[:,4:]&15)|((mn[:,4:]&15)<<4)))
    step=d.astype(np.float32)[:,None]*sc;offset=dm.astype(np.float32)[:,None]*mn
    codes=np.rint((g+offset[:,:,None])/np.where(step==0,1,step)[:,:,None]).clip(0,15).astype(np.uint8).reshape(-1,4,2,32)
    qs=(codes[:,:,0]|(codes[:,:,1]<<4)).reshape(-1,128)
    return np.column_stack((d.view(np.uint8).reshape(-1,2),dm.view(np.uint8).reshape(-1,2),scales,qs))

def pack(x,tensor):
    a=np.ascontiguousarray(x,dtype=np.float32)
    typ=tensor.tensor_type
    if typ==GGMLQuantizationType.Q4_K:
        source=tensor.data.reshape(-1,144);fixed=source.copy()
        sc,mn=Q4_K.get_scale_min(source[:,4:16])
        d=np.ascontiguousarray(source[:,:2]).view('<f2').astype(np.float32)
        dm=np.ascontiguousarray(source[:,2:4]).view('<f2').astype(np.float32)
        step=d*sc;offset=dm*mn
        code=np.rint((a.reshape(-1,8,32)+offset[:,:,None])/np.where(step==0,1,step)[:,:,None]).clip(0,15).astype(np.uint8).reshape(-1,4,2,32)
        fixed[:,16:]=(code[:,:,0]|(code[:,:,1]<<4)).reshape(-1,128)
        fresh=pack_q4(a)
    elif typ==GGMLQuantizationType.Q6_K:
        source=tensor.data.reshape(-1,210);fixed=source.copy()
        d=np.ascontiguousarray(source[:,208:]).view('<f2').astype(np.float32)
        scales=source[:,192:208].view(np.int8).astype(np.float32);step=d*scales
        codes=(32+np.rint(a.reshape(-1,16,16)/np.where(step==0,1,step)[:,:,None])).clip(0,63).astype(np.uint8)
        lo=(codes&15).reshape(-1,2,2,64);hi=(codes>>4).reshape(-1,2,4,32)
        fixed[:,:128]=(lo[:,:,0]|(lo[:,:,1]<<4)).reshape(-1,128)
        fixed[:,128:192]=(hi[:,:,0]|(hi[:,:,1]<<2)|(hi[:,:,2]<<4)|(hi[:,:,3]<<6)).reshape(-1,64)
        fresh=q6_rows(a).reshape(-1,210)
    else:raise ValueError(f'Unsupported quantization {typ}')
    target=a.reshape(-1,256)
    ef=((dequantize(fixed,typ).reshape(-1,256)-target)**2).sum(-1)
    en=((dequantize(fresh,typ).reshape(-1,256)-target)**2).sum(-1)
    result=np.where((en<ef)[:,None],fresh,fixed).reshape(tensor.data.shape)
    if result.nbytes!=tensor.data.nbytes:raise ValueError('Quantized size differs')
    return result
