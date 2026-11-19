#!/usr/bin/env python3
"""Exporta os sprites pixel art (chibi.py/beast.py/creature.py) como ATLAS para o jogo real.
Saida: mmo/assets/chars/cx_<chave>_atlas.png + .json (meta: w,h,ax,ay,cols,anims{<anim>_<vista>:[indices]}).
Vistas: d (frente), u (costas), s (lado direito; esquerda = espelho em tempo de execucao). Escala x2 (1 pixel nativo = 2px de mundo).
Uso: python3 export_atlas.py [chave ...]"""
import json, math, os, sys
from PIL import Image
import chibi as C, beast as BE, creature as CRE, fauna as FA, fauna2, humano as HM
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
    'h_mago': dict(kind='c', ap=dict(cls='mage', weapon='cajado_arcano', face_style='cold'), run=1),
    'h_ladino': dict(kind='c', ap=dict(cls='rogue', weapon='adaga_veneno', weapon2='adaga_veneno', face_style='sly'), run=1),
    'h_clerigo': dict(kind='c', ap=dict(cls='cleric', weapon='maca_ferro'), run=1),
    'h_arqueiro': dict(kind='c', ap=dict(cls='archer', weapon='arco_curto'), run=1),
    'h_bardo': dict(kind='c', ap=dict(cls='mage', weapon='alaude', hair='castanho', clothes='verde', hat='bardcap', pal=dict(U='#b02838', u='#e0485a', V='#6a1428')), run=1),
    'goblin': dict(kind='e', name='goblin'), 'goblin_x': dict(kind='e', name='goblin_x'),
    'esqueleto': dict(kind='c', ap=dict(cls='warrior', skin='osso', hair='g_osso', eyes='oco', hat='none', outfit='ribs', clothes='osso', metal='ferro', weapon='espada_ferro', face_style='hollow', tn_off=2, shape=dict(skull=1, slim=1, eyeglow='W'))),
    'esqmago': dict(kind='c', ap=dict(cls='mage', face_style='hollow', skin='osso', hair='g_osso', hairstyle='bald', eyes='oco', hat='wizard', outfit='robe', clothes='azul', weapon='cajado_gelo', shape=dict(skull=1, eyeglow='W'))),
    'guarda_c': dict(kind='c', ap=dict(cls='warrior', face_style='hollow', skin='osso', hair='g_osso', eyes='oco', hat='rusty_helm', outfit='mail', clothes='osso', metal='ferro', weapon='maca_ferro', bulk=1, shape=dict(shield=1, crest=1, eyeglow='c'), pal=dict(Y='#b02820', X='#e85a3a'))),
    'cultista': dict(kind='c', ap=dict(cls='rogue', skin='fantasma', hair='preto', eyes='brasa', hat='hood', outfit='robe', clothes='roxo', weapon='cajado_caveira', face_style='cold', shape=dict(eyeglow='r'), pal=dict())),
    'gargula': dict(kind='e', name='gargula'),
    'zumbi': dict(kind='c', ap=dict(cls='warrior', skin='zumbi', hair='g_zumbi', hairstyle='long', eyes='oco', hat='none', outfit='cloth', clothes='verde', noweapon=1, arms_fwd=1, face_style='hollow', hdy_off=2, tn_off=1, shape=dict(slim=1, fists=1))),
    'javali': dict(kind='b', name='javali'), 'rato': dict(kind='b', name='rato'),
    'espectro': dict(kind='r', name='espectro'), 'morcego': dict(kind='r', name='morcego'), 'slime': dict(kind='r', name='slime'),
    'rei': dict(kind='c', ap=dict(cls='rei', weapon='espada_rei'), cast=1),
}
J.ENEMY.update({
    'grunk': dict(cls='warrior', skin='goblin', hair='g_goblin', eyes='brasa', hat='gobking', outfit='mail', metal='ferro', clothes='bronze', weapon='machado', tn_off=2, bulk=1, face_style='brute'),
    'morvath': dict(cls='warrior', skin='osso', hair='g_osso', eyes='oco', hat='rusty_helm', outfit='mail', clothes='azul', metal='aco', weapon='espada_gelo', tn_off=1, bulk=1, face_style='hollow'),
})
UNITS.update({
    'n_guarda': dict(kind='c', ap=dict(cls='warrior', hat='helm', outfit='mail', metal='aco', clothes='azul', weapon='espada_ferro')),
    'n_pov_f': dict(kind='e', name='aldeao'),
    'n_ladino_b': dict(kind='c', ap=dict(cls='rogue', weapon='adaga_ferro', clothes='verde')),
    'n_bardo': dict(kind='c', ap=dict(cls='mage', hat='none', outfit='robe', clothes='vermelho', hair='preto', weapon='cajado_natureza')),
})
UNITS.update({
    'goblin': dict(kind='m', spec='goblin'), 'grunk': dict(kind='c', ap=dict(cls='warrior', skin='goblin', hair='g_goblin', eyes='brasa', hat='gobking', outfit='mail', metal='ferro', clothes='bronze', weapon='machado', tn_off=2, bulk=1, face_style='brute')), 'goblin_x': dict(kind='m', spec='goblin_x'), 'sapador': dict(kind='m', spec='goblin_sapador'),
    'carnical': dict(kind='m', spec='carnical'), 'mumia': dict(kind='m', spec='mumia'), 'necro': dict(kind='m', spec='necro'), 'cav_caido': dict(kind='m', spec='cav_caido'),
    'ogro_lenhador': dict(kind='m', spec='ogro_lenhador'), 'afogado': dict(kind='m', spec='afogado'), 'bandido': dict(kind='m', spec='bandido'),
    'ladrao': dict(kind='m', spec='ladrao_esgoto'), 'cult_lodo': dict(kind='m', spec='cultista_lodo'),
    'gnoll': dict(kind='f', name='gnoll'), 'ratkin': dict(kind='f', name='ratkin'), 'harpia': dict(kind='f', name='harpia'), 'tronco': dict(kind='f', name='tronco'),
    'cogumelo': dict(kind='f', name='cogumelo'), 'ogrinho': dict(kind='f', name='ogrinho'), 'lobo': dict(kind='f', name='lobo'), 'aranha': dict(kind='f', name='aranha'),
    'cobra': dict(kind='f', name='cobra'), 'sapo': dict(kind='f', name='sapo'), 'barata': dict(kind='f', name='barata'),
})
UNITS.update({'ogro': dict(kind='c', ap=dict(cls='warrior', skin='ogro', hair='g_ogro_b', eyes='brasa', hat='ogre2', outfit='mail', metal='ferro', clothes='bronze', weapon='maca_ferro', tn_off=3, hdy_off=3, bulk=1, face_style='brute', shape=dict(fists=1))), 'grunk': dict(kind='e', name='grunk'), 'morvath': dict(kind='e', name='morvath')})
ALIAS_CAST_ONLY = False
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


