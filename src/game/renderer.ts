import { GameState, Player, Enemy, Projectile, Particle, PowerUp, XpOrb } from './types';
import { COLORS, ARENA_W, ARENA_H, WARRIOR_ATTACK_RANGE, CAMERA_VIEW_W, CAMERA_VIEW_H, CAMERA_LERP, WALL_LEFT, WALL_RIGHT, WALL_TOP, WALL_BOTTOM } from './constants';
import { ALL_MAPS } from './maps';
import { ActiveHazard } from './maps';

// Camera state
let camX = ARENA_W / 2;
let camY = ARENA_H / 2;

const GRID_SIZE = 40;

export function renderGame(ctx: CanvasRenderingContext2D, state: GameState, canvasW: number, canvasH: number) {
  const time = Date.now() * 0.001;

  // Smooth camera follow player
  if (state.player.alive) {
    camX += (state.player.pos.x - camX) * CAMERA_LERP;
    camY += (state.player.pos.y - camY) * CAMERA_LERP;
  }

  const halfViewW = CAMERA_VIEW_W / 2;
  const halfViewH = CAMERA_VIEW_H / 2;
  camX = Math.max(halfViewW, Math.min(ARENA_W - halfViewW, camX));
  camY = Math.max(halfViewH, Math.min(ARENA_H - halfViewH, camY));

  const scale = Math.min(canvasW / CAMERA_VIEW_W, canvasH / CAMERA_VIEW_H);
  const viewportW = canvasW / scale;
  const viewportH = canvasH / scale;

  ctx.save();

  // Screen shake
  if (state.shakeTimer > 0) {
    const sx = (Math.random() - 0.5) * state.shakeIntensity;
    const sy = (Math.random() - 0.5) * state.shakeIntensity;
    ctx.translate(sx, sy);
  }

  // Clear to deep black
  ctx.fillStyle = COLORS.bg;
  ctx.fillRect(0, 0, canvasW, canvasH);

  ctx.scale(scale, scale);
  ctx.translate(viewportW / 2 - camX, viewportH / 2 - camY);

  // --- NEON GRID with WARP DISTORTION ---
  drawNeonGridWarped(ctx, time, state);
  
  // Arena border
  drawArenaBorder(ctx, time);

  // Player ambient glow
  if (state.player.alive) {
    drawPlayerGlow(ctx, state.player, time);
  }

  // Player trail
  drawTrail(ctx, state, time);

  // Map hazards
  if (state.hazards) state.hazards.forEach(h => drawHazard(ctx, h, time));
  
  // Flame zones
  if (state.flameZones) state.flameZones.forEach(fz => {
    const alpha = Math.min(0.5, fz.lifetime / 3);
    const grad = ctx.createRadialGradient(fz.x, fz.y, 0, fz.x, fz.y, 15);
    grad.addColorStop(0, `rgba(255,100,0,${alpha})`);
    grad.addColorStop(0.5, `rgba(255,50,0,${alpha * 0.5})`);
    grad.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = grad;
    ctx.beginPath(); ctx.arc(fz.x, fz.y, 15, 0, Math.PI * 2); ctx.fill();
  });
  
  // Plasma zones
  if (state.plasmaZones) state.plasmaZones.forEach(pz => {
    const alpha = Math.min(0.4, pz.lifetime / 5);
    const grad = ctx.createRadialGradient(pz.x, pz.y, 0, pz.x, pz.y, pz.radius);
    grad.addColorStop(0, `rgba(191,90,242,${alpha * 0.6})`);
    grad.addColorStop(0.5, `rgba(191,90,242,${alpha * 0.3})`);
    grad.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = grad;
    ctx.beginPath(); ctx.arc(pz.x, pz.y, pz.radius, 0, Math.PI * 2); ctx.fill();
    ctx.strokeStyle = `rgba(191,90,242,${alpha})`;
    ctx.lineWidth = 1;
    ctx.beginPath(); ctx.arc(pz.x, pz.y, pz.radius, 0, Math.PI * 2); ctx.stroke();
  });

  // XP orbs
  state.xpOrbs.forEach(orb => drawXpOrb(ctx, orb, time));

  // Power-ups
  state.powerUps.forEach(pu => { if (pu.alive) drawPowerUp(ctx, pu, time); });

  // Projectiles
  state.projectiles.forEach(p => { if (p.alive) drawProjectile(ctx, p, time); });

  // Enemies
  state.enemies.forEach(e => { if (e.alive) drawEnemy(ctx, e, time, state); });

  // Ability visuals (aura, orbitals)
  if (state.player.alive) {
    drawAbilityVisuals(ctx, state, time);
  }

  // Player
  if (state.player.alive) drawPlayer(ctx, state.player, time);

  // Coop peers with full ship design
  const allPeers = state.coopPeers.length > 0 ? state.coopPeers : (state.coopPeer && state.coopPeer.alive ? [{ ...state.coopPeer, playerId: 'p2', playerLabel: 'P2', dead: false, reviveProgress: 0 }] : []);
  // Filter out local player to avoid ghost ship
  const remotePeers = allPeers.filter(p => p.playerId !== state.localPlayerId);
  
  for (const peer of remotePeers) {
    // Draw dead peers as wreckage
    if (peer.dead || !peer.alive) {
      drawDeadPeer(ctx, peer, time);
      continue;
    }
    
    const fakePlayer: Player = {
      pos: { ...peer.pos }, vel: { x: 0, y: 0 }, radius: 12, alive: true,
      hp: peer.hp ?? 1, maxHp: peer.maxHp ?? 1, class: (peer.shipClass as any) || 'phantom',
      damage: peer.damage, speed: 200,
      attackCooldown: peer.attackCooldown, attackTimer: peer.shooting ? peer.attackCooldown * 0.8 : 0,
      specialCooldown: 5, specialTimer: 0,
      shieldTimer: peer.shieldTimer ?? 0, tripleTimer: 0, speedBoostTimer: 0,
      invincibleTimer: peer.invincibleTimer ?? 0,
      angle: peer.angle,
    };
    drawPlayer(ctx, fakePlayer, time);
    // Player label
    ctx.save();
    ctx.shadowColor = '#39ff14'; ctx.shadowBlur = 6;
    ctx.font = 'bold 8px Orbitron, monospace';
    ctx.fillStyle = '#39ff14'; ctx.textAlign = 'center'; ctx.globalAlpha = 0.85;
    ctx.fillText(peer.playerLabel || 'P2', peer.pos.x, peer.pos.y - 20);
    ctx.restore();
  }

  // Particles
  state.particles.forEach(p => drawParticle(ctx, p));

  // Combo display (in world, above player)
  if (state.combo > 1 && state.player.alive) {
    drawComboIndicator(ctx, state, time);
  }

  // Vignette
  drawVignette(ctx, camX, camY, viewportW, viewportH);

  // Outside arena
  drawOutsideArena(ctx, camX, camY, viewportW, viewportH);

  ctx.restore();

  // Off-screen peer indicators (drawn in screen space, after ctx.restore)
  if (remotePeers.length > 0) {
    drawOffScreenPeerIndicators(ctx, remotePeers, camX, camY, viewportW, viewportH, scale, canvasW, canvasH, time);
  }
}

// Draw dead peer as wreckage
function drawDeadPeer(ctx: CanvasRenderingContext2D, peer: any, time: number) {
  const info = getShipColor(peer.shipClass);
  const pulse = 0.3 + Math.sin(time * 2) * 0.1;
  
  ctx.save();
  ctx.translate(peer.pos.x, peer.pos.y);
  
  // Wreckage particles
  ctx.globalAlpha = 0.6;
  for (let i = 0; i < 8; i++) {
    const angle = (i / 8) * Math.PI * 2 + time * 0.5;
    const dist = 8 + Math.sin(time * 3 + i) * 3;
    const x = Math.cos(angle) * dist;
    const y = Math.sin(angle) * dist;
    ctx.fillStyle = info;
    ctx.beginPath();
    ctx.arc(x, y, 2, 0, Math.PI * 2);
    ctx.fill();
  }
  
  // Revive progress ring
  if (peer.reviveProgress > 0) {
    const progress = peer.reviveProgress;
    ctx.strokeStyle = '#39ff14';
    ctx.lineWidth = 3;
    ctx.globalAlpha = 0.8;
    ctx.beginPath();
    ctx.arc(0, 0, 18, -Math.PI / 2, -Math.PI / 2 + progress * Math.PI * 2);
    ctx.stroke();
    
    // Revive text
    ctx.font = 'bold 10px Orbitron, monospace';
    ctx.fillStyle = '#39ff14';
    ctx.textAlign = 'center';
    ctx.fillText('REVIVING...', 0, -25);
    ctx.fillText(`${Math.floor(progress * 100)}%`, 0, 30);
  } else {
    // "Hold to revive" hint
    ctx.globalAlpha = pulse;
    ctx.font = 'bold 8px Orbitron, monospace';
    ctx.fillStyle = '#ff6b00';
    ctx.textAlign = 'center';
    ctx.fillText('❤️ PRESS TO REVIVE', 0, -22);
  }
  
  // Label
  ctx.globalAlpha = 0.7;
  ctx.font = 'bold 8px Orbitron, monospace';
  ctx.fillStyle = '#ff4060';
  ctx.textAlign = 'center';
  ctx.fillText(`${peer.playerLabel || 'PLAYER'} [DEAD]`, 0, -35);
  
  ctx.restore();
}

// Warp sources: player + recent explosions
interface WarpSource { x: number; y: number; strength: number; radius: number; }

function getWarpSources(state: GameState): WarpSource[] {
  const sources: WarpSource[] = [];
  if (state.player.alive) {
    const speed = Math.hypot(state.player.vel.x || 0, state.player.vel.y || 0);
    sources.push({ x: state.player.pos.x, y: state.player.pos.y, strength: 8 + speed * 0.02, radius: 120 });
  }
  // Shake = recent explosion, add warp at camera center
  if (state.shakeTimer > 0) {
    sources.push({ x: camX, y: camY, strength: 20 * state.shakeTimer, radius: 200 });
  }
  return sources;
}

function warpPoint(px: number, py: number, sources: WarpSource[]): [number, number] {
  let dx = 0, dy = 0;
  for (const s of sources) {
    const ox = px - s.x;
    const oy = py - s.y;
    const d = Math.hypot(ox, oy);
    if (d < s.radius && d > 1) {
      const factor = (1 - d / s.radius) * s.strength;
      dx += (ox / d) * factor;
      dy += (oy / d) * factor;
    }
  }
  return [px + dx, py + dy];
}

function drawNeonGridWarped(ctx: CanvasRenderingContext2D, time: number, state: GameState) {
  const pulse = 0.04 + Math.sin(time * 0.5) * 0.015;
  const sources = getWarpSources(state);
  const hasWarp = sources.length > 0;

  // Bright lines near warp sources
  const segLen = hasWarp ? 20 : ARENA_H; // subdivide near player for smooth warp

  ctx.lineWidth = 0.5;

  // Vertical lines
  for (let x = 0; x <= ARENA_W; x += GRID_SIZE) {
    ctx.beginPath();
    let first = true;
    for (let y = 0; y <= ARENA_H; y += segLen) {
      let [wx, wy] = hasWarp ? warpPoint(x, y, sources) : [x, y];
      // Glow brighter near warp sources
      let brightness = pulse;
      for (const s of sources) {
        const d = Math.hypot(x - s.x, y - s.y);
        if (d < s.radius) brightness = Math.max(brightness, 0.12 * (1 - d / s.radius));
      }
      ctx.strokeStyle = `rgba(0,255,255,${brightness})`;
      if (first) { ctx.moveTo(wx, wy); first = false; }
      else ctx.lineTo(wx, wy);
    }
    ctx.stroke();
  }

  // Horizontal lines
  for (let y = 0; y <= ARENA_H; y += GRID_SIZE) {
    ctx.beginPath();
    let first = true;
    for (let x = 0; x <= ARENA_W; x += segLen) {
      let [wx, wy] = hasWarp ? warpPoint(x, y, sources) : [x, y];
      let brightness = pulse;
      for (const s of sources) {
        const d = Math.hypot(x - s.x, y - s.y);
        if (d < s.radius) brightness = Math.max(brightness, 0.12 * (1 - d / s.radius));
      }
      ctx.strokeStyle = `rgba(0,255,255,${brightness})`;
      if (first) { ctx.moveTo(wx, wy); first = false; }
      else ctx.lineTo(wx, wy);
    }
    ctx.stroke();
  }
}

