#!/usr/bin/env python3
"""Mockup do JOGO ATUAL (Hearthblade) inteiro em pixel art retro: cidade, dungeon (Cripta), floresta, menus, HUD, icones, inimigos.
Formato real: celular em pe, nativo 130x282 (x3 = 390x846). Tudo por codigo."""
import math, os, random
from PIL import Image, ImageDraw
import chibi as C
import icons_pixel as IC
import pxfont


def label(im, xy, txt, col=(240, 226, 190), center=False): pxfont.text(im, xy, txt, col, center)
from teste_clareira import OUT

NW, NH, SC = 130, 282, 3
GOLD = (200, 160, 74); GOLD_D = (110, 80, 40); BG = (16, 14, 28); CREAM = (240, 226, 190)

ENEMY = {
    'goblin': dict(cls='warrior', skin='goblin', hair='g_goblin', eyes='amarelo', hat='gob_ears', outfit='cloth', clothes='bronze', weapon='facao'),
    'esqueleto': dict(cls='warrior', skin='osso', hair='g_osso', eyes='oco', hat='none', outfit='mail', metal='ferro', clothes='preto', weapon='espada_ferro'),
    'javali': dict(cls='warrior', skin='javali', hair='g_javali', eyes='brasa', hat='boar', outfit='cloth', clothes='bronze', weapon='machado'),
    'rato': dict(cls='warrior', skin='rato', hair='g_rato', eyes='oco', hat='rat_ears', outfit='cloth', clothes='preto', weapon='adaga_ferro'),
    'zumbi': dict(cls='warrior', skin='zumbi', hair='g_zumbi', eyes='oco', hat='none', outfit='cloth', clothes='verde', noweapon=1),
    'ogro': dict(cls='warrior', skin='ogro', hair='g_ogro', eyes='brasa', hat='none', outfit='mail', metal='ferro', clothes='bronze', weapon='maca_ferro'),
    'cultista': dict(cls='mage', skin='palida', hair='g_zumbi', eyes='oco', hat='hood', outfit='robe', clothes='preto', weapon='cajado_caveira'),
    'heroi': dict(cls='warrior', hat='helm', outfit='mail', metal='aco', clothes='aco', weapon='espada_aco'),
    'guarda': dict(cls='warrior', skin='goblin', hair='g_goblin', eyes='amarelo', hat='gob_ears', outfit='mail', metal='aco', clothes='aco', weapon='espada_ferro'),
    'aldeao': dict(cls='archer', hat='none', outfit='cloth', noweapon=1),
    'mercador': dict(cls='cleric', hat='none', outfit='robe', clothes='dourado', noweapon=1),
}
_cache = {}


def spr(name, kind='idle', view='down', dense=2):
    k = (name, kind, view)
    if k not in _cache:
        ap = ENEMY[name]; _cache[k] = [f[0] for f in C.anim(view, kind, ap['cls'], None, ap, dense=dense)]
    return _cache[k]


def flip(im): return im.transpose(Image.FLIP_LEFT_RIGHT)


def put(im, spr_, feet, anchor=(36, 38)): im.alpha_composite(spr_, (int(feet[0] - anchor[0]), int(feet[1] - anchor[1])))


def shadow(im, x, y, rx=10, ry=3, a=90):
    ov = Image.new('RGBA', im.size, (0, 0, 0, 0)); ImageDraw.Draw(ov).ellipse([x - rx, y - ry, x + rx, y + ry], fill=(0, 0, 0, a)); im.alpha_composite(ov)


def panel(d, box, fill=BG, border=GOLD, studs=True):
    x0, y0, x1, y1 = box
    d.rectangle([x0, y0, x1, y1], fill=fill); d.rectangle([x0, y0, x1, y1], outline=GOLD_D); d.rectangle([x0 + 1, y0 + 1, x1 - 1, y1 - 1], outline=border)
    if studs:
        for (x, y) in ((x0, y0), (x1, y0), (x0, y1), (x1, y1)): d.rectangle([x - 1, y - 1, x + 1, y + 1], fill=border)


