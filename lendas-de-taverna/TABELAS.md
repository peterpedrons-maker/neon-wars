# TABELAS DO JOGO (geradas do código — `node tools/mmo/gen_tabelas.cjs`)

Tudo aqui é lido do jogo real; para atualizar depois de mexer em XP, inimigos ou classes, rode o gerador de novo.

## 1. Curva de XP do personagem

- XP para subir do nível N para N+1: `38 × N^1.6 + 30` (`xpNeed`).
- **Abates padrão**: quantos monstros PADRÃO do nível N são precisos para subir (`KPL`). **XP do padrão** = XP necessário ÷ abates. Todo monstro dá `XP do padrão × peso do monstro` (peso ≈ 1 para monstro comum; elite ×2 / ×3,5; chefe usa o peso da tabela abaixo).
- Monstros muito abaixo do nível do herói dão cada vez menos XP (diferença de 3 níveis = ×0,85 … 8 níveis = 0).

| Nível | XP p/ subir | Abates padrão | XP do monstro padrão | XP acumulado até o nível |
|---:|---:|---:|---:|---:|
| 1 | 68 | 10 | 6.8 | 0 |
| 2 | 145 | 13 | 11.2 | 68 |
| 3 | 250 | 18 | 13.9 | 213 |
| 4 | 379 | 23 | 16.5 | 463 |
| 5 | 529 | 29 | 18.2 | 842 |
| 6 | 698 | 36 | 19.4 | 1371 |
| 7 | 885 | 44 | 20.1 | 2069 |
| 8 | 1089 | 52 | 20.9 | 2954 |
| 9 | 1308 | 61 | 21.4 | 4043 |
| 10 | 1543 | 70 | 22.0 | 5351 |
| 11 | 1792 | 80 | 22.4 | 6894 |
| 12 | 2055 | 90 | 22.8 | 8686 |
| 13 | 2332 | 101 | 23.1 | 10741 |
| 14 | 2622 | 113 | 23.2 | 13073 |
| 15 | 2924 | 124 | 23.6 | 15695 |
| 16 | 3239 | 137 | 23.6 | 18619 |
| 17 | 3566 | 140 | 25.5 | 21858 |
| 18 | 3905 | 140 | 27.9 | 25424 |
| 19 | 4255 | 140 | 30.4 | 29329 |
| 20 | 4616 | 140 | 33.0 | 33584 |
| 21 | 4988 | 140 | 35.6 | 38200 |
| 22 | 5371 | 140 | 38.4 | 43188 |
| 23 | 5765 | 140 | 41.2 | 48559 |
| 24 | 6169 | 140 | 44.1 | 54324 |
| 25 | 6584 | 140 | 47.0 | 60493 |
| 26 | 7008 | 140 | 50.1 | 67077 |
| 27 | 7443 | 140 | 53.2 | 74085 |
| 28 | 7887 | 140 | 56.3 | 81528 |
| 29 | 8340 | 140 | 59.6 | 89415 |
| 30 | 8804 | 140 | 62.9 | 97755 |
| 31 | 9276 | 140 | 66.3 | 106559 |
| 32 | 9758 | 140 | 69.7 | 115835 |
| 33 | 10249 | 140 | 73.2 | 125593 |
| 34 | 10749 | 140 | 76.8 | 135842 |
| 35 | 11258 | 140 | 80.4 | 146591 |
| 36 | 11775 | 140 | 84.1 | 157849 |
| 37 | 12302 | 140 | 87.9 | 169624 |
| 38 | 12837 | 140 | 91.7 | 181926 |
| 39 | 13380 | 140 | 95.6 | 194763 |
| 40 | 13932 | 140 | 99.5 | 208143 |
| 41 | 14492 | 140 | 103.5 | 222075 |
| 42 | 15061 | 140 | 107.6 | 236567 |
| 43 | 15637 | 140 | 111.7 | 251628 |
| 44 | 16222 | 140 | 115.9 | 267265 |
| 45 | 16815 | 140 | 120.1 | 283487 |
| 46 | 17416 | 140 | 124.4 | 300302 |
| 47 | 18025 | 140 | 128.8 | 317718 |
| 48 | 18641 | 140 | 133.2 | 335743 |
| 49 | 19265 | 140 | 137.6 | 354384 |
| 50 | 19897 | 140 | 142.1 | 373649 |
| 51 | 20537 | 140 | 146.7 | 393546 |
| 52 | 21184 | 140 | 151.3 | 414083 |
| 53 | 21838 | 140 | 156.0 | 435267 |
| 54 | 22501 | 140 | 160.7 | 457105 |
| 55 | 23170 | 140 | 165.5 | 479606 |
| 56 | 23847 | 140 | 170.3 | 502776 |
| 57 | 24531 | 140 | 175.2 | 526623 |
| 58 | 25222 | 140 | 180.2 | 551154 |
| 59 | 25921 | 140 | 185.2 | 576376 |
| 60 | 26627 | 140 | 190.2 | 602297 |

