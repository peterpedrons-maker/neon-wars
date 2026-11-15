"""Heroi desenhado a mao (pixel a pixel). 3 vistas: down, up (metade espelhada) e side (direita)."""
from PIL import Image, ImageDraw
import pxtool
from teste_clareira import sword, limb, STEEL, outline, C, INK

PAL = dict(K='#2a1a2e', J='#ffa04a', H='#e0661e', h='#a8401a', s='#ffd0a8', S='#e0a07c', e='#2a1a2e', r='#f08a8a',
           b='#2a4ca0', B='#4a82e8', c='#9ccaff', o='#b04418', O='#f08030', P='#ffb860', t='#6a4028', y='#ffd05a',
           n='#5a4050', m='#7a4a2e', M='#a8764a', T='#4a2c1c')
RSH = dict(J='H', P='O', c='B', M='m')

DOWN = dict(pal=PAL, mirror=True, rshade=RSH, rows=[
    '.....KKKKK', '...KKJJJJJ', '..KJJJJJJH', '.KJJJJJHHH', '.KJJJHHHHH', 'KJJJHHHHHH', 'KJJHHHhHHh', 'KHhHssHhss',
    'KHhsssssss', 'KHhsssesss', 'KHhsssesss', '.KhrsssSSs', '..KKsssSSS', '...KbBBBBB', '..KbBcBBBB', '..KoPOOOOO',
    '.KoPPOOOOO', '.KoPoOOOOO', '.KoOoOOOOO', '.KsSoOOOOO', '..KKttttyy', '...KoOOOOO', '..KnnnnK..', '..KnnnnK..',
    '.KmmmmmmK.', '.KKKKKKKK.'])
UP = dict(pal=PAL, mirror=True, rshade=RSH, rows=[
    '.....KKKKK', '...KKJJJJJ', '..KJJJJJJH', '.KJJJJJHHH', '.KJJJHHHHH', 'KJJJHHHHHH', 'KJHHHHHhHH', 'KJHHHhHHHH',
    'KHHHHHHhHH', 'KHhHHHhHHH', 'KHhHHhHHHH', '.KhhHHHHhH', '..KKhhhhhh', '...KbBBBBB', '..KbBBBBBB', '..KoPOOOOB',
    '.KoPPOOOOB', '.KoPoOMttb', '.KoOoOMttT', '.KsSoOMttT', '..KKttttTT', '...KoOOOOO', '..KnnnnK..', '..KnnnnK..',
    '.KmmmmmmK.', '.KKKKKKKK.'])
SIDE = dict(pal=PAL, mirror=False, rows=[
    '.....KKKKKKKK.......', '...KKJJJJJJJJKK.....', '..KJJJJJJJHHHHHK....', '.KJJJJJJHHHHHHHHK...', '.KJJJJHHHHHHHHHHHK..',
    'KJJJHHHHHHHHHHHHhhK.', 'KJHHHHHHHHHHhsssssK.', 'KHhHHHHHHHhhssssssK.', 'KHhHHHHHHhsssssssssK', 'KHhHHHHHhsssssesssK.',
    'KHhHHHHHhssssseSssK.', '.KhHHHHhhssrsssSsK..', '..KhhhhhhsssssSSK...', '....KKbBBBBBBBcK....', '...KbbBBBBBBBBcBK...',
    '.....KoPOOOOOOooK...', '.....KoPOOOOOOOoK...', '.....KoOOOOOOOoK....', '.....KoOOOOOOOoK....', '.....KoOOOOOsssK....',
    '.....KttttttyyK.....', '.....KoOOOOOOoK.....', '.....KnnnKnnnK......', '.....KnnnKnnnK......', '....KmmmKmmMMmK.....',
    '....KKKKKKKKKKK.....'])

HEAD = ['.....KKKKK', '...KKJJJJJ', '..KJJJJJJH', '.KJJJJJHHH', '.KJJJHHHHH', 'KJJJHHHHHH']
DOWN['rows'] = HEAD + ['KJJHHHhHHh', 'KHhHssHhss', 'KHhsssssss', 'KHhsssesss', 'KHhsssesss', '.KhrsssSSs', '..KKsssSSS',
    '...KbBBBBB', '..KbBcBBBB', '..KoPOOOOO', '.KoPPOOOOO', '.KoPoOOOOO', '.KoOoOOOOO', '.KsSoOOOOO', '..KKttttyy',
    '...KoOOOOO', '..KnnnnK..', '..KnnnnK..', '.KmmmmmmK.', '.KKKKKKKK.']
UP['rows'] = HEAD + ['KJHHHHHhHH', 'KJHHHhHHHH', 'KHHHHHHhHH', 'KHhHHHhHHH', 'KHhHHhHHHH', '.KhhHHHHhH', '..KKhhhhhh',
    '...KbBBBBB', '..KbBBBBBB', '..KoPOOOOO', '.KoPPOMMMM', '.KoPoOMttt', '.KoOoOMttT', '.KsSoOMttT', '..KKtttTTT',
    '...KoOOOOO', '..KnnnnK..', '..KnnnnK..', '.KmmmmmmK.', '.KKKKKKKK.']


def _shrink(rows):
    out = []
    for i, r in enumerate(rows):
        if 1 <= i <= 12:
            j = next(k for k, c in enumerate(r) if c not in '.K')
            r = '..' + r[:j] + r[j + 2:]
        out.append(r)
    return out


SIDE['rows'] = _shrink(SIDE['rows'])
SPECS = dict(down=DOWN, up=UP, right=SIDE)
CROUCH_DEL = dict(down=(17,), up=(17,), right=(17,))
HOP_DEL = dict(down=(22, 23), up=(22, 23), right=(22, 23))
HAND = dict(down=(17, 19, 80), up=(17, 19, 82), right=(14, 19, 48))  # (x, y_rel_to_row19, angulo)


def hero_px(face, pose='idle', t=0):
    if face == 'left':
        return hero_px('right', pose, t).transpose(Image.FLIP_LEFT_RIGHT)
    spec = SPECS[face]
    dele = ()
    if pose in ('crouch', 'land') or (pose == 'idle' and t): dele = CROUCH_DEL[face]
    if pose == 'hop': dele = HOP_DEL[face]
    base, grid = pxtool.build(spec, dele)
    W = 28 if face == 'right' else 26
    img = Image.new('RGBA', (W, base.height + 2), (0, 0, 0, 0))
    ox = 3 if face != 'right' else 3
    img.alpha_composite(base, (ox, 1))
    hx, hy, ang = HAND[face]
    hy = hy - len(spec['rows']) + base.height + 1 - 0 if False else hy - (len(spec['rows']) - base.height) + 1
    layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
    sword(layer, (hx + ox, hy), ang, 11, 1.2, .4, STEEL, 6)
    d = ImageDraw.Draw(layer)
    layer = outline(layer, INK)
    out = Image.new('RGBA', img.size, (0, 0, 0, 0))
    out.alpha_composite(img); out.alpha_composite(layer)
    out.alpha_composite(img.crop((hx + ox - 2, hy - 2, hx + ox + 2, hy + 2)), (hx + ox - 2, hy - 2))  # mao por cima do cabo
    return out


if __name__ == '__main__':
    import os
    from teste_clareira import OUT
    for k, s in SPECS.items():
        print(k, pxtool.lint(s)[:12])
    items = [hero_px(f, p, 0) for f in ('down', 'up', 'right', 'left') for p in ('idle', 'crouch', 'hop')]
    pxtool.sheet(items, 10, cols=6).convert('RGB').save(os.path.join(OUT, 'heroi_px.png'))
