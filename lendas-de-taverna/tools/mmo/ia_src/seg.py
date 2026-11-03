from PIL import Image,ImageDraw
import numpy as np
from scipy import ndimage
def segment(path,T=26,dil=5,minarea=250):
    im=Image.open(path).convert('RGB');a=np.array(im).astype(int)
    bg=np.median(a[:6].reshape(-1,3),axis=0)
    d=np.abs(a-bg).sum(axis=2)
    fg=d>T
    fg=ndimage.binary_opening(fg,iterations=1)
    lab,n=ndimage.label(ndimage.binary_dilation(fg,iterations=dil))
    out=[]
    for i,sl in enumerate(ndimage.find_objects(lab)):
        m=(lab[sl]==i+1)&ndimage.binary_dilation(fg[sl],iterations=1)
        if m.sum()<minarea:continue
        sub=a[sl]
        al=fg[sl]&m
        # preenche buracos pequenos (interior verde de arbustos/musgo)
        holes=ndimage.binary_fill_holes(al)&~al
        hl,hn=ndimage.label(holes)
        for k in range(1,hn+1):
            if (hl==k).sum()<220:al|=(hl==k)
        rgba=np.dstack([sub,(al*255)]).astype('uint8')
        img=Image.fromarray(rgba,'RGBA')
        bb=img.getbbox()
        if bb:img=img.crop(bb)
        out.append((sl[0].start,sl[1].start,img))
    out.sort(key=lambda t:(round(t[0]/70),t[1]))
    return [o[2] for o in out]
if __name__=='__main__':
    import sys
    for n in ['s1','s2','s3']:
        sp=segment(n+'.jpg')
        print(n,len(sp))
        W=1400;x=y=rh=0;pos=[]
        for k,s in enumerate(sp):
            if x+s.width>W:x=0;y+=rh+18;rh=0
            pos.append((x,y));x+=s.width+10;rh=max(rh,s.height)
        im=Image.new('RGBA',(W,y+rh+20),(200,60,200,255));d=ImageDraw.Draw(im)
        for k,(s,(x,y)) in enumerate(zip(sp,pos)):
            im.alpha_composite(s,(x,y+10));d.text((x,y),str(k),fill=(255,255,0,255))
        im.save('/tmp/mt/seg_%s.png'%n)
