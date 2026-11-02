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


# ======================================================================
# tex.png: texturas BRANCAS (tingidas em tempo real pelo jogo) feitas com numpy + scipy + PIL
#   fumaça/névoa 6x64 | cortes em meia-lua 4x96x48 | anéis de choque 4x96x48 | explosões 4x64 | círculos mágicos 2x128x64
# ======================================================================
from scipy.ndimage import gaussian_filter, map_coordinates


def fbm(S, seed, oct=5):
    rs = np.random.RandomState(seed)
    out = np.zeros((S, S), 'float32')
    amp = 1.0
    tot = 0
    for o in range(oct):
        n = gaussian_filter(rs.rand(S, S).astype('float32'), sigma=S / (4 * 2 ** o), mode='wrap')
        n = (n - n.min()) / (n.max() - n.min() + 1e-6)
        out += n * amp
        tot += amp
        amp *= .55
    return out / tot


def to_rgba(alpha, shade=None):
    a = np.clip(alpha, 0, 1)
    v = np.ones_like(a) if shade is None else np.clip(shade, 0, 1)
    return Image.fromarray((np.dstack([v, v, v, a]) * 255).astype('uint8'), 'RGBA')


def wisp(seed, S=64):
    yy, xx = np.mgrid[0:S, 0:S].astype('float32')
    d = np.hypot(xx - S / 2, yy - S / 2) / (S / 2)
    n = fbm(S, seed)
    # domain warp p/ aspecto de fumaça enrolada
    w = fbm(S, seed + 40) * 6
    n2 = map_coordinates(n, [np.clip(yy + (w - 3) * 3, 0, S - 1), np.clip(xx + (w - 3) * 3, 0, S - 1)], order=1)
    a = np.clip((1 - d ** 1.6) * (.35 + n2 * 1.3) - .12, 0, 1)
    a = gaussian_filter(a, .7)
    a = np.clip(a * 1.5, 0, 1)
    sh = .55 + .45 * n2
    return to_rgba(a * .9, sh)


def slash(seed, W=96, H=48):
    r = np.random.RandomState(seed)
    yy, xx = np.mgrid[0:H, 0:W].astype('float32')
    cx, cy = W * .5, H * 1.35
    R = np.hypot((xx - cx) / 1.0, (yy - cy) * 1.0)
    ang = np.arctan2(cy - yy, xx - cx)  # 0..pi na parte de cima
    mid = 44 + 2 * r.rand()
    th = 7 * np.sin(np.clip((ang - .25) / (np.pi - .5), 0, 1) * np.pi) ** .8
    a = np.clip(1 - np.abs(R - mid) / np.maximum(th, .5), 0, 1)
    a *= ((ang > .25) & (ang < np.pi - .25)).astype('float32')
    streak = .6 + .4 * np.sin(R * 1.7 + r.rand() * 6) * np.sin(ang * 23 + r.rand() * 6)
    a = a * np.clip(streak + .25, 0, 1)
    a = gaussian_filter(a, .6) * 1.25
    core = np.clip(1 - np.abs(R - mid) / np.maximum(th * .35, .4), 0, 1)
    sh = np.clip(.65 + core * .5, 0, 1)
    return to_rgba(a, sh)


def shock(seed, W=96, H=48):
    r = np.random.RandomState(seed)
    yy, xx = np.mgrid[0:H, 0:W].astype('float32')
    d = np.hypot((xx - W / 2) / (W / 2), (yy - H / 2) / (H / 2))
    ang = np.arctan2(yy - H / 2, xx - W / 2)
    wob = .03 * np.sin(ang * (5 + seed % 4) + seed) + .02 * np.sin(ang * 13 + seed * 2)
    ring = np.exp(-((d - .86 - wob) / .06) ** 2)
    inner = .35 * np.exp(-((d - .72 - wob) / .1) ** 2) * (.6 + .4 * np.sin(ang * 17 + seed))
    fade = np.clip(1 - np.maximum(d - .92, 0) * 8, 0, 1)
    a = np.clip(ring + inner, 0, 1) * fade
    a = gaussian_filter(a, .6)
    return to_rgba(np.clip(a * 1.2, 0, 1), np.clip(.6 + ring * .6, 0, 1))


def burst(seed, S=64):
    r = np.random.RandomState(seed)
    yy, xx = np.mgrid[0:S, 0:S].astype('float32')
    dx, dy = xx - S / 2, yy - S / 2
    d = np.hypot(dx, dy) / (S / 2)
    ang = np.arctan2(dy, dx)
    n = 7 + seed % 5
    rays = np.abs(np.sin(ang * n / 2 + seed)) ** 6 + .35 * np.abs(np.sin(ang * n * 1.5 + seed * 2)) ** 10
    a = np.clip(rays * np.clip(1 - d, 0, 1) ** 1.1 * 1.5 + np.exp(-(d / .22) ** 2) * 1.3, 0, 1) * (d < 1)
    a = gaussian_filter(a, .5)
    return to_rgba(np.clip(a * 1.1, 0, 1), np.clip(.6 + np.exp(-(d / .3) ** 2), 0, 1))


def circle(seed, W=128, H=64):
    r = np.random.RandomState(seed)
    big = Image.new('L', (W * 4, H * 4), 0)
    dr = ImageDraw.Draw(big)
    cx, cy = W * 2, H * 2
    rx, ry = W * 2 - 8, H * 2 - 8
    for k, f in enumerate([1, .86, .5]):
        dr.ellipse([cx - rx * f, cy - ry * f, cx + rx * f, cy + ry * f], outline=255, width=7 if k == 0 else 4)
    n = 12 + seed * 4
    for i in range(n):
        a = i / n * 6.283
        r0, r1 = (.86, 1.0) if i % 2 == 0 else (.9, .97)
        dr.line([(cx + math.cos(a) * rx * r0, cy + math.sin(a) * ry * r0), (cx + math.cos(a) * rx * r1, cy + math.sin(a) * ry * r1)], fill=255, width=5)
    # glifos: pequenos arcos/pontos entre os anéis
    for i in range(n):
        a = (i + .5) / n * 6.283
        rr = .93
        x, y = cx + math.cos(a) * rx * rr, cy + math.sin(a) * ry * rr
        if i % 3 == 0:
            dr.ellipse([x - 5, y - 4, x + 5, y + 4], fill=255)
        else:
            dr.line([(x - 6, y), (x + 6, y + 3), (x + 2, y - 6)], fill=255, width=3)
    # estrela/triângulo interno
    m = 3 + seed
    pts = [(cx + math.cos(i * 6.283 * (2 if m == 5 else 1) / m - 1.57) * rx * .62, cy + math.sin(i * 6.283 * (2 if m == 5 else 1) / m - 1.57) * ry * .62) for i in range(m + 1)]
    dr.line(pts, fill=255, width=5)
    im = big.resize((W, H), Image.LANCZOS)
    a = np.asarray(im).astype('float32') / 255
    return to_rgba(a * 1.15, np.clip(.7 + a * .4, 0, 1))


TW, TH = 384, 64 + 48 + 48 + 64 + 64
tx = Image.new('RGBA', (TW, TH), (0, 0, 0, 0))
for i in range(6):
    tx.paste(wisp(5 + i * 11), (i * 64, 0))
for i in range(4):
    tx.paste(slash(3 + i * 7), (i * 96, 64))
    tx.paste(shock(2 + i * 5), (i * 96, 112))
    tx.paste(burst(4 + i * 3), (i * 64, 160))
for i in range(2):
    tx.paste(circle(i), (i * 128, 224))
tx.save(os.path.join(OUT, 'tex.png'), optimize=True)
print('tex ok')
