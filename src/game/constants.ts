import { PlayerClass, EnemyType } from './types';

export const ARENA_W = 1200;
export const ARENA_H = 800;

export const COLORS = {
  bg: '#1a0e0a',
  arena: '#2a1810',
  arenaBorder: '#5a3a28',
  arenaBorderLight: '#8a6a50',
  grid: 'rgba(90,58,40,0.15)',
  // Player classes
  mage: '#9b59b6',
  mageGlow: '#c39bd3',
  archer: '#27ae60',
  archerGlow: '#58d68d',
  warrior: '#e67e22',
  warriorGlow: '#f0b27a',
  // Enemies
  skeleton: '#d5d5c8',
  slime: '#2ecc71',
  bat: '#8e44ad',
  darkKnight: '#2c3e50',
  dragon: '#e74c3c',
  lich: '#6c3483',
  golem: '#7f8c8d',
  // UI
  gold: '#f1c40f',
  health: '#e74c3c',
  healthBg: '#4a1a1a',
  shield: '#3498db',
  xp: '#9b59b6',
  text: '#f5e6d3',
  textDim: '#8a7a6a',
  // Power-ups
  speedPU: '#3498db',
  triplePU: '#e74c3c',
  shieldPU: '#2ecc71',
  healPU: '#e91e63',
  // Particles
  fire: '#ff6b35',
  ice: '#74b9ff',
  magic: '#a29bfe',
};

export const CLASS_STATS: Record<PlayerClass, { hp: number; damage: number; speed: number; attackCooldown: number; specialCooldown: number; radius: number }> = {
  mage: { hp: 80, damage: 15, speed: 200, attackCooldown: 0.3, specialCooldown: 5, radius: 14 },
  archer: { hp: 70, damage: 10, speed: 240, attackCooldown: 0.15, specialCooldown: 4, radius: 12 },
  warrior: { hp: 120, damage: 25, speed: 180, attackCooldown: 0.4, specialCooldown: 3, radius: 16 },
};

export const ENEMY_STATS: Record<EnemyType, { hp: number; damage: number; speed: number; score: number; radius: number; attackCooldown: number; isBoss: boolean }> = {
  skeleton: { hp: 20, damage: 10, speed: 80, score: 10, radius: 12, attackCooldown: 1, isBoss: false },
  slime: { hp: 15, damage: 5, speed: 50, score: 15, radius: 14, attackCooldown: 2, isBoss: false },
  bat: { hp: 10, damage: 8, speed: 160, score: 20, radius: 8, attackCooldown: 0.8, isBoss: false },
  'dark-knight': { hp: 60, damage: 20, speed: 40, score: 50, radius: 18, attackCooldown: 1.5, isBoss: false },
  dragon: { hp: 300, damage: 30, speed: 60, score: 500, radius: 35, attackCooldown: 2, isBoss: true },
  lich: { hp: 250, damage: 25, speed: 50, score: 500, radius: 30, attackCooldown: 1.5, isBoss: true },
  golem: { hp: 400, damage: 40, speed: 30, score: 500, radius: 40, attackCooldown: 3, isBoss: true },
};

export const WAVE_BASE_ENEMIES = 5;
export const WAVE_ENEMY_INCREMENT = 3;
export const BOSS_WAVE_INTERVAL = 5;
export const POWERUP_DROP_CHANCE = 0.15;
export const SPAWN_MARGIN = 50;
export const PROJECTILE_SPEED = 400;
export const PROJECTILE_LIFETIME = 2;
export const WARRIOR_ATTACK_RANGE = 60;
