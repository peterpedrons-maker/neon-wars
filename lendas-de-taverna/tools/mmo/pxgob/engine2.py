"""Motor v2 de pixel art por código: iluminação por normais (esferoides/cápsulas/bisel), rampas de 5 tons com troca de matiz (sombra azulada, luz quente),
tracejado ordenado opcional, oclusão de contato entre peças, contorno seletivo (claro no lado iluminado) e limpeza de pixels soltos."""
import math
from PIL import Image
RAMPS={
 'O':[(206,208,120),(170,182,88),(132,150,68),(92,112,56),(54,70,50)],
 'P':[(214,160,92),(178,120,64),(138,84,48),(98,56,40),(58,34,36)],
 'A':[(140,140,190),(100,102,156),(70,70,120),(46,44,88),(24,22,52)],
 'H':[(250,224,140),(226,184,84),(184,132,56),(128,84,44),(74,46,36)],
 'M':[(226,232,240),(176,186,204),(128,138,164),(86,94,124),(44,50,76)],
 'W':[(255,252,232),(236,228,190),(196,184,142),(148,134,104),(96,86,72)],
 'D':[(168,108,70),(132,82,52),(98,58,40),(66,38,32),(36,22,26)],
 'E':[(255,150,120),(232,76,60),(176,44,48),(120,34,48),(64,24,36)],
}
L=(-.5,-.62,.6);_n=math.sqrt(sum(c*c for c in L));L=tuple(c/_n for c in L)
BAYER=[[0,2],[3,1]]
class Img:
    def __init__(s,w,h):
        s.w,s.h=w,h;s.col=[[None]*w for _ in range(h)];s.pid=[[0]*w for _ in range(h)];s.mat=[[None]*w for _ in range(h)];s.tone=[[0]*w for _ in range(h)];s.n=0
    def shape(s,test,mat,outline=True,dither=0.0,bias=0.0,flat=None):
        s.n+=1;pid=s.n;mask={}
        for y in range(s.h):
            for x in range(s.w):
                r=test(x+.5,y+.5)
                if r is not None:mask[(x,y)]=r
        R=RAMPS[mat]
        if outline:
            for (x,y) in list(mask):
                for dx,dy in((1,0),(-1,0),(0,1),(0,-1)):
                    q=(x+dx,y+dy)
                    if q not in mask and 0<=q[0]<s.w and 0<=q[1]<s.h:
                        t=3 if (dx<0 or dy<0) else 4
                        s.col[q[1]][q[0]]=R[t];s.pid[q[1]][q[0]]=-pid;s.mat[q[1]][q[0]]=None
        for (x,y),nrm in mask.items():
            if flat is not None:t=flat
            else:
                i=nrm[0]*L[0]+nrm[1]*L[1]+nrm[2]*L[2]+bias
                if dither:i+=(BAYER[y&1][x&1]-1.5)*dither
                t=0 if i>.78 else 1 if i>.42 else 2 if i>.05 else 3 if i>-.4 else 4
            s.col[y][x]=R[t];s.pid[y][x]=pid;s.mat[y][x]=mat;s.tone[y][x]=t
        return pid
    def dot(s,x,y,c):
        if 0<=x<s.w and 0<=y<s.h:s.col[y][x]=c;s.pid[y][x]=99999
    def finish(s,ao=True,clean=True):
        if ao:   # oclusão de contato: peça de trás escurece junto de peça da frente (abaixo/direita)
            ch=[]
            for y in range(s.h):
                for x in range(s.w):
                    p=s.pid[y][x]
                    if p>0 and s.mat[y][x]:
                        for d in(2,3):
                            xx,yy=x+d,y+d
                            if 0<=xx<s.w and 0<=yy<s.h:
                                q=s.pid[yy][xx]
                                if q>p and q!=99999:
                                    ch.append((x,y));break
            for x,y in ch:
                t=min(4,s.tone[y][x]+1);s.col[y][x]=RAMPS[s.mat[y][x]][t];s.tone[y][x]=t
        if clean: # remove pixels soltos de um tom isolado
            for y in range(1,s.h-1):
                for x in range(1,s.w-1):
                    c=s.col[y][x]
                    if c is None or s.pid[y][x]<=0 or s.pid[y][x]==99999:continue
                    nb=[s.col[y+dy][x+dx] for dx,dy in((1,0),(-1,0),(0,1),(0,-1))]
                    if c not in nb:
                        cand=[n for n in nb if n is not None]
                        if len(cand)>=3:
                            m=max(set(cand),key=cand.count)
                            if cand.count(m)>=2:s.col[y][x]=m
        return s
    def render(s,scale=1,bg=None):
        im=Image.new('RGBA',(s.w,s.h),(0,0,0,0))
        for y in range(s.h):
            for x in range(s.w):
                c=s.col[y][x]
                if c:im.putpixel((x,y),(*c,255))
        if scale>1:im=im.resize((s.w*scale,s.h*scale),Image.NEAREST)
        if bg:
            b=Image.new('RGBA',im.size,bg);b.alpha_composite(im);return b
        return im
