#!/usr/bin/env python3
"""skel3: heroi 16 bits com DESIGN desenhado a mao (cabeca grande, rosto, luvas, botas) + sombreado em blocos (cel),
sobre o esqueleto 2D. Vistas: right (lado), down (frente), up (costas). Andar 8, parado 8, ataque 10 poses em cada vista."""
import math
from PIL import Image
import skel2d as K
from skel2d import Buf, RAMPS, OUTL, capsule, ellipse, poly, v, add, side_pose, ATK, walk_pose, idle_pose, spring_chain

W, HGT = 64, 56
GY = 48

R3 = dict(RAMPS)
R3['glove'] = ['#3e2018', '#6a3e24', '#8a5a34', '#c08a54']
R3['tunic'] = ['#a8402c', '#d8682e', '#f6923c', '#ffc474']
R3['sleeve'] = ['#7a2c28', '#a8402c', '#c8582c', '#e8782e']
R3['pants'] = ['#34264a', '#503e66', '#6a5886', '#8a78a8']
R3['skin'] = ['#d88a82', '#eeaa9a', '#ffd2b0', '#ffe8d0']
O3 = dict(OUTL)
O3['glove'] = '#1e0e0c'; O3['sleeve'] = '#4a1c20'

# ---- mapeamento de caracteres dos sprites desenhados a mao
CH = {'x': ('hair', 0), 'h': ('hair', 1), 'H': ('hair', 2), 'J': ('hair', 3),
      'o': ('skin', 0), 'S': ('skin', 1), 's': ('skin', 2), 't': ('skin', 3),
      'r': ('blush', 2), 'e': ('eye', 0), 'W': ('white', 3), 'w': ('white', 2), 'k': ('eye', 0), 'n': ('skin', 1),
      'a': ('glove', 0), 'b': ('glove', 1), 'c': ('glove', 2), 'd': ('glove', 3),
      'A': ('boot', 0), 'B': ('boot', 1), 'C': ('boot', 2), 'D': ('boot', 3),
      'P': ('pants', 1), 'p': ('pants', 2), 'q': ('pants', 3),
      'T': ('tunic', 1), 'U': ('tunic', 2), 'V': ('tunic', 3), 'Y': ('tunic', 0),
      'g': ('gold', 2), 'G': ('gold', 3), 'F': ('scarf', 1), 'f': ('scarf', 2), 'E': ('scarf', 3), 'z': ('scarf', 0)}


def stamp(B, rows, ox, oy, flip=False, far=0, mirror=False, rsh=None, pid=True):
    """Estampa sprite desenhado a mao. mirror: rows = metade esquerda (espelha). rsh: troca de tons na metade direita."""
    B.n += 1
    rsh = rsh or {}
    bx0, by0 = int(math.floor(ox + .5)), int(math.floor(oy + .5))
    for j, r in enumerate(rows):
        if mirror:
            r = r + ''.join(rsh.get(c, c) for c in reversed(r))
        if flip: r = r[::-1]
        for i, c in enumerate(r):
            if c == '.': continue
            mat, bd = CH[c]
            x, y = bx0 + i, by0 + j
            if 0 <= x < B.w and 0 <= y < B.h:
                B.m[y][x] = mat; B.b[y][x] = max(0, bd - far); B.pid[y][x] = B.n; B.line[y][x] = False


# ---------------------------------------------------------------- partes desenhadas a mao
# CABECA LATERAL (olhando para a direita) 16x15: cabelo ruivo, olho grande com brilho, bochecha, nariz, boca
HEAD_R = [
    '....xhHHHHHH....',
    '..xhHJJJJJHHH...',
    '.xhHJJJJJHHHHH..',
    '.xhHJJJHHHHHHHs.',
    'xhHJJHHHHHHHhsss',
    'xhHJHHHHHHhhssss',
    'xhHHHHhhhsssWess',
    'xhHHHhhhssssees s'.replace(' ', ''),
    '.hHHhhhhsssseens',
    '.hhHhhhsssrrssss',
    '..xhhhhhsssssSss',
    '...xhhhhhssssSkk'[:16],
    '....xhhhhhssSSSs',
    '.....xhhhSSSSoo.',
    '......xhhoSSoo..',
]
# CABECA FRONTAL (metade esquerda, 8 colunas; espelhada = 16x15)
HEAD_F = [
    '.....xhH', '...xhHJJ', '..xhHJJJ', '.xhHJJJH', '.xhHJJHH', 'xhHHJHHH', 'xhHHHHhH', 'xhHhHsHs',
    'xhhsssss', 'xhhsWess', 'xhhseess', 'xhhseess', '.xhrrsss', '..xhssSk', '....xSss']
