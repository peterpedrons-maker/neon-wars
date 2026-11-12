"""Sons de criaturas (ataque, dor, morte) e de habilidades de chefes: voz sintetizada por formantes + instrumentos reais amostrados (GeneralUser GS).
Uso: cd /tmp/aud && /usr/bin/python3 <este arquivo>  -> /tmp/aud/out/sfx/mob_*.ogg, boss_*.ogg, dg_title.ogg (copiar para lendas-de-taverna/assets/audio/sfx/)"""
import sys
sys.path.insert(0,'/tmp/aud')
src=open('/tmp/aud/sfx.py').read();exec(src[:src.index('# ---------- UI')])
R=np.random.RandomState(21)
def lp(x,f,order=2):
    b,a=signal.butter(order,f/(SR/2),'low');return signal.lfilter(b,a,x)
def room(x,decay=.35,wet=.16): return reverb(x if x.ndim==2 else st(x),decay,wet,pre=.004)
def formant(x,fs,qs=(6,8,10),gains=(1,.7,.4)):
    out=np.zeros_like(x)
    for f,q,g in zip(fs,qs,gains):
        b,a=signal.iirpeak(min(f,SR/2-200)/(SR/2),q);out+=g*signal.lfilter(b,a,x)
    return out
def glottal(f0c,d,rough=0.0,shape='saw'):
    """fonte vocal: f0c(t)->Hz. rough = jitter/amplitude pulsada (grunhido)."""
    t=t_(d);f=f0c(t)*(1+rough*.04*R.randn(len(t)).cumsum()/np.sqrt(np.arange(1,len(t)+1)))
    ph=np.cumsum(f)/SR;x=2*(ph%1)-1
    if shape=='pulse': x=np.where((ph%1)<.25,1.,-.3)
    if rough>0: x*=1-rough*.6*(.5+.5*np.sin(2*np.pi*np.cumsum(np.full(len(t),38+10*R.rand()))/SR))
    return x
def vocal(f0c,d,fs,rough=0,qs=(6,8,10),gains=(1,.7,.4),a=.01,dec=.3,breath=.08,shape='saw'):
    s=glottal(f0c,d,rough,shape);s=formant(s,fs,qs,gains)
    n=hp(noise(d),500)*breath;e=np.minimum(t_(d)/a,1)*np.exp(-t_(d)/dec)
    return (s/ (np.max(np.abs(s))+1e-9)*.9+n)*e
def clack(f=1900,dec=.018,g=.9): return bp(noise(.06),f*.6,f*1.5)*env(.06,.0006,dec)*g
def sav(name,x,peak=.85):
    save_sfx(name,x,peak)
# ============ RATO ============
sq=lambda a,b,d:(lambda t:a+(b-a)*np.clip(t/d,0,1))
x=vocal(sq(2600,4300,.09),.14,[3400,5200],qs=(8,10),gains=(1,.6),dec=.06,breath=.2,shape='pulse')
x=pad_to(x,int(.4*SR))+pad_to(vocal(sq(3000,2300,.1),.16,[3600,5600],qs=(8,10),gains=(1,.6),dec=.07,breath=.2,shape='pulse'),int(.4*SR))*0+0
x2=np.concatenate([x[:int(.16*SR)],np.zeros(int(.05*SR)),vocal(sq(2800,4600,.07),.12,[3400,5200],qs=(8,10),gains=(1,.6),dec=.05,breath=.2,shape='pulse')])
hiss=hp(noise(.28),4500)*env(.28,.02,.09)*.35
sav('mob_rato_atk',room(st(pad_to(x2,int(.5*SR))+pad_to(hiss,int(.5*SR))),.2,.08),.8)
sav('mob_rato_hurt',room(st(vocal(sq(4800,2400,.12),.2,[3200,5600],qs=(8,10),gains=(1,.7),dec=.08,breath=.15,shape='pulse')),.2,.06),.8)
sav('mob_rato_die',room(st(vocal(sq(4600,1500,.38),.5,[2800,5200],qs=(8,10),gains=(1,.7),dec=.2,breath=.12,shape='pulse')+pad_to(thud(.2,150,60,.05,.25),int(.5*SR))),.25,.1),.8)
# ============ JAVALI ============
def grunt(d=.35,f0=105,f1=70,rough=.6,fs=(520,1150,2500)):
    return vocal(lambda t:f0+(f1-f0)*np.clip(t/d,0,1),d,list(fs),rough=rough,qs=(4,5,6),gains=(1,.6,.3),dec=d*.45,breath=.1)
