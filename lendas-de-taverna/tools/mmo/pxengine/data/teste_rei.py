#!/usr/bin/env python3
"""Mockup pixel art: Rei Esquecido na Cripta, com as 5 habilidades (por codigo).
Saida: lendas-de-taverna/mmo/proto_pixel/{rei_cripta.gif,rei_cripta.png,rei_poses.png}"""
import os, math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from teste_clareira import (C, blob, outline, limb, sword, hero2, bay, INK, BROWN, vnoise, OUT)

W, H = 400, 248
ARM = [C(c) for c in ['#0f0c18', '#1c1830', '#2c2646', '#453d6a', '#6c6296']]
BONE = [C(c) for c in ['#3a3240', '#78708a', '#b4aec0', '#dcd8e4', '#f4f2f8']]
CAPE = [C(c) for c in ['#120c1c', '#1e1430', '#2c1c46', '#412a62', '#5a3a84']]
ICE = [C(c) for c in ['#2a4a7a', '#4a7ab0', '#80b8e0', '#bfe4f8', '#f0fbff']]
WISP = [C(c) for c in ['#3a1060', '#7a2cc0', '#b060f0', '#e0a0ff', '#ffffff']]
IRON = [C(c) for c in ['#1c1828', '#2e2840', '#463e66', '#6a5f94', '#9488c0']]
SOUL = [C(c) for c in ['#2a5a90', '#5aa0d8', '#a0e0ff', '#e0f8ff', '#ffffff']]
PUR = C('#c060ff')
FONT = ImageFont.load_default(size=8)
BOSS_INK = C('#120c1c')


def ik2(a, b, l1, l2, sign):
    dx, dy = b[0] - a[0], b[1] - a[1]
    d = math.hypot(dx, dy) or 1e-6
    mx = l1 + l2 - .6
    if d > mx:
        k = mx / d; dx, dy = dx * k, dy * k; d = mx; b = (a[0] + dx, a[1] + dy)
    d = max(d, abs(l1 - l2) + .6)
    A = math.acos(max(-1, min(1, (l1 * l1 + d * d - l2 * l2) / (2 * l1 * d))))
    base = math.atan2(dy, dx) + sign * A
    return (a[0] + math.cos(base) * l1, a[1] + math.sin(base) * l1), b


def tri(d, pts, ramp):
    d.polygon(pts, fill=ramp[2])
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    d.line([pts[0], pts[2]], fill=ramp[3])
    d.line([pts[1], pts[2]], fill=ramp[1])


IDLE = dict(dy=0, lean=0, hr=(82, 70), hl=(38, 74), sa=74, bow=0)
POSES = {
    'Esquecimento': (dict(dy=-2, lean=0, hr=(104, 52), hl=(16, 52), sa=-82, bow=-1), dict(dy=2, lean=0, hr=(110, 56), hl=(10, 56), sa=-70, bow=0)),
    'Eco': (dict(dy=-1, lean=-2, hr=(80, 44), hl=(46, 56), sa=-58, bow=0), dict(dy=2, lean=5, hr=(92, 72), hl=(62, 70), sa=38, bow=1)),
    'Fenda do Vazio': (dict(dy=-3, lean=-2, hr=(76, 44), hl=(62, 46), sa=-90, bow=0), dict(dy=5, lean=6, hr=(84, 80), hl=(70, 78), sa=70, bow=2)),
    'Coroa de Almas': (dict(dy=-4, lean=0, hr=(92, 42), hl=(32, 32), sa=-90, bow=-1), dict(dy=-3, lean=0, hr=(94, 40), hl=(30, 28), sa=-90, bow=-1)),
    'Trevas': (dict(dy=2, lean=0, hr=(64, 78), hl=(58, 80), sa=90, bow=3), dict(dy=-2, lean=0, hr=(104, 60), hl=(16, 60), sa=-60, bow=-2)),
}
HURT = dict(dy=1, lean=-5, hr=(72, 72), hl=(40, 70), sa=60, bow=3)


def mix(a, b, t):
    o = {}
    for k in a:
        if isinstance(a[k], tuple): o[k] = (a[k][0] + (b[k][0] - a[k][0]) * t, a[k][1] + (b[k][1] - a[k][1]) * t)
        else: o[k] = a[k] + (b[k] - a[k]) * t
    return o


