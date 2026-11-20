#!/usr/bin/env python3
"""ANCIAO CORNALVO (raro pacifico da Planicie) - sprite e animacoes proprias.
Desenhado num quadro MAIOR que o dos outros bichos (120x100, pes em y=92) na MESMA densidade de pixel do heroi
(o atlas sai x2 como todos e o jogo usa CXSIZE.cervo=1): nada de esticar pixel para parecer grande.
Esqueleto 2D: corpo (com inclinacao para empinar), pescoco, cabeca, galhada e 4 pernas com 2 segmentos por IK
(joelho da frente dobra para tras ao recolher, jarrete de tras aponta para tras). Usa o renderizador do fauna.py
(uma massa so, luz de cima-esquerda, contorno seletivo).
Uso: python3 cervo.py            -> gera mmo/assets/chars/cx_cervo_atlas.png/.json
     python3 cervo.py sheet out  -> folha de conferencia (todas as animacoes, 3 vistas)"""
import math, os, sys, json
import numpy as np
from PIL import Image
import fauna as FA

W, H, BASE = 120, 112, 104
FA.W, FA.H = W, H                 # o Cv/render do fauna leem estes globais na hora
R, hx = FA.R, FA.hx
PAL = dict(body=R('#646e8c', '#b4bdd2', '#eef1f8'), belly=R('#8e98b2', '#d2d8e8', '#ffffff'), mane=R('#34502a', '#68943e', '#a6d468'),
           antler=R('#7e5210', '#d39424', '#ffe08a'), hoof=R('#221e2e', '#3e3850', '#5c5472'), ear=R('#7e7290', '#beb0c8', '#e6daee'),
           far=R('#4e5672', '#8a93ac', '#b8c0d4'))
TIP = [hx('#fff2b8'), hx('#ffffff')]
FLAT = {'tip': TIP[0], 'tip2': TIP[1], 'rune': hx('#ffd868'), 'rune2': hx('#fff6c8')}
EYE = hx('#ffb22a'); EYEH = hx('#fff6c8'); DARK = hx('#16121e')


def rot(x, y, cx, cy, a):
    c, s = math.cos(a), math.sin(a); x, y = x - cx, y - cy
    return cx + x * c - y * s, cy + x * s + y * c


def ik(hx_, hy_, fx, fy, l1, l2, bend):
    dx, dy = fx - hx_, fy - hy_; d = math.hypot(dx, dy) or 1e-3
    if d > l1 + l2 - .05: fx, fy = hx_ + dx / d * (l1 + l2 - .05), hy_ + dy / d * (l1 + l2 - .05); d = l1 + l2 - .05
    a = math.atan2(fy - hy_, fx - hx_); c = (l1 * l1 + d * d - l2 * l2) / (2 * l1 * d); c = max(-1, min(1, c)); b = math.acos(c)
    ka = a + bend * b
    return hx_ + math.cos(ka) * l1, hy_ + math.sin(ka) * l1, fx, fy


def draw_leg_front(c, hip, foot, r0, r1, r2, far):
    """de frente/costas a perna fica reta (o joelho dobra na direcao da camera, nao para o lado)"""
    reg = 'far' if far else 'body'; kx, ky = hip[0] + (foot[0] - hip[0]) * .45, hip[1] + (foot[1] - hip[1]) * .45
    c.cap(hip[0], hip[1], kx, ky, r0, r1, reg, far); c.cap(kx, ky, foot[0], foot[1] - .8, r1, r2, reg, far)
    c.cap(foot[0] - 1.2, foot[1] - 1.4, foot[0] + 1.2, foot[1] - .2, r2 + .4, r2 + .4, 'hoof', far)


def draw_leg(c, hip, foot, l1, l2, bend, r0, r1, r2, far):
    kx, ky, fx, fy = ik(hip[0], hip[1], foot[0], foot[1], l1, l2, bend)
    reg = 'far' if far else 'body'
    c.cap(hip[0], hip[1], kx, ky, r0, r1, reg, far)
    c.cap(kx, ky, fx, fy - .8, r1, r2, reg, far)
    c.cap(fx - .6, fy - 1.6, fx + .9, fy, r2 + .35, r2 + .5, 'hoof', far)


