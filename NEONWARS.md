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
