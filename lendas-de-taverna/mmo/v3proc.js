/* Cenários por código (sem imagens): chão procedural (ruído) e props 3D (pinheiros, árvores, pedras, arbustos, gramas, flores).
   Para os mapas que já existem, a POSIÇÃO e o TIPO de cada prop vêm dos dados do mapa (assim colisão e jogabilidade não mudam);
   a aparência é toda gerada aqui. Um mapa novo só precisa de dados (props com tipo, máscaras de água/caminho) e um tema. */
(function(){
'use strict';
if(typeof THREE==='undefined'||!window.V3)return;
const T=THREE,U=1.3/46,CT=Math.cos(47*Math.PI/180);
const P=V3.proc={time:{value:0}};
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
      if(env.stoneNonGreen){if(!(g>r+25&&g>b+25))stone[i]=1;}else if(r>g+4&&r>b+18&&r>70)dirt[i]=1;else if(sat<.14&&mx>85)stone[i]=1;}}
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
  x.putImageData(im,0,0);return {canvas:c,M};
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

  puddle(c){const m=Mesh();m.add(jitter(new T.CircleGeometry(.5,12),.3,6),c,M4(0,.03,0,1,1,1,-Math.PI/2));return m.geo();},
  bones(c){const m=Mesh(),cc=new T.Color(c);[[0,0,0,.9,.4],[.05,.04,.1,.8,-.5],[-.1,.03,-.1,.7,1.3]].forEach(([x,y,z,l,rz])=>{m.add(new T.CylinderGeometry(.035,.035,l,5),cc,M4(x,.05+y,z,1,1,1,0,1.5+rz*.3));m.add(new T.IcosahedronGeometry(.07,0),cc,M4(x-l/2*Math.cos(rz*.3),.06+y,z,1,1,1));m.add(new T.IcosahedronGeometry(.07,0),cc,M4(x+l/2*Math.cos(rz*.3),.06+y,z,1,1,1));});m.add(jitter(new T.IcosahedronGeometry(.13,0),.2,3),cc,M4(.2,.1,.15,1,.9,1));return m.geo();},
  twig(c){const m=Mesh();[[0,.5,.9],[.1,-.6,.7],[-.1,1.2,.6]].forEach(([x,rz,l],i)=>m.add(new T.CylinderGeometry(.018,.026,l,4),c,M4(x,.03+i*.015,i*.08,1,1,1,0,1.45+rz*.2)));return m.geo();},
  thorn(c){const m=Mesh(),cc=new T.Color(c);m.add(jitter(new T.IcosahedronGeometry(.42,1),.35,8),cc,M4(0,.3,0,1,.8,1));for(let i=0;i<9;i++){const a=i*2.4,r=.3+hash(i,1,1)*.15;m.add(new T.ConeGeometry(.04,.3,4),cc.clone().multiplyScalar(1.3),M4(Math.cos(a)*r,.3+Math.sin(i*1.7)*.15,Math.sin(a)*r,1,1,1,Math.sin(a)*1.1,-Math.cos(a)*1.1));}return m.geo();},
  tent(c){const m=Mesh(),cc=new T.Color(c);m.add(new T.ConeGeometry(.62,.9,4),cc,M4(0,.45,0,1,1,.9,0,0).multiply(new T.Matrix4().makeRotationY(Math.PI/4)));m.add(new T.PlaneGeometry(.34,.45),0x1a110c,M4(0,.22,.42,1,1,1));
    [[-.3,0.95],[.3,.95]].forEach(([x,y])=>m.add(new T.CylinderGeometry(.02,.02,.5,4),0x3a2616,M4(x*.3,y,0,1,1,1,0,x*3)));m.add(new T.CylinderGeometry(.02,.02,.9,4),0x3a2616,M4(0,.98,0,1,1,1,0,1.57));return m.geo();},
  totem(c){const m=Mesh();m.add(new T.CylinderGeometry(.04,.055,1,6),0x4a3220,M4(0,.5,0,1,1,1));m.add(jitter(new T.IcosahedronGeometry(.12,0),.15,2),0xd8cdb0,M4(0,.9,0,1,1.15,.95));
    m.add(new T.ConeGeometry(.05,.4,4),0x22302c,M4(-.16,.88,0,1,1,1,0,.9));m.add(new T.ConeGeometry(.05,.4,4),0x22302c,M4(.16,.88,0,1,1,1,0,-.9));m.add(new T.ConeGeometry(.04,.3,4),0x22302c,M4(0,1.08,0,1,1,1));
    for(let i=0;i<4;i++)m.add(new T.CylinderGeometry(.015,.015,.14,4),0xd8cdb0,M4(.05*Math.sin(i*2),.35+i*.1,.05*Math.cos(i*2),1,1,1,0,1.2));return m.geo();},
  drums(c){const m=Mesh();m.add(new T.BoxGeometry(1,.1,.5),0x5a3a20,M4(0,.3,0,1,1,1));[[-.4,-.2],[.4,-.2],[-.4,.2],[.4,.2]].forEach(([x,z])=>m.add(new T.CylinderGeometry(.03,.04,.3,4),0x4a2e18,M4(x,.15,z,1,1,1)));
    [-.25,.25].forEach(x=>{m.add(new T.CylinderGeometry(.2,.17,.36,10),0x8a5a30,M4(x,.54,0,1,1,1));m.add(new T.CylinderGeometry(.205,.205,.03,10),0xd9b98a,M4(x,.73,0,1,1,1));m.add(new T.CylinderGeometry(.19,.19,.04,10),0x3a2616,M4(x,.5,0,1,1,1));});return m.geo();},
  mush(c){const m=Mesh(),cc=new T.Color(c);[[0,0,.5,.22],[.28,.1,.32,.15],[-.25,-.05,.26,.13]].forEach(([x,z,h,r])=>{m.add(new T.CylinderGeometry(r*.3,r*.4,h,6),0xe8dcb8,M4(x,h/2,z,1,1,1));m.add(new T.SphereGeometry(r,8,5,0,6.283,0,1.6),cc,M4(x,h,z,1,.8,1));});return m.geo();},

  pillar(c){const m=Mesh(),cc=new T.Color(c);m.add(new T.BoxGeometry(.8,.1,.8),cc.clone().multiplyScalar(.8),M4(0,.05,0,1,1,1));m.add(new T.CylinderGeometry(.3,.34,.78,8),cc,M4(0,.5,0,1,1,1));m.add(new T.BoxGeometry(.82,.12,.82),cc.clone().multiplyScalar(1.1),M4(0,.94,0,1,1,1));m.add(new T.BoxGeometry(.4,.04,.4),cc.clone().multiplyScalar(.6),M4(0,.5,.3,1,1,1));return m.geo();},
  banner(c){const m=Mesh(),cc=new T.Color(c);m.add(new T.CylinderGeometry(.03,.03,1,5),0x4a3220,M4(0,.96,0,1,1,1,0,1.5708));m.add(new T.BoxGeometry(.86,.84,.04),cc,M4(0,.5,0,1,1,1));m.add(new T.ConeGeometry(.43,.3,3),cc,M4(0,.0,0,1,1,.1,0,Math.PI));m.add(new T.BoxGeometry(.3,.3,.045),new T.Color(c).multiplyScalar(1.6),M4(0,.55,0,1,1,1));return m.geo();},
  barrel(c){const m=Mesh();m.add(new T.CylinderGeometry(.42,.36,1,10),c,M4(0,.5,0,1,1,1));[.25,.75].forEach(y=>m.add(new T.CylinderGeometry(.435,.435,.06,10),0x2a2a2e,M4(0,y,0,1,1,1)));return m.geo();},
  crate(c){const m=Mesh(),cc=new T.Color(c);m.add(new T.BoxGeometry(.9,.9,.9),cc,M4(0,.45,0,1,1,1));[[-.43,-.43],[.43,-.43],[-.43,.43],[.43,.43]].forEach(([x,z])=>m.add(new T.BoxGeometry(.1,.94,.1),cc.clone().multiplyScalar(.6),M4(x,.47,z,1,1,1)));m.add(new T.BoxGeometry(.92,.08,.1),cc.clone().multiplyScalar(.65),M4(0,.5,.45,1,1,1));return m.geo();},
  chest(c){const m=Mesh(),cc=new T.Color(c);m.add(new T.BoxGeometry(.95,.5,.6),cc,M4(0,.25,0,1,1,1));m.add(new T.CylinderGeometry(.3,.3,.95,8,1,false,0,Math.PI),cc.clone().multiplyScalar(1.15),M4(0,.5,0,1,1,1,0,1.5708).multiply(new T.Matrix4().makeRotationX(Math.PI/2)));m.add(new T.BoxGeometry(1,.1,.12),0xd9a84a,M4(0,.4,.3,1,1,1));m.add(new T.BoxGeometry(.12,.2,.05),0xd9a84a,M4(0,.45,.31,1,1,1));return m.geo();},
  coffin(c){const m=Mesh();m.add(new T.CylinderGeometry(.3,.22,1,6),c,M4(0,.5,0,1,1,.5));m.add(new T.BoxGeometry(.05,.5,.02),0xb59a60,M4(0,.6,.14,1,1,1));return m.geo();},
  tomb(c){const m=Mesh(),cc=new T.Color(c);m.add(new T.BoxGeometry(.95,.5,.55),cc.clone().multiplyScalar(.9),M4(0,.25,0,1,1,1));m.add(new T.BoxGeometry(1,.14,.62),cc.clone().multiplyScalar(1.1),M4(0,.57,0,1,1,1));m.add(new T.IcosahedronGeometry(.1,0),0xd8cdb0,M4(0,.7,0,1,1.1,1));return m.geo();},
  tombstone(c){const m=Mesh();m.add(new T.BoxGeometry(.7,.6,.2),c,M4(0,.3,0,1,1,1));m.add(new T.CylinderGeometry(.35,.35,.2,8,1,false,0,Math.PI),c,M4(0,.6,0,1,1,1,Math.PI/2,0));m.add(new T.BoxGeometry(.9,.1,.5),new T.Color(c).multiplyScalar(.7),M4(0,.05,0,1,1,1));return m.geo();},
  urn(c){const m=Mesh();m.add(new T.SphereGeometry(.4,8,6),c,M4(0,.4,0,1,1.05,1));m.add(new T.CylinderGeometry(.2,.3,.25,8),c,M4(0,.88,0,1,1,1));return m.geo();},
  block(c){const m=Mesh(),cc=new T.Color(c);m.add(jitter(new T.BoxGeometry(.9,.8,.9),.12,4),cc,M4(0,.4,0,1,1,1));m.add(new T.BoxGeometry(.96,.1,.96),cc.clone().multiplyScalar(1.15),M4(0,.82,0,1,1,1));return m.geo();},
  column(c){const m=Mesh(),cc=new T.Color(c);m.add(new T.CylinderGeometry(.3,.36,1,7),cc,M4(0,.5,0,1,1,1));m.add(new T.BoxGeometry(.8,.08,.8),cc.clone().multiplyScalar(1.1),M4(0,.96,0,1,1,1));return m.geo();},
  rune(c){const m=Mesh();m.add(new T.RingGeometry(.43,.5,40),c,M4(0,.045,0,1,1,1,-Math.PI/2));m.add(new T.RingGeometry(.28,.31,32),c,M4(0,.046,0,1,1,1,-Math.PI/2));for(let i=0;i<5;i++){const a=i*1.2566,b=((i+2)%5)*1.2566;const x1=Math.cos(a)*.36,z1=Math.sin(a)*.36,x2=Math.cos(b)*.36,z2=Math.sin(b)*.36;const l=Math.hypot(x2-x1,z2-z1),ang=Math.atan2(z2-z1,x2-x1);m.add(new T.PlaneGeometry(l,.03),c,M4((x1+x2)/2,.047,(z1+z2)/2,1,1,1,-Math.PI/2).multiply(new T.Matrix4().makeRotationZ(-ang)));}return m.geo();},

  lamp(c){const m=Mesh();m.add(new T.CylinderGeometry(.04,.06,1,6),0x2a2a30,M4(0,.5,0,1,1,1));m.add(new T.BoxGeometry(.3,.4,.3),0x2a2a30,M4(0,1.0,0,1,1,1));m.add(new T.BoxGeometry(.22,.3,.22),0xffe2a0,M4(0,1.0,0,1,1,1));m.add(new T.ConeGeometry(.24,.18,4),0x2a2a30,M4(0,1.28,0,1,1,1).multiply(new T.Matrix4().makeRotationY(Math.PI/4)));return m.geo();},
  bench(c){const m=Mesh(),cc=new T.Color(c);m.add(new T.BoxGeometry(1,.1,.45),cc,M4(0,.45,0,1,1,1));m.add(new T.BoxGeometry(1,.4,.06),cc.clone().multiplyScalar(.85),M4(0,.75,-.2,1,1,1));[-.42,.42].forEach(x=>m.add(new T.BoxGeometry(.07,.45,.4),0x2a2a30,M4(x,.22,0,1,1,1)));return m.geo();},
  planter(c){const m=Mesh();m.add(new T.BoxGeometry(1,.5,.6),0x6a4a2a,M4(0,.25,0,1,1,1));m.add(new T.BoxGeometry(.94,.1,.54),0x3a2a1a,M4(0,.52,0,1,1,1));for(let i=0;i<6;i++){m.add(new T.IcosahedronGeometry(.09,0),new T.Color().setHSL(hash(i,1,1),.7,.6),M4(-.38+i*.15,.62+hash(i,2,2)*.1,(hash(i,3,3)-.5)*.3,1,1,1));}return m.geo();},

  cabinet(c){const m=Mesh(),cc=new T.Color(c);m.add(new T.BoxGeometry(1,.94,1),cc,M4(0,.47,0,1,1,1));m.add(new T.BoxGeometry(1.04,.06,1.06),cc.clone().multiplyScalar(1.25),M4(0,.97,0,1,1,1));[.3,.6].forEach(y=>m.add(new T.BoxGeometry(.92,.03,.04),cc.clone().multiplyScalar(.5),M4(0,y,.5,1,1,1)));m.add(new T.BoxGeometry(.04,.8,.04),cc.clone().multiplyScalar(.5),M4(0,.45,.5,1,1,1));return m.geo();},
  potshelf(c){const m=Mesh(),cc=new T.Color(c);m.add(new T.BoxGeometry(1,.94,1),cc,M4(0,.47,0,1,1,1));m.add(new T.BoxGeometry(1.04,.07,1.06),cc.clone().multiplyScalar(1.3),M4(0,.97,0,1,1,1));
    [.34,.68].forEach((y,j)=>{m.add(new T.BoxGeometry(.94,.04,.3),0x3a2616,M4(0,y,.5,1,1,1));for(let i=0;i<6;i++)m.add(new T.CylinderGeometry(.05,.06,.14,6),new T.Color().setHSL(hash(i,j,4),.65,.5),M4(-.38+i*.15,y+.09,.5,1,1,1));});return m.geo();},
  longcounter(c){const m=Mesh(),cc=new T.Color(c);m.add(new T.BoxGeometry(1,.8,1),cc,M4(0,.4,0,1,1,1));m.add(new T.BoxGeometry(1.01,.08,1.2),cc.clone().multiplyScalar(1.5),M4(0,.84,.05,1,1,1));m.add(new T.BoxGeometry(.98,.5,.02),cc.clone().multiplyScalar(.55),M4(0,.35,.51,1,1,1));return m.geo();},
  plants(c){const m=Mesh();for(let i=0;i<4;i++){const x=-.36+i*.24;m.add(new T.CylinderGeometry(.09,.07,.2,6),0x6a4a2a,M4(x,.1,0,1,1,1));m.add(jitter(new T.IcosahedronGeometry(.13+hash(i,1,1)*.05,0),.4,i+1),i===1?0xc050c0:0x3f7a32,M4(x,.3,0,1,1.3,1));}return m.geo();},
  window(c){const m=Mesh();m.add(new T.BoxGeometry(1,1,.3),0x4a2e18,M4(0,.5,0,1,1,1));m.add(new T.BoxGeometry(.78,.78,.34),0xbfe0f4,M4(0,.5,0,1,1,1));m.add(new T.BoxGeometry(.04,.78,.36),0x4a2e18,M4(0,.5,0,1,1,1));m.add(new T.BoxGeometry(.78,.04,.36),0x4a2e18,M4(0,.5,0,1,1,1));return m.geo();},
  trophy(c){const m=Mesh();m.add(jitter(new T.IcosahedronGeometry(.4,0),.2,3),c,M4(0,.5,0,1,1,.7));[-.3,.3].forEach(x=>m.add(new T.SphereGeometry(.12,6,5),c,M4(x,.85,0,1,1,.6)));m.add(new T.BoxGeometry(.5,.1,.3),0x4a2e18,M4(0,.05,0,1,1,1));return m.geo();},
  wallseg(c){const m=Mesh(),cc=new T.Color(c);m.add(new T.BoxGeometry(1,1,1),cc,M4(0,.5,0,1,1,1));m.add(new T.BoxGeometry(1.01,.1,1.1),cc.clone().multiplyScalar(.7),M4(0,1,0,1,1,1));return m.geo();},
  drape(c){const m=Mesh();m.add(new T.BoxGeometry(1.08,.06,1.5),0x4a2e18,M4(0,.97,0,1,1,1));m.add(new T.BoxGeometry(.96,.9,1),c,M4(0,.5,0,1,1,1));return m.geo();},
  rug(c){const m=Mesh();m.add(new T.BoxGeometry(1,.03,1),c,M4(0,.02,0,1,1,1));m.add(new T.BoxGeometry(.8,.035,.8),new T.Color(c).multiplyScalar(1.3),M4(0,.025,0,1,1,1));return m.geo();},
  forge(c){const m=Mesh(),cc=new T.Color(c);m.add(new T.BoxGeometry(1,.45,1),cc,M4(0,.22,0,1,1,1));m.add(new T.ConeGeometry(.75,.45,4),cc.clone().multiplyScalar(1.1),M4(0,.67,0,1,1,1).multiply(new T.Matrix4().makeRotationY(Math.PI/4)));m.add(new T.BoxGeometry(.3,.6,.4),cc.clone().multiplyScalar(.9),M4(0,1.1,0,1,1,1));
    m.add(new T.BoxGeometry(.5,.26,.04),0x1a0e08,M4(0,.22,.52,1,1,1));m.add(new T.BoxGeometry(.4,.14,.045),0xff7a20,M4(0,.17,.53,1,1,1));return m.geo();},
  table(c){const m=Mesh(),cc=new T.Color(c);m.add(new T.BoxGeometry(1,.1,.7),cc,M4(0,.68,0,1,1,1));[[-.44,-.28],[.44,-.28],[-.44,.28],[.44,.28]].forEach(([x,z])=>m.add(new T.BoxGeometry(.08,.66,.08),cc.clone().multiplyScalar(.7),M4(x,.33,z,1,1,1)));[-.5,.5].forEach(z=>m.add(new T.BoxGeometry(.9,.08,.2),cc.clone().multiplyScalar(.85),M4(0,.4,z*1.1,1,1,1)));return m.geo();},
  frost(c){const m=Mesh();m.add(new T.CylinderGeometry(.05,.11,.62,6),0x3a2a22,M4(0,.31,0,1,1,1));[[.16,.55,0,.5,-1.0],[-.18,.62,.02,.45,1.1],[.04,.76,-.12,.4,.3],[0,.8,.1,.35,-.4]].forEach(([x,y,z,l,rz])=>m.add(new T.CylinderGeometry(.015,.04,l,5),0x4a3a30,M4(x,y,z,1,1,1,0,rz)));
    for(let i=0;i<14;i++)m.add(new T.OctahedronGeometry(.045,0),0xa8dcff,M4((hash(i,1,2)-.5)*.8,.6+hash(i,2,2)*.55,(hash(i,3,2)-.5)*.5,1,1.6,1));return m.geo();},
  barrelpile(c){const m=Mesh();[[-.25,-.1],[.25,-.1],[0,.2]].forEach(([x,z],i)=>{m.add(new T.CylinderGeometry(.24,.2,.6,9),0x7a5230,M4(x,.3,z,1,1,1));[.15,.45].forEach(y=>m.add(new T.CylinderGeometry(.245,.245,.04,9),0x2a2a2e,M4(x,y,z,1,1,1)));});return m.geo();},
  hedge(c){const m=Mesh(),cc=new T.Color(c);[[0,-.34,.3],[.05,0,.34],[-.04,.34,.3]].forEach(([x,z,r],i)=>m.add(jitter(new T.IcosahedronGeometry(r+.1,1),.3,i+3),cc.clone().multiplyScalar(.85+i*.1),M4(x,.3,z,1,.85,1)));return m.geo();},
  flag(c){const m=Mesh(),cc=new T.Color(c);m.add(new T.CylinderGeometry(.03,.04,1,5),0x3a3a40,M4(0,.5,0,1,1,1));m.add(new T.BoxGeometry(.7,.55,.04),cc,M4(.38,.68,0,1,1,1));m.add(new T.ConeGeometry(.35,.18,3),cc,M4(.38,.34,0,1,1,.12,0,Math.PI));return m.geo();},
  sign(c){const m=Mesh();m.add(new T.CylinderGeometry(.04,.05,1,5),0x4a3220,M4(0,.5,0,1,1,1));m.add(new T.BoxGeometry(.6,.14,.04),0x7a5a30,M4(.2,.88,0,1,1,1));m.add(new T.BoxGeometry(.55,.14,.04),0x7a5a30,M4(-.18,.68,0,1,1,1));return m.geo();},
  stall(c){const m=Mesh();[[-.45,-.4],[.45,-.4],[-.45,.4],[.45,.4]].forEach(([x,z])=>m.add(new T.CylinderGeometry(.03,.03,.9,5),0x5a3a20,M4(x,.45,z,1,1,1)));
    for(let i=0;i<6;i++)m.add(new T.BoxGeometry(.18,.04,1.0),i%2?0xf2ecd8:0xb83a30,M4(-.43+i*.172,.98-Math.abs(i-2.5)*0.0,0,1,1,1,.0,0));m.add(new T.BoxGeometry(.96,.4,.4),0x7a5230,M4(0,.2,.1,1,1,1));return m.geo();},
  well(c){const m=Mesh();m.add(new T.CylinderGeometry(.42,.46,.42,10),0x8a8a90,M4(0,.21,0,1,1,1));m.add(new T.CylinderGeometry(.3,.3,.02,10),0x1a2a3a,M4(0,.4,0,1,1,1));[-.38,.38].forEach(x=>m.add(new T.BoxGeometry(.06,.8,.06),0x4a3220,M4(x,.7,0,1,1,1)));m.add(new T.ConeGeometry(.62,.32,4),0x8a4a30,M4(0,1.28,0,1,1,1).multiply(new T.Matrix4().makeRotationY(Math.PI/4)));m.add(new T.CylinderGeometry(.03,.03,.78,5),0x4a3220,M4(0,1.0,0,1,1,1,0,1.5708));return m.geo();},
  pebble(c){const m=Mesh();m.add(jitter(new T.DodecahedronGeometry(.2,0),.4,1),c,M4(0,.06,0,1,.55,1));return m.geo();}
};
MODELS.slime=MODELS.blood=MODELS.puddle;
// ---- classificação a partir dos dados do mapa (tamanho + cor média do recorte do atlas)
const colCache={};
function avgCol(env,id){if(colCache[id])return colCache[id];const a=env.ATLAS_J[id],c=cv(16,16),x=c.getContext('2d',{willReadFrequently:true});x.drawImage(env.ATLAS,a[0],a[1],a[2],a[3],0,0,16,16);const d=x.getImageData(0,0,16,16).data;let r=0,g=0,b=0,w=0,br=0;
  for(let i=0;i<256;i++){const al=d[i*4+3];r+=d[i*4]*al;g+=d[i*4+1]*al;b+=d[i*4+2]*al;w+=al;if(al>128&&d[i*4]*.3+d[i*4+1]*.59+d[i*4+2]*.11>150)br++;}w=w||1;const o=[r/w,g/w,b/w];o.bright=br/256;return colCache[id]=o;}
