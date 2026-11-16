"""Animacoes diferentes para inimigos de OUTROS motores (humano.py/fauna.py/creature.py), pos-processando os quadros do proprio motor.
Mesmo principio do chibi_anim3: tempo e reacao seguem o PESO/jeito da criatura. Sempre ataque 20, dano 9, morte 15 quadros (golpe no quadro 11).
Ataque: lunge (investida), pounce (pulo), slam (pancada pesada), cast (conjura). Dano: flinch, stagger, stoic. Morte: fall, topple, tumble, melt, dissolve."""
import math, numpy as np
from PIL import Image
import chibi as C, rotsprite as R
import chibi_anim2 as A2
W, H, BASE = C.W, C.H, C.BASE

def _bb(im): return im.getchannel('A').getbbox()
def xf(im, sx=1., sy=1., dx=0, dy=0):
    """escala em torno do centro dos pes (nearest, sem suavizar) e desloca"""
    im = im.convert('RGBA'); bb = _bb(im)
    if not bb: return im
    c = im.crop(bb); w, h = c.size; nw, nh = max(1, round(w * sx)), max(1, round(h * sy))
    if (nw, nh) != (w, h): c = c.resize((nw, nh), Image.NEAREST)
    cx = (bb[0] + bb[2]) / 2; out = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    out.alpha_composite(c, (int(round(cx - nw / 2)) + dx, bb[3] - nh + dy)); return _clip(out)
def _clip(im):
    bb = _bb(im)
    if not bb or (bb[0] >= 0 and bb[2] <= W and bb[1] >= 0 and bb[3] <= H): return im
    return im
def pick(fr, t): return fr[min(len(fr) - 1, max(0, int(round(t * (len(fr) - 1)))))].convert('RGBA')
def _dirv(view): return {'side': (1, 0), 'front': (0, 1), 'back': (0, -1)}.get(view, (1, 0))
def _sh(im, dx, dy): return A2.shake(im, dx, dy)

