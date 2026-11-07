"""Corta as 3 folhas do Morcego-Vampiro (mini-chefe), normaliza a escala e gera GIFs. Uso: python3 cut_vampbat.py <pasta_saida>"""
import sys,os
import numpy as np
from PIL import Image,ImageDraw
import cut_grid
UP='/root/.claude/uploads/3ffd125f-a99a-599e-8554-f2b481e86fc1/'
SH=[(UP+'5b2ca6e6-image.jpg',6,5,[('idle',6),('fly',6),('bite',6),('hurt0',3),('bite2',6)]),
    (UP+'de81bdf2-image.jpg',6,3,[('dive',6),('screech',6),('summon',6)]),
    (UP+'e3b50f28-image.jpg',6,3,[('hurt',4),('death',6),('rage',6)])]
def cells(path,nc,nr,rows):
    im=Image.open(path).convert('RGB');W,H=im.size;xs=[round(W*i/nc) for i in range(nc+1)];ys=[round(H*i/nr) for i in range(nr+1)];out={}
    for r,(name,n) in enumerate(rows):
        fr=[]
        for c in range(n):
            cell=im.crop((xs[c]+6,ys[r]+6,xs[c+1]-6,ys[r+1]-6));a=cut_grid.clean(cut_grid.key(cell));fr.append(Image.fromarray(a,'RGBA'))
        out[name]=fr
    return out
def bb(f):return f.getchannel('A').getbbox()
def load():
    parts=[cells(*s) for s in SH];ref=np.median([bb(f)[2]-bb(f)[0] for f in parts[0]['idle']])
    res={}
    for i,p in enumerate(parts):
        if i==0:k=1.0
        else:
            w=np.median([bb(f)[2]-bb(f)[0] for f in (p['summon'][-2:] if 'summon' in p else p['hurt'][:1]+p['death'][:1])]);k=ref/w
        for n,fr in p.items():res[n]=[f.resize((max(1,int(f.width*k)),max(1,int(f.height*k))),Image.NEAREST) for f in fr]
        print('folha',i+1,'escala',round(k,2))
    return res
def stack(fr):
    tr=[f.crop(bb(f)) for f in fr];cw=max(t.width for t in tr)+16;ch=max(t.height for t in tr)+16;out=[]
    for t in tr:
        c=Image.new('RGBA',(cw,ch),(0,0,0,0));c.alpha_composite(t,((cw-t.width)//2,(ch-t.height)//2));out.append(c)
    return out
if __name__=='__main__':
    out=sys.argv[1];os.makedirs(out,exist_ok=True);A=load();BG=(34,30,44,255)
    def gif(name,fr,dur,sc=1.6):
        st=stack(fr);w,h=st[0].size;ims=[]
        for f in st:
            g=f.resize((int(w*sc),int(h*sc)),Image.NEAREST);bg=Image.new('RGBA',g.size,BG);bg.alpha_composite(g);ims.append(bg.convert('RGB').quantize(64,dither=Image.Dither.NONE))
        ims[0].save(f'{out}/vamp_{name}.gif',save_all=True,append_images=ims[1:],duration=dur,loop=0,disposal=2)
    gif('parado',A['idle'],[130]*6);gif('voo',A['fly'],[85]*6);gif('mordida',A['bite'],[120,100,100,130,110,120]);gif('mordida2',A['bite2'],[120,100,100,130,110,120])
    gif('mergulho',A['dive'],[130,100,100,110,130,140]);gif('grito',A['screech'],[140,120,110,160,120,120]);gif('invocar',A['summon'],[140,110,110,160,120,120])
    gif('dano',A['hurt'],[110,120,130,150]);gif('morte',A['death'],[110,110,130,150,200,300]);gif('furia',A['rage'],[140,110,100,110,110,110])
    # contato
    names=['idle','fly','bite','bite2','dive','screech','summon','hurt','death','rage'];S=.55;rows=[]
    for n in names:
        st=stack(A[n]);w,h=st[0].size;r=Image.new('RGB',(int(w*S)*6,int(h*S)),BG[:3])
        for i,f in enumerate(st):
            bg=Image.new('RGBA',f.size,BG);bg.alpha_composite(f);r.paste(bg.convert('RGB').resize((int(w*S),int(h*S)),Image.NEAREST),(i*int(w*S),0))
        rows.append(r)
    o=Image.new('RGB',(max(r.width for r in rows),sum(r.height for r in rows)+4*len(rows)),(20,20,20));y=0
    for r in rows:o.paste(r,(0,y));y+=r.height+4
    o.save(f'{out}/vamp_todos.png');print(o.size)
