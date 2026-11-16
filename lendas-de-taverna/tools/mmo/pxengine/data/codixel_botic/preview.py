import sys, os; sys.path.insert(0, '.'); sys.path.insert(0, '..')
import anims2 as A, pxfont
from soft import CW, CH
from PIL import Image
OUT = '/home/user/neon-wars/lendas-de-taverna/mmo/proto_pixel'
an = A.build()
order = [('PARADO', 'idle'), ('ANDAR', 'walk'), ('ATAQUE', 'attack'), ('CONJURAR', 'cast'), ('DANO', 'hurt'), ('MORTE', 'death')]
S2 = 2; cw, ch = CW * S2, CH * S2 + 14
frames = []
for t in range(66):
    sh = Image.new('RGBA', (cw * 3, ch * 2), (36, 26, 46, 255))
    for i, (lb, k) in enumerate(order):
        fr = an[k]; n = len(fr)
        idx = min(n - 1, t % (n + 8)) if k in ('death', 'hurt') else t % n
        x, y = (i % 3) * cw, (i // 3) * ch
        sh.alpha_composite(fr[idx].resize((CW * S2, CH * S2), Image.NEAREST), (x, y + 14)); pxfont.text(sh, (x + cw // 2, y + 2), lb, (240, 226, 190), center=True)
    frames.append(sh.convert('P', palette=Image.ADAPTIVE, colors=48))
frames[0].save(OUT + '/boticario_animacoes.gif', save_all=True, append_images=frames[1:], duration=71, loop=0, optimize=True)
for name, k in (('morte', 'death'), ('ataque', 'attack')):
    d = an[k]; cols = 8; rows = (len(d) + cols - 1) // cols
    sh = Image.new('RGBA', (cols * CW * 2, rows * CH * 2), (36, 26, 46, 255))
    for i, im in enumerate(d): sh.alpha_composite(im.resize((CW * 2, CH * 2), Image.NEAREST), ((i % cols) * CW * 2, (i // cols) * CH * 2))
    sh.save(OUT + f'/boticario_{name}.png')
print(os.path.getsize(OUT + '/boticario_animacoes.gif') // 1024, 'KB', {k: len(v) for k, v in an.items()})
