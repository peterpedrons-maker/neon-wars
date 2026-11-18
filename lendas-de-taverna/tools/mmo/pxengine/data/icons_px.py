#!/usr/bin/env python3
"""Ícones de ITEM e de INTERFACE em pixel art, 100% por código (32x32 nativos, ampliados x3 = 96px, mesmo nome dos antigos).
Estilo único: contorno escuro por forma, 3 tons (luz em cima/esquerda, sombra embaixo/direita), brilho em 1 pixel.
Uso: python3 icons_px.py [nome ...]   (sem argumentos gera todos em mmo/assets/ico e os ícones de UI em assets/ui-icons)"""
import math, os, sys
import numpy as np
from PIL import Image, ImageDraw

N = 32
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
ICO = os.path.join(ROOT, 'assets', 'ico')
UIDIR = os.path.join(ROOT, 'assets', 'ui-icons')


def hx(h):
    if not isinstance(h, str): return tuple(h)
    h = h.lstrip('#'); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def R(o, d, m, l): return tuple(hx(c) for c in (o, d, m, l))


STEEL = R('#1a2030', '#566680', '#9aaac6', '#e6f0ff'); DSTEEL = R('#12161f', '#3a4458', '#6a7890', '#b4c2da'); GOLD = R('#4a2808', '#a8701a', '#f0b82c', '#fff2a8')
WOOD = R('#24120a', '#52301a', '#84562c', '#b8844c'); LEATH = R('#2a1408', '#6a3a18', '#a46a30', '#d69a58'); DLEATH = R('#1e1008', '#4a2a12', '#764a22', '#a0743a')
RED = R('#2a0c14', '#7a1c2c', '#c43040', '#f07080'); BLUE = R('#0c1a3a', '#1c3e88', '#3a72d0', '#80b4f4'); GREEN = R('#0c2410', '#1c5a2c', '#3c9a48', '#88d878')
PURP = R('#180c34', '#44288a', '#7a50d0', '#c0a0ff'); CREAM = R('#2a2030', '#8a7a78', '#d8ccb8', '#fff8e8'); GRAY = R('#1c1c24', '#4a4a58', '#7e7e90', '#c0c0d0')
BONE = R('#2a2030', '#8a8098', '#d8d0e0', '#ffffff'); BLACK = R('#08080e', '#1c1c2c', '#34344c', '#5c5c80'); TEAL = R('#082a30', '#14606a', '#28a0a8', '#80e8e0')
ORANGE = R('#2a1004', '#8a3c0c', '#e07818', '#ffc060'); PINK = R('#2a0c20', '#8a2860', '#e0509a', '#ffa8d4'); CYAN = R('#082838', '#1c6a9a', '#40b8e8', '#b8f0ff')


class Cv:
    def __init__(s): s.px = np.zeros((N, N, 4), np.uint8)

    def _m(s, fn):
        m = Image.new('L', (N, N), 0); fn(ImageDraw.Draw(m)); return np.array(m) > 127

    def put(s, m, ramp, outline=True, light=True):
        O, D, M, L = ramp; p = np.pad(m, 1); u, d, l, r = p[:-2, 1:-1], p[2:, 1:-1], p[1:-1, :-2], p[1:-1, 2:]
        if outline:
            out = (~m) & (u | d | l | r)
            s.px[out] = (*O, 255)
        tl = m & (~u | ~l); br = m & (~d | ~r)
        s.px[m] = (*M, 255)
        if light:
            s.px[tl & ~br] = (*L, 255); s.px[br & ~tl] = (*D, 255)
            s.px[tl & br] = (*M, 255)
        return m

    def poly(s, pts, ramp, **k): return s.put(s._m(lambda d: d.polygon([tuple(p) for p in pts], fill=255)), ramp, **k)
    def ell(s, box, ramp, **k): return s.put(s._m(lambda d: d.ellipse(box, fill=255)), ramp, **k)
    def rect(s, box, ramp, **k): return s.put(s._m(lambda d: d.rectangle(box, fill=255)), ramp, **k)
    def rrect(s, box, r, ramp, **k): return s.put(s._m(lambda d: d.rounded_rectangle(box, r, fill=255)), ramp, **k)
    def arc(s, box, a0, a1, w, ramp, **k): return s.put(s._m(lambda d: d.arc(box, a0, a1, fill=255, width=w)), ramp, **k)

    def seg(s, p0, p1, w, ramp, **k):
        (x0, y0), (x1, y1) = p0, p1; L = math.hypot(x1 - x0, y1 - y0) or 1; nx, ny = -(y1 - y0) / L * w / 2, (x1 - x0) / L * w / 2
        return s.poly([(x0 + nx, y0 + ny), (x1 + nx, y1 + ny), (x1 - nx, y1 - ny), (x0 - nx, y0 - ny)], ramp, **k)

    def blade(s, p0, p1, w, ramp, tip=3.5, **k):
        (x0, y0), (x1, y1) = p0, p1; L = math.hypot(x1 - x0, y1 - y0) or 1; dx, dy = (x1 - x0) / L, (y1 - y0) / L; nx, ny = -dy * w / 2, dx * w / 2
        return s.poly([(x0 + nx, y0 + ny), (x1 + nx, y1 + ny), (x1 + dx * tip, y1 + dy * tip), (x1 - nx, y1 - ny), (x0 - nx, y0 - ny)], ramp, **k)

    def dot(s, x, y, c):
        c = hx(c) if isinstance(c, str) else c; s.px[y, x] = (c[0], c[1], c[2], 255)
    def dots(s, pts, c):
        for x, y in pts: s.dot(x, y, c)

    def save(s, path, scale=3):
        im = Image.fromarray(s.px, 'RGBA'); im.resize((N * scale, N * scale), Image.NEAREST).save(path)

    def img(s): return Image.fromarray(s.px, 'RGBA')