HEAD_F_RSH = dict(J='H', H='h', W='w')
# CABECA DE COSTAS (metade esquerda): so cabelo + nuca
HEAD_B = [
    '.....xhH', '...xhHJJ', '..xhHJJJ', '.xhHJJJH', '.xhHJJHH', 'xhHHJHHH', 'xhHHHHHH', 'xhHHHHHh',
    'xhHHHhHh', 'xhHHHHhh', 'xhhHHhhh', '.xhhHhhh', '..xhhhhh', '...xhhSS', '.....xSS']
# BOCA ABERTA (ataque): troca da linha da boca
MOUTH_OPEN_R = '...xhhhhhsssSkkk'
LUVA = ['.dc.', 'dccb', 'cccb', '.cb.']             # punho lateral 4x4
LUVA_F = ['.dcc.', 'dcccb', 'cccbb', '.bbb.']       # frontal 5x4
BOTA_R = ['..dCC....', '..CCC....', '..BBB....', '..BBBBBB.', '.CBBBBBBD', '.AAAAAAAA']  # lado (pe a direita)
BOTA_F = ['.DCC.', '.CCB.', 'CCCBA', 'CCBBA', 'AAAAA']
BOTA_B = ['.CCB.', '.CBB.', 'CCBBA', 'CBBBA', 'AAAAA']


# ---------------------------------------------------------------- pintura em blocos (cel)
def cel(B, S, mat, far=0, depth=1, inner=True, base=2, light=True):
    """S = conjunto de pixels. Luz em cima-esquerda: borda superior/esquerda clara, inferior/direita escura (blocos)."""
    B.n += 1
    for (x, y) in S:
        bd = base
        if light and ((x - 1, y - 1) not in S or (x, y - 1) not in S and (x - 1, y) not in S): bd = base + 1
        if (x + 1, y) not in S or (x, y + 1) not in S: bd = base - 1
        if depth >= 2 and ((x + 2, y + 1) not in S or (x + 1, y + 2) not in S) and bd == base: bd = base - 1 if base > 1 else base
        if depth >= 2 and ((x + 2, y + 2) not in S) and bd >= base: bd = base - 1
        if 0 <= x < B.w and 0 <= y < B.h:
            B.m[y][x] = mat; B.b[y][x] = max(0, min(3, bd - far)); B.pid[y][x] = B.n; B.line[y][x] = False
    if inner:
        for (x, y) in S:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                q = (x + dx, y + dy)
                if q not in S and 0 <= q[0] < B.w and 0 <= q[1] < B.h:
                    if B.m[q[1]][q[0]] is not None and B.pid[q[1]][q[0]] != B.n:
                        B.line[y][x] = True
    return S


def pix(f_bb):
    f, bb = f_bb
    x0, y0, x1, y1 = bb
    S = set()
    for y in range(max(0, int(y0)), int(y1) + 1):
        for x in range(max(0, int(x0)), int(x1) + 1):
            if f(x + .5, y + .5) is not None: S.add((x, y))
    return S


def limb(p0, p1, w0, w1): return pix(capsule(p0, p1, w0, w1))
def ell(cx, cy, rx, ry): return pix(ellipse(cx, cy, rx, ry))
def pol(pts): return pix(poly(pts))


class B3(Buf):
    def __init__(self, w=W, h=HGT):
        super().__init__(w, h, R3, O3)


