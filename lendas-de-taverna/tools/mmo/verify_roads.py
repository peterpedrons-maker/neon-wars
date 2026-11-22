"""Confere que nenhuma estrada fica obstruída por cenário sólido (rodar depois de build_mundo.py)."""
import json,glob,math,sys
A='../../mmo/assets'
SMALL={'flower','grass','tuft','pebble','reed','lily'}
bad=0
for f in sorted(glob.glob(A+'/zone_*.json')):
    Z=json.load(open(f));R=Z.get('region',{}).get('roads')
    if not R:continue
    n=0;worst=None
    for p in Z['props']:
        if p.get('k') in SMALL or (p['t']=='p' and not p.get('col')):continue
        cr=max([c[2] for c in p.get('col',[])]+[0]);sz=p.get('s') or 0;clr=46+max(cr,sz*.32)
        d=1e9
        for pts in R:
            for (ax,ay),(bx,by) in zip(pts,pts[1:]):
                vx,vy=bx-ax,by-ay;L=vx*vx+vy*vy or 1;t=max(0,min(1,((p['x']-ax)*vx+(p['y']-ay)*vy)/L));d=min(d,math.hypot(p['x']-ax-t*vx,p['y']-ay-t*vy))
        if d<clr-1:n+=1;worst=worst or (p.get('k') or p.get('id'),p['x'],p['y'],round(d))
    # parede invisível sobre a estrada (fora das bocas das saídas)
    w=0
    for c in Z.get('wallc',[]):
        x,y=c[0],c[1];d=1e9
        for pts in R:
            for (ax,ay),(bx,by) in zip(pts,pts[1:]):
                vx,vy=bx-ax,by-ay;L=vx*vx+vy*vy or 1;t=max(0,min(1,((x-ax)*vx+(y-ay)*vy)/L));d=min(d,math.hypot(x-ax-t*vx,y-ay-t*vy))
        if d<30:w+=1
    if n or w:bad+=1;print(f.split('/')[-1],'props na estrada:',n,worst,'paredes sobre a estrada:',w)
print('OK: estradas livres' if not bad else f'FALHOU em {bad} zonas');sys.exit(1 if bad else 0)
