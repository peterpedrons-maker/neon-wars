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
  const sc={key,mood,grp:new T.Group(),houses:[],winMats:[],sources:[],pool:[],glows:[],smoke:[],chimneys:[],fires:[],fireGeos:[],ents:new Map(),labels:new Map(),dist:mood==='room'?12:12.5,used:0};
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
    const envP={W:ZONE.w,H:ZONE.h,WATER:mood==='town'?null:WATER,WCW,GROUND,stoneNonGreen:mood==='town'};
    let gimg=key==='zone_cripta2'?crpFloor:GROUND;
    if(procOn&&(mood==='field'||mood==='town'))gimg=V3.proc.ground(envP,mood==='town'?V3.proc.palCidade:key==='zone_pantano'?V3.proc.palPantano:V3.proc.palFloresta,key==='zone1'?5:key==='town'?9:7);
    else if(procOn){const pal=key==='zone_esgoto'?V3.proc.palEsgoto:key==='zone_cripta2'?V3.proc.palCripta2:V3.proc.palCripta;gimg=V3.proc.dungeonFloor(envP,pal,key==='zone_esgoto'?4:key==='zone_cripta2'?6:3);
      {const x=gimg.canvas.getContext('2d'),S0=gimg.canvas.width/ZONE.w;x.fillStyle='#030409';for(let cy=0;cy<dgrid.rows;cy++)for(let cx=0;cx<dgrid.cols;cx++)if(!dgrid.isF(cx,cy))x.fillRect(Math.floor((dgrid.ox+cx*dgrid.cw)*S0),Math.floor((dgrid.oy+cy*dgrid.ch)*S0),Math.ceil(dgrid.cw*S0)+1,Math.ceil(dgrid.ch*S0)+1);}}
    const pg=procOn?gimg:null,gTex=texOf(pg?pg.canvas:gimg,1);gTex.anisotropy=8;
    const gm=new T.MeshStandardMaterial({map:gTex,roughness:.95});if(mood!=='dark'){gm.bumpMap=gTex;gm.bumpScale=1.2;}
    const ground=new T.Mesh(new T.PlaneGeometry(GWu,GHu),gm);ground.rotation.x=-Math.PI/2;ground.position.set(GWu/2,0,GHu/2);add(ground);ground.receiveShadow=true;if(pg&&pg.M&&mood!=='dark')add(V3.proc.waterMesh(pg,GWu,GHu,key==='zone_pantano'?[.45,.62,.4]:undefined));if(pg&&key==='zone_esgoto')add(V3.proc.waterMesh(pg,GWu,GHu,[.35,.5,.18]));
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
    const vt=new T.Mesh(new T.PlaneGeometry(3.4,3.9),sc.vm);vt.position.set(0,2.0,.05);pg.add(vt);sc.pl=new T.PointLight(0x9a7aff,1.6,12,2);sc.pl.position.set(0,2.4,1.2);pg.add(sc.pl);}
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
  const me=new T.Mesh(geoFor(S0),mat);me.scale.y=1/CT;
  const root=new T.Group();root.add(me);
  let gh=null;if(e.kind==='hero'){gh=new T.Mesh(geoFor(S0),new T.MeshBasicMaterial({map:tex,transparent:true,opacity:.5,alphaTest:.3,depthFunc:T.GreaterDepth,depthWrite:false,side:T.DoubleSide}));gh.scale.y=1/CT;gh.renderOrder=5;root.add(gh);}
  const bl=new T.Mesh(new T.PlaneGeometry(1.3,.8),new T.MeshBasicMaterial({map:BT,transparent:true,depthWrite:false,polygonOffset:true,polygonOffsetFactor:-4}));bl.rotation.x=-Math.PI/2;bl.position.y=.03;root.add(bl);
  let ring=null;if(e.elite){ring=new T.Mesh(discGeo,new T.MeshBasicMaterial({map:ringTex,color:new T.Color(e.elCol||'#8ec2ff'),transparent:true,blending:T.AdditiveBlending,depthWrite:false,opacity:.6}));ring.rotation.x=-Math.PI/2;ring.position.y=.04;root.add(ring);}
  sc.grp.add(root);r={S0,c,cx:c.getContext('2d'),tex,me,gh,root,bl,ring,seen:0,key:''};sc.ents.set(e,r);return r;}
