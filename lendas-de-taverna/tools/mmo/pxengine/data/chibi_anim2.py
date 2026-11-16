"""Animacao v2 do chibi: monta a sequencia a partir dos quadros do motor (redesenhados por pose) com TEMPO ASSIMETRICO, pausas (holds),
clarao e tremor no impacto, e queda de 90 graus EXATA (rotacao de pixel sem serrilhado) + poeira por codigo.
Regras (skill pixel-art-studio/animation.md): antecipacao lenta, golpe de 1 quadro, impacto parado, recuperacao; hold nos contatos."""
import math, numpy as np
from PIL import Image
import chibi as C
W, H, BASE = C.W, C.H, C.BASE

def _arr(im): return np.array(im.convert('RGBA'))
def flash(im, k=.5):
    a = _arr(im); m = a[..., 3] > 0; a[m, :3] = (a[m, :3] + (255 - a[m, :3]) * k).astype(np.uint8); return Image.fromarray(a)
def shake(im, dx=0, dy=0):
    a = np.roll(_arr(im), (dy, dx), (0, 1)); return Image.fromarray(a)
def lying(im, lift=0, feet_x=46):
    """deita o sprite de costas: rotacao de 90 graus exata em canvas quadrado; pes no chao"""
    S = max(W, H)
    sq = Image.new('RGBA', (S, S), (0, 0, 0, 0)); sq.alpha_composite(im, (0, 0))
    r = Image.fromarray(np.rot90(_arr(sq), 1))                              # anti-horario: cabeca vai para a esquerda
    bb = r.getbbox()
    out = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    dx = feet_x - bb[2]; dy = (BASE + 1 - lift) - bb[3]
    out.alpha_composite(r.crop(bb), (bb[0] + dx, bb[1] + dy)); return out
def dust(im, t, cx=44, n=6):
    a = _arr(im)
    for i in range(n):
        ang = math.pi * (.1 + .8 * i / (n - 1)); d = 3 + t * 14; r = 1 + int(t * 2.2)
        x = int(cx + math.cos(ang) * d * (1 if i % 2 else -1.4)); y = int(BASE - math.sin(ang) * d * .5)
        for yy in range(-r, r + 1):
            for xx in range(-r, r + 1):
                if xx * xx + yy * yy <= r * r and ((xx + yy + i) % 2 == 0 or t < .35):
                    px, py = x + xx, y + yy
                    if 0 <= px < W and 0 <= py < H and a[py, px, 3] == 0: a[py, px] = (200, 186, 160, int(230 * (1 - t * .7)))
    return Image.fromarray(a)
def _sword_only(view, appearance, pose):
    """so a espada (deitada, apontando para a direita): diferenca entre o quadro com e sem arma"""
    ap0 = dict(appearance, noweapon=1)
    a = C.anim(view, 'death', appearance.get('cls', 'warrior'), [pose], appearance, dense=1)[0][0]
    b = C.anim(view, 'death', appearance.get('cls', 'warrior'), [pose], ap0, dense=1)[0][0]
    A, B = _arr(a), _arr(b); m = (A != B).any(2) & (A[..., 3] > 0)
    out = np.zeros_like(A); out[m] = A[m]; return Image.fromarray(out)
def _pose_img(view, appearance, pose):
    return C.anim(view, 'death', appearance.get('cls', 'warrior'), [pose], appearance, dense=1)[0][0]
def build(view, kind, appearance, dense=2):
    base = C.anim(view, kind, appearance.get('cls', 'warrior'), None, appearance, dense=2)
    fr = [f[0] for f in base]; tips = [f[1] for f in base]; bh = [f[2] for f in base]
    if kind == 'attack':       # 19 quadros densos: indice = 2*pose
        seq = [(0, {}), (1, {}), (2, {}), (3, {}), (4, {}), (5, {}), (6, {}), (7, {}), (8, {}), (8, {}), (8, {}),          # antecipacao lenta + pausa no pico
               (10, {}),                                                                                                  # GOLPE: 1 quadro (pula 9)
               (12, {'shake': (1, 0)}), (14, {'shake': (1, 0)}), (14, {}), (14, {}),                                      # impacto parado + tremor
               (16, {}), (17, {}), (18, {}), (18, {})]                                                                    # recuperacao
    elif kind == 'hurt':       # 7 quadros densos
        seq = [(0, {'flash': .4, 'shake': (-1, 0)}), (1, {'shake': (-1, 0)}), (2, {}), (2, {}), (3, {}), (4, {}), (6, {}), (6, {})]
    elif kind == 'death':      # 11 quadros densos -> queda com 90 graus exatos
        seq = [(0, {'flash': .4, 'shake': (-1, 0)}), (1, {}), (2, {}), (3, {}), (4, {}), (5, {}), (6, {}),
               (7, {'lie': 6, 'rot': 1}),                                                                                   # no ar, deitando
               (10, {'lie': 0, 'flash': .35, 'shake': (0, 1), 'dust': .05}),                                                # impacto
               (10, {'lie': 3, 'dust': .25}), (10, {'lie': 0, 'dust': .45}), (10, {'lie': 1, 'dust': .65}), (10, {'lie': 0, 'dust': .85}),
               (10, {'lie': 0}), (10, {'lie': 0})]
    else:
        seq = [(i, {}) for i in range(len(fr))]
    out = []
    if kind == 'death':      # poses de queda: espada para BAIXO (apos 90 graus ela fica deitada no chao, nunca espetada para cima)
        ps = C.extra_poses('death', view); swd = lambda a: dict(ang=a, len=12, side='r') if view != 'right' else dict(ang=a, len=12)
        air = _pose_img(view, appearance, dict(ps[3], sw=swd(165), face='hurt'))
        down = _pose_img(view, appearance | dict(noweapon=1), dict(ps[-1], face='dead'))
        sword = _sword_only(view, appearance, dict(ps[-1], sw=swd(90 if view == 'right' else 100), face='dead'))
    for i, o in seq:
        im = fr[i]
        if 'lie' in o:
            im = lying(air if o.get('rot') else down, lift=o['lie'])
            if not o.get('rot'):
                sb = sword.getbbox()
                if sb:
                    sc = sword.crop(sb); gx = 52; gy = BASE - sc.height + 1 - o['lie']
                    im.alpha_composite(sc, (gx, max(0, gy)))
        if 'dust' in o: im = dust(im, o['dust'])
        if 'flash' in o: im = flash(im, o['flash'])
        if 'shake' in o: im = shake(im, *o['shake'])
        out.append((im, tips[i], bh[i]))
    return out
