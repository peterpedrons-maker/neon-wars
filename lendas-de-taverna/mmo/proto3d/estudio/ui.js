(function(){
const $=s=>document.querySelector(s),$$=s=>[...document.querySelectorAll(s)];
const RAD=Math.PI/180,R90=Math.PI/2;
// ---------- canais (o que cada controle mexe), agrupados por parte do corpo ----------
const D=(k,l,a,b,min,max,step,deg)=>({k,l,a,b,min,max,step,deg});
const PARTS=[
 {id:'corpo',nome:'Corpo',ch:[D('dip','Agachar','em pé','agachado',0,1.2,.01),D('lean','Inclinar o tronco','para trás','para frente',-70,70,1,1),D('twist','Girar o tronco','para trás','para o golpe',-90,90,1,1),D('lunge','Avançar o corpo','','',-1.2,1.2,.01),D('back','Recuar o corpo','recua','',-1.6,0,.01),D('fall','Cair no chão','','',-95,30,1,1),D('own','Controle total (durante corrida)','automático','manual',0,1,.01)]},
 {id:'cabeca',nome:'Cabeça',ch:[D('hx','Cabeça para cima / baixo','para cima','para baixo',-60,60,1,1),D('hy','Olhar para os lados','esquerda','direita',-60,60,1,1),D('cup','Coroa sobe',  'baixa','alta',0,1,.01)]},
 {id:'bd',nome:'Braço direito + espada',ch:[D('sx','Mão para o lado','para dentro','para fora',-1.6,1.6,.01),D('sy','Mão para cima / baixo','baixo','alto',.2,4,.01),D('sz','Mão para frente / trás','trás','frente',-1.6,2.6,.01),D('rx','Ponta da lâmina: cima ⇄ baixo','cima','baixo',-185,185,1,1),D('ry','Girar a lâmina (golpe lateral)','','',-185,185,1,1),D('rz','Rolar a lâmina','','',-185,185,1,1)]},
 {id:'be',nome:'Braço esquerdo',ch:[D('lm','Mão livre','segura a espada','solta',0,1,.01),D('lx','Mão para o lado','para dentro','para fora',-2.2,2.2,.01),D('ly','Mão para cima / baixo','baixo','alto',.2,4,.01),D('lz','Mão para frente / trás','trás','frente',-1.6,3,.01)]},
 {id:'fx',nome:'Brilho e efeitos',ch:[D('glow','Brilho dos olhos e da coroa','apagado','forte',0,2,.01),D('orb','Orbe',  '','',0,2.5,.01),D('fx','Rastro e impacto','','',0,1,.01)]},
 {id:'ajuste',nome:'Andar e correr',tune:true}
];
const TUNES=[['speed','Velocidade do corpo',.4,2,.01],['stepH','Altura do passo',.3,2.2,.01],['armSwing','Balanço do braço livre',0,2.2,.01],['leanRun','Inclinação na corrida',0,2.2,.01],['bob','Sobe e desce do corpo',0,2.5,.01]];
const NOMES={idle:'Parado',walk:'Andar',run:'Correr',attack:'Golpe',forget:'Esquecimento',echo:'Eco',rift:'Fenda do Vazio',crown:'Coroa de Almas',dark:'Trevas',charge:'Investida',hurt:'Dano',death:'Morte'};
const LOCO={idle:0,walk:1,run:2.3};
let REI,SIM,cur='attack',t=0,playing=true,speed=1,loop=true,sel=-1,part='corpo',dirty=false,orig=null,hist=[],histT=0,last=0,booted=false;
const keys=()=>REI.ANIMS[cur];const isLoco=()=>cur in LOCO;
const dur=()=>{const k=keys();return k?k[k.length-1][0]:2};
const fmt=x=>x.toFixed(2).replace('.',',');
// ---------- inicializacao do motor ----------
function boot(){
  requestAnimationFrame(()=>setTimeout(()=>{try{window.bootEngine();}catch(e){$('#load').innerHTML='<div><b>Não foi possível iniciar o 3D</b><span>'+String(e&&e.message||e)+'</span></div>';return;}
    REI=window.REI;SIM=window.sim;
    for(const n in REI.ANIMS)REI.ANIMS[n]=REI.ANIMS[n].map(([tt,p])=>[tt,{...p}]);   // copias independentes (as chaves compartilhavam o mesmo objeto)
    orig=JSON.stringify({a:REI.ANIMS,t:REI.TUNE});
    $('#load').hidden=true;booted=true;buildHandles();buildAnims();render();loadSaved();requestAnimationFrame(loopFrame);},60));}
// ---------- loop de reproducao ----------
function cmd(){const R=R90;if(isLoco())return {move:LOCO[cur],yawTo:R,anim:''};if(cur==='death')return {move:0,yawTo:R,dead:Math.max(.0001,t)};return {move:0,anim:cur,at:t,yawTo:R};}
function loopFrame(ts){requestAnimationFrame(loopFrame);if(!booted)return;const dt=Math.min(.05,(ts-last)/1000||.016);last=ts;
  if(isLoco()){if(playing)SIM.step(dt*speed,cmd());}
  else{if(playing){t+=dt*speed;const d=dur();if(t>=d){if(loop){t=0;REI.reset();}else{t=d;playing=false;syncPlay();}}SIM.step(dt*speed,cmd());}
    else{for(let i=0;i<3;i++)SIM.step(1/30,cmd());}}
  placeHandles();updateTimeUI();}
function syncPlay(){$('#play').textContent=playing?'⏸':'▶';$('#play').classList.toggle('on',playing);}
// ---------- UI: animacoes, chaves, linha do tempo ----------
function buildAnims(){const box=$('#anims');box.innerHTML='';for(const n of ['idle','walk','run','attack','forget','echo','rift','crown','dark','charge','hurt','death']){const b=document.createElement('button');b.textContent=NOMES[n];b.dataset.a=n;b.onclick=()=>pickAnim(n);box.append(b);}markAnim();}
function markAnim(){$$('#anims button').forEach(b=>b.classList.toggle('on',b.dataset.a===cur));$('#animNote').textContent=isLoco()?'Esta animação é automática (andar/correr de verdade, com pés no chão). Ajuste na aba "Andar e correr" ou peça ao Claude.':'Arraste a linha do tempo, toque numa pose (losango azul) e mexa nos controles. Mexer num momento sem pose cria uma pose nova ali.';
  $('#hint').hidden=!$('#sheet').hidden;$('#hint').textContent=isLoco()?'Animação automática: use Ajuste fino › Andar e correr, ou peça ao Claude.':'Toque numa bolinha e arraste para mexer. Arraste o fundo para girar a câmera.';updateHandles();}
function pickAnim(n){cur=n;t=0;sel=-1;REI.reset();playing=true;syncPlay();markAnim();render();}
function render(){buildMarks();buildSliders();updateTimeUI();}
function buildMarks(){const m=$('#marks');m.innerHTML='';if(isLoco())return;const d=dur();keys().forEach(([tt],i)=>{const b=document.createElement('button');b.className='mk'+(i===sel?' sel':'');b.style.left=(tt/d*100)+'%';b.textContent=i+1;b.title='Pose '+(i+1)+' em '+fmt(tt)+' s';b.onclick=()=>{sel=i;t=tt;playing=false;syncPlay();REI.reset?0:0;render();};m.append(b);});}
function updateTimeUI(){const d=isLoco()?1:dur(),s=$('#scrub');if(document.activeElement!==s){s.max=d;s.value=t;}$('#rd').textContent=isLoco()?'movimento contínuo':fmt(t)+' / '+fmt(d)+' s';
  if(!isLoco()){const kt=$('#keyTime');kt.max=d;$('#keyT').textContent=sel>=0?'pose '+(sel+1)+' • '+fmt(keys()[sel][0])+' s':'nenhuma selecionada';if(sel>=0&&document.activeElement!==kt)kt.value=keys()[sel][0];const dd=$('#dur');if(document.activeElement!==dd)dd.value=d;$('#durV').textContent=fmt(d)+' s';}}
$('#scrub').addEventListener('input',e=>{if(isLoco())return;t=+e.target.value;playing=false;syncPlay();sel=nearest(t);buildMarks();});
function nearest(tt){const k=keys();let b=-1,bd=.04;k.forEach(([x],i)=>{const d=Math.abs(x-tt);if(d<bd){bd=d;b=i;}});return b;}
// ---------- edicao ----------
function snapshot(){return JSON.stringify({a:REI.ANIMS,t:REI.TUNE});}
function pushHist(){const now=Date.now();if(now-histT>900){hist.push(snapshot());if(hist.length>30)hist.shift();}histT=now;}
function restoreSnap(s){const o=JSON.parse(s);for(const n in o.a)REI.ANIMS[n]=o.a[n];Object.assign(REI.TUNE,o.t);}
function markDirty(){dirty=true;$('#save').textContent='alterado';clearTimeout(markDirty.h);markDirty.h=setTimeout(save,1400);}
function nearestWide(tt,w){const k=keys();let b=-1,bd=w;k.forEach(([x],i)=>{const d=Math.abs(x-tt);if(d<bd){bd=d;b=i;}});return b;}
function ensureKey(){if(isLoco())return false;if(sel>=0)return true;const i=nearestWide(t,.12);if(i>=0){sel=i;return true;}const p=REI.spline(keys(),Math.min(t,dur()));pushHist();const k=keys();let at=k.findIndex(([x])=>x>t);if(at<0)at=k.length;k.splice(at,0,[+t.toFixed(3),{...p}]);sel=at;buildMarks();return true;}
function setChan(c,v,silent){if(!ensureKey())return;pushHist();const [tt,p]=keys()[sel];p[c]=v;t=tt;playing=false;syncPlay();markDirty();}
function buildSliders(){const box=$('#sliders');box.innerHTML='';const P=PARTS.find(x=>x.id===part);
  $('#parts').innerHTML='';PARTS.forEach(x=>{const b=document.createElement('button');b.textContent=x.nome;b.className=x.id===part?'on':'';b.onclick=()=>{part=x.id;buildSliders();};$('#parts').append(b);});
  if(P.tune){TUNES.forEach(([k,l,mn,mx,st])=>{box.append(row(l,'','',mn,mx,st,REI.TUNE[k],v=>{pushHist();REI.TUNE[k]=v;markDirty();},false));});
    const n=document.createElement('div');n.className='note';n.textContent='Vale para andar, correr e a Investida.';box.append(n);return;}
  if(isLoco()){const n=document.createElement('div');n.className='note';n.textContent='Esta animação é automática. Use a aba "Andar e correr" para ajustar, ou escolha uma animação com poses (Golpe, Investida, Dano…).';box.append(n);return;}
  const pose=sel>=0?keys()[sel][1]:REI.spline(keys(),Math.min(t,dur()));
  P.ch.forEach(c=>{const val=pose[c.k],show=c.deg?val/RAD:val;box.append(row(c.l,c.a,c.b,c.min,c.max,c.step,show,v=>setChan(c.k,c.deg?v*RAD:v),c.deg));});
  if(sel<0){const n=document.createElement('div');n.className='note';n.textContent='Mexer aqui cria uma pose neste momento ('+fmt(t)+' s).';box.append(n);}}
function row(label,a,b,min,max,step,val,on,deg){const r=document.createElement('div');r.className='row';const l=document.createElement('label');const sp=document.createElement('span');l.textContent=label;l.append(sp);const inp=document.createElement('input');inp.type='range';inp.min=min;inp.max=max;inp.step=step;inp.value=val;const show=v=>sp.textContent=(deg?Math.round(v)+'°':(+v).toFixed(2).replace('.',','));show(val);
  inp.addEventListener('input',()=>{show(+inp.value);on(+inp.value);});r.append(l,inp);if(a||b){const h=document.createElement('div');h.className='hn';h.innerHTML='<span>'+a+'</span><span>'+b+'</span>';r.append(h);}return r;}
$('#addKey').onclick=()=>{if(isLoco())return;const p=REI.spline(keys(),Math.min(t,dur()));pushHist();const k=keys();let at=k.findIndex(([x])=>x>t);if(at<0)at=k.length;k.splice(at,0,[+t.toFixed(3),{...p}]);sel=at;markDirty();render();};
$('#dupKey').onclick=()=>{if(isLoco()||sel<0)return;pushHist();const k=keys(),[tt,p]=k[sel];const nt=Math.min(dur(),tt+.12);k.splice(sel+1,0,[+nt.toFixed(3),{...p}]);sel++;t=nt;markDirty();render();};
$('#delKey').onclick=()=>{if(isLoco()||sel<0||keys().length<=2)return;pushHist();keys().splice(sel,1);sel=-1;markDirty();render();};
$('#keyTime').addEventListener('input',e=>{if(sel<0)return;pushHist();const k=keys();let v=+e.target.value;if(sel===0)v=0;if(sel===k.length-1)v=Math.max(v,k[sel-1][0]+.05);const lo=sel>0?k[sel-1][0]+.02:0,hi=sel<k.length-1?k[sel+1][0]-.02:99;k[sel][0]=Math.max(lo,Math.min(hi,v));t=k[sel][0];playing=false;syncPlay();markDirty();buildMarks();});
$('#dur').addEventListener('input',e=>{if(isLoco())return;pushHist();const nd=+e.target.value,od=dur(),f=nd/od;keys().forEach(kk=>kk[0]=+(kk[0]*f).toFixed(3));t*=f;markDirty();buildMarks();});
$('#fixKeys').onclick=()=>{if(isLoco())return;const k=keys();pushHist();for(let i=k.length-2;i>=1;i--){if(k[i+1][0]-k[i][0]<.12)k.splice(i,1);}sel=-1;markDirty();render();};
$('#restore').onclick=()=>{const o=JSON.parse(orig);if(!o.a[cur])return;pushHist();REI.ANIMS[cur]=o.a[cur];sel=-1;markDirty();render();};
$('#undo').onclick=()=>{if(!hist.length)return;restoreSnap(hist.pop());sel=-1;markDirty();render();};
// ---------- gaveta (ajuste fino / Claude / notas) ----------
let pane='fine';function openSheet(p){pane=p||pane;$('#sheet').hidden=false;$('#hint').hidden=true;['fine','chat','notes'].forEach(n=>{$('#p-'+n).hidden=n!==pane;});$$('#sheet header [data-pane]').forEach(b=>b.classList.toggle('on',b.dataset.pane===pane));$$('[data-sheet]').forEach(b=>b.classList.toggle('on',b.dataset.sheet===pane));}
$$('[data-sheet]').forEach(b=>b.onclick=()=>{if(!$('#sheet').hidden&&pane===b.dataset.sheet){closeSheet();}else openSheet(b.dataset.sheet);});
$$('#sheet header [data-pane]').forEach(b=>b.onclick=()=>openSheet(b.dataset.pane));
function closeSheet(){$('#sheet').hidden=true;$('#hint').hidden=false;$$('[data-sheet]').forEach(b=>b.classList.remove('on'));}$('#closeSheet').onclick=closeSheet;
// ---------- transporte e camera ----------
$('#play').onclick=()=>{updateHandles();if(!isLoco()&&!playing&&t>=dur()-.01){t=0;REI.reset();}playing=!playing;syncPlay();};
$('#restart').onclick=()=>{t=0;REI.reset();playing=true;syncPlay();};
$('#loop').onclick=e=>{loop=!loop;e.target.classList.toggle('on',loop);};
const SPD=[1,.5,.25,.1,1.5];let spi=0;$('#speed').onclick=()=>{spi=(spi+1)%SPD.length;speed=SPD[spi];$('#speed').textContent=String(speed).replace('.',',')+'×';};
const CAMS={jogo:{yaw:0,pitch:47*RAD,dist:12.6,ty:2.45},lado:{yaw:0,pitch:6*RAD,dist:13,ty:2.4},frente:{yaw:R90,pitch:8*RAD,dist:13,ty:2.4},cima:{yaw:0,pitch:80*RAD,dist:14,ty:2},perto:{yaw:0,pitch:20*RAD,dist:7.5,ty:2.6}};
$$('.cams button').forEach(b=>b.onclick=()=>Object.assign(REI.CAMV,CAMS[b.dataset.cam]));
(function(){const st=$('#stage');let dragging=false,px=0,py=0,pin=0;const pts=new Map();
 st.addEventListener('pointerdown',e=>{if(e.target.closest('button')||e.target.closest('.hd'))return;st.setPointerCapture(e.pointerId);pts.set(e.pointerId,[e.clientX,e.clientY]);px=e.clientX;py=e.clientY;});
 st.addEventListener('pointermove',e=>{if(!pts.has(e.pointerId)||!REI)return;const c=REI.CAMV;if(pts.size===2){const a=[...pts.values()];const d0=Math.hypot(a[0][0]-a[1][0],a[0][1]-a[1][1]);pts.set(e.pointerId,[e.clientX,e.clientY]);const b=[...pts.values()],d1=Math.hypot(b[0][0]-b[1][0],b[0][1]-b[1][1]);c.dist=Math.max(4,Math.min(22,c.dist*d0/Math.max(1,d1)));return;}
  c.yaw-=(e.clientX-px)*.008;c.pitch=Math.max(.05,Math.min(1.5,c.pitch+(e.clientY-py)*.006));px=e.clientX;py=e.clientY;pts.set(e.pointerId,[e.clientX,e.clientY]);});
 const up=e=>pts.delete(e.pointerId);st.addEventListener('pointerup',up);st.addEventListener('pointercancel',up);
 st.addEventListener('wheel',e=>{if(!REI)return;e.preventDefault();REI.CAMV.dist=Math.max(4,Math.min(22,REI.CAMV.dist*(1+e.deltaY*.001)));},{passive:false});})();
// ---------- alcas sobre o boneco: tocar para selecionar, arrastar para mexer ----------
const HANDLES=[
 {id:'bd',nome:'Mão direita',pos:r=>r.sword.localToWorld(new THREE.Vector3(0,-.12,0))},
 {id:'ponta',nome:'Lâmina',pos:r=>{const v=new THREE.Vector3();r.tip.getWorldPosition(v);return v;}},
 {id:'be',nome:'Mão esquerda',pos:r=>{const h=[r.armSeg[0].hg,r.armSeg[0].ho,r.armSeg[0].hr].find(m=>m.visible)||r.armSeg[0].hr;return h.position.clone();}},
 {id:'cab',nome:'Cabeça',pos:r=>{const v=new THREE.Vector3();r.head.getWorldPosition(v);v.y+=.15;return v;}},
 {id:'tronco',nome:'Tronco',pos:r=>{const v=new THREE.Vector3();r.chest.getWorldPosition(v);v.y+=.45;return v;}},
 {id:'quadril',nome:'Quadril / agachar',pos:r=>{const v=new THREE.Vector3();r.body.getWorldPosition(v);return v;}}];
let hsel=null;const hbox=()=>$('#handles');
function buildHandles(){hbox().innerHTML='';HANDLES.forEach(h=>{const b=document.createElement('button');b.className='hd';b.dataset.h=h.id;b.setAttribute('aria-label',h.nome);b.innerHTML='<span class="lb">'+h.nome+'</span>';hbox().append(b);h.el=b;
  b.addEventListener('pointerdown',e=>{e.preventDefault();e.stopPropagation();selectHandle(h.id);startDrag(h,e);b.setPointerCapture(e.pointerId);});
  b.addEventListener('pointermove',e=>{if(drag&&drag.id===e.pointerId)moveDrag(h,e);});
  const end=e=>{if(drag&&drag.id===e.pointerId)drag=null;};b.addEventListener('pointerup',end);b.addEventListener('pointercancel',end);});}
function selectHandle(id){hsel=id;HANDLES.forEach(h=>h.el.classList.toggle('sel',h.id===id));}
function updateHandles(){const show=booted&&!isLoco();hbox().hidden=!show;}
function placeHandles(){if(!booted||isLoco())return;const r=REI.refs,cv=$('#c').getBoundingClientRect(),st=$('#stage').getBoundingClientRect();
  const P=HANDLES.map(h=>{const v=h.pos(r).project(r.cam);return {h,x:(v.x*.5+.5)*cv.width+cv.left-st.left,y:(-v.y*.5+.5)*cv.height+cv.top-st.top,vis:v.z<1};});
  for(let it=0;it<6;it++)for(let i=0;i<P.length;i++)for(let j=i+1;j<P.length;j++){const a=P[i],b=P[j];if(drag&&(drag.hid===a.h.id||drag.hid===b.h.id))continue;let dx=b.x-a.x,dy=b.y-a.y,d=Math.hypot(dx,dy);const m=40;if(d<m){if(d<.5){dx=1;dy=0;d=1;}const k=(m-d)/2/d;a.x-=dx*k;a.y-=dy*k;b.x+=dx*k;b.y+=dy*k;}}
  P.forEach(q=>{q.h.el.style.left=q.x+'px';q.h.el.style.top=q.y+'px';q.h.el.style.visibility=q.vis?'visible':'hidden';q.h.el.style.zIndex=q.h.id===hsel?5:1;});}
let drag=null;const RC=new THREE.Raycaster(),PL=new THREE.Plane(),V3=THREE.Vector3;
function rayAt(e){const cv=$('#c').getBoundingClientRect(),ndc=new THREE.Vector2(((e.clientX-cv.left)/cv.width)*2-1,-((e.clientY-cv.top)/cv.height)*2+1);RC.setFromCamera(ndc,REI.refs.cam);return RC.ray;}
function hitPlane(e,point){const cam=REI.refs.cam,n=new V3();cam.getWorldDirection(n);PL.setFromNormalAndCoplanarPoint(n,point);const o=new V3();return rayAt(e).intersectPlane(PL,o)?o:null;}
const clampC=(c,v)=>{const d=PARTS.flatMap(p=>p.ch||[]).find(x=>x.k===c);if(!d)return v;const k=d.deg?RAD:1;return Math.max(d.min*k,Math.min(d.max*k,v));};
function startDrag(h,e){if(isLoco())return;ensureKey();pushHist();playing=false;syncPlay();const r=REI.refs,p=h.pos(r);const hit=hitPlane(e,p);drag={id:e.pointerId,hid:h.id,x:e.clientX,y:e.clientY,off:hit?p.clone().sub(hit):new V3(),p0:p.clone(),pose0:{...keys()[sel][1]}};t=keys()[sel][0];}
function setC(c,v){keys()[sel][1][c]=clampC(c,v);}
function moveDrag(h,e){if(!drag||sel<0)return;const r=REI.refs,pose=keys()[sel][1],dx=e.clientX-drag.x,dy=e.clientY-drag.y,p0=drag.pose0;
  if(h.id==='bd'||h.id==='be'){const hit=hitPlane(e,drag.p0);if(!hit)return;const tg=hit.add(drag.off);
    if(h.id==='bd'){const q=r.sword.quaternion,org=tg.clone().add(new V3(0,.12,0).applyQuaternion(q)),l=r.G.worldToLocal(org);setC('sx',l.x);setC('sy',l.y);setC('sz',l.z);}
    else{const l=r.G.worldToLocal(tg);setC('lx',l.x);setC('ly',l.y);setC('lz',l.z);setC('lm',1);}}
  else if(h.id==='ponta'){const hand=r.sword.localToWorld(new V3(0,-.12,0)),hit=hitPlane(e,hand);if(!hit)return;const d=hit.sub(hand).normalize(),inv=r.G.quaternion.clone().invert(),dl=d.applyQuaternion(inv);const rx=Math.acos(Math.max(-1,Math.min(1,dl.y)));setC('rx',rx);if(Math.sin(rx)>.06)setC('ry',Math.atan2(dl.x,dl.z));}
  else if(h.id==='cab'){setC('hy',p0.hy+dx*.009);setC('hx',p0.hx+dy*.009);}
  else if(h.id==='tronco'){setC('twist',p0.twist+dx*.008);setC('lean',p0.lean+dy*.007);}
  else if(h.id==='quadril'){setC('dip',p0.dip+dy*.006);setC('lunge',p0.lunge+dx*.006);}
  t=keys()[sel][0];markDirty();syncSliderValues();}
function syncSliderValues(){if($('#sheet').hidden||pane!=='fine'||sel<0)return;const P=PARTS.find(x=>x.id===part);if(!P||!P.ch)return;const pose=keys()[sel][1];$$('#sliders .row').forEach((row,i)=>{const c=P.ch[i];if(!c)return;const inp=row.querySelector('input'),sp=row.querySelector('label span'),v=c.deg?pose[c.k]/RAD:pose[c.k];if(inp&&document.activeElement!==inp){inp.value=v;sp.textContent=c.deg?Math.round(v)+'°':(+v).toFixed(2).replace('.',',');}});}
// ---------- salvar / carregar (db) ----------
let DB=null,saving=false;
async function initDb(){try{const c=window.claude&&await window.claude.use('db');DB=c||null;}catch(e){DB=null;}}
async function loadSaved(){await initDb();if(!DB){$('#save').textContent='sem salvar (offline)';return;}
  try{const s=await DB.doc('estudio/animacoes').get();if(s.exists){const o=JSON.parse(s.data().json);for(const n in o.a)REI.ANIMS[n]=o.a[n];Object.assign(REI.TUNE,o.t||{});$('#save').textContent='carregado';render();}else $('#save').textContent='pronto';}catch(e){$('#save').textContent='não consegui carregar';}
  subNotes();}
async function save(){if(!DB||saving||!dirty)return;saving=true;dirty=false;$('#save').textContent='salvando…';try{await DB.doc('estudio/animacoes').set({json:snapshot(),at:new Date().toISOString()});$('#save').textContent='salvo';}catch(e){$('#save').textContent='erro ao salvar';dirty=true;}saving=false;if(dirty)setTimeout(save,1500);}
// ---------- anotacoes ----------
function subNotes(){if(!DB)return;try{DB.collection('notas').orderBy('criada','desc').limit(60).onSnapshot(s=>{const box=$('#notes');box.innerHTML='';s.docs.forEach(d=>{const n=d.data();const el=document.createElement('div');el.className='nt'+(n.feita?' done':'');el.innerHTML='<span class="t"></span><p></p>';el.querySelector('.t').textContent=(NOMES[n.anim]||n.anim)+' '+fmt(+n.t||0)+'s';el.querySelector('p').textContent=n.texto;
  const ok=document.createElement('button');ok.textContent=n.feita?'↺':'✓';ok.onclick=()=>DB.doc('notas/'+d.id).update({feita:!n.feita}).catch(()=>{});const x=document.createElement('button');x.textContent='✕';x.className='danger';x.onclick=()=>DB.doc('notas/'+d.id).delete().catch(()=>{});const go=document.createElement('button');go.textContent='ir';go.onclick=()=>{if(n.anim!==cur)pickAnim(n.anim);t=+n.t||0;playing=false;syncPlay();sel=nearest(t);render();};el.append(go,ok,x);box.append(el);});},()=>{});}catch(e){}}
$('#addNote').onclick=async()=>{const tx=$('#noteText').value.trim();if(!tx)return;if(!DB){alert&&0;$('#noteText').placeholder='Salvar notas precisa de login no Claude.';return;}try{await DB.collection('notas').add({anim:cur,t:+t.toFixed(3),texto:tx,feita:false,criada:Date.now()});$('#noteText').value='';}catch(e){}};
$('#copy').onclick=async()=>{const txt=snapshot();try{await navigator.clipboard.writeText(txt);$('#copy').textContent='Copiado ✓';}catch(e){const ta=document.createElement('textarea');ta.value=txt;document.body.append(ta);ta.select();try{document.execCommand('copy');$('#copy').textContent='Copiado ✓';}catch(_){}ta.remove();}setTimeout(()=>$('#copy').textContent='Copiar tudo (JSON)',1800);};
// ---------- chat com o Claude (ele edita as poses por ferramentas) ----------
const SUG=['Faça o golpe mais forte: puxe a espada mais para trás e agache antes de bater','Levante mais a mão esquerda no Esquecimento','Deixe o dano mais exagerado, cabeça para trás','Na Investida, incline mais o corpo para frente'];
SUG.forEach(s=>{const b=document.createElement('button');b.textContent=s;b.onclick=()=>{$('#ask').value=s;};$('#sug').append(b);});
const turns=[];let ctl=null;
const GLOSS=`Você ajusta animações de um personagem 3D (Rei Esquecido, boss de um RPG) por poses-chave. Cada animação é uma lista de poses (chaves) em segundos; o motor interpola com spline. Canais (rotações em RADIANOS nas ferramentas): lean=inclinar tronco (+frente), twist=girar tronco (+para a direção do golpe), dip=agachar (0..1.2), lunge=avançar (+frente), back=recuar (-), fall=cair (-1.57 deitado), hx=cabeça (+olha para baixo), hy=olhar lateral, cup=coroa sobe; espada/mão direita: sx=lado, sy=altura (chão=0, ombro≈2.3, acima da cabeça≈3.5), sz=frente(+)/trás(-), rx=ponta da lâmina (0=para cima, 1.57=para frente, 3.14=para baixo), ry=girar a lâmina (golpe lateral), rz=rolar; mão esquerda: lm=1 solta/0 segura a espada, lx/ly/lz como a direita (lx negativo=lado esquerdo); glow=brilho, orb=orbe, fx=rastro; own=1 mantém a pose mesmo correndo. Animações: idle, walk, run (automáticas; só TUNE: speed, stepH, armSwing, leanRun, bob), attack, forget, echo, rift, crown, dark, charge, hurt, death. Responda em português, curto. Use as ferramentas para realmente editar; valores moderados; depois diga o que mudou em 1-2 frases.`;
function summary(){const k=keys();return {animacao:cur,duracao:+dur().toFixed(2),tempo_atual:+t.toFixed(2),poses:k?k.map(([tt,p],i)=>({i,t:+tt.toFixed(2),...Object.fromEntries(Object.entries(p).map(([a,b])=>[a,+(+b).toFixed(2)]))})):[],tune:REI.TUNE};}
function addMsg(txt,who){const m=document.createElement('div');m.className='m'+(who==='u'?' u':'');m.textContent=txt;$('#msgs').append(m);$('#msgs').scrollTop=1e9;return m;}
async function ask(){const q=$('#ask').value.trim();if(!q)return;$('#askErr').textContent='';let sample=null;try{sample=window.claude&&await window.claude.use('sample');}catch(e){}
  if(!sample){$('#askErr').textContent='O chat precisa abrir dentro do Claude.';return;}
  addMsg(q,'u');$('#ask').value='';turns.push({role:'user',content:q+'\n\n[estado atual]\n'+JSON.stringify(summary()).slice(0,9000)});const bub=addMsg('Pensando…','a');$('#send').disabled=true;$('#stop').hidden=false;ctl=new AbortController();
  const tools=[
   {name:'definir_pose',description:'Define canais de uma pose. Informe animacao, e ou indice da pose (i) ou o tempo em segundos (t, cria pose se não existir). valores = objeto canal->número (rotações em radianos). Retorna a pose resultante.',inputSchema:{type:'object',properties:{animacao:{type:'string'},i:{type:'number'},t:{type:'number'},valores:{type:'object'}},required:['animacao','valores']},execute:inp=>{const a=String(inp.animacao);if(!REI.ANIMS[a])throw new Error('animação desconhecida');const k=REI.ANIMS[a];let idx=inp.i!=null?Math.round(+inp.i):-1;if(idx<0||idx>=k.length){const tt=+inp.t;if(!isFinite(tt))throw new Error('informe i ou t');idx=k.findIndex(([x])=>Math.abs(x-tt)<.03);if(idx<0){const p=REI.spline(k,tt);let at=k.findIndex(([x])=>x>tt);if(at<0)at=k.length;k.splice(at,0,[+tt.toFixed(3),{...p}]);idx=at;}}pushHist();for(const [c,v] of Object.entries(inp.valores||{})){if(c in k[idx][1]&&isFinite(+v))k[idx][1][c]=+v;}if(a!==cur)pickAnim(a);sel=idx;t=k[idx][0];playing=false;syncPlay();markDirty();render();return {i:idx,t:k[idx][0]};}},
   {name:'adicionar_pose',description:'Cria uma pose nova no tempo t (segundos) copiando a animação nesse instante. Retorna o índice.',inputSchema:{type:'object',properties:{animacao:{type:'string'},t:{type:'number'}},required:['animacao','t']},execute:inp=>{const a=String(inp.animacao),k=REI.ANIMS[a];if(!k)throw new Error('animação desconhecida');const tt=+inp.t,p=REI.spline(k,tt);pushHist();let at=k.findIndex(([x])=>x>tt);if(at<0)at=k.length;k.splice(at,0,[+tt.toFixed(3),{...p}]);markDirty();render();return {i:at};}},
   {name:'apagar_pose',description:'Apaga a pose de índice i (mantém no mínimo 2).',inputSchema:{type:'object',properties:{animacao:{type:'string'},i:{type:'number'}},required:['animacao','i']},execute:inp=>{const k=REI.ANIMS[String(inp.animacao)];if(!k||k.length<=2)throw new Error('não dá');pushHist();k.splice(Math.round(+inp.i),1);sel=-1;markDirty();render();return 'ok';}},
   {name:'definir_duracao',description:'Muda a duração (segundos) de uma animação, escalando o tempo das poses.',inputSchema:{type:'object',properties:{animacao:{type:'string'},segundos:{type:'number'}},required:['animacao','segundos']},execute:inp=>{const k=REI.ANIMS[String(inp.animacao)];if(!k)throw new Error('desconhecida');const od=k[k.length-1][0],f=Math.max(.4,Math.min(6,+inp.segundos))/od;pushHist();k.forEach(x=>x[0]=+(x[0]*f).toFixed(3));markDirty();render();return 'ok';}},
   {name:'ajustar_andar_correr',description:'Ajusta TUNE: speed, stepH, armSwing, leanRun ou bob (multiplicadores, 1 = padrão).',inputSchema:{type:'object',properties:{nome:{type:'string'},valor:{type:'number'}},required:['nome','valor']},execute:inp=>{const n=String(inp.nome);if(!(n in REI.TUNE))throw new Error('nome inválido');pushHist();REI.TUNE[n]=+inp.valor;markDirty();render();return 'ok';}},
   {name:'tocar',description:'Troca para uma animação e a toca do início.',inputSchema:{type:'object',properties:{animacao:{type:'string'}},required:['animacao']},execute:inp=>{const a=String(inp.animacao);if(!(a in NOMES))throw new Error('desconhecida');pickAnim(a);return 'ok';}}];
  try{const {text}=await sample([{role:'user',content:GLOSS},...turns.slice(-8)],{tools,cache:false,signal:ctl.signal,modelTier:'default',onText:({text})=>{bub.textContent=text;}});turns.push({role:'assistant',content:text});bub.textContent=text;}
  catch(e){const c=e&&e.code;bub.textContent=(e&&e.text)||'';if(c==='cancelled'){bub.textContent=bub.textContent||'Parado.';}else{$('#askErr').textContent=({not_granted:'Você precisa permitir o Claude nesta página.',rate_limited:'Muitos pedidos. Espere um pouco.',tools_unavailable:'Este app não deixa o Claude editar as poses aqui.'})[c]||'Não consegui falar com o Claude agora.';if(!bub.textContent)bub.remove();}}
  $('#send').disabled=false;$('#stop').hidden=true;ctl=null;}
$('#send').onclick=ask;$('#stop').onclick=()=>ctl&&ctl.abort();
$('#ask').addEventListener('keydown',e=>{if(e.key==='Enter'&&(e.ctrlKey||e.metaKey))ask();});
boot();
})();
