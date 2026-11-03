"""Zona 1 (floresta): campo aberto com bosques espaçados, clareiras com acampamentos e ruínas, lagos, e um portão de entrada ao sul.
Sem estrada obrigatória: o herói anda livre; as árvores formam bosques (densidade por ruído) em vez de cobrir tudo.
Uso (na pasta lendas-de-taverna/tools/mmo):  PACK_DIR=<pack> /usr/bin/python3 build_zone2.py   -> reescreve zone1.json / zone1_ground.png / atlas.*"""
import os,sys,json,hashlib,math,random
HERE=os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE,'town_world.py')).read())
BUSH=[b.resize((max(8,round(b.width*.62)),max(8,round(b.height*.62))),Image.NEAREST) for b in BUSH]   # arbustos menores
OUT=os.path.join(HERE,'..','..','mmo','assets')
THEME=os.environ.get('THEME','');SUF={'goblin':'_gob'}.get(THEME,'')     # THEME=goblin gera zone1_gob.* (toca de goblins)
GOB=THEME=='goblin'
if GOB:
    exec(open(os.path.join(HERE,'goblin_ia.py')).read())      # sprites gerados por IA (ia_src/) já na escala do jogo + colisões
    def dk(im,m=(.64,.8,.66)):
        a=np.array(im).astype(float);a[:,:,0]*=m[0];a[:,:,1]*=m[1];a[:,:,2]*=m[2];return Image.fromarray(a.astype('uint8'),'RGBA')
    VS=[dk(v,(.55,.7,.55)) for v in VS]                       # mato do chão mais escuro
    FENCE=GI['fence'][0]
