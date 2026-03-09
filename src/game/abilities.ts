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
  // NEW ELEMENTAL WEAPONS
  chainLightningDamage: number;
  chainLightningChains: number;
  chainLightningCooldown: number;
  chainLightningTimer: number;
  iceBeamDamage: number;
  iceBeamSlowDuration: number;
  iceBeamCooldown: number;
  iceBeamTimer: number;
  boomerangDamage: number;
  boomerangCount: number;
  boomerangCooldown: number;
  boomerangTimer: number;
  heavyCannonDamage: number;
  heavyCannonCooldown: number;
  heavyCannonTimer: number;
  acidSprayDamage: number;
  acidSprayTicks: number;
  acidSprayCooldown: number;
  acidSprayTimer: number;
  gravityWellRadius: number;
  gravityWellDamage: number;
  gravityWellCooldown: number;
  gravityWellTimer: number;
  teslaCoilDamage: number;
  teslaCoilChains: number;
  teslaCoilCooldown: number;
  teslaCoilTimer: number;
  voidRiftDamage: number;
  voidRiftRadius: number;
  voidRiftCooldown: number;
  voidRiftTimer: number;
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
    // NEW ELEMENTAL WEAPONS
    chainLightningDamage: 0,
    chainLightningChains: 0,
    chainLightningCooldown: 2.5,
    chainLightningTimer: 0,
    iceBeamDamage: 0,
    iceBeamSlowDuration: 0,
    iceBeamCooldown: 1.8,
    iceBeamTimer: 0,
    boomerangDamage: 0,
    boomerangCount: 0,
    boomerangCooldown: 2.0,
    boomerangTimer: 0,
    heavyCannonDamage: 0,
    heavyCannonCooldown: 3.0,
    heavyCannonTimer: 0,
    acidSprayDamage: 0,
    acidSprayTicks: 0,
    acidSprayCooldown: 2.2,
    acidSprayTimer: 0,
    gravityWellRadius: 0,
    gravityWellDamage: 0,
    gravityWellCooldown: 4.5,
    gravityWellTimer: 0,
    teslaCoilDamage: 0,
    teslaCoilChains: 0,
    teslaCoilCooldown: 1.5,
    teslaCoilTimer: 0,
    voidRiftDamage: 0,
    voidRiftRadius: 0,
    voidRiftCooldown: 5.0,
    voidRiftTimer: 0,
    // Passive
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
  // === NEW ELEMENTAL WEAPONS ===
  {
    id: 'chain_lightning_weapon',
    name: 'Raio Cadeia',
    description: 'Dispara raios que saltam entre inimigos',
    icon: '⚡',
    maxLevel: 5,
    category: 'weapon',
    requiresUnlock: true,
    apply: (state) => {
      state.abilities.chainLightningDamage += 18;
      state.abilities.chainLightningChains += 1;
      state.abilities.chainLightningCooldown = Math.max(1.0, state.abilities.chainLightningCooldown - 0.25);
    },
  },
  {
    id: 'ice_beam',
    name: 'Raio de Gelo',
    description: 'Congela inimigos, causando slow prolongado',
    icon: '❄️',
    maxLevel: 5,
    category: 'weapon',
    requiresUnlock: true,
    apply: (state) => {
      state.abilities.iceBeamDamage += 12;
      state.abilities.iceBeamSlowDuration += 0.8;
      state.abilities.iceBeamCooldown = Math.max(0.8, state.abilities.iceBeamCooldown - 0.15);
    },
  },
  {
    id: 'boomerang',
    name: 'Bumerangue',
    description: 'Projétil que retorna, atingindo inimigos duas vezes',
    icon: '🪃',
    maxLevel: 5,
    category: 'weapon',
    requiresUnlock: true,
    apply: (state) => {
      state.abilities.boomerangDamage += 15;
      state.abilities.boomerangCount += 1;
      state.abilities.boomerangCooldown = Math.max(1.2, state.abilities.boomerangCooldown - 0.12);
    },
  },
  {
    id: 'heavy_cannon',
    name: 'Canhão Pesado',
    description: 'Disparo lento mas devastador com alto dano',
    icon: '💀',
    maxLevel: 5,
    category: 'weapon',
    requiresUnlock: true,
    apply: (state) => {
      state.abilities.heavyCannonDamage += 45;
      state.abilities.heavyCannonCooldown = Math.max(1.5, state.abilities.heavyCannonCooldown - 0.2);
    },
  },
  {
    id: 'acid_spray',
    name: 'Spray Ácido',
    description: 'Jatos de ácido que causam dano contínuo',
    icon: '🧪',
    maxLevel: 4,
    category: 'weapon',
    requiresUnlock: true,
    apply: (state) => {
      state.abilities.acidSprayDamage += 8;
      state.abilities.acidSprayTicks += 1;
      state.abilities.acidSprayCooldown = Math.max(1.0, state.abilities.acidSprayCooldown - 0.2);
    },
  },
  {
    id: 'gravity_well',
    name: 'Poço Gravitacional',
    description: 'Cria zonas que puxam e esmagam inimigos',
    icon: '🌀',
    maxLevel: 4,
    category: 'weapon',
    requiresUnlock: true,
    apply: (state) => {
      state.abilities.gravityWellRadius += 35;
      state.abilities.gravityWellDamage += 20;
      state.abilities.gravityWellCooldown = Math.max(2.5, state.abilities.gravityWellCooldown - 0.3);
    },
  },
  {
    id: 'tesla_coil',
    name: 'Bobina Tesla',
    description: 'Arcos elétricos automáticos entre inimigos',
    icon: '🔌',
    maxLevel: 5,
    category: 'weapon',
    requiresUnlock: true,
    apply: (state) => {
      state.abilities.teslaCoilDamage += 10;
      state.abilities.teslaCoilChains += 1;
      state.abilities.teslaCoilCooldown = Math.max(0.6, state.abilities.teslaCoilCooldown - 0.12);
    },
  },
  {
    id: 'void_rift',
    name: 'Fenda do Vazio',
    description: 'Abre portais que sugam e destroem inimigos',
    icon: '🕳️',
    maxLevel: 4,
    category: 'weapon',
    requiresUnlock: true,
    apply: (state) => {
      state.abilities.voidRiftRadius += 30;
      state.abilities.voidRiftDamage += 25;
      state.abilities.voidRiftCooldown = Math.max(3.0, state.abilities.voidRiftCooldown - 0.35);
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
    const now = Date.now();

    for (const e of state.enemies) {
      if (!e.alive) continue;
      const d = dist(e.pos, p.pos);
      if (d < state.abilities.frostNovaRadius) {
        e.hp -= dmg;
        e.flashTimer = 0.15;
        // Slow for 2s without stacking speed multipliers
        const base = e.baseSpeed ?? e.speed;
        e.baseSpeed = base;
        e.speed = base * 0.5;
        e.slowUntil = now + 2000;
      }
    }

    state.particles.push(...createParticles(p.pos, '#80e0ff', 20, state.abilities.frostNovaRadius * 2.4, 2.5));
    state.particles.push(...createParticles(p.pos, '#ffffff', 10, state.abilities.frostNovaRadius * 1.8, 2));
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
            pos: {
              x: p.pos.x + (e.pos.x - p.pos.x) * t + (Math.random() - 0.5) * 10,
              y: p.pos.y + (e.pos.y - p.pos.y) * t + (Math.random() - 0.5) * 10,
            },
            vel: { x: (Math.random() - 0.5) * 40, y: (Math.random() - 0.5) * 40 },
            lifetime: 0.15,
            maxLifetime: 0.15,
            color: '#80d0ff',
            size: 2,
          });
        }
        hits++;
      }
    }
    if (hits === 0) state.abilities.lightningRingTimer = 0.2;
  }
}

