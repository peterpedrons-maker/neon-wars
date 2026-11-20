# TABELAS DO JOGO (geradas do código — `node tools/mmo/gen_tabelas.cjs`)

Tudo aqui é lido do jogo real; para atualizar depois de mexer em XP, inimigos ou classes, rode o gerador de novo.

## 1. Curva de XP do personagem

- **XP para subir** de N para N+1 (`XPN` no jogo): 1.000 no Nv 1, 3.030 no 2, 5.800 no 3… (`1000 × N^1,6`).
- **XP do inimigo PADRÃO de nível N** (`XPM`): cada inimigo multiplica pelo seu peso (XP base × mult. da família ÷ 22; elite ×2 / ×3,5). Os valores são aproximados e escolhidos por faixa, não por contagem de abates.
- **Herói acima do inimigo** (exceto chefe): 1 nível = 100%, 2 níveis = 70%, 3 = 35%, 4 = 12%, **5 ou mais = só 1 XP**. Chefes têm piso de 25%. Assim farmar a área fácil não sobe o nível.

| Nível | XP p/ subir | XP do inimigo padrão (nível N) | ≈ inimigos p/ subir | XP acumulado até o nível |
|---:|---:|---:|---:|---:|
| 1 | 1000 | 83 | 12 | 0 |
| 2 | 3030 | 190 | 16 | 1000 |
| 3 | 5800 | 280 | 21 | 4030 |
| 4 | 9190 | 330 | 28 | 9830 |
| 5 | 13130 | 380 | 35 | 19020 |
| 6 | 17580 | 410 | 43 | 32150 |
| 7 | 22500 | 430 | 52 | 49730 |
| 8 | 27860 | 450 | 62 | 72230 |
| 9 | 33630 | 460 | 73 | 100090 |
| 10 | 39810 | 470 | 85 | 133720 |
| 11 | 46370 | 480 | 97 | 173530 |
| 12 | 53300 | 490 | 109 | 219900 |
| 13 | 60580 | 500 | 121 | 273200 |
| 14 | 68200 | 510 | 134 | 333780 |
| 15 | 76160 | 510 | 149 | 401980 |
| 16 | 84450 | 510 | 166 | 478140 |
| 17 | 93050 | 550 | 169 | 562590 |
| 18 | 101960 | 600 | 170 | 655640 |
| 19 | 111170 | 650 | 171 | 757600 |
| 20 | 120680 | 710 | 170 | 868770 |
| 21 | 130480 | 770 | 169 | 989450 |
| 22 | 140560 | 830 | 169 | 1119930 |
| 23 | 150930 | 890 | 170 | 1260490 |
| 24 | 161560 | 950 | 170 | 1411420 |
| 25 | 172470 | 1000 | 172 | 1572980 |
| 26 | 183640 | 1100 | 167 | 1745450 |
| 27 | 195070 | 1100 | 177 | 1929090 |
| 28 | 206750 | 1200 | 172 | 2124160 |
| 29 | 218690 | 1300 | 168 | 2330910 |
| 30 | 230880 | 1400 | 165 | 2549600 |
| 31 | 243320 | 1400 | 174 | 2780480 |
| 32 | 256000 | 1500 | 171 | 3023800 |
| 33 | 268920 | 1600 | 168 | 3279800 |
| 34 | 282080 | 1700 | 166 | 3548720 |
| 35 | 295470 | 1700 | 174 | 3830800 |
| 36 | 309090 | 1800 | 172 | 4126270 |
| 37 | 322940 | 1900 | 170 | 4435360 |
| 38 | 337020 | 2000 | 169 | 4758300 |
| 39 | 351320 | 2100 | 167 | 5095320 |
| 40 | 365840 | 2200 | 166 | 5446640 |
| 41 | 380590 | 2239 | 170 | 5812480 |
| 42 | 395550 | 2327 | 170 | 6193070 |
| 43 | 410720 | 2416 | 170 | 6588620 |
| 44 | 426110 | 2507 | 170 | 6999340 |
| 45 | 441710 | 2598 | 170 | 7425450 |
| 46 | 457520 | 2691 | 170 | 7867160 |
| 47 | 473540 | 2786 | 170 | 8324680 |
| 48 | 489760 | 2881 | 170 | 8798220 |
| 49 | 506190 | 2978 | 170 | 9287980 |
| 50 | 522820 | 3075 | 170 | 9794170 |
| 51 | 539650 | 3174 | 170 | 10316990 |
| 52 | 556680 | 3275 | 170 | 10856640 |
| 53 | 573910 | 3376 | 170 | 11413320 |
| 54 | 591330 | 3478 | 170 | 11987230 |
| 55 | 608950 | 3582 | 170 | 12578560 |
| 56 | 626760 | 3687 | 170 | 13187510 |
| 57 | 644760 | 3793 | 170 | 13814270 |
| 58 | 662960 | 3900 | 170 | 14459030 |
| 59 | 681340 | 4008 | 170 | 15121990 |
| 60 | 699910 | 4117 | 170 | 15803330 |