function drawComboIndicator(ctx: CanvasRenderingContext2D, state: GameState, time: number) {
  const p = state.player;
  const comboAlpha = Math.min(1, state.comboTimer / 0.5);
  const scale = 1 + Math.sin(time * 8) * 0.05;
  
  ctx.save();
  ctx.translate(p.pos.x, p.pos.y - p.radius - 25);
  ctx.scale(scale, scale);
  
  // Multiplier text
  const mult = state.comboMultiplier;
  const color = mult >= 8 ? '#ff1493' : mult >= 4 ? '#ffff00' : '#0ff';
  ctx.shadowColor = color;
  ctx.shadowBlur = 15;
  ctx.fillStyle = color;
  ctx.font = 'bold 12px Orbitron, monospace';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.globalAlpha = comboAlpha;
  ctx.fillText(`×${mult}`, 0, 0);
  
  // Combo count smaller
  ctx.font = '7px monospace';
  ctx.fillStyle = `rgba(255,255,255,${comboAlpha * 0.6})`;
  ctx.shadowBlur = 0;
  ctx.fillText(`${state.combo} combo`, 0, 10);
  
  ctx.restore();
}

function drawArenaBorder(ctx: CanvasRenderingContext2D, time: number) {
  const glow = 0.6 + Math.sin(time * 2) * 0.2;
  
  // Outer glow
  ctx.shadowColor = '#0ff';
  ctx.shadowBlur = 20;
  ctx.strokeStyle = `rgba(0,255,255,${glow})`;
  ctx.lineWidth = 2;
  ctx.strokeRect(0, 0, ARENA_W, ARENA_H);
  ctx.shadowBlur = 0;

  // Inner bright line
  ctx.strokeStyle = `rgba(0,255,255,${glow * 0.5})`;
  ctx.lineWidth = 1;
  ctx.strokeRect(2, 2, ARENA_W - 4, ARENA_H - 4);
}

function drawPlayerGlow(ctx: CanvasRenderingContext2D, p: Player, time: number) {
  const shipColor = getShipColor(p.class);
  const grad = ctx.createRadialGradient(p.pos.x, p.pos.y, 5, p.pos.x, p.pos.y, 120);
  grad.addColorStop(0, hexToRgba(shipColor, 0.12));
  grad.addColorStop(0.5, hexToRgba(shipColor, 0.03));
  grad.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.fillStyle = grad;
  ctx.fillRect(p.pos.x - 130, p.pos.y - 130, 260, 260);
}

function drawOutsideArena(ctx: CanvasRenderingContext2D, cx: number, cy: number, vw: number, vh: number) {
  ctx.fillStyle = '#000005';
  const left = cx - vw / 2;
  const top = cy - vh / 2;
  if (top < 0) ctx.fillRect(left, top, vw, -top);
  const bottom = cy + vh / 2;
  if (bottom > ARENA_H) ctx.fillRect(left, ARENA_H, vw, bottom - ARENA_H);
  if (left < 0) ctx.fillRect(left, 0, -left, ARENA_H);
  const right = cx + vw / 2;
  if (right > ARENA_W) ctx.fillRect(ARENA_W, 0, right - ARENA_W, ARENA_H);
}

function drawVignette(ctx: CanvasRenderingContext2D, cx: number, cy: number, vw: number, vh: number) {
  const grad = ctx.createRadialGradient(cx, cy, Math.min(vw, vh) * 0.2, cx, cy, Math.max(vw, vh) * 0.6);
  grad.addColorStop(0, 'rgba(0,0,0,0)');
  grad.addColorStop(1, 'rgba(0,0,8,0.4)');
  ctx.fillStyle = grad;
  ctx.fillRect(cx - vw / 2, cy - vh / 2, vw, vh);
}