# ---------------------------------------------------------------- VISTA LATERAL
def draw_side3(j, tail=None, sec=None, strike=False):
    B = B3()
    P = j['P']; sh = j['sh']; ch = j['chest']
    ux, uy = math.sin(math.radians(j['lean'])), -math.cos(math.radians(j['lean']))
    nx, ny = -uy, ux          # normal para a frente
    # --- braco de tras (longe)
    cel(B, limb((sh[0] - .8, sh[1] + .8), j['fel'], 2.2, 1.9), 'sleeve', far=1)
    cel(B, limb(j['fel'], j['fhand'], 1.8, 1.5), 'glove', far=1)
    stamp(B, ['dc', 'cb'], j['fhand'][0] - 1, j['fhand'][1] - 1, far=1)
    # --- perna de tras
    def leg(name, far):
        knee, ank = j[name + 'knee'], j[name + 'ank']
        cel(B, limb(P, knee, 3.1, 2.7), 'pants', far=far)
        cel(B, limb(knee, ank, 2.6, 2.1), 'pants', far=far)
        B.put(knee[0] + .4, knee[1], 'pants', 3 - far) if not far else None
        stamp(B, BOTA_R, ank[0] - 3, ank[1] - 3, far=far)
    leg('f', 1)
    # --- tronco: silhueta de tunica (nao um tubo)
    def T(a, b): return (P[0] + ux * a + nx * b, P[1] + uy * a + ny * b)
    L1 = K.TORSO
    body = [T(L1 * .98, 2.6), T(L1 * .86, 4.4), T(L1 * .55, 4.4), T(L1 * .22, 4.2), T(-1.2, 5.6), T(-2.4, 4.4), T(-2.4, -5.4), T(L1 * .22, -4.2),
            T(L1 * .55, -4.4), T(L1 * .86, -4.6), T(L1 * .98, -3.0)]
    cel(B, pol(body), 'tunic', depth=2)
    # cinto + fivela
    belt = [T(2.0, 4.8), T(2.0, -4.4), T(.9, -4.5), T(.9, 4.9)]
    cel(B, pol(belt), 'belt', inner=False)
    bx, by = T(1.5, 4.2)
    stamp(B, ['gG', 'gg'], bx - 1, by - 1)
    # dobras e gola
    fx, fy = T(L1 * .5, -1.0); B.put(fx, fy, 'tunic', 1); fx, fy = T(L1 * .4, 1.5); B.put(fx, fy, 'tunic', 1)
    fx, fy = T(L1 * .62, 2.0); B.put(fx, fy, 'tunic', 3)
    leg('n', 0)
    # --- cachecol + cauda
    cel(B, ell(ch[0] + .9, ch[1] + .6, 4.4, 2.0), 'scarf')
    if tail:
        for i in range(len(tail) - 1):
            cel(B, limb(tail[i], tail[i + 1], 1.8 - i * .4, 1.4 - i * .4), 'scarf', inner=False)
    # --- rabo de cavalo
    hd = j['head']; hx, hy = hd
    if sec:
        cel(B, limb((hx - 6.2, hy - 1.0), sec, 2.4, 1.0), 'hair')
    # --- cabeca desenhada a mao (centro do crânio em hd)
    rows = list(HEAD_R)
    if strike: rows[11] = MOUTH_OPEN_R
    stamp(B, rows, hx - 8 + .5, hy - 7.5 + .5)
    # --- braco da frente
    cel(B, limb((sh[0] + .4, sh[1]), j['nel'], 2.4, 2.1), 'sleeve')
    cel(B, limb(j['nel'], j['nhand'], 2.0, 1.8), 'sleeve')
    # punho de couro (bracadeira) perto da mao
    hv = (j['nhand'][0] - j['nel'][0], j['nhand'][1] - j['nel'][1]); hl_ = math.hypot(*hv) or 1
    b0 = (j['nhand'][0] - hv[0] / hl_ * 2.2, j['nhand'][1] - hv[1] / hl_ * 2.2)
    cel(B, limb(b0, (j['nhand'][0] - hv[0] / hl_ * 1.0, j['nhand'][1] - hv[1] / hl_ * 1.0), 1.9, 1.9), 'glove', inner=False)
    # --- arma separada
    hand = j['nhand']
    wux, wuy = math.sin(math.radians(j['w'])), math.cos(math.radians(j['w']))
    tip = (hand[0] + wux * 15, hand[1] + wuy * 15)
    cel(B, limb((hand[0] + wux * 3, hand[1] + wuy * 3), tip, 1.5, .35), 'steel', base=2)
    gx, gy = hand[0] + wux * 2.8, hand[1] + wuy * 2.8
    cel(B, limb((gx - wuy * 3.2, gy + wux * 3.2), (gx + wuy * 3.2, gy - wux * 3.2), 1.0, 1.0), 'gold')
    cel(B, limb((hand[0] - wux * 3, hand[1] - wuy * 3), (hand[0] + wux * 2, hand[1] + wuy * 2), 1.1, 1.1), 'boot', inner=False)
    cel(B, ell(hand[0] - wux * 3.7, hand[1] - wuy * 3.7, 1.4, 1.4), 'gold', inner=False)
    stamp(B, LUVA, hand[0] - 2, hand[1] - 2)
    return B.render(), tip


