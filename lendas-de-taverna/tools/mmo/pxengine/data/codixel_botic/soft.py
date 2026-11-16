"""Deformacao macia (linear blend skinning) a partir de UMA pose parada + fisica simples (molas) para membros/cauda/cabeca.
Fonte: ref_idle.png (so a pose parada). Saida: quadros pixelados (paleta fixa) alinhados pelos pes."""
import math, numpy as np
from PIL import Image
from scipy import ndimage as ndi
HERE = __import__('os').path.dirname(__import__('os').path.abspath(__file__))
SRC = Image.open(HERE + '/ref_idle.png').convert('RGBA')
bb = SRC.getbbox(); SRC = SRC.crop(bb); SW, SH = SRC.size            # 149x153
FINAL_H = 64; S = FINAL_H / SH; SS = 4                                 # SS = supersample por pixel final
W, H, OX, OY = 390, 230, 150, 25                                       # canvas em coordenadas-fonte (1 px fonte = 1 unidade)
CW, CH = int(W * S), int(H * S)
# ---- cor: saturacao 1.3 e paleta fixa de 32 cores
a = np.array(SRC).astype(float); m = a[..., 3] > 128
g = a[..., :3].mean(2, keepdims=True); a[..., :3] = np.clip(g + (a[..., :3] - g) * 1.3, 0, 255)
SRCA = a.astype(np.uint8); OPAQUE = m
q = Image.fromarray(SRCA[..., :3]).quantize(32, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
PAL = np.array(q.getpalette()[:96]).reshape(-1, 3)[:32]
IDX = np.array(q).astype(np.int32); IDX[~OPAQUE] = -1
# ---- ossos
BONES = ['body', 'torso', 'head', 'armFu', 'armFl', 'armBu', 'armBl', 'legL', 'legR', 'tailA', 'tailB']
PARENT = {'body': None, 'torso': 'body', 'head': 'torso', 'armFu': 'torso', 'armFl': 'armFu', 'armBu': 'torso', 'armBl': 'armBu', 'legL': 'body', 'legR': 'body', 'tailA': 'body', 'tailB': 'tailA'}
JOINT = {'body': (80, 125), 'torso': (80, 112), 'head': (85, 48), 'armFu': (50, 64), 'armFl': (33, 80), 'armBu': (113, 70), 'armBl': (125, 96), 'legL': (58, 130), 'legR': (95, 132), 'tailA': (45, 138), 'tailB': (15, 128)}
Z = {'body': 0, 'torso': 0, 'head': 3, 'armFu': 1, 'armFl': 2, 'armBu': 1, 'armBl': 2, 'legL': -1, 'legR': -1, 'tailA': -2, 'tailB': -2}
POLY = {  # ordem de pintura (o ultimo vence)
 'torso': [(27, 46), (118, 46), (118, 112), (27, 112), (27, 84)],
 'body': [(27, 92), (66, 92), (66, 112), (118, 112), (118, 140), (86, 140), (70, 136), (44, 136), (27, 128)],
 'head': [(60, 0), (149, 0), (149, 52), (100, 52), (80, 48), (60, 40)],
 'armFu': [(40, 58), (58, 58), (58, 86), (40, 86)],
 'armFl': [(8, 15), (42, 15), (42, 58), (40, 86), (26, 86), (8, 62)],
 'armBu': [(112, 68), (132, 68), (132, 98), (112, 98)],
 'armBl': [(118, 92), (149, 92), (149, 126), (118, 126)],
 'legL': [(42, 134), (70, 134), (70, 153), (42, 153)],
 'legR': [(86, 138), (130, 138), (130, 153), (86, 153)],
 'tailA': [(16, 118), (26, 128), (40, 136), (48, 148), (8, 148), (16, 132)],
 'tailB': [(0, 76), (24, 76), (26, 100), (20, 116), (16, 118), (16, 132), (8, 148), (0, 120)]}
from PIL import ImageDraw
lab = Image.new('L', (SW, SH), 255); d = ImageDraw.Draw(lab)
for i, b in enumerate(BONES):
    if b in POLY: d.polygon(POLY[b], fill=i)
lab = np.array(lab).astype(np.int32)
lab[lab == 255] = 1                                                     # resto = torso
SIG = 3.2
Wt = np.stack([ndi.gaussian_filter((lab == i).astype(float), SIG) for i in range(len(BONES))], 0)
Wt = Wt / np.maximum(Wt.sum(0, keepdims=True), 1e-6)
# amostras (fonte 2x para nao abrir buracos)
UP = 2
ys, xs = np.nonzero(np.kron(OPAQUE, np.ones((UP, UP), bool)))
PX = (xs + .5) / UP; PY = (ys + .5) / UP
SIX = np.minimum((PX).astype(int), SW - 1); SIY = np.minimum((PY).astype(int), SH - 1)
PIDX = IDX[SIY, SIX]; PWT = Wt[:, SIY, SIX]                           # (B,N)
ZORD = np.array([Z[BONES[i]] for i in PWT.argmax(0)])
ORDER = np.argsort(ZORD, kind='stable')
# ---- matrizes
def T(x, y): return np.array([[1, 0, x], [0, 1, y], [0, 0, 1.]])
def R(a): c, s = math.cos(a), math.sin(a); return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1.]])
def Sc(sx, sy): return np.array([[sx, 0, 0], [0, sy, 0], [0, 0, 1.]])
def about(j, M): return T(*j) @ M @ T(-j[0], -j[1])
FEET = (82, 151)
def fk(pose):
    """pose: {'root':(dx,dy,ang,pivot|None,sy), bone:(ang[, sy])}"""
    rt = tuple(pose.get('root', (0, 0, 0, None, 1))); dx, dy, ang, piv, sy = rt[:5]; sx = rt[5] if len(rt) > 5 else 1
    piv = piv or FEET
    Wd = {}
    Wd['body'] = T(dx, dy) @ about(piv, R(ang)) @ about(JOINT['body'], Sc(sx, sy))
    for b in BONES[1:]:
        v = pose.get(b, 0); a_, s_ = (v if isinstance(v, tuple) else (v, 1))
        Wd[b] = Wd[PARENT[b]] @ about(JOINT[b], R(a_) @ Sc(1, s_))
    return Wd
