"""Sons do Ancião Cornalvo (cervo raro da Planície): voz por formantes (bramido grave de cervo) + instrumentos REAIS amostrados
(GeneralUser GS: sinos tubulares, glockenspiel, celesta, harpa, tímpano) para a camada mágica dourada + madeira/raízes por ruído filtrado.
Uso: /usr/bin/python3 cervo_sfx.py  -> out/cervo/*.ogg  (copiar para lendas-de-taverna/assets/audio/sfx/)
Renderizado SEM poder ouvir: só níveis/espectro conferidos. Ajustar com o dono."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from scipy import signal
from lib2 import Score, n, reverb, normalize, fade, save, report, SR
OUT = os.environ.get('OUT', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out', 'cervo')); os.makedirs(OUT, exist_ok=True)
R = np.random.RandomState(7)
def t_(d): return np.arange(int(d * SR)) / SR
def noise(d): return R.randn(int(d * SR))
def bp(x, lo, hi, o=2):
    b, a = signal.butter(o, [lo / (SR / 2), min(hi, SR / 2 - 100) / (SR / 2)], 'band'); return signal.lfilter(b, a, x)
def lp(x, f, o=2):
    b, a = signal.butter(o, f / (SR / 2), 'low'); return signal.lfilter(b, a, x)
def hp(x, f, o=2):
    b, a = signal.butter(o, f / (SR / 2), 'high'); return signal.lfilter(b, a, x)
def env(d, a=.005, dec=.1):
    t = t_(d); return np.minimum(t / max(a, 1e-4), 1) * np.exp(-t / dec)
def st(x, w=0.0):
    x = np.asarray(x, np.float32)
    return np.stack([x, np.roll(x, int(w * SR))], 1) if x.ndim == 1 else x
def pad(x, L):
    x = np.asarray(x);
    if x.ndim == 1: y = np.zeros(L, np.float32); y[:min(L, len(x))] = x[:L]; return y
    y = np.zeros((L, x.shape[1]), np.float32); y[:min(L, len(x))] = x[:L]; return y
def at(x, t0, L):                              # coloca x começando em t0 (s) num vetor de tamanho L
    y = np.zeros((L,) + x.shape[1:], np.float32); i = int(t0 * SR); m = min(len(x), L - i)
    if m > 0: y[i:i + m] = x[:m]
    return y
def formant(x, fs, qs, gains):
    out = np.zeros_like(x)
    for f, q, g in zip(fs, qs, gains):
        b, a = signal.iirpeak(min(f, SR / 2 - 200) / (SR / 2), q); out += g * signal.lfilter(b, a, x)
    return out
def voice(f0c, d, fs, qs=(4, 5, 6), gains=(1, .8, .4), rough=.5, a=.03, dec=None, breath=.12, trem=0):
    """fonte glotal serrilhada com jitter + formantes: bramido de cervo (grave, rouco, com vibrato lento)"""
    t = t_(d); f = f0c(t) * (1 + .012 * np.sin(2 * np.pi * 5.5 * t)); f = f * (1 + rough * .05 * R.randn(len(t)).cumsum() / np.sqrt(np.arange(1, len(t) + 1)))
    ph = np.cumsum(f) / SR; s = 2 * (ph % 1) - 1
    s *= 1 - rough * .55 * (.5 + .5 * np.sin(2 * np.pi * np.cumsum(np.full(len(t), 34 + 8 * R.rand())) / SR))
    if trem: s *= 1 - trem * (.5 + .5 * np.sin(2 * np.pi * 7 * t))
    s = formant(s, fs, qs, gains); s = s / (np.abs(s).max() + 1e-9)
    e = np.minimum(t / a, 1) * np.exp(-t / (dec or d * .6)); e *= np.minimum((d - t) / .06, 1)
    return lp(s * .9 + lp(hp(noise(d), 300), 2500) * breath * .5, 3400) * e
def glide(a, b, d, c=1.0): return lambda t: a + (b - a) * np.clip(t / d, 0, 1) ** c
def thud(d=.5, f0=110, f1=38, dec=.12, g=1.0):
    t = t_(d); f = f1 + (f0 - f1) * np.exp(-t / .06); x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / dec)
    return (x + lp(noise(d), 260) * np.exp(-t / .03) * .6) * g
def crack(f=2200, dec=.012, g=1.0):          # estalo de madeira
    d = .12; return bp(noise(d), f * .5, f * 1.6) * env(d, .0004, dec) * g
def creak(d=.5, f0=240, f1=420, g=.5):       # rangido de madeira (casca esticando)
    t = t_(d); f = f0 + (f1 - f0) * (t / d) + 30 * np.sin(2 * np.pi * 23 * t); x = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * (.5 + .5 * np.sin(2 * np.pi * 31 * t))
    return bp(x, 180, 1800) * np.minimum(t / .05, 1) * np.minimum((d - t) / .08, 1) * g
def whoosh(d, f0, f1, g=.5, a=.4):            # vento: ruído filtrado com varredura
    t = t_(d); x = noise(d); out = np.zeros(len(t)); k = 24
    for i in range(k):
        s, e_ = i * len(t) // k, (i + 1) * len(t) // k; fc = f0 + (f1 - f0) * (i / k)
        out[s:e_] = bp(x, fc * .7, fc * 1.4)[s:e_]
    e = np.sin(np.pi * np.clip(t / d, 0, 1) ** a) ** 1.4; return out * e * g
def inst(prog, notes, bpm=120, vol=115, tail=1.5, rv=.28, rt=1.8, pan=64, drums=False):
    sc = Score(bpm, seed=3); sc.inst(0, prog, vol=vol, pan=pan, drums=drums)
    last = 0
    for b, dur, nm, v in notes:
        sc.note(0, b, dur, n(nm) if isinstance(nm, str) else nm, v); last = max(last, b + dur)
    x = sc.render(last + .2, tail=tail); return reverb(x, rt, rv) if rv else x
def room(x, secs=.5, wet=.18): return reverb(st(x), secs, wet, pre=.004)
def mix(*xs, L=None):
    L = L or max(len(x) for x in xs); y = np.zeros((L, 2), np.float32)
    for x in xs:
        x = st(x); m = min(L, len(x)); y[:m] += x[:m]
    return y
def finish(name, x, rms=-19.0, peak=.9, a=.003, b=.12, q=5):
    x = fade(normalize(np.asarray(x, np.float32), rms, peak), a, b); path = os.path.join(OUT, name + '.ogg'); save(x, path, q); print(name.ljust(14), report(x)); return x

BELL, GLOCK, CELESTA, HARP, TIMP, CHOIR, TUBE, MUSICBOX = 14, 9, 8, 46, 47, 52, 14, 10   # programas GM

# 1) ATAQUE (chifrada): ronco curto e seco + tinido da galhada
def atk():
    L = int(.9 * SR)
    v = voice(glide(150, 92, .35), .5, (420, 900, 2300), rough=.7, a=.02, dec=.2, breath=.18)
    sn = bp(noise(.2), 300, 1500) * env(.2, .01, .07) * .5
    ch = inst(GLOCK, [(0, .3, 'E6', 84), (.12, .3, 'B6', 70)], vol=105, tail=.6, rt=1.2, rv=.3)
    return room(mix(at(st(v), .05, L), at(st(sn), 0, L), at(ch, .06, L) * .5, L=L), .35, .14)
# 2) DANO: grito agudo e curto (cervo ferido), pouco metálico
def hurt():
    L = int(.7 * SR)
    v = voice(glide(420, 210, .3), .4, (700, 1500, 2900), rough=.35, a=.015, dec=.14, breath=.2, trem=.25)
    ch = inst(CELESTA, [(0, .2, 'A6', 70)], vol=90, tail=.5, rt=1.0, rv=.3)
    return room(mix(at(st(v), 0, L), at(ch, .02, L) * .35, L=L), .3, .12)
# 3) MORTE: gemido longo caindo, expiração, queda do corpo e sinos dourados que se apagam
def die():
    L = int(3.2 * SR)
    v = voice(glide(200, 55, 1.5, 1.4), 1.8, (380, 800, 2000), rough=.6, a=.05, dec=.9, breath=.25)
    ex = whoosh(1.0, 700, 250, .22, .5)
    body = thud(.8, 90, 32, .25, 1.0)
    bells = inst(TUBE, [(0, 2, 'E5', 70), (1, 2, 'B4', 62), (2, 2.5, 'E4', 54)], bpm=70, vol=100, tail=2.5, rt=3.0, rv=.4)
    glock = inst(GLOCK, [(0, .5, 'B6', 66), (.6, .5, 'E6', 60), (1.2, .5, 'B5', 52), (1.8, .5, 'E5', 44)], bpm=80, vol=96, tail=2.0, rt=2.5, rv=.4)
    return room(mix(at(st(v), .05, L), at(st(ex), .9, L), at(st(body), 1.35, L), at(bells, .6, L) * .5, at(glock, .7, L) * .45, L=L), 1.0, .22)
# 4) ENFURECE: rugido ascendente + sino grave + glissando de glockenspiel
def engage():
    L = int(2.4 * SR)
    v = voice(glide(80, 135, .5, .8), 1.5, (400, 850, 2100), rough=1.0, a=.06, dec=.9, breath=.2)
    v2 = voice(glide(160, 270, .5, .8), 1.5, (500, 1100, 2400), rough=.8, a=.07, dec=.8, breath=.12) * .45
    bell = inst(TUBE, [(0, 2.5, 'E3', 100), (0, 2.5, 'B3', 90)], bpm=60, vol=118, tail=2.0, rt=3.2, rv=.4)
    gl = inst(GLOCK, [(.1 + i * .1, .4, 'E5' if False else 76 + i * 3, 88 - i * 3) for i in range(8)], bpm=120, vol=110, tail=1.8, rt=2.0, rv=.35)
    tp = inst(TIMP, [(0, .6, 'E2', 127), (.5, .6, 'E2', 120)], bpm=100, vol=127, tail=1.0, rt=1.6, rv=.25)
    return room(mix(at(st(v), .1, L), at(st(v2), .1, L), at(bell, 0, L) * .5, at(gl, .5, L) * .45, at(tp, 0, L) * .7, at(st(thud(.6, 100, 34, .2)), 0, L), L=L), 1.1, .24)
# 5) PISADA DO ANCIÃO: dois cascos pesados + madeira estalando (raízes rompendo) + ressonância dourada
def stomp():
    L = int(1.4 * SR)
    th = at(st(thud(.6, 120, 36, .16, 1.0)), 0, L) + at(st(thud(.7, 95, 30, .2, 1.1)), .34, L)
    tp = inst(TIMP, [(0, .5, 'C2', 127), (.34 * 2, .5, 'G1', 127)], bpm=120, vol=127, tail=1.0, rt=1.4, rv=.2)
    wood = sum(at(st(crack(1500 + 500 * R.rand(), .015 + .02 * R.rand(), .6)), .36 + .07 * i, L) for i in range(9)) + sum(at(st(creak(.35, 200, 520, .35)), .4 + .05 * i, L) for i in range(2))
    gl = inst(GLOCK, [(.0, .5, 'E6', 78), (.1, .5, 'B6', 70), (.2, .5, 'E7', 64)], bpm=120, vol=100, tail=1.2, rt=1.8, rv=.35)
    return room(mix(th, at(tp, 0, L) * .6, wood * .8, at(gl, .4, L) * .45, L=L), .6, .2)
# 6) INVESTIDA: bufo + galope crescente + varredura de glockenspiel ascendente (galhada espectral)
def charge():
    L = int(1.4 * SR)
    snort = bp(noise(.28), 250, 1400) * env(.28, .01, .09) * .9
    hoofs = sum(at(st(thud(.18, 150 + 30 * (i % 2), 60, .04, .5 + .08 * i)), .25 + i * (.16 - i * .006), L) for i in range(6))
    run = whoosh(1.0, 300, 1800, .25, .8)
    gl = inst(GLOCK, [(i * .08, .4, 72 + i * 2, 70 + i * 2) for i in range(10)], bpm=120, vol=108, tail=1.2, rt=1.8, rv=.35)
    v = voice(glide(120, 175, .4), .45, (420, 900, 2200), rough=.8, a=.03, dec=.25, breath=.15)
    return room(mix(at(st(snort), 0, L), hoofs, at(st(run), .25, L), at(gl, .4, L) * .5, at(st(v), .12, L) * .6, L=L), .5, .16)
# 7) BRAMIDO: chamado longo e grave, harmônicos em coro, aurora de celesta/sinos e vento
def bellow():
    L = int(3.0 * SR)
    v = voice(lambda t: 105 + 45 * np.sin(np.pi * np.clip(t / 2.0, 0, 1)) - 25 * np.clip((t - 1.6) / .5, 0, 1), 2.1, (380, 800, 2000), rough=.9, a=.12, dec=1.6, breath=.14)
    v2 = voice(lambda t: 210 + 90 * np.sin(np.pi * np.clip(t / 2.0, 0, 1)), 2.1, (500, 1000, 2500), rough=.6, a=.15, dec=1.5, breath=.08) * .4
    ch = inst(CHOIR, [(0, 3, 'E3', 90), (0, 3, 'B3', 84), (.2, 3, 'E4', 80)], bpm=60, vol=100, tail=2.0, rt=3.0, rv=.4)
    ce = inst(CELESTA, [(.4 + i * .22, .6, 76 + 5 * (i % 4) + 12 * (i // 4), 70 - i * 2) for i in range(10)], bpm=120, vol=100, tail=1.8, rt=2.5, rv=.4)
    tb = inst(TUBE, [(0, 3, 'E4', 70)], bpm=60, vol=100, tail=2.5, rt=3.0, rv=.4)
    wind = whoosh(2.8, 500, 2400, .2, .6)
    tp = inst(TIMP, [(0, .6, 'E2', 120)], bpm=100, vol=120, tail=1.0, rt=1.6, rv=.25)
    return room(mix(at(st(v), .08, L), at(st(v2), .08, L), at(ch, 0, L) * .5, at(ce, .1, L) * .5, at(tb, 0, L) * .35, at(st(wind), .1, L), at(tp, 0, L) * .5, L=L), 1.4, .26)
# 8) COURAÇA DE CASCA: casca rangendo e estalando para cima + glissando de harpa quente
def bark():
    L = int(1.8 * SR)
    cr = creak(1.0, 180, 520, .6)
    ck = sum(at(st(crack(900 + 700 * R.rand(), .02, .6)), .08 + i * .09, L) for i in range(9))
    hp_ = inst(HARP, [(i * .09, .8, 55 + 3 * i + (2 if i % 2 else 0), 76 + i) for i in range(12)], bpm=120, vol=112, tail=1.5, rt=2.0, rv=.3)
    ch = inst(CHOIR, [(.3, 3, 'E3', 80), (.3, 3, 'B3', 72)], bpm=70, vol=90, tail=1.5, rt=2.5, rv=.35)
    sw = whoosh(1.2, 400, 1500, .16, .7)
    return room(mix(at(st(cr), 0, L), ck, at(hp_, .1, L) * .55, at(ch, 0, L) * .35, at(st(sw), .2, L), at(st(thud(.4, 80, 40, .1)), .85, L) * .6, L=L), .6, .2)
# 9) RAÍZES ANCESTRAIS: cristais dourados brotando em sequência (5 golpes) + madeira estalando
def grove():
    L = int(1.7 * SR)
    ch = inst(GLOCK, [(i * .38, .5, 79 + 4 * (i % 3) + (i // 3) * 5, 90 - i * 3) for i in range(5)], bpm=100, vol=110, tail=1.5, rt=2.2, rv=.38)
    tb = inst(TUBE, [(0, 2, 'B4', 70), (1, 2, 'E5', 70)], bpm=70, vol=100, tail=1.5, rt=2.5, rv=.38)
    wood = sum(at(st(crack(1800 + 400 * R.rand(), .018, .7)), i * .38 + .03 * R.rand(), L) + at(st(thud(.25, 100, 40, .06, .6)), i * .38, L) for i in range(5))
    return room(mix(at(ch, 0, L) * .65, at(tb, .2, L) * .4, wood, at(st(whoosh(1.5, 600, 2600, .1, .5)), .1, L), L=L), .8, .24)
# 10) IMUNE: ping cristalino curto (nada passa)
def imune():
    ch = inst(TUBE, [(0, .6, 'E6', 96)], bpm=120, vol=112, tail=1.0, rt=1.2, rv=.3)
    gl = inst(GLOCK, [(0, .4, 'B6', 90), (.05, .4, 'E7', 80)], bpm=120, vol=104, tail=.8, rt=1.0, rv=.3)
    return room(mix(ch * .6, gl * .6), .4, .2)
# 11) PASSO: casco macio (pisada de cervo grande no capim)
def step():
    L = int(.32 * SR)
    return room(mix(at(st(thud(.22, 135, 55, .05, .7)), 0, L), at(st(lp(noise(.1), 900) * env(.1, .002, .025) * .4), 0, L), L=L), .2, .08)
# 12) BRILHO: cintilar discreto da galhada dourada em repouso (aura mágica)
def glint():
    gl = inst(CELESTA, [(0, .5, 'E6', 62), (.35, .5, 'G6', 52), (.7, .5, 'B6', 46)], bpm=120, vol=84, tail=1.5, rt=2.2, rv=.4)
    return room(gl, .8, .25)

if __name__ == '__main__':
    only = set(sys.argv[1:])
    SPEC = [('cervo_atk', atk, -18.5, .9), ('cervo_hurt', hurt, -19, .9), ('cervo_die', die, -19, .92), ('cervo_engage', engage, -17.5, .95),
            ('cervo_stomp', stomp, -17.5, .95), ('cervo_charge', charge, -18.5, .92), ('cervo_bellow', bellow, -18.5, .93), ('cervo_bark', bark, -19.5, .9),
            ('cervo_grove', grove, -19.5, .9), ('cervo_imune', imune, -21, .85), ('cervo_step', step, -24, .8), ('cervo_glint', glint, -26, .8)]
    for nm, fn, rms, pk in SPEC:
        if only and nm not in only: continue
        finish(nm, fn(), rms, pk)
