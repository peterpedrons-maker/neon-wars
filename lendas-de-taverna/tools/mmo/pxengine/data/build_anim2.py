import sys,math,json,numpy as np
from PIL import Image
from hq import Canvas,finish,S
from rig2 import *
from build_anim import cap,Epoly,poly,blade,BONE,STEEL,WOOD,CLOTH,GOLD,ROBE,VOID,SKIN,flash
CW,CH=180,124
CAPE='#240a14 #44121e #76202e #b04050 #e07080'
BONE2='#4a3a2c #7a6648 #b49c70 #e0d0a0 #fff4d0'
def loc(o,f,u,a,b):return (o[0]+f[0]*a+u[0]*b,o[1]+f[1]*a+u[1]*b)
def strip(d,nodes,w0,w1):
    n=len(nodes);L=[];R=[]
    for i,(x,y) in enumerate(nodes):
        a=nodes[max(0,i-1)];b=nodes[min(n-1,i+1)];dx,dy=b[0]-a[0],b[1]-a[1];l=math.hypot(dx,dy) or 1;px,py=-dy/l,dx/l;w=(w0+(w1-w0)*i/(n-1))/2
        L.append((x+px*w,y+py*w));R.append((x-px*w,y-py*w))
    poly(d,L+R[::-1])
def foot(c,E,toe,heel,ramp,wid=4.6):
    ctr=((toe[0]+heel[0])/2,(toe[1]+heel[1])/2);dx,dy=toe[0]-heel[0],toe[1]-heel[1];l=math.hypot(dx,dy) or 1;f=(dx/l,dy/l);u=(f[1],-f[0])
    c.shape(lambda d:Epoly(d,(ctr[0],ctr[1]+1.5),f,u,l/2+2,wid*.62),ramp,blur=1.4)
    c.shape(lambda d:Epoly(d,(toe[0]-f[0]*1.5,toe[1]-f[1]*1.5+1),f,u,3.4,wid*.5),ramp,blur=1)
def hand(c,wr,ang,ramp,grip=0):
    f=(math.cos(ang),math.sin(ang));u=(f[1],-f[0]);pc=add(wr,f,2.4)
    c.shape(lambda d:Epoly(d,pc,f,u,3.2,3),ramp,blur=1.2)
    for k,o in enumerate((-1.6,0,1.6)):
        a=add(add(wr,f,4),u,o);b=add(a,f,2.2-abs(o)*.3);c.shape(lambda d:cap(d,a,b,1.5),ramp,blur=.6)
    t0=add(add(wr,f,2),u,-2.4);t1=add(t0,f,2.6);c.shape(lambda d:cap(d,t0,t1,1.6),ramp,blur=.6)
