"""Monta as folhas do goblin completo (arte de IA) no formato do jogo: walk 9x4, slash 6x4, hurt 6x1, quadros 64x64."""
import sys,os
from PIL import Image
import numpy as np
from scipy import ndimage
H=os.path.dirname(os.path.abspath(__file__))
def keyout(im):
    a=np.array(im.convert('RGB')).astype(int);r,g,b=a[:,:,0],a[:,:,1],a[:,:,2]
    mag=(r>150)&(b>150)&(g<120)
    fg=~mag
    fg=ndimage.binary_opening(fg,iterations=1)
    lab,n=ndimage.label(fg)
    if n>1:
        sz=ndimage.sum(fg,lab,range(1,n+1));keep=[i+1 for i,s in enumerate(sz) if s>=25];fg=np.isin(lab,keep)
    # remove halo rosado nas bordas
    e=ndimage.binary_erosion(fg,iterations=1);edge=fg&~e
    halo=edge&(r>g+40)&(b>g+20)
    fg=fg&~halo
    # tira o tom magenta que vazou do fundo para dentro das bordas (contorno e arma ficam neutros/escuros)
    tint=(r-g>26)&(b-g>10)&fg
    a2=a.copy();gg=g.copy()
    a2[:,:,0]=np.where(tint,np.minimum(r,gg+10),r);a2[:,:,2]=np.where(tint,np.minimum(b,gg+10),b)
    a2[:,:,1]=np.where(tint,(gg*.8).astype(int),g)
    return Image.fromarray(np.dstack([a2.astype('uint8'),(fg*255).astype('uint8')]),'RGBA')
def cells_uniform(path,cols,rows):
    im=Image.open(path).convert('RGB');W,Hh=im.size;cw,ch=W/cols,Hh/rows;out=[]
    for r in range(rows):
        row=[]
        for c in range(cols):
            row.append(keyout(im.crop((round(c*cw),round(r*ch),round((c+1)*cw),round((r+1)*ch)))))
        out.append(row)
    return out
def cells_grid(path,xs,ys,m=4):
    im=Image.open(path).convert('RGB');out=[]
    for r in range(len(ys)-1):
        row=[]
        for c in range(len(xs)-1):
            row.append(keyout(im.crop((xs[c]+m,ys[r]+m,xs[c+1]-m,ys[r+1]-m))))
        out.append(row)
    return out
def bbox(im):
    return im.getbbox()
def to_cell(im,s,feet_y=61,lowhalf=True):
    """reduz com média premultiplicada, alinha os pés em feet_y e o centro do corpo em x=32"""
    w,h=max(1,round(im.width*s)),max(1,round(im.height*s))
    p=im.convert('RGBa').resize((w,h),Image.BOX).convert('RGBA')
    a=np.array(p);a[:,:,3]=np.where(a[:,:,3]>120,255,0);p=Image.fromarray(a,'RGBA')
    bb=p.getbbox()
    if not bb:return Image.new('RGBA',(64,64))
    alpha=np.array(p)[:,:,3]>0;ys,xs=np.where(alpha)
    y0,y1=bb[1],bb[3]
    low=ys>y0+(y1-y0)*.45
    cx=xs[low].mean() if low.any() else (bb[0]+bb[2])/2
    cell=Image.new('RGBA',(64,64),(0,0,0,0))
    ox=int(round(32-cx));oy=int(feet_y-(y1-1))
    cell.alpha_composite(p,(ox,oy)) if (0<=ox and 0<=oy and ox+w<=64 and oy+h<=64) else cell.paste(p,(ox,oy),p)
    return cell
if __name__=='__main__':
    walk=cells_uniform(os.path.join(H,'walk.jpg'),9,4)
    # escala comum: altura do goblin de frente (linha 2) -> 47 px
    hs=[bbox(walk[2][c])[3]-bbox(walk[2][c])[1] for c in range(9)]
    S=47/np.median(hs);print('escala',round(S,4),'altura IA',np.median(hs))
    sheet=Image.new('RGBA',(576,256))
    for r in range(4):
        for c in range(9):sheet.alpha_composite(to_cell(walk[r][c],S),(c*64,r*64))
    sheet.save(os.path.join(H,'goblin2__walk.png'))
    xs=[25,226,428,630,832,1034,1236];ys=[32,234,436,638,840]
    sl=cells_grid(os.path.join(H,'slash.jpg'),xs,ys)
    # a folha de ataque tem escala própria (células 202px): usa a mesma proporção personagem/célula da altura
    hs2=[bbox(sl[2][c])[3]-bbox(sl[2][c])[1] for c in (4,5)]
    S2=47/np.median(hs2);print('escala ataque',round(S2,4))
    sheet=Image.new('RGBA',(384,256))
    for r in range(4):
        for c in range(6):sheet.alpha_composite(to_cell(sl[r][c],S2),(c*64,r*64))
    sheet.save(os.path.join(H,'goblin2__slash.png'))
    hu=cells_uniform(os.path.join(H,'hurt.jpg'),9,4)[0]
    pick=[1,2,3,5,6,8]
    sheet=Image.new('RGBA',(384,64))
    for i,k in enumerate(pick):sheet.alpha_composite(to_cell(hu[k],S,feet_y=61),(i*64,0))
    sheet.save(os.path.join(H,'goblin2__hurt.png'))
    print('ok')
