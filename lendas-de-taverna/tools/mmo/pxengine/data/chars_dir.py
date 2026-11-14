#!/usr/bin/env python3
"""Personagens em 4 direcoes (down/up/right/left) com passo em salto (estilo miniatura).
Poses de cada direcao: idle, crouch, hop, land.  Esquerda = espelho da direita.
Rode: python3 chars_dir.py  -> mmo/proto_pixel/direcoes.png"""
import math
from PIL import Image, ImageDraw
from teste_clareira import (C, blob, outline, limb, sword, hero2, line, bay, INK, BROWN, OUT,
                            ORG, HAIRR, SKIN, SCARF, PANTS, STEEL)
import teste_rei as R
import os

POSE = {'idle': (0, 0), 'crouch': (2, 0), 'hop': (-5, 1), 'land': (2, 0)}  # (dy, tuck)
G = [C(c) for c in ['#2c5a1c', '#4a8a2a', '#78b83c', '#a8dc5a', '#d4f08a']]


def flip(img):
    return img.transpose(Image.FLIP_LEFT_RIGHT)


# ------------------------------------------------------------------ HEROI
def hero_dir(face, pose='idle', t=0):
    if face == 'left':
        return flip(hero_dir('right', pose, t))
    dy, tuck = POSE[pose]
    if pose == 'idle': dy = t
    cx = 20
    if face == 'down':
        src = hero2({'idle': 'idle', 'crouch': 'land', 'hop': 'hop', 'land': 'land'}[pose], t)
        out = Image.new('RGBA', (40, 46), (0, 0, 0, 0)); out.paste(src.crop((0, 0, 38, 46)), (2, 0)); return out
    img = Image.new('RGBA', (40, 46), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    if face == 'up':
        for lx in (cx - 4, cx + 4):
            blob(img, lx, 37 - 3 * tuck + (1 if pose in ('crouch', 'land') else 0), 2.8, 4.6, PANTS, flat=.9, jit=.03)
            blob(img, lx, 41 - 3 * tuck, 3.4, 2.3, BROWN, flat=.6, jit=.03)
        limb(img, (cx - 8, 26 + dy), (cx - 9, 32 + dy), 2.4, 2.0, ORG); blob(img, cx - 9, 33 + dy, 1.9, 1.9, SKIN, edge=False)
        blob(img, cx, 30 + dy, 7.6, 8, ORG, flat=.85, jit=.04)
        blob(img, cx, 29 + dy, 5, 4.5, BROWN, jit=.05)                       # mochila
        d.rectangle([cx - 4, 27 + dy, cx + 4, 27 + dy], fill=BROWN[3])
        d.rectangle([cx - 7, 33 + dy, cx + 7, 33 + dy], fill=BROWN[1])
        blob(img, cx, 23 + dy, 7.8, 3.2, SCARF, flat=.95, jit=.03)
        d.rectangle([cx + 1, 25 + dy, cx + 3, 33 + dy], fill=SCARF[1]); d.rectangle([cx + 1, 25 + dy, cx + 1, 33 + dy], fill=SCARF[2])
        blob(img, cx, 14 + dy, 8.4, 7.6, SKIN, flat=.95, jit=.03)
        blob(img, cx, 12.5 + dy, 9.4, 8.6, HAIRR, flat=.9, jit=.08, seed=6)
        for x, y0, y1 in [(cx - 4, 9, 17), (cx - 1, 8, 18), (cx + 2, 9, 17), (cx + 5, 10, 16)]:
            d.line([x, y0 + dy, x, y1 + dy], fill=HAIRR[1])
        d.point([cx - 3, 8 + dy], fill=HAIRR[4]); d.point([cx - 2, 8 + dy], fill=HAIRR[4])
        sh = (cx + 7, 26 + dy); hand = (cx + 9, 33 + dy)
        limb(img, sh, hand, 2.5, 2.1, ORG)
        sword(img, hand, 78, 15, 1.5, .5, STEEL, 7)
        blob(img, hand[0], hand[1], 2.0, 2.0, SKIN, edge=False)
        return outline(img, INK)
    # ---- direita (perfil)
    leg_off = [(-3, 3), (-2, 2), (-3, 3), (-3, 3)][list(POSE).index(pose)] if pose != 'hop' else (-1, 2)
    for k, lx in enumerate((cx + leg_off[0], cx + leg_off[1])):
        blob(img, lx, 37 - 3 * tuck + (1 if pose in ('crouch', 'land') else 0), 2.8, 4.6, PANTS, flat=.9, jit=.03)
        blob(img, lx + 1, 41 - 3 * tuck, 3.6, 2.3, BROWN, flat=.6, jit=.03)
    limb(img, (cx - 1, 26 + dy), (cx - 3, 32 + dy), 2.3, 1.9, ORG)               # braco de tras
    blob(img, cx - 3, 33 + dy, 1.8, 1.8, SKIN, edge=False)
    blob(img, cx, 30 + dy, 5.8, 8, ORG, flat=.85, jit=.04)
    d.rectangle([cx - 5, 33 + dy, cx + 5, 33 + dy], fill=BROWN[1]); d.rectangle([cx + 3, 33 + dy, cx + 5, 34 + dy], fill=C('#ffd05a'))
    blob(img, cx, 23 + dy, 6.4, 3.2, SCARF, flat=.95, jit=.03)
    fl = [(0, 0), (1, 1), (2, 1), (1, 0)][(t if pose == 'idle' else 2)]
    for k in range(6):
        d.rectangle([cx - 6 - k, 23 + dy + k // 3 + (fl[1] if k > 1 else 0), cx - 5 - k, 24 + dy + k // 3 + (fl[1] if k > 1 else 0)], fill=SCARF[2 if k < 3 else 1])
    hx = cx + 1
    blob(img, hx, 14 + dy, 7.4, 7.6, SKIN, flat=.95, jit=.03)
    d.rectangle([hx + 7, 15 + dy, hx + 8, 16 + dy], fill=SKIN[2]); d.point([hx + 8, 17 + dy], fill=SKIN[1])  # nariz
    blob(img, hx - 1.5, 9.5 + dy, 8.8, 6.8, HAIRR, flat=.2, jit=.1, seed=4)
    blob(img, hx - 6, 15 + dy, 3.2, 5.4, HAIRR, flat=.95, jit=.06, seed=5)
    for x in range(hx - 2, hx + 7):
        if x % 3 != 1: d.point([x, 12 + dy], fill=HAIRR[2 if x % 2 else 1])
    d.rectangle([hx + 3, 15 + dy, hx + 4, 17 + dy], fill=INK); d.point([hx + 3, 15 + dy], fill=C('#8a6aa8'))
    d.point([hx + 2, 18 + dy], fill=C('#f08a8a')); d.point([hx + 5, 19 + dy], fill=SKIN[0])
    sh = (cx + 1, 26 + dy); hand = (cx + 7, 32 + dy)
    limb(img, sh, hand, 2.5, 2.1, ORG)
    sword(img, hand, 52, 15, 1.5, .5, STEEL, 7)
    blob(img, hand[0], hand[1], 2.0, 2.0, SKIN, edge=False)
    return outline(img, INK)


# ------------------------------------------------------------------ GOBLIN
def goblin_dir(face, pose='idle', t=0):
    if face == 'left':
        return flip(goblin_dir('right', pose, t))
    dy, tuck = POSE[pose]
    if pose == 'idle': dy = t
    cx = 20
    img = Image.new('RGBA', (40, 38), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    b = dy
    if face in ('down', 'up'):
        for lx in (cx - 5, cx + 2):
            d.rectangle([lx, 29 - 2 * tuck, lx + 1, 32 - 2 * tuck + (1 if pose in ('crouch', 'land') else 0)], fill=G[1])
            d.rectangle([lx - 1, 32 - 2 * tuck, lx + 2, 32 - 2 * tuck], fill=BROWN[1])
        d.rectangle([cx - 5, 20 + b, cx + 4, 28], fill=G[2]); d.rectangle([cx - 5, 20 + b, cx - 4, 28], fill=G[3]); d.rectangle([cx + 3, 20 + b, cx + 4, 28], fill=G[1])
        d.rectangle([cx - 5, 25, cx + 4, 29 - tuck], fill=BROWN[2]); d.rectangle([cx + 3, 25, cx + 4, 29 - tuck], fill=BROWN[1]); d.rectangle([cx - 5, 25, cx + 4, 25], fill=BROWN[3])
        d.rectangle([cx - 6, 9 + b, cx + 5, 19 + b], fill=G[2] if face == 'down' else G[1])
        d.rectangle([cx - 6, 9 + b, cx - 4, 19 + b], fill=G[3] if face == 'down' else G[2]); d.rectangle([cx + 3, 10 + b, cx + 5, 19 + b], fill=G[1])
        d.rectangle([cx - 6, 19 + b, cx + 5, 19 + b], fill=G[0])
        line(d, (cx - 7, 13 + b), (cx - 13, 10 + b), G[2], 2); line(d, (cx + 6, 13 + b), (cx + 12, 10 + b), G[1], 2)
        if face == 'down':
            d.rectangle([cx - 4, 13 + b, cx - 2, 14 + b], fill=C('#ffe04a')); d.rectangle([cx + 1, 13 + b, cx + 3, 14 + b], fill=C('#ffe04a'))
            d.point([cx - 3, 14 + b], fill=INK); d.point([cx + 2, 14 + b], fill=INK)
            d.rectangle([cx - 4, 12 + b, cx - 2, 12 + b], fill=G[0]); d.rectangle([cx + 1, 12 + b, cx + 3, 12 + b], fill=G[0])
            d.rectangle([cx - 3, 17 + b, cx + 2, 17 + b], fill=G[0]); d.point([cx - 2, 17 + b], fill=C('#ffffff')); d.point([cx + 1, 17 + b], fill=C('#ffffff'))
        else:
            for k in range(3): d.point([cx - 1 + (k % 2), 12 + b + k * 2], fill=G[0])      # coluna / nuca
            d.rectangle([cx - 5, 16 + b, cx + 4, 16 + b], fill=G[0])
            for yy in (22, 25): d.point([cx, yy + b], fill=G[1])
        d.rectangle([cx - 8, 21 + b, cx - 6, 26 + b], fill=G[2]); d.rectangle([cx + 5, 21 + b, cx + 7, 26 + b], fill=G[1])
        ct = (cx + 11, 12 + b) if face == 'down' else (cx + 10, 8 + b)
        line(d, (cx + 7, 25 + b), ct, BROWN[2], 2)
    else:  # direita
        for k, lx in enumerate((cx - 4 + (0 if pose != 'hop' else 1), cx + 1)):
            d.rectangle([lx, 29 - 2 * tuck, lx + 1, 32 - 2 * tuck + (1 if pose in ('crouch', 'land') else 0)], fill=G[1])
            d.rectangle([lx - 1, 32 - 2 * tuck, lx + 3, 32 - 2 * tuck], fill=BROWN[1])
        d.rectangle([cx - 4, 20 + b, cx + 3, 28], fill=G[2]); d.rectangle([cx - 4, 20 + b, cx - 3, 28], fill=G[1]); d.rectangle([cx + 2, 20 + b, cx + 3, 28], fill=G[3])
        d.rectangle([cx - 4, 25, cx + 3, 29 - tuck], fill=BROWN[2]); d.rectangle([cx - 4, 25, cx + 3, 25], fill=BROWN[3])
        d.rectangle([cx - 5, 9 + b, cx + 4, 19 + b], fill=G[2]); d.rectangle([cx - 5, 9 + b, cx - 3, 19 + b], fill=G[1]); d.rectangle([cx + 3, 10 + b, cx + 4, 19 + b], fill=G[3])
        d.rectangle([cx - 5, 19 + b, cx + 4, 19 + b], fill=G[0])
        d.rectangle([cx + 5, 13 + b, cx + 8, 16 + b], fill=G[3]); d.rectangle([cx + 5, 16 + b, cx + 8, 16 + b], fill=G[1])   # nariz
        line(d, (cx - 5, 13 + b), (cx - 12, 9 + b), G[1], 2)                                                                 # orelha
        d.rectangle([cx + 1, 12 + b, cx + 3, 14 + b], fill=C('#ffe04a')); d.point([cx + 3, 13 + b], fill=INK); d.rectangle([cx + 1, 11 + b, cx + 3, 11 + b], fill=G[0])
        d.rectangle([cx + 1, 17 + b, cx + 4, 17 + b], fill=G[0]); d.point([cx + 3, 17 + b], fill=C('#ffffff'))
        d.rectangle([cx - 1, 21 + b, cx + 2, 26 + b], fill=G[2])
        ct = (cx + 11, 24 + b)
        line(d, (cx + 3, 25 + b), ct, BROWN[2], 2)
    d.rectangle([ct[0] - 2, ct[1] - 2, ct[0] + 2, ct[1] + 2], fill=BROWN[3])
    d.point([ct[0] + 1, ct[1] + 1], fill=BROWN[1]); d.point([ct[0] - 1, ct[1] - 1], fill=C('#d8d8e8'))
    return outline(img, INK)


# ------------------------------------------------------------------ REI ESQUECIDO
def rei_dir(face, pose='idle', f=0):
    if face == 'left':
        s, c, t, h = rei_dir('right', pose, f)
        return flip(s), (128 - c[0], c[1]), t, h
    dy0, tuck = POSE[pose]
    dy = round(dy0 * .6) if pose != 'idle' else round(math.sin(f * .9))
    P = dict(dy=dy, lean=0, hr=(86, 76), hl=(40, 78), sa=70, bow=0)
    if face == 'down':
        s, c, t, h = R.rei(P, f)
        return s, c, t, h
    img = Image.new('RGBA', (128, 124), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    cx = 64; AR, IR, BO, CP, IC, WI = R.ARM, R.IRON, R.BONE, R.CAPE, R.ICE, R.WISP
    side = face == 'right'
    sq = 1 if pose in ('crouch', 'land') else 0

    def cape(width_top, off, bottom_jit, front=False):
        top = 54 + dy
        pts = [(cx - width_top + off, top), (cx + width_top + off, top)]
        for i in range(12, -1, -1):
            x = cx + off - (40 if not side else 40) + i * (6.7 if not side else 4.4) + math.sin(f * .5 + i * .9) * 2.2
            y = 111 - ((i * 37) % 9) + math.sin(f * .4 + i) * 1.5
            pts.append((x, y))
        m = Image.new('L', img.size, 0); ImageDraw.Draw(m).polygon(pts, fill=255)
        mp = m.load(); px = img.load()
        for y in range(top, 118):
            for x in range(6, 122):
                if mp[x, y]:
                    fold = math.sin((x - cx) * .42 + math.sin(y * .1) * 1.5)
                    l = .45 + .3 * fold - abs(x - cx - off) / 90 + bay(x, y) * .2
                    if front: l += .06
                    px[x, y] = CP[3 if l > .62 else 2 if l > .34 else 1 if l > .08 else 0]
    if face == 'up':
        # pernas, saia, torso, ombreiras, depois a capa NA FRENTE (vista de costas)
        for lx in (cx - 8, cx + 8):
            blob(img, lx, 99 - 3 * tuck + sq, 6, 10, AR, flat=.92, jit=.03)
            blob(img, lx, 111 - 3 * tuck, 7.5, 3.2, IR, flat=.7, jit=.03)
        blob(img, cx, 88 + dy * .5, 18, 7, AR, flat=.8, jit=.04)
        blob(img, cx, 70 + dy, 18, 19, AR, flat=.9, jit=.03)
        for sx in (-1, 1):
            px_ = cx + sx * 21
            blob(img, px_, 57 + dy, 11, 7.5, IR, flat=.9, jit=.05)
            for ox, h, w in [(sx * 5, 12, 3), (sx * 10, 7, 2)]:
                R.tri(d, [(px_ + ox - w, 54 + dy), (px_ + ox + w, 54 + dy), (px_ + ox + sx * 3, 54 + dy - h)], IR)
        cape(23, 0, 0)
        blob(img, cx, 51 + dy, 9, 4, AR, flat=.9, jit=.03)
        hy = 40 + dy
        blob(img, cx, hy, 8.6, 9.2, AR, flat=.9, jit=.03)                 # elmo visto de tras
        blob(img, cx, hy - 2, 7, 6, IR, flat=.8, jit=.05)
        d.line([cx, hy - 8, cx, hy + 7], fill=AR[1])
        d.rectangle([cx - 8, hy - 8, cx + 8, hy - 6], fill=IR[2]); d.rectangle([cx - 8, hy - 6, cx + 8, hy - 6], fill=IR[1])
        for ox, h in [(-7, 9), (-3.5, 14), (0, 19), (3.5, 14), (7, 9)]:
            R.tri(d, [(cx + ox - 2, hy - 8), (cx + ox + 2, hy - 8), (cx + ox, hy - 8 - h)], IR)
            d.point([round(cx + ox), round(hy - 8 - h + 1)], fill=WI[3]); d.point([round(cx + ox), round(hy - 8 - h)], fill=WI[4])
        shR = (cx + 18, 58 + dy); shL = (cx - 18, 58 + dy)
        eL, hl = R.ik2(shL, (cx - 28, 80 + dy), 17, 17, -1)
        eR, hr = R.ik2(shR, (cx + 30, 76 + dy), 17, 17, +1)
        limb(img, shL, eL, 5.6, 5.0, AR); limb(img, eL, hl, 5.0, 4.2, AR); blob(img, hl[0], hl[1], 4.4, 4.4, IR, jit=.04)
        R.sword(img, hr, 80, 42, 3.2, .8, IC, 14, C('#7a4ac8'), C('#2a1a3a'))
        limb(img, shR, eR, 5.6, 5.0, AR); limb(img, eR, hr, 5.0, 4.2, AR); blob(img, hr[0], hr[1], 4.4, 4.4, IR, jit=.04)
        img = outline(img, R.BOSS_INK)
        return img, (cx, hy - 20), None, None
    # ---------------- perfil direito
    cape(11, -12, 0)
    legs = [(cx - 6, cx + 6), (cx - 4, cx + 4), (cx - 6, cx + 6), (cx - 6, cx + 6)][list(POSE).index(pose)] if pose != 'hop' else (cx - 3, cx + 5)
    for lx in legs:
        blob(img, lx, 99 - 3 * tuck + sq, 5.6, 10, AR, flat=.92, jit=.03)
        blob(img, lx + 2, 111 - 3 * tuck, 7.5, 3.2, IR, flat=.7, jit=.03)
    blob(img, cx, 88 + dy * .5, 13, 7, AR, flat=.8, jit=.04)
    # braco de tras
    shB = (cx - 2, 58 + dy)
    eB, hB = R.ik2(shB, (cx - 8, 82 + dy), 17, 17, -1)
    limb(img, shB, eB, 5.0, 4.6, AR); limb(img, eB, hB, 4.6, 3.8, AR); blob(img, hB[0], hB[1], 4.2, 4.2, IR, jit=.04)
    blob(img, cx, 70 + dy, 12.5, 19, AR, flat=.9, jit=.03)
    d.line([cx - 9, 66 + dy, cx + 9, 66 + dy], fill=AR[1]); d.line([cx - 9, 78 + dy, cx + 9, 78 + dy], fill=AR[1])
    d.polygon([(cx + 8, 64 + dy), (cx + 10, 68 + dy), (cx + 8, 72 + dy)], fill=WI[2])
    d.rectangle([cx - 12, 80 + dy, cx + 12, 81 + dy], fill=C('#5a3a84'))
    px_ = cx + 1
    blob(img, px_, 57 + dy, 10, 7.5, IR, flat=.9, jit=.05)
    for ox, h, w in [(-5, 11, 3), (3, 8, 2)]:
        R.tri(d, [(px_ + ox - w, 54 + dy), (px_ + ox + w, 54 + dy), (px_ + ox - 3, 54 + dy - h)], IR)
    blob(img, cx + 1, 51 + dy, 7, 4, AR, flat=.9, jit=.03)
    hy = 40 + dy; hx = cx + 2
    blob(img, hx, hy, 7.8, 9, BO, flat=.88, jit=.03)
    blob(img, hx + 4, hy + 7, 5, 3.6, BO, flat=.9, jit=.03)                # mandibula p/ frente
    d.rectangle([hx + 2, hy - 1, hx + 6, hy + 3], fill=C('#1a0a24')); d.rectangle([hx + 3, hy, hx + 5, hy + 2], fill=WI[3]); d.point([hx + 3, hy], fill=WI[4])
    d.polygon([(hx + 7, hy + 3), (hx + 9, hy + 5), (hx + 7, hy + 6)], fill=C('#1a0a24'))
    for k in range(0, 8): d.point([hx + 1 + k, hy + 10], fill=C('#1a0a24') if k % 2 else BO[3])
    blob(img, hx - 6, hy, 4, 7, AR, flat=.95, jit=.05)                     # nuca de ferro
    d.rectangle([hx - 8, hy - 8, hx + 8, hy - 6], fill=IR[2]); d.rectangle([hx - 8, hy - 6, hx + 8, hy - 6], fill=IR[1])
    for ox, h in [(-6, 9), (-2.5, 14), (1, 19), (4.5, 14), (7, 9)]:
        R.tri(d, [(hx + ox - 2, hy - 8), (hx + ox + 2, hy - 8), (hx + ox, hy - 8 - h)], IR)
        d.point([round(hx + ox), round(hy - 8 - h + 1)], fill=WI[3]); d.point([round(hx + ox), round(hy - 8 - h)], fill=WI[4])
    shN = (cx + 3, 58 + dy)
    eN, hN = R.ik2(shN, (cx + 22, 76 + dy), 17, 17, +1)
    tip = R.sword(img, hN, 44, 42, 3.2, .8, IC, 14, C('#7a4ac8'), C('#2a1a3a'))
    limb(img, shN, eN, 5.4, 4.8, AR); limb(img, eN, hN, 4.8, 4.2, AR); blob(img, eN[0], eN[1], 4.4, 3.8, IR, jit=.04)
    blob(img, hN[0], hN[1], 4.4, 4.4, IR, jit=.04)
    img = outline(img, R.BOSS_INK)
    return img, (hx, hy - 20), tip, hN


def sheet():
    faces = ['down', 'up', 'right', 'left']
    poses = ['idle', 'crouch', 'hop', 'land']
    out = []
    for name, fn, cw, ch, sc in [('heroi', hero_dir, 40, 46, 3), ('goblin', goblin_dir, 40, 38, 3)]:
        im = Image.new('RGBA', (cw * 4 * 4 + 4, ch + 4), (58, 110, 48, 255))
        for i, fc in enumerate(faces):
            for j, p in enumerate(poses):
                im.alpha_composite(fn(fc, p, 0), ((i * 4 + j) * cw + 2, 2))
        out.append(im.resize((im.width * sc, im.height * sc), Image.NEAREST))
    im = Image.new('RGBA', (128 * 4 * 2 + 4, 128), (50, 36, 70, 255))
    for i, fc in enumerate(faces):
        for j, p in enumerate(['idle', 'land']):
            im.alpha_composite(rei_dir(fc, p, 3)[0], ((i * 2 + j) * 128 + 2, 2))
    out.append(im.resize((im.width * 2, im.height * 2), Image.NEAREST))
    w = max(o.width for o in out)
    s = Image.new('RGB', (w, sum(o.height for o in out) + 12), (30, 30, 36))
    y = 0
    for o in out:
        s.paste(o.convert('RGB'), (0, y)); y += o.height + 6
    s.save(os.path.join(OUT, 'direcoes.png'))


if __name__ == '__main__':
    sheet(); print('ok')
