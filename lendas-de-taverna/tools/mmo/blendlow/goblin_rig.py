"""Goblin low-poly com esqueleto de articulações (pivôs): ombro, cotovelo, pulso, dedos, quadril, joelho, tornozelo, dedos do pé, coluna, pescoço e orelhas.
Uso: /tmp/bpyenv/bin/python goblin_rig.py <idle|walk|attack|hurt|rest> <pasta_saida> [largura altura amostras]"""
import bpy,bmesh,math,random,sys,os
from mathutils import Vector,Matrix
ANIM=sys.argv[1] if len(sys.argv)>1 else 'rest';OUT=sys.argv[2] if len(sys.argv)>2 else '/tmp/gob_rig'
W=int(sys.argv[3]) if len(sys.argv)>3 else 480;H=int(sys.argv[4]) if len(sys.argv)>4 else 540;SM=int(sys.argv[5]) if len(sys.argv)>5 else 20
random.seed(7)
bpy.ops.wm.read_factory_settings(use_empty=True)
sc=bpy.context.scene
def lin(c):return tuple((x/255.0)**2.2 for x in c)
def mat(name,c,rough=.55,spec=.25,metal=0):
    m=bpy.data.materials.new(name);m.use_nodes=True;b=m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value=(*lin(c),1);b.inputs['Roughness'].default_value=rough;b.inputs['Metallic'].default_value=metal
    for k in('Specular IOR Level','Specular'):
        if k in b.inputs:b.inputs[k].default_value=spec
    return m
M=dict(green=mat('green',(120,168,44)),green2=mat('green2',(86,128,32)),ear=mat('ear',(150,98,58)),leather=mat('leather',(128,82,48)),cloth=mat('cloth',(118,74,44)),
  club=mat('club',(160,92,54)),metal=mat('metal',(78,80,92),.35,.5,.6),tan=mat('tan',(218,188,132)),nail=mat('nail',(206,190,140)),tusk=mat('tusk',(242,228,194)),
  eye=mat('eye',(252,192,18),.3,.4),pup=mat('pup',(14,14,16),.4),rim=mat('rim',(60,92,20)))
def finish(o,m,flat=True):
    o.data.materials.append(m)
    for p in o.data.polygons:p.use_smooth=not flat
    return o
def obj_from_bm(bm,name):
    me=bpy.data.meshes.new(name);bm.to_mesh(me);bm.free();o=bpy.data.objects.new(name,me);sc.collection.objects.link(o);return o
def blob(c,s,m,sub=2,noise=.05,rot=(0,0,0),seed=None):
    bm=bmesh.new();bmesh.ops.create_icosphere(bm,subdivisions=sub,radius=1.0)
    rnd=random.Random(seed if seed is not None else random.random())
    for v in bm.verts:v.co=Vector((v.co.x*s[0],v.co.y*s[1],v.co.z*s[2]))*(1+rnd.uniform(-noise,noise))
    R=Matrix.Rotation(rot[2],4,'Z')@Matrix.Rotation(rot[1],4,'Y')@Matrix.Rotation(rot[0],4,'X')
    bmesh.ops.transform(bm,matrix=Matrix.Translation(c)@R,verts=bm.verts)
    return finish(obj_from_bm(bm,'blob'),m)
def limb(p0,p1,r0,r1,m,seg=7,cap=True):
    p0,p1=Vector(p0),Vector(p1);d=p1-p0;L=d.length
    bm=bmesh.new();bmesh.ops.create_cone(bm,cap_ends=cap,cap_tris=False,segments=seg,radius1=r0,radius2=r1,depth=L)
    q=Vector((0,0,1)).rotation_difference(d.normalized()).to_matrix().to_4x4()
    bmesh.ops.transform(bm,matrix=Matrix.Translation((p0+p1)/2)@q,verts=bm.verts)
    return finish(obj_from_bm(bm,'limb'),m)
def ring(c,r,h,m,seg=8,rot=(0,0,0)):
    bm=bmesh.new();bmesh.ops.create_cone(bm,cap_ends=False,segments=seg,radius1=r,radius2=r,depth=h)
    # fecha como anel grosso: duplica menor
    bmesh.ops.create_cone(bm,cap_ends=False,segments=seg,radius1=r*.82,radius2=r*.82,depth=h)
    R=Matrix.Rotation(rot[2],4,'Z')@Matrix.Rotation(rot[1],4,'Y')@Matrix.Rotation(rot[0],4,'X')
    bmesh.ops.transform(bm,matrix=Matrix.Translation(c)@R,verts=bm.verts)
    o=obj_from_bm(bm,'ring');
    # tampas simples: sólido via solidify
    sol=o.modifiers.new('s','SOLIDIFY');sol.thickness=r*.18;sol.offset=0
    return finish(o,m)
