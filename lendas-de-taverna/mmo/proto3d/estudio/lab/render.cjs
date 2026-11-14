// Compara antes/depois: node render.cjs <animacao> [--from out/anims_melhoradas.json] [--gif saida.gif]
const {chromium}=require('playwright');const fs=require('fs');const path=require('path');
const a=process.argv.slice(2);const name=a[0]||'attack';let from=path.join(__dirname,'out','anims_melhoradas.json'),gif=path.join(__dirname,'out',name+'_antes_depois.gif');
for(let i=1;i<a.length;i++){if(a[i]==='--from')from=a[++i];else if(a[i]==='--gif')gif=a[++i];}
(async()=>{const b=await chromium.launch({args:['--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
const p=await b.newPage({viewport:{width:600,height:900}});
await p.goto('http://localhost:8760/lendas-de-taverna/mmo/proto3d/estudio/studio_local.html');await p.waitForFunction("document.getElementById('load').hidden===true",{timeout:180000});
await p.evaluate(()=>{window.requestAnimationFrame=()=>0;});await p.waitForTimeout(300);
const novo=JSON.parse(fs.readFileSync(from,'utf8')).a[name];
const tmp=fs.mkdtempSync('/tmp/rd_');const res={};
for(const [lbl,keys] of [['A',null],['B',novo]]){
  const info=await p.evaluate(([n,k])=>{if(k)REI.ANIMS[n]=k;REI.reset();window.NORENDER=false;return {dur:REI.ANIMS[n][REI.ANIMS[n].length-1][0],score:LAB.evaluate(n,REI.ANIMS[n]).score};},[name,keys]);
  res[lbl]=info;const N=Math.round(info.dur*30);
  for(let i=0;i<N;i++){const d=await p.evaluate(([n,t])=>{sim.step(1/30,n==='death'?{move:0,yawTo:Math.PI/2,dead:Math.max(.0001,t)}:{move:0,anim:n,at:t,yawTo:Math.PI/2});return sim.grab()},[name,i/30]);fs.writeFileSync(`${tmp}/${lbl}${String(i).padStart(4,'0')}.png`,Buffer.from(d.split(',')[1],'base64'));}
  await p.evaluate(n=>{},name);
}
fs.writeFileSync(path.join(tmp,'info.json'),JSON.stringify(res));console.log(tmp);await b.close();})();
