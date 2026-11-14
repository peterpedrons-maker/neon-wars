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


DEFAULT_HAT = {'rei': 'kinghelm', 'warrior': 'none', 'mage': 'wizard', 'archer': 'cap', 'rogue': 'hood', 'cleric': 'circlet'}
DEFAULT_OUTFIT = {'rei': 'mail', 'warrior': 'cloth', 'mage': 'robe', 'archer': 'cloth', 'rogue': 'cloth', 'cleric': 'robe'}


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

PALS['rei'] = _pal(dict(s='#e2daee', S='#8a7aa8', p='#f6f2fb', m='#6a5a88',
                        R='#0e0a1a', r='#2e2648', O='#1c1630', L='#4e4478',
                        w='#1a0c2c', b='#c878ff', B='#7a30c0', k='#0c0618',
                        T='#1e1a34', t='#3c3458', M='#0c0a16',
                        c='#ecc0ff', C='#b060f0', D='#6a2aa8',
                        U='#3c3460', u='#7468a8', V='#1c1830',
                        y='#7a6eb0', o='#2e2650', Q='#3e3668', q='#6a5ea0', j='#6a2aa8', X='#d4a444',
                        A='#d8f4ff', a='#6ab0e4', g='#2a2c44', N='#1c1830', G='#ecc0ff',
                        e='#161024', E='#2a1e44', H='#43306a', P='#b060f0', W='#ecc0ff', I='#4a4272', i='#8a7eb8', J='#1c1830', v='#d878ff', Z='#ecc0ff', z='#b060f0', Y='#6a2aa8'))
