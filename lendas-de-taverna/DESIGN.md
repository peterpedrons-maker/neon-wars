# Lendas de Taverna — documento de design

Registro vivo das decisões de design do projeto. Objetivo: ninguém (eu ou uma
sessão futura) precisa reconstruir o histórico de conversa pra saber o que já
foi decidido, o que está pendente, e por quê. Atualizar este arquivo sempre
que uma decisão de fundação for tomada ou revista.

## Visão geral

RPG tático de grupo, estilo **campanha contínua** (FFT + Darkest Dungeon), não
roguelite. O jogador recruta um elenco de heróis que persiste pra sempre entre
missões — heróis não são descartados ao fim de uma run, equipamento não
reseta, e o progresso (elenco, ouro, itens) fica salvo no aparelho.

Arquivo único (`index.html`), sem build, Three.js r128 + GSAP via CDN. Jogo
publicado em `https://peterpedrons-maker.github.io/neon-wars/lendas-de-taverna/`.

### Decisão histórica importante

O projeto **começou como roguelite** (grupo descartável por run, equipamento
resetado a cada run — de propósito, pra impedir que um item achado numa fase
avançada trivializasse o replay de uma fase inicial). Essa decisão foi
**revertida**: o jogo virou campanha contínua porque isso combina melhor com
o objetivo de ter itens únicos de verdade e personagens que o jogador
desenvolve com apego ao longo do tempo. Em campanha contínua esse problema
original quase não existe (você não "rejoga a fase 1 de novo" depois de ficar
forte, você segue em frente).

## Sistemas já implementados

### Elenco persistente
- Salvo em `localStorage` (chave `lendas_save_v1`), **só neste navegador** —
  sem conta, sem nuvem, sem sincronização entre aparelhos. Limpar os dados do
  site apaga tudo. Decisão consciente: aceito o risco por enquanto, sem
  export/import de save por ora.
- Limite de elenco: **10 heróis** (`ROSTER_CAP`). Recrutar na Taverna soma um
  herói ao elenco pra sempre (não é mais "contratar pra essa run").
- Cada missão usa até **5 heróis ativos** escolhidos do elenco; o resto fica
  de banco.
- Heróis de banco ganham **20% do XP médio do grupo ativo** por missão
  (`BENCH_XP_SHARE` — já reduzido de 50% a pedido explícito, pra não deixar
  o jogador num ponto onde só 5 heróis estão fortes e perder um pesa demais).
  Existe um campo `benchXpBonus` por herói, hoje sempre 0 — reservado pra
  quando equipamento/habilidade puder aumentar esse ganho.
- **Nível individual por herói**, calculado a partir do XP total acumulado
  (`xpTotal`, nunca reseta) via curva de custo crescente por nível
  (`levelForXp`). Cada nível dá +1 PV máx — **placeholder deliberadamente
  simples**, vai ser recalibrado quando a árvore de habilidades/gatilhos
  existir de verdade.
- Existe também **XP de classe** (`lendas_classxp_v1`, `loadClassXP`),
  acumulado por classe só, mas **ainda sem nenhum efeito mecânico** — ideia
  original era desbloquear habilidades de classe com isso (ver seção de
  habilidades abaixo).

### Equipamento
- **8 posições por herói**: arma, mão secundária, cabeça, corpo, mãos, pés,
  2 acessórios (slot genérico `accessory`, preenche o primeiro livre).
- Classes de arma de duas mãos (**Mago, Arqueiro, Bardo**) não usam mão
  secundária.
- **80 itens hoje em código**, fixos, catálogo estático — essa é a v1,
  implementada antes da conversa sobre itens estilo ARPG. **Já foi
  substituída por uma especificação nova (v2), ainda não implementada em
  código** — ver `EQUIPAMENTOS.md` pro desenho completo: 3 eixos (tier,
  raridade, atributo sorteado), itens não-lendários rolam stats no
  momento do drop em vez de serem fixos, arma fica de fora da rolagem
  (curada por família), lendário é escrito à mão. Até essa v2 ser
  implementada, o jogo publicado continua rodando a v1.
- Equipamento **não reseta mais** (era a regra antiga de quando o jogo era
  roguelite). O que sai de um herói vai pro **Cofre da Guilda**, estoque
  compartilhado permanente, prédio próprio na vila com inventário em grade
  (estilo PoE/Diablo), filtrável por slot.

