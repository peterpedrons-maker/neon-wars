const {chromium}=require('playwright');
const CLS=process.argv[2]||'guerreiro',MIN=+(process.argv[3]||20),LV0=+(process.argv[4]||0),ZN=+(process.argv[5]||1),KIND=process.argv[6]||'med';
(async()=>{
 const b=await chromium.launch();const p=await b.newPage({viewport:{width:390,height:844}});
 const errs=[];p.on('pageerror',e=>errs.push(e.message));
 await p.goto('http://127.0.0.1:8760/hearthblade/index.html');await p.waitForFunction(()=>window.__mmo,null,{timeout:40000});
 await p.click('#bNew');await p.waitForTimeout(400);
 const idx=['guerreiro','ladino','mago','clerigo','arqueiro','bardo'].indexOf(CLS);
 await p.evaluate((c)=>{const el=document.querySelector('#cls button[data-k="'+c+'"]');if(el)el.click();},CLS);
 await p.click('#cNext');await p.click('#cNext');await p.fill('#cname','Sim');await p.click('#cNext');await p.waitForTimeout(3500);
 const out=await p.evaluate(([MIN,LV0,ZN,KIND])=>{
  const M=__mmo,G=M.G,S=M.SAVE;
  if(LV0){S.lv=LV0;const pts=3*(LV0-1);S.at={for:Math.round(pts*.4),vit:Math.round(pts*.4),res:Math.round(pts*.2),agi:0,sor:0};for(let i=0;i<8;i++)S.sk[i]=Math.min(5,1+Math.floor(LV0/8));S.eqs=[0,1,2];const kind=KIND,il=Math.round(LV0*(kind==='bis'?1.05:kind==='good'?1.0:.9));for(const sl of ['arma','elmo','armadura','botas','amuleto']){let it,k=0;const mr=kind==='bis'?3:kind==='good'?1:0;do{it=M.genItem(il,mr,kind==='bis'?60:kind==='good'?20:LV0*2);k++;}while(it.slot!==sl&&k<300);if(kind==='bis')it.up=10;else if(kind==='good')it.up=4;S.eq[sl]=it;}S.potions=5;}
  M.enterDungeon(ZN);
  return new Promise(res=>{
    // espera o fade
    setTimeout(()=>{
      G.on=true;const rows=[];let dmgSum=0,prevHp=G.hero.hp,deaths=0,lastKo=false,t=0,kills0=0,minHp=1,hpSum=0,hpN=0,pot0=S.potions;
      const dt=1/30;const step=()=>{
        const h=G.hero;
        for(let i=0;i<30*10;i++){ // 10s por bloco
          M.update(dt);t+=dt;
          if(h.state==='ko'&&!lastKo){deaths++;lastKo=true;}if(h.state!=='ko')lastKo=false;
          if(G.phase==='end'){G.phase='farm';G.boss=null;}
          if(G.boss&&G.phase==='boss'){}
          hpSum+=h.hp/h.maxhp;hpN++;if(h.hp<prevHp)dmgSum+=prevHp-h.hp;prevHp=h.hp;
          if(Math.floor(t)%1===0&&i%30===0){
            const pts=3*(S.lv-1)-Object.values(S.at).reduce((a,b)=>a+b,0);
            if(pts>0){const k=['for','vit','res','for','vit','agi'][(S.at.for+S.at.vit+S.at.res+S.at.agi)%6];S.at[k]++;}
            if(M.skPoints()>0){for(const i2 of [0,1,2,3,4,5,6,7]){if(M.skAvail(i2)&&S.sk[i2]<5){S.sk[i2]++;break;}}}
          }
        }
        const min=Math.round(t/60*10)/10;
        if(Math.round(t)%60===0)rows.push({min:Math.round(t/60),lv:S.lv,deaths,kills:G.kills,hp:Math.round(hpSum/hpN*100)+'%',lossPerKill:Math.round(dmgSum/Math.max(1,G.kills)/G.hero.maxhp*1000)/10,cycle:Math.round(t/Math.max(1,G.kills)*10)/10,mlv:Math.round(G.mobs.reduce((a,m)=>a+m.lv,0)/G.mobs.length),pot:S.potions,gold:S.gold,ph:G.phase});
        if(t>=MIN*60){res(rows);return;}
        setTimeout(step,0);
      };step();
    },3000);
  });
 },[MIN,LV0,ZN,KIND]);
 for(const r of out)console.log(JSON.stringify(r));
 console.log(errs.join('\n')||'ok');await b.close();})();
