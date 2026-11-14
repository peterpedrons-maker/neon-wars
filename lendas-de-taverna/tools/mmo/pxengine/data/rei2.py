#!/usr/bin/env python3
"""Rei Esquecido (arte real do jogo: cavaleiro de armadura escura, caveira coroada, capa de chamas roxas, espada gigante azul-gelo)
no estilo chibi pixel art. Sprite por codigo; espada e peca SEPARADA na mao. ~1.6x o heroi."""
import math
from PIL import Image
from pxrig import Grid, autoline, line_pts
import chibi as C

BW, BH = 112, 120
PAL = dict(K='#0c0814', d='#14101e', A='#2c2646', a='#4a4272', h='#7a6eae',
           V='#b060f0', v='#ecc0ff', u='#6a2aa8', w='#3a1470',
           M='#1a1228', m='#2c1e46', n='#3c2a60',
           S='#c8c0d4', s='#eee8f6', B='#7a6c98', e='#10061c',
           G='#8a6a2a', g='#d4a444', Z='#e4f8ff', z='#6ab0e4', y='#bfe8ff', N='#1c1830')
SEL = {k: v for k, v in dict(A='#0e0a1c', a='#14102a', h='#1c1638', V='#2a0a50', v='#2a0a50', u='#1a0634', w='#1a0634', M='#08040e', m='#0c0618', n='#0c0618',
                             S='#3e3458', s='#3e3458', B='#241a3c', G='#3a2808', g='#3a2808', Z='#1c4a78', z='#1c4a78', y='#1c4a78', N='#08040e', e='#08040e', d='#08040e').items()}


def ell(g, cx, cy, rx, ry, fn):
    for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
        for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
            u, v = (x + .5 - cx) / rx, (y + .5 - cy) / ry
            if u * u + v * v <= 1: g.put(x, y, fn(u, v))


def shade(lo, mid, hi, th=.36):
    return lambda u, v: hi if (u + v) * .7 < -th else (lo if (u + v) * .7 > th else mid)


