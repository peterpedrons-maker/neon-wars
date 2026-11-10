"""Corta as folhas de IA do Gorgash (gorgash_src/*.jpg, fundo magenta) em quadros limpos; tira a capa dos quadros de idle/caminhada.
Uso: python3 gorgash_cut.py <pasta_saida>  -> <folha>_NN.png e <folha>_contact.png"""
import sys,os
import numpy as np
from PIL import Image,ImageDraw
from scipy import ndimage as ND
import cut_grid as CG
import gorgash_uncape as GU
SRC=os.path.join(os.path.dirname(os.path.abspath(__file__)),'gorgash_src')
SPEC={'iw':(6,3),'atk':(4,3),'death':(4,2),'slam':(4,2),'charge':(4,2),'roar':(4,2)}
def cells(name,m=6):
    im=Image.open(f'{SRC}/{name}.jpg').convert('RGB');W,H=im.size;nc,nr=SPEC[name];out=[]
    for r in range(nr):
        for c in range(nc):
            x0,x1,y0,y1=round(W*c/nc),round(W*(c+1)/nc),round(H*r/nr),round(H*(r+1)/nr)
            cell=im.crop((x0+m,y0+m,x1-m,y1-m))
            if name=='iw' and r>=1:k=GU.uncape(cell,m=m)
            elif name=='iw':k=GU.uncape(cell,m=m)   # idle também tem capa
            else:
                a=np.array(cell);box=a[:46,:62];lo=box.max(2)<70;box[lo]=(255,0,255);a[:46,:62]=box;cell=Image.fromarray(a);k=CG.key(cell)
            c=np.array(cell).astype(int);hole=((np.minimum(c[:,:,0],c[:,:,2])-c[:,:,1])>42)&(c[:,:,2]>105)&(c[:,:,0]>105);k[hole,3]=0
            lb,nn=ND.label(k[:,:,3]>0)
            if nn:
                sz=ND.sum(k[:,:,3]>0,lb,range(1,nn+1));k[np.isin(lb,[i+1 for i,v in enumerate(sz) if v<600]),3]=0
            if name=='iw':   # rótulo I1/W1 (preto) no canto sobrevive ao corte: remove no canto
                k[:60,:70,3]=0;k=CG.clean(k)
            else:k=CG.clean(k)
            out.append(Image.fromarray(k,'RGBA'))
    return out
if __name__=='__main__':
    o=sys.argv[1];os.makedirs(o,exist_ok=True)
    for n,(nc,nr) in SPEC.items():
        fr=cells(n);cw=max(f.width for f in fr);ch=max(f.height for f in fr)
        C=Image.new('RGBA',(nc*cw,nr*ch),(60,70,60,255));d=ImageDraw.Draw(C)
        for i,f in enumerate(fr):
            f.save(f'{o}/g{n}_{i:02d}.png');x,y=(i%nc)*cw,(i//nc)*ch;C.alpha_composite(f,(x,y+ch-f.height));d.text((x+4,y+2),f'{n}:{i}',fill=(255,255,0,255))
        C.convert('RGB').save(f'{o}/g{n}_contact.png');print(n,len(fr),cw,ch)
