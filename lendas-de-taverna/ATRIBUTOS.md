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

## 2. Subir de nível (decidido)
- **Tudo automático.** O jogo distribui os pontos sozinho; o jogador não distribui atributo.
  Herói recrutado já com nível vem com os pontos distribuídos (perfil da classe + afinidade).
- **Perfil fixo da classe:** pontos por nível divididos por pesos (ex.: Guerreiro Força 50% ·
  Constituição 30% · Destreza 20%). 2 pontos por nível até o nível 30, depois menos (curva suave,
  **sem teto rígido**, já que o jogador não distribui).
- **Afinidade (novo):** cada herói sorteia, ao ser criado, uma afinidade que faz 2 atributos crescerem
  mais (ex.: Vigoroso = Constituição+Força, Bruto = Força, Ágil = Destreza, Erudito = Inteligência,
  Devoto = Sabedoria, Carismático = Carisma). Aparece na ficha ao lado do traço
  ("Fanfarrão · Bruto") com setas de crescimento por atributo. Traços atuais mantêm seus efeitos.
- **Tela de subir de nível:** resumo do que mudou ("Nível 6! +3 PV, +1 dano, +1 Força").
- **ATQ e DEF crescem devagar** (≈ +4 de ATQ no nível 25); o crescimento forte vai para dano, PV e cura.
- Sensação de evolução: números que sobem de verdade + **árvore de habilidades** (próximo item abaixo),
  que substitui a ideia de "benefício a cada 5 níveis".

## 3. Itens fixos, com raridade e tiers (decidido: sem afixos sorteados)
- Itens **fixos**, gerados por modelo (tipo + tier + raridade) com stats previsíveis, 2–4 bônus
  cada (inclui atributos). Quantidade boa **por classe**: armas específicas por classe (2 por tier),
  demais espaços compartilhados, 1–2 lendários nomeados por classe. Ver também `EQUIPAMENTOS.md`
  (tiers 1–12, raridades, disciplina de poder).
- Raridade continua (Comum → Lendário); botão **"Equipar o melhor"** com comparação clara.
- **Nomes dos tiers: em aberto** (sem "Mithril/Adamante/Celestial"); ver opções em conversa.

## 4. Inimigos
- Cada espécie ganha os **6 atributos**, um perfil de crescimento (como a classe) e valores
  base (ATQ, DEF, PV, dado de dano) como hoje; o **nível vem do mapa** (+2 chefe, +1 líder).
- As mesmas contas dos heróis dão o resto. A `escala` atual (que só aumentava PV) deixa de existir.
- XP por inimigo passa a depender do nível dele.

## 5. Ordem de trabalho
1. Motor: atributos, afinidade, level up automático e inimigos com nível (sem mexer em telas; teste dos números).
2. **Árvore de habilidades** (spec + mockup antes; cooldown por turno; combinada com gatilhos) — antes de balancear.
3. Itens fixos por tier/raridade + "Equipar o melhor" + migração dos saves.
4. Telas (com mockup antes): ficha com 6 atributos e afinidade, resumo de nível, itens.
5. Calibração com a simulação (XP quase linear, nível por mapa, raridade por ato, limite de rodadas).
6. Testes de batalha completos nos mapas novos.
