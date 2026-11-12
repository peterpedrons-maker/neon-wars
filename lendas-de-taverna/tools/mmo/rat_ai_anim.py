"""Anima a arte de IA em pixel art do Rei dos Ratos (pose parada) por esqueleto de pernas: corpo/cano/cauda ficam intactos, as duas pernas giram.
Uso: python3 rat_ai_anim.py <imagem> <pasta_saida>"""
import sys,os,math
import numpy as np,cv2
from PIL import Image
from scipy import ndimage as ND
src,out=sys.argv[1],sys.argv[2];os.makedirs(out,exist_ok=True)
im=Image.open(src).convert('RGB');a=np.array(im).astype(int)
bg=(a[:,:,0]>190)&(a[:,:,1]<90)&(a[:,:,2]>190)
al=~ND.binary_dilation(bg,iterations=1)|~bg
al=~bg
lb,n=ND.label(al);sz=ND.sum(al,lb,range(1,n+1));al=np.isin(lb,[i+1 for i,v in enumerate(sz) if v>sz.max()*.02])
rgba=np.dstack([np.array(im),np.where(al,255,0).astype(np.uint8)])
ys,xs=np.nonzero(al);x0,x1,y0,y1=xs.min(),xs.max(),ys.min(),ys.max();print('bbox',x0,y0,x1,y1)
F=Image.fromarray(rgba,'RGBA').crop((x0-20,y0-20,x1+20,y1+30));A=np.array(F);H,W=A.shape[:2];print(W,H)
al=A[:,:,3]>0;r,g,b=[A[:,:,i].astype(int) for i in range(3)]
cut=int(H*.74)           # abaixo da tanga: pernas
club=al&(r>g+22)&(r<150)&(g<95)&(b<80)
club=ND.binary_dilation(club,iterations=2)&al
tailm=al&(np.arange(W)[None,:]<int(W*.30))&(np.arange(H)[:,None]>cut)
sx=int(W*.545)          # divisão entre as duas pernas (x)
yy=np.arange(H)[:,None];xx=np.arange(W)[None,:]
legzone=al&(yy>=cut-26)&~club&~tailm
L=np.where(legzone&(xx<sx),255,0).astype(np.uint8);R=np.where(legzone&(xx>=sx),255,0).astype(np.uint8)
body=al&~(legzone&(yy>=cut))|club|tailm
def layer(mask):
    d=A.copy();d[:,:,3]=np.where(mask,255,0);return Image.fromarray(d,'RGBA')
LB=layer(body);LL=layer(L>0);LR=layer(R>0)
Image.fromarray(np.hstack([np.array(LB),np.array(LL),np.array(LR)])).save(out+'/parts.png')
def rot(img,ang,piv):
    pad=Image.new('RGBA',(W*2,H*2),(0,0,0,0));pad.alpha_composite(img,(W//2,H//2));p=pad.rotate(ang,resample=Image.NEAREST,center=(piv[0]+W//2,piv[1]+H//2))
    return p.crop((W//2,H//2,W//2+W,H//2+H))
def bbox(m):
    ys,xs=np.nonzero(m);return xs.min(),xs.max(),ys.min(),ys.max()
lx0,lx1,_,_=bbox(L>0);rx0,rx1,_,_=bbox(R>0)
pL=((lx0+lx1)/2,cut-10);pR=((rx0+rx1)/2,cut-10)
def frame(t,amp=20,lift=14,bob=7):
    ph=2*math.pi*t;aL=amp*math.sin(ph);aR=-aL
    dL=-lift*max(0,math.cos(ph));dR=-lift*max(0,-math.cos(ph))
    C=Image.new('RGBA',(W,H+60),(0,0,0,0))
    for LL_,ang,piv,dy in ((LL,aL,pL,dL),(LR,aR,pR,dR)):
        r_=rot(LL_,ang,piv);C.alpha_composite(r_,(0,int(30+dy)))
    bd=-abs(math.sin(ph))*bob
    C.alpha_composite(LB,(0,int(30+bd)))
    return C
def pixelate(img,f):
    w,h=img.size;sm=img.resize((w//f,h//f),Image.BOX)
    a=np.array(sm);a[:,:,3]=np.where(a[:,:,3]>110,255,0);return Image.fromarray(a,'RGBA')
f=int(sys.argv[3]) if len(sys.argv)>3 else 6
fr=[pixelate(frame(i/12),f) for i in range(12)]
for i,x in enumerate(fr):x.save('%s/w%02d.png'%(out,i))
base=pixelate(Image.fromarray(np.array(F)),f);base.save(out+'/base.png');print(base.size)