function kindOf(a,rgb,flat){const [,,w,h]=a,[r,g,b]=rgb,mx=Math.max(r,g,b),mn=Math.min(r,g,b),sat=(mx-mn)/(mx||1),green=g>r+6&&g>=b-4,teal=b>r+6&&g>r,beige=r>150&&g>128&&b>85&&sat<.5,yellow=r>150&&g>125&&b<110&&sat>.35;
  if(flat){if(w>=28||h>=28){if(green||(g>=r-8&&sat<.4&&w>=h*1.3&&mx<150))return 'puddle';if(beige)return 'bones';if(r>g&&sat>.2)return w>=h*1.4?'puddle':'twig';return h>=28&&w<40?'tuft':null;}
    if(green)return 'tuft';if(beige)return 'bones';if(sat<.18)return 'pebble';if(r>g+12&&sat>.3&&mx<150&&w>=h)return 'twig';if(sat>.22&&mx>95)return 'flower';return 'tuft';}
  if(h>=100)return (teal||green)?(b>=g-16?'conifer':'broad'):(r>g+6?'dead':'broad');
  if(w>=80&&h<=80)return 'tent';
  if(w>=60&&h>=45&&h<80)return 'drums';
  if(w<=50&&h>=80)return 'totem';
  if(w<=22&&h>=35)return 'post';
  if(yellow&&h<=45)return 'mush';
  if(h<=70&&w>=28&&w<=50&&h>=28&&r>g&&mx<150&&sat>.15)return 'thorn';
  if(h<=70&&w>=18)return (green&&sat>.18)?'bush':(sat<.45?'rock':null);
  return null;}
