import math,random,os
from PIL import Image,ImageDraw,ImageFont,ImageChops
P='/tmp/claude-0/-home-user-neon-wars/3ffd125f-a99a-599e-8554-f2b481e86fc1/scratchpad/'
O=P+'repos/pxl/out/anims/';V=P+'duelv/';os.makedirs(V,exist_ok=True)
for f in os.listdir(V):os.remove(V+f)
def load(n):
    im=Image.open(O+n+'.gif');r=[]
    for i in range(im.n_frames):
        im.seek(i);r.append(im.convert('RGBA').copy())
    return r
A={n:load(n) for n in ('w_walk','w_idle','w_slash','w_power','w_spin','w_shake','w_roar','w_hurt','w_dodge','g_walk','g_idle','g_slam','g_hurt','g_stun','g_die')}
SW,SH=192,108;SC=5;GYS=92
# ---------- cenário da floresta (pixel art) ----------
def forest():
    r=random.Random(7);im=Image.new('RGBA',(SW,SH));d=ImageDraw.Draw(im)
    for y in range(SH):
        t=y/SH;d.line((0,y,SW,y),fill=(int(120+60*t),int(184+30*t),int(156-10*t),255))
    for x,y,rr in [(10,44,16),(34,38,18),(62,46,15),(90,40,19),(122,45,16),(150,38,18),(178,44,17),(200,40,18)]:
        for k in range(3):d.ellipse((x-rr+k*3,y-rr+k*2,x+rr-k*2,y+rr-k),fill=(46+k*8,98+k*10,70+k*6,255))
    for x in (14,58,104,148,184):   # troncos médios com copas
        d.rectangle((x-3,30,x+2,92),fill=(78,56,40,255));d.rectangle((x-3,30,x-2,92),fill=(106,78,52,255))
        for k,(cx,cy,rr) in enumerate([(x-8,26,15),(x+8,24,16),(x,14,17)]):
            d.ellipse((cx-rr,cy-rr,cx+rr,cy+rr),fill=(34,84,50,255));d.ellipse((cx-rr+2,cy-rr+1,cx+rr-4,cy+rr-5),fill=(52,116,62,255));d.ellipse((cx-rr+4,cy-rr+3,cx+rr-9,cy+rr-10),fill=(84,152,74,255))
    d.rectangle((0,GYS-14,SW,SH),fill=(84,142,62,255))
    for y in range(GYS-14,SH,3):d.line((0,y,SW,y),fill=(74,128,54,255) if (y//3)%2 else (96,156,70,255))
    d.ellipse((20,GYS-4,176,GYS+14),fill=(150,122,82,255));d.ellipse((30,GYS-2,166,GYS+10),fill=(176,146,98,255))
    for _ in range(70):
        x=r.randrange(SW);y=r.randrange(GYS-12,SH);d.line((x,y,x,y-2),fill=(56,110,44,255));d.point((x+1,y-1),fill=(120,180,86,255))
    for _ in range(14):
        x=r.randrange(SW);y=r.randrange(GYS-8,SH-2);c=r.choice([(255,230,120),(255,150,170),(240,240,250)]);d.point((x,y),fill=c+(255,));d.point((x+1,y),fill=c+(255,))
    return im
BG=forest()
FNT=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',17);FNS=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',13);FNB=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',24)
WX0,GXX=40,142
frames=[]
class S:pass
st=S();st.hp=1.0;st.buff=False;st.shake=0;st.nums=[];st.skill='';st.sk_idx=-1;st.msg=('',0);st.stars=False
def num(txt,x,y,col,big=False):st.nums.append(dict(t=txt,x=x,y=y,c=col,age=0,big=big))
def shot(w,g,wx,gx,wdy=0,flash=0,galpha=1.0,zone=None,extra=None):
    im=BG.copy()
    if zone:
        zx,zr,zp=zone;d=ImageDraw.Draw(im,'RGBA');rr=int(zr*zp)
        d.ellipse((zx-zr,GYS-zr//3,zx+zr,GYS+zr//3),fill=(255,60,50,50),outline=(255,90,70,200));d.ellipse((zx-rr,GYS-rr//3,zx+rr,GYS+rr//3),fill=(255,60,50,90))
    gi=ImageOps_mirror(A[g[0]][min(g[1],len(A[g[0]])-1)])
    if flash:
        a=gi.split()[3];wh=Image.new('RGBA',gi.size,(255,255,255,255));mk=a.point(lambda v:166 if v>0 else 0);gi=gi.copy();gi.paste(wh,(0,0),mk);gi.putalpha(a)
    if galpha<1:
        a=gi.split()[3].point(lambda v:int(v*galpha));gi.putalpha(a)
    wi=A[w[0]][min(w[1],len(A[w[0]])-1)]
    sx=random.randint(-1,1) if st.shake>0 else 0;sy=random.randint(-1,1) if st.shake>0 else 0
    if st.shake>0:st.shake-=1
    im.alpha_composite(gi,(gx-45+sx,GYS-64+sy));im.alpha_composite(wi,(wx-50+sx,GYS-64+wdy+sy))
    if st.stars:
        d=ImageDraw.Draw(im);t=len(frames)*.5
        for k in range(3):
            a=t+k*2.1;d.text((gx-3+int(11*math.cos(a)),GYS-58+int(4*math.sin(a))),'*',fill=(255,230,80,255),font=ImageFont.load_default())
    big=im.resize((SW*SC,SH*SC),Image.NEAREST);d=ImageDraw.Draw(big)
    # HUD
    d.rectangle((250,26,710,46),fill=(20,16,26,200),outline=(200,170,80,255));w=int(456*max(0,st.hp));d.rectangle((252,28,252+w,44),fill=(196,48,44,255))
    if st.hp>0:d.rectangle((252,28,252+w,32),fill=(236,96,84,255))
    d.text((480,6),'GRUNK  Nv.8  (Chefe)',fill=(240,224,180,255),font=FNS,anchor='mt')
    d.rectangle((14,480,230,496),fill=(20,16,26,200),outline=(120,170,220,255));d.rectangle((16,482,226,494),fill=(60,190,90,255))
    d.text((14,462),'Guerreiro  Nv.8',fill=(240,240,250,255),font=FNS)
    names=['Golpe Poderoso','Corte Profundo','Grito de Guerra','Abalo Sismico']
    for i,n in enumerate(names):
        x=250+i*120;on=(st.sk_idx==i);d.rectangle((x,470,x+110,500),fill=(30,26,40,230) if not on else (120,90,30,240),outline=(230,200,110,255) if on else (90,84,110,255));d.text((x+55,485),n,fill=(240,230,200,255),font=FNS,anchor='mm')
    if st.buff:d.rectangle((14,500,110,516),fill=(150,80,20,230));d.text((62,508),'ATQ +30%',fill=(255,230,150,255),font=FNS,anchor='mm')
    if st.skill:d.text((480,76),st.skill,fill=(255,240,180,255),font=FNB,anchor='mm',stroke_width=3,stroke_fill=(30,20,10,255))
    if st.msg[1]>0:d.text((480,250),st.msg[0],fill=(255,255,255,255),font=FNB,anchor='mm',stroke_width=3,stroke_fill=(30,20,10,255));st.msg=(st.msg[0],st.msg[1]-1)
    for n in st.nums[:]:
        n['age']+=1;y=n['y']*SC-n['age']*3;al=max(0,1-n['age']/22)
        d.text((n['x']*SC,y),n['t'],fill=tuple(n['c']),font=FNB if n['big'] else FNT,anchor='mm',stroke_width=3 if n['big'] else 2,stroke_fill=(30,16,10,255))
        if n['age']>22:st.nums.remove(n)
    frames.append(big.convert('RGB'))
def ImageOps_mirror(g):
    return g.transpose(Image.FLIP_LEFT_RIGHT)
def seg(n,wf,gf,wxf,gxf,**kw):
    for i in range(n):
        u=i/max(1,n-1);yield i,u,wf(i),gf(i),wxf(u),gxf(u)
# 1 intro
st.skill='';st.msg=('Floresta dos Goblins',16)
for i in range(18):shot(('w_idle',i),('g_idle',i),WX0,GXX)
# 2 aproximação
for i,u,w,g,wx,gx in seg(30,lambda i:('w_walk',i%12),lambda i:('g_idle',i),lambda u:int(40+60*u),lambda u:GXX):shot(w,g,wx,gx)
WX=100
# 3 ataque básico
st.skill='Ataque Basico'
for i in range(14):
    w=('w_slash',i) if i<12 else ('w_idle',i);hit=i in(7,8,9);g=('g_hurt',i-7) if 7<=i<13 else ('g_idle',i)
    if i==7:num('142',GXX-6,50,(255,255,255));st.hp=.92;st.shake=3
    shot(w,g,WX,GXX+(2 if hit else 0),flash=1 if i==7 else 0)
# 4 grito de guerra
st.skill='Grito de Guerra';st.sk_idx=2
for i in range(18):
    shot(('w_roar',min(i,15)),('g_idle',i),WX,GXX)
    if i==8:st.buff=True;st.shake=3
st.skill=''
for i in range(6):shot(('w_idle',i),('g_idle',i),WX,GXX)
# 5 golpe poderoso
st.skill='Golpe Poderoso';st.sk_idx=0
for i in range(20):
    w=('w_power',i) if i<18 else ('w_idle',i);g=('g_hurt',i-11) if 11<=i<17 else ('g_idle',i)
    if i==11:num('468',GXX-4,48,(255,226,90),True);st.hp=.70;st.shake=6;st.msg=('CRITICO!',10)
    shot(w,g,WX,GXX+(4 if 11<=i<14 else 0),flash=1 if i in(11,12) else 0)
st.skill='';st.sk_idx=-1
# 6 Grunk usa pancada; guerreiro esquiva
for i in range(22):
    zp=min(1,i/12) if i<=13 else 1;zone=(WX,26,zp) if i<=15 else None
    g=('g_slam',i) if i<20 else ('g_idle',i)
    wxd=WX-int(22*min(1,max(0,(i-7)/9)));w=('w_dodge',min(9,max(0,i-6))) if 6<=i<=15 else (('w_idle',i) if i<6 else ('w_idle',i))
    wdy=0
    if i==13:st.shake=7;num('Esquivou!',wxd+4,56,(200,230,255));st.msg=('',0)
    if i==8:st.msg=('Grunk prepara uma pancada!',14)
    shot(w,g,wxd if i>=6 else WX,GXX,zone=zone)
WXE=WX-22
# 7 volta + corte profundo
for i in range(10):shot(('w_walk',i%12),('g_idle',i),WXE+int(22*(i/9)),GXX)
st.skill='Corte Profundo';st.sk_idx=1
for i in range(18):
    w=('w_spin',i) if i<16 else ('w_idle',i);g=('g_hurt',(i-4)%6) if 4<=i<15 else ('g_idle',i)
    if i in (4,8,12):num(str(210+i*2),GXX-6+(i-8),52-(i//4)*2,(255,200,120));st.hp=max(.1,st.hp-.07);st.shake=3
    shot(w,g,WX,GXX+(2 if i in(4,8,12) else 0),flash=1 if i in(4,8,12) else 0)
st.skill='';st.sk_idx=-1
# 8 abalo sismico: atordoa
st.skill='Abalo Sismico';st.sk_idx=3
for i in range(22):
    w=('w_shake',i) if i<18 else ('w_idle',i)
    if i==11:st.shake=9;num('390',GXX-6,48,(255,200,120));st.hp=max(.1,st.hp-.06);st.msg=('ATORDOADO!',16);st.stars=True
    g=('g_stun',i%8) if i>=12 else ('g_idle',i)
    shot(w,g,WX,GXX,flash=1 if i==12 else 0)
st.skill=''
# 9 final: golpe poderoso no atordoado
st.skill='Golpe Poderoso';st.sk_idx=0
for i in range(20):
    w=('w_power',i) if i<18 else ('w_idle',i);g=('g_stun',i%8)
    if i==11:num('740',GXX-4,46,(255,226,90),True);st.hp=0;st.shake=10;st.stars=False;st.msg=('CRITICO!',10)
    if i>=11:break
    shot(w,g,WX,GXX)
st.skill='Golpe Poderoso'
for i in range(11,18):
    w=('w_power',i)
    shot(w,('g_hurt',i-11),WX,GXX+3,flash=1 if i==11 else 0)
for i in range(14):
    g=('g_die',i);gal=1.0 if i<8 else max(0,1-(i-8)/6)
    if i==3:st.msg=('Grunk derrotado!',40)
    shot(('w_idle',i),g,WX,GXX-int(i*.4),galpha=gal)
st.skill=''
for i in range(26):shot(('w_idle',i),('g_die',13),WX,GXX,galpha=0)
for i,f in enumerate(frames):f.save(V+'f%03d.png'%i)
print(len(frames))
