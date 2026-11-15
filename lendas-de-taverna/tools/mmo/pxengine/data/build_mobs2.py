import sys,math,json,numpy as np
from PIL import Image
from hq import Canvas,finish,S
CW,CH=104,96
P=lambda *a:[v*S for v in a]
def cap(d,x0,y0,x1,y1,w,fill=255):
    d.line(P(x0,y0,x1,y1),fill=fill,width=int(w*S))
    for x,y in((x0,y0),(x1,y1)):d.ellipse(P(x-w/2,y-w/2,x+w/2,y+w/2),fill=fill)
def ell(d,cx,cy,rx,ry):d.ellipse(P(cx-rx,cy-ry,cx+rx,cy+ry),fill=255)
def poly(d,pts):d.polygon([(x*S,y*S) for x,y in pts],fill=255)
BONE='#5a4a3a #8a7658 #c4b088 #efe2b8 #fff8dc'
STEEL='#1c2038 #34426a #5a74a8 #94b4e0 #dcf0ff'
WOOD='#3a1c14 #6a3420 #a05a30 #d48a46 #f0b868'
CLOTH='#3a2418 #5e3a24 #8c5c34 #bb8a4c'
ROBE='#1c0c40 #3a1878 #6430b8 #9a60f0 #d2a4ff'
VOID='#04020a #0a0614 #140c24 #22163a'
GOLD='#6a3c08 #b87a14 #f0b830 #fff070'
def guard(pose):
    c=Canvas(CW,CH);at=pose=='attack'
    L=4 if at else 0   # inclina para frente
    # pernas
    for sx,fx in((38,34),(54,58)):
        c.shape(lambda d,sx=sx,fx=fx:cap(d,sx+L*.3,62,fx,84,6.5),BONE)
        c.shape(lambda d,sx=sx,fx=fx:(poly(d,[(fx-6,78),(fx+6,78),(fx+5,86),(fx-5,86)])),STEEL,blur=1.3)
        c.shape(lambda d,fx=fx:(ell(d,fx+1,88,8,3.6)),STEEL,blur=1.3)
    # panos
    c.shape(lambda d:poly(d,[(33+L*.3,57),(57+L*.3,57),(61,74),(52,70),(46,77),(40,70),(31,74)]),CLOTH,blur=1.6)
    # braco de tras + escudo
    c.shape(lambda d:cap(d,36+L*.3,41,28,52,6),BONE)
    c.shape(lambda d:ell(d,24,55,13,16),WOOD,blur=3)
    c.shape(lambda d:ell(d,24,55,13,16),'#0a0614',flat='#14080c')
    c.shape(lambda d:ell(d,24,55,12,15),WOOD,blur=4)
    c.shape(lambda d:ell(d,24,55,4.6,5),STEEL,blur=1.8)
    for ang in range(0,360,60):
        x=24+9.5*math.cos(math.radians(ang));y=55+12*math.sin(math.radians(ang));c.shape(lambda d,x=x,y=y:ell(d,x,y,1.1,1.1),STEEL,flat='#aac4ee')
    c.shape(lambda d:(cap(d,24,41,24,70,.9)),WOOD,flat='#2a120c');c.shape(lambda d:cap(d,12,55,36,55,.9),WOOD,flat='#2a120c')
    # torso: caixa toracica + peitoral
    c.shape(lambda d:ell(d,45+L*.4,48,13.5,14.5),STEEL,blur=3.2)
    c.shape(lambda d:poly(d,[(36+L*.4,54),(54+L*.4,54),(52+L*.4,60),(38+L*.4,60)]),CLOTH,blur=1.2)
    c.shape(lambda d:cap(d,34+L*.4,52,56+L*.4,52,1),STEEL,flat='#1c2038')
    c.shape(lambda d:cap(d,45+L*.4,40,45+L*.4,52,1),STEEL,flat='#1c2038')
    c.shape(lambda d:ell(d,45+L*.4,57.5,2.6,2),GOLD,blur=.8)
    # ombros
    c.shape(lambda d:ell(d,33+L*.4,38,7.4,6),STEEL,blur=2.4)
    c.shape(lambda d:ell(d,57+L*.5,38,7.4,6),STEEL,blur=2.4)
    for x,y in((30,36),(35,35),(55,36),(60,35)):c.shape(lambda d,x=x,y=y:ell(d,x+L*.4,y,1,1),STEEL,flat='#e6f4ff')
    # pescoço + cabeça
    c.shape(lambda d:cap(d,45+L*.5,33,45+L*.5,28,5),BONE)
    c.shape(lambda d:ell(d,46+L*.6,22,9.5,10),BONE,blur=3)
    c.shape(lambda d:poly(d,[(41+L*.6,28),(52+L*.6,28),(51+L*.6,33),(42+L*.6,33)]),BONE,blur=1)
    for x in range(43,52,2):c.shape(lambda d,x=x:cap(d,x+L*.6,29,x+L*.6,32.5,.8),BONE,flat='#2a1a14')
    c.shape(lambda d:(ell(d,43+L*.6,22.5,2.8,3.2),ell(d,51+L*.6,22.5,2.8,3.2)),BONE,flat='#0c060a')
    c.shape(lambda d:(ell(d,43.4+L*.6,22.8,1.2,1.4),ell(d,51.4+L*.6,22.8,1.2,1.4)),BONE,flat='#ff8a24')
    c.shape(lambda d:poly(d,[(45.5+L*.6,26),(47.5+L*.6,26),(47+L*.6,29),(46+L*.6,29)]),BONE,flat='#0c060a')
    # elmo
    c.shape(lambda d:(ell(d,46+L*.6,16,10.6,7.5),poly(d,[(36+L*.6,16),(56+L*.6,16),(55+L*.6,19),(37+L*.6,19)])),STEEL,blur=2.8)
    c.shape(lambda d:poly(d,[(44.5+L*.6,17),(47.5+L*.6,17),(47+L*.6,25),(45+L*.6,25)]),STEEL,blur=.8)
    c.shape(lambda d:poly(d,[(44+L*.6,6),(48+L*.6,6),(49+L*.6,10),(43+L*.6,10)]),'#7a1820 #b02830 #e04a40 #ff8a70',blur=1)
    # braço da frente + espada
    if at:
        c.shape(lambda d:cap(d,53+L*.5,41,69,47,6),BONE)
        c.shape(lambda d:poly(d,[(70,45),(98,41),(101,43),(98,45),(70,49)]),STEEL,blur=.7)
        c.shape(lambda d:cap(d,68,42,68,53,2),GOLD,blur=.8);c.shape(lambda d:ell(d,68,55,3,2.6),GOLD,blur=.8)
    else:
        c.shape(lambda d:cap(d,54+L*.5,42,62,56,6),BONE)
        c.shape(lambda d:poly(d,[(60,55),(63,56),(78,26),(75,23)]),STEEL,blur=.7)
        c.shape(lambda d:cap(d,57,54,66,58,2),GOLD,blur=.8);c.shape(lambda d:ell(d,59,58.5,2.4,2.2),GOLD,blur=.8)
    c.shape(lambda d:ell(d,64+(5 if at else 0),57 if not at else 49,3.2,3),BONE,blur=1.3)
    return c
