"""Monta o atlas do chefe Gorgash (orc) a partir das folhas de IA (gorgash_src/), combinando os melhores quadros de cada folha.
Capa removida do idle/caminhada (gorgash_uncape.py). Gera mmo/assets/chars/gorgash_atlas.png/json.
Uso: python3 gorgash_export.py [escala]"""
import sys,json
import numpy as np
from PIL import Image,ImageOps
import gorgash_cut as GC
OUT='../../mmo/assets/chars/'
fl=ImageOps.mirror
def bbox(f):return f.getchannel('A').getbbox()
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

# fator de escala de cada folha (a IA desenhou o orc em tamanhos diferentes por folha), medido pela altura do orc em pé
K={'iw':1.0,'atk':.847,'death':.645,'slam':.59,'charge':.645,'roar':.645}
def build():
    C={n:GC.cells(n) for n in K}
    def F(n,i):
        f=C[n][i];return (f,K[n])
    iw=lambda i:F('iw',i);at=lambda i:F('atk',i);de=lambda i:F('death',i);sl=lambda i:F('slam',i);ch=lambda i:F('charge',i);ro=lambda i:F('roar',i)
    return {'idle':[iw(i) for i in (0,1,2,3,4,5,4,3,2,1)],'walk':[iw(i) for i in range(6,18)],
      'hurt':[at(i) for i in (1,0,2,3)],'attack':[at(i) for i in (4,5,6,8,9,10,11)],
      'slam':[sl(i) for i in range(7)]+[at(10)],
      'charge':[ch(0),ch(1),ch(2),ch(4),ch(5),ch(2),ch(7)],
      'roar':[ro(i) for i in range(7)],'death':[de(i) for i in range(8)]}
def main(sc):
    an=build();info={};scaled={}
    for n,fr in an.items():
        L=[]
        for f,k in fr:
            g=f.resize((max(1,round(f.width*k)),max(1,round(f.height*k))),Image.LANCZOS);ax,gy=anchor(g);info[id(g)]=(ax,gy,bbox(g));L.append(g)
        scaled[n]=L
    L=R=T=B=0
    for fr in scaled.values():
        for f in fr:
            ax,gy,b=info[id(f)];L=max(L,ax-b[0]);R=max(R,b[2]-ax);T=max(T,gy-b[1]);B=max(B,b[3]-gy)
    Wc=int(max(L,R)*2)+20;Hc=int(T+B)+20;gx=Wc//2;gyc=int(T)+10
    def place(f):
        ax,gy,b=info[id(f)];c=Image.new('RGBA',(Wc,Hc),(0,0,0,0));c.alpha_composite(f,(round(gx-ax),round(gyc-gy)));return c
    W=int(Wc*sc);H=int(Hc*sc);frames=[];meta={'w':W,'h':H,'ax':W//2,'ay':int(gyc*sc),'cols':12,'anims':{}}
    for n,fr in scaled.items():
        pl=[place(f) for f in fr]
        if n in('idle','walk'):pl=interp(pl)
        meta['anims'][n]=[len(frames)+i for i in range(len(pl))]
        for c in pl:frames.append(c.resize((W,H),Image.LANCZOS))
    cols=meta['cols'];rows=(len(frames)+cols-1)//cols;A=Image.new('RGBA',(cols*W,rows*H),(0,0,0,0))
    for i,f in enumerate(frames):A.alpha_composite(f,((i%cols)*W,(i//cols)*H))
    A.save(OUT+'gorgash_atlas.png',optimize=True);json.dump(meta,open(OUT+'gorgash_atlas.json','w'))
    print(A.size,len(frames),'quadros; célula',W,H,{k:len(v) for k,v in meta['anims'].items()})
if __name__=='__main__':main(float(sys.argv[1]) if len(sys.argv)>1 else .64)
