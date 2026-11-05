"""Goblin em pixel art desenhado do zero por código (vista frontal): estilo de poucas cores, contorno preto e sombra no canto inferior direito."""
import math
from engine import *
W,H=56,64;OX,OY=4,10
def D(th,side):s=math.radians(th);return ((-math.sin(s) if side=='L' else math.sin(s)),math.cos(s))
def add(p,v,l):return (p[0]+v[0]*l,p[1]+v[1]*l)
def goblin(P):
    """P: bob, head(dx,dy), earL, earR (graus), legs (liftL,liftR,spread), armL(θ1,θ2), armR(θ1,θ2), club(φ,len,front), eyes, lean, mouth"""
    g=Img(W,H);bob=P.get('bob',0);hx,hy=P.get('head',(0,0));lean=P.get('lean',0)
    cx=24+OX;by=OY+bob
    def X(x):return x+OX
    def Y(y):return y+OY+bob
    club_front=P.get('club',(12,15,False))[2]
    # clava atrás do corpo quando levantada
    # ---- mãos e braços (pontos)
    aL=P.get('armL',(14,14));aR=P.get('armR',(24,12))
    SL=(X(17.5+lean*.5),Y(25));SR=(X(30.5+lean*.5),Y(25))
    eL=add(SL,D(aL[0],'L'),5.5);wL=add(eL,D(aL[1],'L'),4.6)
    eR=add(SR,D(aR[0],'R'),5.5);wR=add(eR,D(aR[1],'R'),4.6)
    phi,clen,_=P.get('club',(12,15,False));cd=(math.sin(math.radians(phi)),-math.cos(math.radians(phi)))
    def club():
        p0=add(wR,cd,-3.2);p1=add(wR,cd,clen*.62);tip=add(wR,cd,clen)
        g.shape(capsule(p0,p1,1.4,1.7),'B')
        g.shape(capsule(p1,tip,1.7,2.4),'B',outline=False,shade=.3)
        # cabeça nodosa
        hc=add(wR,cd,clen+1.0);g.hc=hc;g.shape(ellipse(hc[0],hc[1],3.5,3.3,phi),'B')
        for k in range(5):
            a=math.radians(phi+k*72+20);sp=(hc[0]+math.sin(a)*3.4,hc[1]-math.cos(a)*3.4);e=(hc[0]+math.sin(a)*5.6,hc[1]-math.cos(a)*5.6)
            n=((-(e[1]-sp[1])*.35),((e[0]-sp[0])*.35));g.shape(poly([(sp[0]+n[0],sp[1]+n[1]),(sp[0]-n[0],sp[1]-n[1]),e]),'S',outline=False,flat=True)
        g.shape(ellipse(hc[0]-.4,hc[1]-.5,.8,.8),'W',outline=False,flat=True)
    if not club_front:club()
    # ---- orelhas
    eaL,eaR=P.get('earL',0),P.get('earR',0);hh=(X(24+hx),Y(17+hy))
    for side,ea in(('L',eaL),('R',eaR)):
        s=-1 if side=='L' else 1;base=(hh[0]+s*7.5,hh[1]-1.5)
        pts=[(-1,-3),(8,-10),(9,-5.5),(8,-1),(-1,3.2)]
        pts=[(base[0]+s*p[0]*1.0,base[1]+p[1]) for p in pts]
        pts=[rot(p,base,s*ea) for p in pts]
        g.shape(poly(pts),'G')
        inn=[(-.2,-1.6),(6,-7),(6.5,-4.5),(5.5,-1.4),(-.2,1.6)]
        inn=[rot((base[0]+s*p[0]*.95+s*.9,base[1]+p[1]),base,s*ea) for p in inn]
        g.shape(poly(inn),'T',outline=False,shade=.2)
    # ---- pernas
    lL,lR,sp=P.get('legs',(0,0,0))
    for side,lift,s in(('L',lL,-1),('R',lR,1)):
        hipx=cx+s*3.6;hip=(hipx,Y(34));kn=(hipx+s*(.6+sp)+s*lift*.35,Y(38.6)-lift*.55);an=(hipx+s*(.9+sp)+s*lift*.5,Y(41.8)-lift);ft=(an[0]+s*.6,an[1]+1.8)
        g.shape(capsule(hip,kn,3.0,2.7),'G',shade=.34);g.shape(capsule(kn,an,2.7,2.4),'G',shade=.34)
        g.shape(ellipse(ft[0]+s*.6,ft[1],4.2,2.0),'G',shade=.3)
        for k in(-1.7,0,1.7):g.dot(int(ft[0]+s*.3+k),int(ft[1]+.6),OUT) if False else None
    # ---- tronco, tanga e correia
    bx,byy=cx+lean*.5,Y(29)
    g.shape(ellipse(bx,byy,6.8,6.2),'G',shade=.38)
    g.shape(poly([(bx-6.2,Y(33)),(bx+6.2,Y(33)),(bx+6.6,Y(36)),(bx+4.6,Y(38.8)),(bx+2.6,Y(36.6)),(bx,Y(39.2)),(bx-2.6,Y(36.6)),(bx-4.6,Y(38.8)),(bx-6.6,Y(36))]),'B',shade=.4)
    g.shape(capsule((bx-4.5,Y(24)),(bx+3.8,Y(32.5)),.9,.9),'B',outline=False,flat=True)
    g.shape(capsule((bx-6.4,Y(32.8)),(bx+6.4,Y(32.8)),1.0,1.0),'B',outline=False,flat=True)
    g.dot(int(bx-.5),int(Y(28.4)),PAL['S'][0]);g.dot(int(bx+.5),int(Y(28.4)),PAL['S'][0]);g.dot(int(bx),int(Y(29.4)),PAL['S'][1])
    # ---- braços
    g.shape(capsule(SL,eL,2.5,2.2),'G',shade=.34);g.shape(capsule(eL,wL,2.2,2.0),'G',shade=.34);g.shape(ellipse(wL[0],wL[1]+.5,2.5,2.4),'G',shade=.3)
    g.shape(capsule(SR,eR,2.5,2.2),'G',shade=.34);g.shape(capsule(eR,wR,2.2,2.0),'G',shade=.34)
    if club_front:club()
    g.shape(ellipse(wR[0],wR[1],2.6,2.5),'G',shade=.3)
    # ---- cabeça
    g.shape(ellipse(hh[0],hh[1],8.4,6.8),'G',shade=.42)
    hx0,hy0=hh
    ey=P.get('eyes','open')
    for s in(-1,1):
        ex=int(hx0+s*3.6-1)
        if ey=='open':
            for dx in(0,1,2):g.dot(ex+dx,int(hy0-.5),PAL['Y'][0]);g.dot(ex+dx,int(hy0+.5),PAL['Y'][0] if dx!=(1 if s>0 else 1) else OUT)
            g.dot(ex+(2 if s<0 else 0),int(hy0-2.5),OUT);g.dot(ex+1,int(hy0-1.5),OUT);g.dot(ex+(0 if s<0 else 2),int(hy0-1.5),OUT)
        elif ey=='shut':
            for dx in(0,1,2):g.dot(ex+dx,int(hy0+.5),OUT)
        else:  # dano: olho espremido
            for dx in(0,1,2):g.dot(ex+dx,int(hy0-.5+dx*(.8 if s<0 else -.8)),OUT)
    g.dot(int(hx0-1),int(hy0+2.5),PAL['G'][2]);g.dot(int(hx0),int(hy0+2.5),PAL['G'][2])        # narinas
    mo=P.get('mouth',0)
    for dx in range(-3,3):g.dot(int(hx0+dx),int(hy0+4.4+mo),OUT)
    for s in(-1,1):
        g.dot(int(hx0+s*3-(1 if s<0 else 0)),int(hy0+4.4+mo),PAL['W'][0]);g.dot(int(hx0+s*3-(1 if s<0 else 0)),int(hy0+3.4+mo),PAL['W'][0])
    for (dx,dy,c) in P.get('fxrel',[]):g.dot(int(g.hc[0]+dx),int(g.hc[1]+dy),c)
    return g
