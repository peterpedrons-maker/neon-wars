"""Mockup 2.5D no Blender (bpy + Cycles): masmorra em 3D com tijolos e lajes de verdade, arco, pilares, tochas com luz, props, um guerreiro e um rato modelados à mão.
Uso: PYTHONPATH=/tmp/np1 python3 cena25d.py <saida.png> [wide|hero] [largura] [amostras]   (precisa de numpy<2 para o bpy)"""
import bpy,bmesh,math,random,sys
from mathutils import Vector,Matrix,Euler
random.seed(5)
OUT=sys.argv[1] if len(sys.argv)>1 else '/tmp/cena25d.png'
VIEW=sys.argv[2] if len(sys.argv)>2 else 'wide'
RW=int(sys.argv[3]) if len(sys.argv)>3 else 1600
SAMP=int(sys.argv[4]) if len(sys.argv)>4 else 48
def lin(c):return tuple(x**2.2 for x in c)
bpy.ops.wm.read_factory_settings(use_empty=True)
sc=bpy.context.scene;R=sc.render
R.engine='CYCLES';sc.cycles.device='CPU';sc.cycles.samples=SAMP;sc.cycles.use_denoising=True;sc.cycles.denoiser='OPENIMAGEDENOISE'
import os
sc.cycles.max_bounces=int(os.environ.get('BOUNCES','6'));sc.cycles.volume_bounces=1;sc.cycles.volume_step_rate=2.0;sc.cycles.caustics_reflective=False;sc.cycles.caustics_refractive=False
R.resolution_x=RW;R.resolution_y=int(RW*.625);R.image_settings.file_format='PNG'
sc.view_settings.view_transform='AgX';sc.view_settings.look='AgX - Medium High Contrast' if 'AgX - Medium High Contrast' in [i.identifier for i in sc.view_settings.bl_rna.properties['look'].enum_items] else 'None'
# ---------------- materiais ----------------
def _bsdf(m):
    m.use_nodes=True;t=m.node_tree;return t,t.nodes['Principled BSDF']
def mat(name,col,rough=.6,metal=0,emit=0,bump=0,bscale=40,coat=0):
    m=bpy.data.materials.new(name);t,b=_bsdf(m);N=t.nodes;L=t.links
    b.inputs['Base Color'].default_value=(*lin(col),1);b.inputs['Roughness'].default_value=rough;b.inputs['Metallic'].default_value=metal
    if emit:b.inputs['Emission Color'].default_value=(*lin(col),1);b.inputs['Emission Strength'].default_value=emit
    if bump:
        ns=N.new('ShaderNodeTexNoise');ns.inputs['Scale'].default_value=bscale;ns.inputs['Detail'].default_value=8
        bp=N.new('ShaderNodeBump');bp.inputs['Strength'].default_value=bump;L.new(N['Texture Coordinate'].outputs['Object'] if 'Texture Coordinate' in N else N.new('ShaderNodeTexCoord').outputs['Object'],ns.inputs['Vector'])
        L.new(ns.outputs['Fac'],bp.inputs['Height']);L.new(bp.outputs['Normal'],b.inputs['Normal'])
    return m
def mat_stone(name,c0,c1,rough=.85,cell=2.2,bump=.35,moss=0):
    """pedra: tinta por célula (Voronoi) + ruído fino + relevo + bisel falso; moss>0 mistura musgo em manchas"""
    m=bpy.data.materials.new(name);t,b=_bsdf(m);N=t.nodes;L=t.links
    tc=N.new('ShaderNodeTexCoord')
    vo=N.new('ShaderNodeTexVoronoi');vo.inputs['Scale'].default_value=cell;vo.inputs['Randomness'].default_value=1.0;L.new(tc.outputs['Object'],vo.inputs['Vector'])
    ns=N.new('ShaderNodeTexNoise');ns.inputs['Scale'].default_value=24;ns.inputs['Detail'].default_value=10;L.new(tc.outputs['Object'],ns.inputs['Vector'])
    ns2=N.new('ShaderNodeTexNoise');ns2.inputs['Scale'].default_value=1.6;ns2.inputs['Detail'].default_value=4;L.new(tc.outputs['Object'],ns2.inputs['Vector'])
    sep=N.new('ShaderNodeSeparateColor');L.new(vo.outputs['Color'],sep.inputs[0])
    mx=N.new('ShaderNodeMath');mx.operation='MULTIPLY_ADD';mx.inputs[1].default_value=.55;mx.inputs[2].default_value=.0
    L.new(sep.outputs[0],mx.inputs[0])
    a2=N.new('ShaderNodeMath');a2.operation='MULTIPLY_ADD';a2.inputs[1].default_value=.3;a2.inputs[2].default_value=0
    L.new(ns.outputs['Fac'],a2.inputs[0]);ad=N.new('ShaderNodeMath');ad.operation='ADD';L.new(mx.outputs[0],ad.inputs[0]);L.new(a2.outputs[0],ad.inputs[1])
    cr=N.new('ShaderNodeValToRGB');cr.color_ramp.elements[0].color=(*lin(c0),1);cr.color_ramp.elements[1].color=(*lin(c1),1);L.new(ad.outputs[0],cr.inputs['Fac'])
    col=cr.outputs['Color']
    if moss:
        mc=N.new('ShaderNodeMix');mc.data_type='RGBA';mc.blend_type='MIX'
        mr=N.new('ShaderNodeValToRGB');mr.color_ramp.elements[0].position=.55;mr.color_ramp.elements[1].position=.7;L.new(ns2.outputs['Fac'],mr.inputs['Fac'])
        mc.inputs[7].default_value=(*lin((.2,.34,.2)),1);L.new(mr.outputs['Color'],mc.inputs[0]);L.new(col,mc.inputs[6]);col=mc.outputs[2]
    L.new(col,b.inputs['Base Color'])
    bm=N.new('ShaderNodeBump');bm.inputs['Strength'].default_value=bump;bm.inputs['Distance'].default_value=.04;L.new(ns.outputs['Fac'],bm.inputs['Height'])
    bv=N.new('ShaderNodeBevel');bv.inputs['Radius'].default_value=.012;L.new(bv.outputs['Normal'],bm.inputs['Normal']);L.new(bm.outputs['Normal'],b.inputs['Normal'])
    b.inputs['Roughness'].default_value=rough
    return m
