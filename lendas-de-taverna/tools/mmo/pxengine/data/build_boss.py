import json,math
class G:
    def __init__(s,w,h):s.w,s.h=w,h;s.g=[['.']*w for _ in range(h)]
    def ell(s,cx,cy,rx,ry,ramp,light=(-.5,-.65),bias=0.0):
        for y in range(s.h):
            for x in range(s.w):
                nx=(x+.5-cx)/rx;ny=(y+.5-cy)/ry;d=nx*nx+ny*ny
                if d<=1:
                    nz=math.sqrt(1-d);l=-(nx*light[0]+ny*light[1])*.62+nz*.55+bias
                    t=min(len(ramp)-1,max(0,int(l*len(ramp)*1.15)));s.g[y][x]=ramp[t]
    def poly(s,pts,ramp,tone=None,light=(-.5,-.65)):
        xs=[p[0] for p in pts];ys=[p[1] for p in pts];cx=sum(xs)/len(xs);cy=sum(ys)/len(ys);rx=(max(xs)-min(xs))/2 or 1;ry=(max(ys)-min(ys))/2 or 1
        for y in range(s.h):
            for x in range(s.w):
                if inside(x+.5,y+.5,pts):
                    nx=(x+.5-cx)/rx;ny=(y+.5-cy)/ry;l=-(nx*light[0]+ny*light[1])*.5+.45
                    t=tone if tone is not None else min(len(ramp)-1,max(0,int(l*len(ramp)*1.15)));s.g[y][x]=ramp[t]
    def rect(s,x0,y0,x1,y1,ch):
        for y in range(y0,y1+1):
            for x in range(x0,x1+1):
                if 0<=x<s.w and 0<=y<s.h:s.g[y][x]=ch
    def px(s,x,y,ch):
        if 0<=x<s.w and 0<=y<s.h:s.g[y][x]=ch
    def line(s,x0,y0,x1,y1,ch):
        n=int(max(abs(x1-x0),abs(y1-y0)))+1
        for i in range(n+1):
            t=i/max(1,n);s.px(round(x0+(x1-x0)*t),round(y0+(y1-y0)*t),ch)
    def outline(s):
        add=[]
        for y in range(s.h):
            for x in range(s.w):
                if s.g[y][x]=='.':
                    for dx,dy in((1,0),(-1,0),(0,1),(0,-1)):
                        xx,yy=x+dx,y+dy
                        if 0<=xx<s.w and 0<=yy<s.h and s.g[yy][xx] not in('.','k'):add.append((x,y));break
        for x,y in add:s.g[y][x]='k'
    def rows(s,half=False):
        r=[''.join(l) for l in s.g]
        if half:r=[l[:s.w//2+1] for l in r]
        # trim empty rows/cols handled by caller
        return r
def inside(x,y,pts):
    c=False;n=len(pts);j=n-1
    for i in range(n):
        xi,yi=pts[i];xj,yj=pts[j]
        if (yi>y)!=(yj>y) and x<(xj-xi)*(y-yi)/(yj-yi+1e-9)+xi:c=not c
        j=i
    return c
SK='UVWX';PL='Z123';BONE='sqr'+'r';LEAT='efgg'
def part(g,anchor,half=False):return {'anchor':anchor,'rows':g.rows(half),**({'mirror':True} if half else {})}
boss={'name':'boss','canvas':[132,100],'ground':92,'nomouth':True,'hip':24,'tdy':9,'hdy':8,'hdy_f':8,'hx_side':60,'hx_front':66,
 'limbs':{'thigh':11.0,'shin':10.0,'upper':9.0,'fore':8.0,'r':{'thigh':[4.7,3.8],'shin':[3.9,3.2],'upper':[3.9,3.3],'fore':[3.3,2.9],'knee':4.1,'elbow':3.5,'hand':3.9},'mat':{'leg':'orc','arm':'orc','far_tone':-1}},
 'equipment':{'pauldron':True,'kneepad':True},'parts':{}}
P=boss['parts']
# cabeça de lado (olhando para a direita)
h=G(30,28)
h.ell(13,17,10,9.5,SK)                                # crânio/rosto
h.poly([(14,18),(25,17),(28,22),(23,26),(14,26)],SK)  # focinho/mandíbula grande
h.ell(12,8,9,5.5,PL)                                  # elmo baixo
h.poly([(7,6),(2,0),(4,9)],BONE[:3],tone=1);h.poly([(5,3),(1,5),(4,8)],BONE[:3],tone=2)   # chifre
h.poly([(11,3),(14,0),(17,3)],PL)
h.rect(8,11,23,12,'Z');h.line(8,11,23,11,'1')         # aba do elmo
h.px(19,16,'4');h.px(20,16,'4');h.px(19,17,'z');h.line(16,14,23,15,'z')
h.poly([(21,23),(24,23),(23,16)],BONE[:3],tone=2);h.px(23,22,'s');h.px(22,19,'s')   # presas
h.line(16,23,23,23,'z');h.line(15,20,16,24,'U');h.px(17,18,'U');h.px(18,19,'V')
h.outline();P['head_side']=part(h,[13,26])
f=G(26,28)
f.ell(12,17,9.5,9.5,SK);f.ell(12,8,9,5.5,PL)
f.poly([(5,7),(0,0),(3,10)],BONE[:3],tone=1);f.poly([(19,7),(24,0),(21,10)],BONE[:3],tone=1)
f.poly([(10,3),(12,0),(14,3)],PL)
f.rect(3,11,21,12,'Z');f.line(3,11,21,11,'1')
f.ell(8,16,2.4,1.9,'4444');f.ell(16,16,2.4,1.9,'4444');f.px(8,16,'z');f.px(16,16,'z');f.line(4,14,10,15,'z');f.line(20,14,14,15,'z')
f.ell(12,20,4,2.5,'VVWW');f.rect(10,21,14,21,'z');f.line(6,24,18,24,'z')
f.poly([(6,21),(8,21),(7,27)],BONE[:3],tone=2);f.poly([(16,21),(18,21),(17,27)],BONE[:3],tone=2)
f.outline();P['head_front']=part(f,[12,26],True)
b=G(26,26)
b.ell(12,15,9.5,9.5,SK);b.ell(12,10,10,8,PL)
b.poly([(5,7),(0,0),(3,10)],BONE[:3],tone=1);b.poly([(19,7),(24,0),(21,10)],BONE[:3],tone=1)
b.line(6,14,18,14,'Z');b.line(12,4,12,13,'1')
b.outline();P['head_back']=part(b,[12,24],True)
# tronco
t=G(24,18);t.ell(12,9,10.5,8.5,PL);t.ell(12,9,8,6.5,PL,bias=.1);t.rect(9,5,15,12,'Z')
t.ell(12,8,3,3,'IJKL');t.line(5,15,19,15,'Z')
t.outline();P['torso_side']=part(t,[12,6])
tf=G(27,18);tf.ell(13,9,12,8.5,PL);tf.ell(13,8,5,4.5,'IJKL');tf.line(3,6,23,6,'2');tf.line(4,13,22,13,'Z')
tf.px(13,8,'L');tf.px(12,7,'L');tf.outline();P['torso_front']=part(tf,[13,6],True)
tb=G(27,18);tb.ell(13,9,12,8.5,PL);tb.ell(13,12,9,5,'MNQT');tb.line(13,2,13,16,'Z');tb.outline();P['torso_back']=part(tb,[13,6],True)
# cinto e saiote de pele
be=G(24,5);be.rect(1,1,22,3,'f');be.line(1,1,22,1,'g');be.rect(10,0,14,4,'I');be.rect(11,1,13,3,'K');be.outline();P['belt_side']=part(be,[12,2])
bf=G(27,5);bf.rect(1,1,25,3,'f');bf.line(1,1,25,1,'g');bf.rect(11,0,15,4,'I');bf.rect(12,1,14,3,'K');bf.outline();P['belt_front']=part(bf,[13,2],True)
cs=G(22,12);cs.poly([(2,0),(20,0),(21,10),(16,8),(12,12),(8,8),(1,10)],'efgg',light=(-.3,-.6));cs.line(3,2,19,2,'g');cs.outline();P['cloth_side']=part(cs,[10,0])
cf=G(25,12);cf.poly([(2,0),(23,0),(24,10),(19,8),(12,12),(6,8),(1,10)],'efgg',light=(-.3,-.6));cf.line(3,2,22,2,'g');cf.outline();P['cloth_front']=part(cf,[12,0],True)
# botas
bs=G(18,10);bs.poly([(1,1),(11,1),(12,4),(17,6),(17,9),(1,9)],'efgg');bs.line(1,3,11,3,'Z');bs.rect(1,8,17,8,'k') if False else None;bs.outline();P['boot_side']=part(bs,[5,8])
bo=G(16,10);bo.poly([(2,1),(13,1),(15,9),(0,9)],'efgg');bo.line(2,3,13,3,'Z');bo.outline();P['boot_front']=part(bo,[8,8])
# ombreiras com espinhos
for nm in ('pauld_side','pauld_front'):
    p=G(16,14);p.ell(8,8,6.5,5,PL);p.poly([(5,5),(8,0),(11,5)],PL);p.line(3,8,13,8,'2');p.px(8,3,'3');p.outline();P[nm]=part(p,[8,7])
kp=G(11,10);kp.ell(5,5,4,3.5,PL);kp.poly([(3,3),(5,0),(7,3)],PL);kp.px(5,2,'3');kp.outline();P['kneepad']=part(kp,[5,5])
br=G(7,4);br.rect(0,0,6,2,'f');br.outline();P['bracer']=part(br,[3,1])
# machado grande
ax=G(56,28)
ax.line(2,14,50,14,'f');ax.line(2,15,50,15,'e');ax.line(2,13,50,13,'g')       # cabo
for x in (6,9,12):ax.rect(x,12,x,16,'e')                                         # tiras de couro
ax.poly([(34,12),(38,2),(50,0),(54,4),(49,10),(49,18),(54,24),(50,28),(38,26),(34,16)],'mnoO');ax.line(38,6,48,3,'O');ax.line(38,22,48,25,'m');ax.ell(41,14,2.4,2.4,'IJKL')
ax.outline();P['cleaver']=part(ax,[4,14])
json.dump(boss,open('boss.json','w'),indent=1)