### Progressão e nível máximo
- **Nível máximo: 60.**
- **12 tiers de item**, travados por nível, intervalo sempre crescente (nunca
  reacelera perto do fim): nível 1, 3, 6, 10, 15, 21, 28, 36, 42, 48, 54, 60.
  O clímax de progressão é o próprio nível 60, não uma crista no meio.
- Do tier 9 ao 12 (nível 42-60): em vez de um pool genérico de opções,
  **múltiplas dungeons de endgame distintas**, cada uma com tabela de drop e
  1-2 itens Lendários próprios — motivo concreto pra farmar uma dungeon
  específica, não a outra. Lista de dungeons ainda não escrita.

### Atributos primários (feito — `ATTR_NAMES`/`ATTR_BASE`/`recomputeAttrBonus`)
5 atributos — **Força, Destreza, Inteligência, Vitalidade, Fé** — alimentam
dano/PV/crítico por fórmula (nunca ATQ/DEF brutos diretamente, ver disciplina
de combate abaixo). Implementado com valor base por classe (`ATTR_BASE`), o
atributo primário crescendo a cada level up (`CLASS_PRIMARY`/`applyLevelUps`)
e salvo/carregado no save. Mapeamento por classe base abaixo — a coluna de
subclasse ainda é só decisão de design, entra quando subclasses existirem no
código (passo 8 do roadmap):

| Classe | Atributo(s) base | Onde a subclasse diverge |
|---|---|---|
| Guerreiro | Força | Cavaleiro ganha +Vitalidade |
| Ladino | Destreza | Armadilheiro ganha +Inteligência |
| Mago | Inteligência | Geomante ganha +Vitalidade |
| Clérigo | Fé | Templário ganha +Força |
| Arqueiro | Destreza | — |
| Bardo | Inteligência + Destreza | ambas subclasses herdam os dois |
| Paladino | Força + Fé | ambas subclasses herdam os dois |
| Monge | Destreza (Asceta) | Quebra-ossos troca pra Força |

Atributos descartados conscientemente: **Precisão e Evasão** — seriam ATQ e
DEF renomeados, não acrescentam nada nesse sistema (ver disciplina de
combate). Parado em 5 atributos de propósito — cada um a mais multiplica o
trabalho de itemização por todo o catálogo.

### Disciplina de combate (por que o d20 não quebra com 12 tiers de item)
Regra central pra qualquer item/fórmula futura: **ATQ e DEF (o que entra na
rolagem de 1-20) crescem pouco e devagar pelos 12 tiers; dano, PV máximo e
limiar/dano de crítico crescem muito**. Isso existe porque, num sistema de
d20 puro, o que importa pro dado continuar relevante não é o tamanho dos
números — é a distância entre o total de ataque e a DEF do alvo continuar
proporcional. Se ATQ de equipamento crescesse livre, um personagem de tier
alto passaria a acertar sempre, matando a tensão exatamente no endgame, onde
o objetivo é o oposto (dungeons difíceis de verdade). Fórmulas de referência
e tabela de exemplo (tier 1 ao 12) estão em `EQUIPAMENTOS.md`.

Opções descartadas conscientemente nessa conversa:
- **Rolar múltiplos d20 pra acerto** (ex.: 2d20) — muda a distribuição de
  probabilidade (dados somados tendem ao meio, perdendo a imprevisibilidade
  do d20 puro) e não é como nem o D&D de verdade escala — lá, quem cresce é
  o dado de **dano**, não a quantidade de dados de **acerto**.
- **Remover o dado e usar fórmula determinística (ATQ − DEF = dano)** — sem
  aleatoriedade, a diferença de atributo vira uma parede dura: ou acerta
  sempre, ou não causa dano nenhum, sem meio-termo. Isso seria pior
  exatamente no cenário que motivou a pergunta (dungeon difícil de endgame),
  não melhor. Mantido o d20.

### Stats secundários novos
- **Dano Crítico** — multiplicador de dano num acerto crítico (hoje crítico
  só dobra os dados, sempre ×2; isso dá um dial adicional de item).
  **Decidido, não implementado.**