def anim(kind='attack', view='right'):
    if kind == 'walk': poses = [walk_pose(f, 8) for f in range(8)]
    elif kind == 'idle': poses = [idle_pose(f, 8) for f in range(8)]
    else: poses = ATK
    n = len(poses)
    K.THIGH = K.SHIN = 5.6; K.TORSO = 10.4; K.GY = GY
    poses = [dict(p, hoff=8.0, px=30) for p in poses]
    js = [side_pose(p) for p in poses]
    base = [(j['chest'][0] - 2.0, j['chest'][1] + .6) for j in js]
    tails = spring_chain(base, 3.0, drag=(-.9 if kind == 'walk' else 0, 0))
    secb = [(j['head'][0] - 6.0, j['head'][1] - 1.0) for j in js]
    sec = spring_chain(secb, 3.4, drag=(-1.0 if kind == 'walk' else 0, .6), grav=2.6)
    res = []
    for f, j in enumerate(js):
        strike = kind == 'attack' and f in (5, 6, 7)
        img, tip = draw_side3(j, tail=tails[f], sec=sec[f][2], strike=strike)
        res.append((img, tip, j))
    return res


if __name__ == '__main__':
    sc = '/tmp/claude-0/-home-user-neon-wars/3ffd125f-a99a-599e-8554-f2b481e86fc1/scratchpad/'
    for r in HEAD_R: print(len(r), r)
    walk = anim('walk'); atk = anim('attack')
    items = [walk[0][0], walk[2][0], walk[4][0], atk[0][0], atk[3][0], atk[6][0]]
    S = Image.new('RGBA', (W * 6, HGT), (58, 110, 48, 255))
    for i, im in enumerate(items): S.alpha_composite(im, (i * W, 0))
    S.resize((S.width * 5, S.height * 5), Image.NEAREST).convert('RGB').save(sc + 'sk3_side.png')


# ================================================================ VISTAS FRONTAL / COSTAS
LEGV = 11.2
HIP = 2.5


