"""Gera texturas pixel-art de efeitos (rachaduras, poeira, pedras, fagulhas) -> assets/fx/*.png
uso: python3.13 build_fx.py"""
import math, random
import numpy as np
from PIL import Image, ImageFilter, ImageDraw
import os

OUT = os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'fx')
os.makedirs(OUT, exist_ok=True)
R = random.Random(7)


def noise(w, h, scale, seed):
    rs = np.random.RandomState(seed)
    base = rs.rand(h // scale + 2, w // scale + 2)
    im = Image.fromarray((base * 255).astype('uint8')).resize((w, h), Image.BICUBIC)
    return np.asarray(im).astype('float32') / 255


# ---------- rachaduras no chão (4 variações, 128x64) ----------
def crack(seed, W=128, H=64):
    r = random.Random(seed)
    K = 4
    outer = Image.new('L', (W * K, H * K), 0)
    inner = Image.new('L', (W * K, H * K), 0)
    do, di = ImageDraw.Draw(outer), ImageDraw.Draw(inner)
    cx, cy = W * K // 2, H * K // 2

    def branch(x, y, a, length, width, depth):
        pts = [(x, y)]
        for _ in range(int(length / 8)):
            a += r.uniform(-.38, .38)
            x += math.cos(a) * 8
            y += math.sin(a) * 8 * .5
            pts.append((x, y))
            if depth < 1 and r.random() < .16:
                branch(x, y, a + r.choice([-1, 1]) * r.uniform(.6, 1.0), length * .45, width * .55, depth + 1)
        for i in range(len(pts) - 1):
            t = i / max(1, len(pts) - 1)
            w = max(2, int(width * (1 - t * .75)))
            do.line([pts[i], pts[i + 1]], fill=255, width=w)
            wi = int(w * .24)
            if wi >= 3:
                di.line([pts[i], pts[i + 1]], fill=255, width=wi)

    n = 6 + seed % 2
    for i in range(n):
        a = i / n * 6.283 + r.uniform(-.25, .25)
        branch(cx, cy, a, r.uniform(150, 215), 20, 0)
    ml = lambda im: np.asarray(im.resize((W, H), Image.LANCZOS)).astype('float32') / 255
    mo, mi = ml(outer), ml(inner)
    halo = np.asarray(outer.resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(2.4))).astype('float32') / 255
    out = np.zeros((H, W, 4), 'float32')
    out[..., :3] = np.array([40, 24, 14]) / 255
    out[..., 3] = np.clip(halo * 1.5, 0, 1) * .5
    d = mo > .3
    out[d] = [18 / 255, 10 / 255, 6 / 255, .97]
    l = mi > .3
    t = np.clip(mi[l], 0, 1)[:, None]
    out[l, :3] = (np.array([255, 120, 30]) * (1 - t) + np.array([255, 215, 110]) * t) / 255
    out[l, 3] = 1
    return Image.fromarray((out * 255).astype('uint8'), 'RGBA')


# ---------- poeira (6 variações 32x32, esfera de ruído com sombreamento) ----------
def dust(seed, S=32, base=(220, 200, 165), shade=(120, 100, 80)):
    r = np.random.RandomState(seed)
    yy, xx = np.mgrid[0:S, 0:S].astype('float32')
    cx = cy = S / 2
    d = np.hypot(xx - cx, yy - cy) / (S / 2)
    n = noise(S, S, 4, seed) * .5 + noise(S, S, 8, seed + 9) * .5
    dens = np.clip(1.05 - d - (n - .5) * .7, 0, 1)
    dens = np.clip(dens * 1.8, 0, 1)
    dens = (np.round(dens * 4) / 4)  # posteriza p/ pixel-art
    lit = np.clip(1 - (yy - cy) / S * 1.2 + (n - .5) * .4, .3, 1)
    lit = np.round(lit * 4) / 4
    base = np.array(base, 'float32')
    shade = np.array(shade, 'float32')
    col = shade[None, None] * (1 - lit[..., None]) + base[None, None] * lit[..., None]
    out = np.dstack([col / 255, dens * .9])
    return Image.fromarray((out * 255).astype('uint8'), 'RGBA')


# ---------- pedras facetadas (6 variações 16x16) ----------
def rock(seed, S=16):
    r = random.Random(seed)
    big = 8
    im = Image.new('RGBA', (S * big, S * big), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    n = r.randint(6, 8)
    pts = []
    for i in range(n):
        a = i / n * 6.283 + r.uniform(-.2, .2)
        rr = r.uniform(.62, .95) * S * big / 2
        pts.append((S * big / 2 + math.cos(a) * rr, S * big / 2 + math.sin(a) * rr * .9))
    d.polygon(pts, fill=(112, 86, 58, 255))
    c = (S * big / 2 - 8, S * big / 2 - 8)
    # facetas: claro em cima à esquerda, escuro embaixo à direita
    for i in range(n):
        p0, p1 = pts[i], pts[(i + 1) % n]
        mid = ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2)
        ang = math.atan2(mid[1] - S * big / 2, mid[0] - S * big / 2)
        lit = math.cos(ang + 2.35)
        col = (int(112 + 62 * lit), int(86 + 50 * lit), int(58 + 36 * lit), 255)
        d.polygon([c, p0, p1], fill=col)
    d.line(pts + [pts[0]], fill=(38, 26, 16, 255), width=big)
    return im.resize((S, S), Image.NEAREST if False else Image.BOX).convert('RGBA')


# ---------- fagulha/estilhaço de luz (8x8) ----------
def spark(S=8):
    yy, xx = np.mgrid[0:S, 0:S].astype('float32')
    d = np.hypot(xx - S / 2 + .5, yy - S / 2 + .5) / (S / 2)
    a = np.clip(1.2 - d * 1.2, 0, 1)
    out = np.dstack([np.ones((S, S)), 1 - d * .4, 1 - d * .85, a])
    return Image.fromarray((np.clip(out, 0, 1) * 255).astype('uint8'), 'RGBA')


# monta a sheet: linha0 = rachaduras (4 x 128x64) ; linha1 = poeira 6x32 + pedras 6x16 + fagulha
cr = Image.new('RGBA', (128 * 4, 64), (0, 0, 0, 0))
for i in range(4):
    cr.paste(crack(11 + i * 5), (i * 128, 0))
cr.save(os.path.join(OUT, 'crack.png'), optimize=True)

sh = Image.new('RGBA', (32 * 6, 32 + 16 + 8 + 32), (0, 0, 0, 0))
for i in range(6):
    sh.paste(dust(3 + i * 7), (i * 32, 0))
    sh.paste(rock(100 + i * 13), (i * 32, 32))
sh.paste(spark(), (0, 48))
for i in range(6):
    sh.paste(dust(50 + i * 5, base=(170, 255, 110), shade=(40, 110, 40)), (i * 32, 56))
sh.save(os.path.join(OUT, 'bits.png'), optimize=True)
print('ok', os.listdir(OUT))
