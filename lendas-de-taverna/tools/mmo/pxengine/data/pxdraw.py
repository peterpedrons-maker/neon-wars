import math
class G:
    def __init__(s,w,h):s.w,s.h=w,h;s.g=[['.']*w for _ in range(h)]
    def ell(s,cx,cy,rx,ry,ramp,light=(-.5,-.65),bias=0.0):
        for y in range(s.h):
            for x in range(s.w):
                nx=(x+.5-cx)/rx;ny=(y+.5-cy)/ry;d=nx*nx+ny*ny
                if d<=1:
                    nz=math.sqrt(1-d);l=-(nx*light[0]+ny*light[1])*.62+nz*.55+bias
                    t=min(len(ramp)-1,max(0,int(l*len(ramp)*1.15)));s.g[y][x]=ramp[t]
    def poly(s,pts,ramp,tone=None,light=(-.5,-.65)):
        xs=[p[0] for p in pts];ys=[p[1] for p in pts];cx=sum(xs)/len(xs);cy=sum(ys)/len(ys);rx=(max(xs)-min(xs))/2 or 1;ry=(max(ys)-min(ys))/2 or 1
        for y in range(s.h):
            for x in range(s.w):
                if inside(x+.5,y+.5,pts):
                    nx=(x+.5-cx)/rx;ny=(y+.5-cy)/ry;l=-(nx*light[0]+ny*light[1])*.5+.45
                    t=tone if tone is not None else min(len(ramp)-1,max(0,int(l*len(ramp)*1.15)));s.g[y][x]=ramp[t]
    def rect(s,x0,y0,x1,y1,ch):
        for y in range(y0,y1+1):
            for x in range(x0,x1+1):
                if 0<=x<s.w and 0<=y<s.h:s.g[y][x]=ch
    def px(s,x,y,ch):
        if 0<=x<s.w and 0<=y<s.h:s.g[y][x]=ch
    def line(s,x0,y0,x1,y1,ch):
        n=int(max(abs(x1-x0),abs(y1-y0)))+1
        for i in range(n+1):
            t=i/max(1,n);s.px(round(x0+(x1-x0)*t),round(y0+(y1-y0)*t),ch)
    def outline(s):
        add=[]
        for y in range(s.h):
            for x in range(s.w):
                if s.g[y][x]=='.':
                    for dx,dy in((1,0),(-1,0),(0,1),(0,-1)):
                        xx,yy=x+dx,y+dy
                        if 0<=xx<s.w and 0<=yy<s.h and s.g[yy][xx] not in('.','k'):add.append((x,y));break
        for x,y in add:s.g[y][x]='k'
    def rows(s,half=False):
        r=[''.join(l) for l in s.g]
        if half:r=[l[:s.w//2+1] for l in r]
        # trim empty rows/cols handled by caller
        return r
def inside(x,y,pts):
    c=False;n=len(pts);j=n-1
    for i in range(n):
        xi,yi=pts[i];xj,yj=pts[j]
        if (yi>y)!=(yj>y) and x<(xj-xi)*(y-yi)/(yj-yi+1e-9)+xi:c=not c
        j=i
    return c