def prism(pts,thick,m,y0=0.0):
    """polígono convexo no plano XZ extrudado ao longo de -Y"""
    bm=bmesh.new();f=[bm.verts.new((x,y0,z)) for x,z in pts];b=[bm.verts.new((x,y0+thick,z)) for x,z in pts]
    bm.faces.new(f[::-1]);bm.faces.new(b)
    n=len(pts)
    for i in range(n):bm.faces.new((f[i],f[(i+1)%n],b[(i+1)%n],b[i]))
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
    return obj_from_bm(bm,'prism')
def mirror_x(o):
    o.scale.x*=-1
def tri_pyr(c,s,m,rot=(0,0,0),seg=4):
    bm=bmesh.new();bmesh.ops.create_cone(bm,cap_ends=True,cap_tris=False,segments=seg,radius1=s[0],radius2=0.0,depth=s[1])
    R=Matrix.Rotation(rot[2],4,'Z')@Matrix.Rotation(rot[1],4,'Y')@Matrix.Rotation(rot[0],4,'X')
    bmesh.ops.transform(bm,matrix=Matrix.Translation(c)@R,verts=bm.verts)
    return finish(obj_from_bm(bm,'pyr'),m)


def spike(base,d,L,r,m,seg=5):
    b=Vector(base);d=Vector(d).normalized();return limb(b,b+d*L,r,0.0,m,seg=seg,cap=True)
def parent_to(empty,objs):
    for o in objs:
        o.parent=empty;o.matrix_parent_inverse=empty.matrix_world.inverted()
def finger(p0,p1,p2,r,m,seg=6):
    p0,p1,p2=Vector(p0),Vector(p1),Vector(p2)
    limb(p0,p1,r,r*.92,m,seg=seg);blob(p1,(r*1.02,)*3,m,sub=1,noise=.03)
    limb(p1,p2,r*.92,r*.80,m,seg=seg);blob(p2,(r*.84,)*3,m,sub=1,noise=.03)
def mark(n0):return len(bpy.data.objects)
G=M['green'];D=M['green2']
def newobjs(since):return list(bpy.data.objects)[since:]
G=M['green'];D=M['green2']
# ---------------- articulações (pivôs) ----------------
JT={}
def J(name,pos,parent=None):
    e=bpy.data.objects.new(name,None);e.empty_display_size=.04;sc.collection.objects.link(e);e.location=pos;JT[name]=[e,Vector(pos),parent];return e
class grp:
    def __init__(s,j):s.j=j
    def __enter__(s):s.b=set(bpy.data.objects.keys())
    def __exit__(s,*a):
        e,p,_=JT[s.j]
        for o in list(bpy.data.objects):
            if o.name not in s.b and o.type=='MESH' and o.parent is None:o.parent=e;o.matrix_parent_inverse=Matrix.Translation(-p)
J('root',(0,0,0));J('hips',(0,0,.74),'root');J('spine',(0,0,.95),'hips');J('chest',(0,0,1.22),'spine');J('neck',(0,-.04,1.70),'chest')
J('earL',(.60,.04,1.86),'neck');J('earR',(-.60,.04,1.86),'neck')
J('shL',(.62,0,1.50),'chest');J('elL',(.80,-.08,1.16),'shL');J('wrL',(.84,-.27,.93),'elL')
J('shR',(-.62,0,1.50),'chest');J('elR',(-.84,-.18,1.24),'shR');J('wrR',(-.77,-.44,1.08),'elR');J('club',(-.745,-.50,.98),'wrR')
FL=[(-.09,.98),(.03,1.04),(.14,.94)]
for i,(dx,l) in enumerate(FL):
    J(f'fL{i}a',(.86+dx,-.38,.70),'wrL');J(f'fL{i}b',(.86+dx*1.15,-.44,.52*l+.06),f'fL{i}a')
J('tL_a',(.69,-.34,.78),'wrL');J('tL_b',(.64,-.43,.66),'tL_a')
for n,sx in(('L',1),('R',-1)):
    J('th'+n,(sx*.27,0,.62),'hips');J('kn'+n,(sx*.31,-.10,.40),'th'+n);J('an'+n,(sx*.32,-.16,.22),'kn'+n);J('to'+n,(sx*.34,-.46,.12),'an'+n)
