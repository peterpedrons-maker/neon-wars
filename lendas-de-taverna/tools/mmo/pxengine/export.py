"""Export System: gera spritesheets PNG (linhas: costas, esquerda, frente, direita) e JSON com quadros, duração, eventos e âncora."""
import json,os
import numpy as np
from PIL import Image
from .animation import build
from .renderer import lie_down
ROWS=['back','left','front','right']
class Frame:
    def __init__(s,rgba,buf):s.rgba=rgba;s.a=buf.a.copy();s.mat=buf.mat.copy();s.wm=buf.wm.copy()
def render_anim(char,name,**kw):
    poses,ms,events,loop=build(name,**kw);views={}
    for v in ('side','front','back'):
        L=[]
        for P in poses:
            B=char.draw(v,P)
            if P.get('lie'):B=lie_down(B,char.GY);B.wm[:]=False
            L.append(Frame(B.finish(),B))
        views[v]=L
    return dict(name=name,views=views,ms=ms,events=events,loop=loop,n=len(poses))
def sheet(char,A):
    W,H,n=char.W,char.H,A['n'];S=np.zeros((H*4,W*n,4),np.uint8)
    for r,(v,flip) in enumerate((('back',0),('side',1),('front',0),('side',0))):
        for i,f in enumerate(A['views'][v]):
            im=f.rgba[:,::-1] if flip else f.rgba;S[r*H:(r+1)*H,i*W:(i+1)*W]=im
    return Image.fromarray(S,'RGBA')
def export(char,anims,out):
    os.makedirs(out,exist_ok=True);atlas={'name':char.spec['name'],'cell':[char.W,char.H],'anchor':[char.W//2,char.GY],'rows':ROWS,'perspective':'3/4 (lado, frente, costas; direita = lado espelhado)','anims':{}}
    for A in anims:
        sheet(char,A).save(os.path.join(out,f"{atlas['name']}_{A['name']}.png"))
        atlas['anims'][A['name']]={'file':f"{atlas['name']}_{A['name']}.png",'frames':A['n'],'ms':A['ms'],'loop':A['loop'],'events':{str(k):v for k,v in A['events'].items()}}
    json.dump(atlas,open(os.path.join(out,atlas['name']+'.json'),'w'),indent=1);return atlas
