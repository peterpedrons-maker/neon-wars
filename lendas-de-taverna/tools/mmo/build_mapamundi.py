# Mapa-múndi de fantasia da Região 1, a partir da geometria REAL das zonas (tamanho, lados, saídas, água, estradas, props).
# -> mmo/assets/mapa_regiao1.png, mapa_regiao1_ids.png, mapa_regiao1_layout.json   (use /usr/bin/python3)
import numpy as np, random, math, json, os
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy.ndimage import gaussian_filter, zoom, binary_fill_holes, binary_closing, distance_transform_edt
from skimage import measure
from skimage.morphology import skeletonize
A='mmo/assets/'
src=open('tools/mmo/build_mundo.py').read(); ns={}
exec(src[src.index('SIZE=dict'):src.index('def _arrive')],ns); SIZE,LINKS=ns['SIZE'],ns['LINKS']
exec(src[src.index('BIOME=dict'):src.index('def auto_theme')],ns); BIOME=ns['BIOME']
exec(src[src.index('NM=dict'):src.index('OPP=')],ns)
OPP={0:1,1:0,2:3,3:2}
KEYS=['town','estrada','planicie','ponte','colinas','desfiladeiro','passo','goblins','lenhadores','ogros','brejo','brumas','cemiterio','mortos','lago','clareira','eremita','cabana','gruta','mina']
KEYS+=[k for k in SIZE if k not in KEYS]+['cidade2']   # zonas novas do build_mundo.py entram aqui sozinhas (ligadas por LINKS)
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
for i,k in enumerate(KEYS): col[ID==i]=TINT[INT.get(k) or {'forest':'forest','dark':'dark','mount':'mount','grave':'grave','swamp':'swamp'}.get(BIOME.get(k),'plain')]
col=np.stack([gaussian_filter(col[...,c],13) for c in range(3)],-1)
lm=gaussian_filter(land.astype(np.float32),2)[...,None]
img=par*(1-.55*lm)+col*.55*lm
dsea=np.clip(distance_transform_edt(~land)/230,0,1)[...,None]
seac=np.array((142,196,196),np.float32)*(1-dsea)+np.array((70,124,156),np.float32)*dsea     # turquesa raso -> azul fundo
seac=seac*(0.94+0.12*noise(30,21)[...,None])
img=img*lm+(par*.34+seac*.66)*(1-lm)
edge=gaussian_filter(land.astype(np.float32),8); img*=(1-0.25*np.clip(edge*(1-edge)*4,0,1))[...,None]
base=Image.fromarray(np.clip(img,0,255).astype(np.uint8)).resize((W*S,H*S),Image.BICUBIC); d=ImageDraw.Draw(base,'RGBA')
INK=(52,34,18,255)
def P(x,y): return (x*S,y*S)
for c in measure.find_contours(gaussian_filter(land.astype(np.float32),1.5),.5):
    pts=[(p[1]*S,p[0]*S) for p in c[::3]]
    if len(pts)>5: d.line(pts,fill=INK,width=3)
dist_c=distance_transform_edt(~land)
dist_s=gaussian_filter(dist_c,2.5)
for lv,al in((9,150),(20,110),(34,75),(52,45)):
    for c in measure.find_contours(dist_s,lv):
        if len(c)<40: continue
        pts=[(p[1]*S+math.sin(i*.35)*2.2,p[0]*S+math.cos(i*.31)*2.2) for i,p in enumerate(c[::3])]
        d.line(pts,fill=(96,118,126,al),width=2,joint='curve')
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
def solid(pts,fill=(70,40,20,95),wd=3):
    d.line(pts,fill=fill,width=wd,joint='curve')
for i,k in enumerate(KEYS):
    m=gaussian_filter(((ID==i)&land).astype(np.float32),3)
    for c in measure.find_contours(m,.5):
        if len(c)>=30: solid([(p[1]*S,p[0]*S) for p in c[::2]])
