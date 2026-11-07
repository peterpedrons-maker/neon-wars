import sys,os
from goblin2 import *
import poses
from PIL import Image,ImageDraw
OUTD=sys.argv[1];os.makedirs(OUTD,exist_ok=True)
BG=(142,166,76,255);SH=(112,128,64,255)
def comp(g,sc=8):
    sp=g.render(sc);bg=Image.new('RGBA',sp.size,BG);d=ImageDraw.Draw(bg);w,h=sp.size;d.ellipse((w*.2,h*.74,w*.72,h*.86),fill=SH);bg.alpha_composite(sp);return bg
W_=sys.argv[2].split(',') if len(sys.argv)>2 else ['sword']
for wt in W_:
    for name,fn in(('idle',poses.idle),('walk',poses.walk),('attack',poses.attack)):
        P,dur=fn(wt);gs=[goblin(p) for p in P]
        ims=[comp(g).convert('RGB').quantize(48,dither=Image.Dither.NONE) for g in gs]
        ims[0].save(f'{OUTD}/{wt}_{name}.gif',save_all=True,append_images=ims[1:],duration=dur,loop=0,disposal=2)
        row=Image.new('RGB',(W*4*len(gs),H*4),BG)
        for i,g in enumerate(gs):row.paste(comp(g,4).convert('RGB'),(i*W*4,0))
        row.save(f'{OUTD}/{wt}_{name}_row.png')
print('ok')
