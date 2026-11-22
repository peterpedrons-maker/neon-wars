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

## Direção visual (dono + proposta)
- Base: **neon vetorial estilo Geometry Wars** (formas geométricas, brilho/bloom, partículas, grade). É seguro para publicar: o estilo não é protegido; só **não copiar nomes, formas nem sons específicos** do Geometry Wars. É barato de produzir, fica ótimo no celular e entrega "dopamina" por efeito (explosões, rastros, tremor, cores).
- Cada nave e cada inimigo = **silhueta geométrica própria + cor própria + padrão de movimento próprio** (diferenciação que o dono pediu).
- Verificar disponibilidade do nome "Neon Wars" nas lojas/marca antes de publicar (nome comum).

## ARMAS v2 — proposta (de 23 para 12; 5 modificadores; 8 passivas)
Regras: cada arma tem **papel único** (alvo único, multidão, controle, defesa, rajada), **silhueta de efeito própria** e uma **forma máxima (nível 8)** que muda visivelmente o comportamento. Todas ganham etiquetas de elemento (Cinético, Fogo, Gelo, Elétrico, Vazio, Plasma) para as sinergias da etapa seguinte. A arma inicial continua sendo o tiro próprio de cada nave.

| # | Arma (vem de) | Como funciona (nv 1) | Evolução por nível (2–7) | **Nível 8 (forma máxima)** |
|---|---|---|---|---|
| 1 | **Raio Prisma** (Ion Beam) | feixe periódico na direção da mira, perfura tudo | +dano, +comprimento, −recarga | **Prisma**: o feixe se divide em 3 e gira 360° por 2 s, queimando |
| 2 | **Enxame de Mísseis** (Missile Barrage) | 2 mísseis teleguiados por salva | +mísseis, +dano de explosão | **Ogivas em Cacho**: cada míssil explode em 6 mini-mísseis que caçam outros alvos |
| 3 | **Lâmina Bumerangue** (Boomerang) | lâmina que vai e volta, acerta nas duas passagens | +lâminas, +tamanho, perfura | **Tríade Cortante**: 3 lâminas em órbita ampla que voltam deixando rastro de corte |
| 4 | **Satélites** (Orbitals) | drones orbitam e ferem no contato | +drones, +raio, +velocidade | **Anel de Escudo**: 8 satélites que também **destroem balas inimigas** e disparam lasers para fora |
| 5 | **Arco Voltaico** (Chain Lightning + Tesla + Lightning Ring) | raio salta entre inimigos próximos | +saltos, +dano, atordoa | **Tempestade**: arcos permanentes ligando até 12 inimigos, atordoamento em cadeia |
| 6 | **Pulso Nova** (Shockwave + Frost Nova) | anel de choque periódico ao redor da nave, empurra | +raio, +dano, −recarga | **Dupla Nova**: dois anéis seguidos que **apagam todas as balas inimigas** da tela e empurram forte |
| 7 | **Raio Ricochete** (NOVA, no lugar do Rastro Incandescente) | raio rápido que **quica de inimigo em inimigo** (3 quicadas) | +quicadas, +dano, +velocidade | **Pinball Neon**: 10 quicadas, cada quicada solta um anel de faíscas; se não houver alvo, ricocheteia nas bordas da tela (nunca desperdiça) |
| 8 | **Singularidade** (Gravity Well + Void Rift) | buraco negro que puxa inimigos e balas | +raio, +força, +dano | **Colapso**: o buraco negro implode numa explosão gigante e deixa uma fenda que continua puxando |
| 9 | **Railgun** (Canhão Pesado) | tiro lento e devastador que atravessa tudo em linha | +dano, −recarga, +espessura | **Disparo Duplo**: 2 tiros, tremor de tela e raio residual que queima a linha por 1 s |
| 10 | **Sentinelas** (Sentry Drones) | drones autônomos que miram e atiram | +drones, +cadência | **Rede Laser**: sentinelas se ligam por feixes formando uma rede que fere quem a cruza |
| 11 | **Cristais Gélidos** (Raio de Gelo + Frost) | leque de lascas de gelo que desacelera | +lascas, +lentidão, congela | **Congelamento Total**: congela a tela por 1,5 s; quem morre congelado **estilhaça** em dano de área |
| 12 | **Bomba Fragmentada** (Explosivo + Spray Ácido) | projétil que explode e deixa poça corrosiva | +raio, +dano, +poça | **Cascata**: a explosão gera 3 bombas que explodem em cadeia, cada uma deixando poça |

**Modificadores (5)** — tornam qualquer arma compatível mais forte e criam builds: Perfuração, Ricochete, Guiado (auto-mira), Multi-tiro, Explosivo.
**Passivas (8):** Dano, Cadência, Velocidade, Área/Alcance, Ímã de XP, Nano-Reparo, Sorte (+crítico), Blindagem.
Removidas/fundidas: **Rastro Incandescente (fogo atrás da nave: não é projétil e obriga os inimigos a seguirem o jogador; o dono pediu para tirar)**, Neon Aura, Raio Cadeia duplicado, Evasão, XP Boost, Vampirismo (podem voltar como passivas se o dono quiser).

**Decisões do dono:** (1) **o nível 8 NÃO exige passiva**: basta chegar ao nível; (2) **3 slots de arma** por enquanto (aumentar depois, se fizer sentido); (3) tirar o Rastro Incandescente e acrescentar o **Raio Ricochete**; (4) o Modificador "Ricochete" continua existindo para dar quique a outras armas de projétil (build "raio que ricocheteia").
**Em aberto:** sinergias entre elementos; padrões de bala dos chefes; como as armas aparecem nas escolhas de nível (raridade/peso); passivas extras.
