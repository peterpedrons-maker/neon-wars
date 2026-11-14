#!/usr/bin/env python3
"""ARQUEIRO (chibi): ataque basico 'Tiro' nas 4 direcoes + skill 'Chuva de Flechas'.
Saidas: mmo/proto_pixel/arqueiro_basico.gif, arqueiro_chuva.gif"""
import os, math, random
from PIL import Image, ImageDraw
import chibi as C
import teste_clareira as T
import px2_mobs as M
import fx

OUT = T.OUT
W, H = T.W, T.H
CW = C.W
DIRS = {'right': (1, 0), 'down': (0, 1), 'left': (-1, 0), 'up': (0, -1)}


def flip(im): return im.transpose(Image.FLIP_LEFT_RIGHT)


def bow(d, draw, arrow=True): return dict(kind='bow', dir=d, draw=draw, arrow=arrow)


def shot_table(d):
    """8 poses do tiro (puxa, mira, solta, volta). d = direcao (dx,dy)."""
    return [
        dict(sw=bow(d, 1)),
        dict(sw=bow(d, 2), hdx=-1),
        dict(sw=bow(d, 4), hdx=-1, bdx=-1, dx=-1),
        dict(sw=bow(d, 6), hdx=-2, bdx=-1, dx=-1, tn=2, face='shout'),
        dict(sw=bow(d, 6), hdx=-2, bdx=-1, dx=-1, tn=2, face='shout'),
        dict(sw=bow(d, 0, False), hdx=1, dx=1),
        dict(sw=bow(d, -1, False), hdx=1, dx=1),
        dict(sw=bow(d, 0, False)),
    ]


def sprites(face, table):
    v = 'right' if face in ('right', 'left') else face
    ps = []
    for p in table:
        q = dict(p)
        if v != 'right':
            for k in ('dx', 'hdx', 'bdx'): q.pop(k, None)
        ps.append(q)
    res = C.anim(v, 'attack', 'archer', ps)
    if face == 'left': res = [(flip(i), (CW - 1 - t[0], t[1]) if t else None, b) for i, t, b in res]
    return res


HOLD = [2, 2, 2, 3, 2, 2, 2, 3]


def basic():
    st = fx.Stage(); frames = []; gi = 0
    CX, CY = 190, 150
    for face in ('right', 'down', 'left', 'up'):
        d = DIRS[face]
        tbl_dir = d if face != 'left' else (1, 0)         # left = espelho do right
        spr = sprites(face, shot_table(tbl_dir if face != 'left' else (1, 0)))
        en = fx.Enemy(CX + d[0] * 70, CY + d[1] * 40)
        seq = [('ready', f) for f in range(4)]
        for k, h in enumerate(HOLD):
            for t in range(h): seq.append(('shot', k, t))
        for f in range(14): seq.append(('post', f))
        rel = next(i for i, s in enumerate(seq) if s[0] == 'shot' and s[1] == 5 and s[2] == 0)
        FLY = 5
        impact = rel + FLY
        tip0 = None
        stuck = None
        for j, s in enumerate(seq):
            back = fx.layer(); front = fx.layer(); sh = (0, 0)
            k = s[1] if s[0] == 'shot' else 0
            img, tip, behind = spr[min(k, 7)] if s[0] == 'shot' else spr[0 if s[0] == 'ready' else 7]
            ox, oy = CX - CW // 2, CY - C.BASE
            if s[0] == 'shot' and k == 4 and s[2] == 0 and tip: tip0 = (ox + tip[0], oy + tip[1])
            if s[0] == 'shot' and k == 3 and tip:   # brilho na ponta (carregando)
                fx.dither_ellipse(front, ox + tip[0], oy + tip[1], 5, 5, (255, 220, 90), 120)
            if tip0 is None and rel - 2 <= j < rel and tip: tip0 = (ox + tip[0], oy + tip[1])
            tgt = (en.x0, en.y0 - 7)
            if tip0 and rel <= j < impact:
                u = (j - rel + 1) / float(FLY)
                px, py = tip0[0] + (tgt[0] - tip0[0]) * u, tip0[1] + (tgt[1] - tip0[1]) * u
                v = (tgt[0] - tip0[0], tgt[1] - tip0[1]); L = math.hypot(*v) or 1
                for q in (3, 2, 1):   # rastro de movimento
                    fx.arrow(front, px - v[0] / L * q * 3, py - v[1] / L * q * 3, (v[0] / L, v[1] / L), L=6, f=j)
                fx.arrow(front, px, py, (v[0] / L, v[1] / L), L=9, f=j)
            if j == impact:
                en.hit((d[0] * .5, d[1] * .5), '24'); stuck = (tgt[0], tgt[1], (d[0], d[1]))
            if impact <= j < impact + 3: fx.dust(front, tgt[0], tgt[1] + 6, j - impact)
            eimg, ex_, ey_, up, ek = en.step()
            if stuck and j >= impact:
                sx, sy, dd = stuck
                fx.arrow(front, ex_ + 0, ey_ - 7 - up, (dd[0] * 1.0, dd[1] * 1.0), L=4)
            shd = fx.layer(); ImageDraw.Draw(shd).ellipse([ex_ - 8, ey_ - 2, ex_ + 8, ey_ + 3], fill=(0, 0, 0, 70)); back = Image.alpha_composite(shd, back)
            hs = fx.layer(); ImageDraw.Draw(hs).ellipse([CX - 9, CY - 2, CX + 9, CY + 3], fill=(0, 0, 0, 90)); back = Image.alpha_composite(hs, back)
            hero = dict(img=img, x=ox, y=oy, foot=CY)
            dyn_e = dict(img=eimg, x=ex_ - 9, y=ey_ - 13 - up, foot=ey_)
            im = st.compose(gi, back, [hero, dyn_e], front, shake=sh)
            if ek is not None and ek >= 1: fx.draw_number(im, ex_ + 6, ey_ - 26 - ek * 1.2, '24')
            frames.append(im); gi += 1
    return frames


