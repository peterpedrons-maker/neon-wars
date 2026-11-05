"""Armas do jogo desenhadas em pixel art (espada, machado, adaga, cajado, arco, martelo). Ângulo 0 = para cima, + = sentido horário."""
import math
from engine2 import *
def dirv(a):r=math.radians(a);return (math.sin(r),-math.cos(r))
def at(p,d,l):return (p[0]+d[0]*l,p[1]+d[1]*l)
def perp(d):return (-d[1],d[0])
def sword(g,h,a,L=13):
    d=dirv(a);n=perp(d)
    g.shape(tube(at(h,d,-2.5),at(h,d,.6),.9,.9),'D')
    g.shape(tube(at(at(h,d,.8),n,-3),at(at(h,d,.8),n,3),.8,.8),'H')
    b0=at(h,d,1.4);b1=at(h,d,L-2.5);tip=at(h,d,L)
    g.shape(bevel([at(b0,n,-1.5),at(b0,n,1.5),at(b1,n,1.2),tip,at(b1,n,-1.2)],1.4),'M')
    return tip
def dagger(g,h,a):return sword(g,h,a,L=8)
def axe(g,h,a,L=12):
    d=dirv(a);n=perp(d)
    g.shape(tube(at(h,d,-3),at(h,d,L),.95,.95),'D')
    top=at(h,d,L-1)
    pts=[at(at(top,d,1.5),n,-1),at(at(top,d,2.5),n,-5.5),at(at(top,d,-3.5),n,-5.8),at(at(top,d,-2.5),n,-1)]
    g.shape(bevel(pts,1.6),'M')
    g.shape(tube(at(top,d,-2),at(top,d,2.5),1.3,1.1),'M',outline=False)
    return at(top,n,-5.5)
def hammer(g,h,a,L=12):
    d=dirv(a);n=perp(d)
    g.shape(tube(at(h,d,-3),at(h,d,L),1.0,1.0),'D')
    top=at(h,d,L)
    pts=[at(at(top,d,3.5),n,-4),at(at(top,d,3.5),n,4),at(at(top,d,-2.5),n,4),at(at(top,d,-2.5),n,-4)]
    g.shape(bevel(pts,1.8),'M')
    return at(top,d,3.5)
def staff(g,h,a,L=19,glow=0):
    d=dirv(a)
    g.shape(tube(at(h,d,-5),at(h,d,L),.95,.95),'D')
    top=at(h,d,L+1.5)
    if glow:
        for r,t in((glow+3,3),(glow+1.6,2)):
            g.shape(ellipsoid(top[0],top[1],r,r),'E',outline=False,flat=t)
    g.shape(ellipsoid(top[0],top[1],2.6,2.6),'E')
    g.shape(tube(at(h,d,L-3),at(h,d,L-.5),1.6,2.2),'H',outline=False)
    return top
def bow(g,hand,pull=None,a=0,hw=7.5,arrow=None):
    """arco vertical na mão esquerda; pull = posição da mão que puxa a corda"""
    cx,cy=hand;top=(cx+1.5,cy-hw);bot=(cx+1.5,cy+hw);grip=(cx,cy)
    pts=[top,(cx-1.5,cy-hw*.55),(cx-2.4,cy),(cx-1.5,cy+hw*.55),bot]
    for i in range(4):g.shape(tube(pts[i],pts[i+1],.9,.9),'D',outline=(i==0 or True))
    string=pull if pull else (cx+1.5,cy)
    g.shape(tube(top,string,.35,.35),'W',outline=False,flat=1);g.shape(tube(string,bot,.35,.35),'W',outline=False,flat=1)
    if arrow:
        s0,s1=arrow;g.shape(tube(s0,s1,.45,.45),'W',outline=False,flat=2);g.shape(ellipsoid(s1[0],s1[1],1.2,1.2),'M',outline=False)
def shield(g,c):
    g.shape(ellipsoid(c[0],c[1],5.2,6.0),'P');g.shape(ellipsoid(c[0],c[1],2.0,2.4),'M',outline=False)
def trail(g,p0,p1,cols):
    n=int(max(abs(p1[0]-p0[0]),abs(p1[1]-p0[1]))*1.5)+1
    for i in range(n+1):
        t=i/n;g.dot(p0[0]+(p1[0]-p0[0])*t,p0[1]+(p1[1]-p0[1])*t,cols[i%len(cols)])
