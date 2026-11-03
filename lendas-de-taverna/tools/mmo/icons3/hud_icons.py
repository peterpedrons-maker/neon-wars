"""Ícones do HUD principal (menu lateral e barra de baixo) no mesmo padrão dos talentos/habilidades. -> mmo/assets/hud/<id>.png"""
import json,os
Y='#ffd070';B='#6aa8ff';V='#a98aff';R='#ff6a4a';Gn='#6ae08a';O='#ffa050';C='#6ae0ff'
H={'inv':('swap-bag',O),'heroi':('visored-helm',B),'hab':('crossed-swords',R),'tal':('tree-branch',Gn),'cidade':('house',Y),'mapa':('scroll-unfurled',Y),
   'pocao':('round-potion','#ff5a5a'),'esq_roll':('run',C),'esq_blink':('magic-swirl',V),'loja':('shiny-purse',Y)}
D=json.load(open('/tmp/gi/node_modules/@iconify-json/game-icons/icons.json'))['icons']
m=[(k,v[0]) for k,v in H.items() if v[0] not in D]
assert not m,m
os.makedirs('/tmp/hd',exist_ok=True);json.dump(H,open('/tmp/hd/G.json','w'))