for n,j in JT.items():
    e,p,par=j
    if par:
        pe,pp,_=JT[par];e.parent=pe;e.matrix_parent_inverse=Matrix.Translation(-pp)
# ---------------- peças ----------------
with grp('hips'):
    blob((0,.04,.78),(.42,.36,.20),G,sub=1,noise=.04,seed=13)
    bm=bmesh.new();N=15;zt=.86
    top=[bm.verts.new((math.cos(a)*.47,math.sin(a)*.42,zt)) for a in [i*2*math.pi/N for i in range(N)]]
    bot=[]
    for i in range(N):
        a=i*2*math.pi/N;ab=a+math.pi/N;f=(1.0 if math.sin(a)<0.2 else .6)
        bot.append(bm.verts.new((math.cos(a)*.56,math.sin(a)*.51,zt-.12)))
        bot.append(bm.verts.new((math.cos(ab)*.60,math.sin(ab)*.54,zt-.40*f-random.uniform(0,.07))))
    for i in range(N):bm.faces.new((top[i],top[(i+1)%N],bot[(2*i+2)%(2*N)],bot[2*i+1],bot[2*i]))
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
    sk=obj_from_bm(bm,'skirt');sl=sk.modifiers.new('s','SOLIDIFY');sl.thickness=.035;finish(sk,M['cloth'])
with grp('spine'):
    blob((0,-.03,1.02),(.46,.40,.36),G,sub=2,noise=.05,seed=12)
    limb((-.52,-.36,.90),(.52,-.36,.90),.07,.07,M['leather'],seg=4)
with grp('chest'):
    blob((0,.02,1.30),(.54,.42,.46),G,sub=2,noise=.05,seed=11)
    limb((.40,-.30,1.70),(-.38,-.44,.94),.09,.09,M['leather'],seg=4)
    blob((.03,-.545,1.30),(.19,.04,.19),M['metal'],sub=0,noise=0,rot=(0,math.radians(45),0))
    blob((.03,-.565,1.30),(.095,.04,.095),M['leather'],sub=0,noise=0,rot=(0,math.radians(45),0))
# pernas
for n,sx in(('L',1),('R',-1)):
    with grp('th'+n):
        blob((sx*.27,0,.62),(.25,.24,.22),G,sub=2,noise=.05,seed=40+sx);limb((sx*.27,0,.62),(sx*.31,-.10,.40),.21,.17,G,seg=7)
    with grp('kn'+n):
        blob((sx*.31,-.10,.40),(.18,.17,.16),G,sub=1,noise=.04,seed=50+sx);limb((sx*.31,-.10,.40),(sx*.32,-.16,.20),.17,.15,G,seg=7)
        ring((sx*.32,-.15,.26),.19,.11,M['tan'],seg=8,rot=(math.radians(-10),0,0))
    with grp('an'+n):
        blob((sx*.33,-.18,.13),(.27,.36,.12),G,sub=2,noise=.04,rot=(0,0,sx*.08),seed=60+sx)
        blob((sx*.31,.00,.15),(.20,.18,.14),G,sub=1,noise=.04,seed=62+sx);blob((sx*.34,-.40,.15),(.25,.22,.12),G,sub=1,noise=.04,seed=64+sx)
    with grp('to'+n):
        for k,off in enumerate((-.19,0,.19)):
            a=off*1.2*sx;tx=sx*.34+off;ty=-.58-(.03 if k==1 else 0)
            blob((tx,ty,.125),(.125,.19,.11),G,sub=1,noise=.03,rot=(0,0,a*.5),seed=70+k+sx)
            blob((tx+a*.05,ty-.14,.115),(.11,.09,.10),G,sub=1,noise=.03)
            blob((tx+a*.07,ty-.19,.17),(.095,.10,.035),M['nail'],sub=1,noise=.02,rot=(-.35,0,a*.5))
# braço esquerdo (pendurado)
with grp('shL'):
    blob((.62,0,1.50),(.27,.26,.26),G,sub=2,noise=.05,seed=71);limb((.62,0,1.50),(.80,-.08,1.16),.21,.16,G,seg=7)
with grp('elL'):
    blob((.80,-.08,1.16),(.16,.15,.15),G,sub=1,noise=.04,seed=72);limb((.80,-.08,1.16),(.84,-.28,.90),.16,.14,G,seg=7)
    ring((.84,-.27,.93),.17,.10,M['tan'],seg=8,rot=(math.radians(-24),0,0))
