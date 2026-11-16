import math, numpy as np
from soft import *
ez = lambda t: t * t * (3 - 2 * t)
cl = lambda v, a=0., b=1.: max(a, min(b, v))
sn, cs = math.sin, math.cos
DYN = {  # osso: (pai, mola k, amortecimento c, seguir_pai mu)
 'head': ('torso', 70, 7.5, .55), 'armFu': ('torso', 55, 6.5, .65), 'armFl': ('armFu', 60, 6, .5),
 'armBu': ('torso', 55, 6.5, .65), 'armBl': ('armBu', 60, 6, .5), 'tailA': ('body', 45, 5.5, .3), 'tailB': ('tailA', 50, 5, .3)}
def simulate(n, kin, tgt, kicks=None, fps=14, sub=8):
    """kin(f)->dict(root=(dx,dy,ang,pivot,sy), torso=a, legL=a, legR=a, fx=callable)  tgt(f,bone)->deslocamento-alvo (rad)  kicks: {(f,bone):vel}"""
    sp = {b: Spring(DYN[b][1], DYN[b][2]) for b in DYN}
    frames = []; dt = 1. / fps / sub
    for f in range(n):
        k = kin(f)
        for s_ in range(sub):
            ang = {}                                     # angulo local de cada osso na iteracao
            root_a = k['root'][2]; ang['body'] = root_a; ang['torso'] = k.get('torso', 0)
            world = {'body': root_a, 'torso': root_a + ang['torso']}
            for b in ('head', 'armFu', 'armFl', 'armBu', 'armBl', 'tailA', 'tailB'):
                par, kk, cc, mu = DYN[b]
                thp = world[par]
                t_local = tgt(f, b) - mu * thp
                kick = (kicks or {}).get((f, b), 0) if s_ == 0 else 0
                a = sp[b].step(t_local, dt, kick)
                world[b] = thp + a
        pose = {'root': k['root'], 'torso': k.get('torso', 0), 'legL': k.get('legL', 0), 'legR': k.get('legR', 0)}
        for b in DYN: pose[b] = sp[b].a
        if 'sq' in k: pose['torso'] = (k.get('torso', 0), k['sq'])
        frames.append(render(pose, k.get('fx'), k.get('flash', 0.), k.get('shake', (0, 0))))
    return frames
def zero(f, b): return 0.
def idle(n=16):
    def kin(f):
        t = f / n; s = sn(2 * math.pi * t)
        return {'root': (0, -1.4 * s, 0.005 * s, None, 1), 'torso': 0.02 * s, 'sq': 1 + 0.012 * s, 'fx': shadow(0, 22)}
    def tgt(f, b):
        t = f / n; return {'armFu': .04 * sn(2 * math.pi * t - .8), 'armFl': .05 * sn(2 * math.pi * t - 1.4), 'head': .03 * sn(2 * math.pi * t - .5), 'tailA': .12 * sn(2 * math.pi * t - 1.2), 'tailB': .2 * sn(2 * math.pi * t - 1.8)}.get(b, 0)
    return simulate(n, kin, tgt)
def walk(n=16):
    def kin(f):
        t = f / n; s = sn(2 * math.pi * t); c = cs(2 * math.pi * t)
        return {'root': (0, -3 * abs(s), 0.02 * s, None, 1), 'torso': 0.05 * s + 0.03, 'legL': (0.5 * s, 1), 'legR': (-0.5 * s, 1), 'fx': shadow(0, 22)}
    def tgt(f, b):
        t = f / n; s = sn(2 * math.pi * t)
        return {'armFu': -.25 * s, 'armFl': -.2 * s, 'armBu': .35 * s, 'armBl': .25 * s, 'head': -.05 * s, 'tailA': .2 * sn(2 * math.pi * t - .8), 'tailB': .3 * sn(2 * math.pi * t - 1.4)}.get(b, 0)
    fr = simulate(n, kin, tgt)
    return fr
def death(n=28):
    def kin(f):
        if f == 0: return {'root': (0, 0, 0, None, 1), 'fx': shadow(0, 22)}
        if f <= 2:  # golpe
            k = ez(f / 2); return {'root': (-4 * k, -2 * k, -0.08 * k, None, 1), 'torso': -0.22 * k, 'fx': shadow(0, 22)}
        if f <= 7:  # cambaleia: joelhos cedem
            k = (f - 2) / 5; return {'root': (-4 - 6 * k, 3 * k, -0.08 - 0.22 * k, None, 1 - 0.07 * sn(k * 3.14)), 'torso': -0.22 - 0.2 * k, 'legL': (0.35 * k, 1), 'legR': (-0.3 * k, 1), 'sq': 1 - 0.06 * k, 'fx': shadow(0, 22)}
        if f <= 15:  # queda acelera
            k = (f - 7) / 8; a = -0.3 - 1.27 * (k ** 1.7)
            lift = -30 * (min(1, abs(a) / 1.55) ** 2)
            return {'root': (-10 - 22 * k, lift, a, None, 1), 'torso': -0.42 + 0.42 * k, 'legL': (0.35 + 0.3 * k, 1), 'legR': (-0.3 - 0.25 * k, 1), 'fx': shadow(-34 * k, 22 + 24 * k, .5)}
        j = f - 15       # impacto + repouso
        bounce = -5 * math.exp(-j * .55) * abs(cs(j * 1.4)); sq = 1 - 0.1 * math.exp(-j * .7)
        fx = both(shadow(-46, 46, .5), dust(-38, cl((j - 1) / 9)) if 1 <= j <= 10 else None)
        return {'root': (-32, -30 + bounce, -1.57, None, sq), 'torso': 0.0, 'legL': (0.1 * math.exp(-j * .3), 1), 'legR': (-0.08 * math.exp(-j * .3), 1), 'fx': fx}
    def tgt(f, b):
        if f <= 2: return {'head': -.5, 'armFu': .7, 'armFl': .9, 'armBu': -.7, 'armBl': -.6, 'tailA': .3, 'tailB': .6}.get(b, 0)
        if f <= 7: return {'head': -.45, 'armFu': .5 + .3 * sn(f * 1.3), 'armFl': .6, 'armBu': -.5 - .3 * sn(f * 1.1), 'armBl': -.4, 'tailA': .3, 'tailB': .5}.get(b, 0)
        if f <= 15: return {'head': -.2, 'armFu': 0, 'armFl': .2, 'armBu': 0, 'armBl': 0, 'tailA': .3, 'tailB': .6}.get(b, 0)
        return {'head': .12, 'armFu': -.9, 'armFl': .5, 'armBu': .9, 'armBl': .3, 'tailA': -.1, 'tailB': -.25}.get(b, 0)
    kicks = {(16, 'armFu'): -6, (16, 'armBu'): 6, (16, 'armFl'): -5, (16, 'armBl'): 5, (16, 'head'): 5, (16, 'tailB'): -8}
    return simulate(n, kin, tgt, kicks)
