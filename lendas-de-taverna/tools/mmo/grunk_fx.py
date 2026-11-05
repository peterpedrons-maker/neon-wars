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
def channel(an,n=10):
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
