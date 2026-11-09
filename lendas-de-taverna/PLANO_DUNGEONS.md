# Plano de dungeons (rascunho para decidir)

Nível máximo: 60. Muitas dungeons, com 3 tipos que mudam de proporção ao longo do jogo (estilo MMO).

## Tipos
- **L — Levelling:** muita experiência, muitos monstros, missões, mini-chefe. Itens normais; **sem conjuntos**. O chefe da faixa é a missão principal e libera a próxima faixa. Pode dropar único, mas com chance bem baixa (ver abaixo).
- **G — Equipamento (gear):** pouca experiência (~50%), monstros elite, chefe(s) e mini-chefe. Cada uma dropa **um conjunto de 6 peças e os únicos próprios**. Tem a Arena do Chefe (só o chefe), com menos XP e mais chance, para quem caça um item específico.
- **M — Materiais:** XP médio-baixa, grande quantidade de materiais de forja (ferro/runa/cristal e materiais temáticos). Sem únicos.

## Proporção por faixa (invertendo ao longo do jogo)
| Faixa | Níveis | L | G | M | Total | % equipamento+materiais |
|---|---|---|---|---|---|---|
| 1 | 1–10 | 5 | 2 | 0 | 7 | 29% |
| 2 | 10–20 | 5 | 4 | 1 | 10 | 50% |
| 3 | 20–30 | 4 | 5 | 2 | 11 | 64% |
| 4 | 30–40 | 3 | 7 | 2 | 12 | 75% |
| 5 | 40–50 | 3 | 8 | 3 | 14 | 79% |
| 6 | 50–60 | 2 | 9 | 3 | 14 | 86% |
Meta: ~68 dungeons (construídas faixa a faixa, não de uma vez).

## Chance de único (por morte de chefe; mini-chefe: 60%)
| Faixa | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| Dungeon G (equipamento) | 8% | 6% | 4,5% | 3,5% | 2,5% | 2% |
| Dungeon L (levelling) | 1,5% | 1,2% | 0,9% | 0,7% | 0,5% | 0,4% |
- Dungeons L dropam únicos só raramente, e sempre os da própria dungeon.
- **Proteção contra azar (só nas G):** a chance sobe a cada morte sem único e é garantida depois de N mortes (25 na faixa 2, 80 na faixa 6).

## Poder de combate (PC)
- Número **visível** em todo lugar: em cada item (calculado dos atributos do item), na aba do personagem (soma dos itens equipados + atributos + nível) e no portal.
- No portal: "Seu poder de combate **489** / 520 recomendado", com a cor só como apoio (verde ≥ 100%, amarelo 80–99%, vermelho < 80%). Não é trava: o jogador pode entrar fraco para tentar um item.
- A **trava é o nível** (dungeon bloqueada com cadeado até chegar no nível) e os requisitos especiais (derrotar um chefe, ter uma chave ou item).
- O PC recomendado de cada dungeon sai da **simulação** (PC com o qual o herói vence com folga). Os pesos do PC são por classe, para ficar justo para as 6 classes.
- v1: itens + atributos + nível. Talentos e habilidades entram depois.

## Drop por tier e tema (estilo Cabal)
- Cada dungeon dropa **equipamento de um tier específico** (os 12 tiers de 5 em 5 níveis), para todas as classes. Cada item mostra o PC e o **nível necessário** (o do tier).
- Dungeons do mesmo tier têm **temas diferentes** (um foco em defesa, outro em ataque, outro em vida...). Assim uma classe se dá melhor em uma dungeon que em outra.
- O jogador **não vê a lista de itens** da dungeon: a surpresa do drop é parte da graça. O portal só diz "Dropa itens de Tier 2 · nível 6–10".
- Os itens únicos nomeados continuam, como raridade: caem de vez em quando e não aparecem na lista.
- Cada dungeon de equipamento tem 1 conjunto próprio (6 peças, bônus em 2/4/6), dentro do tier e do tema.
- Dungeons de materiais dropam materiais temáticos usados na forja (ex.: reforjar com foco num tipo de afixo).

## Variedade
- Cada dungeon tem um **tipo de inimigo** (enxame, blindado, à distância, veneno, fogo, gelo, morto-vivo…). Algumas classes vão melhor em algumas dungeons.
- Dungeons de equipamento, a partir da faixa 2, são **fechadas e lineares** (começo, meio e fim, com mini-chefe no meio e chefe no fim). A primeira será um piloto.

## Liberação
- Por faixa: derrotar o chefe de uma dungeon L da faixa anterior + nível mínimo. Dentro da faixa, o jogador escolhe qualquer dungeon.

## Produção
- Mapas e famílias de monstros reaproveitados com variações (paleta, props). Cada dungeon G pede 1 chefe (+ mini-chefe) com arte de IA. Dungeons M podem ser versões "mineração" de mapas existentes.

## Telas (mockups aprovados)
- Portal em **tela cheia**: arte da dungeon como fundo, carrossel de cartões com o **nível** (✔ verde / 🔒 vermelho) e abas **Dungeons** e **Especiais** (Arena do Chefe, Boss Rush, dungeons especiais com requisitos).
- Painel de requisitos (nível, chefe, itens), PC com número e linha de equipamento (tier e nível). Sem lista de itens e sem tipo de dungeon na tela.
- Especiais com **ranking** (só em dungeons especiais, com semente semanal). Preparar já o recorde local (tempo, mortes, classe, PC).

## A decidir
1. Total de dungeons (~68; começar com ~20 e crescer por faixa?).
2. Proteção contra azar: concorda?
3. Conjuntos por dungeon: gerar de forma padronizada (bônus por arquétipo) para caber 30+ conjuntos?
4. Fórmula do PC: pesos por classe, calibrados pela simulação.
