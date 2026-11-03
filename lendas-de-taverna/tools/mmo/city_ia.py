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
for n,im in zip(ICB,_cell_icon(os.path.join(_C,'iconsB.jpg'),4,2)):_icon64(im).save(os.path.join(UIO,'ni_%s.png'%n))
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
print('ni_ icons ok; portal',CI['portal'].size,'hole',_hb,'fountain',CI['fountain'].size)
