"""Etapa 3 (Blender): esqueleto e pesos por distância sobre a malha do casco; poses do motor pxengine -> skinning linear; renderiza os quadros."""
import sys,os,json,math,time
import numpy as np,bpy,cv2
HERE=os.path.dirname(os.path.abspath(__file__));sys.path.insert(0,HERE);sys.path.insert(0,os.path.join(HERE,'..','blendgob'));sys.path.insert(0,os.path.join(HERE,'..'))
from scene import reset,set_view,render
from view import load_mesh,paint_mat,S as SC
from pxengine.animation import build
R3=lambda a:np.radians(a)
def rx(theta,about):
    c,s=math.cos(theta),math.sin(theta);M=np.eye(4);M[1,1]=c;M[1,2]=-s;M[2,1]=s;M[2,2]=c
    T1=np.eye(4);T1[:3,3]=about;T0=np.eye(4);T0[:3,3]=-np.array(about);return T1@M@T0
def trans(v):M=np.eye(4);M[:3,3]=v;return M
class Rig:
    def __init__(s,npz):
        d=np.load(npz);s.d=d;s.V=d['verts'].astype(np.float64);s.vox=float(d['vox']);s.YC=d['yc'];s.meta=json.loads(str(d['meta']))
        yc=lambda z:float(s.YC[min(len(s.YC)-1,max(0,int(z/s.vox)))])
        J={}
        for sg,nm in((1,'R'),(-1,'L')):
            J['hip'+nm]=(sg*42,yc(257),257);J['knee'+nm]=(sg*79,yc(137),137);J['ank'+nm]=(sg*79,yc(52),52);J['toe'+nm]=(sg*79,yc(20)+75,22)
            J['sh'+nm]=(sg*113,yc(485),485);J['el'+nm]=(sg*146,yc(362),362);J['wr'+nm]=(sg*163,yc(237),237);J['hand'+nm]=(sg*165,yc(175),172)
        J['pelvis']=(0,yc(245),245);J['neck']=(0,yc(525),525);J['headtop']=(0,yc(680),690)
        s.J={k:np.array(v,float) for k,v in J.items()}
        B=[('spine','pelvis','neck',125),('head','neck','headtop',95)]
        for nm in('R','L'):B+=[('uarm'+nm,'sh'+nm,'el'+nm,42),('farm'+nm,'el'+nm,'wr'+nm,38),('hand'+nm,'wr'+nm,'hand'+nm,34),('thigh'+nm,'hip'+nm,'knee'+nm,60),('shin'+nm,'knee'+nm,'ank'+nm,50),('foot'+nm,'ank'+nm,'toe'+nm,50)]
        s.B=B;s.names=[b[0] for b in B];s.weights()
        s.setup_weapon()
    def weights(s):
        P=s.V;n=len(P);W=np.zeros((n,len(s.B)),np.float32)
        for i,(nm,a,b,r) in enumerate(s.B):
            A=s.J[a];Bp=s.J[b];AB=Bp-A;t=np.clip(((P-A)@AB)/(AB@AB),0,1);C=A+t[:,None]*AB;dd=np.linalg.norm(P-C,axis=1);W[:,i]=np.exp(-(dd/r)**2)
        # braço só pega vértices do lado dele; evita vazar para a barriga
        for i,(nm,a,b,r) in enumerate(s.B):
            if nm.endswith('R') and nm[:-1] in('uarm','farm','hand'):W[P[:,0]<10,i]*=.02
            if nm.endswith('L') and nm[:-1] in('uarm','farm','hand'):W[P[:,0]>-10,i]*=.02
            if nm.endswith('R') and nm[:-1] in('thigh','shin','foot'):W[P[:,0]<-4,i]*=.02
            if nm.endswith('L') and nm[:-1] in('thigh','shin','foot'):W[P[:,0]>4,i]*=.02
        W=W**3
        s_=W.sum(1,keepdims=True);W=np.where(s_>1e-6,W/np.maximum(s_,1e-9),0);bad=(s_[:,0]<1e-6)
        if bad.any():W[bad,0]=1
        # mantém os 4 maiores pesos
        idx=np.argsort(-W,1)[:,4:];np.put_along_axis(W,idx,0,1);W/=W.sum(1,keepdims=True);s.W=W
    def setup_weapon(s):
        d=s.d;wm=d['weapon_mask'].astype(np.uint8);img=d['side_img'];ys_ref=s.meta['ys_ref'];ybs=s.meta['ybs']
        cnts,_=cv2.findContours(wm,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE);c=max(cnts,key=cv2.contourArea)[:,0,:].astype(float)
        eps=1.5;c=cv2.approxPolyDP(c.astype(np.float32).reshape(-1,1,2),eps,True)[:,0,:]
        gcol,grow=565,555;s.wpoly=np.stack([c[:,0]-gcol,grow-c[:,1]],1)    # (y_local, z_local)
        s.wuv=np.stack([c[:,0]/img.shape[1],1-c[:,1]/img.shape[0]],1);s.wimg=img
        s.grip=(s.J['wrR']+np.array([0,0,-22]))
    def pose(s,P):
        g=P.get;K=15.0;J=s.J
        root=trans(np.array([0,g('sway',0)*K*.6+g('fwd',0)*K,(g('bob',0)-g('crouch',0)*1.2)*K]))
        lean=-g('lean',0)*1.0;Msp=root@rx(R3(lean),J['pelvis'])
        Mh=Msp@rx(R3(g('open',0)*8+g('hy',0)*-2),J['neck'])
        M={'spine':Msp,'head':Mh}
        for sg,nm in((1,'R'),(-1,'L')):
            us,fe=(g('us',8),g('fe',12)) if nm=='R' else (g('ls',-8),g('le',-12))
            Mu=Msp@rx(R3(us),J['sh'+nm]);Mf=Mu@rx(R3(fe),J['el'+nm]);Mhand=Mf
            M['uarm'+nm]=Mu;M['farm'+nm]=Mf;M['hand'+nm]=Mhand
            a,k=(g('ra',0),g('rk',0)) if nm=='R' else (g('la',0),g('lk',0))
            Mt=root@rx(R3(a),J['hip'+nm]);Ms=Mt@rx(R3(-k),J['knee'+nm]);Mfo=Ms@rx(R3(-(a-k)*.7),J['ank'+nm])
            M['thigh'+nm]=Mt;M['shin'+nm]=Ms;M['foot'+nm]=Mfo
        s.M=M;V=np.concatenate([s.V,np.ones((len(s.V),1))],1);out=np.zeros((len(V),3))
        for i,nm in enumerate(s.names):
            w=s.W[:,i]
            if not w.any():continue
            sel=w>0;out[sel]+=w[sel,None]*(V[sel]@M[nm].T)[:,:3]
        return out
    def weapon_world(s,P):
        g=P.get;Mh=s.M['handR'];grip=(Mh@np.append(s.grip,1))[:3]
        th=-(g('weapon',22)-11)
        R=rx(R3(th),grip);pts=[]
        n=len(s.wpoly);thick=9.0
        verts=[]
        for sgn in(-1,1):
            for (yl,zl) in s.wpoly:
                ya=math.radians(32);xl=sgn*thick;x2=xl*math.cos(ya)-yl*math.sin(ya);y2=xl*math.sin(ya)+yl*math.cos(ya)
                verts.append((grip[0]+x2,grip[1]+y2,grip[2]+zl))
        V=np.array(verts);V4=np.concatenate([V,np.ones((len(V),1))],1);return (V4@R.T)[:,:3]
