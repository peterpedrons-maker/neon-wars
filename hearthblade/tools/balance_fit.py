import math,numpy as np
C=dict(hp=120,atk=14,def_=8,aspd=.85,crit=.10)
def tierOf(L):return max(1,min(12,1+(max(1,L)-1)//5))
def tm(t):return 1+.07*(t-1)
M=1.4
def gear(L):
    il=max(1,round(.9*L));t=tierOf(il);m=M*tm(t);aff=2
    return (2.2+il*1.1)*m+aff*il*.35*M*tm(t)*.2,(1+il*.35)*m+(1.6+il*.6)*m+(.8+il*.25)*m+aff*il*.18*M*tm(t)*.4,(4+il*3)*m+(8+il*5)*m+(6+il*4)*m+aff*il*2.5*M*tm(t)*.4
import math as _m
TAB={1: [135, 14, 8.8], 2: [171.5, 17.7, 11.5], 3: [212.3, 20.9, 13.8], 5: [316.2, 29.3, 19.7], 8: [496.9, 45.9, 31.5], 10: [634, 55.6, 38.1], 15: [1183.9, 98.7, 66.4], 20: [1738.7, 145, 88.4], 25: [2625.1, 223, 129.3], 30: [3513.6, 301.8, 173.8], 40: [6313.2, 527.5, 307.5], 50: [9503.2, 819.1, 447.5], 60: [13863, 1184.6, 659.1]}
_K=sorted(TAB)
def hero(L):
    for a,b in zip(_K,_K[1:]):
        if a<=L<=b:
            f=(L-a)/(b-a);return tuple(_m.exp(_m.log(x)*(1-f)+_m.log(y)*f) for x,y in zip(TAB[a],TAB[b]))
    return tuple(TAB[_K[-1]])
MA=1.3
def dif(L):return min(1.0,max(0.0,(L-1)/59.0))**1.6   # curva de dificuldade: lenta no começo, íngreme no endgame
def TTf(L):return 5.0+8.5*dif(L)            # tempo p/ matar um monstro do nível do herói (s)
def LOSSf(L):return .07+.30*dif(L)          # fração da vida perdida por abate
LS=list(range(1,61))
need_hp={};need_atk={}
for L in LS:
    hp,pw,df=hero(L)
    dps=pw*(1+C['crit']*.8)/C['aspd']
    need_hp[L]=TTf(L)*dps
    taken=LOSSf(L)*hp/(TTf(L)/MA)
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
