"""Esgotos de Brumavale (dungeon dos ratos gigantes, zona 4): salão central cortado por um canal de esgoto, câmaras de ninhos e a toca do Rei dos Ratos.
Gera mmo/assets/zone_esgoto.json / zone_esgoto_ground.png / atlas_esgoto.*   (paredes e água viram círculos de colisão em 'wallc')
Uso (em lendas-de-taverna/tools/mmo):  PACK_DIR=<pack> /usr/bin/python3 build_esgoto.py"""
import os,sys,json,hashlib,math,random
HERE=os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE,'town_world.py')).read())
OUT=os.path.join(HERE,'..','..','mmo','assets')
Z=1.5;WW,WH=960,1500;C=16;CW,CH=WW//C,WH//C
rr=random.Random(91)
exec(open(os.path.join(HERE,'cripta_ia.py')).read());TORCH=[t for t in CI['torchw']]      # tochas de parede da cripta (mesmo estilo)
exec(open(os.path.join(HERE,'esgoto_ia.py')).read())                                          # sprites e tiles dos esgotos
# ---------- planta
R=[(336,1296,624,1488),(288,224,672,1312),
   (96,1088,300,1264),(660,960,864,1136),(96,800,300,992),(660,640,864,832),(96,480,300,672),(660,336,864,528),
   (208,48,752,288)]
