const {chromium}=require('playwright');const fs=require('fs');
const URL='http://127.0.0.1:8760/lendas-de-taverna/mmo/index.html',D='/tmp/mt/trailer/';
const OV=`(()=>{const d=document.createElement('div');d.id='ov';d.innerHTML='<i class="lb t"></i><i class="lb b"></i><div class="tx"><b></b><span></span></div>';document.body.appendChild(d);const st=document.createElement('style');st.textContent='#ov{position:fixed;inset:0;pointer-events:none;z-index:99999}#ov .lb{position:absolute;left:0;right:0;height:11%;background:#000}#ov .t{top:0}#ov .b{bottom:0}#ov .tx{position:absolute;left:0;right:0;top:0;height:11%;display:flex;flex-direction:column;justify-content:center;text-align:center;opacity:0;padding:0 8px}#ov .tx b{display:block;font:700 19px var(--ft),serif;letter-spacing:.14em;color:#f6dc9a;text-shadow:0 2px 10px #000,0 0 18px rgba(240,180,60,.5)}#ov .tx span{display:block;margin-top:5px;font:600 9px var(--ft),serif;letter-spacing:.26em;color:#e8dcc0;text-shadow:0 2px 6px #000}#ov .tx.on{animation:ovi 3s ease both}#ov .tx.k{top:auto;bottom:0;animation:ovk 1.6s ease both}@keyframes ovi{0%{opacity:0;transform:translateY(8px)}16%{opacity:1;transform:none}82%{opacity:1}100%{opacity:0}}@keyframes ovk{0%{opacity:0}100%{opacity:1}}';document.head.appendChild(st);window.__ov=(a,b,k)=>{const t=d.querySelector('.tx');t.querySelector('b').textContent=a;t.querySelector('span').textContent=b||'';t.className='tx';void t.offsetWidth;t.className='tx '+(k?'k':'on');};})()`;
(async()=>{
 const b=await chromium.launch();
 {const c=await b.newContext({viewport:{width:390,height:844}});const p=await c.newPage();
  await p.goto(URL);await p.waitForFunction(()=>window.__mmo,null,{timeout:40000});
  await p.click('#bNew');await p.waitForTimeout(400);await p.click('#cNext');await p.click('#cNext');await p.fill('#cname','Aldric');await p.click('#cNext');await p.waitForTimeout(4500);
  await p.evaluate(()=>{const M=__mmo,S=M.SAVE;S.lv=45;S.sub='barbaro';S.sk=S.sk.map(()=>5);S.zoneMax=10;S.gold=48210;S.tok=37;S.pets={dourado:1,rubro:1,cinza:1};S.pet='dourado';S.mats={ferro:40,runa:60,cristal:25};S.potions=9;S.potL=4;
   const st=M.SETS[0];S.eq={};['elmo','armadura','luvas','botas','amuleto','anel'].forEach(sl=>{let it;do{it=M.genItem(24,3,0,null,st);}while(it.slot!==sl);it.up=6;S.eq[sl]=it;});
   let w;do{w=M.genItem(24,3,0);}while(w.slot!=='arma');w.wl='guerreiro';w.bn='Espada';w.name='Espada Basáltica';w.icon='i_espada';w.up=7;S.eq.arma=w;
   S.q.m=9;S.cnt={kill:1840,elite:64,boss:12,up:31,set:7};M.recalcHero(true);localStorage.setItem('hb_mmo_save_v1',JSON.stringify(S));});
  await p.waitForTimeout(800);await c.storageState({path:D+'state.json'});await c.close();}
 const T={};
 const scene=async(name,useState,fn)=>{
  const c=await b.newContext({viewport:{width:390,height:844},recordVideo:{dir:D+'v_'+name,size:{width:780,height:1688}},storageState:useState?D+'state.json':undefined});
  const t0=Date.now();const p=await c.newPage();p.on('pageerror',e=>console.log(name,'ERR',e.message));
  await p.goto(URL);await p.waitForFunction(()=>window.__mmo,null,{timeout:40000});await p.evaluate(OV);
  const s=Date.now();T[name]={ss:(s-t0)/1000};await fn(p);T[name].dur=(Date.now()-s)/1000-(T[name].skip||0);
  const v=p.video();await c.close();T[name].file=await v.path();console.log(name,JSON.stringify(T[name]));};
 const go=async p=>{await p.evaluate(()=>{setInterval(()=>{const h=__mmo.G.hero;if(h)h.hp=h.maxhp;},80);});};
 const cont=async(p,n)=>{await p.click('#bCont');await p.waitForTimeout(5200);T[n].ss+=5.2;T[n].skip=5.2;await go(p);};
 await scene('a',true,async p=>{await p.evaluate(()=>{const e=document.getElementById('bCont');if(e)e.style.display='none';});await p.waitForTimeout(700);await p.evaluate(()=>__ov('UMA LENDA DESPERTA','BRUMAVALE CHAMA'));await p.waitForTimeout(3800);});
 await scene('b',false,async p=>{await p.click('#bNew');await p.waitForTimeout(500);await p.evaluate(()=>__ov('SEIS CLASSES','DOZE SUBCLASSES'));
   const bs=await p.$$('#cls button');for(const x of bs){await x.click();await p.waitForTimeout(950);}});
 await scene('c',true,async p=>{await cont(p,'c');await p.evaluate(()=>__ov('BRUMAVALE','A CIDADE DOS HERÓIS'));await p.keyboard.down('w');await p.waitForTimeout(2600);await p.keyboard.up('w');await p.waitForTimeout(600);});
 await scene('d',true,async p=>{await cont(p,'d');await p.evaluate(()=>__mmo.enterDungeon(8));await p.waitForTimeout(1800);await p.evaluate(()=>{__ov('HABILIDADES DEVASTADORAS','ELITES · EVENTOS · HORDAS');__mmo.evStart();});await p.waitForTimeout(6500);});
 await scene('e',true,async p=>{await cont(p,'e');await p.evaluate(()=>__mmo.enterDungeon(6));await p.waitForTimeout(1500);await p.evaluate(()=>{__ov('CHEFES LENDÁRIOS','ENFRENTE O OGRO DE BRUMAVALE');__mmo.spawnBoss();});await p.waitForTimeout(6500);});
 await scene('f',true,async p=>{await cont(p,'f');await p.evaluate(()=>__ov('EQUIPAMENTOS · TALENTOS · PETS','UMA ÁRVORE DE POSSIBILIDADES'));
   await p.click('#bPs');await p.waitForTimeout(1300);await p.click('#tSk');await p.waitForTimeout(1300);await p.click('#tTl');await p.waitForTimeout(1300);await p.click('#pClose');await p.click('#bQ');await p.waitForTimeout(500);await p.click('[data-a="qt:p"]');await p.waitForTimeout(1500);});
 await scene('g',true,async p=>{await p.evaluate(()=>{const e=document.getElementById('bCont');if(e)e.style.display='none';});await p.waitForTimeout(500);await p.evaluate(()=>__ov('EM BREVE','HEARTHBLADE · LENDAS DE BRUMAVALE',true));await p.waitForTimeout(3800);});
 fs.writeFileSync(D+'T.json',JSON.stringify(T,null,1));await b.close();
})();
