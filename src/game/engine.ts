import {
  GameState, InputState, Player, Enemy, EnemyType,
} from './types';
import {
  ARENA_W, ARENA_H, COLORS, WAVE_BASE_ENEMIES,
  WAVE_ENEMY_INCREMENT, BOSS_WAVE_INTERVAL,
  POWERUP_DROP_CHANCE, WARRIOR_ATTACK_RANGE,
  WALL_LEFT, WALL_RIGHT, WALL_TOP, WALL_BOTTOM,
} from './constants';
import {
  createEnemy, createParticles, createPowerUp,
  playerAttack, playerSpecial, dist,
} from './entities';

const WAVE_SPAWN_INTERVAL = 1.0;

export function updateGame(state: GameState, input: InputState, dt: number): void {
  if (state.screen !== 'playing') return;
  const p = state.player;
  if (!p.alive) return;

  // Timers
  p.attackTimer = Math.max(0, p.attackTimer - dt);
  p.specialTimer = Math.max(0, p.specialTimer - dt);
  p.shieldTimer = Math.max(0, p.shieldTimer - dt);
  p.tripleTimer = Math.max(0, p.tripleTimer - dt);
  p.speedBoostTimer = Math.max(0, p.speedBoostTimer - dt);
  p.invincibleTimer = Math.max(0, p.invincibleTimer - dt);
  state.shakeTimer = Math.max(0, state.shakeTimer - dt);

  // Player movement
  const speed = p.speed * (p.speedBoostTimer > 0 ? 1.5 : 1);
  p.vel.x = input.moveX * speed;
  p.vel.y = input.moveY * speed;
  p.pos.x += p.vel.x * dt;
  p.pos.y += p.vel.y * dt;
  p.pos.x = Math.max(WALL_LEFT + p.radius, Math.min(WALL_RIGHT - p.radius, p.pos.x));
  p.pos.y = Math.max(WALL_TOP + p.radius, Math.min(WALL_BOTTOM - p.radius, p.pos.y));

  // Aim
  if (input.aimX !== 0 || input.aimY !== 0) {
    p.angle = Math.atan2(input.aimY, input.aimX);
  }

  // Attack
  if (input.shooting) {
    if (p.class === 'titan') {
      titanBlast(state, dt);
    } else {
      playerAttack(p, state.projectiles);
    }
  }

  // Special
  if (input.special) {
    playerSpecial(p, state.projectiles, state.enemies);
  }

  // Spawn wave enemies
  if (state.waveEnemiesRemaining > 0) {
    state.waveSpawnTimer -= dt;
    if (state.waveSpawnTimer <= 0) {
      state.waveSpawnTimer = WAVE_SPAWN_INTERVAL / (1 + state.wave * 0.05);
      spawnWaveEnemy(state);
      state.waveEnemiesRemaining--;
    }
  }

  // Check wave complete
  const aliveEnemies = state.enemies.filter(e => e.alive).length;
  if (state.waveEnemiesRemaining <= 0 && aliveEnemies === 0) {
    state.screen = 'upgrade';
    return;
  }

  updateEnemies(state, dt);
  updateProjectiles(state, dt);

  // Update particles
  state.particles = state.particles.filter(p => {
    p.lifetime -= dt;
    p.pos.x += p.vel.x * dt;
    p.pos.y += p.vel.y * dt;
    p.vel.x *= 0.96;
    p.vel.y *= 0.96;
    return p.lifetime > 0;
  });

  // Update power-ups
  state.powerUps = state.powerUps.filter(pu => {
    if (!pu.alive) return false;
    pu.lifetime -= dt;
    if (pu.lifetime <= 0) return false;
    if (dist(pu.pos, p.pos) < pu.radius + p.radius) {
      applyPowerUp(state, pu.type as any);
      return false;
    }
    return true;
  });

  // Clean dead
  state.enemies = state.enemies.filter(e => e.alive || e.flashTimer > 0);
  state.projectiles = state.projectiles.filter(p => p.alive);
}

function titanBlast(state: GameState, _dt: number) {
  const p = state.player;
  if (p.attackTimer > 0) return;
  p.attackTimer = p.attackCooldown;

  for (const e of state.enemies) {
    if (!e.alive) continue;
    const d = dist(p.pos, e.pos);
    if (d > WARRIOR_ATTACK_RANGE + e.radius) continue;
    const angleToEnemy = Math.atan2(e.pos.y - p.pos.y, e.pos.x - p.pos.x);
    let angleDiff = Math.abs(angleToEnemy - p.angle);
    if (angleDiff > Math.PI) angleDiff = Math.PI * 2 - angleDiff;
    if (angleDiff < 1.0) {
      damageEnemy(state, e, p.damage * (p.tripleTimer > 0 ? 2 : 1));
    }
  }
  state.particles.push(...createParticles(
    { x: p.pos.x + Math.cos(p.angle) * 30, y: p.pos.y + Math.sin(p.angle) * 30 },
    COLORS.titanGlow, 8, 120, 4
  ));
}