def cult(pose):
    c=Canvas(CW,CH);at=pose=='attack';L=5 if at else 0
    # pes
    for fx in(32,58):c.shape(lambda d,fx=fx:ell(d,fx,88,6.4,3),CLOTH,blur=1.3)
    # manto (cai ate o chao)
    c.shape(lambda d:poly(d,[(36+L*.3,40),(58+L*.3,40),(68,84),(60,87),(48,84),(36,88),(26,84)]),ROBE,blur=4)
    c.shape(lambda d:poly(d,[(38,56),(56,56),(60,84),(48,80),(34,84)]),ROBE,blur=3,light=(-.2,-.8))
    for x in(33,41,50,59):c.shape(lambda d,x=x:cap(d,x+(x-46)*.05,62,x+(x-46)*.25,85,.9),ROBE,flat='#1a0a38')
    c.shape(lambda d:poly(d,[(29,78),(66,78),(67,81),(28,81)]),GOLD,blur=.9)
    for x in range(32,66,5):c.shape(lambda d,x=x:ell(d,x,79.5,1.1,1.1),GOLD,flat='#fff0a0')
    c.shape(lambda d:poly(d,[(37,57),(57,57),(56,61),(38,61)]),GOLD,blur=.9)
    c.shape(lambda d:ell(d,47,59,2.6,2.4),'#7a1020 #c02840 #ff5a6a #ffd0d0',blur=.9)
    # ombros e peito
    c.shape(lambda d:ell(d,47+L*.4,45,14,13),ROBE,blur=3.4)
    # braco de tras
    c.shape(lambda d:cap(d,37+L*.4,44,28,58,6.5),ROBE)
    c.shape(lambda d:ell(d,27,60,3,3),'#6a4a30 #a07850 #d0a878 #f0d0a0',blur=1)
    c.shape(lambda d:(cap(d,26,62,15,78,2.4)),STEEL,blur=.7)
    c.shape(lambda d:ell(d,14,80,3,2.8),GOLD,blur=.8)
    # capuz
    c.shape(lambda d:(ell(d,47+L*.5,25,13,14),poly(d,[(36+L*.5,18),(47+L*.5,3),(58+L*.5,18)])),ROBE,blur=3.6)
    c.shape(lambda d:ell(d,50+L*.5,27,8,9.5),VOID,blur=3,light=(0,0))
    for x in(47,53):
        c.shape(lambda d,x=x:ell(d,x+L*.6,26.5,2,1.6),VOID,flat='#ff3a4a');c.shape(lambda d,x=x:ell(d,x+L*.6-.4,26.2,.8,.7),VOID,flat='#ffe0e0')
    c.shape(lambda d:poly(d,[(47+L*.5,34),(54+L*.5,34),(53+L*.5,35.3),(48+L*.5,35.3)]),VOID,flat='#c8a0ff')
    # braço da frente
    if at:
        c.shape(lambda d:cap(d,57+L*.4,45,70,48,6.5),ROBE);c.shape(lambda d:ell(d,71,48,3,3),'#6a4a30 #a07850 #d0a878 #f0d0a0',blur=1)
        c.shape(lambda d:poly(d,[(72,46),(99,43),(101,45),(99,47),(72,50)]),STEEL,blur=.7);c.shape(lambda d:cap(d,71,43,71,53,2),GOLD,blur=.8)
        c.shape(lambda d:ell(d,100,45,4,4),VOID,flat='#ff3a4a');
    else:
        c.shape(lambda d:cap(d,58+L*.4,46,65,56,6.5),ROBE);c.shape(lambda d:ell(d,66,57,3,3),'#6a4a30 #a07850 #d0a878 #f0d0a0',blur=1)
        c.shape(lambda d:poly(d,[(64,55),(67,56),(77,34),(74,32)]),STEEL,blur=.7);c.shape(lambda d:cap(d,62,54,70,58,2),GOLD,blur=.8)
        c.shape(lambda d:ell(d,77,31,2.4,2.4),VOID,flat='#ff3a4a')
    return c