def limb(c,a,b,w,ramp,blur=2.2):c.shape(lambda d:cap(d,a,b,w),ramp,blur=blur)
def draw_guard(p):
    s=solve(p);c=Canvas(CW,CH);P=s['P'];N=s['N'];W=s['W'];H=s['H'];f0,u0,f2,u2,fh,uh=s['f0'],s['u0'],s['f2'],s['u2'],s['fh'],s['uh'];ch=p['_ch']
    # capa (atras de tudo)
    c.shape(lambda d:strip(d,ch['cape'],13,9),CAPE,blur=3);
    c.shape(lambda d:strip(d,ch['cape'][1:],3,2),CAPE,flat='#e07080')
    # perna de tras
    for k in('B','F'):
        hip,kn,an=s['hip'+k],s['knee'+k],s['ank'+k]
        limb(c,hip,kn,8.4,BONE2);limb(c,kn,an,6.8,BONE2)
        for q in(.25,.55,.8):limb(c,add(hip,(kn[0]-hip[0],kn[1]-hip[1]),q),add(hip,(kn[0]-hip[0],kn[1]-hip[1]),q),1.2,BONE2) if False else None
        c.shape(lambda d:Epoly(d,kn,(1,0),(0,-1),5.2,4.6),STEEL,blur=1.6)
        c.shape(lambda d:cap(d,add(kn,(an[0]-kn[0],an[1]-kn[1]),.35),add(an,(0,0),0),8.2),STEEL,blur=1.5)
        c.shape(lambda d:cap(d,add(kn,(an[0]-kn[0],an[1]-kn[1]),.2),add(kn,(an[0]-kn[0],an[1]-kn[1]),.2),3),GOLD,flat='#b87a14')
        foot(c,an,s['toe'+k],s['heel'+k],STEEL)
        if k=='B':
            # braco de tras + escudo
            sB,eB,wB=s['sB'],s['elB'],s['wrB']
            limb(c,sB,eB,7.4,BONE2);c.shape(lambda d:Epoly(d,eB,(1,0),(0,-1),4,4),BONE2,blur=1.4);limb(c,eB,wB,6.4,BONE2)
            c.shape(lambda d:cap(d,add(eB,(wB[0]-eB[0],wB[1]-eB[1]),.35),wB,7.6),STEEL,blur=1.4)
            hb=s['handB'];sa=p['sa']*D2R;sf=F(sa);su=U(sa);sh=(hb[0]-3,hb[1]+1)
            hand(c,wB,s['haB'],BONE2)
            c.shape(lambda d:Epoly(d,sh,sf,su,14.5,18),WOOD,blur=3);c.shape(lambda d:Epoly(d,sh,sf,su,14.5,18),WOOD,flat='#14080c')
            c.shape(lambda d:Epoly(d,sh,sf,su,13.4,16.9),WOOD,blur=4)
            for q in(-1,1):c.shape(lambda d:cap(d,loc(sh,sf,su,q*8,-12),loc(sh,sf,su,q*8,12),1.6),WOOD,flat='#4a2414')
            c.shape(lambda d:Epoly(d,sh,sf,su,5.6,6),STEEL,blur=2);c.shape(lambda d:Epoly(d,loc(sh,sf,su,-1,-1),sf,su,2,2),STEEL,flat='#dcf0ff')
            for ang in range(0,360,45):
                q=(math.cos(ang*D2R)*11,math.sin(ang*D2R)*14.5);pt=loc(sh,sf,su,q[0],q[1]);c.shape(lambda d:Epoly(d,pt,(1,0),(0,-1),1.2,1.2),STEEL,flat='#aac4ee')
            c.shape(lambda d:cap(d,loc(sh,sf,su,0,-16),loc(sh,sf,su,0,16),1),WOOD,flat='#2a120c');c.shape(lambda d:cap(d,loc(sh,sf,su,-13,0),loc(sh,sf,su,13,0),1),WOOD,flat='#2a120c')
            hand(c,wB,s['haB']+0,BONE2)
        if k=='B':
            # coluna/pelvis (entre as pernas)
            c.shape(lambda d:Epoly(d,P,f0,u0,10.5,5),BONE2,blur=2)
            c.shape(lambda d:Epoly(d,loc(P,f0,u0,0,-.5),f0,u0,3,2.3),BONE2,flat='#0c060a')
    # perna da frente ja desenhada no loop; torso por cima
    c.shape(lambda d:poly(d,[loc(P,f0,u0,-10,5),loc(P,f0,u0,10,5),add(loc(P,f0,u0,9,0),F(math.pi/2+s['p']['lean']*D2R*0),12),add(loc(P,f0,u0,-9,0),F(math.pi/2),12)]),CLOTH,blur=2)
    # costelas aparentes (abdomen)
    for q in range(3):
        c.shape(lambda d:cap(d,loc(W,f2,u2,-5.5,-3-q*0),loc(W,f2,u2,5.5,-3-q*0),1.6),BONE2,flat='#c4b088') if False else None
    for q in range(3):
        y=-3+q*3.2;c.shape(lambda d:cap(d,loc(W,f2,u2,-6,y),loc(W,f2,u2,6,y),1.5),BONE2,blur=.6)
    limb(c,P,W,3.4,BONE2,blur=1.2)
    c.shape(lambda d:poly(d,[loc(P,f0,u0,-9,1),loc(P,f0,u0,9,1),loc(P,f0,u0,8,6),loc(P,f0,u0,-8,6)]),CLOTH,blur=1.2)
    c.shape(lambda d:Epoly(d,loc(P,f0,u0,0,4),f0,u0,2.8,2.2),GOLD,blur=.8)
    # peitoral
    ct=((W[0]+N[0])/2,(W[1]+N[1])/2)
    c.shape(lambda d:Epoly(d,ct,f2,u2,14.5,12.5),STEEL,blur=3.4)
    c.shape(lambda d:cap(d,loc(ct,f2,u2,0,-10),loc(ct,f2,u2,0,9),1.2),STEEL,flat='#1c2038');c.shape(lambda d:cap(d,loc(ct,f2,u2,-12,2),loc(ct,f2,u2,12,2),1.1),STEEL,flat='#1c2038')
    c.shape(lambda d:Epoly(d,loc(ct,f2,u2,0,2),f2,u2,3,2.6),GOLD,blur=.8)
    for t in(-1,1):c.shape(lambda d:cap(d,loc(ct,f2,u2,t*10.5,-8),loc(ct,f2,u2,t*7,-9.5),1),GOLD,flat='#f0b830')
    # tassets
    for k in('B','F'):
        hip,kn=s['hip'+k],s['knee'+k];a=add(hip,(kn[0]-hip[0],kn[1]-hip[1]),.1);b=add(hip,(kn[0]-hip[0],kn[1]-hip[1]),.62)
        c.shape(lambda d:poly(d,[(a[0]-5.4,a[1]),(a[0]+5.4,a[1]),(b[0]+4.4,b[1]),(b[0]-4.4,b[1])]),STEEL,blur=1.6)
        c.shape(lambda d:cap(d,(a[0]-5,a[1]+.6),(a[0]+5,a[1]+.6),1),GOLD,flat='#f0b830')
    # perna da frente por cima (desenhada antes) -> redesenha botas/joelho
    # ombros: ombreiras
    for sg,k in((-1,'B'),(1,'F')):
        sp=s['s'+k];c.shape(lambda d:Epoly(d,add(sp,u2,1.6),f2,u2,9,7.2),STEEL,blur=2.6)
        c.shape(lambda d:poly(d,[add(sp,u2,6),add(add(sp,f2,sg*3.5),u2,12),add(sp,f2,sg*-1.5+0)]),STEEL,blur=.8) if False else None
        sp_t=loc(sp,f2,u2,sg*2,7);sp_b=loc(sp,f2,u2,sg*5.5,13);c.shape(lambda d:poly(d,[loc(sp,f2,u2,sg*-2,6),loc(sp,f2,u2,sg*4,6.5),sp_b]),STEEL,blur=.8)
        for a in(-3,3):c.shape(lambda d:Epoly(d,loc(sp,f2,u2,a,1.6),(1,0),(0,-1),1,1),STEEL,flat='#e6f4ff')
    # gorjal + pescoco
    nt=s['Nt']
    for q in(.2,.5,.8):
        pt=add(N,(nt[0]-N[0],nt[1]-N[1]),q);c.shape(lambda d:Epoly(d,pt,f2,u2,2.7,1.5),BONE2,blur=.7)
    c.shape(lambda d:Epoly(d,loc(N,f2,u2,0,-1),f2,u2,6.5,2.6),STEEL,blur=1.4)
    # cabeca
    jw=p['jaw']*D2R
    c.shape(lambda d:Epoly(d,H,fh,uh,10.8,11.4),BONE2,blur=3.2)
    # bochechas
    for sg in(-1,1):c.shape(lambda d:Epoly(d,loc(H,fh,uh,sg*7,-4),fh,uh,2.6,2.2),BONE2,blur=.8)
    # mandibula
    jc=loc(H,fh,uh,0,-9+p['jaw']*-.45)
    c.shape(lambda d:poly(d,[loc(H,fh,uh,-7,-5),loc(H,fh,uh,7,-5),loc(jc,fh,uh,6,-2.2),loc(jc,fh,uh,-6,-2.2)]),BONE2,blur=1.2)
    for x in range(-5,6,2):c.shape(lambda d:cap(d,loc(H,fh,uh,x,-5.8),loc(H,fh,uh,x,-9.3-p['jaw']*.45),.9),BONE2,flat='#2a1a14')
    c.shape(lambda d:cap(d,loc(H,fh,uh,-6,-6),loc(H,fh,uh,6,-6),.9),BONE2,flat='#2a1a14')
    for ex in(-4.6,4.6):
        c.shape(lambda d:Epoly(d,loc(H,fh,uh,ex,-.5),fh,uh,3.3,3.7),BONE2,flat='#0c060a')
        c.shape(lambda d:Epoly(d,loc(H,fh,uh,ex,-.7),(1,0),(0,-1),1.4+.7*p['pulse'],1.6+.7*p['pulse']),BONE2,flat='#ff9a30' if p['pulse']<.5 else '#ffe08a')
    c.shape(lambda d:poly(d,[loc(H,fh,uh,-1.3,-3),loc(H,fh,uh,1.3,-3),loc(H,fh,uh,.9,-6.2),loc(H,fh,uh,-.9,-6.2)]),BONE2,flat='#0c060a')
    # elmo
    c.shape(lambda d:(Epoly(d,loc(H,fh,uh,0,6.6),fh,uh,12.6,8.6),poly(d,[loc(H,fh,uh,-12.5,6.5),loc(H,fh,uh,12.5,6.5),loc(H,fh,uh,11.5,3),loc(H,fh,uh,-11.5,3)])),STEEL,blur=2.8)
    c.shape(lambda d:poly(d,[loc(H,fh,uh,-1.8,7),loc(H,fh,uh,1.8,7),loc(H,fh,uh,1.2,-3),loc(H,fh,uh,-1.2,-3)]),STEEL,blur=.8)
    c.shape(lambda d:cap(d,loc(H,fh,uh,-12,3.5),loc(H,fh,uh,12,3.5),1.2),GOLD,flat='#f0b830')
    for a in(-8,-3,3,8):c.shape(lambda d:Epoly(d,loc(H,fh,uh,a,5.2),(1,0),(0,-1),.9,.9),STEEL,flat='#e6f4ff')
    # pluma (cadeia)
    c.shape(lambda d:strip(d,ch['plume'],6.5,2.5),'#7a1820 #b02830 #e04a40 #ff8a70',blur=1.6)
    c.shape(lambda d:poly(d,[loc(H,fh,uh,-2.5,13.5),loc(H,fh,uh,2.5,13.5),loc(H,fh,uh,2,10),loc(H,fh,uh,-2,10)]),GOLD,blur=.7)
    # braco da frente + espada
    sF,eF,wF=s['sF'],s['elF'],s['wrF']
    limb(c,sF,eF,7.4,BONE2);c.shape(lambda d:Epoly(d,eF,(1,0),(0,-1),4,4),BONE2,blur=1.4);limb(c,eF,wF,6.4,BONE2)
    c.shape(lambda d:cap(d,add(eF,(wF[0]-eF[0],wF[1]-eF[1]),.35),wF,7.6),STEEL,blur=1.4)
    c.shape(lambda d:Epoly(d,add(eF,(wF[0]-eF[0],wF[1]-eF[1]),.1),(1,0),(0,-1),4.8,4.4),STEEL,blur=1.4)
    hn=s['handF'];wr=p['wa']*D2R;tip=add(hn,F(wr),30)
    if p.get('_prev') and math.hypot(tip[0]-p['_prev'][0][0],tip[1]-p['_prev'][0][1])>10:
        pv,pm_=p['_prev'];pv=(pv[0]+(tip[0]-pv[0])*.5,pv[1]+(tip[1]-pv[1])*.5);cm=add(hn,F(wr),12);pm_=(pm_[0]+(cm[0]-pm_[0])*.5,pm_[1]+(cm[1]-pm_[1])*.5);c.shape(lambda d:poly(d,[cm,tip,pv,pm_]),STEEL,flat='#9cb8dc')
    c.shape(lambda d:blade(d,hn,p['wa'],30,5.2),STEEL,blur=.7)
    c.shape(lambda d:cap(d,add(hn,F(wr),4),add(hn,F(wr),27),.9),STEEL,flat='#f4fbff')
    px_=(-math.sin(wr),math.cos(wr));g0=add(hn,px_,6);g1=add(hn,px_,-6)
    c.shape(lambda d:cap(d,g0,g1,2.2),GOLD,blur=.8)
    pm=add(hn,F(wr),-6);c.shape(lambda d:Epoly(d,pm,(1,0),(0,-1),2.8,2.8),GOLD,blur=.8)
    c.shape(lambda d:cap(d,add(hn,F(wr),-4),add(hn,F(wr),1),3),WOOD,blur=.8)
    hand(c,wF,s['haF'],BONE2)
    return c
