#!/usr/bin/env python3
"""COLOSSO DAS COLINAS (caçada): bicho tão grande que só aparecem as PERNAS (somem em nuvem no alto da tela) e, na fase final, a CABEÇA.
Gera dois atlas (mesmo renderizador do fauna.py: uma massa só, luz de cima-esquerda, contorno seletivo):
  cx_perna_atlas  — perna gigante (frente): idle 12, walk 16, stomp 20 (ergue, bate, poeira), sweep 16 (chute lateral), hurt 9, death 20 (joelho cede e desaba)
  cx_ccabeca_atlas — cabeça (frente): idle 12, descend 16, bite 16, roar 16, spit 16, hurt 9, death 24
Uso: python3 colosso.py  -> mmo/assets/chars/   |  python3 colosso.py sheet out.png"""
import math, os, sys, json
import numpy as np
from PIL import Image
import fauna as FA

R, hx = FA.R, FA.hx
PAL = dict(body=R('#4a3a30', '#8a6e56', '#c4a47c'), fur=R('#33281f', '#6a5240', '#a88a64'), stone=R('#3c3c46', '#6e6e7c', '#a8a8b8'), moss=R('#24401c', '#4c7c30', '#8cc050'),
           hoof=R('#1c1620', '#3a3040', '#5a4c64'), horn=R('#6c5a3a', '#c8b078', '#f4e8c4'), far=R('#2a2018', '#54402e', '#806040'), tusk=R('#8a7a5a', '#e0d4ac', '#fff8dc'),
           skin=R('#3a2c28', '#6e5042', '#a8806c'))
FLAT = {'eye': hx('#ffcf4a'), 'eye2': hx('#fff6c0'), 'mouth': hx('#2a0c10'), 'tongue': hx('#a0384c'), 'rune': hx('#ffcf4a')}
MIST = (206, 214, 226)


def mist(img, top, bot, W, H):
    """a perna some em nuvem no alto: alfa sobe do topo e entra um pouco de névoa clara (dither ordenado)"""
    px = img.load(); B = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]
    for y in range(top, bot):
        k = (y - top) / max(1, bot - top)
        for x in range(W):
            r, g, b, a = px[x, y]
            if a == 0: continue
            if B[y % 4][x % 4] / 16.0 > k * 1.15: px[x, y] = (0, 0, 0, 0)
            elif k < .5 and B[(y + 1) % 4][(x + 2) % 4] / 16.0 > k * 2: px[x, y] = MIST + (255,)
    for y in range(0, top):
        for x in range(W): px[x, y] = (0, 0, 0, 0)
    return img


# ------------------------------------------------------------------ PERNA
LW, LH, LB = 150, 160, 154


