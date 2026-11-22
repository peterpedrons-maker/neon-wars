"""Zonas do MUNDO CONTÍNUO (esboço v3): Estrada de Brumavale (ligação) e Planície de Brumavale (zona de caça maior).
Usa o atlas já gerado (assets/atlas_regiao1.png/json: floresta + props de vila 'v_*'); o chão é uma imagem em 1/4 do mundo
(1 px = 4 px) cujas cores o renderizador reconhece. Cada zona tem `exits` (saída por caminho + fade) e uma barreira de borda
(props densos + parede invisível `wallc`) com aberturas só nas saídas.
Uso (em lendas-de-taverna/tools/mmo):  python3 build_mundo.py   -> assets/zone_estrada.json/_ground.png, zone_planicie.json/_ground.png"""
import os,json,math,random,sys
import numpy as np
from PIL import Image
from scipy.ndimage import distance_transform_edt
from skimage import measure
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import zoneshape as ZS
HERE=os.path.dirname(os.path.abspath(__file__));A=os.path.join(HERE,'..','..','mmo','assets')
AJ=json.load(open(f'{A}/atlas_regiao1.json'))
GS=4
TALL_B=['c0786ec629','bfef3c867f','451b53119f','d32da83612','8b358748b3','dee96fd12c']
TALL_C=['6f5e5b765c','615799f946','a012171cf1','5a100d7474']
BUSH=['5e132ed62f','87f51eb8a1','5369c15f09','1055f1c689']
ROCK=['d876089903','244580aa96','ca1d87b329','8f3ce74d92','ce03221eb2','498aebd592','545a9bb762']
FLATS=[k for k,v in AJ.items() if not k.startswith(('b_','v_')) and v[2]<=16 and v[3]<=19 and k not in('fi0','fi1','fi2','fi3','bf0','bf1','bf2','bf3')]
GR=np.array([74,138,58]);GR2=np.array([66,124,52]);DR=np.array([136,98,62]);WT=np.array([58,116,214]);SH=np.array([196,176,120]);DFc=np.array([40,100,60]);GVc=np.array([96,84,120]);RKc=np.array([108,112,124]);RDc=np.array([168,92,70]);SLc=np.array([226,228,232]);ASc=np.array([60,56,62]);SDc=np.array([206,178,130]);SWc=np.array([74,92,40])

def seg_d(px,py,a,b):
    ax,ay=a;bx,by=b;dx,dy=bx-ax,by-ay;L=dx*dx+dy*dy or 1;t=np.clip(((px-ax)*dx+(py-ay)*dy)/L,0,1);return np.hypot(px-(ax+t*dx),py-(ay+t*dy))
def path_d(px,py,pts):
    d=np.full(px.shape,1e9)
    for a,b in zip(pts,pts[1:]):d=np.minimum(d,seg_d(px,py,a,b))
    return d


# ---- ANTI-SOBREPOSIÇÃO: estruturas (tendas, barris, caixas, totens, tochas...) nunca nascem uma em cima da outra ----
_V={'well':26,'lamp1':5,'lamp2':5,'banner1':8,'banner2':7,'sign':6,'crates':28,'stall':30,'post':6,'barrel1':23,'barrel2':23,'hay1':20,'hay2':20,'bench1':24,'bench2':24,'planter1':20,'planter2':18,'sack1':9,'sack2':9,'torch1':5,'torch2':5,'torch3':5}
_K={'tent':80,'totem':16,'drums':22,'column':14,'tomb':18,'bones':7}
_PRIO={'fire':0,'tent':1,'well':1,'stall':1,'totem':2,'drums':2,'column':3,'tomb':3,'crates':4,'bench1':4,'bench2':4,'hay1':5,'hay2':5,'barrel1':5,'barrel2':5,'planter1':5,'planter2':5,'sack1':6,'sack2':6,'banner1':7,'banner2':7,'sign':7,'post':7,'lamp1':7,'lamp2':7,'torch1':8,'torch2':8,'torch3':8,'bones':9}
_COVER={'flower','tuft','pebble'}
def _foot(p):
    if p['t']=='fire':return 'fire',18
    if p['t']=='k' and p['k'] in _K:return p['k'],_K[p['k']]
    if p['t']=='p' and p['id'].startswith('v_') and p['id'][2:] in _V:return p['id'][2:],_V[p['id'][2:]]
    return None,0
