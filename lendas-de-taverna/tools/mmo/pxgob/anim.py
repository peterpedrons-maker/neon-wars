"""Animações do goblin pixel art (frontal): parado, andar, ataque, dano. Gera GIFs, folhas de sprite e prévia.
Uso: python3 anim.py <pasta_saida>"""
import sys,math,os
from gob import *
from PIL import Image,ImageDraw
OUTD=sys.argv[1] if len(sys.argv)>1 else '/tmp/pxgob';os.makedirs(OUTD,exist_ok=True)
def idle():
    F=[]
    for k in range(6):
        b=[0,0,1,1,1,0][k];s=math.sin(2*math.pi*k/6)
        F.append(dict(bob=b,head=(0,[0,0,0,1,1,0][k]),earL=3*s,earR=-3*s,armL=(14+(b)*1,14),armR=(24+b,12),club=(12+(1 if k in(2,3,4) else 0),15,False),eyes='shut' if k==5 else 'open'))
    return F,[220,220,220,220,220,140]
def walk():
    F=[]
    for k in range(8):
        p=2*math.pi*k/8;s=math.sin(p);c=math.cos(p)
        lL=max(0,s)*3.2;lR=max(0,-s)*3.2
        F.append(dict(bob=0 if abs(s)>.5 else 1,legs=(lL,lR,.3),earL=5*math.sin(2*p-.6),earR=-5*math.sin(2*p-.6),head=(0,0),
          armL=(14+8*s,14+6*s),armR=(24-6*s,12+4*s),club=(12-7*s,15,False)))
    return F,[90]*8
def attack():
    F=[dict(),
     dict(bob=1,legs=(0,0,.4),lean=-1,armR=(95,150),armL=(30,40),club=(8,15,False),earL=-4,earR=4),
     dict(bob=1,legs=(0,0,.7),lean=-1,armR=(130,172),armL=(45,60),club=(20,15,False),earL=-8,earR=8,mouth=1,head=(-1,0)),
     dict(bob=1,legs=(0,0,.7),lean=-1,armR=(160,185),armL=(55,70),club=(-12,16,False),earL=-10,earR=10,mouth=1,head=(-1,-1)),
     dict(bob=0,legs=(0,0,.5),armR=(110,120),armL=(40,30),club=(-85,15,True),earL=-4,earR=4,mouth=1,head=(0,0)),
     dict(bob=2,legs=(0,0,1.2),lean=1,armR=(55,45),armL=(25,20),club=(-150,11,True),earL=12,earR=-12,mouth=1,head=(0,1),eyes='shut',
          fxrel=[(-5,3,PAL['W'][0]),(-6,0,PAL['Y'][0]),(-4,5,PAL['Y'][0]),(-7,4,PAL['W'][0]),(5,3,PAL['W'][0]),(6,1,PAL['Y'][0]),(0,5,PAL['Y'][0])]),
     dict(bob=2,legs=(0,0,1.2),lean=1,armR=(55,45),armL=(25,20),club=(-150,11,True),earL=6,earR=-6,mouth=1,head=(0,1),
          fxrel=[(-6,3,PAL['Y'][1]),(6,3,PAL['Y'][1]),(0,-5,PAL['W'][1])]),
     dict(bob=1,legs=(0,0,.6),armR=(60,60),armL=(20,20),club=(-90,13,True),earL=2,earR=-2),
     dict(bob=0,armR=(35,30),club=(-20,14,False))]
    return F,[110,90,90,70,50,60,150,110,110]
def hurt():
    F=[dict(bob=1,lean=2,head=(1,-1),eyes='hurt',mouth=2,earL=-14,earR=14,armL=(70,80),armR=(80,70),club=(40,15,False),legs=(0,0,.8)),
       dict(bob=2,lean=2,head=(2,0),eyes='hurt',mouth=2,earL=-8,earR=8,armL=(55,60),armR=(60,60),club=(30,15,False),legs=(0,0,1.0)),
       dict(bob=1,lean=0,head=(0,0),eyes='open',mouth=1,earL=6,earR=-6,armL=(30,30),armR=(34,30),club=(18,15,False),legs=(0,0,.5)),
       dict()]
    return F,[110,110,110,120]
def comp(g,scale=8):
    sp=g.render(scale)
    bg=Image.new('RGBA',sp.size,(44,48,60,255));d=ImageDraw.Draw(bg)
    w,h=sp.size;d.ellipse((w*.2,h*.80,w*.8,h*.90),fill=(28,30,40,255))
    bg.alpha_composite(sp);return bg
res={}
for name,fn in(('idle',idle),('walk',walk),('attack',attack),('hurt',hurt)):
    poses,dur=fn();gs=[goblin(p) for p in poses];res[name]=gs
    ims=[comp(g).convert('RGB').quantize(32,dither=Image.Dither.NONE) for g in gs]
    ims[0].save(f'{OUTD}/gob_{name}.gif',save_all=True,append_images=ims[1:],duration=dur,loop=0,disposal=2)
    sheet=Image.new('RGBA',(W*len(gs),H),(0,0,0,0))
    for i,g in enumerate(gs):sheet.alpha_composite(g.render(1),(i*W,0))
    sheet.save(f'{OUTD}/gob_{name}_sheet.png')
# prévia: todos os quadros lado a lado
rows=[]
for name in('idle','walk','attack','hurt'):
    gs=res[name];row=Image.new('RGB',(W*4*len(gs),H*4),(44,48,60))
    for i,g in enumerate(gs):row.paste(g.render(4,(44,48,60,255)).convert('RGB'),(i*W*4,0))
    rows.append(row)
mw=max(r.width for r in rows);P=Image.new('RGB',(mw,sum(r.height for r in rows)),(44,48,60));y=0
for r in rows:P.paste(r,(0,y));y+=r.height
P.save(f'{OUTD}/preview.png');print('ok',P.size)
