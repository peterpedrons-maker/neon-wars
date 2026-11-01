import math,numpy as np
C=dict(hp=120,atk=14,def_=8,aspd=.85,crit=.10)
def tierOf(L):return max(1,min(12,1+(max(1,L)-1)//5))
def tm(t):return 1+.07*(t-1)
M=1.4
def gear(L):
    il=max(1,round(.9*L));t=tierOf(il);m=M*tm(t);aff=2
    return (2.2+il*1.1)*m+aff*il*.35*M*tm(t)*.2,(1+il*.35)*m+(1.6+il*.6)*m+(.8+il*.25)*m+aff*il*.18*M*tm(t)*.4,(4+il*3)*m+(8+il*5)*m+(6+il*4)*m+aff*il*2.5*M*tm(t)*.4
def hero(L,hpg=.15,atg=.12):
    pts=3*(L-1);F,V,R=pts*.4,pts*.4,pts*.2;gf=min(1,(L-1)/10);ga,gd,gh=[x*gf for x in gear(L)]
    return (C['hp']*(1+hpg*(L-1))+gh)*(1+.027*V),(C['atk']*(1+atg*(L-1))+ga)*(1+.02*F),(C['def_']+L*.8+gd)*(1+.02*R)
TT=8.0;LOSS=.12;MA=1.3
LS=list(range(1,61))
need_hp={};need_atk={}
for L in LS:
    hp,pw,df=hero(L)
    dps=pw*(1+C['crit']*.8)/C['aspd']
    need_hp[L]=TT*dps
    taken=(LOSS+.10*math.exp(-(L-1)/8))*hp/(TT/MA)
    lo,hi=.1,1e6
    for _ in range(80):
        a=(lo+hi)/2;red=min(.85,df/(df+5*a));t=a*(1-red)
        if t<taken:lo=a
        else:hi=a
    need_atk[L]=a
H0=87;A0=7.5
def fit(need,base):
    best=None
    for a in [x*.01 for x in range(3,120,2)]:
        for p in [x*.05 for x in range(16,70)]:
            lg=[math.log((1+a*(L-1))**p/need[L]*base) for L in LS[::2]]
            c=-sum(lg)/len(lg)   # escala ótima (log)
            err=sum((x+c)**2 for x in lg)
            if best is None or err<best[0]:best=(err,a,p,math.exp(c))
    return best
for nm,need,base in [('hp',need_hp,H0),('atk',need_atk,A0)]:
    e,a,p,c=fit(need,base);print(nm,'a=%.2f p=%.2f c=%.2f err=%.3f'%(a,p,c,e),'ratio need/model @L1,5,10,20,30,45,60:',[round(need[L]/(base*c*(1+a*(L-1))**p),2) for L in (1,5,10,20,30,45,60)])
