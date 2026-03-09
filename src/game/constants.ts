import { ShipType, EnemyType } from './types';

export const ARENA_W = 1600;
export const ARENA_H = 1200;
export const WALL_LEFT = 0;
export const WALL_RIGHT = ARENA_W;
export const WALL_TOP = 0;
export const WALL_BOTTOM = ARENA_H;
export const CAMERA_VIEW_W = 500;
export const CAMERA_VIEW_H = 375;
export const CAMERA_LERP = 0.08;

// Co-op arena scaling
export function getCoopArenaSize(playerCount: number): { w: number; h: number } {
  if (playerCount <= 2) return { w: 1600, h: 1200 };
  if (playerCount <= 4) return { w: 2000, h: 1500 };
  return { w: 2400, h: 1800 }; // 5-6 players
}

// Particle limits
export const MAX_PARTICLES_SOLO = 200;
export const MAX_PARTICLES_COOP = 80;

export const COLORS: Record<string, string> = {
  bg: '#000008', arena: '#040412', arenaBorder: '#0ff', arenaBorderLight: '#0ff',
  grid: 'rgba(0,255,255,0.06)',
  // Ships
  phantom: '#bf5af2', phantomGlow: '#e0b0ff',
  interceptor: '#00e5ff', interceptorGlow: '#80f0ff',
  titan: '#ff6b00', titanGlow: '#ffaa55',
  spectre: '#9040ff', spectreGlow: '#c090ff',
  valkyrie: '#ff1493', valkyrieGlow: '#ff80b0',
  juggernaut: '#ff4500', juggernautGlow: '#ff8040',
  wraith: '#00ff88', wraithGlow: '#80ffc0',
  sentinel: '#4488ff', sentinelGlow: '#88bbff',
  tempest: '#88ffff', tempestGlow: '#ccffff',
  venom: '#44ff00', venomGlow: '#88ff44',
  nova_ship: '#ff8800', nova_shipGlow: '#ffbb44',
  chronos: '#8888ff', chronosGlow: '#bbbbff',
  leviathan: '#ff2244', leviathanGlow: '#ff6688',
  raptor: '#ffff00', raptorGlow: '#ffff88',
  oracle: '#ff44ff', oracleGlow: '#ff88ff',
  pyro: '#ff4400', pyroGlow: '#ff8844',
  // Legacy compat
  mage: '#bf5af2', mageGlow: '#e0b0ff',
  archer: '#00e5ff', archerGlow: '#80f0ff',
  warrior: '#ff6b00', warriorGlow: '#ffaa55',
  // Base enemies
  drone: '#39ff14', splitter: '#ff1493', dasher: '#ffff00', tank: '#ff4500',
  // Map enemies
  fire_elemental: '#ff6b00', void_ghost: '#9040ff', crystal_golem: '#00e5ff',
  ice_walker: '#88ddff', nebula_shade: '#9966ff', acid_slime: '#88ff00',
  storm_drone: '#ffff44', undead_risen: '#668866', warp_drone: '#ff44ff',
  prism_shard: '#ff88ff', magma_wurm: '#ff4400', quantum_shifter: '#4488ff',
  abyss_horror: '#440088',
  // Bosses
  mothership: '#ff0040', vortex: '#bf5af2', colossus: '#00bfff',
  lava_dragon: '#ff2200', void_lord: '#6000c0', crystal_giant: '#00ffcc',
  frost_titan: '#44ccff', cosmic_horror: '#6600cc', plague_lord: '#66ff00',
  thunder_god: '#ffff00', lich_king: '#44ff88', nexus_guardian: '#ff00ff',
  aurora_phoenix: '#ff66aa', core_titan: '#ff6600', reality_breaker: '#0066ff',
  void_emperor: '#220044',
  // Mega/special
  archon: '#ffd700', oblivion: '#ff0000', death_hunter: '#ff0033',
  // UI
  gold: '#ffff00', health: '#ff0040', healthBg: '#1a0010', shield: '#00e5ff',
  xp: '#bf5af2', text: '#e0e8ff', textDim: '#6080aa',
  speedPU: '#00e5ff', triplePU: '#ff1493', shieldPU: '#39ff14', healPU: '#ff6090',
  fire: '#ff6b00', ice: '#00e5ff', magic: '#bf5af2',
  neonCyan: '#0ff', neonPink: '#ff1493', neonGreen: '#39ff14',
  neonYellow: '#ffff00', neonBlue: '#00bfff',
};

