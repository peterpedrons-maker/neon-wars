#!/usr/bin/env python3
"""GIGANTE DAS COLINAS (esboço, humanoide): corpo inteiro, uma massa só, mesmo motor/paleta do colosso.py.
Uso: python3 gigante.py sheet out.png"""
import sys, math
import numpy as np
from PIL import Image
import fauna as FA
import colosso as CO
R, hx = FA.R, FA.hx
PAL = dict(CO.PAL); FLAT = dict(CO.FLAT)
GW, GH = 260, 420

def giant(view='d', P=None):
    P = P or {}
    FA.W, FA.H = GW, GH
    c = FA.Cv(); c.contact = False
    cx = GW // 2; fy = 408
    if view == 's':
        # PERFIL (olha para a direita): tronco curvado, braço de perto pendendo à frente, perna de longe atras
        for far, sg in ((True, -1), (False, 1)):
            hx0 = cx - 6 + sg * 10
            c.cap(hx0, 214, hx0 + sg * 10, 296, 27, 21, 'fur', far)                      # coxa
            c.ell(hx0 + sg * 10, 300, 24, 22, 'fur', far)                                # joelho
            c.cap(hx0 + sg * 10, 304, hx0 + sg * 12, 388, 20, 15, 'body', far)           # canela
            c.ell(hx0 + sg * 12 + 14, fy - 12, 36, 13, 'skin', far)                      # pe (dedos para a frente)
            for k in range(3): c.cap(hx0 + sg * 12 + 34 + k * 3, fy - 15 + k * 5, hx0 + sg * 12 + 46 + k * 3, fy - 9 + k * 5, 6, 4.5, 'skin', far)
            c.cap(hx0 + sg * 12 + 48, fy - 12, hx0 + sg * 12 + 54, fy - 8, 2.4, 1.2, 'horn', far)
        c.cap(cx + 12, 100, cx + 44, 196, 26, 20, 'body', True); c.cap(cx + 44, 196, cx + 52, 262, 20, 15, 'body', True); c.ell(cx + 56, 276, 20, 24, 'skin', True)
        c.ell(cx - 14, 222, 58, 34, 'fur')                                                # tanga
        c.ell(cx - 6, 150, 58, 76, 'body')                                                # torso
        c.ell(cx - 30, 150, 36, 70, 'fur')                                                # costas peludas
        c.ell(cx + 10, 196, 44, 38, 'body')                                               # barriga
        c.cap(cx - 6, 92, cx + 26, 62, 34, 22, 'fur')                                     # pescoco/juba
        c.ell(cx + 4, 98, 40, 30, 'stone'); c.ell(cx - 8, 94, 34, 24, 'fur')              # ombreira
        c.cap(cx + 6, 106, cx + 34, 190, 28, 22, 'body')                                  # braco de perto
        c.cap(cx + 34, 190, cx + 46, 262, 22, 17, 'body')
        c.ell(cx + 50, 276, 22, 26, 'skin')
        for k in range(4): c.cap(cx + 40 + k * 7, 288, cx + 42 + k * 7, 306, 4.6, 3.2, 'skin')
        c.ell(cx + 34, 50, 34, 31, 'body'); c.ell(cx + 52, 62, 22, 18, 'skin')            # cabeca e focinho
        c.cap(cx + 20, 22, cx + 14, -4, 8, 3, 'horn'); c.cap(cx + 40, 22, cx + 54, -2, 7, 3, 'horn')
        c.cap(cx + 58, 72, cx + 62, 52, 4, 2, 'tusk')
        c.ell(cx + 20, 80, 22, 14, 'fur')
        eye = (cx + 46, 46)
    else:
        back = (view == 'u'); bm = 'far' if back else 'fur'
        for sg in (-1, 1):
            x0 = cx + sg * 34
            c.cap(x0, 214, x0 + sg * 3, 296, 30, 23, bm)                                   # coxa
            c.ell(x0 + sg * 3, 300, 25, 21, bm)                                            # joelho
            c.cap(x0 + sg * 3, 304, x0 + sg * 4, 388, 19, 15, 'body')                      # canela
            c.ell(x0 + sg * 6, fy - 12, 34, 13, 'skin')                                    # pe
            if not back:
                for k in range(-2, 3): c.cap(x0 + sg * 6 + k * 12, fy - 10, x0 + sg * 6 + k * 13, fy - 1, 6.4, 5, 'skin')
                for k in (-2, -1, 0, 1, 2): c.cap(x0 + sg * 6 + k * 13, fy - 3, x0 + sg * 6 + k * 13, fy + 1, 2.4, 1.4, 'horn')
        c.ell(cx, 220, 76, 36, bm)                                                         # tanga de pele
        for i in range(9): c.cap(cx - 64 + i * 16, 238, cx - 66 + i * 16 + (i % 2) * 3, 262 + (i % 3) * 8, 5, 1.2, bm)
        c.ell(cx, 156, 78, 78, 'body' if not back else 'far')                               # torso largo
        c.ell(cx, 196, 60, 44, 'body' if not back else 'far')                               # barriga
        c.ell(cx, 100, 54, 22, 'fur')                                                       # trapezio / pescoco
        for sg in (-1, 1):
            c.ell(cx + sg * 80, 106, 38, 32, 'stone'); c.ell(cx + sg * 78, 98, 34, 26, bm)  # ombreiras
            c.cap(cx + sg * 88, 118, cx + sg * 100, 188, 29, 23, 'body')                     # braco
            c.ell(cx + sg * 100, 188, 24, 22, bm)                                            # cotovelo
            c.cap(cx + sg * 100, 192, cx + sg * 96, 262, 22, 17, 'body')                     # antebraco
            for i in range(4): c.cap(cx + sg * 96 - 10 + i * 7, 240 + (i % 2) * 3, cx + sg * 96 - 10 + i * 7, 250, 5.5, 4, bm)  # pelos
            c.ell(cx + sg * 94, 282, 25, 27, 'skin')                                         # mao
            if not back:
                for k in range(4): c.cap(cx + sg * 94 - 14 + k * 9, 292, cx + sg * 94 - 15 + k * 9, 316, 5.6, 4, 'skin')
                c.cap(cx + sg * 94 - sg * 22, 280, cx + sg * 94 - sg * 14, 304, 5, 4, 'skin')
        # cabeca pequena (1/7 da altura)
        c.ell(cx, 56, 36, 34, 'fur'); c.ell(cx, 62, 28, 28, 'body' if not back else 'far')
        for sg in (-1, 1):
            c.cap(cx + sg * 26, 38, cx + sg * 44, 14, 8, 4.5, 'horn'); c.cap(cx + sg * 44, 14, cx + sg * 46, -10, 4.5, 1.2, 'horn')
        if not back:
            c.ell(cx, 78, 18, 10, 'skin'); c.ell(cx, 88, 20, 9, 'body')
            for sg in (-1, 1): c.cap(cx + sg * 11, 88, cx + sg * 13, 76, 2.8, 1.4, 'tusk')
            for i in range(4): c.cap(cx - 18 + i * 12, 94, cx - 19 + i * 12, 106 + (i % 2) * 4, 3, 1, 'fur')
        eye = (cx - 11, 54)
    # musgo e pedras
    c.ell(cx - 52 if view != 's' else cx - 30, 120, 12, 8, 'moss'); c.ell(cx + 40 if view != 's' else cx + 10, 168, 9, 6, 'moss'); c.ell(cx - 22 if view != 's' else cx - 4, 232, 8, 5, 'stone')
    if view != 'u':
        for (rx, ry) in ((-30, 130), (22, 140), (-4, 160), (36, 118), (-46, 176), (14, 186)):
            if view == 's': rx = rx * .5 - 4
            for dx_, dy_ in ((0, 0), (1, 0), (0, 1), (-1, 0), (0, -1)): c.dot(cx + rx + dx_, ry + dy_, FLAT['rune'])
            c.dot(cx + rx, ry, FLAT['eye2'])
        eyes = [eye] if view == 's' else [(cx - 13, 56), (cx + 13, 56)]
        for ex, ey in eyes:
            for dx_ in (-1, 0, 1, 2):
                for dy_ in (0, 1): c.dot(ex + dx_, ey + dy_, FLAT['eye'])
            c.dot(ex, ey, FLAT['eye2'])
        # pelos longos pendurados nos antebracos e ombros
        if view != 's':
            for sg in (-1, 1):
                for k in range(5): c.cap(cx + sg * (110 - k * 5), 150 + k * 4, cx + sg * (114 - k * 5), 176 + k * 6, 3.2, 1, 'fur')
    return c.render(PAL, FLAT)

def sheet(path, hero_png):
    V = [giant(v) for v in ('d', 's', 'u')]
    pad = 20
    S = Image.new('RGBA', (GW * 3 + 150 + pad * 6, GH + pad * 2), (92, 120, 84, 255))
    for i, im in enumerate(V): S.alpha_composite(im, (pad + i * (GW + pad), pad))
    try:
        H = Image.open(hero_png).convert('RGBA'); S.alpha_composite(H, (GW * 3 + pad * 4, GH + pad - H.height))
    except Exception as e: print('hero', e)
    S.save(path); print(path, S.size)

if __name__ == '__main__':
    sheet(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else '')
