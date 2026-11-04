"""Gera as animações do goblin ilustrado (frames PNG + folhas + GIFs) a partir das poses do motor de animação."""
import sys,os,json
import numpy as np
from PIL import Image
sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
from vecengine.goblin import Goblin
from pxengine.animation import build,TEMPLATES
def lie(im,GY):
    a=np.rot90(im);ys=np.where(a[:,:,3]>40)[0];dy=GY-ys.max()+int(GY*.0)
    out=np.zeros_like(a);h=a.shape[0]
    if dy>=0:out[dy:]=a[:h-dy]
    else:out[:h+dy]=a[-dy:]
    return out
def main(out='out_vec',cell=360,scale=.80,bg=(58,92,48)):
    os.makedirs(out,exist_ok=True);g=Goblin(cell=cell,scale=scale);meta={'cell':cell,'anims':{}}
    for name in TEMPLATES:
        poses,ms,ev,loop=build(name);F=[]
        for P in poses:
            im=g.draw(P)
            if P.get('lie'):im=lie(im,g.GY+int(4*g.k))
            F.append(im)
        sheet=np.concatenate(F,1);Image.fromarray(sheet,'RGBA').save(os.path.join(out,f'goblin_{name}.png'))
        G=[]
        for im in F:
            c=Image.new('RGBA',(cell,cell),(*bg,255));c.alpha_composite(Image.fromarray(im,'RGBA'));G.append(c.convert('P',palette=Image.ADAPTIVE))
        G[0].save(os.path.join(out,f'goblin_{name}.gif'),save_all=True,append_images=G[1:],duration=ms,loop=0,disposal=2)
        meta['anims'][name]={'file':f'goblin_{name}.png','frames':len(F),'ms':ms,'loop':loop,'events':{str(k):v for k,v in ev.items()}}
    json.dump(meta,open(os.path.join(out,'goblin.json'),'w'),indent=1);return out
if __name__=='__main__':print(main(*(sys.argv[1:2] or ['out_vec'])))
