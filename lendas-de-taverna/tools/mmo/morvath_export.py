"""Monta o atlas do chefe Morvath (rei esqueleto) a partir das folhas de IA (morvath_src/).
Gera mmo/assets/chars/morvath_atlas.png/json: idle, walk, hurt, attack, slam, charge, roar, death.
Uso: python3 morvath_export.py [escala]"""
import sys,json
import numpy as np
from PIL import Image,ImageOps
import morvath_cut as MC
OUT='../../mmo/assets/chars/'
C={n:MC.cells(n) for n in ('walkA','atkA','death','slam','roar','charge')}
fl=ImageOps.mirror
def bbox(f):return f.getchannel('A').getbbox()
def rot(f,deg):
    """gira em torno do pé (centro da base) para a queda"""
    b=bbox(f);f=f.crop(b);W,H=f.size;pad=Image.new('RGBA',(W*2,H*2),(0,0,0,0));pad.alpha_composite(f,(W//2,H//2))
    return pad.rotate(deg,resample=Image.BICUBIC,center=(W,H+H//2-4))
def build(sc):
    wa,at,de,sl,ro,ch=[C[n] for n in ('walkA','atkA','death','slam','roar','charge')]
    an={'idle':[wa[i] for i in (0,1,2,3,4,3,2,1)],'walk':[wa[i] for i in range(6,18)],
        'hurt':[at[i] for i in (0,1,2,3)],
        'attack':[at[i] for i in (4,5,6,8,9,10,11)],
        'slam':[sl[i] for i in (0,1,2,3,8,6,10,11)],
        'charge':[ch[i] for i in range(7)],'roar':[ro[i] for i in range(7)],
        'death':[de[0],de[1],de[2],rot(de[2],38),rot(de[2],72),de[6],fl(de[10])]}
    return an
def main(sc):
    an=build(sc);ext=0;mh=0
    for fr in an.values():
        for f in fr:
            b=bbox(f);a=np.array(f.getchannel('A'))[b[1]:b[3],b[0]:b[2]];xs=np.nonzero(a>0)[1];cx=xs.mean();w=b[2]-b[0]
            ext=max(ext,cx,w-cx);mh=max(mh,b[3]-b[1])
    W=int(2*ext*sc)+14;H=int(mh*sc)+14;frames=[];meta={'w':W,'h':H,'ax':W//2,'ay':H-6,'cols':10,'anims':{}}
    for n,fr in an.items():
        meta['anims'][n]=[len(frames)+i for i in range(len(fr))]
        for f in fr:
            b=bbox(f);f=f.crop(b);a=np.array(f.getchannel('A'));cx=np.nonzero(a>0)[1].mean()
            g=f.resize((max(1,round(f.width*sc)),max(1,round(f.height*sc))),Image.LANCZOS)
            c=Image.new('RGBA',(W,H),(0,0,0,0));c.alpha_composite(g,(round(W/2-cx*sc),H-6-g.height));frames.append(c)
    cols=meta['cols'];rows=(len(frames)+cols-1)//cols;A=Image.new('RGBA',(cols*W,rows*H),(0,0,0,0))
    for i,f in enumerate(frames):A.alpha_composite(f,((i%cols)*W,(i//cols)*H))
    A.save(OUT+'morvath_atlas.png',optimize=True);json.dump(meta,open(OUT+'morvath_atlas.json','w'))
    print(A.size,len(frames),'quadros; célula',W,H,{k:len(v) for k,v in meta['anims'].items()})
if __name__=='__main__':main(float(sys.argv[1]) if len(sys.argv)>1 else .62)
