#!/usr/bin/env python3
"""FAUNA 2: criaturas bipedes/aladas/vegetais de UMA SO MASSA (mesmo motor do fauna.py): gnoll, homem-rato, harpia, tronco vivo, cogumelo andante, ogrinho."""
import math
from fauna import Cv, R, hx, FLAT, PAL, W, H, BASE, anim as _anim, DRAW
FLAT.update({'metal': hx('#c8d0e0'), 'wood': hx('#7a5230'), 'bone': hx('#e8e2d0')})
PAL.update({
    'gnoll': dict(body=R('#6a4a22', '#a07a3a', '#d0a860'), belly=R('#a08a60', '#d0bc8a', '#ece0b8'), mane=R('#2e1e0c', '#4e3414', '#6e4c1e'), spot=R('#3e2a10', '#5a3c16', '#7a5424'),
                  cloth=R('#5a2a20', '#8a4430', '#b86a48'), snout=R('#3e2a10', '#5a3c16', '#7a5424')),
    'ratkin': dict(body=R('#4e4658', '#7a728a', '#a8a0b8'), belly=R('#8a8298', '#b4acc4', '#d8d2e4'), ear=R('#a8546a', '#d4849a', '#f2b8c4'), tail=R('#a8607a', '#d48a9e', '#f0b4c0'),
                   cloth=R('#2a3a2a', '#44603a', '#668a54'), nose=R('#a8486a', '#d8708a', '#f4a0b4'), foot=R('#a8607a', '#d48a9e', '#f0b4c0')),
    'harpia': dict(body=R('#5a3a6a', '#8a5aa0', '#b88ad0'), belly=R('#c8a8c0', '#e8d0e0', '#f8ecf4'), wing=R('#3a2448', '#5e3a74', '#8a5aa8'), beak=R('#a87a18', '#d8a830', '#f4d060'),
                  talon=R('#8a7a30', '#b8a448', '#dcd070'), hair=R('#3a2a1a', '#6a4a2a', '#9a7040')),
    'tronco': dict(body=R('#3a2412', '#6a4422', '#94683a'), bark=R('#2a180c', '#4a2e16', '#6a4422'), leaf=R('#2a5a22', '#4a8a36', '#7ac04c'), glow=R('#c88010', '#f0b020', '#fff070'), root=R('#2a180c', '#4a2e16', '#6a4422')),
    'cogumelo': dict(cap=R('#8a2a30', '#c84448', '#e87a74'), stem=R('#b8a888', '#e0d4b8', '#f8f0dc'), spot=R('#d8d0c0', '#f4ecd8', '#ffffff'), foot=R('#8a7a5a', '#b4a47c', '#d4c89c')),
    'ogrinho': dict(body=R('#4a6a2a', '#78a040', '#a8cc66'), belly=R('#88a860', '#b4cc84', '#d8e8aa'), cloth=R('#5a3a20', '#8a5a34', '#b88450'), horn=R('#a89a70', '#d4c898', '#f0e8c4')),
})


def limb(c, x0, y0, x1, y1, r0, r1, reg='body', far=False): c.cap(x0, y0, x1, y1, r0, r1, reg, far)


def weapon(c, x, y, ang, L, kind, side=1):
    dx, dy = math.cos(ang), math.sin(ang)
    c.cap(x, y, x + dx * L, y + dy * L, .8, .8, 'wood')
    if kind == 'spear': c.cap(x + dx * L, y + dy * L, x + dx * (L + 4), y + dy * (L + 4), 1.2, .3, 'metal')
    if kind == 'club': c.cap(x + dx * (L - 3), y + dy * (L - 3), x + dx * (L + 1), y + dy * (L + 1), 2.2, 2.6, 'wood')


