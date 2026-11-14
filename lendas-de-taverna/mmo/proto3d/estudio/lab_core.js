// ===== Laboratório de animação: mede, avalia e melhora sozinho (usado pelo Claude e pelo botão "Avaliar") =====
const LAB=(function(){
const V3=THREE.Vector3,DT=1/30,TOR=1.75,LEG=1.9;
const NOME={attack:'Golpe',forget:'Esquecimento',echo:'Eco',rift:'Fenda do Vazio',crown:'Coroa de Almas',dark:'Trevas',charge:'Investida',hurt:'Dano',death:'Morte'};
const DUR={attack:[1.2,2.8],forget:[1.2,2.4],echo:[1.6,3],rift:[1.4,2.8],crown:[1.8,3.2],dark:[2,3.4],charge:[2,3.4],hurt:[.5,1.1],death:[2,3.6]};
const FORTE={attack:1,rift:1,echo:1,charge:1,hurt:0,death:0,forget:0,crown:0,dark:0};   // tem golpe com antecipação e impacto
const clone=k=>k.map(([t,p])=>[t,{...p}]);
const arr=v=>[v.x,v.y,v.z];
function measure(name,keys){
  const old=ANIMS[name];ANIMS[name]=keys;window.NORENDER=true;resetRig();
  const dur=keys[keys.length-1][0],N=Math.ceil(dur/DT)+1,F=[];
  try{
    for(let i=0;i<24;i++)step(DT,{move:0,anim:'',yawTo:Math.PI/2});
    resetRig();for(let i=0;i<6;i++)step(DT,{move:0,anim:'',yawTo:Math.PI/2});
    for(let i=0;i<N;i++){const at=Math.min(dur,i*DT),cmd=name==='death'?{move:0,yawTo:Math.PI/2,dead:Math.max(.0001,at)}:{move:0,anim:name,at,yawTo:Math.PI/2};
      step(DT,cmd);
      const g=sword.localToWorld(new V3(0,-.12,0)),tp=new V3(),hd=new V3(),ch=new V3(),bd=new V3();tip.getWorldPosition(tp);head.getWorldPosition(hd);chest.getWorldPosition(ch);body.getWorldPosition(bd);
      const lhm=[armSeg[0].hg,armSeg[0].ho,armSeg[0].hr].find(m=>m.visible)||armSeg[0].hr,lh=lhm.position.clone();
      const shR=chest.localToWorld(new V3(.8,.55,0)),shL=chest.localToWorld(new V3(-.8,.55,0));
      const hipL=legSeg[0].th.position,hipR=legSeg[1].th.position,fL=legSeg[0].ft.position,fR=legSeg[1].ft.position;
      F.push({t:at,rh:arr(g),tip:arr(tp),lh:arr(lh),head:arr(hd),chest:arr(ch),hips:arr(bd),fl:arr(fL),fr:arr(fR),
        reachR:g.distanceTo(shR)/TOR,reachL:lh.distanceTo(shL)/TOR,legL:hipL.distanceTo(fL)/LEG,legR:hipR.distanceTo(fR)/LEG,pose:spline(keys,at)});}
  }finally{ANIMS[name]=old;window.NORENDER=false;resetRig();}
  return F;}
const sub=(a,b)=>[a[0]-b[0],a[1]-b[1],a[2]-b[2]],len=a=>Math.hypot(a[0],a[1],a[2]),dot=(a,b)=>a[0]*b[0]+a[1]*b[1]+a[2]*b[2],mul=(a,k)=>[a[0]*k,a[1]*k,a[2]*k];
function ptSeg(p,a,b){const ab=sub(b,a),t=Math.max(0,Math.min(1,dot(sub(p,a),ab)/(dot(ab,ab)||1)));return len(sub(p,[a[0]+ab[0]*t,a[1]+ab[1]*t,a[2]+ab[2]*t]));}
function energia(F){let e=0;for(const k of ['tip','rh','head','hips','lh']){for(let i=1;i<F.length;i++)e+=len(sub(F[i][k],F[i-1][k]));}return e;}
function evaluate(name,keys,F,ref){
  F=F||measure(name,keys);const n=F.length,I=[],M={};let pen=0;
  const add=(tipo,t,msg,w)=>{I.push({tipo,t:+t.toFixed(2),msg});pen+=w;};
  // 1. saltos de velocidade (trancos) na mão da espada, na ponta e na cabeça
  const vel=(k)=>F.map((f,i)=>i?mul(sub(f[k],F[i-1][k]),1/DT):[0,0,0]);
  let tr=0;for(const [k,nm] of [['rh','mão direita'],['tip','ponta da espada'],['head','cabeça'],['hips','quadril']]){const v=vel(k),sp=v.map(len),mx=Math.max(...sp,1);
    for(let i=2;i<n;i++){const jump=len(sub(v[i],v[i-1]))/mx;if(jump>.5&&len(sub(v[i],v[i-1]))>2.5){tr++;if(tr<=6)add('tranco',F[i].t,'tranco na '+nm+' (muda de velocidade de uma vez)',5);}}}
  M.trancos=tr;
  // 2. alcance dos braços e das pernas (peça solta do corpo)
  const rr=F.filter(f=>f.reachR>1.15||f.reachL>1.15),lg=F.filter(f=>f.legL>1.0||f.legR>1.0);M.alcance_braco=+(rr.length/n*100).toFixed(1);M.perna_esticada=+(lg.length/n*100).toFixed(1);
  if(rr.length)add('alcance',rr[0].t,'o braço não alcança onde a mão/espada deveria estar ('+rr.length+' quadros): mão se solta do corpo',Math.min(25,rr.length/n*60));
  if(lg.length)add('perna',lg[0].t,'a perna estica além do limite ('+lg.length+' quadros): pé flutua',Math.min(15,lg.length/n*40));
  // 3. espada atravessando o corpo / chão
  let inter=0,firstI=-1,under=0;F.forEach((f,i)=>{let md=9;for(let s=.15;s<=1;s+=.1){const p=[f.rh[0]+(f.tip[0]-f.rh[0])*s,f.rh[1]+(f.tip[1]-f.rh[1])*s,f.rh[2]+(f.tip[2]-f.rh[2])*s];md=Math.min(md,ptSeg(p,f.hips,f.chest));}if(md<.3){inter++;if(firstI<0)firstI=i;}if(f.tip[1]<-.12)under++;});
  M.espada_no_corpo=inter;if(inter>3)add('colisao',F[firstI].t,'a lâmina atravessa o tronco ('+inter+' quadros)',Math.min(15,inter*.8));
  if(under>2)add('chao',F.find(f=>f.tip[1]<-.12).t,'a ponta da espada entra no chão',Math.min(10,under));
  // 4. pés: deslize enquanto apoiados
  let slide=0,maxs=0;for(const k of ['fl','fr']){for(let i=1;i<n;i++){const a=F[i-1][k],b=F[i][k];if(a[1]<.27&&b[1]<.27){const d=Math.hypot(b[0]-a[0],b[2]-a[2]);slide+=d;maxs=Math.max(maxs,d);}}}
  M.deslize_pes=+slide.toFixed(2);if(maxs>.09)add('deslize',F[0].t,'o pé desliza no chão (até '+maxs.toFixed(2)+' por quadro)',Math.min(12,maxs*60));
  // 5. antecipação, impacto e continuação do movimento (só para animações com golpe)
  const forte=FORTE[name];let ant=null,fol=null,snap=null;
  if(forte){const v=vel('rh').map(len);let pk=0;v.forEach((x,i)=>{if(x>v[pk])pk=i;});const a0=Math.max(0,pk-6),a1=Math.min(n-1,pk+6),d=sub(F[a1].rh,F[a0].rh),dl=len(d)||1,dn=mul(d,1/dl);
    let best=0;for(let i=Math.max(0,pk-24);i<pk-2;i++){best=Math.max(best,-dot(sub(F[i].rh,F[pk-3].rh),dn)*-1*-1);}
    // quanto a mão recuou (contra o golpe) antes de disparar
    let back=0;for(let i=Math.max(0,pk-30);i<pk-1;i++){back=Math.max(back,dot(sub(F[pk-3].rh,F[i].rh),dn)*-1);}
    back=Math.max(0,back);ant=Math.min(1,back/.55);
    let over=0;const fin=F[n-1].rh;for(let i=pk+3;i<n;i++)over=Math.max(over,dot(sub(F[i].rh,F[Math.min(n-1,pk+3)].rh),dn));fol=Math.min(1,over/.5);
    const act=v.filter(x=>x>.5),meanv=act.reduce((s,x)=>s+x,0)/(act.length||1);snap=v[pk]/(meanv||1);
    M.antecipacao=+ant.toFixed(2);M.continuacao=+fol.toFixed(2);M.explosao=+snap.toFixed(2);M.pico_vel=+v[pk].toFixed(1);M.t_impacto=+F[pk].t.toFixed(2);
    if(ant<.5)add('antecipacao',F[Math.max(0,pk-8)].t,'falta preparação antes do golpe: a mão quase não recua (antecipação '+Math.round(ant*100)+'%)',10*(1-ant/.5)+2);
    if(fol<.4)add('continuacao',F[pk].t,'o golpe para seco no impacto: falta a espada passar do alvo e voltar',8*(1-fol/.4)+1);
    if(snap<1.9)add('explosao',F[pk].t,'o golpe é lento e uniforme: falta acelerar de repente no impacto',8*(1-snap/1.9)+2);
    const dips=F.map(f=>f.pose.dip),dmax=Math.max(...dips);M.agachar_max=+dmax.toFixed(2);if(dmax<.12)add('peso',F[pk].t,'falta peso: o corpo quase não afunda no golpe',6);}
  // 6. higiene das poses
  const kt=keys.map(k=>k[0]);let gap=9,gi=0;for(let i=1;i<kt.length;i++)if(kt[i]-kt[i-1]<gap){gap=kt[i]-kt[i-1];gi=i;}M.menor_intervalo=+gap.toFixed(2);if(gap<.12)add('colada',kt[gi],'duas poses coladas ('+gap.toFixed(2)+' s)',8);
  // 7. começo e fim no repouso (menos morte/dano) e duração
  const p0=keys[0][1],p1=keys[keys.length-1][1];let dif=0;for(const c of ['lean','twist','dip','lunge','back','hx','hy','sx','sy','sz','rx','lx','ly','lz','lm'])dif=Math.max(dif,Math.abs(p0[c]-p1[c]));
  M.fecha_no_repouso=+dif.toFixed(2);if(name!=='death'&&dif>.08)add('repouso',kt[kt.length-1],'o fim da animação não volta à pose de repouso (diferença '+dif.toFixed(2)+')',8);
  const dr=DUR[name],dur=kt[kt.length-1];M.duracao=+dur.toFixed(2);if(dr&&(dur<dr[0]||dur>dr[1]))add('duracao',dur,'duração fora do ideal ('+dur.toFixed(1)+'s; o ideal é '+dr[0]+' a '+dr[1]+'s)',5);
  // 8. expressividade: não vale deixar o movimento murcho só para fugir dos problemas
  const en=energia(F);M.energia=+en.toFixed(1);if(ref){const r=en/ref.en;M.energia_vs_original=+r.toFixed(2);if(forte&&M.pico_vel&&ref&&ref.pk&&M.pico_vel<ref.pk*.85)add('fraco',F[Math.floor(n/2)].t,'o golpe ficou mais fraco que o original (pico de velocidade '+M.pico_vel+' contra '+ref.pk.toFixed(1)+')',Math.min(15,(1-M.pico_vel/(ref.pk*.85))*40));
  if(r<.8)add('murcho',F[Math.floor(n/2)].t,'o movimento ficou menor que o original ('+Math.round(r*100)+'% da energia): perdeu expressão',Math.min(30,(1-r/.8)*45));}
  return {nome:NOME[name]||name,score:Math.max(0,Math.round((100-pen)*10)/10),metricas:M,problemas:I.sort((a,b)=>(a.t||0)-(b.t||0))};}
// ---------- melhora sozinho ----------
const CH_MOV=['lean','twist','sx','sy','sz','rx','ry','lunge','lx','ly','lz'];
function sortKeys(k){k.sort((a,b)=>a[0]-b[0]);return k;}
function tHygiene(k0,name){const k=clone(k0);for(let i=k.length-2;i>=1;i--)if(k[i+1][0]-k[i][0]<.14)k.splice(i,1);
  if(name!=='death'){const b=k[0][1],e=k[k.length-1][1];for(const c of Object.keys(e))e[c]=b[c];}return k;}
function tReach(k0,F,f){const k=clone(k0),rest=k[0][1];const bad=F.filter(x=>x.reachR>1.15||x.reachL>1.15);if(!bad.length)return k;
  const idx=new Set(bad.map(x=>{let b=0,bd=9;k.forEach(([t],i)=>{const d=Math.abs(t-x.t);if(d<bd){bd=d;b=i;}});return b;}));
  idx.forEach(i=>{if(i===0||i===k.length-1)return;const p=k[i][1];for(const c of ['sx','sy','sz','lx','ly','lz'])p[c]=rest[c]+(p[c]-rest[c])*f;});return k;}
function tLeg(k0,F,f){const k=clone(k0),bad=F.filter(x=>x.legL>1.0||x.legR>1.0);if(!bad.length)return k;
  new Set(bad.map(x=>{let b=0,bd=9;k.forEach(([t],i)=>{const d=Math.abs(t-x.t);if(d<bd){bd=d;b=i;}});return b;})).forEach(i=>{if(i===0||i===k.length-1)return;const p=k[i][1];p.lunge*=f;p.back*=f;p.dip*=Math.max(.8,f);});return k;}
function tPenetr(k0,F){const k=clone(k0),bad=F.filter(x=>{let md=9;for(let s=.15;s<=1;s+=.1){const p=[x.rh[0]+(x.tip[0]-x.rh[0])*s,x.rh[1]+(x.tip[1]-x.rh[1])*s,x.rh[2]+(x.tip[2]-x.rh[2])*s];md=Math.min(md,ptSeg(p,x.hips,x.chest));}return md<.3;});
  new Set(bad.map(x=>{let b=0,bd=9;k.forEach(([t],i)=>{const d=Math.abs(t-x.t);if(d<bd){bd=d;b=i;}});return b;})).forEach(i=>{if(i===0||i===k.length-1)return;k[i][1].sz+=.12;k[i][1].sx+=.1;});return k;}
function tAnticip(k0,F,amt){const k=clone(k0),pk=+(evaluate('x_',k0,F).metricas.t_impacto||0);if(!pk)return k;let j=k.findIndex(([t])=>t>=pk-.05);if(j<1)j=1;
  // chave de golpe = a primeira que muda forte; antecipação entre a anterior e ela
  const prev=k[j-1],cur=k[j],gap=cur[0]-prev[0];if(gap<.34)return k;const p=Object.assign({},prev[1]);
  for(const c of CH_MOV)p[c]=prev[1][c]+(prev[1][c]-cur[1][c])*amt;p.dip=Math.min(1.1,prev[1].dip+.12*amt/.35);k.splice(j,0,[+(prev[0]+gap*.55).toFixed(3),p]);return sortKeys(k);}
function tFollow(k0,F,amt){const k=clone(k0),pk=+(evaluate('x_',k0,F).metricas.t_impacto||0);if(!pk)return k;let j=k.findIndex(([t])=>t>=pk-.02);if(j<1||j>=k.length-1)return k;
  const prev=k[j-1],cur=k[j],nxt=k[j+1];const gap=nxt[0]-cur[0];if(gap<.3)return k;const p=Object.assign({},cur[1]);for(const c of CH_MOV)p[c]=cur[1][c]+(cur[1][c]-prev[1][c])*amt;p.fx=Math.max(cur[1].fx||0,.6);
  k.splice(j+1,0,[+(cur[0]+Math.min(.16,gap*.4)).toFixed(3),p]);return sortKeys(k);}
function tRetime(k0,F,f){const k=clone(k0),pk=+(evaluate('x_',k0,F).metricas.t_impacto||0);if(!pk)return k;let j=k.findIndex(([t])=>t>=pk-.02);if(j<1)return k;
  const d=(k[j][0]-k[j-1][0])*(f-1);for(let i=j;i<k.length;i++)k[i][0]=+(k[i][0]+d).toFixed(3);return k;}
function tSmooth(k0,alpha){const k=clone(k0);for(let i=1;i<k.length-1;i++)for(const c of CH_MOV){const a=k0[i-1][1][c],b=k0[i][1][c],d=k0[i+1][1][c];k[i][1][c]=b+((a+d)/2-b)*alpha;}return k;}
function tScale(k0,f){return k0.map(([t,p])=>[+(t*f).toFixed(3),{...p}]);}
function improve(name,keys){
  const F0=measure(name,keys),e0=evaluate(name,keys,F0),ref={en:energia(F0),pk:e0.metricas.pico_vel||0};let best=tHygiene(keys,name),F=measure(name,best),rep=evaluate(name,best,F,ref);const before=evaluate(name,keys,F0,ref);const log=[];
  const consider=(label,cand)=>{const F2=measure(name,cand),r2=evaluate(name,cand,F2,ref);if(r2.score>rep.score+.4){log.push(label+': '+rep.score+' → '+r2.score);best=cand;F=F2;rep=r2;return true;}return false;};
  for(let it=0;it<10;it++){let moved=false;const tp=new Set(rep.problemas.map(p=>p.tipo));
    if(tp.has('colada')||tp.has('repouso')){moved=consider('arrumar poses e fechar no repouso',tHygiene(best,name))||moved;}
    if(tp.has('alcance')){for(const f of [.95,.9,.85,.8,.7])if(consider('trazer o braço para dentro do alcance (×'+f+')',tReach(best,F,f))){moved=true;break;}}
    if(tp.has('perna')){for(const f of [.9,.8,.7,.6])if(consider('reduzir o avanço para o pé não flutuar (×'+f+')',tLeg(best,F,f))){moved=true;break;}}
    if(tp.has('colisao')){moved=consider('afastar a espada do tronco',tPenetr(best,F))||moved;}
    if(tp.has('antecipacao')){for(const a of [.35,.6,.9])if(consider('incluir preparação antes do golpe ('+a+')',tAnticip(best,F,a))){moved=true;break;}}
    if(tp.has('continuacao')){for(const a of [.2,.35,.5])if(consider('incluir continuação depois do impacto ('+a+')',tFollow(best,F,a))){moved=true;break;}}
    if(tp.has('explosao')){for(const f of [.85,.7,.55])if(consider('acelerar o golpe (tempo ×'+f+')',tRetime(best,F,f))){moved=true;break;}}
    if(tp.has('tranco')){for(const a of [.2,.35,.5])if(consider('suavizar trancos ('+a+')',tSmooth(best,a))){moved=true;break;}}
    if(tp.has('duracao')){const dr=DUR[name],d=best[best.length-1][0],target=d<dr[0]?dr[0]:dr[1];if(dr)moved=consider('ajustar a duração para '+target+'s',tScale(best,target/d))||moved;}
    if(!moved)break;}
  return {keys:best,antes:before,depois:rep,log};}
return {measure,evaluate,improve,energia,NOME,DUR,tScale};})();
