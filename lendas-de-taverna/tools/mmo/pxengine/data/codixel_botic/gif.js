const {A,render,P}=require('./anim.js');
const spec=[['PARADO','idle',12],['ANDAR','walk',16],['ATAQUE','attack',10],['CONJURAR','cast',10],['DANO','hurt',7],['MORTE','death',11]];
const fr=spec.map(([l,k,n])=>({l,k,n,f:A[k](n).map(p=>render(p))}));
const T=48, frames=[];
for(let t=0;t<T;t++){
  const items=fr.map(({l,n,f,k})=>{let i=t%n; if(k==='death'||k==='hurt') i=Math.min(n-1,t%(n+8)); return {buf:f[Math.min(i,n-1)],label:l,scale:2};});
  frames.push(P.sheet(items,{cols:3,gap:6}));
}
require('fs').writeFileSync('/home/user/neon-wars/lendas-de-taverna/mmo/proto_pixel/boticario_animacoes.gif',Buffer.from(P.gif(frames,{delay:70,scale:1,loop:0})));
// folha numerada de todos os quadros
const all=[];for(const {l,f} of fr) f.forEach((b,i)=>all.push({buf:b,label:l+' '+i,scale:1}));
P.save(P.sheet(all,{cols:10,gap:4}),'/home/user/neon-wars/lendas-de-taverna/mmo/proto_pixel/boticario_quadros.png');
console.log(frames.length,'frames',frames[0].w,'x',frames[0].h);
