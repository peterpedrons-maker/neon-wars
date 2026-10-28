# Logos — prompts para gerar as imagens

Arquivos esperados (PNG, fundo transparente): `assets/brand/publisher.png` e `assets/brand/logo.png`.
O jogo usa a imagem se ela existir; senão fica o texto atual.

## 1) Logo da publicadora — Javali Torto Games
Prompt (inglês funciona melhor nos geradores):

> A game studio emblem logo for "JAVALI TORTO GAMES": a stylized wild boar head in profile with one crooked, bent tusk and a mischievous grin, bold clean shapes, thick dark outline, warm gold and deep brown palette with a touch of ember red, a small crossed hammer and tankard detail optional, wordmark "JAVALI TORTO" in chunky hand-carved fantasy lettering below with the smaller words "GAMES" under it, flat vector emblem with subtle metallic shading, centered composition, transparent background, no background texture, high contrast so it reads on a dark screen, 3:2 aspect ratio.

Negativo: photo, realistic, blurry, extra text, watermark, background scenery.

## 2) Logo do jogo — Hearthblade
> Title logo for a fantasy tactical RPG called "HEARTHBLADE", in the style of classic Final Fantasy Tactics / Final Fantasy title logos: large engraved metallic gold letters with a thin dark outline and slight bevel, a long sword with a small flame (hearth fire) rising behind or through the letters, cozy tavern warmth mixed with epic knightly feel, subtle ember sparks, symmetrical wide composition, transparent background, no subtitle, no tagline, no extra text, crisp edges that stay readable on a dark blurred background, 16:7 aspect ratio.

Negativo: subtitle, tagline, small text, photo background, realistic render, watermark, blur.

## Dicas
- Gere em tamanho grande (≥1600 px de largura) e exporte em PNG com transparência (se o gerador não tirar o fundo, use um removedor de fundo).
- Teste no celular: o logo do jogo ocupa até ~86% da largura da tela; o da publicadora até ~78%.
- O subtítulo "TACTICAL FORGE" é escrito pelo jogo (constante `GAME_TAG`), por isso o logo não deve trazer texto além do nome.
