"""Props pixel-art de goblins (desenhados em código, escala do pack): tenda de couro, totem, estaca com crânio, ossos, paliçada, caldeirão, cogumelos."""
from PIL import Image,ImageDraw
import random
def _o(): return (38,22,14,255)
def tent(seed=0):
    r=random.Random(seed);W,H=46,38;im=Image.new('RGBA',(W,H),(0,0,0,0));d=ImageDraw.Draw(im)
    base=(142,104,64,255);dark=(104,74,46,255);lite=(176,136,86,255)
    d.polygon([(1,H-3),(23,3),(45,H-3)],fill=base);d.polygon([(23,3),(45,H-3),(28,H-3)],fill=dark);d.polygon([(23,3),(1,H-3),(10,H-3)],fill=lite)
    for k in range(1,5):
        y=3+k*6;d.line([(23-k*5,y+2),(23+k*5,y+2)],fill=(92,64,40,255))
    pc=[(150,62,44,255),(86,110,58,255),(190,170,120,255)]
    for (x,y,w,h) in [(10,24,6,5),(30,22,5,6),(20,12,4,4)]:
        c=pc[r.randrange(3)];d.rectangle([x,y,x+w,y+h],fill=c,outline=(60,36,22,255))
    d.polygon([(18,H-3),(23,17),(29,H-3)],fill=(26,14,10,255));d.line([(23,17),(23,H-3)],fill=(14,8,6,255))
    d.polygon([(1,H-3),(23,3),(45,H-3)],outline=_o())
    d.line([(21,0),(25,7)],fill=(80,54,30,255),width=2);d.line([(26,0),(21,7)],fill=(80,54,30,255),width=2)
    d.rectangle([20,9,24,12],fill=(232,226,206,255));d.point([(21,10),(23,10)],fill=(20,10,8,255))
    d.line([(1,H-3),(45,H-3)],fill=_o());return im
def totem(seed=0):
    W,H=20,64;im=Image.new('RGBA',(W,H),(0,0,0,0));d=ImageDraw.Draw(im)
    wood=(112,76,44,255);wd=(78,52,30,255);wl=(150,106,62,255)
    d.rectangle([6,6,13,H-3],fill=wood,outline=_o());d.rectangle([11,7,12,H-4],fill=wd);d.line([(7,8),(7,H-5)],fill=wl)
    # cabeça de goblin (verde)
    d.rectangle([4,8,15,20],fill=(70,150,60,255),outline=_o());d.polygon([(4,12),(0,9),(4,16)],fill=(70,150,60,255),outline=_o());d.polygon([(15,12),(19,9),(15,16)],fill=(70,150,60,255),outline=_o())
    d.rectangle([6,12,8,13],fill=(250,214,60,255));d.rectangle([11,12,13,13],fill=(250,214,60,255));d.rectangle([7,17,12,18],fill=(150,30,30,255))
    # crânio
    d.rectangle([4,24,15,34],fill=(226,218,196,255),outline=_o());d.rectangle([6,27,8,30],fill=(24,14,10,255));d.rectangle([11,27,13,30],fill=(24,14,10,255));d.rectangle([7,32,12,34],fill=(160,150,128,255))
    for x in (8,10,12):d.line([(x,32),(x,34)],fill=(40,30,24,255))
    # presas / pintura de guerra
    d.rectangle([4,38,15,48],fill=(168,120,70,255),outline=_o());d.line([(5,41),(14,41)],fill=(170,36,30,255),width=2);d.line([(5,45),(14,45)],fill=(240,230,200,255))
    d.polygon([(6,48),(8,48),(7,53)],fill=(240,236,220,255));d.polygon([(11,48),(13,48),(12,53)],fill=(240,236,220,255))
    # penas
    for i,c in enumerate([(200,40,36,255),(236,196,60,255),(200,40,36,255)]):d.line([(7+i*3,6),(5+i*4,0)],fill=c,width=2)
    d.rectangle([3,H-5,16,H-3],fill=(104,100,94,255),outline=_o());return im
