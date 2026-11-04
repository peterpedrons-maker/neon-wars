"""Catacumbas de Brumavale (dungeon dos esqueletos, zona 2): nave central, câmaras laterais e sala do chefe, tudo em pedra fria.
Gera mmo/assets/zone_cripta.json / zone_cripta_ground.png / atlas_cripta.*   (mesmo formato da floresta; paredes viram círculos de colisão em 'wallc')
Uso (em lendas-de-taverna/tools/mmo):  PACK_DIR=<pack> /usr/bin/python3 build_cripta.py"""
import os,sys,json,hashlib,math,random
HERE=os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE,'town_world.py')).read())
OUT=os.path.join(HERE,'..','..','mmo','assets')
Z=1.5;WW,WH=960,1500;C=16;CW,CH=WW//C,WH//C
rr=random.Random(77)
exec(open(os.path.join(HERE,'cripta_ia.py')).read())      # sprites e tiles feitos por IA (ia_src/cripta)
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
def dim(im,k):
    a=np.array(im.convert('RGBA')).astype(float);a[:,:,:3]*=k;return Image.fromarray(np.clip(a,0,255).astype('uint8'),'RGBA')
FLP=[dim(t,.84) for t in TL['plain']];FLC=[dim(t,.84) for t in TL['crack']];FLB=[dim(t,.84) for t in TL['bone']];FLR=[dim(t,.84) for t in TL['blood']+TL['rune']];FLD=[dim(t,.9) for t in TL['dirt']]
BRK=[dim(t,.62) for t in TL['brick']]
def pickfloor(r):
    v=r.random()
    return r.choice(FLP) if v<.78 else r.choice(FLC) if v<.91 else r.choice(FLB) if v<.965 else r.choice(FLR)
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
FACE=BRK*2;TOP=[top_cell(rr) for _ in range(6)]
# ---------- chão
W_=Image.new('RGBA',(WW,WH),(14,16,24,255))
for cy in range(CH):
    for cx in range(CW):
        if is_open(cx,cy):
            W_.alpha_composite(pickfloor(rr),(cx*C,cy*C))
        else:
            W_.alpha_composite((FACE[rr.randrange(len(FACE))] if is_open(cx,cy+1) else TOP[rr.randrange(6)]),(cx*C,cy*C))
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
def teia(flip):
    im=Image.new('RGBA',(24,24),(0,0,0,0));d=ImageDraw.Draw(im)
    for k in range(6):d.line([(0,0),(24,k*5)],fill=(200,210,225,70));d.line([(0,0),(k*5,24)],fill=(200,210,225,70))
    for r_ in (7,13,19):d.arc([-r_,-r_,r_,r_],0,90,fill=(200,210,225,90))
    return im.transpose(Image.FLIP_LEFT_RIGHT) if flip else im
def zs(im):return im.resize((max(1,int(im.width*Z)),max(1,int(im.height*Z))),Image.NEAREST)
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
# ---------- tochas nas paredes (sprite da IA + luz)
def lamp_at(x,y):FX.append(dict(k='lamp',x=round(x*Z),y=round(y*Z)))
tcount=0
for cy in range(CH):
    run=0
    for cx in range(CW):
        if (not is_open(cx,cy)) and is_open(cx,cy+1) and is_open(cx,cy+2) and cx>1:
            run+=1
            if run%6==3:
                x=cx*C+8;y=cy*C+16
                add(rr.choice(CI['torchw']),x,y+6,0,True);FX.append(dict(k='lamp',x=round(x*Z),y=round((y-14)*Z),col='#ffb050',r=48));tcount+=1
        else:run=0
def nocol(sp):
    q=sp.copy();q.col=None;return q