def anim_guard2():
    sin=math.sin;T=6.2832
    idle=lambda t:pose(dy=.9*sin(t*T),lean=1.2*sin(t*T+.6),torso=1*sin(t*T+.9),chest=1.3*sin(t*T+1.2),neck=1.5*sin(t*T-.3),head=1.4*sin(t*T-.7),shF=.8*sin(t*T+1),shB=.8*sin(t*T+1),
        handF=(12,14+1.2*sin(t*T+1)),handB=(-12,14+.8*sin(t*T)),wrF=3*sin(t*T+1.3),wa=-78+3*sin(t*T+1),sa=2*sin(t*T),pulse=.5+.5*sin(t*12.566),ftF=2*sin(t*T)*0)
    B=pose()
    atk=[(0,B),(.14,pose(dy=2.5,lean=-5,torso=-3,chest=-4,head=-3,handF=(4,-4),wa=-120,wrF=-12,footF=(14,0),footB=(-14,0),sa=-4,shF=-1)),
         (.34,pose(dy=1.5,lean=-11,torso=-6,chest=-8,neck=-3,head=-3,handF=(-9,-24),wa=-152,wrF=-24,footF=(14,0),footB=(-15,0),ftF=-6,handB=(-9,10),sa=-8,jaw=2,pulse=1,shF=-3,_e='out')),
         (.46,pose(dy=2,lean=3,dx=3,torso=3,chest=4,handF=(10,-14),wa=-60,wrF=10,footF=(18,0),handB=(-10,12),shF=2,_e='in')),
         (.56,pose(dx=8,dy=3,lean=15,torso=5,chest=8,neck=2,head=2,handF=(28,-1),wa=-4,wrF=26,footF=(21,0),footB=(-4,0),ftB=22,handB=(-13,16),sa=10,pulse=1,shF=3,_e='in')),
         (.70,pose(dx=10,dy=3.5,lean=17,torso=5,chest=7,neck=2,head=3,handF=(33,7),wa=14,wrF=14,footF=(22,0),footB=(-3,0),ftB=30,handB=(-14,17),sa=14,pulse=1,shF=3,_e='out')),
         (.86,pose(dx=6,dy=2,lean=9,torso=2,chest=3,handF=(25,11),wa=22,wrF=4,footF=(18,0),footB=(-8,0),ftB=12,sa=6)),(1,B)]
    h0=pose(dx=-5,dy=1,lean=-15,torso=-6,chest=-9,neck=-6,head=-10,handF=(5,2),wa=-100,wrF=-18,handB=(-17,2),sa=-15,footF=(9,0),footB=(-17,0),ftF=-10,jaw=4,flash=1,pulse=1,shF=-3,shB=-3)
    hurt=[(0,h0),(.5,pose(dx=-3,lean=-9,torso=-4,chest=-5,neck=-3,head=-6,handF=(8,8),wa=-90,handB=(-15,8),sa=-8,footF=(10,0),footB=(-15,0),jaw=3)),(1,pose(dx=-1,lean=-3,head=-3,chest=-2,handF=(11,12),wa=-80))]
    death=[(0,h0),(.18,pose(dx=-8,dy=3,lean=-12,torso=-4,chest=-6,neck=-4,head=-8,handF=(4,8),wa=-60,wrF=-10,handB=(-18,6),sa=-20,footF=(6,0),footB=(-20,0),ftF=-12,jaw=5)),
           (.34,pose(dx=-8,dy=11,lean=-8,torso=-2,chest=-4,head=4,handF=(2,16),wa=-30,handB=(-14,16),sa=-10,footF=(8,-1),footB=(-22,0),jaw=6)),
           (.5,pose(dx=-9,dy=12,post=2,grot=-22,lean=-5,chest=-4,handF=(-4,20),wa=10,handB=(-10,16),sa=-30,footF=(8,-3),footB=(-24,0),jaw=6,pulse=0)),
           (.68,pose(dx=-10,dy=10,post=7,grot=-52,lean=-2,handF=(-2,22),wa=60,handB=(-8,14),footF=(4,-8),footB=(-20,-2),jaw=6,pulse=0)),
           (.84,pose(dx=-10,dy=6,post=13,grot=-80,handF=(-2,24),wa=100,handB=(-6,12),footF=(2,-10),footB=(-18,-4),jaw=6,pulse=0)),
           (.93,pose(dx=-10,dy=3,post=15,grot=-87,handF=(0,24),wa=80,handB=(-6,12),footF=(2,-10),footB=(-18,-4),jaw=6,pulse=0)),
           (1,pose(dx=-10,dy=4,post=14,grot=-90,handF=(0,24),wa=70,handB=(-6,12),footF=(2,-10),footB=(-18,-4),jaw=6,pulse=0))]
    return idle,atk,hurt,death