## 2. Metas de ritmo da Região 1 (calibragem feita com o dono)

- Só missões principais (recompensas + abates exigidos): chega no **Nv ~8** (não chega ao 10).
- Principais + secundárias: **Nv ~10**.
- **Nv 12–13** só com caçadas, elites, chefes e uns 150–250 abates extras (sem necessidade de missão).
- Recompensas de missão são em "abates equivalentes" (`kx(n, nível)` = n × XP do monstro padrão): principal **5**, principal com escolha de facção **7**, secundária **3**, Trilha do Caçador **4**, diária **2**; caçadas usam o campo `xk`.

| Missão principal | Nv | Objetivo | XP |
|---|---:|---|---:|
| O Selo | 1 | talk | 34 |
| Estrada Segura | 2 | kill ×10 | 56 |
| Marcas na Planície | 3 | kill ×12 | 69 |
| A Ponte Cortada | 4 | kill ×10 | 115 |
| O Rei Goblin | 5 | boss Grunk | 91 |
| O Eremita | 6 | kill ×12 | 97 |
| Relatório à Ordem | 7 | talk | 141 |
| Os Mortos não Descansam | 8 | kill ×15 | 105 |
| Três Pedidos | 9 | kill ×20 | 107 |
| O Portão do Passo | 10 | bosses ×3 | 110 |

| Missão secundária | Nv | Objetivo | XP |
|---|---:|---|---:|
| Ratos no Estoque | 1 | kill ×6 | 20 |
| Frascos Vazios | 1 | kill ×6 | 20 |
| Oração na Estrada | 2 | kill ×8 | 33 |
| Aço Novo | 2 | kill ×8 | 33 |
| Javalis Famintos | 3 | fam ×6 javali | 42 |
| Goblins no Caminho | 4 | fam ×10 goblin | 49 |
| Carga Perdida | 4 | kill ×8 | 49 |
| Pedras Antigas | 5 | kill ×10 | 55 |
| Selos Estranhos | 5 | elite ×2 | 55 |
| Caçador de Elites | 6 | elite ×3 | 58 |
| Peles de Javali | 7 | fam ×8 javali | 60 |
| Contrato do Conselho | 8 | kill ×12 | 63 |
| Vigília dos Mortos | 8 | fam ×10 esq | 63 |
| Lembrança do Rei | 8 | kill ×12 | 63 |

| Caçada | Rank | Nível | XP | Pontos | Selos | Ouro |
|---|:-:|---|---:|---:|---:|---:|
| O Silêncio da Matilha | D | Nv 3–5 | 25 abates no Nv 5 | 40 | 6 | 150 |
| ??? (em breve) | C | - | - | - | - | - |
| ??? (em breve) | B | - | - | - | - | - |

## 3. Personagem

Valores base por classe (nível 1, sem equipamento). Crescimento por nível: **vida ×(1 + 0,15·(N−1))**, **ataque ×(1 + 0,12·(N−1))**, **defesa +0,8 por nível**.

