const {chromium}=require('playwright');const fs=require('fs');
(async()=>{const b=await chromium.launch({args:['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist']});const p=await b.newPage();p.on('pageerror',e=>console.log('PE',e.message));p.on('console',m=>console.log('C',m.text()));
await p.goto('file://'+__dirname+'/buildings.html');const o=await p.evaluate(()=>window.renderAll());
fs.mkdirSync('/tmp/b3/out',{recursive:true});const meta={};
for(const [id,v] of Object.entries(o)){fs.writeFileSync(`/tmp/b3/out/${id}.png`,Buffer.from(v.url.split(',')[1],'base64'));meta[id]={ax:v.ax,ay:v.ay};}
fs.writeFileSync('/tmp/b3/out/meta.json',JSON.stringify(meta));console.log(Object.keys(o).join(','));await b.close();})();
