#!/usr/bin/env python3
"""CINZAMURO (cidade-fortaleza da Região 2) — gera mmo/assets/cinzamuro.json, cinzamuro_ground.png e atlas_cinza.png/json.
Cidadela de montanha em terraços (rocha cinza). TODAS as peças (muralhas, torres, portões, casas, lojas, rochas, pinheiros, escadas) são desenhadas por código. Rodar: /usr/bin/python3 tools/mmo/build_cinzamuro.py (de lendas-de-taverna/)."""
import json, random, math, colorsys, os
import numpy as np
from PIL import Image, ImageDraw
A = 'mmo/assets/'
R = random.Random(7)
# ------------------------------------------------------------------ paleta de PEDRA CINZA (montanha)
L1, L2, L3, L4, L5 = (176, 182, 196), (148, 155, 172), (122, 130, 148), (92, 99, 118), (62, 68, 86)
MORT = (74, 80, 98); OUT = (40, 44, 58)
def jit(c, k=6):
    d = R.randint(-k, k); return tuple(max(0, min(255, v + d)) for v in c)
def block_wall(w, h, bw=32, bh=16, seed=0):
    """face de muralha de blocos: luz em cima/esquerda, argamassa, pixels de ruído"""
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im); rr = random.Random(seed)
    for r in range(0, h, bh):
        off = (bw // 2) if (r // bh) % 2 else 0
        for c in range(-off, w, bw):
            base = rr.choice([L2, L2, L3, L3, L1])
            x0, x1 = max(0, c), min(w, c + bw); y1 = min(h, r + bh)
            if x1 <= x0: continue
            d.rectangle([x0, r, x1 - 1, y1 - 1], fill=base)
            d.line([(x0, r), (x1 - 1, r)], fill=L1)
            d.line([(x0, r), (x0, y1 - 1)], fill=jit(L1, 3))
            d.line([(x0, y1 - 1), (x1 - 1, y1 - 1)], fill=MORT)
            d.line([(x1 - 1, r), (x1 - 1, y1 - 1)], fill=MORT)
            for _ in range(5):
                px, py = rr.randint(x0, x1 - 1), rr.randint(r, y1 - 1)
                im.putpixel((px, py), jit(L3, 14) + (255,))
    return im
def crenel(w, mh=22, mw=20, gap=12):
    im = Image.new('RGBA', (w, mh), (0, 0, 0, 0)); d = ImageDraw.Draw(im); x = gap // 2
    while x < w:
        x1 = min(w, x + mw)
        d.rectangle([x, 0, x1 - 1, mh - 1], fill=L2); d.line([(x, 0), (x1 - 1, 0)], fill=L1); d.line([(x, 0), (x, mh - 1)], fill=L1)
        d.line([(x1 - 1, 0), (x1 - 1, mh - 1)], fill=L4); x += mw + gap
    return im
def outline(im, col=OUT):
    a = np.array(im); m = a[..., 3] > 0; o = np.zeros_like(m)
    o[1:] |= m[:-1]; o[:-1] |= m[1:]; o[:, 1:] |= m[:, :-1]; o[:, :-1] |= m[:, 1:]; o &= ~m
    a[o] = list(col) + [255]; return Image.fromarray(a)
def shade_side(im, right=14, bottom=10):
    """sombra de baixo/direita (volume)"""
    a = np.array(im).astype(int); h, w = a.shape[:2]
    for x in range(w - right, w):
        t = (x - (w - right)) / right
        a[:, x, :3] = (a[:, x, :3] * (1 - .28 * t)).astype(int)
    for y in range(h - bottom, h):
        t = (y - (h - bottom)) / bottom
        a[y, :, :3] = (a[y, :, :3] * (1 - .25 * t)).astype(int)
    return Image.fromarray(np.clip(a, 0, 255).astype('uint8'))
def paste(dst, src, x, y): dst.alpha_composite(src, (x, y))
# ------------------------------------------------------------------ peças
def wall_seg():
    W, H = 128, 150
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); paste(im, crenel(W), 0, 0)
    face = block_wall(W, H - 22, seed=3); paste(im, face, 0, 22)
    d = ImageDraw.Draw(im); d.rectangle([0, 22, W - 1, 28], fill=L1); d.line([(0, 28), (W - 1, 28)], fill=L3)        # beiral
    for x in (30, 98):                                                                                                  # seteiras
        d.rectangle([x, 62, x + 5, 82], fill=(34, 24, 22)); d.line([(x, 62), (x + 5, 62)], fill=L5)
    return outline(shade_side(im, 0, 12)), (W // 2, H - 1)
def wall_side():
    W, H = 60, 150
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); paste(im, crenel(W, 22, 22, 16), 0, 0)
    paste(im, block_wall(W, H - 22, bw=30, seed=11), 0, 22)
    d = ImageDraw.Draw(im); d.rectangle([0, 22, W - 1, 27], fill=L1)
    return outline(shade_side(im, 14, 8)), (W // 2, H - 1)
def tower():
    W, H = 124, 250
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); body = block_wall(W - 16, H - 40, bw=36, seed=5); paste(im, body, 8, 40)
    d = ImageDraw.Draw(im); d.rectangle([0, 28, W - 1, 46], fill=L2); d.line([(0, 28), (W - 1, 28)], fill=L1); d.line([(0, 46), (W - 1, 46)], fill=MORT)
    paste(im, crenel(W, 28, 22, 12), 0, 2)
    for (x, y) in ((50, 90), (50, 150)):
        d.rectangle([x, y, x + 8, y + 26], fill=(34, 24, 22)); d.line([(x, y), (x + 8, y)], fill=L5)
    d.rectangle([8, H - 46, W - 9, H - 1], fill=L3)
    # estandarte da Ordem
    d.rectangle([W // 2 - 11, 190, W // 2 + 11, 232], fill=(150, 36, 36)); d.polygon([(W // 2 - 11, 232), (W // 2, 244), (W // 2 + 11, 232)], fill=(150, 36, 36))
    d.ellipse([W // 2 - 5, 204, W // 2 + 5, 214], fill=(236, 200, 90))
    return outline(shade_side(im, 16, 10)), (W // 2, H - 1)
def gate_arch():
    W, H = 300, 210
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); paste(im, crenel(W, 24, 26, 16), 0, 0); paste(im, block_wall(W, H - 24, bw=40, seed=9), 0, 24)
    d = ImageDraw.Draw(im); ox0, ox1 = W // 2 - 70, W // 2 + 70
    # vão do arco (transparente) + moldura
    arc = Image.new('L', (W, H), 255); ad = ImageDraw.Draw(arc)
    ad.rectangle([ox0, 90, ox1, H], fill=0); ad.ellipse([ox0, 50, ox1, 130], fill=0)
    a = np.array(im); m = np.array(arc) == 0; a[m] = (0, 0, 0, 0); im = Image.fromarray(a)
    d = ImageDraw.Draw(im)
    for x in range(ox0 - 5, ox1 + 6, 1):                                                                              # aro de pedra
        for y in (50, 51, 52):
            pass
    d.arc([ox0 - 6, 44, ox1 + 6, 136], 180, 360, fill=L1, width=6); d.line([(ox0 - 6, 90), (ox0 - 6, H - 1)], fill=L1, width=6); d.line([(ox1 + 6, 90), (ox1 + 6, H - 1)], fill=L4, width=6)
    for x in range(ox0 + 8, ox1, 14):                                                                                 # grade levantada
        d.line([(x, 56 + int(6 * math.sin((x - W / 2) / 25) ** 2) - 2), (x, 84)], fill=(54, 40, 34), width=3)
    d.rectangle([ox0 + 6, 80, ox1 - 6, 86], fill=(54, 40, 34))
    d.rectangle([W // 2 - 14, 8, W // 2 + 14, 24], fill=L1)
    return outline(shade_side(im, 14, 10)), (W // 2, H - 1)
def keep():
    W, H = 420, 300
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    paste(im, block_wall(W - 120, H - 70, bw=44, seed=21), 60, 70); paste(im, crenel(W - 120, 26, 24, 14), 60, 46)
    for x0 in (0, W - 100):
        paste(im, block_wall(100, H - 40, bw=34, seed=x0 + 5), x0, 40); paste(im, crenel(100, 26, 22, 12), x0, 16)
    d.rectangle([60, 70, W - 61, 80], fill=L1)
    d.rounded_rectangle([W // 2 - 26, H - 110, W // 2 + 26, H - 1], radius=24, fill=(60, 40, 32)); d.line([(W // 2, H - 110), (W // 2, H - 1)], fill=(36, 24, 22), width=2)
    for x in (110, 170, 250, 310):
        d.rectangle([x, 120, x + 12, 156], fill=(34, 24, 22)); d.line([(x, 120), (x + 12, 120)], fill=L5)
    for x in (140, 280):                                                                                              # estandartes da Ordem
        d.rectangle([x - 14, 170, x + 14, 236], fill=(150, 36, 36)); d.polygon([(x - 14, 236), (x, 252), (x + 14, 236)], fill=(150, 36, 36)); d.ellipse([x - 6, 190, x + 6, 202], fill=(236, 200, 90))
    return outline(shade_side(im, 16, 10)), (W // 2, H - 1)
# ------------------------------------------------------------------ peças novas (v2: cidade de montanha)
SL = [(70, 80, 108), (92, 104, 136), (120, 134, 166), (52, 58, 82)]     # ardósia: escuro, médio, claro, sombra
WOOD = (92, 64, 44); WOOD2 = (130, 92, 62); GLOW = (255, 206, 118)
def rock_face(w, h, seed, top_wobble=14):
    """paredão de rocha cinza com estratos, fendas e topo irregular (muro de arrimo dos terraços)"""
    rr = random.Random(seed); a = np.zeros((h, w, 4), 'uint8')
    tops = [top_wobble + int(rr.uniform(-top_wobble, top_wobble) * .6) for _ in range(w // 8 + 2)]
    for x in range(w):
        t = tops[x // 8] + int((tops[min(len(tops) - 1, x // 8 + 1)] - tops[x // 8]) * ((x % 8) / 8))
        for y in range(max(0, t), h):
            band = ((y + int(3 * math.sin(x / 11 + seed))) // 12) % 3
            c = [L3, L2, L3][band]
            if y < t + 4: c = L1
            if x % 29 in (0, 1) and y > t + 8: c = L5          # fenda vertical
            a[y, x] = list(jit(c, 5)) + [255]
    im = Image.fromarray(a); d = ImageDraw.Draw(im)
    for _ in range(w // 6):
        x, y = rr.randint(0, w - 1), rr.randint(top_wobble + 6, h - 1)
        d.line([(x, y), (x + rr.randint(4, 14), y)], fill=L4)
    return outline(shade_side(im, 10, 14))
def cliff_seg(seed=1):
    W_, H_ = 128, 120
    return rock_face(W_, H_, seed), (W_ // 2, H_ - 1)
def stairs_sprite(w=160, steps=7):
    """degraus de pedra vistos de frente (para os vãos dos muros de arrimo)"""
    h = steps * 12 + 6; im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for i in range(steps):
        y = h - 6 - (i + 1) * 12
        d.rectangle([0, y, w - 1, y + 11], fill=[L1, L2][i % 2]); d.line([(0, y), (w - 1, y)], fill=L1); d.line([(0, y + 11), (w - 1, y + 11)], fill=L4)
    return outline(im), (w // 2, h - 1)
def glyph(d, kind, cx, cy, s=1.0):
    def pt(x, y): return (cx + x * s, cy + y * s)
    if kind == 'anvil':
        d.polygon([pt(-9, -3), pt(9, -3), pt(6, 2), pt(3, 2), pt(5, 7), pt(-5, 7), pt(-3, 2), pt(-6, 2)], fill=(40, 44, 52)); d.rectangle([*pt(-11, -4), *pt(-8, -2)], fill=(40, 44, 52))
    elif kind == 'scales':
        d.line([pt(0, -8), pt(0, 7)], fill=(236, 200, 90), width=2); d.line([pt(-8, -5), pt(8, -5)], fill=(236, 200, 90), width=2)
        for sx in (-8, 8): d.polygon([pt(sx, -4), pt(sx - 4, 2), pt(sx + 4, 2)], fill=(236, 200, 90))
    elif kind == 'flask':
        d.rectangle([*pt(-2, -8), *pt(2, -2)], fill=(200, 220, 230)); d.polygon([pt(-2, -2), pt(2, -2), pt(8, 7), pt(-8, 7)], fill=(96, 200, 110)); d.line([pt(-6, 3), pt(6, 3)], fill=(180, 250, 190))
    elif kind == 'star':
        d.polygon([pt(0, -9), pt(2.5, -2.5), pt(9, -2.5), pt(4, 2), pt(6, 8), pt(0, 4), pt(-6, 8), pt(-4, 2), pt(-9, -2.5), pt(-2.5, -2.5)], fill=(236, 200, 90))
    elif kind == 'coin':
        d.ellipse([*pt(-8, -8), *pt(8, 8)], fill=(236, 200, 90)); d.ellipse([*pt(-5, -5), *pt(5, 5)], outline=(176, 132, 40), width=1); d.line([pt(0, -3), pt(0, 3)], fill=(176, 132, 40))
    elif kind == 'lock':
        d.rectangle([*pt(-7, -1), *pt(7, 8)], fill=(236, 200, 90)); d.arc([*pt(-5, -9), *pt(5, 1)], 180, 360, fill=(200, 205, 215), width=2); d.rectangle([*pt(-1, 2), *pt(1, 6)], fill=(60, 44, 20))
def house(seed, w=176, h=170, roof=0, sign=None, awning=None, chim_glow=False, door_w=30):
    """casa de pedra de montanha: telhado de ardósia em quatro águas, paredes de blocos, janelas acesas, porta em arco, tabuleta"""
    rr = random.Random(seed); im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    rh = int(h * .46)
    rc = [(70, 80, 108), (96, 70, 74), (66, 96, 98), (104, 92, 70)][roof % 4]                      # ardósia azul / vinho / verde-azulado / ocre
    # chaminé (atrás do telhado)
    cx = rr.choice([int(w * .22), int(w * .74)]); paste(im, block_wall(22, 46, bw=11, bh=8, seed=seed + 3), cx, 2)
    d.rectangle([cx - 2, 0, cx + 24, 6], fill=L1); d.rectangle([cx + 3, 0, cx + 19, 3], fill=(30, 28, 36))
    # telhado
    d.polygon([(2, rh + 6), (int(w * .2), 6), (int(w * .8), 6), (w - 3, rh + 6)], fill=rc)
    for i, y in enumerate(range(10, rh + 4, 8)):
        k = 1 + .18 * (i % 2)
        col = tuple(min(255, int(v * k)) for v in rc); inset = int((y - 6) * .3)
        d.line([(int(w * .2) - inset + 6, y), (int(w * .8) + inset - 6, y)], fill=tuple(int(v * .72) for v in rc), width=2)
        for x in range(int(w * .2) - inset + 10, int(w * .8) + inset - 8, 16 + (i % 2) * 6):
            d.line([(x, y - 6), (x, y)], fill=tuple(int(v * .8) for v in rc))
    d.line([(int(w * .2), 6), (int(w * .8), 6)], fill=tuple(min(255, int(v * 1.5)) for v in rc), width=3)
    d.polygon([(2, rh + 6), (w - 3, rh + 6), (w - 9, rh + 14), (8, rh + 14)], fill=tuple(int(v * .6) for v in rc))   # beiral/sombra
    # paredes
    paste(im, block_wall(w - 12, h - rh - 12, bw=34, bh=16, seed=seed), 6, rh + 12)
    d.rectangle([4, rh + 12, w - 5, rh + 17], fill=WOOD2); d.line([(4, rh + 17), (w - 5, rh + 17)], fill=WOOD)                  # viga
    for bx in (5, w - 10): d.rectangle([bx, rh + 12, bx + 4, h - 2], fill=WOOD)                                              # pilares
    # janelas
    nwin = 2 if w >= 150 else 1
    dx = w // 2 + (rr.choice([-1, 1]) * (w // 6) if nwin == 1 else 0)
    wx = [w // 2 - w // 3, w // 2 + w // 3] if nwin == 2 else [w // 2 - (dx - w // 2) * 2]
    for x in wx:
        y0 = rh + 30; d.rectangle([x - 11, y0 - 2, x + 11, y0 + 24], fill=WOOD); d.rectangle([x - 8, y0 + 1, x + 8, y0 + 21], fill=GLOW)
        d.line([(x, y0 + 1), (x, y0 + 21)], fill=WOOD); d.line([(x - 8, y0 + 11), (x + 8, y0 + 11)], fill=WOOD)
        d.rectangle([x - 15, y0 - 2, x - 12, y0 + 24], fill=SL[1]); d.rectangle([x + 12, y0 - 2, x + 15, y0 + 24], fill=SL[1])
    # porta em arco
    dc = w // 2; d.rounded_rectangle([dc - door_w // 2 - 4, h - 62, dc + door_w // 2 + 4, h - 1], radius=16, fill=L1)
    d.rounded_rectangle([dc - door_w // 2, h - 58, dc + door_w // 2, h - 1], radius=14, fill=(64, 44, 34)); d.line([(dc, h - 56), (dc, h - 2)], fill=(40, 28, 24))
    d.ellipse([dc + 4, h - 30, dc + 8, h - 26], fill=(236, 200, 90)); d.rectangle([dc - door_w // 2 - 6, h - 6, dc + door_w // 2 + 6, h - 1], fill=L2)
    if awning:
        for i in range(0, w - 20, 16):
            c = awning[(i // 16) % 2]; d.polygon([(10 + i, rh + 20), (26 + i, rh + 20), (28 + i, rh + 36), (8 + i, rh + 36)], fill=c)
    if sign:
        sx = dc + door_w // 2 + 22; d.line([(sx - 14, rh + 40), (sx + 20, rh + 40)], fill=(40, 40, 50), width=3); d.rectangle([sx - 12, rh + 42, sx + 14, rh + 68], fill=WOOD2, outline=WOOD)
        glyph(d, sign, sx + 1, rh + 55, .9)
    if chim_glow:
        d.ellipse([cx + 4, 6, cx + 18, 14], fill=(255, 140, 50))
    # --- volume (vista 3/4): parede lateral + água do telhado à direita, profundidade DX x DY
    DX, DY = 46, 26; big = Image.new('RGBA', (w + DX, h + DY), (0, 0, 0, 0)); big.alpha_composite(im, (0, DY)); d = ImageDraw.Draw(big)
    ry = rh + 12 + DY; base = h + DY
    d.polygon([(w - 6, ry), (w - 6 + DX, ry - DY), (w - 6 + DX, base - 2 - DY), (w - 6, base - 2)], fill=SL[3] if False else L4)      # parede lateral
    for yy_ in range(ry + 14, base - 2, 16):
        o = (yy_ - ry) // 16 % 2 * 14
        d.line([(w - 6, yy_), (w - 6 + DX, yy_ - DY)], fill=MORT)
    for xx_ in range(10, DX, 22):
        d.line([(w - 6 + xx_, ry - int(xx_ * DY / DX)), (w - 6 + xx_, base - 2 - int(xx_ * DY / DX))], fill=MORT)
    d.line([(w - 6 + DX, ry - DY), (w - 6 + DX, base - 2 - DY)], fill=L5, width=2)
    wx0 = w - 6 + DX // 2; wy0 = ry + 26 - DY // 2
    d.rectangle([wx0 - 7, wy0, wx0 + 7, wy0 + 22], fill=WOOD); d.rectangle([wx0 - 5, wy0 + 2, wx0 + 5, wy0 + 20], fill=(150, 120, 80))   # janela lateral
    A = (int(w * .2), 6 + DY); B = (int(w * .8), 6 + DY); Bp = (B[0] + DX, B[1] - DY); Cc = (w - 3, rh + 6 + DY); Ccp = (w - 3 + DX, rh + 6 + DY - DY)
    d.polygon([Cc, Ccp, Bp, B], fill=tuple(int(v * .62) for v in rc))                                                               # água lateral do telhado
    for k_ in range(1, 7):
        t = k_ / 7; a1 = (Cc[0] + (B[0] - Cc[0]) * t, Cc[1] + (B[1] - Cc[1]) * t); a2 = (a1[0] + DX, a1[1] - DY)
        d.line([a1, a2], fill=tuple(int(v * .5) for v in rc))
    d.line([B, Bp], fill=tuple(min(255, int(v * 1.2)) for v in rc), width=3)
    d.polygon([(Cc[0], Cc[1]), (Ccp[0], Ccp[1]), (Ccp[0], Ccp[1] + 8), (Cc[0], Cc[1] + 8)], fill=tuple(int(v * .45) for v in rc))       # beiral lateral
    return outline(shade_side(big, 12, 8)), (w // 2, h + DY - 1)
def pine(seed):
    rr = random.Random(seed); W_, H_ = 58, 124; im = Image.new('RGBA', (W_, H_), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle([W_ // 2 - 4, H_ - 24, W_ // 2 + 4, H_ - 1], fill=(70, 52, 40))
    tiers = 5
    for i in range(tiers):
        y1 = 10 + i * 17; wd = 11 + i * 5; y0 = y1 - 2
        d.polygon([(W_ // 2, y0), (W_ // 2 - wd, y1 + 20), (W_ // 2 + wd, y1 + 20)], fill=[(36, 70, 66), (44, 84, 76), (30, 60, 60)][i % 3])
        d.polygon([(W_ // 2, y0), (W_ // 2 - wd, y1 + 20), (W_ // 2 - wd // 3, y1 + 18)], fill=(62, 110, 96))
        d.line([(W_ // 2 - wd + 3, y1 + 19), (W_ // 2 + wd - 3, y1 + 19)], fill=(24, 48, 50))
    for _ in range(18):
        x, y = rr.randint(16, W_ - 16), rr.randint(14, H_ - 30)
        if im.getpixel((x, y))[3]: d.point((x, y), fill=(220, 232, 240))                    # neve nas pontas
    return outline(im), (W_ // 2, H_ - 1)
def boulder(kind, seed):
    rr = random.Random(seed); sz = [(44, 34), (74, 56), (120, 96)][kind]; W_, H_ = sz
    im = Image.new('RGBA', (W_, H_), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    pts = [(2, H_ - 2)]
    for i in range(1, 9):
        a = math.pi * i / 9; pts.append((W_ / 2 - math.cos(a) * W_ / 2 * rr.uniform(.9, 1.05), H_ - 2 - math.sin(a) * (H_ - 8) * rr.uniform(.8, 1)))
    pts.append((W_ - 2, H_ - 2)); d.polygon(pts, fill=L3)
    d.polygon([pts[0]] + pts[1:5] + [(W_ / 2, H_ * .5), (W_ * .3, H_ - 2)], fill=L2)
    d.polygon([pts[-1]] + pts[-5:-1] + [(W_ * .55, H_ * .45), (W_ * .75, H_ - 2)], fill=L4)
    for _ in range(3 + kind * 3):
        x, y = rr.randint(6, W_ - 8), rr.randint(6, H_ - 4); d.line([(x, y), (x + rr.randint(3, 10), y + rr.randint(-3, 5))], fill=L5)
    return outline(im), (W_ // 2, H_ - 1)
def brazier():
    W_, H_ = 34, 54; im = Image.new('RGBA', (W_, H_), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle([14, 22, 20, H_ - 2], fill=(70, 70, 84)); d.polygon([(4, 14), (30, 14), (24, 26), (10, 26)], fill=(54, 54, 66)); d.line([(4, 14), (30, 14)], fill=L3)
    d.polygon([(10, 14), (17, 0), (24, 14)], fill=(255, 150, 50)); d.polygon([(13, 14), (17, 6), (21, 14)], fill=(255, 220, 110))
    return outline(im), (W_ // 2, H_ - 1)
# ------------------------------------------------------------------ atlas
def build_atlas():
    base = json.load(open(A + 'atlas_regiao1.json')); bim = Image.open(A + 'atlas_regiao1.png').convert('RGBA')
    sprites = {}
    for k, f in (('w_seg', wall_seg()), ('w_side', wall_side()), ('tower', tower()), ('gate', gate_arch()), ('keep', keep()), ('stairs', stairs_sprite()), ('brazier', brazier())):
        sprites[k] = f
    for i in range(3): sprites['cliff%d' % i] = cliff_seg(i + 1)
    for i in range(4): sprites['pine%d' % i] = pine(i + 1)
    for kd in range(3):
        for i in range(2): sprites['rock%d_%d' % (kd, i)] = boulder(kd, 10 * kd + i)
    for i in range(6): sprites['hs%d' % i] = house(30 + i, 150 + 16 * (i % 3), 150 + 8 * (i % 2), roof=i)
    SHOPS = {'fer': dict(w=210, h=190, roof=1, sign='anvil', chim_glow=True), 'mer': dict(w=220, h=180, roof=0, sign='scales', awning=((176, 52, 48), (236, 222, 190))),
             'alq': dict(w=190, h=200, roof=2, sign='flask', chim_glow=False), 'mes': dict(w=210, h=190, roof=0, sign='star'),
             'lei': dict(w=210, h=180, roof=3, sign='coin', awning=((60, 100, 170), (236, 222, 190))), 'cof': dict(w=190, h=170, roof=1, sign='lock')}
    for k, kw in SHOPS.items(): sprites['s_' + k] = house(90 + len(k) * 7 + ord(k[0]), **kw)
    for k in ('v_well', 'v_lamp1', 'v_lamp2', 'v_banner1', 'v_banner2', 'v_sign', 'v_crates', 'v_stall', 'v_post', 'v_barrel1', 'v_barrel2', 'v_hay1', 'v_hay2', 'v_bench1', 'v_bench2', 'v_sack1', 'v_sack2', 'v_torch1', 'v_torch2', 'v_torch3'):
        x, y, w, h, ax, ay = base[k]; sprites[k] = (bim.crop((x, y, x + w, y + h)), (ax, ay))
    AW = 1360; xx = yy = rowh = 0; fr = {}; pos = {}
    for k, (im, anc) in sprites.items():
        w, h = im.size
        if xx + w > AW: xx = 0; yy += rowh + 2; rowh = 0
        pos[k] = (xx, yy, im, anc); xx += w + 2; rowh = max(rowh, h)
    AH = yy + rowh + 2; atlas = Image.new('RGBA', (AW, AH), (0, 0, 0, 0))
    for k, (x, y, im, anc) in pos.items():
        atlas.alpha_composite(im, (x, y)); fr[k] = [x, y, im.width, im.height, anc[0], anc[1]]
    atlas.save(A + 'atlas_cinza.png', optimize=True); json.dump(fr, open(A + 'atlas_cinza.json', 'w'))
    print('atlas', atlas.size, len(fr)); return fr
# ------------------------------------------------------------------ mapa (cidadela em terraços)
W, H = 1600, 2500
WX0, WX1 = 150, 1450                      # muralha externa oeste/leste
SY, NY = 2300, 740                        # muralha sul (portão) e norte (portão)
SG0, SG1 = 710, 890                       # portão sul
NG0, NG1 = 380, 560                       # portão norte (à esquerda: ziguezague)
C1, C2 = 1960, 1460                       # muros de arrimo dos terraços
ST1 = (200, 360)                          # escada 1 (oeste): terraço 1 -> 2
ST2 = (1240, 1400)                        # escada 2 (leste): terraço 2 -> 3
def circ_row(x, y, w, hh, step=18, r=13):
    out = []
    for dy in range(-4, -hh - 1, -18):
        for dx in range(-w // 2 + 8, w // 2 - 6, step):
            out.append([dx, dy, r if dy < -10 else 9])
    return out
def build():
    fr = build_atlas(); props = []
    def P(t, i, x, y, col=None):
        d = {'t': t, 'id': i, 'x': x, 'y': y}
        if col: d['col'] = col
        props.append(d)
    def hwall(yb, x0, x1, gaps, idp='w_seg', step=128, h=130):
        x = x0 + step // 2
        while x < x1:
            if any(g0 - step // 2 < x < g1 + step // 2 for g0, g1 in gaps): x += step; continue
            P('p', idp if idp != 'cliff' else 'cliff%d' % ((x // step) % 3), x, yb, circ_row(x, yb, step, h)); x += step
    # --- muralha externa (norte e sul com portões) + laterais
    hwall(SY, WX0, WX1, [(SG0, SG1)]); hwall(NY, WX0, WX1, [(NG0, NG1)])
    for xb in (WX0, WX1):
        y = NY + 60
        while y <= SY - 10:
            P('p', 'w_side', xb, y, [[0, -4, 13], [0, -22, 13], [0, -40, 13]]); y += 56
    for (x, y) in ((WX0, NY), (WX1, NY), (WX0, SY), (WX1, SY), (SG0 - 62, SY), (SG1 + 62, SY), (NG0 - 62, NY), (NG1 + 62, NY)): P('p', 'tower', x, y + 10, circ_row(x, y, 110, 200))
    gate_col = lambda: [[dx, dy, 13] for dy in (-4, -22, -40, -58, -76, -94) for dx in (-120, -102, -84, 84, 102, 120)]
    P('p', 'gate', (SG0 + SG1) // 2, SY + 10, gate_col()); P('p', 'gate', (NG0 + NG1) // 2, NY + 10, gate_col())
    # --- muros de arrimo dos terraços (rocha) com vão para as escadas
    hwall(C1, WX0 + 24, WX1 - 24, [ST1], 'cliff', 128, 90); hwall(C2, WX0 + 24, WX1 - 24, [ST2], 'cliff', 128, 90)
    for (g0, g1, yb) in ((ST1[0], ST1[1], C1), (ST2[0], ST2[1], C2)):
        P('p', 'stairs', (g0 + g1) // 2, yb + 6, [[0, 80, 1]])
        for x in (g0 - 16, g1 + 16): P('p', 'brazier', x, yb + 4, [[0, -3, 8]])
    # --- Terraço 3 (alto): Bastião, Mestre, Leilão, casas
    P('p', 'keep', 1230, 1180, circ_row(1230, 1180, 420, 240, step=20))
    doors = []
    SH = [('fer', 'Ferreiro', 'anvil', 330, 1760), ('mer', 'Mercador', 'scales', 610, 1760), ('alq', 'Alquimista', 'magic-swirl', 880, 1760), ('cof', 'Cofre', 'locked-chest', 1130, 1790),
          ('mes', 'Mestre de Classe', 'holy-symbol', 560, 1230), ('lei', 'Leilão', 'two-coins', 840, 1230)]
    for (i, nm, ic, x, y) in SH:
        sw = {'fer': 210, 'mer': 220, 'alq': 190, 'mes': 210, 'lei': 210, 'cof': 190}[i]
        P('p', 's_' + i, x, y, [[a + 23, b, r] for a, b, r in circ_row(x, y, sw + 46, 160, step=20)]); doors.append({'id': i, 'nm': nm, 'x': x, 'y': y + 6, 'w': 64, 'h': 82, 'room': 'int_' + i, 'ic': ic})
    for (x, y, k) in ((250, 930, 0), (700, 940, 1), (900, 940, 2), (250, 1140, 3), (1030, 880, 4), (300, 2160, 5), (480, 2170, 1), (1120, 2170, 2), (1320, 2170, 4)):
        P('p', 'hs%d' % k, x, y, [[a + 23, b, r] for a, b, r in circ_row(x, y, 150 + 16 * (k % 3) + 46, 100, step=20)])
    # --- decoração: poço, lampiões, braseiros, barracas, estandartes
    P('p', 'v_well', 800, 2120, [[0, -4, 22], [0, -26, 22]])
    for (x, y) in ((690, 2280), (910, 2280)): P('p', 'v_torch1', x, y, [[0, -3, 6]])
    for (x, y) in ((620, 2060), (980, 2060), (620, 2220), (980, 2220), (470, 1900), (1080, 1900), (700, 1620), (1060, 1620), (470, 1380), (700, 1380), (1000, 1380), (460, 820), (460, 1000)): P('p', 'v_lamp1' if (x + y) % 2 else 'v_lamp2', x, y, [[0, -3, 7]])
    for (x, y, i) in ((590, 2090, 'v_stall'), (1010, 2100, 'v_stall'), (560, 2230, 'v_crates'), (1040, 2240, 'v_crates'), (700, 2050, 'v_barrel1'), (720, 2058, 'v_barrel2'), (880, 2050, 'v_barrel1'), (900, 2056, 'v_hay1'),
                      (430, 1890, 'v_bench1'), (1180, 1890, 'v_bench2'), (700, 1470, 'v_sack1'), (1000, 1440, 'v_sack2'), (720, 1130, 'v_bench1'), (990, 1130, 'v_barrel2'), (450, 1250, 'v_crates'), (1040, 1330, 'v_banner1'), (1420, 1330, 'v_banner1'), (740, 1960, 'v_banner1'), (860, 1960, 'v_banner1')):
        P('p', i, x, y, [[0, -4, 12]] if i != 'v_banner1' else [[0, -3, 6]])
    for (x, y) in ((NG0 - 40, NY + 40), (NG1 + 40, NY + 40), (SG0 - 40, SY - 40), (SG1 + 40, SY - 40)): P('p', 'v_torch1', x, y, [[0, -3, 6]])
    # --- rocha e pinheiros por fora (barreira sólida); corredores livres nas estradas
    rr = random.Random(5)
    def free(x, y):
        if WX0 - 60 < x < WX1 + 60 and NY - 40 < y < SY + 40: return False
        if abs(x - 800) < 150 and y > SY: return False
        if abs(x - 470) < 150 and y < NY: return False
        return True
    gx = 0
    for yy in range(30, H - 20, 78):
        for xx in range(30, W - 20, 86):
            x, y = xx + rr.randint(-26, 26), yy + rr.randint(-26, 26)
            if not free(x, y): continue
            k = rr.random()
            if k < .52: P('p', 'pine%d' % rr.randint(0, 3), x, y, [[0, -3, 11]])
            elif k < .86: P('p', 'rock%d_%d' % (rr.choice([1, 1, 2]), rr.randint(0, 1)), x, y, [[0, -6, 22]])
            else: P('p', 'rock0_%d' % rr.randint(0, 1), x, y, [[0, -3, 10]])
    for (x, y) in ((NG0 - 90, 200), (NG1 + 90, 380), (SG0 - 100, 2420), (SG1 + 100, 2400)): P('p', 'v_torch2', x, y, [[0, -3, 6]])
    npcs = [
        {'id': 'guaz', 'nm': 'Guarda do Portal', 'sh': 'guarda', 'x': 800, 'y': 1980, 'ic': 'treasure-map', 'row': 2, 'win': 'portal'},
        {'id': 'vorak', 'nm': 'Intendente Vorak', 'sh': 'guarda', 'x': 1160, 'y': 1260, 'ic': 'scroll-unfurled', 'row': 2},
        {'id': 'orsa', 'nm': 'Orsa, Mestra das Guildas', 'sh': 'pov_f', 'x': 520, 'y': 1660, 'ic': 'shop', 'row': 2},
        {'id': 'zelle', 'nm': 'Zelle, a Informante', 'sh': 'ladino_b', 'x': 400, 'y': 2250, 'ic': 'hooded-figure', 'row': 2},
        {'id': 'arquivista', 'nm': 'Arquivista Dael', 'sh': 'clerigo', 'x': 760, 'y': 1050, 'ic': 'book-cover', 'row': 2}]
    vill = [{'sh': 'pov_f', 'x': 760, 'y': 2200}, {'sh': 'ladino_b', 'x': 900, 'y': 1900}, {'sh': 'bardo', 'x': 640, 'y': 1860}, {'sh': 'pov_f', 'x': 430, 'y': 1120},
            {'sh': 'guarda', 'x': SG0 + 30, 'y': SY - 70}, {'sh': 'guarda', 'x': SG1 - 30, 'y': SY - 70}, {'sh': 'guarda', 'x': NG0 + 30, 'y': NY + 90}, {'sh': 'guarda', 'x': NG1 - 30, 'y': NY + 90},
            {'sh': 'guarda', 'x': ST1[0] + 40, 'y': C1 - 40}, {'sh': 'guarda', 'x': ST2[1] - 40, 'y': C2 - 40}]
    def tg(x, y): return {'k': 'glow', 'x': x, 'y': y, 'col': '#ffae4a', 'r': 60, 'lo': .4, 'hi': .8, 'fl': 1}
    fx = [tg(NG0 - 40, NY + 12), tg(NG1 + 40, NY + 12), tg(SG0 - 40, SY - 28), tg(SG1 + 40, SY - 28), tg(ST1[0] - 16, C1 - 6), tg(ST1[1] + 16, C1 - 6), tg(ST2[0] - 16, C2 - 6), tg(ST2[1] + 16, C2 - 6),
          {'k': 'smoke', 'x': 330, 'y': 1590}, {'k': 'glow', 'x': 270, 'y': 1730, 'col': '#ff8a2a', 'r': 54, 'lo': .45, 'hi': .9, 'fl': 1}]
    town = {'w': W, 'h': H, 'props': props, 'start': [800, 2220], 'portal': {'x': 800, 'y': 1650, 'stand': [800, 2000], 'fx': {'dx': 0, 'dy': 0, 'rx': 1, 'ry': 1}, 'off': True},
            'npcs': npcs, 'vill': vill, 'doors': doors, 'fx': fx, 'plaza': {'x': 800, 'y': 2130, 'nm': 'Praça dos Registros'}, 'boards': [],
            'exits': [{'id': 'passo', 'nm': 'Passo da Montanha', 'side': 1, 'x': 700, 'y': H - 70, 'w': 200, 'h': 70, 'to': 'zone_passo', 'at': [2250, 330], 'ready': True, 'msg': '', 'toSide': 0},
                      {'id': 'muralha', 'nm': 'Estrada da Muralha', 'side': 0, 'x': 370, 'y': 0, 'w': 200, 'h': 70, 'to': 'zone_muralha', 'at': [1100, 3000], 'ready': False, 'msg': 'A Estrada da Muralha ainda está em obras.', 'toSide': 1}]}
    json.dump(town, open(A + 'cinzamuro.json', 'w'))
    # ---------------- chão (1 px = 1 px do mundo)
    rg = np.random.RandomState(3); g = np.zeros((H, W, 3), 'uint8'); yy, xx = np.mgrid[0:H, 0:W]
    rock = np.array([112, 118, 134]); rock2 = np.array([128, 134, 150])
    n = rg.randint(-7, 7, (H, W, 1)); g[:] = (rock + n).clip(0, 255)
    lowf = np.kron(rg.rand(H // 36 + 2, W // 36 + 2), np.ones((36, 36)))[:H, :W]
    g[lowf > .6] = (rock2 + rg.randint(-7, 7, ((lowf > .6).sum(), 1))).clip(0, 255)
    strat = (((yy + (np.sin(xx / 70.) * 9).astype(int)) // 14) % 5 == 0)
    g[strat & (lowf < .6)] = (rock - 12 + rg.randint(-4, 4, ((strat & (lowf < .6)).sum(), 1))).clip(0, 255)
    inn = (xx > WX0 - 20) & (xx < WX1 + 20) & (yy > NY - 20) & (yy < SY + 24)
    def cobs(a, b, sx=24, sy=24):
        t = ((xx // sx) + (yy // sy)) % 2
        c = np.where(t[..., None] == 0, np.array(a), np.array(b)) + rg.randint(-6, 6, (H, W, 1))
        m = ((xx % sx == 0) | (yy % sy == 0))[..., None]; return np.where(m, np.array([86, 86, 92]), c)
    T1 = cobs((134, 134, 138), (124, 124, 128)); T2 = cobs((126, 128, 136), (116, 118, 126), 28, 20); T3 = cobs((138, 140, 148), (128, 130, 138), 32, 24)
    for (cb, y0, y1) in ((T1, C1, SY + 20), (T2, C2, C1), (T3, NY - 10, C2)):
        m = inn & (yy >= y0) & (yy < y1); g[m] = cb[m]
    # plaças mais claras e vielas de terra batida
    plaza = (np.hypot(xx - 800, (yy - 2130) * 1.25) < 190) | ((abs(xx - 800) < 70) & (yy > C1 - 10)); g[plaza & inn] = (cobs((152, 152, 156), (142, 142, 146))[plaza & inn])
    lane2 = (yy > 1840) & (yy < 1900) & (xx > 200) & (xx < 1400); g[lane2 & inn] = cobs((120, 108, 94), (112, 100, 88), 26, 26)[lane2 & inn]
    lane3 = (yy > 1380) & (yy < 1440) & (xx > 200) & (xx < 1420); g[lane3 & inn] = cobs((120, 108, 94), (112, 100, 88), 26, 26)[lane3 & inn]
    up = (xx > NG0 + 10) & (xx < NG1 - 10) & (yy > NY - 30) & (yy < C2); g[up & inn] = cobs((120, 108, 94), (112, 100, 88), 26, 26)[up & inn]
    # degraus desenhados no chão (faixas claras/escuras) e rampas
    for (s0, s1, yb) in ((ST1[0], ST1[1], C1), (ST2[0], ST2[1], C2)):
        for k in range(8):
            y0 = yb - 6 + k * -0 - 4 + k * 10 - 40; 
    # estrada de pedra até os portões (fora)
    road = ((abs(xx - 800) < 70) & (yy > SY)) | ((abs(xx - 470) < 70) & (yy < NY)); g[road] = (cobs((120, 112, 104), (112, 104, 98), 30, 30)[road]) if False else (146, 128, 106) + rg.randint(-7, 7, (road.sum(), 1))
    # pegada escura sob muros
    for (x0, x1, y0, y1) in ((WX0 - 30, WX1 + 30, NY - 8, NY + 20), (WX0 - 30, WX1 + 30, SY - 8, SY + 20), (WX0 - 20, WX0 + 24, NY, SY), (WX1 - 24, WX1 + 20, NY, SY), (WX0, WX1, C1 - 6, C1 + 18), (WX0, WX1, C2 - 6, C2 + 18)):
        g[y0:y1, x0:x1] = (g[y0:y1, x0:x1] * .62).astype('uint8')
    Image.fromarray(g).save(A + 'cinzamuro_ground.png')
    print('cinzamuro', len(props), 'props', len(doors), 'portas')
if __name__ == '__main__':
    build()
