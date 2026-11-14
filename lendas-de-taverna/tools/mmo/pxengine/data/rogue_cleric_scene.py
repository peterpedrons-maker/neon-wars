#!/usr/bin/env python3
"""LADINO (adagas duplas): Corte Duplo + Golpe Sombrio.  CLERIGO (maca): Martelada Sagrada + Cura Divina.
Saidas: mmo/proto_pixel/ladino_basico.gif, ladino_sombrio.gif, clerigo_basico.gif, clerigo_cura.gif"""
import os, math, random
from PIL import Image, ImageDraw
import chibi as C
import teste_clareira as T
import px2_mobs as M
import fx

OUT = T.OUT
W, H = T.W, T.H
CW = C.W


def dag(ang, ln=8): return dict(kind='dagger', ang=ang, len=ln)


def shadow(back, x, y, r=9, a=90):
    s = fx.layer(); ImageDraw.Draw(s).ellipse([x - r, y - 2, x + r, y + 3], fill=(0, 0, 0, a)); return Image.alpha_composite(s, back)


# ======================================================================= LADINO
ROGUE = [
    dict(tn=2, sw=dag(100), sw2=dict(ang=80, len=8)),
    dict(tn=2, hdx=-1, bdx=-1, dx=-1, sw=dag(215), sw2=dict(ang=95, len=8)),
    dict(tn=3, hdx=3, bdx=1, dx=3, sw=dag(70), sw2=dict(ang=120, len=8), face='shout'),
    dict(tn=2, hdx=-1, bdx=-1, dx=0, sw=dag(90), sw2=dict(ang=215, len=8)),
    dict(tn=3, hdx=3, bdx=1, dx=3, sw=dag(110), sw2=dict(ang=70, len=8), face='shout'),
    dict(tn=3, sw=dag(100), sw2=dict(ang=80, len=8)),
]
RH = [2, 2, 3, 2, 3, 3]


def rogue_basic():
    st = fx.Stage(); frames = []
    CX, CY = 150, 150
    spr = C.anim('right', 'attack', 'rogue', ROGUE)
    en = fx.Enemy(CX + 44, CY, M.SLIME_B)
    seq = [(0, 0)] * 3
    for k, h in enumerate(RH): seq += [(k, t) for t in range(h)]
    seq += [(5, 0)] * 12
    hits = {}
    cnt = 0
    for j, (k, t) in enumerate(seq):
        if k in (2, 4) and t == 0 and cnt < 2: hits[j] = k; cnt += 1
    for j, (k, t) in enumerate(seq):
        back = fx.layer(); front = fx.layer()
        img, tip, bh = spr[k]
        ox, oy = CX - CW // 2, CY - C.BASE
        if j in hits: en.hit((.6, 0), '19')
        for hj, hk in hits.items():
            d = j - hj
            if 0 <= d < 4: fx.slash_x(front, CX + 36, CY - 10, d, r=9 if hk == 2 else 8)
        eimg, ex_, ey_, up, ek = en.step()
        back = shadow(back, ex_, ey_, 8, 70); back = shadow(back, CX, CY)
        dyn = [dict(img=img, x=ox, y=oy, foot=CY), dict(img=eimg, x=ex_ - 9, y=ey_ - 13 - up, foot=ey_)]
        im = st.compose(j, back, dyn, front)
        if ek is not None and ek >= 1: fx.draw_number(im, ex_ + 6, ey_ - 26 - ek * 1.2, '19')
        frames.append(im)
    return frames