function kindDg(a,rgb,flat){const [,,w,h]=a,[r,g,b]=rgb,mx=Math.max(r,g,b),mn=Math.min(r,g,b),sat=(mx-mn)/(mx||1),beige=r>150&&g>128&&b>85&&sat<.5,brown=r>g+8&&g>=b-6&&sat>.22,stone=sat<.4&&mx>60&&b>=r-8;
  if(flat){if(w>=60&&h>=40&&b>r+25&&sat>.3)return 'rune';if(w>=24&&g>r+14&&g>b)return 'slime';if(r>g+28&&r>b+28&&w>=16)return 'blood';
    if(sat<.16&&mx>140&&w>=28)return null;if(beige||rgb.bright>.025)return 'bones';if(w>=28&&w>=h*1.25&&sat>.12&&mx<120)return 'puddle';return w>=28?null:'pebble';}
  if(w<=22&&h>=30)return 'post';
  if(h>=60&&w<=44&&stone)return 'pillar';
  if(h>=44&&w<=54&&h>=w*1.15&&!brown&&sat>.28&&!(g>r&&g>b&&sat<.4))return 'banner';
  if(brown){if(w*1.3<=h)return h>=70?'coffin':'barrel';if(h<=36&&w>=24)return 'chest';return 'crate';}
  if(stone){if(w>=50)return 'tomb';if(w<=34&&h<=46&&h>=20)return 'tombstone';if(w<=30&&h<=30)return 'urn';}
  return h>=w*2.1?'column':'block';}

