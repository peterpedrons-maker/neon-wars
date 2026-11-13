import sys,random,math
sys.path.insert(0,'/home/user/neon-wars/lendas-de-taverna/tools/mmo')
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from pxengine.character import Character
from pxengine.export import render_anim
from pxengine import effects
D='/home/user/neon-wars/lendas-de-taverna/tools/mmo/pxengine/data/'
hero=Character(D+'hero.json');boss=Character(D+'boss.json')
HA={n:render_anim(hero,n) for n in ('idle','walk','attack','skill','hurt','block','dodge')}
BA={n:render_anim(boss,n) for n in ('idle','walk','attack','skill','hurt','death')}
SW,SH,SC=230,124,3
random.seed(4)
# ---------- cenário vivo (estilo do tático)
def scene_bg():
    im=Image.new('RGB',(SW,SH),(98,172,68));px=im.load();d=ImageDraw.Draw(im)
    for y in range(SH):
        for x in range(SW):
            v=random.random();b=(98,172,68)
            if (x//10+y//5)%2==0:b=(110,186,76)
            if v<.07:b=(78,146,58)
            elif v>.965:b=(156,220,114)
            px[x,y]=b
    for y in range(28,SH):                      # arena de terra com borda
        pass
    d.rectangle([14,70,SW-14,SH-12],outline=None)
    # faixa de terra
    for y in range(66,SH-8):
        for x in range(8,SW-8):
            e=min(x-8,SW-9-x,y-66,SH-9-y)
            if e>=0:
                v=random.random();c=(206,150,84) if (x//8+y//4)%2==0 else (216,160,92)
                if v<.08:c=(172,118,64)
                elif v>.97:c=(240,196,128)
                if e<2:c=(140,92,50)
                px[x,y]=c
    # árvores ao fundo
    def tree(cx,cy,r):
        d.ellipse([cx-r+3,cy+r-4,cx+r+3,cy+r+2],fill=(60,120,48))
        d.rectangle([cx-2,cy+2,cx+2,cy+r+4],fill=(106,66,40));d.rectangle([cx-2,cy+2,cx-1,cy+r+4],fill=(138,90,52))
        for dx,dy,rr,c in((0,0,r,(26,98,92)),(-r//2,2,r*.7,(30,112,104)),(r//2,3,r*.7,(30,112,104)),(-2,-r//3,r*.7,(52,150,134)),(1,-r//2,r*.45,(110,196,160))):
            d.ellipse([cx+dx-rr,cy+dy-rr,cx+dx+rr,cy+dy+rr],fill=c)
    for i,(x,y,r) in enumerate([(14,34,13),(46,26,15),(82,38,12),(120,24,16),(158,36,13),(196,28,15),(222,40,12),(30,52,11),(176,54,10)]):tree(x,y,r)
    for i in range(26):
        x=random.randint(0,SW-1);y=random.randint(48,SH-1)
        if px[x,y][0]<130:
            c=random.choice([(255,255,255),(255,220,80),(255,120,160)]);d.point((x,y),fill=c);d.point((x+1,y),fill=c)
    return im
BG=scene_bg()
F=ImageFont.load_default()
def put(canvas,rgba,ax,ay,x,y,flip=False,flash=0,tint=None):
    im=Image.fromarray(rgba,'RGBA');
    if flip:im=im.transpose(Image.FLIP_LEFT_RIGHT);ax=im.width-1-ax
    if flash>0:
        a=np.array(im);m=a[...,3]>0;a[m,:3]=(a[m,:3]*(1-flash)+255*flash).astype(np.uint8);im=Image.fromarray(a,'RGBA')
    canvas.alpha_composite(im,(int(round(x-ax)),int(round(y-ay))))
def shadow(canvas,x,y,rw):
    s=Image.new('RGBA',canvas.size,(0,0,0,0));d=ImageDraw.Draw(s);d.ellipse([x-rw,y-3,x+rw,y+3],fill=(30,60,30,110));canvas.alpha_composite(s)
def frame_of(A,t,loop=False):
    ms=A['ms'];tot=sum(ms);
    if loop:t=t%tot
    t=min(t,tot-1);c=0
    for i,m in enumerate(ms):
        c+=m
        if t<c:return i
    return A['n']-1
def text(canvas,s,x,y,col,out=(20,10,24),big=False):
    d=ImageDraw.Draw(canvas)
    for dx,dy in((1,0),(-1,0),(0,1),(0,-1),(1,1)):d.text((x+dx,y+dy),s,font=F,fill=out)
    d.text((x,y),s,font=F,fill=col)
# ---------- roteiro (ms)
HX0,BX=38,166;GYh=hero.spec['ground'];GYb=boss.spec['ground'];AXh=hero.spec.get('hx_side',36);AXb=boss.spec.get('hx_side',60)
FY=100                                         # linha do chão na cena
tl=[]  # (t0, ator, anim, extra)
T=0
def A_(t,who,anim,**k):tl.append(dict(t=t,who=who,anim=anim,**k))
A_(0,'h','idle');A_(0,'b','idle')
A_(900,'h','walk',x0=38,x1=106,dur=1000)
A_(1900,'h','idle')
A_(2150,'h','attack',lunge=10);A_(3100,'b','hurt');A_(3100,'dmg',None,txt='-184',col=(255,255,255),at='b',fx='slash')
A_(3500,'h','idle')
A_(3700,'b','skill');A_(4900,'h','block',back=4);A_(4900,'dmg',None,txt='BLOQUEOU',col=(120,200,255),at='h',fx=None)
A_(5500,'b','idle');A_(5600,'h','skill',lunge=14);A_(6900,'b','hurt',big=1);A_(6900,'dmg',None,txt='-612!',col=(255,216,74),at='b',fx='shock',crit=1)
A_(7600,'b','attack');A_(8350,'h','dodge',back=-22);A_(8350,'dmg',None,txt='ESQUIVOU',col=(200,230,255),at='h',fx=None)
A_(9100,'h','idle');A_(9100,'b','idle')
A_(9400,'h','attack',lunge=10);A_(10300,'b','death');A_(10300,'dmg',None,txt='-340',col=(255,255,255),at='b',fx='slash')
END=13300
def state(who,t):
    cur=None
    for e in tl:
        if e['who']==who and e['t']<=t:cur=e
    return cur
BHP=[(0,100),(3100,86),(6900,48),(10300,0)];
def hp(t):
    v=100
    for tt,h in BHP:
        if t>=tt:v=h
    return v
fxs={'slash':effects.slash(),'shock':effects.fire(size=48)}
frames=[]
STEP=80
for t in range(0,END,STEP):
    cv=BG.convert('RGBA');shk=0
    # posições
    sh=state('h',t);sb=state('b',t)
    hx=HX0;bx=BX;hh=0
    if sh:
        a=sh['anim'];el=t-sh['t']
        if a=='walk':
            u=min(1,el/sh['dur']);hx=sh['x0']+(sh['x1']-sh['x0'])*u
        else:
            # herói permanece onde terminou a caminhada
            hx=106
            tot=sum(HA[a]['ms'])
            if a in('attack','skill'):u=min(1,el/tot);hx+=sh.get('lunge',0)*math.sin(min(1,u*1.6)*math.pi)*(1 if u<.7 else .4)
            if a=='block':hx-=sh.get('back',0)*min(1,el/300)
            if a=='dodge':
                u=min(1,el/tot);hx+=sh.get('back',0)*math.sin(u*math.pi*.9);hh=-10*math.sin(u*math.pi)
    # ator: posição do boss
    cur_b=sb
    bxx=BX
    if sb and sb['anim']=='skill':
        tot=sum(BA['skill']['ms']);u=min(1,(t-sb['t'])/tot);bxx-=22*math.sin(min(1,u*1.3)*math.pi)
    if sb and sb['anim']=='attack':
        tot=sum(BA['attack']['ms']);u=min(1,(t-sb['t'])/tot);bxx-=14*math.sin(min(1,u*1.5)*math.pi)
    # recuo por dano
    # desenhar (o mais ao fundo primeiro: mesma linha, ordem por x)
    def draw_h():
        A=HA[sh['anim'] if sh else 'idle'];el=t-(sh['t'] if sh else 0);i=frame_of(A,el,A['loop'])
        fl=0
        shadow(cv,hx,FY,11);put(cv,A['views']['side'][i].rgba,AXh,GYh,hx,FY+hh,False,fl)
    def draw_b():
        a=sb['anim'] if sb else 'idle';A=BA[a];el=t-(sb['t'] if sb else 0);i=frame_of(A,el,A['loop'])
        fl=0
        if a=='hurt' and el<160:fl=.7 if not sb.get('big') else .85
        x=bxx+(6 if (a=='hurt' and el<200) else 0)
        shadow(cv,x,FY+1,17);put(cv,A['views']['side'][i].rgba,AXb,GYb,x,FY+1,True,fl)
    draw_h();draw_b()
    # efeitos e números
    for e in tl:
        if e['who']!='dmg':continue
        el=t-e['t']
        if 0<=el<900:
            tx=(bxx if e['at']=='b' else hx);ty=FY-52 if e['at']=='b' else FY-38
            if e.get('fx') and el<560:
                lst=fxs[e['fx']];k=min(len(lst)-1,el//70)
                im=Image.fromarray(lst[k],'RGBA')
                if e['fx']=='slash':
                    im=im.transpose(Image.FLIP_LEFT_RIGHT) if e['at']=='b' else im
                    cv.alpha_composite(im,(int(tx-24),int(FY-62)))
                else:
                    big=im.resize((96,96),Image.NEAREST);cv.alpha_composite(big,(int(tx-48),int(FY-70)))
                if el<140:shk=2 if e.get('crit') else 1
                if el<100:
                    d=ImageDraw.Draw(cv)
                    for q in range(10):
                        ang=q/10*6.283;r=4+el/10
                        d.point((int(tx+math.cos(ang)*r*2),int(FY-40+math.sin(ang)*r)),fill=(255,244,160))
            rise=min(18,el/30);text(cv,e['txt'],int(tx-len(e['txt'])*3),int(ty-rise),e['col'])
    # barras de vida
    d=ImageDraw.Draw(cv)
    d.rectangle([8,6,78,13],fill=(24,14,30));d.rectangle([9,7,77,12],fill=(60,24,34));d.rectangle([9,7,9+int(68*.96),12],fill=(90,220,100));d.rectangle([9,7,9+int(68*.96),8],fill=(160,255,170))
    text(cv,'HEROI',9,14,(255,236,170))
    d.rectangle([SW-120,6,SW-8,13],fill=(24,14,30));d.rectangle([SW-119,7,SW-9,12],fill=(60,24,34))
    w=int(109*hp(t)/100);d.rectangle([SW-119,7,SW-119+w,12],fill=(232,70,60));d.rectangle([SW-119,7,SW-119+w,8],fill=(255,150,120))
    text(cv,'CHEFE ORC',SW-119,14,(255,200,160))
    if t>10300+1400:text(cv,'VITORIA!',SW//2-24,34,(255,230,100))
    img=cv.convert('RGB')
    if shk:
        s2=Image.new('RGB',img.size,(0,0,0));s2.paste(img,(random.randint(-shk,shk),random.randint(-shk,shk)));img=s2
    frames.append(img.resize((SW*SC,SH*SC),Image.NEAREST))
pal=[f.quantize(128,method=Image.MEDIANCUT,dither=Image.NONE) for f in frames]
out='/tmp/claude-0/-home-user-neon-wars/3ffd125f-a99a-599e-8554-f2b481e86fc1/scratchpad/luta_pixel.gif'
pal[0].save(out,save_all=True,append_images=pal[1:],duration=STEP,loop=0,optimize=True,disposal=2)
[frames[int(a/STEP)].save('/tmp/fight/s%d.png'%i) for i,a in enumerate((3000,4700,6200,8300,10600,11800))]
import os;print(len(frames),os.path.getsize(out)//1024,'KB')
