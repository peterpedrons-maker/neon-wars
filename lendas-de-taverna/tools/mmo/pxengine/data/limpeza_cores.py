"""Limpeza de cores (so comparacao, NAO altera os atlas do jogo): funde cores quase iguais de um atlas inteiro (mesma paleta em todos os quadros)."""
import json, numpy as np
from PIL import Image
import pxfont
A = '/home/user/neon-wars/lendas-de-taverna/mmo/assets/chars'
OUT = '/home/user/neon-wars/lendas-de-taverna/mmo/proto_pixel'
def clean(im, tol=26):
    a = np.array(im.convert('RGBA')); m = a[..., 3] > 0
    px = a[m][:, :3].astype(int); key = px[:, 0] * 65536 + px[:, 1] * 256 + px[:, 2]
    u, cnt = np.unique(key, return_counts=True); order = np.argsort(-cnt)
    cols = np.stack([(u >> 16) & 255, (u >> 8) & 255, u & 255], 1)
    kept = []; mapto = {}
    for i in order:
        c = cols[i]; best = None
        for kc in kept:
            if np.abs(c - kc).sum() <= tol * 1.7 and np.linalg.norm(c - kc) <= tol: best = kc; break
        if best is None: kept.append(c); best = c
        mapto[int(u[i])] = best
    out = a.copy(); idx = np.nonzero(m)
    for y, x in zip(*idx):
        k = int(a[y, x, 0]) * 65536 + int(a[y, x, 1]) * 256 + int(a[y, x, 2]); out[y, x, :3] = mapto[k]
    return Image.fromarray(out, 'RGBA'), len(u), len(kept)
def frame(im, j, name):
    w, h, c = j['w'], j['h'], j['cols']; i = j['anims'][name][0]
    return im.crop(((i % c) * w, (i // c) * h, (i % c) * w + w, (i // c) * h + h))
def sheet(keys, path):
    rows = []
    for k in keys:
        j = json.load(open(f'{A}/cx_{k}_atlas.json')); im = Image.open(f'{A}/cx_{k}_atlas.png').convert('RGBA')
        cl, n0, n1 = clean(im); rows.append((k, j, im, cl, n0, n1))
    w, h = rows[0][1]['w'], rows[0][1]['h']
    W = 2 * 3 * w + 30; H = 26 + len(rows) * (h + 22)
    S = Image.new('RGBA', (W, H), (28, 20, 38, 255))
    pxfont.text(S, (W // 4, 6), 'ANTES', (255, 200, 150), center=True); pxfont.text(S, (3 * W // 4, 6), 'DEPOIS', (160, 255, 170), center=True)
    for r, (k, j, im, cl, n0, n1) in enumerate(rows):
        y = 26 + r * (h + 22)
        for side, src in enumerate((im, cl)):
            for v, vn in enumerate(('idle_d', 'idle_s', 'idle_u')):
                S.alpha_composite(frame(src, j, vn), (side * (3 * w + 14) + v * w + 4, y + 14))
        pxfont.text(S, (W // 2, y + 2), f'{k.upper()}  {n0} -> {n1} CORES', (240, 226, 190), center=True)
    S.save(path); return [(r[0], r[4], r[5]) for r in rows]
if __name__ == '__main__':
    print(sheet(['grunk', 'morvath', 'gorgash', 'ratking', 'skrix'], OUT + '/limpeza_cores_1.png'))
    print(sheet(['boticario', 'presa', 'vampiro', 'goblin', 'esqueleto'], OUT + '/limpeza_cores_2.png'))
