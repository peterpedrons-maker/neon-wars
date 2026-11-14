#!/usr/bin/env python3
"""Criaturas sem pernas no estilo chibi: slime (pula), morcego (voa, bate asas), espectro (flutua). Mesmo canvas/pes dos outros; 3 vistas; dense=2."""
import math
from PIL import Image
from pxrig import Grid, autoline
import chibi as C
import beast as B

W, H, BASE = C.W, C.H, C.BASE
PALS = {
    'slime': dict(K='#0c0814', f='#4cc058', F='#96f0a0', e='#24803a', k='#10140c', w='#ffffff', n='#2a9a44', r='#ff7a8a'),
    'morcego': dict(K='#0c0814', f='#6a4a8c', F='#9a78c0', e='#3a2458', k='#10061c', w='#f8f4ec', n='#c04a6a', r='#ff4a5a', u='#4a2e6c', U='#2a1840'),
    'espectro': dict(K='#0c0814', f='#a8d8f0', F='#e4f6ff', e='#5a8ab8', k='#0a1a2c', w='#ffffff', n='#6ad0ff', r='#bff4ff'),
}
SELS = {'slime': {c: '#103a1c' for c in 'fFen'}, 'morcego': {c: '#14081e' for c in 'fFeuU'}, 'espectro': {c: '#2a4a70' for c in 'fFe'}}
for n in SELS: SELS[n].update({'k': '#000000', 'w': '#6a6a70', 'r': '#40101a', 'n': SELS[n].get('n', '#1a3050')})


def draw(kind, view, ph=0.0, sq=1.0, dy=0, lunge=0, face=0, flap=0.0, tail=0.0, arms=0.0):
    g = B.G(W, H); cx = W // 2 + lunge
    if kind == 'slime':
        rx = 12 / math.sqrt(sq); ry = 12 * sq; cy = BASE - ry + 1 + dy
        B.ell(g, cx, cy, rx, ry, B.shade('e', 'f', 'F'))
        B.ell(g, cx - rx * .35, cy - ry * .45, max(1.5, rx * .22), max(1, ry * .16), lambda u, v: 'w')
        ox = 0 if view != 'right' else 4
        ex = ((-4, 4) if view == 'down' else ((2, 6) if view == 'right' else (-4, 4)))
        if view != 'up':
            for e_ in ex:
                B.rect(g, cx + e_ - 1 + (ox if view == 'right' else 0) * 0, round(cy - ry * .1), 2, 3 if face != 2 else 1, 'k'); g.put(cx + e_ - 1, round(cy - ry * .1), 'w')
            if face == 1: B.rect(g, cx + ex[0] + 1, round(cy + ry * .35), 5, 2, 'k')
            else: g.put(cx + ex[0] + 3 if view != 'right' else cx + 5, round(cy + ry * .35), 'k')
        for k in range(3): g.put(cx - 3 + k * 3, round(BASE - 1), 'e')
    elif kind == 'morcego':
        by = BASE - 26 + dy; wl = math.sin(flap) * 9
        for sg in (-1, 1) if view != 'right' else (-1,):
            tip = (cx + sg * 17, by + 3 - wl + (4 if view == 'right' else 0)); mid = (cx + sg * 10, by - 4 - wl * .5)
            for i in range(12):
                t = i / 11
                px = cx + sg * 3 + (tip[0] - cx - sg * 3) * t; py = by + (tip[1] - by) * t + math.sin(t * math.pi) * -4 + (mid[1] - by) * (1 - t) * .5
                B.rect(g, round(px), round(py), 1, round(4 + 5 * (1 - abs(t - .5) * 2) + t * 2), 'u')
            g.put(round(tip[0]), round(tip[1]), 'U')
        B.ell(g, cx, by + 2, 4.5, 6, B.shade('e', 'f', 'F')); B.ell(g, cx, by - 5, 5, 4.5, B.shade('e', 'f', 'F'))
        for sg in (-1, 1): B.rect(g, cx + sg * 4 - (0 if sg > 0 else 1), by - 11, 2, 4, 'f'); g.put(cx + sg * 4, by - 12, 'F')
        if view != 'up':
            for sg in (-1, 1): g.put(cx + sg * 2, by - 5, 'r'); g.put(cx + sg * 2, by - 4, 'r')
            if face == 1: B.rect(g, cx - 1, by - 2, 3, 2, 'k'); g.put(cx - 1, by, 'w'); g.put(cx + 1, by, 'w')
        for sg in (-1, 1): g.put(cx + sg * 2, by + 8, 'n'); g.put(cx + sg * 2, by + 9, 'n')
    else:                                                            # espectro
        by = BASE - 30 + dy
        B.ell(g, cx, by, 9, 8, B.shade('e', 'f', 'F'))
        for y in range(by + 4, by + 28):
            t = (y - by - 4) / 24; hw = 9 - t * 6 + math.sin(y * .5 + tail) * 1.5
            for x in range(int(cx - hw), int(cx + hw) + 1): g.put(x, y, 'F' if x < cx - hw * .3 else 'f' if x < cx + hw * .5 else 'e')
        for sg in (-1, 1):
            ax = cx + sg * (10 + arms * 5); ay = by + 10 - arms * 6
            for i in range(9): g.put(cx + sg * (7 + i * (ax - cx - sg * 7) / 9 * sg if False else 0) + int(sg * (7 + i * .7 + arms * i * .4)), round(by + 8 + i * .7 - arms * i * .5), 'f')
            B.ell(g, ax, ay, 2.2, 2.4, lambda u, v: 'F')
        if view != 'up':
            for sg in (-1, 1): B.rect(g, cx + sg * 4 - 1, by - 2, 3, 4, 'k'); g.put(cx + sg * 4, by - 1, 'r'); g.put(cx + sg * 4, by, 'n')
            B.rect(g, cx - 2, by + 4, 5, 3 if face == 1 else 1, 'k')
    autoline(g)
    im = g.render(PALS[kind], SELS[kind])
    if kind == 'espectro':
        a = im.split()[3].point(lambda v: 205 if v else 0); im.putalpha(a)
    return im


