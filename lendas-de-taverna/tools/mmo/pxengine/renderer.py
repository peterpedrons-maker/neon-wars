"""Visual Renderer: buffer de pixels com material+tom por pixel, membros com sombreado cilíndrico, contorno seletivo, brilho metálico e sombras de contato."""
import json,os,math
import numpy as np
D=os.path.dirname(os.path.abspath(__file__))
MD=json.load(open(os.path.join(D,'data','materials.json')))
hexrgb=lambda h:tuple(int(h[i:i+2],16) for i in (1,3,5))
MATS=list(MD['materials'])+['ink'];MID={m:i for i,m in enumerate(MATS)}
NT=[len(MD['materials'][m]['ramp']) if m!='ink' else 1 for m in MATS]
RAMP=np.zeros((len(MATS),4,3),np.uint8)
for m in MATS:
    r=[hexrgb(h) for h in MD['materials'][m]['ramp']] if m!='ink' else [tuple(MD['ink'])]
    for t in range(4):RAMP[MID[m],t]=r[min(t,len(r)-1)]
INK=np.array(MD['ink'],np.uint8);OUTL=np.array([MD['materials'].get(m,{'outline':0})['outline'] for m in MATS[:-1]]+[0.0])
LIGHT=np.array(MD['light'],float);LIGHT/=np.linalg.norm(LIGHT)
GLYPH={g:(MID[m],t) for g,(m,t) in MD['glyphs'].items()}
def shift(a,dx,dy):
    h,w=a.shape[:2];r=np.zeros_like(a)
    r[max(0,dy):h+min(0,dy),max(0,dx):w+min(0,dx)]=a[max(0,-dy):h-max(0,dy),max(0,-dx):w-max(0,dx)];return r
