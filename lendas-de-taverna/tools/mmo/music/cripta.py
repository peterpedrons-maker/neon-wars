"""Trilha das Catacumbas (família dos esqueletos): Ré menor, 54 bpm — pedal de órgão, coro, cordas graves, violoncelo solo, oboé, harpa, celesta, sino tubular e tímpano de coração.
Uso: cd /tmp/aud && /usr/bin/python3 <este arquivo>  -> /tmp/aud/out/mus_floresta_cripta.ogg  (copiar como assets/audio/music/cripta_esq.ogg)"""
import sys
sys.path.insert(0,'/tmp/aud');sys.path.insert(0,'/home/user/neon-wars/lendas-de-taverna/tools/mmo/music')
from floresta import *
CC=['Dm','Dm','Bb','A','Dm','Gm','Bb','A','Dm','C','Bb','A','Gm','Dm','Bb','A']
def fill_cripta(sc,ch):
    for i,c in enumerate(ch):
        b=i*4;r=root(c,2);tones,_=chord_notes(c,3)
        sc.note(1,b,7.9 if i%2==0 else .01,r,46) if i%2==0 else None                    # pedal de órgão (a cada 2 compassos)
        for t in tones:sc.note(2,b,3.95,t,28,jit=.04)                                    # coro, bem baixo
        for t in tones:sc.note(3,b,3.95,t-12,36,jit=.03)                                 # cordas graves
        if i%2==0:sc.note(7,b,.9,r-12 if r-12>=28 else r,70);sc.note(7,b+.9,.7,r-12 if r-12>=28 else r,52)     # tímpano em 'batida de coração'
        if i%4==2:sc.note(6,b,3.8,tones[0]+24,50)                                        # sino tubular distante
        if i%4==0:
            arp=[tones[0]+12,tones[1]+12,tones[2]+12,tones[1]+24 if len(tones)>1 else tones[0]+24]
            for k in range(4):sc.note(4,b+.5+k*.9,1.8,arp[k],40 if k else 46,vj=5)       # harpa esparsa
        if i%4==3:sc.note(5,b+2,1.5,tones[2]+24,38);sc.note(5,b+3.2,1.0,tones[0]+24,34)  # celesta
    mel(sc,8,0,[('D3',3),('F3',1),('E3',2),('D3',2),('Bb2',4),('A2',2),('C#3',2),('D3',3),('F3',1),('G3',2),('F3',2),('E3',4),('A2',2),('C#3',2)],86,1.0)   # violoncelo solo
    mel(sc,9,32,[('A4',2),('G4',1),('F4',1),('E4',4),('D4',2),('F4',2),('A4',3),('G4',1),('F4',2),('E4',2),('D4',4)],72,1.0)                              # oboé
    mel(sc,8,48,[('G3',2),('F3',2),('D3',4),('Bb2',2),('C3',2),('E3',2),('A2',2),('D3',4),('A2',4)],84,1.0)
INST_C={1:(19,100),2:(52,92),3:(48,90),4:(46,96),5:(8,90),6:(14,86),7:(47,104),8:(42,108),9:(68,94)}
if __name__=='__main__':
    build2('cripta',54,CC,INST_C,fill_cripta,rv=(4.2,.4),lp=7000,hp=60,seed=11,tail=5)
