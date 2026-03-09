import {
  Player, Enemy, Projectile, Particle, PowerUp, Vec2,
  ShipType, EnemyType, PowerUpType, GameState
} from './types';
import {
  CLASS_STATS, ENEMY_STATS, ARENA_W, ARENA_H,
  SPAWN_MARGIN, PROJECTILE_SPEED, PROJECTILE_LIFETIME,
  COLORS, WARRIOR_ATTACK_RANGE
} from './constants';
import { AbilityState } from './abilities';

export function createPlayer(cls: ShipType): Player {
  const s = CLASS_STATS[cls];
  return {
    pos: { x: ARENA_W / 2, y: ARENA_H / 2 },
    vel: { x: 0, y: 0 },
    radius: s.radius,
    alive: true,
    hp: s.hp,
    maxHp: s.hp,
    class: cls,
    damage: s.damage,
    speed: s.speed,
    attackCooldown: s.attackCooldown,
    attackTimer: 0,
    specialCooldown: s.specialCooldown,
    specialTimer: 0,
    shieldTimer: 0,
    tripleTimer: 0,
    speedBoostTimer: 0,
    invincibleTimer: 0,
    angle: 0,
  };
}

export function createEnemy(type: EnemyType, wave: number): Enemy {
  const s = ENEMY_STATS[type];
  const side = Math.floor(Math.random() * 4);
  let x: number, y: number;
  switch (side) {
    case 0: x = Math.random() * ARENA_W; y = -SPAWN_MARGIN; break;
    case 1: x = ARENA_W + SPAWN_MARGIN; y = Math.random() * ARENA_H; break;
    case 2: x = Math.random() * ARENA_W; y = ARENA_H + SPAWN_MARGIN; break;
    default: x = -SPAWN_MARGIN; y = Math.random() * ARENA_H; break;
  }
  const waveScale = 1 + (wave - 1) * 0.08;
  const baseSpeed = s.speed * (1 + (wave - 1) * 0.02);
  return {
    pos: { x, y },
    vel: { x: 0, y: 0 },
    radius: s.radius,
    alive: true,
    type,
    hp: Math.floor(s.hp * waveScale),
    maxHp: Math.floor(s.hp * waveScale),
    damage: Math.floor(s.damage * (1 + (wave - 1) * 0.05)),
    speed: baseSpeed,
    baseSpeed,
    score: s.score,
    attackTimer: 0,
    attackCooldown: s.attackCooldown,
    isBoss: s.isBoss,
    flashTimer: 0,
    bossPhase: s.isBoss ? 0 : undefined,
    bossAttackTimer: s.isBoss ? 2 : undefined,
  };
}

export function createProjectile(
  pos: Vec2, angle: number, damage: number, fromPlayer: boolean,
  color: string, speedMult = 1, mods?: Partial<Projectile>,
): Projectile {
  return {
    pos: { x: pos.x, y: pos.y },
    vel: { x: Math.cos(angle) * PROJECTILE_SPEED * speedMult, y: Math.sin(angle) * PROJECTILE_SPEED * speedMult },
    radius: fromPlayer ? 4 : 5,
    alive: true, damage, fromPlayer,
    lifetime: PROJECTILE_LIFETIME, color,
    ...mods,
  };
}

export function createParticles(pos: Vec2, color: string, count: number, speed = 150, size = 3): Particle[] {
  const particles: Particle[] = [];
  for (let i = 0; i < count; i++) {
    const angle = Math.random() * Math.PI * 2;
    const spd = speed * (0.3 + Math.random() * 0.7);
    const lt = 0.3 + Math.random() * 0.6;
    particles.push({
      pos: { x: pos.x, y: pos.y },
      vel: { x: Math.cos(angle) * spd, y: Math.sin(angle) * spd },
      lifetime: lt, maxLifetime: lt, color,
      size: size * (0.5 + Math.random() * 0.5),
    });
  }
  return particles;
}

