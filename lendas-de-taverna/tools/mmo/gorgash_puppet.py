"""Marionete do Gorgash: corta a folha de partes de IA (gorgash_parts/parts.jpg, 5x3) e monta ciclos por esqueleto (cinemática direta).
Uso: python3 gorgash_puppet.py <pasta_saida>   -> parts_contact.png, walk_sheet.png, walk.gif"""
import sys,os,math
import numpy as np
from PIL import Image,ImageDraw,ImageEnhance
from scipy import ndimage as ND
import cut_grid as CG
SRC=os.path.join(os.path.dirname(os.path.abspath(__file__)),'gorgash_parts','parts.jpg')
def cells():
    im=Image.open(SRC).convert('RGB');W,H=im.size;out=[]
    for r in range(3):
        for c in range(5):
            x0,x1,y0,y1=round(W*c/5),round(W*(c+1)/5),round(H*r/3),round(H*(r+1)/3)
            cell=np.array(im.crop((x0+5,y0+5,x1-5,y1-5)));cell[:46,:50]=(255,0,255)   # número da célula
            k=CG.key(Image.fromarray(cell));lb,n=ND.label(k[:,:,3]>0)
            if n:
                sz=ND.sum(k[:,:,3]>0,lb,range(1,n+1));k[~np.isin(lb,[i+1 for i,v in enumerate(sz) if v>sz.max()*.05]),3]=0
            f=Image.fromarray(k,'RGBA');out.append(f.crop(f.getchannel('A').getbbox()))
    return out
def upright(f,flip_if_wider_bottom=True):
    """gira o membro para o eixo ficar vertical (PCA) e deixa a ponta mais larga em cima"""
    a=np.array(f.getchannel('A'))>0;ys,xs=np.nonzero(a);c=np.cov(np.vstack([xs,ys]));w,v=np.linalg.eigh(c);ax=v[:,1]
    ang=math.degrees(math.atan2(ax[0],ax[1]))
    if ang>90:ang-=180
    if ang<-90:ang+=180
    g=f.rotate(ang,resample=Image.BICUBIC,expand=True)
    g=g.crop(g.getchannel('A').getbbox());m=np.array(g.getchannel('A'))>0;h=m.shape[0]
    if flip_if_wider_bottom and m[int(h*.75):].sum()>m[:int(h*.25)].sum()*1.15:g=g.rotate(180,expand=True)
    return g
def thigh_up(f):
    """coxa: eixo = do centro da pele verde (cima) até a joelheira de metal (baixo); gira para a vertical"""
    a=np.array(f);al=a[:,:,3]>0;r,g,b=[a[:,:,i].astype(int) for i in range(3)]
    skin=al&(g>r+12)&(g>b+25);metal=al&~skin&(abs(r-g)<22)&(abs(g-b)<28)&(g>70)
    sy,sx=np.nonzero(skin);my,mx=np.nonzero(metal)
    if len(sx)<50 or len(mx)<30:return upright(f)
    v=(mx.mean()-sx.mean(),my.mean()-sy.mean());ang=math.degrees(math.atan2(v[0],v[1]))
    g2=f.rotate(ang,resample=Image.BICUBIC,expand=True);return g2.crop(g2.getchannel('A').getbbox())
def prep():
    P=cells();q={}
    q['head']=P[0];q['torso']=P[1];q['pauN']=P[2];q['pauF']=P[3]
    q['uaN']=upright(P[4]);q['uaF']=upright(P[6])
    q['faN']=P[5].rotate(-90,expand=True);q['faF']=P[7].rotate(-90,expand=True)
    q['thN']=thigh_up(P[8]);q['shN']=P[9];q['thF']=thigh_up(P[10]);q['shF']=P[11]
    q['loin']=P[12];q['axe']=P[13]
    for k in q:q[k]=q[k].crop(q[k].getchannel('A').getbbox())
    return q
def dark(f,v=.72):
    a=np.array(f).astype(np.float32);a[:,:,:3]*=v;return Image.fromarray(a.astype(np.uint8),'RGBA')
class Canvas:
    def __init__(s,w,h):s.im=Image.new('RGBA',(w,h),(0,0,0,0))
    def put(s,part,pivot,pos,ang,scale=1.0):
        """cola 'part' com o ponto 'pivot' (px na parte) em 'pos' do mundo, girado 'ang' graus (positivo = sentido horário na tela)"""
        if scale!=1:part=part.resize((max(1,round(part.width*scale)),max(1,round(part.height*scale))),Image.LANCZOS);pivot=(pivot[0]*scale,pivot[1]*scale)
        R=int(math.hypot(max(pivot[0],part.width-pivot[0]),max(pivot[1],part.height-pivot[1])))+2
        pad=Image.new('RGBA',(2*R,2*R),(0,0,0,0));pad.alpha_composite(part,(int(R-pivot[0]),int(R-pivot[1])))
        pad=pad.rotate(ang,resample=Image.BICUBIC,center=(R,R));s.im.alpha_composite(pad,(int(round(pos[0]-R)),int(round(pos[1]-R))))
def fwd(p,L,ang):  # ponto a distância L de p, ang graus da vertical (+ = para a direita), y para baixo
    a=math.radians(ang);return (p[0]+L*math.sin(a),p[1]+L*math.cos(a))
