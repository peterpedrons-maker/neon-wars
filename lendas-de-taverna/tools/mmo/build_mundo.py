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
GR=np.array([74,138,58]);GR2=np.array([66,124,52]);DR=np.array([136,98,62]);WT=np.array([58,116,214]);SH=np.array([196,176,120]);DFc=np.array([40,100,60]);GVc=np.array([96,84,120]);SWc=np.array([74,92,40])

def seg_d(px,py,a,b):
    ax,ay=a;bx,by=b;dx,dy=bx-ax,by-ay;L=dx*dx+dy*dy or 1;t=np.clip(((px-ax)*dx+(py-ay)*dy)/L,0,1);return np.hypot(px-(ax+t*dx),py-(ay+t*dy))
def path_d(px,py,pts):
    d=np.full(px.shape,1e9)
    for a,b in zip(pts,pts[1:]):d=np.minimum(d,seg_d(px,py,a,b))
    return d

def build(name,W,H,seed,nome,nv,roads,trails,waters,exits,camps,pois,start,side_theme,band=(380,380,380,380),dens=1.0,hills=None,packs=0,lairs=(),fdens=1.0,conifer=.3,ground=None,region_extra=None,pack_n=3,gates=(),dead=0.0,shrines=(),wxw=None):
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
    GCOL={'dark':DFc,'grave':GVc,'swamp':SWc}
    if ground in GCOL:img[~water&~shore]=GCOL[ground]
    for sd,th in enumerate(side_theme):
        if th in('dark','grave','swamp'):img[BAND&(side==sd)&~water&~CORR]={'dark':DFc,'grave':GVc,'swamp':SWc}[th]
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
    camp_d=lambda x,y:min([math.hypot(x-cx,y-cy) for cx,cy in list(camps)+list(lairs)+list(shrines)+[(g['x'],g['y']) for g in gates]]+[1e9])
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
        if rr.random()<min(.9,f*.78):
            if dead and rr.random()<dead:addk('dead',x,y,rr.randint(100,150),7)
            else:spr(rr.choice(TALL_C if rr.random()<conifer else TALL_B),x,y)
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
    def deco(x,y):
        if not free(x,y,50) or any(math.hypot(x-g['x'],y-g['y'])<190 for g in gates):return
        r=rr.random()
        if ground=='grave':
            if r<.36:addk('tombstone',x,y,rr.randint(30,48),9)
            elif r<.46:addk('bones',x,y,22)
            elif r<.52:addk('thorn',x,y,42,10)
        elif ground=='swamp':
            if r<.40:addk('puddle',x,y,rr.randint(30,60))
            elif r<.52:addk('mush',x,y,26)
            elif r<.60:addk('thorn',x,y,40,10)
            elif r<.64:addk('bones',x,y,18)
    if ground in('grave','swamp'):place_grid(72,deco,.5)
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
                for _k in range(rr.randint(1,3)):addk('reed',x+rr.uniform(-22,22),y+rr.uniform(-14,14),rr.randint(34,54))
            elif r<.115:addk('rock',x,y,rr.randint(20,34),8)
            elif r<.17:addk('tuft',x,y,rr.randint(14,20))
        deep=erode(water,3)&~erode(water,14);ys,xs=np.nonzero(deep)
        for i in range(0,len(ys),4):
            if rr.random()<.07:
                x=float(wx[ys[i],xs[i]]);y=float(wy[ys[i],xs[i]]);P.append(dict(t='k',k='lily',x=round(x),y=round(y),s=rr.randint(26,40),lift=.06))
    if ground not in('grave','swamp'):
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
           region=dict(nome=nome,nv=nv,gs=1/GS,mundo=name,ground=ground or '',**({'wx':wxw} if wxw else {}),**(region_extra or {})),exits=exs,fx=[],wallc=wall,**({'gates':[dict(nm=g['nm'],dg=g['dg'],x=g['x'],y=g['y'],r=g.get('r',130)) for g in gates]} if gates else {}))
    json.dump(Z,open(f'{A}/{name}.json','w'),separators=(',',':'))
    from collections import Counter
    print(name,'spawns',len(spawns),'props',len(P),Counter(p.get('k') or p.get('t') for p in P).most_common(8),'paredes',len(wall),'saídas',[e['id'] for e in exs])

# ================================================================ TABELA DE ZONAS E LIGAÇÕES (primeira região, Nv 1–10 + áreas das dungeons)
SIZE=dict(estrada=(2200,4200),planicie=(6000,6000),goblins=(5000,5000),brejo=(2200,4200),ponte=(2200,4200),colinas=(5000,5000),
  desfiladeiro=(2200,4200),passo=(4500,4500),cemiterio=(5000,5000),mortos=(4200,2200),lenhadores=(2200,4200),ogros=(5000,5000),
  brumas=(5000,5000),clareira=(2400,2400),gruta=(2400,2400),lago=(2400,2400),mina=(2400,2400),eremita=(2400,2400),cabana=(2400,2400))