def rot(im,ang,AX=46,AY=92):
    cvs=Image.new('RGBA',(CW*2,CH*2),(0,0,0,0));cvs.paste(im,(CW//2,CH//2),im)
    r=cvs.rotate(ang,center=(CW//2+AX,CH//2+AY),resample=Image.NEAREST);a=np.array(r);a[...,3]=np.where(a[...,3]>0,255,0)
    return Image.fromarray(a,'RGBA')
def tint(im,f):
    a=np.array(im).astype(float);m=a[...,3]>0;a[m,:3]=np.clip(a[m,:3]*(1+f)+60*f,0,255);return Image.fromarray(a.astype(np.uint8),'RGBA')
def atlas(fn,out,name):
    idle=finish(fn('idle'));att=finish(fn('attack'))
    hurt=tint(rot(idle,10),.55)
    d0=rot(idle,-84);bb=d0.getbbox();d=Image.new('RGBA',d0.size,(0,0,0,0));d.paste(d0,(0,CH//2+92+2-bb[3]),d0);death=tint(d,-.3)
    fr=[]
    for f in(idle,hurt,att,death):
        c=Image.new('RGBA',(CW*2,CH*2),(0,0,0,0))
        c.paste(f,(0,0),f) if f.size==(CW*2,CH*2) else c.paste(f,(CW//2,CH//2),f);fr.append(c.crop((CW//2-6,CH//2,CW//2+CW+30,CH//2+CH+2)))
    W,H=fr[0].size;A=Image.new('RGBA',(W*4,H),(0,0,0,0))
    for i,f in enumerate(fr):A.paste(f,(i*W,0),f)
    A.save(f'{out}/{name}_px_atlas.png');json.dump({'w':W,'h':H,'ax':52,'ay':94,'cols':4,'anims':{'idle':[0],'hurt':[1],'attack':[2],'death':[3]}},open(f'{out}/{name}_px_atlas.json','w'))
if __name__=='__main__':
    out=sys.argv[1];import os;os.makedirs(out,exist_ok=True)
    for n,f in(('guardac',guard),('cult',cult)):atlas(f,out,n)
