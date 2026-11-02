"""Ícones pixel-art do HUD: poção de cura e 'voltar para a cidade' (casa). uso: python3.13 build_icons2.py"""
from PIL import Image
import os, math
OUT = os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'ico')
N, S = 24, 4
OL = (38, 22, 34, 255)


def canvas():
    return Image.new('RGBA', (N, N), (0, 0, 0, 0))


def put(im, x, y, c):
    if 0 <= x < N and 0 <= y < N:
        im.putpixel((x, y), c)


def rect(im, x0, y0, x1, y1, c):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            put(im, x, y, c)


def outline(im):
    src = im.copy()
    for y in range(N):
        for x in range(N):
            if src.getpixel((x, y))[3] == 0:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    xx, yy = x + dx, y + dy
                    if 0 <= xx < N and 0 <= yy < N and src.getpixel((xx, yy))[3] > 0:
                        im.putpixel((x, y), OL)
                        break


def potion():
    im = canvas()
    cx, cy, rx, ry = 11.5, 15.2, 7.2, 6.8
    liquid_top = 13
    for y in range(N):
        for x in range(N):
            d = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
            if d <= 1:
                if y >= liquid_top:
                    t = (y - liquid_top) / (cy + ry - liquid_top)
                    c = (int(255 - 100 * t), int(96 - 60 * t), int(104 - 60 * t), 255)
                    if y == liquid_top:
                        c = (255, 150, 150, 255)
                else:
                    c = (205, 232, 245, 255)       # vidro vazio no alto do bojo
                put(im, x, y, c)
    rect(im, 10, 6, 13, 10, (205, 232, 245, 255))          # gargalo
    rect(im, 9, 5, 14, 5, (190, 215, 232, 255))              # boca
    rect(im, 9, 2, 14, 4, (150, 98, 54, 255))                # rolha
    rect(im, 9, 2, 14, 2, (186, 128, 74, 255))
    put(im, 13, 3, (110, 70, 38, 255)); put(im, 13, 4, (110, 70, 38, 255))
    for y in range(14, 19):                                  # brilho do vidro
        put(im, 6, y, (255, 255, 255, 255)) if y in (15, 16, 17) else None
    put(im, 7, 14, (255, 255, 255, 255)); put(im, 11, 8, (255, 255, 255, 255)); put(im, 11, 7, (255, 255, 255, 255))
    for (bx, by) in ((13, 16), (15, 18), (10, 19)):          # bolhas
        put(im, bx, by, (255, 205, 205, 255))
    for x in range(8, 15):                                   # sombra na base do líquido
        put(im, x, 21, (130, 28, 44, 255))
    outline(im)
    return im.resize((N * S, N * S), Image.NEAREST)


def house():
    im = canvas()
    wall = (238, 222, 186, 255); wall2 = (205, 184, 142, 255)
    roof = (196, 70, 58, 255); roof2 = (150, 44, 44, 255)
    rect(im, 5, 11, 18, 20, wall)
    rect(im, 5, 11, 5, 20, wall2)
    rect(im, 16, 11, 18, 20, wall2)
    for i, y in enumerate(range(4, 11)):                     # telhado em triângulo
        half = 1 + i * 2
        for x in range(12 - half // 2 - 1, 12 + half // 2 + 2):
            put(im, x, y, roof if (x + y) % 5 else roof2)
    rect(im, 3, 11, 20, 11, roof2)                           # beiral
    rect(im, 15, 3, 16, 7, (150, 90, 70, 255))               # chaminé
    rect(im, 15, 3, 16, 3, (190, 120, 90, 255))
    rect(im, 10, 15, 13, 20, (112, 70, 38, 255))             # porta
    rect(im, 10, 15, 13, 15, (150, 98, 54, 255))
    put(im, 12, 18, (255, 214, 110, 255))
    rect(im, 6, 13, 8, 15, (255, 220, 120, 255))             # janela acesa
    put(im, 7, 13, (255, 245, 190, 255)); put(im, 7, 15, (200, 150, 70, 255)); rect(im, 7, 13, 7, 15, (190, 140, 60, 255)); put(im, 6, 13, (255, 245, 190, 255))
    rect(im, 4, 21, 19, 21, (96, 150, 70, 255))              # chão de grama
    outline(im)
    big = im.resize((N * S, N * S), Image.NEAREST)
    # seta dourada de retorno no canto inferior direito
    a = Image.new('RGBA', (N, N), (0, 0, 0, 0))
    g = (255, 214, 90, 255)
    for (x, y) in ((17, 17), (18, 17), (19, 17), (20, 17), (21, 17), (22, 17), (17, 18), (17, 16), (18, 19), (18, 15), (22, 18), (22, 19), (21, 20), (20, 20), (19, 20)):
        put(a, x, y, g)
    for x in range(18, 22):
        put(a, x, 20, g)
    # seta simples: "<" + traço
    a2 = Image.new('RGBA', (N, N), (0, 0, 0, 0))
    for (x, y) in ((16, 18), (17, 17), (17, 19), (18, 16), (18, 20)):
        put(a2, x, y, g)
    for x in range(17, 23):
        put(a2, x, 18, g)
    outline(a2)
    return Image.alpha_composite(big, a2.resize((N * S, N * S), Image.NEAREST))


if __name__ == '__main__':
    potion().save(os.path.join(OUT, 'v_pocao.png'))
    house().save(os.path.join(OUT, 'v_cidade.png'))
    print('ok')
