#!/usr/bin/env python3
"""chibi: heroi no estilo 'dib' (cabeca enorme ~2/3, corpo minusculo, tudo numa massa so, 2-3 tons por cor).
Replica a construcao do sprite de referencia do dono: cabeca desenhada a mao, mãos em bloco, botas, contorno unico.
Vistas: down (frente), up (costas), right (lado; left = espelho). Andar 8 quadros, parado 6, ataque 10 poses."""
import math
from PIL import Image
from pxrig import Grid, autoline, line_pts

PAL = dict(K='#2a1420',
           R='#9a3030', r='#e84820', O='#f08018', L='#f8b060',
           s='#f2c99a', S='#e08c68', p='#f8e0bc', m='#6a3a4a',
           k='#14101a', w='#ffffff', b='#2e86c8', B='#1c4a98', j='#2e86c8', Z='#fff4b0', z='#ff9a30', Y='#c83010', X='#ffd070', U='#5a46c8', u='#8a78f0', V='#2e2278', F='#f8f0e0', f='#d04040',
           T='#8a2c38', t='#b83c44', M='#5a2836',
           c='#7cc0f0', C='#3a86d0', D='#1c4a98',
           y='#f8b828', o='#e07a18', Q='#f08018', q='#f8b060',
           A='#f6faff', a='#9cb0d2', g='#e8b840', N='#6e4228')
SEL = {**{k: '#5a2430' for k in 'RrOL'}, **{k: '#7a4050' for k in 'sSpm'}, **{k: '#14101a' for k in 'kwbB'},
       **{k: '#4a2030' for k in 'TtM'}, **{k: '#14306a' for k in 'cCDj'}, **{k: '#5a3010' for k in 'yoQq'}, **{k: '#26324e' for k in 'AagN'}}


def _pal(over):
    d = dict(PAL); d.update(over); return d


PALS = {
    'warrior': PAL,
    'mage': _pal(dict(R='#4a3290', r='#8a5ad0', O='#b896f4', L='#e6d4ff', T='#3a2a7a', t='#5e46b8', M='#241a58', c='#fff0a0', C='#f0c040', D='#a07820',
                      y='#f0e8ff', o='#c8b8f0', Q='#6a3aa0', q='#9a6ad0', j='#4a3a98',
                      U='#3a3898', u='#6a68d0', V='#22206a', Z='#fff4b0', z='#ff9a30', Y='#c83010', X='#ffd070')),
    'archer': _pal(dict(R='#5a3418', r='#c0442c', O='#b06a30', L='#e0a868', T='#1c5a30', t='#3a9a48', M='#103a1c', c='#f8f0c0', C='#e8d890', D='#a09050',
                        y='#d8b060', o='#8a6a30', Q='#6a4228', q='#a07850', j='#d8c890',
                        U='#3a9a48', u='#6acb60', V='#1c5a30', F='#f8f0e0', f='#d04040')),
}
SELS = {
    'warrior': SEL,
    'mage': {**SEL, **{k: '#3a2470' for k in 'RrOL'}, **{k: '#1c1450' for k in 'TtM'}, **{k: '#5a3a10' for k in 'cCD'}, **{k: '#1c1450' for k in 'UuVyoQqXj'}, **{k: '#601000' for k in 'ZzY'}},
    'archer': {**SEL, **{k: '#3a2010' for k in 'RrOL'}, **{k: '#0e3a1c' for k in 'TtMUuV'}, **{k: '#5a4a20' for k in 'cCDyoQqj'}, **{k: '#6a5a50' for k in 'Ff'}},
}


def _row(*segs, n=None):
    r = ''.join(c * k for c, k in segs)
    if n: assert len(r) == n, (len(r), r)
    return r


