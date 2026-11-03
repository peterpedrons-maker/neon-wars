"""Trilhas da floresta (uma por família de zona), compostas à mão e renderizadas com instrumentos reais amostrados (GeneralUser GS).
Uso: cd /tmp/aud && /usr/bin/python3 <este arquivo>   (precisa de /tmp/aud/lib.py, comp.py, pylib e do GeneralUser-GS.sf2)
Saída: mus_floresta_<goblin|esq|javali|rato>.ogg em /tmp/aud/out -> copiar para lendas-de-taverna/assets/audio/music/"""
import sys
sys.path.insert(0,'/tmp/aud')
from comp import *
def mel(sc,ch,start,notes,vel,legato=1.0,swell=True):
    b=start
    for k,(nm,d) in enumerate(notes):
        if nm is not None:
            v=vel+(6 if (b%4==0) else 0)-(4 if d<=.5 else 0)
            sc.note(ch,b,d*legato,n(nm),v,jit=0.008,vj=4)
        b+=d
    return b
def bars(sc,fn,chords,**k):
    for i,c in enumerate(chords):fn(sc,i*4,c,i,**k)
def root(c,octv=2):
    r,q,b=parse_chord(c);m=12*(octv+1)+(b if b is not None else r);return m
def build2(name,bpm,chords,inst,fill,tail=3.5,rv=(2.4,.26),lp=9000,hp=60,rms=-21,seed=3,twice=None):
    sc=Score(bpm,seed=seed)
    for ch,(prog,vol) in inst.items():
        if isinstance(prog,tuple):sc.inst(ch,prog[0],bank=prog[1],vol=vol)
        else:sc.inst(ch,prog,vol=vol)
    fill(sc,chords)
    if twice is not None:                       # 2ª volta com os solistas trocados (loop de 32 compassos)
        L=len(chords)*4*60/bpm;sc.ev+=[(t+L,on,twice.get(ch,ch),p,v) for (t,on,ch,p,v) in list(sc.ev)];chords=chords*2
    x=sc.render(len(chords)*4,tail=tail)
    x=reverb(x,*rv);x=loopify(x,int(len(chords)*4*60/bpm*SR));x=tone_shape(x,hp,lp);x=normalize(x,rms)
    p=save(x,'mus_floresta_'+name,'ogg',q=4);print(name,round(len(x)/SR,1),'s',spectrum_report(x));return p

# ---------------- GOBLINS: Ré frígio, 104 bpm — fagote, corne inglês, pizzicato, tambores ----------------
CG=['Dm','Dm','Eb','Dm','Dm','Gm','Eb','A','Dm','Dm','Bb','Eb','Gm','Eb','A','A']
def fill_goblin(sc,ch):
    for i,c in enumerate(ch):
        b=i*4;r=root(c,2);tones,_=chord_notes(c,3)
        # fagote: ostinato rítmico (staccato)
        for bt,dd,x in [(0,.45,0),(1,.45,0),(1.5,.45,12),(3,.45,0),(3.5,.4,7 if i%2 else 0)]:sc.note(1,b+bt,dd,r+x,74 if bt in(0,3) else 62,vj=5)
        # pizzicato fora do tempo
        for bt in (1.5,3.5):
            for t in tones:sc.note(2,b+bt,.3,t,52,jit=.01,vj=6)
        # timpano
        sc.note(3,b,.9,r-0 if r-12<36 else r-12,92 if i%2==0 else 80);sc.note(3,b+2.5,.6,r,66)
        # cordas graves sustentadas
        if i%2==0:
            for t in tones:sc.note(4,b,7.8,t-12,38,jit=.03)
        # percussão (kit): tom grave, tom médio, maracas
        for bt,p,v in [(0,45,92),(1.5,47,70),(2,45,86),(3,43,78),(3.5,50,66)]:sc.note(9,b+bt,.25,p,v,vj=8)
        for k in range(8):sc.note(9,b+k*.5,.1,70,34 if k%2 else 42,vj=6)
    mel(sc,0,0,[('D4',.5),('F4',.5),('A4',1),('G4',.5),('F4',.5),('E4',1),('D4',1.5),('E4',.5),('F4',2),('Eb4',.5),('G4',.5),('Bb4',1),('A4',.5),('G4',.5),('F4',1),('E4',1),('D4',2),(None,2),
        ('D4',.5),('F4',.5),('A4',1),('C5',.5),('A4',.5),('F4',1),('G4',1.5),('Bb4',.5),('D5',2),('Eb5',1),('D5',.5),('C5',.5),('Bb4',1),('G4',1),('C#5',1),('E5',1),('A4',2)],84,.97)
    mel(sc,5,32,[('A4',1),('D5',1),('F5',1),('E5',1),('D5',1.5),('C5',.5),('A4',2),('Bb4',1),('D5',1),('F5',1),('D5',1),('G5',1.5),('F5',.5),('Eb5',1),('D5',1)],78,.95)
    mel(sc,0,48,[('G4',1),('Bb4',1),('D5',2),('Eb5',1.5),('D5',.5),('Bb4',2),('C#5',.5),('D5',.5),('E5',1),('F5',1),('E5',1),('E5',.5),('D5',.5),('C#5',1),('A4',2)],84,.97)
