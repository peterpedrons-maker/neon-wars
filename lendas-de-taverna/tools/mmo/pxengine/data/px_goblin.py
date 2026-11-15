"""Goblin desenhado a mao (pixel a pixel): down, up (metade espelhada) e side (direita)."""
from PIL import Image, ImageDraw
import pxtool
from teste_clareira import outline, INK, C, line

PAL = dict(K='#2a1a2e', L='#78b83c', l='#b4e068', G='#4a8a2a', g='#2c5a1c', y='#ffe04a', e='#2a1a2e', w='#ffffff', d='#1a2a14',
           t='#8a5a34', T='#5a3624', m='#5a3624', M='#8a5a34')
RSH = dict(L='G', l='L')
DOWN = dict(pal=PAL, mirror=True, rshade=RSH, rows=[
    '....KKKKKK', '...KLLLLLL', '..KLLLLLLG', '..KLLLLGGG', 'K.KLLLGGGG', 'KKKLGGGGGG', 'KLLKgggGGG', 'KLLKyyeGGG',
    '.KKKGGGGGG', '..KLGGGGGG', '..KLGdddww', '...KKGGGGG', '....KKGGGG', '..KLLLGGGG', '.KLLLGGGGG', '.KLKLGGGGG',
    '.KLKGGGGGG', '.KlKGGGGGG', '..KKttttTT', '...KtttttT', '...KtttttT', '..KGGGK...', '..KGGGK...', '.KmmmmK...', '.KKKKKK...'])
UP = dict(pal=PAL, mirror=True, rshade=RSH, rows=[
    '....KKKKKK', '...KLLLLLL', '..KLLLLLLG', '..KLLLLGGG', 'K.KLLLGGGG', 'KKKLGGGGGG', 'KLLKGGGGGG', 'KLLKGGGgGG',
    '.KKKGGGGGG', '..KLGGGgGG', '..KLGGGGGG', '...KKGGGGG', '....KKGGGG', '..KLLLGGgG', '.KLLLGGGGg', '.KLKLGGGgG',
    '.KLKGGGGGg', '.KlKGGGGGG', '..KKttttTT', '...KtttttT', '...KtttttT', '..KGGGK...', '..KGGGK...', '.KmmmmK...', '.KKKKKK...'])
SIDE = dict(pal=PAL, mirror=False, rows=[
    '.......KKKKKK.......', '.....KKLLLLLLKK.....', '....KLLLLLLLGGGK....', 'KK..KLLLLLLGGGGGK...', 'KLKKKLLLLLGGGGGGGK..',
    '.KLLKLLLLLGGGGGGGGK.', '..KKKLLLLLGGgyyGGGKK', '....KLLLLLGGGyeGGGGK', '....KLLLLGGGGGGGGLLK', '....KKLLGGGGGGdwdGGK',
    '.....KKGGGGGGGGGKK..', '......KKGGGGGGKK....', '.....KLLGGGGGGGGK...', '.....KLLGGGGGGGGK...', '.....KLGGGGGLLLK....',
    '.....KLGGGGGGLlK....', '.....KttttttttK.....', '.....KtttttttTK.....', '.....KKtttttTKK.....', '......KGGKGGGK......',
    '......KGGKGGGK......', '.....KmmmKmmmmK.....', '.....KKKKKKKKKK.....'])
SPECS = dict(down=DOWN, up=UP, right=SIDE)
CROUCH_DEL = dict(down=(14,), up=(14,), right=(13,))
HOP_DEL = dict(down=(21, 22), up=(21, 22), right=(19, 20))
HAND = dict(down=(17, 17, 'ur'), up=(17, 17, 'ur'), right=(14, 15, 'r'))


def goblin_px(face, pose='idle', t=0):
    if face == 'left':
        return goblin_px('right', pose, t).transpose(Image.FLIP_LEFT_RIGHT)
    spec = SPECS[face]
    dele = ()
    if pose in ('crouch', 'land') or (pose == 'idle' and t): dele = CROUCH_DEL[face]
    if pose == 'hop': dele = HOP_DEL[face]
    base, _ = pxtool.build(spec, dele)
    ox = 5 if face != 'right' else 3
    W = base.width + ox + 8
    img = Image.new('RGBA', (W, base.height + 2), (0, 0, 0, 0))
    img.alpha_composite(base, (ox, 1))
    hx, hy, mode = HAND[face]
    hy = hy - (len(spec['rows']) - base.height) + 1
    hx += ox
    layer = Image.new('RGBA', img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    tip = (hx + 4, hy - 6) if mode == 'ur' else (hx + 6, hy - 2)
    line(d, (hx, hy), tip, C(PAL['t']), 2)
    d.rectangle([tip[0] - 1, tip[1] - 2, tip[0] + 1, tip[1] + 1], fill=C('#a8764a'))
    d.point([tip[0] + 1, tip[1] + 1], fill=C(PAL['T']))
    d.point([tip[0] - 1, tip[1] - 1], fill=C('#d8d8e8'))
    layer = outline(layer, INK)
    out = Image.new('RGBA', img.size, (0, 0, 0, 0)); out.alpha_composite(layer); out.alpha_composite(img)
    out.alpha_composite(img.crop((hx - 2, hy - 2, hx + 2, hy + 2)), (hx - 2, hy - 2))
    return out


if __name__ == '__main__':
    import os
    from teste_clareira import OUT
    for k, s in SPECS.items(): print(k, [w for w in pxtool.lint(s) if 'contorno' in w or 'tamanho' in w or 'sem cor' in w][:6])
    items = [goblin_px(f, p, 0) for f in ('down', 'up', 'right', 'left') for p in ('idle', 'crouch', 'hop')]
    pxtool.sheet(items, 10, cols=6).convert('RGB').save(os.path.join(OUT, 'goblin_px.png'))
