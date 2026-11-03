"""Recolore os monstros LPC (paleta exata): goblins 100% verdes (tanga/roupa por classe) e javali todo na cor da cabeça, com rabo de porco.
Lê chars_src/ (originais) e escreve ../../mmo/assets/chars/. Uso: /usr/bin/python3 recolor_mobs.py"""
import os
from PIL import Image
import numpy as np
from scipy import ndimage
H=os.path.dirname(os.path.abspath(__file__));SRC=os.path.join(H,'chars_src');OUT=os.path.join(H,'..','..','mmo','assets','chars')
def rgb(*a):return tuple(a)
SKIN_GREEN={(249,213,186):(57,170,78),(228,164,124):(34,130,54),(204,134,101):(25,84,29),(153,66,60):(9,50,11),(250,236,231):(83,191,113)}
CLOTH=['E5E6C7','C4B59F','B19998','958080','726B7E','4D4A5D']
def ramp(*hexs):return {tuple(int(CLOTH[i][j:j+2],16) for j in (0,2,4)):tuple(int(hexs[i][j:j+2],16) for j in (0,2,4)) for i in range(6)}
CLOTH_BROWN=ramp('B0804E','96683E','80583A','6C4A2E','54382A','3A281C')
CLOTH_OLIVE=ramp('A0AA64','828C50','6C7642','5A6236','464E2C','343A22')
CLOTH_PURPLE=ramp('9672C8','7E58AE','6A4692','583878','46295E','341C46')
SKIN_BOAR={(249,213,186):(112,78,62),(228,164,124):(98,65,53),(204,134,101):(71,55,48),(153,66,60):(48,34,32),(250,236,231):(142,102,82)}
MAIL_BOAR={(134,126,127):(112,82,66),(114,107,126):(90,64,52),(77,74,93):(60,44,38),(196,181,159):(122,90,70),(255,255,255):(150,110,86),(221,221,221):(136,100,78),(229,230,199):(140,104,82),(177,153,152):(104,76,62),(149,128,128):(96,70,58)}
def remap(a,table,ymask=None):
    out=a.copy()
    for (r,g,b),(R,G,B) in table.items():
        m=(a[:,:,0]==r)&(a[:,:,1]==g)&(a[:,:,2]==b)&(a[:,:,3]>0)
        if ymask is not None:m&=ymask
        out[:,:,0][m]=R;out[:,:,1][m]=G;out[:,:,2][m]=B
    return out
def frames(a,cols,rows,cell=64):
    for r in range(rows):
        for c in range(cols):yield r,c,(r*cell,(r+1)*cell,c*cell,(c+1)*cell)
TAIL_SIDE=[(0,0),(1,0),(2,-1),(2,-2),(1,-3),(0,-3)]       # curva para fora (lado direito), espelhada no outro
TAIL_BACK=[(0,0),(1,-1),(2,-2),(1,-3),(0,-3),(-1,-2)]
def draw_tail(fr,row):
    al=fr[:,:,3]>0
    if not al.any():return
    ys,xs=np.where(al);top=ys.min();hy=top+30
    if hy>=64:return
    line=np.where(al[hy])[0]
    if len(line)==0:return
    if row==0:ax=int(round((line.min()+line.max())/2));pts=[(ax+dx,hy+dy) for dx,dy in TAIL_BACK]
    elif row==1:ax=line.max()+1;pts=[(ax+dx,hy+dy) for dx,dy in TAIL_SIDE]
    elif row==3:ax=line.min()-1;pts=[(ax-dx,hy+dy) for dx,dy in TAIL_SIDE]
    else:return
    S=set(pts)
    for (x,y) in list(S):
        for ox in (-1,0,1):
            for oy in (-1,0,1):
                px,py=x+ox,y+oy
                if (px,py) not in S and 0<=px<64 and 0<=py<64 and (not al[py,px] or row==0):fr[py,px]=(37,27,25,255)
    for i,(x,y) in enumerate(pts):
        if 0<=x<64 and 0<=y<64 and (not al[y,x] or row==0):fr[y,x]=(236,170,158,255) if i%2==0 else (206,138,128,255)
