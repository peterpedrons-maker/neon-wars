# Sistema de equipamento — especificação (v2)

Este arquivo substitui a v1 (catálogo fixo de 80 itens). Depois da conversa
sobre itens estilo ARPG, **não existe mais uma lista fixa de itens pra
listar** — existe uma **receita de geração**. Este documento é essa receita:
os moldes, as fórmulas de rolagem, e exemplos concretos de itens que elas
produziriam. O catálogo "final" só existe no momento em que um item realmente
dropa, calculado em cima dessas regras.

**Status: especificação travada, implementação em código ainda não começou.**
Ver `DESIGN.md` → seção Roadmap pra saber o que precisa existir no código
antes desse sistema rodar de verdade (classes/subclasses, atributos
primários, DEF mágica).

## Os 3 eixos do item

Todo item não-lendário é definido por três coisas independentes, igual
ARPGs de verdade (Diablo, PoE):

1. **Tier** (1 a 12, travado pelo nível do personagem) — define o **teto**
   de poder do item. Um item tier 9 nunca perde pra um tier 3, não importa a
   raridade.
2. **Raridade** (Comum → Lendário) — define **quantos atributos** o item rola
   e quão perto do topo da faixa daquele tier. Raridade não pula tier.
3. **Atributo sorteado** (só em cabeça/corpo/mãos/pés/mão secundária/acessório
   — **arma nunca rola**, fica de fora) — qual dos 5 atributos primários o
   item carrega. Sorteado de forma uniforme entre os 5, independente do grupo
   de peso da armadura (ver `DESIGN.md`).

**Exceção: Lendário não rola.** Item lendário é escrito à mão, com nome
próprio, sempre no topo do tier em que existe, e normalmente amarrado a uma
dungeon de endgame específica (ver seção própria). Isso resolve o "itens
únicos de verdade" que ficou pendente desde o começo da conversa sobre
equipamento.

## Tiers (nível 1 a 60)

| Tier | Nível mínimo |
|---|---|
| 1 | 1 |
| 2 | 3 |
| 3 | 6 |
| 4 | 10 |
| 5 | 15 |
| 6 | 21 |
| 7 | 28 |
| 8 | 36 |
| 9 | 42 |
| 10 | 48 |
| 11 | 54 |
| 12 | 60 |

Intervalo sempre crescente (desbloqueia rápido no início, mais espaçado no
fim) — **sem reacelerar perto do 60**: o clímax é o próprio nível máximo, não
uma crista no meio do caminho. Ver `DESIGN.md` pro motivo dessa escolha.

## Disciplina de poder (por que o d20 continua importando no tier 12)

Regra central, não-negociável pra qualquer item gerado: **ATQ e DEF (os
números que entram na rolagem de 1-20) crescem pouco e devagar; dano, PV e
crítico crescem muito**. Isso existe pra o dado nunca virar decoração, mesmo
no fim do jogo — ver a conversa completa em `DESIGN.md`.

Fórmulas de referência (ilustrativas, ajustar por sensação de jogo depois
que existir conteúdo pra testar):

```
atkBudget(tier)      = round(tier × 0.8)        // total de ATQ de equip. no tier
dmgDiceCount(tier)    = 1 + floor((tier-1) / 3)  // quantos dados de dano
dmgDieSize(tier)      = tier <= 3 ? 6 : tier <= 6 ? 8 : 10
dmgBonusBudget(tier)  = tier × 2                 // bônus fixo de dano
```

| Tier | ATQ total (equip.) | Dado de dano | Bônus de dano |
|---|---|---|---|
| 1 | +1 | 1d6 | +2 |
| 4 | +3 | 2d8 | +8 |
| 7 | +6 | 3d10 | +14 |
| 10 | +8 | 4d10 | +20 |
| 12 | +10 | 4d10 | +24 |

A DEF dos inimigos de cada dungeon precisa escalar em paralelo com o ATQ
total esperado pra quem está naquele tier, mantendo a chance de acerto numa
faixa saudável (~55%–80%) o jogo inteiro. Isso é trabalho de balanceamento
contínuo, não um número fixo — fica marcado aqui pra nunca ser esquecido
quando as dungeons de cada tier forem desenhadas.

## Atributos primários

5 atributos (ver `DESIGN.md` pro mapeamento completo por classe/subclasse):
**Força, Destreza, Inteligência, Vitalidade, Fé**. Alimentam dano/PV/crítico
por fórmula — nunca ATQ/DEF brutos diretamente (mesma disciplina acima).

