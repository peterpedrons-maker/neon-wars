"""Animation Engine: poses-chave, interpolação (Catmull-Rom/smoothstep), ciclos de caminhada/corrida e ações com antecipação, impacto e recuperação."""
import math
def cr(p0,p1,p2,p3,t):return .5*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t*t+(-p0+3*p1-3*p2+p3)*t**3)
def cyc(vals,p):
    ks=vals[:-1];n=len(ks);p%=1.0
    for i in range(n):
        a=ks[i][0];b=ks[(i+1)%n][0]+(1 if i==n-1 else 0);pp=p if p>=a else p+1
        if a<=pp<b:
            t=(pp-a)/(b-a);v=lambda j:ks[j%n][1];return cr(v(i-1),v(i),v(i+1),v(i+2),t)
    return ks[0][1]
def ss(t):return t*t*(3-2*t)
def seq(keys,t,mode='smooth'):
    """keys: lista de (tempo 0..1, pose). Suaviza entre chaves; 'open' e flags pegam o valor da chave mais próxima"""
    ts=[k[0] for k in keys];t=max(ts[0],min(ts[-1],t))
    for (a,A),(b,B) in zip(keys,keys[1:]):
        if a<=t<=b:
            u=(t-a)/(b-a) if b>a else 0;u=ss(u) if mode=='smooth' else u;out={}
            for k in set(A)|set(B):
                va,vb=A.get(k,B.get(k,0)),B.get(k,A.get(k,0))
                out[k]=(va if u<.5 else vb) if k in('open','lie') else va+(vb-va)*u
            return out
    return dict(keys[-1][1])
LEGK=[(0,(1,.1)),(.12,(.6,.3)),(.25,(0,.2)),(.5,(-.93,.1)),(.62,(-.87,.8)),(.75,(-.2,1.1)),(.88,(.67,.55)),(1,(1,.1))]
def leg_pose(p,stride,bend,rest):
    return cyc([(k,v[0]) for k,v in LEGK],p)*stride,max(0,cyc([(k,v[1]) for k,v in LEGK],p)*bend)+rest
def idle(n=10,ms=140):
    out=[]
    for i in range(n):
        p=i/n;s=math.sin(2*math.pi*p);c=math.cos(2*math.pi*p)
        out.append(dict(bob=.9*(.5+.5*s),ls=-8+2*s,le=-18-3*s,us=8+2.5*s,fe=20+2*s,weapon=22+3*s,wf=250+3*s,lean=1+.4*s,hy=-.4*s,csway=.5*c,la=3,lk=10,ra=-3,rk=10))
    return out,[ms]*n,{}
