#!/usr/bin/env python3
"""SENHOR DAS MARES (Maragon) - chefe de cacada que vive SEMPRE dentro d'agua, de frente para a praia.
Visto so de FRENTE (o jogador esta sempre em terra, ao sul): do peito para cima fora d'agua, linha d'agua com espuma.
Mesmo renderizador do fauna.py (uma massa so, luz de cima-esquerda, contorno seletivo); quadro proprio 150x150,
linha d'agua em y=WL. Os bracos podem passar da linha d'agua (golpe na praia, agarrao); o tronco nao.
Animacoes: idle 16, slam 20 (martelada), sweep 20 (varrida), cast 16 (orbe), grab 20 (agarrao), roar 16 (mare),
dive 20 (afunda), under 8 (submerso), emerge 16 (sobe com onda), hurt 9, death 20.
Atlas sai em escala x1 (o jogo usa CXSIZE.mare=2 = mesma densidade de pixel dos outros, x2*0.75).
Uso: python3 mare.py            -> mmo/assets/chars/cx_mare_atlas.png/.json
     python3 mare.py sheet out  -> folha de conferencia"""
import math, os, sys, json
import numpy as np
from PIL import Image
import fauna as FA

W, H, WL = 176, 158, 108
FA.W, FA.H = W, H
R, hx = FA.R, FA.hx
PAL = dict(body=R('#173f52', '#2a7a84', '#5cbfae'), skin=R('#173f52', '#2a7a84', '#5cbfae'), arm=R('#173f52', '#2a7a84', '#5cbfae'), belly=R('#4f7466', '#93bc98', '#d6efc4'),
           shell=R('#7a3a14', '#d98a2c', '#ffd06a'), fin=R('#2a2448', '#4f4a86', '#8f88c4'), coral=R('#7a1e40', '#d85474', '#ffacb4'),
           kelp=R('#1f2e12', '#3f6024', '#77983c'), claw=R('#3a3630', '#bdb49a', '#f2ecd8'), far=R('#123240', '#215f68', '#3f8f88'),
           hand=R('#173f52', '#2a7a84', '#5cbfae'))
FLAT = {'foam': hx('#e8fbff'), 'foam2': hx('#9fe0f2'), 'mouth': hx('#3a0c1c'), 'orb': hx('#8ff6ff'), 'orb2': hx('#ffffff'), 'eye': hx('#fff2a0')}
EYE = hx('#fff2a0'); EYEH = hx('#ffffff'); GLOW = [hx('#7ff4ff'), hx('#c8fbff')]; TEETH = hx('#f4f0e0'); GILL = hx('#0e2a36')
BUB = [hx('#d8f6ff'), hx('#8fd8ee')]
ARMSET = {'arm', 'hand', 'claw', 'fin', 'orb', 'orb2', 'kelp', 'far'}
CX = W // 2


def ik(sx, sy, tx, ty, l1, l2, bend):
    dx, dy = tx - sx, ty - sy; d = math.hypot(dx, dy) or 1e-3
    if d > l1 + l2 - .1: tx, ty = sx + dx / d * (l1 + l2 - .1), sy + dy / d * (l1 + l2 - .1); d = l1 + l2 - .1
    a = math.atan2(ty - sy, tx - sx); c = (l1 * l1 + d * d - l2 * l2) / (2 * l1 * d); b = math.acos(max(-1, min(1, c)))
    ka = a + bend * b
    return sx + math.cos(ka) * l1, sy + math.sin(ka) * l1, tx, ty


