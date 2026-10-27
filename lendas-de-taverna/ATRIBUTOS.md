# Sistema de atributos (proposta simplificada)

Só a **lista** de atributos do D&D; nada das regras deles (sem modificador, sem bônus de
proficiência, sem DEF = 10 + …). Cada atributo é um número que dá bônus diretos e simples em
**2 coisas**. O d20 do jogo continua igual (d20 + ATQ ≥ DEF). Todos os números são ponto de
partida, a calibrar com a simulação (`BALANCEAMENTO.md`).

## 1. Os 6 atributos e o que cada ponto dá
Valor neutro = 10. O bônus conta **só os pontos acima de 10** (abaixo de 10 vira penalidade
pequena). Os valores-base da classe (ATQ, DEF, PV…) continuam como hoje; o atributo soma por cima.

| Atributo | Efeito 1 | Efeito 2 |
|---|---|---|
| **Força** | corpo a corpo: +1 ATQ a cada 3 pts, +1 dano a cada 2 pts | **+1 PV** por ponto |
| **Destreza** | à distância e adagas: +1 ATQ a cada 3 pts, +1 dano a cada 2 pts | +1 DEF a cada 4 pts |
| **Constituição** | **+2 PV** por ponto | +1 Res. Mágica a cada 4 pts |
| **Inteligência** | dano mágico: +1 a cada 2 pts, +1 ATQ mágico a cada 3 pts | +1 de margem de crítico a cada 8 pts |
| **Sabedoria** | cura: +1 a cada 2 pts | +1 Res. Mágica a cada 3 pts; +1 segredos a cada 2 pts |
| **Carisma** | dano do Bardo (+1 a cada 2 pts) e inspiração (+1 a cada 6 pts) | +1% de drop e de XP a cada 2 pts |

Qual atributo vale pro golpe depende da arma da classe: Guerreiro e Clérigo (corpo a corpo)
→ Força · Ladino e Arqueiro → Destreza · Mago → Inteligência · Bardo → Carisma.
Isso faz cada classe se destacar sozinha, e dá espaço pra variar *dentro* da classe
(um Guerreiro de Constituição alta é tanque; de Força alta é atacante).

## 2. Subir de nível
- **Perfil fixo da classe:** 2 pontos por nível, divididos por pesos. Ex.: Guerreiro Força 50% ·
  Constituição 30% · Destreza 20%. Mago Inteligência 50% · Constituição 25% · Sabedoria 25%.
- **Pontos livres:** +1 ponto a cada 2 níveis para o jogador distribuir na ficha do herói.
  Se não gastar, entra pelo perfil da classe (o jogo continua jogando sozinho).
- Sem teto rígido; o bônus cresce sempre, e os inimigos usam as mesmas regras.

Exemplo — Guerreiro (Força 14, Const. 13, Des. 10 no nível 1), pontos livres 50/50 em Força e Const.:
| Nível | Força | Const. | Des. | Bônus total |
|---|---|---|---|---|
| 1 | 14 | 13 | 10 | ATQ +1 · dano +2 · PV +10 |
| 10 | 25 | 20 | 13 | ATQ +5 · dano +7 · PV +35 |
| 25 | 44 | 33 | 19 | ATQ +11 · dano +17 · PV +80 · DEF +2 |
| 50 | 75 | 54 | 29 | ATQ +21 · dano +32 · PV +153 · DEF +4 |
(Hoje, sem itens, o Guerreiro Nv50 teria só +~10 de dano e +50 PV, e nada de ATQ/DEF.)

## 3. Itens com afixos sorteados
- Item = **base** (tipo + espaço, ícone do pack) + **afixos** sorteados + **nível do item**.
- Afixos podem ser **+N de um atributo** (ex.: +3 Força) ou **+N num valor direto**
  (ATQ, DEF, PV, dano, crítico, Res. Mágica, Mov, Alc, segredos).
- Quantidade pela raridade: Comum 1 · Raro 2 · Mágico 3 · Épico 4 · Lendário 5.
- Nível do item = nível do mapa onde dropou; o valor dos afixos cresce com ele.
- Chance de raridade depende do ato (início quase só comum/raro); chefe garante mínimo Mágico.
- Itens antigos dos saves viram uma base com afixos fixos equivalentes (nada se perde).

## 4. Inimigos
- Cada espécie ganha os **6 atributos**, um perfil de crescimento (como a classe) e valores
  base (ATQ, DEF, PV, dado de dano) como hoje; o **nível vem do mapa** (+2 chefe, +1 líder).
- As mesmas contas dos heróis dão o resto. A `escala` atual (que só aumentava PV) deixa de existir.
- XP por inimigo passa a depender do nível dele.

## 5. Ordem de trabalho
1. Motor: atributos, bônus, level up e inimigos (sem mexer em telas; teste dos números).
2. Itens com afixos + migração dos saves.
3. Telas (com mockup antes): ficha com os 6 atributos e pontos livres, itens com afixos, Forja/Cofre.
4. Calibração com a simulação: curva de XP, nível por mapa, raridade por ato, limite de rodadas.
5. Testes de batalha completos nos mapas novos.