# ------------------------------------------------------------------ GNOLL (homem-hiena)
def gnoll(view, ph=0.0, bob=0, lunge=0, mouth=0, squint=False, tail=0.0, head_dy=0, **kw):
    c = Cv(); cx = W // 2; gy = BASE
    if view == 'right':
        bx, by = cx - 2 + lunge * .4, gy - 17 + bob
        for lx, ph0, far in ((-2, 0, True), (2, math.pi, False)):
            lift = max(0, math.sin(ph + ph0)) * 2.6; sw = math.cos(ph + ph0) * 3
            limb(c, bx + lx + 1, by + 6, bx + lx + sw * .5, gy - 3 - lift, 2.6, 1.8, 'body', far); limb(c, bx + lx + sw * .5, gy - 3 - lift, bx + lx + sw, gy - lift, 1.7, 1.3, 'body', far)
        c.ell(bx - 2, by + 1, 6.2, 8.6)                              # tronco curvado
        c.ell(bx - 3, by - 3, 6.6, 6, 'mane')                        # crina da nuca/ombros
        c.ell(bx + .5, by + 4, 4.6, 4.2, 'cloth')                    # tanga
        c.cap(bx + 1, by - 5, bx + 7 + lunge * .3, by - 6 + head_dy, 4.2, 3.6)           # pescoco -> cabeca
        c.cap(bx + 7, by - 6 + head_dy, bx + 13.5 + lunge * .4, by - 4.6 + head_dy, 3.0, 2.2, 'snout')   # focinho de hiena
        c.cap(bx + 4, by - 9.5 + head_dy, bx + 4.5, by - 13 + head_dy, 2.0, .9, 'mane')   # orelha redonda
        c.cap(bx - 6, by + 5, bx - 11, by + 8 + math.sin(tail) * 1.5, 1.5, .9, 'mane')       # rabo
        for k in range(3): c.dot(bx - 4 + k * 3, by + k % 2 * 3, hx('#3e2a10'))               # manchas
        c.dot(bx + 8.5, by - 7.2 + head_dy, hx('#ffd030') if not squint else hx('#14100c')); c.dot(bx + 14.5 + lunge * .4, by - 5.4 + head_dy, hx('#14100c'))
        sw_ = (lunge * .3 + math.sin(ph) * 1.5)
        limb(c, bx + 2, by - 1, bx + 7 + sw_, by + 3, 1.9, 1.5); weapon(c, bx + 7 + sw_, by + 3, -1.1 + (lunge * .05), 15, 'spear')
        if mouth:
            for q in range(5): c.dot(bx + 9 + q + lunge * .4, by - 3.2 + head_dy, hx('#14100c'))
            c.dot(bx + 10, by - 2.2 + head_dy, hx('#f6f2e8')); c.dot(bx + 12, by - 2.2 + head_dy, hx('#f6f2e8'))
    else:
        back = view == 'up'; bx = cx; by = gy - 17 + bob
        for sx, ph0 in ((-3.4, 0), (3.4, math.pi)):
            lift = max(0, math.sin(ph + ph0)) * 2.6
            limb(c, bx + sx, by + 7, bx + sx, gy - lift, 2.6, 1.7)
        c.ell(bx, by + 1, 7.6, 8.8); c.ell(bx, by - 3, 8.2, 5.4, 'mane'); c.ell(bx, by + 5, 5.8, 4.6, 'cloth')
        for sg in (-1, 1): limb(c, bx + sg * 7, by - 2, bx + sg * 9.5, by + 5, 2.1, 1.7)
        hy = by - 8 + head_dy
        c.ell(bx, hy, 5.8, 5.2)
        for sg in (-1, 1): c.cap(bx + sg * 4.4, hy - 3.6, bx + sg * 5, hy - 7.6, 2.1, 1.0, 'mane')
        if back: c.cap(bx, by + 9, bx + math.sin(tail) * 2, by + 13, 1.5, .9, 'mane')
        else:
            c.ell(bx, hy + 2.6, 3.0, 2.6, 'snout')
            for sg in (-1, 1): c.dot(bx + sg * 2.8, hy - 1.4, hx('#ffd030') if not squint else hx('#14100c'))
            c.dot(bx, hy + 2, hx('#14100c'))
            if mouth: [c.dot(bx + q, hy + 4.8, hx('#14100c')) for q in range(-2, 3)]
        weapon(c, bx + 9.5, by + 5, -1.35, 17, 'spear')
    return c.render(PAL['gnoll'], FLAT)


