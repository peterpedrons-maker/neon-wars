#!/usr/bin/env python3
"""Mockup: heroi (esqueleto 2D, 16 bits) anda ate o goblin e ataca com 10 poses; goblin reage.
Saida: mmo/proto_pixel/ataque_clareira.gif, heroi_ataque.png (folha), heroi_andar8.png"""
import os, math
from PIL import Image, ImageDraw
import skel2d as S
import teste_clareira as T

OUT = T.OUT
W, H = T.W, T.H
PXA = 22                       # x da pelve dentro do sprite
HOLD = [3, 2, 2, 3, 1, 1, 3, 3, 2, 3]   # duracao (ticks) de cada pose do ataque
IMPACT_KEY = 6


def walk_speed():
    """px/quadro para o pe de apoio nao deslizar: usa a variacao do x do tornozelo de apoio."""
    js = [S.side_pose(S.walk_pose(f, 8)) for f in range(8)]
    best = []
    for a, b in zip(js, js[1:] + js[:1]):
        # pe que mais recuou em relacao a pelve
        dn = (b['nank'][0] - b['P'][0]) - (a['nank'][0] - a['P'][0])
        df = (b['fank'][0] - b['P'][0]) - (a['fank'][0] - a['P'][0])
        best.append(min(dn, df))
    return -sum(sorted(best)[:4]) / 4.0


def flash(img):
    o = img.copy(); px = o.load()
    for y in range(o.height):
        for x in range(o.width):
            if px[x, y][3]: px[x, y] = (255, 255, 255, 255)
    return o


def flip(im): return im.transpose(Image.FLIP_LEFT_RIGHT)


def timeline():
    """lista de dict por quadro: hero(img,key), gob(img), x do heroi etc."""
    walk = S.anim_side('walk'); idle = S.anim_side('idle'); atk = S.anim_side('attack')
    gidle = S.anim_side('idle', who='goblin'); ghurt = S.anim_side('hurt', who='goblin')
    sp = walk_speed()
    frames = []
    hx = 133.0
    # 1) anda ate perto (16 quadros)
    for f in range(16):
        frames.append(dict(h=walk[f % 8], hx=hx, g=gidle[f % 8], tag='walk'))
        hx += sp
    # 2) pronto (idle) 6 quadros
    for f in range(6):
        frames.append(dict(h=idle[f % 8], hx=hx, g=gidle[(f + 2) % 8], tag='idle'))
    # 3) ataque (10 poses com duracao)
    k0 = len(frames)
    for k, hold in enumerate(HOLD):
        for t in range(hold):
            frames.append(dict(h=atk[k], hx=hx, g=gidle[(k0 + t) % 8], tag='atk', key=k, t=t))
    # impacto -> goblin reage
    impact = next(i for i, fr in enumerate(frames) if fr.get('key') == IMPACT_KEY and fr['t'] == 0)
    hurt_seq = [0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5]
    for i, hk in enumerate(hurt_seq):
        idx = impact + i
        if idx >= len(frames): frames.append(dict(h=idle[i % 8], hx=hx, g=None, tag='post'))
        frames[idx]['g'] = ghurt[hk]; frames[idx]['hurt'] = i
    # 4) recupera e segura
    while len(frames) < impact + 12 + 8:
        i = len(frames)
        frames.append(dict(h=idle[i % 8], hx=hx, g=gidle[i % 8], tag='post'))
    for fr in frames:
        if fr['g'] is None: fr['g'] = gidle[0]
    return frames, impact


