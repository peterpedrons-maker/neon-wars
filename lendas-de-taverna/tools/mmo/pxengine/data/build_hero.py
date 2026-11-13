import json,sys
sys.path.insert(0,'.')
from pxdraw import *
PL='EFGH';GD='IJKL';TAN='ABCD';HAIR='hijl';CAPE='MNQT'
def part(g,anchor,half=False):return {'anchor':anchor,'rows':g.rows(half),**({'mirror':True} if half else {})}
hero={'name':'hero','canvas':[100,88],'ground':82,'nomouth':True,'hip':26,'tdy':7,'hdy':7,'hdy_f':7,'hx_side':44,'hx_front':50,
 'limbs':{'thigh':11.5,'shin':10.5,'upper':7.0,'fore':6.5,'r':{'thigh':[3.7,3.0],'shin':[3.1,2.6],'upper':[2.7,2.3],'fore':[2.3,2.1],'knee':3.2,'elbow':2.6,'hand':2.8},'mat':{'leg':'plate','arm':'plate','far_tone':-1}},
 'equipment':{'pauldron':True,'kneepad':True},'parts':{}}
P=hero['parts']
# ---- cabeça de lado (olhando para a direita)
h=G(26,26)
h.ell(12,14,8.5,9,TAN)                                    # rosto
h.poly([(15,16),(20,16),(20,19),(15,22)],TAN)             # queixo
h.px(20,14,'C');h.px(21,15,'C');h.px(21,16,'B')           # nariz
h.ell(11,8,10,8,HAIR)                                     # cabelo
h.poly([(12,4),(22,9),(21,11),(16,9),(12,10)],HAIR)       # franja
h.poly([(4,8),(0,18),(5,22),(8,14)],HAIR)                 # rabo de cabelo
h.poly([(2,10),(0,15),(3,13)],'ijl'[:3])
h.ell(11,15,2,2.6,'BBCC');h.px(11,15,'A')                 # orelha
h.line(6,8,19,9,'J');h.line(6,7,19,8,'K')                 # tiara dourada
h.px(18,13,'w');h.px(19,13,'w');h.px(19,14,'G');h.px(18,14,'G');h.px(19,14,'k')   # olho
h.line(17,11,21,12,'h')                                   # sobrancelha
h.line(17,19,20,19,'S');h.px(15,20,'A')                   # boca
h.outline();P['head_side']=part(h,[11,23])
f=G(25,26)
f.ell(12,14,8.6,9,TAN);f.ell(12,8,10,8,HAIR)
f.poly([(3,9),(5,2),(8,8)],HAIR);f.poly([(8,8),(12,1),(16,8)],HAIR);f.poly([(16,8),(19,2),(21,9)],HAIR)
f.poly([(5,10),(12,12),(19,10),(19,8),(5,8)],HAIR)
f.line(4,9,20,9,'J');f.line(4,8,20,8,'K')
for ex in (8,16):
    f.px(ex-1,14,'w');f.px(ex,14,'w');f.px(ex+1,14,'w');f.px(ex,14,'G');f.px(ex,15,'k');f.px(ex-1,15,'w');f.px(ex+1,15,'w')
