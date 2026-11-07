"""Ajustes por código nas animações do Grunk: pancada no chão corrigida (corpo de volta + anéis/poeira desenhados), canalização de fúria (aura, defesa e regeneração),
e teste de versão enfurecida por troca de cores. Uso: python3 grunk_fx.py <pasta_saida>"""
import sys,os,math,colorsys,random
import numpy as np
from PIL import Image,ImageDraw
from scipy import ndimage
import cut_grid
CW,CH=360,300;BG=(52,74,46,255)
def rgba(im):return np.array(im.convert('RGBA'))
def strip_fx(im,minsz=90):
    """remove anéis/poeira claros e grandes, preservando dentes e espinhos (componentes pequenos)"""
    a=rgba(im);r,g,b,al=[a[:,:,i].astype(int) for i in range(4)]
    cream=(al>0)&(r>200)&(g>180)&(b>110)&((r-b)<130)
    tan=(al>0)&(r>150)&(g>125)&(b>95)&(r-b<85)&(r-g<45)&(g-b>10)
    fx=cream|tan;lab,n=ndimage.label(fx);out=a.copy()
    for i in range(1,n+1):
        m=lab==i
        if m.sum()>=minsz:out[ndimage.binary_dilation(m,iterations=1),3]=0
    return Image.fromarray(out,'RGBA')
def fxlayer(im,minsz=60):
    a=rgba(im);r,g,b,al=[a[:,:,i].astype(int) for i in range(4)]
    tan=(al>0)&(r>110)&(g>85)&(b>60)&(r-b<95)&(r-g<55)&(g<212)
    lab,n=ndimage.label(tan);out=np.zeros_like(a)
    for i in range(1,n+1):
        m=lab==i
        if m.sum()>=minsz:out[m]=a[m]
    return Image.fromarray(out,'RGBA')
