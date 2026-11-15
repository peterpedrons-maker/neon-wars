#!/usr/bin/env python3
"""MAGO (chibi): ataque basico 'Bola de Fogo' nas 4 direcoes + skill 'Chuva de Meteoros' (fogo do ceu).
Saidas: mmo/proto_pixel/mago_basico.gif, mago_meteoros.gif"""
import os, math, random
from PIL import Image, ImageDraw
import chibi as C
import teste_clareira as T
import px2_mobs as M
import fx

OUT = T.OUT
W, H = T.W, T.H
CW = C.W


def flip(im): return im.transpose(Image.FLIP_LEFT_RIGHT)


# ------------------------------------------------------------------ poses do mago (8 poses de conjuracao)
def staff(ang, orb, ln=24): return dict(kind='staff', ang=ang, orb=orb, len=ln)


CAST_S = [
    dict(sw=staff(180, 1), ar=(1, 0)),
    dict(sw=staff(188, 2), ar=(0, -1), al=(1, -2), hdx=-1, bdx=-1),
    dict(sw=staff(198, 3), ar=(-1, -3), al=(2, -5), hdx=-2, bdx=-1, dx=-1, face='shout'),
    dict(sw=staff(160, 3), ar=(1, -3), al=(2, -5), hdx=-1, bdx=-1, dx=-1, tn=2),
    dict(sw=staff(112, 3, 22), ar=(5, -1), al=(1, -2), hdx=3, bdx=1, dx=2, face='shout'),
    dict(sw=staff(104, 1, 22), ar=(5, 0), al=(0, -1), hdx=3, bdx=1, dx=3),
    dict(sw=staff(128, 1), ar=(3, 0), hdx=2, bdx=1, dx=2),
    dict(sw=staff(172, 1), ar=(1, 0), dx=1),
]


def front_params(table, view):
    out = []
    for i, p in enumerate(table):
        q = dict(p)
        for k in ('dx', 'hdx', 'bdx'): q.pop(k, None)
        lung = 1 if i in (4, 5) else 0
        q['dy'] = lung if view == 'down' else -lung if False else 0
        q['hdy'] = lung if view == 'down' else 0
        sw = dict(q['sw'])
        if i in (4, 5): sw['len'] = 18
        q['sw'] = sw
        out.append(q)
    return out


def sprite_set(view, face, table):
    v = 'right' if face in ('right', 'left') else face
    ps = table if v == 'right' else front_params(table, v)
    res = C.anim(v, 'attack', 'mage', ps)
    if face == 'left': res = [(flip(i), (CW - 1 - t[0], t[1]) if t else None, b) for i, t, b in res]
    return res


def idle_staff(view, face, n=6):
    v = 'right' if face in ('right', 'left') else face
    ps = [dict(sw=staff(180, 1 + (f % 6 in (2, 3)) * 0, 24), tn=3 if f % 6 < 3 else 4, ar=(1, 0)) for f in range(n)]
    res = C.anim(v, 'attack', 'mage', ps)
    if face == 'left': res = [(flip(i), (CW - 1 - t[0], t[1]) if t else None, b) for i, t, b in res]
    return res


DIRS = {'right': (1, 0), 'down': (0, 1), 'left': (-1, 0), 'up': (0, -1)}
HOLD = [2, 2, 2, 2, 2, 2, 2, 3]


# sequencia da conjuracao: (pose, quadros, intensidade da aura inicial -> final)
CHAN = [(0, 3, 0.0, 0.0), (1, 4, 0.2, 0.35), (2, 7, 0.4, 0.85), (3, 5, 0.9, 1.0), (4, 2, 1.0, 0.7), (5, 2, 0.6, 0.4), (6, 2, 0.3, 0.2), (7, 4, 0.1, 0.0)]