WHITE_TO={'goblin':(176,128,78),'gobarq':(160,170,100),'xama':(150,114,200)}
HEAD_G=[(57,170,78),(34,130,54),(25,84,29),(9,50,11),(83,191,113)]
def drop_floating(a,cols,rows):
    """remove pedaços soltos (ex.: arco que ficou fora do corpo nos quadros de andar do arqueiro)"""
    for r,c,(y0,y1,x0,x1) in frames(a,cols,rows):
        fr=a[y0:y1,x0:x1];al=fr[:,:,3]>0
        if not al.any():continue
        lab,n=ndimage.label(ndimage.binary_dilation(al,iterations=2))
        if n>=2:
            sz=ndimage.sum(al,lab,range(1,n+1));keep=1+int(np.argmax(sz))
            fr[(lab!=keep)&al]=(0,0,0,0)
        # sobra do arco acima/ao lado da cabeça (quadros de andar de lado): usa só as cores exatas da cabeça como referência
        al=fr[:,:,3]>0;hm=np.zeros(al.shape,bool)
        for col in HEAD_G:hm|=(fr[:,:,0]==col[0])&(fr[:,:,1]==col[1])&(fr[:,:,2]==col[2])&al
        rows_=np.where(hm.sum(axis=1)>=5)[0]
        if len(rows_)==0:continue
        ht=rows_[0];top=np.where(al.any(axis=1))[0].min()
        if ht-top>4:
            hl=np.where(hm[ht:ht+8].any(axis=0))[0].min()
            kill=al&~hm;rm=np.zeros(64,bool);rm[:ht]=True;kill_a=kill&rm[:,None]
            rm2=np.zeros(64,bool);rm2[:ht+8]=True;cm=np.zeros(64,bool);cm[:max(0,hl-1)]=True;kill_b=kill&rm2[:,None]&cm[None,:]
            fr[kill_a|kill_b]=(0,0,0,0)
def process(name,cloth=None,boar=False):
    for kind in ('walk','slash','hurt','shoot'):
        f=os.path.join(SRC,'%s__%s.png'%(name,kind))
        if not os.path.exists(f):continue
        a=np.array(Image.open(f).convert('RGBA'))
        cols=a.shape[1]//64;rows=a.shape[0]//64
        if boar:
            a=remap(a,SKIN_BOAR)
            # cota de malha -> couro (só abaixo da cabeça nas folhas com corpo em pé; em 'hurt' tudo, exceto o branco das presas)
            out=a.copy()
            for r,c,(y0,y1,x0,x1) in frames(a,cols,rows):
                fr=out[y0:y1,x0:x1];al=fr[:,:,3]>0
                if not al.any():continue
                top=np.where(al.any(axis=1))[0].min()
                ym=np.zeros((64,64),bool);ym[top+16:,:]=True
                if kind=='hurt':ym[:,:]=True
                tbl=dict(MAIL_BOAR)
                if kind=='hurt':tbl.pop((255,255,255),None);tbl.pop((221,221,221),None)
                out[y0:y1,x0:x1]=remap(fr,tbl,ym)
                if kind in('walk','slash'):draw_tail(out[y0:y1,x0:x1],r)
            a=out
        else:
            a=remap(a,SKIN_GREEN)
            if cloth:a=remap(a,cloth)
            if kind!='hurt':
                for r,c,(y0,y1,x0,x1) in frames(a,cols,rows):
                    fr=a[y0:y1,x0:x1];al=fr[:,:,3]>0
                    if not al.any():continue
                    top=np.where(al.any(axis=1))[0].min();ym=np.zeros((64,64),bool);ym[top+17:,:]=True
                    a[y0:y1,x0:x1]=remap(fr,{(255,255,255):WHITE_TO[name],(250,236,231):WHITE_TO[name]},ym)
        if name=='gobarq' and kind in('walk','hurt'):drop_floating(a,cols,rows)
        Image.fromarray(a,'RGBA').save(os.path.join(OUT,'%s__%s.png'%(name,kind)))
process('goblin',CLOTH_BROWN);process('gobarq',CLOTH_OLIVE);process('xama',CLOTH_PURPLE);process('javali',boar=True)
print('ok')