def vec(p0, p1):
    L = math.hypot(p1[0] - p0[0], p1[1] - p0[1]) or 1; return ((p1[0] - p0[0]) / L, (p1[1] - p0[1]) / L)


def add(p, d, k): return (p[0] + d[0] * k, p[1] + d[1] * k)


def sword(c, blade=STEEL, guard=GOLD, grip=LEATH, ln=17, w=5, short=False, base=(7, 25), tipd=(1, -1), gw=11):
    d = vec((0, 0), tipd); n = (-d[1], d[0]); p0 = add(base, d, 5); p1 = add(p0, d, ln)
    c.blade(p0, p1, w, blade, tip=w * .7)
    cen = add(p0, d, 0)
    c.seg(add(cen, n, -gw / 2), add(cen, n, gw / 2), 3, guard)
    c.seg(add(p0, d, -1), add(p0, d, -6), 3, grip)
    c.ell((round(add(p0, d, -7.5)[0] - 2), round(add(p0, d, -7.5)[1] - 2), round(add(p0, d, -7.5)[0] + 2), round(add(p0, d, -7.5)[1] + 2)), guard)
    return p0, p1, d, n


def i_espada(): c = Cv(); sword(c); return c
def i_espada_curta(): c = Cv(); sword(c, ln=11, w=5, base=(8, 24), gw=9); return c
def i_florete():
    c = Cv(); p0, p1, d, n = sword(c, ln=19, w=2.6, gw=8)
    c.arc((p0[0] - 8, p0[1] - 8, p0[0] + 4, p0[1] + 4), 90, 270, 2, GOLD); return c
def i_adaga():
    c = Cv(); d = (.7071, -.7071); n = (-d[1], d[0]); p0 = (13, 19); p1 = add(p0, d, 10)
    c.blade(p0, p1, 6, STEEL, tip=5); c.seg(add(p0, n, -6), add(p0, n, 6), 3, GOLD); c.seg(add(p0, d, -1), add(p0, d, -6), 3, DLEATH); c.ell((3, 25, 7, 29), GOLD); return c


def i_machado():
    c = Cv(); c.seg((7, 26), (23, 9), 3, WOOD)
    c.poly([(16, 3), (22, 4), (27, 9), (28, 17), (23, 13), (19, 15), (17, 11)], STEEL); c.seg((5, 28), (7, 26), 3, LEATH); c.dots([(20, 7), (21, 8)], '#ffffff'); return c


def i_martelo():
    c = Cv(); c.seg((6, 27), (22, 11), 3, WOOD); c.poly([(14, 5), (24, 3), (29, 8), (27, 15), (17, 17), (12, 11)], STEEL); c.seg((16, 6), (26, 14), 1, DSTEEL, outline=False, light=False)
    c.dots([(18, 6), (19, 6)], '#ffffff'); return c


def i_maca():
    c = Cv(); c.seg((7, 27), (21, 13), 3, WOOD)
    for a in range(0, 360, 45):
        x = 22 + 6.2 * math.cos(math.radians(a)); y = 10 + 6.2 * math.sin(math.radians(a)); c.poly([(22 + 4 * math.cos(math.radians(a - 25)), 10 + 4 * math.sin(math.radians(a - 25))), (x, y), (22 + 4 * math.cos(math.radians(a + 25)), 10 + 4 * math.sin(math.radians(a + 25)))], STEEL)
    c.ell((17, 5, 27, 15), STEEL); c.ell((20, 8, 24, 12), DSTEEL, outline=False); c.dot(19, 7, '#ffffff'); return c


def i_cajado():
    c = Cv(); c.seg((6, 28), (21, 13), 3, WOOD); c.seg((14, 20), (18, 16), 3, GOLD, outline=False)
    c.ell((17, 3, 27, 13), CYAN); c.ell((19, 5, 23, 9), R('#082838', '#40b8e8', '#e0ffff', '#ffffff'), outline=False)
    c.arc((15, 1, 29, 15), 200, 340, 2, GOLD); return c


