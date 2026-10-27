# Status (buffs e debuffs) — implementado na branch (v1)

Valem para heróis **e** inimigos. Duração em turnos **do alvo** (contam no início do turno dele). Mostrados como ícones
pequenos ao lado da barra de vida e na lista de turno, com o turno restante.

## Debuffs
| Grupo | Status | Efeito | Duração | Empilha |
|---|---|---|---|---|
| Dano contínuo | **Veneno** | 6% do PV máx. por turno (mín. 2) | 3 | até 3× |
| | **Queimadura** | 8% do PV máx. por turno; Gelo apaga | 3 | não |
| | **Sangramento** | 3 de dano por casa que o alvo anda (+1d4 no início do turno) | 3 | até 2× |
| Controle | **Atordoado** | perde o próximo turno | 1 | não |
| | **Preso** | não anda, ainda pode atacar | 2 | não |
| | **Lento** | −2 Movimento | 2 | não |
| | **Gelado** | Lento + −1 ATQ; Fogo remove | 2 | não |
| | **Medo** | foge do causador | 2 | não |
| | **Provocado** | só pode atacar quem provocou | 2 | não |
| Fraqueza | **Abalado** | −2 DEF | 2 | não |
| | **Enfraquecido** | −25% de dano | 2 | não |
| | **Marcado** | recebe +20% de dano de todos | 2 | não |
| | **Cego** | −4 ATQ | 2 | não |

## Buffs
| Status | Efeito | Duração |
|---|---|---|
| **Inspirado** | +N de acerto no próximo golpe (já existe) | 1 golpe |
| **Fortalecido** | +20% de dano | 2 |
| **Protegido** | +2 DEF | 2 |
| **Escudo** | absorve X de dano (X = 15 + nível) | até acabar / 3 |
| **Regeneração** | recupera 4% do PV máx. por turno | 3 |
| **Veloz** | +2 Movimento | 2 |
| **Foco** | +2 de margem de crítico | 2 |
| **Inabalável** | imune a controle e −30% de dano recebido | 2 |
| **Furtivo** | o próximo golpe é crítico e não pode ser alvo à distância | até atacar |

## Regras
- **Mesmo status** renova a duração (não soma), exceto os que empilham.
- **Sem imunidade após controle** (decisão do dono): o mesmo alvo pode ser controlado em sequência; o limite fica nas recargas das habilidades, na regra de chefes e em Inabalável.
- **Chefes:** imunes a Atordoado e Medo (viram Abalado); Preso e Lento duram 1 turno. **Líderes:** controle dura metade.
- **Fogo × Gelo:** Queimadura remove Gelado e Gelado remove Queimadura. Fogo em alvo Gelado, ou Gelo em alvo Queimando
  (Choque Térmico), causa +50% de dano e remove o status.
- **Limpeza:** Purificar remove todos os debuffs de um aliado; Canção de Vigor remove Medo.
- **Tags** usadas pelas passivas: **[DoT]** veneno/queimadura/sangramento · **[Controle]** atordoado/preso/lento/gelado/medo/provocado ·
  **[Fraqueza]** abalado/enfraquecido/marcado/cego.