f.line(5,12,10,12,'h');f.line(14,12,19,12,'h')
f.px(12,16,'B');f.px(12,17,'B');f.px(11,18,'A');f.line(10,20,14,20,'S')
f.px(3,15,'B');f.px(21,15,'B')
f.outline();P['head_front']=part(f,[12,23],True)
b=G(25,26)
b.ell(12,14,8.6,9,HAIR);b.ell(12,9,10,9,HAIR)
b.poly([(3,9),(5,2),(8,8)],HAIR);b.poly([(8,8),(12,1),(16,8)],HAIR);b.poly([(16,8),(19,2),(21,9)],HAIR)
b.poly([(7,16),(12,26),(17,16)],HAIR);b.line(12,5,12,20,'h');b.line(4,9,20,9,'J')
b.outline();P['head_back']=part(b,[12,23],True)
# ---- tronco
t=G(24,16);t.ell(12,8,10.5,7.5,PL);t.line(3,12,21,12,'E');t.line(4,9,20,9,'F');t.ell(12,5,3,2.5,GD);t.px(12,4,'L')
t.line(3,3,21,3,'J');t.px(6,6,'H');t.px(18,6,'H');t.px(6,11,'H');t.px(18,11,'H')
t.outline();P['torso_side']=part(t,[12,5])
tf=G(27,16);tf.ell(13,8,12,7.5,PL);tf.ell(13,7,4,4,GD);tf.px(13,6,'L');tf.px(12,6,'L');tf.line(4,12,22,12,'E');tf.line(5,3,21,3,'J')
tf.line(4,9,9,9,'F');tf.line(17,9,22,9,'F');tf.px(5,6,'H');tf.px(21,6,'H');tf.px(5,11,'H');tf.px(21,11,'H')
tf.outline();P['torso_front']=part(tf,[13,5],True)
tb=G(27,16);tb.ell(13,8,12,7.5,PL);tb.ell(13,10,9,6.5,CAPE);tb.line(13,3,13,16,'M');tb.line(5,3,21,3,'J');tb.outline();P['torso_back']=part(tb,[13,5],True)
be=G(24,5);be.rect(1,1,22,3,'f');be.line(1,1,22,1,'g');be.rect(10,0,13,4,'I');be.rect(11,1,12,3,'K');be.outline();P['belt_side']=part(be,[12,2])
bf=G(27,5);bf.rect(1,1,25,3,'f');bf.line(1,1,25,1,'g');bf.rect(11,0,15,4,'I');bf.rect(12,1,14,3,'K');bf.outline();P['belt_front']=part(bf,[13,2],True)
cs=G(24,13);cs.poly([(2,0),(21,0),(22,10),(17,8),(12,13),(7,8),(1,10)],CAPE,light=(-.3,-.6));cs.line(2,11,22,10,'T') if False else None;cs.line(3,2,20,2,'T');cs.line(1,10,6,8,'J');cs.line(6,8,12,13,'J');cs.line(12,13,17,8,'J');cs.line(17,8,22,10,'J');cs.outline();P['cloth_side']=part(cs,[11,0])
cf=G(27,13);cf.poly([(2,0),(24,0),(25,10),(19,8),(13,13),(7,8),(1,10)],CAPE,light=(-.3,-.6));cf.line(3,2,23,2,'T');cf.line(1,10,7,8,'J');cf.line(7,8,13,13,'J');cf.line(13,13,19,8,'J');cf.line(19,8,25,10,'J');cf.outline();P['cloth_front']=part(cf,[13,0],True)
bs=G(18,11);bs.poly([(1,1),(11,1),(12,4),(17,6),(17,10),(1,10)],PL);bs.line(1,3,11,3,'J');bs.line(1,4,11,4,'K');bs.line(2,9,16,9,'E');bs.outline();P['boot_side']=part(bs,[5,9])
bo=G(16,11);bo.poly([(2,1),(13,1),(15,10),(0,10)],PL);bo.line(2,3,13,3,'J');bo.line(2,4,13,4,'K');bo.line(1,9,14,9,'E');bo.outline();P['boot_front']=part(bo,[8,9])
for nm in ('pauld_side','pauld_front'):
    p=G(16,14);p.ell(8,7,7,6,GD);p.ell(8,7.5,5.4,4.6,PL);p.px(8,4,'H');p.px(6,6,'H');p.px(8,10,'L') if False else None;p.px(8,7,'L');p.line(3,9,13,9,'E');p.outline();P[nm]=part(p,[8,7])
kp=G(10,9);kp.ell(5,4.5,4.5,4,GD);kp.ell(5,4.5,3,2.6,PL);kp.px(5,4,'L');kp.outline();P['kneepad']=part(kp,[5,4])
br=G(7,4);br.rect(0,0,6,2,'f');br.outline();P['bracer']=part(br,[3,1])
sw=G(52,12)
sw.line(1,6,9,6,'f');sw.line(1,5,9,5,'g');sw.line(1,7,9,7,'e');sw.ell(2,6,2.6,2.6,GD);sw.px(2,6,'L')       # cabo + pomo
sw.poly([(9,0),(12,0),(12,12),(9,12)],GD);sw.line(10,1,10,11,'K')                                         # guarda
sw.poly([(12,3),(46,4),(51,6),(46,8),(12,9)],'mnoO');sw.line(13,4,46,5,'O');sw.line(13,6,47,6,'m');sw.line(13,8,46,8,'n')
sw.px(20,6,'G');sw.px(28,6,'G');sw.px(36,6,'G')                                                           # runas azuis
sw.outline();P['cleaver']=part(sw,[3,6])
json.dump(hero,open('hero.json','w'),indent=1)
