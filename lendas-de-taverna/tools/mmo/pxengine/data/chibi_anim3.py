"""Animacao v3 do chibi: ESTILOS diferentes por personagem (dono: 'todos os humanoides tem o mesmo ataque, dano e morte').
appearance['anim'] = dict(attack=..., hurt=..., death=...). Peso (leve/pesado) decide o tempo: pesado = antecipacao lenta, pausa tremendo, impacto
com poeira, reacao contida; leve = rapido, recuo grande. O que nao for pedido cai no chibi_anim2 (padrao).
  attack: slash (padrao) | smash (pancada pesada) | jab (estocada) | cast (conjura)
  hurt  : flinch (padrao) | stagger (recuo grande) | stoic (quase nao se move)
  death : fall (padrao, cai de costas) | topple (tomba de frente, pesado) | crumble (vira pilha de ossos) | dissolve (vira cinza) | tumble (e arremessado girando)
Todos mantem a contagem de quadros do v2 (ataque 20, dano 9, morte 15): o jogo sincroniza o dano pelo indice."""
import math, random
import numpy as np
from PIL import Image
import chibi as C
import chibi_anim2 as N2
import rotsprite as R
W, H, BASE = C.W, C.H, C.BASE
_arr, flash, shake, dust, lying = N2._arr, N2.flash, N2.shake, N2.dust, N2.lying

# ---------- ataque: estocada (jab) ----------
def _thrust(view):
    sw = (lambda a: dict(ang=a, len=12)) if view == 'right' else (lambda a: dict(ang=a, len=12, side='r'))
    if view == 'right':
        P = [dict(tn=3, ar=(1, 0), sw=sw(100)), dict(tn=3, hdx=-1, bdx=-1, dx=-1, ar=(-1, 0), al=(1, 0), sw=sw(96)),
             dict(tn=3, hdx=-2, bdx=-1, dx=-2, ar=(-3, 0), al=(2, 0), sw=sw(92)), dict(tn=3, hdx=-3, bdx=-2, dx=-2, ar=(-4, 0), al=(3, 0), sw=sw(90), face='shout'),
             dict(tn=3, hdx=-3, bdx=-2, dx=-3, ar=(-5, 0), al=(3, 0), sw=sw(90), face='shout'),
             dict(tn=2, dy=1, hdx=3, bdx=2, dx=3, ar=(4, 0), al=(-2, 0), bl=(-2, 0), br=(2, 0), sw=sw(88), face='shout'),
             dict(tn=2, dy=1, hdx=5, bdx=3, dx=5, ar=(8, 0), al=(-3, 0), bl=(-3, 0), br=(3, 0), sw=sw(88), face='shout'),
             dict(tn=2, dy=1, hdx=5, bdx=3, dx=5, ar=(8, 0), al=(-3, 0), bl=(-3, 0), br=(3, 0), sw=sw(88)),
             dict(tn=3, hdx=3, bdx=1, dx=3, ar=(4, 0), al=(-1, 0), sw=sw(92)), dict(tn=3, hdx=1, dx=1, ar=(1, 0), sw=sw(105))]
    else:
        P = [dict(tn=3, ar=(0, 0), sw=sw(170)), dict(tn=3, ar=(0, -1), al=(0, 1), sw=sw(172)), dict(tn=3, hdy=-1, ar=(0, -3), al=(0, 1), sw=sw(175)),
             dict(tn=3, hdy=-1, ar=(0, -5), al=(-1, 2), sw=sw(178), face='shout'), dict(tn=3, hdy=-1, ar=(0, -6), al=(-1, 2), sw=sw(178), face='shout'),
             dict(tn=2, dy=1, hdy=1, ar=(-1, -1), al=(0, 1), sw=sw(176), face='shout'), dict(tn=2, dy=2, hdy=2, ar=(-1, 4), al=(0, 0), bl=(-1, 0), br=(2, 0), sw=sw(172), face='shout'),
             dict(tn=2, dy=2, hdy=2, ar=(-1, 5), al=(0, 0), bl=(-1, 0), br=(2, 0), sw=sw(172)), dict(tn=3, dy=1, ar=(0, 2), sw=sw(170)), dict(tn=3, ar=(0, 0), sw=sw(168))]
    return P