INST_G={0:(69,106),1:(70,100),2:(45,86),3:(47,100),4:(48,84),5:(73,92),9:((0,128),96)}
# ---------------- ESQUELETOS: Lá menor, 58 bpm — violoncelo, coro, harpa, sinos, cordas graves ----------------
CE=['Am','Am','F','E','Am','Dm','F','E','Am','G','F','E','Dm','Am','F','E']
def fill_esq(sc,ch):
    for i,c in enumerate(ch):
        b=i*4;r=root(c,2);tones,_=chord_notes(c,4)
        for t in tones:sc.note(1,b,3.95,t-12,44,jit=.03)                      # coro (aahs)
        for t in tones:sc.note(2,b,3.95,t,30,jit=.04)                          # cordas em tremolo (suave)
        sc.note(3,b,3.9,r,70)                                                   # contrabaixo longo
        arp=[tones[0],tones[1],tones[2],tones[1]+12 if len(tones)>1 else tones[0]+12]
        for k in range(4):sc.note(4,b+1+k*.75,1.4,arp[k]+12,52 if k==0 else 44,vj=5)  # harpa esparsa
        if i%4==0:sc.note(5,b,3.8,tones[0]+24,56)                              # sino tubular
        if i%2==0:sc.note(6,b,.9,r,78)                                          # tímpano grave
    mel(sc,7,0,[('A3',2),('C4',1),('B3',1),('A3',4),('F3',2),('A3',1),('C4',1),('B3',2),('G#3',2),
                ('A3',1),('C4',1),('E4',2),('D4',2),('F4',1),('E4',1),('C4',1.5),('A3',.5),('F3',2),('G#3',1),('B3',1),('E4',2)],88,1.0)
    mel(sc,0,32,[('E5',2),('D5',1),('C5',1),('B4',2),('G4',2),('A4',2),('C5',1),('A4',1),('G#4',2),('B4',2)],74,1.0)
    mel(sc,7,48,[('D4',2),('A3',2),('C4',1),('B3',1),('A3',2),('F3',1),('A3',1),('C4',1),('A3',1),('B3',2),('G#3',2)],88,1.0)
INST_E={7:(42,108),0:(40,92),1:(52,92),2:(44,70),3:(33,96),4:(46,96),5:(14,86),6:(47,104)}
# ---------------- JAVALIS: Sol, 98 bpm — flauta, rabeca, violão de aço, acordeão, baixo, tambor de mão ----------------
CJ=['G','F','C','G','G','F','D','G','Em','C','G','D','Em','F','D','G']
def fill_javali(sc,ch):
    for i,c in enumerate(ch):
        b=i*4;r=root(c,2);tones,_=chord_notes(c,3)
        for k,t in enumerate([tones[0],tones[1],tones[2],tones[1]]*2):sc.note(2,b+k*.5,.9,t+(12 if k%4==2 else 0),58 if k%4==0 else 46,vj=5)   # violão: arpejo
        for t in tones:sc.note(5,b,3.9,t,36,jit=.03)                           # acordeão: base suave
        for k,x in enumerate([0,0,7,0]):sc.note(3,b+k,.9,r+(12 if k==3 and i%2 else 0) if k!=2 else r+7,70-(k%2)*8,vj=4)  # baixo caminhando
        for bt,p,v in [(0,64,84),(1,60,60),(1.5,60,52),(2,64,78),(3,60,62),(3.5,61,50)]:sc.note(9,b+bt,.2,p,v,vj=8)
        sc.note(9,b+1,.1,54,40);sc.note(9,b+3,.1,54,40)
    M=[('G5',.5),('A5',.5),('B5',1),('D6',1),('B5',.5),('A5',.5),('F5',1),('A5',1),('C6',1),('A5',1),('E5',1),('G5',1),('C6',1),('G5',1),('B5',1.5),('A5',.5),('G5',2),
       ('G5',.5),('A5',.5),('B5',1),('D6',1),('E6',1),('D6',1),('C6',1),('A5',2),('A5',1),('D6',1),('F#6',1),('D6',1),('D6',.5),('B5',.5),('G5',3),
       ('E5',1),('G5',1),('B5',2),('C6',1),('B5',.5),('A5',.5),('G5',2),('B5',1),('D6',1),('G6',2),('F#6',1),('E6',1),('D6',2),
       ('E6',1),('D6',1),('B5',2),('C6',1),('A5',1),('F5',2),('A5',1),('D6',1),('C6',1),('A5',1),('B5',1),('G5',1),('D5',2)]
    mel(sc,0,0,M,88,.95)
    mel(sc,1,0,[(x[0].replace('5','4').replace('6','5') if x[0] else None,x[1]) for x in M],70,1.0)
