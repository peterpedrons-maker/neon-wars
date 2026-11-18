#!/usr/bin/env python3
"""Atlas dos HEROIS PERSONALIZAVEIS (criacao de personagem em pixel art).
Cada heroi vira: base careca e SEM chapeu (por arma) + mascara de cores (pele/roupa) + camadas por classe:
  cx_<chave>_atlas.png/.json   base (careca, sem chapeu); a chave inclui as variantes de arma (h_mago_cetro ...)
  cx_<chave>_mask.png          R=pele, G=roupa (mesma grade do atlas)
  cx_h_<cls>_L_f<i>.png        rosto  i=1..3 (so diferencas)           0 = padrao (ja na base)
  cx_h_<cls>_L_h<i>.png        cabelo i=0..3 (padrao, espetado, longo, moicano); 4 = careca (sem camada)
  cx_h_<cls>_L_t<i>.png        chapeu da classe por cima do cabelo i=0..4
  cx_cust.json                 rampas de cor de referencia (para recolorir em tempo de execucao)
O jogo (index.html, cxCompose) junta as camadas e recolore pele/roupa/cabelo por rampa de luminosidade.
Uso: python3 export_hero.py [classe ...]   (guerreiro mago ladino clerigo arqueiro bardo)"""
import json, os, sys
import numpy as np
from PIL import Image
import chibi as C
import export_atlas as E

OUT = E.OUT
SC = E.SC
W, H = E.W, E.H
HAIR_STY = [None, 'spiky', 'long', 'mohawk']        # 0 padrao,1 espetado,2 longo,3 moicano (4 = careca)
FACE_STY = [None, 'cold', 'sly', 'fierce']
CLASSES = {'guerreiro': 'h_guerreiro', 'mago': 'h_mago', 'ladino': 'h_ladino', 'clerigo': 'h_clerigo', 'arqueiro': 'h_arqueiro', 'bardo': 'h_bardo'}
VARS = {k: [v for v in E._VAR if v.startswith(k + '_')] for k in CLASSES.values()}


def alias(u):
    a = {}
    if u['kind'] == 'c' and not u.get('run'): a['run'] = 'walk'
    if u.get('gcast'): pass
    elif u['kind'] != 'c' or not (u.get('cast') or u['ap']['cls'] in ('mage', 'cleric', 'archer')): a['cast'] = 'attack'
    return a


def frames_of(u):
    """-> (lista de quadros RGBA 72x64, anims {nome: [indices]}) como export_atlas.export()"""
    imgs, anims, al = [], {}, alias(u)
    for kind in ['idle', 'walk', 'run', 'attack', 'hurt', 'death', 'cast']:
        for vk, vn in E.VIEWS.items():
            if kind in al: anims[f'{kind}_{vk}'] = anims[f'{al[kind]}_{vk}']; continue
            idx = []
            for im in E.frames(u, kind, vn):
                im = im.convert('RGBA')
                if im.size != (W, H): c = Image.new('RGBA', (W, H), (0, 0, 0, 0)); c.alpha_composite(im, (0, 0)); im = c
                idx.append(len(imgs)); imgs.append(im)
            anims[f'{kind}_{vk}'] = idx
    return imgs, anims


def U(key, **over):
    u = E.UNITS[key]
    return dict(u, ap=dict(u['ap'], **over))


def arr(imgs): return [np.array(i) for i in imgs]


def diff_mask(a, b): return [np.any(x != y, axis=2) for x, y in zip(a, b)]


def layer(a, m): return [Image.fromarray(np.where(mm[..., None], x, 0).astype(np.uint8), 'RGBA') for x, mm in zip(a, m)]


def bbox_union(lists):
    bb = None
    for L in lists:
        for im in L:
            b = im.getbbox()
            if b: bb = b if bb is None else (min(bb[0], b[0]), min(bb[1], b[1]), max(bb[2], b[2]), max(bb[3], b[3]))
    return bb


