#!/usr/bin/env python3
"""Renderiza os MAPAS REAIS do jogo (chao + props do atlas Pixel Crawler ja existentes em mmo/assets) em pixel art no mesmo grid dos
personagens chibi: tudo reduzido 2x (BOX) -> 1 pixel nativo; tela nativa 195x423 mostrada a 2x (390x846). Escala coerente com o jogo real."""
import json, os
import numpy as np
from PIL import Image, ImageDraw

ROOT = '/home/user/neon-wars/lendas-de-taverna/mmo/assets/'
FILES = {'town': ('town.json', 'town_atlas.json', 'town_ground.png', 'town_atlas.png'), 'zone1': ('zone1.json', 'atlas.json', 'zone1_ground.png', 'atlas.png'),
         'zone1_gob': ('zone1_gob.json', 'atlas_gob.json', 'zone1_gob_ground.png', 'atlas_gob.png'), 'zone_cripta': ('zone_cripta.json', 'atlas_cripta.json', 'zone_cripta_ground.png', 'atlas_cripta.png'),
         'zone_cripta2': ('zone_cripta2.json', 'atlas_cripta2.json', 'zone_cripta2_ground.png', 'atlas_cripta2.png'), 'zone_esgoto': ('zone_esgoto.json', 'atlas_esgoto.json', 'zone_esgoto_ground.png', 'atlas_esgoto.png')}
NW, NH = 195, 423
_c = {}


def half_rgba(img):
    a = np.asarray(img.convert('RGBA'), dtype=np.float32)
    h, w = (a.shape[0] // 2) * 2, (a.shape[1] // 2) * 2
    a = a[:h, :w]; al = a[..., 3:4] / 255.0
    pm = np.concatenate([a[..., :3] * al, a[..., 3:4]], axis=2)
    pm = pm.reshape(h // 2, 2, w // 2, 2, 4).mean(axis=(1, 3))
    alpha = pm[..., 3:4]; rgb = np.where(alpha > 1, pm[..., :3] / np.maximum(alpha / 255.0, 1e-3), 0)
    out = np.concatenate([np.clip(rgb, 0, 255), np.where(alpha > 110, 255, 0)], axis=2).astype(np.uint8)
    im = Image.fromarray(out, 'RGBA')
    rgbim = im.convert('RGB').quantize(colors=40, method=Image.MEDIANCUT, dither=Image.NONE).convert('RGB')
    q = rgbim.convert('RGBA'); q.putalpha(im.split()[3]); return q


def half_rgb(img):
    a = np.asarray(img.convert('RGB'), dtype=np.float32); h, w = (a.shape[0] // 2) * 2, (a.shape[1] // 2) * 2
    a = a[:h, :w].reshape(h // 2, 2, w // 2, 2, 3).mean(axis=(1, 3))
    return Image.fromarray(a.astype(np.uint8), 'RGB').quantize(colors=56, method=Image.MEDIANCUT, dither=Image.NONE).convert('RGB')


class MapV:
    def __init__(self, key):
        j, a, g, at = FILES[key]
        self.m = json.load(open(ROOT + j)); self.fr = json.load(open(ROOT + a))
        self.atlas = Image.open(ROOT + at).convert('RGBA'); self.ground = half_rgb(Image.open(ROOT + g)); self.cache = {}

    def frame(self, fid):
        if fid not in self.cache:
            x, y, w, h, ax, ay = self.fr[fid]
            self.cache[fid] = (half_rgba(self.atlas.crop((x, y, x + w, y + h))), ax // 2, ay // 2)
        return self.cache[fid]

    def render(self, cam, chars=(), shadow=True):
        """cam = centro da camera em coords do mapa; chars = [(sprite RGBA 72x64, mapx, mapy)] (pes do sprite em (36,38))"""
        cx, cy = cam[0] // 2, cam[1] // 2
        x0, y0 = int(cx - NW // 2), int(cy - NH // 2)
        world = Image.new('RGBA', (NW, NH), (20, 20, 30, 255))
        world.paste(self.ground.crop((x0, y0, x0 + NW, y0 + NH)), (0, 0))
        items = []
        for p in self.m['props']:
            t = p.get('t')
            if t == 'flat' and p['id'] in self.fr:
                fi, ax, ay = self.frame(p['id']); world.alpha_composite(fi, (p['x'] // 2 - ax - x0, p['y'] // 2 - ay - y0))
            elif t == 'p' and p['id'] in self.fr: items.append((p['y'], 'p', p))
            elif t == 'portal' and p.get('fr') and p['fr'][0] in self.fr: items.append((p['y'], 'p', dict(p, id=p['fr'][0])))
        for (spr_, mx, my) in chars: items.append((my, 'c', (spr_, mx, my)))
        for y, kind, p in sorted(items, key=lambda t: t[0]):
            if kind == 'p':
                fi, ax, ay = self.frame(p['id']); px, py = p['x'] // 2 - ax - x0, p['y'] // 2 - ay - y0
                if -fi.width < px < NW and -fi.height < py < NH: world.alpha_composite(fi, (px, py))
            else:
                spr_, mx, my = p; fx, fy = mx // 2 - x0, my // 2 - y0
                if shadow:
                    ov = Image.new('RGBA', (NW, NH), (0, 0, 0, 0)); ImageDraw.Draw(ov).ellipse([fx - 9, fy - 2, fx + 9, fy + 3], fill=(0, 0, 0, 90)); world.alpha_composite(ov)
                world.alpha_composite(spr_, (fx - 36, fy - 38))
        return world, (x0, y0)
