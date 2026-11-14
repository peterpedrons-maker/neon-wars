#!/usr/bin/env python3
"""pxrig: monta sprites pixel art por PARTES (cabeca, tronco, pernas, bracos, arma separada) em grade de caracteres.
Contorno seletivo (cor escura do proprio material), pernas que andam (ciclo de 4 poses), arma como peca a parte."""
from PIL import Image


class Grid:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.c = [['.'] * w for _ in range(h)]

    def stamp(self, rows, x, y, mirror=False, rshade=None, solid=False):
        rs = rshade or {}
        for j, r in enumerate(rows):
            if mirror:
                r = r + ''.join(rs.get(ch, ch) for ch in reversed(r))
            for i, ch in enumerate(r):
                if ch == '.' and not solid: continue
                xx, yy = x + i, y + j
                if 0 <= xx < self.w and 0 <= yy < self.h:
                    self.c[yy][xx] = ch
        return self

    def put(self, x, y, ch):
        if 0 <= x < self.w and 0 <= y < self.h: self.c[y][x] = ch

    def get(self, x, y):
        return self.c[y][x] if 0 <= x < self.w and 0 <= y < self.h else '.'

    def rows(self):
        return [''.join(r) for r in self.c]

    def render(self, pal, sel=None):
        """sel: dict material->cor de contorno (contorno seletivo). Contorno 'K' vira cor escura do vizinho mais proximo."""
        img = Image.new('RGBA', (self.w, self.h), (0, 0, 0, 0))
        px = img.load()
        for y in range(self.h):
            for x in range(self.w):
                ch = self.c[y][x]
                if ch == '.': continue
                if ch == 'K' and sel:
                    # procura vizinho nao-K (4 e diagonais) para herdar matiz
                    best = None
                    for dx, dy in ((0, 1), (1, 0), (-1, 0), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)):
                        n = self.get(x + dx, y + dy)
                        if n not in ('.', 'K') and n in sel:
                            best = sel[n]; break
                    col = best or pal['K']
                else:
                    col = pal[ch]
                h = col.lstrip('#')
                px[x, y] = (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 255)
        return img


def line_pts(x0, y0, x1, y1):
    pts = []
    dx, dy = abs(x1 - x0), -abs(y1 - y0)
    sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
    err = dx + dy
    while True:
        pts.append((x0, y0))
        if x0 == x1 and y0 == y1: break
        e2 = 2 * err
        if e2 >= dy: err += dy; x0 += sx
        if e2 <= dx: err += dx; y0 += sy
    return pts


def make_weapon(kind, p0, p1, pal_chars):
    """Arma SEPARADA: devolve (Grid, origem) com cabo, guarda e lamina, contorno proprio.
    kind 'sword' | 'club'. p0 = ponta do cabo (na mao), p1 = ponta da arma (coordenadas locais)."""
    xs = [p0[0], p1[0]]; ys = [p0[1], p1[1]]
    pad = 3
    ox, oy = min(xs) - pad, min(ys) - pad
    g = Grid(max(xs) - min(xs) + pad * 2 + 1, max(ys) - min(ys) + pad * 2 + 1)
    a = (p0[0] - ox, p0[1] - oy); b = (p1[0] - ox, p1[1] - oy)
    pts = line_pts(a[0], a[1], b[0], b[1])
    n = len(pts)
    import math
    L = math.hypot(b[0] - a[0], b[1] - a[1]) or 1
    ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
    nx, ny = -uy, ux
    if kind == 'sword':
        grip = 2
        for i, (x, y) in enumerate(pts):
            if i < grip: g.put(x, y, 't')
            elif i == grip:
                for k in (-2, -1, 0, 1, 2):
                    g.put(round(x + nx * k), round(y + ny * k), 'g')
            else:
                g.put(x, y, 'A' if i % 3 else 'a')
        g.put(*pts[-1], 'A')
    else:  # clava
        for i, (x, y) in enumerate(pts):
            g.put(x, y, 't')
        hx, hy = pts[-1]
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                g.put(hx + dx, hy + dy, 'm')
        g.put(hx - 1, hy - 1, 'M'); g.put(hx, hy - 1, 'M'); g.put(hx + 1, hy + 1, 'T'); g.put(hx, hy + 1, 'T')
    # contorno proprio da arma
    out = Grid(g.w, g.h)
    for y in range(g.h):
        for x in range(g.w):
            out.c[y][x] = g.c[y][x]
    for y in range(g.h):
        for x in range(g.w):
            if g.c[y][x] == '.':
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    if g.get(x + dx, y + dy) != '.':
                        out.c[y][x] = 'K'; break
    return out, (ox, oy)


def autoline(g, ch='K'):
    """Contorno de 1px em volta de tudo (nas celulas vazias vizinhas de pixels)."""
    add = []
    for y in range(-1, g.h + 1):
        for x in range(-1, g.w + 1):
            if g.get(x, y) == '.':
                if any(g.get(x + dx, y + dy) not in ('.', ch) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                    add.append((x, y))
    for x, y in add: g.put(x, y, ch)
    return g
