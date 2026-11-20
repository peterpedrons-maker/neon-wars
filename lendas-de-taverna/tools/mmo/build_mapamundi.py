# Mapa-múndi de fantasia da Região 1 (pergaminho, tinta, aquarela) -> mmo/assets/mapa_regiao1.png + _ids.png
import numpy as np, random, math
from PIL import Image, ImageDraw, ImageFilter
from scipy.ndimage import gaussian_filter, zoom
W,H=1100,2240; S=2; R=random.Random(7); N=np.random.RandomState(7)
Z={ # chave:(cx,cy,w,h,bioma)
'town':(640,1570,320,120,'town'),'zone_estrada':(640,1370,240,100,'road'),'zone_planicie':(640,1130,440,270,'plain'),'zone_ponte':(600,905,240,100,'river'),
'zone_colinas':(560,720,360,170,'hills'),'zone_desfiladeiro':(560,540,240,100,'mount'),'zone_passo':(560,350,340,150,'mount'),'zone_goblins':(190,930,300,200,'dark'),
'zone_lenhadores':(190,720,220,100,'forest'),'zone_ogros':(190,500,300,200,'forest'),'zone_brejo':(380,1360,220,100,'swamp'),'zone_brumas':(210,1580,340,190,'swamp'),
'zone_cemiterio':(920,500,280,200,'grave'),'zone_mortos':(905,300,220,100,'grave'),'zone_lago':(985,1215,190,100,'lake'),'zone_clareira':(150,1130,250,100,'dark'),
'zone_eremita':(140,1360,200,100,'forest'),'zone_cabana':(210,1790,240,100,'swamp'),'zone_gruta':(940,860,230,110,'mount'),'zone_mina':(190,250,230,110,'mount'),
'cidade2':(560,160,320,110,'town')}
KEYS=list(Z); 
def noise(sc,seed):
    r=np.random.RandomState(seed); g=r.rand(H//sc+3,W//sc+3); g=gaussian_filter(g,1.2); z=zoom(g,sc,order=3)[:H,:W]; z=(z-z.min())/(z.max()-z.min()); return z
nA=noise(40,1)-.5; nB=noise(16,2)-.5; nC=noise(80,3)-.5
yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
wx=xx+nA*110+nB*40; wy=yy+nC*110+nB*40
D=np.zeros((len(KEYS),H,W),np.float32)
for i,k in enumerate(KEYS):
    cx,cy,w,h,b=Z[k]; D[i]=np.maximum(np.abs(wx-cx)/(w/2+12),np.abs(wy-cy)/(h/2+12))
ID=D.argmin(0); DM=D.min(0)
from scipy.ndimage import binary_fill_holes,binary_closing,binary_opening
land=DM<1.55+nB*1.1+nC*.5
land=binary_closing(land,iterations=30)
land=binary_fill_holes(land)
land=gaussian_filter(land.astype(np.float32),10)>.5
land[:40,:]=False;land[-40:,:]=False;land[:,:30]=False;land[:,-30:]=False
# imagem base (supersample S)
def up(a): return np.kron(a,np.ones((S,S),a.dtype)) if a.ndim==2 else a
# pergaminho
par=np.zeros((H,W,3),np.float32); par[:]=(226,205,160)
fib=noise(6,11); par+= (fib[...,None]-.5)*28; par+=(noise(150,12)[...,None]-.5)*40
TINT={'town':(214,180,120),'road':(222,196,140),'plain':(204,208,140),'river':(176,198,176),'hills':(196,182,140),'mount':(176,166,150),'dark':(120,150,110),'forest':(150,176,112),'swamp':(150,160,100),'grave':(168,150,170),'lake':(160,190,196)}
col=np.zeros((H,W,3),np.float32)
for i,k in enumerate(KEYS): col[ID==i]=TINT[Z[k][4]]
col=np.stack([gaussian_filter(col[...,c],9) for c in range(3)],-1)
lm=gaussian_filter(land.astype(np.float32),3)[...,None]
img=par*(1-.55*lm)+col*.55*lm
# mar: azul-acinzentado leve fora da terra
sea=np.array((178,190,176),np.float32); img=img*lm+(par*.8+sea*.2)*(1-lm)
# sombra de costa
edge=gaussian_filter(land.astype(np.float32),14); img*= (1-0.25*np.clip(edge*(1-edge)*4,0,1))[...,None]
base=Image.fromarray(np.clip(img,0,255).astype(np.uint8)).resize((W*S,H*S),Image.BICUBIC)
d=ImageDraw.Draw(base,'RGBA')
INK=(52,34,18,255); INK2=(52,34,18,150)
def P(x,y): return (x*S,y*S)
# costa em tinta + ondas
from skimage import measure
for c in measure.find_contours(gaussian_filter(land.astype(np.float32),2),.5):
    pts=[(p[1]*S,p[0]*S) for p in c[::4]]
    if len(pts)>5: d.line(pts,fill=INK,width=3)
from scipy.ndimage import distance_transform_edt
dist_c=distance_transform_edt(~land)
for _ in range(2600):
    x,y=R.randint(10,W-10),R.randint(10,H-10)
    if land[y,x] or dist_c[y,x]>150: continue
    # perto da costa
    if gaussian_filter is None: pass
    d.arc([P(x-9,y-3)[0],P(x-9,y-3)[1],P(x,y+6)[0],P(x,y+6)[1]],200,340,fill=(70,90,100,160),width=2)
    d.arc([P(x,y-3)[0],P(x,y-3)[1],P(x+9,y+6)[0],P(x+9,y+6)[1]],200,340,fill=(70,90,100,160),width=2)
# limites de cada zona: contorno tracejado em tinta
def dashed(pts,on=16,off=9,fill=(70,40,20,215),wd=5):
    acc=0;draw=True
    for p,q in zip(pts,pts[1:]):
        L=math.hypot(q[0]-p[0],q[1]-p[1])
        if draw: d.line([p,q],fill=fill,width=wd)
        acc+=L
        if acc>=(on if draw else off): acc=0;draw=not draw
for i,k in enumerate(KEYS):
    m=gaussian_filter(((ID==i)&land).astype(np.float32),4)
    for c in measure.find_contours(m,.5):
        if len(c)<30: continue
        dashed([(p[1]*S,p[0]*S) for p in c[::2]])
# --- ícones ---
def tree(x,y,k=1,dark=False):
    g=(38,86,48) if not dark else (28,62,48); gl=(70,128,72) if not dark else (50,92,70)
    s=7*k; d.polygon([P(x,y-s*2.3),P(x-s,y),P(x+s,y)],fill=g+(255,),outline=INK)
    d.polygon([P(x,y-s*2.3),P(x-s,y),P(x-s*.1,y)],fill=gl+(255,))
    d.rectangle([P(x-1,y)[0],P(x-1,y)[1],P(x+1,y+3*k)[0],P(x+1,y+3*k)[1]],fill=(80,54,30,255))
def mount(x,y,k=1):
    s=14*k; d.polygon([P(x-s,y),P(x,y-s*1.5),P(x+s,y)],fill=(170,160,140,255),outline=INK)
    d.polygon([P(x,y-s*1.5),P(x+s,y),P(x+s*.1,y)],fill=(112,100,88,255))
    d.polygon([P(x,y-s*1.5),P(x-s*.28,y-s*.95),P(x,y-s*1.05),P(x+s*.28,y-s*.95)],fill=(245,242,234,255))
    d.line([P(x-s,y),P(x,y-s*1.5),P(x+s,y)],fill=INK,width=2)
def hill(x,y,k=1):
    s=11*k; d.chord([P(x-s,y-s*.8),P(x+s,y+s*.8)],180,360,fill=(188,176,120,255),outline=INK)
def reed(x,y):
    for dx in(-3,0,3): d.line([P(x+dx,y),P(x+dx*1.4,y-8)],fill=(80,100,40,255),width=2)
    d.ellipse([P(x-1,y-11)[0],P(x-1,y-11)[1],P(x+1,y-8)[0],P(x+1,y-8)[1]],fill=(110,70,40,255))
def grave(x,y):
    d.rectangle([P(x-3,y-8)[0],P(x-3,y-8)[1],P(x+3,y)[0],P(x+3,y)[1]],fill=(150,148,150,255),outline=INK); d.line([P(x-3,y-4),P(x+3,y-4)],fill=INK,width=1)
def tuft(x,y): d.line([P(x-2,y),P(x-3,y-4)],fill=(100,120,60,200),width=1);d.line([P(x,y),P(x,y-5)],fill=(100,120,60,200),width=1);d.line([P(x+2,y),P(x+3,y-4)],fill=(100,120,60,200),width=1)
def house(x,y,k=1):
    s=8*k; d.rectangle([P(x-s,y-s*.8)[0],P(x-s,y-s*.8)[1],P(x+s,y)[0],P(x+s,y)[1]],fill=(232,214,170,255),outline=INK)
    d.polygon([P(x-s*1.2,y-s*.8),P(x,y-s*1.8),P(x+s*1.2,y-s*.8)],fill=(168,68,44,255),outline=INK)
ptsDone=[]
def free(x,y,r):
    for (a,b,c) in ptsDone:
        if (a-x)**2+(b-y)**2<(r+c)**2: return False
    return True
items=[]
for i,k in enumerate(KEYS):
    cx,cy,w,h,b=Z[k]
    n={'town':0,'road':0,'plain':20,'river':8,'hills':34,'mount':34,'dark':110,'forest':90,'swamp':40,'grave':24,'lake':10}[b]
    if k=='zone_planicie': n=16
    cnt=0;tries=0
    while cnt<n and tries<n*30:
        tries+=1
        x=R.randint(int(cx-w/2),int(cx+w/2)); y=R.randint(int(cy-h/2),int(cy+h/2))
        if not(0<=x<W and 0<=y<H) or not land[y,x]: continue
        if ID[y,x]!=i and b!='plain': continue
        items.append((y,b,x,y,i)); cnt+=1
items.sort()
LAKES=[(985,1215,70,28),(520,1090,60,26),(330,640,0,0)]
RIV=[(600,1000),(590,940),(610,890),(640,850),(700,800),(760,760)]
# lagos e rio (antes dos ícones)
lk=Image.new('L',(W*S,H*S),0); ld=ImageDraw.Draw(lk)
def blob(cx,cy,rx,ry):
    pts=[(cx+math.cos(a)*rx*(1+.18*math.sin(a*3+cx)),cy+math.sin(a)*ry*(1+.18*math.cos(a*2+cy))) for a in np.linspace(0,6.28,40)]
    ld.polygon([P(*p) for p in pts],fill=255)
blob(990,1215,78,30); blob(560,1130,70,28); blob(190,1560,50,20)
def wob(pts,amp,seed,step=6):
    r=random.Random(seed);out=[];
    for p,q in zip(pts,pts[1:]):
        L=math.hypot(q[0]-p[0],q[1]-p[1]);n=max(2,int(L/step));nx,ny=-(q[1]-p[1])/L,(q[0]-p[0])/L;ph=r.random()*6
        for t in range(n):
            u=t/n;o=math.sin(u*math.pi*2+ph)*amp+math.sin(u*9+ph)*amp*.3
            out.append((p[0]+(q[0]-p[0])*u+nx*o,p[1]+(q[1]-p[1])*u+ny*o))
    out.append(pts[-1]);return out
def river(pts,w0,w1,seed):
    pp=wob(pts,16,seed)
    for i,(a,b2) in enumerate(zip(pp,pp[1:])):
        w=w0+(w1-w0)*i/len(pp); ld.line([P(*a),P(*b2)],fill=255,width=int(w*S)); ld.ellipse([P(a[0]-w/2,a[1]-w/2)[0],P(a[0]-w/2,a[1]-w/2)[1],P(a[0]+w/2,a[1]+w/2)[0],P(a[0]+w/2,a[1]+w/2)[1]],fill=255)
river([(760,700),(700,790),(630,880),(600,960),(560,1090)],3,9,3)
river([(800,920),(900,1000),(960,1100),(985,1190)],4,9,5)
river([(630,880),(720,905),(800,920)],5,6,8)
lkb=lk.filter(ImageFilter.GaussianBlur(2)); 
water=Image.new('RGBA',base.size,(104,150,170,255)); base.paste(water,(0,0),lkb)
d=ImageDraw.Draw(base,'RGBA')
lkm=np.array(lk)>128
from scipy.ndimage import binary_erosion
for c in measure.find_contours((lkm).astype(np.float32),.5):
    d.line([(p[1],p[0]) for p in c[::3]],fill=INK,width=3)
for _ in range(500):
    x,y=R.randint(0,W-1),R.randint(0,H-1)
    if lkm[y*S,x*S]: d.line([P(x-5,y),P(x+5,y)],fill=(220,238,240,170),width=2)
for y_,b,x,y,i in items:
    if lkm[y*S,x*S]: continue
    if b in('forest','dark'): tree(x,y,R.uniform(.9,1.3),b=='dark')
    elif b=='mount': mount(x,y,R.uniform(.9,1.5))
    elif b=='hills': hill(x,y,R.uniform(.9,1.4))
    elif b=='swamp': (reed(x,y) if R.random()<.5 else tuft(x,y))
    elif b=='grave': (grave(x,y) if R.random()<.7 else tree(x,y,1,True))
    elif b=='plain': (tuft(x,y) if R.random()<.6 else tree(x,y,.9))
    elif b=='river': tuft(x,y)
# cidades
for k,n,sc in(('town',7,1.3),('cidade2',5,1.1)):
    cx,cy=Z[k][:2]
    for j in range(n): house(cx-60+j*20+R.randint(-4,4),cy+R.randint(-14,16),sc)
# estradas pontilhadas
ADJ=[('town','zone_estrada'),('zone_estrada','zone_planicie'),('zone_planicie','zone_ponte'),('zone_planicie','zone_goblins'),('zone_planicie','zone_brejo'),('zone_planicie','zone_lago'),('zone_goblins','zone_lenhadores'),('zone_goblins','zone_clareira'),('zone_brejo','zone_brumas'),('zone_brejo','zone_eremita'),('zone_ponte','zone_colinas'),('zone_colinas','zone_cemiterio'),('zone_colinas','zone_desfiladeiro'),('zone_desfiladeiro','zone_passo'),('zone_lenhadores','zone_ogros'),('zone_ogros','zone_passo'),('zone_cemiterio','zone_mortos'),('zone_mortos','zone_passo'),('zone_cemiterio','zone_gruta'),('zone_passo','zone_mina'),('zone_brumas','zone_cabana'),('zone_passo','cidade2')]
MAIN={('town','zone_estrada'),('zone_estrada','zone_planicie'),('zone_planicie','zone_ponte'),('zone_ponte','zone_colinas'),('zone_colinas','zone_desfiladeiro'),('zone_desfiladeiro','zone_passo'),('zone_passo','cidade2')}
for a,b in ADJ:
    A=Z[a][:2];B=Z[b][:2]; pts=[A,(A[0],B[1]),B] if abs(A[0]-B[0])>8 and abs(A[1]-B[1])>8 else [A,B]
    pp=wob(pts,9,hash(a+b)%1000,5); main=(a,b) in MAIN; wd=3.4 if main else 2.4
    for j,(x,y) in enumerate(pp):
        if j%2==0: d.ellipse([x*S-wd,y*S-wd,x*S+wd,y*S+wd],fill=(120,40,28,240) if main else (96,64,36,215))
# moldura e bússola
fr=Image.new('RGBA',base.size,(0,0,0,0)); fd=ImageDraw.Draw(fr)
for t,wd in((6,4),(16,2),(20,1)): fd.rectangle([t,t,W*S-t,H*S-t],outline=INK,width=wd)
base=Image.alpha_composite(base.convert('RGBA'),fr); d=ImageDraw.Draw(base,'RGBA')
cx,cy=W-110,140
for a,l,c in((-90,72,(150,40,30,255)),(0,52,INK),(90,52,INK),(180,52,INK)):
    r=math.radians(a); p1=(cx+math.cos(r)*l,cy+math.sin(r)*l); pa=(cx+math.cos(r+1.57)*9,cy+math.sin(r+1.57)*9); pb=(cx+math.cos(r-1.57)*9,cy+math.sin(r-1.57)*9)
    d.polygon([P(*p1),P(*pa),P(cx,cy),P(*pb)],fill=c,outline=INK)
for a in(45,135,225,315):
    r=math.radians(a); d.polygon([P(cx+math.cos(r)*34,cy+math.sin(r)*34),P(cx+math.cos(r+1.57)*6,cy+math.sin(r+1.57)*6),P(cx,cy),P(cx+math.cos(r-1.57)*6,cy+math.sin(r-1.57)*6)],fill=(190,160,100,255),outline=INK)
d.ellipse([P(cx-80,cy-80)[0],P(cx-80,cy-80)[1],P(cx+80,cy+80)[0],P(cx+80,cy+80)[1]],outline=INK,width=3)
# vinheta
out=np.array(base.convert('RGB')).astype(np.float32); hh,ww=out.shape[:2]
v=np.mgrid[0:hh,0:ww]; vx=(v[1]/ww-.5)*2; vy=(v[0]/hh-.5)*2; vg=np.clip(1-.3*(np.maximum(abs(vx),abs(vy))**4),.55,1)
out*=vg[...,None]
fin=Image.fromarray(np.clip(out,0,255).astype(np.uint8)).resize((W//2*1,H//2*1) if False else (W,H),Image.LANCZOS)
fin.save('mmo/assets/mapa_regiao1.png',optimize=True)
Image.fromarray(np.where(land,ID,255).astype(np.uint8)).resize((W//2,H//2),Image.NEAREST).save('mmo/assets/mapa_regiao1_ids.png')
print('ok',KEYS)