| Classe | Papel | Vida | Ataque | Defesa | Vel. ataque (s) | Crítico | Velocidade | Alcance |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Guerreiro | Tanque | 135 | 14 | 8 | 0.85 | 10% | 70 | 30 |
| Ladino | Ágil | 68 | 12 | 4 | 0.68 | 22% | 84 | 28 |
| Mago | Dano à distância | 70 | 14 | 3 | 1.1 | 12% | 68 | 150 |
| Clérigo | Suporte | 108 | 14 | 7 | 0.9 | 8% | 68 | 30 |
| Arqueiro | Atirador | 100 | 15 | 5 | 0.9 | 20% | 76 | 170 |
| Bardo | Apoio | 100 | 13.5 | 6 | 0.85 | 10% | 72 | 140 |

Vida / ataque / defesa SEM equipamento nem atributos:

| Classe | Nv 1 | Nv 5 | Nv 10 | Nv 13 | Nv 20 | Nv 30 | Nv 40 | Nv 50 | Nv 60 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Guerreiro | 135 / 14 / 8.8 | 216 / 21 / 12.0 | 317 / 29 / 16.0 | 378 / 34 / 18.4 | 520 / 46 / 24.0 | 722 / 63 / 32.0 | 925 / 80 / 40.0 | 1127 / 96 / 48.0 | 1330 / 113 / 56.0 |
| Ladino | 68 / 12 / 4.8 | 109 / 18 / 8.0 | 160 / 25 / 12.0 | 190 / 29 / 14.4 | 262 / 39 / 20.0 | 364 / 54 / 28.0 | 466 / 68 / 36.0 | 568 / 83 / 44.0 | 670 / 97 / 52.0 |
| Mago | 70 / 14 / 3.8 | 112 / 21 / 7.0 | 164 / 29 / 11.0 | 196 / 34 / 13.4 | 270 / 46 / 19.0 | 375 / 63 / 27.0 | 480 / 80 / 35.0 | 585 / 96 / 43.0 | 690 / 113 / 51.0 |
| Clérigo | 108 / 14 / 7.8 | 173 / 21 / 11.0 | 254 / 29 / 15.0 | 302 / 34 / 17.4 | 416 / 46 / 23.0 | 578 / 63 / 31.0 | 740 / 80 / 39.0 | 902 / 96 / 47.0 | 1064 / 113 / 55.0 |
| Arqueiro | 100 / 15 / 5.8 | 160 / 22 / 9.0 | 235 / 31 / 13.0 | 280 / 37 / 15.4 | 385 / 49 / 21.0 | 535 / 67 / 29.0 | 685 / 85 / 37.0 | 835 / 103 / 45.0 | 985 / 121 / 53.0 |
| Bardo | 100 / 14 / 6.8 | 160 / 20 / 10.0 | 235 / 28 / 14.0 | 280 / 33 / 16.4 | 385 / 44 / 22.0 | 535 / 60 / 30.0 | 685 / 77 / 38.0 | 835 / 93 / 46.0 | 985 / 109 / 54.0 |

### Atributos

- **3 pontos por nível** para distribuir (Força, Destreza, Inteligência, Vitalidade, Sorte).
- **Atributo principal da classe** (Guerreiro/Clérigo = Força, Ladino/Arqueiro = Destreza, Mago/Bardo = Inteligência): **+1 de ataque por ponto**. Os outros dois de ataque: **+0,5 de ataque por ponto**.
- **Vitalidade: +6 de vida por ponto.** **Sorte: +1% de crítico a cada 5 pontos.**
- Não existe atributo próprio de suporte/fé (o Clérigo hoje usa Força) — ponto em aberto para decidir.

## 4. Inimigos

Vida/ataque abaixo são os valores BASE; no jogo são multiplicados pela tabela de equilíbrio do nível do monstro (seção 5) e pelo multiplicador da família. **Peso de XP** = XP base × multiplicador de XP da família ÷ 22 (1,0 = monstro padrão). Chefe/mini-chefe marcados com ★.

