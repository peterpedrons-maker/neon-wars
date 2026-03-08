import { ShipType, EnemyType } from './types';

export const ARENA_W = 1600;
export const ARENA_H = 1200;

// No walls - open neon grid arena, border is the edge
export const WALL_LEFT = 0;
export const WALL_RIGHT = ARENA_W;
export const WALL_TOP = 0;
export const WALL_BOTTOM = ARENA_H;

// Camera
export const CAMERA_VIEW_W = 500;
export const CAMERA_VIEW_H = 375;
export const CAMERA_LERP = 0.08;

// Neon color palette - Geometry Wars style
export const COLORS = {
  bg: '#000008',
  arena: '#040412',
  arenaBorder: '#0ff',
  arenaBorderLight: '#0ff',
  grid: 'rgba(0,255,255,0.06)',
  // Ship types - vivid neon
  phantom: '#bf5af2',    // purple
  phantomGlow: '#e0b0ff',
  interceptor: '#00e5ff', // cyan
  interceptorGlow: '#80f0ff',
  titan: '#ff6b00',       // orange
  titanGlow: '#ffaa55',
  // Keep backward compat
  mage: '#bf5af2',
  mageGlow: '#e0b0ff',
  archer: '#00e5ff',
  archerGlow: '#80f0ff',
  warrior: '#ff6b00',
  warriorGlow: '#ffaa55',
  // Enemies - neon geometric
  drone: '#39ff14',       // green
  splitter: '#ff1493',    // pink
  dasher: '#ffff00',      // yellow
  tank: '#ff4500',        // red-orange
  mothership: '#ff0040',  // red
  vortex: '#bf5af2',      // purple
  colossus: '#00bfff',    // blue
  // Legacy enemy color mappings
  skeleton: '#39ff14',
  slime: '#ff1493',
  bat: '#ffff00',
  darkKnight: '#ff4500',
  dragon: '#ff0040',
  lich: '#bf5af2',
  golem: '#00bfff',
  // UI
  gold: '#ffff00',
  health: '#ff0040',
  healthBg: '#1a0010',
  shield: '#00e5ff',
  xp: '#bf5af2',
  text: '#e0e8ff',
  textDim: '#6080aa',
  // Power-ups
  speedPU: '#00e5ff',
  triplePU: '#ff1493',
  shieldPU: '#39ff14',
  healPU: '#ff6090',
  // Particles
  fire: '#ff6b00',
  ice: '#00e5ff',
  magic: '#bf5af2',
  // New neon extras
  neonCyan: '#0ff',
  neonPink: '#ff1493',
  neonGreen: '#39ff14',
  neonYellow: '#ffff00',
  neonBlue: '#00bfff',
};

export type PlayerClass = ShipType;

export const CLASS_STATS: Record<ShipType, { hp: number; damage: number; speed: number; attackCooldown: number; specialCooldown: number; radius: number }> = {
  phantom: { hp: 80, damage: 15, speed: 130, attackCooldown: 0.38, specialCooldown: 5, radius: 12 },
  interceptor: { hp: 65, damage: 10, speed: 160, attackCooldown: 0.2, specialCooldown: 4, radius: 10 },
  titan: { hp: 130, damage: 28, speed: 95, attackCooldown: 0.6, specialCooldown: 3, radius: 15 },
};

export const ENEMY_STATS: Record<EnemyType, { hp: number; damage: number; speed: number; score: number; radius: number; attackCooldown: number; isBoss: boolean }> = {
  drone: { hp: 15, damage: 10, speed: 90, score: 10, radius: 10, attackCooldown: 1, isBoss: false },
  splitter: { hp: 20, damage: 5, speed: 60, score: 15, radius: 12, attackCooldown: 2, isBoss: false },
  dasher: { hp: 8, damage: 12, speed: 200, score: 25, radius: 8, attackCooldown: 0.6, isBoss: false },
  tank: { hp: 50, damage: 18, speed: 40, score: 50, radius: 16, attackCooldown: 1.5, isBoss: false },
  mothership: { hp: 300, damage: 25, speed: 50, score: 500, radius: 30, attackCooldown: 2, isBoss: true },
  vortex: { hp: 250, damage: 20, speed: 45, score: 500, radius: 28, attackCooldown: 1.5, isBoss: true },
  colossus: { hp: 400, damage: 35, speed: 30, score: 500, radius: 35, attackCooldown: 3, isBoss: true },
};

export const WAVE_BASE_ENEMIES = 12;
export const WAVE_ENEMY_INCREMENT = 6;
export const BOSS_WAVE_INTERVAL = 5;
export const POWERUP_DROP_CHANCE = 0.18;
export const SPAWN_MARGIN = 90;
export const PROJECTILE_SPEED = 500;
export const PROJECTILE_LIFETIME = 2;
export const WARRIOR_ATTACK_RANGE = 60;
