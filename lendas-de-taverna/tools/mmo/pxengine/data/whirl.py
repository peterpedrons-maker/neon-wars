#!/usr/bin/env python3
"""Habilidade CICLONE (whirlwind): o heroi gira duas voltas com a espada esticada, acertando 3 slimes ao redor.
A lamina e o rastro passam NA FRENTE do corpo quando estao do lado da camera e ATRAS quando estao do lado oposto."""
import os, math
from PIL import Image, ImageDraw, ImageChops
import chibi as C
import teste_clareira as T
import px2_mobs as M
from pxrig import Grid, autoline

OUT = T.OUT
W, H = T.W, T.H
CW = C.W
R = 17.0
BODY_Y = 6          # altura do tronco acima do chao (origem dos bracos e da orbita)


def flip(im): return im.transpose(Image.FLIP_LEFT_RIGHT)


_cache = {}


def body(view, spin_phase, crouch=False, hop=0):
    k = (view, spin_phase % 2, crouch, hop)
    if k in _cache: return _cache[k]
    p = dict(tn=2 if crouch else 3, dy=-hop, face='shout', nomitt=True)
    if view == 'right':
        p.update(ar=(3, -1), al=(-2, 0))
        im = C.render(C.build_side(p)[0])
    elif view == 'left':
        p.update(ar=(3, -1), al=(-2, 0))
        im = flip(C.render(C.build_side(p)[0]))
    else:
        p.update(al=(-3, -1), ar=(3, -1), bl=(0, spin_phase % 2), br=(0, (spin_phase + 1) % 2))
        im = C.render(C.build_front(p, back=(view == 'up'))[0])
    _cache[k] = im
    return im


def sword_img(vx, vy, L, hand):
    """Espada separada na direcao (vx,vy) da tela. Retorna (img, origem)."""
    a = math.degrees(math.atan2(vx, vy))
    ox, oy = int(hand[0]) - 35, int(hand[1]) - 35
    g = Grid(70, 70)
    cells, tip = C.sword_rows((hand[0] - ox, hand[1] - oy), a, L)
    C.stamp_cells(g, cells)
    return g.render(C.PAL, C.SEL), (ox, oy), (tip[0] + ox, tip[1] + oy)



def hand_gear(center, rx, rz, L, sword=True, mitt_only_off=False):
    """Camada do braco da espada: braco ate a mao, espada SAINDO DA MAO (cabo dentro do punho) e punho por cima do cabo.
    Retorna (img_espada, org, tip) e (img_braco_livre, org). rx,rz = direcao no chao do lado do heroi (projetada na tela)."""
    ox, oy = int(center[0]) - 40, int(center[1]) - 35
    c = (center[0] - ox, center[1] - oy)
    hs = (c[0] + rx * 9.0, c[1] + rz * 4.0)           # mao da espada
    ho = (c[0] - rx * 8.0, c[1] - rz * 3.5)           # mao livre (lado oposto)

    def arm_cells(p0, p1):
        cells = {}
        for (x, y) in C.line_pts(round(p0[0]), round(p0[1]), round(p1[0]), round(p1[1])):
            cells[(x, y)] = 't'; cells[(x, y + 1)] = 'T' if (x, y + 1) not in cells else cells[(x, y + 1)]
        return cells

    def mitt_cells(p):
        cx_, cy_ = round(p[0]), round(p[1])
        out = {}
        for dy, row in enumerate(['sss', 'sss', 'sSS']):
            for dx_, ch in enumerate(row): out[(cx_ - 1 + dx_, cy_ - 1 + dy)] = ch
        return out

    # braco livre + punho livre
    go = Grid(80, 70)
    for (x, y), ch in {**arm_cells((c[0] - rx * 3.5, c[1] - rz * 1.2), ho), **mitt_cells(ho)}.items(): go.put(x, y, ch)
    autoline(go)
    off_img = go.render(C.PAL, C.SEL)
    # braco da espada + espada + punho por cima do cabo
    gs = Grid(80, 70)
    for (x, y), ch in {**arm_cells((c[0] + rx * 3.5, c[1] + rz * 1.2), hs), **mitt_cells(hs)}.items(): gs.put(x, y, ch)
    autoline(gs)
    a = math.degrees(math.atan2(rx * R, rz * R * .5))
    cells, tip = C.sword_rows(hs, a, L)
    C.stamp_cells(gs, cells)
    for (x, y), ch in mitt_cells(hs).items(): gs.put(x, y, ch)          # a mao fecha por cima do cabo
    return gs.render(C.PAL, C.SEL), (ox, oy), (tip[0] + ox, tip[1] + oy), off_img


