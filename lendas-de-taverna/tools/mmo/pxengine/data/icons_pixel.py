#!/usr/bin/env python3
"""Icones de item em pixel art (16x16, por codigo) com moldura de raridade."""
import math
from PIL import Image
from pxrig import Grid, autoline
import chibi as C

IP = dict(K='#0c0814', S='#8a96b0', s='#c8d4ec', d='#4a5470', G='#e0b040', g='#f8e080', h='#a07020', r='#d03a48', R='#8a1c28', p='#f4c0c8',
          b='#3a8ae0', B='#1c4aa0', c='#a8dcff', n='#48b858', N='#1c6a30', w='#f4f0e8', W='#b0a8a0', l='#8a5a30', L='#5a3418', o='#e07a18', u='#a060e0', U='#5a2aa0', t='#d8c8a0', T='#9a8a60', k='#2a2438')
ISEL = {c: '#08040e' for c in IP}

ART = {
 'helm': ['....dddddd....', '..dSSSSSSSSd..', '.dSssSSSSSSSd.', '.dSsSSSSSSSSd.', '.dSSSSSSSSSSd.', '.dSKKKSSKKKSd.', '.dSKKKSSKKKSd.', '.dSSSSSSSSSSd.', '.dSS.dSSd.SSd.', '.dd...dd...dd.'],
 'armor': ['..dd......dd..', '.dSSd.dd.dSSd.', 'dSsSSdSSdSSsSd', 'dSsSSSSSSSSsSd', '.dSSSSGGSSSSd.', '.dSSSSGGSSSSd.', '..dSSSSSSSSd..', '..dSSSddSSSd..', '..dSSd..dSSd..', '...dd....dd...'],
 'gloves': ['..dd.dd.dd....', '.dSSdSSdSSd...', '.dSSSSSSSSd...', '.dSsSSSSSSd...', '.dSSSSSSSSSd..', '..dSSSSSSSSd..', '...dSSSSSSd...', '...dGGGGGd....', '...dddddd.....'],
 'boots': ['..dddd........', '.dLLLLd.......', '.dLllLd.......', '.dLllLd.......', '.dLllLd.......', '.dLllLdddd....', '.dLllLLLLLd...', '.dLlllllllLd..', '.dGGGGGGGGGd..', '..ddddddddd...'],
 'ring': ['....dGGd....', '...dGggGd...', '..dGg..gGd..', '.dGg....gGd.', '.dG..ur..Gd.', '.dGg.uU.gGd.', '..dGg..gGd..', '...dGGGGd...', '....dddd....'],
 'amulet': ['.d........d.', '.dd......dd.', '..dd....dd..', '...dd..dd...', '....dddd....', '....dGGd....', '...dGrRGd...', '...dGrRGd...', '....dGGd....', '.....dd.....'],
 'potion': ['....dddd....', '....dWWd....', '.....dd.....', '....dwwd....', '...dwppwd...', '..drrrrrrd..', '..drprrrRd..', '..drrrrrRd..', '..dRrrrRRd..', '...dRRRRd...', '....dddd....'],
 'scroll': ['.dtttttttd..', 'dtTtttttTtd.', 'dttdddddttd.', '.dtttttttd..', '.dtdddddtd..', '.dtttttttd..', '.dtdddddtd..', 'dtTtttttTtd.', '.dtttttttd..'],
 'coin': ['...dddd...', '..dGggGd..', '.dGgGGGGd.', '.dGGhhGGd.', '.dGGhhGGd.', '.dGGGGGGd.', '..dGGGGd..', '...dddd...'],
 'gem': ['..dddddd..', '.dcbbbbcd.', 'dcbbBBbbcd', 'dcbBBBBbBd', '.dbBBBBBd.', '..dbBBBd..', '...dBBd...', '....dd....'],
 'bone': ['dwwd....dwwd', 'dwwwd..dwwwd', '.dwwwddwwwd.', '..dwwwwwwd..', '..dwwwwwwd..', '.dwwwddwwwd.', 'dwwwd..dwwwd', 'dwwd....dwwd'],
 'leather': ['..dddddddd..', '.dllllllld..', 'dlLllllllLd.', 'dlllLLlllld.', 'dllLlllLlld.', '.dlllllllld.', '..dLllllLd..', '...dddddd...'],
 'herb': ['......dd....', '....dnnnd...', '...dnNnnnd..', '.dd.dnnNd...', 'dnnd.dnd.dd.', 'dnNnd.d.dnnd', '.dnnNd.dnNd.', '..dnnNdnnd..', '...dnnnnd...', '....dLLd....', '....dLLd....'],
 'ore': ['...dddd.....', '..dSssSd.dd.', '.dSssSSddSSd', '.dSSdSSdSssd', '..ddSSSdSSd.', '..dSSdddSSd.', '.dSSSd.dSSd.', '.ddddd.dddd.'],
 'key': ['.dGGGd......', 'dGgggGd.....', 'dGg.gGd.....', 'dGgggGd.....', '.dGGGGdd....', '..dGGGGGdd..', '...dGhGGGGd.', '....ddGhdGd.', '......dGd.d.', '.......dd...'],
 'chest': ['.dddddddddd.', 'dLllllllllLd', 'dlLLLLLLLLld', 'dGGGGGGGGGGd', 'dlGGgggGGGld', 'dlLLGhGLLLld', 'dllllGGllllld', 'dLllllllllLd', '.dddddddddd.'],
 'shield': ['.dddddddddd.', 'dSssSSSSSSSd', 'dSsSSSddSSSd', 'dSSSSdGGdSSd', 'dSSSSdGGdSSd', '.dSSSSddSSd.', '.dSSSSSSSSd.', '..dSSSSSSd..', '...dSSSSd...', '....dddd....'],
}
POT = {'red': dict(r='#d03a48', R='#8a1c28', p='#f4a0a8'), 'blue': dict(r='#3a8ae0', R='#1c4aa0', p='#a8dcff'), 'green': dict(r='#48b858', R='#1c6a30', p='#b8f0a8')}
RAR = {'comum': ('#7a7a8c', '#4a4a5a'), 'incomum': ('#58c868', '#2a7a38'), 'raro': ('#4a98f0', '#2458a8'), 'epico': ('#b068f0', '#6a30a8'), 'lendario': ('#f0a030', '#a05c10')}


