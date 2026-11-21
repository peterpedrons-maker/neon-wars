#!/usr/bin/env python3
"""FAUNA 3 (Região 2, Terras Áridas): criaturas do deserto de UMA SO MASSA (mesmo motor do fauna.py).
escorpiao (+sal), lagarto (+salamandra), canino (chacal, lobo-da-poeira, cao-de-guerra, cao-infernal), abutre, escaravelho, verme."""
import math
from fauna import Cv, R, hx, FLAT, PAL, W, H, BASE, DRAW
FLAT.update({'stinger': hx('#e8d8a0'), 'ember': hx('#ffb030')})
PAL.update({
    'escorpiao': dict(body=R('#7a4a1c', '#b07a34', '#dcaa58'), shell=R('#5a3410', '#8a5a22', '#b8843a'), pinca=R('#6a3a14', '#9a622a', '#c88a44'), tail=R('#6a3a14', '#a06a2c', '#d09a4c'), sting=R('#3a2a10', '#6a4a1a', '#9a7030')),
    'escorpiao_sal': dict(body=R('#8a98b0', '#c4d0e0', '#eef4fa'), shell=R('#6a7a98', '#a4b4cc', '#d8e4f2'), pinca=R('#7a8aa8', '#b0c0d8', '#e0ecf8'), tail=R('#7a8aa8', '#b4c4dc', '#e4f0fa'), sting=R('#3a5a9a', '#5a8ae0', '#9ac0ff')),
    'lagarto': dict(body=R('#5a5a50', '#8a8a78', '#b8b8a0'), belly=R('#a09a78', '#c8c29a', '#e6e0bc'), spine=R('#3a3a34', '#5a5a50', '#7a7a68'), eye=R('#caa020', '#f0c840', '#fff090'), claw=R('#aaa090', '#d0c8b4', '#ece6d6')),
    'salamandra': dict(body=R('#7a2a10', '#c84a18', '#f08030'), belly=R('#d8a050', '#f0c870', '#fff0a8'), spine=R('#3a1008', '#6a2010', '#9a3418'), eye=R('#fff060', '#ffffa0', '#ffffff'), claw=R('#3a1c10', '#5a2c18', '#7a3c20')),
    'chacal': dict(body=R('#7a5a2c', '#b08a48', '#dcb870'), belly=R('#c8b088', '#e6d4aa', '#f8ecce'), ear=R('#4a3418', '#7a5a2c', '#a8844a'), nose=R('#14141c', '#2a2a34', '#44444e'), paw=R('#5a4220', '#86642e', '#aa8248'), mane=R('#4a3418', '#6a4c20', '#8a6a34'), horn=R('#c8b890', '#e8dcb8', '#fff6dc'), armor=R('#5a5a68', '#8a8a9a', '#bcbccc')),
    'poeira': dict(body=R('#7a6a58', '#a8947a', '#d4c0a0'), belly=R('#c8b8a0', '#e6dac0', '#f8f0dc'), ear=R('#4a3e32', '#6e5e4a', '#948066'), nose=R('#14141c', '#2a2a34', '#44444e'), paw=R('#5a4e40', '#84725c', '#a8967c'), mane=R('#5a4a38', '#8a7458', '#b09a78'), horn=R('#c8b890', '#e8dcb8', '#fff6dc'), armor=R('#5a5a68', '#8a8a9a', '#bcbccc')),
    'guerra': dict(body=R('#4a3a30', '#74604e', '#a08a72'), belly=R('#a08a72', '#c8b49a', '#e8dcc4'), ear=R('#2a2018', '#4a3a2c', '#6a5640'), nose=R('#14141c', '#2a2a34', '#44444e'), paw=R('#3a2c22', '#5a4636', '#7a6450'), mane=R('#2a2018', '#4a3a2c', '#6a5640'), horn=R('#c8b890', '#e8dcb8', '#fff6dc'), armor=R('#5a5a68', '#8a8a9a', '#bcbccc')),
    'infernal': dict(body=R('#1a1216', '#32242a', '#523c44'), belly=R('#5a2418', '#9a3a1c', '#d85a24'), ear=R('#120c10', '#24181c', '#3a2a30'), nose=R('#ff6a20', '#ffa040', '#ffd080'), paw=R('#14100e', '#2a201c', '#46362e'), mane=R('#8a2410', '#e0501c', '#ffa83a'), horn=R('#3a2a2a', '#5a4040', '#7a5a5a'), armor=R('#5a5a68', '#8a8a9a', '#bcbccc')),
    'abutre': dict(body=R('#3a2a24', '#5e463a', '#86685a'), wing=R('#241812', '#3e2c22', '#5e4434'), neck=R('#a86a5a', '#d49080', '#f0baa8'), head=R('#a05a4a', '#cc8070', '#ecaa98'), beak=R('#8a7a30', '#c8b448', '#ece07a'), ruff=R('#c8bca0', '#e6dcc0', '#f8f0dc'), talon=R('#5a4a30', '#8a7448', '#b0986a')),
    'escaravelho': dict(body=R('#143a40', '#1e7a78', '#3ad0b0'), shell=R('#102a50', '#1c58b0', '#5a9cff'), leg=R('#101820', '#24303c', '#44566a'), horn=R('#1a1a22', '#323240', '#505064'), gold=R('#8a6a10', '#d8a820', '#fff070')),
    'verme': dict(body=R('#7a5a38', '#b08a58', '#dcb884'), ring=R('#5a3a20', '#8a5e34', '#b08850'), maw=R('#4a1018', '#8a2030', '#c04050'), tooth=R('#bca880', '#e8dcb8', '#fff8e0')),
})


