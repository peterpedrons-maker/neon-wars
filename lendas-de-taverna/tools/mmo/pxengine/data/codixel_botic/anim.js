const {P,ref,rig}=require('./rig.js');
const W=230,H=200,OX=36,OY=20, S=+process.env.HGT/153||64/153;
const PI2=Math.PI*2, sn=Math.sin, cs=Math.cos, ez=t=>t*t*(3-2*t), cl=(v,a=0,b=1)=>Math.max(a,Math.min(b,v));
const pal=P.quantize(ref,32,{dither:false}).palette;
function render(pose,flip){
  const b=new P.Buf(W,H); rig.draw(b,OX,OY,pose,{flip:!!flip});
  const q=P.quantize(b,32,{palette:pal,dither:false}).buf;
  let sm=P.resize(q,Math.round(W*S),Math.round(H*S),{mode:true});
  return P.smoothEdge(P.cleanup(sm,{tol:20}));
}
const A={};
A.idle=n=>[...Array(n)].map((_,i)=>{const t=i/n,s=sn(PI2*t);return{body:{a:0.01*s,dy:-1.6*s},head:{a:0.03*sn(PI2*t-0.7)},armF:{a:0.05*sn(PI2*t-1)},armB:{a:-0.04*s},tail:{a:0.14*sn(PI2*t-1.3)},legL:0,legR:0};});
A.walk=n=>[...Array(n)].map((_,i)=>{const t=i/n,s=sn(PI2*t),c=cs(PI2*t);return{body:{a:0.03*s,dy:-3*Math.abs(s)},head:{a:-0.04*s},armF:{a:-0.1*s},armB:{a:0.22*s},tail:{a:0.18*sn(PI2*t-1)},legL:{a:0.5*s,dy:-5*Math.max(0,c)},legR:{a:-0.5*s,dy:-5*Math.max(0,-c)}};});
const ARM=+process.env.ARMSIGN||-1;
A.attack=n=>[...Array(n)].map((_,i)=>{const t=i/(n-1);let w;
  if(t<0.45){w=ez(t/0.45);return{body:{a:-0.1*w,dx:-3*w},head:{a:-0.08*w},armF:{a:ARM*1.1*w},armB:{a:0.3*w},tail:{a:0.2*w},legL:{a:-0.2*w},legR:{a:0.2*w}};}
  if(t<0.7){w=ez((t-0.45)/0.25);return{body:{a:-0.1+0.28*w,dx:-3+8*w},head:{a:-0.08+0.12*w},armF:{a:ARM*(1.1-2.3*w)},armB:{a:0.3-0.5*w},tail:{a:0.2-0.4*w},legL:{a:-0.2+0.3*w},legR:{a:0.2-0.3*w}};}
  w=ez((t-0.7)/0.3);return{body:{a:0.18*(1-w),dx:5*(1-w)},head:{a:0.04*(1-w)},armF:{a:ARM*(-1.2*(1-w))},armB:{a:-0.2*(1-w)},tail:{a:-0.2*(1-w)},legL:{a:0.1*(1-w)},legR:{a:-0.1*(1-w)}};});
A.cast=n=>[...Array(n)].map((_,i)=>{const t=i/(n-1),w=t<0.5?ez(t/0.5):1-ez((t-0.5)/0.5)*0.0;const k=t<0.6?ez(t/0.6):1;return{body:{a:-0.06*k,dy:-1*k},head:{a:-0.12*k},armF:{a:ARM*-0.55*k},armB:{a:0.1*k},tail:{a:0.2*sn(PI2*t*2)},legL:0,legR:0};});
A.hurt=n=>[...Array(n)].map((_,i)=>{const t=i/(n-1),k=t<0.35?ez(t/0.35):1-ez((t-0.35)/0.65);return{body:{a:-0.16*k,dx:-5*k,dy:2*k},head:{a:-0.22*k},armF:{a:ARM*0.6*k},armB:{a:-0.5*k},tail:{a:0.3*k},legL:{a:0.2*k},legR:{a:-0.2*k}};});
A.death=n=>[...Array(n)].map((_,i)=>{const t=i/(n-1),k=ez(cl(t/0.8));return{body:{a:-1.4*k,dx:24*k,dy:12*k},head:{a:-0.2*k},armF:{a:ARM*0.8*k},armB:{a:-0.9*k},tail:{a:0.25*k},legL:{a:0.5*k},legR:{a:-0.4*k}};});
module.exports={A,render,W,H,S,P};
if(require.main===module){
  const fr=[];const names=[];
  for(const [nm,n,pick] of [['idle',12,[0,3,6,9]],['walk',16,[0,4,8,12]],['attack',10,[0,3,5,9]],['cast',10,[0,4,9]],['hurt',7,[1,3]],['death',11,[0,4,7,10]]]){
    const ps=A[nm](n);for(const i of pick){fr.push({buf:render(ps[i]),label:nm+' '+i,scale:2});}
  }
  P.save(P.sheet(fr,{cols:6,gap:6}),'poses.png');
}
