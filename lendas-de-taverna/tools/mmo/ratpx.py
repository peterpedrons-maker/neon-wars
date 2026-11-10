"""Teste: Rei dos Ratos em pixel art feita por código (esqueleto + cinemática direta, 80x80, paleta fixa, contorno automático).
Uso: python3 ratpx.py <pasta_saida>  -> frames PNG (walk/attack/idle) e ratpx.mp4 se ffmpeg existir"""
import sys,os,math
from PIL import Image,ImageDraw
W=H=88;GY=80
P=dict(k=(24,18,22),fur=(122,104,86),furD=(88,74,62),furL=(150,130,108),skin=(204,150,150),cape=(124,116,52),capeD=(92,86,40),capeL=(150,142,70),
       belt=(98,62,38),buck=(190,170,90),cloth=(118,122,116),club=(112,66,44),clubD=(78,44,30),nail=(190,190,190),crown=(150,140,120),crownL=(210,200,150),
       eye=(170,255,90),tooth=(240,226,170),tail=(190,140,140),claw=(60,50,46))
def cap(d,a,b,r0,r1,col):
    n=max(2,int(math.hypot(b[0]-a[0],b[1]-a[1])*1.5))
    for i in range(n+1):
        t=i/n;x=a[0]+(b[0]-a[0])*t;y=a[1]+(b[1]-a[1])*t;r=r0+(r1-r0)*t
        d.ellipse((x-r,y-r,x+r,y+r),fill=col)
def fk(p,L,ang):a=math.radians(ang);return (p[0]+L*math.sin(a),p[1]+L*math.cos(a))
def leg(d,hip,hd,kn,col,colD,front):
    k=fk(hip,11,hd);a=fk(k,11,hd-kn);
    cap(d,hip,k,4.2,3.6,col);cap(d,k,a,3.4,2.6,colD)
    d.ellipse((k[0]-3.2,k[1]-3.2,k[0]+3.2,k[1]+3.2),fill=col)
    fo=(a[0]+5,a[1]+1.2);cap(d,a,fo,2.4,1.6,colD)
    for i in range(3):d.point((int(fo[0]+1),int(fo[1]-1+i)),fill=P['claw'])
    return a
