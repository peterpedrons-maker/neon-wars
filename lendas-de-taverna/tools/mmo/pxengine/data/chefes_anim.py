"""Video com as animacoes de cada chefe (parado, andar, ataque, conjurar, dano, morte) em 3 vistas, lidas dos atlas reais do jogo."""
import json, os, sys
from PIL import Image, ImageDraw
import pxfont, vid
A = '/home/user/neon-wars/lendas-de-taverna/mmo/assets/chars'
OUT = '/home/user/neon-wars/lendas-de-taverna/mmo/proto_pixel'
BOSSES = [('MORVATH', 'morvath', 'Catacumbas'), ('GORGASH', 'gorgash', 'Floresta de Brumavale'), ('REI DOS RATOS', 'ratking', 'Esgotos'),
          ('XAMA SKRIX', 'skrix', 'mini-chefe: Floresta dos Goblins'), ('BOTICARIO PODRE', 'boticario', 'mini-chefe: Esgotos'),
          ('CAP. PRESA-DE-FERRO', 'presa', 'mini-chefe: Floresta de Brumavale'), ('MORCEGO-VAMPIRO', 'vampiro', 'mini-chefe: Catacumbas')]
ROWS = [('PARADO', 'idle'), ('ANDAR', 'walk'), ('ATAQUE', 'attack'), ('CONJURAR', 'cast'), ('DANO', 'hurt'), ('MORTE', 'death')]
VIEWS = [('d', 'FRENTE'), ('s', 'LADO'), ('u', 'COSTAS')]
S = 1  # atlas ja esta em 2x
def load(key):
    j = json.load(open(f'{A}/cx_{key}_atlas.json')); im = Image.open(f'{A}/cx_{key}_atlas.png').convert('RGBA')
    w, h, cols = j['w'], j['h'], j['cols']
    def fr(i): return im.crop(((i % cols) * w, (i // cols) * h, (i % cols) * w + w, (i // cols) * h + h))
    return j, fr
def seg(title, key, sub, secs=5, fps=24):
    j, fr = load(key); w, h = j['w'], j['h']
    cw, ch = w + 8, h + 10; W = 3 * cw + 12; H = 40 + 6 * ch + 8
    out = []
    for t in range(secs * fps):
        c = Image.new('RGBA', (W, H), (28, 20, 38, 255)); d = ImageDraw.Draw(c)
        pxfont.text(c, (W // 2, 4), title, (255, 226, 150), center=True, size=2) if 'size' in pxfont.text.__code__.co_varnames else pxfont.text(c, (W // 2, 4), title, (255, 226, 150), center=True)
        pxfont.text(c, (W // 2, 22), sub.upper(), (170, 150, 200), center=True)
        for r, (nm, an) in enumerate(ROWS):
            for v, (vk, vn) in enumerate(VIEWS):
                x0, y0 = 6 + v * cw, 40 + r * ch
                d.rectangle([x0, y0, x0 + cw - 2, y0 + ch - 2], fill=(44, 34, 58, 255), outline=(90, 70, 110, 255))
                idx = j['anims'][f'{an}_{vk}']
                if not idx: continue
                loopt = t % (len(idx) + (10 if an in ('death', 'hurt') else 0))
                i = idx[min(loopt, len(idx) - 1)]
                c.alpha_composite(fr(i), (x0 + 4, y0 + 2))
            pxfont.text(c, (8, 40 + r * ch + 2), nm, (240, 226, 190))
        out.append(c)
    return out
if __name__ == '__main__':
    frames = []
    for t, k, s in BOSSES: frames += seg(t, k, s)
    n = vid.mp4(frames, OUT + '/chefes_animacoes.mp4', fps=24, scale=1); print('mp4', n // 1024, 'KB', len(frames))
