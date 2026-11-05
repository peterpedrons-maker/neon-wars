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
# ---------- PERNAS E PÉS (frente = -Y)
for sx in(1,-1):
    blob((sx*.27,0,.62),(.25,.24,.22),G,sub=2,noise=.05,seed=40+sx)                  # quadril
    limb((sx*.27,0,.62),(sx*.31,-.10,.40),.21,.17,G,seg=7)
    blob((sx*.31,-.10,.40),(.18,.17,.16),G,sub=1,noise=.04,seed=50+sx)             # joelho
    limb((sx*.31,-.10,.40),(sx*.32,-.16,.20),.17,.15,G,seg=7)
    ring((sx*.32,-.15,.26),.19,.11,M['tan'],seg=8,rot=(math.radians(-10),0,0))
    # pé: sola larga + calcanhar + 3 dedos grossos com unhas
    blob((sx*.33,-.18,.13),(.27,.36,.12),G,sub=2,noise=.04,rot=(0,0,sx*.08),seed=60+sx)
    blob((sx*.31,.00,.15),(.20,.18,.14),G,sub=1,noise=.04,seed=62+sx)                      # calcanhar
    blob((sx*.34,-.40,.15),(.25,.22,.12),G,sub=1,noise=.04,seed=64+sx)                     # peito do pé
    for k,off in enumerate((-.19,0,.19)):
        a=off*1.2*sx
        tx=sx*.34+off;ty=-.58-(.03 if k==1 else 0)
        blob((tx,ty,.125),(.125,.19,.11),G,sub=1,noise=.03,rot=(0,0,a*.5),seed=70+k+sx)  # dedo
        blob((tx+a*.05,ty-.14,.115),(.11,.09,.10),G,sub=1,noise=.03)                    # ponta
        blob((tx+a*.07,ty-.19,.17),(.095,.10,.035),M['nail'],sub=1,noise=.02,rot=(-.35,0,a*.5))   # unha
# ---------- TRONCO
blob((0,.02,1.30),(.54,.42,.46),G,sub=2,noise=.05,seed=11)
blob((0,-.03,1.02),(.46,.40,.36),G,sub=2,noise=.05,seed=12)
blob((0,.04,.78),(.42,.36,.20),G,sub=1,noise=.04,seed=13)
# saiote em dentes
bm=bmesh.new();N=15;zt=.86
top=[bm.verts.new((math.cos(a)*.47,math.sin(a)*.42,zt)) for a in [i*2*math.pi/N for i in range(N)]]
bot=[]
for i in range(N):
    a=i*2*math.pi/N;ab=a+math.pi/N;f=(1.0 if math.sin(a)<0.2 else .6)
    bot.append(bm.verts.new((math.cos(a)*.56,math.sin(a)*.51,zt-.12)))
    bot.append(bm.verts.new((math.cos(ab)*.60,math.sin(ab)*.54,zt-.40*f-random.uniform(0,.07))))
for i in range(N):
    bm.faces.new((top[i],top[(i+1)%N],bot[(2*i+2)%(2*N)],bot[2*i+1],bot[2*i]))
bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
sk=obj_from_bm(bm,'skirt');sl=sk.modifiers.new('s','SOLIDIFY');sl.thickness=.035;finish(sk,M['cloth'])
limb((-.52,-.36,.90),(.52,-.36,.90),.07,.07,M['leather'],seg=4)
limb((.40,-.30,1.70),(-.38,-.44,.94),.09,.09,M['leather'],seg=4)
blob((.03,-.545,1.30),(.19,.04,.19),M['metal'],sub=0,noise=0,rot=(0,math.radians(45),0))
blob((.03,-.565,1.30),(.095,.04,.095),M['leather'],sub=0,noise=0,rot=(0,math.radians(45),0))
# ---------- BRAÇO ESQUERDO (x+): pendurado
blob((.62,0,1.50),(.27,.26,.26),G,sub=2,noise=.05,seed=71)
limb((.62,0,1.50),(.80,-.08,1.16),.21,.16,G,seg=7)
blob((.80,-.08,1.16),(.16,.15,.15),G,sub=1,noise=.04,seed=72)
limb((.80,-.08,1.16),(.84,-.28,.90),.16,.14,G,seg=7)
ring((.84,-.27,.93),.17,.10,M['tan'],seg=8,rot=(math.radians(-24),0,0))
blob((.86,-.36,.78),(.20,.12,.19),G,sub=2,noise=.04,seed=73)                                # palma
for dx,l in ((-.09,.98),(.03,1.04),(.14,.94)):
    finger((.86+dx,-.38,.70),(.86+dx*1.15,-.44,.52*l+.06),(.86+dx*1.2,-.56,.36*l+.12),.075,G)
finger((.69,-.34,.78),(.64,-.43,.66),(.66,-.54,.58),.07,G)                                    # polegar
# ---------- BRAÇO DIREITO (x-): segura a clava
blob((-.62,0,1.50),(.27,.26,.26),G,sub=2,noise=.05,seed=81)
limb((-.62,0,1.50),(-.84,-.18,1.24),.21,.16,G,seg=7)
blob((-.84,-.18,1.24),(.16,.15,.15),G,sub=1,noise=.04,seed=82)
limb((-.84,-.18,1.24),(-.76,-.46,1.06),.16,.14,G,seg=7)
ring((-.77,-.44,1.08),.17,.10,M['tan'],seg=8,rot=(math.radians(-60),0,0))
blob((-.76,-.50,1.06),(.20,.14,.20),G,sub=2,noise=.04,seed=83)                              # palma atrás do cabo
limb((-.72,-.50,.70),(-.77,-.50,1.58),.10,.19,M['club'],seg=8)                 # clava
blob((-.78,-.50,1.74),(.25,.24,.28),M['club'],sub=2,noise=.05,seed=5)
for d in((-1,0,.2),(.9,.1,.25),(-.2,-.9,.3),(-.3,.9,.2),(0,0,1),(-.9,-.5,-.3),(.8,-.6,-.1)):
    dv=Vector(d).normalized();c=Vector((-.78,-.50,1.74))+Vector((dv.x*.2,dv.y*.2,dv.z*.24))
    spike(c,dv,.26,.075,M['metal'],seg=4)
