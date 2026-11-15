#!/usr/bin/env python3
"""skel2d: esqueleto 2D para pixel art 16 bits. Juntas + FK, partes sombreadas volumetricamente (sem dither),
contorno seletivo, linha interna entre partes, arma como peca separada, caudas com mola (movimento secundario).
Vista lateral (right) com andar de 8 quadros e ataque de 10 poses; vistas frente/costas (down/up) com andar de 8 quadros."""
import math
from PIL import Image

LX, LY, LZ = -.5, -.65, .6
_n = math.sqrt(LX * LX + LY * LY + LZ * LZ)
LX, LY, LZ = LX / _n, LY / _n, LZ / _n

RAMPS = {
    'hair': ['#8a3428', '#c0502a', '#e8702c', '#ffb454'],
    'skin': ['#d88a82', '#e8a898', '#ffd0ae', '#ffe6cc'],
    'tunic': ['#8a3a2c', '#b84a2a', '#e8782e', '#ffb868'],
    'scarf': ['#223c8a', '#3a68c8', '#4a88ea', '#9ccaff'],
    'pants': ['#2e2240', '#4a3858', '#625078', '#7c6a96'],
    'boot': ['#2e1a1c', '#523024', '#6e4634', '#a07850'],
    'steel': ['#5a6a90', '#8a9cc0', '#c4d4ee', '#ffffff'],
    'gold': ['#a07828', '#d8a838', '#f4cc58', '#fff0a0'],
    'eye': ['#2a1a3a'] * 4, 'white': ['#c8d0ea', '#e8ecf8', '#ffffff', '#ffffff'], 'blush': ['#f08a8a'] * 4,
    'belt': ['#3e2018', '#5e3420', '#7a4a28', '#a07040'],
}
OUTL = {'hair': '#4a1a20', 'skin': '#7a3a40', 'tunic': '#5a2028', 'scarf': '#141c50', 'pants': '#1c1428', 'boot': '#1a0e10',
        'steel': '#242c4a', 'gold': '#4a3418', 'eye': '#2a1a3a', 'white': '#2a3452', 'blush': '#7a3a40', 'belt': '#1a0e10'}


RAMPS_G = dict(RAMPS)
RAMPS_G.update({
    'skin': ['#2e6a40', '#4a9a3c', '#7ac850', '#b4ee7a'],
    'tunic': ['#2e6a40', '#4a9a3c', '#7ac850', '#b4ee7a'],
    'pants': ['#2a5a38', '#3e8438', '#62ac48', '#8cd060'],
    'scarf': ['#6a4228', '#9a6a3c', '#c8924e', '#e8b878'],
    'boot': ['#2e1a1c', '#523024', '#6e4634', '#a07850'],
    'hair': ['#1a1a20', '#2a2a34', '#3a3a48', '#5a5a6c'],
    'wood': ['#4a2a1c', '#6e4228', '#9a6438', '#c8904e'],
    'white': ['#c8d0ea', '#e8ecf8', '#ffffff', '#ffffff'], 'eye': ['#ffe25a'] * 4,
})
OUTL_G = dict(OUTL); OUTL_G.update({'skin': '#1a3a24', 'tunic': '#1a3a24', 'pants': '#183a20', 'scarf': '#3a2214', 'wood': '#2a160e', 'eye': '#6a4a10'})
RAMPS['wood'] = ['#4a2a1c', '#6e4228', '#9a6438', '#c8904e']; OUTL['wood'] = '#2a160e'


def rgb(h):
    h = h.lstrip('#'); return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 255)


