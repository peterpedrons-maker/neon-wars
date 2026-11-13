import sys,math,json
from PIL import Image
from hq import Canvas,finish,S
from rig2 import *
from build_anim import cap,Epoly,poly,blade,GOLD,ROBE,VOID,SKIN,STEEL,CLOTH
from build_anim2 import strip,foot,hand,limb,loc
CW,CH=180,124
CH3=[('hemL',3,9,40,5,(-.15,1),lambda s:add(s['P'],s['f0'],-9)),('hemR',3,9,40,5,(.15,1),lambda s:add(s['P'],s['f0'],9)),
     ('sash',3,6,50,5,(-.3,1),lambda s:add(s['P'],s['f0'],-2)),('hood',3,4,55,4.5,(-.9,.6),lambda s:add(s['H'],s['uh'],12)),
     ('slvF',2,5,70,6,(.1,1),lambda s:s['wrF']),('slvB',2,5,70,6,(-.1,1),lambda s:s['wrB'])]
def draw(p):
    s=solve(p);c=Canvas(CW,CH);P=s['P'];N=s['N'];W=s['W'];H=s['H'];f0,u0,f2,u2,fh,uh=s['f0'],s['u0'],s['f2'],s['u2'],s['fh'],s['uh'];ch=p['_ch']
    for k in('B','F'):foot(c,s['ank'+k],s['toe'+k],s['heel'+k],CLOTH)
    hl=ch['hemL'];hr=ch['hemR'];flo=GY-p['post']
    def robe(d):
        L=[loc(N,f2,u2,-13,-4)]+[(hl[i][0]-4,hl[i][1]) for i in range(len(hl))]
        R=[loc(N,f2,u2,13,-4)]+[(hr[i][0]+4,hr[i][1]) for i in range(len(hr))]
        poly(d,L+[(L[-1][0]-6,min(flo+1,L[-1][1]+6)),(R[-1][0]+7,min(flo+1,R[-1][1]+6))]+R[::-1])
    c.shape(robe,ROBE,blur=4.2)
    c.shape(lambda d:poly(d,[loc(P,f0,u0,-8,6),loc(P,f0,u0,8,6),(hr[-1][0]-2,hr[-1][1]),(hl[-1][0]+2,hl[-1][1])]),ROBE,blur=3,light=(-.2,-.8))
    for a in(-9,-3,3,9):
        q=(a+9)/18;c.shape(lambda d:cap(d,loc(P,f0,u0,a*.5,2),(hl[-1][0]*(1-q)+hr[-1][0]*q,hl[-1][1]*(1-q)+hr[-1][1]*q),.9),ROBE,flat='#1a0a38')
    c.shape(lambda d:poly(d,[(hl[-1][0]-6,hl[-1][1]-6),(hr[-1][0]+7,hr[-1][1]-6),(hr[-1][0]+7.5,hr[-1][1]-3),(hl[-1][0]-6.5,hl[-1][1]-3)]),GOLD,blur=.9)
    for t in range(6):
        x=hl[-1][0]-4+t*(hr[-1][0]-hl[-1][0]+9)/5;y=(hl[-1][1]+hr[-1][1])/2-4.5;c.shape(lambda d:Epoly(d,(x,y),(1,0),(0,-1),1.1,1.1),GOLD,flat='#fff0a0')
    c.shape(lambda d:strip(d,ch['sash'],5,3),'#7a1020 #c02840 #ff5a6a #ffd0d0',blur=1.2)
    c.shape(lambda d:poly(d,[loc(P,f0,u0,-9,1),loc(P,f0,u0,9,1),loc(P,f0,u0,8,6),loc(P,f0,u0,-8,6)]),GOLD,blur=.9)
    c.shape(lambda d:Epoly(d,loc(P,f0,u0,0,3.5),f0,u0,2.8,2.6),VOID,flat='#c02840')
    def arm(k,hold):
        sh,el,wr=s['s'+k],s['el'+k],s['wr'+k];sl=ch['slv'+k]
        limb(c,sh,el,7.8,ROBE);c.shape(lambda d:Epoly(d,el,(1,0),(0,-1),4.2,4.2),ROBE,blur=1.4);limb(c,el,wr,7,ROBE)
        # manga larga que pende e acompanha (secundaria)
        c.shape(lambda d:strip(d,[add(el,(wr[0]-el[0],wr[1]-el[1]),.55),wr]+sl[1:],8.5,6),ROBE,blur=2)
        c.shape(lambda d:cap(d,add(wr,(0,0),0),add(wr,(0,0),0),1),GOLD,flat='#f0b830')
        hand(c,wr,s['ha'+k],SKIN)
    arm('B',0)
    ct=((W[0]+N[0])/2,(W[1]+N[1])/2)
    c.shape(lambda d:Epoly(d,ct,f2,u2,14.5,13),ROBE,blur=3.6)
    c.shape(lambda d:cap(d,loc(ct,f2,u2,0,-11),loc(ct,f2,u2,0,9),1.2),ROBE,flat='#1a0a38')
    c.shape(lambda d:poly(d,[loc(ct,f2,u2,-3,10),loc(ct,f2,u2,3,10),loc(ct,f2,u2,2,-9),loc(ct,f2,u2,-2,-9)]),GOLD,blur=.7)
    c.shape(lambda d:Epoly(d,loc(ct,f2,u2,0,-4),f2,u2,2.8,2.6),VOID,flat='#c02840')
    for k in('B','F'):c.shape(lambda d:Epoly(d,add(s['s'+k],u2,1.2),f2,u2,8.2,6.4),ROBE,blur=2.6)
    c.shape(lambda d:Epoly(d,loc(N,f2,u2,0,-1),f2,u2,9,4),ROBE,blur=2)
    hd=ch['hood']
    c.shape(lambda d:(Epoly(d,H,fh,uh,13.4,14.4),poly(d,[loc(H,fh,uh,-13,6),loc(H,fh,uh,0,22),loc(H,fh,uh,13,6)])),ROBE,blur=3.8)
    c.shape(lambda d:strip(d,hd,8,2.5),ROBE,blur=1.6)
    c.shape(lambda d:Epoly(d,loc(H,fh,uh,3,-.5),fh,uh,8.6,10),VOID,blur=3,light=(0,0))
    e=2.1+1.3*p['pulse'];ry=1.8*(1-.85*p['blink'])
    if p['pulse']>=0 and p.get('eyes',1):
        for x in(0,6.5):
            c.shape(lambda d:Epoly(d,loc(H,fh,uh,x,.5),fh,uh,e,max(.45,ry)),VOID,flat='#ff3a4a' if p['blink']<.9 else '#6a1a2a')
            if p['blink']<.6:c.shape(lambda d:Epoly(d,loc(H,fh,uh,x-.4,.8),(1,0),(0,-1),.9,.8),VOID,flat='#ffe0e0')
    c.shape(lambda d:cap(d,loc(H,fh,uh,-.5,-8),loc(H,fh,uh,6.5,-8),1.2+p['jaw']*.18),VOID,flat='#c8a0ff')
    c.shape(lambda d:cap(d,loc(H,fh,uh,0,12),loc(H,fh,uh,0,13),1),GOLD,flat='#f0b830')
    arm('F',1)
    hn=s['handF'];wr=p['wa']*D2R
    c.shape(lambda d:blade(d,hn,p['wa'],21,4.2),STEEL,blur=.6);c.shape(lambda d:cap(d,add(hn,F(wr),3),add(hn,F(wr),18),.8),STEEL,flat='#f4fbff')
    px_=(-math.sin(wr),math.cos(wr));c.shape(lambda d:cap(d,add(hn,px_,4.6),add(hn,px_,-4.6),2),GOLD,blur=.8)
    c.shape(lambda d:Epoly(d,add(hn,F(wr),-5),(1,0),(0,-1),2.6,2.6),VOID,flat='#ff3a4a')
    hand(c,s['wrF'],s['haF'],SKIN)
    if p['pulse']>.15:
        hb=s['handB'];r=3+6*p['pulse'];o=(hb[0]+5,hb[1]-4)
        c.shape(lambda d:Epoly(d,o,(1,0),(0,-1),r*1.5,r*1.5),VOID,flat='#7a40d0');c.shape(lambda d:Epoly(d,o,(1,0),(0,-1),r,r),VOID,flat='#e8c0ff');c.shape(lambda d:Epoly(d,o,(1,0),(0,-1),r*.55,r*.55),VOID,flat='#ffffff')
    return c
