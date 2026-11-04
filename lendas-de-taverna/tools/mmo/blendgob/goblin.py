"""Goblin orgânico em Blender: corpo e cabeça em metaballs (massa única e suave), membros em curvas afuniladas, armadura e arma modeladas."""
import sys,os,math
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from scene import *
import bmesh
co=reset(512 if len(sys.argv)>1 and sys.argv[1]=='head' else 384,20);co.data.ortho_scale=1.75
SKIN=mat_noise('skin',(.17,.30,.12),(.36,.50,.20),.52,0,.55,34,.12,12);SKIN2=mat_noise('skin2',(.13,.24,.10),(.28,.40,.16),.55,0,.5,34,.1,12)
LEAT=mat_noise('leat',(.16,.09,.05),(.34,.21,.10),.72,0,.9,70,0,6);CLOTH=mat_noise('cloth',(.07,.06,.12),(.18,.14,.26),.92,0,.7,120,0,4)
METAL=mat_noise('metal',(.18,.20,.26),(.50,.54,.62),.4,1,.35,18,0,10,rough2=.7);BONE=mat_noise('bone',(.62,.56,.40),(.86,.80,.62),.5,0,.3,25,0,6)
AMBER=mat_simple('amber',(.95,.62,.08),.18,0,.6);PUPIL=mat_simple('pupil',(.01,.01,.01),.3);MOUTH=mat_simple('mouth',(.35,.05,.07),.4);PINK=mat_noise('pink',(.55,.25,.25),(.75,.40,.38),.6,0,.3,40,.1,4)
sc=bpy.context.scene
def meta(name,mat,res=.012):
    mb=bpy.data.metaballs.new(name);mb.resolution=res*10;mb.render_resolution=res*7;mb.threshold=.55;o=bpy.data.objects.new(name,mb);sc.collection.objects.link(o);o.data.materials.append(mat);o.scale=(.1,.1,.1);return mb
def el(mb,r,sx=1,sy=1,sz=1,st=2.0):
    e=mb.elements.new(type='ELLIPSOID');e.radius=r*17;e.size_x=sx;e.size_y=sy;e.size_z=sz;e.stiffness=st;return e
MS=meta('skin',SKIN);ML=meta('leat',LEAT,.01)
E={}
for k,(r,sx,sy,sz) in dict(belly=(.15,1,.95,.9),chest=(.15,1.05,.9,1),pelv=(.12,1,.9,.8),hump=(.10,1,.9,.7),neck=(.07,1,1,1),
    skull=(.14,1,1.05,.95),snout=(.075,.9,1.5,.7),jaw=(.06,.9,1.1,.6),nose=(.045,.8,.9,.8),brL=(.04,.7,.8,.5),brR=(.04,.7,.8,.5),chkL=(.05,.8,.8,.7),chkR=(.05,.8,.8,.7),
    lidL=(.03,.9,.8,.45),lidR=(.03,.9,.8,.45),chin=(.04,.8,.8,.7)).items():E[k]=el(MS,r*(1.22 if k in('skull','snout','jaw','nose','brL','brR','chkL','chkR','lidL','lidR','chin') else 1),sx,sy,sz)
