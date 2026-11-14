#!/usr/bin/env python3
"""Cena: heroi chibi anda e ataca nas 4 direcoes (direita, baixo, esquerda, cima) contra um slime."""
import os, math
from PIL import Image, ImageDraw, ImageChops
import chibi as C
import teste_clareira as T
import px2_mobs as M

OUT = T.OUT
W, H = T.W, T.H
HOLD = [3, 2, 2, 3, 1, 1, 3, 3, 2, 3]
IMPACT = 6
_c = {}
CW = C.W


def flip(im): return im.transpose(Image.FLIP_LEFT_RIGHT)


def sprites(face, kind):
    k = (face, kind)
    if k not in _c:
        view = 'right' if face in ('right', 'left') else face
        res = C.anim(view, kind)
        if face == 'left': res = [(flip(i), (CW - 1 - t[0], t[1]) if t else None) for i, t in res]
        _c[k] = res
    return _c[k]


def flash(img):
    o = img.copy(); px = o.load()
    for y in range(o.height):
        for x in range(o.width):
            if px[x, y][3]: px[x, y] = (255, 255, 255, 255)
    return o


def slime_img(name, pal=M.SLIME):
    g, p = M.slime_frame(name, pal); return g.render(p)


DIRS = {'right': (1, 0), 'down': (0, 1), 'left': (-1, 0), 'up': (0, -1)}


def build():
    bg, wm = T.build_static(); objs = T.objects()
    CX, CY = 200, 150
    seq = []
    for face in ('right', 'down', 'left', 'up'):
        dx, dy = DIRS[face]
        sp = 1.5
        n_walk = 16
        hx, hy = CX - dx * sp * n_walk, CY - dy * sp * n_walk
        walk = sprites(face, 'walk'); idle = sprites(face, 'idle'); atk = sprites(face, 'attack')
        sl = (CX + dx * 26, CY + dy * 20)
        fr = []
        for f in range(n_walk):
            fr.append(dict(face=face, spr=walk[f % 8], pos=(hx, hy), slime=('idle', sl)))
            hx += dx * sp; hy += dy * sp
        for f in range(6):
            fr.append(dict(face=face, spr=idle[f % 6], pos=(CX, CY), slime=('idle', sl)))
        imp = None
        for k, hold in enumerate(HOLD):
            for t in range(hold):
                if k == IMPACT and t == 0: imp = len(fr)
                fr.append(dict(face=face, spr=atk[k], pos=(CX, CY), slime=('idle', sl), key=k, t=t))
        react = [('squash', 0, True), ('squash', 0, True), ('stretch', 3, False), ('air', 7, False), ('air', 10, False), ('air', 7, False),
                 ('squash', 0, False), ('idle', 0, False), ('idle', 0, False), ('idle', 0, False), ('idle', 0, False), ('idle', 0, False)]
        for i, r in enumerate(react):
            idx = imp + i
            while idx >= len(fr): fr.append(dict(face=face, spr=idle[idx % 6], pos=(CX, CY), slime=None))
            fr[idx]['slime'] = ('react', sl, i, r, (dx, dy)); fr[idx]['hit'] = i
        while len(fr) < imp + 16: fr.append(dict(face=face, spr=idle[len(fr) % 6], pos=(CX, CY), slime=None))
        for f in fr:
            if f['slime'] is None: f['slime'] = ('idle', sl)
        seq += fr
    return bg, wm, objs, seq


