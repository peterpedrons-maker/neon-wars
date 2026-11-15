"""Heroi v4: por partes + ciclo de andar de 4 poses (pernas de verdade), arma separada. Estilo 16 bits (rampas com troca de matiz, contorno seletivo)."""
import os
from PIL import Image
import pxrig
from pxrig import Grid, autoline, make_weapon

PAL = dict(K='#2a1a3a',
           J='#ffb454', H='#e8702c', h='#a8402e',            # cabelo (sombra puxa para vermelho/roxo)
           s='#ffd6b4', S='#e49a88', r='#f48c8c', e='#2a1a3a',  # pele
           P='#ffbc6a', O='#e8782e', o='#a2402c',              # tunica
           c='#a4d4ff', B='#4a88ea', b='#2a48a6',              # lenco
           N='#7a5c7c', n='#5a4262', d='#3a2a48',              # calca
           M='#b08458', m='#6e4634', D='#3e2420',              # botas
           t='#6e4228', y='#ffdc64',                           # cinto
           A='#f6faff', a='#9cb0d2', g='#eebc44')              # arma
SEL = {**{k: '#5c2018' for k in 'JHh'}, **{k: '#8c4a4c' for k in 'sSr'}, **{k: '#6a2430' for k in 'POo'},
       **{k: '#1c2a6c' for k in 'cBb'}, **{k: '#2a1a34' for k in 'Nnd'}, **{k: '#3a1e20' for k in 'MmDty'},
       **{k: '#3a4a70' for k in 'Aag'}}

HEAD_DOWN = ['..JHH', '.JJHH', 'JJHHH', 'JHHHH', 'HHHsH', 'hsssS', 'hsess', 'hsess', 'hrsss', '.SSss']
HEAD_UP = ['..JHH', '.JJHH', 'JJHHH', 'JHHHH', 'HHHhH', 'HhHHH', 'hHHhH', 'hHhHH', 'hhHHH', '.hhhH']
TORSO_DOWN = ['.bBBB', 'bBcBB', 'oPOOO', 'oPoPO', 'oOoOO', 'oOoOO', 'sSoOO', '.ttty']
TORSO_UP = ['.bBBB', 'bBBBB', 'oPOOO', 'oPoMM', 'oOoMt', 'oOoMt', 'sSoMt', '.ttty']
RSH_HAIR = dict(J='H', P='O', c='B', M='m')
HEAD_SIDE = ['..JJHHH....', '.JJHHHHHH..', 'JJHHHHHHss.', 'JHHHHHhssss', 'HHHHhhhsess', 'HHHhhhhsess', 'hHhhhssSrss', '.hhhhsssSS.', '..hhhsSSS..']
TORSO_SIDE = ['.bBBBb.', 'bBcBBBb', 'oPOOOOo', 'oPOOOOo', 'oOOOOOo', 'oOOOOOo', '.ttttty', '.oOOOo.']


def leg(L, left=True, side=False):
    """Perna de frente/costas: 4 de largura. L linhas (calca + 2 de bota)."""
    rows = ['Nnnd'] * (L - 2) + ['MMmd', 'mmmD']
    return rows if left else [r[::-1] for r in rows]


def hand_shift(g, x_l, x_r, y, left_up=False, right_up=False):
    # eleva a mao 1px (braco "para tras"): troca mao por manga
    if left_up:
        for x in (x_l, x_l + 1):
            g.put(x, y - 1, 's' if x == x_l else 'S'); g.put(x, y, 'o' if x == x_l else 'O')
    if right_up:
        for x in (x_r, x_r - 1):
            g.put(x, y - 1, 's' if x == x_r else 'S'); g.put(x, y, 'o' if x == x_r else 'O')


