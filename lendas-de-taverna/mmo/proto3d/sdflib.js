// biblioteca de escultura por SDF: formas -> malha (surface nets) com cores por material e desgaste por curvatura
const clamp=(x,a,b)=>Math.max(a,Math.min(b,x));
const smin=(a,b,k)=>{const h=Math.max(k-Math.abs(a-b),0)/k;return Math.min(a,b)-h*h*k*.25;};
const smax=(a,b,k)=>-smin(-a,-b,k);
const shell=(d,t)=>Math.abs(d)-t;
function ell(px,py,pz,cx,cy,cz,rx,ry,rz){const x=(px-cx)/rx,y=(py-cy)/ry,z=(pz-cz)/rz;const k0=Math.sqrt(x*x+y*y+z*z);const k1=Math.sqrt(x*x/(rx*rx)+y*y/(ry*ry)+z*z/(rz*rz));return k1<1e-9?-Math.min(rx,ry,rz):k0*(k0-1)/k1;}
function cap(px,py,pz,ax,ay,az,bx,by,bz,r0,r1=r0){const pax=px-ax,pay=py-ay,paz=pz-az,bax=bx-ax,bay=by-ay,baz=bz-az;const h=clamp((pax*bax+pay*bay+paz*baz)/(bax*bax+bay*bay+baz*baz),0,1);const dx=pax-bax*h,dy=pay-bay*h,dz=paz-baz*h;return Math.sqrt(dx*dx+dy*dy+dz*dz)-(r0+(r1-r0)*h);}
function torus(px,py,pz,cx,cy,cz,Rr,r){const x=px-cx,y=py-cy,z=pz-cz;const q=Math.sqrt(x*x+z*z)-Rr;return Math.sqrt(q*q+y*y)-r;}
function rbox(px,py,pz,cx,cy,cz,bx,by,bz,r){const qx=Math.abs(px-cx)-bx,qy=Math.abs(py-cy)-by,qz=Math.abs(pz-cz)-bz;return Math.sqrt(Math.max(qx,0)**2+Math.max(qy,0)**2+Math.max(qz,0)**2)+Math.min(Math.max(qx,qy,qz),0)-r;}
function hash(x,y,z){let h=x*374761393+y*668265263+z*2147483647;h=(h^(h>>13))*1274126177;return ((h^(h>>16))&0xffff)/65535;}
function vnoise(x,y,z){const ix=Math.floor(x),iy=Math.floor(y),iz=Math.floor(z),fx=x-ix,fy=y-iy,fz=z-iz,ux=fx*fx*(3-2*fx),uy=fy*fy*(3-2*fy),uz=fz*fz*(3-2*fz);const L=(a,b,t)=>a+(b-a)*t;
  return L(L(L(hash(ix,iy,iz),hash(ix+1,iy,iz),ux),L(hash(ix,iy+1,iz),hash(ix+1,iy+1,iz),ux),uy),L(L(hash(ix,iy,iz+1),hash(ix+1,iy,iz+1),ux),L(hash(ix,iy+1,iz+1),hash(ix+1,iy+1,iz+1),ux),uy),uz);}
function surfaceNets(f,mn,mx,cell){
  const nx=Math.ceil((mx[0]-mn[0])/cell)+1,ny=Math.ceil((mx[1]-mn[1])/cell)+1,nz=Math.ceil((mx[2]-mn[2])/cell)+1;
  const F=new Float32Array(nx*ny*nz),id=(x,y,z)=>x+nx*(y+ny*z);
  for(let z=0;z<nz;z++)for(let y=0;y<ny;y++)for(let x=0;x<nx;x++)F[id(x,y,z)]=f(mn[0]+x*cell,mn[1]+y*cell,mn[2]+z*cell);
  const vidx=new Int32Array(nx*ny*nz).fill(-1),pos=[];
  const E=[[0,1],[1,2],[2,3],[3,0],[4,5],[5,6],[6,7],[7,4],[0,4],[1,5],[2,6],[3,7]],C=[[0,0,0],[1,0,0],[1,1,0],[0,1,0],[0,0,1],[1,0,1],[1,1,1],[0,1,1]];
  for(let z=0;z<nz-1;z++)for(let y=0;y<ny-1;y++)for(let x=0;x<nx-1;x++){
    const v=C.map(c=>F[id(x+c[0],y+c[1],z+c[2])]);let m=0;for(let i=0;i<8;i++)if(v[i]<0)m|=1<<i;if(m===0||m===255)continue;
    let ax=0,ay=0,az=0,n=0;for(const [a,b] of E){if((v[a]<0)!==(v[b]<0)){const t=v[a]/(v[a]-v[b]);ax+=C[a][0]+(C[b][0]-C[a][0])*t;ay+=C[a][1]+(C[b][1]-C[a][1])*t;az+=C[a][2]+(C[b][2]-C[a][2])*t;n++;}}
    vidx[id(x,y,z)]=pos.length/3;pos.push(mn[0]+(x+ax/n)*cell,mn[1]+(y+ay/n)*cell,mn[2]+(z+az/n)*cell);}
  const idx=[];
  for(let z=1;z<nz-1;z++)for(let y=1;y<ny-1;y++)for(let x=1;x<nx-1;x++){
    const s0=F[id(x,y,z)]<0;
    const chk=(dx,dy,dz,cs)=>{const s1=F[id(x+dx,y+dy,z+dz)]<0;if(s0===s1)return;const q=cs.map(c=>vidx[id(x+c[0],y+c[1],z+c[2])]);if(q.some(v=>v<0))return;if(s0)idx.push(q[0],q[1],q[2],q[0],q[2],q[3]);else idx.push(q[0],q[2],q[1],q[0],q[3],q[2]);};
    chk(1,0,0,[[0,-1,-1],[0,0,-1],[0,0,0],[0,-1,0]]);chk(0,1,0,[[-1,0,-1],[-1,0,0],[0,0,0],[0,0,-1]]);chk(0,0,1,[[-1,-1,0],[0,-1,0],[0,0,0],[-1,0,0]]);}
  return {pos,idx};}
