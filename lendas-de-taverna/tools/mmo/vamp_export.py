"""Exporta os atlas do Morcego-Vampiro (mini-chefe) e do morcego comum para o jogo.
vamp_atlas.png/json: idle, fly, bite, screech, summon, hurt, death(10), dive_up(4), dive_apex, dive_down, dive_hit, dive_end, channel + variantes e_* (forma de fúria, escurecida)
bat_atlas.png/json: fly(6), bite(6), hurt(3), death(6)"""
import sys,json,os
import numpy as np
from PIL import Image
import cut_vampbat as CV,vampbat_fix as VF
OUT='../../mmo/assets/chars/'
def crop(f):return f.crop(f.getchannel('A').getbbox())
def darken(f,k=.55,red=True):
    a=np.array(f).astype(float);m=a[:,:,3]>0;a[m,:3]*=k
    if red:   # olhos/boca ficam vermelhos vivos
        r,g,b=a[:,:,0],a[:,:,1],a[:,:,2];rm=m&(r>g*1.6)&(r>b*1.4);a[rm,0]=np.minimum(255,a[rm,0]/k*1.05)
    return Image.fromarray(np.clip(a,0,255).astype('uint8'),'RGBA')
def build(anims,F,name,pad=6,cols=10):
    tr={n:[crop(f) for f in fr] for n,fr in anims.items()}
    sc={n:[f.resize((max(1,round(f.width*F)),max(1,round(f.height*F))),Image.NEAREST) for f in fr] for n,fr in tr.items()}
    W=max(f.width for fr in sc.values() for f in fr)+2*pad;H=max(f.height for fr in sc.values() for f in fr)+2*pad
    frames=[];meta={'w':W,'h':H,'ax':W//2,'ay':H//2,'cols':cols,'anims':{}}
    for n,fr in sc.items():
        meta['anims'][n]=[len(frames)+i for i in range(len(fr))]
        for f in fr:
            c=Image.new('RGBA',(W,H),(0,0,0,0));c.alpha_composite(f,((W-f.width)//2,(H-f.height)//2));frames.append(c)
    rows=(len(frames)+cols-1)//cols;A=Image.new('RGBA',(cols*W,rows*H),(0,0,0,0))
    for i,f in enumerate(frames):A.alpha_composite(f,((i%cols)*W,(i//cols)*H))
    A.save(OUT+name+'_atlas.png',optimize=True);json.dump(meta,open(OUT+name+'_atlas.json','w'));print(name,'atlas',A.size,len(frames),'quadros; célula',W,H)
if __name__=='__main__':
    A=CV.load()
    seq=[f for f,y,t in VF.seq_death(A)]
    an={'idle':A['idle'],'fly':A['fly'],'bite':A['bite'],'screech':A['screech'],'summon':A['summon'],'hurt':A['hurt'],'death':seq,
        'dive_up':[A['dive'][1],A['summon'][1],A['dive'][1],A['hurt'][1]],'dive_apex':[A['dive'][2]],'dive_down':[A['dive'][3]],'dive_hit':[A['dive'][4]],'dive_end':[A['dive'][5]],
        'channel':A['rage'][2:]}
    full=dict(an)
    for n,fr in an.items():full['e_'+n]=[darken(f) for f in fr]
    rg=A['rage'];full['e_idle']=[rg[2],rg[3],rg[4],rg[5],rg[4],rg[3]];full['e_fly']=full['e_idle']
    build(full,.6,'vamp')
    # morcego comum (folha anterior)
    d='/tmp/claude-0/-home-user-neon-wars/3ffd125f-a99a-599e-8554-f2b481e86fc1/scratchpad/bat/f/'
    ld=lambda k,n:[Image.open(f'{d}{k}_{i}.png').convert('RGBA') for i in range(n)]
    bat={'fly':ld('move',6),'bite':ld('attack',6),'hurt':ld('hurt',3),'death':ld('death',6)}
    w=np.median([f.getchannel('A').getbbox()[2]-f.getchannel('A').getbbox()[0] for f in bat['fly']]);build(bat,46.0/w,'bat')
