const P=require(process.env.HOME+'/.claude/skills/codixel/core/pixel.js');
function sat(b,k){const o=new P.Buf(b.w,b.h);for(let i=0;i<b.px.length;i++){const c=b.px[i];if(((c>>>24)&255)<128)continue;const r=c&255,g=(c>>>8)&255,bl=(c>>>16)&255;const m=(r+g+bl)/3;const f=v=>Math.max(0,Math.min(255,Math.round(m+(v-m)*k)));o.px[i]=(255<<24|f(bl)<<16|f(g)<<8|f(r))>>>0;}return o;}
const ref=sat(P.trim(P.load('ref_idle.png'),0),1.3);
const rig=new P.Rig(ref)
 .bone('body',null,80,125,80,100,0)
 .bone('torso','body',80,112,80,62,0)
 .bone('tailA','body',45,138,15,128,-2)
 .bone('tailB','tailA',15,128,4,82,-2)
 .bone('legL','body',58,130,55,152,-1)
 .bone('legR','body',95,132,108,150,-1)
 .bone('head','torso',85,48,115,25,3)
 .bone('armFu','torso',50,64,33,80,1)
 .bone('armFl','armFu',33,80,22,38,2)
 .bone('armBu','torso',113,70,125,96,1)
 .bone('armBl','armBu',125,96,140,120,2)
 .bind({joint:2,paint:{
  torso:[[27,46],[118,46],[118,112],[27,112],[27,84]],
  body:[[27,92],[66,92],[66,112],[118,112],[118,140],[86,140],[70,136],[44,136],[27,128]],
  head:[[60,0],[149,0],[149,52],[100,52],[80,48],[60,40]],
  armFu:[[40,58],[58,58],[58,86],[40,86]],
  armFl:[[8,15],[42,15],[42,58],[40,86],[26,86],[8,62]],
  armBu:[[112,68],[132,68],[132,98],[112,98]],
  armBl:[[118,92],[149,92],[149,126],[118,126]],
  legL:[[42,134],[70,134],[70,153],[42,153]],
  legR:[[86,138],[130,138],[130,153],[86,153]],
  tailA:[[16,118],[26,128],[40,136],[48,148],[8,148],[16,132]],
  tailB:[[0,76],[24,76],[26,100],[20,116],[16,118],[16,132],[8,148],[0,120]]}});
module.exports={P,ref,rig};
if(require.main===module){const own=P.ruler(rig.ownerMap(),5,{step:10});rig.drawBones(own,0,0,{},{scale:5});P.save(P.sheet([own,rig.legend()]),'owners2.png');}
