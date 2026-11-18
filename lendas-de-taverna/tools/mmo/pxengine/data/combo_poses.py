"""Ataques de combo REDESENHADOS por pose (guerreiro e ladino): cada golpe tem sua propria trajetoria de lamina, postura e pernas.
Convencao do angulo da arma (chibi.py): 0 = aponta para BAIXO, 90 = frente na horizontal, 180 = CIMA, 270 = para TRAS.
Cada ataque = 10 poses-chave (0-4 antecipacao, 5 o corte rapido, 6 IMPACTO, 7-9 recuperacao); 'attack(view, ap, nome)' devolve 20 quadros com o golpe no quadro 11."""
import math
import chibi as C
import chibi_anim2 as N2
W, H, BASE = C.W, C.H, C.BASE

def _hand(a, k=3):
    r = math.radians(a); return (round(k * math.sin(r)), round(k * math.cos(r)))

def _side(angs, lean, dy, tn, face, legs, sw2=None, arm_over=None, k=3):
    P = []
    for i in range(10):
        hx, hy = _hand(angs[i], k)
        d = dict(tn=tn[i], dy=dy[i], hdx=lean[i], bdx=int(lean[i] * .6), dx=int(lean[i] * .7), ar=(hx + 1, hy), al=(0, 0), face=face[i],
                 sw=dict(ang=angs[i], len=12))
        if legs[i]: d['bl'], d['br'] = (-legs[i], 0), (legs[i], 0)
        if arm_over and arm_over.get(i): d['ar'] = arm_over[i]
        if sw2:
            a2 = sw2[i]; h2 = _hand(a2, 2)
            d['al'] = (round(h2[0] * .8), h2[1]); d['sw2'] = dict(ang=a2, len=8)
        P.append(d)
    return P

