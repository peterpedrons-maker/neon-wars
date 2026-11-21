#!/usr/bin/env python3
"""CINZAMURO (cidade-fortaleza da Região 2) — gera mmo/assets/cinzamuro.json, cinzamuro_ground.png e atlas_cinza.png/json.
Peças novas (muralha, torres, portão, casas de adobe, fortaleza, cactos) desenhadas por código no mesmo estilo dos props da Brumavale;
casas de loja = as casas da Brumavale recoloridas para arenito. Rodar: /usr/bin/python3 tools/mmo/build_cinzamuro.py (de lendas-de-taverna/)."""
import json, random, math, colorsys, os
import numpy as np
from PIL import Image, ImageDraw
A = 'mmo/assets/'
R = random.Random(7)
# ------------------------------------------------------------------ paleta de arenito
L1, L2, L3, L4, L5 = (236, 214, 168), (214, 184, 134), (186, 150, 106), (150, 114, 80), (104, 78, 58)
MORT = (120, 92, 66); OUT = (58, 40, 32)
def jit(c, k=6):
    d = R.randint(-k, k); return tuple(max(0, min(255, v + d)) for v in c)
def block_wall(w, h, bw=32, bh=16, seed=0):
    """face de muralha de blocos: luz em cima/esquerda, argamassa, pixels de ruído"""
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im); rr = random.Random(seed)
    for r in range(0, h, bh):
        off = (bw // 2) if (r // bh) % 2 else 0
        for c in range(-off, w, bw):
            base = rr.choice([L2, L2, L3, L3, L1])
            x0, x1 = max(0, c), min(w, c + bw); y1 = min(h, r + bh)
            if x1 <= x0: continue
            d.rectangle([x0, r, x1 - 1, y1 - 1], fill=base)
            d.line([(x0, r), (x1 - 1, r)], fill=L1)                     # luz de cima
            d.line([(x0, r), (x0, y1 - 1)], fill=jit(L1, 3))            # luz da esquerda
            d.line([(x0, y1 - 1), (x1 - 1, y1 - 1)], fill=MORT)         # argamassa embaixo
            d.line([(x1 - 1, r), (x1 - 1, y1 - 1)], fill=MORT)
            for _ in range(5):
                px, py = rr.randint(x0, x1 - 1), rr.randint(r, y1 - 1)
                im.putpixel((px, py), jit(L3, 14) + (255,))
    return im
def crenel(w, mh=22, mw=20, gap=12):
    """merlões ao longo da largura w (altura mh)"""
    im = Image.new('RGBA', (w, mh), (0, 0, 0, 0)); d = ImageDraw.Draw(im); x = gap // 2
    while x < w:
        x1 = min(w, x + mw)
        d.rectangle([x, 0, x1 - 1, mh - 1], fill=L2); d.line([(x, 0), (x1 - 1, 0)], fill=L1); d.line([(x, 0), (x, mh - 1)], fill=L1)
        d.line([(x1 - 1, 0), (x1 - 1, mh - 1)], fill=L4); x += mw + gap
    return im
def outline(im, col=OUT):
    a = np.array(im); m = a[..., 3] > 0; o = np.zeros_like(m)
    o[1:] |= m[:-1]; o[:-1] |= m[1:]; o[:, 1:] |= m[:, :-1]; o[:, :-1] |= m[:, 1:]; o &= ~m
    a[o] = list(col) + [255]; return Image.fromarray(a)
def shade_side(im, right=14, bottom=10):
    """sombra de baixo/direita (volume)"""
    a = np.array(im).astype(int); h, w = a.shape[:2]
    for x in range(w - right, w):
        t = (x - (w - right)) / right
        a[:, x, :3] = (a[:, x, :3] * (1 - .28 * t)).astype(int)
    for y in range(h - bottom, h):
        t = (y - (h - bottom)) / bottom
        a[y, :, :3] = (a[y, :, :3] * (1 - .25 * t)).astype(int)
    return Image.fromarray(np.clip(a, 0, 255).astype('uint8'))
def paste(dst, src, x, y): dst.alpha_composite(src, (x, y))
# ------------------------------------------------------------------ peças
def wall_seg():
    W, H = 128, 150
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); paste(im, crenel(W), 0, 0)
    face = block_wall(W, H - 22, seed=3); paste(im, face, 0, 22)
    d = ImageDraw.Draw(im); d.rectangle([0, 22, W - 1, 28], fill=L1); d.line([(0, 28), (W - 1, 28)], fill=L3)        # beiral
    for x in (30, 98):                                                                                                  # seteiras
        d.rectangle([x, 62, x + 5, 82], fill=(34, 24, 22)); d.line([(x, 62), (x + 5, 62)], fill=L5)
    return outline(shade_side(im, 0, 12)), (W // 2, H - 1)
def wall_side():
    W, H = 60, 150
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); paste(im, crenel(W, 22, 22, 16), 0, 0)
    paste(im, block_wall(W, H - 22, bw=30, seed=11), 0, 22)
    d = ImageDraw.Draw(im); d.rectangle([0, 22, W - 1, 27], fill=L1)
    return outline(shade_side(im, 14, 8)), (W // 2, H - 1)
def tower():
    W, H = 124, 250
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); body = block_wall(W - 16, H - 40, bw=36, seed=5); paste(im, body, 8, 40)
    d = ImageDraw.Draw(im); d.rectangle([0, 28, W - 1, 46], fill=L2); d.line([(0, 28), (W - 1, 28)], fill=L1); d.line([(0, 46), (W - 1, 46)], fill=MORT)
    paste(im, crenel(W, 28, 22, 12), 0, 2)
    for (x, y) in ((50, 90), (50, 150)):
        d.rectangle([x, y, x + 8, y + 26], fill=(34, 24, 22)); d.line([(x, y), (x + 8, y)], fill=L5)
    d.rectangle([8, H - 46, W - 9, H - 1], fill=L3)
    # estandarte da Ordem
    d.rectangle([W // 2 - 11, 190, W // 2 + 11, 232], fill=(150, 36, 36)); d.polygon([(W // 2 - 11, 232), (W // 2, 244), (W // 2 + 11, 232)], fill=(150, 36, 36))
    d.ellipse([W // 2 - 5, 204, W // 2 + 5, 214], fill=(236, 200, 90))
    return outline(shade_side(im, 16, 10)), (W // 2, H - 1)
def gate_arch():
    W, H = 300, 210
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); paste(im, crenel(W, 24, 26, 16), 0, 0); paste(im, block_wall(W, H - 24, bw=40, seed=9), 0, 24)
    d = ImageDraw.Draw(im); ox0, ox1 = W // 2 - 70, W // 2 + 70
    # vão do arco (transparente) + moldura
    arc = Image.new('L', (W, H), 255); ad = ImageDraw.Draw(arc)
    ad.rectangle([ox0, 90, ox1, H], fill=0); ad.ellipse([ox0, 50, ox1, 130], fill=0)
    a = np.array(im); m = np.array(arc) == 0; a[m] = (0, 0, 0, 0); im = Image.fromarray(a)
    d = ImageDraw.Draw(im)
    for x in range(ox0 - 5, ox1 + 6, 1):                                                                              # aro de pedra
        for y in (50, 51, 52):
            pass
    d.arc([ox0 - 6, 44, ox1 + 6, 136], 180, 360, fill=L1, width=6); d.line([(ox0 - 6, 90), (ox0 - 6, H - 1)], fill=L1, width=6); d.line([(ox1 + 6, 90), (ox1 + 6, H - 1)], fill=L4, width=6)
    for x in range(ox0 + 8, ox1, 14):                                                                                 # grade levantada
        d.line([(x, 56 + int(6 * math.sin((x - W / 2) / 25) ** 2) - 2), (x, 84)], fill=(54, 40, 34), width=3)
    d.rectangle([ox0 + 6, 80, ox1 - 6, 86], fill=(54, 40, 34))
    d.rectangle([W // 2 - 14, 8, W // 2 + 14, 24], fill=L1)
    return outline(shade_side(im, 14, 10)), (W // 2, H - 1)
def adobe(seed, w=190, h=150, roof=(196, 164, 118), awn=((190, 60, 50), (236, 222, 190))):
    rr = random.Random(seed); im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    top = 30
    body = block_wall(w, h - top, bw=44, bh=18, seed=seed); paste(im, body, 0, top)
    d.rectangle([0, top - 8, w - 1, top + 6], fill=L1); d.line([(0, top + 6), (w - 1, top + 6)], fill=L4)              # parapeito
    d.rectangle([4, 4, w - 5, top - 8], fill=roof); d.line([(4, 4), (w - 5, 4)], fill=L1)
    for i in range(3):
        x = rr.randint(20, w - 60); d.rectangle([x, top + 24, x + 16, top + 44], fill=(52, 38, 32)); d.line([(x, top + 24), (x + 16, top + 24)], fill=L5)
    dx = rr.choice([w // 2 - 14, w // 2 + 18]); d.rounded_rectangle([dx - 14, h - 56, dx + 14, h - 1], radius=12, fill=(72, 48, 34)); d.line([(dx - 14, h - 56), (dx + 14, h - 56)], fill=(110, 78, 52))
    ax = rr.randint(10, 24)
    for i in range(0, 56, 14):                                                                                         # toldo listrado
        d.polygon([(ax + i, top + 40), (ax + i + 14, top + 40), (ax + i + 16, top + 60), (ax + i - 2, top + 60)], fill=awn[(i // 14) % 2])
    return outline(shade_side(im, 12, 8)), (w // 2, h - 1)
def keep():
    W, H = 420, 300
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    paste(im, block_wall(W - 120, H - 70, bw=44, seed=21), 60, 70); paste(im, crenel(W - 120, 26, 24, 14), 60, 46)
    for x0 in (0, W - 100):
        paste(im, block_wall(100, H - 40, bw=34, seed=x0 + 5), x0, 40); paste(im, crenel(100, 26, 22, 12), x0, 16)
    d.rectangle([60, 70, W - 61, 80], fill=L1)
    d.rounded_rectangle([W // 2 - 26, H - 110, W // 2 + 26, H - 1], radius=24, fill=(60, 40, 32)); d.line([(W // 2, H - 110), (W // 2, H - 1)], fill=(36, 24, 22), width=2)
    for x in (110, 170, 250, 310):
        d.rectangle([x, 120, x + 12, 156], fill=(34, 24, 22)); d.line([(x, 120), (x + 12, 120)], fill=L5)
    for x in (140, 280):                                                                                              # estandartes da Ordem
        d.rectangle([x - 14, 170, x + 14, 236], fill=(150, 36, 36)); d.polygon([(x - 14, 236), (x, 252), (x + 14, 236)], fill=(150, 36, 36)); d.ellipse([x - 6, 190, x + 6, 202], fill=(236, 200, 90))
    return outline(shade_side(im, 16, 10)), (W // 2, H - 1)
def cactus(kind):
    W, H = 46, 78; im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    G1, G2, G3 = (96, 150, 80), (66, 112, 60), (130, 180, 100)
    d.rounded_rectangle([18, 8, 30, H - 2], radius=6, fill=G1); d.line([(20, 12), (20, H - 6)], fill=G3, width=2); d.line([(28, 14), (28, H - 4)], fill=G2, width=2)
    if kind == 0:
        d.rounded_rectangle([4, 30, 16, 44], radius=5, fill=G1); d.rectangle([4, 40, 20, 46], fill=G1); d.rounded_rectangle([32, 22, 44, 36], radius=5, fill=G1); d.rectangle([28, 32, 44, 38], fill=G1)
    for i in range(14):
        x, y = R.randint(10, 38), R.randint(10, H - 6)
        if im.getpixel((x, y))[3]: d.point((x, y), fill=(236, 226, 190))
    return outline(im), (W // 2, H - 1)
def dry_bush():
    W, H = 44, 34; im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for i in range(16):
        a = R.uniform(-1.2, 1.2); l = R.randint(10, 22); x0 = W // 2 + R.randint(-4, 4)
        d.line([(x0, H - 2), (x0 + int(math.sin(a) * l), H - 2 - int(math.cos(a) * l))], fill=R.choice([(150, 120, 72), (120, 92, 56), (176, 148, 92)]), width=2)
    return outline(im), (W // 2, H - 1)
def recolor(src):
    """casa da Brumavale -> arenito (telhado azul/verde/roxo vira terracota; paredes ganham tom de areia)"""
    a = np.array(src.convert('RGBA')).astype(float); out = a.copy()
    for y in range(a.shape[0]):
        for x in range(a.shape[1]):
            r, g, b, al = a[y, x]
            if al == 0: continue
            h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
            if s > .18 and .38 < h < .9:                       # azul/verde/roxo -> terracota
                h = .055 + (h - .5) * .02; s = min(1, s * .95 + .08); v = v * .98
            elif s < .22 and v > .55:                          # paredes claras -> areia
                s = .22; h = .1; v = v * .96
            elif s >= .18 and (h < .1 or h > .93):             # telhados vermelhos -> mais laranja
                h = .045
            rr, gg, bb = colorsys.hsv_to_rgb(h % 1, s, v); out[y, x] = (rr * 255, gg * 255, bb * 255, al)
    return Image.fromarray(out.astype('uint8'))
# ------------------------------------------------------------------ atlas
def build_atlas():
    base = json.load(open(A + 'atlas_regiao1.json')); bim = Image.open(A + 'atlas_regiao1.png').convert('RGBA')
    sprites = {}                                                                                                       # nome -> (img, (ax,ay))
    for k, f in (('w_seg', wall_seg()), ('w_side', wall_side()), ('tower', tower()), ('gate', gate_arch()), ('keep', keep()),
                 ('cactus0', cactus(0)), ('cactus1', cactus(1)), ('bush', dry_bush())):
        sprites[k] = f
    for i in range(6): sprites['ad%d' % i] = adobe(40 + i, 170 + 20 * (i % 3), 140 + 10 * (i % 2), awn=[((190, 60, 50), (236, 222, 190)), ((60, 110, 170), (236, 222, 190)), ((200, 150, 50), (236, 222, 190))][i % 3])
    for k in ('b_mes', 'b_lei', 'b_mer', 'b_alq', 'b_fer', 'b_cof'):                                                   # lojas em arenito
        x, y, w, h, ax, ay = base[k]; sprites['s_' + k[2:]] = (recolor(bim.crop((x, y, x + w, y + h))), (ax, ay))
    for k in ('v_well', 'v_lamp1', 'v_lamp2', 'v_banner1', 'v_banner2', 'v_sign', 'v_crates', 'v_stall', 'v_post', 'v_barrel1', 'v_barrel2', 'v_hay1', 'v_hay2', 'v_bench1', 'v_bench2', 'v_sack1', 'v_sack2', 'v_torch1', 'v_torch2', 'v_torch3',
              'ca1d87b329', 'acb08a8c5b', 'e6d4616d52', '22720f07d4', 'd876089903', 'bfef3c867f', '451b53119f'):
        x, y, w, h, ax, ay = base[k]; sprites[k] = (bim.crop((x, y, x + w, y + h)), (ax, ay))
    # empacota em prateleiras (largura 1360)
    AW = 1360; xx = yy = rowh = 0; fr = {}; pos = {}
    for k, (im, anc) in sprites.items():
        w, h = im.size
        if xx + w > AW: xx = 0; yy += rowh + 2; rowh = 0
        pos[k] = (xx, yy, im, anc); xx += w + 2; rowh = max(rowh, h)
    AH = yy + rowh + 2; atlas = Image.new('RGBA', (AW, AH), (0, 0, 0, 0))
    for k, (x, y, im, anc) in pos.items():
        atlas.alpha_composite(im, (x, y)); fr[k] = [x, y, im.width, im.height, anc[0], anc[1]]
    atlas.save(A + 'atlas_cinza.png', optimize=True); json.dump(fr, open(A + 'atlas_cinza.json', 'w'))
    print('atlas', atlas.size, len(fr)); return fr
# ------------------------------------------------------------------ mapa
W, H = 1600, 2400
WX0, WX1, WTOP, WBOT = 150, 1450, 440, 2180          # muralha: oeste/leste (x), topo/base (y do pé)
GX0, GX1 = 710, 890                                  # vão dos portões
def circ_row(x, y, w, hh, step=18, r=13):
    """colisão de um bloco (footprint de largura w e altura hh acima do pé) em círculos"""
    out = []
    for dy in range(-4, -hh - 1, -18):
        for dx in range(-w // 2 + 8, w // 2 - 6, step):
            out.append([dx, dy, r if dy < -10 else 9])
    return out
def build():
    fr = build_atlas(); props = []
    def P(t, i, x, y, col=None):
        d = {'t': t, 'id': i, 'x': x, 'y': y}
        if col: d['col'] = col
        props.append(d)
    # --- muralha norte e sul (com vão dos portões)
    for (yb, tag) in ((WTOP, 'n'), (WBOT, 's')):
        x = WX0 + 64
        while x < WX1 - 40:
            if GX0 - 64 < x < GX1 + 64: x += 128; continue
            P('p', 'w_seg', x, yb, circ_row(x, yb, 128, 130)); x += 128
    # --- muralha oeste e leste
    for xb in (WX0, WX1):
        y = WTOP + 60
        while y <= WBOT - 10:
            P('p', 'w_side', xb, y, [[0, -4, 13], [0, -22, 13], [0, -40, 13]]); y += 56
    # --- torres de canto e dos portões
    for (x, y) in ((WX0, WTOP), (WX1, WTOP), (WX0, WBOT), (WX1, WBOT), (GX0 - 62, WTOP), (GX1 + 62, WTOP), (GX0 - 62, WBOT), (GX1 + 62, WBOT)):
        P('p', 'tower', x, y + 10, circ_row(x, y, 110, 200))
    # arco do portão sul e norte (apenas as colunas laterais bloqueiam)
    P('p', 'gate', (GX0 + GX1) // 2, WBOT + 10, [[dx, dy, 13] for dy in (-4, -22, -40, -58, -76, -94) for dx in (-120, -102, -84, 84, 102, 120)])
    P('p', 'gate', (GX0 + GX1) // 2, WTOP + 10, [[dx, dy, 13] for dy in (-4, -22, -40, -58, -76, -94) for dx in (-120, -102, -84, 84, 102, 120)])
    # --- Bastião da Ordem (nordeste): fortaleza grande
    P('p', 'keep', 1140, 820, circ_row(1140, 820, 420, 240, step=20))
    # --- lojas (as 6 portas): Mercado do Muro (oeste) e o resto (leste)
    SH = [('fer', 'fer', 'Ferreiro', 'anvil', 420, 1060), ('mer', 'mer', 'Mercador', 'scales', 420, 1460), ('alq', 'alq', 'Alquimista', 'magic-swirl', 420, 1860),
          ('mes', 'mes', 'Mestre de Classe', 'holy-symbol', 1180, 1220), ('lei', 'lei', 'Leilão', 'two-coins', 1180, 1560), ('cof', 'cof', 'Cofre', 'locked-chest', 1180, 1900)]
    doors = []
    for (i, a, nm, ic, x, y) in SH:
        P('p', 's_' + a, x, y, circ_row(x, y, 190, 190, step=20)); doors.append({'id': i, 'nm': nm, 'x': x, 'y': y + 6, 'w': 64, 'h': 82, 'room': 'int_' + i, 'ic': ic})
    # --- casas de adobe (Guildas / Bairro Baixo)
    AD = [(300, 700, 0), (560, 700, 1), (300, 1260, 2), (560, 1270, 3), (1020, 1060, 4), (1330, 1060, 5), (1010, 1760, 1), (1300, 1760, 2), (270, 1660, 3), (580, 1700, 4), (1330, 1400, 0), (1010, 1400, 5)]
    for (x, y, k) in AD:
        w = 170 + 20 * (k % 3)
        P('p', 'ad%d' % k, x, y, circ_row(x, y, w, 120, step=20))
    # --- decoração: lampiões, estandartes, barris, caixas, bancos, poço, tendas de mercado
    P('p', 'v_well', 800, 1210, [[0, -4, 22], [0, -26, 22]])
    for y in range(560, 2100, 150):
        for x in (690, 910): P('p', 'v_lamp1' if (y // 150) % 2 else 'v_lamp2', x, y, [[0, -3, 7]])
    for (x, y, i) in ((600, 1130, 'v_stall'), (610, 1520, 'v_stall'), (990, 1120, 'v_stall'), (610, 1760, 'v_crates'), (1030, 1640, 'v_crates'), (680, 1960, 'v_barrel1'), (700, 1970, 'v_barrel2'), (920, 1960, 'v_barrel1'), (940, 1975, 'v_hay1'),
                      (640, 1260, 'v_bench1'), (960, 1260, 'v_bench2'), (880, 480, 'v_sack1'), (720, 480, 'v_sack2'), (760, 1940, 'v_banner1'), (840, 1940, 'v_banner1')):
        P('p', i, x, y, [[0, -4, 12]] if i not in ('v_banner1',) else [[0, -3, 6]])
    for (x, y) in ((GX0 - 40, WTOP + 40), (GX1 + 40, WTOP + 40), (GX0 - 40, WBOT - 40), (GX1 + 40, WBOT - 40)): P('p', 'v_torch1', x, y, [[0, -3, 6]])
    # --- cactos, arbustos secos e pedras fora e dentro dos muros
    rr = random.Random(5)
    for _ in range(160):
        x, y = rr.randint(40, W - 40), rr.randint(40, H - 40)
        inside = WX0 - 20 < x < WX1 + 20 and WTOP - 30 < y < WBOT + 30
        if inside or (GX0 - 80 < x < GX1 + 80): continue
        k = rr.random()
        P('p', rr.choice(['cactus0', 'cactus1', 'bush', 'bush']) if k < .6 else rr.choice(['ca1d87b329', 'acb08a8c5b', 'e6d4616d52', '22720f07d4']), x, y, [[0, -3, 10]])
    for _ in range(26):
        x, y = rr.randint(200, 1400), rr.randint(520, 2100)
        if any(abs(x - p['x']) < 120 and abs(y - p['y']) < 70 for p in props if p['t'] == 'p') or 700 < x < 900: continue
        P('p', rr.choice(['bush', 'v_barrel2', 'cactus1', 'bush']), x, y, [[0, -3, 8]])
    for _ in range(14): P('p', rr.choice(['bfef3c867f', '451b53119f']), rr.choice([rr.randint(30, 120), rr.randint(1480, 1570)]), rr.randint(300, 2200), [[0, -3, 9]])
    npcs = [
        {'id': 'guaz', 'nm': 'Guarda do Portal', 'sh': 'guarda', 'x': 800, 'y': 1720, 'ic': 'treasure-map', 'row': 2, 'win': 'portal'},
        {'id': 'vorak', 'nm': 'Intendente Vorak', 'sh': 'guarda', 'x': 1030, 'y': 880, 'ic': 'scroll-unfurled', 'row': 2},
        {'id': 'orsa', 'nm': 'Orsa, Mestra das Guildas', 'sh': 'pov_f', 'x': 560, 'y': 1360, 'ic': 'shop', 'row': 2},
        {'id': 'zelle', 'nm': 'Zelle, a Informante', 'sh': 'ladino_b', 'x': 1010, 'y': 1900, 'ic': 'hooded-figure', 'row': 2},
        {'id': 'arquivista', 'nm': 'Arquivista Dael', 'sh': 'clerigo', 'x': 1010, 'y': 700, 'ic': 'book-cover', 'row': 2}]
    vill = [{'sh': 'pov_f', 'x': 760, 'y': 1500}, {'sh': 'ladino_b', 'x': 860, 'y': 1030}, {'sh': 'bardo', 'x': 800, 'y': 900}, {'sh': 'pov_f', 'x': 640, 'y': 1800},
            {'sh': 'guarda', 'x': GX0 + 30, 'y': WBOT - 70}, {'sh': 'guarda', 'x': GX1 - 30, 'y': WBOT - 70}, {'sh': 'guarda', 'x': GX0 + 30, 'y': WTOP + 90}, {'sh': 'guarda', 'x': GX1 - 30, 'y': WTOP + 90}]
    fx = [{'k': 'glow', 'x': GX0 - 40, 'y': WTOP + 12, 'col': '#ffae4a', 'r': 60, 'lo': .4, 'hi': .8, 'fl': 1}, {'k': 'glow', 'x': GX1 + 40, 'y': WTOP + 12, 'col': '#ffae4a', 'r': 60, 'lo': .4, 'hi': .8, 'fl': 1},
          {'k': 'glow', 'x': GX0 - 40, 'y': WBOT - 28, 'col': '#ffae4a', 'r': 60, 'lo': .4, 'hi': .8, 'fl': 1}, {'k': 'glow', 'x': GX1 + 40, 'y': WBOT - 28, 'col': '#ffae4a', 'r': 60, 'lo': .4, 'hi': .8, 'fl': 1},
          {'k': 'smoke', 'x': 420, 'y': 900}, {'k': 'glow', 'x': 360, 'y': 1030, 'col': '#ff8a2a', 'r': 54, 'lo': .45, 'hi': .9, 'fl': 1}]
    town = {'w': W, 'h': H, 'props': props, 'start': [800, 2040], 'portal': {'x': 800, 'y': 1650, 'stand': [800, 1800], 'fx': {'dx': 0, 'dy': 0, 'rx': 1, 'ry': 1}, 'off': True},
            'npcs': npcs, 'vill': vill, 'doors': doors, 'fx': fx, 'plaza': {'x': 800, 'y': 1210, 'nm': 'Praça dos Registros'}, 'boards': [],
            'exits': [{'id': 'passo', 'nm': 'Passo da Montanha', 'side': 1, 'x': 700, 'y': H - 70, 'w': 200, 'h': 70, 'to': 'zone_passo', 'at': [2250, 330], 'ready': True, 'msg': '', 'toSide': 0},
                      {'id': 'muralha', 'nm': 'Estrada da Muralha', 'side': 0, 'x': 700, 'y': 0, 'w': 200, 'h': 70, 'to': 'zone_muralha', 'at': [1100, 3000], 'ready': False, 'msg': 'A Estrada da Muralha ainda está em obras.', 'toSide': 1}],
            }
    json.dump(town, open(A + 'cinzamuro.json', 'w'))
    # ---------------- chão (1 px = 1 px do mundo)
    rg = np.random.RandomState(3); g = np.zeros((H, W, 3), 'uint8')
    sand = np.array([212, 184, 134]); dirt = np.array([186, 154, 108])
    n = rg.randint(-8, 8, (H, W, 1)); g[:] = (sand + n).clip(0, 255)
    yy, xx = np.mgrid[0:H, 0:W]
    out = ~((xx > WX0) & (xx < WX1) & (yy > WTOP - 40) & (yy < WBOT + 10))
    lowf = np.kron(rg.rand(H // 40 + 2, W // 40 + 2), np.ones((40, 40)))[:H, :W]
    patch = out & (lowf > .62); g[patch] = (dirt + rg.randint(-8, 8, (patch.sum(), 1))).clip(0, 255)
    # pedregulho/seixos no deserto
    # chão calçado dentro da cidade (placas de pedra)
    inn = ~out
    tile = ((xx // 24) + (yy // 24)) % 2
    cob = np.where(tile[..., None] == 0, np.array([170, 168, 160]), np.array([158, 156, 148]))
    cob = cob + rg.randint(-8, 8, (H, W, 1))
    mort = ((xx % 24 == 0) | (yy % 24 == 0))[..., None]; cob = np.where(mort, np.array([112, 108, 100]), cob)
    avenue = (xx > 730) & (xx < 870); cross = (yy > 1180) & (yy < 1250); plazaS = (yy > 1780) & (yy < 2090) & (xx > 560) & (xx < 1040); plazaC = (np.hypot(xx - 800, (yy - 1215) * 1.3) < 170)
    street = avenue | cross | plazaS | plazaC | ((yy > 440) & (yy < 520) & (xx > 700) & (xx < 900))
    lane = np.zeros_like(street)
    for (x0, x1, y0, y1) in ((300, 1300, 1000, 1030), (300, 1300, 1620, 1650), (330, 360, 600, 2100), (1240, 1270, 600, 2100)): lane |= (xx > x0) & (xx < x1) & (yy > y0) & (yy < y1)
    g[inn] = np.where(street[inn][:, None], cob[inn] + 18, np.where(lane[inn][:, None], cob[inn], (dirt + 8 + rg.randint(-8, 8, (inn.sum(), 1)))))
    # pegada das muralhas (faixa escura de pedra)
    for (x0, x1, y0, y1) in ((WX0 - 30, WX1 + 30, WTOP - 8, WTOP + 20), (WX0 - 30, WX1 + 30, WBOT - 8, WBOT + 20), (WX0 - 20, WX0 + 24, WTOP, WBOT), (WX1 - 24, WX1 + 20, WTOP, WBOT)):
        g[y0:y1, x0:x1] = (118, 114, 106)
    # estrada de terra até os portões
    road = ((xx > 730) & (xx < 870) & ((yy < WTOP) | (yy > WBOT))); g[road] = (150, 126, 90) + rg.randint(-8, 8, (road.sum(), 1))
    Image.fromarray(g).save(A + 'cinzamuro_ground.png')
    print('cinzamuro', len(props), 'props', len(doors), 'portas')
if __name__ == '__main__':
    build()