def from_art(rows, pal=None):
    g = Grid(16, 16); W = max(len(r) for r in rows); ox = (16 - W) // 2; oy = (16 - len(rows)) // 2
    g.stamp(rows, ox, oy)
    autoline(g)
    p = dict(IP); sel = dict(ISEL)
    if pal: p.update(pal)
    return g.render(p, sel)


def weapon_icon(wid):
    sp = C.WEAPONS[wid]; kind = sp['kind']; pal = dict(IP); pal.update(sp['pal'])
    g = Grid(16, 16)
    if kind in ('sword', 'dagger'):
        cells, tip = C.shaped_rows((4, 12), 135, int(round(min(sp['len'], 15 if kind == 'sword' else 10) * (.62 if kind == 'sword' else .95))), max(1, int(round(sp.get('guard', 3) * .6))), sp.get('shape') or 'straight', sp.get('gstyle', 'bar'), sp.get('glow'), False, False) if True else (None, None)
    elif kind == 'staff': cells, tip = C.staff_rows((5, 11), 135, 20, sp.get('orb', 1))
    elif kind == 'mace': cells, tip = C.mace_rows((5, 11), 135, 14)
    else:
        cells, _, _ = C.bow_rows((7, 8), (1, -1), 0, False, 7)
        tip = None
    for (x, y), ch in cells.items(): g.put(x, y, ch)
    autoline(g)
    return g.render(pal, {c: '#08040e' for c in pal})


def frame(rar='comum', size=20):
    a, b = RAR[rar]; im = Image.new('RGBA', (size, size), (0, 0, 0, 0)); px = im.load()
    h = lambda c: tuple(int(c[i:i + 2], 16) for i in (1, 3, 5)) + (255,)
    for y in range(size):
        for x in range(size):
            if x in (0, size - 1) or y in (0, size - 1):
                if (x in (0, size - 1)) and (y in (0, size - 1)): continue
                px[x, y] = h(b)
            elif x in (1, size - 2) or y in (1, size - 2): px[x, y] = h(a)
            else: px[x, y] = (22, 18, 36, 255)
    return im