def walk(n=12,ms=85,stride=30,bend=78,rest=12,bob=1.5,swing=26,er=26):
    out=[]
    for i in range(n):
        p=i/n;s=math.sin(2*math.pi*p);c=math.cos(2*math.pi*p)
        la,lk=leg_pose(p+.5,stride,bend,rest);ra,rk=leg_pose(p,stride,bend,rest)
        out.append(dict(bob=bob*(.5+.5*math.cos(4*math.pi*(p-.25))),la=la,lk=lk,ra=ra,rk=rk,ls=swing*s,le=-er-8*max(0,c),us=8-swing*.35*s,fe=er+4,
            weapon=22-8*math.sin(2*math.pi*(p-.08)),wf=250+8*s,lean=3,hy=-.5*math.cos(4*math.pi*(p-.1)),csway=1.2*math.sin(2*math.pi*(p-.2))))
    return out,[ms]*n,{0:'step_l',n//2:'step_r'}
def run(n=8,ms=70):
    out=[]
    for i in range(n):
        p=i/n;s=math.sin(2*math.pi*p);c=math.cos(2*math.pi*p)
        la,lk=leg_pose(p+.5,44,96,20);ra,rk=leg_pose(p,44,96,20)
        out.append(dict(bob=2.6*abs(math.sin(2*math.pi*p)),la=la,lk=lk,ra=ra,rk=rk,ls=40*s,le=-50,us=30-14*s,fe=40,weapon=-20-10*s,wf=262,lean=10,hy=-.7*abs(c),csway=2*math.sin(2*math.pi*(p-.2)),lf0=1.2*max(0,s),lf1=1.2*max(0,-s)))
    return out,[ms]*n,{0:'step_l',n//2:'step_r'}
def _keys(n,ms_list,keys,events=None):
    """amostra n quadros ao longo das chaves; cada chave tem 'ms' (duração) e a pose"""
    T=[0];[T.append(T[-1]+k[0]) for k in keys[:-1]];tot=T[-1] or 1
    ks=[(t/tot,k[1]) for t,k in zip(T,keys)]
    out=[seq(ks,i/(n-1)) for i in range(n)]
    return out,ms_list,events or {}
REST=dict(us=8,fe=22,weapon=22,wf=250,lean=0,crouch=0,open=0,ls=-8,le=-18,la=4,lk=10,ra=-4,rk=10,hy=0,bob=0,csway=0)
def P(**k):d=dict(REST);d.update(k);return d
def attack(n=12):
    keys=[(90,P()),(110,P(us=20,fe=30,weapon=28,lean=-3,crouch=3,la=12,lk=26,ra=-8,rk=20)),(150,P(us=125,fe=48,weapon=250,wf=100,lean=-8,la=10,lk=14,ra=-12,rk=10,ls=-24,le=-30)),
          (150,P(us=172,fe=34,weapon=260,wf=92,lean=-11,open=1,la=8,lk=10,ra=-14,rk=8,ls=-34,le=-30,hy=1)),(40,P(us=95,fe=20,weapon=350,wf=190,lean=2,open=1,crouch=1,la=22,lk=20,ra=-14,rk=10,ls=18,le=-8)),
          (50,P(us=55,fe=14,weapon=50,wf=265,lean=11,open=1,crouch=4,la=28,lk=34,ra=-20,rk=14,ls=38,le=-10,hy=-1)),(80,P(us=50,fe=16,weapon=48,wf=265,lean=12,open=1,crouch=4,la=28,lk=34,ra=-20,rk=14,ls=40,le=-10,hy=-1,csway=1.5)),
          (110,P(us=38,fe=30,weapon=70,wf=262,lean=6,crouch=3,la=18,lk=22,ra=-12,rk=14,ls=20)),(120,P(us=18,fe=26,weapon=30,lean=2,crouch=1)),(100,P())]
    ms=[90,110,150,150,40,50,80,110,120,100][:len(keys)]
    out,_,_=_keys(n,None,keys);dur=[round(sum(ms)/n)]*n
    return out,dur,{n//4:'windup',(n*5)//10:'hit'}
def skill(n=14):
    """habilidade especial: golpe pesado em duas mãos, grito e pancada no chão (onda de choque)"""
    keys=[(100,P()),(160,P(us=30,fe=40,weapon=40,lean=-6,crouch=5,la=14,lk=34,ra=-10,rk=30,ls=-20,le=-40,open=1)),(260,P(us=178,fe=24,weapon=265,wf=95,lean=-14,open=1,crouch=0,la=8,lk=12,ra=-14,rk=10,ls=-40,le=-26,bob=2)),
          (60,P(us=120,fe=10,weapon=330,wf=180,lean=6,open=1,crouch=2,la=20,lk=18,ra=-16,rk=10,ls=10)),(60,P(us=50,fe=6,weapon=58,wf=268,lean=16,open=1,crouch=6,la=32,lk=44,ra=-22,rk=18,ls=44,le=-6)),
          (200,P(us=48,fe=8,weapon=56,wf=268,lean=17,open=1,crouch=6,la=32,lk=44,ra=-22,rk=18,ls=44,le=-6,csway=2)),(160,P(us=30,fe=30,weapon=40,lean=8,crouch=3)),(120,P())]
    ms=[100,160,260,60,60,200,160,120];out,_,_=_keys(n,None,keys);return out,[round(sum(ms)/n)]*n,{n//3:'windup',(n*5)//9:'hit'}
def hurt(n=7):
    keys=[(40,P()),(70,P(open=1,lean=-10,us=40,fe=8,weapon=300,wf=235,la=16,lk=14,ra=-8,rk=10,ls=30,le=-4,hy=-1,crouch=1,sway=1.5)),(70,P(open=1,lean=-15,us=58,fe=0,weapon=290,wf=225,la=20,lk=24,ra=-6,rk=14,ls=42,le=-4,hy=-1.5,crouch=2,sway=3)),
          (80,P(open=1,lean=-9,us=42,fe=8,weapon=305,wf=240,la=10,lk=12,crouch=1,sway=1.5)),(100,P(lean=-3,us=20,fe=16,weapon=318,wf=248)),(80,P())]
    out,_,_=_keys(n,None,keys);return out,[70]*n,{1:'hit_recoil'}
def block(n=7):
    keys=[(60,P()),(90,P(us=72,fe=44,weapon=275,wf=0,lean=-3,crouch=2,la=10,lk=20,ra=-6,rk=16)),(220,P(us=78,fe=40,weapon=280,wf=0,lean=-5,crouch=3,la=12,lk=22,ra=-8,rk=18)),
          (60,P(us=70,fe=42,weapon=272,wf=4,lean=-9,crouch=3,la=14,lk=24,ra=-8,rk=18,sway=2)),(120,P(us=76,fe=40,weapon=278,wf=0,lean=-5,crouch=3,la=12,lk=22)),(100,P())]
    out,_,_=_keys(n,None,keys);return out,[90]*n,{3:'block_hit'}
def dodge(n=8):
    keys=[(50,P()),(80,P(crouch=5,lean=-6,la=16,lk=40,ra=-10,rk=36,us=12,fe=28,ls=-30,le=-30)),(110,P(crouch=-1,bob=5,lean=-14,la=-26,lk=70,ra=-34,rk=76,us=36,fe=20,ls=40,le=-24,lf0=3,lf1=3,sway=-5)),
          (90,P(crouch=3,lean=-8,la=12,lk=32,ra=-6,rk=30,us=16,fe=24,sway=-6)),(120,P(crouch=1,lean=-2,sway=-2)),(100,P())]
    out,_,_=_keys(n,None,keys);return out,[75]*n,{2:'dodge_start'}
def death(n=12):
    keys=[(60,P()),(80,P(open=1,lean=-12,us=45,fe=6,weapon=300,wf=230,la=16,lk=14,ra=-8,rk=10,ls=34,le=-4,sway=2,crouch=1)),(110,P(open=1,lean=-20,crouch=5,us=60,fe=4,weapon=300,wf=220,la=26,lk=48,ra=-12,rk=44,ls=44,le=-4,sway=4)),
          (120,P(open=1,lean=-34,crouch=9,us=70,fe=4,weapon=310,wf=215,la=34,lk=70,ra=-4,rk=64,ls=50,le=-4,sway=6,hy=-1)),(140,P(open=1,lie=1,lean=0,crouch=0,us=60,fe=6,weapon=320,wf=214,la=10,lk=24,ra=-8,rk=20,ls=40,le=-10)),
          (200,P(open=1,lie=1,us=50,fe=10,weapon=330,wf=210,la=6,lk=16,ra=-6,rk=14,ls=30,le=-10)),(500,P(open=1,lie=1,us=46,fe=10,weapon=332,wf=210,la=4,lk=14,ra=-4,rk=12,ls=26,le=-10))]
    out,_,_=_keys(n,None,keys);ms=[100]*(n-1)+[600];return out,ms,{n//3:'fall',n-1:'dead'}
TEMPLATES={'idle':idle,'walk':walk,'run':run,'attack':attack,'skill':skill,'hurt':hurt,'block':block,'dodge':dodge,'death':death}
LOOPS={'idle':True,'walk':True,'run':True}
def build(name,**kw):
    poses,ms,events=TEMPLATES[name](**kw);return poses,ms,events,LOOPS.get(name,False)