def bar(d, x, y, w, frac, col, h=3):
    d.rectangle([x - 1, y - 1, x + w, y + h], fill=(10, 6, 16)); d.rectangle([x, y, x + int((w - 1) * frac), y + h - 1], fill=col)
    d.line([x, y, x + int((w - 1) * frac), y], fill=tuple(min(255, c + 60) for c in col))


def hud(im, zone=None, hp=1.0, msgs=(), quest=True, boss=None):
    d = ImageDraw.Draw(im)
    panel(d, (3, 3, 58, 22))
    d.rectangle([5, 5, 19, 19], fill=(50, 26, 26), outline=GOLD)
    hs = spr('heroi')[0].crop((20, 6, 52, 26)).resize((14, 14), Image.NEAREST); im.alpha_composite(hs, (5, 5))
    label(im, (23, 4), 'TESTE', CREAM); bar(d, 22, 14, 34, hp, (210, 50, 50), 4)
    d.rectangle([16, 16, 22, 22], fill=(200, 150, 40), outline=(120, 80, 20)); label(im, (17, 14), '1', (30, 20, 10))
    if zone:
        label(im, (111, 3), zone, GOLD, center=True)
        panel(d, (95, 12, 126, 40)); d.rectangle([98, 15, 123, 37], fill=(10, 10, 22))
        for (x0, y0, x1, y1) in ((102, 20, 120, 24), (108, 26, 114, 36)): d.rectangle([x0, y0, x1, y1], fill=(38, 34, 60))
        d.point([111, 31], fill=(255, 220, 90))
    if quest:
        panel(d, (80, 44, 127, 70), fill=(16, 14, 28)); label(im, (84, 46), 'MISSOES', GOLD); label(im, (84, 54), 'Primeiros', CREAM); label(im, (84, 60), 'passos 0/8', (170, 160, 150))
    for i, t in enumerate(('PERS', 'HABIL', 'DIARIO', 'SOCIAL')):
        y = 186 + i * 17
        panel(d, (112, y, 127, y + 14), fill=(20, 16, 34)); label(im, (119, y + 3), t[:3], CREAM, center=True)
    for i, m in enumerate(list(msgs)[-3:]): label(im, (3, 230 + i * 8), m[:23], CREAM if 'Aviso' not in m else (255, 190, 120))
    d.ellipse([6, 240, 34, 268], outline=GOLD_D, fill=(22, 16, 30)); d.ellipse([14, 248, 26, 260], fill=GOLD)
    panel(d, (36, 262, 126, 279), fill=(16, 12, 26))
    for i in range(6):
        x = 39 + i * 14; d.rectangle([x, 264, x + 12, 277], fill=(22, 16, 34), outline=GOLD if i in (0, 4, 5) else GOLD_D)
    im.alpha_composite(IC.get('espada_aco').crop((1, 1, 15, 15)), (39, 264)); label(im, (53, 266), '2', (150, 130, 100)); label(im, (67, 266), '3', (150, 130, 100))
    im.alpha_composite(IC.get('potion', 'red').crop((2, 2, 14, 14)), (81, 265)); im.alpha_composite(IC.get('boots').crop((1, 1, 14, 14)), (95, 265))
    if boss:
        label(im, (65, 2), boss[0], CREAM, center=True); d.rectangle([3, 11, 126, 16], fill=(14, 8, 16), outline=GOLD); d.rectangle([4, 12, 4 + int(121 * boss[1]), 15], fill=(205, 40, 40))