- ~~**Resistência Mágica**~~ — **feito.** `defMag` existe como stat separado
  do DEF físico (`baseDefMag(def)`, hoje um placeholder `def × 0.7` derivado
  do DEF *base* da classe/ficha — armadura física não entra nessa conta, só
  entrará quando o motor de item v2 permitir rolar Resistência Mágica em
  equipamento, passo 11 do roadmap). Cada ataque é marcado físico ou mágico
  via `CLASSES[cls].magico` / `ENEMIES[kind].magico` (hoje só Mago e o Xamã
  Goblin); `attack()` usa `defMag` em vez de `def` contra um atacante mágico,
  e a rolagem mostra "RES" em vez de "DEF". Paladino e a magia ofensiva do
  Clérigo (quando existirem) só precisam da mesma flag `magico`.

### Habilidades: cooldown por turno, não mana (decidido, não implementado)
Quando o sistema de gatilhos/habilidades existir, o recurso que limita uso
é **cooldown medido em turnos** ("pronta a cada 3 turnos"), não um pool de
mana. Motivo: o combate é automático (IA decide via gatilho), e mana é um
recurso que só compensa quando é o jogador gerenciando momento a momento —
aqui quem "gerenciaria" seria a IA, adicionando complexidade sem o jogador
sentir a gestão. Cooldown por turno é mais simples de implementar, de
mostrar na tela (encaixa na lista de turno que já existe) e pra IA calcular.

### Campanha em atos (estrutura)
- 5 atos, cada um com faixa de nível e um chefe no fim: I Vale de Brumavale
  (Nv. 1–12, Ogro), II Ruínas Esquecidas (12–25, Minotauro), III Cavernas de
  Magma (25–40, Troll), IV Picos Gelados (40–52, Rei Esqueleto), V Cripta Real
  (52–60, Vampiro Senhor). Hoje só o Ato I tem mapas (os 5 que já existiam);
  os outros aparecem travados no Quadro de Missões ("em breve") e ganham mapas
  um por vez.
- Cada mapa tem `ato` e `nivel` recomendado; o briefing avisa quando o grupo
  está abaixo do nível. Mapas se liberam em sequência (progresso salvo).
- Uma run segue pelos mapas do mesmo ato; vencer o chefe fecha o ato. O Modo
  Interminável fica desligado até a campanha estar completa.
- **Ato II (feito):** bioma Ruínas (piso de pedra, colunas quebradas, muros
  baixos, tochas). 5 mapas (6–10, Nv. 14–25) com layouts por tema (pátio,
  corredores, fosso, arena); chefe: Minotauro (mapa 10). Chefes agora são
  genéricos (`boss` no mapa + tabela `BOSSES`). Escala de dificuldade 1.5→2.1,
  a calibrar jogando.
- **Ato III (feito):** bioma Caverna (rocha vulcânica, lava animada do pack no
  lugar da água, estalagmites, céu de brasa). 5 mapas (11–15, Nv. 27–40):
  Fenda de Magma, Túneis de Basalto, Lagos de Lava, Ilhas de Obsidiana, Trono
  do Troll (chefe). Inimigo novo: Esqueleto em Chamas (recolorido). Escala
  2.2→2.8, a calibrar jogando.
- **Ato IV (feito):** bioma Picos Gelados (neve, água gelada, pinheiros, neve
  caindo do pack). 5 mapas (16–20, Nv. 41–52): Passagem Nevada, Lago
  Congelado, Desfiladeiro Gelado, Vila Soterrada, Salão do Rei Esqueleto
  (chefe). Inimigos novos: Esqueleto Gélido, Yeti, Lobo do Inverno (todos
  recoloridos) e Rei Esqueleto (esqueleto grande com coroa). Escala 2.9→3.3.
- **Ato V (feito):** bioma Cripta (pedra roxa, sangue no lugar da água,
  sarcófagos, tochas e estandartes). 5 mapas (21–25, Nv. 53–60): Portões da
  Cripta, Fosso de Sangue, Catacumbas, Salão dos Sarcófagos, Trono do Vampiro
  Senhor (chefe, vampiro grande de asas e florete). Inimigos novos: Guardião da
  Cripta e Espectro Real (recoloridos). Escala 3.4→3.9. Com isso a campanha
  tem 25 mapas em 5 atos; o final mostra "Campanha concluída!".
- Próximos passos: dungeons secretas por ato, objetivos variados, mapa-múndi,
  calibração de dificuldade, dungeons secretas por
  ato, objetivos variados (sobreviver N turnos etc.).

