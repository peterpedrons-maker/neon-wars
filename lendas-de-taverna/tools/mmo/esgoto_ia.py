"""Arte dos Esgotos gerada por IA (folhas em ia_src/esgoto/*.jpg): recorta cada sprite do fundo magenta, reduz para a escala do jogo,
quantiza numa paleta única e define colisões; fatia os tiles de chão/parede/água (16x16). Uso: exec() dentro de build_esgoto.py."""
import os,sys
from PIL import Image
import numpy as np
_H=globals().get('HERE') or os.getcwd()
sys.path.insert(0,os.path.join(_H,'ia_src','cripta'))
from segm import segment
_D=os.path.join(_H,'ia_src','esgoto')
_SH={n:segment(os.path.join(_D,n+'.jpg'),dil=3,minarea=150) for n in ('vida','estr','boss')}
def _crop(im,x0,y0,x1,y1):
    return im.crop((int(im.width*x0),int(im.height*y0),int(im.width*x1),int(im.height*y1)))
_X={}
for _k,_i in enumerate((18,19,20,21)):_X['rh%d'%_k]=_crop(_SH['vida'][_i],.27,.45,.75,1.0)      # buraco de rato na base da parede
_a=_SH['boss'][7];_X['statue2']=_a.crop((0,0,_a.width,int(_a.height*.66)))
def _get(s,i):return _X[i] if isinstance(i,str) else _SH[s][i]
def _scale(im,f):
    w,h=max(1,round(im.width*f)),max(1,round(im.height*f))
    p=im.convert('RGBa').resize((w,h),Image.BOX).convert('RGBA')
    a=np.array(p);a[:,:,3]=np.where(a[:,:,3]>110,255,0);return Image.fromarray(a,'RGBA')
def _clean(im):
    from scipy import ndimage
    a=np.array(im);m=a[:,:,3]>0;edge=m&~ndimage.binary_erosion(m,iterations=1,border_value=1)
    r,g,b=a[:,:,0].astype(int),a[:,:,1].astype(int),a[:,:,2].astype(int)
    pur=edge&((np.minimum(r,b)-g)>10)&(r>g+4)&(b>g+4)
    a[pur,:3]=(24,28,40);return Image.fromarray(a,'RGBA')
CAT={
 'nest':[('vida',i,.24,'wide') for i in (0,1,2)],
 'trash':[('vida',3,.18,'none'),('vida',4,.18,'none')],
 'crate':[('vida',5,.15,'wide'),('vida',6,.15,'wide'),('vida',7,.15,'wide')],
 'sack':[('vida',8,.14,'post')],
 'cheese':[('vida',9,.17,'post')],
 'coins':[('vida',10,.18,'flat')],
 'shroom':[('vida',12,.14,'none'),('vida',13,.14,'none'),('vida',14,.15,'none')],
 'slime':[('vida',15,.18,'flat'),('vida',16,.18,'flat'),('vida',17,.18,'flat')],
 'bones':[('vida',22,.17,'flat'),('vida',23,.17,'flat')],
 'fish':[('vida',27,.16,'flat'),('vida',28,.16,'flat')],
 'lantern':[('vida',34,.17,'none'),('vida',36,.17,'post')],
 'boat':[('vida',42,.23,'wide')],
 'ratholes':[('vida','rh0',.22,'none'),('vida','rh1',.22,'none'),('vida','rh2',.22,'none'),('vida','rh3',.22,'none')],
 'tunnel':[('estr',0,.27,'wide'),('estr',1,.27,'wide'),('estr',3,.27,'wide')],
 'manhole':[('estr',2,.22,'flat'),('estr',5,.22,'flat'),('estr',6,.22,'flat'),('estr',7,.22,'flat')],
 'pipeh':[('estr',4,.22,'none')],
 'pipev':[('estr',9,.22,'post'),('estr',10,.22,'post'),('estr',11,.22,'post')],
 'grate':[('estr',14,.22,'flat'),('estr',15,.22,'flat')],
 'sluice':[('estr',16,.24,'wide')],
 'pillar':[('estr',17,.235,'post'),('estr',18,.235,'post'),('estr',19,.235,'post')],
 'ladder':[('estr',20,.2,'none'),('estr',21,.2,'none')],
 'vault':[('estr',22,.26,'none')],
 'barrel':[('estr',23,.2,'post'),('estr',24,.2,'post'),('estr',25,.2,'wide')],
 'throne':[('boss',1,.21,'wide')],
 'banner':[('boss',2,.23,'none'),('boss',3,.23,'none'),('boss',4,.23,'none')],
 'statue':[('boss',6,.2,'post'),('boss','statue2',.2,'post')],
 'crown':[('boss',11,.23,'wide')],
 'cage':[('boss',12,.19,'post'),('boss',13,.19,'post')],
 'chest':[('boss',14,.2,'wide'),('boss',15,.2,'wide'),('boss',16,.2,'wide')],
 'chain':[('boss',i,.14,'none') for i in (17,18,19,20,23,24)],
 'shrine':[('boss',21,.185,'wide')],
 'spikes':[('boss',22,.17,'none')],
 'snap':[('boss',25,.15,'flat')],
}
def _col(kind,w,h):
    if kind in('flat','none'):return None
    if kind=='post':return [(0,-2,max(3.5,min(7,w*.28)))]
    r=max(4.5,min(8,h*.17));fw=max(8,w*.78);n=max(1,round(fw/9))
    return [(((i/(n-1))-.5)*(fw-8) if n>1 else 0,-max(3,h*.12),r) for i in range(n)]
