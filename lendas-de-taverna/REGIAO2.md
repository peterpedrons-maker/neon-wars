# Região 2 — Terras Áridas de Cinzamuro (Nv 10–20) — PROPOSTA (dono aprovou o rumo; ainda NADA construído)

Esboço: `docs/regiao2_esboco.png` (gerado por `tools/mmo/esboco_regiao2.py`; editar o script e regerar).

## Decisões do dono
- A Cidade 2 é uma **cidade-fortaleza** (não uma cidade de montanha): a Região 1 termina no Passo da Montanha, o guarda protege a passagem e do outro lado, na terra seca, fica a fortaleza.
- **Região maior** que a 1ª (a 1ª é o tutorial): mapas maiores (~7–8 mil px), mais zonas, **inimigos mais agressivos e mais fortes**.
- Terreno **montanhoso, seco, árido**; inimigos sempre **condizentes com o terreno** (nada de animal de floresta no deserto).
- **Mesmo estilo de nomes** da Região 1 (Brumavale, Planície de…, Passo da…, Floresta dos…). Nome da cidade escolhido por mim: **Cinzamuro**.
- **Pelo menos 5 dungeons novas** (≈7 no total contando Cripta e Esgoto), todas Nv 15–20, drops próprios.
- Chefes de caçada ficam sempre no mapa; a caçada fica oculta e já nasce concluída ao matar (regra do CLAUDE.md).

## Cinzamuro (cidade-fortaleza, hub, Nv 10)
Muralha de pedra cinza sobre uma mesa rochosa, portão do Passo ao sul. Três bairros, um por facção: **Bastião da Ordem** (Registros, Maren/Hilda de volta como contatos), **Mercado do Muro** (Guildas: lojas, Guilda dos Caçadores, leilão), **Bairro Baixo** (Remanescentes: informantes, contrabando). Portal fixo das dungeons e teleporte entre cidades. Ato 2 da história (Nv 11–20): disputa pelo novo Escolhido e investigação dos Registros.

## Zonas (23; saída norte = Portão do Deserto → Região 3, mesmo molde do Portão do Passo: guarda + missão "Abrir o Portão" no Nv 20 com 3 de 4 chefes de zona)
**Caminho principal:** Cinzamuro → Estrada da Muralha (10–11) → Planalto Árido (10–12) → Garganta do Vento (12–13) → Mesas Rubras (13–15) → Leito do Rio Seco (14–15) → Salinas Brancas (15–17) → Desfiladeiro Rubro (17–18) → Vale das Forjas Mortas (18–20) → Portão do Deserto (19–20).
**Desvios:** Cânion do Eco (12–14, oeste do Planalto) · Caminho dos Cercos (16–17) → Campo dos Cercos (17–19) · Trilha dos Abutres (15–16) → Ruínas do Sol Caído (16–18).
**Secretas (becos, baú/hunt):** Oásis Escondido (11–12), Mirante dos Abutres (12–13), Tumba do Nômade (14–15), Cisterna Antiga (14–15), Acampamento dos Saqueadores (17–18), Covil do Verme (18–19, entrada do Ninho do Verme), Gruta de Obsidiana (19–20).

## Chefes de zona e inimigos (por terreno)
| Zona | Chefe (mini) | Inimigos novos (Nv do jogo todo = a reserva do BESTIARIO) |
|---|---|---|
| Planalto Árido | Matriarca Escorpião | escorpião, lagarto-de-pedra, chacal, bandido do deserto, abutre |
| Cânion do Eco | Capitão Vento-Seco (bandido) | bandido arqueiro, harpia do cânion, aranha de cristal, morcego gigante |
| Mesas Rubras | Rei das Mesas (troll) | troll das mesas, golem de pedra, lobo-da-poeira, ogro do deserto |
| Salinas Brancas | Rainha Escorpião | escorpião de sal, kobold mineiro, golem de sal, aranha de cristal |
| Ruínas do Sol Caído | Hierofante Solar | múmia, escaravelho, cultista do sol, gárgula de areia, esfinge menor |
| Campo dos Cercos | Marechal Sem-Nome | cavaleiro negro, armadura assombrada, arqueiro de elite, cão de guerra, mago de batalha |
| Vale das Forjas Mortas | Titã de Magma | salamandra, imp, golem de magma, cão infernal, anão renegado |
Mini-chefes por zona a definir. Cada inimigo precisa de **silhueta própria** (BESTIARIO.md) e anim própria.

## Dungeons novas (Nv 15–20, ao lado de Cripta e Esgoto)
1. **Minas de Sal Esquecidas** (Salinas Brancas): kobolds, golems de sal, aranhas de cristal; chefe Rei Kobold Cristalino.
2. **Templo do Sol Soterrado** (Ruínas do Sol Caído): múmias, escaravelhos, cultistas; chefe Hierofante Solar (versão dungeon) ou a Rainha Múmia.
3. **Bastilha Negra** (Campo dos Cercos): fortaleza caída; cavaleiros negros, armaduras assombradas; chefe Marechal Sem-Nome.
4. **Forja de Pedranegra** (Vale das Forjas Mortas): anões renegados, golems de magma; chefe Mestre-Forjador Corrompido.
5. **Ninho do Verme das Areias** (Covil do Verme, secreta): vermes, aranhas; chefe Verme Ancestral.
Cada uma com entrada física na zona + portal fixo em Cinzamuro; drops/conjuntos próprios (armas por subclasse). Níveis de dungeon são da dungeon, não da zona.

## Dificuldade (Região 1 = tutorial)
Fatores da região (a implementar em `region`): aggro ×1,5, leash maior, grupos de 3–5, mais elites (~15%), vida ×1,4 e dano ×1,3 sobre a curva atual de nível, menos "zona segura". Caçadas novas (hunts) com puzzle, no padrão Maragon/Gigante.

## Ordem de construção sugerida
Cinzamuro (cidade) + Estrada da Muralha + Planalto Árido → testar saída do Passo (guarda/portão e fade) → Cânion do Eco → resto do caminho principal → desvios + dungeons → secretas → hunts. Antes: confirmar o esboço com o dono.