| Chave | Nome | Família | Vida | Ataque | XP base | Peso de XP | XP no Nv 1 / 5 / 10 | Ouro | Vel. | Aggro |
|---|---|---|---:|---:|---:|---:|---|---|---:|---:|
| goblin | Goblin | goblin | 78 | 7 | 18 | 1.0 | 7 / 19 / 22 | 3–8 | 46 | 130 |
| esq | Esqueleto | esq | 104 | 9 | 27 | 1.0 | 7 / 19 / 22 | 4–10 | 40 | 120 |
| javali | Javali Selvagem | javali | 125 | 10 | 33 | 1.0 | 7 / 19 / 22 | 5–11 | 60 | 140 |
| rato | Rato Gigante | rato | 42 | 4 | 11 | 1.0 | 7 / 18 / 22 | 1–4 | 58 | 110 |
| gobarq | Goblin Arqueiro | goblin | 62 | 8 | 22 | 1.2 | 8 / 23 / 27 | 3–9 | 44 | 190 |
| xama | Goblin Xamã | goblin | 72 | 9 | 24 | 1.4 | 9 / 25 / 30 | 3–9 | 42 | 170 |
| esqmago | Esqueleto Mago | esq | 80 | 11 | 30 | 1.1 | 8 / 21 / 25 | 4–11 | 38 | 170 |
| esqfogo | Esqueleto Flamejante | esq | 104 | 9 | 29 | 1.1 | 7 / 20 / 24 | 4–10 | 42 | 120 |
| esqgelo | Esqueleto Gélido | esq | 112 | 9 | 29 | 1.1 | 7 / 20 / 24 | 4–10 | 38 | 120 |
| javguer | Javali Guerreiro | javali | 140 | 11 | 36 | 1.1 | 8 / 20 / 25 | 5–12 | 56 | 140 |
| javbruto | Javali Bruto | javali | 195 | 13 | 46 | 1.4 | 10 / 26 / 31 | 6–14 | 46 | 130 |
| javarq | Javali Arqueiro | javali | 92 | 10 | 38 | 1.2 | 8 / 21 / 26 | 5–12 | 48 | 190 |
| javmago | Javali Mago | javali | 100 | 12 | 40 | 1.2 | 8 / 23 / 27 | 5–13 | 42 | 170 |
| ratass | Rato Assassino | rato | 40 | 6 | 14 | 1.3 | 9 / 23 / 28 | 2–5 | 80 | 130 |
| ratarq | Rato Arqueiro | rato | 40 | 5 | 14 | 1.3 | 9 / 23 / 28 | 2–5 | 56 | 190 |
| ratalq | Rato Alquimista | rato | 52 | 6 | 16 | 1.5 | 10 / 27 / 32 | 2–6 | 46 | 170 |
| morcego | Morcego | esq | 50 | 7 | 14 | 0.5 | 4 / 10 / 12 | 2–6 | 78 | 150 |
| vampiro | Morcego-Vampiro ★ | esq | 560 | 9 | 150 | 5.7 | 38 / 103 / 125 | 40–80 | 66 | 260 |
| cult | Cultista | esq | 92 | 10 | 30 | 1.1 | 8 / 21 / 25 | 5–12 | 44 | 160 |
| guarda | Guarda-Caveira | esq | 158 | 10 | 34 | 1.3 | 9 / 23 / 28 | 6–13 | 34 | 130 |
| espectro | Espectro | esq | 88 | 12 | 32 | 1.2 | 8 / 22 / 27 | 5–12 | 60 | 170 |
| gargula | Gárgula | esq | 132 | 12 | 36 | 1.4 | 9 / 25 / 30 | 6–14 | 52 | 150 |
| sapador | Goblin Sapador | goblin | 52 | 11 | 21 | 1.2 | 8 / 22 / 26 | 3–9 | 66 | 150 |
| cogumelo | Cogumelo Andante | goblin | 112 | 7 | 24 | 1.4 | 9 / 25 / 30 | 3–8 | 30 | 110 |
| aranha | Aranha-da-Mata | goblin | 60 | 9 | 22 | 1.2 | 8 / 23 / 27 | 3–9 | 62 | 150 |
| lobo | Lobo Selvagem | javali | 84 | 10 | 26 | 0.8 | 5 / 15 / 18 | 4–10 | 70 | 170 |
| carnical | Carniçal | esq | 122 | 9 | 28 | 1.1 | 7 / 19 / 23 | 4–10 | 38 | 130 |
| necro | Necromante Aprendiz | esq | 78 | 11 | 30 | 1.1 | 8 / 21 / 25 | 4–11 | 38 | 170 |
| cavcaido | Cavaleiro Caído | esq | 190 | 11 | 36 | 1.4 | 9 / 25 / 30 | 5–12 | 32 | 120 |
| mumia | Múmia | esq | 150 | 9 | 30 | 1.1 | 8 / 21 / 25 | 4–11 | 30 | 120 |
| ogrinho | Ogrinho | javali | 112 | 9 | 28 | 0.9 | 6 / 16 / 19 | 4–10 | 54 | 130 |
| ogrolenhador | Ogro Lenhador | javali | 230 | 13 | 44 | 1.4 | 9 / 25 / 30 | 6–14 | 38 | 130 |
| gnoll | Gnoll | javali | 100 | 10 | 30 | 0.9 | 6 / 17 / 20 | 4–11 | 58 | 140 |
| tronco | Tronco Vivo | javali | 210 | 9 | 38 | 1.2 | 8 / 21 / 26 | 5–12 | 28 | 110 |
| harpia | Harpia | javali | 72 | 9 | 28 | 0.9 | 6 / 16 / 19 | 4–10 | 72 | 170 |
| bandido | Bandido | javali | 88 | 10 | 27 | 0.8 | 6 / 15 / 18 | 6–14 | 60 | 140 |
| homemrato | Homem-Rato | rato | 56 | 6 | 16 | 1.5 | 10 / 27 / 32 | 2–6 | 62 | 130 |
| ladrao | Ladrão de Esgoto | rato | 48 | 7 | 16 | 1.5 | 10 / 27 / 32 | 4–10 | 84 | 130 |
| cultlodo | Cultista do Lodo | rato | 66 | 8 | 20 | 1.8 | 12 / 33 / 40 | 3–9 | 40 | 170 |
| sapo | Sapo-do-Esgoto | rato | 96 | 8 | 20 | 1.8 | 12 / 33 / 40 | 3–9 | 46 | 120 |
| cobra | Cobra | rato | 54 | 8 | 18 | 1.6 | 11 / 30 / 36 | 3–8 | 60 | 130 |
| barata | Barata Gigante | rato | 40 | 4 | 12 | 1.1 | 7 / 20 / 24 | 1–4 | 88 | 110 |
| afogado | Afogado | rato | 150 | 8 | 24 | 2.2 | 15 / 40 / 48 | 3–9 | 30 | 110 |
| zumbi | Zumbi Sineiro | esq | 196 | 9 | 34 | 1.3 | 9 / 23 / 28 | 6–13 | 28 | 120 |
| skrix | Xamã Skrix ★ | goblin | 520 | 8 | 150 | 8.5 | 57 / 154 / 186 | 40–80 | 56 | 260 |
| totem | Totem Tóxico | goblin | 150 | 0 | 0 | 0.0 | 0 / 0 / 0 | 0–0 | 0 | - |
| alfa | Presa-Lunar ★ | javali | 330 | 12 | 120 | 3.7 | 25 / 68 / 82 | 30–60 | 84 | 340 |
| javcap | Capitão Presa-de-Ferro ★ | javali | 760 | 11 | 170 | 5.3 | 36 / 96 / 116 | 45–90 | 52 | 260 |
| botic | Boticário Podre ★ | rato | 330 | 6 | 170 | 15.5 | 105 / 282 / 341 | 45–90 | 82 | 320 |

