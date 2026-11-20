# Mapa-múndi de fantasia da Região 1, a partir da geometria REAL das zonas (tamanho, lados, saídas, água, estradas, props).
# -> mmo/assets/mapa_regiao1.png, mapa_regiao1_ids.png, mapa_regiao1_layout.json   (use /usr/bin/python3)
import numpy as np, random, math, json, os
from PIL import Image, ImageDraw, ImageFilter
from scipy.ndimage import gaussian_filter, zoom, binary_fill_holes, binary_closing
from skimage import measure
from skimage.morphology import skeletonize
A='mmo/assets/'
src=open('tools/mmo/build_mundo.py').read(); ns={}
exec(src[src.index('SIZE=dict'):src.index('def _arrive')],ns); SIZE,LINKS=ns['SIZE'],ns['LINKS']
exec(src[src.index('BIOME=dict'):src.index('def auto_theme')],ns); BIOME=ns['BIOME']
OPP={0:1,1:0,2:3,3:2}
KEYS=['town','estrada','planicie','ponte','colinas','desfiladeiro','passo','goblins','lenhadores','ogros','brejo','brumas','cemiterio','mortos','lago','clareira','eremita','cabana','gruta','mina','cidade2']
# --- layout em unidades do jogo (origem = canto da Planície) ---
pos={'planicie':(0,0)}; adj={}
for a,sa,pa,b,pb in LINKS:
    adj.setdefault(a,[]).append((a,sa,pa,b,pb)); adj.setdefault(b,[]).append((b,OPP[sa],pb,a,pa))
q=['planicie']
while q:
    a=q.pop(0)
    for (_,sa,pa,b,pb) in adj[a]:
        if b in pos: continue
        ax,ay=pos[a];aw,ah=SIZE[a];bw,bh=SIZE[b]
        pos[b]={0:(ax+pa-pb,ay-bh),1:(ax+pa-pb,ay+ah),2:(ax-bw,ay+pa-pb),3:(ax+aw,ay+pa-pb)}[sa]; q.append(b)
