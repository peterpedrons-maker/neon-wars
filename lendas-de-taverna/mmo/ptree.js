/* ===== ÁRVORE ÚNICA DE PASSIVAS (estilo PoE) — substitui os 3 ramos de talentos =====
   Malha de anéis hexagonais (6 setores de 60°) em volta de um nó central; cada classe tem 6 setores próprios.
   Tipos de nó: pequeno (1 atributo) · duplo (2 atributos) · notável (2 atributos + mini passiva) · híbrido (mistura dois setores)
   · pedra angular (efeito forte com contrapartida) · subclasse (trancado até escolher a subclasse, Nv10).
   Lê SAVE (cls, lv, sub, gold, tr) e usa funções do jogo: sfx, toast, gConfirm, recalcHero, writeSave, badge, renderPan, tfCalc. */
(function(){
'use strict';
const PT={sc:1,vx:0,vy:0,sel:null,cls:null,fit:true};
window.PT=PT;

/* ---------- atributos: nome, cor, valor base por nó pequeno, formato ---------- */
const ST={
 atk:{n:'Ataque',c:'#ff7a5a',v:.02,f:'p'},crit:{n:'Chance crítica',c:'#ffd24a',v:.01,f:'p'},critd:{n:'Dano crítico',c:'#ff9a3a',v:.05,f:'p'},
 aspd:{n:'Vel. de ataque',c:'#c8e85a',v:.02,f:'p'},spd:{n:'Vel. de movimento',c:'#6ae0ff',v:.015,f:'p'},
 def:{n:'Defesa',c:'#7ab8ff',v:.025,f:'p'},dmgred:{n:'Dano recebido',c:'#9a8aff',v:.01,f:'m'},hp:{n:'Vida',c:'#ff5a7a',v:.03,f:'p'},
 regen:{n:'Regen. de vida/s',c:'#6ae08a',v:.0012,f:'r'},pot:{n:'Eficácia de poção',c:'#4ad8c0',v:.04,f:'p'},
 cdr:{n:'Recarga de habilidades',c:'#c08aff',v:.015,f:'m'},dcd:{n:'Recarga da esquiva',c:'#8ad0ff',v:.03,f:'m'},
 exec:{n:'Dano em alvos <30% vida',c:'#e05a5a',v:.04,f:'p'},boss:{n:'Dano em chefes/elites',c:'#ffc84a',v:.03,f:'p'},
 drop:{n:'Chance de drop extra',c:'#e8c060',v:.02,f:'p'},
 cbw:{n:'Janela do combo',c:'#ffffff',v:.5,f:'u'},cbp:{n:'Cargas de Postura',c:'#9ad0ff',v:1,f:'u'},cb4:{n:'Combo de 4 golpes',c:'#ffb050',v:1,f:'u'}
};
function fmt(k,v){const s=ST[k]||{f:'p'};const a=Math.abs(v),sg=v<0?'−':'+';
 if(s.f==='r')return sg+(a*100).toFixed(2).replace('.',',')+'% vida/s';
 if(s.f==='u')return k==='cbw'?sg+(a*4).toFixed(0)+'% janela, +'+(a*2).toFixed(0)+'% preciso':k==='cb4'?'ativa':sg+Math.round(a)+' carga';
 const x=a*100;return sg+(x%1?x.toFixed(1).replace('.',','):x)+'%';}
function fxText(fx){return Object.keys(fx).map(k=>{const s=ST[k];if(!s)return '';const v=fx[k];
  if(k==='dmgred')return '−'+Math.abs(v*100).toFixed(1).replace('.0','').replace('.',',')+'% dano recebido';
  if(s.f==='m')return '−'+Math.abs(v*100).toFixed(1).replace('.0','').replace('.',',')+'% '+s.n.toLowerCase();
  if(k==='cb4')return 'Combo de 4 golpes (4º em área)';
  return fmt(k,v)+' '+s.n.toLowerCase();}).filter(Boolean).join(' · ');}

/* ---------- glifos 9×9 (um por atributo) ---------- */
const GL={
atk:['......###','.....###.','....###..','#..###...','.####....','..##.....','.#.##....','#...#....','.........'],
crit:['....#....','....#....','..#.#.#..','...###...','#########','...###...','..#.#.#..','....#....','....#....'],
critd:['#...#...#','.#..#..#.','..#.#.#..','...###...','###...###','...###...','..#.#.#..','.#..#..#.','#...#...#'],
aspd:['.........','##...##..','.##...##.','..##...##','...##...#','..##...##','.##...##.','##...##..','.........'],
spd:['..###....','..###....','..###....','..###....','..####...','..#####..','.#######.','.#######.','.........'],
def:['.#######.','#########','#########','#########','#########','.#######.','..#####..','...###...','....#....'],
dmgred:['.#######.','#########','####.####','###...###','####.####','.#######.','..#####..','...###...','....#....'],
hp:['.........','.##...##.','####.####','#########','#########','.#######.','..#####..','...###...','....#....'],
regen:['...###...','...###...','...###...','###.#.###','#########','###.#.###','...###...','...###...','...###...'],
pot:['...###...','....#....','....#....','...###...','..#####..','.#######.','.#######.','.#######.','..#####..'],
cdr:['#########','.#######.','..#####..','...###...','....#....','...###...','..#####..','.#######.','#########'],
dcd:['..#####..','.#.....#.','#.......#','#....##..','#...###..','.#.....#.','..#####.#','.......##','......###'],
exec:['.#######.','#########','##.###.##','##.###.##','#########','.###.###.','..#####..','..#.#.#..','.........'],
boss:['.........','#...#...#','##.###.##','#########','#########','#########','#########','.........','.........'],
drop:['..#####..','.#######.','###...###','##.###.##','##.#.#.##','##.###.##','###...###','.#######.','..#####..'],
cbw:['..#####..','.#.....#.','#..###..#','#.#####.#','#.#####.#','#.#####.#','#..###..#','.#.....#.','..#####..'],
cbp:['.........','.#######.','.........','#########','#########','.........','.#######.','#########','.........'],
cb4:['##.....##','###...###','.##...##.','....#....','...###...','....#....','.##...##.','###...###','##.....##']};
const GC={};
function hexRGB(h){h=h.replace('#','');return[parseInt(h.substr(0,2),16),parseInt(h.substr(2,2),16),parseInt(h.substr(4,2),16)];}
function glyph(k,col){const key=k+col;if(GC[key])return GC[key];const g=GL[k]||GL.atk,cv=document.createElement('canvas');cv.width=cv.height=11;const x=cv.getContext('2d');
 const on=(r,c)=>r>=0&&c>=0&&r<9&&c<9&&g[r][c]==='#';const [R,G,B]=hexRGB(col);
 x.fillStyle='#0b0e16';for(let r=-1;r<10;r++)for(let c=-1;c<10;c++){if(on(r,c))continue;let n=0;for(let a=-1;a<=1;a++)for(let b=-1;b<=1;b++)if(on(r+a,c+b))n=1;if(n)x.fillRect(c+1,r+1,1,1);}
 for(let r=0;r<9;r++)for(let c=0;c<9;c++){if(!on(r,c))continue;const lit=!on(r-1,c)||!on(r,c-1),dk=!on(r+1,c)||!on(r,c+1);
  const m=lit?1.28:dk?.72:1;x.fillStyle=`rgb(${Math.min(255,R*m)|0},${Math.min(255,G*m)|0},${Math.min(255,B*m)|0})`;x.fillRect(c+1,r+1,1,1);}
 return GC[key]=cv.toDataURL();}
window.ptGlyph=glyph;

/* ---------- conteúdo por classe: 6 setores (nome, cor, atributos, 5 notáveis, 3 minis) + 6 pedras angulares ---------- */
const M=(k,v,t)=>({k,v,t});
const CL={
guerreiro:{
 sec:[
 {n:'Fúria',c:'#ff6a4a',p:['atk','crit'],nm:['Golpe Brutal','Sede de Sangue','Ímpeto','Carnificina','Raiva Cega'],mi:[M('critd',.08,'Cicatrizes: golpes críticos mais fortes'),M('exec',.05,'Fim de Luta: mais dano em alvos feridos'),M('aspd',.03,'Frenesi: ataca mais rápido')]},
 {n:'Postura',c:'#7ab8ff',p:['def','dmgred'],nm:['Pés Firmes','Escudo Erguido','Guarda de Ferro','Resistência','Parede Viva'],mi:[M('cbp',1,'Postura Firme: +1 carga de Postura'),M('cbw',.5,'Mão Firme: janela de combo maior'),M('hp',.03,'Couraça: mais vida')]},
 {n:'Bastião',c:'#6ae08a',p:['hp','regen'],nm:['Pele Grossa','Coração de Pedra','Fôlego','Veterano','Recuperação'],mi:[M('pot',.1,'Cantil Cheio: poções melhores'),M('dmgred',.02,'Casca Dura: menos dano recebido'),M('regen',.002,'Segundo Fôlego: regenera vida')]},
 {n:'Ritmo',c:'#c8e85a',p:['aspd','spd'],nm:['Passo Firme','Cadência','Giro Rápido','Avanço','Pé Ligeiro'],mi:[M('dcd',.08,'Rolada Ágil: esquiva recarrega mais rápido'),M('cdr',.03,'Fôlego de Batalha: recarga menor'),M('aspd',.03,'Cadência de Guerra')]},
 {n:'Comando',c:'#ffc84a',p:['boss','atk'],nm:['Voz de Comando','Desafio','Caçador de Líderes','Estandarte','Disciplina'],mi:[M('boss',.06,'Quebra-Elite: mais dano em chefes/elites'),M('drop',.03,'Espólio de Guerra: chance de drop extra'),M('cdr',.03,'Ordens Rápidas')]},
 {n:'Finalizador',c:'#c08aff',p:['critd','exec'],nm:['Golpe Final','Estocada Fatal','Impiedoso','Sentença','Último Suspiro'],mi:[M('cb4',1,'Golpe Final em Área: combo de 4 golpes'),M('crit',.02,'Olho do Carrasco'),M('atk',.04,'Peso do Machado')]}],
 key:[['Berserker','Fúria sem freio: +22% ataque, +10% vel. de ataque, −12% defesa.',{atk:.22,aspd:.1,def:-.12}],
      ['Muralha Imóvel','+25% defesa, −8% dano recebido, −8% vel. de movimento.',{def:.25,dmgred:.08,spd:-.08}],
      ['Coração de Gigante','+30% vida e regeneração, −6% ataque.',{hp:.3,regen:.004,atk:-.06}],
      ['Maré de Aço','+14% vel. de ataque e movimento, −10% defesa.',{aspd:.14,spd:.08,def:-.1}],
      ['General de Guerra','+20% dano em chefes e elites, +10% ataque, −6% vida.',{boss:.2,atk:.1,hp:-.06}],
      ['Carrasco','+30% dano crítico e +12% dano em alvos feridos, −5% crítico.',{critd:.3,exec:.12,crit:-.03}]]},
mago:{
 sec:[
 {n:'Chama',c:'#ff7a3a',p:['atk','crit'],nm:['Centelha','Brasa Viva','Língua de Fogo','Inferno','Cinzas Quentes'],mi:[M('critd',.08,'Combustão: críticos explosivos'),M('exec',.05,'Calcinar: mais dano em alvos feridos'),M('atk',.03,'Chama Alta')]},
 {n:'Gelo',c:'#8ad8ff',p:['dmgred','def'],nm:['Geada','Manto Gélido','Cristal de Gelo','Inverno','Pele de Neve'],mi:[M('def',.04,'Armadura de Gelo'),M('dmgred',.02,'Frio Entorpecente: inimigos batem mais fraco'),M('hp',.04,'Resfriar Ferimentos')]},
 {n:'Arcano',c:'#c08aff',p:['cdr','critd'],nm:['Fluxo Arcano','Runa Gravada','Mente Aberta','Singularidade','Eco Arcano'],mi:[M('cdr',.04,'Foco Arcano: recarga menor'),M('boss',.05,'Dissolver: mais dano em chefes'),M('crit',.02,'Visão Rúnica')]},
 {n:'Éter',c:'#4ad8c0',p:['pot','regen'],nm:['Fonte de Mana','Meditação','Aura Calma','Fluxo Constante','Reserva Etérea'],mi:[M('pot',.1,'Elixir Arcano: poções melhores'),M('regen',.002,'Sopro Etéreo: regeneração'),M('hp',.04,'Corpo Etéreo')]},
 {n:'Tempestade',c:'#ffe85a',p:['aspd','spd'],nm:['Faísca','Condutor','Relâmpago','Trovão','Passo Elétrico'],mi:[M('dcd',.08,'Salto Estático: esquiva recarrega mais rápido'),M('aspd',.03,'Sobrecarga: conjura mais rápido'),M('crit',.02,'Raio Certeiro')]},
 {n:'Cinzas',c:'#d05a8a',p:['exec','boss'],nm:['Marca da Morte','Sopro Final','Eclipse','Ruína','Pó de Estrelas'],mi:[M('exec',.06,'Rebanho de Cinzas: mais dano em feridos'),M('drop',.03,'Pó Precioso: chance de drop extra'),M('atk',.04,'Chama Negra')]}],
 key:[['Combustão Total','+25% ataque e +10% crítico, −15% vida.',{atk:.25,crit:.1,hp:-.15}],
      ['Coração de Gelo','+25% defesa, −10% dano recebido, −10% ataque.',{def:.25,dmgred:.1,atk:-.1}],
      ['Mente Infinita','−18% recarga de habilidades e +10% crítico, −10% defesa.',{cdr:.18,crit:.1,def:-.1}],
      ['Fonte Inesgotável','+40% eficácia de poção e +0,6% regen., −8% ataque.',{pot:.4,regen:.006,atk:-.08}],
      ['Olho da Tempestade','+16% vel. de ataque e +8% movimento, −12% vida.',{aspd:.16,spd:.08,hp:-.12}],
      ['Arauto das Cinzas','+22% dano em chefes e +14% em alvos feridos, −6% defesa.',{boss:.22,exec:.14,def:-.06}]]},
ladino:{
 sec:[
 {n:'Lâmina',c:'#ff6a6a',p:['aspd','crit'],nm:['Corte Rápido','Dança de Lâminas','Ferroada','Flecha de Aço','Retalho'],mi:[M('aspd',.03,'Mãos Velozes'),M('critd',.08,'Corte Profundo'),M('atk',.03,'Fio Afiado')]},
 {n:'Sombra',c:'#9a8aff',p:['dcd','spd'],nm:['Passo Silencioso','Véu Sombrio','Névoa','Manto Negro','Rastro de Fumaça'],mi:[M('dcd',.1,'Passo Sombrio: esquiva recarrega mais rápido'),M('dmgred',.02,'Sombra Esquiva: menos dano'),M('spd',.03,'Pés de Gato')]},
 {n:'Veneno',c:'#6ae08a',p:['atk','exec'],nm:['Gota Amarga','Dose Letal','Toxina','Praga','Veneno Lento'],mi:[M('exec',.06,'Dose Final: mais dano em feridos'),M('atk',.04,'Veneno Forte'),M('boss',.04,'Peçonha de Chefe')]},
 {n:'Fuga',c:'#6ae0ff',p:['spd','dmgred'],nm:['Fôlego Curto','Escapada','Salto Ágil','Cortina','Resvalar'],mi:[M('hp',.04,'Sobrevivente'),M('dmgred',.02,'Escorregadio'),M('regen',.002,'Fôlego de Fuga')]},
 {n:'Saque',c:'#e8c060',p:['drop','pot'],nm:['Mãos Leves','Bolso Cheio','Olho de Ladrão','Contrabando','Faro de Tesouro'],mi:[M('drop',.03,'Furto: chance de drop extra'),M('pot',.1,'Frasco Roubado'),M('crit',.02,'Alvo Fácil')]},
 {n:'Letal',c:'#c08aff',p:['critd','boss'],nm:['Golpe nas Costas','Ponto Fraco','Execução','Assassinato','Última Palavra'],mi:[M('critd',.1,'Golpe Mortal'),M('boss',.06,'Caçador de Chefes'),M('exec',.04,'Sentença Silenciosa')]}],
 key:[['Mil Cortes','+18% vel. de ataque e +8% crítico, −12% vida.',{aspd:.18,crit:.08,hp:-.12}],
      ['Fantasma','+25% menos recarga da esquiva e +10% movimento, −10% defesa.',{dcd:.25,spd:.1,def:-.1}],
      ['Peçonha Mortal','+22% ataque e +12% dano em feridos, −10% defesa.',{atk:.22,exec:.12,def:-.1}],
      ['Pulo da Raposa','+14% movimento e −8% dano recebido, −8% ataque.',{spd:.14,dmgred:.08,atk:-.08}],
      ['Rei dos Ladrões','+10% chance de drop extra e +14% poções, −6% vida.',{drop:.1,pot:.14,hp:-.06}],
      ['Assassino Perfeito','+35% dano crítico e +14% dano em chefes, −5% crítico.',{critd:.35,boss:.14,crit:-.03}]]},
clerigo:{
 sec:[
 {n:'Fé',c:'#ffe08a',p:['hp','regen'],nm:['Oração','Bênção','Vigília','Penitência','Rosário'],mi:[M('hp',.04,'Corpo Abençoado'),M('regen',.002,'Graça Contínua: regenera vida'),M('pot',.1,'Água Benta')]},
 {n:'Luz',c:'#ffd24a',p:['atk','crit'],nm:['Raio de Sol','Fulgor','Lume','Aurora','Brilho Sagrado'],mi:[M('critd',.08,'Clarão Sagrado'),M('atk',.03,'Chama Divina'),M('exec',.05,'Purificar: mais dano em feridos')]},
 {n:'Escudo',c:'#7ab8ff',p:['def','dmgred'],nm:['Égide','Armadura de Luz','Baluarte','Bênção de Ferro','Muro Sagrado'],mi:[M('def',.04,'Escudo da Fé'),M('dmgred',.02,'Proteção Divina'),M('hp',.04,'Carne Abençoada')]},
 {n:'Cura',c:'#4ad8c0',p:['pot','regen'],nm:['Mãos Curadoras','Unguento','Fonte Sagrada','Ressurgir','Bálsamo'],mi:[M('pot',.12,'Poção Sagrada'),M('regen',.0025,'Luz Constante: regenera vida'),M('dcd',.06,'Passo Leve')]},
 {n:'Martelo',c:'#ff9a3a',p:['atk','boss'],nm:['Martelada','Marreta Santa','Julgamento','Fúria Divina','Peso do Pecado'],mi:[M('boss',.06,'Martelo dos Justos'),M('atk',.04,'Peso Sagrado'),M('cdr',.03,'Reza Rápida')]},
 {n:'Graça',c:'#c08aff',p:['cdr','drop'],nm:['Providência','Milagre','Oferenda','Dádiva','Presente do Céu'],mi:[M('cdr',.04,'Graça Rápida: recarga menor'),M('drop',.03,'Dízimo: chance de drop extra'),M('crit',.02,'Sorte Divina')]}],
 key:[['Mártir','+30% vida e regeneração, −8% ataque.',{hp:.3,regen:.005,atk:-.08}],
      ['Raio do Amanhecer','+22% ataque e +8% crítico, −10% defesa.',{atk:.22,crit:.08,def:-.1}],
      ['Bastião Sagrado','+25% defesa e −10% dano recebido, −10% vel. de ataque.',{def:.25,dmgred:.1,aspd:-.1}],
      ['Fonte da Vida','+40% eficácia de poção e +0,5% regen., −8% ataque.',{pot:.4,regen:.005,atk:-.08}],
      ['Martelo do Juízo','+22% dano em chefes e +10% ataque, −8% vel. de movimento.',{boss:.22,atk:.1,spd:-.08}],
      ['Santo Milagreiro','−18% recarga de habilidades e +8% drop, −8% defesa.',{cdr:.18,drop:.08,def:-.08}]]},
arqueiro:{
 sec:[
 {n:'Mira',c:'#ffd24a',p:['crit','critd'],nm:['Olho de Águia','Ponto Cego','Mira Firme','Tiro Certeiro','Respiração'],mi:[M('critd',.1,'Disparo Certeiro'),M('crit',.02,'Foco Profundo'),M('boss',.04,'Tiro no Alvo Grande')]},
 {n:'Rajada',c:'#c8e85a',p:['aspd','atk'],nm:['Corda Tensa','Chuva de Setas','Flecha Dupla','Metralha','Saraivada'],mi:[M('aspd',.04,'Mãos Rápidas'),M('atk',.03,'Ponta de Aço'),M('cdr',.03,'Aljava Cheia')]},
 {n:'Caça',c:'#e8c060',p:['drop','boss'],nm:['Rastreador','Troféu','Pele Rara','Caçador de Feras','Presa Cobiçada'],mi:[M('drop',.03,'Esfolar: chance de drop extra'),M('boss',.06,'Caça Grossa'),M('exec',.05,'Abate')]},
 {n:'Vento',c:'#6ae0ff',p:['spd','dcd'],nm:['Brisa','Passo Leve','Salto do Cervo','Ventania','Pluma'],mi:[M('dcd',.08,'Giro Acrobático: esquiva recarrega mais rápido'),M('spd',.03,'Pés de Vento'),M('dmgred',.02,'Esquiva Instintiva')]},
 {n:'Armadilha',c:'#ff7a5a',p:['exec','cdr'],nm:['Laço','Fosso','Mola de Aço','Isca','Emboscada'],mi:[M('exec',.06,'Armadilha Fatal: mais dano em feridos'),M('cdr',.03,'Preparo Rápido'),M('atk',.04,'Isca Explosiva')]},
 {n:'Natureza',c:'#6ae08a',p:['hp','regen'],nm:['Raiz Firme','Seiva','Casca de Pinho','Floresta Viva','Pele de Musgo'],mi:[M('pot',.1,'Chá de Ervas'),M('regen',.002,'Seiva Vital: regenera vida'),M('def',.04,'Casca Grossa')]}],
 key:[['Olho do Caçador','+35% dano crítico e +10% crítico, −10% vida.',{critd:.35,crit:.1,hp:-.1}],
      ['Chuva Infinita','+20% vel. de ataque e +10% ataque, −12% defesa.',{aspd:.2,atk:.1,def:-.12}],
      ['Predador Alfa','+22% dano em chefes e elites e +8% drop, −8% vida.',{boss:.22,drop:.08,hp:-.08}],
      ['Pés de Vento','+14% movimento e −25% recarga da esquiva, −8% ataque.',{spd:.14,dcd:.25,atk:-.08}],
      ['Mestre das Armadilhas','+16% dano em feridos e −15% recarga, −8% defesa.',{exec:.16,cdr:.15,def:-.08}],
      ['Filho da Floresta','+25% vida, +0,5% regen. e +14% poção, −8% ataque.',{hp:.25,regen:.005,pot:.14,atk:-.08}]]},
bardo:{
 sec:[
 {n:'Melodia',c:'#ff8ad0',p:['cdr','aspd'],nm:['Primeira Nota','Escala Alegre','Refrão','Canção Viva','Solo'],mi:[M('cdr',.04,'Afinação Rápida: recarga menor'),M('aspd',.03,'Dedilhado Veloz'),M('crit',.02,'Nota Perfeita')]},
 {n:'Acorde',c:'#ffd24a',p:['atk','critd'],nm:['Acorde Maior','Tríade','Cordas Altas','Sinfonia','Crescendo'],mi:[M('critd',.1,'Acorde Brilhante'),M('atk',.04,'Corda de Aço'),M('exec',.05,'Nota Final: mais dano em feridos')]},
 {n:'Ritmo',c:'#c8e85a',p:['spd','aspd'],nm:['Compasso','Batida Firme','Giro de Dança','Marcha','Síncope'],mi:[M('dcd',.08,'Pirueta: esquiva recarrega mais rápido'),M('spd',.03,'Passo de Dança'),M('aspd',.03,'Batida Rápida')]},
 {n:'Harmonia',c:'#6ae08a',p:['hp','regen'],nm:['Canto Calmo','Cantiga de Ninar','Voz Doce','Balada','Eco Suave'],mi:[M('hp',.04,'Voz Firme'),M('regen',.002,'Cantiga de Cura: regenera vida'),M('pot',.1,'Poção de Palco')]},
 {n:'Coro',c:'#7ab8ff',p:['pot','def'],nm:['Vozes Unidas','Escudo Sonoro','Muralha de Notas','Hino','Canto de Guerra'],mi:[M('def',.04,'Hino Protetor'),M('dmgred',.02,'Sustenido: menos dano recebido'),M('pot',.1,'Gole de Hidromel')]},
 {n:'Crescendo',c:'#c08aff',p:['boss','exec'],nm:['Estrondo','Clímax','Grande Final','Fortissimo','Cadência Final'],mi:[M('boss',.06,'Solo de Chefe'),M('drop',.03,'Gorjeta: chance de drop extra'),M('atk',.04,'Fortíssimo')]}],
 key:[['Virtuose','−18% recarga e +10% vel. de ataque, −10% defesa.',{cdr:.18,aspd:.1,def:-.1}],
      ['Sinfonia de Guerra','+22% ataque e +25% dano crítico, −12% vida.',{atk:.22,critd:.25,hp:-.12}],
      ['Dança Eterna','+14% movimento e −25% recarga da esquiva, −8% ataque.',{spd:.14,dcd:.25,atk:-.08}],
      ['Canto Restaurador','+25% vida, +0,5% regen. e +14% poção, −8% ataque.',{hp:.25,regen:.005,pot:.14,atk:-.08}],
      ['Coro Inabalável','+22% defesa e −8% dano recebido, −8% movimento.',{def:.22,dmgred:.08,spd:-.08}],
      ['Gran Finale','+22% dano em chefes e +14% em feridos, −6% defesa.',{boss:.22,exec:.14,def:-.06}]]}
};

/* ---------- geometria ---------- */
const RR=k=>34+60*k;             // raio do anel k
const RINGS=6;
const ang=c=>(c*60-90)*Math.PI/180;
function ringPos(k,i){const n=6*k,c=Math.floor(i/k)%6,t=(i%k)/k,a0=ang(c),a1=ang(c+1);
 const x0=Math.cos(a0)*RR(k),y0=Math.sin(a0)*RR(k),x1=Math.cos(a1)*RR(k),y1=Math.sin(a1)*RR(k);return{x:x0+(x1-x0)*t,y:y0+(y1-y0)*t};}

/* ---------- geração da árvore da classe ---------- */
const TP={guerreiro:['gf','gb','gc'],ladino:['la','lp','ls'],mago:['ma','ms','mt'],clerigo:['cc','cf','cp'],arqueiro:['aa','ac','ap'],bardo:['bh','bi','bm']};
function art(n,cls){const P=TP[cls]||TP.guerreiro;if(n.kind==='key')return 'assets/talents/'+P[n.sec%3]+'k.png';if(n.kind==='not'||n.kind==='hyb'||n.kind==='sub'){const h=(n.ring*5+n.idx*3+n.sec)%6+1;return 'assets/talents/'+P[n.sec%3]+h+'.png';}return null;}
const TREES={};
function build(cls){if(TREES[cls])return TREES[cls];const D=CL[cls]||CL.guerreiro,nodes={},list=[];
 const add=o=>{nodes[o.id]=o;list.push(o);o.nb=[];return o;};
 const link=(a,b)=>{if(a===b||!nodes[a]||!nodes[b]||nodes[a].nb.includes(b))return;nodes[a].nb.push(b);nodes[b].nb.push(a);};
 add({id:'c',kind:'start',x:0,y:0,sec:-1,fx:{},nm:'Origem',ds:'Ponto de partida da árvore. Todos os caminhos começam aqui.',st:['hp']});
 const id=(k,i)=>'r'+k+'_'+((i%(6*k)+6*k)%(6*k));
 let notN=0;
 for(let k=1;k<=RINGS;k++)for(let i=0;i<6*k;i++){
  const c=Math.floor(i/k)%6,t=i%k,pole=t===0,p=ringPos(k,i),S=D.sec[c],Sp=D.sec[(c+5)%6];
  if(!(k===RINGS&&pole)){p.x+=Math.sin(k*12.9+i*78.2)*7;p.y+=Math.cos(k*7.1+i*39.3)*7;}
  const o={id:id(k,i),x:p.x,y:p.y,ring:k,idx:i,sec:c};
  const tk=Object.keys(ST);
  const pk=S.p[0],sk=S.p[1];
  if(k===RINGS&&pole){ // pedra angular
   const K=D.key[c];o.kind='key';o.nm=K[0];o.ds=K[1];o.fx=K[2];o.st=Object.keys(K[2]).filter(q=>K[2][q]>0).slice(0,2);o.sec=c;
  }else if(pole&&(k===2||k===4||k===5)){ // híbrido: mistura os dois setores vizinhos
   const a=Sp.p[1],b=S.p[0];o.kind='hyb';o.nm=(Sp.n+' + '+S.n);o.fx={};o.fx[a]=ST[a].v*(k===5?2.2:1.4);o.fx[b===a?S.p[1]:b]=ST[b===a?S.p[1]:b].v*(k===5?2.2:1.4);o.st=Object.keys(o.fx);o.sec2=(c+5)%6;
   o.ds='Híbrido de '+Sp.n+' e '+S.n+'.';
  }else if(pole){ // polos simples (ring 1,3,6 já cobertos): pequeno duplo
   o.kind='dual';o.fx={};o.fx[pk]=ST[pk].v*(1+k*.12);o.fx[sk]=ST[sk].v*(1+k*.12);o.st=[pk,sk];o.nm=S.n+' · '+ST[pk].n.split(' ')[0];o.sec2=(c+5)%6;
  }else{
   const notable=(k===3&&t===1)||(k===4&&t===2)||(k===5&&t===3)||(k===6&&(t===2||t===4));
   if(notable){
    const q=notN%5;const mi=S.mi[q%3];o.kind='not';o.nm=S.nm[q];o.fx={};const sc=1+k*.18;o.fx[pk]=ST[pk].v*sc*1.4;o.fx[sk]=ST[sk].v*sc*1.1;
    o.mini=mi;if(o.fx[mi.k]!=null&&mi.k!==pk&&mi.k!==sk)o.fx[mi.k]=mi.v;else if(mi.k===pk||mi.k===sk)o.fx[mi.k]=(o.fx[mi.k]||0)+mi.v;else o.fx[mi.k]=mi.v;
    o.st=[pk,sk];o.ds=mi.t;notN++;
   }else if((i*7+k*3+c)%3===0){ // duplo
    o.kind='dual';o.fx={};const sc=1+k*.1;o.fx[pk]=ST[pk].v*sc*.8;o.fx[sk]=ST[sk].v*sc*.8;o.st=[pk,sk];o.nm=S.n+' (duplo)';
   }else{
    const kk=(i+k)%2?pk:sk;o.kind='small';o.fx={};o.fx[kk]=ST[kk].v*(1+k*.1);o.st=[kk];o.nm=S.n+' · '+ST[kk].n;
   }
  }
  add(o);}
 // ligações: anel + para dentro
 for(let k=1;k<=RINGS;k++)for(let i=0;i<6*k;i++){
  const skip=k>=3&&((i*5+k*11)%7===0)&&(i%k!==0);   // alguns arcos ficam abertos (mais caminhos alternativos)
  if(!skip)link(id(k,i),id(k,i+1));
  if(k===1)link(id(1,i),'c');
  else{const j=Math.round(i*(k-1)/k);link(id(k,i),id(k-1,j));
   if(i%k!==0&&k>2){const j2=Math.floor(i*(k-1)/k);if(j2!==j)link(id(k,i),id(k-1,j2));}}
 }
 // subclasses (trancadas): saem de dois polos do anel externo
 const SB=(typeof SUBS!=='undefined'&&SUBS[cls])||[];
 SB.forEach((sb,j)=>{const c=1+j*3,p=ringPos(RINGS,c*RINGS),a=ang(c),R=RR(RINGS+1.15);
  const o=add({id:'s'+j,x:Math.cos(a)*R,y:Math.sin(a)*R,ring:RINGS+1,idx:c,sec:c,kind:'sub',sub:sb.id,nm:'Mestre '+sb.nome,ds:sb.desc,fx:{},st:Object.keys(sb.m||{}).slice(0,2)});
  const mm=sb.m||{};for(const k in mm)if(ST[k])o.fx[k]=mm[k]*.5;if(!Object.keys(o.fx).length){o.fx.atk=.05;o.st=['atk'];}
  link('s'+j,id(RINGS,c*RINGS));});
 return TREES[cls]={nodes,list,D};}

/* ---------- estado ---------- */
const own=()=>(SAVE.tr&&typeof SAVE.tr==='object')?SAVE.tr:(SAVE.tr={});
const isAl=(id)=>id==='c'||!!own()[id];
const spent=()=>Object.keys(own()).filter(k=>k!=='c').length;
window.ptTotal=()=>SAVE.lv<2?0:(SAVE.lv-1)+Math.floor(SAVE.lv/4);
window.ptSpent=spent;
window.ptPoints=()=>window.ptTotal()-spent();
function tree(){return build(SAVE.cls);}
function allocatable(n){if(isAl(n.id))return false;if(n.kind==='sub'&&SAVE.sub!==n.sub)return false;return n.nb.some(isAl);}
function whyNot(n){if(isAl(n.id))return 'Já alocado';if(n.kind==='sub'&&SAVE.sub!==n.sub)return SAVE.sub?'Outra subclasse':'Requer a subclasse (Nv10)';return '';}
/* menor caminho de nós não alocados até o alocado mais próximo */
function pathTo(id){const T=tree(),N=T.nodes;if(isAl(id))return[];const prev={},q=[id];prev[id]=null;
 while(q.length){const u=q.shift();for(const v of N[u].nb){if(v in prev)continue;if(N[v].kind==='sub'&&SAVE.sub!==N[v].sub)continue;prev[v]=u;if(isAl(v)){const p=[];let x=u;while(x!==null){p.push(x);x=prev[x];}return p;}q.push(v);}}
 return null;}
function connectedWithout(id){const T=tree(),N=T.nodes,al=Object.keys(own()).filter(k=>k!==id&&k!=='c'),seen={c:1},q=['c'];
 while(q.length){const u=q.shift();for(const v of N[u].nb){if(seen[v]||v===id||!own()[v])continue;seen[v]=1;q.push(v);}}
 return al.every(k=>seen[k]);}

/* ---------- efeitos no jogo ---------- */
Object.assign(TCAP,{atk:.9,def:.9,hp:1.2,spd:.4,aspd:.5,crit:.4,critd:1.4,dmgred:.4,regen:.04,pot:.8,cdr:.35,dcd:.5,exec:.4,boss:.5,drop:.25});
window.ptCalc=function(){const o=own(),N=tree().nodes;TF={};for(const id in o){const n=N[id];if(!n)continue;if(n.kind==='sub'&&SAVE.sub!==n.sub)continue;for(const k in n.fx)TF[k]=(TF[k]||0)+n.fx[k];}
 for(const k in TCAP)if(TF[k]>TCAP[k])TF[k]=TCAP[k];};
function refresh(){tfCalc();if(G.hero)recalcHero(true);writeSave();badge();renderPan();}
function alloc(id,silent){const T=tree(),n=T.nodes[id];if(!n||!allocatable(n)){sfx('ui_denied',.5);return false;}if(ptPoints()<=0){sfx('ui_denied',.5);toast('Sem pontos de passiva',1000);return false;}own()[id]=1;if(!silent){sfx('ui_confirm',.7);refresh();}return true;}
function allocPath(id){const p=pathTo(id);if(!p){sfx('ui_denied',.5);return;}if(p.length>ptPoints()){toast('Faltam '+(p.length-ptPoints())+' ponto(s)',1200);sfx('ui_denied',.5);return;}
 const N=tree().nodes;for(const x of p.slice().reverse()){if(N[x].kind==='sub'&&SAVE.sub!==N[x].sub){sfx('ui_denied',.5);return;}own()[x]=1;}sfx('ui_confirm',.7);refresh();}
function dealloc(id){const cost=10*SAVE.lv;if(!isAl(id)||id==='c')return;if(!connectedWithout(id)){toast('Isso desconectaria outros nós',1300);sfx('ui_denied',.5);return;}
 if(SAVE.gold<cost){toast('Ouro insuficiente ('+cost+')',1200);sfx('ui_denied',.5);return;}SAVE.gold-=cost;delete own()[id];sfx('ui_confirm',.6);refresh();}
function resetAll(){const cost=50*SAVE.lv;if(!spent())return;gConfirm('Devolve todos os pontos da árvore. Custa '+cost+' de ouro.',{title:'Redefinir passivas?',ok:'Redefinir',no:'Cancelar'}).then(ok=>{if(!ok)return;if(SAVE.gold<cost){toast('Ouro insuficiente',1200);sfx('ui_denied');return;}SAVE.gold-=cost;SAVE.tr={};PT.sel=null;sfx('ui_confirm');refresh();});}

/* ---------- migração: talentos antigos viram pontos de árvore (reembolso automático) ---------- */
window.ptMigrate=function(){if(SAVE.trv===1)return;SAVE.trv=1;SAVE.tl={};SAVE.tr=SAVE.tr||{};};

/* ---------- interface ---------- */
const css=`.ptw{position:relative;height:min(66vh,640px);margin:4px 0;border:2px solid #3a4258;border-radius:6px;overflow:hidden;background:#07090f;touch-action:none;user-select:none}
.ptw svg{width:100%;height:100%;display:block}.ptw .zb{position:absolute;right:6px;top:6px;display:flex;flex-direction:column;gap:4px}.ptw .zb button{width:32px;height:32px;font-size:18px;background:#10151f;border:2px solid #556;color:#ffd24a;border-radius:4px;padding:0}
.ptw .ln{stroke:#2b3348;stroke-width:2.4;stroke-linecap:round}.ptw .ln.on{stroke-width:4}.ptw .ln.av{stroke:#8a7a4a;stroke-dasharray:3 4}.ptw .ln.pa{stroke:#ffe08a;stroke-width:4}
.ptw .nc{fill:#10151f;stroke:#445;stroke-width:2.5}.ptw .nc.on{fill:#1b2234}.ptw .nc.av{stroke:#ffd24a}.ptw .nc.sel{stroke:#fff;stroke-width:3.5}.ptw .nc.pa{stroke:#ffe08a}.ptw .lk{opacity:.4}
.ptw text.sl{font:700 9px 'Pixelify Sans',sans-serif;fill:#aab;text-anchor:middle;pointer-events:none}.ptw text.nm{font-family:'Pixelify Sans',sans-serif;font-weight:700;fill:#f2e6c0;text-anchor:middle;paint-order:stroke;stroke:#0a0d14;stroke-width:3px;pointer-events:none}.ptw text.rt{font:700 8px 'Pixelify Sans',sans-serif;fill:#ffd24a;text-anchor:middle;pointer-events:none}
.pts{display:flex;flex-wrap:wrap;gap:4px;margin:4px 0}.pts span{font:11px 'Pixelify Sans',sans-serif;background:#10151f;border:1px solid #3a4258;border-radius:3px;padding:2px 5px;color:#cfd6e6}.pts span img{width:11px;height:11px;image-rendering:pixelated;vertical-align:-1px;margin-right:3px}
.ptd{display:flex;gap:8px;align-items:center;background:#0e131d;border:2px solid #3a4258;border-radius:6px;padding:8px;margin:4px 0;min-height:96px;height:auto!important;overflow:visible!important;flex:none}.ptd .ic{flex:none;width:46px;height:46px;border-radius:50%;border:2px solid var(--bc,#667);background:#10151f;display:flex;align-items:center;justify-content:center;gap:1px}.ptd .ic img{width:20px;height:20px;image-rendering:pixelated}
.ptd .tx{flex:1;min-width:0}.ptd b{display:block;font-size:13px;color:#ffe08a}.ptd .tp{display:block;font-size:10px;color:#8a95ad;text-transform:uppercase;letter-spacing:.5px}.ptd p{margin:2px 0 0;font-size:11px;color:#cfd6e6}.ptd .mi{color:#9be06a}.ptd .wn{color:#ff9a7a}
.ptd button{flex:none;font:12px 'Pixelify Sans',sans-serif;padding:8px 10px;background:#243a24;border:2px solid #6ae08a;color:#fff;border-radius:4px}.ptd button[data-d]{background:#3a2424;border-color:#e08a6a}.ptd button:disabled{opacity:.45;border-color:#556;background:#1a1f2b}`;
(function(){const s=document.createElement('style');s.textContent=css;document.head.appendChild(s);})();

(function(){const c=document.createElement('style');c.textContent=`.psb{display:grid;grid-template-columns:repeat(6,1fr);gap:4px;margin:4px 0}.psb div{min-width:0}.psb span{display:block;font:10px 'Pixelify Sans',sans-serif;text-align:center;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.psb i{display:block;height:4px;background:#1a2030;border:1px solid #2b3348}.psb u{display:block;height:100%}details.pts summary{font:11px 'Pixelify Sans',sans-serif;color:#aab;cursor:pointer;padding:2px}`;document.head.appendChild(c);})();
const KIND={start:'Origem',small:'Passiva',dual:'Passiva dupla',hyb:'Híbrido',not:'Notável',key:'Pedra angular',sub:'Subclasse'};
const RAD={start:15,small:11,dual:13,hyb:14,not:17,key:21,sub:19};
function iconHTML(n,col){const sts=n.st&&n.st.length?n.st:['atk'];return `<div class="ic" style="--bc:${col}">${sts.slice(0,2).map(k=>`<img src="${glyph(k,ST[k]?ST[k].c:'#fff')}">`).join('')}</div>`;}

function fit(vw,vh){const R=RR(RINGS+1.6);PT.sc=Math.min(vw,vh)/(R*2)*1.2;PT.vx=0;PT.vy=0;}
function svgHTML(vw,vh){const T=tree(),N=T.nodes,sel=PT.sel,pth=sel?(pathTo(sel)||[]):[],pset={};pth.forEach(x=>pset[x]=1);
 const vbw=vw/PT.sc,vbh=vh/PT.sc,vx=PT.vx-vbw/2,vy=PT.vy-vbh/2,u=1/PT.sc;
 let h=`<svg id="ptsvg" viewBox="${vx} ${vy} ${vbw} ${vbh}"><defs>`;
 T.D.sec.forEach((S,c)=>{h+=`<radialGradient id="pg${c}"><stop offset="0" stop-color="${S.c}" stop-opacity=".22"/><stop offset="1" stop-color="${S.c}" stop-opacity="0"/></radialGradient>`;});
 h+='</defs>';
 T.D.sec.forEach((S,c)=>{const a=ang(c+.5),r=RR(3.6);h+=`<circle cx="${(Math.cos(a)*r).toFixed(0)}" cy="${(Math.sin(a)*r).toFixed(0)}" r="${RR(4.4)}" fill="url(#pg${c})"/>`;});
 T.D.sec.forEach((S,c)=>{const a=ang(c+.5),r=RR(RINGS+2.3);h+=`<text class="sl" x="${Math.cos(a)*r}" y="${Math.sin(a)*r+3}" style="fill:${S.c};font-size:${(8*u).toFixed(1)}px;opacity:.85">${S.n.toUpperCase()}</text>`;});
 const drawn={};
 T.list.forEach(n=>n.nb.forEach(m=>{const k=n.id<m?n.id+'|'+m:m+'|'+n.id;if(drawn[k])return;drawn[k]=1;const a=n,b=N[m],on=isAl(a.id)&&isAl(b.id),av=!on&&((isAl(a.id)&&allocatable(b))||(isAl(b.id)&&allocatable(a))),pa=pset[a.id]&&(pset[b.id]||isAl(b.id))||pset[b.id]&&isAl(a.id);
  let st='';if(on){const ca=(T.D.sec[a.sec]||T.D.sec[0]).c,cb=(T.D.sec[b.sec]||T.D.sec[0]).c;st=`stroke:${a.sec===b.sec||a.sec<0?cb:ca}`;}
  h+=`<line class="ln ${on?'on':''} ${av?'av':''} ${pa?'pa':''}" x1="${a.x.toFixed(1)}" y1="${a.y.toFixed(1)}" x2="${b.x.toFixed(1)}" y2="${b.y.toFixed(1)}" style="${st}"/>`;}));
 T.list.forEach(n=>{const al=isAl(n.id),av=allocatable(n),S=T.D.sec[n.sec]||T.D.sec[0],lock=n.kind==='sub'&&SAVE.sub!==n.sub,r=RAD[n.kind]||11,x=n.x.toFixed(1),y=n.y.toFixed(1),im=art(n,SAVE.cls);
  const sts=(n.st&&n.st.length?n.st:['atk']).slice(0,2),op=al||av?1:.5;
  const edge=sel===n.id?'#fff':pset[n.id]?'#ffe08a':av?'#ffd24a':al?S.c:(n.kind==='small'||n.kind==='dual'?'#3d4660':S.c);
  h+=`<g data-n="${n.id}" class="${lock?'lk':''}" ${al?`style="filter:drop-shadow(0 0 ${n.kind==='small'?3:6}px ${S.c})"`:''}>`;
  const fill=al?'#242b40':'#0f1420';
  if(n.kind==='key'){const q=r+3;h+=`<polygon points="${x},${(n.y-q).toFixed(1)} ${(n.x+q).toFixed(1)},${y} ${x},${(n.y+q).toFixed(1)} ${(n.x-q).toFixed(1)},${y}" fill="${fill}" stroke="${edge}" stroke-width="3"/>`;}
  else if(n.kind==='hyb'){const pts=[0,1,2,3,4,5].map(i=>{const a=i*Math.PI/3+Math.PI/6;return (n.x+Math.cos(a)*(r+1)).toFixed(1)+','+(n.y+Math.sin(a)*(r+1)).toFixed(1);}).join(' ');h+=`<polygon points="${pts}" fill="${fill}" stroke="${edge}" stroke-width="2.8"/>`;}
  else h+=`<circle class="nc ${al?'on':''}" cx="${x}" cy="${y}" r="${r}" fill="${fill}" style="stroke:${edge};stroke-width:${n.kind==='not'?3.2:2.4}"/>`+(n.kind==='not'?`<circle cx="${x}" cy="${y}" r="${r+3.5}" fill="none" stroke="${S.c}" stroke-width="1.2" opacity="${al?.95:.4}"/>`:'');
  if(im){const w=n.kind==='key'?r*1.5:r*1.5;h+=`<image href="${im}" x="${(n.x-w/2).toFixed(1)}" y="${(n.y-w/2).toFixed(1)}" width="${w.toFixed(1)}" height="${w.toFixed(1)}" style="image-rendering:pixelated;opacity:${op}"/>`;}
  else{const gs=sts.length>1?r*.62:r*1.05;sts.forEach((k,i)=>{const gx=n.x+(sts.length>1?(i?1:-1)*gs*.52:0)-gs/2;h+=`<image href="${glyph(k,ST[k]?ST[k].c:'#fff')}" x="${gx.toFixed(1)}" y="${(n.y-gs/2).toFixed(1)}" width="${gs.toFixed(1)}" height="${gs.toFixed(1)}" style="image-rendering:pixelated;opacity:${op}"/>`;});}
  if(n.mini)h+=`<circle cx="${(n.x+r*.8).toFixed(1)}" cy="${(n.y-r*.8).toFixed(1)}" r="3.4" fill="#9be06a" stroke="#0b0e16" stroke-width="1"/>`;
  if(n.kind==='key'||(n.kind==='not'&&PT.sc>1.1)||n.kind==='sub')h+=`<text class="nm" x="${x}" y="${(n.y+r+12*u+3).toFixed(1)}" style="font-size:${(8.5*u).toFixed(1)}px">${n.nm}</text>`;
  h+='</g>';});
 return h+'</svg>';}

window.renderTalents=function(B){ptMigrate();const T=tree(),N=T.nodes,pts=ptPoints();if(PT.cls!==SAVE.cls){PT.cls=SAVE.cls;PT.sel=null;PT.fit=true;}
 // resumo
 const tot={};Object.keys(own()).concat(['c']).forEach(id=>{const n=N[id];if(!n||(n.kind==='sub'&&SAVE.sub!==n.sub))return;for(const k in n.fx)tot[k]=(tot[k]||0)+n.fx[k];});
 const chips=Object.keys(tot).filter(k=>ST[k]&&Math.abs(tot[k])>1e-6).map(k=>`<span><img src="${glyph(k,ST[k].c)}">${fxText({[k]:tot[k]})}</span>`).join('')||'<span>Nenhum bônus ainda</span>';
 let h=`<div class="avl"><span>Pontos de passiva · ${spent()} usados · 1 por nível (+1 a cada 4)</span><b>${pts}</b></div>`;
 const sc6=[0,0,0,0,0,0];Object.keys(own()).forEach(id=>{const n=N[id];if(n&&n.sec>=0&&n.sec<6)sc6[n.sec]++;});const mx=Math.max(8,...sc6);
 h+=`<div class="psb">${T.D.sec.map((S,c)=>`<div><span style="color:${S.c}">${S.n}</span><i><u style="width:${sc6[c]/mx*100}%;background:${S.c}"></u></i></div>`).join('')}</div>`;
 h+=`<div class="ptw" id="ptw"></div><div class="ptd" id="ptd"></div><details class="pts"><summary>Bônus totais</summary>${chips}</details>`;
 h+=`<div class="acts"><button data-ptr="1" ${spent()?'':'disabled'}>Redefinir passivas (${50*SAVE.lv} ouro)</button></div>`;
 B.innerHTML=h;
 const W=$('ptw'),vw=W.clientWidth||340,vh=W.clientHeight||420;if(PT.fit){fit(vw,vh);PT.fit=false;}
 const paint=()=>{W.innerHTML=svgHTML(vw,vh)+`<div class="zb"><button data-z="1">+</button><button data-z="-1">−</button><button data-z="0">⌖</button></div>`;};
 const detail=()=>{const d=$('ptd');const n=PT.sel&&N[PT.sel];if(!n){d.innerHTML='<div class="tx"><b>Toque num nó</b><p>Arraste para mover, use +/− (ou dois dedos) para o zoom. Nós com ponto verde têm mini passiva; os maiores com anel são notáveis e pedras angulares.</p></div>';return;}
  const S=T.D.sec[n.sec]||T.D.sec[0],al=isAl(n.id),why=whyNot(n),p=al?[]:pathTo(n.id),cost=p?p.length:0;
  const eff=Object.keys(n.fx).map(k=>fxText({[k]:n.fx[k]})).filter(Boolean).join('<br>');
  let btn='';if(n.id==='c'){}else if(al)btn=`<button data-d="${n.id}">Remover (${10*SAVE.lv}g)</button>`;else if(!why&&p&&cost>0)btn=`<button data-a="${n.id}" ${cost<=pts?'':'disabled'}>${cost>1?'Alocar caminho':'Alocar'} (${cost})</button>`;
  d.innerHTML=iconHTML(n,S.c)+`<div class="tx"><span class="tp">${KIND[n.kind]}${n.sec>=0&&n.kind!=='sub'?' · '+S.n:''}</span><b>${n.nm}</b><p>${eff}</p>${n.mini?`<p class="mi">◆ ${n.mini.t}</p>`:n.kind==='sub'||n.kind==='start'?`<p>${n.ds||''}</p>`:''}${why&&!al?`<p class="wn">${why}</p>`:''}${!why&&!al&&p===null?'<p class="wn">Sem caminho</p>':''}</div>`+btn;
  d.querySelectorAll('[data-a]').forEach(e=>e.onclick=()=>n.kind==='sub'||cost>1?allocPath(n.id):alloc(n.id));d.querySelectorAll('[data-d]').forEach(e=>e.onclick=()=>dealloc(n.id));};
 paint();detail();
 // interação
 let drag=null,pts2={},pinch=0,moved=0;
 W.onpointerdown=e=>{pts2[e.pointerId]={x:e.clientX,y:e.clientY};moved=0;drag={x:e.clientX,y:e.clientY,vx:PT.vx,vy:PT.vy};try{W.setPointerCapture(e.pointerId)}catch(_){ }};
 W.onpointermove=e=>{if(!pts2[e.pointerId])return;pts2[e.pointerId]={x:e.clientX,y:e.clientY};const ids=Object.keys(pts2);
  if(ids.length>=2){const a=pts2[ids[0]],b=pts2[ids[1]],dd=Math.hypot(a.x-b.x,a.y-b.y);if(pinch){PT.sc=Math.max(.35,Math.min(3.5,PT.sc*dd/pinch));moved=9;paint();}pinch=dd;return;}
  pinch=0;if(!drag)return;const dx=e.clientX-drag.x,dy=e.clientY-drag.y;if(Math.abs(dx)+Math.abs(dy)>5)moved=9;if(moved){PT.vx=drag.vx-dx/PT.sc;PT.vy=drag.vy-dy/PT.sc;paint();}};
 const up=e=>{const was=pts2[e.pointerId];delete pts2[e.pointerId];pinch=0;if(!Object.keys(pts2).length){const tap=!moved&&was;drag=null;
   if(tap){const g=document.elementFromPoint(e.clientX,e.clientY),gg=g&&g.closest&&g.closest('[data-n]');if(gg&&W.contains(gg)){PT.sel=gg.dataset.n;sfx('ui_click',.5);paint();detail();}else{const z=g&&g.closest&&g.closest('[data-z]');if(z){const v=+z.dataset.z;if(v===0)fit(vw,vh);else PT.sc=Math.max(.35,Math.min(3.5,PT.sc*(v>0?1.3:1/1.3)));paint();}}}}};
 W.onpointerup=up;W.onpointercancel=e=>{delete pts2[e.pointerId];drag=null;pinch=0;};

 W.onwheel=e=>{e.preventDefault();PT.sc=Math.max(.35,Math.min(3.5,PT.sc*(e.deltaY<0?1.15:1/1.15)));paint();};
 const rb=B.querySelector('[data-ptr]');if(rb)rb.onclick=resetAll;
};
window.ptTree=tree;
})();
