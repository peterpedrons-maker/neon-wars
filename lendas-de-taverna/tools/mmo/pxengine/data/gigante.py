#!/usr/bin/env python3
"""GIGANTE DAS COLINAS (esboço v2, humanoide, MESMO nível de detalhe da perna do colosso.py): pelagem em tufos, joelhos protuberantes,
pedras e musgo, runas, garras, pelos pendurados, cinto de ossos, chifres de várias pontas. Uma massa só (fauna.Cv).
Uso: python3 gigante.py sheet out.png [hero.png]"""
import sys, math
from PIL import Image
import fauna as FA
import colosso as CO
PAL = dict(CO.PAL); FLAT = dict(CO.FLAT)
GW, GH = 260, 420
SC = 1.3          # o gigante e' ~30% maior que o esboco anterior (desenhado com mais pixels, nao esticado)

class Sc:
    def __init__(s, cv, k): s.cv, s.k = cv, k
    def ell(s, x, y, rx, ry, reg='body', far=False): s.cv.ell(x * s.k, y * s.k, rx * s.k, ry * s.k, reg, far)
    def cap(s, x0, y0, x1, y1, r0, r1, reg='body', far=False): s.cv.cap(x0 * s.k, y0 * s.k, x1 * s.k, y1 * s.k, r0 * s.k, max(1, r1 * s.k), reg, far)
    def dot(s, x, y, col):
        s.cv.dot(x * s.k, y * s.k, col)
    def render(s, p, f): return s.cv.render(p, f)

def tufts(c, x0, y0, x1, y1, n, sg, ln, r0=3.4, reg='fur'):
    """pelos ao longo de um segmento (sg = lado para onde caem)"""
    for k in range(n):
        t = (k + .5) / n; x = x0 + (x1 - x0) * t; y = y0 + (y1 - y0) * t
        c.cap(x, y, x + sg * (4 + (k % 3)), y + ln + (k % 2) * 4, r0, 1, reg)

