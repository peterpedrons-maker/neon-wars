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

## Classes e subclasses (decidido, ainda não implementado em código)

8 classes base, 2 subclasses cada — base compartilha tipo de arma, peso de
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
8. Implementar as 8 classes base + 16 subclasses no código (sprites, IA,
   afinidade de equipamento) — hoje só as 6 classes originais existem, sem
   Paladino/Monge, sem nenhuma subclasse.
9. Sistema de efeitos de status (pré-requisito de boa parte das subclasses).
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
