// 🚀 Neon Wars - Game Types

export type PlayerClass = ShipType;
export type GameScreen = 'menu' | 'how-to-play' | 'class-select' | 'map-select' | 'playing' | 'upgrade' | 'game-over' | 'leaderboard' | 'shop' | 'multiplayer-lobby' | 'achievements';

export type EnemyType =
  // Base enemies
  | 'drone' | 'splitter' | 'dasher' | 'tank'
  // Map-specific regular enemies
  | 'fire_elemental' | 'void_ghost' | 'crystal_golem'
  | 'ice_walker' | 'nebula_shade' | 'acid_slime' | 'storm_drone'
  | 'undead_risen' | 'warp_drone' | 'prism_shard' | 'magma_wurm'
  | 'quantum_shifter' | 'abyss_horror'
  // Original bosses
  | 'mothership' | 'vortex' | 'colossus'
  // Map-specific bosses
  | 'lava_dragon' | 'void_lord' | 'crystal_giant'
  | 'frost_titan' | 'cosmic_horror' | 'plague_lord' | 'thunder_god'
  | 'lich_king' | 'nexus_guardian' | 'aurora_phoenix' | 'core_titan'
  | 'reality_breaker' | 'void_emperor'
  // Mega-bosses
  | 'archon' | 'oblivion'
  // Death wave
  | 'death_hunter';

export type ShipType =
  | 'phantom' | 'interceptor' | 'titan' | 'spectre' | 'valkyrie' | 'juggernaut'
  | 'wraith' | 'sentinel' | 'tempest' | 'venom' | 'nova_ship' | 'chronos'
  | 'leviathan' | 'raptor' | 'oracle' | 'pyro';

export type PowerUpType = 'speed' | 'triple-shot' | 'shield' | 'heal';

export interface Vec2 { x: number; y: number; }

export interface Entity {
  pos: Vec2; vel: Vec2; radius: number; alive: boolean;
}

export interface Player extends Entity {
  hp: number; maxHp: number; class: ShipType;
  damage: number; speed: number;
  attackCooldown: number; attackTimer: number;
  specialCooldown: number; specialTimer: number;
  shieldTimer: number; tripleTimer: number;
  speedBoostTimer: number; invincibleTimer: number;
  angle: number;
  emote?: { text: string; timer: number };
}

export interface Projectile extends Entity {
  damage: number; fromPlayer: boolean; lifetime: number; color: string;
  pierce?: number; ricochet?: number;
}

export interface Enemy extends Entity {
  type: EnemyType; hp: number; maxHp: number;
  damage: number; speed: number;
  baseSpeed?: number; slowUntil?: number;
  score: number; attackTimer: number; attackCooldown: number;
  isBoss: boolean; flashTimer: number;
  bossPhase?: number; bossAttackTimer?: number;
  dashState?: 'tracking' | 'dashing' | 'cooldown';
  dashTimer?: number; dashAngle?: number; shootTimer?: number;
  resurrectsLeft?: number; // for undead_risen
}

export interface Particle {
  pos: Vec2; vel: Vec2; lifetime: number; maxLifetime: number; color: string; size: number;
}

export interface PowerUp extends Entity {
  type: PowerUpType; lifetime: number;
}

export interface Upgrade {
  id: string; name: string; description: string; icon: string;
  apply: (player: Player) => void;
}

export interface XpOrb {
  pos: Vec2; vel: Vec2; value: number; lifetime: number; radius: number;
}

export interface GameState {
  player: Player;
  enemies: Enemy[];
  projectiles: Projectile[];
  particles: Particle[];
  powerUps: PowerUp[];
  xpOrbs: XpOrb[];
  wave: number;
  score: number;
  enemiesKilled: number;
  bossesKilled: number;
  screen: GameScreen;
  waveEnemiesRemaining: number;
  waveSpawnTimer: number;
  arenaWidth: number;
  arenaHeight: number;
  shakeTimer: number;
  shakeIntensity: number;
  deathWave: boolean;
  combo: number;
  comboTimer: number;
  maxCombo: number;
  comboMultiplier: number;
  xp: number;
  level: number;
  xpToNext: number;
  abilityLevels: Record<string, number>;
  abilities: import('./abilities').AbilityState;
  equippedWeapons: string[];
  weaponSlots: number;
  regenAccumulator: number;
  trail: Array<{ x: number; y: number; age: number }>;
  mapId: string;
  mapDifficulty: import('./maps').MapDifficulty;
  hazards: import('./maps').ActiveHazard[];
  hazardSpawnTimer: number;
  flameZones: Array<{ x: number; y: number; damage: number; lifetime: number }>;
  plasmaZones: Array<{ x: number; y: number; radius: number; damage: number; lifetime: number }>;
  coopPeers: Array<{
    pos: { x: number; y: number }; angle: number; alive: boolean; dead: boolean;
    shipClass: string; shooting: boolean; attackTimer: number; attackCooldown: number;
    damage: number; shieldTimer: number; invincibleTimer: number;
    hp: number; maxHp: number; playerId: string; playerLabel: string;
    reviveProgress: number; emote?: { text: string; timer: number };
  }>;
  coopPeer?: {
    pos: { x: number; y: number }; angle: number; alive: boolean; shipClass: string;
    shooting: boolean; attackTimer: number; attackCooldown: number; damage: number;
    shieldTimer: number; invincibleTimer: number; hp: number; maxHp: number;
    emote?: { text: string; timer: number };
  };
  isHost?: boolean;
  enemiesKilledThisWave: number;
  localPlayerId?: string;
  coopMission?: {
    type: 'switches';
    switches: Array<{ x: number; y: number; active: boolean }>;
    completed: boolean;
  };
}

export interface LeaderboardEntry {
  name: string; score: number; wave: number; class: ShipType; date: string;
}

export interface InputState {
  moveX: number; moveY: number; aimX: number; aimY: number;
  shooting: boolean; special: boolean;
}
