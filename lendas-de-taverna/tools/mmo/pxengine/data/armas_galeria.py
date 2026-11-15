import sys; sys.path.insert(0, '.')
import chibi as C
from PIL import Image, ImageDraw
import pxfont
OUT = '/home/user/neon-wars/lendas-de-taverna/mmo/proto_pixel'
GROUPS = {
 'espadas': ['espada_ferro', 'espada_aco', 'espada_longa', 'montante', 'espada_larga', 'katana', 'cimitarra', 'florete', 'facao', 'espada_dourada', 'espada_chamas', 'espada_gelo'],
 'impacto': ['machado', 'maca_ferro', 'maca_dourada', 'martelo_sagrado', 'serra_cruel', 'adaga_ferro', 'adaga_veneno', 'adaga_sangue'],
 'magia_arco': ['cajado_fogo', 'cajado_gelo', 'cajado_arcano', 'cajado_natureza', 'cajado_caveira', 'arco_curto', 'arco_longo', 'arco_elfico', 'arco_osso'],
}
def cls_of(w):
    if w.startswith('cajado'): return 'mage'
    if w.startswith('arco'): return 'archer'
    if w.startswith('adaga'): return 'rogue'
    if w.startswith('maca') or w.startswith('martelo'): return 'cleric'
    return 'warrior'
def frame(w):
    cls = cls_of(w); ap = dict(cls=cls, weapon=w, hat='none' if cls != 'mage' else 'wizard')
    if cls == 'rogue': ap['weapon2'] = w
    if cls == 'archer':
        import export_atlas as X
        ps = X.archer_ps('attack', 'right'); return C.anim('right', 'walk', 'archer', ps, ap, dense=1)[5][0]
    fr = C.anim('right', 'attack', cls, None, ap, dense=1)
    return fr[6][0]
S = int(sys.argv[1]) if len(sys.argv) > 1 else 4
for g, ws in GROUPS.items():
    cols = 4; rows = (len(ws) + cols - 1) // cols
    sheet = Image.new('RGBA', (cols * 72 * S, rows * 80 * S), (40, 52, 44, 255))
    for i, w in enumerate(ws):
        try: im = frame(w)
        except Exception as e: print(w, e); continue
        cell = Image.new('RGBA', (72, 80), (52, 70, 56, 255)); cell.alpha_composite(im, (0, 14)); pxfont.text(cell, (36, 2), w.upper().replace('_', ' '), (240, 226, 190), center=True)
        sheet.alpha_composite(cell.resize((72 * S, 80 * S), Image.NEAREST), ((i % cols) * 72 * S, (i // cols) * 80 * S))
    sheet.save(f'{OUT}/armas_{g}.png'); print(g, sheet.size)
