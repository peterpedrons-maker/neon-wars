const P=require(process.env.HOME+'/.claude/skills/codixel/core/pixel.js');
let ref=P.trim(P.load('ref_idle.png'),0);
function sat(b,k){const o=new P.Buf(b.w,b.h);for(let i=0;i<b.px.length;i++){const c=b.px[i];if(((c>>>24)&255)<128)continue;const r=c&255,g=(c>>>8)&255,bl=(c>>>16)&255;const m=(r+g+bl)/3;const f=v=>Math.max(0,Math.min(255,Math.round(m+(v-m)*k)));o.px[i]=(255<<24|f(bl)<<16|f(g)<<8|f(r))>>>0;}return o;}
const q=P.quantize(sat(ref,1.3),32,{dither:false});
let sm=P.resize(q.buf,Math.round(ref.w*64/ref.h),64,{mode:true});sm=P.smoothEdge(P.cleanup(sm,{tol:20}));
P.save(sm,'botic_64.png');
const atual=P.trim(P.load('atual.png'),0);
P.save(P.sheet([{buf:ref,label:'REFERENCIA (SUA ARTE)',scale:2},{buf:sm,label:'PIXEL ART 64PX (32 CORES)',scale:5},{buf:atual,label:'ATUAL NO JOGO',scale:3}],{cols:3,gap:14}),'/home/user/neon-wars/lendas-de-taverna/mmo/proto_pixel/boticario_referencia.png');
console.log(P.colorCount(sm).length,'cores',sm.w,'x',sm.h);
