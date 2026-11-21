#!/usr/bin/env python3
"""GIGANTE DAS COLINAS — animações (vista de frente), corpo montado em PEÇAS por cinemática (pernas, braços, tronco, cabeça) e redesenhado a cada quadro
no motor fauna.Cv (uma massa só) + pelo estilo grama (furpass) balançando por fase.
Uso: python3 gigante_anim.py preview out.gif   (todas as animações)   |   python3 gigante_anim.py sheet out.png"""
import sys, math
import numpy as np
from PIL import Image, ImageDraw
from multiprocessing import Pool
import fauna as FA
import colosso as CO
import furpass
import rotsprite as RS

PAL = dict(CO.PAL); FLAT = dict(CO.FLAT)
SK = 1.6                      # escala do gigante (mais pixels, não esticado)
DW, DH, XO, YO = 340, 500, 40, 70   # quadro de projeto (coordenadas do esboço + folga p/ braços e perna erguidos)
CX, FY = 130, 408              # centro e chão (coordenadas do esboço)

def _fast(cv):
    """ell/cap só dentro da caixa do elemento (bem mais rápido que o mgrid inteiro)"""
    H_, W_ = cv.reg.shape
    def ell(cx, cy, rx, ry, reg='body', far=False):
        r = cv.rid(reg); x0, x1 = max(0, int(cx - rx) - 1), min(W_, int(cx + rx) + 2); y0, y1 = max(0, int(cy - ry) - 1), min(H_, int(cy + ry) + 2)
        if x1 <= x0 or y1 <= y0: return
        ys, xs = np.mgrid[y0:y1, x0:x1]
        m = ((xs + .5 - cx) / rx) ** 2 + ((ys + .5 - cy) / ry) ** 2 <= 1
        cv.n += 1; sub = (slice(y0, y1), slice(x0, x1))
        cv.reg[sub][m] = r; cv.ord[sub][m] = cv.n; cv.part[sub][m] = cv.pid(r)
        if far: cv.far[sub][m] = True
    def cap(x0_, y0_, x1_, y1_, r0, r1, reg='body', far=False):
        r = cv.rid(reg); rm = max(r0, r1)
        bx0, bx1 = max(0, int(min(x0_, x1_) - rm) - 1), min(W_, int(max(x0_, x1_) + rm) + 2); by0, by1 = max(0, int(min(y0_, y1_) - rm) - 1), min(H_, int(max(y0_, y1_) + rm) + 2)
        if bx1 <= bx0 or by1 <= by0: return
        ys, xs = np.mgrid[by0:by1, bx0:bx1]
        px, py = xs + .5 - x0_, ys + .5 - y0_; dx, dy = x1_ - x0_, y1_ - y0_; L2 = dx * dx + dy * dy or 1
        t = np.clip((px * dx + py * dy) / L2, 0, 1); rr = r0 + (r1 - r0) * t
        m = (px - t * dx) ** 2 + (py - t * dy) ** 2 <= rr ** 2
        cv.n += 1; sub = (slice(by0, by1), slice(bx0, bx1))
        cv.reg[sub][m] = r; cv.ord[sub][m] = cv.n; cv.part[sub][m] = cv.pid(r)
        if far: cv.far[sub][m] = True
    cv.ell, cv.cap = ell, cap
    return cv

class Sc:
    def __init__(s, cv, k): s.cv, s.k = cv, k
    def ell(s, x, y, rx, ry, reg='body', far=False): s.cv.ell((x + XO) * s.k, (y + YO) * s.k, rx * s.k, ry * s.k, reg, far)
    def cap(s, x0, y0, x1, y1, r0, r1, reg='body', far=False): s.cv.cap((x0 + XO) * s.k, (y0 + YO) * s.k, (x1 + XO) * s.k, (y1 + YO) * s.k, r0 * s.k, max(1, r1 * s.k), reg, far)
    def dot(s, x, y, col): s.cv.dot((x + XO) * s.k, (y + YO) * s.k, col)

def tufts(c, x0, y0, x1, y1, n, sg, ln, r0=3.4, reg='fur'):
    for k in range(n):
        t = (k + .5) / n; x = x0 + (x1 - x0) * t; y = y0 + (y1 - y0) * t
        c.cap(x, y, x + sg * (4 + (k % 3)), y + ln + (k % 2) * 4, r0, 1, reg)

def v2(a, L):  # vetor a partir do eixo "para baixo", positivo = para fora
    return math.sin(a) * L, math.cos(a) * L