### Multiplicadores por família

| Família | Vida | Ataque | XP |
|---|---:|---:|---:|
| goblin | 1.13 | 1.1 | 1.24 |
| esq | 0.85 | 0.86 | 0.83 |
| javali | 0.71 | 0.77 | 0.68 |
| rato | 2.1 | 1.9 | 2 |

## 5. Equilíbrio por nível do monstro

| Nível do monstro | × vida | × ataque |
|---:|---:|---:|
| 1 | 1.3 | 0.5 |
| 2 | 1.7 | 0.6 |
| 3 | 2.2 | 0.8 |
| 4 | 3.0 | 1.0 |
| 5 | 4.0 | 1.3 |
| 6 | 4.6 | 1.8 |
| 7 | 5.2 | 2.4 |
| 8 | 5.9 | 3.3 |
| 9 | 6.8 | 4.4 |
| 10 | 7.7 | 5.9 |
| 11 | 8.3 | 6.4 |
| 12 | 9.0 | 6.8 |
| 13 | 9.7 | 7.3 |
| 14 | 10.5 | 7.9 |
| 15 | 11.3 | 8.5 |
| 16 | 12.2 | 9.1 |
| 17 | 13.2 | 9.7 |
| 18 | 14.2 | 10.4 |
| 19 | 15.4 | 11.2 |
| 20 | 16.6 | 12.0 |

