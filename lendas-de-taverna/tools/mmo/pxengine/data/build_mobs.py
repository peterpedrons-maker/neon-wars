import sys,math,json
sys.path.insert(0,'.')
import numpy as np
from PIL import Image
from pxdraw import G
CW,CH=104,96;AX,AY=46,92
hx=lambda s:tuple(int(s[i:i+2],16) for i in(1,3,5))
RAMPS={'bone':'#7a6a48 #c0b080 #eee0b0 #fffbe0','steel':'#2a3556 #52628c #86a0cc #cce0fa','wood':'#4a2c18 #80502a #b87a3c #e0a860','rag':'#4a3020 #7a5434 #a87848 #d0a468',
 'robe':'#2a1050 #5a24a0 #8a48e0 #c496ff','skin':'#2a4a1c #4c7a2c #7cb43c #bde86c','dark':'#10162c #26325c #46609c #7aa0e0','flame':'#1c4ac8 #3c8cf0 #78d0ff #e8fcff',
 'stone':'#3c4458 #6a748c #9aa6c0 #d4def2','wing':'#2c3450 #4c5a80 #7886b0 #aab8e0','gold':'#8a5a10 #e0a020 #ffd84a #fff4a0','void':'#08040e #120a1c #1c1030 #2a1a44','leaf':'#5a2a18 #a04a28 #e07a30 #ffb860'}
KEY={}   # ramp -> 4 glifos
ch='abcdefghijklmnopqrstuvwxyz'
PAL={};i=0
for n,v in RAMPS.items():
    gl=[ch[i*4+j] if i*4+j<26 else chr(65+i*4+j-26) for j in range(4)];KEY[n]=''.join(gl)
    for g,c in zip(gl,v.split()):PAL[g]=hx(c)
    i+=1
PAL['w']=(255,255,255);PAL['z']=(20,12,30);PAL['R']=(255,70,60);PAL['Y']=(255,230,80);PAL['C']=(120,240,255);PAL['O']=(255,150,40);PAL['S']=(150,20,30)
def K(n):return KEY[n]
def limb(g,x0,y0,x1,y1,w0,w1,ramp):
    dx,dy=x1-x0,y1-y0;L=math.hypot(dx,dy) or 1;px,py=-dy/L,dx/L
    g.poly([(x0+px*w0/2,y0+py*w0/2),(x1+px*w1/2,y1+py*w1/2),(x1-px*w1/2,y1-py*w1/2),(x0-px*w0/2,y0-py*w0/2)],ramp,light=(-.5,-.65))
    g.ell(x1,y1,w1/2,w1/2,ramp)
def blade(g,x0,y0,x1,y1,w,ramp):
    dx,dy=x1-x0,y1-y0;L=math.hypot(dx,dy) or 1;px,py=-dy/L,dx/L
    g.poly([(x0+px*w/2,y0+py*w/2),(x0+dx*.88+px*w/2,y0+dy*.88+py*w/2),(x1,y1),(x0+dx*.88-px*w/2,y0+dy*.88-py*w/2),(x0-px*w/2,y0-py*w/2)],ramp,tone=None)
def render(g):
    a=np.zeros((g.h,g.w,4),np.uint8)
    for y in range(g.h):
        for x in range(g.w):
            c=g.g[y][x]
            if c=='.':continue
            a[y,x]=(PAL.get(c,(20,12,30)) if c!='k' else (20,12,30))+(255,)
    return Image.fromarray(a,'RGBA')
