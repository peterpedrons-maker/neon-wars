"""Região 1 — mapa aberto GRANDE de teste (protótipo): planície, floresta, lago, rio, colinas rochosas e 4 vilas.
Usa os sprites que já existem (atlas da floresta + casas do atlas da cidade); o chão é gerado por código em escala 1/4 do mundo
(1 px do chão = 4 px do mundo) e o renderizador 3D refaz o chão em alta qualidade a partir das máscaras (terra/pedra/água).
Uso (em lendas-de-taverna/tools/mmo):  python3 build_regiao1.py   -> escreve mmo/assets/zone_regiao1.json, zone_regiao1_ground.png, atlas_regiao1.json/png"""
import os,json,math,random
import numpy as np
from PIL import Image
HERE=os.path.dirname(os.path.abspath(__file__));A=os.path.join(HERE,'..','..','mmo','assets')
W=H=5000;GS=4;gw=W//GS;gh=H//GS
rr=random.Random(11);rs=np.random.RandomState(5)

# ------------------------------------------------------------------ atlas = floresta + casas da cidade
fa=json.load(open(f'{A}/atlas.json'));fim=Image.open(f'{A}/atlas.png').convert('RGBA')
ta=json.load(open(f'{A}/town_atlas.json'));tim=Image.open(f'{A}/town_atlas.png').convert('RGBA')
houses=['b_mes','b_lei','b_mer','b_alq','b_fer','b_cof']
strip_h=max(ta[k][3] for k in houses);ww=max(fim.width,sum(ta[k][2]+4 for k in houses))
atl=Image.new('RGBA',(ww,fim.height+strip_h+4),(0,0,0,0));atl.alpha_composite(fim,(0,0))
aj=dict(fa);x=0
for k in houses:
    sx,sy,sw,sh,ax,ay=ta[k];atl.alpha_composite(tim.crop((sx,sy,sx+sw,sy+sh)),(x,fim.height+2));aj[k]=[x,fim.height+2,sw,sh,ax,ay];x+=sw+4
atl.save(f'{A}/atlas_regiao1.png',optimize=True);json.dump(aj,open(f'{A}/atlas_regiao1.json','w'),separators=(',',':'))

