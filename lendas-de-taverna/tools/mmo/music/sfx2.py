"""Efeitos sonoros de combate refeitos: camadas (clique + corpo + cauda), ressonâncias metálicas, corda de arco (Karplus-Strong) e fanfarras com instrumentos amostrados.
Uso: cd /tmp/aud && /usr/bin/python3 <este arquivo> -> /tmp/aud/out/sfx/*.ogg (copiar para lendas-de-taverna/assets/audio/sfx/)"""
import sys,os
sys.path.insert(0,'/tmp/aud')
src=open('/tmp/aud/sfx.py').read();exec(src[:src.index('# ---------- UI')])
R2=np.random.RandomState(11)
_orig_save=save_sfx
def save_sfx(name,x,peak=.85,fade=.015):
    x=np.asarray(x,np.float64)
    if name in ('hit_0','hit_1','crit','slash','equip','tr_equip','spell_hit','arrow_hit'):   # compressão leve: golpes mais cheios
        x=x/(np.max(np.abs(x))+1e-9);x=np.tanh(2.0*x)/np.tanh(2.0)
    return _orig_save(name,x,peak,fade)
def room(x,decay=.35,wet=.18):
    return reverb(x if x.ndim==2 else st(x),decay,wet,pre=.004)
def lp(x,f,order=2):
    b,a=signal.butter(order,f/(SR/2),'low');return signal.lfilter(b,a,x)
def ring(freqs,d,dec,amps=None):
    t=t_(d);amps=amps or [1]*len(freqs);return sum(a*np.sin(2*np.pi*f*t+R2.rand()*6)*np.exp(-t/(dec*(1+.2*i))) for i,(f,a) in enumerate(zip(freqs,amps)))
def ks(f,d,damp=.996):
    N=int(SR/f);buf=R2.randn(N)*.8;buf-=buf.mean();out=np.zeros(int(d*SR))
    for i in range(len(out)):
        out[i]=buf[i%N];buf[i%N]=damp*.5*(buf[i%N]+buf[(i+1)%N])
    return out
def impact(f0,body_dec,crack,low=48,tail=.12,g=1.0):
    d=.45;body=thud(d,f0,low,body_dec,1.0)
    click=hp(noise(.02),2500)*env(.02,.0005,.006)*.7
    snap=bp(noise(.09),600,3200)*env(.09,.001,crack)*.9
    tl=lp(noise(.3),700)*env(.3,.004,tail)*.35
    L=int(d*SR);x=pad_to(body,L)*.95+pad_to(click,L)+pad_to(snap,L)+pad_to(tl,L)
    return x*g
# ---------- golpes ----------
for k,(f0,dec,cr) in enumerate([(165,.085,.03),(135,.1,.04)]):
    x=impact(f0,dec,cr,tail=.1+.03*k)
    tm=sf(116,[(0,.3,'D2' if k==0 else 'F2',118)],bpm=120,vol=127,tail=.5)
    save_sfx(f'hit_{k}',mix(room(st(x),.3,.14),tm*.55,L=len(tm)),.9)
