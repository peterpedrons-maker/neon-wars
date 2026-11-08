"""Monta os atlas do mini-chefe Xamã Skrix e do totem a partir das folhas de IA (skrix_src/).
skrix_atlas.png/json: idle, walk, hurt, attack, death, totem, curse, summon.   totem_atlas.png/json: rise, idle, hit, death.
Uso: python3 skrix_export.py [escala_skrix] [escala_totem]"""
import sys,json,os
import numpy as np
from PIL import Image,ImageOps
import skrix_cut as SC
OUT='../../mmo/assets/chars/'
C={n:SC.cells(n) for n in (1,2,3,4,5,6,7,9)}
fl=lambda f:ImageOps.mirror(f)
def crop(f):
    b=f.getchannel('A').getbbox();return f.crop(b)
def feet_place(frames,W,H,sc):
    """alinha pelo chão (borda inferior) e pelo centro de massa horizontal"""
    out=[]
    for f in frames:
        f=crop(f);a=np.array(f.getchannel('A'));ys,xs=np.nonzero(a>0);cx=xs.mean()
        g=f.resize((max(1,round(f.width*sc)),max(1,round(f.height*sc))),Image.LANCZOS);cx*=sc
        c=Image.new('RGBA',(W,H),(0,0,0,0));x=round(W/2-cx);y=H-6-g.height;c.alpha_composite(g,(x,y));out.append(c)
    return out
def atlas(anims,sc,name,cols=10,fixed=None):
    mw=mh=0
    for fr in anims.values():
        for f in fr:
            b=crop(f);mw=max(mw,b.width);mh=max(mh,b.height)
    W=round(mw*sc*1.55)+12;H=round(mh*sc)+12
    if fixed:W,H=fixed
    frames=[];meta={'w':W,'h':H,'ax':W//2,'ay':H-6,'cols':cols,'anims':{}}
    for n,fr in anims.items():
        meta['anims'][n]=[len(frames)+i for i in range(len(fr))];frames+=feet_place(fr,W,H,sc)
    rows=(len(frames)+cols-1)//cols;A=Image.new('RGBA',(cols*W,rows*H),(0,0,0,0))
    for i,f in enumerate(frames):A.alpha_composite(f,((i%cols)*W,(i//cols)*H))
    A.save(OUT+name+'_atlas.png',optimize=True);json.dump(meta,open(OUT+name+'_atlas.json','w'));print(name,A.size,len(frames),'quadros; célula',W,H)
def rise(f,n=6):
    """totem saindo do chão: o sprite sobe de baixo da linha do chão (recorte no pé)"""
    f=crop(f);W,H=f.size;fr=[]
    for k in range(n):
        t=(k+1)/n;t=1-(1-t)**2;off=round(H*(1-t)*.98)
        c=Image.new('RGBA',(W,H),(0,0,0,0));c.alpha_composite(f,(0,off));fr.append(c.crop((0,0,W,H)))
    return fr
if __name__=='__main__':
    ks=float(sys.argv[1]) if len(sys.argv)>1 else .42
    kt=float(sys.argv[2]) if len(sys.argv)>2 else .30
    s1,s2,s3,s4,s5,s6,s7,s9=[C[i] for i in (1,2,3,4,5,6,7,9)]
    an={'idle':[s3[i] for i in (0,1,2,3,2,1)],'walk':[s3[i] for i in range(4,12)],
        'hurt':[s1[1],s2[1],s1[0],s3[0]],
        'attack':[s1[4],s1[5],s1[6],s1[6],s1[9],s1[9],s3[0]],
        'death':[s4[i] for i in (0,1,2,3,4,6,7)]+[fl(s4[i]) for i in (8,9,10,11)],
        'totem':[s5[i] for i in (0,1,3,5,5,6,7)],'curse':[s6[i] for i in range(8)],'summon':[s7[i] for i in range(8)]}
    atlas(an,ks,'skrix')
    tot={'rise':rise(s9[4]),'idle':[s9[i] for i in range(4,8)],'hit':[s9[8]],'death':[s9[9],s9[10],s9[11]]}
    atlas(tot,kt,'totem',cols=8)
