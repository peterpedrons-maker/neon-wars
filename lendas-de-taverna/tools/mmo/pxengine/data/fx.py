#!/usr/bin/env python3
"""Efeitos visuais em pixel art (por codigo): bola de fogo, meteoro, explosao, onda de choque, circulo magico, brasas, flechas, decals.
Tudo desenhado em camadas RGBA no tamanho nativo da cena (400x248)."""
import math, random
from PIL import Image, ImageDraw, ImageChops
import teste_clareira as T
import px2_mobs as M

W, H = T.W, T.H
B4 = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]


def layer(): return Image.new('RGBA', (W, H), (0, 0, 0, 0))


def dither_ellipse(ov, cx, cy, rx, ry, col, a, k=1.0):
    """Disco com borda tracejada (dither) - efeito de fumaca/brilho em pixel art."""
    px = ov.load()
    for y in range(max(0, int(cy - ry) - 1), min(H, int(cy + ry) + 2)):
        for x in range(max(0, int(cx - rx) - 1), min(W, int(cx + rx) + 2)):
            e = math.hypot((x + .5 - cx) / max(rx, .5), (y + .5 - cy) / max(ry, .5))
            if e <= 1:
                th = B4[y & 3][x & 3] / 16
                if e * k < .55 or th > (e - .45) * 1.8: px[x, y] = (col[0], col[1], col[2], a)


def disc(ov, cx, cy, r, col, a=255):
    ImageDraw.Draw(ov).ellipse([cx - r, cy - r, cx + r, cy + r], fill=(col[0], col[1], col[2], a))


def fireball(ov, x, y, r, f, d=(1, 0), tail=10):
    """Bola de fogo: nucleo branco-amarelo, corpo laranja, chamas vermelhas que seguem para tras."""
    dr = ImageDraw.Draw(ov)
    for i in range(tail, 0, -1):
        tx, ty = x - d[0] * i * 1.4, y - d[1] * i * 1.4
        rr = max(1, r * (1 - i / (tail + 3)) + (1 if (i + f) % 3 == 0 else 0))
        col = (200, 48, 16, 220) if i > tail * .6 else (255, 110, 30, 235) if i > tail * .3 else (255, 170, 50, 245)
        dr.ellipse([tx - rr, ty - rr, tx + rr, ty + rr], fill=col)
    dr.ellipse([x - r, y - r, x + r, y + r], fill=(255, 138, 32, 255))
    dr.ellipse([x - r * .65, y - r * .65, x + r * .65, y + r * .65], fill=(255, 214, 90, 255))
    dr.ellipse([x - r * .3, y - r * .3, x + r * .3, y + r * .3], fill=(255, 250, 200, 255))


def meteor(ov, x, y, r, f, d=(-.38, .92)):
    """Meteoro: rocha escura em chamas, cauda longa; d = direcao do movimento (para baixo/esquerda)."""
    dr = ImageDraw.Draw(ov)
    for i in range(22, 0, -1):
        tx, ty = x - d[0] * i * 1.7, y - d[1] * i * 1.7 + math.sin(i * .9 + f) * 1.3
        rr = max(1, r * (1 - i / 26.0) + (1 if (i + f) % 3 == 0 else 0))
        col = (120, 24, 16, 160) if i > 15 else (210, 56, 20, 215) if i > 8 else (255, 140, 40, 240)
        dr.ellipse([tx - rr, ty - rr, tx + rr, ty + rr], fill=col)
    dr.ellipse([x - r - 1, y - r - 1, x + r + 1, y + r + 1], fill=(255, 150, 40, 255))
    dr.ellipse([x - r + 1, y - r + 1, x + r - 1, y + r - 1], fill=(88, 40, 30, 255))
    dr.ellipse([x - r + 2, y - r + 2, x + r - 3, y + r - 3], fill=(150, 72, 46, 255))
    dr.point([x - 1, y - 2], fill=(255, 220, 140, 255))


def explosion(back, front, cx, cy, k, R=18, seed=0):
    """Explosao em 8 quadros (k=0..7): clarao, bola de fogo, onda de choque, faiscas, fumaca."""
    rnd = random.Random(seed)
    dr = ImageDraw.Draw(front)
    if k <= 1:
        rr = R * (.55 + .4 * k)
        disc(front, cx, cy - 4, rr, (255, 255, 230), 255)
        disc(front, cx, cy - 4, rr * .6, (255, 255, 255), 255)
    if 1 <= k <= 5:
        rr = R * (.8 + .12 * k)
        dither_ellipse(front, cx, cy - 6, rr, rr * .8, (255, 120, 30), 235)
        dither_ellipse(front, cx, cy - 6, rr * .65, rr * .55, (255, 190, 60), 245)
        if k <= 3: dither_ellipse(front, cx, cy - 7, rr * .3, rr * .3, (255, 250, 200), 255)
    if k >= 2:
        sm = (60, 40, 40)
        dither_ellipse(front, cx + rnd.uniform(-4, 4), cy - 10 - k * 3, R * (.5 + .08 * k), R * (.4 + .06 * k), sm, max(0, 190 - k * 24))
    # onda de choque no chao
    rx = 8 + k * 6
    a = max(0, 230 - k * 32)
    dr_b = ImageDraw.Draw(back)
    dr_b.ellipse([cx - rx, cy - rx * .45, cx + rx, cy + rx * .45], outline=(255, 235, 200, a), width=2 if k < 4 else 1)
    # faiscas
    for i in range(10):
        ang = rnd.uniform(0, math.tau) + i
        sp = rnd.uniform(5, 13)
        x = cx + math.cos(ang) * sp * (k + .5) * .8
        y = cy - 4 + math.sin(ang) * sp * (k + .5) * .6 + k * k * .9
        if k < 7:
            c = (255, 230, 120, 255) if i % 2 else (255, 140, 40, 255)
            dr.rectangle([x, y, x + 1, y + 1], fill=c)