def tube(g, p0, p1, w, fn):
    for (x, y) in line_pts(round(p0[0]), round(p0[1]), round(p1[0]), round(p1[1])):
        for dy in range(-(w // 2), w - w // 2):
            for dx in range(-(w // 2), w - w // 2): g.put(x + dx, y + dy, fn(dx, dy))


def flame(g, x, y, h, t, ph=0):
    """chama roxa subindo (3 tons)"""
    for k in range(h):
        wv = int(round(math.sin(t * .9 + ph + k * .55) * (1 + k * .15)))
        w = max(1, (h - k) // 2)
        for q in range(-w + 1, w):
            g.put(x + wv + q, y - k, 'u' if abs(q) >= w - 1 and w > 1 else ('V' if k < h - 2 else 'v'))


def boss(p=None):
    """p: dy, t (fase das chamas), arm_r=(dx,dy) mao da espada rel. ao ombro, arm_l=(dx,dy), sword=angulo (0=baixo,180=cima), jaw, glow, lean"""
    p = p or {}
    dy = p.get('dy', 0); t = p.get('t', 0); jaw = p.get('jaw', 0); glow = p.get('glow', 1)
    lean = p.get('lean', 0)
    g = Grid(BW, BH); cx = BW // 2 + lean
    base = 96 + dy                                   # pes
    # ---- capa de tras (silhueta larga) + chamas roxas
    for y in range(base - 52, base - 2):
        k = (y - (base - 52)) / 50
        hw = 14 + k * 11
        for x in range(int(cx - hw), int(cx + hw) + 1):
            u = (x - cx) / hw
            g.put(x, y, 'M' if abs(u) > .6 or k < .15 else ('m' if u < 0 else 'n'))
    for i, off in enumerate((-24, -18, -12, 12, 18, 24)):
        flame(g, cx + off, base - 1, 7 + (i % 3) * 2, t, i * 1.3)
    flame(g, cx - 4, base - 1, 6, t, 4); flame(g, cx + 5, base - 1, 5, t, 2)
    # ---- pernas e botas
    for sgn in (-1, 1):
        x0 = cx + sgn * 5
        for y in range(base - 14, base - 3):
            for x in range(x0 - 3, x0 + 3):
                g.put(x, y, 'a' if x == x0 - 3 else ('A' if x < x0 + 1 else 'd'))
        for y in range(base - 4, base):
            for x in range(x0 - 4 + (0 if sgn < 0 else 1), x0 + 4 + (0 if sgn < 0 else 1)):
                g.put(x, y, 'A' if y < base - 1 else 'd')
        g.put(x0 - 1, base - 11, 'h'); g.put(x0, base - 11, 'h')            # joelheira
    # ---- tronco (placas)
    ty0, ty1 = base - 38, base - 14
    for y in range(ty0, ty1 + 1):
        k = (y - ty0) / (ty1 - ty0); hw = 11 - k * 3
        for x in range(int(cx - hw), int(cx + hw) + 1):
            u = (x - cx) / hw
            g.put(x, y, 'a' if u < -.45 else ('d' if u > .6 else 'A'))
    for x in range(cx - 9, cx + 10): g.put(x, ty1 - 3, 'g' if x % 2 else 'G'); g.put(x, ty1 - 2, 'G')   # cinto
    g.put(cx - 1, ty1 - 3, 'v'); g.put(cx, ty1 - 3, 'V')
    for yy in range(ty0 + 3, ty0 + 9):                                                     # peitoral com gema
        g.put(cx - 5, yy, 'h'); g.put(cx + 5, yy, 'd')
    ell(g, cx, ty0 + 7, 2.2, 2.6, lambda u, v: 'v' if u + v < -.3 else 'V')
    for k in range(4): g.put(cx - 3 + k * 2, ty0 + 12, 'a')
    # ---- bracos
    shl = (cx - 13, ty0 + 3); shr = (cx + 13, ty0 + 3)
    hl = (shl[0] + p.get('arm_l', (-4, 15))[0], shl[1] + p.get('arm_l', (-4, 15))[1])
    hr = (shr[0] + p.get('arm_r', (6, 15))[0], shr[1] + p.get('arm_r', (6, 15))[1])
    for (s0, h0) in ((shl, hl), (shr, hr)):
        tube(g, s0, h0, 6, lambda a, b: 'a' if a + b < 0 else ('A' if a + b < 2 else 'd'))
        for dx in range(-3, 3):
            for dyy in range(-3, 3):
                if dx * dx + dyy * dyy <= 7: g.put(round(h0[0]) + dx, round(h0[1]) + dyy, 'A' if dx + dyy < 1 else 'd')
        g.put(round(h0[0]) - 1, round(h0[1]) - 2, 'h')
    # ---- ombreiras com espinhos
    for sgn, sh_ in ((-1, shl), (1, shr)):
        ell(g, sh_[0] + sgn * 1, sh_[1] - 1, 8, 6, shade('d', 'A', 'a'))
        for k in range(4): g.put(sh_[0] + sgn * (2 + k * 2), sh_[1] - 7 + k // 2, 'h' if k < 2 else 'a')
        for k in range(3): g.put(sh_[0] + sgn * (3 + k * 2), sh_[1] - 4 - (2 - k) // 2 + 0, 'a')
        g.put(sh_[0] + sgn * 7, sh_[1] - 2, 'V'); g.put(sh_[0] + sgn * 6, sh_[1] - 2, 'u')
        for q in range(-7, 8, 2): g.put(sh_[0] + q + sgn, sh_[1] + 4, 'V')              # borda roxa
    # ---- cabeca: caveira com coroa
    hy = ty0 - 9
    ell(g, cx, hy, 11, 9.5, shade('B', 'S', 's'))
    for y in range(hy + 6 + jaw, hy + 11 + jaw):
        hw = 6 - (y - (hy + 6 + jaw)) * .8
        for x in range(int(cx - hw), int(cx + hw) + 1): g.put(x, y, 'B' if x > cx + 2 else 'S')
    for x in range(cx - 4, cx + 5):
        for y in range(hy + 7 + jaw, hy + 9 + jaw): g.put(x, y, 'e' if (x - cx) % 2 == 0 else 's')
    for sgn in (-1, 1):
        ex = cx + sgn * 4
        for y in range(hy - 3, hy + 3):
            for x in range(ex - 2, ex + 2): g.put(x, y, 'e')
        g.put(ex - 1, hy - 1, 'v'); g.put(ex, hy - 1, 'V'); g.put(ex - 1, hy, 'V'); g.put(ex, hy, 'u')
        if glow > 1: g.put(ex + sgn * 2, hy - 2, 'V'); g.put(ex, hy - 4, 'V')
    g.put(cx - 1, hy + 3, 'e'); g.put(cx, hy + 3, 'e')
    cy0 = hy - 8
    for x in range(cx - 10, cx + 11):                                                       # coroa de ferro
        for yy in range(cy0, cy0 + 3): g.put(x, yy, 'h' if yy == cy0 else ('A' if yy < cy0 + 2 else 'd'))
    for off, hh in {-9: 4, -5: 6, 0: 9, 5: 6, 9: 4}.items():
        for k in range(hh):
            for q in range(2 if k < hh - 2 else 1): g.put(cx + off + q - (1 if k < hh - 2 else 0), cy0 - 1 - k, 'a' if q == 0 else 'A')
        g.put(cx + off, cy0 - hh - 1, 'v' if glow > 1 else 'V')
    for off in (-6, 0, 6): g.put(cx + off, cy0 + 1, 'V'); g.put(cx + off + 1, cy0 + 1, 'v')
    # ---- espada SEPARADA na mao direita (lamina de gelo)
    ang = p.get('sword', 6)
    cells, tip = C.shaped_rows((round(hr[0]), round(hr[1])), ang, 30, 4, 'great', 'cross', None, False, False)
    mp = {'A': 'Z', 'a': 'z', 'g': 'G', 'N': 'N', 'Z': 'y', 'r': 'V'}
    behind = 200 <= ang % 360 <= 262
    sg = Grid(BW, BH)
    for (x, y), ch in cells.items(): sg.put(x, y, mp.get(ch, ch))
    for k, ((x, y), ch) in enumerate(sorted(cells.items())):                                # brilho central na lamina
        if mp.get(ch) == 'Z' and (x + y) % 3 == 0: sg.put(x, y, 'y')
    autoline(g); autoline(sg)
    a = g.render(PAL, SEL); b = sg.render(PAL, SEL)
    out = Image.new('RGBA', (BW, BH), (0, 0, 0, 0))
    if behind: out.alpha_composite(b); out.alpha_composite(a)
    else: out.alpha_composite(a); out.alpha_composite(b)
    return out


POSE = dict(
    idle=lambda f: dict(dy=int(round(math.sin(f * math.pi / 3) * 1)), t=f * .9, arm_r=(6, 15 + int(math.sin(f * math.pi / 3))), sword=22),
    windup=lambda k: dict(dy=-int(2 * k), t=k * 6, arm_r=(8 - 5 * k, 6 - 30 * k), arm_l=(-4 - 5 * k, 15 - 20 * k), sword=int(22 + 176 * k) % 360, jaw=1 if k > .5 else 0, glow=2 if k > .5 else 1, lean=-int(2 * k)),
    slam=lambda k: dict(dy=2, t=k * 9, arm_r=(8, 10), arm_l=(-3, 12), sword=int(190 - 190 * k) % 360 if k < 1 else 0, jaw=2, glow=2, lean=2),
    cast=lambda k: dict(dy=-3, t=k * 8, arm_r=(6, -26), arm_l=(-6, -24), sword=188, jaw=2, glow=2),
    point=lambda k: dict(dy=-1, t=k * 8, arm_r=(24, -4), arm_l=(-5, 13), sword=96, jaw=1, glow=2, lean=-1),
    hurt=lambda k: dict(dy=2, t=k * 8, arm_r=(5, 12), arm_l=(-5, 12), sword=14, jaw=3, glow=0, lean=-2),
)

if __name__ == '__main__':
    import os
    from teste_clareira import OUT
    ps = [POSE['idle'](0), POSE['windup'](1), POSE['slam'](1), POSE['cast'](1), POSE['point'](1), POSE['hurt'](1)]
    A = Image.new('RGBA', (BW * 6, BH), (46, 40, 66, 255))
    for i, p_ in enumerate(ps): A.alpha_composite(boss(p_), (i * BW, 0))
    A.resize((A.width * 3, A.height * 3), Image.NEAREST).convert('RGB').save(os.path.join(OUT, 'rei2_poses.png'))
    b = boss(ps[0]).getbbox(); print(b, b[2] - b[0], b[3] - b[1])