def guard(p):
    g=G(CW,CH);at=p=='attack';lean=6 if at else 0
    limb(g,36,62,33,86,7,6,K('bone'));limb(g,50,62,54,86,7,6,K('bone'))
    g.ell(33,89,7,3.2,K('steel'));g.ell(55,89,7,3.2,K('steel'))
    g.poly([(32,58),(54,58),(58,72),(50,69),(44,75),(38,69),(30,72)],K('rag'))
    g.ell(43+lean*.4,46,14,15,K('steel'));g.line(32,52,54,52,'b');g.rect(40,57,46,59,'v' if False else 'l')
    for (x,y) in((36,44),(48,40),(40,50),(50,48)):g.px(x+lean//3,y,'O')
    g.line(34,38,52,38,'d');g.ell(30,36,6,5,K('steel'));g.ell(56+lean,36,6,5,K('steel'))
    g.ell(46,22,9.5,9.5,K('bone'));g.ell(46+lean*.4,13,10,6,K('steel'));g.rect(38,17,55,18,'b')
    g.px(46,23,'O');g.px(47,23,'O');g.px(52,23,'O');g.px(53,23,'O');g.rect(45,22,48,24,'z');g.rect(51,22,54,24,'z');g.px(46,23,'O');g.px(52,23,'O')
    g.rect(44,29,55,30,'z');
    for x in range(45,55,2):g.px(x,29,'d')
    g.ell(38,27,4,3,K('bone'))
    # braço de trás + escudo
    limb(g,36,40,26,52,6,5,K('bone'));g.ell(24,56,12,15,K('wood'));g.ell(24,56,4.5,5,K('steel'));g.line(24,42,24,70,'f');g.line(12,56,36,56,'f')
    # braço da frente + espada
    if at:limb(g,52,40,70,46,6,5,K('bone'));blade(g,72,46,100,40,5,K('steel'));g.rect(70,42,73,52,'o' if False else 'j')
    else:limb(g,54,42,62,56,6,5,K('bone'));blade(g,62,56,76,28,5,K('steel'));g.rect(58,54,66,58,'j')
    g.outline();return render(g)
def cult(p):
    g=G(CW,CH);at=p=='attack';lean=7 if at else 0
    g.poly([(34,40),(60,40),(66,84),(28,84)],K('robe'),light=(-.4,-.6));g.line(30,80,64,80,'b');g.line(34,56,60,58,'d')
    g.ell(30,88,6,3,K('rag'));g.ell(56,88,6,3,K('rag'));g.line(36,58,58,58,'p')
    g.ell(47+lean*.3,44,13,12,K('robe'));g.ell(47+lean*.5,24,12,13,K('robe'));g.ell(50+lean*.5,25,8,9,K('void'))
    g.px(53+lean//2,24,'R');g.px(54+lean//2,24,'R');g.px(47+lean//2,24,'R');g.px(48+lean//2,24,'R');g.px(48,25,'S')
    g.poly([(38,14),(47,5),(56,14)],K('robe'))
    limb(g,56,42,64+lean*3,50-(2 if at else 0),7,6,K('robe'))
    if at:blade(g,72,48,98,44,4,K('steel'));g.rect(70,44,73,52,'j')
    else:blade(g,64,52,74,36,4,K('steel'));g.rect(61,50,67,54,'j')
    limb(g,38,42,30,56,7,6,K('robe'));blade(g,28,58,18,72,3,K('steel'))
    g.outline();return render(g)
def wraith(p):
    g=G(CW,CH);at=p=='attack';lean=7 if at else 0
    g.poly([(32,62),(60,62),(64,80),(54,90),(46,78),(38,92),(28,80)],K('flame'),light=(-.2,-.8));g.poly([(38,66),(54,66),(50,82),(44,76),(40,84)],K('flame'),tone=3)
    g.ell(46,48,13,15,K('dark'));g.line(34,56,58,56,'n');g.px(40,50,'C');g.px(46,46,'C');g.px(52,52,'C');g.line(44,44,48,52,'C')
    g.ell(30,38,7,5,K('dark'));g.ell(58+lean,38,7,5,K('dark'))
    g.ell(46,23,10,11,K('dark'));g.poly([(40,14),(46,6),(52,14)],K('dark'));g.rect(42,22,54,24,'z');g.rect(43,23,53,23,'C');g.px(47,23,'w');g.px(52,23,'w')
    limb(g,36,42,28,56,6,5,K('dark'))
    if at:limb(g,56,42,74,46,6,5,K('dark'));blade(g,76,46,102,42,5,K('steel'));g.rect(74,42,77,50,'j')
    else:limb(g,56,44,64,56,6,5,K('dark'));blade(g,64,56,76,30,5,K('steel'));g.rect(60,54,68,58,'j')
    g.outline();return render(g)
def garg(p):
    g=G(CW,CH);at=p=='attack';lean=8 if at else 0
    wy=-8 if at else 0
    g.poly([(40,38),(8,16+wy),(14,34),(4,50),(22,46),(18,64),(42,56)],K('wing'),light=(-.3,-.7));g.poly([(52,38),(84,14+wy),(78,32),(90,48),(72,44),(76,62),(50,56)],K('wing'),light=(-.3,-.7))
    for (x1,y1) in((12,24+wy),(8,46),(20,60)):g.line(40,42,x1,y1,'b')
    for (x1,y1) in((82,22+wy),(88,46),(74,58)):g.line(52,42,x1,y1,'b')
    limb(g,36,64,28,78,10,8,K('stone'));limb(g,56,64,62,78,10,8,K('stone'));g.ell(26,86,9,3.5,K('stone'));g.ell(64,86,9,3.5,K('stone'))
    for x in (20,24,28,56,60,64):g.px(x,89,'d')
    g.ell(46+lean*.3,54,15,16,K('stone'));g.line(36,50,56,50,'b');g.line(37,56,55,56,'b');g.line(38,62,54,62,'b')
    limb(g,36,48,28,64+(-6 if at else 0),8,6,K('stone'));limb(g,58,48,66+lean*2,60-(4 if at else 0),8,6,K('stone'))
    for x in (22,26,30):g.px(x,70-(6 if at else 0),'d')
    g.ell(46+lean*.4,28,12,11,K('stone'));g.poly([(36,20),(31,6),(41,16)],K('bone') if False else K('wood')[:0] or K('stone'));g.poly([(58,20),(63,6),(53,16)],K('stone'))
    g.poly([(31,6),(34,10),(37,10)],K('bone'));g.poly([(63,6),(60,10),(57,10)],K('bone'))
    g.px(50+lean//2,26,'Y');g.px(51+lean//2,26,'Y');g.px(41+lean//2,26,'Y');g.px(42+lean//2,26,'Y');g.line(40,24,44,26,'z');g.line(52,24,48,26,'z')
    g.rect(41,34,52,35,'z');g.px(43,36,'w');g.px(50,36,'w')
    g.outline();return render(g)
def zomb(p):
    g=G(CW,CH);at=p=='attack';lean=6 if at else 0
    limb(g,38,64,36,86,11,9,K('rag'));limb(g,54,64,56,86,11,9,K('rag'));g.ell(34,89,8,3.4,K('skin'));g.ell(58,89,8,3.4,K('skin'))
    g.ell(46+lean*.3,52,21,19,K('skin'));g.poly([(26,62),(66,62),(62,78),(30,78)],K('rag'))
    g.ell(40,50,3.5,3,K('skin'));g.px(52,58,'z');g.line(32,60,60,66,'f' if False else 'e')
    for i,(x,y) in enumerate(((34,62),(42,64),(50,65),(58,66))):g.ell(x,y+3,2.6,3,K('gold'))
    g.poly([(30,36),(62,36),(66,46),(46,42),(28,46)],K('rag'))
    limb(g,30,40,16,56,8,7,K('skin'));g.ell(14,59,5,4.5,K('skin'))
    limb(g,62,40,76+(14 if at else 0),52-(2 if at else 0),8,7,K('skin'));g.ell(79+(14 if at else 0),53,5,4.5,K('skin'))
    g.ell(46+lean*.5,26,10,10.5,K('skin'));g.px(43,25,'Y');g.px(44,25,'Y');g.px(51,25,'Y');g.px(52,25,'Y');g.px(44,26,'z');g.px(52,26,'z')
    g.ell(48+lean*.4,32,3.5,2.4,'z'+'z');g.line(40,21,46,20,'a');g.px(36,26,'b')
    g.outline();return render(g)
MOBS={'cult':cult,'guardac':guard,'espectro':wraith,'gargula':garg,'zumbi':zomb}
def rot(im,ang,out=None):
    c=Image.new('RGBA',(CW*2,CH*2),(0,0,0,0));c.paste(im,(CW//2,CH//2));r=c.rotate(ang,center=(CW//2+AX,CH//2+AY),resample=Image.NEAREST)
    a=np.array(r);a[...,3]=np.where(a[...,3]>0,255,0);return Image.fromarray(a,'RGBA')
def tint(im,f):
    a=np.array(im).astype(float);m=a[...,3]>0;a[m,:3]=np.minimum(255,a[m,:3]*(1+f)+30*f);return Image.fromarray(a.astype(np.uint8),'RGBA')
if __name__=='__main__':
    out=sys.argv[1] if len(sys.argv)>1 else '/tmp/mobs/'
    import os;os.makedirs(out,exist_ok=True)
    for k,f in MOBS.items():
        idle=f('idle');att=f('attack')
        hurt=tint(rot(idle,10),.5)
        death=rot(idle,-84);
        # cai de lado: encosta no chão
        bb=death.getbbox();d2=Image.new('RGBA',(CW*2,CH*2),(0,0,0,0));dy=(CH//2+AY+2)-bb[3];d2.paste(death,(0,dy),death);death=tint(d2,-.25)
        frames=[idle,hurt,att,death];cells=[]
        for fr in frames:
            c=Image.new('RGBA',(CW*2,CH*2),(0,0,0,0));c.paste(fr,(0,0),fr) if fr.size==(CW*2,CH*2) else c.paste(fr,(CW//2,CH//2),fr);cells.append(c.crop((CW//2-6,CH//2,CW//2+CW+30,CH//2+CH+2)))
        W,H=cells[0].size;S=Image.new('RGBA',(W*4,H),(0,0,0,0))
        for i,c in enumerate(cells):S.paste(c,(i*W,0),c)
        S.save(f'{out}{k}_px_atlas.png');json.dump({'w':W,'h':H,'ax':AX+6,'ay':AY+2-0,'cols':4,'anims':{'idle':[0],'hurt':[1],'attack':[2],'death':[3]}},open(f'{out}{k}_px_atlas.json','w'))
        print(k,W,H)