const COL={bone:[.86,.8,.66],cloth:[.17,.07,.13],plate:[.16,.15,.22],plateW:[.5,.45,.5],trim:[.62,.4,.2],crown:[.24,.24,.3],glow:[1,.62,1],cape:[.22,.1,.32],blade:[.7,.88,.98],bladeE:[1,1,1]};
const BIAS={glow:-.012,trim:-.006,crown:-.004,plate:-.004,blade:0,cape:0,bone:0,cloth:.002};
/* def: {groups:{id:fn},bounds:[[min],[max]],shift:[sx,sy,sz],cell,smoothPairs:[['bone','cloth',.03]]}  fn(x,y,z) em coords de modelagem; shift subtrai p/ coords locais finais */
function buildGeo(def){
  const ids=Object.keys(def.groups),G=ids.map(k=>def.groups[k]);
  const field=(x,y,z)=>{let d=1e9;const v=G.map(g=>g(x,y,z));if(def.smooth){const a=ids.indexOf(def.smooth[0]),b=ids.indexOf(def.smooth[1]);const s=smin(v[a],v[b],def.smooth[2]);for(let i=0;i<v.length;i++)if(i!==a&&i!==b)d=Math.min(d,v[i]);d=Math.min(d,s);}else for(const q of v)d=Math.min(d,q);return d;};
  const m=surfaceNets(field,def.bounds[0],def.bounds[1],def.cell||.032),n=new Float32Array(m.pos.length),col=new Float32Array(m.pos.length),e=.01,sh=def.shift||[0,0,0];
  for(let i=0;i<m.pos.length;i+=3){const x=m.pos[i],y=m.pos[i+1],z=m.pos[i+2];
    const gx=field(x+e,y,z)-field(x-e,y,z),gy=field(x,y+e,z)-field(x,y-e,z),gz=field(x,y,z+e)-field(x,y,z-e),l=Math.hypot(gx,gy,gz)||1;n[i]=gx/l;n[i+1]=gy/l;n[i+2]=gz/l;
    const ce=.03,curv=(field(x+n[i]*ce,y+n[i+1]*ce,z+n[i+2]*ce)+field(x-n[i]*ce,y-n[i+1]*ce,z-n[i+2]*ce)-2*field(x,y,z))/(ce*ce)*.04;
    const arr=ids.map((k,j)=>[k,G[j](x,y,z)+(BIAS[k]||0)]).sort((a,b)=>a[1]-b[1]);const idk=arr[0][0];let c=COL[idk].slice();const ed=clamp(-curv*.02,0,1),cav=clamp(curv*.02,0,1);
    if(idk==='plate'){const wr=clamp(ed*1.4+(vnoise(x*20,y*20,z*20)-.6)*.5,0,1);c=c.map((v,j)=>v+(COL.plateW[j]-v)*wr);}
    else if(idk==='trim')c=c.map(v=>v*(.8+.5*ed));
    else if(idk==='bone'){const k=.88+.12*vnoise(x*25,y*25,z*25);c=c.map(v=>v*k);}
    else if(idk==='cloth'){const k=.85+.3*vnoise(x*30,y*30,z*30);c=c.map(v=>v*k);}
    else if(idk==='blade'){c=c.map((v,j)=>v+(COL.bladeE[j]-v)*clamp(ed*1.6,0,1));}
    if(idk!=='glow'&&idk!=='blade'){const k=1-.55*cav;c=c.map(v=>v*k);}
    col[i]=c[0];col[i+1]=c[1];col[i+2]=c[2];m.pos[i]-=sh[0];m.pos[i+1]-=sh[1];m.pos[i+2]-=sh[2];}
  const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(m.pos,3));g.setIndex(m.idx);g.setAttribute('normal',new THREE.BufferAttribute(n,3));g.setAttribute('color',new THREE.BufferAttribute(col,3));return g;}