with grp('wrL'):blob((.86,-.36,.78),(.20,.12,.19),G,sub=2,noise=.04,seed=73)
for i,(dx,l) in enumerate(FL):
    p0=(.86+dx,-.38,.70);p1=(.86+dx*1.15,-.44,.52*l+.06);p2=(.86+dx*1.2,-.56,.36*l+.12)
    with grp(f'fL{i}a'):limb(p0,p1,.075,.069,G,seg=6);blob(p1,(.077,)*3,G,sub=1,noise=.03)
    with grp(f'fL{i}b'):limb(p1,p2,.069,.06,G,seg=6);blob(p2,(.063,)*3,G,sub=1,noise=.03)
with grp('tL_a'):limb((.69,-.34,.78),(.64,-.43,.66),.07,.064,G,seg=6);blob((.64,-.43,.66),(.072,)*3,G,sub=1,noise=.03)
with grp('tL_b'):limb((.64,-.43,.66),(.66,-.54,.58),.064,.056,G,seg=6);blob((.66,-.54,.58),(.059,)*3,G,sub=1,noise=.03)
# braço direito (clava)
with grp('shR'):
    blob((-.62,0,1.50),(.27,.26,.26),G,sub=2,noise=.05,seed=81);limb((-.62,0,1.50),(-.84,-.18,1.24),.21,.16,G,seg=7)
with grp('elR'):
    blob((-.84,-.18,1.24),(.16,.15,.15),G,sub=1,noise=.04,seed=82);limb((-.84,-.18,1.24),(-.76,-.46,1.06),.16,.14,G,seg=7)
    ring((-.77,-.44,1.08),.17,.10,M['tan'],seg=8,rot=(math.radians(-60),0,0))
with grp('wrR'):
    blob((-.76,-.50,1.06),(.20,.14,.20),G,sub=2,noise=.04,seed=83)
    for z in (1.20,1.11,1.02,.93):finger((-.62,-.52,z),(-.70,-.70,z-.005),(-.90,-.62,z-.01),.07,G)
    finger((-.62,-.62,1.28),(-.74,-.70,1.28),(-.86,-.68,1.22),.07,G)
with grp('club'):
    # cabo facetado com enrolado de couro, anel de ferro com rebites, cabeça nodosa e espinhos
    cx=lambda z:(-.72-(z-.70)*.057,-.50,z)     # eixo levemente inclinado
    limb(cx(.52),cx(1.02),.085,.105,M['club'],seg=7)                   # cabo
    limb(cx(1.02),cx(1.58),.105,.185,M['club'],seg=7)                  # cabo alargando
    for z in (.62,.78,.94,1.10):ring(cx(z),.115 if z<1 else .135,.07,M['leather'],seg=7)     # enrolado de couro
    ring(cx(1.28),.20,.09,M['metal'],seg=8);ring(cx(1.46),.215,.08,M['metal'],seg=8)             # anéis de ferro
    blob(cx(.50),(.12,.12,.08),M['leather'],sub=1,noise=.03,seed=91)                              # pomo
    blob((-.79,-.50,1.74),(.27,.26,.30),M['club'],sub=2,noise=.07,seed=5)                       # cabeça
    blob((-.79,-.50,1.92),(.17,.17,.12),M['club'],sub=1,noise=.08,seed=6)
    for d in((-1,0,.2),(.9,.1,.25),(-.2,-.9,.3),(-.3,.9,.2),(0,0,1),(-.9,-.5,-.3),(.8,-.6,-.1),(.1,-.7,-.7),(-.7,.6,-.2),(.6,.7,.1)):
        dv=Vector(d).normalized();c=Vector((-.79,-.50,1.74))+Vector((dv.x*.22,dv.y*.22,dv.z*.26));spike(c,dv,.30,.08,M['metal'],seg=5)
    for k in range(5):                                                                              # rebites no anel
        a=k*1.256;blob((-.79+math.cos(a)*.215,-.50+math.sin(a)*.215,1.46),(.035,.035,.035),M['tan'],sub=0,noise=0)
