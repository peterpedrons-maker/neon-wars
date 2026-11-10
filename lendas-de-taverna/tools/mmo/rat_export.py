"""Monta o atlas ratking_atlas.png/json do Rei dos Ratos a partir das tiras do pxl (rat_pxl.px.js, build em out/anims). Uso: python3 rat_export.py <pasta out/anims>"""
import sys,json
from PIL import Image
S=sys.argv[1];OUT='../../mmo/assets/chars/'
names={'idle':'rat_idle','walk':'rat_walk','atk1':'rat_atk1','atk2':'rat_atk2','atk3':'rat_atk3','hurt':'rat_hurt','die':'rat_die','cast':'rat_cast','plague':'rat_plague','dig':'rat_dig'}
W,H=98,74;cols=18;A=Image.new('RGBA',(cols*W,len(names)*H),(0,0,0,0));meta={'w':W,'h':H,'ax':45,'ay':65,'cols':cols,'anims':{}}
for r,(k,f) in enumerate(names.items()):
    im=Image.open('%s/%s.png'%(S,f)).convert('RGBA');n=im.width//W;meta['anims'][k]=[r*cols+i for i in range(n)]
    for i in range(n):A.alpha_composite(im.crop((i*W,0,(i+1)*W,H)),(i*W,r*H))
A.save(OUT+'ratking_atlas.png',optimize=True);json.dump(meta,open(OUT+'ratking_atlas.json','w'));print(A.size,{k:len(v) for k,v in meta['anims'].items()})
