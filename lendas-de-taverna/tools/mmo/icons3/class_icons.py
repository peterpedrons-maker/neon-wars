"""Ícones de classe (mesmo estilo dos talentos/HUD) -> mmo/assets/class/<classe>.png
Uso: python3 class_icons.py  (gera /tmp/ic/G.json), depois: node render.js && sed (OUT) comp.py"""
import json,os
C={'guerreiro':('broadsword','#ff6a4a'),'ladino':('daggers','#6ae08a'),'mago':('wizard-staff','#a98aff'),'clerigo':('holy-symbol','#ffd070'),'arqueiro':('bow-arrow','#6ae0c0'),'bardo':('lyre','#ff8ad0')}
D=json.load(open('/tmp/gi/node_modules/@iconify-json/game-icons/icons.json'))['icons']
assert not [k for k,v in C.items() if v[0] not in D]
os.makedirs('/tmp/ic',exist_ok=True);json.dump(C,open('/tmp/ic/G.json','w'))
