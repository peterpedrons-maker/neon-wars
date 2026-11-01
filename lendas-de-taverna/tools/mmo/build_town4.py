"""Cidade: terreno do pack (Pixel Crawler) + prédios gerados por IA, um a um (tools/mmo/bld/*_key.png, fundo já removido).
Cada prédio: sprite único ordenado por y, colisão preenchendo a pegada (só a porta fica livre), porta clicável, emissores de efeitos (GSAP).
Uso (na pasta lendas-de-taverna/tools/mmo):  /usr/bin/python3 build_town4.py     -> reescreve town.json/town_ground.png/town_atlas.*  (interiores não mudam)"""
import os,sys,json,hashlib
import numpy as np
HERE=os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE,'town_world.py')).read())
exec(open(os.path.join(HERE,'interiors.py')).read())
OUT=os.path.join(HERE,'..','..','mmo','assets')
S=lambda v:round(v*Z)
def make_atlas(sprs,name):
    items=sorted(sprs.items(),key=lambda kv:-kv[1][0].height);Wd_=1024;x=y=sh=0;pos={}
    for k,(im,a) in items:
        if x+im.width+1>Wd_:x=0;y+=sh+1;sh=0
        pos[k]=(x,y,im.width,im.height,a[0],a[1]);x+=im.width+1;sh=max(sh,im.height)
    atlas=Image.new('RGBA',(Wd_,y+sh+1),(0,0,0,0))
    for k,(im,a) in items:atlas.alpha_composite(im,pos[k][:2])
    atlas.save(os.path.join(OUT,name+'.png'),optimize=True);json.dump({k:list(v) for k,v in pos.items()},open(os.path.join(OUT,name+'.json'),'w'))
    return atlas.size
class Reg:
    def __init__(s):s.sprs={};s.props=[]
    def reg(s,img,anc,name=None):
        z=zs(img);a=(int(anc[0]*Z),int(anc[1]*Z));k=name or hashlib.md5(z.tobytes()+bytes(str(z.size),'ascii')).hexdigest()[:10];s.sprs.setdefault(k,(z,a));return k
    def addp(s,img,anc,x,y,col=None,**kw):
        d=dict(t='p',id=s.reg(img,anc),x=S(x),y=S(y));d.update(kw)
        if col:d['col']=[[S(c[0]),S(c[1]),S(c[2])] for c in col]
        s.props.append(d)
    def flat(s,img,anc,x,y):s.props.append(dict(t='flat',id=s.reg(img,anc),x=S(x),y=S(y)))
    def raw(s,img,anc,name):s.sprs[name]=(img,(round(anc[0]),round(anc[1])));return name
# ---------------- terreno (pack) ----------------
TWN=(600,840)
ROW=[290,477,660]            # ruas laterais (px do pack)
def town():
    r=random.Random(7);w=Image.new('RGBA',(WW,WH),(0,0,0,255));fill(w,(0,0,WW,WH),GR,r)
    roads=[[(300,70),(300,300),(300,480),(300,830)]]+[[(168,y),(300,y),(432,y)] for y in ROW]
    pts=[]
    for rd in roads:pts+=poly_pts(rd,12)
    paint_region(w,union_mask(pts,r),DR,r,edge=(112,78,48,255),rim=(40,92,24,255))
    cx,cy,rx,ry=300,ROW[1]+8,52,36   # praça
    for yy in range(0,WH,16):
        for xx in range(0,WW,16):
            if ((xx+8-cx)/rx)**2+((yy+8-cy)/ry)**2<1:w.alpha_composite(r.choice(STN),(xx,yy))
    for yy in range(26,130,16):
        for xx in range(236,364,16):
            if ((xx+8-300)/60)**2+((yy+8-92)/44)**2<1:w.alpha_composite(r.choice(STN),(xx,yy))
    return w.crop((0,0,TWN[0],TWN[1]))
GT=town();ground=zs(GT)
R_=Reg();rr=random.Random(5)
# ---------------- prédios de IA ----------------
SC=0.27                                   # px do mundo por px da imagem (1024)
BASE_Y=880                                # linha do chão da fachada na imagem
WALL=(135,885)                            # paredes (px da imagem)
BX=dict(left=250,right=650)               # centro (x) em px do mundo
BUILD=[('fer','Ferreiro','anvil','left',0),('mer','Mercador','scales','right',0),
       ('mes','Mestre de Classe','holy-symbol','left',1),('alq','Alquimista','health-potion','right',1),
       ('lei','Leilão','coins','left',2),('cof','Cofre','locked-chest','right',2)]
BASEW=[ROW[i]*Z+16 for i in range(3)]     # y (mundo) onde a porta encontra a rua
def premul_resize(im,sz):
    a=np.array(im).astype(float);al=a[...,3:4]/255;rgb=a[...,:3]*al
    pm=Image.fromarray(np.dstack([rgb,a[...,3:4]]).astype('uint8'),'RGBA')
    ch=[pm.getchannel(i).resize(sz,Image.LANCZOS) for i in range(4)]
    r=np.stack([np.array(c).astype(float) for c in ch],-1);A=r[...,3:4]
    rgb=np.where(A>8,np.clip(r[...,:3]/np.maximum(A,1)*255,0,255),0);A=np.where(A>110,255,0)   # borda dura (pixel art)
    return Image.fromarray(np.dstack([rgb,A]).astype('uint8'),'RGBA')
