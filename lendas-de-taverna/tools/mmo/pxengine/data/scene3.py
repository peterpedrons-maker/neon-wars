#!/usr/bin/env python3
"""Cena: heroi (skel3) anda ate o alvo e ataca nas 4 direcoes (direita, baixo, esquerda, cima)."""
import os, math
from PIL import Image, ImageDraw, ImageChops
import skel3 as S3
import skel2d as K
import teste_clareira as T
import px2_mobs as M

OUT = T.OUT
W, H = T.W, T.H
HOLD = [3, 2, 2, 3, 1, 1, 3, 3, 2, 3]
IMPACT = 6
_c = {}


def flip(im): return im.transpose(Image.FLIP_LEFT_RIGHT)


def sprites(face, kind):
    k = (face, kind)
    if k in _c: return _c[k]
    if face in ('right', 'left'):
        res = S3.anim(kind)
        if face == 'left': res = [(flip(i), (S3.W - 1 - t[0], t[1]), j) for i, t, j in res]
        org = (30, S3.GY) if face == 'right' else (S3.W - 1 - 30, S3.GY)
    else:
        res = S3.anim_front(kind, back=(face == 'up'))
        org = (32, S3.GY)
    _c[k] = (res, org)
    return _c[k]


def walk_speed():
    K.THIGH = K.SHIN = 5.6
    js = [K.side_pose(dict(K.walk_pose(f, 8), hoff=8.0, px=30)) for f in range(8)]
    best = []
    for a, b in zip(js, js[1:] + js[:1]):
        dn = (b['nank'][0] - b['P'][0]) - (a['nank'][0] - a['P'][0])
        df = (b['fank'][0] - b['P'][0]) - (a['fank'][0] - a['P'][0])
        best.append(min(dn, df))
    return -sum(sorted(best)[:4]) / 4.0


DIRS = {'right': (1, 0), 'down': (0, 1), 'left': (-1, 0), 'up': (0, -1)}


def flash(img):
    o = img.copy(); px = o.load()
    for y in range(o.height):
        for x in range(o.width):
            if px[x, y][3]: px[x, y] = (255, 255, 255, 255)
    return o


def slime_img(name, pal=M.SLIME):
    g, p = M.slime_frame(name, pal); return g.render(p)


def build():
    bg, wm = T.build_static(); objs = T.objects()
    sp_side = walk_speed(); sp_fb = 2.4
    CX, CY = 200, 150          # posicao de ataque do heroi
    seq = []
    for face in ('right', 'down', 'left', 'up'):
        dx, dy = DIRS[face]
        sp = sp_side if dx else sp_fb
        n_walk = 16
        hx, hy = CX - dx * sp * n_walk, CY - dy * sp * n_walk
        walkres, org = sprites(face, 'walk'); idleres, _ = sprites(face, 'idle'); atkres, _ = sprites(face, 'attack')
        slime_pos = (CX + dx * 36, CY + dy * 26 + (0 if dx else 0))
        if dy: slime_pos = (CX, CY + dy * 30)
        fr = []
        for f in range(n_walk):
            fr.append(dict(face=face, spr=walkres[f % 8], pos=(hx, hy), slime=('idle', 0, False, slime_pos), org=org))
            hx += dx * sp; hy += dy * sp
        for f in range(6):
            fr.append(dict(face=face, spr=idleres[f % 8], pos=(CX, CY), slime=('idle', 0, False, slime_pos), org=org))
        imp = None
        for k, hold in enumerate(HOLD):
            for t in range(hold):
                if k == IMPACT and t == 0: imp = len(fr)
                fr.append(dict(face=face, spr=atkres[k], pos=(CX, CY), slime=('idle', 0, False, slime_pos), org=org, key=k, t=t))
        # reacao do slime (12 quadros) + hero volta
        react = [('squash', 0, True), ('squash', 0, True), ('stretch', 3, False), ('air', 7, False), ('air', 10, False), ('air', 7, False),
                 ('squash', 0, False), ('idle', 0, False), ('idle', 0, False), ('idle', 0, False), ('idle', 0, False), ('idle', 0, False)]
        for i, r in enumerate(react):
            idx = imp + i
            while idx >= len(fr): fr.append(dict(face=face, spr=idleres[idx % 8], pos=(CX, CY), slime=None, org=org))
            fr[idx]['slime'] = ('react', i, r, slime_pos, (dx, dy))
            fr[idx]['hit'] = i
        while len(fr) < imp + 12 + 4: fr.append(dict(face=face, spr=idleres[len(fr) % 8], pos=(CX, CY), slime=None, org=org))
        for f in fr:
            if f['slime'] is None: f['slime'] = ('idle', 0, False, slime_pos)
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
        res = fr['spr']; spr, tip, j = res
        ox, oy = fr['pos'][0] - fr['org'][0], fr['pos'][1] - fr['org'][1]
        T.shadow(im, fr['pos'][0], fr['pos'][1] + 1, 10, 3, 85)
        dyn = [dict(img=spr, x=ox, y=oy, foot=fr['pos'][1])]
        # slime
        s = fr['slime']; sx, sy = s[3]
        if s[0] == 'react':
            idx = s[1]; name, up, fl = s[2]
            ddx, ddy = s[4]
            back = min(idx, 6) * 3.0
            sx += ddx * back; sy += ddy * back * .7
            simg = slime_img(name)
            if fl: simg = flash(simg)
            T.shadow(im, sx, sy, 9 - up * .4, 3, 70)
            dyn.append(dict(img=simg, x=sx - 9, y=sy - 13 - up, foot=sy))
        else:
            name = 'idle'; bob = [0, 0, 1, 1][(i // 3) % 4]
            simg = slime_img('idle')
            T.shadow(im, sx, sy, 9, 3, 70)
            dyn.append(dict(img=simg, x=sx - 9, y=sy - 13, foot=sy))
        tips.append((ox + tip[0], oy + tip[1]) if fr.get('key') is not None else None)
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
                    d.line([smp[q], smp[q + 1]], fill=col, width=1 + int(t_ * 3))
        if fr.get('hit') is not None and fr['hit'] < 4:
            cx, cy = s[3][0] if s[0] != 'react' else s[3][0], s[3][1] - 8
            for kd in range(8):
                ang = kd * .8 + fr['hit'] * .5; r = 3 + fr['hit'] * 5
                x, y = cx + math.cos(ang) * r, cy + math.sin(ang) * r * .8
                d.rectangle([x, y, x + 1, y + 1], fill=(255, 240, 150) if kd % 2 else (255, 255, 255))
        if fr.get('hit') is not None and fr['hit'] >= 1:
            n = T.number('27'); im.paste(n.convert('RGB'), (int(s[3][0]) - 4, int(s[3][1] - 34 - fr['hit'] * 1.2)), n)
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
    save(fr, 'ataque_4direcoes.gif')
    # folha dos 3 conjuntos
    S3.sheet_all(os.path.join(OUT, 'heroi_3vistas.png'), 3)
    print('ok', len(fr))