// ---- chão de masmorra: lajes, rejunte, rachaduras, musgo/sangue; água (esgoto) vem da máscara do jogo
P.dungeonFloor=function(env,pal,seed){
  const M=masks(env),S=.5,w=Math.round(env.W*S),h=Math.round(env.H*S),c=cv(w,h),x=c.getContext('2d'),im=x.createImageData(w,h),d=im.data,s0=seed||3;
  for(let py=0;py<h;py++)for(let px=0;px<w;px++){const gx=px/S,gy=py/S,mx=gx/4,my=gy/4,sp=hash(px,py,s0);
    const bw=pal.bw||32,bh=pal.bh||24,row=Math.floor(gy/bh),off=(row%2)*bw*.5,col=Math.floor((gx+off)/bw),fx=(gx+off)-col*bw,fy=gy-row*bh;
    const tone=hash(col,row,s0)*.34+.83,n=fbm(gx/60,gy/60,s0),n2=fbm(gx/9,gy/9,s0+2);
    let c0=mix(pal.f1,pal.f2,hash(col,row,s0+4));c0=[c0[0]*tone,c0[1]*tone,c0[2]*tone];c0=mix(c0,pal.f3,sst(.5,.8,n)*.45);
    const edge=Math.min(fx,bw-fx,(fy)*(bw/bh),(bh-fy)*(bw/bh));
    if(edge<1.6)c0=mix(c0,pal.mortar,.85);else if(edge<3)c0=mix(c0,pal.f3,.25);
    c0=mix(c0,[0,0,0],(n2-.5)*.22+(sp>.96?.12:0));
    if(pal.moss){const mv=fbm(gx/40,gy/40,s0+11);if(mv>.6)c0=mix(c0,pal.moss,sst(.6,.72,mv)*.7);}
    if(pal.stain){const sv=fbm(gx/70,gy/70,s0+21);if(sv>.7&&hash(col,row,s0+9)>.3)c0=mix(c0,pal.stain,.55);}
    const wv=samp(M.water,M.gw,M.gh,mx,my)+(n2-.5)*.1;
    if(wv>.25){const wt=sst(.25,.5,wv),dp=sst(.5,.9,wv);let wc=mix(pal.w1,pal.w2,dp);wc=mix(wc,[255,255,255],sp>.99?.25:0);c0=mix(c0,mix(pal.shore||pal.mortar,wc,sst(.4,.5,wv)),wt);}
    const k=(py*w+px)*4;d[k]=c0[0];d[k+1]=c0[1];d[k+2]=c0[2];d[k+3]=255;}
  x.putImageData(im,0,0);return {canvas:c,M};
};
// ---- piso de madeira (interiores)
P.woodFloor=function(env,pal,seed){
  const S=1,w=env.W,h=env.H,c=cv(w,h),x=c.getContext('2d'),s0=seed||5;
  x.fillStyle=pal.base;x.fillRect(0,0,w,h);const ph=13;
  for(let r=0;r<Math.ceil(h/ph);r++){let px=-hash(r,1,s0)*60;while(px<w){const len=50+hash(Math.floor(px),r,s0)*70,t=.82+hash(Math.floor(px)+3,r,s0+1)*.3;x.fillStyle=`rgb(${pal.p.map(v=>Math.round(v*t)).join(',')})`;x.fillRect(px+1,r*ph+1,len-2,ph-2);
    x.fillStyle='rgba(0,0,0,.18)';x.fillRect(px,r*ph+ph-1,len,1);x.fillRect(px+len-1,r*ph,1,ph);for(let g=0;g<3;g++){x.fillStyle='rgba(60,30,10,.14)';x.fillRect(px+4+hash(g,Math.floor(px),r)*len,r*ph+2+g*3,10+hash(g,r,2)*24,1);}px+=len;}}
  return {canvas:c,M:null};
};

