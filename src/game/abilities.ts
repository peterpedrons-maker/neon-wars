import { Player, GameState, Enemy, Projectile } from './types';
import { COLORS, PROJECTILE_SPEED } from './constants';
import { createParticles, dist } from './entities';

export type AbilityCategory = 'weapon' | 'passive';

export interface Ability {
  id: string;
  name: string;
  description: string;
  icon: string;
  maxLevel: number;
  category: AbilityCategory;
  apply: (state: GameState) => void;
  requiresUnlock?: boolean; // needs milestone to appear
}

// Passive ability state tracked on GameState
export interface AbilityState {
  orbitals: number;
  auraRadius: number;
  auraDamage: number;
  magnetRadius: number;
  homingChance: number;
  chainCount: number;
  regenRate: number;
  critChance: number;
  projectileCount: number;
  explosionRadius: number;
  // Projectile modifiers (new weapons)
  pierce: number;
  ricochet: number;
  // Timed weapons
  ionBeamDamage: number;
  ionBeamLength: number;
  ionBeamCooldown: number;
  ionBeamTimer: number;
  shockwaveRadius: number;
  shockwaveDamage: number;
  shockwaveCooldown: number;
  shockwaveTimer: number;
  sentryCount: number;
  sentryDamage: number;
  sentryCooldown: number;
  sentryTimer: number;
  // Existing weapon states
  frostNovaRadius: number;
  frostNovaCooldown: number;
  frostNovaTimer: number;
  missileTimer: number;
  missileCooldown: number;
  missileCount: number;
  plasmaFieldRadius: number;
  plasmaFieldDamage: number;
  plasmaFieldTimer: number;
  lightningRingRadius: number;
  lightningRingDamage: number;
  lightningRingTimer: number;
  flameTrailDamage: number;
  // Passive states
  vampirism: number;
  dodge: number;
  xpBonus: number;
  armor: number;
  luck: number;
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
    pierce: 0,
    ricochet: 0,
    ionBeamDamage: 0,
    ionBeamLength: 420,
    ionBeamCooldown: 3.5,
    ionBeamTimer: 0,
    shockwaveRadius: 0,
    shockwaveDamage: 0,
    shockwaveCooldown: 4.0,
    shockwaveTimer: 0,
    sentryCount: 0,
    sentryDamage: 0,
    sentryCooldown: 1.4,
    sentryTimer: 0,
    frostNovaRadius: 0,
    frostNovaCooldown: 5,
    frostNovaTimer: 0,
    missileTimer: 0,
    missileCooldown: 3,
    missileCount: 0,
    plasmaFieldRadius: 0,
    plasmaFieldDamage: 0,
    plasmaFieldTimer: 0,
    lightningRingRadius: 0,
    lightningRingDamage: 0,
    lightningRingTimer: 0,
    flameTrailDamage: 0,
    vampirism: 0,
    dodge: 0,
    xpBonus: 0,
    armor: 0,
    luck: 0,
  };
}