class Buf:
    def __init__(self, w, h, ramps=None, outl=None):
        self.w, self.h = w, h
        self.m = [[None] * w for _ in range(h)]
        self.b = [[0] * w for _ in range(h)]
        self.pid = [[0] * w for _ in range(h)]
        self.line = [[False] * w for _ in range(h)]
        self.n = 0
        self.ramps = ramps or RAMPS
        self.outl = outl or OUTL

    def fill(self, mask, mat, far=0, inner=True, band_fn=None, bbox=None):
        """mask(x,y)->l (luz -1..1) ou None. Pinta com bandas limpas (sem dither)."""
        self.n += 1
        x0, y0, x1, y1 = bbox or (0, 0, self.w, self.h)
        S = {}
        for y in range(max(0, int(y0)), min(self.h, int(y1) + 1)):
            for x in range(max(0, int(x0)), min(self.w, int(x1) + 1)):
                l = mask(x + .5, y + .5)
                if l is None: continue
                bd = 3 if l > .80 else 2 if l > .42 else 1 if l > .05 else 0
                if band_fn: bd = band_fn(x, y, bd)
                S[(x, y)] = max(0, bd - far)
        for (x, y), bd in S.items():
            under = self.m[y][x]
            self.m[y][x] = mat; self.b[y][x] = bd; self.pid[y][x] = self.n; self.line[y][x] = False
        if inner:
            for (x, y) in S:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    q = (x + dx, y + dy)
                    if q not in S and 0 <= q[0] < self.w and 0 <= q[1] < self.h:
                        o = self.pid[q[1]][q[0]]
                        if self.m[q[1]][q[0]] is not None and o != self.n:
                            self.line[y][x] = True
        return S

    def put(self, x, y, mat, band=2):
        x, y = int(x), int(y)
        if 0 <= x < self.w and 0 <= y < self.h:
            self.m[y][x] = mat; self.b[y][x] = band; self.line[y][x] = False; self.pid[y][x] = self.n

    def render(self):
        img = Image.new('RGBA', (self.w, self.h), (0, 0, 0, 0)); px = img.load()
        for y in range(self.h):
            for x in range(self.w):
                m = self.m[y][x]
                if m is None: continue
                px[x, y] = rgb(self.outl[m]) if self.line[y][x] else rgb(self.ramps[m][self.b[y][x]])
        # contorno seletivo externo
        for y in range(-1, self.h + 1):
            for x in range(-1, self.w + 1):
                if 0 <= x < self.w and 0 <= y < self.h and self.m[y][x] is not None: continue
                for dx, dy in ((0, 1), (1, 0), (-1, 0), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.w and 0 <= ny < self.h and self.m[ny][nx] is not None:
                        if 0 <= x < self.w and 0 <= y < self.h:
                            px[x, y] = rgb(self.outl[self.m[ny][nx]])
                        break
        return img


# ---------------------------------------------------------------- formas
def ellipse(cx, cy, rx, ry, cut=None):
    def f(x, y):
        nx, ny = (x - cx) / rx, (y - cy) / ry
        d = nx * nx + ny * ny
        if d > 1: return None
        if cut and cut(x, y): return None
        nz = math.sqrt(max(0, 1 - d))
        return nx * LX + ny * LY + nz * LZ
    return f, (cx - rx, cy - ry, cx + rx + 1, cy + ry + 1)


def capsule(p0, p1, r0, r1):
    x0, y0 = p0; x1, y1 = p1
    dx, dy = x1 - x0, y1 - y0
    L2 = dx * dx + dy * dy or 1e-6

    def f(x, y):
        t = max(0, min(1, ((x - x0) * dx + (y - y0) * dy) / L2))
        cx, cy = x0 + dx * t, y0 + dy * t
        r = r0 + (r1 - r0) * t
        ox, oy = x - cx, y - cy
        d2 = ox * ox + oy * oy
        if d2 > r * r: return None
        nz = math.sqrt(max(0, 1 - d2 / (r * r)))
        return (ox / r) * LX + (oy / r) * LY + nz * LZ
    m = max(r0, r1) + 1
    return f, (min(x0, x1) - m, min(y0, y1) - m, max(x0, x1) + m, max(y0, y1) + m)


def poly(pts, lval=.5):
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]

    def f(x, y):
        inside = False
        j = len(pts) - 1
        for i in range(len(pts)):
            xi, yi = pts[i]; xj, yj = pts[j]
            if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi + 1e-9) + xi: inside = not inside
            j = i
        return lval if inside else None
    return f, (min(xs) - 1, min(ys) - 1, max(xs) + 1, max(ys) + 1)


def v(a, deg, ln):
    """vetor a partir de angulo (0 = para baixo, + = para frente/direita)."""
    r = math.radians(deg)
    return (ln * math.sin(r), ln * math.cos(r))


