"""Monta o atlas do jogo (formato cx_*_atlas) a partir das animacoes do Boticario (rato alquimista). Vista unica (direita); d/u/s apontam para os mesmos quadros."""
import sys, json, os; sys.path.insert(0, '.')
import numpy as np
from PIL import Image
import anims2 as A
from soft import S, OX, OY, FEET, CW, CH
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out'); os.makedirs(OUT, exist_ok=True)
an = A.build()
an['run'] = an['walk']
order = ['idle', 'walk', 'run', 'attack', 'hurt', 'death', 'cast']
frames = []; idx = {}
for k in order:
    if k == 'run': idx['run'] = idx['walk']; continue
    idx[k] = list(range(len(frames), len(frames) + len(an[k]))); frames += an[k]
bb = None
for im in frames:
    b = im.getbbox()
    if b: bb = b if bb is None else (min(bb[0], b[0]), min(bb[1], b[1]), max(bb[2], b[2]), max(bb[3], b[3]))
x0, y0, x1, y1 = max(0, bb[0] - 1), max(0, bb[1] - 1), min(CW, bb[2] + 1), min(CH, bb[3] + 1)
SC = 2; cw, ch = (x1 - x0) * SC, (y1 - y0) * SC; cols = 24; rows = (len(frames) + cols - 1) // cols
atlas = Image.new('RGBA', (cols * cw, rows * ch), (0, 0, 0, 0))
for i, im in enumerate(frames): atlas.alpha_composite(im.crop((x0, y0, x1, y1)).resize((cw, ch), Image.NEAREST), ((i % cols) * cw, (i // cols) * ch))
fx_, fy_ = (OX + FEET[0]) * S - x0, (OY + FEET[1]) * S - y0
meta = {'w': cw, 'h': ch, 'ax': int(round(fx_ * SC)), 'ay': int(round(fy_ * SC)), 'cols': cols, 'anims': {}}
for k in order:
    for v in 'dus': meta['anims'][f'{k}_{v}'] = idx[k]
atlas.save(OUT + '/cx_boticario_atlas.png', optimize=True); json.dump(meta, open(OUT + '/cx_boticario_atlas.json', 'w'))
print('frames', len(frames), 'cell', cw, ch, 'anchor', meta['ax'], meta['ay'], atlas.size)
