"""Renderizador vetorial: formas suaves (supersampling), sombreado em cel-shading com luz de cima-esquerda, contorno grosso e gradientes."""
import math
import numpy as np
import cv2
SS=4          # supersampling
def hexc(h):return np.array([int(h[i:i+2],16) for i in (1,3,5)],float)
def smooth(pts,n=10,closed=True):
    """curva suave (Catmull-Rom) passando pelos pontos"""
    P=np.array(pts,float);m=len(P);out=[]
    for i in range(m if closed else m-1):
        p0,p1,p2,p3=P[(i-1)%m],P[i%m],P[(i+1)%m],P[(i+2)%m]
        if not closed:
            p0=P[max(i-1,0)];p3=P[min(i+2,m-1)]
        for k in range(n):
            t=k/n;out.append(.5*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t*t+(-p0+3*p1-3*p2+p3)*t**3))
    return np.array(out)
def rot(pts,origin,a):
    r=math.radians(a);c,s=math.cos(r),math.sin(r);P=np.array(pts,float)
    return np.stack([origin[0]+P[:,0]*c+P[:,1]*s,origin[1]-P[:,0]*s+P[:,1]*c],1)
def rotw(pts,origin,a):
    """rotação 'de tela' (antihorária, 0 = para a direita), usada pela arma"""
    r=math.radians(a);c,s=math.cos(r),math.sin(r);P=np.array(pts,float)
    return np.stack([origin[0]+P[:,0]*c-P[:,1]*s*-1*-1 if False else origin[0]+P[:,0]*c+P[:,1]*s,origin[1]-P[:,0]*s+P[:,1]*c],1)
class Canvas:
    def __init__(s,w,h):
        s.w,s.h=w,h;s.W,s.H=w*SS,h*SS;s.rgb=np.zeros((s.H,s.W,3),np.float32);s.a=np.zeros((s.H,s.W),np.float32)
    def mask_poly(s,pts):
        m=np.zeros((s.H,s.W),np.uint8);cv2.fillPoly(m,[np.round(np.array(pts)*SS).astype(np.int32)],255);return m>0
    def mask_ell(s,c,rx,ry,ang=0):
        m=np.zeros((s.H,s.W),np.uint8);cv2.ellipse(m,(int(c[0]*SS),int(c[1]*SS)),(max(1,int(rx*SS)),max(1,int(ry*SS))),-ang,0,360,255,-1);return m>0
    def mask_capsule(s,pts,radii):
        m=np.zeros((s.H,s.W),np.uint8)
        for (a,b),(r0,r1) in zip(zip(pts,pts[1:]),radii):
            n=max(2,int(math.hypot(b[0]-a[0],b[1]-a[1])*SS/3))
            for k in range(n+1):
                t=k/n;x=a[0]+(b[0]-a[0])*t;y=a[1]+(b[1]-a[1])*t;r=r0+(r1-r0)*t;cv2.circle(m,(int(x*SS),int(y*SS)),max(1,int(r*SS)),255,-1)
        return m>0
    def paint(s,m,base,shade,light,outline,hl=3.0,sh=4.5,ow=1.4,grad=0.10,shadow_only=False,detail=None):
        """pinta a máscara: base + faixa de luz (cima-esq) + faixa de sombra (baixo-dir) + contorno"""
        ys,xs=np.where(m)
        if len(ys)==0:return
        pad=int((ow+sh+2)*SS)+2;y0,y1,x0,x1=max(0,ys.min()-pad),min(s.H,ys.max()+pad+1),max(0,xs.min()-pad),min(s.W,xs.max()+pad+1)
        mc=m[y0:y1,x0:x1];h,w=mc.shape
        def sft(a,dx,dy):
            r=np.zeros_like(a);r[max(0,dy):h+min(0,dy),max(0,dx):w+min(0,dx)]=a[max(0,-dy):h-max(0,dy),max(0,-dx):w-max(0,dx)];return r
        d1=int(hl*SS);d2=int(sh*SS)
        lit=mc&~sft(mc,d1,int(d1*.9));dk=mc&~sft(mc,-d2,-int(d2*.9))&~lit
        col=np.zeros((h,w,3),np.float32);col[:]=base
        yy=np.linspace(1+grad,1-grad,h)[:,None,None];col*=yy
        col[dk]=np.array(shade);col[lit]=np.array(light)
        if detail is not None:col=detail(col,mc,x0,y0)
        k=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2*int(ow*SS)+1,)*2);big=cv2.dilate(mc.astype(np.uint8),k)>0;ol=big&~mc
        reg=s.rgb[y0:y1,x0:x1];ra=s.a[y0:y1,x0:x1]
        reg[ol]=np.array(outline);ra[ol]=1;reg[mc]=col[mc];ra[mc]=1
    def result(s):
        out=np.zeros((s.H,s.W,4),np.float32);out[:,:,:3]=s.rgb*s.a[:,:,None];out[:,:,3]=s.a
        small=cv2.resize(out,(s.w,s.h),interpolation=cv2.INTER_AREA);a=small[:,:,3:4];rgb=np.where(a>0,small[:,:,:3]/np.maximum(a,1e-6),0)
        return np.clip(np.concatenate([rgb,a*255],2),0,255).astype(np.uint8)