function drawEnt(sc,e,frame){
  const hp=e.kind==='hero'?G.hero:null;
  let fr=null,scale=1,S0;
  if(e.pet){fr=[0,0,128,128,64,116];scale=1;S0=128;}
  else{fr=entFrame(e);if(!fr)return;scale=e.kind==='boss'?e.T.scale:(e.sc||1);S0=Math.max(128,Math.ceil(Math.max(fr[3],fr[4])*scale*1.5/64)*64);}
  const r=entRec(sc,e,S0);r.seen=frame;
  const al=e.dead?Math.max(0,1-Math.max(0,e.deadT-.5)/.6):1;
  const dyn=e.kind==='hero'||e.kind==='boss'||e.flash>0||e.tint||e.shd>0||e.pet||e.elite||(e.dod!=null);
  const key=e.pet?'':fr[0]+','+fr[1]+','+(e.flash>0?1:0)+','+al.toFixed(2)+','+scale;
  if(dyn||key!==r.key){r.key=key;
    const oc=ctx,ox=G.cam.x,oy=G.cam.y,ow=G.LW,oh=G.LH;
    ctx=r.cx;ctx.setTransform(1,0,0,1,0,0);ctx.clearRect(0,0,S0,S0);ctx.imageSmoothingEnabled=false;
    G.cam.x=e.x-S0/2;G.cam.y=e.y-(S0-12);G.LW=S0;G.LH=S0;
    try{
      if(e.pet)drawPet(e,S0/2,S0-12);
      else if(e.kind==='hero'&&e.dod)drawSprite(e,fr,scale,false,Math.min(1,.1+e.dod.t/.22));
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
let frameNo=0,camT=null,shown=false,bad=0;
V3.render=function(){
  try{render3();if(!shown){shown=true;}}catch(err){bad++;V3.err=String(err&&err.message||err);console.error('[v3]',err);if(bad>=3){V3.ready=false;document.body.classList.remove('v3on');if(typeof toast==='function')toast('Modo 2.5D desligado neste aparelho: '+V3.err,5000);}}
};
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
  const asp=cam.aspect,dist=scn.dist*(asp<1?1+(1-asp)*1.2:1);const tx=(G.cam.x+G.LW/2)*U,tz=(G.cam.y+G.LH/2)*U;
  if(!camT)camT=new T.Vector3(tx,0,tz);camT.x+=(tx-camT.x)*.5;camT.z+=(tz-camT.z)*.5;
  const sh=G.shake>0?G.shake:0;cam.position.set(camT.x+(Math.random()-.5)*sh*.3,.9+Math.sin(TILT)*dist,camT.z-1+Math.cos(TILT)*dist);cam.lookAt(camT.x,.9,camT.z-1);
  if(mood==='field'){scn.sun.position.set(camT.x-9,15,camT.z+7);scn.sun.target.position.set(camT.x,0,camT.z);scn.sun.target.updateMatrixWorld();scn.sun.castShadow=sunI>.35;}
  G.cam.rx=Math.round(G.cam.x);G.cam.ry=Math.round(G.cam.y);
  // ---- entidades
  const h=G.hero,list=[h];
  for(const m of G.mobs)if(!(m.dead&&m.deadT>1.1))list.push(m);
  if(G.boss&&!(G.boss.dead&&G.boss.deadT>1.2))list.push(G.boss);
  if(G.petE)list.push(G.petE);
  if(G.scene==='town'){for(const q of (G.npcs||[]))list.push(q);for(const q of (G.vill||[]))list.push(q);}
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
  if(scn.flies){const p=scn.flies.pts.geometry.attributes.position,b=scn.flies.base;for(let i=0;i<scn.flies.n;i++){p.setY(i,.8+((i*37)%10)/6+Math.sin(t*1.5+i)*.3);p.setX(i,b[i*3]+Math.sin(t*.8+i)*.4);}p.needsUpdate=true;}
  if(scn.vm){scn.winMats.forEach(m=>m.emissiveIntensity=.2+n*1.4);scn.vm.uniforms.t.value=t;scn.pl.intensity=1.4+.4*Math.sin(t*2);}
  for(const s of scn.smoke){s.t+=dt;const u=(s.t%4)/4;s.sp.position.set(s.x+u*.9,s.y+u*2.6,s.z+Math.sin(u*5+s.t)*.1);const q=.5+u*1.8;s.sp.scale.set(q,q,1);s.sp.material.opacity=Math.sin(u*Math.PI)*.35*(1-n*.4);}
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
      if(rar>=1&&landed){const bh=[0,30,52,78,108][rar],bw=[0,4,6,8,11][rar],pl=.85+.15*Math.sin(G.t*4+L.x),gg=ctx.createLinearGradient(0,-bh,0,0);gg.addColorStop(0,'rgba(0,0,0,0)');gg.addColorStop(.55,R0.c+'88');gg.addColorStop(1,R0.c);
        ctx.globalAlpha=Math.min(1,(.3+.1*rar)*pl);ctx.fillStyle=gg;ctx.fillRect(-bw/2,-bh,bw,bh);
        ctx.globalAlpha=Math.min(1,.45*pl);const g2=ctx.createLinearGradient(0,-bh*.8,0,0);g2.addColorStop(0,'rgba(255,255,255,0)');g2.addColorStop(1,'rgba(255,255,255,.9)');ctx.fillStyle=g2;ctx.fillRect(-Math.max(1,bw*.2),-bh*.8,Math.max(2,bw*.4),bh*.8);
        ctx.save();ctx.scale(1,.42);const rg=ctx.createRadialGradient(0,0,1,0,0,10+rar*6);rg.addColorStop(0,R0.c);rg.addColorStop(1,'rgba(0,0,0,0)');ctx.globalAlpha=.55*pl;ctx.fillStyle=rg;ctx.beginPath();ctx.arc(0,0,10+rar*6,0,7);ctx.fill();ctx.restore();
        if(rar>=3){ctx.globalAlpha=.9;ctx.fillStyle='#fff';for(let q=0;q<rar;q++){const tt=((G.t*18+q*41+L.x*.7)%bh);ctx.fillRect(Math.round(Math.sin(G.t*3+q*2+L.x)*bw*.6),Math.round(-tt),1,1);}}}
      ctx.globalCompositeOperation='source-over';ctx.globalAlpha=1;
      const im=IMG_ICO[L.it.icon],iy=Math.round(-hh-17-b);
      if(im){ctx.shadowColor='rgba(0,0,0,.85)';ctx.shadowBlur=3;ctx.drawImage(im,-8,iy,16,16);ctx.shadowBlur=0;ctx.shadowColor='transparent';}else{ctx.fillStyle=R0.c;ctx.fillRect(-3,iy+5,6,6);}});
    if(landed){const s=pxScale(L.x,L.y),p=toScreen(L.x,L.y,hh+20+b);lbl.push({x:p[0],y:p[1]-3*s,t:L.it.name||'Item',c:R0.c,r:rar,s});}}
  if(lbl.length){lbl.sort((a,b)=>b.y-a.y);const placed=[];ctx.textAlign='center';
    for(const l of lbl){const fs=Math.max(8,7.5*l.s*k);ctx.font='700 '+fs+'px Rubik,sans-serif';const w=ctx.measureText(l.t).width+4*k;let y=l.y*k,nn=0;while(nn<8&&placed.some(o=>l.x*k-w/2<o.x+o.w&&l.x*k+w/2>o.x&&y-fs<o.y+fs+2&&y+2>o.y-fs)){y-=fs+2;nn++;}placed.push({x:l.x*k-w/2,w,y});
      ctx.lineWidth=2.4*k;ctx.lineJoin='round';ctx.strokeStyle='rgba(10,6,10,.95)';ctx.strokeText(l.t,l.x*k,y);ctx.fillStyle=l.r>=1?l.c:'#d8d2c0';ctx.fillText(l.t,l.x*k,y);}}
  // escudo, bônus, barra de conjuração e seta do portal
  const hel=(G.crp&&typeof crpElev==='function'?crpElev(h):0);
  if(h.shield>0)base(h.x,h.y,()=>{ctx.strokeStyle='rgba(140,200,255,'+(.5+.2*Math.sin(G.t*8))+')';ctx.lineWidth=1.5;ctx.beginPath();ctx.ellipse(0,-18,16,24,0,0,7);ctx.stroke();},hel);
  if(h.buff&&h.buff.t>0)base(h.x,h.y,()=>{ctx.strokeStyle='rgba(255,170,60,'+(.4+.3*Math.sin(G.t*9))+')';ctx.lineWidth=1;ctx.beginPath();ctx.ellipse(0,0,14,6,0,0,7);ctx.stroke();},hel);
  if(h.act&&(h.act.cast||h.act.bow)&&h.act.ch>0&&!h.act.done&&h.state!=='ko')base(h.x,h.y,()=>{const p=Math.min(1,h.act.t/(h.act.ch+.32));ctx.fillStyle='rgba(8,6,12,.88)';ctx.fillRect(-16,-66,32,6);ctx.fillStyle=CHCOL[h.cls];ctx.fillRect(-15,-65,30*p,4);ctx.strokeStyle='#000';ctx.lineWidth=1;ctx.strokeRect(-16.5,-66.5,33,7);},hel);
  if(G.scene==='town'&&!G.room&&!SAVE.entered&&ZONE.portal){const P=ZONE.portal,bob=Math.sin(G.t*5)*3;base(P.x,P.y,()=>{ctx.font='700 14px Rubik,sans-serif';ctx.textAlign='center';ctx.lineWidth=3;ctx.strokeStyle='#1a0a2a';ctx.strokeText('▼',0,-86+bob);ctx.fillStyle='#e6d2ff';ctx.fillText('▼',0,-86+bob);});}
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