# cabeça
with grp('neck'):
    blob((0,-.06,2.00),(.70,.62,.56),G,sub=2,noise=.04,seed=21);blob((0,-.28,1.72),(.50,.38,.32),G,sub=2,noise=.04,seed=22)
    for sx in(1,-1):
        blob((sx*.43,-.36,1.84),(.25,.21,.22),G,sub=1,noise=.04,seed=23+sx)
        blob((sx*.29,-.55,2.17),(.32,.15,.095),D,sub=1,noise=.03,rot=(0,sx*(-.38),sx*(.26)))
        blob((sx*.28,-.54,1.99),(.25,.07,.24),M['rim'],sub=2,noise=0);blob((sx*.28,-.585,1.99),(.20,.06,.21),M['eye'],sub=2,noise=0)
        blob((sx*.255,-.635,1.98),(.095,.04,.105),M['pup'],sub=2,noise=0)
        spike((sx*.31,-.60,1.54),(sx*.08,-.30,1.0),.21,.06,M['tusk'],seg=5)
    blob((0,-.60,1.57),(.34,.12,.08),D,sub=1,noise=.03);blob((0,-.66,1.60),(.26,.10,.10),G,sub=1,noise=.03)
    spike((0,-.50,1.92),(0,-1,-.25),.40,.17,G,seg=4);blob((0,-.55,2.03),(.12,.10,.10),G,sub=1,noise=.03)
for sx,n in((1,'L'),(-1,'R')):
    ptsO=[(0,-.24),(0,.28),(.45,.52),(.95,.78),(1.42,1.12),(1.02,.66),(.62,.14),(.28,-.16)]
    ptsI=[(.10,-.12),(.10,.18),(.46,.42),(.90,.68),(1.20,.96),(.92,.58),(.58,.14),(.32,-.04)]
    with grp('ear'+n):
        o=prism(ptsO,.16,G,y0=0);finish(o,G);oi=prism(ptsI,.05,M['ear'],y0=-.03);finish(oi,M['ear'])
        for ob in(o,oi):
            ob.data.transform(Matrix.Rotation(math.radians(-8),4,'Y'));ob.data.transform(Matrix.Rotation(math.radians(6),4,'Z'));ob.data.transform(Matrix.Translation((.60,.04,1.86)))
            if sx<0:
                ob.data.transform(Matrix.Scale(-1,4,(1,0,0)));ob.data.flip_normals()
# ---------------- cena ----------------
sc.render.engine='CYCLES';sc.cycles.device='CPU';sc.cycles.samples=SM;sc.cycles.use_denoising=True;sc.render.film_transparent=bool(os.environ.get('LAYERS') or os.environ.get('TRANSP'))
sc.render.resolution_x=W;sc.render.resolution_y=H;sc.render.image_settings.file_format='PNG';sc.view_settings.view_transform='Standard'
cam=bpy.data.cameras.new('c');cam.lens=70;co=bpy.data.objects.new('c',cam);sc.collection.objects.link(co);sc.camera=co
tgt=Vector((-0.25,-.05,1.45));pos=Vector((-5.0,-7.4,3.0))
if os.environ.get('CAM'):
    _c=[float(x) for x in os.environ['CAM'].split(',')];pos=Vector(_c[:3]);tgt=Vector(_c[3:6]);co.location=pos;co.rotation_euler=(tgt-pos).to_track_quat('-Z','Y').to_euler()
def area(loc,e,size,col):
    l=bpy.data.lights.new('a','AREA');l.energy=e;l.size=size;l.color=col;o=bpy.data.objects.new('a',l);sc.collection.objects.link(o);o.location=loc;o.rotation_euler=(tgt-Vector(loc)).to_track_quat('-Z','Y').to_euler()
area((-3.5,-4.5,5.5),520,3.2,(1,.95,.88));area((4.5,3.5,3.5),380,4,(.65,.75,1));area((4.5,-4,1.2),60,4,(1,.9,.8))
# chão (sombra suave) para dar apoio nos pés
bpy.ops.mesh.primitive_circle_add(vertices=48,radius=1.6,fill_type='NGON',location=(0,-.1,0));gd=bpy.context.object
if os.environ.get('NOGROUND'):gd.hide_render=True
gm=bpy.data.materials.new('gd');gm.use_nodes=True;b=gm.node_tree.nodes['Principled BSDF'];b.inputs['Base Color'].default_value=(*lin((40,44,52)),1);b.inputs['Roughness'].default_value=.9;gd.data.materials.append(gm)
w=bpy.data.worlds.new('w');sc.world=w;w.use_nodes=True;nt=w.node_tree;N=nt.nodes;Lk=nt.links
tc=N.new('ShaderNodeTexCoord');sp=N.new('ShaderNodeSeparateXYZ');cr=N.new('ShaderNodeValToRGB');bg=N['Background']
cr.color_ramp.elements[0].position=0.0;cr.color_ramp.elements[0].color=(*lin((54,58,66)),1);cr.color_ramp.elements[1].position=1.0;cr.color_ramp.elements[1].color=(*lin((10,12,17)),1)
Lk.new(tc.outputs['Window'],sp.inputs[0]);Lk.new(sp.outputs['Y'],cr.inputs['Fac']);Lk.new(cr.outputs['Color'],bg.inputs['Color']);bg.inputs['Strength'].default_value=.9
# ---------------- animação ----------------
d2r=math.radians
def setpose(P,root=(0,0,0)):
    for n,(e,p,par) in JT.items():
        v=P.get(n,(0,0,0));e.rotation_euler=(d2r(v[0]),d2r(v[1]),d2r(v[2]))
    JT['root'][0].location=root