# ------------------------------------------------------------------ HOMEM-RATO
def ratkin(view, ph=0.0, bob=0, lunge=0, mouth=0, squint=False, tail=0.0, head_dy=0, **kw):
    c = Cv(); cx = W // 2; gy = BASE
    if view == 'right':
        bx, by = cx - 2 + lunge * .4, gy - 14 + bob
        for lx, ph0, far in ((-1.5, 0, True), (1.5, math.pi, False)):
            lift = max(0, math.sin(ph + ph0)) * 2.2; sw = math.cos(ph + ph0) * 2.6
            limb(c, bx + lx, by + 5, bx + lx + sw * .6, gy - 2.5 - lift, 2.0, 1.4, 'body', far); limb(c, bx + lx + sw * .6, gy - 2.6 - lift, bx + lx + sw + 1.5, gy - lift, 1.3, 1.1, 'foot', far)
        c.ell(bx - 1, by, 5.2, 7)
        c.ell(bx, by + 3, 5.4, 3.6, 'cloth')
        c.cap(bx + 1, by - 4, bx + 5 + lunge * .3, by - 5.5 + head_dy, 3.4, 3.2)
        c.cap(bx + 5, by - 5.6 + head_dy, bx + 11.5 + lunge * .4, by - 3.8 + head_dy, 2.4, 1.2)       # focinho de rato
        c.ell(bx + 11.8 + lunge * .4, by - 3.8 + head_dy, 1.1, 1.0, 'nose')
        c.ell(bx + 2.6, by - 9.4 + head_dy, 2.7, 3.0, 'ear')
        for i in range(14):
            t = i / 13; c.ell(bx - 5 - i * .9, by + 5 + math.sin(i * .5 + tail) * 2 * t + t * 3, .8, .8, 'tail')
        limb(c, bx + 1, by - 1, bx + 6 + lunge * .3, by + 3, 1.5, 1.2)
        weapon(c, bx + 6 + lunge * .3, by + 3, -1.25, 15, 'spear')
        c.dot(bx + 7, by - 6.4 + head_dy, hx('#14101c') if not squint else hx('#14101c')); c.dot(bx + 7, by - 7.4 + head_dy, hx('#ffffff')) if not squint else None
        for q in range(3): c.dot(bx + 9 + q, by - 2 + head_dy + (q - 1), hx('#14101c'))
        if mouth: c.dot(bx + 9, by - 2.6 + head_dy, hx('#f8f4ec')); c.dot(bx + 10, by - 2.6 + head_dy, hx('#f8f4ec'))
    else:
        back = view == 'up'; bx = cx; by = gy - 14 + bob
        for sx, ph0 in ((-2.8, 0), (2.8, math.pi)):
            lift = max(0, math.sin(ph + ph0)) * 2.2
            limb(c, bx + sx, by + 6, bx + sx, gy - lift, 2.0, 1.4); c.ell(bx + sx, gy - lift - .4, 2.0, 1.1, 'foot')
        c.ell(bx, by, 6.2, 7); c.ell(bx, by + 3, 6, 3.6, 'cloth')
        for sg in (-1, 1): limb(c, bx + sg * 5.8, by - 2, bx + sg * 7.6, by + 4, 1.6, 1.3)
        hy = by - 8 + head_dy
        c.ell(bx, hy, 4.6, 4.2)
        for sg in (-1, 1): c.ell(bx + sg * 4.4, hy - 3.4, 2.7, 2.9, 'ear')
        if back:
            for i in range(9): c.ell(bx + math.sin(i * .6 + tail) * 2, by + 8 + i * .9, .8, .8, 'tail')
        else:
            c.ell(bx, hy + 2.4, 2.1, 2.0, 'nose')
            for sg in (-1, 1):
                c.dot(bx + sg * 2.2, hy - 1, hx('#14101c')); c.dot(bx + sg * 2.2, hy - 2, hx('#ffffff')) if not squint else None
                for q in range(3): c.dot(bx + sg * (4.4 + q), hy + 2 + (q - 1), hx('#14101c'))
            c.dot(bx, hy + 4.2, hx('#f8f4ec')); c.dot(bx - 1, hy + 4.2, hx('#f8f4ec')) if mouth else None
        weapon(c, bx + 7.6, by + 4, -1.4, 15, 'spear')
    return c.render(PAL['ratkin'], FLAT)


