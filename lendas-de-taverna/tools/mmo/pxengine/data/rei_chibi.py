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
    """p: dy (flutuar), jaw (0-3), arms=((lx,ly),(rx,ry)) maos relativas ao ombro, glow (0..2), crown (dy da coroa).
    Tamanho ~1.45x o heroi (decisao do dono: maior, mas ainda chibi pequenininho)."""
    p = p or {}
    dy = p.get('dy', 0); jaw = p.get('jaw', 0); glow = p.get('glow', 1); cdy = p.get('crown', 0)
    arms = p.get('arms', ((-10, 9), (10, 9)))
    g = Grid(BW, BH)
    cx = BW // 2; top = 22 + dy
    ell(g, cx, top + 19, 13, 12, lambda u, v: 'M' if v > -.2 else 'm')          # capuz de tras
    y0 = top + 25; y1 = top + 46
    for y in range(y0, y1 + 1):
        t = (y - y0) / (y1 - y0); hw = 8 + t * 10
        for x in range(int(cx - hw), int(cx + hw) + 1):
            u = (x - cx) / hw
            fold = (int((x - cx) / 3) % 2 == 0)
            ch = 'M' if abs(u) > .78 else ('R' if u < .15 else 'r')
            if abs(u) < .78 and fold and t > .2: ch = 'R' if ch == 'r' else 'M'
            g.put(x, y, ch)
    for x in range(cx - 18, cx + 19):                                              # barra rasgada
        for yy in range(y1 + 1, y1 + 1 + (abs((x - cx) % 5 - 2) + 1)):
            if abs(x - cx) < 18 - (yy - y1) // 2: g.put(x, yy, 'M')
    for y in range(y0 + 1, y1 - 1):
        g.put(cx - 1, y, 'T'); g.put(cx, y, 't')
    for x in range(cx - 7, cx + 8): g.put(x, y0 - 1, 'T' if x % 2 else 't')
    for sgn in (-1, 1):
        ell(g, cx + sgn * 10, y0 + 1, 5, 4, shade('M', 'R', 'r'))
        g.put(cx + sgn * 10, y0 - 3, 'T'); g.put(cx + sgn * 12, y0 - 2, 'T')
    for sgn, (hx, hy) in zip((-1, 1), arms):
        sx, sy = cx + sgn * 10, y0 + 2
        ex, ey = int(round(sx + hx)), int(round(sy + hy))
        tube(g, (sx, sy), (ex, ey), 6, lambda a, b: 'R' if a + b < 1 else 'M')
        tube(g, (sx, sy), (ex, ey), 3, lambda a, b: 'r')
        for dxh in (-2, -1, 0, 1, 2):
            for dyh in (-2, -1, 0, 1):
                g.put(ex + dxh, ey + dyh, 'S' if dyh > -1 else 's')
        for k in (-2, 0, 2): g.put(ex + k, ey + 2, 'S'); g.put(ex + k, ey + 3, 'B')
    hy = top + 17
    ell(g, cx, hy, 10, 8.5, shade('B', 'S', 's'))
    for y in range(hy + 5 + jaw, hy + 9 + jaw):                                      # mandibula
        hw = 6 - (y - (hy + 5 + jaw)) * .8
        for x in range(int(cx - hw), int(cx + hw) + 1): g.put(x, y, 'B' if x > cx + 2 else 'S')
    for x in range(cx - 4, cx + 5):
        for y in range(hy + 6 + jaw, hy + 8 + jaw): g.put(x, y, 'e' if (x - cx) % 2 == 0 else 's')
    if jaw > 1:
        for x in range(cx - 4, cx + 5): g.put(x, hy + 5, 'e')
    for sgn in (-1, 1):
        ex = cx + sgn * 4
        for y in range(hy - 3, hy + 3):
            for x in range(ex - 2, ex + 2): g.put(x, y, 'e')
        g.put(ex - 1, hy - 1, 'E'); g.put(ex, hy - 1, 'E'); g.put(ex - 1, hy, 'X'); g.put(ex, hy, 'X')
        g.put(ex - 1 if sgn < 0 else ex, hy - 1, 'F')
        if glow > 1: g.put(ex + sgn * 2, hy - 2, 'X')
    g.put(cx - 1, hy + 3, 'e'); g.put(cx, hy + 3, 'e')
    g.put(cx - 7, hy - 3, 'B'); g.put(cx - 6, hy - 2, 'B'); g.put(cx + 6, hy - 4, 'B')
    cy0 = hy - 8 + cdy
    for x in range(cx - 9, cx + 10):
        for yy in range(cy0, cy0 + 3): g.put(x, yy, 'c' if yy == cy0 else ('C' if yy < cy0 + 2 else 'D'))
    for off, h in {-8: 3, -4: 5, 0: 8, 4: 5, 8: 3}.items():
        for k in range(h):
            for q in range(2 if k < h - 2 else 1): g.put(cx + off + q - (1 if k < h - 2 else 0), cy0 - 1 - k, 'c' if q == 0 else 'C')
        g.put(cx + off, cy0 - h - 1, 'G')
    for off in (-5, 0, 5): g.put(cx + off, cy0 + 1, 'g'); g.put(cx + off + 1, cy0 + 1, 'G')
    autoline(g)
    return g.render(PAL, SEL)


def souls(img_w=BW, n=3):
    """posicoes das almas que orbitam a coroa (relativas ao sprite)"""
    return [(BW // 2, 10)]


POSE = dict(
    idle=lambda f: dict(dy=int(round(math.sin(f * math.pi / 3) * 2)), arms=((-10 + int(math.sin(f * math.pi / 3 + 1)), 9 + int(math.sin(f * math.pi / 3 + 2))), (10, 9 + int(math.sin(f * math.pi / 3)))), crown=int(round(math.sin(f * math.pi / 3 + 2)))),
    raise_=lambda k: dict(dy=-int(2 * k), arms=((-9 - 3 * k, 8 - 20 * k), (9 + 3 * k, 8 - 20 * k)), jaw=1 if k > .6 else 0, glow=2 if k > .5 else 1, crown=-int(2 * k)),
    cast=lambda k: dict(dy=-2, arms=((-11, -15), (11, -15)), jaw=2, glow=2, crown=-1),
    point=lambda k: dict(dy=-1, arms=((-8, 7), (16, -3)), jaw=1, glow=2),
    slam=lambda k: dict(dy=3, arms=((-12, 13), (12, 13)), jaw=2, glow=2),
    hurt=lambda k: dict(dy=2, arms=((-7, 6), (7, 6)), jaw=3, glow=0, crown=2),
)

if __name__ == '__main__':
    from PIL import Image
    import os
    from teste_clareira import OUT
    A = Image.new('RGBA', (BW * 5, BH), (40, 36, 56, 255))
    for i, p in enumerate([POSE['idle'](0), POSE['raise_'](1), POSE['cast'](1), POSE['point'](1), POSE['hurt'](1)]):
        A.alpha_composite(boss(p), (i * BW, 0))
    A.resize((A.width * 3, A.height * 3), Image.NEAREST).convert('RGB').save(os.path.join(OUT, 'rei_chibi_poses.png'))