for k,(r,sx,sy,sz) in dict(vest=(.15,1.2,.6,1.15),vestb=(.12,1.1,.45,1.0)).items():E[k]=el(ML,r,sx,sy,sz)
def cyl_mat(m):return None
EYE=[(sphere(AMBER,24,12),sphere(PUPIL,12,6)) for _ in range(2)]
MOUTHO=sphere(MOUTH,16,8)
TUSK=[curve('tusk%d'%i,BONE,4,1.0) for i in range(2)]
LEG=[curve('leg%d'%i,CLOTH,6,1.0) for i in range(2)];ARM=[curve('arm%d'%i,SKIN,5,1.0) for i in range(2)]
BRACER=[cone(LEAT,20,1,1) for _ in range(2)];KNEE=[sphere(METAL,16,8) for _ in range(2)]
BOOT=[sphere(LEAT,20,10) for _ in range(2)];BOOT2=[sphere(LEAT,16,8) for _ in range(2)]
FIST=[sphere(SKIN,18,9) for _ in range(2)];CLAWS=[[cone(BONE,8,1,.05) for _ in range(3)] for _ in range(2)]
PAULD=[sphere(METAL,20,10) for _ in range(2)];SPIKE=[cone(BONE,10,1,.05) for _ in range(2)]
EAR=[cone(SKIN2,18,1,.04) for _ in range(2)];EARI=[cone(PINK,14,1,.04) for _ in range(2)]
# elmo: meia esfera de ferro, aro e chifre
bm=bmesh.new();bmesh.ops.create_uvsphere(bm,u_segments=32,v_segments=16,radius=1);bmesh.ops.delete(bm,geom=[v for v in bm.verts if v.co.z<-.02],context='VERTS')
hm=bpy.data.meshes.new('helm');bm.to_mesh(hm);bm.free();HELM=bpy.data.objects.new('helm',hm);sc.collection.objects.link(HELM);HELM.data.materials.append(METAL)
md=HELM.modifiers.new('sol','SOLIDIFY');md.thickness=.03;md.offset=-1
for p in HELM.data.polygons:p.use_smooth=True
bpy.context.view_layer.objects.active=HELM
RIM=bpy.data.objects.new('rim',bpy.data.meshes.new('rim'));
bpy.ops.mesh.primitive_torus_add(major_radius=1,minor_radius=.07);RIM=bpy.context.object;RIM.data.materials.append(LEAT);bpy.ops.object.shade_smooth()
HORN=curve('horn',BONE,4,1.0)
BELT=None
bpy.ops.mesh.primitive_torus_add(major_radius=1,minor_radius=.14);BELT=bpy.context.object;BELT.data.materials.append(LEAT);bpy.ops.object.shade_smooth()
BUCK=sphere(BONE,16,8);FLAP=[sphere(CLOTH,16,8) for _ in range(2)]
# cutelo: contorno extrudado com chanfro
bm=bmesh.new()
outline=[(.10,.016),(.14,.05),(.30,.075),(.42,.07),(.455,.03),(.46,-.12),(.42,-.17),(.35,-.16),(.31,-.19),(.24,-.15),(.18,-.12),(.10,-.03)]
vs=[bm.verts.new((x,y,0)) for x,y in outline];f=bm.faces.new(vs);r=bmesh.ops.extrude_face_region(bm,geom=[f]);
for v in [e for e in r['geom'] if isinstance(e,bmesh.types.BMVert)]:v.co.z=.016
for v in vs:v.co.z=-.016
HEADSHOT=0
cm=bpy.data.meshes.new('cl');bm.normal_update();bm.to_mesh(cm);bm.free();CLEAVER=bpy.data.objects.new('cl',cm);sc.collection.objects.link(CLEAVER);CLEAVER.data.materials.append(METAL)
md=CLEAVER.modifiers.new('bev','BEVEL');md.width=.006;md.segments=2;CLEAVER.modifiers.new('sub','SUBSURF').levels=1
for p in CLEAVER.data.polygons:p.use_smooth=True
HANDLE=curve('handle',LEAT,3,1.0);GUARD=cone(METAL,12,1,1)
def orient(o,a,b,thick=1.0,length=None):
    d=Vector(b)-Vector(a);o.location=(Vector(a)+Vector(b))/2;o.rotation_mode='QUATERNION';o.rotation_quaternion=d.to_track_quat('Z','Y');L=d.length;o.scale=(thick,thick,L if length is None else length)
def basis(o,loc,x,y):
    x=Vector(x).normalized();y=Vector(y);y=(y-x*y.dot(x)).normalized();z=x.cross(y);m=Matrix(((x.x,y.x,z.x,0),(x.y,y.y,z.y,0),(x.z,y.z,z.z,0),(0,0,0,1)));m.translation=Vector(loc);o.matrix_world=m
