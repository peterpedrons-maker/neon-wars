import {
  Player, Enemy, Projectile, Particle, PowerUp, Vec2,
  PlayerClass, EnemyType, PowerUpType
} from './types';
import {
  CLASS_STATS, ENEMY_STATS, ARENA_W, ARENA_H,
  SPAWN_MARGIN, PROJECTILE_SPEED, PROJECTILE_LIFETIME,
  COLORS, WARRIOR_ATTACK_RANGE
} from './constants';

export function createPlayer(cls: PlayerClass): Player {
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
    radius: fromPlayer ? 5 : 6,
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
    const lt = 0.3 + Math.random() * 0.5;
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

  const color = player.class === 'mage' ? COLORS.magic
    : player.class === 'archer' ? COLORS.archer : COLORS.warrior;

  if (player.class === 'warrior') {
    // Melee sweep - handled via collision in engine
    return;
  }

  const angles = player.tripleTimer > 0 ? [-0.2, 0, 0.2] : [0];
  for (const offset of angles) {
    projectiles.push(createProjectile(
      player.pos,
      player.angle + offset,
      player.damage,
      true,
      color,
      player.class === 'archer' ? 1.3 : 1
    ));
  }
}

export function playerSpecial(player: Player, projectiles: Projectile[], enemies: Enemy[]): void {
  if (player.specialTimer > 0) return;
  player.specialTimer = player.specialCooldown;

  if (player.class === 'mage') {
    // Nova burst - 12 projectiles in all directions
    for (let i = 0; i < 12; i++) {
      const angle = (Math.PI * 2 / 12) * i;
      projectiles.push(createProjectile(player.pos, angle, player.damage * 2, true, COLORS.fire, 0.8));
    }
  } else if (player.class === 'archer') {
    // Rain of arrows - rapid fire at nearest enemies
    const sorted = enemies.filter(e => e.alive).sort((a, b) => {
      const da = Math.hypot(a.pos.x - player.pos.x, a.pos.y - player.pos.y);
      const db = Math.hypot(b.pos.x - player.pos.x, b.pos.y - player.pos.y);
      return da - db;
    });
    for (let i = 0; i < Math.min(8, sorted.length); i++) {
      const e = sorted[i];
      const angle = Math.atan2(e.pos.y - player.pos.y, e.pos.x - player.pos.x);
      projectiles.push(createProjectile(player.pos, angle, player.damage * 1.5, true, COLORS.archerGlow, 1.5));
    }
  } else {
    // Warrior whirlwind - damage all enemies in large radius
    for (const e of enemies) {
      if (!e.alive) continue;
      const dist = Math.hypot(e.pos.x - player.pos.x, e.pos.y - player.pos.y);
      if (dist < WARRIOR_ATTACK_RANGE * 2) {
        e.hp -= player.damage * 3;
        e.flashTimer = 0.15;
      }
    }
  }
}

export function dist(a: Vec2, b: Vec2): number {
  return Math.hypot(a.x - b.x, a.y - b.y);
}