def declutter(P,W,H):
    """Remove sobreposição entre estruturas: o item menos importante é empurrado para o ponto livre mais próximo (até 170px) ou removido.
    Flores/capim/pedrinhas que nasceriam em cima de uma estrutura também saem. Não mexe na posição de quem não conflita."""
    S=[(i,)+_foot(P[i]) for i in range(len(P))];S=[(i,n,r) for i,n,r in S if n]
    S.sort(key=lambda t:(_PRIO.get(t[1],6),-t[2]));kept=[];moved=dropped=0;G={}
    def cell(x,y):return int(x//120),int(y//120)
    def near(x,y):
        cx,cy=cell(x,y)
        for a in(-1,0,1):
            for b in(-1,0,1):
                for q in G.get((cx+a,cy+b),()):yield q
    def hit(x,y,r,slack=3):
        for qx,qy,qr in near(x,y):
            if math.hypot(x-qx,y-qy)<r+qr-slack:return (qx,qy)
        return None
    rm=set()
    for i,n,r in S:
        p=P[i];h=hit(p['x'],p['y'],r)
        if h is None:kept.append((p['x'],p['y'],r));G.setdefault(cell(p['x'],p['y']),[]).append((p['x'],p['y'],r));continue
        base=math.atan2(p['y']-h[1],p['x']-h[0]);ok=False
        for d in range(10,172,10):
            for k in(0,1,-1,2,-2,3,-3,4,-4,5,-5,6):
                a=base+k*.52;x=p['x']+math.cos(a)*d;y=p['y']+math.sin(a)*d
                if 60<x<W-60 and 60<y<H-60 and hit(x,y,r) is None:
                    p['x']=round(x);p['y']=round(y);ok=True;break
            if ok:break
        if ok:
            moved+=1;kept.append((p['x'],p['y'],r));G.setdefault(cell(p['x'],p['y']),[]).append((p['x'],p['y'],r))
        elif n in('fire','tent','well','stall'):kept.append((p['x'],p['y'],r))     # essenciais ficam
        else:rm.add(i);dropped+=1
    for i,p in enumerate(P):          # decoração rasteira em cima de estrutura
        if p['t']=='k' and p['k'] in _COVER and hit(p['x'],p['y'],4,0) is not None:rm.add(i);dropped+=1
    P[:]=[p for i,p in enumerate(P) if i not in rm];return moved,dropped

def build(name,W,H,seed,nome,nv,roads,trails,waters,exits,camps,pois,start,side_theme,band=(380,380,380,380),dens=1.0,hills=None,packs=0,lairs=(),fdens=1.0,conifer=.3,ground=None,region_extra=None,pack_n=3,gates=(),dead=0.0,shrines=(),wxw=None,extra_k=()):
    """side: 0=N 1=S 2=W 3=E. waters: lista de (cx,cy,rx,ry). exits: dict(id,nm,side,pos,to,at,ready,msg). camps/pois: (x,y)."""
    rr=random.Random(seed);gw=W//GS;gh=H//GS
    def smooth(sd,step):
        g=np.random.RandomState(sd).rand(gh//step+3,gw//step+3)
        return np.array(Image.fromarray((g*255).astype('uint8')).resize((gw,gh),Image.BICUBIC),dtype=float)/255
    def fbm(sd,steps=(80,40,20),amps=(.6,.3,.1)):return sum(a*smooth(sd+i,s) for i,(s,a) in enumerate(zip(steps,amps)))
    yy,xx=np.mgrid[0:gh,0:gw];wx=xx*GS+GS/2;wy=yy*GS+GS/2
    N1=fbm(seed+3);N2=fbm(seed+8,(60,30,12),(.5,.35,.15));N3=fbm(seed+14,(120,60,30),(.55,.3,.15));CL=fbm(seed+40,(90,45,22),(.62,.28,.10))
    qx=wx+(N2-.5)*90;qy=wy+(N1-.5)*90
    # ---- FORMATO JOGÁVEL (mesmo do mapa-múndi): tudo fora do contorno é barreira
    INSIDE,CORRM=ZS.inside(name.replace('zone_',''),W,H,exits,wx,wy,True)
    DIN=distance_transform_edt(INSIDE)*GS;DOUT=distance_transform_edt(~INSIDE)*GS
    _in2=DIN>=130;_ix=distance_transform_edt(~_in2,return_indices=True);_id=_ix[0]*GS;_ii2=_ix[1]
    def _clip(pts,keep=110,maxd=520):     # estrada/trilha só existe DENTRO do contorno: trechos que escapam são puxados para dentro (curvas curtas) ou cortados (caminho que nem existe)
        out=[];cur=[]
        for (ax,ay),(bx,by) in zip(pts,pts[1:]):
            n=max(1,int(math.hypot(bx-ax,by-ay)//25))
            for k_ in range(n+1 if (bx,by)==pts[-1] else n):
                x_=ax+(bx-ax)*k_/n;y_=ay+(by-ay)*k_/n;i_=min(gh-1,max(0,int(y_)//GS));j_=min(gw-1,max(0,int(x_)//GS))
                if min(x_,y_,W-x_,H-y_)<200 or DIN[i_,j_]>=keep:
                    if cur and math.hypot(x_-cur[-1][0],y_-cur[-1][1])>110:
                        if len(cur)>1:out.append(cur)
                        cur=[]
                    cur.append((x_,y_))
                elif _id[i_,j_]<=maxd:
                    a_,b_=_ix[1][0][i_,j_],_ix[1][1][i_,j_];pt_=(float(wx[a_,b_]),float(wy[a_,b_]))
                    if cur and math.hypot(pt_[0]-cur[-1][0],pt_[1]-cur[-1][1])>110:     # salto por cima de uma baía: corta a estrada em vez de atravessar a parede
                        if len(cur)>1:out.append(cur)
                        cur=[]
                    cur.append(pt_)
                else:
                    if len(cur)>1:out.append(cur)
                    cur=[]
        if len(cur)>1:out.append(cur)
        res=[]
        for c_ in out:       # suaviza (média móvel) para não ficar serrilhado
            for _ in range(6):c_=[c_[0]]+[((c_[i-1][0]+c_[i][0]+c_[i+1][0])/3,(c_[i-1][1]+c_[i][1]+c_[i+1][1])/3) for i in range(1,len(c_)-1)]+[c_[-1]]
            q_=[]
            for x_,y_ in c_:     # a suavização pode encostar na parede: reprojeta para dentro
                i_=min(gh-1,max(0,int(y_)//GS));j_=min(gw-1,max(0,int(x_)//GS))
                if min(x_,y_,W-x_,H-y_)>=200 and DIN[i_,j_]<keep:a_,b_=_ix[1][0][i_,j_],_ix[1][1][i_,j_];x_,y_=float(wx[a_,b_]),float(wy[a_,b_])
                q_.append((x_,y_))
            res.append(q_)
        return res
    roads=[q for r_ in roads for q in _clip(r_)];trails=[q for r_ in trails for q in _clip(r_,80)]
    _inner=DIN>200;_ii=distance_transform_edt(~_inner,return_indices=True)[1]
    def fixpt(x,y):
        i=min(gh-1,max(0,int(y)//GS));j=min(gw-1,max(0,int(x)//GS))
        if _inner[i,j]:return x,y
        a,b=_ii[0][i,j],_ii[1][i,j];return float(wx[a,b]),float(wy[a,b])
    camps=[fixpt(*c) for c in camps];pois=[fixpt(*c) for c in pois];lairs=[fixpt(*c) for c in lairs];shrines=[fixpt(*c) for c in shrines]
    start=fixpt(*start);gates=[dict(g,**dict(zip(('x','y'),fixpt(g['x'],g['y'])))) for g in gates]
    extra_k=[(k_,*fixpt(x_,y_),s_,r_) for k_,x_,y_,s_,r_ in extra_k]
    if region_extra:
        re_=dict(region_extra)
        for k_ in('boss','colo','mare'):
            if k_ in re_:re_[k_]=dict(re_[k_],**dict(zip(('x','y'),map(round,fixpt(re_[k_]['x'],re_[k_]['y'])))))
        if 'minis' in re_:re_['minis']=[dict(m_,**dict(zip(('x','y'),map(round,fixpt(m_['x'],m_['y']))))) for m_ in re_['minis']]
        if 'cover' in re_:re_['cover']=[[*map(round,fixpt(c_[0],c_[1])),*c_[2:]] for c_ in re_['cover']]
        region_extra=re_
    road_d=np.full(wx.shape,1e9)
    for r in roads:road_d=np.minimum(road_d,path_d(qx,qy,r))
    trail_d=np.full(wx.shape,1e9)
    for r in trails:trail_d=np.minimum(trail_d,path_d(qx,qy,r))
    water=np.zeros(wx.shape,bool);shore=np.zeros(wx.shape,bool)
    for w_ in waters:
        cx,cy,rx,ry=w_[:4];nz=w_[4] if len(w_)>4 else 240   # 5º valor: irregularidade da margem (arena = margem quase lisa)
        e=((wx-cx+(N2-.5)*nz)/rx)**2+((wy-cy+(N1-.5)*nz)/ry)**2;water|=e<1;shore|=(e<1.4)
    water&=INSIDE;shore&=INSIDE;shore&=~water
    # ---- borda: lado mais próximo define a espessura e o tema da barreira
    dists=np.stack([wy,H-wy,wx,W-wx]);side=np.argmin(dists,axis=0);ed=np.min(dists,axis=0)
    BT=np.choose(side,[band[0],band[1],band[2],band[3]])+(N3-.5)*120;BAND=~INSIDE
    # corredores das saídas (sem barreira nem props)
    CORR=np.zeros(wx.shape,bool);LANEP=np.zeros(wx.shape,bool)
    for e in exits:
        along=wx if e['side'] in(0,1) else wy;depth=dists[e['side']]
        LANEP|=(np.abs(along-e['pos'])<100)&(depth<680)
    CORR|=CORRM
    ground_near=np.full(wx.shape,1e9)
    for cx,cy in camps:ground_near=np.minimum(ground_near,np.hypot(wx-cx,wy-cy))
    dirt=((road_d<28)|(trail_d<14)|(N2>.8)&(wy>600)|(ground_near<150)|shore)&~water
    img=np.zeros((gh,gw,3));t=smooth(seed+31,8)
    img[:]=GR[None,None,:]*(1-t[...,None])+GR2[None,None,:]*t[...,None]
    img[dirt]=DR;img[shore]=SH
    GCOL={'dark':DFc,'grave':GVc,'swamp':SWc,'rock':RKc,'red':RDc,'salt':SLc,'ash':ASc,'sand':SDc}
    if ground in GCOL:img[~water&~shore]=GCOL[ground]
    for sd,th in enumerate(side_theme):
        if th in('dark','grave','swamp'):img[BAND&(side==sd)&~water&~CORR]={'dark':DFc,'grave':GVc,'swamp':SWc}[th]
    img[((road_d<26)|(trail_d<12))&~water]=DR;img[LANEP&~water]=DR;img[water]=WT
    Image.fromarray(img.astype('uint8')).save(f'{A}/{name}_ground.png',optimize=True)
    def gi(x,y):return min(gh-1,max(0,int(y)//GS)),min(gw-1,max(0,int(x)//GS))
    def at(m,x,y):i,j=gi(x,y);return m[i,j]
    P=[]
    def addk(k,x,y,s,r=0,wf=None):
        if k=='rock' and ground in('rock','red','salt','ash','sand'):k='crag'    # deserto: rocha sem musgo
        d=dict(t='k',k=k,x=round(x),y=round(y),s=s)
        if r:d['col']=[[0,0,r]]
        if wf:d['wf']=wf
        P.append(d)
    def vp(n,x,y,col=None):
        d=dict(t='p',id='v_'+n,x=round(x),y=round(y))
        if col:d['col']=col
        P.append(d)
    def spr(i,x,y):P.append(dict(t='p',id=i,x=round(x),y=round(y)))
    camp_d=lambda x,y:min([math.hypot(x-cx,y-cy) for cx,cy in list(camps)+list(lairs)+list(shrines)+[(g['x'],g['y']) for g in gates]]+[1e9])
    poi_d=lambda x,y:min([math.hypot(x-cx,y-cy) for cx,cy in pois]+[1e9])
    def free(x,y,m=44):return not(any(math.hypot(x-ex[1],y-ex[2])<ex[4]+70 for ex in extra_k) or at(water,x,y) or (at(shore,x,y) and rr.random()<.7) or at(road_d,x,y)<m or at(trail_d,x,y)<m*.6 or camp_d(x,y)<260 or poi_d(x,y)<200 or at(CORR,x,y))
    def grove(x,y,lo):v=at(CL,x,y);return min(1.0,max(0.0,(v-lo)*7))
    def place_grid(step,fn,jit=.45):
        step=int(step/ math.sqrt(dens))
        for gy in range(40,H-40,step):
            for gx in range(40,W-40,step):
                x=gx+rr.uniform(-1,1)*step*jit;y=gy+rr.uniform(-1,1)*step*jit
                if 40<x<W-40 and 40<y<H-40 and not at(BAND,x,y):fn(x,y)
    def tree(x,y):
        if ground in ARID or not free(x,y):return    # deserto: sem árvores (espinheiros e rochas vêm de mid/deco)
        f=(.30+at(N3,x,y)*.9)*(.4+at(N1,x,y))*grove(x,y,.56 if fdens<=1 else .40)*fdens
        if hills and hills(x,y)>.2:
            if rr.random()<.45*grove(x,y,.5):spr(rr.choice(TALL_C),x,y)
            return
        if rr.random()<min(.9,f*.78):
            if dead and rr.random()<dead:addk('dead',x,y,rr.randint(100,150),7)
            else:spr(rr.choice(TALL_C if rr.random()<conifer else TALL_B),x,y)
    ARID=('rock','red','salt','ash','sand')
    def mid(x,y):
        if not free(x,y):return
        r=rr.random();d=grove(x,y,.55)
        if ground in ARID:
            if r<.10:addk('thorn',x,y,rr.randint(40,58),10)
            elif r<.17:addk('rock',x,y,rr.randint(40,90),14)
            return
        if hills and hills(x,y)>.25:
            if r<.42:spr(rr.choice(ROCK),x,y)
            return
        if r<.08+d*.20:spr(rr.choice(BUSH),x,y)
        elif r<.11+d*.20:spr(rr.choice(ROCK[:4]),x,y)
    def flat(x,y):
        if at(water,x,y) or at(CORR,x,y):return
        if rr.random()<.20+.5*max(0,at(CL,x,y)-.5):P.append(dict(t='flat',id=rr.choice(FLATS),x=round(x),y=round(y)))
    place_grid(58,tree);place_grid(74,mid)
    if ground not in ARID:place_grid(28,flat,.5)
    def deco(x,y):
        if not free(x,y,50) or any(math.hypot(x-g['x'],y-g['y'])<190 for g in gates):return
        r=rr.random()
        if ground=='grave':
            if r<.36:addk('tombstone',x,y,rr.randint(30,48),9)
            elif r<.46:addk('bones',x,y,22)
            elif r<.52:addk('thorn',x,y,42,10)
        elif ground in ARID:
            if r<.22:addk('rock',x,y,rr.randint(40,90),14)
            elif r<.34:addk('thorn',x,y,rr.randint(42,60),10)
            elif r<.42:addk('bones',x,y,20)
            elif r<.50 and ground in('red','rock'):addk('rock',x,y,rr.randint(70,130),22)
        elif ground=='swamp':
            if r<.40:addk('puddle',x,y,rr.randint(30,60))
            elif r<.52:addk('mush',x,y,26)
            elif r<.60:addk('thorn',x,y,40,10)
            elif r<.64:addk('bones',x,y,18)
    if ground in('grave','swamp')+ARID:place_grid(72,deco,.5)
    # ---- retoques de cenário: lagos com juncos, vitórias-régias e pedras; flores em clareiras; capim e seixos na beira dos caminhos
    def erode(m,k):
        r=m.copy()
        for _ in range(k):r=r&np.roll(r,1,0)&np.roll(r,-1,0)&np.roll(r,1,1)&np.roll(r,-1,1)
        return r
    if water.any():
        ys,xs=np.nonzero(shore)
        for i in range(0,len(ys),5):
            x=float(wx[ys[i],xs[i]]);y=float(wy[ys[i],xs[i]])
            if at(CORR,x,y) or at(road_d,x,y)<60 or at(BAND,x,y):continue
            r=rr.random()
            if r<.075:
                if ground in ARID and ground!='sand':continue
                for _k in range(rr.randint(1,3)):addk('reed',x+rr.uniform(-22,22),y+rr.uniform(-14,14),rr.randint(34,54))
            elif r<.115:addk('rock',x,y,rr.randint(20,34),8)
            elif r<.17:addk('tuft',x,y,rr.randint(14,20))
        deep=erode(water,3)&~erode(water,14);ys,xs=np.nonzero(deep)
        for i in range(0,len(ys),4):
            if rr.random()<.07 and (ground not in ARID or ground=='sand'):
                x=float(wx[ys[i],xs[i]]);y=float(wy[ys[i],xs[i]]);P.append(dict(t='k',k='lily',x=round(x),y=round(y),s=rr.randint(26,40),lift=.06))
    if ground not in('grave','swamp')+ARID:
        def meadow(x,y):
            if not free(x,y,50) or grove(x,y,.5)>.25 or rr.random()>.16:return
            for _k in range(rr.randint(4,7)):addk('flower',x+rr.uniform(-46,46),y+rr.uniform(-34,34),rr.randint(16,24))
        place_grid(110,meadow,.5)
    def edgy(x,y):
        d=at(road_d,x,y)
        if 30<d<74 and not at(water,x,y) and not at(CORR,x,y) and camp_d(x,y)>200:
            r=rr.random()
            if r<.34:addk('tuft',x,y,rr.randint(13,19))
            elif r<.40:addk('pebble',x,y,rr.randint(9,13))
    place_grid(34,edgy,.5)
    if ground=='grave':   # ruínas: 4 colunas em volta de um túmulo
        for _ in range(7):
            for _t in range(40):
                x=rr.uniform(700,W-700);y=rr.uniform(700,H-700)
                if free(x,y,90) and not at(BAND,x,y) and not any(math.hypot(x-g['x'],y-g['y'])<260 for g in gates):
                    for dx,dy in((-70,-50),(70,-50),(-70,50),(70,50)):addk('column',x+dx,y+dy,rr.randint(42,66),9)
                    addk('tomb',x,y,38,18);break
    for g in gates:   # portão de dungeon: duas colunas, runa e fogueiras
        gx,gy=g['x'],g['y'];addk('column',gx-75,gy,120,13);addk('column',gx+75,gy,120,13);addk('rune',gx,gy+12,60)
        P.append(dict(t='fire',x=gx-135,y=gy+30,small=1));P.append(dict(t='fire',x=gx+135,y=gy+30,small=1))
    # ---- acampamentos (NPCs avulsos entram com o sistema de quests): tendas, fogueira, caixas, barris, feno, tochas
    for cx,cy in camps:
        r2=random.Random(int(cx*3+cy))
        P.append(dict(t='fire',x=cx,y=cy+10))
        for i,a in enumerate((2.6,0.5,4.4)):addk('tent',cx+math.cos(a)*150,cy+math.sin(a)*105+10,96,26)
        vp('crates',cx-95,cy+95);vp('barrel1',cx+110,cy+100);vp('sack1',cx+75,cy+112);vp('hay1',cx-135,cy+10);vp('torch1',cx-60,cy+60);vp('torch2',cx+70,cy+40)
        vp('banner1' if r2.random()<.5 else 'banner2',cx,cy-120)
    for lx,ly in lairs:   # covil do chefe de zona: totens, tambores, ossos e fogueira em volta
        P.append(dict(t='fire',x=lx,y=ly+10))
        for i in range(6):
            a=i*1.047+.3;addk('totem',lx+math.cos(a)*230,ly+math.sin(a)*160,rr.randint(84,96),5)
        addk('drums',lx+60,ly+40,60);addk('tent',lx-150,ly-70,110,26)
        for i in range(14):
            a=rr.uniform(0,6.28);d=rr.uniform(60,260);addk('bones',lx+math.cos(a)*d,ly+math.sin(a)*d*.7,18)
    for sx,sy in shrines:   # santuário do chefe de zona: anel de colunas (cemitério) ou lodo/cogumelos/ossos (pântano)
        P.append(dict(t='fire',x=sx,y=sy+10))
        for i in range(6):
            a=i*1.047+.4;px_=sx+math.cos(a)*210;py_=sy+math.sin(a)*150
            if ground=='swamp':addk('mush',px_,py_,34);addk('puddle',sx+math.cos(a+.5)*150,sy+math.sin(a+.5)*105,rr.randint(40,60))
            else:addk('column',px_,py_,rr.randint(62,82),10)
        addk('rune',sx,sy+14,70)
        for i in range(10):
            a=rr.uniform(0,6.28);d=rr.uniform(50,200);addk('bones',sx+math.cos(a)*d,sy+math.sin(a)*d*.7,18)
    for x,y in pois:     # ponto de interesse: banco, lampião e estandarte (vista)
        vp('bench1',x-70,y+10,[[-12,-4,8],[12,-4,8]]);vp('lamp1',x+80,y);vp('banner2',x,y-70);vp('post',x+150,y+30)
    # ---- saídas: tochas dos dois lados, estandarte e placa
    for e in exits:
        s=e['side'];p=e['pos'];dep=70
        if s==0:cx,cy=p,dep;ox,oy=1,0
        elif s==1:cx,cy=p,H-dep;ox,oy=1,0
        elif s==2:cx,cy=dep,p;ox,oy=0,1
        else:cx,cy=W-dep,p;ox,oy=0,1
        for sg in(-1,1):vp('torch1' if sg<0 else 'torch2',cx+ox*sg*130,cy+oy*sg*130)
        for sg in(-1,1):addk('column',cx+ox*sg*232,cy+oy*sg*232,rr.randint(92,108),11)
        e['rect']=[cx-(300 if s>=2 else 200) if False else 0,0,0,0]
        hw=190
        if s==0:e['rect']=[p-hw,0,2*hw,110]
        elif s==1:e['rect']=[p-hw,H-110,2*hw,110]
        elif s==2:e['rect']=[0,p-hw,110,2*hw]
        else:e['rect']=[W-110,p-hw,110,2*hw]
    # ---- barreira de borda por lado (tema) + parede invisível, com aberturas nas saídas
    def band_item(x,y,sd):
        th=side_theme[sd];r=rr.random()
        if at(water,x,y) or at(CORR,x,y):return
        if th=='forest':
            if r<.55:spr(rr.choice(TALL_B),x,y)
            elif r<.8:spr(rr.choice(TALL_C),x,y)
            else:spr(rr.choice(BUSH),x,y)
        elif th=='dark':
            if r<.8:spr(rr.choice(TALL_C),x,y)
            else:addk('dead',x,y,rr.randint(110,150),7)
        elif th=='grave':
            if r<.45:addk('dead',x,y,rr.randint(110,150),7)
            elif r<.7:addk('thorn',x,y,rr.randint(44,60),10)
            elif r<.85:addk('tombstone',x,y,rr.randint(34,48),9)
            else:spr(rr.choice(ROCK),x,y)
        elif th=='swamp':
            if r<.4:addk('dead',x,y,rr.randint(100,140),7)
            elif r<.65:addk('thorn',x,y,rr.randint(44,60),10)
            elif r<.8:addk('mush',x,y,28)
            else:addk('puddle',x,y,rr.randint(34,60))
        elif th=='mount':
            if r<.5 and ground not in ARID:spr(rr.choice(ROCK),x,y)
            elif r<.8 or ground in ARID:addk('rock',x,y,rr.randint(110,200),22)
            else:spr(rr.choice(TALL_C),x,y)
        else:
            if r<.6:spr(rr.choice(TALL_C),x,y)
            elif r<.85:spr(rr.choice(TALL_B),x,y)
            else:spr(rr.choice(ROCK),x,y)
    step=int(40/ math.sqrt(dens))
    for gy in range(20,H-20,step):
        for gx in range(20,W-20,step):
            x=gx+rr.uniform(-.5,.5)*step;y=gy+rr.uniform(-.5,.5)*step
            if 0<x<W and 0<y<H and at(BAND,x,y):
                if at(DOUT,x,y)>520 and ((gx//step+gy//step)%3):continue
                band_item(x,y,int(at(side,x,y)))
    for gy in range(40,H-40,110):
        for gx in range(40,W-40,110):
            x=gx+rr.uniform(-.4,.4)*110;y=gy+rr.uniform(-.4,.4)*110
            if not(0<x<W and 0<y<H):continue
            sd=int(at(side,x,y))
            if at(BAND,x,y) and side_theme[sd]=='mount' and 60<at(DOUT,x,y)<700 and not at(water,x,y) and not at(CORR,x,y):addk('mount',x,y,rr.randint(190,270),0,1.5)
    wall=[];KW=.36   # a barreira fica na entrada da faixa: o que o herói vê (crista de montanhas / mata fechada) é exatamente o que o bloqueia
    def ridge(x,y,sd,i):
        th=side_theme[sd];j=lambda a:rr.uniform(-a,a)
        if th=='mount':
            if i%3==0:addk('mount',x+j(22),y+j(22),rr.randint(240,310),0,1.6)
            if i%4==1:addk('rock',x+j(30),y+j(30),rr.randint(110,160),22)
        elif th=='forest':
            spr(rr.choice(TALL_B),x+j(14),y+j(14))
            if i%2==0:spr(rr.choice(TALL_C),x+j(18),y+j(18)+16)
            if i%3==0:spr(rr.choice(BUSH),x+j(16),y+j(16)+28)
        elif th=='dark':
            spr(rr.choice(TALL_C),x+j(14),y+j(14))
            if i%2==0:addk('dead',x+j(16),y+j(16)+14,rr.randint(120,150),7)
        elif th=='grave':
            addk('dead',x+j(14),y+j(14),rr.randint(130,160),7)
            if i%2==0:addk('thorn',x+j(18),y+j(18)+16,rr.randint(48,62),10)
            if i%3==0:addk('tombstone',x+j(18),y+j(18)+26,rr.randint(34,46),9)
        elif th=='swamp':
            addk('dead',x+j(14),y+j(14),rr.randint(120,150),7)
            if i%2==0:addk('thorn',x+j(18),y+j(18)+16,rr.randint(48,62),10)
            if i%3==0:addk('mush',x+j(18),y+j(18)+24,28)
    wi=0
    for c_ in measure.find_contours(np.pad(INSIDE,1,constant_values=False).astype(float),.5):
        acc_=0.0;prev=c_[0]
        for q_ in c_[::1]:
            acc_+=math.hypot(q_[0]-prev[0],q_[1]-prev[1])*GS;prev=q_
            if acc_<26:continue
            acc_=0.0;x=(q_[1]-1)*GS+GS/2;y=(q_[0]-1)*GS+GS/2
            if x<40 or y<40 or x>W-40 or y>H-40:continue            # boca dos corredores (borda do retângulo): aberta
            sd=int(at(side,x,y));wall.append([round(x),round(y),26]);wi+=1
            if wi%2==0 and not at(CORR,x,y) and not at(water,x,y):ridge(x,y,sd,wi//2)
    # contorno jogável (polígonos fechados, ~32px entre pontos): minimapa e mapa de área recortam por ele
    shape=[]
    for c_ in measure.find_contours(np.pad(INSIDE,1,constant_values=False).astype(float),.5):
        pts=[];acc_=1e9;prev=c_[0]
        for q_ in c_:
            acc_+=math.hypot(q_[0]-prev[0],q_[1]-prev[1])*GS;prev=q_
            if acc_<32:continue
            acc_=0;pts.append([int(min(W,max(0,(q_[1]-1)*GS+GS/2))),int(min(H,max(0,(q_[0]-1)*GS+GS/2)))])
        if len(pts)>=12:shape.append(pts)
    spawns=[]
    if packs:
        tries=0;centers=[]
        while len(centers)<packs and tries<4000:
            tries+=1;x=rr.uniform(500,W-500);y=rr.uniform(500,H-500)
            if at(BAND,x,y) or at(DIN,x,y)<260 or at(water,x,y) or at(CORR,x,y) or camp_d(x,y)<420:continue
            if any(math.hypot(x-e['rect'][0]-e['rect'][2]/2,y-e['rect'][1]-e['rect'][3]/2)<900 for e in exits):continue
            if any(math.hypot(x-cx,y-cy)<430 for cx,cy in centers):continue
            centers.append((x,y))
        for gi,(cx,cy) in enumerate(centers):
            n=rr.choices([1,2,3,4],[.32,.3,.24,.14])[0]   # isolados, duplas, grupos pequenos (dá para puxar um a um ou agrupar)
            for i in range(n):
                a=i*6.283/n+rr.uniform(-.5,.5);rad=0 if n==1 else 55+10*n;spawns.append([round(cx+math.cos(a)*rad),round(cy+math.sin(a)*rad*.75),gi])
    for k_,x_,y_,s_,r_ in extra_k:addk(k_,x_,y_,s_,r_)
    _mv,_dr=declutter(P,W,H);print('   anti-sobreposição:',name,'movidos',_mv,'removidos',_dr)
    if name.endswith('lago'):P[:]=[p for p in P if not(380<p['x']<2020 and 930<p['y']<1270 and p.get('k')!='lily')]   # arena do Maragon: só grama e água
    if name.endswith('colinas'):     # clareira redonda do Gigante: nada de cenário (só capim/flor) nem monstros comuns num raio de 780px
        _cx,_cy,_R=2500,2300,780
        P[:]=[p for p in P if not(math.hypot(p['x']-_cx,p['y']-_cy)<_R and p.get('k') not in ('flower','grass','tuft'))]
        spawns[:]=[q for q in spawns if math.hypot(q[0]-_cx,q[1]-_cy)>_R+120]
    # ---- ESTRADAS SEMPRE LIVRES (dono: "estrada passando por dentro de pedras/montanhas"): varredura final tira qualquer
    #      cenário sólido/grande que invada a faixa da estrada ou da trilha (miúdos como flor/capim/seixo ficam)
    _small={'flower','grass','tuft','pebble','reed','lily'}
    def _rd(x,y):
        d=1e9
        for pts in list(roads)+list(trails):
            for (ax,ay),(bx,by) in zip(pts,pts[1:]):
                vx,vy=bx-ax,by-ay;L=vx*vx+vy*vy or 1;t=max(0,min(1,((x-ax)*vx+(y-ay)*vy)/L));d=min(d,math.hypot(x-ax-t*vx,y-ay-t*vy))
        return d
    _rm=0
    for p_ in list(P):
        if p_.get('k') in _small:continue
        if p_['t']=='p' and not p_.get('col'):continue      # sprites decorativos pequenos sem colisão (lampiões etc. já respeitam a estrada)
        cr=max([c[2] for c in p_.get('col',[])]+[0]);sz=p_.get('s') or 0
        clr=46+max(cr,sz*.32)
        if _rd(p_['x'],p_['y'])<clr:P.remove(p_);_rm+=1
    print('   estradas livres:',name,'removidos',_rm)
    P.sort(key=lambda p:p['y'])
    exs=[dict(id=e['id'],nm=e['nm'],side=e['side'],toSide=e.get('toSide',-1),x=e['rect'][0],y=e['rect'][1],w=e['rect'][2],h=e['rect'][3],to=e['to'],at=e['at'],ready=e['ready'],msg=e.get('msg','')) for e in exits]
    marks=[dict(k='camp',x=cx_,y=cy_,nm='Acampamento') for cx_,cy_ in camps]+[dict(k='poi',x=x_,y=y_,nm='Ponto de interesse') for x_,y_ in pois]+[dict(k='lair',x=x_,y=y_,nm='Covil') for x_,y_ in lairs]+[dict(k='shrine',x=x_,y=y_,nm='Santuário') for x_,y_ in shrines]
    Z=dict(w=W,h=H,props=P,spawns=spawns,plaza=[0,0,1,1],pond=[0,0,1,1],road=[],start=list(start),boss=[W//2,H//2],gate=list(start),
           region=dict(nome=nome,nv=nv,gs=1/GS,mundo=name,ground=ground or '',shape=shape,roads=[[[round(x_),round(y_)] for x_,y_ in r_] for r_ in roads],**({'wx':wxw} if wxw else {}),**(region_extra or {})),exits=exs,marks=marks,fx=[],wallc=wall,**({'gates':[dict(nm=g['nm'],dg=g['dg'],x=g['x'],y=g['y'],r=g.get('r',130)) for g in gates]} if gates else {}))
    json.dump(Z,open(f'{A}/{name}.json','w'),separators=(',',':'))
    from collections import Counter
    print(name,'spawns',len(spawns),'props',len(P),Counter(p.get('k') or p.get('t') for p in P).most_common(8),'paredes',len(wall),'saídas',[e['id'] for e in exs])

# ================================================================ TABELA DE ZONAS E LIGAÇÕES (primeira região, Nv 1–10 + áreas das dungeons)
SIZE=dict(estrada=(2200,3400),planicie=(6000,6000),goblins=(5000,5000),brejo=(2200,4200),ponte=(2200,4200),colinas=(5000,5000),
  desfiladeiro=(2200,4200),passo=(4500,4500),cemiterio=(5000,5000),mortos=(4200,2200),lenhadores=(2200,4200),ogros=(5000,5000),
  brumas=(5000,5000),clareira=(2400,2400),gruta=(2400,2400),lago=(2400,2400),mina=(2400,2400),eremita=(2400,2400),cabana=(2400,2400))
NM=dict(estrada='Estrada de Brumavale',planicie='Planície de Brumavale',goblins='Floresta dos Goblins',brejo='Trilha do Brejo',
  ponte='Ponte do Rio',colinas='Colinas Rochosas',desfiladeiro='Desfiladeiro',passo='Passo da Montanha',cemiterio='Cemitério de Brumavale',
  mortos='Estrada dos Mortos',lenhadores='Trilha dos Lenhadores',ogros='Floresta dos Ogros',brumas='Pântano das Brumas',
  clareira='Clareira das Ruínas (secreta)',gruta='Gruta Aberta (secreta)',lago='Margem do Lago (secreta)',mina='Mina Abandonada (secreta)',
  eremita='Bosque do Eremita (secreto)',cabana='Cabana da Bruxa (secreta)')
OPP={0:1,1:0,2:3,3:2}
# (zona A, lado em A, posição em A, zona B, posição em B) — B usa o lado oposto
LINKS=[('estrada',0,1100,'planicie',3700),('planicie',0,3200,'ponte',1100),('planicie',2,2850,'goblins',2500),('planicie',1,1300,'brejo',1100),
  ('planicie',3,3950,'lago',1200),('goblins',0,2500,'lenhadores',1100),('goblins',1,1800,'clareira',1200),('brejo',1,1100,'brumas',2500),
  ('brejo',2,3500,'eremita',1200),('ponte',0,1100,'colinas',2500),('colinas',3,2500,'cemiterio',2500),('colinas',0,2500,'desfiladeiro',1100),
  ('desfiladeiro',0,1100,'passo',1200),('lenhadores',0,1100,'ogros',2500),('ogros',0,2500,'passo',3300),('cemiterio',3,2500,'mortos',1100),
  ('mortos',3,1100,'passo',2250),('cemiterio',1,2500,'gruta',1200),('passo',3,2250,'mina',1200),('brumas',3,2500,'cabana',1200)]
def _arrive(b,sd,pos):
    W,H=SIZE[b];return {0:[pos,170],1:[pos,H-170],2:[170,pos],3:[W-170,pos]}[sd]
# Região 2 (Terras Áridas de Cinzamuro): ficam FORA do trecho SIZE..LINKS que o build_mapamundi.py (Região 1) lê; ganham mapa-múndi próprio depois
SIZE.update(muralha=(2200,4200),planalto=(6400,6400),garganta=(2200,4800),mesas=(6400,6400),leito=(2400,5600),salinas=(6400,6400),rubro=(2200,4800),forjas=(6000,6000),
  portao=(4500,4500),canion=(5200,5200),cercos1=(4600,2200),cercos=(6400,6400),abutres=(4600,2200),ruinas=(5800,5800),oasis=(2400,2400),mirante=(2400,2400),
  tumba=(2400,2400),cisterna=(2400,2400),saqueadores=(2600,2600),verme=(2600,2600),obsidiana=(2600,2600))
NM.update(muralha='Estrada da Muralha',planalto='Planalto Árido',garganta='Garganta do Vento',mesas='Mesas Rubras',leito='Leito do Rio Seco',salinas='Salinas Brancas',
  rubro='Desfiladeiro Rubro',forjas='Vale das Forjas Mortas',portao='Portão do Deserto',canion='Cânion do Eco',cercos1='Caminho dos Cercos',cercos='Campo dos Cercos',
  abutres='Trilha dos Abutres',ruinas='Ruínas do Sol Caído',oasis='Oásis Escondido (secreto)',mirante='Mirante dos Abutres (secreto)',tumba='Tumba do Nômade (secreta)',
  cisterna='Cisterna Antiga (secreta)',saqueadores='Acampamento dos Saqueadores (secreto)',verme='Covil do Verme (secreto)',obsidiana='Gruta de Obsidiana (secreta)')
R2=['muralha','planalto','garganta','mesas','leito','salinas','rubro','forjas','portao','canion','cercos1','cercos','abutres','ruinas','oasis','mirante','tumba','cisterna','saqueadores','verme','obsidiana']
EXL={k:[] for k in SIZE}
for a,sa,pa,b,pb in LINKS:
    sb=OPP[sa]
    EXL[a].append(dict(id=b,nm=NM[b],side=sa,pos=pa,to='zone_'+b,toSide=sb,at=_arrive(b,sb,pb),ready=True))
    EXL[b].append(dict(id=a,nm=NM[a],side=sb,pos=pb,to='zone_'+a,toSide=sa,at=_arrive(a,sa,pa),ready=True))
EXL['estrada'].append(dict(id='cidade',nm='Brumavale',side=1,pos=1100,to='town',toSide=-1,at=[450,170],ready=True))   # a saída sul da cidade chega pelo TOPO da Estrada (que faz uma ferradura até a Planície)
EXL['passo'].append(dict(id='cidade2',nm='Cinzamuro',side=0,pos=2250,to='cinzamuro',toSide=1,at=[800,2420],ready=True,
  msg='Portão do Passo: o guarda só deixa passar a partir do nível 10, com a quest dos chefes (em construção).'))
EXL['muralha'].append(dict(id='cidade2',nm='Cinzamuro',side=1,pos=1100,to='cinzamuro',toSide=-1,at=[470,170],ready=True))
# ligações da Região 2 (A, lado em A, posição em A, B, posição em B; B usa o lado oposto)
LINKS2=[('muralha',0,1100,'planalto',3200),('planalto',0,3200,'garganta',1100),('planalto',2,2800,'canion',2600),('planalto',3,3400,'oasis',1200),
  ('garganta',0,1100,'mesas',3200),('garganta',3,2400,'mirante',1200),('mesas',0,3200,'leito',1200),('mesas',2,3600,'tumba',1200),('mesas',3,2400,'cercos1',1100),
  ('cercos1',3,1100,'cercos',3200),('cercos',3,2800,'saqueadores',1300),('leito',0,1200,'salinas',3200),('leito',2,3000,'cisterna',1200),('leito',3,4200,'abutres',1100),
  ('abutres',3,1100,'ruinas',5400),('ruinas',3,2900,'verme',1300),('salinas',0,3200,'rubro',1100),('rubro',0,1100,'forjas',3000),('forjas',0,3000,'portao',2250),
  ('forjas',2,2400,'obsidiana',1300)]
for a,sa,pa,b,pb in LINKS2:
    sb=OPP[sa]
    EXL[a].append(dict(id=b,nm=NM[b],side=sa,pos=pa,to='zone_'+b,toSide=sb,at=_arrive(b,sb,pb),ready=True))
    EXL[b].append(dict(id=a,nm=NM[a],side=sb,pos=pb,to='zone_'+a,toSide=sa,at=_arrive(a,sa,pa),ready=True))
EXL['portao'].append(dict(id='regiao3',nm='Região 3',side=0,pos=2250,to='zone_regiao3',toSide=1,at=[2250,4330],ready=False,msg='O Portão do Deserto ainda está fechado: a Região 3 está em obras.'))
def auto_roads(name,hub=None):
    W,H=SIZE[name];hub=hub or (W//2,H//2);r_=random.Random(len(name)*7+W);roads=[]
    for e in EXL[name]:
        if e['id']=='cidade':continue
        p=e['pos'];s=e['side']
        P0={0:(p,10),1:(p,H-10),2:(10,p),3:(W-10,p)}[s];P1={0:(p,H*.2),1:(p,H*.8),2:(W*.2,p),3:(W*.8,p)}[s]
        mid=((P1[0]+hub[0])/2+r_.uniform(-140,140),(P1[1]+hub[1])/2+r_.uniform(-140,140));roads.append([P0,P1,mid,hub])
    return roads
# clima por zona (pesos de clear/rain/storm): perto da cidade quase sempre aberto; pântano e cemitério carregados
WX_BY=dict(**{k:dict(clear=8,storm=1) for k in R2},planicie=dict(clear=6,rain=2),goblins=dict(clear=3,rain=3),brejo=dict(clear=2,rain=4),ponte=dict(clear=3,rain=3),colinas=dict(clear=4,rain=2,storm=1),
  desfiladeiro=dict(clear=3,rain=2,storm=2),passo=dict(clear=3,rain=2,storm=2),cemiterio=dict(clear=2,rain=3,storm=2),mortos=dict(clear=2,rain=3,storm=2),
  lenhadores=dict(clear=3,rain=3),ogros=dict(clear=3,rain=3,storm=1),brumas=dict(clear=1,rain=5,storm=2),clareira=dict(clear=3,rain=2),gruta=dict(rain=3,storm=2),
  lago=dict(clear=3,rain=3),mina=dict(clear=3,rain=2,storm=1),eremita=dict(clear=2,rain=3),cabana=dict(clear=1,rain=4,storm=3))
# bioma de cada zona: as bordas fecham com o relevo da zona VIZINHA (planície que dá em montanha fecha com montanha)
BIOME=dict(**{k:'mount' for k in R2},estrada='forest',planicie='forest',goblins='dark',brejo='dark',ponte='forest',colinas='mount',desfiladeiro='mount',passo='mount',cemiterio='grave',
  mortos='grave',lenhadores='dark',ogros='forest',brumas='swamp',clareira='dark',gruta='grave',lago='forest',mina='mount',eremita='dark',cabana='swamp')
def auto_theme(name):
    th=[BIOME[name]]*4
    for e in EXL[name]:
        if e['id'] in BIOME:th[e['side']]=BIOME[e['id']]
    return th
def Z(name,seed,nv,**kw):
    kw['side_theme']=auto_theme(name)
    kw.setdefault('wxw',WX_BY.get(name))
    W,H=SIZE[name];kw.setdefault('roads',auto_roads(name));kw.setdefault('trails',[]);kw.setdefault('waters',[]);kw.setdefault('camps',[])
    kw.setdefault('pois',[]);kw.setdefault('start',(W//2,H//2))
    build('zone_'+name,W,H,seed,NM[name].replace(' (secreta)','').replace(' (secreto)',''),nv,exits=EXL[name],**kw)
MT=['mount','mount','mount','mount']

# ---------------------------------------------------------------- Estrada de Brumavale (ligação, Nv 1) — sem NPCs: a cidade ainda está atrás
Z('estrada',101,'Nv 1',roads=[[(1100,3390),(1060,2800),(1220,2150),(1000,1500),(1180,800),(1100,10)]],
  waters=[(1700,1500,300,220)],pois=[(1100,1700)],start=(1100,3150),side_theme=['forest','forest','forest','forest'],band=(330,330,360,360),dens=.9)
# ---------------------------------------------------------------- Planície de Brumavale (Nv 1–3)
Z('planicie',202,'Nv 1–3',
  roads=[[(3700,5990),(3600,5400),(3100,4600),(2950,3700),(3150,2700),(3050,1700),(3200,700),(3200,10)],
         [(2950,3700),(2100,3500),(1300,3100),(600,2900),(10,2850)],
         [(3100,4600),(2300,5000),(1600,5500),(1300,5990)]],
  trails=[[(3150,3450),(3900,3300),(4800,3300),(5400,3700),(5990,3950)]],waters=[(4300,4150,700,430)],
  camps=[(2200,2300),(4300,1900)],start=(3700,5740),side_theme=['mount','forest','dark','mount'],band=(400,300,420,420),dens=.8,
  hills=lambda x,y:max(0,min(1,(1400-y)/700)),packs=40,pack_n=3,
  region_extra=dict(zlv=1,lv=[1,3],respawn=40,mobs=['rato','javali','rato','lobo','javali']))
# ---------------------------------------------------------------- Floresta dos Goblins (Nv 3–5)
Z('goblins',303,'Nv 3–5',
  roads=[[(4990,2500),(4200,2450),(3300,2600),(2400,2300),(1500,1650)],[(3300,2600),(3000,3400),(2200,3900),(1800,4990)],[(2400,2300),(2300,1300),(2500,10)]],
  waters=[(3700,3700,380,260)],camps=[(4300,2250)],lairs=[(1500,1550)],start=(4800,2500),
  side_theme=['dark','dark','dark','forest'],band=(380,380,400,300),dens=.95,fdens=1.55,conifer=.6,ground='dark',packs=44,pack_n=3,
  region_extra=dict(zlv=1,lv=[3,5],respawn=45,boss=dict(x=1500,y=1550,lv=6,aggro=440,respawn=300),minis=[dict(type='skrix',x=3300,y=3200,aggro=420,respawn=240)]))
# ---------------------------------------------------------------- Trilha do Brejo (ligação, Nv 3–4)
Z('brejo',404,'Nv 3–4',
  roads=[[(1100,10),(1000,700),(1250,1500),(1000,2300),(1200,3200),(1100,4190)],[(10,3500),(600,3450),(1200,3300)]],
  waters=[(1700,2000,300,220),(500,3100,260,200)],pois=[(1200,2100)],start=(1100,150),side_theme=['forest','dark','dark','dark'],band=(330,330,360,360),
  dens=.9,fdens=1.2,conifer=.4,ground='dark',packs=10,pack_n=3,region_extra=dict(zlv=1,lv=[3,4],respawn=40,mobs=['lobo','rato','javali','lobo']))
# ---------------------------------------------------------------- Ponte do Rio (ligação, Nv 3–4): rio com vau/ponte no meio
Z('ponte',505,'Nv 3–4',roads=[[(1100,4190),(1050,3300),(1100,2300),(1150,1200),(1100,10)]],waters=[(380,2100,430,150),(1860,2100,470,150)],
  pois=[(1500,2900)],start=(1100,4000),side_theme=['forest','forest','forest','forest'],band=(330,330,360,360),dens=.9,packs=10,
  region_extra=dict(zlv=1,lv=[3,4],respawn=40,mobs=['javali','lobo','ogrinho','javali']))
# ---------------------------------------------------------------- Colinas Rochosas (Nv 4–6)
Z('colinas',606,'Nv 4–6',waters=[(3600,3600,380,240)],camps=[(1700,3400),(3700,1300)],pois=[(2500,2300)],start=(2500,4800),side_theme=MT,band=(420,300,400,420),dens=.8,
  hills=lambda x,y:.75,packs=36,pack_n=3,region_extra=dict(zlv=1,lv=[4,6],respawn=45,mobs=['javali','lobo','gnoll','harpia','gnoll','javbruto'],colo=dict(x=2500,y=2300)))
# ---------------------------------------------------------------- Desfiladeiro (ligação, Nv 7–8)
Z('desfiladeiro',707,'Nv 7–8',pois=[(1300,2200)],start=(1100,4000),side_theme=MT,band=(300,300,420,420),dens=.7,hills=lambda x,y:.8,packs=12,pack_n=3,
  region_extra=dict(zlv=1,lv=[7,8],respawn=45,mobs=['gnoll','harpia','bandido','lobo']))
# ---------------------------------------------------------------- Passo da Montanha (Nv 8–10) — portão com guarda (quest em construção)
Z('passo',808,'Nv 8–10',pois=[(2250,500),(900,3500)],camps=[(3600,2600)],start=(1200,4300),side_theme=MT,band=(420,300,420,420),dens=.75,
  hills=lambda x,y:.8,packs=32,pack_n=3,region_extra=dict(zlv=1,lv=[8,10],respawn=45,mobs=['bandido','gnoll','javbruto','harpia','ogrinho','bandido']))
# ---------------------------------------------------------------- Cemitério de Brumavale (Nv 10–12) — entrada da Cripta; chefe Morvath; mini Morcego-Vampiro
Z('cemiterio',909,'Nv 10–12',roads=auto_roads('cemiterio',(2700,2400)),camps=[(1100,1500)],shrines=[(2800,3300)],start=(300,2500),
  side_theme=['grave']*4,band=(380,380,380,380),dens=.7,fdens=.5,conifer=.1,dead=.8,ground='grave',packs=36,pack_n=3,
  gates=[dict(nm='Cripta do Rei Esquecido',dg=5,x=3900,y=1100)],
  region_extra=dict(zlv=2,lv=[10,12],respawn=50,mobs=['esq','carnical','necro','cavcaido','mumia','esqmago','esq','carnical'],
    boss=dict(x=2800,y=3300,lv=13,aggro=440,respawn=300),minis=[dict(type='vamp',x=1700,y=3700,lv=11,aggro=420,respawn=240)]))
# ---------------------------------------------------------------- Estrada dos Mortos (ligação, Nv 8–9)
Z('mortos',1010,'Nv 8–9',pois=[(2100,1100)],start=(170,1100),side_theme=['grave']*4,band=(300,300,360,360),dens=.7,fdens=.5,conifer=.1,dead=.8,ground='grave',
  packs=10,pack_n=3,region_extra=dict(zlv=2,lv=[8,9],respawn=45,mobs=['esq','carnical','morcego','mumia']))
# ---------------------------------------------------------------- Trilha dos Lenhadores (ligação, Nv 5–6)
Z('lenhadores',1111,'Nv 5–6',pois=[(1200,2200)],start=(1100,4000),side_theme=['dark']*4,band=(330,330,360,360),dens=.9,fdens=1.3,conifer=.5,ground='dark',packs=10,pack_n=3,
  region_extra=dict(zlv=1,lv=[5,6],respawn=45,mobs=['gnoll','bandido','tronco','lobo']))
# ---------------------------------------------------------------- Floresta dos Ogros (Nv 8–11) — chefe Gorgash; mini Capitão Presa-de-Ferro
Z('ogros',1212,'Nv 8–11',roads=auto_roads('ogros',(2400,2000)),camps=[(3900,3500)],lairs=[(2400,1600)],start=(2500,4800),
  side_theme=['forest','forest','forest','forest'],band=(380,300,380,380),dens=.95,fdens=1.6,conifer=.5,packs=40,pack_n=3,
  region_extra=dict(zlv=3,lv=[8,11],respawn=45,mobs=['ogrinho','gnoll','ogrolenhador','bandido','tronco','harpia','lobo','ogrolenhador'],
    boss=dict(x=2400,y=1600,lv=12,aggro=440,respawn=300),minis=[dict(type='javcap',x=1500,y=3300,lv=11,aggro=420,respawn=240)]))
# ---------------------------------------------------------------- Pântano das Brumas (Nv 10–12) — entrada do Esgoto; chefe Rei dos Ratos; mini Boticário Podre
Z('brumas',1313,'Nv 10–12',roads=auto_roads('brumas',(2500,2500)),waters=[(1300,1500,420,300),(3700,3100,520,340),(1500,3700,340,240)],camps=[(1200,2600)],
  shrines=[(2500,3400)],start=(2500,300),side_theme=['swamp']*4,band=(380,380,380,380),dens=.7,fdens=.5,conifer=.1,dead=.8,ground='swamp',packs=36,pack_n=3,
  gates=[dict(nm='Esgotos de Brumavale',dg=4,x=3600,y=1500)],
  region_extra=dict(zlv=4,lv=[10,12],respawn=50,mobs=['homemrato','ladrao','cultlodo','sapo','cobra','barata','afogado','rato'],
    boss=dict(x=2500,y=3400,lv=13,aggro=440,respawn=300),minis=[dict(type='botic',x=1500,y=2000,lv=11,aggro=420,respawn=240)]))
# ---------------------------------------------------------------- zonas secretas (becos sem saída; baú/hunt no futuro)
SEC=dict(side_theme=['dark']*4,band=(300,300,300,300),dens=.8,packs=5,pack_n=3)
Z('clareira',1414,'Nv 4–5',pois=[(1200,1200)],start=(1200,300),**{**SEC,'ground':'dark'},region_extra=dict(zlv=1,lv=[4,5],respawn=45,mobs=['goblin','sapador','xama','cogumelo']))
Z('gruta',1515,'Nv 10–11',pois=[(1200,1200)],start=(1200,300),**{**SEC,'side_theme':['grave']*4,'ground':'grave','dead':.8,'fdens':.5},region_extra=dict(zlv=2,lv=[10,11],respawn=45,mobs=['esq','necro','mumia','esqmago']))
# Margem do Lago = arena do Senhor das Marés (caçada): lago no extremo norte com margem quase lisa (o chefe fica na água, de frente para a praia)
# e 5 pedras altas na praia que servem de abrigo contra o Tsunami (region.cover)
LAGO_COVER=[(880,1300),(1520,1300),(1200,1560),(640,1620),(1760,1620)]
Z('lago',1616,'Nv 2–3',waters=[(1200,470,1250,560,50)],pois=[(1200,1200)],start=(300,1200),**{**SEC,'side_theme':['forest']*4,'packs':3},
  extra_k=[('rock',x,y,150,30) for x,y in LAGO_COVER],
  region_extra=dict(zlv=1,lv=[2,3],respawn=40,mobs=['rato','javali','lobo'],mare=dict(x=1200,y=975),cover=[[x,y,30] for x,y in LAGO_COVER]))
Z('mina',1717,'Nv 7–8',pois=[(1200,1200)],start=(300,1200),**{**SEC,'side_theme':MT},hills=lambda x,y:.8,region_extra=dict(zlv=1,lv=[7,8],respawn=45,mobs=['bandido','gnoll','morcego']))
Z('eremita',1818,'Nv 3–4',pois=[(1200,1200)],start=(2100,1200),**{**SEC,'ground':'dark','fdens':1.4},region_extra=dict(zlv=1,lv=[3,4],respawn=40,mobs=['lobo','aranha','cogumelo']))
Z('cabana',1919,'Nv 10–11',waters=[(1500,1500,320,220)],pois=[(1000,1200)],start=(300,1200),**{**SEC,'side_theme':['swamp']*4,'ground':'swamp','dead':.8,'fdens':.5},
  region_extra=dict(zlv=4,lv=[10,11],respawn=45,mobs=['homemrato','cultlodo','sapo','afogado']))
# ---------------------------------------------------------------- Estrada da Muralha (ligação, Região 2, Nv 10–11): sai pelo portão norte de Cinzamuro; segue para o Planalto Árido (em obras)
Z('muralha',2020,'Nv 10–11',roads=[[(1100,4190),(1020,3500),(1180,2800),(1050,2100),(1160,1300),(1100,10)]],pois=[(1100,2100)],camps=[(1500,2900)],start=(1100,4030),
  side_theme=MT,band=(380,380,420,420),dens=.45,fdens=.4,conifer=.5,ground='rock',hills=lambda x,y:.9,packs=22,pack_n=3,
  region_extra=dict(zlv=1,lv=[10,11],respawn=45,reg='Terras Áridas',dif=dict(hp=1.4,atk=1.3,agg=1.5),mobs=['bandidodeserto', 'chacal', 'lagarto', 'abutre']))

# ================================================================ REGIÃO 2 — Terras Áridas de Cinzamuro (Nv 10–20)
# Terreno: rocha/areia/argila/sal/cinza, cordilheira em todas as bordas (a região é montanhosa e seca). Inimigos provisórios: reaproveitam os do jogo por terreno
# (bandido, gnoll, harpia, aranha, cobra, barata, múmia, esqueleto, gárgula...) até existirem os bichos do deserto do BESTIARIO.md.
R2X=dict(zlv=1,respawn=45,reg='Terras Áridas',dif=dict(hp=1.4,atk=1.3,agg=1.5))   # Região 2: bichos mais fortes e agressivos (a Região 1 é o tutorial)
def _rr(seed):return random.Random(seed)
def mesas_rocks(W,H,n,seed,avoid=()):
    r=_rr(seed);out=[]
    while len(out)<n:
        x,y=r.randint(500,W-500),r.randint(500,H-500)
        if any(abs(x-ax)<260 and abs(y-ay)<260 for ax,ay in avoid):continue
        out.append(('rock',x,y,r.randint(170,300),40))
    return out
def ruin_set(cx,cy,n,rad,seed):
    r=_rr(seed);out=[]
    for i in range(n):
        a=r.uniform(0,6.28);d=r.uniform(.2,1)*rad
        out.append((r.choice(['column','column','block','tombstone']),round(cx+math.cos(a)*d),round(cy+math.sin(a)*d*.7),r.randint(50,110),20))
    return out
def r2(name,seed,nv,lv,mobs,ground,**kw):
    kw.setdefault('side_theme',MT);kw.setdefault('band',(380,380,420,420));kw.setdefault('dens',.5);kw.setdefault('fdens',.25);kw.setdefault('conifer',0.0);kw.setdefault('dead',1.0)
    kw.setdefault('pack_n',4);kw.setdefault('packs',max(6,int(SIZE[name][0]*SIZE[name][1]/1.1e6)))
    re=dict(R2X,lv=lv,mobs=mobs,**kw.pop('region_extra',{}))
    Z(name,seed,nv,ground=ground,region_extra=re,**kw)

# ---- Planalto Árido (Nv 10–12): a primeira zona de verdade; chão de areia, acampamento de bandidos, covil da Matriarca Escorpião (santuário)
r2('planalto',2121,'Nv 10–12',[10,12],['escorpiao', 'lagarto', 'chacal', 'bandidodeserto', 'abutre', 'chacal', 'escorpiao'],'sand',
   roads=[[(3200,6390),(3100,5500),(3350,4500),(3200,3500),(3300,2400),(3200,1200),(3200,10)],[(3200,3500),(2200,3300),(1100,3000),(10,2800)],[(3300,4000),(4400,3800),(5400,3500),(6390,3400)]],
   camps=[(2100,4500)],shrines=[(4700,1700)],pois=[(3200,3300),(1500,1300)],start=(3200,6150),packs=34)
# ---- Garganta do Vento (Nv 12–13): desfiladeiro estreito e sinuoso, ventos fortes
r2('garganta',2222,'Nv 12–13',[12,13],['saqueador', 'chacal', 'abutre', 'bandidodeserto', 'lagarto'],'rock',
   roads=[[(1100,4790),(1000,4000),(1250,3100),(1000,2200),(1200,1300),(1100,10)]],pois=[(1100,2400)],start=(1100,4600),band=(420,420,420,420),dens=.7)
# ---- Mesas Rubras (Nv 13–15): argila vermelha com mesas gigantes (blocos de rocha)
r2('mesas',2323,'Nv 13–15',[13,15],['trollmesas', 'golempedra', 'lobopoeira', 'ogrodeserto', 'saqueador', 'lobopoeira'],'red',
   roads=[[(3200,6390),(3150,5400),(3300,4500),(3200,3600),(3250,2400),(3200,1200),(3200,10)],[(3200,3700),(2200,3650),(1000,3600),(10,3600)],[(3250,3000),(4200,2800),(5400,2500),(6390,2400)]],
   extra_k=mesas_rocks(6400,6400,34,2323,avoid=[(3200,y) for y in range(300,6300,600)]),camps=[(4800,4800)],shrines=[(1800,1500)],pois=[(3200,3600)],start=(3200,6150),packs=36)
# ---- Leito do Rio Seco (Nv 14–15): leito largo e sinuoso, areia branca e pedregulhos
r2('leito',2424,'Nv 14–15',[14,15],['escaravelho', 'lagarto', 'verme', 'chacal', 'escorpiao'],'sand',
   roads=[[(1200,5590),(1050,4700),(1300,3800),(1000,2900),(1250,2000),(1200,1100),(1200,10)],[(1100,3000),(500,3000),(10,3000)],[(1250,4200),(1800,4200),(2390,4200)]],
   trails=[[(1200,5500),(1500,4600),(900,3700),(1500,2800),(950,1900),(1400,1000)]],pois=[(1200,2900)],start=(1200,5400),band=(340,340,380,380),dens=.55)
# ---- Salinas Brancas (Nv 15–17): planície de sal ofuscante, lago salgado, entrada das Minas de Sal Esquecidas
r2('salinas',2525,'Nv 15–17',[15,17],['escorpiaosal', 'kobold', 'golemsal', 'escorpiaosal', 'kobold'],'salt',
   roads=[[(3200,6390),(3100,5400),(3300,4500),(3200,3600),(3250,2500),(3200,1200),(3200,10)]],waters=[(2000,3000,900,520,120),(4700,4300,600,380,100)],
   camps=[(4600,2000)],shrines=[(1500,1300)],pois=[(3200,3500),(5200,1400)],start=(3200,6150),packs=36,dens=.4)
# ---- Desfiladeiro Rubro (Nv 17–18): garganta de argila vermelha, mais estreita e mais perigosa
r2('rubro',2626,'Nv 17–18',[17,18],['lobopoeira', 'saqueador', 'golempedra', 'atiradordeserto', 'ogrodeserto'],'red',
   roads=[[(1100,4790),(1000,3900),(1250,3000),(1000,2000),(1200,1000),(1100,10)]],pois=[(1100,2500)],start=(1100,4600),band=(420,420,420,420),dens=.65,packs=12)
# ---- Vale das Forjas Mortas (Nv 18–20): cinza vulcânica, forjas em ruína, entrada da Forja de Pedranegra
r2('forjas',2727,'Nv 18–20',[18,20],['salamandra', 'imp', 'golemmagma', 'caoinfernal', 'anaorenegado', 'salamandra'],'ash',
   roads=[[(3000,5990),(2900,5000),(3100,4000),(3000,3000),(3100,2000),(3000,900),(3000,10)],[(3000,3000),(2000,2500),(1000,2400),(10,2400)]],
   camps=[(4400,3500)],shrines=[(4700,1500),(1400,1400)],pois=[(3000,3000)],start=(3000,5780),packs=34)
# ---- Portão do Deserto (Nv 19–20): fortificação do fim da região; guarda e missão "Abrir o Portão" (Região 3 em obras)
r2('portao',2828,'Nv 19–20',[19,20],['cavnegro', 'armadura', 'atiradordeserto', 'golempedra', 'ogrodeserto'],'rock',
   roads=[[(2250,4490),(2300,3500),(2200,2500),(2250,1400),(2250,10)]],camps=[(3300,3300)],pois=[(2250,1300)],start=(2250,4300),packs=18,band=(420,420,420,420))
# ---- Cânion do Eco (Nv 12–14): desvio a oeste do Planalto; paredões vermelhos
r2('canion',2929,'Nv 12–14',[12,14],['atiradordeserto', 'bandidodeserto', 'abutre', 'escorpiao', 'lagarto'],'red',
   roads=[[(5190,2600),(4200,2700),(3000,2500),(1800,2600),(800,2500),(10,2400)]],shrines=[(1000,1500)],pois=[(2600,2600)],start=(4900,2600),packs=22,
   extra_k=mesas_rocks(5200,5200,16,2929,avoid=[(x,2600) for x in range(300,5000,500)]))
# ---- Caminho dos Cercos (Nv 16–17): estrada de ligação, restos de guerra
r2('cercos1',3030,'Nv 16–17',[16,17],['bandidodeserto', 'saqueador', 'caoguerra', 'atiradordeserto'],'sand',
   roads=[[(10,1100),(1200,1050),(2300,1150),(3400,1050),(4590,1100)]],pois=[(2300,1100)],start=(300,1100),packs=8,band=(340,340,380,380),dens=.5)
# ---- Campo dos Cercos (Nv 17–19): campo de batalha antigo, entrada da Bastilha Negra
r2('cercos',3131,'Nv 17–19',[17,19],['cavnegro', 'armadura', 'magobatalha', 'caoguerra', 'atiradordeserto', 'cavnegro'],'rock',
   roads=[[(10,3200),(1200,3100),(2400,3200),(3300,3150),(4400,2900),(5400,2800),(6390,2800)]],camps=[(3400,3800),(2600,2200)],shrines=[(4800,1300)],pois=[(3300,3150)],start=(300,3200),packs=34,
   extra_k=ruin_set(4800,1500,16,700,3131)+ruin_set(2800,4600,10,500,3132))
# ---- Trilha dos Abutres (Nv 15–16): trilha seca, abutres (harpias) sobrevoam
r2('abutres',3232,'Nv 15–16',[15,16],['abutre', 'chacal', 'escorpiao', 'lagarto'],'sand',
   roads=[[(10,1100),(1100,1000),(2300,1200),(3400,1050),(4590,1100)]],pois=[(2300,1100)],start=(300,1100),packs=8,band=(340,340,380,380),dens=.45)
# ---- Ruínas do Sol Caído (Nv 16–18): templo solar em ruínas, entrada do Templo do Sol Soterrado
r2('ruinas',3333,'Nv 16–18',[16,18],['mumiasolar', 'escaravelho', 'cultistasol', 'mumiasolar', 'escaravelho', 'cultistasol'],'sand',
   roads=[[(10,5400),(1200,5300),(2500,4300),(2900,3200),(3500,2900),(5790,2900)]],camps=[],shrines=[(2900,2200)],pois=[(2900,2900)],start=(300,5400),packs=30,
   extra_k=ruin_set(2900,2300,30,900,3333)+ruin_set(1300,4300,12,500,3334)+ruin_set(4500,1400,12,500,3335))
# ---- zonas secretas (becos sem saída)
SEC2=dict(side_theme=MT,band=(300,300,300,300),dens=.5,packs=6,pack_n=3)
r2('oasis',3434,'Nv 11–12',[11,12],['escaravelho', 'lagarto', 'chacal'],'sand',waters=[(1200,1300,420,280,80)],pois=[(1200,900)],start=(300,1200),**SEC2)
r2('mirante',3535,'Nv 12–13',[12,13],['abutre', 'lagarto', 'escorpiao'],'rock',pois=[(1200,1200)],start=(300,1200),**SEC2)
r2('tumba',3636,'Nv 14–15',[14,15],['mumiasolar', 'escaravelho', 'cultistasol'],'sand',pois=[(1200,1200)],start=(300,1200),extra_k=ruin_set(1200,1200,8,400,3636),**SEC2)
r2('cisterna',3737,'Nv 14–15',[14,15],['escorpiaosal', 'kobold', 'lagarto'],'rock',pois=[(1200,1200)],start=(300,1200),waters=[(1500,1500,260,180,60)],**SEC2)
r2('saqueadores',3838,'Nv 17–18',[17,18],['saqueador', 'bandidodeserto', 'atiradordeserto', 'caoguerra'],'sand',camps=[(1300,1300)],pois=[(1300,900)],start=(300,1300),**{**SEC2,'packs':9})
r2('verme',3939,'Nv 18–19',[18,19],['verme', 'escaravelho', 'escorpiao'],'sand',shrines=[(1300,1500)],pois=[(1300,1200)],start=(300,1300),**{**SEC2,'packs':9})
r2('obsidiana',4040,'Nv 19–20',[19,20],['golemmagma', 'imp', 'caoinfernal', 'salamandra'],'ash',pois=[(1300,1300)],start=(300,1300),**{**SEC2,'packs':9})