# crítico: impacto + estalo metálico + acorde de metais + tímpano
met=ring([1180,1950,3110,4300],.7,.12,[1,.7,.5,.3])*env(.7,.001,.2)*.35
brass=sf(56,[(0,.6,'D4',104),(0,.6,'A4',104),(0,.6,'D5',108)],bpm=130,tail=.9,rv=.2)
crit=mix(st(impact(150,.12,.05,low=38,g=1.1)),st(pad_to(met,int(.7*SR))),brass*.55,sf(47,[(0,.5,'D2',124)],bpm=120,tail=1.0,vol=127)*.75,L=int(1.4*SR))
save_sfx('crit',room(crit,.5,.16),.92)
# ar cortado e lâmina
sw=sweep_noise(.32,700,3600)*env(.32,.07,.13);sw2=sweep_noise(.32,1800,5200,'tri')*env(.32,.09,.1)*.4
save_sfx('swing',room(st(pad_to(sw+sw2,int(.4*SR))),.25,.1),.6)
bl=sweep_noise(.2,1800,6000,'ramp')*env(.2,.003,.055)
shing=ring([2200,3700,5100,6400],.6,.16,[1,.8,.6,.35])*env(.6,.001,.22)*.28
save_sfx('slash',mix(st(pad_to(bl,int(.3*SR))+pad_to(thud(.2,170,70,.05,.5),int(.3*SR))),st(shing),L=int(.8*SR)),.85)
save_sfx('miss',room(st(sweep_noise(.28,2400,4200)*env(.28,.06,.09)*.5),.2,.08),.4)
# arco: corda (Karplus-Strong) + vento da haste
tw=ks(196,.45,.9965)*np.exp(-t_(.45)/.2)*.7;ws=sweep_noise(.3,2400,5600,'ramp')*env(.3,.01,.1)*.5
save_sfx('bow',mix(st(pad_to(tw,int(.5*SR))),st(pad_to(ws,int(.5*SR)))),.75)
at=thud(.2,260,110,.04,.7);wd=bp(noise(.07),900,2600)*env(.07,.001,.02)
save_sfx('arrow_hit',mix(st(pad_to(at,int(.25*SR))+pad_to(wd,int(.25*SR))),st(pad_to(ring([420,880],.3,.05)*.15,int(.25*SR)))),.8)
# equipar: tilintar de metal + couro
eq=ring([1760,2640,3520],.5,.1,[1,.6,.4])*env(.5,.001,.12)*.5+pad_to(hp(noise(.1),1800)*env(.1,.002,.03)*.5,int(.5*SR))
save_sfx('equip',mix(st(pad_to(eq,int(.55*SR))),st(pad_to(thud(.16,180,90,.04,.5),int(.55*SR)))),.65)
save_sfx('tr_equip',mix(st(pad_to(eq,int(.55*SR))),st(pad_to(thud(.16,180,90,.04,.5),int(.55*SR)))),.6)
# cura: harpa e coro subindo
heal=mix(sf(46,[(i*.1,1.2,p,64+i*3) for i,p in enumerate(['C5','E5','G5','C6','E6'])],bpm=120,tail=1.4,rv=.3),sf(52,[(0,1.5,'C5',60),(0,1.5,'G5',58)],bpm=100,tail=1.3,rv=.3)*.5)
save_sfx('heal',heal,.7)
# morte: queda + violoncelo descendo
death=mix(st(thud(.6,130,34,.2,1.0)),sf(42,[(0,.8,'D3',96),(.5,1.2,'A2',92)],bpm=90,tail=1.8,rv=.3),sf(47,[(0,.5,'D2',120)],bpm=100,tail=1.5,vol=127)*.7,L=int(2.8*SR))
save_sfx('death',death,.85,.05)
# vitória: fanfarra de metais com tímpanos e harpa
vic=Score(110,seed=9);vic.inst(0,56,vol=108);vic.inst(1,57,vol=104);vic.inst(2,47,vol=110);vic.inst(3,46,vol=90)
for b,d,ps in [(0,.5,['D4','A4']),(.5,.5,['D4','A4']),(1,.5,['F#4','A4','D5']),(1.5,.5,['F#4','A4','D5']),(2,2.2,['A4','D5','F#5'])]:
    for p in ps:vic.note(0,b,d,n(p),100);vic.note(1,b,d,n(p)-12,92)
for b in (0,1,2):vic.note(2,b,.8,n('D2'),110)
for i,p in enumerate(['D5','F#5','A5','D6','F#6','A6']):vic.note(3,2+i*.15,1.2,n(p),70)
x=vic.render(5.5,tail=2.5);x=reverb(x,2.0,.25);save_sfx('victory',x,.82,.05)
# subir de nível: harpa em glissando + metais + brilho
lv=mix(sf(46,[(i*.07,1.4,p,66+i) for i,p in enumerate(['G4','B4','D5','G5','B5','D6','G6'])],bpm=120,tail=1.6,rv=.28),
       sf(56,[(.4,1.0,'G4',96),(.4,1.0,'D5',96),(.4,1.0,'G5',100)],bpm=120,tail=1.4,rv=.25)*.6,
       sf(9,[(.5,.8,'G6',80),(.62,.9,'D7',78)],bpm=120,tail=1.2,rv=.2)*.4)
save_sfx('levelup',lv,.8)
# acerto de magia: estalo cristalino + onda grave
sp=pad_to(thud(.3,200,70,.06,.6),int(.6*SR))+pad_to(ring([1568,2349,3136],.6,.15,[1,.7,.5])*env(.6,.002,.18)*.4,int(.6*SR))
save_sfx('spell_hit',room(st(sp),.4,.2),.7)
print('ok')
