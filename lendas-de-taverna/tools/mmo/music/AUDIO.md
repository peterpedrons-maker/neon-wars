# Áudio do Hearthblade — cobertura por mapa

| Mapa | Música | Ambiente | Efeitos |
|---|---|---|---|
| Cidade | `vila` | vento, pássaros, sino distante, cachorro, martelo, murmúrio (`ambStart('town')`) | UI, passos, combate |
| Interiores (ferreiro, mercador, mestre, alquimista, leilão, cofre) | forja / vila / formacao / templo / taverna / cofre | lareira, murmúrios, rangidos, tilintar (`ambStart('room')`) | UI |
| Floresta dos Goblins | `floresta_goblin` | vento, corvo, coruja, grilos à noite | vozes de goblin |
| Floresta de Brumavale (javalis) | `floresta_javali` | pássaros, javali ao longe | vozes de javali |
| Catacumbas (esqueletos) | `cripta_esq` | gotas, ossos, correntes, sussurros | estalos de ossos |
| Esgotos (ratos) | `esgoto_rato` | gotas, correria, guinchos, bolhas | guinchos de rato |
| Cripta do Rei Esquecido | `cripta_rei` (novo) | coro distante, tochas, porta de pedra, sino, gotas, sussurros | esqueletos + chefe |

Vozes (`mob_<espécie>_<atk|hurt|die>`): rato, javali, goblin, esq, bat, ogro. Chefes: `boss_*` (rugido, pancada, investida, giro, guarda, enxame, praga, escavar, frasco, sombrio) e `dg_title`.
Geradores: `mobsfx.py` (voz por formantes + metais/coro/tímpano reais), `cripta_rei.py` (música), `sfx2.py`, `floresta.py`, `cripta.py`, `esgoto.py`. Precisam de `/tmp/aud` (lib.py, GeneralUser-GS.sf2).

## Abertura (título, criação, cutscene)
| Tela | Música | Efeitos |
|---|---|---|
| Título | `titulo_mmo` (Ré menor, 76 bpm, 32 compassos: trompa, cordas, coro, harpa, tímpano, metais) | — |
| Criação de personagem | `criacao` (Sol maior, 72 bpm: violão de nylon, flauta, oboé, harpa, cordas) | — |
| Cutscene (painéis) | `abertura` (Ré menor, 52 bpm: órgão, coro, cordas em tremolo, violoncelo solo, corne inglês, sinos) | `cut_marca` (mão marcada e marca que brilha), `cut_queda` (o Escolhido caído), `cut_sino` (sino da torre) |
| Cutscene (panorama de Brumavale) | `amanhecer` (toca uma vez, ~29 s, depois entra `vila`) | ambiente da cidade volta |

Gerador: `abertura_mmo.py` + `lib2.py` (partitura em código → instrumentos reais do GeneralUser GS via `tinysoundfont` → reverb → ogg). `python3 abertura_mmo.py all`.

## Cervo (Ancião Cornalvo)
`cervo_sfx.py` gera os 12 sons `cervo_*` (voz por formantes + sinos/glockenspiel/celesta/harpa/tímpano do GeneralUser GS). Ver CLAUDE.md "SONS DO ANCIÃO CORNALVO".
