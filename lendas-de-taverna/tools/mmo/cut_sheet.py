"""Corta uma folha de sprites gerada por IA (grade de células sobre fundo magenta), remove o magenta e a grade, alinha os quadros e gera GIFs.
Uso: python3 cut_sheet.py <imagem> <pasta_saida>   (grade 6x5, linhas: idle, move, attack, hurt, death)"""
import sys,os
import numpy as np
from PIL import Image
src,out=sys.argv[1],sys.argv[2];os.makedirs(out,exist_ok=True)
im=Image.open(src).convert('RGB');W,H=im.size
xs=[round(W*i/6) for i in range(7)];ys=[round(H*i/5) for i in range(6)]
def key(c):
    """remove o magenta e o halo roxo/rosa das bordas (sangramento de cor do fundo, comum em JPG)"""
    from scipy import ndimage
    a=np.array(c).astype(float);m=np.minimum(a[:,:,0],a[:,:,2])-a[:,:,1]
    bg=m>75
    band=ndimage.binary_dilation(bg,iterations=3)&~bg          # faixa de 3 px ao redor do fundo
    fringe=band&(m>26)&(a[:,:,0]>95)                              # pixels da borda ainda puxados para o magenta
    bg2=bg|fringe
    # mais um passo: borda restante com excesso de magenta é corrigida (de-spill)
    band2=ndimage.binary_dilation(bg2,iterations=2)&~bg2
    ex=np.clip(np.minimum(a[:,:,0],a[:,:,2])-a[:,:,1],0,None)
    for ch in (0,2):a[:,:,ch]=np.where(band2,np.clip(a[:,:,ch]-ex*.85,0,255),a[:,:,ch])
    alpha=np.where(bg2,0,255).astype('uint8')
    return Image.fromarray(np.dstack([a.astype('uint8'),alpha]),'RGBA')
def clean(img):
    a=np.array(img);al=a[:,:,3]>0
    # remove ilhas pequenas (restos de grade/ruído): mantém o maior componente e os próximos
    from scipy import ndimage
    lab,n=ndimage.label(ndimage.binary_dilation(al,iterations=3))
    if n>1:
        sizes=ndimage.sum(al,lab,range(1,n+1));keep=[i+1 for i,s in enumerate(sizes) if s>sizes.max()*.02]
        m=np.isin(lab,keep)&ndimage.binary_dilation(al,iterations=1);a[:,:,3]=np.where(m&al,255,0)
    return Image.fromarray(a,'RGBA')
rows=[('idle',4),('move',6),('attack',6),('hurt',3),('death',6)];res={}
for r,(name,n) in enumerate(rows):
    fr=[]
    for c in range(n):
        cell=im.crop((xs[c]+7,ys[r]+7,xs[c+1]-7,ys[r+1]-7));fr.append(clean(key(cell)))
    res[name]=fr
import pickle
def bbox(f):return f.getchannel('A').getbbox()
def stack(fr,mode):
    bb=[bbox(f) for f in fr];cw=max(b[2]-b[0] for b in bb)+8;ch=max(b[3]-b[1] for b in bb)+8
    outf=[]
    for f,b in zip(fr,bb):
        c=Image.new('RGBA',(cw,ch),(0,0,0,0));crop=f.crop(b)
        x=(cw-crop.width)//2
        y=(ch-crop.height)//2 if mode=='center' else ch-crop.height-4
        c.alpha_composite(crop,(x,y));outf.append(c)
    return outf
import json
json.dump({k:len(v) for k,v in res.items()},open(f'{out}/info.json','w'))
for k,v in res.items():
    st=stack(v,'center' if k in('move','idle','attack','hurt') else 'bottom')
    for i,f in enumerate(st):f.save(f'{out}/{k}_{i}.png')
print('ok')
