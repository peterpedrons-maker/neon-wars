import sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from mobgen import *
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),'mobs_out')+'/';os.makedirs(OUT,exist_ok=True)
SPEC={
 'javguer':dict(an='javali',pal=BOAR,legs='pants',torso='legion',hat=None,hair=None,w='guerreiro',atk='slash192',cl=(120,60,50),ct=(170,176,190)),
 'javarq':dict(an='javali',pal=BOAR,legs='leggings',torso='leather',hat='leather_cap',hair=None,w='arqueiro',atk='shoot',cl=(70,96,52),ct=(86,120,60),ch=(60,84,44)),
 'javmago':dict(an='javali',pal=BOAR,legs='pantaloons',torso='longsleeve',hat='wizard',hair=None,w='mago',atk='spellcast',cl=(90,60,150),ct=(120,80,190),ch=(96,64,160)),
 'javbruto':dict(an='javali',pal=BOAR,legs='leggings',torso='plate',hat='leather_cap',hair=None,w='clerigo',atk='slash192',cl=(60,56,64),ct=(88,84,98),ch=(110,112,124)),
 'ratass':dict(an='rato',pal=RAT,legs='pants',torso='leather',hat='bandana',hair=None,w='ladino',atk='slash',cl=(50,44,56),ct=(58,50,66),ch=(40,36,50)),
 'ratarq':dict(an='rato',pal=RAT,legs='leggings',torso='leather',hat='bandana',hair=None,w='arqueiro',atk='shoot',cl=(96,80,60),ct=(120,98,70),ch=(150,60,60)),
 'ratalq':dict(an='rato',pal=RAT,legs='pantaloons',torso='longsleeve',hat='leather_cap',hair=None,w='mago',atk='spellcast',cl=(70,100,60),ct=(96,140,72),ch=(70,104,56)),
}
def tint(l,c):
    if l is None or c is None:return l
    a=np.array(l).astype(float);lum=(a[:,:,0]*.3+a[:,:,1]*.59+a[:,:,2]*.11)/255
    k=np.clip(lum*1.15+.08,0,1)[...,None];col=np.array(c,float)[None,None,:]
    a[:,:,:3]=np.clip(k*col*1.25,0,255);return Image.fromarray(a.astype(np.uint8),'RGBA')
def wl(cls,act,side):
    p=L2+f'w_{cls}_{act}_{side}.png';return ld(p)
def act_files(s,act):
    """act: walk|hurt|atk  -> (body,legs,torso,hat,wbg,wfg,cell,off)"""
    a={'walk':'walk','hurt':'hurt','atk':s['atk']}[act]
    cell=192 if a=='slash192' else 64;off=64 if cell==192 else 0
    g=lambda grp,v:ld(L2+f'male/{a}_{grp}_{v}.png') if v else None
    body=ld(L2+f'male/{a}_skin_0.png')
    wact={'walk':'walk','hurt':'hurt','atk':'act'}[act]
    return a,cell,off,body,g('legs',s['legs']),g('torso',s['torso']),g('hat',s['hat']),wl(s['w'],wact,'bg'),wl(s['w'],wact,'fg')
def make(name,s):
    gray=s['an']=='rato'
    aw=np.array(ld(CH+s['an']+'__walk.png'))
    if gray:aw=gray_head(aw)
    awi=Image.fromarray(aw,'RGBA')
    for act in ('walk','hurt','atk'):
        a,cell,off,body,legs,torso,hat,wbg,wfg=act_files(s,act)
        if body is None:print('falta corpo',name,a);continue
        b=Image.fromarray(remap_skin(np.array(body),s['pal']),'RGBA')
        b=graft(b,awi,cell,off)
        if wbg is not None and wbg.size==b.size:
            c=wbg.copy();c.alpha_composite(b);b=c
        elif wbg is not None:print('tam wbg',name,act,wbg.size,b.size)
        legs=tint(legs,s.get('cl'));torso=tint(torso,s.get('ct'));hat=tint(hat,s.get('ch'))
        for l in (legs,torso,hat):
            if l is not None and l.size==b.size:b=over(b,l)
            elif l is not None:print('tam',name,act,l.size,b.size)
        if wfg is not None and wfg.size==b.size:b=over(b,wfg)
        elif wfg is not None:print('tam wfg',name,act,wfg.size,b.size)
        kind={'walk':'walk','hurt':'hurt','atk':'slash' if a=='slash192' else a}[act]
        b.save(OUT+f'{name}__{kind}.png')
if __name__=='__main__':
    for n,s in SPEC.items():
        if len(sys.argv)>1 and n not in sys.argv[1:]:continue
        make(n,s);print('ok',n)

    # rato de esgoto: só recolor cinza do rato original
    for k in ('walk','hurt','slash'):
        a=np.array(ld(CH+f'rato__{k}.png'));Image.fromarray(gray_head(a),'RGBA').save(OUT+f'ratobase__{k}.png')
