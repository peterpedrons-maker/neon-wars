#!/usr/bin/env python3
"""REPLAY FIEL DO JOGO REAL: o motor do jogo (index.html, update(dt)) roda sem tela e grava posicao/estado de cada ator a 30fps (trace.js);
aqui so TROCAMOS O GRAFICO: sprites chibi pixel art + mapa pixel art. Velocidades, alcances, tempos de ataque, avisos, danos = do jogo.
Uso: python3 replay_pixel.py trace_boss.json saida.mp4 [max_frames]"""
import json, math, os, sys
from PIL import Image, ImageDraw
import mapview as MV
import jogo_pixel2 as J2
import acao_pixel as AP
import jogo_pixel as J
import icons_pixel as IC
import pxfont, vid
from teste_clareira import OUT

NW, NH, SC = MV.NW, MV.NH, 2
VIEW = {0: 'up', 1: 'left', 2: 'down', 3: 'right'}
RAR = ['comum', 'incomum', 'raro', 'epico', 'lendario']
RARC = {'comum': (200, 200, 210), 'incomum': (90, 230, 110), 'raro': (80, 160, 255), 'epico': (190, 110, 255), 'lendario': (255, 170, 50)}
ICON = {'comum': 'coin', 'incomum': 'gem', 'raro': 'katana', 'epico': 'ring', 'lendario': 'amulet'}


def hexc(s, d=(255, 255, 255)):
    try:
        s = s.lstrip('#'); return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))
    except Exception: return d


def mob_sprite(name):
    n = name or ''
    if n.startswith('Rei Esquecido'): return 'REI'
    if n.startswith('Guarda'): return 'esqueleto'
    if n.startswith('Cultista'): return 'cultista'
    if n.startswith('Espectro') or n.startswith('Alma'): return 'espectro'
    if n.startswith('Zumbi'): return 'zumbi'
    if n.startswith('Gárgula') or n.startswith('Gargula'): return 'gargula'
    if n.startswith('Goblin'): return 'goblin'
    if n.startswith('Esqueleto'): return 'esqueleto'
    if n.startswith('Javali'): return 'javali'
    if n.startswith('Rato'): return 'rato'
    if n.startswith('Morcego'): return 'morcego'
    return 'esqueleto'


def mimg(m, F):
    name = mob_sprite(m.get('name')); v = VIEW.get(int(m.get('row', 2)), 'down'); st = m.get('state', 'idle'); a = m.get('act') or {}
    if name == 'REI':
        L = {'attack': len(AP.seq('r', 'attack', 'down')), 'cast': len(AP.seq('r', 'cast', 'down')), 'walk': 16, 'idle': 12}
        if m.get('dead'): im = AP.img('r', 'death', v, int(min(1, (m.get('deadT') or 0) / 1.2) * 10))
        elif st == 'atk':
            u = min(.999, a.get('t', 0) / max(.01, a.get('dur', .6))); im = AP.img('r', 'attack' if a.get('dur', .6) < 1.0 else 'cast', v, int(u * (L['attack'] if a.get('dur', .6) < 1.0 else L['cast'])))
        elif st == 'walk': im = AP.img('r', 'walk', v, int((m.get('animT') or 0) * 16) % 16)
        elif st == 'hurt': im = AP.img('r', 'hurt', v, 0)
        else: im = AP.img('r', 'idle', v, int(F['t'] * 10) % 12)
        return im
    seqk = lambda k: J.spr(name, k, 'right' if v in ('left', 'right') else v)
    def pick(k, i):
        s = seqk(k); im = s[max(0, min(len(s) - 1, i)) if k in ('death', 'hurt', 'attack') else i % len(s)]
        return im.transpose(Image.FLIP_LEFT_RIGHT) if v == 'left' else im
    if m.get('dead'): return pick('death', int(min(1, (m.get('deadT') or 0) / .8) * (len(seqk('death')) - 1)))
    if st == 'atk': u = min(.999, a.get('t', 0) / max(.01, a.get('dur', .8))); return pick('attack', int(u * len(seqk('attack'))))
    if st == 'walk': return pick('walk', int((m.get('animT') or 0) * 14))
    if st == 'hurt': return pick('hurt', 1)
    return pick('idle', int(F['t'] * 10))


def himg(h, F):
    v = VIEW.get(int(h.get('row', 2)), 'down'); st = h.get('state', 'idle'); a = h.get('act') or {}
    if st == 'ko': return AP.img('h', 'hurt', v, 3)
    if h.get('dod'): return AP.tint(AP.img('h', 'walk', v, int(h.get('animT', 0) * 24) % 16), (180, 220, 255), .35)
    if st == 'atk':
        u = min(.999, a.get('t', 0) / max(.01, a.get('dur', .5))); return AP.img('h', 'attack', v, int(u * len(AP.seq('h', 'attack', v))))
    if st == 'walk' and h.get('run'): return AP.img('h', 'run', v, int(h.get('animT', 0) * 20.8) % 16)
    if st == 'walk': return AP.img('h', 'walk', v, int(h.get('animT', 0) * 20.8) % 16)
    return AP.img('h', 'idle', v, int(F['t'] * 10) % 12)


