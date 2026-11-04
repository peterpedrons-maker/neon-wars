"""Efeitos de habilidade (corte, fogo, gelo, eletricidade): geração procedural em pixel art, sem suavização."""
import math,os,json
import numpy as np
from PIL import Image
RAMPS={'slash':['#fffbe0','#ffe38a','#f0a030','#9a4a18'],'fire':['#fff6c8','#ffd048','#f07818','#b02818','#501018'],'ice':['#f4fcff','#a8e4ff','#58a8e8','#2c5ca8'],'bolt':['#ffffff','#e8f0ff','#9ab4ff','#5a64d8']}
hexrgb=lambda h:tuple(int(h[i:i+2],16) for i in (1,3,5))
BAYER=np.array([[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]])/16.
def paint(canvas,val,ramp):
    """val 0..1 (1 = mais quente) -> tom da rampa, com dither ordenado de 4x4"""
    h,w=val.shape;n=len(ramp);yy,xx=np.mgrid[0:h,0:w];v=np.clip(val,0,.999)*(n-1)
    idx=np.floor(v+BAYER[yy%4,xx%4]-.5+.0).astype(int);idx=np.clip(np.where(val>0,(n-1)-np.clip(np.round((1-np.clip(val,0,1))*(n-1)+ (BAYER[yy%4,xx%4]-.5)*.7),0,n-1),0).astype(int),0,n-1)
    cols=np.array([hexrgb(c) for c in ramp],np.uint8);m=val>0.02;canvas[m,:3]=cols[idx[m]];canvas[m,3]=255
def slash(n=7,size=48,ramp=RAMPS['slash'],sweep=(-1.9,1.2)):
    out=[];yy,xx=np.mgrid[0:size,0:size].astype(float);cx,cy=size*.38,size*.52;dx,dy=xx-cx,yy-cy;r=np.hypot(dx,dy);th=np.arctan2(dy,dx)
    for f in range(n):
        t=(f+1)/n;head=sweep[0]+(sweep[1]-sweep[0])*t;tail=head-(1.2+.6*t);arcR=size*.34;w=size*.075*(1-.35*abs(t-.5))
        inside=(th<=head)&(th>=tail);band=np.abs(r-arcR-(th-head)*size*.01)<w*(1-(head-th)/2.2).clip(.15,1)
        v=np.where(inside&band,1-np.clip((head-th)/(head-tail),0,1)*.9,0)*(1-.5*max(0,t-.7)/.3)
        c=np.zeros((size,size,4),np.uint8);paint(c,v,ramp);out.append(c)
    return out
def fire(n=8,size=48,ramp=RAMPS['fire'],seed=3):
    rng=np.random.default_rng(seed);P=[(rng.uniform(-9,9),rng.uniform(0,1),rng.uniform(.6,1.3)) for _ in range(14)];out=[];yy,xx=np.mgrid[0:size,0:size].astype(float)
    for f in range(n):
        t=f/(n-1);v=np.zeros((size,size))
        for px,ph,sp in P:
            age=(t*sp+ph*.5)%1.0;x=size/2+px*(1-age*.5);y=size*.78-age*size*.62*sp;r=(1-age)*(size*.13)+1;d=np.hypot(xx-x,yy-y)/r;v=np.maximum(v,np.clip(1-d,0,1)*(1-age*.55))
        c=np.zeros((size,size,4),np.uint8);paint(c,v,ramp);out.append(c)
    return out
def ice(n=7,size=48,ramp=RAMPS['ice'],seed=5):
    rng=np.random.default_rng(seed);S=[(rng.uniform(0,6.283),rng.uniform(.5,1.0)) for _ in range(9)];out=[];yy,xx=np.mgrid[0:size,0:size].astype(float)
    for f in range(n):
        t=(f+1)/n;v=np.zeros((size,size))
        for a,L in S:
            ln=size*.42*L*min(1,t*1.6);x0,y0=size/2,size/2;steps=int(ln*2)
            for k in range(steps):
                q=k/max(1,steps);px=x0+math.cos(a)*ln*q;py=y0+math.sin(a)*ln*q;d=np.hypot(xx-px,yy-py);v=np.maximum(v,np.clip(1-d/(1.5*(1-q)+.6),0,1)*(1-q*.4))
        v*=1-.6*max(0,t-.75)/.25;c=np.zeros((size,size,4),np.uint8);paint(c,v,ramp);out.append(c)
    return out
def bolt(n=6,size=48,ramp=RAMPS['bolt'],seed=7):
    out=[];yy,xx=np.mgrid[0:size,0:size].astype(float)
    for f in range(n):
        rng=np.random.default_rng(seed+f*13);x=size/2+rng.uniform(-3,3);pts=[(x,0)]
        for y in range(4,size,5):x+=rng.uniform(-6,6);x=np.clip(x,8,size-8);pts.append((x,y))
        v=np.zeros((size,size))
        for (x0,y0),(x1,y1) in zip(pts,pts[1:]):
            for k in range(14):
                t=k/13;px,py=x0+(x1-x0)*t,y0+(y1-y0)*t;v=np.maximum(v,np.clip(1-np.hypot(xx-px,yy-py)/1.8,0,1))
                if k%7==0 and rng.random()<.5:
                    bx=px+rng.uniform(-8,8);by=py+rng.uniform(2,7)
                    for j in range(7):tt=j/6;qx,qy=px+(bx-px)*tt,py+(by-py)*tt;v=np.maximum(v,np.clip(1-np.hypot(xx-qx,yy-qy)/1.2,0,1)*.7)
        v*=1-.5*(f/n);c=np.zeros((size,size,4),np.uint8);paint(c,v,ramp);out.append(c)
    return out
FX={'corte':slash,'fogo':fire,'gelo':ice,'raio':bolt}
def export_fx(out):
    os.makedirs(out,exist_ok=True);meta={}
    for k,f in FX.items():
        fr=f();S=np.concatenate(fr,axis=1);Image.fromarray(S,'RGBA').save(os.path.join(out,f'fx_{k}.png'));meta[k]={'file':f'fx_{k}.png','frames':len(fr),'cell':list(fr[0].shape[:2][::-1]),'ms':70}
        G=[];
        for c in fr:
            bg=Image.new('RGBA',(c.shape[1]*6,c.shape[0]*6),(40,32,48,255));bg.alpha_composite(Image.fromarray(c,'RGBA').resize((c.shape[1]*6,c.shape[0]*6),Image.NEAREST));G.append(bg.convert('P',palette=Image.ADAPTIVE))
        G[0].save(os.path.join(out,f'fx_{k}.gif'),save_all=True,append_images=G[1:],duration=70,loop=0)
    json.dump(meta,open(os.path.join(out,'fx.json'),'w'),indent=1);return meta
