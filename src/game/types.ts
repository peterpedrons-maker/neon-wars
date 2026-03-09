// 🚀 Neon Wars - Game Types (Geometry Wars inspired)

// ShipType defined below with EnemyType
export type PlayerClass = ShipType; // backward compat alias
export type GameScreen = 'menu' | 'how-to-play' | 'class-select' | 'map-select' | 'playing' | 'upgrade' | 'game-over' | 'leaderboard' | 'shop' | 'multiplayer-lobby';
export type EnemyType = 'drone' | 'splitter' | 'dasher' | 'tank' | 'mothership' | 'vortex' | 'colossus' | 'fire_elemental' | 'void_ghost' | 'crystal_golem' | 'lava_dragon' | 'void_lord' | 'crystal_giant';
export type ShipType = 'phantom' | 'interceptor' | 'titan' | 'spectre' | 'valkyrie' | 'juggernaut';
export type PowerUpType = 'speed' | 'triple-shot' | 'shield' | 'heal';

export interface Vec2 {
  x: number;
  y: number;
}

export interface Entity {
  pos: Vec2;
  vel: Vec2;
  radius: number;
  alive: boolean;
}

export interface Player extends Entity {
  hp: number;
  maxHp: number;
  class: ShipType;
  damage: number;
  speed: number;
  attackCooldown: number;
  attackTimer: number;
  specialCooldown: number;
  specialTimer: number;
  shieldTimer: number;
  tripleTimer: number;
  speedBoostTimer: number;
  invincibleTimer: number;
  angle: number;
  emote?: { text: string; timer: number };
}

export interface Projectile extends Entity {
  damage: number;
  fromPlayer: boolean;
  lifetime: number;
  color: string;
  pierce?: number;   // remaining pierces
  ricochet?: number; // remaining ricochets
}

export interface Enemy extends Entity {
  type: EnemyType;
  hp: number;
  maxHp: number;
  damage: number;
  speed: number;
  baseSpeed?: number; // used for temporary slows (e.g. Frost Nova)
  slowUntil?: number; // epoch ms; if now < slowUntil enemy is slowed
  score: number;
  attackTimer: number;
  attackCooldown: number;
  isBoss: boolean;
  flashTimer: number;
  bossPhase?: number;
  bossAttackTimer?: number;
  dashState?: 'tracking' | 'dashing' | 'cooldown';
  dashTimer?: number;
  dashAngle?: number;
  shootTimer?: number;
}

export interface Particle {
  pos: Vec2;
  vel: Vec2;
  lifetime: number;
  maxLifetime: number;
  color: string;
  size: number;
}

export interface PowerUp extends Entity {
  type: PowerUpType;
  lifetime: number;
}

export interface Upgrade {
  id: string;
  name: string;
  description: string;
  icon: string;
  apply: (player: Player) => void;
}

export interface XpOrb {
  pos: Vec2;
  vel: Vec2;
  value: number;
  lifetime: number;
  radius: number;
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
  // Combo system
  combo: number;
  comboTimer: number;
  maxCombo: number;
  comboMultiplier: number;
  // XP / Level system
  xp: number;
  level: number;
  xpToNext: number;
  abilityLevels: Record<string, number>;
  abilities: import('./abilities').AbilityState;
  equippedWeapons: string[];
  weaponSlots: number;
  regenAccumulator: number;
  // Trail system
  trail: Array<{ x: number; y: number; age: number }>;
  // Map
  mapId: string;
  hazards: import('./maps').ActiveHazard[];
  hazardSpawnTimer: number;
  // Flame trail zones
  flameZones: Array<{ x: number; y: number; damage: number; lifetime: number }>;
  // Plasma field zones
  plasmaZones: Array<{ x: number; y: number; radius: number; damage: number; lifetime: number }>;
  // Coop peer info (optional, set in coop mode) - supports up to 3 peers
  coopPeers: Array<{
    pos: { x: number; y: number };
    angle: number;
    alive: boolean;
    dead: boolean; // true if they died
    shipClass: string;
    shooting: boolean;
    attackTimer: number;
    attackCooldown: number;
    damage: number;
    shieldTimer: number;
    invincibleTimer: number;
    hp: number;
    maxHp: number;
    playerId: string;
    playerLabel: string;
    reviveProgress: number; // 0-1 for revive progress
    emote?: { text: string; timer: number };
  }>;
  // Legacy single peer alias (computed from coopPeers[0])
  coopPeer?: {
    pos: { x: number; y: number };
    angle: number;
    alive: boolean;
    shipClass: string;
    shooting: boolean;
    attackTimer: number;
    attackCooldown: number;
    damage: number;
    shieldTimer: number;
    invincibleTimer: number;
    hp: number;
    maxHp: number;
    emote?: { text: string; timer: number };
  };
  isHost?: boolean;
  enemiesKilledThisWave: number;
  localPlayerId?: string; // ID of the local player (to filter out from peer rendering)
  coopMission?: {
    type: 'switches';
    switches: Array<{ x: number; y: number; active: boolean }>;
    completed: boolean;
  };
}

export interface LeaderboardEntry {
  name: string;
  score: number;
  wave: number;
  class: ShipType;
  date: string;
}

export interface InputState {
  moveX: number;
  moveY: number;
  aimX: number;
  aimY: number;
  shooting: boolean;
  special: boolean;
}