def render(pose, fx=None, flash=0., shake=(0, 0)):
    Wd = fk(pose)
    P = np.stack([PX, PY, np.ones_like(PX)], 0)
    out = np.zeros((3, PX.size))
    for i, b in enumerate(BONES):
        out += PWT[i] * (Wd[b] @ P)
    X = (out[0] + OX) * S * SS; Y = (out[1] + OY) * S * SS
    GW, GH = CW * SS, CH * SS
    grid = np.full((GH, GW), -1, np.int32)
    xi = np.round(X).astype(int); yi = np.round(Y).astype(int)
    ok = (xi >= 0) & (xi < GW) & (yi >= 0) & (yi < GH)
    o = ORDER[ok[ORDER]]
    grid[yi[o], xi[o]] = PIDX[o]
    # fecha buracos pequenos
    for _ in range(2):
        empty = grid < 0
        if not empty.any(): break
        filled = np.maximum.reduce([np.roll(grid, s, ax) for s in (1, -1) for ax in (0, 1)])
        grid = np.where(empty & (filled >= 0), filled, grid)
    # efeitos por codigo (sombra/poeira) entram como ids extras na grade
    if fx: fx(grid)
    # moda por bloco
    g4 = grid.reshape(CH, SS, CW, SS).transpose(0, 2, 1, 3).reshape(CH, CW, SS * SS)
    opaque = (g4 >= 0).sum(2)
    cnt = np.stack([(g4 == k).sum(2) for k in range(len(PAL) + 3)], 2)
    best = cnt.argmax(2)
    res = np.zeros((CH, CW, 4), np.uint8)
    pal_ext = np.vstack([PAL, [[36, 26, 46], [184, 168, 144], [90, 70, 100]]])
    solid = opaque >= 7
    res[solid, :3] = pal_ext[best[solid]]; res[solid, 3] = 255
    # pixels soltos (ruido do skinning): remove os que nao tem vizinho
    sol = res[..., 3] > 0; nb = sum(np.roll(np.roll(sol, i, 0), j, 1).astype(int) for i in (-1, 0, 1) for j in (-1, 0, 1) if (i or j))
    res[sol & (nb == 0), 3] = 0
    if flash > 0:                                    # clarao de impacto (1 quadro)
        m_ = res[..., 3] > 0; res[m_, :3] = (res[m_, :3] + (255 - res[m_, :3]) * flash).astype(np.uint8)
    if shake != (0, 0): res = np.roll(res, (shake[1], shake[0]), (0, 1))
    return Image.fromarray(res)
EXTRA_SHADOW, EXTRA_DUST = len(PAL), len(PAL) + 1
def shadow(cx, w, al=0.5):
    def f(grid):
        gx = int((FEET[0] + OX + cx) * S * SS); gy = int((FEET[1] + OY + 2) * S * SS)
        h = int(6 * S * SS); ww = int(w * S * SS)
        yy, xx = np.mgrid[-h:h + 1, -ww:ww + 1]
        m = (xx / max(ww, 1)) ** 2 + (yy / max(h, 1)) ** 2 <= 1
        for (yo, xo) in zip(*np.nonzero(m)):
            y_, x_ = gy + yo - h, gx + xo - ww
            if 0 <= y_ < grid.shape[0] and 0 <= x_ < grid.shape[1] and grid[y_, x_] < 0 and ((x_ // 2 + y_ // 2) % 2 == 0 or al > .7): grid[y_, x_] = EXTRA_SHADOW
    return f
def dust(cx, t, n=7):
    def f(grid):
        gy0 = (FEET[1] + OY - 1) * S * SS
        for i in range(n):
            ang = math.pi * (0.12 + 0.76 * i / (n - 1)); dd = (8 + t * 36) * S * SS
            x = (FEET[0] + OX + cx) * S * SS + math.cos(ang) * dd * (1 if i % 2 else -1) * (1 + .06 * i)
            y = gy0 - math.sin(ang) * dd * .5; r = (2.5 + t * 6) * S * SS
            yy, xx = np.mgrid[int(y - r):int(y + r) + 1, int(x - r):int(x + r) + 1]
            for y_, x_ in zip(yy.ravel(), xx.ravel()):
                if (y_ - y) ** 2 + (x_ - x) ** 2 <= r * r and ((x_ // 2 + y_ // 2 + i) % 2 == 0 or t < .3) and 0 <= y_ < grid.shape[0] and 0 <= x_ < grid.shape[1] and grid[y_, x_] < 0: grid[y_, x_] = EXTRA_DUST
    return f
def both(*fs):
    def f(g):
        for h in fs:
            if h: h(g)
    return f
# ---- molas: segue o pai com atraso (acao sobreposta) e cai com a gravidade
class Spring:
    def __init__(s, k=60., c=7.): s.a = 0.; s.v = 0.; s.k = k; s.c = c
    def step(s, target, dt, kick=0.): s.v += kick; s.v += (-s.k * (s.a - target) - s.c * s.v) * dt; s.a += s.v * dt; return s.a
