const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch({args:['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
 const p=await b.newPage({viewport:{width:400,height:712}});p.on('pageerror',e=>console.log('PE',e.message));p.on('console',m=>{if(m.type()==='error')console.log(m.text())});
 await p.goto('http://127.0.0.1:8760/s25/scene.html');await p.waitForFunction(()=>window.READY,null,{timeout:60000});
 const times=process.argv.slice(2).map(Number);const step=+process.env.STEP||0;
 if(step){let i=0;for(let t=0;t<13600;t+=step){await p.evaluate(t=>step(t),t);await p.screenshot({path:`/tmp/s25/f/${String(i++).padStart(3,'0')}.png`})}console.log(i)}
 else for(const t of times){await p.evaluate(t=>step(t),t);await p.screenshot({path:`/tmp/s25/t${t}.png`})}
 await b.close();})();
