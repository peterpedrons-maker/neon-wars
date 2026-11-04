"""Renderiza as animações do goblin (poses do motor pxengine) em 3 vistas -> frames PNG."""
import sys,os,time,json
sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
sys.argv=[sys.argv[0]]+sys.argv[1:]
from blendgob.goblin import *
from pxengine.animation import build
def main(out,anims,views):
    os.makedirs(out,exist_ok=True);meta={}
    for an in anims:
        poses,ms,ev,loop=build(an);meta[an]=dict(frames=len(poses),ms=ms,events={str(k):v for k,v in ev.items()},loop=loop)
        for v in views:
            set_view(co,v,target=(0,.04,.62))
            for i,P in enumerate(poses):
                t=time.time();pose(P);render(f'{out}/{an}_{v}_{i:02d}.png');print(an,v,i,round(time.time()-t,1),flush=True)
    json.dump(meta,open(f'{out}/meta.json','w'),indent=1)
if __name__=='__main__':
    main(sys.argv[1],sys.argv[2].split(','),sys.argv[3].split(','))
