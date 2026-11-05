"""Corta folhas de sprites de IA (fundo magenta) em células, limpa o fundo e o halo roxo, normaliza a escala entre folhas e gera GIFs.
Usado para o Grunk (3 folhas). Uso: python3 cut_grid.py <pasta_saida>   (editar SHEETS abaixo)"""
import sys,os
import numpy as np
from PIL import Image,ImageDraw
from scipy import ndimage
UP='/root/.claude/uploads/3ffd125f-a99a-599e-8554-f2b481e86fc1/'
SHEETS=[ # arquivo, colunas, fronteiras de linha (None = igual), nomes das linhas
 ('0fd8bd5f-image.jpg',6,[0,211,424,636,848],['idle','walk','hurt','death']),
 ('3bb35003-image.jpg',8,[0,228,592],['attack','slam']),
 ('7c0f29c5-image.jpg',6,[0,256,512,768],['charge','roar','enrage']),
]
def key(c):
    a=np.array(c).astype(float);m=np.minimum(a[:,:,0],a[:,:,2])-a[:,:,1]
    bg=m>75
    band=ndimage.binary_dilation(bg,iterations=3)&~bg
    bg2=bg|(band&(m>26)&(a[:,:,0]>95))
    band2=ndimage.binary_dilation(bg2,iterations=2)&~bg2
    ex=np.clip(np.minimum(a[:,:,0],a[:,:,2])-a[:,:,1],0,None)
    for ch in(0,2):a[:,:,ch]=np.where(band2,np.clip(a[:,:,ch]-ex*.85,0,255),a[:,:,ch])
    return np.dstack([a.astype('uint8'),np.where(bg2,0,255).astype('uint8')])
def clean(a):
    al=a[:,:,3]>0;lab,n=ndimage.label(ndimage.binary_dilation(al,iterations=3))
    if n>1:
        sz=ndimage.sum(al,lab,range(1,n+1));keep=[i+1 for i,s in enumerate(sz) if s>sz.max()*.015]
        m=np.isin(lab,keep)&al;a=a.copy();a[:,:,3]=np.where(m,255,0)
    return a
def main(out):
    os.makedirs(out,exist_ok=True);anims={}
    for f,nc,ys,names in SHEETS:
        im=Image.open(UP+f).convert('RGB');W,H=im.size;xs=[round(W*i/nc) for i in range(nc+1)]
        sheet={}
        hs=[]
        for r,name in enumerate(names):
            fr=[]
            for c in range(nc):
                cell=im.crop((xs[c]+8,ys[r]+8,xs[c+1]-8,ys[r+1]-8));a=clean(key(cell))
                if (a[:,:,3]>0).sum()<400:continue
                fr.append(Image.fromarray(a,'RGBA'))
            sheet[name]=fr
        # escala da folha: altura mediana das caixas das poses (referência de altura do personagem)
        for name,fr in sheet.items():
            for x in fr:
                b=x.getchannel('A').getbbox()
                if b:hs.append(b[3]-b[1])
        h_ref=float(np.median(hs));k=170.0/h_ref
        for name,fr in sheet.items():
            anims[name]=[x.resize((int(x.width*k),int(x.height*k)),Image.NEAREST) for x in fr]
        print(f,'escala',round(k,2),{n:len(v) for n,v in sheet.items()})
    return anims
if __name__=='__main__':
    out=sys.argv[1];anims=main(out)
    CW,CH=360,300;BG=(52,74,46,255)
    for name,fr in anims.items():
        ims=[]
        for x in fr:
            bg=Image.new('RGBA',(CW,CH),BG);d=ImageDraw.Draw(bg);d.ellipse((CW*.25,CH-52,CW*.75,CH-24),fill=(36,52,34,255))
            bg.alpha_composite(x,((CW-x.width)//2,CH-10-x.height));ims.append(bg.convert('RGB').quantize(64,dither=Image.Dither.NONE))
        dur={'idle':[220]*len(ims),'walk':[110]*len(ims),'hurt':[90,90,110,110,110,110],'death':[130,130,150,180,200,300],'attack':[130,110,100,90,120,130,120,120],'slam':[130,110,110,90,110,160,140,120],'charge':[160,90,70,70,100,130],'roar':[160,160,140,150,150,140],'enrage':[200,170,200,200,200,200]}.get(name,[120]*len(ims))
        dur=(dur+[120]*len(ims))[:len(ims)]
        ims[0].save(f'{out}/grunk_{name}.gif',save_all=True,append_images=ims[1:],duration=dur,loop=0,disposal=2);print(name,len(ims))
