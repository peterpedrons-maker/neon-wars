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
import cv2
from scipy import ndimage as ND
def anchor(f):
    """x = centro do tronco (sem capa/espada), y = chão (botas, sem a lâmina); deitado/rotacionado: massa e base da caixa"""
    a=np.array(f);al=a[:,:,3]>0;ys,xs=np.nonzero(al);y0,y1,x0,x1=ys.min(),ys.max(),xs.min(),xs.max();H=y1-y0+1;W=x1-x0+1
    if W>H*.85:return xs.mean(),y1
    rgb=a[:,:,:3].astype(int);cy=ND.binary_dilation((rgb[:,:,1]>rgb[:,:,0]+30)&(rgb[:,:,2]>110),iterations=3)
    red=rgb[:,:,0]>rgb[:,:,2]+20;yy=np.arange(a.shape[0])[:,None]
    t=al&~cy&~red&(yy>y0+H*.28)&(yy<y0+H*.48)
    gy=np.nonzero((al&~cy&~red).any(1))[0].max()
    return (np.nonzero(t)[1].mean() if t.any() else xs.mean()),gy
def interp(fr):
    """insere um quadro intermediário entre cada par (fluxo óptico Farneback), ciclo fechado"""
    out=[]
    def pm(f):
        a=np.array(f).astype(np.float32);a[:,:,:3]*=a[:,:,3:4]/255;return a
    for i,f in enumerate(fr):
        g=fr[(i+1)%len(fr)];A,B=pm(f),pm(g)
        ga=cv2.cvtColor(np.clip(A[:,:,:3],0,255).astype(np.uint8),cv2.COLOR_RGB2GRAY);gb=cv2.cvtColor(np.clip(B[:,:,:3],0,255).astype(np.uint8),cv2.COLOR_RGB2GRAY)
        fl=cv2.calcOpticalFlowFarneback(ga,gb,None,.5,4,25,5,7,1.5,0)
        h,w=ga.shape;gx,gy=np.meshgrid(np.arange(w,dtype=np.float32),np.arange(h,dtype=np.float32))
        wa=cv2.remap(A,gx-.5*fl[:,:,0],gy-.5*fl[:,:,1],cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT)
        wb=cv2.remap(B,gx+.5*fl[:,:,0],gy+.5*fl[:,:,1],cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT)
        m=(wa+wb)/2;al=np.clip(m[:,:,3:4],1,255);rgb=np.clip(m[:,:,:3]*255/al,0,255);al=np.where(m[:,:,3:4]>90,255,0)
        out+=[f,Image.fromarray(np.dstack([rgb,al]).astype(np.uint8),'RGBA')]
    return out
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
    an=build(sc);info={}
    for n,fr in an.items():
        for f in fr:
            ax,gy=anchor(f);b=bbox(f);info[id(f)]=(ax,gy,b)
    L=R=T=B=0
    for fr in an.values():
        for f in fr:
            ax,gy,b=info[id(f)];L=max(L,ax-b[0]);R=max(R,b[2]-ax);T=max(T,gy-b[1]);B=max(B,b[3]-gy)
    Wc=int(max(L,R)*2)+20;Hc=int(T+B)+20;gx=Wc//2;gyc=int(T)+10
    def place(f):
        ax,gy,b=info[id(f)];c=Image.new('RGBA',(Wc,Hc),(0,0,0,0));c.alpha_composite(f,(round(gx-ax),round(gyc-gy)));return c
    W=int(Wc*sc);H=int(Hc*sc);frames=[];meta={'w':W,'h':H,'ax':W//2,'ay':int(gyc*sc),'cols':12,'anims':{}}
    for n,fr in an.items():
        pl=[place(f) for f in fr]
        if n in('idle','walk'):pl=interp(pl)
        meta['anims'][n]=[len(frames)+i for i in range(len(pl))]
        for c in pl:frames.append(c.resize((W,H),Image.LANCZOS))
    cols=meta['cols'];rows=(len(frames)+cols-1)//cols;A=Image.new('RGBA',(cols*W,rows*H),(0,0,0,0))
    for i,f in enumerate(frames):A.alpha_composite(f,((i%cols)*W,(i//cols)*H))
    A.save(OUT+'morvath_atlas.png',optimize=True);json.dump(meta,open(OUT+'morvath_atlas.json','w'))
    print(A.size,len(frames),'quadros; célula',W,H,{k:len(v) for k,v in meta['anims'].items()})
if __name__=='__main__':main(float(sys.argv[1]) if len(sys.argv)>1 else .62)
