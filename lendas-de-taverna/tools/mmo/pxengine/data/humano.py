#!/usr/bin/env python3
"""HUMANO: humanoides inimigos de UMA SO MASSA, proporcao chibi (cabeca grande), cada um com silhueta/cabelo/roupa/arma proprios (regra do dono:
nada de 'heroi com outra cor'). Mesmo motor do fauna.py (mascara unica, luz cima-esquerda, contorno unico). spec = dict (ver SPECS).
API: draw(spec, view, ph, ...) e anim(spec, k, view, dense)."""
import math
import numpy as np
from PIL import Image
from fauna import Cv, hx, FLAT, W, H, BASE


def ramp(c, shift=0):
    r, g, b = hx(c)
    d = (int(r * .56), int(g * .52), int(min(255, b * .66 + 6 + shift)))
    l = (min(255, int(r * 1.28 + 14)), min(255, int(g * 1.24 + 12)), min(255, int(b * 1.14 + 8)))
    return (d, (r, g, b), l)


SKIN = {'pele': '#e8b890', 'escura': '#a06a44', 'palida': '#d8c8d0', 'goblin': '#7aa646', 'osso': '#d8d0b4', 'zumbi': '#7a9a6a', 'afogado': '#6a9aa0', 'ogro': '#7a9a44', 'cinza': '#9a98a8'}


def weapon(c, x, y, ang, L, kind, reg_w='wood', reg_m='metal'):
    dx, dy = math.cos(ang), math.sin(ang)
    if kind == 'sword': c.cap(x - dx * 2, y - dy * 2, x + dx * 3, y + dy * 3, .8, .8, 'wood'); c.cap(x + dx * 3, y + dy * 3, x + dx * (3 + L), y + dy * (3 + L), 1.3, .7, 'metal')
    elif kind == 'dagger': c.cap(x, y, x + dx * 2, y + dy * 2, .8, .8, 'wood'); c.cap(x + dx * 2, y + dy * 2, x + dx * (2 + L * .55), y + dy * (2 + L * .55), 1.0, .4, 'metal')
    elif kind == 'axe':
        c.cap(x, y, x + dx * L, y + dy * L, .8, .8, 'wood'); px, py = -dy, dx
        c.cap(x + dx * (L - 1) + px * 3.2, y + dy * (L - 1) + py * 3.2, x + dx * (L - 1) - px * .6, y + dy * (L - 1) - py * .6, 2.4, 1.2, 'metal')
    elif kind == 'staff':
        c.cap(x - dx * 5, y - dy * 5, x + dx * L, y + dy * L, .8, .8, 'wood')
    elif kind == 'club': c.cap(x, y, x + dx * L, y + dy * L, .9, 1.0, 'wood'); c.cap(x + dx * (L - 4), y + dy * (L - 4), x + dx * (L + 1), y + dy * (L + 1), 2.2, 2.7, 'wood')
    elif kind == 'bomb': c.ell(x, y, 2.9, 2.9, 'bomb'); c.cap(x, y - 2.4, x + 1.4, y - 4.4, .5, .5, 'wood'); c.dot(x + 1.6, y - 5, hx('#ffb030'))
    elif kind == 'sunstaff':
        c.cap(x - dx * 5, y - dy * 5, x + dx * L, y + dy * L, .8, .8, 'wood'); c.ell(x + dx * (L + 2), y + dy * (L + 2), 3.0, 3.0, 'gem'); c.ell(x + dx * (L + 2), y + dy * (L + 2), 1.3, 1.3, 'wood')
        for k in range(8): a = k * .785; c.dot(x + dx * (L + 2) + math.cos(a) * 4.4, y + dy * (L + 2) + math.sin(a) * 4.4, hx('#ffe070'))
    elif kind == 'pick':
        c.cap(x - dx * 2, y - dy * 2, x + dx * L, y + dy * L, .8, .8, 'wood'); px, py = -dy, dx
        c.cap(x + dx * (L - 1) + px * 4, y + dy * (L - 1) + py * 4, x + dx * (L - 1) - px * 4, y + dy * (L - 1) - py * 4, 1.0, 1.0, 'metal')
    elif kind == 'spear':
        c.cap(x - dx * 4, y - dy * 4, x + dx * L, y + dy * L, .8, .8, 'wood'); c.cap(x + dx * L, y + dy * L, x + dx * (L + 4), y + dy * (L + 4), 1.5, .3, 'metal'); px, py = -dy, dx
        c.cap(x + dx * (L - 1) + px * 2.4, y + dy * (L - 1) + py * 2.4, x + dx * (L + 2.4) + px * 2.4, y + dy * (L + 2.4) + py * 2.4, .5, .4, 'metal'); c.cap(x + dx * (L - 1) - px * 2.4, y + dy * (L - 1) - py * 2.4, x + dx * (L + 2.4) - px * 2.4, y + dy * (L + 2.4) - py * 2.4, .5, .4, 'metal')
    elif kind == 'bow':
        px, py = -dy, dx
        c.cap(x - dx * 1 + px * 9, y - dy * 1 + py * 9, x + dx * 5, y + dy * 5, 1.1, 1.1, 'wood'); c.cap(x - dx * 1 - px * 9, y - dy * 1 - py * 9, x + dx * 5, y + dy * 5, 1.1, 1.1, 'wood')
        for k in range(-8, 9): c.dot(x - dx * 1.6 + px * k * 1.1, y - dy * 1.6 + py * k * 1.1, hx('#f4ecd0'))
        c.cap(x - dx * 1.6, y - dy * 1.6, x + dx * 8, y + dy * 8, .5, .3, 'metal')
    elif kind == 'scythe':
        c.cap(x - dx * 3, y - dy * 3, x + dx * L, y + dy * L, .8, .8, 'wood'); px, py = -dy, dx
        c.cap(x + dx * L, y + dy * L, x + dx * L + px * 6, y + dy * L + py * 6 - 1, 1.3, .5, 'metal')





def eye2(c, x, y, col, hi=True, squint=False):
    x, y = int(round(x)), int(round(y)); col = hx(col)
    for dx in (0, 1):
        for dy in (0, 1): c.dot(x + dx, y + dy, col if not squint or dy else hx('#14101c'))
    if hi and not squint: c.dot(x, y, hx('#ffffff'))


def build(spec):
    S = spec; P = {}
    for k in ('skin', 'hair', 'cloth', 'cloth2', 'pants', 'boots', 'hood', 'metal2', 'belly', 'wrap', 'ear', 'turban'):
        if k in S: P[k] = ramp(S[k] if isinstance(S[k], str) else S.get('hood_c', S.get('cloth', '#808080')))
    P['body'] = P['skin']; P['wood'] = ramp('#7a5230'); P['metal'] = ramp(S.get('blade', '#c8d0e0')); P['bomb'] = ramp('#2a2430')
    P['cape'] = ramp(S.get('cape', '#3a2a30')); P['gem'] = ramp(S.get('gem', '#60e090')); P.setdefault('metal2', ramp('#8a92a8')); P.setdefault('turban', ramp('#d8c8a0'))
    return P


