"""Corta as folhas de IA do Xamã Skrix (skrix_src/s1..s9.jpg, grade 4x3, fundo magenta) em quadros limpos.
Uso: python3 skrix_cut.py <pasta_saida>  -> <pasta>/s{N}_{idx}.png (idx 0..11, linha a linha)"""
import sys,os
from PIL import Image
import cut_grid as CG
SRC=os.path.join(os.path.dirname(os.path.abspath(__file__)),'skrix_src')
def cells(n,nc=4,nr=3,m=7):
    im=Image.open(f'{SRC}/s{n}.jpg').convert('RGB');W,H=im.size;out=[]
    for r in range(nr):
        for c in range(nc):
            x0,x1=round(W*c/nc),round(W*(c+1)/nc);y0,y1=round(H*r/nr),round(H*(r+1)/nr)
            cell=im.crop((x0+m,y0+m,x1-m,y1-m));a=CG.clean(CG.key(cell))
            out.append(Image.fromarray(a,'RGBA'))
    return out
if __name__=='__main__':
    o=sys.argv[1];os.makedirs(o,exist_ok=True)
    for n in range(1,10):
        if n==8:continue
        for i,f in enumerate(cells(n)):f.save(f'{o}/s{n}_{i:02d}.png')