def ss(x):x=max(0,min(1,x));return x*x*(3-2*x)
def lerp(a,b,t):return a+(b-a)*t
def mix(A,B,t):
    out={}
    for k in set(A)|set(B):
        a=A.get(k,(0,0,0));b=B.get(k,(0,0,0));out[k]=tuple(lerp(a[i],b[i],t) for i in range(3))
    return out
def add(*Ps):
    out={}
    for P in Ps:
        for k,v in P.items():
            o=out.get(k,(0,0,0));out[k]=(o[0]+v[0],o[1]+v[1],o[2]+v[2])
    return out
def keyed(keys,t):
    """keys: [(t,pose,rootz)]; interpolação suave entre quadros-chave (sem parar em cada um)"""
    for i in range(len(keys)-1):
        t0,P0,r0=keys[i];t1,P1,r1=keys[i+1]
        if t<=t1:
            u=(t-t0)/(t1-t0) if t1>t0 else 1;u=ss(u);return mix(P0,P1,u),tuple(lerp(r0[j],r1[j],u) for j in range(3))
    return keys[-1][1],keys[-1][2]
BASE={'thL':(-6,0,0),'knL':(12,0,0),'anL':(-6,0,0),'thR':(-6,0,0),'knR':(12,0,0),'anR':(-6,0,0),'elL':(-22,0,0),'fL0a':(-14,0,0),'fL0b':(-22,0,0),'fL1a':(-14,0,0),'fL1b':(-22,0,0),'fL2a':(-14,0,0),'fL2b':(-22,0,0),'tL_a':(-10,0,0),'tL_b':(-14,0,0)}
BASEROOT=(0,0,-.03)
def pose_idle(t):
    p=2*math.pi*t;b=math.sin(p);P={}
    P['spine']=(1.5*b,0,1.5*math.sin(p+1))
    P['chest']=(-2.5*b,0,-3*math.sin(p+.6))
    P['hips']=(0,2.5*math.sin(p),-2*math.sin(p))
    P['neck']=(2.2*math.sin(p-.9),0,6*math.sin(p+1.0))
    P['earL']=(0,5*math.sin(p-1.4),0);P['earR']=(0,-5*math.sin(p-1.9),0)
    P['shL']=(-3*math.sin(p-.5),2*math.sin(p),0);P['elL']=(-3*math.sin(p-1),0,0);P['wrL']=(2*math.sin(p-1.4),0,0)
    for i in range(3):P[f'fL{i}a']=(-2*math.sin(p-1.8-i*.3),0,0);P[f'fL{i}b']=(-3*math.sin(p-2.1-i*.3),0,0)
    P['shR']=(2*math.sin(p-.2),0,0);P['elR']=(-2.5*math.sin(p-.8),0,0);P['wrR']=(3*math.sin(p-1.2),0,0)
    P['thL']=(0,0,0);P['knL']=(2*b,0,0);P['knR']=(-2*b,0,0);P['club']=(4*math.sin(p-1.5),0,2*math.sin(p-.7))
    return add(BASE,P),(0,0,BASEROOT[2]+.012*b)
