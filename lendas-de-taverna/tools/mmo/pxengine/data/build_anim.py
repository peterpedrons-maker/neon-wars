import sys,math,json,numpy as np
from PIL import Image
from hq import Canvas,finish,S
from rig import *
CW,CH=150,100
def cap(d,a,b,w):
    d.line([(a[0]*S,a[1]*S),(b[0]*S,b[1]*S)],fill=255,width=int(w*S))
    for x,y in(a,b):d.ellipse([(x-w/2)*S,(y-w/2)*S,(x+w/2)*S,(y+w/2)*S],fill=255)
def Epoly(d,c,f,u,rx,ry):
    pts=[(c[0]+f[0]*rx*math.cos(t)+u[0]*ry*math.sin(t),c[1]+f[1]*rx*math.cos(t)+u[1]*ry*math.sin(t)) for t in [i*math.pi/14 for i in range(28)]]
    d.polygon([(x*S,y*S) for x,y in pts],fill=255)
def poly(d,pts):d.polygon([(x*S,y*S) for x,y in pts],fill=255)
def blade(d,a,ang,ln,w):
    r=ang*D2R;dx,dy=math.cos(r),math.sin(r);px,py=-dy,dx;b=(a[0]+dx*ln,a[1]+dy*ln)
    poly(d,[(a[0]+px*w/2,a[1]+py*w/2),(a[0]+dx*ln*.9+px*w/2,a[1]+dy*ln*.9+py*w/2),b,(a[0]+dx*ln*.9-px*w/2,a[1]+dy*ln*.9-py*w/2),(a[0]-px*w/2,a[1]-py*w/2)]);return b
