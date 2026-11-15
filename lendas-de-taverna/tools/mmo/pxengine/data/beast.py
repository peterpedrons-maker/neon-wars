#!/usr/bin/env python3
"""Animais (rato, javali) no estilo chibi pixel art: quadrupedes por codigo, 3 vistas (down/up/right; left = espelho),
idle/walk/attack/hurt/death com dense=2. Mesmo canvas W,H do heroi (pes em BASE) para entrar nas mesmas cenas."""
import math
from PIL import Image
from pxrig import Grid, autoline
import chibi as C

W, H, BASE = C.W, C.H, C.BASE


class G(Grid):
    def put(self, x, y, ch): super().put(int(round(x)), int(round(y)), ch)

PALS = {
    'rato': dict(K='#0c0814', f='#8e8698', F='#bcb4c8', e='#5a5468', n='#f2a4b4', N='#c2607a', c='#dcd4e4', t='#eaa0aa', w='#f8f4ec', k='#14101c', r='#ff5060', x='#ffffff'),
    'javali': dict(K='#0c0814', f='#8e5c38', F='#be8450', e='#4e2e18', n='#dc9c8a', N='#a45a4c', c='#cca474', t='#a45a4c', w='#f6f2e2', k='#14100c', r='#ff7a30', x='#ffffff'),
    'lobo': dict(K='#0c0814', f='#7a8294', F='#aab2c4', e='#4a5266', n='#2a2a34', N='#14141c', c='#d0d6e4', t='#7a8294', w='#f8f4ec', k='#14101c', r='#ffd030', x='#ffffff'),
}
SELS = {n: {'f': '#26222e', 'F': '#26222e', 'e': '#14101c', 'c': '#3a3446', 'n': '#5a2030', 'N': '#3a1020', 't': '#5a2030', 'w': '#7a7468', 'k': '#000000', 'r': '#4a0c0c', 'x': '#555555'} for n in PALS}
for n, col in (('javali', '#2a1608'), ('lobo', '#1a1e2c')): SELS[n].update({'f': col, 'F': col, 'e': '#0c0804', 'c': '#5a4020'})


def ell(g, cx, cy, rx, ry, fn):
    for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
        for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
            u, v = (x + .5 - cx) / rx, (y + .5 - cy) / ry
            if u * u + v * v <= 1: g.put(x, y, fn(u, v))


def shade(lo, mid, hi, th=.34):
    return lambda u, v: hi if (u + v) * .7 < -th else (lo if (u + v) * .7 > th else mid)


def rect(g, x0, y0, w, h, ch):
    for yy in range(h):
        for xx in range(w): g.put(x0 + xx, y0 + yy, ch)


SPEC = {
    'rato': dict(body=(7.5, 5), head=(5.5, 4.6), legh=3, legw=3, big=0),
    'javali': dict(body=(10, 7), head=(7, 6), legh=4, legw=4, big=1),
    'lobo': dict(body=(10, 6), head=(6, 5), legh=5, legw=3, big=0),
}