def flash(img):
    o = img.copy(); px = o.load()
    for y in range(o.height):
        for x in range(o.width):
            if px[x, y][3]: px[x, y] = (255, 255, 255, 255)
    return o


def slime_img(name, pal=M.SLIME):
    g, p = M.slime_frame(name, pal); return g.render(p)


REACT = [('squash', 0, True), ('squash', 0, False), ('stretch', 3, False), ('air', 7, False), ('air', 10, False), ('air', 7, False),
         ('squash', 0, False), ('idle', 0, False), ('idle', 0, False), ('idle', 0, False), ('idle', 0, False), ('idle', 0, False)]


def timeline():
    seq = []
    for f in range(2): seq.append(dict(kind='wind', f=f))
    for f in range(12): seq.append(dict(kind='spin', f=f))
    for f in range(2): seq.append(dict(kind='end', f=f))
    for f in range(14): seq.append(dict(kind='idle', f=f))
    return seq


def render():
    bg, wm = T.build_static(); objs = T.objects()
    CX, CY = 200, 150
    seq = timeline()
    slimes = [dict(b=math.radians(25), pal=M.SLIME, last=-99), dict(b=math.radians(150), pal=M.SLIME_B, last=-99), dict(b=math.radians(265), pal=M.SLIME_O, last=-99)]
    for s in slimes: s['hit'] = None
    cache = {}; out = []; trail_pts = []
    for i, fr in enumerate(seq):
        im = bg.copy()
        ph = (i // 4) % 6
        if ph not in cache: cache[ph] = T.water_layer(wm, ph)
        im.paste(cache[ph].convert('RGB'), (0, 0), cache[ph])
        for o in objs:
            if 'sh' in o: T.shadow(im, *o['sh'])
        kind, f = fr['kind'], fr['f']
        if kind == 'spin':
            theta_deg = (f + 1) * 60.0            # 2 voltas em 12 quadros
        elif kind == 'wind':
            theta_deg = 0
        else:
            theta_deg = 0
        th = math.radians(theta_deg)
        # direcao da espada no chao (lado direito do heroi) -> tela
        rx, rz = -math.cos(th), math.sin(th)
        spinning = kind == 'spin'
        vsel = int(round((theta_deg % 360) / 90.0)) % 4
        view = ['down', 'right', 'up', 'left'][vsel]
        hop = 1 if (spinning and f % 2 == 0) else 0
        spr = C.anim('down', 'idle')[f % 6][0] if kind == 'idle' else body(view, f, crouch=(kind == 'wind' or kind == 'end'), hop=hop)
        wob = (1 if f % 2 else -1) if spinning else 0
        X, Y = CX + wob, CY
        # slimes: reacao ao golpe
        for s in slimes:
            if spinning:
                psi = math.atan2(rx, rz)
                d = abs((psi - s['b'] + math.pi) % (2 * math.pi) - math.pi)
                if d < math.radians(32) and i - s['last'] > 7:
                    s['hit'] = 0; s['last'] = i
            elif s['hit'] is None: pass
        dyn = []
        T.shadow(im, X, Y + 1, 9, 3, 90)
        for s in slimes:
            sx = CX + math.sin(s['b']) * 30; sy = CY + math.cos(s['b']) * 30 * .55
            if s['hit'] is not None and s['hit'] < len(REACT):
                name, up, fl = REACT[s['hit']]
                back = min(s['hit'], 6) * 2.4
                sx += math.sin(s['b']) * back; sy += math.cos(s['b']) * back * .55
                simg = slime_img(name, s['pal'])
                if fl: simg = flash(simg)
                s['pos'] = (sx, sy)
                T.shadow(im, sx, sy, 9 - up * .4, 3, 70)
                dyn.append(dict(img=simg, x=sx - 9, y=sy - 13 - up, foot=sy))
                if s['hit'] >= 1:
                    n = T.number('27'); im.paste(n.convert('RGB'), (int(sx) + 8, int(sy - 24 - s['hit'] * 1.2)), n)
                s['hit'] += 1
                if s['hit'] >= len(REACT): s['hit'] = None
            else:
                s['pos'] = (sx, sy)
                T.shadow(im, sx, sy, 9, 3, 70)
                dyn.append(dict(img=slime_img('idle', s['pal']), x=sx - 9, y=sy - 13, foot=sy))
        dyn.append(dict(img=spr, x=X - CW // 2, y=Y - C.BASE, foot=Y))
        # --- espada (peca separada) SEMPRE NA MAO: braco -> mao -> cabo
        center = (X, Y - BODY_Y)
        if kind == 'spin':
            vx, vy = rx * R, rz * R * .5
            L = max(7.0, math.hypot(vx, vy))
            g_img, g_org, g_tip, off_img = hand_gear(center, rx, rz, L)
            front_sword = rz > -0.05
        elif kind in ('wind', 'end'):
            g_img, g_org, g_tip, off_img = hand_gear(center, -1.0, 0.15, 12.0)
            front_sword = True
        else:
            g_img = None
        sw_img = g_img; sw_org = g_org if g_img is not None else (0, 0)
        trail_front = Image.new('RGBA', (W, H), (0, 0, 0, 0)); trail_back = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        tf, tb = ImageDraw.Draw(trail_front), ImageDraw.Draw(trail_back)
        if spinning:
            N = 14
            pts = []
            for k in range(N):
                a = th - math.radians(14 * k)
                pts.append((center[0] - math.cos(a) * R, center[1] + math.sin(a) * R * .5, math.sin(a)))
            for k in range(N - 1):
                p0, p1 = pts[k], pts[k + 1]
                t_ = k / (N - 1)
                col = (255, 255, 255, 255) if t_ < .25 else (170, 225, 255, 230) if t_ < .55 else (110, 170, 240, 170)
                dr = tf if (p0[2] + p1[2]) / 2 > -0.05 else tb
                dr.line([p0[:2], p1[:2]], fill=col, width=3 if t_ < .3 else 2)
            # anel de vento no chao e poeira
            for k in range(3):
                rr = 16 + k * 7 + (f % 3) * 2
                tb.ellipse([X - rr, Y - rr * .45 - 2, X + rr, Y + rr * .45 - 2], outline=(220, 245, 220, 120 - k * 30))
            for k in range(9):
                a = th * 1.3 + k * 0.7
                lx = X + math.cos(a) * (24 + (k % 3) * 4); ly = Y - 6 - (k * 3 + f * 2) % 22 + math.sin(a) * 8
                col = (250, 230, 120, 255) if k % 2 else (120, 200, 90, 255)
                (tf if math.sin(a) > 0 else tb).rectangle([lx, ly, lx + 1, ly + 1], fill=col)
        im = im.convert('RGBA')
        im = Image.alpha_composite(im, trail_back)
        if sw_img is not None and not front_sword:
            im.alpha_composite(sw_img, (sw_org[0], sw_org[1]))
        if sw_img is not None and front_sword:
            im.alpha_composite(off_img, (sw_org[0], sw_org[1]))   # braco livre atras do corpo
        for o in sorted(list(objs) + dyn, key=lambda o: o['foot']):
            e = o['img'].convert('RGBA')
            im.alpha_composite(e, (int(o['x']), int(o['y']))) if 0 <= o['x'] < W - e.width and 0 <= o['y'] < H - e.height else im.paste(e.convert('RGB'), (int(o['x']), int(o['y'])), e)
        if sw_img is not None and front_sword:
            im.alpha_composite(sw_img, (sw_org[0], sw_org[1]))
        if sw_img is not None and not front_sword:
            im.alpha_composite(off_img, (sw_org[0], sw_org[1]))   # braco livre na frente
        im = Image.alpha_composite(im, trail_front)
        out.append(im.convert('RGB'))
    return out


def save(frames, name, scale=2):
    big = [f.convert('RGB').resize((W * scale, H * scale), Image.NEAREST) for f in frames]
    n = len(big); pick = [big[i * n // 6] for i in range(6)]
    col = Image.new('RGB', (pick[0].width * 3, pick[0].height * 2))
    for i, p in enumerate(pick): col.paste(p, ((i % 3) * p.width, (i // 3) * p.height))
    pal = col.quantize(colors=220, method=Image.MEDIANCUT, dither=Image.NONE)
    q = [im.quantize(palette=pal, dither=Image.NONE) for im in big]
    q[0].save(os.path.join(OUT, name), save_all=True, append_images=q[1:], duration=70, loop=0, disposal=1)


if __name__ == '__main__':
    fr = render()
    save(fr, 'chibi_ciclone.gif')
    print('ok', len(fr))
