#!/usr/bin/env python3
"""Jogo atual em pixel art retro, v2: MAPAS REAIS do jogo (chao+props do atlas) em escala coerente, HUD/menus em resolucao nativa 195x423 (x2 = 390x846),
celulas de item 26px com estrelas e PC legiveis. Tudo por codigo."""
import math, os, random
from PIL import Image, ImageDraw
import chibi as C
import icons_pixel as IC
import pxfont
import mapview as MV
from jogo_pixel import spr, ENEMY
from teste_clareira import OUT

NW, NH, SC = MV.NW, MV.NH, 2
GOLD = (214, 172, 80); GOLD_D = (120, 88, 44); BG = (16, 14, 28); CREAM = (240, 226, 190); DIM = (150, 140, 130)


def T(im, xy, s, col=CREAM, center=False, k=1): pxfont.text(im, xy, s, col, center, True, k)


def panel(d, box, fill=BG, border=GOLD, studs=True):
    x0, y0, x1, y1 = box
    d.rectangle([x0, y0, x1, y1], fill=fill, outline=GOLD_D); d.rectangle([x0 + 1, y0 + 1, x1 - 1, y1 - 1], outline=border)
    if studs:
        for (x, y) in ((x0, y0), (x1, y0), (x0, y1), (x1, y1)): d.rectangle([x - 1, y - 1, x + 1, y + 1], fill=border)


def bar(d, x, y, w, frac, col, h=5):
    d.rectangle([x - 1, y - 1, x + w, y + h], fill=(10, 6, 16)); d.rectangle([x, y, x + int((w - 1) * frac), y + h - 1], fill=col)
    d.line([x, y, x + int((w - 1) * frac), y], fill=tuple(min(255, c + 70) for c in col))


def hud(im, zone=None, hp=1.0, msgs=(), boss=None, quest=True):
    d = ImageDraw.Draw(im)
    panel(d, (4, 4, 98, 40))
    d.rectangle([8, 8, 34, 34], fill=(50, 26, 26), outline=GOLD)
    im.alpha_composite(spr('heroi')[0].crop((20, 6, 52, 26)).resize((25, 25), Image.NEAREST), (9, 9))
    T(im, (38, 9), 'TESTE', CREAM); bar(d, 38, 18, 56, hp, (210, 50, 50), 8); T(im, (66, 20), '135/135', (255, 236, 236), True)
    T(im, (38, 30), 'PC 147', GOLD)
    d.ellipse([5, 28, 19, 42], fill=(210, 160, 50), outline=(120, 80, 20)); T(im, (12, 32), '1', (40, 24, 8), True)
    if zone:
        T(im, (168, 4), zone, GOLD, True)
        panel(d, (146, 12, 191, 57)); d.rectangle([149, 15, 188, 54], fill=(10, 10, 22))
        for (x0, y0, x1, y1) in ((154, 27, 183, 33), (165, 35, 173, 51)): d.rectangle([x0, y0, x1, y1], fill=(38, 34, 60))
        d.rectangle([168, 40, 170, 42], fill=(255, 220, 90))
    if quest:
        panel(d, (120, 62, 191, 100), fill=(16, 14, 28)); T(im, (126, 67), 'MISSOES', GOLD); T(im, (126, 77), 'Primeiros', CREAM); T(im, (126, 85), 'passos', CREAM); T(im, (186 - pxfont.width('0/8'), 85), '0/8', (140, 255, 160))
    for i, (t, ic) in enumerate((('PERS', 'helm'), ('HABIL', 'espada_aco'), ('DIARIO', 'scroll'), ('SOCIAL', 'ring'))):
        y = 220 + i * 36; panel(d, (160, y, 191, y + 32), fill=(20, 16, 34)); im.alpha_composite(IC.get(ic).crop((1, 1, 15, 15)), (168, y + 3)); T(im, (176, y + 22), t, CREAM, True)
    ov = Image.new('RGBA', im.size, (0, 0, 0, 0)); od = ImageDraw.Draw(ov); od.rectangle([4, 338, 128, 368], fill=(8, 6, 16, 150)); im.alpha_composite(ov)
    for i, m in enumerate(list(msgs)[-3:]): T(im, (8, 341 + i * 9), m, CREAM if 'Aviso' not in m else (255, 190, 120))
    d.ellipse([8, 266, 66, 324], outline=GOLD_D, fill=(22, 16, 30)); d.ellipse([26, 284, 48, 306], fill=GOLD, outline=GOLD_D)
    panel(d, (8, 374, 187, 419), fill=(16, 12, 26))
    for i, (key, ic, lock) in enumerate((('1', 'espada_aco', ''), ('2', None, 'NV5'), ('3', None, 'NV10'), ('P', 'potion', ''), ('E', 'boots', ''))):
        x = 22 + i * 30; d.rectangle([x, 379, x + 27, 413], fill=(22, 16, 34), outline=GOLD if ic else GOLD_D)
        T(im, (x + 3, 382), key, GOLD if ic else DIM)
        if ic: im.alpha_composite((IC.get('potion', 'red') if ic == 'potion' else IC.get(ic)).crop((1, 1, 15, 15)), (x + 7, 392))
        if lock: T(im, (x + 14, 398), lock, DIM, True)
    T(im, (22 + 3 * 30 + 24, 405), '2', CREAM, True)
    if boss:
        T(im, (97, 3), boss[0], CREAM, True, 2); d.rectangle([4, 14, 190, 21], fill=(14, 8, 16), outline=GOLD); d.rectangle([5, 15, 5 + int(184 * boss[1]), 20], fill=(205, 40, 40))


