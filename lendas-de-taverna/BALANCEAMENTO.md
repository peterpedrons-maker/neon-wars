# Balanceamento — análise do estado atual (antes de mexer)

Números tirados do código (`index.html`) e de um modelo simples (grupo de 5: guerreiro,
ladino, mago, clérigo, arqueiro; sem itens; sem cura; inimigos "médios" do pool de cada
mapa). Serve pra ver tendência, não pra decidir valor final.

## 1. O que o personagem ganha ao subir de nível
Por nível (`applyLevelUps`): **+1 PV máximo** e **+1 no atributo primário da classe**
(Bardo: +1 em dois). Nada mais. **ATQ e DEF nunca sobem com o nível.**

Atributos viram bônus (`recomputeAttrBonus`): dano = ⌊(Força+Inteligência)/3⌋, crítico =
⌊Destreza/10⌋, PV extra = ⌊Vitalidade/2⌋, cura = ⌊Fé/3⌋. Vitalidade não é primária de
ninguém, então não cresce.

| Classe | Primário | O que o nível realmente dá |
|---|---|---|
| Guerreiro | Força | +1 PV/nível; +1 dano a cada 3 níveis |
| Mago | Inteligência | +1 PV/nível; +1 dano a cada 3 níveis |
| Bardo | Int + Destreza | +1 PV/nível; +1 dano a cada 3 níveis; +1 crítico a cada 10 |
| Ladino / Arqueiro | Destreza | +1 PV/nível; **dano não cresce**; +1 crítico a cada 10 níveis |
| Clérigo | Fé | +1 PV/nível; **dano não cresce**; +1 de cura a cada 3 níveis |

Exemplo (sem itens), PV / dano médio por golpe:
Guerreiro Nv1 31 / 10,5 → Nv20 50 / 16,5 → Nv60 90 / 29,5.
Ladino Nv1 21 / 8,5 → Nv60 80 / 8,5. Arqueiro 19 / 7,5 → 78 / 7,5. Clérigo 23 / 5,5 → 82 / 5,5.

Curva de XP: custo do nível ×1,18 por nível (100, 118, 139…). XP acumulado: Nv10 1,9 mil ·
Nv20 12 mil · Nv30 67 mil · Nv40 353 mil · Nv50 1,8 milhão · Nv60 9,7 milhões.

## 2. O que o equipamento dá
8 espaços (arma, mão secundária, cabeça, corpo, mãos, pés, 2 acessórios). Cada item soma
em ATQ, DEF, Mov, Alc, dano, PV, crítico ou segredos. Raridade 1–5; ordem de grandeza:
- Comum: +1 em algo. Raro: +2. Mágico: +2 a +4. Épico: +3 a +6. Lendário: +4 a +5 ATQ/DEF,
  +8 a +14 PV, +6 a +8 de dano.
- Kit máximo (8 lendários): ≈ +16 ATQ, +19 DEF, +14 dano, +40 PV, +4 crítico.
- **Itens são a única fonte de ATQ/DEF** do herói.
- Drop: 16% por inimigo morto; chefe 100% (raridade mínima 3). Raridade sorteada
  50/28/14/6/2%, **igual em qualquer mapa** (não depende do nível/ato).
- Itens não têm nível mínimo e não escalam.

## 3. Como o inimigo escala (`makeEnemy`)
Só a **vida** cresce com `escala` (PV × escala). ATQ ganha no máximo +2 e DEF +1 (a
partir de escala 1,25). **O dado de dano do inimigo nunca muda.** Resultado: um Goblin da
escala 9,8 tem ~88 PV, mas bate 1d6+1 como no mapa 1.

Acerto: d20 + ATQ ≥ DEF (1 sempre erra, 20 sempre acerta/critica). O ATQ dos heróis fica
em 2–5 a campanha toda, então a chance de acertar é quase fixa (~45–70%).

## 4. Consequência (modelo, sem itens)
| Mapa | Escala | PV total dos inimigos | Dano do grupo/rodada | Rodadas p/ vencer | Nível do herói (XP real estimado) | Nível recomendado (rótulo) |
|---|---|---|---|---|---|---|
| 1 | 1,0 | 38 | 29 | 1,3 | 1 | 1 |
| 10 | 2,1 | 257 | 25 | 10 | 7 | 10 |
| 25 | 3,9 | 532 | 27 | 20 | 13 | 25 |
| 31 | 5,0 | 719 | 29 | 25 | 14 | 30 |
| 43 | 7,4 | 900 | 29 | 31 | 17 | 40 |
| 55 | 9,8 | 1336 | 29 | 46 | 19 | 50 |

- O dano do grupo fica parado (~27–31/rodada) enquanto a vida dos inimigos cresce ~35×.
  A batalha tem **limite de 24 rodadas**: a partir do mapa ~24 o modelo já passa disso.
- Pela curva de XP atual (~100–330 XP por herói por mapa), o herói chega só a **Nv ~13
  no fim da Run 1 e ~19 no fim da Run 2**. Os rótulos de nível recomendado (25 e 50) e
  o teto Nv 60 não são alcançáveis.
- Mesmo com Nv 19, o nível quase não muda o herói (+18 PV, +3 a +6 de dano). O que decide
  é o item, que depende de sorte e não acompanha o mapa.

## 5. Decisões que precisam ser tomadas
1. **Quanto o nível deve valer.** Hoje vale pouco (PV+dano). Opções: subir ATQ/DEF com o
   nível (ex.: +1 ATQ a cada 4 níveis, +1 DEF a cada 5), e/ou dar dano também a
   Ladino/Arqueiro/Clérigo (hoje não crescem).
2. **Como o inimigo escala.** Em vez de só PV×escala, subir também ATQ/DEF/dano de forma
   moderada (senão fica "saco de PV" e o grupo nunca morre, só demora).
3. **Curva de XP e nível máximo.** Ajustar custo por nível e XP por mapa pra que Nv ~25
   caia no fim da Run 1 e ~50 no fim da Run 2 (como combinado), ou mudar os rótulos.
4. **Itens por ato.** Raridade/qualidade dependendo do mapa (nível do item), ou teto
   de raridade por ato, em vez de 50/28/14/6/2 fixo.
5. **Limite de rodadas (24)** e o que acontece ao estourar.