# galhada: lista de segmentos em coordenadas da cabeca (x para frente, y para cima), espessuras
ANT = [((0, 0), (-4, 7), 1.8, 1.4), ((-4, 7), (-9, 14), 1.4, 1.15), ((-9, 14), (-12, 22), 1.15, .85), ((-12, 22), (-12, 29), .85, .6),
       ((-2, 4), (5, 9), 1.0, .6), ((-5, 9), (1, 15), .95, .55), ((-9, 15), (-4, 22), .85, .5), ((-11, 21), (-7, 28), .75, .5),
       ((-10, 17), (-17, 20), .8, .5), ((-12, 24), (-17, 29), .7, .5)]
TIPS = [(5, 9), (1, 15), (-4, 22), (-7, 28), (-17, 20), (-17, 29), (-12, 29)]
VINES = [((-4, 7), 6), ((-9, 14), 8), ((-10, 17), 5)]          # cipos/musgo pendurados na galhada (ponto, comprimento)


def antler(c, ox, oy, ang, sx=1.0, reg='antler', far=False, glow=0, sc=1.0, vines=None):
    """ang: rotacao da cabeca (rad, 0 = horizontal p/ direita); y da galhada sobe (tela: -y)."""
    def P(p): x, y = p[0] * sc * sx, -p[1] * sc; return rot(ox + x, oy + y, ox, oy, ang)
    for a, b, r0, r1 in ANT:
        (x0, y0), (x1, y1) = P(a), P(b); c.cap(x0, y0, x1, y1, r0, r1, reg if not far else 'far', far)
    if not far and vines:
        for (p, L) in VINES:
            x, y = P(p); sw = vines[1] if isinstance(vines, tuple) else 0
            c.cap(x, y, x + sw * .6 - .5, y + L * .55, .8, .7, 'mane'); c.cap(x + sw * .6 - .5, y + L * .55, x + sw, y + L, .7, .5, 'mane')
    if not far:
        for i, t in enumerate(TIPS):
            x, y = P(t); c.dot(x, y, TIP[(i + glow) % 2])