Z=1.5
WW,WH=960,1500                      # px do pack (mundo = ×1.5)
def zs(im):return im.resize((max(1,int(im.width*Z)),max(1,int(im.height*Z))),Image.NEAREST)
ENTR=(480,1452);START=(480,1385)
GLADES=[(480,1290,'start'),(250,1150,'camp'),(700,1130,'ruin'),(430,960,'camp'),(760,850,'ruin'),(220,820,'camp'),(520,700,'ruin'),(300,520,'camp'),(700,470,'ruin'),(480,300,'camp'),(230,230,'ruin'),(740,220,'camp')]
LAKES=[(130,1040,60,38),(790,1030,64,40),(120,600,56,36),(820,640,60,38),(520,120,70,40)]
rr=random.Random(9)
# ---- ruído de baixa frequência: define bosques (alto) e campinas (baixo)
def smooth(seed,step):
    g=np.random.RandomState(seed).rand(WH//step+2,WW//step+2)
    return np.array(Image.fromarray((g*255).astype('uint8')).resize((WW,WH),Image.BICUBIC),dtype=float)/255
NZ=smooth(21,90)
def lake_in(x,y,m=20):return any(((x-l[0])/(l[2]+m))**2+((y-l[1])/(l[3]+m))**2<1 for l in LAKES)
def glade_d(x,y):return min(math.hypot(x-g[0],y-g[1]) for g in GLADES)
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
    # manchas de terra só nas clareiras (sem estrada)
    patches=[]
    for (gx,gy,k) in GLADES:
        for _ in range(5 if k!='ruin' else 3):patches.append((gx+rr.randrange(-34,34),gy+rr.randrange(-26,26)))
    for _ in range(34 if GOB else 14):patches.append((rr.randrange(80,WW-80),rr.randrange(120,WH-160)))
    paint_region(w,union_mask(patches,r),DR,r,edge=(112,78,48,255),rim=(40,92,24,255))
    lake=[]
    for (lx,ly,a,b) in LAKES:lake+=[(lx+dx,ly+dy) for dx,dy in [(0,0),(a*.5,b*.4),(-a*.5,b*.5),(a*.4,-b*.5),(-a*.7,-b*.1),(a*.8,-b*.1),(0,b*.7),(-a*.2,-b*.6)]]
    paint_region(w,union_mask(lake,r),WR,r,edge=(96,170,226,255),rim=(30,76,40,255))
    for yy in range(1422,1500,16):
        for xx in range(432,528,16):w.alpha_composite(r.choice(STN),(xx,yy))
    # chão de pedra das ruínas
    for (gx,gy,k) in GLADES:
        if k!='ruin':continue
        for yy in range(gy-24,gy+25,16):
            for xx in range(gx-40,gx+41,16):
                if ((xx-gx)/42)**2+((yy-gy)/28)**2<1:w.alpha_composite(r.choice(STN),(xx,yy))
    return w
G_=ground()
if GOB:
    a=np.array(G_).astype(float);a[:,:,0]*=.58;a[:,:,1]*=.72;a[:,:,2]*=.6;G_=Image.fromarray(a.astype('uint8'),'RGBA')
gimg=zs(G_);gimg.convert('RGB').save(os.path.join(OUT,'zone1'+SUF+'_ground.png'),optimize=True)
sprs={}
def reg(img,anc):
    img=zs(img);h=hashlib.md5(img.tobytes()+bytes(str(img.size),'ascii')).hexdigest()[:10]
    if h not in sprs:sprs[h]=(img,(int(anc[0]*Z),int(anc[1]*Z)))
    return h
P=[];ex=[]
def free(x,y,r):
    for (ax,ay,ar) in ex:
        if (x-ax)**2+(y-ay)**2<(ar+r)**2:return False
    return True
def add(spr,x,y,r,**kw):
    ex.append((x,y,r));d=dict(t='p',id=reg(spr,(spr.width//2,spr.height-2)),x=round(x*Z),y=round(y*Z))
    c=getattr(spr,'col',None)
    if c:d['col']=[[round(a*Z),round(b*Z),round(rad*Z)] for a,b,rad in c]       # colisão própria (relativa ao pé do sprite)
    P.append(d)
FX=[]
def add_torch(spr,x,y):
    add(spr,x,y,5);FX.append(dict(k='torch',x=round(x*Z),y=round((y-spr.height*.88)*Z)))
def addflat(spr,x,y):P.append(dict(t='flat',id=reg(spr,(spr.width//2,spr.height)),x=round(x*Z),y=round(y*Z)))
def er(spr):return max(5,spr.width*.38)
def fire(x,y,small=False):
    P.append(dict(t='fire',x=round(x*Z),y=round(y*Z),small=small));ex.append((x,y,10))
def _icy(im):
    a=np.array(im.convert('RGBA'));m=a[:,:,3]>0;b=(a[:,:,2].astype(int)>a[:,:,0].astype(int)+25)&(a[:,:,2]>150)&m
    return m.sum()>0 and b.sum()/m.sum()>.04
T_OAK=[t for t in T_OAK if not _icy(t)] or T_OAK;T_CON=[t for t in T_CON if not _icy(t)] or T_CON
def entr_clear(x,y):return abs(x-ENTR[0])<130 and y>ENTR[1]-260   # corredor livre da entrada
def tree():
    t=rr.random()
    if GOB:return rr.choice(GI['pine']) if t<.72 else rr.choice(GI['twisted']) if t<.84 else rr.choice(GI['bigtree']) if t<.93 else rr.choice(GI['deadskull'])
    return rr.choice(T_OAK) if t<.6 else rr.choice(T_CON)
# ---- portão da floresta
for sx in (-1,1):
    t=max(GI['pine'],key=lambda s:s.height) if GOB else max(T_OAK,key=lambda s:s.height);add(t,ENTR[0]+sx*(58 if GOB else 52),ENTR[1]+4,20)
    fire(ENTR[0]+sx*30,ENTR[1]-2,True)
    add(GI['totem'][0 if sx<0 else 1],ENTR[0]+sx*38,ENTR[1]-14,6) if GOB else add(BAN[1] if sx<0 else BAN[2],ENTR[0]+sx*38,ENTR[1]-14,6)
    for k in range(1,4 if not GOB else 5):add(rr.choice(GI['fence']) if GOB else FENCE,ENTR[0]+sx*(70+k*26 if GOB else 60+k*34),ENTR[1]+10,16)
# ---- clareiras: acampamentos e ruínas (reservam o espaço antes das árvores)
for (gx,gy,k) in GLADES:
    if GOB and k=='camp':
        fire(gx,gy);T1,T2=rr.sample(GI['tent'],2);add(T1,gx-58,gy-14,24);add(T2,gx+54,gy-22,24);add(GI['cauldron'][0],gx+18,gy+14,10)
        if rr.random()<.7:add(GI['drums'][0],gx-8,gy+34,20)
        for _ in range(3):add(rr.choice(GI['stake']),gx+rr.randrange(-80,80),gy+rr.randrange(30,52),5)
        for _ in range(3):addflat(rr.choice(GI['bonepile']),gx+rr.randrange(-60,60),gy+rr.randrange(-6,34))
        add_torch(GI['torch'][0],gx-30,gy+4);add_torch(GI['torch'][1],gx+34,gy+8)
        if rr.random()<.65:add(rr.choice(GI['totem']),gx+rr.choice((-1,1))*96,gy+12,7)
        if rr.random()<.5:add(rr.choice(GI['banner']),gx+rr.choice((-1,1))*76,gy-34,6)
        add(rr.choice(GI['palisade']),gx-86,gy+44,26)
    elif GOB and k=='ruin':
        add(rr.choice(GI['totem']),gx,gy-6,8);fire(gx,gy+16,True)
        for a in range(0,360,45):add(rr.choice(GI['stake']),gx+math.cos(math.radians(a))*54,gy+math.sin(math.radians(a))*34,5)
        for _ in range(3):addflat(rr.choice(GI['bonepile']),gx+rr.randrange(-44,44),gy+rr.randrange(-22,32))
        add_torch(GI['torch'][0],gx-30,gy-18);add_torch(GI['torch'][1],gx+30,gy-18)
        add(rr.choice(GI['barricade']),gx+rr.choice((-1,1))*80,gy+22,26)
    elif k=='camp':
        fire(gx,gy);add(BARREL,gx+28,gy-4,8);add(BARREL,gx+42,gy+6,8);add(FENCE,gx-70,gy+34,36);add(rr.choice(ROCK_BIG),gx-34,gy-20,12)
    elif k=='ruin':
        for a in range(0,360,45):
            ax=gx+math.cos(math.radians(a))*46;ay=gy+math.sin(math.radians(a))*30
            if a%90==0:add(rr.choice(ROCK_BIG),ax,ay,12)
            else:add(rr.choice(ROCK_SM),ax,ay,6)
        add(BAN[rr.randrange(3)],gx-24,gy-26,6);add(BAN[rr.randrange(3)],gx+24,gy-26,6);fire(gx,gy+4,True)
# ---- árvores: borda densa, bosques por ruído, campinas quase vazias
def dens_gap(x,y):
    edge=min(x,WW-x,y,WH-y)
    if edge<70:return 30                      # parede de árvores só na borda do mapa
    v=NZ[min(WH-1,int(y)),min(WW-1,int(x))]
    if v>.75:return 70                        # pequeno bosque fechado
    if v>.67:return 190                       # bosque ralo
    return 420                                # campo aberto: uma árvore isolada aqui e ali
for _ in range(9000):
    x=rr.randrange(-10,WW+10);y=rr.randrange(30,WH+40)
    if lake_in(x,y,12):continue
    if glade_d(x,y)<(150 if min(x,WW-x,y,WH-y)>70 else 0):continue
    if entr_clear(x,y):continue
    if math.hypot(x-START[0],y-START[1])<170 and min(x,WW-x,y,WH-y)>80:continue
    g=dens_gap(x,y)
    if g>=420 and rr.random()<.9:continue
    if free(x,y,g/2):add(tree(),x,y,g/2)
# ---- ambientação: arbustos, pedras, mato e flores
for n in range(150):
    for _ in range(30):
        x=rr.randrange(60,WW-60);y=rr.randrange(100,WH-140)
        if not lake_in(x,y,8) and free(x,y,10) and not entr_clear(x,y):break
    else:continue
    k=n%6
    if GOB:
        t=rr.random()
        if k in(0,1):
            sp=rr.choice(GI['mush']) if t<.28 else rr.choice(GI['thorn']) if t<.5 else rr.choice(GI['bush'])
        elif k==2:sp=rr.choice(GI['stump']+GI['log']) if t<.45 else rr.choice(GI['bush'])
        elif k==3:sp=rr.choice(GI['rockbig'])
        elif k==4:sp=rr.choice(GI['stake']) if t<.25 else rr.choice(GI['rocksm'])
        else:sp=rr.choice(GI['rocksm'])
        if getattr(sp,'kind','')=='flat':addflat(sp,x,y)
        else:add(sp,x,y,er(sp))
        continue
    if k in(0,1,2):add(rr.choice(BUSH),x,y,7)
    elif k==3:add(rr.choice(ROCK_BIG),x,y,12)
    else:add(rr.choice(ROCK_SM),x,y,6)
if GOB:                                      # decoração rasteira: poças, galhos, ossos e flores roxas
    for n in range(260):
        x=rr.randrange(30,WW-30);y=rr.randrange(60,WH-90)
        if entr_clear(x,y):continue
        t=rr.random()
        if lake_in(x,y,6):continue
        sp=rr.choice(GI['puddle']) if t<.12 else rr.choice(GI['twig']) if t<.45 else rr.choice(GI['bone']) if t<.62 else rr.choice(GI['flower'])
        addflat(sp,x,y)
for (gx,gy,k) in GLADES:                     # tufos de mato ao redor de cada clareira
    for _ in range(26):
        x=gx+rr.randrange(-90,90);y=gy+rr.randrange(-60,60)
        if not lake_in(x,y,0):P.append(dict(t='flat',id=reg((s:=rr.choice(VS[-30:])),(s.width//2,s.height)),x=round(x*Z),y=round(y*Z)))
for n in range(1100):
    x=rr.randrange(8,WW-8);y=rr.randrange(30,WH-8)
    if lake_in(x,y,0):continue
    if rr.random()<.9:P.append(dict(t='flat',id=reg((s:=rr.choice(VS)),(s.width//2,s.height)),x=round(x*Z),y=round(y*Z)))
P.sort(key=lambda p:p['y'])
for i,f in enumerate(BFIRE):k=reg(f,(16,32));sprs['bf%d'%i]=sprs.pop(k)
for i,f in enumerate(FIRE):k=reg(f,(16,48));sprs['fi%d'%i]=sprs.pop(k)
items=sorted(sprs.items(),key=lambda kv:-kv[1][0].height);Wd=1024;x=y=sh=0;pos={}
for k,(im,anc) in items:
    if x+im.width+1>Wd:x=0;y+=sh+1;sh=0
    pos[k]=(x,y,im.width,im.height,anc[0],anc[1]);x+=im.width+1;sh=max(sh,im.height)
atlas=Image.new('RGBA',(Wd,y+sh+1),(0,0,0,0))
for k,(im,anc) in items:atlas.alpha_composite(im,pos[k][:2])
atlas.save(os.path.join(OUT,'atlas'+SUF+'.png'),optimize=True);json.dump({k:list(v) for k,v in pos.items()},open(os.path.join(OUT,'atlas'+SUF+'.json'),'w'))
# ---- pontos de nascimento: espalhados pelo campo aberto, longe da entrada
solid=[(p['x']/Z,p['y']/Z) for p in P if p['t']=='p']
spawns=[]
for _ in range(40000):
    if len(spawns)>=46:break
    x=rr.randrange(70,WW-70);y=rr.randrange(110,1270)
    if lake_in(x,y,28) or any((x-a)**2+(y-b)**2<36**2 for a,b in solid):continue
    if any((x-a)**2+(y-b)**2<72**2 for a,b in spawns):continue
    spawns.append((x,y))
spawns=[[round(a*Z),round(b*Z)] for a,b in spawns]
zone=dict(w=gimg.width,h=gimg.height,props=P,spawns=spawns,plaza=[0,0,1,1],pond=[round(LAKES[1][0]*Z),round(LAKES[1][1]*Z),round(LAKES[1][2]*Z),round(LAKES[1][3]*Z)],
  road=[],start=[round(START[0]*Z),round(START[1]*Z)],boss=[round(480*Z),round(300*Z)],gate=[round(ENTR[0]*Z),round(ENTR[1]*Z)])
if FX:zone['fx']=FX
json.dump(zone,open(os.path.join(OUT,'zone1'+SUF+'.json'),'w'),separators=(',',':'))
print('zona',gimg.size,'props',len(P),'árvores',sum(1 for p in P if p['t']=='p' and False),'sprites',len(sprs),'spawns',len(spawns),'atlas',atlas.size)
dbg=gimg.copy().convert('RGBA');d=ImageDraw.Draw(dbg)
for s in spawns:d.ellipse((s[0]-5,s[1]-5,s[0]+5,s[1]+5),fill=(255,0,0,255))
os.makedirs('/tmp/mock',exist_ok=True);dbg.resize((dbg.width//3,dbg.height//3)).save('/tmp/mock/zone2_debug.png')