def arm(c, sx, sy, tx, ty, side, k=1.0, fist=0.0, far=False, kelp=0.0):
    """braco inteiro numa so massa: ombro -> cotovelo -> mao com 3 garras e nadadeira no antebraco.
    side: -1 esquerda da tela, +1 direita. k: escala (mao vindo para a camera fica maior)."""
    l1, l2 = 17 * k, 17 * k
    ex, ey, hx_, hy_ = ik(sx, sy, tx, ty, l1, l2, -side)          # cotovelo para fora
    reg = 'far' if far else 'arm'
    c.cap(sx, sy, ex, ey, 7.0 * k, 5.6 * k, reg, far)
    c.cap(ex, ey, hx_, hy_, 5.6 * k, 4.8 * k, reg, far)
    # nadadeira do antebraco (para fora)
    nx, ny = -(hy_ - ey), (hx_ - ex); nl = math.hypot(nx, ny) or 1; nx, ny = nx / nl * side, ny / nl * side
    if nx * side < 0: nx, ny = -nx, -ny
    mx, my = ex + (hx_ - ex) * .35, ey + (hy_ - ey) * .35
    c.cap(mx, my, mx + nx * 7 * k + (hx_ - ex) * .25, my + ny * 7 * k + (hy_ - ey) * .25, 2.2 * k, .7, 'fin' if not far else 'far', far)
    # mao
    a = math.atan2(hy_ - ey, hx_ - ex)
    c.ell(hx_ + math.cos(a) * 2 * k, hy_ + math.sin(a) * 2 * k, 6.4 * k, 5.6 * k, 'hand' if not far else 'far', far)
    if not far:
        spread = .55 * (1 - fist)
        for j in (-1, 0, 1):
            aa = a + j * spread; L = (7.5 - abs(j) * 1.2) * k * (1 - .45 * fist)
            bx, by = hx_ + math.cos(a) * 5 * k + math.cos(aa + math.pi / 2) * j * 2.2 * k, hy_ + math.sin(a) * 5 * k + math.sin(aa + math.pi / 2) * j * 2.2 * k
            c.cap(bx, by, bx + math.cos(aa) * L, by + math.sin(aa) * L, 1.7 * k, .55, 'claw')
        if kelp:   # algas penduradas no punho
            c.cap(hx_ - 2, hy_ + 2, hx_ - 3 + kelp, hy_ + 9, .9, .6, 'kelp')
    return hx_, hy_