def skull_stake(seed=0):
    r=random.Random(seed);W,H=12,28;im=Image.new('RGBA',(W,H),(0,0,0,0));d=ImageDraw.Draw(im)
    d.rectangle([5,10,6,H-2],fill=(96,66,38,255),outline=_o())
    d.rectangle([1,2,10,7],fill=(228,220,198,255),outline=_o());d.rectangle([2,1,9,1],fill=(228,220,198,255));d.line([(2,0),(9,0)],fill=_o());d.rectangle([3,8,8,10],fill=(214,206,184,255),outline=_o())
    d.rectangle([2,4,4,6],fill=(24,14,10,255));d.rectangle([7,4,9,6],fill=(24,14,10,255));d.point([(5,7),(6,7)],fill=(60,40,30,255));d.line([(4,9),(7,9)],fill=(60,50,40,255))
    d.point([(1,2),(10,2),(1,7),(10,7)],fill=(0,0,0,0))
    if r.random()<.5:d.line([(1,9),(10,9)],fill=_o())
    return im
def bones(seed=0):
    r=random.Random(seed);W,H=28,14;im=Image.new('RGBA',(W,H),(0,0,0,0));d=ImageDraw.Draw(im);B=(226,218,196,255)
    for _ in range(4):
        x=r.randrange(2,18);y=r.randrange(3,11);a=r.randrange(5,10)
        d.line([(x,y),(x+a,y+r.randrange(-2,3))],fill=B,width=2);d.point([(x,y-1),(x,y+1),(x+a,y)],fill=B)
    sx=r.randrange(14,20);d.rectangle([sx,3,sx+7,9],fill=B,outline=_o());d.rectangle([sx+1,5,sx+2,6],fill=(24,14,10,255));d.rectangle([sx+5,5,sx+6,6],fill=(24,14,10,255))
    return im
def palisade(seed=0):
    r=random.Random(seed);W,H=33,28;im=Image.new('RGBA',(W,H),(0,0,0,0));d=ImageDraw.Draw(im)
    for i in range(3):
        x=i*11;h=H-r.randrange(0,4);t=H-h
        d.rectangle([x+1,t+5,x+9,H-2],fill=(100,70,40,255),outline=_o());d.polygon([(x+1,t+5),(x+5,t),(x+9,t+5)],fill=(100,70,40,255),outline=_o())
        d.line([(x+3,t+6),(x+3,H-3)],fill=(140,100,60,255));d.line([(x+8,t+6),(x+8,H-3)],fill=(70,48,28,255))
    d.line([(0,H-9),(W-1,H-9)],fill=(196,170,110,255));d.line([(0,H-8),(W-1,H-8)],fill=(60,40,24,255));return im
def cauldron(seed=0):
    W,H=24,22;im=Image.new('RGBA',(W,H),(0,0,0,0));d=ImageDraw.Draw(im)
    for x in (4,18):d.line([(x,14),(x-1,H-2)],fill=(40,36,34,255),width=2)
    d.ellipse([1,6,22,20],fill=(46,44,50,255),outline=_o());d.ellipse([2,8,10,15],fill=(74,72,80,255))
    d.ellipse([2,3,21,11],fill=(86,84,92,255),outline=_o());d.ellipse([4,5,19,10],fill=(116,214,64,255));d.ellipse([7,6,12,8],fill=(180,244,120,255))
    d.point([(14,6),(16,8),(9,9)],fill=(230,255,190,255));return im
def mushrooms(seed=0,purple=False):
    r=random.Random(seed);W,H=22,16;im=Image.new('RGBA',(W,H),(0,0,0,0));d=ImageDraw.Draw(im)
    cap=(130,70,170,255) if purple else (190,52,44,255);dot=(240,230,210,255)
    for (x,w,h) in [(4,9,8),(13,7,6)]:
        d.rectangle([x+w//2-1,H-h//2-3,x+w//2+1,H-2],fill=(226,214,184,255),outline=_o())
        d.ellipse([x-1,H-h-3,x+w+1,H-h//2-1],fill=cap,outline=_o());d.point([(x+2,H-h-1),(x+w-2,H-h+0),(x+w//2,H-h-2)],fill=dot)
    return im
