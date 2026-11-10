"""Rei dos Ratos em pixel art por código, versão refinada: 176x176 (2x), sombreamento por parte (luz no alto à esquerda), textura de pelo,
remendos no manto, coroa de latas e garfos, cano enferrujado, bigodes, sombra no chão. Reaproveita as poses de ratpx.py.
Uso: python3 ratpx2.py <pasta_saida>"""
import sys,os,math,random
from PIL import Image,ImageDraw
import ratpx as R1
Z=2;W=88*Z;H=106*Z;GY=98
C=dict(k=(26,18,26),
 fur=[(70,56,50),(104,86,72),(136,114,92),(166,142,114)],
 skin=[(150,92,100),(196,138,142),(226,170,170)],
 cape=[(70,66,30),(104,98,44),(136,128,60),(168,158,84)],
 cloth=[(78,82,80),(112,116,112),(146,150,142)],
 belt=[(58,34,22),(96,60,36),(134,88,52)],
 brass=[(120,100,40),(184,160,70),(236,214,120)],
 club=[(56,32,24),(100,60,42),(140,88,60),(172,112,78)],
 rust=(150,70,38),nail=[(110,110,116),(190,190,198)],
 tin=[(86,84,80),(140,138,130),(196,194,184)],
 steel=[(70,74,84),(120,126,138),(176,182,194)],
 eye=(176,255,96),eyeD=(54,96,30),tooth=[(190,170,110),(240,226,170)],claw=(48,40,40),tail=[(150,98,104),(196,144,146),(224,176,174)],whisk=(190,176,150))
def S(v):return v*Z
class G:
    def __init__(s):s.im=Image.new('RGBA',(W,H),(0,0,0,0));s.d=ImageDraw.Draw(s.im)
    def ell(s,cx,cy,rx,ry,col):s.d.ellipse((S(cx-rx),S(cy-ry),S(cx+rx),S(cy+ry)),fill=col)
    def sell(s,cx,cy,rx,ry,pal,k=3):
        # elipse sombreada: camadas deslocadas para o alto-esquerda
        s.ell(cx,cy,rx,ry,pal[0])
        for i in range(1,k):
            f=1-.22*i;o=.16*i
            s.ell(cx-rx*o,cy-ry*o*1.1,rx*f,ry*f,pal[min(i,len(pal)-1)])
        if len(pal)>k:s.ell(cx-rx*.42,cy-ry*.46,rx*.28,ry*.22,pal[k])
    def cap(s,a,b,r0,r1,col):
        n=max(2,int(math.hypot(b[0]-a[0],b[1]-a[1])*Z*1.4))
        for i in range(n+1):
            t=i/n;x=a[0]+(b[0]-a[0])*t;y=a[1]+(b[1]-a[1])*t;r=r0+(r1-r0)*t;s.ell(x,y,r,r,col)
    def scap(s,a,b,r0,r1,pal):
        s.cap(a,b,r0,r1,pal[0]);
        for i,(o,f) in enumerate(((.55,.78),(1.0,.5),(1.4,.24))):
            if i+1>=len(pal):break
            s.cap((a[0]-o*.5,a[1]-o*.6),(b[0]-o*.5,b[1]-o*.6),r0*f,r1*f,pal[i+1])
    def poly(s,pts,col):s.d.polygon([(S(x),S(y)) for x,y in pts],fill=col)
    def line(s,a,b,col,w=1):s.d.line((S(a[0]),S(a[1]),S(b[0]),S(b[1])),fill=col,width=w)
    def pt(s,x,y,col):s.d.point((int(S(x)),int(S(y))),fill=col)
    def rect(s,x0,y0,x1,y1,col):s.d.rectangle((S(x0),S(y0),S(x1)-1,S(y1)-1),fill=col)
def stip(g,cx,cy,rx,ry,seed,n,cols):
    r=random.Random(seed)
    for _ in range(n):
        a=r.random()*6.283;q=math.sqrt(r.random());x=cx+math.cos(a)*rx*q;y=cy+math.sin(a)*ry*q;g.pt(x,y,r.choice(cols))
