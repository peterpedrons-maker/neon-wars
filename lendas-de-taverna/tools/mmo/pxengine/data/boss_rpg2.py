#!/usr/bin/env python3
"""Rei Esquecido (chibi, mesmo sistema do heroi) no formato real do jogo: anda ate o heroi, ataca corpo a corpo, usa as 5 habilidades,
leva dano e morre. Saida: rei_rpg2.gif / rei_rpg2_folha.png / rei_animacoes.png"""
import math, os, random
from PIL import Image, ImageDraw
import chibi as C
import boss_rpg as B
from boss_rpg import bg, paste_feet, tint, shadow, disc, ring, telegraph, flip, NW, NH, SC
from equip_gallery import label
from teste_clareira import OUT

REI_APP = dict(cls='rei', weapon='espada_rei')
REI = {k: {v: [f[0] for f in C.anim(v, k, 'rei', None, REI_APP)] for v in ('down', 'up', 'right')} for k in ('idle', 'walk', 'attack', 'cast', 'hurt', 'death')}


class S(B.St):
    def __init__(s):
        super().__init__()
        s.bx, s.by = 66.0, 112.0; s.bview = 'down'; s.bkind = 'idle'; s.bi = 0; s.balpha = 255; s.victory = False


def rei_img(st, f):
    v = st.bview; vv = 'right' if v in ('left', 'right') else v
    seq = REI[st.bkind][vv]; img = seq[st.bi % len(seq)]
    if v == 'left': img = flip(img)
    if st.bflash > 0 and st.bflash % 2: img = tint(img, (255, 255, 255), .6)
    if st.balpha < 255:
        a = img.split()[3].point(lambda x: int(x * st.balpha / 255)); img = img.copy(); img.putalpha(a)
    return img