pos['estrada']=(4900,6000)            # a Estrada faz uma ferradura: desenhada ao lado, sem bater no Brejo
SZ=dict(SIZE); SZ['town']=(2600,1500); SZ['cidade2']=(3000,1800)
pos['town']=(4900+1100-1300,8700); pos['cidade2']=(pos['passo'][0]+2250-1500,pos['passo'][1]-1800)
xs=[pos[k][0] for k in KEYS]+[pos[k][0]+SZ[k][0] for k in KEYS]; ys=[pos[k][1] for k in KEYS]+[pos[k][1]+SZ[k][1] for k in KEYS]
M=600; x0,x1,y0,y1=min(xs)-M,max(xs)+M,min(ys)-M,max(ys)+M
W=1100; K=W/(x1-x0); H=int((y1-y0)*K); S=2
rect={k:((pos[k][0]-x0)*K,(pos[k][1]-y0)*K,SZ[k][0]*K,SZ[k][1]*K) for k in KEYS}
R=random.Random(7)
def noise(sc,seed,hh=None,ww=None):
    hh=hh or H; ww=ww or W; r=np.random.RandomState(seed); g=gaussian_filter(r.rand(hh//sc+3,ww//sc+3),1.2); z=zoom(g,sc,order=3)[:hh,:ww]; return (z-z.min())/(z.max()-z.min())
nA=noise(40,1)-.5; nB=noise(16,2)-.5; nC=noise(80,3)-.5
yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
wx=xx+nA*60+nB*22; wy=yy+nC*60+nB*22
Dm=np.zeros((len(KEYS),H,W),np.float32)
for i,k in enumerate(KEYS):
    rx,ry,rw,rh=rect[k]; cx,cy=rx+rw/2,ry+rh/2
    Dm[i]=((np.abs(wx-cx)/(rw/2))**3.2+(np.abs(wy-cy)/(rh/2))**3.2)**(1/3.2)
ID=Dm.argmin(0); DM=Dm.min(0)
land=DM<1.14+nB*.35
land=binary_fill_holes(binary_closing(land,iterations=14)); land=gaussian_filter(land.astype(np.float32),5)>.5
land[:12]=False;land[-12:]=False;land[:,:12]=False;land[:,-12:]=False
# --- dados reais das zonas: água e estradas (do chão), props ---
water=np.zeros((H,W),bool); road=np.zeros((H,W),bool); Zj={}
for i,k in enumerate(KEYS):
    if k in('town','cidade2'): continue
    j=json.load(open(A+'zone_%s.json'%k)); g=np.array(Image.open(A+'zone_%s_ground.png'%k).convert('RGB')).astype(int); Zj[k]=j
    rx,ry,rw,rh=rect[k]; m=(ID==i)
    u=np.clip(((xx-rx)/rw*g.shape[1]).astype(int),0,g.shape[1]-1); v=np.clip(((yy-ry)/rh*g.shape[0]).astype(int),0,g.shape[0]-1)
    px=g[v,u]; r_,g_,b_=px[...,0],px[...,1],px[...,2]
    water|=m&(b_>g_+40)&(b_>r_+60); road|=m&(r_>g_+20)&(g_>b_+25)&(r_>100)
water=gaussian_filter(water.astype(np.float32),1.2)>.4
# --- pergaminho e aquarela ---
par=np.zeros((H,W,3),np.float32); par[:]=(226,205,160); par+=(noise(6,11)[...,None]-.5)*28; par+=(noise(150,12)[...,None]-.5)*40
INT={'town':'town','estrada':'road','planicie':'plain','ponte':'river','colinas':'hills','desfiladeiro':'mount','passo':'mount','goblins':'dark','lenhadores':'forest','ogros':'forest','brejo':'swamp','brumas':'swamp','cemiterio':'grave','mortos':'grave','lago':'lake','clareira':'dark','eremita':'forest','cabana':'swamp','gruta':'mount','mina':'mount','cidade2':'town'}
TINT={'town':(214,180,120),'road':(222,196,140),'plain':(204,208,140),'river':(176,198,176),'hills':(196,182,140),'mount':(176,166,150),'dark':(120,150,110),'forest':(150,176,112),'swamp':(150,160,100),'grave':(168,150,170),'lake':(160,190,196)}
col=np.zeros((H,W,3),np.float32)
for i,k in enumerate(KEYS): col[ID==i]=TINT[INT[k]]
col=np.stack([gaussian_filter(col[...,c],5) for c in range(3)],-1)
lm=gaussian_filter(land.astype(np.float32),2)[...,None]
img=par*(1-.55*lm)+col*.55*lm
img=img*lm+(par*.8+np.array((178,190,176),np.float32)*.2)*(1-lm)
edge=gaussian_filter(land.astype(np.float32),8); img*=(1-0.25*np.clip(edge*(1-edge)*4,0,1))[...,None]
base=Image.fromarray(np.clip(img,0,255).astype(np.uint8)).resize((W*S,H*S),Image.BICUBIC); d=ImageDraw.Draw(base,'RGBA')
INK=(52,34,18,255)
def P(x,y): return (x*S,y*S)
for c in measure.find_contours(gaussian_filter(land.astype(np.float32),1.5),.5):
    pts=[(p[1]*S,p[0]*S) for p in c[::3]]
    if len(pts)>5: d.line(pts,fill=INK,width=3)
from scipy.ndimage import distance_transform_edt
dist_c=distance_transform_edt(~land)
for _ in range(2200):
    x,y=R.randint(10,W-10),R.randint(10,H-10)
    if land[y,x] or dist_c[y,x]>110: continue
    d.arc([P(x-9,y-3)[0],P(x-9,y-3)[1],P(x,y+6)[0],P(x,y+6)[1]],200,340,fill=(70,90,100,160),width=2); d.arc([P(x,y-3)[0],P(x,y-3)[1],P(x+9,y+6)[0],P(x+9,y+6)[1]],200,340,fill=(70,90,100,160),width=2)
# água real
wm=np.array(Image.fromarray((water*255).astype(np.uint8)).resize((W*S,H*S),Image.BICUBIC).filter(ImageFilter.GaussianBlur(1.5)))>128
base.paste(Image.new('RGBA',base.size,(104,150,170,255)),(0,0),Image.fromarray((wm*255).astype(np.uint8)))
d=ImageDraw.Draw(base,'RGBA')
for c in measure.find_contours(wm.astype(np.float32),.5):
    if len(c)>12: d.line([(p[1],p[0]) for p in c[::3]],fill=INK,width=3)
wy_,wx_=np.nonzero(water)
for j in R.sample(range(len(wx_)),min(len(wx_),700)): d.line([P(wx_[j]-3,wy_[j]),P(wx_[j]+3,wy_[j])],fill=(220,238,240,170),width=2)
# limites das zonas
def dashed(pts,on=16,off=9,fill=(70,40,20,215),wd=5):
    acc=0;dr=True
    for p,q_ in zip(pts,pts[1:]):
        L=math.hypot(q_[0]-p[0],q_[1]-p[1])
        if dr: d.line([p,q_],fill=fill,width=wd)
        acc+=L
        if acc>=(on if dr else off): acc=0;dr=not dr
for i,k in enumerate(KEYS):
    m=gaussian_filter(((ID==i)&land).astype(np.float32),3)
    for c in measure.find_contours(m,.5):
        if len(c)>=30: dashed([(p[1]*S,p[0]*S) for p in c[::2]])
# --- ícones ---
def tree(x,y,k=1,dark=False):
    g=(38,86,48) if not dark else (28,62,48); gl=(70,128,72) if not dark else (50,92,70); s=6*k
    d.polygon([P(x,y-s*2.3),P(x-s,y),P(x+s,y)],fill=g+(255,),outline=INK); d.polygon([P(x,y-s*2.3),P(x-s,y),P(x-s*.1,y)],fill=gl+(255,))
    d.rectangle([P(x-1,y)[0],P(x-1,y)[1],P(x+1,y+3*k)[0],P(x+1,y+3*k)[1]],fill=(80,54,30,255))
def dead(x,y):
    d.line([P(x,y),P(x,y-10)],fill=INK,width=2); d.line([P(x,y-6),P(x-4,y-11)],fill=INK,width=2); d.line([P(x,y-8),P(x+4,y-12)],fill=INK,width=2)
def mount(x,y,k=1):
    s=12*k; d.polygon([P(x-s,y),P(x,y-s*1.5),P(x+s,y)],fill=(170,160,140,255),outline=INK); d.polygon([P(x,y-s*1.5),P(x+s,y),P(x+s*.1,y)],fill=(112,100,88,255))
    d.polygon([P(x,y-s*1.5),P(x-s*.28,y-s*.95),P(x,y-s*1.05),P(x+s*.28,y-s*.95)],fill=(245,242,234,255)); d.line([P(x-s,y),P(x,y-s*1.5),P(x+s,y)],fill=INK,width=2)
def hill(x,y,k=1):
    s=10*k; d.chord([P(x-s,y-s*.8),P(x+s,y+s*.8)],180,360,fill=(188,176,120,255),outline=INK)
def reed(x,y):
    for dx in(-3,0,3): d.line([P(x+dx,y),P(x+dx*1.4,y-8)],fill=(80,100,40,255),width=2)
def grave(x,y):
    d.rectangle([P(x-3,y-8)[0],P(x-3,y-8)[1],P(x+3,y)[0],P(x+3,y)[1]],fill=(150,148,150,255),outline=INK)
def rock(x,y): d.ellipse([P(x-3,y-3)[0],P(x-3,y-3)[1],P(x+3,y+1)[0],P(x+3,y+1)[1]],fill=(150,144,134,255),outline=INK)
def tent(x,y): d.polygon([P(x-7,y),P(x,y-10),P(x+7,y)],fill=(196,150,84,255),outline=INK)
def column(x,y): d.rectangle([P(x-2,y-10)[0],P(x-2,y-10)[1],P(x+2,y)[0],P(x+2,y)[1]],fill=(214,208,196,255),outline=INK)
def house(x,y,k=1):
    s=7*k; d.rectangle([P(x-s,y-s*.8)[0],P(x-s,y-s*.8)[1],P(x+s,y)[0],P(x+s,y)[1]],fill=(232,214,170,255),outline=INK); d.polygon([P(x-s*1.2,y-s*.8),P(x,y-s*1.8),P(x+s*1.2,y-s*.8)],fill=(168,68,44,255),outline=INK)
occ=np.zeros((H//9+2,W//9+2),bool)
def put(fn,x,y,*a,sp=1):
    if not(0<=x<W and 0<=y<H) or not land[int(y),int(x)] or water[int(y),int(x)]: return False
    gx,gy=int(x)//9,int(y)//9
    if sp and occ[gy,gx]: return False
    occ[gy,gx]=True; fn(x,y,*a); return True
items=[]
def theme_icon(th,x,y,k=1):
    if th=='mount': items.append((y,mount,(x,y,R.uniform(.9,1.4))))
    elif th=='forest': items.append((y,tree,(x,y,R.uniform(.9,1.2),False)))
    elif th=='dark': items.append((y,tree,(x,y,R.uniform(.9,1.2),True)))
    elif th=='grave': items.append((y,grave if R.random()<.6 else dead,(x,y)))
    elif th=='swamp': items.append((y,reed if R.random()<.6 else dead,(x,y)))
    elif th=='hills': items.append((y,hill,(x,y,R.uniform(.9,1.3))))
    else: items.append((y,tree,(x,y,.9,False)))
for i,k in enumerate(KEYS):
    if k not in Zj: continue
    j=Zj[k]; rx,ry,rw,rh=rect[k]; ZW,ZH=j['w'],j['h']; inter=INT[k]
    ex=[(e['side'],(e['x']+e['w']/2 if e['side']<2 else e['y']+e['h']/2)) for e in j.get('exits',[]) if e.get('side',-1)>=0]
    side_th=[BIOME[k]]*4
    for e in j.get('exits',[]):
        nid=e['id']
        if nid in BIOME: side_th[e['side']]=BIOME[nid]
    for p in j['props']:
        X=rx+p['x']/ZW*rw; Y=ry+p['y']/ZH*rh; t,kk=p.get('t'),p.get('k')
        if not(0<=X<W and 0<=Y<H) or ID[int(Y),int(X)]!=i: continue
        if t=='p':
            if R.random()<(.08 if inter in('plain','road','river','lake') else .2): theme_icon('dark' if inter in('dark',) else ('forest' if inter in('plain','forest','road','river','lake','hills') else inter),X,Y)
        elif kk=='mount': items.append((Y,mount,(X,Y,R.uniform(1,1.5))))
        elif kk=='tombstone' and R.random()<.16: items.append((Y,grave,(X,Y)))
        elif kk=='dead' and R.random()<.25: items.append((Y,dead,(X,Y)))
        elif kk in('reed','mush') and R.random()<.12: items.append((Y,reed,(X,Y)))
        elif kk=='rock' and R.random()<.3: items.append((Y,rock,(X,Y)))
        elif kk=='tent': items.append((Y,tent,(X,Y)))
        elif kk=='column' and R.random()<.5: items.append((Y,column,(X,Y)))
    # cordilheiras/matas de borda conforme o que há além de cada lado
    for sd in range(4):
        th=side_th[sd]
        if th in('plain','river','road','lake'): continue
        n=int((rw if sd<2 else rh)/22)
        for t_ in range(n):
            u=R.random(); dep=R.random()**1.4*.14
            lp=(u*(rw if sd<2 else rh))
            if any(abs(lp/(rw if s_<2 else rh)*(SZ[k][0] if s_<2 else SZ[k][1])-pp)<330 for s_,pp in ex if s_==sd): continue
            X,Y={0:(rx+lp,ry+dep*rh),1:(rx+lp,ry+rh-dep*rh),2:(rx+dep*rw,ry+lp),3:(rx+rw-dep*rw,ry+lp)}[sd]
            if 0<=X<W and 0<=Y<H and ID[int(Y),int(X)]==i: theme_icon(th,X,Y)
    for m in j.get('marks',[]):
        if m['k']=='camp': items.append((ry+m['y']/ZH*rh,tent,(rx+m['x']/ZW*rw,ry+m['y']/ZH*rh)))
# colinas e planícies: colinas/tufos
for k in ('colinas',):
    i=KEYS.index(k); rx,ry,rw,rh=rect[k]
    for _ in range(90):
        X,Y=rx+R.random()*rw,ry+R.random()*rh
        if 0<=X<W and 0<=Y<H and ID[int(Y),int(X)]==i: items.append((Y,hill,(X,Y,R.uniform(.9,1.4))))
items.sort(key=lambda t:t[0])
for _,fn,a in items: put(fn,*a)
# cidades
for k,n,sc in(('town',9,1.3),('cidade2',6,1.15)):
    rx,ry,rw,rh=rect[k]
    for jx in range(n): house(rx+rw*.15+jx*(rw*.7/n)+R.randint(-3,3),ry+rh*.5+R.randint(-10,10),sc)
# estradas reais (esqueleto do chão) + ligações entre zonas
sk=skeletonize(gaussian_filter(road.astype(np.float32),1.1)>.3); ys_,xs_=np.nonzero(sk)
for x,y in zip(xs_,ys_):
    if (x+y)%3==0 and land[y,x]: d.ellipse([x*S-2.4,y*S-2.4,x*S+2.4,y*S+2.4],fill=(96,56,32,225))
def seg(p,q_,col,wd):
    L=math.hypot(q_[0]-p[0],q_[1]-p[1]); n=max(2,int(L/3.5))
    for t in range(n+1):
        u=t/n; x=p[0]+(q_[0]-p[0])*u; y=p[1]+(q_[1]-p[1])*u
        if t%2==0: d.ellipse([x*S-wd,y*S-wd,x*S+wd,y*S+wd],fill=col)
# ligações de cidade
for p,q_ in ():
    seg((p[0]+p[2]*.45,p[1]+p[3]*(0 if p is rect['town'] else 1)),(q_[0]+q_[2]*.45,q_[1]+q_[3]*(1 if p is rect['town'] else 0)),(120,40,28,235),2.6)
# moldura e bússola
fr=Image.new('RGBA',base.size,(0,0,0,0)); fd=ImageDraw.Draw(fr)
for t,wd in((6,4),(16,2),(20,1)): fd.rectangle([t,t,W*S-t,H*S-t],outline=INK,width=wd)
base=Image.alpha_composite(base.convert('RGBA'),fr); d=ImageDraw.Draw(base,'RGBA')
cx,cy=W-100,110
for a,l,c in((-90,64,(150,40,30,255)),(0,46,INK),(90,46,INK),(180,46,INK)):
    r=math.radians(a); p1=(cx+math.cos(r)*l,cy+math.sin(r)*l); pa=(cx+math.cos(r+1.57)*8,cy+math.sin(r+1.57)*8); pb=(cx+math.cos(r-1.57)*8,cy+math.sin(r-1.57)*8); d.polygon([P(*p1),P(*pa),P(cx,cy),P(*pb)],fill=c,outline=INK)
d.ellipse([P(cx-72,cy-72)[0],P(cx-72,cy-72)[1],P(cx+72,cy+72)[0],P(cx+72,cy+72)[1]],outline=INK,width=3)
out=np.array(base.convert('RGB')).astype(np.float32); hh,ww=out.shape[:2]; v=np.mgrid[0:hh,0:ww]; vx=(v[1]/ww-.5)*2; vy=(v[0]/hh-.5)*2
out*=np.clip(1-.3*(np.maximum(abs(vx),abs(vy))**4),.55,1)[...,None]
Image.fromarray(np.clip(out,0,255).astype(np.uint8)).resize((W,H),Image.LANCZOS).save(A+'mapa_regiao1.png',optimize=True)
Image.fromarray(np.where(land,ID,255).astype(np.uint8)).resize((W//2,H//2),Image.NEAREST).save(A+'mapa_regiao1_ids.png')
# centros dos rótulos = centro da região visível (centróide da máscara)
lay={'w':W,'h':H,'keys':KEYS,'c':{}}
for i,k in enumerate(KEYS):
    m=(ID==i)&land; ys2,xs2=np.nonzero(m)
    lay['c'][k]=[float(xs2.mean()),float(ys2.mean()),float(np.ptp(xs2)),float(np.ptp(ys2))] if len(xs2) else [0,0,0,0]
json.dump(lay,open(A+'mapa_regiao1_layout.json','w'))
print('ok',W,H)
