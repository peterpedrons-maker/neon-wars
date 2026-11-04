"""Gera as folhas do Rei Esqueleto (boss das Catacumbas) com o sistema de camadas LPC: esqueleto, armadura de placa escurecida,
ombreiras, elmo com chifres, capa rubra e espada brilhante. Saída no formato do jogo (andar 576x256, dano 384x64, ataque 1152x768).
Uso: python3 skel_chefe.py [pasta_spritesheets_do_LPC]"""
import os,sys
from PIL import Image
import numpy as np
R=(sys.argv[1] if len(sys.argv)>1 else '/tmp/lpc_repo/spritesheets').rstrip('/')+'/'
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','mmo','assets','chars')
# (camada, tintura): 'ferro' = placa escura azulada; 'ouro' = detalhes dourados; 'rubro' = capa; None = original
LAYERS=[('cape/solid/bg','rubro'),('body/bodies/skeleton',None),('head/heads/skeleton/adult',None),('legs/armour/plate/male','ferro'),('feet/armour/plate/thin','ferro'),
 ('torso/armour/plate/male','ferro'),('shoulders/pauldrons/male','ouro'),('hat/formal/crown/adult','ouro'),('cape/solid/fg','rubro')]
TINT={'ferro':((.34,.36,.5),(.0,.0,.04)),'ouro':((.95,.72,.25),(.04,.02,0)),'rubro':((.62,.08,.12),(.02,0,0))}
def tint(im,k):
    if not k:return im
    a=np.array(im.convert('RGBA')).astype(float);m,add=TINT[k]
    l=(a[:,:,0]*.3+a[:,:,1]*.59+a[:,:,2]*.11)/255.0
    l=np.clip(l*1.25,0,1)[:,:,None]
    for i in range(3):a[:,:,i]=np.clip((l[:,:,0]*(m[i]*1.6)+add[i])*255+ (l[:,:,0]**3)*70,0,255)
    return Image.fromarray(a.astype('uint8'),'RGBA')
def ld(p,k=None):return tint(Image.open(R+p).convert('RGBA'),k)
def pick(base,act):
    names=[act]+(['run'] if act=='walk' else [])
    for n in names:
        if os.path.exists(R+f'{base}/{n}.png'):return f'{base}/{n}.png',n
    raise SystemExit('falta '+base+' '+act)
def compose(act,size):
    out=Image.new('RGBA',size,(0,0,0,0))
    for base,k in LAYERS:
        try:p,n=pick(base,act)
        except SystemExit:
            if act=='walk' or act=='hurt' or act=='slash':continue
            raise
        im=ld(p,k)
        if n=='run':  # cabeça/capacete só têm corrida (8 quadros): mapeia para os 9 do andar
            t=Image.new('RGBA',(576,256),(0,0,0,0))
            for r in range(4):
                for c in range(9):t.alpha_composite(im.crop(((c*8//9)*64,r*64,(c*8//9)*64+64,r*64+64)),(c*64,r*64))
            im=t
        out.alpha_composite(im.crop((0,0,*size)))
    return out
W='weapon/sword/glowsword/'
def main():
    os.makedirs(OUT,exist_ok=True)
    for act,sz in (('walk',(576,256)),('hurt',(384,64))):
        s=compose(act,sz);t=Image.new('RGBA',sz,(0,0,0,0))
        t.alpha_composite(ld(f'{W}universal_behind/{act}/blue.png'));t.alpha_composite(s);t.alpha_composite(ld(f'{W}{act}/blue.png'))
        t.save(os.path.join(OUT,f'skelchefe__{act}.png'),optimize=True)
    sz=(1152,768);body=Image.new('RGBA',sz,(0,0,0,0));sm=compose('slash',(384,256))
    for r in range(4):
        for c in range(6):body.alpha_composite(sm.crop((c*64,r*64,c*64+64,r*64+64)),(c*192+64,r*192+64))
    a=Image.new('RGBA',sz,(0,0,0,0));a.alpha_composite(ld(f'{W}attack_slash/behind/blue.png'));a.alpha_composite(body);a.alpha_composite(ld(f'{W}attack_slash/blue.png'))
    a.save(os.path.join(OUT,'skelchefe__slash.png'),optimize=True);print('ok')
if __name__=='__main__':main()
