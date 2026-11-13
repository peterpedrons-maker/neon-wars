"""Rig v2: coluna (pelvis/cintura/peito), pescoco, clavicula, ombro-cotovelo-pulso-mao, quadril-joelho-tornozelo-pe, IK, cadeias com mola (pluma/capa)."""
import math
D2R=math.pi/180
GX,GY=84,116;SC=1.22
DIM=dict(thigh=16,shin=16,spine1=8,spine2=18,neck=4,head=11,up=14,fore=13,hand=4,sv=9.5,hv=8)
LEGH=DIM['thigh']+DIM['shin']
def lerp(a,b,t):
    if isinstance(a,(tuple,list)):return tuple(lerp(x,y,t) for x,y in zip(a,b))
    return a+(b-a)*t
def ease(t,k='io'):
    if k=='lin':return t
    if k=='out':return 1-(1-t)**3
    if k=='in':return t*t*t
    return t*t*(3-2*t)
BASE=dict(dx=0,dy=0,lean=0,torso=0,chest=0,neck=0,head=0,grot=0,footB=(-12,0),footF=(12,0),ftB=0,ftF=0,handF=(12,14),handB=(-12,14),wrF=0,wrB=0,shF=0,shB=0,wa=-78,sa=0,pulse=0,jaw=0,flash=0,post=0,sq=1,blink=0)
def pose(**k):
    p=dict(BASE);p.update(k);return p
def sample(keys,t):
    if t<=keys[0][0]:return dict(keys[0][1])
    for (t0,p0),(t1,p1) in zip(keys,keys[1:]):
        if t0<=t<=t1:
            u=(t-t0)/(t1-t0 or 1);u=ease(u,p1.get('_e','io'));return {k:lerp(p0[k],p1[k],u) for k in p0 if not k.startswith('_')}
    return dict(keys[-1][1])
def ik(O,T,l1,l2,score):
    dx,dy=T[0]-O[0],T[1]-O[1];d0=math.hypot(dx,dy) or 1e-6;d=min(max(d0,abs(l1-l2)+.01),l1+l2-.01)
    a=math.atan2(dy,dx);al=math.acos(max(-1,min(1,(l1*l1+d*d-l2*l2)/(2*l1*d))))
    best=None
    for sgn in(1,-1):
        J=(O[0]+math.cos(a+sgn*al)*l1,O[1]+math.sin(a+sgn*al)*l1);sc=score(J)
        if best is None or sc>best[0]:best=(sc,J)
    return best[1],(O[0]+dx/d0*d,O[1]+dy/d0*d)
def U(a):return (math.sin(a),-math.cos(a))
def F(a):return (math.cos(a),math.sin(a))
def add(o,v,k):return (o[0]+v[0]*k,o[1]+v[1]*k)
def solve(p):
    D=DIM;sc=SC
    P=(GX+p['dx']*sc,GY-LEGH+p['dy']*sc)
    a0=(p['lean'])*D2R;a1=(p['lean']+p['torso'])*D2R;a2=(p['lean']+p['torso']+p['chest'])*D2R
    S={'p':p}
    S['P']=P;S['u0']=U(a0);S['f0']=F(a0)
    W=add(P,U((a0+a1)/2),D['spine1']);S['W']=W
    N=add(W,U((a1+a2)/2+0),D['spine2']);S['N']=N;S['u2']=U(a2);S['f2']=F(a2);S['u1']=U(a1);S['f1']=F(a1)
    an=a2+p['neck']*D2R;Nt=add(N,U(an),D['neck']);S['Nt']=Nt
    ah=a2+(p['neck']+p['head'])*D2R;S['uh']=U(ah);S['fh']=F(ah);S['ah']=ah
    S['H']=add(Nt,S['uh'],D['head'])
    S['sF']=add(add(N,S['f2'],D['sv']*.85),S['u2'],-3.5+p['shF']);S['sB']=add(add(N,S['f2'],-D['sv']*.85),S['u2'],-3.5+p['shB'])
    S['hipF']=add(P,S['f0'],D['hv']*.8);S['hipB']=add(P,S['f0'],-D['hv']*.8)
    for s_ in 'FB':
        hip=S['hip'+s_];ft=p['foot'+s_];T=(GX+ft[0]*sc,GY+ft[1]*sc-3.5)
        J,E=ik(hip,T,D['thigh'],D['shin'],lambda J:J[0]);S['knee'+s_]=J;S['ank'+s_]=E
        fa=p['ft'+s_]*D2R;S['toe'+s_]=add(E,F(-fa),9*sc*.85);S['heel'+s_]=add(E,F(-fa),-3.5)
        sh=S['s'+s_];h=p['hand'+s_];T=(N[0]+h[0]*sc,N[1]+h[1]*sc)
        J,E=ik(sh,T,D['up'],D['fore'],lambda J,sh=sh:J[1]-(J[0]-sh[0])*.2);S['el'+s_]=J;S['wr'+s_]=E
        fo=math.atan2(E[1]-J[1],E[0]-J[0])+p['wr'+s_]*D2R;S['ha'+s_]=fo;S['hand'+s_]=add(E,F(fo),D['hand'])
    sq=p.get('sq',1)
    if sq!=1:
        sx=1/math.sqrt(sq)
        for k,v in list(S.items()):
            if isinstance(v,tuple) and len(v)==2 and not k.startswith(('u','f')):S[k]=(GX+(v[0]-GX)*sx,GY+(v[1]-GY)*sq)
    g=p['grot']*D2R
    if g:
        cg,sg=math.cos(g),math.sin(g)
        for k,v in list(S.items()):
            if isinstance(v,tuple) and len(v)==2 and not k.startswith(('u','f')):
                x,y=v[0]-GX,v[1]-GY;S[k]=(GX+x*cg-y*sg,GY+x*sg+y*cg)
            elif isinstance(v,tuple) and len(v)==2:
                S[k]=(v[0]*cg-v[1]*sg,v[0]*sg+v[1]*cg)
        for k in('ha','ah'):pass
        for k in list(S):
            if (k.startswith('ha') and isinstance(S[k],float)) or k=='ah':S[k]=S[k]+g
    S['g']=g
    if p.get('post'):
        for k,v in list(S.items()):
            if isinstance(v,tuple) and len(v)==2 and not k.startswith(('u','f')):S[k]=(v[0],v[1]-p['post'])
    return S
