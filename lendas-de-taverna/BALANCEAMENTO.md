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

## Chefes: entrada, fases e ideias futuras
- Entrada: `ent:'drop'` (cai do céu) ou `ent:'run'` (chega correndo); só depois do rugido aparecem o nome (estilo Dark Souls, só o nome) e a barra de vida. O chefe é invulnerável durante a entrada e as trocas de fase.
- Fases: limiares `BOSS_PH=[.66,.33]` — a cada fase fica mais rápido (+10 %), ataca mais depressa (−10 %) e usa as habilidades mais seguido.
- **Ideia para depois:** como a arte é por camadas, cada fase pode trocar uma peça (ex.: o Rei Esqueleto perde o elmo/ombreira e a armadura fica quebrada; o Grunk joga o escudo fora), gerando uma folha por fase e trocando `T.sheet` em `bossPhaseCheck`.
- Alvo do herói automático: o chefe tem preferência (até 70 px mais longe que o inimigo mais próximo), mas inimigos grudados no herói são atacados antes.
- Simulação: `tools/mmo/sim/boss.cjs <classe> <zona> <perfil> <níveis acima> <lutas>`; vida atual (base): Gorgash 1900, Grunk 2300, Morvath 2300.

## Chefes: postura (poise) e imunidade a knockback
- Chefes e mini-chefes não sofrem knockback nem são interrompidos por golpes comuns.
- Barra de postura oculta: acumula dano (crítico ×1.6); ao chegar a 4% da vida máxima o chefe fica "abalado" 1.4 s (dano extra) e depois ~8.6 s imune a nova quebra. Perde 0.4%/s de postura quando não apanha.
- Compensação da perda do stun por golpe: dano base dos chefes ×0.78 e fúria do Grunk ×1.2 dano / ×1.3 vel. / ×0.8 intervalo (antes 1.4 / 1.4 / .68).
- Alcance do herói é medido da borda do corpo (`T.rad`), então o herói não empurra o chefe.
- Simulação (Grunk, nv 12, equip. 'med', 3 lutas): guerreiro, ladino, clérigo e bardo matam em 60–165 s sem morrer; mago e arqueiro ainda morrem na fúria (arqueiro já falhava antes da mudança).

## Mini-chefe da Floresta: Xamã Skrix
- Evento "errante" da Floresta (~85% das vezes que o evento de mini-chefe sai). Arte vinda de folhas de IA (`tools/mmo/skrix_src`), montadas por `skrix_cut.py` + `skrix_export.py`.
- Habilidades: **Totem tóxico** (poça de veneno periódica; até 2; some em 13 s ou quando destruído), **Maldição** (dot + enfraquecido por 10 s; quebra ao destruir os totens), **Chamado da tribo** (3 goblins + escudo que reduz o dano a 12% por até 12 s ou até os adds morrerem), **Fuga** a 35% de vida (teleporta e finca um totem grande).
- IA do herói em modo automático: com escudo ativo ataca os adds; com maldição ativa ataca o totem mais próximo (`skPrio`).
- Dificuldade ainda não balanceada de propósito (o jogo segue em modo automático para testes).

## Drops únicos por chefe
- Cada chefe tem seus únicos (`bk`): Grunk (Cutelo, Elmo Cornudo, Botas Pesadas), Morvath (Lâmina do Rei Esqueleto, Coroa Gélida, Manto de Ossos), Gorgash (Clava e Couro Grosso). Chance de único: 10% por morte.
- Mini-chefes: Skrix (Cajado, Colar de Dentes, Máscara de Osso) e Morcego-Vampiro (Presa, Garras), 6% por morte. Cada único respeita a classe (`cls`).
- Força: o `mul` de cada único agora é o múltiplo da força de um Épico (atributos base e afixos). Chefe 1.3, mini-chefe 1.2, únicos de área 1.25. Medido por simulação (ilvl 8/14/25): único de chefe ≈ 1.4× Épico, de mini-chefe ≈ 1.3×, peça de conjunto ≈ 1.15×, Épico ≈ 1.5× Mágico (antes o único era ≈ 2× Épico). Itens já salvos mantêm os atributos de quando caíram.
- Regra para a futura Arena do Chefe: precisa ser uma escolha. Menos experiência e mais chance de único, enquanto a dungeon completa dá mais experiência e menos chance de único. Nunca melhor nos dois.
- Variedade: cada chefe tem 1 arma única para cada uma das 6 classes + 3 peças (4 opções por classe); cada mini-chefe, 1 arma por classe + 2 peças (3 opções). Nenhuma classe sai na frente; o sorteio escolhe entre as opções válidas da classe.
- Chances atuais: único de chefe 10%, de mini-chefe 6% (a dungeon completa manda mais XP; a futura Arena terá chance maior e XP menor).
- A chance de único cai com o NÍVEL da dungeon, não com a posição na lista: fator = (8 / nível do chefe)^0,8. Chefe: 10% (Nv 8), 6,8% (Nv 13), 4,3% (Nv 23), 2,6% (Nv 43), ~2% (Nv 60). Mini-chefe: 60% desses valores. Várias dungeons na mesma faixa de nível têm a mesma chance.

## Poder de combate (PC) e nível necessário dos itens
- PC do item = pontuação dos atributos (ataque×3, defesa×2, vida×0,35, crítico%×4, velocidade%×1,5, empurrão×1,2, queda×0,4), com o aprimoramento. Aparece na ficha do item.
- PC do herói = a mesma fórmula sobre os atributos finais (inclui nível, atributos, talentos e conjuntos). Aparece na aba Equip. do personagem.
- Nível necessário do item = início da faixa do tier (Tier 1 = nv 1, Tier 2 = nv 6, Tier 3 = nv 11…). Itens acima do nível não equipam (nem pelo auto-equipar); itens já equipados em saves antigos continuam.

## Poder de combate recomendado por dungeon (calibração)
Simulação (`tools/mmo/sim/pc_calib.cjs` e `boss.cjs`, herói automático, equipamento 'med', luta contra o chefe):
| Dungeon | Chefe (nível) | Perde com PC | Vence com folga com PC | PC recomendado |
|---|---|---|---|---|
| 1 Floresta dos Goblins | Grunk (8) | ≤ 460 | ≥ 570–610 | **600** |
| 2 Catacumbas | Morvath (13) | ≤ 984 | ≥ 1090–1185 | **1100** |
| 3 Floresta de Brumavale | Gorgash (18) | ≤ 870 | ≥ 1056–1214 | **1200** |
| 4 Esgotos | Gorgash (23) | ≤ 1247 | ≥ 1366 | **1400** |
- PC típico de um herói 'med' no nível do chefe: 432 / 717 / 986 / 1325 (as 6 classes ficam dentro de ±12%). Ou seja, os chefes 2 a 4 exigem equipamento acima do 'médio'.
- **Alerta de balanceamento:** o Morvath exige quase o dobro do poder do Grunk (1100 contra 600) e é o salto mais brusco; Gorgash fica em 1200 e 1400. Candidato a ajuste quando formos mexer na dificuldade.
