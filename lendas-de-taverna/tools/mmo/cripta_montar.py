import numpy as np,random,json,os
from PIL import Image,ImageDraw,ImageFilter
random.seed(21)
S=.5
def L(n):return Image.open(f'cn/{n}.png').convert('RGBA')
def sc(im,s=S):return im.resize((max(1,round(im.width*s)),max(1,round(im.height*s))),Image.LANCZOS)
def ft(n):
    t=L(n);w,h=t.size;return sc(t.crop((14,14,w-14,h-24)))
FL=[ft('chao_1'),ft('chao_2'),ft('chao_1'),ft('chao_3'),ft('chao_4'),ft('chao_2')]
CARP=ft('chao_7');CAP=ft('chao_8');CARP=CARP.crop((0,3,CARP.width,CARP.height-3));CAP=CAP.crop((0,3,CAP.width,CAP.height))
def wl(n):
    w=L(n);return sc(w.crop((5,0,w.width-5,w.height)))
WP=[wl('parede_1'),wl('parede_1'),wl('parede_3'),wl('parede_4')]
tw,th=FL[0].size;wh=WP[0].height;cap_h=int(wh*.2);side=34;F=74
AS=.86
arch=sc(L('porta_1'),S*AS);aw,ah=arch.size;leaf=sc(L('porta_2'),S*AS)
ar=np.array(arch);opn=(ar[:,:,:3].max(2)<14)&(ar[:,:,3]>0);ys,xs=np.where(opn);ox0,ox1,oy0,oy1=xs.min(),xs.max(),ys.min(),ys.max()
# vão: chão iluminado (mais escuro no alto, claro embaixo) em vez de preto
_t=Image.new('RGBA',(aw,ah))
for _i in range(0,aw,tw):
    for _j in range(0,ah,th):_t.alpha_composite(FL[0],(_i,_j))
_t=np.array(_t).astype(float);_g=(0.62+0.5*np.linspace(0,1,ah)**1.2)[:,None,None]
_t[:,:,:3]=np.clip(_t[:,:,:3]*_g*1.08+np.array([8,6,0]),0,255)
_ar=ar.copy().astype(float);_ar[opn]=_t[opn]
arch_lit=Image.fromarray(_ar.astype('uint8'),'RGBA')
import scipy.ndimage as ndi
_lum=ar[:,:,:3].astype(float).mean(2);_stone=(ar[:,:,3]>0)&(_lum>119)&~opn
_lab,_n=ndi.label(_stone,structure=np.ones((3,3)));_sz=ndi.sum(_stone,_lab,range(1,_n+1));_ring=np.isin(_lab,[i+1 for i,z in enumerate(_sz) if z>=40])
_inner=ndi.binary_fill_holes(_ring|opn)         # anel + vão
_keep=ndi.binary_dilation(_ring,iterations=1)&(ar[:,:,3]>0)|ndi.binary_dilation(opn,iterations=1)&(ar[:,:,3]>0)
_keep&=ndi.binary_dilation(_inner,iterations=1)
_arr=_ar.copy();_arr[~_keep]=0;_arr[~_keep,3]=0
arch_lit=Image.fromarray(_arr.astype('uint8'),'RGBA')
_fr=ar.copy();_fr[opn]=[0,0,0,0];_fr[~_keep]=0;_fr[~_keep,3]=0;_fr[~(_keep&~opn),3]=0;arch_frame=Image.fromarray(_fr,'RGBA')
def _path(n):
    for pre,d in (('p_','d2/prop_'),('x_','d2/dec_'),('v_','d2/wall_')):
        if n.startswith(pre):return f'{d}{n[2:]}.png'
    return f'decor/{n}.png'
D=lambda n,h:(lambda im:im.resize((max(1,round(im.width*h/im.height)),h),Image.LANCZOS))(Image.open(_path(n)).convert('RGBA'))
def DW(n,w):
    im=Image.open(_path(n)).convert('RGBA');return im.resize((w,max(1,round(im.height*w/im.width))),Image.LANCZOS)
