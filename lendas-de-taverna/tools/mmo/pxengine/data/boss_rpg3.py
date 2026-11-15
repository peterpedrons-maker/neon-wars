#!/usr/bin/env python3
"""Rei Esquecido v3: animacoes com o DOBRO de quadros (dense=2), expressoes de rosto e a habilidade de investida em 3 faixas com 2 copias.
Formato real do jogo (retrato). Saida: rei_rpg3.gif / rei_rpg3_folha.png / expressoes.png / rei_animacoes_dense.png"""
import math, os, random
from PIL import Image, ImageDraw
import chibi as C
import boss_rpg as B
from boss_rpg import bg, paste_feet, tint, shadow, disc, ring, telegraph, flip, NW, NH, SC
from equip_gallery import label
from teste_clareira import OUT

D = 2
HAPP = dict(cls='warrior', hat='helm', outfit='mail', metal='aco', clothes='aco', weapon='espada_aco')
REIAPP = dict(cls='rei', weapon='espada_rei')


def spr(app, cls, kinds):
    return {k: {v: [f[0] for f in C.anim(v, k, cls, None, app, dense=D)] for v in ('down', 'up', 'right')} for k in kinds}


HERO = spr(HAPP, 'warrior', ('idle', 'walk', 'attack', 'hurt'))
REI = spr(REIAPP, 'rei', ('idle', 'walk', 'attack', 'cast', 'hurt', 'death'))


class S(B.St):
    def __init__(s):
        super().__init__()
        s.bx, s.by = 66.0, 112.0; s.bview = 'down'; s.bkind = 'idle'; s.bi = 0; s.balpha = 255; s.victory = False
        s.hkind = 'idle'; s.hi = 0; s.clones = []; s.lanes = []; s.cracks = []; s.flags = set()

    def once(s, k):
        if k in s.flags: return False
        s.flags.add(k); return True


def pick(table, kind, view, i):
    vv = 'right' if view in ('left', 'right') else view
    seq = table[kind][vv]; img = seq[i % len(seq)]
    return flip(img) if view == 'left' else img


def rei_img(st):
    img = pick(REI, st.bkind, st.bview, st.bi)
    if st.bflash > 0 and st.bflash % 2: img = tint(img, (255, 255, 255), .6)
    if st.balpha < 255:
        a = img.split()[3].point(lambda x: int(x * st.balpha / 255)); img = img.copy(); img.putalpha(a)
    return img


def hero_img(st):
    img = pick(HERO, st.hkind, st.view, st.hi)
    if st.tint: img = tint(img, st.tint[0], st.tint[1])
    if st.hurt > 0 and st.hurt % 3 == 0: img = tint(img, (255, 255, 255), .8)
    return img