FB=(-10,0);FF=(10,0)
def P_(**k):
    d=dict(footB=FB,footF=FF,wa=-64);d.update(k);return pose(**d)
sin=math.sin;T=6.2832
def idle(i,n=12):
    t=i/n
    return P_(dx=-1.3*sin(T*t+.4),dy=.9*sin(T*t+.2)+.5*sin(2*T*t),lean=1.3*sin(T*t+.7),torso=1.4*sin(T*t+1.0),chest=2.0*sin(T*t+1.3),neck=1.6*sin(T*t-.1),head=2.4*sin(T*t-.8),
        shF=1.3*sin(T*t+1.1),shB=1.3*sin(T*t+1.1),footF=(10+.6*sin(T*t),0),footB=(-10-.6*sin(T*t),0),
        handF=(12,14+1.8*sin(T*t+1.2)),handB=(-12,14+1.4*sin(T*t+.3)),wrF=5*sin(T*t+1.5),wrB=3*sin(T*t+.8),wa=-64+5*sin(T*t+.9),
        pulse=.4+.35*sin(2*T*t+.5),blink=1 if i in(7,8) else (.5 if i in(6,9) else 0),sq=1-.012*sin(T*t+.2))
# ---- ATAQUE (12): tempos irregulares; contato no quadro 7 ----
ATK=[
 (0/11,P_()),
 (1/11,P_(sq=.95,dy=2.6,dx=-1,lean=-5,torso=-3,chest=-4,neck=3,head=3,handF=(3,3),handB=(-10,6),wa=-100,wrF=-14,shF=-2,shB=-2,pulse=.3,footB=(-11,0))),
 (2/11,P_(sq=.93,dy=3.4,dx=-2,lean=-9,torso=-5,chest=-8,neck=4,head=5,handF=(-1,-3),handB=(-6,2),wa=-128,wrF=-20,shF=-2,shB=-1,pulse=.45,footB=(-12,0),footF=(11,0),ftB=8)),
 (3/11,P_(sq=1.03,dy=1,dx=-2.5,lean=-12,torso=-6,chest=-9,neck=-2,head=-6,handF=(-8,-20),handB=(0,-12),wa=-155,wrF=-26,shF=-3,shB=-4,pulse=.75,footB=(-12,0),ftB=14)),
 (4/11,P_(sq=1.02,dy=.8,dx=-3,lean=-13,torso=-7,chest=-10,neck=-3,head=-7,handF=(-10,-24),handB=(3,-15),wa=-163,wrF=-30,shF=-4,shB=-5,pulse=.95,footB=(-12,0),ftB=16)),
 (5/11,P_(sq=1.02,dy=.9,dx=-3,lean=-13.5,torso=-7,chest=-10,neck=-3,head=-7,handF=(-9.5,-23),handB=(2,-14),wa=-160,wrF=-29,shF=-4,shB=-5,pulse=1,footB=(-12,0),ftB=15)),
 (6/11,P_(sq=1.06,dy=-1,dx=5,lean=7,torso=3,chest=5,neck=3,head=2,handF=(18,-12),handB=(18,-8),wa=-62,wrF=8,shF=2,shB=2,pulse=1,footF=(16,0),footB=(-8,0),ftB=24)),
 (7/11,P_(sq=.95,dy=3,dx=9,lean=17,torso=4,chest=7,neck=2,head=3,handF=(30,6),handB=(32,-6),wa=8,wrF=14,shF=4,shB=4,pulse=1,footF=(16,0),footB=(-5,0),ftB=30)),
 (8/11,P_(sq=.98,dy=2.2,dx=11,lean=20,torso=6,chest=8,neck=1,head=2,handF=(34,12),handB=(34,0),wa=26,wrF=10,shF=3,shB=3,pulse=.6,footF=(17,0),footB=(-4,0),ftB=32)),
 (9/11,P_(sq=1,dy=1.5,dx=8,lean=14,torso=3,chest=4,neck=-2,head=-4,handF=(26,12),handB=(22,6),wa=10,wrF=2,pulse=.35,footF=(15,0),footB=(-7,0),ftB=20)),
 (10/11,P_(sq=1.015,dy=.6,dx=2,lean=-2,torso=-1,chest=-1.5,neck=-1,head=-2,handF=(15,12),handB=(-8,10),wa=-58,wrF=-3,pulse=.3,footF=(11,0),footB=(-10,0))),
 (1,P_())]