def i_varinha():
    c = Cv(); c.seg((7, 27), (21, 13), 2, WOOD); c.seg((7, 27), (11, 23), 3, DLEATH)
    for (x, y, r) in [(24, 8, 5)]:
        c.poly([(x, y - r), (x + 1.6, y - 1.6), (x + r, y), (x + 1.6, y + 1.6), (x, y + r), (x - 1.6, y + 1.6), (x - r, y), (x - 1.6, y - 1.6)], R('#3a0c34', '#a02890', '#f070e0', '#ffe0ff'))
    c.dots([(27, 4), (28, 12), (20, 5)], '#ffffff'); return c


def i_cetro():
    c = Cv(); c.seg((7, 27), (21, 13), 3, WOOD); c.seg((14, 20), (18, 16), 3, GOLD, outline=False)
    c.poly([(22, 3), (27, 9), (22, 15), (17, 9)], PURP); c.poly([(22, 5), (24, 9), (22, 12), (20, 9)], R('#180c34', '#7a50d0', '#e0d0ff', '#ffffff'), outline=False, light=False)
    c.arc((14, 1, 30, 17), 195, 345, 2, GOLD); return c


def i_cetro_sagrado():
    c = Cv(); c.seg((7, 27), (20, 14), 3, GOLD); c.seg((7, 27), (11, 23), 3, WOOD)
    c.ell((16, 2, 28, 14), GOLD); c.ell((19, 5, 25, 11), R('#4a2808', '#fff0a0', '#ffffff', '#ffffff'), outline=False, light=False)
    for a in range(0, 360, 45):
        x = 22 + 8.2 * math.cos(math.radians(a)); y = 8 + 8.2 * math.sin(math.radians(a))
        if 0 <= x < 32 and 0 <= y < 32: c.dot(int(x), int(y), '#fff2a8')
    return c


def i_arco():
    c = Cv(); c.arc((5, 2, 29, 30), 100, 260, 4, WOOD); c.seg((17, 3), (17, 29), 1, CREAM, outline=False, light=False)
    c.seg((11, 16), (28, 16), 2, WOOD); c.poly([(28, 13), (31, 16), (28, 19)], STEEL); c.poly([(10, 13), (14, 16), (10, 19)], RED, outline=False, light=False); return c


def i_arco_longo():
    c = Cv(); c.arc((9, -2, 29, 34), 95, 265, 4, WOOD); c.seg((19, 2), (19, 30), 1, CREAM, outline=False, light=False)
    c.seg((11, 16), (29, 16), 2, WOOD); c.poly([(28, 13), (31, 16), (28, 19)], STEEL); c.poly([(9, 13), (13, 16), (9, 19)], GREEN, outline=False, light=False); return c


def i_aljava():
    c = Cv(); c.seg((10, 26), (20, 12), 8, LEATH); c.seg((9, 27), (12, 23), 9, DLEATH); c.seg((16, 19), (19, 15), 8, GOLD, outline=False)
    for (x, y) in [(20, 7), (23, 9), (17, 6)]:
        c.seg((x - 4, y + 6), (x, y), 2, WOOD); c.poly([(x, y - 3), (x - 2, y + 1), (x + 2, y + 1)], RED)
    c.seg((10, 26), (20, 12), 8, LEATH); c.seg((9, 27), (12, 23), 9, DLEATH); c.seg((16, 19), (19, 15), 8, GOLD, outline=False); return c


def i_alaude():
    c = Cv(); c.seg((15, 17), (26, 6), 3, WOOD); c.rect((24, 3, 29, 8), WOOD); c.dots([(25, 4), (27, 6)], '#d8ccb8')
    c.ell((3, 13, 19, 29), R('#2a1408', '#8a4a1a', '#d08a3c', '#ffd088')); c.ell((8, 18, 14, 24), R('#10080a', '#10080a', '#2a1408', '#2a1408'), outline=True, light=False)
    c.seg((7, 27), (12, 22), 1, GOLD, outline=False, light=False); return c


def i_flauta():
    c = Cv(); c.seg((5, 26), (26, 5), 4, R('#2a1408', '#8a5a1a', '#d8a050', '#ffe0a0'))
    for t in (.35, .5, .65, .8): c.dot(int(5 + 21 * t), int(26 - 21 * t), '#2a1408')
    c.seg((5, 26), (8, 23), 4, GOLD, outline=False); return c


def book(c, cover, band=GOLD, sym=None):
    c.rrect((6, 4, 25, 28), 2, cover); c.rect((4, 5, 8, 27), R(cover[0], cover[1], cover[1], cover[2]))
    c.rect((20, 4, 25, 28), cover, outline=False, light=False); c.rect((6, 22, 25, 25), band, outline=False)
    c.rect((10, 8, 22, 14), band, outline=False, light=False)


