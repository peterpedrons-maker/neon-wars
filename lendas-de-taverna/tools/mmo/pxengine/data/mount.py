#!/usr/bin/env python3
"""MONTARIAS (estilo MMO: só para viajar; some ao entrar em combate). Cavalo por código no motor `fauna.py` (uma massa só).
Gera atlas `cx_mount_<id>_atlas` (idle/walk/run x vistas d/u/s) + `cx_mount_<id>_h_atlas` (só pescoço/cabeça, para ficar na frente do
cavaleiro na vista de frente). O cavaleiro NÃO é desenhado aqui: o jogo o compõe em tempo de execução (cxMountFrame em index.html) para
respeitar a aparência personalizada. `meta.rider` = ponto da sela (x,y em pixels do atlas, relativo ao canto do quadro)."""
import json, math, os, sys
import numpy as np
from PIL import Image
import fauna as F
import chibi as C

W, H, BASE = F.W, F.H, F.BASE
R = F.R
PAL = {
    'cavalo': dict(body=R('#4a2616', '#7a4426', '#a86a40'), mane=R('#1a0e08', '#2c1a0e', '#46301c'), hoof=R('#1a1410', '#2c241c', '#443a2e'),
                   nose=R('#7a4a44', '#a8706a', '#cc9a90'), saddle=R('#3a1c0e', '#6a3418', '#98502a'), blanket=R('#5a1020', '#9a2236', '#cc4a5e'),
                   belly=R('#6a3c24', '#98603c', '#c08a5c'), blaze=R('#b8b0a4', '#e6dece', '#fffaf0'), sock=R('#a8a094', '#dcd4c4', '#fffaf0')),
    'lobo': dict(body=R('#3a404e', '#5e6676', '#8a94a6'), mane=R('#202530', '#363c4a', '#505868'), hoof=R('#14141c', '#262630', '#3a3a46'),
                 nose=R('#14141c', '#2a2a34', '#44444e'), saddle=R('#3a1c0e', '#6a3418', '#98502a'), blanket=R('#1a3a5a', '#2c64a0', '#5a98d0'),
                 belly=R('#7a8294', '#aab2c4', '#d0d6e2'), blaze=R('#d0d6e2', '#eef0f6', '#ffffff'), sock=R('#8a92a4', '#c8cedc', '#ffffff')),
}


def _leg(u, amp, L, run):
    """fase u (0..1) -> (deslocamento x do pe, altura do pe). Apoio: pe vai para tras no chao; balanco: levanta e leva para frente."""
    u %= 1.0; st = .6 if not run else .5
    if u < st: return amp - 2 * amp * (u / st), 0.0
    w = (u - st) / (1 - st); return -amp + 2 * amp * w, math.sin(math.pi * w) * L


def leg2(c, x, hipy, gy, u, amp, L, front, far, run, sock=True):
    """perna de duas partes (coxa + canela) com joelho/jarrete dobrando; casco na ponta."""
    fx, fl = _leg(u, amp, L, run); foot = (x + fx, gy - fl); hip = (x, hipy)
    mx, my = (hip[0] + foot[0]) / 2, (hip[1] + foot[1]) / 2 - .5
    bend = (1.2 + fl * .55) * (1 if front else -1) * (1 if fl > .1 or True else 0)
    kx, ky = mx + bend, my
    c.cap(hip[0], hip[1], kx, ky, 1.9, 1.35, 'body', far)
    c.cap(kx, ky, foot[0], foot[1] - 1.3, 1.35, 1.0, 'sock' if sock else 'body', far)
    c.cap(foot[0], foot[1] - 1.4, foot[0] + .4, foot[1] + .2, 1.2, 1.35, 'hoof', far)


