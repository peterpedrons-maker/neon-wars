import {
  GameState, InputState, Player, Enemy, EnemyType, XpOrb,
} from './types';
import { createAbilityState, updateOrbitals, updateAura, updateRegen, updateFrostNova, updateMissiles, updateLightningRing, triggerChainLightning, xpForLevel } from './abilities';
import { ALL_MAPS, createHazard, ActiveHazard } from './maps';
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
import {
  playShootPhantom, playShootInterceptor, playShootTitan,
  playExplosion, playCombo, playPowerUp, playSpecial,
  playHit, playDamage, playGameOver, playWaveComplete, initAudio,
  startMusic, stopMusic, setMusicIntensity,
} from './audio';

const WAVE_SPAWN_INTERVAL = 0.35;

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
  
  // Combo timer decay
  if (state.comboTimer > 0) {
    state.comboTimer -= dt;
    if (state.comboTimer <= 0) {
      state.combo = 0;
      state.comboMultiplier = 1;
    }
  }

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
      const prevTimer = p.attackTimer;
      playerAttack(p, state.projectiles);
      if (prevTimer <= 0 && p.attackTimer > 0) {
        // Shot was fired
        if (p.class === 'phantom') playShootPhantom();
        else playShootInterceptor();
      }
    }
  }

  // Special
  if (input.special) {
    const prevTimer = p.specialTimer;
    playerSpecial(p, state.projectiles, state.enemies);
    if (prevTimer <= 0 && p.specialTimer > 0) {
      playSpecial();
    }
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

  // Check wave complete - auto start next wave
  const aliveEnemies = state.enemies.filter(e => e.alive).length;
  if (state.waveEnemiesRemaining <= 0 && aliveEnemies === 0) {
    playWaveComplete();
    startWave(state);
  }

  updateEnemies(state, dt);
  updateProjectiles(state, dt);

  // Ability effects
  updateOrbitals(state, dt);
  updateAura(state, dt);
  updateRegen(state, dt);
  updateFrostNova(state, dt);
  updateMissiles(state, dt);
  updateLightningRing(state, dt);
  
  // Flame trail zones
  if (state.abilities.flameTrailDamage > 0 && Math.hypot(p.vel.x, p.vel.y) > 20) {
    state.flameZones.push({ x: p.pos.x, y: p.pos.y, damage: state.abilities.flameTrailDamage, lifetime: 3 });
    if (state.flameZones.length > 50) state.flameZones.shift();
  }
  // Update flame zones
  for (let i = state.flameZones.length - 1; i >= 0; i--) {
    state.flameZones[i].lifetime -= dt;
    if (state.flameZones[i].lifetime <= 0) { state.flameZones.splice(i, 1); continue; }
    const fz = state.flameZones[i];
    for (const e of state.enemies) {
      if (!e.alive) continue;
      if (Math.hypot(e.pos.x - fz.x, e.pos.y - fz.y) < 15 + e.radius) {
        e.hp -= fz.damage * dt;
        e.flashTimer = 0.03;
      }
    }
  }
  
  // Update plasma zones
  if (state.abilities.plasmaFieldRadius > 0) {
    state.abilities.plasmaFieldTimer -= dt;
    if (state.abilities.plasmaFieldTimer <= 0) {
      state.abilities.plasmaFieldTimer = 2;
      state.plasmaZones.push({ x: p.pos.x, y: p.pos.y, radius: state.abilities.plasmaFieldRadius, damage: state.abilities.plasmaFieldDamage, lifetime: 5 });
      if (state.plasmaZones.length > 8) state.plasmaZones.shift();
    }
  }
  for (let i = state.plasmaZones.length - 1; i >= 0; i--) {
    state.plasmaZones[i].lifetime -= dt;
    if (state.plasmaZones[i].lifetime <= 0) { state.plasmaZones.splice(i, 1); continue; }
    const pz = state.plasmaZones[i];
    for (const e of state.enemies) {
      if (!e.alive) continue;
      if (Math.hypot(e.pos.x - pz.x, e.pos.y - pz.y) < pz.radius + e.radius) {
        e.hp -= pz.damage * dt;
        e.flashTimer = 0.03;
      }
    }
  }

  // Update map hazards
  updateHazards(state, dt);

  // Update trail
  if (Math.hypot(p.vel.x, p.vel.y) > 10) {
    state.trail.push({ x: p.pos.x, y: p.pos.y, age: 0 });
  }
  for (let i = state.trail.length - 1; i >= 0; i--) {
    state.trail[i].age += dt;
    if (state.trail[i].age > 0.5) state.trail.splice(i, 1);
  }
  if (state.trail.length > 40) state.trail.splice(0, state.trail.length - 40);

  // Update XP orbs
  const magnetR = state.abilities.magnetRadius;
  state.xpOrbs = state.xpOrbs.filter(orb => {
    orb.lifetime -= dt;
    if (orb.lifetime <= 0) return false;
    // Magnet: attract to player
    const dx = p.pos.x - orb.pos.x;
    const dy = p.pos.y - orb.pos.y;
    const d = Math.hypot(dx, dy);
    if (d < magnetR) {
      const pullSpeed = 300 * (1 - d / magnetR) + 100;
      orb.pos.x += (dx / d) * pullSpeed * dt;
      orb.pos.y += (dy / d) * pullSpeed * dt;
    }
    orb.pos.x += orb.vel.x * dt;
    orb.pos.y += orb.vel.y * dt;
    orb.vel.x *= 0.95;
    orb.vel.y *= 0.95;
    // Collect
    if (d < p.radius + orb.radius + 5) {
      addXp(state, orb.value);
      return false;
    }
    return true;
  });

  // Level up check
  if (state.xp >= state.xpToNext && state.screen === 'playing') {
    state.xp -= state.xpToNext;
    state.level++;
    state.xpToNext = xpForLevel(state.level);
    state.screen = 'upgrade';
    state.particles.push(...createParticles(p.pos, '#ffff00', 30, 200, 4));
    state.particles.push(...createParticles(p.pos, '#ffffff', 15, 150, 3));
  }

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
  playShootTitan();

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

    const dx = p.pos.x - e.pos.x;
    const dy = p.pos.y - e.pos.y;
    const d = Math.hypot(dx, dy);

    // --- UNIQUE ENEMY BEHAVIORS ---
    if (e.type === 'drone') {
      // Drones: swarm in, orbit at close range
      if (d > 80) {
        e.pos.x += (dx / d) * e.speed * dt;
        e.pos.y += (dy / d) * e.speed * dt;
      } else {
        // Orbit the player
        const orbitAngle = Math.atan2(dy, dx) + Math.PI / 2;
        e.pos.x += Math.cos(orbitAngle) * e.speed * 0.8 * dt;
        e.pos.y += Math.sin(orbitAngle) * e.speed * 0.8 * dt;
        // Slowly close in
        e.pos.x += (dx / d) * e.speed * 0.15 * dt;
        e.pos.y += (dy / d) * e.speed * 0.15 * dt;
      }
    } else if (e.type === 'dasher') {
      // Dashers: charge in a straight line, pause, charge again
      if (!e.dashState) e.dashState = 'tracking';
      if (!e.dashTimer) e.dashTimer = 0;
      e.dashTimer -= dt;

      if (e.dashState === 'tracking') {
        // Slowly track player
        if (d > 0) {
          e.pos.x += (dx / d) * e.speed * 0.4 * dt;
          e.pos.y += (dy / d) * e.speed * 0.4 * dt;
        }
        if (e.dashTimer <= 0 && d < 300) {
          // Lock on and dash!
          e.dashState = 'dashing';
          e.dashTimer = 0.4;
          e.dashAngle = Math.atan2(dy, dx);
        }
        if (e.dashTimer <= 0) e.dashTimer = 1.0 + Math.random() * 0.5;
      } else if (e.dashState === 'dashing') {
        // Dash at high speed in locked direction
        const dashSpeed = e.speed * 3.5;
        e.pos.x += Math.cos(e.dashAngle!) * dashSpeed * dt;
        e.pos.y += Math.sin(e.dashAngle!) * dashSpeed * dt;
        // Dash trail particles
        if (Math.random() < 0.5) {
          state.particles.push(...createParticles(e.pos, COLORS.dasher, 1, 60, 2));
        }
        if (e.dashTimer <= 0) {
          e.dashState = 'cooldown';
          e.dashTimer = 0.8;
        }
      } else { // cooldown
        if (e.dashTimer <= 0) {
          e.dashState = 'tracking';
          e.dashTimer = 0.5 + Math.random() * 0.5;
        }
      }
    } else if (e.type === 'splitter') {
      // Splitters: weave side to side while approaching
      const weave = Math.sin(Date.now() * 0.005 + e.pos.x * 0.1) * 60;
      if (d > 0) {
        const perpX = -dy / d;
        const perpY = dx / d;
        e.pos.x += ((dx / d) * e.speed + perpX * weave) * dt;
        e.pos.y += ((dy / d) * e.speed + perpY * weave) * dt;
      }
    } else if (e.type === 'tank') {
      // Tanks: slow advance + shoots at player periodically
      if (d > 0) {
        e.pos.x += (dx / d) * e.speed * dt;
        e.pos.y += (dy / d) * e.speed * dt;
      }
      if (!e.shootTimer) e.shootTimer = 2;
      e.shootTimer -= dt;
      if (e.shootTimer <= 0 && d < 400) {
        e.shootTimer = 2.5 + Math.random();
        // Shoot 3 bullets in a spread
        const baseAngle = Math.atan2(dy, dx);
        for (let i = -1; i <= 1; i++) {
          state.projectiles.push({
            pos: { x: e.pos.x, y: e.pos.y },
            vel: { x: Math.cos(baseAngle + i * 0.15) * 200, y: Math.sin(baseAngle + i * 0.15) * 200 },
            radius: 5, alive: true, damage: e.damage, fromPlayer: false,
            lifetime: 2, color: COLORS.tank,
          });
        }
      }
    } else {
      // Default: move toward player (bosses etc)
      if (d > 0) {
        e.pos.x += (dx / d) * e.speed * dt;
        e.pos.y += (dy / d) * e.speed * dt;
      }
    }

    // Vortex boss: pulls player toward it
    if (e.type === 'vortex' && e.alive) {
      const pullStr = 40;
      const pullDx = e.pos.x - p.pos.x;
      const pullDy = e.pos.y - p.pos.y;
      const pullD = Math.hypot(pullDx, pullDy);
      if (pullD < 250 && pullD > 1) {
        p.pos.x += (pullDx / pullD) * pullStr * dt;
        p.pos.y += (pullDy / pullD) * pullStr * dt;
      }
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
    // Spawns mini drones + fires spread
    for (let i = -4; i <= 4; i++) {
      state.projectiles.push({
        pos: { x: boss.pos.x, y: boss.pos.y },
        vel: { x: Math.cos(angle + i * 0.12) * 280, y: Math.sin(angle + i * 0.12) * 280 },
        radius: 6, alive: true, damage: boss.damage, fromPlayer: false,
        lifetime: 2, color: COLORS.mothership,
      });
    }
    // Spawn 2 mini drones
    for (let i = 0; i < 2; i++) {
      const drone = createEnemy('drone', Math.max(1, state.wave - 2));
      drone.pos = { x: boss.pos.x + (Math.random() - 0.5) * 40, y: boss.pos.y + (Math.random() - 0.5) * 40 };
      drone.hp = Math.floor(drone.hp * 0.5);
      drone.maxHp = drone.hp;
      drone.score = 5;
      state.enemies.push(drone);
    }
  } else if (boss.type === 'vortex') {
    // Spiral pattern
    for (let i = 0; i < 12; i++) {
      const a = (Math.PI * 2 / 12) * i + Date.now() * 0.001;
      state.projectiles.push({
        pos: { x: boss.pos.x, y: boss.pos.y },
        vel: { x: Math.cos(a) * 200, y: Math.sin(a) * 200 },
        radius: 5, alive: true, damage: boss.damage * 0.7, fromPlayer: false,
        lifetime: 2.5, color: COLORS.vortex,
      });
    }
    // Pull particles
    state.particles.push(...createParticles(boss.pos, COLORS.vortex, 15, 100, 3));
  } else if (boss.type === 'colossus') {
    // Shockwave ring + aimed shot
    for (let i = 0; i < 24; i++) {
      const a = (Math.PI * 2 / 24) * i;
      state.projectiles.push({
        pos: { x: boss.pos.x, y: boss.pos.y },
        vel: { x: Math.cos(a) * 160, y: Math.sin(a) * 160 },
        radius: 8, alive: true, damage: boss.damage * 0.5, fromPlayer: false,
        lifetime: 1.5, color: COLORS.colossus,
      });
    }
    // Aimed heavy shot
    state.projectiles.push({
      pos: { x: boss.pos.x, y: boss.pos.y },
      vel: { x: Math.cos(angle) * 350, y: Math.sin(angle) * 350 },
      radius: 12, alive: true, damage: boss.damage, fromPlayer: false,
      lifetime: 2, color: '#ffffff',
    });
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
  // Crit check
  if (state.abilities.critChance > 0 && Math.random() < state.abilities.critChance) {
    damage *= 2;
    state.particles.push(...createParticles(e.pos, '#ffff00', 8, 150, 3));
  }
  
  e.hp -= damage;
  e.flashTimer = 0.1;
  playHit();
  state.particles.push(...createParticles(e.pos, COLORS.neonYellow, 15, 180, 3));
  state.particles.push(...createParticles(e.pos, '#ffffff', 8, 120, 2));
  state.particles.push(...createParticles(e.pos, getEnemyColor(e.type), 10, 150, 2.5));

  if (e.hp <= 0) {
    e.alive = false;
    
    // Combo system
    const prevMult = state.comboMultiplier;
    state.combo++;
    state.comboTimer = 2.0;
    state.comboMultiplier = Math.min(16, Math.pow(2, Math.floor(state.combo / 3)));
    if (state.combo > state.maxCombo) state.maxCombo = state.combo;
    if (state.comboMultiplier > prevMult) playCombo(state.comboMultiplier);
    
    state.score += e.score * state.comboMultiplier;
    state.enemiesKilled++;

    // Spawn XP orbs
    const xpValue = e.isBoss ? 50 : Math.floor(5 + e.score * 0.3);
    const orbCount = e.isBoss ? 8 : Math.min(4, Math.max(1, Math.floor(xpValue / 5)));
    for (let i = 0; i < orbCount; i++) {
      const angle = Math.random() * Math.PI * 2;
      const spd = 60 + Math.random() * 80;
      state.xpOrbs.push({
        pos: { x: e.pos.x, y: e.pos.y },
        vel: { x: Math.cos(angle) * spd, y: Math.sin(angle) * spd },
        value: Math.ceil(xpValue / orbCount),
        lifetime: 12,
        radius: e.isBoss ? 6 : 4,
      });
    }

    // Chain lightning
    if (state.abilities.chainCount > 0) {
      triggerChainLightning(state, e.pos, state.abilities.chainCount, damage * 0.5);
    }

    playExplosion(e.isBoss);

    const color = e.isBoss ? COLORS.neonYellow : getEnemyColor(e.type);
    state.particles.push(...createParticles(e.pos, color, e.isBoss ? 200 : 60, 400, e.isBoss ? 8 : 5));
    state.particles.push(...createParticles(e.pos, '#ffffff', e.isBoss ? 80 : 30, 300, 4));
    const secColor = e.isBoss ? '#ff1493' : COLORS.neonCyan;
    state.particles.push(...createParticles(e.pos, secColor, e.isBoss ? 60 : 25, 250, 3.5));
    state.particles.push(...createParticles(e.pos, COLORS.neonPink, e.isBoss ? 40 : 15, 350, 3));
    state.particles.push(...createParticles(e.pos, COLORS.neonGreen, e.isBoss ? 30 : 12, 280, 2.5));
    
    if (state.comboMultiplier >= 4) {
      state.particles.push(...createParticles(e.pos, '#ffff00', state.comboMultiplier * 3, 350, 4));
    }
    
    if (e.isBoss) {
      state.shakeTimer = 0.5;
      state.shakeIntensity = 14;
    } else {
      state.shakeTimer = Math.max(state.shakeTimer, 0.08);
      state.shakeIntensity = Math.max(state.shakeIntensity, 3);
    }

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
    const dropChance = POWERUP_DROP_CHANCE + (state.comboMultiplier - 1) * 0.02;
    if (Math.random() < dropChance) {
      const pu = createPowerUp(e.pos);
      if (pu) state.powerUps.push(pu);
    }
  }
}

function addXp(state: GameState, amount: number) {
  state.xp += amount;
  // Small particle feedback
  state.particles.push(...createParticles(state.player.pos, '#bf5af2', 2, 40, 1.5));
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

  p.hp -= 1; // Always lose 1 heart per hit
  p.invincibleTimer = 1.0;
  state.shakeTimer = 0.15;
  state.shakeIntensity = 5;
  state.particles.push(...createParticles(p.pos, COLORS.health, 6, 120, 2));
  playDamage();

  if (p.hp <= 0) {
    p.hp = 0;
    p.alive = false;
    state.screen = 'game-over';
    state.particles.push(...createParticles(p.pos, COLORS.neonYellow, 40, 300, 5));
    state.particles.push(...createParticles(p.pos, '#ffffff', 20, 200, 3));
    stopMusic();
    playGameOver();
  }
}

function applyPowerUp(state: GameState, type: string) {
  const p = state.player;
  state.particles.push(...createParticles(p.pos, COLORS.neonYellow, 10, 120, 3));
  playPowerUp();

  switch (type) {
    case 'speed': p.speedBoostTimer = 8; break;
    case 'triple-shot': p.tripleTimer = 8; break;
    case 'shield': p.shieldTimer = 15; break;
    case 'heal': p.hp = Math.min(p.maxHp, p.hp + 1); break;
  }
}

export function startWave(state: GameState) {
  state.wave++;
  setMusicIntensity(state.wave);
  const isBossWave = state.wave % BOSS_WAVE_INTERVAL === 0;
  state.waveEnemiesRemaining = isBossWave
    ? WAVE_BASE_ENEMIES + state.wave * 2 + 1
    : WAVE_BASE_ENEMIES + (state.wave - 1) * WAVE_ENEMY_INCREMENT;
  state.waveSpawnTimer = 0;
  state.screen = 'playing';
}

export function createInitialState(player: Player): GameState {
  initAudio();
  startMusic();
  return {
    player,
    enemies: [],
    projectiles: [],
    particles: [],
    powerUps: [],
    xpOrbs: [],
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
    combo: 0,
    comboTimer: 0,
    maxCombo: 0,
    comboMultiplier: 1,
    xp: 0,
    level: 1,
    xpToNext: xpForLevel(1),
    abilityLevels: {},
    abilities: createAbilityState(),
    regenAccumulator: 0,
    trail: [],
  };
}