def render():
    bg, wm = T.build_static(); objs = T.objects()
    frames, impact = timeline()
    # remove arvores/pedras na area de luta
    objs = [o for o in objs if not (110 < o['foot'] < 215 and 80 < o['x'] + 8 < 340 and o['foot'] > 140 and False)]
    cache = {}
    FY = 170
    GX = 252
    out = []
    tips_world = []
    for i, fr in enumerate(frames):
        im = bg.copy()
        ph = (i // 4) % 6
        if ph not in cache: cache[ph] = T.water_layer(wm, ph)
        im.paste(cache[ph].convert('RGB'), (0, 0), cache[ph])
        for o in objs:
            if 'sh' in o: T.shadow(im, *o['sh'])
        hs, tip, joints = fr['h']
        ox = fr['hx'] - PXA
        gs, gtip, gj = fr['g']
        gox = GX - (S.W - 1 - 22)
        T.shadow(im, fr['hx'], FY, 9, 3, 80)
        T.shadow(im, GX + 4, FY, 9, 3, 80)
        shake = (1 if i % 2 else -1, 0) if (fr.get('tag') == 'atk' and fr.get('key') in (6, 7) and fr['t'] < 2) else (0, 0)
        dyn = []
        hsp = hs
        dyn.append(dict(img=hsp, x=ox, y=FY - S.GY, foot=FY))
        gsp = flip(gs)
        if fr.get('hurt') is not None and fr['hurt'] < 2: gsp = flash(gsp)
        dyn.append(dict(img=gsp, x=gox, y=FY - S.GY, foot=FY))
        tips_world.append((ox + tip[0], FY - S.GY + tip[1]) if fr.get('tag') == 'atk' else None)
        for o in sorted(list(objs) + dyn, key=lambda o: o['foot']):
            T.put(im, o['img'], o['x'], o['y'])
        d = ImageDraw.Draw(im)
        # rastro da espada: arco suavizado (Catmull-Rom) que some na cauda
        if fr.get('tag') == 'atk' and fr['key'] >= 4:
            pts = [p for p in tips_world[-7:] if p][-5:]
            if len(pts) >= 3:
                sm = []
                P_ = [pts[0]] + pts + [pts[-1]]
                for a in range(1, len(P_) - 2):
                    p0, p1, p2, p3 = P_[a - 1], P_[a], P_[a + 1], P_[a + 2]
                    for u in [k / 6 for k in range(6)]:
                        sm.append(tuple(.5 * ((2 * p1[c]) + (-p0[c] + p2[c]) * u + (2 * p0[c] - 5 * p1[c] + 4 * p2[c] - p3[c]) * u * u + (-p0[c] + 3 * p1[c] - 3 * p2[c] + p3[c]) * u ** 3) for c in (0, 1)))
                sm.append(pts[-1])
                for q in range(len(sm) - 1):
                    t = q / max(1, len(sm) - 2)
                    w = 1 + int(t * 3)
                    col = (255, 255, 255) if t > .55 else (170, 220, 255) if t > .25 else (110, 170, 240)
                    d.line([sm[q], sm[q + 1]], fill=col, width=w)
        # faiscas no impacto
        if fr.get('hurt') is not None and fr['hurt'] < 4:
            cx, cy = GX - 10, FY - 22
            for kdx in range(8):
                ang = kdx * .8 + fr['hurt'] * .5
                r = 4 + fr['hurt'] * 5
                x, y = cx + math.cos(ang) * r, cy + math.sin(ang) * r * .8
                d.rectangle([x, y, x + 1, y + 1], fill=(255, 240, 150) if kdx % 2 else (255, 255, 255))
            if fr['hurt'] < 2:
                d.ellipse([cx - 5, cy - 4, cx + 5, cy + 4], outline=(255, 255, 255))
        # numero de dano
        if fr.get('hurt') is not None and fr['hurt'] >= 1:
            n = T.number('27')
            im.paste(n.convert('RGB'), (GX - 4, int(FY - 50 - fr['hurt'] * 1.2)), n)
        if shake != (0, 0):
            im = ImageChops_offset(im, shake)
        out.append(im)
    return out


def ImageChops_offset(im, shake):
    from PIL import ImageChops
    return ImageChops.offset(im, shake[0], shake[1])


def save(frames, name, scale=2):
    big = [f.convert('RGB').resize((W * scale, H * scale), Image.NEAREST) for f in frames]
    n = len(big); pick = [big[i * n // 6] for i in range(6)]
    col = Image.new('RGB', (pick[0].width * 3, pick[0].height * 2))
    for i, p in enumerate(pick): col.paste(p, ((i % 3) * p.width, (i // 3) * p.height))
    pal = col.quantize(colors=220, method=Image.MEDIANCUT, dither=Image.NONE)
    q = [im.quantize(palette=pal, dither=Image.NONE) for im in big]
    q[0].save(os.path.join(OUT, name), save_all=True, append_images=q[1:], duration=80, loop=0, disposal=1)


def sheets():
    walk = S.anim_side('walk'); atk = S.anim_side('attack')
    def sheet(items, cols, zoom, name):
        cw, ch = S.W, S.HGT
        rows = (len(items) + cols - 1) // cols
        Sh = Image.new('RGBA', (cw * cols, ch * rows), (58, 110, 48, 255))
        for i, im in enumerate(items): Sh.alpha_composite(im, ((i % cols) * cw, (i // cols) * ch))
        Sh.resize((Sh.width * zoom, Sh.height * zoom), Image.NEAREST).convert('RGB').save(os.path.join(OUT, name))
    sheet([r[0] for r in walk], 4, 5, 'heroi_andar8.png')
    sheet([r[0] for r in atk], 5, 5, 'heroi_ataque10.png')


if __name__ == '__main__':
    sheets()
    fr = render()
    save(fr, 'ataque_clareira.gif')
    print('ok', len(fr), 'quadros; velocidade', round(walk_speed(), 2))