_BA = lambda **ap: dict(kind='c', ap=ap)
UNITS.update({
 'morvath': _BA(cls='warrior', skin='osso', hair='azul', hairstyle='long', eyes='azul', hat='morvath', outfit='mail', clothes='azul', metal='aco', weapon='montante', tn_off=1, bulk=1, face_style='hollow'),
 'gorgash': _BA(cls='warrior', skin='ogro', hair='preto', hairstyle='mohawk', eyes='brasa', hat='gorgash', outfit='mail', clothes='bronze', metal='ferro', weapon='martelo_guerra', tn_off=2, bulk=1, face_style='brute'),
 'ratking': _BA(cls='rogue', skin='rato', hair='g_rato', hairstyle='spiky', eyes='vermelho', hat='ratking', outfit='cloth', clothes='roxo', weapon='adaga_sangue', weapon2='adaga_sangue', tn_off=1, face_style='sly'),
 'skrix': _BA(cls='mage', skin='goblin', hair='g_goblin', hairstyle='bald', eyes='amarelo', hat='skrix', outfit='robe', clothes='verde', weapon='cajado_caveira', tn_off=-1, face_style='fierce'),
 'boticario': dict(kind='x', src='codixel_botic/out/cx_boticario'),     # rato alquimista (arte original do dono -> codixel); o medico da peste foi erro
 'presa': _BA(cls='warrior', skin='javali', hair='g_javali', hairstyle='mane', eyes='brasa', hat='presa', outfit='mail', clothes='bronze', metal='ferro', weapon='machado', tn_off=2, bulk=1, face_style='brute'),
 'vampiro': dict(kind='v'),
})

