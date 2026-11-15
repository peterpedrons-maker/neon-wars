#!/usr/bin/env python3
"""Vitrine das animacoes (dense=2) de varios personagens em 3 vistas: parado, andar, ataque, dano, morte. Saida: animacoes_pixel.mp4 + .gif leve"""
import os
from PIL import Image
import chibi as C
import pxfont
import vid
from teste_clareira import OUT

CH = [('GUERREIRO', dict(cls='warrior', hat='helm', outfit='mail', metal='aco', clothes='aco', weapon='katana')),
      ('MAGO', dict(cls='mage', weapon='cajado_arcano')),
      ('LADINO', dict(cls='rogue', weapon='adaga_veneno')),
      ('CLERIGO', dict(cls='cleric', weapon='maca_ferro')),
      ('ESQUERDO', dict(cls='warrior', skin='osso', hair='g_osso', eyes='oco', hat='none', outfit='ribs', clothes='osso', metal='ferro', weapon='espada_ferro')),
      ('REI', dict(cls='rei', weapon='espada_rei'))]
CH[4] = ('ESQUELETO', CH[4][1])
VIEWS = ('down', 'right', 'up')
SEQ = [('PARADO', 'idle', 2), ('ANDAR', 'walk', 2), ('ATAQUE', 'attack', 1), ('DANO', 'hurt', 1), ('MORTE', 'death', 1)]
CW, CHh = 64, 54


def build():
    data = {}
    for n, ap in CH:
        for v in VIEWS:
            for lab, k, rep in SEQ:
                data[(n, v, k)] = [f[0] for f in C.anim(v, k, ap['cls'], None, ap, dense=2)]
    frames = []; SC = 3
    for lab, k, rep in SEQ:
        L = len(data[(CH[0][0], 'down', k)])
        for r in range(rep):
            for i in range(L):
                im = Image.new('RGBA', (CW * len(CH), CHh * len(VIEWS) + 18), (46, 62, 52, 255))
                for ci, (n, ap) in enumerate(CH):
                    for vi, v in enumerate(VIEWS):
                        s = data[(n, v, k)][i % len(data[(n, v, k)])]
                        im.alpha_composite(s.crop((4, 4, 4 + CW, 4 + CHh)), (ci * CW, vi * CHh + 18))
                    pxfont.text(im, (ci * CW + CW // 2, 10), n, (240, 226, 190), True)
                pxfont.text(im, (CW * len(CH) // 2, 2), lab, (255, 214, 120), True)
                frames.append(im.convert('RGB').resize((im.width * SC, im.height * SC), Image.NEAREST))
    return frames


if __name__ == '__main__':
    fr = build(); print(len(fr), vid.mp4(fr, os.path.join(OUT, 'animacoes_pixel.mp4'), 18))
    p = fr[0].quantize(colors=128, method=Image.MEDIANCUT, dither=Image.NONE); q = [f.quantize(palette=p, dither=Image.NONE) for f in fr]
    q[0].save(os.path.join(OUT, 'animacoes_pixel.gif'), save_all=True, append_images=q[1:], duration=55, loop=0, disposal=1, optimize=True)
    print(os.path.getsize(os.path.join(OUT, 'animacoes_pixel.gif')))
    for i in (4, 30, 60, 85, 100, 108):
        fr[min(i, len(fr) - 1)].save('/tmp/claude-0/-home-user-neon-wars/3ffd125f-a99a-599e-8554-f2b481e86fc1/scratchpad/show_%03d.png' % i)