_raw={k:[(_clean(_scale(_get(s,i),f)),kd) for (s,i,f,kd) in v] for k,v in CAT.items()}
_all=[im for v in _raw.values() for im,_ in v]
_px=np.concatenate([np.array(im)[np.array(im)[:,:,3]>0][:,:3] for im in _all])
_pal=Image.fromarray(_px[:80000].reshape(-1,1,3).astype('uint8'),'RGB').quantize(colors=96,method=Image.MEDIANCUT,dither=Image.NONE)
def _quant(im):
    a=np.array(im);m=a[:,:,3]>0
    rgb=Image.fromarray(a[:,:,:3],'RGB').quantize(palette=_pal,dither=Image.NONE).convert('RGB')
    return Image.fromarray(np.dstack([np.array(rgb),np.where(m,255,0)]).astype('uint8'),'RGBA')
SI={}
for k,v in _raw.items():
    L=[]
    for im,kd in v:
        q=_quant(im);q.col=_col(kd,q.width,q.height);q.kind=kd;L.append(q)
    SI[k]=L
_T=Image.open(os.path.join(_D,'tiles.jpg')).convert('RGB')
def _tile(x0,y0,x1,y1,m=4):return _T.crop((x0+m,y0+m,x1-m,y1-m)).resize((16,16),Image.BOX).convert('RGBA')
ST={'plain':[_tile(*b) for b in ((3,0,188,190),(195,0,380,190),(388,0,508,190),(516,0,636,190),(3,195,188,382),(195,195,380,382))],
    'moss':[_tile(*b) for b in ((388,195,508,382),(645,0,830,190),(836,0,1020,190))],
    'crack':[_tile(*b) for b in ((516,195,636,382),(708,195,826,382),(836,195,1020,382))],
    'bone':[_tile(*b) for b in ((3,388,122,508),(196,388,316,508),(388,388,508,508))],
    'water':[_tile(*b) for b in ((516,388,636,508),(645,388,765,508),(772,388,892,508),(900,388,1020,508))],
    'brick':[_tile(*b) for b in ((388,515,508,640),(516,515,636,640),(645,515,765,640))]}
if os.environ.get('IA_PREVIEW'):
    W=1500;x=y=rh=0;items=[(k,s) for k,v in SI.items() for s in v];pos=[]
    for k,s in items:
        t=s.resize((s.width*2,s.height*2),Image.NEAREST)
        if x+t.width>W:x=0;y+=rh+8;rh=0
        pos.append((x,y,t));x+=t.width+8;rh=max(rh,t.height)
    pv=Image.new('RGBA',(W,y+rh+140),(210,205,190,255))
    for x,y,t in pos:pv.alpha_composite(t,(x,y))
    xx=0
    for k,v in ST.items():
        for t in v:pv.alpha_composite(t.resize((48,48),Image.NEAREST),(xx,y+rh+20));xx+=52
    pv.save('/tmp/mt/esgoto_ia_preview.png')