def render(Q,pose,W=520,H=560,S=.62):
    """pose: dict com bob, hipN,kneeN,hipF,kneeF (graus), armN,armF (graus no ombro), lean"""
    C=Canvas(W,H);g=H-40;cx=W//2-10
    th=Q['thN'].height*S;sh=Q['shN'].height*S;legL=th*.86+sh*.80
    hip=(cx,g-legL*math.cos(math.radians(8))+pose['bob']-4)
    to=Q['torso'];tw,tH=to.width*S,to.height*S
    # tronco: raiz = base do cinto (centro, 92% da altura)
    tp=(hip[0],hip[1]+2)
    def leg(side,hd,kn,col):
        th_=Q['th'+side];sh_=Q['sh'+side]
        if col!=1:th_,sh_=dark(th_,col),dark(sh_,col)
        hp=(hip[0]+(-2 if side=='N' else 8),hip[1])
        C.put(th_,(th_.width/2,th_.height*.08),hp,hd,S)
        kp=fwd(hp,th_.height*S*.86,hd)
        C.put(sh_,(sh_.width*.5,sh_.height*.10),kp,hd-kn,S)
    # ordem: perna longe, braço longe, tronco, short, perna perto, machado, braço perto
    leg('F',pose['hipF'],pose['kneeF'],.72)
    sho=(tp[0]+8,tp[1]-to.height*S*.74)
    def arm(side,ang,bend,col):
        ua=Q['ua'+side];fa=Q['fa'+side]
        if col!=1:ua,fa=dark(ua,col),dark(fa,col)
        C.put(ua,(ua.width/2,ua.height*.08),sho,ang,S);ep=fwd(sho,ua.height*S*.84,ang)
        C.put(fa,(fa.width/2,fa.height*.10),ep,ang+bend,S);return fwd(ep,fa.height*S*.80,ang+bend)
    handF=arm('F',pose['armF'],14,.72)
    C.put(dark(Q['pauF'],.8),(Q['pauF'].width/2,Q['pauF'].height*.4),(sho[0]+10,sho[1]+4),0,S*.85)
    C.put(to,(to.width/2,to.height*.93),tp,pose.get('lean',0),S)
    hd=Q['head'];neck=(tp[0]+4,tp[1]-to.height*S*.90)
    C.put(hd,(hd.width*.42,hd.height*.80),neck,pose.get('lean',0)*.5,S)
    C.put(Q['loin'],(Q['loin'].width/2,Q['loin'].height*.03),(tp[0]+4,tp[1]-to.height*S*.08),pose['hipN']*.15,S)
    leg('N',pose['hipN'],pose['kneeN'],1)
    handN=arm('N',pose['armN'],16,1)
    ax=Q['axe'];C.put(ax,(ax.width*.22,ax.height*.62),handN,pose.get('axe',18),S*.95)
    C.put(Q['pauN'],(Q['pauN'].width/2,Q['pauN'].height*.4),(sho[0]-4,sho[1]+2),0,S*.85)
    # fantasma da mão da frente por cima do cabo
    return C.im
# guia vermelho e azul (quadril, joelho): perna PERTO e LONGE
POSES=[((28,5),(-22,15)),((10,22),(-26,20)),((0,5),(15,60)),((-12,3),(40,80)),((-22,15),(28,5)),((-26,20),(10,22)),((15,60),(0,5)),((40,80),(-12,3))]
BOB=[4,10,0,-6,4,10,0,-6]
def key_pose(i):
    n,f=POSES[i];A=.62;K=.62;return dict(hipN=n[0]*A,kneeN=n[1]*K,hipF=f[0]*A,kneeF=f[1]*K,armN=-n[0]*.5,armF=-f[0]*.5,bob=BOB[i],lean=2,axe=14+ -n[0]*.25)
def lerp_pose(t,N):
    x=t*8;i=int(math.floor(x))%8;j=(i+1)%8;u=x-math.floor(x);u=u*u*(3-2*u)*.0+u
    a,b=key_pose(i),key_pose(j);return {k:a[k]*(1-u)+b[k]*u for k in a}
if __name__=='__main__':
    o=sys.argv[1];os.makedirs(o,exist_ok=True)
    P=cells();cw=max(f.width for f in P)+10;chh=max(f.height for f in P)+10
    C=Image.new('RGBA',(5*cw,3*chh),(70,80,70,255))
    for i,f in enumerate(P):C.alpha_composite(f,((i%5)*cw,(i//5)*chh))
    C.convert('RGB').save(o+'/parts_contact.png')
    Q=prep()
    names=['head','torso','pauN','pauF','uaN','faN','uaF','faF','thN','shN','thF','shF','loin','axe']
    Cn=Image.new('RGBA',(7*cw,2*chh),(70,80,70,255))
    for i,k in enumerate(names):Cn.alpha_composite(Q[k],((i%7)*cw,(i//7)*chh))
    Cn.convert('RGB').save(o+'/parts_fixed.png')
    N=24;frames=[render(Q,lerp_pose(i/N,N)) for i in range(N)]
    sh=Image.new('RGBA',(8*260,3*280),(86,150,52,255))
    for i,f in enumerate(frames):
        b=f.crop((90,120,350,400));sh.alpha_composite(b,((i%8)*260,(i//8)*280))
    sh.convert('RGB').save(o+'/walk_sheet.png')
    gif=[]
    for f in frames:
        bg=Image.new('RGBA',f.size,(86,150,52,255));bg.alpha_composite(f);gif.append(bg.convert('RGB').crop((90,60,430,520)))
    gif[0].save(o+'/walk.gif',save_all=True,append_images=gif[1:],duration=60,loop=0)
    print('ok')