M=dict(
 wall=mat_stone('wall',(.07,.11,.14),(.2,.27,.3),moss=1),
 wall2=mat_stone('wall2',(.09,.13,.16),(.24,.31,.34)),
 floor=mat_stone('floor',(.07,.14,.2),(.17,.3,.37),rough=.62,cell=3.0,bump=.25),
 frame=mat_stone('frame',(.16,.2,.22),(.36,.42,.42),cell=1.6),
 iron=mat('iron',(.12,.13,.15),.45,.9,bump=.1),
 steel=mat('steel',(.62,.66,.72),.28,1.0,bump=.03,bscale=120),
 steel_d=mat('steel_d',(.28,.31,.36),.4,1.0),
 gold=mat('gold',(.9,.66,.2),.3,1.0),
 wood=mat('wood',(.26,.15,.08),.7,bump=.5,bscale=18),
 wood2=mat('wood2',(.36,.22,.11),.7,bump=.4,bscale=22),
 cloth=mat('cloth',(.55,.07,.08),.85,bump=.25,bscale=90),
 cloth2=mat('cloth2',(.38,.05,.06),.9,bump=.25,bscale=90),
 leather=mat('leather',(.2,.11,.06),.7,bump=.3,bscale=60),
 skin=mat('skin',(.9,.62,.46),.55),
 fur=mat('fur',(.38,.31,.25),.8,bump=1.1,bscale=320),
 fur2=mat('fur2',(.6,.52,.44),.8,bump=.9,bscale=260),
 pink=mat('pink',(.9,.55,.58),.45),
 tooth=mat('tooth',(.95,.92,.8),.4),
 eye=mat('eye',(.02,.02,.03),.1),
 eyer=mat('eyer',(1.0,.1,.05),.3,emit=1.5),
 white=mat('white',(.95,.95,.95),.4),
 flame=mat('flame',(1.0,.45,.08),.5,emit=14),
 flame2=mat('flame2',(1.0,.85,.4),.5,emit=22),
 rune=mat('rune',(.2,.7,1.0),.5,emit=2.2),
 black=mat('black',(.01,.01,.015),1),
)
def link(o,col=None):
    (col or sc.collection).objects.link(o);return o
def ob_from_mesh(name,me,mt):
    o=bpy.data.objects.new(name,me);link(o);
    if mt:o.data.materials.append(mt)
    return o
def smooth(o):
    for p in o.data.polygons:p.use_smooth=True
