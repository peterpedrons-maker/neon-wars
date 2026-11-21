# Mapa-múndi de fantasia da Região 1, a partir da geometria REAL das zonas (tamanho, lados, saídas, água, estradas, props).
# -> mmo/assets/mapa_regiao<N>.png, mapa_regiao<N>_ids.png, mapa_regiao<N>_layout.json   (use /usr/bin/python3)
# Região 1: /usr/bin/python3 tools/mmo/build_mapamundi.py      Região 2: REG=2 /usr/bin/python3 tools/mmo/build_mapamundi.py
# REGRA: toda região nova ganha o MESMO tipo de mapa (relevo, estradas, florestas/montanhas em mancha, zonas orgânicas, nomes) — ver bloco REG==2 e docs.
import numpy as np, random, math, json, os
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy.ndimage import gaussian_filter, zoom, binary_fill_holes, binary_closing, distance_transform_edt
from skimage import measure
from skimage.morphology import skeletonize
A='mmo/assets/'
REG=int(os.environ.get('REG','1'))
src=open('tools/mmo/build_mundo.py').read(); ns={}
exec(src[src.index('SIZE=dict'):src.index('def _arrive')],ns); SIZE,LINKS=ns['SIZE'],ns['LINKS']
exec(src[src.index('R2=['):src.index('EXL={k:[]')].split('\n')[0],ns)
exec(src[src.index('BIOME=dict'):src.index('def auto_theme')],ns); BIOME=ns['BIOME']
exec(src[src.index('NM=dict'):src.index('OPP=')],ns)
OPP={0:1,1:0,2:3,3:2}; ns['OPP']=OPP
if REG==2:
    exec(src[src.index('SIZE.update(muralha'):src.index('EXL={k:[]')],ns); exec(src[src.index('LINKS2=['):src.index('for a,sa,pa,b,pb in LINKS2')],ns)
    R2=ns['R2']; SIZE={k:ns['SIZE'][k] for k in R2}; LINKS=ns['LINKS2']; BIOME={k:'mount' for k in R2}
    GR={k:json.load(open(A+'zone_%s.json'%k))['region'].get('ground','sand') for k in R2}
TOWNK=('town','cidade2') if REG==1 else ('cinzamuro',)
KEYS=['town','estrada','planicie','ponte','colinas','desfiladeiro','passo','goblins','lenhadores','ogros','brejo','brumas','cemiterio','mortos','lago','clareira','eremita','cabana','gruta','mina']
KEYS+=[k for k in SIZE if k not in KEYS]+['cidade2']
if REG==2: KEYS=['cinzamuro']+R2   # zonas novas do build_mundo.py entram aqui sozinhas (ligadas por LINKS)
# --- layout em unidades do jogo (origem = canto da Planície) ---
ROOT='planicie' if REG==1 else 'muralha'
pos={ROOT:(0,0)}; adj={}
for a,sa,pa,b,pb in LINKS:
    adj.setdefault(a,[]).append((a,sa,pa,b,pb)); adj.setdefault(b,[]).append((b,OPP[sa],pb,a,pa))
q=[ROOT]
while q:
    a=q.pop(0)
    for (_,sa,pa,b,pb) in adj[a]:
        if b in pos: continue
        ax,ay=pos[a];aw,ah=SIZE[a];bw,bh=SIZE[b]
        pos[b]={0:(ax+pa-pb,ay-bh),1:(ax+pa-pb,ay+ah),2:(ax-bw,ay+pa-pb),3:(ax+aw,ay+pa-pb)}[sa]; q.append(b)
if REG==1: pos['estrada']=(4900,6000)            # a Estrada faz uma ferradura: desenhada ao lado, sem bater no Brejo
SZ=dict(SIZE); SZ['town']=(2600,1500); SZ['cidade2']=(3000,1800); SZ['cinzamuro']=(2600,1500)
if REG==1:
    pos['town']=(4900+1100-1300,8700); pos['cidade2']=(pos['passo'][0]+2250-1500,pos['passo'][1]-1800)
