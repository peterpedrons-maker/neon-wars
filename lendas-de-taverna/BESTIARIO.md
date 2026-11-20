# Bestiário de Hearthblade (nível 1–60) — NÃO REPETIR inimigos

Leia antes de criar qualquer inimigo. Regras do dono: inimigos combinam com o **chefe da área** (estilo WoW), podem ser animais, humanoides ou criaturas; cada um com **silhueta própria** (nada de "herói com outra cor"); sprite de **uma peça só** (`fauna.py`/`fauna2.py` para criaturas, `chibi.py` para humanoides); nada de "animal mago/arqueiro". Ao usar um inimigo numa área, marque abaixo.

## Áreas atuais (chefe → inimigos)
| Área | Chefe / mini | Inimigos (✔ no jogo, ○ esboço pronto, … ideia) |
|---|---|---|
| Floresta dos Goblins | Grunk / Xamã Skrix + Totem | ✔ goblin, ✔ xamã · ✔ cogumelo andante, ✔ aranha-da-mata, ✔ lobo selvagem, ✔ goblin sapador · … goblin sapador (explode), … goblin ladrão |
| Catacumbas | Morvath / Morcego-Vampiro | ✔ esqueleto, ✔ esq. mago/fogo/gelo, ✔ morcego · ✔ carniçal, ✔ cavaleiro caído, ✔ múmia, ✔ necromante aprendiz, ✔ aranha |
| Floresta de Brumavale | Gorgash (ogro) / Presa-de-Ferro (javali) | ✔ javali selvagem, ✔ javali bruto · ✔ ogrinho, ✔ gnoll, ✔ tronco vivo, ✔ harpia, ✔ bandido, ✔ lobo, ✔ ogro lenhador |
| Esgotos | Rei dos Ratos / Boticário Podre | ✔ rato gigante, ✔ rato assassino, ✔ homem-rato, ✔ sapo-do-esgoto, ✔ cobra, ✔ barata gigante, ✔ afogado, ✔ ladrão de esgoto, ✔ cultista do lodo · ○ lodo (slime) |
| Cripta do Rei Esquecido | Rei Esquecido | ✔ guarda-caveira, cultista, espectro, gárgula, zumbi sineiro |
| Pântano das Brumas | (goblins emprestados) | … a definir (sapo, cobra, sanguessuga, fogo-fátuo, troll do pântano, lagarto-homem) |

Esboços: `mmo/proto_pixel/bestiario_*.png`, código em `tools/mmo/pxengine/data/fauna.py`, `fauna2.py`, `bestiario_sheet.py`.

## Reserva para níveis mais altos (temas WoW/fantasia; NÃO usados ainda)
- **Montanha/gelo:** troll de gelo, yeti, lobo-do-gelo, golem de gelo, elemental de gelo, gigante da montanha, harpia-das-neves, mamute.
- **Deserto/ruínas:** escorpião gigante, múmia-rainha, escaravelho, djinn, gárgula de areia, nagas, cultista do sol, esfinge, tuaregue-ladrão.
- **Vulcão/fogo:** elemental de fogo, salamandra, cão infernal, imp, golem de magma, ogro de fogo, drake menor.
- **Selva/costa:** troll da selva, pantera, ave-do-trovão, murloc-like (homem-peixe), caranguejo gigante, náiade, krakens menores, pirata/contrabandista.
- **Floresta fada/corrompida:** ent anciã, dríade corrompida, lobisomem, vampiro, bruxa, fada sombria, espírito da floresta, corvo gigante.
- **Ruínas anãs/minas:** anão renegado, kobold, golem de pedra, verme das minas, aranha de cristal, morcego gigante, mineiro morto-vivo.
- **Castelo/cavaleiros:** cavaleiro negro, arqueiro de elite, mago de batalha, gárgula, armadura assombrada, inquisidor, cão de guerra.
- **Planos/abismo (nível 50–60):** demônio menor, súcubo, cavaleiro da morte, aberração, devorador de mentes, dragão jovem, lich, arconte caído.
- **Chefes futuros sugeridos:** sapo gigante do esgoto (já aprovado), rei troll, rainha aranha, lich, dragão, senhor do fogo, rei dos mortos, hidra, titã de gelo.

### Caçadas (hunts)
- **Presa-Lunar, o Alfa da Matilha** (lobo gigante, Planície de Brumavale): alvo da caçada "O Silêncio da Matilha" (10 lobos + 10 s parado perto da água). Usa o sprite do lobo ×1,45. Kit: bote + Uivo.
- **Ancião Cornalvo** (cervo branco gigante, galhada dourada que varre para trás com cipós pendurados, juba de musgo, runas douradas no flanco, olhos âmbar; RARO pacífico da Planície de Brumavale, ~60% ao entrar na zona, Nv 40 mostrado como "Nv.??"): não ataca ninguém; se ferido enfurece. Imune a debuffs/atordoar/empurrão. Kit: Chifrada, Pisada do Ancião (raízes), Investida Sagrada (galhada espectral), Bramido (aurora + medo), Couraça de Casca (dano −65% + regeneração 7 s), Raízes Ancestrais (galhadas de cristal prendem), Fúria Ancestral aos 35%. Sprite próprio `cervo.py` (atlas `cx_cervo`).