# ------------------------------------------------------------------ ESCORPIAO (do deserto / de sal)
def _escorpiao(pal):
    def f(view, ph=0.0, bob=0, lunge=0, mouth=0, squint=False, tail=0.0, head_dy=0, **kw):
        c = Cv(); cx = W // 2; gy = BASE
        if view == 'right':
            bx, by = cx - 1 + lunge * .4, gy - 6 + bob
            for i in range(4):
                lift = max(0, math.sin(ph * 2 + i * 1.6)) * 1.6
                for far in (True, False):
                    o = 1.2 if far else 0
                    c.cap(bx - 5 + i * 3.2 + o, by + .5, bx - 7 + i * 3.6 + o, by + 3.4 - lift * .5, 1.0, .7, 'pinca', far)
                    c.cap(bx - 7 + i * 3.6 + o, by + 3.4 - lift * .5, bx - 8 + i * 3.9 + o, gy - lift, .8, .5, 'pinca', far)
            c.ell(bx - 3, by - 1, 8, 4.6)                                   # abdome
            c.ell(bx + 4, by - 1.4, 5, 4.4, 'shell')                        # carapaça
            c.ell(bx - 3, by - .4, 6, 2.2, 'shell')
            # cauda: sobe por trás e arqueia sobre o corpo
            pts = [(bx - 9, by - 1), (bx - 13, by - 5), (bx - 14, by - 10), (bx - 11 + math.sin(tail) * .8, by - 15), (bx - 5 + math.sin(tail) * 1.2, by - 17.5)]
            for (x0, y0), (x1, y1), r in zip(pts, pts[1:], (2.6, 2.4, 2.2, 2.0)): c.cap(x0, y0, x1, y1, r, r * .9, 'tail')
            c.ell(pts[-1][0] + 1.2, pts[-1][1] + 1.6, 2.4, 2.2, 'tail')
            c.cap(pts[-1][0] + 2, pts[-1][1] + 3, pts[-1][0] + 3, pts[-1][1] + 6.4 + (1.5 if mouth else 0), 1.1, .3, 'sting')
            # pinças (garras) à frente
            gx, gy2 = bx + 10 + lunge * .6, by + 1 - (3 if mouth else 0)
            c.cap(bx + 8, by + 1, gx + 2, gy2, 1.5, 1.4, 'pinca'); c.ell(gx + 4.2, gy2 - .4, 3.4, 2.5, 'pinca'); c.cap(gx + 5, gy2 - 1.8, gx + 9, gy2 - 2.4 - (1 if mouth else 0), 1.3, .4, 'pinca'); c.cap(gx + 5, gy2 + 1.2, gx + 9, gy2 + 1.6 + (1 if mouth else 0), 1.1, .4, 'pinca')
            c.dot(bx + 7, by - 3.4, hx('#101010') if squint else hx('#ff3030')); c.dot(bx + 9, by - 3, hx('#101010') if squint else hx('#ff3030'))
        else:
            back = view == 'up'; bx, by = cx + lunge * .2, gy - 8 + bob
            sgn = -1 if not back else 1
            for i in range(4):
                for sg in (-1, 1):
                    lift = max(0, math.sin(ph * 2 + i * 1.7 + (0 if sg > 0 else math.pi))) * 1.6
                    c.cap(bx + sg * 3, by + (i - 1.5) * 2.2, bx + sg * 9.4, by + (i - 1.5) * 2.6 - lift * .3, 1.0, .7, 'pinca', sg < 0)
                    c.cap(bx + sg * 9.4, by + (i - 1.5) * 2.6 - lift * .3, bx + sg * 11, gy - lift, .8, .5, 'pinca', sg < 0)
            c.ell(bx, by + 2.4, 5.6, 6.6)
            c.ell(bx, by - 2.6, 4.6, 4.2, 'shell')
            for k in range(4): c.cap(bx, by + 3 + k * 2.2, bx, by + 4.8 + k * 2.2, 3.6 - k * .5, 3.0 - k * .5, 'shell')
            for sg in (-1, 1):
                c.cap(bx + sg * 3, by - 4 * sgn, bx + sg * 7 + lunge * .1, by - 8 * sgn, 1.5, 1.4, 'pinca')
                c.ell(bx + sg * 7.6, by - 10 * sgn - (2 if mouth else 0) * sgn, 3.2, 2.8, 'pinca'); c.cap(bx + sg * 7.6, by - 12 * sgn, bx + sg * 9, by - 15 * sgn, 1.2, .4, 'pinca')
            if back:
                c.cap(bx, by + 4, bx, by + 12, 2.2, 1.6, 'tail'); c.ell(bx, by + 14, 2.4, 2.2, 'tail'); c.dot(bx, by + 17, hx('#e8d8a0'))
            else:
                c.cap(bx, by - 1, bx + math.sin(tail) * 1.4, by - 14, 2.3, 1.7, 'tail'); c.ell(bx + math.sin(tail) * 1.4, by - 15, 2.3, 2.1, 'tail'); c.dot(bx + math.sin(tail) * 1.4, by - 18 + (3 if mouth else 0), hx('#e8d8a0'))
                for s2 in (-1, 1): c.dot(bx + s2 * 1.6, by - 3, hx('#101010') if squint else hx('#ff3030'))
        return c.render(PAL[pal], FLAT)
    return f


