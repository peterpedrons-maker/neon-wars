import { Player, GameState, Enemy, Projectile } from './types';
import { COLORS, PROJECTILE_SPEED } from './constants';
import { createParticles, dist } from './entities';

export interface Ability {
  id: string;
  name: string;
  description: string;
  icon: string;
  maxLevel: number;
  apply: (state: GameState) => void;
}

// Passive ability state tracked on GameState
export interface AbilityState {
  orbitals: number;        // number of orbital shields
  auraRadius: number;      // damage aura radius (0 = off)
  auraDamage: number;      // dps of aura
  magnetRadius: number;    // XP magnet range
  homingChance: number;    // % chance projectile homes
  chainCount: number;      // chain lightning bounces
  regenRate: number;       // hp regen per second (accumulates)
  critChance: number;      // % chance for 2x damage
  projectileCount: number; // extra projectiles per shot
  explosionRadius: number; // projectiles explode on hit
}

export function createAbilityState(): AbilityState {
  return {
    orbitals: 0,
    auraRadius: 0,
    auraDamage: 0,
    magnetRadius: 60,
    homingChance: 0,
    chainCount: 0,
    regenRate: 0,
    critChance: 0,
    projectileCount: 0,
    explosionRadius: 0,
  };
}

const ALL_ABILITIES: Ability[] = [
  {
    id: 'orbitals',
    name: 'Orbital Drones',
    description: '+1 drone orbital que causa dano ao contato',
    icon: '🛸',
    maxLevel: 5,
    apply: (state) => { state.abilities.orbitals++; },
  },
  {
    id: 'aura',
    name: 'Neon Aura',
    description: 'Aura de dano ao redor da nave',
    icon: '🔮',
    maxLevel: 5,
    apply: (state) => {
      state.abilities.auraRadius += 30;
      state.abilities.auraDamage += 8;
    },
  },
  {
    id: 'magnet',
    name: 'XP Magnet',
    description: 'Aumenta o alcance de coleta de XP',
    icon: '🧲',
    maxLevel: 5,
    apply: (state) => { state.abilities.magnetRadius += 40; },
  },
  {
    id: 'homing',
    name: 'Auto-Mira',
    description: 'Chance de projéteis perseguirem inimigos',
    icon: '🎯',
    maxLevel: 5,
    apply: (state) => { state.abilities.homingChance += 0.15; },
  },
  {
    id: 'chain',
    name: 'Raio Cadeia',
    description: 'Eliminar inimigo causa dano em cadeia',
    icon: '⚡',
    maxLevel: 5,
    apply: (state) => { state.abilities.chainCount++; },
  },
  {
    id: 'regen',
    name: 'Nano-Reparo',
    description: 'Regenera HP lentamente',
    icon: '💚',
    maxLevel: 3,
    apply: (state) => { state.abilities.regenRate += 0.08; },
  },
  {
    id: 'crit',
    name: 'Overcharge',
    description: 'Chance de dano crítico (2x)',
    icon: '💥',
    maxLevel: 5,
    apply: (state) => { state.abilities.critChance += 0.12; },
  },
  {
    id: 'multishot',
    name: 'Multi-Tiro',
    description: '+1 projétil por disparo',
    icon: '🔱',
    maxLevel: 3,
    apply: (state) => { state.abilities.projectileCount++; },
  },
  {
    id: 'explosion',
    name: 'Projétil Explosivo',
    description: 'Projéteis explodem ao acertar',
    icon: '💣',
    maxLevel: 4,
    apply: (state) => { state.abilities.explosionRadius += 25; },
  },
  {
    id: 'damage_up',
    name: 'Canhão Turbo',
    description: '+20% de dano base',
    icon: '🔥',
    maxLevel: 10,
    apply: (state) => { state.player.damage = Math.floor(state.player.damage * 1.2); },
  },
  {
    id: 'speed_up',
    name: 'Propulsor',
    description: '+10% velocidade',
    icon: '🚀',
    maxLevel: 5,
    apply: (state) => { state.player.speed *= 1.1; },
  },
  {
    id: 'fire_rate',
    name: 'Cadência',
    description: '-15% cooldown de tiro',
    icon: '⏩',
    maxLevel: 5,
    apply: (state) => { state.player.attackCooldown *= 0.85; },
  },
];