def draw(P, t=0.0, view='d'):
    back = view == 'u'
    FA.W, FA.H = int(DW * SK), int(DH * SK)
    cv = _fast(FA.Cv()); cv.contact = False
    c = Sc(cv, SK)
    g = lambda k, d=0.0: P.get(k, d)
    pr = g('prone')
    ox, oy = g('lean'), g('dy') + g('crouch') + pr * 110
    hx, hy, jaw = g('headx'), g('heady'), g('jaw')
    br = g('breath')
    cx = CX
    # ---- pernas (cinemática: quadril -> joelho -> pé)
    feet = []
    for sg, key in ((-1, 'L'), (1, 'R')):
        hip = (cx + sg * 36 + ox * .35, 216 + g('dy') + g('crouch') * .9)
        up = g('up' + key); sp = g('sp' + key)
        foot = (cx + sg * 36 + sp + ox * .15, FY - up)
        mid = ((hip[0] + foot[0]) / 2, (hip[1] + foot[1]) / 2)
        kn = (mid[0] + sg * (g('crouch') * .55 + g('bend' + key) * 26), mid[1] - up * .12)
        kl = g('kneel')
        if kl > 0:      # ajoelhado: joelho no chão, canela dobrada para trás (pé fica atrás/embaixo)
            kn = (hip[0] + sg * (26 + kl * 26), lerp(kn[1], FY - 18, kl)); foot = (kn[0] - sg * 6, lerp(foot[1], FY - 26, kl))
        c.cap(hip[0], hip[1], kn[0], kn[1], 31, 23, 'fur')
        tufts(c, hip[0] + sg * 29, hip[1] + 16, kn[0] + sg * 22, kn[1] - 8, 5, sg, 7, 3.4)
        tufts(c, hip[0] - sg * 26, hip[1] + 20, kn[0] - sg * 21, kn[1] - 6, 4, -sg, 7, 3.2)
        c.ell(kn[0], kn[1], 27, 22, 'fur'); c.ell(kn[0] - 8, kn[1] - 4, 9, 6, 'stone'); c.ell(kn[0] + 9, kn[1] + 8, 5, 4, 'moss')
        c.cap(kn[0], kn[1] + 4, foot[0], foot[1] - 20, 19, 15, 'body')
        tufts(c, kn[0] - 14, kn[1] + 16, kn[0] + 14, kn[1] + 18, 5, 1, 14, 2.8)
        feet.append(foot)
        fs = 1 - .25 * kl
        c.ell(foot[0], foot[1] - 11, 34 * fs, (13 - (3 if up > 40 else 0)) * fs, 'hoof')
        for kk in range(-2, 3): c.cap(foot[0] + kk * 12 * fs, foot[1] - 10, foot[0] + kk * 13 * fs, foot[1] - 2, 6.4 * fs, 5 * fs, 'hoof')
        for kk in range(-2, 3): c.cap(foot[0] + kk * 13 * fs, foot[1] - 4, foot[0] + kk * 14 * fs, foot[1] + 2, 2.6, 1.2, 'horn')
    # ---- tanga e tronco (tudo acompanha ox/oy)
    c.ell(cx + ox * .5, 222 + oy * .8, 78, 36, 'fur'); tufts(c, cx - 70 + ox * .5, 240 + oy * .8, cx + 70 + ox * .5, 242 + oy * .8, 14, 1, 22, 5)
    s = 1 + br * .02
    sy = 1 - .45 * pr; wx = 1 + .12 * pr          # caindo para frente: o tronco encurta (escorço) e alarga
    c.ell(cx + ox, 156 + oy + (1 - sy) * 50, 80 * s * wx, 80 * s * sy, 'body'); c.ell(cx + ox, 198 + oy - (1 - sy) * 20, 62 * s * wx, 46 * sy, 'body'); c.ell(cx + ox, 128 + oy + (1 - sy) * 40, 52 * s * wx, 34 * sy, 'fur')
    c.ell(cx + ox, 98 + oy + (1 - sy) * 36, 58 * wx, 22, 'fur')
    c.ell(cx + ox + hx * .5, 84 + oy + hy * .5, 46, 18, 'fur'); tufts(c, cx - 44 + ox + hx * .5, 90 + oy + hy * .5, cx + 44 + ox + hx * .5, 90 + oy + hy * .5, 10, 1, 18, 4.6)
    # ---- braços (cinemática: ombro -> cotovelo -> mão)
    hands = []
    for sg, key in ((-1, 'L'), (1, 'R')):
        S0 = (cx + sg * 80 + ox, 106 + oy)
        c.ell(S0[0], S0[1], 40, 33, 'stone'); c.ell(S0[0] - sg * 2, S0[1] - 8, 35, 26, 'fur')
        for q in range(3): c.cap(S0[0] + sg * (-12 + q * 11), S0[1] - 22, S0[0] + sg * (-8 + q * 12), S0[1] - 46 - q * 4, 6, 1.4, 'horn')
        c.ell(S0[0] + sg * 10, S0[1] - 18, 9, 6, 'moss')
        a1 = g('a1' + key, .10); e = g('e' + key, .0)
        sh = (S0[0] + sg * 10, S0[1] + 12)
        swv = g('s' + key)                                  # balanço PARA FRENTE(+)/TRÁS(-) no eixo da câmera: escorço, não de lado
        dx, dy = v2(a1, 82 * (1 - .28 * swv)); el = (sh[0] + sg * dx, sh[1] + dy - 6 * swv)
        fl = g('f' + key) + max(0, g('s' + key)) * .5                                   # flexão para a câmera: antebraço encurta (escorço) e o cotovelo salta
        dx2, dy2 = v2(a1 + e, 78 * (1 - .5 * fl) * (1 - .3 * swv)); hd = (el[0] + sg * dx2, el[1] + dy2 - 8 * swv)
        c.cap(sh[0], sh[1], el[0], el[1], 30, 23, 'body'); tufts(c, sh[0] + sg * 24, sh[1] + 12, el[0] + sg * 22, el[1] - 4, 5, sg, 10, 3.4)
        c.ell(el[0], el[1], 25 * (1 + .22 * fl), 22 * (1 + .22 * fl), 'fur')
        if abs(e) > .35 or fl > .25:                        # dobra visível no cotovelo (sombra da dobra + calombo)
            c.ell(el[0] - sg * 4, el[1] + 8, 13 + 6 * fl, 7, 'far'); c.ell(el[0] + sg * 8, el[1] - 6, 8, 6, 'stone')
        c.cap(el[0], el[1], hd[0], hd[1], 23 + 4 * fl, 17, 'body')
        mx, my = (el[0] * .35 + hd[0] * .65), (el[1] * .35 + hd[1] * .65)
        c.ell(mx, my, 24, 6, 'stone')
        tufts(c, el[0] - 16, el[1] + 18, el[0] + 18, el[1] + 20, 5, 1, 14, 3.2)
        c.ell(hd[0], hd[1] + 4, 26 * (1 + .1 * fl) * (1 + .2 * swv), 28 * (1 + .1 * fl) * (1 + .2 * swv), 'skin')
        ux, uy = math.sin(a1 + e) * sg, math.cos(a1 + e)   # direção da mão
        px_, py_ = -uy * sg, ux * sg
        for q in range(4):
            off = (q - 1.5) * 10
            bx, by = hd[0] + px_ * off, hd[1] + 4 + py_ * off
            c.cap(bx, by, bx + ux * 24, by + uy * 24, 5.6, 4, 'skin'); c.cap(bx + ux * 22, by + uy * 22, bx + ux * 31, by + uy * 31, 2.4, 1, 'horn')
        hands.append(hd)
    # ---- cabeça
    H0 = (cx + ox + hx, 56 + oy + hy + pr * 18)
    c.ell(H0[0], H0[1], 37, 34, 'fur'); c.ell(H0[0], H0[1] + 6, 29, 29, 'body')
    for sg in (-1, 1):
        c.cap(H0[0] + sg * 28, H0[1] - 18, H0[0] + sg * 46, H0[1] - 40, 8, 4.8, 'horn'); c.cap(H0[0] + sg * 46, H0[1] - 40, H0[0] + sg * 49, H0[1] - 68, 4.8, 1.2, 'horn')
        c.cap(H0[0] + sg * 36, H0[1], H0[0] + sg * 56, H0[1] - 4, 5, 3, 'horn'); c.cap(H0[0] + sg * 56, H0[1] - 4, H0[0] + sg * 64, H0[1] - 20, 3, 1, 'horn')
    c.ell(H0[0] - 18, H0[1] - 10, 12, 7, 'stone'); c.ell(H0[0] + 18, H0[1] - 12, 13, 8, 'moss')
    if back:
        c.ell(H0[0], H0[1] + 8, 33, 30, 'fur'); tufts(c, H0[0] - 26, H0[1] + 22, H0[0] + 26, H0[1] + 26, 8, 1, 16, 4)
    else:
      c.ell(H0[0], H0[1] + 22, 18, 11, 'skin'); c.ell(H0[0], H0[1] + 34 + jaw * 12, 21, 10 + jaw * 4, 'body')
      for sg in (-1, 1):
        c.cap(H0[0] + sg * 12, H0[1] + 34 + jaw * 11, H0[0] + sg * 14, H0[1] + 20 - jaw * 2, 3.2, 1.4, 'tusk')
        c.cap(H0[0] + sg * 36, H0[1] + 14, H0[0] + sg * 42, H0[1] + 40, 6, 3, 'fur')
    if not back: tufts(c, H0[0] - 20, H0[1] + 40 + jaw * 12, H0[0] + 20, H0[1] + 42 + jaw * 12, 5, 1, 12, 3.2)
    # musgo e pedras
    for (mx, my, a, b_) in ((cx - 52, 122, 12, 8), (cx + 40, 168, 9, 6), (cx + 64, 150, 7, 5)): c.ell(mx + ox, my + oy, a, b_, 'moss')
    c.ell(cx - 22 + ox, 232 + oy, 8, 5, 'stone'); c.ell(cx + 54 + ox, 120 + oy, 7, 5, 'stone')
    # runas e olhos (brilham mais no rugido)
    glow = g('glow')
    for (rx, ry) in (() if back else ((cx - 30, 134), (cx + 24, 144), (cx - 4, 164), (cx + 40, 120), (cx - 46, 178), (cx + 14, 188), (cx - 8, 206))):
        for dx_, dy_ in ((0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1)) + (((2, 0), (0, 2), (-2, 0), (0, -2)) if glow > .5 else ()): c.dot(rx + ox + dx_, ry + oy + dy_, FLAT['rune'])
        c.dot(rx + ox, ry + oy, FLAT['eye2'])
    for ex in (() if back else (-13, 13)):
        for dx_ in (-2, -1, 0, 1, 2, 3):
            for dy_ in (0, 1, 2): c.dot(H0[0] + ex + dx_, H0[1] + dy_, FLAT['eye'])
        c.dot(H0[0] + ex, H0[1] + 1, FLAT['eye2']); c.dot(H0[0] + ex + 1, H0[1] + 1, FLAT['eye2'])
    # pelo (grama) e render
    def add(x, y, x2, y2, r0, r1): cv.cap(x, y, x2, y2, r0, r1, 'fur')
    img = furpass.apply(lambda: cv.render(PAL, FLAT), add, t=t, k=SK)
    return img

