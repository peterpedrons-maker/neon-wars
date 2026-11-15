#!/usr/bin/env python3
"""LUTA DE CHEFE EM RITMO DE ACAO (dono: "e um RPG de acao, sem intervalos entre os ataques"): combo encadeado sem pausa, heroi persegue e esquiva (dash com i-frames),
Rei encadeia golpes e habilidades sem ficar parado, hit-stop, contador de combo. Mapa real da Cripta do Rei. Saida: acao_boss.mp4"""
import math, os, random
from PIL import Image, ImageDraw
import chibi as C
import mapview as MV
import jogo_pixel2 as J2
import pxfont, vid
from teste_clareira import OUT

NW, NH, SC = MV.NW, MV.NH, 2
HAPP = dict(cls='warrior', hat='helm', outfit='mail', metal='aco', clothes='aco', weapon='espada_aco')
RAPP = dict(cls='rei', weapon='espada_rei')
DENS = {'idle': 2, 'walk': 2, 'run': 2, 'attack': 1, 'hurt': 1, 'cast': 1, 'death': 1}
_S = {}


def seq(who, kind, view):
    v = 'right' if view in ('left', 'right') else view
    k = (who, kind, v)
    if k not in _S:
        ap, cls = (HAPP, 'warrior') if who == 'h' else (RAPP, 'rei')
        _S[k] = [f[0] for f in C.anim(v, kind, cls, None, ap, dense=DENS[kind])]
    return _S[k]


def img(who, kind, view, i):
    s = seq(who, kind, view); im = s[min(i, len(s) - 1)] if kind in ('death', 'hurt') else s[i % len(s)]
    return im.transpose(Image.FLIP_LEFT_RIGHT) if view == 'left' else im


def facing(dx, dy):
    if abs(dx) > abs(dy) * 1.4: return 'right' if dx > 0 else 'left'
    return 'down' if dy > 0 else 'up'


def tint(im, col, k):
    a = im.split()[3]; o = Image.blend(im, Image.new('RGBA', im.size, col + (255,)), k); o.putalpha(a); return o


class A:
    def __init__(s, x, y, hp): s.x, s.y, s.hp, s.st, s.t, s.view, s.flash, s.hold, s.inv, s.combo = x, y, hp, 'idle', 0, 'down', 0, 0, 0, 0


