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
- **80 itens**, 5 raridades (Comum/Raro/Mágico/Épico/Lendário), raridade só
  cosmética por enquanto (sem efeito de gatilho, sem lore, itens podem
  repetir). Ver `EQUIPAMENTOS.md` pro catálogo completo gerado do código.
- Equipamento **não reseta mais** (era a regra antiga de quando o jogo era
  roguelite). O que sai de um herói vai pro **Cofre da Guilda**, estoque
  compartilhado permanente, prédio próprio na vila com inventário em grade
  (estilo PoE/Diablo), filtrável por slot.

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
   provavelmente indicador visual novo. É a dependência mais cara das três.
3. **Armadilha de terreno** (pro Armadilheiro). Objeto colocável numa casa do
   grid que ativa quando um inimigo entra nela — não existe hoje.

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

## Roadmap em ordem (o que vem depois do quê)

1. ~~Elenco persistente~~ — feito.
2. ~~Economia + Templo~~ — feito.
3. ~~Classes e subclasses (decisão de nomes/papéis)~~ — feito, este arquivo.
4. ~~Relatório de equipamentos~~ — feito, `EQUIPAMENTOS.md`.
5. Sistema de efeitos de status (pré-requisito de quase tudo que vem depois).
6. Ataque em área e armadilha de terreno (mecânicas de combate novas).
7. Implementar as 8 classes base + 16 subclasses no código (sprites, IA,
   afinidade de equipamento).
8. Sistema de gatilhos (biblioteca curada + prédio na vila).
9. Nível de classe ganhando uso mecânico de verdade (hoje só acumula sem
   efeito).

## Decisões explicitamente adiadas (não esquecidas, só não é agora)

- Itens únicos de verdade / sem repetição no catálogo de loot.
- Lore/texto de sabor por item.
- Afinidade de equipamento por subclasse.
- Classe de controle puro (9ª classe).
- Export/import de save (hoje é só local).
