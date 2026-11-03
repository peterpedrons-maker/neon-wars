"""Arte da Floresta dos Goblins gerada por IA (folhas em ia_src/): recorta cada sprite do fundo verde, reduz para a escala do jogo,
quantiza numa paleta única (coesão) e define as áreas de colisão. Uso: exec() dentro de build_zone2.py (THEME=goblin)."""
import os,sys
from PIL import Image
import numpy as np
_H=globals().get('HERE') or os.getcwd()
sys.path.insert(0,os.path.join(_H,'ia_src'))
from seg import segment
SH={n:segment(os.path.join(_H,'ia_src',n+'.jpg'),dil=3,minarea=120) for n in ('s1','s2','s3')}
def _scale(im,f):
    w,h=max(1,round(im.width*f)),max(1,round(im.height*f))
    p=im.convert('RGBa').resize((w,h),Image.BOX).convert('RGBA')
    a=np.array(p);a[:,:,3]=np.where(a[:,:,3]>110,255,0);return Image.fromarray(a,'RGBA')
# kind: tree (tronco), wide (várias bolinhas ao longo da largura), post (poste fino), wall (parede densa), flat (decoração sem colisão), none (sem colisão, em pé)
CAT={
 'pine':[('s3',i,.40,'tree') for i in (0,1,2,5)],
 'deadskull':[('s3',i,.40,'tree') for i in (3,4)],
 'twisted':[('s1',0,.44,'tree'),('s1',1,.44,'tree')],
 'bigtree':[('s1',2,.44,'tree')],
 'stump':[('s3',6,.20,'wide'),('s3',7,.20,'wide')],
 'log':[('s3',8,.21,'wide'),('s3',9,.21,'wide')],
 'bush':[('s3',10,.25,'wide'),('s3',11,.25,'wide'),('s3',12,.25,'wide')]+[('s1',i,.26,'wide') for i in (3,4,7,8)],
 'thorn':[('s3',20,.26,'wide'),('s3',21,.26,'wide'),('s1',5,.26,'wide'),('s1',6,.26,'wide'),('s1',9,.26,'wide'),('s1',10,.26,'wide')],
 'rockbig':[('s3',13,.29,'wide'),('s3',14,.29,'wide'),('s3',15,.29,'wide')],
 'rocksm':[('s3',16,.30,'none'),('s3',17,.30,'flat'),('s3',18,.30,'flat'),('s1',14,.28,'none'),('s1',15,.28,'none')],
 'mush':[('s3',i,.20,'none') for i in (26,27,28,29)],
 'tent':[('s1',24,.28,'wide'),('s1',25,.28,'wide'),('s1',27,.28,'wide')],
 'drums':[('s1',29,.22,'wide')],
 'cauldron':[('s1',36,.13,'wide')],
 'totem':[('s1',34,.28,'post'),('s1',35,.28,'post')],
 'stake':[('s2',i,.14,'post') for i in (0,1,2,3,4)],
 'bonepile':[('s2',i,.17,'flat') for i in (5,6,7,8,9)],
 'palisade':[('s2',10,.20,'wall'),('s2',11,.20,'wall'),('s2',12,.20,'wall')],
 'fence':[('s2',i,.17,'wall') for i in (18,19,20)],
 'barricade':[('s2',13,.20,'wall'),('s2',14,.20,'wall')],
 'banner':[('s2',15,.22,'post'),('s2',16,.22,'post')],
 'torch':[('s2',21,.17,'post'),('s2',22,.17,'post')],
 'puddle':[('s3',i,.25,'flat') for i in (22,23,24,25)],
 'twig':[('s3',i,.30,'flat') for i in (30,31,32,33,34,19)],
 'bone':[('s3',i,.30,'flat') for i in (35,36,42,38)],
 'flower':[('s3',i,.30,'flat') for i in (37,44,45,49)],
}
def _col(kind,w,h):
    if kind=='tree':return [(0,-2,5)]
    if kind=='post':return [(0,-3,3.5)]
    if kind in('flat','none'):return None
    if kind=='wall':
        n=max(1,round(w/8));return [(((i/(n-1))-.5)*(w-8) if n>1 else 0,-3,4.6) for i in range(n)]
    r=max(4.5,min(8,h*.17));fw=max(8,w*.78);n=max(1,round(fw/9))
    return [(((i/(n-1))-.5)*(fw-8) if n>1 else 0,-max(3,h*.12),r) for i in range(n)]
_raw={k:[(_scale(SH[s][i],f),kd) for (s,i,f,kd) in v] for k,v in CAT.items()}
# paleta única (coesão): quantiza todos os sprites juntos
_all=[im for v in _raw.values() for im,_ in v]
_px=np.concatenate([np.array(im)[np.array(im)[:,:,3]>0][:,:3] for im in _all])
_pal=Image.fromarray(_px[:60000].reshape(-1,1,3).astype('uint8'),'RGB').quantize(colors=88,method=Image.MEDIANCUT,dither=Image.NONE)
def _quant(im):
    a=np.array(im);m=a[:,:,3]>0
    rgb=Image.fromarray(a[:,:,:3],'RGB').quantize(palette=_pal,dither=Image.NONE).convert('RGB')
    out=np.array(rgb);out=np.dstack([out,np.where(m,255,0)]).astype('uint8');return Image.fromarray(out,'RGBA')
GI={}
for k,v in _raw.items():
    L=[]
    for im,kd in v:
        q=im if k in('cauldron','torch','mush') else _quant(im);q.col=_col(kd,q.width,q.height);q.kind=kd;L.append(q)
    GI[k]=L
if os.environ.get('IA_PREVIEW'):
    W=1400;x=y=rh=0;items=[(k,s) for k,v in GI.items() for s in v];pos=[]
    for k,s in items:
        t=s.resize((s.width*2,s.height*2),Image.NEAREST)
        if x+t.width>W:x=0;y+=rh+8;rh=0
        pos.append((x,y,t));x+=t.width+8;rh=max(rh,t.height)
    pv=Image.new('RGBA',(W,y+rh+8),(52,86,44,255))
    for x,y,t in pos:pv.alpha_composite(t,(x,y))
    pv.save(os.path.join(_H,'ia_out_preview.png'))