def mini_hp(im, x, y, frac, w=18):
    d = ImageDraw.Draw(im); d.rectangle([x - w // 2 - 1, y - 1, x + w // 2 + 1, y + 3], fill=(10, 6, 16)); d.rectangle([x - w // 2, y, x - w // 2 + int((w - 1) * frac), y + 2], fill=(80, 210, 90))


def scene(key, cam, chars, tags=(), zone='', msgs=(), hp=1.0, nums=(), hpbars=()):
    mv = SCENE_CACHE.setdefault(key, MV.MapV(key))
    im, (x0, y0) = mv.render(cam, chars)
    for (mx, my, txt, col) in tags: T(im, (mx // 2 - x0, my // 2 - y0), txt, col, True)
    for (mx, my, frac) in hpbars: mini_hp(im, mx // 2 - x0, my // 2 - y0, frac)
    for (mx, my, txt, col) in nums: T(im, (mx // 2 - x0, my // 2 - y0), txt, col, True, 2)
    hud(im, zone, hp, msgs)
    return im


SCENE_CACHE = {}


def town(f=0):
    mv = SCENE_CACHE.setdefault('town', MV.MapV('town')); m = mv.m
    chars = [(spr('heroi', 'idle', 'up')[(f // 2) % 12], 470, 776), (spr('guarda', 'idle', 'down')[(f // 2) % 12], 540, 668), (spr('aldeao', 'idle', 'down')[(f // 2) % 12], 393, 776), (spr('mercador', 'idle', 'down')[(f // 2) % 12], 330, 560)]
    tags = [(470, 776 - 80, 'Teste Nv.1', (120, 220, 255)), (540, 668 - 80, 'Capitao Ruvel', (180, 230, 140)), (393, 776 - 80, 'Aldeao', CREAM), (330, 560 - 80, 'Mercador', GOLD)]
    return scene('town', (450, 640), chars, tags, 'BRUMAVALE', ['Bem-vindo, Teste!'])


def forest(f=0):
    mv = SCENE_CACHE.setdefault('zone1', MV.MapV('zone1')); sx, sy = mv.m['start']
    mobs = [('javali', 'right', sx - 90, sy - 300, .8), ('lobo', 'right', sx + 70, sy - 230, 1.0), ('rato', 'down', sx + 20, sy - 360, 1.0), ('javali', 'down', sx - 30, sy - 180, 1.0)]
    chars = [(spr(n, 'idle', v)[(f // 2 + i * 3) % len(spr(n, 'idle', v))], x, y) for i, (n, v, x, y, h) in enumerate(mobs)] + [(spr('heroi', 'idle', 'up')[(f // 2) % 12], sx, sy - 110)]
    return scene('zone1', (sx, sy - 250), chars, [(sx, sy - 190, 'Teste Nv.1', (120, 220, 255))], 'FLORESTA', ['Voce entrou na Floresta.'], hpbars=[(x, y - 66 if v == 'down' else y - 50, h) for (n, v, x, y, h) in mobs], nums=[(mobs[0][2], mobs[0][3] - 70, '38', (255, 224, 74))])


def goblins(f=0):
    mv = SCENE_CACHE.setdefault('zone1_gob', MV.MapV('zone1_gob')); sx, sy = mv.m['start']
    mobs = [('goblin', 'down', sx - 80, sy - 280, 1.0), ('goblin', 'down', sx + 60, sy - 310, .7), ('ogro', 'down', sx + 10, sy - 410, 1.0)]
    chars = [(spr(n, 'idle', v)[(f // 2 + i * 3) % 12], x, y) for i, (n, v, x, y, h) in enumerate(mobs)] + [(spr('heroi', 'idle', 'up')[(f // 2) % 12], sx, sy - 110)]
    return scene('zone1_gob', (sx, sy - 260), chars, [(sx, sy - 190, 'Teste Nv.1', (120, 220, 255))], 'FLORESTA GOBLIN', ['Goblins a frente!'], hpbars=[(x, y - 66, h) for (n, v, x, y, h) in mobs])


def crypt(f=0):
    mv = SCENE_CACHE.setdefault('zone_cripta', MV.MapV('zone_cripta')); sx, sy = mv.m['start']
    mobs = [('esqueleto', 'down', sx - 70, sy - 290, .6), ('cultista', 'down', sx + 80, sy - 330, 1.0), ('zumbi', 'down', sx + 10, sy - 400, 1.0), ('esqueleto', 'down', sx - 10, sy - 220, .9)]
    chars = [(spr(n, 'idle', v)[(f // 2 + i * 3) % 12], x, y) for i, (n, v, x, y, h) in enumerate(mobs)] + [(spr('heroi', 'idle', 'up')[(f // 2) % 12], sx, sy - 110)]
    return scene('zone_cripta', (sx, sy - 250), chars, [(sx, sy - 190, 'Teste Nv.1', (120, 220, 255))], 'CATACUMBAS', ['Voce entrou na Cripta.'], hpbars=[(x, y - 66, h) for (n, v, x, y, h) in mobs], nums=[(mobs[0][2], mobs[0][3] - 72, '38', (255, 224, 74))])


def cell_row(im, items, x0, y0, cols=6, rows=8, pitch=28):
    d = ImageDraw.Draw(im)
    for i in range(cols * rows):
        x = x0 + (i % cols) * pitch; y = y0 + (i // cols) * pitch
        if i < len(items):
            n, r, pc, up, ar = items[i]; ic = IC.get(*(n.split(':') if ':' in n else (n,)))
            im.alpha_composite(IC.cell(ic, r, 29, pc, up, ar), (x, y))
        else: d.rectangle([x, y, x + 28, y + 28], fill=(14, 12, 20), outline=(34, 30, 44))


def tabs(im, d, on):
    panel(d, (4, 34, 191, 392)); d.rectangle([5, 35, 190, 56], fill=(24, 20, 40)); T(im, (12, 42), 'PERSONAGEM', GOLD, False, 2); d.rectangle([170, 38, 186, 54], outline=GOLD_D); T(im, (178, 42), 'X', CREAM, True, 2)
    for i, t in enumerate(('EQUIPAMENTO', 'MOCHILA', 'ATRIBUTOS')):
        x0 = 5 + i * 62; d.rectangle([x0, 58, x0 + 62, 74], fill=(34, 28, 52) if i == on else (18, 14, 30), outline=GOLD_D)
        if i == on: d.line([x0, 74, x0 + 62, 74], fill=GOLD)
        T(im, (x0 + 31, 63), t, GOLD if i == on else CREAM, True)


def menu_char():
    im = Image.new('RGBA', (NW, NH), (12, 10, 20, 255)); d = ImageDraw.Draw(im); tabs(im, d, 0)
    T(im, (97, 82), 'TESTE', GOLD, True, 2); T(im, (97, 96), 'Guerreiro - Nivel 1', DIM, True)
    left = [('helm', 'incomum', 24, 0, 'up'), ('armor', 'raro', 61, 0, None), ('gloves', 'comum', 9, 0, None), ('boots', 'incomum', 17, 0, 'up')]; right = [('espada_aco', 'raro', 88, 3, None), ('shield', 'raro', 52, 0, None), ('amulet', 'lendario', 143, 0, 'up'), ('ring', 'epico', 96, 0, None)]
    for i, (n, r, pc, up, ar) in enumerate(left): im.alpha_composite(IC.cell(IC.get(n), r, 29, pc, up, ar), (8, 108 + i * 35))
    for i, (n, r, pc, up, ar) in enumerate(right): im.alpha_composite(IC.cell(IC.get(n), r, 29, pc, up, ar), (158, 108 + i * 35))
    d.rectangle([42, 106, 154, 244], fill=(18, 14, 30), outline=GOLD_D)
    hs = spr('heroi', 'idle', 'down')[0]; bb = hs.getbbox(); big = hs.crop(bb).resize(((bb[2] - bb[0]) * 2, (bb[3] - bb[1]) * 2), Image.NEAREST)
    ov = Image.new('RGBA', (NW, NH), (0, 0, 0, 0)); ImageDraw.Draw(ov).ellipse([62, 224, 132, 238], fill=(0, 0, 0, 120)); im.alpha_composite(ov); im.alpha_composite(big, (97 - big.width // 2, 232 - big.height))
    d.rectangle([10, 252, 184, 274], fill=(34, 26, 14), outline=GOLD); T(im, (18, 259), 'PODER DE COMBATE', CREAM); T(im, (176, 258), '147', GOLD, True, 2) if False else T(im, (150, 258), '147', GOLD, False, 2)
    stats = [('VIDA', '135', (240, 90, 100)), ('ATAQUE', '14', (255, 150, 80)), ('DEFESA', '9', (110, 180, 255)), ('CRITICO', '10%', (255, 220, 90)), ('EMPURRAO', '30%', (190, 130, 255)), ('VELOCIDADE', '70', (110, 230, 190))]
    for i, (n, v, c) in enumerate(stats):
        x = 12 + (i % 2) * 88; y = 288 + (i // 2) * 24
        d.rectangle([x - 4, y + 1, x - 2, y + 3], fill=c); T(im, (x, y), n, DIM); T(im, (x + 76 - pxfont.width(v, 2), y + 9 - 4), v, c, False, 2); d.line([x - 4, y + 19, x + 76, y + 19], fill=(38, 32, 54))
    return im


def menu_bag():
    im = Image.new('RGBA', (NW, NH), (12, 10, 20, 255)); d = ImageDraw.Draw(im); tabs(im, d, 1)
    for i, (ic, v, c) in enumerate((('coin', '1240', GOLD), ('gem', '12', (120, 210, 255)), ('amulet', '3', (200, 140, 255)))):
        x0 = 8 + i * 60; d.rectangle([x0, 82, x0 + 56, 98], fill=(18, 14, 30), outline=GOLD_D); im.alpha_composite(IC.get(ic).crop((1, 1, 15, 15)), (x0 + 2, 83)); T(im, (x0 + 20, 87), v, c, False, 1)
    d.polygon([(10, 110), (14, 106), (18, 110), (14, 114)], fill=GOLD); T(im, (24, 106), 'MOCHILA', GOLD, False, 2); T(im, (184 - pxfont.width('28/100'), 108), '28/100', DIM); d.line([8, 122, 186, 122], fill=GOLD_D)
    items = [('espada_ferro', 'comum', 31, 0, None), ('katana', 'epico', 212, 0, 'up'), ('machado', 'incomum', 74, 0, None), ('cajado_arcano', 'epico', 188, 2, 'dn'), ('arco_longo', 'raro', 129, 0, None), ('helm', 'incomum', 24, 0, 'up'),
             ('armor', 'raro', 91, 1, None), ('shield', 'raro', 77, 0, 'dn'), ('gloves', 'comum', 12, 0, None), ('boots', 'incomum', 29, 0, 'up'), ('ring', 'epico', 160, 0, None), ('amulet', 'lendario', 305, 0, 'up'),
             ('potion:red', 'comum', None, 0, None), ('potion:red', 'comum', None, 0, None), ('potion:blue', 'comum', None, 0, None), ('potion:green', 'incomum', None, 0, None), ('scroll', 'comum', None, 0, None), ('gem', 'raro', None, 0, None),
             ('bone', 'comum', None, 0, None), ('bone', 'comum', None, 0, None), ('leather', 'comum', None, 0, None), ('herb', 'comum', None, 0, None), ('ore', 'incomum', None, 0, None), ('key', 'epico', None, 0, None),
             ('chest', 'raro', None, 0, None), ('coin', 'comum', None, 0, None), ('martelo_sagrado', 'lendario', 410, 0, 'up'), ('espada_chamas', 'lendario', 388, 4, None)]
    cell_row(im, items, 9, 128, 6, 8, 30)
    return im


def save(im, name): im.convert('RGB').resize((NW * SC, NH * SC), Image.NEAREST).save(os.path.join(OUT, name))


def fight_gif():
    frames = []; nA = len(spr('heroi', 'attack', 'up'))
    mv = SCENE_CACHE.setdefault('zone_cripta', MV.MapV('zone_cripta')); sx, sy = mv.m['start']
    for f in range(60):
        ph = f % 30
        hk, hi = ('attack', ph % nA) if ph < nA else ('idle', f)
        hy = sy - 110 - (6 if hk == 'attack' and 6 < ph < 12 else 0)
        mobs = [('esqueleto', 'down', sx - 30, sy - 190), ('cultista', 'down', sx + 80, sy - 250), ('zumbi', 'down', sx - 70, sy - 300)]
        chars = [(spr(n, 'idle', v)[(f // 2 + i * 3) % 12], x, y) for i, (n, v, x, y) in enumerate(mobs)] + [(spr('heroi', hk, 'up')[hi % len(spr('heroi', hk, 'up'))], sx, hy)]
        nums = [(mobs[0][2], mobs[0][3] - 72 - (ph - 10) * 2, '38', (255, 224, 74))] if 10 <= ph <= 22 else []
        frames.append(scene('zone_cripta', (sx, sy - 250), chars, [], 'CATACUMBAS', ['Esqueleto atingido!'], nums=nums, hpbars=[(x, y - 66, [.6, 1, 1][i]) for i, (n, v, x, y) in enumerate(mobs)]))
    big = [x.convert('RGB').resize((NW * SC, NH * SC), Image.NEAREST) for x in frames]
    p = big[0].quantize(colors=240, method=Image.MEDIANCUT, dither=Image.NONE); q = [b.quantize(palette=p, dither=Image.NONE) for b in big]
    q[0].save(os.path.join(OUT, 'jogo_pixel2_combate.gif'), save_all=True, append_images=q[1:], duration=60, loop=0, disposal=1)


if __name__ == '__main__':
    save(town(), 'jogo2_cidade.png'); save(forest(), 'jogo2_floresta.png'); save(goblins(), 'jogo2_goblins.png'); save(crypt(), 'jogo2_cripta.png'); save(menu_char(), 'jogo2_personagem.png'); save(menu_bag(), 'jogo2_mochila.png'); fight_gif(); print('ok')