### Motor de mapas (variedade estilo FFT)
- Mapas podem ser **desenhados à mão** (`grid` em `MAPS`, grade ASCII): tamanho
  e formato livres, casas vazias (`v`) dão formato à plataforma, alturas 1–4,
  zona de início do grupo (`Z`) e dos inimigos (`E`) por mapa. O desenho pode
  ser espelhado a cada run. O chão flutuante vira uma ponta de rocha por casa
  (InstancedMesh), mais funda longe da borda.
- **Iluminação por mapa** (`luz`): normal, penumbra, escuro. Só o terreno
  escurece; os sprites continuam visíveis.
- Ato I já usa mapas desenhados à mão (12×14, 9×18, 16×12, L 14×14 e arena
  circular 15×14 com plataforma elevada). Atos II–V ainda são gerados; serão
  redesenhados um por vez.
- **Armadilhas e veneno (feito):** casas `T` da grade são armadilhas escondidas
  (espinhos = dano; veneno = 3 turnos de dano). Só os heróis caem; inimigos
  desviam; depois de disparada a casa fica marcada. Veneno existe como estado
  (`u.poison`).
- **Dungeons secretas (feito o sistema):** `secreta:true` + `from` = mapa de
  origem. Achar a passagem abre a dungeon no Quadro (salvo em
  `lendas_secret_v1`). Fase única, mini-chefe (`boss`), primeira vitória dá ouro
  + item raro. Hoje: Toca dos Corvos (Ato I, de Bosque dos Corvos) e Câmara das
  Armadilhas (Ato III, breu + armadilhas, dos Túneis de Basalto). Meta: poucas
  no começo, mais no fim (I:1, II:1, III:2, IV:2, V:3).
- Planejado (antes): dungeon **breu** (terreno invisível, armadilhas só pros heróis,
  inimigos desviam) e dungeons secretas (poucas no início, mais no fim).

- **Mapas maiores (decisão do usuário):** os mapas estavam apertados; a ideia
  é abrir espaço pro modo manual futuro. Atos II–V agora são gerados com
  `w`/`h` por mapa (18–24 de lado, até ~480 casas); o Ato I foi redesenhado
  maior (18×18, 13×22, 22×14, L 18×18, arena 19×18). Zonas de início crescem
  com a altura (5 linhas pros heróis, 7 pros inimigos em mapas altos). A
  quantidade de inimigos varia por mapa (`total`), de 8 a 20.
  Risco aberto: 1 malha por casa — se o desempenho no celular cair, trocar
  por InstancedMesh também no chão.

### Criaturas 2D (lado) e espelhamento
- Criaturas de perfil (lobo, abelha, besouro, peixe, corvo, fantasma) olham pra
  direita no sprite e **espelham** (`faceToward`) conforme o lado da tela do
  alvo/movimento. Sprites frontais (humanoides LPC, gosma, aranha, morcego) não
  precisam.
- Criaturas **multi-estado** (hoje só o lobo, `CREATURE_DEFS[...].multi`): tiras
  separadas de parado (1 quadro, sem respiração), andar, ataque e dano em
  `assets/creatures/<nome>/`. Ataque e dano tocam uma vez e voltam ao parado.
  Fluxo pra novos sprites feitos por IA: pedir 1 imagem por pose (ou folha),
  recortar o fundo verde, alinhar pelo centro de massa, reduzir (~88 px) e
  usar paleta única.

### Campanha: mapas e Modo Interminável
- **5 mapas fixos hoje** (antes eram 3): Campina Verde (Clareira de Brumavale,
  Bosque dos Corvos) e Deserto das Cinzas (Duna Rachada, Vale das Cinzas,
  Covil do Ogro — chefe). Motivo da expansão: a campanha **acabava
  literalmente no mapa 3**, sem loop nem conteúdo depois — jogador zerava e
  não tinha mais o que fazer. Duna Rachada e Vale das Cinzas preenchem a
  transição pro deserto antes do chefe, com o mesmo pool de inimigos já
  existente (sem bicho novo).
