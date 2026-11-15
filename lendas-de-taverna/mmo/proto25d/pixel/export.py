import sys,json,math,random
sys.path.insert(0,'/home/user/neon-wars/lendas-de-taverna/tools/mmo');sys.path.insert(0,'/home/user/neon-wars/lendas-de-taverna/tools/mmo/pxengine/data')
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from pxengine.character import Character
from pxengine.export import render_anim
from pxengine import effects
from pxdraw import G
D='/home/user/neon-wars/lendas-de-taverna/tools/mmo/pxengine/data/';O='/tmp/s25/'
meta={}
for nm,anims in(('hero',('idle','walk','attack','skill','hurt','block','dodge')),('boss',('idle','walk','attack','skill','hurt','death'))):
    ch=Character(D+nm+'.json');meta[nm]={'W':ch.W,'H':ch.H,'ax':ch.spec['hx_side'],'ay':ch.spec['ground'],'anims':{}}
    for a in anims:
        A=render_anim(ch,a);fr=A['views']['side'];S=np.zeros((ch.H,ch.W*A['n'],4),np.uint8)
        for i,f in enumerate(fr):S[:,i*ch.W:(i+1)*ch.W]=f.rgba
        Image.fromarray(S,'RGBA').save(f'{O}{nm}_{a}.png');meta[nm]['anims'][a]={'n':A['n'],'ms':A['ms'],'loop':A['loop']}
# fx
for k,f in(('slash',effects.slash()),('shock',effects.fire(size=48))):
    S=np.concatenate(f,axis=1);Image.fromarray(S,'RGBA').save(f'{O}fx_{k}.png');meta['fx_'+k]={'n':len(f),'size':48}
# textos em pixel
F=ImageFont.load_default()
def txt(s,col,name):
    im=Image.new('RGBA',(len(s)*7+6,16),(0,0,0,0));d=ImageDraw.Draw(im)
    for dx,dy in((1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,-1),(1,-1),(-1,1)):d.text((3+dx,2+dy),s,font=F,fill=(20,10,24,255))
    d.text((3,2),s,font=F,fill=col+(255,));a=np.array(im);a[...,3]=np.where(a[...,3]>110,255,0);Image.fromarray(a,'RGBA').save(f'{O}t_{name}.png');meta['t_'+name]=list(im.size)
for s,c,n in(('-184',(255,255,255),'d1'),('BLOQUEOU',(120,200,255),'blk'),('-612!',(255,216,74),'d2'),('ESQUIVOU',(200,230,255),'dod'),('-340',(255,255,255),'d3'),('VITORIA!',(255,230,100),'win')):txt(s,c,n)
# cenário em pixel art vivo
def render(g,pal,ink=(24,14,34)):
    h=len(g.g);w=len(g.g[0]);a=np.zeros((h,w,4),np.uint8)
    for y in range(h):
        for x in range(w):
            c=g.g[y][x]
            if c=='.':continue
            if c=='k':a[y,x]=ink+(255,)
            else:a[y,x]=pal[c]+(255,)
    return Image.fromarray(a,'RGBA')
hx=lambda s:tuple(int(s[i:i+2],16) for i in(1,3,5))
LEAF={c:hx(v) for c,v in zip('abcd',('#1d6a66','#2f9e7a','#62cc6c','#b4f48c'))}
TRUNK={c:hx(v) for c,v in zip('efg',('#5a3a22','#8a5a30','#c08848'))}
ROCK={c:hx(v) for c,v in zip('mnop',('#4a5068','#7a82a0','#aab4cc','#e0e8f4'))}
BUSH={c:hx(v) for c,v in zip('qrst',('#2a7a3a','#46b048','#7ee060','#c4ff90'))}
FLW={c:hx(v) for c,v in zip('uvwx',('#c83a6a','#f0609a','#ffa0c0','#fff0f4'))}
random.seed(7)
def tree(seed,w=44,h=64):
    random.seed(seed);g=G(w,h)
    g.poly([(w/2-3,h),(w/2+3,h),(w/2+2,h*.45),(w/2-2,h*.45)],'efg');g.poly([(w/2-8,h-1),(w/2-3,h-6),(w/2+4,h-6),(w/2+9,h-1)],'efg')
    blobs=[(w/2,h*.34,w*.40,h*.26),(w*.3,h*.46,w*.27,h*.2),(w*.7,h*.46,w*.27,h*.2),(w/2,h*.2,w*.28,h*.18),(w*.42,h*.3,w*.22,h*.16)]
    for i,(cx,cy,rx,ry) in enumerate(blobs):g.ell(cx,cy,rx,ry,'abcd',bias=.05*i)
    for _ in range(14):
        x=random.randint(int(w*.15),int(w*.85));y=random.randint(int(h*.1),int(h*.6))
        if g.g[y][x] in 'abcd':g.px(x,y,'d') if random.random()<.5 else g.px(x,y,'a')
    g.outline();return render(g,{**LEAF,**TRUNK})
def rock(seed,w=26,h=18):
    g=G(w,h);g.ell(w*.5,h*.62,w*.46,h*.38,'mnop');g.ell(w*.3,h*.7,w*.24,h*.24,'mnop');g.line(int(w*.4),3,int(w*.5),int(h*.6),'m');g.px(int(w*.38),4,'p');g.outline();return render(g,ROCK)
def bush(w=24,h=16):
    g=G(w,h);g.ell(w*.3,h*.65,w*.28,h*.34,'qrst');g.ell(w*.7,h*.65,w*.28,h*.34,'qrst');g.ell(w*.5,h*.45,w*.3,h*.4,'qrst');
    for p in((8,6),(15,5),(12,9),(18,9)):g.px(p[0],p[1],'t')
    g.outline();return render(g,BUSH)
def flowers(w=12,h=10):
    g=G(w,h);
    for (x,y) in((2,5),(6,3),(9,6)):
        g.px(x,y+2,'s');g.px(x,y+1,'r');g.px(x,y-1,'v');g.px(x-1,y,'v');g.px(x+1,y,'v');g.px(x,y+1,'v');g.px(x,y,'x')
    return render(g,{**BUSH,**FLW})
tree(1,84,120).save(O+'sc_tree1.png');tree(2,76,108).save(O+'sc_tree2.png');tree(3,92,132).save(O+'sc_tree3.png');rock(1,40,26).save(O+'sc_rock1.png');rock(2,30,20).save(O+'sc_rock2.png');bush(38,24).save(O+'sc_bush.png');flowers(14,10).save(O+'sc_flw.png')
json.dump(meta,open(O+'meta.json','w'))
print(meta['hero']['W'],meta['boss']['W'],'ok')
