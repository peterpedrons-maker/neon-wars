const {P,ref,rig}=require('./rig2.js');
const W=320,H=235,OX=135,OY=25,S=64/153;
const pal=P.quantize(ref,32,{dither:false}).palette;
const ez=t=>t*t*(3-2*t), cl=(v,a=0,b=1)=>Math.max(a,Math.min(b,v)), lerp=(a,b,t)=>a+(b-a)*t;
const J=[80,125], FEET=[82,151];
function body(a,fx=0,fy=0,dy=0){
  dy+=-30*Math.pow(Math.min(1,Math.abs(a)/1.55),2); // gira o corpo em volta dos pes (fixos) + deslocamentos
  const f=[FEET[0]-J[0],FEET[1]-J[1]],c=Math.cos(a),s=Math.sin(a);
  const r=[f[0]*c-f[1]*s,f[0]*s+f[1]*c];
  return {a,dx:f[0]-r[0]+fx,dy:f[1]-r[1]+fy+dy};
}
function render(pose,fx){
  const b=new P.Buf(W,H); rig.draw(b,OX,OY,pose,{});
  if(fx)fx(b);
  const q=P.quantize(b,32,{palette:pal,dither:false}).buf;
  let sm=P.resize(q,Math.round(W*S),Math.round(H*S),{mode:true});
  return P.smoothEdge(P.cleanup(sm,{tol:20}));
}
const gx=OX+FEET[0], gy=OY+FEET[1];
function shadow(w,al=0.55,c=0){return b=>{for(let y=-6;y<=6;y++)for(let x=-w;x<=w;x++){if((x/w)**2+(y/6)**2<=1){const px=gx+c+x,py=gy+y+2;if(px>=0&&py>=0&&px<b.w&&py<b.h&&!(b.px[py*b.w+px]>>>24)&&((x+y)&1)<al*2)b.px[py*b.w+px]=0xff241a2e;}}}}
function dust(t,cx){return b=>{const n=7;for(let i=0;i<n;i++){const a=Math.PI*(0.1+0.8*i/(n-1));const d=10+t*38;const r=3+t*7*(1-i%2*0.3);const x=cx+Math.cos(a)*d*(i%2?-1:1)*(1+i*0.05),y=gy-3-Math.sin(a)*d*0.45;const al=1-t;for(let yy=-r;yy<=r;yy++)for(let xx=-r;xx<=r;xx++)if(xx*xx+yy*yy<=r*r&&((xx+yy+i)&1)<(al*1.8)){const px=Math.round(x+xx),py=Math.round(y+yy);if(px>=0&&py>=0&&px<b.w&&py<b.h)b.px[py*b.w+px]=0xffb8a890;}}}}
const comb=(...f)=>b=>f.forEach(g=>g&&g(b));
const keys=[];
const R=(o)=>o;
// 0 guarda
keys.push([{body:body(0),torso:0},shadow(22)]);
// 1 golpe: cabeca estala, bracos para fora
keys.push([{body:body(0,-3),torso:{a:-0.14},head:{a:-0.35},armFu:{a:0.6},armFl:{a:0.5},armBu:{a:-0.6},armBl:{a:-0.4},tailA:{a:0.15},tailB:{a:0.4}},shadow(22)]);
// 2-4 cambaleia, joelhos cedem
for(const [i,k] of [[2,0.35],[3,0.7],[4,1]]){
  keys.push([{body:body(-0.12*k,-6*k,0,5*k),torso:{a:-0.18-0.22*k},head:{a:-0.4-0.1*k},armFu:{a:0.7},armFl:{a:0.8*k},armBu:{a:-0.7},armBl:{a:-0.6},legL:{a:0.35*k},legR:{a:-0.3*k},tailA:{a:0.25*k},tailB:{a:0.6*k}},shadow(22)]);
}
// 5-8 cai (acelera)
const fall=[-0.45,-0.85,-1.25,-1.52];
fall.forEach((a,i)=>{const k=(i+1)/4;keys.push([{body:body(a,-8-6*i,0,2*i),torso:{a:-0.35-0.1*k},head:{a:-0.3+0.1*k},armFu:{a:0.9-0.4*k},armFl:{a:0.6},armBu:{a:-0.8+0.3*k},armBl:{a:-0.3},legL:{a:0.4},legR:{a:-0.35},tailA:{a:0.3},tailB:{a:0.5}},shadow(22+30*k,0.5,-34*k)]);});
// 9 impacto (quica) + poeira
keys.push([{body:body(-1.5,-30,0,-5),torso:{a:-0.1},head:{a:-0.05},armFu:{a:0.4},armFl:{a:-0.2},armBu:{a:-0.4},armBl:{a:-0.2},legL:{a:0.3},legR:{a:-0.2},tailA:{a:0.2},tailB:{a:0.3}},comb(shadow(46,0.5,-46),dust(0.15,gx-36))]);
// 10 bate de novo
keys.push([{body:body(-1.57,-31,0,1),torso:{a:-0.05},head:{a:0.08},armFu:{a:0.2},armFl:{a:-0.1},armBu:{a:-0.2},armBl:{a:0.1},legL:{a:0.15},legR:{a:-0.1},tailA:{a:0.1},tailB:{a:0.15}},comb(shadow(46,0.5,-46),dust(0.4,gx-38))]);
// 11-13 relaxa
[[0.5],[0.8],[1]].forEach(([k],i)=>keys.push([{body:body(-1.57,-31,0,1),torso:{a:0},head:{a:0.15*k},armFu:{a:-0.9*k},armFl:{a:0.6*k},armBu:{a:0.9*k},armBl:{a:0.4*k},legL:{a:0.05},legR:{a:0},tailA:{a:-0.1*k},tailB:{a:-0.2*k}},comb(shadow(46,0.5,-46),i<2?dust(0.6+0.2*i,gx-38):null)]));
const frames=keys.map(([p,fx])=>render(p,fx));
module.exports={frames,render,body,shadow,dust,comb,gx,gy,P};
if(require.main===module){P.save(P.sheet(frames.map((b,i)=>({buf:b,label:'m'+i,scale:2})),{cols:5,gap:4}),'death_new.png');}
