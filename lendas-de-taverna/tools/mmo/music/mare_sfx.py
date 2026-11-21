"""Sons do SENHOR DAS MARÉS (caçada da Margem do Lago) — só GRAVAÇÕES REAIS CC0 (OpenGameArt) processadas:
água ("40 CC0 water splash/slime SFX", ondas de praia de jasinski e transitking, bolhas, rumble submarino, splash de bala de canhão)
+ rugidos reais (troll/fera/gorila, já usados no cervo) mais graves por troca de velocidade e misturados com gorgolejo de bolhas.
Fontes em assets/audio_src/mare (e ../cervo). Uso: /usr/bin/python3 mare_sfx.py [nome...] -> out/mare/*.ogg (copiar para assets/audio/sfx/)
Renderizado SEM poder ouvir: só níveis conferidos."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import cervo_real as CR
import cervo_sfx as C
from cervo_sfx import SR, st, at, mix, room, lp, hp
HERE = os.path.dirname(os.path.abspath(__file__))
CR.SRC = os.path.normpath(os.path.join(HERE, '..', '..', '..', 'assets', 'audio_src', 'mare'))
C.OUT = os.path.join(HERE, 'out', 'mare'); os.makedirs(C.OUT, exist_ok=True)
cut, speed, pk = CR.cut, CR.speed, CR.peaknorm
def full(n, fo=.05): x = CR.load(n).copy(); return cut(n, 0, len(x) / SR, .005, fo)
def L(d): return int(d * SR)
def fadein(x, d): n = min(len(x), L(d)); x = x.copy(); x[:n] *= np.linspace(0, 1, n); return x
CV = '../cervo/'

def roar():      # rugido do lago: troll grave + gorgolejo de bolhas por baixo
    v = speed(cut(CV + 'troll-roars_0.ogg', 7.1, 8.68, .03, .4), .7); b = speed(cut('bubbles-loop1.ogg', .2, 2.6, .2, .6), .8)
    return room(mix(at(st(pk(v)), 0, L(2.6)), at(st(pk(b)), .1, L(2.6)) * .35, at(st(pk(full('splash_04.ogg'))), .05, L(2.6)) * .4), .8, .2)
def hurt():
    v = speed(cut(CV + 'troll-roars_0.ogg', .06, .7), .82)
    return room(mix(at(st(pk(v)), 0, L(.9)), at(st(pk(full('splash_09.ogg'))), .02, L(.9)) * .45), .3, .1)
def die():
    v = speed(cut(CV + 'silent_beast_growl.mp3', .02, 2.64, .02, .6), .62); b = cut('bubbles-loop1.ogg', 0, 3.2, .3, 1.2)
    return room(mix(at(st(pk(v)), 0, L(4.2)), at(st(pk(speed(full('cannon_miss.ogg'), .75))), 1.6, L(4.2)) * .7, at(st(pk(b)), 1.8, L(4.2)) * .5), 1.0, .2)
def atk():       # grunhido antes do golpe
    v = speed(cut(CV + 'troll-roars_0.ogg', 3.62, 4.38), .8)
    return room(mix(at(st(pk(v)), 0, L(1.1))), .4, .12)
def slam():      # braço bate na praia: pancada real + coroa de água
    return room(mix(at(st(pk(speed(full(CV + 'bfh1_hit_02.ogg'), .8))), 0, L(1.6)), at(st(pk(speed(full('cannon_miss.ogg'), .85))), .02, L(1.6)) * .9,
                    at(st(pk(full('splash_04.ogg'))), 0, L(1.6)) * .7), .5, .16)
def sweep():     # muralha baixa de água varrendo a praia
    w = cut('wave_02_cc0-11505__transitking__wavesound.flac', .2, 2.0, .15, .5)
    return room(mix(at(st(pk(w)), 0, L(2.0)), at(st(pk(speed(full('splash_07.ogg'), .8))), .3, L(2.0)) * .6), .5, .15)
def cast():      # carregando a magia d'água: bolhas sobem + ronco grave
    b = fadein(cut('bubbles-loop1.ogg', .4, 1.6, .02, .3), .6); r = cut('deep_rumble_6s.ogg', 1, 2.2, .3, .4)
    return room(mix(at(st(pk(b)), 0, L(1.3)), at(st(pk(r)), 0, L(1.3)) * .7, at(st(pk(full('bubble_01.ogg'))), .7, L(1.3)) * .6), .6, .2)
def orb():       # orbe disparado
    return room(mix(at(st(pk(speed(full('bubble_01.ogg'), 1.1))), 0, L(.9)), at(st(pk(full('splash_10.ogg'))), .05, L(.9)) * .8), .4, .15)
def orbhit():
    return room(mix(at(st(pk(full('splash_02.ogg'))), 0, L(.8))), .3, .1)
def geyser():    # jato subindo do chão
    return room(mix(at(st(pk(speed(full('splash_01.ogg'), .85))), 0, L(1.7)), at(st(pk(full('bubble_02.ogg'))), 0, L(1.7)) * .6, at(st(pk(speed(full(CV + 'bfh1_hit_07.ogg'), .8))), 0, L(1.7)) * .4), .5, .15)
def grab():      # tentáculo d'água
    return room(mix(at(st(pk(cut('wave_01_cc0-11505__transitking__wavesound.flac', 0, 1.2, .01, .3))), 0, L(1.4)), at(st(pk(full('splash_11.ogg'))), .2, L(1.4)) * .8), .4, .15)
def whirl():     # redemoinho (5 s)
    w = cut('loop_water_02.ogg', 0, 5, .4, 1.0); b = cut('bubbles-loop1.ogg', 0, 4.8, .5, 1.0)
    return room(mix(at(st(pk(w)), 0, L(5.2)), at(st(pk(b)), .2, L(5.2)) * .45, at(st(pk(cut('deep_rumble_6s.ogg', 0, 5, .5, 1))), 0, L(5.2)) * .5), .6, .2)
def dive():      # mergulho: grande espirro + bolhas descendo
    return room(mix(at(st(pk(speed(full('cannon_miss.ogg'), .8))), 0, L(2.6)), at(st(pk(cut('bubbles-loop1.ogg', 0, 2.2, .05, .8))), .4, L(2.6)) * .6), .7, .2)
def tsunami():   # muralha d'água: duas ondas de praia graves + rumble
    w1 = speed(cut('wave_01_cc0-18363__jasinski__alkaibeach.flac', 0, 4, .3, .8), .7); w2 = speed(cut('wave_02_cc0-11505__transitking__wavesound.flac', 0, 3.2, .2, .8), .75)
    return room(mix(at(st(pk(w1)), 0, L(4.6)), at(st(pk(w2)), .3, L(4.6)) * .8, at(st(pk(cut('deep_rumble_6s.ogg', 0, 4.4, .6, 1))), 0, L(4.6)) * .9), .9, .22)
def emerge():    # sobe da água de uma vez
    return room(mix(at(st(pk(speed(full('splash_07.ogg'), .75))), 0, L(1.8)), at(st(pk(speed(full('splash_01.ogg'), .9))), .05, L(1.8)) * .8, at(st(pk(full('splash_04.ogg'))), 0, L(1.8)) * .7), .6, .18)
def bubbles():
    return room(mix(at(st(pk(cut('bubbles-loop1.ogg', 0, 2.4, .3, .8))), 0, L(2.5))), .5, .2)

SPEC = [('mare_roar', roar, -17.5, .95), ('mare_hurt', hurt, -19, .9), ('mare_die', die, -18.5, .93), ('mare_atk', atk, -19, .9), ('mare_slam', slam, -16.5, .95),
        ('mare_sweep', sweep, -18, .92), ('mare_cast', cast, -20, .88), ('mare_orb', orb, -19, .9), ('mare_orbhit', orbhit, -20, .88), ('mare_geyser', geyser, -18.5, .92),
        ('mare_grab', grab, -18.5, .92), ('mare_whirl', whirl, -21, .85), ('mare_dive', dive, -17.5, .95), ('mare_tsunami', tsunami, -16.5, .96),
        ('mare_emerge', emerge, -17.5, .95), ('mare_bubbles', bubbles, -22, .8)]
if __name__ == '__main__':
    only = set(sys.argv[1:])
    for nm, fn, rms, p in SPEC:
        if only and nm not in only: continue
        C.finish(nm, fn(), rms, p)