def attack(view, ap, style):
    cls = ap.get('cls', 'warrior')
    if style == 'cast':
        base = C.anim(view, 'cast', cls, None, ap, dense=2)
        n = len(base); idx = [min(n - 1, round(i * (n - 1) / 19)) for i in range(20)]
        # conjurar: levanta, treme, solta no meio
        fr = [base[i][0] for i in idx]
        out = []
        for k, im in enumerate(fr):
            if 8 <= k <= 10: im = shake(im, 0, -1 if k % 2 else 0)
            if k == 11: im = flash(im, .35)
            out.append(im)
        return out
    if style == 'jab':
        base = C.anim(view, 'attack', cls, C.densify(_thrust(view), 2), ap, dense=2)
        fr = [b[0] for b in base]
        seq = [(0, {}), (1, {}), (2, {}), (3, {}), (4, {}), (5, {}), (6, {}), (7, {}), (8, {}), (8, {}), (9, {}), (10, {}),
               (12, {'shake': (1, 0)}), (13, {}), (13, {}), (14, {}), (15, {}), (16, {}), (17, {}), (18, {})]
    else:                                                       # smash: pancada pesada (mesmos quadros do golpe, outro tempo)
        base = C.anim(view, 'attack', cls, None, ap, dense=2)
        fr = [b[0] for b in base]
        seq = [(0, {}), (2, {}), (4, {}), (6, {}), (8, {}), (8, {'shake': (0, -1)}), (8, {}), (8, {'shake': (0, -1)}), (8, {}), (10, {}),
               (12, {'shake': (2, 1), 'dust': .12, 'flash': .25}), (12, {'shake': (-1, 1), 'dust': .3}), (12, {'dust': .5}), (14, {'dust': .7}),
               (14, {}), (14, {}), (16, {}), (17, {}), (18, {}), (18, {})]
    out = []
    for i, o in seq:
        im = fr[i]
        if 'dust' in o: im = dust(im, o['dust'], cx=W // 2 + 8, n=5)
        if 'flash' in o: im = flash(im, o['flash'])
        if 'shake' in o: im = shake(im, *o['shake'])
        out.append(im)
    return out

# ---------- dano ----------
def hurt(view, ap, style):
    base = C.anim(view, 'hurt', ap.get('cls', 'warrior'), None, ap, dense=2)
    fr = [b[0] for b in base]
    if style == 'stagger':       # leve: recuo grande, joga o corpo para tras e volta
        seq = [(0, {'shake': (-2, 0)}), (0, {'flash': .5, 'shake': (-4, -1)}), (1, {'shake': (-4, -1)}), (1, {'shake': (-3, 0)}), (2, {'shake': (-2, 0)}),
               (2, {'shake': (-1, 0)}), (3, {}), (4, {}), (6, {})]
    else:                        # stoic: pesado, mal se mexe: clarao + tremor de 1px
        seq = [(0, {}), (0, {'flash': .35, 'shake': (-1, 0)}), (0, {'shake': (-1, 0)}), (1, {}), (1, {}), (2, {}), (3, {}), (4, {}), (6, {})]
    out = []
    for i, o in seq:
        im = fr[min(i, len(fr) - 1)]
        if 'flash' in o: im = flash(im, o['flash'])
        if 'shake' in o: im = shake(im, *o['shake'])
        out.append(im)
    return out

# ---------- morte ----------
def _stand(view, ap):
    return C.anim(view, 'idle', ap.get('cls', 'warrior'), None, ap, dense=1)[0][0].convert('RGBA')
def _fit(im, margin=1):
    """reposiciona para caber no quadro (desloca a esquerda se passar da borda direita) sem cortar"""
    bb = im.getchannel('A').getbbox()
    if not bb: return im
    dx = 0
    if bb[2] > W - margin: dx = (W - margin) - bb[2]
    if bb[0] + dx < margin: dx = margin - bb[0]
    out = Image.new('RGBA', (W, H), (0, 0, 0, 0)); out.alpha_composite(im.crop(bb), (bb[0] + dx, bb[1])); return out
def _ground(im, lift=0):
    bb = im.getchannel('A').getbbox()
    if not bb: return im
    dy = (BASE + 1 - lift) - bb[3]
    out = Image.new('RGBA', (W, H), (0, 0, 0, 0)); out.alpha_composite(im.crop(bb), (bb[0], bb[1] + dy)); return out

def _hurtf(view, ap):
    return [d[0].convert('RGBA') for d in C.anim(view, 'hurt', ap.get('cls', 'warrior'), None, ap, dense=2)]

def topple(view, ap):
    """pesado: aguenta o golpe tremendo, e tomba de frente (rotacao RotSprite em torno dos pes)"""
    hf = _hurtf(view, ap); st = _stand(view, ap); piv = (W // 2, BASE + 1)
    out = [flash(shake(hf[0], -1, 0), .4), hf[1], hf[2], shake(st, 1, 0), shake(st, -1, 0), st]
    for a in [5, 12, 22, 36, 54, 72, 86, 90][:8]: out.append(_fit(R.rotate(st, a, piv)))
    low = _fit(R.rotate(st, 90, piv))
    out.append(dust(flash(shake(low, 0, 1), .3), .1, cx=W // 2 + 10, n=6))
    return out[:15]

def tumble(view, ap):
    """leve: e arremessado para tras, gira no ar e cai deitado de costas"""
    hf = _hurtf(view, ap); dth = C.anim(view, 'death', ap.get('cls', 'warrior'), None, ap, dense=2)
    base = [d[0].convert('RGBA') for d in dth]
    out = [flash(shake(hf[0], -1, 0), .4), hf[1]]
    src = hf[2]; cxp = (W // 2, BASE - 12)
    for a, h in [(-18, 2), (-42, 4), (-68, 5), (-96, 5), (-124, 4), (-150, 2)]:
        out.append(_ground(_fit(R.rotate(src, a, cxp)), lift=h))
    low = N2.lying(base[3], lift=0)
    out.append(dust(flash(shake(low, 0, 1), .35), .1)); out.append(dust(N2.lying(base[3], lift=3), .25)); out.append(dust(low, .45))
    out.append(dust(N2.lying(base[3], lift=1), .65)); out.append(dust(low, .85)); out.append(low); out.append(low)
    return out[:15]

def dissolve(view, ap):
    """vira cinza: pixels somem de cima para baixo e sobem como brasas; sobra um monte pequeno"""
    st = _stand(view, ap); a0 = _arr(st); rnd = np.random.RandomState(7)
    ys, xs = np.nonzero(a0[..., 3]); y0, y1 = ys.min(), ys.max()
    noise = rnd.rand(*a0.shape[:2]); yn = (np.arange(H)[:, None] - y0) / max(1, y1 - y0)
    out = [flash(shake(st, -1, 0), .4), flash(st, .25)]
    for t in range(13):
        p = t / 11.0
        a = a0.copy(); gone = (noise * .55 + (1 - yn) * .45) < p
        a[gone] = 0
        im = Image.fromarray(a)
        b = _arr(im)
        # brasas: pixels removidos sobem e esmaecem
        sel = np.argwhere(gone & (a0[..., 3] > 0))
        for (y, x) in sel[rnd.permutation(len(sel))[:int(70 * (1 - abs(p - .5) * 1.4))]]:
            yy = int(y - 3 - t * 1.8 + rnd.randint(-1, 2)); xx = int(x + rnd.randint(-2, 3))
            if 0 <= yy < H and 0 <= xx < W and b[yy, xx, 3] == 0:
                c = a0[y, x].copy(); c[:3] = np.clip(c[:3].astype(int) + 60, 0, 255).astype(np.uint8); c[3] = max(0, min(255, int(220 * (1 - min(1, p))))); b[yy, xx] = c
        if t >= 10:                                           # montinho de cinza no chao
            for i in range(10):
                xx = W // 2 + rnd.randint(-6, 7); yy = BASE - rnd.randint(0, 2)
                if b[yy, xx, 3] == 0: b[yy, xx] = (150, 140, 150, 220)
        out.append(Image.fromarray(b))
    return out[:15]

def crumble(view, ap):
    """esqueleto/pedra: a cabeca cai e rola, o corpo desmonta em ossos que formam uma pilha"""
    st = _stand(view, ap); a0 = _arr(st); rnd = np.random.RandomState(11)
    ys, xs = np.nonzero(a0[..., 3]); y0, y1 = ys.min(), ys.max(); bh = y1 - y0
    yh = y0 + int(bh * .52)                                           # cabeca = metade de cima
    head = np.zeros_like(a0); head[:yh + 1] = a0[:yh + 1]
    body = [(y, x) for y, x in zip(*np.nonzero(a0[..., 3])) if y > yh]
    cols = {}
    parts = []
    for (y, x) in body:
        delay = 1.5 + (y1 - y) / max(1, bh) * 3.2 + rnd.rand() * 2.0
        xt = int(np.clip(x + rnd.normal(0, 4.0), 8, W - 9)); parts.append([y, x, a0[y, x].copy(), delay, xt])
    # pilha: altura por coluna
    pile = {}
    for pt in sorted(parts, key=lambda q: q[3]):
        h = pile.get(pt[4], 0); pile[pt[4]] = h + 1; pt.append(BASE - h // 2)         # y de pouso
    hb = Image.fromarray(head).crop(Image.fromarray(head).getbbox()); hw, hh = hb.size
    frames = [flash(shake(st, -1, 0), .4), shake(st, 1, 0)]
    for t in range(2, 15):
        b = np.zeros_like(a0)
        # cabeca: cai com gravidade, quica uma vez, rola para a direita
        tt = max(0, t - 3.0); ground_y = BASE - hh * .35
        hy = yh - hh + 1 + .5 * 1.1 * tt * tt
        if hy > ground_y: hy = ground_y - (abs(math.sin((t - 7) * .9)) * 3 if t < 11 else 0)
        hx = W // 2 - hw // 2 + int(min(10, tt * 1.6)); ang = min(78, tt * 11)
        hs = Image.new('RGBA', (W, H), (0, 0, 0, 0)); hs.alpha_composite(hb, (max(0, hx), max(0, int(hy))))
        if ang > 3: hs = R.rotate(hs, ang, (hx + hw / 2, hy + hh / 2))
        hsa = _arr(hs); m = hsa[..., 3] > 0; b[m] = hsa[m]
        for y, x, col, d, xt, yl in parts:
            if t < d: yy, xx = y, x
            else:
                s = t - d; yy = min(yl, y + .5 * 1.2 * s * s); xx = x + (xt - x) * min(1, s / 3.0)
            yy, xx = int(yy), int(xx)
            if 0 <= yy < H and 0 <= xx < W: b[yy, xx] = col
        frames.append(Image.fromarray(b))
    return frames[:15]

def build(view, kind, appearance, dense=2):
    st = (appearance or {}).get('anim') or {}
    ap = dict(appearance)
    if kind == 'attack' and st.get('attack') in ('smash', 'jab', 'cast'):
        fr = attack(view, ap, st['attack'])
    elif kind == 'hurt' and st.get('hurt') in ('stagger', 'stoic'):
        fr = hurt(view, ap, st['hurt'])
    elif kind == 'death' and st.get('death') in ('topple', 'tumble', 'dissolve', 'crumble'):
        fr = {'topple': topple, 'tumble': tumble, 'dissolve': dissolve, 'crumble': crumble}[st['death']](view, ap)
    else:
        return N2.build(view, kind, appearance, dense)
    base = C.anim(view, 'attack' if kind == 'attack' else 'hurt' if kind == 'hurt' else 'death', ap.get('cls', 'warrior'), None, ap, dense=2)
    return [(im, base[min(i, len(base) - 1)][1], base[min(i, len(base) - 1)][2]) for i, im in enumerate(fr)]
