"""Gera mmo/assets/fx/rei_explosao_roxa.png/.json a partir do PixelFx (MIT, github.com/BigTwoFly/PixelFx).
Uso: (no checkout do PixelFx) node tools/render.mjs shadow/dark-explosion --sheet --fps 20 --out rec20
     python3 export_pfx_rei.py /caminho/rec20/shadow/dark-explosion/ <saida mmo/assets/fx>
Recorta os quadros 9..52 (0,45s..2,6s: da liberacao ao fim da fumaca) e empacota numa folha 8 colunas."""
import json, sys
from PIL import Image
d, out = sys.argv[1], sys.argv[2]
j = json.load(open(d + 'dark-explosion.json')); im = Image.open(d + 'dark-explosion.png').convert('RGBA')
fs = [im.crop((f['frame']['x'], f['frame']['y'], f['frame']['x'] + 280, f['frame']['y'] + 248)) for f in j['frames'][9:53]]
bb = None
for f in fs:
    b = f.getchannel('A').point(lambda v: 255 if v > 8 else 0).getbbox()
    if b: bb = b if bb is None else (min(bb[0], b[0]), min(bb[1], b[1]), max(bb[2], b[2]), max(bb[3], b[3]))
w, h, cols = bb[2] - bb[0], bb[3] - bb[1], 8
sh = Image.new('RGBA', (w * cols, h * ((len(fs) + cols - 1) // cols)), (0, 0, 0, 0))
for i, f in enumerate(fs): sh.paste(f.crop(bb), ((i % cols) * w, (i // cols) * h))
sh.save(out + '/rei_explosao_roxa.png', optimize=True)
json.dump(dict(w=w, h=h, n=len(fs), cols=cols, fps=20, ox=140 - bb[0], oy=206 - bb[1]), open(out + '/rei_explosao_roxa.json', 'w'))