# --- ícones ---
def tree(x,y,k=1,dark=False):
    g=(40,92,52) if not dark else (28,66,54); gl=(86,150,84) if not dark else (58,108,84); s_=5.5*k
    d.rectangle([P(x-1,y)[0],P(x-1,y)[1],P(x+1,y+3*k)[0],P(x+1,y+3*k)[1]],fill=(86,56,30,255))
    for j,(w_,y0,y1) in enumerate(((1.25,y-s_*.3,y-s_*0),(1.0,y-s_*1.1,y-s_*.45),(.7,y-s_*2.2,y-s_*1.2))):
        d.polygon([P(x,y1-s_*1.15*(1 if j==2 else .9)),P(x-s_*w_,y0+s_*.9),P(x+s_*w_,y0+s_*.9)],fill=g+(255,),outline=INK)
        d.polygon([P(x,y1-s_*1.15*(1 if j==2 else .9)),P(x-s_*w_,y0+s_*.9),P(x-s_*w_*.1,y0+s_*.9)],fill=gl+(255,))
def dead(x,y):
    d.line([P(x,y),P(x,y-10)],fill=INK,width=2); d.line([P(x,y-6),P(x-4,y-11)],fill=INK,width=2); d.line([P(x,y-8),P(x+4,y-12)],fill=INK,width=2)
def mount(x,y,k=1):
    s_=13*k; top=(x+s_*.08,y-s_*1.6)
    d.polygon([P(x-s_,y),P(*top),P(x+s_,y)],fill=(176,166,146,255)); d.polygon([P(*top),P(x+s_,y),P(x+s_*.12,y)],fill=(112,100,90,255))
    d.polygon([P(*top),P(x-s_*.32,y-s_*1.02),P(x-s_*.08,y-s_*1.18),P(x+s_*.1,y-s_*1.0),P(x+s_*.3,y-s_*1.1)],fill=(246,244,238,255))
    for j in range(3): d.line([P(x+s_*(.2+.2*j),y-s_*(.35+.2*j)),P(x+s_*(.5+.15*j),y-s_*.05)],fill=(70,56,46,170),width=1)
    d.line([P(x-s_,y),P(*top),P(x+s_,y)],fill=INK,width=2)
def hill(x,y,k=1):
    s_=10*k; d.chord([P(x-s_,y-s_*.8),P(x+s_,y+s_*.8)],180,360,fill=(188,176,120,255),outline=INK)
def reed(x,y):
    for dx in(-3,0,3): d.line([P(x+dx,y),P(x+dx*1.4,y-8)],fill=(80,100,40,255),width=2)
def grave(x,y):
    d.rectangle([P(x-3,y-8)[0],P(x-3,y-8)[1],P(x+3,y)[0],P(x+3,y)[1]],fill=(150,148,150,255),outline=INK)
def rock(x,y): d.ellipse([P(x-3,y-3)[0],P(x-3,y-3)[1],P(x+3,y+1)[0],P(x+3,y+1)[1]],fill=(150,144,134,255),outline=INK)
def tent(x,y): d.polygon([P(x-7,y),P(x,y-10),P(x+7,y)],fill=(196,150,84,255),outline=INK)
def column(x,y): d.rectangle([P(x-2,y-10)[0],P(x-2,y-10)[1],P(x+2,y)[0],P(x+2,y)[1]],fill=(214,208,196,255),outline=INK)
def house(x,y,k=1):
    s_=7*k; d.rectangle([P(x-s_,y-s_*.8)[0],P(x-s_,y-s_*.8)[1],P(x+s_,y)[0],P(x+s_,y)[1]],fill=(232,214,170,255),outline=INK); d.polygon([P(x-s_*1.2,y-s_*.8),P(x,y-s_*1.8),P(x+s_*1.2,y-s_*.8)],fill=(168,68,44,255),outline=INK)
