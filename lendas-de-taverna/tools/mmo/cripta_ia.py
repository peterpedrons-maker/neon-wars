"""Arte das Catacumbas gerada por IA (folhas em ia_src/cripta/c1..c4.jpg): recorta cada sprite do fundo magenta, reduz para a escala do jogo,
quantiza numa paleta única e define colisões. Também fatia os tiles de chão (16x16). Uso: exec() dentro de build_cripta.py."""
import os,sys
from PIL import Image
import numpy as np
_H=globals().get('HERE') or os.getcwd()
sys.path.insert(0,os.path.join(_H,'ia_src','cripta'))
from segm import segment
_D=os.path.join(_H,'ia_src','cripta')
_SH={n:segment(os.path.join(_D,n+'.jpg'),dil=d,minarea=120) for n,d in (('c1',4),('c2',1),('c3',3),('c4',4))}
def _split(im,axis):                                   # separa dois objetos colados pelo vão de menor alfa (axis 0 = corta por linhas, 1 = por colunas)
    a=np.array(im)[:,:,3]>0;prof=a.sum(axis=1 if axis==0 else 0);n=len(prof);lo,hi=int(n*.25),int(n*.8)
    cut=lo+int(np.argmin(prof[lo:hi]));parts=[]
    for box in (((0,0,im.width,cut),(0,cut,im.width,im.height)) if axis==0 else ((0,0,cut,im.height),(cut,0,im.width,im.height))):
        p=im.crop(box);bb=p.getbbox();parts.append(p.crop(bb) if bb else p)
    return parts
_c2=list(_SH['c2'])
_a,_b=_split(_c2[34],0);_c,_d=_split(_c2[41],1)
_X={'c2_sword1':_a,'c2_crate':_b,'c2_barrel2':_c,'c2_crate2':_d}      # peças que a IA entregou coladas
def _get(s,i):return _X[i] if isinstance(i,str) else _SH[s][i]
def _scale(im,f):
    w,h=max(1,round(im.width*f)),max(1,round(im.height*f))
    p=im.convert('RGBa').resize((w,h),Image.BOX).convert('RGBA')
    a=np.array(p);a[:,:,3]=np.where(a[:,:,3]>110,255,0);return Image.fromarray(a,'RGBA')
# kind: wide (colisão ao longo da largura), post (poste fino), tree, flat (sem colisão, no chão), none (em pé sem colisão), wall (parede densa)
CAT={
 'sarc':[('c1',i,.24,'wide') for i in (0,1,2,3)],
 'tomb':[('c1',4,.16,'post'),('c1',5,.15,'post'),('c1',6,.15,'post'),('c1',7,.15,'post'),('c1',8,.15,'post'),('c1',9,.15,'post')],
 'coffin':[('c1',10,.19,'wide'),('c1',11,.19,'wide'),('c1',12,.21,'post')],
 'statue':[('c1',13,.24,'post'),('c1',14,.24,'post'),('c1',15,.24,'post')],
 'altar':[('c1',16,.24,'wide')],
 'pillar':[('c1',17,.235,'post'),('c1',18,.23,'post')],
 'brokenp':[('c1',19,.23,'post'),('c1',20,.23,'post'),('c1',22,.23,'post')],
 'mausdoor':[('c1',21,.28,'wide')],
 'urn':[('c1',23,.18,'post'),('c1',24,.18,'post')],
 'bonepile':[('c2',i,.15,'flat') for i in (0,1,2,3)],
 'chainh':[('c2',4,.23,'none'),('c2',5,.23,'none')],
 'chainfloor':[('c2',6,.18,'flat')],
 'cage':[('c2',8,.21,'post'),('c2',9,.21,'post')],
 'candel':[('c2',28,.18,'post'),('c2',29,.18,'post')],
 'armor':[('c2',26,.21,'post'),('c2',33,.22,'post'),('c2',27,.21,'post')],
 'sword':[('c2','c2_sword1',.2,'post'),('c2',35,.18,'post')],
 'crystal':[('c2',36,.21,'post')],
 'rune':[('c2',37,.25,'flat')],
 'runeb':[('c2',38,.25,'flat')],
 'portal':[('c2',39,.25,'wide')],
 'crate':[('c2','c2_crate',.22,'wide'),('c2','c2_crate2',.22,'wide')],
 'barrel':[('c2',40,.2,'post'),('c2','c2_barrel2',.21,'post'),('c2',41,.21,'post')] if False else [('c2',40,.2,'post'),('c2','c2_barrel2',.21,'post')],
 'coins':[('c2',42,.21,'flat')],
 'chest':[('c2',43,.25,'wide')],
 'sack':[('c2',44,.24,'post')],
 'puddle':[('c3',1,.2,'flat')],
 'moss':[('c3',3,.2,'flat'),('c3',4,.2,'flat')],
 'gate':[('c3',7,.36,'wide')],
 'skullpil':[('c3',6,.32,'post')],
 'portcul':[('c3',9,.26,'wide')],
 'banner':[('c4',0,.22,'none'),('c4',1,.22,'none'),('c4',2,.22,'none')],
 'torchw':[('c4',3,.21,'none'),('c4',4,.21,'none')],
 'stake':[('c4',5,.14,'post'),('c4',6,.14,'post'),('c4',7,.14,'post'),('c4',11,.14,'post')],
 'stalag':[('c4',8,.19,'wide'),('c4',9,.19,'wide'),('c4',12,.2,'wide')],
 'book':[('c4',16,.14,'post')],
 'throne':[('c4',17,.25,'wide')],
 'chest2':[('c4',23,.125,'wide'),('c4',24,.125,'wide')],
 'drip':[('c4',i,.12,'flat') for i in (13,14,15,18,20)],
}
def _col(kind,w,h):
    if kind in('flat','none'):return None
    if kind=='post':return [(0,-2,max(3.5,min(7,w*.28)))]
    if kind=='wall':
        n=max(1,round(w/8));return [(((i/(n-1))-.5)*(w-8) if n>1 else 0,-3,4.6) for i in range(n)]
    r=max(4.5,min(8,h*.17));fw=max(8,w*.78);n=max(1,round(fw/9))
    return [(((i/(n-1))-.5)*(fw-8) if n>1 else 0,-max(3,h*.12),r) for i in range(n)]
