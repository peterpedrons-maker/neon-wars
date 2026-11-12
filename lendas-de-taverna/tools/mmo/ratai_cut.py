"""Corta a folha de IA (pixel art) do Rei dos Ratos: 6x3, fundo magenta. Uso: python3 ratai_cut.py <png> <pasta_saida>"""
import sys,os
import numpy as np
from PIL import Image
from scipy import ndimage as ND
src,out=sys.argv[1],sys.argv[2];os.makedirs(out,exist_ok=True)
im=Image.open(src).convert('RGB');W,H=im.size;nc,nr=6,3;fr=[]
for r in range(nr):
    for c in range(nc):
        cell=np.array(im.crop((round(W*c/nc)+4,round(H*r/nr)+4,round(W*(c+1)/nc)-4,round(H*(r+1)/nr)-4)))
        cell[:60,:75]=(255,0,255)                                 # número do quadro
        a=cell.astype(int);bg=(a[:,:,0]>150)&(a[:,:,2]>150)&(a[:,:,1]<110)&(abs(a[:,:,0]-a[:,:,2])<70)
        bg=ND.binary_dilation(bg,iterations=1)&~((a[:,:,1]>110))
        al=~bg;lb,n=ND.label(al)
        if n:
            sz=ND.sum(al,lb,range(1,n+1));al=np.isin(lb,[i+1 for i,v in enumerate(sz) if v>sz.max()*.12])
        al=ND.binary_opening(al,iterations=1)
        rgba=np.dstack([cell,np.where(al,255,0).astype(np.uint8)]);f=Image.fromarray(rgba,'RGBA');b=f.getchannel('A').getbbox();fr.append(f.crop(b))
for i,f in enumerate(fr):f.save('%s/q%02d.png'%(out,i+1))
print([f.size for f in fr][:6])