- **Modo Interminável**: ao vencer o último mapa fixo (hoje o Covil do Ogro),
  a run oferece a opção de entrar no Covil Interminável em vez de encerrar —
  rondas sintéticas sobre o último mapa (`mapOf()` sintetiza o mapa quando
  `n > MAPS.length` e `run.endless` está ligado), cada ronda com mais
  inimigos (`total` cresce) e inimigos mais fortes (`escala` cresce
  +0.12/ronda). Pontua sem fim, pro ranking. Decisão de escopo: isso é a
  resposta *de curto prazo* pra "o que eu faço depois de zerar" — as
  **dungeons de endgame distintas** (tier 9-12, com loot exclusivo) continuam
  como a resposta de longo prazo, ainda não escritas (ver "Decisões adiadas").
  `run.endless` só liga quando o jogador escolhe entrar; nunca pelo fluxo
  normal de `mapOf(n)` com `n` dentro de `MAPS`.

### Economia e recuperação
- **Ouro**: ganho a cada fase vencida, 10% da pontuação da fase
  (`GOLD_PER_SCORE`).
- **Templo da Aurora**: herói que não sobrevive até o fim de uma run (a
  recuperação entre fases da mesma run continua igual — volta com 50% de
  vida e Exausto) fica **Ferido** de verdade. Ferido não entra no grupo
  ativo. Recupera sozinho depois de **2 runs concluídas** (`INJURY_MISSIONS`)
  ou o jogador paga ouro pra curar na hora — custo escala com o nível do
  herói (`INJURY_RUSH_BASE + nível × INJURY_RUSH_PER_LEVEL`).

### Validação (todas as entregas até aqui)
Esse sandbox bloqueia `cdnjs.cloudflare.com` (CDN que o jogo usa), então boa
parte do trabalho foi validado só por leitura de código + scripts Node
isolados reproduzindo a lógica pura. **Isso mudou**: `registry.npmjs.org`
está liberado, então dá pra baixar three.js/gsap via npm, servir uma cópia
local vendorizada (só pra teste, o jogo publicado continua usando CDN normal)
e rodar um Chromium headless via Playwright de verdade. Dois bugs reais já
foram achados assim (barra de unidades escondendo heróis, balão de fala
sobrepondo a lista de turno) que nenhuma leitura de código teria pego. Isso
devia virar rotina antes de qualquer PR daqui pra frente.

## Classes e subclasses

### Modelo decidido (implementado nas 6 classes originais)
- **Classe base nunca muda** (sprite/corpo é por classe — reclasse livre estilo
  FFT foi descartada: o problema de asset é bem maior que trocar arma, e
  dissolve a identidade de "esse é o Rui, o Guerreiro").
- Herói **nasce sem subclasse**. No **nível 10** (`SUB_UNLOCK_LEVEL`) ele
  escolhe 1 de 2 subclasses na **Forja do velho Brasa** (grátis na primeira
  vez). Dá pra **trocar depois pagando ouro** (`subRespecCost`: 60 + 20 ×
  nível). Dragon Nest faz parecido (escolha no nível 15, travada por
  personagem, respec limitado).
- **Progressão única**: continua um nível só por herói (sem trilha de XP
  separada pra subclasse). A subclasse liga a mecânica própria; o resto
  (PV/atributos/equip.) segue crescendo com o nível.
- **Recrutamento escalado** (estilo FFT): nível do recruta = média de nível do
  elenco ± 2 (`newDraw`/`rosterAvgLevel`, teto 60). Recruta que já nasce com
  nível ≥ 10 vem com subclasse sorteada. Recrutar continua sem custo em ouro.
  Atributos sorteados têm variação maior e a tela mostra a descrição do traço,
  pra quem lê e compara escolher melhor que quem clica no automático.
- **Bônus de atraso** (`CATCHUP_*`): herói ≥ 3 níveis abaixo da média do grupo
  ativo ganha +10% de XP por nível de diferença, teto +100%. Rápido o bastante
  pra não ser grind de recomeço, gradual o bastante pra jogador aprender a
  classe jogando — não vira nível 60 de graça.
- **Poder de herói novo vem de 2 eixos**: nível (catch-up) e equipamento (Cofre
  da Guilda é universal). **Pendente**: tier de item travado por nível (já
  especificado em `EQUIPAMENTOS.md`, vem com o motor de item v2, passo 11) —
  sem isso um herói nível 1 consegue vestir qualquer item do cofre.
- Campanha: longa, estilo FFT, sem lore; cidade = lobby; dungeons secretas e
  de chefe único. Modo Interminável implementado mas **fora de foco** até o
  usuário pedir.

