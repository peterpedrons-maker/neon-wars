"""Folha de conferencia dos inimigos REAIS do jogo (le mmo/assets/chars/cx_*_atlas): 1) fila por altura relativa (CXSIZE) e
2) grade com as 3 vistas (frente, lado, costas). Uso: python3 bestiario_folha.py <saida_dir>"""
import json, os, re, sys, glob
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pxfont as F
CH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../../../mmo/assets/chars')
IDX = os.path.join(CH, '../../index.html')
src = open(IDX, encoding='utf8').read()
SZ = {k: float(v) for k, v in re.findall(r'(\w+):(\.?\d*\.?\d+)', re.search(r'const CXSIZE=\{(.*?)\};', src, re.S).group(1))}
CXSC = 0.75
def load(key):
    j = json.load(open(f'{CH}/cx_{key}_atlas.json')); im = Image.open(f'{CH}/cx_{key}_atlas.png').convert('RGBA'); return j, im
def frame(j, im, anim, i=0):
    idx = j['anims'][anim][i]; w, h, c = j['w'], j['h'], j['cols']
    return im.crop(((idx % c) * w, (idx // c) * h, (idx % c) * w + w, (idx // c) * h + h))
def trim(f):
    b = f.getchannel('A').point(lambda v: 255 if v > 8 else 0).getbbox(); return f.crop(b) if b else f
keys = sorted(os.path.basename(p)[3:-11] for p in glob.glob(f'{CH}/cx_*_atlas.json'))
ENEM = [k for k in keys if not k.startswith(('h_', 'n_'))]
BOSS = ['grunk', 'morvath', 'gorgash', 'ratking', 'skrix', 'presa', 'vampiro', 'boticario', 'rei']
NAMES = {}
def size_row(lst, out, title):
    items = []
    for k in lst:
        j, im = load(k); f = frame(j, im, 'idle_s', 0); s = SZ.get(k, 1.0) * CXSC
        f = f.resize((max(1, round(f.width * s)), max(1, round(f.height * s))), Image.NEAREST)
        # ancora nos pes: usa a base opaca do quadro
        b = f.getchannel('A').getbbox(); items.append((k, f, b))
    hero_j, hero_im = load('h_guerreiro'); hf = frame(hero_j, hero_im, 'idle_s', 0); hf = hf.resize((round(hf.width * CXSC), round(hf.height * CXSC)), Image.NEAREST)
    items.insert(0, ('HEROI', hf, hf.getchannel('A').getbbox()))
    Z = 3; per = 9; rows = (len(items) + per - 1) // per; cw = 110; ch_ = 178
    sh = Image.new('RGBA', (per * cw, rows * ch_ + 18), (28, 24, 38, 255)); d = ImageDraw.Draw(sh)
    F.text(sh, (6, 5), title, k=1)
    for n, (k, f, b) in enumerate(items):
        x0, y0 = (n % per) * cw, 18 + (n // per) * ch_
        g = f.crop(b).resize(((b[2] - b[0]) * 2, (b[3] - b[1]) * 2), Image.NEAREST)
        sh.alpha_composite(g, (x0 + (cw - g.width) // 2, y0 + 140 - g.height))
        d.line([(x0 + 6, y0 + 141), (x0 + cw - 6, y0 + 141)], fill=(60, 52, 80, 255))
        F.text(sh, (x0 + cw // 2, y0 + 148), k.upper()[:16], center=True, k=1)
        F.text(sh, (x0 + cw // 2, y0 + 160), 'x%.2f' % (1.0 if k == 'HEROI' else SZ.get(k, 1.0)), center=True, col=(150, 200, 255), k=1)
    sh.convert('RGB').save(out)
def grid(lst, out, title):
    cells = []
    for k in lst:
        j, im = load(k); fs = [trim(frame(j, im, f'idle_{v}', 0)) for v in 'dsu']; cells.append((k, fs))
    cw = 3 * 78 + 10; ch_ = 100; per = 3; rows = (len(cells) + per - 1) // per
    sh = Image.new('RGBA', (per * cw, rows * ch_ + 18), (28, 24, 38, 255)); d = ImageDraw.Draw(sh)
    F.text(sh, (6, 5), title, k=1)
    for n, (k, fs) in enumerate(cells):
        x0, y0 = (n % per) * cw, 18 + (n // per) * ch_
        for v, f in enumerate(fs):
            if f.height > 72 or f.width > 74: r = min(72 / f.height, 74 / f.width); f = f.resize((max(1, int(f.width * r)), max(1, int(f.height * r))), Image.NEAREST)
            sh.alpha_composite(f, (x0 + 4 + v * 78 + (74 - f.width) // 2, y0 + 78 - f.height))
        d.line([(x0 + 4, y0 + 79), (x0 + cw - 8, y0 + 79)], fill=(60, 52, 80, 255))
        F.text(sh, (x0 + cw // 2, y0 + 84), k.upper(), center=True, k=1)
    sh.convert('RGB').save(out)
if __name__ == '__main__':
    o = sys.argv[1]; os.makedirs(o, exist_ok=True)
    mobs = [k for k in ENEM if k not in BOSS]
    size_row(mobs, f'{o}/bestiario_alturas.png', 'ALTURAS RELATIVAS (HEROI A ESQUERDA)')
    size_row([k for k in BOSS if k in keys], f'{o}/chefes_alturas.png', 'CHEFES E MINI-CHEFES')
    grid(mobs, f'{o}/bestiario_vistas.png', 'INIMIGOS: FRENTE / LADO / COSTAS')
    grid([k for k in BOSS if k in keys], f'{o}/chefes_vistas.png', 'CHEFES: FRENTE / LADO / COSTAS')
    print(len(mobs), 'inimigos', [k for k in mobs])
