"""Gera as CAMADAS dos personagens jogáveis (pele/pernas/torso/cabelo/chapéu/arma)
a partir do LPC em assets/lpc, para o jogo recolorir e montar o visual escolhido
na criação de personagem. Saída: mmo/assets/look/<classe>_<ação>_<grupo>.png + look.json
Uso: python3 tools/mmo/build_chars.py   (rodar na pasta lendas-de-taverna)"""
import json, os
from PIL import Image
LPC='assets/lpc/'; OUT='mmo/assets/look/'
R=json.load(open('tools/mmo/char_recipes.json'))
os.makedirs(OUT,exist_ok=True)
TORSOS={'couro':'torso/armour/leather/male/{a}.png','malha':'torso/chainmail/male/{a}.png',
        'placas':'torso/armour/plate/male/{a}.png','tecido':'torso/clothes/longsleeve/formal/male/{a}.png'}
ACTFILE={'slash':'slash','shoot':'shoot','spellcast':'spellcast'}
def grp(p):
    if p.startswith(('body/','head/')): return 'skin'
    if p.startswith('legs/'): return 'legs'
    if p.startswith('torso/'): return 'torso'
    if p.startswith('hair/'): return 'hair'
    if p.startswith('hat/'): return 'hat'
    return 'bg' if ('background' in p or 'behind' in p) else 'fg'
def load(p):
    f=LPC+p
    return Image.open(f).convert('RGBA') if os.path.exists(f) else None
manifest={}
for cls,rec in R.items():
    act=rec['action']; over=rec.get('oversize',False)
    hasHairDefault=any(p.startswith('hair/') for p in rec['walk'])
    info={'act':act,'cell':192 if over else 64,'torso':[],'groups':{}}
    sheets={'walk':rec['walk'],'hurt':rec['hurt'],'act':(rec['actionBody'] if over else rec[act])}
    for name,paths in sheets.items():
        groups={}
        W,H=(1152,768) if (name=='act' and over) else Image.open(LPC+paths[0]).size
        def put(g,im,center=False):
            if im is None: return
            if g not in groups: groups[g]=Image.new('RGBA',(W,H),(0,0,0,0))
            if center:
                for r in range(4):
                    for c in range(6):
                        groups[g].alpha_composite(im.crop((c*64,r*64,c*64+64,r*64+64)),(c*192+64,r*192+64))
            else: groups[g].alpha_composite(im.crop((0,0,W,H)))
        for p in paths:
            put(grp(p),load(p),center=(name=='act' and over))
        if name=='act' and over:
            put('bg',load(rec['actionBehind'])); put('fg',load(rec['actionFront']))
        # variantes de torso
        tdef=[p for p in paths if p.startswith('torso/')]
        if tdef and 'robe' not in tdef[0]:
            fa={'walk':'walk','hurt':'hurt','act':(act if not over else 'slash')}[name]
            for tn,tp in TORSOS.items():
                im=load(tp.format(a=fa))
                if im is None: continue
                t=Image.new('RGBA',(W,H),(0,0,0,0))
                if name=='act' and over:
                    for r in range(4):
                        for c in range(6): t.alpha_composite(im.crop((c*64,r*64,c*64+64,r*64+64)),(c*192+64,r*192+64))
                else: t.alpha_composite(im)
                t.save(f'{OUT}{cls}_{name}_torso_{tn}.png')
                if tn not in info['torso']: info['torso'].append(tn)
            groups.pop('torso',None)
        # cabelo opcional (guerreiro/arqueiro/clérigo)
        if (hasHairDefault or cls=='clerigo') and 'hair' not in groups:
            fa={'walk':'walk','hurt':'hurt','act':(act if not over else 'slash')}[name]
            im=load(f'hair/page/adult/{fa}.png')
            put('hair',im,center=(name=='act' and over))
        for g,im in groups.items():
            im.save(f'{OUT}{cls}_{name}_{g}.png'); info['groups'].setdefault(name,[]).append(g)
    # torsos que existem em todas as 3 ações
    ok=[t for t in info['torso'] if all(os.path.exists(f'{OUT}{cls}_{n}_torso_{t}.png') for n in ('walk','hurt','act'))]
    for t in info['torso']:
        if t not in ok:
            for n in ('walk','hurt','act'):
                f=f'{OUT}{cls}_{n}_torso_{t}.png'
                if os.path.exists(f): os.remove(f)
    info['torso']=ok
    info['dtorso']=next((k for k,v in TORSOS.items() if any(p==v.format(a='walk') for p in rec['walk'])),'robe' if any('robe' in p for p in rec['walk']) else None)
    info['hair']='hair' in info['groups'].get('walk',[])
    info['hairDefault']=hasHairDefault
    info['hat']='hat' in info['groups'].get('walk',[])
    info['legs']='legs' in info['groups'].get('walk',[])
    manifest[cls]=info
json.dump(manifest,open(OUT+'look.json','w'),indent=1)
print(json.dumps(manifest))
