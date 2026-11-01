import json
G={ # id: (glifo, cor)
'meteoros':('meteor-impact','#ff8a2a'),'tremor':('earth-crack','#c9a066'),
'n_giro':('spinning-sword','#ff9a50'),'n_ferro':('layered-armor','#9ab0d0'),'n_esmaga':('hammer-drop','#e0a040'),'n_folego':('health-potion','#5ee07a'),'n_terremoto':('quake-stomp','#c9905a'),
'n_sombra':('shadow-follower','#a07aff'),'n_adagas':('thrown-daggers','#c8d4e8'),'n_veu':('two-shadows','#7a90d0'),'n_execucao':('backstab','#ff4a4a'),'n_laminas':('spinning-blades','#d8e4f0'),
'n_raio':('focused-lightning','#7ac8ff'),'n_gelo':('snowflake-2','#8ae8ff'),'n_barreira':('magic-shield','#7a8aff'),'n_fogo':('fire-bomb','#ff7a2a'),'n_cataclismo':('burning-meteor','#ff5a2a'),
'n_cura':('healing','#5ee07a'),'n_martelo':('thor-hammer','#ffd860'),'n_bencao':('holy-symbol','#ffe27a'),'n_chama':('sunbeams','#ffc050'),'n_ressurgir':('angel-wings','#aaffe0'),
'n_perfura':('barbed-arrow','#a0d060'),'n_chuva':('arrow-cluster','#e8d8a8'),'n_foco':('target-arrows','#ff6a50'),'n_gelida':('ice-bolt','#8ac8ff'),'n_tempestade':('arrow-flights','#6aa0ff'),
'n_melodia':('musical-notes','#5ee07a'),'n_dissonante':('sound-waves','#e070e0'),'n_sinfonia':('musical-score','#ffc060'),'n_balada':('screaming','#b070e0'),'n_crescendo':('sonic-shout','#ffd070'),
's_cav1':('mounted-knight','#9ab8ff'),'s_cav2':('attached-shield','#6a9aff'),'s_cav3':('sun-spear','#ffe28a'),
's_bar1':('enrage','#ff4a3a'),'s_bar2':('axe-swing','#ff7a3a'),'s_bar3':('claw-slashes','#d03a3a'),
's_ass1':('dripping-knife','#e04a6a'),'s_ass2':('ninja-heroic-stance','#8a6aff'),'s_ass3':('ninja-mask','#7a7aaa'),
's_arm1':('wolf-trap','#c0a050'),'s_arm2':('fishing-net','#6ad090'),'s_arm3':('knife-thrust','#a0c060'),
's_pir1':('explosion-rays','#ff6a2a'),'s_pir2':('fire-breath','#ff4a1a'),'s_pir3':('fragmented-meteor','#ff9a3a'),
's_geo1':('stone-block','#c9a066'),'s_geo2':('earth-spit','#b08a50'),'s_geo3':('rock-golem','#a08060'),
's_cur1':('healing-shield','#5ee07a'),'s_cur2':('holy-water','#7affd0'),'s_cur3':('sparkles','#c0ffe0'),
's_tem1':('rune-sword','#ffe27a'),'s_tem2':('sun-radiations','#fff0a0'),'s_tem3':('winged-scepter','#ffd070'),
's_pat1':('eagle-head','#ffb050'),'s_pat2':('eye-target','#ff7a3a'),'s_pat3':('archer','#6ad090'),
's_sar1':('arrow-flights','#e8d8a8'),'s_sar2':('cluster-bomb','#ff7a2a'),'s_sar3':('multiple-targets','#6aa0ff'),
's_con1':('lyre','#5ee07a'),'s_con2':('pan-flute','#ffc060'),'s_con3':('bell-shield','#8ac8ff'),
's_dis1':('harp','#e070c0'),'s_dis2':('death-skull','#a050d0'),'s_dis3':('drama-masks','#ff70a0')}
d=json.load(open('/tmp/gi/node_modules/@iconify-json/game-icons/icons.json'))['icons']
miss=[(k,v[0]) for k,v in G.items() if v[0] not in d]
print('faltam',miss)
json.dump(G,open('/tmp/ic/G.json','w'))
