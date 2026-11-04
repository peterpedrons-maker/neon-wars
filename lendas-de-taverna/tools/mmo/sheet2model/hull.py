"""Etapa 1: segmenta a folha, monta o volume a partir das silhuetas (frente + lado, seções elípticas) e projeta as cores da arte na malha."""
import sys,json
import numpy as np,cv2
from scipy import ndimage
from skimage import measure
def load(path):
    im=cv2.imread(path);b=np.concatenate([im[:20].reshape(-1,3),im[-20:].reshape(-1,3),im[:,:20].reshape(-1,3),im[:,-20:].reshape(-1,3)]);bg=np.median(b,0)
    lab=cv2.cvtColor(im,cv2.COLOR_BGR2LAB).astype(float);bl=cv2.cvtColor(np.uint8([[bg]]),cv2.COLOR_BGR2LAB).astype(float)[0,0]
    d=np.linalg.norm(lab-bl,axis=2);m=(d>14).astype(np.uint8)*255
    m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((5,5),np.uint8));m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n,lbl,st,_=cv2.connectedComponentsWithStats(m);comps=[(st[i][0],i) for i in range(1,n) if st[i][4]>20000];comps.sort()
    views={}
    for name,(x,i) in zip(('front','side','back'),comps):
        mk=ndimage.binary_fill_holes(lbl==i);x0,y0,w,h,_=st[i];views[name]=dict(mask=mk,bbox=(x0,y0,w,h),ybot=y0+h)
    return cv2.cvtColor(im,cv2.COLOR_BGR2RGB),views
def bleed(img,mask,iters=14):
    out=img.astype(np.float32).copy();m=mask.astype(np.float32)
    for _ in range(iters):
        num=cv2.boxFilter(out*m[:,:,None],-1,(3,3),normalize=False);den=cv2.boxFilter(m,-1,(3,3),normalize=False)
        new=(den>0)&(m==0);out[new]=(num[new]/den[new][:,None]);m=np.where(new,1,m)
    return out.astype(np.uint8)
def rastpoly(shape,polys):
    m=np.zeros(shape,np.uint8)
    for p in polys:cv2.fillPoly(m,[np.array(p,np.int32)],255)
    return m>0