# ------------------------------------------------------------------ LAGARTO (de pedra / salamandra)
def _lagarto(pal, flame=False):
    def f(view, ph=0.0, bob=0, lunge=0, mouth=0, squint=False, tail=0.0, head_dy=0, **kw):
        c = Cv(); cx = W // 2; gy = BASE
        if view == 'right':
            bx, by = cx - 4 + lunge * .4, gy - 7 + bob
            for lx, p0, far in ((-9, 0, True), (6, math.pi, True), (-8, math.pi, False), (7, 0, False)):
                lift = max(0, math.sin(ph + p0)) * 2.0; sw = math.cos(ph + p0) * 2.2
                c.cap(bx + lx, by + 1, bx + lx + sw + (2 if lx > 0 else -2), by + 3.4 - lift * .4, 1.7, 1.2, 'body', far)
                c.cap(bx + lx + sw + (2 if lx > 0 else -2), by + 3.4 - lift * .4, bx + lx + sw + (4.2 if lx > 0 else -.6), gy - lift, 1.2, .9, 'body', far)
                c.cap(bx + lx + sw + 3.6, gy - lift, bx + lx + sw + 6.4, gy - lift, .8, .6, 'claw', far)
            c.ell(bx, by, 10.5, 4.6)
            c.ell(bx + 1, by + 2.2, 8, 2.2, 'belly')
            c.cap(bx - 9, by - .4, bx - 22, by + 1.8 + math.sin(tail) * 2.4, 3.4, .9, 'body')
            c.cap(bx + 8, by - 1.4, bx + 14, by - 3.4 + head_dy, 3.4, 3.2)
            c.ell(bx + 16.6 + lunge * .5, by - 3 + head_dy, 5.2, 3.6)
            for k in range(6): c.cap(bx - 8 + k * 3.4, by - 3.6, bx - 8.6 + k * 3.4, by - 6.4 - (k % 2), 1.3, .4, 'spine')
            if flame:
                for k in range(5): c.dot(bx - 7 + k * 3.6, by - 8 - (k % 2) - math.sin(tail + k) * .8, hx('#ffb030')); c.dot(bx - 7 + k * 3.6, by - 9.6 - (k % 2), hx('#ffe070'))
            c.dot(bx + 17, by - 5 + head_dy, hx('#101010') if squint else hx('#f0c030')); c.dot(bx + 19, by - 4.6 + head_dy, hx('#101010') if squint else hx('#f0c030'))
            if mouth:
                for q in range(5): c.dot(bx + 18 + q + lunge * .5, by - 1.4 + head_dy, hx('#2a1018'))
                c.dot(bx + 20, by - .2 + head_dy, hx('#f8f4e8'))
                if flame: c.cap(bx + 22, by - 1.4 + head_dy, bx + 28, by - 3 + head_dy, 1.6, .5, 'claw') if False else [c.dot(bx + 23 + q, by - 2 + head_dy + (q % 2), hx('#ff9a30')) for q in range(5)]
        else:
            back = view == 'up'; bx = cx; by = gy - 7 + bob
            for sg in (-1, 1):
                for i, yy in enumerate((-4, 4)):
                    lift = max(0, math.sin(ph + i * math.pi + (0 if sg > 0 else math.pi))) * 1.8
                    c.cap(bx + sg * 4, by + yy, bx + sg * 10, by + yy + 1 - lift * .3, 1.6, 1.2, 'body', sg < 0)
                    c.cap(bx + sg * 10, by + yy + 1 - lift * .3, bx + sg * 11.4, gy - lift, 1.2, .9, 'body', sg < 0)
            c.ell(bx, by + 1, 5.8, 8.8)
            c.cap(bx, by + 8, bx + math.sin(tail) * 2, by + 17, 3.2, .8, 'body') if not back else c.cap(bx, by + 8, bx + math.sin(tail) * 2, by + 14, 3.2, 1, 'body')
            hy = by - 8 + head_dy; c.ell(bx, hy, 4.8, 4.2)
            for k in range(5): c.dot(bx + (k % 2) * 2 - 1, by - 4 + k * 2.2, hx('#3a3a34') if not flame else hx('#ffb030'))
            if not back:
                for sg in (-1, 1): c.dot(bx + sg * 2.6, hy - 1.2, hx('#101010') if squint else hx('#f0c030'))
                if mouth: [c.dot(bx + q, hy + 3, hx('#2a1018')) for q in range(-2, 3)]
        return c.render(PAL[pal], FLAT)
    return f


