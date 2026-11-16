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

def _ease_in(t): return t * t
def _ease_out(t): return 1 - (1 - t) ** 2
def _ground(im, lift=0, margin=1):
    """pousa no chao (base do bbox em BASE+1) e mantem dentro do quadro"""
    bb = _bb(im)
    if not bb: return im
    dx = 0
    if bb[2] > W - margin: dx = (W - margin) - bb[2]
    if bb[0] + dx < margin: dx = margin - bb[0]
    o = Image.new('RGBA', (W, H), (0, 0, 0, 0)); o.alpha_composite(im.crop(bb), (bb[0] + dx, BASE + 1 - lift - (bb[3] - bb[1]))); return o
def _pivot(st): bb = _bb(st); return ((bb[0] + bb[2]) / 2, bb[3])
def _hit(st, ux, uy):
    """3 quadros de impacto: clarao + recuo com achatamento, segura, comeca a ceder (sem trocar de pose)"""
    return [A2.flash(xf(st, 1.04, .94, -ux * 2, -uy * 2), .35), xf(st, 1.05, .93, -ux * 3, -uy * 3), xf(st, 1.02, .97, -ux * 2, -uy * 2)]
def _dissolve(st, t, seed=9):
    a = np.array(st.convert('RGBA')); hh, ww = a.shape[:2]
    rng = np.random.RandomState(seed); n = rng.rand(hh, ww)
    ys = np.arange(hh)[:, None]; bb = _bb(st); yr = np.clip((ys - bb[1]) / max(1, bb[3] - bb[1]), 0, 1)
    score = n * .45 + (1 - yr) * .55          # topo some primeiro
    gone = (score < t * 1.25) & (a[..., 3] > 0)
    out = a.copy(); out[gone, 3] = 0
    parts = Image.fromarray(out)
    # cinza subindo dos pixels que sumiram (esparso)
    ys_, xs_ = np.where(gone & (((np.arange(ww)[None, :] * 7 + ys * 13) % 5) == 0))
    o = np.array(parts)
    for y, x in zip(ys_, xs_):
        d = int((t * 1.25 - score[y, x]) * 14) + 1; yy = y - d; xx = x + (1 if (x + y) % 2 else -1) * (d // 4)
        if 0 <= yy < hh and 0 <= xx < ww and o[yy, xx, 3] == 0:
            g = int(150 - 60 * min(1, d / 14)); o[yy, xx] = (g, g - 8, g - 4, int(220 * (1 - min(1, d / 15))))
    return Image.fromarray(o)
def _colscale(im, fs, rs, drop=0):
    """deforma por colunas (vista de lado, de frente para a direita): a frente (direita) encolhe em altura por fs, a traseira por rs; interpola no meio"""
    a = np.array(im.convert('RGBA')); bb = _bb(im)
    if not bb: return im
    x0, y0, x1, y1 = bb; out = np.zeros_like(a); ww = max(1, x1 - x0 - 1)
    for x in range(x0, x1):
        w = (x - x0) / ww; w = w * w * (3 - 2 * w); s = 1 - (rs * (1 - w) + fs * w)
        col = a[y0:y1, x]; h = y1 - y0; nh = max(1, int(round(h * s)))
        idx = np.minimum(h - 1, (np.arange(nh) * h / nh).astype(int)); nc = col[idx]
        top = y1 - nh + drop
        if top >= 0 and top + nh <= a.shape[0]: out[top:top + nh, x] = nc
    return Image.fromarray(out)
def _collapse(st, view, hit):
    """quadrupede cedendo: patas da FRENTE dobram primeiro, depois as de TRAS, ate deitar de lado"""
    out = list(hit)
    if view != 'side':
        for k in range(1, 13):
            t = k / 12; e = _ease_in(t); out.append(xf(st, 1 + .35 * e, max(.45, 1 - .55 * e), 0, 0))
        out[-3] = A2.dust(out[-3], .3, cx=W // 2, n=6)
        return out
    seq = []
    for k in range(1, 5): seq.append((.32 * _ease_out(k / 4), 0.0, 0))                       # frente cede (focinho cai)
    for k in range(1, 5): seq.append((.32 + .04 * k / 4, .36 * _ease_out(k / 4), 0))         # traseira cede
    for k in range(1, 5): seq.append((.36 + .04 * k / 4, .36 + .06 * k / 4, 0))              # tomba de lado, acomoda
    for fs, rs, dr in seq: out.append(_colscale(st, fs, rs, dr))
    out[3 + 3] = A2.dust(out[3 + 3], .25, cx=W // 2 + 8, n=5)   # patas da frente batem no chao
    out[3 + 7] = A2.dust(out[3 + 7], .3, cx=W // 2 - 8, n=5)    # traseira bate
    out[3 + 11] = A2.dust(out[3 + 11], .5, cx=W // 2, n=6)
    return out
def death(view, fr, st, style):
    ux, uy = _dirv(view); px, py = _pivot(st); out = _hit(st, ux, uy)
    sgn = -1 if style in ('fall', 'tumble', 'flip') else 1        # cai para tras (longe do golpe) ou para a frente (topple)
    if view != 'side': sgn = -1
    if style == 'collapse': out = _collapse(st, view, out)
    elif style in ('fall', 'topple'):
        lean = [-2 * sgn, -5 * sgn] if style == 'fall' else [3 * sgn, 6 * sgn]      # antecipacao: inclina o contrario/cede antes de cair
        out += [_ground(R.rotate(st, lean[0], (px, py))), _ground(R.rotate(st, lean[1], (px, py)))]
        for k in range(1, 7):                                                        # gravidade: acelera ate 90
            ang = sgn * (lean[1] * sgn * 0 + 90 * _ease_in(k / 6)) if k < 6 else sgn * 90
            ang = sgn * max(abs(lean[1]), 90 * _ease_in(k / 6)) if k < 6 else sgn * 90
            out.append(_ground(R.rotate(st, ang, (px, py))))
        low = out[-1]
        out.append(A2.dust(_ground(R.rotate(st, sgn * 84, (px, py)), 1), .25, cx=int(px), n=6))       # quique
        out.append(A2.dust(low, .6, cx=int(px), n=6)); out.append(low)
    elif style == 'tumble':
        out += [xf(st, 1.0, 1.04, -ux * 3, -uy * 3 - 2)]
        for k in range(1, 8):
            t = k / 7; arc = int(math.sin(t * math.pi) * 9); ang = sgn * 90 * _ease_out(t) * (1 + .5 * (1 - t)) * (1 if t < 1 else 1)
            im = R.rotate(st, max(-100, min(100, ang)) if sgn < 0 else min(100, ang), (px, py - 10))
            out.append(_ground(im, arc))
        out.append(A2.dust(_ground(R.rotate(st, sgn * 84, (px, py)), 1), .25, cx=int(px), n=6)); out.append(A2.dust(_ground(R.rotate(st, sgn * 90, (px, py))), .6, cx=int(px), n=6)); out.append(_ground(R.rotate(st, sgn * 90, (px, py))))
    elif style == 'flip':
        out += [xf(st, 1.0, 1.05, -ux * 3, -uy * 3 - 3)]
        for k in range(1, 8):
            t = k / 7; arc = int(math.sin(t * math.pi) * 10); ang = 180 * _ease_out(t) * (-1 if ux >= 0 else 1)
            out.append(_ground(R.rotate(st, ang, (px, py - 8)), arc))
        low = out[-1]; out.append(A2.dust(_ground(R.rotate(st, -168, (px, py - 8)), 2), .25, cx=int(px), n=6)); out.append(A2.dust(low, .6, cx=int(px), n=6)); out.append(low)
    elif style == 'melt':
        for k in range(1, 13):
            t = k / 12
            wob = math.sin(t * 9) * .09 * (1 - t) if k < 7 else 0           # gelatina treme antes de derreter
            e = _ease_in(max(0, (t - .15) / .85))
            im = xf(st, 1 + .55 * e + wob, max(.07, 1 - .93 * e - wob))
            if t > .78:
                a = np.array(im); a[..., 3] = (a[..., 3] * max(0., 1 - (t - .78) / .3)).astype(np.uint8); im = Image.fromarray(a)
            out.append(im)
    else:  # dissolve
        for k in range(1, 13):
            t = k / 12; out.append(_dissolve(xf(st, 1 - .06 * t, 1 - .04 * t, 0, int(2 * t)), t))
    while len(out) < 15: out.append(out[-1])
    return out[:15]

def build(kind, fr, view, style_set, stand):
    st = stand.convert('RGBA'); fr = [f.convert('RGBA') for f in fr]
    if kind == 'attack': return attack(view, fr, st, style_set['attack'])
    if kind == 'hurt': return hurt(view, fr, st, style_set['hurt'])
    return death(view, fr, st, style_set['death'])
