"""Zona 1 (floresta) maior, com entrada/portal da floresta ao sul e estrada sinuosa com clareiras, acampamento e lago.
Uso (na pasta hearthblade/tools):  PACK_DIR=<pack> /usr/bin/python3 build_zone2.py   -> reescreve zone1.json / zone1_ground.png / atlas.*"""
import os,sys,json,hashlib,math,random
HERE=os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE,'town_world.py')).read())
OUT=os.path.join(HERE,'..','assets')
Z=1.5
WW,WH=960,1500                      # px do pack (mundo = ×1.5)
def zs(im):return im.resize((max(1,int(im.width*Z)),max(1,int(im.height*Z))),Image.NEAREST)
ENTR=(480,1452)                     # centro do portão da floresta
START=(480,1385)
ROAD=[(480,1470),(480,1390),(440,1320),(380,1255),(340,1180),(345,1100),(400,1030),(480,985),(560,935),(610,865),(615,780),(570,700),(500,645),(430,590),(395,510),(410,430),(470,360),(540,300),(570,225),(545,150),(500,110)]
BR_W=[(400,1030),(320,985),(240,930),(180,850),(165,770),(185,700)]            # ramal oeste -> acampamento
BR_E=[(560,935),(650,950),(720,1010),(745,1090),(740,1180)]                      # ramal leste -> lago
CLEAR=[(480,1330),(345,1130),(470,985),(615,800),(450,610),(405,470),(545,290),(520,150),(185,700),(745,1130)]
LAKE_C=(745,1200,70,46)
RP=[]
for rd in (ROAD,BR_W,BR_E):RP+=poly_pts(rd,10)
def rd_dist(x,y):return min(math.hypot(x-a,y-b) for a,b in RP)
def ground():
    r=random.Random(3);w=Image.new('RGBA',(WW,WH),(0,0,0,255));fill(w,(0,0,WW,WH),GR,r)
    nz=np.array(Image.fromarray((np.random.RandomState(4).rand(WH//24+1,WW//24+1)*255).astype('uint8')).resize((WW,WH),Image.BICUBIC),dtype=float)
    lay=Image.new('RGBA',(WW,WH),(0,0,0,0));px=lay.load()
    for yy in range(0,WH-1,2):
        for xx in range(0,WW-1,2):
            v=nz[yy,xx]
            if v>170:px[xx,yy]=(150,200,70,26);px[xx+1,yy]=(150,200,70,26)
            elif v<70:px[xx,yy]=(10,50,10,34);px[xx+1,yy]=(10,50,10,34)
    w.alpha_composite(lay)
    centers=CLEAR+poly_pts(ROAD)+poly_pts(BR_W)+poly_pts(BR_E)
    paint_region(w,union_mask(centers,r),DR,r,edge=(112,78,48,255),rim=(40,92,24,255))
    lake=[(LAKE_C[0]+dx,LAKE_C[1]+dy) for dx,dy in [(0,0),(40,20),(-30,25),(30,-30),(-45,-5),(55,-5),(0,40),(-15,-35)]]
    paint_region(w,union_mask(lake,r),WR,r,edge=(96,170,226,255),rim=(30,76,40,255))
    # pátio de pedra do portão
    for yy in range(1422,1500,16):
        for xx in range(432,528,16):w.alpha_composite(r.choice(STN),(xx,yy))
    return w
G_=ground();GROUND_=G_
gimg=zs(G_);gimg.convert('RGB').save(os.path.join(OUT,'zone1_ground.png'),optimize=True)
sprs={}
def reg(img,anc):
    img=zs(img);h=hashlib.md5(img.tobytes()+bytes(str(img.size),'ascii')).hexdigest()[:10]
    if h not in sprs:sprs[h]=(img,(int(anc[0]*Z),int(anc[1]*Z)))
    return h
rr=random.Random(9);P=[];ex=[]
def free(x,y,r):
    for (ax,ay,ar) in ex:
        if (x-ax)**2+(y-ay)**2<(ar+r)**2:return False
    return True
def add(spr,x,y,r,**kw):
    ex.append((x,y,r));P.append(dict(t='p',id=reg(spr,(spr.width//2,spr.height-2)),x=round(x*Z),y=round(y*Z)))
def tree():
    t=rr.random();return rr.choice(T_OAK) if t<.5 else rr.choice(T_CON) if t<.8 else rr.choice(T_PIN)
def lake_in(x,y,m=20):return ((x-LAKE_C[0])/(LAKE_C[2]+m))**2+((y-LAKE_C[1])/(LAKE_C[3]+m))**2<1
def opened(x,y):
    if rd_dist(x,y)<68:return True
    return any(math.hypot(x-a,y-b)<130 for a,b in CLEAR)
# portão da floresta: duas árvores grandes, tochas e faixas; muralha de árvores atrás
for sx in (-1,1):
    t=max(T_OAK,key=lambda s:s.height);add(t,ENTR[0]+sx*52,ENTR[1]+4,20)
    P.append(dict(t='fire',x=round((ENTR[0]+sx*30)*Z),y=round((ENTR[1]-2)*Z),small=True));ex.append((ENTR[0]+sx*30,ENTR[1]-2,10))
    add(BAN[1] if sx<0 else BAN[2],ENTR[0]+sx*38,ENTR[1]-14,6)
    for k in range(1,4):add(FENCE,ENTR[0]+sx*(60+k*34),ENTR[1]+10,16)
# árvores
for _ in range(7000):
    x=rr.randrange(-10,WW+10);y=rr.randrange(30,WH+40)
    if opened(x,y) or lake_in(x,y):continue
    if y>ENTR[1]-8 and abs(x-ENTR[0])<40:continue
    if free(x,y,18):add(tree(),x,y,18)
for (cx,cy) in CLEAR:                       # pequenos bosques espalhados nas clareiras
    for _ in range(4):
        x=cx+rr.randrange(-70,70);y=cy+rr.randrange(-60,60)
        if rd_dist(x,y)<40 or lake_in(x,y):continue
        t=rr.choice(T_OAKS+T_SM)
        if free(x,y,14):add(t,x,y,14)
for n in range(150):                         # arbustos e pedras
    for _ in range(30):
        c=rr.choice(CLEAR);x=c[0]+rr.randrange(-110,110);y=c[1]+rr.randrange(-110,110)
        if opened(x,y) and rd_dist(x,y)>26 and not lake_in(x,y) and free(x,y,10):break
    else:continue
    k=n%5
    if k in(0,1):add(rr.choice(BUSH),x,y,10)
    elif k==2:add(rr.choice(ROCK_BIG),x,y,12)
    else:add(rr.choice(ROCK_SM),x,y,6)
for n in range(900):                         # mato e flores
    x=rr.randrange(8,WW-8);y=rr.randrange(30,WH-8)
    if lake_in(x,y,0):continue
    if rr.random()<.9:P.append(dict(t='flat',id=reg((s:=rr.choice(VS)),(s.width//2,s.height)),x=round(x*Z),y=round(y*Z)))
# acampamento (ramal oeste) com fogueira, barris e cerca
cx,cy=185,700;P.append(dict(t='fire',x=round(cx*Z),y=round(cy*Z),small=False));ex.append((cx,cy,16))
add(BARREL,cx+26,cy-4,8);add(BARREL,cx+40,cy+4,8);add(FENCE,cx-80,cy+40,40);add(FENCE,cx+70,cy-50,30)
# fogueiras de luz ao longo da estrada
for (x,y) in [(ROAD[4][0]+34,ROAD[4][1]),(ROAD[9][0]-34,ROAD[9][1]),(ROAD[14][0]+34,ROAD[14][1]),(ROAD[18][0]-34,ROAD[18][1])]:
    P.append(dict(t='fire',x=round(x*Z),y=round(y*Z),small=True))
P.sort(key=lambda p:p['y'])
for i,f in enumerate(BFIRE):k=reg(f,(16,32));sprs['bf%d'%i]=sprs.pop(k)
for i,f in enumerate(FIRE):k=reg(f,(16,48));sprs['fi%d'%i]=sprs.pop(k)
items=sorted(sprs.items(),key=lambda kv:-kv[1][0].height);Wd=1024;x=y=sh=0;pos={}
for k,(im,anc) in items:
    if x+im.width+1>Wd:x=0;y+=sh+1;sh=0
    pos[k]=(x,y,im.width,im.height,anc[0],anc[1]);x+=im.width+1;sh=max(sh,im.height)
atlas=Image.new('RGBA',(Wd,y+sh+1),(0,0,0,0))
for k,(im,anc) in items:atlas.alpha_composite(im,pos[k][:2])
atlas.save(os.path.join(OUT,'atlas.png'),optimize=True);json.dump({k:list(v) for k,v in pos.items()},open(os.path.join(OUT,'atlas.json'),'w'))
# pontos de nascimento: ao longo da estrada e nas clareiras, longe da entrada
solid=[(p['x']/Z,p['y']/Z) for p in P if p['t']=='p']
spawns=[]
for _ in range(20000):
    if len(spawns)>=42:break
    c=rr.choice(CLEAR+[RP[i] for i in range(0,len(RP),6)]);x=c[0]+rr.randrange(-70,70);y=c[1]+rr.randrange(-70,70)
    if not(opened(x,y)) or lake_in(x,y,30) or y>1280:continue
    if any((x-a)**2+(y-b)**2<42**2 for a,b in solid):continue
    if any((x-a)**2+(y-b)**2<78**2 for a,b in spawns):continue
    spawns.append((x,y))
spawns=[[round(a*Z),round(b*Z)] for a,b in spawns]
zone=dict(w=gimg.width,h=gimg.height,props=P,spawns=spawns,plaza=[0,0,1,1],pond=[round(LAKE_C[0]*Z),round(LAKE_C[1]*Z),round(LAKE_C[2]*Z),round(LAKE_C[3]*Z)],
  road=[[round(a*Z),round(b*Z)] for a,b in RP],start=[round(START[0]*Z),round(START[1]*Z)],boss=[round(ROAD[-1][0]*Z),round(ROAD[-1][1]*Z)],
  gate=[round(ENTR[0]*Z),round(ENTR[1]*Z)])
json.dump(zone,open(os.path.join(OUT,'zone1.json'),'w'),separators=(',',':'))
print('zona',gimg.size,'props',len(P),'sprites',len(sprs),'spawns',len(spawns),'atlas',atlas.size)
dbg=gimg.copy().convert('RGBA');d=ImageDraw.Draw(dbg)
for s in spawns:d.ellipse((s[0]-5,s[1]-5,s[0]+5,s[1]+5),fill=(255,0,0,255))
d.ellipse((zone['start'][0]-6,zone['start'][1]-6,zone['start'][0]+6,zone['start'][1]+6),fill=(255,255,0,255))
os.makedirs('/tmp/mock',exist_ok=True);dbg.resize((dbg.width//3,dbg.height//3)).save('/tmp/mock/zone2_debug.png')
