"""Recorta sprites de folhas geradas por IA com fundo magenta."""
from PIL import Image,ImageDraw
import numpy as np
from scipy import ndimage
def keyout(im):
    a=np.array(im.convert('RGB')).astype(int);r,g,b=a[:,:,0],a[:,:,1],a[:,:,2]
    mag=(r>140)&(b>140)&(g<130)&(r-g>60)&(b-g>60)
    fg=~mag
    fg=ndimage.binary_opening(fg,iterations=1)
    e=ndimage.binary_erosion(fg,iterations=1);edge=fg&~e
    halo=edge&(r>g+45)&(b>g+25);fg=fg&~halo
    return a,fg
def segment(path,dil=3,minarea=150,tintfix=True):
    im=Image.open(path);a,fg=keyout(im)
    if tintfix:
        r,g,b=a[:,:,0],a[:,:,1],a[:,:,2]
        # tira o magenta que vazou nas bordas e nos vidros: não mexe nos vermelhos/roxos intencionais (precisa ser claro e rosado)
        pass
    lab,n=ndimage.label(ndimage.binary_dilation(fg,iterations=dil))
    out=[]
    for i,sl in enumerate(ndimage.find_objects(lab)):
        m=(lab[sl]==i+1)&fg[sl]
        if m.sum()<minarea:continue
        rgba=np.dstack([a[sl].astype('uint8'),(m*255).astype('uint8')])
        img=Image.fromarray(rgba,'RGBA');bb=img.getbbox()
        if bb:img=img.crop(bb)
        out.append((sl[0].start,sl[1].start,img))
    out.sort(key=lambda t:(round(t[0]/60),t[1]))
    return [o[2] for o in out]
def contact(sp,out,W=1500):
    x=y=rh=0;pos=[]
    for k,s in enumerate(sp):
        if x+max(s.width,24)>W:x=0;y+=rh+22;rh=0
        pos.append((x,y));x+=max(s.width,24)+12;rh=max(rh,s.height)
    im=Image.new('RGBA',(W,y+rh+30),(60,90,60,255));d=ImageDraw.Draw(im)
    for k,(s,(x,y)) in enumerate(zip(sp,pos)):
        im.alpha_composite(s,(x,y+14));d.rectangle([x,y,x+16,y+11],fill=(0,0,0,255));d.text((x+1,y),str(k),fill=(255,255,0,255))
    im.save(out)
if __name__=='__main__':
    for n in ['decor','portal','fountain','iconsA','iconsB']:
        sp=segment(n+'.jpg',dil=3 if n=='decor' else 14,minarea=150)
        print(n,len(sp),[s.size for s in sp][:40]);contact(sp,'/tmp/mt/city_%s.png'%n)
