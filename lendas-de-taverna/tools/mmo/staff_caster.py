import numpy as np,os,sys
from PIL import Image
import os as _o;A=_o.path.join(_o.path.dirname(_o.path.abspath(__file__)),'..','..','mmo','assets')+'/'
SK=np.array(Image.open(A+'look2/male/spellcast_skin_0.png').convert('RGBA'))
def hand(r,c):
    fr=SK[r*64:(r+1)*64,c*64:(c+1)*64,3]>0
    ys,xs=np.where(fr)
    if len(ys)==0:return None
    bot=ys.max();sel=ys<bot-14
    ys,xs=ys[sel],xs[sel]
    if r==1:ex=xs.min();m=xs<=ex+1
    else:ex=xs.max();m=xs>=ex-1
    return int(ex+(1 if r!=1 else -1)*0),int(np.median(ys[m]))
def pole(orb):
    P=np.zeros((64,64,4),np.uint8)
    return P
def draw_staff(frame,hx,hy,orb,r):
    """cajado vertical segurado na mão (hx,hy), por baixo do corpo"""
    fr=np.zeros((64,64,4),np.uint8)
    dk=(52,32,18,255);md=(138,92,52,255);lt=(178,126,74,255)
    x=hx-1 if r!=1 else hx+0
    top=hy-24;bot=hy+9
    def put(px,py,col):
        if 0<=px<64 and 0<=py<64:fr[py,px]=col
    for y in range(top,bot):
        put(x-1,y,dk);put(x+2,y,dk);put(x,y,lt);put(x+1,y,md)
    for xx in (x-1,x,x+1,x+2):put(xx,bot,dk)
    # esfera no topo
    cx,cy=x,top-3
    for dy in range(-3,4):
        for dx in range(-3,4):
            d=dx*dx+dy*dy
            if d<=9:put(cx+1+dx,cy+dy,(30,18,30,255) if d>=7 else orb+(255,))
    put(cx,cy-1,(255,255,255,255));put(cx+1,cy-1,tuple(min(255,v+70) for v in orb)+(255,))
    base=Image.fromarray(fr,'RGBA');base.alpha_composite(Image.fromarray(frame,'RGBA'));return np.array(base)
def apply(src,dst,orb,over=False):
    im=np.array(Image.open(src).convert('RGBA'));out=im.copy()
    for r in range(4):
        for c in range(7):
            h=hand(r,c)
            if h is None:continue
            f=im[r*64:(r+1)*64,c*64:(c+1)*64]
            if over:   # só a camada do cajado (para o herói)
                f=np.zeros_like(f)
            out[r*64:(r+1)*64,c*64:(c+1)*64]=draw_staff(f,h[0],h[1],orb,r)
    Image.fromarray(out,'RGBA').save(dst)
if __name__=='__main__':
    os.makedirs('out2',exist_ok=True)
    apply('out/javmago__spellcast.png','out2/javmago__spellcast.png',(176,96,255))
    apply('out/ratalq__spellcast.png','out2/ratalq__spellcast.png',(130,225,70))
    apply(A+'chars/esqmago__spellcast.png','out2/esqmago__spellcast.png',(120,190,255))
    apply(A+'look2/male/spellcast_skin_0.png','out2/w_mago_act_bg.png',(214,140,60),over=True)
    print('ok')