def rogue_shadow():
    st = fx.Stage(); frames = []
    CY = 148
    X0, X1 = 110, 330
    ready = C.anim('right', 'attack', 'rogue', [dict(tn=2, sw=dag(100), sw2=dict(ang=80, len=8))])[0][0]
    dash = C.anim('right', 'attack', 'rogue', [dict(tn=2, hdx=3, bdx=2, dx=2, bl=(-3, 0), br=(2, 0), sw=dag(250), sw2=dict(ang=250, len=8))])[0][0]
    fin = C.anim('right', 'attack', 'rogue', [dict(tn=2, hdx=2, bdx=1, dx=1, sw=dag(95), sw2=dict(ang=60, len=8), face='shout')])[0][0]
    idle = C.anim('right', 'attack', 'rogue', [dict(tn=3, sw=dag(100), sw2=dict(ang=80, len=8))])[0][0]
    enemies = [fx.Enemy(190, CY + 2, M.SLIME), fx.Enemy(240, CY - 8, M.SLIME_B), fx.Enemy(285, CY + 6, M.SLIME_O)]
    marks = {}
    N = 46
    clones = []
    for j in range(N):
        back = fx.layer(); front = fx.layer(); sh = (0, 0)
        hx = X0
        vis = True; spr = ready
        if j < 5:
            spr = ready
            if j >= 2: fx.aura(back, X0, CY - 17, j, (j - 1) / 3.0, col=(120, 60, 220))
        elif j < 7:
            vis = False
            fx.smoke_puff(front, X0, CY, j - 5)
        elif j < 17:
            vis = False
            u = (j - 7) / 9.0
            hx = X0 + (X1 - X0) * min(1, u)
            clones.append((hx, j))
            for (cx_, cj) in clones[-5:]:
                a = max(0, 160 - (j - cj) * 38)
                c = fx.tint_img(dash, (80, 40, 150), .75)
                px = c.load(); al = c.getchannel('A').point(lambda v: int(v * a / 255)); c.putalpha(al)
                lay = fx.layer(); lay.paste(c, (int(cx_) - CW // 2, CY - C.BASE)); back = Image.alpha_composite(back, lay)
            for e in enemies:
                if abs(hx - e.x0) < 14 and e.k is None and id(e) not in marks:
                    marks[id(e)] = j
                    e.hit((.5, 0), '22')
        elif j < 20:
            hx = X1; spr = fin; fx.smoke_puff(front, X1, CY, j - 17)
        else:
            hx = X1; spr = fin if j < 26 else idle
        # cortes em X e explosao sombria atrasada
        for e in enemies:
            m = marks.get(id(e))
            if m is not None and 0 <= j - m < 5: fx.slash_x(front, e.x0, e.y0 - 9, j - m, r=10)
        if j == 27:
            for e in enemies: e.hit((.3, 0), '48')
        if 27 <= j < 35:
            for e in enemies: fx.explosion(back, front, e.x0, e.y0, j - 27, R=11, seed=int(e.x0)) if False else None
            k_ = j - 27
            for e in enemies:
                dither = fx.dither_ellipse
                dither(front, e.x0, e.y0 - 8, 8 + k_ * 2.2, 8 + k_ * 2.2, (140, 70, 230), max(0, 200 - k_ * 25))
                dither(front, e.x0, e.y0 - 8, 4 + k_, 4 + k_, (230, 200, 255), max(0, 230 - k_ * 30))
            if k_ < 2: sh = (1 if j % 2 else -1, 0)
        dyn = []
        for e in enemies:
            eimg, ex_, ey_, up, ek = e.step()
            back = shadow(back, ex_, ey_, 8, 70)
            dyn.append(dict(img=eimg, x=ex_ - 9, y=ey_ - 13 - up, foot=ey_, ek=ek, ex=ex_, ey=ey_))
        if vis:
            back = shadow(back, hx, CY)
            dyn.append(dict(img=spr, x=hx - CW // 2, y=CY - C.BASE, foot=CY))
        im = st.compose(j, back, dyn, front, shake=sh)
        for d in dyn:
            if 'ek' in d and d['ek'] is not None and d['ek'] >= 1: fx.draw_number(im, d['ex'] + 6, d['ey'] - 26 - d['ek'] * 1.2, '22' if j < 27 else '48')
        frames.append(im)
    return frames


# ======================================================================= CLERIGO
def mace(ang): return dict(kind='mace', ang=ang, len=15)


CLERIC = [
    dict(sw=mace(165)),
    dict(tn=2, ar=(0, -3), sw=mace(195)),
    dict(tn=3, ar=(0, -6), al=(2, -4), hdx=-1, bdx=-1, dx=-1, sw=mace(215), face='shout'),
    dict(tn=3, ar=(2, -4), dx=1, hdx=1, sw=mace(150)),
    dict(tn=2, ar=(5, 1), dx=3, hdx=3, bdx=2, bl=(-2, 0), br=(2, 0), sw=mace(85), face='shout'),
    dict(tn=2, ar=(5, 2), dx=3, hdx=3, bdx=2, sw=mace(75)),
    dict(tn=3, ar=(3, 0), dx=1, hdx=1, sw=mace(120)),
    dict(sw=mace(165)),
]
CH = [3, 2, 3, 2, 2, 3, 2, 3]


def cleric_basic():
    st = fx.Stage(); frames = []
    CX, CY = 150, 150
    spr = C.anim('right', 'attack', 'cleric', CLERIC)
    en = fx.Enemy(CX + 46, CY, M.SLIME)
    seq = [(0, 0)] * 3
    for k, h in enumerate(CH): seq += [(k, t) for t in range(h)]
    seq += [(7, 0)] * 10
    imp = next(j for j, s in enumerate(seq) if s[0] == 4)
    for j, (k, t) in enumerate(seq):
        back = fx.layer(); front = fx.layer(); sh = (0, 0)
        img, tip, bh = spr[k]
        ox, oy = CX - CW // 2, CY - C.BASE
        if j == imp: en.hit((.7, 0), '35')
        d = j - imp
        if 0 <= d < 8:
            hx, hy = CX + 34, CY - 4
            fx.disc(front, hx, hy - 4, max(0, 10 - d * 3), (255, 245, 190), max(0, 230 - d * 40))
            rx = 6 + d * 5
            ImageDraw.Draw(back).ellipse([hx - rx, hy - rx * .45, hx + rx, hy + rx * .45], outline=(255, 226, 120, max(0, 230 - d * 28)), width=2)
            for i in range(4):
                a = i * 1.57 + .8; r = 6 + d * 4
                fx.plus(front, hx + math.cos(a) * r, hy - 6 - d + math.sin(a) * r * .6, (255, 240, 150), max(0, 255 - d * 30))
            if d < 2: sh = (1 if j % 2 else -1, 0)
        if k >= 4 and tip: pass
        eimg, ex_, ey_, up, ek = en.step()
        back = shadow(back, ex_, ey_, 8, 70); back = shadow(back, CX, CY)
        dyn = [dict(img=img, x=ox, y=oy, foot=CY), dict(img=eimg, x=ex_ - 9, y=ey_ - 13 - up, foot=ey_)]
        im = st.compose(j, back, dyn, front, shake=sh)
        if ek is not None and ek >= 1: fx.draw_number(im, ex_ + 6, ey_ - 26 - ek * 1.2, '35')
        frames.append(im)
    return frames


def cleric_heal():
    st = fx.Stage(); frames = []
    HX, HY = 130, 150
    pose = [dict(sw=mace(165)), dict(tn=2, ar=(0, -3), al=(1, -3), sw=mace(180)), dict(tn=3, ar=(1, -6), al=(3, -7), sw=mace(180), hdy=-1, face='shout'),
            dict(tn=3, ar=(1, -7), al=(3, -8), sw=mace(180), hdy=-1, face='shout'), dict(tn=3, ar=(1, -5), al=(2, -5), sw=mace(180)), dict(sw=mace(165))]
    cs = C.anim('right', 'attack', 'cleric', pose)
    war = C.anim('right', 'attack', 'warrior', [dict(tn=3, sw=dict(ang=105, len=12))])[0][0]
    arc = C.anim('right', 'attack', 'archer', [dict(tn=3, sw=dict(kind='bow', dir=(1, 0), draw=2, arrow=False))])[0][0]
    allies = [(250, 144, war, 'war'), (300, 156, arc, 'arc')]
    N = 50
    for j in range(N):
        back = fx.layer(); front = fx.layer()
        if j < 3: pi = 0
        elif j < 6: pi = 1
        elif j < 12: pi = 2 + (j % 2) * 0
        elif j < 24: pi = 3
        elif j < 28: pi = 4
        else: pi = 5
        img, tip, bh = cs[pi]
        ox, oy = HX - CW // 2, HY - C.BASE
        if 3 <= j < 26:   # brilho dourado em volta do clerigo + tiara
            k = min(1, (j - 3) / 8.0)
            fx.dither_ellipse(back, HX, HY - 17, 14 + 3 * k, 22, (255, 230, 120), int(40 + 80 * k))
            if tip: fx.dither_ellipse(front, ox + tip[0], oy + tip[1], 5, 5, (255, 240, 170), 150)
        # pilares de luz + aneis + sinais de + nos aliados
        for (ax, ay, aspr, nm) in allies:
            t0 = 10 if nm == 'war' else 13
            if t0 <= j < t0 + 20:
                k = j - t0
                a = int(min(1, k / 3.0) * 150) if k < 14 else int(max(0, (20 - k) / 6.0) * 150)
                fx.pillar(back, ax, 0, ay - 4, 11, j, a)
                for r_i in range(3):
                    kk = (k + r_i * 3) % 10
                    rx = 6 + kk * 2.4
                    ImageDraw.Draw(back).ellipse([ax - rx, ay - rx * .4, ax + rx, ay + rx * .4], outline=(255, 232, 130, max(0, 220 - kk * 24)), width=1)
                for i in range(7):
                    tt = ((k * .8 + i * 1.5) % 9) / 9.0
                    px_ = ax + math.sin(i * 2.3) * 11
                    fx.plus(front, px_, ay - 4 - tt * 34, (120, 255, 150) if i % 2 else (255, 240, 150), int(255 * (1 - tt)))
        dyn = []
        for (ax, ay, aspr, nm) in allies:
            t0 = 10 if nm == 'war' else 13
            sp = aspr
            if t0 <= j < t0 + 3: sp = fx.tint_img(aspr, (140, 255, 160), .55)
            back = shadow(back, ax, ay)
            dyn.append(dict(img=sp, x=ax - CW // 2, y=ay - C.BASE, foot=ay))
        back = shadow(back, HX, HY)
        dyn.append(dict(img=img, x=ox, y=oy, foot=HY))
        im = st.compose(j, back, dyn, front)
        for (ax, ay, aspr, nm) in allies:
            t0 = 10 if nm == 'war' else 13
            frac = .22 if j < t0 else min(1.0, .22 + (j - t0) / 12.0 * .78)
            fx.hp_bar(im, ax - 11, ay - 44, frac)
            if t0 + 2 <= j < t0 + 14: fx.draw_number(im, ax - 6, ay - 56 - (j - t0 - 2) * 1.2, '+60')
        frames.append(im)
    return frames


def save(frames, name, scale=2, dur=70):
    big = [f.convert('RGB').resize((W * scale, H * scale), Image.NEAREST) for f in frames]
    n = len(big); pick = [big[i * n // 6] for i in range(6)]
    col = Image.new('RGB', (pick[0].width * 3, pick[0].height * 2))
    for i, p in enumerate(pick): col.paste(p, ((i % 3) * p.width, (i // 3) * p.height))
    pal = col.quantize(colors=220, method=Image.MEDIANCUT, dither=Image.NONE)
    q = [im.quantize(palette=pal, dither=Image.NONE) for im in big]
    q[0].save(os.path.join(OUT, name), save_all=True, append_images=q[1:], duration=dur, loop=0, disposal=1)


if __name__ == '__main__':
    save(rogue_basic(), 'ladino_basico.gif'); print('lb')
    save(rogue_shadow(), 'ladino_sombrio.gif'); print('ls')
    save(cleric_basic(), 'clerigo_basico.gif'); print('cb')
    save(cleric_heal(), 'clerigo_cura.gif'); print('cc')