export function getRandomAbilities(count: number, currentLevels: Record<string, number>): Ability[] {
  // Filter out maxed abilities
  const available = ALL_ABILITIES.filter(a => (currentLevels[a.id] || 0) < a.maxLevel);
  const shuffled = [...available].sort(() => Math.random() - 0.5);
  return shuffled.slice(0, count);
}

// XP required for each level
export function xpForLevel(level: number): number {
  return Math.floor(20 + level * 15 + level * level * 2);
}

// Update orbital drones
export function updateOrbitals(state: GameState, dt: number) {
  if (state.abilities.orbitals <= 0) return;
  const p = state.player;
  const count = state.abilities.orbitals;
  const orbitalDamage = 15 + state.wave * 2;
  const orbitalRadius = p.radius + 30;

  for (let i = 0; i < count; i++) {
    const angle = (Date.now() * 0.003) + (i / count) * Math.PI * 2;
    const ox = p.pos.x + Math.cos(angle) * orbitalRadius;
    const oy = p.pos.y + Math.sin(angle) * orbitalRadius;

    for (const e of state.enemies) {
      if (!e.alive) continue;
      const d = Math.hypot(e.pos.x - ox, e.pos.y - oy);
      if (d < e.radius + 8) {
        e.hp -= orbitalDamage * dt;
        e.flashTimer = 0.05;
        if (Math.random() < 0.1) {
          state.particles.push(...createParticles({ x: ox, y: oy }, COLORS.neonCyan, 3, 80, 2));
        }
      }
    }
  }
}

// Update damage aura
export function updateAura(state: GameState, dt: number) {
  if (state.abilities.auraRadius <= 0) return;
  const p = state.player;
  for (const e of state.enemies) {
    if (!e.alive) continue;
    const d = dist(e.pos, p.pos);
    if (d < state.abilities.auraRadius + e.radius) {
      e.hp -= state.abilities.auraDamage * dt;
      e.flashTimer = 0.03;
    }
  }
}

// Update regen
export function updateRegen(state: GameState, dt: number) {
  if (state.abilities.regenRate <= 0) return;
  state.regenAccumulator = (state.regenAccumulator || 0) + state.abilities.regenRate * dt;
  if (state.regenAccumulator >= 1) {
    state.regenAccumulator -= 1;
    state.player.hp = Math.min(state.player.maxHp, state.player.hp + 1);
  }
}

// Chain lightning on enemy death
export function triggerChainLightning(state: GameState, origin: { x: number; y: number }, bounces: number, damage: number) {
  if (bounces <= 0) return;
  let closest: Enemy | null = null;
  let closestDist = 200; // max chain range
  for (const e of state.enemies) {
    if (!e.alive) continue;
    const d = Math.hypot(e.pos.x - origin.x, e.pos.y - origin.y);
    if (d < closestDist) {
      closestDist = d;
      closest = e;
    }
  }
  if (closest) {
    closest.hp -= damage;
    closest.flashTimer = 0.1;
    state.particles.push(...createParticles(closest.pos, COLORS.neonCyan, 8, 100, 2));
    // Visual chain line stored as particles along the path
    const steps = 5;
    for (let i = 0; i < steps; i++) {
      const t = i / steps;
      state.particles.push({
        pos: { x: origin.x + (closest.pos.x - origin.x) * t, y: origin.y + (closest.pos.y - origin.y) * t },
        vel: { x: (Math.random() - 0.5) * 30, y: (Math.random() - 0.5) * 30 },
        lifetime: 0.2,
        maxLifetime: 0.2,
        color: COLORS.neonCyan,
        size: 2,
      });
    }
    if (closest.hp <= 0) {
      // Will be handled by normal death logic, but chain continues
      triggerChainLightning(state, closest.pos, bounces - 1, damage * 0.8);
    } else {
      triggerChainLightning(state, closest.pos, bounces - 1, damage * 0.8);
    }
  }
}
