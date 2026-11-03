/* Simulação de calibração (v2): herói com 8 espaços de equipamento, talentos, poções automáticas com economia (compra com o ouro) e subclasse livre.
   Uso: node sim2.js <classe> <minutos> <nível> <zona> <med|good|bis>   -> uma linha JSON no final */
const {chromium}=require('playwright');
const CLS=process.argv[2]||'guerreiro',MIN=+(process.argv[3]||4),LV0=+(process.argv[4]||1),ZN=+(process.argv[5]||1),KIND=process.argv[6]||'med',PORT=process.env.PORT||8760;
(async()=>{
 const b=await chromium.launch();const p=await b.newPage({viewport:{width:390,height:844}});
 const errs=[];p.on('pageerror',e=>errs.push(e.message));
 await p.goto('http://127.0.0.1:'+PORT+'/lendas-de-taverna/mmo/index.html');await p.waitForFunction(()=>window.__mmo,null,{timeout:60000});
 await p.click('#bNew');await p.waitForTimeout(400);
 await p.evaluate((c)=>{const el=document.querySelector('#cls button[data-k="'+c+'"]');if(el)el.click();},CLS);
 await p.click('#cNext');await p.click('#cNext');await p.fill('#cname','Sim');await p.click('#cNext');await p.waitForTimeout(3500);
 const out=await p.evaluate(([MIN,LV0,ZN,KIND])=>{
  const M=__mmo,G=M.G,S=M.SAVE;
  const alloc=()=>{ // talentos: ramo 1 inteiro, depois ramo 2
    const T=M.TALENTS[S.cls];S.tl={};let pts=M.tlTotal();
    for(const br of T){let go=true;while(go&&pts>0){go=false;let spent=br.nodes.reduce((a,n)=>a+(S.tl[n[0]]||0),0);
      for(let i=0;i<br.nodes.length&&pts>0;i++){const n=br.nodes[i],r=S.tl[n[0]]||0;if(r<n[2]&&spent>=M.TL_REQ[M.TL_TIER[i]]){S.tl[n[0]]=r+1;pts--;spent++;go=true;}}}}
    M.tfCalc();};
  const att=()=>{const pts=3*(S.lv-1)-Object.values(S.at).reduce((a,b)=>a+b,0);for(let i=0;i<pts;i++){const mk=M.MAIN_ATTR[S.cls];const k=(S.at.vit<(S.at[mk]||0)*.45)?'vit':mk;S.at[k]++;}};
  S.lv=LV0;S.at={for:0,des:0,int:0,vit:0,sor:0};att();
  for(let i=0;i<8;i++)S.sk[i]=Math.min(5,1+Math.floor(LV0/8));S.eqs=[0,1,2];
  const il=Math.round(LV0*(KIND==='bis'?1.05:KIND==='good'?1.0:.9)),mr=KIND==='bis'?3:KIND==='good'?1:0;
  for(const sl of M.SLOTS){let it,k=0;do{it=M.genItem(il,mr,KIND==='bis'?60:KIND==='good'?20:LV0*2);k++;}while(it.slot!==sl&&k<400);it.up=KIND==='bis'?7:KIND==='good'?4:2;S.eq[sl]=it;}
  alloc();S.potions=5;S.potL=0;S.gold=0;
  M.enterDungeon(ZN);
  return new Promise(res=>{
    setTimeout(()=>{
      M.recalcHero(false);G.on=true;let dmgSum=0,prevHp=G.hero.hp,deaths=0,lastKo=false,t=0,potUsed=0,pot0=S.potions+S.potL,kills0=G.kills;
      const dt=1/30;const step=()=>{
        const h=G.hero;
        for(let i=0;i<30*10;i++){
          M.update(dt);t+=dt;
          if(h.state==='ko'&&!lastKo){deaths++;lastKo=true;}
          if(h.state!=='ko')lastKo=false;
          if(G.phase==='end'||G.phase==='boss'){G.boss=null;G.phase='farm';G.bossRoll=1;G.dtm=0;}
          if(h.hp<prevHp)dmgSum+=prevHp-h.hp;prevHp=h.hp;
          if(i%30===0){if(!G.ev)G.evT=1e9;att();if(M.skPoints()>0){for(const i2 of [0,1,2,3,4,5,6,7]){if(M.skAvail(i2)&&S.sk[i2]<5){S.sk[i2]++;break;}}}
            // economia: recompra poções com o ouro (preço do alquimista), até 6
            while(S.potions<6&&S.gold>=M.potPrice()){S.gold-=M.potPrice();S.potions++;potUsed--;}}
        }
        if(t>=MIN*60){const k=G.kills-kills0,used=pot0-(S.potions+S.potL)+(0);
          res({cls:S.cls,L:LV0,z:ZN,kind:KIND,deaths,kills:k,loss:Math.round(dmgSum/Math.max(1,k)/h.maxhp*1000)/10,cycle:Math.round(t/Math.max(1,k)*10)/10,mlv:Math.round(G.mobs.reduce((a,m)=>a+m.lv,0)/G.mobs.length),pot:S.potions,gold:S.gold,elite:G.mobs.filter(m=>m.elite).length});return;}
        setTimeout(step,0);
      };step();
    },2500);
  });
 },[MIN,LV0,ZN,KIND]);
 console.log(JSON.stringify(out));if(errs.length)console.error(errs.join('\n'));await b.close();})();