def add(p, q): return (p[0] + q[0], p[1] + q[1])


# ---------------------------------------------------------------- esqueleto (vista lateral, olhando p/ direita)
SC = 0.86
THIGH, SHIN, TORSO, UARM, FARM = 6.6 * SC, 6.6 * SC, 9.6 * SC, 6.2 * SC, 5.8 * SC
GY = 42  # chao
W, HGT = 56, 48


def leg_pts(P, t, k, th=None, sn=None):
    knee = add(P, v(0, t, th or THIGH))
    ank = add(knee, v(0, t - k, sn or SHIN))
    return knee, ank


def side_pose(p, sc=None):
    """p: dict (angulos em graus; 0=baixo, +=frente). Retorna juntas."""
    k_ = (sc or SC) / SC
    THIGH_, SHIN_, TORSO_, UARM_, FARM_ = THIGH * k_, SHIN * k_, TORSO * k_, UARM * k_, FARM * k_
    lean = p.get('lean', 0)
    nl, fl = p['nl'], p['fl']
    # contato com o chao: o pe mais baixo toca GY
    ext = []
    for t, k in (nl, fl):
        knee, ank = leg_pts((0, 0), t, k, THIGH_, SHIN_)
        ext.append(ank[1] + 2.2 * SC)
    py = GY - max(ext) - p.get('crouch', 0)
    P = (p.get('px', 22) + p.get('dx', 0), py)
    j = {'P': P, 'lean': lean}
    for name, (t, k) in (('n', nl), ('f', fl)):
        knee, ank = leg_pts(P, t, k, THIGH_, SHIN_)
        j[name + 'knee'] = knee; j[name + 'ank'] = ank
    up = (math.sin(math.radians(lean)), -math.cos(math.radians(lean)))
    chest = (P[0] + up[0] * TORSO_, P[1] + up[1] * TORSO_)
    j['chest'] = chest
    sh = (P[0] + up[0] * TORSO_ * .86, P[1] + up[1] * TORSO_ * .86)
    j['sh'] = sh
    hl = lean * .35 + p.get('head', 0)
    ho = p.get('hoff', 5.4 * SC)
    j['head'] = (chest[0] + math.sin(math.radians(hl)) * ho + .4, chest[1] - math.cos(math.radians(hl)) * ho)
    for name, (a, fx) in (('n', p['na']), ('f', p['fa'])):
        el = add(sh, v(0, a, UARM_))
        ha = add(el, v(0, a + fx, FARM_))
        j[name + 'el'] = el; j[name + 'hand'] = ha; j[name + 'fore'] = a + fx
    j['w'] = p['w']
    return j