def render(frames, mapkey='zone_cripta2', n=None, zone='CRIPTA DO REI'):
    mv = J2.SCENE_CACHE.setdefault(mapkey, MV.MapV(mapkey)); out = []
    cam = None; ghosts = []
    for fi, F in enumerate(frames[:n]):
        h = F['hero']
        if cam is None: cam = [h['x'], h['y']]
        cam[0] += (h['x'] - cam[0]) * .12; cam[1] += (h['y'] - 28 - cam[1]) * .12
        chars = []
        himage = himg(h, F)
        if (h.get('flash') or 0) > 0 and int(F['t'] * 30) % 2: himage = AP.tint(himage, (255, 255, 255), .7)
        for m in F['mobs']:
            if m.get('dead') and (m.get('deadT') or 0) > 2.2: continue
            im = mimg(m, F)
            if (m.get('flash') or 0) > 0 and int(F['t'] * 30) % 2: im = AP.tint(im, (255, 255, 255), .7)
            if (m.get('name') or '').startswith('Alma'): a = im.split()[3].point(lambda v: 150 if v else 0); im = AP.tint(im, (120, 200, 255), .5); im.putalpha(a)
            if m.get('dead') and (m.get('deadT') or 0) > 1.2: k = max(0, 1 - ((m['deadT']) - 1.2) / 1.0); im = im.copy(); im.putalpha(im.split()[3].point(lambda v, q=k: int(v * q)))
            chars.append((im, m['x'], m['y']))
        chars.append((himage, h['x'], h['y']))
        im, (x0, y0) = mv.render((cam[0], cam[1]), chars)
        N = lambda mx, my: (int(mx) // 2 - x0, int(my) // 2 - y0)
        ov = Image.new('RGBA', (NW, NH), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
        for z in F['zones']:                                          # avisos de area (do jogo: warn/t)
            k = max(0, min(1, z.get('t', 0) / max(.01, z.get('warn', 1)))); col = hexc(z.get('col', '#ff3a2a'), (255, 60, 50)); a_ = int(70 + 110 * k)
            cx, cy = N(z['x'], z['y'])
            if z.get('shape') == 'circle':
                r = z['r'] / 2; d.ellipse([cx - r, cy - r * .6, cx + r, cy + r * .6], fill=col + (int(a_ * .35),), outline=col + (a_,))
                rr = r * k; d.ellipse([cx - rr, cy - rr * .6, cx + rr, cy + rr * .6], outline=(255, 210, 120, a_))
            elif z.get('shape') == 'line':
                ang = z.get('a', z.get('ang', 0)); L = z.get('len', 300) / 2; w = z.get('w', 40) / 4
                dx_, dy_ = math.cos(ang), math.sin(ang); nx, ny = -dy_, dx_
                pts = [(cx + nx * w, cy + ny * w), (cx + dx_ * L + nx * w, cy + dy_ * L + ny * w), (cx + dx_ * L - nx * w, cy + dy_ * L - ny * w), (cx - nx * w, cy - ny * w)]
                d.polygon(pts, fill=col + (int(a_ * .35),), outline=col + (a_,))
        for q in F['loot']:
            px, py = N(q['x'], q['y']); rar = RAR[int(q['rar'])] if isinstance(q.get('rar'), (int, float)) and 0 <= int(q['rar']) < 5 else 'raro'; c = RARC[rar]
            for k in range(0, 40): d.line([px, py - 4 - k, px, py - 4 - k], fill=c + (max(0, 150 - k * 4),)); d.line([px - 1, py - 4 - k, px - 1, py - 4 - k], fill=c + (max(0, 80 - k * 4),)); d.line([px + 1, py - 4 - k, px + 1, py - 4 - k], fill=c + (max(0, 80 - k * 4),))
        im.alpha_composite(ov)
        d = ImageDraw.Draw(im)
        for q in F['mp'] + F['pr']:
            px, py = N(q['x'], q['y'] - 18); c = hexc(q.get('col', '#b890ff'), (180, 130, 255)); d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=c); d.ellipse([px - 1, py - 1, px + 1, py + 1], fill=(255, 255, 255))
        for q in F['loot']:
            px, py = N(q['x'], q['y']); rar = RAR[int(q['rar'])] if isinstance(q.get('rar'), (int, float)) and 0 <= int(q['rar']) < 5 else 'raro'
            im.alpha_composite(IC.get(ICON[rar]), (px - 8, py - 18 + int(2 * math.sin(F['t'] * 8))))
        for m in F['mobs']:
            if m.get('dead') or m.get('maxhp', 0) <= 0: continue
            if (m.get('name') or '').startswith('Alma') or m.get('boss'): continue
            px, py = N(m['x'], m['y'] - 78); J2.mini_hp(im, px, py, max(0, m['hp'] / m['maxhp']))
        for fl in F['fl']:
            px, py = N(fl['x'], fl['y']); col = hexc(fl.get('col', '#ffffff')); k = 2 if (fl.get('size') or 9) >= 11 else 1
            J2.T(im, (px, py - 8), str(fl.get('t', '')).replace('−', '-'), col, True, k)
        hp = h['hp'] / max(1, h['maxhp']); boss = ('REI ESQUECIDO', F['boss']['hp'] / max(1, F['boss']['maxhp'])) if F.get('boss') else None
        J2.hud(im, zone, hp, ['Lute!'], boss=boss)
        out.append(im.convert('RGB').resize((NW * SC, NH * SC), Image.NEAREST))
    return out


if __name__ == '__main__':
    src, dst = sys.argv[1], sys.argv[2]; n = int(sys.argv[3]) if len(sys.argv) > 3 else None
    d = json.load(open(src)); fr = render(d['frames'], d.get('map', 'zone_cripta2'), n)
    print(len(fr), vid.mp4(fr, dst, 30))
    fr[min(len(fr) - 1, 100)].save(dst.replace('.mp4', '_f1.png')); fr[min(len(fr) - 1, 400)].save(dst.replace('.mp4', '_f2.png'))
