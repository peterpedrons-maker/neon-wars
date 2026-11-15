"""Rig humanoide por juntas + IK de 2 ossos + keyframes. Tudo em coordenadas do canvas (1x); y para baixo."""
import math
D2R=math.pi/180
GX,GY=68,94          # ancora: pes no chao
LEGH=26;TORSO=22
def lerp(a,b,t):
    if isinstance(a,(tuple,list)):return tuple(lerp(x,y,t) for x,y in zip(a,b))
    return a+(b-a)*t
def ease(t,k='io'):
    if k=='lin':return t
    if k=='out':return 1-(1-t)**3
    if k=='in':return t*t*t
    return t*t*(3-2*t)
BASE=dict(dx=0,dy=0,lean=0,torso=0,head=0,grot=0,footB=(-12,0),footF=(12,0),handF=(12,14),handB=(-12,14),wa=-78,sa=0,sway=0,pulse=0,jaw=0,flash=0,post=0)
def pose(**k):
    p=dict(BASE);p.update(k);return p
def sample(keys,t):
    """keys=[(t,pose),...] t em 0..1; easing entre chaves (chave pode ter '_e')"""
    if t<=keys[0][0]:return dict(keys[0][1])
    for (t0,p0),(t1,p1) in zip(keys,keys[1:]):
        if t0<=t<=t1:
            u=(t-t0)/(t1-t0 or 1);u=ease(u,p1.get('_e','io'));return {k:lerp(p0[k],p1[k],u) for k in p0 if not k.startswith('_')}
    return dict(keys[-1][1])
def ik(O,T,l1,l2,score):
    dx,dy=T[0]-O[0],T[1]-O[1];d=math.hypot(dx,dy);d=min(max(d,abs(l1-l2)+.01),l1+l2-.01)
    a=math.atan2(dy,dx);cs=(l1*l1+d*d-l2*l2)/(2*l1*d);al=math.acos(max(-1,min(1,cs)))
    best=None
    for s in(1,-1):
        J=(O[0]+math.cos(a+s*al)*l1,O[1]+math.sin(a+s*al)*l1);sc=score(J)
        if best is None or sc>best[0]:best=(sc,J)
    J=best[1];ex=O[0]+math.cos(a)*d,O[1]+math.sin(a)*d
    # ponta real (clamp ao alcance)
    E=(O[0]+dx/ max(1e-6,math.hypot(dx,dy))*d,O[1]+dy/max(1e-6,math.hypot(dx,dy))*d)
    return J,E
def solve(p,L=dict(up=12,fore=11,thigh=13,shin=13,torso=TORSO,sv=9,hv=7),legh=LEGH):
    dx,dy=p['dx'],p['dy']
    P=(GX+dx,GY-legh+dy+ (0))
    l=(p['lean']+p['torso'])*D2R;u=(math.sin(l),-math.cos(l));f=(math.cos(l),math.sin(l))
    N=(P[0]+u[0]*L['torso'],P[1]+u[1]*L['torso'])
    lh=(p['lean']*.4)*D2R;hf=(math.cos(lh),math.sin(lh))
    def loc(o,a,b,fr=f,uu=u):return (o[0]+fr[0]*a+uu[0]*b,o[1]+fr[1]*a+uu[1]*b)
    S={'P':P,'N':N,'u':u,'f':f,'l':l}
    S['sF']=loc(N,L['sv']*.8,-3);S['sB']=loc(N,-L['sv']*.8,-3)
    hl=(p['lean']+p['torso']+p['head'])*D2R;hu=(math.sin(hl),-math.cos(hl));hfv=(math.cos(hl),math.sin(hl))
    S['hu']=hu;S['hf']=hfv;S['H']=(N[0]+hu[0]*10,N[1]+hu[1]*10);S['hl']=hl
    S['hipF']=(P[0]+7,P[1]+1);S['hipB']=(P[0]-7,P[1]+1)
    kneeF=lambda J:J[0];
    for s,hip,ft in(('F',S['hipF'],p['footF']),('B',S['hipB'],p['footB'])):
        T=(GX+ft[0],GY+ft[1]-2);J,E=ik(hip,T,L['thigh'],L['shin'],kneeF);S['knee'+s]=J;S['foot'+s]=E
    for s,sh,h in(('F',S['sF'],p['handF']),('B',S['sB'],p['handB'])):
        T=(N[0]+h[0],N[1]+h[1]);J,E=ik(sh,T,L['up'],L['fore'],lambda J:J[1]-(J[0]-sh[0])*.2);S['el'+s]=J;S['hand'+s]=E
    g=p['grot']*D2R
    if g:
        cg,sg=math.cos(g),math.sin(g)
        for k,v in list(S.items()):
            if isinstance(v,tuple) and k not in('u','f','hu','hf'):
                x,y=v[0]-GX,v[1]-GY;S[k]=(GX+x*cg-y*sg,GY+x*sg+y*cg)
        for k in('u','f','hu','hf'):
            x,y=S[k];S[k]=(x*cg-y*sg,x*sg+y*cg)
        S['l']+=g;S['hl']+=g
    if p.get('post'):
        for k,v in list(S.items()):
            if isinstance(v,tuple) and k not in('u','f','hu','hf'):S[k]=(v[0],v[1]-p['post'])
    S['p']=p;S['g']=g
    return S
def loc(o,fr,uu,a,b):return (o[0]+fr[0]*a+uu[0]*b,o[1]+fr[1]*a+uu[1]*b)