def frame(f, st, back=None, front=None, channel=None, extra=None):
    B.BOSS_FEET = (int(st.bx), int(st.by))
    im = bg(f)
    shadow(im, st.hx, st.hy + 1, 11, 3); shadow(im, st.bx, st.by + 1, 13, 4, 110 if st.balpha > 100 else 40)
    if back: back(im)
    if extra: extra(im)
    paste_feet(im, rei_img(st, f), (st.bx, st.by))
    # heroi e chefe: quem esta mais abaixo na tela fica na frente
    paste_feet(im, B.hero_sprite(st, f), (st.hx, st.hy))
    if front: front(im)
    if st.dark > 0:
        ov = Image.new('RGBA', (NW, NH), (4, 2, 12, 255)); m = Image.new('L', (NW, NH), int(238 * st.dark)); d = ImageDraw.Draw(m)
        for k in range(5):
            rr = 18 + k * 9
            d.ellipse([st.hx - rr, st.hy - 16 - rr * .8, st.hx + rr, st.hy - 16 + rr * .8], fill=int(238 * st.dark * (k + 1) / 5.5) if k > 0 else 0)
        ov.putalpha(m); im.alpha_composite(ov)
        d2 = ImageDraw.Draw(im)
        for sgn in (-1, 1): d2.rectangle([int(st.bx) + sgn * 3 - 1, int(st.by) - 26, int(st.bx) + sgn * 3, int(st.by) - 25], fill=(190, 90, 255))
    B.hud(im, st, channel)
    if st.victory: label(im, (NW // 2, 120), 'VITORIA!', (255, 230, 120), center=True)
    if st.shake != (0, 0):
        sh = Image.new('RGBA', (NW, NH), (0, 0, 0, 255)); sh.alpha_composite(im, st.shake); im = sh
    return im


def run():
    random.seed(5); frames = []; st = S(); fi = [0]

    def emit(**kw):
        frames.append(frame(fi[0], st, **kw)); fi[0] += 1
        if st.hurt > 0: st.hurt -= 1
        if st.bflash > 0: st.bflash -= 1
        st.shake = (0, 0)

    def boss(kind, i=None, view=None):
        st.bkind = kind
        if view: st.bview = view
        if i is not None: st.bi = i

    def hero_walk(tx, ty, steps, **kw):
        sx, sy = st.hx, st.hy; dx, dy = tx - sx, ty - sy
        st.moving = True; st.view = 'right' if dx > 4 else ('left' if dx < -4 else ('up' if dy < 0 else 'down'))
        for i in range(steps):
            u = (i + 1) / steps; st.hx = sx + dx * u; st.hy = sy + dy * u; st.wf += 1; st.bi += 1 if st.bkind == 'idle' else 0
            emit(**kw)
        st.moving = False; st.view = 'up'

    def boss_walk(tx, ty, steps, **kw):
        sx, sy = st.bx, st.by; dx, dy = tx - sx, ty - sy
        st.bview = 'right' if dx > 6 else ('left' if dx < -6 else ('down' if dy > 0 else 'up')); boss('walk')
        for i in range(steps):
            u = (i + 1) / steps; st.bx = sx + dx * u; st.by = sy + dy * u; st.bi = i
            emit(**kw)
        boss('idle', 0, 'down')

    def idle(n):
        boss('idle')
        for i in range(n): st.bi = i; emit()

    def hero_attack():
        st.view = 'up'
        for k in (1, 2, 3, 4, 5, 6, 7, 8):
            st.atk = k
            if k == 5: st.bflash = 3
            emit()
        st.atk = None

    def msg(t): st.msgs.append(t)

    def cast(name, n=10):
        boss('cast')
        for i in range(n):
            st.bi = min(7, int(i / n * 8)); emit(channel=(name, (i + 1) / n))
        st.bi = 4

    # ---- intro: heroi entra, Rei anda ate ele ----
    st.hx, st.hy = 50, 244; idle(4)
    hero_walk(58, 214, 8)
    boss_walk(62, 170, 14)
    # ---- ataque corpo a corpo do Rei ----
    msg('[Aviso] Golpe do Rei!'); boss('attack', 0, 'down')
    for i in range(10):
        st.bi = i
        if i == 6: st.hurt = 5; st.hp = max(.5, st.hp - .12); st.shake = (1, 1); st.hx -= 3
        emit(front=(lambda im, i=i: label(im, (int(st.hx) + 2, int(st.hy) - 40), '57', (255, 224, 74), center=True) if st.hurt else None))
    idle(2)
    hero_walk(52, 208, 6)
    # ---- heroi contra-ataca; Rei reage ----
    st.hx, st.hy = 56, 204
    hero_attack(); st.bhp = .85; boss('hurt', 0, 'down')
    for i in range(4): st.bi = i; emit(front=(lambda im: label(im, (int(st.bx) + 6, int(st.by) - 44), '34', (255, 224, 74), center=True) if True else None))
    idle(2)
    hero_walk(50, 236, 8)
    # ---- 5 habilidades ----
    def go_center():
        boss_walk(66, 118, 10)

    # 1 Esquecimento
    go_center(); msg('[Aviso] Esquecimento!'); cast('Esquecimento')
    for i in range(18):
        t = i / 17
        def back(im, t=t):
            ov = Image.new('RGBA', (NW, NH), (0, 0, 0, 0))
            for k in range(4):
                rr = 6 + t * 120 - k * 11
                if rr > 0: ring(ov, st.bx, st.by, rr, rr * .5, (150 + k * 20, 70, 220), 230 - k * 40, 2)
            for j in range(28):
                a = j * .23 + t * 4; r_ = t * 110 * (.4 + (j % 6) / 7); disc(ov, st.bx + math.cos(a) * r_, st.by + math.sin(a) * r_ * .5, 1, (120, 60, 200), 150)
            im.alpha_composite(ov)
        if t > .7 and st.forgot == 0: st.forgot = .2; st.tint = ((150, 130, 200), .45)
        if t > .9: st.forgot = 1.0
        st.bi = 4; emit(back=back)
    idle(8); st.tint = None; st.forgot = 0
    # 2 Eco
    msg('[Aviso] Eco!'); cast('Eco', 9)
    for i in range(26):
        def extra(im, i=i):
            if i > 2:
                for dx_ in (-38, 38):
                    g = REI['cast']['down'][4]; a = g.split()[3].point(lambda v: 105 if v else 0)
                    g2 = tint(g, (120, 200, 255), .6); g2.putalpha(a); paste_feet(im, g2, (st.bx + dx_, st.by + 4))
        def front(im, i=i):
            ov = Image.new('RGBA', (NW, NH), (0, 0, 0, 0))
            for n_, (sx, t0) in enumerate(((st.bx - 38, 6), (st.bx + 38, 9), (st.bx, 12))):
                if i >= t0:
                    u = min(1, (i - t0) / 7.0); sy = st.by - 16
                    x = sx + (st.hx - sx) * u; y = sy + (st.hy - 16 - sy) * u
                    for tr in range(1, 5): disc(ov, x - (st.hx - sx) * .04 * tr, y - (st.hy - 16 - sy) * .04 * tr, 3 - tr // 2, (150, 70, 230), 130 - tr * 25)
                    disc(ov, x, y, 4, (180, 90, 255), 235); disc(ov, x, y, 2, (255, 255, 255), 255)
                    if u >= 1 and i - t0 == 7: st.hurt = 5; st.hp = max(.3, st.hp - .06)
            im.alpha_composite(ov)
            if st.hurt: label(im, (int(st.hx) + 4, int(st.hy) - 44 - (5 - st.hurt) * 2), str(41 + i), (255, 224, 74), center=True)
        st.bi = 4; emit(front=front, extra=extra)
    idle(6)
    # 3 Fenda do Vazio (heroi desvia)
    msg('[Aviso] Fenda do Vazio!'); cast('Fenda do Vazio', 10)
    spot = (st.hx, st.hy)
    for i in range(30):
        def back(im, i=i, spot=spot):
            ov = Image.new('RGBA', (NW, NH), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
            if i < 11: telegraph(ov, spot[0], spot[1] + 2, 20 + 2 * math.sin(i * 1.4), 1.0 if i > 4 else i / 5)
            elif i < 25:
                k = min(1, (i - 11) / 3.0) if i < 22 else max(0, (25 - i) / 3.0); rx, ry = 22 * k, 11 * k
                d.ellipse([spot[0] - rx - 2, spot[1] - ry - 1, spot[0] + rx + 2, spot[1] + ry + 1], fill=(190, 90, 255, 255))
                d.ellipse([spot[0] - rx, spot[1] - ry, spot[0] + rx, spot[1] + ry], fill=(6, 2, 14, 255))
                for c_ in range(6):
                    a_ = c_ * 1.1 + .3; d.line([spot[0], spot[1], spot[0] + math.cos(a_) * (rx + 14) * k, spot[1] + math.sin(a_) * (ry + 7) * k], fill=(150, 70, 220, 255))
                for j in range(16):
                    a_ = j * .45 + i * .4; r_ = max(2, 40 - ((i * 3 + j * 4) % 40)); disc(ov, spot[0] + math.cos(a_) * r_, spot[1] + math.sin(a_) * r_ * .5, 1, (210, 150, 255), 220)
            im.alpha_composite(ov)
        if i == 4: st.moving = True; st.view = 'right'
        if 4 <= i <= 12:
            st.hx = spot[0] + (i - 4) * 4.5; st.wf += 1
            if i == 12: st.moving = False; st.view = 'up'
        if i == 14: st.shake = (1, 1)
        st.bi = 4 if i < 14 else 5; emit(back=back)
    idle(4)
    # 4 Coroa de Almas
    msg('[Aviso] Coroa de Almas!'); cast('Coroa de Almas', 10)
    for n_ in range(5): setattr(st, 'h%d' % n_, 0)
    for i in range(28):
        def front(im, i=i):
            ov = Image.new('RGBA', (NW, NH), (0, 0, 0, 0)); cx0, cy0 = st.bx, st.by - 38
            for n_ in range(5):
                a_ = n_ * 2 * math.pi / 5 + i * .35
                if i < 12: r_ = 11 + 1.4 * i; x = cx0 + math.cos(a_) * r_; y = cy0 + math.sin(a_) * r_ * .45
                else:
                    u = max(0, min(1, (i - 12 - n_ * 1.5) / 8)); x0 = cx0 + math.cos(a_) * 26; y0 = cy0 + math.sin(a_) * 11
                    mx = (x0 + st.hx) / 2 + (n_ - 2) * 8; my = (y0 + st.hy) / 2
                    x = (1 - u) ** 2 * x0 + 2 * (1 - u) * u * mx + u * u * st.hx; y = (1 - u) ** 2 * y0 + 2 * (1 - u) * u * my + u * u * (st.hy - 16)
                    if u >= 1 and not getattr(st, 'h%d' % n_): setattr(st, 'h%d' % n_, 1); st.hurt = 4; st.hp = max(.15, st.hp - .04)
                    if u >= 1: continue
                for tr in range(1, 4): disc(ov, x - tr * 2, y + tr, 3 - tr // 2, (80, 170, 255), 120 - tr * 30)
                disc(ov, x, y, 4, (90, 190, 255), 230); disc(ov, x, y, 2, (255, 255, 255), 255)
            im.alpha_composite(ov)
            if st.hurt: label(im, (int(st.hx) + 3, int(st.hy) - 44 - (4 - st.hurt) * 2), '31', (160, 220, 255), center=True)
        st.bi = 4; emit(front=front)
    idle(5)
    # 5 Trevas
    msg('[Aviso] Trevas!'); cast('Trevas', 10)
    for i in range(32):
        st.dark = (i / 8 * .9) if i < 8 else (.9 if i < 24 else max(0, .9 - (i - 24) / 8 * .9))
        def back(im, i=i):
            ov = Image.new('RGBA', (NW, NH), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
            if 6 <= i <= 26:
                for k in range(7):
                    pts = []
                    for s_ in range(0, 22):
                        u = s_ / 21; x = st.bx + (st.hx - st.bx) * u; y = st.by + (st.hy - st.by) * u + math.sin(u * 9 + i * .6 + k) * (3 + k % 3); pts.append((x + (k - 3) * 2, y))
                    n = max(2, int(len(pts) * min(1, (i - 6) / 9))); d.line(pts[:n], fill=(14, 6, 34, 235), width=2); d.line(pts[:n], fill=(120, 60, 200, 170), width=1)
            im.alpha_composite(ov)
        if i == 18: st.hurt = 6; st.hp = max(.15, st.hp - .1); st.shake = (1, 0)
        def front(im, i=i):
            if st.hurt: label(im, (int(st.hx) + 3, int(st.hy) - 44 - (6 - st.hurt) * 2), '64', (200, 150, 255), center=True)
        st.bi = 4; emit(back=back, front=front)
    st.dark = 0; idle(6)
    # ---- final: heroi derrota o Rei ----
    boss_walk(64, 150, 10)
    hero_walk(58, 186, 10)
    for rep in range(2):
        hero_attack(); st.bhp = max(.0, st.bhp - .35); boss('hurt', 0, 'down')
        for i in range(4): st.bi = i; emit(front=(lambda im: label(im, (int(st.bx) + 6, int(st.by) - 44), '120', (255, 200, 60), center=True)))
        idle(1)
    st.bhp = 0; boss('death', 0, 'down')
    for i in range(6): st.bi = i; emit()
    for i in range(10): st.balpha = int(255 * (1 - (i + 1) / 10)); st.bi = 5; emit()
    st.victory = True
    for i in range(14): emit()
    big = [f.convert('RGB').resize((NW * SC, NH * SC), Image.NEAREST) for f in frames]
    p = big[0].quantize(colors=240, method=Image.MEDIANCUT, dither=Image.NONE)
    q = [b.quantize(palette=p, dither=Image.NONE) for b in big]
    q[0].save(os.path.join(OUT, 'rei_rpg2.gif'), save_all=True, append_images=q[1:], duration=85, loop=0, disposal=1)
    return len(q), big


def sheet():
    rows = [('idle', 6), ('walk', 8), ('attack', 10), ('cast', 8), ('hurt', 4), ('death', 6)]
    Wc = C.W; Hc = C.H
    A = Image.new('RGBA', (Wc * 10, Hc * 3 * len(rows) // 1), (52, 44, 72, 255)); y = 0
    for k, n in rows:
        for vi, v in enumerate(('down', 'up', 'right')):
            for i in range(n): A.alpha_composite(REI[k][v][i].crop((0, 0, Wc, Hc)), (i * Wc, (vi + 3 * rows.index((k, n))) * Hc))
    A = A.resize((A.width * 2, A.height * 2), Image.NEAREST).convert('RGB'); A.save(os.path.join(OUT, 'rei_animacoes.png'))


if __name__ == '__main__':
    sheet()
    n, big = run(); print(n)
    N_ = len(big); sel = [big[min(N_ - 1, int(N_ * q))] for q in (.03, .09, .13, .18, .24, .3, .4, .5, .6, .7, .85, .97)]
    sh = Image.new('RGB', (NW * SC // 2 * 6, NH * SC // 2 * 2))
    for i, b in enumerate(sel): sh.paste(b.resize((NW * SC // 2, NH * SC // 2), Image.NEAREST), ((i % 6) * NW * SC // 2, (i // 6) * NH * SC // 2))
    sh.save(os.path.join(OUT, 'rei_rpg2_folha.png'))
