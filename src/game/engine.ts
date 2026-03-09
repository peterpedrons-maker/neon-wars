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
    if (p.class === 'titan' || p.class === 'juggernaut') {
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
  const isBossWave = state.wave % BOSS_WAVE_INTERVAL === 0;

  if (isBossWave && state.waveEnemiesRemaining === 1) {
    // Map-exclusive bosses
    const mapBoss: Record<string, EnemyType> = {
      'inferno': 'lava_dragon',
      'void': 'void_lord',
      'crystal': 'crystal_giant',
    };
    if (mapBoss[state.mapId]) {
      state.enemies.push(createEnemy(mapBoss[state.mapId], state.wave));
      return;
    }
    const bosses: EnemyType[] = ['mothership', 'vortex', 'colossus'];
    const boss = bosses[Math.floor(Math.random() * bosses.length)];
    state.enemies.push(createEnemy(boss, state.wave));
    return;
  }

  // Map-exclusive enemies
  const mapExclusives: Record<string, EnemyType[]> = {
    'inferno': ['fire_elemental'],
    'void': ['void_ghost'],
    'crystal': ['crystal_golem'],
  };

  const types: EnemyType[] = ['drone'];
  if (state.wave >= 2) types.push('splitter');
  if (state.wave >= 3) types.push('dasher');
  if (state.wave >= 5) types.push('tank');
  
  // Add map-specific enemies from wave 2+
  const mapEnemies = mapExclusives[state.mapId] || [];
  if (state.wave >= 2 && mapEnemies.length > 0) {
    types.push(...mapEnemies);
  }

  const type = types[Math.floor(Math.random() * types.length)];
  state.enemies.push(createEnemy(type, state.wave));
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
  
  const color = peer.shipClass === 'phantom' ? COLORS.phantom
    : peer.shipClass === 'interceptor' ? COLORS.interceptor
    : peer.shipClass === 'spectre' ? COLORS.spectre
    : peer.shipClass === 'valkyrie' ? COLORS.valkyrie
    : peer.shipClass === 'juggernaut' ? COLORS.juggernaut
    : COLORS.titan;
  
  // Titan/Juggernaut are melee - damage nearby enemies directly
  if (peer.shipClass === 'titan' || peer.shipClass === 'juggernaut') {
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
          proj.alive = false;
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
            state.particles.push(...createParticles(proj.pos, '#ff6b00', 12, expR, 3));
            state.particles.push(...createParticles(proj.pos, '#ffff00', 6, expR * 0.6, 2));
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
    
    // Track boss kills
    if (e.isBoss) state.bossesKilled = (state.bossesKilled || 0) + 1;
    
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
  const map: Record<string, string> = {
    drone: COLORS.drone, splitter: COLORS.splitter, dasher: COLORS.dasher,
    tank: COLORS.tank, mothership: COLORS.mothership, vortex: COLORS.vortex, colossus: COLORS.colossus,
    fire_elemental: COLORS.fire_elemental, void_ghost: COLORS.void_ghost, crystal_golem: COLORS.crystal_golem,
    lava_dragon: COLORS.lava_dragon, void_lord: COLORS.void_lord, crystal_giant: COLORS.crystal_giant,
  };
  return map[type] || '#fff';
}

function damagePlayer(state: GameState, damage: number) {
  const p = state.player;
  if (p.invincibleTimer > 0) return;
  // Dodge check
  if (state.abilities.dodge > 0 && Math.random() < state.abilities.dodge) {
    state.particles.push(...createParticles(p.pos, '#ffffff', 8, 100, 2));
    p.invincibleTimer = 0.3;
    return;
  }
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
  state.enemiesKilledThisWave = 0;
  state.screen = 'playing';
}

export function createInitialState(player: Player, mapId: string = 'neon-grid', weaponSlots: number = 3): GameState {
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
    hazards: [],
    hazardSpawnTimer: 5,
    flameZones: [],
    plasmaZones: [],
    coopPeers: [],
    enemiesKilledThisWave: 0,
  };
}

function updateHazards(state: GameState, dt: number) {
  const map = ALL_MAPS[state.mapId];
  if (!map || map.hazards.length === 0) return;
  
  // Spawn hazards
  state.hazardSpawnTimer -= dt;
  if (state.hazardSpawnTimer <= 0) {
    state.hazardSpawnTimer = 8;
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
    }
  }
}
