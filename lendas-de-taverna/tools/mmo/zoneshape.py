"""FORMATO JOGÁVEL DE CADA ZONA (fonte única).  O mapa-múndi (build_mapamundi.py) e o gerador das zonas (build_mundo.py)
usam a MESMA função: a zona explorável tem exatamente o contorno que o mapa-múndi mostra.
inside(name,W,H,exits,X,Y) -> máscara booleana nas coordenadas do mundo (X,Y = arrays); exits = lista de dict(side,pos).
O contorno é um superelipse com lóbulos e ondulação determinísticos por zona (nenhum retângulo) + um corredor reto de 500px até cada
saída (a saída fica sempre na borda do retângulo da zona e ligada ao miolo)."""
import math, random
import numpy as np
M=300                       # folga mínima do contorno até a borda do retângulo
CORRW=250                   # meia-largura do corredor de saída
SQUARISH={'lago','colinas'} # zonas com arena de chefe: formato bem cheio (quase retângulo arredondado)
def _par(name):
    r=random.Random(sum(ord(c)*(i+7) for i,c in enumerate(name)))
    sq=name in SQUARISH
    return dict(e=5.0 if sq else r.uniform(2.3,3.2),p=[r.uniform(0,6.283) for _ in range(6)],
                am=[.03,.02,.01] if sq else [r.uniform(.10,.20),r.uniform(.06,.12),r.uniform(.03,.07)])
def _main(name,W,H,X,Y):
    q=_par(name); cx,cy=W/2,H/2; a=W/2-M; b=H/2-M
    k=min(1.0,min(W,H)/3600.0)          # zonas estreitas: lóbulos menores (o corredor precisa caber)
    u=(X-cx)/a; v=(Y-cy)/b; th=np.arctan2(v,u); e=q['e']
    d=(np.abs(u)**e+np.abs(v)**e)**(1.0/e)
    am=q['am']; p=q['p']
    mod=1-k*(am[0]*(.5+.5*np.sin(3*th+p[0]))+am[1]*(.5+.5*np.sin(5*th+p[1]))+am[2]*(.5+.5*np.sin(8*th+p[2])))
    wob=k*(.045*np.sin(X/310+p[3])+.035*np.sin(Y/270+p[4])+.025*np.sin((X+Y)/190+p[5]))
    return d<(mod+wob)
def _corridors(name,W,H,exits,X,Y,main):
    """mapa do miolo + corredores: cada corredor avança da borda para dentro até tocar o miolo (e mais 120px)."""
    out=main.copy(); cor=np.zeros(main.shape,bool)
    for e in exits:
        s=e['side']; pos=e['pos']
        n=0
        while True:                       # profundidade até achar o miolo no eixo do corredor
            dd=n*20
            x,y={0:(pos,dd),1:(pos,H-dd),2:(dd,pos),3:(W-dd,pos)}[s]
            if _main(name,W,H,np.array([x]),np.array([y]))[0] or dd>max(W,H)/2: break
            n+=1
        depth=n*20+120
        along=X if s<2 else Y; dep={0:Y,1:H-Y,2:X,3:W-X}[s]
        c=(np.abs(along-pos)<CORRW)&(dep<depth)&(dep>=-5)
        out|=c; cor|=c
    return out,cor
def inside(name,W,H,exits,X,Y,want_corr=False):
    main=_main(name,W,H,X,Y); out,cor=_corridors(name,W,H,exits,X,Y,main)
    return (out,cor) if want_corr else out
