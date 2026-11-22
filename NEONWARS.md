# Neon Wars — auditoria e plano de refazer (decisões do dono)

Jogo web (React + Vite + canvas, `src/`), PWA, ~14 mil linhas. Estilo desejado: **Vampire Survivors com foco em BUILD**. Meta: **publicar** (Android/iOS/PC). Hearthblade é outro jogo (`lendas-de-taverna/`); as regras dele ficam no `CLAUDE.md`, as do Neon Wars aqui.

## Decisões do dono
- Aproveitar o **núcleo** (motor, mapas, naves/classes, habilidades, upgrades, meta-progressão) e refazer o resto; o projeto é antigo (feito quando a IA errava muito) e precisa ser alinhado/limpo.
- **Sem multiplayer** (trabalho desnecessário). **Ranking sim**, depois.
- **Sem conta/login por enquanto** (jogo 100% offline, save local). Back-end só quando houver ranking.
- **Músicas atuais vieram da internet → NÃO podem ir para a loja.** Trocar por trilha original/licenciada (instrumentos reais amostrados, como no Hearthblade, ou banco CC0).
- Publicar: Capacitor (Android/iOS) + Tauri (Windows/Mac/Linux, Steam), do mesmo código web.

## Auditoria
| Parte | Arquivos | Destino |
|---|---|---|
| Núcleo do jogo | `game/engine.ts` (1898), `abilities.ts` (1291), `entities.ts`, `maps.ts`, `upgrades.ts`, `types.ts`, `constants.ts`, `renderer.ts` (2338) | **manter** e revisar para o foco em build |
| Meta-progressão | `meta.ts`, `achievements.ts`, `PlasmaShop.tsx`, `UpgradeScreen.tsx`, `LevelUpScreen.tsx` | manter; salvar em `localStorage` |
| Telas | `MainMenu`, `ClassSelect`, `MapSelect`, `HUD`, `GameOver`, `HowToPlay`, `TouchControls`, `ShipCanvas` | manter |
| **Multiplayer** | `multiplayer.ts`, `MultiplayerLobby.tsx` (558), `CoopGameCanvas.tsx` (500), parte de `Index.tsx` | **remover** |
| **Conta/online** | `hooks/useAuth.tsx`, `AuthScreen.tsx`, `integrations/supabase/*`, `supabase/migrations` (tabelas `profiles`, `game_progress`, `leaderboard`, `public_rooms`) | **remover do fluxo agora** (migrações ficam arquivadas) |
| Ranking | `Leaderboard.tsx` + tabela `leaderboard` | **trocar por ranking local**, deixando uma interface `submitScore/getTop` para ligar a um back-end depois |
| Áudio | `audio.ts` (2043 linhas, síntese) + `public/music-base.mp3` (música da internet) | **trocar a música**; revisar o resto |
| PWA | `public/sw.js`, `manifest.webmanifest`, `InstallPrompt.tsx` | manter até empacotar |

## Ordem sugerida
1. Limpeza: tirar multiplayer + conta (jogo abre direto no menu, save local), rodar build/testes.
2. Ranking local + interface pronta para back-end.
3. Música: remover `music-base.mp3`, criar trilha própria.
4. Revisão de design para **build** (sinergias entre armas/passivas/evoluções, escolha por nível, raridade), com o dono.
5. Visual/ritmo estilo Vampire Survivors.
6. Empacotar (Capacitor + Tauri), ícones/telas das lojas, política de privacidade.

## Sobre Supabase
Para jogo offline com ranking: **não precisa agora**. No futuro, ranking global pode usar (a) Supabase com nome anônimo + validação no servidor, ou (b) placar nativo das plataformas (Google Play Games, Game Center, Steam). Decidir só na etapa do ranking.

## Andamento
- **Etapa 1 (limpeza) FEITA:** removidos multiplayer (`multiplayer.ts`, `MultiplayerLobby`, `CoopGameCanvas`), conta/login (`useAuth`, `AuthScreen`), `src/integrations/supabase` e a dependência `@supabase/supabase-js`. O jogo abre direto no menu; progresso e ranking ficam em `localStorage` (`neon-wars-lb` para o ranking). Build, teste e fluxo menu → nave → mapa conferidos. Ficam arquivados, sem uso: `supabase/` (migrações), `.env` (chaves públicas do projeto antigo) e `bun.lock*` (desatualizados). Os textos de tradução do multiplayer/login continuam em `i18n.tsx` (limpar depois).
- Próximo: etapa 2 (ranking local com interface pronta) e etapa 3 (música).

## Visão do jogo (dono)
- **Gênero:** Vampire Survivors + **bullet hell**, com **foco em BUILD**. Propósito: **dopamina** — explosões, cores, coisas espalhadas na tela, muito feedback.
- **Armas/builds:** muitas armas e passivas que **combinam entre si** (sinergias e evoluções, como no Vampire Survivors), a build do jogador define a partida.
- **Inimigos e chefes:** inimigos que atiram padrões (bullet hell) e **chefes bem feitos** (hoje: chefe a cada 5 ondas, mega-chefes `archon` na onda 15 e `oblivion` na 30).
- **Refazer:** visual inteiro (cenário, naves, fases), **menus** (hoje genéricos e de baixa qualidade), **fluidez** dos movimentos e **diferenciação clara entre as naves** (16 hoje).
- **Pendente de decisão:** nome das sinergias, lista de armas/evoluções, padrões de bullet hell por chefe, direção de arte.

## Estado atual (conferido no código)
- Já existe chefe: a cada 5 ondas (`BOSS_WAVE_INTERVAL`), com chefe do mapa ou `mothership/vortex/colossus`; **mega-chefes `archon` (onda 15) e `oblivion` (onda 30)**; chefes por mapa (lava_dragon, void_lord, frost_titan…).
- ~23 armas e ~10 passivas em `abilities.ts`, mais 8 upgrades simples em `upgrades.ts`; 16 naves; vários mapas com inimigos próprios.
- Sinergias entre armas/passivas: ainda não existem de forma explícita (a investigar).
