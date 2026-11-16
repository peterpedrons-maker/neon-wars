#!/usr/bin/env python3
"""FAUNA: animais pixel art como UMA SO MASSA (regra do dono: nada de circulos encaixados que se leem como pecas separadas).
Todas as partes (tronco, cabeca, pescoco, pernas, cauda, orelhas) sao desenhadas numa MESMA mascara; luz e sombra sao calculadas
sobre a mascara inteira (luz de cima-esquerda, tons em blocos, sem dither); o contorno e unico e seletivo (escuro da propria cor).
Detalhes (olho, narinas, presas) entram depois. API: anim(kind, k, view, dense) -> [(img, None, False)] (mesmo formato do beast.py)."""
import math
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter
import chibi as C

W, H, BASE = C.W, C.H, C.BASE


def hx(s): s = s.lstrip('#'); return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


def darker(c, k): return tuple(max(0, int(v * k)) for v in c)


class Cv:
    def __init__(s):
        s.reg = np.full((H, W), -1, int); s.names = []; s.det = []; s.far = np.zeros((H, W), bool); s.ord = np.zeros((H, W), int); s.n = 0; s.part = np.full((H, W), -1, int); s.cur = None; s.pn = []

    def rid(s, n):
        if n not in s.names: s.names.append(n)
        return s.names.index(n)

    def pid(s, r):
        if s.cur is None: return r
        nm = s.cur + s.names[r] if s.cur.endswith(':') else s.cur
        if nm not in s.pn: s.pn.append(nm)
        return 1000 + s.pn.index(nm)

    def ell(s, cx, cy, rx, ry, reg='body', far=False):
        r = s.rid(reg); ys, xs = np.mgrid[0:H, 0:W]
        m = ((xs + .5 - cx) / rx) ** 2 + ((ys + .5 - cy) / ry) ** 2 <= 1
        s.reg[m] = r; s.n += 1; s.ord[m] = s.n; s.part[m] = s.pid(r)
        if far: s.far[m] = True

    def cap(s, x0, y0, x1, y1, r0, r1, reg='body', far=False):
        r = s.rid(reg); ys, xs = np.mgrid[0:H, 0:W]
        px, py = xs + .5 - x0, ys + .5 - y0; dx, dy = x1 - x0, y1 - y0; L2 = dx * dx + dy * dy or 1
        t = np.clip((px * dx + py * dy) / L2, 0, 1); rr = r0 + (r1 - r0) * t
        m = (px - t * dx) ** 2 + (py - t * dy) ** 2 <= rr ** 2
        s.reg[m] = r; s.n += 1; s.ord[m] = s.n; s.part[m] = s.pid(r)
        if far: s.far[m] = True

    def dot(s, x, y, col): s.det.append((int(round(x)), int(round(y)), col))

    def render(s, ramps, flat=None):
        flat = flat or {}
        M = s.reg >= 0
        bl = gaussian_filter(M.astype(float), 1.7)
        gy, gx = np.gradient(bl)
        mag = np.hypot(gx, gy)
        yy = np.where(M.any(1))[0]; y0, y1 = (yy.min(), yy.max()) if len(yy) else (0, 1)
        ys = np.arange(H)[:, None] * np.ones((1, W))
        base = .22 * (1 - 2 * (ys - y0) / max(1, y1 - y0))
        v = (.6 * gx + .8 * gy) / (mag + 1e-6) * np.clip(mag * 5, 0, 1) + base
        tone = np.where(v > .3, 2, np.where(v < -.22, 0, 1))
        contact = np.zeros((H, W), bool)
        if getattr(s, 'contact', True):
            for dx, dy in ((1, 0), (0, 1), (-1, 0), (0, -1)):
                nr = np.roll(np.roll(s.part, -dy, 0), -dx, 1); no = np.roll(np.roll(s.ord, -dy, 0), -dx, 1)
                contact |= (s.part >= 0) & (nr >= 0) & (nr != s.part) & (no > s.ord) & ~s.far
        img = Image.new('RGBA', (W, H), (0, 0, 0, 0)); px = img.load()
        for y in range(H):
            for x in range(W):
                r = s.reg[y, x]
                if r < 0: continue
                n = s.names[r]
                if n in flat: px[x, y] = flat[n] + (255,); continue
                t = int(tone[y, x]) - (1 if s.far[y, x] else 0)
                if contact[y, x]: t = 0
                px[x, y] = ramps[n][max(0, t)] + (255,)
        # contorno unico, seletivo (escuro da cor do vizinho)
        for y in range(H):
            for x in range(W):
                if M[y, x]: continue
                best = None
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    xx, yy2 = x + dx, y + dy
                    if 0 <= xx < W and 0 <= yy2 < H and M[yy2, xx]:
                        n = s.names[s.reg[yy2, xx]]; c = flat[n] if n in flat else ramps[n][0]
                        best = c if best is None else min(best, c, key=sum)
                if best is not None: px[x, y] = darker(best, .42) + (255,)
        for x, y, c in s.det:
            if 0 <= x < W and 0 <= y < H: px[x, y] = c + (255,)
        return img