def basic():
    st = fx.Stage(); frames = []
    CX, CY = 170, 150
    gi = 0
    for face in ('right', 'down', 'left', 'up'):
        d = DIRS[face]
        cast = sprite_set('right', face, CAST_S); idle = idle_staff('right', face)
        en = fx.Enemy(CX + d[0] * 66, CY + d[1] * 40)
        seq = [('idle', f, 0.0) for f in range(3)]
        for pi, n, k0, k1 in CHAN:
            for t in range(n): seq.append(('cast', pi, k0 + (k1 - k0) * (t / max(1, n - 1)), t))
        for f in range(14): seq.append(('post', f, 0.0))
        launch = next(j for j, s in enumerate(seq) if s[0] == 'cast' and s[1] == 4 and s[3] == 0)
        FLY = 6
        impact = launch + FLY
        orb_start = None
        for j, s in enumerate(seq):
            back = fx.layer(); front = fx.layer(); sh = (0, 0)
            if s[0] in ('idle', 'post'): spr = idle[j % 6]
            else: spr = cast[s[1]]
            img, tip, behind = spr
            wob = (1 if (j % 2) else 0) if (s[0] == 'cast' and s[1] in (2, 3)) else 0       # tremor de energia
            ox, oy = CX - CW // 2 + (wob if s[0] == 'cast' and s[1] == 3 else 0), CY - C.BASE
            k = s[2] if s[0] == 'cast' else 0.0
            if k > 0: fx.aura(back, CX, CY - 17, j, k)                                        # AURA VERMELHA atras do corpo
            if tip and s[0] == 'cast':
                orb = (ox + tip[0], oy + tip[1])
                rr = 4 + int(k * 5) + (1 if j % 2 else 0)
                fx.dither_ellipse(front, orb[0], orb[1], rr + 3, rr + 3, (255, 90, 40), int(80 + 100 * k))
                fx.disc(front, orb[0], orb[1], rr - 1, (255, 170, 60), 150)
                fx.embers(front, orb[0], orb[1], j, n=6, spread=8, rise=16)
                if s[1] in (1, 2, 3): fx.converge(front, orb[0], orb[1], j, k)
                if s[1] == 4 and s[3] == 0:
                    orb_start = orb; fx.disc(front, orb[0], orb[1], 9, (255, 240, 200), 200)       # clarao ao lancar
            if launch <= j < impact and orb_start:
                u = (j - launch + 1) / float(FLY)
                tx, ty = en.x0, en.y0 - 8
                px, py = orb_start[0] + (tx - orb_start[0]) * u, orb_start[1] + (ty - orb_start[1]) * u
                vec = (tx - orb_start[0], ty - orb_start[1]); L = math.hypot(*vec) or 1
                fx.fireball(front, px, py, 5, j, (vec[0] / L, vec[1] / L), tail=11)
            if j == impact: en.hit((d[0] if d[0] else 0.0, d[1] if d[1] else 0.0), '31')
            if impact <= j < impact + 8:
                fx.explosion(back, front, en.x0, en.y0, j - impact, R=14, seed=3)
                if j - impact < 2: sh = (1 if j % 2 else -1, 0)
            eimg, ex_, ey_, up, ek = en.step()
            dyn_e = dict(img=eimg, x=ex_ - 9, y=ey_ - 13 - up, foot=ey_)
            shd = fx.layer(); ImageDraw.Draw(shd).ellipse([ex_ - 8, ey_ - 2, ex_ + 8, ey_ + 3], fill=(0, 0, 0, 70)); back = Image.alpha_composite(shd, back)
            hs = fx.layer(); ImageDraw.Draw(hs).ellipse([CX - 9, CY - 2, CX + 9, CY + 3], fill=(0, 0, 0, 90)); back = Image.alpha_composite(hs, back)
            hero = dict(img=img, x=ox, y=oy, foot=CY)
            im = st.compose(gi, back, [hero, dyn_e], front, shake=sh)
            if ek is not None and ek >= 1:
                fx.draw_number(im, ex_ + 6, ey_ - 26 - ek * 1.2, '31')
            frames.append(im); gi += 1
    return frames


