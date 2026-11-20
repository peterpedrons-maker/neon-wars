# Créditos — modo MMO

## Cenário (chão, árvores, rochas, plantas, fogueira, cerca, barris, estandartes)
**Pixel Crawler — Free Pack**, de **Anokolisa** (itch.io). Termos do pacote: uso livre em projetos
comerciais ou não, alteração permitida, crédito não obrigatório (mas apreciado); **proibido revender
os arquivos** ou vendê-los como produto final. Aqui só entram recortes usados no mapa (`atlas.png`,
`zone1_ground.png`); o pacote original não é redistribuído.

## Personagens
Folhas LPC (Universal LPC Spritesheet Character Generator / Liberated Pixel Cup). Autores e licenças
de cada peça: `../../assets/lpc/CREDITS.md`.

## Ícones de habilidade, sons e músicas
Os mesmos do jogo principal (`../../assets/skill-icons`, `../../assets/audio`).


## Fontes
- Cinzel / Cinzel Decorative (Natanael Gama) e Rubik (Hubert & Fischer) — SIL Open Font License 1.1, em `assets/fonts/`.

## Interface (menus)
- Moeda do HUD recortada do "Pixel Fantasy UI Pack" — UI art: Zanyar's Asset Store.

## Aparência do herói (assets/look2)
Peças do Universal LPC Spritesheet Character Generator (corpo, cabeça, trajes, calças, cabelos e chapéus). Autores e licenças de cada arquivo em `assets/look2/CREDITS.csv` (CC-BY-SA 3.0 / OGA-BY 3.0 / GPL 3.0).

## Ícones das habilidades novas
Glifos de game-icons.net (CC BY 3.0; autores em `lendas-de-taverna/assets/ui-icons/CREDITS.md`) sobre ladrilhos coloridos gerados em `assets/skills/`.
Ícones das subclasses: mesmo método (glifos do game-icons.net sobre ladrilhos coloridos, em `assets/skills/`).

Ícones das habilidades (`assets/skills/`): silhuetas do **game-icons.net** (Lorc, Delapouite e colaboradores, CC BY 3.0 — https://game-icons.net), pintadas em estilo pixel por `tools/mmo/icons3/`.

## Cidade
Cidade: terreno (chão, ruas, árvores) do pack Pixel Crawler; os 6 prédios (`tools/mmo/bld/*_key.png`) foram gerados por IA a partir de prompts do projeto, um a um, com colisões, portas e efeitos montados à mão (`tools/mmo/build_town4.py`).

## Efeitos ambientes
Fumaça, tochas, fonte, portal e vaga-lumes usam GSAP 3.12.5 (`assets/gsap.min.js`, © GreenSock, licença padrão gratuita https://gsap.com/standard-license).

## Floresta dos Goblins (zonas de goblin)
Props (árvores, tendas, totens, estacas, paliçadas, ossos, cogumelos etc.) gerados por IA a partir do estilo do jogo, recortados e reduzidos por `tools/mmo/goblin_ia.py` (folhas originais em `tools/mmo/ia_src/`). Chão e fogueiras vêm do Pixel Crawler (Anokolisa).

## Ícones e cidade (arte por IA)
Ícones da interface (ni_*.png), fonte, portal, lampiões, tochas, estandartes, bancos, canteiros, barraca, poço e demais enfeites da cidade foram gerados por IA a partir do estilo do jogo e processados por `tools/mmo/city_ia.py` (folhas originais em `tools/mmo/ia_src/city/`).

## Ícones de talentos
126 glifos do game-icons.net (Lorc, Delapouite e colaboradores, CC BY 3.0 — https://game-icons.net) pintados em estilo pixel por `tools/mmo/icons3/talentos.py`, no mesmo padrão dos ícones de habilidade.

## Trilhas da floresta e efeitos de combate
Músicas `floresta_*` compostas para o jogo e renderizadas com instrumentos reais amostrados do **GeneralUser GS** (S. Christian Collins, licença própria que permite uso em projetos comerciais). Efeitos de combate refeitos em `tools/mmo/music/sfx2.py` (camadas sintetizadas e instrumentos do mesmo banco de sons).

## Monstros LPC (assets/lpc_monsters)
"[LPC] Monsters" — Charles Sanchez (CharlesGabriel), bagzie e bluecarrot16 — CC-BY-SA 3.0+ ou GPL 3.0+ (morcego: OGA-BY 3.0). https://opengameart.org/content/lpc-monsters . Detalhes em `assets/lpc_monsters/CREDITS.md`.

## Pixelify Sans (fonte da interface pixel art)
SIL Open Font License 1.1 — Stefie Justprince, via Google Fonts (assets/fonts/PixelifySans-*.ttf).

## Sons de criaturas e cavalo (adicionados na rodada "sons dos inimigos")
- **80 CC0 Creature SFX** e **80 CC0 Creature SFX 2** (Chasersgaming, OpenGameArt, CC0) — base dos sons de lobo, aranha, barata, sapo, cobra, tronco vivo, harpia, gnoll, bandido/ladrão, mortos-vivos e cogumelo (`assets/audio/sfx/mob_<familia>_<atk|hurt|die>.ogg`, recortados e normalizados).
- **Wolf monster sound** (OpenGameArt, CC0) — morte do lobo.
- **Zebra whinny** — extraído de vídeo por **Peet J van Eeden** (CC BY 3.0), publicado no OpenGameArt; recortado e baixado de tom para o relincho do cavalo (`mount_neigh.ogg`). Atribuição exigida: Peet J van Eeden (CC BY).
- O som de bufo do cavalo (`mount_snort.ogg`) vem do pacote CC0 acima.

## Almendra (fonte do Diário)
SIL Open Font License 1.1 — Ryoichi Tsunekawa / Flat It, via Google Fonts (assets/fonts/Almendra-*.ttf).

- Músicas `titulo_mmo`, `criacao`, `abertura`, `amanhecer` e efeitos `cut_*` compostos para o jogo (`tools/mmo/music/abertura_mmo.py`) e renderizados com instrumentos reais amostrados do **GeneralUser GS** (S. Christian Collins), como as demais trilhas.
- **Som do arco (`bow.ogg`)**: `Bow.wav` do pacote "Battle Sound Effects" (OpenGameArt, CC0) com `arrow-feathers-01` do pacote "Fantasy Sound Effects – TinySized SFX" (OpenGameArt, CC0), recortados e misturados.