GUARD_CH=[('plume',4,4.6,80,5,(-.85,-.5),lambda s:add(s['H'],s['uh'],13)),('cape',5,6.5,45,5,(-.3,1),lambda s:add(add(s['N'],s['f2'],-7),s['u2'],-2))]
def run_chains(poses,dt,loops=1,spec=GUARD_CH):
    cs={n:Chain(k_,sg,k=kk,c=cc,g=g) for n,k_,sg,kk,cc,g,_ in spec}
    seqs=list(poses)*loops if loops>1 else list(poses);first=solve(poses[0])
    for _ in range(8):
        for n,k_,sg,kk,cc,g,an in spec:cs[n].step(an(first),dt)
    res=[]
    for i,p in enumerate(seqs):
        s=solve(p);r={n:cs[n].step(an(s),dt) for n,k_,sg,kk,cc,g,an in spec}
        if i>=len(seqs)-len(poses):res.append(r)
    return res
def build(name,draw,anims,out,nidle=8,natk=8,nhurt=3,ndeath=8,spec=GUARD_CH):
    idle,atk,hurt,death=anims;frames=[];meta={}
    def add_(lbl,ps,dt,loops=1):
        chs=run_chains(ps,dt,loops,spec);meta[lbl]=list(range(len(frames),len(frames)+len(ps)));prev=None
        for p,chn in zip(ps,chs):
            p=dict(p);p['_ch']=chn;s=solve(p)
            if lbl=='attack':
                p['_prev']=prev;prev=(add(s['handF'],F(p['wa']*D2R),30),add(s['handF'],F(p['wa']*D2R),12))
            im=finish(draw(p))
            if p.get('flash'):im=flash(im,.55*p['flash'])
            if lbl=='death':
                bb=im.getbbox()
                if bb and bb[3]>GY+2:
                    sh=bb[3]-(GY+2);im=im.transform(im.size,Image.AFFINE,(1,0,0,0,1,sh),resample=Image.NEAREST)
            frames.append(im)
    add_('idle',[idle(i/nidle) for i in range(nidle)],1/8,loops=3)
    add_('attack',[sample(atk,i/(natk-1)) for i in range(natk)],.07)
    add_('hurt',[sample(hurt,i/(nhurt-1)) for i in range(nhurt)],.07)
    add_('death',[sample(death,i/(ndeath-1)) for i in range(ndeath)],.1)
    cols=8;rows=(len(frames)+cols-1)//cols;A=Image.new('RGBA',(CW*cols,CH*rows),(0,0,0,0))
    for i,f in enumerate(frames):A.paste(f,((i%cols)*CW,(i//cols)*CH),f)
    A.save(f'{out}/{name}_px_atlas.png')
    json.dump({'w':CW,'h':CH,'ax':GX,'ay':GY,'cols':cols,'anims':meta,'fps':{'idle':8,'death':10},'imp':.56},open(f'{out}/{name}_px_atlas.json','w'))
    return frames,meta
def sheet(fr,meta,path):
    sel=meta['idle'][::2]+meta['attack']+meta['hurt']+meta['death'];W=8
    Sh=Image.new('RGB',(CW*W,CH*((len(sel)+W-1)//W)),(58,92,120))
    for i,k in enumerate(sel):Sh.paste(fr[k],((i%W)*CW,(i//W)*CH),fr[k])
    Sh.save(path)

CULT_CH=[('hemL',3,9,40,5,(-.15,1),lambda s:add(s['P'],s['f0'],-9)),('hemR',3,9,40,5,(.15,1),lambda s:add(s['P'],s['f0'],9)),('sash',3,6,50,5,(-.3,1),lambda s:add(s['P'],s['f0'],-2)),('hood',3,4,60,5,(-.9,.6),lambda s:add(s['H'],s['uh'],12))]
def draw_cult(p):
    s=solve(p);c=Canvas(CW,CH);P=s['P'];N=s['N'];W=s['W'];H=s['H'];f0,u0,f2,u2,fh,uh=s['f0'],s['u0'],s['f2'],s['u2'],s['fh'],s['uh'];ch=p['_ch']
    for k in('B','F'):
        foot(c,s['ank'+k],s['toe'+k],s['heel'+k],CLOTH)
    # manto: abas esquerda/direita + corpo
    gl=P[1]+0
    hl=ch['hemL'];hr=ch['hemR']
    # barra no chao (seguindo cadeias, ancorada ao solo)
    flo=GY-p['post']
    bot=lambda x,dx:(x+dx,flo-1+0)
    def robe(d):
        L=[loc(N,f2,u2,-13,-4)]+[ (hl[i][0]-4,hl[i][1]) for i in range(0,len(hl))]
        R=[loc(N,f2,u2,13,-4)]+[ (hr[i][0]+4,hr[i][1]) for i in range(0,len(hr))]
        bl=(L[-1][0]-6,min(flo,L[-1][1]+6));br=(R[-1][0]+7,min(flo,R[-1][1]+6))
        poly(d,L+[bl,br]+R[::-1])
    c.shape(robe,ROBE,blur=4.2)
    c.shape(lambda d:poly(d,[loc(P,f0,u0,-8,6),loc(P,f0,u0,8,6),(hr[-1][0]-2,hr[-1][1]),(hl[-1][0]+2,hl[-1][1])]),ROBE,blur=3,light=(-.2,-.8))
    # dobras
    for i,a in enumerate((-9,-3,3,9)):
        c.shape(lambda d:cap(d,loc(P,f0,u0,a*.5,2),((hl[-1][0]*(1-(a+9)/18)+hr[-1][0]*((a+9)/18)),(hl[-1][1]*(1-(a+9)/18)+hr[-1][1]*((a+9)/18))),.9),ROBE,flat='#1a0a38')
    # barra dourada
    def band(d):
        a=[(hl[-1][0]-6,hl[-1][1]-6),(hr[-1][0]+7,hr[-1][1]-6),(hr[-1][0]+7.5,hr[-1][1]-3),(hl[-1][0]-6.5,hl[-1][1]-3)];poly(d,a)
    c.shape(band,GOLD,blur=.9)
    for t in range(6):
        x=hl[-1][0]-4+t*(hr[-1][0]-hl[-1][0]+9)/5;y=(hl[-1][1]+hr[-1][1])/2-4.5;c.shape(lambda d:Epoly(d,(x,y),(1,0),(0,-1),1.1,1.1),GOLD,flat='#fff0a0')
    # faixa
    c.shape(lambda d:strip(d,ch['sash'],5,3),'#7a1020 #c02840 #ff5a6a #ffd0d0',blur=1.2)
    c.shape(lambda d:poly(d,[loc(P,f0,u0,-9,1),loc(P,f0,u0,9,1),loc(P,f0,u0,8,6),loc(P,f0,u0,-8,6)]),GOLD,blur=.9)
    c.shape(lambda d:Epoly(d,loc(P,f0,u0,0,3.5),f0,u0,2.8,2.6),VOID,flat='#c02840')
    # braco de tras
    sB,eB,wB=s['sB'],s['elB'],s['wrB']
    limb(c,sB,eB,7.8,ROBE);c.shape(lambda d:Epoly(d,eB,(1,0),(0,-1),4.2,4.2),ROBE,blur=1.4);limb(c,eB,wB,7,ROBE)
    c.shape(lambda d:Epoly(d,add(eB,(wB[0]-eB[0],wB[1]-eB[1]),.7),(1,0),(0,-1),5.2,4.6),ROBE,blur=1.5)
    hand(c,wB,s['haB'],SKIN)
    # peito
    ct=((W[0]+N[0])/2,(W[1]+N[1])/2)
    c.shape(lambda d:Epoly(d,ct,f2,u2,14.5,13),ROBE,blur=3.6)
    c.shape(lambda d:cap(d,loc(ct,f2,u2,0,-11),loc(ct,f2,u2,0,9),1.2),ROBE,flat='#1a0a38')
    c.shape(lambda d:poly(d,[loc(ct,f2,u2,-3,10),loc(ct,f2,u2,3,10),loc(ct,f2,u2,2,-9),loc(ct,f2,u2,-2,-9)]),GOLD,blur=.7)
    c.shape(lambda d:Epoly(d,loc(ct,f2,u2,0,-4),f2,u2,2.8,2.6),VOID,flat='#c02840')
    # ombros
    for sg,k in((-1,'B'),(1,'F')):c.shape(lambda d:Epoly(d,add(s['s'+k],u2,1.2),f2,u2,8.2,6.4),ROBE,blur=2.6)
    # gola + capuz
    c.shape(lambda d:Epoly(d,loc(N,f2,u2,0,-1),f2,u2,9,4),ROBE,blur=2)
    hd=ch['hood']
    c.shape(lambda d:(Epoly(d,H,fh,uh,13.4,14.4),poly(d,[loc(H,fh,uh,-13,6),loc(H,fh,uh,0,22),loc(H,fh,uh,13,6)])),ROBE,blur=3.8)
    c.shape(lambda d:strip(d,hd,8,2.5),ROBE,blur=1.6)
    c.shape(lambda d:Epoly(d,loc(H,fh,uh,0,-.5),fh,uh,8.8,10),VOID,blur=3,light=(0,0))
    e=2.1+1.3*p['pulse']
    for x in(-3.8,3.8):
        c.shape(lambda d:Epoly(d,loc(H,fh,uh,x,.5),fh,uh,e,1.8),VOID,flat='#ff3a4a');c.shape(lambda d:Epoly(d,loc(H,fh,uh,x-.4,.8),(1,0),(0,-1),.9,.8),VOID,flat='#ffe0e0')
    c.shape(lambda d:cap(d,loc(H,fh,uh,-3,-8),loc(H,fh,uh,3,-8),1.2+p['jaw']*.18),VOID,flat='#c8a0ff')
    c.shape(lambda d:cap(d,loc(H,fh,uh,0,12),loc(H,fh,uh,0,13),1),GOLD,flat='#f0b830')
    c.shape(lambda d:cap(d,loc(H,fh,uh,-10,5),loc(H,fh,uh,10,5),1),ROBE,flat='#c8a0ff') if False else None
    # braco da frente + adaga
    sF,eF,wF=s['sF'],s['elF'],s['wrF']
    limb(c,sF,eF,7.8,ROBE);c.shape(lambda d:Epoly(d,eF,(1,0),(0,-1),4.2,4.2),ROBE,blur=1.4);limb(c,eF,wF,7,ROBE)
    c.shape(lambda d:Epoly(d,add(eF,(wF[0]-eF[0],wF[1]-eF[1]),.7),(1,0),(0,-1),5.2,4.6),ROBE,blur=1.5)
    hn=s['handF'];wr=p['wa']*D2R
    c.shape(lambda d:blade(d,hn,p['wa'],21,4.2),STEEL,blur=.6);c.shape(lambda d:cap(d,add(hn,F(wr),3),add(hn,F(wr),18),.8),STEEL,flat='#f4fbff')
    px_=(-math.sin(wr),math.cos(wr));c.shape(lambda d:cap(d,add(hn,px_,4.6),add(hn,px_,-4.6),2),GOLD,blur=.8)
    c.shape(lambda d:Epoly(d,add(hn,F(wr),-5),(1,0),(0,-1),2.6,2.6),VOID,flat='#ff3a4a')
    hand(c,wF,s['haF'],SKIN)
    if p['pulse']>.15:
        hb=s['handB'];r=3+6*p['pulse'];o=(hb[0]+5,hb[1]-4)
        c.shape(lambda d:Epoly(d,o,(1,0),(0,-1),r*1.5,r*1.5),VOID,flat='#7a40d0');c.shape(lambda d:Epoly(d,o,(1,0),(0,-1),r,r),VOID,flat='#e8c0ff');c.shape(lambda d:Epoly(d,o,(1,0),(0,-1),r*.55,r*.55),VOID,flat='#ffffff')
    return c
def anim_cult2():
    sin=math.sin;T=6.2832
    idle=lambda t:pose(footB=(-10,0),footF=(10,0),dy=1.3*sin(t*T),lean=1.5*sin(t*T+.7),torso=1.2*sin(t*T+1),chest=1.6*sin(t*T+1.3),neck=1.8*sin(t*T-.2),head=1.8*sin(t*T-.7),shF=.9*sin(t*T+1),shB=.9*sin(t*T+1),handF=(12,14+1.6*sin(t*T+1)),handB=(-12,14+1.2*sin(t*T)),wrF=4*sin(t*T+1.3),wa=-64+4*sin(t*T+.8),pulse=.35+.35*sin(t*12.566))
    B=pose(footB=(-10,0),footF=(10,0),wa=-64)
    atk=[(0,B),(.16,pose(footB=(-10,0),footF=(10,0),dy=2,lean=-6,torso=-3,chest=-4,head=-4,handF=(2,0),handB=(-10,4),wa=-110,wrF=-14,pulse=.3)),
         (.38,pose(footB=(-11,0),footF=(10,0),dy=1,lean=-12,torso=-4,chest=-8,neck=-3,head=-5,handF=(-6,-20),handB=(2,-12),wa=-150,wrF=-26,pulse=.7,_e='out')),
         (.52,pose(footB=(-11,0),footF=(11,0),dx=3,dy=2,lean=2,torso=3,chest=5,handF=(12,-10),handB=(14,-6),wa=-70,wrF=10,pulse=1,_e='in')),
         (.6,pose(footB=(-8,0),footF=(14,0),ftB=20,dx=7,dy=2.5,lean=15,torso=4,chest=7,neck=2,head=3,handF=(26,2),handB=(30,-8),wa=-6,wrF=24,pulse=1,_e='in')),
         (.74,pose(footB=(-6,0),footF=(15,0),ftB=28,dx=9,dy=3,lean=17,torso=4,chest=6,neck=2,head=4,handF=(29,8),handB=(33,-6),wa=12,wrF=12,pulse=1,_e='out')),
         (.88,pose(footB=(-8,0),footF=(12,0),ftB=10,dx=5,dy=2,lean=8,torso=2,chest=3,handF=(22,10),handB=(18,4),wa=-20,pulse=.4)),(1,B)]
    h0=pose(footB=(-12,0),footF=(8,0),ftF=-8,dx=-5,dy=1,lean=-16,torso=-7,chest=-9,neck=-6,head=-10,handF=(4,2),handB=(-16,2),wa=-100,wrF=-18,flash=1,pulse=0,shF=-3,shB=-3)
    hurt=[(0,h0),(.5,pose(footB=(-11,0),footF=(9,0),dx=-3,lean=-9,torso=-4,chest=-5,neck=-3,head=-6,handF=(8,8),handB=(-15,8),wa=-90)),(1,pose(footB=(-10,0),footF=(10,0),dx=-1,lean=-3,head=-3,chest=-2,wa=-70))]
    death=[(0,h0),(.2,pose(footB=(-14,0),footF=(6,0),dx=-8,dy=3,lean=-14,torso=-4,chest=-6,neck=-4,head=-8,handF=(2,8),wa=-50,handB=(-18,8))),
           (.4,pose(footB=(-16,0),footF=(6,0),dx=-9,dy=12,lean=-8,chest=-4,head=4,handF=(2,16),handB=(-14,18),wa=-20)),
           (.58,pose(footB=(-18,0),footF=(6,0),dx=-9,dy=12,post=2,grot=-30,handF=(-2,20),handB=(-10,18),wa=20)),
           (.75,pose(footB=(-18,0),footF=(2,-6),dx=-10,dy=8,post=8,grot=-62,handF=(0,22),handB=(-8,14),wa=70)),
           (.9,pose(footB=(-18,-2),footF=(2,-8),dx=-10,dy=4,post=14,grot=-86,handF=(0,24),handB=(-6,12),wa=90)),
           (1,pose(footB=(-18,-2),footF=(2,-8),dx=-10,dy=4,post=14,grot=-90,handF=(0,24),handB=(-6,12),wa=80))]
    return idle,atk,hurt,death
if __name__=='__main__':
    import os;out=sys.argv[1];os.makedirs(out,exist_ok=True)
    for n,d,a,sp in(('guardac',draw_guard,anim_guard2(),GUARD_CH),('cult',draw_cult,anim_cult2(),CULT_CH)):
        fr,meta=build(n,d,a,out,spec=sp);sheet(fr,meta,out+f'/{n}2_sheet.png')
