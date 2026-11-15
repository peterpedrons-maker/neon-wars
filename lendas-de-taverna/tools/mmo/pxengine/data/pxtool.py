#!/usr/bin/env python3
"""pxtool: editor de sprites em grade de texto + verificador + visualizador.
Spec: dict(pal={char:'#rrggbb'}, rows=[...], mirror=True|False, rshade={char:char})
 - mirror: as linhas sao a METADE ESQUERDA; a direita e o espelho (com rshade aplicado = luz vinda da esquerda).
 - ops: 'del' = linhas removidas para criar variantes (agachar / saltar).
Uso: python3 pxtool.py  (gera contato ampliado de teste)"""
from PIL import Image


def build(spec, delete=()):
    rows = [r for i, r in enumerate(spec['rows']) if i not in set(delete)]
    out = []
    rs = spec.get('rshade', {})
    for r in rows:
        if spec.get('mirror'):
            right = ''.join(rs.get(c, c) for c in reversed(r))
            out.append(r + right)
        else:
            out.append(r)
    pal = spec['pal']
    w = max(len(r) for r in out)
    img = Image.new('RGBA', (w, len(out)), (0, 0, 0, 0))
    px = img.load()
    for y, r in enumerate(out):
        for x, ch in enumerate(r):
            if ch != '.':
                h = pal[ch].lstrip('#')
                px[x, y] = (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 255)
    return img, out


def lint(spec):
    """Retorna lista de avisos: linhas de tamanho diferente, caracteres sem cor, pixels soltos, contorno aberto."""
    rows = spec['rows']; pal = spec['pal']; warn = []
    w0 = len(rows[0])
    for i, r in enumerate(rows):
        if len(r) != w0: warn.append(f'linha {i}: tamanho {len(r)} != {w0}')
        for c in r:
            if c != '.' and c not in pal: warn.append(f'linha {i}: caractere {c!r} sem cor')
    if warn: return warn
    _, g = build(spec)
    h, w = len(g), len(g[0])
    keep = set(spec.get('single_ok', 'ewyrcK'))
    ink = spec.get('ink', 'K')
    for y in range(h):
        for x in range(w):
            c = g[y][x]
            if c == '.': continue
            nb = [g[y + dy][x + dx] if 0 <= y + dy < h and 0 <= x + dx < w else '.' for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))]
            if c not in keep and c not in nb:
                warn.append(f'pixel solto {c!r} em ({x},{y})')
            if c != ink and '.' in nb:
                warn.append(f'contorno aberto em ({x},{y}) [{c}]')
    return warn


def sheet(items, zoom=8, bg=(58, 110, 48), pad=4, cols=8):
    """items: lista de imagens RGBA. Retorna imagem ampliada."""
    cw = max(i.width for i in items) + pad * 2; ch = max(i.height for i in items) + pad * 2
    rowsn = (len(items) + cols - 1) // cols
    s = Image.new('RGBA', (cw * min(cols, len(items)), ch * rowsn), bg + (255,))
    for k, im in enumerate(items):
        s.alpha_composite(im, ((k % cols) * cw + pad, (k // cols) * ch + pad + (ch - pad * 2 - im.height)))
    return s.resize((s.width * zoom, s.height * zoom), Image.NEAREST)