def place(x,bottom=10):
    bg=Image.new('RGBA',(CW,CH),BG);d=ImageDraw.Draw(bg);d.ellipse((CW*.25,CH-52,CW*.75,CH-24),fill=(36,52,34,255))
    bg.alpha_composite(x,((CW-x.width)//2,CH-bottom-x.height));return bg
def ring(canvas,cx,cy,rx,fade=0,th=3):
    ly=Image.new('RGBA',(CW//3+2,CH//3+2),(0,0,0,0));d=ImageDraw.Draw(ly);ry=max(3,int(rx*.26))
    for t,col in((th,(255,214,90,255)),(max(1,th-1),(255,244,200,255))):
        d.ellipse((cx//3-rx//3-t//2,cy//3-ry//3-t//2,cx//3+rx//3+t//2,cy//3+ry//3+t//2),outline=col,width=t)
    d.ellipse((cx//3-rx//3,cy//3-ry//3,cx//3+rx//3,cy//3+ry//3),outline=(255,255,255,255),width=1)
    a=np.array(ly)
    if fade:
        yy,xx=np.mgrid[0:a.shape[0],0:a.shape[1]];a[((xx+yy)%2==0)&(a[:,:,3]>0)&(np.random.RandomState(1).rand(*a.shape[:2])<fade),3]=0
    ly=Image.fromarray(a,'RGBA').resize((ly.width*3,ly.height*3),Image.NEAREST);canvas.alpha_composite(ly)
def save(frames,dur,path):
    ims=[f.convert('RGB').quantize(64,dither=Image.Dither.NONE) for f in frames];ims[0].save(path,save_all=True,append_images=ims[1:],duration=dur,loop=0,disposal=2)
def slam_fixed(an):
    s=an['slam'];body5=strip_fx(s[4]);body7=strip_fx(s[6]);dust=fxlayer(s[5],60);out=[]
    for i,f in enumerate(s):
        if i<4 or i==7:out.append(place(f));continue
        body=body5 if i==4 else body7;c=place(body)
        bb=body.getchannel('A').getbbox();gx=(CW-body.width)//2+(bb[0]+bb[2])//2;gy=CH-10-body.height+bb[3]-4
        cv=Image.new('RGBA',(CW,CH),(0,0,0,0))
        if i>=5:
            d=Image.new('RGBA',(CW,CH),(0,0,0,0));d.alpha_composite(dust,((CW-dust.width)//2,CH-10-dust.height));cv.alpha_composite(d)
        r=[0,0,0,0,46,92,138][i];ring(cv,gx,gy,r,fade=[0,0,0,0,0,0.15,0.45][i])
        base=Image.new('RGBA',(CW,CH),BG);dd=ImageDraw.Draw(base);dd.ellipse((CW*.25,CH-52,CW*.75,CH-24),fill=(36,52,34,255))
        base.alpha_composite(cv);base.alpha_composite(body,((CW-body.width)//2,CH-10-body.height));out.append(base)
    return out
def channel(an,n=10,bg=True):
    src=an['enrage'][-1];a=rgba(src);mask=a[:,:,3]>0;out=[];rs=random.Random(4)
    parts=[(rs.uniform(.15,.85),rs.random(),rs.uniform(.6,1.2)) for _ in range(14)]
    reg=[(rs.uniform(.2,.8),rs.random()) for _ in range(5)]
    for k in range(n):
        t=k/n;pulse=.5+.5*math.sin(2*math.pi*t)
        W,H=src.size;lay=Image.new('RGBA',(CW,CH),(0,0,0,0));ox,oy=(CW-W)//2,CH-10-H
        # brilho na silhueta (pulsante)
        m=ndimage.binary_dilation(mask,iterations=2+int(pulse*3))&~ndimage.binary_dilation(mask,iterations=0)
        glow=np.zeros((H,W,4),dtype='uint8');glow[m]=(230,50,40,int(110+120*pulse));glow[ndimage.binary_dilation(mask,iterations=1)&~mask]=(255,150,70,255)
        lay.alpha_composite(Image.fromarray(glow,'RGBA'),(ox,oy))
        # corpo (leve respiração)
        body=src if k%2==0 else src.transform(src.size,Image.AFFINE,(1,0,0,0,1,-1))
        lay.alpha_composite(body,(ox,oy))
        d=ImageDraw.Draw(lay)
        # escudo dourado de defesa (arcos girando)
        cx,cy=CW//2,oy+H*.52
        for j in range(6):
            a0=math.degrees(2*math.pi*(j/6+t))
            d.arc((cx-W*.62,cy-H*.58,cx+W*.62,cy+H*.58),a0,a0+22,fill=(255,214,64,230),width=3)
        # brasas subindo
        for (px,ph,sp) in parts:
            yy=1-((t*sp+ph)%1);x=ox+W*px+math.sin((t+ph)*6)*4;y=oy+H*.1+yy*H*.9
            d.rectangle((x,y,x+2,y+2),fill=(255,int(120+90*yy),60,int(255*yy)))
        # regeneração: cruzes verdes subindo
        for (px,ph) in reg:
            yy=1-((t+ph)%1);x=ox+W*px;y=oy+H*.15+yy*H*.75;c=(110,235,120,int(255*min(1,yy*1.6)))
            d.rectangle((x-1,y-4,x+1,y+4),fill=c);d.rectangle((x-4,y-1,x+4,y+1),fill=c)
        if not bg:out.append(lay);continue
        base=Image.new('RGBA',(CW,CH),BG);dd=ImageDraw.Draw(base);dd.ellipse((CW*.25,CH-52,CW*.75,CH-24),fill=(36,52,34,255));base.alpha_composite(lay);out.append(base)
    return out
def enraged(im):
    a=rgba(im).astype(float);out=a.copy()
    for y in range(a.shape[0]):
        for x in range(a.shape[1]):
            if a[y,x,3]==0:continue
            r,g,b=a[y,x,:3]/255;h,s,v=colorsys.rgb_to_hsv(r,g,b)
            if .14<h<.30 and s>.2:     # verde-oliva -> marrom avermelhado escuro
                h=.03;s=min(1,s*1.05);v*=.72
            elif .62<h<.80:            # roxo da ombreira -> grená escuro
                h=.97;v*=.7;s*=1.0
            if h<.07 and v>.25 and s>.3:v=min(1,v*1.0)
            out[y,x,:3]=np.array(colorsys.hsv_to_rgb(h,s,v))*255
    return Image.fromarray(out.astype('uint8'),'RGBA')
def aura(frames,tint=(200,30,30)):
    out=[]
    for k,f in enumerate(frames):
        a=rgba(f);m=a[:,:,3]>0;pulse=.5+.5*math.sin(k*1.1)
        ring_=ndimage.binary_dilation(m,iterations=2)&~m;lay=np.zeros_like(a);lay[ring_]=(*tint,int(120+110*pulse))
        o=Image.fromarray(lay,'RGBA');o.alpha_composite(f);out.append(o)
    return out
if __name__=='__main__':
    outd=sys.argv[1];os.makedirs(outd,exist_ok=True);an=cut_grid.main(outd)
    save(slam_fixed(an),[130,110,110,90,110,160,140,120],f'{outd}/grunk_slam_corrigido.gif')
    save(channel(an),[100]*10,f'{outd}/grunk_canalizar.gif')
    for name,dur in(('idle',[220]*6),('attack',[130,110,100,90,120,130,120,120]),('walk',[110]*6)):
        fr=aura([enraged(x) for x in an[name]],(210,30,30));save([place(x) for x in fr],dur,f'{outd}/grunk_enfurecido_{name}.gif')
    print('ok')

# ---------- elmo da forma enfurecida colado nos quadros recoloridos ----------
def eye_point(im,top=None):
    a=rgba(im).astype(int);r,g,b,al=[a[:,:,i] for i in range(4)]
    red=(al>0)&(r>140)&(g<95)&(b<95)&(r-g>70)
    bb=im.getchannel('A').getbbox()
    if bb is None:return None
    y1=bb[1]+int((bb[3]-bb[1])*.5);red[y1:,:]=False
    lab,n=ndimage.label(ndimage.binary_dilation(red,iterations=1));best=None
    for i in range(1,n+1):
        ys,xs=np.where((lab==i)&red)
        if len(ys)<3:continue
        c=(xs.mean(),ys.mean())
        if best is None or c[1]<best[1]:best=c
    return best
def helmet_sprite(src):
    a=rgba(src).astype(int);r,g,b,al=[a[:,:,i] for i in range(4)];bb=src.getchannel('A').getbbox()
    head=np.zeros(al.shape,bool);head[bb[1]:bb[1]+int((bb[3]-bb[1])*.42),:]=True
    gray=(al>0)&head&(abs(r-g)<12)&(abs(g-b)<18)&(np.maximum(np.maximum(r,g),b)<130)&(np.maximum(np.maximum(r,g),b)>26)
    gray=ndimage.binary_opening(gray,iterations=1)
    lab,n=ndimage.label(gray);sz=ndimage.sum(gray,lab,range(1,n+1));keep=1+int(np.argmax(sz));gm=lab==keep    # maior bloco cinza = capacete
    near=ndimage.binary_dilation(gm,iterations=3)
    dark=(al>0)&head&(np.maximum(np.maximum(r,g),b)<70)&ndimage.binary_dilation(gm,iterations=2)
    cream=(al>0)&head&(r>170)&(g>150)&(b>110)&near
    m=gm|dark|cream
    m=ndimage.binary_closing(m,iterations=1)&(al>0)
    out=np.array(src).copy();out[~m,3]=0
    sp=Image.fromarray(out,'RGBA');ep=eye_point(src)
    return sp,ep
def with_helmet(orig_frames,recolored,src):
    hs,he=helmet_sprite(src);out=[]
    eps=[eye_point(o) for o in orig_frames]
    for i,e in enumerate(eps):   # quadros sem olho visível: interpola entre os vizinhos
        if e is None:
            p=next((eps[j] for j in range(i-1,-1,-1) if eps[j] is not None),None);q=next((eps[j] for j in range(i+1,len(eps)) if eps[j] is not None),None)
            eps[i]=((p[0]+q[0])/2,(p[1]+q[1])/2) if p and q else (p or q)
    for o,rc,ep in zip(orig_frames,recolored,eps):
        canvas=rc.copy()
        if ep is not None and he is not None:
            dx=int(round(ep[0]-he[0]));dy=int(round(ep[1]-he[1]))
            lay=Image.new('RGBA',canvas.size,(0,0,0,0));lay.paste(hs,(dx,dy),hs);canvas.alpha_composite(lay)
        out.append(canvas)
    return out
def run_helmet(an,outd):
    src=an['enrage'][3]   # quadro com o elmo e a pele ainda verde: elmo mais legível
    hs,he=helmet_sprite(src);hs.save(f'{outd}/elmo.png');print('olho elmo',he)
    for name,dur in(('idle',[220]*6),('walk',[110]*6),('attack',[130,110,100,90,120,130,120,120]),('charge',[160,90,70,70,100,130]),('slam',[130,110,110,90,110,160,140,120])):
        orig=an[name];rc=[enraged(x) for x in orig];fr=aura(with_helmet(orig,rc,src),(210,30,30))
        save([place(x) for x in fr],dur,f'{outd}/grunk_enfurecido_elmo_{name}.gif')

# ---------- encaixe fino do elmo: escala + deslocamento por quadro (busca) e suavização no tempo ----------
def skin_mask(im):
    a=rgba(im).astype(float);m=np.zeros(a.shape[:2],bool)
    rgb=a[:,:,:3]/255;mx=rgb.max(2);mn=rgb.min(2);s=np.where(mx>0,(mx-mn)/np.maximum(mx,1e-6),0)
    r,g,b=rgb[:,:,0],rgb[:,:,1],rgb[:,:,2]
    return (a[:,:,3]>0)&(g>=r*.92)&(g>b*1.15)&(s>.22)&(mx>.2)         # tons de verde-oliva
def scaled_helmet(hs,he,s):
    if abs(s-1)<1e-3:return hs,he
    w,h=hs.size;n=hs.resize((max(1,round(w*s)),max(1,round(h*s))),Image.NEAREST);return n,(he[0]*s,he[1]*s)
def fit_one(o,hs,he,eye,scales=(.88,.94,1.0,1.06,1.12),rng=7):
    sil=ndimage.binary_dilation(rgba(o)[:,:,3]>0,iterations=2);sk=skin_mask(o);H,W=sil.shape
    yy,xx=np.mgrid[0:H,0:W]
    near=(abs(xx-eye[0])<64)&(yy>eye[1]-78)&(yy<eye[1]+40);Hs=sk&near;up=Hs&(yy<eye[1]-2)
    best=None
    for s in scales:
        sp,sh=scaled_helmet(hs,he,s);hm0=np.array(sp)[:,:,3]>0
        for dy in range(-rng,rng+1):
            for dx in range(-rng,rng+1):
                ox=int(round(eye[0]-sh[0]))+dx;oy=int(round(eye[1]-sh[1]))+dy
                y0,x0=max(0,oy),max(0,ox);y1,x1=min(H,oy+hm0.shape[0]),min(W,ox+hm0.shape[1])
                if y1<=y0 or x1<=x0:continue
                hm=hm0[y0-oy:y1-oy,x0-ox:x1-ox];region=(slice(y0,y1),slice(x0,x1))
                cov=(hm&up[region]).sum()/max(1,up.sum());out=(hm&~sil[region]).sum()/max(1,hm.sum())
                eyeblk=0
                ex,ey=int(eye[0]),int(eye[1])
                if y0<=ey<y1 and x0<=ex<x1 and hm[ey-y0,ex-x0]:eyeblk=1
                score=cov-.55*out-.8*eyeblk-.01*(abs(dx)+abs(dy))-.15*abs(s-1)
                if best is None or score>best[0]:best=(score,s,dx,dy)
    return best
def helmet_params(orig_frames,src):
    hs,he=helmet_sprite(src);eps=[eye_point(o) for o in orig_frames]
    for i,e in enumerate(eps):
        if e is None:
            p=next((eps[j] for j in range(i-1,-1,-1) if eps[j] is not None),None);q=next((eps[j] for j in range(i+1,len(eps)) if eps[j] is not None),None)
            eps[i]=((p[0]+q[0])/2,(p[1]+q[1])/2) if p and q else (p or q)
    P=[fit_one(o,hs,he,e) for o,e in zip(orig_frames,eps)]
    # suavização temporal (média móvel de 3 quadros) para não tremer
    S=[p[1] for p in P];DX=[p[2] for p in P];DY=[p[3] for p in P];n=len(P)
    def sm(v):return [ (v[max(0,i-1)]+2*v[i]+v[min(n-1,i+1)])/4 for i in range(n)]
    return hs,he,eps,sm(S),sm(DX),sm(DY)
def with_helmet_fit(orig_frames,recolored,src):
    hs,he,eps,S,DX,DY=helmet_params(orig_frames,src);out=[]
    for rc,e,s,dx,dy in zip(recolored,eps,S,DX,DY):
        sp,sh=scaled_helmet(hs,he,s);canvas=rc.copy();lay=Image.new('RGBA',canvas.size,(0,0,0,0))
        lay.paste(sp,(int(round(e[0]-sh[0]+dx)),int(round(e[1]-sh[1]+dy))),sp);canvas.alpha_composite(lay);out.append(canvas)
    return out
def run_helmet_fit(an,outd):
    src=an['enrage'][3]
    for name,dur in(('idle',[220]*6),('walk',[110]*6),('attack',[130,110,100,90,120,130,120,120]),('charge',[160,90,70,70,100,130]),('slam',[130,110,110,90,110,160,140,120])):
        orig=an[name];rc=[enraged(x) for x in orig];fr=aura(with_helmet_fit(orig,rc,src),(210,30,30))
        save([place(x) for x in fr],dur,f'{outd}/grunk_elmo2_{name}.gif')
