"""Goblin (anda) e slime (pula) por partes, estilo 16 bits."""
from pxrig import Grid, autoline, make_weapon

GOB = dict(K='#1c2a20', L='#9ad25a', l='#cdf08a', G='#62a63c', g='#2e6a40', y='#ffe25a', e='#2a1a3a', w='#ffffff', d='#2a1630',
           t='#9a6a3c', T='#6a4228', M='#b08458', m='#6e4634', D='#3e2420', A='#f6faff', a='#9cb0d2')
GSEL = {**{k: '#24502c' for k in 'LlGgyw'}, **{k: '#3a1e20' for k in 'tTMmD'}}
HEAD_D = ['...LLGG', '..lLLGG', 'L.LLLGG', 'LLLgggG', 'LLLyeGG', '.LLLLGG', '..LGdww', '...LLGG']
HEAD_U = ['...LLGG', '..lLLGG', 'L.LLLGG', 'LLLLLGG', 'LLLLGGG', '.LLLLGG', '..LGGGG', '...LGGG']
TORSO_D = ['..LLGG', '.LLLGG', 'gLgLGG', 'gLgLGG', 'gLgGGG', 'LLgGGG', '.tttTT', '.tttTT', '..ttTT']
TORSO_U = ['..LLGG', '.LLLGG', 'gLgLGg', 'gLgGgG', 'gLgGGg', 'LLgGgG', '.tttTT', '.tttTT', '..ttTT']
RSH = dict(L='G', l='L', t='T')
HEAD_S = ['...lLLL....', 'L.lLLLLG...', 'LLLLLLLGgg.', '.LLLLGGGye.', '..LLLGGGGGG', '..LLGGGGGGG', '..LLGGdwdG.', '...LLGGGG..']
TORSO_S = ['.LLGGL.', 'LLLGGGG', 'LLGGGGg', 'LLGGGGg', 'LGGGGGg', '.tttttT', '.tttTT.', '..tTT..']


def leg(L, left=True):
    rows = ['LGGg'] * (L - 2) + ['MMmD', 'mmmD']
    return rows if left else [r[::-1] for r in rows]


def goblin_frame(face, step, W=20, H=28):
    g = Grid(W, H)
    cx = 4
    if face in ('down', 'up'):
        b = 1 if step in (0, 2) else 0
        L = {'stand': (4, 4), 0: (5, 3), 1: (4, 3), 2: (3, 5), 3: (3, 4)}[step]
        y0 = 2 + b
        g.stamp(leg(L[0], True), cx + 1, y0 + 17)
        g.stamp(leg(L[1], False), cx + 5, y0 + 17)
        g.stamp(TORSO_D if face == 'down' else TORSO_U, cx, y0 + 8, mirror=True, rshade=RSH)
        g.stamp(HEAD_D if face == 'down' else HEAD_U, cx - 2, y0, mirror=True, rshade=RSH)
        autoline(g)
        hy = y0 + 13
        dy = 1 if step == 2 else (-1 if step == 0 else 0)
        wpn, (ox, oy) = make_weapon('club', (cx + 11, hy + dy), (cx + 14, hy + dy - 8), None)
        g.stamp(wpn.rows(), ox, oy)
        g.put(cx + 10, hy + dy, 'L'); g.put(cx + 9, hy + dy, 'G')
        return g
    b = 1 if step in (0, 2) else 0
    y0 = 2 + b
    fx = {'stand': (0, 0), 0: (2, -2), 1: (1, 0), 2: (-2, 2), 3: (0, 1)}[step]
    lift = {'stand': (0, 0), 0: (0, 1), 1: (0, 2), 2: (1, 0), 3: (2, 0)}[step]
    hipx = cx + 3
    for k, (dx, lf) in enumerate(((fx[1], lift[1]), (fx[0], lift[0]))):
        top = y0 + 17
        foot_y = top + 5 - lf
        for yy in range(top, foot_y - 2):
            xx = hipx + round(dx * (yy - top) / max(1, foot_y - 2 - top))
            for x in range(xx, xx + 3): g.put(x, yy, 'g' if k == 0 else ('L' if x == xx else 'G'))
        xx = hipx + dx
        for x in range(xx, xx + 4): g.put(x, foot_y - 2, 'M' if x == xx else 'm')
        for x in range(xx, xx + 4): g.put(x, foot_y - 1, 'm' if x < xx + 3 else 'D')
    g.stamp(TORSO_S, cx + 3, y0 + 8)
    g.stamp(HEAD_S, cx, y0)
    sw = {'stand': 0, 0: -2, 1: 0, 2: 2, 3: 0}[step]
    sx, sy = cx + 6, y0 + 10
    for k in range(4):
        xx = sx + round(-sw * k / 3)
        g.put(xx, sy + k, 'G'); g.put(xx + 1, sy + k, 'g')
    fxh, fyh = sx + 2 + sw, sy + 4
    for k in range(4):
        xx = sx + 1 + round(sw * k / 3)
        g.put(xx, sy + k, 'L'); g.put(xx + 1, sy + k, 'G')
    autoline(g)
    wpn, (ox, oy) = make_weapon('club', (fxh + 1, fyh), (fxh + 7, fyh - 5), None)
    g.stamp(wpn.rows(), ox, oy)
    g.put(fxh + 1, fyh, 'L'); g.put(fxh, fyh, 'G')
    return g


SLIME = dict(K='#10301c', L='#a4e866', l='#e6ffc0', G='#5cbc3c', g='#2e8040', e='#1a2a30', w='#ffffff')
SLIME_B = dict(K='#10203a', L='#78c8ff', l='#e0f6ff', G='#3a8ae0', g='#2a4ea8', e='#1a2a30', w='#ffffff')
SLIME_O = dict(K='#3a1810', L='#ffc070', l='#fff0c0', G='#f08a30', g='#b04a24', e='#1a2a30', w='#ffffff')
SLIME_FR = {
    'idle': ['....LLL', '..lLLLL', '.lLLLLL', 'lLLLLLL', 'LLLLeLL', 'LLLLeLL', 'GGGGGGG', 'ggggggg'],
    'squash': ['.....LL', '...lLLL', '.lLLLLL', 'lLLLLLL', 'LLLLLeL', 'LLLLLeL', 'GGGGGGG', 'GGGGGGG', 'ggggggg'][:7] + ['ggggggg'],
    'stretch': ['.....LL', '....lLL', '...lLLL', '..lLLLL', '..LLLLL', '..LLeLL', '..LLeLL', '..LLLLL', '..GGGGG', '..ggggg'],
    'air': ['....LLL', '..lLLLL', '.lLLLLL', 'lLLLLLL', 'LLLLeLL', 'LLLLeLL', 'GGGGGGG', '.ggggg.'],
}
SLIME_FR['squash'] = ['...LLLL', '.lLLLLL', 'lLLLLLL', 'LLLLLLL', 'LLLeLLL', 'GGGGGGG', 'ggggggg']


def slime_frame(name, pal=SLIME):
    rows = SLIME_FR[name]
    g = Grid(18, 14)
    # alinhado pela base
    g.stamp(rows, 2, 14 - len(rows) - 1, mirror=True)
    # mira nos olhos: pupila + brilho
    autoline(g)
    return g, pal
