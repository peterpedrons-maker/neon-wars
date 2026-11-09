// Luta de chefe com herói automático: node boss.js <classe> <zona> [perfil med|good|bis] [níveis acima do mínimo] [lutas]
// Imprime por luta: tempo até matar o chefe (s), mortes do herói, menor vida (%).  Servidor estático na raiz do repo (porta 8760).
const {chromium}=require('playwright');
const CLS=process.argv[2]||'guerreiro',ZN=+(process.argv[3]||1),KIND=process.argv[4]||'med',PLUS=+(process.argv[5]||2),N=+(process.argv[6]||4);
(async()=>{
 const b=await chromium.launch();const p=await b.newPage({viewport:{width:390,height:844}});
 const errs=[];p.on('pageerror',e=>errs.push(e.message));
 await p.goto('http://127.0.0.1:8760/lendas-de-taverna/mmo/index.html');await p.waitForFunction(()=>window.__mmo,null,{timeout:40000});
 await p.click('#bNew');await p.waitForTimeout(400);
 await p.evaluate((c)=>{const el=document.querySelector('#cls button[data-k="'+c+'"]');if(el)el.click();},CLS);
 await p.click('#cNext');await p.click('#cNext');await p.fill('#cname','Sim');await p.click('#cNext');await p.waitForTimeout(3500);
 await p.evaluate(([ZN,KIND,PLUS])=>{const M=__mmo,S=M.SAVE;
   const LV0=6+(ZN-1)*(M.BAL?M.BAL.zoneLv:4)+PLUS;S.lv=LV0;S.dgDone={1:true,2:true,3:true};const pts=3*(LV0-1);S.at={for:0,des:0,int:0,vit:Math.round(pts*.3),sor:0};S.at[M.MAIN_ATTR[S.cls]]=pts-S.at.vit;for(let i=0;i<8;i++)S.sk[i]=Math.min(5,1+Math.floor(LV0/8));S.eqs=[0,1,2];
   const il=Math.round(LV0*(KIND==='bis'?1.05:KIND==='good'?1.0:.9));
   for(const sl of ['arma','elmo','armadura','botas','amuleto']){let it,k=0;const mr=KIND==='bis'?3:KIND==='good'?1:0;do{it=M.genItem(il,mr,KIND==='bis'?60:KIND==='good'?20:LV0*2);k++;}while(it.slot!==sl&&k<300);if(KIND==='bis')it.up=10;else if(KIND==='good')it.up=4;S.eq[sl]=it;}S.potions=5;
   M.enterDungeon(ZN);},[ZN,KIND,PLUS]);
 await p.waitForTimeout(3000);if(process.env.DBG)await p.evaluate(()=>{window.DBG=1});
 const DBG=process.env.DBG;const out=await p.evaluate(([N,HPM,ATM])=>{const M=__mmo,G=M.G,S=M.SAVE,rows=[];const dt=1/30;
  for(let n=0;n<N;n++){
   G.on=true;G.auto=true;G.mobs=[];G.hero.hp=G.hero.maxhp;S.potions=5;if(G.hero.state==='ko')G.hero.state='idle';
   M.spawnBoss();const bs=G.boss;bs.maxhp=Math.round(bs.maxhp*HPM);bs.hp=bs.maxhp;bs.pow*=ATM;let t=0,deaths=0,ko=false,min=1;
   while(t<420&&!bs.dead&&bs.hp>0){M.update(dt);t+=dt;const h=G.hero;if(h.state==='ko'&&!ko){deaths++;ko=true;}if(h.state!=='ko')ko=false;min=Math.min(min,h.hp/h.maxhp);if(window.DBG&&Math.round(t*30)%150===0)rows.push({rng:h.rng,tg:h.tg&&h.tg.name,pow:Math.round(h.pow),cd:+h.cd.toFixed(2),act:!!h.act,sts:h.sts&&Object.keys(h.sts).join(),t:Math.round(t),hp:Math.round(h.hp),mh:h.maxhp,st:h.state,bhp:Math.round(bs.hp),bd:Math.round(Math.hypot(bs.x-h.x,bs.y-h.y)),ph:G.phase});if(G.phase==='end')break;}
   rows.push({boss:bs.name,blv:bs.lv,herolv:S.lv,pc:heroPC(),t:Math.round(t),killed:bs.hp<=0,bossHp:Math.round(bs.hp/bs.maxhp*100)+'%',deaths,minHp:Math.round(min*100)+'%'});
   G.phase='farm';G.boss=null;
  }return rows;},[N,+(process.env.HPM||1),+(process.env.ATM||1)]);
 for(const r of out)console.log(JSON.stringify(r));console.log(errs.join('\n')||'ok');await b.close();})();
