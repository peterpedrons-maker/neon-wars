import sys; sys.path.insert(0, '.')
import export_atlas as X, pxfont
from PIL import Image, ImageDraw
OUTD = '/home/user/neon-wars/lendas-de-taverna/mmo/proto_pixel'
U = lambda **ap: dict(kind='c', ap=ap)
FOREST = [('BANDIDO', U(cls='rogue', hat='hood', clothes='bronze', weapon='adaga_ferro', weapon2='adaga_ferro')),
          ('DRUIDA', U(cls='mage', hat='none', hair='verde', clothes='verde', outfit='robe', weapon='cajado_natureza')),
          ('LENHADOR', U(cls='warrior', hat='none', outfit='cloth', clothes='laranja', weapon='machado', bulk=1, tn_off=1)),
          ('CACADOR', U(cls='archer', hat='cap', clothes='verde', weapon='arco_curto')),
          ('ESPANTALHO', U(cls='warrior', skin='zumbi', hair='g_zumbi', eyes='brasa', hat='bandage', outfit='cloth', clothes='bronze', noweapon=1, arms_fwd=1))]
SEWER = [('LADRAO', U(cls='rogue', hat='hood', clothes='preto', weapon='adaga_veneno', weapon2='adaga_veneno')),
         ('ALQUIMISTA', U(cls='mage', hat='none', hair='verde', clothes='verde', outfit='robe', weapon='cajado_fogo')),
         ('AFOGADO', dict(kind='e', name='zumbi')),
         ('CULTISTA', U(cls='mage', hat='hood', outfit='robe', clothes='verde', skin='palida', eyes='oco', weapon='cajado_caveira')),
         ('FAXINEIRO', U(cls='warrior', hat='none', outfit='cloth', clothes='azul', weapon='maca_ferro', bulk=1))]


def card(nm, u, bg):
    c = Image.new('RGBA', (60, 80), bg); d = ImageDraw.Draw(c); d.rectangle([0, 0, 59, 79], outline=(120, 100, 60, 255))
    for view, yb in (('right', 41), ('down', 76)):
        try: im = X.frames(u, 'idle', view)[0].convert('RGBA')
        except Exception as e: print(nm, e); continue
        b = im.crop(im.getbbox()); c.alpha_composite(b, (30 - b.width // 2, yb - b.height))
    pxfont.text(c, (30, 2), nm, (240, 226, 190), center=True); return c


for items, bg, fn in ((FOREST, (52, 78, 52, 255), 'candidatos_humanoides_floresta.png'), (SEWER, (46, 58, 52, 255), 'candidatos_humanoides_esgoto.png')):
    S = Image.new('RGBA', (64 * len(items) + 4, 88), (24, 18, 32, 255))
    for i, (nm, u) in enumerate(items): S.alpha_composite(card(nm, u, bg), (4 + i * 64, 4))
    S.resize((S.width * 4, S.height * 4), Image.NEAREST).save(f'{OUTD}/{fn}'); print(fn)
