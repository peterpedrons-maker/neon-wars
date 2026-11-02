# Prompt — props e tiles da Floresta dos Goblins

**Como usar:** anexe na IA as 2 imagens de referência (`jogo-floresta.png` e `estilo-props.png`) e cole o prompt abaixo.
Gere uma folha por vez (a lista é dividida em 4 folhas) para a IA manter o mesmo estilo.
Me devolva os PNGs em tamanho grande: eu recorto, reduzo para a escala do jogo e ajusto a paleta para combinar.

---

## Prompt base (cole sempre)

```
Create a pixel art sprite sheet for a top-down 3/4 view fantasy RPG (similar to Pixel Crawler by Anokolisa / Stardew-style 16-bit).
Match EXACTLY the art style of the attached reference images:
- crisp pixel art, NO anti-aliasing, NO blur, NO gradients, NO smooth shading, hard pixel edges
- 1-pixel dark outline in very dark brown (not pure black)
- 3 to 4 shade steps per material, soft cel shading, light coming from the TOP-LEFT, shadow side at the bottom-right
- limited, slightly desaturated palette: moss greens, teal-blue pines, warm browns, bone off-white, dirty leather, rust red; small accents of poison green and yellow
- same camera angle and same level of detail as the reference trees, rocks, fence and barrels
- every object isolated on a flat transparent (or plain #ff00ff magenta) background, evenly spaced in a grid, never touching or overlapping
- no text, no labels, no ground shadows baked in, no watermark
- consistent scale between objects: a tree is about 3x the height of a person, a barrel is about knee height
Theme: a dark, gloomy GOBLIN TRIBE forest camp — crude, handmade, tribal, a bit creepy but charming, not gore.
```

## Folha 1 — acampamento (props grandes)

```
Sheet 1 — goblin camp structures (each one on its own grid cell):
1. 4 variations of a goblin hide tent (patched animal skins, crossed wooden poles on top, dark entrance, a small skull above the door), about 48x40 px at game scale
2. 3 variations of a tall tribal totem pole (carved green goblin face on top with red and yellow feathers, a skull in the middle, boar tusks and red war paint below), about 20x64 px
3. 1 crude wooden goblin watchtower / lookout platform on stilts with rope and hanging bones, about 56x80 px
4. 1 small crude wooden hut with a leaf and hide roof, about 56x56 px
5. 1 black iron cauldron on a tripod with bubbling poison-green liquid, about 24x22 px
6. 1 meat spit (wooden Y-stakes with a roasting boar) over a small fire pit, about 32x24 px
7. 1 hide-drying rack with stretched animal skins, about 32x30 px
8. 1 weapon rack with crude clubs, rusty daggers and a shield, about 28x26 px
```

## Folha 2 — decoração e perigos

```
Sheet 2 — goblin decoration:
1. 5 variations of a skull on a wooden stake (different skulls: goblin, boar, human), about 12x28 px
2. 5 variations of a bone pile (ribs, long bones, 1-2 skulls), about 28x14 px
3. 3 variations of a sharpened-log palisade segment tied with rope, about 32x28 px
4. 2 variations of a spiked wooden barricade (crossed sharpened logs, "cheval de frise"), about 40x20 px
5. 2 crude goblin war banners on a pole (green or red cloth with a painted skull or fang symbol), about 16x48 px
6. 2 torch posts with a flame, about 12x36 px
7. 4 variations of big forest mushrooms (red with white dots, purple, pale yellow), clusters of 2-3, about 22x16 px
8. 3 variations of sacks, crates and a small loot pile (coins, a crooked chest), about 24x20 px
```

## Folha 3 — árvores e natureza sombria

```
Sheet 3 — dark goblin forest nature (same style and scale as the reference trees):
1. 4 dark pine trees (very dark teal-green), tall, ~48x96 px
2. 2 gnarled dead trees with a few skulls or bone charms hanging from the branches, ~64x100 px
3. 2 twisted giant roots / fallen rotten logs with moss, ~40x20 px
4. 4 dark bushes and 3 thorny bramble patches, ~24x20 px
5. 3 mossy rocks, 3 small stones, ~28x30 px
6. 3 small swampy puddles / mud patches seen from above (transparent background), ~32x16 px
7. A few ground decorations: dry twigs, small bones, tiny purple flowers and mushrooms, ~8x8 px each
```

## Folha 4 — tiles de chão (16x16, repetíveis)

```
Sheet 4 — seamless 16x16 ground tiles, top-down, same pixel style:
- 6 dark moss-green grass tiles (subtle variation, no obvious pattern)
- 6 packed mud / dirt tiles, brown with small pebbles
- 3 tiles of dirt with scattered bones
- 3 trampled dark grass tiles
- a 3x3 set of transition tiles dirt-to-grass (edges and corners)
All tiles must tile seamlessly in every direction.
```

---

## Dicas

- IAs de imagem comuns erram a grade de pixels. Se puder, use uma ferramenta especializada em pixel art (por exemplo Retro Diffusion, PixelLab ou Scenario) ou peça à IA para "gerar em tamanho grande, com pixels grandes e nítidos".
- Se uma folha vier ruim, regenere só ela: não precisa refazer tudo.
- Os tiles de chão (folha 4) são os mais difíceis para a IA. Se não saírem repetíveis, eu continuo gerando o chão em código e usamos a IA só para os props.

## Inimigos (depois)

Para os sprites animados dos inimigos o jogo usa quadros de 64x64, 4 direções (cima, esquerda, baixo, direita): andar com 9 quadros, atacar com 6 e levar dano com 6. Quando chegarmos nessa etapa eu preparo um prompt específico com as imagens dos inimigos atuais como referência.