O grupo de peso (Leve/Média/Pesada) decide só a **aparência/família visual**
do item — quem decide **quais atributos podem rolar** é o grupo de afixo do
slot, abaixo.

## Grupos de afixo por slot

Item sortear qualquer um dos 5 atributos em qualquer slot soava incoerente
(um peitoral de armadura pesada rolando Inteligência, por exemplo) — por
isso cada slot pertence a um **grupo de afixo**, que restringe o que pode
rolar ali. Só os acessórios ficam livres de verdade, igual anel/amuleto em
qualquer ARPG.

| Grupo | Atributos possíveis | Slots |
|---|---|---|
| Defensivo | DEF, Resistência Mágica, Vitalidade | Corpo, Cabeça, Mão secundária (quando é escudo) |
| Ofensivo | Força, Destreza, Inteligência | Mãos, Mão secundária (quando é adaga/tomo de conjurador) |
| Utilidade | Destreza, Vitalidade | Pés |
| Livre | qualquer um dos 5 | Acessório 1 e Acessório 2 |

Mão secundária muda de grupo dependendo da família do item (escudo =
defensivo, adaga/tomo = ofensivo) — mesma lógica de família usada nas armas.

## Raridade (dentro de um tier)

| Raridade | O que muda |
|---|---|
| Comum | 1 atributo do grupo do slot (garantido — nunca cai peça fora do papel dela), metade inferior da faixa do tier |
| Raro | 1 atributo do grupo + 1 bônus pequeno fixo (DEF ou PV), metade superior da faixa |
| Mágico | 2 atributos do grupo |
| Épico | 2 atributos do grupo + 1 rolagem que pode **quebrar o grupo** (Dano Crítico, Resistência Mágica, ou um atributo fora do grupo — o momento raro de "caiu uma peça incrível mas inesperada") |
| Lendário | não rola — escrito à mão, sempre no topo do tier, nome e lore próprios |

## Atributos secundários (novos, rolam a partir de Épico)

- **Dano Crítico** — multiplicador de dano em cima de um acerto crítico
  (hoje crítico só dobra os dados; isso daria um dial adicional).
- **Resistência Mágica** — defesa separada da DEF física, só entra em jogo
  contra ataques marcados como mágicos (Mago, magia do Clérigo/Paladino).

## Armas (não rolam — curadas por família)

Arma é o único slot sem rolagem — fica fixa, igual ao catálogo antigo, só
que agora organizada por **família de arma** (não por classe individual, pra
não precisar de 8 catálogos separados) e repetida em cada um dos 12 tiers:

| Família | Classes que usam |
|---|---|
| Armas de corte/impacto (físico corpo-a-corpo) | Guerreiro, Paladino, Monge, Ladino |
| Arcos | Arqueiro |
| Cajados/varinhas (arcano) | Mago, Bardo |
| Símbolos sagrados (maças, cajados santos) | Clérigo |

Cada família ganha 1-2 armas nomeadas por tier, seguindo a disciplina de
poder acima (ATQ quase parado, dano crescendo). Esse catálogo ainda precisa
ser escrito tier a tier — é conteúdo pendente, não uma decisão em aberto.

## Dungeons de endgame (tier 9-12 / nível 42-60)

Em vez de um pool genérico de "4 opções aleatórias" no fim do jogo, cada
tier alto tem **múltiplas dungeons distintas**, cada uma com:
- Tabela de drop própria (os atributos/famílias de item que ela favorece).
- 1-2 itens Lendários exclusivos daquela dungeon (motivo concreto pra
  farmar ali e não em outro lugar).
- Dificuldade própria — mais difícil que a média do tier, de propósito,
  pra justificar o loot melhor.

Lista de dungeons específicas ainda não existe — fica como próximo passo de
conteúdo depois que o sistema base estiver implementado.

## O que falta pra isso rodar (resumo — detalhe completo em `DESIGN.md`)

1. Classes/subclasses no código (hoje só as 6 originais existem, sem
   Paladino/Monge, sem nenhuma subclasse).
2. ~~Os 5 atributos primários como campo do herói + fórmula que os converte
   em dano/PV/crítico~~ — feito, ver `DESIGN.md`.
3. ~~DEF mágica como stat separado + marcação de ataque físico/mágico~~ —
   feito, ver `DESIGN.md`. Ainda não rola em item (depende do item 4 abaixo).
4. Motor de rolagem de item (molde + tier + raridade → instância com valores
   sorteados) substituindo o catálogo fixo atual.
5. Serialização de save por instância de item (cada item agora é único, não
   só uma referência a um id de catálogo).