def hero_frame(face, step, W=18, H=30):
    """step: 'stand' | 0..3 (ciclo de andar)."""
    g = Grid(W, H)
    cx = 4
    if face in ('down', 'up'):
        b = 1 if step in (0, 2) else 0
        L = {'stand': (6, 6), 0: (7, 5), 1: (6, 4), 2: (5, 7), 3: (4, 6)}[step]
        head = HEAD_DOWN if face == 'down' else HEAD_UP
        torso = TORSO_DOWN if face == 'down' else TORSO_UP
        y0 = 2 + b
        # pernas primeiro (atras do tronco)
        g.stamp(leg(L[0], True), cx + 1, y0 + 18)
        g.stamp(leg(L[1], False), cx + 5, y0 + 18)
        g.stamp(torso, cx, y0 + 10, mirror=True, rshade=RSH_HAIR)
        g.stamp(head, cx, y0, mirror=True, rshade=RSH_HAIR)
        # balanco dos bracos (oposto as pernas)
        hy = y0 + 16
        if step == 0: hand_shift(g, cx + 0, cx + 9, hy, left_up=True)
        if step == 2: hand_shift(g, cx + 0, cx + 9, hy, right_up=True)
        autoline(g)
        # arma SEPARADA na mao direita (lado direito da tela)
        wx = cx + 9
        wy = hy
        wpn, (ox, oy) = make_weapon('sword', (wx + 2, wy + 1), (wx + 3, wy + 10), None)
        # a arma balanca: frente quando o braco direito vai a frente
        dy = 1 if step == 2 else (-1 if step == 0 else 0)
        g.stamp(wpn.rows(), ox, oy + dy)
        # mao por cima do cabo
        g.put(wx, hy + dy, 's'); g.put(wx - 1, hy + dy, 'S')
        g.put(wx + 1, hy + dy, 'K')
        return g
    # ---------------- perfil (olhando para a direita)
    b = 1 if step in (0, 2) else 0
    y0 = 2 + b
    cx = 4
    # pernas (tesoura): frente e tras
    fx = {'stand': (0, 0), 0: (3, -3), 1: (1, 0), 2: (-3, 3), 3: (0, 1)}[step]
    lift = {'stand': (0, 0), 0: (0, 1), 1: (0, 2), 2: (1, 0), 3: (2, 0)}[step]
    hipx = cx + 3
    for k, (dx, lf) in enumerate(((fx[1], lift[1]), (fx[0], lift[0]))):   # tras primeiro, depois frente
        shade = 'd' if k == 0 else 'n'
        top = y0 + 18
        foot_y = top + 6 - lf
        for yy in range(top, foot_y - 2):
            t = (yy - top) / max(1, foot_y - 2 - top)
            xx = hipx + round(dx * t)
            for x in range(xx, xx + 3): g.put(x, yy, shade if x == xx + 2 or k == 0 else ('N' if x == xx else 'n'))
        xx = hipx + dx
        for x in range(xx, xx + 4): g.put(x, foot_y - 2, 'M' if x == xx else 'm')
        for x in range(xx, xx + 4): g.put(x, foot_y - 1, 'm' if x < xx + 3 else 'D')
    g.stamp(TORSO_SIDE, cx + 2, y0 + 10)
    g.stamp(HEAD_SIDE, cx, y0)
    # bracos: o de tras e o da frente (balancam)
    sw = {'stand': 0, 0: -2, 1: 0, 2: 2, 3: 0}[step]
    sx, sy = cx + 5, y0 + 12
    for k in range(5):
        for x in (sx + round(-sw * k / 4), sx + round(-sw * k / 4) + 1):
            g.put(x, sy + k, 'O' if x == sx + round(-sw * k / 4) else 'o')
    hx_, hy_ = sx + round(-sw), sy + 5
    g.put(hx_, hy_, 's'); g.put(hx_ + 1, hy_, 'S')
    # braco da frente (com a espada)
    fx_, fy_ = sx + 2 + round(sw * 1), sy + 5
    for k in range(5):
        xx = sx + 1 + round(sw * k / 4)
        g.put(xx, sy + k, 'P'); g.put(xx + 1, sy + k, 'O')
    autoline(g)
    wpn, (ox, oy) = make_weapon('sword', (fx_ + 1, fy_), (fx_ + 7, fy_ + 6), None)
    g.stamp(wpn.rows(), ox, oy)
    g.put(fx_ + 1, fy_, 's'); g.put(fx_, fy_, 'S')
    return g


def render(g):
    return g.render(PAL, SEL)


def sheet(zoom=8):
    import pxtool
    from teste_clareira import OUT
    items = []
    for face in ('down', 'up', 'right'):
        for step in ('stand', 0, 1, 2, 3):
            items.append(render(hero_frame(face, step)))
    s = pxtool.sheet(items, zoom, cols=5)
    return s


if __name__ == '__main__':
    from teste_clareira import OUT
    s = sheet()
    s.convert('RGB').save('/tmp/claude-0/-home-user-neon-wars/3ffd125f-a99a-599e-8554-f2b481e86fc1/scratchpad/h4_v1.png')
    print('ok')
