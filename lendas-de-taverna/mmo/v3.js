/* Visual 2.5D (opcional: ?v3=1). Só troca o DESENHO: a lógica do jogo (movimento, combate, colisão, missões, interface) continua a mesma.
   O mundo é 3D (three.js); personagens e inimigos continuam sendo os sprites do jogo, desenhados pelo próprio drawSprite() num canvas e colocados em pé no mundo.
   Cenas que ainda não têm versão 3D caem automaticamente no desenho 2D antigo. */
(function(){
'use strict';
if(!window.V3_REQ)return;
if(typeof THREE==='undefined'){window.V3_FAIL='three.js ausente';return;}
const T=THREE,U=1.3/46,TILT=47*Math.PI/180,CT=Math.cos(TILT);
const V3=window.V3={ready:false,err:''};
let R,S,cam,glc,stageEl,lbBox,scn=null,fxCv=null;
const $=id=>document.getElementById(id);
const rndSeed=s=>()=>{s=(s*16807)%2147483647;return (s-1)/2147483646;};
function cvs(w,h){const c=document.createElement('canvas');c.width=w;c.height=h;return c;}
function blobTex(a=.55){const c=cvs(64,64),x=c.getContext('2d'),g=x.createRadialGradient(32,32,2,32,32,30);g.addColorStop(0,`rgba(0,0,0,${a})`);g.addColorStop(1,'rgba(0,0,0,0)');x.fillStyle=g;x.fillRect(0,0,64,64);return new T.CanvasTexture(c);}
const BT=blobTex();
const flameTex=(()=>{const c=cvs(64,64),x=c.getContext('2d'),g=x.createRadialGradient(32,32,1,32,32,30);g.addColorStop(0,'rgba(255,240,170,1)');g.addColorStop(.3,'rgba(255,160,60,.8)');g.addColorStop(1,'rgba(255,90,10,0)');x.fillStyle=g;x.fillRect(0,0,64,64);return new T.CanvasTexture(c);})();
function init(){
  stageEl=$('stage');if(!stageEl)return;
  const st=document.createElement('style');st.textContent=`#gl3{position:absolute;inset:0;width:100%;height:100%;display:none}
  body.v3on #gl3{display:block}body.v3on canvas#cv{background:transparent;pointer-events:auto}
  #v3lb{position:absolute;inset:0;pointer-events:none;overflow:hidden;display:none}body.v3on #v3lb{display:block}
  .v3l{position:absolute;transform:translate(-50%,-100%);font:700 11px Rubik,Georgia,sans-serif;letter-spacing:.04em;color:#ffe69a;text-shadow:0 1px 0 #1a0a06,0 0 4px #000,0 0 8px #000;white-space:nowrap}
  .v3l.h{color:#bfe8ff}.v3l small{font-size:9px;opacity:.85;margin-left:3px;color:#d8d2c0}
  .v3ts{position:absolute;left:0;right:0;pointer-events:none;display:none;z-index:2}body.v3on .v3ts{display:block}
  .v3ts.t{top:0;height:15%;-webkit-backdrop-filter:blur(2.5px);backdrop-filter:blur(2.5px);-webkit-mask-image:linear-gradient(#000,transparent);mask-image:linear-gradient(#000,transparent)}
  .v3ts.b{bottom:0;height:18%;-webkit-backdrop-filter:blur(2.5px);backdrop-filter:blur(2.5px);-webkit-mask-image:linear-gradient(transparent,#000);mask-image:linear-gradient(transparent,#000)}
  #v3vg{position:absolute;inset:0;pointer-events:none;display:none;background:radial-gradient(ellipse at 50% 46%,transparent 56%,rgba(2,4,10,.5) 100%)}body.v3on #v3vg{display:block}`;
  document.head.appendChild(st);
  glc=document.createElement('canvas');glc.id='gl3';stageEl.insertBefore(glc,$('cv'));
  // o canvas 2D fica por cima (efeitos); camadas de acabamento ficam depois dele
  const mk=(c,cl)=>{const d=document.createElement('div');d.className=cl;stageEl.insertBefore(d,$('cv').nextSibling);return d;};
  lbBox=document.createElement('div');lbBox.id='v3lb';stageEl.insertBefore(lbBox,$('cv').nextSibling);
  mk(0,'v3ts t');mk(0,'v3ts b');const vg=document.createElement('div');vg.id='v3vg';stageEl.insertBefore(vg,$('cv').nextSibling);
  try{R=new T.WebGLRenderer({canvas:glc,antialias:true,powerPreference:'high-performance'});}catch(err){V3.err='este aparelho não liberou o WebGL';return;}
  R.outputEncoding=T.sRGBEncoding;R.toneMapping=T.ACESFilmicToneMapping;
  S=new T.Scene();cam=new T.PerspectiveCamera(32,1,.5,160);
  V3.ready=true;
}
function size(){const w=stageEl.clientWidth,h=stageEl.clientHeight,d=Math.min(devicePixelRatio||1,2);if(glc._w!==w+'x'+h){glc._w=w+'x'+h;R.setPixelRatio(d);R.setSize(w,h,false);cam.aspect=w/h;cam.updateProjectionMatrix();}}
V3.active=function(){
  if(!V3.ready||typeof G==='undefined'||!G.on||!G.hero)return false;
  const ok=G.scene==='town'&&!G.room&&G.map==='town'&&typeof ZONE!=='undefined'&&ZONE&&ATLAS&&GROUND;
  document.body.classList.toggle('v3on',!!ok);return !!ok;};
// ------------------------------------------------------------------ cenário da cidade
function texOf(img,px){const t=new T.Texture(img);t.encoding=T.sRGBEncoding;if(px){t.magFilter=T.NearestFilter;t.minFilter=T.LinearMipmapLinearFilter;}t.needsUpdate=true;return t;}
function buildTown(){
  const rnd=rndSeed(11);
  const sc={key:'town',grp:new T.Group(),solids:[],houses:[],winMats:[],sources:[],pool:[],glows:[],smoke:[],chimneys:[],ents:new Map(),labels:new Map()};
  const g=sc.grp,add=o=>{g.add(o);return o;};
  S.add(g);
  const aTex=texOf(ATLAS,1),gTex=texOf(GROUND,1),AW=ATLAS.width,AH=ATLAS.height,GWu=ZONE.w*U,GHu=ZONE.h*U;
  sc.hemi=new T.HemisphereLight(0xcfe3ff,0x4a5a3a,.8);sc.sun=new T.DirectionalLight(0xfff0d0,1.0);sc.sun.position.set(-8,14,10);add(sc.hemi);add(sc.sun);
  const ground=new T.Mesh(new T.PlaneGeometry(GWu,GHu),new T.MeshStandardMaterial({map:gTex,bumpMap:gTex,bumpScale:1.2,roughness:.95}));ground.rotation.x=-Math.PI/2;ground.position.set(GWu/2,0,GHu/2);add(ground);
  const far=new T.Mesh(new T.PlaneGeometry(300,300),new T.MeshStandardMaterial({color:0x2c5a22,roughness:1}));far.rotation.x=-Math.PI/2;far.position.set(GWu/2,-.02,GHu/2);add(far);
  // props do atlas
  function quads(items,flat){const pos=[],uv=[],idx=[];let n=0;
    for(const [id,px,py] of items){const a=ATLAS_J[id];if(!a)continue;const [sx,sy,sw,sh,ax,ay]=a,X=px*U,Z=py*U;
      [[-ax,ay],[sw-ax,ay],[sw-ax,ay-sh],[-ax,ay-sh]].forEach(([cx,cy],i)=>{
        if(flat)pos.push(X+cx*U,.02,Z-cy*U);else pos.push(X+cx*U,Math.max(0,cy*U/CT),Z);
        uv.push((sx+[0,1,1,0][i]*sw)/AW,1-(sy+[0,0,1,1][i]*sh)/AH);});
      idx.push(n,n+1,n+2,n,n+2,n+3);n+=4;}
    const geo=new T.BufferGeometry();geo.setAttribute('position',new T.Float32BufferAttribute(pos,3));geo.setAttribute('uv',new T.Float32BufferAttribute(uv,2));geo.setIndex(idx);geo.computeVertexNormals();
    const m=new T.MeshLambertMaterial({map:aTex,alphaTest:.4,side:T.DoubleSide,emissive:0xffffff,emissiveMap:aTex,emissiveIntensity:.0});
    const me=new T.Mesh(geo,m);return add(me);}
  const stand=[],flats=[],lampsP=[];
  for(const p of ZONE.props){if(!p.id||p.t==='portal'||p.t==='fire')continue;const a=ATLAS_J[p.id];if(!a)continue;
    if(p.t==='flat'){flats.push([p.id,p.x,p.y]);continue;}
    if(p.id.startsWith('b_'))continue;stand.push([p.id,p.x,p.y]);
    if(a[2]<=24&&a[3]>=80)lampsP.push([p.x*U,2.3,p.y*U]);}
  const mf=quads(flats,true);mf.material.polygonOffset=true;mf.material.polygonOffsetFactor=-2;quads(stand,false);
  {const pos=[],uv=[],idx=[];let n=0;for(const [id,px,py] of stand){const a=ATLAS_J[id];if(!a||a[3]<60)continue;const X=px*U,Z=py*U,rw=Math.min(a[2],100)*U*.55,rd=rw*.5;
    [[-rw,-rd],[rw,-rd],[rw,rd],[-rw,rd]].forEach(([cx,cz],i)=>{pos.push(X+cx,.03,Z+cz+rd*.6);uv.push([0,1,1,0][i],[0,0,1,1][i]);});idx.push(n,n+1,n+2,n,n+2,n+3);n+=4;}
    const geo=new T.BufferGeometry();geo.setAttribute('position',new T.Float32BufferAttribute(pos,3));geo.setAttribute('uv',new T.Float32BufferAttribute(uv,2));geo.setIndex(idx);
    add(new T.Mesh(geo,new T.MeshBasicMaterial({map:BT,transparent:true,depthWrite:false,polygonOffset:true,polygonOffsetFactor:-3})));}
  // casas 3D
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
  // luzes
  for(const [x,y,z] of lampsP)sc.sources.push({p:new T.Vector3(x,y,z),c:0xffc878,k:1.5,night:1});
  for(const f of ZONE.fx||[])if(f.k==='fire'||f.k==='torch'||(f.k==='glow'&&f.col))sc.sources.push({p:new T.Vector3(f.x*U,1.3,f.y*U+.5),c:f.k==='glow'?parseInt((f.col||'#ff9a3a').slice(1),16):0xffa040,k:1.6,night:.3,fl:1});
  for(let i=0;i<7;i++){const L=new T.PointLight(0xffc878,0,11,2);add(L);sc.pool.push(L);}
  sc.glows=sc.sources.map(s=>{const sp=new T.Sprite(new T.SpriteMaterial({map:flameTex,blending:T.AdditiveBlending,depthWrite:false,transparent:true,color:s.c}));sp.position.copy(s.p);sp.scale.set(1.3,1.3,1);add(sp);return sp;});
  for(const ch of sc.chimneys)for(let i=0;i<6;i++){const sp=new T.Sprite(new T.SpriteMaterial({map:blobTex(.5),transparent:true,depthWrite:false,color:0xcfcfd4,opacity:0}));add(sp);sc.smoke.push({sp,x:ch.x,y:ch.y,z:ch.z,t:i/6*4});}
  return sc;
}
// ------------------------------------------------------------------ entidades (sprites do jogo)
const quadGeo={};
function geoFor(S0){return quadGeo[S0]||(quadGeo[S0]=(()=>{const g=new T.PlaneGeometry(S0*U,S0*U);g.translate(0,(S0/2-12)*U,0);return g;})());}
function entRec(sc,e,S0){let r=sc.ents.get(e);if(r&&r.S0===S0)return r;
  if(r){sc.grp.remove(r.root);r.tex.dispose();}
  const c=cvs(S0,S0),tex=new T.CanvasTexture(c);tex.encoding=T.sRGBEncoding;tex.magFilter=T.NearestFilter;tex.minFilter=T.NearestFilter;tex.generateMipmaps=false;
  const mat=new T.MeshLambertMaterial({map:tex,transparent:true,alphaTest:.3,emissive:0xffffff,emissiveMap:tex,emissiveIntensity:.3,side:T.DoubleSide});
  const me=new T.Mesh(geoFor(S0),mat);me.scale.y=1/CT;
  const root=new T.Group();root.add(me);const bl=new T.Mesh(new T.PlaneGeometry(1.3,.8),new T.MeshBasicMaterial({map:BT,transparent:true,depthWrite:false,polygonOffset:true,polygonOffsetFactor:-4}));bl.rotation.x=-Math.PI/2;bl.position.y=.03;root.add(bl);
  sc.grp.add(root);r={S0,c,cx:c.getContext('2d'),tex,me,root,bl,seen:0};sc.ents.set(e,r);return r;}
function drawEnt(sc,e,frame){
  const fr=entFrame(e);if(!fr)return;const scale=e.kind==='boss'?e.T.scale:(e.sc||1);
  const S0=Math.max(128,Math.ceil(Math.max(fr[3],fr[4])*scale*1.5/64)*64);const r=entRec(sc,e,S0);r.seen=frame;
  const oc=ctx,ox=G.cam.x,oy=G.cam.y,ow=G.LW,oh=G.LH;
  ctx=r.cx;ctx.setTransform(1,0,0,1,0,0);ctx.clearRect(0,0,S0,S0);ctx.imageSmoothingEnabled=false;
  G.cam.x=e.x-S0/2;G.cam.y=e.y-(S0-12);G.LW=S0;G.LH=S0;
  try{const al=e.dead?Math.max(0,1-Math.max(0,e.deadT-.5)/.6):1;drawSprite(e,fr,scale,e.flash>0,al);}catch(err){}
  ctx=oc;G.cam.x=ox;G.cam.y=oy;G.LW=ow;G.LH=oh;
  r.tex.needsUpdate=true;r.root.position.set(e.x*U,0,e.y*U);r.me.position.y=(e.zoff||0)*U/CT;
}
// ------------------------------------------------------------------ projeção e entrada
const tmp=new T.Vector3();
function toScreen(x,y,hpx){tmp.set(x*U,(hpx||0)*U/CT,y*U).project(cam);return [(tmp.x+1)/2*stageEl.clientWidth,(1-tmp.y)/2*stageEl.clientHeight,tmp.z];}
V3.pick=function(cx,cy){const r=stageEl.getBoundingClientRect(),nx=(cx-r.left)/r.width*2-1,ny=-((cy-r.top)/r.height)*2+1;
  const ray=new T.Raycaster();ray.setFromCamera({x:nx,y:ny},cam);const o=ray.ray.origin,d=ray.ray.direction;if(Math.abs(d.y)<1e-5)return [G.hero.x,G.hero.y];const t=-o.y/d.y;return [(o.x+d.x*t)/U,(o.z+d.z*t)/U];};
V3.hitNpc=function(cx,cy){if(!scn)return null;const r=stageEl.getBoundingClientRect(),x=cx-r.left,y=cy-r.top;let best=null,bd=1e9;
  for(const n of (G.npcs||[])){const f=toScreen(n.x,n.y,0),t=toScreen(n.x,n.y,50),w=Math.abs(t[1]-f[1])*.45+8;if(x>f[0]-w&&x<f[0]+w&&y>t[1]-6&&y<f[1]+10){const d=Math.abs(x-f[0]);if(d<bd){bd=d;best=n;}}}return best;};
V3.hitDoor=function(cx,cy){if(!scn)return null;const r=stageEl.getBoundingClientRect(),x=cx-r.left,y=cy-r.top;
  for(const g of scn.houses){const u=g.userData,b=u.box,pts=[[b.min.x,0,b.max.z],[b.max.x,0,b.max.z],[b.min.x,u.h+1.5,b.min.z+.5],[b.max.x,u.h+1.5,b.min.z+.5]].map(p=>{tmp.set(p[0],p[1],p[2]).project(cam);return [(tmp.x+1)/2*stageEl.clientWidth,(1-tmp.y)/2*stageEl.clientHeight];});
    const xs=pts.map(p=>p[0]),ys=pts.map(p=>p[1]);if(x>Math.min(...xs)&&x<Math.max(...xs)&&y>Math.min(...ys)&&y<Math.max(...ys)){const id=u.id.slice(2);const d=(ZONE.doors||[]).find(q=>q.id===id);if(d)return d;}}return null;};
// ------------------------------------------------------------------ laço de desenho
let frameNo=0,camT=null;
let shown=false,bad=0;
V3.render=function(){
  try{render3();if(!shown){shown=true;if(typeof toast==='function')toast('Visual 2.5D ligado',1800);}}catch(err){bad++;V3.err=String(err&&err.message||err);console.error('[v3]',err);if(bad>=3){V3.ready=false;document.body.classList.remove('v3on');if(typeof toast==='function')toast('Visual 2.5D desligado: '+V3.err,5000);}}
};
function render3(){
  if(!scn||scn.key!=='town'){if(scn){S.remove(scn.grp);}scn=buildTown();}
  size();frameNo++;const dt=1/60,t=G.t;
  // luz do dia (usa o relógio do jogo)
  const n=TOD.n||0,L=Math.max(0,TOD.L||1);
  scn.hemi.intensity=.88-.62*n;scn.hemi.color.setHex(n>.5?0x6a82c8:0xcfe3ff);scn.sun.intensity=1.15-.97*n+(TOD.warm||0)*.2;scn.sun.color.setHex(n>.5?0x8aa0ff:(TOD.warm>.4?0xffc890:0xfff0d0));
  const bg=new T.Color(0xa9c9e6).lerp(new T.Color(0x070b1a),Math.min(1,n*1.1));if((TOD.warm||0)>.3)bg.lerp(new T.Color(0xe6a468),(TOD.warm-.3)*.8*(1-n));S.background=bg;S.fog=S.fog||new T.FogExp2(0x9fc4e6,.012);S.fog.color.copy(bg);S.fog.density=.012+.008*n;R.toneMappingExposure=1.0+.15*n;
  // câmera
  const asp=cam.aspect,dist=18*(asp<1?1+(1-asp)*1.2:1);const tx=(G.cam.x+G.LW/2)*U,tz=(G.cam.y+G.LH/2)*U;
  if(!camT)camT=new T.Vector3(tx,0,tz);camT.x+=(tx-camT.x)*.5;camT.z+=(tz-camT.z)*.5;
  const sh=G.shake>0?G.shake:0;cam.position.set(camT.x+(Math.random()-.5)*sh*.3,.9+Math.sin(TILT)*dist,camT.z-1+Math.cos(TILT)*dist);cam.lookAt(camT.x,.9,camT.z-1);
  G.cam.rx=Math.round(G.cam.x);G.cam.ry=Math.round(G.cam.y);
  // entidades
  const ents=[G.hero,...(G.npcs||[]),...(G.vill||[])];for(const e of ents)if(e&&!e.hide)drawEnt(scn,e,frameNo);
  for(const [e,r] of scn.ents)if(r.seen!==frameNo){scn.grp.remove(r.root);r.tex.dispose();scn.ents.delete(e);}
  // casas na frente do herói ficam transparentes
  {const hd=new T.Vector3(G.hero.x*U,1,G.hero.y*U),dir=hd.clone().sub(cam.position),Ld=dir.length();dir.normalize();const ray=new T.Ray(cam.position,dir),hit=new T.Vector3();
   for(const g of scn.houses){const u=g.userData,p=ray.intersectBox(u.box,hit),blk=p&&cam.position.distanceTo(hit)<Ld-.3,tg=blk?.14:1;u.o+=(tg-u.o)*.3;for(const m of u.mats){m.transparent=u.o<.995;m.opacity=u.o;m.depthWrite=u.o>.6;}}}
  // luzes dinâmicas (as 7 mais próximas do herói)
  const hp=new T.Vector3(G.hero.x*U,0,G.hero.y*U),act=scn.sources.map((s,i)=>({s,i,d:s.p.distanceToSquared(hp)})).sort((a,b)=>a.d-b.d);
  scn.pool.forEach((Lt,i)=>{const a=act[i];if(!a){Lt.intensity=0;return;}const f=1+(a.s.fl?.18*Math.sin(t*11+a.i)+.1*Math.sin(t*23+a.i*2):.04*Math.sin(t*3+a.i));Lt.position.copy(a.s.p);Lt.color.setHex(a.s.c);Lt.intensity=a.s.k*(.15+Math.max(n,a.s.night*.6*Math.min(1,n*2.5)))*f*(n>.05||a.s.night?1:.25);Lt.distance=11;});
  scn.sources.forEach((s,i)=>{const gl=scn.glows[i],f=1+(s.fl?.2*Math.sin(t*11+i):.05*Math.sin(t*3+i));gl.material.opacity=Math.min(1,.12+Math.max(n,s.night*.5*Math.min(1,n*2.5))*.9);gl.scale.set(1.4*f,1.4*f,1);});
  scn.winMats.forEach(m=>m.emissiveIntensity=.2+n*1.4);scn.vm.uniforms.t.value=t;scn.pl.intensity=1.4+.4*Math.sin(t*2);
  for(const s of scn.smoke){s.t+=dt;const u=(s.t%4)/4;s.sp.position.set(s.x+u*.9,s.y+u*2.6,s.z+Math.sin(u*5+s.t)*.1);const q=.5+u*1.8;s.sp.scale.set(q,q,1);s.sp.material.opacity=Math.sin(u*Math.PI)*.35*(1-n*.4);}
  R.render(S,cam);
  // ---- camada 2D por cima: efeitos do jogo (partículas, projéteis) com a projeção aproximada, números e nomes
  const cvEl=$('cv'),k=cvEl.width/stageEl.clientWidth;ctx.setTransform(1,0,0,1,0,0);ctx.clearRect(0,0,cvEl.width,cvEl.height);
  {const h=G.hero,s0=toScreen(h.x,h.y,0),s1=toScreen(h.x+100,h.y,0),s2=toScreen(h.x,h.y+100,0),a=(s1[0]-s0[0])/100,b=(s1[1]-s0[1])/100,c=(s2[0]-s0[0])/100,d=(s2[1]-s0[1])/100,cx=G.cam.rx,cy=G.cam.ry;
   ctx.setTransform(k*a,k*b,k*c,k*d,k*(s0[0]+a*(cx-h.x)+c*(cy-h.y)),k*(s0[1]+b*(cx-h.x)+d*(cy-h.y)));ctx.imageSmoothingEnabled=false;
   try{drawProjs(ctx,cx,cy);drawMProjs(ctx,cx,cy);drawFx(ctx,cx,cy);GX.draw(ctx,cx,cy);AMB.draw(ctx,cx,cy);}catch(err){}}
  ctx.setTransform(1,0,0,1,0,0);
  for(const f of G.floats){const sp=toScreen(f.x,f.y,0),a=Math.min(1,f.life/(f.max*.35)),age=f.max-f.life,q=f.pop&&age<.16?1+(1-age/.16)*.6:1,fs=f.size*q*G.K*.8;
    ctx.globalAlpha=a;ctx.font=(f.bold?'800 ':'700 ')+fs+'px Rubik,sans-serif';ctx.textAlign='center';ctx.lineJoin='round';ctx.lineWidth=f.bold?4:3;ctx.strokeStyle='rgba(20,6,4,.96)';ctx.strokeText(f.t,sp[0]*k,sp[1]*k);
    if(f.glow){ctx.shadowColor=f.col;ctx.shadowBlur=9;}ctx.fillStyle=f.col;ctx.fillText(f.t,sp[0]*k,sp[1]*k);ctx.shadowBlur=0;ctx.globalAlpha=1;}
  try{mmDraw();}catch(err){}
  // nomes (HTML por cima)
  const seen=new Set();
  const lab=(e,txt,sub,cl)=>{let el=scn.labels.get(e);if(!el){el=document.createElement('div');lbBox.appendChild(el);scn.labels.set(e,el);}el.className='v3l '+cl;if(el._t!==txt+sub){el._t=txt+sub;el.innerHTML=txt+(sub?'<small>'+sub+'</small>':'');}
    const p=toScreen(e.x,e.y,e.kind==='hero'?62:60);el.style.left=p[0]+'px';el.style.top=p[1]+'px';el.style.display=p[2]<1?'block':'none';seen.add(e);};
  lab(G.hero,SAVE.name||'Herói','Nv.'+SAVE.lv,'h');for(const nn of (G.npcs||[]))lab(nn,nn.nm,'','');
  for(const [e,el] of scn.labels)if(!seen.has(e)){el.remove();scn.labels.delete(e);}
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})();
