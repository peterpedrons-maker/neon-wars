import { GameState, Player, Enemy, Projectile, Particle, PowerUp } from './types';
import { COLORS, ARENA_W, ARENA_H, WARRIOR_ATTACK_RANGE, CAMERA_VIEW_W, CAMERA_VIEW_H, CAMERA_LERP, WALL_LEFT, WALL_RIGHT, WALL_TOP, WALL_BOTTOM } from './constants';

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

  // Power-ups
  state.powerUps.forEach(pu => { if (pu.alive) drawPowerUp(ctx, pu, time); });

  // Projectiles
  state.projectiles.forEach(p => { if (p.alive) drawProjectile(ctx, p, time); });

  // Enemies
  state.enemies.forEach(e => { if (e.alive) drawEnemy(ctx, e, time); });

  // Player
  if (state.player.alive) drawPlayer(ctx, state.player, time);

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
}

function drawNeonGrid(ctx: CanvasRenderingContext2D, time: number) {
  const pulse = 0.04 + Math.sin(time * 0.5) * 0.015;
  
  ctx.strokeStyle = `rgba(0,255,255,${pulse})`;
  ctx.lineWidth = 0.5;

  for (let x = 0; x <= ARENA_W; x += GRID_SIZE) {
    ctx.beginPath();
    ctx.moveTo(x, 0);
    ctx.lineTo(x, ARENA_H);
    ctx.stroke();
  }
  for (let y = 0; y <= ARENA_H; y += GRID_SIZE) {
    ctx.beginPath();
    ctx.moveTo(0, y);
    ctx.lineTo(ARENA_W, y);
    ctx.stroke();
  }
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

// --- PLAYER (SHIP) ---
function drawPlayer(ctx: CanvasRenderingContext2D, p: Player, time: number) {
  ctx.save();
  ctx.translate(p.pos.x, p.pos.y);
  ctx.rotate(p.angle);

  const color = getShipColor(p.class);
  const glowColor = getShipGlow(p.class);

  // Shield effect
  if (p.shieldTimer > 0) {
    const sa = 0.3 + Math.sin(time * 5) * 0.15;
    ctx.beginPath();
    ctx.arc(0, 0, p.radius + 10, 0, Math.PI * 2);
    ctx.strokeStyle = `rgba(0,255,255,${sa})`;
    ctx.lineWidth = 2;
    ctx.setLineDash([4, 4]);
    ctx.lineDashOffset = time * 50;
    ctx.stroke();
    ctx.setLineDash([]);
  }

  if (p.invincibleTimer > 0 && Math.floor(Date.now() / 80) % 2 === 0) {
    ctx.globalAlpha = 0.4;
  }

  // Engine thrust glow
  const thrustPulse = 0.6 + Math.sin(time * 15) * 0.3;
  const speed = Math.hypot(p.vel.x || 0, p.vel.y || 0);
  const thrustLen = 8 + (speed / p.speed) * 12;
  ctx.fillStyle = hexToRgba(color, thrustPulse * 0.6);
  ctx.beginPath();
  ctx.moveTo(-p.radius * 0.5, -3);
  ctx.lineTo(-p.radius - thrustLen, 0);
  ctx.lineTo(-p.radius * 0.5, 3);
  ctx.closePath();
  ctx.fill();

  // Ship body - neon outlined triangle
  ctx.shadowColor = color;
  ctx.shadowBlur = 15 + Math.sin(time * 3) * 5;

  if (p.class === 'phantom') {
    // Sleek diamond shape
    ctx.beginPath();
    ctx.moveTo(p.radius * 1.5, 0);
    ctx.lineTo(0, -p.radius * 0.8);
    ctx.lineTo(-p.radius, -p.radius * 0.4);
    ctx.lineTo(-p.radius, p.radius * 0.4);
    ctx.lineTo(0, p.radius * 0.8);
    ctx.closePath();
  } else if (p.class === 'interceptor') {
    // Narrow arrow
    ctx.beginPath();
    ctx.moveTo(p.radius * 1.6, 0);
    ctx.lineTo(-p.radius * 0.5, -p.radius * 0.7);
    ctx.lineTo(-p.radius * 0.3, 0);
    ctx.lineTo(-p.radius * 0.5, p.radius * 0.7);
    ctx.closePath();
  } else {
    // Titan - heavy wedge
    ctx.beginPath();
    ctx.moveTo(p.radius * 1.3, 0);
    ctx.lineTo(-p.radius * 0.3, -p.radius);
    ctx.lineTo(-p.radius, -p.radius * 0.8);
    ctx.lineTo(-p.radius, p.radius * 0.8);
    ctx.lineTo(-p.radius * 0.3, p.radius);
    ctx.closePath();
  }

  // Fill with dark + stroke with neon
  ctx.fillStyle = hexToRgba(color, 0.15);
  ctx.fill();
  ctx.strokeStyle = color;
  ctx.lineWidth = 1.5;
  ctx.stroke();

  // Inner glow line
  ctx.strokeStyle = glowColor;
  ctx.lineWidth = 0.5;
  ctx.globalAlpha = Math.min(ctx.globalAlpha, 0.6);
  ctx.stroke();
  ctx.globalAlpha = 1;

  // Cockpit dot
  ctx.fillStyle = '#fff';
  ctx.beginPath();
  ctx.arc(p.radius * 0.3, 0, 2, 0, Math.PI * 2);
  ctx.fill();

  ctx.shadowBlur = 0;

  // Speed boost trail
  if (p.speedBoostTimer > 0) {
    ctx.strokeStyle = `rgba(0,229,255,${0.4 + Math.sin(time * 8) * 0.2})`;
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(-p.radius - thrustLen, 0);
    ctx.lineTo(-p.radius - thrustLen - 15, 0);
    ctx.stroke();
  }

  // Triple shot indicator
  if (p.tripleTimer > 0) {
    ctx.fillStyle = `rgba(255,20,147,${0.5 + Math.sin(time * 6) * 0.3})`;
    ctx.beginPath();
    ctx.arc(p.radius * 0.8, -3, 1.5, 0, Math.PI * 2);
    ctx.arc(p.radius * 0.8, 3, 1.5, 0, Math.PI * 2);
    ctx.fill();
  }

  // Titan melee arc
  if (p.class === 'titan' && p.attackTimer > p.attackCooldown * 0.4) {
    const slashProg = (p.attackTimer / p.attackCooldown - 0.4) / 0.6;
    ctx.beginPath();
    ctx.moveTo(0, 0);
    ctx.arc(0, 0, WARRIOR_ATTACK_RANGE, -0.8 + (1 - slashProg) * 1.2, -0.8 + (1 - slashProg) * 1.2 + 1.0);
    ctx.closePath();
    const sg = ctx.createRadialGradient(0, 0, p.radius, 0, 0, WARRIOR_ATTACK_RANGE);
    sg.addColorStop(0, `rgba(255,107,0,${0.5 * slashProg})`);
    sg.addColorStop(1, 'rgba(255,107,0,0)');
    ctx.fillStyle = sg;
    ctx.fill();
  }

  ctx.globalAlpha = 1;
  ctx.restore();
}

// --- ENEMIES (GEOMETRIC SHAPES) ---
function drawEnemy(ctx: CanvasRenderingContext2D, e: Enemy, time: number) {
  ctx.save();
  ctx.translate(e.pos.x, e.pos.y);

  if (e.flashTimer > 0) {
    ctx.globalAlpha = 0.5 + Math.sin(Date.now() * 0.05) * 0.5;
  }

  const color = getEnemyColor(e.type);

  // Boss aura
  if (e.isBoss) {
    const auraR = e.radius + 25 + Math.sin(time * 3) * 8;
    const aGrad = ctx.createRadialGradient(0, 0, e.radius, 0, 0, auraR);
    aGrad.addColorStop(0, hexToRgba(color, 0.3));
    aGrad.addColorStop(0.5, hexToRgba(color, 0.08));
    aGrad.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = aGrad;
    ctx.beginPath(); ctx.arc(0, 0, auraR, 0, Math.PI * 2); ctx.fill();
    
    // Orbiting particles
    for (let i = 0; i < 8; i++) {
      const a = time * 0.8 + (i / 8) * Math.PI * 2;
      ctx.beginPath();
      ctx.arc(Math.cos(a) * (e.radius + 15), Math.sin(a) * (e.radius + 15), 2, 0, Math.PI * 2);
      ctx.fillStyle = hexToRgba(color, 0.4 + Math.sin(time * 2 + i) * 0.2);
      ctx.fill();
    }
  }

  ctx.shadowColor = color;
  ctx.shadowBlur = 12;

  const rot = time * 2;

  if (e.type === 'drone') {
    // Square - rotates
    ctx.save(); ctx.rotate(rot);
    drawNeonShape(ctx, 4, e.radius, color);
    ctx.restore();
  } else if (e.type === 'splitter') {
    // Circle that splits
    ctx.beginPath();
    ctx.arc(0, 0, e.radius, 0, Math.PI * 2);
    ctx.fillStyle = hexToRgba(color, 0.15);
    ctx.fill();
    ctx.strokeStyle = color;
    ctx.lineWidth = 1.5;
    ctx.stroke();
    // Inner circle
    ctx.beginPath();
    ctx.arc(0, 0, e.radius * 0.5, 0, Math.PI * 2);
    ctx.strokeStyle = hexToRgba(color, 0.5);
    ctx.lineWidth = 1;
    ctx.stroke();
  } else if (e.type === 'dasher') {
    // Triangle - fast
    ctx.save(); ctx.rotate(rot * 2);
    drawNeonShape(ctx, 3, e.radius, color);
    ctx.restore();
  } else if (e.type === 'tank') {
    // Hexagon - heavy
    ctx.save(); ctx.rotate(rot * 0.5);
    drawNeonShape(ctx, 6, e.radius, color);
    ctx.restore();
    // Inner hexagon
    ctx.save(); ctx.rotate(-rot * 0.3);
    drawNeonShape(ctx, 6, e.radius * 0.5, color, 0.4);
    ctx.restore();
  } else if (e.type === 'mothership') {
    // Large pentagon with inner detail
    ctx.save(); ctx.rotate(rot * 0.3);
    drawNeonShape(ctx, 5, e.radius, color);
    ctx.restore();
    ctx.save(); ctx.rotate(-rot * 0.5);
    drawNeonShape(ctx, 5, e.radius * 0.6, color, 0.4);
    ctx.restore();
    // Core glow
    const cg = ctx.createRadialGradient(0, 0, 2, 0, 0, e.radius * 0.3);
    cg.addColorStop(0, hexToRgba(color, 0.6));
    cg.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = cg;
    ctx.beginPath(); ctx.arc(0, 0, e.radius * 0.3, 0, Math.PI * 2); ctx.fill();
  } else if (e.type === 'vortex') {
    // Spiral / octagon
    ctx.save(); ctx.rotate(rot);
    drawNeonShape(ctx, 8, e.radius, color);
    ctx.restore();
    ctx.save(); ctx.rotate(-rot * 1.5);
    drawNeonShape(ctx, 8, e.radius * 0.55, color, 0.5);
    ctx.restore();
    // Spiral lines
    for (let i = 0; i < 4; i++) {
      const a = rot * 2 + (i / 4) * Math.PI * 2;
      ctx.strokeStyle = hexToRgba(color, 0.3);
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(Math.cos(a) * e.radius * 0.3, Math.sin(a) * e.radius * 0.3);
      ctx.lineTo(Math.cos(a + 0.5) * e.radius * 0.8, Math.sin(a + 0.5) * e.radius * 0.8);
      ctx.stroke();
    }
  } else if (e.type === 'colossus') {
    // Large diamond with pulsing
    const pulse = 1 + Math.sin(time * 2) * 0.05;
    ctx.save(); ctx.rotate(rot * 0.2); ctx.scale(pulse, pulse);
    drawNeonShape(ctx, 4, e.radius, color);
    ctx.restore();
    ctx.save(); ctx.rotate(-rot * 0.4);
    drawNeonShape(ctx, 4, e.radius * 0.5, color, 0.5);
    ctx.restore();
    // Pulsing core
    const cg2 = ctx.createRadialGradient(0, 0, 2, 0, 0, e.radius * 0.4);
    cg2.addColorStop(0, `rgba(0,191,255,${0.5 + Math.sin(time * 3) * 0.2})`);
    cg2.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = cg2;
    ctx.beginPath(); ctx.arc(0, 0, e.radius * 0.4, 0, Math.PI * 2); ctx.fill();
  } else {
    // Fallback circle
    ctx.beginPath(); ctx.arc(0, 0, e.radius, 0, Math.PI * 2);
    ctx.strokeStyle = color; ctx.lineWidth = 1.5; ctx.stroke();
  }

  ctx.shadowBlur = 0;

  // HP bar for damaged enemies
  if (e.hp < e.maxHp && (e.isBoss || e.maxHp > 20)) {
    const barW = e.radius * 2.4;
    const barH = e.isBoss ? 5 : 3;
    const barY = -e.radius - 10;
    ctx.fillStyle = 'rgba(0,0,0,0.6)';
    ctx.fillRect(-barW / 2 - 1, barY - 1, barW + 2, barH + 2);
    const hpPct = e.hp / e.maxHp;
    ctx.fillStyle = color;
    ctx.fillRect(-barW / 2, barY, barW * hpPct, barH);
  }

  ctx.restore();
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

// --- POWER-UP ---
function drawPowerUp(ctx: CanvasRenderingContext2D, pu: PowerUp, time: number) {
  ctx.save();
  ctx.translate(pu.pos.x, pu.pos.y);

  const pulse = 1 + Math.sin(time * 4) * 0.15;
  const bob = Math.sin(time * 3) * 3;
  ctx.translate(0, bob);

  const colorMap: Record<string, string> = {
    speed: COLORS.speedPU, 'triple-shot': COLORS.triplePU,
    shield: COLORS.shieldPU, heal: COLORS.healPU,
  };
  const color = colorMap[pu.type] || '#fff';

  // Outer glow
  const og = ctx.createRadialGradient(0, 0, pu.radius * 0.3, 0, 0, pu.radius * 2.5);
  og.addColorStop(0, hexToRgba(color, 0.3));
  og.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.fillStyle = og;
  ctx.beginPath(); ctx.arc(0, 0, pu.radius * 2.5, 0, Math.PI * 2); ctx.fill();

  // Rotating ring
  ctx.save(); ctx.rotate(time * 3);
  for (let i = 0; i < 6; i++) {
    const a = (i / 6) * Math.PI * 2;
    ctx.fillStyle = hexToRgba(color, 0.4 + Math.sin(time * 5 + i) * 0.2);
    ctx.beginPath();
    ctx.arc(Math.cos(a) * pu.radius * 1.3 * pulse, Math.sin(a) * pu.radius * 1.3 * pulse, 1.5, 0, Math.PI * 2);
    ctx.fill();
  }
  ctx.restore();

  // Core orb
  ctx.shadowColor = color;
  ctx.shadowBlur = 15;
  ctx.beginPath();
  ctx.arc(0, 0, pu.radius * pulse, 0, Math.PI * 2);
  ctx.fillStyle = hexToRgba(color, 0.3);
  ctx.fill();
  ctx.strokeStyle = color;
  ctx.lineWidth = 1.5;
  ctx.stroke();
  ctx.shadowBlur = 0;

  // Icon
  const iconMap: Record<string, string> = {
    speed: '⚡', 'triple-shot': '◆', shield: '◯', heal: '+',
  };
  ctx.fillStyle = '#fff';
  ctx.font = `${10 * pulse}px monospace`;
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText(iconMap[pu.type] || '?', 0, 0);

  ctx.restore();
}

// ---- Utility ----

function getShipColor(cls: string): string {
  if (cls === 'phantom') return COLORS.phantom;
  if (cls === 'interceptor') return COLORS.interceptor;
  return COLORS.titan;
}

function getShipGlow(cls: string): string {
  if (cls === 'phantom') return COLORS.phantomGlow;
  if (cls === 'interceptor') return COLORS.interceptorGlow;
  return COLORS.titanGlow;
}

function getEnemyColor(type: string): string {
  const map: Record<string, string> = {
    drone: COLORS.drone, splitter: COLORS.splitter, dasher: COLORS.dasher,
    tank: COLORS.tank, mothership: COLORS.mothership, vortex: COLORS.vortex, colossus: COLORS.colossus,
  };
  return map[type] || '#fff';
}

function hexToRgba(hex: string, alpha: number): string {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return `rgba(${r},${g},${b},${alpha})`;
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