def rain():
    st = fx.Stage(); frames = []
    HX, HY = 120, 130
    TC = (262, 134)
    ang = (0.55, -0.83)
    aim = [dict(sw=bow(ang, 1)),
           dict(sw=bow(ang, 2), hdx=-2, bend=1, look='up', dx=-1),
           dict(sw=bow(ang, 4), hdx=-4, bend=3, look='up', dx=-1, bl=(-2, 0), br=(2, 0), tn=3),
           dict(sw=bow(ang, 6), hdx=-6, bend=4, look='up', dx=-2, bl=(-3, 0), br=(2, 0), tn=2, face='shout'),
           dict(sw=bow(ang, 7), hdx=-7, bend=5, look='up', dx=-2, bl=(-3, 0), br=(3, 0), tn=2, face='shout'),
           dict(sw=bow(ang, 0, False), hdx=-4, bend=3, look='up', dx=-1, bl=(-2, 0), br=(2, 0)),
           dict(sw=bow(ang, -1, False), hdx=-2, bend=2, look='up'),
           dict(sw=bow(ang, 0, False))]
    spr = C.anim('right', 'attack', 'archer', aim)
    rnd = random.Random(11)
    enemies = [fx.Enemy(TC[0] - 24, TC[1] - 2, M.SLIME), fx.Enemy(TC[0] + 8, TC[1] - 12, M.SLIME_B), fx.Enemy(TC[0] + 26, TC[1] + 8, M.SLIME_O), fx.Enemy(TC[0] - 6, TC[1] + 12, M.SLIME)]
    arrows = []
    for i in range(26):
        ang_ = rnd.uniform(0, math.tau); r = rnd.uniform(0, 1) ** .6
        arrows.append((TC[0] + math.cos(ang_) * 40 * r, TC[1] + math.sin(ang_) * 17 * r, 24 + int(i * 0.6) + rnd.randint(0, 1)))
    N = 62
    stuck = []
    for j in range(N):
        back = fx.layer(); front = fx.layer(); sh = (0, 0)
        if j < 3: k = 0
        elif j < 10: k = min(7, 1 + (j - 3) // 2) if j < 9 else 3
        k = None
        # sequencia da pose: pronto(3) -> puxa(1,2,3,4: 7 quadros) -> solta
        if j < 3: pi = 0
        elif j < 5: pi = 1
        elif j < 7: pi = 2
        elif j < 10: pi = 3
        elif j < 14: pi = 4
        elif j < 16: pi = 5
        elif j < 18: pi = 6
        else: pi = 7
        img, tip, behind = spr[pi]
        ox, oy = HX - CW // 2, HY - C.BASE
        # circulo dourado no alvo (marca a area)
        if 12 <= j < 50:
            a = int(min(1, (j - 12) / 8.0) * 190) if j < 42 else int(max(0, (50 - j) / 8.0) * 190)
            fx.magic_circle(back, TC[0], TC[1], 44, 20, -j * .1, a, col=(255, 200, 70))
            fx.dither_ellipse(back, TC[0], TC[1], 40, 17, (255, 210, 90), 30 + int(18 * math.sin(j * .6)))
        # carga (brilho na ponta) e flecha grande subindo
        if tip and 3 <= j < 14 and pi < 5:
            tp = (ox + tip[0], oy + tip[1]); fx.dither_ellipse(front, tp[0], tp[1], 3 + (j - 3) * .5, 3 + (j - 3) * .5, (255, 220, 90), 130)
        if tip and pi == 5 and j == 14: launch = (ox + tip[0], oy + tip[1])
        if 14 <= j < 20:
            lx, ly = ox + 30, oy + 18
            u = (j - 14)
            ax, ay = lx + ang[0] * u * 18, ly + ang[1] * u * 18
            fx.arrow(front, ax, ay, ang, L=16, glow=True, f=j)
        # flechas caindo
        for (ix, iy, t) in arrows:
            if t - 4 <= j < t:
                u = (j - (t - 4) + 1) / 4.0
                ax, ay = ix + (1 - u) * 9, iy - 4 - (1 - u) * 72
                fx.arrow(front, ax, ay, (-.12, .99), L=13, glow=True, f=j)
                shd = ImageDraw.Draw(back); rr = 2 + u * 2
                shd.ellipse([ix - rr, iy - rr * .4, ix + rr, iy + rr * .4], fill=(30, 20, 10, 110))
            if j == t:
                for e in enemies:
                    if math.hypot(e.x0 - ix, (e.y0 - iy) * 1.6) < 15:
                        e.hit((0, 0), '18')
                stuck.append((ix, iy, t))
            if t <= j < t + 3: fx.dust(front, ix, iy + 1, j - t, n=4)
        # flechas cravadas (ficam e somem)
        for (ix, iy, t) in stuck:
            if j >= t and j < t + 34:
                a = 255 if j < t + 24 else int(255 * (1 - (j - t - 24) / 10.0))
                ov = fx.layer(); fx.arrow(ov, ix, iy - 8, (0.0, 1.0), L=8)
                if a < 255: ov.putalpha(ov.getchannel('A').point(lambda v: int(v * a / 255)))
                front = Image.alpha_composite(front, ov)
        dyn = []
        for e in enemies:
            eimg, ex_, ey_, up, ek = e.step()
            shd = fx.layer(); ImageDraw.Draw(shd).ellipse([ex_ - 8, ey_ - 2, ex_ + 8, ey_ + 3], fill=(0, 0, 0, 70)); back = Image.alpha_composite(shd, back)
            dyn.append(dict(img=eimg, x=ex_ - 9, y=ey_ - 13 - up, foot=ey_, ek=ek, ex=ex_, ey=ey_))
        hs = fx.layer(); ImageDraw.Draw(hs).ellipse([HX - 9, HY - 2, HX + 9, HY + 3], fill=(0, 0, 0, 90)); back = Image.alpha_composite(hs, back)
        dyn.append(dict(img=img, x=ox, y=oy, foot=HY))
        im = st.compose(j, back, dyn, front, shake=sh)
        for d in dyn:
            if 'ek' in d and d['ek'] is not None and d['ek'] >= 1 and d['ek'] % 2 == 1:
                fx.draw_number(im, d['ex'] + 6, d['ey'] - 26 - d['ek'] * 1.2, '18')
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
    fr = rain(); save(fr, 'arqueiro_chuva.gif'); print('chuva', len(fr))
    fr = basic(); save(fr, 'arqueiro_basico.gif'); print('basico', len(fr))