snort=bp(noise(.22),250,1300)*env(.22,.01,.07)*.8
sav('mob_javali_atk',room(st(pad_to(snort,int(.55*SR))+pad_to(grunt(.34,120,75),int(.55*SR))*np.r_[np.zeros(int(.1*SR)),np.ones(int(.45*SR))][:int(.55*SR)]),.25,.1),.85)
sav('mob_javali_hurt',room(st(vocal(sq(900,520,.22),.3,[1500,3000],qs=(6,8),gains=(1,.6),rough=.4,dec=.14,breath=.1)+pad_to(grunt(.2,140,90),int(.3*SR))*.5),.22,.08),.85)
sav('mob_javali_die',room(st(pad_to(vocal(sq(1000,350,.6),.75,[1400,2800],qs=(6,8),gains=(1,.6),rough=.5,dec=.3,breath=.1),int(1.0*SR))+pad_to(thud(.5,120,40,.14,.7),int(1.0*SR))*np.r_[np.zeros(int(.5*SR)),np.ones(int(.5*SR))]),.35,.14),.9)
# ============ GOBLIN ============
def cackle(n_=4,base=330):
    out=np.zeros(int(.7*SR))
    for i in range(n_):
        d=.09;v=vocal(lambda t:base*(1.08**(i%2))*(1-.25*t/d),d,[900,1900,2800],qs=(5,6,8),gains=(1,.8,.4),dec=.05,breath=.12,shape='pulse')
        o=int(i*.12*SR);out[o:o+len(v)]+=v
    return out
sav('mob_goblin_atk',room(st(cackle(4,300)),.25,.1),.8)
sav('mob_goblin_hurt',room(st(vocal(sq(520,330,.18),.24,[850,1800,2700],qs=(5,6,8),gains=(1,.8,.4),dec=.12,breath=.12,shape='pulse')),.22,.08),.8)
sav('mob_goblin_die',room(st(vocal(sq(480,170,.55),.7,[800,1700,2600],qs=(5,6,8),gains=(1,.8,.4),dec=.3,breath=.1,shape='pulse')+pad_to(thud(.2,120,50,.06,.3),int(.7*SR))),.3,.12),.8)
# ============ ESQUELETO: ossos + madeira (bloco de madeira e xilofone reais) ============
wb=sf(115,[(0,.1,'C5',100),(.09,.1,'D5',96),(.17,.1,'C5',92),(.27,.1,'E5',100)],bpm=140,vol=120,tail=.2)
sav('mob_esq_atk',room(mix(wb,st(pad_to(clack(2300),int(.5*SR))),L=len(wb)),.25,.12),.8)
L_=int(.3*SR)
sav('mob_esq_hurt',room(st(pad_to(clack(2600),L_)+pad_to(np.r_[np.zeros(int(.03*SR)),clack(1500)],L_)+pad_to(bp(noise(.2),1200,3800)*env(.2,.002,.04)*.5,L_)),.2,.08),.8)
col=np.zeros(int(1.2*SR))
for i in range(14):
    o=int((i**1.15)*.055*SR);c=clack(R.uniform(1200,3400),R.uniform(.012,.03),R.uniform(.4,1)*(1-i/18));col[o:o+len(c)]+=c[:len(col)-o]
sav('mob_esq_die',room(mix(st(col),st(pad_to(thud(.3,140,50,.1,.7),int(1.2*SR))),sf(115,[(0,.1,'G4',90),(.3,.1,'E4',80),(.55,.1,'C4',70)],bpm=140,vol=110,tail=.3)*.8,L=int(1.3*SR)),.35,.16),.85)
# ============ MORCEGO ============
def screech(d=.35,f0=5200,f1=7800):
    t=t_(d);f=f0+(f1-f0)*np.sin(np.pi*np.clip(t/d,0,1)*.9)+180*np.sin(2*np.pi*38*t)
    x=np.sin(2*np.pi*np.cumsum(f)/SR)+.4*np.sin(4*np.pi*np.cumsum(f)/SR);return x*env(d,.01,d*.5)*.8
