"""Remove a capa do Gorgash dos quadros de idle/caminhada (a IA desenhou capa só nessa folha).
A capa fica atrás do corpo, à esquerda da linha das costas B(y); o cabo do machado (marrom) e as botas ficam."""
import numpy as np,cv2
from PIL import Image
from scipy import ndimage as nd
import cut_grid as CG
# linha das costas (x na célula 229x256 sem margem; y -> x). À esquerda disso, abaixo de y=88, é capa.
BK=[(88,60),(96,66),(120,70),(150,74),(180,80),(196,80),(200,70),(206,54),(256,50)]
def back_line(y):return np.interp(y,[p[0] for p in BK],[p[1] for p in BK])
def uncape(cell,dx=0,m=6):
    """cell: PIL RGB da célula (já sem margem m). dx: deslocamento horizontal do corpo em relação ao W1."""
    k=CG.key(cell);a=np.array(cell).astype(np.float32);h,w=k.shape[:2]
    yy,xx=np.mgrid[0:h,0:w];B=back_line(yy+m)-m+dx
    left=(xx<B)&(yy+m>88)
    rgb=a;brown=(rgb[:,:,0]>rgb[:,:,2]+22)&(rgb[:,:,0]>62)         # cabo do machado / correias
    # cabo: componente marrom contínuo dentro da zona da capa
    haft=nd.binary_dilation(brown&left,iterations=2)
    lb,n=nd.label(haft);keep=np.zeros_like(left)
    for i in range(1,n+1):
        if (lb==i).sum()>60:keep|=lb==i
    alpha=k[:,:,3]>0
    cut=left&alpha&~keep
    # suaviza a borda do corte e limpa restos
    cut=nd.binary_closing(cut,iterations=2)
    alpha2=alpha&~cut
    k=k.copy();k[:,:,3]=np.where(alpha2,255,0)
    return k
if __name__=='__main__':
    import sys
    im=Image.open('gorgash_src/iw.jpg').convert('RGB');W,H=im.size;cw,ch=W/6,H/3;m=6
    out=[]
    for r,c in [(1,c) for c in range(6)]+[(2,c) for c in range(6)]+[(0,c) for c in range(6)]:
        cell=im.crop((round(c*cw)+m,round(r*ch)+m,round((c+1)*cw)-m,round((r+1)*ch)-m))
        out.append(Image.fromarray(uncape(cell)))
    Cn=Image.new('RGB',(6*out[0].width,3*out[0].height),(70,80,70))
    for i,f in enumerate(out):
        bgc=Image.new('RGBA',f.size,(70,80,70,255));bgc.alpha_composite(f);Cn.paste(bgc.convert('RGB'),((i%6)*f.width,(i//6)*f.height))
    Cn.save(sys.argv[1]);print(Cn.size)
