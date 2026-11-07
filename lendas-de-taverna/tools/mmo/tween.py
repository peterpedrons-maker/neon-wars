"""Gera quadros intermediários entre dois sprites (fluxo óptico + mistura), mantendo pixels nítidos: tween(A,B,t)."""
import numpy as np,cv2
from PIL import Image
def _canvas(frames,pad=10):
    bbs=[f.getchannel('A').getbbox() for f in frames];W=max(b[2]-b[0] for b in bbs)+2*pad;H=max(b[3]-b[1] for b in bbs)+2*pad;return W,H,bbs
def center(f,W,H,bb,anchor=None):
    c=Image.new('RGBA',(W,H),(0,0,0,0));t=f.crop(bb);c.alpha_composite(t,((W-t.width)//2,(H-t.height)//2));return c
def _flow(a,b):
    ga=cv2.cvtColor(a[:,:,:3],cv2.COLOR_RGB2GRAY);gb=cv2.cvtColor(b[:,:,:3],cv2.COLOR_RGB2GRAY)
    ga=np.where(a[:,:,3]>0,ga,0).astype('uint8');gb=np.where(b[:,:,3]>0,gb,0).astype('uint8')
    d=cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM);return d.calc(ga,gb,None)
def _warp(img,flow,t):
    h,w=img.shape[:2];gx,gy=np.meshgrid(np.arange(w),np.arange(h));mx=(gx-flow[:,:,0]*t).astype('float32');my=(gy-flow[:,:,1]*t).astype('float32')
    pm=img.astype('float32').copy();pm[:,:,:3]*=pm[:,:,3:4]/255.0
    out=cv2.remap(pm,mx,my,cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT,borderValue=(0,0,0,0));return out
def tween(A,B,t,pos_a=(0,0),pos_b=(0,0)):
    a=np.array(A);b=np.array(B);fab=_flow(a,b);fba=_flow(b,a)
    wa=_warp(a,fab,t);wb=_warp(b,fba,1-t)
    al=(1-t)*wa[:,:,3]+t*wb[:,:,3]
    # cor vem do quadro mais próximo no tempo (evita cores fantasmas); o outro só preenche onde o primeiro não tem pixel
    pa,pb=(wa,wb) if t<.5 else (wb,wa)
    cov=np.maximum(pa[:,:,3],1)
    rgb_a=pa[:,:,:3]/(cov[:,:,None]/255.0);rgb_b=pb[:,:,:3]/(np.maximum(pb[:,:,3],1)[:,:,None]/255.0)
    rgb=np.where((pa[:,:,3]>110)[:,:,None],rgb_a,rgb_b)
    out=np.zeros_like(a,dtype='float32');m=al>110
    out[m,:3]=rgb[m]
    out[:,:,3]=np.where(m,255,0);out=np.clip(out,0,255).astype('uint8')
    # paleta: cores mais próximas das duas folhas (mantém aparência de pixel art)
    src=np.concatenate([a[a[:,:,3]>0][:,:3],b[b[:,:,3]>0][:,:3]]);from PIL import Image as I
    pal=I.fromarray(src.reshape(-1,1,3)).quantize(28,method=I.Quantize.MEDIANCUT);P=np.array(pal.getpalette()[:28*3]).reshape(-1,3).astype(float)
    ys,xs=np.where(out[:,:,3]>0);px=out[ys,xs,:3].astype(float);idx=((px[:,None,:]-P[None])**2).sum(-1).argmin(1);out[ys,xs,:3]=P[idx].astype('uint8')
    return Image.fromarray(out,'RGBA')
def interpolate(frames,n_between=1,loop=False):
    """frames alinhados a um canvas comum; devolve a lista com n quadros novos entre cada par"""
    W,H,bbs=_canvas(frames);C=[center(f,W,H,bb) for f,bb in zip(frames,bbs)];out=[]
    for i in range(len(C)-(0 if loop else 1)):
        a,b=C[i],C[(i+1)%len(C)];out.append(a)
        for k in range(1,n_between+1):out.append(tween(a,b,k/(n_between+1)))
    if not loop:out.append(C[-1])
    return out
