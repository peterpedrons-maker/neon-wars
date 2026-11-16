"""Icones novos de item (96x96 = 32x32 nativos x3, mesmo estilo dos i_*.png: item na diagonal, contorno escuro, 3 tons, brilho).
Uso: python3 icons_novos.py  -> grava lendas-de-taverna/assets/ico/i_<nome>.png (alaude, flauta, varinha) e uma folha de conferencia."""
import os, math
import numpy as np
from PIL import Image
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../../assets/ico')
N = 32; K = 3
OL = (26, 18, 36, 255)
def hexc(h): h = h.lstrip('#'); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (255,)
class Cv:
    def __init__(s): s.a = np.zeros((N, N, 4), np.uint8); s.own = np.zeros((N, N), np.int16) - 1
    def mask_poly(s, pts):
        from PIL import ImageDraw
        m = Image.new('L', (N, N), 0); ImageDraw.Draw(m).polygon(pts, fill=255); return np.array(m) > 0
    def mask_ell(s, cx, cy, rx, ry, ang=0):
        ys, xs = np.mgrid[0:N, 0:N]; dx, dy = xs + .5 - cx, ys + .5 - cy
        c, sn = math.cos(ang), math.sin(ang); u = dx * c + dy * sn; v = -dx * sn + dy * c
        return (u / rx) ** 2 + (v / ry) ** 2 <= 1
    def mask_line(s, x0, y0, x1, y1, w):
        ys, xs = np.mgrid[0:N, 0:N]; px, py = xs + .5, ys + .5
        vx, vy = x1 - x0, y1 - y0; L2 = vx * vx + vy * vy
        t = np.clip(((px - x0) * vx + (py - y0) * vy) / L2, 0, 1); d = np.hypot(px - (x0 + t * vx), py - (y0 + t * vy)); return d <= w / 2
    def fill(s, m, base, lo=None, hi=None, light=(-1, -1)):
        """pinta m com 3 tons: luz vem de cima-esquerda"""
        lo = lo or tuple(int(c * .66) for c in base[:3]) + (255,); hi = hi or tuple(min(255, int(c * 1.3 + 14)) for c in base[:3]) + (255,)
        ys, xs = np.nonzero(m)
        if not len(ys): return
        proj = (xs * light[0] + ys * light[1]).astype(float); lo_t, hi_t = np.percentile(proj, 66), np.percentile(proj, 22)
        for x, y, p in zip(xs, ys, proj): s.a[y, x] = hi if p <= hi_t else (lo if p >= lo_t else base)
    def px(s, x, y, c):
        if 0 <= x < N and 0 <= y < N: s.a[y, x] = c
    def outline(s):
        al = s.a[..., 3] > 0; pad = np.pad(al, 1); near = pad[:-2, 1:-1] | pad[2:, 1:-1] | pad[1:-1, :-2] | pad[1:-1, 2:]
        out = near & ~al
        for y, x in zip(*np.nonzero(out)): s.a[y, x] = OL
        # contorno mais claro (da propria cor) onde a luz bate seria exagero: mantem contorno unico
    def save(s, name):
        im = Image.fromarray(s.a, 'RGBA').resize((N * K, N * K), Image.NEAREST); im.save(f'{OUT}/{name}.png'); return im