op=np.zeros((CH,CW),bool)
for x0,y0,x1,y1 in R:op[y0//C:y1//C,x0//C:x1//C]=True
wat=np.zeros((CH,CW),bool);wat[336//C:1280//C,432//C:528//C]=True
for y0,y1 in ((1088,1136),(784,832),(496,544)):wat[y0//C:y1//C,432//C:528//C]=False      # pontes
BR=np.zeros((CH,CW),bool)
for y0,y1 in ((1088,1136),(784,832),(496,544)):BR[y0//C:y1//C,432//C:528//C]=True
wat&=op
def is_open(cx,cy):return 0<=cx<CW and 0<=cy<CH and op[cy,cx]
def is_water(cx,cy):return 0<=cx<CW and 0<=cy<CH and wat[cy,cx]
def is_ground(cx,cy):return is_open(cx,cy) and not is_water(cx,cy)
# ---------- texturas
def dim(im,k):
    a=np.array(im.convert('RGBA')).astype(float);a[:,:,:3]*=k;return Image.fromarray(np.clip(a,0,255).astype('uint8'),'RGBA')
FLP=[dim(t,.86) for t in ST['plain']];FLM=[dim(t,.9) for t in ST['moss']];FLC=[dim(t,.9) for t in ST['crack']];FLB=[dim(t,.9) for t in ST['bone']]
WAT=[dim(t,.85) for t in ST['water']];BRK=[dim(t,.7) for t in ST['brick']]
def pickfloor(r):
    v=r.random()
    return r.choice(FLP) if v<.58 else r.choice(FLM) if v<.80 else r.choice(FLC) if v<.93 else r.choice(FLB)
def top_cell(r):
    im=Image.new('RGBA',(C,C),(24,31,30,255));d=im.load()
    for _ in range(10):d[r.randrange(C),r.randrange(C)]=(31,40,36,255)
    for _ in range(4):d[r.randrange(C),r.randrange(C)]=(18,23,24,255)
    for _ in range(3):d[r.randrange(C),r.randrange(C)]=(38,58,34,255)
    return im
TOP=[top_cell(rr) for _ in range(6)]
# ---------- chão
W_=Image.new('RGBA',(WW,WH),(12,16,16,255))
for cy in range(CH):
    for cx in range(CW):
        if is_water(cx,cy):W_.alpha_composite(rr.choice(WAT),(cx*C,cy*C))
        elif is_open(cx,cy):
            t=pickfloor(rr)
            if BR[cy,cx]:t=dim(rr.choice(ST['plain']),.78)
            W_.alpha_composite(t,(cx*C,cy*C))
        else:
            W_.alpha_composite((BRK[rr.randrange(len(BRK))] if is_open(cx,cy+1) else TOP[rr.randrange(6)]),(cx*C,cy*C))
d=ImageDraw.Draw(W_)
sh=Image.new('RGBA',(WW,WH),(0,0,0,0));sd=ImageDraw.Draw(sh)
for cy in range(CH):
    for cx in range(CW):
        if not is_open(cx,cy):
            if is_open(cx-1,cy):d.line([(cx*C,cy*C),(cx*C,cy*C+C-1)],fill=(52,70,62,255))
            if is_open(cx+1,cy):d.line([(cx*C+C-1,cy*C),(cx*C+C-1,cy*C+C-1)],fill=(52,70,62,255))
            if is_open(cx,cy-1):d.line([(cx*C,cy*C),(cx*C+C-1,cy*C)],fill=(66,88,76,255))
        elif is_water(cx,cy):                                                         # borda viscosa do canal
            for dx,dy,a_,b_ in ((-1,0,(cx*C,cy*C),(cx*C,cy*C+C-1)),(1,0,(cx*C+C-1,cy*C),(cx*C+C-1,cy*C+C-1)),(0,-1,(cx*C,cy*C),(cx*C+C-1,cy*C)),(0,1,(cx*C,cy*C+C-1),(cx*C+C-1,cy*C+C-1))):
                if not is_water(cx+dx,cy+dy):d.line([a_,b_],fill=(58,92,38,255),width=2)
        else:
            if not is_open(cx,cy-1):sd.rectangle([cx*C,cy*C,cx*C+C-1,cy*C+5],fill=(0,0,0,70))
            if not is_open(cx-1,cy):sd.rectangle([cx*C,cy*C,cx*C+3,cy*C+C-1],fill=(0,0,0,50))
            if not is_open(cx+1,cy):sd.rectangle([cx*C+C-4,cy*C,cx*C+C-1,cy*C+C-1],fill=(0,0,0,50))
W_.alpha_composite(sh)
# corrimãos das pontes (duas linhas de pedra escura nas bordas) e manchas
d=ImageDraw.Draw(W_)
for y0,y1 in ((1088,1136),(784,832),(496,544)):
    for x in (432,520):d.rectangle([x,y0,x+7,y1-1],fill=(46,58,56,255),outline=(24,30,30,255))
def stain(col,n,rad,al):
    lay=Image.new('RGBA',(WW,WH),(0,0,0,0));ld=ImageDraw.Draw(lay)
    for _ in range(n):
        cx=rr.randrange(CW);cy=rr.randrange(CH)
        if not is_ground(cx,cy) or not is_ground(cx+1,cy) or not is_ground(cx,cy+1):continue
        x=cx*C+rr.randrange(C);y=cy*C+rr.randrange(C)
        for k in range(5):
            ox=x+rr.randrange(-rad,rad);oy=y+rr.randrange(-rad//2,rad//2);ld.ellipse([ox,oy,ox+rr.randrange(3,rad),oy+rr.randrange(2,rad//2+3)],fill=col+(al,))
    W_.alpha_composite(lay)
stain((10,18,14),220,14,55);stain((44,76,28),30,10,70)
gimg=W_.resize((int(WW*Z),int(WH*Z)),Image.NEAREST)
gimg.convert('RGB').save(os.path.join(OUT,'zone_esgoto_ground.png'),optimize=True)
def zs(im):return im.resize((max(1,int(im.width*Z)),max(1,int(im.height*Z))),Image.NEAREST)
sprs={};P=[];FX=[];ex=[]
def reg(img,anc):
    img=zs(img);h=hashlib.md5(img.tobytes()+bytes(str(img.size),'ascii')).hexdigest()[:10]
    if h not in sprs:sprs[h]=(img,(int(anc[0]*Z),int(anc[1]*Z)))
    return h
def free(x,y,r):return all((x-ax)**2+(y-ay)**2>=(ar+r)**2 for ax,ay,ar in ex)
def add(spr,x,y,r,flat=False):
    ex.append((x,y,r));d=dict(t='flat' if flat else 'p',id=reg(spr,(spr.width//2,spr.height if flat else spr.height-2)),x=round(x*Z),y=round(y*Z))
    c=getattr(spr,'col',None)
    if c and not flat:d['col']=[[round(a*Z),round(b*Z),round(rad*Z)] for a,b,rad in c]
    P.append(d)
def fire(x,y,small=False):P.append(dict(t='fire',x=round(x*Z),y=round(y*Z),small=small));ex.append((x,y,10))
def cell_free(x,y,m=2):
    cx,cy=int(x//C),int(y//C)
    return all(is_ground(cx+i,cy+j) for i in range(-m,m+1) for j in range(-m,m+1))
def nocol(sp):
    q=sp.copy();q.col=None;return q
def solid_ok(x,y,m=1):return cell_free(x,y-8,m)
def glow(x,y,col,r=40):FX.append(dict(k='lamp',x=round(x*Z),y=round(y*Z),col=col,r=r))
def teia(flip):
    im=Image.new('RGBA',(24,24),(0,0,0,0));d=ImageDraw.Draw(im)
    for k in range(6):d.line([(0,0),(24,k*5)],fill=(200,215,200,70));d.line([(0,0),(k*5,24)],fill=(200,215,200,70))
    for r_ in (7,13,19):d.arc([-r_,-r_,r_,r_],0,90,fill=(200,215,200,90))
    return im.transpose(Image.FLIP_LEFT_RIGHT) if flip else im
# ---------- decoração das paredes: tochas, buracos de rato, escadas, correntes, canos
tcount=0
for cy in range(CH):
    run=0
    for cx in range(CW):
        if (not is_open(cx,cy)) and is_open(cx,cy+1) and is_open(cx,cy+2) and cx>1:
            run+=1;x=cx*C+8;y=cy*C+16
            if run%7==3:add(rr.choice(TORCH),x,y+6,0,True);glow(x,y-14,'#ffb050',48);tcount+=1
            elif run%7==6 and rr.random()<.75:add(nocol(rr.choice(SI['ratholes'])),x,y+14,0,True)
            elif run%11==8:add(nocol(rr.choice(SI['ladder'])),x,y+14,0,True)
            elif run%13==9:add(nocol(rr.choice(SI['chain'])),x,y+22,0,True)
            elif run%17==12:add(nocol(SI['pipeh'][0]),x,y+10,0,True)
        else:run=0
# ---------- câmaras de ninhos
for ci,(x0,y0,x1,y1) in enumerate(R[2:8]):
    cx=(x0+x1)//2;cy=(y0+y1)//2
    for sx in (x0+36,x1-36):
        for sy in (y0+60,y1-14):
            if solid_ok(sx,sy,1) and free(sx,sy,10):add(rr.choice(SI['pillar']),sx,sy,9)
    fire(cx,cy+8)
    for _ in range(rr.randrange(2,4)):
        sx=rr.randrange(x0+50,x1-50);sy=rr.randrange(y0+50,y1-14)
        if solid_ok(sx,sy,2) and free(sx,sy,22):add(rr.choice(SI['nest']),sx,sy,20)
    for _ in range(rr.randrange(3,5)):
        sx=rr.randrange(x0+40,x1-40);sy=rr.randrange(y0+46,y1-14)
        if solid_ok(sx,sy,1) and free(sx,sy,12):add(rr.choice(SI['crate']+SI['barrel']),sx,sy,10)
    for _ in range(rr.randrange(2,4)):
        sx=rr.randrange(x0+36,x1-36);sy=rr.randrange(y0+40,y1-10)
        if cell_free(sx,sy,0):add(rr.choice(SI['trash']),sx,sy,0,True)
    for _ in range(rr.randrange(2,4)):
        sx=rr.randrange(x0+36,x1-36);sy=rr.randrange(y0+40,y1-10)
        if cell_free(sx,sy,0):add(rr.choice(SI['slime']+SI['bones']+SI['fish']),sx,sy,0,True)
    for _ in range(rr.randrange(1,3)):
        sx=rr.randrange(x0+40,x1-40);sy=rr.randrange(y0+50,y1-14)
        if solid_ok(sx,sy,1) and free(sx,sy,8):add(rr.choice(SI['shroom']),sx,sy,5);glow(sx,sy-8,'#7aff6a',30)
    if rr.random()<.6:
        sx=rr.randrange(x0+50,x1-50);sy=rr.randrange(y0+54,y1-14)
        if solid_ok(sx,sy,1) and free(sx,sy,12):add(rr.choice(SI['cage']+SI['statue']),sx,sy,10)
    if rr.random()<.7:
        sx=rr.randrange(x0+40,x1-40);sy=rr.randrange(y0+50,y1-14)
        if solid_ok(sx,sy,1) and free(sx,sy,8):add(rr.choice(SI['cheese']+SI['sack']),sx,sy,6)
    if rr.random()<.5:
        sx=rr.randrange(x0+40,x1-40);sy=rr.randrange(y0+50,y1-14)
        if solid_ok(sx,sy,1) and free(sx,sy,8):add(rr.choice(SI['pipev']),sx,sy,7)
    if rr.random()<.5:
        sx=rr.randrange(x0+40,x1-40);sy=rr.randrange(y0+46,y1-14)
        if cell_free(sx,sy,1):add(rr.choice(SI['coins']+SI['snap']+SI['manhole']),sx,sy,0,True)
    if ci in(1,4) and solid_ok(x0+60 if ci%2==0 else x1-60,y0+60,2):add(rr.choice(SI['tunnel']),x0+60 if ci%2==0 else x1-60,y0+58,30)
    for sx in (x0+80,x1-80):add(rr.choice(SI['banner']),sx,y0+14,3)
    if rr.random()<.5:
        sx=rr.randrange(x0+60,x1-60);sy=rr.randrange(y0+46,y1-14)
        if solid_ok(sx,sy,1) and free(sx,sy,8):add(SI['lantern'][1],sx,sy,5);glow(sx,sy-18,'#ffcc66',44)
# ---------- salão central: passarelas
for y in range(1230,330,-120):
    for sx in (312,648):
        if solid_ok(sx,y,1) and free(sx,y,10):add(rr.choice(SI['pillar']),sx,y,9)
for _ in range(26):
    sx=rr.choice((rr.randrange(300,420),rr.randrange(540,660)));sy=rr.randrange(260,1290)
    if cell_free(sx,sy,0) and free(sx,sy,8):add(rr.choice(SI['bones']+SI['slime']+SI['fish']+SI['trash']),sx,sy,0,True)
for _ in range(10):
    sx=rr.choice((rr.randrange(310,420),rr.randrange(540,650)));sy=rr.randrange(300,1280)
    if solid_ok(sx,sy,1) and free(sx,sy,10):add(rr.choice(SI['barrel']+SI['crate']),sx,sy,9)
for _ in range(8):
    sx=rr.choice((rr.randrange(310,420),rr.randrange(540,650)));sy=rr.randrange(300,1280)
    if cell_free(sx,sy,1) and free(sx,sy,8):add(rr.choice(SI['manhole']+SI['grate']),sx,sy,0,True)
for _ in range(6):
    sx=rr.choice((rr.randrange(310,420),rr.randrange(540,650)));sy=rr.randrange(300,1280)
    if solid_ok(sx,sy,1) and free(sx,sy,6):add(rr.choice(SI['shroom']),sx,sy,5);glow(sx,sy-8,'#7aff6a',30)
add(nocol(SI['boat'][0]),480,1010,0,True);add(nocol(SI['boat'][0]),480,640,0,True)    # barcos de rato-pirata afundando no canal
add(SI['sluice'][0],480,352,40)
for sx in (-1,1):fire(480+sx*130,1180,True);fire(480+sx*130,700,True)
# ---------- entrada
ENTR=(480,1478);START=(480,1380)
for sx in (-1,1):
    add(SI['pillar'][0],ENTR[0]+sx*84,ENTR[1]+6,9);fire(ENTR[0]+sx*54,ENTR[1]-14,True)
    add(SI['banner'][1 if sx<0 else 2],ENTR[0]+sx*118,ENTR[1]-28,3)
add(SI['tunnel'][0],ENTR[0]-190,ENTR[1]-24,30);add(SI['tunnel'][2],ENTR[0]+190,ENTR[1]-24,30)
for sx,sy in ((372,1350),(588,1350)):add(rr.choice(SI['crate']+SI['barrel']+SI['sack']),sx,sy,10)
# ---------- toca do Rei dos Ratos
bx,by=480,176
add(SI['throne'][0],bx,by-24,26);add(SI['crown'][0],bx,by+60,30)
for sx in (-1,1):
    add(SI['statue'][0 if sx<0 else 1],bx+sx*106,by-28,12)
    add(SI['pillar'][0],bx+sx*172,by-30,9);add(SI['pillar'][0],bx+sx*172,by+70,9)
    add(rr.choice(SI['chest']),bx+sx*212,by+30,12)
    add(rr.choice(SI['cage']),bx+sx*140,by+84,10)
    fire(bx+sx*114,by+66)
add(SI['shrine'][0],bx-232,by-4,34);add(nocol(SI['vault'][0]),bx+236,by-10,0)
add(SI['snap'][0],bx-60,by+120,0,True);add(SI['snap'][0],bx+60,by+120,0,True);add(nocol(SI['spikes'][0]),bx+170,by+120,0)
for _ in range(6):
    sx=rr.randrange(240,720);sy=rr.randrange(110,270)
    if cell_free(sx,sy,0):add(rr.choice(SI['bones']+SI['trash']+SI['slime']),sx,sy,0,True)
for x0,y0,x1,y1 in R[2:9]:
    P.append(dict(t='flat',id=reg(teia(False),(0,0)),x=round((x0+2)*Z),y=round((y0+4+24)*Z)))
    P.append(dict(t='flat',id=reg(teia(True),(24,0)),x=round((x1-2)*Z),y=round((y0+4+24)*Z)))
P.sort(key=lambda p:p['y'])
# ---------- colisões: paredes e água do canal
wallc=[]
for cy in range(CH):
    for cx in range(CW):
        if not is_open(cx,cy):
            if any(is_open(cx+i,cy+j) for i in (-1,0,1) for j in (-1,0,1)):wallc.append([round((cx*C+8)*Z),round((cy*C+8)*Z),round(10*Z)])
        elif is_water(cx,cy):wallc.append([round((cx*C+8)*Z),round((cy*C+8)*Z),round(10*Z)])
solid=[(p['x']/Z,p['y']/Z) for p in P if p['t']=='p']
spawns=[]
for _ in range(60000):
    if len(spawns)>=44:break
    x=rr.randrange(60,WW-60);y=rr.randrange(60,1290)
    if not cell_free(x,y,2):continue
    if any((x-a)**2+(y-b)**2<26**2 for a,b in solid):continue
    if any((x-a)**2+(y-b)**2<64**2 for a,b in spawns):continue
    if math.hypot(x-START[0],y-START[1])<150:continue
    if y<250:continue
    spawns.append((x,y))
spawns=[[round(a*Z),round(b*Z)] for a,b in spawns]
for i,f in enumerate(BFIRE):k=reg(f,(16,32));sprs['bf%d'%i]=sprs.pop(k)
for i,f in enumerate(FIRE):k=reg(f,(16,48));sprs['fi%d'%i]=sprs.pop(k)
items=sorted(sprs.items(),key=lambda kv:-kv[1][0].height);Wd=1024;x=y=sh=0;pos={}
for k,(im,anc) in items:
    if x+im.width+1>Wd:x=0;y+=sh+1;sh=0
    pos[k]=(x,y,im.width,im.height,anc[0],anc[1]);x+=im.width+1;sh=max(sh,im.height)
atlas=Image.new('RGBA',(Wd,y+sh+1),(0,0,0,0))
for k,(im,anc) in items:atlas.alpha_composite(im,pos[k][:2])
atlas.save(os.path.join(OUT,'atlas_esgoto.png'),optimize=True);json.dump({k:list(v) for k,v in pos.items()},open(os.path.join(OUT,'atlas_esgoto.json'),'w'))
zone=dict(w=gimg.width,h=gimg.height,props=P,spawns=spawns,plaza=[0,0,1,1],road=[],start=[round(START[0]*Z),round(START[1]*Z)],boss=[round(bx*Z),round(by*Z)],gate=[round(ENTR[0]*Z),round(ENTR[1]*Z)],wallc=wallc,fx=FX,dark=1)
json.dump(zone,open(os.path.join(OUT,'zone_esgoto.json'),'w'),separators=(',',':'))
print('esgoto',gimg.size,'props',len(P),'sprites',len(sprs),'spawns',len(spawns),'colisões',len(wallc),'tochas',tcount)