doors=[];FX=[];BI={}
for (k,nm,ic,side,row) in BUILD:
    im=Image.open(os.path.join(HERE,'bld',k+'_key.png')).convert('RGBA');bb=im.getbbox();im=im.crop(bb)
    ax,ay=512-bb[0],BASE_Y-bb[1]
    sz=(round(im.width*SC),round(im.height*SC));spr=premul_resize(im,sz)
    cxw=BX[side];byw=BASEW[row]-22;ax_s,ay_s=ax*SC,ay*SC
    name='b_'+k;sid=R_.raw(spr,(ax_s,ay_s),name)
    x0,x1=(WALL[0]-512)*SC,(WALL[1]-512)*SC;hgt=ay_s+10           # altura útil até o topo
    cols=[]
    for dx in np.arange(x0+6,x1-5,14):                              # fileira da frente (porta livre)
        if abs(dx)<30:continue
        cols.append([round(float(dx)),-4,9])
    yo=-30
    while yo>-(hgt*.82):                                            # miolo (inclui atrás da porta)
        for dx in np.arange(x0+8,x1-6,22):cols.append([round(float(dx)),yo,13])
        yo-=18
    R_.props.append(dict(t='p',id=sid,x=round(cxw),y=round(byw),col=cols))
    BI[k]=(cxw,byw)
    doors.append(dict(id=k,nm=nm,x=round(cxw),y=round(byw+6),w=64,h=82,room='int_'+k,ic=ic))
    c=lambda ix,iy:(round(cxw+(ix-512)*SC),round(byw+(iy-BASE_Y)*SC))
    E=lambda kind,ix,iy,**kw:FX.append(dict(k=kind,x=c(ix,iy)[0],y=c(ix,iy)[1],**kw))
    if k=='fer':
        E('smoke',783,110);E('glow',270,740,col='#ff8a2a',r=54,lo=.45,hi=.9,fl=1);E('glow',515,780,col='#ff9a3a',r=26,lo=.4,hi=.8,fl=1);E('spark',270,760,col='#ffb347')
    if k=='mer':E('lamp',95,690,col='#ffc860',r=44)
    if k=='alq':
        E('smoke',790,110,col='#a9ffb4');E('glow',790,335,col='#7dff8a',r=50,lo=.35,hi=.75);E('bubble',950,745,col='#7dff8a');E('glow',950,745,col='#7dff8a',r=34,lo=.3,hi=.6)
    if k=='cof':
        for ix in (198,826):E('fire',ix,820,r=52)
    if k=='mes':
        for ix in (357,660):E('fire',ix,672,r=40)
        E('sparkle',510,170,col='#ffe27a');E('glow',512,440,col='#ffd070',r=64,lo=.25,hi=.5)
    if k=='lei':E('sparkle',505,170,col='#ffe27a')
# portal
def portal_frame(f):
    Wd,Hh=96,110;im=Image.new('RGBA',(Wd,Hh),(0,0,0,0));d=ImageDraw.Draw(im);cx,cy=48,60
    for r_ in range(34,4,-2):
        k=r_/34;d.ellipse((cx-r_*.62,cy-r_*1.0,cx+r_*.62,cy+r_*1.0),fill=(int(90+110*(1-k)),int(70+120*(1-k)),255,int(60+190*(1-k))))
    for i in range(36):
        a=i*0.52+f*0.5;rr_=6+i*0.8;xx=cx+math.cos(a)*rr_*.5;yy=cy+math.sin(a)*rr_*.85;d.rectangle((xx,yy,xx+1,yy+1),fill=(255,255,255,230))
    for side in (-1,1):
        for yy in range(18,100,8):d.rectangle((cx+side*30-5,yy,cx+side*30+5,yy+7),fill=(122,122,132,255),outline=(60,58,68,255))
    for xx in range(cx-34,cx+36,8):d.rectangle((xx,8,xx+7,17),fill=(140,140,152,255),outline=(60,58,68,255))
    for xx in range(cx-24,cx+26,8):d.rectangle((xx,16,xx+7,23),fill=(122,122,132,255),outline=(60,58,68,255))
    return im
PF=[R_.reg(portal_frame(i),(48,108),'pf%d'%i) for i in range(8)]
R_.props.append(dict(t='portal',fr=PF,fps=6,x=S(300),y=S(86),col=[[S(-30),S(-4),S(7)],[S(30),S(-4),S(7)]]))
FX.append(dict(k='portal',x=S(300),y=S(86)-44))
# fonte (praça)
def fountain():
    im=Image.new('RGBA',(80,70),(0,0,0,0));d=ImageDraw.Draw(im)
    d.ellipse((2,20,77,66),fill=(70,68,80,255));d.ellipse((6,22,73,58),fill=(150,148,160,255));d.ellipse((10,26,69,54),fill=(90,170,230,255));d.ellipse((16,30,63,50),fill=(130,200,245,255))
    d.rectangle((35,6,44,40),fill=(150,148,160,255),outline=(70,68,80,255));d.ellipse((28,2,51,12),fill=(150,148,160,255),outline=(70,68,80,255))
    return im,(40,60)