SELS = {
    'warrior': SEL,
    'mage': {**SEL, **{k: '#3a2470' for k in 'RrOL'}, **{k: '#1c1450' for k in 'TtM'}, **{k: '#5a3a10' for k in 'cCD'}, **{k: '#1c1450' for k in 'UuVyoQqXj'}, **{k: '#601000' for k in 'ZzY'}},
    'rogue': {**SEL, **{k: '#0c0c18' for k in 'RrOLUuV'}, **{k: '#14141f' for k in 'TtM'}, **{k: '#4a0c14' for k in 'cCD'}, **{k: '#2a2a3a' for k in 'yoQqj'}},
    'cleric': {**SEL, **{k: '#6a5420' for k in 'RrOL'}, **{k: '#5a5078' for k in 'TtM'}, **{k: '#6a4a10' for k in 'cCDyoQqUuV'}},
    'rei': {**SEL, **{k: '#08040e' for k in 'RrOLTtMUuVyoQqeEHIiJ'}, **{k: '#3e3458' for k in 'sSpm'}, **{k: '#2a0a50' for k in 'cCDjPWvZzY'}, **{k: '#3a2808' for k in 'X'}, **{k: '#1c4a78' for k in 'AaG'}},
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
    _eyes_v = eyes; eyes = 'open' if eyes in ('open', 'angry', 'sad', 'happy', 'hurt', 'dead') else eyes
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
    if _eyes_v in ('happy', 'hurt', 'dead', 'angry', 'sad'):
        for rr_ in range(10 + o, 14 + o):
            for c in range(14, 17): g[rr_][c] = 's'
        K = lambda r_, c_: g[r_ + o].__setitem__(c_, 'k')
        if _eyes_v == 'happy': K(10, 15); K(11, 14); K(11, 16)
        elif _eyes_v == 'hurt': K(10, 14); K(11, 15); K(12, 14); K(11, 16)
        elif _eyes_v == 'dead': K(10, 14); K(10, 16); K(11, 15); K(12, 14); K(12, 16)
        else:                                                    # angry / sad: olho aberto + sobrancelha
            for dc, ch in enumerate('kkk'): g[10 + o][14 + dc] = ch
            for dc, ch in enumerate('wwb'): g[11 + o][14 + dc] = ch
            for dc, ch in enumerate('wbb'): g[12 + o][14 + dc] = ch
            for dc, ch in enumerate('sbB'): g[13 + o][14 + dc] = ch
            if _eyes_v == 'angry': g[9 + o][14] = 'k'; g[9 + o][15] = 'k'; g[10 + o][13] = 'k'
            else: g[9 + o][15] = 'k'; g[9 + o][16] = 'k'; g[10 + o][17] = 'k'; g[14 + o][14] = 'b'
    if mouth == 'smile':
        for c in (16, 17, 18, 19): g[15 + o][c] = 's'
        for c in (16, 17, 18): g[15 + o][c] = 'k'
        g[14 + o][19] = 'k'; g[14 + o][15] = 'k'
    elif mouth == 'frown':
        for c in (16, 17, 18, 19): g[15 + o][c] = 's'
        for c in (17, 18): g[14 + o][c] = 'k'
        g[15 + o][16] = 'k'; g[15 + o][19] = 'k'
    elif mouth == 'o':
        for c in (16, 17, 18, 19): g[15 + o][c] = 's'
        for c in (17, 18):
            g[14 + o][c] = 'k'; g[15 + o][c] = 'k'; g[16 + o][c] = 'k'
    return [''.join(r) for r in g]


FACES = {'n': ('n', 'open'), 'shout': ('shout', 'open'), 'blink': ('n', 'closed'), 'happy': ('smile', 'happy'), 'angry': ('frown', 'angry'),
         'hurt': ('shout', 'hurt'), 'surprised': ('o', 'open'), 'sad': ('frown', 'sad'), 'dead': ('n', 'dead'), 'smirk': ('smile', 'open')}


def face_front(head, face):
    """expressoes de frente (metade esquerda 11 col, espelhada): olhos nas colunas 5-7 linhas 10-13, boca linha 15"""
    h = [list(r) for r in head]
    def K(r, c, ch='k'):
        if 0 <= r < len(h) and 0 <= c < len(h[r]): h[r][c] = ch
    def clear_eye():
        for r in range(10, 14):
            for c in range(5, 8): h[r][c] = 's'
    if face == 'shout': h[15] = list('...sskkksssk')
    elif face == 'blink': h[10] = list('RrOsskkkssp'); h[11] = list('RrOssssssss'); h[12] = list('ROOssssssss'); h[13] = list('.rOssssssss')
    elif face == 'happy':
        clear_eye(); K(10, 6); K(11, 5); K(11, 7)
        for c in (8, 9, 10): K(15, c)
        K(14, 7)
    elif face == 'smirk':
        for c in (9, 10): K(15, c)
        K(14, 8)
    elif face == 'angry':
        K(9, 4); K(9, 5); K(9, 6); K(10, 7, 'k')
        for c in (9, 10): K(15, c)
        K(16, 8)
    elif face == 'hurt':
        clear_eye(); K(10, 5); K(11, 6); K(12, 5); K(11, 7)
        h[15] = list('...sskkksssk'); K(16, 9); K(16, 10)
    elif face == 'surprised':
        K(9, 5); K(9, 6); K(8, 6, 's')
        K(15, 9); K(15, 10); K(16, 9); K(16, 10); K(14, 9); K(14, 10)
    elif face == 'sad':
        K(9, 6); K(9, 7); K(10, 4, 'k'); K(14, 5, 'b')
        for c in (9, 10): K(15, c)
        K(16, 8)
    elif face == 'dead':
        clear_eye(); K(10, 5); K(10, 7); K(11, 6); K(12, 5); K(12, 7)
        for c in (9, 10): K(15, c)
    return [''.join(r) for r in h]


HEAD_S = make_head_side()


def _strands(rows, pts, ch='r', only='O'):
    g = [list(r) for r in rows]
    for (x, y) in pts:
        if 0 <= y < len(g) and 0 <= x < len(g[y]) and g[y][x] in only: g[y][x] = ch
    return [''.join(r) for r in g]


def _no_speckle(rows, top, bot):
    out = []
    for i, r in enumerate(rows):
        if top <= i <= bot: r = r[0] + r[1:].replace('r', 'O') if False else ''.join('O' if (c == 'r' and 3 <= k) else c for k, c in enumerate(r))
        out.append(r)
    return out


# frente: mechas saindo da coroa para baixo/fora
HEAD_F = _strands(_no_speckle(HEAD_F, 1, 7), [(8, 2), (7, 3), (6, 4), (5, 5), (4, 6), (5, 2), (4, 3), (3, 4)])
HEAD_B = _strands(_no_speckle(HEAD_B, 1, 12), [(8, 3), (7, 4), (6, 5), (5, 6), (3, 9), (3, 10), (9, 8), (9, 9)])
HEAD_F_UP = HEAD_F[:9] + [HEAD_F[10], HEAD_F[11], HEAD_F[12], HEAD_F[13], HEAD_F[14], HEAD_F[15], '....ssssssS', '....SSSSSSS', '......SSSSS']
HEAD_S = _strands(_no_speckle([r for r in HEAD_S], 1, 7) if False else HEAD_S,
                  [(8, 2), (7, 3), (6, 4), (5, 5), (4, 6), (3, 8), (2, 10), (12, 2), (11, 3), (10, 4), (9, 5), (8, 6), (7, 8), (6, 10), (5, 12), (4, 3), (3, 4), (3, 6)])
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
def sword_rows(hand, ang, length=10, guard=3, wide=False, serrate=False, glow=None, gem=False, shape=None, gstyle='bar'):
    return shaped_rows(hand, ang, length, guard, shape or ('wide' if wide else 'straight'), gstyle, glow, gem, serrate)
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


# perfis de lamina: (largura_meia(t), curvatura em celulas, estilo de guarda)
def _prof(shape):
    P = {
        'straight': (lambda t: 1.0, 0, 'bar'),
        'wide':    (lambda t: 1.3, 0, 'bar'),
        'broad':   (lambda t: 1.6 if t < .72 else 1.6 - (t - .72) * 5.2, 0, 'cross'),
        'leaf':    (lambda t: 0.4 + 1.6 * math.sin(math.pi * min(1, t * 1.1) ** .8), 0, 'bar'),
        'katana':  (lambda t: .5, 3.2, 'disc'),
        'scimitar': (lambda t: .5 + 1.5 * min(1, t / .6) if t < .8 else 2 - (t - .8) * 8, 3.5, 'bar'),
        'rapier':  (lambda t: 0.0, 0, 'cup'),
        'cleaver': (lambda t: 1.3, 0.8, 'none'),
        'flame':   (lambda t: 0.9 + .8 * math.sin(t * 17) * (1 - t * .6), 0, 'cross'),
        'great':   (lambda t: 2.1, 0, 'cross'),
        'axe':     (None, 0, 'none'),
    }
    return P[shape]


def shaped_rows(hand, ang, length, guard, shape, gstyle, glow, gem, serrate):
    """Armas com SILHUETA propria (nao so cor): lamina larga, curva, florete, facao, chamejante, montante, machado."""
    a = math.radians(ang); ux, uy = math.sin(a), math.cos(a); nx, ny = -uy, ux
    hw, curve, gs = _prof(shape)
    gs = gstyle if gstyle != 'bar' else gs
    cells = {}
    def put(x, y, ch, over=True):
        k = (round(x), round(y))
        if over or k not in cells: cells[k] = ch
    # cabo + pomo
    for yy in range(int(hand[1]) - 6, int(hand[1]) + 7):
        for xx in range(int(hand[0]) - 6, int(hand[0]) + 7):
            rx, ry = xx - hand[0], yy - hand[1]
            sd = rx * ux + ry * uy; td = rx * nx + ry * ny
            if -3.5 <= sd <= 2.1 and abs(td) <= .55: put(xx, yy, 'N')
            if -4.4 <= sd < -3.5 and abs(td) <= .55: put(xx, yy, 'g')
    gx, gy = hand[0] + ux * 2, hand[1] + uy * 2
    if shape == 'axe':
        L = length
        for d in range(-3, L): put(hand[0] + ux * d, hand[1] + uy * d, 'N')
        put(hand[0] - ux * 3.4, hand[1] - uy * 3.4, 'g')
        for j in range(0, 6):                         # cabeca do machado (crescente) de um lado do cabo
            sd = L - 7 + j
            reach = [2, 3, 4, 4, 3, 2][j]
            for k in range(1, reach + 1):
                put(hand[0] + ux * sd + nx * k, hand[1] + uy * sd + ny * k, 'a' if k == reach else 'A')
            put(hand[0] + ux * sd, hand[1] + uy * sd, 'g')
        tip = (hand[0] + ux * (L - 1), hand[1] + uy * (L - 1))
        for d in (-1, 0):
            put(hand[0] + ux * (L + d) - nx * 1, hand[1] + uy * (L + d) - ny * 1, 'g')
        return cells, tip
    # guarda (amostragem rigida, igual a lamina)
    for yy in range(int(hand[1]) - 8, int(hand[1]) + 9):
        for xx in range(int(hand[0]) - 8, int(hand[0]) + 9):
            rx, ry = xx - hand[0], yy - hand[1]
            sd = rx * ux + ry * uy; td = rx * nx + ry * ny
            a_ = abs(td); on = False
            if gs == 'bar': on = abs(sd - 2) <= .55 and a_ <= guard + .3
            elif gs == 'cross':
                gw = guard + 1
                on = (abs(sd - 2) <= .55 and a_ <= gw + .3) or (a_ >= gw - .6 and a_ <= gw + .3 and 1 <= sd <= 2.6 and False)
                if abs(sd - 1.2) <= .4 and gw - .8 <= a_ <= gw + .3: on = True
            elif gs == 'disc': on = abs(sd - 2) <= 1.0 and a_ <= 2.3 and not (abs(sd - 2) < .5 and a_ < .6 and False)
            elif gs == 'cup':
                on = (abs(sd + 1.6) <= .55 and a_ <= 3.2) or (2.4 <= a_ <= 3.3 and -1.8 <= sd <= 2.5) or (abs(sd - 2.3) <= .5 and a_ <= 3.3)
            if on: put(xx, yy, 'g')
    L = length; s0 = 3
    lastp = (hand[0] + ux * L, hand[1] + uy * L)
    # amostragem RIGIDA: cada pixel e testado no sistema local (s ao longo da lamina, t perpendicular):
    # a espessura nao varia com o angulo, entao a lamina fica solida em todos os quadros.
    R = int(L + 8)
    for yy in range(int(hand[1]) - R, int(hand[1]) + R + 1):
        for xx in range(int(hand[0]) - R, int(hand[0]) + R + 1):
            rx, ry = xx - hand[0], yy - hand[1]
            sd = rx * ux + ry * uy; td = rx * nx + ry * ny
            if sd < s0 - .5 or sd > L + .4: continue
            tt = (sd - s0) / max(1.0, L - s0)
            off = curve * tt * tt
            w = max(0.0, hw(tt))
            if shape in ('broad', 'great', 'flame', 'katana', 'leaf'):
                w *= min(1.0, (L - sd) / 1.6 + .4)        # ponta em losango curto
            elif shape in ('straight', 'wide'):
                w *= min(1.0, (L - sd) / 0.9 + .55)       # espada reta: largura cheia ate quase a ponta
            cover = w + .55
            if abs(td - off) > cover: continue
            edge = (td - off) > max(0.0, w - .35) and w >= .3
            if shape in ('rapier',): edge = (td - off) > 0.05
            put(xx, yy, 'a' if edge else 'A')
            if serrate and int(sd) % 2 == 0 and td - off < -(w + .2): put(xx, yy, 'a')
            if glow and sd > s0 + 2 and int(sd) % 3 == 0 and abs(abs(td - off) - (w + 1.2)) < .5:
                put(xx, yy, 'Z' if glow != 'dark' else 'z')
    last = lastp
    if gem: put(gx + ux * 1.5, gy + uy * 1.5, 'r')
    tip = last
    put(tip[0], tip[1], 'A')
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
    cells, tip = sword_rows(hxy, swd['ang'], swd.get('len', 12), swd.get('guard', 1 if kind == 'dagger' else 3), swd.get('wide', False), swd.get('serrate', False), swd.get('glow'), swd.get('gem', False), swd.get('shape'), swd.get('gstyle', 'bar'))
    behind = (back or (185 <= swd['ang'] <= 265)) if view == 'front' else (185 <= swd['ang'] <= 265)
    return cells, tip, behind, []


# ---------------------------------------------------------------- acessorios por classe
HAT_F = ['............U', '...........uU', '..........uUU', '.........uUUU', '........uUUUU', '.......uUUUUU', '......uUUUUUU', '.....uUUUUUUU', '....uUUUUUUUU', '...XXXXXXXXXX', '..uUUUUUUUUUU', 'uUUUUUUUUUUUU', 'VVVVVVVVVVVVV']


def hat_side():
    rows = []
    for k in range(11):
        w = min(21, 2 + 2 * k)
        start = 11 - w // 2 - int((10 - k) * 0.5)
        r = ['.'] * 25
        for i in range(w): r[start + i + 1] = 'u' if i == 0 else 'U'
        if k == 9:
            for i in range(w): r[start + i + 1] = 'X'
        rows.append(''.join(r))
    rows.append('.V' + 'U' * 21 + 'V.')
    rows.append('..' + 'V' * 21 + '..')
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
    """Itens desenhados ANTES do corpo (ficam atras): aljava do arqueiro; capa do Rei."""
    if cls == 'rei':
        if not back: rei_cape(g, view, cx, body_top, dx, bdx)
        return
    if cls != 'archer': return
    if view == 'side': g.stamp(QUIVER_S, cx - 11 + dx + bdx, body_top - 3)
    elif back: g.stamp(QUIVER_S, cx - 10 + dx, body_top - 3)
    else: g.stamp(['r.r', 'F.F'], cx - 10 + dx, body_top - 3)


def post_accessory(g, cls, view, cx, body_top, dx=0, back=False):
    """Itens por cima do corpo: tira da aljava; capa do Rei vista de costas."""
    if cls == 'rei':
        if back and view != 'side': rei_cape(g, view, cx, body_top, dx, 0, over=True)
        return
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
    """Elmo de aco: cupula + aba, protetor de bochecha/nariz (frente) e nuca; o cabelo aparece embaixo."""
    mp = {'R': 'V', 'O': 'U', 'L': 'u', 'r': 'U'}
    out = []
    back = view == 'back'
    for i, r in enumerate(rows):
        if back and i <= 9: r = ''.join(mp.get(c, c) for c in r)
        elif back and i == 10: r = ''.join('V' if c in 'ROLr' else c for c in r)
        elif not back and i <= 5: r = ''.join(mp.get(c, c) for c in r)
        elif not back and i == 6: r = ''.join('V' if c in 'ROLr' else c for c in r)
        elif not back and 7 <= i <= 12: r = ''.join({'R': 'V', 'O': 'U', 'r': 'U'}.get(c, c) if k < 2 else c for k, c in enumerate(r))
        out.append(r)
    if not back:
        for i in (7, 8, 9, 10):
            r = list(out[i])
            if len(r) > 10 and r[10] in 'sp': r[10] = 'u'                      # protetor de nariz
            out[i] = ''.join(r)
    # rebites e brilho da cupula
    g = [list(r) for r in out]
    for (x, y) in ((4, 3), (8, 3)): g[y][x] = 'u'
    g[1][5] = g[1][6] = g[2][4] = 'u'
    return [''.join(r) for r in g]


def helm_head_side(rows):
    """Elmo de lado: cupula cobre topo e costas ate a orelha; aba; protetor de bochecha; cabelo aparece na nuca."""
    mp = {'R': 'V', 'O': 'U', 'L': 'u', 'r': 'U'}
    g = [list(r) for r in rows]
    for y, r in enumerate(g):
        for x, c in enumerate(r):
            if c not in mp: continue
            if y <= 7 or (8 <= y <= 12 and x <= 12):
                g[y][x] = mp[c]
    # aba (faixa escura na linha 7) e rebites
    for x, c in enumerate(g[7]):
        if c in 'UuV': g[7][x] = 'V'
    for x in (4, 9, 14): g[4][x] = 'u'
    for x in (4, 5, 6, 7): g[1][x] = 'u'
    g[2][5] = 'u'
    # protetor de bochecha (placa na frente da orelha) e de nariz
    for y in (9, 10, 11, 12):
        for x in (11, 12): g[y][x] = 'U' if x == 11 else 'V'
    for y in (8, 9, 10):
        if g[y][17] in 'sp': g[y][17] = 'u'
    return [''.join(r) for r in g]


def accessory2(g, hat, view, hx, hy, back=False):
    if hat == 'wizard':
        if view == 'side': g.stamp(hat_side(), hx - 2, hy - 7)
        else:
            g.stamp(HAT_F, hx - 2, hy - 7, mirror=True, rshade=dict(u='U'))
    elif hat == 'cap':
        g.stamp(['..F', '.Ff', 'Ff.', 'f..'], hx + 4, hy - 3) if view == 'side' else g.stamp(['..F', '.Ff', 'Ff.', 'f..'], hx + 17, hy - 3)
    elif hat == 'kinghelm':
        if view == 'side':
            for off, h in ((4, 3), (9, 5), (14, 6), (18, 4)):
                for k in range(h):
                    g.put(hx + off, hy + 1 - k, 'v' if k == h - 1 else 'i'); g.put(hx + off + 1, hy + 1 - k, 'I')
            for x in range(hx + 3, hx + 20): g.put(x, hy + 2, 'i' if x % 3 else 'v')
        else:
            g.stamp(['..........v', '..........i', '......v...I', '......i..iI', '..v...I..II', '..i..iI.iII', 'iIiIiIIIIII'], hx, hy - 5, mirror=True, rshade=dict(i='I'))
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
        if view == 'side': g.stamp(hat_side(), hx - 2, hy - 7)
        else: g.stamp(HAT_F, hx - 2, hy - 7, mirror=True, rshade=dict(u='U'))
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
    if outfit == 'mail' and _REI:
        if view == 'side': g.stamp(['..i..', '.iuUV', 'iuUUV', 'uUUVV', '.UVV.'], cx - 5 + dx + bdx, body_top - 1)
        else:
            g.stamp(['..i.', '.iuU', 'iuUU', 'uUUV', '.UVV'], cx - 13 + dx, body_top - 1)
            g.stamp(['.i..', 'Uui.', 'UUui', 'VUUu', 'VVU.'], cx + 9 + dx, body_top - 1)
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


# ================================================================ HIERARQUIA DE CAMADAS (arco): o que aparece e o que fica escondido
def bow_vertical(center, toward, draw, arrow, span=7):
    """Arco visto de frente/costas: limbos VERTICAIS (arco de perfil para a camera). toward=+1 mira p/ camera, -1 para longe."""
    cells = {}; n = 14; prev = None; top = bot = None
    for i in range(n + 1):
        t = -1 + 2 * i / n
        x = center[0] + 2.2 * (1 - t * t); y = center[1] + t * span
        if prev is not None:
            for (xx, yy) in line_pts(round(prev[0]), round(prev[1]), round(x), round(y)): cells[(xx, yy)] = 'N'
        prev = (x, y)
        if i == 0: top = (x, y)
        if i == n: bot = (x, y)
    pull = (center[0] - 2, center[1] - toward * draw)
    for p0 in (top, bot):
        for (xx, yy) in line_pts(round(p0[0]), round(p0[1]), round(pull[0]), round(pull[1])): cells.setdefault((xx, yy), 'a')
    cells[(round(top[0]), round(top[1]))] = 'g'; cells[(round(bot[0]), round(bot[1]))] = 'g'
    tip = (center[0] - 1, center[1] + toward * 5)
    if arrow:
        for (xx, yy) in line_pts(round(pull[0]), round(pull[1]), round(tip[0]), round(tip[1])): cells[(xx, yy)] = 'q'
        cells[(round(tip[0]), round(tip[1]))] = 'A'; cells[(round(tip[0]), round(tip[1] + toward))] = 'A'
        cells[(round(pull[0]) + 1, round(pull[1]))] = 'r'; cells[(round(pull[0]) - 1, round(pull[1]))] = 'r'
    return cells, tip, pull


def bow_front_geom(swd, back, cx, dx, my0, body_top):
    """Frente/costas. 'carry' = arco horizontal na frente da barriga com as DUAS maos (de costas fica escondido, so as pontas aparecem).
    'aim' = braco do arco para a camera/para longe, mao da corda no rosto; de costas o arco fica ATRAS do corpo (so a ponta
    do arco e da flecha aparecem acima da cabeca e o cotovelo da corda sai de lado)."""
    mode = swd.get('mode', 'aim'); span = swd.get('span', 11)
    if mode == 'carry':
        c = (cx + dx + 1, my0 + 2)
        cells, tip, pull = bow_rows(c, (0, 1), 0, False, 8)
        mitts = [(c[0] - 3, c[1]), (c[0] + 3, c[1])]
        arms = {**arm_cells((cx + dx - 5, my0 - 1), mitts[0]), **arm_cells((cx + dx + 5, my0 - 1), mitts[1])}
        return dict(cells=cells, tip=tip, behind=back, mitts=mitts, arms=arms, front_cells=[])
    toward = -1 if back else 1
    draw = swd.get('draw', 0); arrow = swd.get('arrow', True)
    sp = min(span, 7)
    c = (cx + dx + 1, body_top - 15) if back else (cx + dx + 2, my0 + 3)
    cells, tip, pull = bow_vertical(c, toward, draw, arrow, sp)
    mitts = [c, pull]
    arms = {**arm_cells((cx + dx + 5, my0 - 1), c), **arm_cells((cx + dx - 4, my0 - 1), pull)}
    fc = []
    if back:
        fc = [(cx + dx + 6, my0, 't'), (cx + dx + 7, my0, 't'), (cx + dx + 7, my0 + 1, 'T'), (cx + dx + 6, my0 + 1, 'T')]
    return dict(cells=cells, tip=tip, behind=back, mitts=mitts, arms=arms, front_cells=fc)


def bow_side_geom(swd, cx, dx, bdx, bend, body_top):
    mode = swd.get('mode', 'aim')
    S = (cx + 1 + dx + bdx - bend * .9, body_top + 1.5)
    if mode == 'carry':
        c = (cx + dx + bdx + 8, body_top + 5)
        cells, tip, pull = bow_rows(c, (1, 0), 0, False, int(swd.get('span', 11) * .8))
        mitts = [(c[0] - 1, c[1]), (c[0] - 1, c[1] + 3)]
        arms = {**arm_cells(S, mitts[0]), **arm_cells((S[0] - 1, S[1] + 1), mitts[1])}
        return dict(cells=cells, tip=tip, behind=False, mitts=mitts, arms=arms, front_cells=[])
    d = swd['dir']; bc = (S[0] + d[0] * 10, S[1] + d[1] * 10)
    cells, tip, pull = bow_rows(bc, d, swd.get('draw', 0), swd.get('arrow', True), swd.get('span', 11))
    arms = {**arm_cells(S, bc), **arm_cells((S[0] - 1, S[1] + 1), pull)}
    return dict(cells=cells, tip=tip, behind=False, mitts=[bc, pull], arms=arms, front_cells=[])


def draw_bow_layer(g, info, mode):
    """mode: 'behind' (antes do corpo: arco inteiro atras), 'arms' (bracos+maos, antes do contorno), 'post' (arco + maos por cima)."""
    if mode in ('behind', 'arms'):
        for (x, y), ch in info['arms'].items(): g.put(x, y, ch)
    if mode in ('behind', 'post'): stamp_cells(g, info['cells'])
    for m in info['mitts']:
        for (ox, oy) in ((0, 0), (1, 0), (0, 1), (1, 1)): g.put(round(m[0]) - 1 + ox, round(m[1]) - 1 + oy, 's' if oy == 0 else 'S')


_REI = False
_T = 0


def rei_cape(g, view, cx, body_top, dx=0, bdx=0, over=False):
    """Capa rasgada do Rei com chamas roxas na barra. over=True: de costas, a capa fica POR CIMA do corpo."""
    T = _T; hem = body_top + 8
    if view == 'side':
        for y in range(body_top - 1, hem + 1):
            k = (y - body_top + 1) / (hem - body_top + 1)
            x1 = cx + 1 + dx + bdx; x0 = int(cx - 3 + dx + bdx - 3 - k * 9)
            for x in range(x0, x1 + 1):
                g.put(x, y, 'H' if x == x0 or y == body_top - 1 else ('E' if (x + y) % 4 else 'e'))
        xs = range(int(cx - 15 + dx + bdx), int(cx - 2 + dx + bdx))
    else:
        for y in range(body_top - 1, hem + 1):
            k = (y - body_top + 1) / (hem - body_top + 1); hw = int(7 + k * 4)
            for x in range(cx - hw + dx, cx + hw + dx + 1):
                u = (x - cx - dx) / max(1, hw)
                g.put(x, y, 'H' if abs(u) > .85 or y == body_top - 1 else ('E' if u < 0 else 'e'))
        if over:
            for y in range(body_top + 1, hem): g.put(cx + dx, y, 'H')
        xs = range(cx - 11 + dx, cx + 12 + dx)
    for x in xs:                                                 # chamas roxas subindo da barra (so nas laterais: pernas livres)
        if view != 'side' and abs(x - cx - dx) < 5: continue
        h = 1 + int(2 + 2 * math.sin(T * .9 + x * 1.1))
        for k in range(h): g.put(x, hem - k + 1, 'W' if k == h - 1 else ('P' if k > 0 else 'Y'))


def stamp_cells(g, cells):
    for (x, y), c in cells.items(): g.put(x, y, c)
    for (x, y) in list(cells):
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if g.get(x + dx, y + dy) == '.': g.put(x + dx, y + dy, 'K')


# ---------------------------------------------------------------- composicao
W, H = 72, 64
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
    swd = p.get('sw'); tip = None; hxy = None; behind = False; hands2 = []; bowinfo = None
    if swd:
        side = swd.get('side', 'r')
        al_, ar_ = p.get('al', (0, 0)), p.get('ar', (0, 0))
        hxy = (cx + (7 if side == 'r' else -7) + dx + (ar_ if side == 'r' else al_)[0] + 1, my0 + 1 + (ar_ if side == 'r' else al_)[1])
        if side != 'r': hxy = (hxy[0] - 1, hxy[1])
        if swd.get('kind') == 'bow':
            bowinfo = bow_front_geom(swd, back, cx, dx, my0, body_top)
            cells, tip, behind, hands2 = bowinfo['cells'], bowinfo['tip'], bowinfo['behind'], bowinfo['mitts']
            if behind: draw_bow_layer(g, bowinfo, 'behind')
        else:
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
    if not p.get('nomitt') and not bow:
        g.stamp(MITT_L, cx - 9 + dx + al[0], my + al[1])
        g.stamp([r[::-1] for r in MITT_L], cx + 6 + dx + ar[0], my + ar[1])
    # cabeca
    hx, hy = cx - 11 + dx + p.get('hdx', 0), body_top - 17 + p.get('hdy', 0)
    head = list(HEAD_B if back else (HEAD_F_UP if p.get('look') == 'up' else HEAD_F))
    hat = p.get('hat', DEFAULT_HAT[cls]); outfit = p.get('outfit', DEFAULT_OUTFIT[cls])
    if hat == 'cap': head = cap_head(head, 'front')
    elif hat == 'hood': head = hood_head(head, 'front')
    elif hat in ('helm', 'kinghelm'): head = helm_head(head, 'back' if back else 'front')
    if p.get('face', 'n') != 'n' and not back:
        head = face_front(head, p['face'])
    g.stamp(head, hx, hy, mirror=True, rshade=RSH_F)
    accessory2(g, hat, 'front', hx, hy, back)
    post_accessory(g, cls, 'front', cx, body_top, dx, back)
    if bowinfo:
        for (x, y, ch) in bowinfo['front_cells']: g.put(x, y, ch)
        if not behind: draw_bow_layer(g, bowinfo, 'arms')
    autoline(g)
    sw2 = p.get('sw2')
    if sw2:
        h2 = (cx - 7 + dx + al[0], my + 1 + al[1])
        c2, t2 = sword_rows(h2, sw2['ang'], sw2.get('len', 8), 1)
        stamp_cells(g, c2)
        for (ox, oy) in ((0, 0), (1, 0), (0, 1), (1, 1)): g.put(round(h2[0]) - 1 + ox, round(h2[1]) - 1 + oy, 's' if oy == 0 else 'S')
    # espada separada (por cima do corpo, exceto quando passa atras da cabeca)
    if swd:
        if bowinfo:
            if not behind: draw_bow_layer(g, bowinfo, 'post')
        else:
            if not behind: stamp_cells(g, cells)
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
    bowinfo = None
    if swd:
        hxy = (cx + 4 + dx + af_[0] + 1, body_top + 4 + af_[1])
        if swd.get('kind') == 'bow':
            bowinfo = bow_side_geom(swd, cx, dx, p.get('bdx', 0), p.get('bend', 0), body_top)
            cells, tip, behind, hands2 = bowinfo['cells'], bowinfo['tip'], False, bowinfo['mitts']
        else:
            cells, tip, behind, hands2 = weapon_rows(swd, hxy, 'side', False, (hxy[0] + 2, hxy[1]))
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
    if not p.get('nomitt') and not bowinfo: g.stamp(['ss', 'sS'], cx - 6 + dx + ab[0], body_top + 3 + ab[1])
    # cabeca (perfil)
    hx, hy = cx - 11 + dx + p.get('hdx', 0), body_top - 17 + p.get('hdy', 0)
    head = make_head_side(*FACES.get(p.get('face', 'n'), ('n', 'open')), p.get('look', 'n'))
    hat = p.get('hat', DEFAULT_HAT[cls]); outfit = p.get('outfit', DEFAULT_OUTFIT[cls])
    if hat == 'cap': head = cap_head_side(head)
    elif hat == 'hood': head = hood_head_side(head)
    elif hat in ('helm', 'kinghelm'): head = helm_head_side(head)
    g.stamp(head, hx, hy)
    accessory2(g, hat, 'side', hx, hy)
    if not p.get('nomitt') and not bowinfo: g.stamp(['ss', 'sS'], cx + 3 + dx + af[0], body_top + 3 + af[1])
    if bowinfo: draw_bow_layer(g, bowinfo, 'arms')
    autoline(g)
    sw2 = p.get('sw2')
    if sw2:
        h2 = (cx - 4 + dx + ab[0], body_top + 4 + ab[1])
        c2, t2 = sword_rows(h2, sw2['ang'], sw2.get('len', 8), 1)
        stamp_cells(g, c2)
        for (ox, oy) in ((0, 0), (1, 0), (0, 1), (1, 1)): g.put(round(h2[0]) - 1 + ox, round(h2[1]) - 1 + oy, 's' if oy == 0 else 'S')
    if swd:
        if bowinfo: draw_bow_layer(g, bowinfo, 'post')
        else:
            if not behind: stamp_cells(g, cells)
            mc = hxy
            g.put(round(mc[0]) - 1, round(mc[1]) - 1, 's'); g.put(round(mc[0]), round(mc[1]) - 1, 's')
            g.put(round(mc[0]) - 1, round(mc[1]), 'S'); g.put(round(mc[0]), round(mc[1]), 'S')
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
    'espada_ferro': dict(kind='sword', len=12, guard=2, pal=dict(A='#e6eef6', a='#8190a8', g='#8a6a3a', N='#4a3020')),
    'espada_aco': dict(kind='sword', len=13, guard=3, pal=dict(A='#f6faff', a='#9cb0d2', g='#e8b840', N='#6e4228')),
    'espada_longa': dict(kind='sword', len=16, guard=3, pal=dict(A='#eef4ff', a='#8aa0c8', g='#c8a040', N='#4a3020')),
    'montante': dict(kind='sword', len=17, guard=4, wide=True, pal=dict(A='#e0e8f0', a='#8890a8', g='#a0a0b0', N='#3a2a20')),
    'espada_dourada': dict(kind='sword', len=14, guard=4, gem=True, pal=dict(A='#fff4a8', a='#e8b840', g='#f4cc58', N='#7a4a20')),
    'espada_chamas': dict(kind='sword', len=14, guard=3, glow='fire', pal=dict(A='#ffe070', a='#ff7a20', g='#8a2a10', N='#3a1a10', Z='#fff0a0', z='#ff6a20')),
    'espada_gelo': dict(kind='sword', len=14, guard=3, glow='ice', pal=dict(A='#e8fcff', a='#58c8f0', g='#3a78c8', N='#244a7a', Z='#ffffff')),
    'espada_sombria': dict(kind='sword', len=14, guard=3, glow='dark', serrate=True, pal=dict(A='#b080ff', a='#3a2070', g='#1a1030', N='#0c0818', z='#d8b0ff')),
    'serra_cruel': dict(kind='sword', len=12, guard=2, serrate=True, wide=True, pal=dict(A='#d8d0c0', a='#7a6a58', g='#5a3a20', N='#2a1a10')),
    # formatos novos (silhueta diferente, nao so cor)
    'espada_larga': dict(kind='sword', len=14, guard=3, shape='broad', pal=dict(A='#e8eef8', a='#8c9cb8', g='#b89040', N='#4a3020')),
    'katana': dict(kind='sword', len=15, guard=2, shape='katana', pal=dict(A='#f4f8ff', a='#8a9ab8', g='#2a2a3a', N='#6a1c24')),
    'cimitarra': dict(kind='sword', len=14, guard=2, shape='scimitar', pal=dict(A='#f0e8c8', a='#a89058', g='#c8a030', N='#5a2a18')),
    'florete': dict(kind='sword', len=17, guard=3, shape='rapier', pal=dict(A='#f4f8ff', a='#8a9ab8', g='#e8b840', N='#4a2030')),
    'facao': dict(kind='sword', len=12, guard=2, shape='cleaver', pal=dict(A='#c8c0b0', a='#6a6050', g='#5a3a20', N='#3a2418')),
    'chamejante': dict(kind='sword', len=16, guard=3, shape='flame', glow='fire', pal=dict(A='#ffd060', a='#e04818', g='#6a1c10', N='#2a1008', Z='#fff0a0', z='#ff6a20')),
    'montante_real': dict(kind='sword', len=18, guard=4, shape='great', gem=True, pal=dict(A='#eef2fa', a='#7c88a8', g='#e8b840', N='#3a2a20')),
    'machado': dict(kind='sword', len=16, guard=1, shape='axe', pal=dict(A='#c8d0dc', a='#6a7488', g='#7a5a30', N='#5a3a20')),
    'espada_rei': dict(kind='sword', len=18, guard=3, shape='great', gstyle='cross', glow='ice', pal=dict(A='#d8f4ff', a='#6ab0e4', g='#2a2c44', N='#1c1830', Z='#ffffff')),
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


for _w in WEAPONS.values():                      # espadas mais longas e imponentes (cabeca grande pede arma grande)
    if _w['kind'] == 'sword' and not _w.get('_scaled'):
        _w['len'] = round(_w['len'] * 1.3); _w['_scaled'] = True


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
    dict(tn=3, dy=1, ar=(-2, 0), sw=dict(ang=60, len=12, side='r')),
    dict(tn=3, ar=(0, 0), sw=dict(ang=140, len=12, side='r')),
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
    dict(tn=3, hdx=-3, bdx=-2, dx=-2, ar=(-3, 2), al=(3, 0), sw=dict(ang=258, len=12)),
    dict(tn=3, hdx=-3, bdx=-2, dx=-2, ar=(-3, 3), al=(3, 0), sw=dict(ang=272, len=12), face='shout'),
    dict(tn=3, hdx=2, bdx=1, dx=1, ar=(1, -3), al=(-1, 0), sw=dict(ang=165, len=12), face='shout'),
    dict(tn=2, dy=1, hdx=4, bdx=2, dx=3, ar=(4, -1), al=(-2, 0), bl=(-2, 0), br=(2, 0), sw=dict(ang=128, len=12), face='shout'),
    dict(tn=2, dy=1, hdx=4, bdx=2, dx=3, ar=(5, 1), al=(-2, 0), bl=(-2, 0), br=(2, 0), sw=dict(ang=88, len=12)),
    dict(tn=3, hdx=2, bdx=1, dx=2, ar=(4, 1), al=(-1, 0), bl=(-1, 0), br=(1, 0), sw=dict(ang=92, len=12)),
    dict(tn=3, hdx=1, bdx=0, dx=1, ar=(1, 0), sw=dict(ang=112, len=12)),
]