// ===== WEAPONS (consume weapon slots) =====
const WEAPON_ABILITIES: Ability[] = [
  {
    id: 'orbitals',
    name: 'Orbital Drones',
    description: '+1 drone orbital que causa dano ao contato',
    icon: '🛸',
    maxLevel: 5,
    category: 'weapon',
    apply: (state) => { state.abilities.orbitals++; },
  },
  {
    id: 'aura',
    name: 'Neon Aura',
    description: 'Aura de dano ao redor da nave',
    icon: '🔮',
    maxLevel: 5,
    category: 'weapon',
    apply: (state) => {
      state.abilities.auraRadius += 30;
      state.abilities.auraDamage += 8;
    },
  },
  {
    id: 'chain',
    name: 'Raio Cadeia',
    description: 'Eliminar inimigo causa dano em cadeia',
    icon: '⚡',
    maxLevel: 5,
    category: 'weapon',
    apply: (state) => { state.abilities.chainCount++; },
  },
  {
    id: 'multishot',
    name: 'Multi-Tiro',
    description: '+1 projétil por disparo',
    icon: '🔱',
    maxLevel: 3,
    category: 'weapon',
    apply: (state) => { state.abilities.projectileCount++; },
  },
  {
    id: 'explosion',
    name: 'Projétil Explosivo',
    description: 'Projéteis explodem ao acertar',
    icon: '💣',
    maxLevel: 4,
    category: 'weapon',
    apply: (state) => { state.abilities.explosionRadius += 25; },
  },
  {
    id: 'homing',
    name: 'Auto-Mira',
    description: 'Chance de projéteis perseguirem inimigos',
    icon: '🎯',
    maxLevel: 5,
    category: 'weapon',
    apply: (state) => { state.abilities.homingChance += 0.15; },
  },
  {
    id: 'piercing_rounds',
    name: 'Balas Perfurantes',
    description: 'Projéteis atravessam inimigos (+1 perfuração)',
    icon: '🧿',
    maxLevel: 4,
    category: 'weapon',
    apply: (state) => { state.abilities.pierce += 1; },
  },
  {
    id: 'ricochet_rounds',
    name: 'Ricochete',
    description: 'Projéteis ricocheteiam em outro alvo (+1 ricochete)',
    icon: '🪩',
    maxLevel: 4,
    category: 'weapon',
    apply: (state) => { state.abilities.ricochet += 1; },
  },
  {
    id: 'ion_beam',
    name: 'Ion Beam',
    description: 'Feixe periódico na direção da mira',
    icon: '📡',
    maxLevel: 5,
    category: 'weapon',
    apply: (state) => {
      state.abilities.ionBeamDamage += 20;
      state.abilities.ionBeamLength += 60;
      state.abilities.ionBeamCooldown = Math.max(1.2, state.abilities.ionBeamCooldown - 0.35);
    },
  },
  {
    id: 'shockwave_emitter',
    name: 'Shockwave',
    description: 'Explosão periódica ao redor da nave',
    icon: '💫',
    maxLevel: 5,
    category: 'weapon',
    apply: (state) => {
      state.abilities.shockwaveRadius += 45;
      state.abilities.shockwaveDamage += 14;
      state.abilities.shockwaveCooldown = Math.max(1.5, state.abilities.shockwaveCooldown - 0.35);
    },
  },
  {
    id: 'sentry_drones',
    name: 'Sentry Drones',
    description: 'Drones automáticos disparam nos inimigos',
    icon: '🤖',
    maxLevel: 5,
    category: 'weapon',
    apply: (state) => {
      state.abilities.sentryCount += 1;
      state.abilities.sentryDamage += 6;
      state.abilities.sentryCooldown = Math.max(0.5, state.abilities.sentryCooldown - 0.12);
    },
  },
  // === NEW WEAPONS (unlockable) ===
  {
    id: 'frost_nova',
    name: 'Frost Nova',
    description: 'Explosão periódica que congela inimigos próximos',
    icon: '❄️',
    maxLevel: 5,
    category: 'weapon',
    requiresUnlock: true,
    apply: (state) => {
      state.abilities.frostNovaRadius += 40;
      state.abilities.frostNovaCooldown = Math.max(2, state.abilities.frostNovaCooldown - 0.5);
    },
  },
  {
    id: 'missile_barrage',
    name: 'Missile Barrage',
    description: 'Dispara mísseis teleguiados automaticamente',
    icon: '🚀',
    maxLevel: 5,
    category: 'weapon',
    requiresUnlock: true,
    apply: (state) => {
      state.abilities.missileCount += 2;
      state.abilities.missileCooldown = Math.max(1, state.abilities.missileCooldown - 0.3);
    },
  },
  {
    id: 'plasma_field',
    name: 'Plasma Field',
    description: 'Deixa zonas de plasma no chão que causam dano',
    icon: '🟣',
    maxLevel: 4,
    category: 'weapon',
    requiresUnlock: true,
    apply: (state) => {
      state.abilities.plasmaFieldRadius += 20;
      state.abilities.plasmaFieldDamage += 12;
    },
  },
  {
    id: 'lightning_ring',
    name: 'Lightning Ring',
    description: 'Raios automáticos atingem inimigos próximos',
    icon: '⚡',
    maxLevel: 5,
    category: 'weapon',
    requiresUnlock: true,
    apply: (state) => {
      state.abilities.lightningRingRadius += 30;
      state.abilities.lightningRingDamage += 15;
    },
  },
  {
    id: 'flame_trail',
    name: 'Flame Trail',
    description: 'Deixa rastro de fogo ao se mover',
    icon: '🔥',
    maxLevel: 4,
    category: 'weapon',
    requiresUnlock: true,
    apply: (state) => {
      state.abilities.flameTrailDamage += 10;
    },
  },
];