function spawnWaveEnemy(state: GameState) {
  const isBossWave = state.wave % BOSS_WAVE_INTERVAL === 0;

  if (isBossWave && state.waveEnemiesRemaining === 1) {
    const bosses: EnemyType[] = ['mothership', 'vortex', 'colossus'];
    const boss = bosses[Math.floor(Math.random() * bosses.length)];
    state.enemies.push(createEnemy(boss, state.wave));
    return;
  }

  const types: EnemyType[] = ['drone'];
  if (state.wave >= 2) types.push('splitter');
  if (state.wave >= 3) types.push('dasher');
  if (state.wave >= 5) types.push('tank');

  const type = types[Math.floor(Math.random() * types.length)];
  state.enemies.push(createEnemy(type, state.wave));
}

function updateEnemies(state: GameState, dt: number) {
  const p = state.player;

  for (const e of state.enemies) {
    if (!e.alive) {
      e.flashTimer -= dt;
      continue;
    }

    e.flashTimer = Math.max(0, e.flashTimer - dt);
    e.attackTimer = Math.max(0, e.attackTimer - dt);

    // Move toward player
    const dx = p.pos.x - e.pos.x;
    const dy = p.pos.y - e.pos.y;
    const d = Math.hypot(dx, dy);

    if (d > 0) {
      let moveX = (dx / d) * e.speed * dt;
      let moveY = (dy / d) * e.speed * dt;

      // Dasher erratic movement
      if (e.type === 'dasher') {
        moveX += (Math.random() - 0.5) * 4;
        moveY += (Math.random() - 0.5) * 4;
      }

      e.pos.x += moveX;
      e.pos.y += moveY;
    }

    e.pos.x = Math.max(WALL_LEFT + e.radius, Math.min(WALL_RIGHT - e.radius, e.pos.x));
    e.pos.y = Math.max(WALL_TOP + e.radius, Math.min(WALL_BOTTOM - e.radius, e.pos.y));

    // Boss attacks
    if (e.isBoss && e.bossAttackTimer !== undefined) {
      e.bossAttackTimer! -= dt;
      if (e.bossAttackTimer! <= 0) {
        e.bossAttackTimer = e.attackCooldown;
        bossAttack(state, e);
      }
    }

    // Contact damage
    if (dist(e.pos, p.pos) < e.radius + p.radius) {
      if (e.attackTimer <= 0) {
        damagePlayer(state, e.damage);
        e.attackTimer = e.attackCooldown;
      }
    }
  }
}

function bossAttack(state: GameState, boss: Enemy) {
  const p = state.player;
  const angle = Math.atan2(p.pos.y - boss.pos.y, p.pos.x - boss.pos.x);

  if (boss.type === 'mothership') {
    for (let i = -4; i <= 4; i++) {
      state.projectiles.push({
        pos: { x: boss.pos.x, y: boss.pos.y },
        vel: { x: Math.cos(angle + i * 0.12) * 280, y: Math.sin(angle + i * 0.12) * 280 },
        radius: 6, alive: true, damage: boss.damage, fromPlayer: false,
        lifetime: 2, color: COLORS.mothership,
      });
    }
  } else if (boss.type === 'vortex') {
    for (let i = 0; i < 10; i++) {
      const a = (Math.PI * 2 / 10) * i;
      state.projectiles.push({
        pos: { x: boss.pos.x, y: boss.pos.y },
        vel: { x: Math.cos(a) * 200, y: Math.sin(a) * 200 },
        radius: 5, alive: true, damage: boss.damage * 0.7, fromPlayer: false,
        lifetime: 2.5, color: COLORS.vortex,
      });
    }
  } else if (boss.type === 'colossus') {
    for (let i = 0; i < 20; i++) {
      const a = (Math.PI * 2 / 20) * i;
      state.projectiles.push({
        pos: { x: boss.pos.x, y: boss.pos.y },
        vel: { x: Math.cos(a) * 160, y: Math.sin(a) * 160 },
        radius: 8, alive: true, damage: boss.damage * 0.5, fromPlayer: false,
        lifetime: 1.5, color: COLORS.colossus,
      });
    }
    state.shakeTimer = 0.3;
    state.shakeIntensity = 8;
  }
}