// --- PLAYER (SHIP) --- Premium detailed designs with dynamic animations
function drawPlayer(ctx: CanvasRenderingContext2D, p: Player, time: number) {
  ctx.save();
  ctx.translate(p.pos.x, p.pos.y);
  
  const color = getShipColor(p.class);
  const glowColor = getShipGlow(p.class);
  const speed = Math.hypot(p.vel.x || 0, p.vel.y || 0);
  const speedRatio = Math.min(1, speed / (p.speed * 1.5));
  const r = p.radius;
  
  // Attack recoil animation
  const attackProg = p.attackTimer / p.attackCooldown;
  const recoil = attackProg > 0.7 ? (attackProg - 0.7) / 0.3 * 2.5 : 0;
  
  // Banking/tilt based on turning (simulate via velocity angle vs facing angle)
  const bankAmount = Math.sin(time * 2.5) * speedRatio * 0.08;
  
  ctx.rotate(p.angle + bankAmount);
  
  // Slight recoil translation
  ctx.translate(-recoil, 0);

  // Shield effect - rotating hex with inner ring
  if (p.shieldTimer > 0) {
    const sa = 0.3 + Math.sin(time * 5) * 0.15;
    ctx.save();
    ctx.rotate(-p.angle - bankAmount + time * 0.5);
    drawNeonShape(ctx, 6, r + 14, '#0ff', sa);
    ctx.rotate(time * -1);
    drawNeonShape(ctx, 6, r + 10, '#0ff', sa * 0.4);
    ctx.restore();
  }

  if (p.invincibleTimer > 0 && Math.floor(Date.now() / 80) % 2 === 0) {
    ctx.globalAlpha = 0.4;
  }

  // === MULTI-LAYERED ENGINE EXHAUST ===
  const thrustBase = 0.5 + Math.sin(time * 22) * 0.2 + Math.sin(time * 37) * 0.15;
  const thrustLen = 10 + speedRatio * 35 + Math.sin(time * 15) * 3;
  const exhaustSpread = p.class === 'titan' ? 7 : p.class === 'phantom' ? 4.5 : 3.5;
  const numExhausts = p.class === 'titan' ? 3 : 2;
  
  // Attack boost exhaust flare
  const attackFlare = attackProg > 0.5 ? (attackProg - 0.5) * 2 : 0;
  const totalThrustLen = thrustLen + attackFlare * 15;
  
  for (let ei = 0; ei < numExhausts; ei++) {
    const oy = numExhausts === 3 
      ? (ei - 1) * exhaustSpread 
      : (ei === 0 ? -1 : 1) * exhaustSpread;
    
    // Layer 1: Wide outer glow cone
    const outerLen = totalThrustLen * 1.3;
    const outerGrad = ctx.createLinearGradient(-r * 0.4, 0, -r - outerLen, 0);
    outerGrad.addColorStop(0, hexToRgba(color, thrustBase * 0.25));
    outerGrad.addColorStop(0.5, hexToRgba(color, thrustBase * 0.12));
    outerGrad.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = outerGrad;
    ctx.beginPath();
    ctx.moveTo(-r * 0.4, oy - 5);
    ctx.quadraticCurveTo(-r - outerLen * 0.5, oy - 2, -r - outerLen, oy);
    ctx.quadraticCurveTo(-r - outerLen * 0.5, oy + 2, -r * 0.4, oy + 5);
    ctx.closePath(); ctx.fill();
    
    // Layer 2: Colored flame core
    const flameFlicker = Math.sin(time * 30 + ei * 2.5) * 0.15;
    ctx.fillStyle = hexToRgba(color, (thrustBase + flameFlicker) * 0.55);
    ctx.beginPath();
    ctx.moveTo(-r * 0.38, oy - 3.2);
    ctx.bezierCurveTo(
      -r - totalThrustLen * 0.3, oy - 2 + Math.sin(time * 25) * 1.5,
      -r - totalThrustLen * 0.7, oy + Math.sin(time * 19) * 1,
      -r - totalThrustLen, oy
    );
    ctx.bezierCurveTo(
      -r - totalThrustLen * 0.7, oy - Math.sin(time * 19) * 1,
      -r - totalThrustLen * 0.3, oy + 2 - Math.sin(time * 25) * 1.5,
      -r * 0.38, oy + 3.2
    );
    ctx.closePath(); ctx.fill();
    
    // Layer 3: White-hot inner core
    const innerLen = totalThrustLen * 0.6;
    ctx.fillStyle = hexToRgba('#ffffff', (thrustBase + flameFlicker) * 0.8);
    ctx.beginPath();
    ctx.moveTo(-r * 0.35, oy - 1.5);
    ctx.bezierCurveTo(
      -r - innerLen * 0.4, oy - 0.8 + Math.sin(time * 35) * 0.5,
      -r - innerLen * 0.7, oy,
      -r - innerLen, oy
    );
    ctx.bezierCurveTo(
      -r - innerLen * 0.7, oy,
      -r - innerLen * 0.4, oy + 0.8 - Math.sin(time * 35) * 0.5,
      -r * 0.35, oy + 1.5
    );
    ctx.closePath(); ctx.fill();
    
    // Layer 4: Exhaust nozzle glow ring
    ctx.strokeStyle = hexToRgba(glowColor, thrustBase * 0.6);
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.ellipse(-r * 0.4, oy, 1.5, 3.5, 0, 0, Math.PI * 2);
    ctx.stroke();
  }
  
  // Central exhaust heat distortion glow
  const heatGrad = ctx.createRadialGradient(-r * 0.3, 0, 2, -r * 0.3, 0, totalThrustLen * 1.2);
  heatGrad.addColorStop(0, hexToRgba(color, 0.25 + speedRatio * 0.15));
  heatGrad.addColorStop(0.4, hexToRgba(color, 0.08));
  heatGrad.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.fillStyle = heatGrad;
  ctx.fillRect(-r - totalThrustLen * 1.3, -exhaustSpread - 8, totalThrustLen * 1.5 + r * 0.3, (exhaustSpread + 8) * 2);
  
  // Exhaust particle sparks (scattered dots behind engines)
  for (let si = 0; si < Math.floor(3 + speedRatio * 6); si++) {
    const sparkX = -r - Math.random() * totalThrustLen * 1.5;
    const sparkY = (Math.random() - 0.5) * exhaustSpread * 3;
    const sparkAlpha = Math.random() * 0.5 * thrustBase;
    const sparkSize = 0.5 + Math.random() * 1.5;
    ctx.fillStyle = hexToRgba(si % 2 === 0 ? color : '#ffffff', sparkAlpha);
    ctx.beginPath(); ctx.arc(sparkX, sparkY, sparkSize, 0, Math.PI * 2); ctx.fill();
  }

  // === ATTACK MUZZLE FLASH ===
  if (attackProg > 0.6) {
    const flashIntensity = (attackProg - 0.6) / 0.4;
    const flashR = r * 1.5 + flashIntensity * 12;
    const muzzleX = p.class === 'titan' ? r * 0.8 : r * 1.8;
    
    const muzzleGrad = ctx.createRadialGradient(muzzleX, 0, 0, muzzleX, 0, flashR);
    muzzleGrad.addColorStop(0, hexToRgba('#ffffff', flashIntensity * 0.7));
    muzzleGrad.addColorStop(0.3, hexToRgba(color, flashIntensity * 0.5));
    muzzleGrad.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = muzzleGrad;
    ctx.beginPath(); ctx.arc(muzzleX, 0, flashR, 0, Math.PI * 2); ctx.fill();
    
    // Muzzle spark lines
    ctx.strokeStyle = hexToRgba(color, flashIntensity * 0.6);
    ctx.lineWidth = 0.8;
    for (let si = 0; si < 5; si++) {
      const sa = (si / 5) * Math.PI * 2 + time * 12;
      const sLen = 4 + flashIntensity * 8;
      ctx.beginPath();
      ctx.moveTo(muzzleX + Math.cos(sa) * 2, Math.sin(sa) * 2);
      ctx.lineTo(muzzleX + Math.cos(sa) * sLen, Math.sin(sa) * sLen);
      ctx.stroke();
    }
  }

  ctx.shadowColor = color;
  ctx.shadowBlur = 18 + Math.sin(time * 3) * 6 + attackFlare * 15;

  // === SHIP BODY with speed-reactive energy lines ===
  if (p.class === 'phantom') {
    // === PHANTOM: Sleek stealth craft ===
    ctx.beginPath();
    ctx.moveTo(r * 1.8, 0);
    ctx.lineTo(r * 0.6, -r * 0.25);
    ctx.lineTo(r * 0.1, -r * 0.35);
    ctx.lineTo(-r * 0.3, -r * 1.2);
    ctx.lineTo(-r * 0.7, -r * 1.0);
    ctx.lineTo(-r * 0.55, -r * 0.25);
    ctx.lineTo(-r * 0.7, -r * 0.15);
    ctx.lineTo(-r * 0.7, r * 0.15);
    ctx.lineTo(-r * 0.55, r * 0.25);
    ctx.lineTo(-r * 0.7, r * 1.0);
    ctx.lineTo(-r * 0.3, r * 1.2);
    ctx.lineTo(r * 0.1, r * 0.35);
    ctx.lineTo(r * 0.6, r * 0.25);
    ctx.closePath();
    ctx.fillStyle = hexToRgba(color, 0.15 + speedRatio * 0.08); ctx.fill();
    ctx.strokeStyle = color; ctx.lineWidth = 1.5; ctx.stroke();
    
    // Wing energy lines - pulse faster at speed
    const energyPulse = 0.4 + Math.sin(time * (4 + speedRatio * 8)) * 0.3;
    ctx.strokeStyle = hexToRgba(glowColor, energyPulse); ctx.lineWidth = 0.8 + speedRatio * 0.5;
    ctx.beginPath();
    ctx.moveTo(r * 0.3, -r * 0.2); ctx.lineTo(-r * 0.4, -r * 0.9);
    ctx.moveTo(r * 0.3, r * 0.2); ctx.lineTo(-r * 0.4, r * 0.9);
    ctx.stroke();
    
    // Animated energy flow along wings
    const flowPos = (time * 3) % 1;
    const fX = r * 0.3 + (-r * 0.7 - r * 0.3) * flowPos;
    const fY = -r * 0.2 + (-r * 0.7) * flowPos;
    ctx.fillStyle = hexToRgba('#ffffff', 0.6 * (1 - flowPos));
    ctx.beginPath(); ctx.arc(fX, fY, 1.5, 0, Math.PI * 2); ctx.fill();
    ctx.beginPath(); ctx.arc(fX, -fY, 1.5, 0, Math.PI * 2); ctx.fill();
    
    // Wing tip lights (pulsing)
    const wingPulse = 0.5 + Math.sin(time * 4) * 0.3;
    ctx.fillStyle = hexToRgba(glowColor, wingPulse);
    ctx.beginPath(); ctx.arc(-r * 0.3, -r * 1.15, 1.5 + wingPulse, 0, Math.PI * 2); ctx.fill();
    ctx.beginPath(); ctx.arc(-r * 0.3, r * 1.15, 1.5 + wingPulse, 0, Math.PI * 2); ctx.fill();
    // Wing tip glow halos
    const tipGrad1 = ctx.createRadialGradient(-r * 0.3, -r * 1.15, 0, -r * 0.3, -r * 1.15, 5);
    tipGrad1.addColorStop(0, hexToRgba(glowColor, wingPulse * 0.5));
    tipGrad1.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = tipGrad1;
    ctx.beginPath(); ctx.arc(-r * 0.3, -r * 1.15, 5, 0, Math.PI * 2); ctx.fill();
    const tipGrad2 = ctx.createRadialGradient(-r * 0.3, r * 1.15, 0, -r * 0.3, r * 1.15, 5);
    tipGrad2.addColorStop(0, hexToRgba(glowColor, wingPulse * 0.5));
    tipGrad2.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = tipGrad2;
    ctx.beginPath(); ctx.arc(-r * 0.3, r * 1.15, 5, 0, Math.PI * 2); ctx.fill();
    
    // Center spine
    ctx.strokeStyle = hexToRgba(color, 0.3); ctx.lineWidth = 0.6;
    ctx.beginPath(); ctx.moveTo(r * 1.2, 0); ctx.lineTo(-r * 0.5, 0); ctx.stroke();
    ctx.strokeStyle = hexToRgba(color, 0.15); ctx.lineWidth = 0.4;
    ctx.beginPath();
    ctx.moveTo(r * 0.1, -r * 0.3); ctx.lineTo(-r * 0.5, -r * 0.2);
    ctx.moveTo(r * 0.1, r * 0.3); ctx.lineTo(-r * 0.5, r * 0.2);
    ctx.stroke();
    
  } else if (p.class === 'interceptor') {
    // === INTERCEPTOR: Twin-boom sleek fighter ===
    ctx.beginPath();
    ctx.moveTo(r * 2.0, 0);
    ctx.lineTo(r * 0.8, -r * 0.2);
    ctx.lineTo(r * 0.3, -r * 0.35);
    ctx.lineTo(-r * 0.2, -r * 0.3);
    ctx.lineTo(-r * 0.5, -r * 0.15);
    ctx.lineTo(-r * 0.5, r * 0.15);
    ctx.lineTo(-r * 0.2, r * 0.3);
    ctx.lineTo(r * 0.3, r * 0.35);
    ctx.lineTo(r * 0.8, r * 0.2);
    ctx.closePath();
    ctx.fillStyle = hexToRgba(color, 0.12 + speedRatio * 0.06); ctx.fill();
    ctx.strokeStyle = color; ctx.lineWidth = 1.2; ctx.stroke();
    
    // Twin boom nacelles with pulsing energy
    for (const side of [-1, 1]) {
      ctx.beginPath();
      ctx.moveTo(r * 0.4, side * r * 0.35);
      ctx.lineTo(-r * 0.1, side * r * 0.7);
      ctx.lineTo(-r * 0.6, side * r * 0.65);
      ctx.lineTo(-r * 0.4, side * r * 0.35);
      ctx.closePath();
      ctx.fillStyle = hexToRgba(color, 0.1); ctx.fill();
      ctx.strokeStyle = color; ctx.lineWidth = 1; ctx.stroke();
      
      // Nacelle glow - reactive to speed
      const nacPulse = 0.4 + Math.sin(time * 6 + side) * 0.2 + speedRatio * 0.3;
      ctx.fillStyle = hexToRgba(glowColor, nacPulse);
      ctx.beginPath(); ctx.arc(-r * 0.3, side * r * 0.55, 1.5 + speedRatio, 0, Math.PI * 2); ctx.fill();
      // Nacelle glow halo
      const nacGrad = ctx.createRadialGradient(-r * 0.3, side * r * 0.55, 0, -r * 0.3, side * r * 0.55, 5 + speedRatio * 3);
      nacGrad.addColorStop(0, hexToRgba(glowColor, nacPulse * 0.4));
      nacGrad.addColorStop(1, 'rgba(0,0,0,0)');
      ctx.fillStyle = nacGrad;
      ctx.beginPath(); ctx.arc(-r * 0.3, side * r * 0.55, 5 + speedRatio * 3, 0, Math.PI * 2); ctx.fill();
    }
    
    // Canard wings
    ctx.strokeStyle = hexToRgba(glowColor, 0.6); ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(r * 1.0, -r * 0.1); ctx.lineTo(r * 0.5, -r * 0.5);
    ctx.moveTo(r * 1.0, r * 0.1); ctx.lineTo(r * 0.5, r * 0.5);
    ctx.stroke();
    
    // Speed lines - more intense at high velocity
    if (speed > p.speed * 0.2) {
      const lineAlpha = Math.min(0.3, speedRatio * 0.4);
      ctx.strokeStyle = hexToRgba(color, lineAlpha); ctx.lineWidth = 0.5 + speedRatio * 0.5;
      for (let i = -2; i <= 2; i++) {
        const lineLen = 8 + speedRatio * 25 + Math.sin(time * 12 + i * 3) * 3;
        ctx.beginPath(); 
        ctx.moveTo(-r * 0.6, i * 2.5); 
        ctx.lineTo(-r - lineLen, i * 2.5); 
        ctx.stroke();
      }
    }
    
    // Nose laser emitter with pulsing halo
    const nosePulse = 0.6 + Math.sin(time * 8) * 0.3;
    ctx.fillStyle = hexToRgba('#ffffff', nosePulse);
    ctx.beginPath(); ctx.arc(r * 1.8, 0, 1.2, 0, Math.PI * 2); ctx.fill();
    const noseGrad = ctx.createRadialGradient(r * 1.8, 0, 0, r * 1.8, 0, 4);
    noseGrad.addColorStop(0, hexToRgba(color, nosePulse * 0.4));
    noseGrad.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = noseGrad;
    ctx.beginPath(); ctx.arc(r * 1.8, 0, 4, 0, Math.PI * 2); ctx.fill();
    
  } else if (p.class === 'titan') {
    // === TITAN: Heavy armored gunship ===
    ctx.beginPath();
    ctx.moveTo(r * 1.5, 0);
    ctx.lineTo(r * 0.6, -r * 0.45);
    ctx.lineTo(r * 0.1, -r * 0.6);
    ctx.lineTo(-r * 0.3, -r * 1.15);
    ctx.lineTo(-r * 0.8, -r * 1.05);
    ctx.lineTo(-r * 0.9, -r * 0.6);
    ctx.lineTo(-r, -r * 0.3);
    ctx.lineTo(-r, r * 0.3);
    ctx.lineTo(-r * 0.9, r * 0.6);
    ctx.lineTo(-r * 0.8, r * 1.05);
    ctx.lineTo(-r * 0.3, r * 1.15);
    ctx.lineTo(r * 0.1, r * 0.6);
    ctx.lineTo(r * 0.6, r * 0.45);
    ctx.closePath();
    ctx.fillStyle = hexToRgba(color, 0.18 + speedRatio * 0.05); ctx.fill();
    ctx.strokeStyle = color; ctx.lineWidth = 2; ctx.stroke();
    ctx.strokeStyle = hexToRgba(glowColor, 0.25); ctx.lineWidth = 0.8;
    ctx.beginPath();
    ctx.moveTo(r * 0.4, -r * 0.35); ctx.lineTo(-r * 0.7, -r * 0.35);
    ctx.moveTo(r * 0.4, r * 0.35); ctx.lineTo(-r * 0.7, r * 0.35);
    ctx.moveTo(-r * 0.4, -r * 0.8); ctx.lineTo(-r * 0.4, r * 0.8);
    ctx.moveTo(r * 0.2, -r * 0.4); ctx.lineTo(-r * 0.5, -r * 0.9);
    ctx.moveTo(r * 0.2, r * 0.4); ctx.lineTo(-r * 0.5, r * 0.9);
    ctx.stroke();
    for (const side of [-1, 1]) {
      ctx.fillStyle = hexToRgba(color, 0.4);
      ctx.fillRect(r * 0.8, side * r * 0.25 - 1.5, r * 0.5, 3);
      ctx.strokeStyle = color; ctx.lineWidth = 0.8;
      ctx.strokeRect(r * 0.8, side * r * 0.25 - 1.5, r * 0.5, 3);
      const barrelHeat = attackProg > 0.3 ? (attackProg - 0.3) / 0.7 : 0;
      if (barrelHeat > 0) {
        ctx.fillStyle = hexToRgba('#ffffff', barrelHeat * 0.5);
        ctx.beginPath(); ctx.arc(r * 1.3, side * r * 0.25, 2 + barrelHeat * 2, 0, Math.PI * 2); ctx.fill();
      }
    }
    const armorPulse = 0.3 + Math.sin(time * 2) * 0.15 + speedRatio * 0.2;
    ctx.fillStyle = hexToRgba(glowColor, armorPulse);
    ctx.beginPath(); ctx.arc(-r * 0.3, -r * 1.0, 2 + armorPulse * 2, 0, Math.PI * 2); ctx.fill();
    ctx.beginPath(); ctx.arc(-r * 0.3, r * 1.0, 2 + armorPulse * 2, 0, Math.PI * 2); ctx.fill();
    for (const sy of [-1, 1]) {
      const shGrad = ctx.createRadialGradient(-r * 0.3, sy * r * 1.0, 0, -r * 0.3, sy * r * 1.0, 6);
      shGrad.addColorStop(0, hexToRgba(glowColor, armorPulse * 0.4));
      shGrad.addColorStop(1, 'rgba(0,0,0,0)');
      ctx.fillStyle = shGrad;
      ctx.beginPath(); ctx.arc(-r * 0.3, sy * r * 1.0, 6, 0, Math.PI * 2); ctx.fill();
    }
    const reactPulse = 0.4 + Math.sin(time * 3) * 0.15 + attackFlare * 0.3;
    const reactGrad = ctx.createRadialGradient(0, 0, 1, 0, 0, r * 0.4);
    reactGrad.addColorStop(0, hexToRgba('#ffffff', reactPulse));
    reactGrad.addColorStop(0.3, hexToRgba(color, reactPulse * 0.6));
    reactGrad.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = reactGrad;
    ctx.beginPath(); ctx.arc(-r * 0.2, 0, r * 0.4, 0, Math.PI * 2); ctx.fill();
    if (p.attackTimer > p.attackCooldown * 0.4) {
      const slashProg = (p.attackTimer / p.attackCooldown - 0.4) / 0.6;
      ctx.beginPath(); ctx.moveTo(0, 0);
      ctx.arc(0, 0, WARRIOR_ATTACK_RANGE, -0.8 + (1 - slashProg) * 1.2, -0.8 + (1 - slashProg) * 1.2 + 1.0);
      ctx.closePath();
      const sg = ctx.createRadialGradient(0, 0, r, 0, 0, WARRIOR_ATTACK_RANGE);
      sg.addColorStop(0, `rgba(255,107,0,${0.5 * slashProg})`);
      sg.addColorStop(1, 'rgba(255,107,0,0)');
      ctx.fillStyle = sg; ctx.fill();
      ctx.strokeStyle = hexToRgba('#ffaa55', slashProg * 0.6);
      ctx.lineWidth = 1.5;
      ctx.stroke();
    }

  } else if (p.class === 'spectre') {
    // === SPECTRE: Curved stealth blade with phase shimmer ===
    const phase = Math.sin(time * 5) * 0.15;
    ctx.globalAlpha = 0.85 + phase;
    ctx.beginPath();
    ctx.moveTo(r * 2.0, 0);
    ctx.quadraticCurveTo(r * 1.2, -r * 0.5, r * 0.2, -r * 0.6);
    ctx.lineTo(-r * 0.4, -r * 0.8);
    ctx.quadraticCurveTo(-r * 0.7, -r * 0.4, -r * 0.6, 0);
    ctx.quadraticCurveTo(-r * 0.7, r * 0.4, -r * 0.4, r * 0.8);
    ctx.lineTo(r * 0.2, r * 0.6);
    ctx.quadraticCurveTo(r * 1.2, r * 0.5, r * 2.0, 0);
    ctx.closePath();
    ctx.fillStyle = hexToRgba(color, 0.12 + speedRatio * 0.06); ctx.fill();
    ctx.strokeStyle = color; ctx.lineWidth = 1.2; ctx.stroke();
    // Phase dashed lines
    ctx.strokeStyle = hexToRgba(glowColor, 0.4 + Math.sin(time * 8) * 0.3);
    ctx.lineWidth = 0.7;
    ctx.setLineDash([4, 5]);
    ctx.beginPath();
    ctx.moveTo(r * 1.5, -r * 0.15); ctx.lineTo(-r * 0.3, -r * 0.65);
    ctx.moveTo(r * 1.5, r * 0.15); ctx.lineTo(-r * 0.3, r * 0.65);
    ctx.stroke();
    ctx.setLineDash([]);
    // Ghost afterimage trail
    for (let i = 1; i <= 3; i++) {
      const offset = i * 6;
      const trailAlpha = 0.08 * (4 - i);
      ctx.fillStyle = hexToRgba(color, trailAlpha);
      ctx.beginPath();
      ctx.moveTo(r * 2.0 - offset, 0);
      ctx.quadraticCurveTo(r * 1.2 - offset, -r * 0.4, r * 0.2 - offset, -r * 0.5);
      ctx.quadraticCurveTo(-r * 0.5 - offset, 0, r * 0.2 - offset, r * 0.5);
      ctx.quadraticCurveTo(r * 1.2 - offset, r * 0.4, r * 2.0 - offset, 0);
      ctx.closePath(); ctx.fill();
    }
    // Core ghost eye
    const ghostPulse = 0.5 + Math.sin(time * 6) * 0.4;
    const ghostGrad = ctx.createRadialGradient(r * 0.3, 0, 0, r * 0.3, 0, r * 0.4);
    ghostGrad.addColorStop(0, hexToRgba('#ffffff', ghostPulse));
    ghostGrad.addColorStop(0.4, hexToRgba(color, ghostPulse * 0.5));
    ghostGrad.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = ghostGrad;
    ctx.beginPath(); ctx.arc(r * 0.3, 0, r * 0.4, 0, Math.PI * 2); ctx.fill();
    ctx.globalAlpha = 1;

  } else if (p.class === 'valkyrie') {
    // === VALKYRIE: Angular wings spread wide like a bird of war ===
    ctx.beginPath();
    ctx.moveTo(r * 1.8, 0);
    ctx.lineTo(r * 0.5, -r * 0.3);
    ctx.lineTo(r * 0.1, -r * 0.4);
    ctx.lineTo(-r * 0.2, -r * 1.4);
    ctx.lineTo(-r * 0.5, -r * 1.2);
    ctx.lineTo(-r * 0.3, -r * 0.35);
    ctx.lineTo(-r * 0.6, -r * 0.2);
    ctx.lineTo(-r * 0.6, r * 0.2);
    ctx.lineTo(-r * 0.3, r * 0.35);
    ctx.lineTo(-r * 0.5, r * 1.2);
    ctx.lineTo(-r * 0.2, r * 1.4);
    ctx.lineTo(r * 0.1, r * 0.4);
    ctx.lineTo(r * 0.5, r * 0.3);
    ctx.closePath();
    ctx.fillStyle = hexToRgba(color, 0.15 + speedRatio * 0.06); ctx.fill();
    ctx.strokeStyle = color; ctx.lineWidth = 1.5; ctx.stroke();
    // Wing energy spear lines
    const spearPulse = 0.5 + Math.sin(time * 5) * 0.3;
    ctx.strokeStyle = hexToRgba(glowColor, spearPulse); ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(-r * 0.2, -r * 1.4); ctx.lineTo(r * 0.3, -r * 0.2);
    ctx.moveTo(-r * 0.2, r * 1.4); ctx.lineTo(r * 0.3, r * 0.2);
    ctx.stroke();
    // Wing tip gems with halos
    for (const sy of [-1, 1]) {
      ctx.fillStyle = hexToRgba('#ffffff', spearPulse);
      ctx.beginPath(); ctx.arc(-r * 0.2, sy * r * 1.35, 2, 0, Math.PI * 2); ctx.fill();
      const tipGrad = ctx.createRadialGradient(-r * 0.2, sy * r * 1.35, 0, -r * 0.2, sy * r * 1.35, 6);
      tipGrad.addColorStop(0, hexToRgba(glowColor, spearPulse * 0.5));
      tipGrad.addColorStop(1, 'rgba(0,0,0,0)');
      ctx.fillStyle = tipGrad;
      ctx.beginPath(); ctx.arc(-r * 0.2, sy * r * 1.35, 6, 0, Math.PI * 2); ctx.fill();
    }
    // Rapid-fire emitters at nose
    const nosePulse = 0.6 + Math.sin(time * 10) * 0.3;
    ctx.fillStyle = hexToRgba(color, nosePulse);
    ctx.beginPath(); ctx.arc(r * 1.6, -r * 0.08, 1.5, 0, Math.PI * 2); ctx.fill();
    ctx.beginPath(); ctx.arc(r * 1.6, r * 0.08, 1.5, 0, Math.PI * 2); ctx.fill();
    // Inner wing structure
    ctx.strokeStyle = hexToRgba(glowColor, 0.2); ctx.lineWidth = 0.5;
    ctx.beginPath();
    ctx.moveTo(r * 0.3, -r * 0.25); ctx.lineTo(-r * 0.35, -r * 1.0);
    ctx.moveTo(r * 0.3, r * 0.25); ctx.lineTo(-r * 0.35, r * 1.0);
    ctx.stroke();

  } else {
    // === JUGGERNAUT: Bulky hexagonal fortress ===
    const sides = 6;
    ctx.beginPath();
    for (let i = 0; i <= sides; i++) {
      const a = (i / sides) * Math.PI * 2 - Math.PI / 6;
      const rr = r * 1.3;
      const px = Math.cos(a) * rr;
      const py = Math.sin(a) * rr * 0.85;
      if (i === 0) ctx.moveTo(px, py); else ctx.lineTo(px, py);
    }
    ctx.closePath();
    ctx.fillStyle = hexToRgba(color, 0.2 + speedRatio * 0.05); ctx.fill();
    ctx.strokeStyle = color; ctx.lineWidth = 2.5; ctx.stroke();
    // Inner armor hex
    ctx.strokeStyle = hexToRgba(glowColor, 0.3); ctx.lineWidth = 1;
    ctx.beginPath();
    for (let i = 0; i <= sides; i++) {
      const a = (i / sides) * Math.PI * 2 - Math.PI / 6;
      const rr = r * 0.8;
      const px = Math.cos(a) * rr;
      const py = Math.sin(a) * rr * 0.85;
      if (i === 0) ctx.moveTo(px, py); else ctx.lineTo(px, py);
    }
    ctx.closePath(); ctx.stroke();
    // Cross armor plating
    ctx.strokeStyle = hexToRgba(glowColor, 0.15); ctx.lineWidth = 0.6;
    ctx.beginPath();
    ctx.moveTo(-r * 0.8, 0); ctx.lineTo(r * 0.8, 0);
    ctx.moveTo(0, -r * 0.7); ctx.lineTo(0, r * 0.7);
    ctx.stroke();
    // Triple turret barrels
    for (const side of [-1, 0, 1]) {
      ctx.fillStyle = hexToRgba(color, 0.5);
      ctx.fillRect(r * 0.9, side * r * 0.35 - 1.5, r * 0.6, 3);
      ctx.strokeStyle = color; ctx.lineWidth = 0.8;
      ctx.strokeRect(r * 0.9, side * r * 0.35 - 1.5, r * 0.6, 3);
      const barrelHeat = attackProg > 0.3 ? (attackProg - 0.3) / 0.7 : 0;
      if (barrelHeat > 0) {
        ctx.fillStyle = hexToRgba('#ffffff', barrelHeat * 0.4);
        ctx.beginPath(); ctx.arc(r * 1.5, side * r * 0.35, 2 + barrelHeat * 2, 0, Math.PI * 2); ctx.fill();
      }
    }
    // Massive reactor core
    const corePulse = 0.4 + Math.sin(time * 2) * 0.2 + attackFlare * 0.3;
    const coreGrad = ctx.createRadialGradient(0, 0, 1, 0, 0, r * 0.5);
    coreGrad.addColorStop(0, hexToRgba('#ffffff', corePulse));
    coreGrad.addColorStop(0.3, hexToRgba(color, corePulse * 0.6));
    coreGrad.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = coreGrad;
    ctx.beginPath(); ctx.arc(0, 0, r * 0.5, 0, Math.PI * 2); ctx.fill();
    // Corner armor nodes
    for (let i = 0; i < sides; i++) {
      const a = (i / sides) * Math.PI * 2 - Math.PI / 6;
      const nx = Math.cos(a) * r * 1.25;
      const ny = Math.sin(a) * r * 1.25 * 0.85;
      const nodePulse = 0.3 + Math.sin(time * 3 + i) * 0.15;
      ctx.fillStyle = hexToRgba(glowColor, nodePulse);
      ctx.beginPath(); ctx.arc(nx, ny, 2, 0, Math.PI * 2); ctx.fill();
    }
  }

  // Cockpit/nose glow (all ships)
  const cockpitX = p.class === 'interceptor' ? r * 0.5 : r * 0.4;
  const cockpitR = p.class === 'titan' ? 3.5 : 2.5;
  const cockpitGrad = ctx.createRadialGradient(cockpitX, 0, 0, cockpitX, 0, cockpitR + 3);
  cockpitGrad.addColorStop(0, '#ffffff');
  cockpitGrad.addColorStop(0.3, glowColor);
  cockpitGrad.addColorStop(1, hexToRgba(color, 0));
  ctx.fillStyle = cockpitGrad;
  ctx.beginPath(); ctx.arc(cockpitX, 0, cockpitR + 1, 0, Math.PI * 2); ctx.fill();
  ctx.shadowBlur = 0;

  // Power-up visual indicators (enhanced)
  if (p.speedBoostTimer > 0) {
    const boostPulse = 0.4 + Math.sin(time * 10) * 0.2;
    // Multiple speed boost trails
    for (let i = 0; i < 3; i++) {
      ctx.fillStyle = hexToRgba('#00e5ff', boostPulse * (1 - i * 0.25));
      ctx.beginPath();
      ctx.moveTo(-r * 0.5, -2 + i * 0.5);
      ctx.lineTo(-r - totalThrustLen - 20 - i * 8, 0);
      ctx.lineTo(-r * 0.5, 2 - i * 0.5);
      ctx.closePath(); ctx.fill();
    }
  }
  if (p.tripleTimer > 0) {
    const tPulse = 0.5 + Math.sin(time * 6) * 0.3;
    ctx.fillStyle = hexToRgba('#ff1493', tPulse);
    ctx.beginPath(); ctx.arc(r * 1.2, -4, 2 + tPulse, 0, Math.PI * 2); ctx.fill();
    ctx.beginPath(); ctx.arc(r * 1.2, 4, 2 + tPulse, 0, Math.PI * 2); ctx.fill();
    ctx.beginPath(); ctx.arc(r * 1.5, 0, 1.5 + tPulse, 0, Math.PI * 2); ctx.fill();
  }
  
  ctx.globalAlpha = 1;
  ctx.restore();
}