HURT=[
 (0,P_(sq=.92,dy=3,dx=-4,lean=-16,torso=-7,chest=-9,neck=-8,head=-12,handF=(5,0),handB=(-17,0),wa=-102,wrF=-18,shF=-4,shB=-4,blink=1,footF=(9,0),footB=(-14,0))),
 (.2,P_(sq=1.04,dy=-.5,dx=-7,lean=-20,torso=-8,chest=-11,neck=-6,head=-10,handF=(1,-2),handB=(-20,-2),wa=-112,wrF=-22,shF=-3,shB=-3,blink=.8,footF=(8,0),footB=(-18,0),ftF=-8)),
 (.4,P_(sq=.98,dy=1.2,dx=-5,lean=-12,torso=-5,chest=-5,neck=-3,head=-3,handF=(8,8),handB=(-15,8),wa=-90,wrF=-8,blink=.3,footF=(9,0),footB=(-16,0))),
 (.6,P_(dy=.5,dx=-2,lean=-4,torso=-2,chest=-2,neck=-1,head=-5,handF=(11,12),handB=(-12,12),wa=-72)),
 (.8,P_(sq=1.01,dx=-.5,lean=-1,head=1,wa=-62)),
 (1,P_())]
DEATH=[
 (0,HURT[0][1]),
 (.09,HURT[1][1]),
 (.2,P_(sq=.88,dy=7,dx=-8,lean=-11,torso=-4,chest=-6,neck=-6,head=-9,handF=(2,12),handB=(-18,10),wa=-40,wrF=-12,footF=(7,0),footB=(-18,0),blink=.8)),
 (.31,P_(sq=.78,dy=13,dx=-9,lean=-8,torso=-2,chest=-4,neck=-4,head=-14,handF=(2,18),handB=(-14,20),wa=-18,wrF=8,footF=(7,-1),footB=(-20,0),blink=1)),
 (.42,P_(sq=.78,dy=13,dx=-10,post=1,grot=-18,lean=-6,chest=-5,neck=-6,head=-16,handF=(-2,20),handB=(-10,18),wa=12,footF=(7,-2),footB=(-20,-1),blink=1)),
 (.53,P_(sq=.86,dy=11,dx=-10,post=4,grot=-42,lean=-3,chest=-3,neck=-8,head=-12,handF=(-2,22),handB=(-8,16),wa=50,footF=(4,-5),footB=(-19,-3),blink=1)),
 (.62,P_(sq=.92,dy=8,dx=-10,post=9,grot=-68,lean=-2,neck=-6,head=-8,handF=(0,24),handB=(-8,14),wa=78,footF=(2,-8),footB=(-18,-4),blink=1)),
 (.7,P_(sq=.84,dy=5,dx=-10,post=13,grot=-88,handF=(2,24),handB=(-6,12),wa=95,footF=(2,-9),footB=(-18,-4),blink=1)),
 (.77,P_(sq=.97,dy=6,dx=-10,post=17,grot=-84,handF=(2,24),handB=(-6,12),wa=92,footF=(2,-9),footB=(-18,-4),blink=1)),
 (.84,P_(sq=.93,dy=4,dx=-10,post=14.5,grot=-89,handF=(2,25),handB=(-6,14),wa=85,footF=(2,-9),footB=(-18,-4),blink=1)),
 (.92,P_(sq=1,dy=4,dx=-10,post=14,grot=-90,handF=(3,26),handB=(-5,15),wa=78,footF=(2,-9),footB=(-18,-4),blink=1,pulse=0)),
 (1,P_(sq=1,dy=4,dx=-10,post=14,grot=-90,handF=(3,26),handB=(-5,15),wa=76,footF=(2,-9),footB=(-18,-4),blink=1,pulse=0))]
