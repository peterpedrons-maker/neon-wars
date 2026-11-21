"""Sons do GIGANTE DAS COLINAS (humanoide enorme) — só gravações reais CC0 (assets/audio_src/cervo e mare), bem mais graves (varispeed) e com reverb de vale:
passos = pancadas de terra + rumble; pisada/soco no chão = impacto + pedras; rugido = troll/gorila bem lentos; dor = grunhido de gorila grave; ajoelhar e morrer = impactos + rumble.
Uso: /usr/bin/python3 gigante_sfx.py -> out/gigante/*.ogg (copiar para assets/audio/sfx/gig_*.ogg). Sem poder ouvir: só níveis conferidos."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import cervo_real as CR
import cervo_sfx as C
from cervo_sfx import SR, st, at, mix, room
HERE = os.path.dirname(os.path.abspath(__file__)); A = os.path.normpath(os.path.join(HERE, '..', '..', '..', 'assets', 'audio_src'))
CR.SRC = os.path.join(A, 'cervo'); C.OUT = os.path.join(HERE, 'out', 'gigante'); os.makedirs(C.OUT, exist_ok=True)
cut, speed, pk = CR.cut, CR.speed, CR.peaknorm
def full(n, fo=.05): x = CR.load(n); return cut(n, 0, len(x) / SR, .005, fo)
def L(d): return int(d * SR)
M = '../mare/'
def rumble(a, b, fi=.1, fo=.8): return st(pk(cut(M + 'deep_rumble_6s.ogg', a, b, fi, fo)))
def step():
    return room(mix(at(st(pk(speed(full('bfh1_hit_02.ogg'), .38))), 0, L(1.8)), at(st(pk(speed(full('bfh1_hit_07.ogg'), .5))), .015, L(1.8)) * .6, at(rumble(0, 1.4, .01, .7), 0, L(1.8)) * .8), 1.2, .24)
def stomp():
    return room(mix(at(st(pk(speed(full('bfh1_hit_02.ogg'), .32))), 0, L(2.8)), at(st(pk(speed(full('bfh1_hit_07.ogg'), .42))), .03, L(2.8)), at(st(pk(speed(full('bfh1_rock_falling_01.ogg'), .55))), .12, L(2.8)) * .8,
                    at(rumble(0, 2.4, .01, 1.0), 0, L(2.8)) * .9), 1.4, .28)
def punch():
    return room(mix(at(st(pk(speed(full('bfh1_hit_07.ogg'), .34))), 0, L(2.4)), at(st(pk(speed(full('bfh1_hit_02.ogg'), .45))), .04, L(2.4)), at(st(pk(speed(full('bfh1_rock_falling_03.ogg'), .5))), .14, L(2.4)) * .7,
                    at(rumble(0, 2.0, .01, .9), 0, L(2.4)) * .8), 1.2, .26)
def roar():
    return room(mix(at(st(pk(speed(cut('troll-roars_0.ogg', 7.1, 8.68, .08, .6), .36))), 0, L(4.6)), at(st(pk(speed(cut('gorilla_roar.ogg', .04, .66, .03, .3), .42))), .1, L(4.6)) * .6,
                    at(rumble(0, 4.2, .4, 1.2), 0, L(4.6)) * .7), 1.8, .3)
def hurt():
    return room(mix(at(st(pk(speed(cut('gorilla_grunt.ogg', .02, .9, .01, .2), .46))), 0, L(1.8)), at(st(pk(speed(full('bfh1_hit_02.ogg'), .6))), .02, L(1.8)) * .4), .7, .2)
def kneel():
    return room(mix(at(st(pk(speed(full('bfh1_hit_02.ogg'), .3))), 0, L(3.6)), at(st(pk(speed(full('bfh1_hit_07.ogg'), .36))), .55, L(3.6)), at(st(pk(speed(full('bfh1_rock_falling_01.ogg'), .5))), .2, L(3.6)) * .8,
                    at(st(pk(speed(full('bfh1_rock_falling_03.ogg'), .45))), .7, L(3.6)) * .6, at(rumble(0, 3.2, .02, 1.2), 0, L(3.6)) * .9), 1.6, .3)
def die():
    return room(mix(at(st(pk(speed(cut('troll-roars_0.ogg', 7.1, 8.68, .08, .9), .32))), 0, L(7.0)), at(st(pk(speed(full('bfh1_hit_02.ogg'), .28))), 3.2, L(7.0)), at(st(pk(speed(full('bfh1_hit_07.ogg'), .34))), 3.5, L(7.0)) * .8,
                    at(st(pk(speed(full('bfh1_rock_falling_01.ogg'), .45))), 3.3, L(7.0)) * .8, at(rumble(0, 6.0, .3, 2.0), 0, L(7.0)) * .8), 2.0, .32)
SPEC = [('gig_step', step, -18.5, .9), ('gig_stomp', stomp, -15.5, .96), ('gig_punch', punch, -15.5, .96), ('gig_roar', roar, -16.5, .95), ('gig_hurt', hurt, -18, .92), ('gig_kneel', kneel, -15.5, .96), ('gig_die', die, -16.5, .96)]
if __name__ == '__main__':
    only = set(sys.argv[1:])
    for nm, fn, rms, p in SPEC:
        if only and nm not in only: continue
        C.finish(nm, fn(), rms, p)