def attack(view, fr, st, style):
    ux, uy = _dirv(view); out = []
    for i in range(20):
        if i <= 10: t = .55 * (i / 10) ** 1.6
        elif i <= 14: t = .55 + .25 * (i - 10) / 4
        else: t = .8 + .2 * (i - 14) / 5
        im = pick(fr, t)
        if style == 'lunge':
            if i <= 10: k = i / 10; im = xf(im, 1 - .05 * k, 1 + .05 * k, int(-ux * 2 * k), int(-uy * 2 * k))
            elif i <= 14: k = 1 - abs(i - 12) / 2.5; im = xf(im, 1.08, .94, int(ux * (2 + 3 * k)), int(uy * (2 + 3 * k)))
            else: k = (19 - i) / 5; im = xf(im, 1, 1, int(ux * 2 * k), int(uy * 2 * k))
        elif style == 'pounce':
            if i <= 9: k = i / 9; im = xf(im, 1 + .12 * k, 1 - .18 * k)
            elif i <= 14:
                k = (i - 9) / 5; im = xf(im, .94, 1.1, int(ux * 7 * k), int(uy * 7 * k) - int(math.sin(k * math.pi) * 8) * (1 if view == 'side' else 0))
            else:
                k = (19 - i) / 5; im = xf(im, 1 + .1 * k, 1 - .12 * k, int(ux * 7 * k), int(uy * 7 * k))
                if i == 15: im = A2.dust(im, .15, cx=W // 2 + ux * 7, n=5)
        elif style == 'slam':
            if i <= 10: k = i / 10; im = xf(im, 1 - .03 * k, 1 + .10 * k, 0, -int(3 * k)); im = _sh(im, (-1) ** i if i >= 6 else 0, 0)
            elif i <= 13: im = xf(im, 1.1, .88, int(ux * 2), int(uy * 2)); im = A2.flash(im, .25) if i == 11 else im; im = A2.dust(im, (i - 10) / 4, cx=W // 2 + ux * 8, n=6)
            else: k = (19 - i) / 6; im = xf(im, 1 + .08 * k, 1 - .08 * k)
        else:  # cast
            if i <= 10: k = i / 10; im = xf(im, 1, 1 + .06 * k, -int(ux * 1.5 * k), -int(uy * 1.5 * k) - int(2 * k))
            elif i == 11: im = A2.flash(xf(im, 1.05, 1.0, int(ux * 2), int(uy * 2)), .5)
            else: k = (19 - i) / 8; im = xf(im, 1, 1 + .06 * max(k, 0))
        out.append(im)
    return out

def hurt(view, fr, st, style):
    ux, uy = _dirv(view); out = []
    for i in range(9):
        im = pick(fr, min(1, i / 8))
        if style == 'stoic': im = A2.flash(_sh(st, 1 if i % 2 else -1, 0), .35) if i < 2 else _sh(st, 1 if i % 2 and i < 5 else 0, 0)
        elif style == 'stagger':
            k = math.sin(min(1, i / 8) * math.pi); im = xf(im, 1 - .06 * k, 1 + .04 * k, -int(ux * 5 * k), -int(uy * 5 * k)); im = A2.flash(im, .45) if i == 1 else im
        else:
            k = max(0, 1 - i / 6); im = xf(im, 1 + .1 * k, 1 - .12 * k, -int(ux * 2 * k), -int(uy * 2 * k)); im = A2.flash(im, .5) if i == 1 else im
        out.append(im)
    return out

def _erode(im, k, seed=3):
    a = np.array(im); rng = np.random.RandomState(seed); m = rng.rand(*a.shape[:2])
    ys = np.arange(a.shape[0])[:, None] / a.shape[0]
    a[(m + (1 - ys) * .0 + ys * .0) < k, 3] = 0; return Image.fromarray(a)
def death(view, fr, st, style):
    ux, uy = _dirv(view); piv = (W // 2, BASE + 1); out = []
    hf = A2.flash(_sh(st, -ux, -uy), .4); base = [hf, pick(fr, .6)] if fr else [hf, st]
    if style == 'topple':
        out = base + [_sh(st, 1, 0), _sh(st, -1, 0), st]
        for a in (5, 12, 22, 36, 54, 72, 86, 90): out.append(A2.shake(R.rotate(st, a, piv), 0, 0))
        out[-1] = A2.dust(out[-1], .1, cx=W // 2 + 10, n=6)
    elif style == 'fall':
        low = A2.lying(st, feet_x=W // 2 + 8)
        out = base + [xf(st, 1, 1.02, -1), xf(st, 1.02, .96, -2), xf(st, 1.05, .9, -3)]
        for k in range(1, 7): out.append(xf(low, 1, 1, 0, 0) if k > 3 else R.rotate(st, -25 * k, piv))
        out.append(A2.dust(low, .2, cx=W // 2, n=6)); out.append(A2.dust(low, .6, cx=W // 2, n=6))
    elif style == 'tumble':
        out = base
        for k in range(1, 9):
            t = k / 8; im = R.rotate(st, -min(90, 540 * t) % 360 if t < 1 else -90, (W // 2, BASE - 10))
            out.append(xf(im, 1, 1, int(-ux * 12 * t), int(-uy * 12 * t) - int(math.sin(t * math.pi) * 10)))
        out.append(A2.dust(out[-1], .2, cx=W // 2 - 10, n=6)); out.append(A2.dust(out[-2], .6, cx=W // 2 - 10, n=6))
        out = out[:15]
    elif style == 'flip':   # bichos: capotam e ficam de barriga para cima
        out = base
        def gr(im, lift=0):
            bb = _bb(im); o = Image.new('RGBA', (W, H), (0, 0, 0, 0)); o.alpha_composite(im.crop(bb), (bb[0], BASE + 1 - lift - (bb[3] - bb[1]) )); return o
        for k in range(1, 9):
            t = k / 8; im = R.rotate(st, -180 * min(1, t * 1.15) * ux if ux else -180 * t, (W // 2, BASE - 8))
            out.append(gr(im, int(math.sin(min(1, t * 1.2) * math.pi) * 8) if t < .85 else 0))
        out.append(A2.dust(out[-1], .2, cx=W // 2, n=6)); out.append(A2.dust(out[-2], .6, cx=W // 2, n=6))
    elif style == 'melt':
        out = base + [_sh(st, 1, 0)]
        for k in range(1, 12):
            t = k / 11; im = xf(st, 1 + .5 * t, max(.08, 1 - .95 * t)); out.append(_erode(im, max(0, t - .5) * 1.2, 5) if t > .5 else im)
    else:  # dissolve
        out = base + [_sh(st, 1, 0)]
        for k in range(1, 12):
            t = k / 11; im = xf(st, 1 - .1 * t, 1 + .15 * t, 0, -int(4 * t)); out.append(_erode(im, t * 1.05, 9))
    while len(out) < 15: out.append(out[-1])
    return out[:15]

def build(kind, fr, view, style_set, stand):
    st = stand.convert('RGBA'); fr = [f.convert('RGBA') for f in fr]
    if kind == 'attack': return attack(view, fr, st, style_set['attack'])
    if kind == 'hurt': return hurt(view, fr, st, style_set['hurt'])
    return death(view, fr, st, style_set['death'])