## 2. Metas de ritmo da Região 1 (calibragem feita com o dono)

- Só missões principais (recompensas + abates exigidos): chega no **Nv ~8** (não chega ao 10).
- Principais + secundárias: **Nv ~10**.
- **Nv 12–13** só com caçadas, elites, chefes e uns 150–250 abates extras (sem necessidade de missão).
- Recompensas de missão = XP de N inimigos padrão do nível da missão (`kx`): principal **5**, principal com escolha **7**, secundária **3**, Trilha do Caçador **4**, diária **2**; a caçada do Alfa vale 25. Os valores finais aparecem nas tabelas abaixo.

| Missão principal | Nv | Objetivo | XP |
|---|---:|---|---:|
| O Selo | 1 | talk | 415 |
| Estrada Segura | 2 | kill ×10 | 950 |
| Marcas na Planície | 3 | kill ×12 | 1400 |
| A Ponte Cortada | 4 | kill ×10 | 2310 |
| O Rei Goblin | 5 | boss Grunk | 1900 |
| O Eremita | 6 | kill ×12 | 2050 |
| Relatório à Ordem | 7 | talk | 3010 |
| Os Mortos não Descansam | 8 | kill ×15 | 2250 |
| Três Pedidos | 9 | kill ×20 | 2300 |
| O Portão do Passo | 10 | bosses ×3 | 2350 |