# ---------------------------------------------------------------- CABECA FRONTAL (metade esquerda, 11 col -> 22x18)
HEAD_F = [
    '....RRRRRRR', '..RROOOOOOO', '.ROOLLOOOOO', '.ROOLOOOOOO', 'RROOOOOOOOO', 'ROOOOOOOOOO',
    'ROOOOOOOOOO', 'ROOrOOOOrOO', 'ROOOOOssOOs', 'RrOOssssssp',
    'RrOsskkkssp', 'RrOswwbssss', 'ROOswbbssss', '.rOssbBssss',
    '..mSSsssssp', '...sssssssk', '....ssssssS', '......SSSSS']
HEAD_F_SHOUT = ['...sssssskk'] if False else None
RSH_F = dict(L='O', p='s')
# CABECA DE COSTAS
HEAD_B = [
    '....RRRRRRR', '..RROOOOOOO', '.ROOLLOOOOO', '.ROOLOOOOOO', 'RROOOOOOOOO', 'ROOOOOOOOOO',
    'ROOOOOOOOOO', 'ROOrOOOOrOO', 'ROOOOOOOOOO', 'ROOOOOOOOOO', 'ROOOOOOOrOO', 'ROOOOOOOOOO',
    'RrOOOOOOOOO', '.ROOOOOOOOO', '..RrOOOOOOO', '...RROOOOOO', '.....RSSSSS', '......SSSSS']
# CABECA LATERAL (olhando para a direita) 21x18, construida como a frontal: cabelo bob + franja + mecha lateral + rosto redondo
def make_head_side(mouth='n', eyes='open'):
    Wd, Hd = 21, 18
    bounds = [(4, 16), (2, 18), (1, 19), (1, 19), (0, 19), (0, 19), (0, 19), (0, 19), (0, 19), (0, 19), (0, 19), (0, 20), (0, 20), (1, 19), (1, 19), (2, 19), (4, 18), (6, 16)]
    hair_end = [99, 99, 99, 99, 99, 99, 99, 99, 13, 12, 12, 12, 12, 11, 10, 9, 7, -1]
    g = [['.'] * Wd for _ in range(Hd)]
    for r in range(Hd):
        l, rr = bounds[r]
        for c in range(l, rr + 1):
            g[r][c] = 'O' if c <= hair_end[r] else 's'
    # franja irregular sobre a testa (linha 8) e pontas
    for c, ch in zip(range(14, 20), 'OsOssO'): g[8][c] = ch
    for c in range(14, 20): g[9][c] = 's'
    # aro escuro do cabelo (topo e costas)
    for r in range(Hd):
        cols = [c for c in range(Wd) if g[r][c] == 'O']
        if not cols: continue
        g[r][cols[0]] = 'R'
        if r == 0:
            for c in cols: g[r][c] = 'R'
        if r == 1:
            for c in cols[:2] + cols[-2:]: g[r][c] = 'R'
        if r in (2, 3) and len(cols) > 1: g[r][cols[1]] = 'R'
        if r in (13, 14, 15, 16): g[r][cols[-1]] = 'R'
    # luz e acentos do cabelo
    g[2][4] = 'L'; g[2][5] = 'L'; g[3][4] = 'L'
    g[6][8] = 'r'; g[7][15] = 'r'; g[9][3] = 'r'; g[10][2] = 'r'; g[12][4] = 'r'; g[13][6] = 'r'; g[9][12] = 'r'; g[10][12] = 'r'; g[11][12] = 'r'
    # olho grande (3x4), bochecha, boca, nariz, queixo
    if eyes == 'open':
        for dc, ch in enumerate('kkk'): g[10][14 + dc] = ch
        for dc, ch in enumerate('wwb'): g[11][14 + dc] = ch
        for dc, ch in enumerate('wbb'): g[12][14 + dc] = ch
        for dc, ch in enumerate('sbB'): g[13][14 + dc] = ch
    else:
        for dc in range(3): g[11][14 + dc] = 'k'
    g[14][13] = 'S'; g[14][14] = 'S'
    g[11][20] = 'p'; g[12][20] = 'S'
    if mouth == 'n':
        g[15][16] = 'k'; g[15][17] = 'k'
    else:
        for c in range(15, 19): g[15][c] = 'k'
        g[16][16] = 'k'; g[16][17] = 'k'
    for c in range(8, 14): g[17][c] = 'S'
    for c in range(14, 17): g[16][c] = 'S' if g[16][c] == 's' else g[16][c]
    return [''.join(r) for r in g]


