# recorta o kit do medidor de rank (src.png, gerado pelo dono, ja com fundo transparente) em pecas separadas
from PIL import Image
import os
D = os.path.join(os.path.dirname(__file__), '..', '..', 'mmo', 'assets', 'kit', 'rank')
im = Image.open(os.path.join(D, 'src.png')).convert('RGBA')
CROPS = {
    'frame': (40, 205, 650, 300), 'fire': (600, 35, 790, 160),
    'D': (870, 85, 1030, 270), 'C': (1085, 75, 1265, 255), 'B': (1305, 75, 1475, 260),
    'A': (880, 290, 1110, 540), 'S': (1150, 270, 1430, 550),
    'combo': (60, 810, 450, 975), 'hits': (630, 870, 760, 965),
}
for k, b in CROPS.items():
    c = im.crop(b)
    a = c.getchannel('A').point(lambda v: 255 if v > 24 else 0)
    bb = a.getbbox()
    c = c.crop(bb) if bb else c
    if k == 'fire':   # tira o halo escuro em volta do fogo (alfa pelo brilho)
        import numpy as np
        a = np.array(c).astype(float); m = a[..., :3].max(2)
        a[..., 3] = a[..., 3] * np.clip((m - 60) / 90, 0, 1); c = Image.fromarray(a.astype('uint8'))
        bb = c.getchannel('A').point(lambda v: 255 if v > 24 else 0).getbbox(); c = c.crop(bb) if bb else c
    c.save(os.path.join(D, k + '.png')); print(k, c.size)