# ------------------------------------------------------------------ SKILL: CHUVA DE METEOROS
def meteors():
    st = fx.Stage(); frames = []
    HX, HY = 120, 130
    TC = (262, 134)
    side = sprite_set('right', 'right', CAST_S)
    # poses de canalizacao (ambas as maos ao alto)
    chan = []
    for k in range(8):
        orb = 2 if k < 4 else 3
        chan.append(dict(sw=staff(180, orb, 26), ar=(1, -6), al=(3, -7), hdy=-1 if k % 2 else 0, tn=3 if k % 2 else 4, face='shout' if k > 3 else None))
    chan = [{k: v for k, v in p.items() if v is not None} for p in chan]
    chan_spr = C.anim('right', 'attack', 'mage', chan)
    idle = idle_staff('right', 'right')
    enemies = [fx.Enemy(TC[0] - 24, TC[1] - 2, M.SLIME), fx.Enemy(TC[0] + 8, TC[1] - 12, M.SLIME_B), fx.Enemy(TC[0] + 26, TC[1] + 8, M.SLIME_O), fx.Enemy(TC[0] - 6, TC[1] + 12, M.SLIME)]
    impacts = [(18, (TC[0] - 16, TC[1] - 2)), (22, (TC[0] + 18, TC[1] + 7)), (25, (TC[0] + 2, TC[1] - 9)), (29, (TC[0] - 24, TC[1] + 9)), (33, (TC[0] + 12, TC[1] + 10))]
    FALL = 7
    decals = []
    N = 56
    for j in range(N):
        back = fx.layer(); front = fx.layer(); sh = (0, 0)
        # pose do mago
        if j < 2: spr = idle[j % 6]
        elif j < 10: spr = chan_spr[j - 2]
        elif j < 13: spr = side[[4, 5, 5][j - 10]]
        elif j < 17: spr = side[[6, 7, 7, 7][j - 13]]
        else: spr = idle[j % 6]
        img, tip, behind = spr
        ox, oy = HX - CW // 2, HY - C.BASE
        # circulo magico no chao
        if 2 <= j < 44:
            a = int(min(1, (j - 2) / 6.0) * 200) if j < 36 else int(max(0, (44 - j) / 8.0) * 200)
            fx.magic_circle(back, TC[0], TC[1], 44, 20, j * .12, a)
            if j < 40: fx.dither_ellipse(back, TC[0], TC[1], 40, 17, (255, 120, 40), 40 + int(25 * math.sin(j * .5)))
        # AURA VERMELHA do mago enquanto canaliza
        if 2 <= j < 17:
            kk = min(1.0, (j - 2) / 9.0) if j < 13 else max(0.0, 1 - (j - 13) / 4.0)
            fx.aura(back, HX, HY - 17, j, kk)
        # brilho do orbe + aura enquanto canaliza
        if tip and 2 <= j < 14:
            orb = (ox + tip[0], oy + tip[1])
            r = 6 + int(min(j - 2, 8) * .6) + (j % 2)
            fx.dither_ellipse(front, orb[0], orb[1], r + 4, r + 4, (255, 150, 50), 110)
            fx.disc(front, orb[0], orb[1], r - 2, (255, 210, 90), 160)
            fx.embers(front, orb[0], orb[1] + 4, j, n=8, spread=10, rise=24)
        if 3 <= j < 12:  # raios de energia do circulo ate o orbe
            for i in range(3):
                ang = j * .5 + i * 2.1
                ImageDraw.Draw(back).line([TC[0] + math.cos(ang) * 30, TC[1] + math.sin(ang) * 12, TC[0] + math.cos(ang) * 6, TC[1] - 6 - (j - 3) * 3], fill=(255, 190, 80, 120))
        # ceu em chamas
        if 10 <= j < 44:
            a = min(80, (j - 10) * 12) if j < 36 else max(0, 80 - (j - 36) * 10)
            fx.vignette_top(front, a)
        dyn = []
        # sombra de cada meteoro + meteoro + explosao
        for (ij, (ix, iy)) in impacts:
            t0 = ij - FALL
            if t0 - 3 <= j < ij:   # sombra crescendo
                k = (j - (t0 - 3)) / float(FALL + 3)
                shd = ImageDraw.Draw(back); rr = 3 + k * 10
                shd.ellipse([ix - rr, iy - rr * .45, ix + rr, iy + rr * .45], fill=(30, 10, 10, 120), outline=(255, 90, 30, 160))
            if t0 <= j < ij:
                u = (j - t0 + 1) / float(FALL)
                mx = ix + (1 - u) * 46; my = iy - 6 - (1 - u) * 118
                fx.meteor(front, mx, my, 5 + u * 2, j)
            if j == ij:
                for e in enemies:
                    dd = math.hypot(e.x0 - ix, (e.y0 - iy) * 1.6)
                    if dd < 28:
                        v = (e.x0 - ix, e.y0 - iy); L = math.hypot(*v) or 1
                        e.hit((v[0] / L, v[1] / L), str(40 + (ij * 7) % 30), burn=8)
                decals.append((ix, iy + 2, 12, 5, 110, j))
            if ij <= j < ij + 8:
                fx.explosion(back, front, ix, iy, j - ij, R=17, seed=ij)
                if j - ij < 3: sh = (1 if j % 2 else -1, 1 if (j // 2) % 2 else 0)
        # inimigos
        for e in enemies:
            eimg, ex_, ey_, up, ek = e.step()
            shd = fx.layer(); ImageDraw.Draw(shd).ellipse([ex_ - 8, ey_ - 2, ex_ + 8, ey_ + 3], fill=(0, 0, 0, 70)); back = Image.alpha_composite(shd, back)
            dyn.append(dict(img=eimg, x=ex_ - 9, y=ey_ - 13 - up, foot=ey_, ek=ek, ex=ex_, ey=ey_))
            if e.burn > 0 or (ek is not None):
                pass
        hero = dict(img=img, x=ox, y=oy, foot=HY)
        hs = fx.layer(); ImageDraw.Draw(hs).ellipse([HX - 9, HY - 2, HX + 9, HY + 3], fill=(0, 0, 0, 90)); back = Image.alpha_composite(hs, back)
        dyn.append(hero)
        dec = [(cx, cy, rx, ry, a if (j - t) < 24 else int(a * max(0, 1 - (j - t - 24) / 12.0))) for (cx, cy, rx, ry, a, t) in decals]
        im = st.compose(j, back, dyn, front, extra_decals=dec, shake=sh)
        # chamas nos inimigos queimando e numeros
        for d in dyn:
            if 'ek' in d and d['ek'] is not None:
                if d['ek'] >= 1: fx.draw_number(im, d['ex'] + 6, d['ey'] - 26 - d['ek'] * 1.2, '47')
                ov = fx.layer()
                for q in range(6):
                    ImageDraw.Draw(ov).rectangle([d['ex'] - 6 + q * 2, d['ey'] - 12 - ((j + q * 3) % 8), d['ex'] - 5 + q * 2, d['ey'] - 11 - ((j + q * 3) % 8)], fill=(255, 150 if q % 2 else 220, 40, 220))
                imr = im.convert('RGBA'); imr = Image.alpha_composite(imr, ov); im = imr.convert('RGB')
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
    fr = meteors(); save(fr, 'mago_meteoros.gif'); print('meteoros', len(fr))
    fr = basic(); save(fr, 'mago_basico.gif'); print('basico', len(fr))