| Missão secundária | Nv | Objetivo | XP |
|---|---:|---|---:|
| Ratos no Estoque | 1 | kill ×6 | 249 |
| Frascos Vazios | 1 | kill ×6 | 249 |
| Oração na Estrada | 2 | kill ×8 | 570 |
| Aço Novo | 2 | kill ×8 | 570 |
| Javalis Famintos | 3 | fam ×6 javali | 840 |
| Goblins no Caminho | 4 | fam ×10 goblin | 990 |
| Carga Perdida | 4 | kill ×8 | 990 |
| Pedras Antigas | 5 | kill ×10 | 1140 |
| Selos Estranhos | 5 | elite ×2 | 1140 |
| Caçador de Elites | 6 | elite ×3 | 1230 |
| Peles de Javali | 7 | fam ×8 javali | 1290 |
| Contrato do Conselho | 8 | kill ×12 | 1350 |
| Vigília dos Mortos | 8 | fam ×10 esq | 1350 |
| Lembrança do Rei | 8 | kill ×12 | 1350 |

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
| goblin | Goblin | goblin | 78 | 7 | 18 | 1.0 | 84 / 386 / 477 | 3–8 | 46 | 130 |
| esq | Esqueleto | esq | 104 | 9 | 27 | 1.0 | 85 / 387 / 479 | 4–10 | 40 | 120 |
| javali | Javali Selvagem | javali | 125 | 10 | 33 | 1.0 | 85 / 388 / 479 | 5–11 | 60 | 140 |
| rato | Rato Gigante | rato | 42 | 4 | 11 | 1.0 | 83 / 380 / 470 | 1–4 | 58 | 110 |
| gobarq | Goblin Arqueiro | goblin | 62 | 8 | 22 | 1.2 | 103 / 471 / 583 | 3–9 | 44 | 190 |
| xama | Goblin Xamã | goblin | 72 | 9 | 24 | 1.4 | 112 / 514 / 636 | 3–9 | 42 | 170 |
| esqmago | Esqueleto Mago | esq | 80 | 11 | 30 | 1.1 | 94 / 430 / 532 | 4–11 | 38 | 170 |
| esqfogo | Esqueleto Flamejante | esq | 104 | 9 | 29 | 1.1 | 91 / 416 / 514 | 4–10 | 42 | 120 |
| esqgelo | Esqueleto Gélido | esq | 112 | 9 | 29 | 1.1 | 91 / 416 / 514 | 4–10 | 38 | 120 |
| javguer | Javali Guerreiro | javali | 140 | 11 | 36 | 1.1 | 92 / 423 / 523 | 5–12 | 56 | 140 |
| javbruto | Javali Bruto | javali | 195 | 13 | 46 | 1.4 | 118 / 540 / 668 | 6–14 | 46 | 130 |
| javarq | Javali Arqueiro | javali | 92 | 10 | 38 | 1.2 | 97 / 446 / 552 | 5–12 | 48 | 190 |
| javmago | Javali Mago | javali | 100 | 12 | 40 | 1.2 | 103 / 470 / 581 | 5–13 | 42 | 170 |
| ratass | Rato Assassino | rato | 40 | 6 | 14 | 1.3 | 106 / 484 / 598 | 2–5 | 80 | 130 |
| ratarq | Rato Arqueiro | rato | 40 | 5 | 14 | 1.3 | 106 / 484 / 598 | 2–5 | 56 | 190 |
| ratalq | Rato Alquimista | rato | 52 | 6 | 16 | 1.5 | 121 / 553 / 684 | 2–6 | 46 | 170 |
| morcego | Morcego | esq | 50 | 7 | 14 | 0.5 | 44 / 201 / 248 | 2–6 | 78 | 150 |
| vampiro | Morcego-Vampiro ★ | esq | 560 | 9 | 150 | 5.7 | 470 / 2150 / 2660 | 40–80 | 66 | 260 |
| cult | Cultista | esq | 92 | 10 | 30 | 1.1 | 94 / 430 / 532 | 5–12 | 44 | 160 |
| guarda | Guarda-Caveira | esq | 158 | 10 | 34 | 1.3 | 106 / 487 / 603 | 6–13 | 34 | 130 |
| espectro | Espectro | esq | 88 | 12 | 32 | 1.2 | 100 / 459 / 567 | 5–12 | 60 | 170 |
| gargula | Gárgula | esq | 132 | 12 | 36 | 1.4 | 113 / 516 / 638 | 6–14 | 52 | 150 |
| sapador | Goblin Sapador | goblin | 52 | 11 | 21 | 1.2 | 98 / 450 / 556 | 3–9 | 66 | 150 |
| cogumelo | Cogumelo Andante | goblin | 112 | 7 | 24 | 1.4 | 112 / 514 / 636 | 3–8 | 30 | 110 |
| aranha | Aranha-da-Mata | goblin | 60 | 9 | 22 | 1.2 | 103 / 471 / 583 | 3–9 | 62 | 150 |
| lobo | Lobo Selvagem | javali | 84 | 10 | 26 | 0.8 | 67 / 305 / 378 | 4–10 | 70 | 170 |
| carnical | Carniçal | esq | 122 | 9 | 28 | 1.1 | 88 / 401 / 496 | 4–10 | 38 | 130 |
| necro | Necromante Aprendiz | esq | 78 | 11 | 30 | 1.1 | 94 / 430 / 532 | 4–11 | 38 | 170 |
| cavcaido | Cavaleiro Caído | esq | 190 | 11 | 36 | 1.4 | 113 / 516 / 638 | 5–12 | 32 | 120 |
| mumia | Múmia | esq | 150 | 9 | 30 | 1.1 | 94 / 430 / 532 | 4–11 | 30 | 120 |
| ogrinho | Ogrinho | javali | 112 | 9 | 28 | 0.9 | 72 / 329 / 407 | 4–10 | 54 | 130 |
| ogrolenhador | Ogro Lenhador | javali | 230 | 13 | 44 | 1.4 | 113 / 517 / 639 | 6–14 | 38 | 130 |
| gnoll | Gnoll | javali | 100 | 10 | 30 | 0.9 | 77 / 352 / 436 | 4–11 | 58 | 140 |
| tronco | Tronco Vivo | javali | 210 | 9 | 38 | 1.2 | 97 / 446 / 552 | 5–12 | 28 | 110 |
| harpia | Harpia | javali | 72 | 9 | 28 | 0.9 | 72 / 329 / 407 | 4–10 | 72 | 170 |
| bandido | Bandido | javali | 88 | 10 | 27 | 0.8 | 69 / 317 / 392 | 6–14 | 60 | 140 |
| homemrato | Homem-Rato | rato | 56 | 6 | 16 | 1.5 | 121 / 553 / 684 | 2–6 | 62 | 130 |
| ladrao | Ladrão de Esgoto | rato | 48 | 7 | 16 | 1.5 | 121 / 553 / 684 | 4–10 | 84 | 130 |
| cultlodo | Cultista do Lodo | rato | 66 | 8 | 20 | 1.8 | 151 / 691 / 855 | 3–9 | 40 | 170 |
| sapo | Sapo-do-Esgoto | rato | 96 | 8 | 20 | 1.8 | 151 / 691 / 855 | 3–9 | 46 | 120 |
| cobra | Cobra | rato | 54 | 8 | 18 | 1.6 | 136 / 622 / 769 | 3–8 | 60 | 130 |
| barata | Barata Gigante | rato | 40 | 4 | 12 | 1.1 | 91 / 415 / 513 | 1–4 | 88 | 110 |
| afogado | Afogado | rato | 150 | 8 | 24 | 2.2 | 181 / 829 / 1025 | 3–9 | 30 | 110 |
| zumbi | Zumbi Sineiro | esq | 196 | 9 | 34 | 1.3 | 106 / 487 / 603 | 6–13 | 28 | 120 |
| skrix | Xamã Skrix ★ | goblin | 520 | 8 | 150 | 8.5 | 702 / 3213 / 3974 | 40–80 | 56 | 260 |
| totem | Totem Tóxico | goblin | 150 | 0 | 0 | 0.0 | 0 / 0 / 0 | 0–0 | 0 | - |
| alfa | Presa-Lunar ★ | javali | 330 | 12 | 120 | 3.7 | 308 / 1409 / 1743 | 30–60 | 84 | 340 |
| javcap | Capitão Presa-de-Ferro ★ | javali | 760 | 11 | 170 | 5.3 | 436 / 1997 / 2470 | 45–90 | 52 | 260 |
| botic | Boticário Podre ★ | rato | 330 | 6 | 170 | 15.5 | 1283 / 5873 / 7264 | 45–90 | 82 | 320 |

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