sav('mob_bat_atk',room(st(screech(.3,5800,8200)+hp(noise(.3),5000)*env(.3,.01,.1)*.15),.25,.1),.7)
sav('mob_bat_hurt',room(st(screech(.18,7800,5200)),.2,.07),.7)
sav('mob_bat_die',room(st(screech(.5,6800,2200)),.3,.1),.7)
# ============ OGRO / CHEFES ============
def roar(d=1.0,f0=75,f1=48,fs=(420,850,2000),rough=1.0,breath=.18):
    return vocal(lambda t:f0+(f1-f0)*np.clip(t/d,0,1)+6*np.sin(2*np.pi*7*t),d,list(fs),rough=rough,qs=(3,4,5),gains=(1,.8,.4),a=.04,dec=d*.55,breath=breath)
def swell_inst(prog,notes,bpm=70,vol=115,tail=1.0): return sf(prog,notes,bpm=bpm,vol=vol,tail=tail,rv=.25)
sav('mob_ogro_atk',room(mix(st(roar(.8,95,60)),sf(57,[(0,.7,'D2',110)],bpm=90,vol=118,tail=.5),L=int(1.2*SR)),.4,.18),.9)
sav('mob_ogro_hurt',room(st(roar(.45,110,70,breath=.1)),.3,.12),.88)
sav('mob_ogro_die',room(mix(st(roar(1.5,85,32)),st(pad_to(thud(.7,90,30,.25,1.0),int(2.0*SR)))*np.r_[np.zeros(int(1.2*SR)),np.ones(int(.8*SR))].reshape(-1,1),sf(47,[(1.0,.6,'D2',120)],bpm=80,vol=127,tail=1.0),L=int(2.4*SR)),.6,.22),.92)
# chefe: rugido (metais graves + coro + rugido vocal)
sav('boss_roar',room(mix(st(roar(1.2,90,45)),sf(57,[(0,1.4,'D2',118),(0,1.4,'A2',112)],bpm=70,vol=120,tail=1.0),sf(52,[(.1,1.4,'D3',100),(.1,1.4,'F3',96)],bpm=70,vol=110,tail=1.2,rv=.3),sf(47,[(0,.5,'D2',127)],bpm=100,vol=127,tail=1.0),L=int(2.4*SR)),.6,.22),.92)
# pancada no chão
sav('boss_slam',room(mix(st(thud(.7,110,28,.22,1.1)),st(lp(noise(.5),500)*env(.5,.002,.16)*.8),sf(116,[(0,.4,'C2',127),(.12,.4,'G1',120)],bpm=120,vol=127,tail=.8),sf(47,[(0,.5,'C2',127)],bpm=100,vol=127,tail=1.0),st(hp(noise(.1),2000)*env(.1,.001,.03)*.5),L=int(1.6*SR)),.5,.2),.95)
# investida: tambores crescentes + vento
sav('boss_charge',room(mix(sf(116,[(i*.14,.2,'C2' if i%2 else 'G1',70+i*7) for i in range(9)],bpm=120,vol=124,tail=.6),st(sweep_noise(1.3,300,2200,'ramp')*env(1.3,.5,.9)*.55),st(roar(.7,85,70)*.7),L=int(1.8*SR)),.4,.16),.9)
# giro: lâmina cortando o ar em ciclos
sp=np.zeros(int(1.4*SR))
for k in range(4):
    sw_=sweep_noise(.3,900,3600)*env(.3,.05,.12);o=int(k*.3*SR);sp[o:o+len(sw_)]+=sw_[:len(sp)-o]*(.6+.1*k)
sav('boss_spin',room(mix(st(sp),sf(116,[(0,.2,'C2',100),(.6,.2,'C2',100)],bpm=120,vol=110,tail=.4),L=int(1.5*SR)),.3,.12),.85)
# guarda (escudo): metal pesado
sav('boss_guard',room(mix(st(ring_:=sum(np.sin(2*np.pi*f*t_(.9)+R.rand()*6)*np.exp(-t_(.9)/(.2+i*.05)) for i,f in enumerate([420,860,1320,2100]))*.3),st(thud(.25,200,80,.06,.7)),sf(14,[(0,.9,'C4',90)],bpm=100,vol=110,tail=.8),L=int(1.3*SR)),.35,.15),.8)
# enxame: muitos guinchos
sw=np.zeros(int(1.5*SR))
for i in range(14):
    v=vocal(sq(R.uniform(3000,4800),R.uniform(2200,5200),.1),.14,[3400,5400],qs=(8,10),gains=(1,.7),dec=.06,breath=.2,shape='pulse');o=int(R.uniform(0,1.3)*SR);sw[o:o+len(v)]+=v[:len(sw)-o]*R.uniform(.4,.9)
