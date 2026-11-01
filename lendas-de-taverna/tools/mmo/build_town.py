# Exporta a cidade (lobby) para ../assets: town_ground.png, town_atlas.*, town.json
import os,sys,json,hashlib,shutil
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'town_world.py')).read())
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','mmo','assets')
ground=zs(TG);ground.convert('RGB').save(os.path.join(OUT,'town_ground.png'),optimize=True)
sprs={};props=[]
def reg(img,anc,name=None):
    s=zs(img);a=(int(anc[0]*Z),int(anc[1]*Z))
    k=name or hashlib.md5(s.tobytes()+bytes(str(s.size),'ascii')).hexdigest()[:10]
    sprs.setdefault(k,(s,a));return k
def addp(img,anc,x,y,col=None,**kw):
    d=dict(t='p',id=reg(img,anc),x=round(x*Z),y=round(y*Z));d.update(kw)
    if col:d['col']=[[round(c[0]*Z),round(c[1]*Z),round(c[2]*Z)] for c in col]
    props.append(d)
def house_col(w=96):return [(dx,-4,6) for dx in range(-(w//2)+6,w//2-3,10)]
H_FER=make_house(WALL_WOOD,ROOF_B);H_MER=make_house(WALL_CREAM,ROOF_G);H_ALQ=make_house(WALL_TIMBER,ROOF_G);H_DEC=make_house(WALL_CREAM,ROOF_B)
for (h,x,y) in [(H_FER,60,206),(H_MER,340,206),(H_ALQ,60,392),(H_DEC,340,392)]:addp(h[0],h[1],x,y,house_col())
# estações animadas
fr_a=[reg(f,(32,70),'anv%d'%i) for i,f in enumerate(ANVIL)];props.append(dict(t='anim',fr=fr_a,fps=5,x=round(66*Z),y=round(238*Z),col=[[round(c[0]*Z),round(c[1]*Z),round(c[2]*Z)] for c in [(-18,-3,8),(0,-3,8),(18,-3,8)]]))
ALC=frame_grid(ST+'Alchemy/Alchemy_Table_03-Sheet.png',80,80,24)
fr_l=[reg(f,(40,76),'alc%d'%i) for i,f in enumerate(ALC)];props.append(dict(t='anim',fr=fr_l,fps=5,x=round(66*Z),y=round(424*Z),col=[[round(c[0]*Z),round(c[1]*Z),round(c[2]*Z)] for c in [(-24,-3,8),(-8,-3,8),(8,-3,8),(24,-3,8)]]))
tb=table(44,(190,60,50));addp(tb[0],tb[1],338,240,[(-16,-3,7),(0,-3,7),(16,-3,7)])
addp(BARREL,(BARREL.width//2,BARREL.height-2),310,236,[(0,-3,8)])
# portal
PF=[reg(portal_img,(48,108),'pf%d'%i) for i,portal_img in enumerate([None]*0)]
import math
def portal_frame(f):
    W,H=96,110;im=Image.new('RGBA',(W,H),(0,0,0,0));d=ImageDraw.Draw(im);cx,cy=48,60
    for r in range(34,4,-2):
        k=r/34;col=(int(90+110*(1-k)),int(70+120*(1-k)),255,int(60+190*(1-k)));d.ellipse((cx-r*.62,cy-r*1.0,cx+r*.62,cy+r*1.0),fill=col)
    for i in range(36):
        a=i*0.52+f*0.5;rr_=6+i*0.8;x=cx+math.cos(a)*rr_*.5;y=cy+math.sin(a)*rr_*.85;d.rectangle((x,y,x+1,y+1),fill=(255,255,255,230))
    for side in (-1,1):
        for yy in range(18,100,8):d.rectangle((cx+side*30-5,yy,cx+side*30+5,yy+7),fill=(122,122,132,255),outline=(60,58,68,255))
    for xx in range(cx-34,cx+36,8):d.rectangle((xx,8,xx+7,17),fill=(140,140,152,255),outline=(60,58,68,255))
    for xx in range(cx-24,cx+26,8):d.rectangle((xx,16,xx+7,23),fill=(122,122,132,255),outline=(60,58,68,255))
    return im
PF=[reg(portal_frame(i),(48,108),'pf%d'%i) for i in range(8)]
props.append(dict(t='portal',fr=PF,fps=6,x=round(200*Z),y=round(76*Z),col=[[round(-30*Z),round(-4*Z),round(7*Z)],[round(30*Z),round(-4*Z),round(7*Z)]]))
# decoração
rr=random.Random(5)
def tree():
    t=rr.random();return rr.choice(T_OAK) if t<.5 else rr.choice(T_CON) if t<.8 else rr.choice(T_PIN)
for _ in range(900):
    x=rr.randrange(-10,TWN[0]+10);y=rr.randrange(20,TWN[1]+40)
    if 20<x<TWN[0]-20 and 50<y<TWN[1]-10:continue
    if any(abs(p.get('_x',-999)-x)<14 and abs(p.get('_y',-999)-y)<8 for p in props[-60:]):continue
    t=tree();addp(t,(t.width//2,t.height-2),x,y,[(0,-2,6)],_x=x,_y=y)
for (x,y) in [(118,262),(282,262),(140,196),(260,196),(150,320),(250,320)]:
    lamp=Image.new('RGBA',(10,40),(0,0,0,0));ld=ImageDraw.Draw(lamp);ld.rectangle((4,12,5,39),fill=(60,44,30,255));ld.rectangle((1,3,8,13),fill=(40,30,20,255));ld.rectangle((2,4,7,11),fill=(255,214,120,255))
    addp(lamp,(5,39),x,y,[(0,-2,3)],lamp=True)
for (x,y) in [(110,150),(290,150),(110,350),(290,350),(30,300),(370,300)]:
    b=rr.choice(BUSH);addp(b,(b.width//2,b.height-3),x,y,[(-6,-3,6),(6,-3,6)])
for k,b in enumerate(BAN):addp(b,(b.width//2,b.height-2),150+k*50,100,[(0,-2,5)])
for (x,y) in [(150,310),(250,310),(90,296),(310,296)]:addp(FENCE,(FENCE.width//2,FENCE.height-2),x,y,[(dx,-3,6) for dx in (-20,-10,0,10,20)]) if False else None
for n in range(120):
    x=rr.randrange(30,TWN[0]-30);y=rr.randrange(70,TWN[1]-20)
    if ((x-200)/100)**2+((y-252)/70)**2<1:continue
    s=rr.choice(VS[-30:]);props.append(dict(t='flat',id=reg(s,(s.width//2,s.height)),x=round(x*Z),y=round(y*Z)))
for p in props:p.pop('_x',None);p.pop('_y',None)
# atlas
items=sorted(sprs.items(),key=lambda kv:-kv[1][0].height);Wd_=1024;x=y=sh=0;pos={}
for k,(im,a) in items:
    if x+im.width+1>Wd_:x=0;y+=sh+1;sh=0
    pos[k]=(x,y,im.width,im.height,a[0],a[1]);x+=im.width+1;sh=max(sh,im.height)
atlas=Image.new('RGBA',(Wd_,y+sh+1),(0,0,0,0))
for k,(im,a) in items:atlas.alpha_composite(im,pos[k][:2])
atlas.save(os.path.join(OUT,'town_atlas.png'),optimize=True);json.dump({k:list(v) for k,v in pos.items()},open(os.path.join(OUT,'town_atlas.json'),'w'))
S=lambda v:round(v*Z)
town=dict(w=ground.width,h=ground.height,props=props,start=[S(200),S(312)],
  portal=dict(x=S(200),y=S(76),stand=[S(200),S(76+34)]),
  npcs=[dict(id='fer',nm='Ferreiro',sh='guardiao',x=S(108),y=S(246),ic='anvil',row=1,win='forja'),
        dict(id='mer',nm='Mercador',sh='bardo',x=S(296),y=S(250),ic='coins',row=3,win='mercador'),
        dict(id='alq',nm='Alquimista',sh='mago',x=S(112),y=S(434),ic='health-potion',row=1,win='alquimista'),
        dict(id='gua',nm='Guarda do Portal',sh='guarda',x=S(200),y=S(122),ic='treasure-map',row=2,win='portal')],
  vill=[dict(sh='pov_f',x=S(170),y=S(270)),dict(sh='ladino_b',x=S(240),y=S(290))])
json.dump(town,open(os.path.join(OUT,'town.json'),'w'),separators=(',',':'))
CH=os.path.join(OUT,'chars')
for n in ['bardo','guardiao','mago','guarda','pov_f','ladino_b']:
    for k in ['walk','hurt']:
        f=f'/tmp/idle/{n}__{k}.png'
        if os.path.exists(f):shutil.copy(f,CH)
print('town props',len(props),'sprites',len(sprs),'atlas',atlas.size)
