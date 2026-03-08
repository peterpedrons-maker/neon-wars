

# ⚔️ Medieval Wars — Geometry Wars Fantasy Medieval

Um jogo de arena top-down estilo Geometry Wars com temática Fantasy Medieval, controles teclado+mouse e touch, seleção de classe e sistema completo de progressão.

## 🎮 Tela Inicial & Menu
- Tela título com arte medieval estilizada (título em fonte gótica, fundo com castelo/arena)
- Menu: **Jogar**, **Leaderboard**, **Como Jogar**
- Seleção de classe antes de cada partida: **Mago** (projéteis mágicos), **Arqueiro** (flechas rápidas), **Guerreiro** (ataque corpo-a-corpo em área)

## 🕹️ Gameplay Principal (Canvas 2D)
- Arena única medieval (com bordas de pedra/muralha)
- **Controles Desktop**: WASD para mover, mouse para mirar, clique para atacar
- **Controles Mobile**: Joystick virtual esquerdo (mover) e direito (mirar/atacar)
- Sistema de ondas com dificuldade crescente (mais inimigos, mais rápidos, novos tipos)
- HUD: vida, pontuação, onda atual, habilidade especial

## 👾 Inimigos
- **Esqueletos** — básicos, andam em direção ao jogador
- **Slimes** — lentos, se dividem ao morrer
- **Morcegos** — rápidos, movimento errático
- **Cavaleiros Sombrios** — resistentes, avançam devagar
- **Boss** a cada 5 ondas (Dragão, Lich, Golem de Pedra) com padrões de ataque únicos

## ⚡ Power-ups & Upgrades
- Power-ups aparecem na arena: velocidade, ataque triplo, escudo, cura
- **Tela de upgrade entre ondas**: escolha 1 de 3 melhorias aleatórias (dano, velocidade, vida max, habilidade especial)

## 🏆 Progressão & Leaderboard
- Pontuação baseada em inimigos derrotados e ondas sobrevividas
- Leaderboard local (localStorage) com nome e pontuação
- Tela de Game Over mostrando estatísticas da partida

## 🎨 Visual & Efeitos
- Estilo pixel-art/retro com paleta medieval (tons de marrom, dourado, roxo escuro)
- Partículas ao derrotar inimigos (explosões mágicas)
- Efeitos de flash ao tomar dano
- Animações suaves de movimento e ataque

## 🔧 Técnico
- Renderização via Canvas 2D com game loop customizado
- Detecção de dispositivo para alternar entre controles teclado/mouse e touch
- Estado do jogo gerenciado via hooks React

