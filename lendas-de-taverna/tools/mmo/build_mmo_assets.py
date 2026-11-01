# Exporta atlas + mapa da zona 1 para ../assets. Requer PACK_DIR (pack Pixel Crawler) e o numpy/scipy/Pillow.
import os,sys,json,hashlib,shutil
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'world.py')).read())
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','mmo','assets')
Z=1.5
def zs(im):return im.resize((max(1,int(im.width*Z)),max(1,int(im.height*Z))),Image.NEAREST)
ground=zs(GROUND);ground.convert('RGB').save(os.path.join(OUT,'zone1_ground.png'),optimize=True)
sprs={};meta=[]
def reg(img,anc):
    img=zs(img);h=hashlib.md5(img.tobytes()+bytes(str(img.size),'ascii')).hexdigest()[:10]
    if h not in sprs:sprs[h]=(img,(int(anc[0]*Z),int(anc[1]*Z)))
    return h
props=[]
for p in PROPS:
    if p.get('fire'):
        props.append(dict(t='fire',x=round(p['x']*Z),y=round(p['y']*Z),small=bool(p.get('small'))));continue
    if p.get('flat'):
        s=p['spr'];props.append(dict(t='flat',id=reg(s,(s.width//2,s.height)),x=round(p['x']*Z),y=round(p['y']*Z)));continue
    props.append(dict(t='p',id=reg(p['spr'],p['anc']),x=round(p['x']*Z),y=round(p['y']*Z)))
for i,f in enumerate(BFIRE):reg_id=reg(f,(16,32));sprs['bf%d'%i]=sprs.pop(reg_id)
for i,f in enumerate(FIRE):reg_id=reg(f,(16,48));sprs['fi%d'%i]=sprs.pop(reg_id)
# empacota (prateleiras)
items=sorted(sprs.items(),key=lambda kv:-kv[1][0].height);W=1024;x=y=sh=0;pos={}
for k,(im,anc) in items:
    if x+im.width+1>W:x=0;y+=sh+1;sh=0
    pos[k]=(x,y,im.width,im.height,anc[0],anc[1]);x+=im.width+1;sh=max(sh,im.height)
atlas=Image.new('RGBA',(W,y+sh+1),(0,0,0,0))
for k,(im,anc) in items:atlas.alpha_composite(im,pos[k][:2])
atlas.save(os.path.join(OUT,'atlas.png'),optimize=True)
json.dump({k:list(v) for k,v in pos.items()},open(os.path.join(OUT,'atlas.json'),'w'))
# pontos de nascimento: longe de árvores e do rio, dentro do campo
import random
rr=random.Random(5);solid=[(p['x'],p['y']) for p in props if p['t']=='p']
spawns=[]
OPENS=(int(150*Z),int(240*Z),int(620*Z),int(840*Z))
for _ in range(4000):
    if len(spawns)>=18:break
    x=rr.randrange(OPENS[0],OPENS[2]);y=rr.randrange(OPENS[1],OPENS[3])
    if any((x-a)**2+(y-b)**2<44**2 for a,b in solid):continue
    if any((x-a)**2+(y-b)**2<120**2 for a,b in spawns):continue
    if ((x-POND_C[0]*Z)/(POND_C[2]*Z+30))**2+((y-POND_C[1]*Z)/(POND_C[3]*Z+30))**2<1:continue
    if PLAZA[0]*Z-40<x<PLAZA[2]*Z+40 and PLAZA[1]*Z-40<y<PLAZA[3]*Z+260:continue
    spawns.append((x,y))
zone=dict(w=ground.width,h=ground.height,props=props,spawns=spawns,plaza=[round(v*Z) for v in PLAZA],pond=[round(v*Z) for v in POND_C],
          road=[[round(a*Z),round(b*Z)] for a,b in poly_pts(ROAD,30)+poly_pts(ROAD2,30)],start=[round(150*Z),round(420*Z)],boss=[round(360*Z),round(110*Z)])
json.dump(zone,open(os.path.join(OUT,'zone1.json'),'w'),separators=(',',':'))
print('props',len(props),'sprites',len(sprs),'spawns',len(spawns),'atlas',atlas.size)
# personagens (LPC) já exportados
CH=os.path.join(OUT,'chars')
for n in ['guerreiro','ladino','mago','clerigo','arqueiro','bardo']:
    for k in ['walk','hurt','slash','spellcast','shoot']:
        f=f'/tmp/idle/{n}__{k}.png'
        if os.path.exists(f):shutil.copy(f,CH)
for n in ['goblin','esqueleto','javali','rato','ogro']:
    for k in ['walk','hurt','slash']:shutil.copy(f'/tmp/idle/{n}__{k}.png',CH)