if __name__ == '__main__':
    from PIL import Image
    import sys
    fr = death()
    cols = 7; rows = (len(fr) + cols - 1) // cols
    sh = Image.new('RGBA', (cols * CW * 2, rows * CH * 2), (40, 30, 50, 255))
    for i, im in enumerate(fr): sh.alpha_composite(im.resize((CW * 2, CH * 2), Image.NEAREST), ((i % cols) * CW * 2, (i // cols) * CH * 2))
    sh.save('/tmp/claude-0/-home-user-neon-wars/3ffd125f-a99a-599e-8554-f2b481e86fc1/scratchpad/death_soft.png'); print(sh.size)

def attack(n=14):
    def kin(f):
        if f <= 4: k = ez(f / 4); return {'root': (-5 * k, 2 * k, -0.1 * k, None, 1 - .04 * k), 'torso': -0.22 * k, 'legL': (-0.25 * k, 1), 'legR': (0.2 * k, 1), 'fx': shadow(0, 22)}
        if f <= 7: k = ez((f - 4) / 3); return {'root': (-5 + 14 * k, 2 - 3 * k, -0.1 + 0.3 * k, None, 1 + .03 * k), 'torso': -0.22 + 0.5 * k, 'legL': (-0.25 + 0.5 * k, 1), 'legR': (0.2 - 0.4 * k, 1), 'fx': shadow(0, 22)}
        k = ez((f - 7) / 6); return {'root': (9 * (1 - k), -1 * (1 - k), 0.2 * (1 - k), None, 1), 'torso': 0.28 * (1 - k), 'legL': (0.25 * (1 - k), 1), 'legR': (-0.2 * (1 - k), 1), 'fx': shadow(0, 22)}
    def tgt(f, b):
        if f <= 4: return {'armFu': .9, 'armFl': 1.1, 'armBu': -.5, 'armBl': -.3, 'head': -.12, 'tailA': .3, 'tailB': .5}.get(b, 0)
        if f <= 8: return {'armFu': -1.3, 'armFl': -.9, 'armBu': .5, 'armBl': .3, 'head': .12, 'tailA': -.3, 'tailB': -.5}.get(b, 0)
        return {}.get(b, 0)
    return simulate(n, kin, tgt, {(5, 'armFl'): -6, (5, 'armFu'): -4, (5, 'tailB'): -5})
def cast(n=12):
    def kin(f):
        k = ez(cl(f / 5)) * (1 if f < 9 else 1 - ez((f - 9) / 2))
        return {'root': (0, -2 * k, -0.04 * k, None, 1), 'torso': -0.1 * k, 'fx': shadow(0, 22)}
    def tgt(f, b):
        k = ez(cl(f / 5)) * (1 if f < 9 else 1 - ez((f - 9) / 2))
        return {'armFu': .55 * k, 'armFl': -.7 * k, 'armBu': -.3 * k, 'armBl': -.2 * k, 'head': -.25 * k, 'tailA': .15 * sn(f), 'tailB': .3 * sn(f - .6)}.get(b, 0)
    return simulate(n, kin, tgt)
def hurt(n=8):
    def kin(f):
        k = ez(f / 2) if f <= 2 else 1 - ez((f - 2) / 5)
        return {'root': (-5 * k, 1 * k, -0.12 * k, None, 1 - .05 * k), 'torso': -0.2 * k, 'legL': (0.15 * k, 1), 'legR': (-0.15 * k, 1), 'fx': shadow(0, 22)}
    def tgt(f, b):
        return {'head': -.45, 'armFu': .6, 'armFl': .5, 'armBu': -.6, 'armBl': -.4, 'tailA': .3, 'tailB': .5}.get(b, 0) * (1 if f <= 3 else 0.2)
    return simulate(n, kin, tgt, {(1, 'head'): -9, (1, 'armFu'): 7, (1, 'armBu'): -7, (1, 'tailB'): 8})
ALL = None
def build():
    return {'idle': idle(), 'walk': walk(), 'attack': attack(), 'cast': cast(), 'hurt': hurt(), 'death': death()}
