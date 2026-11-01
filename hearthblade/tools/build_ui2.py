"""Recorta/redimensiona as peças do 'Pixel Fantasy UI Pack' (Zanyar's Asset Store) usadas no MMO.
Uso: /usr/bin/python3 tools/build_ui2.py <pasta_do_pack>   (o pack bruto NÃO vai pro repositório)"""
import sys,json,os
from PIL import Image
import numpy as np
P=sys.argv[1]; O='mmo/assets/ui2/'; os.makedirs(O,exist_ok=True)
def trim(im):
    a=np.array(im)[:,:,3];ys,xs=np.where(a>20);return im.crop((xs.min(),ys.min(),xs.max()+1,ys.max()+1))
def ld(p): return Image.open(os.path.join(P,p)).convert('RGBA')
def save(im,n,w):
    im=trim(im);h=round(im.height*w/im.width);im.resize((w,h),Image.LANCZOS).save(O+n,optimize=True);return (w,h)
info={}
info['panel']=save(ld('panels/panel-frame.png'),'panel.png',700)
info['btn']=save(ld('buttons/button-normal.png'),'btn.png',480)
info['btn_gold']=save(ld('buttons/button-hover.png'),'btn_gold.png',480)
info['btn_press']=save(ld('buttons/button-pressed.png'),'btn_press.png',480)
info['dialog']=save(ld('misc/dialog-box.png'),'dialog.png',560)
info['coin']=save(ld('misc/coin-plaque.png'),'coin.png',420)
# barras: o miolo colorido vira um "buraco" transparente; o jogo desenha o preenchimento por baixo
for n,cond,fn in (('bar_hp',lambda a:(a[:,:,0]>200)&(a[:,:,1]<40)&(a[:,:,2]<40),'bars/bar-health.png'),
                  ('bar_mp',lambda a:(a[:,:,2]>200)&(a[:,:,0]<60)&(a[:,:,1]>80)&(a[:,:,1]<160),'bars/bar-mana.png')):
    im=ld(fn);a=np.array(im);m=cond(a);ys,xs=np.where(m)
    x0,x1,y0,y1=xs.min(),xs.max(),ys.min(),ys.max()
    a[y0:y1+1,x0:x1+1,3]=0   # vira janela
    im=Image.fromarray(a);b=np.array(im)[:,:,3];yy,xx=np.where(b>20);bx0,by0=xx.min(),yy.min()
    im=trim(im);w=380;s=w/im.width;im=im.resize((w,round(im.height*s)),Image.LANCZOS);im.save(O+n+'.png',optimize=True)
    info[n]={'size':im.size,'hole':[(x0-bx0)*s/w,(y0-by0)*s/im.height,(x1-bx0+1)*s/w,(y1-by0+1)*s/im.height]}
# ícones (grade 4x2 de 560px)
sh=ld('icons/icons-sheet.png');names=['heart','mana','coin','sword','shield','potion','key','star']
for i,n in enumerate(names):
    c=sh.crop(((i%4)*560,(i//4)*560,(i%4)*560+560,(i//4)*560+560));c=trim(c);c.thumbnail((96,96),Image.LANCZOS);c.save(O+'i_'+n+'.png',optimize=True)
json.dump(info,open(O+'ui2.json','w'),indent=1,default=lambda o:int(o));print(json.dumps(info,default=lambda o:int(o)))
