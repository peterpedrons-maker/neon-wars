"""Animacoes por POSES-CHAVE com tempo assimetrico (antecipacao lenta, golpe de 1 quadro, impacto parado, recuperacao) + molas + clarao/tremor.
Regras: skill pixel-art-studio (animation.md): 'speed asymmetry IS the punch', hold nos contatos, tremor de 1px + clarao no impacto."""
import math
from soft import *
import anims as A
from anims import simulate, ez, cl, sn, cs
DEF = {'sx': 1, 'sy': 1}
def timeline(keys):
    """keys: [(tick, dict, ease)]; ease descreve o trecho que CHEGA nesta chave: 'smooth','in','out','lin','hold'"""
    keys = sorted(keys, key=lambda k: k[0])
    names = set()
    for _, d, _ in keys: names |= set(d)
    def at(f):
        out = {}
        for n in names:
            dflt = DEF.get(n, 0)
            pts = [(t, d.get(n, None), e) for t, d, e in keys]
            # valor em cada chave (herda o anterior)
            vals = []; cur = dflt
            for t, v, e in pts:
                cur = cur if v is None else v; vals.append((t, cur, e))
            if f <= vals[0][0]: out[n] = vals[0][1]; continue
            if f >= vals[-1][0]: out[n] = vals[-1][1]; continue
            for (t0, v0, _), (t1, v1, e1) in zip(vals, vals[1:]):
                if t0 <= f <= t1:
                    u = (f - t0) / (t1 - t0) if t1 > t0 else 1
                    if e1 == 'hold': u = 0 if f < t1 else 1
                    elif e1 == 'smooth': u = ez(u)
                    elif e1 == 'in': u = u * u
                    elif e1 == 'out': u = 1 - (1 - u) ** 2
                    out[n] = v0 + (v1 - v0) * u; break
        return out
    return at
def make(n, at, shadow_fn=None, kicks=None, dust_from=None):
    def kin(f):
        p = at(f); ang = p.get('ang', 0)
        lift = -30 * (min(1, abs(ang) / 1.55) ** 2)
        fx = shadow(p.get('shc', 0), p.get('shw', 22), .5)
        if dust_from is not None and dust_from <= f <= dust_from + 8: fx = both(fx, dust(-38, cl((f - dust_from) / 8)))
        k = {'root': (p.get('dx', 0), p.get('dy', 0) + lift, ang, None, p.get('sy', 1), p.get('sx', 1)), 'torso': p.get('tor', 0),
             'legL': (p.get('lL', 0), 1), 'legR': (p.get('lR', 0), 1), 'fx': fx}
        if p.get('flash', 0) > 0.01: k['flash'] = p['flash']
        if p.get('shx', 0) or p.get('shy', 0): k['shake'] = (int(round(p.get('shx', 0))), int(round(p.get('shy', 0))))
        return k
    def tgt(f, b):
        p = at(f); return p.get({'head': 'th', 'armFu': 'tfu', 'armFl': 'tfl', 'armBu': 'tbu', 'armBl': 'tbl', 'tailA': 'tta', 'tailB': 'ttb'}[b], 0)
    return simulate(n, kin, tgt, kicks)
def S(**k): return k
def idle(n=8):
    keys = []
    for i in range(n + 1):
        s = sn(2 * math.pi * i / n)
        keys.append((i, S(dy=-1.5 * s, tor=0.02 * s, sy=1 + .012 * s, tfu=.05 * sn(2 * math.pi * i / n - .8), tfl=.07 * sn(2 * math.pi * i / n - 1.4), th=.04 * sn(2 * math.pi * i / n - .6), tta=.14 * sn(2 * math.pi * i / n - 1.2), ttb=.22 * sn(2 * math.pi * i / n - 1.8)), 'lin'))
    return make(n, timeline(keys))
def walk(n=8):
    keys = []
    for i in range(n + 1):
        t = 2 * math.pi * i / n; s, c = sn(t), cs(t)
        keys.append((i, S(dy=1.5 * c * c * 0 + (-3.2 * abs(s) + 1.4), ang=0.03 * s, tor=0.07, lL=0.7 * s, lR=-0.7 * s, tfu=-.3 * s, tfl=-.25 * s, tbu=.5 * s, tbl=.35 * s, th=-.06 * s, tta=.25 * sn(t - .8), ttb=.35 * sn(t - 1.4)), 'lin'))
    return make(n, timeline(keys))
