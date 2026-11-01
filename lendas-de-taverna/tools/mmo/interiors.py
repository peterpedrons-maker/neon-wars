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
SP['barrel']=BARREL;SP['crate']=BARREL;SP['chest']=BARREL
FLOORS=[IW.crop((0,322,80,400)),IW.crop((80,322,160,400)),IW.crop((160,322,240,400)),IW.crop((240,322,320,400))]
WALLS=[IW.crop((200,70,284,140)),IW.crop((104,70,188,140)),IW.crop((10,70,94,140)),IW.crop((296,70,380,140))]
IW_,IH_=240,272
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
    # parede da frente com a abertura da porta
    band=wl.crop((0,30,wl.width,60))
    bh=26;by=IH_-bh
    for x in range(-6,IW_,band.width-4):im.alpha_composite(band.crop((0,0,band.width,bh)),(x,by))
    d=ImageDraw.Draw(im);gx=IW_//2
    d.rectangle((gx-17,by-2,gx+17,IH_),fill=(60,36,20,255))
    d.rectangle((gx-14,by,gx+14,IH_),fill=(236,224,170,255));d.rectangle((gx-14,by,gx+14,by+3),fill=(190,170,110,255))
    d.rectangle((gx-11,IH_-9,gx+11,IH_-3),fill=(120,70,60,255),outline=(70,40,30,255))   # tapete
    d.line((gx-17,by-3,gx+17,by-3),fill=(130,92,52,255))
    props=[]
    def P(n,x,y,col=None,auto=False):
        sp=SP[n];props.append((sp,x,y,(autocol(sp) if auto else (col or []))))
    CT=[(-40,0,8),(-20,0,8),(0,0,8),(20,0,8),(40,0,8)];cx=IW_//2
    if kind=='mer':
        P('shelf',34,66,auto=True);P('rack',cx,60);P('banner1',IW_-34,56);P('plants',44,IH_-34,auto=True);P('counter',cx,128,CT);P('barrel',IW_-30,128,auto=True);NPC=(cx,112)
    elif kind=='fer':
        P('furnace',52,80,auto=True);P('oven',IW_-46,80,auto=True);P('rack',cx,60);P('counter',cx,132,CT);P('barrel',30,150,auto=True);P('plants',IW_-44,IH_-34,auto=True);NPC=(cx,116)
    elif kind=='alq':
        P('shelf',32,66,auto=True);P('shelf',cx,66,auto=True);P('banner2',IW_-34,56);P('potions',IW_-30,110);P('counter',cx,132,CT);P('plants',44,IH_-34,auto=True);NPC=(cx,116)
    elif kind=='mes':
        P('banner1',44,56);P('banner2',IW_-44,56);P('shelf',cx,66,auto=True);P('table',cx,140,[(-18,0,9),(0,0,9),(18,0,9)]);P('plants',44,IH_-34,auto=True);P('plants',IW_-44,IH_-34,auto=True);NPC=(cx,100)
    elif kind=='cof':
        P('shelf',36,66,auto=True);P('rack',cx+16,60);P('barrel',IW_-34,76,auto=True);P('counter',cx,132,CT);P('barrel',30,150,auto=True);NPC=(cx,116)
    else:
        P('banner1',44,56);P('banner2',IW_-44,56);P('shelf',cx,66,auto=True);P('counter',cx,132,CT);P('barrel',30,146,auto=True);P('barrel',IW_-30,146,auto=True);NPC=(cx,116)
    return im,props,NPC,None
