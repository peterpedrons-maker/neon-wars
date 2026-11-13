// partes do Rei Esquecido (coords locais do osso: y do osso proximal -> distal, z = frente)
const P={};
// --- cabeca: caveira + mandibula + vertebras (sem coroa) ---
P.head={bounds:[[-.5,3.5,-.45],[.5,4.65,.5]],shift:[0,4.13,0],cell:.026,groups:{
 bone:(x,y,z)=>{const ax=Math.abs(x);let d=ell(x,y,z,0,4.25,.02,.31,.37,.35);d=smin(d,ell(ax,y,z,.2,4.12,.2,.1,.09,.1),.09);d=smin(d,rbox(x,y,z,0,3.93,.14,.16,.07,.15,.04),.06);
  if(ax<.17){const rx=((x+.3)%.06+.06)%.06-.03;d=smin(d,rbox(rx,y,z,0,3.98,.28,.018,.035,.02,.006),.012);}
  d=smin(d,cap(x,y,z,0,3.55,0,0,3.95,0,.085),.05);for(let i=0;i<3;i++)d=smin(d,torus(x,y,z,0,3.68+i*.1,0,.085,.028),.03);
  d=smax(d,-ell(ax,y,z,.125,4.28,.3,.085,.095,.08),.03);d=smax(d,-ell(x,y,z,0,4.12,.35,.032,.06,.05),.02);d=smax(d,-ell(ax,y,z,.27,4.15,.1,.05,.12,.12),.04);return d;}}};
P.crown={bounds:[[-.5,4.35,-.45],[.5,5.2,.45]],shift:[0,4.47,0],cell:.022,groups:{
 crown:(x,y,z)=>{let d=torus(x,y,z,0,4.52,0,.31,.032);d=smin(d,torus(x,y,z,0,4.6,0,.3,.022),.03);for(let i=0;i<7;i++){const a=i/7*Math.PI*2,h=.34+.17*(i%2),sx=Math.sin(a)*.3,sz=Math.cos(a)*.3;d=smin(d,cap(x,y,z,sx,4.52,sz,sx*1.08,4.52+h,sz*1.08,.05,.01),.025);}return d;},
 glow:(x,y,z)=>{let d=1e9;for(let i=0;i<7;i++){const a=i/7*Math.PI*2,h=.34+.17*(i%2);d=Math.min(d,ell(x,y,z,Math.sin(a)*.3*1.08,4.52+h+.012,Math.cos(a)*.3*1.08,.03,.03,.03));}return d;}}};
// --- torso: gibao, peitoral, lames, gorjal, ombreiras em laminas, gola de tras, bronze ---
const CH=2.83;
P.chest={bounds:[[-1.7,2.2,-.8],[1.7,4.0,.85]],shift:[0,CH,0],cell:.03,groups:{
 cloth:(x,y,z)=>{let d=ell(x,y,z,0,2.98,.02,.72,.8,.46);d=smin(d,cap(x,y,z,0,3.5,0,0,3.72,0,.2),.1);d+=.005*Math.sin(y*90)*Math.sin(x*70);return d;},
 plate:(x,y,z)=>{const ax=Math.abs(x);
  let c=shell(ell(x,y,z,0,3.0,.03,.8,.85,.52),.04);c=smax(c,-(z+.12),.04);c=smax(c,y-3.62+ax*.35,.05);c=smax(c,-(y-2.62)-ax*.25,.05);c=smin(c,cap(x,y,z,0,3.5,.46,0,2.7,.5,.07,.045),.04);
  for(const gx of[-.3,.3])c=smax(c,-cap(x,y,z,gx,3.45,.5,gx*1.15,2.75,.5,.02),.012);c=smax(c,-torus(x,y,z,0,3.3,0,.55,.014),.01);
  let g=Math.min(torus(x,y,z,0,3.66,0,.4,.05),torus(x,y,z,0,3.76,0,.34,.045));g=smin(g,shell(ell(x,y,z,0,3.7,0,.42,.14,.38),.035),.03);g=smax(g,-(y-3.9),.03);
  let q=shell(ell(ax,y,z,1.0,3.46,0,.56,.2,.5),.035);q=smax(q,-(y-3.6),.03);let q2=shell(ell(ax,y,z,.94,3.64,0,.46,.17,.42),.035);q2=smax(q2,-(y-3.78),.03);let q3=shell(ell(ax,y,z,.86,3.82,0,.34,.14,.32),.035);q3=smax(q3,-(y-3.95),.03);
  q=Math.min(q,q2,q3);for(let i=0;i<2;i++){const t=(i-.5)*.34;q=smin(q,cap(ax,y,z,1.1,3.86,t*.7,1.38+i*.04,4.12+.06*i,t*1.2,.095,.02),.025);}
  return Math.min(c,g,q);},
 trim:(x,y,z)=>{const ax=Math.abs(x);let d=Math.min(torus(x,y,z,0,3.66,0,.405,.022),torus(x,y,z,0,3.76,0,.345,.02));
  for(let i=0;i<9;i++){const a=(i/8-.5)*2.3;d=Math.min(d,ell(x,y,z,Math.sin(a)*.8,3.02-Math.abs(a)*.05,.03+Math.cos(a)*.5,.03,.03,.03));}
  for(let i=0;i<5;i++){const a=i/4*Math.PI*.7+.2;d=Math.min(d,ell(ax,y,z,.96+Math.cos(a)*.44,3.54+Math.sin(a)*.22,(i-2)*.18,.03,.03,.03));}return d;},
 cape:(x,y,z)=>{let co=shell(ell(x,y,z,0,3.78,-.3,.62,.62,.2),.03);co=smax(co,z+.08,.03);co=smax(co,y-(4.25+.2*Math.max(0,Math.sin(x*13))),.02);co=smax(co,-(y-3.1),.03);return co;}}};
