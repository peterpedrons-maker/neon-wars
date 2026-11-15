#!/usr/bin/env python3
"""Mede movimentos reais de captura de movimento (BVH) para calibrar o avaliador de animações.
uso: python3 bvh_features.py arquivo1.bvh [arquivo2.bvh ...] > saida.json
Para cada arquivo acha o golpe (pico de velocidade da mão/ponta) e mede: explosão, antecipação, continuação, tempos e peso."""
import sys,json,math
import numpy as np
def parse(path):
    toks=open(path).read().split();i=0;joints=[]
    def nxt():
        nonlocal i;t=toks[i];i+=1;return t
    assert nxt()=='HIERARCHY'
    def body(parent,name,kind):
        assert nxt()=='OFFSET';off=[float(nxt()),float(nxt()),float(nxt())];ch=[]
        if kind!='End':
            assert nxt()=='CHANNELS';n=int(nxt());ch=[nxt() for _ in range(n)]
        idx=len(joints);joints.append(dict(name=name,parent=parent,off=off,ch=ch,end=kind=='End'))
        while True:
            t=nxt()
            if t=='}':break
            if t=='End':nxt();assert nxt()=='{';body(idx,joints[idx]['name']+'_End','End')
            else:
                nm=nxt();assert nxt()=='{';body(idx,nm,'JOINT')
    kind=nxt();assert kind=='ROOT';name=nxt();assert nxt()=='{';body(-1,name,'ROOT')
    assert nxt()=='MOTION';assert nxt()=='Frames:';nf=int(nxt());assert nxt()=='Frame';assert nxt()=='Time:';dt=float(nxt())
    nch=sum(len(j['ch']) for j in joints);data=np.array([float(nxt()) for _ in range(nf*nch)]).reshape(nf,nch)
    return joints,data,dt
def rot(axis,a):
    c,s=math.cos(a),math.sin(a)
    return {'X':np.array([[1,0,0],[0,c,-s],[0,s,c]]),'Y':np.array([[c,0,s],[0,1,0],[-s,0,c]]),'Z':np.array([[c,-s,0],[s,c,0],[0,0,1]])}[axis]
def fk(joints,data):
    nf=len(data);P=np.zeros((nf,len(joints),3))
    for f in range(nf):
        c=0;W=[None]*len(joints);Pos=[None]*len(joints)
        for k,j in enumerate(joints):
            R=np.eye(3);pos=np.array(j['off'],float)
            for ch in j['ch']:
                v=data[f,c];c+=1
                if ch.endswith('position'):pos=pos+np.eye(3)[ 'XYZ'.index(ch[0])]*v if k==0 else pos
                else:R=R@rot(ch[0],math.radians(v))
            if j['parent']<0:
                Wm=R;Pw=pos
                # root position channels substituem o offset
                if any(ch.endswith('position') for ch in j['ch']):
                    Pw=np.array([data[f,j['ch'].index(x)] for x in ('Xposition','Yposition','Zposition')])
            else:
                Wm=W[j['parent']]@R;Pw=Pos[j['parent']]+W[j['parent']]@np.array(j['off'],float)
            W[k]=Wm;Pos[k]=Pw;P[f,k]=Pw
    return P
def find(joints,*keys):
    for k in keys:
        for i,j in enumerate(joints):
            if k.lower() in j['name'].lower():return i
    return None
def features(path):
    joints,data,dt=parse(path);P=fk(joints,data);n=len(P)
    # normaliza pela altura do corpo (cabeça - pé)
    head=find(joints,'head','neck');foot=find(joints,'foot','toe')
    up=int(np.argmax(np.var(P[:,0,:],axis=0)))if False else 1
    H=float(np.median(P[:,head,1]-P[:,foot,1])) if head is not None and foot is not None else 1.0
    H=max(H,1e-6)
    out={'arquivo':path,'quadros':n,'dt':dt,'altura':round(H,2)}
    best=None
    for nm in ('righthand','lefthand','rhand','lhand','hand'):
        for i,j in enumerate(joints):
            if nm in j['name'].lower().replace('_','') and not j['end']:
                v=np.linalg.norm(np.diff(P[:,i,:],axis=0),axis=1)/dt/H
                if best is None or v.max()>best[1].max():best=(j['name'],v,i)
    if best is None:out['erro']='mão não encontrada';return out
    nm,v,i=best;v[:4]=0;pk=int(np.argmax(v));vmax=float(v[pk]);act=v[v>.15*vmax]
    d=P[min(n-1,pk+4),i]-P[max(0,pk-4),i];dn=d/(np.linalg.norm(d)+1e-9)
    def proj(a,b):return float(np.dot(P[a,i]-P[b,i],dn))/H
    back=max([0.0]+[-proj(pk-3,k) for k in range(max(0,pk-int(1.2/dt)),pk-2)] if pk>4 else [0.0])
    over=max([0.0]+[proj(k,min(n-1,pk+3)) for k in range(pk+3,min(n,pk+int(1.2/dt)))]) if pk+4<n else 0.0
    on=pk
    while on>0 and v[on]>.25*vmax:on-=1
    off=pk
    while off<n-1 and v[off]>.25*vmax:off+=1
    hip=find(joints,'hips','hip','pelvis');dip=float(P[:,hip,1].max()-P[:,hip,1].min())/H if hip is not None else 0
    out.update(dict(ponta=nm,pico_vel=round(vmax,2),explosao=round(vmax/float(act.mean()),2),antecipacao_altura=round(back,2),continuacao_altura=round(over,2),
      t_subida=round((pk-on)*dt,2),t_descida=round((off-pk)*dt,2),t_pico=round(pk*dt,2),duracao=round(n*dt,2),variacao_quadril=round(dip,2)))
    return out
if __name__=='__main__':
    res=[]
    for p in sys.argv[1:]:
        try:res.append(features(p))
        except Exception as e:res.append({'arquivo':p,'erro':str(e)})
    print(json.dumps(res,indent=1,ensure_ascii=False))