INST_J={0:(73,108),1:(40,96),2:(25,96),3:(32,100),5:(21,90),9:((0,128),96)}
# ---------------- RATOS: Mi dórico, 76 bpm — clarinete, marimba, contrabaixo pizz, violoncelo, celesta ----------------
CR=['Em','C','Am','B','Em','D','C','B','Em','G','Am','Em','C','D','B','Em']
def fill_rato(sc,ch):
    for i,c in enumerate(ch):
        b=i*4;r=root(c,2);tones,_=chord_notes(c,3)
        for k,t in enumerate([tones[0],tones[2],tones[1],tones[2]]+[tones[0],tones[2],tones[1],tones[2]]):sc.note(1,b+k*.5,.45,t+12,56 if k%4==0 else 44,vj=5)   # marimba
        sc.note(2,b,.9,r,72);sc.note(2,b+2,.9,r+7 if i%2 else r,64)             # contrabaixo pizz
        for t in tones:sc.note(3,b,3.95,t-12,40,jit=.03)                        # violoncelo sustentado
        if i%2==1:sc.note(4,b+1.5,1.5,tones[2]+24,52);sc.note(4,b+3,1,tones[0]+24,44)   # celesta esparsa
        for t in tones:sc.note(5,b,3.95,t,28,jit=.04)
    mel(sc,0,0,[('E4',1),('G4',.5),('A4',.5),('B4',2),('C5',1.5),('B4',.5),('G4',2),('A4',1),('C5',1),('E5',2),('D#5',1),('F#5',1),('B4',2),
        ('E5',1),('D5',.5),('B4',.5),('G4',2),('F#4',1),('A4',1),('D5',2),('E5',1),('G5',1),('C5',2),('D#5',.5),('E5',.5),('F#5',2),
        (None,1),('B4',1),('E5',1),('G5',1),('G5',2),('D5',1),('B4',1),('C5',1),('E5',1),('A4',2),('B4',1),('G4',1),('E4',2),
        ('E4',1),('G4',1),('C5',1),('E5',1),('D5',1.5),('C5',.5),('A4',2),('B4',1),('D#5',1),('F#5',2),('E5',2),('B4',2)],86,.97)
INST_R={0:(71,106),1:(12,96),2:(32,100),3:(42,86),4:(8,92),5:(48,70)}
if __name__=='__main__':
    which=sys.argv[1:] or ['goblin','esq','javali','rato']
    if 'goblin' in which:build2('goblin',104,CG,INST_G,fill_goblin,rv=(2.2,.24),lp=8500,hp=70,seed=5,twice={0:5,5:0})
    if 'esq' in which:build2('esq',58,CE,INST_E,fill_esq,rv=(3.6,.36),lp=7800,hp=70,seed=6,tail=4.5)
    if 'javali' in which:build2('javali',98,CJ,INST_J,fill_javali,rv=(1.8,.2),lp=9500,hp=70,seed=7,twice={0:1,1:0})
    if 'rato' in which:build2('rato',76,CR,INST_R,fill_rato,rv=(2.8,.3),lp=8500,hp=70,seed=8,twice={0:4,4:0})
