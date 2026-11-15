import sys; sys.path.insert(0, '.')
import fauna as F, creature as CRE, pxfont
from PIL import Image, ImageDraw
OUTD = '/home/user/neon-wars/lendas-de-taverna/mmo/proto_pixel'


def card(name, im_side, im_front, bg):
    c = Image.new('RGBA', (60, 80), bg); d = ImageDraw.Draw(c)
    d.rectangle([0, 0, 59, 79], outline=(120, 100, 60, 255))
    side = im_side.crop(im_side.getbbox()); front = im_front.crop(im_front.getbbox()) if im_front else None
    c.alpha_composite(side, (30 - side.width // 2, 41 - side.height))
    if front: c.alpha_composite(front, (30 - front.width // 2, 76 - front.height))
    pxfont.text(c, (30, 2), name, (240, 226, 190), center=True)
    return c


def sheet(items, bg, fn):
    S = Image.new('RGBA', (60 * len(items) + 4 * (len(items) + 1), 88), (24, 18, 32, 255))
    for i, (nm, kd) in enumerate(items):
        if kd in F.DRAW: a, b = F.DRAW[kd]('right', .6), F.DRAW[kd]('down', .6)
        else: a, b = CRE.draw(kd, 'right'), None
        S.alpha_composite(card(nm, a, b, bg), (4 + i * 64, 4))
    S = S.resize((S.width * 4, S.height * 4), Image.NEAREST); S.save(f'{OUTD}/{fn}'); print(fn, S.size)


sheet([('JAVALI', 'javali'), ('LOBO', 'lobo'), ('URSO', 'urso'), ('COBRA', 'cobra'), ('ARANHA', 'aranha')], (52, 78, 52, 255), 'candidatos_floresta.png')
sheet([('RATO', 'rato'), ('BARATA', 'barata'), ('SAPO', 'sapo'), ('COBRA', 'cobra'), ('ARANHA', 'aranha')], (46, 58, 52, 255), 'candidatos_esgoto.png')