# ------------------------------------------------------------------ ruído suave
def smooth(seed,step,w=gw,h=gh):
    g=np.random.RandomState(seed).rand(h//step+3,w//step+3)
    return np.array(Image.fromarray((g*255).astype('uint8')).resize((w,h),Image.BICUBIC),dtype=float)/255
def fbm(seed,steps=(80,40,20),amps=(.6,.3,.1)):
    return sum(a*smooth(seed+i,s) for i,(s,a) in enumerate(zip(steps,amps)))
yy,xx=np.mgrid[0:gh,0:gw];wx=xx*GS+GS/2;wy=yy*GS+GS/2           # coordenadas do mundo de cada pixel do chão
N1=fbm(3);N2=fbm(8,(60,30,12),(.5,.35,.15));N3=fbm(14,(120,60,30),(.55,.3,.15))

# ------------------------------------------------------------------ geografia
VILLAS=[('Vila do Portão',2500,4350),('Aldeia do Bosque',1050,3000),('Vila do Lago',3900,3750),('Posto da Colina',2500,1250)]
START=(2500,4800)
LAKE=(3600,2450,640,470)
ROADS=[[START,(2500,4350),(2500,3900),(3000,3800),(3900,3750)],
       [(2500,4350),(1900,3900),(1500,3450),(1050,3000)],
       [(1050,3000),(1300,2400),(1900,1900),(2500,1250)],
       [(2500,3900),(2600,3000),(2500,2000),(2500,1250)],
       [(3900,3750),(4300,3300),(4400,2800)]]
RIVER=[(4200,2700),(4500,2800),(4750,2760),(5000,2900)]
def seg_d(px,py,a,b):
    ax,ay=a;bx,by=b;dx,dy=bx-ax,by-ay;L=dx*dx+dy*dy or 1;t=np.clip(((px-ax)*dx+(py-ay)*dy)/L,0,1);return np.hypot(px-(ax+t*dx),py-(ay+t*dy))
def path_d(px,py,pts):
    d=np.full(px.shape,1e9)
    for a,b in zip(pts,pts[1:]):d=np.minimum(d,seg_d(px,py,a,b))
    return d
# estradas ondulam um pouco (deslocamento do ponto de consulta)
qx=wx+(N2-.5)*90;qy=wy+(N1-.5)*90
road_d=np.full(wx.shape,1e9)
for r in ROADS:road_d=np.minimum(road_d,path_d(qx,qy,r))
river_d=path_d(wx+(N2-.5)*140,wy+(N3-.5)*140,RIVER)
lk=((wx-LAKE[0]+(N2-.5)*260)/LAKE[2])**2+((wy-LAKE[1]+(N1-.5)*260)/LAKE[3])**2
pond=((wx-1250)/190)**2+((wy-4150)/130)**2+(N3-.5)*.5
water=(lk<1)|(river_d<34)|(pond<1)
shore=((lk<1.35)|(river_d<62)|(pond<1.6))&~water
vil_d=np.full(wx.shape,1e9)
for _,vx,vy in VILLAS:vil_d=np.minimum(vil_d,np.hypot(wx-vx,wy-vy))
start_d=np.hypot(wx-START[0],wy-START[1])
# colinas ao norte (pedra) e manchas de terra
hill=np.clip((1750-wy)/750+(N3-.5)*1.3,0,1)
stone=(hill>.6)&(N2>.4)&~water
dirt=((road_d<30)|(N2>.74)&(wy>1500)|(vil_d<150)|(hill>.32)&(N1>.5)|shore)&~water&~stone
# ------------------------------------------------------------------ imagem do chão (cores que as máscaras do renderizador reconhecem)
GR=np.array([74,138,58]);GR2=np.array([66,124,52]);DR=np.array([136,98,62]);ST=np.array([150,152,150]);WT=np.array([58,116,214]);SH=np.array([196,176,120])
img=np.zeros((gh,gw,3));t=smooth(31,8)
img[:]=GR[None,None,:]*(1-t[...,None])+GR2[None,None,:]*t[...,None]
img[dirt]=DR;img[shore]=SH;img[stone]=ST;img[water]=WT
Image.fromarray(img.astype('uint8')).save(f'{A}/zone_regiao1_ground.png',optimize=True)

# ------------------------------------------------------------------ props
TALL_B=['c0786ec629','bfef3c867f','451b53119f','d32da83612','8b358748b3','dee96fd12c']   # árvores de copa larga
TALL_C=['6f5e5b765c','615799f946','a012171cf1','5a100d7474']                                   # coníferas
BUSH=['5e132ed62f','87f51eb8a1','5369c15f09','1055f1c689']
ROCK=['d876089903','244580aa96','ca1d87b329','8f3ce74d92','ce03221eb2','498aebd592','545a9bb762']
FLATS=[k for k,v in fa.items() if v[2]<=16 and v[3]<=19 and k not in('fi0','fi1','fi2','fi3','bf0','bf1','bf2','bf3')]
def gi(x,y):return min(gh-1,max(0,int(y)//GS)),min(gw-1,max(0,int(x)//GS))
def at(m,x,y):i,j=gi(x,y);return m[i,j]
P=[];used=[]
def free(x,y,r):
    return all((x-a)**2+(y-b)**2>=(r+c)**2 for a,b,c in used[-400:])
def place_grid(step,fn,jit=.45):
    n=0
    for gy in range(40,H-40,step):
        for gx in range(40,W-40,step):
            x=gx+rr.uniform(-1,1)*step*jit;y=gy+rr.uniform(-1,1)*step*jit
            if 40<x<W-40 and 40<y<H-40:n+=fn(x,y) or 0
    return n
def near_road(x,y,m=44):return at(road_d,x,y)<m
def blocked(x,y):return at(water,x,y) or at(shore,x,y) and rr.random()<.7 or near_road(x,y) or at(vil_d,x,y)<340 or at(start_d,x,y)<230
def forest_dens(x,y):
    f=(1-min(1,x/2300))*.85+.05                       # mais denso a oeste
    f+=max(0,at(N3,x,y)-.5)*1.1
    f*= .35+at(N1,x,y)*1.0
    return f*(0 if at(stone,x,y) else 1)
def tree(x,y):
    if blocked(x,y):return 0
    d=forest_dens(x,y)
    h=at(hill,x,y)
    if h>.2:                                            # colinas: poucas coníferas
        if rr.random()>.16*h:return 0
        ids=TALL_C
    else:
        if rr.random()>min(.92,d):return 0
        ids=TALL_C if (rr.random()<.5 and x<2600) else TALL_B
    P.append(dict(t='p',id=rr.choice(ids),x=round(x),y=round(y)));used.append((x,y,22));return 1
def mid(x,y):
    if blocked(x,y):return 0
    h=at(hill,x,y);d=forest_dens(x,y)
    r=rr.random()
    if h>.25:
        if r<.5:P.append(dict(t='p',id=rr.choice(ROCK),x=round(x),y=round(y)));return 1
        return 0
    if r<.18+d*.12:P.append(dict(t='p',id=rr.choice(BUSH),x=round(x),y=round(y)));return 1
    if r<.23+d*.12:P.append(dict(t='p',id=rr.choice(ROCK[:4]),x=round(x),y=round(y)));return 1
    return 0
def flat(x,y):
    if at(water,x,y) or at(stone,x,y):return 0
    if rr.random()>(.55 if forest_dens(x,y)<.4 else .28):return 0
    P.append(dict(t='flat',id=rr.choice(FLATS),x=round(x),y=round(y)));return 1
# vilas: casas em volta, fogueira no centro e caixotes
HC=[[-78,-6,30],[0,-6,30],[78,-6,30]]
FIRES=[]
for nm,vx,vy in VILLAS:
    ang0=rr.uniform(0,6.28);n=3 if nm!='Posto da Colina' else 2
    for i in range(n):
        a=ang0+i*6.283/n;hx=vx+math.cos(a)*250;hy=vy+math.sin(a)*190+30
        P.append(dict(t='p',id=houses[(i+VILLAS.index((nm,vx,vy)))%len(houses)],x=round(hx),y=round(hy),col=HC));used.append((hx,hy,120))
    P.append(dict(t='fire',x=vx,y=vy));used.append((vx,vy,40))
place_grid(54,tree)
place_grid(70,mid)
place_grid(26,flat,.5)
P.sort(key=lambda p:p['y'])
Z=dict(w=W,h=H,props=P,spawns=[],plaza=[0,0,1,1],pond=[0,0,1,1],road=[],start=[START[0],START[1]-60],boss=[2500,1100],gate=[START[0],START[1]+40],
       region=dict(nome='Planície de Brumavale',gs=1/GS,vilas=[dict(nome=n,x=x,y=y) for n,x,y in VILLAS]),
       fx=[dict(k='fire',x=x,y=y) for _,x,y in VILLAS] if False else [])
json.dump(Z,open(f'{A}/zone_regiao1.json','w'),separators=(',',':'))
print('props',len(P),'trees',sum(1 for p in P if p.get('id') in TALL_B+TALL_C),'ground',(gw,gh))
