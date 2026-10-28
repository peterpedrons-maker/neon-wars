# Itens — especificação final (fixos, por tier e raridade)

Substitui o catálogo de 80 itens e a ideia de afixos sorteados. Itens são **fixos**, gerados por
modelo (tipo × tier × raridade), com stats previsíveis. Tudo calculado por `tools/sim_endgame.py`.

## 1. Tiers (um por ato; 11 e 12 são endgame)
| Tier | Nome | Origem | Nível mínimo |
|---|---|---|---|
| 1 | Rústico | Vale | 1 |
| 2 | Rúnico | Ruínas | 6 |
| 3 | Basáltico | Cavernas | 11 |
| 4 | Boreal | Picos Gelados | 16 |
| 5 | Sepulcral | Cripta | 21 |
| 6 | Crepuscular | Brumavale Sombria | 26 |
| 7 | Profundo | Ruínas Profundas | 31 |
| 8 | Ancestral | Magma Ancestral | 36 |
| 9 | Eterno | Picos Eternos | 41 |
| 10 | Esquecido | Cripta Esquecida | 46 |
| 11 | Régio | Endgame | 51 |
| 12 | Primordial | Endgame | 56 |
Nome do item = tipo + estilo do tier ("Espada Basáltica", "Elmo Boreal"). Tier 1 e 2 em diante
só aparecem em mapas do ato correspondente (e acima).

## 2. Raridade
| Raridade | Linhas de bônus | Fator | Como aparece |
|---|---|---|---|
| Comum | 2 | 0,6 | drop comum |
| Raro | 2 | 0,8 | drop comum |
| Mágico | 3 | 1,0 | drop comum; mínimo garantido em chefe |
| Épico | 3 | 1,25 | drop comum (raro nos primeiros atos); garantido em dungeon secreta |
| Lendário | 4 | 1,5 | **escrito à mão**, nome próprio; só de chefe final, dungeon secreta ou endgame |

Chance de raridade no drop (Comum/Raro/Mágico/Épico) por tier: T1–2 65/28/7/0 · T3–4 50/30/17/3 ·
T5–6 40/32/21/7 · T7–8 30/32/27/11 · T9–10 22/30/31/17 · T11–12 15/25/35/25.
Drop: 16% por inimigo (+ bônus de Carisma), chefe sempre.

## 3. Valor de cada linha (tier t, fator f)
- **Atributo** (+Força etc.): round((1 + 0,35·(t−1)) · f)
- **Dano**: round(0,4·t·f) · **PV**: round(1,2·t·f) · **ATQ** (só arma e luvas): round(t/6·f)
- **DEF** (corpo, cabeça, pés, escudo) e **Res. Mágica**: round(t/8·f)
- **Crítico** +1 só em Épico/Lendário a partir do tier 6 · **Mov/Alc**: +1 em poucos itens (pés, armas de longe)
Ex.: Espada Esquecida Épica (tier 10, f 1,25): +5 Força, +5 dano, +2 ATQ.

## 4. Espaços e linhas (ordem de prioridade; a raridade define quantas valem)
| Espaço | Linhas |
|---|---|
| Arma (por classe) | atributo principal · dano · ATQ · crítico |
| Corpo | pesada/média: Constituição · DEF · PV · Res. Mág. · leve/tecido: atributo principal · Res. Mág. · PV · DEF |
| Cabeça | atributo secundário · PV · DEF · ATQ |
| Mãos | atributo principal · ATQ · dano · DEF |
| Pés | atributo secundário · DEF · PV · (Mov) |
| Mão secundária | escudo: secundário · DEF · PV · Res. Mág. · adaga: principal · ATQ · dano · crítico (Mago, Arqueiro, Bardo não usam) |
| Acessórios (2) | principal · secundário · PV · DEF/Res. Mág. |
Principal/secundário por classe: Guerreiro Força/Const. · Ladino Destreza/Const. · Mago Inteligência/Sabedoria ·
Clérigo Sabedoria/Const. · Arqueiro Destreza/Const. · Bardo Carisma/Destreza.

## 5. Famílias por classe (nomes; cada uma existe nos 12 tiers)
- **Armas** (2 por classe): Guerreiro espada · machado | Ladino adaga · rapieira | Mago cajado · varinha |
  Clérigo maça · martelo | Arqueiro arco curto · arco longo | Bardo alaúde · flauta.
- **Armadura**: pesada (Guerreiro), média (Clérigo), leve (Ladino, Arqueiro, Bardo), tecido (Mago); 4 peças cada
  (elmo/couraça/manoplas/grevas · capuz/gibão/luvas/botas · chapéu/manto/luvas finas/sandálias…).
- **Escudos** (Guerreiro, Clérigo) e **adagas reservas** (Ladino); **acessórios**: anel, amuleto, talismã, bracelete,
  um por atributo (+ vida e defesa).
- **Lendários nomeados:** 1 por classe nos tiers 5, 10 e 12 (18 itens), de chefes finais e dungeons secretas.
Isso dá ~39 modelos por tier × 12 tiers × 5 raridades gerados, sem sorteio de afixo.

## 6. Quality of life
- Botão **"Equipar o melhor"**: escolhe a peça de maior pontuação por espaço (itemScore) respeitando classe e mãos.
- Comparação clara em cada item (já existe `itemDiff`); vender item sobrando por ouro.
- Itens antigos do save viram o modelo mais próximo (tier 1–2) com a mesma raridade.

## 7. O que a simulação mostrou (herói de nível N, kit completo da raridade indicada, sem habilidades)
Ver `tools/sim_endgame.py`. Resumo no relatório da conversa; pontos de ajuste encontrados:
1. **Clérigo bate fraco** (~12–24 por golpe e acerta 25–40%): atacar com Sabedoria, não com Força.
2. **Heróis passam dos inimigos no fim**: DEF e dano de item + atributo deixam inimigos acertando 5–20%.
   Precisa de teto de DEF/ATQ e de crescimento maior do inimigo (DEF por nível, PV/dano).
3. **Mago é o único frágil** (PV ~110–150): bom, é a identidade da classe.
4. Crítico sobe sem limite com Inteligência (Mago): limitar a +6.

---
## Implementado (v1)
- Itens gerados por molde × tier × raridade (`genItem`), id `molde.tier.raridade` (ex.: `espada.6.3`); `itemById` reconstrói qualquer item (saves antigos com os 17 itens antigos continuam válidos).
- Moldes por classe (armas, 4 peças de armadura por grupo pesada/média/leve/tecido, escudo/adaga reserva, 6 acessórios por atributo). Itens de uma classe só servem a ela (`item.cls`).
- Linhas e valores seguem as fórmulas deste documento; atributos de item entram na conta dos atributos (`h.itemAttr`) e rebatem em dano/crítico/PV.
- Drop: tier = ato do mapa (25% de vir do tier anterior; chefe pode subir 1), classe/espaço sorteados entre o grupo (loot útil), raridade pela tabela por tier (chefe: Mágico no mínimo). Lendário não rola.
- **Equipar o melhor** (`equipBest`): por herói e "em todos" no Cofre, e por herói na mochila da missão; pontuação por classe (`heroScore`: atributo principal 3, secundário 2, Constituição 1,5).
- Corrigido: tirar item de herói pelo Cofre (seletor errado no clique).