def R(d, m, l): return (hx(d), hx(m), hx(l))


PAL = {
    'javali': dict(body=R('#4a2a18', '#7a4a2c', '#a8744a'), belly=R('#6a4a34', '#9a7250', '#c8a070'), mane=R('#1e1008', '#34200f', '#4e3016'),
                   snout=R('#a8606a', '#d08a90', '#eab0b0'), hoof=R('#2a1c14', '#4a3424', '#6a4e38'), far=R('#34200f', '#4e3016', '#6a4222')),
    'rato': dict(body=R('#5a5468', '#8a8298', '#b8b0c8'), belly=R('#9a92a8', '#c8c0d4', '#e6e0ee'), ear=R('#b8607a', '#e090a8', '#f6c0cc'),
                 tail=R('#b8707e', '#dc9aa6', '#f2c0c8'), foot=R('#b8707e', '#dc9aa6', '#f2c0c8'), nose=R('#b8506a', '#e0708a', '#f6a0b4')),
    'lobo': dict(body=R('#4a5266', '#7a8294', '#aab2c4'), belly=R('#8a92a4', '#b8c0d0', '#dce2ec'), ear=R('#2a3040', '#4a5266', '#6a7286'),
                 nose=R('#14141c', '#2a2a34', '#44444e'), paw=R('#3a4256', '#5a6276', '#7a8296')),
}
FLAT = {'tusk': hx('#f4efde'), 'claw': hx('#e8e2d0'), 'fang': hx('#f6f2e8')}


def leg(c, x, hipy, foot_y, sw, lift, r0, r1, reg, far, foot='hoof'):
    fy = foot_y - lift
    c.cap(x, hipy, x + sw, fy - 1.5, r0, r1, reg, far)
    c.cap(x + sw, fy - 1.6, x + sw + .8, fy, r1 + .1, r1 + .3, foot, far)