# ------------------------------------------------------------------ sequências de pose
def ease(u): u = max(0, min(1, u)); return u * u * (3 - 2 * u)
def lerp(a, b, u): return a + (b - a) * u

def seq(name):
    o = []
    if name == 'idle':
        for i in range(16):
            ph = i / 16 * 2 * math.pi
            o.append(dict(breath=math.sin(ph), dy=-1.5 * math.sin(ph), lean=2 * math.sin(ph * .5 + 1), a1L=.10 + .03 * math.sin(ph + 1), a1R=.10 + .03 * math.sin(ph + 2.2), eL=.25 + .06 * math.sin(ph), eR=.25 + .06 * math.sin(ph + 1.5), fL=.18, fR=.18, headx=math.sin(ph) * 1.5, heady=1.2 * math.sin(ph + .5), _t=ph))
    elif name == 'walk':
        for i in range(24):
            ph = i / 24 * 2 * math.pi; sn = math.sin(ph)
            # braços pendurados e RELAXADOS: só balançam um pouco (o da frente avança em escorço), sem abrir de lado
            o.append(dict(dy=-abs(sn) * 7, lean=sn * 7, upL=max(0, sn) * 30, upR=max(0, -sn) * 30, bendL=max(0, sn) * .6, bendR=max(0, -sn) * .6,
                          a1L=.07, a1R=.07, sL=-.42 * sn, sR=.42 * sn, eL=.2, eR=.2, fL=.1, fR=.1, heady=math.sin(ph * 2) * 1.5, breath=math.sin(ph * 2), _t=ph * 1.3))
    elif name == 'stomp':     # ergue a perna direita, bate o pé no chão, o corpo cede e treme
        for i in range(24):
            if i < 11: u = ease(i / 10); P = dict(upR=95 * u, bendR=.9 * u, lean=-14 * u, crouch=-4 * u, a1L=.1 + .6 * u, a1R=.1 + .9 * u, eL=.3 + .7 * u, eR=.3 + .8 * u, fL=.5 * u, fR=.4 * u, headx=-3 * u, heady=-3 * u, glow=u)
            elif i < 13: P = dict(upR=95, bendR=.9, lean=-14, crouch=-4, a1L=.7, a1R=1.0, eL=1.0, eR=1.1, fL=.5, fR=.4, glow=1, headx=-3, heady=-3)
            elif i < 15: u = (i - 12) / 2; P = dict(upR=95 * (1 - u), bendR=.9 * (1 - u), lean=lerp(-14, 8, u), crouch=lerp(-4, 22, u), a1L=lerp(.7, .3, u), a1R=lerp(1.0, .3, u), eL=lerp(1.0, .3, u), eR=lerp(1.1, .3, u), fL=.3, fR=.3, headx=2, heady=lerp(-3, 8, u), jaw=.5 * u)
            elif i < 19: u = (i - 14) / 4; P = dict(lean=8 - 3 * u, crouch=22 - 6 * u, a1L=.3, a1R=.3, eL=.3, eR=.3, fL=.3, fR=.3, heady=8 - 4 * u, jaw=.5 * (1 - u), shake=(1 if i % 2 else -1) * 3 * (1 - u))
            else: u = ease((i - 18) / 5); P = dict(lean=lerp(5, 0, u), crouch=lerp(16, 0, u), a1L=lerp(.3, .1, u), a1R=lerp(.3, .1, u), heady=lerp(4, 0, u))
            P['lean'] = P.get('lean', 0) + P.get('shake', 0); P['_t'] = i * .5; o.append(P)
    elif name == 'smash':     # os dois braços sobem, descem esmagando; corpo inclina e treme no impacto
        for i in range(24):
            if i < 11: u = ease(i / 10); P = dict(a1L=lerp(.1, 2.6, u), a1R=lerp(.1, 2.6, u), eL=lerp(.25, 1.5, u), eR=lerp(.25, 1.5, u), fL=.5 * u, fR=.5 * u, crouch=-6 * u, lean=-6 * u, heady=-4 * u, jaw=.4 * u, glow=u, breath=u)
            elif i < 13: P = dict(a1L=2.6, a1R=2.6, eL=1.5, eR=1.5, fL=.5, fR=.5, crouch=-6, lean=-6, heady=-4, jaw=.5, glow=1)
            elif i < 15: u = (i - 12) / 2; P = dict(a1L=lerp(2.6, .35, u), a1R=lerp(2.6, .35, u), eL=lerp(1.5, .2, u), eR=lerp(1.5, .2, u), fL=lerp(.5, .1, u), fR=lerp(.5, .1, u), crouch=lerp(-6, 26, u), lean=0, heady=lerp(-4, 12, u), jaw=.6)
            elif i < 19: u = (i - 14) / 4; P = dict(a1L=.35, a1R=.35, crouch=26 - 8 * u, heady=12 - 5 * u, jaw=.4 * (1 - u), shake=(1 if i % 2 else -1) * 4 * (1 - u))
            else: u = ease((i - 18) / 5); P = dict(a1L=lerp(.35, .1, u), a1R=lerp(.35, .1, u), crouch=lerp(18, 0, u), heady=lerp(7, 0, u))
            P['lean'] = P.get('lean', 0) + P.get('shake', 0); P['_t'] = i * .6; o.append(P)
    elif name == 'sweep':     # SOCO NO CHÃO: levanta o punho, desce o corpo todo (agacha e curva) e bate a mão no chão
        for i in range(24):
            if i < 9: u = ease(i / 8); P = dict(a1R=lerp(.1, 1.5, u), eR=lerp(.25, -1.3, u), fR=.4 * u, lean=-10 * u, a1L=.1 + .2 * u, eL=.5, fL=.3, heady=-2 * u, glow=u)
            elif i < 12: u = ease((i - 8) / 3); P = dict(a1R=lerp(1.5, .12, u), eR=lerp(-1.3, .05, u), fR=0, lean=lerp(-10, 12, u), a1L=.3, eL=.5, fL=.3, crouch=118 * u, bendL=.8 * u, bendR=.8 * u, heady=10 * u, jaw=.4 * u)
            elif i < 18: u = (i - 12) / 5; P = dict(a1R=.12, eR=.05, a1L=.3, eL=.5, fL=.3, lean=12, crouch=118, bendL=.8, bendR=.8, heady=10, shake=(1 if i % 2 else -1) * 3 * (1 - u))
            else: u = ease((i - 17) / 6); P = dict(a1R=lerp(.12, .1, u), eR=lerp(.05, .25, u), a1L=lerp(.3, .1, u), lean=lerp(12, 0, u), crouch=lerp(118, 0, u), bendL=lerp(.8, 0, u), bendR=lerp(.8, 0, u), heady=lerp(10, 0, u))
            P['lean'] = P.get('lean', 0) + P.get('shake', 0); P['_t'] = i * .5; o.append(P)
    elif name == 'roar':
        for i in range(20):
            u = ease(min(1, i / 7)) * (1 - ease((i - 15) / 5) if i > 15 else 1)
            sh = (1 if i % 2 else -1) * 2.5 * u if 7 <= i <= 15 else 0
            o.append(dict(a1L=.1 + .8 * u, a1R=.1 + .8 * u, eL=.3 + 1.0 * u, eR=.3 + 1.0 * u, fL=.35 * u, fR=.35 * u, heady=-7 * u, jaw=1.0 * u, breath=2 * u, glow=u, lean=sh, crouch=-3 * u, _t=i * .8))
    elif name == 'hurt':
        for i in range(10):
            u = math.sin(min(1, i / 6) * math.pi)
            o.append(dict(lean=10 * u, headx=8 * u, heady=-4 * u, a1L=.1 + .4 * u, a1R=.1 + .4 * u, eL=.3 + .7 * u, eR=.3 + .7 * u, fL=.4 * u, fR=.4 * u, crouch=4 * u, jaw=.5 * u, _t=i * .7, _flash=1 if i == 1 else 0))
    elif name == 'death':     # cambaleia, as pernas cedem, ajoelha, tomba PARA FRENTE (para a câmera) e deita
        for i in range(32):
            if i < 8: u = ease(i / 7); P = dict(lean=10 * math.sin(u * 3), crouch=lerp(0, 22, u), bendL=.5 * u, bendR=.5 * u, heady=5 * u, a1L=.1 + .4 * u, a1R=.1 + .4 * u, eL=.3 + .5 * u, eR=.3 + .5 * u, fL=.3 * u, fR=.3 * u, jaw=.5 * u)
            elif i < 15: u = ease((i - 8) / 6); P = dict(lean=lerp(0, -6, u), crouch=lerp(22, 74, u), kneel=u, heady=lerp(5, 14, u), a1L=.5, a1R=.5, eL=.8, eR=.8, fL=.3, fR=.3, jaw=.8, bendL=.5, bendR=.5)
            elif i < 17: P = dict(lean=-4 + 5 * math.sin((i - 15) * 2.2), crouch=74, kneel=1, heady=lerp(14, 20, (i - 15) / 2), a1L=.3, a1R=.3, eL=.25, eR=.25, sL=-.5, sR=-.5, fL=.2, fR=.2, jaw=.8, bendL=.5, bendR=.5)      # pausa ajoelhado
            elif i < 25: u = ((i - 17) / 7) ** 2; P = dict(lean=lerp(-4, 0, u), crouch=74 + 6 * u, kneel=1, prone=u, heady=lerp(14, 30, u), a1L=lerp(.5, .9, u), a1R=lerp(.5, .9, u), eL=lerp(.8, .3, u), eR=lerp(.8, .3, u), fL=lerp(.3, .6, u), fR=lerp(.3, .6, u), jaw=.4 * (1 - u), bendL=.5, bendR=.5)
            else: u = (i - 25) / 6; P = dict(crouch=80, kneel=1, prone=1 - .09 * abs(math.sin(u * math.pi * 2)) * (1 - u), heady=30, a1L=.9, a1R=.9, eL=.3, eR=.3, fL=.6, fR=.6, jaw=0, bendL=.5, bendR=.5, shake=(1 if i % 2 else -1) * 2.5 * (1 - u))
            P['lean'] = P.get('lean', 0) + P.get('shake', 0); P['_t'] = i * .35; o.append(P)
    return o


