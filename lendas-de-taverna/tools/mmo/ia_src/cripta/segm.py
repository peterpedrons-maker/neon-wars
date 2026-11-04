"""Recorta os sprites das folhas de IA da cripta (fundo magenta com grade)."""
from PIL import Image,ImageDraw
import numpy as np
from scipy import ndimage
def segment(path,dil=4,minarea=300):
    im=Image.open(path).convert('RGB');a=np.array(im).astype(int);r,g,b=a[:,:,0],a[:,:,1],a[:,:,2]
    bg=(r>150)&(b>150)&(g<0.62*np.minimum(r,b))&(np.abs(r-b)<75)
    fg=~bg
    fg=ndimage.binary_opening(fg,iterations=1)
    lab,n=ndimage.label(ndimage.binary_dilation(fg,iterations=dil))
    out=[]
    for i,sl in enumerate(ndimage.find_objects(lab)):
        m=(lab[sl]==i+1)&ndimage.binary_dilation(fg[sl],iterations=1)
        if m.sum()<minarea:continue
        al=fg[sl]&m
        holes=ndimage.binary_fill_holes(al)&~al
        hl,hn=ndimage.label(holes)
        for k in range(1,hn+1):
            if (hl==k).sum()<260:al|=(hl==k)
        sub_=a[sl];mg=(sub_[:,:,0]>140)&(sub_[:,:,2]>140)&(sub_[:,:,1]<0.62*np.minimum(sub_[:,:,0],sub_[:,:,2]))&(np.abs(sub_[:,:,0]-sub_[:,:,2])<75)
        al=al&~mg
        rgba=np.dstack([a[sl],(al*255)]).astype('uint8');img=Image.fromarray(rgba,'RGBA');bb=img.getbbox()
        if bb:img=img.crop(bb)
        out.append((sl[0].start,sl[1].start,img))
    out.sort(key=lambda t:(round(t[0]/110),t[1]))
    return [o[2] for o in out]
if __name__=='__main__':
    DIL={'c1':4,'c2':1,'c3':3,'c4':4}
    for n in ['c1','c2','c3','c4']:
        sp=segment(f'/home/user/neon-wars/lendas-de-taverna/tools/mmo/ia_src/cripta/{n}.jpg',dil=DIL[n],minarea=120)
        print(n,len(sp))
        W=1500;x=y=rh=0;pos=[]
        for k,s in enumerate(sp):
            s2=s if max(s.size)<=260 else s.resize((int(s.width*260/max(s.size)),int(s.height*260/max(s.size))))
            if x+s2.width>W:x=0;y+=rh+22;rh=0
            pos.append((x,y,s2));x+=s2.width+12;rh=max(rh,s2.height)
        im=Image.new('RGBA',(W,y+rh+30),(60,40,70,255));d=ImageDraw.Draw(im)
        for k,(x,y,s) in enumerate(pos):im.alpha_composite(s,(x,y+12));d.text((x,y),str(k),fill=(255,255,0,255))
        im.save(f'/tmp/mt/cseg_{n}.png')
