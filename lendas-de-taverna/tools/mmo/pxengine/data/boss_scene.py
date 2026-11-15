#!/usr/bin/env python3
"""Mockup: Rei Esquecido (chibi) vs guerreiro, 5 habilidades com barra de canalizacao. Tudo por codigo."""
import math, os, random
from PIL import Image, ImageDraw, ImageChops
import chibi as C
import rei_chibi as R
from equip_gallery import label
from teste_clareira import OUT

NW, NH = 240, 144
HX, HY = 50, 120          # pes do heroi
BX, BY = 178, 118         # pes do chefe
SC = 3
APP = dict(cls='warrior', hat='helm', outfit='mail', metal='aco', clothes='aco', weapon='espada_aco')
HERO = [C.anim('right', 'idle', 'warrior', None, APP)[i][0] for i in range(6)]


def bg(f):
    im = Image.new('RGBA', (NW, NH), (26, 22, 38, 255)); d = ImageDraw.Draw(im)
    for y in range(44, NH, 12):                                  # piso de pedra (tijolos)
        for x in range(((y // 12) % 2) * 12 - 12, NW, 24):
            tone = (38 + ((x * 7 + y * 13) % 9), 33 + ((x * 5 + y * 3) % 7), 52 + ((x + y) % 8))
            d.rectangle([x, y, x + 22, y + 10], fill=tone)
            d.line([x, y + 10, x + 22, y + 10], fill=(22, 18, 34)); d.line([x + 23, y, x + 23, y + 10], fill=(22, 18, 34))
    d.rectangle([0, 0, NW, 43], fill=(30, 26, 46))                # parede do fundo com arcos
    for x in range(0, NW, 40):
        d.rectangle([x + 4, 10, x + 34, 43], fill=(20, 16, 32)); d.ellipse([x + 4, 2, x + 34, 22], fill=(20, 16, 32))
        d.line([x, 0, x, 43], fill=(48, 42, 66))
    for tx in (20, 120, 220):                                     # tochas
        fl = 2 + int(2 * math.sin(f * .9 + tx))
        d.rectangle([tx - 1, 26, tx + 1, 34], fill=(80, 56, 34))
        d.ellipse([tx - 3, 19 - fl // 2, tx + 3, 27], fill=(255, 150, 50)); d.ellipse([tx - 1, 21, tx + 1, 26], fill=(255, 235, 140))
    return im


def paste_center(im, spr, feet, flip=False):
    bb = spr.getbbox()
    if not bb: return
    c = spr.crop(bb)
    if flip: c = c.transpose(Image.FLIP_LEFT_RIGHT)
    im.alpha_composite(c, (feet[0] - c.width // 2, feet[1] - c.height))


def tint(img, col, k):
    a = img.split()[3]
    solid = Image.new('RGBA', img.size, col + (255,))
    out = Image.blend(img, solid, k); out.putalpha(a); return out


def shadow(im, x, y, rx, ry, a=90):
    ov = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    d.ellipse([x - rx, y - ry, x + rx, y + ry], fill=(0, 0, 0, a)); im.alpha_composite(ov)


def disc(ov, x, y, r, col, a=255):
    ImageDraw.Draw(ov).ellipse([x - r, y - r, x + r, y + r], fill=col + (a,))


def ring(ov, x, y, rx, ry, col, a=255, dash=3):
    d = ImageDraw.Draw(ov)
    for k in range(0, 360, 6):
        if (k // 6) % dash == 0: continue
        px = x + math.cos(math.radians(k)) * rx; py = y + math.sin(math.radians(k)) * ry
        d.point([px, py], fill=col + (a,))


def bar(im, x, y, w, frac, col, back=(20, 14, 30)):
    d = ImageDraw.Draw(im)
    d.rectangle([x - 1, y - 1, x + w, y + 3], fill=(10, 6, 18)); d.rectangle([x, y, x + w - 1, y + 2], fill=back)
    d.rectangle([x, y, x + int((w - 1) * frac), y + 2], fill=col)


def dmg(im, x, y, txt, col=(255, 224, 74)):
    label(im, (x, y), txt, col, center=True)


class State:
    def __init__(self):
        self.hurt = 0; self.hero_tint = None; self.hero_dx = 0; self.hero_dy = 0; self.hp = 1.0; self.bhp = 1.0
        self.forgot = 0.0; self.dark = 0.0; self.dark_r = 40


def frame(f, st, bpose, back=None, front=None, channel=None, bflip=False, boss_extra=None):
    im = bg(f)
    shadow(im, HX, HY + 1, 12, 3); shadow(im, BX, BY + 2, 22, 5, 100)
    if back: back(im)
    bs = R.boss(bpose); bcy = BY - 82 + 18                       # sprite flutua acima do chao
    bspr = bs
    if boss_extra: boss_extra(im)
    paste_center(im, bspr, (BX, BY + 8 + bpose.get('dy', 0) * 0))
    hs = HERO[f % 6]
    if st.hero_tint: hs = tint(hs, st.hero_tint[0], st.hero_tint[1])
    if st.hurt > 0 and st.hurt % 2: hs = tint(hs, (255, 255, 255), .85)
    paste_center(im, hs, (HX + st.hero_dx, HY + st.hero_dy))
    if front: front(im)
    if st.dark > 0:                                              # escuridao com buraco de luz em volta do heroi
        ov = Image.new('RGBA', (NW, NH), (4, 2, 12, 255)); m = Image.new('L', (NW, NH), 0); d = ImageDraw.Draw(m)
        a = int(235 * st.dark)
        d.rectangle([0, 0, NW, NH], fill=a)
        r = st.dark_r
        for k in range(5):
            d.ellipse([HX - r - k * 6, HY - 18 - r * .8 - k * 5, HX + r + k * 6, HY - 18 + r * .8 + k * 5], fill=int(a * (k + 1) / 6) if k < 4 else int(a * .9) and 0) if False else None
        for k, fr in enumerate((1.0, .75, .5, .25)):
            rr = r * (1 + k * .45)
            d.ellipse([HX - rr, HY - 18 - rr * .8, HX + rr, HY - 18 + rr * .8], fill=int(a * (1 - fr) + a * .0) if False else int(a * (k + 1) / 5))
        d.ellipse([HX - r * .6, HY - 18 - r * .5, HX + r * .6, HY - 18 + r * .5], fill=0) if st.dark < .4 else None
        ov.putalpha(m); im.alpha_composite(ov)
        paste_center(im, tint(R.boss(dict(bpose, glow=2)), (255, 255, 255), 0) if False else R.boss(dict(bpose, glow=2)).crop((0, 0, 0, 0)) if False else Image.new('RGBA', (1, 1)), (0, 0))
        # olhos do chefe continuam brilhando no escuro
        d2 = ImageDraw.Draw(im)
        ey = BY - 27
        for sgn in (-1, 1): d2.rectangle([BX + sgn * 4 - 1, ey - 1, BX + sgn * 4, ey], fill=(154, 240, 255)); d2.point([BX + sgn * 4 - 1, ey - 1], fill=(255, 255, 255))
    # UI
    label(im, (NW // 2, 2), 'REI ESQUECIDO', (255, 230, 170), center=True)
    bar(im, NW // 2 - 40, 12, 80, st.bhp, (190, 60, 90))
    bar(im, 8, NH - 10, 40, st.hp, (80, 200, 90)); label(im, (8, NH - 20), 'HEROI', (220, 230, 255))
    if channel:
        name, k = channel
        bar(im, BX - 24, BY - 56, 48, k, (200, 120, 255), back=(40, 24, 60))
        label(im, (BX, BY - 68), name.upper(), (230, 200, 255), center=True)
    if st.forgot > 0:
        label(im, (HX, HY - 62), '?', (200, 160, 255), center=True)
        d = ImageDraw.Draw(im)
        for i in range(3):
            c = (90, 80, 120) if st.forgot > .5 else (200, 180, 255)
            d.rectangle([HX - 10 + i * 8, HY - 52, HX - 5 + i * 8, HY - 47], fill=c, outline=(40, 30, 60))
    return im


def hit(st, n=6): st.hurt = n


def run():
    random.seed(7)
    frames = []
    st = State()

    def emit(f, bpose, **kw):
        im = frame(f, st, bpose, **kw)
        frames.append(im)
        if st.hurt > 0: st.hurt -= 1

    def idle(n, f0=0):
        for i in range(n): emit(f0 + i, R.POSE['idle'](i))

    def channel(name, n=10, f0=0):
        for i in range(n):
            k = (i + 1) / n
            emit(f0 + i, R.POSE['raise_'](k), channel=(name, k))

    f = 0
    idle(8)
    # ---- 1 ESQUECIMENTO ----
    channel('Esquecimento'); f = 10
    for i in range(18):
        t = i / 17
        def back(im, t=t):
            ov = Image.new('RGBA', (NW, NH), (0, 0, 0, 0))
            for k in range(4):
                rr = 8 + (t * 140) - k * 12
                if rr > 0: ring(ov, BX, BY - 6, rr, rr * .38, (150 + k * 20, 70, 220), 220 - k * 40, dash=2)
            for j in range(24):
                a = j * .26 + t * 5; r_ = t * 150 * (.5 + (j % 5) / 6)
                px, py = BX + math.cos(a) * r_ * -1, BY - 8 + math.sin(a) * r_ * .3
                disc(ov, px, py, 2 if j % 3 else 3, (110, 50, 190), 150)
            im.alpha_composite(ov)
        if t > .75 and st.forgot == 0: st.forgot = .2; st.hero_tint = ((150, 130, 200), .45)
        if t > .9: st.forgot = 1.0
        emit(f + i, R.POSE['cast'](1), back=back)
    st.hero_tint = ((150, 130, 200), .45)
    idle(6, 40); st.hero_tint = None; st.forgot = 0
    # ---- 2 ECO ----
    channel('Eco', 9)
    for i in range(24):
        t = i / 23
        def back(im, t=t):
            ov = Image.new('RGBA', (NW, NH), (0, 0, 0, 0))
            ring(ov, BX, BY + 2, 22 + 5 * math.sin(t * 9), 7, (120, 200, 255), 200, dash=2)
            im.alpha_composite(ov)
        def extra(im, t=t):
            if t > .08:
                for dy_, dx_ in ((-20, -26), (20, -26)):
                    ghost = R.boss(R.POSE['cast'](1)); a = ghost.split()[3].point(lambda v: 110 if v else 0)
                    g2 = tint(ghost, (110, 190, 255), .55); g2.putalpha(a)
                    paste_center(im, g2, (BX + dx_, BY + 8 + dy_), )
        def front(im, i=i):
            ov = Image.new('RGBA', (NW, NH), (0, 0, 0, 0))
            for n_, (sy, t0) in enumerate(((BY - 34, 6), (BY - 28, 9), (BY - 44, 12), (BY - 20, 15))):
                if i >= t0:
                    u = min(1, (i - t0) / 6.0)
                    x = BX - 20 + (HX - (BX - 20)) * u; y = (sy if n_ % 2 == 0 else sy) + (HY - 20 - sy) * u
                    disc(ov, x, y, 4, (180, 90, 255), 230); disc(ov, x, y, 2, (255, 255, 255), 255)
                    for tr in range(1, 5): disc(ov, x + tr * 5 * (1 - u + .2), y - (HY - 20 - sy) * .05 * tr, 3 - tr // 2, (150, 70, 230), 130 - tr * 25)
                    if u >= 1 and i - t0 == 6: hit(st); st.hero_dx = -2; st.hp = max(.2, st.hp - .08)
            im.alpha_composite(ov)
            if st.hurt: dmg(im, HX + 4, HY - 56 - (6 - st.hurt) * 2, str(52 + i))
        st.hero_dx = 0 if i % 3 == 0 else st.hero_dx
        emit(60 + i, R.POSE['cast'](1), back=back, front=front, boss_extra=extra)
    st.hero_dx = 0
    idle(6, 90)
    # ---- 3 FENDA DO VAZIO ----
    channel('Fenda do Vazio', 10)
    for i in range(26):
        t = i / 25
        def back(im, i=i):
            ov = Image.new('RGBA', (NW, NH), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
            if i < 8:                                    # aviso: circulo no chao sob o heroi
                pulse = 14 + 2 * math.sin(i * 1.4)
                ring(ov, HX, HY, pulse, pulse * .38, (255, 90, 120), 230, dash=2)
                d.ellipse([HX - pulse, HY - pulse * .38, HX + pulse, HY + pulse * .38], fill=(255, 60, 100, 40))
            elif i < 20:
                k = min(1, (i - 8) / 3.0) if i < 17 else max(0, (20 - i) / 3.0)
                rx, ry = 18 * k, 7 * k
                d.ellipse([HX - rx - 2, HY - ry - 1, HX + rx + 2, HY + ry + 1], fill=(190, 90, 255, 255))
                d.ellipse([HX - rx, HY - ry, HX + rx, HY + ry], fill=(6, 2, 14, 255))
                for c_ in range(5):                     # rachaduras
                    a_ = c_ * 1.3 + .4
                    d.line([HX, HY, HX + math.cos(a_) * (rx + 12) * k, HY + math.sin(a_) * (ry + 5) * k], fill=(150, 70, 220, 255))
                for j in range(14):                      # particulas sugadas
                    a_ = j * .5 + i * .4; r_ = max(2, 34 - ((i * 3 + j * 4) % 34))
                    disc(ov, HX + math.cos(a_) * r_, HY + math.sin(a_) * r_ * .4, 1, (210, 150, 255), 220)
            im.alpha_composite(ov)
        if i == 9:
            hit(st, 6); st.hp = max(.15, st.hp - .14)
        st.hero_dy = -4 if 9 <= i <= 10 else (-2 if i == 11 else 0)
        def front(im, i=i):
            if st.hurt: dmg(im, HX + 2, HY - 58 - max(0, i - 9) * 2, '88')
        emit(120 + i, R.POSE['cast'](1) if i < 12 else R.POSE['slam'](1), back=back, front=front)
    st.hero_dy = 0
    idle(6, 150)
    # ---- 4 COROA DE ALMAS ----
    channel('Coroa de Almas', 10)
    for i in range(26):
        def front(im, i=i):
            ov = Image.new('RGBA', (NW, NH), (0, 0, 0, 0))
            cx0, cy0 = BX, BY - 44
            for n_ in range(5):
                a_ = n_ * 2 * math.pi / 5 + i * .35
                if i < 12:
                    r_ = 14 + 1.5 * i; x = cx0 + math.cos(a_) * r_; y = cy0 - 10 + math.sin(a_) * r_ * .45
                else:
                    u = min(1, (i - 12 - n_ * 1.5) / 8)
                    u = max(0, u)
                    x0 = cx0 + math.cos(a_) * 30; y0 = cy0 - 10 + math.sin(a_) * 13
                    mx = (x0 + HX) / 2; my = min(y0, HY - 60) - 10 * math.sin(n_ + 1)
                    x = (1 - u) ** 2 * x0 + 2 * (1 - u) * u * mx + u * u * HX
                    y = (1 - u) ** 2 * y0 + 2 * (1 - u) * u * my + u * u * (HY - 20)
                    if u >= 1 and not getattr(st, 'h%d' % n_, 0): setattr(st, 'h%d' % n_, 1); hit(st, 4); st.hp = max(.1, st.hp - .05)
                    if u >= 1: continue
                for tr in range(1, 4): disc(ov, x - tr * 2, y + tr, 3 - tr // 2, (80, 170, 255), 120 - tr * 30)
                disc(ov, x, y, 4, (90, 190, 255), 230); disc(ov, x, y, 2, (255, 255, 255), 255)
            im.alpha_composite(ov)
            if st.hurt: dmg(im, HX + 3, HY - 56 - (4 - st.hurt) * 2, '31', (160, 220, 255))
        for n_ in range(5): setattr(st, 'h%d' % n_, 0) if i == 0 else None
        emit(180 + i, R.POSE['cast'](1), front=front)
    idle(6, 210)
    # ---- 5 TREVAS ----
    channel('Trevas', 10)
    for i in range(30):
        t = i / 29
        if i < 8: st.dark = i / 8 * .9
        elif i < 22: st.dark = .9
        else: st.dark = max(0, .9 - (i - 22) / 8 * .9)
        st.dark_r = 26 if 6 < i < 24 else 40
        def back(im, i=i):
            ov = Image.new('RGBA', (NW, NH), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
            if 6 <= i <= 24:
                for k in range(7):                      # tentaculos de sombra serpenteando ate o heroi
                    pts = []
                    for s in range(0, 20):
                        u = s / 19
                        x = BX - 20 + (HX - BX + 20) * u; y = BY - 4 + (HY - BY + 4) * u + math.sin(u * 9 + i * .6 + k) * (3 + k % 3)
                        pts.append((x, y + (k - 3) * 2))
                    d.line(pts[:max(2, int(len(pts) * min(1, (i - 6) / 8)))], fill=(14, 6, 34, 230), width=2)
                    d.line(pts[:max(2, int(len(pts) * min(1, (i - 6) / 8)))], fill=(120, 60, 200, 160), width=1)
            im.alpha_composite(ov)
        if i == 16: hit(st, 6); st.hp = max(.05, st.hp - .1); st.hero_dx = -2
        if i == 20: st.hero_dx = 0
        def front(im, i=i):
            if st.hurt: dmg(im, HX + 3, HY - 56 - (6 - st.hurt) * 2, '64', (200, 150, 255))
        emit(240 + i, R.POSE['cast'](1) if i < 24 else R.POSE['idle'](i), back=back, front=front)
    st.dark = 0
    idle(8, 280)
    big = [f.convert('RGB').resize((NW * SC, NH * SC), Image.NEAREST) for f in frames]
    p = big[0].quantize(colors=240, method=Image.MEDIANCUT, dither=Image.NONE)
    q = [b.quantize(palette=p, dither=Image.NONE) for b in big]
    path = os.path.join(OUT, 'rei_chibi_habilidades.gif')
    q[0].save(path, save_all=True, append_images=q[1:], duration=85, loop=0, disposal=1)
    return len(q), big


if __name__ == '__main__':
    n, big = run()
    print(n)
    N_ = len(big); sel = [big[min(N_ - 1, int(N_ * q))] for q in (.03, .09, .13, .2, .25, .31, .38, .46, .55, .64, .7, .8)]
    sh = Image.new('RGB', (NW * SC // 2 * 4, NH * SC // 2 * 3))
    for i, b in enumerate(sel):
        sh.paste(b.resize((NW * SC // 2, NH * SC // 2), Image.NEAREST), ((i % 4) * NW * SC // 2, (i // 4) * NH * SC // 2))
    sh.save(os.path.join(OUT, 'rei_chibi_folha.png'))