# ------------------------------------------------------------------ HARPIA
def harpia(view, ph=0.0, bob=0, lunge=0, mouth=0, squint=False, tail=0.0, head_dy=0, **kw):
    c = Cv(); cx = W // 2; gy = BASE
    fl = math.sin(ph * 2) * 1.0; by = gy - 22 + bob + math.sin(ph) * 1.5; bx = cx + lunge * .4
    for sg in (-1, 1):                                                  # asas (um unico bloco com o corpo)
        c.cap(bx + sg * 3, by - 3, bx + sg * 15, by - 9 - fl * 6, 3.0, 1.2, 'wing', sg < 0)
        c.cap(bx + sg * 15, by - 9 - fl * 6, bx + sg * 19, by - 1 - fl * 8, 1.4, .6, 'wing', sg < 0)
        c.cap(bx + sg * 4, by, bx + sg * 15, by - 2 - fl * 6, 2.4, 1.0, 'wing', sg < 0)
    c.ell(bx, by + 2, 5.2, 7.2)
    c.ell(bx, by + 3.4, 3.4, 4.6, 'belly')
    c.cap(bx, by + 8, bx - 1.5, by + 15, 2.4, 1.2)                      # cauda/pernas de ave
    for sg in (-1, 1):
        c.cap(bx + sg * 2.4, by + 8, bx + sg * 3, gy - 3 - (1 if sg > 0 else 0) * fl, 1.0, .8, 'talon')
        c.cap(bx + sg * 3, gy - 3, bx + sg * 4.4, gy, 1.2, .5, 'talon')
    hy = by - 8 + head_dy + lunge * .2
    c.ell(bx, hy, 4.6, 4.4)
    c.cap(bx - 4, hy - 2, bx - 5.5, hy + 5, 1.6, .9, 'hair'); c.cap(bx + 4, hy - 2, bx + 5.5, hy + 5, 1.6, .9, 'hair')
    c.ell(bx, hy - 3.4, 4.6, 2.2, 'hair')
    c.cap(bx, hy + 1.5, bx + (3 if view == 'right' else 0), hy + 3.4, 1.5, .5, 'beak')
    for sg in (-1, 1): c.dot(bx + sg * 1.9, hy - .6, hx('#ffe04a') if not squint else hx('#14101c'))
    if mouth: c.dot(bx, hy + 4.2, hx('#14100c'))
    return c.render(PAL['harpia'], FLAT)