// --- ENEMIES --- Enhanced with unique visuals per behavior
function drawEnemy(ctx: CanvasRenderingContext2D, e: Enemy, time: number, state?: GameState) {
  ctx.save();
  ctx.translate(e.pos.x, e.pos.y);
  if (e.flashTimer > 0) ctx.globalAlpha = 0.5 + Math.sin(Date.now() * 0.05) * 0.5;
  const color = getEnemyColor(e.type);

  if (e.isBoss) {
    const auraR = e.radius + 25 + Math.sin(time * 3) * 8;
    const aGrad = ctx.createRadialGradient(0, 0, e.radius, 0, 0, auraR);
    aGrad.addColorStop(0, hexToRgba(color, 0.3));
    aGrad.addColorStop(0.5, hexToRgba(color, 0.08));
    aGrad.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = aGrad;
    ctx.beginPath(); ctx.arc(0, 0, auraR, 0, Math.PI * 2); ctx.fill();
    for (let i = 0; i < 10; i++) {
      const a = time * 0.8 + (i / 10) * Math.PI * 2;
      const ox = Math.cos(a) * (e.radius + 18);
      const oy = Math.sin(a) * (e.radius + 18);
      ctx.fillStyle = hexToRgba(color, 0.5);
      ctx.beginPath(); ctx.arc(ox, oy, 2.5, 0, Math.PI * 2); ctx.fill();
      ctx.strokeStyle = hexToRgba(color, 0.1); ctx.lineWidth = 0.5;
      ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(ox, oy); ctx.stroke();
    }
  }

  ctx.shadowColor = color; ctx.shadowBlur = 12;
  const rot = time * 2;

  if (e.type === 'drone') {
    // Enhanced drone: spinning diamond with pulsing inner eye and orbiting dots
    ctx.save(); ctx.rotate(rot);
    drawNeonShape(ctx, 4, e.radius, color);
    // Inner cross
    ctx.strokeStyle = hexToRgba(color, 0.4); ctx.lineWidth = 0.8;
    ctx.beginPath();
    ctx.moveTo(-e.radius * 0.5, 0); ctx.lineTo(e.radius * 0.5, 0);
    ctx.moveTo(0, -e.radius * 0.5); ctx.lineTo(0, e.radius * 0.5);
    ctx.stroke();
    // Pulsing eye
    const eyePulse = 0.5 + Math.sin(time * 6) * 0.4;
    const eyeGrad = ctx.createRadialGradient(0, 0, 0, 0, 0, e.radius * 0.35);
    eyeGrad.addColorStop(0, hexToRgba('#ffffff', eyePulse));
    eyeGrad.addColorStop(0.5, hexToRgba(color, eyePulse * 0.6));
    eyeGrad.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = eyeGrad;
    ctx.beginPath(); ctx.arc(0, 0, e.radius * 0.35, 0, Math.PI * 2); ctx.fill();
    ctx.restore();
    // Orbiting micro-dots
    for (let i = 0; i < 4; i++) {
      const oa = time * 5 + (i / 4) * Math.PI * 2;
      const ox = Math.cos(oa) * (e.radius + 4);
      const oy = Math.sin(oa) * (e.radius + 4);
      ctx.fillStyle = hexToRgba(color, 0.4);
      ctx.beginPath(); ctx.arc(ox, oy, 1, 0, Math.PI * 2); ctx.fill();
    }
  } else if (e.type === 'splitter') {
    // Enhanced splitter: mitosis animation with wobbling membrane
    const wobble = Math.sin(time * 4) * 0.08;
    ctx.save(); ctx.scale(1 + wobble, 1 - wobble);
    ctx.beginPath(); ctx.arc(0, 0, e.radius, 0, Math.PI * 2);
    ctx.fillStyle = hexToRgba(color, 0.15); ctx.fill();
    ctx.strokeStyle = color; ctx.lineWidth = 1.5; ctx.stroke();
    // Division line that pulses
    const divPulse = 0.3 + Math.sin(time * 3) * 0.2;
    ctx.strokeStyle = hexToRgba(color, divPulse); ctx.lineWidth = 1.2;
    ctx.beginPath(); ctx.moveTo(0, -e.radius); ctx.lineTo(0, e.radius); ctx.stroke();
    // Twin nuclei
    for (const sx of [-0.35, 0.35]) {
      const nucPulse = 0.5 + Math.sin(time * 5 + sx * 10) * 0.3;
      const nucGrad = ctx.createRadialGradient(e.radius * sx, 0, 0, e.radius * sx, 0, e.radius * 0.3);
      nucGrad.addColorStop(0, hexToRgba('#ffffff', nucPulse));
      nucGrad.addColorStop(0.5, hexToRgba(color, nucPulse * 0.5));
      nucGrad.addColorStop(1, 'rgba(0,0,0,0)');
      ctx.fillStyle = nucGrad;
      ctx.beginPath(); ctx.arc(e.radius * sx, 0, e.radius * 0.3, 0, Math.PI * 2); ctx.fill();
    }
    // Membrane particles
    for (let i = 0; i < 8; i++) {
      const a = (i / 8) * Math.PI * 2 + time * 2;
      const pr = e.radius + Math.sin(time * 3 + i) * 3;
      ctx.fillStyle = hexToRgba(color, 0.3);
      ctx.beginPath(); ctx.arc(Math.cos(a) * pr, Math.sin(a) * pr, 1, 0, Math.PI * 2); ctx.fill();
    }
    ctx.restore();
  } else if (e.type === 'dasher') {
    // Enhanced dasher: streak effect when dashing, charging glow
    const isDashing = e.dashState === 'dashing';
    const isCharging = e.dashState === 'tracking' && e.dashTimer !== undefined && e.dashTimer < 0.3;
    const faceAngle = e.dashAngle ?? rot * 2;
    
    // Dash afterimage trail
    if (isDashing) {
      for (let i = 1; i <= 4; i++) {
        const trailAlpha = (1 - i * 0.22) * 0.3;
        const tx = -Math.cos(faceAngle) * i * 8;
        const ty = -Math.sin(faceAngle) * i * 8;
        ctx.save(); ctx.translate(tx, ty); ctx.rotate(faceAngle);
        ctx.globalAlpha = trailAlpha;
        ctx.beginPath();
        ctx.moveTo(e.radius * 1.3, 0);
        ctx.lineTo(-e.radius * 0.8, -e.radius * 0.9);
        ctx.lineTo(-e.radius * 0.4, 0);
        ctx.lineTo(-e.radius * 0.8, e.radius * 0.9);
        ctx.closePath();
        ctx.fillStyle = hexToRgba(color, 0.15); ctx.fill();
        ctx.restore();
      }
      ctx.globalAlpha = e.flashTimer > 0 ? 0.5 + Math.sin(Date.now() * 0.05) * 0.5 : 1;
    }
    
    ctx.save(); ctx.rotate(faceAngle);
    ctx.beginPath();
    ctx.moveTo(e.radius * 1.3, 0);
    ctx.lineTo(-e.radius * 0.8, -e.radius * 0.9);
    ctx.lineTo(-e.radius * 0.4, 0);
    ctx.lineTo(-e.radius * 0.8, e.radius * 0.9);
    ctx.closePath();
    ctx.fillStyle = hexToRgba(color, isDashing ? 0.25 : 0.12); ctx.fill();
    ctx.strokeStyle = color; ctx.lineWidth = isDashing ? 2.5 : 1.5; ctx.stroke();
    
    // Speed lines when dashing
    if (isDashing) {
      ctx.strokeStyle = hexToRgba(color, 0.5); ctx.lineWidth = 1;
      for (let i = 0; i < 5; i++) {
        const y = (i - 2) * 3;
        const len = 10 + Math.random() * 15;
        ctx.beginPath(); ctx.moveTo(-e.radius, y); ctx.lineTo(-e.radius - len, y); ctx.stroke();
      }
    }
    
    // Charge-up glow
    if (isCharging) {
      const chargePulse = 0.4 + Math.sin(time * 20) * 0.3;
      const chargeGrad = ctx.createRadialGradient(0, 0, 0, 0, 0, e.radius * 1.5);
      chargeGrad.addColorStop(0, hexToRgba('#ffffff', chargePulse));
      chargeGrad.addColorStop(0.3, hexToRgba(color, chargePulse * 0.6));
      chargeGrad.addColorStop(1, 'rgba(0,0,0,0)');
      ctx.fillStyle = chargeGrad;
      ctx.beginPath(); ctx.arc(0, 0, e.radius * 1.5, 0, Math.PI * 2); ctx.fill();
    }
    
    // Nose light
    const nosePulse = 0.6 + Math.sin(time * 8) * 0.3;
    ctx.fillStyle = hexToRgba('#ffffff', nosePulse);
    ctx.beginPath(); ctx.arc(e.radius * 1.0, 0, 1.5, 0, Math.PI * 2); ctx.fill();
    ctx.restore();
  } else if (e.type === 'tank') {
    // Enhanced tank: heavy hex with shield layers, rotating turret with barrel heat
    const tankRot = rot * 0.3;
    ctx.save(); ctx.rotate(tankRot);
    drawNeonShape(ctx, 6, e.radius, color);
    // Inner shield ring
    drawNeonShape(ctx, 6, e.radius * 0.65, color, 0.35);
    // Armor plating lines
    ctx.strokeStyle = hexToRgba(color, 0.2); ctx.lineWidth = 0.6;
    for (let i = 0; i < 6; i++) {
      const a1 = (i / 6) * Math.PI * 2 - Math.PI / 2;
      const a2 = ((i + 0.5) / 6) * Math.PI * 2 - Math.PI / 2;
      ctx.beginPath();
      ctx.moveTo(Math.cos(a1) * e.radius * 0.65, Math.sin(a1) * e.radius * 0.65);
      ctx.lineTo(Math.cos(a2) * e.radius, Math.sin(a2) * e.radius);
      ctx.stroke();
    }
    ctx.restore();
    
    // Rotating turret aimed at player
    const turretAngle = state ? Math.atan2(state.player.pos.y - e.pos.y, state.player.pos.x - e.pos.x) : time * 1.5;
    ctx.save(); ctx.rotate(turretAngle);
    ctx.strokeStyle = hexToRgba(color, 0.8); ctx.lineWidth = 3;
    ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(e.radius * 1.2, 0); ctx.stroke();
    // Barrel tip
    ctx.fillStyle = color;
    ctx.beginPath(); ctx.arc(e.radius * 1.2, 0, 3, 0, Math.PI * 2); ctx.fill();
    // Barrel heat glow
    const heatPulse = 0.3 + Math.sin(time * 4) * 0.2;
    const heatGrad = ctx.createRadialGradient(e.radius * 1.2, 0, 0, e.radius * 1.2, 0, 6);
    heatGrad.addColorStop(0, hexToRgba('#ffffff', heatPulse));
    heatGrad.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = heatGrad;
    ctx.beginPath(); ctx.arc(e.radius * 1.2, 0, 6, 0, Math.PI * 2); ctx.fill();
    ctx.restore();
    
    // Central reactor
    const reactGrad = ctx.createRadialGradient(0, 0, 0, 0, 0, e.radius * 0.35);
    reactGrad.addColorStop(0, hexToRgba('#ffffff', 0.5));
    reactGrad.addColorStop(0.5, hexToRgba(color, 0.3));
    reactGrad.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = reactGrad;
    ctx.beginPath(); ctx.arc(0, 0, e.radius * 0.35, 0, Math.PI * 2); ctx.fill();
  } else if (e.type === 'mothership') {
    // Enhanced mothership: pulsing pentagon with drone bays and energy web
    ctx.save(); ctx.rotate(rot * 0.3); drawNeonShape(ctx, 5, e.radius, color); ctx.restore();
    ctx.save(); ctx.rotate(-rot * 0.5); drawNeonShape(ctx, 5, e.radius * 0.6, color, 0.4); ctx.restore();
    // Drone bay lights
    for (let i = 0; i < 5; i++) {
      const a = (i / 5) * Math.PI * 2 + rot * 0.3;
      const bayPulse = 0.4 + Math.sin(time * 4 + i * 1.2) * 0.3;
      const bx = Math.cos(a) * e.radius * 0.8;
      const by = Math.sin(a) * e.radius * 0.8;
      const bayGrad = ctx.createRadialGradient(bx, by, 0, bx, by, 6);
      bayGrad.addColorStop(0, hexToRgba('#ff0040', bayPulse));
      bayGrad.addColorStop(1, 'rgba(0,0,0,0)');
      ctx.fillStyle = bayGrad;
      ctx.beginPath(); ctx.arc(bx, by, 6, 0, Math.PI * 2); ctx.fill();
    }
    // Energy web connecting bays
    ctx.strokeStyle = hexToRgba(color, 0.15); ctx.lineWidth = 0.5;
    for (let i = 0; i < 5; i++) {
      for (let j = i + 1; j < 5; j++) {
        const a1 = (i / 5) * Math.PI * 2 + rot * 0.3;
        const a2 = (j / 5) * Math.PI * 2 + rot * 0.3;
        ctx.beginPath();
        ctx.moveTo(Math.cos(a1) * e.radius * 0.8, Math.sin(a1) * e.radius * 0.8);
        ctx.lineTo(Math.cos(a2) * e.radius * 0.8, Math.sin(a2) * e.radius * 0.8);
        ctx.stroke();
      }
    }
    // Central core
    const cg = ctx.createRadialGradient(0, 0, 2, 0, 0, e.radius * 0.35);
    cg.addColorStop(0, hexToRgba('#ffffff', 0.6)); cg.addColorStop(0.5, hexToRgba(color, 0.4)); cg.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = cg; ctx.beginPath(); ctx.arc(0, 0, e.radius * 0.35, 0, Math.PI * 2); ctx.fill();
  } else if (e.type === 'vortex') {
    // Enhanced vortex: hypnotic spirals with pull field visualization
    ctx.save(); ctx.rotate(rot); drawNeonShape(ctx, 8, e.radius, color); ctx.restore();
    ctx.save(); ctx.rotate(-rot * 1.5); drawNeonShape(ctx, 8, e.radius * 0.55, color, 0.5); ctx.restore();
    // Dynamic spirals
    for (let i = 0; i < 6; i++) {
      const a = rot * 2.5 + (i / 6) * Math.PI * 2;
      const spiralAlpha = 0.15 + Math.sin(time * 3 + i) * 0.1;
      ctx.strokeStyle = hexToRgba(color, spiralAlpha); ctx.lineWidth = 1.2;
      ctx.beginPath();
      for (let t = 0; t < 1; t += 0.05) {
        const r = e.radius * 0.2 + t * e.radius * 0.8;
        const sa = a + t * 2;
        if (t === 0) ctx.moveTo(Math.cos(sa) * r, Math.sin(sa) * r);
        else ctx.lineTo(Math.cos(sa) * r, Math.sin(sa) * r);
      }
      ctx.stroke();
    }
    // Pull field rings
    for (let ri = 1; ri <= 3; ri++) {
      const ringR = e.radius + ri * 25;
      const ringAlpha = (0.08 - ri * 0.02) * (1 + Math.sin(time * 4 + ri) * 0.5);
      ctx.strokeStyle = hexToRgba(color, ringAlpha); ctx.lineWidth = 0.8;
      ctx.setLineDash([4, 4]); ctx.lineDashOffset = time * 30;
      ctx.beginPath(); ctx.arc(0, 0, ringR, 0, Math.PI * 2); ctx.stroke();
      ctx.setLineDash([]);
    }
    // Central vortex eye
    const vGrad = ctx.createRadialGradient(0, 0, 0, 0, 0, e.radius * 0.3);
    vGrad.addColorStop(0, hexToRgba('#ffffff', 0.6 + Math.sin(time * 5) * 0.2));
    vGrad.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = vGrad; ctx.beginPath(); ctx.arc(0, 0, e.radius * 0.3, 0, Math.PI * 2); ctx.fill();
  } else if (e.type === 'colossus') {
    // Enhanced colossus: massive pulsing diamond with shockwave rings
    const pulse = 1 + Math.sin(time * 2) * 0.05;
    ctx.save(); ctx.rotate(rot * 0.2); ctx.scale(pulse, pulse); drawNeonShape(ctx, 4, e.radius, color); ctx.restore();
    ctx.save(); ctx.rotate(-rot * 0.4); drawNeonShape(ctx, 4, e.radius * 0.5, color, 0.5); ctx.restore();
    // Energy cross-beams
    for (let i = 0; i < 4; i++) {
      const a = (i / 4) * Math.PI * 2 + rot * 0.2;
      const beamPulse = 0.3 + Math.sin(time * 3 + i * 0.5) * 0.2;
      ctx.strokeStyle = hexToRgba(color, beamPulse);
      ctx.lineWidth = 2;
      ctx.beginPath(); ctx.moveTo(0, 0);
      ctx.lineTo(Math.cos(a) * e.radius * 0.9, Math.sin(a) * e.radius * 0.9); ctx.stroke();
      // Beam endpoint glow
      const bx = Math.cos(a) * e.radius * 0.9;
      const by = Math.sin(a) * e.radius * 0.9;
      ctx.fillStyle = hexToRgba(color, beamPulse * 0.6);
      ctx.beginPath(); ctx.arc(bx, by, 3, 0, Math.PI * 2); ctx.fill();
    }
    // Shockwave ring effect
    const shockPhase = (time * 0.8) % 1;
    const shockR = e.radius + shockPhase * 40;
    const shockAlpha = (1 - shockPhase) * 0.15;
    ctx.strokeStyle = hexToRgba(color, shockAlpha); ctx.lineWidth = 2;
    ctx.beginPath(); ctx.arc(0, 0, shockR, 0, Math.PI * 2); ctx.stroke();
    // Central reactor
    const cg2 = ctx.createRadialGradient(0, 0, 2, 0, 0, e.radius * 0.4);
    cg2.addColorStop(0, hexToRgba('#ffffff', 0.5 + Math.sin(time * 3) * 0.2));
    cg2.addColorStop(0.5, hexToRgba(color, 0.3));
    cg2.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = cg2; ctx.beginPath(); ctx.arc(0, 0, e.radius * 0.4, 0, Math.PI * 2); ctx.fill();
  } else if (e.type === 'fire_elemental') {
    // Fire elemental: flickering flame shape
    const flicker = Math.sin(time * 12) * 0.1;
    ctx.save(); ctx.scale(1 + flicker, 1 - flicker);
    ctx.beginPath();
    ctx.moveTo(0, -e.radius * 1.3);
    ctx.bezierCurveTo(e.radius * 0.8, -e.radius * 0.5, e.radius * 0.6, e.radius * 0.5, 0, e.radius);
    ctx.bezierCurveTo(-e.radius * 0.6, e.radius * 0.5, -e.radius * 0.8, -e.radius * 0.5, 0, -e.radius * 1.3);
    ctx.closePath();
    ctx.fillStyle = hexToRgba(color, 0.25); ctx.fill();
    ctx.strokeStyle = color; ctx.lineWidth = 1.5; ctx.stroke();
    // Inner flame
    ctx.fillStyle = hexToRgba('#ffff00', 0.3 + Math.sin(time * 8) * 0.15);
    ctx.beginPath(); ctx.arc(0, -e.radius * 0.2, e.radius * 0.4, 0, Math.PI * 2); ctx.fill();
    // Core
    ctx.fillStyle = hexToRgba('#ffffff', 0.5);
    ctx.beginPath(); ctx.arc(0, -e.radius * 0.2, e.radius * 0.15, 0, Math.PI * 2); ctx.fill();
    ctx.restore();
  } else if (e.type === 'void_ghost') {
    // Void ghost: semi-transparent floating specter
    const ghostAlpha = 0.4 + Math.sin(time * 4) * 0.2;
    ctx.globalAlpha = ghostAlpha;
    ctx.beginPath();
    ctx.moveTo(0, -e.radius);
    ctx.quadraticCurveTo(e.radius * 1.2, -e.radius * 0.3, e.radius * 0.8, e.radius * 0.3);
    ctx.quadraticCurveTo(e.radius * 0.4, e.radius * 0.8, e.radius * 0.2, e.radius);
    ctx.quadraticCurveTo(0, e.radius * 0.7, -e.radius * 0.2, e.radius);
    ctx.quadraticCurveTo(-e.radius * 0.4, e.radius * 0.8, -e.radius * 0.8, e.radius * 0.3);
    ctx.quadraticCurveTo(-e.radius * 1.2, -e.radius * 0.3, 0, -e.radius);
    ctx.closePath();
    ctx.fillStyle = hexToRgba(color, 0.2); ctx.fill();
    ctx.strokeStyle = color; ctx.lineWidth = 1; ctx.stroke();
    // Eyes
    ctx.fillStyle = hexToRgba('#ffffff', 0.8);
    ctx.beginPath(); ctx.arc(-e.radius * 0.25, -e.radius * 0.15, 2, 0, Math.PI * 2); ctx.fill();
    ctx.beginPath(); ctx.arc(e.radius * 0.25, -e.radius * 0.15, 2, 0, Math.PI * 2); ctx.fill();
    ctx.globalAlpha = 1;
  } else if (e.type === 'crystal_golem') {
    // Crystal golem: heavy geometric crystal shape
    const pulse = 1 + Math.sin(time * 2) * 0.04;
    ctx.save(); ctx.rotate(rot * 0.15); ctx.scale(pulse, pulse);
    // Body - large hexagonal crystal
    drawNeonShape(ctx, 6, e.radius, color);
    drawNeonShape(ctx, 6, e.radius * 0.5, color, 0.5);
    // Crystal shards sticking out
    for (let i = 0; i < 6; i++) {
      const a = (i / 6) * Math.PI * 2;
      const sx = Math.cos(a) * e.radius * 0.8;
      const sy = Math.sin(a) * e.radius * 0.8;
      ctx.save(); ctx.translate(sx, sy); ctx.rotate(a + time * 0.5);
      ctx.fillStyle = hexToRgba(color, 0.3);
      ctx.beginPath();
      ctx.moveTo(0, -4); ctx.lineTo(3, 4); ctx.lineTo(-3, 4); ctx.closePath();
      ctx.fill();
      ctx.restore();
    }
    // Central glow
    const cGrad = ctx.createRadialGradient(0, 0, 0, 0, 0, e.radius * 0.4);
    cGrad.addColorStop(0, hexToRgba('#ffffff', 0.4));
    cGrad.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = cGrad;
    ctx.beginPath(); ctx.arc(0, 0, e.radius * 0.4, 0, Math.PI * 2); ctx.fill();
    ctx.restore();
  } else {
    ctx.beginPath(); ctx.arc(0, 0, e.radius, 0, Math.PI * 2);
    ctx.strokeStyle = color; ctx.lineWidth = 1.5; ctx.stroke();
  }

  ctx.shadowBlur = 0;
  if (e.hp < e.maxHp && (e.isBoss || e.maxHp > 20)) {
    const barW = e.radius * 2.4;
    const barH = e.isBoss ? 5 : 3;
    const barY = -e.radius - 10;
    ctx.fillStyle = 'rgba(0,0,0,0.6)';
    ctx.fillRect(-barW / 2 - 1, barY - 1, barW + 2, barH + 2);
    ctx.fillStyle = color;
    ctx.fillRect(-barW / 2, barY, barW * (e.hp / e.maxHp), barH);
  }
  ctx.restore();
}