def render(pose):
    S=4;im=Image.new('RGBA',(W*S,H*S),(0,0,0,0));
    big=Image.new('RGBA',(W,H),(0,0,0,0));d=ImageDraw.Draw(big)
    hipx=34;lean=pose.get('lean',0)
    # altura: pé mais baixo encosta no chão
    def feet(hy):
        res=[]
        for hd,kn in ((pose['hF'],pose['kF']),(pose['hN'],pose['kN'])):
            k=fk((0,0),11,hd);a=fk(k,11,hd-kn);res.append(a[1])
        return max(res)
    hipy=GY-feet(0)-2.5+pose.get('bob',0);hip=(hipx,hipy)
    # cauda (atrás)
    t0=(hipx-8,hipy+2);tw=pose.get('tail',0)
    pts=[t0,(hipx-17,hipy+6+tw),(hipx-24,hipy+3-tw),(hipx-29,hipy+7)]
    for i in range(3):cap(d,pts[i],pts[i+1],2.2-i*.4,1.8-i*.4,P['tail'])
    # perna longe (atrás, mais escura)
    leg(d,hip,pose['hF'],pose['kF'],P['furD'],P['furD'],False)
    # braço longe
    sh=(hipx+7+lean,hipy-23)
    e=fk(sh,8,-pose['aF']);h=fk(e,8,-pose['aF']+22);cap(d,sh,e,3.2,2.8,P['furD']);cap(d,e,h,2.8,2.2,P['furD'])
    # corpo: barriga, peito
    bx=hipx+2+lean*.5;by=hipy-12
    d.ellipse((bx-14,by-13,bx+13,by+13),fill=P['fur'])
    d.ellipse((bx-6,by-12,bx+13,by+10),fill=P['furL'])
    d.ellipse((bx-9,by-3,bx+11,by+14),fill=P['skin'])            # barriga rosada
    # tanga e cinto
    d.polygon([(bx-10,by+8),(bx+10,by+8),(bx+8,by+19),(bx+2,by+16),(bx-4,by+20),(bx-9,by+16)],fill=P['cloth'])
    d.rectangle((bx-12,by+5,bx+12,by+8),fill=P['belt']);d.ellipse((bx-1,by+4,bx+4,by+9),fill=P['buck'])
    # manto (ombros)
    cp=[(bx-14,by-14),(bx-4,by-22),(bx+12,by-20),(bx+16,by-12),(bx+9,by-9),(bx+3,by-13),(bx-6,by-4),(bx-15,by-2)]
    d.polygon(cp,fill=P['cape']);d.polygon([(bx-14,by-14),(bx-4,by-22),(bx+2,by-20),(bx-8,by-8),(bx-15,by-2)],fill=P['capeL'])
    d.polygon([(bx-6,by-4),(bx+3,by-13),(bx+9,by-9),(bx,by+1)],fill=P['capeD'])
    # cabeça (focinho)
    hx=bx+13+lean*.5;hy=by-23+pose.get('hb',0)
    d.ellipse((hx-8,hy-7,hx+7,hy+7),fill=P['fur'])
    cap(d,(hx+2,hy-1),(hx+15,hy+3),5,1.6,P['fur']);d.ellipse((hx+14,hy+1,hx+17,hy+5),fill=P['skin'])
    d.polygon([(hx-6,hy-8),(hx-2,hy-14),(hx+2,hy-8)],fill=P['skin']);d.polygon([(hx-5,hy-8),(hx-2,hy-12),(hx+1,hy-8)],fill=P['furD'])
    d.rectangle((hx+8,hy+4,hx+9,hy+7),fill=P['tooth']);d.rectangle((hx+11,hy+5,hx+12,hy+7),fill=P['tooth'])
    d.rectangle((hx+5,hy-3,hx+7,hy-2),fill=P['eye'])
    # coroa de lata e garfos
    d.rectangle((hx-6,hy-12,hx+5,hy-8),fill=P['crown']);d.rectangle((hx-6,hy-12,hx+5,hy-11),fill=P['crownL'])
    for i,xx in enumerate((hx-5,hx-1,hx+3)):d.line((xx,hy-12,xx,hy-17+(i%2)),fill=P['crownL'])
    # perna perto
    leg(d,(hipx+2,hipy),pose['hN'],pose['kN'],P['fur'],P['furL'],True)
    # braço perto + cano
    sh2=(hipx+3+lean,hipy-23)
    e=fk(sh2,8,-pose['aN']);hd=fk(e,8,-pose['aN']+pose.get('bend',26))
    cap(d,sh2,e,3.6,3.2,P['fur']);cap(d,e,hd,3.2,2.6,P['fur']);d.rectangle((e[0]-3,e[1]-1,e[0]+3,e[1]+2),fill=P['belt'])
    ca=pose['club'];c0=fk(hd,-6,ca);c1=fk(hd,20,ca)
    cap(d,c0,c1,1.8,3.4,P['club']);cap(d,c0,fk(hd,1,ca),1.8,2,P['clubD'])
    for q in (12,16,19):
        n=fk(hd,q,ca);d.point((int(n[0]+2),int(n[1])),fill=P['nail']);d.point((int(n[0]-2),int(n[1])),fill=P['nail'])
    d.ellipse((hd[0]-2.6,hd[1]-2.6,hd[0]+2.6,hd[1]+2.6),fill=P['fur'])
    # contorno + sombra simples
    a=big.getchannel('A').point(lambda v:255 if v>100 else 0);big.putalpha(a)
    px=big.load();out=Image.new('RGBA',(W,H),(0,0,0,0));po=out.load()
    for y in range(H):
        for x in range(W):
            if px[x,y][3]:po[x,y]=px[x,y]
    for y in range(H):
        for x in range(W):
            if not px[x,y][3]:
                for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
                    xx,yy=x+dx,y+dy
                    if 0<=xx<W and 0<=yy<H and px[xx,yy][3]:po[x,y]=P['k']+(255,);break
    return out