WEAPON_BLADE=[(618,540),(760,596),(838,606),(842,614),(811,708),(790,660),(745,673),(700,668),(655,650),(655,640),(612,628),(604,600),(615,560)]
WEAPON_HANDLE=[(458,486),(470,484),(528,512),(528,540),(452,514)]
def build(path,out,vox=2.0,sigma=1.3):
    img,V=load(path);F,S,B=V['front'],V['side'],V['back']
    Wp=rastpoly(img.shape[:2],[WEAPON_BLADE,WEAPON_HANDLE]);Wp=cv2.dilate(Wp.astype(np.uint8),np.ones((5,5),np.uint8))>0
    Sm=S['mask']&~Wp
    # a arma tapa a perna na vista lateral: nas linhas em que sobrou pouco, preenche a profundidade interpolando entre as linhas vizinhas boas
    ybs_=S['ybot'];good={}
    for z in range(0,700):
        r=ybs_-z
        if 0<=r<Sm.shape[0]:
            idx=np.where(Sm[r])[0]
            if len(idx)>=100:good[z]=(idx.min(),idx.max())
    zs=sorted(good)
    for z in range(60,230):
        r=ybs_-z;idx=np.where(Sm[r])[0]
        if len(idx)<100:
            lo=max([q for q in zs if q<z],default=None);hi=min([q for q in zs if q>z],default=None)
            if lo is not None and hi is not None:
                t=(z-lo)/(hi-lo);y0=int(good[lo][0]*(1-t)+good[hi][0]*t);y1=int(good[lo][1]*(1-t)+good[hi][1]*t);Sm[r,y0:y1+1]=True
    fx0,fy0,fw,fh=F['bbox'];cxf=fx0+fw/2;bx0,_,bw,_=B['bbox'];cxb=bx0+bw/2
    sx0,_,sw,_=S['bbox'];ys_ref=sx0+sw*.52
    ybf,ybs,ybb=F['ybot'],S['ybot'],B['ybot']
    ZH=int(max(F['bbox'][3],S['bbox'][3]));HX=210;HY=210
    nx=int(2*HX/vox);ny=int(2*HY/vox);nz=int(ZH/vox)+4
    Dt=cv2.distanceTransform(F['mask'].astype(np.uint8),cv2.DIST_L2,5)
    vol=np.zeros((nx,ny,nz),np.float32);YC=np.zeros(nz,np.float32)
    xs=(np.arange(nx)*vox-HX);ys=(np.arange(ny)*vox-HY)
    for k in range(nz):
        z=k*vox;rf=int(round(ybf-z));rs=int(round(ybs-z))
        if not(0<=rf<img.shape[0] and 0<=rs<img.shape[0]):continue
        fcols=np.round(cxf-xs).astype(int);ok=(fcols>=0)&(fcols<img.shape[1]);frow=np.zeros(nx,bool);frow[ok]=F['mask'][rf,fcols[ok]]
        dt=np.zeros(nx,np.float32);dt[ok]=Dt[rf,fcols[ok]]
        srow=Sm[rs];idx=np.where(srow)[0]
        if len(idx)==0 or not frow.any():continue
        # extensão em profundidade desta linha (pela silhueta lateral, sem a arma)
        y0=idx.min()-ys_ref;y1=idx.max()-ys_ref;yc=(y0+y1)/2;d=y1-y0;YC[k]=yc
        depth=np.minimum(d,3.4*dt+4)
        scols=np.round(ys_ref+ys).astype(int);sok=(scols>=0)&(scols<img.shape[1]);srw=np.zeros(ny,bool);srw[sok]=Sm[rs,scols[sok]]
        occ=frow[:,None]&srw[None,:]&(np.abs(ys[None,:]-yc)<=depth[:,None]/2)
        vol[:,:,k]=occ
    vol=ndimage.gaussian_filter(vol,sigma)
    verts,faces,normals,_=measure.marching_cubes(vol,level=.5,spacing=(vox,vox,vox))
    verts[:,0]-=HX;verts[:,1]-=HY      # px: x (esquerda do personagem = direita da tela frontal), y (frente), z (altura)
    # cores: projeção da frente/costas/lado com mistura pela normal
    ims={n:bleed(img,V[n]['mask'] if n!='side' else Sm) for n in('front','side','back')}
    def samp(im,col,row):
        return np.stack([ndimage.map_coordinates(im[:,:,c].astype(np.float32),[row,col],order=1,mode='nearest') for c in range(3)],1)
    x,y,z=verts[:,0],verts[:,1],verts[:,2]
    cf=samp(ims['front'],cxf-x,ybf-z);cb=samp(ims['back'],cxb+x,ybb-z);cs=samp(ims['side'],ys_ref+y,ybs-z)
    nx_,ny_,nz_=normals[:,0],normals[:,1],normals[:,2]
    wf=np.maximum(ny_,0)**3;wb=np.maximum(-ny_,0)**3;ws=np.abs(nx_)**3*1.2;t=wf+wb+ws+1e-6
    col=(cf*wf[:,None]+cb*wb[:,None]+cs*ws[:,None])/t[:,None]
    # arma: contorno do cutelo (px) para o Blender
    wm=rastpoly(img.shape[:2],[WEAPON_BLADE,WEAPON_HANDLE,[(520,508),(622,536),(612,568),(522,548)]])
    np.savez_compressed(out,yc=YC,vox=vox,verts=verts.astype(np.float32),faces=faces.astype(np.int32),colors=np.clip(col,0,255).astype(np.uint8),normals=normals.astype(np.float32),
        weapon_mask=wm,side_img=ims['side'],meta=json.dumps(dict(ys_ref=float(ys_ref),ybs=int(ybs),cxf=float(cxf),ybf=int(ybf),H=ZH)))
    return verts,faces
if __name__=='__main__':
    v,f=build(sys.argv[1],sys.argv[2]);print('verts',len(v),'faces',len(f),'bbox',v.min(0),v.max(0))