def leg(P, view='d'):
    FA.W, FA.H = LW, LH
    c = FA.Cv(); c.contact = False
    cx = LW // 2 + P.get('dx', 0); up = P.get('up', 0); sq = P.get('sq', 0); bend = P.get('bend', 0); sw = P.get('sway', 0)
    ty = 8 + P.get('drop', 0)
    fy = LB - up
    fx = cx + P.get('foot', 0)
    if view == 's':      # PERFIL (vira para a direita; a esquerda e' espelho): coxa estreita, joelho para a frente, canela inclinada, casco com dedos para a frente
        top = (cx + sw * .4, ty + 34)
        knee = (cx + 9 + bend * 16 + sw * .5, LB - 62 - up * .5 + P.get('kn', 0))
        c.ell(top[0], top[1] + 6, 21, 22, 'fur'); c.cap(top[0], top[1] + 10, knee[0], knee[1], 20, 15, 'fur')
        c.cap(knee[0], knee[1], fx + 2, fy - 16, 12, 8.5 + sq, 'body')
        c.ell(knee[0], knee[1], 16, 15, 'fur')
        for k in range(5):                                                   # pelos caindo atras da coxa
            yy = top[1] + 6 + k * 11; xx = top[0] - 20 + k * .8
            c.cap(xx, yy, xx - 6, yy + 9 + (k % 2) * 3, 3.4, 1, 'fur')
        for i in range(4): c.cap(knee[0] - 8 + i * 5, knee[1] + 10, knee[0] - 10 + i * 5 + sw * .2, knee[1] + 22 + (i % 2) * 5, 2.6, 1, 'fur')
        c.ell(knee[0] - 5, knee[1] - 5, 7, 5, 'stone'); c.ell(top[0] + 6, top[1] + 14, 9, 7, 'moss')
        c.ell(fx + 6, fy - 9, 19 + sq * 3, 9 - sq * 2, 'hoof')
        for s_ in (0, 1): c.cap(fx + 12 + s_ * 6, fy - 8 + s_ * 2, fx + 22 + s_ * 6, fy - 2 + sq, 5.6, 4.4, 'hoof')
        c.cap(fx + 24, fy - 5, fx + 31, fy - 1, 2.6, 1.4, 'horn')
        rg = P.get('rune', 0)
        for i, (rx, ry) in enumerate(((2, 46), (-4, 58))): c.dot(cx + rx + sw * .3, ty + ry, FLAT['rune'] if (i + rg) % 3 else hx('#fff0a0'))
    else:                # FRENTE ('d') e COSTAS ('u')
        back = (view == 'u'); bm = 'far' if back else 'fur'
        knee = (cx + sw * .3 + bend * 10, LB - 62 - up * .5 + P.get('kn', 0))
        top = (cx + sw, ty + 34)
        c.ell(top[0], top[1] + 6, 29, 22, bm); c.cap(top[0], top[1] + 10, knee[0], knee[1], 27, 19, bm)
        c.cap(knee[0], knee[1], fx, fy - 18, 17, 11.5 + sq * 1.5, 'body')
        c.ell(knee[0], knee[1], 21, 17, bm)
        for sg in (-1, 1):
            for k in range(5):
                yy = top[1] + 8 + k * 10; xx = top[0] + sg * (27 - k * 1.2) + (knee[0] - top[0]) * k / 7
                c.cap(xx, yy, xx + sg * 5, yy + 8 + (k % 2) * 3, 3.2, 1, bm)
        c.ell(knee[0] - 8, knee[1] - 4, 8, 6, 'stone'); c.ell(knee[0] + 9, knee[1] + 7, 5, 4, 'moss')
        c.ell(top[0] + 14, top[1] + 12, 12, 8, 'moss'); c.ell(top[0] - 18, top[1] + 28, 8, 5, 'stone')
        c.ell(fx, fy - 10, 25 + sq * 4, 10 - sq * 2, 'hoof')
        if back:                                                             # de costas: calcanhar largo e vinco atras do joelho
            c.ell(fx, fy - 8, 17, 8, 'hoof'); c.cap(knee[0] - 12, knee[1] + 4, knee[0] + 12, knee[1] + 4, 3, 3, 'far')
        else:
            for s_ in (-1, 0, 1): c.cap(fx + s_ * 15, fy - 7, fx + s_ * 18, fy - 1 + sq, 7, 5.2, 'hoof')
            for s_ in (-1, 1): c.cap(fx + s_ * 19, fy - 10, fx + s_ * 22, fy - 2, 3, 1.6, 'horn')
        for i, ox in enumerate((-18, -9, 0, 9, 18)): c.cap(knee[0] + ox, knee[1] + 12, knee[0] + ox + sw * .2, knee[1] + 24 + (i % 2) * 5, 2.8, 1, bm)
        if not back:
            rg = P.get('rune', 0)
            for i, (rx, ry) in enumerate(((-10, 46), (9, 52), (-2, 60), (14, 38))):
                c.dot(cx + rx + sw * .3, ty + ry, FLAT['rune'] if (i + rg) % 3 else hx('#fff0a0'))
    img = c.render(PAL, FLAT)
    if P.get('crack'):
        px = img.load()
        for k in range(P['crack']):
            x = int(cx - 8 + (k * 7) % 17); y = int(ty + 90 + (k * 11) % 40)
            for j in range(6):
                xx, yy = x + j % 2, y + j
                if 0 <= xx < LW and 0 <= yy < LH and px[xx, yy][3]: px[xx, yy] = (20, 12, 10, 255)
    # a coxa continua para CIMA sem fim: acima da linha ROW repete-se a linha da coxa com textura periodica de 12 quadros (o jogo empilha essa faixa ate o topo da tela)
    px = img.load(); ROW = 44
    for x in range(LW):
        r, g, b, a = px[x, ROW]
        for y in range(0, ROW):
            if a == 0: px[x, y] = (0, 0, 0, 0); continue
            h = (x * 7 + (y % 12) * 13 + (x // 5) * 11) % 9
            k = 1.0 + (h - 4) * .02 + .05 * math.sin(x * .9) - (.1 if y % 12 in (0, 1) else 0)
            px[x, y] = (max(0, min(255, int(r * k))), max(0, min(255, int(g * k))), max(0, min(255, int(b * k))), 255)
    return img


def ease(t): return t * t * (3 - 2 * t)


def seq_leg(kind):
    o = []
    if kind == 'idle':
        for i in range(12): s = math.sin(i / 12 * 6.283); o.append(dict(sway=s * 1.5, rune=i // 2, sq=0))
    elif kind == 'walk':       # passo pesado: ergue, avança, assenta (o jogo toca em loop)
        for i in range(16):
            u = i / 16; s = math.sin(u * 6.283); lift = max(0, s)
            o.append(dict(up=lift * 14, foot=math.cos(u * 6.283) * -5, sway=s * 2, sq=1 if (i in (8, 9)) else 0, rune=i // 2, dx=0))
    elif kind == 'stomp':      # ergue bem alto (antecipa), bate (impacto no quadro 11), segura e volta
        for i in range(20):
            if i < 9: t = ease(i / 8); o.append(dict(up=44 * t, bend=-.6 * t, sway=-2 * t, kn=-8 * t, rune=i))
            elif i < 11: t = (i - 9) / 1.5; o.append(dict(up=44 * (1 - min(1, t)), bend=-.6 * (1 - min(1, t)), kn=-8 * (1 - min(1, t)), sq=min(1, t), rune=i))
            elif i < 14: o.append(dict(up=0, sq=2, drop=2, rune=i, crack=6 + i))
            else: t = ease((i - 14) / 5); o.append(dict(up=0, sq=2 * (1 - t), drop=2 * (1 - t), rune=i, crack=int(10 * (1 - t))))
    elif kind == 'sweep':      # chute lateral: recolhe o joelho, estica para o lado e volta
        for i in range(16):
            if i < 6: t = ease(i / 5); o.append(dict(up=16 * t, foot=-10 * t, bend=.5 * t, rune=i))
            elif i < 9: t = (i - 6) / 2; o.append(dict(up=16 - 6 * t, foot=-10 + 34 * t, bend=.5 - .3 * t, sway=4 * t, rune=i))
            elif i < 12: o.append(dict(up=8, foot=24, sway=4, rune=i))
            else: t = ease((i - 12) / 3); o.append(dict(up=8 * (1 - t), foot=24 * (1 - t), sway=4 * (1 - t), rune=i))
    elif kind == 'hurt':
        for i in range(9):
            t = math.sin(min(1, i / 6) * math.pi); o.append(dict(sway=-4 * t, sq=1 if 1 <= i <= 3 else 0, up=3 * t, dx=int(-2 * t), rune=i))
    elif kind == 'death':      # joelho cede, a perna tomba para o lado e se desfaz no chão
        for i in range(20):
            if i < 6: t = ease(i / 5); o.append(dict(kn=14 * t, bend=.7 * t, sway=-3 * t, sq=1, rune=0))
            else: t = ease(min(1, (i - 6) / 12)); o.append(dict(kn=14 + 14 * t, bend=.7 + .7 * t, sway=-3 - 8 * t, drop=int(60 * t), dx=int(-6 * t), sq=2, crack=12))
    return [[leg(P, v) for P in o] for v in ('d', 'u', 's')]


# ------------------------------------------------------------------ CABEÇA
HW, HH, HB = 150, 140, 136


def head(P):
    FA.W, FA.H = HW, HH
    c = FA.Cv(); c.contact = False
    cx = HW // 2 + P.get('dx', 0); y0 = 46 + P.get('dy', 0); jaw = P.get('jaw', 0); sh = P.get('shake', 0)
    # chifres curvos
    for sg in (-1, 1):
        c.cap(cx + sg * 30, y0 - 6, cx + sg * 52, y0 - 24, 7, 4.5, 'horn'); c.cap(cx + sg * 52, y0 - 24, cx + sg * 58 + sg * 4, y0 - 52, 4.5, 1.2, 'horn')
        c.cap(cx + sg * 38, y0 + 6, cx + sg * 60, y0 + 2, 5, 3, 'horn'); c.cap(cx + sg * 60, y0 + 2, cx + sg * 68, y0 - 12, 3, 1, 'horn')
    c.ell(cx, y0 + 12, 44, 38, 'fur')                                # cranio/juba
    c.ell(cx, y0 + 18, 36, 32, 'body')                               # rosto
    for sg in (-1, 1): c.ell(cx + sg * 20, y0 + 4, 13, 9, 'moss') if sg > 0 else c.ell(cx + sg * 20, y0 + 2, 11, 7, 'stone')
    c.ell(cx, y0 + 36, 22, 12, 'skin')                               # focinho
    c.ell(cx, y0 + 46 + jaw * 9, 25, 11 + jaw * 3, 'body')           # mandibula
    for sg in (-1, 1): c.cap(cx + sg * 14, y0 + 44 + jaw * 8, cx + sg * 17, y0 + 30 - jaw * 2, 3.2, 1.6, 'tusk')   # presas
    for sg in (-1, 1): c.cap(cx + sg * 34, y0 + 28, cx + sg * 40, y0 + 52, 6, 3, 'fur')                              # barbas laterais
    for i in range(5): c.cap(cx - 20 + i * 10, y0 + 56 + jaw * 8, cx - 22 + i * 11, y0 + 70 + jaw * 8 + (i % 2) * 5, 3, 1, 'fur')
    img = c.render(PAL, FLAT); _px = img.load()
    class _S:
        def __setitem__(s_, k, v):
            if 0 <= k[0] < HW and 0 <= k[1] < HH: _px[k] = v
    px = _S()
    ey = y0 + 20
    for sg in (-1, 1):
        for dx in (-3, -2, -1, 0, 1, 2, 3):
            for dy in (-1, 0, 1):
                if abs(dx) < 3 or dy == 0: px[cx + sg * 18 + dx, ey + dy] = FLAT['eye'] + (255,)
        px[cx + sg * 18, ey] = FLAT['eye2'] + (255,)
        for dx in range(-5, 6): px[cx + sg * 18 + dx, ey - 3 - (1 if abs(dx) > 3 else 0)] = (20, 12, 8, 255)          # sobrancelha
    for dx in (-4, 4): px[cx + dx, y0 + 38] = (10, 6, 6, 255)                                                           # narinas
    my = y0 + 44 + int(jaw * 4)
    if jaw > .15:
        for xx in range(-14, 15):
            for yy in range(0, int(2 + jaw * 8)):
                px[cx + xx, my + yy] = FLAT['mouth'] + (255,)
        for xx in range(-8, 9): px[cx + xx, my + int(1 + jaw * 5)] = FLAT['tongue'] + (255,)
    else:
        for xx in range(-14, 15): px[cx + xx, my] = (12, 8, 8, 255)
    return img


def seq_head(kind):
    o = []
    if kind == 'idle':
        for i in range(12): s = math.sin(i / 12 * 6.283); o.append(dict(dy=int(s * 2), jaw=.15 + .1 * s))
    elif kind == 'descend':    # vem de cima da tela
        for i in range(16): t = ease(i / 15); o.append(dict(dy=int(-90 * (1 - t) - 10 * math.sin(t * 3.14) * 0), jaw=.2 * (1 - t), shake=0))
    elif kind == 'bite':       # abre muito, abaixa, fecha com estalo
        for i in range(16):
            if i < 6: t = ease(i / 5); o.append(dict(dy=int(-14 * t), jaw=1.2 * t))
            elif i < 9: t = (i - 6) / 2; o.append(dict(dy=int(-14 + 36 * t), jaw=1.2 - 1.2 * min(1, t * 1.2)))
            elif i < 12: o.append(dict(dy=22, jaw=0, dx=(i % 2) * 2 - 1))
            else: t = ease((i - 12) / 3); o.append(dict(dy=int(22 * (1 - t)), jaw=.05))
    elif kind == 'roar':
        for i in range(16):
            if i < 4: t = ease(i / 3); o.append(dict(dy=int(-8 * t), jaw=1.2 * t))
            elif i < 12: o.append(dict(dy=-8, jaw=1.3, dx=(i % 2) * 2 - 1))
            else: t = ease((i - 12) / 3); o.append(dict(dy=int(-8 * (1 - t)), jaw=1.3 * (1 - t)))
    elif kind == 'spit':       # recua, depois cospe
        for i in range(16):
            if i < 7: t = ease(i / 6); o.append(dict(dy=int(-10 * t), jaw=.4 * t))
            elif i < 10: o.append(dict(dy=int(-10 + 14 * (i - 7) / 2), jaw=1.1))
            else: t = ease((i - 10) / 5); o.append(dict(dy=int(4 * (1 - t)), jaw=.5 * (1 - t)))
    elif kind == 'hurt':
        for i in range(9): t = math.sin(min(1, i / 6) * math.pi); o.append(dict(dy=int(6 * t), jaw=.7 * t, dx=int(-3 * t)))
    elif kind == 'death':
        for i in range(24):
            t = ease(min(1, i / 16)); o.append(dict(dy=int(70 * t), jaw=1.3 * (1 - t * .7), dx=int(math.sin(i * 1.6) * 3 * (1 - t))))
    return [head(P) for P in o]


def pack(imgs_by_kind, W, H, name, out_dir, base, cut_to=None):
    imgs, anims = [], {}
    for kind, fr in imgs_by_kind.items():
        if fr and isinstance(fr[0], list):      # um conjunto de quadros por vista (d, u, s)
            for v, f3 in zip(('d', 'u', 's'), fr):
                anims[f'{kind}_{v}'] = list(range(len(imgs), len(imgs) + len(f3))); imgs += f3
            continue
        idx = list(range(len(imgs), len(imgs) + len(fr))); imgs += fr
        for v in ('d', 'u', 's'): anims[f'{kind}_{v}'] = idx
    bb = None
    for im in imgs:
        b = im.getbbox()
        if b: bb = b if bb is None else (min(bb[0], b[0]), min(bb[1], b[1]), max(bb[2], b[2]), max(bb[3], b[3]))
    x0, y0, x1, y1 = max(0, bb[0] - 1), max(0, bb[1] - 1), min(W, bb[2] + 1), min(H, bb[3] + 1)
    if cut_to: y1 = min(y1, cut_to)
    w, h = x1 - x0, y1 - y0; cols = max(1, 3900 // w); rows = (len(imgs) + cols - 1) // cols
    A = Image.new('RGBA', (cols * w, rows * h), (0, 0, 0, 0))
    for i, im in enumerate(imgs): A.alpha_composite(im.crop((x0, y0, x1, y1)), ((i % cols) * w, (i // cols) * h))
    A.save(os.path.join(out_dir, f'cx_{name}_atlas.png'), optimize=True)
    json.dump(dict(w=w, h=h, ax=(W // 2 - x0), ay=(base + 1 - y0), cols=cols, anims=anims), open(os.path.join(out_dir, f'cx_{name}_atlas.json'), 'w'))
    print(name, len(imgs), 'quadros', A.size, os.path.getsize(os.path.join(out_dir, f'cx_{name}_atlas.png')) // 1024, 'KB')


def export(out):
    pack({k: seq_leg(k) for k in ('idle', 'walk', 'stomp', 'sweep', 'hurt', 'death')}, LW, LH, 'perna', out, LB)
    anim = {'attack': 'stomp', 'cast': 'sweep'}
    # nomes que o motor usa: walk/attack/cast ja existem como stomp/sweep
    for nm in ('perna',):
        p = os.path.join(out, f'cx_{nm}_atlas.json'); j = json.load(open(p))
        for v in ('d', 'u', 's'):
            j['anims'][f'attack_{v}'] = j['anims'][f'stomp_{v}']; j['anims'][f'cast_{v}'] = j['anims'][f'sweep_{v}']
        json.dump(j, open(p, 'w'))
    pack({k: seq_head(k) for k in ('idle', 'descend', 'bite', 'roar', 'spit', 'hurt', 'death')}, HW, HH, 'ccabeca', out, HB)
    p = os.path.join(out, 'cx_ccabeca_atlas.json'); j = json.load(open(p))
    for v in ('d', 'u', 's'):
        j['anims'][f'walk_{v}'] = j['anims'][f'idle_{v}']; j['anims'][f'attack_{v}'] = j['anims'][f'bite_{v}']; j['anims'][f'cast_{v}'] = j['anims'][f'roar_{v}']
    json.dump(j, open(p, 'w'))


def sheet(path):
    rows = [(LW, LH, seq_leg(k)[2]) for k in ('idle', 'walk', 'stomp', 'sweep', 'hurt', 'death')] + [(HW, HH, seq_head(k)) for k in ('idle', 'descend', 'bite', 'roar', 'spit', 'hurt', 'death')]
    cols = max(len(r[2]) for r in rows); Hs = max(r[1] for r in rows); Ws = max(r[0] for r in rows)
    S = Image.new('RGBA', (cols * Ws, len(rows) * Hs), (92, 120, 84, 255))
    for j, (w, h, fr) in enumerate(rows):
        for i, im in enumerate(fr): S.alpha_composite(im, (i * Ws, j * Hs))
    S.save(path); print(path, S.size)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'sheet': sheet(sys.argv[2])
    else: export(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..', 'mmo', 'assets', 'chars')))