# ------------------------------------------------------------------ CANINOS (chacal, lobo-da-poeira, cao de guerra, cao infernal)
def _canino(pal, size=1.0, lean=1.0, mane=False, horns=False, armor=False, ember=False):
    def f(view, ph=0.0, bob=0, lunge=0, mouth=0, squint=False, tail=0.0, head_dy=0, **kw):
        c = Cv(); cx = W // 2; gy = BASE; s = size
        EYE = hx('#101010') if squint else (hx('#ff7a20') if ember else hx('#ffd030'))
        if view == 'right':
            bx, by = cx - 3 + lunge * .4, gy - 13 * s + bob
            for lx, ph0, far in ((-8, 0, True), (7, math.pi, True), (-7, math.pi, False), (8, 0, False)):
                lift = max(0, math.sin(ph + ph0)) * 2.8; sw = math.cos(ph + ph0) * 2.8
                x0 = bx + lx * s; fy = gy - lift
                c.cap(x0, by + 2, x0 + sw, fy - 1.6, 1.7 * s, 1.1, 'body', far); c.cap(x0 + sw, fy - 1.7, x0 + sw + .8, fy, 1.2, 1.3, 'paw', far)
            c.ell(bx - 6 * s, by + .6, 5.2 * s, 4.6 * s * lean)
            c.ell(bx + 1, by - .6, 9.2 * s, 4.8 * s * lean)
            c.ell(bx + 6 * s, by - 1, 5.2 * s, 5.4 * s * lean)
            c.ell(bx + 1, by + 3 * s * lean, 7 * s, 1.8, 'belly')
            if mane:
                for k in range(6): c.cap(bx + 8 * s - k * 3.2, by - 4 * s, bx + 7 * s - k * 3.2, by - 9.4 * s - (k % 2), 1.6, .5, 'mane')
            if armor:
                c.ell(bx + 1, by - 2.6 * s, 8.4 * s, 2.4, 'armor')
                for k in range(4): c.dot(bx - 5 + k * 3.6, by - 5.2 * s, hx('#d8dcec'))
            c.cap(bx + 9 * s, by - 2 * s, bx + 14 * s, by - 3.4 * s + head_dy, 4.4 * s, 3.6 * s)
            c.cap(bx + 14 * s, by - 2.6 * s + head_dy, bx + 20 * s + lunge * .5, by - .6 + head_dy, 2.8 * s, 1.9 * s)
            c.cap(bx + 12.5 * s, by - 6 * s + head_dy, bx + 11.4 * s, by - 12.6 * s + head_dy, 1.9 * s, .8, 'ear')          # orelha alta
            c.cap(bx + 11 * s, by - 5.6 * s + head_dy, bx + 9 * s, by - 11 * s + head_dy, 1.6 * s, .7, 'ear')
            if horns:
                c.cap(bx + 12 * s, by - 7 * s + head_dy, bx + 8 * s, by - 14 * s + head_dy, 1.7, .4, 'horn'); c.cap(bx + 14 * s, by - 6.6 * s + head_dy, bx + 13 * s, by - 14 * s + head_dy, 1.5, .4, 'horn')
            c.cap(bx - 10 * s, by - .5, bx - 17 * s, by + 4 * s + math.sin(tail) * 2, 2.2 * s, 1.0, 'mane' if ember else 'body')
            c.dot(bx + 14 * s, by - 3.6 * s + head_dy, EYE); c.dot(bx + 17 * s, by - 3.4 * s + head_dy, EYE); c.dot(bx + 21 * s, by - .8 + head_dy, hx('#14101c'))
            if ember:
                for k in range(4): c.dot(bx - 2 + k * 3, by - 1 + (k % 2), hx('#ff7a20'))
            if armor: c.cap(bx + 8.6 * s, by + 1, bx + 10 * s, by + 3.6 * s, 1.8, 1.8, 'armor'); [c.dot(bx + 9 * s + q * 1.1, by + 3.4 * s + 1, hx('#f0f0f8')) for q in range(-1, 2)]
            if mouth:
                for q in range(5): c.dot(bx + 16 * s + q + lunge * .5, by + 1.2 + head_dy, hx('#14101c'))
                c.dot(bx + 17 * s, by + 2 + head_dy, hx('#f8f4e8')); c.dot(bx + 19 * s, by + 2 + head_dy, hx('#f8f4e8'))
        else:
            back = view == 'up'; bx = cx; by = gy - 13 * s + bob
            for sx, ph0 in ((-4.5, 0), (4.5, math.pi)):
                lift = max(0, math.sin(ph + ph0)) * 2.8
                c.cap(bx + sx * s, by + 3, bx + sx * s, gy - lift - 1.4, 1.9 * s, 1.3, 'body'); c.cap(bx + sx * s, gy - lift - 1.5, bx + sx * s, gy - lift, 1.3, 1.5, 'paw')
            c.ell(bx, by + 1, 7.4 * s, 6.4 * s * lean)
            hy = by - 3 * s + head_dy + (lunge * .3 if not back else 0)
            if mane and not back: c.ell(bx, hy + 1, 7 * s, 6 * s, 'mane')
            c.ell(bx, hy, 5.6 * s, 5.2 * s)
            for sg in (-1, 1): c.cap(bx + sg * 4 * s, hy - 3.6, bx + sg * 5.6 * s, hy - 10.8 * s, 2.0 * s, .8, 'ear')
            if horns:
                for sg in (-1, 1): c.cap(bx + sg * 2.4, hy - 5, bx + sg * 5.4, hy - 12.5, 1.6, .4, 'horn')
            if armor: c.ell(bx, by - 1.6 * s, 7.6 * s, 2.6, 'armor')
            if back: c.cap(bx, by + 6, bx + math.sin(tail) * 2, by + 12, 2, 1.2, 'mane' if ember else 'body')
            else:
                c.ell(bx, hy + 3.2 * s, 2.8 * s, 2.4 * s, 'belly'); c.dot(bx, hy + 3, hx('#14141c')); c.dot(bx, hy + 4, hx('#14141c'))
                for sg in (-1, 1): c.dot(bx + sg * 3, hy - 1.5, EYE)
                if mouth: [c.dot(bx + q, hy + 6, hx('#14101c')) for q in range(-2, 3)]
        return c.render(PAL[pal], FLAT)
    return f