## 6. Onde cada inimigo aparece (zonas do mundo)

| Zona | Nível dos monstros | Monstros | Chefe | Mini-chefes |
|---|---|---|---|---|
| Planície de Brumavale | 1–3 | rato, javali, lobo | - | - |
| Margem do Lago | 2–3 | rato, javali, lobo | - | - |
| Trilha do Brejo | 3–4 | lobo, rato, javali | - | - |
| Bosque do Eremita | 3–4 | lobo, aranha, cogumelo | - | - |
| Floresta dos Goblins | 3–5 | (família da zona) | Grunk Nv 6 | skrix |
| Ponte do Rio | 3–4 | javali, lobo, ogrinho | - | - |
| Clareira das Ruínas | 4–5 | goblin, sapador, xama, cogumelo | - | - |
| Colinas Rochosas | 4–6 | javali, lobo, gnoll, harpia, javbruto | - | - |
| Trilha dos Lenhadores | 5–6 | gnoll, bandido, tronco, lobo | - | - |
| Desfiladeiro | 7–8 | gnoll, harpia, bandido, lobo | - | - |
| Mina Abandonada | 7–8 | bandido, gnoll, morcego | - | - |
| Estrada dos Mortos | 8–9 | esq, carnical, morcego, mumia | - | - |
| Floresta dos Ogros | 8–11 | ogrinho, gnoll, ogrolenhador, bandido, tronco, harpia, lobo | Gorgash Nv 12 | javcap Nv 11 |
| Passo da Montanha | 8–10 | bandido, gnoll, javbruto, harpia, ogrinho | - | - |
| Pântano das Brumas | 10–12 | homemrato, ladrao, cultlodo, sapo, cobra, barata, afogado, rato | Rei dos Ratos Nv 13 | botic Nv 11 |
| Cabana da Bruxa | 10–11 | homemrato, cultlodo, sapo, afogado | - | - |
| Cemitério de Brumavale | 10–12 | esq, carnical, necro, cavcaido, mumia, esqmago | Morvath Nv 13 | vamp Nv 11 |
| Gruta Aberta | 10–11 | esq, necro, mumia, esqmago | - | - |
| Estrada de Brumavale | - | (família da zona) | - | - |

Famílias das dungeons fechadas (`FAMV`, sorteio):

- **crip**: guarda, cult, espectro, gargula, zumbi
- **goblin**: goblin, sapador, xama, cogumelo, aranha, lobo
- **esq**: esq, carnical, necro, cavcaido, esqmago, mumia, morcego, aranha
- **javali**: javali, ogrinho, gnoll, ogrolenhador, bandido, tronco, javbruto, harpia, lobo
- **rato**: rato, homemrato, ladrao, cultlodo, sapo, ratass, cobra, barata, afogado

## 7. Drops (regras atuais)

- **Equipamento**: monstro comum 20% de chance de 1 item (+bônus de sorte/talentos); elite 1 item (dourado 2); chefe 2 itens, o primeiro com raridade maior. Nível do item = ½·nível do herói + ½·nível do monstro (+2 se chefe).
- **Materiais**: comum 22% de 1; elite azul 1–2 (90%); elite dourado 2–3; chefe 4–7. O tipo do material depende do nível do item.
- **Ainda não existe drop específico por inimigo ou por dungeon** (todos usam a mesma regra) — fica para a fase de dungeons/itens únicos.