# ------------------------------------------------------------------ JAVALI SELVAGEM
def javali(view, ph=0.0, bob=0, lunge=0, mouth=0, squint=False, tail=0.0, head_dy=0, pose=False, fd=0, rd=0, fsw=0, rsw=0, flift=0, rlift=0, legs_top=False, **kw):
    m = (fd + rd) / 2; head_dy = head_dy + fd
    c = Cv(); cx = W // 2; gy = BASE
    if view == 'right':
        bx, by = cx - 3 + lunge * .4, gy - 12 + bob
        for i, (lx, ph0, far) in enumerate(((-7, 0, True), (6.5, math.pi, True), (-6, math.pi, False), (7, 0, False))):
            lift = max(0, math.sin(ph + ph0)) * 2.6; sw = math.cos(ph + ph0) * 2.4; hyl = by + 3.5
            if pose:
                fr_ = lx > 0; sw = (fsw if fr_ else rsw) * (.8 if far else 1); lift = (flift if fr_ else rlift) * (.8 if far else 1); hyl = by + 3.5 + (fd if fr_ else rd)
            leg(c, bx + lx, hyl, gy, sw, lift, 1.9 * (1.3 if pose else 1), 1.35 * (1.3 if pose else 1), 'body', far)
        c.ell(bx - 6.5, by + 1.2 + rd, 5.2, 4.6)                         # garupa mais baixa e estreita
        c.ell(bx - .5, by - .2 + m, 8.8, 5.9)                           # tronco
        c.ell(bx + 5, by - 2.4 + fd, 6.2, 7.0)                           # cernelha ALTA (silhueta de javali: ombro alto, traseiro baixo)
        c.ell(bx + .5, by + 3.3 + m, 6.4, 2.6, 'belly')
        c.cap(bx + 8, by - 1.5 + fd, bx + 14.5 + lunge * .4, by + 2.2 + head_dy, 5.6, 4.0)           # pescoco grosso descendo para a cabeca
        c.cap(bx + 14, by + 3 + head_dy, bx + 20.5 + lunge * .5, by + 5 + head_dy, 3.0, 2.3, 'snout')   # focinho longo e baixo
        c.ell(bx + 21 + lunge * .5, by + 5.2 + head_dy, 1.6, 2.0, 'snout')                        # disco do focinho
        c.cap(bx + 11.5, by - 3 + head_dy, bx + 10.2, by - 7.4 + head_dy, 2.1, 1.0, 'mane')         # orelha em pe
        c.cap(bx - 11, by - 2 + rd, bx - 14.5, by - 4 + rd + math.sin(tail) * 1.4, 1.0, .5, 'mane')           # rabo fino
        for k in range(9):                                                                           # crina eriçada (crista contínua)
            x = bx - 9 + k * 2.1; top = by + m * (.4 + .6 * k / 8) - 5.6 - (1.8 if 3 <= k <= 6 else 0) - (1.2 if k in (4, 5) else 0)
            c.cap(x, top + 1, x + .5, top - 2.2, 1.1, .5, 'mane')
        c.cap(bx + 16.8 + lunge * .5, by + 6.8 + head_dy, bx + 19.2 + lunge * .5, by + 3.4 + head_dy, .9, .6, 'tusk')  # presa curva
        ex, ey = bx + 13.2 + lunge * .4, by - .6 + head_dy
        c.dot(ex, ey, hx('#ff8a30') if not squint else hx('#14100c')); c.dot(ex + 1, ey, hx('#14100c')) if not squint else None
        c.dot(bx + 21.5 + lunge * .5, by + 4.6 + head_dy, hx('#14100c'))
        if mouth:
            for q in range(5): c.dot(bx + 16 + q + lunge * .5, by + 7 + head_dy, hx('#14100c'))
        if pose and legs_top:
            for i, (lx, ph0, far) in enumerate(((-7, 0, True), (6.5, math.pi, True), (-6, math.pi, False), (7, 0, False))):
                lift = max(0, math.sin(ph + ph0)) * 2.6; sw = math.cos(ph + ph0) * 2.4; hyl = by + 3.5
                if pose:
                    fr_ = lx > 0; sw = (fsw if fr_ else rsw) * (.8 if far else 1); lift = (flift if fr_ else rlift) * (.8 if far else 1); hyl = by + 3.5 + (fd if fr_ else rd)
                leg(c, bx + lx, hyl, gy, sw, lift, 1.9 * (1.3 if pose else 1), 1.35 * (1.3 if pose else 1), 'body', far)
    else:
        back = view == 'up'; bx = cx; by = gy - 12 + bob
        for sx, ph0 in ((-5.5, 0), (5.5, math.pi)):
            lift = max(0, math.sin(ph + ph0)) * 2.6; swv = 0
            if pose: lift = flift; swv = (1 if sx > 0 else -1) * fsw
            leg(c, bx + sx, by + 3.5, gy, swv, lift, 2.1, 1.6, 'body', False)
        c.ell(bx, by + 1, 9.2, 6.8)
        c.ell(bx, by + 3.4, 5.6, 2.8, 'belly') if not back else None
        for k in range(-4, 5): c.cap(bx + k * 2.1, by - 5, bx + k * 2.1 + .3, by - 8.8 + (1.2 if abs(k) > 2 else 0), 1.0, .5, 'mane')
        hy = by - 1 + head_dy + (lunge * .3 if not back else 0)
        c.ell(bx, hy, 7.2, 6.2)
        for sg in (-1, 1): c.cap(bx + sg * 5.4, hy - 4.6, bx + sg * 6.2, hy - 8.4, 2.0, 1.0, 'mane')
        if back:
            c.cap(bx, by + 6, bx + math.sin(tail) * 1.5, by + 9.5, .9, .5, 'mane')
        else:
            c.ell(bx, hy + 3.4, 4.2, 3.1, 'snout')
            for sg in (-1, 1):
                c.cap(bx + sg * 4.2, hy + 5, bx + sg * 5.8, hy + 1.2, .9, .6, 'tusk')
                c.dot(bx + sg * 3.6, hy - 1.5, hx('#ff8a30') if not squint else hx('#14100c')); c.dot(bx + sg * 2.6, hy - 1.5, hx('#14100c')) if not squint else None
                c.dot(bx + sg * 1.1, hy + 3.2, hx('#14100c'))
            if mouth:
                for q in range(-2, 3): c.dot(bx + q, hy + 6.4, hx('#14100c'))
    return c.render(PAL['javali'], FLAT)


