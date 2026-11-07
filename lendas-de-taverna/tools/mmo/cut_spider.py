"""Corta as folhas da aranha comum (IA, fundo magenta) e gera GIFs. Uso: python3 cut_spider.py <pasta_saida>"""
import sys,os
import numpy as np
from PIL import Image,ImageDraw
import cut_grid
UP='/root/.claude/uploads/3ffd125f-a99a-599e-8554-f2b481e86fc1/'
S1=(UP+'4cda2c3d-image.jpg',6,4,[('idle',6),('run',6),('bite',6),('hurt',4)])
S2=(UP+'6fca475f-image.jpg',6,2,[('web',6),('death',6)])
def cells(path,nc,nr,rows):
    im=Image.open(path).convert('RGB');W,H=im.size;xs=[round(W*i/nc) for i in range(nc+1)];ys=[round(H*i/nr) for i in range(nr+1)];out={}
    for r,(name,n) in enumerate(rows):
        fr=[]
        for c in range(n):
            cell=im.crop((xs[c]+6,ys[r]+6,xs[c+1]-6,ys[r+1]-6));a=cut_grid.clean(cut_grid.key(cell));fr.append(Image.fromarray(a,'RGBA'))
        out[name]=fr
    return out
def trim(f):
    b=f.getchannel('A').getbbox();return f.crop(b),b
def load():
    A=cells(*S1);B=cells(*S2)
    w1=np.median([trim(f)[0].width for f in A['idle']]);w2=np.median([trim(f)[0].width for f in B['web'][4:]]);k=w1/w2
    for n,fr in B.items():A[n]=[f.resize((max(1,int(f.width*k)),max(1,int(f.height*k))),Image.NEAREST) for f in fr]
    return A,k
def stack(fr,mode='ground'):
    tr=[trim(f)[0] for f in fr];cw=max(t.width for t in tr)+14;ch=max(t.height for t in tr)+14;out=[]
    for t in tr:
        c=Image.new('RGBA',(cw,ch),(0,0,0,0));c.alpha_composite(t,((cw-t.width)//2,ch-7-t.height if mode=='ground' else (ch-t.height)//2));out.append(c)
    return out
if __name__=='__main__':
    out=sys.argv[1];os.makedirs(out,exist_ok=True);A,k=load();print('escala folha 2:',round(k,2),{n:len(v) for n,v in A.items()})
    BG=(52,74,46,255)
    def gif(name,fr,dur,sc=2.4,flip=False):
        st=stack(fr);w,h=st[0].size;sz=(int((w+30)*sc),int((h+40)*sc));ims=[]
        for f in st:
            if flip:f=f.transpose(Image.FLIP_LEFT_RIGHT)
            g=f.resize((int(w*sc),int(h*sc)),Image.NEAREST);bg=Image.new('RGBA',sz,BG);d=ImageDraw.Draw(bg);d.ellipse((sz[0]*.2,sz[1]*.82,sz[0]*.8,sz[1]*.94),fill=(36,52,34,255));bg.alpha_composite(g,((sz[0]-g.width)//2,sz[1]-int(14*sc)-g.height));ims.append(bg.convert('RGB').quantize(64,dither=Image.Dither.NONE))
        ims[0].save(f'{out}/aranha_{name}.gif',save_all=True,append_images=ims[1:],duration=dur,loop=0,disposal=2)
    gif('idle',A['idle'],[200]*6);gif('run',A['run'],[70]*6);gif('mordida',A['bite'],[110,100,100,120,110,110]);gif('dano',A['hurt'],[110,130,130,150]);gif('teia',A['web'],[120,110,110,110,120,120]);gif('morte',A['death'],[110,110,130,150,200,300])
    # percurso: corre e ataca (imagem composta)
    W,H=520,300;fr=[];run=A['run'];bite=A['bite']
    import math
    for t in range(48):
        x=60+t*7.5 if t<30 else 60+30*7.5;f=run[t%6] if t<30 else bite[min(5,(t-30)//3)]
        tr=trim(f)[0];bg=Image.new('RGBA',(W,H),BG);d=ImageDraw.Draw(bg);d.ellipse((x-40,H-70,x+50,H-50),fill=(36,52,34,255));bg.alpha_composite(tr.resize((int(tr.width*1.4),int(tr.height*1.4)),Image.NEAREST),(int(x-tr.width*.7),H-60-int(tr.height*1.4)));fr.append(bg.convert('RGB').quantize(64,dither=Image.Dither.NONE))
    fr[0].save(f'{out}/aranha_percurso.gif',save_all=True,append_images=fr[1:],duration=80,loop=0,disposal=2)
    row=[stack(A[n])[0] for n in ('idle','run','bite','hurt','web','death')]
