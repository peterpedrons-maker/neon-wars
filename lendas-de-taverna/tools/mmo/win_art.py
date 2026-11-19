"""Processa a arte das janelas (assets/kit/win/src/*.jpg, geradas pelo dono) -> PNGs pixelados em assets/kit/win/.
pagina: recorta a página, fundo cinza vira transparente.  capa: moldura de couro (miolo e fora transparentes).
nicho/mochila/loja/mestre: fundos opacos reduzidos. Reduz com LANCZOS para largura nativa W e quantiza (sem dither)."""
import numpy as np, sys, os
from PIL import Image
from scipy import ndimage as ndi
D=os.path.join(os.path.dirname(__file__),'..','..','mmo','assets','kit','win');S=os.path.join(D,'src')
def gray_mask(a,tol=16):
    r,g,b=[a[...,i].astype(int) for i in range(3)]
    return (np.max(a[...,:3],2).astype(int)-np.min(a[...,:3],2)<tol)&(r>40)&(r<190)
def flood(mask,seeds):
    lab,_=ndi.label(mask);keep=set(lab[y,x] for y,x in seeds if mask[y,x]);return np.isin(lab,list(keep))
def reduce(im,W,colors):
    h=round(im.height*W/im.width);im=im.resize((W,h),Image.LANCZOS)
    a=im.getchannel('A') if im.mode=='RGBA' else None
    q=im.convert('RGB').quantize(colors,dither=Image.NONE).convert('RGB')
    if a is not None:
        a=a.point(lambda v:255 if v>110 else 0);q=q.convert('RGBA');q.putalpha(a)
    return q
def pagina():
    im=Image.open(os.path.join(S,'pagina.jpg')).convert('RGB');a=np.array(im)
    m=gray_mask(a,14);out=flood(m,[(2,2),(2,a.shape[1]-3),(a.shape[0]-3,2),(a.shape[0]-3,a.shape[1]-3)])
    out=ndi.binary_dilation(out,iterations=1)
    rgba=np.dstack([a,np.where(out,0,255).astype(np.uint8)]);ys,xs=np.where(~out);box=(xs.min(),ys.min(),xs.max()+1,ys.max()+1)
    Image.fromarray(rgba,'RGBA').crop(box).save(os.path.join(D,'_pagina_full.png'))
    reduce(Image.fromarray(rgba,'RGBA').crop(box),int(sys.argv[2]) if len(sys.argv)>2 else 170,40).save(os.path.join(D,'pagina.png'))
def capa():
    im=Image.open(os.path.join(S,'capa.jpg')).convert('RGB');a=np.array(im);H,W=a.shape[:2]
    m=gray_mask(a,14);out=flood(m,[(2,2),(2,W-3),(H-3,2),(H-3,W-3)]);hole=flood(m,[(H//2,W//2)])
    al=np.where(out|hole,0,255).astype(np.uint8);rgba=np.dstack([a,al])
    im2=Image.fromarray(rgba,'RGBA');ys,xs=np.where(al>0);box=(xs.min(),ys.min(),xs.max()+1,ys.max()+1);im2=im2.crop(box)
    ys2,xs2=np.where(hole);print('hole in crop',xs2.min()-box[0],ys2.min()-box[1],xs2.max()-box[0],ys2.max()-box[1],'size',im2.size)
    im2.save(os.path.join(D,'_capa_full.png'));reduce(im2,int(sys.argv[2]) if len(sys.argv)>2 else 170,48).save(os.path.join(D,'capa.png'))
def fundo(n,W,colors=56):
    im=Image.open(os.path.join(S,n+'.jpg')).convert('RGB');reduce(im,W,colors).convert('RGB').save(os.path.join(D,n+'.png'))
if __name__=='__main__':
    w=sys.argv[1] if len(sys.argv)>1 else 'all'
    if w in('all','pagina'):pagina()
    if w in('all','capa'):capa()
    if w=='all':
        fundo('nicho',122,64);fundo('mochila',170,56);fundo('loja',170,56);fundo('mestre',170,56)