function updateProjectiles(state: GameState, dt: number) {
  const p = state.player;

  for (const proj of state.projectiles) {
    if (!proj.alive) continue;
    proj.pos.x += proj.vel.x * dt;
    proj.pos.y += proj.vel.y * dt;
    proj.lifetime -= dt;

    if (proj.lifetime <= 0 || proj.pos.x < -20 || proj.pos.x > ARENA_W + 20 ||
        proj.pos.y < -20 || proj.pos.y > ARENA_H + 20) {
      proj.alive = false;
      continue;
    }

    if (proj.fromPlayer) {
      for (const e of state.enemies) {
        if (!e.alive) continue;
        if (dist(proj.pos, e.pos) < proj.radius + e.radius) {
          proj.alive = false;
          damageEnemy(state, e, proj.damage);
          break;
        }
      }
    } else {
      if (dist(proj.pos, p.pos) < proj.radius + p.radius) {
        proj.alive = false;
        damagePlayer(state, proj.damage);
      }
    }
  }
}

function damageEnemy(state: GameState, e: Enemy, damage: number) {
  e.hp -= damage;
  e.flashTimer = 0.1;
  state.particles.push(...createParticles(e.pos, COLORS.neonYellow, 4, 100, 2));

  if (e.hp <= 0) {
    e.alive = false;
    state.score += e.score;
    state.enemiesKilled++;

    // Death explosion - lots of neon particles
    const color = e.isBoss ? COLORS.neonYellow : getEnemyColor(e.type);
    state.particles.push(...createParticles(e.pos, color, e.isBoss ? 40 : 15, 250, e.isBoss ? 5 : 3));
    state.particles.push(...createParticles(e.pos, '#ffffff', 5, 180, 2));

    // Splitter split
    if (e.type === 'splitter' && e.maxHp > 8) {
      for (let i = 0; i < 2; i++) {
        const child = createEnemy('splitter', Math.max(1, state.wave - 1));
        child.pos = { x: e.pos.x + (i === 0 ? -15 : 15), y: e.pos.y };
        child.hp = Math.floor(e.maxHp * 0.4);
        child.maxHp = child.hp;
        child.radius = Math.max(5, e.radius * 0.7);
        child.score = Math.floor(e.score * 0.5);
        state.enemies.push(child);
      }
    }

    // Power-up drop
    if (Math.random() < POWERUP_DROP_CHANCE) {
      const pu = createPowerUp(e.pos);
      if (pu) state.powerUps.push(pu);
    }
  }
}

function getEnemyColor(type: EnemyType): string {
  const map: Record<string, string> = {
    drone: COLORS.drone, splitter: COLORS.splitter, dasher: COLORS.dasher,
    tank: COLORS.tank, mothership: COLORS.mothership, vortex: COLORS.vortex, colossus: COLORS.colossus,
  };
  return map[type] || '#fff';
}

function damagePlayer(state: GameState, damage: number) {
  const p = state.player;
  if (p.invincibleTimer > 0) return;
  if (p.shieldTimer > 0) {
    p.shieldTimer = 0;
    state.particles.push(...createParticles(p.pos, COLORS.neonCyan, 15, 150, 3));
    p.invincibleTimer = 0.5;
    return;
  }

  p.hp -= damage;
  p.invincibleTimer = 0.5;
  state.shakeTimer = 0.15;
  state.shakeIntensity = 5;
  state.particles.push(...createParticles(p.pos, COLORS.health, 6, 120, 2));

  if (p.hp <= 0) {
    p.hp = 0;
    p.alive = false;
    state.screen = 'game-over';
    state.particles.push(...createParticles(p.pos, COLORS.neonYellow, 40, 300, 5));
    state.particles.push(...createParticles(p.pos, '#ffffff', 20, 200, 3));
  }
}

function applyPowerUp(state: GameState, type: string) {
  const p = state.player;
  state.particles.push(...createParticles(p.pos, COLORS.neonYellow, 10, 120, 3));

  switch (type) {
    case 'speed': p.speedBoostTimer = 8; break;
    case 'triple-shot': p.tripleTimer = 8; break;
    case 'shield': p.shieldTimer = 15; break;
    case 'heal': p.hp = Math.min(p.maxHp, p.hp + 25); break;
  }
}

export function startWave(state: GameState) {
  state.wave++;
  const isBossWave = state.wave % BOSS_WAVE_INTERVAL === 0;
  state.waveEnemiesRemaining = isBossWave
    ? WAVE_BASE_ENEMIES + state.wave * 2 + 1
    : WAVE_BASE_ENEMIES + (state.wave - 1) * WAVE_ENEMY_INCREMENT;
  state.waveSpawnTimer = 0;
  state.screen = 'playing';
}

export function createInitialState(player: Player): GameState {
  return {
    player,
    enemies: [],
    projectiles: [],
    particles: [],
    powerUps: [],
    wave: 0,
    score: 0,
    enemiesKilled: 0,
    screen: 'playing',
    waveEnemiesRemaining: 0,
    waveSpawnTimer: 0,
    arenaWidth: ARENA_W,
    arenaHeight: ARENA_H,
    shakeTimer: 0,
    shakeIntensity: 0,
  };
}
