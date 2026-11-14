#!/usr/bin/env python3
"""GUERREIRO (chibi): skill 'Golpe Sismico' - pula, bate a espada no chao, rachaduras + onda de choque jogam os inimigos para cima.
Saida: mmo/proto_pixel/guerreiro_sismico.gif"""
import os, math, random
from PIL import Image, ImageDraw
import chibi as C
import teste_clareira as T
import px2_mobs as M
import fx

OUT = T.OUT
W, H = T.W, T.H
CW = C.W


def sw(ang): return dict(ang=ang, len=12, side='r')


POSES = [
    dict(sw=sw(165)),
    dict(tn=2, sw=sw(175), ar=(0, -1)),
    dict(tn=4, ar=(0, -4), al=(0, -3), sw=sw(190)),
    dict(tn=4, ar=(0, -6), al=(1, -5), sw=sw(200), face='shout'),
    dict(tn=4, ar=(0, -7), al=(1, -6), sw=sw(205), face='shout'),
    dict(tn=3, ar=(-1, -2), al=(1, -1), sw=sw(290), face='shout'),
    dict(tn=2, dy=2, ar=(-1, 3), al=(0, 2), bl=(-1, 0), br=(2, 0), sw=sw(358), face='shout'),
    dict(tn=2, dy=2, ar=(-1, 3), al=(0, 2), bl=(-1, 0), br=(2, 0), sw=sw(352)),
    dict(tn=3, dy=1, sw=sw(20)),
    dict(tn=3, sw=sw(150)),
]
HOLD = [3, 2, 2, 2, 2, 1, 3, 3, 2, 4]
JUMP = [0, 0, 5, 9, 11, 6, 0, 0, 0, 0]


def crack_lines(cx, cy, n=9, seed=3):
    rnd = random.Random(seed)
    lines = []
    for i in range(n):
        ang = i * math.tau / n + rnd.uniform(-.2, .2)
        pts = [(cx, cy)]
        L = rnd.uniform(34, 58)
        x, y = cx, cy
        for s in range(8):
            ang += rnd.uniform(-.45, .45)
            step = L / 8
            x += math.cos(ang) * step; y += math.sin(ang) * step * .5
            pts.append((x, y))
        lines.append(pts)
    return lines


def run():
    st = fx.Stage(); frames = []
    CX, CY = 200, 152
    spr = C.anim('down', 'attack', 'warrior', POSES)
    cracks = crack_lines(CX + 6, CY, 9)
    en_pos = [(CX - 52, CY + 6, M.SLIME), (CX + 54, CY + 4, M.SLIME_B), (CX - 30, CY + 30, M.SLIME_O), (CX + 34, CY + 32, M.SLIME), (CX, CY - 34, M.SLIME_B)]
    enemies = [fx.Enemy(x, y, p) for x, y, p in en_pos]
    seq = [('pre', f) for f in range(3)]
    for k, h in enumerate(HOLD):
        for t in range(h): seq.append(('a', k, t))
    for f in range(12): seq.append(('post', f))
    imp = next(i for i, s in enumerate(seq) if s[0] == 'a' and s[1] == 6 and s[2] == 0)
    rnd = random.Random(5)
    debris = [(rnd.uniform(-1.2, 1.2), rnd.uniform(-5.5, -2.5), rnd.choice([(120, 110, 100), (170, 160, 140), (80, 70, 60)])) for _ in range(16)]
    scorch = []
    for j, s in enumerate(seq):
        back = fx.layer(); front = fx.layer(); shk = (0, 0)
        if s[0] == 'a': k = s[1]; jump = JUMP[k]
        else: k = 0 if s[0] == 'pre' else 9; jump = 0
        img, tip, behind = spr[k]
        ox, oy = CX - CW // 2, CY - C.BASE - jump
        # sombra encolhe no pulo
        sr = 9 - jump * .35
        hs = fx.layer(); ImageDraw.Draw(hs).ellipse([CX - sr, CY - 2, CX + sr, CY + 3], fill=(0, 0, 0, 90 - jump * 3)); back = Image.alpha_composite(hs, back)
        d = j - imp
        if d >= 0:
            # rachaduras que crescem + brilho
            prog = min(1.0, (d + 1) / 5.0)
            dr = ImageDraw.Draw(back)
            for pts in cracks:
                n = max(2, int(len(pts) * prog) + 1)
                seg = pts[:n]
                a = 255 if d < 18 else max(0, int(255 * (1 - (d - 18) / 10.0)))
                dr.line(seg, fill=(255, 150, 50, a // 2), width=3)
                dr.line(seg, fill=(30, 14, 10, a), width=1)
            # onda de choque (anel) + poeira
            if d < 10:
                rx = 10 + d * 9; a = max(0, 240 - d * 24)
                dr.ellipse([CX + 6 - rx, CY - rx * .45, CX + 6 + rx, CY + rx * .45], outline=(255, 244, 210, a), width=3 if d < 4 else 2)
                dr.ellipse([CX + 6 - rx * .8, CY - rx * .36, CX + 6 + rx * .8, CY + rx * .36], outline=(255, 190, 90, a // 2), width=1)
                fx.dither_ellipse(front, CX + 6, CY - 4 - d, rx * .55, rx * .22, (190, 170, 130), max(0, 170 - d * 18))
            # pedras voando
            for i, (vx, vy, col) in enumerate(debris):
                t = d
                if 0 <= t < 14:
                    x = CX + 6 + vx * t * 3.2; y = CY - 2 + vy * t + .55 * t * t
                    if y < CY + 4: ImageDraw.Draw(front).rectangle([x, y, x + 1, y + 1], fill=col + (255,))
            if d < 5: shk = (2 if j % 2 else -2, 1 if j % 2 else 0)
            elif d < 9: shk = (1 if j % 2 else -1, 0)
            if d == 0: scorch.append(1)
        # inimigos: onda atinge conforme distancia
        for e in enemies:
            dist = math.hypot(e.x0 - (CX + 6), (e.y0 - CY) * 2.2)
            tarr = int(dist / 9.0)
            if d == tarr and e.k is None:
                v = (e.x0 - CX, e.y0 - CY); L = math.hypot(*v) or 1
                e.hit((v[0] / L, v[1] / L), '55')
        dyn = []
        for e in enemies:
            eimg, ex_, ey_, up, ek = e.step()
            hh = up * 1.8 if ek is not None else 0
            shd = fx.layer(); ImageDraw.Draw(shd).ellipse([ex_ - 8, ey_ - 2, ex_ + 8, ey_ + 3], fill=(0, 0, 0, 70)); back = Image.alpha_composite(shd, back)
            dyn.append(dict(img=eimg, x=ex_ - 9, y=ey_ - 13 - hh, foot=ey_, ek=ek, ex=ex_, ey=ey_))
        dyn.append(dict(img=img, x=ox, y=oy, foot=CY))
        im = st.compose(j, back, dyn, front, shake=shk)
        for q in dyn:
            if 'ek' in q and q['ek'] is not None and q['ek'] >= 1:
                fx.draw_number(im, q['ex'] + 6, q['ey'] - 28 - q['ek'] * 1.4, '55')
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
    fr = run(); save(fr, 'guerreiro_sismico.gif'); print('ok', len(fr))
