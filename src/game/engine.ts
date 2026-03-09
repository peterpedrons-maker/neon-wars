import {
  GameState, InputState, Player, Enemy, EnemyType, XpOrb,
} from './types';
import {
  createAbilityState,
  updateOrbitals,
  updateAura,
  updateRegen,
  updateFrostNova,
  updateMissiles,
  updateLightningRing,
  updateIonBeam,
  updateShockwave,
  updateSentries,
  triggerChainLightning,
  xpForLevel,
  // New elemental weapons
  updateChainLightningWeapon,
  updateIceBeam,
  updateBoomerang,
  updateHeavyCannon,
  updateAcidSpray,
  updateGravityWell,
  updateTeslaCoil,
  updateVoidRift,
  checkProjectileSynergy,
} from './abilities';
import { ALL_MAPS, createHazard, ActiveHazard } from './maps';
import {
  ARENA_W, ARENA_H, COLORS, WAVE_BASE_ENEMIES,
  WAVE_ENEMY_INCREMENT, BOSS_WAVE_INTERVAL,
  POWERUP_DROP_CHANCE, WARRIOR_ATTACK_RANGE,
  WALL_LEFT, WALL_RIGHT, WALL_TOP, WALL_BOTTOM,
} from './constants';
import {
  createEnemy, createParticles, createPowerUp, createProjectile,
  playerAttack, playerSpecial, dist,
} from './entities';
import {
  playShootPhantom, playShootInterceptor, playShootTitan,
  playExplosion, playCombo, playPowerUp, playSpecial,
  playHit, playDamage, playGameOver, playWaveComplete, initAudio,
  startMusic, stopMusic, setMusicIntensity, setBossMusic,
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
  if (p.emote && p.emote.timer > 0) p.emote.timer -= dt;
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
  if (p.class === 'titan' || p.class === 'juggernaut' || p.class === 'leviathan') {
      titanBlast(state, dt);
    } else {
      const prevTimer = p.attackTimer;
      playerAttack(p, state.projectiles, state.abilities);
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
      const diff = getDifficultySettings(state);
      state.waveSpawnTimer = (WAVE_SPAWN_INTERVAL / (1 + state.wave * 0.05)) / diff.spawnRateMult;
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
  
  // Coop: host simulates all peers shooting
  if (state.coopPeers.length > 0) {
    for (const peer of state.coopPeers) {
      if (peer.emote && peer.emote.timer > 0) peer.emote.timer -= dt;
      updateCoopPeerShootingSingle(state, peer, dt);
    }
  } else if (state.coopPeer) {
    if (state.coopPeer.emote && state.coopPeer.emote.timer > 0) state.coopPeer.emote.timer -= dt;
    updateCoopPeerShooting(state, dt);
  }

  // Ability effects
  updateOrbitals(state, dt);
  updateAura(state, dt);
  updateRegen(state, dt);
  updateFrostNova(state, dt);
  updateMissiles(state, dt);
  updateLightningRing(state, dt);
  updateIonBeam(state, dt);
  updateShockwave(state, dt);
  updateSentries(state, dt);
  
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

  // Update XP orbs - only host processes collection (guest gets synced values)
  const magnetR = state.abilities.magnetRadius;
  const peer = state.coopPeer;
  const allPeers = state.coopPeers.length > 0 ? state.coopPeers : (peer ? [peer] : []);
  state.xpOrbs = state.xpOrbs.filter(orb => {
    orb.lifetime -= dt;
    if (orb.lifetime <= 0) return false;
    // Magnet: attract to nearest player
    const dxP = p.pos.x - orb.pos.x;
    const dyP = p.pos.y - orb.pos.y;
    const dP = Math.hypot(dxP, dyP);
    
    let closestDx = dxP, closestDy = dyP, closestD = dP;
    for (const cp of allPeers) {
      if (!cp.alive) continue;
      const dxPeer = cp.pos.x - orb.pos.x;
      const dyPeer = cp.pos.y - orb.pos.y;
      const dPeer = Math.hypot(dxPeer, dyPeer);
      if (dPeer < closestD) {
        closestDx = dxPeer; closestDy = dyPeer; closestD = dPeer;
      }
    }
    
    if (closestD < magnetR) {
      const pullSpeed = 300 * (1 - closestD / magnetR) + 100;
      orb.pos.x += (closestDx / closestD) * pullSpeed * dt;
      orb.pos.y += (closestDy / closestD) * pullSpeed * dt;
    }
    orb.pos.x += orb.vel.x * dt;
    orb.pos.y += orb.vel.y * dt;
    orb.vel.x *= 0.95;
    orb.vel.y *= 0.95;
    // Only host collects XP (guest receives synced XP via game_sync)
    if (state.isHost !== false) {
      // Collect by local player
      if (dP < p.radius + orb.radius + 5) {
        addXp(state, orb.value);
        return false;
      }
      // Collect by peer (host adds XP for both)
      if (peer && peer.alive) {
        const dPeer = Math.hypot(peer.pos.x - orb.pos.x, peer.pos.y - orb.pos.y);
        if (dPeer < 12 + orb.radius + 5) {
          addXp(state, orb.value);
          return false;
        }
      }
    }
    return true;
  });

  // Level up check (only host triggers level up; guest receives it via broadcast)
  if (state.isHost !== false && state.xp >= state.xpToNext && state.screen === 'playing') {
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
  // Death wave: only death_hunters
  if (state.deathWave) {
    const enemy = createEnemy('death_hunter', state.wave);
    applyDifficultyToEnemy(state, enemy);
    enemy.speed *= 1 + (state.wave - 30) * 0.05;
    enemy.baseSpeed = enemy.speed;
    state.enemies.push(enemy);
    return;
  }
  
  const isMegaBoss = state.wave === 15 || state.wave === 30;
  const isBossWave = state.wave % BOSS_WAVE_INTERVAL === 0;
  const map = ALL_MAPS[state.mapId];

  // Mega-boss spawn (last enemy of the wave)
  if (isMegaBoss && state.waveEnemiesRemaining === 1) {
    const bossType: EnemyType = state.wave === 15 ? 'archon' : 'oblivion';
    const boss = createEnemy(bossType, state.wave);
    applyDifficultyToEnemy(state, boss);
    state.enemies.push(boss);
    setBossMusic(bossType);
    return;
  }

  // Map-specific boss on boss waves
  if (isBossWave && !isMegaBoss && state.waveEnemiesRemaining === 1) {
    const bossType = map?.bossEnemy || (['mothership', 'vortex', 'colossus'] as EnemyType[])[Math.floor(Math.random() * 3)];
    const boss = createEnemy(bossType, state.wave);
    applyDifficultyToEnemy(state, boss);
    state.enemies.push(boss);
    setBossMusic(bossType);
    return;
  }

  // Regular enemies
  const types: EnemyType[] = ['drone'];
  if (state.wave >= 2) types.push('splitter');
  if (state.wave >= 3) types.push('dasher');
  if (state.wave >= 5) types.push('tank');

  // Add map-specific enemies from wave 2+
  const mapEnemies = map?.regularEnemies || [];
  if (state.wave >= 2 && mapEnemies.length > 0) {
    types.push(...mapEnemies);
  }

  const type = types[Math.floor(Math.random() * types.length)];
  const enemy = createEnemy(type, state.wave);
  applyDifficultyToEnemy(state, enemy);
  state.enemies.push(enemy);
}

function updateEnemies(state: GameState, dt: number) {
  const p = state.player;
  const peer = state.coopPeer;
  const allPeers = state.coopPeers.length > 0 ? state.coopPeers : (peer ? [peer] : []);

  for (const e of state.enemies) {
    if (!e.alive) {
      e.flashTimer -= dt;
      continue;
    }

    // Apply temporary slows (e.g. Frost Nova)
    const base = e.baseSpeed ?? e.speed;
    e.baseSpeed = base;
    if (e.slowUntil && Date.now() < e.slowUntil) {
      e.speed = base * 0.5;
    } else {
      e.speed = base;
      e.slowUntil = undefined;
    }

    e.flashTimer = Math.max(0, e.flashTimer - dt);
    e.attackTimer = Math.max(0, e.attackTimer - dt);

    // Find nearest player target (host player or any coop peer)
    let targetX = p.pos.x, targetY = p.pos.y;
    let minDist = Math.hypot(p.pos.x - e.pos.x, p.pos.y - e.pos.y);
    for (const cp of allPeers) {
      if (!cp.alive) continue;
      const d = Math.hypot(cp.pos.x - e.pos.x, cp.pos.y - e.pos.y);
      if (d < minDist) {
        minDist = d;
        targetX = cp.pos.x;
        targetY = cp.pos.y;
      }
    }

    const dx = targetX - e.pos.x;
    const dy = targetY - e.pos.y;
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
    } else if (e.type === 'fire_elemental') {
      // Fire Elemental: approaches and periodically shoots fire rings
      if (d > 120) {
        e.pos.x += (dx / d) * e.speed * dt;
        e.pos.y += (dy / d) * e.speed * dt;
      }
      if (!e.shootTimer) e.shootTimer = 3;
      e.shootTimer -= dt;
      if (e.shootTimer <= 0) {
        e.shootTimer = 2.5 + Math.random();
        // Fire ring - 8 fireballs
        for (let i = 0; i < 8; i++) {
          const a = (i / 8) * Math.PI * 2;
          state.projectiles.push({
            pos: { x: e.pos.x, y: e.pos.y },
            vel: { x: Math.cos(a) * 150, y: Math.sin(a) * 150 },
            radius: 4, alive: true, damage: e.damage, fromPlayer: false,
            lifetime: 1.5, color: '#ff6b00',
          });
        }
        state.particles.push(...createParticles(e.pos, '#ff6b00', 10, 100, 3));
      }
      // Fire aura particles
      if (Math.random() < 0.3) {
        state.particles.push(...createParticles(e.pos, '#ff4500', 1, 40, 2));
      }
    } else if (e.type === 'void_ghost') {
      // Void Ghost: teleports periodically, phases through obstacles
      if (!e.dashTimer) e.dashTimer = 2;
      e.dashTimer -= dt;
      if (e.dashTimer <= 0) {
        e.dashTimer = 2.5 + Math.random() * 2;
        // Teleport near player
        const teleAngle = Math.random() * Math.PI * 2;
        const teleDist = 80 + Math.random() * 100;
        state.particles.push(...createParticles(e.pos, '#9040ff', 12, 120, 3));
        e.pos.x = p.pos.x + Math.cos(teleAngle) * teleDist;
        e.pos.y = p.pos.y + Math.sin(teleAngle) * teleDist;
        state.particles.push(...createParticles(e.pos, '#9040ff', 12, 120, 3));
      }
      // Slowly drift toward player
      if (d > 0) {
        e.pos.x += (dx / d) * e.speed * 0.5 * dt;
        e.pos.y += (dy / d) * e.speed * 0.5 * dt;
      }
      // Ghost particles
      if (Math.random() < 0.2) {
        state.particles.push(...createParticles(e.pos, '#9040ff', 1, 30, 1.5));
      }
    } else if (e.type === 'crystal_golem') {
      // Crystal Golem: slow tank that reflects projectiles on death
      if (d > 0) {
        e.pos.x += (dx / d) * e.speed * dt;
        e.pos.y += (dy / d) * e.speed * dt;
      }
      // Ground slam when close
      if (!e.shootTimer) e.shootTimer = 3;
      e.shootTimer -= dt;
      if (e.shootTimer <= 0 && d < 150) {
        e.shootTimer = 3;
        // Shockwave
        for (let i = 0; i < 12; i++) {
          const a = (i / 12) * Math.PI * 2;
          state.projectiles.push({
            pos: { x: e.pos.x, y: e.pos.y },
            vel: { x: Math.cos(a) * 120, y: Math.sin(a) * 120 },
            radius: 6, alive: true, damage: e.damage, fromPlayer: false,
            lifetime: 1, color: '#00e5ff',
          });
        }
        state.shakeTimer = 0.15;
        state.shakeIntensity = 4;
        state.particles.push(...createParticles(e.pos, '#00e5ff', 15, 150, 4));
      }
    } else if (e.type === 'ice_walker') {
      // Ice Walker: slow advance, periodically freezes nearby then shatters
      if (d > 0) {
        e.pos.x += (dx / d) * e.speed * dt;
        e.pos.y += (dy / d) * e.speed * dt;
      }
      if (!e.shootTimer) e.shootTimer = 3;
      e.shootTimer -= dt;
      if (e.shootTimer <= 0 && d < 200) {
        e.shootTimer = 3 + Math.random();
        for (let i = 0; i < 8; i++) {
          const a = (i / 8) * Math.PI * 2;
          state.projectiles.push({ pos: { x: e.pos.x, y: e.pos.y }, vel: { x: Math.cos(a) * 100, y: Math.sin(a) * 100 }, radius: 4, alive: true, damage: e.damage, fromPlayer: false, lifetime: 1.5, color: '#88ddff' });
        }
        state.particles.push(...createParticles(e.pos, '#88ddff', 8, 80, 2));
      }
    } else if (e.type === 'nebula_shade') {
      // Nebula Shade: fast, weaves erratically
      const weave = Math.sin(Date.now() * 0.008 + e.pos.y * 0.05) * 80;
      if (d > 0) {
        const perpX = -dy / d;
        const perpY = dx / d;
        e.pos.x += ((dx / d) * e.speed + perpX * weave) * dt;
        e.pos.y += ((dy / d) * e.speed + perpY * weave) * dt;
      }
      if (Math.random() < 0.15) state.particles.push(...createParticles(e.pos, '#9966ff', 1, 30, 1.5));
    } else if (e.type === 'acid_slime') {
      // Acid Slime: slow, leaves acid trail
      if (d > 0) {
        e.pos.x += (dx / d) * e.speed * dt;
        e.pos.y += (dy / d) * e.speed * dt;
      }
      if (Math.random() < 0.1) {
        state.flameZones.push({ x: e.pos.x, y: e.pos.y, damage: e.damage * 0.3, lifetime: 4 });
      }
    } else if (e.type === 'storm_drone') {
      // Storm Drone: very fast, orbits then dashes
      if (!e.dashState) e.dashState = 'tracking';
      if (!e.dashTimer) e.dashTimer = 0;
      e.dashTimer -= dt;
      if (e.dashState === 'tracking') {
        if (d > 60) {
          const orbitAngle = Math.atan2(dy, dx) + Math.PI / 2;
          e.pos.x += Math.cos(orbitAngle) * e.speed * dt;
          e.pos.y += Math.sin(orbitAngle) * e.speed * dt;
          e.pos.x += (dx / d) * e.speed * 0.2 * dt;
          e.pos.y += (dy / d) * e.speed * 0.2 * dt;
        }
        if (e.dashTimer <= 0 && d < 250) {
          e.dashState = 'dashing'; e.dashTimer = 0.3; e.dashAngle = Math.atan2(dy, dx);
        }
        if (e.dashTimer <= 0) e.dashTimer = 0.8 + Math.random() * 0.5;
      } else if (e.dashState === 'dashing') {
        e.pos.x += Math.cos(e.dashAngle!) * e.speed * 3 * dt;
        e.pos.y += Math.sin(e.dashAngle!) * e.speed * 3 * dt;
        if (e.dashTimer <= 0) { e.dashState = 'cooldown'; e.dashTimer = 0.5; }
      } else {
        if (e.dashTimer <= 0) { e.dashState = 'tracking'; e.dashTimer = 0.5; }
      }
    } else if (e.type === 'undead_risen') {
      // Undead: slow shamble toward player
      if (d > 0) {
        e.pos.x += (dx / d) * e.speed * dt;
        e.pos.y += (dy / d) * e.speed * dt;
      }
    } else if (e.type === 'warp_drone') {
      // Warp Drone: teleports around, shoots at player
      if (!e.dashTimer) e.dashTimer = 1.5;
      e.dashTimer -= dt;
      if (e.dashTimer <= 0) {
        e.dashTimer = 1.5 + Math.random() * 1.5;
        const tA = Math.random() * Math.PI * 2;
        const tD = 60 + Math.random() * 120;
        state.particles.push(...createParticles(e.pos, '#ff44ff', 8, 100, 2));
        e.pos.x = targetX + Math.cos(tA) * tD;
        e.pos.y = targetY + Math.sin(tA) * tD;
        state.particles.push(...createParticles(e.pos, '#ff44ff', 8, 100, 2));
        // Shoot on arrival
        const shootA = Math.atan2(targetY - e.pos.y, targetX - e.pos.x);
        state.projectiles.push({ pos: { x: e.pos.x, y: e.pos.y }, vel: { x: Math.cos(shootA) * 200, y: Math.sin(shootA) * 200 }, radius: 4, alive: true, damage: e.damage, fromPlayer: false, lifetime: 2, color: '#ff44ff' });
      }
      if (d > 0) {
        e.pos.x += (dx / d) * e.speed * 0.3 * dt;
        e.pos.y += (dy / d) * e.speed * 0.3 * dt;
      }
    } else if (e.type === 'prism_shard') {
      // Prism Shard: slow, reflects projectiles (handled in hazard-like way)
      if (d > 0) {
        e.pos.x += (dx / d) * e.speed * dt;
        e.pos.y += (dy / d) * e.speed * dt;
      }
    } else if (e.type === 'magma_wurm') {
      // Magma Wurm: charges then burrows, shoots fire on surface
      if (!e.dashState) e.dashState = 'tracking';
      if (!e.dashTimer) e.dashTimer = 0;
      e.dashTimer -= dt;
      if (e.dashState === 'tracking') {
        if (d > 0) { e.pos.x += (dx / d) * e.speed * dt; e.pos.y += (dy / d) * e.speed * dt; }
        if (e.dashTimer <= 0 && d < 200) {
          e.dashState = 'dashing'; e.dashTimer = 0.5; e.dashAngle = Math.atan2(dy, dx);
        }
        if (e.dashTimer <= 0) e.dashTimer = 2;
      } else if (e.dashState === 'dashing') {
        e.pos.x += Math.cos(e.dashAngle!) * e.speed * 2.5 * dt;
        e.pos.y += Math.sin(e.dashAngle!) * e.speed * 2.5 * dt;
        state.flameZones.push({ x: e.pos.x, y: e.pos.y, damage: e.damage * 0.4, lifetime: 3 });
        if (e.dashTimer <= 0) { e.dashState = 'cooldown'; e.dashTimer = 1.5; }
      } else {
        if (e.dashTimer <= 0) { e.dashState = 'tracking'; e.dashTimer = 1; }
      }
    } else if (e.type === 'quantum_shifter') {
      // Quantum Shifter: very fast, teleports on hit, unpredictable movement
      const zigzag = Math.sin(Date.now() * 0.01 + e.pos.x * 0.1) * 100;
      if (d > 0) {
        const perpX = -dy / d; const perpY = dx / d;
        e.pos.x += ((dx / d) * e.speed + perpX * zigzag) * dt;
        e.pos.y += ((dy / d) * e.speed + perpY * zigzag) * dt;
      }
    } else if (e.type === 'abyss_horror') {
      // Abyss Horror: slow approach, periodic tentacle burst
      if (d > 0) {
        e.pos.x += (dx / d) * e.speed * dt;
        e.pos.y += (dy / d) * e.speed * dt;
      }
      if (!e.shootTimer) e.shootTimer = 3;
      e.shootTimer -= dt;
      if (e.shootTimer <= 0 && d < 300) {
        e.shootTimer = 2.5 + Math.random();
        for (let i = 0; i < 10; i++) {
          const a = (i / 10) * Math.PI * 2;
          state.projectiles.push({ pos: { x: e.pos.x, y: e.pos.y }, vel: { x: Math.cos(a) * 120, y: Math.sin(a) * 120 }, radius: 5, alive: true, damage: e.damage * 0.5, fromPlayer: false, lifetime: 1.5, color: '#440088' });
        }
        state.particles.push(...createParticles(e.pos, '#440088', 12, 100, 3));
      }
    } else if (e.type === 'death_hunter') {
      // Death Hunter: extremely fast, homes directly
      if (d > 0) {
        e.pos.x += (dx / d) * e.speed * dt;
        e.pos.y += (dy / d) * e.speed * dt;
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

    // Contact damage to local player
    if (dist(e.pos, p.pos) < e.radius + p.radius) {
      if (e.attackTimer <= 0) {
        damagePlayer(state, e.damage);
        e.attackTimer = e.attackCooldown;
      }
    }
    // Contact damage to peer (host handles peer damage)
    if (peer && peer.alive && dist(e.pos, peer.pos) < e.radius + 12) {
      // We can't directly damage peer, but we apply contact via broadcast
      // For now, enemies take contact damage priority from nearest
    }
  }
}

// Host simulates peer shooting (legacy single peer)
function updateCoopPeerShooting(state: GameState, dt: number) {
  const peer = state.coopPeer;
  if (!peer || !peer.alive || !peer.shooting) return;
  updateCoopPeerShootingSingle(state, peer, dt);
}

// Host simulates a single peer shooting
function updateCoopPeerShootingSingle(state: GameState, peer: { pos: { x: number; y: number }; angle: number; alive: boolean; shipClass: string; shooting: boolean; attackTimer: number; attackCooldown: number; damage: number }, dt: number) {
  if (!peer.alive || !peer.shooting) return;
  
  peer.attackTimer = Math.max(0, peer.attackTimer - dt);
  if (peer.attackTimer > 0) return;
  peer.attackTimer = peer.attackCooldown;
  
  const color = COLORS[peer.shipClass] || COLORS.phantom;
  
  // Melee ships - damage nearby enemies directly
  if (peer.shipClass === 'titan' || peer.shipClass === 'juggernaut' || peer.shipClass === 'leviathan') {
    for (const e of state.enemies) {
      if (!e.alive) continue;
      const d = dist(peer.pos, e.pos);
      if (d > WARRIOR_ATTACK_RANGE + e.radius) continue;
      const angleToEnemy = Math.atan2(e.pos.y - peer.pos.y, e.pos.x - peer.pos.x);
      let angleDiff = Math.abs(angleToEnemy - peer.angle);
      if (angleDiff > Math.PI) angleDiff = Math.PI * 2 - angleDiff;
      if (angleDiff < 1.0) {
        damageEnemy(state, e, peer.damage);
      }
    }
    return;
  }
  
  const speedMult = peer.shipClass === 'interceptor' ? 1.3 : peer.shipClass === 'spectre' ? 1.5 : 1;
  
  if (peer.shipClass === 'valkyrie') {
    const vAngles = [-0.08, 0.08];
    for (const offset of vAngles) {
      state.projectiles.push(createProjectile(peer.pos, peer.angle + offset, peer.damage, true, color, 1.2));
    }
  } else {
    state.projectiles.push(createProjectile(peer.pos, peer.angle, peer.damage, true, color, speedMult));
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
    state.projectiles.push({
      pos: { x: boss.pos.x, y: boss.pos.y },
      vel: { x: Math.cos(angle) * 350, y: Math.sin(angle) * 350 },
      radius: 12, alive: true, damage: boss.damage, fromPlayer: false,
      lifetime: 2, color: '#ffffff',
    });
    state.shakeTimer = 0.3;
    state.shakeIntensity = 8;
  } else if (boss.type === 'lava_dragon') {
    // Fire breath cone + lava pools
    for (let i = -5; i <= 5; i++) {
      state.projectiles.push({
        pos: { x: boss.pos.x, y: boss.pos.y },
        vel: { x: Math.cos(angle + i * 0.08) * (250 + Math.abs(i) * 15), y: Math.sin(angle + i * 0.08) * (250 + Math.abs(i) * 15) },
        radius: 7, alive: true, damage: boss.damage * 0.6, fromPlayer: false,
        lifetime: 1.8, color: '#ff4500',
      });
    }
    // Leave lava at current position
    state.particles.push(...createParticles(boss.pos, '#ff6b00', 25, 200, 4));
    state.shakeTimer = 0.2;
    state.shakeIntensity = 6;
  } else if (boss.type === 'void_lord') {
    // Teleport + void explosions at random spots near player
    for (let i = 0; i < 5; i++) {
      const rAngle = Math.random() * Math.PI * 2;
      const rDist = 40 + Math.random() * 120;
      const tx = p.pos.x + Math.cos(rAngle) * rDist;
      const ty = p.pos.y + Math.sin(rAngle) * rDist;
      for (let j = 0; j < 8; j++) {
        const a = (j / 8) * Math.PI * 2;
        state.projectiles.push({
          pos: { x: tx, y: ty },
          vel: { x: Math.cos(a) * 130, y: Math.sin(a) * 130 },
          radius: 5, alive: true, damage: boss.damage * 0.4, fromPlayer: false,
          lifetime: 1.2, color: '#9040ff',
        });
      }
      state.particles.push(...createParticles({ x: tx, y: ty }, '#6000c0', 12, 120, 3));
    }
    // Teleport boss
    const telAngle = Math.random() * Math.PI * 2;
    state.particles.push(...createParticles(boss.pos, '#9040ff', 20, 150, 3));
    boss.pos.x = p.pos.x + Math.cos(telAngle) * 200;
    boss.pos.y = p.pos.y + Math.sin(telAngle) * 200;
    state.particles.push(...createParticles(boss.pos, '#9040ff', 20, 150, 3));
  } else if (boss.type === 'crystal_giant') {
    // Giant crystal shockwave + crystal shards that persist
    for (let i = 0; i < 16; i++) {
      const a = (Math.PI * 2 / 16) * i;
      state.projectiles.push({
        pos: { x: boss.pos.x, y: boss.pos.y },
        vel: { x: Math.cos(a) * 140, y: Math.sin(a) * 140 },
        radius: 10, alive: true, damage: boss.damage * 0.5, fromPlayer: false,
        lifetime: 2, color: '#00ffcc',
      });
    }
    // Heavy aimed crystal lance
    for (let i = -1; i <= 1; i++) {
      state.projectiles.push({
        pos: { x: boss.pos.x, y: boss.pos.y },
        vel: { x: Math.cos(angle + i * 0.1) * 300, y: Math.sin(angle + i * 0.1) * 300 },
        radius: 14, alive: true, damage: boss.damage, fromPlayer: false,
        lifetime: 2.5, color: '#00e5ff',
      });
    }
    state.shakeTimer = 0.4;
    state.shakeIntensity = 10;
    state.particles.push(...createParticles(boss.pos, '#00ffcc', 30, 250, 5));
  } else if (boss.type === 'frost_titan') {
    // Ice shards + freeze zone
    for (let i = 0; i < 16; i++) {
      const a = (Math.PI * 2 / 16) * i;
      state.projectiles.push({ pos: { x: boss.pos.x, y: boss.pos.y }, vel: { x: Math.cos(a) * 160, y: Math.sin(a) * 160 }, radius: 7, alive: true, damage: boss.damage * 0.5, fromPlayer: false, lifetime: 2, color: '#88ddff' });
    }
    state.particles.push(...createParticles(boss.pos, '#88ddff', 25, 200, 4));
    state.shakeTimer = 0.3; state.shakeIntensity = 8;
  } else if (boss.type === 'cosmic_horror') {
    // Tentacle burst from multiple points
    for (let i = 0; i < 6; i++) {
      const rA = Math.random() * Math.PI * 2;
      const rD = 50 + Math.random() * 100;
      const tx = p.pos.x + Math.cos(rA) * rD;
      const ty = p.pos.y + Math.sin(rA) * rD;
      for (let j = 0; j < 6; j++) {
        const a = (j / 6) * Math.PI * 2;
        state.projectiles.push({ pos: { x: tx, y: ty }, vel: { x: Math.cos(a) * 140, y: Math.sin(a) * 140 }, radius: 5, alive: true, damage: boss.damage * 0.4, fromPlayer: false, lifetime: 1.5, color: '#6600cc' });
      }
    }
    state.particles.push(...createParticles(boss.pos, '#9966ff', 30, 250, 5));
    state.shakeTimer = 0.4; state.shakeIntensity = 10;
  } else if (boss.type === 'plague_lord') {
    // Poison clouds + acid spray
    for (let i = 0; i < 20; i++) {
      const a = (Math.PI * 2 / 20) * i;
      const spd = 100 + Math.random() * 80;
      state.projectiles.push({ pos: { x: boss.pos.x, y: boss.pos.y }, vel: { x: Math.cos(a) * spd, y: Math.sin(a) * spd }, radius: 6, alive: true, damage: boss.damage * 0.3, fromPlayer: false, lifetime: 3, color: '#66ff00' });
    }
    state.particles.push(...createParticles(boss.pos, '#88ff00', 25, 180, 4));
  } else if (boss.type === 'thunder_god') {
    // Lightning bolts + aimed thunder
    for (let i = 0; i < 8; i++) {
      const a = angle + (i - 3.5) * 0.2;
      state.projectiles.push({ pos: { x: boss.pos.x, y: boss.pos.y }, vel: { x: Math.cos(a) * 400, y: Math.sin(a) * 400 }, radius: 4, alive: true, damage: boss.damage * 0.6, fromPlayer: false, lifetime: 1.5, color: '#ffff00' });
    }
    for (let i = 0; i < 12; i++) {
      const a = (Math.PI * 2 / 12) * i + Date.now() * 0.002;
      state.projectiles.push({ pos: { x: boss.pos.x, y: boss.pos.y }, vel: { x: Math.cos(a) * 220, y: Math.sin(a) * 220 }, radius: 5, alive: true, damage: boss.damage * 0.4, fromPlayer: false, lifetime: 2, color: '#ffff44' });
    }
    state.shakeTimer = 0.3; state.shakeIntensity = 10;
  } else if (boss.type === 'lich_king') {
    // Summon undead + death beam
    for (let i = 0; i < 3; i++) {
      const d = createEnemy('undead_risen', state.wave);
      d.pos = { x: boss.pos.x + (Math.random() - 0.5) * 80, y: boss.pos.y + (Math.random() - 0.5) * 80 };
      state.enemies.push(d);
    }
    for (let i = -2; i <= 2; i++) {
      state.projectiles.push({ pos: { x: boss.pos.x, y: boss.pos.y }, vel: { x: Math.cos(angle + i * 0.1) * 320, y: Math.sin(angle + i * 0.1) * 320 }, radius: 10, alive: true, damage: boss.damage * 0.7, fromPlayer: false, lifetime: 2, color: '#44ff88' });
    }
    state.particles.push(...createParticles(boss.pos, '#668866', 20, 180, 4));
  } else if (boss.type === 'nexus_guardian') {
    // NEXUS GUARDIAN: Portal network — opens warp rifts that shoot multi-directional burst
    const phase = (boss.bossPhase || 0) % 4;
    if (phase === 0) {
      // Rotating warp portal ring — 4 portals at cardinal directions that each shoot 5 bullets
      for (let portal = 0; portal < 4; portal++) {
        const portalA = (Math.PI / 2) * portal + Date.now() * 0.0008;
        const px2 = boss.pos.x + Math.cos(portalA) * 120;
        const py2 = boss.pos.y + Math.sin(portalA) * 120;
        state.particles.push(...createParticles({ x: px2, y: py2 }, '#ff44ff', 8, 80, 2));
        for (let i = 0; i < 5; i++) {
          const a = (Math.PI * 2 / 5) * i + portalA;
          state.projectiles.push({ pos: { x: px2, y: py2 }, vel: { x: Math.cos(a) * 200, y: Math.sin(a) * 200 }, radius: 5, alive: true, damage: boss.damage * 0.4, fromPlayer: false, lifetime: 2, color: '#ff00ff' });
        }
      }
    } else if (phase === 1) {
      // Boss teleports to a random location and fires a dense aimed cone
      state.particles.push(...createParticles(boss.pos, '#ff44ff', 20, 150, 3));
      boss.pos.x = p.pos.x + (Math.random() - 0.5) * 300;
      boss.pos.y = p.pos.y + (Math.random() - 0.5) * 300;
      boss.pos.x = Math.max(100, Math.min(ARENA_W - 100, boss.pos.x));
      boss.pos.y = Math.max(100, Math.min(ARENA_H - 100, boss.pos.y));
      state.particles.push(...createParticles(boss.pos, '#ff44ff', 20, 150, 3));
      for (let i = -6; i <= 6; i++) {
        state.projectiles.push({ pos: { x: boss.pos.x, y: boss.pos.y }, vel: { x: Math.cos(angle + i * 0.07) * 340, y: Math.sin(angle + i * 0.07) * 340 }, radius: 8, alive: true, damage: boss.damage * 0.6, fromPlayer: false, lifetime: 2, color: '#ff00cc' });
      }
    } else if (phase === 2) {
      // Expanding void ring — 3 rings at different speeds
      for (let ring = 0; ring < 3; ring++) {
        const spd = 120 + ring * 80;
        const count = 10 + ring * 4;
        const offset = ring * (Math.PI / count);
        for (let i = 0; i < count; i++) {
          const a = (Math.PI * 2 / count) * i + offset;
          state.projectiles.push({ pos: { x: boss.pos.x, y: boss.pos.y }, vel: { x: Math.cos(a) * spd, y: Math.sin(a) * spd }, radius: 6 - ring, alive: true, damage: boss.damage * 0.35, fromPlayer: false, lifetime: 3, color: '#cc00ff' });
        }
      }
    } else {
      // Spawn warp drones + laser cross
      for (let i = 0; i < 4; i++) {
        const wd = createEnemy('warp_drone', Math.max(1, state.wave - 1));
        wd.pos = { x: boss.pos.x + Math.cos((i / 4) * Math.PI * 2) * 60, y: boss.pos.y + Math.sin((i / 4) * Math.PI * 2) * 60 };
        state.enemies.push(wd);
      }
      for (let i = 0; i < 4; i++) {
        const a = (Math.PI / 2) * i;
        for (let j = 0; j < 3; j++) {
          state.projectiles.push({ pos: { x: boss.pos.x, y: boss.pos.y }, vel: { x: Math.cos(a + j * 0.05) * 280, y: Math.sin(a + j * 0.05) * 280 }, radius: 9, alive: true, damage: boss.damage * 0.55, fromPlayer: false, lifetime: 2.5, color: '#ffffff' });
        }
      }
    }
    boss.bossPhase = (boss.bossPhase || 0) + 1;
    state.shakeTimer = 0.3; state.shakeIntensity = 10;
    state.particles.push(...createParticles(boss.pos, '#ff00ff', 25, 220, 4));
  } else if (boss.type === 'aurora_phoenix') {
    // AURORA PHOENIX: Prism beams + rebirth mechanics
    const phase = (boss.bossPhase || 0) % 4;
    if (phase === 0) {
      // Rainbow prism burst — each wave different color/direction
      const colors = ['#ff66aa', '#ff88ff', '#aa66ff', '#66aaff', '#66ffaa', '#ffff66'];
      for (let c = 0; c < colors.length; c++) {
        const baseA = angle + (c / colors.length) * Math.PI * 0.5;
        for (let i = -2; i <= 2; i++) {
          state.projectiles.push({ pos: { x: boss.pos.x, y: boss.pos.y }, vel: { x: Math.cos(baseA + i * 0.12) * (250 + c * 20), y: Math.sin(baseA + i * 0.12) * (250 + c * 20) }, radius: 5, alive: true, damage: boss.damage * 0.35, fromPlayer: false, lifetime: 2.5, color: colors[c] });
        }
      }
    } else if (phase === 1) {
      // Fire nova + dive toward player
      for (let i = 0; i < 24; i++) {
        const a = (Math.PI * 2 / 24) * i;
        state.projectiles.push({ pos: { x: boss.pos.x, y: boss.pos.y }, vel: { x: Math.cos(a) * 180, y: Math.sin(a) * 180 }, radius: 6, alive: true, damage: boss.damage * 0.4, fromPlayer: false, lifetime: 2, color: '#ff88ff' });
      }
      // Dash toward player
      boss.pos.x += (p.pos.x - boss.pos.x) * 0.4;
      boss.pos.y += (p.pos.y - boss.pos.y) * 0.4;
      state.particles.push(...createParticles(boss.pos, '#ff66aa', 30, 300, 5));
    } else if (phase === 2) {
      // Spiral of mixed color shots
      const now2 = Date.now() * 0.003;
      for (let i = 0; i < 3; i++) {
        for (let j = 0; j < 12; j++) {
          const a = (Math.PI * 2 / 12) * j + now2 + i * 1.0;
          const spd = 160 + i * 50;
          const clr = i === 0 ? '#ff66aa' : i === 1 ? '#aa66ff' : '#66ffaa';
          state.projectiles.push({ pos: { x: boss.pos.x, y: boss.pos.y }, vel: { x: Math.cos(a) * spd, y: Math.sin(a) * spd }, radius: 5, alive: true, damage: boss.damage * 0.3, fromPlayer: false, lifetime: 3, color: clr });
        }
      }
    } else {
      // Rebirth: teleport center, spawn prism_shards, fire cross lance
      state.particles.push(...createParticles(boss.pos, '#ffffff', 40, 300, 6));
      boss.pos.x = ARENA_W / 2 + (Math.random() - 0.5) * 200;
      boss.pos.y = ARENA_H / 2 + (Math.random() - 0.5) * 200;
      for (let i = 0; i < 3; i++) {
        const ps = createEnemy('prism_shard', state.wave);
        ps.pos = { x: boss.pos.x + (Math.random() - 0.5) * 100, y: boss.pos.y + (Math.random() - 0.5) * 100 };
        state.enemies.push(ps);
      }
      state.particles.push(...createParticles(boss.pos, '#ff88ff', 50, 400, 7));
      for (let i = 0; i < 8; i++) {
        const a = (Math.PI / 4) * i;
        for (let j = 0; j < 4; j++) {
          state.projectiles.push({ pos: { x: boss.pos.x, y: boss.pos.y }, vel: { x: Math.cos(a + j * 0.04) * 360, y: Math.sin(a + j * 0.04) * 360 }, radius: 10, alive: true, damage: boss.damage * 0.65, fromPlayer: false, lifetime: 2, color: '#ffffff' });
        }
      }
    }
    boss.bossPhase = (boss.bossPhase || 0) + 1;
    state.shakeTimer = 0.4; state.shakeIntensity = 12;
    state.particles.push(...createParticles(boss.pos, '#ff66aa', 30, 280, 5));
  } else if (boss.type === 'core_titan') {
    // CORE TITAN: Magma eruptions + armor phases
    const phase = (boss.bossPhase || 0) % 4;
    if (phase === 0) {
      // Lava eruption columns — 5 locations around arena
      for (let i = 0; i < 5; i++) {
        const rx = 150 + Math.random() * (ARENA_W - 300);
        const ry = 150 + Math.random() * (ARENA_H - 300);
        state.particles.push(...createParticles({ x: rx, y: ry }, '#ff4400', 20, 200, 5));
        for (let j = 0; j < 8; j++) {
          const a = (Math.PI * 2 / 8) * j;
          state.projectiles.push({ pos: { x: rx, y: ry }, vel: { x: Math.cos(a) * 160, y: Math.sin(a) * 160 }, radius: 7, alive: true, damage: boss.damage * 0.45, fromPlayer: false, lifetime: 2, color: '#ff6600' });
        }
      }
      state.shakeTimer = 0.5; state.shakeIntensity = 15;
    } else if (phase === 1) {
      // Armor barrage — heavy slow aimed shots
      for (let i = -3; i <= 3; i++) {
        state.projectiles.push({ pos: { x: boss.pos.x, y: boss.pos.y }, vel: { x: Math.cos(angle + i * 0.1) * 260, y: Math.sin(angle + i * 0.1) * 260 }, radius: 14, alive: true, damage: boss.damage * 0.85, fromPlayer: false, lifetime: 2.5, color: '#ff6600' });
      }
      // Lava trail at boss position
      state.flameZones.push({ x: boss.pos.x, y: boss.pos.y, damage: boss.damage * 0.3, lifetime: 5 });
    } else if (phase === 2) {
      // Magma ring — slow close-range explosion
      for (let i = 0; i < 20; i++) {
        const a = (Math.PI * 2 / 20) * i;
        state.projectiles.push({ pos: { x: boss.pos.x, y: boss.pos.y }, vel: { x: Math.cos(a) * 130, y: Math.sin(a) * 130 }, radius: 9, alive: true, damage: boss.damage * 0.5, fromPlayer: false, lifetime: 2.5, color: '#ff4400' });
      }
      // Spawn magma wurms
      for (let i = 0; i < 2; i++) {
        const mw = createEnemy('magma_wurm', Math.max(1, state.wave - 2));
        mw.pos = { x: boss.pos.x + (Math.random() - 0.5) * 80, y: boss.pos.y + (Math.random() - 0.5) * 80 };
        state.enemies.push(mw);
      }
    } else {
      // Meltdown: global lava flood + charge toward player
      for (let i = 0; i < 8; i++) {
        const rx2 = 100 + Math.random() * (ARENA_W - 200);
        const ry2 = 100 + Math.random() * (ARENA_H - 200);
        state.flameZones.push({ x: rx2, y: ry2, damage: boss.damage * 0.25, lifetime: 6 });
        state.particles.push(...createParticles({ x: rx2, y: ry2 }, '#ff4400', 10, 100, 3));
      }
      boss.pos.x += (p.pos.x - boss.pos.x) * 0.5;
      boss.pos.y += (p.pos.y - boss.pos.y) * 0.5;
      state.particles.push(...createParticles(boss.pos, '#ff6600', 40, 350, 7));
      state.shakeTimer = 0.6; state.shakeIntensity = 18;
    }
    boss.bossPhase = (boss.bossPhase || 0) + 1;
    state.particles.push(...createParticles(boss.pos, '#ff4400', 30, 280, 5));
  } else if (boss.type === 'reality_breaker') {
    // REALITY BREAKER: Quantum phase attacks — projectiles phase shift direction mid-air
    const phase = (boss.bossPhase || 0) % 4;
    if (phase === 0) {
      // Quantum scatter — shots curve unpredictably (approximated by multiple angles)
      for (let i = 0; i < 18; i++) {
        const a = (Math.PI * 2 / 18) * i + Date.now() * 0.0015;
        const spd = 140 + Math.sin(i * 0.7) * 60;
        state.projectiles.push({ pos: { x: boss.pos.x, y: boss.pos.y }, vel: { x: Math.cos(a) * spd, y: Math.sin(a) * spd }, radius: 5, alive: true, damage: boss.damage * 0.35, fromPlayer: false, lifetime: 3.5, color: '#4488ff' });
      }
    } else if (phase === 1) {
      // Gravity well barrage — multiple aimed + a pull zone
      for (let i = -5; i <= 5; i++) {
        state.projectiles.push({ pos: { x: boss.pos.x, y: boss.pos.y }, vel: { x: Math.cos(angle + i * 0.09) * 350, y: Math.sin(angle + i * 0.09) * 350 }, radius: 9, alive: true, damage: boss.damage * 0.65, fromPlayer: false, lifetime: 2, color: '#88aaff' });
      }
      // Teleport + dimension wave
      state.particles.push(...createParticles(boss.pos, '#4488ff', 20, 200, 3));
      boss.pos.x = p.pos.x + (Math.random() - 0.5) * 350;
      boss.pos.y = p.pos.y + (Math.random() - 0.5) * 350;
      boss.pos.x = Math.max(100, Math.min(ARENA_W - 100, boss.pos.x));
      boss.pos.y = Math.max(100, Math.min(ARENA_H - 100, boss.pos.y));
      state.particles.push(...createParticles(boss.pos, '#4488ff', 20, 200, 3));
    } else if (phase === 2) {
      // Twin spiral — 2 spiral arms rotating in opposite directions
      const now3 = Date.now() * 0.002;
      for (let arm = 0; arm < 2; arm++) {
        for (let i = 0; i < 10; i++) {
          const a = (Math.PI * 2 / 10) * i + now3 * (arm === 0 ? 1 : -1);
          state.projectiles.push({ pos: { x: boss.pos.x, y: boss.pos.y }, vel: { x: Math.cos(a) * 190, y: Math.sin(a) * 190 }, radius: 6, alive: true, damage: boss.damage * 0.4, fromPlayer: false, lifetime: 2.5, color: arm === 0 ? '#4488ff' : '#ff4488' });
        }
      }
      // Also spawn quantum shifters
      for (let i = 0; i < 2; i++) {
        const qs = createEnemy('quantum_shifter', Math.max(1, state.wave - 1));
        qs.pos = { x: boss.pos.x + (Math.random() - 0.5) * 120, y: boss.pos.y + (Math.random() - 0.5) * 120 };
        state.enemies.push(qs);
      }
    } else {
      // Reality collapse — bullets from multiple arena corners, aimed cross
      const corners = [[0, 0], [ARENA_W, 0], [ARENA_W, ARENA_H], [0, ARENA_H]];
      for (const [cx2, cy2] of corners) {
        const ca = Math.atan2(p.pos.y - cy2, p.pos.x - cx2);
        for (let i = -2; i <= 2; i++) {
          state.projectiles.push({ pos: { x: cx2, y: cy2 }, vel: { x: Math.cos(ca + i * 0.1) * 240, y: Math.sin(ca + i * 0.1) * 240 }, radius: 7, alive: true, damage: boss.damage * 0.45, fromPlayer: false, lifetime: 3, color: '#66aaff' });
        }
      }
      state.shakeTimer = 0.5; state.shakeIntensity = 14;
    }
    boss.bossPhase = (boss.bossPhase || 0) + 1;
    state.shakeTimer = Math.max(state.shakeTimer, 0.4); state.shakeIntensity = Math.max(state.shakeIntensity, 12);
    state.particles.push(...createParticles(boss.pos, '#4488ff', 30, 280, 5));
  } else if (boss.type === 'void_emperor') {
    // VOID EMPEROR: Absolute darkness — all attacks are massive, arena-wide, draining
    const phase = (boss.bossPhase || 0) % 5;
    if (phase === 0) {
      // Oblivion nova — giant ring of void shots
      for (let i = 0; i < 28; i++) {
        const a = (Math.PI * 2 / 28) * i;
        state.projectiles.push({ pos: { x: boss.pos.x, y: boss.pos.y }, vel: { x: Math.cos(a) * 170, y: Math.sin(a) * 170 }, radius: 8, alive: true, damage: boss.damage * 0.45, fromPlayer: false, lifetime: 3, color: '#220044' });
      }
    } else if (phase === 1) {
      // Death beams: 4 rotating aimed salvos
      for (let b = 0; b < 4; b++) {
        const bA = angle + (b * Math.PI / 2);
        for (let i = -3; i <= 3; i++) {
          state.projectiles.push({ pos: { x: boss.pos.x, y: boss.pos.y }, vel: { x: Math.cos(bA + i * 0.08) * 400, y: Math.sin(bA + i * 0.08) * 400 }, radius: 11, alive: true, damage: boss.damage * 0.75, fromPlayer: false, lifetime: 2, color: '#440088' });
        }
      }
      state.shakeTimer = 0.5; state.shakeIntensity = 16;
    } else if (phase === 2) {
      // Void rift burst — spawn multiple void horrors
      for (let i = 0; i < 3; i++) {
        const ah = createEnemy('abyss_horror', Math.max(1, state.wave - 2));
        const rA = (Math.PI * 2 / 3) * i;
        ah.pos = { x: boss.pos.x + Math.cos(rA) * 100, y: boss.pos.y + Math.sin(rA) * 100 };
        state.enemies.push(ah);
      }
      // Pull vortex
      for (let i = 0; i < 16; i++) {
        const a = (Math.PI * 2 / 16) * i;
        state.projectiles.push({ pos: { x: boss.pos.x, y: boss.pos.y }, vel: { x: Math.cos(a) * 140, y: Math.sin(a) * 140 }, radius: 6, alive: true, damage: boss.damage * 0.4, fromPlayer: false, lifetime: 2.5, color: '#550077' });
      }
      state.particles.push(...createParticles(boss.pos, '#220044', 40, 350, 6));
    } else if (phase === 3) {
      // Shadow phase — teleport 4 times, each time firing a burst
      for (let t = 0; t < 4; t++) {
        const tA = (Math.PI / 2) * t + Date.now() * 0.001;
        const tX = boss.pos.x + Math.cos(tA) * 150;
        const tY = boss.pos.y + Math.sin(tA) * 150;
        const tXc = Math.max(80, Math.min(ARENA_W - 80, tX));
        const tYc = Math.max(80, Math.min(ARENA_H - 80, tY));
        for (let i = 0; i < 10; i++) {
          const a = (Math.PI * 2 / 10) * i;
          state.projectiles.push({ pos: { x: tXc, y: tYc }, vel: { x: Math.cos(a) * 200, y: Math.sin(a) * 200 }, radius: 7, alive: true, damage: boss.damage * 0.5, fromPlayer: false, lifetime: 2, color: '#660099' });
        }
        state.particles.push(...createParticles({ x: tXc, y: tYc }, '#440088', 15, 150, 3));
      }
    } else {
      // Emperor's Wrath — massive full-arena attack, then slow recovery
      for (let i = 0; i < 4; i++) {
        const eA = (Math.PI / 2) * i;
        for (let j = 0; j < 8; j++) {
          state.projectiles.push({ pos: { x: boss.pos.x, y: boss.pos.y }, vel: { x: Math.cos(eA + j * 0.08) * 340, y: Math.sin(eA + j * 0.08) * 340 }, radius: 12, alive: true, damage: boss.damage * 0.9, fromPlayer: false, lifetime: 2.5, color: '#ff00ff' });
        }
      }
      // Gravity pulse — pull player in for 0.5s
      const pullDx = boss.pos.x - p.pos.x;
      const pullDy = boss.pos.y - p.pos.y;
      const pullD = Math.hypot(pullDx, pullDy);
      if (pullD > 1) {
        p.pos.x += (pullDx / pullD) * 60;
        p.pos.y += (pullDy / pullD) * 60;
      }
      state.shakeTimer = 0.8; state.shakeIntensity = 20;
      state.particles.push(...createParticles(boss.pos, '#ff00ff', 60, 500, 9));
    }
    boss.bossPhase = (boss.bossPhase || 0) + 1;
    state.shakeTimer = Math.max(state.shakeTimer, 0.4); state.shakeIntensity = Math.max(state.shakeIntensity, 12);
    state.particles.push(...createParticles(boss.pos, '#440088', 35, 300, 6));
  } else if (boss.type === 'archon') {
    // Archon: Golden storm - massive spread + homing orbs + spawns tanks
    // Phase 1: wide golden spread
    for (let i = 0; i < 20; i++) {
      const a = (Math.PI * 2 / 20) * i + Date.now() * 0.002;
      state.projectiles.push({
        pos: { x: boss.pos.x, y: boss.pos.y },
        vel: { x: Math.cos(a) * 240, y: Math.sin(a) * 240 },
        radius: 8, alive: true, damage: boss.damage * 0.5, fromPlayer: false,
        lifetime: 2.5, color: '#ffd700',
      });
    }
    // Phase 2: aimed triple lance
    for (let i = -2; i <= 2; i++) {
      state.projectiles.push({
        pos: { x: boss.pos.x, y: boss.pos.y },
        vel: { x: Math.cos(angle + i * 0.15) * 380, y: Math.sin(angle + i * 0.15) * 380 },
        radius: 12, alive: true, damage: boss.damage, fromPlayer: false,
        lifetime: 2, color: '#fff700',
      });
    }
    // Spawn reinforcements
    for (let i = 0; i < 3; i++) {
      const t = createEnemy('tank', state.wave);
      t.pos = { x: boss.pos.x + (Math.random() - 0.5) * 80, y: boss.pos.y + (Math.random() - 0.5) * 80 };
      state.enemies.push(t);
    }
    state.shakeTimer = 0.5;
    state.shakeIntensity = 12;
    state.particles.push(...createParticles(boss.pos, '#ffd700', 40, 300, 6));
  } else if (boss.type === 'oblivion') {
    // Oblivion: Ultimate devastation - multi-phase attack
    const phase = (boss.bossPhase || 0) % 3;
    if (phase === 0) {
      // Blood nova - expanding rings
      for (let ring = 0; ring < 3; ring++) {
        for (let i = 0; i < 16; i++) {
          const a = (Math.PI * 2 / 16) * i + ring * 0.13;
          const spd = 160 + ring * 60;
          state.projectiles.push({
            pos: { x: boss.pos.x, y: boss.pos.y },
            vel: { x: Math.cos(a) * spd, y: Math.sin(a) * spd },
            radius: 7, alive: true, damage: boss.damage * 0.4, fromPlayer: false,
            lifetime: 2.5, color: '#ff0000',
          });
        }
      }
    } else if (phase === 1) {
      // Death beam - concentrated burst at player
      for (let i = -3; i <= 3; i++) {
        state.projectiles.push({
          pos: { x: boss.pos.x, y: boss.pos.y },
          vel: { x: Math.cos(angle + i * 0.06) * 450, y: Math.sin(angle + i * 0.06) * 450 },
          radius: 14, alive: true, damage: boss.damage * 0.8, fromPlayer: false,
          lifetime: 2, color: '#ff0033',
        });
      }
    } else {
      // Void summon + teleport
      for (let i = 0; i < 4; i++) {
        const rA = Math.random() * Math.PI * 2;
        const d2 = 60 + Math.random() * 100;
        const tx = p.pos.x + Math.cos(rA) * d2;
        const ty = p.pos.y + Math.sin(rA) * d2;
        for (let j = 0; j < 10; j++) {
          const a = (j / 10) * Math.PI * 2;
          state.projectiles.push({
            pos: { x: tx, y: ty },
            vel: { x: Math.cos(a) * 150, y: Math.sin(a) * 150 },
            radius: 6, alive: true, damage: boss.damage * 0.35, fromPlayer: false,
            lifetime: 1.5, color: '#880000',
          });
        }
      }
      // Teleport
      state.particles.push(...createParticles(boss.pos, '#ff0000', 30, 200, 4));
      const tA = Math.random() * Math.PI * 2;
      boss.pos.x = p.pos.x + Math.cos(tA) * 180;
      boss.pos.y = p.pos.y + Math.sin(tA) * 180;
      state.particles.push(...createParticles(boss.pos, '#ff0000', 30, 200, 4));
      // Spawn void ghosts
      for (let i = 0; i < 2; i++) {
        const vg = createEnemy('void_ghost', state.wave);
        vg.pos = { x: boss.pos.x + (Math.random() - 0.5) * 60, y: boss.pos.y + (Math.random() - 0.5) * 60 };
        state.enemies.push(vg);
      }
    }
    boss.bossPhase = (boss.bossPhase || 0) + 1;
    state.shakeTimer = 0.6;
    state.shakeIntensity = 16;
    state.particles.push(...createParticles(boss.pos, '#ff0000', 50, 350, 7));
  }
}

function updateProjectiles(state: GameState, dt: number) {
  const p = state.player;

  for (const proj of state.projectiles) {
    if (!proj.alive) continue;
    
    // Homing: player projectiles slightly track nearest enemy
    if (proj.fromPlayer && state.abilities.homingChance > 0) {
      let nearest: Enemy | null = null;
      let nearestDist = 200;
      for (const e of state.enemies) {
        if (!e.alive) continue;
        const d = dist(proj.pos, e.pos);
        if (d < nearestDist) { nearestDist = d; nearest = e; }
      }
      if (nearest && Math.random() < state.abilities.homingChance) {
        const targetAngle = Math.atan2(nearest.pos.y - proj.pos.y, nearest.pos.x - proj.pos.x);
        const currentAngle = Math.atan2(proj.vel.y, proj.vel.x);
        let diff = targetAngle - currentAngle;
        if (diff > Math.PI) diff -= Math.PI * 2;
        if (diff < -Math.PI) diff += Math.PI * 2;
        const turnRate = 3 * dt;
        const turn = Math.max(-turnRate, Math.min(turnRate, diff));
        const newAngle = currentAngle + turn;
        const speed = Math.hypot(proj.vel.x, proj.vel.y);
        proj.vel.x = Math.cos(newAngle) * speed;
        proj.vel.y = Math.sin(newAngle) * speed;
      }
    }
    
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
          damageEnemy(state, e, proj.damage);

          // Explosion radius: damage nearby enemies too
          if (state.abilities.explosionRadius > 0) {
            const expR = state.abilities.explosionRadius;
            for (const e2 of state.enemies) {
              if (!e2.alive || e2 === e) continue;
              if (dist(proj.pos, e2.pos) < expR + e2.radius) {
                e2.hp -= proj.damage * 0.5;
                e2.flashTimer = 0.08;
              }
            }
            state.particles.push(...createParticles(proj.pos, '#ff6b00', 8, expR * 1.6, 2.5));
            state.particles.push(...createParticles(proj.pos, '#ffff00', 4, expR * 1.2, 2));
          }

          // Pierce / Ricochet logic
          if (proj.pierce && proj.pierce > 0) {
            proj.pierce -= 1;
            // nudge forward to avoid re-colliding same enemy this frame
            const vlen = Math.hypot(proj.vel.x, proj.vel.y) || 1;
            proj.pos.x += (proj.vel.x / vlen) * (e.radius + 6);
            proj.pos.y += (proj.vel.y / vlen) * (e.radius + 6);
          } else if (proj.ricochet && proj.ricochet > 0) {
            proj.ricochet -= 1;
            let nearest: Enemy | null = null;
            let nearestDist = 99999;
            for (const e2 of state.enemies) {
              if (!e2.alive || e2 === e) continue;
              const d2 = dist(e2.pos, proj.pos);
              if (d2 < nearestDist) { nearestDist = d2; nearest = e2; }
            }
            if (nearest) {
              const a = Math.atan2(nearest.pos.y - proj.pos.y, nearest.pos.x - proj.pos.x);
              const spd = Math.hypot(proj.vel.x, proj.vel.y);
              proj.vel.x = Math.cos(a) * spd;
              proj.vel.y = Math.sin(a) * spd;
            } else {
              proj.alive = false;
            }
          } else {
            proj.alive = false;
          }

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
    state.particles.push(...createParticles(e.pos, '#ffff00', 5, 220, 2.5));
  }

  e.hp -= damage;
  e.flashTimer = 0.1;
  playHit();
  // Lower general particle density (better perf) — deaths still go chaotic
  state.particles.push(...createParticles(e.pos, COLORS.neonYellow, 8, 220, 2.5));
  state.particles.push(...createParticles(e.pos, '#ffffff', 4, 160, 2));
  state.particles.push(...createParticles(e.pos, getEnemyColor(e.type), 6, 200, 2.2));

  if (e.hp <= 0) {
    e.alive = false;
    
    // Track boss kills
    if (e.isBoss) {
      state.bossesKilled = (state.bossesKilled || 0) + 1;
      setBossMusic(null); // Return to map music
    }
    
    // Trigger death wave after defeating Oblivion (wave 30 boss)
    if (e.type === 'oblivion') {
      state.deathWave = true;
    }
    
    // Vampirism
    if (state.abilities.vampirism > 0 && Math.random() < state.abilities.vampirism) {
      state.player.hp = Math.min(state.player.maxHp, state.player.hp + 1);
      state.particles.push(...createParticles(state.player.pos, '#ff0060', 5, 60, 2));
    }
    
    // Combo system
    const prevMult = state.comboMultiplier;
    state.combo++;
    state.comboTimer = 2.0;
    state.comboMultiplier = Math.min(16, Math.pow(2, Math.floor(state.combo / 3)));
    if (state.combo > state.maxCombo) state.maxCombo = state.combo;
    if (state.comboMultiplier > prevMult) playCombo(state.comboMultiplier);
    
    state.score += e.score * state.comboMultiplier;
    state.enemiesKilled++;
    state.enemiesKilledThisWave++;

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
    // Less dense overall, but MUCH wider spread on death
    state.particles.push(...createParticles(e.pos, color, e.isBoss ? 160 : 45, 700, e.isBoss ? 7 : 4.5));
    state.particles.push(...createParticles(e.pos, '#ffffff', e.isBoss ? 60 : 20, 620, 3.5));
    const secColor = e.isBoss ? '#ff1493' : COLORS.neonCyan;
    state.particles.push(...createParticles(e.pos, secColor, e.isBoss ? 50 : 18, 650, 3.2));
    state.particles.push(...createParticles(e.pos, COLORS.neonPink, e.isBoss ? 35 : 12, 720, 3));
    state.particles.push(...createParticles(e.pos, COLORS.neonGreen, e.isBoss ? 25 : 10, 680, 2.6));
    
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

    // Power-up drop (luck bonus)
    const dropChance = POWERUP_DROP_CHANCE + (state.comboMultiplier - 1) * 0.02 + (state.abilities.luck || 0);
    if (Math.random() < dropChance) {
      const pu = createPowerUp(e.pos);
      if (pu) state.powerUps.push(pu);
    }
  }
}

function addXp(state: GameState, amount: number) {
  const bonus = 1 + (state.abilities.xpBonus || 0);
  state.xp += Math.floor(amount * bonus);
  state.particles.push(...createParticles(state.player.pos, '#bf5af2', 2, 40, 1.5));
}

function getEnemyColor(type: EnemyType): string {
  return COLORS[type] || '#fff';
}

function damagePlayer(state: GameState, damage: number) {
  const p = state.player;
  if (p.invincibleTimer > 0) return;

  // Dodge check
  if (state.abilities.dodge > 0 && Math.random() < state.abilities.dodge) {
    state.particles.push(...createParticles(p.pos, '#ffffff', 6, 140, 2));
    p.invincibleTimer = 0.3;
    return;
  }

  // Armor actually reduces the chance of losing a heart
  if (state.abilities.armor > 0 && Math.random() < state.abilities.armor) {
    state.particles.push(...createParticles(p.pos, COLORS.neonCyan, 6, 160, 2));
    p.invincibleTimer = 0.5;
    return;
  }

  if (p.shieldTimer > 0) {
    p.shieldTimer = 0;
    state.particles.push(...createParticles(p.pos, COLORS.neonCyan, 10, 200, 2.5));
    p.invincibleTimer = 0.5;
    return;
  }

  p.hp -= 1; // Always lose 1 heart per hit
  p.invincibleTimer = 1.0;
  state.shakeTimer = 0.15;
  state.shakeIntensity = 5;
  state.particles.push(...createParticles(p.pos, COLORS.health, 4, 180, 2));
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
  
  // Death wave: endless fast enemies
  if (state.deathWave) {
    state.waveEnemiesRemaining = 50 + state.wave * 5;
    state.waveSpawnTimer = 0;
    state.enemiesKilledThisWave = 0;
    state.screen = 'playing';
    return;
  }
  
  const isMegaBoss = state.wave === 15 || state.wave === 30;
  const isBossWave = state.wave % BOSS_WAVE_INTERVAL === 0;
  
  // Co-op scaling: more players = more enemies
  const playerCount = 1 + (state.coopPeers?.length || 0);
  const coopMult = 1 + (playerCount - 1) * 0.4; // +40% per extra player
  
  let baseEnemies = isMegaBoss
    ? WAVE_BASE_ENEMIES + state.wave * 3 + 1
    : isBossWave
      ? WAVE_BASE_ENEMIES + state.wave * 2 + 1
      : WAVE_BASE_ENEMIES + (state.wave - 1) * WAVE_ENEMY_INCREMENT;
  
  state.waveEnemiesRemaining = Math.floor(baseEnemies * coopMult);
  state.waveSpawnTimer = 0;
  state.enemiesKilledThisWave = 0;
  state.screen = 'playing';
}

export function createInitialState(
  player: Player,
  mapId: string = 'neon-grid',
  weaponSlots: number = 3,
  mapDifficulty: import('./maps').MapDifficulty = 'medium',
): GameState {
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
    bossesKilled: 0,
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
    equippedWeapons: [],
    weaponSlots,
    regenAccumulator: 0,
    trail: [],
    mapId,
    mapDifficulty,
    hazards: [],
    hazardSpawnTimer: 5,
    flameZones: [],
    plasmaZones: [],
    coopPeers: [],
    enemiesKilledThisWave: 0,
    deathWave: false,
  };
}

function getDifficultySettings(state: GameState) {
  const map = ALL_MAPS[state.mapId];
  const d = map?.difficulties?.[state.mapDifficulty];
  return d ?? {
    enemyHpMult: 1,
    enemyDamageMult: 1,
    enemySpeedMult: 1,
    spawnRateMult: 1,
    hazardRateMult: 1,
  };
}

function applyDifficultyToEnemy(state: GameState, e: Enemy) {
  const d = getDifficultySettings(state);
  
  // Co-op scaling: bosses get much harder with more players
  const playerCount = 1 + (state.coopPeers?.length || 0);
  const coopHpMult = e.isBoss ? (1 + (playerCount - 1) * 0.6) : (1 + (playerCount - 1) * 0.2);
  const coopDmgMult = e.isBoss ? (1 + (playerCount - 1) * 0.25) : 1;
  
  e.hp = Math.max(1, Math.floor(e.hp * d.enemyHpMult * coopHpMult));
  e.maxHp = Math.max(1, Math.floor(e.maxHp * d.enemyHpMult * coopHpMult));
  e.damage = Math.max(1, Math.floor(e.damage * d.enemyDamageMult * coopDmgMult));
  const base = e.baseSpeed ?? e.speed;
  e.speed = base * d.enemySpeedMult;
  e.baseSpeed = e.speed;
}

function updateHazards(state: GameState, dt: number) {
  const map = ALL_MAPS[state.mapId];
  if (!map || map.hazards.length === 0) return;

  const diff = getDifficultySettings(state);

  // Spawn hazards
  state.hazardSpawnTimer -= dt;
  if (state.hazardSpawnTimer <= 0) {
    state.hazardSpawnTimer = 8 / diff.hazardRateMult;
    for (const h of map.hazards) {
      const active = state.hazards.filter(a => a.type === h.type).length;
      if (active < h.maxActive && Math.random() < h.spawnChance) {
        state.hazards.push(createHazard(h.type, ARENA_W, ARENA_H));
      }
    }
  }

  const p = state.player;
  for (let i = state.hazards.length - 1; i >= 0; i--) {
    const hz = state.hazards[i];
    hz.lifetime -= dt;
    if (hz.lifetime <= 0) { state.hazards.splice(i, 1); continue; }

    // Hazard effects
    if (hz.type === 'lava_pool') {
      const d = Math.hypot(p.pos.x - hz.pos.x, p.pos.y - hz.pos.y);
      if (d < hz.radius + p.radius && p.invincibleTimer <= 0) {
        // Damage handled by normal damage system — apply slow
        p.speedBoostTimer = 0;
      }
      for (const e of state.enemies) {
        if (!e.alive) continue;
        const ed = Math.hypot(e.pos.x - hz.pos.x, e.pos.y - hz.pos.y);
        if (ed < hz.radius + e.radius) {
          e.hp -= 5 * dt;
          e.flashTimer = 0.03;
        }
      }
    } else if (hz.type === 'black_hole' && hz.pullStrength) {
      // Pull everything toward it
      const pull = hz.pullStrength;
      const pdx = hz.pos.x - p.pos.x;
      const pdy = hz.pos.y - p.pos.y;
      const pd = Math.hypot(pdx, pdy);
      if (pd < 200 && pd > 5) {
        p.pos.x += (pdx / pd) * pull * dt * (1 - pd / 200);
        p.pos.y += (pdy / pd) * pull * dt * (1 - pd / 200);
      }
      for (const e of state.enemies) {
        if (!e.alive) continue;
        const edx = hz.pos.x - e.pos.x;
        const edy = hz.pos.y - e.pos.y;
        const ed = Math.hypot(edx, edy);
        if (ed < 200 && ed > 5) {
          e.pos.x += (edx / ed) * pull * 1.5 * dt * (1 - ed / 200);
          e.pos.y += (edy / ed) * pull * 1.5 * dt * (1 - ed / 200);
        }
        // Damage at center
        if (ed < hz.radius + e.radius) {
          e.hp -= 20 * dt;
          e.flashTimer = 0.03;
        }
      }
    } else if (hz.type === 'crystal_shard') {
      // Reflect projectiles passing through (keeps chaos without hard-stopping gameplay)
      for (const proj of state.projectiles) {
        if (!proj.alive) continue;
        const d = Math.hypot(proj.pos.x - hz.pos.x, proj.pos.y - hz.pos.y);
        if (d < hz.radius + proj.radius) {
          proj.vel.x *= -1;
          proj.vel.y *= -1;
          if (!proj.fromPlayer) {
            proj.fromPlayer = true;
            proj.color = '#00e5ff';
          }
          state.particles.push(...createParticles(proj.pos, '#00e5ff', 3, 220, 2));
        }
      }
    }
  }
}
