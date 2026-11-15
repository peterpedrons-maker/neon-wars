#!/usr/bin/env python3
"""Cenas de teste: personagens andando em todas as direcoes (passo em salto).
Gera mmo/proto_pixel/andar_clareira.gif e andar_cripta.gif"""
import os, math
import numpy as np
from PIL import Image, ImageDraw
import teste_clareira as T
import teste_rei as R
import chars_dir as D
import px_hero, px_goblin

W, H, OUT = T.W, T.H, T.OUT
CYC = 6  # crouch, air, air, air, land, stand


class Walker:
    def __init__(self, pts, step, start=0.0):
        self.pts = pts; self.step = step
        self.seg = [math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:] + pts[:1])]
        self.per = sum(self.seg); self.start = start

    def at(self, f):
        cyc, ph = divmod(f, CYC)
        moved = cyc * self.step + (self.step * min(max(ph - 1, 0), 3) / 3 if ph <= 4 else self.step)
        # fase 0 agacha, 1-3 no ar (anda), 4 pousa, 5 parado
        dist = (self.start + moved) % self.per
        for i, L in enumerate(self.seg):
            if dist <= L:
                a, b = self.pts[i], self.pts[(i + 1) % len(self.pts)]
                u = dist / L
                dx, dy = b[0] - a[0], b[1] - a[1]
                face = ('right' if dx > 0 else 'left') if abs(dx) > abs(dy) else ('down' if dy > 0 else 'up')
                pose = ['crouch', 'hop', 'hop', 'hop', 'land', 'idle'][ph]
                air = [0, 4, 7, 4, 0, 0][ph]
                return a[0] + dx * u, a[1] + dy * u, face, pose, air
            dist -= L
        return self.pts[0][0], self.pts[0][1], 'down', 'idle', 0


def clareira(frames=78):
    bg, wm = T.build_static()
    objs = T.objects()
    hero = Walker([(160, 112), (250, 112), (250, 150), (160, 150)], 20)
    gob = Walker([(180, 126), (180, 142), (230, 142), (230, 126)], 140 * 2 / 13)
    cache = {}
    out = []
    sl = {(n, k): T.slime(r, k) for n, r in [('g', T.SLIME_G), ('b', T.SLIME_B), ('o', T.SLIME_O)] for k in (-1, 0, 1)}
    for f in range(frames):
        im = bg.copy()
        ph = (f // 4) % 6
        if ph not in cache: cache[ph] = T.water_layer(wm, ph)
        im.paste(cache[ph].convert('RGB'), (0, 0), cache[ph])
        for o in objs:
            if 'sh' in o: T.shadow(im, *o['sh'])
        dyn = []
        for w, fn in [(hero, px_hero.hero_px), (gob, px_goblin.goblin_px)]:
            x, y, face, pose, air = w.at(f)
            T.shadow(im, x, y, 7 - air * .3, 2.5, 80 if air == 0 else 50)
            sp = fn(face, pose, (f // 6) % 2)
            dyn.append(dict(img=sp, x=x - sp.width // 2, y=y - sp.height + 1 - air, foot=y))
        for i, (x, y, name) in enumerate([(148, 82, 'g'), (218, 78, 'b'), (258, 216, 'o')]):
            s = math.sin((f / 12 + i * .33) * 2 * math.pi)
            sp, cx, fy = sl[(name, int(round(s)))]
            jump = max(0, math.sin((f / 12 + i * .33) * 2 * math.pi - .6)) * 4
            T.shadow(im, x, y, 8 - jump * .4, 3, 70)
            dyn.append(dict(img=sp, x=x - cx, y=y - fy - jump, foot=y))
        for j, (bx, by, col) in enumerate([(150, 100, T.C('#ffffff')), (300, 120, T.C('#ffd23a'))]):
            a = (f / frames + j * .5) * 2 * math.pi
            dyn.append(dict(img=T.butterfly(f // 2 + j, col), x=bx + math.cos(a) * 18, y=by + math.sin(a * 2) * 6, foot=999))
        for o in sorted(list(objs) + dyn, key=lambda o: o['foot']):
            T.put(im, o['img'], o['x'], o['y'])
        out.append(im)
    return out


def cripta(frames=72):
    bg = R.crypt_bg(); col = R.column()
    rei = Walker([(190, 150), (270, 150), (270, 190), (190, 190)], 20)
    hero = Walker([(70, 190), (70, 150), (130, 150), (130, 190)], 140 * 2 / 12 * 1.0)
    out = []
    for f in range(frames):
        im = R.lit(bg, f, math.sin(f * .5)).convert('RGBA')
        for tx in (96, 304): R.torch_flame(f, tx, 46, im)
        for cxx in (40, 128, 280, 362): im.alpha_composite(col, (cxx - 11, 20))
        ents = []
        x, y, face, pose, air = rei.at(f)
        sh = Image.new('RGBA', (W, H), (0, 0, 0, 0)); sd = ImageDraw.Draw(sh)
        sd.ellipse([x - 24, y - 4, x + 24, y + 8], fill=(0, 0, 0, 110))
        spr = D.rei_dir(face, pose, f)[0]
        ents.append((y, spr, x - 64, y - 114 - air * .5))
        hx, hy, hf, hp, ha = hero.at(f)
        sd.ellipse([hx - 8, hy - 3, hx + 8, hy + 3], fill=(0, 0, 0, 100))
        hs_ = px_hero.hero_px(hf, hp, (f // 6) % 2); ents.append((hy, hs_, hx - hs_.width // 2, hy - hs_.height + 1 - ha))
        im = Image.alpha_composite(im, sh)
        for _, s, xx, yy in sorted(ents, key=lambda e: e[0]):
            im.alpha_composite(s, (int(xx), int(yy)))
        out.append(im.convert('RGB'))
    return out


def save(frames, name):
    big = [f.convert('RGB').resize((W * 2, H * 2), Image.NEAREST) for f in frames]
    n = len(big); pick = [big[i * n // 6] for i in range(6)]
    col = Image.new('RGB', (pick[0].width * 3, pick[0].height * 2))
    for i, p in enumerate(pick): col.paste(p, ((i % 3) * p.width, (i // 3) * p.height))
    pal = col.quantize(colors=200, method=Image.MEDIANCUT, dither=Image.NONE)
    q = [im.quantize(palette=pal, dither=Image.NONE) for im in big]
    q[0].save(os.path.join(OUT, name), save_all=True, append_images=q[1:], duration=80, loop=0, disposal=1)


if __name__ == '__main__':
    D.sheet()
    save(clareira(), 'andar_clareira.gif')
    save(cripta(), 'andar_cripta.gif')
    print('ok')