def make_weapon(rig):
    import bmesh
    n=len(rig.wpoly);bm=bmesh.new();vs=[]
    for sgn in(-1,1):
        for (yl,zl) in rig.wpoly:vs.append(bm.verts.new((sgn*9*SC,yl*SC,zl*SC)))
    f1=bm.faces.new(vs[:n][::-1]);f2=bm.faces.new(vs[n:])
    for i in range(n):bm.faces.new((vs[i],vs[(i+1)%n],vs[n+(i+1)%n],vs[n+i]))
    me=bpy.data.meshes.new('weap');bm.to_mesh(me);bm.free()
    bm2=bmesh.new();bm2.from_mesh(me);bmesh.ops.triangulate(bm2,faces=bm2.faces[:]);uv=bm2.loops.layers.uv.new('uv')
    for fc in bm2.faces:
        for l in fc.loops:
            vi=l.vert.index;l[uv].uv=tuple(rig.wuv[vi%n])
    bm2.to_mesh(me);bm2.free()
    for p in me.polygons:p.use_smooth=False
    img=rig.wimg;pth='/tmp/ref/side_tex.png';cv2.imwrite(pth,cv2.cvtColor(img,cv2.COLOR_RGB2BGR))
    m=bpy.data.materials.new('wm');m.use_nodes=True;t=m.node_tree;b=t.nodes['Principled BSDF'];tx=t.nodes.new('ShaderNodeTexImage');tx.image=bpy.data.images.load(pth);tx.image.colorspace_settings.name='sRGB'
    t.links.new(tx.outputs['Color'],b.inputs['Base Color']);t.links.new(tx.outputs['Color'],b.inputs['Emission Color']);b.inputs['Emission Strength'].default_value=.55;b.inputs['Roughness'].default_value=.5
    me.materials.append(m);o=bpy.data.objects.new('weap',me);bpy.context.scene.collection.objects.link(o);return o
def run(npz,out,anims,views,res=384,samples=16,only=None):
    os.makedirs(out,exist_ok=True)
    co=reset(res,samples);co.data.ortho_scale=1.75
    rig=Rig(npz);o,_=load_mesh(npz);o.data.materials.append(paint_mat());wo=make_weapon(rig);meta={}
    for an in anims:
        poses,ms,ev,loop=build(an);meta[an]=dict(frames=len(poses),ms=ms,events={str(k):v for k,v in ev.items()},loop=loop)
        idx=range(len(poses)) if only is None else only
        for v in views:
            set_view(co,v,target=(0,0,.62))
            for i in idx:
                t=time.time();P=poses[i];V=rig.pose(P)
                o.data.vertices.foreach_set('co',(V*SC).astype(np.float32).reshape(-1));o.data.update()
                W=rig.weapon_world(P)*SC;wo.data.vertices.foreach_set('co',W.astype(np.float32).reshape(-1));wo.data.update()
                render(f'{out}/{an}_{v}_{i:02d}.png');print(an,v,i,round(time.time()-t,1),flush=True)
    json.dump(meta,open(f'{out}/meta.json','w'),indent=1)
if __name__=='__main__':
    npz,out,anims,views=sys.argv[1:5];only=[int(x) for x in sys.argv[5].split(',')] if len(sys.argv)>5 else None
    run(npz,out,anims.split(','),views.split(','),only=only)