// --- TRAIL ---
function drawTrail(ctx: CanvasRenderingContext2D, state: GameState, time: number) {
  const trail = state.trail;
  if (trail.length < 2) return;
  const color = getShipColor(state.player.class);
  
  for (let i = 0; i < trail.length; i++) {
    const t = trail[i];
    const alpha = (1 - t.age / 0.5) * 0.4;
    const size = (1 - t.age / 0.5) * 3;
    if (alpha <= 0) continue;
    
    const trailGrad = ctx.createRadialGradient(t.x, t.y, 0, t.x, t.y, size * 2);
    trailGrad.addColorStop(0, hexToRgba(color, alpha));
    trailGrad.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = trailGrad;
    ctx.beginPath(); ctx.arc(t.x, t.y, size * 2, 0, Math.PI * 2); ctx.fill();
    
    ctx.fillStyle = hexToRgba('#ffffff', alpha * 0.6);
    ctx.beginPath(); ctx.arc(t.x, t.y, size * 0.4, 0, Math.PI * 2); ctx.fill();
  }
}

// --- XP ORB ---
function drawXpOrb(ctx: CanvasRenderingContext2D, orb: XpOrb, time: number) {
  ctx.save();
  ctx.translate(orb.pos.x, orb.pos.y);
  
  const pulse = 1 + Math.sin(time * 8 + orb.pos.x * 0.1) * 0.2;
  const alpha = Math.min(1, orb.lifetime / 2);
  
  // Outer glow
  const glow = ctx.createRadialGradient(0, 0, 0, 0, 0, orb.radius * 3 * pulse);
  glow.addColorStop(0, `rgba(191,90,242,${0.3 * alpha})`);
  glow.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.fillStyle = glow;
  ctx.beginPath(); ctx.arc(0, 0, orb.radius * 3 * pulse, 0, Math.PI * 2); ctx.fill();
  
  // Core
  ctx.shadowColor = '#bf5af2';
  ctx.shadowBlur = 8;
  ctx.fillStyle = `rgba(224,176,255,${0.7 * alpha})`;
  ctx.beginPath(); ctx.arc(0, 0, orb.radius * pulse * 0.6, 0, Math.PI * 2); ctx.fill();
  ctx.fillStyle = `rgba(255,255,255,${0.5 * alpha})`;
  ctx.beginPath(); ctx.arc(0, 0, orb.radius * pulse * 0.3, 0, Math.PI * 2); ctx.fill();
  ctx.shadowBlur = 0;
  
  ctx.restore();
}

