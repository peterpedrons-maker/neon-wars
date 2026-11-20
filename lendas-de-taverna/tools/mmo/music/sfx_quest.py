"""Sons de missão do Hearthblade com instrumentos REAIS (GeneralUser GS): aceitar, objetivo cumprido, missão completa.
Uso: python3 sfx_quest.py  -> out/q_accept.ogg q_obj.ogg q_done.ogg  (copiar para lendas-de-taverna/assets/audio/sfx)"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib2 import *
OUT = os.environ.get('OUT', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')); os.makedirs(OUT, exist_ok=True)
def q_accept():   # pergaminho aceito: harpa subindo + cordas suaves (curto, discreto)
    sc = Score(120, seed=11)
    for c, p, v, pn in [(0, 46, 104, 58), (1, 48, 62, 64), (2, 9, 70, 70)]: sc.inst(c, p, vol=v, pan=pn)
    for k, m in enumerate(['G4', 'D5', 'G5']): sc.note(0, k * .32, 1.2, n(m), 84 - k * 3)
    for t in triad('G', 3): sc.note(1, .1, 2.0, t + 12, 54)
    sc.note(2, .96, 1.4, n('B5'), 64)
    x = reverb(sc.render(3, tail=1.6), 2.2, .3); x = x[:int(1.9 * SR)]; return fade(normalize(x, -20), .004, .7)
def q_obj():      # objetivo cumprido: duas notas de vibrafone/celesta
    sc = Score(132, seed=12)
    for c, p, v, pn in [(0, 11, 100, 60), (1, 8, 78, 68)]: sc.inst(c, p, vol=v, pan=pn)
    sc.note(0, 0, 1.0, n('E5'), 84); sc.note(1, 0.02, 1.0, n('E6'), 52)
    sc.note(0, .5, 1.6, n('B5'), 90); sc.note(1, .52, 1.6, n('B6'), 56)
    x = reverb(sc.render(2, tail=1.4), 1.8, .26); x = x[:int(1.5 * SR)]; return fade(normalize(x, -20.5), .003, .6)
def q_done():     # missão completa: trompas + cordas + harpa, resolvendo em maior (fanfarra curta)
    sc = Score(104, seed=13)
    for c, p, v, pn in [(0, 60, 104, 60), (1, 48, 80, 64), (2, 46, 100, 56), (3, 56, 74, 70), (4, 47, 96, 64), (5, 9, 70, 66)]: sc.inst(c, p, vol=v, pan=pn)
    sc.seq(0, 0, [('G4', .5), ('B4', .5), ('D5', 1), ('C5', .5), ('D5', .5), ('G5', 2.5)], 86, .98)
    sc.seq(3, 0, [('D4', .5), ('G4', .5), ('B4', 1), ('A4', .5), ('B4', .5), ('D5', 2.5)], 60, .98)
    for t in triad('G', 3): sc.note(1, 1.0, 3.2, t + 12, 66)
    for t in triad('C', 3): sc.note(1, 0, 1.0, t + 12, 56)
    for k, m in enumerate(['G3', 'D4', 'G4', 'B4', 'D5', 'G5']): sc.note(2, 2.0 + k * .12, 2.0, n(m), 78 - k * 2)
    sc.note(4, 0, 1.0, n('G2'), 96); sc.note(4, 2.0, 1.4, n('G2'), 104)
    sc.note(5, 2.2, 2.0, n('D6'), 66); sc.note(5, 2.4, 2.0, n('G6'), 66)
    x = reverb(sc.render(6, tail=2.2), 2.8, .34); x = x[:int(3.8 * SR)]; return fade(normalize(x, -19), .004, 1.2)
if __name__ == '__main__':
    for fn, f in ((q_accept, 'q_accept.ogg'), (q_obj, 'q_obj.ogg'), (q_done, 'q_done.ogg')):
        x = fn(); print(f, report(x)); save(x, os.path.join(OUT, f), 5)