def varinha():
    c = Cv(); x0, y0, x1, y1 = 6, 26, 22, 10
    c.fill(c.mask_line(x0, y0, x1, y1, 3.2), hexc('#8a5a34'), hexc('#4e3020'), hexc('#c08a52'))
    for t in (.12, .22):                                              # empunhadura enrolada
        bx, by = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t; c.fill(c.mask_line(bx - 1.2, by - 1.2, bx + 1.2, by + 1.2, 1.4), hexc('#e0b040'))
    c.fill(c.mask_ell(x1 + 1, y1 - 1, 2.4, 2.4), hexc('#e0b040'), hexc('#a07820'), hexc('#fff0a0'))           # engaste dourado
    # estrela / cristal na ponta
    cx_, cy_ = 25.5, 6.5
    star = c.mask_poly([(cx_, cy_ - 5), (cx_ + 1.6, cy_ - 1.6), (cx_ + 5, cy_), (cx_ + 1.6, cy_ + 1.6), (cx_, cy_ + 5), (cx_ - 1.6, cy_ + 1.6), (cx_ - 5, cy_), (cx_ - 1.6, cy_ - 1.6)])
    c.fill(star, hexc('#b070ff'), hexc('#6a30c0'), hexc('#e8c8ff'))
    c.px(int(cx_) - 1, int(cy_) - 1, hexc('#ffffff')); c.px(int(cx_), int(cy_), hexc('#fff0ff'))
    for (dx, dy) in ((-6, -3), (4, -6), (6, 3)): c.px(int(cx_) + dx, int(cy_) + dy, hexc('#e8c8ff'))       # faiscas
    c.outline(); return c.save('i_varinha')

def flauta():
    c = Cv(); x0, y0, x1, y1 = 5, 27, 27, 5
    c.fill(c.mask_line(x0, y0, x1, y1, 4.2), hexc('#c9a060'), hexc('#7a5a34'), hexc('#f0d498'))
    for t in (.04, .5, .96):                                          # aneis de latao
        bx, by = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t; c.fill(c.mask_line(bx - 1.6, by - 1.6, bx + 1.6, by + 1.6, 1.6), hexc('#e0b040'), hexc('#a07820'), hexc('#fff0a0'))
    for t in (.24, .32, .40, .58, .66, .74):                          # furos
        bx, by = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t; c.px(int(bx), int(by), hexc('#2a1810'))
    c.px(int(x0 + (x1 - x0) * .82), int(y0 + (y1 - y0) * .82), hexc('#2a1810'))
    c.outline(); return c.save('i_flauta')

def alaude():
    c = Cv()
    body = c.mask_ell(11.5, 21, 7.4, 8.4, -.78)                      # corpo em pera, inclinado
    c.fill(body, hexc('#b5733a'), hexc('#6a3e1c'), hexc('#e0a468'))
    neck = c.mask_line(15, 16, 25, 6, 2.4); c.fill(neck, hexc('#7a4a26'), hexc('#4a2c14'), hexc('#a8703c'))
    head = c.mask_poly([(24, 4), (29, 4), (30, 9), (27, 9), (26, 6.5)]); c.fill(head, hexc('#6a3e1c'), hexc('#3a2010'), hexc('#8a5a2c'))
    c.fill(c.mask_ell(11.5, 21.5, 2.6, 2.6), hexc('#2a1408'))                                                     # boca do alaude
    c.fill(c.mask_ell(11.5, 21.5, 3.6, 3.6) & ~c.mask_ell(11.5, 21.5, 2.6, 2.6), hexc('#e0b040'), hexc('#a07820'), hexc('#fff0a0'))   # aro dourado
    for k in range(3): c.px(25 + k, 5 + (k > 1), hexc('#e0b040'))                                                  # cravelhas
    for off in (-.9, 0, .9):                                         # cordas
        for t in np.linspace(.18, .95, 28): c.px(int(8 + off + (28 - 8) * t * .8 - 0), int(25 - off - (25 - 6) * t * .82), hexc('#f4ecd0'))
    c.outline(); return c.save('i_alaude')

if __name__ == '__main__':
    ims = [f() for f in (varinha, flauta, alaude)]
    ref = [Image.open(f'{OUT}/{n}.png').convert('RGBA') for n in ('i_cetro', 'i_cajado', 'i_adaga')]
    sh = Image.new('RGBA', (96 * 6, 96), (40, 34, 52, 255))
    for k, i in enumerate(ref + ims): sh.alpha_composite(i, (k * 96, 0))
    sh.convert('RGB').save('/tmp/claude-0/-home-user-neon-wars/3ffd125f-a99a-599e-8554-f2b481e86fc1/scratchpad/icons_novos.png')
