// Calibração do poder de combate (PC) recomendado por dungeon.
// Para cada dungeon, classe e perfil de equipamento (med/good/bis), monta o herói no nível do chefe e mede o PC.
// Uso: node pc_calib.cjs   (servidor estático na raiz do repo, porta 8760)
const {chromium}=require('playwright');
const CLS=['guerreiro','ladino','mago','clerigo','arqueiro','bardo'],KINDS=['med','good','bis'];
(async()=>{const b=await chromium.launch();const res={};
 for(const cls of CLS){const p=await b.newPage({viewport:{width:390,height:844}});
  await p.goto('http://127.0.0.1:8760/lendas-de-taverna/mmo/index.html');await p.waitForFunction(()=>window.__mmo,null,{timeout:40000});
  await p.click('#bNew');await p.waitForTimeout(400);await p.evaluate((c)=>{const el=document.querySelector('#cls button[data-k="'+c+'"]');if(el)el.click();},cls);
  await p.click('#cNext');await p.click('#cNext');await p.fill('#cname','Sim');await p.click('#cNext');await p.waitForTimeout(3500);
  const r=await p.evaluate(()=>{const M=__mmo,S=M.SAVE,out={};
   for(const Z of [1,2,3,4]){const LV0=M.BAL.zoneLv*(Z-1)+8;out[Z]={};   // nível do chefe
    for(const KIND of ['med','good','bis']){S.lv=LV0;const pts=3*(LV0-1);S.at={for:0,des:0,int:0,vit:Math.round(pts*.3),sor:0};S.at[M.MAIN_ATTR[S.cls]]=pts-S.at.vit;for(let i=0;i<8;i++)S.sk[i]=Math.min(5,1+Math.floor(LV0/8));S.eqs=[0,1,2];S.eq={};
     const il=Math.round(LV0*(KIND==='bis'?1.05:KIND==='good'?1.0:.9));
     for(const sl of ['arma','elmo','armadura','botas','amuleto','luvas','anel']){let it,k=0;const mr=KIND==='bis'?3:KIND==='good'?1:0;do{it=M.genItem(il,mr,KIND==='bis'?60:KIND==='good'?20:LV0*2);k++;}while(it.slot!==sl&&k<400);if(KIND==='bis')it.up=10;else if(KIND==='good')it.up=4;S.eq[sl]=it;}
     recalcHero(true);out[Z][KIND]=heroPC();}}
   return out;});
  res[cls]=r;await p.close();}
 const rows={};for(const Z of [1,2,3,4]){rows[Z]={};for(const K of KINDS){const v=CLS.map(c=>res[c][Z][K]);rows[Z][K]={media:Math.round(v.reduce((a,b)=>a+b,0)/v.length),min:Math.min(...v),max:Math.max(...v)};}}
 console.log(JSON.stringify(rows));console.log(JSON.stringify(res));await b.close();})();
