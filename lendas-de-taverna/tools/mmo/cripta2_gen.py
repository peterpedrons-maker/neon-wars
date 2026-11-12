#!/usr/bin/env python3
"""Gera a Cripta do Rei Esquecido (pixel art por código): chão+paredes, atlas de props, máscara de colisão e JSON da zona.
Uso: python3 cripta2_gen.py  -> escreve em ../../mmo/assets/ (zone_cripta2*.png/json, atlas_cripta2.*, portal/d5.jpg)"""
import random, math, json, os, numpy as np
from PIL import Image, ImageDraw
random.seed(11)
HERE=os.path.dirname(os.path.abspath(__file__)); AS=os.path.normpath(HERE+'/../../mmo/assets')
SRC=AS+'/cripta/d2/'
TW,TH,CAP=48,45,9
GW,GH=68,42; OY=9; SHD=12
W,H=GW*TW,GH*TH+OY
K=dict(dk=(8,14,28),w0=(44,66,76),w1=(70,98,104),w1b=(76,104,110),w2=(98,130,132),w3=(128,158,154),
 f0=(16,46,70),f1=(26,68,94),f1b=(22,60,86),f1c=(30,76,100),f2=(40,90,114),f3=(56,108,126),
 r0=(70,20,28),r1=(104,30,38),r2=(150,50,48),gold=(190,150,70),
 wood=(80,52,40),wood2=(54,34,30),m0=(36,68,50),m1=(54,96,62),m2=(78,126,74),bone=(204,198,176),bone2=(150,146,134),
 cy=(90,210,230),iron=(60,66,78),iron2=(96,104,116))
BAY=np.array([[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]])
def hh(x,y,s=0): return ((x*73856093)^(y*19349663)^(s*83492791))%1000
# ---------- mapa: caminho único, sem atalhos
ROOMS=dict(ent=(1,7,8,9),A=(9,3,23,13),B=(28,3,44,14),C=(49,3,63,14),D=(48,22,63,34),E=(31,22,43,34),F=(3,22,26,38))
CORR=[(24,7,27,9),(45,7,48,9),(54,15,56,21),(44,27,47,29),(27,27,30,29)]
g=[['#']*GW for _ in range(GH)]
for (x0,y0,x1,y1) in list(ROOMS.values())+CORR:
    for y in range(y0,y1+1):
        for x in range(x0,x1+1): g[y][x]='.'
fl=lambda x,y:0<=x<GW and 0<=y<GH and g[y][x]=='.'
near=lambda x,y:any(fl(x+i,y+j) for i in(-1,0,1) for j in(-1,0,1))
# plataforma do Rei (sala F): mundo x[192,512], y[Yp0,Yp1]; escada x[304,400]
YP0=OY+22*TH; YP1=OY+27*TH; PX0,PX1=336,1104; SX0,SX1=600,840; ELEV=24; ST_H=36
cv=np.zeros((H,W,3),np.uint8); cv[:]=K['dk']
def floorpix(gx,gy):
    sr=gy//15; xo=(sr%2)*8; sc=(gx+xo)//16
    base=[K['f1'],K['f1b'],K['f1c']][hh(sc,sr)%3]
    if gy%15==0 or (gx+xo)%16==0: return K['f0']
    if gy%15==1 or (gx+xo)%16==1: return K['f2']
    r=hh(gx,gy,1)
    return K['f0'] if r<60 else K['f2'] if r<120 else base
for cy_ in range(GH):
    for cx_ in range(GW):
        if not fl(cx_,cy_): continue
        for y in range(TH):
            for x in range(TW):
                gx,gy=cx_*TW+x,cy_*TH+y
                cv[OY+gy,gx]=floorpix(gx,gy)
        for y in range(TH):
            for x in range(TW):
                d=0
                if not fl(cx_,cy_-1) and y<12 and BAY[y%4][x%4]<(12-y)*2: d=1
                if not fl(cx_-1,cy_) and x<7 and BAY[y%4][x%4]<(7-x)*3: d=1
                if not fl(cx_+1,cy_) and x>=41 and BAY[y%4][x%4]<(x-40)*3: d=1
                if d: cv[OY+cy_*TH+y,cx_*TW+x]=(cv[OY+cy_*TH+y,cx_*TW+x]*0.7).astype(np.uint8)