def tall_wall(w,segw):
    A=w.crop((0,0,segw,wh-8));B=w.crop((0,cap_h,segw,wh-8));C=w.crop((0,wh-8,segw,wh))
    im=Image.new('RGBA',(segw,A.height+B.height+C.height),(0,0,0,0));im.alpha_composite(A,(0,0));im.alpha_composite(B,(0,A.height));im.alpha_composite(C,(0,A.height+B.height));return im
BH=(wh-8)+(wh-8-cap_h)+8
_bf=Image.open('d2/boss_porta_vazia.png').convert('RGBA');_bs=BH/_bf.height;_bf=_bf.resize((round(_bf.width*_bs),BH),Image.LANCZOS)
_ba=np.array(_bf);_bo=(_ba[:,:,:3].max(2)<22)&(_ba[:,:,3]>0);_bl,_bn=ndi.label(_bo);_bz=ndi.sum(_bo,_bl,range(1,_bn+1));_bo=_bl==(int(np.argmax(_bz))+1)
_ys,_xs=np.where(_bo);OW=int(_xs.max()-_xs.min()+1)-6;_ba[_bo]=[0,0,0,0];BOSS_FR=Image.fromarray(_ba,'RGBA');print('porta do chefe',BOSS_FR.size,'vão',OW)
# layout (de baixo para cima): (nome, colunas, linhas, deslocamento do corredor de saída em colunas)
ROOMS=[('atrio',7,4,0),('guardioes',6,5,-1),('armadilhas',9,3,1),('altares',6,5,0),('cofre',4,3,-1),('camara',9,7,None)]
COR_ROWS=2.25
CW=9*tw+2*side
# calcula posições de cima para baixo
y=0;placed=[]
for idx in range(len(ROOMS)-1,-1,-1):
    nm,c,r,off=ROOMS[idx]
    band_y=y;floor_y=y+wh;floor_h=int(r*th);placed.append(dict(i=idx,nm=nm,c=c,r=r,off=off,band_y=band_y,floor_y=floor_y,floor_h=floor_h,x0=(CW-c*tw)//2))
    y=floor_y+floor_h
    if idx>0:
        cor_h=int(COR_ROWS*th);placed[-1]['cor_y']=y;placed[-1]['cor_h']=cor_h;y+=cor_h
H=y+wh-F+10
placed.sort(key=lambda p:p['i'])
# corredor que entra em R(k+1) pelo sul sai da porta de R(k): coluna absoluta
for p in placed:
    if p['off'] is not None:p['door_cx']=CW//2+p['off']*tw
bg=Image.new('RGBA',(CW,H),(6,8,12,255));front=Image.new('RGBA',(CW,H),(0,0,0,0))
walk=np.zeros((H,CW),bool);hard=np.zeros((H,CW),bool)
def put(img,im,x,y):img.alpha_composite(im,(int(x),int(y)))
def floorfill(x0,y0,w,h,carpet_col=None,carpet_rows=0):
    for j in range(int(np.ceil(h/th))):
        for i in range(int(np.ceil(w/tw))):
            t=random.choice(FL) if random.random()<.85 else FL[0]
            put(bg,t.crop((0,0,min(tw,w-i*tw),min(th,h-j*th))),x0+i*tw,y0+j*th)
for p in placed:
    nm,c,r=p['nm'],p['c'],p['r'];x0=p['x0'];fy=p['floor_y'];fh=p['floor_h'];rw=c*tw
    floorfill(x0,fy,rw,fh)
    # tapete: do arco para baixo
    if p['off'] is not None and nm in('atrio','guardioes','altares','camara'):
        cx=p['door_cx'];cols=[(cx-tw//2)]
        for j in range(r):put(bg,CARP if j<r-1 else CAP,cols[0],fy+j*(th-6)) if False else put(bg,CARP.resize((CARP.width,th)) if j<r-1 else CAP.resize((CAP.width,th)),cols[0],fy+j*th)
    # parede norte (faixa): tijolo contínuo, passagem aberta (sem porta) e decoração de parede
    cur=x0;banners=[]
    while cur<x0+rw:
        w=random.choice(WP[:3])
        put(bg,w.crop((0,0,min(w.width,x0+rw-cur),w.height)),cur,p['band_y']);cur+=w.width
    gapx=p['door_cx'] if p['off'] is not None else None
    if gapx is not None:floorfill(gapx-tw//2,p['band_y'],tw,wh)
    BCOL={'atrio':'v_est_verm','guardioes':'v_est_azul','armadilhas':'v_est_verde','altares':'v_est_verm','cofre':'v_est_azul','camara':'v_est_verm'}[nm]
    for frac,kind in ((.2,'b'),(.8,'b'),(.5,'w')):
        xx=int(x0+rw*frac)
        if gapx is not None and abs(xx-gapx)<tw*.95:continue
        if kind=='b':im=D(BCOL,98);put(bg,im,xx-im.width//2,p['band_y']+cap_h-3)
        else:im=D('v_janela',76);put(bg,im,xx-im.width//2,p['band_y']+cap_h+12)
        banners.append(xx)
    p['banners']=banners
    # laterais (capa rotacionada)
    LH=fh+wh
    capstrip=WP[0].crop((0,0,WP[0].width,cap_h)).resize((LH,side)).rotate(90,expand=True).crop((0,0,side,LH))
    LH2=(fy+fh-F+cap_h)-p['band_y'];cs2=WP[0].crop((0,0,WP[0].width,cap_h)).resize((LH2,side)).rotate(90,expand=True).crop((0,0,side,LH2))
    put(front,cs2,x0-side,p['band_y']);put(front,cs2.transpose(Image.FLIP_LEFT_RIGHT),x0+rw,p['band_y'])
    # parede sul alta na camada da frente, com vão para o corredor (exceto a primeira sala)
    bottom=fy+fh;gx=None
    if p['i']>0:
        prev=placed[p['i']-1];gx=prev['door_cx']
    boss=(p['i']==5)
    BG_=tw
    cur=x0-side
    while cur<x0+rw+side:
        w=WP[0]
        for sx_ in range(0,w.width,1):pass
        segw=min(w.width,x0+rw+side-cur)
        seg=w.crop((0,0,segw,w.height))
        if gx is not None and cur<gx+BG_//2 and cur+seg.width>gx-BG_//2:
            a0=max(0,gx-BG_//2-cur);a1=min(seg.width,gx+BG_//2-cur)
            if a0>0:put(front,seg.crop((0,0,a0,seg.height)),cur,bottom-F)
            if a1<seg.width:put(front,seg.crop((a1,0,seg.width,seg.height)),cur+a1,bottom-F)
        else:put(front,seg,cur,bottom-F)
        cur+=w.width
    if boss and gx is not None:
        lf=Image.open('d2/boss_folha_esq.png').convert('RGBA');lh=wh-6;lw=max(8,round(lf.width*lh/lf.height))
        lfs=lf.resize((lw,lh),Image.LANCZOS).resize((max(8,lw//2),lh),Image.LANCZOS)     # folha aberta: recolhida na lateral
        put(front,lfs,gx-tw//2,bottom-F+2);put(front,lfs.transpose(Image.FLIP_LEFT_RIGHT),gx+tw//2-lfs.width,bottom-F+2)
        sk=D('v_placa',34);put(front,sk,gx-sk.width//2,bottom-F+cap_h+4)
        p['boss_door']=[int(gx),int(bottom-F)]
    # andável
    m=14
    walk[fy+6:bottom-F+24,x0+m:x0+rw-m]=True
    if gx is not None:walk[bottom-F+24:bottom+8,gx-BG_//2+10:gx+BG_//2-10]=True
    # abertura do arco: do chão da sala até acima da faixa
    if p['off'] is not None:
        cx=p['door_cx'];walk[p['band_y']+int(wh*.4):fy+8,cx-tw//2+14:cx+tw//2-14]=True
    # corredor para a sala seguinte (fica acima da faixa desta sala? não: abaixo da sala k+1)
# corredores
SP='ex/sp/spritepilot-environment-pack/32px/'
def spf(n,k,scl=2):
    im=Image.open(SP+n).convert('RGBA');fw=im.height;return im.crop((k*fw,0,k*fw+fw,fw)).resize((fw*scl,fw*scl),Image.NEAREST)
props=[];torches=[]
for p in placed:
    if 'cor_y' not in p:continue
    below=placed[p['i']-1];gx=below['door_cx'];cy=p['cor_y'];ch=p['cor_h']
    floorfill(gx-tw//2,cy,tw,ch)
    capstrip=WP[0].crop((0,0,WP[0].width,cap_h)).resize((ch+cap_h,side)).rotate(90,expand=True).crop((0,0,side,ch))
    top=cy-F;LHc=below['band_y']+cap_h-top;csc=WP[0].crop((0,0,WP[0].width,cap_h)).resize((LHc,side)).rotate(90,expand=True).crop((0,0,side,LHc))
    put(front,csc,gx-tw//2-side,top);put(front,csc.transpose(Image.FLIP_LEFT_RIGHT),gx+tw//2,top)
    walk[cy-F+26:below['floor_y']+8,gx-tw//2+14:gx+tw//2-14]=True
    # chão do corredor entre a faixa e a parede da sala de cima já coberto; tapete no corredor
for p in placed:
    # tochas nas faixas, dos dois lados do arco
    cxs=[p['x0']+tw//2+int(.3*tw),p['x0']+p['c']*tw-tw//2-int(.3*tw)]
    for tx in sorted(set(cxs)):
        if p['x0']+30<tx<p['x0']+p['c']*tw-30 and all(abs(tx-bx)>46 for bx in p.get('banners',[])) and all(abs(tx-ox)>110 or abs(oy-(p['band_y']+int(wh*.30)))>20 for ox,oy in torches):torches.append((tx,p['band_y']+int(wh*.30)))
# props: (sprite, x, base_y, altura)
import math
decals=[]
for p in placed:
    nm=p['nm'];fy=p['floor_y'];fh=p['floor_h'];x0=p['x0'];rw=p['c']*tw;b=fy+fh-F;mid=x0+rw//2
    if nm=='atrio':
        props+=[('f_braseiro',p['door_cx']-int(1.1*tw),fy+int(.7*th),62),('f_braseiro',p['door_cx']+int(1.1*tw),fy+int(.7*th),62),('f_pilar',x0+int(.45*tw),fy+int(1.5*th),104),('f_pilar',x0+rw-int(.45*tw),fy+int(1.5*th),104)]
    if nm=='guardioes':
        props+=[('f_estatua',mid,fy+int(.95*th),124),('f_pilar',x0+int(.5*tw),fy+int(1.2*th),104),('f_pilar',x0+rw-int(.5*tw),fy+int(1.2*th),104),('p_rack',x0+int(1.05*tw),fy+52,70),('p_rack',x0+rw-int(1.05*tw),fy+52,70)]
        decals+=[('x_runa',mid+int(.4*tw),fy+int(fh*.6),170,.95)]
    if nm=='armadilhas':
        props+=[('f_pilar',x0+int(.5*tw),fy+int(1.1*th),104),('f_pilar',x0+rw-int(.5*tw),fy+int(1.1*th),104)]
        for ci_ in range(4):
            xx=x0+int(tw*(1.6+1.6*ci_))
            if abs(xx-p['door_cx'])<tw*.8:continue
            decals.append(('x_placa_on' if ci_%2 else 'x_placa_off',xx,fy+int(fh*.55),82,1))
    if nm=='altares':
        props+=[('f_altar',x0+int(.9*tw),fy+int(1.7*th),70),('f_altar',x0+rw-int(.9*tw),fy+int(1.7*th),70),('f_altar',mid,fy+int(.9*th),70),('f_pilar',x0+int(.45*tw),b-4,104),('f_pilar',x0+rw-int(.45*tw),b-4,104)]
    if nm=='cofre':
        props+=[('p_bau',x0+int(.55*tw),fy+44,52),('p_prateleira',x0+rw-int(1.0*tw),fy+42,50),('f_jaula',x0+rw-int(.55*tw),b-4,92)]
    if nm=='camara':
        cx=mid;cyy=fy+int(fh*.50)
        props+=[('f_altar',cx,cyy+34,110)]
        for k in range(8):
            a_=k*math.pi/4+math.pi/8;props.append(('f_pilar',int(cx+math.cos(a_)*(rw*.40)),int(cyy+math.sin(a_)*(fh*.36))+30,112))
        props+=[('f_estatua',x0+int(.6*tw),b-4,124),('f_estatua',x0+rw-int(.6*tw),b-4,124)]
        decals+=[('x_runa',cx,cyy+22,330,.9)]
for n,cx,cy,w_,al in decals:
    im=DW(n,w_)
    if al<1:
        a=np.array(im);a[:,:,3]=(a[:,:,3]*al).astype('uint8');im=Image.fromarray(a,'RGBA')
    put(bg,im,cx-im.width//2,cy-im.height//2)
# regra: nada de objeto em cima do tapete / do caminho da porta
_dc={p['i']:p.get('door_cx') for p in placed}
def _room_of(by):
    for p in placed:
        if p['floor_y']-5<=by<=p['floor_y']+p['floor_h']+5:return p
    return None
_ok=[]
for n,x,by,h in props:
    p=_room_of(by)
    if p is not None and p.get('door_cx') is not None and p['nm'] in ('atrio','guardioes','altares') and abs(x-p['door_cx'])<tw*.85:continue
    _ok.append((n,x,by,h))
props=_ok
# aranhas nos cantos das faixas
webs=[]
for p in placed:
    if random.random()<.8:webs.append(('w_teia',p['x0']+8,p['band_y']+4,60,False));webs.append(('w_teia',p['x0']+p['c']*tw-8,p['band_y']+4,60,True))
# bloqueios das props
cache={}
def spr(n,h):
    if (n,h) not in cache:cache[(n,h)]=D(n,h)
    return cache[(n,h)]
for n,x,by,h in sorted(props,key=lambda t:t[2]):
    im=spr(n,h);put(bg,im,x-im.width//2,by-im.height)
    fw=max(14,int(im.width*.55));hard[by-int(im.height*.18):by+6,x-fw//2:x+fw//2]=True
for n,x,y,h,fl in webs:
    im=spr(n,h);im=im.transpose(Image.FLIP_LEFT_RIGHT) if fl else im
    put(bg,im,x-(im.width if fl else 0),y)
walk&=~hard
# tochas (frame estático) e luzes
glow=Image.new('RGBA',(CW,H),(0,0,0,0));gd=ImageDraw.Draw(glow)
for tx,ty in torches:
    put(bg,spf('wall-torch-32px_strip8.png',2),tx-32,ty-24)
    gd.ellipse((tx-120,ty+10,tx+120,ty+260),fill=(255,150,50,34))
glow=glow.filter(ImageFilter.GaussianBlur(26));bg.alpha_composite(glow)
# vinheta de profundidade no chão (escurece perto das paredes) e leve névoa fria
arr=np.array(bg).astype(float)
arch_frame.save('cripta_arco_frame.png');arch_lit.save('cripta_arco_lit.png')
json.dump({'W':CW,'H':H,'arch':[aw,ah,int(ox0),int(ox1),int(oy0),int(oy1)],'torches':torches,'rooms':[{k:(int(v) if isinstance(v,(int,np.integer)) else v) for k,v in p.items() if v is not None} for p in placed],'props':[(n,int(x),int(b),int(h)) for n,x,b,h in props]},open('cripta_layout.json','w'))
bg.save('cripta_bg.png');front.save('cripta_front.png');np.save('cripta_walk.npy',walk)
ov=np.array(bg.convert('RGB')).copy();ov[walk]=(ov[walk]*.6+np.array([0,200,60])*.4).astype('uint8');Image.fromarray(ov).resize((CW//3,H//3)).save('cripta_walk_ov.png')
comp=bg.copy();comp.alpha_composite(front);comp.convert('RGB').save('cripta_mapa_completo.png')
comp.convert('RGB').resize((CW*2//5,H*2//5),Image.LANCZOS).save('cripta_overview.png');print('ok',CW,H,len(props),len(torches))
