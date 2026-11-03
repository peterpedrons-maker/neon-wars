"""Moldura do HUD do herói (IA): recorta a variação de baixo, abre os vãos (retrato, barra de vida, barra de XP) como transparência
e grava mmo/assets/ui2/hud_frame.png + hud_frame.json (posição dos vãos em frações da imagem). Uso: /usr/bin/python3 hud_ia.py"""
import os,json
from PIL import Image
import numpy as np
from scipy import ndimage
H=os.path.dirname(os.path.abspath(__file__));OUT=os.path.join(H,'..','..','mmo','assets','ui2')
im=np.array(Image.open(os.path.join(H,'ia_src','city','hud.jpg')).convert('RGB')).astype(int)
r,g,b=im[:,:,0],im[:,:,1],im[:,:,2]
mag=(r>140)&(b>140)&(g<130)&(r-g>60)&(b-g>60)
lab,n=ndimage.label(mag);alpha=np.full(mag.shape,255,np.uint8)
sizes=ndimage.sum(mag,lab,range(1,n+1));objs=ndimage.find_objects(lab)
slots={}
for i,sl in enumerate(objs):
    if sizes[i]<300:continue
    y0,y1,x0,x1=sl[0].start,sl[0].stop,sl[1].start,sl[1].stop
    if y0==0 and x0==0:alpha[lab==i+1]=0;continue                 # fundo externo
    if y0<400:continue                                              # só a variação de baixo
    kind='face' if x1-x0<250 and y1-y0>150 else 'hp' if y1-y0>30 and x1-x0>400 else 'xp'
    ym=(y0+y1)//2
    if kind in('hp','xp'):                                          # estende o vão até a tampa dourada (o resto escuro da barra vira transparente também)
        x=x1
        while x<im.shape[1]-2:
            pr,pg,pb=im[ym,x];
            if pr>140 and pg>100 and pb<110:break
            x+=1
        x1=x-1
    slots[kind]=(x0,y0,x1,y1)
    if kind=='face':alpha[lab==i+1]=0
    else:alpha[y0:y1,x0:x1]=0
alpha[:385,:]=0
# limites da moldura
ys,xs=np.where(alpha>0);fy0,fy1,fx0,fx1=ys.min(),ys.max()+1,xs.min(),xs.max()+1
rgba=np.dstack([im.astype('uint8'),alpha])[fy0:fy1,fx0:fx1];fr=Image.fromarray(rgba,'RGBA')
# reduz com média premultiplicada (bordas duras)
TW=440;TH=round(fr.height*TW/fr.width)
p=fr.convert('RGBa').resize((TW,TH),Image.BOX).convert('RGBA');a=np.array(p);a[:,:,3]=np.where(a[:,:,3]>110,255,0);p=Image.fromarray(a,'RGBA')
p.save(os.path.join(OUT,'hud_frame.png'))
W0,H0=fx1-fx0,fy1-fy0
J={k:[(v[0]-fx0)/W0,(v[1]-fy0)/H0,(v[2]-fx0)/W0,(v[3]-fy0)/H0] for k,v in slots.items()};J['ratio']=TH/TW
json.dump(J,open(os.path.join(OUT,'hud_frame.json'),'w'));print(TW,TH,J)
