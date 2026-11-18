#!/usr/bin/env python3
"""Monta os ícones de item (assets/ico/i_*.png, 96px) a partir de packs CC0 (Idylwild's Armory/Arsenal/Arcanum, 32x32, e
"496 pixel art icons" da OpenGameArt, 34x34). Fontes copiadas em assets/ico_src/. Itens sem equivalente nos packs
(alaúde, flauta, chapéu, coroa...) continuam vindo de tools/mmo/pxengine/data/icons_px.py.
Uso: python3 import_icons.py [sheet saida.png]"""
import os, sys
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
SRC = os.path.join(ROOT, 'assets', 'ico_src'); OUT = os.path.join(ROOT, 'assets', 'ico')
IW = lambda n: ('idylwild', n); G4 = lambda n: ('oga496', n)
MAP = {
    'espada': IW('sword3'), 'espada_curta': IW('dagger3'), 'florete': IW('sword5'), 'adaga': IW('dagger2'), 'machado': IW('axe2'), 'martelo': IW('hammer1'),
    'maca': IW('mace1'), 'cajado': IW('staff3'), 'cetro': IW('wand2'), 'cetro_sagrado': IW('mace2'), 'varinha': IW('wand1'), 'arco': IW('bow1'), 'arco_longo': IW('bow3'),
    'aljava': IW('arrow3'), 'elmo': IW('close_helmet'), 'elmo_sagrado': IW('platemail_helmet'), 'capuz': IW('cloth_hood'), 'boina': IW('leather_cap'), 'cornos': IW('horned_helmet'),
    'chapeu': G4('C_Hat01'), 'couraca': IW('platemail'), 'cota': IW('chainmail_jacket'), 'colete': IW('leather_jacket'), 'manto': IW('cloak'), 'tunica': IW('cloth_robe'),
    'botas': IW('leather_boots'), 'grevas': IW('greaves'), 'sandalias': IW('cloth_shoes'), 'colar': IW('tile048'), 'pingente': IW('tile049'), 'talisma': IW('tile047'),
    'luvas': IW('leather_gloves'), 'luvas_finas': IW('cloth_gloves'), 'manoplas': IW('gauntlets'), 'manoplas_leves': IW('chainmail_gloves'),
    'escudo': IW('iron_buckler'), 'escudog': IW('tower_shield'), 'escudo_sagrado': IW('kite_shield'),
    'livro': IW('grimoire_closed'), 'orbe': IW('crystal_ball'), 'livro_cancoes': IW('rotulus_unfurled'), 'gema': IW('crystal_blue'),
    'bracadeira': IW('leather_bracers'), 'bracelete': IW('iron_bracers'), 'anel': IW('gold_ring'),
}
# ícones de interface/materiais (assets/ui-icons): chave = arquivo, valor = (fonte, tamanho de saída, matiz opcional em graus)
UI = {'health-potion': (IW('potion_full_1'), 64, None), 'coins': (G4('I_GoldCoin'), 64, None), 'gems': (G4('I_Ruby'), 64, None),
      'ni_pocao': (IW('potion_full_1'), 96, None), 'ni_pmaior': (IW('potion_full_3'), 64, None),
      'ni_eforca': (IW('potion_full_1'), 64, 28), 'ni_edefesa': (IW('potion_full_3'), 64, None), 'ni_esorte': (IW('potion_full_1'), 64, 55), 'ni_evigor': (IW('potion_full_2'), 64, None),
      'ni_ferro': (IW('iron_ingot'), 64, None), 'ni_runa': (IW('runestone_water'), 64, None), 'ni_cristal': (IW('crystal_purple'), 64, None),
      'ni_livro': (IW('grimoire_closed'), 64, None), 'ni_moedas': (G4('I_GoldCoin'), 64, None)}
def hue(im, deg):
    import colorsys
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if a == 0: continue
            h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
            if s > .3: r, g, b = [int(c * 255) for c in colorsys.hsv_to_rgb((h + deg / 360) % 1, s, v)]; px[x, y] = (r, g, b, a)
    return im
def load(k):
    d, n = MAP[k]; return Image.open(os.path.join(SRC, d, n + '.png')).convert('RGBA')
def build(k):
    im = load(k); w, h = im.size; S = 96
    sc = max(1, S // max(w, h)); big = im.resize((w * sc, h * sc), Image.NEAREST)
    c = Image.new('RGBA', (S, S), (0, 0, 0, 0)); c.alpha_composite(big, ((S - big.width) // 2, (S - big.height) // 2)); return c
if __name__ == '__main__':
    if sys.argv[1:2] == ['sheet']:
        ks = list(MAP); cols = 9; Sx = Image.new('RGBA', (cols * 100, ((len(ks) + cols - 1) // cols) * 100), (20, 16, 28, 255))
        for i, k in enumerate(ks): Sx.alpha_composite(build(k), ((i % cols) * 100 + 2, (i // cols) * 100 + 2))
        Sx.save(sys.argv[2])
    else:
        for k in MAP: build(k).save(os.path.join(OUT, f'i_{k}.png'))
        UID = os.path.join(ROOT, 'assets', 'ui-icons')
        for k, ((d, n), S, hu) in UI.items():
            im = Image.open(os.path.join(SRC, d, n + '.png')).convert('RGBA')
            if hu: im = hue(im, hu)
            w, h = im.size; sc = max(1, S // max(w, h)); big = im.resize((w * sc, h * sc), Image.NEAREST)
            c = Image.new('RGBA', (S, S), (0, 0, 0, 0)); c.alpha_composite(big, ((S - big.width) // 2, (S - big.height) // 2)); c.save(os.path.join(UID, k + '.png'))
        print(len(MAP), 'ícones de item e', len(UI), 'de interface gerados')
        print(len(MAP), 'ícones gerados')