export function createPowerUp(pos: Vec2): PowerUp | null {
  if (Math.random() < 0.03) {
    return { pos: { x: pos.x, y: pos.y }, vel: { x: 0, y: 0 }, radius: 10, alive: true, type: 'heal', lifetime: 8 };
  }
  const types: PowerUpType[] = ['speed', 'triple-shot', 'shield'];
  const type = types[Math.floor(Math.random() * types.length)];
  return { pos: { x: pos.x, y: pos.y }, vel: { x: 0, y: 0 }, radius: 10, alive: true, type, lifetime: 10 };
}

// Melee ships - attack nearby enemies instead of shooting projectiles
const MELEE_SHIPS: ShipType[] = ['titan', 'juggernaut', 'leviathan'];

// Ships with custom speed multipliers
const SPEED_MULTS: Partial<Record<ShipType, number>> = {
  interceptor: 1.3, spectre: 1.5, raptor: 1.6, tempest: 1.4, wraith: 1.3,
};

export function playerAttack(player: Player, projectiles: Projectile[], abilities?: AbilityState): void {
  if (player.attackTimer > 0) return;
  player.attackTimer = player.attackCooldown;

  const color = COLORS[player.class] || COLORS.phantom;

  // Melee ships don't shoot projectiles
  if (MELEE_SHIPS.includes(player.class)) return;

  const extraProjectiles = abilities?.projectileCount || 0;
  const baseAngles = player.tripleTimer > 0 ? [-0.2, 0, 0.2] : [0];
  let angles = [...baseAngles];
  for (let i = 1; i <= extraProjectiles; i++) {
    angles.push(i * 0.12);
    angles.push(-i * 0.12);
  }

  const mods = abilities ? { pierce: abilities.pierce || 0, ricochet: abilities.ricochet || 0 } : undefined;

  // Valkyrie: twin emitters
  if (player.class === 'valkyrie') {
    const vAngles = [-0.08, 0.08];
    for (let i = 1; i <= extraProjectiles; i++) {
      vAngles.push(0.08 + i * 0.12);
      vAngles.push(-0.08 - i * 0.12);
    }
    for (const offset of vAngles) {
      projectiles.push(createProjectile(player.pos, player.angle + offset, player.damage, true, color, 1.2, mods));
    }
    return;
  }

  // Venom: poison shots (slower but lingering)
  if (player.class === 'venom') {
    const vAngles = player.tripleTimer > 0 ? [-0.15, 0, 0.15] : [0];
    for (const offset of vAngles) {
      projectiles.push(createProjectile(player.pos, player.angle + offset, player.damage, true, color, 0.8, { ...mods, lifetime: 3 }));
    }
    return;
  }

  // Oracle: homing shots
  if (player.class === 'oracle') {
    for (const offset of angles) {
      projectiles.push(createProjectile(player.pos, player.angle + offset, player.damage, true, color, 0.9, { ...mods }));
    }
    return;
  }

  // Nova: slow powerful shots
  if (player.class === 'nova_ship') {
    projectiles.push(createProjectile(player.pos, player.angle, player.damage, true, color, 0.7, { ...mods, radius: 8 } as any));
    return;
  }

  // Pyro: flamethrower spread
  if (player.class === 'pyro') {
    for (let i = -2; i <= 2; i++) {
      projectiles.push(createProjectile(player.pos, player.angle + i * 0.1, player.damage * 0.5, true, color, 0.6 + Math.random() * 0.4, { ...mods, lifetime: 0.6 }));
    }
    return;
  }

  // Sentinel: shield burst (fewer but stronger)
  if (player.class === 'sentinel') {
    for (const offset of angles) {
      projectiles.push(createProjectile(player.pos, player.angle + offset, player.damage, true, color, 0.9, mods));
    }
    return;
  }

  // Raptor: ultra-fast tiny shots
  if (player.class === 'raptor') {
    projectiles.push(createProjectile(player.pos, player.angle + (Math.random() - 0.5) * 0.15, player.damage, true, color, 1.6, mods));
    return;
  }

  const speedMult = SPEED_MULTS[player.class] || 1;
  for (const offset of angles) {
    projectiles.push(createProjectile(player.pos, player.angle + offset, player.damage, true, color, speedMult, mods));
  }
}

