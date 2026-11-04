"""Etapa 2 (Blender): importa a malha do casco com cores por vértice e renderiza as vistas para comparar com a folha."""
import sys,os,json,math
import numpy as np,bpy
from mathutils import Vector
S=1.2/700.0
def load_mesh(npz,name='body'):
    d=np.load(npz);v=d['verts']*S;f=d['faces'];c=d['colors'].astype(np.float32)/255.0
    me=bpy.data.meshes.new(name);me.vertices.add(len(v));me.vertices.foreach_set('co',v.reshape(-1).astype(np.float32))
    me.loops.add(len(f)*3);me.polygons.add(len(f));me.loops.foreach_set('vertex_index',f.reshape(-1));me.polygons.foreach_set('loop_start',np.arange(0,len(f)*3,3,dtype=np.int32));me.polygons.foreach_set('loop_total',np.full(len(f),3,dtype=np.int32))
    me.update();me.validate()
    ca=me.color_attributes.new('Col','FLOAT_COLOR','POINT');rgba=np.concatenate([c**2.2,np.ones((len(c),1),np.float32)],1);ca.data.foreach_set('color',rgba.reshape(-1))
    for p in me.polygons:p.use_smooth=True
    o=bpy.data.objects.new(name,me);bpy.context.scene.collection.objects.link(o);return o,d
def paint_mat(name='paint',emit=.55):
    m=bpy.data.materials.new(name);m.use_nodes=True;t=m.node_tree;b=t.nodes['Principled BSDF'];a=t.nodes.new('ShaderNodeVertexColor');a.layer_name='Col'
    t.links.new(a.outputs['Color'],b.inputs['Base Color']);t.links.new(a.outputs['Color'],b.inputs['Emission Color']);b.inputs['Emission Strength'].default_value=emit;b.inputs['Roughness'].default_value=.7
    for k in('Specular IOR Level','Specular'):
        if k in b.inputs:b.inputs[k].default_value=.2
    return m
if __name__=='__main__':
    sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','blendgob'))
    from scene import reset,set_view,render
    co=reset(512,16);co.data.ortho_scale=1.6
    o,_=load_mesh(sys.argv[1]);o.data.materials.append(paint_mat())
    for v in('front','side','back'):
        set_view(co,v,target=(0,0.0,.6));render(f'{sys.argv[2]}_{v}.png')
