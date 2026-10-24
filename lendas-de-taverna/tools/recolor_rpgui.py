"""Recolore as imagens do RPGUI (npm rpgui@1.0.3, zlib) pro tema "couro" do jogo.
Uso: python3 tools/recolor_rpgui.py <pasta com as imagens originais> [pasta de saída]
Botões dourados (cta) ganham um ouro mais sóbrio; barras de progresso ficam como no original."""
import colorsys, os, shutil, sys
from PIL import Image
SRC = sys.argv[1]; DST = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(__file__), '..', 'assets', 'rpgui')
COURO = (0, 0.55, 0.72)                       # matiz, saturação, valor
OURO = (10, 0.95, 1.0)
KEEP = {'progress', 'progress-red', 'progress-green', 'progress-blue'}
def tf(rgb, dh, sm, vm):
    h, s, v = colorsys.rgb_to_hsv(*[c / 255 for c in rgb]); h = (h + dh / 360) % 1
    return tuple(round(c * 255) for c in colorsys.hsv_to_rgb(h, min(1, s * sm), min(1, v * vm)))
USED = ['border-image-golden','border-image-golden2','border-image-grey','border-image','background-image-golden','background-image-golden2','background-image-grey','background-image','button','button-hover','button-down','button-golden','button-golden-hover','button-golden-down','hr','hr-golden','progress','progress-red','progress-green','progress-blue','progress-bar-left','progress-bar-track','progress-bar-right']
os.makedirs(DST, exist_ok=True)
for n in USED:
    f = n + '.png'
    if n in KEEP: shutil.copy(os.path.join(SRC, f), os.path.join(DST, f)); continue
    pal = OURO if n.startswith('button-golden') else COURO
    im = Image.open(os.path.join(SRC, f)).convert('RGBA'); px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if a: px[x, y] = tf((r, g, b), *pal) + (a,)
    im.save(os.path.join(DST, f))
parts = [Image.open(os.path.join(DST, n + '.png')).convert('RGBA') for n in ('progress-bar-left', 'progress-bar-track', 'progress-bar-right')]
bar = Image.new('RGBA', (sum(p.width for p in parts), parts[0].height), (0, 0, 0, 0)); x = 0
for p in parts: bar.paste(p, (x, 0)); x += p.width
bar.save(os.path.join(DST, 'bar-frame.png'))
for n in ('progress-bar-left', 'progress-bar-track', 'progress-bar-right'): os.remove(os.path.join(DST, n + '.png'))
print('ok ->', DST)
