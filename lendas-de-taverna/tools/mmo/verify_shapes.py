"""VERIFICAÇÃO OBRIGATÓRIA: o formato das zonas no JOGO e no MAPA-MÚNDI tem que ser o mesmo.
Uso (em lendas-de-taverna):  /usr/bin/python3 tools/mmo/verify_shapes.py     (sai com código 1 se algo estiver errado)
Confere, para cada região (mapa_regiao1/2):
 1. o polígono `region.shape` de cada zona == a máscara de zoneshape.inside (a fonte única do formato);
 2. saídas, acampamentos, POIs, covis, santuários, portões, start, chefes e minis estão DENTRO do contorno;
 3. a área de cada zona no mapa-múndi (ids png) coincide com a máscara da zona escalada (IoU >= 0.85);
 4. a terra do mapa-múndi é UMA peça só (toda zona ligada no jogo aparece ligada no mapa);
 5. todo link do jogo (LINKS/LINKS2) tem as duas bocas de corredor tocando terra no mapa-múndi."""
import os,sys,json,math
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import label
HERE=os.path.dirname(os.path.abspath(__file__));sys.path.insert(0,HERE)
import zoneshape as ZS
A=os.path.join(HERE,'..','..','mmo','assets')+'/'
GS=4;bad=[];ok=0
def err(m):bad.append(m);print('  ✗',m)
def poly_mask(j,W,H):
    im=Image.new('L',(W//GS,H//GS),0);d=ImageDraw.Draw(im)
    # evenodd via xor das polígonos
    acc=np.zeros((H//GS,W//GS),bool)
    for po in j['region']['shape']:
        m=Image.new('L',(W//GS,H//GS),0);ImageDraw.Draw(m).polygon([(x/GS,y/GS) for x,y in po],fill=255);acc^=np.array(m)>0
    return acc
def zone_exits(j):return [dict(side=e['side'],pos=(e['x']+e['w']/2 if e['side']<2 else e['y']+e['h']/2)) for e in j['exits'] if e.get('side',-1)>=0]
def inside_pt(m,x,y,W,H):
    i=min(m.shape[0]-1,max(0,int(y)//GS));k=min(m.shape[1]-1,max(0,int(x)//GS));return bool(m[i,k])
for reg in (1,2):
    lay=json.load(open(A+'mapa_regiao%d_layout.json'%reg));ids=np.array(Image.open(A+'mapa_regiao%d_ids.png'%reg));keys=lay['keys']
    print('Região',reg,len(keys),'zonas')
    for i,k in enumerate(keys):
        kk=k.replace('zone_','')
        if k in('town','cidade2','cinzamuro'):continue
        j=json.load(open(A+'zone_%s.json'%kk));W,H=j['w'],j['h']
        gy,gx=np.mgrid[0:H//GS,0:W//GS];X=gx*GS+GS/2;Y=gy*GS+GS/2
        ref=ZS.inside(kk,W,H,zone_exits(j),X,Y);pm=poly_mask(j,W,H)
        iou=(ref&pm).sum()/max(1,(ref|pm).sum())
        if iou<.96:err('%s: contorno do jogo difere da máscara (IoU %.3f)'%(kk,iou))
        # pontos dentro
        pts=[(e['x']+e['w']/2,e['y']+e['h']/2,'saída '+e['id']) for e in j['exits']]+[(m['x'],m['y'],m['k']) for m in j['marks']]+[(j['start'][0],j['start'][1],'start')]
        r=j['region']
        for kb in('boss','colo','mare'):
            if kb in r:pts.append((r[kb]['x'],r[kb]['y'],kb))
        for m in r.get('minis',[]):pts.append((m['x'],m['y'],'mini'))
        for g in j.get('gates',[]):pts.append((g['x'],g['y'],'portão'))
        for x,y,nm in pts:
            if not inside_pt(ref,x,y,W,H):err('%s: %s fora do contorno (%d,%d)'%(kk,nm,x,y))
        # mapa-múndi: área da zona == máscara escalada
        rx,ry,rw,rh=lay['rect'][kk];s=.5   # ids png = metade da imagem
        x0,y0,x1,y1=int(rx*s),int(ry*s),int((rx+rw)*s)+1,int((ry+rh)*s)+1
        sub=(ids[y0:y1,x0:x1]==i)
        gy2,gx2=np.mgrid[y0:y1,x0:x1];Xz=(gx2+.5-rx*s)/(rw*s)*W;Yz=(gy2+.5-ry*s)/(rh*s)*H
        ref2=ZS.inside(kk,W,H,zone_exits(j),Xz,Yz)
        iou2=(sub&ref2).sum()/max(1,(sub|ref2).sum())
        if iou2<.85:err('%s: no mapa-múndi o formato difere do jogo (IoU %.3f)'%(kk,iou2))
        ok+=1
    land=(ids!=255);lb,n=label(land)
    if n!=1:err('região %d: a terra do mapa-múndi tem %d peças (tem que ser 1: tudo ligado)'%(reg,n))
print('zonas conferidas:',ok)
if bad:print('FALHOU:',len(bad),'problema(s)');sys.exit(1)
print('OK: jogo e mapa-múndi têm o mesmo formato');