def slot(icon, rar='comum', size=20):
    im = frame(rar, size)
    if icon is not None: im.alpha_composite(icon, ((size - 16) // 2, (size - 16) // 2))
    return im


STARS = {'comum': 1, 'incomum': 2, 'raro': 3, 'epico': 4, 'lendario': 5}


def cell(icon, rar='comum', size=18, pc=None, up=0, arrow=None):
    """celula de item como no jogo: moldura/fundo da raridade, icone, estrelas (topo), PC (embaixo), +N de melhoria e seta comparativa"""
    import pxfont
    a, b = RAR[rar]; ha = tuple(int(a[i:i + 2], 16) for i in (1, 3, 5)); hb = tuple(int(b[i:i + 2], 16) for i in (1, 3, 5))
    im = Image.new('RGBA', (size, size), (0, 0, 0, 0)); px = im.load()
    for y in range(size):
        for x in range(size):
            t = (x + y) / (2 * size)
            bgc = tuple(int(13 + (c - 13) * .22 * (1 - t)) for c in ha) + (255,)
            px[x, y] = hb + (255,) if (x in (0, size - 1) or y in (0, size - 1)) else (ha + (255,) if (x in (1, size - 2) or y in (1, size - 2)) else bgc)
    for (x, y) in ((0, 0), (size - 1, 0), (0, size - 1), (size - 1, size - 1)): px[x, y] = (0, 0, 0, 0)
    if icon is not None:
        ic = icon.crop((1, 1, 15, 15)); im.alpha_composite(ic, ((size - 14) // 2, (size - 14) // 2 - 1))
        for k in range(STARS[rar]): px[2 + k * 2, 2] = (255, 214, 74, 255)
        if pc is not None:
            t = pc if isinstance(pc, str) else str(pc)
            pxfont.text(im, (size - 2 - pxfont.width(t), size - 7), t, (255, 236, 170), False, True)
        if up: pxfont.text(im, (size - 2 - pxfont.width('+%d' % up), 3), '+%d' % up, (140, 255, 160))
        if arrow == 'up': px[size - 4, 3] = (90, 255, 120, 255); px[size - 5, 4] = (90, 255, 120, 255); px[size - 3, 4] = (90, 255, 120, 255)
        if arrow == 'dn': px[size - 4, 4] = (255, 90, 90, 255); px[size - 5, 3] = (255, 90, 90, 255); px[size - 3, 3] = (255, 90, 90, 255)
    return im


def get(name, pot=None):
    if name == 'potion': return from_art(ART['potion'], POT[pot or 'red'])
    if name in ART: return from_art(ART[name])
    return weapon_icon(name)


if __name__ == '__main__':
    import os
    from teste_clareira import OUT
    names = [('espada_aco', 'raro'), ('espada_ferro', 'comum'), ('katana', 'epico'), ('machado', 'incomum'), ('espada_chamas', 'lendario'), ('adaga_veneno', 'raro'), ('cajado_arcano', 'epico'), ('cajado_fogo', 'incomum'), ('arco_longo', 'raro'), ('maca_ferro', 'comum'), ('martelo_sagrado', 'lendario'),
             ('helm', 'incomum'), ('armor', 'raro'), ('gloves', 'comum'), ('boots', 'incomum'), ('shield', 'raro'), ('ring', 'epico'), ('amulet', 'lendario'), ('potion:red', 'comum'), ('potion:blue', 'comum'), ('potion:green', 'incomum'),
             ('scroll', 'comum'), ('coin', 'comum'), ('gem', 'raro'), ('bone', 'comum'), ('leather', 'comum'), ('herb', 'comum'), ('ore', 'incomum'), ('key', 'epico'), ('chest', 'raro')]
    S = Image.new('RGBA', (20 * 10, 20 * 3), (14, 10, 24, 255))
    for i, (n, r) in enumerate(names):
        ic = get(*(n.split(':') if ':' in n else (n,)))
        S.alpha_composite(slot(ic, r), ((i % 10) * 20, (i // 10) * 20))
    S.resize((S.width * 5, S.height * 5), Image.NEAREST).convert('RGB').save(os.path.join(OUT, 'icones_itens.png'))
