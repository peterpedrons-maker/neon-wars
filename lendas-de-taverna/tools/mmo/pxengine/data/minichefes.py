"""Mini-chefes sem humanoide: Morcego-Vampiro (creature.py ampliado e recolorido) e Capitao Presa-de-Ferro (javali com elmo/placas de ferro)."""
import numpy as np
from PIL import Image
import creature as CR, fauna as F

def _scale(im, k):
    b = im.getbbox(); c = im.crop(b); return c.resize((round(c.width * k), round(c.height * k)), Image.NEAREST)

def vampiro(view, ph=0.0, **kw):
    return vamp_img(CR.draw('morcego', view, ph), view)

def vamp_img(src, view):
    a = np.array(src.convert('RGBA')).astype(int)
    m = a[..., 3] > 0
    r, g, b = a[..., 0].copy(), a[..., 1].copy(), a[..., 2].copy()
    lum = (r + g + b) / 3
    # roxo -> carmesim escuro com asas quase pretas
    a[..., 0] = np.where(m, np.clip(lum * .85 + 6, 0, 255), 0); a[..., 1] = np.where(m, lum * .12, 0); a[..., 2] = np.where(m, lum * .26 + 4, 0)
    # olhos vermelhos originais viram dourados
    eye = m & (r > 200) & (g < 90)
    a[eye] = (255, 220, 70, 255)
    im = Image.fromarray(a.astype('uint8'), 'RGBA')
    im = _scale(im, 1.6)
    px = im.load(); W, H = im.size
    # presas brancas logo abaixo da cabeca
    cx = W // 2 if view != 'right' else int(W * .42)
    hy = int(H * .38)
    for dx, dy in ((-2, 0), (-2, 1), (2, 0), (2, 1)):
        if 0 <= cx + dx < W and 0 <= hy + dy < H: px[cx + dx, hy + dy] = (250, 250, 240, 255)
    out = Image.new('RGBA', (72, 64), (0, 0, 0, 0)); out.alpha_composite(im, (36 - W // 2, 2)); return out

def presa(view, ph=0.0, **kw):
    im = F.javali(view, ph).convert('RGBA'); b = im.getbbox(); c = im.crop(b)
    a = np.array(c).astype(int); m = a[..., 3] > 0; H, W = m.shape
    steel = lambda t: (int(110 + 110 * t), int(118 + 112 * t), int(134 + 112 * t), 255)
    # elmo/placa de ferro sobre a cabeca (parte superior do lado do focinho) e faixa de armadura no dorso
    if view == 'right':
        head = np.zeros_like(m); head[: int(H * .55), int(W * .66):] = True
        band = np.zeros_like(m); band[:, int(W * .40):int(W * .50)] = True
    else:
        head = np.zeros_like(m); head[: int(H * .30), :] = True
        band = np.zeros_like(m); band[int(H * .66):int(H * .74), :] = True
    brown = m & (a[..., 0] > a[..., 2] + 20) & (a[..., 0] < 200) & (a[..., 1] < a[..., 0] - 10)
    for k, reg in ((0, head), (1, band)):
        sel = brown & reg
        ys, xs = np.nonzero(sel)
        for y, x in zip(ys, xs): a[y, x] = steel(.75 if (y + x) % 4 else .35)
    # rebites e presas de ferro
    for y, x in zip(*np.nonzero(brown & head)): 
        if (x * 3 + y) % 7 == 0: a[y, x] = (250, 250, 255, 255)
    white = m & (a[..., 0] > 225) & (a[..., 1] > 225) & (a[..., 2] > 200) & ~head
    a[white] = (170, 180, 200, 255)
    im2 = Image.fromarray(a.astype('uint8'), 'RGBA'); im2 = im2.resize((round(W * 1.45), round(H * 1.45)), Image.NEAREST)
    out = Image.new('RGBA', (72, 64), (0, 0, 0, 0)); out.alpha_composite(im2, (36 - im2.width // 2, 60 - im2.height)); return out
