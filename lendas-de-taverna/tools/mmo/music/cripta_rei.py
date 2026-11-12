"""Trilha da Cripta do Rei Esquecido: Dó menor, 52 bpm — órgão de tubos, coro, cordas graves, violoncelo solo, trompa, corne inglês, harpa, celesta, sino tubular, tímpano.
Uso: cd /tmp/aud && /usr/bin/python3 <este arquivo>  -> /tmp/aud/out/mus_floresta_cripta_rei.ogg  (copiar como assets/audio/music/cripta_rei.ogg)"""
import sys
sys.path.insert(0,'/tmp/aud');sys.path.insert(0,'/home/user/neon-wars/lendas-de-taverna/tools/mmo/music')
from floresta import *
CC=['Cm','Cm','Ab','G','Cm','Fm','Ab','G','Cm','Eb','Bb','G','Fm','Cm','Ab','G','Cm','Cm','Db','G','Fm','Bb','Ab','G']
def fill(sc,ch):
    for i,c in enumerate(ch):
        b=i*4;r=root(c,2);tones,_=chord_notes(c,3)
        if i%2==0: sc.note(1,b,7.9,r,50)                                        # pedal de órgão
        for t in tones: sc.note(2,b,3.95,t,30+(6 if i>=16 else 0),jit=.04)      # coro
        for t in tones: sc.note(3,b,3.95,t-12,38,jit=.03)                       # cordas graves
        if i%2==0: sc.note(7,b,.9,r if r>=36 else r+12,76);sc.note(7,b+.9,.7,r if r>=36 else r+12,56)   # tímpano: batida de coração
        if i>=16 and i%2==1: sc.note(7,b+2,.6,r if r>=36 else r+12,66)
        if i%4==2: sc.note(6,b,3.8,tones[0]+24,52)                              # sino tubular
        if i%2==0:
            arp=[tones[0]+12,tones[1]+12,tones[2]+12,tones[1]+24]
            for k in range(4): sc.note(4,b+.5+k*.9,1.8,arp[k],40 if k else 48,vj=5)   # harpa
        if i%4==3: sc.note(5,b+2,1.5,tones[2]+24,40);sc.note(5,b+3.2,1.0,tones[0]+24,36)   # celesta
        if i>=8 and i%4==0: sc.note(9,b,3.9,tones[0]+12,46)                     # trompa sustentada
    # violoncelo solo (tema)
    mel(sc,8,0,[('C3',3),('Eb3',1),('D3',2),('C3',2),('G2',4),('Ab2',2),('Bb2',2),('C3',3),('Eb3',1),('F3',2),('Eb3',2),('D3',4),('G2',4)],86,1.0)
    mel(sc,8,32,[('C3',2),('G3',2),('F3',2),('Eb3',2),('D3',4),('F3',2),('Eb3',2),('C3',4),('D3',2),('B2',2),('C3',4)],88,1.0)
    # corne inglês (resposta)
    mel(sc,10,16,[('G4',2),('F4',1),('Eb4',1),('D4',4),('C4',2),('Eb4',2),('G4',3),('F4',1),('Eb4',2),('D4',2),('C4',4)],72,1.0)
    # trompa (tema triunfal sombrio na segunda metade)
    mel(sc,9,64,[('C4',3),('Eb4',1),('G4',4),('F4',2),('Eb4',2),('D4',4),('C4',2),('Eb4',2),('G4',3),('Ab4',1),('G4',2),('F4',2),('D4',4),('G3',4)],92,1.0)
INST={1:(19,100),2:(52,92),3:(48,90),4:(46,96),5:(8,90),6:(14,86),7:(47,106),8:(42,108),9:(60,96),10:(69,94)}
if __name__=='__main__':
    build2('cripta_rei',52,CC,INST,fill,rv=(4.6,.42),lp=7200,hp=60,seed=13,tail=5,twice={8:10,10:8})