# ------------------------------------------------------------------ RATO GIGANTE
def rato(view, ph=0.0, bob=0, lunge=0, mouth=0, squint=False, tail=0.0, head_dy=0, ear=0, **kw):
    c = Cv(); cx = W // 2; gy = BASE
    if view == 'right':
        bx, by = cx - 2 + lunge * .4, gy - 7 + bob
        for lx, ph0, far in ((-4, 0, True), (4, math.pi, True), (-3.5, math.pi, False), (4.5, 0, False)):
            lift = max(0, math.sin(ph + ph0)) * 1.8; sw = math.cos(ph + ph0) * 1.6
            leg(c, bx + lx, by + 2, gy, sw, lift, 1.5, 1.2, 'body', far, 'foot')
        c.ell(bx - 1, by, 7.2, 4.6)                                   # corpo (arredondado atras)
        c.ell(bx - 3, by + .8, 6, 4.6)
        c.ell(bx, by + 2.5, 5.4, 2.4, 'belly')
        c.cap(bx + 5, by - .5, bx + 10.5 + lunge * .4, by + 1 + head_dy, 3.9, 2.6)               # corpo afunila no focinho
        c.cap(bx + 10, by + 1 + head_dy, bx + 13.5 + lunge * .5, by + 2 + head_dy, 1.7, 1.3, 'nose')
        c.ell(bx + 5.4, by - 4 + head_dy + ear, 2.8, 3.1, 'ear')
        for i in range(15):                                           # cauda longa, fina e continua
            t = i / 14; x = bx - 7 - i * .95; y = by + 1 + math.sin(i * .5 + tail) * 2.2 * t + t * 2
            c.ell(x, y, .85, .85, 'tail')
        ex, ey = bx + 8.6 + lunge * .4, by - .8 + head_dy
        c.dot(ex, ey, hx('#14101c') if not squint else hx('#14101c')); c.dot(ex, ey - 1, hx('#ffffff')) if not squint else None
        c.dot(bx + 14 + lunge * .5, by + 1.5 + head_dy, hx('#14101c'))
        for q in range(3): c.dot(bx + 12 + q + lunge * .4, by + 3 + head_dy + (1 if q == 2 else 0), hx('#14101c'))   # bigodes
        if mouth: c.dot(bx + 12, by + 4 + head_dy, hx('#f8f4ec')); c.dot(bx + 13, by + 4 + head_dy, hx('#f8f4ec'))
    else:
        back = view == 'up'; bx = cx; by = gy - 7 + bob
        for sx, ph0 in ((-3.8, 0), (3.8, math.pi)):
            lift = max(0, math.sin(ph + ph0)) * 1.8
            leg(c, bx + sx, by + 2, gy, 0, lift, 1.6, 1.3, 'body', False, 'foot')
        c.ell(bx, by + .5, 6.2, 5.2)
        hy = by - 1.5 + head_dy + (lunge * .3 if not back else 0)
        c.ell(bx, hy, 5.2, 4.6)
        for sg in (-1, 1): c.ell(bx + sg * 4.6, hy - 4 + ear, 2.9, 3.1, 'ear')
        if back:
            for i in range(10): c.ell(bx + math.sin(i * .6 + tail) * 2.2, by + 4 + i * .9, .85, .85, 'tail')
        else:
            c.ell(bx, hy + 2.6, 2.4, 2.1, 'nose')
            for sg in (-1, 1):
                c.dot(bx + sg * 2.6, hy - 1, hx('#14101c')); c.dot(bx + sg * 2.6, hy - 2, hx('#ffffff')) if not squint else None
                for q in range(3): c.dot(bx + sg * (4.8 + q), hy + 2 + (q - 1), hx('#14101c'))
            c.dot(bx, hy + 4.6, hx('#f8f4ec')); c.dot(bx - 1, hy + 4.6, hx('#f8f4ec')); c.dot(bx + 1, hy + 4.6, hx('#f8f4ec')) if mouth else None
    return c.render(PAL['rato'], FLAT)