// Ion Beam - periodic line strike in aim direction
export function updateIonBeam(state: GameState, dt: number) {
  if (state.abilities.ionBeamDamage <= 0) return;
  state.abilities.ionBeamTimer -= dt;
  if (state.abilities.ionBeamTimer > 0) return;

  state.abilities.ionBeamTimer = state.abilities.ionBeamCooldown;
  const p = state.player;
  const len = state.abilities.ionBeamLength;
  const width = 18;
  const dx = Math.cos(p.angle);
  const dy = Math.sin(p.angle);
  const damage = state.abilities.ionBeamDamage + state.wave * 2;

  for (const e of state.enemies) {
    if (!e.alive) continue;
    const ex = e.pos.x - p.pos.x;
    const ey = e.pos.y - p.pos.y;
    const t = ex * dx + ey * dy;
    if (t < 0 || t > len) continue;
    const px = p.pos.x + dx * t;
    const py = p.pos.y + dy * t;
    const distToLine = Math.hypot(e.pos.x - px, e.pos.y - py);
    if (distToLine < width + e.radius) {
      e.hp -= damage;
      e.flashTimer = 0.12;
    }
  }

  // Visual sweep
  for (let i = 0; i < 10; i++) {
    const t = (i / 10) * len;
    state.particles.push(...createParticles({ x: p.pos.x + dx * t, y: p.pos.y + dy * t }, '#80d0ff', 2, 260, 2));
  }
}