im=Image.fromarray(cv); d=ImageDraw.Draw(im); px=im.load()
def P(x,y,c):
    x=int(x);y=int(y)
    if 0<=x<W and 0<=y<H: px[x,y]=K[c] if isinstance(c,str) else c
def cell(cx,cy,ox=16,oy=15): return cx*TW+ox, OY+cy*TH+oy
# ---------- decalques de chão
def puddle(x,y,w=12):
    for yy in range(-2,3):
        ww=int(w/2*math.sqrt(max(0,1-(yy/2.6)**2)))
        for xx in range(-ww,ww+1): P(x+xx,y+yy,'f3' if (xx+yy)%5 else (110,170,190))
    P(x-2,y-1,(170,220,235)); P(x+1,y,(170,220,235))
def bones(x,y):
    for dx,dy in((0,0),(1,0),(2,0),(3,1),(4,1),(-1,1),(5,0)): P(x+dx,y+dy,'bone')
    for dx,dy in((1,2),(2,2),(3,3),(4,3)): P(x+dx,y+dy,'bone2')
def skull(x,y):
    for yy in range(4):
        for xx in range(5): P(x+xx,y+yy,'bone' if not(yy==3 and xx in(0,4)) else 'bone2')
    P(x+1,y+1,'dk'); P(x+3,y+1,'dk'); P(x+2,y+3,'dk')
def rubble(x,y):
    for _ in range(9): P(x+random.randint(-4,4),y+random.randint(-2,2),random.choice(['w0','w1','w2']))
def moss(x,y,n=14):
    for _ in range(n): P(x+random.randint(-4,4),y+random.randint(-2,2),random.choice(['m0','m1','m1','m2']))
def crack(x,y,n=7):
    for _ in range(n): P(x,y,'dk'); x+=random.choice([-1,0,1]); y+=1
def blood(x,y):
    for _ in range(26): P(x+random.randint(-5,5),y+random.randint(-2,2),random.choice([(80,18,24),(104,28,32),(60,12,20)]))