def fk(p,L,ang):a=math.radians(ang);return (p[0]+L*math.sin(a),p[1]+L*math.cos(a))
def leg(g,hip,hd,kn,pal,seed,near):
    k=fk(hip,11,hd);a=fk(k,11,hd-kn)
    g.scap(hip,k,4.4,3.7,pal);g.sell(k[0],k[1],3.4,3.4,pal)
    g.scap(k,a,3.5,2.5,pal)
    stip(g,(hip[0]+k[0])/2,(hip[1]+k[1])/2,3.5,6,seed,26,[pal[0],pal[2]]);stip(g,(k[0]+a[0])/2,(k[1]+a[1])/2,2.6,6,seed+1,18,[pal[0],pal[2]])
    # bota/pata: pé com garras
    fo=(a[0]+5.5,a[1]+1.3);g.scap(a,fo,2.6,1.7,pal)
    for i in range(3):
        y=fo[1]-1.3+i*1.2;g.line((fo[0]+.5,y),(fo[0]+2.4,y+.3),C['claw'])
    if near:g.rect(k[0]-3.4,k[1]+3.2,k[0]+3.4,k[1]+5.2,C['steel'][1])    # tira de sucata
def render(pose):
    g=G();hipx=34;lean=pose.get('lean',0)
    def feet():
        res=[]
        for hd,kn in ((pose['hF'],pose['kF']),(pose['hN'],pose['kN'])):
            k=fk((0,0),11,hd);a=fk(k,11,hd-kn);res.append(a[1])
        return max(res)
    hipy=GY-feet()-2.5+pose.get('bob',0);hip=(hipx,hipy)
    g.ell(hipx+4,GY+1.5,19,2.6,(20,16,22,150))   # sombra no chão
    # cauda segmentada
    tw=pose.get('tail',0);pts=[(hipx-8,hipy+2),(hipx-17,hipy+6+tw),(hipx-25,hipy+3-tw),(hipx-31,hipy+7)]
    for i in range(3):
        g.scap(pts[i],pts[i+1],2.3-i*.45,1.8-i*.45,C['tail'])
        mx=(pts[i][0]+pts[i+1][0])/2;my=(pts[i][1]+pts[i+1][1])/2
        for j in (-.3,.3):g.pt(mx+j*9,my+j*5,C['tail'][0])
    leg(g,hip,pose['hF'],pose['kF'],C['fur'][:3],11,False)
    # braço longe (escuro)
    sh=(hipx+7+lean,hipy-23);e=fk(sh,8,-pose['aF']);h=fk(e,8,-pose['aF']+22)
    g.scap(sh,e,3.3,2.9,C['fur'][:3]);g.scap(e,h,2.9,2.2,C['fur'][:3]);g.sell(h[0],h[1],2.4,2.4,C['fur'][:3])
    bx=hipx+2+lean*.5;by=hipy-12
    # corpo de pelo
    g.sell(bx,by,13.5,13,C['fur'])
    # tufos de pelo na silhueta
    r=random.Random(5)
    for i in range(14):
        a=-0.5+i*.5;x=bx+math.cos(a+3.1)*13.5;y=by+math.sin(a+3.1)*13;g.poly([(x,y),(x-1.6,y+1.8),(x+.6,y+2.8)],C['fur'][1])
    stip(g,bx,by,12,11,21,120,[C['fur'][0],C['fur'][3],C['fur'][2]])
    # barriga rosada com tufos
    g.sell(bx+1,by+5,10,10,C['skin'],3);stip(g,bx+1,by+5,9,9,22,50,[C['skin'][0],C['skin'][2]])
    for (px_,py_,rr) in ((bx-3,by+2,1.8),(bx+5,by-3,1.4),(bx-7,by-5,1.5)):g.ell(px_,py_,rr,rr*.8,C['skin'][1])   # manchas de sarna
    # tanga rasgada
    g.poly([(bx-10,by+8),(bx+10,by+8),(bx+8,by+20),(bx+5,by+16),(bx+2,by+21),(bx-2,by+16),(bx-5,by+20),(bx-9,by+15)],C['cloth'][0])
    g.poly([(bx-10,by+8),(bx+3,by+8),(bx+1,by+17),(bx-3,by+15),(bx-5,by+19),(bx-9,by+15)],C['cloth'][1])
    # cinto + fivela (tampinha)
    g.rect(bx-12,by+5,bx+12,by+8.6,C['belt'][1]);g.rect(bx-12,by+5,bx+12,by+6.2,C['belt'][2]);g.rect(bx-12,by+7.6,bx+12,by+8.6,C['belt'][0])
    g.sell(bx+1,by+6.8,3,3,C['brass'],2);g.ell(bx+1,by+6.8,1.2,1.2,C['brass'][0])
    for i in range(-5,6,3):g.pt(bx+i*2,by+6.6,C['belt'][0])
    # manto de trapos com remendos e barra rasgada
    cp=[(bx-14,by-14),(bx-4,by-22),(bx+12,by-20),(bx+16,by-12),(bx+10,by-8),(bx+5,by-5),(bx+2,by-9),(bx-1,by-3),(bx-5,by-6),(bx-9,by-1),(bx-12,by-5),(bx-15,by-1)]
    g.poly(cp,C['cape'][1]);g.poly([(bx-14,by-14),(bx-4,by-22),(bx+4,by-21),(bx-3,by-12),(bx-8,by-3),(bx-15,by-1)],C['cape'][2])
    g.poly([(bx+5,by-5),(bx+10,by-8),(bx+16,by-12),(bx+12,by-6),(bx+8,by-3)],C['cape'][0])
    g.rect(bx-10,by-15,bx-3,by-9,C['cape'][3]);g.rect(bx-10,by-15,bx-3,by-14.4,C['cape'][2])   # remendo
    for i in range(4):g.pt(bx-9.5+i*2,by-12,C['cape'][0])
    g.rect(bx+3,by-17,bx+8,by-12,C['cape'][0])
    stip(g,bx,by-12,12,7,31,50,[C['cape'][0],C['cape'][3]])
    g.sell(bx+12,by-9,2.2,2.2,C['cape'],2)   # nó
    # cabeça
    hx=bx+13+lean*.5;hy=by-23+pose.get('hb',0)
    g.sell(hx,hy,8,7.2,C['fur']);stip(g,hx,hy,7,6,41,40,[C['fur'][0],C['fur'][3]])
    g.scap((hx+2,hy-.5),(hx+15,hy+3),5,1.7,C['fur']);stip(g,hx+8,hy+1.5,6,3,42,24,[C['fur'][0],C['fur'][3]])
    g.sell(hx+15.4,hy+3,2,1.6,C['skin'],2);g.pt(hx+15,hy+2.2,(255,230,230))
    # orelha com interior rosa
    g.poly([(hx-6.5,hy-5),(hx-3,hy-13),(hx+1.5,hy-6)],C['fur'][1]);g.poly([(hx-5,hy-6),(hx-3,hy-11),(hx,hy-6.5)],C['skin'][1])
    # olho brilhante, sobrancelha e cicatriz
    g.rect(hx+3.6,hy-3.4,hx+8,hy-1,C['eyeD']);g.rect(hx+4.6,hy-2.8,hx+7.4,hy-1.4,C['eye']);g.pt(hx+5,hy-2.6,(240,255,210))
    g.line((hx+3,hy-4.6),(hx+8.6,hy-3.2),C['fur'][0],1)
    g.line((hx+1,hy+1),(hx+4,hy+4),C['skin'][0])
    # dentes e boca
    g.line((hx+8,hy+4.8),(hx+15,hy+4.2),C['k'])
    for xx in (8.2,11):
        g.rect(hx+xx,hy+4.6,hx+xx+2,hy+7.8,C['tooth'][0]);g.rect(hx+xx,hy+4.6,hx+xx+1.2,hy+7.2,C['tooth'][1])
    for i in range(3):g.line((hx+14,hy+3+i*.8),(hx+19.5,hy+1.5+i*2.2),C['whisk'])   # bigodes
    # coroa de lata, tampinhas e garfos
    g.rect(hx-6.5,hy-13,hx+5.5,hy-7.5,C['tin'][1]);g.rect(hx-6.5,hy-13,hx+5.5,hy-11.6,C['tin'][2]);g.rect(hx-6.5,hy-8.6,hx+5.5,hy-7.5,C['tin'][0])
    for i in range(-3,4):g.line((hx-1+i*1.8,hy-12.5),(hx-1+i*1.8,hy-8.2),C['tin'][0])
    for xx,hh in ((hx-5.5,6),(hx-1.5,8),(hx+3,5.5)):
        g.line((xx,hy-13),(xx,hy-13-hh),C['tin'][2]);g.line((xx-1,hy-13-hh),(xx-1,hy-13-hh+2),C['tin'][2]);g.line((xx+1,hy-13-hh),(xx+1,hy-13-hh+2),C['tin'][2])
    g.sell(hx+1,hy-10,1.8,1.8,C['brass'],2)
    # perna perto
    leg(g,(hipx+2,hipy),pose['hN'],pose['kN'],C['fur'],13,True)
    # braço perto + braçadeira + cano
    sh2=(hipx+3+lean,hipy-23);e=fk(sh2,8,-pose['aN']);hd=fk(e,8,-pose['aN']+pose.get('bend',26))
    g.scap(sh2,e,3.2,2.9,C["fur"]);stip(g,(sh2[0]+e[0])/2,(sh2[1]+e[1])/2,3,5,51,18,[C['fur'][0],C['fur'][3]])
    g.scap(e,hd,2.9,2.4,C["fur"])
    m=((e[0]+hd[0])/2,(e[1]+hd[1])/2);g.sell(m[0],m[1],3.4,3.0,C['steel'],2);g.pt(m[0]-1,m[1]-1,C['steel'][2])   # braçadeira de sucata
    ca=pose['club'];c0=fk(hd,-6,ca);c1=fk(hd,21,ca)
    g.scap(c0,c1,1.8,3.7,C['club'])
    for q in (-3,2,8):g.pt(*fk(hd,q,ca),C['rust'])
    for q in (11,15,19):
        n=fk(hd,q,ca);g.line((n[0]+1,n[1]),(n[0]+3.2,n[1]-.6),C['nail'][1]);g.line((n[0]-1,n[1]),(n[0]-3.2,n[1]+.6),C['nail'][0])
    g.sell(hd[0],hd[1],2.8,2.6,C['fur'])
    for i in range(3):g.pt(hd[0]+1.5,hd[1]+i-1,C['claw'])
    # contorno: 1 px escuro e leve contorno interno mais suave
    im=g.im;a=im.getchannel('A').point(lambda v:255 if v>90 else 0);im.putalpha(a)
    px=im.load();out=im.copy();po=out.load()
    for y in range(H):
        for x in range(W):
            if px[x,y][3]==0:
                for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
                    xx,yy=x+dx,y+dy
                    if 0<=xx<W and 0<=yy<H and px[xx,yy][3]==255 and px[xx,yy][:3]!=(20,16,22):po[x,y]=C['k']+(255,);break
    return out
if __name__=='__main__':
    o=sys.argv[1];os.makedirs(o,exist_ok=True)
    segs=[('ANDAR',R1.walk,24,3),('ATAQUE',R1.attack,16,3),('PARADO',R1.idle,20,2)];n=0;SC=4
    for name,fn,N,reps in segs:
        for r in range(reps):
            for i in range(N):
                f=render(fn(i/N));big=f.resize((W*SC,H*SC),Image.NEAREST)
                bg=Image.new('RGBA',(W*SC,H*SC+50),(54,66,52,255));dd=ImageDraw.Draw(bg)
                dd.rectangle((0,(GY+3)*Z*SC,W*SC,H*SC+50),fill=(72,58,46,255))
                bg.alpha_composite(big,(0,0))
                if name=='ATAQUE' and .56<=i/N<=.75:
                    dd.arc((W*SC*.55,H*SC*.35,W*SC*.98,H*SC*.95),300,60,fill=(255,240,180,255),width=8)
                dd.text((10,H*SC+16),'Rei dos Ratos (pixel art por codigo, refinado): '+name,fill=(255,255,255,255))
                bg.convert('RGB').save('%s/f%03d.png'%(o,n));n+=1
    print(n)