### Mecânica de cada subclasse
Usam ganchos que já existem no motor (bônus no `parts[]` do ataque, `critBonus`,
flags `inspired`/`shaken`) em vez de um sistema de efeitos de status genérico.
Duas saíram simplificadas por falta de sistema: **Saraivador** (seria dano em
área; hoje respinga 40% do dano num inimigo colado no alvo) e **Armadilheiro**
(seria armadilha de terreno; hoje +3 de acerto no primeiro golpe da batalha).
Voltam à versão completa no passo 10. **Paladino/Monge** continuam só design
(classes novas, exigem sprite próprio — pesquisar asset antes).

8 classes base, 2 subclasses cada (tabela de papel/nomes — decidido, as 6
primeiras linhas já valem para o código; Paladino/Monge ainda são só
design) — base compartilha tipo de arma, peso de
armadura e esqueleto de comportamento de IA; subclasse diverge em
comportamento de verdade (não só número), efeito visual próprio, e afinidade
de equipamento.

| Base (já existe) | Papel | Subclasse A | Subclasse B |
|---|---|---|---|
| Guerreiro | Tanque melee | Cavaleiro — defensivo, protege o aliado mais fraco | Bárbaro — ofensivo, ignora a própria vida, aplica Sangramento |
| Ladino | Ágil, acha segredos | Assassino — mira o alvo mais frágil, bônus vs. isolado | Armadilheiro — coloca armadilhas no terreno |
| Mago | Dano à distância | Piromante — crítico/explosivo, aplica Queimando | Geomante — mais tanque que DPS, reduz armadura inimiga ou escuda aliado |
| Clérigo | Suporte (cura) | Curandeiro — cura pura no mais ferido | Templário — smite/cura híbrido, ganha "Abençoado" ao atacar |
| Arqueiro | Atirador | Patrulheiro — precisão single-target, empilha dano no mesmo alvo | Saraivador — volley que acerta vários inimigos próximos |
| Bardo | Suporte (bônus) | Consonante — buffs de harmonia/ofensivos | Dissonante — debuffs de discórdia |
| Paladino (nova) | Tanque híbrido | Guardião — tanque puro, protege/absorve dano | Cruzado — ofensivo, cura a si mesmo ao acertar |
| Monge (nova) | Melee ágil autossustentável | Quebra-ossos — dano crescente a cada golpe seguido | Asceta — esquiva/reposiciona, contra-ataca |

Guerreiro/Cavaleiro vs. Paladino/Guardião não são redundantes por desenho:
Cavaleiro é puramente marcial (intercepta e protege, sem nada místico);
Guardião (Paladino) carrega sustentação própria no kit base da classe
(cura/escudo leve), não só na subclasse — ele é "tanque com fé", não
"tanque melhor".

Ficou de fora de propósito: um "controlador puro" (stun/confusão) — candidato
a uma 9ª classe mais pra frente, não faz parte da base inicial.

### Dependências técnicas que essas subclasses exigem (nenhuma existe ainda)
1. **Sistema de efeitos de status** (Sangramento, Queimando, Vulnerável,
   Abençoado, redução de armadura). Hoje o combate só tem dano/cura/crítico
   puro. Sem isso, metade das subclasses vira "a mesma coisa com nome
   diferente".
2. **Ataque em área** (pro Saraivador). Hoje o motor de combate só mira um
   alvo por vez — implica lógica de alcance em área, resolução multi-alvo,
   provavelmente indicador visual novo.
3. **Armadilha de terreno** (pro Armadilheiro). Objeto colocável numa casa do
   grid que ativa quando um inimigo entra nela — não existe hoje.
4. **Terreno intransponível + habilidade/item que permite atravessar** (ex.:
   "montanha" que bloqueia todo mundo, um item deixa escalar). Hoje todo
   terreno é passável (morro só dá bônus de altura, não bloqueia). Ideia
   registrada, não é prioridade — fica pro roadmap de conteúdo de mapa.

## Sistema de gatilhos (planejado, não implementado)

Ideia: pegar a *essência* do sistema de Gambit de Final Fantasy XII (condição
→ ação, com prioridade), não recriar a densidade dele. Objetivo: dar ao
jogador uma sensação real de controle sobre o combate automático, sem virar
um construtor de lógica livre (que seria um risco grande de UX, já que o
jogo já lida com bastante informação na tela).