// --- ABILITY VISUALS ---
function drawAbilityVisuals(ctx: CanvasRenderingContext2D, state: GameState, time: number) {
  const p = state.player;
  const abilities = state.abilities;
  
  // Damage aura
  if (abilities.auraRadius > 0) {
    const auraPulse = 0.08 + Math.sin(time * 3) * 0.04;
    const auraGrad = ctx.createRadialGradient(p.pos.x, p.pos.y, p.radius, p.pos.x, p.pos.y, abilities.auraRadius);
    const auraColor = getShipColor(p.class);
    auraGrad.addColorStop(0, hexToRgba(auraColor, auraPulse));
    auraGrad.addColorStop(0.7, hexToRgba(auraColor, auraPulse * 0.3));
    auraGrad.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = auraGrad;
    ctx.beginPath(); ctx.arc(p.pos.x, p.pos.y, abilities.auraRadius, 0, Math.PI * 2); ctx.fill();
    // Aura edge
    ctx.strokeStyle = hexToRgba(auraColor, auraPulse * 0.5);
    ctx.lineWidth = 1;
    ctx.setLineDash([3, 3]); ctx.lineDashOffset = time * 20;
    ctx.beginPath(); ctx.arc(p.pos.x, p.pos.y, abilities.auraRadius, 0, Math.PI * 2); ctx.stroke();
    ctx.setLineDash([]);
  }
  
  // Orbital drones
  if (abilities.orbitals > 0) {
    const count = abilities.orbitals;
    const orbitalRadius = p.radius + 30;
    for (let i = 0; i < count; i++) {
      const angle = (time * 3) + (i / count) * Math.PI * 2;
      const ox = p.pos.x + Math.cos(angle) * orbitalRadius;
      const oy = p.pos.y + Math.sin(angle) * orbitalRadius;
      
      // Orbital glow
      const oGrad = ctx.createRadialGradient(ox, oy, 0, ox, oy, 8);
      oGrad.addColorStop(0, 'rgba(0,255,255,0.5)');
      oGrad.addColorStop(1, 'rgba(0,0,0,0)');
      ctx.fillStyle = oGrad;
      ctx.beginPath(); ctx.arc(ox, oy, 8, 0, Math.PI * 2); ctx.fill();
      
      // Orbital core
      ctx.shadowColor = '#0ff';
      ctx.shadowBlur = 6;
      ctx.fillStyle = '#0ff';
      ctx.beginPath(); ctx.arc(ox, oy, 3, 0, Math.PI * 2); ctx.fill();
      ctx.fillStyle = '#fff';
      ctx.beginPath(); ctx.arc(ox, oy, 1.5, 0, Math.PI * 2); ctx.fill();
      ctx.shadowBlur = 0;
    }
    // Orbit path
    ctx.strokeStyle = 'rgba(0,255,255,0.06)';
    ctx.lineWidth = 0.5;
    ctx.beginPath(); ctx.arc(p.pos.x, p.pos.y, orbitalRadius, 0, Math.PI * 2); ctx.stroke();
  }
}

