#!/usr/bin/env python3
"""Sistema de aparencia + equipamentos (dados): galeria de armas, personalizacao, armaduras por classe e tela de criacao de personagem."""
import os
from PIL import Image, ImageDraw, ImageFont
import chibi as C
from teste_clareira import OUT

FONT = ImageFont.load_default(size=8)
BG = (58, 110, 48)


def label(im, xy, txt, col=(255, 240, 200), center=False):
    d = ImageDraw.Draw(im); d.fontmode = '1'
    x, y = xy
    if center: x = x - int(d.textlength(txt, font=FONT)) // 2
    d.text((x + 1, y + 1), txt, font=FONT, fill=(20, 12, 24))
    d.text((x, y), txt, font=FONT, fill=col)


def sprite(app, view='right', pose=None, kind='attack'):
    cls = app.get('cls', 'warrior')
    return C.anim(view, kind, cls, [pose], app)[0][0]


CLS_OF = {'sword': 'warrior', 'staff': 'mage', 'bow': 'archer', 'dagger': 'rogue', 'mace': 'cleric'}


def weapon_pose(kind, view='right'):
    if kind == 'sword': return dict(tn=3, sw=dict(ang=100, len=12), ar=(1, 0))
    if kind == 'staff': return dict(tn=3, sw=dict(kind='staff', ang=180, orb=1))
    if kind == 'bow': return dict(tn=3, sw=dict(kind='bow', dir=(1, 0), draw=3, arrow=True))
    if kind == 'dagger': return dict(tn=3, sw=dict(kind='dagger', ang=100, len=8), sw2=dict(ang=80, len=8))
    return dict(tn=3, sw=dict(kind='mace', ang=150, len=15))