def anim(kind, k, view, dense=2):
    n = {'idle': 6, 'walk': 8, 'attack': 10, 'hurt': 4, 'death': 6}[k] * dense; out = []
    for i in range(n):
        u = i / max(1, n - 1); ph = 2 * math.pi * i / n; kw = {}
        if kind == 'slime':
            if k == 'idle': kw = dict(sq=1 + .07 * math.sin(ph))
            elif k == 'walk':
                hop = max(0, math.sin(ph)); kw = dict(sq=1.18 - .05 * hop if hop > .15 else .8, dy=-int(round(hop * 8)))
            elif k == 'attack': kw = dict(sq=.75 if u < .3 else 1.3 if u < .7 else .95, lunge=int(round(10 * math.sin(max(0, u - .3) / .7 * math.pi))), face=1 if .3 < u < .8 else 0)
            elif k == 'hurt': kw = dict(sq=.7 + .3 * u, lunge=-int(round(3 * math.sin(u * math.pi))), face=2)
            else: kw = dict(sq=max(.18, 1 - u * .95), face=2)
        elif kind == 'morcego':
            if k == 'idle': kw = dict(flap=ph * 3, dy=int(round(math.sin(ph) * 2)))
            elif k == 'walk': kw = dict(flap=ph * 4, dy=int(round(math.sin(ph * 2) * 2)))
            elif k == 'attack': kw = dict(flap=ph * 5, dy=int(round(16 * math.sin(u * math.pi))) - (3 if u < .25 else 0), face=1 if .35 < u < .8 else 0)
            elif k == 'hurt': kw = dict(flap=ph * 6, dy=int(round(-3 * math.sin(u * math.pi))), lunge=-int(round(3 * math.sin(u * math.pi))))
            else: kw = dict(flap=ph * (1 - u) * 3, dy=int(round(u * 26)), face=0)
        else:
            if k == 'idle': kw = dict(tail=ph, dy=int(round(math.sin(ph) * 2)))
            elif k == 'walk': kw = dict(tail=ph * 2, dy=int(round(math.sin(ph) * 2)), arms=.3)
            elif k == 'attack': kw = dict(tail=ph * 2, arms=1.0 if .3 < u < .8 else .3, lunge=int(round(8 * math.sin(max(0, u - .25) / .75 * math.pi))), face=1 if .3 < u < .8 else 0)
            elif k == 'hurt': kw = dict(tail=ph * 3, lunge=-int(round(3 * math.sin(u * math.pi))))
            else: kw = dict(tail=ph, dy=-int(u * 10), arms=u)
        im = draw(kind, view, ph, **kw)
        if kind == 'espectro' and k == 'death': im.putalpha(im.split()[3].point(lambda v, q=1 - u: int(v * q)))
        if kind == 'slime' and k == 'death' and u > .6: im.putalpha(im.split()[3].point(lambda v, q=max(0, 1 - (u - .6) / .4): int(v * q)))
        out.append((im, None, False))
    return out
