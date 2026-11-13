"""Motor pixel-art HQ: formas desenhadas em 4x, sombreadas por mapa de altura, reduzidas a paleta fixa, contorno colorido."""
import math,numpy as np
from PIL import Image,ImageDraw,ImageFilter
S=4
def hx(s):return tuple(int(s[i:i+2],16) for i in(1,3,5))
class Canvas:
    def __init__(s,w,h):
        s.w,s.h=w,h;s.rgb=np.zeros((h*S,w*S,3),np.uint8);s.a=np.zeros((h*S,w*S),bool)
    def shape(s,fn,ramp,blur=2.2,light=(-.55,-.6),flat=None,steps=None):
        m=Image.new('L',(s.w*S,s.h*S),0);d=ImageDraw.Draw(m);fn(d)
        M=np.array(m)>127
        if not M.any():return
        if flat is not None:
            s.rgb[M]=hx(flat) if isinstance(flat,str) else flat;s.a|=M;return
        hmap=np.array(m.filter(ImageFilter.GaussianBlur(blur*S)),float)/255
        gy,gx=np.gradient(hmap);k=9.0/S
        nx,ny,nz=-gx*k*S,-gy*k*S,np.ones_like(gx)
        n=np.sqrt(nx*nx+ny*ny+nz*nz);nx/=n;ny/=n;nz/=n
        lz=.62;L=math.sqrt(light[0]**2+light[1]**2+lz*lz)
        # luz vem de light (apontando para o lado de onde vem); superficie virada para a luz = claro
        lam=(nx*light[0]*-1+ny*light[1]*-1)/L*-1*-1
        lam=-(nx*light[0]+ny*light[1])/L+nz*lz/L
        t=np.clip((lam-.2)/.75,0,.999)
        R=[hx(c) for c in ramp.split()];N=len(R)
        idx=(t*N).astype(int) if steps is None else (t*steps).astype(int)*N//steps
        idx=np.clip(idx,0,N-1)
        col=np.array(R,np.uint8)[idx]
        s.rgb[M]=col[M];s.a|=M
    def sub(s):
        """reduz 4x pegando o pixel central; devolve RGBA 1x"""
        c=S//2;rgb=s.rgb[c::S,c::S];a=s.a[c::S,c::S]
        return rgb.copy(),a.copy()
def finish(cv,outline='dark',rim=None):
    rgb,a=cv.sub();h,w=a.shape
    out=np.zeros((h,w,4),np.uint8);out[...,:3]=rgb;out[...,3]=np.where(a,255,0)
    # contorno colorido: pega cor vizinha, escurece e puxa para azul-roxo
    ol=np.zeros((h,w,4),np.uint8)
    for y in range(h):
        for x in range(w):
            if a[y,x]:continue
            best=None
            for dx,dy in((1,0),(-1,0),(0,1),(0,-1)):
                xx,yy=x+dx,y+dy
                if 0<=xx<w and 0<=yy<h and a[yy,xx]:
                    c=rgb[yy,xx].astype(float);best=c if best is None else np.minimum(best,c)
            if best is not None:
                c=best*.28+np.array([14,8,30])*.72*0+np.array([10,6,26])
                ol[y,x]=(*np.clip(c,0,255).astype(np.uint8),255)
    m=ol[...,3]>0;out[m]=ol[m]
    return Image.fromarray(out,'RGBA')