def frame(P):
    c = FA.Cv(); c.contact = False
    sink = P.get('sink', 0); bob = P.get('bob', 0); lean = P.get('lean', 0); tilt = P.get('tilt', 0); back = P.get('back', 0)
    by = WL - 22 + bob + sink; bx = CX + lean
    sh = P.get('shrug', 0)
    shL, shR = (bx - 27, by - 18 - sh), (bx + 27, by - 18 - sh)
    hy = by - 40 - back * 3; hxp = bx + tilt * 2
    # bracos que ficam ATRAS do corpo (erguidos para tras da cabeca)
    hands = {}
    def do_arm(side, front):
        key = 'L' if side < 0 else 'R'; A = P.get(key, (side * 12, 26)); sp = shL if side < 0 else shR
        if bool(A[2] if len(A) > 2 else 0) != (not front): return   # A[2] = 1 -> atras do corpo
        k = P.get('k' + key, 1.0)
        hands[key] = arm(c, sp[0], sp[1], sp[0] + A[0], sp[1] + A[1], side, k, P.get('fist' + key, 0), kelp=P.get('kelp', 0) if side > 0 else 0)
    do_arm(-1, False); do_arm(1, False)
    # algas penduradas nos ombros (atras)
    sw = P.get('sway', 0)
    for sgn in (-1, 1):
        x0 = bx + sgn * 30; y0 = by - 14
        c.cap(x0, y0, x0 + sgn * 2 + sw, y0 + 16, 2.0, 1.2, 'kelp'); c.cap(x0 + sgn * 2 + sw, y0 + 16, x0 + sgn * 3 + sw * 1.6, y0 + 26, 1.2, .7, 'kelp')
    # tronco
    c.ell(bx, by, 26, 26)                                       # peito/abdome
    c.ell(bx, by - 14, 30, 13)                                  # ombros largos
    c.ell(bx, by + 4, 16, 18, 'belly')                          # placa ventral
    for sgn in (-1, 1):
        c.ell(bx + sgn * 26, by - 19 - sh, 12, 10, 'shell')       # ombreiras de concha/cracas
        c.cap(bx + sgn * 22, by - 26 - sh, bx + sgn * 33, by - 31 - sh, 2.4, 1.0, 'shell')   # espinho da ombreira
    # pescoco + cabeca
    c.cap(bx, by - 26, hxp, hy + 6, 10, 9)
    c.ell(hxp, hy, 16, 14)                                      # cranio
    c.ell(hxp, hy + 7 + P.get('mouth', 0) * 2.2, 14, 7)         # mandibula (desce ao rugir)
    # nadadeiras-orelha e crista
    fl = P.get('flap', 0)
    for sgn in (-1, 1):
        c.cap(hxp + sgn * 14, hy - 2, hxp + sgn * (26 + fl), hy - 9 + fl * .5, 3.2, .8, 'fin')
        c.cap(hxp + sgn * 14, hy + 2, hxp + sgn * (23 + fl * .6), hy + 2, 2.2, .6, 'fin')
    crest = [(0, -14, 0, -33), (-5, -13, -9, -31), (5, -13, 9, -31), (-9, -11, -16, -28), (9, -11, 16, -28), (-12, -8, -22, -21), (12, -8, 22, -21), (-14, -3, -25, -12), (14, -3, 25, -12)]
    for x0, y0, x1, y1 in crest:
        c.cap(hxp + x0, hy + y0, hxp + x1 + fl * .3 * (1 if x1 > 0 else -1), hy + y1 - back * 2, 3.2 if x0 == 0 else 2.6, .6, 'fin')
    for x0, y0, x1, y1 in ((-4, -12, -5, -17), (3, -13, 4, -19), (9, -10, 10, -15)):
        c.cap(hxp + x0, hy + y0, hxp + x1, hy + y1, 1.4, .8, 'coral')                         # coral na cabeca
    # bracos da frente
    do_arm(-1, True); do_arm(1, True)
    # orbe de agua entre as maos
    orb = P.get('orb', 0)
    if orb:
        ox, oy = P.get('orbp', (bx, by - 4)); c.ell(ox, oy, orb, orb, 'orb'); c.ell(ox - orb * .3, oy - orb * .3, max(1, orb * .4), max(1, orb * .4), 'orb2')
    # ---- corta tudo do TRONCO abaixo da linha d'agua (bracos e orbe ficam)
    cut = np.arange(H)[:, None] >= WL
    keep = np.isin(np.array([s for s in c.names] + ['_'])[np.where(c.reg >= 0, c.reg, len(c.names))], list(ARMSET))
    keep &= ~np.isin(np.array([s for s in c.names] + ['_'])[np.where(c.reg >= 0, c.reg, len(c.names))], ['kelp'])
    if sink > 0: keep[:] = False             # afundando: some TUDO abaixo da linha d'agua (bracos e crista tambem)
    c.reg[cut & ~keep] = -1
    # ---- espuma na linha d'agua (onde o corpo encosta na agua) + respingos
    rows = np.where((c.reg[:WL, :] >= 0).any(0))[0]
    fo = P.get('foam', 1.0); ph = P.get('ph', 0)
    if len(rows) and fo > 0:
        x0, x1 = rows.min() - 5, rows.max() + 5
        for x in range(max(1, x0), min(W - 1, x1 + 1)):
            hgt = 1 + int(1.5 + 1.5 * math.sin(x * .7 + ph * 6.283) + 1.2 * math.sin(x * 1.9 - ph * 12.566)) * fo
            for y in range(WL - int(hgt), WL + 2):
                if 0 <= y < H:
                    r0 = c.reg[y, x]
                    if r0 >= 0 and c.names[r0] in ARMSET and y >= WL - 3: continue      # braco na frente da agua nao e cortado pela espuma
                    c.reg[y, x] = c.rid('foam' if (x + y + int(ph * 8)) % 5 else 'foam2')
    # olhos, boca, guelras, runas bioluminescentes
    sq = P.get('squint', 0); m = P.get('mouth', 0)
    if hy + 2 < WL:
        for sgn in (-1, 1):
            ex = hxp + sgn * 6
            if sq: c.dot(ex - 1, hy, GILL); c.dot(ex, hy, GILL); c.dot(ex + 1, hy, GILL)
            else:
                for dx in (-1, 0, 1):
                    for dy in (-1, 0): c.dot(ex + dx, hy + dy, EYE)
                c.dot(ex - sgn, hy - 1, EYEH)
        if hy + 7 < WL:
            if m > .3:
                for xx in range(-6, 7):
                    for yy in range(0, int(1 + m * 3)): c.dot(hxp + xx, hy + 6 + yy, FLAT['mouth'])
                for xx in (-5, -2, 2, 5): c.dot(hxp + xx, hy + 6, TEETH); c.dot(hxp + xx, hy + 6 + int(m * 3), TEETH)
            else:
                for xx in range(-7, 8): c.dot(hxp + xx, hy + 7, GILL)
                for xx in (-6, -4, -2, 2, 4, 6): c.dot(hxp + xx, hy + 8, TEETH)
        for sgn in (-1, 1):
            for i in range(3):
                gy = by - 24 + i * 3
                if gy < WL - 1: c.dot(hxp + sgn * (8 - i), gy, GILL); c.dot(hxp + sgn * (9 - i), gy, GILL)
    BD = hx('#5f8a70'); SC = hx('#1f5d68')
    for j in range(-12, 20, 5):                                   # placas segmentadas da barriga
        y = by + j
        if y >= WL - 1: break
        w_ = int(13 * math.sqrt(max(0, 1 - ((j - 4) / 18) ** 2)))
        for xx in range(-w_ + 2, w_ - 1):
            if (xx + j) % 7: c.dot(bx + xx, y, BD)
    for (sx_, sy_) in ((-18, -6), (-21, 2), (-15, 8), (18, -6), (21, 2), (15, 8), (-24, -14), (24, -14), (-12, -22), (12, -22)):
        y = by + sy_
        if y < WL - 1: c.dot(bx + sx_, y, SC); c.dot(bx + sx_ + 1, y + 1, SC)      # escamas escuras nos flancos
    if hy + 8 < WL:
        for sgn in (-1, 1):                                       # presas saindo da boca
            c.dot(hxp + sgn * 7, hy + 9 + int(m * 2), TEETH); c.dot(hxp + sgn * 7, hy + 10 + int(m * 2), TEETH)
    rg = P.get('rune', 0)
    for i, (rx_, ry_) in enumerate(((-9, -4), (9, -4), (0, 2), (-5, 10), (5, 10), (0, -10))):
        y = by + ry_
        if y < WL - 2: c.dot(bx + rx_, y, GLOW[(i + rg) % 2] if (i + rg) % 3 else hx('#4fe0f0'))
    img = c.render(PAL, FLAT)
    # bolhas (desenhadas por cima, pixels soltos e brilhantes)
    px = img.load()
    for (bxp, byp, s) in P.get('bubbles', []):
        bxp, byp = int(bxp), int(byp)
        for dx in range(-s, s + 1):
            for dy in range(-s, s + 1):
                if 0 <= bxp + dx < W and 0 <= byp + dy < H and abs(dx) + abs(dy) == s: px[bxp + dx, byp + dy] = BUB[(dx + dy) % 2] + (255,)
        if 0 <= bxp - 1 < W and 0 <= byp - 1 < H and s > 1: px[bxp - 1, byp - 1] = (255, 255, 255, 255)
    # anel de ondulacao na agua (pontilhado claro, cresce com 'ring')
    rg2 = P.get('ring', 0)
    if rg2:
        rx_, ry_ = min(82, 30 + rg2 * 36), min(12, 5 + rg2 * 5)
        for a in range(0, 360, 4):
            x = int(CX + math.cos(math.radians(a)) * rx_); y = int(WL + 2 + math.sin(math.radians(a)) * ry_)
            if 0 <= x < W and 0 <= y < H and px[x, y][3] == 0 and (a // 4) % 3: px[x, y] = BUB[(a // 8) % 2] + (255,)
    return img


def ease(t): return t * t * (3 - 2 * t)
def lerp(a, b, t): return a + (b - a) * t
def lerp2(a, b, t): return tuple(lerp(x, y, t) for x, y in zip(a, b))


REST_L, REST_R = (-12, 26), (12, 26)


def seq(kind):
    out = []
    if kind == 'idle':
        n = 16
        for i in range(n):
            u = i / n; s = math.sin(u * 2 * math.pi); s2 = math.sin(u * 4 * math.pi)
            out.append(dict(bob=round(1.5 * s), L=(-12 - s, 26 + s * 2), R=(12 + s, 26 - s * 2), sway=s * 2, flap=1 + s, tilt=.3 * s, ph=u, rune=i // 2, mouth=.15 if 6 <= i <= 9 else 0,
                            bubbles=[(CX - 34 + 6 * s, WL - 2 - (i % 8) * 2, 1)] if i % 8 < 5 else []))
    elif kind == 'slam':                     # martelada: ergue o braco direito bem alto, bate na PRAIA (mao vem para a camera)
        n = 20
        for i in range(n):
            if i < 8:
                t = ease(i / 7); P = dict(R=lerp2(REST_R, (14, -52, 1), t) + ((1,) if t > .5 else ()), lean=-2 * t, back=t, mouth=.6 * t, shrug=2 * t, L=(-14, 22), tilt=-.5 * t)
                if t <= .5: P['R'] = lerp2(REST_R, (14, -52), t)
            elif i < 11:
                t = (i - 8) / 2; P = dict(R=lerp2((14, -52), (4, 76), t), kR=1 + .35 * t, lean=-2 + 5 * t, bob=3 * t, mouth=1, L=(-16, 20), fistR=1, tilt=.6)
            elif i < 15:
                P = dict(R=(4, 76), kR=1.35, lean=3, bob=3, mouth=1 if i < 13 else .5, L=(-16, 20), fistR=1, squint=1 if i == 11 else 0, ring=(i - 10) * .25, tilt=.6)
            else:
                t = ease((i - 15) / 4); P = dict(R=lerp2((4, 76), REST_R, t), kR=1.35 - .35 * t, lean=3 - 3 * t, bob=round(3 * (1 - t)), L=(-16 + 4 * t, 20 + 6 * t), fistR=1 - t, ring=1 + t * .5 if t < .9 else 0)
            P.setdefault('ph', i / n); P.setdefault('rune', i); P.setdefault('flap', 2); out.append(P)
    elif kind == 'sweep':                    # varrida: braco esquerdo abre para fora e varre a praia da esquerda para a direita
        n = 20
        for i in range(n):
            if i < 7:
                t = ease(i / 6); P = dict(L=lerp2(REST_L, (-44, 6), t), lean=-3 * t, tilt=-t, mouth=.4 * t, shrug=1, R=(14, 22))
            elif i < 12:
                t = (i - 7) / 4; a = math.radians(180 - 150 * t); P = dict(L=(math.cos(a) * 50 + 8, 22 + math.sin(a) * 40), kL=1 + .3 * math.sin(t * math.pi), lean=-3 + 7 * t, tilt=-1 + 2 * t, mouth=1, R=(16, 20), ring=.3 * t)
            elif i < 15:
                P = dict(L=(52, 30), kL=1.05, lean=4, tilt=1, mouth=.6, R=(18, 18), ring=.6)
            else:
                t = ease((i - 15) / 4); P = dict(L=lerp2((52, 30), REST_L, t), kL=1.05 - .05 * t, lean=4 - 4 * t, tilt=1 - t, R=lerp2((18, 18), REST_R, t))
            P.setdefault('ph', i / n); P.setdefault('rune', i); P.setdefault('flap', 2); out.append(P)
    elif kind == 'cast':                     # orbe d'agua: junta as maos no peito, o orbe cresce e e lancado para frente
        n = 16
        for i in range(n):
            if i < 9:
                t = ease(i / 8); P = dict(L=lerp2(REST_L, (16, 10), t), R=lerp2(REST_R, (-16, 10), t), orb=1 + 6 * t, orbp=(CX, WL - 30), rune=i * 2, mouth=.3, flap=2 + t)
            elif i < 11:
                t = (i - 9) / 1; P = dict(L=(18, 26), R=(-18, 26), kL=1.15, kR=1.15, orb=7 - 5 * t, orbp=(CX, WL - 24 + 12 * t), lean=0, bob=2, mouth=1)
            else:
                t = ease((i - 11) / 4); P = dict(L=lerp2((18, 26), REST_L, t), R=lerp2((-18, 26), REST_R, t), bob=round(2 * (1 - t)), mouth=.5 * (1 - t))
            P.setdefault('ph', i / n); P.setdefault('rune', i); out.append(P)
    elif kind == 'grab':                     # agarrao: braco direito avanca MUITO para a praia, fecha a mao e puxa de volta
        n = 20
        for i in range(n):
            if i < 6:
                t = ease(i / 5); P = dict(R=lerp2(REST_R, (24, 2), t), lean=-2 * t, tilt=-.4 * t, mouth=.4 * t)
            elif i < 9:
                t = (i - 6) / 2; P = dict(R=lerp2((24, 2), (2, 86), t), kR=1 + .45 * t, lean=-2 + 6 * t, mouth=1)
            elif i < 12:
                P = dict(R=(2, 86), kR=1.45, lean=4, mouth=.8, fistR=(i - 8) / 3)
            else:
                t = ease((i - 12) / 7); P = dict(R=lerp2((2, 86), (-4, 18), t), kR=1.45 - .45 * t, lean=4 - 4 * t, fistR=1 - t * .8, mouth=.5)
            P.setdefault('L', (-14, 22)); P.setdefault('ph', i / n); P.setdefault('rune', i); out.append(P)
    elif kind == 'roar':                     # Mare: abre os bracos, joga a cabeca para tras e ruge (runas acendem)
        n = 16
        for i in range(n):
            if i < 5: t = ease(i / 4); P = dict(L=lerp2(REST_L, (-36, -18), t), R=lerp2(REST_R, (36, -18), t), back=t, shrug=3 * t, mouth=t)
            elif i < 12: P = dict(L=(-38, -22 + (i % 2)), R=(38, -22 + ((i + 1) % 2)), back=1.2, shrug=3, mouth=1.2, flap=4, bob=-1, ring=(i - 5) * .18, lean=(i % 2) - .5)
            else: t = ease((i - 12) / 3); P = dict(L=lerp2((-38, -22), REST_L, t), R=lerp2((38, -22), REST_R, t), back=1.2 * (1 - t), shrug=3 * (1 - t), mouth=1.2 * (1 - t))
            P.setdefault('ph', i / n); P.setdefault('rune', i * 2); out.append(P)
    elif kind == 'dive':                     # mergulho: ergue os bracos, toma impulso e afunda (espuma alta, bolhas)
        n = 20
        for i in range(n):
            if i < 6: t = ease(i / 5); P = dict(L=lerp2(REST_L, (-20, -40, 1), t)[:2] + ((1,) if t > .6 else ()), R=lerp2(REST_R, (20, -40), t)[:2] + ((1,) if t > .6 else ()), bob=-3 * t, back=.6 * t, mouth=.5)
            else:
                t = ease((i - 6) / 13); P = dict(L=(-18, -42, 1), R=(18, -42, 1), sink=90 * t, foam=1 + 2 * (1 - abs(t - .4) / .6), ring=t,
                                                 bubbles=[(CX + 22 * math.sin(i * 1.7 + k), WL - 4 - ((i * 3 + k * 7) % 14), 1 + (k % 2)) for k in range(5)])
            P.setdefault('ph', i / n); out.append(P)
    elif kind == 'under':                    # submerso: so bolhas e ondulacao (loop)
        n = 8
        for i in range(n):
            out.append(dict(sink=120, foam=0, ring=.5 + .5 * ((i % 4) / 4), ph=i / n,
                            bubbles=[(CX - 20 + 10 * k + 2 * math.sin(i + k), WL - 2 - ((i * 2 + k * 5) % 10), 1 + (k + i) % 2) for k in range(5)]))
    elif kind == 'emerge':                   # sobe de uma vez com a onda, bracos abertos, ruge e se assenta
        n = 16
        for i in range(n):
            if i < 5: t = ease(i / 4); P = dict(sink=110 * (1 - t) - 4 * t, L=(-30, -30), R=(30, -30), mouth=1.2, back=1, foam=3, ring=t,
                                                  bubbles=[(CX + 30 * math.sin(k * 2.1), WL - 4 - k * 3, 2) for k in range(6)])
            elif i < 10: P = dict(sink=-4 + (i - 5), L=(-34, -26), R=(34, -26), mouth=1.2, back=1, foam=2, flap=4, ring=1 + (i - 5) * .15, shrug=3)
            else: t = ease((i - 10) / 5); P = dict(L=lerp2((-34, -26), REST_L, t), R=lerp2((34, -26), REST_R, t), mouth=1.2 * (1 - t), back=1 - t, foam=1 + (1 - t))
            P.setdefault('ph', i / n); P.setdefault('rune', i); out.append(P)
    elif kind == 'hurt':
        n = 9
        for i in range(n):
            t = math.sin(min(1, i / 6) * math.pi)
            out.append(dict(lean=round(-3 * t), bob=-round(2 * t), back=.7 * t, squint=1 if i < 6 else 0, mouth=.8 * t, L=(-16 - 6 * t, 20), R=(16 + 6 * t, 20), ph=i / n, shrug=2 * t))
    elif kind == 'death':                    # ruge de dor, desaba para a frente e afunda devagar, um braco por ultimo
        n = 20
        for i in range(n):
            if i < 5: t = ease(i / 4); P = dict(L=lerp2(REST_L, (-30, -24), t), R=lerp2(REST_R, (30, -24), t), back=1.2 * t, mouth=1.2, squint=1)
            elif i < 10: t = ease((i - 5) / 4); P = dict(L=lerp2((-30, -24), (-24, 30), t), R=lerp2((30, -24), (24, 30), t), back=1.2 - 1.6 * t, mouth=1 - .6 * t, squint=1, lean=2 * t, bob=3 * t)
            else:
                t = ease((i - 10) / 9); P = dict(sink=10 + 100 * t, L=(-20, 30), R=(10, -46, 0) if t < .85 else (10, -46), squint=1, lean=2, foam=1 + 1.5 * (1 - t), ring=t,
                                                 bubbles=[(CX + 18 * math.sin(i * 1.3 + k), WL - 3 - ((i * 2 + k * 5) % 12), 1 + k % 2) for k in range(4)])
            P.setdefault('ph', i / n); out.append(P)
    return [frame(P) for P in out]


KINDS = ['idle', 'slam', 'sweep', 'cast', 'grab', 'roar', 'dive', 'under', 'emerge', 'hurt', 'death']
VIEWS = ('d', 'u', 's')


def export(out_dir, sc=1):
    imgs, anims = [], {}
    for kind in KINDS:
        fr = seq(kind); idx = list(range(len(imgs), len(imgs) + len(fr))); imgs += fr
        for v in VIEWS: anims[f'{kind}_{v}'] = idx
    for v in VIEWS:          # nomes que o motor usa: parado/andar/ataque/conjurar/dano/morte
        anims[f'walk_{v}'] = anims[f'idle_{v}']; anims[f'attack_{v}'] = anims[f'slam_{v}']; anims[f'cast_{v}'] = anims[f'roar_{v}']
    bb = None
    for im in imgs:
        b = im.getbbox()
        if b: bb = b if bb is None else (min(bb[0], b[0]), min(bb[1], b[1]), max(bb[2], b[2]), max(bb[3], b[3]))
        if b and (b[1] <= 0 or b[0] <= 0 or b[2] >= W or b[3] >= H): print('AVISO: quadro toca a borda', b)
    x0, y0, x1, y1 = max(0, bb[0] - 1), max(0, bb[1] - 1), min(W, bb[2] + 1), min(H, bb[3] + 1)
    cw, ch = x1 - x0, y1 - y0; w, h = cw * sc, ch * sc; cols = max(1, 4000 // w); rows = (len(imgs) + cols - 1) // cols
    A = Image.new('RGBA', (cols * w, rows * h), (0, 0, 0, 0))
    for i, im in enumerate(imgs): A.alpha_composite(im.crop((x0, y0, x1, y1)).resize((w, h), Image.NEAREST), ((i % cols) * w, (i // cols) * h))
    A.save(os.path.join(out_dir, 'cx_mare_atlas.png'), optimize=True)
    json.dump(dict(w=w, h=h, ax=(CX - x0) * sc, ay=(WL - y0) * sc, cols=cols, anims=anims), open(os.path.join(out_dir, 'cx_mare_atlas.json'), 'w'))
    print('mare', len(imgs), 'quadros', A.size, os.path.getsize(os.path.join(out_dir, 'cx_mare_atlas.png')) // 1024, 'KB')


def sheet(path, kinds=None):
    rows = [seq(k) for k in (kinds or KINDS)]
    cols = max(len(r) for r in rows)
    S = Image.new('RGBA', (cols * W, len(rows) * H), (64, 120, 150, 255))
    from PIL import ImageDraw
    d = ImageDraw.Draw(S)
    for j in range(len(rows)): d.rectangle([0, j * H + WL, cols * W, j * H + H], fill=(196, 176, 120, 255))
    for j, r in enumerate(rows):
        for i, im in enumerate(r): S.alpha_composite(im, (i * W, j * H))
    S.resize((S.width * 2, S.height * 2), Image.NEAREST).save(path); print(path, S.size)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'sheet': sheet(sys.argv[2], sys.argv[3:] or None)
    else: export(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..', 'mmo', 'assets', 'chars')))
