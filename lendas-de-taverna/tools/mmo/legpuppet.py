"""Caminhada por recorte de pernas: mantém o corpo de cima do quadro original (arte de IA) e anima só as pernas, cortadas da própria imagem.
Uso: python3 legpuppet.py <imagem> <x0,y0,x1,y1 da célula> <y_do_corte> <pasta_saida> [escala]"""
import sys,os,math
import numpy as np
import cv2
from PIL import Image
from scipy import ndimage as ND
import cut_grid as CG
def load(path,box):
    im=Image.open(path).convert('RGB').crop(box);a=np.array(im);a[:44,:60]=(255,0,255)   # número da célula
    k=CG.key(Image.fromarray(a));lb,n=ND.label(k[:,:,3]>0)
    if n:
        sz=ND.sum(k[:,:,3]>0,lb,range(1,n+1));k[~np.isin(lb,[i+1 for i,v in enumerate(sz) if v>sz.max()*.03]),3]=0
    f=Image.fromarray(k,'RGBA');return f
def split(f,cut,overlap=20,tail_pink=True):
    a=np.array(f);al=a[:,:,3]>0;h,w=al.shape;r,g,b=[a[:,:,i].astype(int) for i in range(3)]
    tail=al&(r>g+22)&(r>150)&(b>g-5)            # cauda rosada: fica no corpo
    below=np.zeros_like(al);below[cut:]=True
    club=al&(r>g+30)&(r<175)&(g>b+6)&~tail      # cano enferrujado: fica no corpo, as pernas ganham pele no lugar
    club=ND.binary_dilation(club,iterations=1)&al&~tail
    legs=al&below&~tail&~club
    filled=ND.binary_closing(legs,structure=np.ones((3,3)),iterations=7)&below&al&club   # buracos do cano dentro da silhueta das pernas
    fillmask=(filled&~legs)
    rgb=cv2.inpaint(np.ascontiguousarray(a[:,:,:3]),(club&below).astype(np.uint8)*255,5,cv2.INPAINT_TELEA)
    a_fill=a.copy();a_fill[:,:,:3]=rgb
    legs=legs|fillmask
    # separa as duas pernas pelo vale de colunas entre elas (abaixo de cut+25)
    colp=legs[cut+25:].sum(0).astype(float);colp=ND.gaussian_filter1d(colp,3)
    xs=np.nonzero(legs[cut+25:].any(0))[0];x0,x1=xs.min(),xs.max()
    mid0,mid1=int(x0+(x1-x0)*.3),int(x0+(x1-x0)*.7);sx=mid0+int(np.argmin(colp[mid0:mid1]))
    body=a.copy();body[:,:,3]=np.where(al&~((legs&~fillmask)&(np.arange(h)[:,None]>=cut)),255,0)   # corpo + cauda + cano, sem pernas
    # as pernas ganham 'overlap' px acima do corte (ficam atrás do corpo)
    lg=al&(np.arange(h)[:,None]>=cut-overlap)&~tail
    lg=(al&(np.arange(h)[:,None]>=cut-overlap)&~tail&~club)|fillmask
    L=a_fill.copy();L[:,:,3]=np.where(lg&(np.arange(w)[None,:]<sx),255,0)
    R=a_fill.copy();R[:,:,3]=np.where(lg&(np.arange(w)[None,:]>=sx),255,0)
    return Image.fromarray(body,'RGBA'),Image.fromarray(L,'RGBA'),Image.fromarray(R,'RGBA'),sx
def piece(img):
    b=img.getchannel('A').getbbox();return img.crop(b),b
def dark(f,v=.78):
    a=np.array(f).astype(np.float32);a[:,:,:3]*=v;return Image.fromarray(a.astype(np.uint8),'RGBA')
def compose(f,body,L,R,cut,t,amp=17,lift=9,bob=3,overlap=20,sway=1.2):
    W,H=f.size;C=Image.new('RGBA',(W,H+40),(0,0,0,0))
    ph=2*math.pi*t;aL=amp*math.sin(ph);aR=-aL
    def put(piece_img,ang,dy,col):
        p,b=piece(piece_img)
        if col<1:p=dark(p,col)
        px=(b[0]+b[2])/2-b[0];py=(cut-overlap+14)-b[1]     # pivô: quadril, 14 px abaixo do topo da perna
        py=max(4,py);R_=int(math.hypot(p.width,p.height))+4
        pad=Image.new('RGBA',(2*R_,2*R_),(0,0,0,0));pad.alpha_composite(p,(int(R_-px),int(R_-py)))
        pad=pad.rotate(ang,resample=Image.BICUBIC,center=(R_,R_))
        C.alpha_composite(pad,(int(b[0]+px-R_),int(b[1]+py-R_+20+dy)))
    # elevação do pé quando a perna avança (ângulo crescente)
    dL=-lift*max(0,math.cos(ph));dR=-lift*max(0,-math.cos(ph))
    put(L,aL,dL,.78);put(R,aR,dR,1.0)
    bd=-abs(math.sin(ph))*bob
    C.alpha_composite(body.rotate(sway*math.sin(ph),resample=Image.BICUBIC,center=(W/2,cut)),(0,int(20+bd)))
    return C
if __name__=='__main__':
    path=sys.argv[1];box=tuple(int(v) for v in sys.argv[2].split(','));cut=int(sys.argv[3]);out=sys.argv[4]
    os.makedirs(out,exist_ok=True)
    f=load(path,box);b=f.getchannel('A').getbbox();f=f.crop(b);cut=cut-b[1]
    body,L,R,sx=split(f,cut);print('corte',cut,'divisão x',sx,f.size)
    frames=[compose(f,body,L,R,cut,i/24) for i in range(24)]
    for i,fr in enumerate(frames):fr.save('%s/w%02d.png'%(out,i))
    Image.fromarray(np.array(body)).save(out+'/body.png');L.save(out+'/legL.png');R.save(out+'/legR.png')
