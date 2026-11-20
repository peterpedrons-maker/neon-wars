"""Sons do Ancião Cornalvo v2 — GRAVAÇÕES REAIS (OpenGameArt, CC0) processadas: troca de velocidade (voz maior/mais grave),
cortes, camadas e reverb de sala. Só os brilhos mágicos mantêm instrumentos reais amostrados (GeneralUser GS), em volume baixo.
Fontes em assets/audio_src/cervo (Trot, troll-roars, silent_beast_growl*, gorilla_*). Uso: /usr/bin/python3 cervo_real.py -> out/cervo/*.ogg
Renderizado SEM poder ouvir: só níveis/espectro conferidos."""
import sys, os, subprocess, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from scipy import signal
import cervo_sfx as C
from cervo_sfx import SR, st, at, mix, room, finish, inst, lp, hp, bp, noise, thud, crack, whoosh
SRC = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'assets', 'audio_src', 'cervo'))
_cache = {}
def load(name):
    if name in _cache: return _cache[name]
    tmp = tempfile.mktemp(suffix='.raw')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', os.path.join(SRC, name), '-ac', '1', '-ar', str(SR), '-f', 'f32le', tmp], check=True)
    x = np.fromfile(tmp, np.float32); os.remove(tmp); _cache[name] = x; return x
def cut(name, a, b, fi=.01, fo=.05):
    x = load(name)[int(a * SR):int(b * SR)].copy(); n = len(x)
    x *= np.minimum(np.arange(n) / max(fi * SR, 1), 1) * np.minimum((n - np.arange(n)) / max(fo * SR, 1), 1); return x
def speed(x, r):                       # varispeed: r<1 = mais grave e mais longo (animal maior)
    n = int(len(x) / r); return signal.resample(x, n).astype(np.float32) if n > 8 else x
def peaknorm(x, g=.9): return x / (np.abs(x).max() + 1e-9) * g
def hoof(i=0, r=1.0, g=1.0):           # um casco real do trote (de 1,35 s em diante, ~0,2 s entre batidas)
    t0 = [1.352, 1.544, 1.762, 1.945, 2.138, 2.332, 2.553, 2.733, 2.961, 3.165, 3.385, 3.583][i % 12]
    return speed(cut('Trot.ogg', t0 - .015, t0 + .2, .002, .12), r) * g
def L_(d): return int(d * SR)
CHOIR, TIMP, TUBE, GLOCK, CELESTA = C.CHOIR, C.TIMP, C.TUBE, C.GLOCK, C.CELESTA

def atk():
    L = L_(1.0)
    v = speed(cut('gorilla_snarl_02.ogg', .06, 1.1), .78) * 1.0
    h = hoof(3, .7, 1.2)
    return room(mix(at(st(peaknorm(v)), .02, L), at(st(h), 0, L) * .8, L=L), .35, .12)
def hurt():
    L = L_(.8)
    v = speed(cut('silent_beast_growl_1.mp3', .02, .96), 1.08)
    v2 = speed(cut('gorilla_roar.ogg', .04, .66), 1.3) * .5
    return room(mix(at(st(peaknorm(v)), 0, L), at(st(peaknorm(v2)), .03, L) * .5, L=L), .3, .1)
def die():
    L = L_(3.4)
    v = speed(cut('silent_beast_growl.mp3', .02, 2.64, .02, .5), .72)
    body = at(st(hoof(5, .45, 1.6)), 1.5, L) + at(st(thud(.8, 80, 30, .25, .5)), 1.55, L)
    bells = inst(TUBE, [(0, 2, 'E5', 55), (1, 2, 'B4', 48)], bpm=70, vol=85, tail=2.5, rt=3.0, rv=.4)
    return room(mix(at(st(peaknorm(v)), .05, L), body, at(bells, 1.2, L) * .25, L=L), 1.0, .2)
def engage():
    L = L_(2.6)
    v = speed(cut('troll-roars_0.ogg', 7.1, 8.68), .85)
    v2 = speed(cut('troll-roars_0.ogg', 3.62, 4.38), 1.05) * .6
    tp = inst(TIMP, [(0, .6, 'E2', 125)], bpm=100, vol=120, tail=1.0, rt=1.6, rv=.25)
    bell = inst(TUBE, [(0, 2.5, 'E3', 90)], bpm=60, vol=100, tail=2.0, rt=3.2, rv=.4)
    return room(mix(at(st(peaknorm(v)), .1, L), at(st(peaknorm(v2)), .08, L) * .45, at(tp, 0, L) * .5, at(bell, 0, L) * .25, L=L), 1.1, .22)
def stomp():
    L = L_(1.4)
    hs = at(st(hoof(2, .55, 1.8)), 0, L) + at(st(hoof(7, .5, 2.0)), .34, L)
    tp = inst(TIMP, [(0, .5, 'C2', 127), (.68, .5, 'G1', 127)], bpm=120, vol=127, tail=1.0, rt=1.4, rv=.2)
    wood = sum(at(st(crack(1500 + 500 * C.R.rand(), .015 + .02 * C.R.rand(), .5)), .36 + .07 * i, L) for i in range(8))
    gl = inst(GLOCK, [(0, .5, 'E6', 70), (.1, .5, 'B6', 62)], bpm=120, vol=90, tail=1.2, rt=1.8, rv=.35)
    return room(mix(hs, at(tp, 0, L) * .45, wood * .6, at(gl, .4, L) * .25, L=L), .6, .18)
def charge():
    L = L_(1.5)
    sn = speed(cut('gorilla_grunt.ogg', .02, .9), 1.0) * .8
    run = sum(at(st(hoof(i, .85 + .0 * i, .8 + .07 * i)), .22 + i * (.17 - i * .008), L) for i in range(7))
    gl = inst(GLOCK, [(i * .08, .4, 72 + i * 2, 66 + i * 2) for i in range(8)], bpm=120, vol=95, tail=1.2, rt=1.8, rv=.35)
    return room(mix(at(st(peaknorm(sn)), 0, L) * .7, run, at(gl, .4, L) * .25, L=L), .5, .15)
def bellow():
    L = L_(3.2)
    v = speed(cut('troll-roars_0.ogg', 7.1, 8.68, .08, .5), .62)
    ch = inst(CHOIR, [(0, 3, 'E3', 80), (0, 3, 'B3', 74)], bpm=60, vol=90, tail=2.0, rt=3.0, rv=.4)
    ce = inst(CELESTA, [(.6 + i * .25, .6, 76 + 5 * (i % 4) + 12 * (i // 4), 58 - i * 2) for i in range(8)], bpm=120, vol=90, tail=1.8, rt=2.5, rv=.4)
    return room(mix(at(st(peaknorm(v)), .08, L), at(ch, 0, L) * .28, at(ce, .2, L) * .3, L=L), 1.4, .24)

if __name__ == '__main__':
    only = set(sys.argv[1:])
    SPEC = [('cervo_atk', atk, -18.5, .9), ('cervo_hurt', hurt, -19, .9), ('cervo_die', die, -19, .92), ('cervo_engage', engage, -17.5, .95),
            ('cervo_stomp', stomp, -17.5, .95), ('cervo_charge', charge, -18.5, .92), ('cervo_bellow', bellow, -18.5, .93),
            ('cervo_step', lambda: room(mix(at(st(hoof(4, .8, 1.0)), 0, L_(.32)), L=L_(.32)), .2, .08), -24, .8)]
    for nm, fn, rms, pk in SPEC:
        if only and nm not in only: continue
        finish(nm, fn(), rms, pk)