function drawNeonShape(ctx: CanvasRenderingContext2D, sides: number, radius: number, color: string, alpha = 1) {
  ctx.beginPath();
  for (let i = 0; i <= sides; i++) {
    const a = (i / sides) * Math.PI * 2 - Math.PI / 2;
    const x = Math.cos(a) * radius;
    const y = Math.sin(a) * radius;
    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  }
  ctx.closePath();
  ctx.fillStyle = hexToRgba(color, 0.1 * alpha);
  ctx.fill();
  ctx.strokeStyle = hexToRgba(color, alpha);
  ctx.lineWidth = 1.5;
  ctx.stroke();
}

// --- PROJECTILE ---
function drawProjectile(ctx: CanvasRenderingContext2D, p: Projectile, time: number) {
  ctx.save();
  ctx.translate(p.pos.x, p.pos.y);

  // Trail glow
  const tg = ctx.createRadialGradient(0, 0, 1, 0, 0, p.radius * 4);
  tg.addColorStop(0, hexToRgba(p.color, 0.4));
  tg.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.fillStyle = tg;
  ctx.beginPath(); ctx.arc(0, 0, p.radius * 4, 0, Math.PI * 2); ctx.fill();

  // Core
  ctx.shadowColor = p.color;
  ctx.shadowBlur = 12;
  ctx.fillStyle = '#fff';
  ctx.beginPath(); ctx.arc(0, 0, p.radius * 0.6, 0, Math.PI * 2); ctx.fill();
  ctx.fillStyle = p.color;
  ctx.beginPath(); ctx.arc(0, 0, p.radius, 0, Math.PI * 2); ctx.fill();
  ctx.shadowBlur = 0;

  ctx.restore();
}

// --- PARTICLE ---
function drawParticle(ctx: CanvasRenderingContext2D, p: Particle) {
  const alpha = p.lifetime / p.maxLifetime;
  ctx.save();
  ctx.globalAlpha = alpha;

  const glowR = p.size * alpha * 3;
  const pg = ctx.createRadialGradient(p.pos.x, p.pos.y, 0, p.pos.x, p.pos.y, glowR);
  pg.addColorStop(0, p.color);
  pg.addColorStop(0.3, hexToRgba(p.color, 0.4 * alpha));
  pg.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.fillStyle = pg;
  ctx.beginPath(); ctx.arc(p.pos.x, p.pos.y, glowR, 0, Math.PI * 2); ctx.fill();

  ctx.fillStyle = '#fff';
  ctx.beginPath(); ctx.arc(p.pos.x, p.pos.y, p.size * alpha * 0.4, 0, Math.PI * 2); ctx.fill();
  ctx.restore();
}