def cavalo(view, u=0.0, bob=0, amp=3.0, lift=2.6, tail=0.0, head=False, pal='cavalo', run=False, nod=0.0, idle=False):
    """head=True: so pescoco+cabeca+crina (camada que fica na frente do cavaleiro na vista de frente)."""
    c = F.Cv(); cx = W // 2; gy = BASE; by = gy - 15 + bob; rider = None
    if idle: amp = 0.0; lift = 0.0
    if run: offs = {'nh': 0.0, 'fh': .08, 'nf': .5, 'ff': .58}
    else: offs = {'nh': 0.0, 'nf': .25, 'fh': .5, 'ff': .75}
    if view == 'right':
        if not head:
            for name, lx, front, far in (('fh', -6.0, False, True), ('ff', 6.0, True, True), ('nh', -5.0, False, False), ('nf', 6.8, True, False)):
                leg2(c, cx + lx, by + 3, gy, u + offs[name], amp, lift, front, far, run, sock=(name in ('nh', 'nf')))
            c.ell(cx - 7, by, 6.2, 5.6); c.ell(cx, by + .3, 9.4, 5.9); c.ell(cx, by + 3.4, 8, 2.3, 'belly'); c.ell(cx + 7, by - .6, 5.8, 6.1)
            tl = math.sin(tail) * (3.2 if run else 2.0); tu = -3.5 if run else 0
            c.cap(cx - 11, by - 3, cx - 15, by - 2 + tu + 2.5, 2.2, 1.6, 'mane'); c.cap(cx - 15, by - 2 + tu + 2.5, cx - 17.5 + (2 if run else 0), by + 7 + tu * .4 + tl, 1.6, .8, 'mane')
            c.ell(cx - .5, by - 5.4, 5.2, 1.5, 'blanket'); c.ell(cx - .5, by - 6.0, 3.4, 1.3, 'saddle'); c.cap(cx + 2.5, by - 5, cx + 3.2, by + 1.2, .7, .5, 'saddle')
        hd = int(round(nod))
        c.cap(cx + 9, by - 3, cx + 14 + (1 if run else 0), by - 11 + hd + (3 if run else 0), 3.6, 2.3)
        hx0, hy0 = cx + 14 + (1 if run else 0), by - 11 + hd + (3 if run else 0)
        c.cap(hx0, hy0, hx0 + 6, hy0 + 3.6, 2.7, 2.0)
        c.cap(hx0 + 5, hy0 + 3, hx0 + 8.4, hy0 + 5.4, 2.0, 1.7, 'nose')
        c.cap(hx0 - 1, hy0 - 2, hx0 - .2, hy0 - 5, 1.2, .5)
        c.cap(cx + 8.4, by - 5.4, hx0 - 1.6, hy0 - 1.8, 1.5, 1.2, 'mane')
        for q in range(3 if not run else 0): c.cap(cx + 8 + q * 1.3, by - 5 + q * -2.2, cx + 6.4 + q * 1.3, by - 3.4 + q * -2.2 + 1.5, .9, .5, 'mane')
        c.cap(hx0 + 5.5, hy0 + 3.4, cx + 6.4, by - 5, .6, .5, 'saddle')
        c.dot(hx0 + 3.6, hy0 + 1, F.hx('#14100c')); c.dot(hx0 + 8.6, hy0 + 5, F.hx('#14100c')); c.dot(hx0 + 3.2, hy0 + .4, F.hx('#f4ece0'))
        rider = (cx - .5, by - 7.2)
    else:
        back = view == 'up'
        if not head:
            for name, lx, front in (('nh', -4.4, False), ('nf', 4.4, True)):
                leg2(c, cx + lx, by + 3, gy, u + offs[name], 0.0, lift * (1.4 if run else 1), front, False, run)
            c.ell(cx, by + .5, 8.2 if not back else 8.4, 6.8); c.ell(cx, by + 4, 7.6, 2.4, 'belly'); c.ell(cx, by - 4.8, 5.6, 1.6, 'blanket')
            if back: c.ell(cx, by - 5.4, 3.6, 1.3, 'saddle'); c.cap(cx, by - 1, cx + math.sin(tail) * 2.6, by + 11, 2.8, 1.3, 'mane')
        if not back:
            hd = int(round(nod))
            c.cap(cx, by - 2, cx, by - 10, 5.0, 3.2); c.ell(cx, by - 13 + hd, 3.0, 4.2); c.ell(cx, by - 9.5 + hd, 2.1, 1.5, 'nose')
            c.cap(cx - 2.2, by - 16.2 + hd, cx - 2.6, by - 19 + hd, 1.1, .5); c.cap(cx + 2.2, by - 16.2 + hd, cx + 2.6, by - 19 + hd, 1.1, .5)
            c.cap(cx, by - 15.5 + hd, cx, by - 9 + hd, 1.1, 1.0, 'blaze')
            c.cap(cx, by - 4, cx, by - 15, 1.6, 1.2, 'mane'); c.dot(cx - 2.2, by - 13.4 + hd, F.hx('#14100c')); c.dot(cx + 2.2, by - 13.4 + hd, F.hx('#14100c'))
        rider = (cx, by - 6.4) if not back else (cx, by - 6.8)
    img = c.render(PAL[pal], F.FLAT)
    return img, rider


