import sys; sys.path.insert(0, '.')
import chibi as C, chibi_anim2 as N, pxfont
from PIL import Image
HERO = dict(cls='warrior', hat='helm', outfit='mail', metal='aco', clothes='aco', weapon='espada_aco')
OUT = '/home/user/neon-wars/lendas-de-taverna/mmo/proto_pixel'
W, H = C.W, C.H; S = 3
def seqs(view):
    return {k: ([f[0] for f in C.anim(view, k, 'warrior', None, HERO, dense=2)], [f[0] for f in N.build(view, k, HERO)]) for k in ('attack', 'hurt', 'death')}
def gif(view, name):
    sq = seqs(view); frames = []
    labels = {'attack': 'ATAQUE', 'hurt': 'DANO', 'death': 'MORTE'}
    cw, ch = W * S, H * S
    for t in range(40):
        sh = Image.new('RGBA', (cw * 3, ch * 2 + 30), (40, 34, 52, 255))
        for c, k in enumerate(('attack', 'hurt', 'death')):
            for r in (0, 1):
                fr = sq[k][r]; n = len(fr); i = min(n - 1, t % (n + 6))
                sh.alpha_composite(fr[i].resize((cw, ch), Image.NEAREST), (c * cw, 15 + r * (ch + 0)))
            pxfont.text(sh, (c * cw + cw // 2, 3), labels[k], (240, 226, 190), center=True)
        pxfont.text(sh, (6, 18), 'ANTES', (255, 190, 150)); pxfont.text(sh, (6, ch + 18), 'DEPOIS', (160, 255, 170))
        frames.append(sh.convert('P', palette=Image.ADAPTIVE, colors=64))
    frames[0].save(f'{OUT}/{name}', save_all=True, append_images=frames[1:], duration=83, loop=0, optimize=True)
gif('right', 'guerreiro_antes_depois.gif')
# folha de verificacao das 3 vistas (so DEPOIS)
rows = []
for v in ('right', 'down', 'up'):
    for k in ('attack', 'hurt', 'death'): rows.append([f[0] for f in N.build(v, k, HERO)])
cols = max(len(r) for r in rows)
sh = Image.new('RGBA', (cols * W * 2, len(rows) * H * 2), (40, 34, 52, 255))
for r, fr in enumerate(rows):
    for i, im in enumerate(fr): sh.alpha_composite(im.resize((W * 2, H * 2), Image.NEAREST), (i * W * 2, r * H * 2))
sh.save(f'{OUT}/guerreiro_vistas_depois.png'); print('ok')
