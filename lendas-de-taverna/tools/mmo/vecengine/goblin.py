"""Goblin ilustrado (vista lateral), montado em esqueleto com membros que dobram: cabeça, tronco, braços, pernas, botas, capacete e cutelo."""
import math
import numpy as np
from .render import Canvas,hexc,smooth,rot,SS
C=dict(
 skin=(hexc('#6fa84c'),hexc('#3f7a3c'),hexc('#a4d472'),hexc('#1c2c20')),
 skin2=(hexc('#5a9040'),hexc('#336a34'),hexc('#86b85c'),hexc('#1c2c20')),
 leat=(hexc('#8a5a32'),hexc('#52361f'),hexc('#c08a50'),hexc('#2a1a10')),
 metal=(hexc('#9aa2b8'),hexc('#545c78'),hexc('#e6ecf8'),hexc('#1c2030')),
 cloth=(hexc('#4c4470'),hexc('#2c2644'),hexc('#7a70a0'),hexc('#16122a')),
 bone=(hexc('#ece0b8'),hexc('#b8a47c'),hexc('#fff8dc'),hexc('#3a2e1c')),
 pink=(hexc('#e8908c'),hexc('#b8605e'),hexc('#ffc0bc'),hexc('#3a1c1c')),
 white=(hexc('#f8f8f0'),hexc('#c8c8c0'),hexc('#ffffff'),hexc('#2a2430')),
 yell=(hexc('#ffd840'),hexc('#e0a020'),hexc('#fff4a0'),hexc('#3a2a10')),
 dark=(hexc('#241c2c'),hexc('#241c2c'),hexc('#54486a'),hexc('#100c14')),
 red=(hexc('#c83c44'),hexc('#7c1c28'),hexc('#f08084'),hexc('#2a0c10')))
def P(cv,m,mat,**k):
    b,s,l,o=C[mat];cv.paint(m,b,s,l,o,**k)