def _lerp_ang(a, b, t):
    d = ((b - a + 180) % 360) - 180
    return (a + d * t) % 360


def interp_pose(a, b, t):
    out = {}
    for k in set(a) | set(b):
        va, vb = a.get(k), b.get(k)
        if va is None or vb is None: out[k] = va if va is not None else vb; continue
        if k in ('sw', 'sw2') and isinstance(va, dict) and isinstance(vb, dict):
            d = dict(va)
            if 'ang' in va and 'ang' in vb: d['ang'] = _lerp_ang(va['ang'], vb['ang'], t)
            if 'len' in va and 'len' in vb: d['len'] = va['len'] + (vb['len'] - va['len']) * t
            for kk in ('draw',):
                if kk in va and kk in vb: d[kk] = va[kk] + (vb[kk] - va[kk]) * t
            out[k] = d
        elif isinstance(va, (int, float)) and isinstance(vb, (int, float)): out[k] = int(round(va + (vb - va) * t))
        elif isinstance(va, (tuple, list)) and isinstance(vb, (tuple, list)) and len(va) == len(vb) and all(isinstance(x, (int, float)) for x in va + vb):
            out[k] = tuple(int(round(x + (y - x) * t)) for x, y in zip(va, vb))
        else: out[k] = va if t < .5 else vb
    return out


