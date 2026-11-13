"""Motor pixel-art HQ: formas desenhadas em 4x, sombreadas por mapa de altura, reduzidas a paleta fixa, contorno colorido."""
import math,numpy as np
from PIL import Image,ImageDraw,ImageFilter
S=4
def hx(s):return tuple(int(s[i:i+2],16) for i in(1,3,5))
class Canvas:
    def __init__(s,w,h):
        s.w,s.h=w,h;s.rgb=np.zeros((h*S,w*S,3),np.uint8);s.a=np.zeros((h*S,w*S),bool)
    def shape(s,fn,ramp,blur=2.2,light=(-.55,-.6),flat=None,steps=None,ao=True,rim=.30,dith=.07):
        m=Image.new('L',(s.w*S,s.h*S),0);d=ImageDraw.Draw(m);fn(d)
        bb=m.getbbox()
        if bb is None:return
        pad=int(blur*S*3+2*S*2+4)
        x0,y0=max(0,bb[0]-pad),max(0,bb[1]-pad);x1,y1=min(s.w*S,bb[2]+pad),min(s.h*S,bb[3]+pad)
        m=m.crop((x0,y0,x1,y1));M=np.array(m)>127
        rgb=s.rgb[y0:y1,x0:x1];A=s.a[y0:y1,x0:x1]
        if flat is not None:
            rgb[M]=hx(flat) if isinstance(flat,str) else flat;A|=M;return
        if ao and A.any():
            ring=np.array(m.filter(ImageFilter.MaxFilter(2*S*2+1)))>127
            ring&=~M&A;rgb[ring]=(rgb[ring].astype(float)*.70).astype(np.uint8)
        hmap=np.array(m.filter(ImageFilter.GaussianBlur(blur*S)),float)/255
        gy,gx=np.gradient(hmap);k=9.0/S
        nx,ny,nz=-gx*k*S,-gy*k*S,np.ones_like(gx)
        n=np.sqrt(nx*nx+ny*ny+nz*nz);nx/=n;ny/=n;nz/=n
        lz=.62;Ln=math.sqrt(light[0]**2+light[1]**2+lz*lz)
        lam=-(nx*light[0]+ny*light[1])/Ln+nz*lz/Ln
        t=(lam-.2)/.75
        if rim:
            r=np.clip(nx*.6+ny*.5,0,1)**1.5*(1-nz)*1.6;t=t+r*rim
        if dith:
            ys,xs=np.mgrid[y0:y1,x0:x1];bay=np.array([[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]])/16.-.5
            t=t+bay[(ys//S)%4,(xs//S)%4]*dith
        t=np.clip(t,0,.999)
        R=[hx(c) for c in ramp.split()];N=len(R)
        idx=(t*N).astype(int) if steps is None else (t*steps).astype(int)*N//steps
        idx=np.clip(idx,0,N-1)
        col=np.array(R,np.uint8)[idx]
        rgb[M]=col[M];A|=M
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