// --- quadril: cinto + faldas ---
P.pelvis={bounds:[[-.65,-.75,-.5],[.65,.4,.55]],shift:[0,0,0],cell:.03,groups:{
 cloth:(x,y,z)=>{let d=ell(x,y,z,0,-.02,0,.5,.3,.34);d=smin(d,ell(x,y,z,0,-.3,-.02,.44,.3,.3),.08);return d;},
 plate:(x,y,z)=>{const ax=Math.abs(x);let d=shell(ell(x,y,z,0,.18,0,.5,.12,.38),.035);d=smax(d,-(y-.26),.03);
  for(const sg of[-1,1]){const px=x*sg;let t=shell(ell(px,y,z,.26,-.28,.2,.2,.42,.14),.03);t=smax(t,-(z+.02),.02);t=smax(t,y+.7,.02);d=Math.min(d,t);let t2=shell(ell(px,y,z,.5,-.2,.0,.1,.36,.26),.03);t2=smax(t2,y+.62,.02);d=Math.min(d,t2);}
  return d;},
 trim:(x,y,z)=>Math.min(torus(x,y,z,0,.18,0,.5,.02),torus(x,y,z,0,.07,0,.49,.018)),
 glow:(x,y,z)=>ell(x,y,z,0,.18,.43,.045,.06,.03)}};
// --- membros ---
function sleeve(x,y,z,L,r0,r1){return cap(x,y,z,0,0,0,0,L,0,r0,r1);}
P.uarm={bounds:[[-.4,-.1,-.45],[.4,1.0,.35]],cell:.028,groups:{
 cloth:(x,y,z)=>sleeve(x,y,z,.9,.15,.12),
 plate:(x,y,z)=>{let d=shell(cap(x,y,z,0,.15,0,0,.6,0,.19,.17),.035);d=smax(d,-(z+.1),.03);let e=shell(ell(x,y,z,0,.9,0,.2,.2,.19),.035);e=smax(e,-(y-.95)*0-(-(y-.92)),.03);d=Math.min(d,e);
  d=smin(d,cap(x,y,z,0,.92,-.12,0,1.0,-.38,.07,.012),.03);return d;},
 trim:(x,y,z)=>Math.min(torus(x,y-.15,z,0,0,0,.195,.02),torus(x,y-.6,z,0,0,0,.18,.02))}};
P.farm={bounds:[[-.4,-.1,-.35],[.4,1.15,.45]],cell:.028,groups:{
 cloth:(x,y,z)=>sleeve(x,y,z,.85,.12,.1),
 plate:(x,y,z)=>{let d=shell(cap(x,y,z,0,.08,0,0,.74,0,.15,.2),.035);d=smax(d,-(z+.08),.03);
  const f=ell(x,y,z,0,.9,.03,.13,.12,.12);let k=Math.min(f,ell(x,y,z,.0,.99,.09,.12,.05,.06));
  for(const i of[-1,0,1])k=smin(k,cap(x,y,z,i*.065,.95,.1,i*.065,1.0,.17,.04,.02),.03);k=smin(k,cap(x,y,z,.1,.86,.05,.14,.78,.14,.04,.03),.03);
  return Math.min(d,k);},
 trim:(x,y,z)=>Math.min(torus(x,y-.08,z,0,0,0,.16,.02),torus(x,y-.74,z,0,0,0,.2,.022))}};
