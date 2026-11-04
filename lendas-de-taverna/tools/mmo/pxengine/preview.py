"""Preview System: reproduz as animações (janela do Pygame se houver tela; senão GIF e folha de contato)."""
import os
import numpy as np
from PIL import Image
def gifs(char,A,out,scale=6,bg=(58,92,48)):
    os.makedirs(out,exist_ok=True);F=[]
    for i in range(A['n']):
        c=Image.new('RGBA',(char.W*scale*3,char.H*scale),(*bg,255))
        for j,v in enumerate(('front','side','back')):
            im=Image.fromarray(A['views'][v][i].rgba,'RGBA').resize((char.W*scale,char.H*scale),Image.NEAREST);c.alpha_composite(im,(j*char.W*scale,0))
        F.append(c.convert('P',palette=Image.ADAPTIVE))
    p=os.path.join(out,f"{char.spec['name']}_{A['name']}.gif");F[0].save(p,save_all=True,append_images=F[1:],duration=A['ms'],loop=0,disposal=2);return p
def window(char,A,view='front',scale=8):
    """janela interativa (Pygame): setas trocam a vista, ESC sai"""
    import pygame;pygame.init();s=pygame.display.set_mode((char.W*scale,char.H*scale));clk=pygame.time.Clock();i=0;views=['front','side','back'];vi=views.index(view);t=0
    while True:
        for e in pygame.event.get():
            if e.type==pygame.QUIT or (e.type==pygame.KEYDOWN and e.key==pygame.K_ESCAPE):return
            if e.type==pygame.KEYDOWN and e.key in(pygame.K_LEFT,pygame.K_RIGHT):vi=(vi+1)%3
        f=A['views'][views[vi]][i].rgba;surf=pygame.image.frombuffer(f.tobytes(),(char.W,char.H),'RGBA')
        s.fill((58,92,48));s.blit(pygame.transform.scale(surf,(char.W*scale,char.H*scale)),(0,0));pygame.display.flip()
        clk.tick(1000/A['ms'][i]);i=(i+1)%A['n']
def contact(char,A,out):
    W,H=char.W,char.H;n=A['n'];S=np.zeros((H*3,W*n,4),np.uint8);S[:]=(58,92,48,255)
    for r,v in enumerate(('front','side','back')):
        for i,f in enumerate(A['views'][v]):
            a=f.rgba;m=a[:,:,3]>0;reg=S[r*H:(r+1)*H,i*W:(i+1)*W];reg[m]=a[m]
    p=os.path.join(out,f"{char.spec['name']}_{A['name']}_contato.png");Image.fromarray(S,'RGBA').save(p);return p
