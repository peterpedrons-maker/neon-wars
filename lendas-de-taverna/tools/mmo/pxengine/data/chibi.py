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
           A='#f6faff', a='#9cb0d2', g='#e8b840', N='#6e4228', G='#fff0a0')
SEL = {**{k: '#5a2430' for k in 'RrOL'}, **{k: '#7a4050' for k in 'sSpm'}, **{k: '#14101a' for k in 'kwbB'},
       **{k: '#4a2030' for k in 'TtM'}, **{k: '#14306a' for k in 'cCDj'}, **{k: '#5a3010' for k in 'yoQq'}, **{k: '#26324e' for k in 'AagN'}}


DEFAULT_HAT = {'warrior': 'none', 'mage': 'wizard', 'archer': 'cap', 'rogue': 'hood', 'cleric': 'circlet'}
DEFAULT_OUTFIT = {'warrior': 'cloth', 'mage': 'robe', 'archer': 'cloth', 'rogue': 'cloth', 'cleric': 'robe'}


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
PALS['rogue'] = _pal(dict(R='#1a1a28', r='#4a4a68', O='#34344a', L='#6a6a90', T='#2e2e44', t='#4a4a68', M='#1a1a28', c='#ff7a6a', C='#d03a3a', D='#8a1c24',
                          y='#c8c8d8', o='#8a8aa0', Q='#2a2a3a', q='#4a4a60', j='#d03a3a', U='#3a3a52', u='#5c5c7c', V='#1a1a28'))
PALS['cleric'] = _pal(dict(R='#b89840', r='#e8c870', O='#f8e8a0', L='#fff8d0', T='#a89cc0', t='#f4f0fa', M='#7a7098', c='#fff0a0', C='#f0c040', D='#a07820',
                           y='#f0c040', o='#c89020', Q='#b89868', q='#d8c088', j='#f4f0fa', U='#f0c040', u='#fff0a0', V='#a07820', X='#ffd070'))