# ------------------------------------------------------------------ LOBO
def lobo(view, ph=0.0, bob=0, lunge=0, mouth=0, squint=False, tail=0.0, head_dy=0, pose=False, fd=0, rd=0, fsw=0, rsw=0, flift=0, rlift=0, legs_top=False, **kw):
    m = (fd + rd) / 2; head_dy = head_dy + fd
    c = Cv(); cx = W // 2; gy = BASE
    if view == 'right':
        bx, by = cx - 3 + lunge * .4, gy - 13 + bob
        for lx, ph0, far in ((-8, 0, True), (7, math.pi, True), (-7, math.pi, False), (8, 0, False)):
            lift = max(0, math.sin(ph + ph0)) * 2.6; sw = math.cos(ph + ph0) * 2.6; hyl = by + 2
            if pose:
                fr_ = lx > 0; sw = (fsw if fr_ else rsw) * (.8 if far else 1); lift = (flift if fr_ else rlift) * (.8 if far else 1); hyl = by + 2 + (fd if fr_ else rd)
            leg(c, bx + lx, hyl, gy, sw, lift, 1.9 * (1.3 if pose else 1), 1.3 * (1.3 if pose else 1), 'body', far, 'paw')
        c.ell(bx - 6, by + .5 + rd, 5.6, 5)
        c.ell(bx + 1, by - .3 + m, 9.2, 5.2)
        c.ell(bx + 6, by - 1 + fd, 5.4, 5.6)
        c.ell(bx + 1, by + 3 + m, 7, 2.2, 'belly')
        c.cap(bx + 9, by - 2 + fd, bx + 14 + lunge * .4, by - 3 + head_dy, 4.6, 3.8)
        c.cap(bx + 14, by - 2.5 + head_dy, bx + 20 + lunge * .5, by - .5 + head_dy, 3.0, 2.0)
        c.cap(bx + 12.5, by - 6 + head_dy, bx + 12, by - 10 + head_dy, 1.7, .8, 'ear')
        c.cap(bx - 10, by - .5 + rd, bx - 18, by + 3 + rd + math.sin(tail) * 2, 2.0, 1.2)
        c.dot(bx + 15, by - 3.5 + head_dy, hx('#ffd030') if not squint else hx('#14101c'))
        c.dot(bx + 21, by - 1 + head_dy, hx('#14101c'))
        if mouth:
            for q in range(5): c.dot(bx + 16 + q + lunge * .5, by + 1.2 + head_dy, hx('#14101c'))
            c.dot(bx + 17, by + 2 + head_dy, hx('#f8f4e8')); c.dot(bx + 19, by + 2 + head_dy, hx('#f8f4e8'))
        if pose and legs_top:
            for lx, ph0, far in ((-8, 0, True), (7, math.pi, True), (-7, math.pi, False), (8, 0, False)):
                lift = max(0, math.sin(ph + ph0)) * 2.6; sw = math.cos(ph + ph0) * 2.6; hyl = by + 2
                if pose:
                    fr_ = lx > 0; sw = (fsw if fr_ else rsw) * (.8 if far else 1); lift = (flift if fr_ else rlift) * (.8 if far else 1); hyl = by + 2 + (fd if fr_ else rd)
                leg(c, bx + lx, hyl, gy, sw, lift, 1.9 * (1.3 if pose else 1), 1.3 * (1.3 if pose else 1), 'body', far, 'paw')
    else:
        back = view == 'up'; bx = cx; by = gy - 13 + bob
        for sx, ph0 in ((-4.5, 0), (4.5, math.pi)):
            lift = max(0, math.sin(ph + ph0)) * 2.6; swv = 0
            if pose: lift = flift; swv = (1 if sx > 0 else -1) * fsw
            leg(c, bx + sx, by + 3, gy, swv, lift, 2.0, 1.5, 'body', False, 'paw')
        c.ell(bx, by + 1, 7.6, 6.6)
        hy = by - 3 + head_dy + (lunge * .3 if not back else 0)
        c.ell(bx, hy, 6, 5.4)
        for sg in (-1, 1): c.cap(bx + sg * 4.2, hy - 4, bx + sg * 4.8, hy - 8.6, 1.9, .9, 'ear')
        if back: c.cap(bx, by + 6, bx + math.sin(tail) * 2, by + 11, 2, 1.2)
        else:
            c.ell(bx, hy + 3.2, 2.9, 2.5, 'belly')
            c.dot(bx, hy + 3, hx('#14141c')); c.dot(bx, hy + 4, hx('#14141c'))
            for sg in (-1, 1): c.dot(bx + sg * 3, hy - 1.5, hx('#ffd030') if not squint else hx('#14101c'))
            if mouth: [c.dot(bx + q, hy + 6, hx('#14101c')) for q in range(-2, 3)]
    return c.render(PAL['lobo'], FLAT)


DRAW = {'javali': javali, 'rato': rato, 'lobo': lobo}


PAL.update({
    'urso': dict(body=R('#3a2418', '#6a4028', '#94603c'), belly=R('#5a3a28', '#84583a', '#b08058'), snout=R('#8a6a48', '#b8946a', '#d8b88a'),
                 ear=R('#2a1810', '#4a2c1c', '#6a4228'), paw=R('#2a1810', '#4a2c1c', '#6a4228')),
    'cobra': dict(body=R('#2a5a2a', '#4a8a3a', '#7ac04a'), belly=R('#9a9a4a', '#cacd70', '#eef0a0'), mark=R('#1a3a1a', '#2a5a2a', '#3a7a30'), tongue=R('#a8203a', '#d8405a', '#f07a8a')),
    'aranha': dict(body=R('#241a30', '#3e2c54', '#5e467a'), mark=R('#5a1020', '#9a2038', '#d04a5a'), leg=R('#1a1220', '#30223e', '#4a3860')),
    'barata': dict(body=R('#3a2410', '#6a4420', '#a0703a'), shell=R('#4a2c14', '#8a5a2a', '#c8924c'), leg=R('#2a1a0c', '#4a3018', '#6a4a2a')),
    'sapo': dict(body=R('#2e5a28', '#4e8a3a', '#7cc050'), belly=R('#8a9a50', '#b8c878', '#dce8a0'), mark=R('#1e3e1c', '#2e5a28', '#3e7a34'), eye=R('#a89018', '#e8c830', '#f8e870')),
})