def side(P):
    c = FA.Cv(); c.contact = False; gy = BASE; cx = W // 2 - 4
    bx = cx + P.get('lean', 0); by = gy - 37 + P.get('bob', 0) - P.get('lift', 0)
    pitch = -P.get('rear', 0) * .62 + P.get('dip', 0)          # empinar: frente sobe (giro em torno do quadril)
    hipP = (bx - 12, by + 2)
    T = lambda x, y: rot(x, y, hipP[0], hipP[1], pitch)
    fdrop, rdrop = P.get('fdrop', 0), P.get('rdrop', 0)
    def Tb(x, y, k):           # ponto do corpo com queda da frente/tras (morte)
        x, y = T(x, y); return x, y + fdrop * k + rdrop * (1 - k)
    ph, gal = P.get('ph', 0), P.get('gal', 0)
    legs = [('rf', 11, True, False), ('rh', -12, True, True), ('lf', 13, False, False), ('lh', -10, False, True)]
    LEGS = {}
    for nm, lx, far, hind in legs:
        k = 1.0 if not hind else 0.0
        hip = Tb(bx + lx, by + 5, k)
        if 'feet' in P and nm in P['feet']:
            fx, fy = P['feet'][nm]; fx += hip[0]; fy += hip[1]
        else:
            if gal:   # galope: pares quase juntos, fase aerea
                off = {'lh': 0, 'rh': .12, 'lf': .5, 'rf': .62}[nm]
            else:     # passo em 4 tempos
                off = {'lh': 0, 'lf': .25, 'rh': .5, 'rf': .75}[nm]
            q = 2 * math.pi * (ph + off)
            st = P.get('stride', 4.5 if not gal else 9)
            fx = bx + lx + math.cos(q) * st + (1.5 if hind else -0.5)
            fy = gy - max(0, math.sin(q)) * (P.get('step', 3.5) if not gal else 7)
            if P.get('paw') and nm == 'lf': fx += P['paw'] * 3; fy = gy - abs(P['paw']) * 5
        LEGS[nm] = (hip, (fx, fy), hind, far)
    # pernas do lado de la (atras do corpo)
    for nm, (hip, ft, hind, far) in LEGS.items():
        if far: draw_leg(c, hip, ft, 15, 15, (1 if hind else -1), 2.6, 1.7, 1.25, True)
    # corpo
    c.ell(*Tb(bx - 11, by + 1, 0), 10.5, 10.2)                          # garupa
    c.ell(*Tb(bx, by, .5), 14.5, 9.4)                                   # tronco
    c.ell(*Tb(bx + 11, by - 1, 1), 11, 11.2)                            # peito/cernelha
    c.ell(*Tb(bx + 1, by + 5.5, .5), 11, 3.4, 'belly')                  # barriga clara
    # cauda (tufo branco)
    tx, ty = Tb(bx - 21, by - 4, 0); tw = P.get('tail', 0)
    c.cap(tx, ty, tx - 3.2, ty - 2 + tw, 2.4, 1.6, 'belly')
    # pernas do lado de ca
    for nm, (hip, ft, hind, far) in LEGS.items():
        if not far: draw_leg(c, hip, ft, 15, 15, (1 if hind else -1), 2.9, 1.9, 1.35, False)
    # pescoco
    na = math.radians(P.get('neck', 58)) - pitch * 0 + pitch
    sx0, sy0 = Tb(bx + 15, by - 6, 1)
    nx, ny = sx0 + math.cos(-na) * 17 + P.get('lunge', 0), sy0 + math.sin(-na) * 17
    c.cap(sx0, sy0, nx, ny, 7.2, 4.6)
    c.ell(sx0 + 1, sy0 + 4, 5.5, 6, 'belly')                            # babado branco do peito
    # juba de musgo no pescoco (de cima)
    for k in range(6):
        t = k / 5; mx, my = sx0 + (nx - sx0) * t, sy0 + (ny - sy0) * t
        px, py = -math.sin(-na) * 5.5, math.cos(-na) * 5.5
        c.cap(mx - px * .8, my - py * .8 + 1, mx - px * 1.1 - 2.2, my - py * 1.1 + 4.5, 2.0, .8, 'mane')
    # cabeca
    ha = math.radians(P.get('head', -24)) + pitch
    hx1, hy1 = nx + math.cos(ha) * 12, ny + math.sin(-ha) * -1 * -1 + math.sin(ha) * 0
    hx1, hy1 = nx + math.cos(-ha) * 13.5, ny + math.sin(-ha) * 13.5
    # antler de la (atras da cabeca)
    ax, ay = nx - math.cos(-ha) * 1 + 0, ny - 3.2
    antler(c, ax + 2.5, ay - .5, -.55 - ha * .3 + P.get('aa', 0), far=True, sc=.95)
    c.cap(nx - 1, ny, hx1, hy1, 5.6, 3.0)                               # cranio -> focinho
    mo = P.get('mouth', 0)
    if mo: c.cap(nx + 3, ny + 2.5, hx1 - 1, hy1 + 2 + mo * 2.2, 1.8, 1.2)   # maxilar aberto
    c.cap(nx - 1.5, ny - 1.5, nx - 8, ny - 3.5 + P.get('ear', 0), 2.5, 1.0, 'ear')
    antler(c, ax, ay, -.55 - ha * .3 + P.get('aa', 0), glow=P.get('glow', 0), sc=1.0, vines=(1, P.get('sway', 0)))
    # detalhes: olho, narina, runas no flanco
    ex, ey = nx + math.cos(-ha) * 4.5 + .5, ny + math.sin(-ha) * 4.5 - 1.6
    if P.get('squint'): c.dot(ex, ey, DARK); c.dot(ex + 1, ey, DARK)
    else: c.dot(ex, ey, EYE); c.dot(ex + 1, ey, EYE); c.dot(ex, ey - 1, EYEH)
    c.dot(hx1 + .5, hy1 - .5, DARK)
    if mo:
        c.dot(hx1 - 2, hy1 + 1.5, DARK); c.dot(hx1 - 3, hy1 + 1.5, DARK)
    rg = P.get('rune', 0)
    for i, (rx_, ry_) in enumerate(((-6, -3), (-3, -5), (0, -3), (3, -5), (-9, 0))):
        x, y = Tb(bx + rx_, by + ry_, .5); c.dot(x, y, FLAT['rune2'] if (i + rg) % 3 == 0 else FLAT['rune'])
    return c.render(PAL, FLAT)


