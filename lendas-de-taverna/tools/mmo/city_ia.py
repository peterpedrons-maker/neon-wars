"""Arte da cidade e ícones gerados por IA (folhas em ia_src/city/): recorta, reduz para a escala do jogo e entrega sprites para build_town4.py.
 exec() dentro de build_town4.py (usa HERE, OUT, Image, np). Também grava os ícones em mmo/assets/ui-icons/ni_*.png."""
import os,sys
from PIL import Image
import numpy as np
from scipy import ndimage
_C=os.path.join(HERE,'ia_src','city');sys.path.insert(0,_C)
from segmag import segment as _seg,keyout as _key
def _scale(im,f=None,w=None,h=None):
    if w:f=w/im.width
    if h:f=h/im.height
    W,H=max(1,round(im.width*f)),max(1,round(im.height*f))
    p=im.convert('RGBa').resize((W,H),Image.BOX).convert('RGBA');a=np.array(p);a[:,:,3]=np.where(a[:,:,3]>110,255,0);return Image.fromarray(a,'RGBA')
def _amber(im):
    """vidros rosados (vazamento do magenta) -> âmbar quente"""
    a=np.array(im).astype(int);r,g,b=a[:,:,0],a[:,:,1],a[:,:,2]
    m=(a[:,:,3]>0)&(r>150)&(b>130)&(g<r-12)&(b>g+8)
    L=(r+g+b)/3.0/255
    out=a.copy();out[:,:,0]=np.where(m,np.clip(255*(.55+.45*L),0,255),out[:,:,0]);out[:,:,1]=np.where(m,np.clip(205*(.5+.5*L),0,255),out[:,:,1]);out[:,:,2]=np.where(m,np.clip(110*(.35+.65*L),0,255),out[:,:,2])
    return Image.fromarray(out.astype('uint8'),'RGBA')
def _cell_icon(im_path,cols,rows):
    im=Image.open(im_path).convert('RGB');W,H=im.size;cw,ch=W/cols,H/rows;out=[]
    for r in range(rows):
        for c in range(cols):
            cell=im.crop((round(c*cw),round(r*ch),round((c+1)*cw),round((r+1)*ch)))
            a,fg=_key(cell);rgba=np.dstack([a.astype('uint8'),(fg*255).astype('uint8')]);img=Image.fromarray(rgba,'RGBA');bb=img.getbbox()
            out.append(img.crop(bb) if bb else img)
    return out