GAITS = {'idle': 6, 'walk': 8, 'run': 8}


def frames(view, kind, pal='cavalo', head=False):
    n = GAITS[kind] * 2; out = []; rid = []
    for i in range(n):
        u = i / n; ph = 2 * math.pi * u
        if kind == 'idle': im, r = cavalo(view, u, bob=1 if math.sin(ph) > .55 else 0, tail=ph, head=head, pal=pal, idle=True, nod=math.sin(ph * 1))
        elif kind == 'walk': im, r = cavalo(view, u, bob=-1 if abs(math.sin(ph * 2)) > .8 else 0, amp=3.2, lift=2.8, tail=ph * 2, head=head, pal=pal, nod=1.4 * math.sin(ph * 2 + 1))
        else: im, r = cavalo(view, u, bob=(-2 if math.sin(ph * 2) > .3 else (1 if math.sin(ph * 2) < -.7 else 0)), amp=5.4, lift=4.6, tail=ph * 3, head=head, pal=pal, run=True, nod=2.2 * math.sin(ph * 2 + .6))
        out.append(im); rid.append(r)
    return out, rid


def export(mid='cavalo', pal='cavalo', out_dir=None):
    out_dir = out_dir or os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..', 'mmo', 'assets', 'chars'))
    SC = 2; VIEWS = {'d': 'down', 'u': 'up', 's': 'right'}; imgs = []; himgs = []; anims = {}; rider = {}; riderf = {}
    for kind in GAITS:
        for vk, vn in VIEWS.items():
            fr, rid = frames(vn, kind, pal); hf = frames(vn, kind, pal, head=True)[0] if vn == 'down' else [Image.new('RGBA', (W, H), (0, 0, 0, 0))] * len(fr)
            idx = []
            for im, himg, r in zip(fr, hf, rid): idx.append(len(imgs)); imgs.append(im); himgs.append(himg)
            anims[f'{kind}_{vk}'] = idx; rider[vk] = r; riderf[f'{kind}_{vk}'] = rid
    bb = None
    for im in imgs:
        b = im.getbbox()
        if b: bb = b if bb is None else (min(bb[0], b[0]), min(bb[1], b[1]), max(bb[2], b[2]), max(bb[3], b[3]))
    x0, y0, x1, y1 = max(0, bb[0] - 1), max(0, bb[1] - 1), min(W, bb[2] + 1), min(H, bb[3] + 1)
    cw, ch = x1 - x0, y1 - y0; cols = 24; rows = (len(imgs) + cols - 1) // cols; w, h = cw * SC, ch * SC

    def atlas(L):
        A = Image.new('RGBA', (cols * w, rows * h), (0, 0, 0, 0))
        for i, im in enumerate(L): A.alpha_composite(im.crop((x0, y0, x1, y1)).resize((w, h), Image.NEAREST), ((i % cols) * w, (i // cols) * h))
        return A
    atlas(imgs).save(os.path.join(out_dir, f'cx_mount_{mid}_atlas.png'), optimize=True)
    atlas(himgs).save(os.path.join(out_dir, f'cx_mount_{mid}_h_atlas.png'), optimize=True)
    meta = dict(w=w, h=h, ax=(W // 2 - x0) * SC, ay=(BASE - y0) * SC, cols=cols, anims=anims, rider={k: [round((v[0] - x0) * SC), round((v[1] - y0) * SC)] for k, v in rider.items()}, riderf={k: [[round((q[0] - x0) * SC), round((q[1] - y0) * SC)] for q in v] for k, v in riderf.items()})
    json.dump(meta, open(os.path.join(out_dir, f'cx_mount_{mid}_atlas.json'), 'w')); json.dump(meta, open(os.path.join(out_dir, f'cx_mount_{mid}_h_atlas.json'), 'w'))
    print(mid, len(imgs), 'quadros', meta['rider'])


if __name__ == '__main__':
    if sys.argv[1:2] == ['sheet']:
        S = Image.new('RGBA', (W * 8, H * 9), (52, 70, 52, 255))
        for ki, kind in enumerate(('idle', 'walk', 'run')):
            for vi, v in enumerate(('right', 'down', 'up')):
                fr, rid = frames(v, kind)
                for i, im in enumerate(fr[:8]): S.alpha_composite(im, (i * W, (ki * 3 + vi) * H))
        S.resize((S.width * 2, S.height * 2), Image.NEAREST).convert('RGB').save(sys.argv[2])
    else: export()
