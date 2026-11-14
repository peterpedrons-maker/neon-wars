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


# ======================================================================= LADINO: LEQUE DE ADAGAS + VENENO
def dagger_img(ang, over=None, ln=7):
    from pxrig import Grid
    g = Grid(26, 26)
    cells, tip = C.sword_rows((13, 13), ang, ln, 1)
    C.stamp_cells(g, cells)
    pal = dict(C.PALS['rogue'])
    if over: pal.update(over)
    return g.render(pal, C.sel_for('rogue', pal, over or {}))


def rogue_fan():
    st = fx.Stage(); frames = []
    HX, HY = 120, 140
    app = dict(cls='rogue', weapon='adaga_veneno', weapon2='adaga_veneno')
    pose = [dict(tn=2, sw=dag(100), sw2=dict(ang=80, len=8)),
            dict(tn=2, hdx=-2, bdx=-1, dx=-1, ar=(-2, -3), sw=dag(215), sw2=dict(ang=215, len=8)),
            dict(tn=3, hdx=3, bdx=1, dx=3, ar=(5, -1), sw=dag(85), sw2=dict(ang=80, len=8), face='shout'),
            dict(tn=3, hdx=2, bdx=1, dx=2, ar=(3, 0), sw=dag(95), sw2=dict(ang=80, len=8)),
            dict(tn=3, sw=dag(100), sw2=dict(ang=80, len=8))]
    sp = C.anim('right', 'attack', 'rogue', pose, app)
    over = C.make_palette(app)
    enemies = [fx.Enemy(250, 120, M.SLIME), fx.Enemy(270, 142, M.SLIME_B), fx.Enemy(248, 166, M.SLIME_O)]
    targets = [(250, 112), (262, 126), (272, 140), (262, 156), (250, 168)]
    LAUNCH, FLY = 9, 6
    poison = {}
    for j in range(46):
        back = fx.layer(); front = fx.layer()
        pi = 0 if j < 4 else 1 if j < 9 else 2 if j < 12 else 3 if j < 15 else 4
        img, tip, bh = sp[pi]
        ox, oy = HX - CW // 2, HY - C.BASE
        if 4 <= j < 9: fx.aura(back, HX, HY - 17, j, (j - 3) / 5.0, col=(90, 220, 90))
        for i, tg in enumerate(targets):
            if LAUNCH <= j < LAUNCH + FLY:
                u = (j - LAUNCH + 1) / float(FLY)
                sx, sy = ox + 30, oy + 22
                x = sx + (tg[0] - sx) * u; y = sy + (tg[1] - sy) * u
                ang = (j * 70 + i * 40) % 360
                di = dagger_img(ang, over)
                lay = fx.layer(); lay.paste(di, (int(x) - 13, int(y) - 13)); front = Image.alpha_composite(front, lay)
                for q in (1, 2):
                    fx.dither_ellipse(front, x - (tg[0] - sx) / 60.0 * q * 3, y - (tg[1] - sy) / 60.0 * q * 3, 2, 2, (120, 230, 90), 90)
            if j == LAUNCH + FLY:
                fx.dust(front, tg[0], tg[1], 0, n=5)
        if j == LAUNCH + FLY:
            for e in enemies: e.hit((.4, 0), '14'); poison[id(e)] = j
        dyn = []
        for e in enemies:
            eimg, ex_, ey_, up, ek = e.step()
            pj = poison.get(id(e))
            if pj is not None and j - pj < 28:
                eimg = fx.tint_img(eimg, (90, 200, 70), .45 if (j // 2) % 2 else .3)
                for q in range(4):
                    ov = fx.layer(); ImageDraw.Draw(ov).ellipse([ex_ - 4 + q * 3, ey_ - 22 - ((j + q * 5) % 10), ex_ - 2 + q * 3, ey_ - 20 - ((j + q * 5) % 10)], fill=(140, 240, 110, 230))
                    front = Image.alpha_composite(front, ov)
                if (j - pj) % 7 == 4: e.hit((0, 0), '8')
            back = shadow(back, ex_, ey_, 8, 70)
            dyn.append(dict(img=eimg, x=ex_ - 9, y=ey_ - 13 - up, foot=ey_, ek=ek, ex=ex_, ey=ey_, poison=pj is not None and j - pj < 28))
        back = shadow(back, HX, HY)
        dyn.append(dict(img=img, x=ox, y=oy, foot=HY))
        im = st.compose(j, back, dyn, front)
        for d in dyn:
            if 'ek' in d and d['ek'] is not None and d['ek'] >= 1:
                fx.draw_number(im, d['ex'] + 6, d['ey'] - 28 - d['ek'] * 1.2, '14' if j < LAUNCH + FLY + 3 else '8')
        frames.append(im)
    return frames


# ======================================================================= CLERIGO: JULGAMENTO DIVINO
def cleric_judgement():
    st = fx.Stage(); frames = []
    HX, HY = 120, 140
    app = dict(cls='cleric', weapon='martelo_sagrado')
    pose = [dict(sw=mace(165)), dict(tn=2, ar=(0, -3), al=(1, -3), sw=mace(185)), dict(tn=3, ar=(1, -6), al=(3, -7), sw=mace(190), hdy=-1, face='shout'),
            dict(tn=3, ar=(5, -2), dx=2, hdx=3, sw=mace(95), face='shout'), dict(tn=3, ar=(5, 0), dx=2, hdx=3, sw=mace(90)), dict(sw=mace(165))]
    sp = C.anim('right', 'attack', 'cleric', pose, app)
    TC = (262, 144)
    enemies = [fx.Enemy(TC[0] - 18, TC[1] - 6, M.SLIME), fx.Enemy(TC[0] + 12, TC[1] - 14, M.SLIME_B), fx.Enemy(TC[0] + 22, TC[1] + 10, M.SLIME_O), fx.Enemy(TC[0] - 8, TC[1] + 12, M.SLIME)]
    for j in range(52):
        back = fx.layer(); front = fx.layer(); sh = (0, 0)
        pi = 0 if j < 3 else 1 if j < 6 else 2 if j < 14 else 3 if j < 17 else 4 if j < 24 else 5
        img, tip, bh = sp[pi]
        ox, oy = HX - CW // 2, HY - C.BASE
        if 4 <= j < 17:
            k = min(1.0, (j - 4) / 8.0)
            fx.dither_ellipse(back, HX, HY - 17, 14 + 3 * k, 22, (255, 230, 120), int(40 + 90 * k))
            if tip: fx.dither_ellipse(front, ox + tip[0], oy + tip[1], 5 + k * 3, 5 + k * 3, (255, 240, 170), 160)
            fx.converge(front, ox + (tip[0] if tip else 28), oy + (tip[1] if tip else 20), j, k, col=(255, 235, 150))
        # circulo de luz no alvo (marca)
        if 8 <= j < 40:
            a = int(min(1, (j - 8) / 6.0) * 170) if j < 32 else int(max(0, (40 - j) / 8.0) * 170)
            fx.magic_circle(back, TC[0], TC[1], 46, 20, j * .08, a, col=(255, 224, 120))
        # feixe de luz do ceu (cai em 3 quadros) + cruz brilhante + anel
        if 16 <= j < 36:
            k = j - 16
            top = max(0, 0 - 0)
            reach = min(1.0, (k + 1) / 3.0)
            ybot = TC[1] * reach
            a = 230 if k < 12 else max(0, int(230 * (1 - (k - 12) / 8.0)))
            fx.pillar(back, TC[0], 0, ybot, 20 if k < 14 else 14, j, a, col=(255, 240, 170))
            fx.pillar(front, TC[0], 0, ybot, 8, j, min(255, a + 20), col=(255, 255, 240))
            if k >= 2:
                r = 14 + (k % 5) * 2
                dr = ImageDraw.Draw(front)
                for (dx, dy) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    dr.line([TC[0], TC[1] - 6, TC[0] + dx * (r + 8), TC[1] - 6 + dy * (r + 4)], fill=(255, 250, 200, 220), width=2)
                rx = 8 + (k % 10) * 5
                ImageDraw.Draw(back).ellipse([TC[0] - rx, TC[1] - rx * .45, TC[0] + rx, TC[1] + rx * .45], outline=(255, 236, 160, max(0, 230 - (k % 10) * 24)), width=2)
            if k < 3: sh = (1 if j % 2 else -1, 0)
            for i in range(7):
                t = ((k * .9 + i * 1.7) % 10) / 10.0
                fx.plus(front, TC[0] + math.sin(i * 2.3) * 16, TC[1] - 4 - t * 40, (255, 240, 150), int(255 * (1 - t)))
        if j == 18:
            for e in enemies:
                v = (e.x0 - TC[0], e.y0 - TC[1]); L = math.hypot(*v) or 1
                e.hit((v[0] / L * .6, v[1] / L * .6), '72')
        dyn = []
        for e in enemies:
            eimg, ex_, ey_, up, ek = e.step()
            back = shadow(back, ex_, ey_, 8, 70)
            dyn.append(dict(img=eimg, x=ex_ - 9, y=ey_ - 13 - up, foot=ey_, ek=ek, ex=ex_, ey=ey_))
            if 20 <= j < 36:   # estrelas de atordoamento
                for q in range(3):
                    a_ = j * .5 + q * 2.1
                    fx.plus(front, ex_ + math.cos(a_) * 7, ey_ - 22 + math.sin(a_) * 2.5, (255, 224, 80), 255)
        back = shadow(back, HX, HY)
        dyn.append(dict(img=img, x=ox, y=oy, foot=HY))
        im = st.compose(j, back, dyn, front, shake=sh)
        for d in dyn:
            if 'ek' in d and d['ek'] is not None and d['ek'] >= 1: fx.draw_number(im, d['ex'] + 6, d['ey'] - 28 - d['ek'] * 1.2, '72')
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
    save(rogue_fan(), 'ladino_leque_veneno.gif'); print('lf')
    save(cleric_judgement(), 'clerigo_julgamento.gif'); print('cj')
