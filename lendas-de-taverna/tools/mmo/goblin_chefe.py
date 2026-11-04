"""Gera as folhas do Goblin Chefe (boss da Floresta dos Goblins) com o sistema de camadas LPC: corpo + cabeça de goblin pintados de verde,
armadura de couro, ombreiras, perneiras de placa, elmo nasal e machado de guerra. Saída no formato do jogo (andar 576x256, dano 384x64, ataque 1152x768).
Uso: python3 goblin_chefe.py [pasta_spritesheets_do_LPC]   (padrão: /tmp/lpc_repo/spritesheets)"""
import os,sys
from PIL import Image
import numpy as np
R=(sys.argv[1] if len(sys.argv)>1 else '/tmp/lpc_repo/spritesheets').rstrip('/')+'/'
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','mmo','assets','chars')
SKIN={(249,213,186):(57,170,78),(228,164,124):(34,130,54),(204,134,101):(25,84,29),(153,66,60):(9,50,11),(250,236,231):(83,191,113)}
LAYERS=[('body/bodies/male',1),('head/heads/goblin/adult',1),('legs/armour/plate/male',0),('feet/armour/plate/thin',0),('torso/armour/leather/male',0),('shoulders/legion/male',0),('hat/helmet/nasal/adult',0)]
def remap(im,t):
    a=np.array(im.convert('RGBA'))
    for (r,g,b),(R_,G,B) in t.items():
        m=(a[:,:,0]==r)&(a[:,:,1]==g)&(a[:,:,2]==b)&(a[:,:,3]>0);a[m,:3]=(R_,G,B)
    return Image.fromarray(a,'RGBA')
def ld(p,t=None):
    im=Image.open(R+p).convert('RGBA');return remap(im,t) if t else im
def pick(base,act):
    for p in (f'{base}/{act}.png',f'{base}/{act}/iron.png',f'{base}/{act}/steel.png'):
        if os.path.exists(R+p):return p
    raise SystemExit('falta '+base+' '+act)
def compose(act,size):
    out=Image.new('RGBA',size,(0,0,0,0))
    for base,green in LAYERS:
        im=ld(pick(base,act),SKIN if green else None);out.alpha_composite(im.crop((0,0,*size)))
    return out
def main():
    os.makedirs(OUT,exist_ok=True)
    for act,sz,wp in (('walk',(576,256),'weapon/blunt/waraxe/walk/waraxe.png'),('hurt',(384,64),'weapon/blunt/waraxe/hurt/waraxe.png')):
        s=compose(act,sz)
        if act=='walk':
            t=Image.new('RGBA',sz,(0,0,0,0));t.alpha_composite(ld('weapon/blunt/waraxe/behind/walk/waraxe.png'));t.alpha_composite(s);s=t
        s.alpha_composite(ld(wp));s.save(os.path.join(OUT,f'gobchefe__{act}.png'),optimize=True)
    sz=(1152,768);body=Image.new('RGBA',sz,(0,0,0,0));sm=compose('slash',(384,256))
    for r in range(4):
        for c in range(6):body.alpha_composite(sm.crop((c*64,r*64,c*64+64,r*64+64)),(c*192+64,r*192+64))
    a=Image.new('RGBA',sz,(0,0,0,0));a.alpha_composite(ld('weapon/blunt/waraxe/attack_slash/behind/waraxe.png'));a.alpha_composite(body);a.alpha_composite(ld('weapon/blunt/waraxe/attack_slash/waraxe.png'))
    a.save(os.path.join(OUT,'gobchefe__slash.png'),optimize=True);print('ok')
if __name__=='__main__':main()
