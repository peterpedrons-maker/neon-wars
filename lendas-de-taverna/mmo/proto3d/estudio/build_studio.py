import re,sys
D='/home/user/neon-wars/lendas-de-taverna/mmo/proto3d/'
eng=open(D+'rei_sdf.html').read()
body=eng[eng.rindex('<script>')+8:eng.rindex('</script>')]
def rep(a,b,n=1):
    global body
    assert a in body,a[:70];body=body.replace(a,b) if n==0 else body.replace(a,b,n)
# camera livre (orbita) + TUNE + CAMV
rep("TILT=47*Math.PI/180;","TILT=47*Math.PI/180;const TUNE={speed:1,leanRun:1,stepH:1,armSwing:1,bob:1},CAMV={yaw:0,pitch:TILT,dist:12.6,ty:2.45};")
i=body.index("const ZQ=new URLSearchParams");j=body.index("const gd=new THREE.DataTexture")
body=body[:i]+"function placeCam(x,z){const c=CAMV;cam.position.set(x+c.dist*Math.sin(c.yaw)*Math.cos(c.pitch),c.ty+c.dist*Math.sin(c.pitch),z+c.dist*Math.cos(c.yaw)*Math.cos(c.pitch));cam.lookAt(x,c.ty,z);}\n"+body[j:]
rep("const camx=ZQ?0:sp('cmx',Math.sin(S.yaw)*1.5,30,8),camz=ZQ?0:sp('cmz',Math.cos(S.yaw)*1.5,30,8);placeCam(G.position.x+camx,G.position.z+camz);","placeCam(G.position.x,G.position.z);")
rep("cmd.move*2.2-S.spd","cmd.move*2.2*TUNE.speed-S.spd")
rep(".26*r",".26*r*TUNE.leanRun",0)
rep("(.3+.28*r)","(.3+.28*r)*TUNE.stepH")
rep("(swLn*(.5+.3*r))*wa","(swLn*(.5+.3*r)*TUNE.armSwing)*wa")
rep("(.07+.14*r)","(.07+.14*r)*TUNE.bob")
rep("R.render(scene,cam);\n}\nwindow.sim","if(!window.NORENDER)R.render(scene,cam);\n}\nwindow.sim")
rep("window.sim={step,S,R,cv,grab(){return cv.toDataURL('image/png');}};","function resetRig(){S.x=0;S.z=0;S.spd=0;S.vx=0;S.vz=0;S.ph=0;S.w=0;S.r=0;S.t=0;S.yaw=Math.PI/2;for(const k in SP)delete SP[k];PL.cur[0].set(0,0,0);PL.cur[1].set(0,0,0);PL.stp.forEach(s=>s.on=false);PL.moving=false;PL.st=[false,false];}\nwindow.sim={step,S,R,cv,grab(){return cv.toDataURL('image/png');}};window.REI={ANIMS,B,spline,TUNE,CAMV,reset:resetRig,S,refs:{G,sword,tip,head,chest,body,armSeg,legSeg,cam}};"+open(D+'estudio/lab_core.js').read()+"\nwindow.LAB=LAB;")
rep("placeCam(0,0);","S.yaw=Math.PI/2;placeCam(0,0);")
rep("sx:.05,sy:2.35,sz:.62","sx:.05,sy:2.8,sz:.62")
rep("ik2(S0,tgt,.9,.85,POLE,el);","const dd=S0.distanceTo(tgt),st=Math.max(1,Math.min(1.14,dd/1.74));ik2(S0,tgt,.9*st,.85*st,POLE,el);armSeg[i].up.scale.y=st;armSeg[i].fo.scale.y=st;")
rep("const hit=(a==='attack'&&at>.4&&at<1.0)||","const hit=(k.fx>.15)||")
body=body.replace("const W=300,H=300,cv=document.getElementById('c');","const W=300,H=300,cv=document.getElementById('c');")
libs=open(D+'sdflib.js').read()+'\n'+open(D+'parts.js').read()
ui=open(D+'estudio/ui.html').read();uijs=open(D+'estudio/ui.js').read()
def page(three):
    return ui+'\n<script src="'+three+'"></script>\n<script>\n'+libs+'\n</script>\n<script>\nwindow.bootEngine=function(){\n'+body+'\n};\n</script>\n<script>\n'+uijs+'\n</script>\n'
open(D+'estudio/studio.html','w').write(page('https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js'))
open(D+'estudio/studio_local.html','w').write('<!doctype html><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">'+page('../../three.min.js'))
print(len(page('x')))