def ik(a, b, l1, l2, out):
    """Cotovelo (2 ossos) escolhendo a solucao mais para fora (out=+1 direita, -1 esquerda) e para baixo."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    d = math.hypot(dx, dy) or 1e-6
    mx = l1 + l2 - .4
    if d > mx: k = mx / d; dx, dy = dx * k, dy * k; d = mx; b = (a[0] + dx, a[1] + dy)
    d = max(d, abs(l1 - l2) + .6)
    A = math.acos(max(-1, min(1, (l1 * l1 + d * d - l2 * l2) / (2 * l1 * d))))
    base = math.atan2(dy, dx)
    best = None
    for sg in (1, -1):
        ang = base + sg * A
        e = (a[0] + math.cos(ang) * l1, a[1] + math.sin(ang) * l1)
        score = e[0] * out * 1.0 + e[1] * .6
        if best is None or score > best[0]: best = (score, e)
    return best[1], b


def front_pose(p, sd=1):
    """p: dict com legs=[(spread,flex,depth,lift) esquerda, direita], hs=(out,down) mao da espada rel. ao ombro,
    ho=(out,down) mao livre, w=angulo da espada, wl=comprimento rel., dy (peito), tilt, crouch, headdy."""
    cx = p.get('cx', 32)
    lg = p['legs']
    ext = []
    for k, (s, fl, dpt, lift) in enumerate(lg):
        ext.append(LEGV * math.cos(math.radians(fl * .55)) - lift + dpt * .9)
    py = GY - 2.4 - max(ext) - p.get('crouch', 0)
    P = (cx + p.get('dx', 0), py)
    j = {'P': P, 'legs': []}
    for k, (s, fl, dpt, lift) in enumerate(lg):
        side = -1 if k == 0 else 1
        hip = (P[0] + side * HIP, P[1] + .5)
        legv = LEGV * math.cos(math.radians(fl * .55)) - lift + dpt * .9
        foot = (hip[0] + side * s, hip[1] + legv)
        knee = (hip[0] + side * (s * .4 + fl / 45.0), hip[1] + legv * .5)
        j['legs'].append((hip, knee, foot, dpt, lift))
    chest = (P[0] + p.get('lean', 0), P[1] - 9.8 + p.get('dy', 0))
    j['chest'] = chest
    tilt = p.get('tilt', 0)
    shS = (chest[0] + sd * 4.7, chest[1] + 1.6 - tilt)      # ombro da espada
    shO = (chest[0] - sd * 4.7, chest[1] + 1.6 + tilt)
    j['shS'], j['shO'] = shS, shO
    hs, ho = p['hs'], p['ho']
    hS = (shS[0] + sd * hs[0], shS[1] + hs[1]); hO = (shO[0] - sd * ho[0], shO[1] + ho[1])
    eS, hS = ik(shS, hS, 5.8, 5.4, sd); eO, hO = ik(shO, hO, 5.8, 5.4, -sd)
    j.update(eS=eS, hS=hS, eO=eO, hO=hO)
    j['head'] = (chest[0] + p.get('hdx', 0), chest[1] - 8.4 + p.get('headdy', 0))
    j['w'] = p['w']; j['wl'] = p.get('wl', 1.0); j['sd'] = sd
    return j


def draw_front3(j, back=False, strike=False, tailpts=None):
    B = B3()
    P = j['P']; ch = j['chest']; sd = j['sd']
    # pernas
    for k in (0, 1):
        hip, knee, foot, dpt, lift = j['legs'][k]
        cel(B, limb(hip, knee, 3.0, 2.7), 'pants')
        cel(B, limb(knee, (foot[0], foot[1] - 1.5), 2.7, 2.3), 'pants')
        stamp(B, BOTA_B if back else BOTA_F, foot[0] - 2.5, foot[1] - 3.5)
    # tronco
    sw = 4.9
    body = [(ch[0] - 3.2, ch[1] - .6), (ch[0] + 3.2, ch[1] - .6), (ch[0] + sw, ch[1] + 1.4), (ch[0] + sw - .4, ch[1] + 6),
            (P[0] + 4.8, P[1] + 1.2), (P[0] - 4.8, P[1] + 1.2), (ch[0] - sw + .4, ch[1] + 6), (ch[0] - sw, ch[1] + 1.4)]
    cel(B, pol(body), 'tunic', depth=2)
    by = P[1] - .8
    cel(B, pol([(P[0] - 4.8, by), (P[0] + 4.8, by), (P[0] + 4.8, by - 1.3), (P[0] - 4.8, by - 1.3)]), 'belt', inner=False)
    if not back:
        stamp(B, ['gG', 'gg'], P[0] - 1, by - 1.6)
        # dobras da tunica
        B.put(ch[0] - 1.5, ch[1] + 4, 'tunic', 1); B.put(ch[0] + 2.5, ch[1] + 5, 'tunic', 1)
    else:
        B.put(ch[0] - 1.5, ch[1] + 4, 'tunic', 1); B.put(ch[0] + 1.5, ch[1] + 3, 'tunic', 1)
    # cachecol
    cel(B, ell(ch[0], ch[1] + .2, 5.2, 2.0), 'scarf')
    if not back:
        sx = ch[0] + 1.5 * sd
        cel(B, pol([(sx - 1.6, ch[1] + 1.2), (sx + 1.6, ch[1] + 1.2), (sx + 1.9, ch[1] + 5.2), (sx - 1.0, ch[1] + 5.0)]), 'scarf', inner=False)
    else:
        tx = ch[0]
        cel(B, pol([(tx - 1.8, ch[1] + 1.0), (tx + 1.8, ch[1] + 1.0), (tx + 2.2, ch[1] + 7.5), (tx - 1.6, ch[1] + 7.0)]), 'scarf')
    # cabeca desenhada a mao
    hx, hy = j['head']
    rows = HEAD_B if back else list(HEAD_F)
    if strike and not back: rows = rows[:13] + ['..xhsSkk'] + rows[14:]
    stamp(B, rows, hx - 8 + .5, hy - 7.5 + .5, mirror=True, rsh=HEAD_F_RSH)
    if back:
        for k_, (cc, bd_) in enumerate([('hair', 3), ('hair', 2), ('hair', 1), ('hair', 0)]):
            B.put(hx - 1, hy + 7.5 + k_, cc, bd_); B.put(hx, hy + 7.5 + k_, cc, max(0, bd_ - 1))
        B.put(hx - 1, hy + 6.5, 'gold', 3); B.put(hx, hy + 6.5, 'gold', 2)
    # bracos (mangas + bracadeira + luva)
    for who in ('O', 'S'):
        sh = j['sh' + who]; el = j['e' + who]; ha = j['h' + who]
        cel(B, limb(sh, el, 2.5, 2.2), 'sleeve')
        cel(B, limb(el, ha, 2.1, 1.9), 'sleeve')
        hv = (ha[0] - el[0], ha[1] - el[1]); hl_ = math.hypot(*hv) or 1
        cel(B, limb((ha[0] - hv[0] / hl_ * 2.1, ha[1] - hv[1] / hl_ * 2.1), (ha[0] - hv[0] / hl_ * .9, ha[1] - hv[1] / hl_ * .9), 2.0, 2.0), 'glove', inner=False)
        if who == 'O':
            stamp(B, LUVA_F, ha[0] - 2, ha[1] - 2)
    # espada (peca separada) na mao S
    hand = j['hS']
    wx, wy = math.sin(math.radians(j['w'])) * sd, math.cos(math.radians(j['w']))
    L = 15 * j['wl']
    tip = (hand[0] + wx * L, hand[1] + wy * L)
    cel(B, limb((hand[0] + wx * 3, hand[1] + wy * 3), tip, 1.5, .35), 'steel')
    gx, gy = hand[0] + wx * 2.8, hand[1] + wy * 2.8
    cel(B, limb((gx - wy * 3.2, gy + wx * 3.2), (gx + wy * 3.2, gy - wx * 3.2), 1.0, 1.0), 'gold')
    cel(B, limb((hand[0] - wx * 3, hand[1] - wy * 3), (hand[0] + wx * 2, hand[1] + wy * 2), 1.1, 1.1), 'boot', inner=False)
    cel(B, ell(hand[0] - wx * 3.7, hand[1] - wy * 3.7, 1.4, 1.4), 'gold', inner=False)
    stamp(B, LUVA_F, hand[0] - 2, hand[1] - 2)
    return B.render(), tip


# ---- poses frente/costas
def walk_front(f, n=8, back=False):
    ph = 2 * math.pi * f / n
    legs = []
    for k, side in enumerate((-1, 1)):
        psi = ph + (0 if k == 0 else math.pi)
        fwd = math.cos(psi)
        lift = max(0, -math.sin(psi)) * 3.2
        legs.append((.3 + .4 * abs(fwd), 22 * max(0, -math.sin(psi)), fwd * 2.4 * (-1 if back else 1), lift))
    a = math.cos(ph)
    return dict(legs=legs, hs=(3.8, 7.6 - 1.6 * a), ho=(3.8, 7.6 + 1.6 * a), w=158, wl=.9, dy=0, crouch=-abs(math.sin(ph * 2)) * 0 + (1 if abs(math.sin(ph)) < .4 else 0) * -0.0,
                headdy=-.5 * abs(math.cos(ph)))


def idle_front(f, n=8):
    s = math.sin(2 * math.pi * f / n)
    return dict(legs=[(.8, 6, .4, 0), (.8, 6, -.2, 0)], hs=(4.2, 6.8 + .3 * s), ho=(4.0, 7.6 - .3 * s), w=152 + 2 * s, wl=1.0, dy=-.5 * s, headdy=.3 * s)


# (hs(out,down), ho, w, lean, dy, tilt, crouch, headdy, legs)
ATKF = [
    dict(hs=(4.5, 6.5), ho=(4, 8), w=150, dy=0, tilt=0, crouch=0, headdy=0, legs=[(1.2, 10, 1.0, 0), (1.0, 6, -1.0, 0)]),
    dict(hs=(6, 3), ho=(5, 5), w=165, dy=-.4, tilt=-.6, crouch=.4, headdy=-.4, legs=[(1.4, 12, .6, 0), (1.2, 8, -1.4, 0)]),
    dict(hs=(6.5, -3), ho=(7, 1), w=178, dy=-.8, tilt=-1.2, crouch=1.0, headdy=-.6, legs=[(1.6, 14, 0, 0), (1.6, 12, -1.8, 0)]),
    dict(hs=(4.5, -8.5), ho=(8, -1), w=196, dy=-1.0, tilt=-1.8, crouch=1.6, headdy=-1.0, legs=[(2.0, 16, -.4, 0), (2.0, 16, -2.2, 0)]),
    dict(hs=(3, -8), ho=(7, 1), w=214, dy=-.6, tilt=-1.2, crouch=1.2, headdy=-.4, legs=[(2.2, 18, .2, 0), (2.0, 14, -2.0, 0)]),
    dict(hs=(1, -2), ho=(4, 6), w=262, dy=.8, tilt=.6, crouch=1.6, headdy=.6, legs=[(3.0, 24, 1.6, 0), (2.2, 10, -2.4, 0)]),
    dict(hs=(-1.5, 9), ho=(2, 9), w=338, dy=2.0, tilt=1.6, crouch=2.6, headdy=1.6, legs=[(4.2, 34, 3.6, 0), (2.6, 6, -3.0, 0)]),
    dict(hs=(-3, 10), ho=(2, 9), w=326, dy=2.2, tilt=1.8, crouch=2.8, headdy=1.8, legs=[(4.2, 34, 3.6, 0), (2.6, 6, -3.0, 0)]),
    dict(hs=(1, 8), ho=(3, 8), w=352, dy=1.2, tilt=.8, crouch=1.8, headdy=1.0, legs=[(3.2, 22, 2.2, 0), (2.0, 8, -1.6, 0)]),
    dict(hs=(3.8, 7), ho=(4, 8), w=138, dy=.4, tilt=.2, crouch=.8, headdy=.3, legs=[(2.0, 12, 1.2, 0), (1.4, 8, -.8, 0)]),
]
ATKB = []
for q in ATKF:
    d = dict(q)
    d['hs'] = (q['hs'][0], q['hs'][1] if q['hs'][1] < 0 else q['hs'][1] * .35 - 1.0)   # golpe vai para longe da camera: mao sobe na tela
    d['w'] = 172 if 300 < q['w'] < 360 or q['w'] > 330 else q['w'] if q['w'] < 215 else 188
    d['wl'] = .6 if q['w'] > 240 else 1.0
    d['dy'] = -q['dy'] * .6; d['headdy'] = -q['headdy'] * .6
    d['legs'] = [(s, fl, -dp, lf) for (s, fl, dp, lf) in q['legs']]
    ATKB.append(d)


def anim_front(kind='attack', back=False):
    sd = 1 if back else -1       # costas: espada no lado direito da tela; frente: no esquerdo
    if kind == 'walk': poses = [walk_front(f, 8, back) for f in range(8)]
    elif kind == 'idle': poses = [idle_front(f, 8) for f in range(8)]
    else: poses = ATKB if back else ATKF
    res = []
    for f, p in enumerate(poses):
        p = dict(p)
        j = front_pose(p, sd)
        strike = kind == 'attack' and f in (5, 6, 7)
        img, tip = draw_front3(j, back=back, strike=strike)
        res.append((img, tip, j))
    return res


def sheet_all(path, zoom=4):
    rows = [anim('walk'), anim('attack')]
    cols = 10
    items = []
    names = []
    S = Image.new('RGBA', (W * 10, HGT * 6), (58, 110, 48, 255))
    y = 0
    for label, res in [('side_walk', anim('walk')), ('side_atk', anim('attack')), ('front_walk', anim_front('walk')), ('front_atk', anim_front('attack')),
                       ('back_walk', anim_front('walk', True)), ('back_atk', anim_front('attack', True))]:
        for i, r in enumerate(res): S.alpha_composite(r[0], (i * W, y))
        y += HGT
    S.resize((S.width * zoom, S.height * zoom), Image.NEAREST).convert('RGB').save(path)


if __name__ == '__main__':
    sheet_all('/tmp/claude-0/-home-user-neon-wars/3ffd125f-a99a-599e-8554-f2b481e86fc1/scratchpad/sk3_all.png', 3)