def render():
    bg, wm, objs, seq = build()
    cache = {}; out = []; tips = []
    for i, fr in enumerate(seq):
        im = bg.copy()
        ph = (i // 4) % 6
        if ph not in cache: cache[ph] = T.water_layer(wm, ph)
        im.paste(cache[ph].convert('RGB'), (0, 0), cache[ph])
        for o in objs:
            if 'sh' in o: T.shadow(im, *o['sh'])
        spr, tip = fr['spr']
        ox, oy = fr['pos'][0] - CW // 2, fr['pos'][1] - C.BASE
        T.shadow(im, fr['pos'][0], fr['pos'][1], 9, 3, 90)
        dyn = [dict(img=spr, x=ox, y=oy, foot=fr['pos'][1])]
        s = fr['slime']
        if s[0] == 'react':
            sl, idx, r, d = s[1], s[2], s[3], s[4]
            name, up, fl = r
            back = min(idx, 6) * 2.2
            sx, sy = sl[0] + d[0] * back, sl[1] + d[1] * back * .7
            simg = slime_img(name)
            if fl: simg = flash(simg)
            T.shadow(im, sx, sy, 9 - up * .4, 3, 70)
            dyn.append(dict(img=simg, x=sx - 9, y=sy - 13 - up, foot=sy))
        else:
            sx, sy = s[1]
            T.shadow(im, sx, sy, 9, 3, 70)
            dyn.append(dict(img=slime_img('idle'), x=sx - 9, y=sy - 13, foot=sy))
        tips.append((ox + tip[0], oy + tip[1]) if (fr.get('key') is not None and tip) else None)
        for o in sorted(list(objs) + dyn, key=lambda o: o['foot']):
            T.put(im, o['img'], o['x'], o['y'])
        d = ImageDraw.Draw(im)
        if fr.get('key') is not None and fr['key'] >= 4:
            pts = [p for p in tips[-7:] if p][-5:]
            if len(pts) >= 3:
                smp = []
                P_ = [pts[0]] + pts + [pts[-1]]
                for a in range(1, len(P_) - 2):
                    p0, p1, p2, p3 = P_[a - 1], P_[a], P_[a + 1], P_[a + 2]
                    for u in [k / 6 for k in range(6)]:
                        smp.append(tuple(.5 * ((2 * p1[c]) + (-p0[c] + p2[c]) * u + (2 * p0[c] - 5 * p1[c] + 4 * p2[c] - p3[c]) * u * u + (-p0[c] + 3 * p1[c] - 3 * p2[c] + p3[c]) * u ** 3) for c in (0, 1)))
                smp.append(pts[-1])
                for q in range(len(smp) - 1):
                    t_ = q / max(1, len(smp) - 2)
                    col = (255, 255, 255) if t_ > .55 else (170, 220, 255) if t_ > .25 else (110, 170, 240)
                    d.line([smp[q], smp[q + 1]], fill=col, width=1 + int(t_ * 2))
        if fr.get('hit') is not None and fr['hit'] < 4:
            sl = s[1]
            cx, cy = sl[0], sl[1] - 8
            for kd in range(8):
                ang = kd * .8 + fr['hit'] * .5; r = 3 + fr['hit'] * 5
                x, y = cx + math.cos(ang) * r, cy + math.sin(ang) * r * .8
                d.rectangle([x, y, x + 1, y + 1], fill=(255, 240, 150) if kd % 2 else (255, 255, 255))
        if fr.get('hit') is not None and fr['hit'] >= 1:
            n = T.number('27'); sl = s[1]
            im.paste(n.convert('RGB'), (int(sl[0]) + 8, int(sl[1] - 20 - fr['hit'] * 1.2)), n)
        if fr.get('key') in (6, 7) and fr.get('t', 9) < 2:
            im = ImageChops.offset(im, 1 if i % 2 else -1, 0)
        out.append(im)
    return out


def save(frames, name, scale=2):
    big = [f.convert('RGB').resize((W * scale, H * scale), Image.NEAREST) for f in frames]
    n = len(big); pick = [big[i * n // 6] for i in range(6)]
    col = Image.new('RGB', (pick[0].width * 3, pick[0].height * 2))
    for i, p in enumerate(pick): col.paste(p, ((i % 3) * p.width, (i // 3) * p.height))
    pal = col.quantize(colors=220, method=Image.MEDIANCUT, dither=Image.NONE)
    q = [im.quantize(palette=pal, dither=Image.NONE) for im in big]
    q[0].save(os.path.join(OUT, name), save_all=True, append_images=q[1:], duration=80, loop=0, disposal=1)


if __name__ == '__main__':
    fr = render()
    save(fr, 'chibi_ataque_4direcoes.gif')
    C.sheet(os.path.join(OUT, 'chibi_3vistas.png'), 3)
    print('ok', len(fr))