// --- POWER-UP (Very distinct from enemies — white bg circle + colored icon + label) ---
function drawPowerUp(ctx: CanvasRenderingContext2D, pu: PowerUp, time: number) {
  ctx.save();
  ctx.translate(pu.pos.x, pu.pos.y);

  const pulse = 1 + Math.sin(time * 3) * 0.06;
  const bob = Math.sin(time * 2.5) * 3;
  ctx.translate(0, bob);

  const colorMap: Record<string, string> = {
    speed: '#ffff00', 'triple-shot': '#ff44ff',
    shield: '#44ffff', heal: '#44ff44',
  };
  const color = colorMap[pu.type] || '#fff';
  const r = 10 * pulse;


  // Outer rotating dashed ring
  ctx.save();
  ctx.rotate(time * 1.5);
  ctx.setLineDash([4, 4]);
  ctx.strokeStyle = hexToRgba(color, 0.5);
  ctx.lineWidth = 1.5;
  ctx.beginPath(); ctx.arc(0, 0, r * 2.2, 0, Math.PI * 2); ctx.stroke();
  ctx.setLineDash([]);
  ctx.restore();

  // Large white filled circle background (key differentiator from enemies)
  ctx.shadowColor = color;
  ctx.shadowBlur = 25;
  ctx.fillStyle = 'rgba(255,255,255,0.92)';
  ctx.strokeStyle = color;
  ctx.lineWidth = 2.5;
  ctx.beginPath(); ctx.arc(0, 0, r, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
  ctx.shadowBlur = 0;

  // Draw icon inside the white circle
  if (pu.type === 'speed') {
    // Bold lightning bolt
    ctx.fillStyle = '#cc8800';
    ctx.strokeStyle = '#886600';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(-1, -r * 0.7);
    ctx.lineTo(4, -r * 0.1);
    ctx.lineTo(0, -r * 0.1);
    ctx.lineTo(1, r * 0.7);
    ctx.lineTo(-4, r * 0.1);
    ctx.lineTo(0, r * 0.1);
    ctx.closePath();
    ctx.fill(); ctx.stroke();
  } else if (pu.type === 'triple-shot') {
    // Three small circles in a fan (like projectiles)
    ctx.fillStyle = '#cc00cc';
    for (let i = -1; i <= 1; i++) {
      const angle = i * 0.4 - Math.PI / 2;
      const dx = Math.cos(angle) * r * 0.45;
      const dy = Math.sin(angle) * r * 0.45;
      ctx.beginPath(); ctx.arc(dx, dy, 3, 0, Math.PI * 2); ctx.fill();
    }
    // Arrow base
    ctx.strokeStyle = '#cc00cc';
    ctx.lineWidth = 1.5;
    ctx.beginPath(); ctx.moveTo(0, r * 0.3); ctx.lineTo(0, -r * 0.1); ctx.stroke();
  } else if (pu.type === 'shield') {
    // Shield icon (rounded chevron)
    ctx.fillStyle = '#0088aa';
    ctx.strokeStyle = '#005566';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(0, -r * 0.65);
    ctx.lineTo(r * 0.55, -r * 0.3);
    ctx.lineTo(r * 0.55, r * 0.15);
    ctx.quadraticCurveTo(0, r * 0.75, 0, r * 0.75);
    ctx.quadraticCurveTo(0, r * 0.75, -r * 0.55, r * 0.15);
    ctx.lineTo(-r * 0.55, -r * 0.3);
    ctx.closePath();
    ctx.fill(); ctx.stroke();
  } else if (pu.type === 'heal') {
    // Red/green cross
    ctx.fillStyle = '#cc2222';
    const cw = r * 0.3;
    const ch = r * 0.6;
    ctx.fillRect(-cw, -ch, cw * 2, ch * 2);
    ctx.fillRect(-ch, -cw, ch * 2, cw * 2);
  }

  // Colored label below (big and clear)
  ctx.fillStyle = color;
  ctx.font = 'bold 8px Orbitron, monospace';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'top';
  const labelMap: Record<string, string> = {
    speed: '⚡SPD', 'triple-shot': '▶▶▶', shield: '🛡SHD', heal: '♥HP',
  };
  ctx.fillText(labelMap[pu.type] || '', 0, r + 4);

  // Vertical beam of light above
  const beamAlpha = 0.15 + Math.sin(time * 4) * 0.08;
  const beam = ctx.createLinearGradient(0, -60, 0, -r);
  beam.addColorStop(0, 'rgba(255,255,255,0)');
  beam.addColorStop(1, hexToRgba(color, beamAlpha));
  ctx.fillStyle = beam;
  ctx.fillRect(-3, -60, 6, 60 - r);

  ctx.restore();
}

// ---- Utility ----

function getShipColor(cls: string): string {
  const map: Record<string, string> = {
    phantom: COLORS.phantom, interceptor: COLORS.interceptor, titan: COLORS.titan,
    spectre: COLORS.spectre, valkyrie: COLORS.valkyrie, juggernaut: COLORS.juggernaut,
  };
  return map[cls] || COLORS.phantom;
}

function getShipGlow(cls: string): string {
  const map: Record<string, string> = {
    phantom: COLORS.phantomGlow, interceptor: COLORS.interceptorGlow, titan: COLORS.titanGlow,
    spectre: COLORS.spectreGlow, valkyrie: COLORS.valkyrieGlow, juggernaut: COLORS.juggernautGlow,
  };
  return map[cls] || COLORS.phantomGlow;
}

function getEnemyColor(type: string): string {
  const map: Record<string, string> = {
    drone: COLORS.drone, splitter: COLORS.splitter, dasher: COLORS.dasher,
    tank: COLORS.tank, mothership: COLORS.mothership, vortex: COLORS.vortex, colossus: COLORS.colossus,
    fire_elemental: COLORS.fire_elemental, void_ghost: COLORS.void_ghost, crystal_golem: COLORS.crystal_golem,
    lava_dragon: COLORS.lava_dragon, void_lord: COLORS.void_lord, crystal_giant: COLORS.crystal_giant,
  };
  return map[type] || '#fff';
}

function hexToRgba(hex: string, alpha: number): string {
  if (!hex || hex[0] !== '#') return `rgba(255,255,255,${alpha})`;
  // Support 3-char hex (#fff) and 4-char (#ffff)
  let r: number, g: number, b: number;
  if (hex.length === 4) {
    r = parseInt(hex[1] + hex[1], 16);
    g = parseInt(hex[2] + hex[2], 16);
    b = parseInt(hex[3] + hex[3], 16);
  } else {
    r = parseInt(hex.slice(1, 3), 16);
    g = parseInt(hex.slice(3, 5), 16);
    b = parseInt(hex.slice(5, 7), 16);
  }
  if (isNaN(r)) r = 255;
  if (isNaN(g)) g = 255;
  if (isNaN(b)) b = 255;
  return `rgba(${r},${g},${b},${alpha})`;
}

function drawHazard(ctx: CanvasRenderingContext2D, h: ActiveHazard, time: number) {
  const alpha = Math.min(1, h.lifetime / 3);
  const pulse = 0.5 + Math.sin(time * 3) * 0.2;
  
  if (h.type === 'lava_pool') {
    const grad = ctx.createRadialGradient(h.pos.x, h.pos.y, 0, h.pos.x, h.pos.y, h.radius);
    grad.addColorStop(0, `rgba(255,80,0,${0.4 * alpha * pulse})`);
    grad.addColorStop(0.5, `rgba(255,30,0,${0.25 * alpha})`);
    grad.addColorStop(0.8, `rgba(200,0,0,${0.1 * alpha})`);
    grad.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = grad;
    ctx.beginPath(); ctx.arc(h.pos.x, h.pos.y, h.radius, 0, Math.PI * 2); ctx.fill();
    // Bubbles
    for (let i = 0; i < 3; i++) {
      const ba = time * 2 + i * 2;
      const bx = h.pos.x + Math.cos(ba) * h.radius * 0.5;
      const by = h.pos.y + Math.sin(ba) * h.radius * 0.5;
      ctx.fillStyle = `rgba(255,150,0,${0.4 * alpha * Math.abs(Math.sin(ba))})`;
      ctx.beginPath(); ctx.arc(bx, by, 2, 0, Math.PI * 2); ctx.fill();
    }
  } else if (h.type === 'black_hole') {
    // Spinning rings
    ctx.save(); ctx.translate(h.pos.x, h.pos.y);
    const grad = ctx.createRadialGradient(0, 0, 0, 0, 0, h.radius * 3);
    grad.addColorStop(0, `rgba(100,0,200,${0.5 * alpha})`);
    grad.addColorStop(0.3, `rgba(50,0,100,${0.2 * alpha})`);
    grad.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = grad;
    ctx.beginPath(); ctx.arc(0, 0, h.radius * 3, 0, Math.PI * 2); ctx.fill();
    // Accretion disk
    ctx.strokeStyle = `rgba(191,90,242,${0.5 * alpha * pulse})`;
    ctx.lineWidth = 1.5;
    ctx.beginPath(); ctx.arc(0, 0, h.radius + Math.sin(time * 4) * 5, 0, Math.PI * 2); ctx.stroke();
    ctx.strokeStyle = `rgba(150,0,255,${0.3 * alpha})`;
    ctx.beginPath(); ctx.arc(0, 0, h.radius * 0.5, time, time + Math.PI * 1.5); ctx.stroke();
    // Core
    ctx.fillStyle = `rgba(0,0,0,${0.8 * alpha})`;
    ctx.beginPath(); ctx.arc(0, 0, h.radius * 0.4, 0, Math.PI * 2); ctx.fill();
    ctx.restore();
  } else if (h.type === 'crystal_shard') {
    ctx.save(); ctx.translate(h.pos.x, h.pos.y); ctx.rotate(time * 0.5);
    ctx.strokeStyle = `rgba(0,229,255,${0.6 * alpha * pulse})`;
    ctx.lineWidth = 1.5;
    // Diamond shape
    ctx.beginPath();
    ctx.moveTo(0, -h.radius); ctx.lineTo(h.radius * 0.6, 0);
    ctx.lineTo(0, h.radius); ctx.lineTo(-h.radius * 0.6, 0); ctx.closePath();
    ctx.stroke();
    ctx.fillStyle = `rgba(0,229,255,${0.1 * alpha})`;
    ctx.fill();
    // Inner glow
    const cGrad = ctx.createRadialGradient(0, 0, 0, 0, 0, h.radius);
    cGrad.addColorStop(0, `rgba(0,229,255,${0.3 * alpha})`);
    cGrad.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = cGrad;
    ctx.beginPath(); ctx.arc(0, 0, h.radius, 0, Math.PI * 2); ctx.fill();
    ctx.restore();
  }
}

// Off-screen peer direction indicators
function drawOffScreenPeerIndicators(
  ctx: CanvasRenderingContext2D,
  peers: Array<{ pos: { x: number; y: number }; alive: boolean; dead?: boolean; playerLabel: string; shipClass: string }>,
  cX: number, cY: number, vW: number, vH: number,
  scale: number, canvasW: number, canvasH: number, time: number,
) {
  const margin = 40;
  const halfW = canvasW / 2;
  const halfH = canvasH / 2;
  const PEER_COLORS = ['#39ff14', '#ff1493', '#ffff00'];

  for (let i = 0; i < peers.length; i++) {
    const p = peers[i];
    // Show indicator even if dead (so you can find them to revive)
    // if (!p.alive && !p.dead) continue;

    // Convert peer world pos to screen pos
    const sx = halfW + (p.pos.x - cX) * scale;
    const sy = halfH + (p.pos.y - cY) * scale;

    // Check if off-screen
    if (sx >= margin && sx <= canvasW - margin && sy >= margin && sy <= canvasH - margin) continue;

    // Clamp to screen edges
    const angle = Math.atan2(sy - halfH, sx - halfW);
    const edgeX = Math.max(margin, Math.min(canvasW - margin, halfW + Math.cos(angle) * (halfW - margin)));
    const edgeY = Math.max(margin, Math.min(canvasH - margin, halfH + Math.sin(angle) * (halfH - margin)));

    const color = PEER_COLORS[i % PEER_COLORS.length];
    const pulse = 0.7 + Math.sin(time * 4 + i) * 0.3;

    ctx.save();
    ctx.translate(edgeX, edgeY);
    ctx.rotate(angle);

    // Arrow
    ctx.fillStyle = color;
    ctx.globalAlpha = pulse;
    ctx.beginPath();
    ctx.moveTo(14, 0);
    ctx.lineTo(-6, -8);
    ctx.lineTo(-3, 0);
    ctx.lineTo(-6, 8);
    ctx.closePath();
    ctx.fill();

    // Glow
    ctx.shadowColor = color;
    ctx.shadowBlur = 12;
    ctx.fill();
    ctx.shadowBlur = 0;

    // Label
    ctx.rotate(-angle);
    ctx.globalAlpha = 0.9;
    ctx.font = 'bold 10px Orbitron, monospace';
    ctx.fillStyle = color;
    ctx.textAlign = 'center';
    ctx.fillText(p.playerLabel || `P${i + 2}`, 0, -14);
    ctx.restore();
  }
}

export function getScale(canvasW: number, canvasH: number) {
  return Math.min(canvasW / CAMERA_VIEW_W, canvasH / CAMERA_VIEW_H);
}

export function getOffset(canvasW: number, canvasH: number) {
  const scale = getScale(canvasW, canvasH);
  const viewportW = canvasW / scale;
  const viewportH = canvasH / scale;
  return {
    x: (viewportW / 2 - camX) * scale,
    y: (viewportH / 2 - camY) * scale,
  };
}

export function getCameraPos() {
  return { x: camX, y: camY };
}

export function resetCamera() {
  camX = ARENA_W / 2;
  camY = ARENA_H / 2;
}