def walk(t):
    ph=2*math.pi*t;A=30;K=34
    hN=A*math.sin(ph);hF=-hN
    kN=max(2,K*max(0,math.cos(ph))+6);kF=max(2,K*max(0,-math.cos(ph))+6)
    # perna que avança dobra o joelho; a de apoio fica quase reta
    kN=6+K*max(0,math.sin(ph+math.pi/2));kF=6+K*max(0,-math.sin(ph+math.pi/2))
    return dict(hN=hN,kN=kN,hF=hF,kF=kF,aN=10+hN*.15,aF=-hN*.7,club=70+hN*.2,bob=-abs(math.cos(ph))*1.6,lean=1,tail=math.sin(ph)*2,hb=math.sin(ph*2)*.6)
def idle(t):
    ph=2*math.pi*t;b=math.sin(ph)
    return dict(hN=10,kN=14,hF=-8,kF=12,aN=8,aF=4,club=72,bob=-b*.8,lean=1,tail=b*1.5,hb=b*.8)
def attack(t):
    # 0..1: preparo (0-.35), pico, golpe (.5-.65), impacto, recupera
    def lerp(a,b,u):return a+(b-a)*u
    keys=[(0,dict(hN=14,kN=16,hF=-14,kF=14,aN=8,aF=6,club=72,bend=26,lean=1,bob=0,tail=0)),
          (.22,dict(hN=8,kN=30,hF=-20,kF=28,aN=-40,aF=30,club=150,bend=30,lean=-3,bob=1.5,tail=2)),
          (.42,dict(hN=6,kN=10,hF=-24,kF=10,aN=-140,aF=60,club=200,bend=14,lean=-5,bob=-1,tail=3)),
          (.56,dict(hN=34,kN=44,hF=-36,kF=10,aN=60,aF=-30,club=-20,bend=20,lean=5,bob=3,tail=-2)),
          (.70,dict(hN=34,kN=44,hF=-36,kF=10,aN=70,aF=-30,club=-34,bend=20,lean=6,bob=3.5,tail=-3)),
          (1.0,dict(hN=14,kN=16,hF=-14,kF=14,aN=8,aF=6,club=72,bend=26,lean=1,bob=0,tail=0))]
    for i in range(len(keys)-1):
        t0,a=keys[i];t1,b=keys[i+1]
        if t0<=t<=t1:
            u=(t-t0)/(t1-t0);u=u*u*(3-2*u) if i not in(2,) else u*u
            r={k:lerp(a[k],b[k],u) for k in a};r['hb']=0;return r
    return keys[-1][1]
if __name__=='__main__':
    o=sys.argv[1];os.makedirs(o,exist_ok=True)
    segs=[('ANDAR',walk,24,3),('ATAQUE',attack,16,3),('PARADO',idle,20,2)]
    n=0;S=7
    for name,fn,N,reps in segs:
        for r in range(reps):
            for i in range(N):
                f=render(fn(i/N));big=f.resize((W*S,H*S),Image.NEAREST)
                bg=Image.new('RGBA',(W*S,H*S+50),(52,64,50,255))
                from PIL import ImageDraw as D
                dd=D.Draw(bg);dd.rectangle((0,(GY+1)*S,W*S,H*S+50),fill=(70,56,44,255))
                bg.alpha_composite(big,(0,0))
                # impacto do ataque: arco simples
                if name=='ATAQUE' and .56<=i/N<=.75:
                    dd.arc((W*S*.55,H*S*.35,W*S*.98,H*S*.95),300,60,fill=(255,240,180,255),width=6)
                dd.text((10,H*S+14),'Rei dos Ratos (pixel art por codigo): '+name,fill=(255,255,255,255))
                bg.convert('RGB').save('%s/f%03d.png'%(o,n));n+=1
    print(n)
