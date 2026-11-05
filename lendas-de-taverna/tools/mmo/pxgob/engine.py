"""Motor mínimo de pixel art por código: formas (elipse, cápsula, polígono) com z-order, sombreamento por forma (luz no canto superior esquerdo),
contorno de 1 px por peça e paleta fixa. Cada quadro é desenhado do zero (sem 3D, sem suavização), então rotações ficam limpas no pixel."""
import math
from PIL import Image
OUT=(14,9,18)
PAL={
 'G':[(96,190,78),(52,113,69),(32,59,71)],      # verde: base, sombra, sombra profunda
 'B':[(181,112,82),(114,64,56),(63,39,49)],     # couro/madeira
 'T':[(226,166,115),(181,112,82),(114,64,56)],  # pele/interior da orelha
 'S':[(157,178,200),(68,101,123),(32,59,71)],   # metal
 'W':[(255,255,255),(200,206,214),(157,178,200)],
 'Y':[(255,214,64),(214,150,30),(143,52,63)],
 'K':[(24,16,28),(14,9,18),(14,9,18)],
 'R':[(223,65,74),(143,52,63),(63,39,49)],
}
LIGHT=(-.55,-.83)
class Img:
    def __init__(s,w,h):
        s.w,s.h=w,h;s.px=[[None]*w for _ in range(h)];s.pid=[[0]*w for _ in range(h)];s.n=0
    def shape(s,test,mat,outline=True,shade=.42,deep=None,flat=False):
        """test(x,y)->None ou (nx,ny) normal aproximada em [-1,1] se o pixel pertence à forma"""
        s.n+=1;pid=s.n;mask={}
        for y in range(s.h):
            for x in range(s.w):
                r=test(x+.5,y+.5)
                if r is not None:mask[(x,y)]=r
        if outline:
            ring=set()
            for (x,y) in mask:
                for dx,dy in((1,0),(-1,0),(0,1),(0,-1)):
                    q=(x+dx,y+dy)
                    if q not in mask and 0<=q[0]<s.w and 0<=q[1]<s.h:ring.add(q)
            for (x,y) in ring:s.px[y][x]=OUT;s.pid[y][x]=-pid
        tones=PAL[mat]
        for (x,y),nrm in mask.items():
            t=0
            if not flat:
                d=nrm[0]*-LIGHT[0]+nrm[1]*-LIGHT[1]
                if d>shade:t=1
                if deep is not None and d>deep:t=2
            s.px[y][x]=tones[t];s.pid[y][x]=pid
        return pid
    def dot(s,x,y,col):
        if 0<=x<s.w and 0<=y<s.h:s.px[y][x]=col;s.pid[y][x]=99999
    def render(s,scale=1,bg=None):
        im=Image.new('RGBA',(s.w,s.h),(0,0,0,0))
        for y in range(s.h):
            for x in range(s.w):
                c=s.px[y][x]
                if c:im.putpixel((x,y),(*c,255))
        if scale>1:im=im.resize((s.w*scale,s.h*scale),Image.NEAREST)
        if bg:
            b=Image.new('RGBA',im.size,bg);b.alpha_composite(im);return b
        return im
# ---- formas
def ellipse(cx,cy,rx,ry,rot=0):
    c,sn=math.cos(math.radians(rot)),math.sin(math.radians(rot))
    def t(x,y):
        dx,dy=x-cx,y-cy;u=(dx*c+dy*sn)/rx;v=(-dx*sn+dy*c)/ry
        if u*u+v*v<=1:
            n=math.hypot(u,v) or 1;nx,ny=u/ max(n,1e-6),v/max(n,1e-6)
            # normal no espaço da tela
            return (nx*c-ny*sn)*min(1,n*1.0),(nx*sn+ny*c)*min(1,n*1.0)
        return None
    return t
def capsule(p0,p1,r0,r1=None):
    r1=r0 if r1 is None else r1;ax,ay=p0;bx,by=p1;dx,dy=bx-ax,by-ay;L2=dx*dx+dy*dy or 1e-6
    def t(x,y):
        u=max(0,min(1,((x-ax)*dx+(y-ay)*dy)/L2));cx,cy=ax+dx*u,ay+dy*u;r=r0+(r1-r0)*u
        ox,oy=x-cx,y-cy;d=math.hypot(ox,oy)
        if d<=r:
            n=d/r if r else 0;m=math.hypot(ox,oy) or 1;return (ox/m*n,oy/m*n)
        return None
    return t
def poly(pts):
    n=len(pts);cx=sum(p[0] for p in pts)/n;cy=sum(p[1] for p in pts)/n
    R=max(math.hypot(p[0]-cx,p[1]-cy) for p in pts) or 1
    def t(x,y):
        ins=False;j=n-1
        for i in range(n):
            xi,yi=pts[i];xj,yj=pts[j]
            if ((yi>y)!=(yj>y)) and (x<(xj-xi)*(y-yi)/((yj-yi) or 1e-9)+xi):ins=not ins
            j=i
        if ins:
            ox,oy=(x-cx)/R,(y-cy)/R;return (ox,oy)
        return None
    return t
def rot(p,piv,deg):
    c,s=math.cos(math.radians(deg)),math.sin(math.radians(deg));x,y=p[0]-piv[0],p[1]-piv[1]
    return (piv[0]+x*c-y*s,piv[1]+x*s+y*c)