def mini_hp(im, x, y, frac, w=14):
    d = ImageDraw.Draw(im); d.rectangle([x - w // 2 - 1, y - 1, x + w // 2 + 1, y + 2], fill=(10, 6, 16)); d.rectangle([x - w // 2, y, x - w // 2 + int((w - 1) * frac), y + 1], fill=(80, 210, 90))


def tag(im, x, y, txt, col=CREAM): label(im, (x, y), txt, col, center=True)


# ------------------------------------------------------------------ cenarios
def tree(d, x, y, r=11):
    d.rectangle([x - 2, y - 2, x + 2, y + 8], fill=(80, 52, 30)); d.line([x - 2, y - 2, x - 2, y + 8], fill=(110, 76, 44))
    for (dx, dy, rr, col) in ((0, -8, r, (30, 92, 44)), (-r // 2, -3, r - 3, (36, 108, 50)), (r // 2, -3, r - 3, (30, 92, 44)), (-2, -12, r - 4, (60, 150, 70))):
        d.ellipse([x + dx - rr, y + dy - rr, x + dx + rr, y + dy + rr], fill=col, outline=(18, 60, 30))
    d.ellipse([x - 6, y - 14, x - 1, y - 10], fill=(110, 190, 90))


def house(d, x, y, w=36, h=26, roof=(160, 56, 48)):
    d.rectangle([x, y, x + w, y + h], fill=(206, 186, 150), outline=(80, 56, 36))
    for yy in range(y + 4, y + h, 7): d.line([x + 1, yy, x + w - 1, yy], fill=(184, 162, 126))
    d.polygon([(x - 4, y), (x + w // 2, y - 16), (x + w + 4, y)], fill=roof, outline=(70, 24, 24))
    for k in range(3): d.line([x - 2 + k * 2, y - 2 - k * 4, x + w + 2 - k * 2, y - 2 - k * 4], fill=tuple(max(0, c - 30) for c in roof))
    d.rectangle([x + w // 2 - 4, y + h - 12, x + w // 2 + 4, y + h], fill=(90, 56, 30), outline=(50, 30, 16))
    for wx in (x + 4, x + w - 11):
        d.rectangle([wx, y + 6, wx + 7, y + 14], fill=(250, 214, 110), outline=(80, 56, 36)); d.line([wx + 3, y + 6, wx + 3, y + 14], fill=(80, 56, 36))


def lamp(d, x, y):
    d.rectangle([x - 1, y - 18, x + 1, y], fill=(40, 40, 54)); d.rectangle([x - 3, y - 24, x + 3, y - 18], fill=(255, 210, 110), outline=(60, 50, 40)); d.rectangle([x - 4, y - 26, x + 4, y - 24], fill=(40, 40, 54))


def well(d, x, y):
    d.ellipse([x - 13, y - 4, x + 13, y + 8], fill=(120, 116, 130), outline=(50, 46, 60)); d.ellipse([x - 10, y - 2, x + 10, y + 5], fill=(30, 40, 70))
    for px in (x - 11, x + 10): d.rectangle([px, y - 22, px + 2, y], fill=(86, 56, 30))
    d.polygon([(x - 15, y - 20), (x, y - 30), (x + 15, y - 20)], fill=(150, 72, 44), outline=(70, 30, 20))


def town(f=0):
    im = Image.new('RGBA', (NW, NH), (66, 130, 66, 255)); d = ImageDraw.Draw(im)
    random.seed(4)
    for _ in range(260): x, y = random.randint(0, NW), random.randint(0, NH); d.point([x, y], fill=(84, 154, 78) if (x + y) % 2 else (54, 112, 56))
    for y in range(0, NH, 10):                                           # estrada de pedra
        for x in range(34 + (y // 10 % 2) * 6 - 6, 98, 12):
            d.rectangle([x, y, x + 10, y + 8], fill=(150 + (x * 7 + y) % 20, 144 + (x + y * 3) % 18, 150 + (x * 3) % 16), outline=(104, 100, 112))
    house(d, 4, 44, 34, 26); house(d, 92, 56, 34, 26, roof=(60, 96, 150)); house(d, 8, 112, 30, 22, roof=(150, 110, 40))
    tree(d, 14, 168); tree(d, 118, 150); tree(d, 112, 214); tree(d, 10, 224, 9)
    for fx, fy in ((22, 98), (28, 100), (104, 108), (110, 112), (16, 196), (100, 190)):
        d.rectangle([fx, fy, fx + 1, fy + 1], fill=random.choice([(240, 90, 120), (250, 220, 90), (150, 120, 240)]))
    lamp(d, 38, 128); lamp(d, 92, 128); lamp(d, 38, 214); lamp(d, 92, 214)
    d.rectangle([40, 140, 90, 150], fill=(34, 30, 44), outline=(14, 10, 22)); label(im, (65, 141), 'ZONA SEGURA', GOLD, center=True)
    label(im, (65, 118), 'Entre no portal', CREAM, center=True)
    well(d, 66, 196)
    for (nm, x, y, n, col) in (('guarda', 100, 170, 'Capitao Ruvel', (180, 230, 140)), ('mercador', 40, 96, 'Mercador', GOLD), ('aldeao', 90, 106, 'Aldeao', CREAM)):
        shadow(im, x, y, 9, 3); put(im, spr(nm, 'idle', 'down')[(f // 2) % 12], (x, y)); tag(im, x, y - 38, n, col)
    shadow(im, 62, 228); put(im, spr('heroi', 'idle', 'up')[(f // 2) % 12], (62, 228)); tag(im, 62, 190, 'Teste Nv.1', (120, 220, 255))
    hud(im, 'BRUMAVALE', msgs=['[Sistema] Bem-vindo a Brumavale!'])
    return im


def crypt(f=0, mobs=None, hurt=None, nums=()):
    im = Image.new('RGBA', (NW, NH), (14, 12, 22, 255)); d = ImageDraw.Draw(im)
    for y in range(60, 262, 12):
        for x in range(((y // 12) % 2) * 10 - 10, NW, 20):
            t = (34 + (x * 7 + y * 13) % 9, 36 + (x * 5 + y) % 8, 52 + (x + y * 3) % 9)
            d.rectangle([x, y, x + 18, y + 10], fill=t, outline=(20, 18, 32))
    d.rectangle([0, 0, NW, 59], fill=(26, 24, 42))
    for y in range(18, 59, 8):
        for x in range(((y // 8) % 2) * 8 - 8, NW, 16): d.rectangle([x, y, x + 14, y + 6], fill=(32 + (x + y) % 8, 30 + (y) % 6, 50), outline=(18, 16, 30))
    for tx in (22, 66, 108):
        fl = 2 + int(2 * math.sin(f * .45 + tx)); d.rectangle([tx - 1, 34, tx + 1, 44], fill=(80, 56, 34)); d.ellipse([tx - 4, 26 - fl // 2, tx + 4, 36], fill=(255, 150, 50)); d.ellipse([tx - 2, 29, tx + 2, 35], fill=(255, 235, 140))
        ov = Image.new('RGBA', (NW, NH), (0, 0, 0, 0)); ImageDraw.Draw(ov).ellipse([tx - 26, 20, tx + 26, 80], fill=(255, 170, 70, 26)); im.alpha_composite(ov)
    return im


def forest(f=0):
    im = Image.new('RGBA', (NW, NH), (50, 112, 58, 255)); d = ImageDraw.Draw(im); random.seed(8)
    for _ in range(320): x, y = random.randint(0, NW), random.randint(0, NH); d.point([x, y], fill=(64, 134, 66) if (x + y) % 2 else (40, 92, 48))
    for y in range(0, NH, 3):
        x0 = 52 + int(10 * math.sin(y * .05)); d.rectangle([x0, y, x0 + 26, y + 2], fill=(150, 124, 86) if (y // 3) % 3 else (136, 110, 76))
    for (x, y, r) in ((12, 70, 12), (112, 66, 12), (20, 120, 11), (110, 130, 11), (8, 190, 12), (118, 200, 12), (30, 90, 9), (96, 96, 9)): tree(d, x, y, r)
    for x, y in ((40, 160), (84, 150), (60, 210)): d.ellipse([x - 5, y - 2, x + 5, y + 3], fill=(130, 126, 140), outline=(70, 66, 84))
    return im


def scene_fight(kind='crypt', f=0, hero=('idle', 0), mobs=(), nums=(), flash=None, msgs=(), hp=1.0):
    im = crypt(f) if kind == 'crypt' else forest(f)
    items = []
    for (nm, x, y, view, k, i, hpf) in mobs: items.append((y, nm, x, view, k, i, hpf))
    hk, hi, hx, hy = hero if len(hero) == 4 else (hero[0], hero[1], 60, 200)
    items.append((hy, 'heroi', hx, 'up', hk, hi, None))
    for (y, nm, x, view, k, i, hpf) in sorted(items):
        seq = spr(nm, k, 'up' if view == 'up' else view)
        s = seq[i % len(seq)]
        if nm != 'heroi' and flash and flash == (nm, x): s = Image.blend(s, Image.new('RGBA', s.size, (255, 255, 255, 255)), .7); s.putalpha(seq[i % len(seq)].split()[3])
        shadow(im, x, y + 1); put(im, s, (x, y))
        if hpf is not None: mini_hp(im, x, y - 36, hpf)
    for (x, y, t, c) in nums: label(im, (x, y), t, c, center=True)
    hud(im, 'CRIPTA' if kind == 'crypt' else 'FLORESTA', hp=hp, msgs=msgs or ['[Sistema] Voce entrou na Cripta.'])
    return im


def menu_char():
    im = Image.new('RGBA', (NW, NH), (12, 10, 20, 255)); d = ImageDraw.Draw(im)
    panel(d, (3, 22, 126, 260)); d.rectangle([4, 23, 125, 38], fill=(24, 20, 40)); label(im, (10, 27), 'PERSONAGEM', GOLD); d.rectangle([110, 25, 122, 37], outline=GOLD_D); label(im, (116, 27), 'X', CREAM, center=True)
    for i, (t, on) in enumerate((('EQUIP.', 1), ('MOCHILA', 0), ('ATRIB.', 0))):
        x0 = 4 + i * 40; d.rectangle([x0, 40, x0 + 40, 52], fill=(34, 28, 52) if on else (18, 14, 30), outline=GOLD_D)
        if on: d.line([x0, 52, x0 + 40, 52], fill=GOLD)
        label(im, (x0 + 20, 42), t[:9], GOLD if on else CREAM, center=True)
    label(im, (65, 58), 'TESTE', GOLD, center=True); label(im, (65, 67), 'Guerreiro - Nivel 1', (160, 150, 140), center=True)
    left = [('helm', 'incomum'), ('armor', 'raro'), ('gloves', 'comum'), ('boots', 'incomum')]; right = [('espada_aco', 'raro'), ('shield', 'raro'), ('amulet', 'lendario'), ('ring', 'epico')]
    for i, (n, r) in enumerate(left): im.alpha_composite(IC.slot(IC.get(n), r), (8, 80 + i * 24))
    for i, (n, r) in enumerate(right): im.alpha_composite(IC.slot(IC.get(n), r), (102, 80 + i * 24))
    d.rectangle([32, 78, 98, 172], fill=(18, 14, 30), outline=GOLD_D)
    shadow(im, 65, 150, 14, 4, 120); put(im, spr('heroi', 'idle', 'down')[0].resize((144, 128), Image.NEAREST) if False else spr('heroi', 'idle', 'down')[0], (65, 148))
    im.alpha_composite(spr('heroi', 'idle', 'down')[0].crop((16, 0, 56, 44)).resize((80, 88), Image.NEAREST), (25, 82)) if False else None
    d.rectangle([8, 176, 122, 192], fill=(34, 26, 14), outline=GOLD); label(im, (14, 181), 'PODER DE COMBATE', CREAM); label(im, (116, 180), '147', GOLD, center=False) if False else label(im, (104, 181), '147', GOLD)
    stats = [('VIDA', '135', (240, 90, 100)), ('ATAQUE', '14', (255, 150, 80)), ('DEFESA', '9', (110, 180, 255)), ('CRITICO', '10%', (255, 220, 90)), ('EMPURRAO', '30%', (190, 130, 255)), ('VELOCIDADE', '70', (110, 230, 190))]
    for i, (n, v, c) in enumerate(stats):
        x = 9 + (i % 2) * 60; y = 200 + (i // 2) * 14
        d.rectangle([x - 4, y + 3, x - 2, y + 5], fill=c); label(im, (x, y), n, (150, 142, 134)); label(im, (x + 52 - pxfont.width(v), y), v, c)
        d.line([x - 4, y + 10, x + 52, y + 10], fill=(38, 32, 54))
    return im


def menu_bag():
    im = Image.new('RGBA', (NW, NH), (12, 10, 20, 255)); d = ImageDraw.Draw(im)
    panel(d, (3, 22, 126, 260)); d.rectangle([4, 23, 125, 38], fill=(24, 20, 40)); label(im, (10, 27), 'PERSONAGEM', GOLD); d.rectangle([110, 25, 122, 37], outline=GOLD_D); label(im, (116, 27), 'X', CREAM, center=True)
    for i, (t, on) in enumerate((('EQUIP.', 0), ('MOCHILA', 1), ('ATRIB.', 0))):
        x0 = 4 + i * 40; d.rectangle([x0, 40, x0 + 40, 52], fill=(34, 28, 52) if on else (18, 14, 30), outline=GOLD_D)
        if on: d.line([x0, 52, x0 + 40, 52], fill=GOLD)
        label(im, (x0 + 20, 42), t[:9], GOLD if on else CREAM, center=True)
    items = [('espada_ferro', 'comum'), ('katana', 'epico'), ('machado', 'incomum'), ('cajado_arcano', 'epico'), ('arco_longo', 'raro'), ('helm', 'incomum'), ('armor', 'raro'), ('shield', 'raro'), ('gloves', 'comum'), ('boots', 'incomum'),
             ('ring', 'epico'), ('amulet', 'lendario'), ('potion:red', 'comum'), ('potion:red', 'comum'), ('potion:blue', 'comum'), ('potion:green', 'incomum'), ('scroll', 'comum'), ('gem', 'raro'), ('bone', 'comum'), ('bone', 'comum'),
             ('leather', 'comum'), ('herb', 'comum'), ('ore', 'incomum'), ('key', 'epico'), ('chest', 'raro'), ('coin', 'comum'), ('martelo_sagrado', 'lendario'), ('espada_chamas', 'lendario')]
    for i in range(35):
        x = 6 + (i % 5) * 23; y = 58 + (i // 5) * 23
        ic = None; r = 'comum'
        if i < len(items): n, r = items[i]; ic = IC.get(*(n.split(':') if ':' in n else (n,)))
        im.alpha_composite(IC.slot(ic, r, 21), (x, y))
    label(im, (8, 222), 'MOCHILA 28/100', CREAM); im.alpha_composite(IC.get('coin').crop((2, 2, 14, 14)), (82, 220)); label(im, (96, 222), '1.240', GOLD)
    d.rectangle([8, 236, 62, 252], fill=(34, 26, 14), outline=GOLD); label(im, (35, 241), 'ORGANIZAR', CREAM, center=True)
    d.rectangle([68, 236, 122, 252], fill=(34, 26, 14), outline=GOLD_D); label(im, (95, 241), 'VENDER', (150, 140, 120), center=True)
    return im


def save_png(im, name): im.convert('RGB').resize((NW * SC, NH * SC), Image.NEAREST).save(os.path.join(OUT, name))


def roster():
    names = ['goblin', 'esqueleto', 'javali', 'rato', 'zumbi', 'ogro', 'cultista', 'guarda']
    Wc = 38; fr = []
    for fidx in range(24):
        im = Image.new('RGBA', (Wc * len(names), 36 * 3 + 10), (40, 52, 44, 255)); d = ImageDraw.Draw(im)
        for i, n in enumerate(names):
            for r, (kind, view) in enumerate((('walk', 'down'), ('walk', 'right'), ('attack', 'down'))):
                seq = spr(n, kind, view); s = seq[(fidx if kind == 'walk' else fidx * len(seq) // 24) % len(seq)]
                put(im, s.crop((8, 0, 64, 52)), (i * Wc + Wc // 2 + 0, 36 * r + 40), anchor=(28, 38))
            label(im, (i * Wc + Wc // 2, 36 * 3 + 0), n[:7].upper(), CREAM, center=True)
        fr.append(im.convert('RGB').resize((im.width * 3, im.height * 3), Image.NEAREST))
    p = fr[0].quantize(colors=200, method=Image.MEDIANCUT, dither=Image.NONE); q = [f.quantize(palette=p, dither=Image.NONE) for f in fr]
    q[0].save(os.path.join(OUT, 'inimigos_animados.gif'), save_all=True, append_images=q[1:], duration=60, loop=0, disposal=1)


def fight_gif():
    frames = []; random.seed(2)
    nA = len(spr('heroi', 'attack', 'up'))
    for f in range(80):
        ph = f % 40
        hk, hi = ('attack', ph % nA) if ph < nA else ('idle', f)
        flash = ('esqueleto', 44) if ph in (10, 11) else None
        nums = [(44, 150 - (ph - 10) * 2, '38', (255, 224, 74))] if 10 <= ph <= 20 else []
        dead = f >= 40 and ph >= 14
        mobs = [('esqueleto', 44, 150, 'down', 'idle', f, .6 if f < 40 else .25), ('cultista', 86, 140, 'down', 'idle', f + 3, 1.0), ('zumbi', 66, 120, 'down', 'walk', f, 1.0), ('esqueleto', 100, 168, 'down', 'idle', f + 5, .9)]
        frames.append(scene_fight('crypt', f, (hk, hi, 56, 196), mobs, nums, flash, ['[Sistema] Voce entrou na Cripta.', '[Aviso] Esqueleto atingido!']))
    big = [x.convert('RGB').resize((NW * SC, NH * SC), Image.NEAREST) for x in frames]
    p = big[0].quantize(colors=220, method=Image.MEDIANCUT, dither=Image.NONE); q = [b.quantize(palette=p, dither=Image.NONE) for b in big]
    q[0].save(os.path.join(OUT, 'jogo_pixel_combate.gif'), save_all=True, append_images=q[1:], duration=60, loop=0, disposal=1)


if __name__ == '__main__':
    save_png(town(), 'jogo_pixel_cidade.png'); save_png(menu_char(), 'jogo_pixel_personagem.png'); save_png(menu_bag(), 'jogo_pixel_mochila.png')
    mobs = [('esqueleto', 44, 150, 'down', 'idle', 0, .6), ('cultista', 86, 140, 'down', 'idle', 3, 1.0), ('zumbi', 66, 118, 'down', 'idle', 0, 1.0), ('esqueleto', 100, 170, 'down', 'idle', 2, .9)]
    save_png(scene_fight('crypt', 0, ('idle', 0, 56, 206), mobs, [(44, 112, '38', (255, 224, 74)), (86, 100, '21', (255, 224, 74))]), 'jogo_pixel_cripta.png')
    mobs2 = [('goblin', 40, 130, 'down', 'idle', 0, 1.0), ('goblin', 88, 120, 'down', 'idle', 4, .7), ('javali', 66, 160, 'down', 'idle', 2, 1.0), ('rato', 100, 180, 'down', 'idle', 6, 1.0)]
    save_png(scene_fight('forest', 0, ('idle', 0, 52, 210), mobs2, msgs=['[Sistema] Voce entrou na Floresta.']), 'jogo_pixel_floresta.png')
    roster(); fight_gif(); print('ok')