def i_livro(): c = Cv(); book(c, LEATH); c.dots([(14, 10), (15, 10), (16, 10), (15, 11), (15, 12)], '#4a2808'); return c


def i_livro_cancoes():
    c = Cv(); book(c, BLUE, GOLD); c.ell((12, 11, 16, 14), R('#4a2808', '#4a2808', '#4a2808', '#4a2808'), outline=False, light=False); c.seg((16, 12), (16, 7), 1, R('#4a2808', '#4a2808', '#4a2808', '#4a2808'), outline=False, light=False)
    c.dots([(17, 7), (18, 8)], '#4a2808'); return c


def i_orbe():
    c = Cv(); c.poly([(9, 28), (23, 28), (21, 23), (11, 23)], GOLD); c.ell((6, 3, 26, 23), CYAN)
    c.ell((9, 6, 15, 12), R('#082838', '#b8f0ff', '#ffffff', '#ffffff'), outline=False, light=False); c.arc((9, 7, 23, 21), 20, 90, 2, R('#082838', '#1c6a9a', '#1c6a9a', '#1c6a9a'), outline=False, light=False); return c


def i_gema():
    c = Cv(); c.poly([(16, 3), (26, 12), (16, 29), (6, 12)], R('#2a0c14', '#982040', '#e84860', '#ffa0b0'))
    c.poly([(16, 3), (20, 12), (16, 29), (12, 12)], R('#2a0c14', '#e84860', '#ff8898', '#ffe0e8'), outline=False, light=False); c.seg((6, 12), (26, 12), 1, R('#2a0c14', '#982040', '#982040', '#982040'), outline=False, light=False)
    c.dots([(12, 8), (13, 7)], '#ffffff'); return c


def i_coracao():
    c = Cv(); c.poly([(16, 28), (4, 15), (4, 9), (8, 5), (13, 5), (16, 9), (19, 5), (24, 5), (28, 9), (28, 15)], RED); c.dots([(8, 9), (9, 8), (10, 8)], '#ffffff'); return c


def i_garra():
    c = Cv()
    for k, x in enumerate((8, 14, 20, 26)):
        c.poly([(x - 2, 26), (x + 2, 26), (x + 3, 14), (x + 6 - k, 4), (x, 12)], BONE)
    c.rrect((5, 24, 29, 29), 2, DLEATH); return c


def i_anel():
    c = Cv(); c.arc((4, 8, 28, 32), 0, 360, 5, GOLD); c.poly([(16, 2), (22, 8), (16, 14), (10, 8)], R('#2a0c14', '#982040', '#e84860', '#ffa0b0')); c.dots([(14, 6), (15, 5)], '#ffffff'); return c


def i_bracelete():
    c = Cv(); c.arc((3, 3, 29, 29), 0, 360, 6, STEEL); c.arc((3, 3, 29, 29), 0, 360, 1, GOLD, outline=False, light=False)
    c.ell((13, 3, 19, 9), GOLD); return c


def i_bracadeira():
    c = Cv(); c.seg((7, 25), (23, 9), 12, LEATH); c.seg((10, 28), (12, 26), 12, DLEATH, outline=False, light=False)
    c.seg((11, 17), (15, 21), 3, GOLD, outline=False, light=False); c.seg((17, 11), (21, 15), 3, GOLD, outline=False, light=False); c.dots([(14, 16), (18, 12)], '#fff2a8'); return c


def i_colar():
    c = Cv(); c.arc((3, -6, 29, 24), 20, 160, 2, GOLD)
    for (x, y) in [(6, 13), (9, 17), (13, 20), (19, 20), (23, 17), (26, 13)]: c.ell((x - 2, y - 2, x + 2, y + 2), ORANGE)
    c.ell((13, 21, 19, 29), R('#2a0c14', '#982040', '#e84860', '#ffa0b0')); return c


def i_pingente():
    c = Cv(); c.arc((5, -8, 27, 18), 25, 155, 1, GOLD, outline=False, light=False); c.poly([(16, 14), (23, 20), (16, 29), (9, 20)], CYAN); c.dots([(14, 18), (15, 17)], '#ffffff'); return c


def i_talisma():
    c = Cv(); c.rrect((7, 5, 25, 29), 4, BLACK); c.ell((10, 13, 22, 21), CREAM); c.ell((14, 14, 18, 20), R('#08080e', '#08080e', '#8a1c2c', '#c43040'), outline=True, light=False)
    c.ell((13, 2, 19, 8), GOLD, outline=True); return c


def i_capuz():
    c = Cv(); c.poly([(16, 3), (25, 10), (26, 27), (16, 22), (6, 27), (7, 10)], LEATH); c.poly([(16, 10), (21, 14), (21, 22), (16, 19), (11, 22), (11, 14)], R('#10080a', '#10080a', '#1e1008', '#1e1008'), outline=True, light=False); return c


