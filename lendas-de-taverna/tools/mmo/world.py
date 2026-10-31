# Gerado a partir dos scripts de mockup: constroi o mapa da zona 1 com o pack Pixel Crawler (Anokolisa).
# Uso: PACK_DIR=<pasta do pack> python3 build_mmo_assets.py
from PIL import Image,ImageDraw
import numpy as np, glob, os
from scipy import ndimage
import os
P=os.environ.get('PACK_DIR','/tmp/pc/Pixel Crawler - Free Pack')+'/'
def L(p):return Image.open(P+p).convert('RGBA')
def slice_sprites(im,min_px=12,dil=2):
    a=np.array(im)[:,:,3]>0
    lab,n=ndimage.label(ndimage.binary_dilation(a,iterations=dil))
    out=[]
    for i,sl in enumerate(ndimage.find_objects(lab)):
        y,x=sl;sub=im.crop((x.start,y.start,x.stop,y.stop))
        m=(lab[sl]==i+1)
        mm=Image.fromarray((np.kron(m,np.ones((1,1)))*255).astype('uint8'))
        sub=Image.composite(sub,Image.new('RGBA',sub.size,(0,0,0,0)),mm) if False else sub
        if (np.array(sub)[:,:,3]>0).sum()>=min_px:out.append(sub)
    out.sort(key=lambda s:0)
    return out
def sheet_contact(items,W=1100,pad=6,bg=(88,150,60,255),label=True):
    x=y=0;rh=0;pos=[]
    for k,s in enumerate(items):
        if x+s.width>W:x=0;y+=rh+pad+10;rh=0
        pos.append((x,y));x+=s.width+pad;rh=max(rh,s.height)
    H=y+rh+20;im=Image.new('RGBA',(W,H),bg);d=ImageDraw.Draw(im)
    for k,(s,(x,y)) in enumerate(zip(items,pos)):
        im.alpha_composite(s,(x,y+8));d.text((x,y-1),str(k),fill=(255,255,0,255))
    return im
def runs(v):
    r=[];s=None
    for i,x in enumerate(v):
        if x and s is None:s=i
        if not x and s is not None:r.append((s,i));s=None
    if s is not None:r.append((s,len(v)))
    return r
def split_grid(im,min_px=30):
    a=np.array(im)[:,:,3]>0;out=[]
    for (y0,y1) in runs(a.any(1)):
        for (x0,x1) in runs(a[y0:y1].any(0)):
            sub=im.crop((x0,y0,x1,y1))
            if (np.array(sub)[:,:,3]>0).sum()>=min_px:out.append(sub)
    return out

import random, math
FLT=L('Environment/Tilesets/Floors_Tiles.png');WT=L('Environment/Tilesets/Water_tiles.png')
def tile(im,tx,ty):return im.crop((tx*16,ty*16,tx*16+16,ty*16+16))
GR=[tile(FLT,tx,10) for tx in (1,2,3)]
DR=[tile(FLT,tx,10) for tx in (11,12,13)]
WR=[WT.crop((16+i*16,112,32+i*16,128)) for i in range(3)]
STN=[tile(FLT,tx,ty) for tx in (16,17,18) for ty in (0,1,2)]
RING=[FLT.crop((0,0,80,80)),FLT.crop((0,80,80,160))]
DRING=[FLT.crop((160,0,240,80)),FLT.crop((160,80,240,160))]
def fill(im,box,tiles,rnd):
    for y in range(box[1],box[3],16):
        for x in range(box[0],box[2],16):im.alpha_composite(rnd.choice(tiles),(x,y))
