import json,os
from PIL import Image,ImageDraw,ImageFilter,ImageChops
G=json.load(open('/tmp/ic/G.json'));OUT='/home/user/neon-wars/hearthblade/assets/skills/';os.makedirs(OUT,exist_ok=True)
def hexc(h):return tuple(int(h[i:i+2],16) for i in (1,3,5))
def mix(a,b,t):return tuple(int(a[i]+(b[i]-a[i])*t) for i in range(3))
for id,(g,col) in G.items():
    acc=hexc(col);raw=Image.open(f'/tmp/ic/raw/{id}.png').convert('RGBA')
    a=raw.split()[3].resize((32,32),Image.BOX).point(lambda v:255 if v>90 else 0)   # máscara em 32px
    a=a.resize((64,64),Image.NEAREST)
    # contorno escuro (2px em 64)
    out=a.filter(ImageFilter.MaxFilter(5)).point(lambda v:255 if v>0 else 0)
    tile=Image.new('RGBA',(64,64),(13,11,17,255));d=ImageDraw.Draw(tile)
    for r in range(30,0,-2):  # brilho radial discreto
        t=1-r/30;d.ellipse([32-r,32-r,32+r,32+r],fill=mix((13,11,17),mix(acc,(0,0,0),.55),t*.9)+(255,))
    d.rectangle([0,0,63,63],outline=mix(acc,(0,0,0),.45)+(255,),width=2);d.rectangle([2,2,61,61],outline=mix(acc,(255,255,255),.1)+(70,),width=1)
    # glifo: 3 faixas de cor (claro->cor->escuro), estilo pixel
    light=mix(acc,(255,255,255),.62);mid=acc;dark=mix(acc,(0,0,0),.35)
    glyph=Image.new('RGBA',(64,64),(0,0,0,0));gp=glyph.load();ap=a.load()
    ys=[y for y in range(64) for x in range(64) if ap[x,y]];y0,y1=min(ys),max(ys)
    for y in range(64):
        for x in range(64):
            if ap[x,y]:
                t=(y-y0)/max(1,(y1-y0));c=light if t<.3 else mid if t<.68 else dark
                gp[x,y]=c+(255,)
    # realce de 1px no topo-esquerda
    hl=ImageChops.subtract(a,a.transform(a.size,Image.AFFINE,(1,0,2,0,1,2)))
    hp=hl.load()
    for y in range(64):
        for x in range(64):
            if hp[x,y]>0 and ap[x,y]:gp[x,y]=mix(light,(255,255,255),.6)+(255,)
    ol=Image.new('RGBA',(64,64),(10,6,4,255));tile.paste(ol,(0,0),out)
    tile.alpha_composite(glyph)
    tile.save(OUT+id+'.png',optimize=True)
print(len(G))