def draw(kind, view, ph=0.0, bob=0, lunge=0, mouth=0, squint=False, tail=0.0, head_dy=0, ear=0):
    sp = SPEC[kind]; g = G(W, H); cx = W // 2; gy = BASE
    br, bh = sp['body']; hr, hh = sp['head']; lh = sp['legh']; lw = sp['legw']
    s, c = math.sin(ph), math.cos(ph)
    f_ = lambda lo, mid, hi: shade(lo, mid, hi)
    if view == 'right':
        bx = cx - 4 + lunge * .5; by = gy - lh - bh + 1 + bob
        # cauda (atras)
        if kind == 'rato':
            for i in range(14):
                tx = bx - br - i * .9; ty = by + 1 + math.sin(i * .55 + tail) * 2 + i * .12
                g.put(round(tx), round(ty), 't'); g.put(round(tx), round(ty) + 1, 't')
        elif kind == 'lobo':
            for i in range(9):
                tx = bx - br - i * .7; ty = by - 2 + i * .45 + math.sin(tail + i * .4)
                ell(g, tx, ty, 2.2 - i * .12, 2.2 - i * .12, shade('e', 'f', 'F'))
        else:
            for i in range(4): g.put(round(bx - br - i), round(by - 1 - (1 if i > 1 else 0) + math.sin(tail) * 0), 'e'); g.put(round(bx - br - i), round(by - 1), 'e')
        # pernas (pares diagonais)
        for i, (lxo, ph0) in enumerate(((-br + 3, 0), (-br + 7, math.pi), (br - 6, math.pi), (br - 2, 0))):
            lift = max(0, math.sin(ph + ph0)) * 2.2 if ph != 0 or True else 0
            sw = math.cos(ph + ph0) * 1.6
            lx = bx + lxo + sw; ly = gy - lh - lift
            rect(g, round(lx) - lw // 2, round(ly), lw, lh + round(lift) - (1 if i % 2 else 0), 'e' if i in (0, 1) else 'f')
            rect(g, round(lx) - lw // 2, gy - 1 - round(lift), lw + 1, 1, 'e')
        # corpo
        ell(g, bx, by, br, bh, f_('e', 'f', 'F'))
        ell(g, bx + 1, by + bh * .55, br * .7, bh * .4, lambda u, v: 'c')
        if kind == 'javali':
            for k in range(7): g.put(round(bx - br + 2 + k * 2.4), round(by - bh - 1 + (k % 2)), 'e'); g.put(round(bx - br + 2 + k * 2.4), round(by - bh), 'e')
        # cabeca
        hx = bx + br + hr - 4 + lunge * .5; hy = by - 1 + head_dy + (2 if kind == 'javali' else 0)
        ell(g, hx, hy, hr, hh, f_('e', 'f', 'F'))
        if kind == 'rato':
            ell(g, hx + hr - 1, hy + 1, 2.4, 1.8, lambda u, v: 'n'); g.put(round(hx + hr + 1), round(hy), 'N')
            ell(g, hx - 1, hy - hh + 1 + ear, 2.6, 2.6, lambda u, v: 'F' if u * u + v * v > .35 else 'n')
            g.put(round(hx + 2), round(hy - 1), 'k'); g.put(round(hx + 2), round(hy - 2), 'k')
            if not squint: g.put(round(hx + 3), round(hy - 2), 'x') if False else g.put(round(hx + 2), round(hy - 2), 'x')
            for q in range(3): g.put(round(hx + hr + 1 + q), round(hy + 2 + (q - 1)), 'k')
            if mouth: rect(g, round(hx + hr - 2), round(hy + 3), 3, 2, 'k'); g.put(round(hx + hr - 2), round(hy + 3), 'w'); g.put(round(hx + hr), round(hy + 3), 'w')
            else: g.put(round(hx + hr - 2), round(hy + 3), 'w'); g.put(round(hx + hr - 1), round(hy + 3), 'w')
        elif kind == 'javali':
            ell(g, hx + hr - 1, hy + 2, 3.6, 3.2, shade('N', 'n', 'n')); g.put(round(hx + hr + 1), round(hy + 1), 'k'); g.put(round(hx + hr + 2), round(hy + 2), 'k')
            for q in range(4): g.put(round(hx + hr - 1 + q * .6), round(hy + 5 - q), 'w'); g.put(round(hx + hr - 1 + q * .6) + 1, round(hy + 4 - q), 'w')
            ell(g, hx - 1, hy - hh + 1, 2.4, 3, lambda u, v: 'e')
            g.put(round(hx + 2), round(hy - 2), 'r' if not squint else 'k'); g.put(round(hx + 1), round(hy - 2), 'k')
            if mouth: rect(g, round(hx + hr - 2), round(hy + 5), 4, 2, 'k')
        else:                                                                       # lobo
            ell(g, hx + hr + 1, hy + 1, 3.6, 2.4, shade('e', 'f', 'F')); g.put(round(hx + hr + 4), round(hy), 'n'); g.put(round(hx + hr + 4), round(hy) + 1, 'n')
            for dx in (0, 3): g.put(round(hx - 1 + dx), round(hy - hh), 'f'); g.put(round(hx - 1 + dx), round(hy - hh - 1), 'f'); g.put(round(hx + dx), round(hy - hh - 2), 'F')
            g.put(round(hx + 2), round(hy - 2), 'r' if not squint else 'k')
            if mouth: rect(g, round(hx + hr), round(hy + 2), 4, 2, 'k'); g.put(round(hx + hr + 1), round(hy + 2), 'w'); g.put(round(hx + hr + 3), round(hy + 2), 'w')
    else:
        back = view == 'up'
        by = gy - lh - bh + 1 + bob; bx = cx; hy = by - 3 + head_dy + lunge * .3
        for i, lxo in enumerate((-br + 3, br - 3)):
            lift = max(0, math.sin(ph + (0 if i == 0 else math.pi))) * 2.2
            rect(g, round(bx + lxo) - lw // 2, round(gy - lh - lift), lw, lh + round(lift), 'f'); rect(g, round(bx + lxo) - lw // 2, gy - 1 - round(lift), lw + 1, 1, 'e')
        ell(g, bx, by + 1, br * .85, bh, f_('e', 'f', 'F'))
        if back:
            if kind == 'rato':
                for i in range(10): g.put(round(bx + math.sin(i * .6 + tail) * 2), round(by + bh - 1 + i * .8), 't')
            elif kind == 'lobo':
                ell(g, bx + math.sin(tail) * 2, by + bh + 1, 2.4, 4, shade('e', 'f', 'F'))
            else: g.put(bx, by + bh - 1, 'e'); g.put(bx, by + bh, 'e')
            if kind == 'javali':
                for k in range(-4, 5, 2): g.put(bx + k, by - bh + 1, 'e')
        ell(g, bx, hy - (0 if back else 0) + 1, hr * (1.0 if kind != 'rato' else .95), hh, f_('e', 'f', 'F'))
        hr_ = hr
        if kind == 'rato':
            for sg in (-1, 1): ell(g, bx + sg * (hr - 1), hy - hh + 1 + ear, 2.8, 2.8, lambda u, v: 'F' if u * u + v * v > .35 else 'n')
        elif kind == 'javali':
            for sg in (-1, 1): ell(g, bx + sg * (hr - 1), hy - hh + 1, 2.4, 3, lambda u, v: 'e')
        else:
            for sg in (-1, 1):
                for q in range(3): g.put(bx + sg * (hr - 2 - q * 0), round(hy - hh - q), 'f')
        if not back:
            for sg in (-1, 1):
                ex = bx + sg * 3
                g.put(ex, hy - 1, 'k'); g.put(ex, hy, 'k') if not squint else g.put(ex, hy - 1, 'k')
                g.put(ex - (1 if sg > 0 else 0) + (0 if sg > 0 else 0), hy - 2, 'x') if False else g.put(ex, hy - 2, 'r' if kind != 'rato' else 'x')
            if kind == 'rato':
                ell(g, bx, hy + 3, 2.2, 1.8, lambda u, v: 'n'); g.put(bx, hy + 5, 'w'); g.put(bx - 1, hy + 5, 'w') if True else None; g.put(bx + 1, hy + 5, 'w')
                for q in range(3): g.put(bx - 5 - q, hy + 3 + (q - 1), 'k'); g.put(bx + 5 + q, hy + 3 + (q - 1), 'k')
            elif kind == 'javali':
                ell(g, bx, hy + 3, 4, 3, shade('N', 'n', 'n')); g.put(bx - 1, hy + 3, 'k'); g.put(bx + 1, hy + 3, 'k')
                for sg in (-1, 1): g.put(bx + sg * 4, hy + 5, 'w'); g.put(bx + sg * 4, hy + 4, 'w'); g.put(bx + sg * 5, hy + 3, 'w')
            else:
                ell(g, bx, hy + 3, 2.6, 2.2, shade('e', 'f', 'F')); g.put(bx, hy + 4, 'n'); g.put(bx - 1, hy + 4, 'n')
            if mouth: rect(g, bx - 2, hy + 5, 4, 2, 'k')
    autoline(g)
    return g.render(PALS[kind], SELS[kind])


def anim(kind, k, view, dense=2):
    n = {'idle': 6, 'walk': 8, 'attack': 10, 'hurt': 4, 'death': 6}[k] * dense
    out = []
    for i in range(n):
        u = i / max(1, n - 1)
        if k == 'idle': im = draw(kind, view, 0, bob=int(round(math.sin(2 * math.pi * i / n))) * (1 if view != 'right' else 1) * 0 + (1 if math.sin(2 * math.pi * i / n) > .5 else 0), tail=2 * math.pi * i / n * 2, ear=1 if i % n in (n - 3, n - 2) else 0, squint=i % n in (n - 3, n - 2))
        elif k == 'walk': im = draw(kind, view, 2 * math.pi * i / n, bob=-1 if abs(math.sin(2 * math.pi * i / n * 2)) > .8 else 0, tail=4 * math.pi * i / n)
        elif k == 'attack':
            t = math.sin(min(1, u * 1.15) * math.pi)
            wind = -3 if u < .3 else 0
            lunge = int(round(wind * math.sin(u / .3 * math.pi / 2))) if u < .3 else int(round(9 * math.sin((u - .3) / .7 * math.pi)))
            im = draw(kind, view, 0, bob=0, lunge=lunge, mouth=1 if .4 < u < .75 else 0, head_dy=-2 if kind == 'javali' and u > .4 and u < .8 else (1 if .4 < u < .75 else 0), tail=u * 10)
        elif k == 'hurt': im = draw(kind, view, 0, lunge=-int(round(3 * math.sin(u * math.pi))), squint=True, mouth=1 if u < .6 else 0, head_dy=-1)
        else:
            base = draw(kind, view, 0, lunge=-3 if u < .3 else -4, squint=True, mouth=1)
            if u < .35: im = base
            else:
                im = base.transpose(Image.FLIP_TOP_BOTTOM).transform(base.size, Image.AFFINE, (1, 0, 0, 0, 1, -(H - BASE - 2) * 0 + 0))
                bb = im.getbbox()
                if bb:
                    sh = BASE - bb[3] + 1; im2 = Image.new('RGBA', base.size, (0, 0, 0, 0)); im2.alpha_composite(im, (0, sh)); im = im2
        out.append((im, None, False))
    return out


if __name__ == '__main__':
    import os
    from teste_clareira import OUT
    kinds = ('rato', 'javali', 'lobo')
    S = Image.new('RGBA', (56 * 12, 46 * 3 * len(kinds) * 1), (52, 70, 52, 255)); y = 0
    for kd in kinds:
        for vi, v in enumerate(('right', 'down', 'up')):
            x = 0
            for k, idxs in (('idle', (0, 4)), ('walk', (0, 4, 8, 12)), ('attack', (0, 8, 12, 15)), ('hurt', (2,)), ('death', (8,))):
                seq = anim(kd, k, v)
                for i in idxs: S.alpha_composite(seq[i][0].crop((8, 2, 64, 48)), (x * 56, y)); x += 1
            y += 46
    S.crop((0, 0, 56 * 12, y)).resize((56 * 12 * 2, y * 2), Image.NEAREST).convert('RGB').save(os.path.join(OUT, 'bichos_teste.png'))