export type PlayerClass = ShipType;

export const CLASS_STATS: Record<ShipType, { hp: number; damage: number; speed: number; attackCooldown: number; specialCooldown: number; radius: number }> = {
  // ─── Tier 1: Starter ships ───────────────────────────────────────────────────
  // Phantom: balanced DPS, stealth nova special. Good all-rounder.
  phantom:     { hp: 3, damage: 16, speed: 135, attackCooldown: 0.35, specialCooldown: 5,   radius: 12 },
  // Interceptor: low dmg per shot but blazing fire rate + lock-on special.
  interceptor: { hp: 3, damage: 11, speed: 165, attackCooldown: 0.18, specialCooldown: 3.5, radius: 10 },
  // Titan: melee tank — high base damage, melee range, shockwave special.
  titan:       { hp: 4, damage: 32, speed: 100, attackCooldown: 0.55, specialCooldown: 3,   radius: 15 },
  // Spectre: glass cannon — blink + ghost explosion. High burst.
  spectre:     { hp: 2, damage: 22, speed: 155, attackCooldown: 0.28, specialCooldown: 3.5, radius: 11 },
  // Valkyrie: twin guns, wide spread; lances special.
  valkyrie:    { hp: 4, damage: 13, speed: 140, attackCooldown: 0.22, specialCooldown: 3.5, radius: 11 },
  // ─── Tier 2: Advanced ships ──────────────────────────────────────────────────
  // Juggernaut: armored bruiser — melee AoE. Tanky and devastating up close.
  juggernaut:  { hp: 6, damage: 38, speed: 80,  attackCooldown: 0.75, specialCooldown: 5.5, radius: 17 },
  // Wraith: assassin — fast, phase-shift special, shadow clones.
  wraith:      { hp: 2, damage: 20, speed: 150, attackCooldown: 0.32, specialCooldown: 3.5, radius: 10 },
  // Sentinel: defensive fortress — shield burst, barrier deploy special.
  sentinel:    { hp: 5, damage: 24, speed: 85,  attackCooldown: 0.42, specialCooldown: 4.5, radius: 14 },
  // Tempest: storm craft — fast with tornado pull/blast special.
  tempest:     { hp: 3, damage: 15, speed: 158, attackCooldown: 0.26, specialCooldown: 3,   radius: 11 },
  // Venom: poison specialist — lingering projectiles + toxic cloud.
  venom:       { hp: 3, damage: 18, speed: 122, attackCooldown: 0.38, specialCooldown: 4,   radius: 11 },
  // ─── Tier 3: Elite ships ─────────────────────────────────────────────────────
  // Nova: slow heavy shots + supernova AoE. Big damage, slow fire.
  nova_ship:   { hp: 3, damage: 32, speed: 112, attackCooldown: 0.52, specialCooldown: 4.5, radius: 13 },
  // Chronos: time mage — time freeze special, balanced stats.
  chronos:     { hp: 3, damage: 15, speed: 128, attackCooldown: 0.30, specialCooldown: 5.5, radius: 11 },
  // Leviathan: mega-tank — 8 hp, devour special that heals on kill.
  leviathan:   { hp: 8, damage: 45, speed: 60,  attackCooldown: 0.95, specialCooldown: 6.5, radius: 20 },
  // Raptor: hyper-speed micro-fighter — wall-of-bullets blitz dash.
  raptor:      { hp: 2, damage: 13, speed: 210, attackCooldown: 0.13, specialCooldown: 2.5, radius: 9  },
  // Oracle: mystic — aims at nearest enemy automatically; marks all enemies.
  oracle:      { hp: 3, damage: 14, speed: 132, attackCooldown: 0.33, specialCooldown: 3.5, radius: 11 },
  // Pyro: flamethrower — wide spread, low lifetime; inferno ring special.
  pyro:        { hp: 3, damage: 21, speed: 118, attackCooldown: 0.38, specialCooldown: 4,   radius: 12 },
};