# ------------------------------------------------------------------ TRONCO VIVO (treant jovem)
def tronco(view, ph=0.0, bob=0, lunge=0, mouth=0, squint=False, tail=0.0, head_dy=0, **kw):
    c = Cv(); cx = W // 2; gy = BASE
    bx = cx + lunge * .3; by = gy - 14 + bob
    for sx, ph0 in ((-5.5, 0), (5.5, math.pi)):
        lift = max(0, math.sin(ph + ph0)) * 2.4
        c.cap(bx + sx * .6, by + 7, bx + sx, gy - lift, 3.2, 2.2, 'root'); c.ell(bx + sx, gy - lift - .6, 3.2, 1.5, 'root')
    c.ell(bx, by, 8, 11)                                                # tronco grosso
    c.ell(bx, by - 11, 6.4, 2.6, 'bark')
    for sg in (-1, 1):
        c.cap(bx + sg * 6, by - 6, bx + sg * 13, by - 13 - sg * math.sin(ph) * 1.5 - (lunge * .2), 2.2, 1.0, 'bark')       # galhos/braços
        c.cap(bx + sg * 13, by - 13, bx + sg * 15, by - 17, 1.0, .6, 'bark')
        c.ell(bx + sg * 14, by - 17, 3, 2.6, 'leaf'); c.ell(bx + sg * 9, by - 18, 3.4, 2.8, 'leaf')
    c.ell(bx, by - 20, 7, 4.2, 'leaf'); c.ell(bx - 4, by - 17, 3.6, 3, 'leaf')
    for k in range(4): c.dot(bx - 5 + k * 3, by - 5 + (k % 2) * 6, hx('#2a180c')); c.dot(bx - 4 + k * 3, by - 4 + (k % 2) * 6, hx('#2a180c'))
    ex = 3 if view == 'right' else 0
    for sg in (-1, 1) if view != 'right' else (1,):
        c.ell(bx + sg * 3.2 + ex * .5, by - 6, 1.7, 1.7, 'glow') if not squint else c.dot(bx + sg * 3.2, by - 6, hx('#14100c'))
    c.ell(bx + ex * .5, by - 1, 2.6, 2.0 + (1.5 if mouth else 0), 'glow') if mouth else c.ell(bx + ex * .5, by - 1, 2.6, .9, 'bark')
    return c.render(PAL['tronco'], FLAT)


# ------------------------------------------------------------------ COGUMELO ANDANTE
def cogumelo(view, ph=0.0, bob=0, lunge=0, mouth=0, squint=False, tail=0.0, head_dy=0, **kw):
    c = Cv(); cx = W // 2; gy = BASE
    hop = max(0, math.sin(ph)) * 2.4
    bx = cx + lunge * .3; by = gy - 8 - hop + bob
    for sx, ph0 in ((-3, 0), (3, math.pi)):
        lift = max(0, math.sin(ph + ph0)) * 2.0
        c.cap(bx + sx, by + 4, bx + sx, gy - lift, 1.8, 1.4, 'stem'); c.ell(bx + sx, gy - lift - .4, 2.3, 1.1, 'foot')
    c.ell(bx, by + 1, 5.2, 6, 'stem')
    c.ell(bx, by - 5.5, 10, 6.4 - (1 if mouth else 0), 'cap')
    c.ell(bx, by - 1.6, 8, 1.6, 'stem')
    for (dx, dy, r) in ((-4.5, -7.6, 1.5), (3.5, -9, 1.7), (6.2, -5, 1.2), (-1, -10.5, 1.1), (0, -5, 1.3)): c.ell(bx + dx, by + dy, r, r, 'spot')
    ex = 1 if view == 'right' else 0
    for sg in (-1, 1) if view != 'right' else (1,):
        c.dot(bx + sg * 2 + ex * 1.5, by - .8, hx('#14100c')); c.dot(bx + sg * 2 + ex * 1.5, by - 1.8, hx('#ffffff')) if not squint else None
    if mouth: c.dot(bx + ex, by + 2.2, hx('#14100c')); c.dot(bx + ex + 1, by + 2.2, hx('#14100c'))
    return c.render(PAL['cogumelo'], FLAT)