P.woodWall=function(w,h,seed){const c=cv(w*2,h*2),x=c.getContext('2d');x.scale(2,2);x.fillStyle='#3a2616';x.fillRect(0,0,w,h);
  for(let i=0;i<w/10;i++){const t=.8+hash(i,1,seed||1)*.35;x.fillStyle=`rgb(${Math.round(106*t)},${Math.round(70*t)},${Math.round(38*t)})`;x.fillRect(i*10+.5,0,9,h);x.fillStyle='rgba(0,0,0,.25)';x.fillRect(i*10+9,0,1,h);for(let g=0;g<4;g++){x.fillStyle='rgba(40,20,8,.18)';x.fillRect(i*10+2+g,hash(i,g,5)*h,1,12+hash(i,g,6)*20);}}
  x.fillStyle='#2a190c';x.fillRect(0,0,w,8);x.fillRect(0,h*.62,w,6);x.fillRect(0,h-10,w,10);for(const px of [0,w/3,2*w/3,w-8])x.fillRect(px,0,8,h);
  for(const wx of [w*.2,w*.72]){x.fillStyle='#1a0e06';x.fillRect(wx-3,16,56,50);const g=x.createLinearGradient(0,18,0,64);g.addColorStop(0,'#a9d2f0');g.addColorStop(1,'#e8f2f8');x.fillStyle=g;x.fillRect(wx,19,50,44);x.fillStyle='#1a0e06';x.fillRect(wx+24,19,3,44);x.fillRect(wx,39,50,3);}
  const t=new T.CanvasTexture(c);t.encoding=T.sRGBEncoding;return t;};
