"""Sons do COLOSSO DAS COLINAS — só gravações reais CC0 (fontes em assets/audio_src/cervo e mare): pancadas/pedras (pack 75 CC0 breaking/falling/hit),
rugidos de troll/fera/gorila, rumble submarino e ondas (para o chute). Tudo mais grave (varispeed) e com reverb de sala grande.
Uso: /usr/bin/python3 colosso_sfx.py -> out/colosso/*.ogg (copiar para assets/audio/sfx/col_*.ogg). Sem poder ouvir: só níveis conferidos."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import cervo_real as CR
import cervo_sfx as C
from cervo_sfx import SR, st, at, mix, room
HERE = os.path.dirname(os.path.abspath(__file__)); A = os.path.normpath(os.path.join(HERE, '..', '..', '..', 'assets', 'audio_src'))
CR.SRC = os.path.join(A, 'cervo'); C.OUT = os.path.join(HERE, 'out', 'colosso'); os.makedirs(C.OUT, exist_ok=True)
cut, speed, pk = CR.cut, CR.speed, CR.peaknorm
def full(n, fo=.05): x = CR.load(n); return cut(n, 0, len(x) / SR, .005, fo)
def L(d): return int(d * SR)
M = '../mare/'
def roar():
    v = speed(cut('troll-roars_0.ogg', 7.1, 8.68, .06, .5), .5)
    return room(mix(at(st(pk(v)), 0, L(3.4)), at(st(pk(cut(M + 'deep_rumble_6s.ogg', 0, 3, .4, .8))), 0, L(3.4)) * .6), 1.4, .28)
def step():
    return room(mix(at(st(pk(speed(full('bfh1_hit_02.ogg'), .55))), 0, L(1.4)), at(st(pk(cut(M + 'deep_rumble_6s.ogg', 0, 1.2, .01, .6))), 0, L(1.4)) * .7), 1.0, .22)
def stomp():
    return room(mix(at(st(pk(speed(full('bfh1_hit_02.ogg'), .5))), 0, L(2.0)), at(st(pk(speed(full('bfh1_hit_07.ogg'), .55))), .04, L(2.0)), at(st(pk(speed(full('bfh1_rock_falling_01.ogg'), .6))), .1, L(2.0)) * .7,
                    at(st(pk(speed(full('bfh1_rock_falling_03.ogg'), .55))), .3, L(2.0)) * .5), 1.0, .22)
def sweep():
    return room(mix(at(st(pk(speed(cut(M + 'wave_02_cc0-11505__transitking__wavesound.flac', .2, 2.2, .1, .4), .6))), 0, L(2.6)), at(st(pk(speed(full('bfh1_rock_falling_03.ogg'), .6))), .9, L(2.6)) * .8), .9, .2)
def fall():
    return room(mix(at(st(pk(speed(full('bfh1_hit_02.ogg'), .45))), 0, L(3.2)), at(st(pk(speed(full('bfh1_rock_falling_01.ogg'), .5))), .1, L(3.2)), at(st(pk(speed(full('bfh1_rock_falling_03.ogg'), .45))), .5, L(3.2)) * .8,
                    at(st(pk(cut(M + 'deep_rumble_6s.ogg', 0, 3, .05, 1))), 0, L(3.2)) * .6), 1.4, .28)
def bite():
    return room(mix(at(st(pk(speed(cut('gorilla_roar.ogg', .04, .66), .6))), 0, L(1.2)), at(st(pk(speed(full('bfh1_hit_07.ogg'), .6))), .05, L(1.2))), .6, .2)
def spit():
    return room(mix(at(st(pk(speed(cut('gorilla_grunt.ogg', .02, .9), .55))), 0, L(1.4)), at(st(pk(speed(full('bfh1_rock_falling_01.ogg'), .9))), .25, L(1.4)) * .6), .5, .18)
def die():
    v = speed(cut('troll-roars_0.ogg', 7.1, 8.68, .06, .8), .42)
    return room(mix(at(st(pk(v)), 0, L(5.2)), at(st(pk(speed(full('bfh1_hit_02.ogg'), .4))), 2.4, L(5.2)), at(st(pk(speed(full('bfh1_rock_falling_01.ogg'), .45))), 2.6, L(5.2)) * .8,
                    at(st(pk(cut(M + 'deep_rumble_6s.ogg', 0, 5, .3, 1.5))), 0, L(5.2)) * .6), 1.8, .3)
SPEC = [('col_roar', roar, -17, .95), ('col_step', step, -19, .9), ('col_stomp', stomp, -16.5, .96), ('col_sweep', sweep, -18.5, .92), ('col_fall', fall, -16.5, .96),
        ('col_bite', bite, -17.5, .94), ('col_spit', spit, -19, .9), ('col_die', die, -17, .95)]
if __name__ == '__main__':
    only = set(sys.argv[1:])
    for nm, fn, rms, p in SPEC:
        if only and nm not in only: continue
        C.finish(nm, fn(), rms, p)
