"""Zonas do MUNDO CONTÍNUO (esboço v3): Estrada de Brumavale (ligação) e Planície de Brumavale (zona de caça maior).
Usa o atlas já gerado (assets/atlas_regiao1.png/json: floresta + props de vila 'v_*'); o chão é uma imagem em 1/4 do mundo
(1 px = 4 px) cujas cores o renderizador reconhece. Cada zona tem `exits` (saída por caminho + fade) e uma barreira de borda
(props densos + parede invisível `wallc`) com aberturas só nas saídas.
Uso (em lendas-de-taverna/tools/mmo):  python3 build_mundo.py   -> assets/zone_estrada.json/_ground.png, zone_planicie.json/_ground.png"""
import os,json,math,random
import numpy as np
from PIL import Image
HERE=os.path.dirname(os.path.abspath(__file__));A=os.path.join(HERE,'..','..','mmo','assets')
AJ=json.load(open(f'{A}/atlas_regiao1.json'))
GS=4
TALL_B=['c0786ec629','bfef3c867f','451b53119f','d32da83612','8b358748b3','dee96fd12c']
TALL_C=['6f5e5b765c','615799f946','a012171cf1','5a100d7474']
BUSH=['5e132ed62f','87f51eb8a1','5369c15f09','1055f1c689']
ROCK=['d876089903','244580aa96','ca1d87b329','8f3ce74d92','ce03221eb2','498aebd592','545a9bb762']
FLATS=[k for k,v in AJ.items() if not k.startswith(('b_','v_')) and v[2]<=16 and v[3]<=19 and k not in('fi0','fi1','fi2','fi3','bf0','bf1','bf2','bf3')]
GR=np.array([74,138,58]);GR2=np.array([66,124,52]);DR=np.array([136,98,62]);WT=np.array([58,116,214]);SH=np.array([196,176,120]);DFc=np.array([40,100,60])

def seg_d(px,py,a,b):
    ax,ay=a;bx,by=b;dx,dy=bx-ax,by-ay;L=dx*dx+dy*dy or 1;t=np.clip(((px-ax)*dx+(py-ay)*dy)/L,0,1);return np.hypot(px-(ax+t*dx),py-(ay+t*dy))
def path_d(px,py,pts):
    d=np.full(px.shape,1e9)
    for a,b in zip(pts,pts[1:]):d=np.minimum(d,seg_d(px,py,a,b))
    return d

