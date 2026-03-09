import React, { createContext, useContext, useState, useCallback, ReactNode } from 'react';

export type Language = 'pt' | 'en';

const translations = {
  // ===== MAIN MENU =====
  subtitle: { pt: 'Arena de Sobrevivência Cósmica', en: 'Cosmic Survival Arena' },
  play: { pt: '🚀 Jogar', en: '🚀 Play' },
  multiplayer_coop: { pt: '🎮 Multiplayer Coop', en: '🎮 Multiplayer Coop' },
  plasma_shop: { pt: '⚡ Loja de Plasma', en: '⚡ Plasma Shop' },
  achievements_btn: { pt: '🏆 Conquistas', en: '🏆 Achievements' },
  leaderboard: { pt: '📊 Leaderboard', en: '📊 Leaderboard' },
  how_to_play: { pt: '📡 Como Jogar', en: '📡 How to Play' },
  logout: { pt: 'Sair', en: 'Logout' },
  controls_hint: { pt: 'WASD + Mouse • Touch Friendly', en: 'WASD + Mouse • Touch Friendly' },
  runs: { pt: 'Runs', en: 'Runs' },
  kills: { pt: 'Kills', en: 'Kills' },
  best_wave: { pt: 'Best Wave', en: 'Best Wave' },
  best_score: { pt: 'Best Score', en: 'Best Score' },
  plasma: { pt: 'Plasma', en: 'Plasma' },
  language: { pt: '🌐 EN', en: '🌐 PT' },

  // ===== AUTH =====
  auth_subtitle: { pt: 'Arena de Sobrevivência Cósmica', en: 'Cosmic Survival Arena' },
  login: { pt: '🔑 ENTRAR', en: '🔑 LOGIN' },
  signup: { pt: '🚀 CRIAR CONTA', en: '🚀 SIGN UP' },
  pilot_name: { pt: 'Nome de Piloto', en: 'Pilot Name' },
  pilot_name_placeholder: { pt: 'Ex: NeonSlayer', en: 'Ex: NeonSlayer' },
  email: { pt: 'Email', en: 'Email' },
  email_placeholder: { pt: 'piloto@neonwars.com', en: 'pilot@neonwars.com' },
  password: { pt: 'Senha', en: 'Password' },
  processing: { pt: '⏳ Processando...', en: '⏳ Processing...' },
  login_btn: { pt: '🔑 Entrar', en: '🔑 Login' },
  signup_btn: { pt: '🚀 Criar Conta', en: '🚀 Sign Up' },
  pilot_name_error: { pt: 'Nome de piloto deve ter pelo menos 2 caracteres', en: 'Pilot name must be at least 2 characters' },
  signup_success: { pt: 'Conta criada! Verifique seu email para confirmar o cadastro.', en: 'Account created! Check your email to confirm.' },
  cloud_save: { pt: 'Progresso salvo na nuvem automaticamente', en: 'Progress saved to cloud automatically' },
  loading: { pt: 'Carregando...', en: 'Loading...' },

  // ===== CLASS SELECT =====
  choose_ship: { pt: 'Escolha sua Nave', en: 'Choose your Ship' },
  back: { pt: '← Voltar', en: '← Back' },

  // ===== SHIP DESCRIPTIONS =====
  ship_phantom_desc: { pt: 'Nave ágil com disparos energéticos. Especial: Nova de plasma.', en: 'Agile ship with energy shots. Special: Plasma nova.' },
  ship_interceptor_desc: { pt: 'Ultra veloz com tiro rápido. Especial: Lock-on barrage.', en: 'Ultra fast with rapid fire. Special: Lock-on barrage.' },
  ship_titan_desc: { pt: 'Ataque devastador em área. Especial: Onda de choque.', en: 'Devastating area attack. Special: Shockwave.' },
  ship_spectre_desc: { pt: 'Furtiva com teleporte. Especial: Teleporte + explosão.', en: 'Stealth with teleport. Special: Teleport + explosion.' },
  ship_valkyrie_desc: { pt: 'Guerreira alada, tiro duplo. Especial: Chuva de lanças.', en: 'Winged warrior, double shot. Special: Spear rain.' },
  ship_juggernaut_desc: { pt: 'Fortaleza indestrutível. Especial: Campo de destruição.', en: 'Indestructible fortress. Special: Destruction field.' },
  ship_wraith_desc: { pt: 'Fantasma que cria clones sombrios. Especial: Invisibilidade + clones.', en: 'Ghost that creates shadow clones. Special: Invisibility + clones.' },
  ship_sentinel_desc: { pt: 'Tanque com barreira protetora. Especial: Escudo + reflexão.', en: 'Tank with barrier. Special: Shield + reflection.' },
  ship_tempest_desc: { pt: 'Controlador de ventos. Especial: Tornado que puxa inimigos.', en: 'Wind controller. Special: Tornado pulls enemies.' },
  ship_venom_desc: { pt: 'Envenenador com tiros tóxicos. Especial: Nuvem venenosa.', en: 'Poisoner with toxic shots. Special: Poison cloud.' },
  ship_nova_ship_desc: { pt: 'Poder destrutivo bruto. Especial: Supernova massiva.', en: 'Raw destructive power. Special: Massive supernova.' },
  ship_chronos_desc: { pt: 'Manipulador do tempo. Especial: Congela todos os inimigos.', en: 'Time manipulator. Special: Freezes all enemies.' },
  ship_leviathan_desc: { pt: 'Colosso devorador. Especial: Devora e se cura.', en: 'Devouring colossus. Special: Devours and heals.' },
  ship_raptor_desc: { pt: 'O mais veloz. Tiro ultra-rápido. Especial: Blitz dash.', en: 'The fastest. Ultra-rapid fire. Special: Blitz dash.' },
  ship_oracle_desc: { pt: 'Tiros rastreadores. Especial: Marca todos os inimigos.', en: 'Tracking shots. Special: Marks all enemies.' },
  ship_pyro_desc: { pt: 'Lança-chamas devastador. Especial: Anel de fogo.', en: 'Devastating flamethrower. Special: Fire ring.' },
  ship_stats_dmg: { pt: 'DMG', en: 'DMG' },
  ship_stats_vel_media: { pt: 'VEL: Média', en: 'SPD: Medium' },
  ship_stats_vel_alta: { pt: 'VEL: Alta', en: 'SPD: High' },
  ship_stats_vel_baixa: { pt: 'VEL: Baixa', en: 'SPD: Low' },
  ship_stats_vel_lenta: { pt: 'VEL: Lenta', en: 'SPD: Slow' },
  ship_stats_vel_maxima: { pt: 'VEL: Máxima', en: 'SPD: Max' },
  ship_stats_vel_media_plus: { pt: 'VEL: Média+', en: 'SPD: Medium+' },
  ship_stats_vel_media_minus: { pt: 'VEL: Média-', en: 'SPD: Medium-' },

  // ===== MAP SELECT =====
  select_map: { pt: 'Selecione o Mapa', en: 'Select Map' },
  easy: { pt: 'Fácil', en: 'Easy' },
  medium: { pt: 'Médio', en: 'Medium' },
  hard: { pt: 'Difícil', en: 'Hard' },
  easy_hint: { pt: 'Mais tranquilo', en: 'More relaxed' },
  medium_hint: { pt: 'Padrão', en: 'Standard' },
  hard_hint: { pt: 'Bem puxado', en: 'Very challenging' },
  unlock_milestones: { pt: 'Complete milestones para desbloquear', en: 'Complete milestones to unlock' },
  hazards_active: { pt: '⚠️ Hazards ativos', en: '⚠️ Active hazards' },

  // ===== HOW TO PLAY =====
  htp_title: { pt: '📡 Como Jogar', en: '📡 How to Play' },
  htp_desktop: { pt: '🖥️ Desktop', en: '🖥️ Desktop' },
  htp_move: { pt: 'Mover nave', en: 'Move ship' },
  htp_aim: { pt: 'Mirar', en: 'Aim' },
  htp_shoot: { pt: 'Disparar', en: 'Shoot' },
  htp_special: { pt: 'Habilidade Especial', en: 'Special Ability' },
  htp_mobile: { pt: '📱 Mobile', en: '📱 Mobile' },
  htp_move_joystick: { pt: 'Mover', en: 'Move' },
  htp_aim_joystick: { pt: 'Mirar e Disparar', en: 'Aim and Shoot' },
  htp_special_btn: { pt: 'Habilidade Especial', en: 'Special Ability' },
  htp_powerups: { pt: '⚡ Power-ups', en: '⚡ Power-ups' },
  htp_speed: { pt: 'Velocidade', en: 'Speed' },
  htp_speed_desc: { pt: 'Propulsão acelerada', en: 'Accelerated propulsion' },
  htp_triple: { pt: 'Tiro Triplo', en: 'Triple Shot' },
  htp_triple_desc: { pt: 'Disparo em leque', en: 'Fan shot' },
  htp_shield: { pt: 'Escudo', en: 'Shield' },
  htp_shield_desc: { pt: 'Bloqueia o próximo golpe', en: 'Blocks next hit' },
  htp_repair: { pt: 'Reparo', en: 'Repair' },
  htp_repair_desc: { pt: 'Recupera HP', en: 'Restores HP' },
  htp_tip_title: { pt: '⚠️ Dica', en: '⚠️ Tip' },
  htp_tip: { pt: 'A cada 5 waves um Boss aparece! Colete power-ups e escolha upgrades entre as waves.', en: 'Every 5 waves a Boss appears! Collect power-ups and choose upgrades between waves.' },
  boss: { pt: 'Boss', en: 'Boss' },

  // ===== LEADERBOARD =====
  lb_title: { pt: '🏆 Leaderboard', en: '🏆 Leaderboard' },
  lb_empty: { pt: 'Nenhum score ainda. Jogue para aparecer aqui!', en: 'No scores yet. Play to appear here!' },

  // ===== ACHIEVEMENTS =====
  ach_title: { pt: '🏆 CONQUISTAS', en: '🏆 ACHIEVEMENTS' },
  ach_all: { pt: 'Todas', en: 'All' },
  ach_global: { pt: 'Globais', en: 'Global' },
  ach_easy: { pt: 'Fácil', en: 'Easy' },
  ach_moderate: { pt: 'Moderada', en: 'Moderate' },
  ach_hard: { pt: 'Difícil', en: 'Hard' },
  ach_extreme: { pt: 'Extrema', en: 'Extreme' },
  ach_section_easy: { pt: '⚡ Fácil', en: '⚡ Easy' },
  ach_section_moderate: { pt: '⭐ Moderada', en: '⭐ Moderate' },
  ach_section_hard: { pt: '🔥 Difícil', en: '🔥 Hard' },
  ach_section_extreme: { pt: '💀 Extrema', en: '💀 Extreme' },

  // ===== PLASMA SHOP =====
  shop_title: { pt: '⚡ PLASMA SHOP', en: '⚡ PLASMA SHOP' },
  shop_all: { pt: 'Tudo', en: 'All' },
  shop_base_weapons: { pt: 'Armas Base', en: 'Base Weapons' },
  shop_elemental: { pt: 'Elementais', en: 'Elemental' },
  shop_ships: { pt: 'Naves', en: 'Ships' },
  shop_slots: { pt: 'Slots', en: 'Slots' },
  shop_stats: { pt: 'Stats', en: 'Stats' },
  shop_passives: { pt: 'Passivas', en: 'Passives' },

  // ===== SHOP ITEM DESCRIPTIONS =====
  shop_orbital_desc: { pt: '+1 drone orbital que causa dano ao contato', en: '+1 orbital drone dealing contact damage' },
  shop_aura_desc: { pt: 'Aura de dano ao redor da nave', en: 'Damage aura around the ship' },
  shop_chain_desc: { pt: 'Eliminar inimigo causa dano em cadeia', en: 'Killing enemy causes chain damage' },
  shop_multishot_desc: { pt: '+1 projétil por disparo', en: '+1 projectile per shot' },
  shop_explosion_desc: { pt: 'Projéteis explodem ao acertar', en: 'Projectiles explode on hit' },
  shop_homing_desc: { pt: 'Chance de projéteis perseguirem inimigos', en: 'Chance for homing projectiles' },
  shop_piercing_desc: { pt: 'Projéteis atravessam inimigos', en: 'Projectiles pierce through enemies' },
  shop_ricochet_desc: { pt: 'Projéteis ricocheteiam em outro alvo', en: 'Projectiles ricochet to another target' },
  shop_ion_desc: { pt: 'Feixe periódico na direção da mira', en: 'Periodic beam toward aim direction' },
  shop_shockwave_desc: { pt: 'Explosão periódica ao redor da nave', en: 'Periodic explosion around ship' },
  shop_sentry_desc: { pt: 'Drones automáticos disparam nos inimigos', en: 'Auto-firing sentry drones' },
  shop_frost_desc: { pt: 'Explosão que congela inimigos próximos', en: 'Explosion that freezes nearby enemies' },
  shop_missile_desc: { pt: 'Mísseis teleguiados automáticos', en: 'Auto-guided missiles' },
  shop_plasma_field_desc: { pt: 'Zonas de plasma no chão', en: 'Plasma zones on the ground' },
  shop_lightning_desc: { pt: 'Raios automáticos atingem inimigos', en: 'Auto lightning strikes enemies' },
  shop_flame_desc: { pt: 'Rastro de fogo ao se mover', en: 'Fire trail when moving' },
  shop_chain_lightning_desc: { pt: 'Raios que saltam entre inimigos', en: 'Lightning that arcs between enemies' },
  shop_ice_beam_desc: { pt: 'Congela inimigos com slow prolongado', en: 'Freezes enemies with prolonged slow' },
  shop_boomerang_desc: { pt: 'Projétil que retorna, atingindo duas vezes', en: 'Returning projectile, hits twice' },
  shop_heavy_cannon_desc: { pt: 'Disparo lento mas devastador', en: 'Slow but devastating shot' },
  shop_acid_desc: { pt: 'Ácido que causa dano contínuo (DoT)', en: 'Acid dealing damage over time (DoT)' },
  shop_gravity_desc: { pt: 'Zones que puxam e esmagam inimigos', en: 'Zones that pull and crush enemies' },
  shop_tesla_desc: { pt: 'Arcos elétricos automáticos entre inimigos', en: 'Auto electric arcs between enemies' },
  shop_void_desc: { pt: 'Portais que sugam e destroem inimigos', en: 'Portals that suck and destroy enemies' },

  // Shop ship descriptions
  shop_spectre_desc: { pt: 'Nave furtiva com teleporte. Alta velocidade, baixa vida.', en: 'Stealth ship with teleport. High speed, low HP.' },
  shop_valkyrie_desc: { pt: 'Guerreira alada com tiro duplo e chuva de lanças.', en: 'Winged warrior with double shot and spear rain.' },
  shop_juggernaut_desc: { pt: 'Fortaleza indestrutível. 5 HP base, dano massivo.', en: 'Indestructible fortress. 5 base HP, massive damage.' },
  shop_sentinel_desc: { pt: 'Tanque com barreira. Especial: Escudo + reflexão.', en: 'Tank with barrier. Special: Shield + reflection.' },
  shop_venom_desc: { pt: 'Envenenador com tiros tóxicos persistentes.', en: 'Poisoner with persistent toxic shots.' },
  shop_nova_desc: { pt: 'Poder bruto. Especial: Supernova devastadora.', en: 'Raw power. Special: Devastating supernova.' },
  shop_leviathan_desc: { pt: 'Colosso devorador. 8 HP, dano extremo.', en: 'Devouring colossus. 8 HP, extreme damage.' },
  shop_oracle_desc: { pt: 'Tiros rastreadores inteligentes.', en: 'Smart tracking shots.' },
  shop_pyro_desc: { pt: 'Lança-chamas devastador de curto alcance.', en: 'Devastating short-range flamethrower.' },

  // Shop perm stats
  shop_hp_name: { pt: '+1 HP Máximo', en: '+1 Max HP' },
  shop_hp_desc: { pt: 'Começa cada run com +1 HP', en: 'Start each run with +1 HP' },
  shop_damage_name: { pt: '+10% Dano Base', en: '+10% Base Damage' },
  shop_damage_desc: { pt: 'Bônus de dano permanente', en: 'Permanent damage bonus' },
  shop_speed_name: { pt: '+5% Velocidade', en: '+5% Speed' },
  shop_speed_desc: { pt: 'Move mais rápido desde o início', en: 'Move faster from the start' },
  shop_magnet_name: { pt: '+20% XP Magnet', en: '+20% XP Magnet' },
  shop_magnet_desc: { pt: 'Coleta XP de mais longe', en: 'Collect XP from farther away' },
  shop_armor_name: { pt: '+10% Redução Dano', en: '+10% Damage Reduction' },
  shop_armor_desc: { pt: 'Recebe menos dano permanentemente', en: 'Take less damage permanently' },
  shop_plasma_mult_name: { pt: '+10% Plasma Ganho', en: '+10% Plasma Earned' },
  shop_plasma_mult_desc: { pt: 'Ganha mais plasma por run', en: 'Earn more plasma per run' },
  shop_slot_desc: { pt: 'Equipe até {n} armas por run', en: 'Equip up to {n} weapons per run' },

  // Shop passives
  shop_regen_name: { pt: 'Regeneração', en: 'Regeneration' },
  shop_regen_desc: { pt: 'Regenera 1 HP a cada 30s em todas as runs', en: 'Regenerate 1 HP every 30s in all runs' },
  shop_crit_name: { pt: 'Precisão Crítica', en: 'Critical Precision' },
  shop_crit_desc: { pt: '+5% de chance de crítico em todas as runs', en: '+5% crit chance in all runs' },
  shop_luck_name: { pt: 'Fortuna', en: 'Fortune' },
  shop_luck_desc: { pt: '+5% chance de drop de power-up', en: '+5% power-up drop chance' },
  shop_xp_name: { pt: 'Experiência+', en: 'Experience+' },
  shop_xp_desc: { pt: '+10% XP ganho em todas as runs', en: '+10% XP gained in all runs' },
  shop_dodge_name: { pt: 'Evasão Instintiva', en: 'Instinctive Evasion' },
  shop_dodge_desc: { pt: '+3% chance de esquivar dano', en: '+3% chance to dodge damage' },

  // Shop badges
  badge_base: { pt: 'BASE', en: 'BASE' },
  badge_nave: { pt: 'NAVE', en: 'SHIP' },
  badge_passiva: { pt: 'PASSIVA', en: 'PASSIVE' },
  badge_ice: { pt: 'GELO', en: 'ICE' },
  badge_missile: { pt: 'MÍSSIL', en: 'MISSILE' },
  badge_plasma: { pt: 'PLASMA', en: 'PLASMA' },
  badge_lightning: { pt: 'RAIO', en: 'LIGHTNING' },
  badge_fire: { pt: 'FOGO', en: 'FIRE' },
  badge_arc: { pt: 'ARC', en: 'ARC' },
  badge_slow: { pt: 'SLOW', en: 'SLOW' },
  badge_return: { pt: 'VOLTA', en: 'RETURN' },
  badge_power: { pt: 'PODER', en: 'POWER' },
  badge_acid: { pt: 'ÁCIDO', en: 'ACID' },
  badge_grav: { pt: 'GRAV', en: 'GRAV' },
  badge_tesla: { pt: 'TESLA', en: 'TESLA' },
  badge_void: { pt: 'VAZIO', en: 'VOID' },

  // ===== GAME OVER =====
  destroyed: { pt: 'DESTROYED', en: 'DESTROYED' },
  wave_label: { pt: 'Wave', en: 'Wave' },
  kills_label: { pt: 'Kills', en: 'Kills' },
  callsign: { pt: 'Callsign...', en: 'Callsign...' },
  save: { pt: 'Salvar', en: 'Save' },
  score_saved: { pt: '✅ Score saved!', en: '✅ Score saved!' },
  play_again: { pt: '🚀 Jogar Novamente', en: '🚀 Play Again' },
  menu: { pt: 'Menu', en: 'Menu' },
  unlocked_prefix: { pt: 'Desbloqueado:', en: 'Unlocked:' },

  // ===== LEVEL UP =====
  level_up: { pt: 'LEVEL UP! 🎉', en: 'LEVEL UP! 🎉' },
  level_label: { pt: 'Nível', en: 'Level' },
  weapons_slots: { pt: 'Armas', en: 'Weapons' },
  choose_ability: { pt: 'Escolha uma habilidade:', en: 'Choose an ability:' },
  weapon_tag: { pt: '🔫 ARMA', en: '🔫 WEAPON' },
  passive_tag: { pt: '⚙️ PASSIVA', en: '⚙️ PASSIVE' },
  new_tag: { pt: 'NOVO', en: 'NEW' },

  // ===== UPGRADE SCREEN =====
  wave_complete: { pt: 'Wave {n} Completa! 🎉', en: 'Wave {n} Complete! 🎉' },
  choose_upgrade: { pt: 'Escolha um upgrade:', en: 'Choose an upgrade:' },

  // ===== HUD =====
  this_wave: { pt: 'esta wave', en: 'this wave' },
  shared_score: { pt: 'PONTUAÇÃO COMPARTILHADA', en: 'SHARED SCORE' },
  ready: { pt: '⚡ READY', en: '⚡ READY' },
  dead: { pt: 'DEAD', en: 'DEAD' },

  // ===== MULTIPLAYER LOBBY =====
  mp_title: { pt: '🎮 Multiplayer Coop', en: '🎮 Multiplayer Coop' },
  mp_subtitle: { pt: 'Até 6 jogadores online!', en: 'Up to 6 players online!' },
  create_private: { pt: '🏠 Criar Sala Privada', en: '🏠 Create Private Room' },
  create_public: { pt: '🌐 Criar Sala Pública', en: '🌐 Create Public Room' },
  browse_rooms: { pt: '🔍 Buscar Salas Públicas', en: '🔍 Browse Public Rooms' },
  code_placeholder: { pt: 'CÓDIGO', en: 'CODE' },
  join: { pt: 'Entrar', en: 'Join' },
  refresh: { pt: '🔄 Atualizar', en: '🔄 Refresh' },
  rooms_found: { pt: 'sala(s) encontrada(s)', en: 'room(s) found' },
  loading_rooms: { pt: 'Carregando...', en: 'Loading...' },
  no_rooms: { pt: 'Nenhuma sala pública disponível. Crie uma!', en: 'No public rooms available. Create one!' },
  players: { pt: 'jogadores', en: 'players' },
  waiting_players: { pt: 'Aguardando jogadores... (máx 6)', en: 'Waiting for players... (max 6)' },
  connecting: { pt: 'Conectando...', en: 'Connecting...' },
  players_connected: { pt: 'jogadores conectados', en: 'players connected' },
  waiting_confirm: { pt: 'Aguardando confirmação dos jogadores...', en: 'Waiting for player confirmation...' },
  players_confirmed: { pt: 'Jogadores confirmaram! Iniciando...', en: 'Players confirmed! Starting...' },
  waiting_countdown: { pt: 'Aguardando contagem...', en: 'Waiting for countdown...' },
  preparing_battle: { pt: 'Preparando batalha...', en: 'Preparing battle...' },
  host_wants_start: { pt: '🚀 Host quer iniciar!', en: '🚀 Host wants to start!' },
  confirm: { pt: '✅ Confirmar', en: '✅ Confirm' },
  decline: { pt: '❌ Recusar', en: '❌ Decline' },
  public_room: { pt: '🌐 SALA PÚBLICA', en: '🌐 PUBLIC ROOM' },
  private_room: { pt: '🔒 SALA PRIVADA', en: '🔒 PRIVATE ROOM' },
  host_ship: { pt: '👑 HOST — SUA NAVE', en: '👑 HOST — YOUR SHIP' },
  your_ship: { pt: '🎮 SUA NAVE', en: '🎮 YOUR SHIP' },
  other_players: { pt: '🎮 OUTROS JOGADORES', en: '🎮 OTHER PLAYERS' },
  map_label: { pt: '🗺️ MAPA', en: '🗺️ MAP' },
  host_chooses: { pt: '(host escolhe)', en: '(host chooses)' },
  leave: { pt: 'Sair', en: 'Leave' },
  start_game: { pt: '🚀 Iniciar', en: '🚀 Start' },
  chat: { pt: '💬 CHAT', en: '💬 CHAT' },
  no_messages: { pt: 'Sem mensagens...', en: 'No messages...' },
  type_msg: { pt: 'Digite...', en: 'Type...' },
  quick_lets_go: { pt: 'Vamos!', en: "Let's go!" },
  quick_careful: { pt: 'Cuidado!', en: 'Watch out!' },
  quick_ready: { pt: 'Pronto!', en: 'Ready!' },

  // ===== ACHIEVEMENTS (names translated) =====
  ach_first_kill: { pt: 'Primeiro Abate', en: 'First Kill' },
  ach_beginner: { pt: 'Iniciante', en: 'Beginner' },
  ach_decent_score: { pt: 'Pontuação Decente', en: 'Decent Score' },
  ach_combo_beginner: { pt: 'Combo Iniciante', en: 'Combo Beginner' },
  ach_persistent: { pt: 'Persistente', en: 'Persistent' },
  ach_veteran: { pt: 'Veterano', en: 'Veteran' },
  ach_epic_score: { pt: 'Pontuação Épica', en: 'Epic Score' },
  ach_combo_killer: { pt: 'Combo Killer', en: 'Combo Killer' },
  ach_versatile: { pt: 'Piloto Versátil', en: 'Versatile Pilot' },
  ach_boss_hunter: { pt: 'Caça-Chefes', en: 'Boss Hunter' },
  ach_exterminator: { pt: 'Exterminador', en: 'Exterminator' },
} as const;

type TranslationKey = keyof typeof translations;

interface LanguageContextType {
  lang: Language;
  setLang: (lang: Language) => void;
  t: (key: TranslationKey, replacements?: Record<string, string | number>) => string;
}

const LanguageContext = createContext<LanguageContextType>({
  lang: 'pt',
  setLang: () => {},
  t: (key) => key,
});

export const LanguageProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [lang, setLangState] = useState<Language>(() => {
    const saved = localStorage.getItem('neon-wars-lang');
    return (saved === 'en' || saved === 'pt') ? saved : 'pt';
  });

  const setLang = useCallback((newLang: Language) => {
    setLangState(newLang);
    localStorage.setItem('neon-wars-lang', newLang);
  }, []);

  const t = useCallback((key: TranslationKey, replacements?: Record<string, string | number>): string => {
    const entry = translations[key];
    if (!entry) return key;
    let text = entry[lang] || entry['pt'] || key;
    if (replacements) {
      Object.entries(replacements).forEach(([k, v]) => {
        text = text.replace(`{${k}}`, String(v));
      });
    }
    return text;
  }, [lang]);

  return (
    <LanguageContext.Provider value={{ lang, setLang, t }}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = () => useContext(LanguageContext);
export { translations };
export type { TranslationKey };