BONE='#5a4a3a #8a7658 #c4b088 #efe2b8 #fff8dc';STEEL='#1c2038 #34426a #5a74a8 #94b4e0 #dcf0ff'
WOOD='#3a1c14 #6a3420 #a05a30 #d48a46 #f0b868';CLOTH='#3a2418 #5e3a24 #8c5c34 #bb8a4c';GOLD='#6a3c08 #b87a14 #f0b830 #fff070'
ROBE='#1c0c40 #3a1878 #6430b8 #9a60f0 #d2a4ff';VOID='#04020a #0a0614 #140c24 #22163a';SKIN='#4a3020 #7a5434 #b08050 #e8c090'
def L(o,fr,uu,a,b):return loc(o,fr,uu,a,b)
def draw_guard(p):
    s=solve(p);c=Canvas(CW,CH);P=s['P'];f=s['f'];u=s['u'];hf=s['hf'];hu=s['hu'];H=s['H']
    # pernas
    for k in('B','F'):
        hip,kn,ft=s['hip'+k],s['knee'+k],s['foot'+k]
        c.shape(lambda d:cap(d,hip,kn,6.5),BONE)
        c.shape(lambda d:cap(d,kn,ft,6.5),BONE)
        mid=((kn[0]+ft[0])/2,(kn[1]+ft[1])/2);c.shape(lambda d:cap(d,mid,ft,7.4),STEEL,blur=1.4)
        c.shape(lambda d:(Epoly(d,(kn[0]+.5,kn[1]),(1,0),(0,-1),4.2,3.6)),STEEL,blur=1.4)
        fo=(ft[0]+3,ft[1]+2);c.shape(lambda d:Epoly(d,fo,(1,0),(0,-1),8,3.6),STEEL,blur=1.3)
        if k=='B':
            # pano de tras
            sw=p['sway']
            c.shape(lambda d:poly(d,[L(P,f,u,-12,-2),L(P,f,u,6,-2),(P[0]+12+sw,P[1]+18),(P[0]+2+sw,P[1]+12),(P[0]-4+sw,P[1]+19),(P[0]-13+sw,P[1]+14)]),CLOTH,blur=1.6)
    # braco de tras + escudo
    c.shape(lambda d:cap(d,s['sB'],s['elB'],6),BONE);c.shape(lambda d:cap(d,s['elB'],s['handB'],5.4),BONE)
    sh=(s['handB'][0]-5,s['handB'][1]+1);sa=p['sa']*D2R;sf=(math.cos(sa),math.sin(sa));su=(math.sin(sa),-math.cos(sa))
    c.shape(lambda d:Epoly(d,sh,sf,su,12.5,15.5),WOOD,blur=3);c.shape(lambda d:Epoly(d,sh,sf,su,12.5,15.5),WOOD,flat='#14080c')
    c.shape(lambda d:Epoly(d,sh,sf,su,11.4,14.4),WOOD,blur=4);c.shape(lambda d:Epoly(d,sh,sf,su,4.6,5),STEEL,blur=1.8)
    for ang in range(0,360,60):
        q=(math.cos(ang*D2R)*9,math.sin(ang*D2R)*12);pt=L(sh,sf,su,q[0],q[1]);c.shape(lambda d:Epoly(d,pt,(1,0),(0,-1),1.1,1.1),STEEL,flat='#aac4ee')
    c.shape(lambda d:cap(d,L(sh,sf,su,0,-14),L(sh,sf,su,0,14),.9),WOOD,flat='#2a120c');c.shape(lambda d:cap(d,L(sh,sf,su,-12,0),L(sh,sf,su,12,0),.9),WOOD,flat='#2a120c')
    # torso
    tc=L(P,f,u,0,11)
    c.shape(lambda d:Epoly(d,tc,f,u,13.5,14.5),STEEL,blur=3.2)
    c.shape(lambda d:poly(d,[L(P,f,u,-9,-4),L(P,f,u,9,-4),L(P,f,u,8,2),L(P,f,u,-8,2)]),CLOTH,blur=1.2)
    c.shape(lambda d:cap(d,L(P,f,u,-10,12),L(P,f,u,10,12),1),STEEL,flat='#1c2038');c.shape(lambda d:cap(d,L(P,f,u,0,4),L(P,f,u,0,22),1),STEEL,flat='#1c2038')
    c.shape(lambda d:Epoly(d,L(P,f,u,0,-1.5),f,u,2.6,2),GOLD,blur=.8)
    for k,sg in(('B',-1),('F',1)):
        c.shape(lambda d:Epoly(d,L(s['N'],f,u,sg*7,-2.5),f,u,7.4,6),STEEL,blur=2.4)
        for a in(-3,3):c.shape(lambda d:Epoly(d,L(s['N'],f,u,sg*7+a,-2),(1,0),(0,-1),1,1),STEEL,flat='#e6f4ff')
    # pescoco/cabeca
    c.shape(lambda d:cap(d,s['N'],L(s['N'],hf,hu,0,7),5),BONE)
    c.shape(lambda d:Epoly(d,H,hf,hu,9.5,10),BONE,blur=3)
    c.shape(lambda d:poly(d,[L(H,hf,hu,-5,-6),L(H,hf,hu,6,-6),L(H,hf,hu,5,-11+p['jaw']*-.3),L(H,hf,hu,-4,-11+p['jaw']*-.3)]),BONE,blur=1)
    for x in range(-3,6,2):c.shape(lambda d:cap(d,L(H,hf,hu,x,-6.5),L(H,hf,hu,x,-9.5-p['jaw']*.3),.8),BONE,flat='#2a1a14')
    for ex in(-3,5):
        c.shape(lambda d:Epoly(d,L(H,hf,hu,ex,-.5),hf,hu,2.8,3.2),BONE,flat='#0c060a')
        c.shape(lambda d:Epoly(d,L(H,hf,hu,ex+.5,-.7),(1,0),(0,-1),1.2+.5*p['pulse'],1.4+.5*p['pulse']),BONE,flat='#ff9a30' if p['pulse']<.5 else '#ffd070')
    c.shape(lambda d:poly(d,[L(H,hf,hu,1,-3),L(H,hf,hu,3,-3),L(H,hf,hu,2.6,-6),L(H,hf,hu,1.4,-6)]),BONE,flat='#0c060a')
    c.shape(lambda d:(Epoly(d,L(H,hf,hu,0,6),hf,hu,10.6,7.5),poly(d,[L(H,hf,hu,-10,6),L(H,hf,hu,10,6),L(H,hf,hu,9,3),L(H,hf,hu,-9,3)])),STEEL,blur=2.8)
    c.shape(lambda d:poly(d,[L(H,hf,hu,-1.5,6),L(H,hf,hu,1.5,6),L(H,hf,hu,1,-2),L(H,hf,hu,-1,-2)]),STEEL,blur=.8)
    sw=p['sway']*.4
    c.shape(lambda d:poly(d,[L(H,hf,hu,-2,15),L(H,hf,hu,3,15),L(H,hf,hu,4-sw*2,11),L(H,hf,hu,-3,11)]),'#7a1820 #b02830 #e04a40 #ff8a70',blur=1)
    # braco da frente + espada
    c.shape(lambda d:cap(d,s['sF'],s['elF'],6),BONE);c.shape(lambda d:cap(d,s['elF'],s['handF'],5.4),BONE)
    hnd=s['handF'];tip=None
    def sword(d):
        global tip
        tip=blade(d,hnd,p['wa'],26,4.5)
    c.shape(sword,STEEL,blur=.7)
    wr=p['wa']*D2R;gd=(hnd[0]-math.cos(wr)*0,hnd[1]-math.sin(wr)*0)
    gx0=(hnd[0]-math.sin(wr)*5,hnd[1]+math.cos(wr)*5);gx1=(hnd[0]+math.sin(wr)*5,hnd[1]-math.cos(wr)*5)
    c.shape(lambda d:cap(d,gx0,gx1,2),GOLD,blur=.8)
    pm=(hnd[0]-math.cos(wr)*5,hnd[1]-math.sin(wr)*5);c.shape(lambda d:Epoly(d,pm,(1,0),(0,-1),2.4,2.4),GOLD,blur=.8)
    c.shape(lambda d:Epoly(d,hnd,(1,0),(0,-1),3.2,3),BONE,blur=1.3)
    return c
