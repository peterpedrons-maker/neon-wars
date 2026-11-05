"""Goblin low-poly (estilo facetado, cores chapadas) em Blender/bpy. Uso: /tmp/bpyenv/bin/python goblin_low.py saida.png [largura altura amostras]"""
import bpy,bmesh,math,random,sys
from mathutils import Vector,Matrix
OUT=sys.argv[1] if len(sys.argv)>1 else '/tmp/goblin_low.png'
W=int(sys.argv[2]) if len(sys.argv)>2 else 900;H=int(sys.argv[3]) if len(sys.argv)>3 else 1000;SM=int(sys.argv[4]) if len(sys.argv)>4 else 64
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
M=dict(green=mat('green',(128,176,40)),green2=mat('green2',(98,146,30)),ear=mat('ear',(150,98,58)),leather=mat('leather',(128,82,48)),cloth=mat('cloth',(118,74,44)),
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

G=M['green']
# ---- pés e pernas (frente = -Y)
for sx in(1,-1):
    foot=blob((sx*.32,-.18,.17),(.30,.46,.17),G,sub=2,noise=.05,rot=(0,0,sx*.12))
    for k,off in enumerate((-.16,0,.16)):
        n=blob((sx*.32+off*.95+sx*.01,-.58,.12),(.07,.11,.045),M['nail'],sub=1,noise=.03,rot=(0,0,0))
    limb((sx*.30,-.05,.30),(sx*.28,0,.80),.20,.17,G,seg=7)
    ring((sx*.29,-.04,.40),.22,.12,M['tan'],seg=8)
# ---- tronco
blob((0,.02,1.12),(.50,.40,.58),G,sub=2,noise=.05,seed=11)
blob((0,-.05,1.0),(.40,.30,.45),M['green2'],sub=1,noise=.03,seed=3).scale=(1.0,.9,1.0)  # barriga levemente mais escura (invisível por dentro; só dá volume)
# saiote de couro em dentes
bm=bmesh.new();N=14;rt=.42;zt=.82
top=[bm.verts.new((math.cos(a)*rt*1.05,math.sin(a)*rt*.82+.0,zt)) for a in [i*2*math.pi/N for i in range(N)]]
bot=[]
for i in range(N):
    a=i*2*math.pi/N;ab=a+math.pi/N
    bot.append(bm.verts.new((math.cos(a)*rt*1.2,math.sin(a)*rt*.95,zt-.10)))
    bot.append(bm.verts.new((math.cos(ab)*rt*1.28,math.sin(ab)*rt*1.0,zt-.34-random.uniform(0,.08))))
for i in range(N):
    t0,t1=top[i],top[(i+1)%N];b0,bt,b1=bot[2*i],bot[2*i+1],bot[(2*i+2)%(2*N)]
    bm.faces.new((t0,t1,b1,bt,b0))
bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
sk=obj_from_bm(bm,'skirt');sol=sk.modifiers.new('s','SOLIDIFY');sol.thickness=.03;finish(sk,M['cloth'])
# correia diagonal + fivela
limb((.36,-.30,1.66),(-.34,-.37,.84),.085,.085,M['leather'],seg=4)
blob((.02,-.455,1.24),(.17,.035,.17),M['metal'],sub=0,noise=0,rot=(0,math.radians(45),0))
blob((.02,-.47,1.24),(.085,.035,.085),M['leather'],sub=0,noise=0,rot=(0,math.radians(45),0))
limb((-.44,-.30,.90),(.46,-.30,.90),.06,.06,M['leather'],seg=4)  # cinto
# ---- braços: esquerdo do goblin (x+) pendurado; direito (x-) segura a clava
limb((.52,0,1.48),(.78,-.10,.98),.17,.15,G,seg=7);ring((.77,-.10,1.02),.17,.10,M['tan'],seg=8,rot=(math.radians(-14),0,0))
blob((.80,-.14,.82),(.19,.17,.17),G,sub=2,noise=.05)
for k,(dx,dz) in enumerate(((.12,.0),(.02,-.04),(-.08,-.02),(.00,-.12))):pass
for dx in(-.10,0,.10):
    blob((.80+dx*.9,-.20,.64),(.06,.08,.12),G,sub=1,noise=.04,rot=(.15,0,0))
limb((-.52,0,1.46),(-.66,-.28,1.08),.17,.15,G,seg=7)
ring((-.66,-.30,1.10),.17,.10,M['tan'],seg=8,rot=(math.radians(-25),math.radians(-10),0))
blob((-.68,-.40,.96),(.20,.17,.17),G,sub=2,noise=.05)
# clava
limb((-.69,-.40,.62),(-.74,-.36,1.50),.095,.17,M['club'],seg=8)
blob((-.745,-.36,1.60),(.21,.20,.22),M['club'],sub=2,noise=.04,seed=5)
for (x,y,z,rx,ry) in((-.95,-.36,1.28,0,-1.4),(-.55,-.50,1.40,1.3,0),(-.90,-.18,1.55,-.9,-1.1),(-.62,-.22,1.15,-1.2,1.0)):
    tri_pyr((x,y,z),(.09,.30),M['metal'],rot=(rx,ry,0),seg=4)
# ---- cabeça
head=blob((0,-.04,1.88),(.70,.62,.58),G,sub=2,noise=.04,seed=21)
blob((0,-.30,1.70),(.46,.36,.30),G,sub=1,noise=.04,seed=2)         # focinho/mandíbula
# sobrancelhas
for sx in(1,-1):
    brow=blob((sx*.27,-.50,2.06),(.30,.14,.09),G,sub=1,noise=.02,rot=(0.0,sx*(-.32),sx*(.28)))
    # olho: aro escuro, globo amarelo, pupila
    blob((sx*.27,-.55,1.93),(.22,.06,.22),M['rim'],sub=1,noise=0)
    blob((sx*.27,-.59,1.93),(.17,.05,.19),M['eye'],sub=1,noise=0)
    blob((sx*.25,-.635,1.93),(.085,.035,.10),M['pup'],sub=1,noise=0)
# nariz
tri_pyr((0,-.58,1.78),(.13,.34),G,rot=(math.pi/2+.35,0,0),seg=4)
# bocas e presas
blob((0,-.58,1.58),(.30,.10,.07),M['green2'],sub=1,noise=.03)
for sx in(1,-1):tri_pyr((sx*.20,-.60,1.62),(.055,.20),M['tusk'],rot=(0,0,0),seg=5)
# orelhas
for sx in(1,-1):
    ptsO=[(.50,1.80),(.80,1.76),(1.28,2.20),(1.50,2.72),(1.12,2.60),(.66,2.32),(.46,2.04)]
    o=prism(ptsO,.08,G,y0=0.02);finish(o,G)
    ptsI=[(.60,1.90),(.80,1.86),(1.14,2.22),(1.28,2.58),(.98,2.46),(.70,2.24),(.58,2.04)]
    oi=prism(ptsI,.035,M['ear'],y0=-.012);finish(oi,M['ear'])
    for ob in(o,oi):
        ob.rotation_euler=(0,0,0)
        # gira em torno do ponto da base para abrir e recuar
        ob.location=(0,0,0)
        ob.data.transform(Matrix.Translation((-.5,0,-1.9)))
        ob.data.transform(Matrix.Rotation(math.radians(-14),4,'Y'))
        ob.data.transform(Matrix.Rotation(math.radians(24),4,'Z'))
        ob.data.transform(Matrix.Translation((.5,0,1.9)))
        if sx<0:ob.scale.x=-1
bpy.context.view_layer.update()
# ---- cena
bpy.ops.object.select_all(action='DESELECT')
for ob in sc.objects:
    if ob.type=='MESH' and ob.scale.x<0:   # normais após espelhar
        pass
sc.render.engine='CYCLES';sc.cycles.device='CPU';sc.cycles.samples=SM;sc.cycles.use_denoising=True
sc.render.resolution_x=W;sc.render.resolution_y=H;sc.render.image_settings.file_format='PNG'
sc.view_settings.view_transform='Standard'
cam=bpy.data.cameras.new('c');cam.lens=70;co=bpy.data.objects.new('c',cam);sc.collection.objects.link(co);sc.camera=co
tgt=Vector((0.1,-.05,1.38));pos=Vector((4.4,-6.3,2.7));co.location=pos;co.rotation_euler=(tgt-pos).to_track_quat('-Z','Y').to_euler()
def area(loc,e,size,col):
    l=bpy.data.lights.new('a','AREA');l.energy=e;l.size=size;l.color=col;o=bpy.data.objects.new('a',l);sc.collection.objects.link(o);o.location=loc;o.rotation_euler=(tgt-Vector(loc)).to_track_quat('-Z','Y').to_euler()
area((-3.5,-4.5,5.5),520,3.2,(1,.95,.88));area((4.5,3.5,3.5),380,4,(.65,.75,1));area((4.5,-4,1.2),60,4,(1,.9,.8))
w=bpy.data.worlds.new('w');sc.world=w;w.use_nodes=True;nt=w.node_tree;N=nt.nodes;Lk=nt.links
tc=N.new('ShaderNodeTexCoord');sp=N.new('ShaderNodeSeparateXYZ');cr=N.new('ShaderNodeValToRGB');bg=N['Background']
cr.color_ramp.elements[0].position=0.0;cr.color_ramp.elements[0].color=(*lin((54,58,66)),1);cr.color_ramp.elements[1].position=1.0;cr.color_ramp.elements[1].color=(*lin((10,12,17)),1)
Lk.new(tc.outputs['Window'],sp.inputs[0]);Lk.new(sp.outputs['Y'],cr.inputs['Fac']);Lk.new(cr.outputs['Color'],bg.inputs['Color']);bg.inputs['Strength'].default_value=.9
# fundo visível só para a câmera (a luz do mundo fica baixa para não lavar as facetas)
sc.render.filepath=OUT;bpy.ops.render.render(write_still=True);print('ok',OUT)