def dil4(m):return m|shift(m,1,0)|shift(m,-1,0)|shift(m,0,1)|shift(m,0,-1)
class Buf:
    def __init__(s,w,h):s.w,s.h=w,h;s.wm=np.zeros((h,w),bool);s.a=np.zeros((h,w),bool);s.mat=np.full((h,w),-1,np.int16);s.tone=np.zeros((h,w),np.int8)
    def _write(s,m,mat,tone,edge,cast):
        if edge:
            nb=dil4(m)&~m&s.a;s.tone[nb]=0
        if cast:
            cs=shift(m,1,1)&~m&s.a;s.tone[cs]=np.maximum(0,s.tone[cs]-1)
        s.a[m]=True;s.mat[m]=mat[m];s.tone[m]=tone[m]
    def glyphs(s,part,x0,y0,edge=False,cast=False,flip=False):
        """part=(mask,mat,tone) do tamanho do desenho; colado com o canto em (x0,y0)"""
        pm,pmat,ptone=part
        if flip:pm,pmat,ptone=pm[:,::-1],pmat[:,::-1],ptone[:,::-1]
        h,w=pm.shape;m=np.zeros((s.h,s.w),bool);mat=np.zeros((s.h,s.w),np.int16);tone=np.zeros((s.h,s.w),np.int8)
        xs0,ys0=max(0,x0),max(0,y0);xs1,ys1=min(s.w,x0+w),min(s.h,y0+h)
        if xs1<=xs0 or ys1<=ys0:return
        sub=(slice(ys0-y0,ys1-y0),slice(xs0-x0,xs1-x0))
        m[ys0:ys1,xs0:xs1]=pm[sub];mat[ys0:ys1,xs0:xs1]=pmat[sub];tone[ys0:ys1,xs0:xs1]=ptone[sub];s._write(m,mat,tone,edge,cast)
    def rot_glyphs(s,part,anchor,pos,angle,edge=False,scale=1.0):
        """gira um desenho de pixels (OpenCV, vizinho mais próximo: sem suavização) em torno da âncora e cola com a âncora em pos"""
        import cv2
        import cv2 as _cv
        pm,pmat,ptone=part
        if scale!=1.0:
            h0,w0=pm.shape;nw,nh=max(1,round(w0*scale)),max(1,round(h0*scale))
            rs=lambda a,dt:_cv.resize(a.astype(dt),(nw,nh),interpolation=_cv.INTER_NEAREST)
            pm=rs(pm,np.uint8)>0;pmat=rs(pmat,np.int16);ptone=rs(ptone,np.uint8).astype(np.int8);anchor=(round(anchor[0]*scale),round(anchor[1]*scale))
        h,w=pm.shape;R=int(math.hypot(w,h))+3;S=2*R
        m=np.zeros((S,S),np.uint8);mt=np.zeros((S,S),np.int16);tn=np.zeros((S,S),np.uint8)
        ox,oy=R-anchor[0],R-anchor[1];m[oy:oy+h,ox:ox+w]=pm;mt[oy:oy+h,ox:ox+w]=pmat;tn[oy:oy+h,ox:ox+w]=ptone
        M=cv2.getRotationMatrix2D((R,R),angle,1.0)
        f=lambda a,dt:cv2.warpAffine(a.astype(dt),M,(S,S),flags=cv2.INTER_NEAREST,borderValue=0)
        rm=f(m,np.uint8)>0;rmat=f(mt,np.int16);rt=f(tn,np.uint8)
        X0,Y0=round(pos[0])-R,round(pos[1])-R
        before=s.a.copy();s.glyphs((rm,rmat,rt.astype(np.int8)),X0,Y0,edge=edge)
        s.wm=np.zeros_like(s.a);ys0,xs0=max(0,Y0),max(0,X0);ys1,xs1=min(s.h,Y0+S),min(s.w,X0+S)
        if ys1>ys0 and xs1>xs0:s.wm[ys0:ys1,xs0:xs1]=rm[ys0-Y0:ys1-Y0,xs0-X0:xs1-X0]
    def tube(s,pts,radii,mat,far=False,edge=True,joints=(),tone_bias=0):
        """membro afunilado com sombreado cilíndrico (luz global); radii: um (r0,r1) por segmento; joints: (ponto,raio)"""
        Y,X=np.mgrid[0:s.h,0:s.w].astype(float);best=np.full((s.h,s.w),9.0);nx=np.zeros((s.h,s.w));ny=np.zeros((s.h,s.w));nz=np.ones((s.h,s.w))
        def consider(ratio,sx,sy):
            nonlocal best,nx,ny,nz
            ok=ratio<best;best=np.where(ok,ratio,best);nx=np.where(ok,sx,nx);ny=np.where(ok,sy,ny);nz=np.where(ok,np.sqrt(np.clip(1-np.minimum(ratio,1)**2,0,1)),nz)
        for (a,b),(r0,r1) in zip(zip(pts,pts[1:]),radii):
            ax,ay=a;bx,by=b;dx,dy=bx-ax,by-ay;L2=max(1e-6,dx*dx+dy*dy);t=np.clip(((X-ax)*dx+(Y-ay)*dy)/L2,0,1)
            cx,cy=ax+t*dx,ay+t*dy;r=r0+(r1-r0)*t;d=np.hypot(X-cx,Y-cy);L=math.sqrt(L2);px,py=-dy/L,dx/L
            sd=((X-cx)*px+(Y-cy)*py)/np.maximum(r,.01);consider(d/np.maximum(r,.01)*(1-1e-9),np.clip(sd,-1,1)*px,np.clip(sd,-1,1)*py)
        for (jx,jy),r in joints:
            d=np.hypot(X-jx,Y-jy)/r;consider(d,np.clip((X-jx)/r,-1,1),np.clip((Y-jy)/r,-1,1))
        m=best<=1.0
        if not m.any():return
        lam=nx*LIGHT[0]+ny*LIGHT[1]+nz*LIGHT[2];n=NT[mat];t=np.clip(((lam+0.15)/1.05)*n,0,n-1e-6).astype(np.int8)
        t=np.clip(t+tone_bias-(1 if far else 0),0,n-1).astype(np.int8)
        matA=np.full((s.h,s.w),mat,np.int16);s._write(m,matA,t,edge,False)
    def finish(s,texture=True):
        h,w=s.h,s.w;tone=s.tone.copy();mat=s.mat.copy();a=s.a
        # brilho metálico: borda iluminada (canto superior esquerdo) do metal vira o tom mais claro
        # luz global (cima-esquerda): borda esquerda/superior de cada peça sobe um tom, direita/inferior desce um
        multi=np.array([n>=3 for n in NT]+[False]);mt=multi[np.clip(mat,0,len(MATS)-1)]&a
        litm=mt&(~shift(a,1,0)|~shift(a,0,1));dark=mt&(~shift(a,-1,0)|~shift(a,0,-1))&~litm
        nmax=np.array(NT)[np.clip(mat,0,len(MATS)-1)]-1
        tone=np.where(litm,np.minimum(tone+1,nmax),tone);tone=np.where(dark,np.maximum(tone-1,0),tone).astype(np.int8)
        mm=a&(mat==MID['metal']);hi=mm&~shift(mm,1,1)&~shift(mm,1,0)&~shift(mm,0,1)
        tone[hi]=NT[MID['metal']]-1
        if texture:
            cl=a&(mat==MID['cloth'])&(tone==1);yy,xx=np.mgrid[0:h,0:w];tone[cl&((xx+yy)%4==0)]=0
        rgb=np.zeros((h,w,4),np.uint8);rr=RAMP[np.clip(mat,0,len(MATS)-1),np.clip(tone,0,3)];rgb[a,:3]=rr[a];rgb[a,3]=255
        # contorno seletivo: cada borda externa leva a cor escura do material vizinho
        edge=dil4(a)&~a;out_col=np.zeros((h,w,3),float);got=np.zeros((h,w),bool)
        for dx,dy in((0,1),(1,0),(-1,0),(0,-1)):   # vizinho acima (o pixel está sob o sprite) tem prioridade a tinta pura
            na=shift(a,dx,dy);nm=shift(mat,dx,dy);sel=edge&na&~got
            if (dx,dy)==(0,1):out_col[sel]=INK;got|=sel;continue
            o=OUTL[np.clip(nm,0,len(MATS)-1)];base=RAMP[np.clip(nm,0,len(MATS)-1),0].astype(float)
            col=INK*(1-o[...,None])+base*o[...,None]*.55;out_col[sel]=col[sel];got|=sel
        rgb[edge,:3]=out_col[edge].astype(np.uint8);rgb[edge,3]=255
        return rgb