for z in (1.20,1.11,1.02,.93):                                                               # 4 dedos envolvendo o cabo
    finger((-.62,-.52,z),(-.70,-.70,z-.005),(-.90,-.62,z-.01),.07,G)
finger((-.62,-.62,1.28),(-.74,-.70,1.28),(-.86,-.68,1.22),.07,G)                              # polegar por cima
# ---------- CABEÇA
h0=len(bpy.data.objects)
blob((0,-.06,2.00),(.70,.62,.56),G,sub=2,noise=.04,seed=21)
blob((0,-.28,1.72),(.50,.38,.32),G,sub=2,noise=.04,seed=22)
for sx in(1,-1):
    blob((sx*.43,-.36,1.84),(.25,.21,.22),G,sub=1,noise=.04,seed=23+sx)    # bochechas
    blob((sx*.29,-.55,2.17),(.32,.15,.095),D,sub=1,noise=.03,rot=(0,sx*(-.38),sx*(.26)))      # sobrancelha pesada
    blob((sx*.28,-.54,1.99),(.25,.07,.24),M['rim'],sub=2,noise=0)                         # aro do olho
    blob((sx*.28,-.585,1.99),(.20,.06,.21),M['eye'],sub=2,noise=0)
    blob((sx*.255,-.635,1.98),(.095,.04,.105),M['pup'],sub=2,noise=0)
    spike((sx*.31,-.60,1.54),(sx*.08,-.30,1.0),.21,.06,M['tusk'],seg=5)               # presas
blob((0,-.60,1.57),(.34,.12,.08),D,sub=1,noise=.03)                                       # boca
blob((0,-.66,1.60),(.26,.10,.10),G,sub=1,noise=.03)                                       # queixo
spike((0,-.50,1.92),(0,-1,-.25),.40,.17,G,seg=4)                                          # nariz de pirâmide
blob((0,-.55,2.03),(.12,.10,.10),G,sub=1,noise=.03)
# orelhas
for sx in(1,-1):
    ptsO=[(0,-.22),(0,.26),(.48,.62),(1.00,1.12),(1.32,1.58),(.98,1.46),(.46,.94),(.10,.40)]
    ptsO=[(0,-.24),(0,.28),(.45,.52),(.95,.78),(1.42,1.12),(1.02,.66),(.62,.14),(.28,-.16)]
    ptsI=[(.10,-.12),(.10,.18),(.46,.42),(.90,.68),(1.20,.96),(.92,.58),(.58,.14),(.32,-.04)]
    o=prism(ptsO,.16,G,y0=0);finish(o,G);oi=prism(ptsI,.05,M['ear'],y0=-.03);finish(oi,M['ear'])
    for ob in(o,oi):
        ob.data.transform(Matrix.Rotation(math.radians(-8),4,'Y'))
        ob.data.transform(Matrix.Rotation(math.radians(6),4,'Z'))
        ob.data.transform(Matrix.Translation((.60,.04,1.86)))
        if sx<0:ob.scale.x=-1
hp=newobjs(h0)
em=bpy.data.objects.new('headpivot',None);sc.collection.objects.link(em);em.location=(0,0,1.7)
bpy.context.view_layer.update();parent_to(em,hp);em.rotation_euler=(math.radians(-3),0,math.radians(4))
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
tgt=Vector((0.25,-.05,1.5));pos=Vector((5.0,-7.4,3.0));co.location=pos;co.rotation_euler=(tgt-pos).to_track_quat('-Z','Y').to_euler()
def area(loc,e,size,col):
    l=bpy.data.lights.new('a','AREA');l.energy=e;l.size=size;l.color=col;o=bpy.data.objects.new('a',l);sc.collection.objects.link(o);o.location=loc;o.rotation_euler=(tgt-Vector(loc)).to_track_quat('-Z','Y').to_euler()
area((-3.5,-4.5,5.5),520,3.2,(1,.95,.88));area((4.5,3.5,3.5),380,4,(.65,.75,1));area((4.5,-4,1.2),60,4,(1,.9,.8))
w=bpy.data.worlds.new('w');sc.world=w;w.use_nodes=True;nt=w.node_tree;N=nt.nodes;Lk=nt.links
tc=N.new('ShaderNodeTexCoord');sp=N.new('ShaderNodeSeparateXYZ');cr=N.new('ShaderNodeValToRGB');bg=N['Background']
cr.color_ramp.elements[0].position=0.0;cr.color_ramp.elements[0].color=(*lin((54,58,66)),1);cr.color_ramp.elements[1].position=1.0;cr.color_ramp.elements[1].color=(*lin((10,12,17)),1)
Lk.new(tc.outputs['Window'],sp.inputs[0]);Lk.new(sp.outputs['Y'],cr.inputs['Fac']);Lk.new(cr.outputs['Color'],bg.inputs['Color']);bg.inputs['Strength'].default_value=.9
# fundo visível só para a câmera (a luz do mundo fica baixa para não lavar as facetas)
sc.render.filepath=OUT;bpy.ops.render.render(write_still=True);print('ok',OUT)