fi,fa=fountain();FXY=(300,ROW[1]+8)
R_.addp(fi,fa,FXY[0],FXY[1],[(-26,-10,8),(0,-10,8),(26,-10,8)])
FX.append(dict(k='fountain',x=S(FXY[0]),y=S(FXY[1])-66))
# postes ao longo da rua central
lamp=Image.new('RGBA',(10,40),(0,0,0,0));ld=ImageDraw.Draw(lamp);ld.rectangle((4,12,5,39),fill=(60,44,30,255));ld.rectangle((1,3,8,13),fill=(40,30,20,255));ld.rectangle((2,4,7,11),fill=(255,214,120,255))
for (x,y) in [(268,200),(332,200),(268,390),(332,390),(268,570),(332,570),(268,730),(332,730)]:
    R_.addp(lamp,(5,39),x,y,[(0,-2,3)]);FX.append(dict(k='lamp',x=S(x),y=S(y)-30,col='#ffd278',r=42))
# arbustos e barris nas bordas
for (x,y) in [(90,170),(510,170),(90,330),(510,330),(90,520),(510,520),(90,700),(510,700),(200,130),(400,130)]:
    b=rr.choice(BUSH);R_.addp(b,(b.width//2,b.height-3),x,y,autocol(b))
for (x,y) in [(96,250),(504,250),(96,430),(504,430),(96,610),(504,610)]:R_.addp(BARREL,(BARREL.width//2,BARREL.height-2),x,y,autocol(BARREL))
for k,b in enumerate(BAN):R_.addp(b,(b.width//2,b.height-2),240+k*60,60,autocol(b))
# árvores: anel de borda
def tree():
    t=rr.random();return rr.choice(T_OAK)
placed=[]
def okpos(x,y,rad):return all((x-a)**2+(y-b)**2>=(rad+c)**2 for (a,b,c) in placed)
for _ in range(2600):
    x=rr.randrange(-14,TWN[0]+14);y=rr.randrange(20,TWN[1]+40)
    if 38<x<TWN[0]-38 and 64<y<TWN[1]-22:continue
    if not okpos(x,y,16):continue
    t=tree();placed.append((x,y,16));R_.addp(t,(t.width//2,t.height-2),x,y,[(0,-2,6)])
for n in range(280):
    x=rr.randrange(24,TWN[0]-24);y=rr.randrange(60,TWN[1]-20)
    s=rr.choice(VS[-30:]);R_.flat(s,(s.width//2,s.height),x,y)
# vaga-lumes
for i in range(9):FX.append(dict(k='firefly',x=S(rr.randrange(60,540)),y=S(rr.randrange(120,TWN[1]-60))))
R_.props.sort(key=lambda p:p['y'])
Wd,Hd=ground.width,ground.height
npcs=[dict(id='gua',nm='Guarda do Portal',sh='guarda',x=S(300),y=S(132),ic='treasure-map',row=2,win='portal')]
vill=[dict(sh='pov_f',x=S(262),y=S(ROW[1]+40)),dict(sh='ladino_b',x=S(345),y=S(ROW[2]+30)),dict(sh='bardo',x=S(300),y=S(ROW[0]-40))]
town_json=dict(w=Wd,h=Hd,props=R_.props,start=[S(300),S(ROW[1]-60)],portal=dict(x=S(300),y=S(86),stand=[S(300),S(86+36)]),npcs=npcs,vill=vill,doors=doors,fx=FX)
ground.convert('RGB').save(os.path.join(OUT,'town_ground.png'),optimize=True)
json.dump(town_json,open(os.path.join(OUT,'town.json'),'w'),separators=(',',':'))
print('town',Wd,Hd,make_atlas(R_.sprs,'town_atlas'),len(R_.props),'fx',len(FX))
# debug
dbg=ground.copy().convert('RGBA');d=ImageDraw.Draw(dbg)
at=Image.open(os.path.join(OUT,'town_atlas.png'));aj=json.load(open(os.path.join(OUT,'town_atlas.json')))
for p in R_.props:
    a=aj.get(p.get('id'))
    if a and p['t']=='p' and a[3]>=22:dbg.alpha_composite(at.crop((a[0],a[1],a[0]+a[2],a[1]+a[3])),(p['x']-a[4],p['y']-a[5]))
    for c in p.get('col',[]):d.ellipse((p['x']+c[0]-c[2],p['y']+c[1]-c[2],p['x']+c[0]+c[2],p['y']+c[1]+c[2]),outline=(255,0,0,200))
for dr in doors:d.rectangle((dr['x']-4,dr['y']-4,dr['x']+4,dr['y']+4),fill=(255,255,0,255))
for f in FX:d.ellipse((f['x']-3,f['y']-3,f['x']+3,f['y']+3),fill=(0,255,255,255))
os.makedirs('/tmp/mock',exist_ok=True);dbg.save('/tmp/mock/town4_debug.png')
