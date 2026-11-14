#!/usr/bin/env python3
"""Combate animado no mapa real: inimigos ANDAM ate o heroi, atacam, apanham (flash+recuo), morrem e DROPAM item com feixe de luz por raridade;
o heroi persegue e ataca sozinho (auto). Particulas: poeira, faiscas, numeros. Saida: combate_pixel.gif"""
import math, os, random
from PIL import Image, ImageDraw
import mapview as MV
import jogo_pixel2 as J2
from jogo_pixel import spr
import icons_pixel as IC
import pxfont
from teste_clareira import OUT

NW, NH, SC = MV.NW, MV.NH, 2
RARC = {'comum': (200, 200, 210), 'incomum': (90, 230, 110), 'raro': (80, 160, 255), 'epico': (190, 110, 255), 'lendario': (255, 170, 50)}


def S(name, kind, view, i):
    v = 'right' if view in ('left', 'right') else view
    seq = spr(name, kind, v); im = seq[i % len(seq)]
    return im.transpose(Image.FLIP_LEFT_RIGHT) if view == 'left' else im


def facing(dx, dy):
    if abs(dx) > abs(dy) * 1.3: return 'right' if dx > 0 else 'left'
    return 'down' if dy > 0 else 'up'


class Mob:
    def __init__(s, name, x, y, hp, speed, rng, dmg, fly=0, loot=('comum', 'coin')):
        s.name, s.x, s.y, s.hp, s.max, s.sp, s.rng, s.dmg, s.fly, s.loot = name, x, y, hp, hp, speed, rng, dmg, fly, loot
        s.st = 'walk'; s.t = 0; s.cd = random.randint(0, 20); s.hitdone = False; s.fade = 0; s.view = 'down'; s.flash = 0; s.kx = 0.0; s.ky = 0.0; s.off = random.randint(0, 11)

    def seq_len(s, kind): return len(spr(s.name, kind, 'right' if s.view in ('left', 'right') else s.view))