def front(P, back=False):
    c = FA.Cv(); c.contact = False; gy = BASE; bx = W // 2; by = gy - 36 + P.get('bob', 0) - P.get('lift', 0)
    rear = P.get('rear', 0); hd = P.get('hd', 0); fdrop = P.get('fdrop', 0)
    ph, gal = P.get('ph', 0), P.get('gal', 0)
    sink = fdrop
    # pernas: de frente as 2 da frente na frente; as de tras aparecem entre/atras
    def legpos(sx, off, far, hind):
        q = 2 * math.pi * (ph + off)
        lift = max(0, math.sin(q)) * (3.5 if not gal else 6)
        if rear and not hind: lift = 12 * rear
        hip = (bx + sx, by + 6 + sink + (-rear * 10 if not hind else 0))
        foot = (bx + sx * (1.1 if not hind else 1.0), gy - lift)
        if P.get('fold'): foot = (bx + sx * 1.6, hip[1] + 6)
        return hip, foot
    order = [(-5, .5, True, True), (5, 0, True, True)] if not back else [(-6, .25, True, False), (6, .75, True, False)]
    order2 = [(-6.5, .25, False, False), (6.5, .75, False, False)] if not back else [(-5.5, 0, False, True), (5.5, .5, False, True)]
    for sx, off, far, hind in order:
        hip, ft = legpos(sx, off, far, hind); draw_leg_front(c, hip, ft, 3.0, 1.9, 1.35, True)
    # corpo (peito visto de frente / garupa de costas)
    c.ell(bx, by + sink - rear * 6, 13.5, 13)
    if not back: c.ell(bx, by + 4 + sink - rear * 6, 6, 7, 'belly')
    else: c.ell(bx, by - 6 + sink, 4, 3.4, 'belly')                       # tufo do rabo
    for sx, off, far, hind in order2:
        hip, ft = legpos(sx, off, far, hind); draw_leg_front(c, hip, ft, 3.4, 2.2, 1.5, False)
    # pescoco e cabeca
    hy = by - 21 + sink + hd * 12 - rear * 5 - P.get('hu', 0) * 3
    if back:
        c.cap(bx, by - 6 + sink - rear * 6, bx, hy + 4, 6.5, 5)
        for k in range(5): c.cap(bx + (k - 2) * 2.2, by - 8 + sink - k * 2.4 - rear * 6, bx + (k - 2) * 2.6, by - 4 + sink - k * 2.4 - rear * 6, 1.4, .7, 'mane')
        c.ell(bx, hy, 5.4, 5.2)
        for sg in (-1, 1): c.cap(bx + sg * 4, hy - 2, bx + sg * 9, hy - 4 + P.get('ear', 0), 2.4, 1, 'ear')
    else:
        c.cap(bx, by - 4 + sink - rear * 6, bx, hy + 5, 6.5, 5)
        c.ell(bx, by - 2 + sink - rear * 6, 5, 6, 'belly')
        for sg in (-1, 1): c.cap(bx + sg * 4, hy - 2, bx + sg * 9, hy - 4 + P.get('ear', 0), 2.4, 1, 'ear')
        c.ell(bx, hy, 6, 6.2)
        c.cap(bx, hy + 2, bx, hy + 8 + P.get('mouth', 0) * 1.5, 4, 2.8)
        for sg in (-1, 1): c.cap(bx + sg * 6, hy + 3, bx + sg * 8, hy + 10, 1.6, .9, 'mane')
    # galhada espelhada (larga, imponente)
    sc = 1.0 - hd * .15
    for sg in (-1, 1):
        ox, oy = bx + sg * 3, hy - 3.5
        def Pp(p, sg=sg, ox=ox, oy=oy):
            return ox + sg * (-p[0] * .9 + p[1] * .55) * sc, oy - (p[1] * .9 - hd * p[1] * .35) * sc
        for a, b, r0, r1 in ANT:
            (x0, y0), (x1, y1) = Pp(a), Pp(b); c.cap(x0, y0, x1, y1, r0, r1, 'antler')
        for (p, L) in VINES:
            x, y = Pp(p); c.cap(x, y, x + sg * .5, y + L * .9, .8, .5, 'mane')
        for i, t in enumerate(TIPS):
            x, y = Pp(t); c.dot(x, y, TIP[(i + P.get('glow', 0)) % 2])
    if not back:
        sq = P.get('squint')
        for sg in (-1, 1):
            if sq: c.dot(bx + sg * 3, hy, DARK)
            else: c.dot(bx + sg * 3, hy, EYE); c.dot(bx + sg * 3, hy - 1, EYEH)
        c.dot(bx - 1, hy + 8 + P.get('mouth', 0) * 1.5, DARK); c.dot(bx + 1, hy + 8 + P.get('mouth', 0) * 1.5, DARK)
        rg = P.get('rune', 0)
        for i, (rx_, ry_) in enumerate(((-7, 3), (7, 3), (0, 10))):
            c.dot(bx + rx_, by + ry_ + sink - rear * 6, FLAT['rune2'] if (i + rg) % 3 == 0 else FLAT['rune'])
    return c.render(PAL, FLAT)


