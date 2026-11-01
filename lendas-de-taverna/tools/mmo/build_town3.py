"""Cidade a partir da arte de IA (town_ai.jpg): chão = imagem, prédios/árvores viram camadas por cima do herói,
colisões e portas marcadas à mão. Uso: /usr/bin/python3 build_town3.py   (portas e interiores continuam do build_town2)"""
import os,json,sys
from PIL import Image,ImageDraw
HERE=os.path.dirname(os.path.abspath(__file__));OUT=os.path.join(HERE,'..','..','mmo','assets')
K=0.8
src=Image.open(os.path.join(HERE,'town_ai.jpg')).convert('RGBA')
W0,H0=src.size;GW,GH=round(W0*K),round(H0*K)
ground=src.resize((GW,GH),Image.LANCZOS)
S=lambda v:round(v*K)
sprs={};props=[]
def reg(img,anc,name):sprs[name]=(img,(round(anc[0]),round(anc[1])));return name
blank=reg(Image.new('RGBA',(2,2),(0,0,0,0)),(1,1),'blank')
def col_line(x0,x1,y,r=8,step=14):return [[S(x),S(y),r] for x in range(x0,x1,step)]
def overlay(name,box,base,cols,top_only=True):
    x0,y0,x1,y1=box;sp=ground.crop((S(x0),S(y0),S(x1),S(base)))
    reg(sp,(sp.width/2,sp.height),name)
    props.append(dict(t='p',id=name,x=S((x0+x1)/2),y=S(base),col=cols))
# prédios: caixa (x0,y0,x1,y1) em px da imagem, base = linha dos pés, porta
B=[('fer',(55,270,325,570),540,(245,545)),('mes',(475,215,715,560),550,(540,572)),('cof',(510,675,725,900),885,(570,900)),
   ('mer',(50,660,275,910),885,(190,905)),('alq',(40,930,330,1190),1150,(220,1170)),('lei',(450,855,760,1200),1160,(565,1180))]
NAMES={'fer':'Ferreiro','mes':'Mestre de Classe','cof':'Cofre','mer':'Mercador','alq':'Alquimista','lei':'Leilão'}
ICON={'fer':'anvil','mes':'holy-symbol','cof':'locked-chest','mer':'scales','alq':'health-potion','lei':'coins'}
doors=[]
for k,box,base,door in B:
    x0,y0,x1,y1=box
    cols=[]
    for x in range(x0+8,x1-8,14):
        if abs(x-door[0])<26:continue
        cols.append([S(x)-S((x0+x1)/2),-4,8])
    overlay('b_'+k,box,base,cols)
    doors.append(dict(id=k,nm=NAMES[k],x=S(door[0]),y=S(door[1]),w=S(x1-x0),h=S(base-y0),room='int_'+k,ic=ICON[k]))
# portal
px0,py0,px1,py1=318,20,452,185
overlay('portal_arch',(px0,py0,px1,py1),178,[[S(-52),-4,10],[S(52),-4,10]])
# árvores grandes (copas por cima): (cx,base,largura,altura)
T=[(120,215,230,215),(300,95,150,95),(610,200,235,200),(515,100,140,100),(25,420,80,150),(745,400,100,170),(30,1060,110,150),(75,1340,200,180),(610,1360,230,160),(755,1060,60,140)]
for i,(cx,base,w,h) in enumerate(T):
    box=(max(0,cx-w//2),max(0,base-h),min(W0,cx+w//2),base)
    overlay('t%d'%i,box,base,[[0,-2,S(14)]])
# colisões soltas (sem imagem): fonte, barris, lampiões, bancadas
for (x,y,r) in [(385,680,56),(527,150,12),(535,170,10),(40,450,10),(320,445,10),(165,880,10),(45,815,10),(385,830,8),(455,835,8),(440,470,8),(738,1130,10),(745,1090,10),(180,1220,10),(300,1020,12),(70,1120,10),(720,535,10),(140,590,22),(215,545,16),(60,610,12)]:
    props.append(dict(t='p',id=blank,x=S(x),y=S(y),col=[[0,0,S(r)]]))
# bordas do mundo
doors_json=doors
atl_items=sorted(sprs.items(),key=lambda kv:-kv[1][0].height);Wd=1024;x=y=sh=0;pos={}
for k,(im,a) in atl_items:
    if x+im.width+1>Wd:x=0;y+=sh+1;sh=0
    pos[k]=(x,y,im.width,im.height,a[0],a[1]);x+=im.width+1;sh=max(sh,im.height)
atlas=Image.new('RGBA',(Wd,y+sh+1),(0,0,0,0))
for k,(im,a) in atl_items:atlas.alpha_composite(im,pos[k][:2])
atlas.save(os.path.join(OUT,'town_atlas.png'),optimize=True);json.dump({k:list(v) for k,v in pos.items()},open(os.path.join(OUT,'town_atlas.json'),'w'))
ground.convert('RGB').save(os.path.join(OUT,'town_ground.png'),optimize=True)
props.sort(key=lambda p:p['y'])
town=dict(w=GW,h=GH,props=props,start=[S(385),S(790)],portal=dict(x=S(385),y=S(170),stand=[S(385),S(215)]),
 npcs=[dict(id='gua',nm='Guarda do Portal',sh='guarda',x=S(385),y=S(230),ic='treasure-map',row=2,win='portal')],
 vill=[dict(sh='pov_f',x=S(300),y=S(800)),dict(sh='ladino_b',x=S(470),y=S(950)),dict(sh='bardo',x=S(380),y=S(1050))],doors=doors_json)
json.dump(town,open(os.path.join(OUT,'town.json'),'w'),separators=(',',':'))
print('ok',GW,GH,len(props))
# debug
dbg=ground.copy();d=ImageDraw.Draw(dbg)
for p in props:
    for c in p.get('col',[]):d.ellipse((p['x']+c[0]-c[2],p['y']+c[1]-c[2],p['x']+c[0]+c[2],p['y']+c[1]+c[2]),outline=(255,0,0,255))
for dr in doors:d.rectangle((dr['x']-4,dr['y']-4,dr['x']+4,dr['y']+4),fill=(255,255,0,255))
dbg.save('/tmp/mock/town3_debug.png')
