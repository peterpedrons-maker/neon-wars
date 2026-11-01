"""Gera as camadas de aparência (iguais para TODAS as classes) a partir do gerador LPC completo.
Uso: /usr/bin/python3 tools/mmo/build_look2.py <spritesheets_do_LPC> (rodar em lendas-de-taverna)
Saída: mmo/assets/look2/<sexo>/<acao>_<grupo>_<variante>.png, w_<classe>_*.png (armas) e look2.json"""
import json,os,sys
from PIL import Image
SS=sys.argv[1].rstrip('/')+'/'; LPC='assets/lpc/'; OUT='mmo/assets/look2/'
R=json.load(open('tools/mmo/char_recipes.json'))
TORSO={'leather':'torso/armour/leather/{s}/{a}.png','chainmail':'torso/chainmail/{s}/{a}.png','plate':'torso/armour/plate/{s}/{a}.png','legion':'torso/armour/legion/{s}/{a}.png','longsleeve':'torso/clothes/longsleeve/longsleeve/{s}/{a}.png'}
LEGS={'pantaloons':'legs/pantaloons/{l}/{a}.png','pants':'legs/pants/{l}/{a}.png','leggings':'legs/leggings/{l}/{a}.png'}
HAIR={'page':'hair/page/adult/{a}.png','long':'hair/long/adult/{a}.png','messy1':'hair/messy1/adult/{a}.png','bangslong':'hair/bangslong/adult/{a}.png'}
HAT={'hood':'hat/cloth/hood/adult/{a}.png','leather_cap':'hat/cloth/leather_cap/adult/{a}.png','wizard':'hat/magic/wizard/base/adult/{a}.png','bandana':'hat/cloth/bandana/adult/{a}.png'}
ACTS={'walk':'walk','hurt':'hurt','slash':'slash','shoot':'shoot','spellcast':'spellcast','slash192':'slash'}
SEX={'male':('male','male'),'female':('female','thin')}
def ld(p,root=SS):
    f=root+p
    return Image.open(f).convert('RGBA') if os.path.exists(f) else None
def place(im,over):
    if not over: return im
    out=Image.new('RGBA',(1152,768),(0,0,0,0))
    for r in range(4):
        for c in range(6): out.alpha_composite(im.crop((c*64,r*64,c*64+64,r*64+64)),(c*192+64,r*192+64))
    return out
os.makedirs(OUT,exist_ok=True);man={'torso':list(TORSO),'legs':list(LEGS),'hair':list(HAIR),'hat':list(HAT),'classes':{}}
miss=set()
for sx,(ts,ls) in SEX.items():
    os.makedirs(OUT+sx,exist_ok=True)
    for ak,fa in ACTS.items():
        over=ak=='slash192'
        skin=None
        for p in (f'body/bodies/{ts}/{fa}.png',f'head/heads/human/{ts}/{fa}.png'):
            im=ld(p)
            if im is None: miss.add(p);continue
            im=place(im,over);skin=im if skin is None else (skin.alpha_composite(im) or skin)
        size=skin.size
        def save(g,v,im):
            if im is None: return False
            c=Image.new('RGBA',size,(0,0,0,0));c.alpha_composite(place(im,over).crop((0,0,size[0],size[1])));c.save(f'{OUT}{sx}/{ak}_{g}_{v}.png',optimize=True);return True
        skin.save(f'{OUT}{sx}/{ak}_skin_0.png',optimize=True)
        for v,t in TORSO.items():
            if not save('torso',v,ld(t.format(s=ts,a=fa))): miss.add(t.format(s=ts,a=fa))
        for v,t in LEGS.items():
            if not save('legs',v,ld(t.format(l=ls,a=fa))): miss.add(t.format(l=ls,a=fa))
        for v,t in HAIR.items():
            if not save('hair',v,ld(t.format(a=fa))): miss.add(t.format(a=fa))
        for v,t in HAT.items():
            if not save('hat',v,ld(t.format(a=fa))): miss.add(t.format(a=fa))
# armas/escudos/aljava por classe (iguais ao que o jogo já usava)
for cls,rec in R.items():
    act=rec['action'];over=rec.get('oversize',False)
    key='slash192' if over else act
    man['classes'][cls]={'act':key,'cell':192 if over else 64}
    sheets={'walk':rec['walk'],'hurt':rec['hurt'],'act':(rec['actionBody'] if over else rec[act])}
    for name,paths in sheets.items():
        W,H=(1152,768) if (name=='act' and over) else Image.open(LPC+rec['walk'][0] if name!='hurt' else LPC+rec['hurt'][0]).size
        if name=='act' and not over: W,H=Image.open(LPC+rec[act][0]).size
        g={'bg':Image.new('RGBA',(W,H),(0,0,0,0)),'fg':Image.new('RGBA',(W,H),(0,0,0,0))};used={'bg':0,'fg':0}
        for p in paths:
            if p.startswith(('body/','head/','legs/','torso/','hair/','hat/')): continue
            gg='bg' if ('background' in p or 'behind' in p) else 'fg';im=ld(p,LPC)
            if im: g[gg].alpha_composite(im.crop((0,0,W,H)));used[gg]=1
        if name=='act' and over:
            for p,gg in ((rec['actionBehind'],'bg'),(rec['actionFront'],'fg')):
                im=ld(p,LPC);g[gg].alpha_composite(im.crop((0,0,W,H)));used[gg]=1
        for gg in ('bg','fg'):
            if used[gg]: g[gg].save(f'{OUT}w_{cls}_{name}_{gg}.png',optimize=True)
        man['classes'][cls].setdefault('w',{})[name]=[k for k in ('bg','fg') if used[k]]
json.dump(man,open(OUT+'look2.json','w'),indent=1)
print('faltando:',sorted(miss)[:40],len(miss))
