import json,base64,sys,os
H=os.path.dirname(os.path.abspath(__file__));A=H+'/../assets/'
z=json.load(open(A+'town.json'));at=json.load(open(A+'town_atlas.json'))
props=[[p['t'],p['id'],p['x'],p['y'],([[c[0],c[1],c[2]] for c in p['col']] if p.get('col') and not p['id'].startswith('b_') else None)] for p in z['props'] if p['t'] in('p','flat') and p['id'] in at]
data=dict(props=props,atlas={k:v for k,v in at.items() if k in {p[1] for p in props}},doors=[{k:d[k] for k in('nm','x','y')} for d in z['doors']],fx=[f for f in z['fx'] if f['k'] in('fire','torch','glow')])
files=dict(ground=A+'town_ground.png',atlas=A+'town_atlas.png',hw=A+'chars/guerreiro__walk.png',gw=A+'chars/guarda__walk.png',pw=A+'chars/pov_f__walk.png',lw=A+'chars/ladino_b__walk.png',bw=A+'chars/bardo__walk.png')
mode=sys.argv[1] if len(sys.argv)>1 else 'dev'
def b64(f):return 'data:image/png;base64,'+base64.b64encode(open(f,'rb').read()).decode()
src=open(H+'/town.src.html').read()
if mode=='dev':
    data['img']={k:os.path.relpath(v,H) for k,v in files.items()}
    out=src.replace('<script>/*THREE*/</script>','<script src="three.min.js"></script>')
    open(H+'/town.html','w').write(out.replace('/*DATA*/',json.dumps(data,separators=(',',':'))))
else:
    data['img']={k:b64(v) for k,v in files.items()}
    out=src.replace('<script>/*THREE*/</script>','<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>').replace('/*DATA*/',json.dumps(data,separators=(',',':')))
    out=out.replace('<!doctype html>\n<html lang="pt-BR"><head><meta charset="utf-8">\n','').replace('<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no,viewport-fit=cover">\n','').replace('</style></head><body>','</style>').replace('</script></body></html>','</script>')
    open(sys.argv[2],'w').write(out)
print('ok',mode,len(props))
