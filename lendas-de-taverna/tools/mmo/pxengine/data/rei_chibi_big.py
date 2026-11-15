#!/usr/bin/env python3
"""Rei Esquecido no estilo chibi pixel art (maior que o heroi, ~1.4x). Sprite desenhado por codigo (grade + formas sombreadas),
poses por parametros (bracos, mandibula, flutuar). Habilidades: Esquecimento, Eco, Fenda do Vazio, Coroa de Almas, Trevas."""
import math
from PIL import Image
from pxrig import Grid, autoline, line_pts

BW, BH = 96, 92
PAL = dict(K='#120a1e',
           S='#c8c0d4', s='#eee8f6', B='#7a6c98',                    # osso (luz quente / sombra fria)
           e='#1a1030', E='#9af0ff', F='#ffffff', X='#4a9ad8',        # orbita e brilho dos olhos
           c='#ffe8a0', C='#d8a840', D='#8a5a20', g='#b060f0', G='#e8b8ff',   # coroa e gemas
           R='#4a2c7a', r='#6a44a0', M='#261444', m='#38205c',        # manto
           T='#c89838', t='#e8c860', W='#e8f8ff', w='#8ad0f0')        # debrum dourado, almas
SEL = {'S': '#4a3e68', 's': '#4a3e68', 'B': '#2a2048', 'c': '#6a4410', 'C': '#5a3410', 'D': '#3a2008', 'g': '#4a1a80', 'G': '#4a1a80',
       'R': '#1a0c30', 'r': '#1a0c30', 'M': '#0c0618', 'm': '#0c0618', 'T': '#5a3a10', 't': '#5a3a10', 'e': '#0c0618', 'W': '#2a5a90', 'w': '#2a5a90'}


def ell(g, cx, cy, rx, ry, fn):
    for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
        for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
            u, v = (x + .5 - cx) / rx, (y + .5 - cy) / ry
            if u * u + v * v <= 1: g.put(x, y, fn(u, v))


def shade(lo, mid, hi, th=.38):
    return lambda u, v: hi if (u + v) * .7 < -th else (lo if (u + v) * .7 > th else mid)