def atlas(imgs, crop, mode='RGBA', opaque=False):
    x0, y0, x1, y1 = crop; cw, ch = x1 - x0, y1 - y0; cols = 24; rows = (len(imgs) + cols - 1) // cols; w, h = cw * SC, ch * SC
    A = Image.new('RGBA', (cols * w, rows * h), (0, 0, 0, 255 if opaque else 0))
    for i, im in enumerate(imgs): A.alpha_composite(im.crop(crop).resize((w, h), Image.NEAREST), ((i % cols) * w, (i // cols) * h))
    return A, dict(w=w, h=h, cols=cols)


def pal_of(u):
    pal = dict(C.PALS[u['ap']['cls']]); pal.update(C.make_palette(u['ap'])); return pal


def build_class(cls):
    key = CLASSES[cls]; base_u = E.UNITS[key]; D = {}
    ap0 = dict(hat='none', hairstyle='bald', hair='castanho')
    # --- base careca/sem chapeu + mascaras ------------------------------------------------------------------
    def render_with(k, **o):
        imgs, an = frames_of(U(k, **o)); return imgs, an
    keys = [key] + VARS[key]
    R = {}
    for k in keys:
        base, an = render_with(k, **ap0)
        altc = 'roxo' if (E.UNITS[k]['ap'].get('clothes') == 'vermelho') else 'vermelho'
        if E.UNITS[k]['ap'].get('clothes') in (None,) and False: pass
        sk, _ = render_with(k, **ap0, skin='ogro')
        cl, _ = render_with(k, **ap0, clothes=altc)
        a = arr(base); ms = diff_mask(a, arr(sk)); mc = diff_mask(a, arr(cl))
        R[k] = dict(base=base, an=an, ms=ms, mc=mc)
        print(' ', k, len(base), 'quadros; pele', sum(int(m.sum()) for m in ms), 'roupa', sum(int(m.sum()) for m in mc), flush=True)
    b0 = arr(R[key]['base'])
    # --- camadas (so da arma padrao da classe) -------------------------------------------------------------
    layers = {}
    ap1 = dict(hat='none', hair='castanho')                        # cabelo castanho de referencia (recolorido no jogo)
    hair_r = {}
    for i, st in enumerate(HAIR_STY):
        im, _ = render_with(key, **ap1, hairstyle=(st or 'default'))
        hair_r[i] = im; layers[f'h{i}'] = layer(arr(im), diff_mask(arr(im), b0))
    for i, st in enumerate(FACE_STY):
        if st is None: continue
        im, _ = render_with(key, **ap0, face_style=st)
        layers[f'f{i}'] = layer(arr(im), diff_mask(arr(im), b0))
    hat0 = base_u['ap'].get('hat') or C.DEFAULT_HAT[base_u['ap']['cls']]
    for i in range(5):
        st = 'bald' if i == 4 else (HAIR_STY[i] or 'default')
        off, _ = render_with(key, **ap1, hairstyle=st)
        on, _ = render_with(key, **dict(ap1, hat=hat0), hairstyle=st)
        layers[f't{i}'] = layer(arr(on), diff_mask(arr(on), arr(off)))
        print('  chapeu', i, flush=True)
    crop = bbox_union([R[k]['base'] for k in keys] + [v for v in layers.values()])
    crop = (max(0, crop[0] - 1), max(0, crop[1] - 1), min(W, crop[2] + 1), min(H, crop[3] + 1))
    for k in keys:
        A, m = atlas(R[k]['base'], crop)
        A.save(os.path.join(OUT, f'cx_{k}_atlas.png'), optimize=True)
        json.dump(dict(w=m['w'], h=m['h'], ax=(E.AX - crop[0]) * SC, ay=(E.AY - crop[1]) * SC, cols=m['cols'], anims=R[k]['an']), open(os.path.join(OUT, f'cx_{k}_atlas.json'), 'w'))
        mk = [Image.fromarray(np.stack([ms * 255, mc * 255, np.zeros_like(ms, dtype=np.uint8), np.full(ms.shape, 255)], -1).astype(np.uint8), 'RGBA') for ms, mc in zip(R[k]['ms'], R[k]['mc'])]
        M, _ = atlas(mk, crop, opaque=True); M.convert('RGB').save(os.path.join(OUT, f'cx_{k}_mask.png'), optimize=True)
    for n, L in layers.items():
        A, _ = atlas(L, crop); A.save(os.path.join(OUT, f'cx_{key}_L_{n}.png'), optimize=True)
    pal = pal_of(base_u)
    return cls, dict(skin=[pal['S'], pal['s'], pal['p']], clothes=[pal['M'], pal['T'], pal['t']], hair=[C.HAIRS['castanho'][c] for c in 'ROrL'])


if __name__ == '__main__':
    from multiprocessing import Pool
    todo = sys.argv[1:] or list(CLASSES)
    with Pool(min(4, len(todo))) as p: res = dict(p.map(build_class, todo))
    f = os.path.join(OUT, 'cx_cust.json')
    cur = json.load(open(f)) if os.path.exists(f) else {}
    cur.update(res); json.dump(cur, open(f, 'w'))
    print('ok', list(res))
