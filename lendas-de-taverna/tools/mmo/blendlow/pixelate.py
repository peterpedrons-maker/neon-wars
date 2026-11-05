"""Converte quadros RGBA renderizados do modelo 3D em pixel art: recorta, reduz, quantiza numa paleta única e adiciona contorno escuro.
Uso: python3 pixelate.py <pasta> <prefixo> <altura_px> <ncores> <saida_prefixo>"""
import sys,glob
import numpy as np
from PIL import Image
pasta,pref,H,NC,out=sys.argv[1],sys.argv[2],int(sys.argv[3]),int(sys.argv[4]),sys.argv[5]
fs=sorted(glob.glob(f'{pasta}/{pref}_*.png'));ims=[Image.open(f).convert('RGBA') for f in fs]
bb=[im.getchannel('A').point(lambda v:255 if v>20 else 0).getbbox() for im in ims]
x0=min(b[0] for b in bb);y0=min(b[1] for b in bb);x1=max(b[2] for b in bb);y1=max(b[3] for b in bb)
pad=6;box=(x0-pad,y0-pad,x1+pad,y1+pad);w0,h0=box[2]-box[0],box[3]-box[1];sc=H/h0;W=max(1,round(w0*sc))
small=[]
for im in ims:
    c=im.crop(box);a=np.array(c).astype(float);al=a[:,:,3:4]/255.0
    pm=Image.fromarray((a[:,:,:3]*al).astype('uint8'));aa=Image.fromarray(a[:,:,3].astype('uint8'))
    pm=pm.resize((W,H),Image.BOX);aa=aa.resize((W,H),Image.BOX)
    arr=np.array(pm).astype(float);ar=np.array(aa).astype(float)/255.0
    rgb=np.where(ar[:,:,None]>.05,arr/np.maximum(ar[:,:,None],.05),0).clip(0,255)
    small.append((rgb,ar>=.5))
cat=np.concatenate([r[m] for r,m in small]).astype('uint8').reshape(-1,1,3)
pal=Image.fromarray(cat).quantize(NC,method=Image.Quantize.MEDIANCUT)
P=np.array(pal.getpalette()[:NC*3]).reshape(-1,3).astype(float)
OUTL=np.array([22,14,26])
res=[]
for i,(rgb,m) in enumerate(small):
    idx=((rgb[:,:,None,:]-P[None,None,:,:])**2).sum(-1).argmin(-1);col=P[idx]
    mm=np.pad(m,1);d=np.zeros_like(mm)
    for dy,dx in((-1,0),(1,0),(0,-1),(0,1)):d|=np.roll(np.roll(mm,dy,0),dx,1)
    ol=d&~mm;ol=ol[1:-1,1:-1]
    img=np.zeros((H,W,4),dtype='uint8');img[m,:3]=col[m];img[m,3]=255
    # contorno 1px fora; precisa de 1px de folga
    big=np.zeros((H+2,W+2,4),dtype='uint8');big[1:-1,1:-1]=img
    mb=np.pad(m,1);db=np.zeros_like(mb)
    for dy,dx in((-1,0),(1,0),(0,-1),(0,1)):db|=np.roll(np.roll(mb,dy,0),dx,1)
    o=db&~mb;big[o,:3]=OUTL;big[o,3]=255
    res.append(Image.fromarray(big))
for i,r in enumerate(res):r.save(f'{out}_{i:03d}.png')
print(len(res),'quadros',res[0].size,'paleta',NC)
