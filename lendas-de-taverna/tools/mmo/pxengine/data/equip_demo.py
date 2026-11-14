#!/usr/bin/env python3
"""Demo: abre o inventario, equipa cada arma (formato muda), e usa o golpe com ela."""
import os, math, random
from PIL import Image, ImageDraw
import chibi as C
from equip_gallery import label
from teste_clareira import OUT
import fx

WS = ['espada_ferro', 'katana', 'cimitarra', 'florete', 'espada_larga', 'machado', 'chamejante', 'montante_real']
TRAIL = False   # risco de corte so em skills; golpe basico sem risco (decisao do dono)
COL = {'chamejante': (255, 140, 50)}
Wd, Hd = 130, 90
OX, OY = 14, 26


def bg():
    b = Image.new('RGB', (Wd, Hd), (70, 130, 56)); d = ImageDraw.Draw(b)
    for y in range(0, Hd, 4):
        for x in range((y // 4 % 2) * 2, Wd, 4): d.point([x, y], fill=(86, 150, 66))
    d.ellipse([OX + 18, OY + 28, OX + 52, OY + 36], fill=(40, 90, 40))
    return b


def icon(d, wid, x, y, sel):
    sp = C.WEAPONS[wid]; pal = dict(sp['pal'], r='#e84a4a')
    cells, _ = C.sword_rows((6, 14), 180, min(sp['len'], 15), sp.get('guard', 3), sp.get('wide', False), sp.get('serrate', False), sp.get('glow'), sp.get('gem', False), sp.get('shape'), 'bar')
    d.rectangle([x, y, x + 11, y + 15], fill=(60, 70, 96) if not sel else (110, 90, 40), outline=(240, 210, 90) if sel else (30, 34, 50))
    for (cx, cy), c in cells.items():
        if 0 <= cx < 12 and 0 <= cy < 16:
            h = pal.get(c, '#ff00ff'); d.point([x + cx, y + cy], fill=tuple(int(h[i:i + 2], 16) for i in (1, 3, 5)))


def inv(im, sel):
    d = ImageDraw.Draw(im)
    d.rectangle([0, Hd - 20, Wd, Hd], fill=(24, 28, 44))
    for i, w in enumerate(WS): icon(d, w, 3 + i * 16, Hd - 18, i == sel)


def run():
    frames = []
    random.seed(3)
    for si, wid in enumerate(WS):
        app = dict(cls='warrior', weapon=wid, hat='helm', outfit='mail', metal='aco', clothes='aco')
        seq = C.anim('right', 'attack', 'warrior', None, app)
        pal = C.WEAPONS[wid]['pal']; hexc = pal['A'].lstrip('#'); tc = tuple(int(hexc[i:i + 2], 16) for i in (0, 2, 4))
        # 1) equipando: cursor no inventario + brilho
        for k in range(8):
            b = bg(); inv(b, si)
            img = seq[0][0]
            if k >= 3:
                ov = fx.layer() if False else None
            b.paste(img.convert('RGB'), (OX, OY), img)
            d = ImageDraw.Draw(b)
            if 2 <= k <= 6:
                r = (k - 1) * 3
                for a in range(0, 360, 30):
                    px = OX + 30 + math.cos(math.radians(a + k * 12)) * r; py = OY + 14 + math.sin(math.radians(a + k * 12)) * r * .7
                    d.point([px, py], fill=(255, 245, 160)); d.point([px + 1, py], fill=(255, 220, 90))
            d.ellipse([91, OY + 22, 107, OY + 30], fill=(40, 90, 40)); d.ellipse([91, OY + 12, 105, OY + 28], fill=(110, 200, 90), outline=(40, 120, 50))
            label(b, (Wd // 2, 3), ('EQUIPANDO: ' if k < 7 else 'EQUIPADO: ') + wid.replace('_', ' ').upper(), (255, 240, 200), center=True)
            frames.append(b)
        # 2) golpe com rastro
        trail = []
        for k in [0, 1, 2, 3, 4, 5, 6, 6, 7, 9, 9, 9]:
            img, tip, bh = seq[k]
            b = bg(); inv(b, si)
            d = ImageDraw.Draw(b)
            if tip is not None: trail.append((tip[0] + OX, tip[1] + OY))
            trail = trail[-5:]
            if not bh:
                pass
            b.paste(img.convert('RGB'), (OX, OY), img)
            d = ImageDraw.Draw(b)
            for j in (range(1, len(trail)) if TRAIL else []):
                d.line([trail[j - 1], trail[j]], fill=tc, width=2 if j > len(trail) // 2 else 1)
            if True:
                ex = 98
                d.ellipse([ex - 8, OY + 22, ex + 8, OY + 30], fill=(40, 90, 40))
                d.ellipse([ex - 7, OY + 12, ex + 7, OY + 28], fill=(255, 255, 255) if k in (5, 6) else (110, 200, 90), outline=(40, 120, 50))
                d.point([ex - 3, OY + 18], fill=(0, 0, 0)); d.point([ex + 2, OY + 18], fill=(0, 0, 0))
                if k in (6, 7): fx.draw_number(b, ex - 6, OY - 4 - (k - 6) * 3, str(40 + si * 7)) if False else None
            if k >= 5:
                label(b, (98, OY - 6 - (k - 5)), str(40 + si * 7), (255, 224, 74), center=True)
            label(b, (Wd // 2, 3), wid.replace('_', ' ').upper(), (255, 240, 200), center=True)
            frames.append(b)
    big = [f.resize((Wd * 4, Hd * 4), Image.NEAREST) for f in frames]
    p = big[0].quantize(colors=220, method=Image.MEDIANCUT, dither=Image.NONE)
    q = [f.quantize(palette=p, dither=Image.NONE) for f in big]
    q[0].save(os.path.join(OUT, 'equip_demo_troca_arma.gif'), save_all=True, append_images=q[1:], duration=80, loop=0, disposal=1)
    return len(q)


if __name__ == '__main__':
    print(run())