def draw_side(j, tail=None, sec=None, extra=None, who='hero'):
    """Desenha o heroi de lado. j = juntas. tail: (lista de pontos do lenco), sec: ponta do rabo de cavalo."""
    B = Buf(W, HGT, ramps=RAMPS_G if who == 'goblin' else None, outl=OUTL_G if who == 'goblin' else None)
    P = j['P']
    # braco de tras (longe)
    sh = j['sh']
    B.fill(*capsule(sh, j['fel'], 2.2 * SC + .6, 1.9 * SC + .5), 'tunic', far=1) if False else None
    f, bb = capsule(add(sh, (-.6, .6)), j['fel'], 2.1, 1.8); B.fill(f, 'tunic', far=1, bbox=bb)
    f, bb = capsule(j['fel'], j['fhand'], 1.8, 1.5); B.fill(f, 'skin', far=1, bbox=bb)
    # perna de tras
    for name, far in (('f', 1), ('n', 0)):
        knee, ank = j[name + 'knee'], j[name + 'ank']
        if name == 'n':
            # tronco entre as pernas
            f, bb = capsule(P, j['chest'], 4.4, 4.6)
            B.fill(f, 'tunic', bbox=bb)
            # aba da tunica
            ux, uy = math.sin(math.radians(j['lean'])), -math.cos(math.radians(j['lean']))
            hem = [(P[0] - 3.8, P[1] - 1.5), (P[0] + 3.8, P[1] - 1.5), (P[0] + 4.6, P[1] + 2.4), (P[0] - 4.6, P[1] + 2.4)]
            f, bb = poly(hem, .30); B.fill(f, 'scarf' if who == 'goblin' else 'tunic', inner=False, bbox=bb)
            f, bb = poly([(P[0] - 4.2, P[1] - 1.8), (P[0] + 4.2, P[1] - 1.8), (P[0] + 4.2, P[1] + .2), (P[0] - 4.2, P[1] + .2)], .6)
            B.fill(f, 'belt', inner=False, bbox=bb)
            B.put(P[0] + 3, P[1] - .6, 'gold', 3); B.put(P[0] + 2, P[1] - .6, 'gold', 2)
        f, bb = capsule(P, knee, 3.0 * SC + .6, 2.5 * SC + .5); B.fill(f, 'pants', far=far, bbox=bb)
        f, bb = capsule(knee, ank, 2.5 * SC + .5, 2.0 * SC + .5); B.fill(f, 'pants', far=far, bbox=bb)
        # bota (pe aponta para frente)
        f, bb = ellipse(ank[0] + 1.6, ank[1] + .9, 3.0, 1.7); B.fill(f, 'boot', far=far, bbox=bb)
        f, bb = capsule((ank[0] - .3, ank[1] - 1.9), (ank[0] - .1, ank[1] + .4), 2.1, 2.1); B.fill(f, 'boot', far=far, inner=False, bbox=bb)
        if name == 'f':
            pass
    # torso por cima das pernas de tras ja desenhado; lenco no pescoco
    ch = j['chest']
    f, bb = ellipse(ch[0] + .6, ch[1] + .6, 4.0, 2.0); B.fill(f, 'scarf', bbox=bb)
    # cauda do lenco (segue a mola)
    if tail:
        for i in range(len(tail) - 1):
            f, bb = capsule(tail[i], tail[i + 1], 1.7 - i * .35, 1.4 - i * .35); B.fill(f, 'scarf', inner=False, bbox=bb)
    # rabo de cavalo
    hd = j['head']
    if sec:
        f, bb = capsule((hd[0] - 4.2, hd[1] - .5), sec, 2.2, 1.0); B.fill(f, 'hair', bbox=bb)
    hx, hy = hd
    if who == 'goblin':
        # orelha pontuda para tras + cabeca grande, nariz grande, olho amarelo, presa
        f, bb = poly([(hx - 3.5, hy - 2.5), (hx - 11.5, hy - 6.5), (hx - 4.5, hy + 1.8)], .55); B.fill(f, 'skin', bbox=bb)
        f, bb = ellipse(hx, hy, 7.3, 6.4); B.fill(f, 'skin', bbox=bb)
        f, bb = ellipse(hx + 6.6, hy + 1.6, 2.6, 1.9); B.fill(f, 'skin', bbox=bb)
        B.put(hx + 3.0, hy - .6, 'eye', 0); B.put(hx + 4.0, hy - .6, 'eye', 1); B.put(hx + 3.5, hy + .4, 'white', 1)
        for dx in (2.0, 3.0, 4.0, 5.0): B.put(hx + dx, hy - 2.0 + (dx - 2) * .15, 'skin', 0)
        B.put(hx + 4.4, hy + 3.6, 'white', 3); B.put(hx + 3.4, hy + 3.6, 'tunic', 0); B.put(hx + 2.4, hy + 3.6, 'tunic', 0)
        B.put(hx - .6, hy + .4, 'skin', 0)
    else:
        f, bb = ellipse(hd[0], hd[1], 6.9, 6.6)
        B.fill(f, 'skin', bbox=bb)
        def hair_mask(x, y):
            nx, ny = (x - (hx - 1.0)) / 7.3, (y - (hy - 1.4)) / 7.0
            d = nx * nx + ny * ny
            if d > 1: return None
            if x > hx + 0.4 and y > hy - 2.2: return None      # rosto
            if x > hx - 1.8 and y > hy + 1.6: return None
            nz = math.sqrt(max(0, 1 - d))
            return nx * LX + ny * LY + nz * LZ
        B.fill(hair_mask, 'hair', bbox=(hx - 8, hy - 8, hx + 8, hy + 6), inner=False)
        for i, (dx, dy) in enumerate([(1.8, -1.2), (2.8, -.6), (3.8, -.2)]):
            B.put(hx + dx, hy + dy, 'hair', 2 if i else 3)
        B.put(hx + 3.2, hy + .2, 'eye', 0); B.put(hx + 3.2, hy + 1.2, 'eye', 0)
        B.put(hx + 2.2, hy + .2, 'white', 2)
        B.put(hx + 2.6, hy - 1.2, 'hair', 0); B.put(hx + 3.6, hy - 1.2, 'hair', 0)
        B.put(hx + 5.0, hy + 1.2, 'skin', 3)
        B.put(hx + 2.2, hy + 2.4, 'blush', 2)
        B.put(hx - .8, hy + 1.0, 'skin', 0); B.put(hx - .8, hy + 2.0, 'skin', 1)
    # braco da frente (com espada)
    f, bb = capsule(add(sh, (.4, 0)), j['nel'], 2.2, 1.9); B.fill(f, 'tunic', bbox=bb)
    f, bb = capsule(j['nel'], j['nhand'], 1.9, 1.6); B.fill(f, 'skin', bbox=bb)
    # ---- arma: peca separada
    hand = j['nhand']
    ux, uy = math.sin(math.radians(j['w'])), math.cos(math.radians(j['w']))
    if who == 'goblin':
        tip = (hand[0] + ux * 11, hand[1] + uy * 11)
        f, bb = capsule((hand[0] - ux * 2, hand[1] - uy * 2), tip, 1.1, 2.7); B.fill(f, 'wood', bbox=bb)
        for k in (-1, 0, 1):
            B.put(tip[0] + k * 1.6 + ux * 1.2, tip[1] + uy * 1.2 - 2.2 * (1 if abs(uy) > abs(ux) else 0) * 0, 'steel', 3)
        f, bb = ellipse(hand[0], hand[1], 1.9, 1.9); B.fill(f, 'skin', bbox=bb)
    else:
        tip = (hand[0] + ux * 15, hand[1] + uy * 15)
        f, bb = capsule((hand[0] + ux * 3, hand[1] + uy * 3), tip, 1.35, .5); B.fill(f, 'steel', bbox=bb)
        gx, gy = hand[0] + ux * 2.6, hand[1] + uy * 2.6
        f, bb = capsule((gx - uy * 3.0, gy + ux * 3.0), (gx + uy * 3.0, gy - ux * 3.0), 1.0, 1.0); B.fill(f, 'gold', bbox=bb)
        f, bb = capsule((hand[0] - ux * 3, hand[1] - uy * 3), (hand[0] + ux * 2, hand[1] + uy * 2), 1.1, 1.1); B.fill(f, 'boot', bbox=bb)
        f, bb = ellipse(hand[0] - ux * 3.6, hand[1] - uy * 3.6, 1.4, 1.4); B.fill(f, 'gold', bbox=bb)
        f, bb = ellipse(hand[0], hand[1], 1.9, 1.9); B.fill(f, 'skin', bbox=bb)
    img = B.render()
    return img, tip