# ------------------------------------------------------------------ ABUTRE-CARNICEIRO
def abutre(view, ph=0.0, bob=0, lunge=0, mouth=0, squint=False, tail=0.0, head_dy=0, **kw):
    c = Cv(); cx = W // 2; gy = BASE
    if view == 'right':
        bx, by = cx - 2 + lunge * .4, gy - 15 + bob
        for lx, p0, far in ((-1.5, 0, True), (1.5, math.pi, False)):
            lift = max(0, math.sin(ph + p0)) * 2.2; sw = math.cos(ph + p0) * 2.2
            c.cap(bx + lx, by + 5, bx + lx + sw * .5, gy - 2.4 - lift, 1.5, 1.0, 'talon', far); c.cap(bx + lx + sw * .5, gy - 2.4 - lift, bx + lx + sw + 3, gy - lift, 1.0, .8, 'talon', far)
        c.ell(bx - 2, by + 1, 8.4, 7.4)                                   # tronco curvado
        c.cap(bx - 8, by + 3, bx - 15 + math.sin(tail) * .8, by + 9, 3.2, 1.8, 'wing')   # cauda
        c.ell(bx - 3, by - 1, 7.4, 6, 'wing')                              # asa dobrada
        c.cap(bx + 4, by - 3, bx + 8 + lunge * .3, by - 10 + head_dy, 2.4, 1.9, 'neck')   # pescoço
        c.ell(bx + 5, by - 3.4, 5.6, 3.6, 'ruff')                          # gola de penas
        hxx, hyy = bx + 9 + lunge * .5, by - 12 + head_dy
        c.ell(hxx, hyy, 3.4, 3.2, 'head')
        c.cap(hxx + 2.4, hyy + .4, hxx + 7.4, hyy + 2.4 + (1.8 if mouth else 0), 1.8, .7, 'beak')
        c.dot(hxx + 1, hyy - .8, hx('#101010') if squint else hx('#ffd030'))
    else:
        back = view == 'up'; bx = cx; by = gy - 15 + bob
        for sx in (-3, 3):
            lift = max(0, math.sin(ph + (0 if sx > 0 else math.pi))) * 2.2
            c.cap(bx + sx, by + 6, bx + sx, gy - 2.4 - lift, 1.5, 1.0, 'talon'); c.cap(bx + sx, gy - 2.4 - lift, bx + sx, gy - lift, 1.2, 1.1, 'talon')
        c.ell(bx, by + 1, 7.4, 8.2)
        for sg in (-1, 1): c.ell(bx + sg * 7.4, by + 1, 4.2, 8.4, 'wing')
        if back: c.ell(bx, by - 2, 6, 6, 'wing')
        else:
            c.ell(bx, by - 4, 5.4, 3.6, 'ruff'); c.cap(bx, by - 5, bx, by - 10 + head_dy, 2.2, 1.8, 'neck'); c.ell(bx, by - 13 + head_dy, 3.4, 3.2, 'head')
            c.cap(bx, by - 12 + head_dy, bx + 1, by - 8 + head_dy + (2 if mouth else 0), 1.6, .6, 'beak')
            for sg in (-1, 1): c.dot(bx + sg * 1.8, by - 14 + head_dy, hx('#101010') if squint else hx('#ffd030'))
    return c.render(PAL['abutre'], FLAT)


