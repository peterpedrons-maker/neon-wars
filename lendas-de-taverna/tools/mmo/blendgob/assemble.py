"""Monta GIFs e folhas (linhas: costas, esquerda, frente, direita) a partir dos frames renderizados no Blender."""
import sys,os,json
import numpy as np
from PIL import Image
sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
from pxengine.animation import build
def lie(im,margin=26):
    a=np.rot90(im);ys=np.where(a[:,:,3]>40)[0];H=a.shape[0];dy=(H-margin)-ys.max();out=np.zeros_like(a)
    if dy>=0:out[dy:]=a[:H-dy]
    else:out[:H+dy]=a[-dy:]
    return out
def main(src,out,bg=(58,72,58)):
    os.makedirs(out,exist_ok=True);meta=json.load(open(f'{src}/meta.json'));atlas={'anims':{},'rows':['back','left','front','right']}
    for an,m in meta.items():
        n=m['frames'];poses=build(an)[0];V={}
        for v in ('front','side','back'):
            L=[]
            for i in range(n):
                im=np.array(Image.open(f'{src}/{an}_{v}_{i:02d}.png').convert('RGBA'))
                if poses[i].get('lie'):im=lie(im)
                L.append(im)
            V[v]=L
        H,W=V['front'][0].shape[:2];rows=[]
        for v,flip in(('back',0),('side',1),('front',0),('side',0)):
            r=np.concatenate([(f[:,::-1] if flip else f) for f in V['side' if v=='side' else v]],1);rows.append(r)
        Image.fromarray(np.concatenate(rows,0),'RGBA').save(f'{out}/goblin_{an}.png')
        G=[]
        for i in range(n):
            c=Image.new('RGBA',(W*3,H),(*bg,255))
            for j,v in enumerate(('front','side','back')):c.alpha_composite(Image.fromarray(V[v][i],'RGBA'),(j*W,0))
            G.append(c.convert('P',palette=Image.ADAPTIVE))
        G[0].save(f'{out}/goblin_{an}.gif',save_all=True,append_images=G[1:],duration=m['ms'],loop=0,disposal=2)
        atlas['anims'][an]={'file':f'goblin_{an}.png','frames':n,'ms':m['ms'],'loop':m['loop'],'events':m['events']}
    atlas['cell']=[W,H];json.dump(atlas,open(f'{out}/goblin.json','w'),indent=1)
if __name__=='__main__':main(sys.argv[1],sys.argv[2])