def densify(ps, k=2):
    """k-1 poses interpoladas entre cada par: animacao com k vezes mais quadros (mais fluida)"""
    if k <= 1: return list(ps)
    out = []
    for i in range(len(ps) - 1):
        for j in range(k): out.append(interp_pose(ps[i], ps[i + 1], j / k))
    out.append(dict(ps[-1]))
    return out


def extra_poses(kind, view):
    """conjurar (bracos e espada para o alto), dano (recuo) e morte (desaba) - valem para qualquer personagem com espada"""
    up = 188
    if kind == 'cast':
        sw = lambda a: dict(ang=a, len=12, side='r') if view != 'right' else dict(ang=a, len=12)
        return [dict(tn=3, ar=(0, 0), sw=sw(165)), dict(tn=2, ar=(0, -2), al=(0, -1), sw=sw(180), hdy=0),
                dict(tn=3, ar=(0, -5), al=(0, -5), sw=sw(up), face='angry', hdy=-1), dict(tn=3, ar=(0, -6), al=(0, -6), sw=sw(up), face='shout', hdy=-1, dy=-1),
                dict(tn=3, ar=(0, -6), al=(0, -6), sw=sw(up), face='shout', hdy=-1, dy=-1), dict(tn=3, ar=(0, -6), al=(0, -6), sw=sw(up), face='shout', hdy=-1, dy=-1),
                dict(tn=3, ar=(0, -3), al=(0, -3), sw=sw(175), face='shout'), dict(tn=3, ar=(0, 0), sw=sw(165))]
    if kind == 'hurt':
        sw = lambda a: dict(ang=a, len=12, side='r') if view != 'right' else dict(ang=a, len=12)
        return [dict(tn=2, dx=-1, hdx=-1, ar=(-1, 1), al=(1, 1), sw=sw(150), face='hurt'), dict(tn=2, dx=-2, hdx=-2, hdy=1, ar=(-2, 1), al=(2, 1), sw=sw(140), face='hurt'),
                dict(tn=3, dx=-1, hdx=-1, ar=(-1, 0), sw=sw(150), face='angry'), dict(tn=3, ar=(0, 0), sw=sw(165), face='angry')]
    sw = lambda a: dict(ang=a, len=12, side='r') if view != 'right' else dict(ang=a, len=12)
    return [dict(tn=2, dx=-1, hdx=-1, ar=(-1, 1), sw=sw(150), face='shout'), dict(tn=1, dx=-2, dy=1, hdx=-2, hdy=1, ar=(-2, 2), al=(2, 2), sw=sw(130), face='hurt'),
            dict(tn=1, dx=-3, dy=3, hdx=-3, hdy=3, ar=(-3, 3), al=(3, 2), bl=(-2, 0), br=(2, 0), sw=sw(115), face='shout'),
            dict(tn=0, dx=-3, dy=5, hdx=-3, hdy=5, ar=(-3, 4), al=(3, 3), bl=(-3, 0), br=(3, 0), sw=sw(100), face='shout'),
            dict(tn=0, dx=-3, dy=7, hdx=-3, hdy=6, ar=(-3, 5), al=(3, 4), bl=(-3, 0), br=(3, 0), sw=sw(95)), dict(tn=0, dx=-3, dy=7, hdx=-3, hdy=6, ar=(-3, 5), al=(3, 4), bl=(-3, 0), br=(3, 0), sw=sw(92), face='dead')]


def anim(view, kind, cls='warrior', ps_override=None, appearance=None, dense=1):
    global _REI, _T
    out = []
    over = None
    if appearance:
        cls = appearance.get('cls', cls); over = make_palette(appearance)
    if kind == 'walk': ps = [walk_params(f, 8 * dense, view) for f in range(8 * dense)]
    elif kind == 'idle':
        ps = [idle_params(f, 6 * dense, view) for f in range(6 * dense)]
        if dense > 1:
            for _k in (len(ps) - 3, len(ps) - 2): ps[_k] = dict(ps[_k], face='blink')
            for _k in range(len(ps)): ps[_k]['hdy'] = -1 if (_k % len(ps)) in (len(ps) // 2 - 1, len(ps) // 2) else 0
    elif kind in ('cast', 'hurt', 'death'): ps = extra_poses(kind, view)
    else: ps = ATK_S if view == 'right' else (ATK_B if view == 'up' else ATK_F)
    if kind not in ('walk', 'idle') and dense > 1 and ps_override is None: ps = densify(ps, dense)
    if ps_override is not None: ps = ps_override
    _REI = (cls == 'rei')
    for _i, p in enumerate(ps):
        _T = _i
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