HEAD_S = make_head_side()
MOUTH_F_OPEN = '...sskkksssk'[:11]
# ---------------------------------------------------------------- CORPO / MAOS / BOTAS
BODY_F_TOP = ['.cCCCC', '.ttttt']                      # (metade; 6 col)  lenco + peito
BODY_F_MID = '.ttttt'
BODY_F_FOLD = '.tttMt'
BODY_F_BELT = '.oyyyy'
BODY_F_HEM = '..TTTT'
BODY_B_TOP = ['.cCCCC', '.cttCC']
MITT_L = ['pss', 'sss', '.sS']
BOOT_F = ['jjj', 'QQQ', 'qQQ']
BOOT_S = ['.jj..', '.QQQq', 'QQQQQ']

BODY_S = dict(sc='.cCCCCD.', t0='.tttttT.', t1='.ttttTT.', t2='.tttMTT.', belt='.oyyyyo.', hem='..TTTT..')


# ---------------------------------------------------------------- espada (peca separada)
def sword_rows(hand, ang, length=10):
    """Retorna Grid proprio da espada (cabo, guarda, lamina) com contorno proprio; hand e ponto de empunhadura (coords globais)."""
    a = math.radians(ang)
    ux, uy = math.sin(a), math.cos(a)
    tip = (hand[0] + ux * length, hand[1] + uy * length)
    pts = line_pts(round(hand[0] - ux * 2), round(hand[1] - uy * 2), round(tip[0]), round(tip[1]))
    cells = {}
    for i, (x, y) in enumerate(pts):
        d = i
        if d < 2: cells[(x, y)] = 'N'
        elif d == 2:
            nx, ny = -uy, ux
            for k in (-3, -2, -1, 0, 1, 2, 3): cells[(round(x + nx * k), round(y + ny * k))] = 'g'
        else:
            cells[(x, y)] = 'A'
            ox, oy = (1, 0) if abs(uy) >= abs(ux) else (0, 1)
            if i < len(pts) - 1: cells.setdefault((x + ox, y + oy), 'a')
    cells[(round(tip[0]), round(tip[1]))] = 'A'
    return cells, tip



def staff_rows(hand, ang, length=24, orb=1):
    """Cajado SEPARADO: cabo na mao, orbe de fogo no topo (orb 0..3 = tamanho do brilho)."""
    a = math.radians(ang)
    ux, uy = math.sin(a), math.cos(a)
    bx, by = hand[0] - ux * 7, hand[1] - uy * 7
    tip = (hand[0] + ux * (length - 7), hand[1] + uy * (length - 7))
    cells = {}
    pts = line_pts(round(bx), round(by), round(tip[0]), round(tip[1]))
    for i, (x, y) in enumerate(pts):
        cells[(x, y)] = 'g' if i == 0 else 'N'
    tx, ty = round(tip[0]), round(tip[1])
    for dx, dy in ((-1, 0), (1, 0), (0, 1)): cells[(tx + dx, ty + dy)] = 'g'           # garra de ouro
    ox, oy = round(tip[0] + ux * 3), round(tip[1] + uy * 3)
    r = {0: 1, 1: 2, 2: 3, 3: 4}[orb]
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            d = math.hypot(dx, dy)
            if d <= r + .3:
                cells[(ox + dx, oy + dy)] = 'Z' if d < r * .45 else 'z' if d < r * .85 else 'Y'
    return cells, (ox, oy)