def draw(S, view, ph=0.0, bob=0, lunge=0, mouth=0, squint=False, head_dy=0, **kw):
    c = Cv(); cx = W // 2; gy = BASE; P = build(S)
    h = S.get('h', 1.0); hr = S.get('head', 7.4); tr = S.get('torso', 5.0); ty = S.get('torso_h', 5.2); leg = S.get('leg', 6.0)
    by = gy - leg - ty + 1 + bob; hy = by - ty - hr * .55 + head_dy
    if S.get('stoop'): hy += S['stoop']
    big = S.get('bulk', 0)
    w = tr + big
    lift = lambda p0: max(0, math.sin(ph + p0)) * 2.4
    if view == 'right':
        bx = cx - 1 + lunge * .4
        c.cur = 'cape'
        if S.get('cape') and S.get('has_cape', 1): c.cap(bx - 3, by - ty + 1, bx - 7, gy - 4 + math.sin(ph) * .8, 3.4, 4.4, 'cape')
        c.cur = 'legs'
        for lx, p0, far in ((-1.6, 0, True), (1.4, math.pi, False)):
            l_ = lift(p0); sw = math.cos(ph + p0) * 3.0
            c.cap(bx + lx, by + ty - 1, bx + lx + sw * .6, gy - 2.2 - l_, S.get('leg_r', 2.1) + big * .25, S.get('leg_r', 2.1) * .86, 'pants', far)
            c.cap(bx + lx + sw * .6, gy - 3 - l_, bx + lx + sw + 1.2, gy - .6 - l_, 2.0, 1.7, 'boots', far); c.ell(bx + lx + sw + 2.2, gy - 1.2 - l_, 2.3, 1.3, 'boots', far)
        c.cur = 'torso'
        c.ell(bx - .5, by - ty * .25, w, ty * .8 + .6, 'cloth'); c.ell(bx - .3, by + ty * .55, w * .78, ty * .55 + .6, 'cloth')
        if S.get('robe'): c.ell(bx - .5, by + ty + leg * .35, w + 2.6, leg * .55 + 1.5, 'cloth')
        if S.get('chest'): c.ell(bx + .6, by - ty * .15, w * .62, ty * .55, 'metal2')
        if S.get('belly'): c.ell(bx + .5, by + 1, w * .75, ty * .7, 'belly')
        if S.get('tunic'): c.ell(bx, by + ty * .7, w + .6, 2.2, 'cloth2')
        c.cur = 'pad'
        if S.get('pads'): c.ell(bx - 1, by - ty + 1.2, 3.4 + big * .4, 2.8, 'metal2')
        if S.get('wraps'):
            for k in range(-2, 3): c.ell(bx + k * 1.8, by + k % 2, 1.0, ty * .95, 'wrap')
        c.cur = 'arm'
        ax = -.55 + (lunge * .04) - math.sin(ph) * .2
        sx_, sy_ = bx + 1.5, by - ty + 2
        hx_, hy2 = sx_ + math.cos(ax + .7) * 6.8, sy_ + math.sin(ax + .7) * 6.8 + 1.6
        c.cap(sx_, sy_, hx_, hy2, S.get('arm_r', 1.9) + big * .2, S.get('arm_r', 1.9) * .9, S.get('arm_reg') or ('cloth2' if S.get('sleeves') else 'cloth')); c.ell(hx_, hy2, S.get('hand_r', 1.9), S.get('hand_r', 1.9), S.get('hand_reg', 'body'))
        c.cur = 'weapon'
        if S.get('weapon'): weapon(c, hx_, hy2, S.get('wang', -.95) + lunge * .03, S.get('wlen', 10), S['weapon'])
        # cabeça
        c.cur = 'head:'
        hxx = bx + 1.2 + lunge * .3
        if S.get('hair_back'): c.ell(hxx - 2.6, hy + 1.6, hr * .8, hr * .95, 'hair')
        if S.get('hood'): c.ell(hxx - 1.2, hy - .4, hr + 1.4, hr + 1.2, 'hood'); c.cap(hxx - 5, hy + 1, hxx - 7, hy + 6, 2.4, 1.4, 'hood')
        if S.get('hood_point'): c.cap(hxx - 1, hy - hr, hxx - 4, hy - hr - 6, 3.2, .5, 'hood')
        c.ell(hxx, hy, hr * .93, hr, 'body') if not S.get('hood') else c.ell(hxx + 1.6, hy + .8, hr * .72, hr * .82, 'body')
        if S.get('helm'):
            if S.get('helm_open'): c.ell(hxx - .2, hy - hr * .8, hr + .6, hr * .42, 'metal2'); c.cap(hxx + hr * .45, hy - hr * .6, hxx + hr * .5, hy + 1.2, .8, .8, 'metal2')
            else: c.ell(hxx - .2, hy - 1.2, hr + .6, hr * .8, 'metal2')
        if S.get('ears'): c.cap(hxx - 1, hy - 1, hxx - 7.5, hy - 4.2, 2.1, .7, 'body'); c.cap(hxx - 1, hy, hxx - 7, hy - 1.5, 1.5, .5, 'body')
        if S.get('nose'): c.ell(hxx + hr * .93 + .4, hy + 1.8, S['nose'], S['nose'] * .85, 'body')
        if S.get('snout'): c.ell(hxx + hr * .9 + 1.6, hy + 2.4, 3.6, 2.8, 'body')
        if S.get('hair_style') in ('spiky', 'wild'):
            for k in range(5):
                a = -2.7 + k * .42; L_ = hr + 1.6 + (k % 2) * 1.2; c.cap(hxx + math.cos(a) * hr * .6, hy + math.sin(a) * hr * .6 - .5, hxx + math.cos(a) * L_, hy + math.sin(a) * L_, 1.9, .7, 'hair')
        if S.get('hair_style') in ('mohawk',):
            for k in range(5): c.cap(hxx - 3 + k * 1.6, hy - hr + .8, hxx - 3.6 + k * 1.7, hy - hr - 3 - (k % 2), 1.3, .5, 'hair')
        if S.get('hair_style') == 'weeds':
            c.ell(hxx - .5, hy - hr * .55, hr * .9, hr * .5, 'hair')
            for k in range(3): c.cap(hxx - 3 - k * 1.6, hy - 1, hxx - 4 - k * 2.0 + math.sin(ph + k) * .6, hy + hr + 4 + k, 1.3, .6, 'hair')
        if S.get('hair_style') == 'fringe': c.ell(hxx + .4, hy - hr * .62, hr * .9, hr * .46, 'hair')
        if S.get('hair_style') == 'tuft': c.cap(hxx, hy - hr + 1, hxx + 2, hy - hr - 3.2, 1.8, .6, 'hair')
        if S.get('horns'): c.cap(hxx - 1.5, hy - hr + 1.5, hxx - 3, hy - hr - 4.4, 1.7, .5, 'horn'); c.cap(hxx + 3.5, hy - hr + 1.6, hxx + 4.4, hy - hr - 3.6, 1.5, .5, 'horn')
        if S.get('mask'): c.ell(hxx + hr * .5, hy + hr * .66, hr * .5, hr * .3, 'cloth2'); c.cap(hxx - hr * .7, hy + hr * .3, hxx - hr - 3, hy + hr * .6 + math.sin(ph) * 1.2, 1.0, .5, 'cloth2')
        if S.get('bandana'): c.ell(hxx - .2, hy - hr * .55, hr * .98, 1.9, 'cloth2'); c.cap(hxx - hr + .5, hy - hr * .55, hxx - hr - 3, hy - hr * .2 + math.sin(ph) * 1.5, 1.0, .4, 'cloth2')
        if S.get('hat'): c.ell(hxx, hy - hr * .72, hr + 3.2, 1.6, 'cloth2'); c.ell(hxx + .3, hy - hr - 2, hr * .66, 3.6, 'cloth2')
        if S.get('turban'):
            c.ell(hxx - .4, hy - hr * .5, hr + 1.2, hr * .62 + .8, 'turban'); c.ell(hxx - .6, hy - hr * .9, hr * .72, 2.6, 'turban'); c.cap(hxx - hr + .4, hy - 1, hxx - hr - 3, hy + 4 + math.sin(ph) * 1.2, 1.8, .8, 'turban')
        if S.get('beard'): c.ell(hxx + 1.2, hy + hr * .98, hr * .55, hr * .4 + S['beard'] * .5, 'hair')
        if S.get('nemes'): c.cap(hxx - hr + .6, hy, hxx - hr - 1.5, hy + hr + 4, 2.6, 2.2, 'turban'); c.ell(bx - .5, by - ty + 1.2, w * .9, 1.5, 'turban')
        if S.get('spikes'):
            for k in range(3): c.cap(bx - 2 + k * 2.2, by - ty + 1, bx - 3 + k * 2.6, by - ty - 5 - (k % 2) * 2, 1.9, .3, 'gem')
        if S.get('crests'): [c.cap(hxx - 1 + k * 2.4, hy - hr + .8, hxx - 1.6 + k * 2.4, hy - hr - 3.4 - (k % 2), 1.2, .4, 'cloth2') for k in range(-1, 3)]
        ex, ey = hxx + hr * .5, hy - .6
        col = S.get('eye', '#14101c'); eye2(c, ex, ey - .5, col, S.get('eye_hi', 1), squint)
        if S.get('eye2'): c.dot(ex + 2, ey, hx(S['eye2']))
        if S.get('scar'): c.dot(ex - 1, ey + 1.5, hx('#8a3a3a')); c.dot(ex, ey + 2.5, hx('#8a3a3a'))
        if mouth and not S.get('mask'): [c.dot(hxx + hr * .5 + q, hy + hr * .55, hx('#2a1018')) for q in range(0, 3)]
        if S.get('tusks'): c.cap(hxx + hr * .55, hy + hr * .62, hxx + hr * .66, hy + hr * .62 - 3.4, .9, .5, 'bone')
    else:
        back = view == 'up'; bx = cx
        c.cur = 'cape'
        if S.get('cape') and S.get('has_cape', 1) and back: c.ell(bx, by + 1, w + 2.4, ty + 4.2, 'cape')
        c.cur = 'legs'
        for sx, p0 in ((-2.6, 0), (2.6, math.pi)):
            l_ = lift(p0)
            c.cap(bx + sx, by + ty - 1, bx + sx, gy - 2.6 - l_, S.get('leg_r', 2.1) + big * .25, S.get('leg_r', 2.1) * .86, 'pants'); c.cap(bx + sx, gy - 3.4 - l_, bx + sx, gy - .5 - l_, 2.1, 1.9, 'boots'); c.ell(bx + sx, gy - 1 - l_, 2.5, 1.3, 'boots')
        c.cur = 'torso'
        c.ell(bx, by - ty * .25, w + 1.0, ty * .8 + .6, 'cloth'); c.ell(bx, by + ty * .55, (w + 1.0) * .8, ty * .55 + .6, 'cloth')
        if S.get('robe'): c.ell(bx, by + ty + leg * .35, w + 3.2, leg * .55 + 1.5, 'cloth')
        if S.get('chest') and not back: c.ell(bx, by - ty * .15, w * .66, ty * .55, 'metal2')
        if S.get('belly') and not back: c.ell(bx, by + 1, w * .8, ty * .7, 'belly')
        if S.get('tunic'): c.ell(bx, by + ty * .7, w + 1.4, 2.2, 'cloth2')
        c.cur = 'pad'
        if S.get('pads'):
            for sg in (-1, 1): c.ell(bx + sg * (w - .4), by - ty + 1.4, 3.4 + big * .4, 2.8, 'metal2')
        if S.get('wraps'):
            for k in range(-2, 3): c.ell(bx, by + k * 1.9, w, 1.0, 'wrap')
        if S.get('cape') and S.get('has_cape', 1) and back: pass
        c.cur = 'arm'
        for sg in (-1, 1):
            sx_, sy_ = bx + sg * (w + .2), by - ty + 2; ex_, ey_ = sx_ + sg * 1.6, sy_ + 6.8
            if S.get('arms_fwd') and not back: ex_, ey_ = sx_ + sg * .6, sy_ + 4
            c.cap(sx_, sy_, ex_, ey_, S.get('arm_r', 1.9) + big * .25, S.get('arm_r', 1.9) * .9 + big * .15, S.get('arm_reg') or ('cloth2' if S.get('sleeves') else 'cloth')); c.ell(ex_, ey_ + .6, S.get('hand_r', 1.9) + big * .3, S.get('hand_r', 1.9) + big * .3, S.get('hand_reg', 'body'))
            if S.get('bracers'): c.dot(ex_ - 1, ey_ - 1, hx('#3a2a1a')); c.dot(ex_, ey_ - 1, hx('#3a2a1a')); c.dot(ex_ + 1, ey_ - 1, hx('#3a2a1a'))
        c.cur = 'weapon'
        if S.get('weapon'): weapon(c, bx + w + 2, by + 3, S.get('wang_f', -1.3), S.get('wlen', 10), S['weapon'])
        c.cur = 'head:'
        hh = hy
        if S.get('hair_back') or S.get('hair') and back: c.ell(bx, hh + 1.2, hr + .4, hr + .6, 'hair') if back else c.ell(bx, hh - 1, hr + .6, hr + .4, 'hair')
        if S.get('hood'): c.ell(bx, hh - .2, hr + 1.4, hr + 1.2, 'hood'); c.cap(bx, hh + hr - 1, bx, hh + hr + 3, 3, 1.6, 'hood')
        if S.get('hood_point'): c.cap(bx, hh - hr, bx + 1.5, hh - hr - 6, 3.2, .5, 'hood')
        if S.get('hood') and not back: c.ell(bx, hh + 1.2, hr * .74, hr * .8, 'body')
        elif not S.get('hood'): c.ell(bx, hh, hr, hr * .98, 'hood' if (back and S.get('hood')) else ('hair' if back and S.get('hair_style') in ('long',) else 'body'))
        if S.get('helm'):
            if S.get('helm_open'): c.ell(bx, hh - hr * .8, hr + .8, hr * .42, 'metal2'); c.cap(bx, hh - hr * .6, bx, hh + 1.6, .8, .8, 'metal2')
            else: c.ell(bx, hh - 1.2, hr + .8, hr * .82, 'metal2')
        if S.get('ears'):
            for sg in (-1, 1): c.cap(bx + sg * (hr - 1), hh - 1, bx + sg * (hr + 6.5), hh - 4.4, 2.1, .7, 'body')
        if S.get('hair_style') in ('spiky', 'wild'):
            for k in range(6):
                a = -2.9 + k * .52; L_ = hr + 1.6 + (k % 2) * 1.2; c.cap(bx + math.cos(a) * hr * .6, hh + math.sin(a) * hr * .6 - .5, bx + math.cos(a) * L_, hh + math.sin(a) * L_, 1.9, .7, 'hair')
        if S.get('hair_style') == 'mohawk':
            for k in range(5): c.cap(bx, hh - hr + 1 + k * 1.2, bx, hh - hr - 3 - (k % 2) + k * 1.2, 1.2, .5, 'hair') if False else c.cap(bx - 1 + k * .5, hh - hr + 1, bx - 1 + k * .5, hh - hr - 3 - (k % 2), 1.2, .5, 'hair')
        if S.get('hair_style') == 'weeds':
            c.ell(bx, hh - hr * .5, hr, hr * .55, 'hair')
            for sg in (-1, 1):
                for k in range(2): c.cap(bx + sg * (hr - .6 + k * 1.6), hh, bx + sg * (hr + .4 + k * 1.8), hh + hr + 3 + k * 1.5 + math.sin(ph + k + sg) * .6, 1.4, .6, 'hair')
        if S.get('hair_style') == 'fringe' and not back: c.ell(bx, hh - hr * .56, hr * .98, hr * .5, 'hair')
        if S.get('hair_style') == 'fringe' and back: c.ell(bx, hh, hr, hr * .98, 'hair')
        if S.get('hair_style') == 'tuft': c.cap(bx, hh - hr + 1, bx + 1.5, hh - hr - 3.2, 1.8, .6, 'hair')
        if S.get('horns'):
            for sg in (-1, 1): c.cap(bx + sg * (hr - 2), hh - hr + 2, bx + sg * (hr - .5), hh - hr - 3.8, 1.7, .5, 'horn')
        if S.get('bandana'): c.ell(bx, hh - hr * .55, hr, 1.9, 'cloth2')
        if S.get('hat'): c.ell(bx, hh - hr * .72, hr + 3.2, 1.6, 'cloth2'); c.ell(bx, hh - hr - 2, hr * .66, 3.6, 'cloth2')
        if S.get('turban'):
            c.ell(bx, hh - hr * .5, hr + 1.2, hr * .62 + .8, 'turban'); c.ell(bx, hh - hr * .9, hr * .72, 2.6, 'turban')
            if back: c.cap(bx + 1, hh + 1, bx + 2.4, hh + hr + 3, 1.8, .8, 'turban')
        if S.get('beard') and not back: c.ell(bx, hh + hr * .98, hr * .58, hr * .4 + S['beard'] * .5, 'hair')
        if S.get('nemes'):
            for sg in (-1, 1): c.cap(bx + sg * (hr - .4), hh, bx + sg * (hr + 1.2), hh + hr + 3, 2.2, 2.0, 'turban')
            c.ell(bx, by - ty + 1.2, w * .95, 1.6, 'turban')
        if S.get('spikes'):
            for sg in (-1, 1):
                for k in range(3): c.cap(bx + sg * (w - 1 + k * 1.6), by - ty + 1.4, bx + sg * (w + k * 2.2), by - ty - 4 - (k % 2) * 2, 1.9, .3, 'gem')
        if S.get('crests'): [c.cap(bx - 3 + k * 2, hh - hr + .8, bx - 3.4 + k * 2, hh - hr - 3.4 - (k % 2), 1.2, .4, 'cloth2') for k in range(0, 4)]
        if not back:
            col = S.get('eye', '#14101c')
            for sg in (-1, 1):
                eye2(c, bx + sg * hr * .42 - (1 if sg < 0 else 0), hh - 1.2 + (1 if S.get('hood') else 0), col, S.get('eye_hi', 1), squint)
            if S.get('snout'): c.ell(bx, hh + hr * .5, 3.2, 2.5, 'body')
            if S.get('nose'): c.ell(bx, hh + 1.8, S['nose'], S['nose'] * .85, 'body')
            if S.get('mask'): c.ell(bx, hh + hr * .66, hr * .78, hr * .3, 'cloth2')
            if S.get('scar'): c.dot(bx + hr * .42, hh + 1.2, hx('#8a3a3a')); c.dot(bx + hr * .42 + 1, hh + 2.2, hx('#8a3a3a'))
            if mouth and not S.get('mask'): [c.dot(bx + q, hh + hr * .6, hx('#2a1018')) for q in range(-1, 2)]
            elif not S.get('mask'): c.dot(bx, hh + hr * .6, hx('#4a2a2a'))
            if S.get('open_mouth'): [c.dot(bx + q, hh + hr * .6 + r, hx('#2a1018')) for q in range(-1, 2) for r in (0, 1)]
            if S.get('tusks'):
                for sg in (-1, 1): c.cap(bx + sg * hr * .6, hh + hr * .6, bx + sg * hr * .66, hh + hr * .6 - 3.2, .9, .5, 'bone')
            if S.get('eyeG'):
                pass
    details(c, S, view, bx, by, hy, hr, w, ty, view == 'up', ph)
    P.setdefault('horn', ramp('#d8cca0')); P.setdefault('bone', ramp('#e8e2d0'))
    return c.render(P, {k: v for k, v in FLAT.items() if k in ('white',) and False} or {})


