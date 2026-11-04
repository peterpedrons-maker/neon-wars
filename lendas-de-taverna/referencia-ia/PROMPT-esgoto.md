# Prompts — props e tiles dos Esgotos de Brumavale (dungeon dos ratos)

**Como usar:** anexe na IA as 2 imagens de referência (`ref-esgoto-estilo.png` e `jogo-floresta.png`) e cole UM prompt por vez (cada um já traz o estilo completo). Me devolva os PNGs grandes: eu recorto, reduzo para a escala do jogo e ajusto a paleta.

## Folha 1 — túneis, canos e estruturas

```
Create a pixel art sprite sheet for a top-down 3/4 view dark-fantasy RPG (similar to Pixel Crawler by Anokolisa / 16-bit). Match EXACTLY the art style of the attached reference images (the crypt props are the target style: same outline, same shading, same palette feel): crisp pixel art, NO anti-aliasing, NO blur, NO gradients, NO smooth shading, hard pixel edges; a 1-pixel dark outline in very dark blue-brown (not pure black); 3 to 4 shade steps per material, soft cel shading, light coming from the TOP-LEFT and shadow at the bottom-right; a limited, slightly desaturated palette: dark blue-gray wet stone, mossy green-gray brick, murky toxic green sewage water, rusty orange iron and copper pipes, rotten brown wood, dirty straw, bone off-white, with tiny accents of glowing fungus green and warm lantern yellow; same camera angle and level of detail as the reference props and rats; every object isolated on a flat transparent (or plain #ff00ff magenta) background, evenly spaced in a grid, never touching or overlapping; no text, no labels, no baked ground shadows, no watermark; consistent scale between objects (the rat in the reference is about 64 px tall, a stone arch is about two people wide). Theme: the SEWERS under the village of Brumavale, home of the giant rat tribe — damp, dark, grimy, toxic, a bit disgusting but charming, not gore.

Sheet 1 — tunnels, pipes and structures (each object in its own grid cell, sizes at game scale):
1. 2 big arched sewer tunnel mouths in a mossy brick wall (one open and dark, one half-blocked by an iron grate), about 80x72 px
2. 3 round iron manhole covers (closed, slightly open, fully open showing a dark hole), flat on the floor, about 24x16 px
3. 4 big drain pipes sticking out of a brick wall: a horizontal one dripping green sludge, a vertical one, a broken leaking one, and a rusty valve pipe with a wheel; about 32x40 px
4. 3 stone catwalk bridge pieces over sewage: straight, corner, and a broken one with a gap; about 48x24 px
5. 2 rusty metal floor grates and 1 iron sluice gate (raised and lowered), about 32x24 px
6. 3 stone columns covered in moss and slime, 2 intact and 1 broken, about 20x56 px
7. 2 wall-mounted iron ladders (one intact, one broken), about 14x48 px
8. 3 rusty barrels, one of them toxic with a glowing green leak, about 16x22 px
9. 1 large circular rusty vault door leading to the rat king's lair, about 64x72 px
```

## Folha 2 — vida, lixo e ninhos

```
Create a pixel art sprite sheet for a top-down 3/4 view dark-fantasy RPG (similar to Pixel Crawler by Anokolisa / 16-bit). Match EXACTLY the art style of the attached reference images (the crypt props are the target style: same outline, same shading, same palette feel): crisp pixel art, NO anti-aliasing, NO blur, NO gradients, NO smooth shading, hard pixel edges; a 1-pixel dark outline in very dark blue-brown (not pure black); 3 to 4 shade steps per material, soft cel shading, light coming from the TOP-LEFT and shadow at the bottom-right; a limited, slightly desaturated palette: dark blue-gray wet stone, mossy green-gray brick, murky toxic green sewage water, rusty orange iron and copper pipes, rotten brown wood, dirty straw, bone off-white, with tiny accents of glowing fungus green and warm lantern yellow; same camera angle and level of detail as the reference props and rats; every object isolated on a flat transparent (or plain #ff00ff magenta) background, evenly spaced in a grid, never touching or overlapping; no text, no labels, no baked ground shadows, no watermark; consistent scale between objects (the rat in the reference is about 64 px tall, a stone arch is about two people wide). Theme: the SEWERS under the village of Brumavale, home of the giant rat tribe — damp, dark, grimy, toxic, a bit disgusting but charming, not gore.

Sheet 2 — rat life, garbage and nests:
1. 3 rat nests made of straw, rags, bones and stolen shiny things, about 40x24 px
2. 4 garbage piles (rotten food, bones, rags, broken bottles), about 32x20 px
3. 3 rotten wooden crates and 2 torn sacks of grain, about 22x20 px
4. 2 big wheels of moldy cheese stacked (one bitten), and 1 pile of stolen coins and trinkets, about 24x18 px
5. 4 glowing green mushroom clusters (small, medium, big, tiny), about 12x14 px to 24x24 px
6. 3 puddles of toxic green slime on the floor, flat, about 32x16 px
7. 4 rat holes in a brick wall base with whiskers and eyes glowing in the dark, about 16x14 px
8. 3 dead fish skeletons and 2 piles of bones, about 20x10 px
9. 2 hanging iron lanterns with a warm flame, and 1 standing oil lamp, about 12x28 px
10. 3 corner cobwebs with a few trapped flies, semi-transparent, about 24x24 px
11. 2 broken wooden rowboats half sunk (a rat pirate boat), about 56x28 px
```