def run(max_frames=520):
    random.seed(21)
    mv = J2.SCENE_CACHE.setdefault('zone_cripta2', MV.MapV('zone_cripta2')); bx0, by0 = mv.m['boss']; ax, ay = 720, 1120   # arena (plataforma real do chefe)
    H = A(ax, ay + 140, 1.0); B = A(ax, ay - 70, 1.0); H.view = 'up'; B.view = 'down'
    queue = ['melee', 'rift', 'melee', 'souls', 'melee', 'echo', 'melee', 'forget', 'melee', 'dark', 'melee', 'rift', 'souls', 'melee', 'melee', 'melee']
    skill = None; boss_act = 'chase'; bi = 0; qi = 0; sw2 = 0
    parts = []; nums = []; orbs = []; frames = []; freeze = 0; shake = (0, 0); combo = 0; combo_t = 0; dash_cd = 0; forgot = 0; dark = 0.0; channel = None; dead_t = -1; end_t = 0
    hero_hits = 0
    def spark(x, y, col=(255, 240, 160), n=8):
        for _ in range(n): parts.append([x, y, random.uniform(-3.5, 3.5), random.uniform(-4, -.5), 8, col])
    def hurt_hero(dmg, x, y):
        nonlocal shake
        if H.inv > 0 or H.st == 'dead': return
        H.hp = max(.05, H.hp - dmg); H.st = 'hurt'; H.t = 0; H.flash = 4; shake = (1, 1)
        nums.append([H.x, H.y - 100, str(int(dmg * 900)), (255, 120, 110), 0]); spark(H.x, H.y - 30, (255, 90, 80), 7)
    for f in range(max_frames):
        shake = (0, 0)
        if freeze > 0: freeze -= 1
        else:
            # ================= HEROI =================
            dx, dy = B.x - H.x, B.y - H.y; dist = math.hypot(dx, dy) or 1
            H.inv = max(0, H.inv - 1); dash_cd = max(0, dash_cd - 1)
            danger = skill.danger(H) if skill else False
            if B.st == 'dead': H.st = 'idle'; H.t += 1
            elif H.st == 'dash':
                H.t += 1; H.x += H.dvx; H.y += H.dvy
                if f % 2 == 0: parts.append([H.x, H.y - 20, 0, 0, 5, (200, 220, 255)])
                if H.t >= 6: H.st = 'idle'; H.t = 0
            elif H.st == 'hurt':
                H.t += 1
                if H.t >= 4: H.st = 'idle'; H.t = 0
            elif danger and dash_cd == 0:
                px, py = skill.escape(H); n = math.hypot(px, py) or 1
                H.st = 'dash'; H.t = 0; H.dvx = px / n * 9; H.dvy = py / n * 9; H.inv = 8; dash_cd = 40; H.view = facing(px, py)
            elif H.st == 'attack':
                H.t += 1
                if H.t == 6:
                    d = math.hypot(B.x - H.x, B.y - H.y)
                    if d < 100:
                        hero_hits += 1; H.combo += 1; combo = H.combo; combo_t = 20
                        heavy = H.combo % 3 == 0; dmg = .095 if heavy else .055
                        B.hp = max(0, B.hp - dmg); B.flash = 3; freeze = 3 if heavy else 2
                        nums.append([B.x + random.randint(-10, 10), B.y - 130, str(int(dmg * 2700)), (255, 224, 74) if not heavy else (255, 160, 60), 0]); spark(B.x, B.y - 50, (255, 240, 170) if not heavy else (255, 180, 80), 12 if heavy else 8)
                        shake = (1, 1) if heavy else (0, 1)
                        if heavy: parts.append([B.x, B.y - 40, 0, 0, 10, (255, 255, 255)])
                if H.t >= 9:
                    if math.hypot(B.x - H.x, B.y - H.y) < 112: H.t = 2     # ENCADEIA sem pausa
                    else: H.st = 'idle'; H.t = 0
                else:
                    if 3 <= H.t <= 7 and math.hypot(B.x - H.x, B.y - H.y) > 70: H.x += dx / dist * 4; H.y += dy / dist * 4    # avanca no golpe
            else:
                H.view = facing(dx, dy)
                if dist < 96 and B.st != 'dead': H.st = 'attack'; H.t = 0
                else: H.st = 'walk'; H.x += dx / dist * 3.6; H.y += dy / dist * 3.6; H.t += 1; (parts.append([H.x, H.y, random.uniform(-.4, .4), -.5, 6, (170, 160, 150)]) if f % 3 == 0 else None)
            if combo_t > 0: combo_t -= 1
            else: combo = 0; H.combo = 0 if H.st != 'attack' else H.combo
            # ================= REI =================
            B.inv = 0; bdx, bdy = H.x - B.x, H.y - B.y; bd = math.hypot(bdx, bdy) or 1
            if B.hp <= 0 and B.st != 'dead': B.st = 'dead'; B.t = 0; skill = None; orbs.clear(); dead_t = f
            if B.st == 'dead': B.t += 1
            elif skill is not None:                                   # executando habilidade (nao fica parado: a propria habilidade move o Rei)
                skill.update(f, B, H, orbs, hurt_hero)
                B.st = skill.pose; B.t = skill.bt
                if skill.done: skill = None; boss_act = 'chase'; B.view = 'down'
            elif boss_act == 'chase':
                B.view = facing(bdx, bdy); B.st = 'walk'; B.t += 1
                B.x += bdx / bd * 3.0; B.y += bdy / bd * 3.0
                if bd < 92:
                    nxt = queue[qi % len(queue)]; qi += 1
                    if nxt == 'melee': boss_act = 'melee'; B.st = 'attack'; B.t = 0; sw2 = 2
                    else: skill = make_skill(nxt, B, H); boss_act = 'skill'
                elif qi % len(queue) in (1, 3, 5, 7, 9, 11, 12) and f % 1 == 0 and bd > 150:   # habilidades a distancia: conjura andando ate ficar a postos
                    nxt = queue[qi % len(queue)]
                    if nxt != 'melee': qi += 1; skill = make_skill(nxt, B, H); boss_act = 'skill'
            elif boss_act == 'melee':
                B.t += 1; B.view = facing(bdx, bdy)
                if B.t == 6 and bd < 120: hurt_hero(.05, B.x, B.y)
                if 3 <= B.t <= 7 and bd > 70: B.x += bdx / bd * 4; B.y += bdy / bd * 4
                if B.t >= 9:
                    if sw2 > 0 and bd < 130: sw2 -= 1; B.t = 2
                    else: boss_act = 'chase'; B.st = 'walk'
            for m in (H, B):
                if m.flash > 0: m.flash -= 1
            for o in orbs:
                o.update(H, hurt_hero)
            orbs[:] = [o for o in orbs if o.life > 0]
            for p in parts: p[0] += p[2] * 2; p[1] += p[3] * 2; p[4] -= 1
            parts[:] = [p for p in parts if p[4] > 0]
            forgot = skill.forgot_flag(H) if skill and hasattr(skill, 'forgot_flag') and skill.forgot_flag(H) else max(0, forgot - 1)
        # ================= desenho =================
        kind_h = {'idle': 'idle', 'walk': 'walk', 'attack': 'attack', 'hurt': 'hurt', 'dash': 'walk', 'dead': 'idle'}[H.st]
        hi = H.t if H.st != 'attack' else min(H.t, 9)
        himg = img('h', kind_h, H.view, hi)
        if H.st == 'dash': himg = tint(himg, (180, 220, 255), .35)
        if H.flash % 2 == 1 and H.flash: himg = tint(himg, (255, 255, 255), .8)
        if forgot > 0: himg = tint(himg, (150, 130, 200), .4)
        bk = {'idle': 'idle', 'walk': 'walk', 'attack': 'attack', 'cast': 'cast', 'hurt': 'hurt', 'dead': 'death', 'dash': 'attack'}.get(B.st, 'idle')
        bimg = img('r', bk, B.view, B.t)
        if B.flash % 2 == 1 and B.flash: bimg = tint(bimg, (255, 255, 255), .7)
        if B.st == 'dead' and B.t > len(seq('r', 'death', 'down')): bimg = bimg.copy(); bimg.putalpha(bimg.split()[3].point(lambda v, q=max(0, 1 - (B.t - len(seq('r', 'death', 'down'))) / 18): int(v * q)))
        chars = [(himg, H.x, H.y), (bimg, B.x, B.y)]
        extra_c = skill.chars() if skill else []
        im, (x0, y0) = mv.render(((H.x + B.x) / 2, (H.y + B.y) / 2 - 20), chars + extra_c)
        N = lambda mx, my: (int(mx) // 2 - x0, int(my) // 2 - y0)
        d = ImageDraw.Draw(im)
        if skill: skill.draw_under(im, N)
        for o in orbs: o.draw(im, N)
        for p in parts:
            px, py = N(p[0], p[1]); d.rectangle([px, py, px + 1, py + 1], fill=p[5])
        for n_ in nums:
            n_[4] += 1; px, py = N(n_[0], n_[1] - n_[4] * 1.6); J2.T(im, (px, py), n_[2], n_[3], True, 2)
        nums[:] = [n_ for n_ in nums if n_[4] < 16]
        if skill: skill.draw_over(im, N)
        if skill and skill.dark > 0:
            hx_, hy_ = N(H.x, H.y - 30); ov = Image.new('RGBA', (NW, NH), (4, 2, 12, 255)); m = Image.new('L', (NW, NH), int(235 * skill.dark)); md = ImageDraw.Draw(m)
            for k in range(5): rr = 16 + k * 9; md.ellipse([hx_ - rr, hy_ - rr * .8, hx_ + rr, hy_ + rr * .8], fill=int(235 * skill.dark * (k + 1) / 5.5) if k else 0)
            ov.putalpha(m); im.alpha_composite(ov)
        chan = (skill.name, skill.chan) if skill and skill.chan is not None else None
        J2.hud(im, 'CRIPTA DO REI', H.hp, ['Combo x%d' % combo if combo > 1 else 'Lute!'], boss=('REI ESQUECIDO', B.hp))
        if chan:
            bx_, by_ = N(B.x, B.y - 100); d.rectangle([bx_ - 26, by_, bx_ + 26, by_ + 5], fill=(18, 10, 30), outline=(190, 120, 255)); d.rectangle([bx_ - 25, by_ + 1, bx_ - 25 + int(50 * chan[1]), by_ + 4], fill=(200, 120, 255)); J2.T(im, (bx_, by_ - 8), chan[0].upper(), (235, 205, 255), True)
        if forgot > 0: J2.T(im, N(H.x, H.y - 96), '?', (200, 160, 255), True, 2); d.rectangle([22, 379, 49, 413], fill=(10, 8, 16, 190))
        if combo > 1: J2.T(im, (186, 112), 'COMBO', GOLD_ := (255, 214, 90), False if False else True) if False else (J2.T(im, (160, 106), 'COMBO', (255, 214, 90)), J2.T(im, (178, 114), 'x%d' % combo, (255, 240, 170), True, 2))
        if B.st == 'dead' and B.t > 24: J2.T(im, (97, 150), 'VITORIA!', (255, 230, 120), True, 2)
        if shake != (0, 0):
            sh = Image.new('RGBA', (NW, NH), (0, 0, 0, 255)); sh.alpha_composite(im, shake); im = sh
        frames.append(im)
        if B.st == 'dead' and B.t > 60: break
    big = [x.convert('RGB').resize((NW * SC, NH * SC), Image.NEAREST) for x in frames]
    return big


# ---------------------------------------------------------------- habilidades
class Orb:
    def __init__(s, x, y, tx, ty, sp=6.0, homing=.0): s.x, s.y = x, y; a = math.atan2(ty - y, tx - x); s.vx, s.vy = math.cos(a) * sp, math.sin(a) * sp; s.life = 46; s.sp = sp; s.hm = homing
    def update(s, H, hurt):
        if s.hm:
            a = math.atan2(H.y - 20 - s.y, H.x - s.x); ca = math.atan2(s.vy, s.vx); da = ((a - ca + math.pi) % (2 * math.pi)) - math.pi; ca += max(-s.hm, min(s.hm, da)); s.vx, s.vy = math.cos(ca) * s.sp, math.sin(ca) * s.sp
        s.x += s.vx; s.y += s.vy; s.life -= 1
        if math.hypot(H.x - s.x, H.y - 20 - s.y) < 18: hurt(.035, s.x, s.y); s.life = 0
    def draw(s, im, N):
        px, py = N(s.x, s.y); d = ImageDraw.Draw(im)
        for k in range(1, 4): d.rectangle([px - s.vx * k * .5 - 1, py - s.vy * k * .5 - 1, px - s.vx * k * .5 + 1, py - s.vy * k * .5 + 1], fill=(150, 80, 230))
        d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(180, 100, 255)); d.ellipse([px - 1, py - 1, px + 1, py + 1], fill=(255, 255, 255))


