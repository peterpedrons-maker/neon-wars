import os,sys,numpy as np
from PIL import Image
from scipy import ndimage
import os as _o;A=_o.path.join(_o.path.dirname(_o.path.abspath(__file__)),'..','..','mmo','assets')+'/'
L2=A+'look2/';CH=A+'chars/'
def ld(p):
    return Image.open(p).convert('RGBA') if os.path.exists(p) else None
SK={(249,213,186):0,(228,164,124):1,(204,134,101):2,(153,66,60):3,(250,236,231):4}
BOAR={0:(112,78,62),1:(98,65,53),2:(71,55,48),3:(48,34,32),4:(142,102,82)}
RAT={0:(172,172,182),1:(140,140,152),2:(104,104,118),3:(66,62,76),4:(208,208,218)}
def remap_skin(a,pal):
    out=a.copy()
    for (r,g,b),k in SK.items():
        m=(a[:,:,0]==r)&(a[:,:,1]==g)&(a[:,:,2]==b)&(a[:,:,3]>0);out[:,:,:3][m]=pal[k]
    return out
def gray_head(a):
    """rato: funde a pelagem rosada em ramp cinza pela luminância (mantém contorno escuro, nariz/orelha rosados quando bem rosa)"""
    out=a.copy();rgb=a[:,:,:3].astype(float);al=a[:,:,3]>0
    lum=(rgb[:,:,0]*.3+rgb[:,:,1]*.59+rgb[:,:,2]*.11)
    sat=(rgb.max(2)-rgb.min(2))
    ramp=np.array([[26,24,32],[52,50,62],[84,84,96],[116,116,130],[152,152,166],[190,190,204]],float)
    idx=np.clip(lum/255*5,0,4.999);i0=idx.astype(int);f=(idx-i0)[...,None]
    col=ramp[i0]*(1-f)+ramp[np.minimum(i0+1,5)]*f
    pink=(rgb[:,:,0]>rgb[:,:,1]+40)&(rgb[:,:,0]>150)&(rgb[:,:,2]>100)   # nariz/orelha/rabo rosados: ficam rosa-acinzentado
    pass
    out[:,:,:3][al]=np.clip(col[al],0,255).astype(np.uint8);return out
def frames_iter(w,h,cell):
    for r in range(h//cell):
        for c in range(w//cell):yield r,c
def graft(body,animal_walk,cell,off,gray=False):
    """troca a cabeça do corpo humano pela cabeça do bicho (quadro 0 da caminhada, mesma direção)"""
    W,H=body.size;out=np.array(body);aw=np.array(animal_walk)
    for r,c in frames_iter(W,H,cell):
        y0,x0=r*cell,c*cell;fr=out[y0+off:y0+off+64,x0+off:x0+off+64]
        al=fr[:,:,3]>0
        if not al.any():continue
        ys,xs=np.where(al);top=ys.min()
        row=min(3,r) if H>64 else 2
        row=r if H>64 else 2
        src=aw[row*64:(row+1)*64,0:64]
        sal=src[:,:,3]>0
        if not sal.any():continue
        sys_,sxs=np.where(sal);stop=sys_.min()
        hs=src.copy();hs[stop+17:]=0
        hal=hs[:,:,3]>0
        if not hal.any():continue
        hy,hx=np.where(hal);hcx=hx.mean()
        head_rows=slice(top,top+16)
        sub=al[head_rows];_,hxb=np.where(sub);bcx=hxb.mean() if len(hxb) else 32
        dx=int(round(bcx-hcx));dy=top-stop
        # apaga cabeça humana
        cols=slice(max(0,int(bcx)-9),min(64,int(bcx)+10))
        fr[top:top+16,cols]=0
        # cola cabeça do bicho
        for y in range(64):
            for x in range(64):
                if hs[y,x,3]>0:
                    ty,tx=y+dy,x+dx
                    if 0<=ty<64 and 0<=tx<64:fr[ty,tx]=hs[y,x]
    return Image.fromarray(out,'RGBA')
def over(base,layer):
    if layer is None:return base
    base=base.copy();base.alpha_composite(layer);return base