def urso(view, ph=0.0, bob=0, lunge=0, mouth=0, squint=False, tail=0.0, head_dy=0, **kw):
    c = Cv(); cx = W // 2; gy = BASE
    if view == 'right':
        bx, by = cx - 3 + lunge * .4, gy - 14 + bob
        for lx, ph0, far in ((-8, 0, True), (7, math.pi, True), (-7, math.pi, False), (8, 0, False)):
            lift = max(0, math.sin(ph + ph0)) * 2.0; sw = math.cos(ph + ph0) * 2.0
            leg(c, bx + lx, by + 3, gy, sw, lift, 3.4, 2.8, 'body', far, 'paw')
        c.ell(bx - 5, by + 1, 7.4, 7)
        c.ell(bx + 1, by - 1, 10, 7.4)
        c.ell(bx + 6.5, by - 2.6, 6.5, 7.4)
        c.ell(bx, by + 4.4, 7, 2.8, 'belly')
        c.cap(bx + 9, by - 1, bx + 15 + lunge * .4, by + 1.2 + head_dy, 5.6, 4.6)
        c.cap(bx + 15, by + 2.5 + head_dy, bx + 20 + lunge * .5, by + 3.4 + head_dy, 3.0, 2.4, 'snout')
        c.ell(bx + 12, by - 4.8 + head_dy, 2.3, 2.3, 'ear')
        c.ell(bx - 11, by - .5, 2, 2.2)
        c.dot(bx + 15.5, by - .6 + head_dy, hx('#14100c') if not squint else hx('#14100c')); c.dot(bx + 15.5, by - 1.6 + head_dy, hx('#fff0c0')) if not squint else None
        c.dot(bx + 21, by + 2.6 + head_dy, hx('#14100c')); c.dot(bx + 20, by + 2.6 + head_dy, hx('#14100c'))
        if mouth:
            for q in range(5): c.dot(bx + 16 + q + lunge * .5, by + 5.4 + head_dy, hx('#14100c'))
            c.dot(bx + 17, by + 6.4 + head_dy, hx('#f6f2e8')); c.dot(bx + 19, by + 6.4 + head_dy, hx('#f6f2e8'))
    else:
        back = view == 'up'; bx = cx; by = gy - 14 + bob
        for sx, ph0 in ((-6.5, 0), (6.5, math.pi)):
            lift = max(0, math.sin(ph + ph0)) * 2.0
            leg(c, bx + sx, by + 4, gy, 0, lift, 3.4, 2.9, 'body', False, 'paw')
        c.ell(bx, by + 1, 11, 8.2)
        hy = by - 2 + head_dy + (lunge * .3 if not back else 0)
        c.ell(bx, hy, 7.2, 6.4)
        for sg in (-1, 1): c.ell(bx + sg * 5.6, hy - 5, 2.5, 2.5, 'ear')
        if back: c.ell(bx, by + 7, 2.2, 2)
        else:
            c.ell(bx, hy + 2.8, 3.7, 3, 'snout')
            for sg in (-1, 1): c.dot(bx + sg * 3.4, hy - 1.5, hx('#14100c'))
            c.dot(bx, hy + 2, hx('#14100c')); c.dot(bx - 1, hy + 2, hx('#14100c'))
            if mouth: [c.dot(bx + q, hy + 5.6, hx('#14100c')) for q in range(-2, 3)]
    return c.render(PAL['urso'], FLAT)


def cobra(view, ph=0.0, bob=0, lunge=0, mouth=0, squint=False, tail=0.0, head_dy=0, **kw):
    c = Cv(); cx = W // 2; gy = BASE
    N = 40; pts = []
    for i in range(N):
        t = i / (N - 1)                                   # 0 = ponta da cauda, 1 = cabeca
        x = cx - 17 + t * 25 + lunge * .6 * t
        wave = math.sin(t * 11 - ph * 2) * (4.2 * (1 - t) ** .8 + .4)
        lift = (max(0, t - .66) / .34) ** 1.5 * (12 + bob - head_dy * .6)
        y = gy - 3 - wave - lift
        r = .55 + 2.5 * min(1, t * 1.25)
        if t > .93: r = 2.2
        pts.append((x, y, r))
    for (x, y, r) in pts: c.ell(x, y, r, r * .92)
    hx_, hy_, _ = pts[-1]; px_, py_, _ = pts[-4]
    c.ell(hx_ + 2.4, hy_ - .2, 4.4, 2.7)                  # cabeca triangular achatada
    c.ell(hx_ - 1.5, hy_ + 3.2, 3.4, 3.4, 'belly')       # papo claro
    c.dot(hx_ + 3, hy_ - 1.3, hx('#ffd030') if not squint else hx('#101010'))
    if mouth or int(ph * 3) % 4 == 0:
        c.cap(hx_ + 6.5, hy_ + .8, hx_ + 10, hy_ + 1.6, .5, .3, 'tongue'); c.dot(hx_ + 10.6, hy_ + .6, hx('#d8405a')); c.dot(hx_ + 10.6, hy_ + 2.4, hx('#d8405a'))
    if mouth:
        c.dot(hx_ + 5, hy_ + 2.4, hx('#f6f2e8')); c.dot(hx_ + 6.5, hy_ + 2.4, hx('#f6f2e8'))
    for i in range(5, N - 6, 4): c.dot(pts[i][0], pts[i][1] - 1, PAL['cobra']['mark'][1]); c.dot(pts[i][0] + 1, pts[i][1] - 1, PAL['cobra']['mark'][1])
    return c.render(PAL['cobra'], FLAT)


