"""Trilha dos Esgotos (família dos ratos): Dó menor, 88 bpm — clarinete baixo, marimba, pizzicato, tuba, violoncelo, glockenspiel e tímpano.
Uso: cd /tmp/aud && /usr/bin/python3 <este arquivo>  -> /tmp/aud/out/mus_floresta_esgoto.ogg  (copiar como assets/audio/music/esgoto_rato.ogg)"""
import sys
sys.path.insert(0,'/tmp/aud');sys.path.insert(0,'/home/user/neon-wars/lendas-de-taverna/tools/mmo/music')
from floresta import *
CS=['Cm','Cm','Ab','G','Cm','Fm','Ab','G','Cm','Bb','Ab','G','Fm','Cm','Ab','G']
def fill_esgoto(sc,ch):
    for i,c in enumerate(ch):
        b=i*4;r=root(c,2);tones,_=chord_notes(c,3)
        for k,t in enumerate([tones[0],tones[2],tones[1],tones[2]]*2):sc.note(1,b+k*.5,.4,t+12,52 if k%4==0 else 40,vj=5)         # marimba (arpejo)
        for bt in (1,3):
            for t in tones:sc.note(2,b+bt,.25,t,48,jit=.012,vj=6)                                                                   # pizzicato no contratempo
        sc.note(3,b,.9,r,72);sc.note(3,b+2,.9,r+7 if i%2 else r,64)                                                                 # tuba abafada
        for t in tones:sc.note(4,b,3.95,t-12,36,jit=.03)                                                                            # violoncelo sustentado
        if i%4==3:sc.note(5,b+2.5,.8,tones[2]+24,44);sc.note(5,b+3.2,.8,tones[0]+24,38)                                              # glockenspiel
        if i%2==0:sc.note(6,b,.6,r-12 if r-12>=36 else r,70)                                                                          # tímpano
    mel(sc,0,0,[('C4',1),('Eb4',.5),('G4',.5),('F4',1),('Eb4',1),('Ab3',1.5),('C4',.5),('Eb4',2),('B3',1),('D4',1),('G4',2),
        ('C4',1),('Eb4',.5),('G4',.5),('Ab4',1),('G4',1),('F4',1),('Ab4',1),('C5',2),('Bb4',1),('Ab4',.5),('G4',.5),('F4',1),('D4',1),('B3',2),
        ('C4',.5),('D4',.5),('Eb4',1),('G4',1),('F4',1),('Eb4',1),('Db4',1),('C4',2),('Bb3',1),('Ab3',1),('G3',2),('Eb4',1),('F4',1),('G4',2),
        ('F4',1),('Ab4',1),('C5',2),('Eb4',1),('G4',1),('C5',2),('B4',1),('G4',1),('F4',1),('D4',1),('C4',2)],84,.95)
INST_S={0:(71,106),1:(12,92),2:(45,92),3:(58,92),4:(42,84),5:(9,86),6:(47,98)}
if __name__=='__main__':
    build2('esgoto',88,CS,INST_S,fill_esgoto,rv=(2.6,.3),lp=8200,hp=60,seed=14,tail=4)
