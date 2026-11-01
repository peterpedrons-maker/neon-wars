"""Interiores das casas da cidade (Pixel Crawler). Usado por build_town2.py"""
import random
IP=L('Environment/Structures/Buildings/Interior/Interior_Props_01.png');IW=L('Environment/Structures/Buildings/Interior/Interior_Walls_01.png')
def ipc(b):
    im=IP.crop(b);bb=im.getbbox();return im.crop(bb) if bb else im
BOX=dict(counter=(112,225,210,258),shelf=(48,98,98,140),rack=(175,145,226,200),furnace=(272,48,333,146),oven=(388,45,436,146),
  banner1=(232,0,268,58),banner2=(325,0,362,58),plants=(0,350,86,384),door=(133,177,176,226),bed=(0,293,50,346),
  table=(0,225,64,285),bookcase=(48,98,98,140),chest=(66,283,100,320),crate=(155,257,200,290),window=(66,177,100,225),
  potions=(520,286,598,340),barrel=(224,100,246,130),anvilish=(150,290,190,330))
SP={k:ipc(b) for k,b in BOX.items()}
pass
FLOORS=[IW.crop((0,322,80,400)),IW.crop((80,322,160,400)),IW.crop((160,322,240,400)),IW.crop((240,322,320,400))]
WALLS=[IW.crop((200,70,284,140)),IW.crop((104,70,188,140)),IW.crop((10,70,94,140)),IW.crop((296,70,380,140))]

import json as _json
_ipa=np.array(IP)[:,:,3]>0
_lab,_n=ndimage.label(_ipa)
_META=[]
for _i,_sl in enumerate(ndimage.find_objects(_lab)):
    _y,_x=_sl
    if (_lab[_sl]==_i+1).sum()<20:continue
    _META.append((_x.start,_y.start,_x.stop,_y.stop))
def SPI(i):
    b=_META[i];return IP.crop(b)
def _bottle(col,i):
    xs=[13,29,45,61];ys=[(10,20),(25,35),(41,51)]
    x=xs[i%4];y0,y1=ys[col%3];return SP['potions'].crop((x-1,y0-1,x+9,y1))
def shelf_potions(seed):
    sh=SP['shelf'].copy();r=random.Random(seed)
    for k in range(4):
        b=_bottle(r.randrange(3),r.randrange(4));sh.alpha_composite(b,(10+k*9,27-b.height))
    return sh
