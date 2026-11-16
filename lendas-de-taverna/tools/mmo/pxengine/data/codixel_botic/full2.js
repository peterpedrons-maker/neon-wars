const D=require('./death2.js');const {P,render,shadow,body}=D;
const {A}=require('./anim.js');
const conv=p=>{const o={...p};if(p.armF!==undefined){const a=typeof p.armF==='object'?p.armF.a:p.armF;o.armFu={a:a*0.6};o.armFl={a:a*0.5};delete o.armF;}
 if(p.armB!==undefined){const a=typeof p.armB==='object'?p.armB.a:p.armB;o.armBu={a:a*0.6};o.armBl={a:a*0.5};delete o.armB;}
 if(p.tail!==undefined){const a=typeof p.tail==='object'?p.tail.a:p.tail;o.tailA={a:a*0.4};o.tailB={a:a};delete o.tail;}return o;};
const mk=(n,f)=>A[n](f).map(p=>render(conv(p),shadow(22)));
const anims={idle:mk('idle',12),walk:mk('walk',16),attack:mk('attack',10),cast:mk('cast',10),hurt:mk('hurt',7),death:D.frames};
module.exports={anims};
if(require.main===module){
 const spec=[['PARADO','idle'],['ANDAR','walk'],['ATAQUE','attack'],['CONJURAR','cast'],['DANO','hurt'],['MORTE','death']];
 const T=60,frames=[];
 for(let t=0;t<T;t++){
  const items=spec.map(([l,k])=>{const f=anims[k],n=f.length;let i=(k==='death'||k==='hurt')?Math.min(n-1,t%(n+10)):t%n;return{buf:f[i],label:l,scale:2};});
  frames.push(P.sheet(items,{cols:3,gap:6}));
 }
 require('fs').writeFileSync('/home/user/neon-wars/lendas-de-taverna/mmo/proto_pixel/boticario_animacoes.gif',Buffer.from(P.gif(frames,{delay:70,scale:1,loop:0})));
 const all=[];for(const [l,k] of spec)anims[k].forEach((b,i)=>all.push({buf:b,label:l+' '+i,scale:1}));
 P.save(P.sheet(all,{cols:10,gap:4}),'/home/user/neon-wars/lendas-de-taverna/mmo/proto_pixel/boticario_quadros.png');
 P.save(P.sheet(anims.death.map((b,i)=>({buf:b,label:'MORTE '+i,scale:2})),{cols:5,gap:4}),'/home/user/neon-wars/lendas-de-taverna/mmo/proto_pixel/boticario_morte.png');
 console.log('ok',frames[0].w,frames[0].h);
}
