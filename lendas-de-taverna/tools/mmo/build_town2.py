"""Cidade grande + interiores das casas (Pixel Crawler). Uso: PACK_DIR=<pack> /usr/bin/python3 build_town2.py  (na pasta tools/mmo)"""
import os,sys,json,hashlib
HERE=os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE,'town_world.py')).read())
exec(open(os.path.join(HERE,'interiors.py')).read())
OUT=os.path.join(HERE,'..','..','mmo','assets');ICO=os.path.join(HERE,'..','..','assets','ui-icons')
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
# ---------------- casas ----------------
def glyph(name,col):
    g=Image.open(os.path.join(ICO,name+'.png')).convert('RGBA');px=g.load()
    for yy in range(g.height):
        for xx in range(g.width):
            if px[xx,yy][3]>40:px[xx,yy]=col+(255,)
            else:px[xx,yy]=(0,0,0,0)
    return g
def house(wall,roof,ic,tint):
    ww,wh=wall.size;rw,rh=roof.size;W=rw+16;H=rh+wh+6
    im=Image.new('RGBA',(W,H),(0,0,0,0));d=ImageDraw.Draw(im)
    wx=(W-ww)//2;wy=rh-12;base=wy+wh
    d.ellipse((wx-6,base-8,wx+ww+6,base+8),fill=(0,0,0,70))             # sombra
    im.alpha_composite(wall,(wx,wy))
    d.rectangle((wx-3,base-6,wx+ww+2,base),fill=(96,92,100,255),outline=(52,50,60,255)) # soleira de pedra
    # janelas com persiana e floreira
    for fx in (wx+14,wx+ww-34):
        d.rectangle((fx,wy+14,fx+20,wy+36),fill=(52,32,18,255));d.rectangle((fx+2,wy+16,fx+18,wy+34),fill=(150,210,240,255));d.line((fx+10,wy+16,fx+10,wy+34),fill=(52,32,18,255));d.line((fx+2,wy+25,fx+18,wy+25),fill=(52,32,18,255))
        d.rectangle((fx-4,wy+14,fx-1,wy+36),fill=tint);d.rectangle((fx+21,wy+14,fx+24,wy+36),fill=tint)
        d.rectangle((fx-2,wy+36,fx+22,wy+41),fill=(104,70,42,255));
        for k in range(5):d.rectangle((fx+k*4,wy+34,fx+k*4+2,wy+37),fill=((220,70,80,255),(240,200,70,255),(230,120,200,255))[k%3])
    # porta
    dx=wx+ww//2-12;dy=base-40
    d.rectangle((dx-3,dy-4,dx+27,base),fill=(52,32,18,255));d.rectangle((dx,dy,dx+24,base-1),fill=(30,18,10,255))
    d.rectangle((dx+1,dy+1,dx+23,base-1),fill=(122,82,48,255));d.rectangle((dx+2,dy+2,dx+22,base-1),fill=(138,94,56,255))
    for k in range(4):d.line((dx+6*(k+1),dy+2,dx+6*(k+1),base-2),fill=(96,64,36,255))
    d.rectangle((dx+18,base-20,dx+20,base-17),fill=(240,200,90,255))
    d.rectangle((dx-6,dy-9,dx+30,dy-4),fill=tint);d.rectangle((dx-6,dy-9,dx+30,dy-8),fill=(255,255,255,70))   # toldo
    for k in range(0,37,6):d.rectangle((dx-6+k,dy-4,dx-6+k+2,dy-1),fill=tint)
    # placa pendurada com o ícone
    sx=wx+ww-26;sy=wy-2
    d.line((sx+9,sy-2,sx+9,sy+3),fill=(60,40,24,255));d.rectangle((sx,sy+3,sx+19,sy+21),fill=(60,40,24,255),outline=(30,20,12,255));d.rectangle((sx+2,sy+5,sx+17,sy+19),fill=(214,170,96,255))
    g=glyph(ic,(70,40,20)).resize((14,14),Image.NEAREST);im.alpha_composite(g,(sx+3,sy+6))
    # chaminé + telhado
    ch=Image.new('RGBA',(14,30),(0,0,0,0));cd=ImageDraw.Draw(ch);cd.rectangle((0,4,13,29),fill=(120,100,96,255),outline=(60,50,50,255));cd.rectangle((-1,0,14,5),fill=(90,76,72,255),outline=(50,40,40,255))
    rx0=(W-rw)//2;ra=roof.split()[3].load();gcol=tuple(int(c*.55) for c in roof.resize((1,1),Image.BOX).getpixel((0,0))[:3])+(255,)
    for xx in range(rw):
        yb=-1
        for yy in range(rh-1,-1,-1):
            if ra[xx,yy]>200:yb=yy;break
        if yb>=0 and yb<wy+6:
            d.line((rx0+xx,yb-2,rx0+xx,wy+4),fill=gcol)
    d.rectangle((W//2-6,wy-12,W//2+6,wy-2),fill=(40,26,16,255),outline=(20,12,8,255));d.rectangle((W//2-4,wy-10,W//2+4,wy-4),fill=(120,160,190,255))
    im.alpha_composite(ch,(wx+10,2));im.alpha_composite(roof,(rx0,0))
    return im,(W//2,base+2),(W,H,wx,ww,base)
# ---------------- cidade ----------------
TWN=(600,740)
def town():
    r=random.Random(7);w=Image.new('RGBA',(WW,WH),(0,0,0,255));fill(w,(0,0,WW,WH),GR,r)
    roads=[[(300,70),(300,280),(300,440),(300,740)],[(190,280),(300,280),(410,280)],[(190,440),(300,440),(410,440)],[(190,600),(300,600),(410,600)]]
    pts=[]
    for rd in roads:pts+=poly_pts(rd,12)
    paint_region(w,union_mask(pts,r),DR,r,edge=(112,78,48,255),rim=(40,92,24,255))
    cx,cy,rx,ry=300,440,96,64   # praça
    for yy in range(0,WH,16):
        for xx in range(0,WW,16):
            if ((xx+8-cx)/rx)**2+((yy+8-cy)/ry)**2<1:w.alpha_composite(r.choice(STN),(xx,yy))
    for yy in range(26,130,16):
        for xx in range(236,364,16):
            if ((xx+8-300)/60)**2+((yy+8-92)/44)**2<1:w.alpha_composite(r.choice(STN),(xx,yy))
    return w.crop((0,0,TWN[0],TWN[1]))
GT=town();ground=zs(GT)
R_=Reg();rr=random.Random(5)
BUILD=[('fer',190,280,WALL_WOOD,ROOF_B,'anvil',(190,60,50),'Ferreiro'),('mer',410,280,WALL_CREAM,ROOF_G,'scales',(60,120,200),'Mercador'),
 ('alq',190,440,WALL_TIMBER,ROOF_G,'health-potion',(70,170,90),'Alquimista'),('mes',410,440,WALL_CREAM,ROOF_B,'holy-symbol',(200,170,60),'Mestre de Classe'),
 ('cof',190,600,WALL_WOOD,ROOF_G,'locked-chest',(150,90,200),'Cofre'),('lei',410,600,WALL_TIMBER,ROOF_B,'coins',(220,140,50),'Leilão')]
doors=[];META=json.load(open(os.path.join(HERE,'b3d','out','meta.json')))
def outline(im,col=(24,14,8,255)):
    a=im.split()[3];dil=a.filter(ImageFilter.MaxFilter(3));ol=Image.new('RGBA',im.size,col);out=Image.new('RGBA',im.size,(0,0,0,0));out.paste(ol,(0,0),dil);out.alpha_composite(im);return out
for (k,x,y,wl,rf,ic,tint,nm) in BUILD:
    spr=Image.open(os.path.join(HERE,'b3d','out',k+'.png')).convert('RGBA');m=META[k]
    bb=spr.getbbox();spr=spr.crop((bb[0],bb[1],bb[2],spr.height));ax=m['ax']-bb[0];ay=m['ay']-bb[1]
    spr=outline(spr);ax+=0;ay+=0
    al=spr.split()[3].load();ry=int(min(spr.height-1,ay-5));xs=[xx for xx in range(spr.width) if al[xx,ry]>10];x0,x1=(min(xs),max(xs)) if xs else (0,spr.width)
    col=[(dx-ax,-4,6) for dx in range(x0+4,x1-2,9) if abs(dx-ax)>13]
    R_.addp(spr,(ax,ay+2),x,y,col)
    doors.append(dict(id=k,nm=nm,x=S(x),y=S(y-3),w=S(x1-x0+10),h=S(spr.height-4),room='int_'+k,ic=ic))
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
# fonte
def fountain():
    im=Image.new('RGBA',(80,70),(0,0,0,0));d=ImageDraw.Draw(im)
    d.ellipse((2,20,77,66),fill=(70,68,80,255));d.ellipse((6,22,73,58),fill=(150,148,160,255));d.ellipse((10,26,69,54),fill=(90,170,230,255));d.ellipse((16,30,63,50),fill=(130,200,245,255))
    d.rectangle((35,6,44,40),fill=(150,148,160,255),outline=(70,68,80,255));d.ellipse((28,2,51,12),fill=(150,148,160,255),outline=(70,68,80,255));d.rectangle((38,-0,41,6),fill=(190,230,255,255))
    return im,(40,60)
fi,fa=fountain();R_.addp(fi,fa,300,440,[(-26,-10,8),(0,-10,8),(26,-10,8)])
# postes, arbustos, barris, bancos
lamp=Image.new('RGBA',(10,40),(0,0,0,0));ld=ImageDraw.Draw(lamp);ld.rectangle((4,12,5,39),fill=(60,44,30,255));ld.rectangle((1,3,8,13),fill=(40,30,20,255));ld.rectangle((2,4,7,11),fill=(255,214,120,255))
for (x,y) in [(262,190),(338,190),(262,360),(338,360),(262,520),(338,520),(262,670),(338,670),(214,290),(386,290),(214,450),(386,450),(214,610),(386,610)]:R_.addp(lamp,(5,39),x,y,[(0,-2,3)])
for (x,y) in [(60,200),(540,200),(60,360),(540,360),(60,520),(540,520),(200,120),(400,120),(250,360),(350,360),(250,520),(350,520)]:
    b=rr.choice(BUSH);R_.addp(b,(b.width//2,b.height-3),x,y,autocol(b))
for (x,y) in [(60,280),(540,280),(60,440),(540,440),(60,600),(540,600)]:R_.addp(BARREL,(BARREL.width//2,BARREL.height-2),x,y,autocol(BARREL))
for k,b in enumerate(BAN):R_.addp(b,(b.width//2,b.height-2),240+k*60,60,autocol(b))
# árvores: anel de borda + alguns bosques entre as casas
def tree():
    t=rr.random();return rr.choice(T_OAK) if t<.5 else rr.choice(T_CON) if t<.8 else rr.choice(T_PIN)
placed=[]
def okpos(x,y,rad):
    return all((x-a)**2+(y-b)**2>=(rad+c)**2 for (a,b,c) in placed)
for _ in range(2200):
    x=rr.randrange(-14,TWN[0]+14);y=rr.randrange(20,TWN[1]+40)
    if 44<x<TWN[0]-44 and 70<y<TWN[1]-24:continue
    if not okpos(x,y,16):continue
    t=tree();placed.append((x,y,16));R_.addp(t,(t.width//2,t.height-2),x,y,[(0,-2,6)])
for (x,y) in [(210,150),(390,150),(40,340),(560,340)]:
    if y>TWN[1]-20:continue
    t=rr.choice(T_OAKS+T_SM);R_.addp(t,(t.width//2,t.height-2),x,y,[(0,-2,6)])
for n in range(260):
    x=rr.randrange(24,TWN[0]-24);y=rr.randrange(60,TWN[1]-20)
    s=rr.choice(VS[-30:]);R_.flat(s,(s.width//2,s.height),x,y)
R_.props.sort(key=lambda p:p['y'])
npcs=[dict(id='gua',nm='Guarda do Portal',sh='guarda',x=S(300),y=S(132),ic='treasure-map',row=2,win='portal')]
vill=[dict(sh='pov_f',x=S(250),y=S(390)),dict(sh='ladino_b',x=S(350),y=S(520)),dict(sh='bardo',x=S(300),y=S(330))]
town_json=dict(w=ground.width,h=ground.height,props=R_.props,start=[S(300),S(380)],portal=dict(x=S(300),y=S(86),stand=[S(300),S(86+36)]),npcs=npcs,vill=vill,doors=doors)
ground.convert('RGB').save(os.path.join(OUT,'town_ground.png'),optimize=True)
json.dump(town_json,open(os.path.join(OUT,'town.json'),'w'),separators=(',',':'))
print('town',make_atlas(R_.sprs,'town_atlas'),len(R_.props))
# ---------------- interiores ----------------
IR=Reg()
INFO={'mer':('Bram, o Mercador','bardo','scales','mercador'),'fer':('Brasa, o Ferreiro','guardiao','anvil','forja'),'alq':('Mirela, a Alquimista','mago','health-potion','alquimista'),
 'mes':('Mestre Aurelius','clerigo','holy-symbol','subclasse'),'cof':('Gregor, o Banqueiro','ladino','locked-chest','cofre'),'lei':('Selene, a Leiloeira','pov_f','coins','leilao')}
for i,k in enumerate(['mer','fer','alq','mes','cof','lei']):
    im,props,npc,door=interior(k,i+1);g=zs(im)
    g.convert('RGB').save(os.path.join(OUT,'int_%s_ground.png'%k),optimize=True)
    pl=[]
    for (spr,x,y,col) in sorted(props,key=lambda p:p[2]):
        IR.props=[]
        sid=IR.reg(spr,(spr.width//2,spr.height-1))
        d=dict(t='p',id=sid,x=S(x),y=S(y))
        if col:d['col']=[[S(c[0]),S(c[1]),S(c[2])] for c in col]
        pl.append(d)
    nm,sh,ic,win=INFO[k]
    ax=npc[0];ay=npc[1]
    cy_=[p for p in props if p[0] is SP['counter']];cby=cy_[0][2] if cy_ else ay+40
    n=dict(id=k,nm=nm,sh=sh,x=S(npc[0]),y=S(npc[1]),ic=ic,row=2,win=win,r=S(52),ap=[S(npc[0]),S(cby+18)])
    zone=dict(w=g.width,h=g.height,props=pl,start=[S(IW_//2),S(IH_-46)],ymin=S(64),portal=dict(x=-999,y=-999,stand=[S(IW_//2),S(IH_-46)]),npcs=[n],vill=[],exit=dict(x=S(IW_//2),y=S(IH_-16)),room=k)
    json.dump(zone,open(os.path.join(OUT,'int_%s.json'%k),'w'),separators=(',',':'))
print('interiores',make_atlas(IR.sprs,'int_atlas'))