SP.update(dict(rug=SPI(100),bear=SPI(8),window=SPI(34),window2=SPI(35),wardrobe=SPI(10),chand=SPI(25),rtable=SPI(7),chair=SPI(6),bench=SPI(31),bluerug=SPI(33),stove=SPI(2),sidetable=SPI(56),barrel=SPI(86),blank=Image.new('RGBA',(2,2),(0,0,0,0)),pshelf1=shelf_potions(1),pshelf2=shelf_potions(2),pshelf3=shelf_potions(3),crate=SPI(76),chest=SPI(58)))
IW_,IH_=200,236
def autocol(spr,r=5,dy=-2):
    w=spr.width;n=max(1,int(w//8));x0=-(w/2)+r+1;st=(w-2*r-2)/max(1,n-1) if n>1 else 0
    return [(round(x0+i*st) if n>1 else 0,dy,r) for i in range(n)]
def interior(kind,seed=1):
    wi={'mer':0,'fer':1,'alq':0,'mes':2,'cof':1,'lei':3}[kind];fi=wi
    fl=FLOORS[fi].crop((16,16,64,64));im=Image.new('RGBA',(IW_,IH_),(0,0,0,255))
    for y in range(0,IH_,48):
        for x in range(0,IW_,48):im.alpha_composite(fl,(x,y))
    wl=WALLS[wi]
    for x in range(-6,IW_,wl.width-8):im.alpha_composite(wl,(x,-12))
    bh=26;by=IH_-bh;gx=IW_//2
    d=ImageDraw.Draw(im)
    d.rectangle((gx-17,by-2,gx+17,IH_),fill=(60,36,20,255));d.rectangle((gx-14,by,gx+14,IH_),fill=(236,224,170,255));d.rectangle((gx-14,by,gx+14,by+3),fill=(190,170,110,255))
    d.rectangle((gx-11,IH_-9,gx+11,IH_-3),fill=(120,70,60,255),outline=(70,40,30,255))
    # parede da frente = camada própria (desenhada POR CIMA dos objetos), com a abertura da porta transparente
    band=wl.crop((0,30,wl.width,60));BAND=Image.new('RGBA',(IW_,bh),(0,0,0,0))
    for x in range(-6,IW_,band.width-4):BAND.alpha_composite(band.crop((0,0,band.width,bh)),(x,0))
    for xx in range(gx-17,gx+18):
        for yy in range(bh):BAND.putpixel((xx,yy),(0,0,0,0))
    ImageDraw.Draw(BAND).line((gx-18,0,gx-18,bh),fill=(60,36,20,255));ImageDraw.Draw(BAND).line((gx+18,0,gx+18,bh),fill=(60,36,20,255))
    cx=IW_//2;props=[];flat=[]
    def P(n,x,y,col=None,auto=False):
        sp=SP[n];props.append((sp,x,y,(autocol(sp) if auto else (col or []))))
    def F(n,x,y):   # tapete no chão (sem colisão)
        sp=SP[n];im.alpha_composite(sp,(x-sp.width//2,y-sp.height//2))
    CT=[(-40,0,8),(-20,0,8),(0,0,8),(20,0,8),(40,0,8)]
    def COUNTER(y):
        c=SP['counter'];h=c.height;big=Image.new('RGBA',(IW_,h),(0,0,0,0))
        for x in range(0,IW_,16):big.alpha_composite(c.crop((14,0,30,h)),(x,0))
        big.alpha_composite(c.crop((0,0,14,h)),(0,0));big.alpha_composite(c.crop((c.width-60,0,c.width,h)),(IW_-60,0))
        props.append((big,IW_//2,y,[(dx-IW_//2,0,8) for dx in range(6,IW_-4,12)]))
    pass
    if kind=='mer':
        P('window',34,46);P('window',IW_-34,46);P('bear',cx,40);P('shelf',cx-62,72,auto=True);P('shelf',cx+62,72,auto=True)
        COUNTER(128);P('barrel',26,150,auto=True);P('crate',IW_-26,150,auto=True);P('plants',38,IH_-10,auto=True);NPC=(cx,112)
    elif kind=='fer':
        P('furnace',44,82,auto=True);P('oven',IW_-40,82,auto=True);P('rack',cx,62);COUNTER(128);P('barrel',24,160,auto=True);P('crate',IW_-24,160,auto=True);P('barrel',IW_-28,IH_-12,auto=True);NPC=(cx,112)
    elif kind=='alq':
        P('window',34,46);P('pshelf1',cx-52,72,auto=True);P('pshelf2',cx+52,72,auto=True);P('pshelf3',cx,68,auto=True);COUNTER(128);P('plants',38,IH_-10,auto=True);P('plants',IW_-38,IH_-10,auto=True);NPC=(cx,112)
    elif kind=='mes':
        P('banner1',34,56);P('banner2',IW_-34,56);P('chand',cx,24);P('shelf',cx,70,auto=True);P('table',cx,128,[(-18,0,9),(0,0,9),(18,0,9)]);P('plants',38,IH_-10,auto=True);P('plants',IW_-38,IH_-10,auto=True);P('bench',30,150,auto=True);P('bench',IW_-30,150,auto=True);NPC=(cx,96)
    elif kind=='cof':
        P('window',34,46);P('wardrobe',IW_-32,86,auto=True);P('rack',cx-8,62);COUNTER(128);P('chest',26,150,auto=True);P('chest',IW_-26,160,auto=True);P('barrel',30,IH_-12,auto=True);NPC=(cx,112)
    else:
        P('banner1',34,56);P('banner2',IW_-34,56);P('bear',cx,40);P('shelf',cx-58,72,auto=True);P('shelf',cx+58,72,auto=True);COUNTER(128);P('crate',26,150,auto=True);P('crate',IW_-26,150,auto=True);NPC=(cx,112)
    return im,props,NPC,BAND