NM=dict(estrada='Estrada de Brumavale',planicie='Planície de Brumavale',goblins='Floresta dos Goblins',brejo='Trilha do Brejo',
  ponte='Ponte do Rio',colinas='Colinas Rochosas',desfiladeiro='Desfiladeiro',passo='Passo da Montanha',cemiterio='Cemitério de Brumavale',
  mortos='Estrada dos Mortos',lenhadores='Trilha dos Lenhadores',ogros='Floresta dos Ogros',brumas='Pântano das Brumas',
  clareira='Clareira das Ruínas (secreta)',gruta='Gruta Aberta (secreta)',lago='Margem do Lago (secreta)',mina='Mina Abandonada (secreta)',
  eremita='Bosque do Eremita (secreto)',cabana='Cabana da Bruxa (secreta)')
OPP={0:1,1:0,2:3,3:2}
# (zona A, lado em A, posição em A, zona B, posição em B) — B usa o lado oposto
LINKS=[('estrada',0,1100,'planicie',3000),('planicie',0,3200,'ponte',1100),('planicie',2,2850,'goblins',2500),('planicie',1,1300,'brejo',1100),
  ('planicie',3,3950,'lago',1200),('goblins',0,2500,'lenhadores',1100),('goblins',1,1800,'clareira',1200),('brejo',1,1100,'brumas',2500),
  ('brejo',3,2100,'eremita',1200),('ponte',0,1100,'colinas',2500),('colinas',3,2500,'cemiterio',2500),('colinas',0,2500,'desfiladeiro',1100),
  ('desfiladeiro',0,1100,'passo',1200),('lenhadores',0,1100,'ogros',2500),('ogros',0,2500,'passo',3300),('cemiterio',3,2500,'mortos',1100),
  ('mortos',3,1100,'passo',2250),('cemiterio',1,2500,'gruta',1200),('passo',3,2250,'mina',1200),('brumas',3,2500,'cabana',1200)]
def _arrive(b,sd,pos):
    W,H=SIZE[b];return {0:[pos,170],1:[pos,H-170],2:[170,pos],3:[W-170,pos]}[sd]
EXL={k:[] for k in SIZE}
for a,sa,pa,b,pb in LINKS:
    sb=OPP[sa]
    EXL[a].append(dict(id=b,nm=NM[b],side=sa,pos=pa,to='zone_'+b,toSide=sb,at=_arrive(b,sb,pb),ready=True))
    EXL[b].append(dict(id=a,nm=NM[a],side=sb,pos=pb,to='zone_'+a,toSide=sa,at=_arrive(a,sa,pa),ready=True))
EXL['estrada'].append(dict(id='cidade',nm='Brumavale',side=1,pos=1100,to='town',toSide=-1,at=[450,1150],ready=True))
EXL['passo'].append(dict(id='cidade2',nm='Cidade 2',side=0,pos=2250,to='zone_cidade2',toSide=1,at=[1100,4000],ready=False,
  msg='Portão do Passo: o guarda só deixa passar a partir do nível 10, com a quest dos chefes (em construção).'))