Direção decidida:
- **Biblioteca curada de gatilhos prontos** (algo como 10-15 opções bem
  desenhadas: "curar aliado <20% vida", "focar inimigo com Sangramento",
  "focar inimigo isolado"), não um menu de condição×alvo×ação livre.
- Gatilhos rodam **como regras de prioridade antes do comportamento padrão
  da (sub)classe** — se nenhum gatilho ativo bate a condição, a IA cai no
  comportamento automático de sempre (`COMO`, já existente). Isso aproveita
  o que já existe em vez de reescrever o combate do zero.
- Prédio próprio na vila pra gerenciar isso (nome ainda não decidido —
  ideias soltas: "Painel de Gatilhos", "Combos").
- Depende do sistema de efeitos de status pra boa parte dos exemplos citados
  (ex.: "foca inimigo sangrando" não existe sem Sangramento existir).
- Incentivo por engajamento: herói com gatilho configurado de verdade (não
  só o comportamento padrão da classe) deve ganhar um pouco mais de
  recompensa que um deixado 100% no automático — recompensa o jogador que se
  envolve mais, sem precisar de modo manual completo (ver abaixo).

### Modo manual — avaliado e adiado de propósito
Cogitado dar ao jogador a opção de jogar a batalha manualmente (em vez de só
IA automática), com recompensa maior pra quem jogar assim. Avaliação: é
tecnicamente possível, mas é maior que quase tudo o resto somado — equivale
a construir um segundo modo de combate completo (seleção de unidade,
alcance, alvo, confirmação, por turno), não um recurso a mais. O sistema de
gatilhos já existe exatamente pra dar sensação de controle sem esse custo.
Decisão: **não entra no roadmap atual**, fica registrado como ideia de
longuíssimo prazo. O incentivo por engajamento (ver acima) captura o espírito
da ideia original sem precisar do modo manual completo.

## Roadmap em ordem (o que vem depois do quê)

1. ~~Elenco persistente~~ — feito.
2. ~~Economia + Templo~~ — feito.
3. ~~Classes e subclasses (decisão de nomes/papéis)~~ — feito, este arquivo.
4. ~~Relatório de equipamentos (v1, catálogo fixo)~~ — feito, superado pela
   especificação v2 em `EQUIPAMENTOS.md`.
5. ~~Especificação do sistema de item estilo ARPG (tiers, raridade,
   atributos, disciplina de combate)~~ — feito, este arquivo +
   `EQUIPAMENTOS.md`. **Nada disso está implementado em código ainda** — o
   jogo publicado roda a v1 (catálogo fixo de 80 itens).
6. ~~Implementar os 5 atributos primários como campo do herói + fórmula que
   os converte em dano/PV/crítico~~ — feito (`ATTR_NAMES`/`ATTR_BASE`/
   `recomputeAttrBonus`/`applyLevelUps`). Pré-requisito de quase tudo abaixo.
7. ~~Implementar DEF mágica + marcação físico/mágico por ataque~~ — feito
   (`defMag`/`baseDefMag`/`isMagicAttacker`, hoje só Mago e Xamã Goblin
   marcados `magico:true`).