// ---- paredes 3D a partir de uma grade (isF(cx,cy): é chão?)
P.walls=function(add,o){
  const {rows,cols,isF,cw,ch,ox,oy,radius=1,brickCol='#2a2d38',capCol='#454a5a',moss=0}=o;
  const U_=U,gw=cw*U_,gh=ch*U_;
  const brick=(()=>{const c=cv(128,128),x=c.getContext('2d');x.fillStyle='#14161c';x.fillRect(0,0,128,128);const bc=new T.Color(brickCol);for(let j=0;j<4;j++)for(let i=-1;i<3;i++){const px=i*64+(j%2?32:0)+1,py=j*32+2,l=.7+Math.random()*.6;x.fillStyle='#'+bc.clone().multiplyScalar(l).getHexString();x.fillRect(px,py,61,28);x.fillStyle='rgba(255,255,255,.07)';x.fillRect(px,py,61,2);if(moss&&Math.random()<moss){x.fillStyle='rgba(70,110,40,.55)';x.fillRect(px+Math.random()*30,py+14,20+Math.random()*30,14);}}
    const t=new T.CanvasTexture(c);t.encoding=T.sRGBEncoding;t.wrapS=t.wrapT=T.RepeatWrapping;t.anisotropy=4;return t;})();
  const cap=(()=>{const c=cv(64,64),x=c.getContext('2d');x.fillStyle=capCol;x.fillRect(0,0,64,64);for(let i=0;i<120;i++){x.fillStyle=`rgba(${Math.random()<.5?'0,0,0':'255,255,255'},${.04+Math.random()*.06})`;x.fillRect(Math.random()*64,Math.random()*64,2+Math.random()*6,2+Math.random()*4);}const t=new T.CanvasTexture(c);t.encoding=T.sRGBEncoding;return t;})();
  const wall=new Uint8Array(rows*cols);
  for(let cy=0;cy<rows;cy++)for(let cx=0;cx<cols;cx++){if(isF(cx,cy))continue;let near=false;for(let dy=-radius;dy<=radius&&!near;dy++)for(let dx=-radius;dx<=radius;dx++)if(isF(cx+dx,cy+dy)){near=true;break;}if(near)wall[cy*cols+cx]=1;}
  const W=(x,y)=>x>=0&&y>=0&&x<cols&&y<rows&&wall[y*cols+x];
  const sp=[],su=[],si=[],tp=[],tu=[],ti=[];let sn=0,tn=0;
  const sq=(Pp,Uu,I,n,v,uv)=>{v.forEach(q=>Pp.push(...q));uv.forEach(q=>Uu.push(...q));I.push(n,n+1,n+2,n,n+2,n+3);};
  for(let cy=0;cy<rows;cy++)for(let cx=0;cx<cols;cx++){if(!W(cx,cy))continue;
    let fS=false,fEW=false;for(let k=1;k<=radius;k++){if(isF(cx,cy+k))fS=true;if(isF(cx+k,cy)||isF(cx-k,cy))fEW=true;}
    const h=fS?3.4:(fEW?1.5:.9),x0=ox+cx*gw,x1=x0+gw,z0=(oy+cy*ch)*U_,z1=z0+gh,vv=h/gw;
    sq(tp,tu,ti,tn,[[x0,h,z1],[x1,h,z1],[x1,h,z0],[x0,h,z0]],[[0,0],[1,0],[1,1],[0,1]]);tn+=4;
    if(!W(cx,cy+1)){sq(sp,su,si,sn,[[x0,0,z1],[x1,0,z1],[x1,h,z1],[x0,h,z1]],[[0,0],[1,0],[1,vv],[0,vv]]);sn+=4;}
    if(!W(cx+1,cy)){sq(sp,su,si,sn,[[x1,0,z1],[x1,0,z0],[x1,h,z0],[x1,h,z1]],[[0,0],[1,0],[1,vv],[0,vv]]);sn+=4;}
    if(!W(cx-1,cy)){sq(sp,su,si,sn,[[x0,0,z0],[x0,0,z1],[x0,h,z1],[x0,h,z0]],[[0,0],[1,0],[1,vv],[0,vv]]);sn+=4;}}
  const bg=(Pp,Uu,I)=>{const g=new T.BufferGeometry();g.setAttribute('position',new T.Float32BufferAttribute(Pp,3));g.setAttribute('uv',new T.Float32BufferAttribute(Uu,2));g.setIndex(I);g.computeVertexNormals();return g;};
  if(sn)add(new T.Mesh(bg(sp,su,si),new T.MeshStandardMaterial({map:brick,roughness:.95,side:T.DoubleSide})));
  if(tn)add(new T.Mesh(bg(tp,tu,ti),new T.MeshStandardMaterial({map:cap,roughness:.9,side:T.DoubleSide})));
  return {wall};
};
// ---- fogueira / tocha procedurais: pedras, toras e chama em shader (sem imagens)
const flameMat=()=>new T.ShaderMaterial({transparent:true,depthWrite:false,blending:T.AdditiveBlending,side:T.DoubleSide,uniforms:{t:P.time,seed:{value:0}},
  vertexShader:'varying vec2 vUv;void main(){vUv=uv;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}',
  fragmentShader:'varying vec2 vUv;uniform float t;float h(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}float n(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(h(i),h(i+vec2(1,0)),f.x),mix(h(i+vec2(0,1)),h(i+vec2(1,1)),f.x),f.y);}void main(){vec2 u=vUv;float y=u.y;float w=(1.-y)*.5*(.7+.3*n(vec2(y*3.,t*2.)));float x=abs(u.x-.5)+(n(vec2(u.x*4.,y*3.-t*3.5))-.5)*.35*y;float f=smoothstep(w,w*.2,x)*(1.-y*.85);if(f<.02)discard;vec3 c=mix(vec3(1.,.95,.6),vec3(1.,.35,.05),y*1.2);gl_FragColor=vec4(c*(1.2+f),f);}'});
P.fire=function(add,x,z,s,kind){
  const g=new T.Group();g.position.set(x,0,z);const lm=new T.MeshStandardMaterial({color:0x3a2616,roughness:1}),sm=new T.MeshStandardMaterial({color:0x6a6a70,roughness:1,flatShading:true});
  if(kind==='torch'){const st=new T.Mesh(new T.CylinderGeometry(.04,.05,.9*s,6),lm);st.position.y=.45*s;g.add(st);const cup=new T.Mesh(new T.CylinderGeometry(.1,.06,.12,6),new T.MeshStandardMaterial({color:0x2a2a2e}));cup.position.y=.92*s;g.add(cup);}
  else{for(let i=0;i<3;i++){const l=new T.Mesh(new T.CylinderGeometry(.06,.07,.8*s,6),lm);l.rotation.z=1.4;l.rotation.y=i*1.05;l.position.y=.09;g.add(l);}
    for(let i=0;i<8;i++){const a=i/8*6.283,r=new T.Mesh(new T.DodecahedronGeometry(.13*s,0),sm);r.position.set(Math.cos(a)*.5*s,.08,Math.sin(a)*.5*s);r.scale.y=.7;g.add(r);}}
  const fh=(kind==='torch'?.55:1.1)*s,fw=(kind==='torch'?.4:.8)*s,fy=kind==='torch'?.95*s:.1;
  for(let i=0;i<2;i++){const f=new T.Mesh(new T.PlaneGeometry(fw,fh),flameMat());f.position.y=fy+fh/2;f.rotation.y=i*Math.PI/2;g.add(f);}
  add(g);return g;};
