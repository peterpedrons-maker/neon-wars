"""Validation System: confere alinhamento, tamanho, arma, limites, saltos entre quadros, transparência, paleta e iluminação dos spritesheets."""
import numpy as np
from skimage.metrics import structural_similarity as ssim
from .renderer import MD,RAMP,MATS,OUTL,INK,MID
def allowed_colors():
    S={tuple(int(x) for x in INK)}
    for m in range(len(MATS)):
        for t in range(4):S.add(tuple(int(x) for x in RAMP[m,t]))
        if m<len(MATS)-1:
            o=OUTL[m];S.add(tuple(int(v) for v in (INK*(1-o)+RAMP[m,0].astype(float)*o*.55).astype(np.uint8)))
    return S
ALLOWED=allowed_colors()
def gray(f):
    a=f.rgba;g=np.full(a.shape[:2],128.,float);m=a[:,:,3]>0;g[m]=a[m,:3].mean(1);return g
def validate(char,anims):
    issues=[];I=lambda lvl,an,v,i,msg:issues.append(dict(level=lvl,anim=an,view=v,frame=i,msg=msg))
    GY=char.GY;idle=next((A for A in anims if A['name']=='idle'),None)
    ref_h=None
    if idle:
        hs=[np.where(f.a.any(1))[0] for f in idle['views']['front']];ref_h=np.median([h.max()-h.min()+1 for h in hs])
    for A in anims:
        an=A['name']
        for v,fr in A['views'].items():
            prev=None;wc=[]
            for i,f in enumerate(fr):
                a=f.rgba;lying=an=='death' and i>=A['n']//2
                al=np.unique(a[:,:,3])
                if not set(al.tolist())<={0,255}:I('error',an,v,i,'transparência parcial (alpha fora de 0/255)')
                if (a[0,:,3]>0).any() or (a[-1,:,3]>0).any() or (a[:,0,3]>0).any() or (a[:,-1,3]>0).any():I('error',an,v,i,'pixels tocando a borda do quadro (corte)')
                op=a[:,:,3]>0;cols={tuple(c) for c in a[op][:,:3].tolist()};bad=cols-ALLOWED
                if bad:I('warn',an,v,i,f'{len(bad)} cor(es) fora da paleta: {sorted(bad)[:3]}')
                ys=np.where(op.any(1))[0]
                if not lying and an not in('dodge','run') and not (GY-2<=ys.max()<=GY+2):I('warn',an,v,i,f'pés fora da linha do chão (y={ys.max()}, esperado {GY-2}..{GY+2})')
                body=f.a&~f.wm;by=np.where(body.any(1))[0]
                if ref_h and not lying and an not in('dodge') and len(by):
                    h=by.max()-by.min()+1
                    if abs(h-ref_h)/ref_h>.28:I('warn',an,v,i,f'altura do corpo {h}px difere do idle ({ref_h:.0f}px)')
                wc.append(int(f.wm.sum()))
                g=gray(f)
                if prev is not None:
                    s=ssim(prev,g,data_range=255)
                    if s<.30 and not lying:I('warn',an,v,i,f'salto visual entre quadros (SSIM {s:.2f})')
                    c0=np.array(np.nonzero(prev_mask)).mean(1);c1=np.array(np.nonzero(op)).mean(1)
                    if np.hypot(*(c1-c0))>(12 if an in('dodge','death') else 8):I('warn',an,v,i,f'centro de massa saltou {np.hypot(*(c1-c0)):.1f}px')
                prev=g;prev_mask=op
            if wc and not (an=='death'):
                if min(wc)<8:I('error',an,v,wc.index(min(wc)),f'arma some (só {min(wc)} px)')
                for i in range(1,len(wc)):
                    if wc[i-1] and (wc[i]/wc[i-1]>3.2 or wc[i]/wc[i-1]<.3):I('warn',an,v,i,f'arma muda de tamanho de {wc[i-1]} para {wc[i]} px')
            if A['loop'] and len(fr)>2:
                s=ssim(gray(fr[-1]),gray(fr[0]),data_range=255)
                if s<.5:I('warn',an,v,len(fr)-1,f'emenda do loop (SSIM último→primeiro {s:.2f})')
    # consistência entre vistas e luz
    if idle:
        h=lambda v:(lambda ys:ys.max()-ys.min()+1)(np.where(idle['views'][v][0].a.any(1))[0])
        hs={v:h(v) for v in('side','front','back')}
        if max(hs.values())-min(hs.values())>3:I('warn','idle','*',0,f'alturas diferentes entre vistas: {hs}')
        f=idle['views']['front'][0];a=f.rgba;lum=a[:,:,:3].mean(2);op=(a[:,:,3]>0)&~f.wm;xs=np.where(op.any(0))[0];mid=(xs.min()+xs.max())//2
        L=lum[:,:mid][op[:,:mid]].mean();R=lum[:,mid:][op[:,mid:]].mean()
        if L<R-3:I('warn','idle','front',0,f'luz parece vir da direita (lado esquerdo {L:.0f} < direito {R:.0f})')
    return issues
def report(issues):
    from collections import Counter
    c=Counter(i['level'] for i in issues);lines=[f"validação: {c.get('error',0)} erro(s), {c.get('warn',0)} aviso(s)"]
    seen=Counter()
    for i in issues:
        key=(i['level'],i['anim'],i['msg'].split('(')[0][:40]);seen[key]+=1
        if seen[key]<=2:lines.append(f"  {i['level']:5} {i['anim']}/{i['view']}/{i['frame']}: {i['msg']}")
    return '\n'.join(lines)