def i_elmo():
    c = Cv(); c.poly([(5, 28), (5, 14), (9, 6), (16, 3), (23, 6), (27, 14), (27, 28), (22, 28), (22, 22), (10, 22), (10, 28)], STEEL)
    c.rect((10, 14, 22, 16), BLACK, outline=False, light=False); c.rect((15, 14, 17, 22), BLACK, outline=False, light=False); c.seg((16, 3), (16, 11), 2, RED); return c


def i_cornos():
    c = Cv(); c.poly([(9, 28), (7, 16), (10, 9), (16, 7), (22, 9), (25, 16), (23, 28), (19, 28), (19, 22), (13, 22), (13, 28)], STEEL)
    c.poly([(8, 14), (3, 12), (2, 5), (6, 8), (9, 11)], BONE); c.poly([(24, 14), (29, 12), (30, 5), (26, 8), (23, 11)], BONE); c.rect((9, 15, 23, 17), GOLD, outline=False, light=False); return c


def i_coroa():
    c = Cv(); c.poly([(4, 24), (3, 8), (10, 15), (16, 5), (22, 15), (29, 8), (28, 24)], GOLD); c.rect((4, 21, 28, 25), GOLD)
    for (x, y, rr) in [(10, 22, RED), (16, 22, BLUE), (22, 22, GREEN)]: c.dot(x, y, rr[2])
    c.dots([(3, 7), (16, 4), (29, 7)], '#ffffff'); return c


def i_chapeu():
    c = Cv(); c.poly([(16, 2), (22, 20), (10, 20)], PURP); c.ell((2, 17, 30, 27), PURP); c.rect((10, 17, 22, 20), GOLD, outline=False, light=False)
    c.poly([(16, 6), (17, 9), (20, 9), (17.5, 11), (18.5, 14), (16, 12), (13.5, 14), (14.5, 11), (12, 9), (15, 9)], GOLD, outline=False, light=False); return c


def i_boina():
    c = Cv(); c.ell((4, 10, 28, 26), RED); c.rect((7, 21, 25, 26), R('#2a0c14', '#5a1020', '#7a1c2c', '#9a2c3c'), outline=False, light=False)
    c.seg((24, 8), (30, 2), 2, GOLD); c.poly([(24, 3), (30, 1), (28, 8)], R('#4a2808', '#f0b82c', '#fff2a8', '#ffffff')); return c


def i_mascara():
    c = Cv(); c.poly([(5, 8), (16, 5), (27, 8), (26, 19), (21, 28), (11, 28), (6, 19)], R('#1c1c24', '#8a8a9c', '#d4d4e4', '#ffffff'))
    c.poly([(8, 12), (14, 14), (13, 17), (8, 16)], BLACK); c.poly([(24, 12), (18, 14), (19, 17), (24, 16)], BLACK); c.rect((15, 21, 17, 24), BLACK, outline=False, light=False); return c


def mail_tex(c, m, col):
    ys, xs = np.nonzero(m)
    for y, x in zip(ys, xs):
        if (x + y) % 2 == 0 and tuple(c.px[y, x][:3]) == tuple(col[2]): c.px[y, x] = (*col[1], 255)


def torso(c, ramp, sleeve=True):
    m = c.poly([(11, 4), (16, 7), (21, 4), (28, 9), (26, 17), (23, 15), (23, 28), (9, 28), (9, 15), (6, 17), (4, 9)], ramp); return m


def i_cota():
    c = Cv(); m = torso(c, STEEL); mail_tex(c, m, STEEL); c.rect((9, 24, 23, 28), DSTEEL, outline=False, light=False); c.poly([(13, 4), (16, 8), (19, 4)], BLACK, outline=False, light=False); return c


def i_couraca():
    c = Cv(); c.poly([(5, 8), (12, 4), (16, 7), (20, 4), (27, 8), (25, 17), (22, 29), (10, 29), (7, 17)], STEEL)
    c.seg((16, 8), (16, 28), 2, DSTEEL, outline=False, light=False); c.seg((9, 17), (23, 17), 1, DSTEEL, outline=False, light=False); c.ell((6, 4, 12, 10), STEEL); c.ell((20, 4, 26, 10), STEEL)
    c.dots([(11, 11), (12, 10)], '#ffffff'); return c


def i_colete():
    c = Cv(); c.poly([(9, 4), (16, 9), (23, 4), (26, 10), (24, 29), (17, 29), (16, 12), (15, 29), (8, 29), (6, 10)], LEATH)
    c.seg((12, 14), (20, 14), 1, GOLD, outline=False, light=False); c.seg((12, 19), (20, 19), 1, GOLD, outline=False, light=False); c.seg((12, 24), (20, 24), 1, GOLD, outline=False, light=False); return c


