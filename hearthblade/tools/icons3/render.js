const {chromium}=require('playwright');const fs=require('fs');
(async()=>{
 const G=JSON.parse(fs.readFileSync('/tmp/ic/G.json'));const D=JSON.parse(fs.readFileSync('/tmp/gi/node_modules/@iconify-json/game-icons/icons.json')).icons;
 const b=await chromium.launch();const p=await b.newPage({viewport:{width:128,height:128},deviceScaleFactor:1});
 fs.mkdirSync('/tmp/ic/raw',{recursive:true});
 for(const [id,[g]] of Object.entries(G)){
  const body=D[g].body;
  await p.setContent(`<body style="margin:0;background:transparent"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="128" height="128" style="color:#fff;fill:#fff">${body}</svg></body>`);
  await p.screenshot({path:`/tmp/ic/raw/${id}.png`,omitBackground:true});
 }
 await b.close();console.log(Object.keys(G).length);})();
