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
IW_,IH_=288,384
def interior(kind,seed=1):
    r=random.Random(seed)
    fi={'mer':0,'fer':1,'alq':0,'mes':2,'cof':1,'lei':3}[kind];wi={'mer':0,'fer':1,'alq':0,'mes':2,'cof':1,'lei':3}[kind]
    fl=FLOORS[fi].crop((16,16,64,64));im=Image.new('RGBA',(IW_,IH_),(0,0,0,255))
    for y in range(0,IH_,48):
        for x in range(0,IW_,48):im.alpha_composite(fl,(x,y))
    wl=WALLS[wi]
    for x in range(-6,IW_,wl.width-8):im.alpha_composite(wl,(x,-12))
    props=[]   # (spr, x, y_base, colliders)
    def P(n,x,y,col=None):props.append((SP[n],x,y,col or []))
    NPC=None
    if kind=='mer':
        P('shelf',50,66);P('rack',144,60);P('banner1',226,56);P('plants',40,350);P('crate',250,352)
        P('counter',144,168,[(-40,0,8),(-20,0,8),(0,0,8),(20,0,8),(40,0,8)]);P('barrel',30,160,[(0,0,8)]);P('barrel',258,160,[(0,0,8)]);NPC=(144,150)
    elif kind=='fer':
        P('furnace',70,86,[(0,0,14)]);P('oven',222,86,[(0,0,14)]);P('rack',146,60)
        P('counter',144,176,[(-40,0,8),(-20,0,8),(0,0,8),(20,0,8),(40,0,8)]);P('crate',40,160,[(0,0,8)]);P('barrel',258,170,[(0,0,8)]);P('plants',250,352);NPC=(144,156)
    elif kind=='alq':
        P('shelf',46,66);P('shelf',130,66);P('banner2',214,56);P('potions',250,110)
        P('counter',144,170,[(-40,0,8),(-20,0,8),(0,0,8),(20,0,8),(40,0,8)]);P('plants',36,350);P('plants',250,350);P('barrel',262,170,[(0,0,8)]);NPC=(144,152)
    elif kind=='mes':
        P('banner1',70,56);P('banner2',218,56);P('shelf',144,66);P('table',144,210,[(-20,0,10),(0,0,10),(20,0,10)]);P('plants',36,350);P('plants',250,350);NPC=(144,170)
    elif kind=='cof':
        P('shelf',52,66);P('rack',150,60);P('chest',240,76,[(0,0,8)])
        P('counter',144,170,[(-40,0,8),(-20,0,8),(0,0,8),(20,0,8),(40,0,8)]);P('chest',36,166,[(0,0,8)]);P('chest',258,166,[(0,0,8)]);NPC=(144,152)
    else:
        P('banner1',60,56);P('banner2',228,56);P('shelf',144,66)
        P('counter',144,170,[(-40,0,8),(-20,0,8),(0,0,8),(20,0,8),(40,0,8)]);P('crate',40,166,[(0,0,8)]);P('crate',256,166,[(0,0,8)]);NPC=(144,152)
    # porta de saída (parte de baixo)
    door=SP['door']
    return im,props,NPC,door