# ------------------------------------------------------------------ OGRINHO (filhote de ogro — mesma massa unica)
def ogrinho(view, ph=0.0, bob=0, lunge=0, mouth=0, squint=False, tail=0.0, head_dy=0, **kw):
    c = Cv(); cx = W // 2; gy = BASE
    if view == 'right':
        bx, by = cx - 2 + lunge * .4, gy - 13 + bob
        for lx, ph0, far in ((-2, 0, True), (2, math.pi, False)):
            lift = max(0, math.sin(ph + ph0)) * 2.2; sw = math.cos(ph + ph0) * 2.4
            limb(c, bx + lx, by + 5, bx + lx + sw, gy - lift, 3.0, 2.4, 'body', far)
        c.ell(bx - 1, by, 7.4, 7.8); c.ell(bx + .5, by + 4, 6.2, 3.4, 'cloth'); c.ell(bx, by + 1.2, 4.4, 4.4, 'belly')
        c.ell(bx + 3.6, by - 9 + head_dy, 5.8, 5.2)                                                       # cabeca grande e quadrada
        c.cap(bx + 7, by - 8.4 + head_dy, bx + 10, by - 7 + head_dy, 2.4, 2.0)
        c.cap(bx + 1, by - 13 + head_dy, bx - .6, by - 17 + head_dy, 1.6, .5, 'horn'); c.cap(bx + 6.4, by - 13.2 + head_dy, bx + 7.4, by - 16.6 + head_dy, 1.4, .5, 'horn')
        c.cap(bx + 8, by - 5.6 + head_dy, bx + 8.4, by - 8.4 + head_dy, .8, .6, 'horn')                   # presa
        limb(c, bx + 2, by - 1, bx + 8 + lunge * .3, by + 4, 2.6, 2.2); weapon(c, bx + 8 + lunge * .3, by + 4, -1.0, 11, 'club')
        c.dot(bx + 7.2, by - 10 + head_dy, hx('#ffd030') if not squint else hx('#14100c')); c.dot(bx + 10.6, by - 7.4 + head_dy, hx('#14100c'))
        if mouth:
            for q in range(4): c.dot(bx + 7 + q, by - 5 + head_dy, hx('#14100c'))
    else:
        back = view == 'up'; bx = cx; by = gy - 13 + bob
        for sx, ph0 in ((-3.4, 0), (3.4, math.pi)):
            lift = max(0, math.sin(ph + ph0)) * 2.2
            limb(c, bx + sx, by + 6, bx + sx, gy - lift, 3.0, 2.4)
        c.ell(bx, by, 8.6, 7.8); c.ell(bx, by + 4, 7.4, 3.4, 'cloth')
        for sg in (-1, 1): limb(c, bx + sg * 8, by - 2, bx + sg * 10, by + 4, 2.7, 2.3)
        hy = by - 9 + head_dy; c.ell(bx, hy, 6.8, 5.6)
        for sg in (-1, 1): c.cap(bx + sg * 4.4, hy - 4.4, bx + sg * 5.6, hy - 8.8, 1.5, .5, 'horn')
        if not back:
            for sg in (-1, 1): c.dot(bx + sg * 2.8, hy - 1.2, hx('#ffd030') if not squint else hx('#14100c')); c.cap(bx + sg * 3.2, hy + 3.6, bx + sg * 3.6, hy + 1.2, .8, .6, 'horn')
            c.dot(bx, hy + 1.6, hx('#14100c'))
            if mouth: [c.dot(bx + q, hy + 4.2, hx('#14100c')) for q in range(-2, 3)]
        weapon(c, bx + 10, by + 4, -1.3, 12, 'club')
    return c.render(PAL['ogrinho'], FLAT)


DRAW.update({'gnoll': gnoll, 'ratkin': ratkin, 'harpia': harpia, 'tronco': tronco, 'cogumelo': cogumelo, 'ogrinho': ogrinho})

if __name__ == '__main__':
    from PIL import Image
    ks = ['gnoll', 'ratkin', 'harpia', 'tronco', 'cogumelo', 'ogrinho']
    S = Image.new('RGBA', (72 * 5 * 3, 64 * 5 * 4), (52, 70, 52, 255))
    for i, k in enumerate(ks):
        for j, v in enumerate(('right', 'down')):
            S.alpha_composite(DRAW[k](v, .6).resize((72 * 5, 64 * 5), Image.NEAREST), ((i % 3) * 72 * 5, ((i // 3) * 2 + j) * 64 * 5))
    S.save('/tmp/fauna2.png'); print(S.size)
