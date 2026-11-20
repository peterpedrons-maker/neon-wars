# TABELAS DO JOGO (geradas do código — `node tools/mmo/gen_tabelas.cjs`)

Tudo aqui é lido do jogo real; para atualizar depois de mexer em XP, inimigos ou classes, rode o gerador de novo.

## 1. Curva de XP do personagem

- XP para subir do nível N para N+1: `38 × N^1.6 + 30` (`xpNeed`).
- **Abates padrão**: quantos monstros PADRÃO do nível N são precisos para subir (`KPL`). **XP do padrão** = XP necessário ÷ abates. Todo monstro dá `XP do padrão × peso do monstro` (peso ≈ 1 para monstro comum; elite ×2 / ×3,5; chefe usa o peso da tabela abaixo).
- Monstros muito abaixo do nível do herói dão cada vez menos XP (diferença de 3 níveis = ×0,85 … 8 níveis = 0).

| Nível | XP p/ subir | Abates padrão | XP do monstro padrão | XP acumulado até o nível |
|---:|---:|---:|---:|---:|
| 1 | 68 | 12 | 5.7 | 0 |
| 2 | 145 | 16 | 9.1 | 68 |
| 3 | 250 | 21 | 11.9 | 213 |
| 4 | 379 | 28 | 13.5 | 463 |
| 5 | 529 | 35 | 15.1 | 842 |
| 6 | 698 | 43 | 16.2 | 1371 |
| 7 | 885 | 52 | 17.0 | 2069 |
| 8 | 1089 | 62 | 17.6 | 2954 |
| 9 | 1308 | 73 | 17.9 | 4043 |
| 10 | 1543 | 84 | 18.4 | 5351 |
| 11 | 1792 | 96 | 18.7 | 6894 |
| 12 | 2055 | 108 | 19.0 | 8686 |
| 13 | 2332 | 122 | 19.1 | 10741 |
| 14 | 2622 | 135 | 19.4 | 13073 |
| 15 | 2924 | 149 | 19.6 | 15695 |
| 16 | 3239 | 164 | 19.8 | 18619 |
| 17 | 3566 | 170 | 21.0 | 21858 |
| 18 | 3905 | 170 | 23.0 | 25424 |
| 19 | 4255 | 170 | 25.0 | 29329 |
| 20 | 4616 | 170 | 27.2 | 33584 |
| 21 | 4988 | 170 | 29.3 | 38200 |
| 22 | 5371 | 170 | 31.6 | 43188 |
| 23 | 5765 | 170 | 33.9 | 48559 |
| 24 | 6169 | 170 | 36.3 | 54324 |
| 25 | 6584 | 170 | 38.7 | 60493 |
| 26 | 7008 | 170 | 41.2 | 67077 |
| 27 | 7443 | 170 | 43.8 | 74085 |
| 28 | 7887 | 170 | 46.4 | 81528 |
| 29 | 8340 | 170 | 49.1 | 89415 |
| 30 | 8804 | 170 | 51.8 | 97755 |
| 31 | 9276 | 170 | 54.6 | 106559 |
| 32 | 9758 | 170 | 57.4 | 115835 |
| 33 | 10249 | 170 | 60.3 | 125593 |
| 34 | 10749 | 170 | 63.2 | 135842 |
| 35 | 11258 | 170 | 66.2 | 146591 |
| 36 | 11775 | 170 | 69.3 | 157849 |
| 37 | 12302 | 170 | 72.4 | 169624 |
| 38 | 12837 | 170 | 75.5 | 181926 |
| 39 | 13380 | 170 | 78.7 | 194763 |
| 40 | 13932 | 170 | 82.0 | 208143 |
| 41 | 14492 | 170 | 85.2 | 222075 |
| 42 | 15061 | 170 | 88.6 | 236567 |
| 43 | 15637 | 170 | 92.0 | 251628 |
| 44 | 16222 | 170 | 95.4 | 267265 |
| 45 | 16815 | 170 | 98.9 | 283487 |
| 46 | 17416 | 170 | 102.4 | 300302 |
| 47 | 18025 | 170 | 106.0 | 317718 |
| 48 | 18641 | 170 | 109.7 | 335743 |
| 49 | 19265 | 170 | 113.3 | 354384 |
| 50 | 19897 | 170 | 117.0 | 373649 |
| 51 | 20537 | 170 | 120.8 | 393546 |
| 52 | 21184 | 170 | 124.6 | 414083 |
| 53 | 21838 | 170 | 128.5 | 435267 |
| 54 | 22501 | 170 | 132.4 | 457105 |
| 55 | 23170 | 170 | 136.3 | 479606 |
| 56 | 23847 | 170 | 140.3 | 502776 |
| 57 | 24531 | 170 | 144.3 | 526623 |
| 58 | 25222 | 170 | 148.4 | 551154 |
| 59 | 25921 | 170 | 152.5 | 576376 |
| 60 | 26627 | 170 | 156.6 | 602297 |

## 2. Metas de ritmo da Região 1 (calibragem feita com o dono)