# ESTILOS DE ANIMACAO por personagem (chibi_anim3): attack slash|smash|jab|cast, hurt flinch|stagger|stoic, death fall|topple|crumble|dissolve|tumble
ANIMS = {
    'h_bardo': dict(attack='play', hurt='stagger'),
    'h_mago': dict(attack='mthrust', hurt='stagger'), 'h_ladino': dict(attack='rcut', hurt='stagger', death='tumble'), 'h_guerreiro': dict(attack='wchop'), 'h_clerigo': dict(attack='cbash'),
    'esqueleto': dict(attack='jab', hurt='stagger', death='crumble'), 'esqmago': dict(attack='cast', hurt='stagger', death='dissolve'),
    'guarda_c': dict(attack='smash', hurt='stoic', death='crumble'), 'cultista': dict(attack='cast', hurt='stagger', death='dissolve'),
    'gargula': dict(attack='jab', hurt='stoic', death='crumble'), 'zumbi': dict(attack='smash', hurt='stoic', death='topple'),
    'ogro': dict(attack='smash', hurt='stoic', death='topple'), 'grunk': dict(attack='smash', hurt='stoic', death='topple'),
    'morvath': dict(attack='smash', hurt='stoic', death='crumble'), 'gorgash': dict(attack='smash', hurt='stoic', death='topple'),
    'ratking': dict(attack='jab', hurt='stagger', death='tumble'), 'skrix': dict(attack='cast', hurt='stagger', death='dissolve'),
    'presa': dict(attack='smash', hurt='stoic', death='topple'), 'rei': dict(attack='smash', hurt='stoic', death='crumble'),
}
for _k, _v in ANIMS.items():
    if _k in UNITS: UNITS[_k]['anim'] = _v
# COMBOS: animacoes de ataque diferentes por golpe (attack2/3/4 = golpe 2, 3 e finalizador). (pose base, variante) -> chibi_anim3.combo_frames
COMBO_KINDS = ('attack2', 'attack3', 'attack4')
COMBO = {
    'h_guerreiro': dict(attack2=('wrise', None), attack3=('jab', 'spin'), attack4=('wslam', None)),
    'h_mago': dict(attack2=('msweep', None), attack3=('msweep', 'spin'), attack4=('mchan', None)),
    'h_ladino': dict(attack2=('rrev', None), attack3=('rstab', None), attack4=('rx', None)),
    'h_clerigo': dict(attack2=('cback', None), attack3=('jab', 'spin'), attack4=('cpray', None)),
    'h_arqueiro': dict(attack2=('aq2', None), attack3=('aq3', None), attack4=('aq4', None)),
    'h_bardo': dict(attack2=('bstrum', None), attack3=('bdance', None), attack4=('bchord', None)),
}
for _k in list(UNITS):
    _b = '_'.join(_k.split('_')[:2])
    if _k.startswith('h_') and _b in COMBO: UNITS[_k]['combo'] = COMBO[_b]
UNITS['h_guerreiro']['twirl'] = True      # Tufao (Giro de Lamina empoderado): anim 'spin'
GCAST = {'grunk': 'slam', 'gorgash': 'slam', 'presa': 'slam', 'morvath': 'cast', 'ratking': 'cast', 'vampiro': 'cast', 'skrix': 'cast'}
GEN = {   # (ataque, dano, morte) para inimigos fora do motor chibi
    'goblin': ('lunge', 'flinch', 'tumble'), 'goblin_x': ('cast', 'stagger', 'dissolve'), 'sapador': ('lunge', 'flinch', 'tumble'), 'bandido': ('lunge', 'flinch', 'fall'),
    'carnical': ('lunge', 'flinch', 'melt'), 'mumia': ('slam', 'stoic', 'dissolve'), 'necro': ('cast', 'stagger', 'dissolve'), 'cav_caido': ('slam', 'stoic', 'topple'),
    'ogro_lenhador': ('slam', 'stoic', 'topple'), 'afogado': ('lunge', 'stagger', 'melt'), 'ladrao': ('lunge', 'flinch', 'tumble'), 'cult_lodo': ('cast', 'stagger', 'melt'),
    'javali': ('pounce', 'flinch', 'collapse'), 'rato': ('pounce', 'stagger', 'flip'), 'lobo': ('pounce', 'flinch', 'collapse'), 'cobra': ('pounce', 'flinch', 'melt'),
    'aranha': ('pounce', 'flinch', 'melt'), 'barata': ('pounce', 'flinch', 'melt'), 'sapo': ('pounce', 'stagger', 'melt'), 'gnoll': ('lunge', 'flinch', 'fall'),
    'ratkin': ('lunge', 'flinch', 'tumble'), 'harpia': ('pounce', 'stagger', 'flip'), 'tronco': ('slam', 'stoic', 'topple'), 'cogumelo': ('cast', 'flinch', 'melt'),
    'ogrinho': ('slam', 'stoic', 'topple'), 'espectro': ('cast', 'stagger', 'dissolve'), 'morcego': ('pounce', 'stagger', 'flip'), 'slime': ('pounce', 'flinch', 'melt'),
    'vampiro': ('pounce', 'stagger', 'flip'),
}
for _k, _v in GCAST.items():
    if _k in UNITS: UNITS[_k]['gcast'] = _v