def prim(kind,loc=(0,0,0),sc_=(1,1,1),mt=None,rot=(0,0,0),sub=0,seg=24,**k):
    if kind=='sphere':bpy.ops.mesh.primitive_uv_sphere_add(segments=seg,ring_count=seg//2,radius=1,location=loc)
    elif kind=='cube':bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    elif kind=='cyl':bpy.ops.mesh.primitive_cylinder_add(vertices=seg,radius=k.get('r',1),depth=k.get('d',1),location=loc)
    elif kind=='cone':bpy.ops.mesh.primitive_cone_add(vertices=seg,radius1=k.get('r',1),radius2=k.get('r2',0),depth=k.get('d',1),location=loc)
    elif kind=='torus':bpy.ops.mesh.primitive_torus_add(major_radius=k.get('r',1),minor_radius=k.get('r2',.1),major_segments=seg,minor_segments=12,location=loc)
    o=bpy.context.active_object;o.scale=sc_;o.rotation_euler=[math.radians(a) for a in rot]
    if mt:o.data.materials.append(mt)
    if kind in('sphere','cyl','cone','torus'):smooth(o)
    if sub:
        m=o.modifiers.new('s','SUBSURF');m.levels=sub;m.render_levels=sub
    return o
def bevel(o,w=.02,seg=2):
    m=o.modifiers.new('b','BEVEL');m.width=w;m.segments=seg;m.limit_method='ANGLE';return o
def limb(a,b,r0,r1,mt,sub=1):
    """segmento afunilado entre dois pontos (membros) com pontas arredondadas"""
    a=Vector(a);b=Vector(b);d=b-a;L=d.length;mid=(a+b)/2
    o=prim('cyl',mid,(1,1,1),mt,r=1,d=1,seg=16);o.scale=(r0,r0,L)
    o.rotation_euler=d.to_track_quat('Z','Y').to_euler()
    for p,r in((a,r0),(b,r1)):
        s=prim('sphere',p,(r,r,r),mt,seg=16)
    return o
# ---------------- geometria em blocos (parede/piso) ----------------
def bricks_mesh(name,mt,boxes):
    bm=bmesh.new()
    for (c,s,rz) in boxes:
        bmesh.ops.create_cube(bm,size=1.0)
        verts=bm.verts[-8:]
        M_=Matrix.Translation(c)@Matrix.Rotation(rz,4,'Z')@Matrix.Diagonal((*s,1))
        for v in verts:v.co=M_@v.co
    me=bpy.data.meshes.new(name);bm.to_mesh(me);bm.free()
    o=ob_from_mesh(name,me,mt)
    bv=o.modifiers.new('bv','BEVEL');bv.width=.012;bv.segments=2;bv.limit_method='ANGLE'
    return o
ROOM_X=6.0;ROOM_Y=4.5;WALL_H=3.1;BD=.5   # meia-largura, meia-profundidade, altura, espessura da parede
def wall_boxes(length,height,x0,hole=None,axis='x',base=(0,0),depth=BD,course=.285):
    """tijolos de uma parede; hole(xl,zl)->True remove o tijolo (abertura do arco). Devolve lista (centro, tamanho, rot)"""
    out=[];z=0;row=0
    while z<height-.01:
        h=min(course,height-z);x=0;off=(row%2)*.28
        pos=-off
        while pos<length:
            w=random.choice([.5,.56,.62,.7]);w=min(w,length-max(pos,0)) if pos+w>length else w
            a=max(pos,0);bw=pos+w-a
            if bw>.05:
                xc=a+bw/2;zc=z+h/2
                skip=hole and hole(xc+x0,zc)
                if not skip:
                    dj=random.uniform(-.02,.02);dd=depth+dj*2
                    if axis=='x':out.append(((base[0]+x0+xc,base[1]+dj,zc),(bw-.025,dd,h-.025),0))
                    else:out.append(((base[0]+dj,base[1]+x0+xc,zc),(dd,bw-.025,h-.025),0))
            pos+=w
        z+=h;row+=1
    return out
# ---------------- piso ----------------
fb=[];sw,sh=.62,.5
nx=int(2*ROOM_X/sw)+2;ny=int(2*ROOM_Y/sh)+2
for j in range(ny):
    off=(j%2)*sw*.5
    for i in range(nx+1):
        x=-ROOM_X-sw+i*sw+off+sw/2;y=-ROOM_Y-sh/2+j*sh+sh/2+.0
        if x-sw/2>ROOM_X+.05 or y>ROOM_Y+.05 or x+sw/2<-ROOM_X-.05 or y<-ROOM_Y-.4:continue
        fb.append(((x,y,random.uniform(-.012,.008)-.12),(sw-.028,sh-.028,.24),0))
floor=bricks_mesh('floor',M['floor'],fb)
# ---------------- paredes ----------------
ARCH_W=.95;SPRING=1.65
def hole_back(xg,zg):
    if abs(xg)<ARCH_W+.02 and zg<SPRING:return True
    return math.hypot(xg,zg-SPRING)<ARCH_W+.04 and zg>=SPRING
back=bricks_mesh('wall_back',M['wall'],wall_boxes(2*ROOM_X+BD,WALL_H,-ROOM_X-BD/2,hole_back,'x',(0,ROOM_Y+BD/2)))
left=bricks_mesh('wall_left',M['wall2'],wall_boxes(2*ROOM_Y+BD,WALL_H,-ROOM_Y-BD/2,None,'y',(-ROOM_X-BD/2,0)))
# coroamento (pedra de remate) das paredes
for (c,s) in(((0,ROOM_Y+BD/2,WALL_H+.07),(2*ROOM_X+BD+.3,BD+.18,.16)),((-ROOM_X-BD/2,0,WALL_H+.07),(BD+.18,2*ROOM_Y+.3,.16))):
    o=prim('cube',c,s,M['frame']);bevel(o,.03)
# moldura do arco: aduelas + ombreiras
fr=[]
for k in range(13):
    a0=math.pi*k/13;a1=math.pi*(k+1)/13;am=(a0+a1)/2
    ri,ro=ARCH_W,ARCH_W+.42+.05*(k%2)
    cx=math.cos(am)*(ri+ro)/2;cz=SPRING+math.sin(am)*(ri+ro)/2
    wdt=(a1-a0)*(ri+ro)/2-.02
    o=prim('cube',(cx,ROOM_Y+BD/2+.04,cz),(ro-ri,BD+.12,wdt),M['frame'],rot=(0,-math.degrees(am)+90,0));bevel(o,.02)
for sx in(-1,1):
    z=0
    while z<SPRING-.01:
        h=min(.4+random.uniform(0,.1),SPRING-z)
        o=prim('cube',(sx*(ARCH_W+.2),ROOM_Y+BD/2+.04,z+h/2),(.42,BD+.12,h-.02),M['frame']);bevel(o,.02);z+=h
o=prim('cube',(0,ROOM_Y+BD/2+.08,SPRING+ARCH_W+.34),(.34,BD+.2,.5),M['frame']);bevel(o,.03)   # pedra-chave
# corredor atrás do arco (escuro, com brilho de runa distante)
prim('cube',(0,ROOM_Y+BD+2.2,-.02),(2.0,4.4,.04),M['black'])
for sx in(-1,1):prim('cube',(sx*1.0,ROOM_Y+BD+2.2,1.6),(.1,4.4,3.2),M['wall'])
prim('cube',(0,ROOM_Y+BD+4.4,1.5),(2.0,.1,3.2),M['wall'])
rn=prim('torus',(0,ROOM_Y+BD+4.3,1.0),(1,1,1),M['rune'],rot=(90,0,0),r=.55,r2=.025,seg=40)
l=bpy.data.lights.new('rn','POINT');l.energy=90;l.color=(.3,.8,1);l.shadow_soft_size=.3;lo=bpy.data.objects.new('rn',l);link(lo);lo.location=(0,ROOM_Y+BD+3.9,1.0)
# ---------------- pilares ----------------
def pillar(x,y):
    prim('cube',(x,y,.14),(.9,.9,.28),M['frame']);prim('cyl',(x,y,.5),(1,1,1),M['wall2'],r=.34,d=.5)
    c=prim('cyl',(x,y,1.75),(1,1,1),M['wall2'],r=.29,d=2.4,seg=20)
    prim('torus',(x,y,.8),(1,1,1),M['frame'],r=.34,r2=.05)
    prim('torus',(x,y,2.8),(1,1,1),M['frame'],r=.31,r2=.06)
    o=prim('cube',(x,y,3.0),(.85,.85,.26),M['frame']);bevel(o,.03)
for x,y in((-3.4,2.2),(3.4,2.2),(-3.6,-1.9),(4.9,-2.7)):pillar(x,y)
# ---------------- tochas e luz ----------------
LIGHTS=[]
def torch(loc,face='y',sign=-1):
    x,y,z=loc
    prim('cyl',(x,y,z-.05),(1,1,1),M['wood'],r=.045,d=.55,rot=(0,0,0))
    prim('cyl',(x,y,z+.2),(1,1,1),M['iron'],r=.085,d=.14)
    fl=prim('sphere',(x,y,z+.36),(.075,.075,.19),M['flame'],seg=16);prim('sphere',(x,y,z+.33),(.04,.04,.12),M['flame2'],seg=12)
    if face=='y':prim('cube',(x,y-sign*.0,z-.12),(.1,.18,.05),M['iron']);
    l=bpy.data.lights.new('t','POINT');l.energy=170;l.color=(1,.6,.28);l.shadow_soft_size=.12
    lo=bpy.data.objects.new('t',l);link(lo);lo.location=(x+(.0 if face=='y' else .12),y-.12 if face=='y' else y,z+.4)
for x in(-4.2,-2.2,2.2,4.2):torch((x,ROOM_Y-.08,2.0),'y')
for y in(-2.8,.0,2.4):torch((-ROOM_X+.08,y,2.0),'x')
# estandartes
def banner(x,y,z,axis='x'):
    me=bpy.data.meshes.new('b');bm=bmesh.new();w=.36;h=1.35
    rows=10
    for r in range(rows+1):
        t=r/rows;ww=w*(1-.0*t)
        for c in(-1,0,1):
            xx=c*ww;zz=-t*h;yy=-.05*math.sin(t*3)-.03*(c*c)*(1-t)
            if t>.88 and c==0:zz+=.18*(t-.88)/.12
            bm.verts.new((xx,yy,zz))
    bm.verts.ensure_lookup_table()
    for r in range(rows):
        for c in range(2):
            a=r*3+c;bm.faces.new((bm.verts[a],bm.verts[a+1],bm.verts[a+4],bm.verts[a+3]))
    bm.to_mesh(me);bm.free();o=ob_from_mesh('ban',me,M['cloth']);smooth(o);o.modifiers.new('s','SUBSURF').levels=1
    o.location=(x,y,z)
    if axis=='y':o.rotation_euler=(0,0,math.radians(90))
    prim('cyl',(x,y+(0 if axis=='x' else 0),z+.02),(1,1,1),M['wood'],r=.03,d=.8,rot=(0,90,0) if axis=='x' else (90,0,0))
    # emblema
    if axis=='x':prim('cone',(x,y-.06,z-.5),(.12,.02,.2),M['gold'],rot=(90,0,0),r=1,d=1,seg=4)
for x in(-3.2,0,3.2):
    if abs(x)>.1:banner(x,ROOM_Y-.05,2.75)
banner(-ROOM_X+.06,-.9,2.75,'y');banner(-ROOM_X+.06,1.2,2.75,'y')
# ---------------- tapete ----------------
def plane(c,s,mt,z=0):return prim('cube',(c[0],c[1],z),(s[0],s[1],.016),mt)
plane((0,.2),(2.0,8.9),M['gold'],.005);plane((0,.2),(1.84,8.74),M['cloth2'],.012);plane((0,.2),(1.5,8.4),M['cloth'],.02)
for yy in [i*.6-3.8 for i in range(14)]:plane((0,yy),(1.5,.06),M['gold'],.026)
# ---------------- props ----------------
def barrel(x,y,s=1.0,rot=0):
    b=prim('cyl',(x,y,.42*s),(1,1,1),M['wood2'],r=.3*s,d=.84*s,seg=24);b.scale=(1,1,1)
    bm=bmesh.new();bm.from_mesh(b.data)
    for v in bm.verts:
        k=1+.16*(1-abs((v.co.z)/(.42*s))**2)
        v.co.x*=k;v.co.y*=k
    bm.to_mesh(b.data);bm.free();smooth(b)
    for z in(.14,.42,.7):prim('torus',(x,y,z*s+.0),(1,1,1),M['iron'],r=.31*s*(1+.12*(1-((z-.42)/.42)**2)*.9),r2=.022*s)
def crate(x,y,s=1.0,rz=0):
    o=prim('cube',(x,y,.3*s),(.6*s,.6*s,.6*s),M['wood'],rot=(0,0,rz));bevel(o,.03)
    for k in(-1,1):
        p=prim('cube',(x,y,.3*s),(.64*s,.08*s,.64*s),M['wood2'],rot=(0,0,rz+90*(k>0)));
def chest(x,y,rz=0):
    prim('cube',(x,y,.22),(.8,.5,.44),M['wood'],rot=(0,0,rz));
    l=prim('cyl',(x,y,.44),(1,1,1),M['wood2'],r=.25,d=.8,rot=(0,90,rz),seg=24);l.scale=(1,1,1)
    prim('cube',(x,y,.2),(.84,.12,.5),M['gold'],rot=(0,0,rz));prim('cube',(x,y-.26,.38),(.1,.04,.14),M['gold'],rot=(0,0,rz))
barrel(-5.2,3.6);barrel(-4.5,3.9,.9);barrel(-5.3,2.6,.85);crate(-4.6,2.9,1,15);crate(-4.9,2.8,.7,-20);
crate(-5.3,-3.2,1.0,10);crate(-5.4,-3.9,.85,-5);chest(5.0,3.6,0);barrel(5.3,2.9,.9);crate(-5.4,1.1,.8,5)
# esqueleto caído, caveira, ossos
prim('sphere',(4.4,-1.2,.13),(.13,.15,.14),M['tooth'],seg=16);prim('sphere',(4.35,-1.28,.2),(.1,.06,.06),M['tooth'],seg=12)
for (x,y,rz) in((4.6,-1.0,30),(4.2,-1.5,80),(4.8,-1.4,-20)):prim('cyl',(x,y,.04),(1,1,1),M['tooth'],r=.025,d=.45,rot=(0,90,rz),seg=10)
# poça refletora
pud=prim('cyl',(2.3,-2.6,.011),(1,1,1),mat('water',(.16,.32,.42),.05,0),r=.6,d=.005,seg=40);pud.scale=(1.2,.7,1)
# pedras soltas
for i in range(16):
    x=random.uniform(-5,5);y=random.uniform(-4,4)
    if abs(x)<1.1:continue
    prim('sphere',(x,y,.03),(random.uniform(.04,.1),random.uniform(.04,.1),random.uniform(.02,.05)),M['wall2'],seg=10)
# teias nos cantos
def web(x,y,z,sx,sy):
    for k in range(7):
        a=k/6*math.pi/2;ex=x+sx*math.cos(a)*.7;ey=y+sy*math.sin(a)*.0;ez=z-math.sin(a)*.7
        c=bpy.data.curves.new('w','CURVE');c.dimensions='3D';sp=c.splines.new('BEZIER');sp.bezier_points.add(1)
        sp.bezier_points[0].co=(x,y,z);sp.bezier_points[1].co=(ex,ey,ez)
        for p in sp.bezier_points:p.handle_left_type=p.handle_right_type='VECTOR'
        c.bevel_depth=.004;o=bpy.data.objects.new('w',c);link(o);o.data.materials.append(M['white'])
    for t in(.35,.7):
        pts=[(x+sx*math.cos(k/6*math.pi/2)*.7*t,y,z-math.sin(k/6*math.pi/2)*.7*t) for k in range(7)]
        c=bpy.data.curves.new('w','CURVE');c.dimensions='3D';sp=c.splines.new('POLY');sp.points.add(6)
        for i,p in enumerate(pts):sp.points[i].co=(*p,1)
        c.bevel_depth=.003;o=bpy.data.objects.new('w',c);link(o);o.data.materials.append(M['white'])
web(-ROOM_X+.02,ROOM_Y-.02,WALL_H-.05,1,0)
# ---------------- GUERREIRO ----------------
WAR={}
def warrior(px,py,rz):
    root=bpy.data.objects.new('warrior',None);link(root);root.location=(px,py,0);root.rotation_euler=(0,0,math.radians(rz))
    objs0=set(bpy.data.objects)
    S=1.0
    # botas e pernas
    for sy in(-1,1):
        prim('sphere',(.04,sy*.13,.075),(.17,.11,.085),M['leather'],seg=20)
        limb((0,sy*.12,.1),(0,sy*.12,.5),.075,.07,M['steel_d'])
        prim('sphere',(.02,sy*.12,.52),(.1,.1,.09),M['steel'],seg=16)   # joelheira
    # tronco: couraça + saia de couro + cinto
    prim('sphere',(0,0,.8),(.24,.3,.34),M['steel'],seg=28);prim('cube',(.13,0,.8),(.06,.26,.4),M['steel_d'],sub=0)
    prim('cyl',(0,0,.56),(1,1,1),M['cloth'],r=.28,d=.3,seg=24)                       # saia (tabardo)
    prim('torus',(0,0,.64),(1,1,1),M['leather'],r=.26,r2=.035);prim('cube',(.26,0,.64),(.02,.09,.08),M['gold'])
    # ombreiras e braços
    for sy in(-1,1):
        prim('sphere',(0,sy*.34,1.0),(.17,.17,.15),M['steel'],seg=20);prim('torus',(0,sy*.34,.93),(1,1,.5),M['gold'],r=.15,r2=.012)
    _A=set(bpy.data.objects)
    # braço da espada (y-): levantado para a frente
    limb((0,-.34,1.0),(.28,-.5,.98),.065,.06,M['steel_d']);limb((.28,-.5,.98),(.42,-.38,1.2),.06,.055,M['leather'])
    prim('sphere',(.42,-.38,1.21),(.075,.075,.075),M['leather'],seg=14)
    _arm=[o for o in bpy.data.objects if o not in _A]
    # braço do escudo (y+): dobrado à frente do corpo
    limb((0,.34,1.0),(.12,.5,.82),.065,.06,M['steel_d']);limb((.12,.5,.82),(.34,.5,.86),.06,.055,M['leather'])
    # cabeça
    prim('sphere',(0,0,1.3),(.25,.23,.25),M['skin'],seg=28)
    for sy in(-1,1):
        prim('sphere',(.2,sy*.09,1.31),(.04,.035,.05),M['eye'],seg=12);prim('sphere',(.225,sy*.09+.012,1.325),(.012,.012,.012),M['white'],seg=8)
        prim('cube',(.2,sy*.09,1.37),(.02,.09,.016),M['leather'],rot=(sy*-14,0,0))   # sobrancelhas
    prim('sphere',(.24,0,1.25),(.03,.03,.03),M['skin'],seg=10)
    # elmo
    h=prim('sphere',(0,0,1.47),(.285,.27,.19),M['steel'],seg=32)
    bpy.ops.object.select_all(action='DESELECT')
    prim('torus',(0,0,1.375),(1.0,.95,1),M['steel_d'],r=.275,r2=.03,seg=32);prim('cube',(.265,0,1.34),(.03,.045,.14),M['steel_d'])
    for sy in(-1,1):prim('cube',(.02,sy*.265,1.33),(.16,.03,.12),M['steel_d'],rot=(0,0,0))
    # penacho vermelho
    pts=[(-.05,0,1.62),(-.14,0,1.7),(-.26,0,1.68),(-.35,0,1.6),(-.4,0,1.48),(-.4,0,1.36)]
    for i,p in enumerate(pts):prim('sphere',p,(.07-.004*i,.04,.07-.004*i),M['cloth'],seg=14)
    # capa
    me=bpy.data.meshes.new('cape');bm=bmesh.new()
    for r in range(9):
        t=r/8
        for c in range(7):
            u=(c/6-.5)*(.52+.2*t);bm.verts.new((-.22-.14*t-.02*math.sin(c*1.2),u,1.05-t*.78+.03*math.sin(c*2+r)))
    bm.verts.ensure_lookup_table()
    for r in range(8):
        for c in range(6):
            a=r*7+c;bm.faces.new((bm.verts[a],bm.verts[a+1],bm.verts[a+8],bm.verts[a+7]))
    bm.to_mesh(me);bm.free();cp=ob_from_mesh('cape',me,M['cloth2']);smooth(cp);cp.modifiers.new('s','SUBSURF').levels=1;cp.modifiers.new('sol','SOLIDIFY').thickness=.015
    # espada (raiz na mão, inclinada para a frente e para baixo)
    sx,sy_,sz=.42,-.38,1.21
    sr=bpy.data.objects.new('swordroot',None);link(sr);sr.location=(sx,sy_,sz);sr.rotation_euler=(math.radians(-8),math.radians(62),0)
    def sp(o):o.parent=sr;o.location=o.location-Vector((sx,sy_,sz));return o
    sp(prim('cyl',(sx,sy_,sz+.02),(1,1,1),M['leather'],r=.022,d=.2,seg=12))
    sp(prim('cube',(sx,sy_,sz+.14),(.06,.3,.035),M['gold']))
    bl=sp(prim('cube',(sx,sy_,sz+.66),(.035,.1,.98),M['steel']));bevel(bl,.008)
    tp=prim('cone',(sx,sy_,sz+1.2),(.1,.035,.2),M['steel'],r=1,d=1,seg=4);tp.scale=(.045,.05,.2);sp(tp)
    sp(prim('sphere',(sx,sy_,sz-.09),(.04,.04,.04),M['gold'],seg=12))
    S0=Vector((0,-.34,1.0));armR=bpy.data.objects.new('armR',None);link(armR);armR.location=S0
    for o in _arm+[sr]:
        o.parent=armR;o.location=o.location-S0
    WAR['arm']=armR
    # escudo redondo
    shx,shy,shz=.36,.56,.86
    sd=prim('cyl',(shx,shy,shz),(1,1,1),M['wood2'],r=.36,d=.07,rot=(0,90,0),seg=40)
    sd.rotation_euler=(0,math.radians(90),0)
    r1=prim('torus',(shx+.04,shy,shz),(1,1,1),M['steel'],r=.36,r2=.035,rot=(0,90,0),seg=40)
    prim('sphere',(shx+.07,shy,shz),(.08,.08,.08),M['gold'],seg=16)
    for a in range(0,360,45):
        prim('cube',(shx+.045,shy+.22*math.cos(math.radians(a)),shz+.22*math.sin(math.radians(a))),(.015,.05,.015),M['iron'],rot=(a,0,0))
    new=[o for o in bpy.data.objects if o not in objs0]
    for o in new:
        if o.parent is None:
            o.parent=root
    WAR['root']=root;return root
# ---------------- RATO ----------------
def rat(px,py,rz,s=1.0):
    root=bpy.data.objects.new('rat',None);link(root);root.location=(px,py,0);root.rotation_euler=(0,0,math.radians(rz));objs0=set(bpy.data.objects)
    F=M['fur'];F2=M['fur2'];P=M['pink']
    # corpo agachado, pronto para o bote (olha para -X)
    b=prim('sphere',(.06,0,.3),(.42,.19,.19),F,rot=(0,-10,0),seg=32);prim('sphere',(.02,0,.22),(.36,.16,.12),F2,rot=(0,-10,0),seg=24)
    prim('sphere',(.34,0,.34),(.22,.17,.17),F,seg=24)                                  # quadril
    prim('sphere',(-.34,0,.4),(.2,.15,.15),F,seg=24)                                    # pescoço
    # cabeça e focinho
    prim('sphere',(-.52,0,.42),(.17,.125,.125),F,seg=28)
    prim('cone',(-.67,0,.4),(.1,.1,.2),F2,rot=(0,90,0),r=1,d=1,seg=20).scale=(.1,.1,.2)
    prim('sphere',(-.79,0,.4),(.03,.03,.03),P,seg=12)
    for sy in(-1,1):
        prim('sphere',(-.56,sy*.085,.47),(.035,.03,.035),M['eyer'],seg=12);prim('sphere',(-.575,sy*.095,.49),(.01,.01,.01),M['white'],seg=8)
        e=prim('cyl',(-.47,sy*.1,.58),(1,1,1),F,r=.08,d=.02,rot=(sy*-25,20,0),seg=24);e.scale=(1,1.0,1)
        prim('cyl',(-.475,sy*.098,.585),(1,1,1),P,r=.055,d=.022,rot=(sy*-25,20,0),seg=20)
        prim('cube',(-.74,sy*.02,.34),(.015,.012,.05),M['tooth'])
        # bigodes
        for k in(-1,0,1):
            c=bpy.data.curves.new('wh','CURVE');c.dimensions='3D';sp=c.splines.new('BEZIER');sp.bezier_points.add(1)
            sp.bezier_points[0].co=(-.74,sy*.04,.4+k*.015);sp.bezier_points[1].co=(-.86,sy*(.2+.04*abs(k)),.4+k*.05)
            for p in sp.bezier_points:p.handle_left_type=p.handle_right_type='VECTOR'
            c.bevel_depth=.003;o=bpy.data.objects.new('wh',c);link(o);o.data.materials.append(M['white'])
    # patas
    for sy in(-1,1):
        limb((-.3,sy*.13,.3),(-.46,sy*.15,.2),.045,.035,F);limb((-.46,sy*.15,.2),(-.58,sy*.16,.07),.035,.03,F2);prim('sphere',(-.6,sy*.16,.04),(.07,.04,.025),P,seg=12)
        for k in(-1,0,1):prim('cone',(-.65,sy*.16+k*.025,.035),(.012,.012,.03),M['tooth'],rot=(0,90,0),r=1,d=1,seg=6).scale=(.012,.012,.04)
        limb((.28,sy*.14,.34),(.4,sy*.16,.15),.08,.05,F);limb((.4,sy*.16,.15),(.28,sy*.16,.05),.05,.035,F2);prim('sphere',(.3,sy*.16,.04),(.1,.045,.025),P,seg=12)
    # cauda (curva)
    c=bpy.data.curves.new('tail','CURVE');c.dimensions='3D';sp=c.splines.new('BEZIER');sp.bezier_points.add(3)
    for p,co in zip(sp.bezier_points,[(.46,0,.32),(.8,.05,.15),(1.05,-.25,.1),(1.35,-.15,.35)]):
        p.co=co;p.handle_left_type=p.handle_right_type='AUTO'
    c.bevel_depth=.028;c.use_fill_caps=True;o=bpy.data.objects.new('tail',c);link(o);o.data.materials.append(P)
    # trapo/cinto improvisado
    prim('torus',(.0,0,.3),(1,1,1),M['leather'],r=.17,r2=.02,rot=(0,80,0),seg=24).scale=(1,1.1,1)
    new=[o for o in bpy.data.objects if o not in objs0]
    for o in new:
        if o.parent is None:
            o.parent=root
    root.scale=(s,s,s);return root
import os

# ================= PERSONAGENS EM PIXEL ART (sprites do jogo) NO CENÁRIO 3D (estilo HD-2D) =================
SPR={}
CHARS_DIR='/home/user/neon-wars/lendas-de-taverna/mmo/assets/chars/'
PXW=1.3/46.0      # unidades de mundo por pixel do sprite (herói de 46 px = 1,3 de altura)
def sprite_plane(name,png,cell,cols,rows,ax,ay,parent,flip=False,tint=None):
    im=bpy.data.images.load(CHARS_DIR+png);im.colorspace_settings.name='sRGB'
    bm=bmesh.new();x0=-ax*PXW;x1=(cell-ax)*PXW;zb=-(cell-ay)*PXW;zt=ay*PXW
    if flip:x0,x1=-x1,-x0
    vs=[bm.verts.new((x0,0,zb)),bm.verts.new((x1,0,zb)),bm.verts.new((x1,0,zt)),bm.verts.new((x0,0,zt))]
    f=bm.faces.new(vs);uv=bm.loops.layers.uv.new()
    uvs=[(0,0),(1,0),(1,1),(0,1)]
    if flip:uvs=[(1,0),(0,0),(0,1),(1,1)]
    for l,u in zip(f.loops,uvs):l[uv].uv=u
    me=bpy.data.meshes.new(name);bm.to_mesh(me);bm.free()
    o=bpy.data.objects.new(name,me);link(o);o.parent=parent
    m=bpy.data.materials.new(name);m.use_nodes=True;t=m.node_tree;N=t.nodes;L=t.links
    for n in list(N):N.remove(n)
    tc=N.new('ShaderNodeTexCoord');mp=N.new('ShaderNodeMapping');mp.inputs['Scale'].default_value=(1/cols,1/rows,1)
    tx=N.new('ShaderNodeTexImage');tx.image=im;tx.interpolation='Closest';tx.extension='CLIP'
    L.new(tc.outputs['UV'],mp.inputs['Vector']);L.new(mp.outputs['Vector'],tx.inputs['Vector'])
    fl=N.new('ShaderNodeValue');fl.outputs[0].default_value=0.0                       # clarão branco (dano)
    base=tx.outputs['Color']
    if tint:
        tm=N.new('ShaderNodeMix');tm.data_type='RGBA';tm.blend_type='MULTIPLY';tm.inputs[0].default_value=1.0;L.new(tx.outputs['Color'],tm.inputs[6]);tm.inputs[7].default_value=(*[c**2.2 for c in tint],1);base=tm.outputs[2]
    mixc=N.new('ShaderNodeMix');mixc.data_type='RGBA';L.new(fl.outputs[0],mixc.inputs[0]);L.new(base,mixc.inputs[6]);mixc.inputs[7].default_value=(1,1,1,1)
    df=N.new('ShaderNodeBsdfDiffuse');L.new(mixc.outputs[2],df.inputs['Color'])
    em=N.new('ShaderNodeEmission');L.new(mixc.outputs[2],em.inputs['Color']);em.inputs['Strength'].default_value=.38
    fe=N.new('ShaderNodeMath');fe.operation='MAXIMUM';L.new(fl.outputs[0],fe.inputs[0]);fe.inputs[1].default_value=0
    ad=N.new('ShaderNodeAddShader');L.new(df.outputs[0],ad.inputs[0]);L.new(em.outputs[0],ad.inputs[1])
    vis=N.new('ShaderNodeValue');vis.outputs[0].default_value=1.0
    af=N.new('ShaderNodeMath');af.operation='MULTIPLY';L.new(tx.outputs['Alpha'],af.inputs[0]);L.new(vis.outputs[0],af.inputs[1])
    tr=N.new('ShaderNodeBsdfTransparent');mx=N.new('ShaderNodeMixShader');L.new(af.outputs[0],mx.inputs[0]);L.new(tr.outputs[0],mx.inputs[1]);L.new(ad.outputs[0],mx.inputs[2])
    out=N.new('ShaderNodeOutputMaterial');L.new(mx.outputs[0],out.inputs['Surface']);o.data.materials.append(m)
    SPR[name]=dict(o=o,mp=mp,cols=cols,rows=rows,fl=fl,vis=vis,m=m)
    return o
def spr_frame(name,f,col,row):
    d=SPR[name];mp=d['mp'];mp.inputs['Location'].default_value=(col/d['cols'],1-(row+1)/d['rows'],0)
    mp.inputs['Location'].keyframe_insert('default_value',frame=f)
def spr_show(name,f,on):
    o=SPR[name]['o'];o.hide_render=not on;o.keyframe_insert('hide_render',frame=f)
def spr_val(name,key,f,v):
    n=SPR[name][key].outputs[0];n.default_value=v;n.keyframe_insert('default_value',frame=f)
def blob(parent,rx,ry,al=.5):
    bm=bmesh.new();vs=[bm.verts.new((-rx,-ry,.014)),bm.verts.new((rx,-ry,.014)),bm.verts.new((rx,ry,.014)),bm.verts.new((-rx,ry,.014))];f=bm.faces.new(vs);uv=bm.loops.layers.uv.new()
    for l,u in zip(f.loops,[(0,0),(1,0),(1,1),(0,1)]):l[uv].uv=u
    me=bpy.data.meshes.new('blob');bm.to_mesh(me);bm.free();o=bpy.data.objects.new('blob',me);link(o);o.parent=parent
    m=bpy.data.materials.new('blob');m.use_nodes=True;t=m.node_tree;N=t.nodes;L=t.links
    for n in list(N):N.remove(n)
    tc=N.new('ShaderNodeTexCoord');gr=N.new('ShaderNodeTexGradient');gr.gradient_type='SPHERICAL'
    mp=N.new('ShaderNodeMapping');mp.inputs['Location'].default_value=(-.5,-.5,0);L.new(tc.outputs['UV'],mp.inputs['Vector']);L.new(mp.outputs[0],gr.inputs[0])
    cr=N.new('ShaderNodeValToRGB');cr.color_ramp.elements[0].color=(al,al,al,1);cr.color_ramp.elements[0].position=0;cr.color_ramp.elements[1].color=(0,0,0,1);cr.color_ramp.elements[1].position=.5
    L.new(gr.outputs[0],cr.inputs[0]);bs=N.new('ShaderNodeBsdfDiffuse');bs.inputs['Color'].default_value=(0,0,0,1)
    tr=N.new('ShaderNodeBsdfTransparent');mx=N.new('ShaderNodeMixShader');L.new(cr.outputs[0],mx.inputs[0]);L.new(tr.outputs[0],mx.inputs[1]);L.new(bs.outputs[0],mx.inputs[2])
    out=N.new('ShaderNodeOutputMaterial');L.new(mx.outputs[0],out.inputs['Surface']);o.data.materials.append(m);return o
def build_sprites():
    hero=bpy.data.objects.new('hero',None);link(hero);hero.location=(-1.3,-.5,0)
    rat_=bpy.data.objects.new('ratroot',None);link(rat_);rat_.location=(4.6,-.35,0)
    SPR['_hero']=hero;SPR['_rat']=rat_
    # âncoras: x,y do pé na folha de caminhada (como no jogo); folhas de ataque têm célula maior (+ (cell-64)/2)
    hax,hay=28,61;rax,ray=27,61
    sprite_plane('h_idle','guerreiro__walk.png',64,9,4,hax,hay,hero)
    sprite_plane('h_slash','guerreiro__slash.png',192,6,4,hax+64,hay+64,hero)
    sprite_plane('r_walk','rato__walk.png',64,9,4,rax,ray,rat_,tint=(.62,.5,.42))
    sprite_plane('r_slash','rato__slash.png',64,6,4,rax,ray,rat_,tint=(.62,.5,.42))
    sprite_plane('r_hurt','rato__hurt.png',64,6,1,rax,ray,rat_,tint=(.62,.5,.42))
    blob(hero,.5,.28,.55);blob(rat_,.55,.3,.55)
    return hero,rat_
CH=os.environ.get('CHARS','3d')
if CH=='3d':
    warrior(-1.45,-.5,-28)
    RATROOT=rat(1.5,-.15,22,1.3)
else:
    HERO,RATR=build_sprites()
# ---------------- ambiente e luz ----------------
w=bpy.data.worlds.new('w');sc.world=w;w.use_nodes=True;bg=w.node_tree.nodes['Background'];bg.inputs[0].default_value=(.015,.02,.035,1);bg.inputs[1].default_value=1.0
def area(loc,rot,e,col,size):
    l=bpy.data.lights.new('a','AREA');l.energy=e;l.color=col;l.size=size;o=bpy.data.objects.new('a',l);link(o);o.location=loc;o.rotation_euler=[math.radians(a) for a in rot];return o
area((-1,-3,7.5),(20,0,0),260,(.5,.64,1.0),9)    # luz fria de cima (preenchimento)
area((6,-7,4),(70,0,35),300,(1,.78,.6),5)          # recorte quente frontal
# névoa volumétrica leve
vol=prim('cube',(0,0,2.2),(ROOM_X*2,ROOM_Y*2,4.4),None)
if os.environ.get('VOL','1')=='0':
    bpy.data.objects.remove(vol)
else:
    vm=bpy.data.materials.new('vol');vm.use_nodes=True;nt=vm.node_tree
    for n in list(nt.nodes):nt.nodes.remove(n)
    pv=nt.nodes.new('ShaderNodeVolumePrincipled');pv.inputs['Density'].default_value=.012;pv.inputs['Color'].default_value=(.6,.7,.9,1);pv.inputs['Anisotropy'].default_value=.45
    out=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(pv.outputs[0],out.inputs['Volume']);vol.data.materials.append(vm)
    vol.display_type='WIRE'
# ---------------- câmera ----------------
cam=bpy.data.cameras.new('cam');co=bpy.data.objects.new('cam',cam);link(co);sc.camera=co
def look(co,pos,tgt,lens):
    co.location=pos;d=Vector(tgt)-Vector(pos);co.rotation_euler=d.to_track_quat('-Z','Y').to_euler();co.data.lens=lens
if VIEW=='wide':
    look(co,(10.5,-12.5,9.0),(-0.3,.6,.9),52)
else:
    look(co,(.6,-6.3,2.6),(0,-.1,.8),44);co.data.dof.use_dof=True;co.data.dof.focus_distance=(Vector((.6,-6.3,2.6))-Vector((0,-.3,.8))).length;co.data.dof.aperture_fstop=4.0

def kf(o,f,loc=None,rot=None,scl=None):
    if loc is not None:o.location=loc;o.keyframe_insert('location',frame=f)
    if rot is not None:o.rotation_euler=[math.radians(a) for a in rot];o.keyframe_insert('rotation_euler',frame=f)
    if scl is not None:o.scale=scl;o.keyframe_insert('scale',frame=f)
def fcs(act):
    try:return list(act.fcurves)
    except AttributeError:
        out=[]
        for l in act.layers:
            for st in l.strips:
                for cb in st.channelbags:out+=list(cb.fcurves)
        return out
def ease(o,mode='BEZIER'):
    if o.animation_data and o.animation_data.action:
        for fc in fcs(o.animation_data.action):
            for k in fc.keyframe_points:k.interpolation=mode

def animate_sprites():
    sc.render.fps=24;hero=SPR['_hero'];rr=SPR['_rat'];END=156
    # --- guerreiro: parado (respirando) -> golpe -> parado
    spr_show('h_slash',1,False);spr_show('h_idle',1,True)
    for f in range(1,END+1,12):
        kf(hero,f,(-1.3,-.5,.014*((f//12)%2)))
    kf(hero,64,(-1.3,-.5,0));kf(hero,70,(-1.05,-.5,0));kf(hero,84,(-1.05,-.5,0));kf(hero,100,(-1.3,-.5,0))
    spr_frame('h_idle',1,0,3);spr_frame('h_slash',1,0,3)
    spr_show('h_idle',66,False);spr_show('h_slash',66,True)
    for i in range(6):spr_frame('h_slash',66+i*2,i,3)
    spr_show('h_slash',80,False);spr_show('h_idle',80,True)
    # --- rato: anda, ataca, leva o golpe, some
    for n in('r_walk','r_slash','r_hurt'):spr_show(n,1,n=='r_walk')
    for f in range(1,61,3):spr_frame('r_walk',f,1+((f//3)%8),1)
    kf(rr,1,(4.8,-.35,0));kf(rr,60,(2.0,-.35,0));kf(rr,62,(2.0,-.35,0))
    spr_show('r_walk',62,False);spr_show('r_slash',62,True)
    for i in range(6):spr_frame('r_slash',62+i*2,i,1)
    kf(rr,68,(1.55,-.35,0));kf(rr,72,(1.3,-.35,0))          # bote para a frente
    spr_show('r_slash',73,False);spr_show('r_hurt',73,True)  # leva a espadada
    for i,c in enumerate((0,1,2,2,2,2)):spr_frame('r_hurt',73+i*3,c,0)
    kf(rr,73,(1.3,-.35,0));kf(rr,91,(2.7,-.35,0));kf(rr,100,(2.9,-.35,0))
    spr_val('r_hurt','fl',73,1.0);spr_val('r_hurt','fl',78,0.0)
    spr_val('r_hurt','vis',96,1.0);spr_val('r_hurt','vis',118,0.0)
    # --- tochas
    for o in bpy.data.objects:
        if o.type=='LIGHT' and o.data.type=='POINT' and o.name.startswith('t'):
            e=o.data.energy;o.data.keyframe_insert('energy',frame=1)
            fc=fcs(o.data.animation_data.action)[0];m=fc.modifiers.new('NOISE');m.scale=3+random.random()*3;m.strength=e*.35;m.phase=random.random()*50
    # --- câmera: aproxima, treme no golpe, sobe e recua
    tg=bpy.data.objects.new('tg',None);link(tg)
    kf(tg,1,(.1,-.3,.9));kf(tg,70,(.45,-.3,.85));kf(tg,100,(.6,-.3,.85));kf(tg,END,(.3,-.2,.9))
    kf(co,1,(.3,-8.2,3.6));kf(co,60,(.5,-7.0,3.0));kf(co,70,(.5,-7.0,3.0))
    for f,dx,dz in((71,.08,.05),(73,-.07,-.05),(75,.05,.03),(77,0,0)):kf(co,f,(.5+dx,-7.0,3.0+dz))
    kf(co,110,(.8,-7.2,3.1));kf(co,END,(2.4,-8.6,4.2))
    for f,l in((1,40),(100,40),(END,38)):cam.lens=l;cam.keyframe_insert('lens',frame=f)
    tc=co.constraints.new('TRACK_TO');tc.target=tg;tc.track_axis='TRACK_NEGATIVE_Z';tc.up_axis='UP_Y'
    cam.dof.use_dof=True;cam.dof.focus_object=tg;cam.dof.aperture_fstop=2.4
    # keyframes de sprite e visibilidade sem interpolação
    for n,d in SPR.items():
        if n.startswith('_'):continue
        for idn in(d['m'].node_tree,d['o']):
            if idn.animation_data and idn.animation_data.action:
                for fc in fcs(idn.animation_data.action):
                    for k in fc.keyframe_points:
                        if 'Location' in fc.data_path or 'hide_render' in fc.data_path or 'default_value' in fc.data_path and 'fl' in fc.data_path:k.interpolation='CONSTANT'
    for o in(tg,co,hero,rr):ease(o)
    sc.frame_start=1;sc.frame_end=END
def animate():
    if CH=='sprites':return animate_sprites()
    sc.render.fps=24;wr=WAR['root'];arm=WAR['arm'];rt=RATROOT
    wx,wy=-1.45,-.5;wrz=-28
    # --- guerreiro: respira, ergue a espada, golpeia, comemora
    for f in range(1,217,12):kf(wr,f,(wx,wy,.012*(1 if (f//12)%2 else 0)),(0,0,wrz))
    kf(wr,84,(wx,wy,0),(0,0,wrz));kf(wr,90,(wx+.28,wy+.04,0),(0,0,wrz+10));kf(wr,98,(wx+.3,wy+.05,0),(0,0,wrz+12));kf(wr,132,(wx,wy,0),(0,0,wrz))
    for f,a in((1,0),(58,0),(78,-48),(82,-52),(89,38),(97,62),(112,40),(132,10),(150,-34),(190,-34),(216,-20)):kf(arm,f,None,(-6,a,0))
    # --- rato: rasteja, agacha, salta, é lançado para trás e cai
    pts=[(1,4.4,0),(10,4.0,.05),(18,3.7,0),(26,3.4,.05),(34,3.1,0),(42,2.85,.05),(50,2.6,0),(58,2.4,.05),(66,2.3,0)]
    for f,x,z in pts:kf(rt,f,(x,-.15,z),(0,0,22),(1.3,1.3,1.3))
    kf(rt,74,(2.3,-.15,0),(0,0,22),(1.34,1.3,1.0))                     # agacha
    kf(rt,78,(2.3,-.15,0),(0,0,22),(1.34,1.3,.95))
    kf(rt,84,(1.4,-.15,.95),(0,14,22),(1.3,1.3,1.3))                   # salto
    kf(rt,90,(.4,-.15,.6),(0,-22,22),(1.3,1.3,1.3))                 # contato com a espada
    kf(rt,102,(1.9,-.15,1.0),(90,10,22),(1.3,1.3,1.3))                 # arremessado
    kf(rt,112,(2.5,-.1,.26),(90,0,35),(1.3,1.3,1.3))                   # cai de lado
    kf(rt,118,(2.6,-.1,.25),(90,0,35),(1.3,1.3,1.3))
    kf(rt,216,(2.6,-.1,.25),(90,0,35),(1.3,1.3,1.3))
    for o in(wr,arm,rt):ease(o)
    # --- tochas tremulando
    for o in bpy.data.objects:
        if o.type=='LIGHT' and o.data.type=='POINT' and o.name.startswith('t'):
            e=o.data.energy;o.data.keyframe_insert('energy',frame=1)
            fc=fcs(o.data.animation_data.action)[0];m=fc.modifiers.new('NOISE');m.scale=3+random.random()*3;m.strength=e*.35;m.phase=random.random()*50
    # --- câmera: aproxima, acompanha o golpe e recua para a vista geral
    tg=bpy.data.objects.new('tg',None);link(tg);cam_=co
    kf(tg,1,(0,-.1,.8));kf(tg,84,(.2,-.2,.9));kf(tg,100,(.5,-.2,.8));kf(tg,150,(.2,-.1,.8));kf(tg,216,(-.3,.6,.9))
    kf(co,1,(.6,-6.3,2.6));kf(co,70,(.1,-5.2,2.0));kf(co,100,(.8,-5.0,1.9));kf(co,150,(1.2,-5.6,2.2));kf(co,216,(10.5,-12.5,9.0))
    for f,l in((1,44),(100,40),(150,42),(216,52)):cam.lens=l;cam.keyframe_insert('lens',frame=f)
    tc=co.constraints.new('TRACK_TO');tc.target=tg;tc.track_axis='TRACK_NEGATIVE_Z';tc.up_axis='UP_Y'
    cam.dof.focus_object=tg;cam.dof.use_dof=True;cam.dof.aperture_fstop=3.2
    for o in(tg,co):ease(o)
    sc.frame_start=1;sc.frame_end=216
if VIEW=='anim':
    animate()
    FS=int(sys.argv[5]) if len(sys.argv)>5 else 1;FE=int(sys.argv[6]) if len(sys.argv)>6 else sc.frame_end
    import os;os.makedirs(OUT,exist_ok=True)
    for f in range(FS,FE+1):
        sc.frame_set(f);R.filepath=f'{OUT}/f{f:04d}.png';bpy.ops.render.render(write_still=True)
    print('ok anim',FS,FE)
else:
    R.filepath=OUT
    bpy.ops.render.render(write_still=True)
    print('ok',OUT)