const DIMS={bench:16,planter:16,cabinet:26,potshelf:26,longcounter:30,plants:18,window:6,wallseg:16,drape:6,rug:(w,h)=>h*1.3,forge:46,table:56,stall:44,sign:8,flag:8,well:60,barrelpile:36,hedge:(w,h)=>h*.8,trophy:14};
const TOWNMAP={'7721':'lamp','d6ee':'lamp','0ed4':'lamp','5a6a':'lamp','52e1':'lamp','c15b':'barrelpile','4ce7':'barrelpile','8291':'bench','769a':'bench','9304':'flag','7c7e':'flag','63e3':'planter','afca':'planter','8a8b':'sign','df9b':'stall','15eb':'well','32e6':'hedge','718d':'hedge'};
const INMAP={'5dfc':'cabinet','0dd8':'cabinet','ae14':'potshelf','f586':'potshelf','2774':'potshelf','adee':'longcounter','6bde':'plants','1168':'window','5d78':'trophy','ecbe':'wallseg','a719':'wallseg','0367':'wallseg','e04f':'wallseg','df00':'drape','3820':'drape','64c7':'bench','dca1':'rug','1c44':'forge','fbc2':'forge','f1a3':'lamp','5b39':'table','a94a':'table'};
function kindTown(a,rgb,flat,id){const mk0=TOWNMAP[(id||'').slice(0,4)];if(mk0)return (mk0==='bench'||mk0==='planter')?mk0:null;const [,,w,h]=a,[r,g,b]=rgb,mx=Math.max(r,g,b),mn=Math.min(r,g,b),sat=(mx-mn)/(mx||1),green=g>r+6&&g>=b-4,brown=r>g+8&&g>=b-6&&sat>.22;
  if(flat)return rgb[1]>rgb[0]+6?'tuft':'flower';
  if(h>=100&&w>=90)return (b>=r-4)?'frost':(sat<.5?'dead':'broad');
  if(h<=70&&w>=18&&green&&sat>.18)return 'bush';
  return null;}
function kindIn(a,rgb,flat,id){return null;const mk0=INMAP[(id||'').slice(0,4)];if(mk0)return mk0;const [,,w,h]=a,[r,g,b]=rgb,sat=(Math.max(r,g,b)-Math.min(r,g,b))/(Math.max(r,g,b)||1),green=g>r+6&&g>=b-4;
  if(flat)return null;if(h<=70&&green&&sat>.18)return 'bush';if(w<=22&&h>=60)return 'lamp';return kindDg(a,rgb,false);}
// ---- floresta: devolve o que sobrou (props sem modelo) para continuarem como sprites
P.forest=function(env,add,rnd,items,theme){const DG=theme==='dungeon'||theme==='indoor';
  const mats={},buckets={},rest={stand:[],flats:[]};
  const take=(list,flat)=>{for(const it of list){const [id,x,y]=it,a=env.ATLAS_J[id];if(!a)continue;const rgb=avgCol(env,id),k=theme==='indoor'?kindIn(a,rgb,flat,id):theme==='town'?kindTown(a,rgb,flat,id):DG?kindDg(a,rgb,flat):kindOf(a,rgb,flat);if(!k||!MODELS[k]){if(k&&!MODELS[k])console.warn('[v3] sem modelo:',k);if(DG&&flat)continue;(flat?rest.flats:rest.stand).push(it);continue;}(buckets[k]=buckets[k]||[]).push({x,y,a,rgb});}};
  take(items.stand,false);take(items.flats,true);
  const runeMat=()=>new T.MeshBasicMaterial({vertexColors:true,transparent:true,blending:T.AdditiveBlending,depthWrite:false,opacity:.9});
  const slimeMat=()=>new T.MeshStandardMaterial({vertexColors:true,emissive:0x40c040,emissiveIntensity:.5,roughness:.3});
  const mk=sw=>{const m=new T.MeshStandardMaterial({vertexColors:true,flatShading:true,roughness:.92});if(sw)m.onBeforeCompile=sh=>{sh.uniforms.uTime=P.time;sh.vertexShader='uniform float uTime;\n'+sh.vertexShader.replace('#include <begin_vertex>','#include <begin_vertex>\n#ifdef USE_INSTANCING\nfloat ph=instanceMatrix[3].x*.9+instanceMatrix[3].z*.6;\n#else\nfloat ph=0.;\n#endif\ntransformed.x+=sin(uTime*1.7+ph)*position.y*'+sw.toFixed(3)+';transformed.z+=cos(uTime*1.3+ph*1.3)*position.y*'+(sw*.6).toFixed(3)+';');};return m;};
  const SW={tuft:.35,flower:.25,bush:.05,broad:.02,conifer:.012,dead:.01,mush:0};
  const BASE={conifer:[28,66,62],broad:[74,92,46],tuft:[78,128,52],bush:[58,104,46],rock:[118,118,112],thorn:[84,58,36],tent:[130,84,58],puddle:null,bones:[214,204,176],twig:[84,60,40],mush:[220,190,70],pillar:null,banner:null,lamp:[40,40,46],bench:[122,86,50],planter:[110,74,44],barrel:[110,76,44],crate:[120,84,48],chest:[122,80,40],coffin:[90,62,40],tomb:null,tombstone:null,urn:null,block:null,column:null,rune:null,slime:[96,200,70],blood:[96,24,22]};
  for(const k in buckets){const L=buckets[k];if(!L.length)continue;
    const avg=L.reduce((s,q)=>[s[0]+q.rgb[0],s[1]+q.rgb[1],s[2]+q.rgb[2]],[0,0,0]).map(v=>v/L.length);
    const base=(theme==='town'&&(k==='broad'||k==='dead'||k==='bush'))?avg:k==='rune'?avg.map(v=>Math.min(255,v*2.6+20)):(BASE[k]||avg);
    const col=new T.Color(`rgb(${base.map(Math.round).join(',')})`);
    const geo=MODELS[k](k==='flower'?0xffffff:col),im=new T.InstancedMesh(geo,(k==='rune'?runeMat():k==='slime'?slimeMat():mk(SW[k]||0)),L.length),m4=new T.Matrix4(),q=new T.Quaternion(),e=new T.Euler();
    im.castShadow=!(k==='rune'||k==='slime'||k==='blood'||k==='puddle'||k==='bones'||k==='twig'||k==='pebble'||k==='tuft'||k==='flower');im.receiveShadow=true;
    L.forEach((it,i)=>{const w=it.a[2],h=it.a[3],r=hash(Math.round(it.x),Math.round(it.y),11);let H,R;
      const DM=DIMS[k];
      if(DM){H=h*U/CT*.85*({forge:.7,well:.75,cabinet:.9}[k]||1);R=w*U*.5;}else if(k==='conifer'||k==='broad'||k==='dead'||k==='frost'){H=h*U/CT*.8;R=w*U*.5;}else if(k==='post'){H=h*U/CT*.85;R=1;}
      else if(k==='rock'||k==='bush'||k==='thorn'){H=Math.max(.5,h*U/CT*.9);R=Math.max(.6,w*U*.6);}
      else if(k==='lamp'||k==='pillar'||k==='banner'||k==='column'||k==='tombstone'||k==='urn'||k==='barrel'||k==='crate'||k==='chest'||k==='coffin'||k==='block'||k==='tomb'){H=h*U/CT*.85;R=w*U*.5;}
      else if(k==='rune'||k==='slime'||k==='blood'){H=1;R=Math.max(.3,Math.max(w,h*1.2)*U*.5);}
      else if(k==='tent'||k==='drums'||k==='totem'||k==='mush'){H=h*U/CT*.85;R=w*U*.5;}
      else if(k==='puddle'||k==='twig'){H=1;R=Math.max(.3,Math.max(w,h*1.2)*U*.5);}else if(k==='bones'){H=1;R=Math.max(.25,Math.max(w,h*1.2)*U*.3);}
      else{H=Math.max(.35,h*U*2.2);R=Math.max(.5,w*U*2);}
      e.set(0,(k==='tent'||k==='drums'||DM?0:r*6.283),0);q.setFromEuler(e);const sc=k==='totem'||k==='post'||DM?1:.9+r*.25;
      const sx=k==='post'?1:(k==='totem'?H*.45:k==='lamp'?Math.max(.55,R*2*2.4):R*2*sc),sz=DM?(typeof DM==='function'?DM(w,h):DM)*U:(k==='post'?1:sx);m4.compose(new T.Vector3(it.x*U,0,it.y*U),q,new T.Vector3(sx,H*sc,sz));im.setMatrixAt(i,m4);
      const c0=new T.Color(k==='flower'?`hsl(${Math.round(hash(i,3,3)*360)},70%,62%)`:'#ffffff');if(k!=='flower')c0.multiplyScalar(.88+hash(i,5,5)*.22);else c0.convertSRGBToLinear();im.setColorAt(i,c0);});
    im.instanceMatrix.needsUpdate=true;if(im.instanceColor)im.instanceColor.needsUpdate=true;im.frustumCulled=false;add(im);}
  P.lastRest=rest;P.lastKinds=Object.fromEntries(Object.entries(buckets).map(([k,v])=>[k,v.length]));
  return rest;
};