sav('boss_swarm',room(st(sw+hp(noise(1.5),4000)*env(1.5,.3,.9)*.12),.4,.16),.85)
# poça de praga / veneno: borbulhar
bub=np.zeros(int(1.2*SR))
for i in range(12):
    f=R.uniform(180,420);d=.12;tt=t_(d);b_=np.sin(2*np.pi*np.cumsum(f*(1+2.2*tt/d))/SR)*np.exp(-tt/.05);o=int(R.uniform(0,1.05)*SR);bub[o:o+len(b_)]+=b_*R.uniform(.4,1)
sav('boss_plague',room(st(bub+lp(noise(1.2),900)*env(1.2,.2,.7)*.25),.3,.12),.8)
# escavar: terra e pedras
sav('boss_burrow',room(mix(st(lp(noise(1.2),700)*env(1.2,.15,.6)*.9),st(thud(.9,70,28,.3,.9)),sf(116,[(0,.4,'C2',100),(.5,.4,'C2',90),(.9,.4,'C2',100)],bpm=120,vol=110,tail=.6),L=int(1.6*SR)),.4,.16),.88)
# frasco / vidro quebrando
gl=np.zeros(int(.8*SR))
for i in range(22):
    f=R.uniform(2400,7200);d=R.uniform(.05,.2);b_=np.sin(2*np.pi*f*t_(d))*np.exp(-t_(d)/(d*.4));o=int(R.uniform(0,.12)*SR+i*.012*SR);gl[o:o+len(b_)]+=b_[:len(gl)-o]*R.uniform(.3,.9)
sav('boss_flask',room(st(gl+hp(noise(.8),3000)*env(.8,.001,.05)*.3),.3,.14),.8)
sav('boss_throw',room(st(sweep_noise(.28,1200,3800)*env(.28,.05,.1)+pad_to(bp(noise(.1),300,1200)*env(.1,.002,.04)*.3,int(.28*SR))),.2,.08),.7)
# invocação sombria (coro + sino + cordas graves) — Rei Esquecido e magias de chefe
sav('boss_dark',room(mix(sf(52,[(0,2.5,'C3',100),(0,2.5,'Eb3',96),(0,2.5,'G3',92)],bpm=60,vol=118,tail=1.5,rv=.35),sf(14,[(0,1.5,'C4',90),(1.2,1.5,'G3',80)],bpm=60,vol=110,tail=1.5),sf(47,[(0,.5,'C2',127),(1,.5,'C2',127)],bpm=60,vol=127,tail=1.0),st(roar(1.5,70,40,breath=.12))*.6,L=int(4.2*SR)),.6,.25),.9)
sav('boss_rei_roar',room(mix(st(roar(1.6,80,36)),sf(57,[(0,2,'C2',120),(0,2,'G2',116)],bpm=60,vol=124,tail=1.2),sf(52,[(.2,2,'C3',110),(.2,2,'Eb3',106),(.2,2,'G3',104)],bpm=60,vol=118,tail=1.6,rv=.35),sf(19,[(0,2.5,'C2',110)],bpm=60,vol=120,tail=1.5),sf(47,[(0,.5,'C2',127),(.5,.5,'C2',127)],bpm=100,vol=127,tail=1.0),L=int(3.6*SR)),.7,.28),.95)
# título de dungeon: impacto orquestral (tímpano + metais + coro + sino) 
sav('dg_title',room(mix(sf(47,[(0,.5,'D2',127),(.12,.5,'D2',120)],bpm=100,vol=127,tail=1.5),sf(57,[(.05,2.5,'D2',120),(.05,2.5,'A2',116)],bpm=60,vol=124,tail=1.5),sf(61,[(.35,2.2,'D3',112),(.35,2.2,'F3',108),(.35,2.2,'A3',108)],bpm=60,vol=118,tail=1.5,rv=.3),sf(52,[(.9,2.5,'D4',104),(.9,2.5,'A4',100)],bpm=60,vol=112,tail=2.0,rv=.35),sf(14,[(.1,1.5,'D4',100),(1.8,1.5,'A3',90)],bpm=60,vol=112,tail=2.0),L=int(5.2*SR)),.8,.28),.92)
print('ok')
