"""Ícones do HUD principal (menu lateral e barra de baixo) no mesmo padrão dos talentos/habilidades. -> mmo/assets/hud/<id>.png"""
import json,os
Y='#ffd070';B='#6aa8ff';V='#a98aff';R='#ff6a4a';Gn='#6ae08a';O='#ffa050';C='#6ae0ff'
H={'inv':('knapsack',O),'heroi':('visored-helm',B),'hab':('crossed-swords',R),'tal':('tree-branch',Gn),'cidade':('portal',V),'mapa':('scroll-unfurled',Y),
   'pocao':('round-potion','#ff5a5a'),'esq_roll':('run',C),'esq_blink':('magic-swirl',V),'loja':('shiny-purse',Y)}
D=json.load(open('/tmp/gi/node_modules/@iconify-json/game-icons/icons.json'))['icons']
m=[(k,v[0]) for k,v in H.items() if v[0] not in D]
assert not m,m
import sys
if 'post' in sys.argv:
    # voltar à cidade: portal + seta dourada entrando nele
    from PIL import Image,ImageDraw
    p=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','..','mmo','assets','hud','cidade.png');im=Image.open(p).convert('RGBA');d=ImageDraw.Draw(im)
    pts=[(6,40),(22,40),(22,34),(35,45),(22,56),(22,50),(6,50)]
    d.polygon([(x+0,y) for x,y in pts],fill=(10,6,4,255))
    d.polygon([(x+1,y+1) for x,y in [(6,40),(21,40),(21,35),(32,45),(21,55),(21,50),(6,50)]],fill=(255,208,112,255))
    d.polygon([(8,42),(22,42),(22,38),(30,45),(22,52),(22,48),(8,48)],fill=(255,236,170,255))
    im.save(p);print('seta ok');sys.exit(0)
os.makedirs('/tmp/hd',exist_ok=True);json.dump(H,open('/tmp/hd/G.json','w'))