HOP=[
 (0,P_(sq=.9,dy=3.5,dx=-1,lean=-4,torso=-2,chest=-4,neck=2,head=3,handF=(6,8),handB=(-12,8),wa=-90,wrF=-8,shF=-2,shB=-2,footB=(-11,0),footF=(11,0),pulse=.3)),
 (.2,P_(sq=1.08,dy=-3,dx=1,lean=5,torso=3,chest=4,neck=-2,head=-3,handF=(14,0),handB=(-10,-2),wa=-50,wrF=10,shF=3,shB=3,footB=(-10,-2),footF=(10,0),ftB=30,ftF=18,pulse=.5)),
 (.4,P_(sq=1.05,dy=-9,dx=2,lean=6,torso=2,chest=3,neck=-3,head=-4,handF=(16,-4),handB=(-6,-6),wa=-40,wrF=14,shF=4,shB=4,footB=(-8,-9),footF=(9,-8),ftB=40,ftF=30,pulse=.6)),
 (.6,P_(sq=1.02,dy=-8,dx=3,lean=3,torso=1,chest=1,neck=-1,head=-2,handF=(12,2),handB=(-8,0),wa=-60,wrF=6,shF=2,shB=2,footB=(-9,-5),footF=(11,-2),ftB=20,ftF=8,pulse=.5)),
 (.78,P_(sq=.88,dy=4.5,dx=2,lean=-2,torso=-2,chest=-4,neck=3,head=4,handF=(8,10),handB=(-12,10),wa=-84,wrF=-10,shF=-3,shB=-3,footB=(-11,0),footF=(12,0),pulse=.35)),
 (.9,P_(sq=1.03,dy=-.5,dx=1,lean=1,torso=1,chest=1.5,neck=-1,head=-1,handF=(12,13),handB=(-12,13),wa=-66,wrF=2)),
 (1,P_())]
