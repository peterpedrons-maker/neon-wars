import { PlayerClass, EnemyType } from './types';

export const ARENA_W = 2400;
export const ARENA_H = 1800;

// Camera zoom: how many "world pixels" the viewport shows
export const CAMERA_VIEW_W = 500;
export const CAMERA_VIEW_H = 380;
export const CAMERA_LERP = 0.08;

export const COLORS = {
  bg: '#0d0b1a',
  arena: '#1e1a2e',
  arenaBorder: '#4a3a6e',
  arenaBorderLight: '#7a5aaa',
  grid: 'rgba(100,70,180,0.12)',
  // Player classes - vivid!
  mage: '#a855f7',
  mageGlow: '#d8b4fe',
  archer: '#22d3ee',
  archerGlow: '#67e8f9',
  warrior: '#f97316',
  warriorGlow: '#fdba74',
  // Enemies - vivid
  skeleton: '#e2e8f0',
  slime: '#4ade80',
  bat: '#c084fc',
  darkKnight: '#475569',
  dragon: '#ef4444',
  lich: '#a855f7',
  golem: '#94a3b8',
  // UI
  gold: '#fbbf24',
  health: '#ef4444',
  healthBg: '#450a0a',
  shield: '#38bdf8',
  xp: '#a855f7',
  text: '#f1f5f9',
  textDim: '#94a3b8',
  // Power-ups - vivid
  speedPU: '#38bdf8',
  triplePU: '#f43f5e',
  shieldPU: '#34d399',
  healPU: '#fb7185',
  // Particles
  fire: '#ff6b35',
  ice: '#7dd3fc',
  magic: '#c4b5fd',
};

export const CLASS_STATS: Record<PlayerClass, { hp: number; damage: number; speed: number; attackCooldown: number; specialCooldown: number; radius: number }> = {
  mage: { hp: 80, damage: 15, speed: 200, attackCooldown: 0.3, specialCooldown: 5, radius: 16 },
  archer: { hp: 70, damage: 10, speed: 240, attackCooldown: 0.15, specialCooldown: 4, radius: 14 },
  warrior: { hp: 120, damage: 25, speed: 180, attackCooldown: 0.4, specialCooldown: 3, radius: 18 },
};

export const ENEMY_STATS: Record<EnemyType, { hp: number; damage: number; speed: number; score: number; radius: number; attackCooldown: number; isBoss: boolean }> = {
  skeleton: { hp: 20, damage: 10, speed: 80, score: 10, radius: 14, attackCooldown: 1, isBoss: false },
  slime: { hp: 15, damage: 5, speed: 50, score: 15, radius: 16, attackCooldown: 2, isBoss: false },
  bat: { hp: 10, damage: 8, speed: 160, score: 20, radius: 10, attackCooldown: 0.8, isBoss: false },
  'dark-knight': { hp: 60, damage: 20, speed: 40, score: 50, radius: 20, attackCooldown: 1.5, isBoss: false },
  dragon: { hp: 300, damage: 30, speed: 60, score: 500, radius: 40, attackCooldown: 2, isBoss: true },
  lich: { hp: 250, damage: 25, speed: 50, score: 500, radius: 35, attackCooldown: 1.5, isBoss: true },
  golem: { hp: 400, damage: 40, speed: 30, score: 500, radius: 45, attackCooldown: 3, isBoss: true },
};

export const WAVE_BASE_ENEMIES = 5;
export const WAVE_ENEMY_INCREMENT = 3;
export const BOSS_WAVE_INTERVAL = 5;
export const POWERUP_DROP_CHANCE = 0.15;
export const SPAWN_MARGIN = 50;
export const PROJECTILE_SPEED = 400;
export const PROJECTILE_LIFETIME = 2;
export const WARRIOR_ATTACK_RANGE = 70;