def pose_walk(t):
    ph=2*math.pi*t;P={}
    for n,sx,p in(('L',1,ph),('R',-1,ph+math.pi)):
        s=math.sin(p);c=math.cos(p)
        th=-30*s;kn=10+58*max(0,c)**1.4+8*max(0,-s)*0
        P['th'+n]=(th,0,0);P['kn'+n]=(kn,0,0)
        P['an'+n]=(-(th+kn)*.9+16*max(0,-s)*max(0,-c+.2),0,0);P['to'+n]=(-22*max(0,c)*max(0,s+.4)+16*max(0,-s)*max(0,.4-c),0,0)
    sL=math.sin(ph+math.pi);sR=-sL
    P['shL']=(-26*sL,0,0);P['elL']=(-(8+22*max(0,sL)+6*max(0,-sL)),0,0);P['wrL']=(8*sL,0,0)
    for i in range(3):P[f'fL{i}a']=(-6*sL,0,0);P[f'fL{i}b']=(-8*sL,0,0)
    P['shR']=(-9*sR,0,-3*math.sin(ph));P['elR']=(-(6+9*max(0,sR)),0,0);P['wrR']=(6*sR,0,0)
    P['hips']=(0,5*math.sin(ph),7*math.sin(ph));P['spine']=(2,0,-4*math.sin(ph));P['chest']=(-3,0,-6*math.sin(ph))
    P['neck']=(2+2*math.cos(2*ph),0,5*math.sin(ph-.3));P['earL']=(0,-9*math.sin(2*ph-1.0),0);P['earR']=(0,9*math.sin(2*ph-1.0),0)
    P['club']=(10*math.sin(ph-1.2),0,4*math.sin(ph-.5))
    return add(BASE,P),(0,0,BASEROOT[2]+.035*math.cos(2*ph))
def K(d,rz=0,ry=0):return (add(BASE,d),(0,ry,BASEROOT[2]+rz))
L_CROUCH={'thL':(-14,0,0),'knL':(38,0,0),'anL':(-16,0,0),'thR':(10,0,0),'knR':(40,0,0),'anR':(-24,0,0)}
ATK=[(0,)+K({}),
 (.13,)+K(dict(L_CROUCH,hips=(0,0,-4),spine=(-3,0,-4),chest=(-4,0,-7),neck=(-4,0,4),shR=(60,-4,8),elR=(-58,0,0),wrR=(-26,0,0),shL=(-22,0,18),elL=(-42,0,0),earL=(0,-10,0),earR=(0,10,0)),-.08),
 (.30,)+K(dict(L_CROUCH,hips=(0,0,-8),spine=(-5,0,-6),chest=(-7,0,-10),neck=(-6,0,7),shR=(135,-4,6),elR=(-62,0,0),wrR=(-70,0,0),shL=(-40,0,28),elL=(-56,0,0),wrL=(-8,0,0),
   knL=(44,0,0),knR=(46,0,0),earL=(0,-16,0),earR=(0,16,0),fL0a=(6,0,0),fL1a=(6,0,0),fL2a=(6,0,0),fL0b=(0,0,0),fL1b=(0,0,0),fL2b=(0,0,0)),-.12),
 (.39,)+K(dict(L_CROUCH,hips=(0,0,0),spine=(0,0,0),chest=(2,0,2),neck=(2,0,0),shR=(190,0,0),elR=(-62,0,0),wrR=(-62,0,0),shL=(-10,0,32),elL=(-50,0,0),thL=(-24,0,0),knL=(34,0,0),anL=(-8,0,0),thR=(14,0,0),knR=(30,0,0),earL=(0,8,0),earR=(0,-8,0)),-.10),
 (.46,)+K(dict(hips=(0,0,9),spine=(10,0,3),chest=(10,0,8),neck=(6,0,-14),shR=(256,0,0),elR=(-18,0,0),wrR=(-76,0,0),shL=(24,0,36),elL=(-46,0,0),
   thL=(-36,0,0),knL=(30,0,0),anL=(-6,0,0),thR=(20,0,0),knR=(14,0,0),anR=(-22,0,0),earL=(0,28,0),earR=(0,-28,0)),-.07,-.22),
 (.55,)+K(dict(hips=(0,0,8),spine=(11,0,3),chest=(11,0,8),neck=(8,0,-12),shR=(268,0,0),elR=(-24,0,0),wrR=(-72,0,0),shL=(28,0,38),elL=(-44,0,0),
   thL=(-38,0,0),knL=(36,0,0),anL=(-6,0,0),thR=(22,0,0),knR=(20,0,0),anR=(-26,0,0),earL=(0,18,0),earR=(0,-18,0)),-.11,-.26),
 (.78,)+K(dict(hips=(0,0,5),spine=(3,0,2),chest=(2,0,5),neck=(2,0,-2),shR=(310,0,0),elR=(-38,0,0),wrR=(-40,0,0),shL=(6,0,14),elL=(-34,0,0),
   thL=(-16,0,0),knL=(22,0,0),anL=(-6,0,0),thR=(8,0,0),knR=(18,0,0),anR=(-14,0,0)),-.05,-.08),
 (1,)+K({'shR':(360,0,0)})]