def run(frames_n=220):
    random.seed(9)
    mv = J2.SCENE_CACHE.setdefault('zone_cripta', MV.MapV('zone_cripta')); sx, sy = mv.m['start']
    H = dict(x=float(sx), y=float(sy - 60), hp=1.0, st='idle', t=0, view='up', flash=0, hurt=0, target=None, hitdone=False, cd=0)
    mobs = [Mob('esqueleto', sx - 80, sy - 420, 3, 1.3, 46, .09), Mob('zumbi', sx + 60, sy - 520, 4, .8, 42, .12), Mob('morcego', sx + 20, sy - 600, 2, 2.0, 40, .06, fly=1, loot=('incomum', 'gem')),
            Mob('esqueleto', sx + 110, sy - 700, 3, 1.3, 46, .09, loot=('raro', 'katana')), Mob('slime', sx - 40, sy - 780, 2, 1.1, 36, .05, loot=('comum', 'potion:green'))]
    loot = []; parts = []; nums = []; frames = []; shake = (0, 0)
    for f in range(frames_n):
        shake = (0, 0)
        # ---- heroi (auto) ----
        alive = [m for m in mobs if m.st != 'dead']
        tgt = min(alive, key=lambda m: math.hypot(m.x - H['x'], m.y - H['y'])) if alive else None
        if H['st'] == 'hurt':
            H['t'] += 1
            if H['t'] >= len(spr('heroi', 'hurt', 'up')): H['st'] = 'idle'; H['t'] = 0
        elif H['st'] == 'attack':
            H['t'] += 1; n = len(spr('heroi', 'attack', 'right' if H['view'] in ('left', 'right') else H['view']))
            if H['t'] >= 10 and not H['hitdone']:
                H['hitdone'] = True
                for m in alive:
                    if math.hypot(m.x - H['x'], m.y - H['y']) < 82:
                        m.hp -= 1; m.flash = 4; d = math.hypot(m.x - H['x'], m.y - H['y']) or 1; m.kx = (m.x - H['x']) / d * 5; m.ky = (m.y - H['y']) / d * 5
                        nums.append([m.x, m.y - 100, str(32 + random.randint(0, 9)), (255, 224, 74), 0]); shake = (1, 1)
                        for _ in range(7): parts.append([m.x, m.y - 40, random.uniform(-3, 3), random.uniform(-4, -1), 8, (255, 240, 160)])
                        if m.hp <= 0: m.st = 'dead'; m.t = 0
                        elif m.st != 'dead': m.st = 'hurt'; m.t = 0
            if H['t'] >= n: H['st'] = 'idle'; H['t'] = 0; H['cd'] = 6
        else:
            H['cd'] = max(0, H['cd'] - 1)
            if tgt:
                dx, dy = tgt.x - H['x'], tgt.y - H['y']; d = math.hypot(dx, dy); H['view'] = facing(dx, dy)
                if d < 78 and H['cd'] == 0: H['st'] = 'attack'; H['t'] = 0; H['hitdone'] = False
                elif d >= 70:
                    H['st'] = 'walk'; H['x'] += dx / d * 2.4; H['y'] += dy / d * 2.4; H['t'] += 1
                    if f % 4 == 0: parts.append([H['x'], H['y'], random.uniform(-.5, .5), -.6, 7, (190, 180, 160)])
                else: H['st'] = 'idle'; H['t'] += 1
            else: H['st'] = 'idle'; H['t'] += 1
        # ---- inimigos ----
        for m in mobs:
            if m.st == 'dead':
                m.t += 1; ln = m.seq_len('death')
                if m.t == ln and not any(l['m'] is m for l in loot): loot.append(dict(m=m, x=m.x, y=m.y, t=0, r=m.loot[0], icon=m.loot[1], fly=False))
                if m.t >= ln: m.fade += 1
                continue
            dx, dy = H['x'] - m.x, H['y'] - m.y; d = math.hypot(dx, dy) or 1
            if m.st == 'hurt':
                m.t += 1; m.x += m.kx; m.y += m.ky; m.kx *= .6; m.ky *= .6
                if m.t >= m.seq_len('hurt'): m.st = 'walk'; m.t = 0
            elif m.st == 'attack':
                m.t += 1; ln = m.seq_len('attack')
                if m.t == int(ln * .55) and d < m.rng + 24 and H['st'] != 'hurt':
                    H['hp'] = max(.05, H['hp'] - m.dmg); H['st'] = 'hurt'; H['t'] = 0; nums.append([H['x'], H['y'] - 90, str(int(m.dmg * 300)), (255, 120, 110), 0]); shake = (1, 0)
                    for _ in range(6): parts.append([H['x'], H['y'] - 30, random.uniform(-3, 3), random.uniform(-3, -.5), 8, (255, 90, 80)])
                if m.t >= ln: m.st = 'walk'; m.t = 0; m.cd = 30
            else:
                m.view = facing(dx, dy)
                if d > m.rng: m.x += dx / d * m.sp; m.y += dy / d * m.sp; m.t += 1
                    # poeira
                elif m.cd <= 0: m.st = 'attack'; m.t = 0
                else: m.t += 1
                m.cd -= 1
                if m.st == 'walk' and f % 5 == 0 and not m.fly: parts.append([m.x, m.y, random.uniform(-.4, .4), -.5, 6, (170, 160, 150)])
            if m.flash: m.flash -= 1
        # ---- montar ----
        chars = []
        hv = H['view']
        hk = {'idle': 'idle', 'walk': 'walk', 'attack': 'attack', 'hurt': 'hurt'}[H['st']]
        himg = S('heroi', hk, hv, H['t'])
        if H['st'] == 'hurt' and H['t'] % 3 == 0: himg = Image.blend(himg, Image.new('RGBA', himg.size, (255, 255, 255, 255)), .8) if False else himg
        chars.append((himg, H['x'], H['y']))
        for m in mobs:
            if m.fade > 14: continue
            k = {'walk': 'walk', 'attack': 'attack', 'hurt': 'hurt', 'dead': 'death'}[m.st]
            img = S(m.name, k, m.view, m.t + (m.off if m.st == 'walk' else 0) if k != 'death' else min(m.t, m.seq_len('death') - 1))
            if m.flash % 2 == 1:
                a = img.split()[3]; img = Image.blend(img, Image.new('RGBA', img.size, (255, 255, 255, 255)), .75); img.putalpha(a)
            if m.fade: img = img.copy(); img.putalpha(img.split()[3].point(lambda v, q=max(0, 1 - m.fade / 14): int(v * q)))
            chars.append((img, m.x, m.y))
        im, (x0, y0) = mv.render((H['x'], H['y'] - 70), chars)
        d = ImageDraw.Draw(im)
        def N(mx, my): return int(mx // 2 - x0), int(my // 2 - y0)
        for m in mobs:
            if m.st != 'dead':
                off = 82 if m.name in ('esqueleto', 'zumbi', 'goblin', 'ogro') else (92 if m.fly else 56); px, py = N(m.x, m.y - off); J2.mini_hp(im, px, py, max(0, m.hp / m.max))
        # loot com feixe de luz
        for l in loot:
            l['t'] += 1; px, py = N(l['x'], l['y']); col = RARC[l['r']]
            if l['t'] < 34:
                ov = Image.new('RGBA', (NW, NH), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
                for k in range(0, 46):
                    od.line([px, py - 4 - k, px, py - 4 - k], fill=col + (max(0, 150 - k * 3),)); od.line([px - 1, py - 4 - k, px - 1, py - 4 - k], fill=col + (max(0, 90 - k * 3),)); od.line([px + 1, py - 4 - k, px + 1, py - 4 - k], fill=col + (max(0, 90 - k * 3),))
                im.alpha_composite(ov)
                bob = int(2 * math.sin(l['t'] * .4)); ic = IC.get(*(l['icon'].split(':') if ':' in l['icon'] else (l['icon'],)))
                im.alpha_composite(ic, (px - 8, py - 18 + bob)); 
                if l['t'] % 5 == 0: parts.append([l['x'] + random.randint(-8, 8), l['y'] - 20, 0, -1, 8, col])
            elif l['t'] < 48:
                u = (l['t'] - 34) / 14; hx_, hy_ = N(H['x'], H['y'] - 30); ic = IC.get(*(l['icon'].split(':') if ':' in l['icon'] else (l['icon'],)))
                im.alpha_composite(ic, (int(px + (hx_ - px) * u) - 8, int(py - 18 + (hy_ - py + 18) * u)))
            elif l['t'] == 48: nums.append([H['x'], H['y'] - 110, '+' + l['icon'].split(':')[0].upper()[:8], col, 0])
        for p in parts: p[0] += p[2] * 2; p[1] += p[3] * 2; p[4] -= 1
        for p in parts:
            if p[4] > 0: px, py = N(p[0], p[1]); d.rectangle([px, py, px + 1, py + 1], fill=p[5])
        parts[:] = [p for p in parts if p[4] > 0]
        for n_ in nums:
            n_[4] += 1; px, py = N(n_[0], n_[1] - n_[4] * 1.4); J2.T(im, (px, py), n_[2], n_[3], True, 2)
        nums[:] = [n_ for n_ in nums if n_[4] < 18]
        J2.hud(im, 'CATACUMBAS', H['hp'], ['Esqueleto derrotado!' if any(m.st == 'dead' for m in mobs) else 'Inimigos a frente!'])
        if shake != (0, 0):
            sh = Image.new('RGBA', (NW, NH), (0, 0, 0, 255)); sh.alpha_composite(im, shake); im = sh
        frames.append(im)
    big = [x.convert('RGB').resize((NW * SC, NH * SC), Image.NEAREST) for x in frames]
    p = big[0].quantize(colors=240, method=Image.MEDIANCUT, dither=Image.NONE); q = [b.quantize(palette=p, dither=Image.NONE) for b in big]
    q[0].save(os.path.join(OUT, 'combate_pixel.gif'), save_all=True, append_images=q[1:], duration=55, loop=0, disposal=1)
    return len(q), big


if __name__ == '__main__':
    n, big = run(); print(n)
    sel = [big[min(n - 1, int(n * q))] for q in (.06, .14, .22, .3, .38, .46, .55, .63, .72, .8, .9, .97)]
    sh = Image.new('RGB', (NW * SC // 2 * 6, NH * SC // 2 * 2))
    for i, b in enumerate(sel): sh.paste(b.resize((NW * SC // 2, NH * SC // 2), Image.NEAREST), ((i % 6) * NW * SC // 2, (i // 6) * NH * SC // 2))
    sh.save(os.path.join(OUT, 'combate_pixel_folha.png'))
