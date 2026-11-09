"""Corta as folhas de IA do Morvath (morvath_src/*.jpg, fundo magenta) em quadros limpos.
Uso: python3 morvath_cut.py <pasta_saida>  -> contato <pasta>/<folha>_contact.png e quadros <folha>_NN.png"""
import sys,os
import numpy as np
from PIL import Image,ImageDraw
import cut_grid as CG
SRC=os.path.join(os.path.dirname(os.path.abspath(__file__)),'morvath_src')
def grid(nc,nr,W,H):return [[(round(W*c/nc),round(H*r/nr),round(W*(c+1)/nc),round(H*(r+1)/nr)) for c in range(nc)] for r in range(nr)]
def rows(ys,xss,W):
    return [[(xs[i],ys[r],xs[i+1],ys[r+1]) for i in range(len(xs)-1)] for r,xs in enumerate(xss)]
SPEC={'iw1':(4,3),'iw2':(4,3),'iw3':(4,3),'walkA':(6,3),'walkB':(6,3),'atkA':(4,3),'atkB':(4,3),'death':(4,3),'slam':(4,3),'roar':'irr','charge':'irr'}
LAB={'death','slam','roar','charge'}
def cells(name,m=7):
    im=Image.open(f'{SRC}/{name}.jpg').convert('RGB');W,H=im.size;sp=SPEC[name]
    if sp=='irr':R=rows([0,283,565,848],[[0,315,632,1264],[0,632,1264],[0,632,1264]],W)
    else:R=grid(sp[0],sp[1],W,H)
    out=[]
    for row in R:
        for (x0,y0,x1,y1) in row:
            cell=im.crop((x0+m,y0+m,x1-m,y1-m))
            if name in LAB:
                a=np.array(cell);h,w=a.shape[:2];box=a[:78]
                lo=(box.max(2)<62);hi=(box.min(2)>200)&(np.arange(w)[None,:]<240)
                box[lo|hi]=(255,0,255);a[:78]=box;cell=Image.fromarray(a)
            k=CG.key(cell);c=np.array(cell).astype(int)
            hole=((np.minimum(c[:,:,0],c[:,:,2])-c[:,:,1])>42)&(c[:,:,2]>105)&(c[:,:,0]>105)
            k[hole,3]=0
            from scipy import ndimage as ND
            lb,nn=ND.label(k[:,:,3]>0)
            if nn:
                sz=ND.sum(k[:,:,3]>0,lb,range(1,nn+1));k[np.isin(lb,[i+1 for i,v in enumerate(sz) if v<600]),3]=0
            a=CG.clean(k);out.append(Image.fromarray(a,'RGBA'))
    return out
if __name__=='__main__':
    o=sys.argv[1];os.makedirs(o,exist_ok=True)
    for n in SPEC:
        fr=cells(n);cw=max(f.width for f in fr);ch=max(f.height for f in fr);cols=6 if n.startswith('walk') else 4 if SPEC[n]!='irr' else 4
        rws=(len(fr)+cols-1)//cols;C=Image.new('RGBA',(cols*cw,rws*ch),(60,70,60,255));d=ImageDraw.Draw(C)
        for i,f in enumerate(fr):
            f.save(f'{o}/{n}_{i:02d}.png');x,y=(i%cols)*cw,(i//cols)*ch;C.alpha_composite(f,(x,y+ch-f.height));d.text((x+4,y+2),f'{n}:{i}',fill=(255,255,0,255))
        C.convert('RGB').save(f'{o}/{n}_contact.png');print(n,len(fr),cw,ch)