def frame(f, st, back=None, front=None, channel=None, extra=None):
    B.BOSS_FEET = (int(st.bx), int(st.by))
    im = bg(f // 2)
    # rachaduras do vazio (ficam no chao)
    if st.cracks:
        ov = Image.new('RGBA', (NW, NH), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
        for (x, y0, y1, a) in st.cracks:
            d.rectangle([x - 6, y0, x + 6, y1], fill=(8, 2, 16, int(a * .85)))
            for yy in range(int(y0), int(y1), 5):
                d.line([x - 6, yy, x - 3 + (yy % 3), yy + 4], fill=(190, 90, 255, a)); d.line([x + 6, yy + 2, x + 3 - (yy % 3), yy + 6], fill=(190, 90, 255, a))
            d.line([x, y0, x + 1, y1], fill=(120, 50, 200, a))
        im.alpha_composite(ov)
    if st.lanes:
        ov = Image.new('RGBA', (NW, NH), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
        for (x, ya, a) in st.lanes:
            d.rectangle([x - 9, ya, x + 9, 262], fill=(230, 40, 50, int(a * .30)))
            for yy in range(int(ya), 262, 6):
                d.line([x - 9, yy, x - 9, yy + 2], fill=(255, 80, 80, a)); d.line([x + 9, yy, x + 9, yy + 2], fill=(255, 80, 80, a))
            d.line([x - 9, 262, x + 9, 262], fill=(255, 190, 90, a))
        im.alpha_composite(ov)
    shadow(im, st.hx, st.hy + 1, 11, 3); shadow(im, st.bx, st.by + 1, 13, 4, 110 if st.balpha > 100 else 40)
    if back: back(im)
    if extra: extra(im)
    for (cx_, cy_, al, kind, idx, tr) in st.clones:        # copias do Rei (sombras)
        for k in range(tr, 0, -1):
            g = pick(REI, kind, 'down', idx); a = g.split()[3].point(lambda v, q=al * (1 - k / (tr + 1)) * .5: int(q) if v else 0)
            g2 = tint(g, (110, 40, 190), .7); g2.putalpha(a); paste_feet(im, g2, (cx_, cy_ - k * 7))
        g = pick(REI, kind, 'down', idx); a = g.split()[3].point(lambda v, q=al: int(q) if v else 0)
        g2 = tint(g, (70, 30, 130), .45); g2.putalpha(a); paste_feet(im, g2, (cx_, cy_))
    boss_first = st.by <= st.hy
    if boss_first: paste_feet(im, rei_img(st), (st.bx, st.by))
    paste_feet(im, hero_img(st), (st.hx, st.hy))
    if not boss_first: paste_feet(im, rei_img(st), (st.bx, st.by))
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

    def steps(n): return [k / 2 for k in range(n * 2)]       # quadros logicos x2 (fluidez)

    def boss(kind, i=0, view=None):
        st.bkind = kind; st.bi = i
        if view: st.bview = view

    def hero(kind, i=0): st.hkind = kind; st.hi = i

    def hero_walk(tx, ty, n, **kw):
        sx, sy = st.hx, st.hy; dx, dy = tx - sx, ty - sy
        st.view = 'right' if dx > 4 else ('left' if dx < -4 else ('up' if dy < 0 else 'down')); hero('walk')
        for k in range(n * 2):
            u = (k + 1) / (n * 2); st.hx = sx + dx * u; st.hy = sy + dy * u; st.hi = k; emit(**kw)
        st.view = 'up'; hero('idle')

    def boss_walk(tx, ty, n, **kw):
        sx, sy = st.bx, st.by; dx, dy = tx - sx, ty - sy
        st.bview = 'right' if dx > 6 else ('left' if dx < -6 else ('down' if dy > 0 else 'up')); boss('walk')
        for k in range(n * 2):
            u = (k + 1) / (n * 2); st.bx = sx + dx * u; st.by = sy + dy * u; st.bi = k; emit(**kw)
        boss('idle', 0, 'down')

    def idle(n):
        boss('idle'); hero('idle')
        for k in range(n * 2): st.bi = k; st.hi = k; emit()

    def hero_attack(hit_cb=None):
        st.view = 'up'; hero('attack')
        for k in range(len(HERO['attack']['up'])):
            st.hi = k
            if k == 10:
                st.bflash = 4
                if hit_cb: hit_cb()
            emit()
        hero('idle')

    def msg(t): st.msgs.append(t)

    def cast(name, n=10):
        boss('cast')
        L = len(REI['cast']['down'])
        for k in range(n * 2):
            st.bi = min(L - 1, int(k / (n * 2) * L)); st.hi = k; emit(channel=(name, (k + 1) / (n * 2)))
        st.bi = 6

    def hurt_hero(ms=12):
        st.hurt = ms; hero('hurt'); st.hi = 0

    # ---- intro ----
    st.hx, st.hy = 50, 244; idle(3)
    hero_walk(58, 214, 8)
    boss_walk(62, 170, 14)
    # ---- golpe corpo a corpo do Rei ----
    msg('[Aviso] Golpe do Rei!'); boss('attack', 0, 'down')
    L = len(REI['attack']['down'])
    for k in range(L):
        st.bi = k
        if k == 11: st.hp = max(.5, st.hp - .12); st.shake = (1, 1); hurt_hero(10)
        if st.hkind == 'hurt': st.hi = min(len(HERO['hurt']['up']) - 1, st.hi + 1)
        emit(front=(lambda im: label(im, (int(st.hx) + 2, int(st.hy) - 42), '57', (255, 224, 74), center=True) if st.hurt else None))
    hero('idle'); st.hurt = 0
    idle(2)
    hero_walk(52, 208, 5)
    # ---- contra-ataque ----
    st.hx, st.hy = 56, 204

    def hitb(): st.bhp = .85
    hero_attack(hitb); boss('hurt', 0, 'down')
    for k in range(len(REI['hurt']['down'])):
        st.bi = k; emit(front=(lambda im: label(im, (int(st.bx) + 6, int(st.by) - 46), '34', (255, 224, 74), center=True)))
    idle(2)
    hero_walk(49, 236, 8)

    def go_center(): boss_walk(66, 118, 10)

    # ===== 1 ESQUECIMENTO =====
    go_center(); msg('[Aviso] Esquecimento!'); cast('Esquecimento')
    for i in steps(18):
        t = i / 17
        def back(im, t=t):
            ov = Image.new('RGBA', (NW, NH), (0, 0, 0, 0))
            for k in range(4):
                rr = 6 + t * 120 - k * 11
                if rr > 0: ring(ov, st.bx, st.by, rr, rr * .5, (150 + k * 20, 70, 220), 230 - k * 40, 2)
            for j in range(28):
                a = j * .23 + t * 4; r_ = t * 110 * (.4 + (j % 6) / 7); disc(ov, st.bx + math.cos(a) * r_, st.by + math.sin(a) * r_ * .5, 1, (120, 60, 200), 150)
            im.alpha_composite(ov)
        if t > .7 and st.once('forget1'): st.forgot = .2; st.tint = ((150, 130, 200), .45)
        if t > .9: st.forgot = 1.0
        st.bi = int(6 + (i % 2)); st.hi += 1; emit(back=back)
    st.hero_expr = 'sad'
    idle(6); st.tint = None; st.forgot = 0
    # ===== 2 ECO =====
    msg('[Aviso] Eco!'); cast('Eco', 9)
    for i in steps(26):
        def extra(im, i=i):
            if i > 2:
                for dx_ in (-38, 38):
                    g = REI['cast']['down'][6]; a = g.split()[3].point(lambda v: 105 if v else 0)
                    g2 = tint(g, (120, 200, 255), .6); g2.putalpha(a); paste_feet(im, g2, (st.bx + dx_, st.by + 4))
        def front(im, i=i):
            ov = Image.new('RGBA', (NW, NH), (0, 0, 0, 0))
            for n_, (sx, t0) in enumerate(((st.bx - 38, 6), (st.bx + 38, 9), (st.bx, 12))):
                if i >= t0:
                    u = min(1, (i - t0) / 7.0); sy = st.by - 16
                    x = sx + (st.hx - sx) * u; y = sy + (st.hy - 16 - sy) * u
                    for tr in range(1, 5): disc(ov, x - (st.hx - sx) * .04 * tr, y - (st.hy - 16 - sy) * .04 * tr, 3 - tr // 2, (150, 70, 230), 130 - tr * 25)
                    disc(ov, x, y, 4, (180, 90, 255), 235); disc(ov, x, y, 2, (255, 255, 255), 255)
                    if u >= 1 and st.once('eco%d' % n_): hurt_hero(8); st.hp = max(.3, st.hp - .06)
            im.alpha_composite(ov)
            if st.hurt: label(im, (int(st.hx) + 4, int(st.hy) - 42 - (8 - st.hurt), ), str(41 + int(i)), (255, 224, 74), center=True)
        if st.hkind == 'hurt': st.hi = min(len(HERO['hurt']['up']) - 1, st.hi + 1)
        elif st.hurt == 0: hero('idle')
        st.bi = 6 + (int(i * 2) % 2); emit(front=front, extra=extra)
    hero('idle'); st.hurt = 0
    idle(6)
    # ===== 3 FENDA DO VAZIO: investida em 3 faixas, o Rei e 2 copias =====
    msg('[Aviso] Fenda do Vazio!'); cast('Fenda do Vazio', 10)
    lanes_x = [st.bx - 34, st.bx, st.bx + 34]
    hero_walk(49, 236, 4)
    st.clones = [(lanes_x[0], st.by, 0, 'cast', 6, 0), (lanes_x[2], st.by, 0, 'cast', 6, 0)]
    for i in steps(10):                                   # copias surgem; faixas de aviso (escalonadas como no jogo)
        al = min(190, int(i * 40))
        st.clones = [(lanes_x[0], st.by, al, 'cast', 6, 0), (lanes_x[2], st.by, al, 'cast', 6, 0)]
        st.lanes = [(lanes_x[1], st.by, min(200, int(max(0, i - 1) * 55))), (lanes_x[0], st.by, min(200, int(max(0, i - 3) * 55))), (lanes_x[2], st.by, min(200, int(max(0, i - 5) * 55)))]
        st.bi = 6; emit()
    for i in steps(6): st.bi = 6; emit()                  # segura o aviso
    boss('attack', 12, 'down')
    y0 = st.by; yend = 252
    for i in steps(10):                                   # investida: ease-in, estocada com as 3 faixas ao mesmo tempo
        u = (i / 9.5) ** 2 if i < 9.5 else 1.0
        yy = y0 + (yend - y0) * u
        st.by = yy; st.bi = 12 + (int(i * 2) % 2)
        st.clones = [(lanes_x[0], yy, 200, 'attack', 12 + (int(i * 2) % 2), 3), (lanes_x[2], yy, 200, 'attack', 12 + (int(i * 2) % 2), 3)]
        st.cracks = [(lanes_x[0], y0, yy, 220), (lanes_x[1], y0, yy, 220), (lanes_x[2], y0, yy, 220)]
        st.lanes = [(x, y0, max(0, 200 - int(i * 22))) for x in lanes_x]
        if i > 7: st.shake = (1, 0) if int(i * 2) % 2 else (0, 1)
        emit()
    st.lanes = []
    for i in steps(8):                                    # copias se dissipam; fendas somem aos poucos; heroi desvia (ESQUIVOU)
        a = max(0, 200 - int(i * 40))
        st.clones = [(lanes_x[0], yend, a, 'attack', 13, 0), (lanes_x[2], yend, a, 'attack', 13, 0)] if a > 0 else []
        st.cracks = [(x, y0, yend, max(0, 220 - int(i * 22))) for x in lanes_x]
        st.view = 'up'; hero('idle'); st.hi = int(i * 2)
        st.bi = 14 + min(3, int(i)); emit(front=(lambda im: label(im, (int(st.hx), int(st.hy) - 42), 'ESQUIVOU!', (140, 255, 180), center=True)))
    st.clones = []
    boss_walk(66, 118, 12, back=None)
    for i in steps(6):
        st.cracks = [(x, y0, yend, max(0, 70 - int(i * 12))) for x in lanes_x]; st.bi = int(i * 2); emit()
    st.cracks = []; idle(3)
    # ===== 4 COROA DE ALMAS =====
    msg('[Aviso] Coroa de Almas!'); cast('Coroa de Almas', 10)
    for i in steps(28):
        def front(im, i=i):
            ov = Image.new('RGBA', (NW, NH), (0, 0, 0, 0)); cx0, cy0 = st.bx, st.by - 38
            for n_ in range(5):
                a_ = n_ * 2 * math.pi / 5 + i * .35
                if i < 12: r_ = 11 + 1.4 * i; x = cx0 + math.cos(a_) * r_; y = cy0 + math.sin(a_) * r_ * .45
                else:
                    u = max(0, min(1, (i - 12 - n_ * 1.5) / 8)); x0 = cx0 + math.cos(a_) * 26; y0 = cy0 + math.sin(a_) * 11
                    mx = (x0 + st.hx) / 2 + (n_ - 2) * 8; my = (y0 + st.hy) / 2
                    x = (1 - u) ** 2 * x0 + 2 * (1 - u) * u * mx + u * u * st.hx; y = (1 - u) ** 2 * y0 + 2 * (1 - u) * u * my + u * u * (st.hy - 16)
                    if u >= 1 and st.once('soul%d' % n_): hurt_hero(6); st.hp = max(.15, st.hp - .04)
                    if u >= 1: continue
                for tr in range(1, 4): disc(ov, x - tr * 2, y + tr, 3 - tr // 2, (80, 170, 255), 120 - tr * 30)
                disc(ov, x, y, 4, (90, 190, 255), 230); disc(ov, x, y, 2, (255, 255, 255), 255)
            im.alpha_composite(ov)
            if st.hurt: label(im, (int(st.hx) + 3, int(st.hy) - 42), '31', (160, 220, 255), center=True)
        if st.hkind == 'hurt': st.hi = min(len(HERO['hurt']['up']) - 1, st.hi + 1)
        elif st.hurt == 0: hero('idle'); st.hi += 1
        st.bi = 6 + (int(i * 2) % 3); emit(front=front)
    hero('idle'); st.hurt = 0; idle(5)
    # ===== 5 TREVAS =====
    msg('[Aviso] Trevas!'); cast('Trevas', 10)
    for i in steps(32):
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
        if i >= 18 and st.once('dark_hit'): hurt_hero(10); st.hp = max(.15, st.hp - .1); st.shake = (1, 0)
        if st.hkind == 'hurt': st.hi = min(len(HERO['hurt']['up']) - 1, st.hi + 1)
        def front(im, i=i):
            if st.hurt: label(im, (int(st.hx) + 3, int(st.hy) - 42), '64', (200, 150, 255), center=True)
        st.bi = 6 + (int(i * 2) % 3); emit(back=back, front=front)
    st.dark = 0; hero('idle'); st.hurt = 0; idle(6)
    # ---- final ----
    boss_walk(64, 150, 10)
    hero_walk(58, 186, 10)
    for rep in range(2):
        def hb(rep=rep): st.bhp = max(.0, st.bhp - .35)
        hero_attack(hb); boss('hurt', 0, 'down')
        for k in range(len(REI['hurt']['down'])): st.bi = k; emit(front=(lambda im: label(im, (int(st.bx) + 6, int(st.by) - 46), '120', (255, 200, 60), center=True)))
        idle(1)
    st.bhp = 0; boss('death', 0, 'down')
    for k in range(len(REI['death']['down'])): st.bi = k; emit()
    for i in range(14): st.balpha = int(255 * (1 - (i + 1) / 14)); st.bi = len(REI['death']['down']) - 1; emit()
    st.victory = True
    for i in range(22): st.hi = i; emit()
    big = [f.convert('RGB').resize((NW * SC, NH * SC), Image.NEAREST) for f in frames]
    p = big[0].quantize(colors=240, method=Image.MEDIANCUT, dither=Image.NONE)
    q = [b.quantize(palette=p, dither=Image.NONE) for b in big]
    q[0].save(os.path.join(OUT, 'rei_rpg3.gif'), save_all=True, append_images=q[1:], duration=45, loop=0, disposal=1)
    return len(q), big


def sheets():
    # expressoes
    faces = ['n', 'blink', 'happy', 'smirk', 'angry', 'hurt', 'surprised', 'sad', 'dead', 'shout']
    A = Image.new('RGBA', (C.W * len(faces), C.H * 4), (52, 44, 72, 255))
    for r, (app, cls, view) in enumerate(((HAPP, 'warrior', 'down'), (dict(cls='mage'), 'mage', 'down'), (REIAPP, 'rei', 'down'), (HAPP, 'warrior', 'right'))):
        for i, f in enumerate(faces):
            im = C.anim(view, 'idle', cls, [dict(tn=3, face=f)], app)[0][0]; A.alpha_composite(im, (i * C.W, r * C.H))
    A = A.crop((0, 0, A.width, A.height)).resize((A.width * 2, A.height * 2), Image.NEAREST).convert('RGB'); A.save(os.path.join(OUT, 'expressoes.png'))
    # animacoes densas do Rei
    rows = [('idle', 12), ('walk', 16), ('attack', 19), ('cast', 15), ('hurt', 7), ('death', 11)]
    Wc, Hc = 56, 46
    S_ = Image.new('RGBA', (Wc * 19, Hc * 3 * len(rows)), (52, 44, 72, 255))
    for ri, (k, n) in enumerate(rows):
        for vi, v in enumerate(('down', 'up', 'right')):
            for i in range(n): S_.alpha_composite(REI[k][v][i].crop((8, 2, 8 + Wc, 2 + Hc)), (i * Wc, (ri * 3 + vi) * Hc))
    S_.convert('RGB').save(os.path.join(OUT, 'rei_animacoes_dense.png'))


if __name__ == '__main__':
    sheets()
    n, big = run(); print(n)
    N_ = len(big); sel = [big[min(N_ - 1, int(N_ * q))] for q in (.04, .1, .15, .2, .25, .3, .36, .4, .43, .46, .5, .56, .62, .7, .8, .97)]
    sh = Image.new('RGB', (NW * SC // 2 * 8, NH * SC // 2 * 2))
    for i, b in enumerate(sel): sh.paste(b.resize((NW * SC // 2, NH * SC // 2), Image.NEAREST), ((i % 8) * NW * SC // 2, (i // 8) * NH * SC // 2))
    sh.save(os.path.join(OUT, 'rei_rpg3_folha.png'))
