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
# bug: dis() religava todas as maos (o punho no cabo ficava visivel dentro do tronco)
rep("for(const q in hm)hm[q].visible=(q===kind);","for(const q in hm){hm[q].userData.hide=(q!==kind);hm[q].visible=(q===kind);}")
rep("obj.visible=vis;};","obj.visible=vis&&!obj.userData.hide;};")

# colisao: braco/mao/cotovelo nao atravessam o tronco (elipse em torno do eixo quadril-peito, coordenadas do peito)
rep("  const shW=s=>chest.localToWorld(new THREE.Vector3(s*.8,.55,0));","""  const shW=s=>chest.localToWorld(new THREE.Vector3(s*.8,.55,0));
  const pushOut=(v,rx,rz)=>{const l=chest.worldToLocal(v.clone());if(l.y>-.85&&l.y<1.05){let ex=l.x/rx,ez=l.z/rz,d=Math.hypot(ex,ez);if(d<1){const zE=rz*Math.sqrt(Math.max(0,1-ex*ex));l.z=l.z>=-.15*rz?zE:-zE;return chest.localToWorld(l);}}return v;};
  {const g0=sword.localToWorld(new THREE.Vector3(0,-.12,0)),g1=pushOut(g0,.76,.64);if(g1!==g0){sword.position.add(g1.clone().sub(g0));sword.updateMatrixWorld(true);}}""")
rep("    const el=new THREE.Vector3();POLE.copy(G.localToWorld(new THREE.Vector3(side*.8,-.6,-.2))).sub(G.position);","    if(i===0){const t2=pushOut(tgt,.76,.64);tgt.copy(t2);}\n    const el=new THREE.Vector3();POLE.copy(G.localToWorld(new THREE.Vector3(side*.8,-.6,-.2))).sub(G.position);")
rep("armSeg[i].up.scale.y=st;armSeg[i].fo.scale.y=st;","""for(let it=0;it<3;it++){const m1=S0.clone().lerp(el,.55),m2=el.clone().lerp(tgt,.45);let mv=false;for(const [pt,k] of [[el,1],[m1,1.8],[m2,1.8]]){const q=pushOut(pt,.6,.5);if(q!==pt){const dl=q.clone().sub(pt);if(dl.lengthSq()>1e-6){el.add(dl.multiplyScalar(k));mv=true;}}}if(!mv)break;}
    armSeg[i].up.scale.y=S0.distanceTo(el)/.9;armSeg[i].fo.scale.y=el.distanceTo(tgt)/.85;""")

rep("const hit=(a==='attack'&&at>.4&&at<1.0)||","const hit=(k.fx>.15)||")
body=body.replace("const W=300,H=300,cv=document.getElementById('c');","const W=300,H=300,cv=document.getElementById('c');")
libs=open(D+'sdflib.js').read()+'\n'+open(D+'parts.js').read()
ui=open(D+'estudio/ui.html').read();uijs=open(D+'estudio/ui.js').read()
def page(three):
    return ui+'\n<script src="'+three+'"></script>\n<script>\n'+libs+'\n</script>\n<script>\nwindow.bootEngine=function(){\n'+body+'\n};\n</script>\n<script>\n'+uijs+'\n</script>\n'
open(D+'estudio/studio.html','w').write(page('https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js'))
open(D+'estudio/studio_local.html','w').write('<!doctype html><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">'+page('../../three.min.js'))
print(len(page('x')))