def build(out):
    anims={'idle':[idle(i) for i in range(12)]}
    for nm,keys,n in(('attack',ATK,12),('hurt',HURT,6),('death',DEATH,12),('hop',HOP,6)):
        anims[nm]=[sample_spline(keys,i/(n-1)) for i in range(n)]
    # preenche chaves faltantes com BASE
    for nm in anims:
        anims[nm]=[{**BASE,**p} for p in anims[nm]]
    dts={'idle':1/8,'attack':.06,'hurt':.06,'death':.08,'hop':.06};frames=[];meta={}
    for nm,ps in anims.items():
        loops=3 if nm=='idle' else 1
        # cadeias
        cs={n:Chain(k_,sg,k=kk,c=cc,g=g) for n,k_,sg,kk,cc,g,_ in CH3};first=solve(ps[0])
        seqs=ps*loops;res=[]
        for _ in range(8):
            for n,k_,sg,kk,cc,g,an in CH3:cs[n].step(an(first),dts[nm])
        for i,p in enumerate(seqs):
            s=solve(p);r={n:cs[n].step(an(s),dts[nm]) for n,k_,sg,kk,cc,g,an in CH3}
            if i>=len(seqs)-len(ps):res.append(r)
        meta[nm]=list(range(len(frames),len(frames)+len(ps)))
        for p,r in zip(ps,res):
            p=dict(p);p['_ch']=r;im=finish(draw(p))
            if nm=='death':
                bb=im.getbbox()
                if bb and bb[3]>GY+2:
                    sh=bb[3]-(GY+2);im=im.transform(im.size,Image.AFFINE,(1,0,0,0,1,sh),resample=Image.NEAREST)
            frames.append(im)
    cols=8;rows=(len(frames)+cols-1)//cols;A=Image.new('RGBA',(CW*cols,CH*rows),(0,0,0,0))
    for i,f in enumerate(frames):A.paste(f,((i%cols)*CW,(i//cols)*CH),f)
    A.save(f'{out}/cult_px_atlas.png')
    json.dump({'w':CW,'h':CH,'ax':GX,'ay':GY,'cols':cols,'anims':meta,'fps':{'idle':8,'death':12},'imp':7/11},open(f'{out}/cult_px_atlas.json','w'))
    return frames,meta
if __name__=='__main__':
    import os;out=sys.argv[1];os.makedirs(out,exist_ok=True)
    fr,meta=build(out)
    for nm,idx in meta.items():
        W_=6;Sh=Image.new('RGB',(CW*W_,CH*((len(idx)+W_-1)//W_)),(58,92,120))
        for i,k in enumerate(idx):Sh.paste(fr[k],((i%W_)*CW,(i//W_)*CH),fr[k])
        Sh.save(f'{out}/c3_{nm}.png')