def auto_roads(name,hub=None):
    W,H=SIZE[name];hub=hub or (W//2,H//2);r_=random.Random(len(name)*7+W);roads=[]
    for e in EXL[name]:
        if e['id']=='cidade':continue
        p=e['pos'];s=e['side']
        P0={0:(p,10),1:(p,H-10),2:(10,p),3:(W-10,p)}[s];P1={0:(p,H*.2),1:(p,H*.8),2:(W*.2,p),3:(W*.8,p)}[s]
        mid=((P1[0]+hub[0])/2+r_.uniform(-140,140),(P1[1]+hub[1])/2+r_.uniform(-140,140));roads.append([P0,P1,mid,hub])
    return roads
# clima por zona (pesos de clear/rain/storm): perto da cidade quase sempre aberto; pântano e cemitério carregados
WX_BY=dict(planicie=dict(clear=6,rain=2),goblins=dict(clear=3,rain=3),brejo=dict(clear=2,rain=4),ponte=dict(clear=3,rain=3),colinas=dict(clear=4,rain=2,storm=1),
  desfiladeiro=dict(clear=3,rain=2,storm=2),passo=dict(clear=3,rain=2,storm=2),cemiterio=dict(clear=2,rain=3,storm=2),mortos=dict(clear=2,rain=3,storm=2),
  lenhadores=dict(clear=3,rain=3),ogros=dict(clear=3,rain=3,storm=1),brumas=dict(clear=1,rain=5,storm=2),clareira=dict(clear=3,rain=2),gruta=dict(rain=3,storm=2),
  lago=dict(clear=3,rain=3),mina=dict(clear=3,rain=2,storm=1),eremita=dict(clear=2,rain=3),cabana=dict(clear=1,rain=4,storm=3))
def Z(name,seed,nv,**kw):
    kw.setdefault('wxw',WX_BY.get(name))
    W,H=SIZE[name];kw.setdefault('roads',auto_roads(name));kw.setdefault('trails',[]);kw.setdefault('waters',[]);kw.setdefault('camps',[])
    kw.setdefault('pois',[]);kw.setdefault('start',(W//2,H//2))
    build('zone_'+name,W,H,seed,NM[name].replace(' (secreta)','').replace(' (secreto)',''),nv,exits=EXL[name],**kw)
MT=['mount','mount','mount','mount']

# ---------------------------------------------------------------- Estrada de Brumavale (ligação, Nv 1) — sem NPCs: a cidade ainda está atrás
Z('estrada',101,'Nv 1',roads=[[(1100,4190),(1100,3800),(1000,3200),(1250,2600),(1100,2000),(900,1400),(1100,800),(1100,10)]],
  waters=[(1750,2350,330,230)],pois=[(1500,1500)],start=(1100,4000),side_theme=['forest','forest','forest','forest'],band=(330,330,360,360),dens=.9)
# ---------------------------------------------------------------- Planície de Brumavale (Nv 1–3)
Z('planicie',202,'Nv 1–3',
  roads=[[(3000,5990),(3000,5400),(3100,4600),(2950,3700),(3150,2700),(3050,1700),(3200,700),(3200,10)],
         [(2950,3700),(2100,3500),(1300,3100),(600,2900),(10,2850)],
         [(3100,4600),(2300,5000),(1600,5500),(1300,5990)]],
  trails=[[(3150,3450),(3900,3300),(4800,3300),(5400,3700),(5990,3950)]],waters=[(4300,4150,700,430)],
  camps=[(2200,2300),(4300,1900)],start=(3000,5740),side_theme=['mount','forest','dark','mount'],band=(400,300,420,420),dens=.8,
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
  roads=[[(1100,10),(1000,700),(1250,1500),(1000,2300),(1200,3200),(1100,4190)],[(2190,2100),(1800,2100),(1200,2100)]],
  waters=[(1700,2000,300,220),(500,3100,260,200)],pois=[(1200,2100)],start=(1100,150),side_theme=['forest','dark','dark','dark'],band=(330,330,360,360),
  dens=.9,fdens=1.2,conifer=.4,ground='dark',packs=10,pack_n=3,region_extra=dict(zlv=1,lv=[3,4],respawn=40,mobs=['lobo','rato','javali','lobo']))
# ---------------------------------------------------------------- Ponte do Rio (ligação, Nv 3–4): rio com vau/ponte no meio
Z('ponte',505,'Nv 3–4',roads=[[(1100,4190),(1050,3300),(1100,2300),(1150,1200),(1100,10)]],waters=[(380,2100,430,150),(1860,2100,470,150)],
  pois=[(1500,2900)],start=(1100,4000),side_theme=['forest','forest','forest','forest'],band=(330,330,360,360),dens=.9,packs=10,
  region_extra=dict(zlv=1,lv=[3,4],respawn=40,mobs=['javali','lobo','ogrinho','javali']))
# ---------------------------------------------------------------- Colinas Rochosas (Nv 4–6)
Z('colinas',606,'Nv 4–6',waters=[(3600,3600,380,240)],camps=[(1700,3400),(3700,1300)],start=(2500,4800),side_theme=MT,band=(420,300,400,420),dens=.8,
  hills=lambda x,y:.75,packs=36,pack_n=3,region_extra=dict(zlv=1,lv=[4,6],respawn=45,mobs=['javali','lobo','gnoll','harpia','gnoll','javbruto']))
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
Z('lago',1616,'Nv 2–3',waters=[(1200,1250,500,330)],pois=[(1200,500)],start=(300,1200),**{**SEC,'side_theme':['forest']*4},region_extra=dict(zlv=1,lv=[2,3],respawn=40,mobs=['rato','javali','lobo']))
Z('mina',1717,'Nv 7–8',pois=[(1200,1200)],start=(300,1200),**{**SEC,'side_theme':MT},hills=lambda x,y:.8,region_extra=dict(zlv=1,lv=[7,8],respawn=45,mobs=['bandido','gnoll','morcego']))
Z('eremita',1818,'Nv 3–4',pois=[(1200,1200)],start=(300,1200),**{**SEC,'ground':'dark','fdens':1.4},region_extra=dict(zlv=1,lv=[3,4],respawn=40,mobs=['lobo','aranha','cogumelo']))
Z('cabana',1919,'Nv 10–11',waters=[(1500,1500,320,220)],pois=[(1000,1200)],start=(300,1200),**{**SEC,'side_theme':['swamp']*4,'ground':'swamp','dead':.8,'fdens':.5},
  region_extra=dict(zlv=4,lv=[10,11],respawn=45,mobs=['homemrato','cultlodo','sapo','afogado']))
