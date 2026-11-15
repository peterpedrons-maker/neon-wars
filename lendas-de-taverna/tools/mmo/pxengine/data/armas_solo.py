import sys; sys.path.insert(0, '.')
import chibi as C, icons_pixel as IC, pxfont
from pxrig import Grid, autoline
from PIL import Image
OUT = '/home/user/neon-wars/lendas-de-taverna/mmo/proto_pixel'
GROUPS = {
 'guerreiro': ['espada_ferro', 'espada_aco', 'espada_longa', 'montante', 'machado', 'martelo_guerra', 'espada_chamas', 'espada_gelo'],
 'ladino_cle_bardo': ['adaga_ferro', 'adaga_veneno', 'adaga_sangue', 'espada_curta', 'maca_ferro', 'maca_dourada', 'martelo_sagrado', 'florete'],
 'magia_arco': ['cajado_fogo', 'cajado_gelo', 'cajado_arcano', 'cajado_natureza', 'cajado_caveira', 'cetro_arcano', 'arco_curto', 'arco_longo', 'arco_elfico', 'arco_osso'],
}
def solo(w, N=36):
    sp = C.WEAPONS[w]; kind = sp['kind']; pal = dict(IC.IP); pal.update(w='#ffffff', Z='#fff4b0', z='#ff9a30', r='#d03a48'); pal.update(sp['pal'])
    g = Grid(N, N); hand = (9, 28)
    if kind in ('sword', 'dagger'):
        cells, tip = C.shaped_rows(hand, 135, sp['len'] if kind == 'sword' else sp['len'], sp.get('guard', 3), sp.get('shape') or ('wide' if sp.get('wide') else 'straight'), sp.get('gstyle', 'bar'), sp.get('glow'), sp.get('gem', False), sp.get('serrate', False))
    elif kind == 'staff': cells, tip = C.staff_rows(hand, 135, sp.get('len', 24), sp.get('orb', 1), sp.get('head','orb'))
    elif kind == 'mace': cells, tip = C.mace_rows(hand, 135, sp.get('len', 15), sp.get('head','flanged'))
    else:
        cells, _, _ = C.bow_rows((N // 2, N // 2), (1, -1), 0, True, sp.get('span', 11)); tip = None
    for (x, y), ch in cells.items():
        if ch not in pal: pal[ch] = '#e8e0c8'
        g.put(x, y, ch)
    autoline(g)
    return g.render(pal, {c: '#08040e' for c in pal})
S = 8
for gname, ws in GROUPS.items():
    cols = 4; rows = (len(ws) + cols - 1) // cols
    sheet = Image.new('RGBA', (cols * 40 * S, rows * 44 * S), (40, 52, 44, 255))
    for i, w in enumerate(ws):
        try: im = solo(w)
        except Exception as e: print(w, 'ERR', e); continue
        cell = Image.new('RGBA', (40, 44), (52, 70, 56, 255)); cell.alpha_composite(im, (2, 6)); pxfont.text(cell, (20, 1), w.upper().replace('_', ' '), (240, 226, 190), center=True)
        sheet.alpha_composite(cell.resize((40 * S, 44 * S), Image.NEAREST), ((i % cols) * 40 * S, (i // cols) * 44 * S))
    sheet.save(f'{OUT}/armas_{gname}.png'); print(gname, sheet.size)
