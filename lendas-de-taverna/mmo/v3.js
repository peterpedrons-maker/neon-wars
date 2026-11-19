/* Visual 2.5D — único modo de desenho do jogo. Só troca o DESENHO: a lógica (movimento, combate, colisão, missões, interface) é a do jogo 2D.
   O mundo é 3D (three.js); personagens, inimigos e o chefe continuam sendo os sprites do jogo, desenhados pelo próprio drawSprite() num canvas e colocados em pé no mundo.
   Se o aparelho não tiver WebGL, o jogo cai sozinho no desenho 2D antigo (render() em index.html). */
(function(){
'use strict';
if(window.V3_OFF)return;
if(typeof THREE==='undefined'){window.V3_FAIL='three.js ausente';return;}
const T=THREE,U=1.3/46,TILT=47*Math.PI/180,CT=Math.cos(TILT);
const V3=window.V3={ready:false,err:''};
let R,S,cam,glc,stageEl,lbBox;
const scenes=new Map();let scn=null;
const $=id=>document.getElementById(id);
const rndSeed=s=>()=>{s=(s*16807)%2147483647;return (s-1)/2147483646;};
function cvs(w,h){const c=document.createElement('canvas');c.width=w;c.height=h;return c;}
function blobTex(a=.55){const c=cvs(64,64),x=c.getContext('2d'),g=x.createRadialGradient(32,32,2,32,32,30);g.addColorStop(0,`rgba(0,0,0,${a})`);g.addColorStop(1,'rgba(0,0,0,0)');x.fillStyle=g;x.fillRect(0,0,64,64);return new T.CanvasTexture(c);}
const BT=blobTex();
const flameTex=(()=>{const c=cvs(64,64),x=c.getContext('2d'),g=x.createRadialGradient(32,32,1,32,32,30);g.addColorStop(0,'rgba(255,240,170,1)');g.addColorStop(.3,'rgba(255,160,60,.8)');g.addColorStop(1,'rgba(255,90,10,0)');x.fillStyle=g;x.fillRect(0,0,64,64);return new T.CanvasTexture(c);})();
const ringTex=(()=>{const c=cvs(64,64),x=c.getContext('2d'),g=x.createRadialGradient(32,32,8,32,32,31);g.addColorStop(0,'rgba(255,255,255,.25)');g.addColorStop(.78,'rgba(255,255,255,.55)');g.addColorStop(1,'rgba(255,255,255,0)');x.fillStyle=g;x.fillRect(0,0,64,64);return new T.CanvasTexture(c);})();
function init(){
  stageEl=$('stage');if(!stageEl)return;
  const st=document.createElement('style');st.textContent=`#gl3{position:absolute;inset:0;width:100%;height:100%;display:none}
  body.v3on #gl3{display:block}body.v3on canvas#cv{background:transparent;pointer-events:auto}
  #v3lb{position:absolute;inset:0;pointer-events:none;overflow:hidden;display:none}body.v3on #v3lb{display:block}
  .v3l{position:absolute;transform:translate(-50%,-100%);font:700 11px Rubik,Georgia,sans-serif;letter-spacing:.04em;color:#ffe69a;text-shadow:0 1px 0 #1a0a06,0 0 4px #000,0 0 8px #000;white-space:nowrap;text-align:center}
  .v3l.h{color:#bfe8ff}.v3l.b{color:#ffa680}.v3l.m{color:#ffecd6}.v3l.e{color:#8ec2ff}.v3l.g{color:#ffd24a}.v3l small{font-size:9px;opacity:.85;margin-left:3px;color:#d8d2c0}
  .v3l .bar{height:5px;margin:2px auto 0;background:rgba(10,6,8,.92);border:1px solid #000;box-sizing:content-box}.v3l .bar i{display:block;height:100%;background:#d6403a}.v3l.h .bar i{background:#5ed05e}.v3l.b .bar i{background:#e0502a}
  .v3ts{position:absolute;left:0;right:0;pointer-events:none;display:none;z-index:2}body.v3on .v3ts{display:block}
  .v3ts.t{top:0;height:15%;-webkit-backdrop-filter:blur(2.5px);backdrop-filter:blur(2.5px);-webkit-mask-image:linear-gradient(#000,transparent);mask-image:linear-gradient(#000,transparent)}
  .v3ts.b{bottom:0;height:18%;-webkit-backdrop-filter:blur(2.5px);backdrop-filter:blur(2.5px);-webkit-mask-image:linear-gradient(transparent,#000);mask-image:linear-gradient(transparent,#000)}
  #v3vg{position:absolute;inset:0;pointer-events:none;display:none;background:radial-gradient(ellipse at 50% 46%,transparent 56%,rgba(2,4,10,.5) 100%)}body.v3on #v3vg{display:block}`;
  document.head.appendChild(st);
  glc=document.createElement('canvas');glc.id='gl3';stageEl.insertBefore(glc,$('cv'));
  const mk=cl=>{const d=document.createElement('div');d.className=cl;stageEl.insertBefore(d,$('cv').nextSibling);return d;};
  lbBox=document.createElement('div');lbBox.id='v3lb';stageEl.insertBefore(lbBox,$('cv').nextSibling);
  const vg=document.createElement('div');vg.id='v3vg';stageEl.insertBefore(vg,$('cv').nextSibling);
  try{R=new T.WebGLRenderer({canvas:glc,antialias:true,powerPreference:'high-performance'});}catch(err){V3.err='este aparelho não liberou o WebGL';return;}
  R.outputEncoding=T.sRGBEncoding;R.shadowMap.enabled=true;R.shadowMap.type=T.PCFSoftShadowMap;R.toneMapping=T.ACESFilmicToneMapping;
  S=new T.Scene();cam=new T.PerspectiveCamera(32,1,.5,200);
  V3.ready=true;
}
function size(){const w=stageEl.clientWidth,h=stageEl.clientHeight,d=Math.min(devicePixelRatio||1,2);if(glc._w!==w+'x'+h){glc._w=w+'x'+h;R.setPixelRatio(d);R.setSize(w,h,false);cam.aspect=w/h;cam.updateProjectionMatrix();}}
// imagem só-chão da Cripta (as paredes e a plataforma viram geometria 3D)
let crpFloor=null,crpFloorReq=false;
function needFloor(){if(crpFloor||crpFloorReq)return;crpFloorReq=true;const im=new Image();im.onload=()=>{crpFloor=im;};im.onerror=()=>{crpFloor=GROUND;};im.src='assets/zone_cripta2_floor.png';}
V3.active=function(){
  if(!V3.ready||typeof G==='undefined'||!G.on||!G.hero||typeof ZONE==='undefined'||!ZONE||!ATLAS||!GROUND){document.body.classList.remove('v3on');return false;}
  if(G.map==='zone_cripta2'){needFloor();if(!crpFloor){document.body.classList.remove('v3on');return false;}}
  document.body.classList.add('v3on');return true;};
function texOf(img,px){const t=new T.Texture(img);t.encoding=T.sRGBEncoding;if(px){t.magFilter=T.NearestFilter;t.minFilter=T.LinearMipmapLinearFilter;}t.needsUpdate=true;return t;}
function crTex(draw,w,h,rep){const c=cvs(w,h);draw(c.getContext('2d'),w,h);const t=new T.CanvasTexture(c);t.encoding=T.sRGBEncoding;t.wrapS=t.wrapT=T.RepeatWrapping;t.anisotropy=4;if(rep)t.repeat.set(rep[0],rep[1]);return t;}
function bufGeo(pos,uv,idx,norm){const g=new T.BufferGeometry();g.setAttribute('position',new T.Float32BufferAttribute(pos,3));g.setAttribute('uv',new T.Float32BufferAttribute(uv,2));g.setIndex(idx);if(norm)g.computeVertexNormals();return g;}
function disposeScene(sc){S.remove(sc.grp);sc.grp.traverse(o=>{if(o.geometry&&!o.geometry._shared)o.geometry.dispose();if(o.material){(Array.isArray(o.material)?o.material:[o.material]).forEach(m=>{if(m.map&&!m.map._shared)m.map.dispose();m.dispose();});}});for(const [,r] of sc.ents)r.tex.dispose();for(const [,el] of sc.labels)el.remove();}
[BT,flameTex,ringTex].forEach(t=>t._shared=true);
const TOPDOWN=new Set(['5b39','a94a','dca1','64c7','0367']);   /* arte desenhada vista de cima (mesas, bancos, tapetes): fica deitada no chão */
const hex=(s,d)=>{try{const v=parseInt(String(s||'').replace('#','').slice(0,6),16);return isNaN(v)?d:v;}catch(e){return d;}};
// ------------------------------------------------------------------ cenários
function buildScene(key){
  const mood=ZONE.room?'room':ZONE.dark?'dark':key==='town'?'town':'field';
  const rnd=rndSeed(11);
  const sc={key,mood,grp:new T.Group(),houses:[],winMats:[],sources:[],pool:[],glows:[],smoke:[],chimneys:[],fires:[],fireGeos:[],ents:new Map(),labels:new Map(),dist:mood==='room'?12:mood==='town'?12.5:20,used:0};
  const g=sc.grp,add=o=>{g.add(o);return o;};
  S.add(g);
  const aTex=texOf(ATLAS,1),AW=ATLAS.width,AH=ATLAS.height,GWu=ZONE.w*U,GHu=ZONE.h*U;
  sc.hemi=new T.HemisphereLight(0xcfe3ff,0x4a5a3a,.8);sc.sun=new T.DirectionalLight(0xfff0d0,1.0);sc.sun.position.set(-8,14,10);add(sc.hemi);add(sc.sun);
  sc.hl=new T.PointLight(0xffb870,0,10,2);add(sc.hl);
  if(mood==='field'){const sh=sc.sun.shadow;sc.sun.castShadow=true;sh.mapSize.set(2048,2048);const c=sh.camera;c.left=-17;c.right=17;c.top=17;c.bottom=-17;c.near=1;c.far=60;sh.bias=-.0006;sh.normalBias=.03;add(sc.sun.target);}
  // ---- chão
  let dgrid=null;
  if(mood==='room'){
    const WH=88,H=GROUND.height,W=GROUND.width,pr0=V3.proc&&!window.V3_NOPROC,ft=pr0?texOf(V3.proc.woodFloor({W,H},V3.proc.palMadeira,key.length).canvas,1):texOf(GROUND,1),wt=pr0?V3.proc.woodWall(W,WH,key.length):texOf(GROUND,1);
    ft.repeat.set(1,(H-WH)/H);ft.offset.set(0,0);if(!pr0){wt.repeat.set(1,WH/H);wt.offset.set(0,(H-WH)/H);}sc.proc=pr0;
    const fl=new T.Mesh(new T.PlaneGeometry(W*U,(H-WH)*U),new T.MeshStandardMaterial({map:ft,roughness:.9}));fl.rotation.x=-Math.PI/2;fl.position.set(W*U/2,0,(WH+(H-WH)/2)*U);add(fl);
    const wh=WH*U/CT,wl=new T.Mesh(new T.PlaneGeometry(W*U,wh),new T.MeshBasicMaterial({map:wt,depthTest:false,depthWrite:false}));wl.position.set(W*U/2,wh/2,WH*U);wl.renderOrder=-10;add(wl);
    const top=new T.Mesh(new T.PlaneGeometry(W*U+10,8),new T.MeshBasicMaterial({color:0x120a06,depthTest:false,depthWrite:false}));top.position.set(W*U/2,wh+4,WH*U);top.renderOrder=-11;add(top);
    const sm=new T.MeshStandardMaterial({color:0x2a1a0e,roughness:.95});
    for(const sx of[-.4,W*U+.4]){const sw=new T.Mesh(new T.BoxGeometry(.8,3.2,(H-WH)*U),sm);sw.position.set(sx,1.6,(WH+(H-WH)/2)*U);add(sw);}
    sc.hemi.color.setHex(0xffe6bf);sc.hemi.groundColor.setHex(0x5a4020);
    for(const [px,pz] of[[W*.28,H*.40],[W*.72,H*.40],[W*.5,H*.7]])sc.sources.push({p:new T.Vector3(px*U,2.4,pz*U),c:0xffc070,k:1.3,night:1,still:1,nog:1});
  }else{
    const procOn=(mood==='field'||mood==='dark'||mood==='town')&&V3.proc&&!window.V3_NOPROC;sc.proc=procOn;
    dgrid=(procOn&&mood==='dark')?dungeonGrid(key):null;
    const envP={W:ZONE.w,H:ZONE.h,WATER:mood==='town'?null:WATER,WCW,GROUND,stoneNonGreen:mood==='town',S:ZONE.w>3000?.3:.5,themes:!!ZONE.region};
    let gimg=key==='zone_cripta2'?crpFloor:GROUND;
    if(procOn&&(mood==='field'||mood==='town'))gimg=V3.proc.ground(envP,mood==='town'?V3.proc.palCidade:(key==='zone_pantano'||(ZONE.region&&ZONE.region.ground==='swamp'))?V3.proc.palPantano:V3.proc.palFloresta,key==='zone1'?5:key==='town'?9:7);
    else if(procOn){const pal=key==='zone_esgoto'?V3.proc.palEsgoto:key==='zone_cripta2'?V3.proc.palCripta2:V3.proc.palCripta;gimg=V3.proc.dungeonFloor(envP,pal,key==='zone_esgoto'?4:key==='zone_cripta2'?6:3);
      {const x=gimg.canvas.getContext('2d'),S0=gimg.canvas.width/ZONE.w;x.fillStyle='#030409';for(let cy=0;cy<dgrid.rows;cy++)for(let cx=0;cx<dgrid.cols;cx++)if(!dgrid.isF(cx,cy))x.fillRect(Math.floor((dgrid.ox+cx*dgrid.cw)*S0),Math.floor((dgrid.oy+cy*dgrid.ch)*S0),Math.ceil(dgrid.cw*S0)+1,Math.ceil(dgrid.ch*S0)+1);}}
    const pg=procOn?gimg:null,gTex=texOf(pg?pg.canvas:gimg,1);gTex.anisotropy=8;
    const gm=new T.MeshStandardMaterial({map:gTex,roughness:.95});if(mood!=='dark'){gm.bumpMap=gTex;gm.bumpScale=1.2;}
    const ground=new T.Mesh(new T.PlaneGeometry(GWu,GHu),gm);ground.rotation.x=-Math.PI/2;ground.position.set(GWu/2,0,GHu/2);add(ground);ground.receiveShadow=true;if(pg&&pg.M&&mood!=='dark'){add(V3.proc.waterMesh(pg,GWu,GHu,(key==='zone_pantano'||(ZONE.region&&ZONE.region.ground==='swamp'))?[.45,.62,.4]:undefined));sc.lifeUpd=V3.proc.waterLife(add,pg,GWu,GHu,key==='zone_pantano'?{slow:.7,opacity:.5,size:1.5}:{opacity:.55,size:1.5,per:280});}if(pg&&key==='zone_esgoto'){add(V3.proc.waterMesh(pg,GWu,GHu,[.35,.5,.18]));sc.lifeUpd=V3.proc.waterLife(add,pg,GWu,GHu,{size:1.8,slow:.45,opacity:.45,per:420});}
    if(ZONE.region&&ZONE.exits&&ZONE.exits.length)sc.exitUpd=V3.proc.exitMarks(add,ZONE.exits,ZONE.w,ZONE.h);
    if(mood!=='dark'){const far=new T.Mesh(new T.PlaneGeometry(400,400),new T.MeshStandardMaterial({color:0x2c5a22,roughness:1}));far.rotation.x=-Math.PI/2;far.position.set(GWu/2,-.02,GHu/2);add(far);}
  }
  // ---- props do atlas (billboards em pé, mesclados)
  function quads(items,flat){const pos=[],uv=[],idx=[];let n=0;
    for(const [id,px,py] of items){const a=ATLAS_J[id];if(!a)continue;const [sx,sy,sw,sh,ax,ay]=a,X=px*U,Z=py*U;
      [[-ax,ay],[sw-ax,ay],[sw-ax,ay-sh],[-ax,ay-sh]].forEach(([cx,cy],i)=>{
        if(flat)pos.push(X+cx*U,.02,Z-cy*U);else pos.push(X+cx*U,Math.max(0,cy*U/CT),Z);
        uv.push((sx+[0,1,1,0][i]*sw)/AW,1-(sy+[0,0,1,1][i]*sh)/AH);});
      idx.push(n,n+1,n+2,n,n+2,n+3);n+=4;}
    if(!n)return null;const geo=bufGeo(pos,uv,idx,1);
    const m=new T.MeshLambertMaterial({map:aTex,alphaTest:.4,side:T.DoubleSide,emissive:0xffffff,emissiveMap:aTex,emissiveIntensity:0});
    return add(new T.Mesh(geo,m));}
  const stand=[],flats=[],lampsP=[];
  for(const p of ZONE.props){if(p.t==='fire'){sc.fires.push(p);continue;}
    if(!p.id||p.t==='portal')continue;
    const a=ATLAS_J[p.id];if(!a)continue;
    if(mood==='room'&&p.id.slice(0,4)==='f1a3')continue;   /* lustre preto (arte sem luz): fica só a luz */
    if(p.t==='flat'||(mood==='room'&&TOPDOWN.has(p.id.slice(0,4)))){flats.push([p.id,p.x,p.y]);continue;}
    if(key==='town'&&p.id.startsWith('b_'))continue;stand.push([p.id,p.x,p.y]);
    if(key==='town'&&a[2]<=24&&a[3]>=80)lampsP.push([p.x*U,2.3,p.y*U]);}
  if(key==='zone_pantano'&&V3.proc)V3.proc.direct(add,ZONE.props.filter(p=>p.k),sc);
  if(ZONE.region&&V3.proc)V3.proc.direct(add,ZONE.props.filter(p=>p.k),sc);
  if(key==='zone_cripta2'&&V3.proc){   // Cripta: cada prop do atlas vira o modelo certo (nada de adivinhar pela cor)
    const MAPC=[['prop_barril','barrel',.85],['prop_caixas','crates',1.1],['braseiro','brazier',.9],['pilar','pillar',.8],['prop_potes','pots',.9],['prop_sacos','sacks',1],['prop_altar','altar',1.05],['prop_bau','chest',1.2],['prop_mesa','table',1.1],['prop_prateleira','potshelf',1.0],['prop_jaula','cage',1.05]],pl=ZONE.crp&&ZONE.crp.plat,lift=pl?pl.elev*U/CT:0,list=[],keep=[];
    for(const p of ZONE.props){const a=ATLAS_J[p.id];if(p.t!=='p'||!a){keep.push(p);continue;}const e=MAPC.find(q=>p.id.startsWith(q[0]));if(!e){keep.push(p);continue;}
      const it={k:e[1],x:p.x,y:p.y,s:a[3],wf:(a[2]/a[3])/e[2]*(e[1]==='pillar'?1.3:1),fix:1,hk:e[1]==='pillar'?1:.85,lift:/_e$/.test(p.id)?lift:0};list.push(it);
      if(e[1]==='brazier'){V3.proc.fire(add,p.x*U,p.y*U-.1,.9,'bowl').position.y=it.lift;sc.sources.push({p:new T.Vector3(p.x*U,1.0+it.lift,p.y*U+.3),c:0xffa040,k:1.6,night:1,fl:1});}}
    V3.proc.direct(add,list,sc);stand.length=0;flats.length=0;}
    let st0=stand,fl0=flats;if(sc.proc){const rest=V3.proc.forest({ATLAS,ATLAS_J},add,rnd,{stand,flats},mood==='dark'?'dungeon':mood==='town'?'town':mood==='room'?'indoor':'outdoor');st0=rest.stand;fl0=rest.flats;
    if(mood==='dark'&&dgrid)V3.proc.walls(add,Object.assign({brickCol:key==='zone_esgoto'?'#2c3a2c':'#2a3340',capCol:key==='zone_esgoto'?'#46563f':'#4a5568',moss:key==='zone_esgoto'?.5:0,radius:key==='zone_cripta2'?1:2},dgrid,{ox:0}));}
  const mf=quads(fl0,true);if(mf){mf.material.polygonOffset=true;mf.material.polygonOffsetFactor=-2;}quads(st0,false);
  {const pos=[],uv=[],idx=[];let n=0;for(const [id,px,py] of stand){const a=ATLAS_J[id];if(!a||a[3]<60)continue;const X=px*U,Z=py*U,rw=Math.min(a[2],100)*U*.55,rd=rw*.5;
    [[-rw,-rd],[rw,-rd],[rw,rd],[-rw,rd]].forEach(([cx,cz],i)=>{pos.push(X+cx,.03,Z+cz+rd*.6);uv.push([0,1,1,0][i],[0,0,1,1][i]);});idx.push(n,n+1,n+2,n,n+2,n+3);n+=4;}
    if(n)add(new T.Mesh(bufGeo(pos,uv,idx,0),new T.MeshBasicMaterial({map:BT,transparent:true,depthWrite:false,polygonOffset:true,polygonOffsetFactor:-3,opacity:mood==='dark'?.8:1})));}
  // fogueiras: base + chama animada (4 quadros do atlas)
  if(sc.proc){for(const p of sc.fires)V3.proc.fire(add,p.x*U,p.y*U,p.small?.7:1,'fire');sc.fires.length=0;}
  for(const p of sc.fires){const b=ATLAS_J.bf0,fi=ATLAS_J.fi0;if(!b||!fi)continue;const X=p.x*U,Z=(p.y+4)*U,pos=[],uv=[],idx=[0,1,2,0,2,3,4,5,6,4,6,7];
    const put=(a,lift,zz)=>{const [sx,sy,sw,sh,ax,ay]=a;[[-ax,ay],[sw-ax,ay],[sw-ax,ay-sh],[-ax,ay-sh]].forEach(([cx,cy],i)=>{pos.push(X+cx*U,Math.max(0,(cy+lift)*U/CT),zz);uv.push((sx+[0,1,1,0][i]*sw)/AW,1-(sy+[0,0,1,1][i]*sh)/AH);});};
    put(b,0,Z);put(fi,18,Z+.02);const geo=bufGeo(pos,uv,idx,1);
    add(new T.Mesh(geo,new T.MeshLambertMaterial({map:aTex,alphaTest:.3,side:T.DoubleSide,emissive:0xffffff,emissiveMap:aTex,emissiveIntensity:.35})));sc.fireGeos.push(geo);}
  // ---- extras por cenário
  if(key==='town')townExtras(sc,add,rnd);
  if(key==='zone_cripta2')crpExtras(sc,add,sc.proc);
  // ---- luzes
  for(const [x,y,z] of lampsP)sc.sources.push({p:new T.Vector3(x,y,z),c:0xffc878,k:1.5,night:1});
  for(const f of (typeof zoneAutoFx==='function'?zoneAutoFx(ZONE):(ZONE.fx||[]))){
    if(f.k==='fire')sc.sources.push({p:new T.Vector3(f.x*U,1.0,f.y*U+.4),c:0xffa040,k:1.9,night:.3,fl:1});
    else if(f.k==='torch')sc.sources.push({p:new T.Vector3(f.x*U,key==='zone_cripta2'?2.1:1.6,f.y*U+.5),c:0xffa040,k:1.6,night:1,fl:1});
    else if(f.k==='lamp'&&key!=='town')sc.sources.push({p:new T.Vector3(f.x*U,2.2,f.y*U+.5),c:hex(f.col,0xffb050),k:1.5,night:1});
    else if(f.k==='glow'&&f.col)sc.sources.push({p:new T.Vector3(f.x*U,1.3,f.y*U+.5),c:hex(f.col,0xff9a3a),k:1.6,night:.3,fl:1});}
  if(sc.proc)for(const f of (typeof zoneAutoFx==='function'?zoneAutoFx(ZONE):[]))if(f.k==='torch'||(f.k==='lamp'&&mood==='dark'))V3.proc.fire(add,f.x*U,f.y*U+.45,f.k==='lamp'?.75:1,'torch');
  for(let i=0;i<7;i++){const L=new T.PointLight(0xffc878,0,11,2);add(L);sc.pool.push(L);}
  sc.glows=sc.sources.map(s=>{const sp=new T.Sprite(new T.SpriteMaterial({map:flameTex,blending:T.AdditiveBlending,depthWrite:false,transparent:true,color:s.c}));sp.position.copy(s.p);sp.scale.set(1.3,1.3,1);sp.visible=!s.nog;add(sp);return sp;});
  if(key==='zone_pantano'){const NF=160,fp=new Float32Array(NF*3);for(let i=0;i<NF;i++){const y=300+(i/NF)*1800;fp[i*3]=(720+Math.sin(y*.004)*190+Math.sin(y*.011)*60+(Math.random()-.5)*380)*U;fp[i*3+1]=.6+Math.random()*2.4;fp[i*3+2]=y*U;}
    const fg=new T.BufferGeometry();fg.setAttribute('position',new T.BufferAttribute(fp,3));const fc=cvs(32,32),fx=fc.getContext('2d'),gr=fx.createRadialGradient(16,16,0,16,16,16);gr.addColorStop(0,'rgba(220,255,160,1)');gr.addColorStop(1,'rgba(220,255,160,0)');fx.fillStyle=gr;fx.fillRect(0,0,32,32);
    sc.flies={pts:new T.Points(fg,new T.PointsMaterial({map:new T.CanvasTexture(fc),size:.5,transparent:true,blending:T.AdditiveBlending,depthWrite:false})),base:fp,n:NF};add(sc.flies.pts);}
  for(const ch of sc.chimneys)for(let i=0;i<6;i++){const sp=new T.Sprite(new T.SpriteMaterial({map:blobTex(.5),transparent:true,depthWrite:false,color:0xcfcfd4,opacity:0}));add(sp);sc.smoke.push({sp,x:ch.x,y:ch.y,z:ch.z,t:i/6*4});}
  sc.lifeFn=buildLife(sc,add);
  return sc;
}
function townExtras(sc,add,rnd){
  const HC={b_fer:{name:'Ferreiro',roof:'#2d3540',wall:'#b99a74',glow:'#ff8a2a',smoke:1},b_mer:{name:'Mercador',roof:'#7a3b29',wall:'#c4a58a',glow:'#ffd27a'},b_mes:{name:'Mestre de Classe',roof:'#34455a',wall:'#c9b8a8',glow:'#ffd27a'},b_alq:{name:'Alquimista',roof:'#355868',wall:'#a99aa6',glow:'#9affc0',smoke:1},b_lei:{name:'Leilão',roof:'#562729',wall:'#b98f6c',glow:'#ffd27a'},b_cof:{name:'Cofre',roof:'#364b42',wall:'#6a6668',glow:'#8ac8ff'}};
  function facade(cfg){const W=512,H=384,c=cvs(W,H),x=c.getContext('2d'),e=cvs(W,H),y=e.getContext('2d');
    x.fillStyle=cfg.wall;x.fillRect(0,0,W,H);for(let i=0;i<500;i++){x.fillStyle=`rgba(${rnd()<.5?'0,0,0':'255,255,255'},${.03+rnd()*.05})`;x.fillRect(rnd()*W,rnd()*H,2+rnd()*6,2+rnd()*3);}
    y.fillStyle='#000';y.fillRect(0,0,W,H);const stoneH=70;x.fillStyle='#6a6e72';x.fillRect(0,H-stoneH,W,stoneH);
    for(let j=0;j<3;j++)for(let i=0;i<10;i++){x.fillStyle=`hsl(210,6%,${34+rnd()*14}%)`;x.fillRect(i*52+(j%2)*26+2,H-stoneH+j*23+2,48,19);}
    x.fillStyle='#3a2616';const bw=14;x.fillRect(0,0,W,bw);x.fillRect(0,H-stoneH-bw/2,W,bw);x.fillRect(0,H*.38,W,bw);for(const px of[0,W/4,W/2,3*W/4,W-bw])x.fillRect(px,0,bw,H-stoneH);
    x.strokeStyle='#3a2616';x.lineWidth=10;x.beginPath();x.moveTo(0,H*.38);x.lineTo(W/4,0);x.moveTo(W,H*.38);x.lineTo(3*W/4,0);x.stroke();
    const dx=W/2-44,dy=H-stoneH-130,dw=88,dh=130+stoneH;
    x.fillStyle='#2c3034';x.beginPath();x.moveTo(dx-8,H);x.lineTo(dx-8,dy+30);x.arc(W/2,dy+30,dw/2+8,Math.PI,0);x.lineTo(dx+dw+8,H);x.fill();
    x.fillStyle='#4a2d18';x.beginPath();x.moveTo(dx,H);x.lineTo(dx,dy+30);x.arc(W/2,dy+30,dw/2,Math.PI,0);x.lineTo(dx+dw,H);x.fill();
    x.fillStyle='rgba(0,0,0,.35)';for(let i=1;i<5;i++)x.fillRect(dx+i*dw/5,dy+8,2,dh);x.fillStyle='#1a1c20';x.fillRect(dx,dy+50,dw,8);x.fillRect(dx,dy+110,dw,8);x.fillStyle='#d9a84a';x.fillRect(W/2-3,dy+70,6,10);
    for(const wxp of[70,W-70-82]){x.fillStyle='#2c1a0e';x.fillRect(wxp-6,H*.5-6,94,84);x.fillStyle='#1a2230';x.fillRect(wxp,H*.5,82,72);x.fillStyle='#5a3a1e';x.fillRect(wxp-14,H*.5,14,72);x.fillRect(wxp+82,H*.5,14,72);
      y.fillStyle=cfg.glow;y.fillRect(wxp,H*.5,82,72);x.fillStyle=cfg.glow;x.globalAlpha=.18;x.fillRect(wxp,H*.5,82,72);x.globalAlpha=1;x.fillStyle='#2c1a0e';x.fillRect(wxp+39,H*.5,4,72);x.fillRect(wxp,H*.5+34,82,4);y.fillStyle='#000';y.fillRect(wxp+39,H*.5,4,72);y.fillRect(wxp,H*.5+34,82,4);}
    const t=new T.CanvasTexture(c),et=new T.CanvasTexture(e);t.encoding=T.sRGBEncoding;et.encoding=T.sRGBEncoding;t.anisotropy=4;return [t,et];}
  function sideTex(cfg){const c=cvs(256,256),x=c.getContext('2d');x.fillStyle=cfg.wall;x.fillRect(0,0,256,256);x.fillStyle='#3a2616';x.fillRect(0,0,256,10);x.fillRect(0,100,256,10);for(const p of[0,120,246])x.fillRect(p,0,10,256);x.fillStyle='#6a6e72';x.fillRect(0,196,256,60);const t=new T.CanvasTexture(c);t.encoding=T.sRGBEncoding;return t;}
  function roofTex(col){const c=cvs(256,256),x=c.getContext('2d');x.fillStyle=col;x.fillRect(0,0,256,256);for(let j=0;j<16;j++)for(let i=-1;i<9;i++){const px=i*32+(j%2)*16,py=j*16;x.fillStyle=`rgba(${rnd()<.5?'0,0,0':'255,255,255'},${.05+rnd()*.12})`;x.fillRect(px+1,py+1,30,14);x.fillStyle='rgba(0,0,0,.3)';x.fillRect(px,py+14,32,2);}const t=new T.CanvasTexture(c);t.wrapS=t.wrapT=T.RepeatWrapping;t.repeat.set(3,2);t.encoding=T.sRGBEncoding;return t;}
  function sign(name){const c=cvs(256,96),x=c.getContext('2d');x.fillStyle='#3a2210';x.fillRect(0,0,256,96);x.fillStyle='#5a3a1e';x.fillRect(5,5,246,86);x.fillStyle='#f0d890';x.font='700 30px Georgia';x.textAlign='center';x.textBaseline='middle';x.fillText(name,128,50,230);const t=new T.CanvasTexture(c);t.encoding=T.sRGBEncoding;return t;}
  function house(id,px,py){const cfg=HC[id];if(!cfg)return;const gr=new T.Group();gr.position.set(px*U,0,py*U);
    const w=5.3,d=4.5,h=2.9,[ft,fe]=facade(cfg),st=sideTex(cfg);
    const ws=new T.MeshStandardMaterial({map:st,roughness:.9}),wf=new T.MeshStandardMaterial({map:ft,emissiveMap:fe,emissive:0xffffff,emissiveIntensity:.25,roughness:.9});sc.winMats.push(wf);
    const body=new T.Mesh(new T.BoxGeometry(w,h,d),[ws,ws,new T.MeshStandardMaterial({color:0x444}),new T.MeshStandardMaterial({color:0x222}),wf,ws]);body.position.set(0,h/2,-d/2);gr.add(body);
    const rt=roofTex(cfg.roof),hip=new T.BufferGeometry(),a=w/2+.45,b=d/2+.45,rh=1.45,ra=1.0,v=[[-a,0,b],[a,0,b],[a,0,-b],[-a,0,-b],[-ra,rh,-.1],[ra,rh,-.1]];
    const f=[[0,1,5],[0,5,4],[1,2,5],[2,3,4],[2,4,5],[3,0,4]],P=[],UV=[];f.forEach(t=>t.forEach(q=>P.push(...v[q])));f.forEach(()=>UV.push(0,0,1,0,.5,1));
    hip.setAttribute('position',new T.Float32BufferAttribute(P,3));hip.setAttribute('uv',new T.Float32BufferAttribute(UV,2));hip.computeVertexNormals();
    const rf=new T.Mesh(hip,new T.MeshStandardMaterial({map:rt,roughness:.85,side:T.DoubleSide}));rf.position.set(0,h,-d/2);gr.add(rf);
    const rim=new T.Mesh(new T.BoxGeometry(w+1,.14,d+1),new T.MeshStandardMaterial({color:0x2a1a0e,roughness:.9}));rim.position.set(0,h+.04,-d/2);gr.add(rim);
    const ch=new T.Mesh(new T.BoxGeometry(.7,1.2,.7),new T.MeshStandardMaterial({color:0x3b3b40,roughness:.9}));ch.position.set(w*.28,h+1.1,-d*.6);gr.add(ch);
    if(cfg.smoke)sc.chimneys.push({x:gr.position.x+w*.28,y:h+1.8,z:gr.position.z-d*.6});
    const sg=new T.Mesh(new T.PlaneGeometry(1.5,.56),new T.MeshBasicMaterial({map:sign(cfg.name),side:T.DoubleSide}));sg.position.set(0,h*.72,.35);gr.add(sg);
    const br=new T.Mesh(new T.BoxGeometry(.06,.06,.6),new T.MeshStandardMaterial({color:0x222}));br.position.set(0,h*.72+.34,.1);gr.add(br);
    for(let i=0;i<2;i++){const s2=new T.Mesh(new T.BoxGeometry(1.6-i*.3,.12,.5),new T.MeshStandardMaterial({color:0x5a5d62,roughness:.9}));s2.position.set(0,.06+i*.12,.28+(1-i)*.25);gr.add(s2);}
    const mats=[];gr.traverse(o=>{if(o.material)(Array.isArray(o.material)?o.material:[o.material]).forEach(m=>{if(!mats.includes(m))mats.push(m);});});
    gr.userData={mats,o:1,box:new T.Box3(new T.Vector3(gr.position.x-w/2-.7,0,gr.position.z-d-.7),new T.Vector3(gr.position.x+w/2+.7,h+1.7,gr.position.z+.5)),id,w,d,h};sc.houses.push(gr);add(gr);}
  for(const p of ZONE.props)if(p.id&&p.id.startsWith('b_'))house(p.id,p.x,p.y);
  // portal 3D (arco + vórtice)
  {const P=ZONE.portal,pg=new T.Group();pg.position.set(P.x*U,0,P.y*U);add(pg);const sm=new T.MeshStandardMaterial({color:0x2f3338,roughness:.95});
    for(const s of[-1,1]){const p1=new T.Mesh(new T.BoxGeometry(.9,3.4,.9),sm);p1.position.set(s*1.75,1.7,0);pg.add(p1);const b1=new T.Mesh(new T.BoxGeometry(1.2,.35,1.2),sm);b1.position.set(s*1.75,.18,0);pg.add(b1);const c1=new T.Mesh(new T.BoxGeometry(1.1,.3,1.1),sm);c1.position.set(s*1.75,3.5,0);pg.add(c1);}
    const arc=new T.Mesh(new T.TorusGeometry(1.75,.42,12,36,Math.PI),sm);arc.position.set(0,3.4,0);pg.add(arc);
    sc.vm=new T.ShaderMaterial({transparent:true,depthWrite:false,blending:T.AdditiveBlending,uniforms:{t:{value:0}},vertexShader:'varying vec2 u;void main(){u=uv*2.-1.;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}',
      fragmentShader:'varying vec2 u;uniform float t;void main(){float r=length(u*vec2(1.,.85));if(r>1.)discard;float a=atan(u.y,u.x);float s=sin(a*4.+r*9.-t*3.)*.5+.5;float s2=sin(a*3.-r*13.+t*2.2)*.5+.5;vec3 c=mix(vec3(.25,.1,.6),vec3(.5,.85,1.),s*s2);float f=smoothstep(1.,.75,r);gl_FragColor=vec4(c*(.5+.9*s)*f+vec3(.9,.8,1.)*pow(max(0.,1.-r*1.6),2.),f*.95);}'});
    const vt=new T.Mesh(new T.PlaneGeometry(3.4,3.9),sc.vm);vt.position.set(0,2.0,.05);pg.add(vt);
    if(typeof PXFX==='undefined'||PXFX){const tx=new T.TextureLoader().load('assets/fx/portal_arcano.png',()=>{vt.visible=false;sp.visible=true;});tx.magFilter=T.NearestFilter;tx.minFilter=T.NearestFilter;tx.generateMipmaps=false;tx.repeat.set(1/8,1/6);
      const sp=new T.Mesh(new T.PlaneGeometry(7.6,5.95),new T.MeshBasicMaterial({map:tx,transparent:true,depthWrite:false}));sp.position.set(0,2.5,.1);sp.visible=false;pg.add(sp);sc.pt=tx;}sc.pl=new T.PointLight(0x9a7aff,1.6,12,2);sc.pl.position.set(0,2.4,1.2);pg.add(sc.pl);}
}

// grade de "é chão?" das masmorras: Cripta usa a grade do mapa; Catacumbas/Esgoto leem os cômodos (claro = chão, escuro = vazio)
const gridCache={};
function dungeonGrid(key){if(gridCache[key])return gridCache[key];let r;
  if(key==='zone_cripta2'&&ZONE.grid){const gr=ZONE.grid,[TW,TH,OY]=ZONE.cell||[48,45,9];r={rows:gr.length,cols:gr[0].length,isF:(x,y)=>y>=0&&y<gr.length&&x>=0&&x<gr[0].length&&gr[y][x]!=='#',cw:TW,ch:TH,ox:0,oy:OY};}
  else{const cw=24,cols=Math.ceil(ZONE.w/cw),rows=Math.ceil(ZONE.h/cw),c=cvs(cols,rows),x=c.getContext('2d',{willReadFrequently:true});x.drawImage(GROUND,0,0,cols,rows);const d=x.getImageData(0,0,cols,rows).data,F=new Uint8Array(cols*rows);
    for(let i=0;i<cols*rows;i++){const l=d[i*4]*.3+d[i*4+1]*.59+d[i*4+2]*.11;F[i]=l>46?1:0;}
    if(typeof WATER!=='undefined'&&WATER&&WCW)for(let cy=0;cy<rows;cy++)for(let cx=0;cx<cols;cx++)if(WATER[Math.min(cy*6+3,Math.ceil(ZONE.h/4)-1)*WCW+Math.min(cx*6+3,WCW-1)])F[cy*cols+cx]=1;
    r={rows,cols,isF:(x,y)=>y>=0&&y<rows&&x>=0&&x<cols&&F[y*cols+x]===1,cw,ch:cw,ox:0,oy:0};}
  return gridCache[key]=r;}

// ---- vida no cenário: pássaros que cruzam o céu (com sombra no chão), borboletas, folhas caindo, poeira e morcegos nas masmorras
function buildLife(sc,add){
  const mood=sc.mood,wing=(up)=>{const c=cvs(64,32),x=c.getContext('2d');x.fillStyle='#1c1812';x.beginPath();x.ellipse(32,18,7,4,0,0,7);x.fill();
    x.beginPath();if(up){x.moveTo(28,16);x.quadraticCurveTo(18,2,6,5);x.quadraticCurveTo(18,10,28,19);x.moveTo(36,16);x.quadraticCurveTo(46,2,58,5);x.quadraticCurveTo(46,10,36,19);}else{x.moveTo(28,18);x.quadraticCurveTo(18,24,6,28);x.quadraticCurveTo(20,19,28,20);x.moveTo(36,18);x.quadraticCurveTo(46,24,58,28);x.quadraticCurveTo(44,19,36,20);}x.fill();return new T.CanvasTexture(c);};
  const L={fl:[],bf:[],lv:null,dust:null,t:0},tU=wing(1),tD=wing(0);
  const mk=(bat)=>{const mt=new T.SpriteMaterial({map:tU,transparent:true,depthWrite:false,color:bat?0x2a2236:0xffffff,opacity:.92}),sp=new T.Sprite(mt);sp.visible=false;add(sp);
    const sh=new T.Mesh(new T.PlaneGeometry(1.1,.5),new T.MeshBasicMaterial({map:BT,transparent:true,depthWrite:false,opacity:.35}));sh.rotation.x=-Math.PI/2;sh.visible=false;add(sh);return {sp,sh,mt,on:false,x:0,z:0,dx:1,v:3,h:6,ph:Math.random()*6,wait:Math.random()*6,bat};};
  if(mood==='field'||mood==='town')for(let i=0;i<4;i++)L.fl.push(mk(0));
  if(mood==='dark')for(let i=0;i<3;i++)L.fl.push(mk(1));
  if(mood==='field'||mood==='town'){const bc=cvs(32,32),x=bc.getContext('2d');x.fillStyle='#fff';x.beginPath();x.ellipse(11,14,9,7,-.3,0,7);x.fill();x.beginPath();x.ellipse(21,14,9,7,.3,0,7);x.fill();x.fillStyle='#3a2a20';x.fillRect(15,9,2,12);const bt=new T.CanvasTexture(bc);
    const cols=[0xffb02e,0xff6aa8,0x8ad0ff,0xfff06a,0xc89aff];for(let i=0;i<10;i++){const sp=new T.Sprite(new T.SpriteMaterial({map:bt,color:cols[i%5],transparent:true,depthWrite:false}));sp.scale.set(.5,.5,1);sp.visible=false;add(sp);L.bf.push({sp,ax:0,az:0,ph:Math.random()*10,r:1.2+Math.random()*2.4,sp0:.5+Math.random()*.7,h:.5+Math.random()*1.2,init:0});}}
  const mkPts=(n,col,size,op,add2)=>{const g=new T.BufferGeometry(),p=new Float32Array(n*3);g.setAttribute('position',new T.BufferAttribute(p,3));const pc=cvs(16,16),px=pc.getContext('2d'),gr=px.createRadialGradient(8,8,0,8,8,8);gr.addColorStop(0,'rgba(255,255,255,1)');gr.addColorStop(1,'rgba(255,255,255,0)');px.fillStyle=gr;px.fillRect(0,0,16,16);
    const o=new T.Points(g,new T.PointsMaterial({map:new T.CanvasTexture(pc),color:col,size,transparent:true,opacity:op,depthWrite:false,blending:add2?T.AdditiveBlending:T.NormalBlending}));o.frustumCulled=false;add(o);return {o,p,n,s:Array.from({length:n},()=>[Math.random()*20-10,Math.random()*12,Math.random()*16-8,Math.random()*6])};};
  if(mood==='field'||mood==='town')L.lv=mkPts(34,0xc89a3a,.34,.9,0);
  if(mood==='dark'||mood==='room')L.dust=mkPts(48,0xbfc8e8,.16,.5,1);
  return function(t,dt,n,cx,cz){
    const day=1-Math.min(1,n*1.6);
    for(const b of L.fl){b.wait-=dt;
      if(!b.on){if(b.wait<=0&&(b.bat?n>-1:day>.3)){b.on=true;b.dx=Math.random()<.5?1:-1;b.x=cx-b.dx*16;b.z=cz+(Math.random()-.5)*10;b.v=(b.bat?4.2:3.4)+Math.random()*2;b.h=b.bat?2.4+Math.random()*1.5:5.5+Math.random()*3;b.ph=Math.random()*6;b.sp.visible=true;b.sh.visible=!b.bat;}continue;}
      b.x+=b.dx*b.v*dt;b.z+=Math.sin(t*.7+b.ph)*dt*.9;const y=b.h+Math.sin(t*2.1+b.ph)*.35;b.sp.position.set(b.x,y,b.z);
      const fl=Math.sin(t*(b.bat?20:13)+b.ph)>0;b.mt.map=fl?tU:tD;b.sp.scale.set(b.bat?1.5:1.3,b.bat?.75:.65,1);b.sh.position.set(b.x,.04,b.z+.6);b.sh.scale.set(1+(fl?.15:0),1,1);b.sh.material.opacity=.28*day;
      if(Math.abs(b.x-cx)>18){b.on=false;b.sp.visible=false;b.sh.visible=false;b.wait=(b.bat?9:7)+Math.random()*16;}}
    for(const f of L.bf){f.sp.visible=day>.25;if(day<=.25)continue;if(!f.init||Math.hypot(f.ax-cx,f.az-cz)>11){f.ax=cx+(Math.random()-.5)*16;f.az=cz+(Math.random()-.5)*12;f.init=1;}
      const a=t*f.sp0+f.ph;f.sp.position.set(f.ax+Math.cos(a*1.3)*f.r+Math.sin(a*2.7)*.5,f.h+Math.sin(a*2.1)*.35,f.az+Math.sin(a)*f.r*.7);const w=.45+.45*Math.abs(Math.sin(t*14+f.ph));f.sp.scale.set(.55*w+.1,.5,1);f.sp.material.opacity=Math.min(1,day*1.4);}
    if(L.lv){const q=L.lv;for(let i=0;i<q.n;i++){const s=q.s[i];s[1]-=dt*(.5+s[3]*.07);if(s[1]<0){s[1]=9+Math.random()*3;s[0]=Math.random()*20-10;s[2]=Math.random()*16-8;}const k=i*3;q.p[k]=cx+s[0]+Math.sin(t*.9+s[3]*3)*.8;q.p[k+1]=s[1];q.p[k+2]=cz+s[2]+Math.cos(t*.7+s[3])*.5;}q.o.geometry.attributes.position.needsUpdate=true;q.o.material.opacity=.9*day;q.o.visible=day>.1;}
    if(L.dust){const q=L.dust;for(let i=0;i<q.n;i++){const s=q.s[i];s[1]+=dt*.12;if(s[1]>7)s[1]=0;const k=i*3;q.p[k]=cx+s[0]+Math.sin(t*.4+s[3]*2)*.6;q.p[k+1]=s[1]+.3;q.p[k+2]=cz+s[2]+Math.cos(t*.3+s[3])*.4;}q.o.geometry.attributes.position.needsUpdate=true;}
  };}
// ---- Cripta: paredes de tijolo a partir da grade, plataforma e escada
function crpExtras(sc,add,skipWalls){
  const gr=ZONE.grid,[TW,TH,OY]=ZONE.cell||[48,45,9];if(!gr)return;
  const rows=gr.length,cols=gr[0].length,isF=(x,y)=>y>=0&&y<rows&&x>=0&&x<cols&&gr[y][x]!=='#';
  const brick=crTex((x,w,h)=>{x.fillStyle='#16181f';x.fillRect(0,0,w,h);for(let j=0;j<4;j++)for(let i=-1;i<3;i++){const px=i*(w/2)+(j%2?w/4:0)+1,py=j*h/4+2;x.fillStyle=`hsl(228,${6+Math.random()*10}%,${22+Math.random()*14}%)`;x.fillRect(px,py,w/2-3,h/4-4);x.fillStyle='rgba(255,255,255,.07)';x.fillRect(px,py,w/2-3,2);}},128,128);
  const slab=crTex((x,w,h)=>{x.fillStyle='#3d4150';x.fillRect(0,0,w,h);for(let i=0;i<260;i++){x.fillStyle=`rgba(${Math.random()<.5?'0,0,0':'255,255,255'},${.03+Math.random()*.06})`;x.fillRect(Math.random()*w,Math.random()*h,2+Math.random()*7,2+Math.random()*4);}x.strokeStyle='rgba(0,0,0,.4)';x.lineWidth=2;x.strokeRect(1,1,w-2,h-2);},128,128);
  const sp=[],su=[],si=[],tp=[],tu=[],ti=[];let sn=0,tn=0;const cw=TW*U,ch=TH*U;
  const sq=(P,Uv,I,n,v,uvs)=>{v.forEach(q=>P.push(...q));uvs.forEach(q=>Uv.push(...q));I.push(n,n+1,n+2,n,n+2,n+3);};
  for(let cy=0;cy<rows;cy++)for(let cx=0;cx<cols;cx++){if(gr[cy][cx]!=='#')continue;
    let near=false;for(let dy=-1;dy<=1&&!near;dy++)for(let dx=-1;dx<=1;dx++)if(isF(cx+dx,cy+dy)){near=true;break;}if(!near)continue;
    const fS=isF(cx,cy+1),fE=isF(cx+1,cy),fW=isF(cx-1,cy),h=fS?3.4:(fE||fW?1.5:.9),x0=cx*cw,x1=x0+cw,z0=(OY+cy*TH)*U,z1=z0+ch,vv=h/cw;
    sq(tp,tu,ti,tn,[[x0,h,z1],[x1,h,z1],[x1,h,z0],[x0,h,z0]],[[0,0],[1,0],[1,1],[0,1]]);tn+=4;
    sq(sp,su,si,sn,[[x0,0,z1],[x1,0,z1],[x1,h,z1],[x0,h,z1]],[[0,0],[1,0],[1,vv],[0,vv]]);sn+=4;
    if(fE){sq(sp,su,si,sn,[[x1,0,z1],[x1,0,z0],[x1,h,z0],[x1,h,z1]],[[0,0],[1,0],[1,vv],[0,vv]]);sn+=4;}
    if(fW){sq(sp,su,si,sn,[[x0,0,z0],[x0,0,z1],[x0,h,z1],[x0,h,z0]],[[0,0],[1,0],[1,vv],[0,vv]]);sn+=4;}}
  if(sn&&!skipWalls)add(new T.Mesh(bufGeo(sp,su,si,1),new T.MeshStandardMaterial({map:brick,roughness:.95,side:T.DoubleSide})));
  if(tn&&!skipWalls)add(new T.Mesh(bufGeo(tp,tu,ti,1),new T.MeshStandardMaterial({map:slab,roughness:.9,side:T.DoubleSide})));
  // plataforma elevada (trono do Rei) + escada
  const P=ZONE.crp&&ZONE.crp.plat;if(P){const H=P.elev*U/CT,w=(P.x1-P.x0)*U,d=(P.y1-P.y0)*U;sc.plat={H,x0:P.x0,x1:P.x1,y0:P.y0,y1:P.y1};
    const box=new T.Mesh(new T.BoxGeometry(w,H,d),[0,1,2,3,4,5].map(i=>new T.MeshStandardMaterial({map:i===2?slab:brick,roughness:.9})));box.position.set((P.x0+P.x1)/2*U,H/2,(P.y0+P.y1)/2*U);add(box);
    const stp=crTex((x,w2,h2)=>{x.fillStyle='#4a4e5e';x.fillRect(0,0,w2,h2);for(let i=0;i<6;i++){x.fillStyle=`rgba(255,255,255,${i%2?.05:.12})`;x.fillRect(0,i*h2/6,w2,h2/6-3);x.fillStyle='rgba(0,0,0,.45)';x.fillRect(0,(i+1)*h2/6-3,w2,3);}},64,128);
    const a0=P.sx0*U,a1=P.sx1*U,z0=P.y1*U,z1=(P.y1+P.sh)*U;
    add(new T.Mesh(bufGeo([a0,0,z1,a1,0,z1,a1,H,z0,a0,H,z0],[0,0,1,0,1,1,0,1],[0,1,2,0,2,3],1),new T.MeshStandardMaterial({map:stp,roughness:.9,side:T.DoubleSide})));}
}
// ------------------------------------------------------------------ entidades (sprites do jogo)
const quadGeo={};
function geoFor(S0){return quadGeo[S0]||(quadGeo[S0]=(()=>{const g=new T.PlaneGeometry(S0*U,S0*U);g.translate(0,(S0/2-12)*U,0);g._shared=true;return g;})());}
const discGeo=new T.CircleGeometry(1,24);discGeo._shared=true;
function entRec(sc,e,S0){let r=sc.ents.get(e);if(r&&r.S0===S0)return r;
  if(r){sc.grp.remove(r.root);r.tex.dispose();}
  const c=cvs(S0,S0),tex=new T.CanvasTexture(c);tex.encoding=T.sRGBEncoding;tex.magFilter=T.NearestFilter;tex.minFilter=T.NearestFilter;tex.generateMipmaps=false;
  const mat=new T.MeshLambertMaterial({map:tex,transparent:true,alphaTest:.3,emissive:0xffffff,emissiveMap:tex,emissiveIntensity:.3,side:T.DoubleSide});
  if(e.kind==='boss'||e.mini)mat.emissiveIntensity=.7;
  const me=new T.Mesh(geoFor(S0),mat);me.scale.y=1/CT;
  const root=new T.Group();root.add(me);
  let gh=null;if(e.kind==='hero'||e.kind==='mob'||e.kind==='boss'){gh=new T.Mesh(geoFor(S0),new T.MeshBasicMaterial({map:tex,color:e.kind==='hero'?0xffffff:0xffc4c4,transparent:true,opacity:e.kind==='hero'?.5:.45,alphaTest:.3,depthFunc:T.GreaterDepth,depthWrite:false,side:T.DoubleSide}));gh.scale.y=1/CT;gh.renderOrder=5;root.add(gh);}
  const bl=new T.Mesh(new T.PlaneGeometry(1.3,.8),new T.MeshBasicMaterial({map:BT,transparent:true,depthWrite:false,polygonOffset:true,polygonOffsetFactor:-4}));bl.rotation.x=-Math.PI/2;bl.position.y=.03;root.add(bl);
  let ring=null;if(e.elite){ring=new T.Mesh(discGeo,new T.MeshBasicMaterial({map:ringTex,color:new T.Color(e.elCol||'#8ec2ff'),transparent:true,blending:T.AdditiveBlending,depthWrite:false,opacity:.6}));ring.rotation.x=-Math.PI/2;ring.position.y=.04;root.add(ring);}
  sc.grp.add(root);r={S0,c,cx:c.getContext('2d'),tex,me,gh,root,bl,ring,seen:0,key:''};sc.ents.set(e,r);return r;}
function drawEnt(sc,e,frame){
  const hp=e.kind==='hero'?G.hero:null;
  let fr=null,scale=1,S0;
  if(e.pet){fr=[0,0,128,128,64,116];scale=1;S0=128;}
  else{fr=entFrame(e);if(!fr)return;scale=e.kind==='boss'?(typeof bsc==='function'?bsc(e):e.T.scale):(typeof msc==='function'?msc(e):(e.sc||1));S0=Math.max(128,Math.ceil(Math.max(fr[3],fr[4])*scale*1.5/64)*64);}
  const r=entRec(sc,e,S0);r.seen=frame;
  const al=e.dead?Math.max(0,1-Math.max(0,e.deadT-.5)/.6):1;
  const dyn=e.kind==='hero'||e.kind==='boss'||e.flash>0||e.tint||e.shd>0||e.pet||e.elite||(e.dod!=null);
  const dxk=e.dx?Math.round(e.dx.y*2)+','+Math.round(e.dx.rot*60)+','+Math.round(e.dx.sx*40)+','+Math.round(e.dx.sy*40)+','+Math.round(e.dx.x*2):'',key=e.pet?'':fr[0]+','+fr[1]+','+(e.flash>0?1:0)+','+al.toFixed(2)+','+scale+','+dxk;
  if(dyn||key!==r.key){r.key=key;
    const oc=ctx,ox=G.cam.x,oy=G.cam.y,ow=G.LW,oh=G.LH;
    ctx=r.cx;ctx.setTransform(1,0,0,1,0,0);ctx.clearRect(0,0,S0,S0);ctx.imageSmoothingEnabled=false;
    G.cam.x=e.x-S0/2;G.cam.y=e.y-(S0-12);G.LW=S0;G.LH=S0;
    try{
      if(e.pet)drawPet(e,S0/2,S0-12);
      else if(e.kind==='hero'&&e.dod){if(typeof drawDodge==='function')drawDodge(e,fr,scale);else drawSprite(e,fr,scale,false,Math.min(1,.1+e.dod.t/.22));}
      else{
        const ra=e.kind==='boss'&&e.T.atlas&&((e.ent&&e.ent.k==='roar')||(e.act&&e.act.skill&&e.act.anim==='roar'&&!e.dead));
        if(ra&&typeof roarAura==='function')roarAura(e,S0/2,S0-12,0);
        if(typeof fxBoss==='function'&&fxBoss(e)){e.tint=bossTint(e);if(e.gh&&e.gh.length)drawGhosts(e);}
        drawSprite(e,fr,scale,e.flash>0,al);if(e.tint)e.tint=null;
        if(e.shd>0&&e.type==='skrix'&&!e.dead&&typeof skShield==='function')skShield(e,S0/2,S0-12,fr,scale);
        if(ra&&typeof roarAura==='function')roarAura(e,S0/2,S0-12,1);}
    }catch(err){}
    ctx=oc;G.cam.x=ox;G.cam.y=oy;G.LW=ow;G.LH=oh;r.tex.needsUpdate=true;}
  const el=(G.crp&&typeof crpElev==='function'?crpElev(e):0)*U/CT,zz=(e.zoff||0)*U/CT;   /* andar e esquivar só deslizam; saltos de habilidade (zoff) continuam */
  r.root.position.set(e.x*U,el,e.y*U);r.me.position.y=zz;if(r.gh)r.gh.position.y=zz;
  const sw=e.kind==='hero'?22:e.kind==='boss'?40:(e.T?e.T.sw:22),sr=(e.T&&e.T.shr)||sw*.62,fl=zz?Math.min(.6,zz*CT/U/220):0,bs=sr*3.1*U/1.3*(1-fl);
  r.bl.scale.set(bs,bs,1);r.bl.material.opacity=Math.min(1,al*(1-fl)*(sc.mood==='dark'?.9:1));
  if(r.ring){const p=.5+.5*Math.sin(G.t*4+e.x),q=(sw*.8+3*p)*U;r.ring.scale.set(q*1.1,q*1.1,1);r.ring.visible=!e.dead;}
  return r;
}
// ------------------------------------------------------------------ projeção e entrada
const tmp=new T.Vector3();
function toScreen(x,y,hpx){tmp.set(x*U,(hpx||0)*U/CT,y*U).project(cam);return [(tmp.x+1)/2*stageEl.clientWidth,(1-tmp.y)/2*stageEl.clientHeight,tmp.z];}
V3.toScreen=toScreen;
function pxScale(x,y){const a=toScreen(x,y,0),b=toScreen(x,y,10);return Math.max(.2,Math.abs(a[1]-b[1])/10);}
V3.pick=function(cx,cy){const r=stageEl.getBoundingClientRect(),nx=(cx-r.left)/r.width*2-1,ny=-((cy-r.top)/r.height)*2+1;
  const ray=new T.Raycaster();ray.setFromCamera({x:nx,y:ny},cam);const o=ray.ray.origin,d=ray.ray.direction;if(Math.abs(d.y)<1e-5)return [G.hero.x,G.hero.y];
  if(scn&&scn.plat){const P=scn.plat,t=(P.H-o.y)/d.y,X=(o.x+d.x*t)/U,Y=(o.z+d.z*t)/U;if(t>0&&X>=P.x0&&X<=P.x1&&Y>=P.y0&&Y<=P.y1)return [X,Y];}
  const t=-o.y/d.y;return [(o.x+d.x*t)/U,(o.z+d.z*t)/U];};
V3.hitNpc=function(cx,cy){if(!scn)return null;const r=stageEl.getBoundingClientRect(),x=cx-r.left,y=cy-r.top;let best=null,bd=1e9;
  for(const n of (G.npcs||[])){const f=toScreen(n.x,n.y,0),t=toScreen(n.x,n.y,50),w=Math.abs(t[1]-f[1])*.45+8;if(x>f[0]-w&&x<f[0]+w&&y>t[1]-6&&y<f[1]+10){const d=Math.abs(x-f[0]);if(d<bd){bd=d;best=n;}}}return best;};
V3.hitDoor=function(cx,cy){if(!scn||!scn.houses.length)return null;const r=stageEl.getBoundingClientRect(),x=cx-r.left,y=cy-r.top;
  for(const g of scn.houses){const u=g.userData,b=u.box,pts=[[b.min.x,0,b.max.z],[b.max.x,0,b.max.z],[b.min.x,u.h+1.5,b.min.z+.5],[b.max.x,u.h+1.5,b.min.z+.5]].map(p=>{tmp.set(p[0],p[1],p[2]).project(cam);return [(tmp.x+1)/2*stageEl.clientWidth,(1-tmp.y)/2*stageEl.clientHeight];});
    const xs=pts.map(p=>p[0]),ys=pts.map(p=>p[1]);if(x>Math.min(...xs)&&x<Math.max(...xs)&&y>Math.min(...ys)&&y<Math.max(...ys)){const id=u.id.slice(2);const d=(ZONE.doors||[]).find(q=>q.id===id);if(d)return d;}}return null;};
// ------------------------------------------------------------------ laço de desenho
let frameNo=0,camT=null,shown=false,bad=0,zk=1,camBossId=null,camKick=0;
V3.render=function(){
  try{render3();if(!shown){shown=true;}}catch(err){bad++;V3.err=String(err&&err.message||err);console.error('[v3]',err);if(bad>=3){V3.ready=false;document.body.classList.remove('v3on');if(typeof toast==='function')toast('Modo 2.5D desligado neste aparelho: '+V3.err,5000);}}
};

// ---- decais de chão (rachaduras/buracos) como planos 3D DEITADOS no próprio chão: mesma perspectiva, luz e profundidade do terreno
function syncDecals(){
  if(!scn||typeof G==='undefined'||typeof gdSprite!=='function')return;
  const D=G.gdec||[];let dg=scn.dg;if(!dg){dg=scn.dg=new T.Group();scn.grp.add(dg);}
  const live=new Set();
  for(const d of D){
    const t=d.t-(d.delay||0);if(t<0)continue;live.add(d);
    const spr=gdSprite(d.kind,d.R,d.th,d.sd,d.L),w=spr.width*2*U,hh=spr.height*2*U;
    let m=d._m;
    if(!m){
      if(!spr._tx){const tx=new T.CanvasTexture(spr);tx.encoding=T.sRGBEncoding;tx.magFilter=T.NearestFilter;tx.minFilter=T.NearestFilter;tx.generateMipmaps=false;spr._tx=tx;}
      const geo=new T.PlaneGeometry(w,hh);geo.rotateX(-Math.PI/2);if(d.kind==='line')geo.translate(w/2,0,0);
      const mat=new T.MeshStandardMaterial({map:spr._tx,transparent:true,depthWrite:false,roughness:1,metalness:0,polygonOffset:true,polygonOffsetFactor:-2,polygonOffsetUnits:-2});
      const mesh=new T.Mesh(geo,mat);mesh.renderOrder=2;const piv=new T.Group();piv.add(mesh);dg.add(piv);d._m=piv;m=piv;m.userData.mat=mat;
    }
    const a=d.a||0,grow=Math.min(1,t/.22),fade=Math.max(0,Math.min(1,(d.life-d.t)/1.4)),mat=m.userData.mat;
    m.rotation.y=-a;
    if(d.kind==='line'){m.position.set((d.x-Math.cos(a)*spr.width)*U,.02,(d.y-Math.sin(a)*spr.width)*U);m.scale.set(Math.max(.02,grow),1,1);}
    else{m.position.set(d.x*U,.02,d.y*U);const k=d.kind==='star'?.25+.75*grow:.4+.6*Math.min(1,t/.18);m.scale.set(k,1,k);}
    mat.opacity=fade;
    const gl=typeof GDPAL!=='undefined'&&GDPAL[d.th]&&GDPAL[d.th].glow&&t<2.2;
    if(gl){mat.emissiveMap=spr._tx;mat.emissive.setRGB(1,1,1);mat.emissiveIntensity=Math.max(0,(.45+.2*Math.sin(G.t*9))*(1-t/2.2));}else{mat.emissiveIntensity=0;}
  }
  for(const c of dg.children.slice()){let ok=false;for(const d of live)if(d._m===c){ok=true;break;}if(!ok){dg.remove(c);c.traverse(o=>{if(o.geometry)o.geometry.dispose();if(o.material)o.material.dispose();});}}
}
/* EFEITOS NO CHÃO (PixelFx deitados no terreno, na mesma perspectiva do mapa): G.fx kind 'spr' com ground:true vira um plano 3D */
function syncGroundFx(){
  if(!scn||typeof G==='undefined'||typeof FXS==='undefined')return;
  let gg=scn.gfx;if(!gg){gg=scn.gfx=new T.Group();scn.grp.add(gg);}
  const live=new Set();
  for(const f of (G.fx||[])){
    if((f.k==='ringw'||f.k==='wave')&&!(f.delay>0)){
      live.add(f);let o=f._g;
      if(!o){
        const cv=document.createElement('canvas');cv.width=cv.height=128;const tx=new T.CanvasTexture(cv);tx.encoding=T.sRGBEncoding;
        const geo=new T.PlaneGeometry(1,1);geo.rotateX(-Math.PI/2);
        const mat=new T.MeshBasicMaterial({map:tx,transparent:true,depthWrite:false,polygonOffset:true,polygonOffsetFactor:-3,polygonOffsetUnits:-3,blending:f.k==='ringw'?T.AdditiveBlending:T.NormalBlending});
        const mesh=new T.Mesh(geo,mat);mesh.renderOrder=3;gg.add(mesh);o=f._g={mesh,tx,mat,cv};
      }
      const t=1-f.life/f.max,al=Math.max(0,1-t),c=o.cv.getContext('2d');c.clearRect(0,0,128,128);
      let r;
      if(f.k==='ringw'){r=Math.max(4,f.r1*(1-Math.pow(1-t,2.2)));const inner=Math.max(0,r-f.w*(1-t*.5)-4)/r*64;
        const g=c.createRadialGradient(64,64,inner,64,64,64);g.addColorStop(0,'rgba(0,0,0,0)');g.addColorStop(.72,f.col);g.addColorStop(1,'rgba(0,0,0,0)');c.fillStyle=g;c.beginPath();c.arc(64,64,64,0,7);c.fill();o.mat.opacity=al*.9;}
      else{r=Math.max(2,f.r1*(1-Math.pow(1-t,2)));c.strokeStyle=f.col;c.lineWidth=Math.max(1.5,(f.w*(1-t)+1)/r*60);c.beginPath();c.arc(64,64,60,0,7);c.stroke();o.mat.opacity=al;}
      o.tx.needsUpdate=true;o.mesh.scale.set(r*2*U,1,r*2*U);o.mesh.position.set(f.x*U,.03,f.y*U);
      continue;
    }
    if(f.k!=='spr'||!f.ground)continue;const S=FXS[f.n];if(!S||!S.m)continue;
    const dl=f.delay||0;if(dl>0)continue;const m=S.m,age=(f.max-f.life);if(age<0)continue;
    live.add(f);let o=f._g;
    if(!o){
      const tx=new T.Texture(S.im);tx.encoding=T.sRGBEncoding;tx.magFilter=T.NearestFilter;tx.minFilter=T.NearestFilter;tx.generateMipmaps=false;tx.needsUpdate=true;
      const w=m.w*f.sc*U,h=m.h*f.sc*U,geo=new T.PlaneGeometry(w,h);geo.rotateX(-Math.PI/2);
      const mat=new T.MeshBasicMaterial({map:tx,transparent:true,depthWrite:false,polygonOffset:true,polygonOffsetFactor:-3,polygonOffsetUnits:-3,blending:f.add?T.AdditiveBlending:T.NormalBlending});
      const mesh=new T.Mesh(geo,mat);mesh.renderOrder=3;gg.add(mesh);o=f._g={mesh,tx,mat};
    }
    const t=Math.min(.999,age/f.max),i=Math.min(m.n-1,Math.floor(t*m.n)),iw=S.im.width,ih=S.im.height;
    o.tx.repeat.set(m.w/iw,m.h/ih);o.tx.offset.set(((i%m.cols)*m.w)/iw,1-(Math.floor(i/m.cols)*m.h+m.h)/ih);
    /* o ponto de ancora do quadro cai sobre (x,y) no chao */
    o.mesh.position.set((f.x+(m.w/2-m.ox)*f.sc)*U,.03,(f.y+(m.h/2-m.oy)*f.sc*1.0)*U);
  }
  for(const c of gg.children.slice()){let ok=false;for(const f of live)if(f._g&&f._g.mesh===c){ok=true;break;}if(!ok){gg.remove(c);if(c.geometry)c.geometry.dispose();if(c.material){if(c.material.map)c.material.map.dispose();c.material.dispose();}}}
}

/* EFEITOS 3D REAIS (k:'m3'): malhas three.js no mundo (perspectiva 2.5D de verdade). Unidades dos modelos = px do jogo (grupo escalado por U*sc). */
const M3={};
function _tx(w,h,draw){const cv=document.createElement('canvas');cv.width=w;cv.height=h;draw(cv.getContext('2d'),w,h);const tx=new T.CanvasTexture(cv);tx.encoding=T.sRGBEncoding;return tx;}
function _mt(col,op,add,map){return new T.MeshBasicMaterial({color:col,map:map||null,transparent:true,opacity:op,depthWrite:false,blending:add?T.AdditiveBlending:T.NormalBlending,side:T.DoubleSide});}
function _ext(pts,d){const sh=new T.Shape();pts.forEach((p,i)=>i?sh.lineTo(p[0],p[1]):sh.moveTo(p[0],p[1]));sh.closePath();const g=new T.ExtrudeGeometry(sh,{depth:d,bevelEnabled:false});g.translate(0,0,-d/2);return g;}
const ez=t=>t*t;
/* JULGAMENTO: espada de luz gigante cai do ceu e crava no alvo, com coluna de luz */
M3.sword={build(f,g){
  const bl=new T.Mesh(_ext([[0,0],[7,18],[7,84],[-7,84],[-7,18]],3),_mt(0xfff6cc,1,false));
  const gl=new T.Mesh(_ext([[0,-6],[10,16],[10,90],[-10,90],[-10,16]],4),_mt(0xffd860,.4,true));
  const gd=new T.Mesh(new T.BoxGeometry(38,6,8),_mt(0xe8b840,1,false));gd.position.y=88;
  const gr=new T.Mesh(new T.CylinderGeometry(3.4,3.4,26,8),_mt(0xb07a30,1,false));gr.position.y=104;
  const pm=new T.Mesh(new T.SphereGeometry(5,10,8),_mt(0xffe890,1,false));pm.position.y=120;
  const rs=new T.Mesh(new T.BoxGeometry(2.4,60,.6),_mt(0xffffff,.9,true));rs.position.set(0,50,2.2);
  const sw=new T.Group();sw.add(gl,bl,gd,gr,pm,rs);g.add(sw);g.userData.sw=sw;
  const col=new T.Mesh(new T.CylinderGeometry(20,20,520,20,1,true),_mt(0xffe890,0,true,_tx(2,64,(c,w,h)=>{const q=c.createLinearGradient(0,0,0,h);q.addColorStop(0,'rgba(255,255,255,0)');q.addColorStop(.5,'rgba(255,240,170,.9)');q.addColorStop(1,'rgba(255,200,80,1)');c.fillStyle=q;c.fillRect(0,0,w,h);})));col.position.y=260;g.add(col);g.userData.col=col;
  const pad=new T.Mesh(new T.CircleGeometry(40,28),_mt(0xffd860,0,true,_tx(64,64,(c,w,h)=>{const q=c.createRadialGradient(32,32,0,32,32,32);q.addColorStop(0,'rgba(255,255,220,.9)');q.addColorStop(1,'rgba(255,200,60,0)');c.fillStyle=q;c.fillRect(0,0,w,h);})));pad.rotation.x=-Math.PI/2;pad.position.y=1;g.add(pad);g.userData.pad=pad;},
 upd(f,g,t){const sw=g.userData.sw,col=g.userData.col,pad=g.userData.pad,I=.34;
  if(t<I){const k=ez(t/I);sw.position.y=420*(1-k);pad.material.opacity=.8*k;col.material.opacity=0;}
  else{const u=(t-I)/(1-I);sw.position.y=-6+Math.sin(u*40)*(1-u)*2;pad.material.opacity=.8*(1-u);col.material.opacity=Math.max(0,1-u*2.6);col.scale.set(1+u*.8,1,1+u*.8);
   const fade=u>.6?1-(u-.6)/.4:1;sw.children.forEach(c=>{if(c.userData.o===undefined)c.userData.o=c.material.opacity;c.material.opacity=c.userData.o*fade;});}
  sw.rotation.y=Math.sin(t*6)*.05;}};
/* MARTELO DIVINO: martelo gigante com sombra no chao */
M3.hammer={build(f,g){
  const hd=new T.Mesh(new T.CylinderGeometry(19,19,66,18).rotateZ(Math.PI/2),_mt(0xf2e2a8,1,false));hd.position.y=22;
  const b1=new T.Mesh(new T.CylinderGeometry(21.5,21.5,10,18).rotateZ(Math.PI/2),_mt(0xd8a838,1,false));b1.position.set(-30,22,0);const b2=b1.clone();b2.position.x=30;
  const gem=new T.Mesh(new T.SphereGeometry(9,12,8),_mt(0xffffff,1,true));gem.position.set(0,22,0);
  const hl=new T.Mesh(new T.CylinderGeometry(5.5,5.5,120,8),_mt(0x8a5a28,1,false));hl.position.y=88;
  const gl=new T.Mesh(new T.SphereGeometry(40,14,10),_mt(0xffd860,.28,true));gl.position.y=22;
  const H=new T.Group();H.add(gl,hd,b1,b2,hl,gem);g.add(H);g.userData.H=H;
  const sh=new T.Mesh(new T.CircleGeometry(46,24),_mt(0x000000,0,false));sh.rotation.x=-Math.PI/2;sh.position.y=.6;g.add(sh);g.userData.sh=sh;},
 upd(f,g,t){const H=g.userData.H,sh=g.userData.sh,I=.4;
  if(t<I){const k=ez(t/I);H.position.y=440*(1-k);H.rotation.x=.5*(1-k)+.35;sh.material.opacity=.32*k;sh.scale.setScalar(.3+.7*k);}
  else{const u=(t-I)/(1-I);H.position.y=0;H.rotation.x=.35;H.position.x=Math.sin(u*50)*(1-u)*2.5;const fade=u>.55?1-(u-.55)/.45:1;H.children.forEach(c=>{if(c.userData.o===undefined)c.userData.o=c.material.opacity;c.material.opacity=c.userData.o*fade;});sh.material.opacity=.32*fade;}}};
/* CURA: sigilo de cruz no chao + aneis de luz subindo */
M3.heal={build(f,g){
  const tx=_tx(256,256,(c,w,h)=>{c.translate(128,128);c.strokeStyle='#bfffc0';c.lineWidth=5;c.beginPath();c.arc(0,0,118,0,7);c.stroke();c.lineWidth=3;c.beginPath();c.arc(0,0,96,0,7);c.stroke();c.fillStyle='#8ef08a';c.fillRect(-14,-70,28,140);c.fillRect(-70,-14,140,28);c.fillStyle='#e8ffe0';c.fillRect(-6,-70,12,140);c.fillRect(-70,-6,140,12);for(let i=0;i<12;i++){c.rotate(Math.PI/6);c.fillStyle='#bfffc0';c.fillRect(-3,-122,6,14);}});
  const sg=new T.Mesh(new T.PlaneGeometry(240,240),_mt(0xffffff,0,true,tx));sg.rotation.x=-Math.PI/2;sg.position.y=1.2;g.add(sg);g.userData.sg=sg;
  g.userData.rg=[];for(let i=0;i<5;i++){const r=new T.Mesh(new T.TorusGeometry(54,2.4,6,40),_mt(i%2?0xd8ffd0:0x8ef08a,0,true));r.rotation.x=Math.PI/2;g.add(r);g.userData.rg.push(r);}},
 upd(f,g,t){const sg=g.userData.sg;sg.material.opacity=Math.min(1,t*6)*Math.max(0,1-Math.pow(Math.max(0,(t-.55)/.45),1.5))*.5;sg.rotation.z=t*2.2;
  g.userData.rg.forEach((r,i)=>{const u=(t-i*.09)/.6;if(u<0||u>1){r.material.opacity=0;return;}r.position.y=4+u*130;r.scale.setScalar(1.1-u*.55);r.material.opacity=Math.sin(u*Math.PI)*.9;});}};
/* CURA MAIOR: domo/cupula translucida em volta do heroi */
M3.dome={build(f,g){
  const tx=_tx(256,128,(c,w,h)=>{const q=c.createLinearGradient(0,0,0,h);q.addColorStop(0,'rgba(200,255,210,.05)');q.addColorStop(.7,'rgba(160,255,180,.22)');q.addColorStop(1,'rgba(220,255,230,.85)');c.fillStyle=q;c.fillRect(0,0,w,h);c.strokeStyle='rgba(240,255,240,.55)';c.lineWidth=2;for(let x=0;x<w;x+=32){c.beginPath();c.moveTo(x,0);c.lineTo(x,h);c.stroke();}for(let y=16;y<h;y+=28){c.beginPath();c.moveTo(0,y);c.lineTo(w,y);c.stroke();}});
  const d=new T.Mesh(new T.SphereGeometry(78,28,14,0,Math.PI*2,0,Math.PI/2),_mt(0xffffff,0,true,tx));g.add(d);g.userData.d=d;
  const rg=new T.Mesh(new T.RingGeometry(70,80,48),_mt(0xbfffd0,0,true,_tx(8,8,(c,w,h)=>{c.fillStyle='#fff';c.fillRect(0,0,w,h);})));rg.rotation.x=-Math.PI/2;rg.position.y=1.4;g.add(rg);g.userData.rg=rg;},
 upd(f,g,t){const d=g.userData.d,rg=g.userData.rg,a=Math.min(1,t*8)*Math.min(1,(1-t)*6);d.material.opacity=a*(.8+.2*Math.sin(t*40));d.rotation.y=t*3;const s=1+.03*Math.sin(t*30);d.scale.set(s,s,s);rg.material.opacity=a*.8;rg.rotation.z=-t*4;}};
/* FURIA DIVINA: asas de luz atras do heroi */
M3.wings={build(f,g){
  const pts=[[0,0],[28,34],[60,44],[96,36],[78,22],[108,10],[84,-2],[104,-22],[72,-24],[84,-46],[50,-36],[34,-60],[18,-30],[6,-20]];
  const mk=(sx)=>{const w=new T.Group();const o=new T.Mesh(_ext(pts,1),_mt(0xffc840,.38,true));const i=new T.Mesh(_ext(pts.map(p=>[p[0]*.72,p[1]*.72]),1),_mt(0xfff0b0,.42,true));w.add(o,i);w.scale.x=sx;return w;};
  const L=mk(-1),R=mk(1),pv=new T.Group();pv.add(L,R);pv.position.set(0,46,-7);g.add(pv);g.userData.L=L;g.userData.R=R;g.userData.pv=pv;},
 upd(f,g,t){const a=Math.min(1,t*10)*Math.min(1,(1-t)*8),fl=Math.sin(t*26)*.16;const {L,R,pv}=g.userData;L.rotation.y=.5+fl;R.rotation.y=-.5-fl;L.rotation.z=R.rotation.z=.1*Math.sin(t*26);pv.scale.setScalar(.6+.4*a);pv.children.forEach(w=>w.children.forEach(m=>{if(m.userData.o===undefined)m.userData.o=m.material.opacity;m.material.opacity=m.userData.o*a;}));}};
/* parede cilindrica de luz que se expande (pulso da furia) */
M3.wall={build(f,g){const c=new T.Mesh(new T.CylinderGeometry(1,1,70,36,1,true),_mt(0xffd860,0,true,_tx(2,64,(c,w,h)=>{const q=c.createLinearGradient(0,0,0,h);q.addColorStop(0,'rgba(255,255,255,0)');q.addColorStop(.5,'rgba(255,230,140,.9)');q.addColorStop(1,'rgba(255,200,60,1)');c.fillStyle=q;c.fillRect(0,0,w,h);})));c.position.y=35;g.add(c);g.userData.c=c;},
 upd(f,g,t){const c=g.userData.c,r=24+(f.r||110)*(1-Math.pow(1-t,2));c.scale.set(r,1,r);c.material.opacity=.85*(1-t);}};

/* ===== MODELOS 3D: guerreiro, ladino e mago ===== */
const _R=(a,b)=>a+Math.random()*(b-a);
function _fd(g,a){g.traverse(m=>{if(m.isMesh){const u=m.material.userData;if(u.o===undefined)u.o=m.material.opacity;m.material.opacity=u.o*a;}});}
function _gr(stops){return _tx(2,64,(c,w,h)=>{const q=c.createLinearGradient(0,0,0,h);stops.forEach(s=>q.addColorStop(s[0],s[1]));c.fillStyle=q;c.fillRect(0,0,w,h);});}
function _fc(f,d){return f.c==null?d:f.c;}
/* GIRO DE LAMINA: funil de vento com poeira orbitando */
M3.tornado={build(f,g){g.userData.L=[];for(let i=0;i<5;i++){const tx=_tx(128,32,(c,w,h)=>{c.clearRect(0,0,w,h);for(let k=0;k<26;k++){c.fillStyle='rgba(255,255,255,'+(.25+Math.random()*.6)+')';c.fillRect(Math.random()*w,Math.random()*h,10+Math.random()*30,2);}});tx.wrapS=T.RepeatWrapping;
  const m=new T.Mesh(new T.CylinderGeometry(30+i*11,20+i*10,30,28,1,true),_mt(i%2?0xfff0d0:0xd8e8ff,.8,true,tx));m.position.y=15+i*27;g.add(m);g.userData.L.push(m);}
  g.userData.D=[];for(let i=0;i<8;i++){const b=new T.Mesh(new T.BoxGeometry(5,5,5),_mt(i%2?0xb8a070:0x8a7a5a,1,false));g.add(b);g.userData.D.push(b);}},
 upd(f,g,t){const a=Math.min(1,t*12)*Math.min(1,(1-t)*10),T0=t*f.max;g.userData.L.forEach((m,i)=>{m.material.map.offset.x=-T0*(1.4+i*.3);m.rotation.y=T0*(2+i*.4);m.material.opacity=.8*a;});
  g.userData.D.forEach((b,i)=>{const an=T0*(5+i*.5)+i*.8,h=10+((T0*40+i*37)%110),r=24+h*.32;b.position.set(Math.cos(an)*r,h,Math.sin(an)*r);b.rotation.set(an,an*1.3,0);b.material.opacity=a;});}};
/* onda de choque: casca hemisferica que se expande */
M3.shock={build(f,g){const c=_fc(f,0xffe0b0);const m=new T.Mesh(new T.SphereGeometry(1,28,12,0,Math.PI*2,0,Math.PI/2),_mt(c,.8,true,_gr([[0,'rgba(255,255,255,.05)'],[.6,'rgba(255,255,255,.35)'],[1,'rgba(255,255,255,1)']])));g.add(m);g.userData.m=m;},
 upd(f,g,t){const r=(f.r||100)*(1-Math.pow(1-t,2.4));g.userData.m.scale.set(r,r*.55,r);g.userData.m.material.opacity=.85*(1-t);}};
/* pedras que voam e caem */
M3.rocks={build(f,g){g.userData.P=[];const c=_fc(f,0x8a7a60),n=f.n||10;for(let i=0;i<n;i++){const m=new T.Mesh(new T.DodecahedronGeometry(_R(3,7)*(f.s||1)),_mt(i%3?c:0xd8c8a8,1,false));const a=_R(0,6.28),v=_R(30,(f.r||100)*1.1);g.add(m);g.userData.P.push({m,vx:Math.cos(a)*v,vz:Math.sin(a)*v,vy:_R(130,260),sp:_R(3,9)});}},
 upd(f,g,t){const T0=t*f.max;g.userData.P.forEach(p=>{const tt=Math.min(T0,1.1);p.m.position.set(p.vx*tt*.7,Math.max(0,p.vy*tt-420*tt*tt),p.vz*tt*.7);p.m.rotation.x=T0*p.sp;p.m.rotation.y=T0*p.sp*.7;});_fd(g,t>.75?(1-t)*4:1);}};
/* ABALO SISMICO: aneis erguidos do terreno que se propagam */
M3.ripple={build(f,g){g.userData.R=[];for(let i=0;i<3;i++){const m=new T.Mesh(new T.TorusGeometry(1,.09,6,52),_mt(i===1?0xfff0d0:0xc9a878,1,false));m.rotation.x=Math.PI/2;g.add(m);g.userData.R.push(m);}},
 upd(f,g,t){g.userData.R.forEach((m,i)=>{const u=Math.min(1,Math.max(0,(t-i*.12)/.7)),r=(f.r||110)*(.25+.75*(1-Math.pow(1-u,2)));m.scale.set(r,r*.35,r);m.position.y=6*Math.sin(u*Math.PI);m.material.opacity=Math.max(0,1-u)*(u>0?1:0);});}};
/* MURALHA: 6 escudos orbitando */
M3.shields={build(f,g){g.userData.S=[];for(let i=0;i<6;i++){const pts=[[-11,14],[11,14],[11,0],[0,-16],[-11,0]];const w=new T.Group();w.add(new T.Mesh(_ext(pts.map(p=>[p[0]*1.18,p[1]*1.18]),3.2),_mt(0xe8c050,1,false)),new T.Mesh(_ext(pts,4),_mt(0x4a78c8,1,false)),new T.Mesh(new T.SphereGeometry(3,8,6),_mt(0xfff0b0,1,false)));w.children[2].position.z=3;g.add(w);g.userData.S.push(w);}
  const rg=new T.Mesh(new T.RingGeometry(40,50,48),_mt(0x8ac8ff,.3,true));rg.rotation.x=-Math.PI/2;rg.position.y=1.3;g.add(rg);g.userData.rg=rg;},
 upd(f,g,t){const T0=t*f.max,a=Math.min(1,t*14)*Math.min(1,(1-t)*14);g.userData.S.forEach((w,i)=>{const an=T0*1.9+i*Math.PI/3;w.position.set(Math.cos(an)*46,22+Math.sin(T0*3+i)*2,Math.sin(an)*46);w.rotation.y=Math.PI/2-an;w.scale.setScalar(.3+.7*a);});g.userData.rg.rotation.z=T0;_fd(g,a);}};
/* FURIA SELVAGEM: chamas que sobem em volta do guerreiro */
M3.flames={build(f,g){g.userData.F=[];const tx=_gr([[0,'rgba(255,255,200,0)'],[.25,'rgba(255,230,120,.9)'],[.6,'rgba(255,110,30,.95)'],[1,'rgba(160,20,10,.9)']]);for(let i=0;i<8;i++){const h=i<7?52:90,m=new T.Mesh(new T.ConeGeometry(i<7?9:15,h,8,1,true).translate(0,h/2,0),_mt(i%2?0xff7a2a:0xff3a1a,.8,true,tx));const a=i*.9,r=i<7?18:0;m.position.set(Math.cos(a)*r,0,Math.sin(a)*r);m.userData.h=h;g.add(m);g.userData.F.push(m);}},
 upd(f,g,t){const T0=t*f.max,a=Math.min(1,t*10)*Math.min(1,(1-t)*10);g.userData.F.forEach((m,i)=>{m.scale.set(.9+.2*Math.sin(T0*17+i),(.75+.3*Math.sin(T0*13+i*2))*a,.9+.2*Math.cos(T0*15+i));m.rotation.y=T0*3+i;});}};
/* humo escuro */
M3.smoke={build(f,g){g.userData.P=[];const c=_fc(f,0x3a2060);for(let i=0;i<6;i++){const m=new T.Mesh(new T.SphereGeometry(_R(8,13),10,8),_mt(c,.8,false));g.add(m);g.userData.P.push({m,a:_R(0,6.28),v:_R(20,45)});}},
 upd(f,g,t){g.userData.P.forEach(p=>{p.m.position.set(Math.cos(p.a)*p.v*t*1.6,14+t*40,Math.sin(p.a)*p.v*t*1.6);p.m.scale.setScalar(.6+t*1.6);});_fd(g,1-t);}};
/* DANCA DAS SOMBRAS: corte em X de laminas roxas */
M3.xslash={build(f,g){const pts=[[-46,0],[0,5],[46,0],[0,-5]],c=_fc(f,0xb890ff);g.userData.B=[0,1].map(i=>{const b=new T.Group();b.add(new T.Mesh(_ext(pts,1),_mt(c,.9,true)),new T.Mesh(_ext(pts.map(p=>[p[0]*.8,p[1]*.4]),1),_mt(0xffffff,1,true)));b.position.y=24;b.rotation.z=(i?-1:1)*.75;g.add(b);return b;});},
 upd(f,g,t){const k=Math.min(1,t*5),a=1-Math.max(0,(t-.4)/.6);g.userData.B.forEach((b,i)=>{b.scale.set(.2+.8*(i?Math.min(1,Math.max(0,t*5-.5)):k),1,1);});_fd(g,a);}};
/* EXECUCAO: foice em arco */
M3.scythe={build(f,g){const sh=new T.Shape();sh.absarc(0,0,58,-1.0,1.0,false);sh.absarc(0,0,40,1.0,-1.0,true);const gm=new T.ExtrudeGeometry(sh,{depth:2,bevelEnabled:false});const m=new T.Mesh(gm,_mt(0xe8d8ff,1,true)),o=new T.Mesh(gm,_mt(0xb04080,.5,true));o.scale.set(1.18,1.18,1.2);const p=new T.Group();p.add(o,m);p.position.y=34;g.add(p);g.userData.p=p;},
 upd(f,g,t){const p=g.userData.p,k=Math.min(1,t*3);p.rotation.z=1.6-3.2*(1-Math.pow(1-k,2));p.rotation.y=.5;_fd(g,t<.5?1:1-(t-.5)*2);}};
/* MARCA DA MORTE: cristal rubro sobre o alvo */
M3.mark={build(f,g){const c=new T.Mesh(new T.OctahedronGeometry(11),_mt(0xff4a7a,.9,true)),k=new T.Mesh(new T.OctahedronGeometry(6),_mt(0x300010,1,false)),rg=new T.Mesh(new T.RingGeometry(22,27,6),_mt(0xff4a7a,.7,true));rg.rotation.x=-Math.PI/2;rg.position.y=1.5;c.position.y=k.position.y=72;g.add(c,k,rg);g.userData.c=c;g.userData.k=k;g.userData.rg=rg;},
 upd(f,g,t){const T0=t*f.max,e=f.ft;if(e&&e.dead){g.visible=false;return;}if(e){f.x=e.x;f.y=e.y;g.position.set(e.x*U,.02,e.y*U);}const y=72+Math.sin(T0*4)*4;g.userData.c.position.y=g.userData.k.position.y=y;g.userData.c.rotation.y=g.userData.k.rotation.y=T0*3;g.userData.rg.rotation.z=T0*2;const a=Math.min(1,t*20)*(t>.9?(1-t)*10:1);_fd(g,a);}};
/* ARMADILHA DE ESPINHOS */
M3.spikes={build(f,g){g.userData.S=[];for(let i=0;i<16;i++){const a=_R(0,6.28),d=Math.sqrt(Math.random())*(f.r||80),m=new T.Mesh(new T.ConeGeometry(_R(3,5),_R(22,36),6).translate(0,15,0),_mt(i%3?0x5a7a30:0xb8c878,1,false));m.position.set(Math.cos(a)*d,0,Math.sin(a)*d*.8);m.rotation.set(_R(-.25,.25),0,_R(-.25,.25));g.add(m);g.userData.S.push({m,d:_R(0,.15)});}},
 upd(f,g,t){const T0=t*f.max;g.userData.S.forEach((p,i)=>{const u=Math.min(1,Math.max(0,(T0-p.d)*7)),r=t>.9?(1-t)*10:1;p.m.scale.y=Math.max(.01,u*r*(.85+.15*Math.sin(T0*9+i)));});}};
/* CHUVA DE ADAGAS: adagas 3D que caem e ficam cravadas */
M3.daggers={build(f,g){g.userData.D=(f.pts||[]).map(p=>{const d=new T.Group();d.add(new T.Mesh(_ext([[0,0],[3,8],[3,26],[-3,26],[-3,8]],1.4),_mt(0xdde4f4,1,false)),new T.Mesh(new T.BoxGeometry(10,2,3),_mt(0x6a7090,1,false)),new T.Mesh(new T.CylinderGeometry(1.6,1.6,10,6),_mt(0x4a3a30,1,false)));d.children[1].position.y=28;d.children[2].position.y=34;d.scale.setScalar(1.35);g.add(d);return{d,x:p[0],z:p[1]*.9,t0:p[2],rz:_R(-.3,.3)};});},
 upd(f,g,t){const T0=t*f.max;g.userData.D.forEach(p=>{const u=(T0-p.t0)/.2;p.d.visible=u>=0;if(u<0)return;const k=Math.min(1,u);p.d.position.set(p.x,-3+(1-k)*(1-k)*300,p.z);p.d.rotation.z=p.rz;p.d.rotation.x=.12;});_fd(g,t>.8?(1-t)*5:1);}};
/* METEORO: rocha em chamas caindo na diagonal, aviso no chao */
M3.meteor={build(f,g){const rk=new T.Mesh(new T.IcosahedronGeometry(17,1),_mt(0x6a2a10,1,false)),gl=new T.Mesh(new T.SphereGeometry(24,12,10),_mt(0xff7a2a,.5,true)),tl=new T.Mesh(new T.ConeGeometry(20,130,12).translate(0,65,0),_mt(0xff5a1a,.55,true,_gr([[0,'rgba(255,255,160,0)'],[.4,'rgba(255,170,60,.7)'],[1,'rgba(255,80,20,1)']])));const m=new T.Group();m.add(gl,rk,tl);g.add(m);g.userData.m=m;g.userData.tl=tl;
  const w=new T.Mesh(new T.CircleGeometry(1,40),_mt(0xff2a10,.4,true,_tx(64,64,(c,W,H)=>{const q=c.createRadialGradient(32,32,10,32,32,32);q.addColorStop(0,'rgba(255,60,30,.25)');q.addColorStop(.85,'rgba(255,60,30,.7)');q.addColorStop(1,'rgba(255,60,30,0)');c.fillStyle=q;c.fillRect(0,0,W,H);})));w.rotation.x=-Math.PI/2;w.position.y=1.2;g.add(w);g.userData.w=w;},
 upd(f,g,t){const k=Math.min(1,t/.98),e=k*k,m=g.userData.m;m.position.set(130*(1-e),430*(1-e),0);m.children[1].rotation.x=T0r(t);const dx=130,dy=430,ang=Math.atan2(dx,dy);g.userData.tl.rotation.z=-ang;g.userData.tl.rotation.x=0;g.userData.w.scale.setScalar((f.r||120)*(.4+.6*k));g.userData.w.material.opacity=.5*(.6+.4*Math.sin(t*60));if(t>.97){m.visible=false;g.userData.w.visible=false;}}};
function T0r(t){return t*9;}
/* NOVA GELIDA: cristais de gelo brotam em anel + casca gelada */
M3.icenova={build(f,g){const sh=new T.Mesh(new T.SphereGeometry(1,24,12,0,Math.PI*2,0,Math.PI/2),_mt(0xbfeaff,.6,true,_gr([[0,'rgba(255,255,255,.1)'],[1,'rgba(220,245,255,1)']])));g.add(sh);g.userData.sh=sh;g.userData.C=[];const n=14;for(let i=0;i<n;i++){const a=i*6.283/n+_R(-.1,.1),r=(f.r||170)*_R(.62,.92),h=_R(34,64),c=new T.Mesh(new T.ConeGeometry(_R(5,8),h,5).translate(0,h/2,0),_mt(i%2?0x8ad0ff:0xdff4ff,.85,false));c.position.set(Math.cos(a)*r,0,Math.sin(a)*r*.85);c.rotation.set(_R(-.2,.2),0,_R(-.2,.2));g.add(c);g.userData.C.push({c,d:i*.012});}},
 upd(f,g,t){const r=(f.r||170)*(1-Math.pow(1-Math.min(1,t*4),3));g.userData.sh.scale.set(r,r*.5,r);g.userData.sh.material.opacity=.6*Math.max(0,1-t*3.5);g.userData.C.forEach(p=>{const u=Math.min(1,Math.max(0,(t-p.d)*6)),o=t>.85?(1-t)/.15:1;p.c.scale.setScalar(Math.max(.01,u*o));});}};
M3.iceblock={build(f,g){const b=new T.Mesh(new T.BoxGeometry(28,38,28),_mt(0xaee4ff,.45,false)),e=new T.Mesh(new T.OctahedronGeometry(10),_mt(0xffffff,.8,true));b.position.y=19;e.position.y=44;g.add(b,e);g.userData.b=b;g.userData.e=e;},
 upd(f,g,t){const m=f.ft;if(m){if(m.dead){g.visible=false;return;}g.position.set(m.x*U,.02,m.y*U);}g.userData.e.rotation.y=t*8;_fd(g,t<.06?t/.06:t>.9?(1-t)*10:1);}};
/* RAIO ARCANO: feixe 3D com aneis em espiral */
M3.beam={build(f,g){const L=f.L||300,mk=(r,c,o,add)=>new T.Mesh(new T.CylinderGeometry(r,r,L,12,1,true).rotateZ(Math.PI/2).translate(L/2,0,0),_mt(c,o,add));g.userData.o=mk(24,0xa070ff,.5,true);g.userData.i=mk(10,0xffffff,.97,true);g.add(g.userData.o,g.userData.i);g.userData.R=[];for(let i=0;i<6;i++){const r=new T.Mesh(new T.TorusGeometry(30,3.2,6,20).rotateY(Math.PI/2),_mt(0xd8c0ff,.85,true));g.add(r);g.userData.R.push(r);}
  const cap=new T.Mesh(new T.SphereGeometry(30,12,10),_mt(0xe0d0ff,.75,true));g.add(cap);g.userData.cap=cap;g.userData.end=cap.clone();g.add(g.userData.end);},
 upd(f,g,t){const H=G.hero;if(H){f.x=H.x;f.y=H.y;g.position.set(H.x*U,.02,H.y*U);}g.position.y=22*U;g.rotation.y=-(f.a||0);const L=f.L||300,p=1+.12*Math.sin(t*90),a=Math.min(1,t*14)*Math.min(1,(1-t)*14);g.userData.o.scale.set(1,p,p);g.userData.i.scale.set(1,1+.2*Math.sin(t*120),1+.2*Math.sin(t*120));g.userData.R.forEach((r,i)=>{r.position.x=((t*f.max*260+i*L/6)%L);r.rotation.x=t*f.max*8+i;});g.userData.end.position.x=L;g.userData.end.scale.setScalar(.6+.3*Math.sin(t*70));_fd(g,a);}};
/* INFERNO: poca de lava com colunas de fogo */
M3.lava={build(f,g){const r=f.r||84,d=new T.Mesh(new T.CircleGeometry(r,36),_mt(0xff6a1a,.75,true,_tx(128,128,(c,W,H)=>{const q=c.createRadialGradient(64,64,10,64,64,64);q.addColorStop(0,'rgba(255,230,120,.9)');q.addColorStop(.55,'rgba(255,110,30,.8)');q.addColorStop(1,'rgba(120,20,0,0)');c.fillStyle=q;c.fillRect(0,0,W,H);for(let i=0;i<40;i++){c.fillStyle='rgba(60,10,0,.35)';c.fillRect(Math.random()*W,Math.random()*H,8,2);}})));d.rotation.x=-Math.PI/2;d.position.y=1.3;g.add(d);g.userData.d=d;
  const tx=_gr([[0,'rgba(255,255,200,0)'],[.3,'rgba(255,220,100,.9)'],[1,'rgba(255,70,20,1)']]);g.userData.F=[];for(let i=0;i<7;i++){const a=_R(0,6.28),dd=Math.sqrt(Math.random())*r*.75,h=_R(70,110),m=new T.Mesh(new T.CylinderGeometry(3,_R(8,13),h,8,1,true).translate(0,h/2,0),_mt(0xff6a1a,.8,true,tx));m.position.set(Math.cos(a)*dd,0,Math.sin(a)*dd*.8);g.add(m);g.userData.F.push(m);}},
 upd(f,g,t){const T0=t*f.max,a=Math.min(1,t*8)*Math.min(1,(1-t)*8);g.userData.d.material.opacity=.75*a*(.85+.15*Math.sin(T0*10));g.userData.F.forEach((m,i)=>{m.scale.set(1,(.6+.45*Math.sin(T0*9+i*1.7))*a,1);m.rotation.y=T0*2+i;});}};
/* ESTACAS DE PEDRA: pilares de rocha que sobem em ondas */
M3.stakes={build(f,g){g.userData.S=(f.pts||[]).map((p,i)=>{const h=_R(95,150),m=new T.Mesh(new T.CylinderGeometry(4,_R(15,21),h,6).translate(0,h/2,0),_mt(i%3?0x9a8a70:0x7a6a52,1,false)),c=new T.Mesh(new T.ConeGeometry(6,16,6).translate(0,h+5,0),_mt(0xe8d8b8,1,false));const w=new T.Group();w.add(m,c);w.position.set(p[0],0,p[1]*.9);w.rotation.set(_R(-.18,.18),_R(0,3),_R(-.18,.18));g.add(w);return{w,t0:p[2],h};});},
 upd(f,g,t){const T0=t*f.max;g.userData.S.forEach(p=>{const u=Math.min(1,Math.max(0,(T0-p.t0)*4.5)),o=1+.15*Math.sin(u*3.14);p.w.position.y=-p.h*(1-u)*(1-u);p.w.scale.setScalar(t>.8?Math.max(.01,(1-t)/.2):1);});}};

/* ===== MODELOS 3D: arqueiro e bardo ===== */
function _arrow(L,col){const g=new T.Group();const sh=new T.Mesh(new T.CylinderGeometry(1.3,1.3,L,6).rotateZ(Math.PI/2).translate(L/2,0,0),_mt(0xb08848,1,false)),hd=new T.Mesh(new T.ConeGeometry(3.6,10,6).rotateZ(-Math.PI/2).translate(L+3,0,0),_mt(col||0xe8eef8,1,false));g.add(sh,hd);for(let i=0;i<2;i++){const f=new T.Mesh(new T.PlaneGeometry(10,6).translate(4,0,0),_mt(0x6ac84a,1,false));f.rotation.x=i*Math.PI/2;g.add(f);}return g;}
function _note(col,sc){const g=new T.Group(),m=_mt(col,.95,true);const h=new T.Mesh(new T.SphereGeometry(5,10,8),m);h.scale.set(1.25,.8,1);h.rotation.z=.4;const st=new T.Mesh(new T.CylinderGeometry(.9,.9,22,5).translate(0,11,0),m);st.position.x=5.2;const fl=new T.Mesh(new T.BoxGeometry(8,2.4,1).translate(4,0,0),m);fl.position.set(5.2,21,0);fl.rotation.z=-.6;g.add(h,st,fl);g.scale.setScalar(sc||1);return g;}
/* arco da flecha caindo inclinada ate (x,z) no chao */
function _drop(p,L,u,k0){const dx=.35/Math.hypot(.35,1),dy=-1/Math.hypot(.35,1),a=p.a;a.rotation.z=Math.atan2(dy,dx);a.visible=u>=0;if(u<0)return;const k=Math.min(1,u),s=330*(1-k*k),Lt=L+8;a.position.set(p.x-dx*(s+Lt),-dy*(s+Lt),p.z);}
/* CHUVA DE FLECHAS */
M3.volley={build(f,g){g.userData.A=(f.pts||[]).map(p=>{const a=_arrow(34,0xe8eef8);g.add(a);return{a,x:p[0],z:p[1]*.9,t0:p[2]};});},
 upd(f,g,t){const T0=t*f.max;g.userData.A.forEach(p=>_drop(p,34,(T0-p.t0)/.24));_fd(g,t>.8?(1-t)*5:1);}};
/* FLECHAS EXPLOSIVAS: flechas que cravam e explodem em esferas verde-agua */
M3.boomarrow={build(f,g){g.userData.A=(f.pts||[]).map(p=>{const a=_arrow(34,0x6affc0);g.add(a);const e=new T.Mesh(new T.SphereGeometry(1,16,12),_mt(0x6affc0,.7,true,_gr([[0,'rgba(255,255,255,1)'],[1,'rgba(80,255,190,.5)']])));e.position.set(p[0],10,p[1]*.9);g.add(e);const r=new T.Mesh(new T.TorusGeometry(1,.1,6,28),_mt(0xd8fff0,.9,true));r.rotation.x=Math.PI/2;r.position.set(p[0],2,p[1]*.9);g.add(r);return{a,e,r,x:p[0],z:p[1]*.9,t0:p[2]};});},
 upd(f,g,t){const T0=t*f.max,R=f.r||48;g.userData.A.forEach(p=>{const u=(T0-p.t0)/.2;_drop(p,34,u);const w=(T0-p.t0-.2-.12)/.35,on=w>=0&&w<1;p.e.visible=p.r.visible=on;if(on){const k=1-Math.pow(1-w,2);p.e.scale.setScalar(R*(.3+.7*k));p.e.material.opacity=.7*(1-w);p.r.scale.set(R*1.3*k,R*1.3*k*.4,R*1.3*k);p.r.material.opacity=.9*(1-w);}if(w>=0)p.a.visible=false;});}};
/* TEMPESTADE: leque de 8 flechas em voo com rastro */
M3.arrowfan={build(f,g){g.userData.A=[];for(let i=0;i<12;i++){const a=_arrow(30,0xe8eef8),tr=new T.Mesh(new T.CylinderGeometry(4.5,.4,150,6).rotateZ(-Math.PI/2).translate(-75,0,0),_mt(0xb8ffd0,.6,true));a.scale.setScalar(2);a.add(tr);g.add(a);g.userData.A.push({a,an:(i-5.5)*.085,t0:i*.05,tr});}},
 upd(f,g,t){const T0=t*f.max;g.userData.A.forEach(p=>{const u=(T0-p.t0)/.75;p.a.visible=u>=0&&u<1.15;if(u<0)return;const d=Math.min(u,1)*320,an=(f.a||0)+p.an;p.a.position.set(Math.cos(an)*(20+d),24,Math.sin(an)*(20+d));p.a.rotation.y=-an;p.tr.material.opacity=.6*(1-Math.min(1,u*.9));});}};
/* TIRO PERFURANTE: lanca gigante que corta o ar com aneis de choque */
M3.lance={build(f,g){const L=f.L||420,a=_arrow(80,0xf0fff4);a.scale.set(2,3.4,3.4);g.add(a);g.userData.a=a;g.userData.c=new T.Mesh(new T.CylinderGeometry(8,8,1,10,1,true).rotateZ(Math.PI/2).translate(.5,0,0),_mt(0xffffff,.95,true));g.userData.o=new T.Mesh(new T.CylinderGeometry(22,22,1,12,1,true).rotateZ(Math.PI/2).translate(.5,0,0),_mt(0x6aff9a,.5,true));g.add(g.userData.c,g.userData.o);g.userData.R=[];for(let i=0;i<7;i++){const r=new T.Mesh(new T.TorusGeometry(1,.07,6,24).rotateY(Math.PI/2),_mt(0xd8ffe8,.9,true));g.add(r);g.userData.R.push(r);}},
 upd(f,g,t){const L=f.L||420,k=Math.min(1,t/.22),d=L*k;g.rotation.y=-(f.a||0);g.position.y=24*U;g.userData.a.position.set(d-60,0,0);g.userData.c.scale.set(d,1,1);g.userData.o.scale.set(d,1+Math.sin(t*50)*.1,1+Math.sin(t*50)*.1);const fa=t>.6?Math.max(0,1-(t-.6)*2.5):1;g.userData.c.material.opacity=.9*fa;g.userData.o.material.opacity=.4*fa;g.userData.a.visible=t<.35;
  g.userData.R.forEach((r,i)=>{const px=(i+1)*L/8,u=(t-.22*px/L)/.5;r.visible=u>=0&&u<1;if(!r.visible)return;r.position.x=px;const rr=16+u*62;r.scale.set(1,rr,rr);r.material.opacity=.9*(1-u);});}};
/* PONTO FRACO (ladino): losango roxo pulsando num dos 4 lados do inimigo + anel no chao */
M3.weakpt={build(f,g){const q=new T.Group(),m=_mt(0x8a3aff,1,false);q.userData.d=new T.Mesh(new T.OctahedronGeometry(13,0),m);q.userData.d.position.y=24;q.userData.c=new T.Mesh(new T.OctahedronGeometry(4,0),_mt(0xffffff,1,true));q.userData.c.position.y=24;q.userData.r=new T.Mesh(new T.TorusGeometry(18,2.4,6,28).rotateX(Math.PI/2),_mt(0x7a2aef,1,false));q.userData.r.position.y=1;q.userData.b=new T.Mesh(new T.CylinderGeometry(3,3,40,6,1,true).translate(0,20,0),_mt(0x8a3aff,.55,false));q.add(q.userData.d,q.userData.c,q.userData.r,q.userData.b);g.add(q);g.userData.q=q;},
 upd(f,g,t){const e=f.ft,w=e&&e.wp;if(!e||e.dead||!w||!w.on){g.visible=false;return;}const q=g.userData.q,vv=[[0,-1],[-1,0],[0,1],[1,0]][w.s],r=((e.T&&e.T.rad)||14)+24,tm=G.t;f.x=e.x;f.y=e.y;g.position.set(e.x*U,.02,e.y*U);q.position.set(vv[0]*r,0,vv[1]*r*.9);
  const pu=1+.18*Math.sin(tm*9),warn=w.t>3.6?(Math.sin(tm*30)>0?1:.35):1,fi=Math.min(1,w.age*5);q.userData.d.scale.setScalar(pu);q.userData.d.rotation.y=tm*3;q.userData.c.rotation.y=-tm*4;q.userData.r.scale.setScalar(1+.25*Math.sin(tm*6));q.userData.d.position.y=24+Math.sin(tm*4)*3;_fd(g,fi*warn);}};
/* MARCA DO CACADOR: mira girando em volta do alvo */
M3.reticle={build(f,g){const m=_mt(0xff5a3a,.95,true);g.userData.a=new T.Group();g.userData.a.add(new T.Mesh(new T.TorusGeometry(24,1.8,6,40),m),new T.Mesh(new T.TorusGeometry(14,1.2,6,32),_mt(0xffa060,.8,true)));for(let i=0;i<4;i++){const k=new T.Mesh(new T.BoxGeometry(3,12,2),m);const an=i*Math.PI/2;k.position.set(Math.cos(an)*24,Math.sin(an)*24,0);k.rotation.z=an+Math.PI/2;g.userData.a.add(k);}g.userData.a.position.y=34;g.add(g.userData.a);
  g.userData.d=new T.Mesh(new T.SphereGeometry(3,8,6),_mt(0xffffff,1,true));g.userData.d.position.y=34;g.add(g.userData.d);},
 upd(f,g,t){const e=f.ft;if(e&&e.dead){g.visible=false;return;}if(e){f.x=e.x;f.y=e.y;g.position.set(e.x*U,.02,e.y*U);}const T0=t*f.max,sc=T0<.25?2.2-1.2*(T0/.25):1+.06*Math.sin(T0*6);g.userData.a.scale.setScalar(sc);g.userData.a.rotation.z=T0*1.6;g.userData.a.position.y=34+Math.sin(T0*3)*2;_fd(g,Math.min(1,T0*8)*(t>.92?(1-t)*12:1));}};
/* CRESCENDO: cascas sonoras em ondas crescentes + notas voando */
M3.soundwave={build(f,g){const tx=_tx(256,64,(c,w,h)=>{c.clearRect(0,0,w,h);for(let y=0;y<h;y+=8){c.fillStyle='rgba(255,255,255,'+(y%16?.9:.4)+')';c.fillRect(0,y,w,3);}});tx.wrapS=tx.wrapT=T.RepeatWrapping;g.userData.S=[];for(let i=0;i<3;i++){const m=new T.Mesh(new T.SphereGeometry(1,28,12,0,Math.PI*2,0,Math.PI/2),_mt([0xff8ac8,0xffd860,0xa8e8ff][i],.7,true,tx));g.add(m);g.userData.S.push(m);}
  g.userData.N=[];for(let i=0;i<9;i++){const n=_note([0xff8ac8,0xffd860,0xa8e8ff][i%3],1.2);g.add(n);g.userData.N.push({n,an:i*.7,v:_R(.8,1.1),h:_R(15,45)});}},
 upd(f,g,t){const R=f.r||130;g.userData.S.forEach((m,i)=>{const u=Math.min(1,Math.max(0,(t-i*.14)/.55)),r=R*(.5+.25*i)*(1-Math.pow(1-u,2));m.scale.set(r,r*.5,r);m.material.opacity=.7*(1-u)*(u>0?1:0);});g.userData.N.forEach(p=>{const d=(.2+t)*R*p.v*.9;p.n.position.set(Math.cos(p.an)*d,p.h+Math.sin(t*8+p.an)*6,Math.sin(p.an)*d);p.n.rotation.y=-p.an;});g.userData.N.forEach(p=>{p.n.traverse(m=>{if(m.isMesh)m.material.opacity=.95*(1-Math.max(0,(t-.6)/.4));});});}};
/* SINFONIA: pauta de cinco linhas em helice com notas */
M3.staff={build(f,g){g.userData.L=[];for(let i=0;i<5;i++){const pts=[];for(let k=0;k<=60;k++){const a=k/60*Math.PI*4+i*.25,y=8+k/60*70+i*0;pts.push(new T.Vector3(Math.cos(a)*(30+i*0),y+i*2.2,Math.sin(a)*(30+i*0)));}const tb=new T.Mesh(new T.TubeGeometry(new T.CatmullRomCurve3(pts),60,.9,5),_mt(0xffe8a0,.85,true));g.add(tb);g.userData.L.push(tb);}
  g.userData.N=[];for(let i=0;i<5;i++){const n=_note(i%2?0xff8ac8:0xa8e8ff,1);g.add(n);g.userData.N.push({n,ph:i*1.25});}},
 upd(f,g,t){const T0=t*f.max,a=Math.min(1,t*10)*Math.min(1,(1-t)*10);g.rotation.y=T0*1.2;g.userData.N.forEach(p=>{const an=T0*2.2+p.ph,y=14+((T0*20+p.ph*14)%64);p.n.position.set(Math.cos(an)*34,y,Math.sin(an)*34);p.n.rotation.y=-an;});_fd(g,a);g.userData.N.forEach(p=>p.n.traverse(m=>{if(m.isMesh)m.material.opacity=.95*a;}));}};
/* BALADA SOMBRIA: notas escuras afundam em espiral sobre o alvo */
M3.dirge={build(f,g){g.userData.N=[];for(let i=0;i<5;i++){const n=_note(i%2?0x8a40c8:0x3a1a60,1.1);g.add(n);g.userData.N.push({n,ph:i*1.26});}g.userData.P=[];for(let i=0;i<5;i++){const m=new T.Mesh(new T.SphereGeometry(_R(9,13),10,8),_mt(0x4a2070,.5,false));g.add(m);g.userData.P.push({m,a:_R(0,6.28)});}},
 upd(f,g,t){const e=f.ft;if(e&&e.dead){g.visible=false;return;}if(e){f.x=e.x;f.y=e.y;g.position.set(e.x*U,.02,e.y*U);}const T0=t*f.max;g.userData.N.forEach(p=>{const an=T0*-1.8+p.ph,y=80-((T0*22+p.ph*16)%70);p.n.position.set(Math.cos(an)*26,y,Math.sin(an)*26);p.n.rotation.y=-an;});g.userData.P.forEach((p,i)=>{p.m.position.set(Math.cos(p.a+T0)*16,8+((T0*14+i*9)%34),Math.sin(p.a+T0)*16);p.m.scale.setScalar(.7+.3*Math.sin(T0*3+i));});const a=Math.min(1,T0*5)*(t>.9?(1-t)*10:1);_fd(g,a);}};
/* HARMONIA: harpa dourada com cordas vibrando */
M3.harp={build(f,g){const gold=_mt(0xffd860,.95,true),H=new T.Group();H.add(new T.Mesh(new T.TorusGeometry(26,2.4,6,24,Math.PI),gold));const pl=new T.Mesh(new T.CylinderGeometry(2.4,2.4,52,6),gold);pl.position.x=26;pl.position.y=-26+0;pl.rotation.z=0;const base=new T.Mesh(new T.CylinderGeometry(2.4,2.4,52,6).rotateZ(Math.PI/2),gold);base.position.set(0,0,0);H.add(base);
  g.userData.S=[];for(let i=0;i<7;i++){const x=-22+i*7.3,h=Math.sqrt(Math.max(4,26*26-x*x));const st=new T.Mesh(new T.CylinderGeometry(.5,.5,h,4).translate(0,h/2,0),_mt(0xffffff,.9,true));st.position.x=x;H.add(st);g.userData.S.push(st);}H.position.set(0,26,24);g.add(H);g.userData.H=H;
  g.userData.N=[];for(let i=0;i<3;i++){const n=_note(0xffe890,1.2);g.add(n);g.userData.N.push({n,ph:i*2.1});}},
 upd(f,g,t){const T0=t*f.max,a=Math.min(1,t*10)*Math.min(1,(1-t)*10);g.userData.H.position.y=26+Math.sin(T0*2)*3;g.userData.S.forEach((s,i)=>{s.scale.x=1+Math.sin(T0*40+i)*.8;});g.userData.N.forEach(p=>{const an=T0*1.6+p.ph;p.n.position.set(Math.cos(an)*42,30+Math.sin(T0*3+p.ph)*8,Math.sin(an)*42);p.n.rotation.y=-an;});_fd(g,a);g.userData.N.forEach(p=>p.n.traverse(m=>{if(m.isMesh)m.material.opacity=.95*a;}));}};
/* CACOFONIA: lascas dissonantes deitadas que explodem para fora */
M3.shards={build(f,g){g.userData.S=[];const n=14;for(let i=0;i<n;i++){const an=i*Math.PI*2/n+_R(-.08,.08),L=_R(34,56),c=new T.Mesh(new T.ConeGeometry(_R(4,7),L,4).rotateZ(-Math.PI/2).translate(L/2,0,0),_mt(i%2?0xc040ff:0xff4a8a,.9,true));const w=new T.Group();w.add(c);w.rotation.y=-an;w.rotation.z=0;c.rotation.z=.25;g.add(w);g.userData.S.push({w,L,an,d:_R(.7,1)});}
  g.userData.N=[];for(let i=0;i<5;i++){const n=_note(0xff2a5a,1.2);g.add(n);g.userData.N.push({n,an:i*1.26+.3});}},
 upd(f,g,t){const R=f.r||140,u=Math.min(1,t/.3),e=1-Math.pow(1-u,3);g.userData.S.forEach(p=>{p.w.children[0].position.x=R*.2*e*p.d+10;p.w.scale.setScalar(.3+.7*e);});g.userData.N.forEach(p=>{const d=R*.5*e,h=Math.max(0,60*Math.sin(Math.min(1,t/.7)*Math.PI));p.n.position.set(Math.cos(p.an)*d,h+4,Math.sin(p.an)*d);p.n.rotation.z=t*9;});_fd(g,t>.65?(1-t)/.35:1);g.userData.N.forEach(p=>p.n.traverse(m=>{if(m.isMesh)m.material.opacity=.95*(t>.65?(1-t)/.35:1);}));}};
function syncM3(){
  if(!scn||typeof G==='undefined')return;
  let gg=scn.m3g;if(!gg){gg=scn.m3g=new T.Group();scn.grp.add(gg);}
  const live=new Set();
  for(const f of (G.fx||[])){
    if(f.k!=='m3'||f.delay>0)continue;const D=M3[f.n];if(!D)continue;live.add(f);let o=f._g;
    if(!o){const g=new T.Group();g.renderOrder=6;D.build(f,g);g.traverse(m=>{if(m.isMesh)m.renderOrder=6;});o=f._g={mesh:g};gg.add(g);}
    const g=o.mesh,t=Math.min(.999,1-f.life/f.max),H=G.hero;g.visible=true;if(f.need&&H&&!H[f.need]&&f.life>.05)f.life=.05;
    if(f.fol&&H){f.x=H.x;f.y=H.y;}
    g.position.set(f.x*U,.02,f.y*U);g.scale.setScalar(U*(f.sc||1));D.upd(f,g,t);
  }
  for(const c of gg.children.slice()){let ok=false;for(const f of live)if(f._g&&f._g.mesh===c){ok=true;break;}if(!ok){gg.remove(c);c.traverse(m=>{if(m.geometry)m.geometry.dispose();if(m.material){if(m.material.map)m.material.map.dispose();m.material.dispose();}});}}
}
const _c1=new T.Color(),_c2=new T.Color();
function render3(){
  if(!scn||scn.key!==G.map){
    if(scn){scn.grp.visible=false;for(const [,el] of scn.labels)el.remove();scn.labels.clear();}
    let s=scenes.get(G.map);if(!s){s=buildScene(G.map);scenes.set(G.map,s);}
    s.grp.visible=true;scn=s;camT=null;
    for(const [k,v] of scenes)if(v!==scn&&scenes.size>3){disposeScene(v);scenes.delete(k);}
  }
  size();frameNo++;const dt=1/60,t=G.t,mood=scn.mood;
  // ---- luz e atmosfera por tipo de cenário
  const nTod=TOD.n||0,wm=TOD.warm||0;
  let n,bgc,fogD,fogC,hemi,sunI,hemC=0xcfe3ff,sunC=0xfff0d0;
  if(mood==='town'||mood==='field'){
    n=nTod*(mood==='town'?1:.45);hemi=(mood==='field'?1.02:.88)-.62*n;sunI=1.15-.97*n+wm*.2;hemC=n>.5?0x6a82c8:0xcfe3ff;sunC=n>.5?0x8aa0ff:(wm>.4?0xffc890:0xfff0d0);
    bgc=_c1.setHex(0xa9c9e6).lerp(_c2.setHex(0x070b1a),Math.min(1,n*1.1));if(wm>.3)bgc.lerp(_c2.setHex(0xe6a468),(wm-.3)*.8*(1-n));
    fogD=.012+.008*n;
    if(mood==='field'){const th=(typeof ZTHEME!=='undefined'&&G.scene==='dungeon')?ZTHEME[famOf(G.zoneLv)]:null;if(th){hemC=new T.Color(hemC).multiply(_c2.set(th.mul)).getHex();}}
  }else if(mood==='dark'){n=.9;hemi=G.map==='zone_cripta2'?.95:.85;sunI=.22;hemC=0x7f8cc4;sunC=0x8aa0ff;bgc=_c1.setHex(0x04050a);fogD=.026;}
  else{n=.45;hemi=1.0;sunI=.35;hemC=0xffe6bf;sunC=0xffd9a0;bgc=_c1.setHex(0x0b0806);fogD=.004;}
  if(G.map==='zone_pantano'){n=.85;hemi=.8;hemC=0x6a86a8;sunI=.9;sunC=0xa8c4ff;bgc=_c1.setHex(0x142420);fogD=.03;}
  scn.hemi.intensity=hemi;scn.hemi.color.setHex(hemC);scn.sun.intensity=sunI;scn.sun.color.setHex(sunC);
  if(V3.proc)V3.proc.time.value=t;
  S.background=bgc.clone();S.fog=S.fog||new T.FogExp2(0x9fc4e6,.012);S.fog.color.copy(bgc);S.fog.density=fogD;R.toneMappingExposure=1.0+.15*n+(mood==='dark'?.25:0);
  // ---- câmera (segue o centro da câmera do jogo)
  // zoom cinematográfico: a câmera se afasta quando um chefe/mini-chefe chega e acompanha a luta, depois volta ao normal
  let foc=null,tgtZ=1,chan=0;
  {const B=G.boss&&!G.boss.dead?G.boss:null;let M=null,md=1e9;for(const m of G.mobs)if(m.mini&&!m.dead){const d=Math.hypot(m.x-G.hero.x,m.y-G.hero.y);if(d<md&&d<520){md=d;M=m;}}
   foc=B||M;const id=foc&&(foc.id||foc.name||'x')+(foc===B?'B':'M');
   if(id&&id!==camBossId){camBossId=id;camKick=foc===B?3.2:2.4;}else if(!id){camBossId=null;}
   if(camKick>0)camKick-=dt;
   if(foc){tgtZ=foc===B?1.34:1.22;if(foc.ent||camKick>0)tgtZ+=foc===B?.3:.2;
     const ac=foc.act;if(ac&&ac.skill&&ac.t<ac.dur){const wide={rift:.5,charge:.55,zig:.5,leap:.45,dive:.4,echo:.35,spin:.3}[ac.anim];tgtZ+=wide||.22;chan=1;}}}
  zk+=(tgtZ-zk)*Math.min(1,dt*(tgtZ>zk?1.6:.9));
  const asp=cam.aspect,dist=(window.__cd||scn.dist)*(asp<1?(1+(1-asp)*1.2)*(1+(zk-1)*.7)/(zk):1)*(asp<1?zk:zk);let tx=(G.cam.x+G.LW/2)*U,tz=(G.cam.y+G.LH/2)*U;
  if(foc&&zk>1.02){const w=Math.min(chan?.62:.45,(zk-1)*.9);tx+=(foc.x*U-tx)*w;tz+=(foc.y*U-tz)*w;}
  if(!camT)camT=new T.Vector3(tx,0,tz);camT.x+=(tx-camT.x)*.5;camT.z+=(tz-camT.z)*.5;
  const sh=G.shake>0?G.shake:0;cam.position.set(camT.x+(Math.random()-.5)*sh*.3,.9+Math.sin(TILT)*dist,camT.z-1+Math.cos(TILT)*dist);cam.lookAt(camT.x,.9,camT.z-1);
  if(mood==='field'){scn.sun.position.set(camT.x-9,15,camT.z+7);scn.sun.target.position.set(camT.x,0,camT.z);scn.sun.target.updateMatrixWorld();scn.sun.castShadow=sunI>.35;}
  G.cam.rx=Math.round(G.cam.x);G.cam.ry=Math.round(G.cam.y);
  // ---- entidades
  const h=G.hero,list=[h];
  for(const m of G.mobs)if(!(m.dead&&m.deadT>1.1))list.push(m);
  if(G.boss&&!(G.boss.dead&&G.boss.deadT>1.2))list.push(G.boss);
  if(G.petE)list.push(G.petE);
  if(G.scene==='town'){for(const q of (G.npcs||[]))list.push(q);for(const q of (G.vill||[]))list.push(q);}else if(G.scene==='dungeon'&&G.npcs&&G.npcs.length){for(const q of G.npcs)list.push(q);}
  const lim=(dist*1.15)/U*.0+Math.pow(dist*1.6,2);
  for(const e of list){if(!e||e.hide)continue;const dx=e.x*U-camT.x,dz=e.y*U-camT.z;
    if(e!==h&&dx*dx+dz*dz>lim){const r0=scn.ents.get(e);if(r0){r0.seen=frameNo;r0.root.visible=false;}continue;}
    const r=drawEnt(scn,e,frameNo);if(r)r.root.visible=true;}
  for(const [e,r] of scn.ents)if(r.seen!==frameNo){scn.grp.remove(r.root);r.tex.dispose();r.root.traverse(o=>{if(o.material&&o.material!==undefined&&!o.material.map)o.material.dispose();});scn.ents.delete(e);}
  // ---- casas na frente do herói ficam transparentes (cidade)
  if(scn.houses.length){const hd=new T.Vector3(h.x*U,1,h.y*U),dir=hd.clone().sub(cam.position),Ld=dir.length();dir.normalize();const ray=new T.Ray(cam.position,dir),hit=new T.Vector3();
   for(const g of scn.houses){const u=g.userData,p=ray.intersectBox(u.box,hit),blk=p&&cam.position.distanceTo(hit)<Ld-.3,tg=blk?.14:1;u.o+=(tg-u.o)*.3;for(const m of u.mats){m.transparent=u.o<.995;m.opacity=u.o;m.depthWrite=u.o>.6;}}}
  // ---- luzes dinâmicas (as 7 mais próximas do herói) + tocha do herói
  const hp=new T.Vector3(h.x*U,0,h.y*U),act=scn.sources.map((s,i)=>({s,i,d:s.p.distanceToSquared(hp)})).sort((a,b)=>a.d-b.d);
  const lit=mood==='dark'||mood==='room';
  scn.pool.forEach((Lt,i)=>{const a=act[i];if(!a){Lt.intensity=0;return;}const f=1+(a.s.fl?.18*Math.sin(t*11+a.i)+.1*Math.sin(t*23+a.i*2):.04*Math.sin(t*3+a.i));Lt.position.copy(a.s.p);Lt.color.setHex(a.s.c);
    Lt.intensity=a.s.k*(lit?(mood==='room'?.9:1.05):(.15+Math.max(n,a.s.night*.6*Math.min(1,n*2.5)))*(n>.05||a.s.night?1:.25))*f;Lt.distance=lit?12:11;});
  scn.sources.forEach((s,i)=>{const gl=scn.glows[i];if(s.nog)return;const f=1+(s.fl?.2*Math.sin(t*11+i):.05*Math.sin(t*3+i));gl.material.opacity=lit?.85:Math.min(1,.12+Math.max(n,s.night*.5*Math.min(1,n*2.5))*.9);gl.scale.set(1.4*f,1.4*f,1);});
  scn.hl.position.set(h.x*U,1.8+(G.crp&&typeof crpElev==='function'?crpElev(h)*U/CT:0),h.y*U+.3);scn.hl.intensity=mood==='dark'?1.5:G.map==='zone_pantano'?1.1:Math.max(0,(n-.3)*.9);scn.hl.distance=9;scn.hl.color.setHex(0xffb870);
  if(scn.fireGeos.length){const f=Math.floor(t*8)%4,fi=ATLAS_J['fi'+f],b=ATLAS_J['bf'+f],AW=ATLAS.width,AH=ATLAS.height;if(fi&&b)for(const geo of scn.fireGeos){const uv=geo.attributes.uv;[[b,0],[fi,4]].forEach(([a,o])=>{for(let i=0;i<4;i++)uv.setXY(o+i,(a[0]+[0,1,1,0][i]*a[2])/AW,1-(a[1]+[0,0,1,1][i]*a[3])/AH);});uv.needsUpdate=true;}}
  if(scn.lifeUpd)scn.lifeUpd(t,dt);
  if(scn.exitUpd)scn.exitUpd(t);
  if(scn.lifeFn)scn.lifeFn(t,dt,n,camT.x,camT.z);
  if(scn.flies){const p=scn.flies.pts.geometry.attributes.position,b=scn.flies.base;for(let i=0;i<scn.flies.n;i++){p.setY(i,.8+((i*37)%10)/6+Math.sin(t*1.5+i)*.3);p.setX(i,b[i*3]+Math.sin(t*.8+i)*.4);}p.needsUpdate=true;}
  if(scn.vm){scn.winMats.forEach(m=>m.emissiveIntensity=.2+n*1.4);scn.vm.uniforms.t.value=t;if(scn.pt){const i=Math.floor(t*20)%48;scn.pt.offset.set((i%8)/8,1-(Math.floor(i/8)+1)/6);}scn.pl.intensity=1.4+.4*Math.sin(t*2);}
  for(const s of scn.smoke){s.t+=dt;const u=(s.t%4)/4;s.sp.position.set(s.x+u*.9,s.y+u*2.6,s.z+Math.sin(u*5+s.t)*.1);const q=.5+u*1.8;s.sp.scale.set(q,q,1);s.sp.material.opacity=Math.sin(u*Math.PI)*.35*(1-n*.4);}
  if(V3.proc&&V3.proc.stU){const q=V3.proc.stU;if(!ZONE.room&&!ZONE.dark&&h){const v=new T.Vector3(h.x*U,1.1,h.y*U).project(cam),bs=R.getDrawingBufferSize(new T.Vector2());q.hp.value.set((v.x*.5+.5)*bs.x,(v.y*.5+.5)*bs.y);q.hz.value=(v.z+1)/2;q.r.value=bs.x*.2;}else q.r.value=0;}
  try{syncDecals();}catch(e){}try{syncGroundFx();}catch(e){}try{syncM3();}catch(e){console.error('m3',e);}
  R.render(S,cam);
  overlay2D(h,list);
}
// ---- camada 2D por cima: efeitos do jogo, itens, números e nomes
function overlay2D(h,list){
  const cvEl=$('cv'),k=cvEl.width/stageEl.clientWidth;ctx.setTransform(1,0,0,1,0,0);ctx.clearRect(0,0,cvEl.width,cvEl.height);
  const base=(x,y,fn,el)=>{const s=pxScale(x,y),p=toScreen(x,y,el||0);ctx.save();ctx.setTransform(k*s,0,0,k*s,k*p[0],k*p[1]);ctx.imageSmoothingEnabled=false;try{fn(s);}catch(err){}ctx.restore();};
  {const s0=toScreen(h.x,h.y,0),s1=toScreen(h.x+100,h.y,0),s2=toScreen(h.x,h.y+100,0),a=(s1[0]-s0[0])/100,b=(s1[1]-s0[1])/100,c=(s2[0]-s0[0])/100,d=(s2[1]-s0[1])/100,cx=G.cam.rx,cy=G.cam.ry;
   ctx.setTransform(k*a,k*b,k*c,k*d,k*(s0[0]+a*(cx-h.x)+c*(cy-h.y)),k*(s0[1]+b*(cx-h.x)+d*(cy-h.y)));ctx.imageSmoothingEnabled=false;
   try{if(typeof drawZones==='function')drawZones(ctx,cx,cy);}catch(err){}
   try{drawProjs(ctx,cx,cy);drawMProjs(ctx,cx,cy);drawFx(ctx,cx,cy);GX.draw(ctx,cx,cy);AMB.draw(ctx,cx,cy);}catch(err){}}
  ctx.setTransform(1,0,0,1,0,0);
  // baú
  if(G.chest){const C=G.chest;base(C.x,C.y,()=>{const p=.5+.5*Math.sin(G.t*4);ctx.fillStyle='rgba(0,0,0,.35)';ctx.beginPath();ctx.ellipse(0,1,10,3.4,0,0,7);ctx.fill();
    if(!C.open){ctx.globalCompositeOperation='lighter';ctx.globalAlpha=.25+.2*p;ctx.fillStyle='#ffc83a';ctx.beginPath();ctx.ellipse(0,-4,17,8,0,0,7);ctx.fill();ctx.globalCompositeOperation='source-over';ctx.globalAlpha=1;}
    ctx.fillStyle='#2a1608';ctx.fillRect(-9,-12,18,13);ctx.fillStyle='#7a4a22';ctx.fillRect(-8,-7,16,7);ctx.fillStyle='#9a6430';ctx.fillRect(-8,-C.open*5-11,16,5);ctx.fillStyle='#d8a838';ctx.fillRect(-8,-7,16,1);ctx.fillRect(-1,-6,2,4);ctx.fillRect(-5,-7,1,7);ctx.fillRect(4,-7,1,7);
    if(C.open){ctx.globalCompositeOperation='lighter';ctx.globalAlpha=.6;ctx.fillStyle='#ffe08a';ctx.fillRect(-7,-9,14,3);}});}
  // itens no chão (feixe por raridade, ícone, nome)
  const lbl=[];
  for(const L of G.loot){const sp=toScreen(L.x,L.y,0);if(sp[0]<-60||sp[0]>stageEl.clientWidth+60||sp[1]<-60||sp[1]>stageEl.clientHeight+80)continue;
    const R0=RAR[L.it.rar],rar=L.it.rar,landed=L.t>=L.fly,b=(L.t>=L.fly&&L.t<L.fly+L.rest)?Math.abs(Math.sin(G.t*4+L.x))*2.5:0,hh=L.h||0;
    base(L.x,L.y,()=>{ctx.fillStyle='rgba(0,0,0,.35)';ctx.beginPath();ctx.ellipse(0,0,6,2.4,0,0,7);ctx.fill();ctx.globalCompositeOperation='lighter';
      if(rar>=1&&landed){const bh=[0,36,66,104,170][rar],bw=[0,5,8,12,19][rar],pl=.85+.15*Math.sin(G.t*4+L.x),gg=ctx.createLinearGradient(0,-bh,0,0);gg.addColorStop(0,'rgba(0,0,0,0)');gg.addColorStop(.55,R0.c+'88');gg.addColorStop(1,R0.c);
        ctx.globalAlpha=Math.min(1,(.3+.1*rar)*pl);ctx.fillStyle=gg;ctx.fillRect(-bw/2,-bh,bw,bh);
        ctx.globalAlpha=Math.min(1,.45*pl);const g2=ctx.createLinearGradient(0,-bh*.8,0,0);g2.addColorStop(0,'rgba(255,255,255,0)');g2.addColorStop(1,'rgba(255,255,255,.9)');ctx.fillStyle=g2;ctx.fillRect(-Math.max(1,bw*.2),-bh*.8,Math.max(2,bw*.4),bh*.8);
        if(rar>=3){const ph=(G.t*(rar>=4?1.1:.8)+L.x*.01)%1;ctx.save();ctx.scale(1,.42);ctx.globalAlpha=(1-ph)*.7;ctx.strokeStyle=R0.c;ctx.lineWidth=rar>=4?3:2;ctx.beginPath();ctx.arc(0,0,8+ph*(rar>=4?46:32),0,7);ctx.stroke();ctx.restore();ctx.globalAlpha=1;}
      if(rar>=4){const pl2=.7+.3*Math.sin(G.t*6+L.x);ctx.globalAlpha=pl2;const g3=ctx.createLinearGradient(0,-bh*1.1,0,0);g3.addColorStop(0,'rgba(255,255,255,0)');g3.addColorStop(1,'rgba(255,240,200,.95)');ctx.fillStyle=g3;ctx.fillRect(-2.2,-bh*1.1,4.4,bh*1.1);ctx.globalAlpha=1;}
      ctx.save();ctx.scale(1,.42);const rg=ctx.createRadialGradient(0,0,1,0,0,10+rar*6);rg.addColorStop(0,R0.c);rg.addColorStop(1,'rgba(0,0,0,0)');ctx.globalAlpha=.55*pl;ctx.fillStyle=rg;ctx.beginPath();ctx.arc(0,0,10+rar*6,0,7);ctx.fill();ctx.restore();
        if(rar>=3){ctx.globalAlpha=.9;ctx.fillStyle='#fff';for(let q=0;q<rar;q++){const tt=((G.t*18+q*41+L.x*.7)%bh);ctx.fillRect(Math.round(Math.sin(G.t*3+q*2+L.x)*bw*.6),Math.round(-tt),1,1);}}}
      ctx.globalCompositeOperation='source-over';ctx.globalAlpha=1;
      const im=IMG_ICO[L.it.icon],iy=Math.round(-hh-17-b);
      if(im){ctx.shadowColor='rgba(0,0,0,.85)';ctx.shadowBlur=3;ctx.drawImage(im,-8,iy,16,16);ctx.shadowBlur=0;ctx.shadowColor='transparent';}else{ctx.fillStyle=R0.c;ctx.fillRect(-3,iy+5,6,6);}});
    if(landed){const s=pxScale(L.x,L.y),p=toScreen(L.x,L.y,hh+20+b);lbl.push({x:p[0],y:p[1]-3*s,t:L.it.name||'Item',c:R0.c,r:rar,s});}}
  if(lbl.length){lbl.sort((a,b)=>b.y-a.y);const placed=[];ctx.textAlign='center';
    for(const l of lbl){const fs=Math.max(8,7.5*l.s*k);ctx.font='700 '+fs+'px Rubik,sans-serif';const w=ctx.measureText(l.t).width+4*k;let y=l.y*k,nn=0;while(nn<8&&placed.some(o=>l.x*k-w/2<o.x+o.w&&l.x*k+w/2>o.x&&y-fs<o.y+fs+2&&y+2>o.y-fs)){y-=fs+2;nn++;}placed.push({x:l.x*k-w/2,w,y});
      ctx.lineWidth=2.4*k;ctx.lineJoin='round';ctx.strokeStyle='rgba(10,6,10,.95)';ctx.strokeText(l.t,l.x*k,y);ctx.fillStyle=l.r>=1?l.c:'#d8d2c0';ctx.fillText(l.t,l.x*k,y);}}
  // Trevas do Rei Esquecido: só enxerga ao redor do herói e do chefe
  if(G.darkT>0){const k2=k,fade=Math.min(1,G.darkT/1.2,(16-G.darkT)/1.2+.2);ctx.save();ctx.setTransform(1,0,0,1,0,0);ctx.fillStyle='rgba(2,2,8,'+(.9*fade)+')';ctx.fillRect(0,0,cvEl.width,cvEl.height);ctx.globalCompositeOperation='destination-out';
    const hole=(e,R)=>{const s=pxScale(e.x,e.y),p=toScreen(e.x,e.y,20),rr=R*s*k2,g=ctx.createRadialGradient(p[0]*k2,p[1]*k2,rr*.25,p[0]*k2,p[1]*k2,rr);g.addColorStop(0,'rgba(0,0,0,'+fade+')');g.addColorStop(1,'rgba(0,0,0,0)');ctx.fillStyle=g;ctx.fillRect(p[0]*k2-rr,p[1]*k2-rr,rr*2,rr*2);};
    hole(h,120);if(G.boss&&!G.boss.dead)hole(G.boss,95);for(const m of G.mobs)if(m.orb&&!m.dead)hole(m,34);ctx.restore();}
  // escudo, bônus, barra de conjuração e seta do portal
  const hel=(G.crp&&typeof crpElev==='function'?crpElev(h):0);
  if(h.shield>0){const st=Math.max(0,Math.min(1,h.shield/Math.max(1,h.maxhp*.35)));if(h.shield<(V3._sh||0)-1)V3._shHit=.35;V3._sh=h.shield;V3._shHit=Math.max(0,(V3._shHit||0)-1/60);const hit=V3._shHit>0?V3._shHit/.35:0,tm=G.t;
    base(h.x,h.y,()=>{const R=34,Rx=R*.82,Ry=R*1.12,cy0=-26;ctx.save();ctx.translate(0,cy0);
      const g=ctx.createRadialGradient(0,0,Ry*.35,0,0,Ry);g.addColorStop(0,'rgba(120,200,255,0)');g.addColorStop(.7,'rgba(110,190,255,'+(.10+.10*st+.3*hit)+')');g.addColorStop(1,'rgba(190,235,255,'+(.40+.25*st+.4*hit)+')');
      ctx.fillStyle=g;ctx.beginPath();ctx.ellipse(0,0,Rx,Ry,0,0,7);ctx.fill();
      ctx.save();ctx.beginPath();ctx.ellipse(0,0,Rx,Ry,0,0,7);ctx.clip();ctx.strokeStyle='rgba(200,240,255,'+(.22+.18*st+.4*hit)+')';ctx.lineWidth=.9;const hs=9,ox=(tm*6)%(hs*1.73);
      for(let yy=-Ry-hs;yy<Ry+hs;yy+=hs*1.5){const row=Math.round((yy+Ry)/(hs*1.5));for(let xx=-Rx-hs*2;xx<Rx+hs*2;xx+=hs*1.73){const cx=xx+(row%2?hs*.87:0)+ox-hs*1.73;ctx.beginPath();for(let k=0;k<6;k++){const an=k*Math.PI/3+Math.PI/6;ctx[k?'lineTo':'moveTo'](cx+Math.cos(an)*hs*.9,yy+Math.sin(an)*hs*.9);}ctx.closePath();ctx.stroke();}}
      const sw=((tm*.9)%1)*2-1;const sg=ctx.createLinearGradient(-Rx,sw*Ry-12,Rx,sw*Ry+12);sg.addColorStop(0,'rgba(255,255,255,0)');sg.addColorStop(.5,'rgba(255,255,255,'+(.28+.3*hit)+')');sg.addColorStop(1,'rgba(255,255,255,0)');ctx.fillStyle=sg;ctx.fillRect(-Rx,-Ry,Rx*2,Ry*2);ctx.restore();
      ctx.lineWidth=1.6+hit*2;ctx.strokeStyle='rgba(215,242,255,'+(.75+.25*Math.sin(tm*7)+hit*.4)+')';ctx.shadowColor='#8ac8ff';ctx.shadowBlur=10+hit*14;ctx.beginPath();ctx.ellipse(0,0,Rx,Ry,0,0,7);ctx.stroke();ctx.shadowBlur=0;
      ctx.lineWidth=1;ctx.strokeStyle='rgba(140,210,255,.5)';ctx.beginPath();ctx.ellipse(0,Ry*.88,Rx*.95,Ry*.18,0,0,7);ctx.stroke();
      ctx.fillStyle='#e8f8ff';for(let i=0;i<5;i++){const ph=(tm*.6+i*.2)%1,an=i*1.9+tm*.4;ctx.globalAlpha=(1-ph)*.9;ctx.fillRect(Math.cos(an)*Rx*.9-1,Ry*.8-ph*Ry*1.6,2,2);}ctx.globalAlpha=1;ctx.restore();},hel);}
  if(h.buff&&h.buff.t>0)base(h.x,h.y,()=>{ctx.strokeStyle='rgba(255,170,60,'+(.4+.3*Math.sin(G.t*9))+')';ctx.lineWidth=1;ctx.beginPath();ctx.ellipse(0,0,14,6,0,0,7);ctx.stroke();},hel);
  if(h.act&&(h.act.cast||h.act.bow)&&h.act.ch>0&&!h.act.done&&h.state!=='ko')base(h.x,h.y,()=>{const p=Math.min(1,h.act.t/(h.act.ch+.32));ctx.fillStyle='rgba(8,6,12,.88)';ctx.fillRect(-16,-66,32,6);ctx.fillStyle=CHCOL[h.cls];ctx.fillRect(-15,-65,30*p,4);ctx.strokeStyle='#000';ctx.lineWidth=1;ctx.strokeRect(-16.5,-66.5,33,7);},hel);
  if(G.scene==='town'&&!G.room&&!SAVE.entered&&ZONE.portal){const P=ZONE.portal,bob=Math.sin(G.t*5)*3;base(P.x,P.y,()=>{ctx.font='700 14px Rubik,sans-serif';ctx.textAlign='center';ctx.lineWidth=3;ctx.strokeStyle='#1a0a2a';ctx.strokeText('▼',0,-86+bob);ctx.fillStyle='#e6d2ff';ctx.fillText('▼',0,-86+bob);});}
  // barra de canalização: toda habilidade de chefe/mini-chefe mostra nome, barra enchendo e um aviso, para o jogador saber o que vem
  const SKN={forget:'Esquecimento',echo:'Eco',rift:'Fenda do Vazio',crown:'Coroa de Almas',dark:'Trevas',slam:'Pancada no chão',charge:'Investida',roar:'Rugido',leap:'Salto',summon:'Invocação',plague:'Praga',swarm:'Enxame',burrow:'Escavar',totem:'Totem',curse:'Maldição',blink:'Teletransporte',rain:'Chuva de frascos',bounce:'Frasco ricochete',potion:'Poção misteriosa',guard:'Guarda',spin:'Machadada giratória',zig:'Investida em zigue-zague',dive:'Mergulho',screech:'Grito'};
  for(const e of list){if(!e||e.dead||!e.act||!e.act.skill||(e.kind!=='boss'&&!e.mini))continue;const a=e.act,w=Math.max(.2,a.dur-.45),p=Math.min(1,a.t/w);if(a.t>=a.dur)continue;
    const sc=(e.T&&e.T.scale)||1,hh=e.kind==='boss'?170*sc+(e.zoff||0):100,nm=SKN[a.anim]||a.anim,pulse=.5+.5*Math.sin(G.t*14);
    base(e.x,e.y,()=>{const bw=64,y0=-hh-14;ctx.textAlign='center';ctx.font='800 9px Rubik,sans-serif';ctx.lineJoin='round';ctx.lineWidth=3;ctx.strokeStyle='rgba(14,4,4,.97)';
      if(p<1){ctx.fillStyle='rgba(8,4,8,.9)';ctx.fillRect(-bw/2-2,y0-2,bw+4,10);ctx.fillStyle='#3a1210';ctx.fillRect(-bw/2,y0,bw,6);const g=ctx.createLinearGradient(-bw/2,0,bw/2,0);g.addColorStop(0,'#ff8a2a');g.addColorStop(1,'#ffe060');ctx.fillStyle=g;ctx.fillRect(-bw/2,y0,bw*p,6);ctx.strokeStyle='rgba(255,200,120,'+(.5+.4*pulse)+')';ctx.lineWidth=1;ctx.strokeRect(-bw/2-1.5,y0-1.5,bw+3,9);}
      ctx.lineWidth=3;ctx.strokeStyle='rgba(14,4,4,.97)';ctx.strokeText(nm,0,y0-6);ctx.fillStyle=p<1?'#ffe9b0':'#ff7a5a';ctx.fillText(nm,0,y0-6);
      if(p<1){ctx.font='800 15px Rubik,sans-serif';ctx.globalAlpha=.55+.45*pulse;ctx.lineWidth=3;ctx.strokeText('!',-bw/2-10,y0+8);ctx.fillStyle='#ff5a3a';ctx.fillText('!',-bw/2-10,y0+8);ctx.strokeText('!',bw/2+10,y0+8);ctx.fillText('!',bw/2+10,y0+8);ctx.globalAlpha=1;}});}
  // números de combate: cada tipo tem cara própria (dano, crítico, dano recebido, cura, poção, roubo de vida)
  for(const f of G.floats){const sp=toScreen(f.x,f.y,0),a=Math.min(1,f.life/(f.max*.35)),age=f.max-f.life,pp=f.pop&&age<.18?1+(1-age/.18)*.7:1,kd=f.kd||'dmg';
    let fs=f.size*pp*G.K*1.05,X=sp[0]*k,Y=sp[1]*k;
    if(kd==='crit')fs*=1.35;else if(kd==='taken')fs*=1.1;else if(kd==='pot')fs*=1.25;else if(kd==='steal')fs*=.95;
    if(kd==='taken'&&age<.2){X+=Math.sin(age*90)*3*k;}
    ctx.save();ctx.globalAlpha=a;ctx.textAlign='center';ctx.lineJoin='round';
    const txt=String(f.t),lw=(kd==='crit'||kd==='pot'?5:4)*k*.8;
    const stroke=kd==='heal'||kd==='pot'?'rgba(6,36,14,.96)':kd==='steal'?'rgba(50,6,32,.96)':kd==='taken'?'rgba(40,2,2,.97)':'rgba(24,8,2,.96)';
    if(kd==='crit'){ // estrela dourada por trás + etiqueta
      const R0=fs*(1.05+.12*Math.sin(age*18)),n=10;ctx.save();ctx.translate(X,Y-fs*.35);ctx.rotate(age*1.2);ctx.beginPath();for(let i=0;i<n*2;i++){const r=i%2?R0*.62:R0,an=i/(n*2)*6.283;ctx.lineTo(Math.cos(an)*r,Math.sin(an)*r);}ctx.closePath();ctx.fillStyle='rgba(255,196,50,.30)';ctx.fill();ctx.restore();
      if(age<.55){ctx.font='800 '+(fs*.42)+'px Rubik,sans-serif';ctx.lineWidth=lw*.7;ctx.strokeStyle=stroke;ctx.strokeText('CRÍTICO',X,Y-fs*1.05);ctx.fillStyle='#ff9a2a';ctx.fillText('CRÍTICO',X,Y-fs*1.05);}}
    ctx.font=(f.bold||kd!=='dmg'?'800 ':'700 ')+fs+'px Rubik,sans-serif';
    let label=txt;if(kd==='steal')label=txt+' ♥';
    const w=ctx.measureText(label).width;
    if(kd==='heal'||kd==='pot'){ // cruz de cura à esquerda
      const cs=fs*.62,cx0=X-w/2-cs*.85,cy0=Y-fs*.34;ctx.fillStyle=stroke;ctx.fillRect(cx0-cs*.2-lw*.5,cy0-cs*.55-lw*.5,cs*.4+lw,cs*1.1+lw);ctx.fillRect(cx0-cs*.55-lw*.5,cy0-cs*.2-lw*.5,cs*1.1+lw,cs*.4+lw);
      ctx.fillStyle='#7dff9a';ctx.fillRect(cx0-cs*.2,cy0-cs*.55,cs*.4,cs*1.1);ctx.fillRect(cx0-cs*.55,cy0-cs*.2,cs*1.1,cs*.4);}
    ctx.lineWidth=lw;ctx.strokeStyle=stroke;ctx.strokeText(label,X,Y);
    const col=kd==='heal'||kd==='pot'?'#7dff9a':kd==='steal'?'#ff7ab8':kd==='crit'?'#ffd24a':f.col;
    if(kd==='crit'){const g=ctx.createLinearGradient(0,Y-fs,0,Y);g.addColorStop(0,'#fff6c8');g.addColorStop(1,'#ffb020');ctx.fillStyle=g;}else ctx.fillStyle=col;
    if(f.glow||kd==='heal'||kd==='pot'||kd==='steal'||kd==='crit'){ctx.shadowColor=col;ctx.shadowBlur=(kd==='crit'?14:10)*k*.8;}
    ctx.fillText(label,X,Y);ctx.shadowBlur=0;
    if(kd==='pot'&&age<1){ctx.font='700 '+(fs*.38)+'px Rubik,sans-serif';ctx.lineWidth=lw*.6;ctx.strokeStyle=stroke;ctx.strokeText('poção',X,Y+fs*.5);ctx.fillStyle='#c8ffd6';ctx.fillText('poção',X,Y+fs*.5);}
    ctx.restore();}
  ctx.setTransform(1,0,0,1,0,0);
  try{mmDraw();}catch(err){}
  // ---- nomes e barras de vida (HTML por cima)
  const seen=new Set();
  const lab=(e,txt,sub,cl,hpx,bar)=>{let el=scn.labels.get(e);if(!el){el=document.createElement('div');lbBox.appendChild(el);scn.labels.set(e,el);}
    const sig=txt+'|'+sub+'|'+cl+'|'+(bar!=null?1:0);if(el._s!==sig){el._s=sig;el.className='v3l '+cl;el.innerHTML=txt+(sub?'<small>'+sub+'</small>':'')+(bar!=null?'<div class="bar"><i></i></div>':'');el._b=el.querySelector('.bar i');el._bw=0;}
    if(bar!=null&&el._b){const bw=e.kind==='boss'?46:e.kind==='hero'?28:e.elite?32:24;if(el._bw!==bw){el._bw=bw;el._b.parentNode.style.width=bw+'px';}el._b.style.width=Math.round(clamp(e.hp/e.maxhp,0,1)*100)+'%';if(e.elite)el._b.parentNode.style.borderColor=e.elCol;}
    const el2=(G.crp&&typeof crpElev==='function'?crpElev(e):0)+(e.zoff||0),p=toScreen(e.x,e.y,hpx+el2);el.style.left=p[0]+'px';el.style.top=p[1]+'px';el.style.display=p[2]<1?'block':'none';seen.add(e);};
  for(const e of list){if(!e||e.dead||e.hide||e.kind==='vill'||e.pet)continue;
    if(e.kind==='npc'){lab(e,e.nm,'','',60);continue;}
    const tag=plateTag(e),hbar=e.kind==='hero'?G.scene!=='town':e.hp>0&&!e.ent;if(!tag&&!hbar)continue;
    const q=tag.indexOf('  Nv.'),nm=q>0?tag.slice(0,q):tag,lv=q>0?tag.slice(q+2):'';
    const cl=e.kind==='hero'?'h':e.kind==='boss'?'b':e.elite?(e.tier==='gold'?'g':'e'):'m';
    lab(e,nm,lv,cl,e.kind==='boss'?102:62,hbar?1:null);}
  for(const [e,el] of scn.labels)if(!seen.has(e)){el.remove();scn.labels.delete(e);}
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})();