8. ~~Implementar as 12 subclasses das 6 classes originais~~ — feito, com
   Saraivador e Armadilheiro simplificados (ver seção "Classes e
   subclasses"). **Ainda falta**: Paladino/Monge como classes novas de
   verdade (sprite próprio, pesquisa de asset primeiro) + suas 4 subclasses.
9. Sistema de efeitos de status (destrava a versão completa de Saraivador/
   Armadilheiro e abre caminho pras subclasses de Paladino/Monge).
10. Ataque em área e armadilha de terreno (mecânicas de combate novas).
11. Motor de rolagem de item (substituir o catálogo fixo pela v2) +
    serialização de save por instância de item.
12. Escrever o catálogo de verdade em cima do motor: armas por família,
    itens Lendários por dungeon de endgame.
13. Sistema de gatilhos (biblioteca curada + prédio na vila) + incentivo por
    engajamento.
14. Nível de classe ganhando uso mecânico de verdade (hoje só acumula sem
    efeito).

## Decisões explicitamente adiadas (não esquecidas, só não é agora)

- Lista de dungeons de endgame específicas (nomes, temas, loot exclusivo).
- Catálogo de armas por família, tier a tier.
- Classe de controle puro (9ª classe).
- Terreno intransponível + habilidade de travessia (ex.: escalar montanha).
- Modo de combate manual (avaliado, adiado — ver seção de gatilhos acima).
- Export/import de save (hoje é só local).

## Kit de UI novo e Quadro de Missões (faixa de regiões)
- Artes geradas por IA recortadas de folhas com fundo magenta: `assets/regioes/` (9 banners, hoje usados 5 por ato), `assets/icones/` (16 ícones de tipo de mapa, ainda sem uso) e `assets/ui/` (27 peças: painéis, faixas de linha em 3 estados, botões, cartas de região, selos, barra, divisor, fitas).
- Quadro de Missões (`renderMissions`): faixa de cartas por ato + cabeçalho com progresso + lista do ato selecionado. Revelação gradual: concluídos, o disponível e um "???"; o resto vira "+ N mapas ainda não descobertos". Dungeons secretas só aparecem depois de achadas. Classe `.qd` no `#pi` (removida em `setMode`). Estado da região em `qdAto`.
- Próximas telas a migrar para o kit (sempre com antes/depois aprovado): briefing do mapa, Taverna, Vila, Cofre/Forja/Templo, formação, batalha.

## Regra: só sprites do pack
- Nenhum personagem (herói, inimigo, aldeão) aparece com arte desenhada por código. Heróis e inimigos humanoides usam `LPC_RECIPES`; criaturas usam `CREATURE_DEFS`. O Xamã Goblin agora também tem receita LPC.
- Retrato antes de o sheet carregar = imagem em branco (`BLANK_IMG`), nunca o desenho gerado. Quando todos os sheets ficam prontos, os retratos são recalculados e a tela aberta (Taverna, Recrutar, Ficha, briefing) é redesenhada.
- As funções `heroSprite`/`enemySprite` ficam só como último recurso interno e não são mais usadas para nenhum personagem existente. Ao criar inimigo ou classe nova, crie a receita LPC (ou criatura) junto.

## Ícones coloridos (assets/ico)
- 86 ícones recortados das folhas de IA (fundo magenta): classes (`c_`), subclasses (`s_`), atributos (`t_`), slots (`l_`), vila/UI (`v_`) e 32 tipos de item (`i_`). Mapa em `NIC` (index.html); `ico()` usa o ícone novo e só cai nas silhuetas antigas (`assets/ui-icons`, game-icons.net) se faltar algum.
- Itens: os 80 itens do jogo usam os tipos (`i_espada`, `i_elmo`, ...). A raridade vira brilho colorido ao redor do ícone (`itemIco`).
- Para trocar um ícone, regenere só aquele e recorte com o mesmo nome em `assets/ico/`.

## Plano de campanha e mapas (decidido com o dono do jogo)
- **Regra de inimigos:** 5 a 8 por mapa comum (até 9 nos difíceis); chefe = chefe + 3 a 5 acompanhantes. Sem "20 na tela" como padrão.
- **Ideia guardada (usar lá na frente):** fases especiais de horda, com 15 a 20 inimigos fortes, só como exceção rara e avisada.
- **Objetivos variados (como no FFT):** derrotar todos, derrotar o líder, sobreviver N turnos, proteger um aliado.
- **Estrutura:** Run 1 = 5 biomas em ordem (Nv 1–~25); Run 2 = os mesmos 5 biomas de novo no difícil (paleta/variantes de inimigo diferentes, mapas novos, Nv ~25–50); depois o **endgame**: só dungeons muito difíceis, muitos chefes secretos e opcionais. Sem terceira passada por enquanto.
- **Mapas:** menos de 100; foco em qualidade e variedade (temas à mão), reaproveitando biomas, sprites e efeitos.
- **Balanceamento (XP, nível, vida/ataque):** só depois dos mapas prontos.
- Referência de inspiração: Final Fantasy Tactics (5 aliados contra ~5–8 inimigos; objetivos variados).

## Pendente (adiado pelo dono): mapas maiores e tileset
- Mapas maiores (~18–22 × 20–26, câmera arrastável) e mais "vida" no cenário.
- Tileset externo estilo LPC (candidatos: LPC Compatible Terrain, LPC Forest tiles,
  LPC Modified base tiles, Terrain atlas — OpenGameArt; conferir licença; CC-BY-SA
  exige crédito). Sandbox não acessa opengameart.org; o dono envia os PNGs ou libera a rede.