def draw(view, P):
    if view == 'right': return side(P)
    return front(P, back=(view == 'up'))


# ------------------------------------------------------------------ animacoes
def ease(t): return t * t * (3 - 2 * t)


def seq(view, kind):
    out = []
    if kind == 'idle':                       # respira, abaixa a cabeca, orelha mexe, rabo, galhada cintila
        n = 16
        for i in range(n):
            u = i / n; s = math.sin(u * 2 * math.pi)
            out.append(dict(bob=1 if s > .55 else 0, head=-24 + 3 * s, neck=58 + 2 * s, ear=(-1.5 if 9 <= i <= 11 else 0), tail=(-1.5 if i in (3, 4) else 0),
                            glow=(i // 4) % 2, rune=i // 3, hd=.05 * (s + 1), ph=0, stride=0, step=0, sway=math.sin(u * 2 * math.pi + 1)))
    elif kind == 'walk':                     # passo em 4 tempos, cabeca acompanha
        n = 16
        for i in range(n):
            u = i / n
            out.append(dict(ph=u, bob=-1 if abs(math.sin(u * 4 * math.pi)) > .85 else 0, head=-24 + 3 * math.sin(u * 4 * math.pi), neck=57 + 2 * math.sin(u * 4 * math.pi),
                            tail=math.sin(u * 2 * math.pi), glow=(i // 4) % 2, rune=i // 3, sway=-math.sin(u * 4 * math.pi)))
    elif kind == 'run':                      # galope: fase aerea, corpo em arco, pescoco estendido
        n = 12
        for i in range(n):
            u = i / n; s = math.sin(u * 2 * math.pi)
            out.append(dict(ph=u, gal=1, lift=max(0, s) * 4, bob=0, dip=.08 * s, neck=44 + 6 * s, head=-30 + 4 * s, lean=1, tail=-2, glow=i % 2, rune=i, ear=1, sway=-2))
    elif kind == 'attack':                   # chifrada: abaixa a galhada (antecipa), arremete para cima/frente, segura e volta
        n = 20
        for i in range(n):
            if i < 8: t = ease(i / 7); P = dict(head=-24 - 40 * t, neck=58 - 22 * t, lean=-3 * t, bob=int(t * 1.5), hd=.8 * t, paw=math.sin(i * 1.2) * t * .8)
            elif i < 11: t = (i - 8) / 2; P = dict(head=-64 + 74 * t, neck=36 + 24 * t, lean=-3 + 10 * t, hd=.8 - .9 * t, lift=2 * t, lunge=2 * t, mouth=1)
            elif i < 14: P = dict(head=8, neck=62, lean=7, hd=-.1, lift=2, lunge=2, mouth=1, squint=0)
            else: t = ease((i - 14) / 5); P = dict(head=8 - 32 * t, neck=62 - 4 * t, lean=7 - 7 * t, lift=2 - 2 * t, lunge=2 - 2 * t)
            P.update(stride=0, step=0, glow=i % 2, rune=i); out.append(P)
    elif kind == 'stomp':                    # empina nas patas de tras e bate no chao (impacto no quadro 15)
        n = 20
        for i in range(n):
            if i < 4: t = ease(i / 3); P = dict(dip=.06 * t, head=-24 - 10 * t, bob=int(2 * t), hd=.3 * t)
            elif i < 13: t = ease((i - 4) / 8); P = dict(rear=t, head=-34 + 50 * t, neck=58 + 8 * t, mouth=1 if i > 8 else 0, hu=t, glow=i % 2,
                                                         feet=dict(rf=(4 + 4 * t, 16 - 6 * t), lf=(6 + 4 * t, 14 - 6 * t)) if t > .35 else {})
            elif i < 15: t = (i - 13) / 2; P = dict(rear=1 - t * 1.05, head=16 - 40 * t, neck=66 - 10 * t, mouth=1, hu=1 - t)
            elif i < 17: P = dict(rear=0, dip=.1, bob=3, head=-34, neck=52, hd=.4, squint=1, glow=1)
            else: t = ease((i - 17) / 2); P = dict(dip=.1 * (1 - t), bob=int(3 * (1 - t)), head=-34 + 10 * t, neck=52 + 6 * t, hd=.4 * (1 - t))
            P.setdefault('stride', 0); P.setdefault('step', 0); P.setdefault('rune', i); out.append(P)
    elif kind == 'charge':                   # cava o chao com a pata, abaixa a galhada e dispara em galope
        n = 20
        for i in range(n):
            if i < 12: t = ease(min(1, i / 5)); P = dict(head=-24 - 46 * t, neck=58 - 26 * t, hd=.9 * t, lean=-2 * t, bob=int(t), paw=math.sin(i * 1.4) * (1 if i > 3 else 0), stride=0, step=0, glow=i % 2, rune=i)
            else: u = (i - 12) / 8; s = math.sin(u * 2 * math.pi); P = dict(ph=u, gal=1, lift=max(0, s) * 3, head=-70, neck=30, hd=1, lean=3, tail=-2, ear=1, glow=i % 2, rune=i)
            out.append(P)
    elif kind == 'roar':                     # bramido: ergue a cabeca, abre a boca, runas e galhada acendem
        n = 20
        for i in range(n):
            if i < 6: t = ease(i / 5); P = dict(head=-24 - 14 * t, neck=58 - 10 * t, hd=.3 * t, bob=int(t))
            elif i < 15: t = ease(min(1, (i - 6) / 3)); P = dict(head=-38 + 70 * t, neck=48 + 22 * t, hu=t, mouth=1 + (i % 2) * .4, glow=i % 2, rune=i, lift=1, ear=-1)
            else: t = ease((i - 15) / 4); P = dict(head=32 - 56 * t, neck=70 - 12 * t, hu=1 - t, mouth=1 if t < .5 else 0)
            P.update(stride=0, step=0); P.setdefault('rune', i); P.setdefault('glow', i % 2); out.append(P)
    elif kind == 'bless':                    # Couraca de Casca: curva a cabeca, galhada para frente brilhando, se firma
        n = 20
        for i in range(n):
            t = ease(min(1, i / 8)); r = ease(max(0, (i - 14) / 5))
            out.append(dict(head=-24 - 40 * t + 40 * r, neck=58 - 18 * t + 18 * r, hd=.7 * t * (1 - r), bob=int(2 * t * (1 - r)), glow=i % 2, rune=i * 2, stride=0, step=0))
    elif kind == 'hurt':
        n = 9
        for i in range(n):
            t = math.sin(min(1, i / 6) * math.pi)
            out.append(dict(lean=-3 * t, head=-24 + 18 * t, neck=58 + 6 * t, squint=1 if i < 6 else 0, mouth=1 if 1 <= i <= 4 else 0, ear=1, stride=0, step=0, hu=.5 * t))
    elif kind == 'death':                    # cambaleia, joelhos da frente cedem, depois tras; deita com a cabeca no chao
        n = 15
        for i in range(n):
            if i < 3: P = dict(lean=-2, head=-6, neck=64, squint=1, mouth=1, hu=.6)
            elif i < 7: t = ease((i - 3) / 3); P = dict(fdrop=11 * t, head=-6 - 30 * t, neck=64 - 24 * t, hd=.5 * t, squint=1, fold=1 if t > .5 else 0,
                                                       feet=dict(rf=(6, 14 - 6 * t), lf=(8, 14 - 6 * t)) if view == 'right' else {})
            else: t = ease(min(1, (i - 7) / 4)); P = dict(fdrop=11 + 2 * t, rdrop=11 * t, head=-36 - 20 * t, neck=40 - 14 * t, hd=.5 + .5 * t, squint=1, fold=1,
                                                         feet=dict(rf=(6, 8), lf=(8, 8), rh=(4, 10 - 3 * t), lh=(6, 10 - 3 * t)) if view == 'right' else {})
            P.update(stride=0, step=0); out.append(P)
    if kind in ('stomp', 'charge', 'roar', 'bless') and len(out) == 20:   # 16 quadros (impacto continua em 75%)
        out = [out[round(i * 19 / 15)] for i in range(16)]
    return [draw(view, P) for P in out]


KINDS = ['idle', 'walk', 'run', 'attack', 'hurt', 'death', 'stomp', 'charge', 'roar', 'bless']
VIEWS = {'d': 'down', 'u': 'up', 's': 'right'}


def export(out_dir, sc=2):
    imgs, anims = [], {}
    for kind in KINDS:
        for vk, vn in VIEWS.items():
            fr = seq(vn, kind); anims[f'{kind}_{vk}'] = list(range(len(imgs), len(imgs) + len(fr))); imgs += fr
    anims.update({f'cast_{v}': anims[f'roar_{v}'] for v in VIEWS})
    bb = None
    for im in imgs:
        b = im.getbbox()
        if b: bb = b if bb is None else (min(bb[0], b[0]), min(bb[1], b[1]), max(bb[2], b[2]), max(bb[3], b[3]))
    x0, y0, x1, y1 = max(0, bb[0] - 1), max(0, bb[1] - 1), min(W, bb[2] + 1), min(H, bb[3] + 1)
    for im in imgs:
        b = im.getbbox()
        if b and (b[1] <= 0 or b[0] <= 0 or b[2] >= W or b[3] > H): print('AVISO: quadro toca a borda', b)
    cw, ch = x1 - x0, y1 - y0; w, h = cw * sc, ch * sc; cols = 24; rows = (len(imgs) + cols - 1) // cols
    A = Image.new('RGBA', (cols * w, rows * h), (0, 0, 0, 0))
    for i, im in enumerate(imgs): A.alpha_composite(im.crop((x0, y0, x1, y1)).resize((w, h), Image.NEAREST), ((i % cols) * w, (i // cols) * h))
    A.save(os.path.join(out_dir, 'cx_cervo_atlas.png'), optimize=True)
    json.dump(dict(w=w, h=h, ax=(W // 2 - x0) * sc, ay=(BASE + 1 - y0) * sc, cols=cols, anims=anims), open(os.path.join(out_dir, 'cx_cervo_atlas.json'), 'w'))
    print('cervo', len(imgs), 'quadros', A.size, os.path.getsize(os.path.join(out_dir, 'cx_cervo_atlas.png')) // 1024, 'KB')


def sheet(path):
    rows = []
    for kind in KINDS:
        for vn in ('right', 'down', 'up'):
            rows.append(seq(vn, kind))
    cols = max(len(r) for r in rows)
    S = Image.new('RGBA', (cols * W, len(rows) * H), (60, 84, 52, 255))
    for j, r in enumerate(rows):
        for i, im in enumerate(r): S.alpha_composite(im, (i * W, j * H))
    S.resize((S.width * 2, S.height * 2), Image.NEAREST).save(path); print(path, S.size)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'sheet': sheet(sys.argv[2])
    else: export(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..', 'mmo', 'assets', 'chars')))