def tube(g, p0, p1, w, fn):
    pts = line_pts(round(p0[0]), round(p0[1]), round(p1[0]), round(p1[1]))
    for (x, y) in pts:
        for dy in range(-(w // 2), w - w // 2):
            for dx in range(-(w // 2), w - w // 2):
                g.put(x + dx, y + dy, fn(dx, dy))


def boss(p=None):
    """p: dy (flutuar), jaw (0-3), arms=((lx,ly),(rx,ry)) maos relativas ao ombro, glow (0..2), crown (dy da coroa)."""
    p = p or {}
    dy = p.get('dy', 0); jaw = p.get('jaw', 0); glow = p.get('glow', 1); cdy = p.get('crown', 0)
    arms = p.get('arms', ((-15, 13), (15, 13)))
    g = Grid(BW, BH)
    cx = BW // 2; top = 8 + dy
    # capuz/manto de tras (silhueta escura)
    ell(g, cx, top + 30, 20, 18, lambda u, v: 'M' if v > -.2 else 'm')
    # manto: trapezio com dobras e barra rasgada
    y0 = top + 38; y1 = top + 70
    for y in range(y0, y1 + 1):
        t = (y - y0) / (y1 - y0)
        hw = 11 + t * 15
        rag = int(math.sin(y * .0 + 0) * 0)
        for x in range(int(cx - hw), int(cx + hw) + 1):
            u = (x - cx) / hw
            fold = (int((x - cx) / 4) % 2 == 0)
            ch = 'M' if abs(u) > .78 else ('R' if (u + t * .0) < .15 else 'r')
            if abs(u) < .78 and fold and t > .15: ch = 'R' if ch == 'r' else 'M'
            g.put(x, y, ch)
    # barra rasgada (pontas) e almas subindo
    for x in range(int(cx - 26), int(cx + 27)):
        tooth = int(3 + 3 * math.sin(x * 1.3 + p.get('t', 0) * .0))
        for yy in range(y1 + 1, y1 + 1 + (abs((x - cx) % 6 - 3) + 1)):
            if abs(x - cx) < 25 - (yy - y1): g.put(x, yy, 'M')
    # debrum dourado central e gola
    for y in range(y0 + 2, y1 - 1):
        g.put(cx - 1, y, 'T'); g.put(cx, y, 't')
    for x in range(cx - 10, cx + 11): g.put(x, y0 - 1, 'T' if x % 2 else 't')
    # ombreiras
    for sgn in (-1, 1):
        ell(g, cx + sgn * 14, y0 + 1, 7, 5, shade('M', 'R', 'r'))
        for k in range(3): g.put(cx + sgn * (14 + k * 2 - 2), y0 - 5 + (1 if k == 1 else 0), 'T')
    # bracos (mangas largas) + maos de osso
    for sgn, (hx, hy) in zip((-1, 1), arms):
        sx, sy = cx + sgn * 14, y0 + 2
        ex, ey = int(round(sx + hx)), int(round(sy + hy))
        tube(g, (sx, sy), (ex, ey), 9, lambda a, b: 'R' if a + b < 1 else 'M')
        tube(g, (sx, sy), (ex, ey), 5, lambda a, b: 'r')
        for q in range(-4, 5): g.put(ex + q, ey - 4, 'T') if abs(hx) < 40 and False else None
        for dxh in (-3, -2, -1, 0, 1, 2, 3):                 # mao: palma + dedos
            for dyh in (-3, -2, -1, 0, 1):
                g.put(ex + dxh, ey + dyh, 'S' if dyh > -1 else 's')
        for k in (-3, -1, 1, 3): g.put(ex + k, ey + 2, 'S'); g.put(ex + k, ey + 3, 'B')
    # cranio
    hy = top + 28
    ell(g, cx, hy, 14, 12, shade('B', 'S', 's'))
    # mandibula (abre ao conjurar)
    for y in range(hy + 7 + jaw, hy + 13 + jaw):
        hw = 8 - (y - (hy + 7 + jaw)) * .7
        for x in range(int(cx - hw), int(cx + hw) + 1):
            g.put(x, y, 'B' if x > cx + 3 else 'S')
    for x in range(cx - 6, cx + 7):                         # dentes
        for y in range(hy + 9 + jaw, hy + 12 + jaw):
            g.put(x, y, 'e' if (x - cx) % 3 == 0 else 's')
    if jaw:
        for x in range(cx - 6, cx + 7): g.put(x, hy + 8, 'e'); g.put(x, hy + 9, 'e') if jaw > 1 else None
    # orbitas + brilho
    for sgn in (-1, 1):
        ex = cx + sgn * 6
        for y in range(hy - 3, hy + 4):
            for x in range(ex - 3, ex + 3):
                if (x - ex + .5) ** 2 / 9 + (y - hy - .5) ** 2 / 12 <= 1: g.put(x, y, 'e')
        for (a, b, c_) in ((0, 0, 'E'), (-1, 0, 'X'), (0, 1, 'E'), (-1, 1, 'X')):
            g.put(ex + a, hy + b, c_)
        g.put(ex - 1 if sgn < 0 else ex, hy, 'F')
        if glow > 1:
            g.put(ex + sgn * 3 + (0), hy - 1, 'X'); g.put(ex + sgn * 3, hy, 'E')
    g.put(cx - 1, hy + 4, 'e'); g.put(cx, hy + 4, 'e'); g.put(cx - 1, hy + 5, 'e'); g.put(cx, hy + 5, 'e')   # nariz
    for k, (rx_, ry_) in enumerate(((-9, -5), (9, -6))):                                                  # rachaduras
        g.put(cx + rx_, hy + ry_, 'B'); g.put(cx + rx_ + (1 if rx_ < 0 else -1), hy + ry_ + 1, 'B')
    # coroa: aro + 5 pontas + gemas
    cy0 = hy - 10 + cdy
    for x in range(cx - 13, cx + 14):
        for yy in range(cy0, cy0 + 4):
            g.put(x, yy, 'c' if yy == cy0 else ('C' if yy < cy0 + 3 else 'D'))
    heights = {-12: 5, -8: 8, -4: 6, 0: 11, 4: 6, 8: 8, 12: 5}
    for off, h in heights.items():
        for k in range(h):
            wdt = 1 if k > h - 3 else 2
            for q in range(wdt + (1 if k < h - 3 else 0)):
                g.put(cx + off + q - (1 if wdt > 1 else 0), cy0 - 1 - k, 'c' if q == 0 else 'C')
        g.put(cx + off, cy0 - h - 1, 'G')
    for off in (-8, 0, 8): g.put(cx + off, cy0 + 1, 'g'); g.put(cx + off + 1, cy0 + 1, 'G')
    autoline(g)
    return g.render(PAL, SEL)


def souls(img_w=BW, n=3):
    """posicoes das almas que orbitam a coroa (relativas ao sprite)"""
    return [(BW // 2, 10)]


POSE = dict(
    idle=lambda f: dict(dy=int(round(math.sin(f * math.pi / 3) * 2)), arms=((-15 + int(math.sin(f * math.pi / 3 + 1)), 13 + int(math.sin(f * math.pi / 3 + 2))), (15, 13 + int(math.sin(f * math.pi / 3)))), crown=int(round(math.sin(f * math.pi / 3 + 2)))),
    raise_=lambda k: dict(dy=-int(3 * k), arms=((-14 - 4 * k, 12 - 30 * k), (14 + 4 * k, 12 - 30 * k)), jaw=1 if k > .6 else 0, glow=2 if k > .5 else 1, crown=-int(2 * k)),
    cast=lambda k: dict(dy=-2, arms=((-16, -22), (16, -22)), jaw=2, glow=2, crown=-1),
    point=lambda k: dict(dy=-1, arms=((-12, 10), (24, -4)), jaw=1, glow=2),
    slam=lambda k: dict(dy=3, arms=((-18, 20), (18, 20)), jaw=2, glow=2),
    hurt=lambda k: dict(dy=2, arms=((-10, 8), (10, 8)), jaw=3, glow=0, crown=2),
)

if __name__ == '__main__':
    from PIL import Image
    import os
    from teste_clareira import OUT
    A = Image.new('RGBA', (BW * 5, BH), (40, 36, 56, 255))
    for i, p in enumerate([POSE['idle'](0), POSE['raise_'](1), POSE['cast'](1), POSE['point'](1), POSE['hurt'](1)]):
        A.alpha_composite(boss(p), (i * BW, 0))
    A.resize((A.width * 3, A.height * 3), Image.NEAREST).convert('RGB').save(os.path.join(OUT, 'rei_chibi_poses.png'))
