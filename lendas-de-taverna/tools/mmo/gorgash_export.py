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
def soften(A,cells=None,CW=0,CH=0):
    """Recolorização POR MATERIAL (não é um filtro único): separa pele, couro/tecido laranja, metal e pelo por cor e textura
    e trata cada um com sua própria curva de luz e tom: pele verde viva e clara, couro cobre quente, aço frio com brilho especular,
    pelo marrom acinzentado. Contornos escuros ficam escuros para preservar os detalhes da armadura."""
    a=np.array(A);al=a[:,:,3]>0
    hsv=cv2.cvtColor(a[:,:,:3],cv2.COLOR_RGB2HSV).astype(np.float32);H,Sx,V=hsv[:,:,0],hsv[:,:,1],hsv[:,:,2]
    lab=cv2.cvtColor(a[:,:,:3],cv2.COLOR_RGB2LAB).astype(np.float32);L,Ac,Bc=lab[:,:,0],lab[:,:,1],lab[:,:,2]
    var=np.sqrt(np.maximum(cv2.blur(L*L,(5,5))-cv2.blur(L,(5,5))**2,0))
    skin=al&(H>=22)&(H<=52)&(Sx>38)
    warm=al&~skin&(((H<=22)|(H>=168))&(Sx>62)&(V>45))
    fur=al&~skin&~warm&(L<80)&(var>10)
    metal=al&~skin&~warm&~fur
    def soft(m):return np.clip(cv2.GaussianBlur(m.astype(np.float32),(0,0),1.0),0,1)
    ms={'skin':soft(skin),'warm':soft(warm),'fur':soft(fur),'metal':soft(metal)}
    Lo=np.zeros_like(L);Ao=np.zeros_like(L);Bo=np.zeros_like(L);W=np.zeros_like(L)+1e-6
    # (faixa de L de saída, gama, croma alvo a/b, mistura do croma, ganho do croma, realce especular)
    P={'skin':((62,206),.82,(128-30,128+38),.42,1.45,0),
       'warm':((50,190),.85,(128+30,128+42),.30,1.30,0),
       'fur':((48,150),.9,(128+7,128+15),.40,1.0,0),
       'metal':((30,216),.9,(128-3,128-16),.45,1.0,34)}
    PG={}
    for k,m in ms.items():
        sel=(m>.5);PG[k]=np.percentile(L[sel],[3,98]) if sel.sum()>100 else (10,200)
    def pct(k,sel_cell):
        lo,hi=PG[k]
        if sel_cell is not None and sel_cell.sum()>150:
            cl,ch=np.percentile(L[sel_cell],[3,98]);lo=.2*lo+.8*cl;hi=.2*hi+.8*ch
        return lo,hi
    cellid=None
    if cells:
        cellid=np.zeros(L.shape,np.int32)
        for n in range(cells):
            cellid[(n//12)*CH:(n//12+1)*CH,(n%12)*CW:(n%12+1)*CW]=n+1
    for k,m in ms.items():
        sel=(m>.5)
        if cellid is None:lo,hi=PG[k];stretch=None
        (o0,o1),gam,(ta,tb),mix,gain,spec=P[k]
        if cellid is None:
            t=np.clip((L-lo)/max(1,hi-lo),0,1)
        else:
            t=np.zeros_like(L)
            for n in range(1,cells+1):
                cm=(cellid==n)
                if not (cm&sel).any():continue
                lo,hi=pct(k,cm&sel);t[cm]=np.clip((L[cm]-lo)/max(1,hi-lo),0,1)
        Ln=o0+(o1-o0)*np.power(t,gam)
        if spec:Ln+=spec*np.clip((t-.62)/.38,0,1)**1.6
        # contornos/frestas escuras continuam escuros
        o=np.clip((38-L)/22,0,1);Ln=Ln*(1-o)+np.minimum(L*1.25+6,60)*o
        An=128+(Ac-128)*gain;Bn=128+(Bc-128)*gain
        An=An*(1-mix)+ta*mix;Bn=Bn*(1-mix)+tb*mix
        Lo+=Ln*m;Ao+=An*m;Bo+=Bn*m;W+=m
    Lo/=W;Ao/=W;Bo/=W
    rgb=cv2.cvtColor(np.dstack([np.clip(Lo,0,255),np.clip(Ao,0,255),np.clip(Bo,0,255)]).astype(np.uint8),cv2.COLOR_LAB2RGB)
    # olhos vermelho-alaranjados brilhantes: preservados e realçados
    eye=al&(a[:,:,0]>190)&(a[:,:,1]<130)&(a[:,:,2]<90)
    rgb[eye]=a[:,:,:3][eye]
    out=np.dstack([rgb,a[:,:,3]]);out[~al]=0
    return Image.fromarray(out,'RGBA')
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
    A=soften(A,len(frames),W,H)
    A.save(OUT+'gorgash_atlas.png',optimize=True);json.dump(meta,open(OUT+'gorgash_atlas.json','w'))
    print(A.size,len(frames),'quadros; célula',W,H,{k:len(v) for k,v in meta['anims'].items()})
if __name__=='__main__':main(float(sys.argv[1]) if len(sys.argv)>1 else .64)