# ---------------------------------------------------------------- animacoes laterais
def walk_pose(f, n=8, A=34, speed_dir=1):
    ph = 2 * math.pi * f / n
    def leg(psi):
        t = A * math.cos(psi)
        sp = math.sin(psi)
        if sp > 0:   # fase de apoio (pe no chao, vai para tras)
            k = 8 * sp
        else:        # balanco (levanta e passa)
            k = 62 * (-sp)
        return (t, k)
    nl = leg(ph); fl = leg(ph + math.pi)
    na = -26 * math.cos(ph); fa = 26 * math.cos(ph)
    return dict(lean=4, nl=nl, fl=fl, na=(na + 8, 28 + max(0, -na) * .6), fa=(fa + 4, 28 + max(0, -fa) * .6),
                w=118 + na * 1.2, head=0, crouch=0)


def idle_pose(f, n=8):
    s = math.sin(2 * math.pi * f / n)
    return dict(lean=3 + s * .8, nl=(10, 8), fl=(-10, 6), na=(26 + s * 2, 48), fa=(-18 - s, 26), w=110 + s * 4, head=0, crouch=.3 + .3 * s)


# (lean, dx, nl, fl, nA(a,flex), fA, w)
ATK = [
    dict(lean=3, dx=0, nl=(16, 18), fl=(-16, 10), na=(30, 60), fa=(-25, 30), w=118, head=0, crouch=0),      # 0 pronto
    dict(lean=-4, dx=-1, nl=(12, 24), fl=(-20, 14), na=(100, 50), fa=(20, 30), w=170, head=-2, crouch=.5),   # 1 antecipacao
    dict(lean=-11, dx=-2.5, nl=(8, 30), fl=(-26, 20), na=(176, 30), fa=(55, 20), w=228, head=-3, crouch=1.2),  # 2 sobe a espada
    dict(lean=-16, dx=-3.5, nl=(6, 34), fl=(-30, 26), na=(198, 22), fa=(72, 15), w=250, head=-4, crouch=1.8),  # 3 pico (preparo)
    dict(lean=-8, dx=-1.5, nl=(14, 30), fl=(-28, 22), na=(186, 20), fa=(50, 20), w=215, head=-2, crouch=1.2),  # 4 inicio do golpe
    dict(lean=8, dx=2, nl=(26, 38), fl=(-30, 10), na=(104, 10), fa=(12, 25), w=120, head=2, crouch=1.4),      # 5 desce rapido
    dict(lean=20, dx=6, nl=(40, 55), fl=(-38, 4), na=(78, 5), fa=(-52, 35), w=72, head=5, crouch=2.4),        # 6 impacto
    dict(lean=22, dx=7, nl=(40, 55), fl=(-38, 4), na=(62, 5), fa=(-60, 40), w=46, head=6, crouch=2.6),        # 7 continuacao
    dict(lean=12, dx=4, nl=(30, 40), fl=(-30, 8), na=(46, 25), fa=(-40, 40), w=64, head=3, crouch=1.6),       # 8 recupera
    dict(lean=5, dx=1, nl=(20, 26), fl=(-20, 10), na=(34, 45), fa=(-28, 32), w=98, head=1, crouch=.6),        # 9 volta
]


