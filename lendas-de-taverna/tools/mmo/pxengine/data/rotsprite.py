"""RotSprite (Xenowhirl) em Python/numpy: rotacao de pixel art sem borrar nem quebrar contorno.
Passos: Scale2x (EPX) x3 = 8x -> rotacao por vizinho mais proximo -> reducao por MODA (cor mais frequente no bloco 8x8).
API: rotate(img RGBA PIL, graus, pivot=(x,y)|None, canvas=None) -> PIL RGBA (mesmo tamanho; pivot fixo). Sentido horario positivo (tela)."""
import numpy as np
from PIL import Image

def _pack(a):
    a = a.astype(np.uint32)
    return (a[..., 0] << 24) | (a[..., 1] << 16) | (a[..., 2] << 8) | a[..., 3]

def _unpack(p):
    return np.stack([(p >> 24) & 255, (p >> 16) & 255, (p >> 8) & 255, p & 255], -1).astype(np.uint8)

def _scale2x(p):
    h, w = p.shape
    q = np.pad(p, 1, mode='edge')
    P = p; A = q[:-2, 1:-1]; D = q[2:, 1:-1]; C = q[1:-1, :-2]; B = q[1:-1, 2:]
    p1 = np.where((C == A) & (C != D) & (A != B), A, P)
    p2 = np.where((A == B) & (A != C) & (B != D), B, P)
    p3 = np.where((D == C) & (D != B) & (C != A), C, P)
    p4 = np.where((B == D) & (B != A) & (D != C), D, P)
    out = np.empty((h * 2, w * 2), np.uint32)
    out[0::2, 0::2] = p1; out[0::2, 1::2] = p2; out[1::2, 0::2] = p3; out[1::2, 1::2] = p4
    return out

def _mode_blocks(p, k):
    h, w = p.shape
    b = p.reshape(h // k, k, w // k, k).transpose(0, 2, 1, 3).reshape(h // k, w // k, k * k)
    b = np.sort(b, axis=-1)
    n = b.shape[-1]
    # contagem de corridas: para cada posicao, quantos iguais ate o fim da corrida
    same = (b[..., 1:] == b[..., :-1])
    run = np.ones(b.shape, np.int32)
    for i in range(n - 2, -1, -1):
        run[..., i] = np.where(same[..., i], run[..., i + 1] + 1, 1)
    # prefere opaco em empate de contagem: peso = run*2 + (alpha>0)
    score = run * 2 + ((b & 255) > 0)
    idx = score.argmax(-1)
    return np.take_along_axis(b, idx[..., None], -1)[..., 0]

def rotate(img, deg, pivot=None, up=3):
    img = img.convert('RGBA')
    w, h = img.size
    px, py = pivot if pivot is not None else (w / 2, h / 2)
    p = _pack(np.array(img))
    # transparente = valor unico (evita matizes diferentes de alpha 0)
    p = np.where((p & 255) == 0, np.uint32(0), p)
    for _ in range(up): p = _scale2x(p)
    k = 2 ** up
    H, W = p.shape
    a = np.deg2rad(deg)
    c, s = np.cos(a), np.sin(a)
    ys, xs = np.mgrid[0:H, 0:W].astype(np.float64)
    cx, cy = (px + .0) * k, (py + .0) * k
    dx, dy = xs + .5 - cx, ys + .5 - cy
    sx = c * dx + s * dy + cx      # inversa da rotacao horaria
    sy = -s * dx + c * dy + cy
    ix, iy = np.floor(sx).astype(int), np.floor(sy).astype(int)
    ok = (ix >= 0) & (ix < W) & (iy >= 0) & (iy < H)
    out = np.zeros((H, W), np.uint32)
    out[ok] = p[iy[ok], ix[ok]]
    small = _mode_blocks(out, k)
    return Image.fromarray(_unpack(small), 'RGBA')

def rotate_nearest(img, deg, pivot=None):
    img = img.convert('RGBA'); w, h = img.size
    px, py = pivot if pivot is not None else (w / 2, h / 2)
    return img.rotate(-deg, resample=Image.NEAREST, center=(px, py))