def ease(t):
    t = max(0, min(1, t)); return t * t * (3 - 2 * t)


def rei(P, f=0, glow=1.0):
    """Sprite do Rei Esquecido. Canvas 128x124, pes em (64,114)."""
    img = Image.new('RGBA', (128, 124), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    dy, lean, bow = int(round(P['dy'])), int(round(P['lean'])), int(round(P['bow']))
    cx = 64
    # capa (atras): poligono com barra rasgada + sombreamento por dobras
    top = 54 + dy
    pts = [(cx - 24 + lean, top), (cx + 24 + lean, top)]
    for i in range(12, -1, -1):
        x = cx - 40 + i * 6.7 + math.sin(f * .5 + i * .9) * 2.2
        y = 111 - ((i * 37) % 9) + math.sin(f * .4 + i) * 1.5
        pts.append((x, y))
    m = Image.new('L', img.size, 0)
    ImageDraw.Draw(m).polygon(pts, fill=255)
    mp = m.load(); px = img.load()
    for y in range(top, 118):
        for x in range(10, 118):
            if mp[x, y]:
                fold = math.sin((x - cx) * .42 + math.sin(y * .1) * 1.5)
                l = .45 + .3 * fold - abs(x - cx) / 90 + (y - top) * -.002 + bay(x, y) * .2
                i = 3 if l > .62 else 2 if l > .34 else 1 if l > .08 else 0
                px[x, y] = CAPE[i]
    # pernas
    for lx in (cx - 8, cx + 8):
        blob(img, lx, 99, 6, 10, ARM, flat=.92, jit=.03)
        blob(img, lx + (1 if lx > cx else -1), 111, 7.5, 3.2, IRON, flat=.7, jit=.03)
        d.rectangle([lx - 4, 102, lx + 4, 103], fill=ARM[1])
        blob(img, lx, 95, 4.5, 3, IRON, jit=.03)  # joelheira
    # saia / tassets
    blob(img, cx + lean * .4, 88 + dy * .5, 18, 7, ARM, flat=.8, jit=.04)
    for k in range(-14, 15, 7):
        d.rectangle([cx + k + lean * .4 - 1, 86 + dy * .5, cx + k + lean * .4 + 1, 94 + dy * .5], fill=ARM[1])
    # torso
    tx = cx + lean * .6
    blob(img, tx, 70 + dy, 18, 19, ARM, flat=.9, jit=.03)
    d.line([tx - 15, 66 + dy, tx + 15, 66 + dy], fill=ARM[1]); d.line([tx - 14, 78 + dy, tx + 14, 78 + dy], fill=ARM[1])
    d.polygon([(tx, 62 + dy), (tx + 4, 68 + dy), (tx, 74 + dy), (tx - 4, 68 + dy)], fill=WISP[1])
    d.polygon([(tx, 64 + dy), (tx + 2, 68 + dy), (tx, 72 + dy), (tx - 2, 68 + dy)], fill=WISP[3])
    d.rectangle([tx - 16, 80 + dy, tx + 16, 81 + dy], fill=C('#5a3a84'))
    d.rectangle([tx - 2, 80 + dy, tx + 2, 82 + dy], fill=WISP[2])
    # ombreiras com espinhos
    for sx in (-1, 1):
        px_ = tx + sx * 21
        blob(img, px_, 57 + dy, 11, 7.5, IRON, flat=.9, jit=.05)
        d.line([px_ - 8, 59 + dy, px_ + 8, 59 + dy], fill=IRON[1])
        for ox, h, w in [(sx * 5, 12, 3), (sx * 10, 7, 2)]:
            tri(d, [(px_ + ox - w, 54 + dy), (px_ + ox + w, 54 + dy), (px_ + ox + sx * 3, 54 + dy - h)], IRON)
    blob(img, tx, 51 + dy, 9, 4, ARM, flat=.9, jit=.03)
    # cabeca (cranio) + coroa
    hy = 40 + dy + bow
    hx = cx + lean
    blob(img, hx, hy, 8.4, 9, BONE, flat=.88, jit=.03)
    blob(img, hx, hy + 8, 6, 3.8, BONE, flat=.9, jit=.03)
    for ex in (-4, 4):
        d.rectangle([hx + ex - 2, hy - 1, hx + ex + 1, hy + 3], fill=C('#1a0a24'))
        gl = WISP[3] if glow > .5 else WISP[1]
        d.rectangle([hx + ex - 1, hy, hx + ex, hy + 2], fill=gl)
        d.point([hx + ex - 1, hy], fill=WISP[4])
    d.polygon([(hx - 1, hy + 4), (hx + 1, hy + 4), (hx, hy + 7)], fill=C('#1a0a24'))
    for k in range(-4, 5):
        d.point([hx + k, hy + 10], fill=C('#1a0a24') if k % 2 else BONE[3])
    d.rectangle([hx - 8, hy - 8, hx + 8, hy - 6], fill=IRON[2])
    d.rectangle([hx - 8, hy - 6, hx + 8, hy - 6], fill=IRON[1])
    for ox, h, gem in [(-7, 9, 1), (-3.5, 14, 1), (0, 19, 1), (3.5, 14, 1), (7, 9, 1)]:
        tri(d, [(hx + ox - 2, hy - 8), (hx + ox + 2, hy - 8), (hx + ox, hy - 8 - h)], IRON)
        d.point([round(hx + ox), round(hy - 8 - h + 1)], fill=WISP[3])
        d.point([round(hx + ox), round(hy - 8 - h)], fill=WISP[4])
    # bracos (IK) + espada
    shR = (tx + 18, 58 + dy); shL = (tx - 18, 58 + dy)
    hr, hl = P['hr'], P['hl']
    eL, hl = ik2(shL, hl, 17, 17, -1)
    eR, hr = ik2(shR, hr, 17, 17, +1)
    limb(img, shL, eL, 5.6, 5.0, ARM); limb(img, eL, hl, 5.0, 4.2, ARM)
    blob(img, eL[0], eL[1], 4.6, 3.8, IRON, jit=.04)
    tip = sword(img, hr, P['sa'], 42, 3.2, .8, ICE, 14, C('#7a4ac8'), C('#2a1a3a'))
    limb(img, shR, eR, 5.6, 5.0, ARM); limb(img, eR, hr, 5.0, 4.2, ARM)
    blob(img, eR[0], eR[1], 4.6, 3.8, IRON, jit=.04)
    blob(img, hr[0], hr[1], 4.4, 4.4, IRON, jit=.04)
    if abs(hl[0] - hr[0]) + abs(hl[1] - hr[1]) < 14:
        pass
    blob(img, hl[0], hl[1], 4.4, 4.4, IRON, jit=.04)
    img = outline(img, BOSS_INK)
    # fiapos roxos da capa (depois do contorno)
    px = img.load()
    for i in range(9):
        x = cx - 38 + i * 9 + math.sin(f * .55 + i * 1.3) * 3
        y = 112 - (i * 5) % 7 - abs(math.sin(f * .45 + i)) * 4
        for k in range(5):
            xx, yy = int(x + math.sin(f * .6 + i + k) * 1.5), int(y - k * 2)
            if 0 <= xx < 128 and 0 <= yy < 124:
                px[xx, yy] = WISP[3 if k < 2 else 2 if k < 4 else 1]
    return img, (hx, hy - 20), tip, hr


def tint(spr, alpha=130):
    o = spr.copy(); p = o.load()
    for y in range(o.size[1]):
        for x in range(o.size[0]):
            r, g, b, a = p[x, y]
            if a:
                l = (r + g + b) / 765
                i = min(4, int(l * 5 + .3))
                c = WISP[i]
                p[x, y] = (c[0], c[1], c[2], alpha)
    return o


# ------------------------------------------------------------------- cripta
def font_text(img, xy, s, col, shadow=INK, center=False):
    d = ImageDraw.Draw(img); d.fontmode = '1'
    x, y = xy
    if center:
        x = x - int(d.textlength(s, font=FONT)) // 2
    for ox, oy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        d.text((x + ox, y + oy), s, font=FONT, fill=shadow)
    d.text((x, y), s, font=FONT, fill=col)


def crypt_bg():
    random.seed(5)
    img = Image.new('RGB', (W, H))
    px = img.load()
    FLOOR_Y = 84
    # parede de tijolos
    for y in range(FLOOR_Y):
        for x in range(W):
            row = y // 8
            bx = (x + (row % 2) * 8) % 16
            by = y % 8
            seed = ((x + (row % 2) * 8) // 16 * 7 + row * 13) % 5
            base = [(52, 50, 72), (58, 56, 80), (46, 44, 66), (62, 58, 84), (50, 48, 70)][seed]
            c = base
            if by == 0 or bx == 0: c = (28, 26, 42)
            elif by == 1 or bx == 1: c = tuple(min(255, v + 14) for v in base)
            elif by == 7: c = tuple(v - 8 for v in base)
            px[x, y] = c
    # piso de lajes
    rng = np.random.RandomState(3)
    for y in range(FLOOR_Y, H):
        for x in range(W):
            row = (y - FLOOR_Y) // 20
            tx = (x + (row % 2) * 12) // 24
            ty = (y - FLOOR_Y) % 20
            tcx = (x + (row % 2) * 12) % 24
            base = [(60, 58, 84), (66, 64, 92), (54, 52, 78), (70, 66, 96)][(tx * 5 + row * 3) % 4]
            c = base
            if ty == 0 or tcx == 0: c = (30, 28, 46)
            elif ty == 1 or tcx == 1: c = tuple(min(255, v + 16) for v in base)
            elif ty == 19 or tcx == 23: c = tuple(v - 10 for v in base)
            if rng.rand() < .012 and c == base: c = tuple(v + 10 for v in base)
            px[x, y] = c
    d = ImageDraw.Draw(img)
    # rachaduras
    for _ in range(9):
        x, y = random.randint(20, W - 20), random.randint(FLOOR_Y + 8, H - 6)
        for k in range(random.randint(8, 18)):
            d.point([x, y], fill=(26, 24, 40)); x += random.choice((-1, 0, 1, 1)); y += random.choice((0, 1, 1))
    # nicho/arco central atras do rei
    d.rectangle([166, 14, 266, FLOOR_Y - 1], fill=(20, 16, 32))
    d.pieslice([166, -8, 266, 52], 180, 360, fill=(20, 16, 32))
    for k in range(8):
        d.arc([164 - k, -10 - k, 268 + k, 54 + k], 180, 360, fill=(80 - k * 3, 72 - k * 3, 108 - k * 3))
    for yy in range(14, FLOOR_Y):
        d.point([165, yy], fill=(86, 80, 116)); d.point([267, yy], fill=(86, 80, 116))
    # tapete/runas do chefe
    return img


def column(h=78):
    s = Image.new('RGBA', (22, h), (0, 0, 0, 0)); p = s.load()
    for y in range(h):
        for x in range(2, 20):
            cap = y < 6 or y > h - 8
            wd = x if not cap else x
            l = 1 - (x - 2) / 17
            c = [(36, 34, 54), (56, 54, 82), (84, 82, 116), (112, 110, 146)][min(3, int(l * 4))]
            if (y % 9 == 8) and not cap: c = (30, 28, 46)
            if y in (0, h - 1) or x in (2, 19): c = (22, 20, 34)
            p[x, y] = (*c, 255)
    d = ImageDraw.Draw(s)
    d.rectangle([0, 0, 21, 5], fill=(92, 90, 124)); d.rectangle([0, 0, 21, 0], fill=(130, 128, 164)); d.rectangle([0, 5, 21, 5], fill=(30, 28, 46))
    d.rectangle([0, h - 8, 21, h - 1], fill=(72, 70, 100)); d.rectangle([0, h - 1, 21, h - 1], fill=(26, 24, 40))
    return s


def torch_flame(f, x, y, img):
    d = ImageDraw.Draw(img)
    fl = [(0, 0), (1, -1), (-1, 0), (0, -2)][f % 4]
    d.rectangle([x - 1, y + 4, x + 1, y + 12], fill=(86, 54, 30)); d.rectangle([x - 3, y + 3, x + 3, y + 4], fill=(150, 150, 170))
    d.polygon([(x - 3, y + 3), (x + 3, y + 3), (x + 2 + fl[0], y - 4 + fl[1]), (x + fl[0], y - 8 + fl[1]), (x - 2 + fl[0], y - 3)], fill=(255, 130, 30))
    d.polygon([(x - 2, y + 3), (x + 2, y + 3), (x + fl[0], y - 4 + fl[1])], fill=(255, 210, 80))
    d.point([x, y + 1], fill=(255, 250, 200))


def lit(bg, f, boss_pulse):
    a = np.asarray(bg).astype('float32')
    yy, xx = np.mgrid[0:H, 0:W].astype('float32')
    bayer = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]], 'float32') / 16 - .5
    bm = np.tile(bayer, (H // 4 + 1, W // 4 + 1))[:H, :W]
    out = a * .46
    def light(cx, cy, r, col, k):
        dd = np.sqrt((xx - cx) ** 2 + ((yy - cy) * 1.3) ** 2)
        I = np.clip(1 - dd / r, 0, 1) ** 1.2 * k
        I = np.floor(I * 6 + bm * .9 + .5) / 6
        return I[..., None] * np.array(col, 'float32')[None, None, :]
    fl = [1.0, .93, 1.05, .9][f % 4]
    for tx in (96, 304):
        out += a * light(tx, 50, 110, (1.4, .9, .5), .95 * fl) * .9
    out += a * light(232, 150, 100 + boss_pulse * 8, (.9, .4, 1.5), .75 + boss_pulse * .1)
    return Image.fromarray(np.clip(out, 0, 255).astype('uint8'))


# ------------------------------------------------------------------- efeitos
def soul_sprite(f):
    s = Image.new('RGBA', (12, 14), (0, 0, 0, 0))
    blob(s, 6, 6, 4.2, 4.6, SOUL, flat=.95, jit=.06, edge=False)
    d = ImageDraw.Draw(s)
    for k in range(4):
        d.point([5 + int(math.sin(f * .8 + k) * 1.5) + (k % 2), 9 + k], fill=SOUL[2 - k // 2])
    d.rectangle([4, 5, 4, 6], fill=INK); d.rectangle([7, 5, 7, 6], fill=INK)
    return outline(s, SOUL[0])


def glow_dot(ov, x, y, r, col, a=200):
    d = ImageDraw.Draw(ov)
    d.ellipse([x - r, y - r, x + r, y + r], fill=(col[0], col[1], col[2], a))


def dither_ellipse(ov, cx, cy, rx, ry, col, a, thick=None):
    px = ov.load()
    for y in range(max(0, int(cy - ry) - 1), min(H, int(cy + ry) + 2)):
        for x in range(max(0, int(cx - rx) - 1), min(W, int(cx + rx) + 2)):
            e = math.hypot((x - cx) / rx, (y - cy) / ry)
            if e <= 1:
                if thick is not None and e < 1 - thick: continue
                k = (e if thick is None else (e - (1 - thick)) / thick)
                if bay(x, y) + .5 < k * 1.0 + .15:
                    px[x, y] = (col[0], col[1], col[2], a)


def main():
    random.seed(9)
    bg = crypt_bg()
    col = column()
    BX, BY = 252, 176
    HX, HY = 128, 204
    ov_cache = {}
    hs = {k: hero2(*k) for k in [('idle', 0), ('idle', 1), ('wind', 0), ('strike', 0), ('recover', 0), ('hop', 0), ('land', 0)]}
    skills = ['Esquecimento', 'Eco', 'Fenda do Vazio', 'Coroa de Almas', 'Trevas']
    timeline = [(None, i) for i in range(6)]
    for s in skills: timeline += [(s, k) for k in range(16)]
    rng = random.Random(4)
    crack_pts = []
    sx, sy = BX + 30, BY + 2
    n = 14
    for i in range(n + 1):
        t = i / n
        crack_pts.append((sx + (HX + 6 - sx) * t + (rng.uniform(-4, 4) if 0 < i < n else 0), sy + (HY - 4 - sy) * t + (rng.uniform(-5, 5) if 0 < i < n else 0)))
    frames = []
    for fi, (skill, k) in enumerate(timeline):
        # pose do chefe
        if skill is None:
            P = mix(IDLE, IDLE, 0); P['dy'] = math.sin(fi * .9) * 1.0
            cast = 0
        else:
            wnd, rel = POSES[skill]
            if k < 6: P = mix(IDLE, wnd, ease(k / 5))
            elif k < 11: P = mix(wnd, rel, ease((k - 6) / 2))
            else: P = mix(rel, IDLE, ease((k - 11) / 4))
            cast = (k + 1) / 6 if k < 6 else 0
        boss, crown, tip, hand = rei(P, fi)
        base = lit(bg, fi, math.sin(fi * .5))
        im = base.convert('RGBA')
        d = ImageDraw.Draw(im)
        for tx in (96, 304): torch_flame(fi, tx, 46, im)
        # runa no chao
        ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
        pulse = .5 + .5 * math.sin(fi * .5)
        od.ellipse([BX - 46, BY - 14, BX + 46, BY + 20], outline=(150, 70, 230, int(110 + 80 * pulse)))
        od.ellipse([BX - 38, BY - 10, BX + 38, BY + 16], outline=(110, 50, 190, 120))
        for a in range(0, 360, 30):
            r = math.radians(a + fi * 3)
            od.point([BX + int(math.cos(r) * 42), BY + 3 + int(math.sin(r) * 15)], fill=(230, 160, 255, 230))
        im = Image.alpha_composite(im, ov)
        # colunas (atras do chefe)
        for cxx in (40, 128, 280, 362):
            im.alpha_composite(col, (cxx - 11, 20))
        # ---------------- efeitos atras do chefe
        ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
        if skill == 'Esquecimento':
            if k < 6:
                rr = 12 + k * 7
                dither_ellipse(ov, BX, BY + 4, rr, rr * .38, (170, 90, 255), 150, .25)
            elif k < 12:
                rr = (k - 5) * 38
                dither_ellipse(ov, BX, BY + 4, rr, rr * .38, (190, 110, 255), 200 - (k - 6) * 20, .18)
                dither_ellipse(ov, BX, BY + 4, max(4, rr - 10), max(2, (rr - 10) * .38), (90, 40, 160), 110, None)
                for g in range(10):
                    gx = BX + math.cos(g * 2.1 + k) * rr * .8; gy = BY + 4 + math.sin(g * 2.1 + k) * rr * .3 - (k - 5) * 3
                    od.rectangle([gx - 1, gy, gx + 1, gy], fill=(240, 200, 255, 230)); od.rectangle([gx, gy - 1, gx, gy + 1], fill=(240, 200, 255, 230))
        if skill == 'Fenda do Vazio' and k >= 6:
            u = min(1, (k - 5) / 4.0)
            m = int(len(crack_pts) * u)
            pts = crack_pts[:max(2, m + 1)]
            fade = 255 if k < 12 else int(255 * (1 - (k - 11) / 4))
            od.line(pts, fill=(170, 70, 240, fade), width=7)
            od.line(pts, fill=(8, 3, 16, fade), width=4)
            if k >= 9:
                ex, ey = HX + 6, HY - 4
                rr = (k - 8) * 7 if k < 12 else max(0, 30 - (k - 11) * 9)
                od.ellipse([ex - rr, ey - rr * .45, ex + rr, ey + rr * .45], fill=(6, 2, 12, 255), outline=(190, 90, 255, 255), width=2)
            for g in range(6):
                gx, gy = crack_pts[min(m, len(crack_pts) - 1)]
                rx_ = gx + rng.uniform(-6, 6); od.rectangle([rx_, gy - (k - 5) * 2 - g, rx_ + 1, gy - (k - 5) * 2 - g + 1], fill=(90, 80, 110, 255))
        im = Image.alpha_composite(im, ov)
        # clones do Eco
        if skill == 'Eco':
            for j, (ox, delay) in enumerate([(-58, 1), (58, 2)]):
                kk = k - delay
                if k < 4: al = 0
                else: al = 150 if k < 13 else int(150 * (1 - (k - 12) / 4))
                if al <= 0: continue
                wnd, rel = POSES['Eco']
                if kk < 6: Pc = mix(IDLE, wnd, ease(kk / 5))
                elif kk < 11: Pc = mix(wnd, rel, ease((kk - 6) / 2))
                else: Pc = mix(rel, IDLE, ease((kk - 11) / 4))
                b2 = tint(rei(Pc, fi)[0], al)
                if j == 0: b2 = b2.transpose(Image.FLIP_LEFT_RIGHT)
                im.alpha_composite(b2, (BX + ox - 64, BY - 114 + (4 if j == 0 else 8)))
        # sombras + chefe + heroi
        sh = Image.new('RGBA', (W, H), (0, 0, 0, 0)); sd = ImageDraw.Draw(sh)
        sd.ellipse([BX - 26, BY - 4, BX + 26, BY + 8], fill=(0, 0, 0, 110))
        # heroi
        if skill in ('Esquecimento', 'Fenda do Vazio', 'Coroa de Almas') and 6 <= k <= 10:
            hk = ('hop', 0) if k in (7, 8, 9) else ('land', 0)
            hy_off = -abs(math.sin((k - 6) / 4 * math.pi)) * 14
            hx_off = (k - 6) * (-5 if skill == 'Fenda do Vazio' else 3)
        elif skill == 'Eco' and k in (9, 10):
            hk = ('hop', 0); hy_off = -10; hx_off = -(k - 8) * 4
        else:
            hk = ('idle', (fi // 4) % 2) if skill != 'Eco' or k < 11 else ('idle', 0); hy_off = 0; hx_off = 0
        if skill is not None and k == 3 and skill == 'Eco': hk = ('wind', 0)
        sd.ellipse([HX - 9 + hx_off, HY - 3, HX + 9 + hx_off, HY + 3], fill=(0, 0, 0, 100 if hy_off == 0 else 60))
        im = Image.alpha_composite(im, sh)
        im.alpha_composite(boss, (BX - 64, BY - 114))
        im.alpha_composite(hs[hk], (int(HX - 18 + hx_off), int(HY - 42 + hy_off)))
        # ---------------- efeitos na frente
        ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
        crown_x, crown_y = BX - 64 + crown[0], BY - 114 + crown[1]
        glowk = 18 + 4 * math.sin(fi * .6)
        dither_ellipse(ov, crown_x, crown_y + 8, glowk, glowk * .6, (190, 100, 255), 130, .5)
        if skill == 'Eco' and 6 <= k <= 10:
            for j, (ox, delay) in enumerate([(-58, 1), (58, 2)]):
                kk = k - delay
                if 6 <= kk <= 9:
                    cxs = BX + ox + (20 if j else -20) * (1 if kk > 6 else .5)
                    for a in range(-70, 40, 4):
                        r = math.radians(a); xs = cxs + math.cos(r) * 30 * (-1 if j == 0 else 1); ys = BY - 56 + math.sin(r) * 34
                        od.rectangle([xs, ys, xs + 1, ys + 1], fill=(235, 190, 255, 230))
            if k >= 8:
                for a in range(-80, 30, 4):
                    r = math.radians(a); od.rectangle([BX + 24 + math.cos(r) * 34, BY - 60 + math.sin(r) * 38, BX + 25 + math.cos(r) * 34, BY - 59 + math.sin(r) * 38], fill=(220, 240, 255, 240))
        if skill == 'Coroa de Almas':
            souls = []
            for i in range(7):
                ang = k * .55 + i * 2 * math.pi / 7
                ox_, oy_ = crown_x + math.cos(ang) * 34, crown_y + 8 + math.sin(ang) * 11
                if k >= 6:
                    u = ease((k - 6) / 4.0)
                    tx_, ty_ = HX + (i - 3) * 3, HY - 22 + (i % 3) * 3
                    ox2 = ox_ + (tx_ - ox_) * u; oy2 = oy_ + (ty_ - oy_) * u - math.sin(u * math.pi) * 22
                    souls.append((ox2, oy2, math.sin(ang)))
                    for tr in range(1, 4):
                        uu = max(0, u - tr * .08)
                        od.rectangle([ox_ + (tx_ - ox_) * uu, oy_ + (ty_ - oy_) * uu - math.sin(uu * math.pi) * 22 + 4, ox_ + (tx_ - ox_) * uu + 1, oy_ + (ty_ - oy_) * uu - math.sin(uu * math.pi) * 22 + 5], fill=(170, 230, 255, 200 - tr * 50))
                else:
                    souls.append((ox_, oy_, math.sin(ang)))
            fadeS = 1.0 if k < 12 else max(0, 1 - (k - 11) / 3)
            ov = Image.alpha_composite(Image.new('RGBA', (W, H), (0, 0, 0, 0)), ov)
            im = Image.alpha_composite(im, ov); ov = Image.new('RGBA', (W, H), (0, 0, 0, 0))
            if fadeS > 0:
                for (sx_, sy_, z) in sorted(souls, key=lambda t: t[2]):
                    ss = soul_sprite(fi + int(sx_))
                    im.alpha_composite(ss, (int(sx_ - 6), int(sy_ - 7)))
        if skill == 'Trevas':
            c = 0
            if k < 6: c = 0
            elif k < 11: c = ease((k - 5) / 4)
            else: c = 1 - ease((k - 11) / 4)
            # nevoa se juntando
            if k < 6:
                for g in range(16):
                    ang = g * .4 + k * .6; rr = 70 - k * 9 + (g % 4) * 8
                    od.rectangle([BX + math.cos(ang) * rr, BY - 40 + math.sin(ang) * rr * .5, BX + math.cos(ang) * rr + 1, BY - 40 + math.sin(ang) * rr * .5 + 1], fill=(190, 110, 255, 220))
            if c > 0:
                px = ov.load()
                R = 40 + (1 - c) * 240
                for y in range(H):
                    for x in range(W):
                        dd = math.hypot(x - HX, (y - HY + 20) * 1.1)
                        if dd > R * .35 + 20:
                            kk = min(1, (dd - (R * .35 + 20)) / 60)
                            a = int(205 * c * kk)
                            if a > 0 and bay(x, y) + .5 < kk + .25 and (x + y) % 2 == 0 or a > 150:
                                px[x, y] = (6, 2, 16, min(235, int(a * 1.1)))
        im = Image.alpha_composite(im, ov)
        # olhos do chefe brilham no escuro (apos escurecer)
        if skill == 'Trevas' and k >= 6:
            ed = ImageDraw.Draw(im)
            for ex in (-4, 4):
                ed.rectangle([crown_x + ex - 1, crown_y + 29, crown_x + ex, crown_y + 31], fill=WISP[3])
        # ---------------- UI
        font_text(im, (W // 2, 6), 'REI ESQUECIDO', (255, 233, 168), center=True)
        d = ImageDraw.Draw(im)
        d.rectangle([W // 2 - 62, 17, W // 2 + 62, 23], fill=INK)
        d.rectangle([W // 2 - 61, 18, W // 2 + 61, 22], fill=(40, 20, 40))
        d.rectangle([W // 2 - 61, 18, W // 2 + 30, 22], fill=(190, 40, 70)); d.rectangle([W // 2 - 61, 18, W // 2 + 30, 19], fill=(240, 100, 120))
        if skill and k < 6:
            bx0, by0 = BX - 28, BY - 140
            d.rectangle([bx0 - 1, by0 - 1, bx0 + 57, by0 + 7], fill=INK)
            d.rectangle([bx0, by0, bx0 + 56, by0 + 6], fill=(34, 20, 56))
            d.rectangle([bx0, by0, bx0 + int(56 * cast), by0 + 6], fill=(176, 96, 240))
            d.rectangle([bx0, by0, bx0 + int(56 * cast), by0 + 1], fill=(240, 190, 255))
            font_text(im, (BX, by0 - 11), skill, (255, 255, 255), center=True)
        frames.append(im.convert('RGB'))
    big = [f.resize((W * 2, H * 2), Image.NEAREST) for f in frames]
    big[4 + 6 + 8].save(os.path.join(OUT, 'rei_cripta.png'))
    pal = big[20].quantize(colors=128, method=Image.MEDIANCUT, dither=Image.NONE)
    q = [im.quantize(palette=pal, dither=Image.NONE) for im in big]
    q[0].save(os.path.join(OUT, 'rei_cripta.gif'), save_all=True, append_images=q[1:], duration=80, loop=0, disposal=1)
    # folha de poses
    ps = Image.new('RGBA', (128 * 6, 124), (60, 40, 80, 255))
    items = [('idle', IDLE)] + [(n, POSES[n][0]) for n in ['Esquecimento', 'Eco', 'Fenda do Vazio', 'Coroa de Almas']] + [('Trevas', POSES['Trevas'][0])]
    for i, (n, P) in enumerate(items):
        ps.alpha_composite(rei(P, 3)[0], (i * 128, 0))
    ps.resize((ps.width * 2, ps.height * 2), Image.NEAREST).convert('RGB').save(os.path.join(OUT, 'rei_poses.png'))
    print('ok', len(frames), 'frames')


if __name__ == '__main__':
    main()