## Folha 3 — chão e água (tiles 16x16 e peças)

```
Create a pixel art sprite sheet for a top-down 3/4 view dark-fantasy RPG (similar to Pixel Crawler by Anokolisa / 16-bit). Match EXACTLY the art style of the attached reference images (the crypt props are the target style: same outline, same shading, same palette feel): crisp pixel art, NO anti-aliasing, NO blur, NO gradients, NO smooth shading, hard pixel edges; a 1-pixel dark outline in very dark blue-brown (not pure black); 3 to 4 shade steps per material, soft cel shading, light coming from the TOP-LEFT and shadow at the bottom-right; a limited, slightly desaturated palette: dark blue-gray wet stone, mossy green-gray brick, murky toxic green sewage water, rusty orange iron and copper pipes, rotten brown wood, dirty straw, bone off-white, with tiny accents of glowing fungus green and warm lantern yellow; same camera angle and level of detail as the reference props and rats; every object isolated on a flat transparent (or plain #ff00ff magenta) background, evenly spaced in a grid, never touching or overlapping; no text, no labels, no baked ground shadows, no watermark; consistent scale between objects (the rat in the reference is about 64 px tall, a stone arch is about two people wide). Theme: the SEWERS under the village of Brumavale, home of the giant rat tribe — damp, dark, grimy, toxic, a bit disgusting but charming, not gore.

Sheet 3 — floor tiles and water:
Part A — seamless 16x16 floor tiles, top-down, that tile in every direction:
- 6 dark wet blue-gray stone flagstone tiles (subtle variation)
- 4 mossy flagstone tiles
- 3 cracked flagstone tiles with weeds
- 3 flagstone tiles with scattered bones and straw
- 4 murky green sewage water tiles (calm surface, slightly different ripples)
- a 3x3 set of transition tiles from stone to sewage water (edges and corners, with a slimy edge)
- 4 mossy dark brick wall tiles (wall face, 16x16) and 2 wall-top tiles
Part B — separate objects on a transparent background:
- 3 big patches of floating garbage and green scum on water, about 40x24 px
- 2 sewage waterfalls pouring from a wall pipe into the channel, about 32x48 px
- 2 stone stairways going down into the water, about 48x40 px
- 3 stepping stones, about 16x12 px
```

## Folha 4 — chefe e extras

```
Create a pixel art sprite sheet for a top-down 3/4 view dark-fantasy RPG (similar to Pixel Crawler by Anokolisa / 16-bit). Match EXACTLY the art style of the attached reference images (the crypt props are the target style: same outline, same shading, same palette feel): crisp pixel art, NO anti-aliasing, NO blur, NO gradients, NO smooth shading, hard pixel edges; a 1-pixel dark outline in very dark blue-brown (not pure black); 3 to 4 shade steps per material, soft cel shading, light coming from the TOP-LEFT and shadow at the bottom-right; a limited, slightly desaturated palette: dark blue-gray wet stone, mossy green-gray brick, murky toxic green sewage water, rusty orange iron and copper pipes, rotten brown wood, dirty straw, bone off-white, with tiny accents of glowing fungus green and warm lantern yellow; same camera angle and level of detail as the reference props and rats; every object isolated on a flat transparent (or plain #ff00ff magenta) background, evenly spaced in a grid, never touching or overlapping; no text, no labels, no baked ground shadows, no watermark; consistent scale between objects (the rat in the reference is about 64 px tall, a stone arch is about two people wide). Theme: the SEWERS under the village of Brumavale, home of the giant rat tribe — damp, dark, grimy, toxic, a bit disgusting but charming, not gore.

Sheet 4 — boss lair and extras:
1. 1 throne of the Rat King made of garbage, bones, rusty swords and stolen treasure, about 56x64 px
2. 1 huge rat king nest with a pile of treasure and a crown, about 72x40 px
3. 2 stone rat statues with red gem eyes, about 24x40 px
4. 3 torn banners with a rat skull symbol (dark red, brown, green), about 16x48 px
5. 2 wall-mounted torches with a flame, about 12x36 px
6. 3 big wooden treasure chests in different states (closed, open with coins, broken), about 28x24 px
7. 2 iron cages with pet rats inside, about 24x28 px
8. 1 giant rusty trap with spikes (open) and 1 snap-trap with cheese bait, about 24x20 px
9. 3 hanging ropes and chains with hooks, about 12x40 px
10. 1 stone sewer shrine to a rat god with candles and offerings, about 40x44 px
```

