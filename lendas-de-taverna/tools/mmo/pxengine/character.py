"""Character Generator: monta o personagem a partir de JSON (peças desenhadas em tons + membros com articulações)."""
import json,math,os
import numpy as np
from .renderer import Buf,part_from_rows,MID,D
def ang(p,a,L):r=math.radians(a);return (p[0]+math.sin(r)*L,p[1]+math.cos(r)*L)
class Character:
    def __init__(s,path):
        s.spec=json.load(open(path));s.W,s.H=s.spec['canvas'];s.GY=s.spec['ground'];s.L=s.spec['limbs'];s.R=s.L['r']
        s.parts={k:(part_from_rows(v['rows'],v.get('mirror',False)),tuple(v['anchor'])) for k,v in s.spec['parts'].items()}
        s.equip=s.spec.get('equipment',{})
    def open_head(s,name,op):
        part,a=s.parts[name]
        if not op or name=='head_back' or s.spec.get('nomouth'):return part,a
        from .renderer import GLYPH
        m,mat,tone=[x.copy() for x in part]
        spots={'head_side':[(x,15,'z') for x in range(8,14)]+[(x,16,'R') for x in range(9,13)],'head_front':[(x,14,'z') for x in range(6,11)]+[(x,15,'R') for x in range(7,10)]}[name]
        for x,y,gl in spots:m[y,x]=True;mat[y,x],tone[y,x]=GLYPH[gl]
        return (m,mat,tone),a
    def put(s,buf,name,pos,flip=False,edge=False,cast=False):
        part,a=s.parts[name];w=part[0].shape[1]
        ax=(w-1-a[0]) if flip else a[0]
        buf.glyphs(part,round(pos[0]-ax),round(pos[1]-a[1]),edge=edge,cast=cast,flip=flip)
    def proj(s,view,a,L):
        r=math.radians(a)
        if view=='side':return (math.sin(r)*L,math.cos(r)*L)
        k=.32 if view=='front' else -.32
        return (0,L*(math.cos(r)+k*math.sin(r)))
    def chain(s,view,p0,a1,a2,L1,L2,out,sg):
        d1=s.proj(view,a1,L1);K=(p0[0]+d1[0]+(sg*out*abs(a2-a1)/70 if view!='side' else 0),p0[1]+d1[1])
        d2=s.proj(view,a2,L2);E=(K[0]+d2[0]+(sg*out*abs(a2-a1)/110 if view!='side' else 0),K[1]+d2[1]);return K,E
    def draw(s,view,P):
        g=P.get;B=Buf(s.W,s.H);side=view=='side';bk=view=='back';L,R=s.L,s.R
        SP=s.spec;hx=SP.get('hx_side',36) if side else SP.get('hx_front',44);hy=s.GY-SP.get('hip',15)-g('bob',0)-g('crouch',0);lean=g('lean',0);tx=hx+(lean*.35 if side else 0)+g('sway',0);ty=hy-SP.get('tdy',4)
        sh=[(tx+1,ty-4)] if side else [(tx-6,ty-3),(tx+6,ty-3)]
        def leg(i,far):
            a,k=g('la' if far else 'ra',0),g('lk' if far else 'rk',0);lift=g('lf%d'%i,0)
            H0=(hx+(1 if far else -1),hy) if side else (hx+(-3 if i==0 else 3),hy)
            K,A=s.chain(view,H0,a,a-(k if side else k*.45),L['thigh'],L['shin'],2.2,-1 if i==0 else 1);A=(A[0],A[1]-lift)
            B.tube([H0,K,A],[R['thigh'],R['shin']],MID[L.get('mat',{}).get('leg','cloth')],far=far,joints=[(K,R['knee'])]);return K,A
        def arm(us,fe,i,far,own=False):
            S=sh[0] if side else sh[i];S=(S[0]+((1 if far else -1) if side else 0),S[1])
            K,E=s.chain(view,S,us,us+fe,L['upper'],L['fore'],3.0,-1 if (not side and i==0) else 1)
            B.tube([S,K,E],[R['upper'],R['fore']],MID[L.get('mat',{}).get('arm','skin')],far=far,joints=[(K,R['elbow']),(E,R['hand'])]);return S,K,E
        if side:
            arm(g('ls',-8),g('le',-12),0,True)
            K1,A1=leg(0,True);s.put(B,'boot_side',(A1[0]+2,A1[1]+2),edge=True)
            s.put(B,'torso_side',(tx,ty),edge=True);s.put(B,'belt_side',(tx,hy-2),edge=True);s.put(B,'cloth_side',(tx+lean*.1+g('csway',0),hy),edge=True)
            K2,A2=leg(1,False);s.put(B,'boot_side',(A2[0]+2,A2[1]+2),edge=True)
            if 'kneepad' in s.equip:s.put(B,'kneepad',(K2[0]+1,K2[1]),edge=True)
            hn='head_side';hd=(tx+1+g('hx',0),ty-SP.get('hdy',6)+g('hy',0))
            S,K,Hd=arm(g('us',8),g('fe',12),0,False);wr=g('weapon',22)
            hp,ha=s.open_head(hn,g('open',0))
            B.glyphs(hp,round(hd[0]-ha[0]),round(hd[1]-ha[1]),edge=True,cast=True)
            if 'pauldron' in s.equip:s.put(B,'pauld_side',(S[0],S[1]),edge=True)
        else:
            tn='torso_back' if bk else 'torso_front';hn='head_back' if bk else 'head_front'
            K1,A1=leg(0,False);K2,A2=leg(1,False)
            s.put(B,'boot_front',(A1[0],A1[1]+2),edge=True);s.put(B,'boot_front',(A2[0],A2[1]+2),flip=True,edge=True)
            s.put(B,tn,(tx,ty+1),edge=True);s.put(B,'belt_front',(tx,hy-2),edge=True);s.put(B,'cloth_front',(tx+g('csway',0),hy),edge=True)
            if 'kneepad' in s.equip and not bk:s.put(B,'kneepad',K1,edge=True);s.put(B,'kneepad',K2,edge=True)
            lsw=g('ls',-8);S1,Kk1,E1=arm(max(8,-lsw*.6+6),g('le',-12)*.5-6,1,False)
            hp,ha=s.open_head(hn,g('open',0));hd=(tx,ty-SP.get('hdy_f',5)+g('hy',0));B.glyphs(hp,round(hd[0]-ha[0]),round(hd[1]-ha[1]),edge=True,cast=True)
            S,K,Hd=arm(g('us',8)*(1 if g('us',8)>100 else .7),g('fe',12)*.5,0,False);wr=g('wf',250)
            if 'pauldron' in s.equip:
                s.put(B,'pauld_front',(S[0],S[1]),edge=True);s.put(B,'pauld_front',(S1[0],S1[1]),flip=True,edge=True)
        # arma: gira em torno do cabo
        cp,ca=s.parts['cleaver'];B.rot_glyphs(cp,ca,Hd,-wr if side else wr,edge=True,scale=1.0 if side else round(1-.5*max(0,-math.sin(math.radians(wr))),2))
        return B