# ------------------------------------------------------------------ VISTA DE LADO (perfil, virado para a direita; a esquerda é espelho)
def draw_side(P, t=0.0):
    FA.W, FA.H = int(DW * SK), int(DH * SK)
    cv = _fast(FA.Cv()); cv.contact = False
    c = Sc(cv, SK)
    g = lambda k, d=0.0: P.get(k, d)
    cx = CX; ox = g('lean'); oy = g('dy') + g('crouch'); br = g('breath'); hx, hy, jaw = g('headx'), g('heady'), g('jaw')
    def leg(hipx, stp, up, far):
        reg = 'far' if far else 'fur'; hip = (hipx + ox * .3, 216 + oy * .9); foot = (hip[0] + stp, FY - up)
        kn = ((hip[0] + foot[0]) / 2 + 16, (hip[1] + foot[1]) / 2 - up * .12)
        c.cap(hip[0], hip[1], kn[0], kn[1], 29, 22, reg); c.ell(kn[0], kn[1], 24, 21, reg)
        if not far: c.ell(kn[0] + 4, kn[1] - 3, 8, 6, 'stone')
        c.cap(kn[0], kn[1] + 4, foot[0] - 2, foot[1] - 18, 19, 14, 'far' if far else 'body')
        tufts(c, kn[0] - 14, kn[1] + 10, kn[0] - 10, kn[1] + 40, 4, -1, 8, 3)
        c.ell(foot[0] + 12, foot[1] - 11, 38, 13, 'hoof')
        for kk in range(3): c.cap(foot[0] + 26 + kk * 8, foot[1] - 9, foot[0] + 38 + kk * 8, foot[1] - 2, 5, 3.4, 'hoof'); c.cap(foot[0] + 38 + kk * 8, foot[1] - 4, foot[0] + 44 + kk * 8, foot[1] + 1, 2.4, 1.2, 'horn')
    leg(cx - 10, g('stF'), g('upF'), True); leg(cx + 8, g('stN'), g('upN'), False)
    # braço de trás (atrás do tronco)
    def arm(a1, e, far):
        sh = (cx + 4 + ox, 120 + oy); reg = 'far' if far else 'body'
        el = (sh[0] + math.sin(a1) * 82, sh[1] + math.cos(a1) * 82); hd = (el[0] + math.sin(a1 + e) * 78, el[1] + math.cos(a1 + e) * 78)
        c.cap(sh[0], sh[1], el[0], el[1], 28, 22, 'far' if far else 'body'); c.ell(el[0], el[1], 22, 20, 'far' if far else 'fur')
        c.cap(el[0], el[1], hd[0], hd[1], 22, 17, reg); c.ell(hd[0], hd[1] + 4, 25, 27, 'far' if far else 'skin')
        if not far:
            ux, uy = math.sin(a1 + e), math.cos(a1 + e)
            for q in range(3):
                off = (q - 1) * 11; bx, by = hd[0] + uy * off * -1, hd[1] + 4 + ux * off
                c.cap(bx, by, bx + ux * 22, by + uy * 22, 5.4, 4, 'skin'); c.cap(bx + ux * 21, by + uy * 21, bx + ux * 29, by + uy * 29, 2.4, 1, 'horn')
    arm(g('aF'), g('eF', .25), True)
    # tanga, tronco, corcunda, barriga
    c.ell(cx + ox * .5, 222 + oy * .8, 58, 34, 'fur'); tufts(c, cx - 52 + ox * .5, 240 + oy * .8, cx + 52 + ox * .5, 242 + oy * .8, 10, 1, 20, 5)
    s0 = 1 + br * .02
    c.ell(cx + ox, 160 + oy, 56 * s0, 82 * s0, 'body'); c.ell(cx - 28 + ox, 116 + oy, 44, 40, 'fur'); c.ell(cx + 16 + ox, 178 + oy, 40 * s0, 50 * s0, 'fur')
    c.ell(cx - 6 + ox, 152 + oy, 36, 60, 'fur')
    tufts(c, cx - 50 + ox, 130 + oy, cx - 36 + ox, 220 + oy, 7, -1, 16, 4.4)          # franja de pelo nas costas
    # ombro de pedra com espinhos + musgo
    c.ell(cx + 2 + ox, 112 + oy, 36, 28, 'stone'); c.ell(cx + ox, 106 + oy, 32, 22, 'fur')
    for q in range(3): c.cap(cx - 12 + q * 12 + ox, 92 + oy, cx - 8 + q * 13 + ox, 66 - q * 4 + oy, 6, 1.4, 'horn')
    c.ell(cx + 8 + ox, 100 + oy, 9, 6, 'moss'); c.ell(cx + 20 + ox, 170 + oy, 8, 6, 'moss'); c.ell(cx - 10 + ox, 200 + oy, 7, 5, 'stone')
    # pescoço + cabeça (focinho para a direita)
    H0 = (cx + 20 + ox + hx, 62 + oy + hy)
    c.cap(cx + 2 + ox, 112 + oy, H0[0] - 6, H0[1] + 10, 26, 22, 'fur')
    c.ell(H0[0], H0[1], 36, 33, 'fur'); c.ell(H0[0] + 8, H0[1] + 6, 28, 26, 'body')
    c.ell(H0[0] + 34, H0[1] + 14, 21, 14, 'skin'); c.ell(H0[0] + 26, H0[1] + 28 + jaw * 10, 19, 9 + jaw * 3, 'body')
    c.cap(H0[0] + 30, H0[1] + 27 + jaw * 9, H0[0] + 36, H0[1] + 6, 3.4, 1.4, 'tusk')
    c.cap(H0[0] + 12, H0[1] - 26, H0[0] + 28, H0[1] - 50, 7, 4, 'horn'); c.cap(H0[0] + 28, H0[1] - 50, H0[0] + 30, H0[1] - 74, 4, 1.2, 'horn')
    c.cap(H0[0] - 6, H0[1] - 24, H0[0] - 26, H0[1] - 46, 8.4, 5, 'horn'); c.cap(H0[0] - 26, H0[1] - 46, H0[0] - 32, H0[1] - 72, 5, 1.2, 'horn')
    c.cap(H0[0] - 14, H0[1] + 6, H0[0] - 34, H0[1] + 16, 5, 3, 'horn')
    c.ell(H0[0] - 16, H0[1] - 10, 11, 7, 'stone'); c.ell(H0[0] + 6, H0[1] - 14, 10, 7, 'moss')
    tufts(c, H0[0] - 36, H0[1] + 8, H0[0] - 8, H0[1] + 38, 6, -1, 15, 4)               # juba
    for dx_ in (0, 1, 2, 3):
        for dy_ in (0, 1, 2): c.dot(H0[0] + 22 + dx_, H0[1] + 4 + dy_, FLAT['eye'])
    c.dot(H0[0] + 24, H0[1] + 5, FLAT['eye2'])
    for (rx, ry) in ((cx + 6, 140), (cx + 22, 168), (cx - 4, 190)): c.dot(rx + ox, ry + oy, FLAT['rune']); c.dot(rx + ox + 1, ry + oy, FLAT['eye2'])
    arm(g('aN'), g('eN', .25), False)
    def add(x, y, x2, y2, r0, r1): cv.cap(x, y, x2, y2, r0, r1, 'fur')
    return furpass.apply(lambda: cv.render(PAL, FLAT), add, t=t, k=SK)