export function playerSpecial(player: Player, projectiles: Projectile[], enemies: Enemy[]): void {
  if (player.specialTimer > 0) return;
  player.specialTimer = player.specialCooldown;

  const color = COLORS[player.class] || COLORS.phantom;

  if (player.class === 'phantom') {
    // Plasma nova
    for (let i = 0; i < 16; i++) {
      const angle = (Math.PI * 2 / 16) * i;
      projectiles.push(createProjectile(player.pos, angle, player.damage * 2, true, COLORS.neonPink, 0.8));
    }
  } else if (player.class === 'interceptor') {
    // Lock-on barrage
    const sorted = enemies.filter(e => e.alive).sort((a, b) =>
      Math.hypot(a.pos.x - player.pos.x, a.pos.y - player.pos.y) -
      Math.hypot(b.pos.x - player.pos.x, b.pos.y - player.pos.y)
    );
    for (let i = 0; i < Math.min(10, sorted.length); i++) {
      const e = sorted[i];
      const angle = Math.atan2(e.pos.y - player.pos.y, e.pos.x - player.pos.x);
      projectiles.push(createProjectile(player.pos, angle, player.damage * 1.5, true, COLORS.neonCyan, 1.5));
    }
  } else if (player.class === 'spectre') {
    // Teleport + ghost explosion
    player.pos.x += Math.cos(player.angle) * 120;
    player.pos.y += Math.sin(player.angle) * 120;
    player.invincibleTimer = 1.0;
    for (let i = 0; i < 12; i++) {
      const angle = (Math.PI * 2 / 12) * i;
      projectiles.push(createProjectile(player.pos, angle, player.damage * 2.5, true, '#9040ff', 0.6));
    }
  } else if (player.class === 'valkyrie') {
    // Rain of lances
    for (let i = 0; i < 8; i++) {
      const angle = player.angle + (i - 3.5) * 0.15;
      projectiles.push(createProjectile(
        { x: player.pos.x + (i - 3.5) * 20, y: player.pos.y },
        angle, player.damage * 1.8, true, '#ff1493', 1.2
      ));
    }
  } else if (player.class === 'juggernaut') {
    // Massive destruction field
    for (const e of enemies) {
      if (!e.alive) continue;
      const d = Math.hypot(e.pos.x - player.pos.x, e.pos.y - player.pos.y);
      if (d < WARRIOR_ATTACK_RANGE * 3) { e.hp -= player.damage * 4; e.flashTimer = 0.2; }
    }
  } else if (player.class === 'titan') {
    // Shockwave
    for (const e of enemies) {
      if (!e.alive) continue;
      const d = Math.hypot(e.pos.x - player.pos.x, e.pos.y - player.pos.y);
      if (d < WARRIOR_ATTACK_RANGE * 2.5) { e.hp -= player.damage * 3; e.flashTimer = 0.15; }
    }
  } else if (player.class === 'wraith') {
    // Phase shift: become invisible + leave shadow clones that shoot
    player.invincibleTimer = 2.0;
    for (let i = 0; i < 6; i++) {
      const angle = (Math.PI * 2 / 6) * i;
      const cx = player.pos.x + Math.cos(angle) * 60;
      const cy = player.pos.y + Math.sin(angle) * 60;
      for (let j = 0; j < 4; j++) {
        const a2 = (Math.PI * 2 / 4) * j;
        projectiles.push(createProjectile({ x: cx, y: cy }, a2, player.damage * 1.2, true, color, 1.0));
      }
    }
  } else if (player.class === 'sentinel') {
    // Deploy barrier: massive shield + reflect zone
    player.shieldTimer = 8;
    for (let i = 0; i < 20; i++) {
      const angle = (Math.PI * 2 / 20) * i;
      projectiles.push(createProjectile(player.pos, angle, player.damage * 1.5, true, color, 0.5));
    }
  } else if (player.class === 'tempest') {
    // Tornado: pulls enemies in then explodes
    for (const e of enemies) {
      if (!e.alive) continue;
      const d = Math.hypot(e.pos.x - player.pos.x, e.pos.y - player.pos.y);
      if (d < 200) {
        const dx = player.pos.x - e.pos.x;
        const dy = player.pos.y - e.pos.y;
        e.pos.x += dx * 0.5;
        e.pos.y += dy * 0.5;
        e.hp -= player.damage * 1.5;
        e.flashTimer = 0.15;
      }
    }
    for (let i = 0; i < 16; i++) {
      const angle = (Math.PI * 2 / 16) * i;
      projectiles.push(createProjectile(player.pos, angle, player.damage, true, color, 1.2));
    }
  } else if (player.class === 'venom') {
    // Toxic cloud: massive poison AoE
    for (let i = 0; i < 24; i++) {
      const angle = (Math.PI * 2 / 24) * i;
      const spd = 0.3 + Math.random() * 0.5;
      projectiles.push(createProjectile(player.pos, angle, player.damage * 0.8, true, color, spd, { lifetime: 4 }));
    }
  } else if (player.class === 'nova_ship') {
    // Supernova: massive explosion
    for (const e of enemies) {
      if (!e.alive) continue;
      const d = Math.hypot(e.pos.x - player.pos.x, e.pos.y - player.pos.y);
      if (d < 250) {
        e.hp -= player.damage * 5;
        e.flashTimer = 0.3;
      }
    }
  } else if (player.class === 'chronos') {
    // Time Freeze: slow all enemies
    for (const e of enemies) {
      if (!e.alive) continue;
      e.slowUntil = Date.now() + 5000;
    }
    // Bonus: shoot time shards
    for (let i = 0; i < 12; i++) {
      const angle = (Math.PI * 2 / 12) * i;
      projectiles.push(createProjectile(player.pos, angle, player.damage * 2, true, color, 0.8));
    }
  } else if (player.class === 'leviathan') {
    // Devour: massive AoE damage + heal
    for (const e of enemies) {
      if (!e.alive) continue;
      const d = Math.hypot(e.pos.x - player.pos.x, e.pos.y - player.pos.y);
      if (d < WARRIOR_ATTACK_RANGE * 4) {
        e.hp -= player.damage * 5;
        e.flashTimer = 0.25;
        if (e.hp <= 0) player.hp = Math.min(player.maxHp, player.hp + 1);
      }
    }
  } else if (player.class === 'raptor') {
    // Blitz: dash forward shooting a wall of bullets
    player.pos.x += Math.cos(player.angle) * 150;
    player.pos.y += Math.sin(player.angle) * 150;
    player.invincibleTimer = 0.8;
    for (let i = -8; i <= 8; i++) {
      const perpAngle = player.angle + Math.PI / 2;
      const ox = Math.cos(perpAngle) * i * 8;
      const oy = Math.sin(perpAngle) * i * 8;
      projectiles.push(createProjectile(
        { x: player.pos.x + ox, y: player.pos.y + oy },
        player.angle, player.damage * 1.5, true, color, 1.3
      ));
    }
  } else if (player.class === 'oracle') {
    // Foresight: mark all enemies, each takes bonus damage burst
    for (const e of enemies) {
      if (!e.alive) continue;
      e.hp -= player.damage * 2;
      e.flashTimer = 0.2;
      const angle = Math.atan2(e.pos.y - player.pos.y, e.pos.x - player.pos.x);
      projectiles.push(createProjectile(player.pos, angle, player.damage, true, color, 2.0));
    }
  } else if (player.class === 'pyro') {
    // Inferno: ring of fire expanding outward
    for (let ring = 0; ring < 3; ring++) {
      for (let i = 0; i < 12; i++) {
        const angle = (Math.PI * 2 / 12) * i + ring * 0.15;
        projectiles.push(createProjectile(player.pos, angle, player.damage * 1.5, true, color, 0.5 + ring * 0.3, { lifetime: 2 }));
      }
    }
  }
}

export function dist(a: Vec2, b: Vec2): number {
  return Math.hypot(a.x - b.x, a.y - b.y);
}
