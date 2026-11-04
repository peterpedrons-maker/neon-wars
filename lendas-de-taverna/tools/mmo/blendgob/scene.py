"""Cena e materiais para o goblin em Blender (bpy): câmera ortográfica, luzes presas à câmera (iluminação igual em todas as vistas) e materiais procedurais."""
import bpy,math
from mathutils import Vector,Matrix
def lin(c):return tuple(x**2.2 for x in c)
def reset(res=384,samples=24):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.device='CPU';sc.cycles.samples=samples;sc.cycles.use_denoising=True
    try:sc.cycles.denoiser='OPENIMAGEDENOISE'
    except:pass
    sc.render.resolution_x=sc.render.resolution_y=res;sc.render.film_transparent=True;sc.render.image_settings.file_format='PNG';sc.render.image_settings.color_mode='RGBA'
    sc.view_settings.view_transform='Filmic' if False else 'Standard'
    cam=bpy.data.cameras.new('c');cam.type='ORTHO';cam.ortho_scale=2.0;co=bpy.data.objects.new('c',cam);sc.collection.objects.link(co);sc.camera=co
    def sun(e,rx,rz,col,ang):
        s=bpy.data.lights.new('s','SUN');s.energy=e;s.angle=math.radians(ang);s.color=col;o=bpy.data.objects.new('s',s);sc.collection.objects.link(o);o.parent=co;o.rotation_euler=(math.radians(rx),0,math.radians(rz))
    sun(3.6,-50,-35,(1,.93,.82),18)      # principal: cima-esquerda
    sun(1.1,-70,150,(.55,.65,1),30)      # contraluz frio
    sun(.5,-20,40,(1,.8,.7),40)          # preenchimento
    w=bpy.data.worlds.new('w');sc.world=w;w.use_nodes=True;n=w.node_tree.nodes['Background'];n.inputs[0].default_value=(.16,.17,.24,1);n.inputs[1].default_value=1.0
    return co
def set_view(co,view,target=(0,0,.55),el=26,dist=8):
    az={'front':Vector((0,1,0)),'side':Vector((1,0,0)),'back':Vector((0,-1,0))}[view]
    t=Vector(target);pos=t+az*dist*math.cos(math.radians(el))+Vector((0,0,dist*math.sin(math.radians(el))))
    co.location=pos;d=t-pos;co.rotation_euler=d.to_track_quat('-Z','Y').to_euler()
def _nodes(m):m.use_nodes=True;return m.node_tree,m.node_tree.nodes['Principled BSDF']
def mat_simple(name,col,rough=.6,metal=0,emit=0,spec=.4):
    m=bpy.data.materials.new(name);t,b=_nodes(m);b.inputs['Base Color'].default_value=(*lin(col),1);b.inputs['Roughness'].default_value=rough;b.inputs['Metallic'].default_value=metal
    for k in('Specular IOR Level','Specular'):
        if k in b.inputs:b.inputs[k].default_value=spec
    if emit:b.inputs['Emission Color'].default_value=(*lin(col),1);b.inputs['Emission Strength'].default_value=emit
    return m
def mat_noise(name,c0,c1,rough=.6,metal=0,bump=.4,scale=30,sss=0,detail=10,rough2=None):
    """cor que varia por ruído entre c0 e c1 + relevo fino (poros, couro, riscos)"""
    m=bpy.data.materials.new(name);t,b=_nodes(m);N=t.nodes;L=t.links
    tc=N.new('ShaderNodeTexCoord');mp=N.new('ShaderNodeMapping');mp.inputs['Scale'].default_value=(1,1,1)
    ns=N.new('ShaderNodeTexNoise');ns.inputs['Scale'].default_value=scale;ns.inputs['Detail'].default_value=detail
    ns2=N.new('ShaderNodeTexNoise');ns2.inputs['Scale'].default_value=scale*.12;ns2.inputs['Detail'].default_value=3
    L.new(tc.outputs['Object'],mp.inputs[0]);L.new(mp.outputs[0],ns.inputs['Vector']);L.new(mp.outputs[0],ns2.inputs['Vector'])
    cr=N.new('ShaderNodeValToRGB');cr.color_ramp.elements[0].color=(*lin(c0),1);cr.color_ramp.elements[1].color=(*lin(c1),1)
    mix=N.new('ShaderNodeMath');mix.operation='MULTIPLY_ADD';mix.inputs[1].default_value=.6;mix.inputs[2].default_value=.2
    L.new(ns2.outputs['Fac'],mix.inputs[0]);L.new(mix.outputs[0],cr.inputs['Fac']);L.new(cr.outputs['Color'],b.inputs['Base Color'])
    bp=N.new('ShaderNodeBump');bp.inputs['Strength'].default_value=bump;bp.inputs['Distance'].default_value=.02;L.new(ns.outputs['Fac'],bp.inputs['Height']);L.new(bp.outputs['Normal'],b.inputs['Normal'])
    b.inputs['Roughness'].default_value=rough;b.inputs['Metallic'].default_value=metal
    if sss:
        for k in('Subsurface Weight','Subsurface'):
            if k in b.inputs:b.inputs[k].default_value=sss
        if 'Subsurface Radius' in b.inputs:b.inputs['Subsurface Radius'].default_value=(.8,.35,.2)
    if rough2 is not None:
        rr=N.new('ShaderNodeMapRange');rr.inputs['To Min'].default_value=rough;rr.inputs['To Max'].default_value=rough2;L.new(ns.outputs['Fac'],rr.inputs['Value']);L.new(rr.outputs['Result'],b.inputs['Roughness'])
    return m
def sphere(m,seg=32,ring=16):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg,ring_count=ring,radius=1);o=bpy.context.object;o.data.materials.append(m);bpy.ops.object.shade_smooth();return o
def cone(m,v=20,r1=1,r2=.5):
    bpy.ops.mesh.primitive_cone_add(vertices=v,radius1=r1,radius2=r2,depth=1);o=bpy.context.object;o.data.materials.append(m);bpy.ops.object.shade_smooth();return o
def curve(name,m,pts=6,bev=.5,res=6):
    cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.resolution_u=res;cu.bevel_depth=bev;cu.bevel_resolution=6;cu.use_fill_caps=True
    sp=cu.splines.new('NURBS');sp.points.add(pts-1);sp.use_endpoint_u=True;sp.order_u=4
    o=bpy.data.objects.new(name,cu);bpy.context.scene.collection.objects.link(o);o.data.materials.append(m);return o
def set_curve(o,P,R):
    sp=o.data.splines[0]
    for p,(c,r) in zip(sp.points,zip(P,R)):p.co=(c[0],c[1],c[2],1);p.radius=r
def subsurf(o,l=2):
    md=o.modifiers.new('s','SUBSURF');md.levels=l;md.render_levels=l;return o
def render(path):
    bpy.context.scene.render.filepath=path;bpy.ops.render.render(write_still=True)