// ===== PASSIVES (unlimited) =====
const PASSIVE_ABILITIES: Ability[] = [
  {
    id: 'magnet',
    name: 'XP Magnet',
    description: 'Aumenta o alcance de coleta de XP',
    icon: '🧲',
    maxLevel: 5,
    category: 'passive',
    apply: (state) => { state.abilities.magnetRadius += 40; },
  },
  {
    id: 'regen',
    name: 'Nano-Reparo',
    description: 'Regenera HP lentamente',
    icon: '💚',
    maxLevel: 3,
    category: 'passive',
    apply: (state) => { state.abilities.regenRate += 0.08; },
  },
  {
    id: 'crit',
    name: 'Overcharge',
    description: 'Chance de dano crítico (2x)',
    icon: '💥',
    maxLevel: 5,
    category: 'passive',
    apply: (state) => { state.abilities.critChance += 0.12; },
  },
  {
    id: 'damage_up',
    name: 'Canhão Turbo',
    description: '+20% de dano base',
    icon: '🔥',
    maxLevel: 10,
    category: 'passive',
    apply: (state) => { state.player.damage = Math.floor(state.player.damage * 1.2); },
  },
  {
    id: 'speed_up',
    name: 'Propulsor',
    description: '+10% velocidade',
    icon: '🏃',
    maxLevel: 5,
    category: 'passive',
    apply: (state) => { state.player.speed *= 1.1; },
  },
  {
    id: 'fire_rate',
    name: 'Cadência',
    description: '-15% cooldown de tiro',
    icon: '⏩',
    maxLevel: 5,
    category: 'passive',
    apply: (state) => { state.player.attackCooldown *= 0.85; },
  },
  {
    id: 'vampirism',
    name: 'Vampirismo',
    description: 'Chance de curar ao eliminar inimigos',
    icon: '🧛',
    maxLevel: 3,
    category: 'passive',
    apply: (state) => { state.abilities.vampirism += 0.15; },
  },
  {
    id: 'dodge',
    name: 'Evasão',
    description: 'Chance de esquivar dano',
    icon: '💨',
    maxLevel: 4,
    category: 'passive',
    apply: (state) => { state.abilities.dodge += 0.08; },
  },
  {
    id: 'xp_bonus',
    name: 'XP Boost',
    description: '+15% XP ganho',
    icon: '📈',
    maxLevel: 5,
    category: 'passive',
    apply: (state) => { state.abilities.xpBonus += 0.15; },
  },
  {
    id: 'armor',
    name: 'Blindagem',
    description: 'Reduz dano recebido (menos knockback)',
    icon: '🛡️',
    maxLevel: 3,
    category: 'passive',
    apply: (state) => { state.abilities.armor += 0.15; },
  },
  {
    id: 'luck',
    name: 'Sorte',
    description: 'Mais drops e chances melhores',
    icon: '🍀',
    maxLevel: 3,
    category: 'passive',
    apply: (state) => { state.abilities.luck += 0.1; },
  },
];

export const ALL_ABILITIES: Ability[] = [...WEAPON_ABILITIES, ...PASSIVE_ABILITIES];

export function getRandomAbilities(
  count: number,
  currentLevels: Record<string, number>,
  weaponSlots: number,
  equippedWeapons: string[],
  unlockedAbilities: string[],
): Ability[] {
  const equippedWeaponCount = equippedWeapons.length;
  const weaponsFull = equippedWeaponCount >= weaponSlots;

  const available = ALL_ABILITIES.filter(a => {
    // Skip maxed
    if ((currentLevels[a.id] || 0) >= a.maxLevel) return false;
    // Skip locked abilities
    if (a.requiresUnlock && !unlockedAbilities.includes(a.id)) return false;
    // If weapon slots full, only show already-equipped weapons or passives
    if (a.category === 'weapon' && weaponsFull && !equippedWeapons.includes(a.id)) return false;
    return true;
  });

  const shuffled = [...available].sort(() => Math.random() - 0.5);
  // Ensure mix: try to have at least 1 weapon and 1 passive if possible
  const weapons = shuffled.filter(a => a.category === 'weapon');
  const passives = shuffled.filter(a => a.category === 'passive');
  
  const result: Ability[] = [];
  if (weapons.length > 0 && passives.length > 0 && count >= 2) {
    result.push(weapons[0], passives[0]);
    const remaining = shuffled.filter(a => a.id !== weapons[0].id && a.id !== passives[0].id);
    result.push(...remaining.slice(0, count - 2));
  } else {
    result.push(...shuffled.slice(0, count));
  }
  
  return result.slice(0, count);
}

// XP required for each level
export function xpForLevel(level: number): number {
  return Math.floor(25 + level * 18 + level * level * 3.5);
}

