import math,sys,json
def dif(L):return min(1.0,max(0.0,(L-1)/59.0))**1.6
TT=lambda L:5.0+8.5*dif(L);LOSS=lambda L:(.07+.30*dif(L))*100
meas={int(k):tuple(v) for k,v in json.loads(sys.argv[1]).items()}
K=json.loads(sys.argv[2])        # {"L":[hpmult,atkmult]} atual (multiplicadores sobre a base)
damp=float(sys.argv[3]) if len(sys.argv)>3 else .85
ks=sorted(meas)
raw={}
for L in ks:
    loss,cyc=meas[L];rh=TT(L)/max(.8,cyc-2.0);ra=(LOSS(L)/max(.2,loss))/rh;raw[L]=(math.log(min(6,max(.25,rh))),math.log(min(30,max(.15,ra))))
sm={}
for i,L in enumerate(ks):
    a=raw[ks[max(0,i-1)]];b=raw[L];c=raw[ks[min(len(ks)-1,i+1)]]
    sm[L]=tuple((.25*a[j]+.5*b[j]+.25*c[j])*damp for j in (0,1))
def at(tab,L):
    kk=sorted(int(x) for x in tab)
    if L<=kk[0]:return tab[str(kk[0])]
    if L>=kk[-1]:return tab[str(kk[-1])]
    for a,b in zip(kk,kk[1:]):
        if a<=L<=b:
            f=(L-a)/(b-a);x=tab[str(a)];y=tab[str(b)];return [math.exp(math.log(x[j])*(1-f)+math.log(y[j])*f) for j in (0,1)]
out={}
for L in [1,5,10,20,30,40,50,60]:
    cur=at(K,L);s=sm[min(ks,key=lambda k:abs(k-L))] if L not in sm else sm[L]
    out[str(L)]=[round(cur[0]*math.exp(s[0]),3),round(cur[1]*math.exp(s[1]),3)]
print(json.dumps(out))