// Shockwave - periodic radial burst
export function updateShockwave(state: GameState, dt: number) {
  if (state.abilities.shockwaveRadius <= 0) return;
  state.abilities.shockwaveTimer -= dt;
  if (state.abilities.shockwaveTimer > 0) return;

  state.abilities.shockwaveTimer = state.abilities.shockwaveCooldown;
  const p = state.player;
  const r = state.abilities.shockwaveRadius;
  const damage = state.abilities.shockwaveDamage + state.wave;

  for (const e of state.enemies) {
    if (!e.alive) continue;
    if (dist(e.pos, p.pos) < r + e.radius) {
      e.hp -= damage;
      e.flashTimer = 0.1;
    }
  }

  state.particles.push(...createParticles(p.pos, '#ffffff', 12, r * 3.5, 2.5));
  state.particles.push(...createParticles(p.pos, COLORS.neonPink, 10, r * 3.2, 2.5));
}

// Sentry drones - periodic auto-shots
export function updateSentries(state: GameState, dt: number) {
  if (state.abilities.sentryCount <= 0) return;
  state.abilities.sentryTimer -= dt;
  if (state.abilities.sentryTimer > 0) return;

  state.abilities.sentryTimer = state.abilities.sentryCooldown;
  const p = state.player;
  const alive = state.enemies.filter(e => e.alive);
  if (alive.length === 0) return;

  const sorted = alive.sort((a, b) => dist(a.pos, p.pos) - dist(b.pos, p.pos));
  const shots = Math.min(state.abilities.sentryCount + state.abilities.projectileCount, sorted.length);

  for (let i = 0; i < shots; i++) {
    const t = sorted[i];
    const angle = Math.atan2(t.pos.y - p.pos.y, t.pos.x - p.pos.x);
    state.projectiles.push({
      pos: { x: p.pos.x, y: p.pos.y },
      vel: { x: Math.cos(angle) * PROJECTILE_SPEED * 0.9, y: Math.sin(angle) * PROJECTILE_SPEED * 0.9 },
      radius: 4,
      alive: true,
      damage: (state.abilities.sentryDamage + p.damage * 0.25) * 0.9,
      fromPlayer: true,
      lifetime: 2.2,
      color: COLORS.neonCyan,
      pierce: Math.max(0, state.abilities.pierce - 1),
      ricochet: state.abilities.ricochet,
    });
  }

  state.particles.push(...createParticles(p.pos, COLORS.neonCyan, 4, 120, 2));
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

// === NEW ELEMENTAL WEAPON UPDATE FUNCTIONS ===

// Chain Lightning Weapon - fires arcing projectiles
export function updateChainLightningWeapon(state: GameState, dt: number) {
  if (state.abilities.chainLightningChains <= 0) return;
  state.abilities.chainLightningTimer -= dt;
  if (state.abilities.chainLightningTimer > 0) return;
  
  state.abilities.chainLightningTimer = state.abilities.chainLightningCooldown;
  const p = state.player;
  const alive = state.enemies.filter(e => e.alive);
  if (alive.length === 0) return;
  
  const nearest = alive.sort((a, b) => dist(a.pos, p.pos) - dist(b.pos, p.pos))[0];
  const angle = Math.atan2(nearest.pos.y - p.pos.y, nearest.pos.x - p.pos.x);
  
  state.projectiles.push({
    pos: { x: p.pos.x, y: p.pos.y },
    vel: { x: Math.cos(angle) * PROJECTILE_SPEED * 0.9, y: Math.sin(angle) * PROJECTILE_SPEED * 0.9 },
    radius: 6, alive: true, damage: state.abilities.chainLightningDamage + state.wave * 2, fromPlayer: true,
    lifetime: 2, color: '#00ffff',
    element: 'lightning',
    chainLightning: state.abilities.chainLightningChains,
  });
  
  state.particles.push(...createParticles(p.pos, '#00ffff', 6, 80, 2));
}

// Ice Beam - fires freezing projectiles
export function updateIceBeam(state: GameState, dt: number) {
  if (state.abilities.iceBeamDamage <= 0) return;
  state.abilities.iceBeamTimer -= dt;
  if (state.abilities.iceBeamTimer > 0) return;
  
  state.abilities.iceBeamTimer = state.abilities.iceBeamCooldown;
  const p = state.player;
  
  // Fire ice projectile in aim direction
  state.projectiles.push({
    pos: { x: p.pos.x, y: p.pos.y },
    vel: { x: Math.cos(p.angle) * PROJECTILE_SPEED * 0.7, y: Math.sin(p.angle) * PROJECTILE_SPEED * 0.7 },
    radius: 8, alive: true, damage: state.abilities.iceBeamDamage + state.wave, fromPlayer: true,
    lifetime: 2.5, color: '#88ddff',
    element: 'ice',
    iceSlow: state.abilities.iceBeamSlowDuration * 1000, // ms
  });
  
  state.particles.push(...createParticles(p.pos, '#88ddff', 5, 60, 2));
}

// Boomerang - projectiles that return
export function updateBoomerang(state: GameState, dt: number) {
  if (state.abilities.boomerangCount <= 0) return;
  state.abilities.boomerangTimer -= dt;
  if (state.abilities.boomerangTimer > 0) return;
  
  state.abilities.boomerangTimer = state.abilities.boomerangCooldown;
  const p = state.player;
  
  const count = state.abilities.boomerangCount;
  for (let i = 0; i < count; i++) {
    const offset = (i - (count - 1) / 2) * 0.3;
    state.projectiles.push({
      pos: { x: p.pos.x, y: p.pos.y },
      vel: { x: Math.cos(p.angle + offset) * PROJECTILE_SPEED * 0.8, y: Math.sin(p.angle + offset) * PROJECTILE_SPEED * 0.8 },
      radius: 7, alive: true, damage: state.abilities.boomerangDamage + state.wave * 1.5, fromPlayer: true,
      lifetime: 4, color: '#ffaa00',
      boomerang: true,
      returning: false,
      originPos: { x: p.pos.x, y: p.pos.y },
      pierce: 99, // infinite pierce for boomerang
    });
  }
  
  state.particles.push(...createParticles(p.pos, '#ffaa00', 4, 60, 2));
}

// Heavy Cannon - slow but devastating
export function updateHeavyCannon(state: GameState, dt: number) {
  if (state.abilities.heavyCannonDamage <= 0) return;
  state.abilities.heavyCannonTimer -= dt;
  if (state.abilities.heavyCannonTimer > 0) return;
  
  state.abilities.heavyCannonTimer = state.abilities.heavyCannonCooldown;
  const p = state.player;
  
  state.projectiles.push({
    pos: { x: p.pos.x, y: p.pos.y },
    vel: { x: Math.cos(p.angle) * PROJECTILE_SPEED * 0.4, y: Math.sin(p.angle) * PROJECTILE_SPEED * 0.4 },
    radius: 14, alive: true, damage: state.abilities.heavyCannonDamage + state.wave * 3, fromPlayer: true,
    lifetime: 4, color: '#ff4444',
    heavy: true,
    pierce: 2, // pierces 2 enemies
  });
  
  // Screen shake for heavy shot
  state.shakeTimer = 0.1;
  state.shakeIntensity = 4;
  state.particles.push(...createParticles(p.pos, '#ff4444', 8, 100, 3));
}

// Acid Spray - DoT damage
export function updateAcidSpray(state: GameState, dt: number) {
  if (state.abilities.acidSprayDamage <= 0) return;
  state.abilities.acidSprayTimer -= dt;
  if (state.abilities.acidSprayTimer > 0) return;
  
  state.abilities.acidSprayTimer = state.abilities.acidSprayCooldown;
  const p = state.player;
  
  // Spray 5 acid droplets in a cone
  for (let i = -2; i <= 2; i++) {
    const spread = i * 0.2;
    const speedVar = 0.7 + Math.random() * 0.4;
    state.projectiles.push({
      pos: { x: p.pos.x, y: p.pos.y },
      vel: { x: Math.cos(p.angle + spread) * PROJECTILE_SPEED * speedVar, y: Math.sin(p.angle + spread) * PROJECTILE_SPEED * speedVar },
      radius: 5, alive: true, damage: state.abilities.acidSprayDamage, fromPlayer: true,
      lifetime: 1.5, color: '#66ff00',
      element: 'acid',
      acid: state.abilities.acidSprayTicks,
    });
  }
  
  state.particles.push(...createParticles(p.pos, '#66ff00', 6, 80, 2));
}

// Gravity Well - creates pulling zones
export function updateGravityWell(state: GameState, dt: number) {
  if (state.abilities.gravityWellRadius <= 0) return;
  state.abilities.gravityWellTimer -= dt;
  if (state.abilities.gravityWellTimer > 0) return;
  
  state.abilities.gravityWellTimer = state.abilities.gravityWellCooldown;
  const p = state.player;
  
  // Create gravity zone projectile
  const alive = state.enemies.filter(e => e.alive);
  if (alive.length === 0) return;
  
  // Target densest enemy cluster
  const target = alive[Math.floor(Math.random() * Math.min(3, alive.length))];
  
  state.projectiles.push({
    pos: { x: target.pos.x, y: target.pos.y },
    vel: { x: 0, y: 0 },
    radius: state.abilities.gravityWellRadius, alive: true, damage: state.abilities.gravityWellDamage, fromPlayer: true,
    lifetime: 2.5, color: '#9966ff',
    element: 'gravity',
    gravityPull: state.abilities.gravityWellRadius * 1.5,
  });
  
  state.particles.push(...createParticles(target.pos, '#9966ff', 15, 150, 3));
}

// Tesla Coil - auto chains between enemies
export function updateTeslaCoil(state: GameState, dt: number) {
  if (state.abilities.teslaCoilDamage <= 0) return;
  state.abilities.teslaCoilTimer -= dt;
  if (state.abilities.teslaCoilTimer > 0) return;
  
  state.abilities.teslaCoilTimer = state.abilities.teslaCoilCooldown;
  const p = state.player;
  const range = 150;
  
  const alive = state.enemies.filter(e => e.alive && dist(e.pos, p.pos) < range);
  if (alive.length === 0) {
    state.abilities.teslaCoilTimer = 0.3;
    return;
  }
  
  // Start chain from nearest enemy
  const nearest = alive.sort((a, b) => dist(a.pos, p.pos) - dist(b.pos, p.pos))[0];
  
  // Draw lightning to first target
  drawLightningArc(state, p.pos, nearest.pos, '#00ffff');
  nearest.hp -= state.abilities.teslaCoilDamage + state.wave;
  nearest.flashTimer = 0.1;
  
  // Chain to nearby enemies
  let current = nearest;
  const hit = new Set([nearest]);
  for (let c = 0; c < state.abilities.teslaCoilChains; c++) {
    let nextTarget: Enemy | null = null;
    let nextDist = 120;
    for (const e of state.enemies) {
      if (!e.alive || hit.has(e)) continue;
      const d = dist(e.pos, current.pos);
      if (d < nextDist) {
        nextDist = d;
        nextTarget = e;
      }
    }
    if (nextTarget) {
      drawLightningArc(state, current.pos, nextTarget.pos, '#00ffff');
      nextTarget.hp -= state.abilities.teslaCoilDamage * 0.8;
      nextTarget.flashTimer = 0.08;
      hit.add(nextTarget);
      current = nextTarget;
    }
  }
}

// Void Rift - opens portals that damage enemies
export function updateVoidRift(state: GameState, dt: number) {
  if (state.abilities.voidRiftRadius <= 0) return;
  state.abilities.voidRiftTimer -= dt;
  if (state.abilities.voidRiftTimer > 0) return;
  
  state.abilities.voidRiftTimer = state.abilities.voidRiftCooldown;
  const p = state.player;
  
  // Create void rift at aim position (200 units ahead)
  const rx = p.pos.x + Math.cos(p.angle) * 150;
  const ry = p.pos.y + Math.sin(p.angle) * 150;
  
  state.projectiles.push({
    pos: { x: rx, y: ry },
    vel: { x: 0, y: 0 },
    radius: state.abilities.voidRiftRadius, alive: true, damage: state.abilities.voidRiftDamage, fromPlayer: true,
    lifetime: 3, color: '#660099',
    element: 'void',
    gravityPull: state.abilities.voidRiftRadius * 2,
  });
  
  state.particles.push(...createParticles({ x: rx, y: ry }, '#9933ff', 20, 200, 4));
}

// Helper function to draw lightning arcs
function drawLightningArc(state: GameState, from: { x: number; y: number }, to: { x: number; y: number }, color: string) {
  const steps = 5;
  for (let i = 0; i < steps; i++) {
    const t = i / steps;
    const jitter = i > 0 && i < steps - 1 ? (Math.random() - 0.5) * 15 : 0;
    state.particles.push({
      pos: {
        x: from.x + (to.x - from.x) * t + jitter,
        y: from.y + (to.y - from.y) * t + jitter,
      },
      vel: { x: (Math.random() - 0.5) * 30, y: (Math.random() - 0.5) * 30 },
      lifetime: 0.15,
      maxLifetime: 0.15,
      color,
      size: 2.5,
    });
  }
}

// === SYNERGY SYSTEM ===
export interface SynergyEffect {
  fire_ice: 'steam_explosion'; // Fire + Ice = Steam explosion
  fire_lightning: 'plasma_burst'; // Fire + Lightning = Plasma
  ice_lightning: 'shatter'; // Ice + Lightning = Shatter
  acid_fire: 'toxic_flame'; // Acid + Fire = Toxic flames
  gravity_lightning: 'emp'; // Gravity + Lightning = EMP
  void_fire: 'hellfire'; // Void + Fire = Hellfire
}

export function checkProjectileSynergy(state: GameState, proj1: any, proj2: any) {
  if (!proj1.element || !proj2.element || proj1.element === 'none' || proj2.element === 'none') return;
  if (proj1.element === proj2.element) return;
  
  const elem1 = proj1.element;
  const elem2 = proj2.element;
  const midX = (proj1.pos.x + proj2.pos.x) / 2;
  const midY = (proj1.pos.y + proj2.pos.y) / 2;
  
  // Fire + Ice = Steam Explosion
  if ((elem1 === 'fire' && elem2 === 'ice') || (elem1 === 'ice' && elem2 === 'fire')) {
    createSteamExplosion(state, midX, midY, (proj1.damage + proj2.damage) * 1.5);
  }
  // Fire + Lightning = Plasma Burst
  else if ((elem1 === 'fire' && elem2 === 'lightning') || (elem1 === 'lightning' && elem2 === 'fire')) {
    createPlasmaBurst(state, midX, midY, (proj1.damage + proj2.damage) * 1.8);
  }
  // Ice + Lightning = Shatter
  else if ((elem1 === 'ice' && elem2 === 'lightning') || (elem1 === 'lightning' && elem2 === 'ice')) {
    createShatterEffect(state, midX, midY, (proj1.damage + proj2.damage) * 1.6);
  }
  // Acid + Fire = Toxic Flame
  else if ((elem1 === 'acid' && elem2 === 'fire') || (elem1 === 'fire' && elem2 === 'acid')) {
    createToxicFlame(state, midX, midY, (proj1.damage + proj2.damage) * 1.4);
  }
  // Gravity + Lightning = EMP
  else if ((elem1 === 'gravity' && elem2 === 'lightning') || (elem1 === 'lightning' && elem2 === 'gravity')) {
    createEMPBurst(state, midX, midY, (proj1.damage + proj2.damage) * 2.0);
  }
  // Void + Fire = Hellfire
  else if ((elem1 === 'void' && elem2 === 'fire') || (elem1 === 'fire' && elem2 === 'void')) {
    createHellfireBurst(state, midX, midY, (proj1.damage + proj2.damage) * 2.2);
  }
}

function createSteamExplosion(state: GameState, x: number, y: number, damage: number) {
  const radius = 80;
  for (const e of state.enemies) {
    if (!e.alive) continue;
    if (dist(e.pos, { x, y }) < radius + e.radius) {
      e.hp -= damage;
      e.flashTimer = 0.2;
      // Also slow enemies
      e.slowUntil = Date.now() + 1500;
      e.speed = (e.baseSpeed ?? e.speed) * 0.5;
    }
  }
  state.particles.push(...createParticles({ x, y }, '#ffffff', 30, radius * 2, 4));
  state.particles.push(...createParticles({ x, y }, '#88ccff', 20, radius * 1.5, 3));
  state.shakeTimer = 0.2;
  state.shakeIntensity = 6;
}

function createPlasmaBurst(state: GameState, x: number, y: number, damage: number) {
  const radius = 100;
  for (const e of state.enemies) {
    if (!e.alive) continue;
    if (dist(e.pos, { x, y }) < radius + e.radius) {
      e.hp -= damage;
      e.flashTimer = 0.25;
    }
  }
  state.particles.push(...createParticles({ x, y }, '#ff00ff', 40, radius * 2, 5));
  state.particles.push(...createParticles({ x, y }, '#00ffff', 25, radius * 1.8, 4));
  state.shakeTimer = 0.3;
  state.shakeIntensity = 10;
}

function createShatterEffect(state: GameState, x: number, y: number, damage: number) {
  // Creates ice shards that fly outward
  for (let i = 0; i < 12; i++) {
    const angle = (Math.PI * 2 / 12) * i;
    state.projectiles.push({
      pos: { x, y },
      vel: { x: Math.cos(angle) * 300, y: Math.sin(angle) * 300 },
      radius: 4, alive: true, damage: damage / 4, fromPlayer: true,
      lifetime: 0.8, color: '#88ddff',
      element: 'ice',
    });
  }
  state.particles.push(...createParticles({ x, y }, '#88ddff', 35, 150, 3));
  state.shakeTimer = 0.15;
  state.shakeIntensity = 5;
}

function createToxicFlame(state: GameState, x: number, y: number, damage: number) {
  const radius = 70;
  for (const e of state.enemies) {
    if (!e.alive) continue;
    if (dist(e.pos, { x, y }) < radius + e.radius) {
      e.hp -= damage;
      e.flashTimer = 0.15;
    }
  }
  // Leave toxic zone
  state.flameZones.push({ x, y, damage: damage * 0.3, lifetime: 4 });
  state.particles.push(...createParticles({ x, y }, '#88ff00', 25, radius * 1.5, 4));
  state.particles.push(...createParticles({ x, y }, '#ff6600', 15, radius * 1.2, 3));
}

function createEMPBurst(state: GameState, x: number, y: number, damage: number) {
  const radius = 120;
  for (const e of state.enemies) {
    if (!e.alive) continue;
    if (dist(e.pos, { x, y }) < radius + e.radius) {
      e.hp -= damage;
      e.flashTimer = 0.3;
      // Stun (massive slow)
      e.slowUntil = Date.now() + 3000;
      e.speed = (e.baseSpeed ?? e.speed) * 0.2;
    }
  }
  state.particles.push(...createParticles({ x, y }, '#00ffff', 50, radius * 2, 4));
  state.particles.push(...createParticles({ x, y }, '#ffffff', 30, radius * 1.5, 3));
  state.shakeTimer = 0.4;
  state.shakeIntensity = 12;
}

function createHellfireBurst(state: GameState, x: number, y: number, damage: number) {
  const radius = 90;
  for (const e of state.enemies) {
    if (!e.alive) continue;
    if (dist(e.pos, { x, y }) < radius + e.radius) {
      e.hp -= damage;
      e.flashTimer = 0.25;
    }
  }
  // Create expanding fire ring
  for (let i = 0; i < 16; i++) {
    const angle = (Math.PI * 2 / 16) * i;
    state.projectiles.push({
      pos: { x, y },
      vel: { x: Math.cos(angle) * 200, y: Math.sin(angle) * 200 },
      radius: 6, alive: true, damage: damage / 5, fromPlayer: true,
      lifetime: 1.2, color: '#ff4400',
      element: 'fire',
    });
  }
  state.particles.push(...createParticles({ x, y }, '#ff0000', 40, radius * 2, 5));
  state.particles.push(...createParticles({ x, y }, '#660099', 25, radius * 1.5, 4));
  state.shakeTimer = 0.35;
  state.shakeIntensity = 14;
}