def giant(view='d'):
    FA.W, FA.H = int(GW * SC), int(GH * SC)
    c = Sc(FA.Cv(), SC); c.cv.contact = False
    cx = GW // 2; fy = 408
    back = (view == 'u'); bm = 'far' if back else 'fur'; bb = 'far' if back else 'body'
    runes = []
    if view == 's':
        sx = lambda v: cx - 8 + v          # perfil: eixo do corpo
        for far, sg in ((True, -1), (False, 1)):
            x0 = sx(sg * 16); f = far
            c.cap(x0, 218, x0 + 4, 296, 30, 22, 'fur', f)                         # coxa
            tufts(c, x0 - 28, 232, x0 - 18, 290, 6, -1, 9, reg='fur')
            c.ell(x0 + 8, 304, 25, 22, 'fur', f); c.ell(x0 + 14, 300, 9, 7, 'stone', f); c.ell(x0 + 4, 312, 8, 5, 'moss', f)   # joelho
            c.cap(x0 + 8, 308, x0 + 6, 388, 19, 14, 'body', f)                  # canela
            tufts(c, x0 - 8, 318, x0 - 4, 378, 5, -1, 8, 2.8)
            c.ell(x0 + 12, fy - 11, 34, 12, 'hoof', f)                            # pé
            for k in range(3): c.cap(x0 + 30 + k * 4, fy - 14 + k * 5, x0 + 42 + k * 4, fy - 8 + k * 5, 6.4, 4.4, 'hoof', f)
            for k in range(3): c.cap(x0 + 44 + k * 4, fy - 11 + k * 5, x0 + 52 + k * 4, fy - 7 + k * 5, 2.4, 1.2, 'horn', f)
        c.ell(sx(-12), 224, 62, 36, 'fur')                                         # tanga
        tufts(c, sx(-58), 240, sx(30), 244, 11, 1, 20, 4.6)
        c.ell(sx(-4), 150, 60, 78, 'body'); c.ell(sx(-30), 150, 38, 74, 'fur'); c.ell(sx(12), 198, 44, 38, 'body')
        tufts(c, sx(-62), 110, sx(-52), 210, 8, -1, 16, 4.6)                       # costas peludas
        c.cap(sx(-6), 94, sx(30), 62, 34, 22, 'fur'); tufts(c, sx(-24), 74, sx(14), 92, 6, -1, 14, 4.6)
        # braco de longe
        c.cap(sx(12), 102, sx(46), 196, 26, 20, 'body', True); c.cap(sx(46), 196, sx(54), 262, 20, 15, 'body', True); c.ell(sx(58), 276, 20, 24, 'skin', True)
        # ombro e braco de perto
        c.ell(sx(4), 100, 42, 32, 'stone'); c.ell(sx(-8), 94, 36, 26, 'fur'); c.ell(sx(-14), 82, 12, 8, 'moss')
        for k in range(3): c.cap(sx(-6 + k * 12), 76, sx(-4 + k * 14), 54, 6, 1.4, 'horn')   # espinhos
        c.cap(sx(8), 108, sx(36), 190, 29, 22, 'body'); tufts(c, sx(2), 120, sx(24), 184, 6, -1, 14, 4)
        c.ell(sx(36), 192, 24, 22, 'fur'); c.cap(sx(36), 196, sx(48), 262, 22, 17, 'body')
        c.cap(sx(30), 236, sx(60), 244, 4, 4, 'stone'); tufts(c, sx(36), 226, sx(46), 256, 5, -1, 12, 3.4)
        c.ell(sx(52), 278, 24, 27, 'skin')
        for k in range(4): c.cap(sx(40 + k * 8), 290, sx(42 + k * 8), 312, 5.2, 3.6, 'skin')
        for k in range(4): c.cap(sx(42 + k * 8), 310, sx(43 + k * 8), 318, 2.2, 1, 'horn')
        # cabeca
        c.ell(sx(34), 52, 36, 33, 'fur'); c.ell(sx(38), 58, 28, 28, 'body'); c.ell(sx(56), 68, 22, 17, 'skin'); c.ell(sx(48), 86, 18, 8, 'body')
        for sg2, (ax_, ay_) in enumerate(((sx(18), 28), (sx(40), 26))):
            c.cap(ax_, ay_, ax_ + 4, ay_ - 20, 8, 4.5, 'horn'); c.cap(ax_ + 4, ay_ - 20, ax_ - 2 + sg2 * 10, ay_ - 48, 4.5, 1.2, 'horn')
        c.cap(sx(60), 80, sx(64), 62, 4.2, 2, 'tusk'); tufts(c, sx(36), 90, sx(52), 92, 4, 1, 12, 3)
        c.ell(sx(44), 40, 12, 6, 'moss')
        eyes = [(sx(48), 50)]; runes = [(sx(-4), 132), (sx(14), 160), (sx(-20), 176), (sx(34), 120), (sx(40), 214)]
    else:
        for sg in (-1, 1):
            x0 = cx + sg * 36
            c.cap(x0, 216, x0 + sg * 3, 296, 31, 23, bm)                                  # coxa
            tufts(c, x0 + sg * 29, 232, x0 + sg * 24, 292, 6, sg, 7, 3.4, bm)
            tufts(c, x0 - sg * 26, 236, x0 - sg * 21, 290, 5, -sg, 7, 3.2, bm)
            c.ell(x0 + sg * 3, 302, 27, 22, bm)                                          # joelho protuberante
            c.ell(x0 + sg * 3 - 8, 298, 9, 6, 'stone'); c.ell(x0 + sg * 3 + 9, 310, 5, 4, 'moss')
            c.cap(x0 + sg * 3, 306, x0 + sg * 4, 388, 19, 15, bb)                           # canela
            tufts(c, x0 + sg * 4 - 14, 318, x0 + sg * 4 + 14, 320, 5, 1, 14, 2.8, bm)    # pelos pendurados do joelho
            c.ell(x0 + sg * 6, fy - 11, 34, 13, 'hoof')                                  # pé
            if not back:
                for k in range(-2, 3): c.cap(x0 + sg * 6 + k * 12, fy - 10, x0 + sg * 6 + k * 13, fy - 2, 6.4, 5, 'hoof')
                for k in range(-2, 3): c.cap(x0 + sg * 6 + k * 13, fy - 4, x0 + sg * 6 + k * 14, fy + 2, 2.6, 1.2, 'horn')
        c.ell(cx, 222, 78, 36, bm)                                                       # tanga de pele
        tufts(c, cx - 70, 240, cx + 70, 242, 14, 1, 22, 5, bm)
        c.ell(cx, 156, 80, 80, bb); c.ell(cx, 198, 62, 46, bb)                            # torso e barriga
        c.ell(cx, 128, 52, 34, 'fur' if not back else 'far')                                # peitoral peludo
        c.ell(cx, 98, 58, 22, 'fur')                                                          # trapezio
        # juba
        c.ell(cx, 84, 46, 18, 'fur'); tufts(c, cx - 44, 90, cx + 44, 90, 10, 1, 18, 4.6, 'fur')
        for sg in (-1, 1):
            c.ell(cx + sg * 80, 106, 40, 33, 'stone'); c.ell(cx + sg * 78, 98, 35, 26, bm)     # ombreira
            for k in range(3): c.cap(cx + sg * (68 + k * 11), 84, cx + sg * (72 + k * 12), 60 - k * 4, 6, 1.4, 'horn')
            c.ell(cx + sg * 90, 88, 9, 6, 'moss')
            c.cap(cx + sg * 90, 118, cx + sg * 101, 188, 30, 23, bb)                         # braco
            tufts(c, cx + sg * 118, 128, cx + sg * 122, 184, 6, sg, 10, 3.4, bm)
            c.ell(cx + sg * 101, 190, 25, 22, bm)                                           # cotovelo
            c.cap(cx + sg * 101, 194, cx + sg * 96, 262, 23, 17, bb)                         # antebraco
            tufts(c, cx + sg * 80, 206, cx + sg * 112, 208, 5, 1, 16, 3.4, bm)
            c.cap(cx + sg * 96 - 20, 244, cx + sg * 96 + 20, 244, 4.6, 4.6, 'stone')        # braceleira
            c.ell(cx + sg * 94, 282, 26, 28, 'skin')                                         # mao
            if not back:
                for k in range(4): c.cap(cx + sg * 94 - 15 + k * 10, 294, cx + sg * 94 - 16 + k * 10, 318, 5.6, 4, 'skin')
                for k in range(4): c.cap(cx + sg * 94 - 16 + k * 10, 316, cx + sg * 94 - 16 + k * 10, 325, 2.4, 1, 'horn')
                c.cap(cx + sg * 94 - sg * 23, 282, cx + sg * 94 - sg * 14, 306, 5.2, 4, 'skin')
        # cabeca pequena
        c.ell(cx, 56, 37, 34, 'fur'); c.ell(cx, 62, 29, 29, bb)
        for sg in (-1, 1):
            c.cap(cx + sg * 28, 38, cx + sg * 46, 16, 8, 4.8, 'horn'); c.cap(cx + sg * 46, 16, cx + sg * 49, -12, 4.8, 1.2, 'horn')
            c.cap(cx + sg * 36, 56, cx + sg * 56, 52, 5, 3, 'horn'); c.cap(cx + sg * 56, 52, cx + sg * 64, 36, 3, 1, 'horn')
        if not back:
            c.ell(cx - 18, 46, 12, 7, 'stone'); c.ell(cx + 18, 44, 13, 8, 'moss')           # sobrancelhas
            c.ell(cx, 78, 18, 11, 'skin'); c.ell(cx, 90, 21, 10, 'body')                      # focinho e mandibula
            for sg in (-1, 1): c.cap(cx + sg * 12, 90, cx + sg * 14, 76, 3.2, 1.4, 'tusk')
            for sg in (-1, 1): c.cap(cx + sg * 36, 70, cx + sg * 42, 96, 6, 3, 'fur')
            tufts(c, cx - 20, 96, cx + 20, 98, 5, 1, 12, 3.2)
        eyes = [(cx - 13, 56), (cx + 13, 56)]
        runes = [(cx - 30, 134), (cx + 24, 144), (cx - 4, 164), (cx + 40, 120), (cx - 46, 178), (cx + 14, 188), (cx - 8, 206)]
        if not back: runes += [(cx - 96, 214), (cx + 96, 206), (cx - 36, 340), (cx + 36, 340), (cx, 36)]
    # musgo e pedras espalhados
    for (mx, my, a, b_) in ((cx - 52, 122, 12, 8), (cx + 40, 168, 9, 6), (cx - 60, 196, 8, 5), (cx + 64, 150, 7, 5)):
        if view == 's': mx = cx - 8 + (mx - cx) * .45
        c.ell(mx, my, a, b_, 'moss')
    for (mx, my, a, b_) in ((cx - 22, 232, 8, 5), (cx + 54, 120, 7, 5), (cx - 14, 176, 6, 4)):
        if view == 's': mx = cx - 8 + (mx - cx) * .45
        c.ell(mx, my, a, b_, 'stone')
    if view != 'u':
        for (rx, ry) in runes:
            for dx_, dy_ in ((0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1)): c.dot(rx + dx_, ry + dy_, FLAT['rune'])
            c.dot(rx, ry, FLAT['eye2'])
        for ex, ey in eyes:
            for dx_ in (-1, 0, 1, 2):
                for dy_ in (0, 1): c.dot(ex + dx_, ey + dy_, FLAT['eye'])
            c.dot(ex, ey, FLAT['eye2'])
    img = c.render(PAL, FLAT)
    return fur(c, img, view, back)