// Update orbital drones - projectileCount adds extra orbitals
export function updateOrbitals(state: GameState, dt: number) {
  if (state.abilities.orbitals <= 0) return;
  const p = state.player;
  const count = state.abilities.orbitals + state.abilities.projectileCount;
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

// Frost Nova - periodic freeze burst
export function updateFrostNova(state: GameState, dt: number) {
  if (state.abilities.frostNovaRadius <= 0) return;
  state.abilities.frostNovaTimer -= dt;
  if (state.abilities.frostNovaTimer <= 0) {
    state.abilities.frostNovaTimer = state.abilities.frostNovaCooldown;
    const p = state.player;
    const dmg = 10 + state.wave * 3;
    for (const e of state.enemies) {
      if (!e.alive) continue;
      const d = dist(e.pos, p.pos);
      if (d < state.abilities.frostNovaRadius) {
        e.hp -= dmg;
        e.flashTimer = 0.15;
        e.speed *= 0.5; // slow
        setTimeout(() => { if (e.alive) e.speed *= 2; }, 2000);
      }
    }
    state.particles.push(...createParticles(p.pos, '#80e0ff', 30, state.abilities.frostNovaRadius * 2, 3));
    state.particles.push(...createParticles(p.pos, '#ffffff', 15, state.abilities.frostNovaRadius * 1.5, 2));
  }
}

// Auto missiles - projectileCount adds extra missiles
export function updateMissiles(state: GameState, dt: number) {
  if (state.abilities.missileCount <= 0) return;
  state.abilities.missileTimer -= dt;
  if (state.abilities.missileTimer <= 0) {
    state.abilities.missileTimer = state.abilities.missileCooldown;
    const p = state.player;
    const alive = state.enemies.filter(e => e.alive);
    const sorted = alive.sort((a, b) => dist(a.pos, p.pos) - dist(b.pos, p.pos));
    const extraProj = state.abilities.projectileCount;
    const totalMissiles = state.abilities.missileCount + extraProj;
    const targets = sorted.slice(0, totalMissiles);
    for (const t of targets) {
      const angle = Math.atan2(t.pos.y - p.pos.y, t.pos.x - p.pos.x);
      state.projectiles.push({
        pos: { x: p.pos.x, y: p.pos.y },
        vel: { x: Math.cos(angle) * PROJECTILE_SPEED * 0.7, y: Math.sin(angle) * PROJECTILE_SPEED * 0.7 },
        radius: 5, alive: true, damage: p.damage * 0.8, fromPlayer: true,
        lifetime: 3, color: '#ff6b00',
      });
    }
    if (targets.length > 0) {
      state.particles.push(...createParticles(p.pos, '#ff6b00', 5, 60, 2));
    }
  }
}

// Lightning Ring - periodic auto-strikes, projectileCount adds extra targets
export function updateLightningRing(state: GameState, dt: number) {
  if (state.abilities.lightningRingRadius <= 0) return;
  state.abilities.lightningRingTimer -= dt;
  if (state.abilities.lightningRingTimer <= 0) {
    state.abilities.lightningRingTimer = 0.8;
    const p = state.player;
    let hits = 0;
    const maxHits = 1 + state.abilities.projectileCount;
    for (const e of state.enemies) {
      if (!e.alive) continue;
      if (hits >= maxHits) break;
      const d = dist(e.pos, p.pos);
      if (d < state.abilities.lightningRingRadius) {
        e.hp -= state.abilities.lightningRingDamage;
        e.flashTimer = 0.1;
        const steps = 4;
        for (let i = 0; i < steps; i++) {
          const t = i / steps;
          state.particles.push({
            pos: { x: p.pos.x + (e.pos.x - p.pos.x) * t + (Math.random() - 0.5) * 10, y: p.pos.y + (e.pos.y - p.pos.y) * t + (Math.random() - 0.5) * 10 },
            vel: { x: (Math.random() - 0.5) * 40, y: (Math.random() - 0.5) * 40 },
            lifetime: 0.15, maxLifetime: 0.15,
            color: '#80d0ff', size: 2,
          });
        }
        hits++;
      }
    }
    if (hits === 0) state.abilities.lightningRingTimer = 0.2;
  }
}

// Chain lightning on enemy death
export function triggerChainLightning(state: GameState, origin: { x: number; y: number }, bounces: number, damage: number) {
  if (bounces <= 0) return;
  let closest: Enemy | null = null;
  let closestDist = 200;
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
    const steps = 5;
    for (let i = 0; i < steps; i++) {
      const t = i / steps;
      state.particles.push({
        pos: { x: origin.x + (closest.pos.x - origin.x) * t, y: origin.y + (closest.pos.y - origin.y) * t },
        vel: { x: (Math.random() - 0.5) * 30, y: (Math.random() - 0.5) * 30 },
        lifetime: 0.2, maxLifetime: 0.2,
        color: COLORS.neonCyan, size: 2,
      });
    }
    triggerChainLightning(state, closest.pos, bounces - 1, damage * 0.8);
  }
}