// Enemy stat helper - creates compact definitions
function es(hp: number, dmg: number, spd: number, score: number, r: number, cd: number, boss: boolean) {
  return { hp, damage: dmg, speed: spd, score, radius: r, attackCooldown: cd, isBoss: boss };
}

export const ENEMY_STATS: Record<EnemyType, { hp: number; damage: number; speed: number; score: number; radius: number; attackCooldown: number; isBoss: boolean }> = {
  // Base
  drone:           es(15,  10,  90,  10,  10, 1,   false),
  splitter:        es(20,  5,   60,  15,  12, 2,   false),
  dasher:          es(8,   12,  130, 25,  8,  0.6, false),
  tank:            es(50,  18,  40,  50,  16, 1.5, false),
  // Map regular enemies
  fire_elemental:  es(30,  15,  70,  35,  13, 1.2, false),
  void_ghost:      es(18,  20,  110, 40,  10, 0.8, false),
  crystal_golem:   es(60,  12,  35,  45,  18, 2,   false),
  ice_walker:      es(25,  12,  55,  30,  12, 1.5, false),
  nebula_shade:    es(20,  18,  100, 40,  10, 0.9, false),
  acid_slime:      es(35,  10,  50,  30,  14, 2,   false),
  storm_drone:     es(15,  14,  140, 35,  9,  0.5, false),
  undead_risen:    es(22,  15,  70,  30,  11, 1.2, false),
  warp_drone:      es(16,  16,  120, 35,  9,  0.7, false),
  prism_shard:     es(40,  8,   45,  35,  13, 1.8, false),
  magma_wurm:      es(45,  20,  60,  45,  15, 1.3, false),
  quantum_shifter: es(18,  22,  130, 50,  10, 0.6, false),
  abyss_horror:    es(55,  25,  50,  60,  16, 1.5, false),
  // Original bosses
  mothership:      es(300,  25, 50,  500,  30, 2,   true),
  vortex:          es(250,  20, 45,  500,  28, 1.5, true),
  colossus:        es(400,  35, 30,  500,  35, 3,   true),
  // Map bosses
  lava_dragon:     es(500,  30, 45,  800,  35, 2,   true),
  void_lord:       es(400,  35, 40,  800,  32, 1.8, true),
  crystal_giant:   es(600,  25, 25,  800,  40, 2.5, true),
  frost_titan:     es(450,  28, 35,  800,  36, 2.2, true),
  cosmic_horror:   es(550,  32, 30,  900,  38, 2,   true),
  plague_lord:     es(480,  22, 40,  850,  34, 1.8, true),
  thunder_god:     es(500,  35, 50,  900,  32, 1.5, true),
  lich_king:       es(520,  30, 35,  900,  35, 2,   true),
  nexus_guardian:  es(600,  28, 25,  950,  40, 2.5, true),
  aurora_phoenix:  es(480,  25, 55,  900,  30, 1.5, true),
  core_titan:      es(700,  40, 20,  1000, 45, 3,   true),
  reality_breaker: es(650,  38, 35,  1000, 38, 2,   true),
  void_emperor:    es(800,  45, 30,  1200, 42, 2,   true),
  // Mega-bosses
  archon:          es(2500, 50, 35,  3000, 50, 1.5, true),
  oblivion:        es(5000, 70, 40,  8000, 55, 1.2, true),
  // Death wave
  death_hunter:    es(80,   40, 200, 100,  11, 0.4, false),
};

export const WAVE_BASE_ENEMIES = 20;
export const WAVE_ENEMY_INCREMENT = 10;
export const BOSS_WAVE_INTERVAL = 5;
export const POWERUP_DROP_CHANCE = 0.06;
export const SPAWN_MARGIN = 90;
export const PROJECTILE_SPEED = 500;
export const PROJECTILE_LIFETIME = 2;
export const WARRIOR_ATTACK_RANGE = 60;
