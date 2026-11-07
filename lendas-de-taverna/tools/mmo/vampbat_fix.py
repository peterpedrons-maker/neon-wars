"""Mergulho e morte do Morcego-Vampiro com transições suaves, só com quadros das folhas da IA + rotação em pixel.
mergulho: sobe inclinado (quadros inclinados das folhas), vira e desce com as asas fechadas até o impacto; morte: gira no ar antes de cair."""
import sys,os
from PIL import Image,ImageDraw
import cut_vampbat as C
def crop(f):return f.crop(f.getchannel('A').getbbox())
def seq_dive(A):
    d,h,s=A['dive'],A['hurt'],A['summon']
    # (quadro, deslocamento vertical em px, tempo ms)
    return [(d[0],0,90),(d[1],-14,80),(s[1],-34,80),(d[1],-58,80),(h[1],-80,90),(d[2],-82,110),(d[3],-60,70),(d[3],-26,55),(d[4],6,150),(d[5],0,110),(d[0],0,110)]
def seq_death(A):
    d=A['death'];rot=lambda f,a:crop(f).rotate(-a,resample=Image.NEAREST,expand=True)
    out=[(d[0],0,100),(d[1],4,90)]
    for a,y in((35,10,),(75,22),(115,36),(150,50)):out.append((rot(d[1],a),y,70))
    out+= [(d[2],56,90),(d[3],70,100),(d[4],82,130),(d[5],90,500)]
    return out
def render(seq,path,BG=(34,30,44,255),sc=1.7,pad=16,tw=None):
    tr=[(crop(f) if f.getchannel('A').getbbox() else f,y,t) for f,y,t in seq]
    W=max(t.width for t,_,_ in tr)+2*pad;ys=[y for _,y,_ in tr];top=min(ys);bot=max(ys);H=max(t.height for t,_,_ in tr)+(bot-top)+2*pad
    ims=[]
    for t,y,ms in tr:
        c=Image.new('RGBA',(W,H),BG);c.alpha_composite(t,((W-t.width)//2,pad+(y-top)+(max(x.height for x,_,_ in tr)-t.height)//2));
        c=c.resize((int(W*sc),int(H*sc)),Image.NEAREST);ims.append(c.convert('RGB').quantize(64,dither=Image.Dither.NONE))
    ims[0].save(path,save_all=True,append_images=ims[1:],duration=[ms for _,_,ms in tr],loop=0,disposal=2);return ims
if __name__=='__main__':
    out=sys.argv[1];os.makedirs(out,exist_ok=True);A=C.load()
    render(seq_dive(A),f'{out}/vamp3_mergulho.gif');render(seq_death(A),f'{out}/vamp3_morte.gif');print('ok')
