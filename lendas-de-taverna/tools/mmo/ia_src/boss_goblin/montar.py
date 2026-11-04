"""Monta as folhas do boss dos goblins a partir da folha gerada por IA (grade 9x9, fundo magenta): recorta cada célula, remove o magenta,
alinha os pés e o centro, normaliza a escala e grava folhas no mesmo arranjo do jogo (andar 9x4, ataque 6x4, dano 6x1) + GIFs."""
import os,sys,json
import numpy as np,cv2
from PIL import Image
from scipy import ndimage
HERE=os.path.dirname(os.path.abspath(__file__))
SRC=os.path.join(HERE,'folha_ia.jpg');OUT=os.path.join(HERE,'out');CELL=128
def key(rgb):
    r,g,b=[rgb[:,:,i].astype(int) for i in range(3)]
    bg=(r>140)&(b>140)&(g<0.62*np.minimum(r,b))&(np.abs(r-b)<90)
    fg=~bg;fg=ndimage.binary_opening(fg,iterations=1);lab,n=ndimage.label(ndimage.binary_dilation(fg,iterations=3))
    if n==0:return fg
    sizes=ndimage.sum(fg,lab,range(1,n+1));keep=np.isin(lab,[i+1 for i,s in enumerate(sizes) if s>=max(60,sizes.max()*.02)])
    fg=fg&keep;return ndimage.binary_fill_holes(fg)
def defringe(rgb,a):
    a=ndimage.binary_erosion(a,iterations=1,border_value=0);edge=a&~ndimage.binary_erosion(a,iterations=2,border_value=1)
    r,g,b=[rgb[:,:,i].astype(int) for i in range(3)];pur=edge&((np.minimum(r,b)-g)>18)&(r>g+8)&(b>g+8);rgb=rgb.copy();rgb[pur]=(30,26,34);return rgb,a
def cells(img):
    H,W=img.shape[:2];n=9;out={}
    for r in range(n):
        for c in range(n):
            y0,y1=int(r*H/n),int((r+1)*H/n);x0,x1=int(c*W/n),int((c+1)*W/n);out[(r,c)]=img[y0:y1,x0:x1]
    return out
def extract(cell):
    a=key(cell);
    if a.sum()<50:return None
    rgb,a=defringe(cell,a);ys,xs=np.where(a)
    core=ndimage.binary_opening(a,structure=np.ones((9,9)));cy,cx=np.where(core) if core.any() else (ys,xs)
    return dict(rgb=rgb,a=a,bottom=ys.max(),cx=(cx.min()+cx.max())/2,ch=cy.max()-cy.min()+1 if len(cy) else ys.max()-ys.min()+1)
def place(f,scale):
    """escala o recorte e devolve uma célula CELL x CELL com os pés em y=CELL-8 e o centro do corpo em x=CELL/2"""
    h,w=f['a'].shape;rgba=np.dstack([f['rgb'],f['a']*255]).astype(np.uint8)
    im=Image.fromarray(rgba,'RGBA');nw,nh=max(1,round(w*scale)),max(1,round(h*scale));im=im.resize((nw,nh),Image.LANCZOS)
    cell=Image.new('RGBA',(CELL,CELL),(0,0,0,0));ox=int(CELL/2-f['cx']*scale);oy=int(CELL-8-f['bottom']*scale)
    cell.alpha_composite(im,(ox,oy)) if 0<=ox and 0<=oy and ox+nw<=CELL and oy+nh<=CELL else cell.paste(im,(ox,oy),im)
    a=np.array(cell);a[:,:,3]=np.where(a[:,:,3]>110,255,0);return Image.fromarray(a,'RGBA')
def main():
    img=cv2.cvtColor(cv2.imread(SRC),cv2.COLOR_BGR2RGB);C=cells(img);F={k:extract(v) for k,v in C.items()}
    hs=[f['ch'] for f in F.values() if f];target=float(np.median(hs));print('altura mediana do corpo',target,'quadros',len(hs))
    def sheet(rows,ncols,name,names):
        S=Image.new('RGBA',(CELL*ncols,CELL*len(rows)),(0,0,0,0));frames={}
        for ri,r in enumerate(rows):
            for c in range(ncols):
                f=F.get((r,c))
                if not f:continue
                s=float(np.clip(target/f['ch'],.85,1.18));cell=place(f,s);S.alpha_composite(cell,(c*CELL,ri*CELL));frames[(ri,c)]=cell
        S.save(os.path.join(OUT,name));return frames
    os.makedirs(OUT,exist_ok=True)
    walk=sheet([0,1,2,3],9,'goblinboss__walk.png',None);atk=sheet([4,5,6,7],6,'goblinboss__slash.png',None);hurt=sheet([8],6,'goblinboss__hurt.png',None)
    bg=(58,92,48,255);K=3
    def gif(frames,rows,n,name,ms):
        G=[]
        for c in range(n):
            im=Image.new('RGBA',(CELL*K*len(rows),CELL*K),bg)
            for ri,_ in enumerate(rows):
                f=frames.get((ri,c))
                if f:im.alpha_composite(f.resize((CELL*K,CELL*K),Image.NEAREST),(ri*CELL*K,0))
            G.append(im.convert('P',palette=Image.ADAPTIVE))
        G[0].save(os.path.join(OUT,name),save_all=True,append_images=G[1:],duration=ms,loop=0,disposal=2)
    gif(walk,[0,1,2,3],9,'andar.gif',110);gif(atk,[0,1,2,3],6,'ataque.gif',130);gif(hurt,[0],6,'dano.gif',160)
    json.dump({'cell':CELL,'walk':{'frames':9,'rows':['costas(arte mostra frente)','esquerda','frente','direita']},'slash':{'frames':6},'hurt':{'frames':6,'nota':'os 2 últimos quadros são a morte'}},open(os.path.join(OUT,'goblinboss.json'),'w'),indent=1,ensure_ascii=False)
if __name__=='__main__':main()