def part_from_rows(rows,mirror=False):
    if mirror:rows=[r+r[-2::-1] for r in rows]
    w=max(len(r) for r in rows);h=len(rows);m=np.zeros((h,w),bool);mat=np.zeros((h,w),np.int16);tone=np.zeros((h,w),np.int8)
    for y,r in enumerate(rows):
        for x,ch in enumerate(r):
            if ch in GLYPH:m[y,x]=True;mat[y,x],tone[y,x]=GLYPH[ch]
    return m,mat,tone
def lie_down(buf,ground):
    """cair: gira o quadro 90 graus (sem perda) e apoia no chão"""
    h,w=buf.a.shape;a=np.rot90(buf.a);mat=np.rot90(buf.mat);tone=np.rot90(buf.tone)
    ys=np.where(a.any(1))[0];xs=np.where(a.any(0))[0]
    if len(ys)==0:return buf
    dy=(ground+1)-ys.max();cx=(xs.min()+xs.max())//2;dx=w//2-cx
    n=Buf(buf.w,buf.h)
    for src,dst in((a,n.a),(mat,n.mat),(tone,n.tone)):
        r=np.zeros_like(dst);ys0,xs0=max(0,dy),max(0,dx)
        sub=src[max(0,-dy):h-max(0,dy) if dy>=0 else h,max(0,-dx):w-max(0,dx) if dx>=0 else w]
        r[ys0:ys0+sub.shape[0],xs0:xs0+sub.shape[1]]=sub;dst[:]=r
    return n