def rx(v,a):c,s=math.cos(a),math.sin(a);return Vector((v[0],v[1]*c+v[2]*s,-v[1]*s+v[2]*c))
def fdir(a):return Vector((0,math.sin(math.radians(a)),-math.cos(math.radians(a))))
def ik2(p,a,b):return None
def pose(P):
    g=P.get;bob=g('bob',0)*.011;cr_=g('crouch',0)*.011;lean=math.radians(g('lean',0))*1.4
    H=Vector((g('sway',0)*.012,g('fwd',0),.585+bob-cr_));T=lambda v:H+rx(v,lean)
    TL=T((0,.02,.0))
    E['pelv'].co=T((0,0.0,.03));E['belly'].co=T((0,.045,.135));E['chest'].co=T((0,.012,.285));E['hump'].co=T((0,-.065,.37));E['neck'].co=T((0,.02,.43))
    E['vest'].co=T((0,.095,.265));E['vestb'].co=T((0,-.01,.28))
    # cabeça
    hp=math.radians(g('hy',0)*-6+g('open',0)*-6)+lean*-.5;HS=1.22;N=T((0,.03,.44));HC=lambda v:N+rx(Vector(v)*HS,hp)
    hc=HC((0,.085,.115));op=g('open',0)
    E['skull'].co=hc;E['snout'].co=HC((0,.205,.08));E['jaw'].co=HC((0,.185,.02-.05*op));E['nose'].co=HC((0,.285,.105));E['chin'].co=HC((0,.205,-.01-.06*op))
    E['brL'].co=HC((-.062,.18,.168));E['brR'].co=HC((.062,.18,.168));E['chkL'].co=HC((-.085,.15,.075));E['chkR'].co=HC((.085,.15,.075))
    E['lidL'].co=HC((-.064,.185,.153));E['lidR'].co=HC((.064,.185,.153))
    for i,sg in enumerate((-1,1)):
        w,pu=EYE[i];w.location=HC((sg*.064,.185,.115));w.scale=(.041,.043,.041);pu.location=HC((sg*.064,.222,.115));pu.scale=(.01,.006,.032)
    MOUTHO.location=HC((0,.17,.03-.02*op));MOUTHO.scale=(.05,.09,.035+.02*op)
    for i,sg in enumerate((-1,1)):
        pts=[HC((sg*.05,.2,.0-.05*op)),HC((sg*.058,.215,.03-.04*op)),HC((sg*.055,.225,.07-.03*op)),HC((sg*.05,.222,.105-.03*op))];set_curve(TUSK[i],pts,[.02,.017,.011,.003]);TUSK[i].data.bevel_depth=1.0
        a=HC((sg*.12,.07,.12));d=Vector((sg*.8,-.55,.38+.05*math.sin(g('csway',0))));d.normalize();b=a+d*.25
        orient(EAR[i],a,b,1,.25);EAR[i].scale=(.05,.012,.25);EARI[i].scale=(.03,.006,.2);orient(EARI[i],a+d*.015+Vector((0,0,0)),b-d*.01,1,.2);EARI[i].scale=(.03,.006,.2)
        for ob in(EAR[i],EARI[i]):
            ob.rotation_mode='QUATERNION';q=d.to_track_quat('Z','Y');ob.rotation_quaternion=q
    # elmo
    HELM.location=HC((0,.05,.185));HELM.scale=(.19,.2,.14);HELM.rotation_euler=(hp-.05,0,0)
    RIM.location=HC((0,.055,.165));RIM.rotation_euler=(hp-.05,0,0);RIM.scale=(.186,.196,.045)
    set_curve(HORN,[HC((0,.0,.285)),HC((0,-.02,.335)),HC((0,-.065,.36)),HC((0,-.11,.35))],[.036,.029,.016,.004]);HORN.data.bevel_depth=1.0
    # cinto, fivela, tanga
    BELT.location=T((0,.02,.045));BELT.scale=(.125,.115,.05);BELT.rotation_euler=(lean,0,0);BUCK.location=T((0,.137,.047));BUCK.scale=(.03,.014,.03)
    sw=g('csway',0)*.03
    FLAP[0].location=T((0,.12,-.045))+Vector((0,sw,0));FLAP[0].scale=(.09,.014,.105);FLAP[0].rotation_euler=(lean+g('csway',0)*.1,0,0)
    FLAP[1].location=T((0,-.08,-.04))+Vector((0,-sw,0));FLAP[1].scale=(.09,.014,.1);FLAP[1].rotation_euler=(lean-g('csway',0)*.1,0,0)
    # pernas
    for i,sg in enumerate((1,-1)):   # i=0 perna direita(+x)
        far=(sg==-1);a=math.radians(g('ra' if sg==1 else 'la',0));k=math.radians(g('rk' if sg==1 else 'lk',0))
        hip=H+Vector((sg*.085,0,0));kn=hip+Vector((0,math.sin(a)*.285,-math.cos(a)*.285));an=kn+Vector((0,math.sin(a-k)*.275,-math.cos(a-k)*.275))
        kn.x+=sg*.015
        set_curve(LEG[i],[hip,hip.lerp(kn,.5)+Vector((0,0,.0)),kn,kn.lerp(an,.45),kn.lerp(an,.85),an],[.075,.066,.060,.052,.045,.04]);LEG[i].data.bevel_depth=1.0
        KNEE[i].location=kn+Vector((0,.03,.0));KNEE[i].scale=(.055,.045,.06)
        ang=a-k;BOOT[i].location=an+Vector((0,.05,-.045));BOOT[i].scale=(.062,.125,.06);BOOT[i].rotation_euler=(-ang*.3,0,0);BOOT2[i].location=an+Vector((0,-.01,-.005));BOOT2[i].scale=(.058,.062,.1)
    # braços (direita +x segura o cutelo)
    S0=T((0,0,.355));hands={}
    for i,sg in enumerate((1,-1)):
        us,fe=(g('us',8),g('fe',12)) if sg==1 else (g('ls',-8),g('le',-12))
        sh=S0+rx(Vector((sg*.175,0,.0)),lean);d1=fdir(us);d1.x=sg*.22;d1.normalize();el=sh+d1*.215
        d2=fdir(us+fe);d2.x=sg*.10;d2.normalize();hd=el+d2*.20
        set_curve(ARM[i],[sh,sh.lerp(el,.5),el,el.lerp(hd,.5),hd],[.058,.052,.047,.042,.038]);ARM[i].data.bevel_depth=1.0
        FIST[i].location=hd+d2*.015;FIST[i].scale=(.05,.05,.052)
        for j,off in enumerate((-.022,0,.022)):
            tip=hd+d2*.1+Vector((off,0,0));orient(CLAWS[i][j],hd+d2*.045+Vector((off*.6,0,0)),tip,.012,.07)
        orient(BRACER[i],el.lerp(hd,.30),el.lerp(hd,.70),.058,.075)
        PAULD[i].location=sh+Vector((sg*.02,0,.02));PAULD[i].scale=(.085,.075,.062);PAULD[i].rotation_euler=(0,sg*.5,0)
        orient(SPIKE[i],sh+Vector((sg*.05,0,.06)),sh+Vector((sg*.09,0,.15)),.03,.1)
        hands[sg]=(hd,d2)
    for e in E.values():e.co=Vector(e.co)*10
    hd,d2=hands[1];wr=math.radians(-g('weapon',22));d=Vector((0,math.cos(wr),math.sin(wr)));p=Vector((0,-d.z,d.y))
    ang=math.radians(18);side=Vector((1,0,0))
    # lâmina com a face levemente voltada para a câmera frontal
    dn=d.normalized();pn=(p*math.cos(ang)+side*math.sin(ang)).normalized()
    basis(CLEAVER,hd+dn*.01,dn,pn);set_curve(HANDLE,[hd-dn*.13,hd-dn*.04,hd+dn*.06],[.022,.022,.022]);HANDLE.data.bevel_depth=1.0
    orient(GUARD,hd+dn*.095,hd+dn*.118,.045,.03)
if __name__=='__main__' and len(sys.argv)>1 and sys.argv[1]=='head':
    set_view(co,'front',target=(0,.35,.95),el=15);co.data.ortho_scale=.6
    pose(dict(us=8,fe=26,ls=-8,le=-26,weapon=22,la=3,lk=12,ra=-3,rk=12,lean=1));render('/tmp/bg/head_front.png')
    set_view(co,'side',target=(0,.35,.95),el=15);render('/tmp/bg/head_side.png');sys.exit()
if __name__=='__main__':
    os.makedirs('/tmp/bg',exist_ok=True)
    for v in ('front','side','back'):
        set_view(co,v,target=(0,.04,.62));pose(dict(us=8,fe=26,ls=-8,le=-26,weapon=22,la=3,lk=12,ra=-3,rk=12,lean=1));render('/tmp/bg/n_%s.png'%v)