// ---- água animada: uma lâmina com shader que lê a máscara do lago (brilhos, ondas e reflexo do céu)
P.waterMesh=function(g,GWu,GHu,tint){
  const M=g.M,c=cv(M.gw,M.gh),x=c.getContext('2d'),im=x.createImageData(M.gw,M.gh);for(let i=0;i<M.gw*M.gh;i++){const v=Math.max(0,Math.min(255,Math.round(M.water[i]*255)));im.data[i*4]=im.data[i*4+1]=im.data[i*4+2]=v;im.data[i*4+3]=255;}x.putImageData(im,0,0);
  const tex=new T.CanvasTexture(c);tex.minFilter=tex.magFilter=T.LinearFilter;
  const mat=new T.ShaderMaterial({transparent:true,depthWrite:false,uniforms:{t:P.time,mask:{value:tex},sz:{value:new T.Vector2(GWu,GHu)},tint:{value:new T.Vector3(...(tint||[.55,.78,.95]))}},
    vertexShader:'varying vec2 vUv;varying vec3 vW;void main(){vUv=uv;vec4 w=modelMatrix*vec4(position,1.);vW=w.xyz;gl_Position=projectionMatrix*viewMatrix*w;}',
    fragmentShader:'uniform sampler2D mask;uniform vec3 tint;uniform float t;varying vec2 vUv;varying vec3 vW;void main(){float m=texture2D(mask,vec2(vUv.x,1.-vUv.y)).r;if(m<.46)discard;float a=smoothstep(.46,.56,m);'+
      'float w1=sin(vW.x*2.3+t*1.1+sin(vW.z*1.7+t*.7)*1.3),w2=sin(vW.z*3.1-t*1.4+sin(vW.x*2.1-t*.5)*1.1);float r=(w1*w2)*.5+.5;'+
      'float sp=pow(max(0.,sin(vW.x*9.+t*2.3)*sin(vW.z*8.-t*1.9)),10.);vec3 c=tint*(.1+.14*r)+vec3(1.)*sp*.55;gl_FragColor=vec4(c,a*(.18+.22*r+sp*.4));}'});
  const mesh=new T.Mesh(new T.PlaneGeometry(GWu,GHu),mat);mesh.rotation.x=-Math.PI/2;mesh.position.set(GWu/2,.04,GHu/2);mesh.renderOrder=2;return mesh;};
P.palCripta={f1:[78,106,122],f2:[62,88,104],f3:[40,58,72],mortar:[22,32,42],bw:32,bh:24,stain:[70,28,28],w1:[40,70,90],w2:[20,40,60]};
P.palEsgoto={f1:[64,84,66],f2:[50,70,58],f3:[34,52,44],mortar:[18,28,24],bw:32,bh:24,moss:[52,92,40],w1:[86,130,50],w2:[50,86,34],shore:[34,52,36]};
P.palCripta2={f1:[70,92,112],f2:[54,76,98],f3:[34,50,70],mortar:[18,26,38],bw:40,bh:30,stain:[60,24,30],w1:[40,70,90],w2:[20,40,60]};
P.palCidade={g1:[62,128,36],g2:[78,144,44],g3:[48,110,30],d1:[116,86,54],d2:[132,100,62],d3:[96,70,44],st:[126,114,98],sm:[72,64,54],shore:[150,130,90],w1:[70,140,170],w2:[34,84,120]};
P.palMadeira={base:'#6a4a2a',p:[148,104,60]};
P.palFloresta={g1:[40,86,34],g2:[56,106,42],g3:[30,68,30],d1:[116,86,54],d2:[132,100,62],d3:[96,70,44],st:[128,128,120],sm:[70,70,66],shore:[150,130,90],w1:[70,140,170],w2:[34,84,120]};
})();