def i_tunica():
    c = Cv(); c.poly([(11, 4), (16, 7), (21, 4), (29, 12), (26, 18), (23, 15), (24, 29), (8, 29), (9, 15), (6, 18), (3, 12)], CREAM); c.rect((8, 21, 24, 23), LEATH, outline=False, light=False)
    c.poly([(13, 4), (16, 9), (19, 4)], R('#2a2030', '#8a7a78', '#8a7a78', '#8a7a78'), outline=False, light=False); return c


def i_manto():
    c = Cv(); c.poly([(10, 3), (22, 3), (28, 28), (22, 24), (16, 29), (10, 24), (4, 28)], GREEN); c.poly([(10, 3), (22, 3), (20, 8), (12, 8)], GOLD); c.ell((14, 5, 18, 9), RED); c.seg((16, 10), (16, 26), 1, R('#0c2410', '#1c5a2c', '#1c5a2c', '#1c5a2c'), outline=False, light=False); return c


def i_botas():
    c = Cv()
    for ox in (0, 12):
        c.poly([(5 + ox, 6), (13 + ox, 6), (13 + ox, 20), (17 + ox, 23), (17 + ox, 28), (4 + ox, 28), (4 + ox, 6)], LEATH); c.rect((4 + ox, 6, 13 + ox, 9), DLEATH, outline=False, light=False); c.rect((4 + ox, 25, 17 + ox, 28), BLACK, outline=False, light=False)
    return c


def i_grevas():
    c = Cv()
    for ox in (0, 12):
        c.poly([(5 + ox, 5), (14 + ox, 5), (14 + ox, 19), (18 + ox, 22), (18 + ox, 28), (4 + ox, 28), (4 + ox, 5)], STEEL); c.rect((4 + ox, 11, 14 + ox, 13), DSTEEL, outline=False, light=False); c.ell((5 + ox, 12, 12 + ox, 17), STEEL)
    return c


def i_sandalias():
    c = Cv()
    for ox, oy in ((0, 0), (11, 3)):
        c.poly([(5 + ox, 6 + oy), (14 + ox, 6 + oy), (15 + ox, 24 + oy), (9 + ox, 27 + oy), (5 + ox, 23 + oy)], LEATH)
        c.seg((5 + ox, 11 + oy), (15 + ox, 13 + oy), 2, DLEATH, outline=False, light=False); c.seg((5 + ox, 17 + oy), (15 + ox, 19 + oy), 2, DLEATH, outline=False, light=False)
    return c


def hand(c, ox, ramp, cuff):
    for k, fx in enumerate((4, 7, 10, 13)):
        top = 5 + (0 if k in (1, 2) else 2) + (1 if k == 2 else 0)
        c.rrect((fx + ox, top, fx + 2 + ox, 17), 1, ramp)
    c.rrect((3 + ox, 14, 15 + ox, 25), 3, ramp); c.rrect((12 + ox, 13, 17 + ox, 20), 2, ramp); c.rect((3 + ox, 23, 15 + ox, 28), cuff)


def i_luvas():
    c = Cv(); hand(c, 1, LEATH, DLEATH); hand(c, 13, LEATH, DLEATH); return c


def i_manoplas():
    c = Cv(); hand(c, 1, STEEL, DSTEEL); hand(c, 13, STEEL, DSTEEL); return c


def i_escudo():
    c = Cv(); c.ell((3, 3, 29, 29), WOOD); c.arc((3, 3, 29, 29), 0, 360, 3, STEEL); c.ell((11, 11, 21, 21), STEEL); c.ell((14, 14, 18, 18), GOLD, outline=False, light=False)
    for a in range(0, 360, 90): c.seg((16, 16), (16 + 9 * math.cos(math.radians(a + 45)), 16 + 9 * math.sin(math.radians(a + 45))), 1, DLEATH, outline=False, light=False)
    return c


def i_escudog():
    c = Cv(); c.poly([(4, 5), (28, 5), (28, 17), (16, 30), (4, 17)], STEEL); c.seg((16, 7), (16, 27), 2, DSTEEL, outline=False, light=False); c.seg((6, 14), (26, 14), 2, DSTEEL, outline=False, light=False)
    c.ell((12, 10, 20, 18), GOLD); c.dots([(7, 8), (8, 7)], '#ffffff'); return c


def i_escudo_sagrado():
    c = Cv(); c.poly([(4, 4), (28, 4), (28, 17), (16, 30), (4, 17)], GOLD); c.poly([(7, 7), (25, 7), (25, 16), (16, 26), (7, 16)], CREAM)
    c.rect((14, 8, 18, 22), GOLD, outline=False, light=False); c.rect((9, 12, 23, 15), GOLD, outline=False, light=False); return c



# ============================ ÍCONES DE INTERFACE (mesmo nome dos antigos em assets/ui-icons) ============================
def u_coins():
    c = Cv()
    for (x, y) in [(4, 20), (15, 21), (10, 12), (19, 11)]:
        c.ell((x, y, x + 12, y + 8), GOLD); c.ell((x + 2, y + 1, x + 10, y + 6), R('#4a2808', '#f0b82c', '#fff2a8', '#fff2a8'), outline=False, light=False)
    c.dots([(11, 14), (12, 14), (26, 13), (22, 23)], '#ffffff'); return c