def solid_ok(x,y,m=1):return cell_free(x,y-8,m)
# ---------- câmaras
for ci,(x0,y0,x1,y1) in enumerate(R[2:8]):
    cx=(x0+x1)//2;cy=(y0+y1)//2
    for sx in (x0+36,x1-36):                                   # colunas nos cantos
        for sy in (y0+60,y1-14):
            if solid_ok(sx,sy,1) and free(sx,sy,10):add(CI['pillar'][0],sx,sy,9)
    fire(cx,cy+8)
    if ci in(2,5):add(CI['altar'][0],cx,y0+54,30)              # altares sacrificiais
    for k in range(rr.randrange(2,4)):                         # sarcófagos junto à parede norte e sul
        sx=rr.randrange(x0+70,x1-70);sy=rr.choice((y0+46,y1-12))
        if solid_ok(sx,sy,2) and free(sx,sy,26):add(rr.choice(CI['sarc']),sx,sy,26)
    for _ in range(rr.randrange(3,6)):
        sx=rr.randrange(x0+40,x1-40);sy=rr.randrange(y0+50,y1-14)
        if solid_ok(sx,sy,1) and free(sx,sy,12):add(rr.choice(CI['tomb']),sx,sy,9)
    for _ in range(rr.randrange(1,3)):
        sx=rr.randrange(x0+50,x1-50);sy=rr.randrange(y0+54,y1-14)
        if solid_ok(sx,sy,1) and free(sx,sy,16):add(rr.choice(CI['coffin']),sx,sy,14)
    for _ in range(2):
        sx=rr.randrange(x0+36,x1-36);sy=rr.randrange(y0+46,y1-12)
        if solid_ok(sx,sy,1) and free(sx,sy,10):add(rr.choice(CI['urn']),sx,sy,8)
    if rr.random()<.55:
        sx=rr.choice((x0+60,x1-60));sy=rr.randrange(y0+54,y1-14)
        if solid_ok(sx,sy,1) and free(sx,sy,16):add(rr.choice(CI['statue']),sx,sy,12)
    if rr.random()<.5:
        sx=rr.randrange(x0+50,x1-50);sy=rr.randrange(y0+60,y1-14)
        if solid_ok(sx,sy,1) and free(sx,sy,14):add(rr.choice(CI['cage']),sx,sy,12)
    if rr.random()<.45:
        sx=rr.randrange(x0+50,x1-50);sy=rr.randrange(y0+60,y1-14)
        if solid_ok(sx,sy,1) and free(sx,sy,12):add(rr.choice(CI['armor']),sx,sy,10)
    for _ in range(rr.randrange(3,5)):
        sx=rr.randrange(x0+36,x1-36);sy=rr.randrange(y0+36,y1-10)
        if cell_free(sx,sy,0):add(rr.choice(CI['bonepile']),sx,sy,0,True)
    for _ in range(rr.randrange(1,3)):
        sx=rr.randrange(x0+36,x1-36);sy=rr.randrange(y0+50,y1-14)
        if solid_ok(sx,sy,1) and free(sx,sy,8):add(rr.choice(CI['candel'][:1]),sx,sy,5)
    if rr.random()<.6:
        sx=rr.randrange(x0+50,x1-50);sy=rr.randrange(y0+54,y1-14)
        if solid_ok(sx,sy,1) and free(sx,sy,12):add(rr.choice(CI['crate']+CI['barrel']),sx,sy,10)
    for sx in (x0+80,x1-80):                                   # estandartes na parede norte
        add(CI['banner'][rr.randrange(3)],sx,y0+14,3,False)
    if rr.random()<.7:
        sx=rr.randrange(x0+60,x1-60);sy=rr.randrange(y0+46,y1-14)
        if cell_free(sx,sy,1):add(rr.choice(CI['puddle']+CI['moss']),sx,sy,0,True)
    if rr.random()<.5:
        sx=rr.randrange(x0+60,x1-60);sy=rr.randrange(y0+46,y1-14)
        if cell_free(sx,sy,1):add(rr.choice([CI['rune'][0],CI['runeb'][0]]),sx,sy,0,True)
    if rr.random()<.5 and solid_ok(x0+30,y1-12,1):add(rr.choice(CI['stalag']),rr.choice((x0+30,x1-30)),y1-12,14)
# ---------- nave e átrio
for y in range(1180,300,-190):
    fire(480-62,y,True);fire(480+62,y,True)
for _ in range(34):
    sx=rr.randrange(396,564);sy=rr.randrange(260,1290)
    if free(sx,sy,8):add(rr.choice(CI['bonepile']),sx,sy,0,True)