# ------------------------------------------------------------------ ESCARAVELHO SAGRADO
def escaravelho(view, ph=0.0, bob=0, lunge=0, mouth=0, squint=False, tail=0.0, head_dy=0, **kw):
    c = Cv(); cx = W // 2; gy = BASE
    if view == 'right':
        bx, by = cx - 1 + lunge * .4, gy - 7 + bob
        for i in range(3):
            lift = max(0, math.sin(ph * 2 + i * 2.1)) * 1.8
            for far in (True, False):
                o = 1.4 if far else 0
                c.cap(bx - 4 + i * 4 + o, by + 2, bx - 6 + i * 4.4 + o, by + 4.4 - lift * .4, 1.0, .8, 'leg', far); c.cap(bx - 6 + i * 4.4 + o, by + 4.4 - lift * .4, bx - 7 + i * 4.6 + o, gy - lift, .8, .5, 'leg', far)
        c.ell(bx - 1, by - 1, 10, 6.6, 'shell')                           # élitros (cúpula brilhante)
        c.cap(bx - 8, by - 1.6, bx - 8, by + 1.2, .5, .5, 'leg') if False else None
        c.ell(bx + 8.4, by - .4, 4.4, 3.6)                                 # pronoto
        c.ell(bx + 12.6 + lunge * .5, by + .6 + head_dy, 3.2, 2.6)       # cabeça
        c.cap(bx + 13, by - 1.6 + head_dy, bx + 14.4 + lunge * .5, by - 6 + head_dy - (1 if mouth else 0), 1.4, .4, 'horn')   # chifre
        c.ell(bx - 1, by - 4.6, 3.6, 1.4, 'gold'); c.ell(bx + 3, by - 3, 1.8, 1.2, 'gold')                                  # filetes dourados
        c.dot(bx + 13, by - .2 + head_dy, hx('#101010') if squint else hx('#ff4030'))
    else:
        back = view == 'up'; bx = cx; by = gy - 8 + bob
        for i in range(3):
            for sg in (-1, 1):
                lift = max(0, math.sin(ph * 2 + i * 2.1 + (0 if sg > 0 else math.pi))) * 1.8
                c.cap(bx + sg * 4, by + (i - 1) * 3.4, bx + sg * 10, by + (i - 1) * 3.8 + 2 - lift * .4, 1.0, .8, 'leg', sg < 0); c.cap(bx + sg * 10, by + (i - 1) * 3.8 + 2 - lift * .4, bx + sg * 11.6, gy - lift, .8, .5, 'leg', sg < 0)
        c.ell(bx, by + 1.6, 7, 8, 'shell'); c.cap(bx, by - 5, bx, by + 9, .5, .5, 'gold')
        c.ell(bx, by - 6.4, 4.6, 3.4)
        if not back:
            c.cap(bx, by - 9, bx, by - 14 - (1 if mouth else 0), 1.4, .4, 'horn')
            for sg in (-1, 1): c.dot(bx + sg * 2, by - 7, hx('#101010') if squint else hx('#ff4030'))
    return c.render(PAL['escaravelho'], FLAT)


