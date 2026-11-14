#!/usr/bin/env python3
"""Troca de equipamento em tempo real: o guerreiro golpeia com cada espada do catalogo (visual muda so trocando o id)."""
import os
from PIL import Image, ImageDraw
import chibi as C
from equip_gallery import label
from teste_clareira import OUT
import fx

SWORDS = ['espada_ferro', 'espada_aco', 'espada_longa', 'montante', 'espada_dourada', 'espada_chamas', 'espada_gelo', 'espada_sombria', 'serra_cruel']


def run():
    frames = []
    for wid in SWORDS:
        app = dict(cls='warrior', weapon=wid)
        seq = C.anim('right', 'attack', 'warrior', None, app)
        order = [0, 0, 1, 2, 3, 4, 5, 6, 6, 7, 9, 9]
        for k in order:
            img, tip, bh = seq[k]
            bg = Image.new('RGB', (110, 80), (70, 130, 56))
            d = ImageDraw.Draw(bg)
            for y in range(0, 80, 4):
                for x in range((y // 4 % 2) * 2, 110, 4): d.point([x, y], fill=(86, 150, 66))
            d.ellipse([30, 62, 64, 70], fill=(40, 90, 40))
            bg.paste(img.convert('RGB'), (5, 40 - 12 + 4 - 6 + 4), img)
            # recorte e brilho especial
            lab = wid.replace('_', ' ').upper()
            label(bg, (55, 4), lab, (255, 240, 200), center=True)
            frames.append(bg.resize((440, 320), Image.NEAREST))
    pal = frames[0].quantize(colors=200, method=Image.MEDIANCUT, dither=Image.NONE)
    q = [f.quantize(palette=pal, dither=Image.NONE) for f in frames]
    q[0].save(os.path.join(OUT, 'equip_troca_espada.gif'), save_all=True, append_images=q[1:], duration=90, loop=0, disposal=1)
    return len(frames)


if __name__ == '__main__':
    print(run())