def spring_chain(base_pts_per_frame, seg, damp=.78, k=.32, drag=(0, 0), loops=4, grav=.8):
    """base_pts_per_frame: lista (por quadro) da ancora. Retorna lista (por quadro) de cadeias com atraso."""
    n = len(base_pts_per_frame)
    pts = [(base_pts_per_frame[0][0] - seg * (i + 1), base_pts_per_frame[0][1]) for i in range(2)]
    prev = list(pts)
    out = []
    for lp in range(loops):
        out = []
        for f in range(n):
            a = base_pts_per_frame[f]
            chain = [a]
            for i in range(2):
                p = pts[i]; q = prev[i]
                anchor = chain[-1]
                vel = ((p[0] - q[0]) * damp, (p[1] - q[1]) * damp)
                tx, ty = anchor[0] - seg * .6 + drag[0], anchor[1] + grav + drag[1]
                np_ = (p[0] + vel[0] + (tx - p[0]) * k, p[1] + vel[1] + (ty - p[1]) * k)
                # mantem comprimento
                dx, dy = np_[0] - anchor[0], np_[1] - anchor[1]
                L = math.hypot(dx, dy) or 1
                np_ = (anchor[0] + dx / L * seg, anchor[1] + dy / L * seg)
                prev[i] = p; pts[i] = np_
                chain.append(np_)
            out.append(chain)
    return out


GOB_SC = .8


def gob_walk(f, n=8):
    p = walk_pose(f, n, A=26)
    p['lean'] = 13; p['crouch'] = 1.2; p['head'] = 6
    p['na'] = (p['na'][0] + 10, 40); p['fa'] = (p['fa'][0] + 6, 40); p['w'] = 100 + (p['na'][0] - 20) * .8
    return p


