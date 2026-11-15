import sys; sys.path.insert(0, '.')
import fauna, fauna2, humano, creature as CRE, export_atlas as X, pxfont
from PIL import Image, ImageDraw
OUTD = '/home/user/neon-wars/lendas-de-taverna/mmo/proto_pixel'
U = lambda **ap: dict(kind='c', ap=ap)
EXTRA = {
 'bandido': U(cls='rogue', hat='bandana', skin='escura', clothes='bronze', weapon='adaga_ferro', weapon2='adaga_ferro'),
 'carnical': dict(kind='e', name='zumbi'),
 'cav_caido': U(cls='warrior', skin='osso', hair='g_osso', eyes='oco', hat='rusty_helm', outfit='mail', clothes='aco', metal='ferro', weapon='espada_larga', bulk=1, tn_off=1),
 'mumia': U(cls='warrior', skin='palida', hair='g_zumbi', eyes='oco', hat='bandage', outfit='cloth', clothes='branco', noweapon=1, arms_fwd=1),
 'necro': dict(kind='e', name='cultista'),
 'goblin': dict(kind='e', name='goblin'), 'goblin_x': dict(kind='e', name='goblin_x'),
 'afogado': U(cls='warrior', skin='esverdeada', hair='g_zumbi', eyes='oco', hat='bandage', outfit='cloth', clothes='azul', noweapon=1, arms_fwd=1),
}
AREAS = {
 'floresta_goblins': ('FLORESTA DOS GOBLINS (Grunk)', [('GOBLIN', 'goblin'), ('XAMA', 'goblin_x'), ('SAPADOR', 'goblin_sapador'), ('COGUMELO', 'cogumelo'), ('ARANHA', 'aranha'), ('LOBO', 'lobo')]),
 'catacumbas': ('CATACUMBAS (Morvath)', [('CARNICAL', 'carnical'), ('NECROMANTE', 'necro'), ('CAV CAIDO', 'cav_caido'), ('MUMIA', 'mumia'), ('ARANHA', 'aranha')]),
 'floresta_brumavale': ('FLORESTA DE BRUMAVALE (Gorgash)', [('OGRINHO', 'ogrinho'), ('OGRO LENH', 'ogro_lenhador'), ('GNOLL', 'gnoll'), ('TRONCO', 'tronco'), ('HARPIA', 'harpia'), ('BANDIDO', 'bandido'), ('JAVALI', 'javali')]),
 'esgotos': ('ESGOTOS (Rei dos Ratos)', [('RATO', 'rato'), ('HOMEM-RATO', 'ratkin'), ('LADRAO', 'ladrao_esgoto'), ('CULTISTA', 'cultista_lodo'), ('SAPO', 'sapo'), ('COBRA', 'cobra'), ('LODO', 'slime'), ('BARATA', 'barata'), ('AFOGADO', 'afogado')]),
}


def spr(k, view):
    if k in humano.SPECS: return humano.draw(humano.SPECS[k], view, .6)
    if k in fauna.DRAW: return fauna.DRAW[k](view, .6)
    if k == 'slime': return CRE.draw('slime', view)
    return X.frames(EXTRA[k], 'idle', view)[0].convert('RGBA')


def card(nm, k, bg):
    c = Image.new('RGBA', (60, 156), bg); d = ImageDraw.Draw(c); d.rectangle([0, 0, 59, 155], outline=(120, 100, 60, 255))
    for view, yb in (('right', 50), ('down', 101), ('up', 152)):
        im = spr(k, view); b = im.getbbox()
        if not b: continue
        b = im.crop(b); c.alpha_composite(b, (30 - b.width // 2, yb - b.height))
    pxfont.text(c, (30, 1), nm, (240, 226, 190), center=True); return c


for key, (title, items) in AREAS.items():
    n = len(items); S = Image.new('RGBA', (64 * n + 4, 176), (24, 18, 32, 255))
    pxfont.text(S, (4, 3), title, (255, 214, 120))
    for i, (nm, k) in enumerate(items): S.alpha_composite(card(nm, k, (52, 70, 56, 255)), (4 + i * 64, 14))
    S.resize((S.width * 4, S.height * 4), Image.NEAREST).save(f'{OUTD}/bestiario_{key}.png'); print(key)
