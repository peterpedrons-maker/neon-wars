import math,sys,json
def dif(L):return min(1.0,max(0.0,(L-1)/59.0))**1.6
TT=lambda L:5.0+8.5*dif(L);LOSS=lambda L:(.07+.30*dif(L))*100
meas={int(k):tuple(v) for k,v in json.loads(sys.argv[1]).items()}
BAL=json.loads(sys.argv[2])
TRAVEL=2.0;ks=sorted(meas)
def _reg(pts):
    n=len(pts);mx=sum(x for x,_ in pts)/n;my=sum(y for _,y in pts)/n
    b=sum((x-mx)*(y-my) for x,y in pts)/max(1e-9,sum((x-mx)**2 for x,_ in pts));return lambda x:my+b*(x-mx)
def _raw(L):
    loss,cyc=meas[L];rh=TT(L)/max(.8,cyc-TRAVEL);ra=(LOSS(L)/max(.2,loss))/rh;return rh,ra
_rh=_reg([(L,math.log(_raw(L)[0])) for L in ks]);_ra=_reg([(L,math.log(_raw(L)[1])) for L in ks])
corr=lambda L:(math.exp(_rh(L)),math.exp(_ra(L)))
hpm=lambda L:BAL['hpC']*(1+BAL['hpA']*(L-1))**BAL['hpP'];am=lambda L:BAL['atkC']*(1+BAL['atkA']*(L-1))**BAL['atkP']
LS=list(range(1,61))
needh={L:87*hpm(L)*corr(L)[0] for L in LS};needa={L:7.5*am(L)*corr(L)[1] for L in LS}
def fit(need,base):
    best=None
    for a in [x*.01 for x in range(2,100,1)]:
        for p in [x*.05 for x in range(10,90)]:
            lg=[math.log(base*(1+a*(L-1))**p/need[L]) for L in LS[::2]]
            c=-sum(lg)/len(lg);err=sum((x+c)**2 for x in lg)
            if best is None or err<best[0]:best=(err,a,p,math.exp(c))
    return best
for nm,need,base in [('hp',needh,87),('atk',needa,7.5)]:
    e,a,p,c=fit(need,base);print(nm,'C=%.3f A=%.2f P=%.2f err=%.3f'%(c,a,p,e),[round(need[L]/(base*c*(1+a*(L-1))**p),2) for L in (1,5,10,20,30,45,60)])
print('corr hp/atk',[(L,round(corr(L)[0],2),round(corr(L)[1],2)) for L in (1,5,20,40,60)])
