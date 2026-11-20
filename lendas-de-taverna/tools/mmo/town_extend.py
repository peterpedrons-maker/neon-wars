"""Estende a cidade de Brumavale para o SUL (dono: "aumente a cidade, só mais para o sul, deixe o que já está construído").
Idempotente: se town.json já tem h >= NEWH não faz nada.
 - chão: as 1170 linhas de cima ficam; entram DY linhas novas (grama + estrada) e a PRAÇA DOS CAÇADORES (dois recortes da travessa de pedra existente);
 - tudo que estava na borda sul (árvores da moldura, decoração da saída) desce DY px; a saída para a Estrada desce junto;
 - mato/árvores novos preenchem as laterais do trecho novo; a praça ganha barraca, quadro de caçadas, estandartes, tochas, barris e feno;
 - `boards` (quadro de caçadas, interativo) e o NPC do Mestre Caçador ficam em index.html (TOWN_X / HUNT).
Uso (em lendas-de-taverna/tools/mmo):  /usr/bin/python3 town_extend.py"""
import json,os,random
from PIL import Image
HERE=os.path.dirname(os.path.abspath(__file__))
A=os.path.join(HERE,'..','..','mmo','assets')
DY=600;CUT=1170;NEWH=1260+DY
d=json.load(open(os.path.join(A,'town.json')))
if d['h']>=NEWH:
    print('cidade já estendida');raise SystemExit
rnd=random.Random(77)
# ---------- chão ----------
g=Image.open(os.path.join(A,'town_ground.png')).convert('RGB');W,H=g.size
ng=Image.new('RGB',(W,NEWH))
ng.paste(g.crop((0,0,W,CUT)),(0,0))
tile=g.crop((0,CUT,W,H));th=tile.height          # 90 linhas de grama + estrada reta
y=CUT;k=0
while y<NEWH-th*0:
    t=tile if k%2==0 else tile.transpose(Image.FLIP_TOP_BOTTOM)
    ng.paste(t,(0,y));y+=th;k+=1
# a moldura sul original volta para o fim
ng.paste(g.crop((0,CUT,W,H)),(0,NEWH-(H-CUT)))
# praça: dois recortes da travessa de pedra (y 950..1040), com a mesma borda irregular
bar=g.crop((0,950,W,1040))
PLAZA_Y=1360
ng.paste(bar,(0,PLAZA_Y));ng.paste(bar,(0,PLAZA_Y+62))
ng.save(os.path.join(A,'town_ground.png'),optimize=True)
# ---------- mundo ----------
for p in d['props']:
    if p['y']>=CUT:p['y']+=DY
for f in d['fx']:
    if f['y']>=CUT:f['y']+=DY
for e in d['exits']:e['y']+=DY
d['h']=NEWH
byid={}
for p in d['props']:
    byid.setdefault(p.get('id'),p)
def prop(i,x,y,col=True):
    q={'t':'p','id':i,'x':x,'y':y}
    src=byid.get(i)
    if col and src and src.get('col'):q['col']=src['col']
    return q
STALL='df9b85d47e';BANR='9304b8baba';BANG='7c7e14d6af';SIGN='bf9ca3b6d1';TORCH='0ed4292e28';BARREL='4ce7146925';BARREL2='c15bd74f53';HAY='bc4bd6de62';CRATE='325c09bfaa';BENCH='8291e154cc';LAMP='7721eadc70';LAMP2='d6ee88fa2c'
new=[
  prop(STALL,560,1412),                 # barraca da guilda (o Mestre Caçador fica na frente, em (560,1442))
  prop(BANR,505,1402),prop(BANG,615,1402),
  prop(SIGN,340,1438),                  # quadro de caçadas (interativo em d['boards'])
  prop(TORCH,316,1402),prop(TORCH,684,1402),
  prop(BARREL,676,1452),prop(BARREL2,648,1470),prop(HAY,705,1486),prop(CRATE,300,1476),
  prop(BENCH,372,1484),
]
# lampiões ao longo da estrada nova (pares a cada 170 px), fora da praça
for yy in range(1290,1790,170):
    if 1330<yy<1520:continue
    new+=[prop(LAMP2,372,yy),prop(LAMP,528,yy)]
# mato, árvores e flores nas laterais do trecho novo (mesmos ids da moldura existente)
tpl=[p for p in d['props'] if p['t'] in('p','flat') and CUT-260<p['y']<CUT and not p.get('col') and p['x']<350 or CUT-260<p['y']<CUT and not p.get('col') and p['x']>550]
tpl=[p for p in tpl if p.get('id') not in(BANR,BANG,LAMP,LAMP2,STALL,SIGN,TORCH)]
for i in range(210):
    x=rnd.randint(-10,910);yy=rnd.randint(CUT+30,NEWH-120)
    if 330<x<570:continue                       # corredor da estrada
    if 1330<yy<1520 and 270<x<730:continue      # praça
    t=rnd.choice(tpl);new.append({k:v for k,v in t.items() if k not in('x','y','_ex')}|{'x':x,'y':yy})
d['props']+=new
# a estrada precisa sair limpa pela moldura sul (sem árvores no corredor)
d['props']=[q for q in d['props'] if not (q['y']>=CUT+DY+30 and 330<q['x']<570 and not q.get('_ex'))]
d['props'].sort(key=lambda p:p['y'])
d['boards']=[{'id':'cacadas','nm':'Quadro de Caçadas','x':340,'y':1450,'ic':'treasure-map','win':'cacadas'}]
d['plaza']={'x':450,'y':PLAZA_Y,'nm':'Praça dos Caçadores'}
json.dump(d,open(os.path.join(A,'town.json'),'w'),separators=(',',':'))
print('ok',NEWH,len(new))