def u_gems():
    c = Cv(); c.poly([(9, 5), (16, 11), (9, 27), (2, 11)], CYAN); c.poly([(9, 5), (12, 11), (9, 27), (6, 11)], R('#082838', '#40b8e8', '#b8f0ff', '#ffffff'), outline=False, light=False)
    c.poly([(23, 8), (30, 14), (23, 28), (16, 14)], PINK); c.poly([(23, 8), (26, 14), (23, 28), (20, 14)], R('#2a0c20', '#e0509a', '#ffa8d4', '#ffffff'), outline=False, light=False); return c


def u_padlock():
    c = Cv(); c.arc((8, 2, 24, 20), 180, 360, 4, STEEL); c.rrect((5, 13, 27, 29), 3, GOLD); c.ell((14, 17, 18, 21), BLACK, outline=False, light=False); c.rect((15, 20, 17, 25), BLACK, outline=False, light=False); return c


def u_helmet():
    c = i_elmo(); return c


def u_scroll_unfurled():
    c = Cv(); c.rect((8, 6, 25, 26), R('#2a1c08', '#c0a060', '#f0dca0', '#fff8d8')); c.ell((4, 3, 12, 9), R('#2a1c08', '#c0a060', '#f0dca0', '#fff8d8')); c.ell((21, 23, 29, 29), R('#2a1c08', '#c0a060', '#f0dca0', '#fff8d8'))
    for y in (11, 15, 19): c.seg((11, y), (22, y), 1, R('#4a2808', '#7a4a20', '#7a4a20', '#7a4a20'), outline=False, light=False)
    return c


def u_health_potion():
    c = Cv(); c.ell((5, 11, 27, 31), R('#2a0c14', '#982040', '#e84860', '#ffa0b0')); c.rect((12, 3, 20, 14), R('#2a2030', '#8a98b0', '#c8d8f0', '#ffffff')); c.rect((11, 2, 21, 5), WOOD)
    c.ell((9, 17, 14, 22), R('#2a0c14', '#ffa0b0', '#ffe0e8', '#ffffff'), outline=False, light=False); return c


def u_anvil():
    c = Cv(); c.poly([(2, 8), (30, 8), (26, 14), (20, 15), (22, 21), (26, 26), (6, 26), (10, 21), (12, 15), (6, 14)], DSTEEL); c.rect((6, 26, 26, 29), BLACK); c.seg((4, 9), (28, 9), 1, STEEL, outline=False, light=False); return c


def u_greek_temple():
    c = Cv(); c.poly([(2, 12), (16, 3), (30, 12)], CREAM); c.rect((4, 12, 28, 14), CREAM)
    for x in (6, 12, 18, 24): c.rect((x, 15, x + 3, 25), CREAM)
    c.rect((3, 25, 29, 29), CREAM); return c


def u_team_idea():
    c = Cv(); c.ell((3, 5, 15, 17), R('#2a1c10', '#a46a30', '#e0a868', '#ffe0b0')); c.poly([(1, 29), (2, 19), (8, 17), (14, 19), (15, 29)], BLUE)
    c.ell((17, 3, 29, 15), R('#2a1c10', '#a46a30', '#f0c088', '#ffe8c8')); c.poly([(15, 29), (16, 17), (23, 15), (30, 17), (31, 29)], RED); return c


def u_magic_swirl():
    c = Cv(); c.arc((3, 3, 29, 29), 30, 330, 4, PURP); c.arc((9, 9, 23, 23), 100, 400, 3, R('#180c34', '#7a50d0', '#c0a0ff', '#ffffff')); c.dots([(16, 16), (17, 16)], '#ffffff'); return c


def u_check_mark():
    c = Cv(); c.poly([(3, 17), (8, 12), (13, 18), (25, 5), (30, 10), (13, 28)], GREEN); return c


def u_crossed_swords():
    c = Cv(); c.blade((6, 26), (25, 7), 4, STEEL, tip=3); c.blade((26, 26), (7, 7), 4, STEEL, tip=3)
    c.seg((4, 21), (11, 28), 3, GOLD); c.seg((28, 21), (21, 28), 3, GOLD); return c


def u_treasure_map():
    c = Cv(); c.poly([(3, 7), (11, 5), (21, 8), (29, 5), (29, 25), (21, 28), (11, 25), (3, 27)], R('#2a1c08', '#c0a060', '#f0dca0', '#fff8d8'))
    c.seg((9, 21), (14, 13), 1, RED, outline=False, light=False); c.seg((14, 13), (23, 19), 1, RED, outline=False, light=False); c.seg((21, 11), (25, 15), 2, RED, outline=False, light=False); c.seg((25, 11), (21, 15), 2, RED, outline=False, light=False); return c


