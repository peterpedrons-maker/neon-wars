// Laboratório de animação (uso do Claude): node lab.cjs <eval|improve|render> [animacao ...] [--from arquivo.json] [--out pasta]
// Carrega o estúdio num navegador sem tela, mede cada animação quadro a quadro, avalia e melhora sozinho.
const {chromium}=require('playwright');const fs=require('fs');const path=require('path');
const args=process.argv.slice(2);const cmd=args[0]||'eval';let from=null,out=path.join(__dirname,'out');const names=[];
for(let i=1;i<args.length;i++){if(args[i]==='--from')from=args[++i];else if(args[i]==='--out')out=args[++i];else names.push(args[i]);}
const ALL=['attack','forget','echo','rift','crown','dark','charge','hurt','death'];const list=names.length?names:ALL;
(async()=>{const b=await chromium.launch({args:['--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
const p=await b.newPage({viewport:{width:600,height:900}});const errs=[];p.on('pageerror',e=>errs.push(e.message));
await p.goto('http://localhost:8760/lendas-de-taverna/mmo/proto3d/estudio/studio_local.html');await p.waitForFunction("document.getElementById('load').hidden===true",{timeout:180000});
await p.evaluate(()=>{window.requestAnimationFrame=()=>0;});await p.waitForTimeout(300);
if(from){const j=JSON.parse(fs.readFileSync(from,'utf8'));await p.evaluate(a=>{for(const n in a)REI.ANIMS[n]=a[n];},j.a||j);}
fs.mkdirSync(out,{recursive:true});
const fmt=r=>{let s=`\n== ${r.nome}: nota ${r.score}/100\n   métricas: ${Object.entries(r.metricas).map(([k,v])=>k+'='+v).join('  ')}\n`;for(const q of r.problemas)s+=`   - [${q.t}s] ${q.tipo}: ${q.msg}\n`;if(!r.problemas.length)s+='   sem problemas medidos\n';return s;};
if(cmd==='eval'){for(const n of list){const r=await p.evaluate(n=>LAB.evaluate(n,REI.ANIMS[n]),n);console.log(fmt(r));}}
if(cmd==='improve'){const res={a:{}};for(const n of list){const r=await p.evaluate(n=>{const o=LAB.improve(n,REI.ANIMS[n]);return o;},n);res.a[n]=r.keys;console.log(`\n##### ${r.antes.nome}: ${r.antes.score} → ${r.depois.score}`);r.log.forEach(l=>console.log('   • '+l));console.log(fmt(r.depois));}
  fs.writeFileSync(path.join(out,'anims_melhoradas.json'),JSON.stringify(res));console.log('salvo em',path.join(out,'anims_melhoradas.json'));}
console.log(errs.slice(0,3).join('|')||'');await b.close();})();
