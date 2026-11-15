#!/usr/bin/env python3
"""Cena: heroi e goblin ANDANDO (ciclo de 4 poses, pernas alternando), slimes pulando. Sprites por partes (px2_*)."""
import os, math
from PIL import Image
import teste_clareira as T
import px2_hero as H
import px2_mobs as M

W, HH, OUT = T.W, T.H, T.OUT
CYC = [0, 0, 1, 2, 2, 3]  # 6 ticks por ciclo


class Walker:
    def __init__(self, pts, speed):
        self.pts = pts; self.sp = speed
        self.seg = [math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:] + pts[:1])]
        self.per = sum(self.seg)

    def at(self, f):
        dist = (self.sp * f) % self.per
        for i, L in enumerate(self.seg):
            if dist <= L:
                a, b = self.pts[i], self.pts[(i + 1) % len(self.pts)]
                u = dist / L; dx, dy = b[0] - a[0], b[1] - a[1]
                face = ('right' if dx > 0 else 'left') if abs(dx) > abs(dy) else ('down' if dy > 0 else 'up')
                return a[0] + dx * u, a[1] + dy * u, face, CYC[f % 6]
            dist -= L


_cache = {}


def hero_spr(face, step):
    k = ('h', face, step)
    if k not in _cache:
        fc = 'right' if face == 'left' else face
        im = H.render(H.hero_frame(fc, step))
        _cache[k] = im.transpose(Image.FLIP_LEFT_RIGHT) if face == 'left' else im
    return _cache[k]


def gob_spr(face, step):
    k = ('g', face, step)
    if k not in _cache:
        fc = 'right' if face == 'left' else face
        im = M.goblin_frame(fc, step).render(M.GOB, M.GSEL)
        _cache[k] = im.transpose(Image.FLIP_LEFT_RIGHT) if face == 'left' else im
    return _cache[k]


SL_SEQ = [('idle', 0), ('idle', 0), ('squash', 0), ('stretch', 2), ('air', 6), ('air', 7), ('air', 5), ('stretch', 2), ('squash', 0), ('idle', 0), ('idle', 0), ('idle', 0)]


def slime_spr(name, pal):
    k = ('s', name, id(pal))
    if k not in _cache:
        g, p = M.slime_frame(name, pal); _cache[k] = g.render(p)
    return _cache[k]


def clareira(frames=78):
    bg, wm = T.build_static(); objs = T.objects()
    hero = Walker([(160, 112), (250, 112), (250, 150), (160, 150)], 256 / frames)
    gob = Walker([(180, 126), (180, 142), (230, 142), (230, 126)], 140 * 2 / frames)
    cache = {}; out = []
    for f in range(frames):
        im = bg.copy()
        ph = (f // 4) % 6
        if ph not in cache: cache[ph] = T.water_layer(wm, ph)
        im.paste(cache[ph].convert('RGB'), (0, 0), cache[ph])
        for o in objs:
            if 'sh' in o: T.shadow(im, *o['sh'])
        dyn = []
        for w, fn, ax, ay in [(hero, hero_spr, 9, 27), (gob, gob_spr, 10, 25)]:
            x, y, face, st = w.at(f)
            T.shadow(im, x, y, 7, 2.5, 80)
            sp = fn(face, st)
            dyn.append(dict(img=sp, x=x - ax, y=y - ay, foot=y))
        for i, (x, y, pal) in enumerate([(148, 82, M.SLIME), (218, 78, M.SLIME_B), (258, 216, M.SLIME_O)]):
            name, up = SL_SEQ[(f + i * 4) % 12]
            sp = slime_spr(name, pal)
            T.shadow(im, x, y, 8 - up * .5, 3, 70)
            dyn.append(dict(img=sp, x=x - 9, y=y - 13 - up, foot=y))
        for j, (bx, by, col) in enumerate([(150, 100, T.C('#ffffff')), (300, 120, T.C('#ffd23a'))]):
            a = (f / frames + j * .5) * 2 * math.pi
            dyn.append(dict(img=T.butterfly(f // 2 + j, col), x=bx + math.cos(a) * 18, y=by + math.sin(a * 2) * 6, foot=999))
        for o in sorted(list(objs) + dyn, key=lambda o: o['foot']):
            T.put(im, o['img'], o['x'], o['y'])
        out.append(im)
    return out


def save(frames, name):
    big = [f.convert('RGB').resize((W * 2, HH * 2), Image.NEAREST) for f in frames]
    n = len(big); pick = [big[i * n // 6] for i in range(6)]
    col = Image.new('RGB', (pick[0].width * 3, pick[0].height * 2))
    for i, p in enumerate(pick): col.paste(p, ((i % 3) * p.width, (i // 3) * p.height))
    pal = col.quantize(colors=200, method=Image.MEDIANCUT, dither=Image.NONE)
    q = [im.quantize(palette=pal, dither=Image.NONE) for im in big]
    q[0].save(os.path.join(OUT, name), save_all=True, append_images=q[1:], duration=80, loop=0, disposal=1)


def sheets():
    import pxtool
    items = [H.render(H.hero_frame(f, s)) for f in ('down', 'up', 'right') for s in ('stand', 0, 1, 2, 3)]
    pxtool.sheet(items, 8, cols=5).convert('RGB').save(os.path.join(OUT, 'heroi_andar.png'))
    items = [M.goblin_frame(f, s).render(M.GOB, M.GSEL) for f in ('down', 'up', 'right') for s in ('stand', 0, 1, 2, 3)]
    items += [slime_spr(n, p) for n in ('idle', 'squash', 'stretch', 'air') for p in (M.SLIME, M.SLIME_B)]
    pxtool.sheet(items, 8, cols=8).convert('RGB').save(os.path.join(OUT, 'goblin_slime_andar.png'))


if __name__ == '__main__':
    sheets()
    save(clareira(), 'andar_clareira_v2.gif')
    print('ok')