for _k, _v in GEN.items():
    if _k in UNITS and UNITS[_k]['kind'] != 'c': UNITS[_k]['gen'] = dict(attack=_v[0], hurt=_v[1], death=_v[2])

# VARIANTES DO HEROI POR ARMA EQUIPADA (o sprite muda com a arma): chave = <heroi>_<variante>; o jogo escolhe por tipo de arma (HVAR em index.html)
_VAR = {'h_guerreiro_machado': ('h_guerreiro', dict(weapon='machado')), 'h_guerreiro_martelo': ('h_guerreiro', dict(weapon='martelo_guerra')),
        'h_ladino_espadacurta': ('h_ladino', dict(weapon='espada_curta', weapon2='espada_curta')),
        'h_mago_cetro': ('h_mago', dict(weapon='cetro_arcano')), 'h_mago_varinha': ('h_mago', dict(weapon='varinha')),
        'h_clerigo_martelo': ('h_clerigo', dict(weapon='martelo_sagrado')), 'h_clerigo_cetro': ('h_clerigo', dict(weapon='cetro_sagrado')),
        'h_arqueiro_longo': ('h_arqueiro', dict(weapon='arco_longo')), 'h_bardo_flauta': ('h_bardo', dict(weapon='flauta'))}
for _k, (_b, _o) in _VAR.items():
    UNITS[_k] = dict(UNITS[_b], ap=dict(UNITS[_b]['ap'], **_o))
    if _b in ANIMS: UNITS[_k]['anim'] = ANIMS[_b]

# VARIANTES DO HEROI POR ARMA EQUIPADA (o sprite muda com a arma): chave = <heroi>_<variante>; o jogo escolhe por tipo de arma (HVAR em index.html)
_VAR = {'h_guerreiro_machado': ('h_guerreiro', dict(weapon='machado')), 'h_guerreiro_martelo': ('h_guerreiro', dict(weapon='martelo_guerra')),
        'h_ladino_espadacurta': ('h_ladino', dict(weapon='espada_curta', weapon2='espada_curta')),
        'h_mago_cetro': ('h_mago', dict(weapon='cetro_arcano')), 'h_mago_varinha': ('h_mago', dict(weapon='varinha')),
        'h_clerigo_martelo': ('h_clerigo', dict(weapon='martelo_sagrado')), 'h_clerigo_cetro': ('h_clerigo', dict(weapon='cetro_sagrado')),
        'h_arqueiro_longo': ('h_arqueiro', dict(weapon='arco_longo')), 'h_bardo_flauta': ('h_bardo', dict(weapon='flauta'))}
for _k, (_b, _o) in _VAR.items():
    UNITS[_k] = dict(UNITS[_b], ap=dict(UNITS[_b]['ap'], **_o))
    if _b in ANIMS: UNITS[_k]['anim'] = ANIMS[_b]


def frames(u, kind, view):
    if kind == 'cast' and u.get('gcast'):                 # habilidade de chefe: animacao propria (nao reaproveita o ataque)
        import genanim as GA
        st = frames0(u, 'idle', view)[0]
        if u['kind'] == 'c':
            base = [f[0].convert('RGBA') for f in C.anim(view, 'cast', u['ap']['cls'], None, u['ap'], dense=1)]
        else:
            base = [f.convert('RGBA') for f in frames0(u, 'idle', view)]
        return GA.attack({'right': 'side', 'down': 'front', 'up': 'back'}.get(view, view), base, st.convert('RGBA'), u['gcast'])
    fr = frames0(u, kind, view)
    if u.get('gen') and kind in ('attack', 'hurt', 'death'):
        import genanim as GA
        st = frames0(u, 'idle', view)[0]
        return GA.build(kind, fr, view, u['gen'], st, u.get('name', 'javali'))
    return fr

