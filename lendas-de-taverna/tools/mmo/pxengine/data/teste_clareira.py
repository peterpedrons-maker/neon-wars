#!/usr/bin/env python3
"""Teste de pixel art top-down 100% por codigo: clareira, heroi, goblin, slimes.
Saida: lendas-de-taverna/mmo/proto_pixel/{clareira.png,clareira.gif,sprites.png}
Nao mexe no jogo. Rode: python3 teste_clareira.py"""
import os, math, random
import numpy as np
from PIL import Image, ImageDraw

W, H = 400, 248
OUT = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'mmo', 'proto_pixel'))
os.makedirs(OUT, exist_ok=True)


def C(h, a=255):
    return (int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16), a)


B4 = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]
def bay(x, y): return B4[y & 3][x & 3] / 16 - .5


GRASS = [C(c) for c in ['#24561f', '#2f7a2c', '#47a038', '#6cbf44', '#9ad95a']]
TREE_G = [C(c) for c in ['#12351f', '#1d5a31', '#2c8038', '#4aa845', '#8bd05c']]
TREE_B = [C(c) for c in ['#0e2150', '#173d78', '#2360ac', '#3d92d4', '#86d0f0']]
TREE_P = [C(c) for c in ['#3e1747', '#722a72', '#a4468f', '#d572b4', '#f7b4d8']]
STONE = [C(c) for c in ['#352f4c', '#58547a', '#8481a3', '#abaac8', '#d4d4e8']]
MOSS = [C(c) for c in ['#2a3a2e', '#3f5a4a', '#5f8a5a', '#86b070', '#b4d890']]
WATER = [C(c) for c in ['#143f80', '#1f62ad', '#3a8bd2', '#7cc2f0', '#c4ecff']]
BROWN = [C(c) for c in ['#2e1a14', '#5a3624', '#8a5a34', '#b88450', '#dcaa72']]
SLIME_G = [C(c) for c in ['#1f5a24', '#3f9a38', '#74cc48', '#b0ec6c', '#efffc0']]
SLIME_B = [C(c) for c in ['#143e80', '#2872c4', '#52acec', '#92dcff', '#e4f9ff']]
SLIME_O = [C(c) for c in ['#7a2210', '#cc4a1c', '#f08832', '#ffb85c', '#ffeaa8']]
INK = C('#2a1a2e')