def gob_idle(f, n=8):
    s_ = math.sin(2 * math.pi * f / n)
    return dict(lean=11 + s_ * 1.2, nl=(10, 14), fl=(-8, 12), na=(30 + s_ * 3, 40), fa=(-10 - s_ * 2, 30), w=120 + s_ * 6, head=5, crouch=1.4 + .4 * s_)


GOB_HURT = [
    dict(lean=-8, dx=-1, nl=(8, 20), fl=(-14, 14), na=(60, 50), fa=(30, 40), w=140, head=-6, crouch=.6),
    dict(lean=-18, dx=-3, nl=(4, 26), fl=(-22, 20), na=(90, 40), fa=(60, 30), w=170, head=-12, crouch=1.2),
    dict(lean=-22, dx=-5, nl=(2, 30), fl=(-26, 22), na=(110, 30), fa=(80, 25), w=190, head=-14, crouch=1.6),
    dict(lean=-14, dx=-4, nl=(6, 26), fl=(-20, 18), na=(80, 36), fa=(50, 30), w=150, head=-8, crouch=1.2),
    dict(lean=-4, dx=-2, nl=(8, 22), fl=(-14, 14), na=(50, 44), fa=(20, 36), w=128, head=-2, crouch=.8),
    dict(lean=6, dx=0, nl=(10, 16), fl=(-10, 12), na=(34, 42), fa=(-6, 32), w=122, head=3, crouch=1.2),
]
GOB_DEATH = [
    dict(lean=-22, dx=-5, nl=(2, 30), fl=(-26, 22), na=(110, 30), fa=(80, 25), w=190, head=-14, crouch=1.6),
    dict(lean=-34, dx=-8, nl=(0, 44), fl=(-30, 34), na=(120, 20), fa=(100, 20), w=200, head=-20, crouch=4),
    dict(lean=-52, dx=-11, nl=(-6, 70), fl=(-34, 60), na=(130, 20), fa=(110, 20), w=210, head=-28, crouch=7),
    dict(lean=-72, dx=-13, nl=(-10, 86), fl=(-40, 80), na=(140, 10), fa=(120, 10), w=220, head=-36, crouch=10),
]


def anim_side(kind='walk', n=None, who='hero'):
    """Devolve lista de (img, tip). kind: walk | idle | attack."""
    g = who == 'goblin'
    if kind == 'walk':
        n = n or 8; poses = [(gob_walk if g else walk_pose)(f, n) for f in range(n)]
    elif kind == 'idle':
        n = n or 8; poses = [(gob_idle if g else idle_pose)(f, n) for f in range(n)]
    elif kind == 'hurt':
        poses = GOB_HURT; n = len(poses)
    elif kind == 'death':
        poses = GOB_DEATH; n = len(poses)
    else:
        poses = ATK; n = len(poses)
    js = [side_pose(p, GOB_SC if g else None) for p in poses]
    base = [(j['chest'][0] - 2.0, j['chest'][1] + .6) for j in js]
    tails = spring_chain(base, 3.0, drag=(-.9 if kind == 'walk' else 0, 0))
    secb = [(j['head'][0] - 4.0, j['head'][1] + .2) for j in js]
    sec = spring_chain(secb, 3.2, drag=(-1.0 if kind == 'walk' else 0, .6))
    res = []
    for f, j in enumerate(js):
        img, tip = draw_side(j, tail=tails[f] if not g else None, sec=sec[f][2] if not g else None, who=who)
        res.append((img, tip, j))
    return res


if __name__ == '__main__':
    import sys
    sc = '/tmp/claude-0/-home-user-neon-wars/3ffd125f-a99a-599e-8554-f2b481e86fc1/scratchpad/'
    walk = anim_side('walk'); atk = anim_side('attack')
    items = [r[0] for r in walk] + [r[0] for r in atk]
    cw, ch = 48, 48
    cols = 8
    rows = (len(items) + cols - 1) // cols
    S = Image.new('RGBA', (cw * cols, ch * rows), (58, 110, 48, 255))
    for i, im in enumerate(items): S.alpha_composite(im, ((i % cols) * cw, (i // cols) * ch))
    S.resize((S.width * 4, S.height * 4), Image.NEAREST).convert('RGB').save(sc + 'skel_v1.png')
    print('ok')
