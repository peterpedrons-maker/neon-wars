#!/usr/bin/env python3
"""Exporta os sprites pixel art (chibi.py/beast.py/creature.py) como ATLAS para o jogo real.
Saida: mmo/assets/chars/cx_<chave>_atlas.png + .json (meta: w,h,ax,ay,cols,anims{<anim>_<vista>:[indices]}).
Vistas: d (frente), u (costas), s (lado direito; esquerda = espelho em tempo de execucao). Escala x2 (1 pixel nativo = 2px de mundo).
Uso: python3 export_atlas.py [chave ...]"""
import json, math, os, sys
from PIL import Image
import chibi as C, beast as BE, creature as CRE
import jogo_pixel as J

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..', 'mmo', 'assets', 'chars')
OUT = os.path.abspath(OUT)
SC = 2
W, H = C.W, C.H            # 72x64
AX, AY = W // 2, C.BASE     # pes
VIEWS = {'d': 'down', 'u': 'up', 's': 'right'}
HERO = dict(cls='warrior', hat='helm', outfit='mail', metal='aco', clothes='aco', weapon='espada_aco')
UNITS = {
    'h_guerreiro': dict(kind='c', ap=HERO, run=1),
    'h_mago': dict(kind='c', ap=dict(cls='mage', weapon='cajado_arcano'), run=1),
    'h_ladino': dict(kind='c', ap=dict(cls='rogue', weapon='adaga_veneno', weapon2='adaga_veneno'), run=1),
    'h_clerigo': dict(kind='c', ap=dict(cls='cleric', weapon='maca_ferro'), run=1),
    'h_arqueiro': dict(kind='c', ap=dict(cls='archer', weapon='arco_curto'), run=1),
    'h_bardo': dict(kind='c', ap=dict(cls='mage', weapon='cajado_natureza', hair='castanho', clothes='verde'), run=1),
    'goblin': dict(kind='e', name='goblin'), 'goblin_x': dict(kind='e', name='goblin_x'),
    'esqueleto': dict(kind='e', name='esqueleto'),
    'esqmago': dict(kind='c', ap=dict(cls='mage', skin='osso', hair='g_osso', eyes='oco', hat='hood', outfit='robe', clothes='azul', weapon='cajado_gelo')),
    'guarda_c': dict(kind='c', ap=dict(cls='warrior', skin='osso', hair='g_osso', eyes='oco', hat='rusty_helm', outfit='mail', clothes='osso', metal='ferro', weapon='maca_ferro', bulk=1)),
    'cultista': dict(kind='e', name='cultista'), 'gargula': dict(kind='e', name='gargula'), 'zumbi': dict(kind='e', name='zumbi'),
    'javali': dict(kind='b', name='javali'), 'rato': dict(kind='b', name='rato'),
    'espectro': dict(kind='r', name='espectro'), 'morcego': dict(kind='r', name='morcego'), 'slime': dict(kind='r', name='slime'),
    'rei': dict(kind='c', ap=dict(cls='rei', weapon='espada_rei'), cast=1),
}
J.ENEMY.update({
    'grunk': dict(cls='warrior', skin='goblin', hair='g_goblin', eyes='amarelo', hat='gob_ears', outfit='mail', metal='ferro', clothes='bronze', weapon='machado', tn_off=1, bulk=1),
    'morvath': dict(cls='warrior', skin='osso', hair='g_osso', eyes='oco', hat='rusty_helm', outfit='mail', clothes='azul', metal='aco', weapon='espada_gelo', tn_off=1, bulk=1),
})
UNITS.update({
    'n_guarda': dict(kind='c', ap=dict(cls='warrior', hat='helm', outfit='mail', metal='aco', clothes='azul', weapon='espada_ferro')),
    'n_pov_f': dict(kind='e', name='aldeao'),
    'n_ladino_b': dict(kind='c', ap=dict(cls='rogue', weapon='adaga_ferro', clothes='verde')),
    'n_bardo': dict(kind='c', ap=dict(cls='mage', hat='none', outfit='robe', clothes='vermelho', hair='preto', weapon='cajado_natureza')),
})
UNITS.update({'ogro': dict(kind='e', name='ogro'), 'grunk': dict(kind='e', name='grunk'), 'morvath': dict(kind='e', name='morvath')})
DENS = {'idle': 2, 'walk': 2, 'run': 2, 'attack': 1, 'hurt': 1, 'death': 1, 'cast': 1}


BOWD = {'right': (1, 0), 'down': (0, 1), 'up': (0, -1)}


def bowp(d, draw, arrow=True, mode='aim'): return dict(kind='bow', dir=d, draw=draw, arrow=arrow, mode=mode)


