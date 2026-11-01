"""Ícones das habilidades novas do MMO: glifo branco (assets/ui-icons, game-icons.net CC-BY 3.0) sobre ladrilho colorido.
Uso: /usr/bin/python3 tools/mmo/build_skill_icons2.py   (na pasta lendas-de-taverna)"""
from PIL import Image,ImageDraw
import os
OUT='mmo/assets/skills/';os.makedirs(OUT,exist_ok=True)
# id: (glifo, cor do ladrilho)
S={'n_giro':('whirlwind','#b4442a'),'n_ferro':('layered-armor','#6a7fa0'),'n_esmaga':('warhammer','#a0642a'),'n_folego':('healing','#3a9a52'),'n_terremoto':('thor-fist','#8a5a30'),
'n_sombra':('hooded-assassin','#5a4a8a'),'n_adagas':('flying-dagger','#8a8a96'),'n_veu':('cloak','#3a5a7a'),'n_execucao':('sacrificial-dagger','#a02a3a'),'n_laminas':('tornado-discs','#6a3a8a'),
'n_raio':('lightning-helix','#3a7ac8'),'n_gelo':('snowflake-1','#4aa8d0'),'n_barreira':('magic-shield','#5a5ac0'),'n_fogo':('fire-gem','#d0502a'),'n_cataclismo':('crystal-ball','#8a3ab0'),
'n_cura':('heart-plus','#3a9a52'),'n_martelo':('warhammer','#c0a02a'),'n_bencao':('holy-symbol','#d0b040'),'n_chama':('sunrise','#d07a2a'),'n_ressurgir':('sparkles','#40b0a0'),
'n_perfura':('arrow-cluster','#6a8a3a'),'n_chuva':('target-arrows','#3a7a5a'),'n_foco':('bullseye','#c04a3a'),'n_gelida':('snowflake-1','#5a9ac8'),'n_tempestade':('bow-arrow','#3a6ac0'),
'n_melodia':('lyre','#3a9a52'),'n_dissonante':('harp','#a04a8a'),'n_sinfonia':('drama-masks','#c0802a'),'n_balada':('skull-staff','#5a8a3a'),'n_crescendo':('winged-scepter','#c04a2a')}
def hexc(h):return tuple(int(h[i:i+2],16) for i in (1,3,5))
for k,(g,c) in S.items():
    base=hexc(c);W=64;im=Image.new('RGBA',(W,W),(0,0,0,0));d=ImageDraw.Draw(im)
    for y in range(W):
        t=y/(W-1);col=tuple(int(base[i]*(1.25-.55*t)) for i in range(3))
        d.line([(0,y),(W,y)],fill=tuple(min(255,v) for v in col)+(255,))
    d.rectangle([0,0,W-1,W-1],outline=(20,12,8,255),width=2);d.rectangle([2,2,W-3,W-3],outline=(255,235,170,120),width=1)
    gl=Image.open('assets/ui-icons/'+g+'.png').convert('RGBA');gl=gl.resize((48,48),Image.NEAREST)
    sh=Image.new('RGBA',gl.size,(0,0,0,0));sh.paste((0,0,0,160),mask=gl.split()[3])
    im.alpha_composite(sh,(10,12));im.alpha_composite(gl,(8,9))
    im.save(OUT+k+'.png',optimize=True)
print(len(S))