def weapons_gallery(path, zoom=4, cols=6):
    ids = list(C.WEAPONS)
    cw, ch = 40 * zoom, 44 * zoom + 14
    rows = (len(ids) + cols - 1) // cols
    A = Image.new('RGB', (cw * cols, ch * rows), BG)
    for i, wid in enumerate(ids):
        k = C.WEAPONS[wid]['kind']
        app = dict(cls=CLS_OF[k], weapon=wid)
        if k == 'dagger': app['weapon2'] = wid
        im = sprite(app, 'right', weapon_pose(k))
        im = im.resize((im.width * zoom, im.height * zoom), Image.NEAREST)
        x, y = (i % cols) * cw, (i // cols) * ch
        A.paste(im.convert('RGB'), (x, y), im)
        label(A, (x + cw // 2, y + 44 * zoom), wid.replace('_', ' '), center=True)
    A.save(path)


def customization(path, zoom=3):
    rows = []
    base = dict(cls='warrior')
    p = dict(tn=3, sw=dict(ang=165, len=12, side='r'))
    sets = [
        ('CABELO', [dict(base, hair=h) for h in C.HAIRS]),
        ('PELE', [dict(base, skin=s_) for s_ in C.SKINS]),
        ('OLHOS', [dict(base, eyes=e) for e in C.EYES]),
        ('ROUPA', [dict(base, clothes=c) for c in C.CLOTHES]),
        ('CACHECOL', [dict(base, accent=a) for a in C.ACCENTS]),
        ('CHAPEU', [dict(base, hat=h) for h in ('none', 'wizard', 'cap', 'hood', 'helm', 'circlet', 'crown', 'bandana')]),
    ]
    cw, ch = 40 * zoom, 44 * zoom + 12
    n = max(len(r[1]) for r in sets)
    A = Image.new('RGB', (cw * n, (ch + 12) * len(sets)), BG)
    for r, (name, apps) in enumerate(sets):
        label(A, (4, r * (ch + 12)), name)
        for i, app in enumerate(apps):
            im = sprite(app, 'down', p).resize((40 * zoom, 44 * zoom), Image.NEAREST)
            x, y = i * cw, r * (ch + 12) + 10
            A.paste(im.convert('RGB'), (x, y), im)
            nm = [v for k, v in app.items() if k != 'cls'][0]
            label(A, (x + cw // 2, y + 44 * zoom - 2), str(nm), center=True)
    A.save(path)


def outfits_sheet(path, zoom=4):
    looks = [
        ('GUERREIRO INICIAL', dict(cls='warrior', weapon='espada_ferro'), dict(sw=dict(ang=165, len=12, side='r'))),
        ('GUERREIRO COTA', dict(cls='warrior', outfit='mail', hat='helm', clothes='aco', metal='aco', accent='vermelho', weapon='espada_aco'), dict(sw=dict(ang=165, len=12, side='r'))),
        ('GUERREIRO OURO', dict(cls='warrior', outfit='mail', hat='crown', clothes='dourado', metal='ouro', accent='azul', weapon='espada_dourada'), dict(sw=dict(ang=165, len=12, side='r'))),
        ('MAGO MANTO', dict(cls='mage', weapon='cajado_fogo'), dict(sw=dict(kind='staff', ang=180, orb=1))),
        ('MAGO ARCANO', dict(cls='mage', clothes='azul', hair='branco', weapon='cajado_arcano'), dict(sw=dict(kind='staff', ang=180, orb=2))),
        ('ARQUEIRO', dict(cls='archer', weapon='arco_longo'), dict(sw=dict(kind='bow', dir=(0, 1), draw=2, arrow=False))),
        ('LADINO', dict(cls='rogue', weapon='adaga_veneno', weapon2='adaga_veneno'), dict(sw=dict(kind='dagger', ang=120, len=8), sw2=dict(ang=240, len=8))),
        ('CLERIGO', dict(cls='cleric', weapon='martelo_sagrado'), dict(sw=dict(kind='mace', ang=170, len=15))),
    ]
    cw, ch = 40 * zoom, 44 * zoom + 12
    A = Image.new('RGB', (cw * len(looks), ch * 3), BG)
    for i, (nm, app, p) in enumerate(looks):
        for r, view in enumerate(('down', 'up', 'right')):
            pp = dict(tn=3, **p)
            if view == 'right' and app['cls'] == 'warrior': pp['sw'] = dict(ang=105, len=12)
            if app['cls'] == 'archer': pp['sw'] = dict(kind='bow', dir={'down': (0, 1), 'up': (0, -1), 'right': (1, 0)}[view], draw=2, arrow=False)
            if view == 'right' and app['cls'] == 'rogue': pp['sw2'] = dict(ang=80, len=8); pp['sw'] = dict(kind='dagger', ang=100, len=8)
            if view == 'right' and app['cls'] == 'cleric': pp['sw'] = dict(kind='mace', ang=150, len=15)
            im = sprite(app, view, pp).resize((40 * zoom, 44 * zoom), Image.NEAREST)
            A.paste(im.convert('RGB'), (i * cw, r * ch), im)
        label(A, (i * cw + cw // 2, 3 * ch - 12), nm, center=True)
    A.save(path)


def creation_ui(path):
    """Mockup da tela de criacao de personagem (retrato, 270x480 nativo, ampliado 3x)."""
    Wn, Hn = 270, 480
    im = Image.new('RGB', (Wn, Hn), (34, 22, 30))
    d = ImageDraw.Draw(im)
    d.rectangle([2, 2, Wn - 3, Hn - 3], outline=(200, 150, 60)); d.rectangle([4, 4, Wn - 5, Hn - 5], outline=(90, 60, 40))
    label(im, (Wn // 2, 10), 'CRIAR PERSONAGEM', (255, 224, 140), center=True)
    # preview
    d.rectangle([20, 24, Wn - 21, 168], fill=(70, 130, 56), outline=(200, 150, 60))
    for y in range(24, 168, 4):
        for x in range(21 + (y // 4 % 2) * 2, Wn - 21, 4):
            d.point([x, y], fill=(86, 150, 66))
    app = dict(cls='warrior', outfit='mail', hat='helm', clothes='azul', metal='aco', accent='dourado', hair='castanho', eyes='verde', skin='bronze', weapon='espada_gelo')
    spr = sprite(app, 'down', dict(tn=3, sw=dict(ang=165, len=12, side='r'))).resize((40 * 3, 44 * 3), Image.NEAREST)
    d.ellipse([Wn // 2 - 26, 150, Wn // 2 + 26, 160], fill=(40, 90, 40))
    im.paste(spr.convert('RGB'), (Wn // 2 - 60, 30), spr)
    for dx, tx in ((-1, '<'), (1, '>')):
        label(im, (Wn // 2 + dx * 90, 90), tx, (255, 240, 200), center=True)
    # abas de classe
    clsl = [('warrior', 'GUER'), ('mage', 'MAGO'), ('archer', 'ARCO'), ('rogue', 'LADI'), ('cleric', 'CLER')]
    for i, (c, nm) in enumerate(clsl):
        x = 14 + i * 49
        d.rectangle([x, 174, x + 44, 206], fill=(60, 40, 50) if c != 'warrior' else (110, 80, 40), outline=(200, 150, 60) if c == 'warrior' else (90, 60, 40))
        hd = C.anim('down', 'idle', c, [dict(tn=3)])[0][0].crop((8, 8, 32, 30))
        im.paste(hd.convert('RGB'), (x + 10, 175), hd)
        label(im, (x + 22, 198), nm, center=True)
    # secoes
    def swatches(y, title, cols, sel=0):
        label(im, (14, y), title)
        for i, col in enumerate(cols):
            x = 14 + i * 22
            d.rectangle([x, y + 11, x + 17, y + 26], fill=col, outline=(255, 240, 200) if i == sel else (20, 12, 24), width=2 if i == sel else 1)
    swatches(214, 'CABELO', [tuple(int(v[k:k + 2], 16) for k in (1, 3, 5)) for v in [h['O'] for h in C.HAIRS.values()]], 2)
    swatches(246, 'PELE', [tuple(int(v[k:k + 2], 16) for k in (1, 3, 5)) for v in [h['s'] for h in C.SKINS.values()]], 1)
    swatches(278, 'OLHOS', [tuple(int(v[k:k + 2], 16) for k in (1, 3, 5)) for v in [h['b'] for h in C.EYES.values()]], 1)
    swatches(310, 'ROUPA', [tuple(int(v[k:k + 2], 16) for k in (1, 3, 5)) for v in [h['t'] for h in C.CLOTHES.values()]][:10], 1)
    # chapeus
    label(im, (14, 342), 'CHAPEU / ELMO')
    for i, h in enumerate(('none', 'helm', 'hood', 'cap', 'crown')):
        x = 14 + i * 48
        d.rectangle([x, 353, x + 43, 391], fill=(60, 40, 50), outline=(255, 240, 200) if h == 'helm' else (90, 60, 40), width=2 if h == 'helm' else 1)
        a2 = dict(app, hat=h, outfit='cloth' if h != 'helm' else 'mail')
        t = sprite(a2, 'down', dict(tn=3)).crop((8, 4, 32, 26)).resize((42, 38), Image.NEAREST)
        im.paste(t.convert('RGB'), (x + 1, 353), t)
    # arma inicial
    label(im, (14, 398), 'ARMA INICIAL')
    for i, wid in enumerate(('espada_ferro', 'espada_aco', 'espada_dourada', 'espada_chamas', 'espada_gelo', 'espada_sombria')):
        x = 14 + i * 40
        d.rectangle([x, 409, x + 35, 445], fill=(60, 40, 50), outline=(255, 240, 200) if wid == 'espada_gelo' else (90, 60, 40), width=2 if wid == 'espada_gelo' else 1)
        t = sprite(dict(cls='warrior', weapon=wid), 'right', dict(tn=3, sw=dict(ang=105, len=12))).crop((10, 14, 40, 44))
        im.paste(t.convert('RGB'), (x + 3, 411), t)
    d.rectangle([60, 452, Wn - 61, 470], fill=(180, 60, 40), outline=(255, 220, 140))
    label(im, (Wn // 2, 457), 'CRIAR', (255, 245, 220), center=True)
    im.resize((Wn * 3, Hn * 3), Image.NEAREST).save(path)


if __name__ == '__main__':
    weapons_gallery(os.path.join(OUT, 'equip_armas.png'))
    customization(os.path.join(OUT, 'equip_personalizacao.png'))
    outfits_sheet(os.path.join(OUT, 'equip_armaduras_classes.png'))
    creation_ui(os.path.join(OUT, 'equip_criacao_personagem.png'))
    print('ok')