def build(name,W,H,seed,nome,nv,roads,trails,waters,exits,camps,pois,start,side_theme,band=(380,380,380,380),dens=1.0,hills=None,packs=0,lairs=(),fdens=1.0,conifer=.3,ground=None,region_extra=None,pack_n=3):
    """side: 0=N 1=S 2=W 3=E. waters: lista de (cx,cy,rx,ry). exits: dict(id,nm,side,pos,to,at,ready,msg). camps/pois: (x,y)."""
    rr=random.Random(seed);gw=W//GS;gh=H//GS
    def smooth(sd,step):
        g=np.random.RandomState(sd).rand(gh//step+3,gw//step+3)
        return np.array(Image.fromarray((g*255).astype('uint8')).resize((gw,gh),Image.BICUBIC),dtype=float)/255
    def fbm(sd,steps=(80,40,20),amps=(.6,.3,.1)):return sum(a*smooth(sd+i,s) for i,(s,a) in enumerate(zip(steps,amps)))
    yy,xx=np.mgrid[0:gh,0:gw];wx=xx*GS+GS/2;wy=yy*GS+GS/2
    N1=fbm(seed+3);N2=fbm(seed+8,(60,30,12),(.5,.35,.15));N3=fbm(seed+14,(120,60,30),(.55,.3,.15));CL=fbm(seed+40,(90,45,22),(.62,.28,.10))
    qx=wx+(N2-.5)*90;qy=wy+(N1-.5)*90
    road_d=np.full(wx.shape,1e9)
    for r in roads:road_d=np.minimum(road_d,path_d(qx,qy,r))
    trail_d=np.full(wx.shape,1e9)
    for r in trails:trail_d=np.minimum(trail_d,path_d(qx,qy,r))
    water=np.zeros(wx.shape,bool);shore=np.zeros(wx.shape,bool)
    for cx,cy,rx,ry in waters:
        e=((wx-cx+(N2-.5)*240)/rx)**2+((wy-cy+(N1-.5)*240)/ry)**2;water|=e<1;shore|=(e<1.4)
    shore&=~water
    # ---- borda: lado mais próximo define a espessura e o tema da barreira
    dists=np.stack([wy,H-wy,wx,W-wx]);side=np.argmin(dists,axis=0);ed=np.min(dists,axis=0)
    BT=np.choose(side,[band[0],band[1],band[2],band[3]])+(N3-.5)*120;BAND=ed<BT
    # corredores das saídas (sem barreira nem props)
    CORR=np.zeros(wx.shape,bool)
    for e in exits:
        along=wx if e['side'] in(0,1) else wy;depth=dists[e['side']]
        CORR|=(np.abs(along-e['pos'])<180+(N2-.5)*60)&(depth<BT+80)
    ground_near=np.full(wx.shape,1e9)
    for cx,cy in camps:ground_near=np.minimum(ground_near,np.hypot(wx-cx,wy-cy))
    dirt=((road_d<28)|(trail_d<14)|(N2>.8)&(wy>600)|(ground_near<150)|shore)&~water
    img=np.zeros((gh,gw,3));t=smooth(seed+31,8)
    img[:]=GR[None,None,:]*(1-t[...,None])+GR2[None,None,:]*t[...,None]
    img[dirt]=DR;img[shore]=SH
    if ground=='dark':img[~water&~shore]=DFc
    for sd,th in enumerate(side_theme):
        if th=='dark':img[BAND&(side==sd)&~water&~CORR]=DFc
    img[((road_d<26)|(trail_d<12))&~water]=DR;img[water]=WT
    Image.fromarray(img.astype('uint8')).save(f'{A}/{name}_ground.png',optimize=True)
    def gi(x,y):return min(gh-1,max(0,int(y)//GS)),min(gw-1,max(0,int(x)//GS))
    def at(m,x,y):i,j=gi(x,y);return m[i,j]
    P=[]
    def addk(k,x,y,s,r=0,wf=None):
        d=dict(t='k',k=k,x=round(x),y=round(y),s=s)
        if r:d['col']=[[0,0,r]]
        if wf:d['wf']=wf
        P.append(d)
    def vp(n,x,y,col=None):
        d=dict(t='p',id='v_'+n,x=round(x),y=round(y))
        if col:d['col']=col
        P.append(d)
    def spr(i,x,y):P.append(dict(t='p',id=i,x=round(x),y=round(y)))
    camp_d=lambda x,y:min([math.hypot(x-cx,y-cy) for cx,cy in list(camps)+list(lairs)]+[1e9])
    poi_d=lambda x,y:min([math.hypot(x-cx,y-cy) for cx,cy in pois]+[1e9])
    def free(x,y,m=44):return not(at(water,x,y) or (at(shore,x,y) and rr.random()<.7) or at(road_d,x,y)<m or at(trail_d,x,y)<m*.6 or camp_d(x,y)<260 or poi_d(x,y)<200 or at(CORR,x,y))
    def grove(x,y,lo):v=at(CL,x,y);return min(1.0,max(0.0,(v-lo)*7))
    def place_grid(step,fn,jit=.45):
        step=int(step/ math.sqrt(dens))
        for gy in range(40,H-40,step):
            for gx in range(40,W-40,step):
                x=gx+rr.uniform(-1,1)*step*jit;y=gy+rr.uniform(-1,1)*step*jit
                if 40<x<W-40 and 40<y<H-40 and not at(BAND,x,y):fn(x,y)
    def tree(x,y):
        if not free(x,y):return
        f=(.30+at(N3,x,y)*.9)*(.4+at(N1,x,y))*grove(x,y,.56 if fdens<=1 else .40)*fdens
        if hills and hills(x,y)>.2:
            if rr.random()<.45*grove(x,y,.5):spr(rr.choice(TALL_C),x,y)
            return
        if rr.random()<min(.9,f*.78):spr(rr.choice(TALL_C if rr.random()<conifer else TALL_B),x,y)
    def mid(x,y):
        if not free(x,y):return
        r=rr.random();d=grove(x,y,.55)
        if hills and hills(x,y)>.25:
            if r<.42:spr(rr.choice(ROCK),x,y)
            return
        if r<.08+d*.20:spr(rr.choice(BUSH),x,y)
        elif r<.11+d*.20:spr(rr.choice(ROCK[:4]),x,y)
    def flat(x,y):
        if at(water,x,y) or at(CORR,x,y):return
        if rr.random()<.20+.5*max(0,at(CL,x,y)-.5):P.append(dict(t='flat',id=rr.choice(FLATS),x=round(x),y=round(y)))
    place_grid(58,tree);place_grid(74,mid);place_grid(28,flat,.5)
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
        e['rect']=[cx-(300 if s>=2 else 200) if False else 0,0,0,0]
        hw=220
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
        elif th=='mount':
            if r<.5:spr(rr.choice(ROCK),x,y)
            elif r<.8:addk('rock',x,y,rr.randint(110,200),22)
            else:spr(rr.choice(TALL_C),x,y)
        else:
            if r<.6:spr(rr.choice(TALL_C),x,y)
            elif r<.85:spr(rr.choice(TALL_B),x,y)
            else:spr(rr.choice(ROCK),x,y)
    step=int(40/ math.sqrt(dens))
    for gy in range(20,H-20,step):
        for gx in range(20,W-20,step):
            x=gx+rr.uniform(-.5,.5)*step;y=gy+rr.uniform(-.5,.5)*step
            if 0<x<W and 0<y<H and at(BAND,x,y):band_item(x,y,int(at(side,x,y)))
    for gy in range(40,H-40,110):
        for gx in range(40,W-40,110):
            x=gx+rr.uniform(-.4,.4)*110;y=gy+rr.uniform(-.4,.4)*110
            if not(0<x<W and 0<y<H):continue
            sd=int(at(side,x,y))
            if at(BAND,x,y) and side_theme[sd]=='mount' and at(ed,x,y)<at(BT,x,y)*.6 and not at(water,x,y) and not at(CORR,x,y):addk('mount',x,y,rr.randint(190,270),0,1.5)
    wall=[]
    for t_ in range(40,max(W,H)-40,26):
        pts=[]
        if t_<W-40:pts+=[(t_,.5*at(BT,t_,40),0,t_),(t_,H-.5*at(BT,t_,H-40),1,t_)]
        if t_<H-40:pts+=[(.5*at(BT,40,t_),t_,2,t_),(W-.5*at(BT,W-40,t_),t_,3,t_)]
        for x,y,sd,al in pts:
            if any(e['side']==sd and abs(al-e['pos'])<200 for e in exits):continue
            wall.append([round(x),round(y),24])
    spawns=[]
    if packs:
        tries=0;centers=[]
        while len(centers)<packs and tries<4000:
            tries+=1;x=rr.uniform(500,W-500);y=rr.uniform(500,H-500)
            if at(BAND,x,y) or at(water,x,y) or at(CORR,x,y) or camp_d(x,y)<420:continue
            if any(math.hypot(x-e['rect'][0]-e['rect'][2]/2,y-e['rect'][1]-e['rect'][3]/2)<900 for e in exits):continue
            if any(math.hypot(x-cx,y-cy)<430 for cx,cy in centers):continue
            centers.append((x,y))
        for gi,(cx,cy) in enumerate(centers):
            n=rr.choices([1,2,3,4],[.32,.3,.24,.14])[0]   # isolados, duplas, grupos pequenos (dá para puxar um a um ou agrupar)
            for i in range(n):
                a=i*6.283/n+rr.uniform(-.5,.5);rad=0 if n==1 else 55+10*n;spawns.append([round(cx+math.cos(a)*rad),round(cy+math.sin(a)*rad*.75),gi])
    P.sort(key=lambda p:p['y'])
    exs=[dict(id=e['id'],nm=e['nm'],side=e['side'],toSide=e.get('toSide',-1),x=e['rect'][0],y=e['rect'][1],w=e['rect'][2],h=e['rect'][3],to=e['to'],at=e['at'],ready=e['ready'],msg=e.get('msg','')) for e in exits]
    Z=dict(w=W,h=H,props=P,spawns=spawns,plaza=[0,0,1,1],pond=[0,0,1,1],road=[],start=list(start),boss=[W//2,H//2],gate=list(start),
           region=dict(nome=nome,nv=nv,gs=1/GS,mundo=name,**(region_extra or {})),exits=exs,fx=[],wallc=wall)
    json.dump(Z,open(f'{A}/{name}.json','w'),separators=(',',':'))
    from collections import Counter
    print(name,'spawns',len(spawns),'props',len(P),Counter(p.get('k') or p.get('t') for p in P).most_common(8),'paredes',len(wall),'saídas',[e['id'] for e in exs])

# ---------------------------------------------------------------- Estrada de Brumavale (ligação, Nv 1) — sem NPCs: a cidade ainda está atrás
build('zone_estrada',2200,4200,101,'Estrada de Brumavale','Nv 1',
  roads=[[(1100,4190),(1100,3800),(1000,3200),(1250,2600),(1100,2000),(900,1400),(1100,800),(1100,10)]],trails=[],
  waters=[(1750,2350,330,230)],
  exits=[dict(id='cidade',nm='Brumavale',side=1,pos=1100,to='town',toSide=-1,at=[450,1150],ready=True),
         dict(id='planicie',nm='Planície de Brumavale',side=0,pos=1100,to='zone_planicie',toSide=1,at=[3000,5740],ready=True)],
  camps=[],pois=[(1500,1500)],start=(1100,4000),side_theme=['forest','forest','forest','forest'],band=(330,330,360,360),dens=.9)

# ---------------------------------------------------------------- Planície de Brumavale (zona de caça, Nv 1–3) — 6000×6000
build('zone_planicie',6000,6000,202,'Planície de Brumavale','Nv 1–3',
  roads=[[(3000,5990),(3000,5400),(3100,4600),(2950,3700),(3150,2700),(3050,1700),(3200,700),(3200,10)],
         [(2950,3700),(2100,3500),(1300,3100),(600,2900),(10,2850)],
         [(3100,4600),(2300,5000),(1600,5500),(1300,5990)]],
  trails=[[(3150,3450),(3900,3300),(4800,3300),(5400,3700),(5990,3950)]],
  waters=[(4300,4150,700,430)],
  exits=[dict(id='estrada',nm='Estrada de Brumavale',side=1,pos=3000,to='zone_estrada',toSide=0,at=[1100,160],ready=True),
         dict(id='ponte',nm='Ponte do Rio',side=0,pos=3200,to='zone_ponte',toSide=1,at=[1100,3900],ready=False,msg='Ponte do Rio: caminho em construção.'),
         dict(id='goblins',nm='Floresta dos Goblins',side=2,pos=2850,to='zone_goblins',toSide=3,at=[4860,2500],ready=True),
         dict(id='brejo',nm='Trilha do Brejo',side=1,pos=1300,to='zone_brejo',toSide=0,at=[1100,150],ready=False,msg='Trilha do Brejo: caminho em construção.'),
         dict(id='lago',nm='Margem do Lago (secreta)',side=3,pos=3950,to='zone_lago',toSide=2,at=[500,1000],ready=False,msg='Margem do Lago: caminho em construção.')],
  camps=[(2200,2300),(4300,1900)],pois=[],start=(3000,5740),
  side_theme=['mount','forest','dark','mount'],band=(400,300,420,420),dens=.8,
  hills=lambda x,y:max(0,min(1,(1400-y)/700)),packs=40,pack_n=3,
  region_extra=dict(zlv=1,lv=[1,3],respawn=40,mobs=['rato','javali','rato','lobo','javali']))

# ---------------------------------------------------------------- Floresta dos Goblins (zona de caça, Nv 3–5) — 5000×5000, mata escura
build('zone_goblins',5000,5000,303,'Floresta dos Goblins','Nv 3–5',
  roads=[[(4990,2500),(4200,2450),(3300,2600),(2400,2300),(1500,1650)],
         [(3300,2600),(3000,3400),(2200,3900),(1800,4990)],
         [(2400,2300),(2300,1300),(2500,10)]],trails=[],
  waters=[(3700,3700,380,260)],
  exits=[dict(id='planicie',nm='Planície de Brumavale',side=3,pos=2500,to='zone_planicie',toSide=2,at=[180,2850],ready=True),
         dict(id='lenhadores',nm='Trilha dos Lenhadores',side=0,pos=2500,to='zone_lenhadores',toSide=1,at=[1100,4000],ready=False,msg='Trilha dos Lenhadores: caminho em construção.'),
         dict(id='clareira',nm='Clareira das Ruínas (secreta)',side=1,pos=1800,to='zone_clareira',toSide=0,at=[1000,150],ready=False,msg='Clareira das Ruínas: caminho em construção.')],
  camps=[(4300,2250)],pois=[],lairs=[(1500,1550)],start=(4800,2500),
  side_theme=['dark','dark','dark','forest'],band=(380,380,400,300),dens=.95,fdens=1.55,conifer=.6,ground='dark',packs=44,pack_n=3,
  region_extra=dict(zlv=1,lv=[3,5],respawn=45,boss=dict(x=1500,y=1550,lv=6,aggro=440,respawn=300),minis=[dict(type='skrix',x=3300,y=3200,aggro=420,respawn=240)]))
