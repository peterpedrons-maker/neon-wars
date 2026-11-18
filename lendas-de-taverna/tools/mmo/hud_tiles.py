#!/usr/bin/env python3
"""Ícones do menu lateral da HUD (Pers./Habil./Diário/Social/Montar): pack CC0 Idylwild's + dois desenhados por código
(Social e Montar) no mesmo estilo (contorno por forma, 3 tons, luz em cima/esquerda). Saída: mmo/assets/hud/*.png (64x64 = 32 nativos x2)."""
import os, numpy as np
from PIL import Image, ImageFilter
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
SRC = os.path.join(ROOT, 'assets', 'ico_src', 'idylwild')
OUT = os.path.join(ROOT, 'mmo', 'assets', 'hud')
hx = lambda s: tuple(int(s[i:i + 2], 16) for i in (1, 3, 5))


def glow(im, col, r=2, a=.55):
    """brilho colorido em volta do ícone (64x64)"""
    al = np.array(im)[..., 3] > 0
    m = Image.fromarray((al * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(2 * r + 1)).filter(ImageFilter.GaussianBlur(1.6))
    g = np.zeros((*al.shape, 4), np.uint8); g[..., :3] = hx(col); g[..., 3] = (np.array(m) * a).astype(np.uint8)
    out = Image.fromarray(g, 'RGBA'); out.alpha_composite(im); return out


def pack(name):
    im = Image.open(os.path.join(SRC, name + '.png')).convert('RGBA')
    c = Image.new('RGBA', (32, 32), (0, 0, 0, 0)); c.alpha_composite(im, ((32 - im.width) // 2, (32 - im.height) // 2))
    return c


def shape(h, w, fn):
    y, x = np.mgrid[0:h, 0:w] + .5
    return fn(x, y)


def paint(canvas, mask, ramp, light=(-1, -1)):
    """pinta `mask` com rampa [escuro, médio, claro, brilho] e contorno escuro; luz em cima/esquerda"""
    H, W = mask.shape
    edge = mask & ~np.pad(mask, 1)[2:, 1:-1] | mask & ~np.pad(mask, 1)[:-2, 1:-1] | mask & ~np.pad(mask, 1)[1:-1, 2:] | mask & ~np.pad(mask, 1)[1:-1, :-2]
    ys, xs = np.nonzero(mask); cy, cx = ys.mean(), xs.mean(); ext = max(ys.max() - ys.min(), xs.max() - xs.min(), 1) / 2
    k = ((xs - cx) * light[0] + (ys - cy) * light[1]) / (ext * 1.41)      # -1 (sombra) .. 1 (luz)
    for y, x, t in zip(ys, xs, k):
        c = ramp[0] if t < -.45 else ramp[1] if t < .35 else ramp[2] if t < .75 else ramp[3]
        canvas[y, x] = (*hx(c), 255)
    return mask


def outline(canvas, mask, col='#1a1020'):
    pad = np.pad(mask, 1); nb = pad[2:, 1:-1] | pad[:-2, 1:-1] | pad[1:-1, 2:] | pad[1:-1, :-2]
    o = nb & ~mask
    canvas[o] = (*hx(col), 255)


def social():
    cv = np.zeros((32, 32, 4), np.uint8)
    skin = ['#b8764a', '#e0a070', '#f2c496', '#ffe2c0']
    blue = ['#1c3a78', '#2f60b8', '#4a86e0', '#8ab8ff']; red = ['#7a1c24', '#b8303a', '#e05a5a', '#ff9a8a']
    def person(cx, cy, body, hair):
        head = shape(32, 32, lambda x, y: ((x - cx) / 5.2) ** 2 + ((y - cy) / 5.6) ** 2 <= 1)
        torso = shape(32, 32, lambda x, y: (y >= cy + 6) & (y <= 30) & (abs(x - cx) <= 8.2 - np.clip(30 - y, 0, 5) * 0 - np.clip((cy + 9 - y), 0, 4) * .5))
        torso &= shape(32, 32, lambda x, y: ((x - cx) / 8.4) ** 2 + ((y - (cy + 17)) / 11.5) ** 2 <= 1)
        m = head | torso
        outline(cv, m); paint(cv, torso, body); paint(cv, head, skin)
        hr = shape(32, 32, lambda x, y: head[np.clip(y.astype(int), 0, 31), np.clip(x.astype(int), 0, 31)] & (y < cy - 1.8 + np.abs(x - cx) * .35))
        paint(cv, hr, hair)
        for ex in (cx - 2.2, cx + 2.2):                       # olhos
            cv[int(cy + 1), int(ex)] = (*hx('#1a1020'), 255)
        cv[int(cy + 3), int(cx)] = (*hx('#b8503a'), 255)
    person(11, 9, blue, ['#2a1a10', '#4a2e1a', '#6a4426', '#8a6038'])
    person(21, 10, red, ['#7a3a10', '#b8651c', '#e0902c', '#ffc866'])
    return Image.fromarray(cv, 'RGBA')


def ferradura():
    cv = np.zeros((32, 32, 4), np.uint8)
    ring = shape(32, 32, lambda x, y: (((x - 16) / 11.2) ** 2 + ((y - 15) / 12) ** 2 <= 1) & (((x - 16) / 6.2) ** 2 + ((y - 14) / 7) ** 2 >= 1) & ~((y > 20) & (abs(x - 16) < 6.2)))
    outline(cv, ring); paint(cv, ring, ['#4a5262', '#8a94a8', '#c4ccdc', '#f4f8ff'])
    for (x, y) in ((6, 12), (7, 18), (25, 12), (24, 18), (9, 7), (22, 7)):               # furos dos pregos
        cv[y, x] = (*hx('#1a1020'), 255); cv[y, x + 1] = (*hx('#2a3040'), 255)
    cv[6, 12:15] = (*hx('#ffffff'), 255)
    return Image.fromarray(cv, 'RGBA')


def bussola():
    cv = np.zeros((32, 32, 4), np.uint8)
    ring = shape(32, 32, lambda x, y: (((x - 16) / 14) ** 2 + ((y - 16) / 14) ** 2 <= 1) & (((x - 16) / 11) ** 2 + ((y - 16) / 11) ** 2 >= 1))
    face = shape(32, 32, lambda x, y: ((x - 16) / 11) ** 2 + ((y - 16) / 11) ** 2 < 1)
    outline(cv, ring | face); paint(cv, face, ['#2a2236', '#3a3050', '#4a4066', '#5a5080']); paint(cv, ring, ['#6e4a14', '#b8892f', '#e8c868', '#fff0b0'])
    for a in range(0, 360, 45):                                           # marcas
        import math
        r0, r1 = (8.2, 10.2) if a % 90 == 0 else (9, 10)
        for r in np.arange(r0, r1, .5):
            cv[int(16 + math.sin(math.radians(a)) * r), int(16 + math.cos(math.radians(a)) * r)] = (*hx('#e8d8a0'), 255)
    def needle(sign, ramp):                                              # agulha em losango apontando para cima/baixo
        m = shape(32, 32, lambda x, y: (np.abs(x - 16) <= 3.2 * (1 - np.abs(y - 16 + sign * 0) / 9.5)) & (((y < 16) if sign < 0 else (y >= 16))) & (np.abs(y - 16) <= 9.5))
        paint(cv, m, ramp)
    needle(-1, ['#7a1c24', '#b8303a', '#e05a5a', '#ff9a8a']); needle(1, ['#8a94a8', '#b8c0d0', '#dfe6f2', '#ffffff'])
    cv[16, 16] = (*hx('#1a1020'), 255); cv[15, 15] = (*hx('#ffe08a'), 255)
    return Image.fromarray(cv, 'RGBA')


def finish(im32, name, col):
    big = im32.resize((64, 64), Image.NEAREST)
    glow(big, col).save(os.path.join(OUT, name + '.png'))


if __name__ == '__main__':
    finish(pack('platemail_helmet'), 'heroi', '#8ab8ff')
    a = pack('sword3'); b = pack('sword5').transpose(Image.FLIP_LEFT_RIGHT); c = Image.new('RGBA', (32, 32), (0, 0, 0, 0)); c.alpha_composite(b); c.alpha_composite(a)
    finish(c, 'hab', '#ff6a5a')
    finish(pack('rotulus_unfurled'), 'diario', '#ffd070')
    finish(social(), 'social', '#6aa0ff')
    finish(ferradura(), 'montaria', '#7ae08a')
    finish(bussola(), 'atalhos', '#ffd070')
    print('ok')