for _ in range(10):
    sx=rr.randrange(400,560);sy=rr.randrange(300,1280)
    if free(sx,sy,10):add(rr.choice(ROCK_SM),sx,sy,6)
for _ in range(6):
    sx=rr.randrange(410,550);sy=rr.randrange(320,1280)
    if free(sx,sy,10):add(rr.choice(CI['stake']),sx,sy,4)
for sy in (1000,700,440):
    add(rr.choice([CI['rune'][0],CI['runeb'][0]]),480,sy,0,True)
for sx in (-1,1):
    for sy in (1230,880,520):
        sp=rr.choice(CI['candel'][:1])
        if free(480+sx*92,sy,8):add(sp,480+sx*92,sy,5)
# ---------- portão da entrada
ENTR=(480,1478);START=(480,1380)
add(nocol(CI['gate'][0]),ENTR[0],ENTR[1]+8,0)
for sx in (-1,1):
    add(CI['skullpil'][0],ENTR[0]+sx*88,ENTR[1]+8,10)
    fire(ENTR[0]+sx*60,ENTR[1]-14,True)
    add(CI['banner'][1 if sx<0 else 2],ENTR[0]+sx*118,ENTR[1]-28,3)
for sx,sy in ((372,1350),(588,1350)):
    add(rr.choice(CI['crate']+CI['barrel']+CI['sack']),sx,sy,10)
# ---------- sala do chefe: trono, estátuas, runas, baús, estalagmites
bx,by=480,176
add(CI['throne'][0],bx,by-30,26)
for sx in (-1,1):
    add(CI['statue'][1 if sx<0 else 2],bx+sx*104,by-36,12)
    add(CI['pillar'][0],bx+sx*170,by-30,9);add(CI['pillar'][0],bx+sx*170,by+66,9)
    add(rr.choice(CI['chest2']),bx+sx*210,by+28,12)
    add(rr.choice(CI['stalag']),bx+sx*236,by+88,14)
    fire(bx+sx*120,by+64)
add(CI['rune'][0],bx-60,by+40,0,True);add(CI['runeb'][0],bx+60,by+40,0,True)
add(CI['book'][0],bx+92,by+6,6)
for _ in range(5):
    sx=rr.randrange(240,720);sy=rr.randrange(110,270)
    if cell_free(sx,sy,0):add(rr.choice(CI['bonepile']),sx,sy,0,True)
# correntes penduradas nas paredes, cristais arcanos e o portal selado
for cy in range(CH):
    run=0
    for cx in range(CW):
        if (not is_open(cx,cy)) and is_open(cx,cy+1) and is_open(cx,cy+2) and cx>1:
            run+=1
            if run%9==6:add(nocol(rr.choice(CI['chainh'])),cx*C+8,cy*C+26,0,True)
        else:run=0
def glow_at(x,y,col,r=44):FX.append(dict(k='lamp',x=round(x*Z),y=round(y*Z),col=col,r=r))
for ci in (1,3,4):
    x0,y0,x1,y1=R[2+ci]
    for _ in range(12):
        sx=rr.randrange(x0+60,x1-60);sy=rr.randrange(y0+60,y1-14)
        if solid_ok(sx,sy,1) and free(sx,sy,12):add(CI['crystal'][0],sx,sy,9);glow_at(sx,sy-16,'#6ad0ff');break
    for _ in range(12):
        sx=rr.randrange(x0+40,x1-40);sy=rr.randrange(y0+50,y1-14)
        if cell_free(sx,sy,1):add(CI['chainfloor'][0],sx,sy,0,True);break
add(nocol(CI['portal'][0]),480-224,176-10,0);glow_at(480-224,176-34,'#5aaaff',60)
add(CI['crystal'][0],480+224,176+10,9);glow_at(480+224,176-6,'#6ad0ff')
# cobwebs nos cantos das câmaras (processual, sem colisão)
for x0,y0,x1,y1 in R[2:9]:
    P.append(dict(t='flat',id=reg(teia(False),(0,0)),x=round((x0+2)*Z),y=round((y0+4+24)*Z)))
    P.append(dict(t='flat',id=reg(teia(True),(24,0)),x=round((x1-2)*Z),y=round((y0+4+24)*Z)))
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
