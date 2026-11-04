"""Catacumbas de Brumavale (dungeon dos esqueletos, zona 2): nave central, câmaras laterais e sala do chefe, tudo em pedra fria.
Gera mmo/assets/zone_cripta.json / zone_cripta_ground.png / atlas_cripta.*   (mesmo formato da floresta; paredes viram círculos de colisão em 'wallc')
Uso (em lendas-de-taverna/tools/mmo):  PACK_DIR=<pack> /usr/bin/python3 build_cripta.py"""
import os,sys,json,hashlib,math,random
HERE=os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE,'town_world.py')).read())
OUT=os.path.join(HERE,'..','..','mmo','assets')
Z=1.5;WW,WH=960,1500;C=16;CW,CH=WW//C,WH//C
rr=random.Random(77)
# ---------- planta: retângulos abertos (px do pack); o resto é parede
R=[(336,1296,624,1488),            # átrio de entrada
   (384,224,576,1312),             # nave central
   (96,1088,400,1264),(560,960,864,1136),(96,800,400,992),(560,640,864,832),(96,480,400,672),(560,336,864,528),   # câmaras
   (208,48,752,288)]               # sala do chefe
op=np.zeros((CH,CW),bool)
for x0,y0,x1,y1 in R:op[y0//C:y1//C,x0//C:x1//C]=True
def is_open(cx,cy):return 0<=cx<CW and 0<=cy<CH and op[cy,cx]
# ---------- texturas (pixel art procedural na paleta fria do jogo)
def tint(im,m=(.56,.64,.80),b=-6):
    a=np.array(im.convert('RGBA')).astype(float);a[:,:,0]=a[:,:,0]*m[0]+b;a[:,:,1]=a[:,:,1]*m[1]+b;a[:,:,2]=a[:,:,2]*m[2]+b
    return Image.fromarray(np.clip(a,0,255).astype('uint8'),'RGBA')
FL=[tint(tile(FLT,tx,ty)) for tx in (16,17,18) for ty in (0,1,2)]
def face_cell(r):
    im=Image.new('RGBA',(C,C),(22,26,36,255));d=im.load()
    pal=[(48,57,76),(56,66,88),(42,50,67),(52,61,82)]
    for row in range(2):
        y0=row*8;vx=7 if row==0 else 15
        for bx,(x0,x1) in enumerate(((0,vx),(vx+1,16)) if row==0 else ((0,vx),)):
            col=r.choice(pal)
            for y in range(y0,y0+7):
                for x in range(x0,x1):
                    d[x,y]=tuple(min(255,c+14) for c in col) if y==y0 else col
        if row==1:
            for y in range(y0,y0+7):d[0,y]=(22,26,36,255)
    for x in range(C):d[x,7]=(22,26,36,255);d[x,15]=(16,19,28,255)
    return im
def top_cell(r):
    im=Image.new('RGBA',(C,C),(27,31,44,255));d=im.load()
    for _ in range(10):d[r.randrange(C),r.randrange(C)]=(33,38,52,255)
    for _ in range(4):d[r.randrange(C),r.randrange(C)]=(21,24,34,255)
    return im
FACE=[face_cell(rr) for _ in range(6)];TOP=[top_cell(rr) for _ in range(6)]
# ---------- chão
W_=Image.new('RGBA',(WW,WH),(14,16,24,255))
for cy in range(CH):
    for cx in range(CW):
        if is_open(cx,cy):
            t=rr.choice(FL).copy()
            if rr.random()<.12:                      # rachadura
                d=ImageDraw.Draw(t);x=rr.randrange(3,12);y=rr.randrange(3,12);d.line([(x,y),(x+rr.randrange(-6,7),y+rr.randrange(2,6))],fill=(30,36,50,255))
            W_.alpha_composite(t,(cx*C,cy*C))
        else:
            W_.alpha_composite((FACE if is_open(cx,cy+1) else TOP)[rr.randrange(6)],(cx*C,cy*C))
# beiras: borda clara no topo da parede (junto ao chão aberto vizinho) e sombra no chão encostado na parede
d=ImageDraw.Draw(W_)
sh=Image.new('RGBA',(WW,WH),(0,0,0,0));sd=ImageDraw.Draw(sh)
for cy in range(CH):
    for cx in range(CW):
        if not is_open(cx,cy):
            if is_open(cx-1,cy):d.line([(cx*C,cy*C),(cx*C,cy*C+C-1)],fill=(58,68,92,255))
            if is_open(cx+1,cy):d.line([(cx*C+C-1,cy*C),(cx*C+C-1,cy*C+C-1)],fill=(58,68,92,255))
            if is_open(cx,cy-1):d.line([(cx*C,cy*C),(cx*C+C-1,cy*C)],fill=(70,82,108,255))
        else:
            if not is_open(cx,cy-1):sd.rectangle([cx*C,cy*C,cx*C+C-1,cy*C+5],fill=(0,0,0,70))
            if not is_open(cx-1,cy):sd.rectangle([cx*C,cy*C,cx*C+3,cy*C+C-1],fill=(0,0,0,50))
            if not is_open(cx+1,cy):sd.rectangle([cx*C+C-4,cy*C,cx*C+C-1,cy*C+C-1],fill=(0,0,0,50))
W_.alpha_composite(sh)
# manchas escuras, ladrilhos de runa e sangue seco espalhados no chão aberto
def stain(col,n,rad,al):
    lay=Image.new('RGBA',(WW,WH),(0,0,0,0));ld=ImageDraw.Draw(lay)
    for _ in range(n):
        cx=rr.randrange(CW);cy=rr.randrange(CH)
        if not is_open(cx,cy) or not is_open(cx+1,cy) or not is_open(cx,cy+1):continue
        x=cx*C+rr.randrange(C);y=cy*C+rr.randrange(C)
        for k in range(5):
            ox=x+rr.randrange(-rad,rad);oy=y+rr.randrange(-rad//2,rad//2);ld.ellipse([ox,oy,ox+rr.randrange(3,rad),oy+rr.randrange(2,rad//2+3)],fill=col+(al,))
    W_.alpha_composite(lay)
stain((18,20,30),220,14,60);stain((70,22,22),26,9,70)
gimg=W_.resize((int(WW*Z),int(WH*Z)),Image.NEAREST)
gimg.convert('RGB').save(os.path.join(OUT,'zone_cripta_ground.png'),optimize=True)
# ---------- sprites procedurais
def zs(im):return im.resize((max(1,int(im.width*Z)),max(1,int(im.height*Z))),Image.NEAREST)
def poly(d,pts,fill,out=(16,19,28,255)):d.polygon(pts,fill=fill,outline=out)
def sarcofago(v):
    w,h=36,24;im=Image.new('RGBA',(w,h),(0,0,0,0));d=ImageDraw.Draw(im)
    top=(118,130,152,255);mid=(92,103,126,255);dk=(66,75,96,255)
    poly(d,[(2,9),(w-3,9),(w-1,13),(w-1,h-3),(1,h-3),(1,13)],dk)               # corpo
    poly(d,[(3,4),(w-4,4),(w-2,10),(2,10)],top)                                  # tampa
    d.line([(5,6),(w-6,6)],fill=(150,163,186,255))
    if v%3==0:d.rectangle([w//2-1,5,w//2,9],fill=(70,80,102,255));d.rectangle([w//2-3,6,w//2+2,6],fill=(70,80,102,255))
    if v%3==1:d.ellipse([w//2-3,5,w//2+2,9],fill=(160,172,194,255));d.point((w//2-1,7),fill=(40,46,62,255));d.point((w//2+1,7),fill=(40,46,62,255))
    if v%3==2:d.line([(w//2-5,5),(w//2+5,9)],fill=(30,34,46,255));d.line([(w//2,5),(w//2-2,9)],fill=(30,34,46,255))
    d.line([(2,11),(w-3,11)],fill=mid)
    im.col=[(-10,-5,8),(0,-5,8),(10,-5,8)]
    return im
def lapide(v):
    im=Image.new('RGBA',(12,18),(0,0,0,0));d=ImageDraw.Draw(im)
    poly(d,[(2,17),(2,6),(4,2),(7,2),(9,6),(9,17)],(104,116,138,255))
    d.line([(5,4),(5,9)],fill=(40,46,62,255));d.line([(3,6),(7,6)],fill=(40,46,62,255))
    d.line([(3,16),(8,16)],fill=(76,86,108,255));im.col=[(0,-3,5)];return im
def pilar(h=44):
    im=Image.new('RGBA',(16,h),(0,0,0,0));d=ImageDraw.Draw(im)
    poly(d,[(1,h-2),(1,h-7),(15,h-7),(15,h-2)],(84,95,118,255))
    poly(d,[(3,h-7),(3,5),(13,5),(13,h-7)],(104,116,140,255))
    d.rectangle([4,6,6,h-8],fill=(132,146,172,255));d.rectangle([10,6,12,h-8],fill=(76,86,108,255))
    poly(d,[(1,5),(1,1),(15,1),(15,5)],(122,135,160,255));im.col=[(0,-3,7)];return im
def caixao():
    im=Image.new('RGBA',(18,28),(0,0,0,0));d=ImageDraw.Draw(im)
    poly(d,[(5,2),(13,2),(16,9),(14,26),(4,26),(2,9)],(88,64,48,255),(24,16,12,255))
    d.line([(9,4),(9,22)],fill=(60,42,32,255));d.line([(6,8),(12,8)],fill=(60,42,32,255));im.col=[(0,-4,7),(0,-12,6)];return im
def teia(flip):
    im=Image.new('RGBA',(24,24),(0,0,0,0));d=ImageDraw.Draw(im)
    for k in range(6):d.line([(0,0),(24,k*5)],fill=(200,210,225,70));d.line([(0,0),(k*5,24)],fill=(200,210,225,70))
    for r_ in (7,13,19):d.arc([-r_,-r_,r_,r_],0,90,fill=(200,210,225,90))
    return im.transpose(Image.FLIP_LEFT_RIGHT) if flip else im
SARC=[sarcofago(i) for i in range(3)];TOMB=[lapide(i) for i in range(2)];PIL=pilar();PILS=pilar(30);COF=caixao()
# ossos (dos goblins, mesma escala do jogo) e outros reaproveitados
try:
    HERE_=HERE
    exec(open(os.path.join(HERE,'goblin_ia.py')).read())
    BONES=GI['bonepile']+GI['bone'];STAKE=GI['stake']
except Exception as e:
    print('sem arte de ossos:',e);BONES=[];STAKE=[]
# ---------- registro de sprites e props
sprs={};P=[];FX=[];ex=[]
def reg(img,anc):
    img=zs(img);h=hashlib.md5(img.tobytes()+bytes(str(img.size),'ascii')).hexdigest()[:10]
    if h not in sprs:sprs[h]=(img,(int(anc[0]*Z),int(anc[1]*Z)))
    return h
def free(x,y,r):
    return all((x-ax)**2+(y-ay)**2>=(ar+r)**2 for ax,ay,ar in ex)
def add(spr,x,y,r,flat=False):
    ex.append((x,y,r));d=dict(t='flat' if flat else 'p',id=reg(spr,(spr.width//2,spr.height if flat else spr.height-2)),x=round(x*Z),y=round(y*Z))
    c=getattr(spr,'col',None)
    if c and not flat:d['col']=[[round(a*Z),round(b*Z),round(rad*Z)] for a,b,rad in c]
    P.append(d)
def fire(x,y,small=False):P.append(dict(t='fire',x=round(x*Z),y=round(y*Z),small=small));ex.append((x,y,10))
def torch_at(x,y):FX.append(dict(k='torch',x=round(x*Z),y=round(y*Z)))
def cell_free(x,y,m=2):                              # ponto aberto com folga de m células
    cx,cy=int(x//C),int(y//C)
    return all(is_open(cx+i,cy+j) for i in range(-m,m+1) for j in range(-m,m+1))
# ---------- tochas nas paredes (suportes pintados no chão + chama)
d=ImageDraw.Draw(W_)
tcount=0
for cy in range(CH):
    run=0
    for cx in range(CW):
        if (not is_open(cx,cy)) and is_open(cx,cy+1) and is_open(cx,cy+2):
            run+=1
            if run%6==3 and cx>1:
                x=cx*C+8;y=cy*C+8
                d.rectangle([x-1,y-2,x+1,y+5],fill=(80,56,34,255));d.rectangle([x-3,y-4,x+3,y-2],fill=(60,64,76,255))
                torch_at(x,y-6);tcount+=1
        else:run=0
gimg=W_.resize((int(WW*Z),int(WH*Z)),Image.NEAREST);gimg.convert('RGB').save(os.path.join(OUT,'zone_cripta_ground.png'),optimize=True)
# ---------- colunas, sarcófagos, lápides, caixões, ossos, estandartes
for x0,y0,x1,y1 in R[2:8]:
    for sx in (x0+40,x1-40):                          # colunas nos cantos das câmaras
        for sy in (y0+44,y1-18):
            if cell_free(sx,sy-10,1):add(PIL,sx,sy,8)
    cx=(x0+x1)//2;cy=(y0+y1)//2
    fire(cx,cy+6)
    for k in range(rr.randrange(3,5)):
        sx=rr.randrange(x0+60,x1-60);sy=rr.choice((y0+34,y1-10))
        if cell_free(sx,sy-6,2) and free(sx,sy,22):add(rr.choice(SARC),sx,sy,22)
    for _ in range(rr.randrange(3,6)):
        sx=rr.randrange(x0+40,x1-40);sy=rr.randrange(y0+40,y1-20)
        if cell_free(sx,sy-6,1) and free(sx,sy,10):add(rr.choice(TOMB),sx,sy,8)
    for _ in range(rr.randrange(4,8)):
        sx=rr.randrange(x0+30,x1-30);sy=rr.randrange(y0+30,y1-14)
        if BONES and cell_free(sx,sy,0):add(rr.choice(BONES),sx,sy,0,True)
    if rr.random()<.6 and cell_free((x0+x1)//2+50,y0+40,2):add(COF,(x0+x1)//2+50,y0+34,8)
# nave e átrio: fogueiras e restos
for y in range(1180,300,-190):
    fire(480-60,y,True);fire(480+60,y,True)
for _ in range(34):
    sx=rr.randrange(396,564);sy=rr.randrange(260,1290)
    if BONES and free(sx,sy,6):add(rr.choice(BONES),sx,sy,0,True)
for _ in range(10):
    sx=rr.randrange(400,560);sy=rr.randrange(300,1280)
    if free(sx,sy,10):add(rr.choice(ROCK_SM),sx,sy,6)
# portão: colunas, braseiros e entrada
ENTR=(480,1470);START=(480,1380)
for sx in (-1,1):
    add(PIL,ENTR[0]+sx*84,ENTR[1]+6,8);add(PILS,ENTR[0]+sx*84,ENTR[1]-52,8)
    fire(ENTR[0]+sx*50,ENTR[1]-16,True)
    add(BAN[1 if sx<0 else 2],ENTR[0]+sx*118,ENTR[1]-30,6)
# estandartes encostados nas paredes dos fundos das câmaras
for x0,y0,x1,y1 in R[2:8]:
    for sx in (x0+80,x1-80):
        add(BAN[rr.randrange(3)],sx,y0+16,4)
# teias nos cantos das câmaras (decoração, sem colisão)
for x0,y0,x1,y1 in R[2:9]:
    P.append(dict(t='flat',id=reg(teia(False),(0,0)),x=round((x0+2)*Z),y=round((y0+4+24)*Z)))
    P.append(dict(t='flat',id=reg(teia(True),(24,0)),x=round((x1-2)*Z),y=round((y0+4+24)*Z)))
# sala do chefe: círculo de colunas e tochas
bx,by=480,168
for a in range(0,360,60):
    px_=bx+math.cos(math.radians(a))*150;py_=by+math.sin(math.radians(a))*58+24
    if cell_free(px_,py_-10,1):add(PIL,px_,py_,8)
fire(bx-110,by+60);fire(bx+110,by+60)
P.sort(key=lambda p:p['y'])
# ---------- paredes: círculos de colisão nas células de parede coladas no espaço aberto
wallc=[]
for cy in range(CH):
    for cx in range(CW):
        if is_open(cx,cy):continue
        if any(is_open(cx+i,cy+j) for i in (-1,0,1) for j in (-1,0,1)):wallc.append([round((cx*C+8)*Z),round((cy*C+8)*Z),round(10*Z)])
# ---------- pontos de nascimento: câmaras e nave, com folga e longe da entrada
solid=[(p['x']/Z,p['y']/Z) for p in P if p['t']=='p']
spawns=[]
for _ in range(60000):
    if len(spawns)>=44:break
    x=rr.randrange(60,WW-60);y=rr.randrange(60,1290)
    if not cell_free(x,y,2):continue
    if any((x-a)**2+(y-b)**2<26**2 for a,b in solid):continue
    if any((x-a)**2+(y-b)**2<64**2 for a,b in spawns):continue
    if math.hypot(x-START[0],y-START[1])<150:continue
    if y<290 and abs(x-480)<400 and y<250:continue                      # sala do chefe fica livre
    spawns.append((x,y))
spawns=[[round(a*Z),round(b*Z)] for a,b in spawns]
# ---------- atlas
for i,f in enumerate(BFIRE):k=reg(f,(16,32));sprs['bf%d'%i]=sprs.pop(k)
for i,f in enumerate(FIRE):k=reg(f,(16,48));sprs['fi%d'%i]=sprs.pop(k)
items=sorted(sprs.items(),key=lambda kv:-kv[1][0].height);Wd=1024;x=y=sh=0;pos={}
for k,(im,anc) in items:
    if x+im.width+1>Wd:x=0;y+=sh+1;sh=0
    pos[k]=(x,y,im.width,im.height,anc[0],anc[1]);x+=im.width+1;sh=max(sh,im.height)
atlas=Image.new('RGBA',(Wd,y+sh+1),(0,0,0,0))
for k,(im,anc) in items:atlas.alpha_composite(im,pos[k][:2])
atlas.save(os.path.join(OUT,'atlas_cripta.png'),optimize=True);json.dump({k:list(v) for k,v in pos.items()},open(os.path.join(OUT,'atlas_cripta.json'),'w'))
zone=dict(w=gimg.width,h=gimg.height,props=P,spawns=spawns,plaza=[0,0,1,1],road=[],start=[round(START[0]*Z),round(START[1]*Z)],boss=[round(bx*Z),round(by*Z)],gate=[round(ENTR[0]*Z),round(ENTR[1]*Z)],wallc=wallc,fx=FX,dark=1)
json.dump(zone,open(os.path.join(OUT,'zone_cripta.json'),'w'),separators=(',',':'))
print('cripta',gimg.size,'props',len(P),'sprites',len(sprs),'spawns',len(spawns),'paredes',len(wallc),'tochas',tcount)