def details(c, S, view, bx, by, hh, hr, w, ty, back, ph):
    """pixels de detalhe (cinto, fivela, tira, bandagens, visor, costelas, penacho...) desenhados depois da massa."""
    dk = hx(S.get('dark', '#1a1218'))
    if view == 'right':
        fx = [bx - 1.5 + q for q in range(-2, 3)]
    else:
        fx = [bx + q for q in range(-int(w) + 1, int(w))]
    if S.get('belt') and not (back and view != 'right'):
        yb = int(round(by + ty * .55))
        for x in fx: c.dot(x, yb, hx(S.get('belt_c', '#2a1a10')))
        if view != 'right': c.dot(bx, yb, hx('#e8c040')); c.dot(bx + 1, yb, hx('#e8c040'))
    if S.get('strap') and view != 'up':
        for k in range(8): c.dot((bx - w * .7 + k * 1.5) if view != 'right' else (bx - 2 + k * .7), by - ty * .8 + k * 1.1, hx(S.get('strap_c', '#3a2418')))
    if S.get('crown'):
        cc = hx(S.get('crown_c', '#e8e2d0')); px_ = bx - 1 if view == 'right' else bx; n_ = 5 if view != 'right' else 4
        for k in range(n_):
            xx = px_ + (k - (n_ - 1) / 2) * (hr * 2 * .8 / (n_ - 1)); hgt = 2 + (1 if k in (1, 2, 3) else 0)
            for r in range(int(hgt)): c.dot(xx, hh - hr - 1 - r + 1, cc)
        for q in range(int(-hr * .8), int(hr * .8) + 1): c.dot(px_ + q, hh - hr + 1, hx(S.get('crown_band', '#8a7a50')))
    if S.get('feathers'):
        cols = [hx(q) for q in S.get('feather_c', ['#d83a3a', '#e8c040', '#3aa0d8'])]
        px_ = bx - 1 if view == 'right' else bx
        for k, col in enumerate(cols):
            a = -1.9 + k * .62 if view != 'right' else -2.3 + k * .5
            for r in range(3, 9): c.dot(px_ + math.cos(a) * r, hh - hr * .55 + math.sin(a) * r, col); c.dot(px_ + math.cos(a) * r + 1, hh - hr * .55 + math.sin(a) * r, col)
    if S.get('warpaint') and not back:
        col = hx(S.get('paint_c', '#e8e0d0'))
        if view == 'right': [c.dot(bx + 4 + k, hh + 2 + (k % 2), col) for k in range(3)]
        else:
            for sg in (-1, 1): [c.dot(bx + sg * (2 + k), hh + 2.6 + (k % 2), col) for k in range(3)]
    if S.get('bones') and not back:
        for k in range(-2, 3): c.dot(bx + k * 1.4 - (1 if view == 'right' else 0), by - ty + 3 + abs(k) * .5, hx('#e8e2d0'))
    if S.get('stripes'):
        col = hx(S.get('stripe_c', '#8a7a54'))
        if view == 'right':
            for k in range(-3, 3): c.dot(bx - 3 + k * 1.2 + 3, by + k * 1.9 - 1, col); c.dot(bx - 2 + k * 1.2 + 3, by + k * 1.9, col)
            for k in range(3): c.dot(bx + 3 + k * 1.5, by - ty + 4 + k * 1.2, col)
        else:
            for k in range(-4, 5):
                y = by - ty + 2 + k * 1.9 + ty
                for x in range(int(bx - w + 1), int(bx + w)): 
                    if (x + k) % 3 == 0: c.dot(x, by + k * 1.5, col)
    if S.get('ribs') and not back:
        for k in range(3):
            for sg in (-1, 1): c.dot(bx + (sg * (1.5 + k * .5) if view != 'right' else 1.5 + k * .5), by - 1 + k * 1.6, hx('#2a3a22'))
    if S.get('visor') and not back:
        if view == 'right':
            for q in range(3): c.dot(bx + 4 + q, hh - 1, dk)
        else:
            for q in range(-3, 4): c.dot(bx + q, hh - 1, dk)
        c.dot(bx + (5 if view == 'right' else -1), hh - 1, hx(S.get('eye', '#60b0ff'))); c.dot(bx + (6 if view == 'right' else 1), hh - 1, hx(S.get('eye', '#60b0ff')))
    if S.get('plume'):
        px = bx - 1 if view == 'right' else bx
        for k in range(5): c.dot(px + math.sin(ph * 2 + k) * .6, hh - hr - 1 - k * .8 + 2, hx(S.get('plume_c', '#c83a3a'))); c.dot(px + 1, hh - hr - 1 - k * .8 + 2, hx(S.get('plume_c', '#c83a3a')))
    if S.get('rivets'):
        for k in (-1, 1): c.dot(bx + k * (w * .6), by - 1, hx('#d8dcec'))
    if S.get('head_stripes'):
        col = hx(S.get('stripe_c', '#8a7a54')); c0 = bx - 1 if view == 'right' else bx
        for k in range(-3, 4):
            y = hh + k * 1.5 + 1
            for q in range(-int(hr * .8), int(hr * .8) + 1):
                if (q + k) % 3 == 0 or abs(q) > hr * .7: c.dot(c0 + q + (1 if view == 'right' else 0), y, col)
        if not back:
            for q in range(-4, 5): c.dot(c0 + q + (1.5 if view == 'right' else 0), hh - 1, hx('#1a1812'))
            for sg in (-1, 1): c.dot(c0 + sg * 2.4 + (1.5 if view == 'right' else 0), hh - 1, hx(S.get('eye', '#40e8a0')))
        for k in range(4): c.dot(c0 - hr + (3 if view != 'right' else -2) - k * .6, hh + 3 + k * 1.4 + math.sin(ph + k) * .6, hx('#d8ccA4'))
    if S.get('emblem') and not back:
        ec = hx(S.get('emblem_c', '#ffe070')); ex_, ey_ = (bx + 1, by - 1) if view == 'right' else (bx, by - 1)
        for a in range(8): c.dot(ex_ + math.cos(a * .785) * 2.6, ey_ + math.sin(a * .785) * 2.6, ec)
        c.dot(ex_, ey_, ec)
    if S.get('brow') and not back:
        bc = hx(S.get('dark', '#1a1218'))
        for k in range(-2, 3): c.dot(bx + k + (3 if view == 'right' else 0), hh - 2.6, bc)
    if S.get('cracks'):
        cc = hx(S.get('crack_c', '#3a3a46'))
        for k in range(5): c.dot(bx - 3 + k * 1.4 + (1 if view == 'right' else 0), by - ty + 1 + k * 1.6, cc); c.dot(bx + 2 - k * .8, by - 1 + k * 1.2, cc)
    if S.get('lava'):
        lc = [hx('#ff9a30'), hx('#ffd060')]
        for k in range(6): c.dot(bx - 3 + k * 1.2, by - ty + 2 + (k * 7) % 5, lc[k % 2]); c.dot(bx + 2 - k * .7, by + (k * 5) % 4, lc[(k + 1) % 2])
        if not back: c.dot(bx, hh - 1, lc[1])
    if S.get('crystals'):
        cr = [hx('#a8d8ff'), hx('#e0f4ff')]
        for sg in (-1, 1):
            for k in range(3): c.cap(bx + sg * (w - 1 + k * .6), by - ty + 1, bx + sg * (w + k * 1.6), by - ty - 3 - k, 1.1, .3, 'gem') if False else [c.dot(bx + sg * (w + k * 1.5), by - ty - j + 1, cr[(j + k) % 2]) for j in range(2 + k)]
    if S.get('lamp'):
        lx_ = bx + (3 if view == 'right' else 0); c.dot(lx_, hh - hr - 1, hx('#ffe070')); c.dot(lx_ + 1, hh - hr - 1, hx('#fff6b0')); c.dot(lx_, hh - hr, hx('#ffe070'))
    if S.get('sockets') and not back:
        if view == 'right': c.dot(bx + 4, hh - 1, dk); c.dot(bx + 4, hh - 2, dk)
        else:
            for sg in (-1, 1): c.dot(bx + sg * hr * .42, hh - 1.6, dk); c.dot(bx + sg * hr * .42 + 1, hh - 1.6, dk)
    if S.get('stitch') and not back:
        for k in range(4): c.dot(bx + (1.5 if view == 'right' else -hr * .3) + k * .8, hh + 2 + k * .6, hx('#3a2a22'))
    if S.get('rags'):
        for k in range(4): c.dot(bx - w + 1 + k * 2.2, by + ty - 1 + (k % 2), hx('#00000000')[:3] if False else hx(S.get('cloth2', '#4a3a2e')))
    if S.get('skull') :
        sx, sy = (bx + 6, hh - 7) if view == 'right' else (bx + w + 3, by - 9)
        for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, -1), (1, -1), (-1, -1), (0, 1)): c.dot(sx + dx, sy + dy, hx('#e8e2d0'))
        c.dot(sx - .6, sy - .6, dk); c.dot(sx + .6, sy - .6, dk)


