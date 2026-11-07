import math
from weapons import *
def idle(wt):
    F=[]
    for k in range(4):
        b=[0,0,1,1][k];F.append(dict(weapon=wt,bob=b,handR=(34,31+b*.5) if wt!='bow' else (30,31),handL=(10,31+b*.5) if wt!='bow' else (10,28+b*.5),wang=15 if wt!='staff' else 0,head=(0,0),earL=[0,1,2,1][k],earR=[0,-1,-2,-1][k],shield=(wt=='sword'),
          **(dict(pull=None) if wt=='bow' else {})))
    return F,[260]*4
def walk(wt):
    F=[]
    for k in range(6):
        p=2*math.pi*k/6;s=math.sin(p);c=math.cos(p)
        lift=lambda v:max(0,v)*2.6
        F.append(dict(weapon=wt,bob=0 if abs(s)>.5 else 1,feet=(17.5-s*1.5,38-lift(s)+0*c,26.5-s*1.5,38-lift(-s)),handR=(34-s*1.5,31+c*.8) if wt!='bow' else (30-s,31),handL=(10+s*1.5,31-c*.8) if wt!='bow' else (10,28-c*.6),wang=15-s*6 if wt!='staff' else -s*4,
          earL=3*math.sin(2*p),earR=-3*math.sin(2*p),shield=(wt=='sword')))
    return F,[100]*6
def tipfx(cols):
    def f(g,tip):pass
    return f
def attack(wt):
    base=dict(weapon=wt,shield=(wt=='sword'))
    if wt in('sword',):
        H=[((34,31),15),((37,22),55),((35,15),32),((25,22),-40),((14,29),-115),((11,33),-140),((11,33),-140),((28,31),-30),((34,31),15)]
    elif wt=='axe':
        H=[((34,31),15),((34,22),20),((33,10),12),((32,14),80),((30,31),168),((30,34),175),((30,34),175),((32,30),110),((34,31),15)]
    elif wt=='hammer':
        H=[((34,31),15),((35,22),25),((33,9),10),((31,16),85),((28,33),170),((28,35),178),((28,35),178),((31,30),110),((34,31),15)]
    elif wt=='dagger':
        H=[((34,31),15),((36,28),30),((38,25),60),((30,34),175),((26,40),180),((30,34),175),((34,31),90),((34,31),15)]
    elif wt=='staff':
        H=[((34,31),0),((34,26),0),((34,20),0),((34,18),8),((34,20),20),((34,24),30),((34,28),10),((34,31),0),((34,31),0)]
    elif wt=='bow':
        BH=[((30,31),(10,28),None,None),((30,28),(8,27),None,None),((26,27),(8,27),'n',None),((21,26),(8,27),'d',None),((19,26),(8,27),'d',None),((27,28),(8,27),'f',None),((30,29),(9,28),None,None),((30,31),(10,28),None,None),((30,31),(10,28),None,None)]
        F=[]
        for i,(hr,hl,ar,_) in enumerate(BH):
            p=dict(base);p.update(handR=hr,handL=hl,wang=0,bob=[0,0,1,1,1,1,0,0,0][i],earL=[0,-2,-3,-4,-5,4,2,0,0][i],earR=[0,2,3,4,5,-4,-2,0,0][i],shield=False)
            if ar in('n','d'):p['pull']=hr;p['arrow']=((hr[0],hr[1]),(hl[0]-5,hl[1]))
            if ar=='f':p['pull']=None;p['arrow']=((2,hl[1]),(-9,hl[1]))
            F.append(p)
        return F,[120,90,90,80,160,70,110,120,120]
    else:
        H=[((34,31),0)]*9
    F=[]
    n=len(H);prev_tip=[None]
    for i,(hand,a) in enumerate(H):
        p=dict(base);p.update(handR=hand,wang=a,bob=[0,1,1,1,0,2,2,1,0][i],earL=[0,-3,-6,-4,3,8,5,2,0][i],earR=[0,3,6,4,-3,-8,-5,-2,0][i],head=(0,[0,0,-1,0,0,1,1,0,0][i]),
               handL=(10,31) if wt!='sword' else (9+[0,-1,-2,-2,0,1,1,0,0][i],31))
        if wt=='staff':
            p['glow']=[0,0,1.5,3,4.5,3,1.5,0,0][i]
        if wt in('sword','axe','hammer','dagger') and 3<=i<=6:
            def mk(i=i):
                def f(g,tip):
                    if tip is None:return
                    # rastro: arco entre a ponta atual e uma anterior
                    k=(i-3)
                    pts=[(H[i-1][0],H[i-1][1]),(hand,a)]
                    pa=at(H[i-1][0],dirv(H[i-1][1]),13 if wt=='sword' else 12);pb=tip
                    cols=[RAMPS['W'][0],RAMPS['M'][0],RAMPS['W'][1]]
                    pa=(pb[0]+(pa[0]-pb[0])*.45,pb[1]+(pa[1]-pb[1])*.45);trail(g,pa,pb,cols[:2])
                    if i in(4,5) and wt in('axe','hammer','dagger','sword'):
                        for dx,dy,c in((-3,2,'W'),(3,3,'W'),(0,5,'H'),(-5,0,'H'),(5,0,'W')):g.dot(tip[0]+dx,tip[1]+dy,RAMPS[c][0])
                return f
            p['fx']=mk()
        F.append(p)
    return F,[120,90,90,60,50,90,160,110,120][:n]
