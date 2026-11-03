"""Ícones dos 126 talentos: glifos do game-icons.net (CC BY 3.0) pintados no mesmo estilo dos ícones de habilidade (placa escura, brilho radial, 3 faixas de cor).
Uso: python3 talentos.py  (precisa de /tmp/gi com @iconify-json/game-icons e do playwright) -> mmo/assets/talents/<id>.png"""
import json,os,subprocess,sys
R='#ff6a4a';B='#6aa8ff';Y='#ffd070';V='#a98aff';C='#6ae0ff';Gn='#6ae08a';O='#ffa050';K='#ffc83a'
T={
# guerreiro
'gf1':('mailed-fist',R),'gf2':('blood',R),'gf3':('axe-swing',R),'gf4':('scar-wound',R),'gf5':('chopped-skull',R),'gf6':('bear-head',R),'gfk':('horned-helm',K),
'gb1':('leather-armor',B),'gb2':('breastplate',B),'gb3':('turtle-shell',B),'gb4':('lungs',B),'gb5':('spiked-shield',B),'gb6':('standing-potion',B),'gbk':('castle',K),
'gc1':('thor-fist',Y),'gc2':('hammer-drop',Y),'gc3':('shiny-purse',Y),'gc4':('medal',Y),'gc5':('open-treasure-chest',Y),'gc6':('attached-shield',Y),'gck':('imperial-crown',K),
# ladino
'la1':('broad-dagger',R),'la2':('eye-target',R),'la3':('poison-bottle',R),'la4':('backstab',R),'la5':('thrown-daggers',R),'la6':('daemon-skull',R),'lak':('sacrificial-dagger',K),
'ls1':('footprint',V),'ls2':('wind-slap',V),'ls3':('cloak',V),'ls4':('hood',V),'ls5':('run',V),'ls6':('shadow-follower',V),'lsk':('ghost',K),
'lp1':('shiny-purse',Y),'lp2':('treasure-map',Y),'lp3':('open-book',Y),'lp4':('clover',Y),'lp5':('hand-bag',Y),'lp6':('magic-potion',Y),'lpk':('ghost-ally',K),
# mago
'ma1':('concentration-orb',V),'ma2':('comet-spark',V),'ma3':('sound-waves',V),'ma4':('unstable-orb',V),'ma5':('hourglass',V),'ma6':('broken-shield',V),'mak':('dragon-orb',K),
'mt1':('magic-swirl',C),'mt2':('portal',C),'mt3':('magic-shield',C),'mt4':('feathered-wing',C),'mt5':('empty-hourglass',C),'mt6':('open-palm',C),'mtk':('clockwork',K),
'ms1':('spell-book',Y),'ms2':('bubbling-flask',Y),'ms3':('meditation',Y),'ms4':('scroll-unfurled',Y),'ms5':('all-seeing-eye',Y),'ms6':('stone-bust',Y),'msk':('brain',K),
# clerigo
'cf1':('warhammer',Y),'cf2':('hand-of-god',Y),'cf3':('flame',Y),'cf4':('weight-scale',Y),'cf5':('angel-wings',Y),'cf6':('sun-radiations',Y),'cfk':('cross-shield',K),
'cp1':('chest-armor',B),'cp2':('heart-armor',B),'cp3':('magic-shield',B),'cp4':('steeltoe-boots',B),'cp5':('bolt-shield',B),'cp6':('sun-spear',B),'cpk':('greek-temple',K),
'cc1':('healing',Gn),'cc2':('health-potion',Gn),'cc3':('hand-bandage',Gn),'cc4':('glass-heart',Gn),'cc5':('coins',Gn),'cc6':('prayer',Gn),'cck':('holy-grail',K),
# arqueiro
'ap1':('bow-arrow',O),'ap2':('dead-eye',O),'ap3':('barbed-arrow',O),'ap4':('broadhead-arrow',O),'ap5':('bow-string',O),'ap6':('armor-downgrade',O),'apk':('eagle-head',K),
'aa1':('leather-boot',Gn),'aa2':('run',Gn),'aa3':('lightning-bow',Gn),'aa4':('robin-hood-hat',Gn),'aa5':('wind-slap',Gn),'aa6':('arrow-wings',Gn),'aak':('tornado',K),
'ac1':('paw-print',Y),'ac2':('animal-hide',Y),'ac3':('wolf-head',Y),'ac4':('wolf-trap',Y),'ac5':('meat',Y),'ac6':('stag-head',Y),'ack':('saber-toothed-cat-head',K),
# bardo
'bm1':('drum',O),'bm2':('metronome',O),'bm3':('flute',O),'bm4':('lyre',O),'bm5':('musical-notes',O),'bm6':('musical-score',O),'bmk':('harp',K),
'bi1':('drama-masks',Y),'bi2':('two-coins',Y),'bi3':('gift-of-knowledge',Y),'bi4':('ceremonial-mask',Y),'bi5':('moon',Y),'bi6':('quill',Y),'bik':('laurel-crown',K),
'bh1':('sound-waves',Gn),'bh2':('ballerina-shoes',Gn),'bh3':('magic-shield',Gn),'bh4':('sonic-shout',Gn),'bh5':('healing',Gn),'bh6':('echo-ripples',Gn),'bhk':('angel-wings',K)}
D=json.load(open('/tmp/gi/node_modules/@iconify-json/game-icons/icons.json'))['icons']
miss=[(k,v[0]) for k,v in T.items() if v[0] not in D]
if miss:print('FALTAM',miss);sys.exit(1)
os.makedirs('/tmp/tl',exist_ok=True);json.dump(T,open('/tmp/tl/G.json','w'));print(len(T),'ok')