def bow_rows(center, d, draw=0, arrow=True):
    """Arco SEPARADO + flecha (apontando para d=(dx,dy) unitario). Retorna cells, ponta da flecha, ponto onde a mao de puxar fica."""
    dx, dy = d
    px_, py_ = -dy, dx
    cells = {}
    n = 16
    prev = None
    top = None; bot = None
    for i in range(n + 1):
        t = -1 + 2 * i / n
        bulge = 3.0 * (1 - t * t)
        x = center[0] + px_ * t * 8 + dx * bulge
        y = center[1] + py_ * t * 8 + dy * bulge
        if prev is not None:
            for (xx, yy) in line_pts(round(prev[0]), round(prev[1]), round(x), round(y)): cells[(xx, yy)] = 'N'
        prev = (x, y)
        if i == 0: top = (x, y)
        if i == n: bot = (x, y)
    pull = (center[0] - dx * draw, center[1] - dy * draw)
    for p0 in (top, bot):
        for (xx, yy) in line_pts(round(p0[0]), round(p0[1]), round(pull[0]), round(pull[1])): cells.setdefault((xx, yy), 'a')
    cells[(round(top[0]), round(top[1]))] = 'g'; cells[(round(bot[0]), round(bot[1]))] = 'g'
    tip = (center[0] + dx * 9, center[1] + dy * 9)
    if arrow:
        for (xx, yy) in line_pts(round(pull[0]), round(pull[1]), round(tip[0]), round(tip[1])): cells[(xx, yy)] = 'q'
        cells[(round(tip[0]), round(tip[1]))] = 'A'
        cells[(round(tip[0] - dx), round(tip[1] - dy))] = 'A'
        for k in (0, 1, 2):
            fx, fy = round(pull[0] + dx * k), round(pull[1] + dy * k)
            cells[(fx + round(px_), fy + round(py_))] = 'r'; cells[(fx - round(px_), fy - round(py_))] = 'r'
    return cells, tip, pull


def weapon_rows(swd, hxy, view, back=False, bow_center=None):
    """Roteador de armas. Retorna (cells, tip, behind, mitts2)."""
    kind = swd.get('kind', 'sword')
    if kind == 'staff':
        cells, tip = staff_rows(hxy, swd.get('ang', 180), swd.get('len', 24), swd.get('orb', 1))
        return cells, tip, False, []
    if kind == 'bow':
        c = bow_center or hxy
        cells, tip, pull = bow_rows(c, swd['dir'], swd.get('draw', 0), swd.get('arrow', True))
        return cells, tip, (back and swd['dir'][1] < 0), [pull]
    cells, tip = sword_rows(hxy, swd['ang'], swd.get('len', 12))
    behind = (back or (185 <= swd['ang'] <= 265)) if view == 'front' else (185 <= swd['ang'] <= 265)
    return cells, tip, behind, []


# ---------------------------------------------------------------- acessorios por classe
HAT_F = ['..........u', '..........U', '.........uU', '.........uU', '........uUU', '........uUU', '.......uUUU', '.......XXXX', 'VUUUUUUUUUU', '.VVVVVVVVVV']


