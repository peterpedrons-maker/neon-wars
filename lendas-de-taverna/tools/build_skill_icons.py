#!/usr/bin/env python3
"""Ícones coloridos das habilidades que o pack não traz prontos: pega silhuetas do game-icons (assets/ui-icons),
sobe 2× sem suavizar e pinta/acrescenta detalhes (gotas, brasas, rachaduras…). Saída: assets/skill-icons/*.png (64×64).
Uso: python3 tools/build_skill_icons.py   (precisa de Pillow)"""
from PIL import Image, ImageDraw
import os
ROOT=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','assets')
PARCH=(244,230,196);GREEN=(110,214,74);RED=(214,64,52);GOLD=(255,214,98);BLUE=(110,170,255);ORANGE=(255,150,50);BROWN=(201,138,74);VIOLET=(176,120,240)
def base(name,col=PARCH,flip=False):
    im=Image.open(f'{ROOT}/ui-icons/{name}.png').convert('RGBA').resize((64,64),Image.NEAREST)
    if flip:im=im.transpose(Image.FLIP_LEFT_RIGHT)
    px=im.load()
    for y in range(64):
        for x in range(64):
            r,g,b,a=px[x,y]
            if a>40:px[x,y]=(*col,255)
            else:px[x,y]=(0,0,0,0)
    return im
def recolor(im,fn):
    px=im.load()
    for y in range(64):
        for x in range(64):
            if px[x,y][3]:
                c=fn(x,y)
                if c:px[x,y]=(*c,255)
    return im
def drop(d,x,y,col,u=3):
    for i,row in enumerate(("..X..",".XXX.","XXXXX","XXXXX",".XXX.")):
        for j,ch in enumerate(row):
            if ch=='X':d.rectangle([x+j*u,y+i*u,x+j*u+u-1,y+i*u+u-1],fill=col)
    d.rectangle([x+u*2,y+u*2,x+u*2+u-1,y+u*2+u-1],fill=(255,255,255,220))  # brilho
def star(d,x,y,col,u=3):
    for dx,dy in ((0,0),(1,0),(-1,0),(0,1),(0,-1),(2,0),(-2,0),(0,2),(0,-2)):
        d.rectangle([x+dx*u,y+dy*u,x+dx*u+u-1,y+dy*u+u-1],fill=col)
def line(d,a,b,col,w=3):d.line([a,b],fill=col,width=w)
def save(im,name):im.save(f'{ROOT}/skill-icons/{name}.png');print(name)
def comp(*layers):
    out=Image.new('RGBA',(64,64),(0,0,0,0))
    for l in layers:out=Image.alpha_composite(out,l)
    return out
def draw_layer(fn):
    l=Image.new('RGBA',(64,64),(0,0,0,0));fn(ImageDraw.Draw(l));return l
os.makedirs(f'{ROOT}/skill-icons',exist_ok=True)
# Lâmina Envenenada: adaga com a ponta verde e gotas
im=recolor(base('plain-dagger'),lambda x,y:GREEN if x>34 and y<30 else None)
save(comp(im,draw_layer(lambda d:[drop(d,42,40,GREEN),drop(d,50,28,GREEN,2),drop(d,30,50,GREEN,2)])),'lamina_envenenada')
# Corte Profundo: garras + sangue
save(comp(base('claw-slashes'),draw_layer(lambda d:[drop(d,40,42,RED),drop(d,48,30,RED,2),drop(d,22,50,RED,2)])),'corte_profundo')
# Golpe Poderoso: espada com impacto
save(comp(base('broadsword'),draw_layer(lambda d:[[line(d,(48,16),(48+dx,16+dy),ORANGE,3) for dx,dy in ((12,-8),(14,2),(10,12),(2,-14))],star(d,50,14,GOLD,2)])),'golpe_poderoso')
# Grito de Guerra: elmo com ondas de som
def wave(d):
    for r,c in ((26,RED),(31,(255,120,90))):
        d.arc([32-r,32-r,32+r,32+r],-50,50,fill=c,width=3);d.arc([32-r,32-r,32+r,32+r],130,230,fill=c,width=3)
save(comp(base('horned-helm'),draw_layer(wave)),'grito_guerra')
# Escudo Aliado: escudo redondo com brilho azul
save(comp(draw_layer(lambda d:d.ellipse([6,6,58,58],outline=BLUE+(160,),width=3)),base('round-shield',(214,232,255)),draw_layer(lambda d:[star(d,52,12,BLUE,2),star(d,12,52,BLUE,2)])),'escudo_aliado')
# Golpe nas Costas: adaga com sombra roxa
save(comp(draw_layer(lambda d:[d.ellipse([10,34,54,60],fill=VIOLET+(120,)),line(d,(6,20),(24,30),VIOLET,3),line(d,(4,28),(20,36),VIOLET,2)]),base('sacrificial-dagger')),'golpe_costas')
# Tremor: punho + rachaduras no chão
def crack(d):
    pts=[(6,58),(16,52),(22,58),(32,50),(40,58),(50,52),(58,58)]
    d.line(pts,fill=BROWN,width=3)
    for x,y in ((12,46),(28,44),(46,46),(54,40)):d.rectangle([x,y,x+3,y+3],fill=BROWN)
save(comp(base('fist'),draw_layer(crack)),'tremor')
# Flecha Incendiária: flecha com a ponta em chamas
def arrow(d):
    line(d,(8,58),(38,28),(205,165,115),3)                              # haste
    for k in (0,7,14):line(d,(8+k,58-k),(2+k,52-k),(245,235,205),3)      # penas
    d.polygon([(34,34),(46,22),(52,28)],fill=(214,218,228))             # ponta
    d.polygon([(44,26),(38,12),(47,15),(50,1),(58,13),(63,22),(56,30)],fill=ORANGE)
    d.polygon([(48,25),(45,16),(51,18),(53,10),(57,19),(55,26)],fill=GOLD)
save(comp(draw_layer(arrow)),'flecha_incendiaria')
# Golpe Sagrado: espada rúnica dourada com brilho
save(comp(draw_layer(lambda d:d.ellipse([4,4,60,60],outline=GOLD+(140,),width=3)),base('broadsword',GOLD),draw_layer(lambda d:[star(d,52,10,(255,255,255),2),star(d,10,52,(255,240,180),2),star(d,54,50,(255,240,180),2)])),'golpe_sagrado')