occ=np.zeros((H//15+2,W//15+2),bool)
def put(fn,x,y,*a,sp=1):
    if not(0<=x<W and 0<=y<H) or not land[int(y),int(x)] or water[int(y),int(x)]: return False
    gx,gy=int(x)//15,int(y)//15
    if sp and occ[gy,gx]: return False
    occ[gy,gx]=True; fn(x,y,*a); return True
items=[]
Fl=np.zeros((H,W),np.float32); Fd=np.zeros((H,W),np.float32); Mt=np.zeros((H,W),np.float32); Gv=np.zeros((H,W),np.float32); Sw=np.zeros((H,W),np.float32)
def acc(arr,X,Y,w=1.0):
    if 0<=X<W and 0<=Y<H: arr[int(Y),int(X)]+=w
for i,k in enumerate(KEYS):
    if k not in Zj: continue
    j=Zj[k]; rx,ry,rw,rh=rect[k]; ZW,ZH=j['w'],j['h']; inter=INT.get(k) or 'forest'
    ex=[(e['side'],(e['x']+e['w']/2 if e['side']<2 else e['y']+e['h']/2)) for e in j.get('exits',[]) if e.get('side',-1)>=0]
    side_th=[BIOME.get(k,'forest')]*4
    for e in j.get('exits',[]):
        if e['id'] in BIOME: side_th[e['side']]=BIOME[e['id']]
    zm=(ID==i)
    for p_ in j['props']:
        X=rx+p_['x']/ZW*rw; Y=ry+p_['y']/ZH*rh; t,kk=p_.get('t'),p_.get('k')
        if not(0<=X<W and 0<=Y<H) or not zm[int(Y),int(X)]: continue
        if t=='p': acc(Fd if inter=='dark' else (Sw if inter=='swamp' else (Gv if inter=='grave' else (Mt if inter=='mount' else Fl))),X,Y)
        elif kk=='mount': acc(Mt,X,Y,3)
        elif kk=='tombstone': acc(Gv,X,Y)
        elif kk=='tent': items.append((Y,tent,(X,Y)))
        elif kk=='column' and R.random()<.12: items.append((Y,column,(X,Y)))
        elif kk=='rock' and R.random()<.05: items.append((Y,rock,(X,Y)))
    if inter=='mount': Mt[zm]+=.03
    # relevo de borda = o que existe do outro lado de cada lado
    for sd in range(4):
        th=side_th[sd]; tgt={'forest':Fl,'dark':Fd,'mount':Mt,'grave':Gv,'swamp':Sw}.get(th)
        if tgt is None: continue
        dep=max(7,int(.13*(rw if sd>=2 else rh)))
        strip=np.zeros((H,W),bool)
        X0,Y0,X1,Y1=int(rx),int(ry),int(rx+rw),int(ry+rh)
        if sd==0: strip[Y0:Y0+dep,X0:X1]=True
        if sd==1: strip[Y1-dep:Y1,X0:X1]=True
        if sd==2: strip[Y0:Y1,X0:X0+dep]=True
        if sd==3: strip[Y0:Y1,X1-dep:X1]=True
        strip&=zm
        for s_,pp in ex:   # vão das passagens
            c=(pp/(SZ[k][0] if s_<2 else SZ[k][1]))*(rw if s_<2 else rh)
            if s_!=sd: continue
            if sd<2: strip[:,int(rx+c-14):int(rx+c+14)]=False
            else: strip[int(ry+c-14):int(ry+c+14),:]=False
        tgt[strip]+=.09
    for m_ in j.get('marks',[]):
        if m_['k']=='camp': items.append((ry+m_['y']/ZH*rh,tent,(rx+m_['x']/ZW*rw,ry+m_['y']/ZH*rh)))
i_col=KEYS.index('colinas'); rx,ry,rw,rh=rect['colinas']
for _ in range(60):
    X,Y=rx+R.random()*rw,ry+R.random()*rh
    if 0<=X<W and 0<=Y<H and ID[int(Y),int(X)]==i_col: items.append((Y,hill,(X,Y,R.uniform(.9,1.3))))
def stylize(acc_,thr,wash,line,icon,edge_gap,inner_p,sig=6):
    dn=gaussian_filter(acc_,sig); pos_=dn[dn>1e-4]; thr=max(thr,float(np.percentile(pos_,58))) if pos_.size else thr; m=(dn>thr)&land&~water; m=gaussian_filter(m.astype(np.float32),3)>.5
    if not m.any(): return
    mk=np.array(Image.fromarray((m*255).astype(np.uint8)).resize((W*S,H*S),Image.BICUBIC).filter(ImageFilter.GaussianBlur(2)))
    base.paste(Image.new('RGBA',base.size,wash),(0,0),Image.fromarray((mk>128).astype(np.uint8)*110))
    dd=ImageDraw.Draw(base,'RGBA')
    for c in measure.find_contours(gaussian_filter(m.astype(np.float32),1.5),.5):
        if len(c)<20: continue
        dd.line([(p[1]*S,p[0]*S) for p in c[::3]],fill=line,width=3)
        L=0;prev=c[0]
        for p in c[::2]:
            L+=math.hypot(p[0]-prev[0],p[1]-prev[1]);prev=p
            if L>=edge_gap:
                L=0; items.append((p[0],icon,(p[1]+R.uniform(-2,2),p[0]+R.uniform(-1,3))))
    ys_,xs_=np.nonzero(m)
    for j in R.sample(range(len(xs_)),min(len(xs_),int(len(xs_)/float(inner_p**2)))): items.append((ys_[j],icon,(xs_[j]+R.uniform(-2,2),ys_[j])))
dk=(0,0,0)
def f_light(x,y,k=1): tree(x,y,R.uniform(.9,1.15),False)
def f_dark(x,y,k=1): tree(x,y,R.uniform(.9,1.15),True)
def mt(x,y,k=1): mount(x,y,R.uniform(1.0,1.5))
def sw(x,y,k=1): reed(x,y) if R.random()<.6 else dead(x,y)
def gv(x,y,k=1): grave(x,y) if R.random()<.7 else dead(x,y)
stylize(Fl,.04,(70,130,70,255),(40,84,44,200),f_light,22,34)
stylize(Fd,.04,(30,86,64,255),(24,60,44,210),f_dark,22,34)
stylize(Mt,.035,(150,138,122,255),(70,56,44,200),mt,24,38)
stylize(Gv,.025,(130,110,140,255),(70,50,80,190),gv,22,30)
stylize(Sw,.03,(110,130,60,255),(70,84,36,190),sw,22,34)
items.sort(key=lambda t:t[0])
d=ImageDraw.Draw(base,'RGBA')
for _,fn,a in items: put(fn,*a)
# cidades
for k,n,sc in(('town',9,1.3),('cidade2',6,1.15)):
    rx,ry,rw,rh=rect[k]
    for jx in range(n): house(rx+rw*.15+jx*(rw*.7/n)+R.randint(-3,3),ry+rh*.5+R.randint(-10,10),sc)
# estradas reais (esqueleto do chão) + ligações entre zonas
# (estradas internas: malha limpa passagem -> centro da zona, desenhada abaixo)
def seg(p,q_,col,wd):
    L=math.hypot(q_[0]-p[0],q_[1]-p[1]); n=max(2,int(L/3.5))
    for t in range(n+1):
        u=t/n; x=p[0]+(q_[0]-p[0])*u; y=p[1]+(q_[1]-p[1])*u
        if t%2==0: d.ellipse([x*S-wd,y*S-wd,x*S+wd,y*S+wd],fill=col)
def bez(p0,p1,p2,n=40):
    return [((1-t)**2*p0[0]+2*(1-t)*t*p1[0]+t*t*p2[0],(1-t)**2*p0[1]+2*(1-t)*t*p1[1]+t*t*p2[1]) for t in np.linspace(0,1,n)]
def ex_pt(k,sd,pos_):
    rx,ry,rw,rh=rect[k]; ZW,ZH=SZ[k]
    return {0:(rx+pos_/ZW*rw,ry),1:(rx+pos_/ZW*rw,ry+rh),2:(rx,ry+pos_/ZH*rh),3:(rx+rw,ry+pos_/ZH*rh)}[sd]
def pull(k,pt):
    i=KEYS.index(k); rx,ry,rw,rh=rect[k]; hub=(rx+rw/2,ry+rh/2)
    for t in np.linspace(0,1,60):
        x=pt[0]+(hub[0]-pt[0])*t; y=pt[1]+(hub[1]-pt[1])*t
        if 0<=x<W and 0<=y<H and land[int(y),int(x)] and ID[int(y),int(x)]==i and not water[int(y),int(x)]: return (x,y)
    return hub
def hubpt(k):
    rx,ry,rw,rh=rect[k]; return pull(k,(rx+rw/2,ry+rh/2))
def road(pts,w=4): d.line([(x*S,y*S) for x,y in pts],fill=(104,62,34,235),width=w,joint='curve')
EXITS={}
for a_,sa,pa,b_,pb in LINKS:
    EXITS.setdefault(a_,[]).append((sa,pa)); EXITS.setdefault(b_,[]).append((OPP[sa],pb))
for k,exl in EXITS.items():
    H_=hubpt(k)
    for sd,pp in exl:
        E=pull(k,ex_pt(k,sd,pp)); mid=((E[0]+H_[0])/2+(H_[1]-E[1])*.08,(E[1]+H_[1])/2-(H_[0]-E[0])*.08)
        road(bez(E,mid,H_,30))
for a_,sa,pa,b_,pb in LINKS:
    A_=ex_pt(a_,sa,pa); B_=ex_pt(b_,OPP[sa],pb); mid=((A_[0]+B_[0])/2,(A_[1]+B_[1])/2)
    if math.hypot(A_[0]-B_[0],A_[1]-B_[1])>45: continue   # ligação em ciclo (zonas não coladas): sem estrada reta atravessando o mapa
    A2,B2=pull(a_,A_),pull(b_,B_); road(bez(A2,((A2[0]+B2[0])/2,(A2[1]+B2[1])/2),B2,24))
# ligações de cidade
t_,e_,pa_,c2_=rect['town'],rect['estrada'],rect['passo'],rect['cidade2']
for A_,B_ in (((t_[0]+t_[2]*.45,t_[1]),(e_[0]+e_[2]*.45,e_[1]+e_[3])),((pa_[0]+pa_[2]*.5,pa_[1]),(c2_[0]+c2_[2]*.5,c2_[1]+c2_[3]))):
    if math.hypot(A_[0]-B_[0],A_[1]-B_[1])<90:
        pts=bez(A_,((A_[0]+B_[0])/2+6,(A_[1]+B_[1])/2),B_); d.line([(x*S,y*S) for x,y in pts],fill=(104,62,34,235),width=4,joint='curve')
# navios no mar
def ship(x,y,k=1):
    d.polygon([P(x-9*k,y),P(x+9*k,y),P(x+6*k,y+5*k),P(x-6*k,y+5*k)],fill=(120,80,44,255),outline=INK)
    d.line([P(x,y),P(x,y-16*k)],fill=INK,width=2)
    d.polygon([P(x,y-15*k),P(x+9*k,y-4*k),P(x,y-4*k)],fill=(240,228,196,255),outline=INK); d.polygon([P(x,y-13*k),P(x-7*k,y-4*k),P(x,y-4*k)],fill=(232,218,182,255),outline=INK)
n_=0
for _ in range(400):
    x,y=R.randint(60,W-60),R.randint(60,H-60)
    if not land[y,x] and 45<dist_c[y,x]<110 and n_<5: ship(x,y,R.uniform(.9,1.2)); n_+=1
# monstro marinho
def serpent(x,y,k=1):
    col=(54,110,96,255); hl=(96,160,132,255)
    for i in range(3):
        cx_=x+i*26*k; r=11*k
        d.chord([P(cx_-r,y-r)[0],P(cx_-r,y-r)[1],P(cx_+r,y+r)[0],P(cx_+r,y+r)[1]],180,360,fill=col,outline=INK)
        d.arc([P(cx_-r*.6,y-r*.7)[0],P(cx_-r*.6,y-r*.7)[1],P(cx_+r*.6,y+r*.7)[0],P(cx_+r*.6,y+r*.7)[1]],200,340,fill=hl,width=2)
        d.line([P(cx_-r-3*k,y+2),P(cx_+r+3*k,y+2)],fill=(220,238,240,200),width=2)
    hx,hy=x-14*k,y-12*k
    d.ellipse([P(hx-8*k,hy-7*k)[0],P(hx-8*k,hy-7*k)[1],P(hx+8*k,hy+5*k)[0],P(hx+8*k,hy+5*k)[1]],fill=col,outline=INK)
    d.ellipse([P(hx-4*k,hy-3*k)[0],P(hx-4*k,hy-3*k)[1],P(hx-1*k,hy)[0],P(hx-1*k,hy)[1]],fill=(250,230,120,255),outline=INK)
    d.polygon([P(hx-8*k,hy-6*k),P(hx-12*k,hy-12*k),P(hx-5*k,hy-8*k)],fill=hl,outline=INK)
for _ in range(600):
    x,y=R.randint(120,W-160),R.randint(900,H-120)
    if not land[y,x] and dist_c[y,x]>120 and not land[max(0,y-40):y+40,max(0,x-40):x+110].any(): serpent(x,y,1.7); break
# redemoinho
def whirl(x,y):
    for i in range(14):
        a0=i*.55; r=4+i*2.6; d.arc([P(x-r,y-r*.55)[0],P(x-r,y-r*.55)[1],P(x+r,y+r*.55)[0],P(x+r,y+r*.55)[1]],math.degrees(a0),math.degrees(a0)+250,fill=(40,80,108,200),width=2)
for _ in range(300):
    x,y=R.randint(700,W-120),R.randint(250,800)
    if not land[y,x] and dist_c[y,x]>90: whirl(x,y); break
# nomes do mar (letras espaçadas, levemente inclinadas)
try:
    fm=ImageFont.truetype('mmo/assets/fonts/Almendra-Bold.ttf',26*S)
    def sea_name(txt,cx,cy,ang,col=(44,84,112,185)):
        sp=5*S; wd=sum(d.textlength(c,font=fm)+sp for c in txt); lay=Image.new('RGBA',(int(wd)+40,70*S),(0,0,0,0)); ld=ImageDraw.Draw(lay); xx=20
        for c in txt: ld.text((xx,35*S),c,font=fm,fill=col,anchor='lm'); xx+=ld.textlength(c,font=fm)+sp
        lay=lay.rotate(ang,expand=True,resample=Image.BICUBIC); base.paste(lay,(int(cx*S-lay.width/2),int(cy*S-lay.height/2)),lay)
    sea_name('MAR DAS BRUMAS',930,1010,-9); sea_name('GOLFO DO ALVORECER',880,1700,7)
except Exception as e: print('mar',e)
d=ImageDraw.Draw(base,'RGBA')
# moldura e bússola
fr=Image.new('RGBA',base.size,(0,0,0,0)); fd=ImageDraw.Draw(fr)
for t,wd in((6,4),(16,2),(20,1)): fd.rectangle([t,t,W*S-t,H*S-t],outline=INK,width=wd)
base=Image.alpha_composite(base.convert('RGBA'),fr); d=ImageDraw.Draw(base,'RGBA')
cx,cy=W-100,112
for rr,wd in((78,3),(70,1),(52,1)): d.ellipse([P(cx-rr,cy-rr)[0],P(cx-rr,cy-rr)[1],P(cx+rr,cy+rr)[0],P(cx+rr,cy+rr)[1]],outline=INK,width=wd)
for a_ in range(0,360,15):
    r=math.radians(a_); d.line([P(cx+math.cos(r)*70,cy+math.sin(r)*70),P(cx+math.cos(r)*(78 if a_%45==0 else 74),cy+math.sin(r)*(78 if a_%45==0 else 74))],fill=INK,width=2)
for a_,l,c in((-90,60,(160,42,30,255)),(0,60,(236,220,176,255)),(90,60,(236,220,176,255)),(180,60,(236,220,176,255)),(-45,38,(200,170,110,255)),(45,38,(200,170,110,255)),(135,38,(200,170,110,255)),(225,38,(200,170,110,255))):
    r=math.radians(a_); w_=9 if l>50 else 6
    p1=(cx+math.cos(r)*l,cy+math.sin(r)*l); pa=(cx+math.cos(r+1.57)*w_,cy+math.sin(r+1.57)*w_); pb=(cx+math.cos(r-1.57)*w_,cy+math.sin(r-1.57)*w_)
    d.polygon([P(*p1),P(*pa),P(cx,cy),P(*pb)],fill=c,outline=INK)
d.ellipse([P(cx-5,cy-5)[0],P(cx-5,cy-5)[1],P(cx+5,cy+5)[0],P(cx+5,cy+5)[1]],fill=INK)
from PIL import ImageFont
try:
    ft=ImageFont.truetype('mmo/assets/fonts/Almendra-Bold.ttf',30*S); fs_=ImageFont.truetype('mmo/assets/fonts/Almendra-Regular.ttf',15*S)
    bx,by=W//2,H-70
    d.rounded_rectangle([P(bx-190,by-34)[0],P(bx-190,by-34)[1],P(bx+190,by+30)[0],P(bx+190,by+30)[1]],radius=14,fill=(228,208,160,235),outline=INK,width=4)
    d.rounded_rectangle([P(bx-182,by-28)[0],P(bx-182,by-28)[1],P(bx+182,by+24)[0],P(bx+182,by+24)[1]],radius=10,outline=(120,80,40,200),width=2)
    d.text(P(bx,by-8),'Região de Brumavale',font=ft,fill=(70,36,16,255),anchor='mm'); d.text(P(bx,by+14),'Nível 1 a 12',font=fs_,fill=(120,56,30,255),anchor='mm')
except Exception as e: print('fonte',e)
out=np.array(base.convert('RGB')).astype(np.float32); hh,ww=out.shape[:2]; v=np.mgrid[0:hh,0:ww]; vx=(v[1]/ww-.5)*2; vy=(v[0]/hh-.5)*2
out*=np.clip(1-.3*(np.maximum(abs(vx),abs(vy))**4),.55,1)[...,None]
Image.fromarray(np.clip(out,0,255).astype(np.uint8)).resize((W,H),Image.LANCZOS).save(A+'mapa_regiao1.png',optimize=True)
Image.fromarray(np.where(land,ID,255).astype(np.uint8)).resize((W//2,H//2),Image.NEAREST).save(A+'mapa_regiao1_ids.png')
# centros dos rótulos = centro da região visível (centróide da máscara)
NMd=ns.get('NM') or {}
lay={'w':W,'h':H,'keys':[k if k in('town','cidade2') else 'zone_'+k for k in KEYS],'nm':{('zone_'+k):NMd.get(k,k) for k in KEYS if k not in('town','cidade2')},'c':{}}
for i,k in enumerate(KEYS):
    m=(ID==i)&land; ys2,xs2=np.nonzero(m)
    lay['c'][k]=[float(xs2.mean()),float(ys2.mean()),float(np.ptp(xs2)),float(np.ptp(ys2))] if len(xs2) else [0,0,0,0]
json.dump(lay,open(A+'mapa_regiao1_layout.json','w'))
print('ok',W,H)
