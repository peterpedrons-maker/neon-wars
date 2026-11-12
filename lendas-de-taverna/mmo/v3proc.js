/* Cenários por código (sem imagens): chão procedural (ruído) e props 3D (pinheiros, árvores, pedras, arbustos, gramas, flores).
   Para os mapas que já existem, a POSIÇÃO e o TIPO de cada prop vêm dos dados do mapa (assim colisão e jogabilidade não mudam);
   a aparência é toda gerada aqui. Um mapa novo só precisa de dados (props com tipo, máscaras de água/caminho) e um tema. */
(function(){
'use strict';
if(typeof THREE==='undefined'||!window.V3)return;
const T=THREE,U=1.3/46,CT=Math.cos(47*Math.PI/180);
const P=V3.proc={};
function hash(x,y,s){let h=(x*374761393+y*668265263+s*982451653)|0;h=Math.imul(h^(h>>>13),1274126177);return ((h^(h>>>16))>>>0)/4294967296;}
function vn(x,y,s){const xi=Math.floor(x),yi=Math.floor(y),xf=x-xi,yf=y-yi,u=xf*xf*(3-2*xf),v=yf*yf*(3-2*yf);
  return (hash(xi,yi,s)*(1-u)+hash(xi+1,yi,s)*u)*(1-v)+(hash(xi,yi+1,s)*(1-u)+hash(xi+1,yi+1,s)*u)*v;}
const fbm=(x,y,s)=>vn(x,y,s)*.5+vn(x*2,y*2,s+1)*.25+vn(x*4,y*4,s+2)*.125+vn(x*8,y*8,s+3)*.0625;
const lerp=(a,b,t)=>a+(b-a)*t,sst=(a,b,x)=>{const t=Math.max(0,Math.min(1,(x-a)/(b-a)));return t*t*(3-2*t);};
const mix=(c1,c2,t)=>[lerp(c1[0],c2[0],t),lerp(c1[1],c2[1],t),lerp(c1[2],c2[2],t)];
function cv(w,h){const c=document.createElement('canvas');c.width=w;c.height=h;return c;}
// ---- máscaras em grade de 4px (água do jogo; caminho/pedra lidos como dados do mapa original)
function blur(m,w,h,r){const o=new Float32Array(m.length);for(let y=0;y<h;y++)for(let x=0;x<w;x++){let s=0,n=0;for(let dy=-r;dy<=r;dy++)for(let dx=-r;dx<=r;dx++){const xx=x+dx,yy=y+dy;if(xx<0||yy<0||xx>=w||yy>=h)continue;s+=m[yy*w+xx];n++;}o[y*w+x]=s/n;}return o;}
function masks(env){
  const gw=Math.ceil(env.W/4),gh=Math.ceil(env.H/4),water=new Float32Array(gw*gh),dirt=new Float32Array(gw*gh),stone=new Float32Array(gw*gh);
  if(env.WATER&&env.WCW)for(let y=0;y<gh;y++)for(let x=0;x<gw;x++)if(env.WATER[y*env.WCW+x])water[y*gw+x]=1;
  if(env.GROUND){const c=cv(gw,gh),x=c.getContext('2d',{willReadFrequently:true});x.drawImage(env.GROUND,0,0,gw,gh);const d=x.getImageData(0,0,gw,gh).data;
    for(let i=0;i<gw*gh;i++){const r=d[i*4],g=d[i*4+1],b=d[i*4+2];if(water[i])continue;const mx=Math.max(r,g,b),mn=Math.min(r,g,b),sat=(mx-mn)/(mx||1);
      if(r>g+4&&r>b+18&&r>70)dirt[i]=1;else if(sat<.14&&mx>85)stone[i]=1;}}
  return {gw,gh,water:blur(blur(water,gw,gh,2),gw,gh,1),dirt:blur(dirt,gw,gh,1),stone:blur(stone,gw,gh,1)};
}
const samp=(m,gw,gh,gx,gy)=>{const x=Math.max(0,Math.min(gw-1.001,gx)),y=Math.max(0,Math.min(gh-1.001,gy)),xi=x|0,yi=y|0,xf=x-xi,yf=y-yi;
  return (m[yi*gw+xi]*(1-xf)+m[yi*gw+xi+1]*xf)*(1-yf)+(m[(yi+1)*gw+xi]*(1-xf)+m[(yi+1)*gw+xi+1]*xf)*yf;};
// ---- chão procedural
P.ground=function(env,pal,seed){
  const M=masks(env),S=.5,w=Math.round(env.W*S),h=Math.round(env.H*S),c=cv(w,h),x=c.getContext('2d'),im=x.createImageData(w,h),d=im.data,s0=seed||7;
  for(let py=0;py<h;py++)for(let px=0;px<w;px++){const gx=px/S,gy=py/S,mx=gx/4,my=gy/4;
    const n=fbm(gx/120,gy/120,s0),n2=fbm(gx/22,gy/22,s0+9),sp=hash(px,py,s0);
    let col=mix(mix(pal.g1,pal.g2,sst(.3,.7,n)),pal.g3,sst(.55,.8,n2)*.6);
    col=mix(col,pal.g2,(sp>.93?.35:0));
    const dv=samp(M.dirt,M.gw,M.gh,mx,my)+(n2-.5)*.5;
    if(dv>.35){const t=sst(.35,.55,dv),dc=mix(mix(pal.d1,pal.d2,n2),pal.d3,sp>.9?.5:0);col=mix(col,dc,t);}
    const sv=samp(M.stone,M.gw,M.gh,mx,my);
    if(sv>.5){const bx=Math.floor(gx/16),by=Math.floor(gy/9),off=(by&1)*8,jx=(gx+off)%16,jy=gy%9,mort=jx<1.2||jy<1.2,sh=.82+hash(Math.floor((gx+off)/16),by,s0)*.3;
      col=mix(col,mort?pal.sm:[pal.st[0]*sh,pal.st[1]*sh,pal.st[2]*sh],sst(.5,.6,sv));}
    const wv=samp(M.water,M.gw,M.gh,mx,my)+(n2-.5)*.12;
    if(wv>.22){if(wv<.42){col=mix(col,pal.shore,sst(.22,.32,wv));}
      if(wv>=.42){const dp=sst(.42,.85,wv),rip=Math.sin(gx*.09+gy*.05+n*9)*.5+.5;let wc=mix(pal.w1,pal.w2,dp);wc=mix(wc,[255,255,255],(rip>.93?.22:0)+(sp>.985?.35:0));col=mix(pal.shore,wc,sst(.42,.5,wv));}}
    const k=(py*w+px)*4;d[k]=col[0];d[k+1]=col[1];d[k+2]=col[2];d[k+3]=255;}
  x.putImageData(im,0,0);return c;
};
// ---- modelos 3D mesclados (um por tipo; instanciados)
function Mesh(){const pos=[],nor=[],col=[];
  return {add(geo,color,m){const g=geo.index?geo.toNonIndexed():geo.clone();g.applyMatrix4(m);g.computeVertexNormals();const p=g.attributes.position.array,n=g.attributes.normal.array,c=new T.Color(color).convertSRGBToLinear();
    for(let i=0;i<p.length;i+=3){pos.push(p[i],p[i+1],p[i+2]);nor.push(n[i],n[i+1],n[i+2]);const sh=.88+hash(Math.round(p[i]*50),Math.round(p[i+1]*50),3)*.24;col.push(c.r*sh,c.g*sh,c.b*sh);}},
    geo(){const g=new T.BufferGeometry();g.setAttribute('position',new T.Float32BufferAttribute(pos,3));g.setAttribute('normal',new T.Float32BufferAttribute(nor,3));g.setAttribute('color',new T.Float32BufferAttribute(col,3));return g;}};}
const M4=(x,y,z,sx,sy,sz,rx,rz)=>{const m=new T.Matrix4(),q=new T.Quaternion().setFromEuler(new T.Euler(rx||0,0,rz||0));return m.compose(new T.Vector3(x,y,z),q,new T.Vector3(sx,sy,sz));};
function jitter(geo,amt,seed){const p=geo.attributes.position;for(let i=0;i<p.count;i++){const x=p.getX(i),y=p.getY(i),z=p.getZ(i),k=hash(Math.round(x*100),Math.round(y*100)+Math.round(z*100),seed);p.setXYZ(i,x*(1+(k-.5)*amt),y*(1+(hash(i,seed,1)-.5)*amt),z*(1+(k-.5)*amt));}geo.computeVertexNormals();return geo;}
const MODELS={
  conifer(c){const m=Mesh(),tr=new T.Color(0x4a3220);m.add(new T.CylinderGeometry(.05,.08,.3,6),tr,M4(0,.15,0,1,1,1));
    const base=new T.Color(c).multiplyScalar(.8),top=new T.Color(c).multiplyScalar(1.25);
    [[.22,.5,.42],[.4,.42,.38],[.58,.34,.34],[.74,.26,.3],[.88,.17,.26]].forEach(([y,r,h],i)=>m.add(new T.ConeGeometry(r,h,7),base.clone().lerp(top,i/4),M4(0,y,0,1,1,1)));return m.geo();},
  broad(c){const m=Mesh();m.add(new T.CylinderGeometry(.07,.11,.5,6),0x4a3220,M4(0,.25,0,1,1,1));const cc=new T.Color(c);
    [[0,.72,0,.34],[-.2,.6,.05,.24],[.2,.62,-.05,.25],[.02,.9,.03,.22],[0,.55,.2,.2]].forEach(([x,y,z,r],i)=>m.add(jitter(new T.IcosahedronGeometry(r,0),.35,i+4),cc.clone().multiplyScalar(.85+i*.07),M4(x,y,z,1,.8,1)));return m.geo();},
  dead(c){const m=Mesh();m.add(new T.CylinderGeometry(.05,.11,.62,6),0x3a2a22,M4(0,.31,0,1,1,1));
    [[.16,.55,0,.5,-1.0],[-.18,.62,.02,.45,1.1],[.04,.76,-.12,.4,.3],[0,.8,.1,.35,-.4]].forEach(([x,y,z,l,rz])=>m.add(new T.CylinderGeometry(.015,.04,l,5),0x3a2a22,M4(x,y,z,1,1,1,0,rz)));
    const cc=new T.Color(0x23413f);[[.3,.8,0,.15],[-.3,.85,.05,.14],[.05,1.0,-.1,.14]].forEach(([x,y,z,r],i)=>m.add(jitter(new T.IcosahedronGeometry(r,0),.4,i+9),cc,M4(x,y,z,1,.7,1)));return m.geo();},
  rock(c){const m=Mesh();m.add(jitter(new T.DodecahedronGeometry(.5,0),.45,3),c,M4(0,.22,0,1,.62,.85));m.add(jitter(new T.DodecahedronGeometry(.3,0),.5,5),new T.Color(c).multiplyScalar(.85),M4(.42,.1,.1,1,.7,1));return m.geo();},
  bush(c){const m=Mesh(),cc=new T.Color(c);[[0,.2,0,.34],[.25,.15,.1,.22],[-.22,.14,-.05,.2]].forEach(([x,y,z,r],i)=>m.add(jitter(new T.IcosahedronGeometry(r,0),.35,i+2),cc.clone().multiplyScalar(.85+i*.1),M4(x,y,z,1,.75,1)));return m.geo();},
  post(c){const m=Mesh();m.add(new T.CylinderGeometry(.05,.07,1,6),0x4a3220,M4(0,.5,0,1,1,1));m.add(new T.CylinderGeometry(.1,.07,.12,6),0x2a2a2e,M4(0,1.02,0,1,1,1));return m.geo();},
  tuft(c){const m=Mesh(),cc=new T.Color(c);for(let i=0;i<5;i++){const a=i/5*6.283,r=.16;m.add(new T.ConeGeometry(.035,.45+(i%2)*.15,3),cc.clone().multiplyScalar(.8+i*.08),M4(Math.cos(a)*r*.5,.22,Math.sin(a)*r*.5,1,1,1,Math.sin(a)*.35,-Math.cos(a)*.35));}return m.geo();},
  flower(c){const m=Mesh();m.add(new T.CylinderGeometry(.012,.015,.3,4),0x3f6a2c,M4(0,.15,0,1,1,1));m.add(new T.IcosahedronGeometry(.07,0),c,M4(0,.32,0,1,.6,1));return m.geo();},
  pebble(c){const m=Mesh();m.add(jitter(new T.DodecahedronGeometry(.2,0),.4,1),c,M4(0,.06,0,1,.55,1));return m.geo();}
};
// ---- classificação a partir dos dados do mapa (tamanho + cor média do recorte do atlas)
const colCache={};
function avgCol(env,id){if(colCache[id])return colCache[id];const a=env.ATLAS_J[id],c=cv(8,8),x=c.getContext('2d',{willReadFrequently:true});x.drawImage(env.ATLAS,a[0],a[1],a[2],a[3],0,0,8,8);const d=x.getImageData(0,0,8,8).data;let r=0,g=0,b=0,w=0;
  for(let i=0;i<64;i++){const al=d[i*4+3];r+=d[i*4]*al;g+=d[i*4+1]*al;b+=d[i*4+2]*al;w+=al;}w=w||1;return colCache[id]=[r/w,g/w,b/w];}
function kindOf(a,rgb,flat){const [,,w,h]=a,[r,g,b]=rgb,mx=Math.max(r,g,b),mn=Math.min(r,g,b),sat=(mx-mn)/(mx||1),green=g>r+6&&g>=b-4,teal=b>r+6&&g>r;
  if(flat){if(w>=28||h>=28)return null;if(green)return 'tuft';if(sat<.18)return 'pebble';return 'flower';}
  if(h>=100)return (teal||green)?(b>=g-16?'conifer':'broad'):(r>g+6?'dead':'broad');
  if(w<=22&&h>=35)return 'post';
  if(h<=70&&w>=18)return (green&&sat>.18)?'bush':(sat<.3?'rock':null);
  return null;}
// ---- floresta: devolve o que sobrou (props sem modelo) para continuarem como sprites
P.forest=function(env,add,rnd,items){
  const mats={},buckets={},rest={stand:[],flats:[]};
  const take=(list,flat)=>{for(const it of list){const [id,x,y]=it,a=env.ATLAS_J[id];if(!a)continue;const rgb=avgCol(env,id),k=kindOf(a,rgb,flat);if(!k){(flat?rest.flats:rest.stand).push(it);continue;}(buckets[k]=buckets[k]||[]).push({x,y,a,rgb});}};
  take(items.stand,false);take(items.flats,true);
  const mat=new T.MeshStandardMaterial({vertexColors:true,flatShading:true,roughness:.92});
  for(const k in buckets){const L=buckets[k];if(!L.length)continue;
    const avg=L.reduce((s,q)=>[s[0]+q.rgb[0],s[1]+q.rgb[1],s[2]+q.rgb[2]],[0,0,0]).map(v=>v/L.length);
    const base=k==='conifer'?[28,66,62]:k==='broad'?[74,92,46]:k==='tuft'?[78,128,52]:k==='bush'?[58,104,46]:k==='rock'?[118,118,112]:avg;
    const col=new T.Color(`rgb(${base.map(Math.round).join(',')})`);
    const geo=MODELS[k](k==='flower'?0xffffff:col),im=new T.InstancedMesh(geo,mat,L.length),m4=new T.Matrix4(),q=new T.Quaternion(),e=new T.Euler();
    L.forEach((it,i)=>{const w=it.a[2],h=it.a[3],r=hash(Math.round(it.x),Math.round(it.y),11);let H,R;
      if(k==='conifer'||k==='broad'||k==='dead'){H=h*U/CT*.8;R=w*U*.5;}else if(k==='post'){H=h*U/CT*.85;R=1;}
      else if(k==='rock'||k==='bush'){H=Math.max(.5,h*U/CT*.9);R=Math.max(.6,w*U*.6);}else{H=Math.max(.35,h*U*2.2);R=Math.max(.5,w*U*2);}
      e.set(0,r*6.283,0);q.setFromEuler(e);const sc=.9+r*.25;m4.compose(new T.Vector3(it.x*U,0,it.y*U),q,k==='post'?new T.Vector3(1,H,1):new T.Vector3(R*2*sc,H*sc,R*2*sc));im.setMatrixAt(i,m4);
      const c0=new T.Color(k==='flower'?`hsl(${Math.round(hash(i,3,3)*360)},70%,62%)`:'#ffffff');if(k!=='flower')c0.multiplyScalar(.88+hash(i,5,5)*.22);else c0.convertSRGBToLinear();im.setColorAt(i,c0);});
    im.instanceMatrix.needsUpdate=true;if(im.instanceColor)im.instanceColor.needsUpdate=true;im.frustumCulled=false;add(im);}
  return rest;
};
P.palFloresta={g1:[40,86,34],g2:[56,106,42],g3:[30,68,30],d1:[116,86,54],d2:[132,100,62],d3:[96,70,44],st:[128,128,120],sm:[70,70,66],shore:[150,130,90],w1:[70,140,170],w2:[34,84,120]};
})();