# ---- formas com normal 3D
def ellipsoid(cx,cy,rx,ry,rot=0,zr=None):
    c,sn=math.cos(math.radians(rot)),math.sin(math.radians(rot))
    def t(x,y):
        dx,dy=x-cx,y-cy;u=(dx*c+dy*sn)/rx;v=(-dx*sn+dy*c)/ry;q=u*u+v*v
        if q<=1:
            z=math.sqrt(1-q);nx=u*c-v*sn;ny=u*sn+v*c;n=math.sqrt(nx*nx+ny*ny+z*z) or 1;return (nx/n,ny/n,z/n)
        return None
    return t
def tube(p0,p1,r0,r1=None):
    r1=r0 if r1 is None else r1;ax,ay=p0;bx,by=p1;dx,dy=bx-ax,by-ay;L2=dx*dx+dy*dy or 1e-6
    def t(x,y):
        u=max(0,min(1,((x-ax)*dx+(y-ay)*dy)/L2));cx,cy=ax+dx*u,ay+dy*u;r=r0+(r1-r0)*u
        ox,oy=x-cx,y-cy;q=(ox*ox+oy*oy)/(r*r)
        if q<=1:
            z=math.sqrt(1-q);n=math.sqrt(ox*ox/(r*r)+oy*oy/(r*r)+z*z) or 1;return (ox/r/n,oy/r/n,z/n)
        return None
    return t
def bevel(pts,depth=2.2):
    n=len(pts)
    def inside(x,y):
        ins=False;j=n-1
        for i in range(n):
            xi,yi=pts[i];xj,yj=pts[j]
            if ((yi>y)!=(yj>y)) and (x<(xj-xi)*(y-yi)/((yj-yi) or 1e-9)+xi):ins=not ins
            j=i
        return ins
    def dist(x,y):
        best=1e9;bx=by=0
        for i in range(n):
            ax,ay=pts[i];cx,cy=pts[(i+1)%n];dx,dy=cx-ax,cy-ay;L2=dx*dx+dy*dy or 1e-6
            u=max(0,min(1,((x-ax)*dx+(y-ay)*dy)/L2));px,py=ax+dx*u,ay+dy*u;d=math.hypot(x-px,y-py)
            if d<best:best=d;bx,by=x-px,y-py
        return best,bx,by
    def t(x,y):
        if not inside(x,y):return None
        d,ox,oy=dist(x,y);k=min(1,d/depth);z=math.sqrt(max(.05,1-(1-k)**2));m=math.hypot(ox,oy) or 1
        e=(1-k);nx,ny=-ox/m*e*-1,-oy/m*e*-1
        # normal aponta para fora da borda mais próxima
        nx,ny=(ox/m)*e,(oy/m)*e;n_=math.sqrt(nx*nx+ny*ny+z*z) or 1;return (-nx/n_*-1*-1,ny/n_*-1*-1,z/n_) if False else (nx/n_,ny/n_,z/n_)
    return t
def rot(p,piv,deg):
    c,s=math.cos(math.radians(deg)),math.sin(math.radians(deg));x,y=p[0]-piv[0],p[1]-piv[1]
    return (piv[0]+x*c-y*s,piv[1]+x*s+y*c)