def vnoise(w, h, s, seed):
    r = np.random.RandomState(seed)
    g = r.rand(h // s + 3, w // s + 3).astype('float32')
    im = Image.fromarray((g * 255).astype('uint8')).resize(((w // s + 3) * s, (h // s + 3) * s), Image.BICUBIC)
    return (np.asarray(im).astype('float32') / 255)[:h, :w]


def outline(img, col):
    w, h = img.size
    src = img.load()
    out = img.copy()
    o = out.load()
    for y in range(h):
        for x in range(w):
            if src[x, y][3] == 0:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h and src[nx, ny][3] > 0:
                        o[x, y] = col
                        break
    return out


def blob(img, cx, cy, rx, ry, ramp, tex=0, flat=None, jit=0.12, seed=0, edge=True):
    """Pinta um blob sombreado (luz vindo de cima-esquerda) com dither e textura de folhas."""
    px = img.load()
    w, h = img.size
    rng = np.random.RandomState(seed)
    jn = rng.rand(h + 4, w + 4)
    mask = {}
    for y in range(max(0, int(cy - ry) - 2), min(h, int(cy + ry) + 3)):
        for x in range(max(0, int(cx - rx) - 2), min(w, int(cx + rx) + 3)):
            nx = (x + .5 - cx) / rx
            ny = (y + .5 - cy) / ry
            if flat is not None and ny > flat:
                continue
            e = nx * nx + ny * ny + (jn[y, x] - .5) * jit * 2
            if e > 1:
                continue
            mask[(x, y)] = (nx, ny, math.sqrt(max(0, 1 - e)))
    for (x, y), (nx, ny, hh) in mask.items():
        l = (-.5 * nx - .7 * ny) * .8 + .5 * hh
        if tex:
            u = (x + ((y // 3) % 2) * 2) % 4
            v = y % 3
            if u == 0 and v == 0: l += .34 * tex
            elif u in (1, 2) and v == 2: l -= .26 * tex
        l += bay(x, y) * .16
        i = 4 if l > .64 else 3 if l > .33 else 2 if l > -.02 else 1
        if edge and (x, y + 1) not in mask:
            i = 1 if i > 1 else 0
        px[x, y] = ramp[i]


def shadow(bg, cx, cy, rx, ry, a=70):
    m = Image.new('L', bg.size, 0)
    d = ImageDraw.Draw(m)
    d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=a)
    bg.paste(Image.new('RGB', bg.size, (16, 40, 20)), (0, 0), m)


# ---------------------------------------------------------------- cenario
def make_grass():
    v = vnoise(W, H, 30, 1) * .66 + vnoise(W, H, 10, 2) * .24 + vnoise(W, H, 4, 3) * .10
    p1, p2, p3 = np.percentile(v, [5, 70, 93])
    img = Image.new('RGB', (W, H))
    px = img.load()
    for y in range(H):
        for x in range(W):
            t = v[y, x] + bay(x, y) * .06
            i = 1 if t < p1 else 2 if t < p2 else 3 if t < p3 else 4
            px[x, y] = GRASS[i][:3]
    return img


def water_mask():
    wob = vnoise(W, H, 14, 7)
    wob2 = vnoise(W, H, 18, 9)
    m = np.zeros((H, W), bool)
    for y in range(H):
        fac = max(0, 1 - (y / 205) ** 2.5)
        for x in range(W):
            left = x < 36 - y * .24 + (wob[y, x] - .5) * 34
            right = x > W - 56 * fac + (wob2[y, x] - .5) * 30 and fac > 0.02 and y < 210
            m[y, x] = left or right
    return m


def dilate(m):
    d = m.copy()
    d[1:] |= m[:-1]; d[:-1] |= m[1:]; d[:, 1:] |= m[:, :-1]; d[:, :-1] |= m[:, 1:]
    return d


def water_layer(mask, phase):
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    px = img.load()
    inner = ~dilate(~mask)
    rim = dilate(mask) & ~mask
    for y in range(H):
        for x in range(W):
            if mask[y, x]:
                row = y // 4
                xo = x + (row % 2) * 3 + phase
                u = xo % 6
                v = y % 4
                c = WATER[2]
                if v == 0 and u in (1, 2, 3): c = WATER[3]
                elif v == 1 and u in (0, 4): c = WATER[3]
                elif v == 2 and u in (2,): c = WATER[1]
                if (x + y * 3) % 17 == 0 and v == 0: c = WATER[4]
                if not inner[y, x]: c = WATER[4] if (x + phase) % 3 else WATER[3]
                px[x, y] = c
            elif rim[y, x]:
                px[x, y] = WATER[0]
    return img


def stone_sprite(rx, ry, ramp, seed, tex=0):
    img = Image.new('RGBA', (rx * 2 + 4, ry * 2 + 4), (0, 0, 0, 0))
    blob(img, rx + 2, ry + 2, rx, ry, ramp, flat=.7, jit=.18, seed=seed)
    return outline(img, ramp[0])


def tree_sprite(kind, seed):
    """kind: 'bigc','smallc' (conifera em camadas), 'round' (arbusto rosa)."""
    rp = {'bigc_b': TREE_B, 'bigc_g': TREE_G, 'small_g': TREE_G, 'small_b': TREE_B, 'round_p': TREE_P, 'round_g': TREE_G}[kind]
    if kind.startswith('bigc'):
        w, h, fx, fy = 60, 78, 30, 70
        tiers = [(30, 56, 24, 11), (30, 43, 20, 10), (30, 31, 15, 9), (30, 20, 10, 8), (30, 12, 5, 7)]
    elif kind.startswith('small'):
        w, h, fx, fy = 40, 56, 20, 50
        tiers = [(20, 40, 15, 8), (20, 29, 11, 7), (20, 20, 7, 6), (20, 13, 3, 5)]
    else:
        w, h, fx, fy = 64, 52, 32, 46
        tiers = [(32, 32, 26, 14), (17, 27, 12, 10), (47, 27, 12, 10), (32, 21, 15, 11), (24, 15, 9, 7), (40, 15, 9, 7)]
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if not kind.startswith('round'):
        tw = 3 if kind.startswith('small') else 4
        d.rectangle([fx - tw, fy - 8, fx + tw - 1, fy], fill=BROWN[2])
        d.rectangle([fx - tw, fy - 8, fx - tw + 1, fy], fill=BROWN[3])
        d.rectangle([fx + tw - 2, fy - 8, fx + tw - 1, fy], fill=BROWN[1])
    for i, (cx, cy, rx, ry) in enumerate(tiers):
        blob(img, cx, cy, rx, ry, rp, tex=1, flat=.55 if not kind.startswith('round') else .7, jit=.1, seed=seed + i)
    # cristais/brilho no topo das coniferas (como no gif)
    spr = outline(img, rp[0])
    return spr, fx, fy


def stump_sprite():
    img = Image.new('RGBA', (22, 18), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle([3, 7, 18, 13], fill=BROWN[2])
    d.rectangle([3, 7, 6, 13], fill=BROWN[3])
    d.rectangle([14, 7, 18, 13], fill=BROWN[1])
    d.ellipse([2, 11, 19, 16], fill=BROWN[1])
    d.rectangle([3, 9, 18, 13], fill=BROWN[2])
    d.rectangle([3, 9, 5, 13], fill=BROWN[3])
    d.rectangle([15, 9, 18, 13], fill=BROWN[1])
    d.ellipse([2, 3, 19, 11], fill=BROWN[4])
    d.ellipse([4, 4, 17, 10], fill=BROWN[3])
    d.ellipse([7, 5, 14, 9], outline=BROWN[2])
    d.point([10, 7], fill=BROWN[2])
    return outline(img, BROWN[0])


def put(bg, spr, x, y):
    bg.paste(spr.convert('RGB'), (int(x), int(y)), spr)


# ---------------------------------------------------------------- personagens
def line(d, p0, p1, col, th=1):
    x0, y0 = p0; x1, y1 = p1
    n = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
    for i in range(n + 1):
        t = i / max(1, n)
        x = round(x0 + (x1 - x0) * t); y = round(y0 + (y1 - y0) * t)
        for k in range(th):
            d.point([x, y + k], fill=col)


def hero(pose='idle', t=0):
    """Canvas 44x36. pes em (14,32). t = 0/1 respiracao."""
    img = Image.new('RGBA', (44, 36), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    bob = 1 if (pose == 'idle' and t) else 0
    SK, SKs = C('#f2c496'), C('#d89a72')
    OR = [C('#7a2e18'), C('#c2501e'), C('#ee7a2a'), C('#ffa850')]
    HAIR = [C('#8a3012'), C('#e0602a'), C('#ff8c3c')]
    # pernas
    d.rectangle([11, 29, 12, 32], fill=C('#4a2c22')); d.rectangle([16, 29, 17, 32], fill=C('#4a2c22'))
    d.point([11, 32], fill=C('#2e1a14')); d.point([16, 32], fill=C('#2e1a14'))
    by = bob
    # corpo
    d.rectangle([9, 19 + by, 18, 28], fill=OR[2])
    d.rectangle([9, 19 + by, 10, 28], fill=OR[3])
    d.rectangle([17, 19 + by, 18, 28], fill=OR[1])
    d.rectangle([9, 26, 18, 26], fill=BROWN[1])
    d.point([13, 26], fill=C('#ffd05a')); d.point([14, 26], fill=C('#ffd05a'))
    d.rectangle([9, 28, 18, 28], fill=OR[0]) if False else None
    # lenco
    d.rectangle([9, 18 + by, 18, 19 + by], fill=C('#3b6fd0'))
    d.rectangle([9, 18 + by, 18, 18 + by], fill=C('#5f98f0'))
    d.rectangle([17, 19 + by, 18, 19 + by], fill=C('#27489a'))
    d.rectangle([17, 20 + by, 18, 22 + by], fill=C('#27489a'))
    # cabeca
    d.rectangle([9, 8 + by, 18, 17 + by], fill=SK)
    d.rectangle([17, 9 + by, 18, 17 + by], fill=SKs)
    d.rectangle([9, 17 + by, 18, 17 + by], fill=SKs)
    # cabelo/chapeu laranja
    d.rectangle([8, 5 + by, 19, 9 + by], fill=HAIR[1])
    d.rectangle([9, 4 + by, 18, 5 + by], fill=HAIR[2])
    d.rectangle([8, 6 + by, 9, 13 + by], fill=HAIR[1])
    d.rectangle([18, 6 + by, 19, 13 + by], fill=HAIR[0])
    d.rectangle([10, 9 + by, 12, 9 + by], fill=HAIR[1]); d.rectangle([14, 9 + by, 17, 9 + by], fill=HAIR[1])
    # olhos
    d.rectangle([11, 12 + by, 11, 13 + by], fill=INK); d.rectangle([16, 12 + by, 16, 13 + by], fill=INK)
    d.point([11, 12 + by], fill=C('#ffffff')) if False else None
    d.point([13, 15 + by], fill=SKs); d.point([14, 15 + by], fill=SKs)
    # braco esquerdo
    d.rectangle([7, 20 + by, 8, 25 + by], fill=OR[1]); d.point([7, 26 + by], fill=SK); d.point([8, 26 + by], fill=SK)
    # braco direito + espada
    ang = {'idle': (22, 26 + by, 25, 33), 'wind': (21, 17, 17, 3), 'strike': (24, 21, 41, 18),
           'recover': (22, 25, 31, 33)}[pose]
    hx, hy = ang[0], ang[1]
    d.rectangle([19, 20 + by, 20, 24 + by], fill=OR[1])
    shoulder = (20, 21 + by)
    # braco ate a mao
    line(d, shoulder, (hx, hy), OR[1], 2)
    d.rectangle([hx - 1, hy - 1, hx, hy], fill=SK)
    # lamina
    bx, by2 = ang[2], ang[3]
    dx, dy = bx - hx, by2 - hy
    n = max(abs(dx), abs(dy)) or 1
    ux, uy = dx / n, dy / n
    gx, gy = hx + ux * 2, hy + uy * 2
    # guarda
    px_, py_ = -uy, ux
    line(d, (gx - px_ * 2, gy - py_ * 2), (gx + px_ * 2, gy + py_ * 2), C('#d8a840'))
    line(d, (hx, hy), (gx, gy), BROWN[1])
    line(d, (gx + ux, gy + uy), (bx, by2), C('#9aa6c4'), 2)
    line(d, (gx + ux, gy + uy), (bx, by2), C('#f4f8ff'), 1)
    img = outline(img, INK)
    if pose == 'strike':
        d2 = ImageDraw.Draw(img)
        for k in range(-62, 36, 3):
            a = math.radians(k)
            r = 17
            x = 24 + math.cos(a) * r; y = 21 + math.sin(a) * r
            al = 255
            d2.point([round(x), round(y)], fill=C('#ffffff'))
            d2.point([round(x - 1), round(y)], fill=C('#bfe8ff'))
    return img


def goblin(pose='idle', t=0):
    img = Image.new('RGBA', (40, 36), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    G = [C('#2c5a1c'), C('#4a8a2a'), C('#78b83c'), C('#a8dc5a')]
    bob = 1 if (pose == 'idle' and t) else 0
    ox = 0
    d.rectangle([11, 29, 12, 32], fill=G[1]); d.rectangle([17, 29, 18, 32], fill=G[1])
    d.rectangle([10, 32, 12, 32], fill=BROWN[1]); d.rectangle([16, 32, 18, 32], fill=BROWN[1])
    # corpo + tanga
    d.rectangle([10, 20 + bob, 19, 28], fill=G[2]); d.rectangle([10, 20 + bob, 11, 28], fill=G[3]); d.rectangle([18, 20 + bob, 19, 28], fill=G[1])
    d.rectangle([10, 25, 19, 29], fill=BROWN[2]); d.rectangle([18, 25, 19, 29], fill=BROWN[1]); d.rectangle([10, 25, 19, 25], fill=BROWN[3])
    # cabeca
    d.rectangle([9, 9 + bob, 20, 19 + bob], fill=G[2]); d.rectangle([9, 9 + bob, 11, 19 + bob], fill=G[3]); d.rectangle([18, 10 + bob, 20, 19 + bob], fill=G[1])
    d.rectangle([9, 19 + bob, 20, 19 + bob], fill=G[1])
    # orelhas pontudas
    for k in range(6):
        d.rectangle([3 + k, 12 + bob - (k // 3), 8, 13 + bob + (0 if k < 4 else 0)], fill=G[2]) if False else None
    line(d, (8, 13 + bob), (2, 10 + bob), G[2], 2); line(d, (21, 13 + bob), (27, 10 + bob), G[1], 2)
    d.point([8, 13 + bob], fill=G[2]); d.point([21, 13 + bob], fill=G[1])
    # olhos e boca
    d.rectangle([11, 13 + bob, 13, 14 + bob], fill=C('#ffe04a')); d.rectangle([16, 13 + bob, 18, 14 + bob], fill=C('#ffe04a'))
    d.point([12, 14 + bob], fill=INK); d.point([17, 14 + bob], fill=INK)
    d.rectangle([11, 12 + bob, 13, 12 + bob], fill=G[0]); d.rectangle([16, 12 + bob, 18, 12 + bob], fill=G[0])
    d.rectangle([12, 17 + bob, 17, 17 + bob], fill=G[0]); d.point([13, 17 + bob], fill=C('#ffffff')); d.point([16, 17 + bob], fill=C('#ffffff'))
    # bracos + maca
    d.rectangle([7, 21 + bob, 9, 26 + bob], fill=G[2]); d.rectangle([20, 21 + bob, 22, 26 + bob], fill=G[1])
    club_top = (27, 12) if pose != 'hurt' else (30, 20)
    line(d, (23, 25 + bob), club_top, BROWN[2], 2)
    d.rectangle([club_top[0] - 2, club_top[1] - 2, club_top[0] + 2, club_top[1] + 2], fill=BROWN[3])
    d.point([club_top[0] + 1, club_top[1] + 1], fill=BROWN[1]); d.point([club_top[0] - 1, club_top[1] - 1], fill=C('#d8d8e8'))
    img = outline(img, INK)
    if pose == 'hurt':
        px = img.load()
        for y in range(img.size[1]):
            for x in range(img.size[0]):
                if px[x, y][3] and px[x, y][:3] != INK[:3]:
                    px[x, y] = (255, 255, 255, 255)
        img = img.transform(img.size, Image.AFFINE, (1, 0, -2, 0, 1, 0))
    return img


def slime(ramp, s):
    """s em [-1,1]: achatado(-)/esticado(+)."""
    rx = int(round(10 - 1.5 * s)); ry = int(round(8 + 1.5 * s))
    img = Image.new('RGBA', (rx * 2 + 6, ry * 2 + 6), (0, 0, 0, 0))
    cx, cy = rx + 3, ry + 3 + 2
    blob(img, cx, cy, rx, ry, ramp, flat=.5, jit=.04, seed=3, edge=False)
    d = ImageDraw.Draw(img)
    ey = cy - 1
    d.rectangle([cx - 4, ey, cx - 3, ey + 2], fill=INK); d.rectangle([cx + 2, ey, cx + 3, ey + 2], fill=INK)
    d.point([cx - 4, ey], fill=C('#ffffff')); d.point([cx + 2, ey], fill=C('#ffffff'))
    d.point([cx - rx // 2 - 1, cy - ry // 2 - 1], fill=ramp[4]); d.point([cx - rx // 2, cy - ry // 2 - 1], fill=ramp[4])
    d.point([cx - rx // 2 - 1, cy - ry // 2], fill=ramp[4])
    return outline(img, ramp[0]), cx, img.size[1] - 3


FONT = {'0': '111101101101111', '1': '010110010010111', '2': '111001111100111', '3': '111001111001111', '4': '101101111001001',
        '5': '111100111001111', '6': '111100111101111', '7': '111001001001001', '8': '111101111101111', '9': '111101111001111'}


def number(txt, col=C('#ffe04a')):
    img = Image.new('RGBA', (len(txt) * 4 + 2, 9), (0, 0, 0, 0))
    px = img.load()
    for i, ch in enumerate(txt):
        for k, b in enumerate(FONT[ch]):
            if b == '1':
                px[1 + i * 4 + k % 3, 1 + k // 3] = col
    return outline(img, INK)


def butterfly(f, col):
    img = Image.new('RGBA', (7, 5), (0, 0, 0, 0))
    px = img.load()
    if f % 2:
        for p in [(0, 1), (1, 0), (1, 1), (5, 0), (5, 1), (6, 1), (2, 2), (4, 2)]: px[p] = col
    else:
        for p in [(1, 2), (2, 2), (1, 3), (4, 2), (5, 2), (5, 3)]: px[p] = col
    px[3, 2] = INK; px[3, 3] = INK
    return img


# ---------------------------------------------------------------- composicao
def build_static():
    random.seed(11)
    bg = make_grass()
    wm = water_mask()
    solid = dilate(dilate(wm))
    # trilha de pedras
    pts = [(-10, 150), (50, 146), (110, 156), (165, 184), (230, 198), (290, 180), (345, 154), (410, 148)]
    stones = []
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        n = int(math.hypot(x1 - x0, y1 - y0))
        for i in range(0, n, 6):
            t = i / n
            cx = x0 + (x1 - x0) * t; cy = y0 + (y1 - y0) * t
            for _ in range(2):
                sx = cx + random.uniform(-3, 3); sy = cy + random.uniform(-18, 18)
                stones.append((sx, sy))
    placed = []
    for (sx, sy) in sorted(stones, key=lambda p: p[1]):
        rx = random.randint(4, 6); ry = random.randint(3, 4)
        if any((sx - px_) ** 2 + ((sy - py_) * 1.5) ** 2 < (rx + qx + 1) ** 2 for px_, py_, qx in placed): continue
        if 0 <= int(sx) < W and 0 <= int(sy) < H and solid[int(sy), int(sx)]: continue
        placed.append((sx, sy, rx))
        ramp = MOSS if random.random() < .12 else STONE
        sp = stone_sprite(rx, ry, ramp, random.randint(0, 999))
        shadow(bg, sx, sy + ry, rx + 1, 2, 50)
        put(bg, sp, sx - rx - 2, sy - ry - 2)
    # tufos de grama + flores
    for _ in range(420):
        x, y = random.randint(2, W - 3), random.randint(2, H - 3)
        if solid[y, x]: continue
        px = bg.load()
        col = GRASS[3][:3] if random.random() < .6 else GRASS[1][:3]
        for dx, dy in ((0, 0), (-1, -1), (1, -2), (0, -1)):
            if 0 <= x + dx < W and 0 <= y + dy < H: px[x + dx, y + dy] = col
    for _ in range(26):
        x, y = random.randint(10, W - 12), random.randint(70, H - 6)
        if solid[y, x]: continue
        petal, ctr = (C('#ffffff'), C('#ffd23a')) if random.random() < .5 else (C('#e8453c'), C('#ffffff'))
        px = bg.load()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)): px[x + dx, y + dy] = petal[:3]
        px[x, y] = ctr[:3]
    return bg, wm


def objects():
    obj = []
    spr = {k: tree_sprite(k, i * 7) for i, k in enumerate(['bigc_b', 'bigc_g', 'small_g', 'small_b', 'round_p', 'round_g'])}
    def tree(kind, x, y):
        s, fx, fy = spr[kind]
        obj.append(dict(img=s, x=x - fx, y=y - fy, foot=y, sh=(x, y, fx * .55, 4)))
    tree('bigc_b', 98, 70); tree('bigc_g', 168, 36); tree('small_g', 134, 54); tree('bigc_b', 272, 74)
    tree('small_b', 238, 40); tree('bigc_g', 336, 58); tree('small_b', 318, 38); tree('small_g', 58, 40)
    tree('small_g', 376, 120)
    tree('round_p', 66, 240); tree('small_g', 142, 236); tree('bigc_b', 322, 236); tree('bigc_g', 372, 214)
    tree('small_b', 296, 176); tree('small_g', 256, 222)
    tree('small_g', 20, 196)
    s = stump_sprite()
    for (x, y) in [(52, 90), (338, 100), (198, 236)]:
        obj.append(dict(img=s, x=x - 11, y=y - 15, foot=y, sh=(x, y, 10, 3)))
    for (x, y, rx, ry, ramp, sd) in [(32, 122, 10, 7, STONE, 4), (140, 230, 5, 4, STONE, 5), (66, 180, 8, 6, STONE, 8), (236, 106, 6, 5, STONE, 9),
                                     (86, 164, 6, 5, MOSS, 12)]:
        sp = stone_sprite(rx, ry, ramp, sd)
        obj.append(dict(img=sp, x=x - rx - 2, y=y - ry * 2 - 2, foot=y, sh=(x, y, rx + 2, 3)))
    return obj


def render_frame(f, bg, wm, objs, cache):
    im = bg.copy()
    ph = (f // 4) % 6
    if ph not in cache['w']: cache['w'][ph] = water_layer(wm, ph)
    wl = cache['w'][ph]
    im.paste(wl.convert('RGB'), (0, 0), wl)
    ents = list(objs)
    for o in ents:
        shadow(im, *o['sh']) if 'sh' in o else None
    # fase da luta
    cyc = f % 24
    if cyc < 8: hp, gp = ('idle', (cyc // 4) % 2), ('idle', (cyc // 4) % 2)
    elif cyc < 10: hp, gp = ('wind', 0), ('idle', 0)
    elif cyc < 12: hp, gp = ('strike', 0), ('hurt', 0)
    elif cyc < 14: hp, gp = ('recover', 0), ('hurt', 0)
    else: hp, gp = ('idle', (cyc // 4) % 2), ('idle', (cyc // 4) % 2)
    dyn = []
    HX, HY, GX, GY = 188, 186, 226, 188
    shadow(im, HX, HY, 8, 3); shadow(im, GX, GY, 8, 3)
    dyn.append(dict(img=cache['h'][(hp[0], hp[1])], x=HX - 14, y=HY - 32, foot=HY))
    dyn.append(dict(img=cache['g'][(gp[0], gp[1])], x=GX - 14 + (3 if gp[0] == 'hurt' and cyc < 12 else 1 if gp[0] == 'hurt' else 0), y=GY - 32, foot=GY))
    # slimes
    for i, (x, y, ramp, name) in enumerate([(148, 82, SLIME_G, 'g'), (218, 78, SLIME_B, 'b'), (258, 216, SLIME_O, 'o')]):
        s = math.sin((f / 12 + i * .33) * 2 * math.pi)
        k = int(round(s * 1.0))
        sp, cx, fy = cache['s'][(name, k)]
        jump = max(0, math.sin((f / 12 + i * .33) * 2 * math.pi - .6)) * 4
        shadow(im, x, y, 8 - jump * .4, 3, 70)
        dyn.append(dict(img=sp, x=x - cx, y=y - fy - jump, foot=y))
    # borboletas
    for j, (bx, by, col) in enumerate([(150, 118, C('#ffffff')), (300, 120, C('#ffd23a'))]):
        a = (f / 24 + j * .5) * 2 * math.pi
        dyn.append(dict(img=butterfly(f // 2 + j, col), x=bx + math.cos(a) * 18, y=by + math.sin(a * 2) * 6, foot=999))
    # numero de dano
    if 10 <= cyc < 22:
        dyn.append(dict(img=cache['n'], x=GX - 4, y=GY - 44 - (cyc - 10) * .8, foot=1000))
    for o in sorted(ents + dyn, key=lambda o: o['foot']):
        put(im, o['img'], o['x'], o['y'])
    return im


def main():
    bg, wm = build_static()
    objs = objects()
    cache = {'w': {}, 'h': {}, 'g': {}, 's': {}, 'n': number('27')}
    for p, t in [('idle', 0), ('idle', 1), ('wind', 0), ('strike', 0), ('recover', 0)]:
        cache['h'][(p, t)] = hero(p, t)
    for p, t in [('idle', 0), ('idle', 1), ('hurt', 0)]:
        cache['g'][(p, t)] = goblin(p, t)
    for name, r in [('g', SLIME_G), ('b', SLIME_B), ('o', SLIME_O)]:
        for k in (-1, 0, 1):
            cache['s'][(name, k)] = slime(r, k)
    frames = [render_frame(f, bg, wm, objs, cache) for f in range(24)]
    big = [f.resize((W * 2, H * 2), Image.NEAREST) for f in frames]
    big[10].save(os.path.join(OUT, 'clareira.png'))
    pal = big[0].quantize(colors=96, method=Image.MEDIANCUT, dither=Image.NONE)
    q = [im.quantize(palette=pal, dither=Image.NONE) for im in big]
    q[0].save(os.path.join(OUT, 'clareira.gif'), save_all=True, append_images=q[1:], duration=90, loop=0, disposal=1)
    # folha de sprites ampliada (4x)
    sh = Image.new('RGB', (44 * 5 + 40 * 3 + 60, 40), (60, 120, 50))
    x = 2
    for k in [('idle', 0), ('idle', 1), ('wind', 0), ('strike', 0), ('recover', 0)]:
        put(sh, cache['h'][k], x, 2); x += 44
    for k in [('idle', 0), ('idle', 1), ('hurt', 0)]:
        put(sh, cache['g'][k], x, 2); x += 40
    for n in 'gbo':
        put(sh, cache['s'][(n, 0)][0], x, 8); x += 20
    sh.resize((sh.width * 4, sh.height * 4), Image.NEAREST).save(os.path.join(OUT, 'sprites.png'))
    print('ok', OUT)


if __name__ == '__main__':
    main()