def _icon64(im):
    s=min(60/im.width,60/im.height);t=_scale(im,f=s);cell=Image.new('RGBA',(64,64),(0,0,0,0));cell.alpha_composite(t,((64-t.width)//2,(64-t.height)//2));return cell
ICN=['heroi','livro','talentos','botas','tp','bigorna','reforja','ferro','runa','cristal','moedas','desmontar']
ICB=['eforca','evigor','esorte','pmaior','d1','d2','d3','d4']
UIO=os.path.join(OUT,'..','..','assets','ui-icons')
for n,im in zip(ICN,_cell_icon(os.path.join(_C,'iconsA.jpg'),4,3)):_icon64(im).save(os.path.join(UIO,'ni_%s.png'%n))
def _largest(im):
    a=np.array(im);m=a[:,:,3]>0;lab,n=ndimage.label(m,structure=np.ones((3,3)))
    if n<2:return im
    sz=ndimage.sum(m,lab,range(1,n+1));k=1+int(np.argmax(sz));a[lab!=k]=(0,0,0,0);o=Image.fromarray(a,'RGBA');return o.crop(o.getbbox())
_ib=dict(zip(ICB,_cell_icon(os.path.join(_C,'iconsB.jpg'),4,2)))
for n in ('eforca','evigor','esorte'):_ib[n]=_largest(_ib[n])     # tira os iconezinhos (fogo, coracao, trevo) ao lado do frasco
def _recolor_blue(im):
    a=np.array(im).astype(int);r,g,b=a[:,:,0],a[:,:,1],a[:,:,2];liq=(a[:,:,3]>0)&(g>r+25)&(g>b+25)
    L=(r+g+b)/3.0
    a[:,:,0]=np.where(liq,L*.45,a[:,:,0]);a[:,:,1]=np.where(liq,L*.85,a[:,:,1]);a[:,:,2]=np.where(liq,np.clip(L*1.5,0,255),a[:,:,2])
    return Image.fromarray(a.astype('uint8'),'RGBA')
_ib['edefesa']=_recolor_blue(_ib['evigor'])
for n,im in _ib.items():
    if n.startswith('d'):continue
    _icon64(im).save(os.path.join(UIO,'ni_%s.png'%n))
import shutil;shutil.copy(os.path.join(UIO,'..','ico','v_pocao.png'),os.path.join(UIO,'ni_pocao.png'))
# ---- cidade
_D=_seg(os.path.join(_C,'decor.jpg'),dil=3,minarea=150)
CI={}
def _pick(i,**k):return _scale(_D[i],**k)
CI['torch']=[_pick(i,h=38) for i in (0,1,2)]
CI['lamp']=[_amber(_pick(i,h=56)) for i in (9,10)]
CI['banner']=[_pick(i,h=40) for i in (11,12,13)]
CI['bench']=[_pick(i,w=36) for i in (18,19)]
CI['flowerbox']=[_pick(i,w=34) for i in (17,22)]
CI['barrels']=[_pick(15,w=34),_pick(23,w=34),_pick(28,w=20)]
CI['crates']=[_pick(24,w=40)]
CI['well']=[_pick(20,w=42)]
CI['stall']=[_pick(27,w=46)]
CI['sign']=[_pick(25,h=40),_pick(26,h=32)]
CI['hay']=[_pick(29,w=26),_pick(30,w=26)]
CI['sack']=[_pick(31,h=18),_pick(32,h=18)]
_P=_seg(os.path.join(_C,'portal.jpg'),dil=3,minarea=3000)
def _hole(img):
    a=np.array(img)[:,:,3]>0;filled=ndimage.binary_fill_holes(a);hole=filled&~a;lab,n=ndimage.label(hole)
    if n==0:return None
    sz=ndimage.sum(hole,lab,range(1,n+1));k=1+int(np.argmax(sz));ys,xs=np.where(lab==k);return (xs.min(),xs.max(),ys.min(),ys.max())
_pi=_P[0];_ps=110/_pi.width;CI['portal']=_scale(_pi,f=_ps)
_hb=_hole(CI['portal']);CI['portal_hole']=_hb   # (x0,x1,y0,y1) em px do sprite (pack)
_F=_seg(os.path.join(_C,'fountain.jpg'),dil=3,minarea=3000)
CI['fountain']=_scale(_F[1],w=84)
CI['well_big']=_scale(_D[20],w=58)
print('ni_ icons ok; portal',CI['portal'].size,'hole',_hb,'fountain',CI['fountain'].size)

# ---- portal de frente (desenhado em código com a paleta do portal gerado por IA): dois pilares, verga com gema, vão oval vazio
def _front_portal():
    Wd,Hh=118,132;im=Image.new('RGBA',(Wd,Hh),(0,0,0,0));from PIL import ImageDraw;d=ImageDraw.Draw(im)
    O=(26,22,28,255);S1=(150,146,138,255);S2=(118,114,108,255);S3=(88,84,82,255);S4=(62,60,62,255);MO=(70,104,52,255);MO2=(50,80,40,255)
    cx=Wd//2
    def block(x0,y0,x1,y1,seed):
        d.rectangle([x0,y0,x1,y1],fill=S2,outline=O);d.line([(x0+1,y0+1),(x1-1,y0+1)],fill=S1);d.line([(x0+1,y0+1),(x0+1,y1-1)],fill=S1);d.line([(x1-1,y0+2),(x1-1,y1-1)],fill=S3);d.line([(x0+2,y1-1),(x1-1,y1-1)],fill=S3)
        if seed%3==0:d.point([(x0+4,y0+4),(x0+5,y0+5),(x1-4,y1-3)],fill=S4)
    # degraus
    for i,(w,y) in enumerate([(100,Hh-8),(90,Hh-14)]):block(cx-w//2,y,cx+w//2,y+7,i)
    # pilares (blocos empilhados)
    for side in(-1,1):
        px=cx+side*38
        for k,y in enumerate(range(24,Hh-14,14)):block(px-11,y,px+11,min(Hh-15,y+14),k+side)
        block(px-14,18,px+14,28,1);block(px-14,Hh-22,px+14,Hh-14,2)   # capitel e base
        for y in range(40,Hh-34,12):
            d.rectangle([px-2,y,px+2,y+7],fill=(90,200,255,255));d.rectangle([px-1,y+1,px+1,y+6],fill=(190,240,255,255))     # runas brilhantes
    # arco/verga
    d.rectangle([cx-52,6,cx+52,24],fill=S2,outline=O)
    for k in range(7):block(cx-52+k*15,6,cx-52+k*15+15,24,k)
    d.polygon([(cx-52,24),(cx-27,24),(cx-27,34),(cx-52,28)],fill=S3,outline=O);d.polygon([(cx+52,24),(cx+27,24),(cx+27,34),(cx+52,28)],fill=S3,outline=O)
    d.rectangle([cx-10,2,cx+10,26],fill=S1,outline=O)
    d.polygon([(cx,6),(cx+6,14),(cx,24),(cx-6,14)],fill=(225,50,60,255),outline=(90,12,24,255));d.polygon([(cx,9),(cx+3,14),(cx,18),(cx-2,14)],fill=(255,170,170,255))
    # vão oval
    hx0,hx1,hy0,hy1=cx-27,cx+27,34,Hh-18
    d.ellipse([hx0-3,hy0-3,hx1+3,hy1+3],fill=S3,outline=O)
    hole=Image.new('L',(Wd,Hh),0);ImageDraw.Draw(hole).ellipse([hx0,hy0,hx1,hy1],fill=255)
    a=np.array(im);m=np.array(hole)>0;a[m]=(0,0,0,0);im=Image.fromarray(a,'RGBA');d=ImageDraw.Draw(im)
    d.arc([hx0-1,hy0-1,hx1+1,hy1+1],0,360,fill=O)
    # musgo e trepadeiras
    rnd=__import__('random').Random(4)
    for _ in range(26):
        x=rnd.choice([rnd.randrange(cx-62,cx-24),rnd.randrange(cx+24,cx+62)]);y=rnd.randrange(8,Hh-10)
        if (x-cx)**2/(27**2)+(y-(hy0+hy1)/2)**2/(((hy1-hy0)/2)**2)<1.1 and hy0<y<hy1:continue
        if a[min(Hh-1,y),min(Wd-1,x),3]>0:d.rectangle([x,y,x+rnd.randrange(1,4),y+rnd.randrange(1,3)],fill=MO if rnd.random()<.6 else MO2)
    for side in(-1,1):
        x=cx+side*(48+rnd.randrange(-3,3))
        for y in range(10,Hh-16,3):
            x+=rnd.choice((-1,0,0,1));
            if a[y,min(Wd-1,max(0,x)),3]>0:d.point((x,y),fill=MO)
    return im,(hx0,hx1,hy0,hy1)
CI['portal_front'],CI['portal_front_hole']=_front_portal()
# ---- ícones de dungeon genéricos (floresta, gelo, ruínas, árvore seca) a partir dos props da floresta dos goblins
sys.path.insert(0,os.path.join(HERE,'ia_src'))
from seg import segment as _segg
_G=_segg(os.path.join(HERE,'ia_src','s3.jpg'),dil=3,minarea=120)
def _tint(im,m):
    a=np.array(im).astype(float);a[:,:,0]*=m[0];a[:,:,1]*=m[1];a[:,:,2]*=m[2];return Image.fromarray(np.clip(a,0,255).astype('uint8'),'RGBA')
def _pad(im):
    return _icon64(im)
_pine=_G[0];_rock=_G[13];_dead=_G[3]
_pn=_pad(_pine);_pn.save(os.path.join(UIO,'ni_d1.png'))
_pad(_tint(_pine,(1.0,1.25,1.5))).save(os.path.join(UIO,'ni_d2.png'))
_pad(_rock).save(os.path.join(UIO,'ni_d3.png'))
_pad(_dead).save(os.path.join(UIO,'ni_d4.png'))
# ---- portal de frente gerado por IA (variação da esquerda: pedra limpa); mantém o desenhado em código se o recorte falhar
try:
    _PF=_seg(os.path.join(_C,'portal_front.jpg'),dil=3,minarea=3000)
    _pf=_scale(_PF[0],w=124);_hh=_hole(_pf)
    if _hh is not None:CI['portal_front'],CI['portal_front_hole']=_pf,_hh;print('portal IA',_pf.size,_hh)
except Exception as e:print('portal IA falhou',e)
