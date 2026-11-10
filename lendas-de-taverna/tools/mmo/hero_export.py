"""Atlas pxhero_atlas.png/json do Guerreiro em pixel art (hero_pxl.px.js): lados espelhados, frente e costas. Uso: python3 hero_export.py <out/anims>"""
import sys,json
from PIL import Image,ImageOps
S=sys.argv[1];OUT='../../mmo/assets/chars/'
W,H=98,74;AX=51;cols=18
side={'walk':'w_walk','slash':'w_slash','power':'w_power','spin':'w_spin','shake':'w_shake','roar':'w_roar','hurt':'w_hurt','dodge':'w_dodge'}
fb={'walk_down':'w_front','walk_up':'w_back'}
rows=[]
def strip(f):
    im=Image.open('%s/%s.png'%(S,f)).convert('RGBA');return [im.crop((i*W,0,(i+1)*W,H)) for i in range(im.width//W)]
def mir(g):
    m=ImageOps.mirror(g);o=Image.new('RGBA',(W,H),(0,0,0,0));o.alpha_composite(m,(2*AX-(W-1),0));return o
for k,f in side.items():
    fr=strip(f);rows.append((k+'_r',fr));rows.append((k+'_l',[mir(g) for g in fr]))
for k,f in fb.items():rows.append((k,strip(f)))
A=Image.new('RGBA',(cols*W,len(rows)*H),(0,0,0,0));meta={'w':W,'h':H,'ax':AX,'ay':65,'cols':cols,'anims':{}}
for r,(k,fr) in enumerate(rows):
    meta['anims'][k]=[r*cols+i for i in range(len(fr))]
    for i,g in enumerate(fr):A.alpha_composite(g,(i*W,r*H))
A.save(OUT+'pxhero_atlas.png',optimize=True);json.dump(meta,open(OUT+'pxhero_atlas.json','w'));print(A.size,{k:len(v) for k,v in meta['anims'].items()})
