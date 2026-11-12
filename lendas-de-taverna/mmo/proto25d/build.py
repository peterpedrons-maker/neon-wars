import base64,sys,os
H=os.path.dirname(os.path.abspath(__file__));C=H+'/../assets/chars/'
src=open(H+'/index.src.html').read()
def b64(f):return 'data:image/png;base64,'+base64.b64encode(open(C+f,'rb').read()).decode()
files=dict(hw='guerreiro__walk.png',hs='guerreiro__slash.png',rw='rato__walk.png',rs='rato__slash.png',rh='rato__hurt.png')
mode=sys.argv[1] if len(sys.argv)>1 else 'dev'
if mode=='dev':
    spr='{'+','.join(f"{k}:'../assets/chars/{v}'" for k,v in files.items())+'}'
    out=src.replace('<script>/*THREE*/</script>','<script src="three.min.js"></script>').replace('/*SPRITES*/',spr)
    open(H+'/index.html','w').write(out)
elif mode=='art':
    spr='{'+','.join(f"{k}:'{b64(v)}'" for k,v in files.items())+'}'
    out=src.replace('<script>/*THREE*/</script>','<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>').replace('/*SPRITES*/',spr)
    out=out.replace('<!doctype html>\n<html lang="pt-BR"><head><meta charset="utf-8">\n','').replace('<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no,viewport-fit=cover">\n','').replace('</style></head><body>','</style>').replace('</script></body></html>','</script>')
    open(sys.argv[2],'w').write(out)
else:
    spr='{'+','.join(f"{k}:'{b64(v)}'" for k,v in files.items())+'}'
    out=src.replace('<script>/*THREE*/</script>','<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>').replace('/*SPRITES*/',spr)
    open(sys.argv[2],'w').write(out)
print('ok',mode)