def seq_side(name):
    o = []
    if name == 'idle':
        for i in range(8):
            ph = i / 8 * 2 * math.pi; o.append(dict(breath=math.sin(ph), dy=-1.5 * math.sin(ph), lean=1.5 * math.sin(ph * .5 + 1), aN=.1 + .04 * math.sin(ph + 1), aF=.1 + .04 * math.sin(ph + 2.2), eN=.25, eF=.25, heady=1.2 * math.sin(ph + .5), _t=ph))
    elif name == 'walk':
        for i in range(12):
            ph = i / 12 * 2 * math.pi; sn, cs = math.sin(ph), math.cos(ph)
            o.append(dict(dy=-abs(sn) * 7, lean=3 + sn * 3, stN=44 * cs, upN=30 * max(0, -sn), stF=-44 * cs, upF=30 * max(0, sn), aN=-.5 * cs, aF=.5 * cs, eN=.3 + .25 * max(0, cs), eF=.3 + .25 * max(0, -cs),
                          heady=math.sin(ph * 2) * 1.5, breath=math.sin(ph * 2), _t=ph * 1.3))
    elif name == 'hurt':
        for i in range(10):
            u = ease(min(1, i / 2)) * (1 - ease(max(0, (i - 4) / 5))); o.append(dict(lean=-16 * u, headx=-6 * u, heady=-8 * u, jaw=.6 * u, aN=.1 + .5 * u, aF=.1 + .5 * u, eN=.3 + .5 * u, eF=.3 + .5 * u, crouch=4 * u, _t=i * .7, _flash=1 if i == 1 else 0))
    return o

