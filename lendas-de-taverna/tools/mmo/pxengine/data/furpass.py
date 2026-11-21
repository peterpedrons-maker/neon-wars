#!/usr/bin/env python3
"""PELO COMO GRAMA (dono aprovou no Gigante; vale para TODO bicho peludo): fios curtos sobre o corpo (raiz escura, ponta clara, tombando para fora e para baixo)
+ franja de fios na silhueta (entram na máscara do motor, ganham contorno e sombra). Chifres, garras, presas e ossos NÃO ganham fios.
Seleção dos fios por HASH da posição (estável entre quadros: o pelo não "pisca", só balança com a fase t).
Uso:  img = furpass.apply(render_fn, add_cap_fn, t=fase, k=escala)
  render_fn() -> PIL RGBA (renderiza a máscara atual do fauna.Cv)
  add_cap_fn(x,y,x2,y2,r0,r1) -> adiciona um fio na região de pelo (coordenadas em pixels do quadro)"""
import math
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, binary_erosion, binary_dilation

def _h(x, y, s=0):
    return ((x * 73856093) ^ (y * 19349663) ^ (s * 83492791)) % 1000 / 1000.0

def bone_mask(rgb):
    """pixels claros (osso, chifre, garra, presa) + folga de 3px: ficam lisos"""
    b = (rgb[:, :, 0] > 175) & (rgb[:, :, 1] > 150)
    return binary_dilation(b, iterations=3)

def apply(render_fn, add_cap_fn, t=0.0, k=1.0, fringe=.20, inner=.07):
    img = render_fn(); arr = np.array(img)
    a = arr[:, :, 3] > 0
    bone = bone_mask(arr[:, :, :3].astype(int))
    bl = gaussian_filter(a.astype(float), 2.2); gy, gx = np.gradient(bl)
    edge = a & ~binary_erosion(a, iterations=2) & ~bone
    ys, xs = np.where(edge)
    for x, y in zip(xs, ys):
        if _h(x, y) >= fringe: continue
        nx, ny = -gx[y, x], -gy[y, x]; L = math.hypot(nx, ny) or 1; nx, ny = nx / L, ny / L
        ny = ny * .6 + .55
        ln = (4 + _h(x, y, 1) * 5) * k / 1.3
        sw = math.sin(t + x * .07) * 1.6 * k / 1.3
        add_cap_fn(x, y, x + nx * ln + sw, y + ny * ln, 2.0 * k / 1.3, .5)
    img2 = render_fn(); arr = np.array(img2).astype(float)
    m = arr[:, :, 3] > 0
    inn = binary_erosion(m, iterations=4) & ~bone_mask(arr[:, :, :3].astype(int))
    yy, xx = np.where(inn)
    cxm = arr.shape[1] / 2
    for x, y in zip(xx, yy):
        if _h(x, y, 2) >= inner: continue
        base = arr[y, x, :3].copy()
        ln = int(4 + _h(x, y, 3) * 5)
        dxs = np.sign(x - cxm) * .3 + math.sin(t + y * .05 + x * .03) * .5
        for q in range(ln):
            px_, py_ = int(round(x + dxs * q)), y + q
            if 0 <= px_ < arr.shape[1] and 0 <= py_ < arr.shape[0] and inn[py_, px_]:
                f = .82 + .4 * (q / max(1, ln - 1))
                arr[py_, px_, :3] = np.clip(base * f + (8 if q == ln - 1 else 0), 0, 255)
    return Image.fromarray(arr.astype(np.uint8), 'RGBA')
