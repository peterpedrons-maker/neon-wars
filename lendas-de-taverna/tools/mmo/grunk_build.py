"""Monta o atlas final do Grunk (normal e enfurecido) a partir das 3 folhas de IA: quadros transparentes, elmo ajustado quadro a quadro, pancada corrigida.
Uso: python3 grunk_build.py <pasta_saida> [--check]   (gera grunk_check_*.png para conferir o elmo quadro a quadro)"""
import sys,os,json,math
import numpy as np
from PIL import Image
from scipy import ndimage
import cut_grid,grunk_fx as G
CW,CH=G.CW,G.CH
def place_t(x,bottom=10):
    c=Image.new('RGBA',(CW,CH),(0,0,0,0));c.alpha_composite(x,((CW-x.width)//2,CH-bottom-x.height));return c
def slam_rgba(an):
    s=an['slam'];body5=G.strip_fx(s[4]);body7=G.strip_fx(s[6]);dust=G.fxlayer(s[5],60);out=[]
    for i,f in enumerate(s):
        if i<4 or i==7:out.append(place_t(f));continue
        body=body5 if i==4 else body7
        bb=body.getchannel('A').getbbox();gx=(CW-body.width)//2+(bb[0]+bb[2])//2;gy=CH-10-body.height+bb[3]-4
        cv=Image.new('RGBA',(CW,CH),(0,0,0,0))
        if i>=5:cv.alpha_composite(dust,((CW-dust.width)//2,CH-10-dust.height))
        G.ring(cv,gx,gy,[0,0,0,0,46,92,138][i],fade=[0,0,0,0,0,0.15,0.45][i])
        cv.alpha_composite(body,((CW-body.width)//2,CH-10-body.height));out.append(cv)
    return out
def base_sets(an):
    S={k:[place_t(x) for x in an[k]] for k in('idle','walk','attack','charge','roar','hurt','death')}
    S['roar'][4]=S['roar'][3].copy()   # quadro com o anel vermelho cheio (quadrado) é descartado: o anel é redesenhado por código no jogo
    S['slam']=slam_rgba(an);return S
EYE_NEIGH={'roar':[4]}
EYE_OVR={('charge',4):(237,155)}   # olho marcado à mão onde a detecção falha (cabeça baixa na investida)
HELM_OVR={}   # (anim,i)->(dx,dy,scale) ajuste manual; None = sem elmo
def helmet_frames(name,orig,rec,src,hs,he,eps,S,DX,DY):
    out=[]
    for i,(rc,e,s,dx,dy) in enumerate(zip(rec,eps,S,DX,DY)):
        ov=HELM_OVR.get((name,i),'auto')
        if ov is None or e is None:out.append(rc);continue
        if ov!='auto':dx,dy,s=ov
        sp,sh=G.scaled_helmet(hs,he,s);canvas=rc.copy();lay=Image.new('RGBA',canvas.size,(0,0,0,0))
        lay.paste(sp,(int(round(e[0]-sh[0]+dx)),int(round(e[1]-sh[1]+dy))),sp);
        # recorta o elmo à silhueta do corpo dilatada (nada flutuando solto no ar)
        sil=ndimage.binary_dilation(np.array(rc)[:,:,3]>0,iterations=7);a=np.array(lay);a[~sil,3]=0;lay=Image.fromarray(a,'RGBA')
        canvas.alpha_composite(lay);out.append(canvas)
    return out
def enraged_sets(S,an,src):
    out={}
    for name in('idle','walk','attack','slam','charge','hurt','roar'):
        frames=S[name];rec=[G.enraged(x) for x in frames]
        # olho vem do quadro original colocado na tela (mesma geometria dos recoloridos)
        hs,he,eps,Ss,DX,DY=G.helmet_params(frames,src)
        for (nm,i),pt in EYE_OVR.items():
            if nm==name:eps[i]=pt
        for i in EYE_NEIGH.get(name,[]):   # olho não detectado direito (ex.: cabeça baixa): usa a média dos vizinhos
            eps[i]=((eps[i-1][0]+eps[i+1][0])/2,(eps[i-1][1]+eps[i+1][1])/2);Ss[i]=(Ss[i-1]+Ss[i+1])/2;DX[i]=(DX[i-1]+DX[i+1])/2;DY[i]=(DY[i-1]+DY[i+1])/2
        out[name]=G.aura(helmet_frames(name,frames,rec,src,hs,he,eps,Ss,DX,DY),(210,30,30))
    dr=[G.enraged(x) for x in S['death']]
    hs,he,eps,Ss,DX,DY=G.helmet_params(S['death'][:3],src)
    dh=helmet_frames('death',S['death'][:3],dr[:3],src,hs,he,eps,Ss,DX,DY)
    out['death']=dh+dr[3:]
    return out
if __name__=='__main__':
    out=sys.argv[1];os.makedirs(out,exist_ok=True);an=cut_grid.main(out);S=base_sets(an);src=an['enrage'][3];E=enraged_sets(S,an,src)
    if '--check' in sys.argv:
        for name,fr in E.items():
            n=len(fr);tw=240;o=Image.new('RGB',(tw*n,200),(52,74,46))
            for i,f in enumerate(fr):
                bg=Image.new('RGBA',f.size,(52,74,46,255));bg.alpha_composite(f);ep=G.eye_point(S[name][i]) or (CW/2,70)
                box=(int(ep[0]-70),int(ep[1]-75),int(ep[0]+50),int(ep[1]+25));o.paste(bg.crop(box).resize((tw,200),Image.NEAREST).convert('RGB'),(i*tw,0))
            o.save(f'{out}/grunk_check_{name}.png')
        print('checks ok')


def export(out_png,out_json,F=.66):
    """grunk_atlas.png (frames reduzidos por F, âncora no chão) + json com as animações do Grunk normal e enfurecido"""
    an=cut_grid.main('/tmp/grunk_tmp');S=base_sets(an);src=an['enrage'][3];E=enraged_sets(S,an,src)
    ch=G.channel(an,10,bg=False)
    W,H=int(CW*F),int(CH*F);frames=[];meta={'w':W,'h':H,'ax':W//2,'ay':int((CH-10)*F),'cols':9,'anims':{}}
    def add(name,fr):
        meta['anims'][name]=[len(frames)+i for i in range(len(fr))]
        for f in fr:frames.append(f.resize((W,H),Image.BOX))
    for k in('idle','walk','attack','slam','charge','roar','hurt','death'):add(k,S[k])
    for k in('idle','walk','attack','slam','charge','roar','hurt','death'):add('e_'+k,E[k])
    add('channel',ch)
    cols=meta['cols'];rows=(len(frames)+cols-1)//cols;A=Image.new('RGBA',(cols*W,rows*H),(0,0,0,0))
    for i,f in enumerate(frames):A.alpha_composite(f,((i%cols)*W,(i//cols)*H))
    A.save(out_png,optimize=True);json.dump(meta,open(out_json,'w'));print('atlas',A.size,len(frames),'quadros')
