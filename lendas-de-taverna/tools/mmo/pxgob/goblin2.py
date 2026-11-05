"""Goblin top-down v3: corpo e cabeça mais angulosos (testa reta, maçã do rosto, queixo), tronco trapezoidal, pernas e braços articulados (IK de 2 ossos)."""
import math
from engine2 import *
from weapons import *
W,H=64,64;OX,OY=10,12
def ik(S,T,l1,l2,bend):
    dx,dy=T[0]-S[0],T[1]-S[1];d=min(math.hypot(dx,dy),l1+l2-.01);d=max(d,abs(l1-l2)+.01)
    a=math.atan2(dy,dx);c=(l1*l1+d*d-l2*l2)/(2*l1*d);c=max(-1,min(1,c));b=math.acos(c)*bend
    return (S[0]+l1*math.cos(a+b),S[1]+l1*math.sin(a+b))
def goblin(P):
    g=Img(W,H);g.ox,g.oy=OX,OY;b=P.get('bob',0);lean=P.get('lean',0);hdx,hdy=P.get('head',(0,0))
    def Y(y):return y+b
    wt=P.get('weapon','sword');hR=P.get('handR',(34,31));hL=P.get('handL',(10,31));wa=P.get('wang',15)
    SRp=(29.5+lean*.4,Y(24.2));SLp=(14.5+lean*.4,Y(24.2))
    # ---- arma atrás
    behind=P.get('behind',False)
    def weapon():
        if wt=='sword':return sword(g,hR,wa)
        if wt=='dagger':return dagger(g,hR,wa)
        if wt=='axe':return axe(g,hR,wa)
        if wt=='hammer':return hammer(g,hR,wa)
        if wt=='staff':return staff(g,hR,wa,glow=P.get('glow',0))
        if wt=='bow':return None
    tip=None
    if behind:tip=weapon()
    # ---- orelhas (angulosas)
    ea=P.get('earL',0),P.get('earR',0)
    for s,e in((-1,ea[0]),(1,ea[1])):
        bx=22+s*8
        pts=[(bx-s*1,Y(13.5)),(bx+s*14,Y(9.5)+e*.2),(bx+s*12.5,Y(15.5)+e*.2),(bx+s*7,Y(18.3)),(bx,Y(18.6))]
        g.shape(bevel(pts,2.2),'O')
        ins=[(bx+s*1.2,Y(14.6)),(bx+s*10,Y(11.7)+e*.2),(bx+s*9.5,Y(15)+e*.2),(bx+s*5.5,Y(17.2)),(bx+s*1.2,Y(17.4))]
        g.shape(bevel(ins,1.2),'H',outline=False,bias=-.15)
    # ---- pernas (IK) e botas
    fl=P.get('feet',(17.5,38,26.5,38))
    for hipx,fx,fy,s in((19.5,fl[0],fl[1],-1),(24.5,fl[2],fl[3],1)):
        hip=(hipx,Y(32.5));foot=(fx,Y(fy)-(0));kn=ik(hip,(fx,Y(fy)-1.5),4.2,4.2,-s*.6)
        g.shape(tube(hip,kn,2.5,2.2),'O');g.shape(tube(kn,(fx,Y(fy)-1.5),2.2,2.0),'O')
        g.shape(bevel([(fx-3.6,Y(fy)-1.8),(fx+3.6,Y(fy)-1.8),(fx+4,Y(fy)+1.6),(fx-4,Y(fy)+1.6)],1.5),'P')
        for k in(-2.2,0,2.2):g.dot(fx+k,Y(fy)+1,RAMPS['W'][2])
    # ---- tronco (trapézio) + tanga + cinto
    g.shape(bevel([(15.5,Y(23)),(28.5,Y(23)),(27.5,Y(29)),(26,Y(33.5)),(18,Y(33.5)),(16.5,Y(29))],3.0),'O')
    g.shape(bevel([(17,Y(31.5)),(27,Y(31.5)),(28.5,Y(35.5)),(25.6,Y(38)),(22,Y(35.2)),(18.4,Y(38)),(15.5,Y(35.5))],1.8),'P',dither=.05)
    g.shape(tube((16.2,Y(31.4)),(27.8,Y(31.4)),.9,.9),'D',outline=False)
    g.shape(bevel([(21,Y(30.4)),(23,Y(30.4)),(23,Y(32.4)),(21,Y(32.4))],.7),'M',outline=False)
    g.shape(tube((16.5,Y(23.6)),(26.5,Y(31)),.7,.7),'P',outline=False,flat=2)       # correia
    # ---- braço esquerdo (+ escudo)
    eL=ik(SLp,(hL[0],Y(hL[1])),5.4,5.4,-.7);eR=ik(SRp,(hR[0],Y(hR[1])),5.4,5.4,.7)
    if P.get('shield'):shield(g,(hL[0]-2.5,Y(hL[1])-1))
    g.shape(tube(SLp,eL,2.5,2.1),'O');g.shape(tube(eL,(hL[0],Y(hL[1])),2.1,1.9),'O');g.shape(ellipsoid(hL[0],Y(hL[1]),2.5,2.4),'H')
    if wt=='bow':
        pull=P.get('pull');bow(g,(hL[0],Y(hL[1])),pull,arrow=P.get('arrow'))
    # ---- braço direito
    g.shape(tube(SRp,eR,2.5,2.1),'O');g.shape(tube(eR,(hR[0],Y(hR[1])),2.1,1.9),'O')
    if not behind and wt!='bow':tip=weapon()
    g.shape(ellipsoid(hR[0],Y(hR[1]),2.5,2.4),'H')
    # ombreiras
    g.shape(ellipsoid(14,Y(23.2),4.4,2.9),'A',dither=.04);g.shape(ellipsoid(30,Y(23.2),4.4,2.9),'A',dither=.04)
    # ---- cabeça angulosa
    hx,hy=22+hdx,Y(16)+hdy
    pts=[(hx-6.5,hy-7.2),(hx+6.5,hy-7.2),(hx+8.4,hy-3.6),(hx+8.4,hy+1.8),(hx+5.4,hy+6.4),(hx,hy+8.2),(hx-5.4,hy+6.4),(hx-8.4,hy+1.8),(hx-8.4,hy-3.6)]
    g.shape(bevel(pts,3.4),'O',dither=.03)
    g.shape(bevel([(hx-3.2,hy-6.6),(hx+3.2,hy-6.6),(hx+2.4,hy-4.6),(hx-2.4,hy-4.6)],1.0),'H',outline=False,flat=1)      # marca dourada
    for s in(-1,1):   # sobrancelha pesada inclinada
        g.shape(bevel([(hx+s*1.2,hy-2.8),(hx+s*7.6,hy-4.0),(hx+s*7.6,hy-2.0),(hx+s*1.2,hy-.4)],.9),'O',outline=False,bias=-.45)
    for s in(-1,1):
        ex=hx+s*4.2-1
        g.dot(ex,hy+0,RAMPS['W'][0]);g.dot(ex+1,hy+0,RAMPS['E'][1]);g.dot(ex,hy+1,RAMPS['O'][4]);g.dot(ex+1,hy+1,RAMPS['O'][4])
    g.shape(bevel([(hx-1.8,hy+1.6),(hx+1.8,hy+1.6),(hx+1.2,hy+3.6),(hx-1.2,hy+3.6)],.8),'O',outline=False,bias=-.2)      # nariz
    for dx in range(-3,3):g.dot(hx+dx,hy+5.2,RAMPS['O'][4])
    for s in(-1,1):
        g.dot(hx+s*3-(1 if s<0 else 0),hy+5.2,RAMPS['W'][0]);g.dot(hx+s*3-(1 if s<0 else 0),hy+4.2,RAMPS['W'][0])
    if P.get('fx'):P['fx'](g,tip)
    return g.finish()