def web(x,y,sx,sy):
    for i in range(1,16):
        P(x+sx*i,y,(150,162,168)); P(x,y+sy*i,(150,162,168))
        if i%2: P(x+sx*i,y+sy*(i//2),(130,142,150)); P(x+sx*(i//2),y+sy*i,(130,142,150))
def plate(x,y):
    d.rectangle([x-14,y-9,x+14,y+9],fill=K['w0'],outline=K['dk']); d.rectangle([x-11,y-6,x+11,y+6],fill=K['w1'],outline=K['w0'])
    for dx in(-6,0,6): P(x+dx,y,'dk'); P(x+dx,y-3,'dk'); P(x+dx,y+3,'dk')
def rune(x,y,r=40):
    for a in range(0,360,2):
        t=math.radians(a); P(x+r*math.cos(t),y+r*0.62*math.sin(t),'cy'); P(x+(r-5)*math.cos(t),y+(r-5)*0.62*math.sin(t),(50,140,170))
    pts=[(x+(r-5)*math.cos(math.radians(a)),y+(r-5)*0.62*math.sin(math.radians(a))) for a in range(-90,270,72)]
    for i in range(5):
        a,b=pts[i],pts[(i+2)%5]
        for s in range(0,21): P(a[0]+(b[0]-a[0])*s/20,a[1]+(b[1]-a[1])*s/20,(70,170,200))
    for a in range(0,360,30):
        t=math.radians(a); P(x+(r+3)*math.cos(t),y+(r+3)*0.62*math.sin(t),'cy')
def carpet_h(x0,x1,yc,hgt=28):
    for x in range(x0,x1):
        for y in range(yc-hgt//2,yc+hgt//2):
            c='r1'
            if y in(yc-hgt//2,yc+hgt//2-1): c='gold'
            elif y in(yc-hgt//2+1,yc+hgt//2-2): c='r0'
            elif x%8<2 and abs(y-yc)<hgt//2-3: c='r2'
            P(x,y,c)
def carpet_v(xc,y0,y1,wid=28):
    for y in range(y0,y1):
        for x in range(xc-wid//2,xc+wid//2):
            c='r1'
            if x in(xc-wid//2,xc+wid//2-1): c='gold'
            elif x in(xc-wid//2+1,xc+wid//2-2): c='r0'
            elif y%8<2 and abs(x-xc)<wid//2-3: c='r2'
            P(x,y,c)
def rug(x0,y0,x1,y1):
    d.rectangle([x0,y0,x1,y1],fill=K['r1'],outline=K['gold']); d.rectangle([x0+2,y0+2,x1-2,y1-2],outline=K['r0'])
    cx,cy=(x0+x1)//2,(y0+y1)//2
    for i in range(0,14): P(cx-i,cy,'gold'); P(cx+i,cy,'gold')
    d.polygon([(cx,cy-10),(cx+8,cy),(cx,cy+10),(cx-8,cy)],outline=K['gold'],fill=K['r2']); P(cx,cy,'gold')
# ---------- tapetes e marcas fixas
x,y=cell(12,5,0,0); rug(x,y+8,x+9*TW,y+7*TH-8)                              # átrio
rune(*cell(36,8,0,0))                                                       # salão dos guardiões
for cx_ in(52,56,60):
    for cy_ in(6,10): plate(*cell(cx_,cy_,24,22))                           # salão das armadilhas
rune(2*TW,OY+8*TH+22,16)                                                    # selo na entrada
YC=OY+28*TH+22
carpet_h(720,27*TW+4,YC,28)                                                 # corredor -> câmara do Rei
carpet_v(720,YP1+ST_H+2,YC+14,28)
# ---------- decalques automáticos por sala (sem tapete)
AUTO={'A':12,'B':16,'C':14,'D':18,'E':12,'F':22,'ent':4}
fns=[puddle,bones,rubble,moss,crack,blood,skull,moss,rubble,puddle]
for key,n in AUTO.items():
    x0,y0,x1,y1=ROOMS[key]
    for _ in range(n):
        cx_,cy_=random.randint(x0,x1),random.randint(y0,y1)
        if key=='F' and (PX0<=cx_*TW<PX1 and OY+cy_*TH<YP1+60): continue
        f=random.choice(fns); f(*cell(cx_,cy_,random.randint(8,40),random.randint(10,34)))
for key_,(x0_,y0_,x1_,y1_) in ROOMS.items():
    for (cx,cy_,sx,sy) in((x0_,y0_,1,1),(x1_,y0_,-1,1),(x0_,y1_,1,-1),(x1_,y1_,-1,-1)):
        x,y=cell(cx,cy_,0 if sx>0 else TW-1,0 if sy>0 else TH-1); web(x,y,sx,sy)
# ---------- plataforma + escada da câmara do Rei
def stone_slab(x,y,w0=16,h0=15):
    return K['w1b'] if hh(x//w0,y//h0)%2 else K['w1']
for yy in range(YP0-ELEV,YP1-ELEV):
    for xx in range(PX0,PX1):
        c=stone_slab(xx,yy)
        if yy%15==0 or xx%16==0: c=K['w0']
        elif yy%15==1: c=K['w2']
        P(xx,yy,c)
for xx in range(PX0,PX1): P(xx,YP0-ELEV,'dk')
for yy in range(YP0-ELEV,YP1-ELEV): P(PX0,yy,'w3'); P(PX0-1,yy,'dk'); P(PX1,yy,'dk'); P(PX1-1,yy,'w0')
# face frontal (riser) com tijolos
for yy in range(YP1-ELEV,YP1):
    for xx in range(PX0,PX1+1):
        if SX0<=xx<SX1: continue
        r=hh(xx,yy,4); c=K['w1']
        if (yy-(YP1-ELEV))%8==7 or (xx%10==9): c=K['w0']
        elif r<80: c=K['w0']
        P(xx,yy,c)
    P(PX0-1,yy,'dk')
for xx in range(PX0-1,PX1+1):
    if not(SX0<=xx<SX1): P(xx,YP1-1,'dk')
# degraus: topo(554) riser tread riser tread ...
y=YP1-ELEV
seq=[('ri',6),('tr',12),('ri',6),('tr',12),('ri',6),('tr',12),('ri',6)]
for kind,hgt in seq:
    for yy in range(y,y+hgt):
        for xx in range(SX0,SX1):
            c=K['w3'] if kind=='tr' and yy==y else K['w2'] if kind=='tr' else K['w0']
            if kind=='tr' and (hash((xx,yy))%9==0): c=K['w1']
            P(xx,yy,c)
    y+=hgt
for yy in range(YP1-ELEV,y): P(SX0-1,yy,'dk'); P(SX1,yy,'dk'); P(SX0,yy,'w3'); P(SX1-1,yy,'w0')
for xx in range(SX0-1,SX1+1): P(xx,y-1,'dk')
carpet_v(720,YP1-ELEV,y,24)
# ---------- sprites
def spr(name,w):
    s=Image.open(SRC+name).convert('RGBA'); h=max(1,round(s.height*w/s.width))
    s=s.resize((w,h),Image.LANCZOS); a=s.getchannel('A').point(lambda v:255 if v>110 else 0)
    q=s.convert('RGB').quantize(18,dither=0).convert('RGB').convert('RGBA'); q.putalpha(a); return q
def pillar():
    w,h=24,70; s=Image.new('RGBA',(w,h),(0,0,0,0)); dd=ImageDraw.Draw(s)
    dd.rectangle([1,60,w-2,h-1],fill=K['w2']+(255,),outline=K['dk']+(255,)); dd.rectangle([4,8,w-5,60],fill=K['w1']+(255,))
    dd.rectangle([4,8,8,60],fill=K['w3']+(255,)); dd.rectangle([w-9,8,w-5,60],fill=K['w0']+(255,))
    for y in range(14,60,10): dd.line([4,y,w-5,y],fill=K['w0']+(255,))
    dd.line([3,8,3,60],fill=K['dk']+(255,)); dd.line([w-4,8,w-4,60],fill=K['dk']+(255,))
    dd.rectangle([0,0,w-1,9],fill=K['w2']+(255,),outline=K['dk']+(255,)); dd.line([1,1,w-2,1],fill=K['w3']+(255,)); return s
def brazier():
    s=Image.new('RGBA',(22,24),(0,0,0,0)); dd=ImageDraw.Draw(s)
    dd.rectangle([10,13,11,23],fill=K['iron']+(255,)); dd.rectangle([5,21,16,23],fill=K['iron']+(255,))
    dd.polygon([(0,8),(21,8),(16,18),(5,18)],fill=K['iron']+(255,),outline=K['dk']+(255,)); dd.line([1,8,20,8],fill=K['iron2']+(255,)); return s
def banner():
    s=Image.new('RGBA',(15,32),(0,0,0,0)); dd=ImageDraw.Draw(s)
    dd.rectangle([0,0,14,2],fill=K['wood']+(255,))
    dd.polygon([(1,3),(13,3),(13,31),(8,25),(6,25),(1,31)],fill=K['r1']+(255,),outline=K['r0']+(255,))
    dd.line([3,6,11,6],fill=K['gold']+(255,)); dd.polygon([(7,11),(10,16),(7,21),(4,16)],fill=K['gold']+(255,)); return s
def torchsp():
    s=Image.new('RGBA',(10,18),(0,0,0,0)); dd=ImageDraw.Draw(s)
    dd.rectangle([3,4,6,17],fill=K['wood']+(255,)); dd.rectangle([1,2,8,4],fill=K['iron']+(255,)); return s
def skull_niche(x,y):
    d.rectangle([x,y,x+13,y+16],fill=K['dk'],outline=K['w0']); skull(x+4,y+6); d.line([x-1,y-1,x+14,y-1],fill=K['w3'])
def paste(s,x,y): im.paste(s,(int(x),int(y)),s)
# ---------- paredes
def wall_px(gx,gy,yl):
    if yl<0:
        r=yl+CAP
        if r<5: return K['w3'] if hh(gx,gy,2)>120 else K['w2']
        return K['w2'] if r==5 else K['dk']
    row=gy//6; inrow=gy%6; off=(row%2)*5
    if yl==0: return K['dk']
    if inrow==5 or (gx+off)%10==9: return K['w0']
    if inrow==0: return K['w2']
    bid=hh((gx+off)//10,row,3); r=hh(gx,gy,4)
    if r<55: return K['w0']
    if r<110: return K['w2']
    return K['w1b'] if bid%3==0 else K['w1']
def draw_wall(cx_,cy_):
    cap=not(cy_>0 and g[cy_-1][cx_]=='#' and near(cx_,cy_-1)); y0=-CAP if cap else 0
    fs=fl(cx_,cy_+1); fW=fl(cx_-1,cy_); fE=fl(cx_+1,cy_)
    for yl in range(y0,TH):
        for x in range(TW):
            gx,gy=cx_*TW+x,cy_*TH+yl; c=wall_px(gx,gy,yl)
            if yl>=0:
                if fW and x==0: c=K['dk']
                if fE and x==TW-1: c=K['dk']
                if fW and x==1 and c!=K['dk']: c=K['w2']
                if fE and x==TW-2 and c!=K['dk']: c=K['w0']
                if fs and yl>=TH-SHD and BAY[gy%4][gx%4]<(yl-(TH-SHD))*2: c=K['w0'] if yl<TH-3 else K['dk']
            P(gx,OY+gy,c)
walls=[(x,y) for y in range(GH) for x in range(GW) if g[y][x]=='#' and near(x,y)]
backs=[c for c in walls if not fl(c[0],c[1]-1)]; fronts=[c for c in walls if fl(c[0],c[1]-1)]
for c in backs: draw_wall(*c)
for c in fronts: draw_wall(*c)
def wxy(cx,cy,ox=24,oy=0): return cx*TW+ox, OY+cy*TH+oy
decor=[]
for key_,(x0_,y0_,x1_,y1_) in ROOMS.items():
    n_=0
    for cx in range(x0_+2,x1_-1,3):
        kind=['torch','banner','torch','niche'][n_%4] if key_!='ent' else 'torch'
        if key_ in('ent',) and n_%2: kind='niche'
        decor.append((kind,cx,y0_-1)); n_+=1
for (x0_,y0_,x1_,y1_) in CORR:
    if x1_-x0_>=y1_-y0_: decor.append(('torch',(x0_+x1_)//2,y0_-1))
fx=[]
for kind,cx,cy in decor:
    if g[cy][cx]!='#': continue
    x,y=wxy(cx,cy)
    if kind=='banner': paste(banner(),x-7,y+6)
    elif kind=='torch': paste(torchsp(),x-5,y+12); fx.append(dict(k='torch',x=x,y=y+14))
    elif kind=='niche': skull_niche(x-7,y+12)
for cx,cy in backs:
    if fl(cx,cy+1) and hh(cx,cy,7)<380:
        x,y=wxy(cx,cy,hh(cx,cy,8)%36+6,TH-3); moss(x,y,12)
# ---------- props (atlas) com colisão
props=[]; atlas_items={}
def prop(name,w,cx,cy,ox=16,oy=26,col=None):
    s=spr(name,w); key=f'{name[:-4]}_{w}'; atlas_items.setdefault(key,s)
    x,y=cx*TW+ox,OY+cy*TH+oy
    props.append(dict(t='p',id=key,x=x,y=y,col=col if col is not None else [[0,-2,max(4,w//3)]]))
def pil(cx,cy):
    atlas_items.setdefault('pilar',pillar()); props.append(dict(t='p',id='pilar',x=cx*TW+16,y=OY+cy*TH+26,col=[[0,-2,8]]))
def onplat(x,y): return PX0<=x<=PX1 and YP0<=y<=YP1
def braz(x,y):
    atlas_items.setdefault('braseiro',brazier()); props.append(dict(t='p',id='braseiro',x=x,y=y,col=[[0,-2,9]])); fx.append(dict(k='torch',x=x,y=y-20-(ELEV if onplat(x,y) else 0),r=70))
def P_(key,name,w,fx_,fy_,ox=24,oy=38,col=None): 
    x0_,y0_,x1_,y1_=ROOMS[key]; prop(name,w,int(x0_+(x1_-x0_)*fx_),int(y0_+(y1_-y0_)*fy_),ox,oy,col)
# Átrio
braz(12*TW+24,OY+4*TH+38); braz(22*TW+24,OY+4*TH+38); braz(12*TW+24,OY+12*TH+38); braz(22*TW+24,OY+12*TH+38)
prop('prop_mesa.png',40,10,4,24,36); prop('prop_potes.png',18,22,4,24,40); prop('prop_barril.png',22,10,12,24,40); prop('prop_sacos.png',26,22,12,30,40)
# Guardiões: 4 pilares + decoração
for cx,cy in((32,6),(40,6),(32,12),(40,12)): pil(cx,cy)
prop('prop_barril.png',22,29,4,24,40); prop('prop_potes.png',20,43,4,24,40); prop('prop_caixas.png',30,43,13,22,40); prop('prop_barril.png',22,29,13,24,40)
# Armadilhas
prop('prop_barril.png',22,50,4,24,40); prop('prop_caixas.png',30,62,13,22,40); prop('prop_sacos.png',26,50,13,26,40); prop('prop_potes.png',18,62,4,24,40)
# Altares: 3 altares na parede norte
for cx in(52,56,60): prop('prop_altar.png',44,cx,24,24,40,[[0,-4,16]])
prop('prop_barril.png',22,49,33,24,40); prop('prop_sacos.png',26,62,33,26,40); prop('prop_caixas.png',30,62,23,22,40); prop('prop_potes.png',18,49,23,24,40)
# Cofre sombrio
prop('prop_prateleira.png',44,35,22,24,22); prop('prop_bau.png',34,41,23,24,40); prop('prop_barril.png',22,32,33,24,40)
prop('prop_caixas.png',30,42,33,22,40); prop('prop_jaula.png',44,32,28,30,44)
# Câmara do Rei: trono, braseiros, entulho
prop('prop_altar.png',60,15,23,0,50,[[0,-4,26],[-14,-4,14],[14,-4,14]])
braz(11*TW+24,YP0+110); braz(19*TW+24,YP0+110)
prop('prop_barril.png',22,4,37,24,40); prop('prop_caixas.png',30,25,37,22,40); prop('prop_bau.png',34,4,23,24,40); prop('prop_potes.png',20,25,23,24,40)
# ---------- luz (tramada)
lights=[(f['x'],f['y'],80 if f.get('r',0)<=60 else 110,(70,36,0)) for f in fx]+[(36*TW,OY+8*TH,60,(0,30,44))]
arr=np.array(im).astype(np.int32)
yy_,xx_=np.mgrid[0:H,0:W]; bay=BAY[yy_%4,xx_%4]/16.0
tot=np.zeros((H,W)); add=np.zeros((H,W,3))
for lx,ly,R,col in lights:
    x0,x1,y0,y1=max(0,int(lx-R)),min(W,int(lx+R)+1),max(0,int(ly-R)),min(H,int(ly+R)+1)
    X,Y=xx_[y0:y1,x0:x1],yy_[y0:y1,x0:x1]; dd=np.hypot(X-lx,(Y-ly)*1.15); i=np.clip(1-dd/R,0,1)**1.4
    lvl=np.floor(i*4+bay[y0:y1,x0:x1]).clip(0,4)
    add[y0:y1,x0:x1]+=lvl[...,None]*np.array(col)/2.0; tot[y0:y1,x0:x1]+=i
arr=arr+add.astype(np.int32)
dark=np.floor(np.clip(1-tot*1.4,0,1)*2.2+bay).clip(0,3)
arr=arr*(0.9**dark)[...,None]
im=Image.fromarray(arr.clip(0,255).astype(np.uint8))
# ---------- máscara de colisão (1 = bloqueado), amostrada a cada 4px
m=np.zeros((H,W),bool)
for y in range(GH):
    for x in range(GW):
        if g[y][x]=='#':
            m[OY+y*TH:OY+(y+1)*TH, x*TW:(x+1)*TW]=True
            if fl(x,y-1): m[max(0,OY+y*TH-CAP-2):OY+y*TH, x*TW:(x+1)*TW]=True   # parede sul: beiral cobre o chão
# plataforma: borda frontal e laterais bloqueadas (exceto a escada)
m[YP1-4:YP1+5, PX0-8:SX0]=True; m[YP1-4:YP1+5, SX1:PX1+8]=True
m[YP0:YP1+5, PX0-8:PX0+1]=True; m[YP0:YP1+5, PX1-1:PX1+9]=True
m[YP1:YP1+ST_H, SX0-8:SX0]=True; m[YP1:YP1+ST_H, SX1:SX1+8]=True
mask=np.zeros(((H+3)//4,(W+3)//4),np.uint8)
for j in range(mask.shape[0]):
    for i in range(mask.shape[1]):
        mask[j,i]=255 if m[min(H-1,j*4+2),min(W-1,i*4+2)] else 0
Image.fromarray(mask).save(AS+'/zone_cripta2_walk.png')
im.save(AS+'/zone_cripta2_ground.png')
# ---------- atlas de props
names=list(atlas_items); X=Y=RH=0; AW=512; aj={}; items=[]
for n in names:
    s=atlas_items[n]
    if X+s.width+2>AW: X=0; Y+=RH+2; RH=0
    items.append((n,s,X,Y)); aj[n]=[X,Y,s.width,s.height,s.width//2,s.height]; X+=s.width+2; RH=max(RH,s.height)
for p_ in props:
    if onplat(p_['x'],p_['y']):
        e_=aj[p_['id']]; aj[p_['id']+'_e']=[e_[0],e_[1],e_[2],e_[3],e_[4],e_[5]+ELEV]; p_['id']+='_e'
at=Image.new('RGBA',(AW,Y+RH+2),(0,0,0,0))
for n,s,x,y in items: at.paste(s,(x,y))
at.save(AS+'/atlas_cripta2.png'); json.dump(aj,open(AS+'/atlas_cripta2.json','w'))
# ---------- zona
C=lambda cx,cy,ox=24,oy=30:[cx*TW+ox,OY+cy*TH+oy]
def room(id_,nm,key,mobs,**k):
    x0_,y0_,x1_,y1_=ROOMS[key]; return dict(id=id_,nm=nm,x0=x0_*TW,y0=OY+y0_*TH,x1=(x1_+1)*TW,y1=OY+(y1_+1)*TH,mobs=mobs,**k)
rooms=[
 room('A','Átrio dos Esquecidos','A',[C(14,6),C(18,6),C(14,10),C(18,10),C(16,8),C(20,8)]),
 room('B','Salão dos Guardiões','B',[C(31,5),C(41,5),C(34,9),C(38,9),C(31,12),C(41,12),C(36,6),C(36,11),C(43,8)]),
 room('C','Salão das Armadilhas','C',[C(52,5),C(60,5),C(54,8),C(58,8),C(52,12),C(60,12),C(56,12),C(62,8)]),
 room('D','Câmara dos Altares','D',[C(52,28),C(56,28),C(60,28),C(51,32),C(55,32),C(59,32),C(62,30),C(54,25),C(58,25),C(56,30)]),
 room('E','Cofre Sombrio','E',[C(35,26),C(39,26),C(35,31),C(39,31),C(41,28),C(37,29)]),
 room('F','Câmara do Rei Esquecido','F',[],boss=[720,YP0+95])]
route=[C(2,8,0,22),C(12,8),C(25,8,24,22),C(36,9),C(46,8,24,22),C(56,9),C(55,15,24,22),C(55,21,24,22),C(55,28),C(45,28,24,22),C(37,28),C(28,28,24,22),C(20,30),[720,YP1+ST_H+30]]
zone=dict(w=W,h=H,ymin=20,props=props,spawns=[],plaza=[0,0,0,0],road=[],start=[1*TW+30,OY+8*TH+22],boss=[720,YP0+95],gate=[0,0],fx=fx,dark=1,
 crp=dict(rooms=rooms,route=route,plat=dict(x0=PX0,x1=PX1,y0=YP0,y1=YP1,sx0=SX0,sx1=SX1,elev=ELEV,sh=ST_H),walkTo=[8*TW,OY+8*TH+22]))
json.dump(zone,open(AS+'/zone_cripta2.json','w'))
# ---------- imagem do portal (recorte do mapa)
ov=im.crop((0,0,W,H)).resize((W*2,H*2),Image.NEAREST)
cw=int(ov.height*1.6); port=ov.crop((0,0,min(ov.width,cw),ov.height)).resize((1280,800),Image.NEAREST).convert('RGB')
port.save(AS+'/portal/d5.jpg',quality=88)
im.resize((W//2,H//2),Image.NEAREST).save('/tmp/cripta2_preview.png')
print('ok',W,H,len(props),len(fx))
