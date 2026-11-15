import sys,glob,json,os
from PIL import Image,ImageDraw,ImageFont
import numpy as np
tmp,out=sys.argv[1],sys.argv[2];info=json.load(open(tmp+'/info.json'))
A=sorted(glob.glob(tmp+'/A*.png'));B=sorted(glob.glob(tmp+'/B*.png'));n=max(len(A),len(B))
try:font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',20)
except Exception:font=ImageFont.load_default()
fr=[];allp=[]
def get(l,i):
    return Image.open(l[min(i,len(l)-1)]).convert('RGBA')
pix=np.concatenate([np.array(get(A,i))[::4,::4].reshape(-1,4) for i in range(0,len(A),9)]);pix=pix[pix[:,3]>200][:,:3]
side=int(len(pix)**.5);pal=Image.fromarray(pix[:side*side].reshape(side,side,3).astype(np.uint8)).quantize(48,method=Image.MEDIANCUT)
def prep(im):
    a=np.array(im);m=a[...,3]>128;q=Image.fromarray(a[...,:3]).quantize(palette=pal,dither=Image.NONE).convert('RGB');b=np.array(q);b[~m]=(58,92,120);return Image.fromarray(b).resize((im.width*2,im.height*2),Image.NEAREST)
for i in range(n):
    S=Image.new('RGB',(1200,600),(58,92,120));
    for j,(l,lab) in enumerate(((A,'ANTES  nota %s'%info['A']['score']),(B,'DEPOIS  nota %s'%info['B']['score']))):
        S.paste(prep(get(l,i)),(j*600,0));d=ImageDraw.Draw(S);d.text((j*600+14,10),lab,fill=(255,255,255),font=font,stroke_width=2,stroke_fill=(20,10,40))
    fr.append(S)
fr[0].save(out,save_all=True,append_images=fr[1:],duration=33,loop=0);print(out,len(fr))