SPECS = {
 'grunk': dict(skin='#6e9e3e', arm_reg='body', chest=1, ears=1, nose=3.0, hair='#2a1a10', hair_style=None, cloth='#5a3a28', cloth2='#8a5a34', pants='#7a6a52', boots='#2a1a12', weapon='axe', wlen=16, wang=-.85, eye='#ff5030', eye_hi=0,
         head=7.8, torso=6.6, torso_h=6.2, leg=7.2, bulk=3.2, bracers=1, tusks=1, pads=1, metal2='#8a6a4a', cape='#4a2a18', belt=1, strap=1, strap_c='#2a1a10', scar=1, crown=1, crown_c='#efe6cc', bones=1, tunic=1, rivets=1, blade='#a8a8b8'),
 'goblin': dict(skin='#7aae48', ears=1, nose=2.4, hair='#3a2a18', hair_style='tuft', cloth='#7a5030', cloth2='#a07a40', pants='#5a4a30', boots='#3a2a1a', weapon='club', wlen=11, wang=-.9, eye='#f0e040', head=7.8, torso=4.0, torso_h=4.6, leg=4.8, tunic=1, belt=1, strap=1, strap_c='#4a3020', eye_hi=1, scar=1),
 'goblin_x': dict(skin='#6a9a58', ears=1, nose=2.2, cloth='#4a2a5a', cloth2='#8a3a6a', pants='#3a2a3a', boots='#2a1a2a', weapon='staff', wlen=15, wang=-1.2, wang_f=-1.4, eye='#ff6a40', head=7.8, torso=4.2, torso_h=4.6, leg=4.8, feathers=1, warpaint=1, bones=1, tunic=1, belt=1, belt_c='#6a2a5a', skull=1, eye_hi=0, paint_c='#f0e8d0', robe=0, hair='#2a1a30', hair_style='tuft'),
 'bandido': dict(skin=SKIN['pele'], hair='#3a2a20', hair_style='fringe', bandana=1, mask=1, cloth='#7a5a38', cloth2='#b02a2a', pants='#3a3430', boots='#2a2420', weapon='dagger', wlen=9, scar=1, eye='#2a3a5a', tunic=1, sleeves=1, head=7.2, belt=1, strap=1, torso=5.2),
 'carnical': dict(skin='#86a860', hair='#2a3a22', hair_style='wild', cloth='#6a5a48', cloth2='#4a3a2e', pants='#3a3a3a', boots='#2a2a2a', eye='#e8d040', eye_hi=0, stoop=3, arms_fwd=1, head=7.6, torso=4.8, scar=1, ribs=1, sockets=1, stitch=1, rags=1, tunic=1, open_mouth=1),
 'mumia': dict(skin='#dccfa6', wraps=1, cloth='#d0c49c', wrap='#e6dab4', cloth2='#bcb088', pants='#c8bc94', boots='#b8ac84', eye='#40e8a0', eye_hi=0, arms_fwd=1, head=7.4, bulk=.6, stripes=1, stripe_c='#8a7a54', head_stripes=1, torso=5.2, sleeves=1),
 'necro': dict(skin='#1c1626', robe=1, hood='#3a2a50', cloth='#2e2248', cloth2='#5a4a86', pants='#2a2040', boots='#1a1428', weapon='staff', wlen=15, wang=-1.2, wang_f=-1.4, eye='#e03a5a', eye_hi=0, head=7.2, torso=4.8, sleeves=1, tunic=1, belt=1, belt_c='#6a2a5a', skull=1, scar=0),
 'cav_caido': dict(skin=SKIN['osso'], helm=1, metal2='#8a92a8', cloth='#6a7288', cloth2='#a8b0c4', pants='#3a4050', boots='#2a2e3a', weapon='sword', wlen=14, wang=-1.0, pads=1, eye='#60b0ff', eye_hi=0, bulk=1.8, head=7.4, torso=5.8, sleeves=1, cape='#4a2a3a', visor=1, plume=1, plume_c='#b83040', rivets=1, belt=1, belt_c='#2a2e3a'),
 'goblin_sapador': dict(skin=SKIN['goblin'], ears=1, nose=1.8, hair='#4a3a20', hair_style='tuft', cloth='#8a5a30', cloth2='#c8a040', pants='#4a3a2a', boots='#3a2a1a', weapon='bomb', eye='#f0d040', eye_hi=1, head=7.0, torso=4.8, leg=5.2, tunic=1, bandana=1, belt=1, strap=1, strap_c='#6a2a18'),
 'ogro_lenhador': dict(skin=SKIN['ogro'], tusks=1, horns=1, hair='#3a2a1a', hair_style='tuft', cloth='#a85030', cloth2='#7a3a20', pants='#4a3a2a', boots='#3a2a20', belly='#98b85c', weapon='axe', wlen=13, wang=-.9, eye='#f0d040', head=8.0, torso=6.4, torso_h=6.0, leg=6.0, bulk=2.2, tunic=1, scar=1, belt=1),
 'afogado': dict(skin='#7aa8ac', hair='#1e4a38', hair_style='weeds', belly='#a8c8c0', cloth='#3a5a6a', cloth2='#2a4a5a', pants='#2a3a4a', boots='#1a2a3a', eye='#e0f0ff', eye_hi=0, arms_fwd=1, stoop=2, head=7.6, torso=4.8, tunic=1, sockets=1, rags=1, bulk=.8),
 'ladrao_esgoto': dict(skin='#c89a78', hair='#5a3a20', hair_style='fringe', bandana=1, hat=1, mask=1, cloth='#2e4a34', cloth2='#4a6a3a', pants='#2a2a2a', boots='#1a1a1a', weapon='dagger', wlen=10, eye='#e8e050', eye_hi=0, head=7.0, torso=4.6, sleeves=1, belt=1, strap=1),
 'cultista_lodo': dict(skin='#14200e', robe=1, hood='#3a5a2a', hood_point=1, cloth='#2a4a1e', cloth2='#6a9a3a', pants='#2a4a1e', boots='#1a2a14', weapon='staff', wlen=15, wang=-1.2, wang_f=-1.4, eye='#a0ff60', eye_hi=0, head=7.2, torso=5.0, sleeves=1, tunic=1, belt=1, belt_c='#7ac03a', skull=1),
}
SPECS.update({
 # ---- Região 2: GOLEMS refinados (braços e punhos grossos, ombros largos, cabeça pequena afundada, rachaduras)
 'golem_pedra': dict(skin='#7c7c88', cloth='#8a8a98', cloth2='#a2a2b0', pants='#6a6a78', boots='#52525e', metal2='#a8a8b6', chest=1, pads=1, cracks=1, crack_c='#2e2e3a', brow=1, eye='#ffa030', eye_hi=0, head=5.8, torso=8.4, torso_h=7.0, leg=4.8, leg_r=3.4, arm_r=3.4, hand_r=4.0, hand_reg='cloth2', bulk=3.6, arm_reg='cloth', dark='#1a1a22'),
 'golem_sal': dict(skin='#b8b0cc', cloth='#c8c0dc', cloth2='#e8e0f4', pants='#a49cb8', boots='#8a8298', metal2='#e8e0f4', chest=1, pads=1, spikes=1, gem='#7ac8ff', cracks=1, crack_c='#5a6a9a', brow=1, eye='#40b0ff', eye_hi=0, head=5.8, torso=8.2, torso_h=7.0, leg=4.8, leg_r=3.4, arm_r=3.4, hand_r=4.0, hand_reg='cloth2', bulk=3.6, arm_reg='cloth', dark='#2a2a44'),
 'golem_magma': dict(skin='#2e2428', cloth='#42302e', cloth2='#5a3a30', pants='#2a1c1c', boots='#1a1212', metal2='#e8641a', chest=1, pads=1, lava=1, spikes=1, gem='#ff8a30', brow=1, eye='#ffe060', eye_hi=0, head=5.8, torso=8.6, torso_h=7.2, leg=4.8, leg_r=3.4, arm_r=3.5, hand_r=4.2, hand_reg='metal2', bulk=3.8, arm_reg='cloth', dark='#0e0808'),
})
SPECS.update({
 # ---- Região 2 (Terras Áridas): humanoides do deserto, cada um com silhueta própria
 'bandido_deserto': dict(skin='#c89a6a', turban='#e0d0a8', mask=1, cloth='#c8a060', cloth2='#a83a2a', pants='#6a5a40', boots='#4a3a28', weapon='sword', wlen=11, wang=-.95, eye='#2a1a10', eye_hi=1, head=7.0, torso=5.0, tunic=1, belt=1, belt_c='#7a2a1a', strap=1, strap_c='#5a3a20', sleeves=1, cape='#8a3a2a', scar=1),
 'saqueador': dict(skin='#c08a60', helm=1, helm_open=1, metal2='#7a6a58', hair='#2a1a10', beard=.8, cloth='#6a4a30', cloth2='#3a2a1c', pants='#4a3a2a', boots='#2a1a12', weapon='axe', wlen=13, wang=-.9, eye='#e8c040', eye_hi=0, head=7.4, torso=5.8, torso_h=5.6, bulk=1.6, pads=1, scar=1, belt=1, strap=1, sleeves=1, rivets=1, cape='#5a2a1a'),
 'atirador_deserto': dict(skin='#d8aa78', turban='#6a7a4a', mask=1, cloth='#8a7a4a', cloth2='#5a6a3a', pants='#5a4a30', boots='#3a2a1a', weapon='bow', wlen=11, wang=-1.4, wang_f=-1.6, eye='#2a3a1a', eye_hi=1, head=6.8, torso=4.8, tunic=1, belt=1, strap=1, strap_c='#4a3a20', sleeves=1),
 'cultista_sol': dict(skin='#c88a50', emblem=1, robe=1, hood='#e8b830', hood_point=1, cloth='#c87a18', cloth2='#f0d060', pants='#c87a18', boots='#6a4a18', weapon='sunstaff', wlen=16, wang=-1.2, wang_f=-1.4, gem='#ffe070', eye='#fff080', eye_hi=0, head=7.2, torso=5.0, sleeves=1, tunic=1, belt=1, belt_c='#f0d060'),
 'mumia_solar': dict(skin='#d8c890', wraps=1, nemes=1, turban='#e8c040', cloth='#e0cc88', wrap='#f0e0a0', cloth2='#c8a850', pants='#d8c484', boots='#b8a064', eye='#ffd040', eye_hi=0, arms_fwd=1, head=7.4, bulk=.8, stripes=1, stripe_c='#b8902a', head_stripes=1, torso=5.4, sleeves=1, crests=1, belt=1, belt_c='#e8c040', emblem=1, emblem_c='#e8c040'),
 'kobold': dict(skin='#b87040', ears=1, nose=2.0, helm=1, helm_open=1, metal2='#8a8a96', lamp=1, cloth='#6a4a34', cloth2='#8a6a44', pants='#4a3a2a', boots='#3a2a1a', weapon='pick', wlen=10, wang=-.9, eye='#ffe040', eye_hi=1, head=7.8, torso=3.8, torso_h=4.2, leg=4.2, tunic=1, belt=1, strap=1, strap_c='#3a2a18'),
 'anao_renegado': dict(skin='#e0a878', hair='#c85a1a', beard=2.0, helm=1, helm_open=1, metal2='#6a6a78', cloth='#5a2a2a', cloth2='#8a8a96', pants='#3a2a2a', boots='#2a1a1a', weapon='axe', wlen=12, wang=-.9, eye='#ff7a30', eye_hi=0, head=7.4, torso=6.2, torso_h=5.0, leg=4.4, bulk=2.6, pads=1, rivets=1, belt=1, belt_c='#6a3a1a', scar=1, sleeves=1, tunic=1),
 'golem_pedra_old': dict(skin='#8a8a94', cloth='#7a7a86', cloth2='#9a9aa6', pants='#6a6a76', boots='#5a5a66', metal2='#9a9aa6', chest=1, pads=1, cracks=1, crack_c='#3a3a46', eye='#ffa030', eye_hi=0, head=5.4, torso=7.6, torso_h=7.0, leg=5.2, bulk=3.8, arm_reg='cloth2', arms_fwd=1),
 'golem_sal_old': dict(skin='#e8e4e8', cloth='#d8d4dc', cloth2='#f4f0f6', pants='#c8c4cc', boots='#b8b4bc', metal2='#f4f0f6', chest=1, pads=1, crystals=1, cracks=1, crack_c='#9aa8c8', eye='#60c0ff', eye_hi=0, head=5.4, torso=7.4, torso_h=6.8, leg=5.2, bulk=3.6, arm_reg='cloth2', arms_fwd=1),
 'golem_magma_old': dict(skin='#2a2024', cloth='#3a2a2a', cloth2='#5a3a30', pants='#2a1c1c', boots='#1a1212', metal2='#e0601a', chest=1, pads=1, lava=1, eye='#ffe060', eye_hi=0, head=5.4, torso=7.6, torso_h=7.0, leg=5.2, bulk=3.8, arm_reg='cloth2', arms_fwd=1, horns=1),
 'cav_negro': dict(skin='#2a2630', helm=1, metal2='#3a3a48', cloth='#26262e', cloth2='#4a4a5a', pants='#1e1e26', boots='#14141c', weapon='sword', wlen=16, wang=-1.0, pads=1, eye='#ff3030', eye_hi=0, bulk=2.2, head=7.4, torso=5.9, sleeves=1, cape='#6a1a1a', visor=1, plume=1, plume_c='#8a1a1a', rivets=1, belt=1, belt_c='#6a1a1a'),
 'armadura': dict(skin='#14101c', helm=1, metal2='#8a92a8', cloth='#6a7288', cloth2='#a8b0c4', pants='#4a5268', boots='#3a4258', weapon='sword', wlen=13, wang=-1.0, pads=1, eye='#a060ff', eye_hi=0, bulk=2.4, head=7.2, torso=5.8, sleeves=1, visor=1, rivets=1, belt=1, belt_c='#2a2e3a', arms_fwd=1, stoop=1),
 'mago_batalha': dict(skin='#c89a78', robe=1, hat=1, hair='#e8e4e0', beard=1.6, cloth='#3a4a8a', cloth2='#d8a830', pants='#3a4a8a', boots='#2a2a4a', weapon='staff', wlen=15, wang=-1.2, wang_f=-1.4, eye='#a0d0ff', eye_hi=0, head=7.0, torso=5.0, sleeves=1, tunic=1, belt=1, belt_c='#d8a830', skull=0),
 'imp': dict(skin='#c83a28', horns=1, ears=1, nose=1.6, cloth='#3a1a1a', cloth2='#c83a28', pants='#c83a28', boots='#8a2a20', weapon='spear', wlen=12, wang=-.95, eye='#ffe040', eye_hi=0, head=7.8, torso=3.8, torso_h=4.4, leg=4.2, tunic=1, scar=0, cape='#5a1a14'),
 'troll_mesas': dict(skin='#7a6a8a', tusks=1, hair='#3a2a4a', hair_style='mohawk', belly='#9a8aa8', cloth='#6a4a3a', cloth2='#8a6a4a', pants='#4a3a2a', boots='#3a2a1a', weapon='club', wlen=14, wang=-.9, eye='#ffd040', eye_hi=0, head=7.6, torso=6.6, torso_h=6.4, leg=6.4, bulk=3.0, pads=1, scar=1, belt=1, tunic=1),
 'ogro_deserto': dict(skin='#b09a58', tusks=1, horns=1, turban='#8a3a2a', belly='#c8b878', cloth='#8a5a30', cloth2='#6a3a20', pants='#4a3a2a', boots='#3a2a20', weapon='axe', wlen=13, wang=-.9, eye='#a02a10', eye_hi=0, head=8.0, torso=6.4, torso_h=6.0, leg=6.0, bulk=2.4, scar=1, belt=1, tunic=1, strap=1, strap_c='#5a2a18'),
})
for k, S in SPECS.items(): S.setdefault('has_cape', 1)