def hole_mask(ring):
    a=np.array(ring)[:,:,3]==0
    lab,n=ndimage.label(a);c=lab[ring.height//2,ring.width//2]
    return Image.fromarray(((lab==c)*255).astype('uint8'))
HM=[hole_mask(r) for r in RING]
def clearing(world,x,y,rnd,tiles=None,ring=None):
    tiles=tiles or DR;k=rnd.randrange(2)
    layer=Image.new('RGBA',(80,80),(0,0,0,0));fill(layer,(0,0,80,80),tiles,rnd)
    world.paste(layer,(x,y),HM[k]);world.alpha_composite(RING[k],(x,y))

from PIL import ImageFont, ImageFilter, ImageChops
import os
import numpy as np
LW,LH,SC=270,480,2            # vista lógica e escala
WW,WH=720,960
R=random.Random(11)
# ---------------- sprites ----------------
def frames(path,fw,fh):
    im=L(path);n=im.width//fw;return [im.crop((i*fw,0,(i+1)*fw,fh)) for i in range(n)]
def anchor_for(frs):
    bot=max((f.getbbox() or (0,0,0,0))[3] for f in frs);return (frs[0].width//2,bot)
def flipall(frs):return [f.transpose(Image.FLIP_LEFT_RIGHT) for f in frs]
def trim(s):
    b=s.getbbox();return s.crop(b) if b else s
MOBP='Entities/Mobs/'
def mobset(folder,name,dh=64):
    base=MOBP+folder+'/'+name+'/'
    run=frames(base+'Run/Run-Sheet.png',64,64);idle=frames(base+'Idle/Idle-Sheet.png',32,32)
    dd=L(base+'Death/Death-Sheet.png');death=[dd.crop((i*64,0,(i+1)*64,dd.height)) for i in range(dd.width//64)]
    return dict(run=run,runL=flipall(run),idle=idle,idleL=flipall(idle),death=death,deathL=flipall(death),anc=anchor_for(run),dh=dd.height)
MOBS={'orc':mobset('Orc Crew','Orc'),'orcw':mobset('Orc Crew','Orc - Warrior'),'orcr':mobset('Orc Crew','Orc - Rogue'),'orcs':mobset('Orc Crew','Orc - Shaman'),
      'skw':mobset('Skeleton Crew','Skeleton - Warrior'),'skr':mobset('Skeleton Crew','Skeleton - Rogue'),'skm':mobset('Skeleton Crew','Skeleton - Mage')}
KN=dict(run=frames("Entities/Npc's/Knight/Run/Run-Sheet.png",64,64),idle=frames("Entities/Npc's/Knight/Idle/Idle-Sheet.png",32,32))
KN['runL']=flipall(KN['run']);KN['idleL']=flipall(KN['idle']);KN['anc']=anchor_for(KN['run'])
# --------------- cenário ----------------
def trees_from(path,keep):
    s=split_grid(L(path),30);return [s[i] for i in keep if i<len(s)]
T_OAK=trees_from('Environment/Props/Static/Trees/Model_01/Size_04.png',[0,1,2,3,5,6,7,8])
T_CON=trees_from('Environment/Props/Static/Trees/Model_02/Size_04.png',[0,1,3,4])
T_PIN=trees_from('Environment/Props/Static/Trees/Model_03/Size_03.png',[0,1,3,4])
T_SM=trees_from('Environment/Props/Static/Trees/Model_02/Size_03.png',[0,1,3,4])
_o=L('Environment/Props/Static/Trees/Model_01/Size_03.png')
T_OAKS=[trim(_o.crop((c*48,r*96,c*48+48,r*96+96))) for r in (0,1) for c in (0,1)]
RK=slice_sprites(L('Environment/Props/Static/Rocks.png'));ROCK_BIG=[RK[i] for i in (3,4,5,6,38,39)];ROCK_SM=[RK[i] for i in (1,2,7,8,9,10,11,12)]
veg=L('Environment/Props/Static/Vegetation.png');BUSH=split_grid(veg.crop((0,0,200,150)),50)
VS=[s for s in slice_sprites(veg,6,1) if s.width<=18 and s.height<=18]
_C=slice_sprites(L('Environment/Structures/Buildings/Props.png'))+slice_sprites(L('Environment/Props/Static/Furniture.png'))[:40]
FENCE=_C[4];BARREL=_C[9]
BFIRE=frames('Environment/Structures/Stations/Bonfire/Bonfire_02-Sheet.png',32,32);FIRE=frames('Environment/Structures/Stations/Bonfire/Fire_01-Sheet.png',32,48)
BAN=[slice_sprites(L('Environment/Props/Static/Dungeon_Props.png'))[i] for i in (10,11,12)]
GR_AREA=(0,0,WW,WH)
ROAD=[(150,420),(200,385),(260,350),(300,300),(335,255),(358,200),(360,150)]
ROAD2=[(150,420),(215,470),(300,560),(380,640),(470,700),(520,745)]
def poly_pts(pts,step=13):
    out=[]
    for (x0,y0),(x1,y1) in zip(pts,pts[1:]):
        n=max(1,int(math.hypot(x1-x0,y1-y0)/step))
        for k in range(n):out.append((x0+(x1-x0)*k/n,y0+(y1-y0)*k/n))
    return out+[pts[-1]]
def union_mask(centers,r):
    m=Image.new('L',(WW,WH),0)
    for (x,y) in centers:
        k=r.randrange(2);hm=HM[k]
        m.paste(255,(int(x)-40,int(y)-40),hm)
    return m
def paint_region(w,mask,tiles,r,edge=None,rim=None):
    layer=Image.new('RGBA',(WW,WH),(0,0,0,0));fill(layer,(0,0,WW,WH),tiles,r)
    w.paste(layer,(0,0),mask)
    ero=mask.filter(ImageFilter.MinFilter(3));dil=mask.filter(ImageFilter.MaxFilter(3))
    if edge:
        e=ImageChops.subtract(mask,ero);w.paste(Image.new('RGBA',(WW,WH),edge),(0,0),e)
    if rim:
        e2=ImageChops.subtract(dil,mask);w.paste(Image.new('RGBA',(WW,WH),rim),(0,0),e2)
def build_ground():
    r=random.Random(3);w=Image.new('RGBA',(WW,WH),(0,0,0,255));fill(w,(0,0,WW,WH),GR,r)
    # manchas de grama mais clara/escura (variação suave)
    nz=noise_arr=np.array(Image.fromarray((np.random.RandomState(4).rand(WH//24+1,WW//24+1)*255).astype('uint8')).resize((WW,WH),Image.BICUBIC),dtype=float)
    lay=Image.new('RGBA',(WW,WH),(0,0,0,0));px=lay.load()
    for yy in range(0,WH,2):
        for xx in range(0,WW,2):
            v=nz[yy,xx]
            if v>170:px[xx,yy]=(150,200,70,26);px[xx+1,yy]=(150,200,70,26)
            elif v<70:px[xx,yy]=(10,50,10,34);px[xx+1,yy]=(10,50,10,34)
    w.alpha_composite(lay)
    cl=[(90,300),(450,260),(230,500),(500,540),(110,700),(380,780),(560,380),(300,350),(180,560)]
    centers=cl+[(x,y) for (x,y) in poly_pts(ROAD)]+[(x,y) for (x,y) in poly_pts(ROAD2)]
    paint_region(w,union_mask(centers,r),DR,r,edge=(112,78,48,255),rim=(40,92,24,255))
    lake=[(500,740),(540,760),(520,800),(580,740),(470,790),(580,800),(610,770),(560,720)]
    paint_region(w,union_mask(lake,r),WR,r,edge=(96,170,226,255),rim=(30,76,40,255))
    px0,py0,px1,py1=PLAZA
    for yy in range(py0,py1,16):
        for xx in range(px0,px1,16):w.alpha_composite(r.choice(STN),(xx,yy))
    # moldura da praça (borda escura)
    d=ImageDraw.Draw(w);d.rectangle((px0-1,py0-1,px1,py1),outline=(52,50,60,255));d.rectangle((px0,py0,px1-1,py1-1),outline=(96,94,104,255))
    return w
PLAZA=(240,36,480,156)
POND_C=(545,765,75,48)
GROUND=build_ground()
def build_props():
    rr=random.Random(9);P=[];ex=[]
    RP=poly_pts(ROAD,10)+poly_pts(ROAD2,10)
    def free(x,y,r):
        if r>=8 and any((x-a)**2+(y-b)**2<(r+22)**2 for (a,b) in RP):return False
        if ((x-POND_C[0])/(POND_C[2]+20))**2+((y-POND_C[1])/(POND_C[3]+20))**2<1:return False
        if PLAZA[0]-50<x<PLAZA[2]+50 and PLAZA[1]-90<y<PLAZA[3]+190:return False
        for (ax,ay,ar) in ex:
            if (x-ax)**2+(y-ay)**2<(ar+r)**2:return False
        return True
    def add(spr,x,y,r,**kw):
        ex.append((x,y,r));P.append(dict(x=x,y=y,spr=spr,anc=(spr.width//2,spr.height-2),**kw))
    def tree():
        t=rr.random()
        return rr.choice(T_OAK) if t<0.5 else rr.choice(T_CON) if t<0.8 else rr.choice(T_PIN)
    OPEN=(110,230,640,860)
    for _ in range(2600):
        x=rr.randrange(0,WW);y=rr.randrange(40,WH+30)
        if OPEN[0]<x<OPEN[2] and OPEN[1]<y<OPEN[3]:continue
        t=tree()
        if free(x,y,18):add(t,x,y,18)
    for (cx,cy) in [(200,400),(540,450),(230,640),(450,650),(380,500),(150,540),(600,620)]:
        for _ in range(2):
            x=cx+rr.randrange(-25,25);y=cy+rr.randrange(-20,20)
            t=rr.choice(T_OAKS+T_SM)
            if free(x,y,14):add(t,x,y,14)
    for n in range(55):
        for _ in range(30):
            x=rr.randrange(OPEN[0],OPEN[2]);y=rr.randrange(OPEN[1],OPEN[3])
            if free(x,y,10):break
        else:continue
        k=n%5
        if k in(0,1):add(rr.choice(BUSH),x,y,10)
        elif k==2:add(rr.choice(ROCK_BIG),x,y,12)
        else:add(rr.choice(ROCK_SM),x,y,6)
    for n in range(340):
        x=rr.randrange(8,WW-8);y=rr.randrange(30,WH-8)
        if ((x-POND_C[0])/POND_C[2])**2+((y-POND_C[1])/POND_C[3])**2<1.1:continue
        if PLAZA[0]-8<x<PLAZA[2]+8 and PLAZA[1]-8<y<PLAZA[3]+8:continue
        if VS and rr.random()<0.9:P.append(dict(x=x,y=y,spr=rr.choice(VS),anc=None,flat=True))
    # acampamento
    cx,cy=190,300;P.append(dict(x=cx,y=cy,fire=True));ex.append((cx,cy,16))
    add(BARREL,cx+22,cy-4,8);add(FENCE,cx-90,cy+45,40)
    for (tx,ty,t) in [(PLAZA[0]-26,70,T_PIN[0]),(PLAZA[0]-30,150,T_CON[1]),(PLAZA[2]+26,80,T_PIN[1]),(PLAZA[2]+30,158,T_CON[0]),(PLAZA[0]-10,PLAZA[3]+8,ROCK_BIG[1]),(PLAZA[2]+8,PLAZA[3]+10,ROCK_BIG[0])]:add(t,tx,ty,6)
    for k,b in enumerate(BAN):add(b,PLAZA[0]+40+k*90,PLAZA[1]+22,6)
    for (bx,by) in [(PLAZA[0]+8,PLAZA[3]-6),(PLAZA[2]-8,PLAZA[3]-6),(PLAZA[0]+8,PLAZA[1]+60),(PLAZA[2]-8,PLAZA[1]+60)]:P.append(dict(x=bx,y=by,fire=True,small=True))
    for n in range(10):
        cx2=rr.randrange(110,640);cy2=rr.randrange(230,860)
        if not free(cx2,cy2,10):continue
        for k in range(9):
            P.append(dict(x=cx2+rr.randrange(-22,22),y=cy2+rr.randrange(-14,14),spr=rr.choice(VS[-30:]),anc=None,flat=True))
    P.sort(key=lambda p:p['y']);return P
PROPS=build_props()