_raw={k:[(_scale(_get(s,i),f),kd) for (s,i,f,kd) in v] for k,v in CAT.items()}
_all=[im for v in _raw.values() for im,_ in v]
_px=np.concatenate([np.array(im)[np.array(im)[:,:,3]>0][:,:3] for im in _all])
_pal=Image.fromarray(_px[:80000].reshape(-1,1,3).astype('uint8'),'RGB').quantize(colors=96,method=Image.MEDIANCUT,dither=Image.NONE)
def _quant(im):
    a=np.array(im);m=a[:,:,3]>0
    rgb=Image.fromarray(a[:,:,:3],'RGB').quantize(palette=_pal,dither=Image.NONE).convert('RGB')
    return Image.fromarray(np.dstack([np.array(rgb),np.where(m,255,0)]).astype('uint8'),'RGBA')
CI={}
for k,v in _raw.items():
    L=[]
    for im,kd in v:
        q=_quant(im);q.col=_col(kd,q.width,q.height);q.kind=kd;L.append(q)
    CI[k]=L
# tiles de chão 16x16 (cada célula da folha tem 128 px = tile ampliado 8x)
_c3=Image.open(os.path.join(_D,'c3.jpg')).convert('RGB')
def _tile(cx,cy):
    t=_c3.crop((cx*128+6,cy*128+6,cx*128+122,cy*128+122)).resize((16,16),Image.BOX)
    return t.convert('RGBA')
TL={'plain':[_tile(c,r) for c,r in ((0,0),(1,0),(2,0),(3,0),(0,1),(1,1))],
    'crack':[_tile(c,r) for c,r in ((2,1),(3,1),(0,3))],
    'bone':[_tile(c,r) for c,r in ((4,1),(0,2),(1,2))],
    'blood':[_tile(c,r) for c,r in ((2,2),(3,2))],
    'rune':[_tile(4,2)],
    'dirt':[_tile(c,3) for c in (1,2,3,4)],
    'brick':[_tile(4,0),_tile(6,2),_tile(7,2)]}
if os.environ.get('IA_PREVIEW'):
    W=1500;x=y=rh=0;items=[(k,s) for k,v in CI.items() for s in v];pos=[]
    for k,s in items:
        t=s.resize((s.width*2,s.height*2),Image.NEAREST)
        if x+t.width>W:x=0;y+=rh+8;rh=0
        pos.append((x,y,t));x+=t.width+8;rh=max(rh,t.height)
    pv=Image.new('RGBA',(W,y+rh+140),(52,44,66,255))
    for x,y,t in pos:pv.alpha_composite(t,(x,y))
    xx=0
    for k,v in TL.items():
        for t in v:pv.alpha_composite(t.resize((48,48),Image.NEAREST),(xx,y+rh+20));xx+=52
    pv.save('/tmp/mt/cripta_ia_preview.png')