def u_clover():
    c = Cv()
    for (x, y) in [(16, 8), (8, 15), (24, 15), (16, 21)]: c.ell((x - 6, y - 6, x + 6, y + 6), GREEN)
    c.seg((16, 22), (21, 30), 2, R('#0c2410', '#1c5a2c', '#3c9a48', '#88d878')); return c


def u_fist():
    c = Cv(); c.rrect((5, 8, 26, 25), 5, R('#2a1408', '#a46a30', '#e0a868', '#ffe0b0'))
    for x in (8, 13, 18, 23): c.seg((x, 10), (x, 16), 1, R('#2a1408', '#a46a30', '#a46a30', '#a46a30'), outline=False, light=False)
    c.rect((6, 24, 25, 29), R('#2a0c14', '#7a1c2c', '#c43040', '#f07080')); return c


def u_heart_plus():
    c = i_coracao(); c.rect((13, 10, 19, 22), CREAM) if False else None
    c.rect((14, 10, 18, 22), R('#2a2030', '#c8c0d0', '#ffffff', '#ffffff'), outline=False, light=False); c.rect((9, 14, 23, 18), R('#2a2030', '#c8c0d0', '#ffffff', '#ffffff'), outline=False, light=False); return c


def u_shop():
    c = Cv(); c.rect((4, 14, 28, 29), WOOD); c.poly([(2, 5), (30, 5), (28, 14), (4, 14)], RED)
    for x in (8, 16, 24): c.rect((x, 5, x + 4, 14), CREAM, outline=False, light=False)
    c.rect((10, 19, 22, 29), DLEATH); return c


def u_imperial_crown(): return i_coroa()


UI = {n[2:].replace('_', '-'): f for n, f in list(globals().items()) if n.startswith('u_') and callable(f)}


def make_ui(only=None):
    for k, f in UI.items():
        if only and k not in only: continue
        f().save(os.path.join(UIDIR, k + '.png'), scale=1)


def tile(c, frame, bg=((30, 24, 40), (14, 10, 22))):
    """moldura de botão do HUD (mesma família de hud/heroi.png): 32 nativos x2 = 64px"""
    T = Cv(); px = T.px; f = hx(frame)
    for y in range(N):
        t = y / (N - 1); col = tuple(int(bg[0][i] * (1 - t) + bg[1][i] * t) for i in range(3)); px[y, :] = (*col, 255)
    px[0:2, :] = (*f, 255); px[-2:, :] = (*f, 255); px[:, 0:2] = (*f, 255); px[:, -2:] = (*f, 255)
    px[2, 2:-2] = (*(min(255, v + 40) for v in f), 255)
    ic = c.img().resize((24, 24), Image.LANCZOS); a = np.array(ic); a[..., 3] = np.where(a[..., 3] > 110, 255, 0)
    Tm = T.img(); Tm.alpha_composite(Image.fromarray(a, 'RGBA'), (4, 4)); return Tm


def make_tiles():
    hud = os.path.join(ROOT, 'mmo', 'assets', 'hud')
    tile(u_scroll_unfurled(), '#a07828').resize((64, 64), Image.NEAREST).save(os.path.join(hud, 'diario.png'))
    tile(u_team_idea(), '#3a78d8').resize((64, 64), Image.NEAREST).save(os.path.join(hud, 'social.png'))

ITEMS = {n[2:]: f for n, f in list(globals().items()) if n.startswith('i_') and callable(f)}


def make_items(only=None):
    os.makedirs(ICO, exist_ok=True)
    for k, f in ITEMS.items():
        if only and k not in only: continue
        f().save(os.path.join(ICO, f'i_{k}.png'))


def usheet(path):
    ks = list(UI); cols = 8
    S = Image.new('RGBA', (cols * 70, ((len(ks) + cols - 1) // cols) * 70), (38, 38, 52, 255))
    for i, k in enumerate(ks): S.alpha_composite(UI[k]().img().resize((64, 64), Image.NEAREST), ((i % cols) * 70 + 3, (i // cols) * 70 + 3))
    S.save(path)


def sheet(path, names=None):
    ks = [k for k in ITEMS if not names or k in names]; cols = 8
    S = Image.new('RGBA', (cols * 100, ((len(ks) + cols - 1) // cols) * 100), (38, 38, 52, 255))
    for i, k in enumerate(ks): S.alpha_composite(ITEMS[k]().img().resize((96, 96), Image.NEAREST), ((i % cols) * 100 + 2, (i // cols) * 100 + 2))
    S.save(path); return ks


if __name__ == '__main__':
    if sys.argv[1:2] == ['sheet']: print(sheet(sys.argv[2]))
    elif sys.argv[1:2] == ['ui']: make_ui(); make_tiles()
    else: make_items(sys.argv[1:] or None)