else: pos['cinzamuro']=(pos['muralha'][0]+1100-1300,pos['muralha'][1]+SIZE['muralha'][1]-100)
xs=[pos[k][0] for k in KEYS]+[pos[k][0]+SZ[k][0] for k in KEYS]; ys=[pos[k][1] for k in KEYS]+[pos[k][1]+SZ[k][1] for k in KEYS]
M=600 if REG==1 else 2600; x0,x1,y0,y1=min(xs)-M,max(xs)+M,min(ys)-M,max(ys)+M
W=1100; K=W/(x1-x0); H=int((y1-y0)*K); S=2
rect={k:((pos[k][0]-x0)*K,(pos[k][1]-y0)*K,SZ[k][0]*K,SZ[k][1]*K) for k in KEYS}
R=random.Random(7)
def noise(sc,seed,hh=None,ww=None):
    hh=hh or H; ww=ww or W; r=np.random.RandomState(seed); g=gaussian_filter(r.rand(hh//sc+3,ww//sc+3),1.2); z=zoom(g,sc,order=3)[:hh,:ww]; return (z-z.min())/(z.max()-z.min())
nA=noise(40,1)-.5; nB=noise(16,2)-.5; nC=noise(80,3)-.5
yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
WARP=60 if REG==1 else 110
wx=xx+nA*WARP+nB*22; wy=yy+nC*WARP+nB*22
Dm=np.zeros((len(KEYS),H,W),np.float32)
for i,k in enumerate(KEYS):
    rx,ry,rw,rh=rect[k]; cx,cy=rx+rw/2,ry+rh/2
    if REG==1: Dm[i]=((np.abs(wx-cx)/(rw/2))**3.2+(np.abs(wy-cy)/(rh/2))**3.2)**(1/3.2)
    else:
        rr=np.random.RandomState(100+i); ang=np.arctan2(wy-cy,wx-cx); ex_=rr.uniform(2.1,2.7)
        mod=1.16+.15*np.sin(3*ang+rr.uniform(0,6.3))+.09*np.sin(5*ang+rr.uniform(0,6.3))+.06*np.sin(8*ang+rr.uniform(0,6.3))
        Dm[i]=((np.abs(wx-cx)/(rw/2))**ex_+(np.abs(wy-cy)/(rh/2))**ex_)**(1/ex_)/mod
ID=Dm.argmin(0); DM=Dm.min(0)
land=DM<1.14+nB*.35
land=binary_fill_holes(binary_closing(land,iterations=14)); land=gaussian_filter(land.astype(np.float32),5)>.5
land[:12]=False;land[-12:]=False;land[:,:12]=False;land[:,-12:]=False
# --- dados reais das zonas: água e estradas (do chão), props ---
water=np.zeros((H,W),bool); road=np.zeros((H,W),bool); Zj={}
for i,k in enumerate(KEYS):
    if k in TOWNK: continue
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
TINT.update(sand=(220,190,130),red=(196,118,84),salt=(232,228,218),ash=(120,112,120),rock=(168,166,172))
if REG==2: INT={k:GR.get(k,'sand') for k in KEYS}; INT['cinzamuro']='rock'
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
Rk=np.zeros((H,W),np.float32); Th=np.zeros((H,W),np.float32); Fl=np.zeros((H,W),np.float32); Fd=np.zeros((H,W),np.float32); Mt=np.zeros((H,W),np.float32); Gv=np.zeros((H,W),np.float32); Sw=np.zeros((H,W),np.float32)
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
        if t=='p': acc(Mt if REG==2 else Fd if inter=='dark' else (Sw if inter=='swamp' else (Gv if inter=='grave' else (Mt if inter=='mount' else Fl))),X,Y)
        elif kk=='mount': acc(Mt,X,Y,3)
        elif kk=='crag' and REG==2: acc(Rk,X,Y,.25)
        elif kk=='thorn' and REG==2: acc(Th,X,Y,.7)
        elif kk=='tombstone': acc(Gv,X,Y)
        elif kk=='tent': items.append((Y,tent,(X,Y)))
        elif kk=='column' and R.random()<.12: items.append((Y,column,(X,Y)))
        elif kk=='rock' and R.random()<.05: items.append((Y,rock,(X,Y)))
    if inter=='mount': Mt[zm]+=.03
    if REG==2 and ZW>0: pass
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
        if REG==2: strip&=(noise(22,sd+60)>.36+.1*(sd%2))
        tgt[strip]+=.09
    for m_ in j.get('marks',[]):
        if m_['k']=='camp': items.append((ry+m_['y']/ZH*rh,tent,(rx+m_['x']/ZW*rw,ry+m_['y']/ZH*rh)))
i_col=KEYS.index('colinas') if REG==1 else 0; rx,ry,rw,rh=rect['colinas' if REG==1 else KEYS[0]]
for _ in range(60 if REG==1 else 0):
    X,Y=rx+R.random()*rw,ry+R.random()*rh
    if 0<=X<W and 0<=Y<H and ID[int(Y),int(X)]==i_col: items.append((Y,hill,(X,Y,R.uniform(.9,1.3))))
# relevo com sombreado (luz de noroeste): montanhas altas, florestas e colinas levemente elevadas
Hh=gaussian_filter(Mt,9)*60+gaussian_filter(Rk,6)*5+gaussian_filter(Fl+Fd+Gv+Sw,9)*2.5+(noise(55,31)-.5)*.9+gaussian_filter(land.astype(np.float32),10)*.6
Hh=Hh*land
gy_,gx_=np.gradient(gaussian_filter(Hh,1.6))
sh_=np.clip((-gx_-gy_)*9,-1,1)                      # luz vindo do canto superior esquerdo
sh_big=np.array(Image.fromarray(((sh_+1)*127.5).astype(np.uint8)).resize((W*S,H*S),Image.BICUBIC),np.float32)/127.5-1
lm_big=np.array(Image.fromarray((gaussian_filter(land.astype(np.float32),2)*255).astype(np.uint8)).resize((W*S,H*S),Image.BICUBIC),np.float32)/255
arr=np.array(base,np.float32)*(1+.27*sh_big*lm_big)[...,None]
base.paste(Image.fromarray(np.clip(arr,0,255).astype(np.uint8)))
def stylize(acc_,thr,wash,line,icon,edge_gap,inner_p,sig=6):
    dn=gaussian_filter(acc_,sig); pos_=dn[dn>1e-4]; thr=max(thr,float(np.percentile(pos_,58))) if pos_.size else thr; m=(dn>thr)&land&~water; m=gaussian_filter(m.astype(np.float32),3)>.5
    if not m.any(): return m
    mk=np.array(Image.fromarray((m*255).astype(np.uint8)).resize((W*S,H*S),Image.BICUBIC).filter(ImageFilter.GaussianBlur(2)))
    base.paste(Image.new('RGBA',base.size,wash),(0,0),Image.fromarray((mk>128).astype(np.uint8)*110))
    dd=ImageDraw.Draw(base,'RGBA')
    for c in measure.find_contours(gaussian_filter(m.astype(np.float32),1.5),.5):
        if len(c)<20: continue
        dd.line([(p[1]*S,p[0]*S) for p in c[::3]],fill=line,width=3)
        L=0;prev=c[0]
        for p in c[::2]:
            L+=math.hypot(p[0]-prev[0],p[1]-prev[1]);prev=p
            if L>=edge_gap and icon:
                L=0; items.append((p[0],icon,(p[1]+R.uniform(-2,2),p[0]+R.uniform(-1,3))))
    ys_,xs_=np.nonzero(m)
    for j in (R.sample(range(len(xs_)),min(len(xs_),int(len(xs_)/float(inner_p**2)))) if icon else []): items.append((ys_[j],icon,(xs_[j]+R.uniform(-2,2),ys_[j])))
    return m
dk=(0,0,0)
def f_light(x,y,k=1): tree(x,y,R.uniform(.9,1.15),False)
def f_dark(x,y,k=1): tree(x,y,R.uniform(.9,1.15),True)
def mt(x,y,k=1): mount(x,y,R.uniform(1.0,1.5))
def sw(x,y,k=1): reed(x,y) if R.random()<.6 else dead(x,y)
def gv(x,y,k=1): grave(x,y) if R.random()<.7 else dead(x,y)
GRI=np.zeros((H,W),np.int32)
for i_,k_ in enumerate(KEYS): GRI[ID==i_]=['sand','red','salt','ash','rock'].index(INT.get(k_,'sand')) if INT.get(k_,'sand') in ('sand','red','salt','ash','rock') else 0
PALM={'sand':((200,170,120),(140,108,74)),'red':((190,104,74),(124,62,44)),'salt':((214,210,204),(150,146,146)),'ash':((104,100,108),(58,54,64)),'rock':((176,168,160),(112,102,96))}
def gpal(x,y): return PALM[['sand','red','salt','ash','rock'][GRI[min(H-1,max(0,int(y))),min(W-1,max(0,int(x)))]]]
def mount_c(x,y,k=1):
    c1,c2=gpal(x,y); s_=13*k; top=(x+s_*.08,y-s_*1.6)
    d.polygon([P(x-s_,y),P(*top),P(x+s_,y)],fill=c1+(255,)); d.polygon([P(*top),P(x+s_,y),P(x+s_*.12,y)],fill=c2+(255,))
    for j in range(3): d.line([P(x+s_*(.2+.2*j),y-s_*(.35+.2*j)),P(x+s_*(.5+.15*j),y-s_*.05)],fill=(60,44,36,150),width=1)
    d.line([P(x-s_,y),P(*top),P(x+s_,y)],fill=INK,width=2)
def mesa(x,y,k=1):
    c1,c2=gpal(x,y); w_=11*k; h_=11*k
    d.polygon([P(x-w_,y),P(x-w_*.8,y-h_),P(x+w_*.8,y-h_),P(x+w_,y)],fill=c1+(255,)); d.polygon([P(x+w_*.25,y-h_),P(x+w_*.8,y-h_),P(x+w_,y),P(x+w_*.25,y)],fill=c2+(255,))
    d.polygon([P(x-w_*.8,y-h_),P(x+w_*.8,y-h_),P(x+w_*.7,y-h_-3*k),P(x-w_*.7,y-h_-3*k)],fill=tuple(min(255,v+34) for v in c1)+(255,))
    for j in (.3,.55,.78): d.line([P(x-w_*(1-.2*j),y-h_*j),P(x+w_*(1-.2*j),y-h_*j)],fill=c2+(255,),width=1)
    d.line([P(x-w_,y),P(x-w_*.8,y-h_),P(x-w_*.7,y-h_-3*k),P(x+w_*.7,y-h_-3*k),P(x+w_*.8,y-h_),P(x+w_,y)],fill=INK,width=2)
def rockpile(x,y,k=1):
    c1,c2=gpal(x,y)
    for dx,dy,r_ in((-4,0,3.4),(2,.5,4.2),(7,-1,2.6)):
        d.ellipse([P(x+dx-r_,y+dy-r_*.8)[0],P(x+dx-r_,y+dy-r_*.8)[1],P(x+dx+r_,y+dy+r_*.5)[0],P(x+dx+r_,y+dy+r_*.5)[1]],fill=c1+(255,),outline=INK)
def thorn(x,y,k=1):
    for a_ in(-50,-25,0,25,50):
        r_=math.radians(a_-90); d.line([P(x,y),P(x+math.cos(r_)*7,y+math.sin(r_)*7)],fill=(88,92,40,255),width=2)
    d.ellipse([P(x-1.5,y-1.5)[0],P(x-1.5,y-1.5)[1],P(x+1.5,y+1.5)[0],P(x+1.5,y+1.5)[1]],fill=(60,52,28,255))
def dune(x,y,k=1):
    c1,c2=gpal(x,y); d.arc([P(x-11,y-5)[0],P(x-11,y-5)[1],P(x+11,y+5)[0],P(x+11,y+5)[1]],200,340,fill=tuple(int(v*.72) for v in c1)+(210,),width=2)
def keep(x,y,k=1):
    w_=12*k; d.rectangle([P(x-w_,y-w_*.9)[0],P(x-w_,y-w_*.9)[1],P(x+w_,y)[0],P(x+w_,y)[1]],fill=(150,148,156,255),outline=INK)
    for tx in(-w_,w_):
        d.rectangle([P(x+tx-4*k,y-w_*1.5)[0],P(x+tx-4*k,y-w_*1.5)[1],P(x+tx+4*k,y)[0],P(x+tx+4*k,y)[1]],fill=(120,118,128,255),outline=INK)
        d.polygon([P(x+tx-5*k,y-w_*1.5),P(x+tx,y-w_*2.1),P(x+tx+5*k,y-w_*1.5)],fill=(140,56,44,255),outline=INK)
    d.arc([P(x-4*k,y-8*k)[0],P(x-4*k,y-8*k)[1],P(x+4*k,y+0)[0],P(x+4*k,y+0)[1]],180,360,fill=INK,width=2)
if REG==1:
    stylize(Fl,.04,(70,130,70,255),(40,84,44,200),f_light,22,34)
    stylize(Fd,.04,(30,86,64,255),(24,60,44,210),f_dark,22,34)
    stylize(Mt,.035,(150,138,122,255),(70,56,44,200),mt,24,38)
    stylize(Gv,.025,(130,110,140,255),(70,50,80,190),gv,22,30)
    stylize(Sw,.03,(110,130,60,255),(70,84,36,190),sw,22,34)
else:
    d_=ImageDraw.Draw(base,'RGBA'); D2=lambda: ImageDraw.Draw(base,'RGBA')
    def mount_n(x,y,k=1):
        c1,c2=gpal(x,y); s_=13*k; tx=x+s_*R.uniform(-.2,.28); top=(tx,y-s_*R.uniform(1.3,1.9)); dd=D2()
        dd.polygon([P(x-s_,y),P(*top),P(x+s_*R.uniform(.8,1.1),y)],fill=c1+(255,)); dd.polygon([P(*top),P(x+s_,y),P(x+s_*.1,y)],fill=c2+(255,))
        for j in range(R.randint(2,4)): dd.line([P(tx+s_*(.1+.2*j),y-s_*(.5+.15*j)),P(tx+s_*(.35+.15*j),y-s_*.05)],fill=(60,44,36,140),width=1)
        dd.line([P(x-s_,y),P(*top),P(x+s_,y)],fill=INK,width=2)
    def mesa_n(x,y,k=1):
        c1,c2=gpal(x,y); w_=R.uniform(8,15)*k; h_=R.uniform(8,16)*k; dd=D2(); sl=R.uniform(.7,.9)
        dd.ellipse([P(x-w_*1.1,y-2)[0],P(x-w_*1.1,y-2)[1],P(x+w_*1.3,y+3)[0],P(x+w_*1.3,y+3)[1]],fill=(70,40,24,70))
        dd.polygon([P(x-w_,y),P(x-w_*sl,y-h_),P(x+w_*sl,y-h_),P(x+w_,y)],fill=c1+(255,)); dd.polygon([P(x+w_*.2,y-h_),P(x+w_*sl,y-h_),P(x+w_,y),P(x+w_*.2,y)],fill=c2+(255,))
        dd.polygon([P(x-w_*sl,y-h_),P(x+w_*sl,y-h_),P(x+w_*(sl-.1),y-h_-3*k),P(x-w_*(sl-.1),y-h_-3*k)],fill=tuple(min(255,v+36) for v in c1)+(255,))
        for j in (.25,.5,.75): dd.line([P(x-w_*(1-.2*j),y-h_*j),P(x+w_*(1-.2*j),y-h_*j)],fill=c2+(255,),width=1)
        dd.line([P(x-w_,y),P(x-w_*sl,y-h_),P(x-w_*(sl-.1),y-h_-3*k),P(x+w_*(sl-.1),y-h_-3*k),P(x+w_*sl,y-h_),P(x+w_,y)],fill=INK,width=2)
    def dune_n(x,y,k=1):
        c1,c2=gpal(x,y); dd=D2()
        for j in range(R.randint(2,4)):
            ox=R.uniform(-9,9); oy=R.uniform(-3,6); w_=R.uniform(7,13)
            dd.arc([P(x+ox-w_,y+oy-w_*.45)[0],P(x+ox-w_,y+oy-w_*.45)[1],P(x+ox+w_,y+oy+w_*.45)[0],P(x+ox+w_,y+oy+w_*.45)[1]],195,345,fill=tuple(int(v*.66) for v in c1)+(220,),width=2)
    def bones(x,y,k=1):
        dd=D2(); dd.ellipse([P(x-3,y-3)[0],P(x-3,y-3)[1],P(x+3,y+2)[0],P(x+3,y+2)[1]],fill=(238,232,214,255),outline=INK)
        for ex in(-1.2,1.2): dd.point(P(x+ex,y-.5),fill=INK)
        for j in range(3): dd.line([P(x-6+j*1,y+4+j*1.5),P(x+6-j*1,y+4+j*1.5)],fill=(226,220,200,255),width=1)
    def volcano(x,y,k=1):
        dd=D2(); s_=17*k
        dd.polygon([P(x-s_,y),P(x-s_*.28,y-s_*1.3),P(x+s_*.28,y-s_*1.3),P(x+s_,y)],fill=(86,78,88,255)); dd.polygon([P(x+s_*.28,y-s_*1.3),P(x+s_,y),P(x+s_*.2,y)],fill=(48,42,52,255))
        dd.ellipse([P(x-s_*.3,y-s_*1.4)[0],P(x-s_*.3,y-s_*1.4)[1],P(x+s_*.3,y-s_*1.2)[0],P(x+s_*.3,y-s_*1.2)[1]],fill=(236,110,40,255),outline=INK)
        dd.line([P(x-s_*.1,y-s_*1.2),P(x-s_*.35,y-s_*.5),P(x-s_*.2,y-s_*.1)],fill=(236,120,44,255),width=2)
        for j in range(4): dd.ellipse([P(x+j*2-2,y-s_*1.5-j*5)[0],P(x+j*2-2,y-s_*1.5-j*5)[1],P(x+j*2+4+j,y-s_*1.5-j*5+5+j)[0],P(x+j*2+4+j,y-s_*1.5-j*5+5+j)[1]],fill=(90,86,90,140-j*25))
        dd.line([P(x-s_,y),P(x-s_*.28,y-s_*1.3),P(x+s_*.28,y-s_*1.3),P(x+s_,y)],fill=INK,width=2)
    def palm(x,y,k=1):
        dd=D2(); dd.line([P(x,y),P(x+2*k,y-7*k),P(x+1*k,y-12*k)],fill=(98,68,36,255),width=2)
        for a_ in(-160,-120,-60,-20,-90):
            r=math.radians(a_); dd.line([P(x+1*k,y-12*k),P(x+1*k+math.cos(r)*8*k,y-12*k+math.sin(r)*6*k+3*k)],fill=(48,112,52,255),width=2)
    def crystal(x,y,k=1):
        dd=D2(); c=R.choice(((222,236,242),(196,220,236),(240,240,232)))
        for dx,h_ in((-3,5),(0,8),(3,4)): dd.polygon([P(x+dx-2,y),P(x+dx,y-h_*k),P(x+dx+2,y)],fill=c+(255,),outline=INK)
    def ocrystal(x,y,k=1):
        dd=D2()
        for dx,h_ in((-3,7),(0,11),(3,6)): dd.polygon([P(x+dx-2,y),P(x+dx,y-h_*k),P(x+dx+2,y)],fill=(44,40,60,255),outline=(150,120,200,255))
    def pyramid(x,y,k=1):
        dd=D2(); s_=13*k; dd.polygon([P(x-s_,y),P(x,y-s_*.95),P(x+s_,y)],fill=(226,196,140,255)); dd.polygon([P(x,y-s_*.95),P(x+s_,y),P(x+s_*.1,y)],fill=(170,134,90,255))
        for j in(.3,.55,.75): dd.line([P(x-s_*(1-j),y-s_*.95*j),P(x+s_*(1-j),y-s_*.95*j)],fill=(150,116,76,200),width=1)
        dd.line([P(x-s_,y),P(x,y-s_*.95),P(x+s_,y)],fill=INK,width=2)
    def ruin(x,y,k=1):
        dd=D2()
        for dx,h_ in((-6,9),(0,13),(6,6)):
            dd.rectangle([P(x+dx-2,y-h_)[0],P(x+dx-2,y-h_)[1],P(x+dx+2,y)[0],P(x+dx+2,y)[1]],fill=(224,212,188,255),outline=INK)
        dd.polygon([P(x+3,y-1),P(x+9,y-1),P(x+8,y+2),P(x+2,y+2)],fill=(190,178,154,255),outline=INK)
    def shrine(x,y,k=1):
        dd=D2(); dd.rectangle([P(x-7,y-7)[0],P(x-7,y-7)[1],P(x+7,y)[0],P(x+7,y)[1]],fill=(220,208,184,255),outline=INK); dd.polygon([P(x-9,y-7),P(x,y-14),P(x+9,y-7)],fill=(196,170,110,255),outline=INK)
        for dx in(-4,0,4): dd.line([P(x+dx,y-6),P(x+dx,y)],fill=INK,width=1)
    def well(x,y,k=1):
        dd=D2(); dd.ellipse([P(x-6,y-3)[0],P(x-6,y-3)[1],P(x+6,y+3)[0],P(x+6,y+3)[1]],fill=(150,142,130,255),outline=INK); dd.ellipse([P(x-3.5,y-1.5)[0],P(x-3.5,y-1.5)[1],P(x+3.5,y+1.5)[0],P(x+3.5,y+1.5)[1]],fill=(74,120,150,255))
    def flame(x,y,k=1):
        dd=D2(); dd.polygon([P(x,y-11),P(x+4,y-3),P(x+2,y),P(x-2,y),P(x-4,y-3)],fill=(240,130,40,255),outline=INK); dd.polygon([P(x,y-6),P(x+2,y-1),P(x-2,y-1)],fill=(252,220,90,255))
        for j in range(3): dd.ellipse([P(x+j*2,y-14-j*4)[0],P(x+j*2,y-14-j*4)[1],P(x+j*2+5,y-14-j*4+5)[0],P(x+j*2+5,y-14-j*4+5)[1]],fill=(80,76,80,130-j*30))
    def vulture(x,y,k=1):
        dd=D2(); dd.line([P(x-6,y-2),P(x-3,y-4),P(x,y),P(x+3,y-4),P(x+6,y-2)],fill=(40,30,30,255),width=2)
    def gate_icon(x,y,k=1):
        dd=D2()
        for dx in(-12,12): dd.rectangle([P(x+dx-5,y-20)[0],P(x+dx-5,y-20)[1],P(x+dx+5,y)[0],P(x+dx+5,y)[1]],fill=(160,160,172,255),outline=INK); dd.polygon([P(x+dx-6,y-20),P(x+dx,y-27),P(x+dx+6,y-20)],fill=(140,56,44,255),outline=INK)
        dd.rectangle([P(x-8,y-12)[0],P(x-8,y-12)[1],P(x+8,y)[0],P(x+8,y)[1]],fill=(120,118,130,255),outline=INK); dd.arc([P(x-6,y-14)[0],P(x-6,y-14)[1],P(x+6,y-2)[0],P(x+6,y-2)[1]],180,360,fill=INK,width=2)
    def worm(x,y,k=1):
        dd=D2()
        for i_ in range(4):
            cx_=x+i_*13-20; dd.chord([P(cx_-6,y-8)[0],P(cx_-6,y-8)[1],P(cx_+6,y+6)[0],P(cx_+6,y+6)[1]],180,360,fill=(160,110,84,255),outline=INK)
        dd.ellipse([P(x-30,y-9)[0],P(x-30,y-9)[1],P(x-18,y+1)[0],P(x-18,y+1)[1]],fill=(190,130,100,255),outline=INK)
    def tent2(x,y,k=1): tent(x,y)
    def zrand(zm,n,mind=9,edge=0):
        ys_,xs_=np.nonzero(zm); out=[]
        if not len(xs_): return out
        for _ in range(n*12):
            if len(out)>=n: break
            j=R.randrange(len(xs_)); x,y=float(xs_[j])+R.uniform(-.4,.4),float(ys_[j])+R.uniform(-.4,.4)
            if all((x-a)**2+(y-b)**2>mind*mind for a,b in out): out.append((x,y))
        return out
    def rwalk(x,y,ang,n,step,wob):
        pts=[(x,y)]
        for _ in range(n): ang+=R.uniform(-wob,wob); x+=math.cos(ang)*step; y+=math.sin(ang)*step; pts.append((x,y))
        return pts
    # montanhas: cordilheiras irregulares (picos grandes no miolo, morros menores nas bordas, espaçamento aleatório)
    mm=stylize(Mt,.035,(130,118,108,255),(70,56,44,200),None,34,70)
    if mm is not None and mm.any():
        dm=distance_transform_edt(mm); ys_,xs_=np.nonzero(mm); out=[]
        for _ in range(len(xs_)//10):
            j=R.randrange(len(xs_)); x,y=float(xs_[j]),float(ys_[j]); sz=.55+min(1.1,dm[int(y),int(x)]/8)*R.uniform(.6,1.2); md=9+sz*6
            if R.random()<.45 or any((x-a)**2+(y-b)**2<md*md for a,b in out): continue
            out.append((x,y)); items.append((y,mount_n,(x,y,sz)))
    ZG=lambda k: INT.get(k,'sand')
    for i_,k_ in enumerate(KEYS):
        if k_ in TOWNK: continue
        zm=(ID==i_)&land&~water; ar=int(zm.sum()); n=max(8,ar//900); g=ZG(k_); rx_,ry_,rw_,rh_=rect[k_]
        ing=gaussian_filter(zm.astype(np.float32),5)>.82     # interior: longe da borda
        zi=zm&ing
        dr=ImageDraw.Draw(base,'RGBA')
        if g=='sand':
            for x,y in zrand(zi,n//3,16): items.append((y,dune_n,(x,y)))
            for x,y in zrand(zi,n//2,11): items.append((y,thorn,(x,y)))
            for x,y in zrand(zi,n//8,26): items.append((y,dead,(x,y)))
            for x,y in zrand(zi,n//9,30): items.append((y,bones,(x,y)))
            for x,y in zrand(zi,n//6,22): items.append((y,rockpile,(x,y)))
        elif g=='red':
            for cx_,cy_ in zrand(zi,max(2,ar//7000),34):
                for _ in range(R.randint(3,6)):
                    a_=R.uniform(0,6.3); r_=R.uniform(3,16); x,y=cx_+math.cos(a_)*r_,cy_+math.sin(a_)*r_*.7
                    if 0<=x<W and 0<=y<H and zm[int(y),int(x)]: items.append((y,mesa_n,(x,y,R.uniform(.8,1.5))))
            for _ in range(max(2,ar//14000)):
                x,y=zrand(zi,1,1)[0] if zi.any() else (rx_,ry_); pts=rwalk(x,y,R.uniform(0,6.3),R.randint(10,22),R.uniform(2.5,4),.6)
                dr.line([(a*S,b*S) for a,b in pts],fill=(80,38,26,170),width=3,joint='curve')
            for x,y in zrand(zi,n//5,16): items.append((y,thorn,(x,y)))
            for x,y in zrand(zi,n//6,20): items.append((y,rockpile,(x,y)))
        elif g=='salt':
            for _ in range(max(6,ar//3500)):
                x,y=zrand(zi,1,1)[0] if zi.any() else (rx_,ry_); pts=rwalk(x,y,R.uniform(0,6.3),R.randint(5,12),R.uniform(3,5),.8)
                dr.line([(a*S,b*S) for a,b in pts],fill=(150,150,156,190),width=2,joint='curve')
            for x,y in zrand(zi,n//3,12): items.append((y,crystal,(x,y)))
            for x,y in zrand(zi,n//9,28): items.append((y,bones,(x,y)))
            for x,y in zrand(zi,n//8,22): items.append((y,thorn,(x,y)))
        elif g=='ash':
            for x,y in zrand(zi,max(1,ar//9000),34): items.append((y,volcano,(x,y,R.uniform(.9,1.5))))
            for _ in range(max(2,ar//9000)):
                x,y=zrand(zi,1,1)[0] if zi.any() else (rx_,ry_); pts=rwalk(x,y,R.uniform(0,6.3),R.randint(10,20),R.uniform(3,4.5),.5)
                dr.line([(a*S,b*S) for a,b in pts],fill=(40,20,16,255),width=7,joint='curve'); dr.line([(a*S,b*S) for a,b in pts],fill=(238,112,40,255),width=4,joint='curve')
            for x,y in zrand(zi,n//3,12): items.append((y,rockpile,(x,y)))
            for x,y in zrand(zi,n//9,30): items.append((y,dead,(x,y)))
            if k_=='obsidiana':
                for x,y in zrand(zi,n//2,10): items.append((y,ocrystal,(x,y)))
        else:
            for x,y in zrand(zi,n//2,13): items.append((y,rockpile,(x,y)))
            for x,y in zrand(zi,n//5,20): items.append((y,dead,(x,y)))
            for x,y in zrand(zi,n//4,14): items.append((y,thorn,(x,y)))
        # marcas reais da zona
        j_=Zj[k_]; ZW_,ZH_=j_['w'],j_['h']
        for m_ in j_.get('marks',[]):
            X=rx_+m_['x']/ZW_*rw_; Y=ry_+m_['y']/ZH_*rh_
            if m_['k']=='shrine': items.append((Y,shrine,(X,Y)))
        for p_ in j_['props']:
            X=rx_+p_['x']/ZW_*rw_; Y=ry_+p_['y']/ZH_*rh_
            if not(0<=X<W and 0<=Y<H) or ID[int(Y),int(X)]!=i_: continue
            if p_.get('k')=='fire' or p_.get('t')=='fire': items.append((Y,flame,(X,Y)))
            elif p_.get('k') in('column','block') and R.random()<.5: items.append((Y,ruin,(X,Y)))
        # personalidade de cada zona
        if k_=='leito':
            cx_,cy_=rx_+rw_/2,ry_+rh_/2; pts=[(cx_+math.sin(t*5)*rw_*.12,ry_+rh_*t) for t in np.linspace(.04,.96,50)]
            dr.line([(a*S,b*S) for a,b in pts],fill=(120,86,56,255),width=14,joint='curve'); dr.line([(a*S,b*S) for a,b in pts],fill=(210,176,128,255),width=9,joint='curve')
            for a,b in pts[::3]: dr.line([(a*S-3,b*S-2),(a*S+3,b*S+2)],fill=(140,104,70,255),width=1)
        if k_=='oasis':
            ys_,xs_=np.nonzero(gaussian_filter(water.astype(np.float32)*(ID==i_),3)>.15)
            for _ in range(10):
                if len(xs_)==0: break
                j=R.randrange(len(xs_)); a_=R.uniform(0,6.3); x,y=xs_[j]+math.cos(a_)*7,ys_[j]+math.sin(a_)*6
                if 0<=x<W and 0<=y<H and land[int(y),int(x)] and not water[int(y),int(x)]: items.append((y,palm,(x,y,R.uniform(.9,1.3))))
        if k_ in('tumba','ruinas'): 
            x,y=rx_+rw_*.5,ry_+rh_*.5; items.append((y,pyramid,(x,y,1.6 if k_=='ruinas' else 1.1)))
        if k_=='cisterna': items.append((ry_+rh_*.5,well,(rx_+rw_*.5,ry_+rh_*.5)))
        if k_=='verme': items.append((ry_+rh_*.5,worm,(rx_+rw_*.5,ry_+rh_*.5)))
        if k_=='portao': items.append((ry_+rh_*.18,gate_icon,(rx_+rw_*.5,ry_+rh_*.18,1.4)))
        if k_ in('abutres','mirante','garganta'):
            for x,y in zrand(zm,4,18): items.append((y-8,vulture,(x,y-8)))
        if k_ in('cercos','cercos1','saqueadores'):
            for x,y in zrand(zi,8 if k_=='cercos' else 5,12): items.append((y,tent2,(x,y)))
        if k_=='forjas':
            for x,y in zrand(zi,5,24): items.append((y,flame,(x,y)))
items.sort(key=lambda t:t[0])
if REG==2:
    def sized(fn,sc):
        def w(x,y,*a):
            global P
            old=P; P=lambda u,v:((x+(u-x)*sc)*S,(y+(v-y)*sc)*S)
            try: fn(x,y,*a)
            finally: P=old
        return w
    SC2={dune_n:1.6,thorn:1.7,dead:1.6,bones:1.7,rockpile:1.7,mesa_n:1.35,crystal:1.7,ocrystal:1.6,volcano:1.35,palm:1.6,flame:1.6,ruin:1.5,shrine:1.5,pyramid:1.25,vulture:1.7,tent2:1.6,well:1.7,worm:1.4}
    items=[(y,sized(fn,SC2[fn]) if fn in SC2 else fn,a) for y,fn,a in items]
    items.sort(key=lambda t:t[0])
d=ImageDraw.Draw(base,'RGBA')
for _,fn,a in items: put(fn,*a)
# cidades
for k,n,sc in((('town',9,1.3),('cidade2',6,1.15)) if REG==1 else (('cinzamuro',0,1),)):
    rx,ry,rw,rh=rect[k]
    if REG==2: keep(rx+rw*.5,ry+rh*.62,1.5); [house(rx+rw*(.18+.64*i_/7),ry+rh*.78+R.randint(-3,3),.9) for i_ in range(8)]
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
ROADS=[]; MARKS=[]
MAINZ=['town','estrada','planicie','ponte','colinas','desfiladeiro','passo','cidade2'] if REG==1 else ['cinzamuro','muralha','planalto','garganta','mesas','leito','salinas','rubro','forjas','portao']
def ismain(a,b): return a in MAINZ and b in MAINZ and abs(MAINZ.index(a)-MAINZ.index(b))==1
def road(pts,main=False): ROADS.append(([(x*S,y*S) for x,y in pts],main))
EXITS={}
for a_,sa,pa,b_,pb in LINKS:
    EXITS.setdefault(a_,[]).append((sa,pa,b_)); EXITS.setdefault(b_,[]).append((OPP[sa],pb,a_))
for k,exl in EXITS.items():
    H_=hubpt(k)
    for sd,pp,nb in exl:
        E=pull(k,ex_pt(k,sd,pp)); mid=((E[0]+H_[0])/2+(H_[1]-E[1])*.08,(E[1]+H_[1])/2-(H_[0]-E[0])*.08)
        road(bez(E,mid,H_,30),ismain(k,nb))
for a_,sa,pa,b_,pb in LINKS:
    A_=ex_pt(a_,sa,pa); B_=ex_pt(b_,OPP[sa],pb)
    if math.hypot(A_[0]-B_[0],A_[1]-B_[1])>45: continue   # ligação em ciclo: sem estrada reta atravessando o mapa
    A2,B2=pull(a_,A_),pull(b_,B_); road(bez(A2,((A2[0]+B2[0])/2,(A2[1]+B2[1])/2),B2,24),ismain(a_,b_)); MARKS.append(((A_[0]+B_[0])/2,(A_[1]+B_[1])/2,ismain(a_,b_)))
if REG==1:
  t_,e_,pa_,c2_=rect['town'],rect['estrada'],rect['passo'],rect['cidade2']
  CITYL=(((t_[0]+t_[2]*.45,t_[1]),(e_[0]+e_[2]*.45,e_[1]+e_[3]),('town','estrada')),((pa_[0]+pa_[2]*.5,pa_[1]),(c2_[0]+c2_[2]*.5,c2_[1]+c2_[3]),('passo','cidade2')))
else:
  t_,m_=rect['cinzamuro'],rect['muralha']; CITYL=(((t_[0]+t_[2]*.5,t_[1]+t_[3]*.3),(m_[0]+m_[2]*1100/4200*0+m_[2]*.5,m_[1]+m_[3]),('a','b')),)
for A_,B_,mk in CITYL:
    if math.hypot(A_[0]-B_[0],A_[1]-B_[1])<90: road(bez(A_,((A_[0]+B_[0])/2+6,(A_[1]+B_[1])/2),B_),True)
# desenho em camadas: contorno escuro -> miolo de terra batida -> fio central (principal = vermelho tracejado)
def strokes(w,col,main_only=None):
    for pts,mn in ROADS:
        if main_only is True and not mn: continue
        if main_only is False and mn: continue
        d.line(pts,fill=col,width=w,joint='curve')
        for q in (pts[0],pts[-1]): d.ellipse([q[0]-w/2,q[1]-w/2,q[0]+w/2,q[1]+w/2],fill=col)
strokes(10,(58,34,16,235),False); strokes(14,(58,34,16,240),True)
strokes(6,(218,188,132,255),False); strokes(9,(236,206,126,255),True)
for pts,mn in ROADS:
    if not mn: continue
    acc=0;dr=True
    for p_,q_ in zip(pts,pts[1:]):
        L=math.hypot(q_[0]-p_[0],q_[1]-p_[1])
        if dr: d.line([p_,q_],fill=(150,48,32,235),width=2)
        acc+=L
        if acc>=(14 if dr else 9): acc=0;dr=not dr
# marcos de pedra nas passagens entre zonas
for x,y,mn in MARKS:
    r=(7 if mn else 5)*S/2
    d.ellipse([x*S-r-2,y*S-r-2,x*S+r+2,y*S+r+2],fill=(58,34,16,255)); d.ellipse([x*S-r,y*S-r,x*S+r,y*S+r],fill=(214,206,190,255))
    d.arc([x*S-r,y*S-r,x*S+r,y*S+r],200,340,fill=(255,255,255,200),width=2)
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
    if REG==1: sea_name('MAR DAS BRUMAS',930,1010,-9); sea_name('GOLFO DO ALVORECER',880,1700,7)
    else:
        for txt,xs_,ys_,an_ in(('MAR DE CINZAS',(int(W*.06),int(W*.3)),(int(H*.4),int(H*.62)),90),('GOLFO DO SAL',(int(W*.6),int(W*.72)),(int(H*.12),int(H*.38)),-6)):
            sub=dist_c[ys_[0]:ys_[1],xs_[0]:xs_[1]]; iy,ix=np.unravel_index(np.argmax(np.where(~land[ys_[0]:ys_[1],xs_[0]:xs_[1]],sub,0)),sub.shape)
            sea_name(txt,xs_[0]+ix,ys_[0]+iy,an_)
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
    d.text(P(bx,by-8),'Região de Brumavale' if REG==1 else 'Terras Áridas de Cinzamuro',font=ft if REG==1 else ImageFont.truetype('mmo/assets/fonts/Almendra-Bold.ttf',24*S),fill=(70,36,16,255),anchor='mm'); d.text(P(bx,by+14),'Nível 1 a 12' if REG==1 else 'Nível 10 a 20',font=fs_,fill=(120,56,30,255),anchor='mm')
except Exception as e: print('fonte',e)
out=np.array(base.convert('RGB')).astype(np.float32); hh,ww=out.shape[:2]; v=np.mgrid[0:hh,0:ww]; vx=(v[1]/ww-.5)*2; vy=(v[0]/hh-.5)*2
out*=np.clip(1-.3*(np.maximum(abs(vx),abs(vy))**4),.55,1)[...,None]
Image.fromarray(np.clip(out,0,255).astype(np.uint8)).resize((W,H),Image.LANCZOS).save(A+'mapa_regiao%d.png'%REG,optimize=True)
Image.fromarray(np.where(land,ID,255).astype(np.uint8)).resize((W//2,H//2),Image.NEAREST).save(A+'mapa_regiao%d_ids.png'%REG)
# centros dos rótulos = centro da região visível (centróide da máscara)
NMd=ns.get('NM') or {}
lay={'w':W,'h':H,'keys':[k if k in TOWNK else 'zone_'+k for k in KEYS],'nm':{('zone_'+k):NMd.get(k,k) for k in KEYS if k not in TOWNK},'c':{}}
for i,k in enumerate(KEYS):
    m=(ID==i)&land; ys2,xs2=np.nonzero(m)
    lay['c'][k]=[float(xs2.mean()),float(ys2.mean()),float(np.ptp(xs2)),float(np.ptp(ys2))] if len(xs2) else [0,0,0,0]
json.dump(lay,open(A+'mapa_regiao%d_layout.json'%REG,'w'))
print('ok',W,H)