class Goblin:
    def __init__(s,cell=256,scale=1.0):
        s.cell=cell;s.k=cell/256*scale;s.GY=int(cell*.92)
    def L(s,v):return v*s.k
    def draw(s,pose,view='side'):
        g=pose.get;k=s.k;cv=Canvas(s.cell,s.cell);F=lambda x:x*k
        cx=s.cell*.40
        # sombra suave no chão
        import cv2
        sm=np.zeros((cv.H,cv.W),np.float32);cv2.ellipse(sm,(int((cx+6*k)*SS),int((s.GY+4*k)*SS)),(int(44*k*SS),int(8*k*SS)),0,0,360,1,-1);sm=cv2.GaussianBlur(sm,(0,0),5*SS*k)*.55
        cv.rgb[:]=np.array([14,18,16],np.float32);cv.a[:]=sm
        crouch=g('crouch',0)*3*k;bob=g('bob',0)*3*k;lean=g('lean',0)
        TH,SH,UA,FA=46*k,44*k,34*k,32*k
        hip=(cx+g('sway',0)*3*k+lean*1.2*k,s.GY-88*k+8*k-bob+crouch*1.0)
        def seg(p,a,L):r=math.radians(a);return (p[0]+math.sin(r)*L,p[1]+math.cos(r)*L)
        def leg(far):
            a,kb=g('la' if far else 'ra',0),g('lk' if far else 'rk',0)
            H=(hip[0]+(5 if far else -5)*k,hip[1]);K=seg(H,a,TH);A=seg(K,a-kb,SH);return H,K,A
        def foot(A,a,far,cv):
            ang=-(g('la' if far else 'ra',0)-g('lk' if far else 'rk',0))*.35
            pts=[(-10,-14),(9,-14),(22,-4),(40,6),(38,16),(-12,16)]
            pl=smooth(rot(np.array(pts)*k,(A[0],A[1]),0),6) if False else np.array(pts)*k+np.array(A)
            m=cv.mask_poly(smooth(pl,8));P(cv,m,'leat' if not far else 'leat',hl=2.6,sh=3.4)
            sole=np.array([(-12,12),(38,12),(38,17),(-12,17)])*k+np.array(A);P(cv,cv.mask_poly(sole),'dark',hl=0,sh=0)
        def arm(us,fe,far):
            S=(hip[0]+(2+lean*.3)*k+8*k,hip[1]-62*k+0*k) if True else None
            E=seg(S,us,UA);Hd=seg(E,us+fe,FA);return S,E,Hd
        # --- perna longe
        H,K,A=leg(True);P(cv,cv.mask_capsule([H,K,A],[(12*k,9.5*k),(9.5*k,7*k)]),'cloth',hl=2.4,sh=4)
        foot(A,0,True,cv)
        # --- braço longe
        S,E,Hd=arm(g('ls',-8),g('le',-12),True)
        P(cv,cv.mask_capsule([S,E,Hd],[(9*k,7.5*k),(7.5*k,6.5*k)]),'skin2',hl=2,sh=3.2);P(cv,cv.mask_ell(Hd,8*k,7.5*k),'skin2',hl=2,sh=3)
        # --- tronco
        belly=cv.mask_ell((hip[0]+6*k+lean*.5*k,hip[1]-26*k),32*k,30*k);chest=cv.mask_ell((hip[0]+2*k+lean*.9*k,hip[1]-52*k),28*k,24*k)
        P(cv,belly|chest,'skin',hl=3.6,sh=6,ow=1.6)
        vest=np.array([(-20,-70),(16,-74),(30,-42),(24,-12),(-14,-8),(-26,-40)])*k+np.array([hip[0]+lean*.8*k,hip[1]])
        P(cv,cv.mask_poly(smooth(vest,8)),'leat',hl=3,sh=5)
        for dx in (-10,6):    # costuras / tiras do colete
            ln=np.array([(dx,-66),(dx+10,-14)])*k+np.array([hip[0]+lean*.8*k,hip[1]])
            P(cv,cv.mask_capsule([tuple(ln[0]),tuple(ln[1])],[(2.2*k,2.2*k)]),'cloth',hl=0,sh=0,ow=.6)
        # tanga (balança)
        sw=g('csway',0)*2.5*k
        cl=np.array([(-24,2),(30,2),(24+sw*.3,34),(8+sw*.6,28),(-4+sw,40),(-18+sw*.5,30)])*k+np.array([hip[0]+lean*.3*k,hip[1]])
        P(cv,cv.mask_poly(smooth(cl,6)),'cloth',hl=2.6,sh=4.4)
        belt=np.array([(-32,-10),(36,-10),(36,6),(-32,6)])*k+np.array([hip[0]+lean*.3*k,hip[1]])
        P(cv,cv.mask_poly(smooth(belt,5)),'leat',hl=2,sh=3.2);P(cv,cv.mask_ell((hip[0]-14*k+lean*.3*k,hip[1]-2*k),9*k,9*k),'bone',hl=2,sh=3);P(cv,cv.mask_ell((hip[0]-17*k+lean*.3*k,hip[1]-4*k),2*k,2.6*k),'dark',hl=0,sh=0,ow=0);P(cv,cv.mask_ell((hip[0]-11*k+lean*.3*k,hip[1]-4*k),2*k,2.6*k),'dark',hl=0,sh=0,ow=0)
        # --- perna perto + joelheira + bota
        H,K,A=leg(False);P(cv,cv.mask_capsule([H,K,A],[(13*k,10*k),(10*k,7.5*k)]),'cloth',hl=2.6,sh=4.2)
        P(cv,cv.mask_ell(K,10*k,10*k),'metal',hl=2.4,sh=3.4);foot(A,0,False,cv)
        # --- cabeça (acompanha o pescoço do tronco)
        nk=(hip[0]+4*k+lean*1.8*k+g('hx',0)*k,hip[1]-70*k+g('hy',0)*3*k);hs=1.0
        def HP(pts):return np.array(pts)*k+np.array(nk)
        # orelha (atrás)
        ear=HP([(-14,-34),(-34,-56),(-62,-78),(-48,-50),(-30,-28)]);P(cv,cv.mask_poly(smooth(ear,6)),'skin2',hl=2,sh=3.5);P(cv,cv.mask_poly(smooth(HP([(-20,-36),(-38,-54),(-52,-66),(-42,-48),(-28,-32)]),5)),'pink',hl=1.2,sh=2,ow=.7)
        skull=cv.mask_ell(tuple(HP([(6,-34)])[0]),32*k,28*k)
        snout=cv.mask_poly(smooth(HP([(14,-40),(40,-40),(58,-30),(54,-14),(34,-8),(10,-10)]),8))
        P(cv,skull|snout,'skin',hl=3.6,sh=6,ow=1.6)
        nose=cv.mask_ell(tuple(HP([(56,-30)])[0]),9*k,8*k);P(cv,nose,'skin',hl=2,sh=3,ow=1.2)
        P(cv,cv.mask_ell(tuple(HP([(60,-30)])[0]),2.6*k,2.2*k),'dark',hl=0,sh=0,ow=0)
        # mandíbula e presas
        op=g('open',0)*7*k
        jaw=cv.mask_poly(smooth(HP([(8,-10),(40,-10+op/k),(56,-6+op/k),(48,4+op/k),(20,8+op/k)]),6));P(cv,jaw,'skin2',hl=2,sh=3.5)
        if op>0:P(cv,cv.mask_poly(HP([(14,-8),(48,-8),(50,-8+op/k),(14,-8+op/k)])),'red',hl=0,sh=0,ow=0)
        for tx in (40,26):
            tu=HP([(tx,-8+op/k*1.0),(tx+4,-8+op/k),(tx+2,-26+op/k*.5)]);P(cv,cv.mask_poly(tu),'bone',hl=1,sh=1.6,ow=.9)
        # olho bravo
        P(cv,cv.mask_ell(tuple(HP([(26,-42)])[0]),10.5*k,10.5*k),'white',hl=0,sh=2.4,ow=1.2);P(cv,cv.mask_ell(tuple(HP([(29,-42)])[0]),7*k,8*k),'yell',hl=1,sh=2,ow=.8)
        P(cv,cv.mask_ell(tuple(HP([(31,-42)])[0]),2.6*k,5.4*k),'dark',hl=0,sh=0,ow=0);P(cv,cv.mask_ell(tuple(HP([(27,-46)])[0]),2*k,2*k),'white',hl=0,sh=0,ow=0)
        brow=HP([(14,-58),(40,-48),(42,-54),(16,-66)]);P(cv,cv.mask_poly(brow),'skin2',hl=0,sh=1.8,ow=1.2);P(cv,cv.mask_poly(smooth(HP([(14,-58),(40,-48),(40,-52),(16,-63)]),3)),'dark',hl=0,sh=0,ow=0)
        # capacete + chifre
        helm=np.array([(-30,-46),(-26,-70),(-6,-86),(22,-84),(40,-70),(44,-52),(30,-56),(8,-58),(-14,-52)])*k+np.array(nk)
        P(cv,cv.mask_poly(smooth(helm,8)),'metal',hl=3.4,sh=5.4,ow=1.5)
        P(cv,cv.mask_poly(HP([(-32,-50),(46,-50),(46,-58),(-32,-58)])),'leat',hl=1.6,sh=2.6)
        horn=HP([(-4,-82),(-10,-100),(-22,-118),(-14,-98),(6,-84)]);P(cv,cv.mask_poly(smooth(horn,6)),'bone',hl=1.6,sh=2.6,ow=1.2)
        for rx in (-18,0,18):P(cv,cv.mask_ell(tuple(HP([(rx,-54)])[0]),2.2*k,2.2*k),'metal',hl=.8,sh=1,ow=.5)
        # braço perto
        S,E,Hd=arm(g('us',8),g('fe',12),False)
        P(cv,cv.mask_capsule([S,E,Hd],[(10*k,8*k),(8*k,7*k)]),'skin',hl=2.4,sh=3.6)
        ba=((E[0]*.4+Hd[0]*.6,E[1]*.4+Hd[1]*.6));P(cv,cv.mask_capsule([E,ba],[(8.3*k,8.3*k)]),'leat',hl=1.4,sh=2.2,ow=1)
        P(cv,cv.mask_ell(S,11*k,10*k),'metal',hl=2.6,sh=3.6)    # ombreira
        P(cv,cv.mask_ell(Hd,9*k,8.5*k),'skin',hl=2,sh=3)
        # cutelo na mão
        wr=-g('weapon',22)   # graus antihorário
        def W(pts):
            r=math.radians(wr);c,sn=math.cos(r),math.sin(r);A=np.array(pts,float)*k*0.8
            return np.stack([Hd[0]+A[:,0]*c+A[:,1]*sn,Hd[1]-A[:,0]*sn+A[:,1]*c],1)
        P(cv,cv.mask_poly(W([(-18,-5),(46,-5),(46,5),(-18,5)])),'leat',hl=1.2,sh=1.8,ow=1.2)
        P(cv,cv.mask_poly(W([(42,-11),(50,-11),(50,11),(42,11)])),'metal',hl=1,sh=1.6,ow=1.2)
        bl=W([(50,-9),(78,-16),(120,-30),(150,-24),(156,-12),(152,30),(124,40),(86,24),(50,10)]);P(cv,cv.mask_poly(smooth(bl,5)),'metal',hl=3,sh=5,ow=1.6)
        P(cv,cv.mask_poly(W([(60,-3),(138,-14),(138,-9),(60,2)])),'metal',hl=0,sh=1.4,ow=.6)
        for nx in (96,118,140):
            P(cv,cv.mask_ell(tuple(W([(nx,-26)])[0]),4*k,3*k),'metal',hl=0,sh=0,ow=0)
        return cv.result()
