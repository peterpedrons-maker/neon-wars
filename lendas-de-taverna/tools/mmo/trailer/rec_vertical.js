const {chromium}=require('playwright');const fs=require('fs');
const URL='http://127.0.0.1:8760/lendas-de-taverna/mmo/index.html',D='/tmp/mt/trailer3/';fs.mkdirSync(D,{recursive:true});
const W=720,H=1280;
const INIT=`(()=>{
 const st=document.createElement('style');st.textContent=\`
 #hud,#soc,#qtr,#itb,#mmenu,#bar,#chat,#banner,#joy,#toast,#sts,#buffs,#prog,#boss,#zone,#gold,#mm{display:none!important}
 #ov{position:fixed;inset:0;pointer-events:none;z-index:99999;overflow:hidden;font-family:var(--fd),serif}
 #ov .vg{position:absolute;inset:0;background:radial-gradient(ellipse at 50% 50%,transparent 52%,rgba(0,0,0,.55) 100%)}
 #ov .lb{position:absolute;left:0;right:0;height:6%;background:#000;z-index:3}#ov .t{top:0}#ov .b{bottom:0}
 #ov canvas{position:absolute;inset:0;mix-blend-mode:screen}
 #ov .fl{position:absolute;inset:0;background:#fff;opacity:0;z-index:2}
 #ov .hbw{position:absolute;left:0;right:0;top:33%;text-align:center;z-index:4;padding:0 4vw}
 #ov .hbt{display:inline-block;padding:.1em .12em .28em;font:700 9vw/1.05 var(--fd);letter-spacing:.08em;color:transparent;background:linear-gradient(105deg,transparent 38%,rgba(255,255,255,.95) 50%,transparent 62%),linear-gradient(180deg,#fff7d6 0%,#f6cf63 36%,#b9721d 62%,#ffe8a0 100%);background-size:260% 100%,100% 100%;background-position:160% 0,0 0;-webkit-background-clip:text;background-clip:text;filter:drop-shadow(0 5px 0 #3a1b04) drop-shadow(0 0 30px rgba(255,160,40,.65));animation:slam 3.3s cubic-bezier(.2,.8,.2,1) both,shine 1.5s .55s ease-out both}
 #ov .hbt.sm{font-size:6.6vw}
 #ov .hbs{margin-top:2vw;font:600 2.9vw var(--ft);letter-spacing:.3em;color:#f0e3c0;text-shadow:0 2px 10px #000,0 0 18px rgba(255,170,60,.45);animation:sub 3.3s ease both}
 #ov .hbl{height:3px;margin:16px auto;background:linear-gradient(90deg,transparent,#f6cf63,transparent);animation:ln 3.3s ease both}
 @keyframes slam{0%{opacity:0;transform:scale(1.7);letter-spacing:.34em;filter:blur(18px) drop-shadow(0 0 30px rgba(255,160,40,.65))}10%{opacity:1;transform:scale(.98);letter-spacing:.1em}16%{transform:scale(1)}86%{opacity:1;transform:scale(1.03)}100%{opacity:0;transform:scale(1.06)}}
 @keyframes shine{from{background-position:160% 0,0 0}to{background-position:-60% 0,0 0}}
 @keyframes sub{0%,12%{opacity:0;transform:translateY(14px)}28%{opacity:1;transform:none}86%{opacity:1}100%{opacity:0}}
 @keyframes ln{0%{width:0;opacity:0}14%{opacity:1}30%{width:62vw}86%{width:70vw;opacity:1}100%{width:80vw;opacity:0}}
 #ov .hbc{position:absolute;left:6%;bottom:12%;z-index:4;display:flex;align-items:center;gap:3.4vw;animation:cin 3.6s cubic-bezier(.2,.8,.2,1) both}
 #ov .hbc img{width:15vw;height:15vw;image-rendering:pixelated;filter:drop-shadow(0 0 22px rgba(255,190,70,.6))}
 #ov .hbc b{display:block;padding:.06em .1em .2em;font:700 9.4vw/1 var(--fd);letter-spacing:.1em;color:transparent;background:linear-gradient(180deg,#fff7d6 0%,#f6cf63 40%,#b9721d 70%,#ffe8a0 100%);-webkit-background-clip:text;background-clip:text;filter:drop-shadow(0 4px 0 #3a1b04) drop-shadow(0 0 22px rgba(255,160,40,.55))}
 #ov .hbc span{display:block;margin-top:1.4vw;font:600 2.7vw var(--ft);letter-spacing:.22em;color:#f0e3c0;text-shadow:0 2px 10px #000}
 @keyframes cin{0%{opacity:0;transform:translateX(-90px)}12%{opacity:1;transform:none}86%{opacity:1}100%{opacity:0;transform:translateX(30px)}}
 #ov .blk{position:absolute;inset:0;background:#000;z-index:1}
 #ov .big{position:absolute;left:0;right:0;top:30%;text-align:center;z-index:4}
 \`;document.head.appendChild(st);
 window.resizeCanvas=function(){const s=document.getElementById('stage'),cv=document.getElementById('cv');cv.width=s.clientWidth;cv.height=s.clientHeight;G.K=3;G.LW=Math.ceil(cv.width/3);G.LH=Math.ceil(cv.height/3);};
 window.fitStage=function(){document.getElementById('stage').style.width=innerWidth+'px';resizeCanvas();};
 fitStage();
 const ov=document.createElement('div');ov.id='ov';ov.innerHTML='<div class="vg"></div><canvas></canvas><div class="fl"></div><i class="lb t"></i><i class="lb b"></i>';document.body.appendChild(ov);
 const c=ov.querySelector('canvas');c.width=innerWidth;c.height=innerHeight;const x=c.getContext('2d');
 const P=Array.from({length:90},()=>({x:Math.random()*innerWidth,y:Math.random()*innerHeight,r:1+Math.random()*3,v:20+Math.random()*60,s:Math.random()*6,a:.3+Math.random()*.7}));
 let last=performance.now();(function f(n){const dt=Math.min(.05,(n-last)/1000);last=n;x.clearRect(0,0,c.width,c.height);x.globalCompositeOperation='lighter';
  for(const p of P){p.y-=p.v*dt;p.x+=Math.sin(n/700+p.s)*14*dt;if(p.y<-10){p.y=innerHeight+10;p.x=Math.random()*innerWidth;}
   const a=p.a*(.6+.4*Math.sin(n/160+p.s)),g=x.createRadialGradient(p.x,p.y,0,p.x,p.y,p.r*4);g.addColorStop(0,'rgba(255,190,80,'+a+')');g.addColorStop(1,'rgba(255,90,20,0)');x.fillStyle=g;x.beginPath();x.arc(p.x,p.y,p.r*4,0,7);x.fill();}
  requestAnimationFrame(f);})(last);
 const flash=()=>{ov.querySelector('.fl').animate([{opacity:.6},{opacity:0}],{duration:520,easing:'ease-out'});};
 const shake=()=>{document.body.animate([{transform:'translate(0,0)'},{transform:'translate(-14px,8px)'},{transform:'translate(12px,-10px)'},{transform:'translate(-8px,6px)'},{transform:'translate(5px,-3px)'},{transform:'translate(0,0)'}],{duration:520,easing:'ease-out'});};
 window.__T=(a,b,sm)=>{const e=document.createElement('div');e.className='hbw';e.innerHTML='<div class="hbl"></div><div class="hbt'+(sm?' sm':'')+'">'+a.replace('|','<br>')+'</div><div class="hbs">'+(b||'')+'</div><div class="hbl"></div>';ov.appendChild(e);flash();shake();setTimeout(()=>e.remove(),3500);};
 window.__CARD=(cls,a,b)=>{const e=document.createElement('div');e.className='hbc';e.innerHTML='<img src="assets/class/'+cls+'.png"><div><b>'+a+'</b><span>'+b+'</span></div>';ov.appendChild(e);flash();setTimeout(()=>e.remove(),3700);};
 window.__BLACK=(on)=>{let b=ov.querySelector('.blk');if(on&&!b){b=document.createElement('div');b.className='blk';ov.insertBefore(b,ov.firstChild);}if(!on&&b)b.remove();};
})()`;
const CLS=[['guerreiro','GUERREIRO','A MURALHA DE AÇO',3],['ladino','LADINO','LÂMINA NAS SOMBRAS',5],['mago','MAGO','SENHOR DAS TEMPESTADES',6],['clerigo','CLÉRIGO','A LUZ SAGRADA',8],['arqueiro','ARQUEIRO','OLHAR DE FALCÃO',2],['bardo','BARDO','A CANÇÃO DA GUERRA',7]];
(async()=>{
 const b=await chromium.launch();
 for(const [c] of CLS)fs.copyFileSync('/tmp/mt/trailer2/st_'+c+'.json',D+'st_'+c+'.json');
 const T={};
 const scene=async(name,state,fn)=>{
  const c=await b.newContext({viewport:{width:W,height:H},storageState:state?D+'st_'+state+'.json':undefined});
  const p=await c.newPage();p.on('pageerror',e=>console.log(name,'ERR',e.message));
  await p.goto(URL);await p.waitForFunction(()=>window.__mmo,null,{timeout:40000});await p.evaluate(INIT);
  const cdp=await c.newCDPSession(p),frames=[];
  cdp.on('Page.screencastFrame',f=>{frames.push([f.metadata.timestamp,f.data]);cdp.send('Page.screencastFrameAck',{sessionId:f.sessionId}).catch(()=>{});});
  await cdp.send('Page.startScreencast',{format:'jpeg',quality:90,maxWidth:W,maxHeight:H,everyNthFrame:1});
  T[name]={ss:0,ev:[]};let s=Date.now();const mark=l=>T[name].ev.push([l,(Date.now()-s)/1000]);
  const sync=()=>{s=Date.now();T[name].ss=s/1000;};sync();
  await fn(p,sync,mark);T[name].dur=(Date.now()-s)/1000;T[name].end=Date.now()/1000;
  await cdp.send('Page.stopScreencast');await c.close();
  const dir=D+'f_'+name+'/';fs.mkdirSync(dir,{recursive:true});const list=[];
  frames.forEach((f,i)=>{const fn2=dir+String(i).padStart(5,'0')+'.jpg';fs.writeFileSync(fn2,Buffer.from(f[1],'base64'));list.push([f[0],fn2]);});
  T[name].frames=list;const inw=list.filter(x=>x[0]>=T[name].ss&&x[0]<=T[name].end).length;
  console.log(name,'frames',list.length,'na janela',inw,'fps',(inw/T[name].dur).toFixed(1),'dur',T[name].dur.toFixed(1));};
 const inv=p=>p.evaluate(()=>{setInterval(()=>{const h=__mmo.G.hero;if(h)h.hp=h.maxhp;},80);});
 // título
 await scene('a',null,async(p,sync,mark)=>{await p.evaluate(()=>{document.getElementById('bNew')&&0;__BLACK(true);});sync();await p.waitForTimeout(500);mark('title');await p.evaluate(()=>{__T('HEARTHBLADE','LENDAS DE BRUMAVALE');});await p.waitForTimeout(3600);});
 // cidade
 await scene('b','guerreiro',async(p,sync,mark)=>{await p.evaluate(()=>__BLACK(true));await p.click('#bCont');await p.waitForTimeout(5200);await inv(p);sync();await p.evaluate(()=>__BLACK(false));mark('town');await p.evaluate(()=>__T('BRUMAVALE','ONDE TODA LENDA COMEÇA'));await p.keyboard.down('w');await p.waitForTimeout(2600);await p.keyboard.up('w');await p.waitForTimeout(1600);});
 // classes
 for(const [cls,nm,ep,z] of CLS){
  await scene('c_'+cls,cls,async(p,sync,mark)=>{await p.evaluate(()=>__BLACK(true));await p.click('#bCont');await p.waitForTimeout(5200);await inv(p);await p.evaluate(z=>__mmo.enterDungeon(z),z);await p.waitForTimeout(1800);sync();await p.evaluate(()=>__BLACK(false));mark('card');await p.evaluate(([c,n,e])=>__CARD(c,n,e),[cls,nm,ep]);await p.waitForTimeout(3600);});
 }
 // chefe
 await scene('d','guerreiro',async(p,sync,mark)=>{await p.evaluate(()=>__BLACK(true));await p.click('#bCont');await p.waitForTimeout(5200);await inv(p);await p.evaluate(()=>__mmo.enterDungeon(6));await p.waitForTimeout(1800);sync();await p.evaluate(()=>__BLACK(false));await p.waitForTimeout(900);mark('boss');await p.evaluate(()=>{__T('CHEFES|LENDÁRIOS','ENFRENTE O OGRO DE BRUMAVALE');__mmo.spawnBoss();});await p.waitForTimeout(6500);});
 // horda
 await scene('e','mago',async(p,sync,mark)=>{await p.evaluate(()=>__BLACK(true));await p.click('#bCont');await p.waitForTimeout(5200);await inv(p);await p.evaluate(()=>__mmo.enterDungeon(5));await p.waitForTimeout(1500);sync();await p.evaluate(()=>__BLACK(false));mark('horde');await p.evaluate(()=>{__mmo.evStart();__T('HORDAS · ELITES|EVENTOS','NENHUMA BATALHA É IGUAL',true);});await p.waitForTimeout(4600);});
 // fim
 await scene('f',null,async(p,sync,mark)=>{await p.evaluate(()=>__BLACK(true));sync();await p.waitForTimeout(400);mark('end');await p.evaluate(()=>{__T('EM BREVE','HEARTHBLADE · LENDAS DE BRUMAVALE');});await p.waitForTimeout(3600);});
 fs.writeFileSync(D+'T.json',JSON.stringify(T,null,1));await b.close();
})();