P.thigh={bounds:[[-.4,-.1,-.4],[.4,1.1,.55]],cell:.03,groups:{
 cloth:(x,y,z)=>sleeve(x,y,z,.95,.18,.15),
 plate:(x,y,z)=>{let d=shell(cap(x,y,z,0,.1,0,0,.8,0,.22,.19),.035);d=smax(d,-(z+.04),.03);let k=shell(ell(x,y,z,0,.97,.06,.18,.17,.18),.035);k=smax(k,-(y-1.0)*0-(-(y-.95)),.03);d=Math.min(d,k);d=smin(d,cap(x,y,z,0,.97,.18,0,1.0,.44,.07,.012),.03);return d;},
 trim:(x,y,z)=>Math.min(torus(x,y-.1,z,0,0,0,.225,.02),torus(x,y-.8,z,0,0,0,.195,.02))}};
P.shin={bounds:[[-.4,-.1,-.4],[.4,1.1,.45]],cell:.03,groups:{
 cloth:(x,y,z)=>sleeve(x,y,z,.95,.15,.12),
 plate:(x,y,z)=>{let d=shell(cap(x,y,z,0,.08,0,0,.88,0,.19,.15),.035);d=smax(d,-(z+.05),.03);d=smin(d,cap(x,y,z,0,.1,.18,0,.8,.2,.025,.02),.03);return d;},
 trim:(x,y,z)=>Math.min(torus(x,y-.08,z,0,0,0,.195,.02),torus(x,y-.88,z,0,0,0,.155,.022))}};
P.boot={bounds:[[-.35,-.3,-.35],[.35,.25,.9]],cell:.028,groups:{   // origem no tornozelo, z+ = ponta
 cloth:(x,y,z)=>ell(x,y,z,0,-.04,.2,.15,.1,.3),
 plate:(x,y,z)=>{let d=shell(ell(x,y,z,0,-.06,.24,.17,.12,.38),.035);d=smax(d,y-.02+Math.max(0,z-.1)*.2,.03);d=smin(d,cap(x,y,z,0,-.1,.5,0,-.02,.82,.1,.015),.04);d=smin(d,ell(x,y,z,0,-.12,-.12,.13,.1,.1),.05);return d;},
 trim:(x,y,z)=>torus(x,y,z-.0,0,0,0,.15,.02)}};
// --- espada ---
P.blade={bounds:[[-.3,.1,-.1],[.3,2.9,.1]],cell:.02,groups:{
 blade:(x,y,z)=>{const t=clamp((y-1.9)/.85,0,1),w=.115*(1-t*t*.9)+.012,ax=Math.abs(x),th=(.032*(1-Math.pow(ax/Math.max(w,.001),2))+.008)*(1-.6*t)-.013*(ax<.028&&y>.4&&y<2.2?1:0);
  const prof=Math.max(ax-w,Math.abs(z)-Math.max(th,.004));return Math.max(prof,.18-y,y-2.78);}}};
P.hilt={bounds:[[-.6,-.8,-.2],[.6,.4,.2]],cell:.022,groups:{
 trim:(x,y,z)=>{const ax=Math.abs(x);let d=rbox(x,y,z,0,.18,0,.4,.05,.07,.02);d=smin(d,cap(ax,y,z,.38,.18,0,.55,.42,0,.06,.025),.03);d=smin(d,ell(x,y,z,0,.18,0,.12,.1,.1),.03);
  d=Math.min(d,ell(x,y,z,0,-.62,0,.11,.11,.11));for(let i=0;i<5;i++)d=Math.min(d,torus(x,y,z,0,-.05-i*.12,0,.075,.012));return d;},
 plate:(x,y,z)=>cap(x,y,z,0,-.55,0,0,.1,0,.065),
 glow:(x,y,z)=>ell(x,y,z,0,-.62,0,.06,.06,.06)}};
function mk(def){return buildGeo(def);}