SELS = {
    'warrior': SEL,
    'mage': {**SEL, **{k: '#3a2470' for k in 'RrOL'}, **{k: '#1c1450' for k in 'TtM'}, **{k: '#5a3a10' for k in 'cCD'}, **{k: '#1c1450' for k in 'UuVyoQqXj'}, **{k: '#601000' for k in 'ZzY'}},
    'rogue': {**SEL, **{k: '#0c0c18' for k in 'RrOLUuV'}, **{k: '#14141f' for k in 'TtM'}, **{k: '#4a0c14' for k in 'cCD'}, **{k: '#2a2a3a' for k in 'yoQqj'}},
    'cleric': {**SEL, **{k: '#6a5420' for k in 'RrOL'}, **{k: '#5a5078' for k in 'TtM'}, **{k: '#6a4a10' for k in 'cCDyoQqUuV'}},
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
def make_head_side(mouth='n', eyes='open', look='n'):
    o = -1 if look == 'up' else (1 if look == 'down' else 0)
    Wd, Hd = 21, 18
    bounds = [(4, 16), (2, 18), (1, 19), (1, 19), (0, 19), (0, 19), (0, 19), (0, 19), (0, 19), (0, 19), (0, 19), (0, 20), (0, 20), (1, 19), (1, 19), (2, 19), (4, 18), (6, 16)]
    hair_end = [99, 99, 99, 99, 99, 99, 99, 99, 13, 12, 12, 12, 12, 11, 10, 9, 7, -1]
    g = [['.'] * Wd for _ in range(Hd)]
    for r in range(Hd):
        l, rr = bounds[r]
        for c in range(l, rr + 1):
            g[r][c] = 'O' if c <= hair_end[r] else 's'
    # franja irregular sobre a testa (linha 8) e pontas
    for c, ch in zip(range(14, 20), 'OsOssO'): g[8 + o][c] = ch
    for c in range(14, 20): g[9 + o][c] = 's'
    if o == -1:
        for c in range(14, 20): g[8][c] = 's'
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
        for dc, ch in enumerate('kkk'): g[10 + o][14 + dc] = ch
        for dc, ch in enumerate('wwb'): g[11 + o][14 + dc] = ch
        for dc, ch in enumerate('wbb'): g[12 + o][14 + dc] = ch
        for dc, ch in enumerate('sbB'): g[13 + o][14 + dc] = ch
    else:
        for dc in range(3): g[11 + o][14 + dc] = 'k'
    g[14 + o][13] = 'S'; g[14 + o][14] = 'S'
    g[11 + o][20] = 'p'; g[12 + o][20] = 'S'
    if mouth == 'n':
        g[15 + o][16] = 'k'; g[15 + o][17] = 'k'
    else:
        for c in range(15, 19): g[15 + o][c] = 'k'
        g[16 + o][16] = 'k'; g[16 + o][17] = 'k'
    if o == -1:
        for c in range(13, 19): g[16][c] = 'S'
    for c in range(8, 14): g[17][c] = 'S'
    for c in range(14, 17): g[16][c] = 'S' if g[16][c] == 's' else g[16][c]
    return [''.join(r) for r in g]


HEAD_S = make_head_side()
HEAD_F_UP = HEAD_F[:9] + [HEAD_F[10], HEAD_F[11], HEAD_F[12], HEAD_F[13], HEAD_F[14], HEAD_F[15], '....ssssssS', '....SSSSSSS', '......SSSSS']
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
def sword_rows(hand, ang, length=10, guard=3, wide=False, serrate=False, glow=None, gem=False):
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
            for k in range(-guard, guard + 1): cells[(round(x + nx * k), round(y + ny * k))] = 'g'
        else:
            cells[(x, y)] = 'A'
            ox, oy = (1, 0) if abs(uy) >= abs(ux) else (0, 1)
            if i < len(pts) - 1 and not (serrate and i % 3 == 0): cells.setdefault((x + ox, y + oy), 'a')
            if wide: cells.setdefault((x - ox, y - oy), 'A')
            if glow and i > 4 and i % 3 == 0:
                cells[(x - ox * (2 if wide else 1) * (-1 if glow == 'ice' else 1), y - oy * (2 if wide else 1) * (-1 if glow == 'ice' else 1))] = 'Z' if glow != 'dark' else 'z'
    cells[(round(tip[0]), round(tip[1]))] = 'A'
    if gem:
        gx, gy = round(hand[0] + ux * 2.6), round(hand[1] + uy * 2.6)
        cells[(gx, gy)] = 'r'
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


def bow_rows(center, d, draw=0, arrow=True, span=11):
    """Arco SEPARADO + flecha (apontando para d=(dx,dy) unitario). Retorna cells, ponta da flecha, ponto onde a mao de puxar fica."""
    dx, dy = d
    px_, py_ = -dy, dx
    cells = {}
    n = 22
    prev = None
    top = None; bot = None
    for i in range(n + 1):
        t = -1 + 2 * i / n
        bulge = 4.0 * (1 - t * t)
        x = center[0] + px_ * t * span + dx * bulge
        y = center[1] + py_ * t * span + dy * bulge
        if prev is not None:
            for (xx, yy) in line_pts(round(prev[0]), round(prev[1]), round(x), round(y)): cells[(xx, yy)] = 'N'
        prev = (x, y)
        if i == 0: top = (x, y)
        if i == n: bot = (x, y)
    pull = (center[0] - dx * draw, center[1] - dy * draw)
    for p0 in (top, bot):
        for (xx, yy) in line_pts(round(p0[0]), round(p0[1]), round(pull[0]), round(pull[1])): cells.setdefault((xx, yy), 'a')
    cells[(round(top[0]), round(top[1]))] = 'g'; cells[(round(bot[0]), round(bot[1]))] = 'g'
    tip = (center[0] + dx * 11, center[1] + dy * 11)
    if arrow:
        for (xx, yy) in line_pts(round(pull[0]), round(pull[1]), round(tip[0]), round(tip[1])): cells[(xx, yy)] = 'q'
        cells[(round(tip[0]), round(tip[1]))] = 'A'
        cells[(round(tip[0] - dx), round(tip[1] - dy))] = 'A'
        for k in (0, 1, 2):
            fx, fy = round(pull[0] + dx * k), round(pull[1] + dy * k)
            cells[(fx + round(px_), fy + round(py_))] = 'r'; cells[(fx - round(px_), fy - round(py_))] = 'r'
    return cells, tip, pull


def mace_rows(hand, ang, length=15):
    """Maca SEPARADA: cabo de madeira e cabeca de ouro com espinhos."""
    a = math.radians(ang)
    ux, uy = math.sin(a), math.cos(a)
    tip = (hand[0] + ux * (length - 3), hand[1] + uy * (length - 3))
    cells = {}
    for (x, y) in line_pts(round(hand[0] - ux * 3), round(hand[1] - uy * 3), round(tip[0]), round(tip[1])): cells[(x, y)] = 'N'
    cx, cy = round(tip[0] + ux * 2), round(tip[1] + uy * 2)
    for dy in (-2, -1, 0, 1, 2):
        for dx in (-2, -1, 0, 1, 2):
            if abs(dx) + abs(dy) <= 3: cells[(cx + dx, cy + dy)] = 'g'
    cells[(cx - 1, cy - 1)] = 'G'; cells[(cx, cy - 1)] = 'G'; cells[(cx - 1, cy)] = 'G'
    cells[(cx + 1, cy + 1)] = 'N'; cells[(cx + 2, cy)] = 'A'; cells[(cx - 3, cy)] = 'A'; cells[(cx, cy - 3)] = 'A'; cells[(cx, cy + 3)] = 'A'
    return cells, (cx, cy)


def weapon_rows(swd, hxy, view, back=False, bow_center=None):
    """Roteador de armas. Retorna (cells, tip, behind, mitts2)."""
    kind = swd.get('kind', 'sword')
    if kind == 'staff':
        cells, tip = staff_rows(hxy, swd.get('ang', 180), swd.get('len', 24), swd.get('orb', 1))
        return cells, tip, False, []
    if kind == 'bow':
        c = bow_center or hxy
        cells, tip, pull = bow_rows(c, swd['dir'], swd.get('draw', 0), swd.get('arrow', True), swd.get('span', 11))
        return cells, tip, (back and swd['dir'][1] < 0), [pull]
    if kind == 'mace':
        cells, tip = mace_rows(hxy, swd['ang'], swd.get('len', 15))
        return cells, tip, (185 <= swd['ang'] <= 265), []
    cells, tip = sword_rows(hxy, swd['ang'], swd.get('len', 12), swd.get('guard', 1 if kind == 'dagger' else 3), swd.get('wide', False), swd.get('serrate', False), swd.get('glow'), swd.get('gem', False))
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


QUIVER_S = ['.r.r.', '.F.F.', '.q.q.', 'QQQQQ', 'QqqQQ', 'QqqQQ', 'QqqQQ', '.QQQ.']


def pre_accessory(g, cls, view, cx, body_top, dx=0, bdx=0, back=False):
    """Itens desenhados ANTES do corpo (ficam atras): aljava do arqueiro."""
    if cls != 'archer': return
    if view == 'side': g.stamp(QUIVER_S, cx - 11 + dx + bdx, body_top - 3)
    elif back: g.stamp(QUIVER_S, cx - 10 + dx, body_top - 3)
    else: g.stamp(['r.r', 'F.F'], cx - 10 + dx, body_top - 3)


def post_accessory(g, cls, view, cx, body_top, dx=0, back=False):
    """Itens por cima do corpo: tira da aljava."""
    if cls != 'archer' or view == 'side': return
    for i in range(9):
        x = cx - 5 + dx + i; y = body_top + 1 + i // 2
        g.put(x, y, 'o')


def hood_head(rows, view):
    """Capuz do ladino: cobre topo e laterais do cabelo."""
    mp = {'R': 'V', 'O': 'U', 'L': 'u', 'r': 'U'}
    out = []
    for i, r in enumerate(rows):
        if i <= 6: r = ''.join(mp.get(c, c) for c in r)
        elif view == 'front' and i <= 14: r = ''.join(mp.get(c, c) if k < 3 else c for k, c in enumerate(r))
        out.append(r)
    return out


def hood_head_side(rows):
    mp = {'R': 'V', 'O': 'U', 'L': 'u', 'r': 'U'}
    out = []
    for i, r in enumerate(rows):
        if i <= 15: r = ''.join(mp.get(c, c) for c in r)
        out.append(r)
    return out


def helm_head(rows, view):
    """Elmo de aco: recolore o topo + protetores de bochecha (frente)."""
    out = cap_head(rows, view)
    for i in range(7, 14):
        r = out[i]
        out[i] = ''.join({'R': 'V', 'O': 'U', 'r': 'U'}.get(c, c) if k < 2 else c for k, c in enumerate(r))
    for i in (7, 8, 9, 10):
        r = list(out[i])
        if len(r) > 10 and r[10] in 'sp': r[10] = 'u'          # protetor de nariz
        out[i] = ''.join(r)
    return out


def helm_head_side(rows):
    out = hood_head_side(rows)
    for i in (9, 10, 11):
        r = list(out[i])
        if len(r) > 17: r[17] = 'u'
        out[i] = ''.join(r)
    return out


def accessory2(g, hat, view, hx, hy, back=False):
    if hat == 'wizard':
        if view == 'side': g.stamp(hat_side(), hx - 1, hy - 4)
        else:
            g.stamp(HAT_F, hx, hy - 4, mirror=True, rshade=dict(u='U'))
            g.put(hx + 10, hy - 1, 'X'); g.put(hx + 11, hy - 1, 'X')
    elif hat == 'cap':
        g.stamp(['..F', '.Ff', 'Ff.', 'f..'], hx + 4, hy - 3) if view == 'side' else g.stamp(['..F', '.Ff', 'Ff.', 'f..'], hx + 17, hy - 3)
    elif hat == 'helm':
        if view == 'side': g.stamp(['..f.', '.ffF', 'fFF.', 'F...'], hx - 2, hy - 3)
        else: g.stamp(['.ff', 'ffF', 'fFF'], hx + 9, hy - 5, mirror=True)
    elif hat == 'circlet':
        if view == 'side':
            for x in range(hx + 9, hx + 19): g.put(x, hy + 6, 'X')
            g.put(hx + 18, hy + 5, 'G')
        else:
            for x in range(hx + 3, hx + 19): g.put(x, hy + 6, 'X')
            g.put(hx + 10, hy + 5, 'G'); g.put(hx + 11, hy + 5, 'G')
    elif hat == 'crown':
        y = hy - 2
        for i, x in enumerate(range(hx + 5, hx + 17)):
            g.put(x, y + (1 if i % 3 else 0), 'g'); g.put(x, y + 2, 'g')
        g.put(hx + 10, y - 1, 'G'); g.put(hx + 11, y - 1, 'G')
    elif hat == 'bandana':
        for x in range(hx + 1, hx + (20 if view == 'side' else 21)): g.put(x, hy + 6, 'r')


def accessory(g, cls, view, hx, hy, back=False):
    if cls == 'cleric':
        if view == 'side':
            for x in range(hx + 9, hx + 19): g.put(x, hy + 6, 'X')
            g.put(hx + 18, hy + 5, 'G')
        else:
            for x in range(hx + 3, hx + 19): g.put(x, hy + 6, 'X')
            g.put(hx + 10, hy + 5, 'G'); g.put(hx + 11, hy + 5, 'G')
    if cls == 'mage':
        if view == 'side': g.stamp(hat_side(), hx - 1, hy - 4)
        else: g.stamp(HAT_F, hx, hy - 4, mirror=True, rshade=dict(u='U'))
        g.put(hx + 10, hy - 1, 'X'); g.put(hx + 11, hy - 1, 'X')
    elif cls == 'archer':
        if view == 'side': g.stamp(['..F', '.Ff', 'Ff.', 'f..'], hx + 4, hy - 3)
        else: g.stamp(['..F', '.Ff', 'Ff.', 'f..'], hx + 17, hy - 3)


def arm_cells(p0, p1, thick=2):
    """Braco de manga (t/T) ligando ombro -> mao; a mao e desenhada por cima."""
    cells = {}
    for (x, y) in line_pts(round(p0[0]), round(p0[1]), round(p1[0]), round(p1[1])):
        cells[(x, y)] = 't'
        if thick > 1: cells.setdefault((x, y + 1), 'T')
    return cells


# ---------------------------------------------------------------- roupas (outfit): cota de malha / manto completo
def outfit_pass(g, outfit, view, cx, body_top, boot_top, dx=0, bdx=0, back=False, al=(0, 0), ar=(0, 0)):
    if outfit == 'mail':
        # textura de cota de malha (xadrez de 2 tons) + ombreiras + saiote de malha
        for y in range(body_top + 1, boot_top):
            for x in range(cx - 8 + dx, cx + 8 + dx):
                if g.get(x, y) in 'tT' and (x + y) % 2 == 0: g.put(x, y, 'M')
        if view == 'side':
            g.stamp(['.uuU.', 'uUUUV', '.UVVV'], cx - 4 + dx + bdx, body_top + 1)
            g.stamp(['UUUUUU', 'UuUuUV'], cx - 5 + dx + bdx, boot_top - 1)
        else:
            g.stamp(['.uuU', 'uUUUV', '.UVVV'], cx - 10 + dx, body_top + 1)
            g.stamp(['Uuu.', 'VUUUu', 'VVVU.'], cx + 6 + dx, body_top + 1)
            g.stamp(['UuUuUV'], cx - 6 + dx, boot_top - 1, mirror=True)
    elif outfit == 'robe':
        # manto completo: cobre as botas, mangas largas, listra dourada
        if view == 'side':
            g.stamp(['.tttttttTT.', 'ttttttttTTT', 'tttttttttTT', 'CTCTCTCTCTC'], cx - 6 + dx + bdx, boot_top - 2)
            g.stamp(['QQ..QQ'], cx - 4 + dx + bdx, boot_top + 2)
            g.stamp(['.ttt', 'ttTT', 'tTT.'], cx + 0 + dx + bdx, body_top + 3)
        else:
            g.stamp(['.ttttTT', 'tttttTT', 'ttttttT', 'tttttTT', 'CTCTCTC'], cx - 8 + dx, boot_top - 2, mirror=True, rshade=dict(t='T'))
            g.stamp(['QQ.QQ'], cx - 5 + dx, boot_top + 3, mirror=False)
            g.stamp(['.tt', 'ttT', 'tTT'], cx - 10 + dx + al[0], body_top + 1 + al[1])
            g.stamp(['tt.', 'Ttt', 'TTt'], cx + 8 + dx + ar[0], body_top + 1 + ar[1])
            for y in range(body_top + 2, boot_top + 2): g.put(cx - 1 + dx, y, 'C'); g.put(cx + dx, y, 'C')


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
    hat = p.get('hat', DEFAULT_HAT[cls]); outfit = p.get('outfit', DEFAULT_OUTFIT[cls])
    swd = p.get('sw'); tip = None; hxy = None; behind = False; hands2 = []
    if swd:
        side = swd.get('side', 'r')
        al_, ar_ = p.get('al', (0, 0)), p.get('ar', (0, 0))
        hxy = (cx + (7 if side == 'r' else -7) + dx + (ar_ if side == 'r' else al_)[0] + 1, my0 + 1 + (ar_ if side == 'r' else al_)[1])
        if side != 'r': hxy = (hxy[0] - 1, hxy[1])
        cells, tip, behind, hands2 = weapon_rows(swd, hxy, 'front', back, (cx + dx + 1, my0 + 3))
        if behind: stamp_cells(g, cells)
    pre_accessory(g, cls, 'front', cx, body_top, dx, 0, back)
    # botas
    g.stamp(BOOT_F, cx - 5 + dx + bl[0], boot_top - bl[1])
    g.stamp(BOOT_F, cx + 2 + dx + br[0], boot_top - br[1])
    # corpo (metade espelhada)
    rows = (BODY_B_TOP if back else BODY_F_TOP) + [BODY_F_MID] * max(0, tn - 2) + [BODY_F_FOLD if tn >= 3 else BODY_F_MID, BODY_F_BELT, BODY_F_HEM]
    rows = rows[:body_h]
    g.stamp(rows, cx - 6 + dx, body_top, mirror=True, rshade=dict(t='T', c='C', y='o'))
    outfit_pass(g, outfit, 'front', cx, body_top, boot_top, dx, 0, back, p.get('al', (0, 0)), p.get('ar', (0, 0)))
    # maos (blocos de pele)
    al, ar = p.get('al', (0, 0)), p.get('ar', (0, 0))
    my = body_top + 2
    bow = bool(swd and swd.get('kind') == 'bow')
    if not p.get('nomitt'):
        if not (bow and hands2): g.stamp(MITT_L, cx - 9 + dx + al[0], my + al[1])
        if not bow: g.stamp([r[::-1] for r in MITT_L], cx + 6 + dx + ar[0], my + ar[1])
    # cabeca
    hx, hy = cx - 11 + dx + p.get('hdx', 0), body_top - 17 + p.get('hdy', 0)
    head = list(HEAD_B if back else (HEAD_F_UP if p.get('look') == 'up' else HEAD_F))
    hat = p.get('hat', DEFAULT_HAT[cls]); outfit = p.get('outfit', DEFAULT_OUTFIT[cls])
    if hat == 'cap': head = cap_head(head, 'front')
    elif hat == 'hood': head = hood_head(head, 'front')
    elif hat == 'helm': head = helm_head(head, 'front')
    if p.get('face') == 'shout' and not back:
        head[15] = '...sskkksssk'
    if p.get('face') == 'blink' and not back:
        head[10] = 'RrOsskkkssp'; head[11] = 'RrOssssssss'; head[12] = 'ROOssssssss'; head[13] = '.rOssssssss'
    g.stamp(head, hx, hy, mirror=True, rshade=RSH_F)
    accessory2(g, hat, 'front', hx, hy, back)
    post_accessory(g, cls, 'front', cx, body_top, dx, back)
    for hp in hands2:
        for (ox, oy) in ((0, 0), (1, 0), (0, 1), (1, 1)): g.put(round(hp[0]) + ox, round(hp[1]) + oy, 's')
    if bow:
        bc = (cx + dx + 1, my0 + 3)
        Sr, Sl = (cx + 5 + dx, my0 - 1), (cx - 4 + dx, my0 - 1)
        for (x, y), ch in {**arm_cells(Sr, bc), **(arm_cells(Sl, hands2[0]) if hands2 else {})}.items(): g.put(x, y, ch)
        for (ox, oy) in ((0, 0), (1, 0), (0, 1), (1, 1)): g.put(round(bc[0]) + ox - 1, round(bc[1]) + oy - 1, 's')
    autoline(g)
    sw2 = p.get('sw2')
    if sw2:
        h2 = (cx - 7 + dx + al[0], my + 1 + al[1])
        c2, t2 = sword_rows(h2, sw2['ang'], sw2.get('len', 8), 1)
        stamp_cells(g, c2)
        for (ox, oy) in ((0, 0), (1, 0), (0, 1), (1, 1)): g.put(round(h2[0]) - 1 + ox, round(h2[1]) - 1 + oy, 's' if oy == 0 else 'S')
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
    hat = p.get('hat', DEFAULT_HAT[cls]); outfit = p.get('outfit', DEFAULT_OUTFIT[cls])
    swd = p.get('sw'); tip = None; behind = False; hands2 = []
    bow_arms = None
    if swd:
        hxy = (cx + 4 + dx + af_[0] + 1, body_top + 4 + af_[1])
        bc = (hxy[0] + 2, hxy[1])
        if swd.get('kind') == 'bow':
            bend_ = p.get('bend', 0)
            S = (cx + 1 + dx + p.get('bdx', 0) - bend_ * .9, body_top + 1.5)       # ombro
            d_ = swd['dir']
            bc = (S[0] + d_[0] * 10, S[1] + d_[1] * 10)                               # mao do arco: braco ESTICADO na linha da mira
            bow_arms = S
        cells, tip, behind, hands2 = weapon_rows(swd, hxy, 'side', False, bc)
        if behind: stamp_cells(g, cells)
    pre_accessory(g, cls, 'side', cx, body_top, dx, p.get('bdx', 0))
    g.stamp(BOOT_S, cx - 6 + dx + bk[0], boot_top - bk[1])
    g.stamp(BOOT_S, cx - 1 + dx + bf[0], boot_top - bf[1])
    rows = [BODY_S['sc'], BODY_S['t0']] + [BODY_S['t1']] * max(0, tn - 2) + [BODY_S['t2'], BODY_S['belt'], BODY_S['hem']]
    rows = rows[:body_h]
    bend = p.get('bend', 0)
    for ri, row in enumerate(rows):
        off = -int(round(bend * (len(rows) - 1 - ri) / max(1, len(rows) - 1)))
        g.stamp([row], cx - 5 + dx + p.get('bdx', 0) + off, body_top + ri)
    outfit_pass(g, outfit, 'side', cx, body_top, boot_top, dx, p.get('bdx', 0))
    fl = p.get('flut', 0)
    g.stamp(['CC.', '.CD', '..D'], cx - 8 + dx + p.get('bdx', 0) - fl, body_top + fl // 2)
    # braco de tras (so um bloco atras) e da frente
    ab, af = p.get('al', (0, 0)), p.get('ar', (0, 0))
    if not p.get('nomitt') and not bow_arms: g.stamp(['ss', 'sS'], cx - 6 + dx + ab[0], body_top + 3 + ab[1])
    # cabeca (perfil)
    hx, hy = cx - 11 + dx + p.get('hdx', 0), body_top - 17 + p.get('hdy', 0)
    head = make_head_side('shout' if p.get('face') == 'shout' else 'n', 'closed' if p.get('face') == 'blink' else 'open', p.get('look', 'n'))
    hat = p.get('hat', DEFAULT_HAT[cls]); outfit = p.get('outfit', DEFAULT_OUTFIT[cls])
    if hat == 'cap': head = cap_head_side(head)
    elif hat == 'hood': head = hood_head_side(head)
    elif hat == 'helm': head = helm_head_side(head)
    g.stamp(head, hx, hy)
    accessory2(g, hat, 'side', hx, hy)
    if not p.get('nomitt') and not bow_arms: g.stamp(['ss', 'sS'], cx + 3 + dx + af[0], body_top + 3 + af[1])
    if bow_arms:
        for (x, y), ch in {**arm_cells(bow_arms, bc), **(arm_cells((bow_arms[0] - 1, bow_arms[1] + 1), hands2[0]) if hands2 else {})}.items(): g.put(x, y, ch)
        for (mx, my_) in [bc] + list(hands2):
            for (ox, oy) in ((0, 0), (1, 0), (0, 1), (1, 1)): g.put(round(mx) - 1 + ox, round(my_) - 1 + oy, 's' if oy == 0 else 'S')
    autoline(g)
    sw2 = p.get('sw2')
    if sw2:
        h2 = (cx - 4 + dx + ab[0], body_top + 4 + ab[1])
        c2, t2 = sword_rows(h2, sw2['ang'], sw2.get('len', 8), 1)
        stamp_cells(g, c2)
        for (ox, oy) in ((0, 0), (1, 0), (0, 1), (1, 1)): g.put(round(h2[0]) - 1 + ox, round(h2[1]) - 1 + oy, 's' if oy == 0 else 'S')
    if swd:
        if not behind: stamp_cells(g, cells)
        bowd = swd.get('kind') == 'bow'
        mc = bc if bowd else hxy
        g.put(round(mc[0]) - 1, round(mc[1]) - 1, 's'); g.put(round(mc[0]), round(mc[1]) - 1, 's')
        g.put(round(mc[0]) - 1, round(mc[1]), 'S'); g.put(round(mc[0]), round(mc[1]), 'S')
        for hp in hands2:
            g.put(round(hp[0]) - 1, round(hp[1]) - 1, 's'); g.put(round(hp[0]), round(hp[1]) - 1, 's')
            g.put(round(hp[0]) - 1, round(hp[1]), 'S'); g.put(round(hp[0]), round(hp[1]), 'S')
    return g, tip, behind


def render(g, cls='warrior', over=None):
    pal = dict(PALS[cls])
    if over: pal.update(over)
    return g.render(pal, sel_for(cls, pal, over or {}))

# ================================================================ APARENCIA E EQUIPAMENTOS (tudo e DADO: troca em tempo de execucao)
def darken(h, k=.5):
    h = h.lstrip('#'); r, g_, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return '#%02x%02x%02x' % (int(r * k), int(g_ * k), int(b * k))


SKINS = {'clara': dict(s='#f2c99a', S='#e08c68', p='#f8e0bc'), 'bronze': dict(s='#d9a070', S='#b87850', p='#ecc298'),
         'escura': dict(s='#a8704a', S='#80502e', p='#c8906a'), 'palida': dict(s='#f8e4da', S='#e0a8a0', p='#fff4ee'),
         'esverdeada': dict(s='#b8d890', S='#88b068', p='#d8f0b8')}
HAIRS = {'ruivo': dict(R='#9a3030', r='#e84820', O='#f08018', L='#f8b060'), 'preto': dict(R='#10101c', r='#38384c', O='#242436', L='#585878'),
         'castanho': dict(R='#4a2c14', r='#a8602c', O='#7a4a24', L='#b88050'), 'loiro': dict(R='#b89840', r='#e8c870', O='#f8e8a0', L='#fff8d0'),
         'branco': dict(R='#8a90a8', r='#c8d0e0', O='#e8ecf4', L='#ffffff'), 'azul': dict(R='#1c3a8a', r='#3a78e0', O='#4a98f0', L='#a0d0ff'),
         'rosa': dict(R='#a02860', r='#e8509a', O='#f878b8', L='#ffb8dc'), 'verde': dict(R='#1c5a30', r='#3aa850', O='#58c868', L='#a8f0a8')}
EYES = {'azul': dict(b='#2e86c8', B='#1c4a98'), 'verde': dict(b='#38b058', B='#1c6a30'), 'castanho': dict(b='#9a6a38', B='#5a3418'),
        'violeta': dict(b='#9a58e0', B='#5a2aa0'), 'vermelho': dict(b='#e84a4a', B='#901c24'), 'dourado': dict(b='#f0c040', B='#a07820')}
CLOTHES = {'vermelho': dict(T='#8a2c38', t='#b83c44', M='#5a2836'), 'azul': dict(T='#244a9a', t='#3a78d8', M='#162c60'), 'verde': dict(T='#1c5a30', t='#3a9a48', M='#103a1c'),
           'roxo': dict(T='#3a2a7a', t='#5e46b8', M='#241a58'), 'preto': dict(T='#1c1c2a', t='#383850', M='#0c0c18'), 'branco': dict(T='#a89cc0', t='#f4f0fa', M='#7a7098'),
           'dourado': dict(T='#a07828', t='#e8b840', M='#6a4a14'), 'aco': dict(T='#4a5468', t='#9aa8c0', M='#2e3648'), 'bronze': dict(T='#6a3c20', t='#b87840', M='#40220e'),
           'laranja': dict(T='#a84a14', t='#e87a24', M='#6a2c0c')}
ACCENTS = {'azul': dict(c='#7cc0f0', C='#3a86d0', D='#1c4a98'), 'vermelho': dict(c='#ff7a6a', C='#d03a3a', D='#8a1c24'), 'dourado': dict(c='#fff0a0', C='#f0c040', D='#a07820'),
           'verde': dict(c='#a8f0a0', C='#48b858', D='#1c6a30'), 'preto': dict(c='#585870', C='#34344a', D='#1a1a28'), 'branco': dict(c='#ffffff', C='#d8d8ec', D='#9898b8')}
METAL = {'aco': dict(U='#9aa8c0', u='#d8e4f4', V='#4a5468', Q='#5a6478', q='#9aa8c0', j='#d8e4f4'),
         'ouro': dict(U='#e8b840', u='#fff0a0', V='#a07828', Q='#a07828', q='#e8b840', j='#fff0a0'),
         'ferro': dict(U='#6a6e7c', u='#9a9eac', V='#3a3c48', Q='#3a3c48', q='#6a6e7c', j='#9a9eac')}

# armas: params (forma) + pal (cores). Troca de arma = trocar o id.
WEAPONS = {
    # espadas
    'espada_ferro': dict(kind='sword', len=11, guard=2, pal=dict(A='#c0c8d0', a='#7c8898', g='#8a6a3a', N='#4a3020')),
    'espada_aco': dict(kind='sword', len=13, guard=3, pal=dict(A='#f6faff', a='#9cb0d2', g='#e8b840', N='#6e4228')),
    'espada_longa': dict(kind='sword', len=16, guard=3, pal=dict(A='#eef4ff', a='#8aa0c8', g='#c8a040', N='#4a3020')),
    'montante': dict(kind='sword', len=17, guard=4, wide=True, pal=dict(A='#e0e8f0', a='#8890a8', g='#a0a0b0', N='#3a2a20')),
    'espada_dourada': dict(kind='sword', len=14, guard=4, gem=True, pal=dict(A='#fff4a8', a='#e8b840', g='#f4cc58', N='#7a4a20')),
    'espada_chamas': dict(kind='sword', len=14, guard=3, glow='fire', pal=dict(A='#ffe070', a='#ff7a20', g='#8a2a10', N='#3a1a10', Z='#fff0a0', z='#ff6a20')),
    'espada_gelo': dict(kind='sword', len=14, guard=3, glow='ice', pal=dict(A='#e8fcff', a='#58c8f0', g='#3a78c8', N='#244a7a', Z='#ffffff')),
    'espada_sombria': dict(kind='sword', len=14, guard=3, glow='dark', serrate=True, pal=dict(A='#b080ff', a='#3a2070', g='#1a1030', N='#0c0818', z='#d8b0ff')),
    'serra_cruel': dict(kind='sword', len=12, guard=2, serrate=True, wide=True, pal=dict(A='#d8d0c0', a='#7a6a58', g='#5a3a20', N='#2a1a10')),
    # cajados
    'cajado_fogo': dict(kind='staff', len=24, orb=1, pal=dict(Z='#fff4b0', z='#ff9a30', Y='#c83010', N='#6e4228', g='#e8b840')),
    'cajado_gelo': dict(kind='staff', len=24, orb=1, pal=dict(Z='#ffffff', z='#58c8f0', Y='#2a68c0', N='#4a5a78', g='#c8d8f0')),
    'cajado_arcano': dict(kind='staff', len=26, orb=2, pal=dict(Z='#ffe0ff', z='#c060f0', Y='#6a2aa0', N='#3a2050', g='#a070d0')),
    'cajado_natureza': dict(kind='staff', len=24, orb=1, pal=dict(Z='#e8ffd0', z='#58c858', Y='#2a7a30', N='#5a3a20', g='#78a848')),
    'cajado_caveira': dict(kind='staff', len=24, orb=1, pal=dict(Z='#fff8e0', z='#a8e060', Y='#4a7a20', N='#2a2018', g='#d8d0b8')),
    # arcos
    'arco_curto': dict(kind='bow', span=10, pal=dict(N='#8a5a30', a='#e8e0c8', g='#c8a060')),
    'arco_longo': dict(kind='bow', span=13, pal=dict(N='#6e4228', a='#e8e0c8', g='#8a6a3a')),
    'arco_elfico': dict(kind='bow', span=12, pal=dict(N='#d8b850', a='#f0fff0', g='#48b858')),
    'arco_osso': dict(kind='bow', span=11, pal=dict(N='#e8e0d0', a='#b0a898', g='#8a8070')),
    # adagas e macas
    'adaga_ferro': dict(kind='dagger', len=8, guard=1, pal=dict(A='#d8e0e8', a='#7c8898', g='#8a6a3a', N='#3a2418')),
    'adaga_veneno': dict(kind='dagger', len=8, guard=1, glow='ice', pal=dict(A='#c8f0a0', a='#48b848', g='#2a6a30', N='#1a2a18', Z='#e8ffb0')),
    'adaga_sangue': dict(kind='dagger', len=9, guard=1, serrate=True, pal=dict(A='#ffb0a8', a='#c02a30', g='#4a1018', N='#2a0c10')),
    'maca_ferro': dict(kind='mace', len=15, pal=dict(g='#9aa0b0', G='#d8e0f0', N='#4a3020', A='#c8d0e0')),
    'maca_dourada': dict(kind='mace', len=15, pal=dict(g='#e8b840', G='#fff0a0', N='#6e4228', A='#fff4c8')),
    'martelo_sagrado': dict(kind='mace', len=16, pal=dict(g='#f8f0e0', G='#ffffff', N='#a07828', A='#fff0a0')),
}


def make_palette(app):
    """Aparencia (dados) -> overrides de paleta."""
    over = {}
    if 'skin' in app: over.update(SKINS[app['skin']])
    if 'hair' in app: over.update(HAIRS[app['hair']])
    if 'eyes' in app: over.update(EYES[app['eyes']])
    if 'clothes' in app: over.update(CLOTHES[app['clothes']])
    if 'accent' in app: over.update(ACCENTS[app['accent']])
    if 'metal' in app: over.update(METAL[app['metal']])
    for k in ('boots',):
        pass
    if 'weapon' in app: over.update(WEAPONS[app['weapon']].get('pal', {}))
    if 'weapon2' in app: over.update(WEAPONS[app['weapon2']].get('pal', {}))
    return over


def apply_appearance(p, app):
    """Aplica chapeu, roupa e arma da aparencia aos parametros de pose."""
    q = dict(p)
    if 'hat' in app: q['hat'] = app['hat']
    if 'outfit' in app: q['outfit'] = app['outfit']
    wid = app.get('weapon')
    if wid and q.get('sw'):
        w = WEAPONS[wid]
        keep = {k: v for k, v in q['sw'].items() if k in ('ang', 'dir', 'draw', 'arrow', 'orb', 'side')}
        base = {k: v for k, v in w.items() if k != 'pal'}
        if w['kind'] == 'sword' and q['sw'].get('kind') in ('dagger', 'mace', 'staff', 'bow'): base = {}
        q['sw'] = {**q['sw'], **base, **keep} if base else q['sw']
        if 'len' in keep and 'len' in base: pass
    w2 = app.get('weapon2')
    if w2 and q.get('sw2'):
        w = WEAPONS[w2]; q['sw2'] = {**q['sw2'], **{k: v for k, v in w.items() if k not in ('pal', 'kind', 'ang')}}
    return q


GROUPS = {'RrOL': 'R', 'TtM': 'M', 'cCD': 'D', 'sSp': 'S'}


def sel_for(cls, pal, over):
    sel = dict(SELS[cls])
    for chars, dark in GROUPS.items():
        if any(c in over for c in chars):
            col = darken(pal[dark], .5 if dark != 'S' else .55)
            for c in chars: sel[c] = col
    if any(c in over for c in 'UuV'): sel.update({c: darken(pal['V'], .55) for c in 'UuV'})
    if any(c in over for c in 'QqjyoUuV') and 'Q' in over: sel.update({c: darken(pal['Q'], .55) for c in 'Qqj'})
    return sel



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


def anim(view, kind, cls='warrior', ps_override=None, appearance=None):
    out = []
    over = None
    if appearance:
        cls = appearance.get('cls', cls); over = make_palette(appearance)
    if kind == 'walk': ps = [walk_params(f, 8, view) for f in range(8)]
    elif kind == 'idle': ps = [idle_params(f, 6, view) for f in range(6)]
    else: ps = ATK_S if view == 'right' else (ATK_B if view == 'up' else ATK_F)
    if ps_override is not None: ps = ps_override
    for p in ps:
        p = dict(p, cls=cls)
        if appearance: p = apply_appearance(p, appearance)
        if view == 'right': g, tip, bh = build_side(p)
        else: g, tip, bh = build_front(p, back=(view == 'up'))
        out.append((render(g, cls, over), tip, bh))
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