def magic_circle(ov, cx, cy, rx, ry, rot, a, col=(255, 140, 50)):
    dr = ImageDraw.Draw(ov)
    c = (col[0], col[1], col[2], a)
    for k, f in enumerate((1.0, .8, .45)):
        dr.ellipse([cx - rx * f, cy - ry * f, cx + rx * f, cy + ry * f], outline=c if k != 1 else (col[0], col[1] - 30, col[2], a // 2), width=1)
    # runas: tracos radiais + estrela
    for i in range(12):
        ang = rot + i * math.tau / 12
        x0, y0 = cx + math.cos(ang) * rx * .82, cy + math.sin(ang) * ry * .82
        x1, y1 = cx + math.cos(ang) * rx * .97, cy + math.sin(ang) * ry * .97
        dr.line([x0, y0, x1, y1], fill=c)
    pts = [(cx + math.cos(rot * -1.3 + i * math.tau / 5 * 2) * rx * .75, cy + math.sin(rot * -1.3 + i * math.tau / 5 * 2) * ry * .75) for i in range(6)]
    dr.line(pts, fill=(col[0], col[1], col[2], a // 2))


def embers(ov, cx, cy, f, n=10, spread=14, rise=26, col=((255, 200, 80), (255, 120, 40))):
    for i in range(n):
        t = ((f * .7 + i * 1.7) % 10) / 10.0
        x = cx + math.sin(i * 2.1 + f * .4) * spread * (.4 + t)
        y = cy - t * rise
        ImageDraw.Draw(ov).point([x, y], fill=col[i % 2] + (int(255 * (1 - t)),))


def vignette_top(ov, a):
    """Brilho avermelhado no topo (ceu em chamas)."""
    px = ov.load()
    for y in range(0, 90):
        k = (1 - y / 90.0)
        for x in range(W):
            if B4[y & 3][x & 3] / 16 < k * a / 255.0 * 1.4:
                px[x, y] = (230, 70, 20, int(a * k * .9) + 20)


def flash_img(img):
    o = img.copy(); px = o.load()
    for y in range(o.height):
        for x in range(o.width):
            if px[x, y][3]: px[x, y] = (255, 255, 255, 255)
    return o


def tint_img(img, col, k=.6):
    o = img.copy(); px = o.load()
    for y in range(o.height):
        for x in range(o.width):
            r, g, b, a = px[x, y]
            if a: px[x, y] = (int(r + (col[0] - r) * k), int(g + (col[1] - g) * k), int(b + (col[2] - b) * k), a)
    return o


# ---------------------------------------------------------------- palco (cenario + inimigos)
REACT = [('squash', 0, True), ('squash', 0, False), ('stretch', 3, False), ('air', 7, False), ('air', 10, False), ('air', 7, False),
         ('squash', 0, False), ('idle', 0, False), ('idle', 0, False), ('idle', 0, False)]


class Stage:
    def __init__(self, clear=(70, 105, 340, 222)):
        self.bg, self.wm = T.build_static(); self.cache = {}
        x0, y0, x1, y1 = clear
        self.objs = [o for o in T.objects() if not (x0 < o['x'] + o['img'].width / 2 < x1 and y0 < o['foot'] < y1 + 40 and o['foot'] > y0)]

    def base(self, i):
        im = self.bg.copy()
        ph = (i // 4) % 6
        if ph not in self.cache: self.cache[ph] = T.water_layer(self.wm, ph)
        im.paste(self.cache[ph].convert('RGB'), (0, 0), self.cache[ph])
        for o in self.objs:
            if 'sh' in o: T.shadow(im, *o['sh'])
        return im.convert('RGBA')

    def compose(self, i, back, dyn, front, extra_decals=(), shake=(0, 0)):
        im = self.base(i)
        for (cx, cy, rx, ry, a) in extra_decals:
            ov = layer(); dither_ellipse(ov, cx, cy, rx, ry, (22, 12, 10), a); im = Image.alpha_composite(im, ov)
        im = Image.alpha_composite(im, back)
        for o in sorted(list(self.objs) + dyn, key=lambda o: o['foot']):
            e = o['img'].convert('RGBA')
            x, y = int(o['x']), int(o['y'])
            layer_ = layer(); layer_.paste(e, (x, y)); im = Image.alpha_composite(im, layer_)
        im = Image.alpha_composite(im, front)
        if shake != (0, 0): im = ImageChops.offset(im, shake[0], shake[1])
        return im.convert('RGB')


class Enemy:
    def __init__(self, x, y, pal=M.SLIME):
        self.x0, self.y0, self.pal = x, y, pal
        self.k = None; self.dir = (1, 0); self.burn = 0; self.num = 0; self.dmg = '27'

    def hit(self, d, dmg='27', burn=0):
        self.k = 0; self.dir = d; self.burn = burn; self.dmg = dmg

    def step(self):
        """Retorna (img, x, y, up, flash, num_y) e avanca a reacao."""
        x, y, up, fl, name = self.x0, self.y0, 0, False, 'idle'
        if self.k is not None:
            name, up, fl = REACT[self.k]
            back = min(self.k, 6) * 2.4
            x += self.dir[0] * back; y += self.dir[1] * back * .6
        g, p = M.slime_frame(name, self.pal)
        img = g.render(p)
        if fl: img = flash_img(img)
        k = self.k
        if self.k is not None:
            self.k += 1
            if self.k >= len(REACT): self.k = None
        return img, x, y, up, k


def draw_number(im, x, y, txt='27', col=(255, 224, 74)):
    n = T.number(txt)
    im.paste(n.convert('RGB'), (int(x), int(y)), n)


def arrow(ov, x, y, d, L=9, glow=False, f=0):
    """Flecha em voo: haste, ponta de aco, penas; d = direcao unitaria."""
    dr = ImageDraw.Draw(ov)
    x0, y0 = x - d[0] * L, y - d[1] * L
    if glow:
        for i in range(8):
            t = i / 8.0
            dr.ellipse([x0 + (x - x0) * t - 2, y0 + (y - y0) * t - 2, x0 + (x - x0) * t + 2, y0 + (y - y0) * t + 2], fill=(255, 220, 90, 70))
    dr.line([x0, y0, x, y], fill=(248, 176, 96, 255), width=1)
    dr.rectangle([x - 1, y - 1, x + 1, y + 1], fill=(246, 250, 255, 255))
    dr.point([x + d[0] * 2, y + d[1] * 2], fill=(246, 250, 255, 255))
    px_, py_ = -d[1], d[0]
    for k in (0, 2):
        fx_, fy_ = x0 + d[0] * k, y0 + d[1] * k
        dr.point([fx_ + px_, fy_ + py_], fill=(232, 72, 32, 255)); dr.point([fx_ - px_, fy_ - py_], fill=(232, 72, 32, 255))


def dust(ov, x, y, k, n=5):
    for i in range(n):
        a = i * 1.3 + .7
        r = 2 + k * 2
        ImageDraw.Draw(ov).rectangle([x + math.cos(a) * r, y + math.sin(a) * r * .5 - k, x + math.cos(a) * r + 1, y + math.sin(a) * r * .5 - k + 1], fill=(210, 190, 150, max(0, 220 - k * 55)))


def aura(ov, cx, cy, f, k, col=(255, 64, 40), h=22):
    """Aura vermelha pulsante em volta do corpo (k 0..1 = intensidade): halo tracejado + chamas subindo."""
    pulse = .5 + .5 * math.sin(f * .8)
    r = 13 + 6 * k + pulse * 2
    dither_ellipse(ov, cx, cy, r, h + 4 * k + pulse * 2, col, int(55 + 70 * k))
    dither_ellipse(ov, cx, cy, r * .66, (h + 2) * .85, (255, 130, 60), int(40 + 80 * k * (.6 + .4 * pulse)))
    dr = ImageDraw.Draw(ov)
    rnd = random.Random(7)
    for i in range(int(6 + 8 * k)):
        a = i * 2.4 + rnd.random() * 2
        t = ((f * .9 + i * 1.9) % 12) / 12.0
        x = cx + math.cos(a) * r * (.6 + .5 * (1 - t)) * (1 if i % 2 else -1) * .8
        y = cy + h * .7 - t * (h * 1.7)
        c = (255, 90 + int(120 * t), 40, int(255 * (1 - t)))
        dr.rectangle([x, y, x + 1, y + 2 if t < .5 else y + 1], fill=c)


def converge(ov, tx, ty, f, k, n=10, R=30, col=(255, 150, 60)):
    """Particulas de energia convergindo para o orbe."""
    rnd = random.Random(3)
    for i in range(n):
        a = rnd.uniform(0, math.tau); r0 = R * rnd.uniform(.7, 1.1)
        t = ((f * .6 + i * 1.3) % 8) / 8.0
        x = tx + math.cos(a) * r0 * (1 - t); y = ty + math.sin(a) * r0 * (1 - t) * .8
        ImageDraw.Draw(ov).rectangle([x, y, x + 1, y + 1], fill=col + (int(60 + 195 * t * k),))