DWpx, DHpx = int(DW * SK), int(DH * SK)
OUT_W, OUT_H = int(DW * SK * 1.45), int(DH * SK)    # quadro final (largo p/ a queda lateral)

def frame(args):
    name, i, P = args
    img = draw(P, P.get('_t', 0))
    can = Image.new('RGBA', (OUT_W, OUT_H), (0, 0, 0, 0))
    fall = None
    if fall is None:
        can.alpha_composite(img, ((OUT_W - DWpx) // 2, 0))
    else:      # queda: gira em torno dos pés (RotSprite), acelerando (gravidade), com quique no fim
        u = min(1, fall); ang = 90 * (u * u) if u < .86 else 90 + (math.sin((u - .86) / .14 * math.pi) * -4)
        base = Image.new('RGBA', (OUT_W, OUT_H), (0, 0, 0, 0)); base.alpha_composite(img, ((OUT_W - DWpx) // 2, 0))
        piv = ((OUT_W) // 2 + int(P.get('lean', 0)) * 0, int((FY + YO) * SK))
        can = RS.rotate(base, ang, piv)
    return can

def build(names=None, pool=True):
    names = names or ['idle', 'walk', 'stomp', 'smash', 'sweep', 'roar', 'hurt', 'death']
    jobs = [(n, i, P) for n in names for i, P in enumerate(seq(n))]
    with Pool(4) as p: imgs = p.map(frame, jobs, chunksize=3)
    out = {n: [] for n in names}
    for (n, i, P), im in zip(jobs, imgs): out[n].append(im)
    return out

def preview(path, names=None, hero=None):
    out = build(names)
    from PIL import ImageFont
    fr = []
    BG = (92, 120, 84, 255)
    sc = .5
    W_, H_ = int(OUT_W * sc), int(OUT_H * sc)
    try: ft = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 15)
    except Exception: ft = None
    for n, lst in out.items():
        rep = 2 if n in ('idle', 'walk') else 1
        for _ in range(rep):
            for im in lst:
                f = Image.new('RGBA', (W_, H_ + 22), BG)
                f.alpha_composite(im.resize((W_, H_), Image.NEAREST), (0, 22))
                d = ImageDraw.Draw(f); d.text((6, 3), n.upper() + f'  ({len(lst)} quadros)', fill=(255, 240, 200, 255), font=ft)
                fr.append(f.convert('P', palette=Image.ADAPTIVE, colors=64))
    fr[0].save(path, save_all=True, append_images=fr[1:], duration=50, loop=0, optimize=False, disposal=2)
    print(path, len(fr), 'quadros', {k: len(v) for k, v in out.items()})
    return out

# ------------------------------------------------------------------ atlas do jogo (escala de jogo SK=.6, 3 vistas; costas só em parado/andar/dano, o resto cai na frente)
def export(out_dir='../../../../mmo/assets/chars'):
    import json, os
    global SK
    SK = .6
    front = ['idle', 'walk', 'stomp', 'smash', 'sweep', 'roar', 'hurt', 'death']
    backn = ['idle', 'walk', 'hurt']
    sidn = ['idle', 'walk', 'hurt']
    jobs = [(n, i, P, 'd') for n in front for i, P in enumerate(seq(n))] + [(n, i, P, 'u') for n in backn for i, P in enumerate(seq(n))] + [(n, i, P, 's') for n in sidn for i, P in enumerate(seq_side(n))]
    with Pool(4) as p: imgs = p.map(_fv, jobs, chunksize=3)
    w, h = int(DW * SK), int(DH * SK); cols = 20; rows = -(-len(imgs) // cols)
    A = Image.new('RGBA', (cols * w, rows * h), (0, 0, 0, 0)); idx = {}
    for k, ((n, i, P, v), im) in enumerate(zip(jobs, imgs)):
        A.alpha_composite(im, ((k % cols) * w, (k // cols) * h)); idx.setdefault((n, v), []).append(k)
    an = {}
    alias = {'attack': 'smash', 'cast': 'roar'}
    for nm in front + list(alias):
        src = alias.get(nm, nm)
        f = idx[(src, 'd')]
        b = idx.get((src, 'u'), f)
        an[nm + '_d'] = f; an[nm + '_s'] = idx.get((src, 's'), f); an[nm + '_u'] = b
    d = idx[('death', 'd')]; an['kneel_d'] = an['kneel_s'] = an['kneel_u'] = d[:17]
    for v in 'dsu': an['death_' + v] = d[17:]      # a morte do jogo parte do joelho no chão (ele só morre ajoelhado)
    assert A.width <= 4096 and A.height <= 4096, A.size
    A.save(os.path.join(out_dir, 'cx_gigante_atlas.png'), optimize=True)
    json.dump(dict(w=w, h=h, ax=(CX + XO) * SK, ay=(FY + YO) * SK, cols=cols, anims=an), open(os.path.join(out_dir, 'cx_gigante_atlas.json'), 'w'))
    print('gigante', len(imgs), 'quadros', A.size)

def _fv(a):
    n, i, P, v = a
    global SK
    SK = .6
    return draw_side(P, P.get('_t', 0)) if v == 's' else draw(P, P.get('_t', 0), v)


if __name__ == '__main__':
    if sys.argv[1] == 'preview': preview(sys.argv[2], sys.argv[3].split(',') if len(sys.argv) > 3 else None)
    elif sys.argv[1] == 'export': export()
    elif sys.argv[1] == 'one':
        P = seq(sys.argv[3])[int(sys.argv[4])]; frame((sys.argv[3], 0, P)).save(sys.argv[2])