- Só missões principais (recompensas + abates exigidos): chega no **Nv ~8** (não chega ao 10).
- Principais + secundárias: **Nv ~10**.
- **Nv 12–13** só com caçadas, elites, chefes e uns 150–250 abates extras (sem necessidade de missão).
- Recompensas de missão são em "abates equivalentes" (`kx(n, nível)` = n × XP do monstro padrão): principal **5**, principal com escolha de facção **7**, secundária **3**, Trilha do Caçador **4**, diária **2**; caçadas usam o campo `xk`.

| Missão principal | Nv | Objetivo | XP |
|---|---:|---|---:|
| O Selo | 1 | talk | 28 |
| Estrada Segura | 2 | kill ×10 | 45 |
| Marcas na Planície | 3 | kill ×12 | 60 |
| A Ponte Cortada | 4 | kill ×10 | 95 |
| O Rei Goblin | 5 | boss Grunk | 76 |
| O Eremita | 6 | kill ×12 | 81 |
| Relatório à Ordem | 7 | talk | 119 |
| Os Mortos não Descansam | 8 | kill ×15 | 88 |
| Três Pedidos | 9 | kill ×20 | 90 |
| O Portão do Passo | 10 | bosses ×3 | 92 |

| Missão secundária | Nv | Objetivo | XP |
|---|---:|---|---:|
| Ratos no Estoque | 1 | kill ×6 | 17 |
| Frascos Vazios | 1 | kill ×6 | 17 |
| Oração na Estrada | 2 | kill ×8 | 27 |
| Aço Novo | 2 | kill ×8 | 27 |
| Javalis Famintos | 3 | fam ×6 javali | 36 |
| Goblins no Caminho | 4 | fam ×10 goblin | 41 |
| Carga Perdida | 4 | kill ×8 | 41 |
| Pedras Antigas | 5 | kill ×10 | 45 |
| Selos Estranhos | 5 | elite ×2 | 45 |
| Caçador de Elites | 6 | elite ×3 | 49 |
| Peles de Javali | 7 | fam ×8 javali | 51 |
| Contrato do Conselho | 8 | kill ×12 | 53 |
| Vigília dos Mortos | 8 | fam ×10 esq | 53 |
| Lembrança do Rei | 8 | kill ×12 | 53 |

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
| goblin | Goblin | goblin | 78 | 7 | 18 | 1.0 | 6 / 15 / 19 | 3–8 | 46 | 130 |
| esq | Esqueleto | esq | 104 | 9 | 27 | 1.0 | 6 / 15 / 19 | 4–10 | 40 | 120 |
| javali | Javali Selvagem | javali | 125 | 10 | 33 | 1.0 | 6 / 15 / 19 | 5–11 | 60 | 140 |
| rato | Rato Gigante | rato | 42 | 4 | 11 | 1.0 | 6 / 15 / 18 | 1–4 | 58 | 110 |
| gobarq | Goblin Arqueiro | goblin | 62 | 8 | 22 | 1.2 | 7 / 19 / 23 | 3–9 | 44 | 190 |
| xama | Goblin Xamã | goblin | 72 | 9 | 24 | 1.4 | 8 / 20 / 25 | 3–9 | 42 | 170 |
| esqmago | Esqueleto Mago | esq | 80 | 11 | 30 | 1.1 | 6 / 17 / 21 | 4–11 | 38 | 170 |
| esqfogo | Esqueleto Flamejante | esq | 104 | 9 | 29 | 1.1 | 6 / 17 / 20 | 4–10 | 42 | 120 |
| esqgelo | Esqueleto Gélido | esq | 112 | 9 | 29 | 1.1 | 6 / 17 / 20 | 4–10 | 38 | 120 |
| javguer | Javali Guerreiro | javali | 140 | 11 | 36 | 1.1 | 6 / 17 / 20 | 5–12 | 56 | 140 |
| javbruto | Javali Bruto | javali | 195 | 13 | 46 | 1.4 | 8 / 21 / 26 | 6–14 | 46 | 130 |
| javarq | Javali Arqueiro | javali | 92 | 10 | 38 | 1.2 | 7 / 18 / 22 | 5–12 | 48 | 190 |
| javmago | Javali Mago | javali | 100 | 12 | 40 | 1.2 | 7 / 19 / 23 | 5–13 | 42 | 170 |
| ratass | Rato Assassino | rato | 40 | 6 | 14 | 1.3 | 7 / 19 / 23 | 2–5 | 80 | 130 |
| ratarq | Rato Arqueiro | rato | 40 | 5 | 14 | 1.3 | 7 / 19 / 23 | 2–5 | 56 | 190 |
| ratalq | Rato Alquimista | rato | 52 | 6 | 16 | 1.5 | 8 / 22 / 27 | 2–6 | 46 | 170 |
| morcego | Morcego | esq | 50 | 7 | 14 | 0.5 | 3 / 8 / 10 | 2–6 | 78 | 150 |
| vampiro | Morcego-Vampiro ★ | esq | 560 | 9 | 150 | 5.7 | 32 / 86 / 104 | 40–80 | 66 | 260 |
| cult | Cultista | esq | 92 | 10 | 30 | 1.1 | 6 / 17 / 21 | 5–12 | 44 | 160 |
| guarda | Guarda-Caveira | esq | 158 | 10 | 34 | 1.3 | 7 / 19 / 24 | 6–13 | 34 | 130 |
| espectro | Espectro | esq | 88 | 12 | 32 | 1.2 | 7 / 18 / 22 | 5–12 | 60 | 170 |
| gargula | Gárgula | esq | 132 | 12 | 36 | 1.4 | 8 / 21 / 25 | 6–14 | 52 | 150 |
| sapador | Goblin Sapador | goblin | 52 | 11 | 21 | 1.2 | 7 / 18 / 22 | 3–9 | 66 | 150 |
| cogumelo | Cogumelo Andante | goblin | 112 | 7 | 24 | 1.4 | 8 / 20 / 25 | 3–8 | 30 | 110 |
| aranha | Aranha-da-Mata | goblin | 60 | 9 | 22 | 1.2 | 7 / 19 / 23 | 3–9 | 62 | 150 |
| lobo | Lobo Selvagem | javali | 84 | 10 | 26 | 0.8 | 5 / 12 / 15 | 4–10 | 70 | 170 |
| carnical | Carniçal | esq | 122 | 9 | 28 | 1.1 | 6 / 16 / 19 | 4–10 | 38 | 130 |
| necro | Necromante Aprendiz | esq | 78 | 11 | 30 | 1.1 | 6 / 17 / 21 | 4–11 | 38 | 170 |
| cavcaido | Cavaleiro Caído | esq | 190 | 11 | 36 | 1.4 | 8 / 21 / 25 | 5–12 | 32 | 120 |
| mumia | Múmia | esq | 150 | 9 | 30 | 1.1 | 6 / 17 / 21 | 4–11 | 30 | 120 |
| ogrinho | Ogrinho | javali | 112 | 9 | 28 | 0.9 | 5 / 13 / 16 | 4–10 | 54 | 130 |
| ogrolenhador | Ogro Lenhador | javali | 230 | 13 | 44 | 1.4 | 8 / 21 / 25 | 6–14 | 38 | 130 |
| gnoll | Gnoll | javali | 100 | 10 | 30 | 0.9 | 5 / 14 / 17 | 4–11 | 58 | 140 |
| tronco | Tronco Vivo | javali | 210 | 9 | 38 | 1.2 | 7 / 18 / 22 | 5–12 | 28 | 110 |
| harpia | Harpia | javali | 72 | 9 | 28 | 0.9 | 5 / 13 / 16 | 4–10 | 72 | 170 |
| bandido | Bandido | javali | 88 | 10 | 27 | 0.8 | 5 / 13 / 15 | 6–14 | 60 | 140 |
| homemrato | Homem-Rato | rato | 56 | 6 | 16 | 1.5 | 8 / 22 / 27 | 2–6 | 62 | 130 |
| ladrao | Ladrão de Esgoto | rato | 48 | 7 | 16 | 1.5 | 8 / 22 / 27 | 4–10 | 84 | 130 |
| cultlodo | Cultista do Lodo | rato | 66 | 8 | 20 | 1.8 | 10 / 27 / 33 | 3–9 | 40 | 170 |
| sapo | Sapo-do-Esgoto | rato | 96 | 8 | 20 | 1.8 | 10 / 27 / 33 | 3–9 | 46 | 120 |
| cobra | Cobra | rato | 54 | 8 | 18 | 1.6 | 9 / 25 / 30 | 3–8 | 60 | 130 |
| barata | Barata Gigante | rato | 40 | 4 | 12 | 1.1 | 6 / 16 / 20 | 1–4 | 88 | 110 |
| afogado | Afogado | rato | 150 | 8 | 24 | 2.2 | 12 / 33 / 40 | 3–9 | 30 | 110 |
| zumbi | Zumbi Sineiro | esq | 196 | 9 | 34 | 1.3 | 7 / 19 / 24 | 6–13 | 28 | 120 |
| skrix | Xamã Skrix ★ | goblin | 520 | 8 | 150 | 8.5 | 48 / 128 / 155 | 40–80 | 56 | 260 |
| totem | Totem Tóxico | goblin | 150 | 0 | 0 | 0.0 | 0 / 0 / 0 | 0–0 | 0 | - |
| alfa | Presa-Lunar ★ | javali | 330 | 12 | 120 | 3.7 | 21 / 56 / 68 | 30–60 | 84 | 340 |
| javcap | Capitão Presa-de-Ferro ★ | javali | 760 | 11 | 170 | 5.3 | 30 / 79 / 97 | 45–90 | 52 | 260 |
| botic | Boticário Podre ★ | rato | 330 | 6 | 170 | 15.5 | 88 / 234 / 284 | 45–90 | 82 | 320 |

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