def frames0(u, kind, view):
    if kind == 'quake':
        import chibi_anim3 as N3
        return N3.combo_frames(view, dict(u['ap']), 'wplant', None)
    if kind == 'crush':
        import chibi_anim3 as N3
        return N3.combo_frames(view, dict(u['ap']), 'wcrush', None)
    if kind == 'spin':
        import combo_poses as CP
        return CP.twirl(dict(u['ap']))
    if kind in COMBO_KINDS:
        import chibi_anim3 as N3
        bs, var = u['combo'][kind]
        import combo_poses as CP
        if bs in CP.TABLE and var is None: return N3.combo_frames(view, dict(u['ap']), bs, None)
        if bs == 'same' or (u['kind'] == 'c' and u['ap']['cls'] == 'archer'):
            return N3.variant(frames0(u, 'attack', view), var, view)
        return N3.combo_frames(view, dict(u['ap']), bs, var)
    k, d = u['kind'], DENS[kind]
    kk = kind
    if k == 'c' and u['ap']['cls'] == 'archer':
        return [f[0] for f in C.anim(view, 'walk', 'archer', archer_ps(kind, view), u['ap'], dense=1)]
    if k == 'c' and kind in ('attack', 'hurt', 'death') and u['ap']['cls'] != 'archer' and not (kind == 'attack' and ALIAS_CAST_ONLY):
        import chibi_anim3 as N3
        return [f[0] for f in N3.build(view, kind, dict(u['ap'], anim=u.get('anim')))]
    if k == 'c':
        if kind == 'cast' and not (u.get('cast') or u['ap']['cls'] in ('mage', 'cleric', 'archer')): kk = 'attack'
        if kind == 'run' and not u.get('run'): kk = 'walk'
        try: return [f[0] for f in C.anim(view, kk, u['ap']['cls'], None, u['ap'], dense=d)]
        except Exception as ex:
            print('  fallback', kind, view, ex); return [f[0] for f in C.anim(view, 'walk' if kind in ('run',) else 'attack', u['ap']['cls'], None, u['ap'], dense=d)]
    if kind in ('run',): kk = 'walk'
    if kind == 'cast': kk = 'attack'
    if k == 'm': return [f[0] for f in HM.anim(u['spec'], 'walk' if kk == 'run' else kk, view, d)]
    if k == 'f': return [f[0] for f in FA.anim(u['name'], 'walk' if kk == 'run' else kk, view, d)]
    if k == 'v':
        import minichefes as MC
        return [MC.vamp_img(f[0], view) for f in CRE.anim('morcego', kk, view, d)]
    if k == 'e' and kind in ('attack', 'hurt', 'death') and u['name'] in J.ENEMY and not u['name'].startswith('n_') and J.ENEMY[u['name']].get('cls') != 'archer':
        import chibi_anim3 as N3
        return [f[0] for f in N3.build(view, kind, dict(J.ENEMY[u['name']], anim=u.get('anim')))]
    if k == 'e': return J.spr(u['name'], kk, view, d)
    if k == 'b': return [f[0] for f in FA.anim(u['name'], kk, view, d)]
    return [f[0] for f in CRE.anim(u['name'], kk, view, d)]


def export(key):
    u = UNITS[key]; imgs = []; anims = {}
    if u['kind'] == 'x':                       # atlas ja montado por outro pipeline (codixel): so copia
        import shutil
        shutil.copy(os.path.join(os.path.dirname(os.path.abspath(__file__)), u['src'] + '_atlas.png'), os.path.join(OUT, f'cx_{key}_atlas.png'))
        shutil.copy(os.path.join(os.path.dirname(os.path.abspath(__file__)), u['src'] + '_atlas.json'), os.path.join(OUT, f'cx_{key}_atlas.json')); print(key, 'copiado de', u['src']); return
    kinds = ['idle', 'walk', 'run', 'attack', 'hurt', 'death', 'cast'] + (list(COMBO_KINDS) if u.get('combo') else []) + (['spin'] if u.get('twirl') else []) + (['crush', 'quake'] if u.get('twirl') else [])
    ALIAS = {}
    if u['kind'] == 'c' and not u.get('run'): ALIAS['run'] = 'walk'
    elif u['kind'] != 'c': ALIAS['run'] = 'walk'
    if u.get('gcast'): pass
    elif u['kind'] != 'c' or not (u.get('cast') or u['ap']['cls'] in ('mage', 'cleric', 'archer')): ALIAS['cast'] = 'attack'
    for kind in kinds:
        for vk, vn in VIEWS.items():
            if kind in ALIAS: anims[f'{kind}_{vk}'] = anims[f'{ALIAS[kind]}_{vk}']; continue
            if kind == 'spin' and vk != 'd': anims[f'{kind}_{vk}'] = anims['spin_d']; continue
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
