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
  return {
    pos: { x, y },
    vel: { x: 0, y: 0 },
    radius: s.radius,
    alive: true,
    type,
    hp: Math.floor(s.hp * waveScale),
    maxHp: Math.floor(s.hp * waveScale),
    damage: Math.floor(s.damage * (1 + (wave - 1) * 0.05)),
    speed: s.speed * (1 + (wave - 1) * 0.02),
    score: s.score,
    attackTimer: 0,
    attackCooldown: s.attackCooldown,
    isBoss: s.isBoss,
    flashTimer: 0,
    bossPhase: s.isBoss ? 0 : undefined,
    bossAttackTimer: s.isBoss ? 2 : undefined,
  };
}

export function createProjectile(pos: Vec2, angle: number, damage: number, fromPlayer: boolean, color: string, speedMult = 1): Projectile {
  return {
    pos: { x: pos.x, y: pos.y },
    vel: { x: Math.cos(angle) * PROJECTILE_SPEED * speedMult, y: Math.sin(angle) * PROJECTILE_SPEED * speedMult },
    radius: fromPlayer ? 4 : 5,
    alive: true,
    damage,
    fromPlayer,
    lifetime: PROJECTILE_LIFETIME,
    color,
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
      lifetime: lt,
      maxLifetime: lt,
      color,
      size: size * (0.5 + Math.random() * 0.5),
    });
  }
  return particles;
}

export function createPowerUp(pos: Vec2): PowerUp | null {
  const types: PowerUpType[] = ['speed', 'triple-shot', 'shield', 'heal'];
  const type = types[Math.floor(Math.random() * types.length)];
  return {
    pos: { x: pos.x, y: pos.y },
    vel: { x: 0, y: 0 },
    radius: 10,
    alive: true,
    type,
    lifetime: 10,
  };
}

export function playerAttack(player: Player, projectiles: Projectile[]): void {
  if (player.attackTimer > 0) return;
  player.attackTimer = player.attackCooldown;

  const color = player.class === 'phantom' ? COLORS.phantom
    : player.class === 'interceptor' ? COLORS.interceptor 
    : player.class === 'spectre' ? COLORS.spectre
    : player.class === 'valkyrie' ? COLORS.valkyrie
    : player.class === 'juggernaut' ? COLORS.juggernaut
    : COLORS.titan;

  if (player.class === 'titan' || player.class === 'juggernaut') {
    // Heavy blast - handled in engine for area damage
    return;
  }

  const angles = player.tripleTimer > 0 ? [-0.2, 0, 0.2] : [0];
  
  // Valkyrie shoots double
  if (player.class === 'valkyrie') {
    for (const offset of [-0.08, 0.08]) {
      projectiles.push(createProjectile(player.pos, player.angle + offset, player.damage, true, color, 1.2));
    }
    return;
  }
  
  for (const offset of angles) {
    projectiles.push(createProjectile(
      player.pos,
      player.angle + offset,
      player.damage,
      true,
      color,
      player.class === 'interceptor' ? 1.3 : player.class === 'spectre' ? 1.5 : 1
    ));
  }
}

export function playerSpecial(player: Player, projectiles: Projectile[], enemies: Enemy[]): void {
  if (player.specialTimer > 0) return;
  player.specialTimer = player.specialCooldown;

  if (player.class === 'phantom') {
    for (let i = 0; i < 16; i++) {
      const angle = (Math.PI * 2 / 16) * i;
      projectiles.push(createProjectile(player.pos, angle, player.damage * 2, true, COLORS.neonPink, 0.8));
    }
  } else if (player.class === 'interceptor') {
    const sorted = enemies.filter(e => e.alive).sort((a, b) => {
      const da = Math.hypot(a.pos.x - player.pos.x, a.pos.y - player.pos.y);
      const db = Math.hypot(b.pos.x - player.pos.x, b.pos.y - player.pos.y);
      return da - db;
    });
    for (let i = 0; i < Math.min(10, sorted.length); i++) {
      const e = sorted[i];
      const angle = Math.atan2(e.pos.y - player.pos.y, e.pos.x - player.pos.x);
      projectiles.push(createProjectile(player.pos, angle, player.damage * 1.5, true, COLORS.neonCyan, 1.5));
    }
  } else if (player.class === 'spectre') {
    // Teleport forward + ghost explosion
    const teleportDist = 120;
    player.pos.x += Math.cos(player.angle) * teleportDist;
    player.pos.y += Math.sin(player.angle) * teleportDist;
    player.invincibleTimer = 1.0;
    // Explosion at arrival
    for (let i = 0; i < 12; i++) {
      const angle = (Math.PI * 2 / 12) * i;
      projectiles.push(createProjectile(player.pos, angle, player.damage * 2.5, true, '#9040ff', 0.6));
    }
  } else if (player.class === 'valkyrie') {
    // Rain of energy lances from above
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
      const dist = Math.hypot(e.pos.x - player.pos.x, e.pos.y - player.pos.y);
      if (dist < WARRIOR_ATTACK_RANGE * 3) {
        e.hp -= player.damage * 4;
        e.flashTimer = 0.2;
      }
    }
  } else {
    // Titan shockwave
    for (const e of enemies) {
      if (!e.alive) continue;
      const dist = Math.hypot(e.pos.x - player.pos.x, e.pos.y - player.pos.y);
      if (dist < WARRIOR_ATTACK_RANGE * 2.5) {
        e.hp -= player.damage * 3;
        e.flashTimer = 0.15;
      }
    }
  }
}

export function dist(a: Vec2, b: Vec2): number {
  return Math.hypot(a.x - b.x, a.y - b.y);
}