# ---------- animacoes (poses-chave) ----------
def anim_guard():
    idle=lambda t:pose(dy=.7*math.sin(t*6.2832),lean=1.2*math.sin(t*6.2832+.6),head=1.5*math.sin(t*6.2832-.5),handF=(12,14+1.2*math.sin(t*6.2832+1)),handB=(-12,14+.8*math.sin(t*6.2832)),wa=-78+3*math.sin(t*6.2832+1),sway=1.5*math.sin(t*6.2832-1),pulse=.5+.5*math.sin(t*12.566),sa=2*math.sin(t*6.2832))
    B=pose()
    atk=[(0,B),(.14,pose(dy=2.5,lean=-5,handF=(4,-4),wa=-120,footF=(14,0),footB=(-14,0),head=-3,sa=-4)),
         (.34,pose(dy=1.5,lean=-11,torso=-5,head=-5,handF=(-9,-24),wa=-152,footF=(14,0),footB=(-15,0),handB=(-9,10),sa=-8,jaw=2,pulse=1,_e='out')),
         (.46,pose(dy=2,lean=3,dx=3,handF=(10,-14),wa=-60,footF=(18,0),handB=(-10,12),_e='in')),
         (.56,pose(dx=8,dy=3,lean=15,torso=5,head=4,handF=(28,-1),wa=-4,footF=(21,0),footB=(-4,0),handB=(-13,16),sa=10,pulse=1,_e='in')),
         (.70,pose(dx=10,dy=3.5,lean=17,torso=5,head=5,handF=(33,7),wa=14,footF=(22,0),footB=(-3,0),handB=(-14,17),sa=14,pulse=1,_e='out')),
         (.86,pose(dx=6,dy=2,lean=9,handF=(25,11),wa=22,footF=(18,0),footB=(-8,0),sa=6)),
         (1,B)]
    hurt=[(0,pose(dx=-5,dy=1,lean=-15,torso=-7,head=-14,handF=(5,2),wa=-100,handB=(-17,2),sa=-15,footF=(9,0),footB=(-17,0),jaw=4,flash=1,pulse=1)),
          (.5,pose(dx=-3,lean=-9,torso=-4,head=-8,handF=(8,8),wa=-90,handB=(-15,8),sa=-8,footF=(10,0),footB=(-15,0),jaw=3)),
          (1,pose(dx=-1,lean=-3,head=-3,handF=(11,12),wa=-80))]
    death=[(0,pose(dx=-5,dy=1,lean=-15,torso=-7,head=-14,handF=(5,2),wa=-100,handB=(-17,2),sa=-15,footF=(9,0),footB=(-17,0),jaw=4,flash=1,pulse=1)),
           (.18,pose(dx=-8,dy=3,lean=-12,torso=-4,head=-6,handF=(4,8),wa=-60,handB=(-18,6),sa=-20,footF=(6,0),footB=(-20,0))),
           (.34,pose(dx=-8,dy=11,lean=-8,torso=-2,head=4,handF=(2,16),wa=-30,handB=(-14,16),sa=-10,footF=(8,-1),footB=(-22,0),jaw=5)),
           (.5,pose(dx=-9,dy=12,post=2,grot=-22,lean=-5,handF=(-4,20),wa=10,handB=(-10,16),sa=-30,footF=(8,-3),footB=(-24,0),jaw=5,pulse=0)),
           (.68,pose(dx=-10,dy=10,post=7,grot=-52,lean=-2,handF=(-2,22),wa=60,handB=(-8,14),footF=(4,-8),footB=(-20,-2),jaw=6,pulse=0)),
           (.84,pose(dx=-10,dy=6,post=13,grot=-80,handF=(-2,24),wa=100,handB=(-6,12),footF=(2,-10),footB=(-18,-4),jaw=6,pulse=0)),
           (.93,pose(dx=-10,dy=3,post=15,grot=-87,handF=(0,24),wa=80,handB=(-6,12),footF=(2,-10),footB=(-18,-4),jaw=6,pulse=0)),
           (1,pose(dx=-10,dy=4,post=14,grot=-90,handF=(0,24),wa=70,handB=(-6,12),footF=(2,-10),footB=(-18,-4),jaw=6,pulse=0))]
    return idle,atk,hurt,death