def archer_ps(kind, view):
    d = BOWD[view]; carry = bowp(d, 0, False, 'carry'); n = {'idle': 6, 'walk': 8, 'run': 8}.get(kind)
    if n:
        fn = {'idle': C.idle_params, 'walk': C.walk_params, 'run': C.run_params}[kind]; ps = [fn(f, n * DENS[kind], view) for f in range(n * DENS[kind])]
    elif kind in ('attack', 'cast'):
        return [dict(sw=bowp(d, 0, False, 'carry')), dict(sw=bowp(d, 2)), dict(sw=bowp(d, 4), hdx=-1), dict(sw=bowp(d, 6), hdx=-1, bdx=-1, dx=-1),
                dict(sw=bowp(d, 8), hdx=-2, bdx=-1, dx=-1, tn=2, face='shout'), dict(sw=bowp(d, 8), hdx=-2, bdx=-1, dx=-1, tn=2, face='shout'),
                dict(sw=bowp(d, 0, False), hdx=1, dx=1), dict(sw=bowp(d, -1, False), hdx=1, dx=1), dict(sw=bowp(d, 2, False)), dict(sw=bowp(d, 0, False, 'carry'))]
    else: ps = C.extra_poses(kind, view)
    return [dict(p, sw=dict(carry)) for p in ps]


def frames(u, kind, view):
    k, d = u['kind'], DENS[kind]
    kk = kind
    if k == 'c' and u['ap']['cls'] == 'archer':
        return [f[0] for f in C.anim(view, 'walk', 'archer', archer_ps(kind, view), u['ap'], dense=1)]
    if k == 'c':
        if kind == 'cast' and not (u.get('cast') or u['ap']['cls'] in ('mage', 'cleric', 'archer')): kk = 'attack'
        if kind == 'run' and not u.get('run'): kk = 'walk'
        try: return [f[0] for f in C.anim(view, kk, u['ap']['cls'], None, u['ap'], dense=d)]
        except Exception as ex:
            print('  fallback', kind, view, ex); return [f[0] for f in C.anim(view, 'walk' if kind in ('run',) else 'attack', u['ap']['cls'], None, u['ap'], dense=d)]
    if kind in ('run',): kk = 'walk'
    if kind == 'cast': kk = 'attack'
    if k == 'e': return J.spr(u['name'], kk, view, d)
    if k == 'b': return [f[0] for f in BE.anim(u['name'], kk, view, d)]
    return [f[0] for f in CRE.anim(u['name'], kk, view, d)]


def export(key):
    u = UNITS[key]; imgs = []; anims = {}
    kinds = ['idle', 'walk', 'run', 'attack', 'hurt', 'death', 'cast']
    ALIAS = {}
    if u['kind'] == 'c' and not u.get('run'): ALIAS['run'] = 'walk'
    elif u['kind'] != 'c': ALIAS['run'] = 'walk'
    if u['kind'] != 'c' or not (u.get('cast') or u['ap']['cls'] in ('mage', 'cleric', 'archer')): ALIAS['cast'] = 'attack'
    for kind in kinds:
        for vk, vn in VIEWS.items():
            if kind in ALIAS: anims[f'{kind}_{vk}'] = anims[f'{ALIAS[kind]}_{vk}']; continue
            fr = frames(u, kind, vn); idx = []
            for im in fr:
                im = im.convert('RGBA')
                if im.size != (W, H): c = Image.new('RGBA', (W, H), (0, 0, 0, 0)); c.alpha_composite(im, (0, 0)); im = c
                idx.append(len(imgs)); imgs.append(im)
            anims[f'{kind}_{vk}'] = idx
    bb = None
    for im in imgs:
        b = im.getbbox()
        if b: bb = b if bb is None else (min(bb[0], b[0]), min(bb[1], b[1]), max(bb[2], b[2]), max(bb[3], b[3]))
    x0, y0, x1, y1 = max(0, bb[0] - 1), max(0, bb[1] - 1), min(W, bb[2] + 1), min(H, bb[3] + 1)
    imgs = [im.crop((x0, y0, x1, y1)) for im in imgs]; cw, ch = x1 - x0, y1 - y0
    cols = 24; rows = (len(imgs) + cols - 1) // cols; w, h = cw * SC, ch * SC
    A = Image.new('RGBA', (cols * w, rows * h), (0, 0, 0, 0))
    for i, im in enumerate(imgs): A.alpha_composite(im.resize((w, h), Image.NEAREST), ((i % cols) * w, (i // cols) * h))
    A.save(os.path.join(OUT, f'cx_{key}_atlas.png'), optimize=True)
    json.dump(dict(w=w, h=h, ax=(AX - x0) * SC, ay=(AY - y0) * SC, cols=cols, anims=anims), open(os.path.join(OUT, f'cx_{key}_atlas.json'), 'w'))
    print(key, len(imgs), A.size, os.path.getsize(os.path.join(OUT, f'cx_{key}_atlas.png')) // 1024, 'KB')


if __name__ == '__main__':
    for k in (sys.argv[1:] or UNITS): export(k)