def hat_side():
    rows = []
    for k in range(8):
        w = 2 + (k // 2) * 2 + 2 if k < 6 else 10
        w = [2, 2, 4, 4, 6, 6, 8, 8][k]
        start = 11 - w // 2 - int((7 - k) * 0.45)
        r = ['.'] * 23
        for i in range(w): r[start + i] = 'u' if i == 0 else 'U'
        if k == 7:
            for i in range(w): r[start + i] = 'X'
        rows.append(''.join(r))
    rows.append('V' + 'U' * 21 + 'V')
    rows.append('.' + 'V' * 21 + '.')
    return rows


def cap_head(rows, view):
    """Boné do arqueiro: recolore o topo do cabelo."""
    mp = {'R': 'V', 'O': 'U', 'L': 'u', 'r': 'U'}
    out = []
    for i, r in enumerate(rows):
        if i <= 5: r = ''.join(mp.get(c, c) for c in r)
        elif i == 6: r = ''.join('V' if c in 'ROLr' else c for c in r)
        out.append(r)
    return out


def cap_head_side(rows):
    out = cap_head(rows, 'side')
    r7 = ''.join('V' if c in 'ROLr' else c for c in out[7])
    out[7] = r7
    r8 = list(out[8])
    for i in range(16, min(21, len(r8))):
        if r8[i] != '.': r8[i] = 'V'
    out[8] = ''.join(r8)
    return out


def accessory(g, cls, view, hx, hy, back=False):
    if cls == 'mage':
        if view == 'side': g.stamp(hat_side(), hx - 1, hy - 4)
        else: g.stamp(HAT_F, hx, hy - 4, mirror=True, rshade=dict(u='U'))
    elif cls == 'archer':
        if view == 'side': g.stamp(['..F', '.Ff', 'Ff.', 'f..'], hx + 4, hy - 3)
        else: g.stamp(['..F', '.Ff', 'Ff.', 'f..'], hx + 17, hy - 3)


def stamp_cells(g, cells):
    for (x, y), c in cells.items(): g.put(x, y, c)
    for (x, y) in list(cells):
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if g.get(x + dx, y + dy) == '.': g.put(x + dx, y + dy, 'K')


# ---------------------------------------------------------------- composicao
W, H = 40, 44
BASE = 38


def build_front(p, back=False):
    """p: dict(dx,dy,hdx,hdy,tn,al,ar,bl,br,sw,face,hand) -> (Grid, tip)."""
    g = Grid(W, H)
    dx, dy = p.get('dx', 0), p.get('dy', 0)
    tn = p.get('tn', 3)
    bl, br = p.get('bl', (0, 0)), p.get('br', (0, 0))      # (dx, lift)
    cx = W // 2
    base = BASE + dy
    boot_top = base - 3
    body_h = tn + 3
    body_top = boot_top - body_h
    my0 = body_top + 2
    cls = p.get('cls', 'warrior')
    swd = p.get('sw'); tip = None; hxy = None; behind = False; hands2 = []
    if swd:
        side = swd.get('side', 'r')
        al_, ar_ = p.get('al', (0, 0)), p.get('ar', (0, 0))
        hxy = (cx + (7 if side == 'r' else -7) + dx + (ar_ if side == 'r' else al_)[0] + 1, my0 + 1 + (ar_ if side == 'r' else al_)[1])
        if side != 'r': hxy = (hxy[0] - 1, hxy[1])
        cells, tip, behind, hands2 = weapon_rows(swd, hxy, 'front', back, (cx + dx + 1, my0 + 3))
        if behind: stamp_cells(g, cells)
    # botas
    g.stamp(BOOT_F, cx - 5 + dx + bl[0], boot_top - bl[1])
    g.stamp(BOOT_F, cx + 2 + dx + br[0], boot_top - br[1])
    # corpo (metade espelhada)
    rows = (BODY_B_TOP if back else BODY_F_TOP) + [BODY_F_MID] * max(0, tn - 2) + [BODY_F_FOLD if tn >= 3 else BODY_F_MID, BODY_F_BELT, BODY_F_HEM]
    rows = rows[:body_h]
    g.stamp(rows, cx - 6 + dx, body_top, mirror=True, rshade=dict(t='T', c='C', y='o'))
    if cls == 'mage': g.stamp(['.tttttT', 'TTTTTTT'], cx - 7 + dx, boot_top - 1, mirror=True, rshade=dict(t='T'))
    # maos (blocos de pele)
    al, ar = p.get('al', (0, 0)), p.get('ar', (0, 0))
    my = body_top + 2
    bow = bool(swd and swd.get('kind') == 'bow')
    if not p.get('nomitt'):
        if not (bow and hands2): g.stamp(MITT_L, cx - 9 + dx + al[0], my + al[1])
        if not bow: g.stamp([r[::-1] for r in MITT_L], cx + 6 + dx + ar[0], my + ar[1])
    # cabeca
    hx, hy = cx - 11 + dx + p.get('hdx', 0), body_top - 17 + p.get('hdy', 0)
    head = list(HEAD_B if back else HEAD_F)
    if cls == 'archer': head = cap_head(head, 'front')
    if p.get('face') == 'shout' and not back:
        head[15] = '...sskkksssk'
    if p.get('face') == 'blink' and not back:
        head[10] = 'RrOsskkkssp'; head[11] = 'RrOssssssss'; head[12] = 'ROOssssssss'; head[13] = '.rOssssssss'
    g.stamp(head, hx, hy, mirror=True, rshade=RSH_F)
    accessory(g, cls, 'front', hx, hy, back)
    for hp in hands2:
        for (ox, oy) in ((0, 0), (1, 0), (0, 1), (1, 1)): g.put(round(hp[0]) + ox, round(hp[1]) + oy, 's')
    if bow:
        bc = (cx + dx + 1, my0 + 3)
        for (ox, oy) in ((0, 0), (1, 0), (0, 1), (1, 1)): g.put(round(bc[0]) + ox - 1, round(bc[1]) + oy - 1, 's')
    autoline(g)
    # espada separada (por cima do corpo, exceto quando passa atras da cabeca)
    if swd:
        if not behind: stamp_cells(g, cells)
        if bow:
            bc = (cx + dx + 1, my0 + 3)
            for (ox, oy) in ((0, 0), (1, 0), (0, 1), (1, 1)): g.put(round(bc[0]) - 1 + ox, round(bc[1]) - 1 + oy, 's' if oy == 0 else 'S')
            for hp in hands2:
                for (ox, oy) in ((0, 0), (1, 0), (0, 1), (1, 1)): g.put(round(hp[0]) + ox, round(hp[1]) + oy, 's' if oy == 0 else 'S')
        else:
            for (ox, oy) in ((0, 0), (1, 0), (0, 1), (1, 1)):
                g.put(round(hxy[0]) - 1 + ox, round(hxy[1]) - 1 + oy, 's' if oy == 0 else 'S')
    return g, tip, behind


def build_side(p):
    g = Grid(W, H)
    dx, dy = p.get('dx', 0), p.get('dy', 0)
    tn = p.get('tn', 3)
    cx = W // 2
    base = BASE + dy
    boot_top = base - 3
    body_h = tn + 3
    body_top = boot_top - body_h
    bk, bf = p.get('bl', (0, 0)), p.get('br', (0, 0))      # pe de tras, pe da frente (dx, lift)
    ab_, af_ = p.get('al', (0, 0)), p.get('ar', (0, 0))
    cls = p.get('cls', 'warrior')
    swd = p.get('sw'); tip = None; behind = False; hands2 = []
    if swd:
        hxy = (cx + 4 + dx + af_[0] + 1, body_top + 4 + af_[1])
        cells, tip, behind, hands2 = weapon_rows(swd, hxy, 'side', False, (hxy[0] + 2, hxy[1]))
        if behind: stamp_cells(g, cells)
    g.stamp(BOOT_S, cx - 6 + dx + bk[0], boot_top - bk[1])
    g.stamp(BOOT_S, cx - 1 + dx + bf[0], boot_top - bf[1])
    rows = [BODY_S['sc'], BODY_S['t0']] + [BODY_S['t1']] * max(0, tn - 2) + [BODY_S['t2'], BODY_S['belt'], BODY_S['hem']]
    rows = rows[:body_h]
    g.stamp(rows, cx - 5 + dx + p.get('bdx', 0), body_top)
    if cls == 'mage': g.stamp(['.tttttttTT.', 'TTTTTTTTTTT'], cx - 6 + dx + p.get('bdx', 0), boot_top - 1)
    fl = p.get('flut', 0)
    g.stamp(['CC.', '.CD', '..D'], cx - 8 + dx + p.get('bdx', 0) - fl, body_top + fl // 2)
    # braco de tras (so um bloco atras) e da frente
    ab, af = p.get('al', (0, 0)), p.get('ar', (0, 0))
    if not p.get('nomitt'): g.stamp(['ss', 'sS'], cx - 6 + dx + ab[0], body_top + 3 + ab[1])
    # cabeca (perfil)
    hx, hy = cx - 11 + dx + p.get('hdx', 0), body_top - 17 + p.get('hdy', 0)
    head = make_head_side('shout' if p.get('face') == 'shout' else 'n', 'closed' if p.get('face') == 'blink' else 'open')
    if cls == 'archer': head = cap_head_side(head)
    g.stamp(head, hx, hy)
    accessory(g, cls, 'side', hx, hy)
    if not p.get('nomitt'): g.stamp(['ss', 'sS'], cx + 3 + dx + af[0], body_top + 3 + af[1])
    autoline(g)
    if swd:
        if not behind: stamp_cells(g, cells)
        bowd = swd.get('kind') == 'bow'
        mc = (hxy[0] + 2, hxy[1]) if bowd else hxy
        g.put(round(mc[0]) - 1, round(mc[1]) - 1, 's'); g.put(round(mc[0]), round(mc[1]) - 1, 's')
        g.put(round(mc[0]) - 1, round(mc[1]), 'S'); g.put(round(mc[0]), round(mc[1]), 'S')
        for hp in hands2:
            g.put(round(hp[0]) - 1, round(hp[1]) - 1, 's'); g.put(round(hp[0]), round(hp[1]) - 1, 's')
            g.put(round(hp[0]) - 1, round(hp[1]), 'S'); g.put(round(hp[0]), round(hp[1]), 'S')
    return g, tip, behind


def render(g, cls='warrior'):
    return g.render(PALS[cls], SELS[cls])


# ---------------------------------------------------------------- animacoes
def walk_params(f, n=8, view='down'):
    ph = 2 * math.pi * f / n
    s = math.sin(ph); c = math.cos(ph)
    up = abs(s)
    p = dict(dy=-1 if up > .7 else 0, tn=3, hdy=0 if up < .7 else 0)
    if view in ('down', 'up'):
        p['bl'] = (0, max(0, s) * 2.2); p['br'] = (0, max(0, -s) * 2.2)
        p['bl'] = (0, round(p['bl'][1])); p['br'] = (0, round(p['br'][1]))
        p['al'] = (0, round(c * 1.2)); p['ar'] = (0, round(-c * 1.2))
        p['hdx'] = 0
    else:
        p['bl'] = (round(c * 3), round(max(0, -s) * 2)); p['br'] = (round(-c * 3), round(max(0, s) * 2))
        p['al'] = (round(c * 2), 0); p['ar'] = (round(-c * 2), 0)
    p['sw'] = dict(ang=165, len=11, side='r') if view != 'right' else dict(ang=100, len=11)
    p['flut'] = int(round(max(0, c) * 2))
    return p


def idle_params(f, n=6, view='down'):
    s = math.sin(2 * math.pi * f / n)
    p = dict(tn=3 if s > -.3 else 3, hdy=0, dy=0)
    p['hdy'] = 0 if s < .3 else -1 if False else 0
    p['tn'] = 3 if s < .5 else 4
    p['sw'] = dict(ang=170, len=11, side='r') if view != 'right' else dict(ang=105, len=11)
    return p


ATK_F = [   # frente (espada na mao direita da tela, golpe de cima-direita para baixo-esquerda)
    dict(tn=3, ar=(0, 0), sw=dict(ang=165, len=12, side='r')),
    dict(tn=2, dy=0, hdy=0, ar=(0, -1), al=(0, 1), sw=dict(ang=190, len=12, side='r')),
    dict(tn=3, hdy=-1, ar=(0, -3), al=(0, 1), sw=dict(ang=200, len=12, side='r'), face='shout'),
    dict(tn=3, hdy=-1, hdx=1, ar=(0, -5), al=(-1, 2), sw=dict(ang=205, len=12, side='r')),
    dict(tn=3, hdy=0, ar=(0, -5), al=(-1, 2), sw=dict(ang=235, len=12, side='r'), face='shout'),
    dict(tn=3, dy=1, hdy=1, ar=(-1, -1), al=(0, 1), sw=dict(ang=300, len=12, side='r'), face='shout'),
    dict(tn=2, dy=2, hdy=1, ar=(-3, 2), al=(0, 0), bl=(-1, 0), br=(2, 0), sw=dict(ang=350, len=12, side='r'), face='shout'),
    dict(tn=2, dy=2, hdy=1, ar=(-4, 2), al=(0, 0), bl=(-1, 0), br=(2, 0), sw=dict(ang=345, len=12, side='r')),
    dict(tn=3, dy=1, ar=(-2, 1), sw=dict(ang=10, len=12, side='r')),
    dict(tn=3, ar=(0, 0), sw=dict(ang=150, len=12, side='r')),
]
ATK_B = [dict(q) for q in ATK_F]
for _i, _a in {5: 195, 6: 172, 7: 168, 8: 160, 9: 150}.items():
    ATK_B[_i]['sw'] = dict(ang=_a, len=12, side='r')
for _i in (5, 6, 7, 8):
    ATK_B[_i]['ar'] = (int(round(ATK_F[_i]['ar'][0] * .5)), -2)
ATK_S = [
    dict(tn=3, sw=dict(ang=105, len=12), ar=(1, 0)),
    dict(tn=2, hdx=-1, bdx=-1, ar=(-1, -1), al=(1, 0), sw=dict(ang=150, len=12)),
    dict(tn=3, hdx=-2, bdx=-1, hdy=0, dx=-1, ar=(-2, -3), al=(2, 0), sw=dict(ang=205, len=12), face='shout'),
    dict(tn=3, hdx=-3, bdx=-2, dx=-2, ar=(-2, -5), al=(3, 0), sw=dict(ang=235, len=12)),
    dict(tn=3, hdx=-1, bdx=-1, dx=-1, ar=(0, -5), al=(2, 0), sw=dict(ang=190, len=12), face='shout'),
    dict(tn=3, hdx=2, bdx=1, dx=1, ar=(3, -2), al=(-1, 0), sw=dict(ang=120, len=12), face='shout'),
    dict(tn=2, dy=1, hdx=4, bdx=2, dx=3, ar=(5, 1), al=(-2, 0), bl=(-2, 0), br=(2, 0), sw=dict(ang=85, len=12), face='shout'),
    dict(tn=2, dy=1, hdx=4, bdx=2, dx=3, ar=(5, 2), al=(-2, 0), bl=(-2, 0), br=(2, 0), sw=dict(ang=60, len=12)),
    dict(tn=3, hdx=2, bdx=1, dx=2, ar=(3, 1), al=(-1, 0), bl=(-1, 0), br=(1, 0), sw=dict(ang=75, len=12)),
    dict(tn=3, hdx=1, bdx=0, dx=1, ar=(1, 0), sw=dict(ang=100, len=12)),
]


def anim(view, kind, cls='warrior', ps_override=None):
    out = []
    if kind == 'walk': ps = [walk_params(f, 8, view) for f in range(8)]
    elif kind == 'idle': ps = [idle_params(f, 6, view) for f in range(6)]
    else: ps = ATK_S if view == 'right' else (ATK_B if view == 'up' else ATK_F)
    if ps_override is not None: ps = ps_override
    for p in ps:
        p = dict(p, cls=cls)
        if view == 'right': g, tip, bh = build_side(p)
        else: g, tip, bh = build_front(p, back=(view == 'up'))
        out.append((render(g, cls), tip, bh))
    return out


def sheet(path, zoom=4):
    rows = []
    for view in ('down', 'up', 'right'):
        rows.append(anim(view, 'walk')); rows.append(anim(view, 'attack'))
    S = Image.new('RGBA', (W * 10, H * len(rows)), (58, 110, 48, 255))
    for r, row in enumerate(rows):
        for i, (im, tip, bh) in enumerate(row): S.alpha_composite(im, (i * W, r * H))
    S.resize((S.width * zoom, S.height * zoom), Image.NEAREST).convert('RGB').save(path)


if __name__ == '__main__':
    sheet('/tmp/claude-0/-home-user-neon-wars/3ffd125f-a99a-599e-8554-f2b481e86fc1/scratchpad/chibi_v1.png', 3)
    print('ok')