def anim(spec, k, view, dense=2):
    S = SPECS[spec] if isinstance(spec, str) else spec
    n = {'idle': 6, 'walk': 8, 'attack': 10, 'hurt': 4, 'death': 6}[k] * dense; out = []
    for i in range(n):
        u = i / max(1, n - 1); ph = 2 * math.pi * i / n
        if k == 'idle': im = draw(S, view, 0, bob=1 if math.sin(ph) > .5 else 0)
        elif k == 'walk': im = draw(S, view, ph, bob=-1 if abs(math.sin(ph * 2)) > .8 else 0)
        elif k == 'attack':
            lunge = int(round(-3 * math.sin(u / .3 * math.pi / 2))) if u < .3 else int(round(8 * math.sin((u - .3) / .7 * math.pi)))
            im = draw(S, view, 0, lunge=lunge, mouth=1 if .4 < u < .75 else 0, head_dy=-1 if .4 < u < .8 else 0)
        elif k == 'hurt': im = draw(S, view, 0, lunge=-int(round(3 * math.sin(u * math.pi))), squint=True, mouth=1, head_dy=-1)
        else:
            im = draw(S, view, 0, lunge=-3, squint=True, mouth=1)
            if u > .3:
                a = np.array(im); t = min(1, (u - .3) / .5)
                im = Image.fromarray(a).rotate(-80 * t, resample=Image.NEAREST, center=(W // 2, BASE))
                bb = im.getbbox(); im2 = Image.new('RGBA', (W, H), (0, 0, 0, 0))
                if bb: im2.alpha_composite(im, (0, BASE - bb[3] + 1))
                im = im2
        out.append((im, None, False))
    return out


if __name__ == '__main__':
    import sys
    ks = sys.argv[1:] or list(SPECS)
    S = Image.new('RGBA', (72 * 4 * len(ks), 64 * 4 * 2), (52, 70, 52, 255))
    for i, k in enumerate(ks):
        for j, v in enumerate(('right', 'down')):
            S.alpha_composite(draw(SPECS[k], v, .6).resize((72 * 4, 64 * 4), Image.NEAREST), (i * 72 * 4, j * 64 * 4))
    S.save('/tmp/humano.png'); print(S.size)