# ------------------------------------------------------------------ VERME DAS AREIAS
def verme(view, ph=0.0, bob=0, lunge=0, mouth=0, squint=False, tail=0.0, head_dy=0, **kw):
    c = Cv(); cx = W // 2; gy = BASE
    N = 9
    for i in range(N):                                    # corpo segmentado que sobe da areia
        t = i / (N - 1)
        x = cx - 14 + t * 14 + lunge * .5 * t; y = gy - 2 - (math.sin(t * math.pi) * (9 + bob) + t * 8) + math.sin(ph * 2 - t * 6) * 1.2
        r = 4.6 + 3 * t
        c.ell(x, y, r, r * .9)
        c.cap(x - r * .5, y - r * .6, x - r * .5, y + r * .6, .6, .6, 'ring')
    hxx = cx + lunge * .6 + 1; hyy = gy - 2 - 8 - 8 + head_dy
    c.ell(hxx, hyy, 7.4, 6.2); c.ell(hxx + 2.4, hyy + .6, 4.4, 4.2, 'maw')
    for k in range(6):
        a = k * 1.05; c.cap(hxx + 2.4 + math.cos(a) * 4, hyy + .6 + math.sin(a) * 3.8, hxx + 2.4 + math.cos(a) * 2.4, hyy + .6 + math.sin(a) * 2.2, .8, .3, 'tooth')
    c.dot(hxx - 3, hyy - 3, hx('#101010') if squint else hx('#101010'))
    return c.render(PAL['verme'], FLAT)


