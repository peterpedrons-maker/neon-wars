#!/usr/bin/env python3
"""Mockup no FORMATO REAL DO JOGO (RPG de celular em pe, camera de cima, HUD do jogo): Rei Esquecido vs heroi, 5 habilidades.
Nativo 130x282 (x3 = 390x846). Tudo por codigo."""
import math, os, random
from PIL import Image, ImageDraw
import chibi as C
import rei2 as R
from equip_gallery import label
from teste_clareira import OUT

NW, NH = 130, 282
SC = 3
APP = dict(cls='warrior', hat='helm', outfit='mail', metal='aco', clothes='aco', weapon='espada_aco')


def A(view, kind): return [f[0] for f in C.anim(view, kind, 'warrior', None, APP)]


HERO = {'idle': {v: A(v, 'idle') for v in ('up', 'down', 'right')}, 'walk': {v: A(v, 'walk') for v in ('up', 'down', 'right')}, 'atk': A('up', 'attack')}
BOSS_FEET = (66, 150)
FLOOR_Y0, FLOOR_Y1 = 62, 262


def flip(im): return im.transpose(Image.FLIP_LEFT_RIGHT)


def bg(f):
    im = Image.new('RGBA', (NW, NH), (18, 14, 28, 255)); d = ImageDraw.Draw(im)
    for y in range(FLOOR_Y0, FLOOR_Y1, 10):                      # piso de pedra (visto de cima)
        for x in range(((y // 10) % 2) * 9 - 18, NW, 18):
            tone = (36 + ((x * 7 + y * 13) % 9), 32 + ((x * 5 + y * 3) % 7), 50 + ((x + y) % 8))
            d.rectangle([x, y, x + 16, y + 8], fill=tone)
            d.line([x, y + 9, x + 17, y + 9], fill=(20, 16, 32)); d.line([x + 17, y, x + 17, y + 9], fill=(20, 16, 32))
    cx, cy = 65, 180                                               # circulo ritual
    d.ellipse([cx - 52, cy - 36, cx + 52, cy + 36], outline=(72, 52, 110)); d.ellipse([cx - 44, cy - 30, cx + 44, cy + 30], outline=(52, 38, 84))
    for k in range(8):
        a = k * math.pi / 4 + .2; d.line([cx + math.cos(a) * 36, cy + math.sin(a) * 25, cx + math.cos(a) * 44, cy + math.sin(a) * 30], fill=(96, 64, 150))
    d.rectangle([0, 0, NW, FLOOR_Y0 - 1], fill=(28, 24, 44))      # parede do fundo com arcos
    for x in range(-6, NW, 34):
        d.rectangle([x + 6, 26, x + 28, FLOOR_Y0 - 1], fill=(14, 10, 24)); d.ellipse([x + 6, 18, x + 28, 36], fill=(14, 10, 24))
        d.line([x, 14, x, FLOOR_Y0], fill=(46, 40, 66))
    for tx in (22, 66, 108):
        fl = 2 + int(2 * math.sin(f * .9 + tx))
        d.rectangle([tx - 1, 44, tx + 1, 52], fill=(80, 56, 34))
        d.ellipse([tx - 3, 37 - fl // 2, tx + 3, 45], fill=(255, 150, 50)); d.ellipse([tx - 1, 39, tx + 1, 44], fill=(255, 235, 140))
    for px in (4, 126):                                            # pilares laterais
        d.rectangle([px - 4, FLOOR_Y0, px + 4, FLOOR_Y1], fill=(24, 20, 38)); d.line([px - 4, FLOOR_Y0, px - 4, FLOOR_Y1], fill=(50, 44, 72))
    d.rectangle([0, FLOOR_Y1, NW, NH], fill=(12, 8, 20))
    return im


def paste_center(im, spr, feet):
    bb = spr.getbbox()
    if not bb: return
    c = spr.crop(bb)
    im.alpha_composite(c, (int(feet[0] - c.width // 2), int(feet[1] - c.height)))


def paste_feet(im, spr, feet, anchor=(36, 38)):
    """posiciona sprite do heroi/chefe pelo ponto dos pes (anchor no canvas do sprite)"""
    im.alpha_composite(spr, (int(feet[0] - anchor[0]), int(feet[1] - anchor[1])))


def tint(img, col, k):
    a = img.split()[3]; out = Image.blend(img, Image.new('RGBA', img.size, col + (255,)), k); out.putalpha(a); return out


def shadow(im, x, y, rx, ry, a=95):
    ov = Image.new('RGBA', im.size, (0, 0, 0, 0)); ImageDraw.Draw(ov).ellipse([x - rx, y - ry, x + rx, y + ry], fill=(0, 0, 0, a)); im.alpha_composite(ov)


def disc(ov, x, y, r, col, a=255): ImageDraw.Draw(ov).ellipse([x - r, y - r, x + r, y + r], fill=col + (a,))


def ring(ov, x, y, rx, ry, col, a=255, dash=3):
    d = ImageDraw.Draw(ov)
    for k in range(0, 360, 5):
        if (k // 5) % dash == 0: continue
        d.point([x + math.cos(math.radians(k)) * rx, y + math.sin(math.radians(k)) * ry], fill=col + (a,))


def telegraph(ov, x, y, r, k=1.0, a=170):
    """circulo de aviso vermelho com rachaduras e anel dourado (como no jogo)"""
    d = ImageDraw.Draw(ov); ry = r * .5
    d.ellipse([x - r, y - ry, x + r, y + ry], fill=(230, 40, 50, int(a * .28)))
    ring(ov, x, y, r, ry, (255, 70, 70), a, 1); ring(ov, x, y, r * .72, ry * .72, (230, 190, 90), a, 2)
    for c in range(6):
        ang = c * 1.05 + .3; d.line([x, y, x + math.cos(ang) * r * .7 * k, y + math.sin(ang) * ry * .7 * k], fill=(255, 200, 120, int(a * .8)))


class St:
    def __init__(s):
        s.hp = 1.0; s.bhp = 1.0; s.hx, s.hy = 52.0, 232.0; s.view = 'up'; s.flipx = False; s.moving = False; s.wf = 0
        s.hurt = 0; s.tint = None; s.dark = 0.0; s.forgot = 0.0; s.bflash = 0; s.msgs = ['[Sistema] Arena do Chefe: so voce e o chefe.', '[Aviso] Rei Esquecido chegou!']
        s.ghost = None; s.shake = (0, 0); s.atk = None; s.bjitter = 0


def hero_sprite(st, f):
    v = st.view
    if st.atk is not None:
        img = HERO['atk'][st.atk]
    elif st.moving:
        vv = 'right' if v in ('left', 'right') else v
        img = HERO['walk'][vv][st.wf % 8]
        if v == 'left': img = flip(img)
    else:
        vv = 'right' if v in ('left', 'right') else v
        img = HERO['idle'][vv][(f // 2) % 6]
        if v == 'left': img = flip(img)
    if st.tint: img = tint(img, st.tint[0], st.tint[1])
    if st.hurt > 0 and st.hurt % 2: img = tint(img, (255, 255, 255), .85)
    return img


def hud(im, st, channel):
    d = ImageDraw.Draw(im)
    label(im, (NW // 2, 2), 'REI ESQUECIDO', (255, 230, 180), center=True)
    d.rectangle([3, 11, NW - 4, 17], fill=(14, 8, 16), outline=(150, 110, 60)); d.rectangle([4, 12, 4 + int((NW - 9) * st.bhp), 16], fill=(205, 40, 40)); d.line([4, 12, NW - 5, 12], fill=(255, 120, 100))
    d.rectangle([3, 21, 56, 39], fill=(18, 12, 28), outline=(150, 110, 60)); d.rectangle([5, 23, 18, 36], fill=(60, 30, 30), outline=(200, 160, 80))
    hs = HERO['idle']['down'][0].crop((20, 6, 52, 26)).resize((13, 13), Image.NEAREST); im.alpha_composite(hs, (5, 23))
    label(im, (22, 22), 'TESTE', (255, 240, 210))
    d.rectangle([21, 31, 54, 35], fill=(40, 10, 14), outline=(120, 60, 50)); d.rectangle([22, 32, 22 + int(31 * st.hp), 34], fill=(210, 50, 50))
    d.rectangle([96, 21, 126, 56], fill=(14, 12, 24), outline=(190, 150, 70))                      # minimapa
    for (x0, y0, x1, y1) in ((100, 26, 122, 32), (104, 34, 118, 52)): d.rectangle([x0, y0, x1, y1], fill=(36, 30, 56))
    d.point([110 + int((st.hx - 65) / 10), 44], fill=(255, 220, 90))
    d.ellipse([64, 29, 66, 31], fill=(190, 60, 255)) if False else None
    d.point([111, 30], fill=(190, 70, 255)); d.point([112, 30], fill=(190, 70, 255))
    # joystick
    d.ellipse([8, 232, 36, 260], outline=(150, 120, 70), fill=(24, 18, 30)); d.ellipse([16, 240, 28, 252], fill=(210, 170, 80))
    # barra de habilidades
    for i in range(6):
        x = 38 + i * 15
        d.rectangle([x, 262, x + 13, 276], fill=(20, 14, 28), outline=(200, 160, 80) if i in (0, 4, 5) else (110, 90, 60))
    d.rectangle([40, 264, 49, 274], fill=(60, 66, 90)); d.line([44, 265, 44, 272], fill=(220, 230, 250))              # espada
    label(im, (53, 264), '2', (170, 150, 120)); label(im, (68, 264), '3', (170, 150, 120))
    d.ellipse([83, 266, 91, 274], fill=(210, 40, 70)); d.rectangle([85, 263, 89, 266], fill=(230, 200, 160))
    d.rectangle([100, 265, 108, 273], fill=(120, 220, 255))
    for i, m in enumerate(st.msgs[-2:]): label(im, (3, 242 + i * 9 - 2) if False else (38, 250 + i * 0), '', (0, 0, 0))
    m = st.msgs[-1]; label(im, (40, 249), m[:16], (230, 220, 190) if 'Aviso' not in m else (255, 190, 120))
    if channel:
        name, k = channel
        d.rectangle([BOSS_FEET[0] - 25, 63, BOSS_FEET[0] + 24, 68], fill=(18, 10, 30), outline=(190, 120, 255)); d.rectangle([BOSS_FEET[0] - 24, 64, BOSS_FEET[0] - 24 + int(48 * k), 67], fill=(200, 120, 255))
        label(im, (BOSS_FEET[0], 52), name.upper(), (235, 205, 255), center=True)
    if st.forgot > 0:
        label(im, (int(st.hx), int(st.hy) - 56), '?', (200, 160, 255), center=True)
        for i in range(3):
            c = (90, 80, 120) if st.forgot > .5 else (200, 180, 255)
            d.rectangle([int(st.hx) - 12 + i * 8, int(st.hy) - 48, int(st.hx) - 7 + i * 8, int(st.hy) - 43], fill=c, outline=(40, 30, 60))


def frame(f, st, bpose, back=None, front=None, channel=None, extra=None):
    im = bg(f)
    shadow(im, st.hx, st.hy + 1, 11, 3); shadow(im, BOSS_FEET[0], BOSS_FEET[1] + 1, 24, 6, 110)
    if back: back(im)
    if extra: extra(im)
    bs = R.boss(bpose)
    if st.bflash > 0 and st.bflash % 2: bs = tint(bs, (255, 255, 255), .6)
    paste_feet(im, bs, (BOSS_FEET[0] + st.bjitter, BOSS_FEET[1] - 4), anchor=(R.BW // 2, 96))
    paste_feet(im, hero_sprite(st, f), (st.hx, st.hy))
    if front: front(im)
    if st.dark > 0:
        ov = Image.new('RGBA', (NW, NH), (4, 2, 12, 255)); m = Image.new('L', (NW, NH), int(238 * st.dark)); d = ImageDraw.Draw(m)
        for k in range(5):
            rr = 18 + k * 9
            d.ellipse([st.hx - rr, st.hy - 16 - rr * .8, st.hx + rr, st.hy - 16 + rr * .8], fill=int(238 * st.dark * (k + 1) / 5.5) if k > 0 else 0)
        ov.putalpha(m); im.alpha_composite(ov)
        d2 = ImageDraw.Draw(im)
        for sgn in (-1, 1):
            d2.rectangle([BOSS_FEET[0] + sgn * 4 - 1, BOSS_FEET[1] - 66, BOSS_FEET[0] + sgn * 4, BOSS_FEET[1] - 65], fill=(190, 90, 255))
    hud(im, st, channel)
    if st.shake != (0, 0):
        sh = Image.new('RGBA', (NW, NH), (0, 0, 0, 255)); sh.alpha_composite(im, st.shake); im = sh
    return im


def run():
    random.seed(11)
    frames = []; st = St(); fi = [0]

    def emit(bpose, **kw):
        im = frame(fi[0], st, bpose, **kw); frames.append(im); fi[0] += 1
        if st.hurt > 0: st.hurt -= 1
        if st.bflash > 0: st.bflash -= 1
        st.shake = (0, 0)

    def walk_to(tx, ty, steps, bp=None, **kw):
        sx, sy = st.hx, st.hy
        dx, dy = tx - sx, ty - sy
        st.moving = True
        st.view = 'right' if dx > 4 else ('left' if dx < -4 else ('up' if dy < 0 else 'down'))
        for i in range(steps):
            u = (i + 1) / steps; st.hx = sx + dx * u; st.hy = sy + dy * u; st.wf += 1
            emit(bp(i) if callable(bp) else (bp or R.POSE['idle'](i)), **kw)
        st.moving = False; st.view = 'up'

    def idle(n):
        for i in range(n): emit(R.POSE['idle'](i + fi[0]))

    def hero_attack():
        st.view = 'up'
        for k in (1, 2, 3, 4, 5, 6, 7, 8):
            st.atk = k
            if k == 5: st.bflash = 3; st.bhp = max(.05, st.bhp - .02); st.bjitter = 0
            emit(R.POSE['idle'](k + fi[0]))
        st.atk = None

    def channel(name, n=10):
        for i in range(n):
            k = (i + 1) / n
            emit(R.POSE['windup'](k), channel=(name, k))

    def msg(t): st.msgs.append(t)

    st.hx, st.hy = 50, 236
    walk_to(60, 200, 8)
    hero_attack(); idle(3)
    # ===== 1 ESQUECIMENTO =====
    msg('[Aviso] Esquecimento!'); channel('Esquecimento')
    for i in range(18):
        t = i / 17
        def back(im, t=t):
            ov = Image.new('RGBA', (NW, NH), (0, 0, 0, 0))
            for k in range(4):
                rr = 6 + t * 120 - k * 11
                if rr > 0: ring(ov, BOSS_FEET[0], BOSS_FEET[1], rr, rr * .5, (150 + k * 20, 70, 220), 230 - k * 40, 2)
            for j in range(28):
                a = j * .23 + t * 4; r_ = t * 110 * (.4 + (j % 6) / 7)
                disc(ov, BOSS_FEET[0] + math.cos(a) * r_, BOSS_FEET[1] + math.sin(a) * r_ * .5, 1, (120, 60, 200), 150)
            im.alpha_composite(ov)
        if t > .7 and st.forgot == 0: st.forgot = .2; st.tint = ((150, 130, 200), .45)
        if t > .9: st.forgot = 1.0
        emit(R.POSE['cast'](1), back=back)
    idle(8); st.tint = None; st.forgot = 0
    # ===== 2 ECO =====
    msg('[Aviso] Eco!'); channel('Eco', 9)
    for i in range(26):
        def extra(im, i=i):
            if i > 2:
                for dx_ in (-40, 40):
                    g = R.boss(R.POSE['cast'](1)); a = g.split()[3].point(lambda v: 105 if v else 0)
                    g2 = tint(g, (120, 200, 255), .6); g2.putalpha(a); paste_feet(im, g2, (BOSS_FEET[0] + dx_, BOSS_FEET[1] + 6 - 4), anchor=(R.BW // 2, 96))
        def front(im, i=i):
            ov = Image.new('RGBA', (NW, NH), (0, 0, 0, 0))
            for n_, (sx, t0) in enumerate(((BOSS_FEET[0] - 40, 6), (BOSS_FEET[0] + 40, 9), (BOSS_FEET[0], 12))):
                if i >= t0:
                    u = min(1, (i - t0) / 7.0); sy = BOSS_FEET[1] - 30
                    x = sx + (st.hx - sx) * u; y = sy + (st.hy - 18 - sy) * u
                    for tr in range(1, 5): disc(ov, x - (st.hx - sx) * .04 * tr, y - (st.hy - 18 - sy) * .04 * tr, 3 - tr // 2, (150, 70, 230), 130 - tr * 25)
                    disc(ov, x, y, 4, (180, 90, 255), 235); disc(ov, x, y, 2, (255, 255, 255), 255)
                    if u >= 1 and i - t0 == 7: st.hurt = 5; st.hp = max(.2, st.hp - .07)
            im.alpha_composite(ov)
            if st.hurt: label(im, (int(st.hx) + 4, int(st.hy) - 56 - (5 - st.hurt) * 2), str(41 + i), (255, 224, 74), center=True)
        emit(R.POSE['cast'](1), front=front, extra=extra)
    idle(6)
    # ===== 3 FENDA DO VAZIO ===== (heroi desvia)
    msg('[Aviso] Fenda do Vazio!'); channel('Fenda do Vazio', 10)
    spot = (st.hx, st.hy)
    for i in range(30):
        if i == 6: pass
        def back(im, i=i, spot=spot):
            ov = Image.new('RGBA', (NW, NH), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
            if i < 11: telegraph(ov, spot[0], spot[1] + 2, 20 + 2 * math.sin(i * 1.4), 1.0 if i > 4 else i / 5)
            elif i < 25:
                k = min(1, (i - 11) / 3.0) if i < 22 else max(0, (25 - i) / 3.0)
                rx, ry = 22 * k, 11 * k
                d.ellipse([spot[0] - rx - 2, spot[1] - ry - 1, spot[0] + rx + 2, spot[1] + ry + 1], fill=(190, 90, 255, 255))
                d.ellipse([spot[0] - rx, spot[1] - ry, spot[0] + rx, spot[1] + ry], fill=(6, 2, 14, 255))
                for c_ in range(6):
                    a_ = c_ * 1.1 + .3; d.line([spot[0], spot[1], spot[0] + math.cos(a_) * (rx + 14) * k, spot[1] + math.sin(a_) * (ry + 7) * k], fill=(150, 70, 220, 255))
                for j in range(16):
                    a_ = j * .45 + i * .4; r_ = max(2, 40 - ((i * 3 + j * 4) % 40))
                    disc(ov, spot[0] + math.cos(a_) * r_, spot[1] + math.sin(a_) * r_ * .5, 1, (210, 150, 255), 220)
            im.alpha_composite(ov)
        if i == 4:
            st.moving = True; st.view = 'right'
        if 4 <= i <= 12:
            st.hx = spot[0] + (i - 4) * 4.5; st.wf += 1
            if i == 12: st.moving = False; st.view = 'up'
        if i == 14: st.shake = (1, 1)
        emit(R.POSE['cast'](1) if i < 13 else R.POSE['slam']((i - 13) / 6), back=back)
    idle(4)
    # ===== 4 COROA DE ALMAS =====
    msg('[Aviso] Coroa de Almas!'); channel('Coroa de Almas', 10)
    for n_ in range(5): setattr(st, 'h%d' % n_, 0)
    for i in range(28):
        def front(im, i=i):
            ov = Image.new('RGBA', (NW, NH), (0, 0, 0, 0)); cx0, cy0 = BOSS_FEET[0], BOSS_FEET[1] - 74
            for n_ in range(5):
                a_ = n_ * 2 * math.pi / 5 + i * .35
                if i < 12: r_ = 12 + 1.5 * i; x = cx0 + math.cos(a_) * r_; y = cy0 + math.sin(a_) * r_ * .45
                else:
                    u = max(0, min(1, (i - 12 - n_ * 1.5) / 8))
                    x0 = cx0 + math.cos(a_) * 28; y0 = cy0 + math.sin(a_) * 12
                    mx = (x0 + st.hx) / 2 + (n_ - 2) * 8; my = (y0 + st.hy) / 2
                    x = (1 - u) ** 2 * x0 + 2 * (1 - u) * u * mx + u * u * st.hx; y = (1 - u) ** 2 * y0 + 2 * (1 - u) * u * my + u * u * (st.hy - 18)
                    if u >= 1 and not getattr(st, 'h%d' % n_): setattr(st, 'h%d' % n_, 1); st.hurt = 4; st.hp = max(.1, st.hp - .04)
                    if u >= 1: continue
                for tr in range(1, 4): disc(ov, x - tr * 2, y + tr, 3 - tr // 2, (80, 170, 255), 120 - tr * 30)
                disc(ov, x, y, 4, (90, 190, 255), 230); disc(ov, x, y, 2, (255, 255, 255), 255)
            im.alpha_composite(ov)
            if st.hurt: label(im, (int(st.hx) + 3, int(st.hy) - 56 - (4 - st.hurt) * 2), '31', (160, 220, 255), center=True)
        emit(R.POSE['cast'](1), front=front)
    idle(5)
    # ===== 5 TREVAS =====
    msg('[Aviso] Trevas!'); channel('Trevas', 10)
    for i in range(32):
        st.dark = (i / 8 * .9) if i < 8 else (.9 if i < 24 else max(0, .9 - (i - 24) / 8 * .9))
        def back(im, i=i):
            ov = Image.new('RGBA', (NW, NH), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
            if 6 <= i <= 26:
                for k in range(7):
                    pts = []
                    for s in range(0, 22):
                        u = s / 21; x = BOSS_FEET[0] + (st.hx - BOSS_FEET[0]) * u; y = BOSS_FEET[1] + (st.hy - BOSS_FEET[1]) * u + math.sin(u * 9 + i * .6 + k) * (3 + k % 3)
                        pts.append((x + (k - 3) * 2, y))
                    n = max(2, int(len(pts) * min(1, (i - 6) / 9)))
                    d.line(pts[:n], fill=(14, 6, 34, 235), width=2); d.line(pts[:n], fill=(120, 60, 200, 170), width=1)
            im.alpha_composite(ov)
        if i == 18: st.hurt = 6; st.hp = max(.05, st.hp - .1); st.shake = (1, 0)
        def front(im, i=i):
            if st.hurt: label(im, (int(st.hx) + 3, int(st.hy) - 56 - (6 - st.hurt) * 2), '64', (200, 150, 255), center=True)
        emit(R.POSE['cast'](1) if i < 26 else R.POSE['idle'](i), back=back, front=front)
    st.dark = 0; idle(8)
    big = [f.convert('RGB').resize((NW * SC, NH * SC), Image.NEAREST) for f in frames]
    p = big[0].quantize(colors=240, method=Image.MEDIANCUT, dither=Image.NONE)
    q = [b.quantize(palette=p, dither=Image.NONE) for b in big]
    q[0].save(os.path.join(OUT, 'rei_rpg_habilidades.gif'), save_all=True, append_images=q[1:], duration=85, loop=0, disposal=1)
    return len(q), big


if __name__ == '__main__':
    n, big = run(); print(n)
    N_ = len(big); sel = [big[min(N_ - 1, int(N_ * q))] for q in (.04, .12, .2, .3, .38, .46, .58, .68, .78, .88)]
    sh = Image.new('RGB', (NW * SC // 2 * 5, NH * SC // 2 * 2))
    for i, b in enumerate(sel): sh.paste(b.resize((NW * SC // 2, NH * SC // 2), Image.NEAREST), ((i % 5) * NW * SC // 2, (i // 5) * NH * SC // 2))
    sh.save(os.path.join(OUT, 'rei_rpg_folha.png'))