def aranha(view, ph=0.0, bob=0, lunge=0, mouth=0, squint=False, tail=0.0, head_dy=0, **kw):
    c = Cv(); cx = W // 2; gy = BASE
    bx, by = cx + lunge * .3, gy - 9 + bob
    for i in range(4):
        for sg in (-1, 1):
            a = (i - 1.5) * .55 + (0 if i < 2 else .15)
            lift = max(0, math.sin(ph * 2 + i * 1.6 + (0 if sg > 0 else math.pi))) * 2.2
            kx, ky = bx + sg * (9 + i * .8), by - 8 - lift - (2 if i in (1, 2) else 0) + i * .8
            fx_, fy_ = bx + sg * (17 + (1 - abs(i - 1.5)) * 3), gy - lift + (i - 1.5) * -.8
            c.cap(bx + sg * 2.6, by + (i - 1.5) * 1.6, kx, ky, 1.2, .9, 'leg', sg < 0)
            c.cap(kx, ky, fx_, fy_, .9, .5, 'leg', sg < 0)
    c.ell(bx, by + 2.4, 5.8, 5.2)                          # abdome
    c.ell(bx, by - 3.8 + head_dy * .3, 3.7, 3.2)           # cefalotorax
    c.ell(bx, by + 3, 1.6, 2.4, 'mark')
    for sg in (-1, 1):
        c.dot(bx + sg * 1.4, by - 5, hx('#ff3a4a') if not squint else hx('#201020')); c.dot(bx + sg * 2.6, by - 4, hx('#ff3a4a') if not squint else hx('#201020'))
        c.cap(bx + sg * 1.4, by - 6, bx + sg * 2.4, by - 8.4 + (2 if mouth else 0), .7, .5, 'leg')
    return c.render(PAL['aranha'], FLAT)


def barata(view, ph=0.0, bob=0, lunge=0, mouth=0, squint=False, tail=0.0, head_dy=0, **kw):
    c = Cv(); cx = W // 2; gy = BASE
    bx, by = cx + lunge * .3, gy - 6 + bob
    for i in range(3):
        for sg in (-1, 1):
            lift = max(0, math.sin(ph * 2 + i * 2.1 + (0 if sg > 0 else math.pi))) * 1.8
            c.cap(bx + sg * 3, by + (i - 1) * 3.2, bx + sg * 8.5, by + (i - 1) * 3.6 + 2 - lift * .4, 1, .8, 'leg', sg < 0)
            c.cap(bx + sg * 8.5, by + (i - 1) * 3.6 + 2 - lift * .4, bx + sg * 10.5, gy - lift, .8, .5, 'leg', sg < 0)
    c.ell(bx, by + 2.2, 5.2, 7.4, 'shell')                  # elitros (viram uma peca so)
    c.ell(bx, by - 5.2, 4.2, 3.4)                           # cabeca/pronoto
    c.cap(bx, by - 3, bx, by + 8, .4, .4, 'body')
    for sg in (-1, 1):
        c.cap(bx + sg * 1.6, by - 8, bx + sg * (5 + math.sin(tail + sg) * 1.2), by - 14 + (3 if mouth else 0), .6, .4, 'leg')
        c.dot(bx + sg * 1.6, by - 6, hx('#14100c') if not squint else hx('#14100c'))
    return c.render(PAL['barata'], FLAT)