import numpy as np
from scipy.ndimage import gaussian_filter, binary_erosion
def fur(c, img, view, back, t=0.0, seed=3):
    """PELO COMO GRAMA: (1) franja de fios saindo da silhueta (entram na mascara e ganham contorno/sombra do motor);
    (2) fios curtos por cima do corpo, claros na ponta e escuros na raiz, com balanco (t) para animar."""
    rng = np.random.RandomState(seed)
    a = np.array(img)[:, :, 3] > 0
    bl = gaussian_filter(a.astype(float), 2.2); gy, gx = np.gradient(bl)
    rgb = np.array(img)[:, :, :3].astype(int)
    notbone = ~((rgb[:, :, 0] > 175) & (rgb[:, :, 1] > 150))      # chifres, garras e presas ficam lisos
    edge = a & ~binary_erosion(a, iterations=2) & notbone
    ys, xs = np.where(edge)
    reg = 'far' if back else 'fur'
    for i in rng.choice(len(xs), min(len(xs), int(len(xs) * .22)), replace=False):
        x, y = xs[i], ys[i]
        nx, ny = -gx[y, x], -gy[y, x]; L = math.hypot(nx, ny) or 1; nx, ny = nx / L, ny / L
        ny = ny * .6 + .55            # os fios caem um pouco para baixo (peso)
        ln = rng.uniform(4, 9) * c.k / 1.3
        sw = math.sin(t + x * .07) * 1.6
        c.cv.cap(x, y, x + nx * ln + sw, y + ny * ln, 2.0, .5, reg)
    img2 = c.cv.render(PAL, FLAT)
    arr = np.array(img2).astype(float); m = arr[:, :, 3] > 0
    inner = binary_erosion(m, iterations=4) & ~((arr[:, :, 0] > 175) & (arr[:, :, 1] > 150))
    yy, xx = np.where(inner)
    cxm = arr.shape[1] / 2
    for i in rng.choice(len(xx), min(len(xx), int(len(xx) * .07)), replace=False):
        x, y = xx[i], yy[i]; base = arr[y, x, :3].copy()
        ln = int(rng.randint(4, 9)); dxs = (np.sign(x - cxm) * .3 + math.sin(t + y * .05 + x * .03) * .5)
        for k in range(ln):
            px_, py_ = int(round(x + dxs * k)), y + k
            if 0 <= px_ < arr.shape[1] and 0 <= py_ < arr.shape[0] and inner[py_, px_]:
                f = .82 + .4 * (k / max(1, ln - 1))      # raiz escura -> ponta clara
                arr[py_, px_, :3] = np.clip(base * f + (8 if k == ln - 1 else 0), 0, 255)
    return Image.fromarray(arr.astype(np.uint8), 'RGBA')

def sheet(path, hero_png=''):
    V = [giant(v) for v in ('d', 's', 'u')]
    pad = 20
    W_, H_ = V[0].size
    S = Image.new('RGBA', (W_ * 3 + 150 + pad * 6, H_ + pad * 2), (92, 120, 84, 255))
    for i, im in enumerate(V): S.alpha_composite(im, (pad + i * (W_ + pad), pad))
    try:
        H = Image.open(hero_png).convert('RGBA'); S.alpha_composite(H, (W_ * 3 + pad * 4, H_ + pad - H.height))
    except Exception as e: print('hero', e)
    S.save(path); print(path, S.size)
    # ampliacao da frente para conferir o detalhe
    big = V[0].resize((W_ * 3, H_ * 3), Image.NEAREST)
    bg = Image.new('RGBA', big.size, (92, 120, 84, 255)); bg.alpha_composite(big)
    bg.save(path.replace('.png', '_frente_grande.png'))

if __name__ == '__main__':
    sheet(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else '')