class Chain:
    """cadeia com mola: segue um ancora com inercia (pluma, capa, barra do manto)"""
    def __init__(s,n,seg,k=60,c=7,g=(0,1)):
        s.n,s.seg,s.k,s.c,s.g=n,seg,k,c,g;s.pos=None;s.vel=None
    def step(s,anchor,dt,sub=4):
        if s.pos is None:
            s.pos=[(anchor[0]+s.g[0]*s.seg*i,anchor[1]+s.g[1]*s.seg*i) for i in range(s.n+1)];s.vel=[(0,0)]*(s.n+1)
        for _ in range(sub):
            h=dt/sub;s.pos[0]=anchor
            for i in range(1,s.n+1):
                par=s.pos[i-1];rest=(par[0]+s.g[0]*s.seg,par[1]+s.g[1]*s.seg)
                ax=(rest[0]-s.pos[i][0])*s.k-s.vel[i][0]*s.c;ay=(rest[1]-s.pos[i][1])*s.k-s.vel[i][1]*s.c
                vx=s.vel[i][0]+ax*h;vy=s.vel[i][1]+ay*h;s.vel[i]=(vx,vy);s.pos[i]=(s.pos[i][0]+vx*h,s.pos[i][1]+vy*h)
                dx,dy=s.pos[i][0]-par[0],s.pos[i][1]-par[1];L=math.hypot(dx,dy) or 1
                if L>s.seg*1.6:s.pos[i]=(par[0]+dx/L*s.seg*1.6,par[1]+dy/L*s.seg*1.6)
        return list(s.pos)

def sample_spline(keys,t):
    """spline cubica (Hermite/cardinal) entre poses-chave com tempos irregulares: da arcos e overshoot naturais"""
    ts=[k[0] for k in keys]
    if t<=ts[0]:return {k:v for k,v in keys[0][1].items() if not k.startswith('_')}
    if t>=ts[-1]:return {k:v for k,v in keys[-1][1].items() if not k.startswith('_')}
    i=max(j for j in range(len(ts)-1) if ts[j]<=t);t0,t1=ts[i],ts[i+1];u=(t-t0)/(t1-t0);h=t1-t0
    def cmp(name,c=None):
        def val(j):
            v=keys[j][1][name];return v if c is None else v[c]
        p0,p1=val(i),val(i+1)
        def tan(j):
            a=max(j-1,0);b=min(j+1,len(ts)-1)
            return (val(b)-val(a))/(ts[b]-ts[a]) if b!=a else 0
        m0,m1=tan(i)*h,tan(i+1)*h
        u2,u3=u*u,u*u*u
        return (2*u3-3*u2+1)*p0+(u3-2*u2+u)*m0+(-2*u3+3*u2)*p1+(u3-u2)*m1
    out={}
    for k,v in keys[0][1].items():
        if k.startswith('_'):continue
        out[k]=tuple(cmp(k,c) for c in range(len(v))) if isinstance(v,(tuple,list)) else cmp(k)
    return out
