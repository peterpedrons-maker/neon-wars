# Hearthblade — modo MMO automático (`/mmo/`)

Novo modo do jogo: **RPG de ação automático**, em retrato. O jogador cria **um único herói**
e o acompanha ao longo das zonas: ele anda sozinho pelo mapa, ataca o monstro mais próximo,
ganha XP, sobe de nível e, ao limpar a clareira, enfrenta o chefe. O jogo tático antigo
continua em `../index.html`.

Acesso: `https://peterpedrons-maker.github.io/neon-wars/lendas-de-taverna/mmo/`

## Etapa 1 (esta versão)
- Título, **criação de personagem** (6 classes, nome), salvamento em `localStorage` (`hb_mmo_save_v1`).
- Mapa da **Clareira de Brumavale** (zona 1): estrada, lago, acampamento, ruínas do chefe.
- Herói automático (andar/caçar/atacar), com **ataque corpo a corpo, mágico e à distância**,
  habilidade 1 automática por classe (as outras 2 aparecem bloqueadas até o Nv.5 e Nv.10).
- Monstros com IA (vagar, perseguir, atacar), **knockback físico**, reaparecimento.
- XP/nível, ouro, KO e reanimação, chefe (Ogro), tela de zona limpa e zonas mais difíceis.
- Modo **AUTO / MANUAL** (manual: toque no mapa para andar) e velocidade x1/x2.
- Sons de todas as ações (reaproveitando `../assets/audio`) e música.

## Etapa 2
- **Itens**: 5 espaços (arma, elmo, armadura, botas, amuleto), 5 raridades (Comum a Lendário) com
  bônus extras por raridade, ícones por classe, nível do item. Monstros dropam no chão (o herói
  vai buscar); o chefe sempre dropa (mínimo Raro).
- **Mochila** (24 vagas): comparar com o equipado, equipar, vender, equipar melhores, vender comuns,
  **auto-equipar**, comprar **poções** (usadas sozinhas abaixo de 35% de vida).
- **Habilidades**: as 3 de cada classe agora têm efeito (golpe, área, meteoros, escudo, reforço, veneno/queimadura),
  disparam sozinhas; 1 ponto por nível para subir habilidades (até 5) e 4 passivas; reset por ouro.
- Arqueiro e Mago recuam entre disparos (kiting). Chefe exige nível mínimo (zona + 4).
- Balanceamento: zona 1 leva ~3 a 5 min no x1.

## Próximas etapas
3. Mais zonas e biomas, chefes finais, itens únicos/lendários, subclasses, nuvem.

## Arquitetura
- `index.html`: tudo em um arquivo (canvas 2D + HUD em DOM). Escala inteira de pixels (`G.K`).
- `assets/zone1_ground.png` + `assets/zone1.json` + `assets/atlas.*`: mapa **pré-renderizado**
  (chão) e lista de props, gerados por `../tools/mmo/build_mmo_assets.py` a partir do pack.
- `assets/chars/*.png`: folhas LPC (heróis e monstros) exportadas do gerador do jogo.

## Créditos de arte
Veja `assets/CREDITS.md`.