DRAW.update({
    'escorpiao': _escorpiao('escorpiao'), 'escorpiao_sal': _escorpiao('escorpiao_sal'),
    'lagarto': _lagarto('lagarto'), 'salamandra': _lagarto('salamandra', flame=True),
    'chacal': _canino('chacal', size=.9, lean=.82), 'lobo_poeira': _canino('poeira', size=1.12, lean=.95, mane=True),
    'cao_guerra': _canino('guerra', size=1.1, lean=1.0, armor=True), 'cao_infernal': _canino('infernal', size=1.12, lean=.95, horns=True, ember=True),
    'abutre': abutre, 'escaravelho': escaravelho, 'verme': verme})

if __name__ == '__main__':
    import sys
    from PIL import Image
    ks = sys.argv[1:] or ['escorpiao', 'escorpiao_sal', 'lagarto', 'salamandra', 'chacal', 'lobo_poeira', 'cao_guerra', 'cao_infernal', 'abutre', 'escaravelho', 'verme']
    S = Image.new('RGBA', (72 * 4 * 3, 64 * 4 * len(ks)), (150, 120, 80, 255))
    for i, k in enumerate(ks):
        for j, v in enumerate(('right', 'down', 'up')):
            S.alpha_composite(DRAW[k](v, .6).resize((72 * 4, 64 * 4), Image.NEAREST), (j * 72 * 4, i * 64 * 4))
    S.save('/tmp/fauna3.png'); print(S.size)