def rgbdim(im,f):
    a=np.array(im).astype(float);m=a[...,3]>0;a[m,:3]=np.clip(a[m,:3]*f,0,255);return Image.fromarray(a.astype(np.uint8),'RGBA')
def flash(im,k):
    a=np.array(im).astype(float);m=a[...,3]>0;a[m,:3]=np.clip(a[m,:3]*(1-k)+255*k,0,255);return Image.fromarray(a.astype(np.uint8),'RGBA')
def build(name,draw,anims,out,nidle=8,natk=8,nhurt=3,ndeath=8):
    idle,atk,hurt,death=anims;frames=[];meta={}
    def add(lbl,ps):
        meta[lbl]=list(range(len(frames),len(frames)+len(ps)))
        for p in ps:
            im=finish(draw(p))
            if p.get('flash'):im=flash(im,.55*p['flash'])
            if lbl=='death':
                bb=im.getbbox()
                if bb and bb[3]>GY+2:
                    sh=bb[3]-(GY+2);im=im.transform(im.size,Image.AFFINE,(1,0,0,0,1,sh),resample=Image.NEAREST)
            frames.append(im)
    add('idle',[idle(i/nidle) for i in range(nidle)])
    add('attack',[sample(atk,i/(natk-1)) for i in range(natk)])
    add('hurt',[sample(hurt,i/(nhurt-1)) for i in range(nhurt)])
    add('death',[sample(death,i/(ndeath-1)) for i in range(ndeath)])
    cols=8;rows=(len(frames)+cols-1)//cols;A=Image.new('RGBA',(CW*cols,CH*rows),(0,0,0,0))
    for i,f in enumerate(frames):A.paste(f,((i%cols)*CW,(i//cols)*CH),f)
    A.save(f'{out}/{name}_px_atlas.png')
    json.dump({'w':CW,'h':CH,'ax':GX,'ay':GY,'cols':cols,'anims':meta,'fps':{'idle':8,'death':10},'imp':.56},open(f'{out}/{name}_px_atlas.json','w'))
    return frames,meta
if False:
    out=sys.argv[1];import os;os.makedirs(out,exist_ok=True)
    fr,meta=build('guardac',draw_guard,anim_guard(),out)
    sel=meta['idle'][::2]+meta['attack']+meta['hurt']+meta['death']
    W=8;Sh=Image.new('RGB',(CW*W,CH*((len(sel)+W-1)//W)),(58,92,120))
    for i,k in enumerate(sel):Sh.paste(fr[k],((i%W)*CW,(i//W)*CH),fr[k])
    Sh.save(out+'/guard_sheet.png');print(Sh.size)

def draw_cult(p):
    s=solve(p,legh=24);c=Canvas(CW,CH);P=s['P'];f=s['f'];u=s['u'];hf=s['hf'];hu=s['hu'];H=s['H'];sw=p['sway']
    for k in('B','F'):
        ft=s['foot'+k];c.shape(lambda d:Epoly(d,(ft[0]+2,ft[1]+2),(1,0),(0,-1),6.4,3),CLOTH,blur=1.3)
    N=s['N'];g_=s['g'];Rr=lambda q:(GX+(q[0]-GX)*math.cos(g_)-(q[1]-GY)*math.sin(g_),GY-p['post']+(q[0]-GX)*math.sin(g_)+(q[1]-GY)*math.cos(g_))
    # manto
    top=[L(N,f,u,-12,-4),L(N,f,u,12,-4)]
    hem=[Rr(q) for q in[(GX+30+sw*.6,GY-1),(GX+22+sw*.3,GY+1),(GX+8,GY),(GX-6,GY+1),(GX-20-sw*.5,GY),(GX-30-sw,GY-3)]]
    c.shape(lambda d:poly(d,[top[0],L(P,f,u,-13,3)]+[hem[-1]]+hem[-2::-1]+[L(P,f,u,13,3),top[1]]),ROBE,blur=4)
    c.shape(lambda d:poly(d,[L(P,f,u,-9,6),L(P,f,u,9,6),Rr((GX+10+sw*.3,GY-1)),Rr((GX-12-sw*.4,GY-1))]),ROBE,blur=3,light=(-.2,-.8))
    for x in(-17,-8,2,12):
        a=L(P,f,u,x*.4,4);b=Rr((GX+x*1.5+sw*(.3+(x+17)/60),GY-2));c.shape(lambda d:cap(d,a,b,.9),ROBE,flat='#1a0a38')
    c.shape(lambda d:poly(d,[Rr((GX-26-sw*.5,GY-9)),Rr((GX+27+sw*.5,GY-9)),Rr((GX+28+sw*.6,GY-6)),Rr((GX-27-sw*.6,GY-6))]),GOLD,blur=.9)
    for x in range(-22,26,6):c.shape(lambda d:Epoly(d,Rr((GX+x+sw*.3,GY-7.5)),(1,0),(0,-1),1.1,1.1),GOLD,flat='#fff0a0')
    c.shape(lambda d:poly(d,[L(P,f,u,-8,-1),L(P,f,u,8,-1),L(P,f,u,7,3),L(P,f,u,-7,3)]),GOLD,blur=.9)
    c.shape(lambda d:Epoly(d,L(P,f,u,0,1),f,u,2.6,2.4),ROBE,flat='#c02840')
    # braço de tras (mao magica)
    c.shape(lambda d:cap(d,s['sB'],s['elB'],6.5),ROBE);c.shape(lambda d:cap(d,s['elB'],s['handB'],6),ROBE)
    hb=s['handB'];c.shape(lambda d:Epoly(d,hb,(1,0),(0,-1),3,3),SKIN,blur=1)
    gl=.5+.5*p['pulse']
    # peito
    c.shape(lambda d:Epoly(d,L(P,f,u,0,12),f,u,14,13),ROBE,blur=3.4)
    # capuz
    c.shape(lambda d:(Epoly(d,H,hf,hu,13,14),poly(d,[L(H,hf,hu,-13,6),L(H,hf,hu,0,22),L(H,hf,hu,13,6)])),ROBE,blur=3.6)
    c.shape(lambda d:Epoly(d,L(H,hf,hu,3,-1),hf,hu,8,9.5),VOID,blur=3,light=(0,0))
    e=2.0+1.2*p['pulse']
    for x in(0,6):
        c.shape(lambda d:Epoly(d,L(H,hf,hu,x,0),hf,hu,e,1.7),VOID,flat='#ff3a4a');c.shape(lambda d:Epoly(d,L(H,hf,hu,x-.4,.3),(1,0),(0,-1),.8,.7),VOID,flat='#ffe0e0')
    c.shape(lambda d:poly(d,[L(H,hf,hu,0,-8),L(H,hf,hu,6,-8),L(H,hf,hu,5.4,-9.3),L(H,hf,hu,.6,-9.3)]),VOID,flat='#c8a0ff')
    # braço da frente + adaga
    c.shape(lambda d:cap(d,s['sF'],s['elF'],6.5),ROBE);c.shape(lambda d:cap(d,s['elF'],s['handF'],6),ROBE)
    hn=s['handF'];c.shape(lambda d:blade(d,hn,p['wa'],17,3.4),STEEL,blur=.6)
    wr=p['wa']*D2R;g0=(hn[0]-math.sin(wr)*3.5,hn[1]+math.cos(wr)*3.5);g1=(hn[0]+math.sin(wr)*3.5,hn[1]-math.cos(wr)*3.5)
    c.shape(lambda d:cap(d,g0,g1,1.8),GOLD,blur=.8)
    pm=(hn[0]-math.cos(wr)*4,hn[1]-math.sin(wr)*4);c.shape(lambda d:Epoly(d,pm,(1,0),(0,-1),2.2,2.2),VOID,flat='#ff3a4a')
    c.shape(lambda d:Epoly(d,hn,(1,0),(0,-1),3,3),SKIN,blur=1)
    # orbe magico na mao de tras durante o ataque
    if p['pulse']>.15:
        r=3+5*p['pulse'];c.shape(lambda d:Epoly(d,(hb[0]+4,hb[1]-3),(1,0),(0,-1),r,r),VOID,flat='#e8c0ff');c.shape(lambda d:Epoly(d,(hb[0]+4,hb[1]-3),(1,0),(0,-1),r*.6,r*.6),VOID,flat='#ffffff')
    return c
def anim_cult():
    sin=math.sin
    idle=lambda t:pose(footB=(-10,0),footF=(10,0),dy=1.2*sin(t*6.2832),lean=1.5*sin(t*6.2832+.7),head=2*sin(t*6.2832-.6),handF=(12,14+1.6*sin(t*6.2832+1)),handB=(-12,14+1.2*sin(t*6.2832)),wa=-64+4*sin(t*6.2832+.8),sway=2.5*sin(t*6.2832-1.2),pulse=.35+.35*sin(t*12.566))
    B=pose(footB=(-10,0),footF=(10,0),wa=-64)
    atk=[(0,B),(.16,pose(footB=(-10,0),footF=(10,0),dy=2,lean=-6,head=-4,handF=(2,0),handB=(-10,4),wa=-110,sway=-3,pulse=.3)),
         (.38,pose(footB=(-11,0),footF=(10,0),dy=1,lean=-12,torso=-4,head=-8,handF=(-6,-20),handB=(2,-12),wa=-150,sway=-5,pulse=.7,_e='out')),
         (.52,pose(footB=(-11,0),footF=(11,0),dx=3,dy=2,lean=2,handF=(12,-10),handB=(14,-6),wa=-70,sway=4,pulse=1,_e='in')),
         (.6,pose(footB=(-8,0),footF=(14,0),dx=7,dy=2.5,lean=15,torso=4,head=5,handF=(26,2),handB=(30,-8),wa=-6,sway=8,pulse=1,_e='in')),
         (.74,pose(footB=(-6,0),footF=(15,0),dx=9,dy=3,lean=17,torso=4,head=6,handF=(29,8),handB=(33,-6),wa=12,sway=10,pulse=1,_e='out')),
         (.88,pose(footB=(-8,0),footF=(12,0),dx=5,dy=2,lean=8,handF=(22,10),handB=(18,4),wa=-20,sway=4,pulse=.4)),(1,B)]
    h0=pose(footB=(-12,0),footF=(8,0),dx=-5,dy=1,lean=-16,torso=-8,head=-15,handF=(4,2),handB=(-16,2),wa=-100,sway=-8,flash=1,pulse=0)
    hurt=[(0,h0),(.5,pose(footB=(-11,0),footF=(9,0),dx=-3,lean=-9,torso=-4,head=-8,handF=(8,8),handB=(-15,8),wa=-90,sway=-4)),(1,pose(footB=(-10,0),footF=(10,0),dx=-1,lean=-3,head=-3,wa=-70,sway=-1))]
    death=[(0,h0),(.2,pose(footB=(-14,0),footF=(6,0),dx=-8,dy=3,lean=-14,torso=-4,head=-8,handF=(2,8),wa=-50,handB=(-18,8),sway=-10,pulse=0)),
           (.4,pose(footB=(-16,0),footF=(6,0),dx=-9,dy=12,lean=-8,head=4,handF=(2,16),handB=(-14,18),wa=-20,sway=-6,pulse=0)),
           (.58,pose(footB=(-18,0),footF=(6,0),dx=-9,dy=12,post=2,grot=-30,handF=(-2,20),handB=(-10,18),wa=20,sway=-4,pulse=0)),
           (.75,pose(footB=(-18,0),footF=(2,-6),dx=-10,dy=8,post=8,grot=-62,handF=(0,22),handB=(-8,14),wa=70,pulse=0)),
           (.9,pose(footB=(-18,-2),footF=(2,-8),dx=-10,dy=4,post=14,grot=-86,handF=(0,24),handB=(-6,12),wa=90,pulse=0)),
           (1,pose(footB=(-18,-2),footF=(2,-8),dx=-10,dy=4,post=14,grot=-90,handF=(0,24),handB=(-6,12),wa=80,pulse=0))]
    return idle,atk,hurt,death
def main2(out):
    import os;os.makedirs(out,exist_ok=True)
    for n,d,a in(('guardac',draw_guard,anim_guard()),('cult',draw_cult,anim_cult())):
        fr,meta=build(n,d,a,out)
        sel=meta['idle'][::2]+meta['attack']+meta['hurt']+meta['death'];W=8
        Sh=Image.new('RGB',(CW*W,CH*((len(sel)+W-1)//W)),(58,92,120))
        for i,k in enumerate(sel):Sh.paste(fr[k],((i%W)*CW,(i//W)*CH),fr[k])
        Sh.save(f'{out}/{n}_sheet.png')
if __name__=='__main__':main2(sys.argv[1])