def _front(angs, lean, dy, tn, face, legs, sw2=None, arm_over=None, k=3):
    P = []
    for i in range(10):
        hx, hy = _hand(angs[i], k)
        d = dict(tn=tn[i], dy=dy[i], hdy=-1 if lean[i] < -1 else (1 if lean[i] > 2 else 0), ar=(hx, hy), al=(0, 0), face=face[i], sw=dict(ang=angs[i], len=12, side='r'))
        if legs[i]: d['bl'], d['br'] = (-legs[i] // 2 - 1, 0), (legs[i] // 2 + 1, 0)
        if arm_over and arm_over.get(i): d['ar'] = arm_over[i]
        if sw2:
            a2 = sw2[i]; h2 = _hand(a2, 2); d['al'] = (h2[0], h2[1]); d['sw2'] = dict(ang=a2, len=8)
        P.append(d)
    return P

N, S_ = 'n', 'shout'
FACE = [N, N, N, N, N, S_, S_, S_, N, N]
# --------------------------------- GUERREIRO ---------------------------------
WAR = {
 # 1) CORTE DESCENDENTE: espada sobe por tras da cabeca e desce em diagonal
 'wchop': dict(angs=[150, 205, 268, 275, 278, 105, 50, 35, 60, 110], lean=[0, -1, -2, -3, -3, 2, 5, 5, 3, 1], dy=[0, 0, 0, 0, 0, 0, 1, 1, 0, 0],
               tn=[3, 3, 3, 3, 3, 3, 2, 2, 3, 3], face=FACE, legs=[0, 0, 0, 1, 1, 2, 3, 3, 1, 0]),
 # 2) CORTE ASCENDENTE: abaixa a espada para tras agachado e sobe cortando de baixo para cima
 'wrise': dict(angs=[100, 70, 40, 15, 345, 25, 100, 160, 150, 120], lean=[0, 1, 2, 3, 3, 1, -2, -3, -2, 0], dy=[0, 0, 1, 1, 1, 0, 0, -1, 0, 0],
               tn=[3, 3, 2, 2, 2, 3, 3, 3, 3, 3], face=FACE, legs=[0, 1, 2, 3, 3, 3, 2, 1, 0, 0]),
 # 4) PANCADA COM SALTO: levanta a espada com as duas maos, salta e bate no chao
 'wslam': dict(angs=[120, 160, 172, 178, 178, 130, 20, 10, 40, 100], lean=[0, -1, -2, -2, -2, 2, 4, 4, 2, 0], dy=[0, 0, -1, -3, -4, -2, 2, 2, 1, 0],
               tn=[3, 3, 3, 3, 3, 3, 2, 2, 3, 3], face=FACE, legs=[0, 0, 0, 0, 0, 1, 3, 3, 1, 0], arm_over={3: (-1, -4), 4: (-1, -5), 5: (1, -2)}),
}
# --------------------------------- LADINO (duas adagas) ---------------------------------
ROG = {
 # 1) CORTE DIAGONAL com a adaga da frente (a de tras fica de guarda)
 'rcut': dict(angs=[120, 150, 170, 182, 185, 110, 50, 40, 60, 110], lean=[0, -1, -2, -2, -2, 2, 4, 4, 2, 0], dy=[0, 0, 0, 0, 0, 0, 1, 1, 0, 0], tn=[3, 3, 3, 3, 3, 3, 2, 2, 3, 3],
              face=FACE, legs=[0, 0, 1, 1, 1, 2, 2, 2, 1, 0], sw2=[120, 120, 125, 125, 125, 120, 115, 115, 120, 120]),
 # 2) CORTE INVERSO ASCENDENTE com a adaga de tras
 'rrev': dict(angs=[110, 110, 110, 110, 110, 100, 95, 100, 110, 110], lean=[0, 1, 2, 2, 2, 0, -2, -2, -1, 0], dy=[0, 0, 1, 1, 1, 0, 0, 0, 0, 0], tn=[3, 3, 2, 2, 2, 3, 3, 3, 3, 3],
              face=FACE, legs=[0, 1, 2, 2, 2, 2, 2, 1, 0, 0], sw2=[100, 60, 30, 10, 345, 40, 120, 165, 150, 120]),
 # 3) ESTOCADA DUPLA: recolhe as duas adagas e espeta uma depois da outra
 'rstab': dict(angs=[100, 95, 92, 90, 90, 88, 90, 90, 95, 100], lean=[0, -1, -2, -3, -3, 3, 5, 5, 3, 1], dy=[0, 0, 0, 0, 0, 0, 1, 1, 0, 0], tn=[3, 3, 3, 3, 3, 3, 2, 2, 3, 3],
               face=FACE, legs=[0, 0, 1, 1, 1, 3, 3, 3, 1, 0], sw2=[100, 98, 95, 92, 92, 90, 88, 88, 95, 100], arm_over={3: (-4, 0), 4: (-5, 0), 5: (6, 0), 6: (8, 0), 7: (8, 0)}),
 # 4) FINALIZADOR EM X: salta e cruza as duas adagas
 'rx': dict(angs=[140, 165, 180, 185, 185, 120, 55, 45, 60, 100], lean=[0, -1, -2, -2, -2, 2, 4, 4, 2, 0], dy=[0, 0, -1, -2, -3, -2, 1, 1, 0, 0], tn=[3, 3, 3, 3, 3, 3, 2, 2, 3, 3],
            face=FACE, legs=[0, 0, 0, 0, 0, 1, 3, 3, 1, 0], sw2=[100, 140, 170, 185, 190, 250, 305, 315, 300, 200]),
}
TABLE = dict(WAR, **ROG)
SEQ = [0, 1, 2, 3, 4, 5, 6, 7, 8, 8, 9, 10, 12, 13, 13, 14, 15, 16, 17, 18]          # indices dos 19 quadros densos; o golpe cai no 11-12

def poses(view, name):
    t = TABLE[name]
    return (_side if view == 'right' else _front)(t['angs'], t['lean'], t['dy'], t['tn'], t['face'], t['legs'], t.get('sw2'), t.get('arm_over'))

def attack(view, ap, name):
    cls = ap.get('cls', 'warrior')
    base = C.anim(view, 'attack', cls, C.densify(poses(view, name), 2), ap, dense=2)
    fr = [b[0] for b in base]; out = []
    heavy = name in ('wslam', 'rx')
    for k, i in enumerate(SEQ):
        im = fr[min(i, len(fr) - 1)]
        if k == 11: im = N2.flash(im, .35 if heavy else .22)
        if k in (11, 12) and not heavy: im = N2.shake(im, 1, 0)
        if heavy:
            if k == 11: im = N2.shake(im, 1, 1)
            if k in (11, 12): im = N2.dust(im, .12 + .22 * (k - 11), cx=W // 2 + 6, n=6)
            if k == 13: im = N2.dust(im, .55, cx=W // 2 + 6, n=6)
            if k == 14: im = N2.dust(im, .8, cx=W // 2 + 6, n=5)
        out.append(im)
    return out