HURT=[(0,)+K({}),
 (.14,)+K({'spine':(-10,0,0),'chest':(-22,0,6),'neck':(-24,0,-8),'hips':(-8,0,-4),'shR':(28,0,-22),'elR':(-28,0,0),'wrR':(15,0,0),'shL':(-36,0,44),'elL':(-26,0,0),
   'thL':(-18,0,0),'knL':(30,0,0),'anL':(-12,0,0),'thR':(12,0,0),'knR':(38,0,0),'anR':(-24,0,0),'earL':(0,34,0),'earR':(0,-34,0),'fL0a':(6,0,0),'fL1a':(6,0,0),'fL2a':(6,0,0)},-.05),
 (.4,)+K({'spine':(6,0,0),'chest':(8,0,-3),'neck':(8,0,4),'hips':(3,0,3),'shR':(-6,0,2),'elR':(-24,0,0),'shL':(-4,0,12),'elL':(-30,0,0),'thL':(-10,0,0),'knL':(26,0,0),'anL':(-8,0,0),'thR':(6,0,0),'knR':(20,0,0),'anR':(-12,0,0),'earL':(0,-16,0),'earR':(0,16,0)},-.07),
 (.7,)+K({'spine':(-2,0,0),'chest':(-2,0,1),'neck':(-2,0,0),'earL':(0,6,0),'earR':(0,-6,0)},-.035),
 (1,)+K({})]
def track(L,t):
    for i in range(len(L)-1):
        t0,v0=L[i];t1,v1=L[i+1]
        if t<=t1:
            u=ss((t-t0)/(t1-t0)) if t1>t0 else 1;return tuple(lerp(v0[k],v1[k],u) for k in range(3))
    return L[-1][1]
CLUB=[(0,(0,0,0)),(.13,(-8,0,0)),(.30,(-24,0,0)),(.39,(-12,0,0)),(.46,(-32,0,0)),(.55,(-34,0,0)),(.66,(-14,0,0)),(.78,(0,0,0)),(1,(0,0,0))]
ABD=[(0,(0,0,0)),(.13,(0,0,8)),(.30,(0,0,24)),(.39,(0,0,26)),(.46,(0,0,10)),(.55,(0,0,0)),(1,(0,0,0))]
def pose_attack(t):
    P,r=keyed(ATK,t);P=dict(P);P['club']=track(CLUB,t);a=track(ABD,t);o=P.get('shR',(0,0,0));P['shR']=(o[0],o[1],o[2]+a[2]);return P,r
HC=[(0,(0,0,0)),(.14,(-30,0,10)),(.4,(18,0,-6)),(.7,(-6,0,2)),(1,(0,0,0))]
def pose_hurt(t):
    P,r=keyed(HURT,t);P=dict(P);P['club']=track(HC,t);return P,r
FN={'idle':(pose_idle,48),'walk':(pose_walk,24),'attack':(pose_attack,40),'hurt':(pose_hurt,20)}
import os
os.makedirs(OUT,exist_ok=True)
TS=[float(x) for x in sys.argv[6].split(',')] if len(sys.argv)>6 else None
if ANIM=='rest':
    setpose(*pose_idle(0));sc.render.filepath=OUT+'/rest.png';bpy.ops.render.render(write_still=True)
else:
    fn,N=FN[ANIM]
    frames=[(i,t) for i,t in enumerate(TS)] if TS else [(i,i/N) for i in range(N)]
    LAY=bool(os.environ.get('LAYERS'))
    meshes=[o for o in bpy.data.objects if o.type=='MESH']
    clubs=[o for o in meshes if o.parent is JT['club'][0]]
    others=[o for o in meshes if o not in clubs]
    for i,t in frames:
        P,r=fn(t);setpose(P,r)
        if not LAY:
            sc.render.filepath=f'{OUT}/{ANIM}_{i:03d}.png';bpy.ops.render.render(write_still=True);continue
        for o in clubs:o.hide_render=True
        for o in others:o.is_holdout=False
        sc.render.filepath=f'{OUT}/{ANIM}_{i:03d}_body.png';bpy.ops.render.render(write_still=True)
        for o in clubs:o.hide_render=False
        for o in others:o.is_holdout=True
        sc.render.filepath=f'{OUT}/{ANIM}_{i:03d}_club.png';bpy.ops.render.render(write_still=True)
        for o in others:o.is_holdout=False
print('ok')
