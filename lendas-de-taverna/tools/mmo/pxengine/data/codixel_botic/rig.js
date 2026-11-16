const P=require(process.env.HOME+'/.claude/skills/codixel/core/pixel.js');
function sat(b,k){const o=new P.Buf(b.w,b.h);for(let i=0;i<b.px.length;i++){const c=b.px[i];if(((c>>>24)&255)<128)continue;const r=c&255,g=(c>>>8)&255,bl=(c>>>16)&255;const m=(r+g+bl)/3;const f=v=>Math.max(0,Math.min(255,Math.round(m+(v-m)*k)));o.px[i]=(255<<24|f(bl)<<16|f(g)<<8|f(r))>>>0;}return o;}
const ref=sat(P.trim(P.load('ref_idle.png'),0),1.3);
const rig=new P.Rig(ref)
 .bone('body',null,80,125,80,70,0)
 .bone('tail','body',45,138,4,82,-1)
 .bone('legL','body',58,130,55,152,-1)
 .bone('legR','body',95,132,108,150,-1)
 .bone('head','body',85,45,115,25,2)
 .bone('armF','body',45,62,20,35,1)
 .bone('armB','body',113,70,140,118,1)
 .bind({joint:2,paint:{
  body:[[27,84],[118,84],[118,140],[86,140],[70,136],[44,136],[27,128]],
  head:[[60,0],[149,0],[149,52],[100,52],[80,48],[60,40]],
  armF:[[8,15],[42,15],[48,60],[48,80],[30,82],[8,60]],
  armB:[[112,68],[149,68],[149,126],[118,126],[110,100]],
  legL:[[42,134],[70,134],[70,153],[42,153]],
  legR:[[86,138],[130,138],[130,153],[86,153]],
  tail:[[0,76],[24,76],[26,100],[20,116],[26,128],[40,136],[48,148],[8,148],[0,120]]}});
module.exports={P,ref,rig};
if(require.main===module){
 const own=P.ruler(rig.ownerMap(),5,{step:10});rig.drawBones(own,0,0,{},{scale:5});
 P.save(P.sheet([own,rig.legend()]),'owners.png');
}