def attack(n=11):
    k = [(0, S(), 'lin'),
         (1, S(dx=-3, dy=3, ang=-.05, sy=.96, tor=-.12, tfu=.6, tfl=.8, tbu=-.3, th=-.08, tta=.2), 'smooth'),
         (3, S(dx=-8, dy=3, ang=-.14, sy=.95, sx=1.02, tor=-.32, lL=-.3, lR=.25, tfu=1.1, tfl=1.25, tbu=-.5, tbl=-.3, th=-.16, tta=.35, ttb=.5), 'smooth'),
         (4, S(dx=13, dy=-2, ang=.1, sy=.97, sx=1.06, tor=.22, lL=.5, lR=-.4, tfu=-.7, tfl=-.4, tbu=.5, tbl=.3, th=.06, tta=-.3, ttb=-.5), 'in'),
         (5, S(dx=14, dy=-1, shx=1), 'hold'), (6, S(shx=0), 'hold'),
         (8, S(dx=6, dy=0, ang=.08, sy=1, sx=1.02, tor=.15, lL=.2, lR=-.15, tfu=-.5, tfl=-.3, tbu=.2, th=.05, tta=-.1, ttb=-.2), 'smooth'),
         (10, S(dx=0, ang=0, sx=1, tor=0, lL=0, lR=0, tfu=0, tfl=0, tbu=0, tbl=0, th=0, tta=0, ttb=0), 'smooth')]
    return make(n, timeline(k), kicks={(4, 'armFu'): -5, (4, 'armFl'): -4, (4, 'tailB'): -6, (4, 'head'): 3})
def cast(n=12):
    k = [(0, S(), 'lin'), (4, S(dy=-2, ang=-.05, tor=-.12, tfu=.6, tfl=-.8, tbu=-.3, tbl=-.2, th=-.28, tta=.2, ttb=.3), 'smooth'),
         (6, S(flash=.3), 'hold'), (7, S(flash=0), 'hold'), (8, S(flash=.3), 'hold'), (9, S(flash=0), 'hold'),
         (11, S(dy=0, ang=0, tor=0, tfu=0, tfl=0, tbu=0, tbl=0, th=0, tta=0, ttb=0), 'smooth')]
    return make(n, timeline(k))
def hurt(n=7):
    k = [(0, S(), 'lin'), (1, S(dx=-6, dy=1, ang=-.14, tor=-.25, sy=.95, flash=.5, shx=-1, th=-.5, tfu=.6, tfl=.5, tbu=-.6, tbl=-.4, tta=.3, ttb=.5, lL=.15, lR=-.15), 'in'),
         (2, S(flash=0, shx=0), 'hold'), (3, S(), 'hold'), (6, S(dx=0, dy=0, ang=0, tor=0, sy=1, th=0, tfu=0, tfl=0, tbu=0, tbl=0, tta=0, ttb=0, lL=0, lR=0), 'smooth')]
    return make(n, timeline(k), kicks={(1, 'head'): -9, (1, 'armFu'): 7, (1, 'armBu'): -7, (1, 'tailB'): 8})
def death(n=22):
    k = [(0, S(), 'lin'),
         (1, S(dx=-5, dy=-2, ang=-.1, tor=-.25, flash=.5, shx=-1, th=-.5, tfu=.7, tfl=.9, tbu=-.7, tbl=-.6, tta=.3, ttb=.6), 'in'),
         (2, S(flash=0, shx=0), 'hold'),
         (5, S(dx=-10, dy=3, ang=-.3, tor=-.45, lL=.35, lR=-.3, th=-.45, tfu=.55, tfl=.6, tbu=-.55, tbl=-.4), 'smooth'),
         (7, S(dy=7, sy=.9, ang=-.3, tor=-.5, lL=.5, lR=-.4), 'smooth'), (8, S(), 'hold'),
         (12, S(dx=-32, dy=0, sy=1, ang=-1.57, tor=0, lL=.65, lR=-.55, th=-.2, tfu=0, tfl=.2, tbu=0, tbl=0, tta=.3, ttb=.6, shc=-46, shw=46), 'in'),
         (13, S(sy=.88, flash=.35, shy=1), 'hold'),
         (14, S(dy=-5, sy=1.02, flash=0, shy=0), 'hold'),
         (15, S(dy=0, sy=.93, shy=1), 'hold'),
         (16, S(shy=0), 'hold'),
         (21, S(sy=1, lL=.1, lR=-.08, th=.14, tfu=-.9, tfl=.5, tbu=.9, tbl=.4, tta=-.1, ttb=-.25), 'out')]
    return make(n, timeline(k), kicks={(1, 'head'): -9, (1, 'armFu'): 7, (1, 'armBu'): -7, (13, 'armFu'): -6, (13, 'armBu'): 6, (13, 'armFl'): -5, (13, 'armBl'): 5, (13, 'head'): 5, (13, 'tailB'): -8}, dust_from=13)
def build():
    return {'idle': idle(), 'walk': walk(), 'attack': attack(), 'cast': cast(), 'hurt': hurt(), 'death': death()}
if __name__ == '__main__':
    from PIL import Image
    an = build(); cols = 8
    rows = sum((len(v) + cols - 1) // cols for v in an.values())
    sh = Image.new('RGBA', (cols * CW * 2, rows * CH * 2), (36, 26, 46, 255)); y = 0
    for k, fr in an.items():
        for i, im in enumerate(fr): sh.alpha_composite(im.resize((CW * 2, CH * 2), Image.NEAREST), ((i % cols) * CW * 2, (y + i // cols) * CH * 2))
        y += (len(fr) + cols - 1) // cols
    sh.save('/tmp/claude-0/-home-user-neon-wars/3ffd125f-a99a-599e-8554-f2b481e86fc1/scratchpad/anims2.png'); print({k: len(v) for k, v in an.items()}, sh.size)