class Skill:
    name = ''; pose = 'cast'; dark = 0; chan = None
    def __init__(s, B, H): s.f = 0; s.done = False; s.bt = 0
    def danger(s, H): return False
    def escape(s, H): return (1, 0)
    def chars(s): return []
    def draw_under(s, im, N): pass
    def draw_over(s, im, N): pass


class Rift(Skill):
    name = 'Fenda do Vazio'
    def __init__(s, B, H):
        super().__init__(B, H); s.lx = [B.x - 70, B.x, B.x + 70]; s.y0 = B.y; s.cl = [[s.lx[0], B.y], [s.lx[2], B.y]]; s.hit = False
    def danger(s, H): return 6 <= s.f <= 26 and any(abs(H.x - x) < 30 for x in s.lx)
    def escape(s, H): xs = min(s.lx + [H.x], key=lambda x: abs(x - H.x)); return (1 if H.x >= xs else -1, 0) if False else ((1, 0) if H.x > (s.lx[0] + s.lx[1]) / 2 and H.x < (s.lx[1] + s.lx[2]) / 2 and H.x >= s.lx[1] else (-1, 0) if H.x < s.lx[1] and H.x > s.lx[0] else ((1, 0) if H.x >= s.lx[1] else (-1, 0)))
    def update(s, f, B, H, orbs, hurt):
        s.f += 1; F = s.f
        s.chan = min(1, F / 10) if F <= 10 else None; s.pose = 'cast' if F < 12 else 'attack'; s.bt = min(7, F // 2) if F < 12 else 6
        if 12 <= F <= 22:
            u = ((F - 12) / 10) ** 1.6; B.y = s.y0 + 250 * u; s.cl[0][1] = s.cl[1][1] = B.y
            if not s.hit and any(abs(H.x - x) < 24 for x in s.lx) and s.y0 + 250 * u - 40 < H.y < s.y0 + 250 * u + 40: hurt(.08, H.x, H.y); s.hit = True
        if F >= 36: s.done = True
    def chars(s):
        if s.f < 4: return []
        g = img('r', 'cast', 'down', 6) if s.f < 12 else img('r', 'attack', 'down', 6)
        a = g.split()[3].point(lambda v: 130 if v else 0); g2 = tint(g, (80, 30, 140), .5); g2.putalpha(a)
        return [(g2, s.cl[0][0], s.cl[0][1]), (g2, s.cl[1][0], s.cl[1][1])]
    def draw_under(s, im, N):
        ov = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
        for k, x in enumerate(s.lx):
            on = max(0, min(1, (s.f - 2 - k * 2) / 5)); 
            if 0 < s.f < 24:
                a = int(200 * on); x0, y0_ = N(x - 20, s.y0); x1, y1_ = N(x + 20, s.y0 + 260)
                d.rectangle([x0, y0_, x1, y1_], fill=(230, 40, 50, int(a * .30))); d.line([x0, y0_, x0, y1_], fill=(255, 90, 90, a)); d.line([x1, y0_, x1, y1_], fill=(255, 90, 90, a))
            if s.f >= 12:
                x0, y0_ = N(x - 12, s.y0); x1, y1_ = N(x + 12, B_y(s) if False else s.y0 + 250 * min(1, ((s.f - 12) / 10) ** 1.6))
                d.rectangle([x0, y0_, x1, y1_], fill=(8, 2, 16, max(0, 230 - (s.f - 12) * 7))); d.line([x0, y0_, x0, y1_], fill=(190, 90, 255, max(0, 255 - (s.f - 12) * 7)))
        im.alpha_composite(ov)


def B_y(s): return s.y0


class Souls(Skill):
    name = 'Coroa de Almas'
    def __init__(s, B, H): super().__init__(B, H); s.o = [[0, 0] for _ in range(5)]; s.fired = [False] * 5; s.B = B
    def danger(s, H): return 14 <= s.f <= 30 and False
    def update(s, f, B, H, orbs, hurt):
        s.f += 1; F = s.f; s.chan = min(1, F / 10) if F <= 10 else None; s.pose = 'cast'; s.bt = min(7, F // 2) if F < 14 else 6
        for i in range(5):
            if F >= 12 + i * 3 and not s.fired[i]:
                s.fired[i] = True; a = i * 2 * math.pi / 5 + F * .3; ox, oy = B.x + math.cos(a) * 36, B.y - 74 + math.sin(a) * 14; orbs.append(Orb(ox, oy, H.x, H.y - 20, 5.5, .09))
        if F >= 30: s.done = True
    def draw_over(s, im, N):
        if s.f < 14:
            d = ImageDraw.Draw(im)
            for i in range(5):
                if s.fired[i]: continue
                a = i * 2 * math.pi / 5 + s.f * .3; px, py = N(s.B.x + math.cos(a) * (14 + s.f * 1.6), s.B.y - 74 + math.sin(a) * (6 + s.f * .6))
                d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(90, 190, 255)); d.ellipse([px - 1, py - 1, px + 1, py + 1], fill=(255, 255, 255))


class Echo(Skill):
    name = 'Eco'
    def __init__(s, B, H): super().__init__(B, H); s.cx = [B.x - 80, B.x + 80]; s.cy = B.y + 10; s.shots = {12: 0, 17: 1, 22: 0, 27: 1}
    def update(s, f, B, H, orbs, hurt):
        s.f += 1; F = s.f; s.chan = min(1, F / 9) if F <= 9 else None; s.pose = 'cast'; s.bt = min(7, F // 2) if F < 14 else 6
        if F in s.shots: orbs.append(Orb(s.cx[s.shots[F]], s.cy - 30, H.x, H.y - 20, 6.2, .05))
        if F >= 34: s.done = True
    def chars(s):
        if s.f < 4: return []
        g = img('r', 'cast', 'down', 6); a = g.split()[3].point(lambda v: 120 if v else 0); g2 = tint(g, (120, 200, 255), .6); g2.putalpha(a)
        return [(g2, s.cx[0], s.cy), (g2, s.cx[1], s.cy)]


class Forget(Skill):
    name = 'Esquecimento'
    def __init__(s, B, H): super().__init__(B, H); s.cx, s.cy = B.x, B.y; s.ff = 0
    def update(s, f, B, H, orbs, hurt):
        s.f += 1; F = s.f; s.chan = min(1, F / 9) if F <= 9 else None; s.pose = 'cast'; s.bt = min(7, F // 2) if F < 14 else 6
        if F >= 30: s.done = True
    def forgot_flag(s, H):
        if s.f < 10: return 0
        r = (s.f - 10) * 9
        return 60 if abs(math.hypot(H.x - s.cx, H.y - s.cy) - r) < 24 and H.inv == 0 else 0
    def draw_under(s, im, N):
        if s.f < 10: return
        ov = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov); r = (s.f - 10) * 9
        for k in range(4):
            rr = r - k * 12
            if rr > 0:
                cx, cy = N(s.cx, s.cy); d.ellipse([cx - rr // 2, cy - rr // 4, cx + rr // 2, cy + rr // 4], outline=(150 + k * 20, 70, 220, 230 - k * 50))
        im.alpha_composite(ov)


class Dark(Skill):
    name = 'Trevas'
    def __init__(s, B, H): super().__init__(B, H); s.hit = False
    def update(s, f, B, H, orbs, hurt):
        s.f += 1; F = s.f; s.chan = min(1, F / 10) if F <= 10 else None; s.pose = 'cast'; s.bt = min(7, F // 2) if F < 14 else 6
        s.dark = min(.9, F / 8) if F < 32 else max(0, .9 - (F - 32) / 8)
        if F == 22 and not s.hit:
            s.hit = True; hurt(.06, H.x, H.y)
        if F >= 40: s.done = True
    def danger(s, H): return 14 <= s.f < 21
    def escape(s, H): return (1 if H.x < 720 else -1, 1)
    def draw_under(s, im, N):
        if 8 <= s.f <= 30: pass


def make_skill(n, B, H): return {'rift': Rift, 'souls': Souls, 'echo': Echo, 'forget': Forget, 'dark': Dark}[n](B, H)


if __name__ == '__main__':
    big = run(); print(len(big), vid.mp4(big, os.path.join(OUT, 'acao_boss.mp4'), 24))
    n = len(big)
    sel = [big[min(n - 1, int(n * q))] for q in (.03, .09, .15, .22, .3, .38, .46, .54, .62, .7, .8, .95)]
    sh = Image.new('RGB', (NW * SC // 2 * 6, NH * SC // 2 * 2))
    for i, b in enumerate(sel): sh.paste(b.resize((NW * SC // 2, NH * SC // 2), Image.NEAREST), ((i % 6) * NW * SC // 2, (i // 6) * NH * SC // 2))
    sh.save(os.path.join(OUT, 'acao_boss_folha.png'))
