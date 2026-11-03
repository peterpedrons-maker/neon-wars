"""Ícones de classe (mesmo estilo dos talentos/HUD) -> mmo/assets/class/<classe>.png
Uso: python3 class_icons.py  (gera /tmp/ic/G.json), depois: node render.js && sed (OUT) comp.py"""
import json,os
C={'guerreiro':('broadsword','#ff6a4a'),'ladino':('daggers','#6ae08a'),'mago':('wizard-staff','#a98aff'),'clerigo':('holy-symbol','#ffd070'),'arqueiro':('bow-arrow','#6ae0c0'),'bardo':('lyre','#ff8ad0')}
S={'sub_cavaleiro':('crested-helmet','#ff8a6a'),'sub_barbaro':('battle-axe','#e04a2a'),'sub_assassino':('dripping-blade','#8aeaa0'),'sub_armadilheiro':('claws','#4ab868'),
   'sub_piromante':('flame','#c8a0ff'),'sub_geomante':('crystal-cluster','#8a6aef'),'sub_curandeiro':('heart-plus','#ffe090'),'sub_templario':('templar-shield','#e8b040'),
   'sub_patrulheiro':('target-arrows','#8af0d8'),'sub_saraivador':('arrow-cluster','#4ac0a8'),'sub_consonante':('double-quaver','#ffa8e0'),'sub_dissonante':('sonic-boom','#e060b0')}
C.update(S)
D=json.load(open('/tmp/gi/node_modules/@iconify-json/game-icons/icons.json'))['icons']
assert not [k for k,v in C.items() if v[0] not in D]
os.makedirs('/tmp/ic',exist_ok=True);json.dump(C,open('/tmp/ic/G.json','w'))