def sapo(view, ph=0.0, bob=0, lunge=0, mouth=0, squint=False, tail=0.0, head_dy=0, **kw):
    c = Cv(); cx = W // 2; gy = BASE
    hop = max(0, math.sin(ph)) * 4
    sq = 1.0 - hop * .03
    if view == 'right':
        bx, by = cx - 2 + lunge * .4, gy - 8 - hop + bob
        c.cap(bx - 6, by + 3, bx - 9 - hop * .3, gy - 1 - hop * .6, 3.6, 1.6, 'body', True)
        c.cap(bx - 9 - hop * .3, gy - 1.5 - hop * .6, bx - 4, gy - hop * .5, 1.6, 1.2, 'body', True)
        c.ell(bx - 1, by, 8.4, 6.2 * sq)
        c.ell(bx, by + 3, 6, 3, 'belly')
        c.cap(bx + 4, by + 3, bx + 8, gy - hop * .3, 1.9, 1.5)
        c.cap(bx - 5, by + 2, bx - 1, gy - hop * .2, 3.2, 1.6)
        c.ell(bx + 7 + lunge * .4, by - 1 + head_dy, 5.4, 4.4)
        c.ell(bx + 6, by - 5 + head_dy, 2.5, 2.5, 'eye')
        c.dot(bx + 7, by - 5.5 + head_dy, hx('#14100c') if not squint else hx('#14100c'))
        if mouth:
            for q in range(6): c.dot(bx + 8 + q + lunge * .4, by + 1.5 + head_dy, hx('#14100c'))
            c.cap(bx + 12, by + 1.6 + head_dy, bx + 18 + lunge * .6, by + 2 + head_dy, .8, .6, 'mark') if False else None
        c.dot(bx + 12 + lunge * .4, by - 1.5 + head_dy, hx('#14100c'))
    else:
        back = view == 'up'; bx = cx; by = gy - 8 - hop + bob
        for sg in (-1, 1): c.ell(bx + sg * 7, gy - 2 - hop * .4, 3.4, 2.4, 'body', True)
        c.ell(bx, by + .5, 8.8, 6.4 * sq)
        c.ell(bx, by + 3.4, 5, 2.6, 'belly') if not back else None
        hy = by - 3 + head_dy + (lunge * .3 if not back else 0)
        c.ell(bx, hy, 6.4, 4.4)
        for sg in (-1, 1):
            c.ell(bx + sg * 4.2, hy - 4, 2.5, 2.5, 'eye')
            if not back: c.dot(bx + sg * 4.2, hy - 4.4, hx('#14100c'))
        if not back and mouth:
            for q in range(-3, 4): c.dot(bx + q, hy + 3, hx('#14100c'))
        if not back: c.dot(bx - 1, hy + 1, hx('#14100c')); c.dot(bx + 1, hy + 1, hx('#14100c'))
    return c.render(PAL['sapo'], FLAT)


DRAW.update({'urso': urso, 'cobra': cobra, 'aranha': aranha, 'barata': barata, 'sapo': sapo})


def anim(kind, k, view, dense=2):
    n = {'idle': 6, 'walk': 8, 'attack': 10, 'hurt': 4, 'death': 6}[k] * dense
    d = DRAW[kind]; out = []
    for i in range(n):
        u = i / max(1, n - 1); ph = 2 * math.pi * i / n
        if k == 'idle': im = d(view, 0, bob=1 if math.sin(ph) > .5 else 0, tail=ph)
        elif k == 'walk': im = d(view, ph, bob=-1 if abs(math.sin(ph * 2)) > .8 else 0, tail=ph * 2)
        elif k == 'attack':
            wind = -3 if u < .3 else 0
            lunge = int(round(wind * math.sin(u / .3 * math.pi / 2))) if u < .3 else int(round(9 * math.sin((u - .3) / .7 * math.pi)))
            im = d(view, 0, lunge=lunge, mouth=1 if .4 < u < .75 else 0, head_dy=-2 if u > .4 and u < .8 else 0, tail=u * 10)
        elif k == 'hurt': im = d(view, 0, lunge=-int(round(3 * math.sin(u * math.pi))), squint=True, mouth=1 if u < .6 else 0, head_dy=-1)
        else:
            im = d(view, 0, lunge=-3, squint=True, mouth=1)
            if u > .35:
                a = np.array(im); a = a[::-1]
                bb = Image.fromarray(a).getbbox(); im2 = Image.new('RGBA', (W, H), (0, 0, 0, 0))
                if bb: im2.alpha_composite(Image.fromarray(a), (0, BASE - bb[3] + 1))
                im = im2
        out.append((im, None, False))
    return out


if __name__ == '__main__':
    import sys
    kinds = sys.argv[1:] or list(DRAW)
    S = Image.new('RGBA', (W * 8, H * 3 * len(kinds)), (52, 70, 52, 255))
    for ki, kd in enumerate(kinds):
        for vi, v in enumerate(('right', 'down', 'up')):
            seq = anim(kd, 'walk', v, 1)
            for i, (im, _, _) in enumerate(seq): S.alpha_composite(im, (i * W, (ki * 3 + vi) * H))
    S.resize((S.width * 2, S.height * 2), Image.NEAREST).save('/tmp/fauna_test.png'); print(S.size)
