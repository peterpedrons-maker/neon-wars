import { GameState, Player, Enemy, Projectile, Particle, PowerUp } from './types';
import { COLORS, ARENA_W, ARENA_H, WARRIOR_ATTACK_RANGE, CAMERA_VIEW_W, CAMERA_VIEW_H, CAMERA_LERP } from './constants';

// Camera state
let camX = ARENA_W / 2;
let camY = ARENA_H / 2;

// Cached textures
let floorPattern: CanvasPattern | null = null;
let floorPatternCanvas: HTMLCanvasElement | null = null;

function createFloorPattern(ctx: CanvasRenderingContext2D): CanvasPattern | null {
  if (floorPattern && floorPatternCanvas) return floorPattern;
  const tile = document.createElement('canvas');
  tile.width = 64;
  tile.height = 64;
  const tc = tile.getContext('2d')!;

  // Rich stone tile
  const bg = tc.createLinearGradient(0, 0, 64, 64);
  bg.addColorStop(0, '#252040');
  bg.addColorStop(0.5, '#1e1a2e');
  bg.addColorStop(1, '#1a1528');
  tc.fillStyle = bg;
  tc.fillRect(0, 0, 64, 64);

  // Subtle noise
  for (let i = 0; i < 60; i++) {
    const x = Math.random() * 64;
    const y = Math.random() * 64;
    const s = Math.random() * 2.5 + 0.5;
    const bright = Math.random() > 0.5;
    tc.fillStyle = bright ? `rgba(180,160,255,${Math.random() * 0.06})` : `rgba(0,0,0,${Math.random() * 0.1})`;
    tc.fillRect(x, y, s, s);
  }

  // Tile grooves
  tc.strokeStyle = 'rgba(0,0,0,0.35)';
  tc.lineWidth = 2;
  tc.strokeRect(1, 1, 62, 62);
  tc.strokeStyle = 'rgba(150,130,200,0.06)';
  tc.lineWidth = 1;
  tc.strokeRect(3, 3, 58, 58);

  // Random cracks
  if (Math.random() > 0.5) {
    tc.strokeStyle = 'rgba(0,0,0,0.2)';
    tc.lineWidth = 0.7;
    tc.beginPath();
    tc.moveTo(10 + Math.random() * 20, 10 + Math.random() * 10);
    tc.lineTo(30 + Math.random() * 10, 30 + Math.random() * 10);
    tc.stroke();
  }

  // Random moss
  if (Math.random() > 0.7) {
    tc.fillStyle = 'rgba(74,222,128,0.04)';
    tc.beginPath();
    tc.arc(20 + Math.random() * 24, 40 + Math.random() * 20, 5 + Math.random() * 5, 0, Math.PI * 2);
    tc.fill();
  }

  floorPatternCanvas = tile;
  floorPattern = ctx.createPattern(tile, 'repeat');
  return floorPattern;
}

export function renderGame(ctx: CanvasRenderingContext2D, state: GameState, canvasW: number, canvasH: number) {
  const time = Date.now() * 0.001;

  // Smooth camera follow player
  if (state.player.alive) {
    camX += (state.player.pos.x - camX) * CAMERA_LERP;
    camY += (state.player.pos.y - camY) * CAMERA_LERP;
  }

  // Clamp camera to arena bounds
  const halfViewW = CAMERA_VIEW_W / 2;
  const halfViewH = CAMERA_VIEW_H / 2;
  camX = Math.max(halfViewW, Math.min(ARENA_W - halfViewW, camX));
  camY = Math.max(halfViewH, Math.min(ARENA_H - halfViewH, camY));

  // Scale: fit the camera view into the canvas
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

  // Clear
  ctx.fillStyle = '#08061a';
  ctx.fillRect(0, 0, canvasW, canvasH);

  // Transform: scale + translate so camera center is at canvas center
  ctx.scale(scale, scale);
  ctx.translate(viewportW / 2 - camX, viewportH / 2 - camY);

  // Arena floor
  const pattern = createFloorPattern(ctx);
  if (pattern) {
    ctx.fillStyle = pattern;
  } else {
    ctx.fillStyle = COLORS.arena;
  }
  ctx.fillRect(0, 0, ARENA_W, ARENA_H);

  // Grid overlay
  ctx.strokeStyle = COLORS.grid;
  ctx.lineWidth = 0.5;
  for (let x = 0; x <= ARENA_W; x += 64) {
    ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, ARENA_H); ctx.stroke();
  }
  for (let y = 0; y <= ARENA_H; y += 64) {
    ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(ARENA_W, y); ctx.stroke();
  }

  // Ambient glow around player
  if (state.player.alive) {
    const p = state.player;
    const gc = p.class === 'mage' ? '168,85,247' : p.class === 'archer' ? '34,211,238' : '249,115,22';
    const grad = ctx.createRadialGradient(p.pos.x, p.pos.y, 10, p.pos.x, p.pos.y, 180);
    grad.addColorStop(0, `rgba(${gc},0.15)`);
    grad.addColorStop(0.5, `rgba(${gc},0.04)`);
    grad.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = grad;
    ctx.fillRect(p.pos.x - 200, p.pos.y - 200, 400, 400);
  }

  // Torches along walls
  const torchPositions = [
    [30, 30], [ARENA_W / 3, 20], [ARENA_W * 2 / 3, 20], [ARENA_W - 30, 30],
    [30, ARENA_H - 30], [ARENA_W / 3, ARENA_H - 20], [ARENA_W * 2 / 3, ARENA_H - 20], [ARENA_W - 30, ARENA_H - 30],
    [20, ARENA_H / 3], [20, ARENA_H * 2 / 3], [ARENA_W - 20, ARENA_H / 3], [ARENA_W - 20, ARENA_H * 2 / 3],
  ];
  torchPositions.forEach(([tx, ty], i) => drawTorchLight(ctx, tx, ty, time + i * 0.7));

  // Stone wall
  drawStoneWall(ctx, time);

  // Power-ups
  state.powerUps.forEach(pu => { if (pu.alive) drawPowerUp(ctx, pu, time); });

  // Projectiles
  state.projectiles.forEach(p => { if (p.alive) drawProjectile(ctx, p, time); });

  // Shadows
  state.enemies.forEach(e => { if (e.alive) drawShadow(ctx, e.pos.x, e.pos.y, e.radius); });
  if (state.player.alive) drawShadow(ctx, state.player.pos.x, state.player.pos.y, state.player.radius);

  // Enemies
  state.enemies.forEach(e => { if (e.alive) drawEnemy(ctx, e, time); });

  // Player
  if (state.player.alive) drawPlayer(ctx, state.player, time);

  // Particles
  state.particles.forEach(p => drawParticle(ctx, p));

  // Vignette inside arena
  drawVignette(ctx);

  // Darkness outside arena
  drawOutsideArena(ctx, camX, camY, viewportW, viewportH);

  ctx.restore();
}

function drawOutsideArena(ctx: CanvasRenderingContext2D, cx: number, cy: number, vw: number, vh: number) {
  ctx.fillStyle = '#08061a';
  const left = cx - vw / 2;
  const top = cy - vh / 2;
  // Top
  if (top < 0) ctx.fillRect(left, top, vw, -top);
  // Bottom
  const bottom = cy + vh / 2;
  if (bottom > ARENA_H) ctx.fillRect(left, ARENA_H, vw, bottom - ARENA_H);
  // Left
  if (left < 0) ctx.fillRect(left, 0, -left, ARENA_H);
  // Right
  const right = cx + vw / 2;
  if (right > ARENA_W) ctx.fillRect(ARENA_W, 0, right - ARENA_W, ARENA_H);
}

function drawShadow(ctx: CanvasRenderingContext2D, x: number, y: number, radius: number) {
  ctx.save();
  ctx.beginPath();
  ctx.ellipse(x, y + radius * 0.7, radius * 1.0, radius * 0.35, 0, 0, Math.PI * 2);
  ctx.fillStyle = 'rgba(0,0,0,0.4)';
  ctx.fill();
  ctx.restore();
}

function drawTorchLight(ctx: CanvasRenderingContext2D, x: number, y: number, time: number) {
  const flicker = 0.85 + Math.sin(time * 6) * 0.08 + Math.sin(time * 9.7) * 0.05 + Math.sin(time * 15) * 0.02;
  const r = 140 * flicker;
  const grad = ctx.createRadialGradient(x, y, 3, x, y, r);
  grad.addColorStop(0, `rgba(255,180,60,${0.2 * flicker})`);
  grad.addColorStop(0.3, `rgba(255,120,30,${0.08 * flicker})`);
  grad.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.fillStyle = grad;
  ctx.fillRect(x - r, y - r, r * 2, r * 2);

  // Flame
  ctx.save();
  ctx.translate(x, y);
  const fSize = 5 + Math.sin(time * 10) * 2;
  const grad2 = ctx.createRadialGradient(0, -3, 1, 0, -3, fSize);
  grad2.addColorStop(0, 'rgba(255,240,120,0.95)');
  grad2.addColorStop(0.4, 'rgba(255,140,30,0.7)');
  grad2.addColorStop(1, 'rgba(255,60,0,0)');
  ctx.fillStyle = grad2;
  ctx.beginPath();
  ctx.arc(0, -3, fSize, 0, Math.PI * 2);
  ctx.fill();

  // Torch base
  ctx.fillStyle = '#5a3a20';
  ctx.fillRect(-2, 0, 4, 8);
  ctx.restore();
}

function drawStoneWall(ctx: CanvasRenderingContext2D, time: number) {
  const wallW = 12;

  // Outer dark
  ctx.strokeStyle = '#0d0820';
  ctx.lineWidth = wallW + 6;
  ctx.strokeRect(-3, -3, ARENA_W + 6, ARENA_H + 6);

  // Main wall with gradient
  const wallGrad = ctx.createLinearGradient(0, 0, ARENA_W, ARENA_H);
  wallGrad.addColorStop(0, '#5a4a80');
  wallGrad.addColorStop(0.3, '#4a3a6e');
  wallGrad.addColorStop(0.7, '#3a2a5e');
  wallGrad.addColorStop(1, '#5a4a80');
  ctx.strokeStyle = wallGrad;
  ctx.lineWidth = wallW;
  ctx.strokeRect(wallW / 2, wallW / 2, ARENA_W - wallW, ARENA_H - wallW);

  // Inner highlight
  ctx.strokeStyle = 'rgba(180,160,255,0.15)';
  ctx.lineWidth = 1;
  ctx.strokeRect(wallW + 1, wallW + 1, ARENA_W - wallW * 2 - 2, ARENA_H - wallW * 2 - 2);

  // Stone block marks
  ctx.strokeStyle = 'rgba(0,0,0,0.35)';
  ctx.lineWidth = 1;
  for (let x = 0; x < ARENA_W; x += 48) {
    ctx.beginPath();
    ctx.moveTo(x, 0); ctx.lineTo(x, wallW);
    ctx.moveTo(x, ARENA_H - wallW); ctx.lineTo(x, ARENA_H);
    ctx.stroke();
  }
  for (let y = 0; y < ARENA_H; y += 48) {
    ctx.beginPath();
    ctx.moveTo(0, y); ctx.lineTo(wallW, y);
    ctx.moveTo(ARENA_W - wallW, y); ctx.lineTo(ARENA_W, y);
    ctx.stroke();
  }

  // Decorative runes on wall
  ctx.fillStyle = 'rgba(168,85,247,0.08)';
  ctx.font = '10px serif';
  ctx.textAlign = 'center';
  const runes = ['⚔', '☆', '◆', '✦', '⬥'];
  for (let i = 0; i < 16; i++) {
    const rx = 50 + (i * 100) % ARENA_W;
    const ry = i < 8 ? 5 : ARENA_H - 5;
    ctx.fillText(runes[i % runes.length], rx, ry + 4);
  }
}

function drawVignette(ctx: CanvasRenderingContext2D) {
  const grad = ctx.createRadialGradient(ARENA_W / 2, ARENA_H / 2, ARENA_W * 0.2, ARENA_W / 2, ARENA_H / 2, ARENA_W * 0.65);
  grad.addColorStop(0, 'rgba(0,0,0,0)');
  grad.addColorStop(1, 'rgba(0,0,0,0.35)');
  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, ARENA_W, ARENA_H);
}

function drawPlayer(ctx: CanvasRenderingContext2D, p: Player, time: number) {
  ctx.save();
  ctx.translate(p.pos.x, p.pos.y);

  const glowColor = p.class === 'mage' ? COLORS.mageGlow : p.class === 'archer' ? COLORS.archerGlow : COLORS.warriorGlow;
  const baseColor = p.class === 'mage' ? COLORS.mage : p.class === 'archer' ? COLORS.archer : COLORS.warrior;
  const glowRGB = p.class === 'mage' ? '168,85,247' : p.class === 'archer' ? '34,211,238' : '249,115,22';

  // Shield effect
  if (p.shieldTimer > 0) {
    const shieldAlpha = 0.35 + Math.sin(time * 4) * 0.15;
    ctx.beginPath();
    ctx.arc(0, 0, p.radius + 12, 0, Math.PI * 2);
    const shGrad = ctx.createRadialGradient(0, 0, p.radius, 0, 0, p.radius + 12);
    shGrad.addColorStop(0, `rgba(56,189,248,${shieldAlpha})`);
    shGrad.addColorStop(1, 'rgba(56,189,248,0)');
    ctx.fillStyle = shGrad;
    ctx.fill();
    ctx.beginPath();
    ctx.arc(0, 0, p.radius + 11, 0, Math.PI * 2);
    ctx.strokeStyle = `rgba(125,211,252,${0.5 + Math.sin(time * 6) * 0.2})`;
    ctx.lineWidth = 2;
    ctx.setLineDash([5, 5]);
    ctx.lineDashOffset = time * 40;
    ctx.stroke();
    ctx.setLineDash([]);
  }

  // Invincibility flash
  if (p.invincibleTimer > 0 && Math.floor(Date.now() / 80) % 2 === 0) {
    ctx.globalAlpha = 0.5;
  }

  // Outer glow ring
  ctx.shadowColor = glowColor;
  ctx.shadowBlur = 25 + Math.sin(time * 3) * 8;

  // Body
  const bodyGrad = ctx.createRadialGradient(-4, -4, 2, 0, 0, p.radius);
  bodyGrad.addColorStop(0, lightenColor(baseColor, 60));
  bodyGrad.addColorStop(0.5, baseColor);
  bodyGrad.addColorStop(1, darkenColor(baseColor, 40));
  ctx.beginPath();
  ctx.arc(0, 0, p.radius, 0, Math.PI * 2);
  ctx.fillStyle = bodyGrad;
  ctx.fill();

  // Bright inner ring
  ctx.beginPath();
  ctx.arc(0, 0, p.radius * 0.65, 0, Math.PI * 2);
  ctx.strokeStyle = `rgba(255,255,255,0.2)`;
  ctx.lineWidth = 1.5;
  ctx.stroke();

  // Class-specific decoration on body
  if (p.class === 'mage') {
    // Arcane runes orbiting
    for (let i = 0; i < 3; i++) {
      const a = time * 1.5 + (i / 3) * Math.PI * 2;
      const ox = Math.cos(a) * (p.radius + 5);
      const oy = Math.sin(a) * (p.radius + 5);
      ctx.beginPath();
      ctx.arc(ox, oy, 2, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(216,180,254,${0.5 + Math.sin(time * 3 + i) * 0.3})`;
      ctx.fill();
    }
  } else if (p.class === 'archer') {
    // Speed lines when moving
    if (Math.abs(p.vel?.x || 0) > 0 || Math.abs(p.vel?.y || 0) > 0) {
      for (let i = 0; i < 2; i++) {
        const a = p.angle + Math.PI + (i - 0.5) * 0.4;
        ctx.beginPath();
        ctx.moveTo(Math.cos(a) * p.radius, Math.sin(a) * p.radius);
        ctx.lineTo(Math.cos(a) * (p.radius + 8 + Math.random() * 5), Math.sin(a) * (p.radius + 8));
        ctx.strokeStyle = `rgba(103,232,249,0.3)`;
        ctx.lineWidth = 1;
        ctx.stroke();
      }
    }
  }

  // Weapon
  ctx.save();
  ctx.rotate(p.angle);
  ctx.shadowBlur = 0;
  if (p.class === 'warrior') {
    // Big sword
    ctx.beginPath();
    ctx.moveTo(p.radius + 20, 0);
    ctx.lineTo(p.radius + 5, -4);
    ctx.lineTo(p.radius - 2, -6);
    ctx.lineTo(p.radius - 2, 6);
    ctx.lineTo(p.radius + 5, 4);
    ctx.closePath();
    const swordGrad = ctx.createLinearGradient(p.radius - 2, 0, p.radius + 20, 0);
    swordGrad.addColorStop(0, '#aaa');
    swordGrad.addColorStop(0.5, '#e0e0e0');
    swordGrad.addColorStop(1, '#ccc');
    ctx.fillStyle = swordGrad;
    ctx.fill();
    ctx.strokeStyle = 'rgba(255,255,255,0.3)';
    ctx.lineWidth = 0.5;
    ctx.stroke();
    // Guard
    ctx.fillStyle = '#a0522d';
    ctx.fillRect(p.radius - 4, -8, 5, 16);
    // Gem on guard
    ctx.beginPath();
    ctx.arc(p.radius - 1.5, 0, 2.5, 0, Math.PI * 2);
    ctx.fillStyle = '#ef4444';
    ctx.fill();
  } else if (p.class === 'archer') {
    // Arrow
    ctx.beginPath();
    ctx.moveTo(p.radius + 22, 0);
    ctx.lineTo(p.radius + 16, -2.5);
    ctx.lineTo(p.radius + 4, 0);
    ctx.lineTo(p.radius + 16, 2.5);
    ctx.closePath();
    ctx.fillStyle = '#92400e';
    ctx.fill();
    // Arrow shaft
    ctx.beginPath();
    ctx.moveTo(p.radius + 4, 0);
    ctx.lineTo(p.radius - 8, 0);
    ctx.strokeStyle = '#78350f';
    ctx.lineWidth = 1.5;
    ctx.stroke();
    // Bow
    ctx.beginPath();
    ctx.arc(0, 0, p.radius + 4, -0.7, 0.7);
    ctx.strokeStyle = '#92400e';
    ctx.lineWidth = 2.5;
    ctx.stroke();
    // Bowstring
    ctx.beginPath();
    ctx.moveTo(Math.cos(-0.7) * (p.radius + 4), Math.sin(-0.7) * (p.radius + 4));
    ctx.lineTo(p.radius - 6, 0);
    ctx.lineTo(Math.cos(0.7) * (p.radius + 4), Math.sin(0.7) * (p.radius + 4));
    ctx.strokeStyle = 'rgba(200,200,200,0.6)';
    ctx.lineWidth = 0.8;
    ctx.stroke();
  } else {
    // Staff
    ctx.beginPath();
    ctx.moveTo(p.radius + 8, 0);
    ctx.lineTo(p.radius - 12, 0);
    ctx.strokeStyle = '#78350f';
    ctx.lineWidth = 3;
    ctx.stroke();
    // Orb at tip
    const orbGrad = ctx.createRadialGradient(p.radius + 10, 0, 1, p.radius + 10, 0, 6);
    orbGrad.addColorStop(0, '#fff');
    orbGrad.addColorStop(0.3, COLORS.mageGlow);
    orbGrad.addColorStop(1, COLORS.mage);
    ctx.beginPath();
    ctx.arc(p.radius + 10, 0, 6, 0, Math.PI * 2);
    ctx.fillStyle = orbGrad;
    ctx.fill();
    // Orb sparkle
    ctx.beginPath();
    ctx.arc(p.radius + 8, -2, 1.5, 0, Math.PI * 2);
    ctx.fillStyle = 'rgba(255,255,255,0.8)';
    ctx.fill();
  }
  ctx.restore();

  // Warrior melee arc
  if (p.class === 'warrior' && p.attackTimer > p.attackCooldown * 0.5) {
    ctx.beginPath();
    ctx.moveTo(0, 0);
    ctx.arc(0, 0, WARRIOR_ATTACK_RANGE, p.angle - 0.8, p.angle + 0.8);
    ctx.closePath();
    const slashGrad = ctx.createRadialGradient(0, 0, p.radius, 0, 0, WARRIOR_ATTACK_RANGE);
    slashGrad.addColorStop(0, 'rgba(249,115,22,0.5)');
    slashGrad.addColorStop(1, 'rgba(249,115,22,0)');
    ctx.fillStyle = slashGrad;
    ctx.fill();
    // Bright arc edge
    ctx.beginPath();
    ctx.arc(0, 0, WARRIOR_ATTACK_RANGE, p.angle - 0.8, p.angle + 0.8);
    ctx.strokeStyle = 'rgba(253,186,116,0.6)';
    ctx.lineWidth = 3;
    ctx.stroke();
  }

  ctx.shadowBlur = 0;
  ctx.globalAlpha = 1;
  ctx.restore();
}

function drawEnemy(ctx: CanvasRenderingContext2D, e: Enemy, time: number) {
  ctx.save();
  ctx.translate(e.pos.x, e.pos.y);

  if (e.flashTimer > 0) {
    ctx.globalAlpha = 0.6 + Math.sin(Date.now() * 0.05) * 0.4;
  }

  const colorMap: Record<string, string> = {
    skeleton: COLORS.skeleton,
    slime: COLORS.slime,
    bat: COLORS.bat,
    'dark-knight': COLORS.darkKnight,
    dragon: COLORS.dragon,
    lich: COLORS.lich,
    golem: COLORS.golem,
  };
  const color = colorMap[e.type] || '#fff';

  // Boss aura
  if (e.isBoss) {
    const auraR = e.radius + 20 + Math.sin(time * 3) * 8;
    const aGrad = ctx.createRadialGradient(0, 0, e.radius, 0, 0, auraR);
    aGrad.addColorStop(0, hexToRgba(color, 0.35));
    aGrad.addColorStop(0.5, hexToRgba(color, 0.1));
    aGrad.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = aGrad;
    ctx.beginPath();
    ctx.arc(0, 0, auraR, 0, Math.PI * 2);
    ctx.fill();

    // Rotating runes
    ctx.save();
    ctx.rotate(time * 0.6);
    for (let i = 0; i < 8; i++) {
      const a = (i / 8) * Math.PI * 2;
      const rx = Math.cos(a) * (e.radius + 12);
      const ry = Math.sin(a) * (e.radius + 12);
      ctx.beginPath();
      ctx.arc(rx, ry, 2.5, 0, Math.PI * 2);
      ctx.fillStyle = hexToRgba(color, 0.3 + Math.sin(time * 2 + i) * 0.15);
      ctx.fill();
    }
    ctx.restore();
  }

  // Enemy body
  ctx.beginPath();
  if (e.type === 'slime') {
    const wobble = Math.sin(time * 4) * 3;
    ctx.ellipse(0, 2 + wobble * 0.3, e.radius + wobble * 0.6, e.radius * 0.75 - wobble * 0.3, 0, 0, Math.PI * 2);
    const slimeGrad = ctx.createRadialGradient(-4, -3, 2, 0, 0, e.radius);
    slimeGrad.addColorStop(0, lightenColor(color, 60));
    slimeGrad.addColorStop(0.4, color);
    slimeGrad.addColorStop(1, darkenColor(color, 40));
    ctx.fillStyle = slimeGrad;
    ctx.fill();
    // Big shine
    ctx.beginPath();
    ctx.ellipse(-e.radius * 0.3, -e.radius * 0.2, e.radius * 0.3, e.radius * 0.18, -0.3, 0, Math.PI * 2);
    ctx.fillStyle = 'rgba(255,255,255,0.4)';
    ctx.fill();
    // Eyes
    ctx.fillStyle = '#000';
    ctx.beginPath();
    ctx.arc(-4, 0, 2.5, 0, Math.PI * 2);
    ctx.arc(4, 0, 2.5, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = '#fff';
    ctx.beginPath();
    ctx.arc(-3.5, -0.5, 1, 0, Math.PI * 2);
    ctx.arc(4.5, -0.5, 1, 0, Math.PI * 2);
    ctx.fill();
  } else if (e.type === 'bat') {
    const wingFlap = Math.sin(time * 14) * 0.5;
    // Wings
    ctx.save();
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.moveTo(0, 0);
    ctx.quadraticCurveTo(-e.radius * 1.5, -e.radius * (1.2 + wingFlap), -e.radius * 2, e.radius * 0.3);
    ctx.quadraticCurveTo(-e.radius, e.radius * 0.4, 0, 0);
    ctx.fill();
    ctx.beginPath();
    ctx.moveTo(0, 0);
    ctx.quadraticCurveTo(e.radius * 1.5, -e.radius * (1.2 + wingFlap), e.radius * 2, e.radius * 0.3);
    ctx.quadraticCurveTo(e.radius, e.radius * 0.4, 0, 0);
    ctx.fill();
    // Body
    const batGrad = ctx.createRadialGradient(0, 0, 1, 0, 0, e.radius * 0.6);
    batGrad.addColorStop(0, lightenColor(color, 30));
    batGrad.addColorStop(1, darkenColor(color, 30));
    ctx.beginPath();
    ctx.ellipse(0, 0, e.radius * 0.6, e.radius * 0.8, 0, 0, Math.PI * 2);
    ctx.fillStyle = batGrad;
    ctx.fill();
    // Eyes
    ctx.fillStyle = '#ff4444';
    ctx.shadowColor = '#ff4444';
    ctx.shadowBlur = 6;
    ctx.beginPath();
    ctx.arc(-3, -2, 2, 0, Math.PI * 2);
    ctx.arc(3, -2, 2, 0, Math.PI * 2);
    ctx.fill();
    ctx.shadowBlur = 0;
    // Fangs
    ctx.fillStyle = '#fff';
    ctx.beginPath();
    ctx.moveTo(-2, 2); ctx.lineTo(-1, 5); ctx.lineTo(0, 2);
    ctx.moveTo(0, 2); ctx.lineTo(1, 5); ctx.lineTo(2, 2);
    ctx.fill();
    ctx.restore();
  } else if (e.type === 'skeleton') {
    ctx.arc(0, 0, e.radius, 0, Math.PI * 2);
    const skelGrad = ctx.createRadialGradient(-2, -2, 1, 0, 0, e.radius);
    skelGrad.addColorStop(0, '#f8fafc');
    skelGrad.addColorStop(0.5, color);
    skelGrad.addColorStop(1, '#94a3b8');
    ctx.fillStyle = skelGrad;
    ctx.fill();
    // Skull cracks
    ctx.strokeStyle = 'rgba(0,0,0,0.15)';
    ctx.lineWidth = 0.5;
    ctx.beginPath();
    ctx.moveTo(-2, -e.radius * 0.5);
    ctx.lineTo(0, -2);
    ctx.lineTo(3, -e.radius * 0.3);
    ctx.stroke();
    // Eye sockets
    ctx.fillStyle = '#1e1b4b';
    ctx.beginPath();
    ctx.ellipse(-4, -2, 3, 3.5, 0, 0, Math.PI * 2);
    ctx.ellipse(4, -2, 3, 3.5, 0, 0, Math.PI * 2);
    ctx.fill();
    // Red glow eyes
    ctx.fillStyle = '#ef4444';
    ctx.shadowColor = '#ef4444';
    ctx.shadowBlur = 5;
    ctx.beginPath();
    ctx.arc(-4, -2, 1.5, 0, Math.PI * 2);
    ctx.arc(4, -2, 1.5, 0, Math.PI * 2);
    ctx.fill();
    ctx.shadowBlur = 0;
    // Jaw
    ctx.strokeStyle = '#64748b';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.arc(0, 4, 5, 0, Math.PI);
    ctx.stroke();
  } else if (e.type === 'dark-knight') {
    ctx.arc(0, 0, e.radius, 0, Math.PI * 2);
    const dkGrad = ctx.createRadialGradient(-4, -4, 2, 0, 0, e.radius);
    dkGrad.addColorStop(0, '#64748b');
    dkGrad.addColorStop(0.5, color);
    dkGrad.addColorStop(1, '#1e293b');
    ctx.fillStyle = dkGrad;
    ctx.fill();
    // Armor lines
    ctx.strokeStyle = 'rgba(200,200,220,0.15)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.arc(0, 0, e.radius * 0.75, -Math.PI * 0.4, Math.PI * 0.4);
    ctx.stroke();
    ctx.beginPath();
    ctx.arc(0, 0, e.radius * 0.5, -Math.PI * 0.3, Math.PI * 0.3);
    ctx.stroke();
    // Visor with glow
    ctx.fillStyle = '#ef4444';
    ctx.shadowColor = '#ef4444';
    ctx.shadowBlur = 8;
    ctx.fillRect(-6, -3, 12, 3);
    ctx.shadowBlur = 0;
    // Horns
    ctx.strokeStyle = '#1e293b';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(-e.radius * 0.5, -e.radius * 0.5);
    ctx.lineTo(-e.radius * 0.7, -e.radius * 0.9);
    ctx.moveTo(e.radius * 0.5, -e.radius * 0.5);
    ctx.lineTo(e.radius * 0.7, -e.radius * 0.9);
    ctx.stroke();
  } else if (e.type === 'dragon') {
    ctx.arc(0, 0, e.radius, 0, Math.PI * 2);
    const drGrad = ctx.createRadialGradient(-8, -8, 4, 0, 0, e.radius);
    drGrad.addColorStop(0, '#fca5a5');
    drGrad.addColorStop(0.4, color);
    drGrad.addColorStop(1, '#7f1d1d');
    ctx.fillStyle = drGrad;
    ctx.fill();
    // Scale pattern
    ctx.strokeStyle = 'rgba(255,200,100,0.2)';
    ctx.lineWidth = 0.7;
    for (let i = 0; i < 6; i++) {
      ctx.beginPath();
      ctx.arc(0, 0, e.radius * (0.25 + i * 0.13), 0, Math.PI * 2);
      ctx.stroke();
    }
    // Fire breath glow
    const ang = Math.atan2(camY - e.pos.y, camX - e.pos.x);
    ctx.save();
    ctx.rotate(ang);
    const fbGrad = ctx.createRadialGradient(e.radius * 0.5, 0, 2, e.radius * 0.5, 0, 20);
    fbGrad.addColorStop(0, `rgba(255,200,50,${0.3 + Math.sin(time * 6) * 0.15})`);
    fbGrad.addColorStop(1, 'rgba(255,100,0,0)');
    ctx.fillStyle = fbGrad;
    ctx.beginPath();
    ctx.arc(e.radius * 0.5, 0, 20, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
    // Eyes
    ctx.fillStyle = '#fbbf24';
    ctx.shadowColor = '#fbbf24';
    ctx.shadowBlur = 8;
    ctx.beginPath();
    ctx.ellipse(-10, -8, 4, 3, 0, 0, Math.PI * 2);
    ctx.ellipse(10, -8, 4, 3, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = '#000';
    ctx.shadowBlur = 0;
    ctx.beginPath();
    ctx.ellipse(-10, -8, 1.5, 3, 0, 0, Math.PI * 2);
    ctx.ellipse(10, -8, 1.5, 3, 0, 0, Math.PI * 2);
    ctx.fill();
  } else if (e.type === 'lich') {
    ctx.arc(0, 0, e.radius, 0, Math.PI * 2);
    const lGrad = ctx.createRadialGradient(-5, -5, 2, 0, 0, e.radius);
    lGrad.addColorStop(0, '#c084fc');
    lGrad.addColorStop(0.5, color);
    lGrad.addColorStop(1, '#3b0764');
    ctx.fillStyle = lGrad;
    ctx.fill();
    // Soul wisps orbiting
    for (let i = 0; i < 5; i++) {
      const ang = time * 2 + (i / 5) * Math.PI * 2;
      const dist = e.radius + 8 + Math.sin(time * 3 + i) * 3;
      const ox = Math.cos(ang) * dist;
      const oy = Math.sin(ang) * dist;
      ctx.beginPath();
      ctx.arc(ox, oy, 3, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(196,132,252,${0.4 + Math.sin(time * 4 + i) * 0.25})`;
      ctx.fill();
    }
    // Skull face
    ctx.fillStyle = '#e9d5ff';
    ctx.beginPath();
    ctx.arc(0, -2, e.radius * 0.45, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = '#3b0764';
    ctx.beginPath();
    ctx.ellipse(-5, -4, 3, 4, 0, 0, Math.PI * 2);
    ctx.ellipse(5, -4, 3, 4, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = '#a855f7';
    ctx.shadowColor = '#a855f7';
    ctx.shadowBlur = 6;
    ctx.beginPath();
    ctx.arc(-5, -4, 1.5, 0, Math.PI * 2);
    ctx.arc(5, -4, 1.5, 0, Math.PI * 2);
    ctx.fill();
    ctx.shadowBlur = 0;
  } else if (e.type === 'golem') {
    ctx.arc(0, 0, e.radius, 0, Math.PI * 2);
    const gGrad = ctx.createRadialGradient(-6, -6, 3, 0, 0, e.radius);
    gGrad.addColorStop(0, '#cbd5e1');
    gGrad.addColorStop(0.5, color);
    gGrad.addColorStop(1, '#334155');
    ctx.fillStyle = gGrad;
    ctx.fill();
    // Rocky texture
    ctx.strokeStyle = 'rgba(0,0,0,0.15)';
    ctx.lineWidth = 1;
    for (let i = 0; i < 5; i++) {
      const ang = (i / 5) * Math.PI * 2 + 0.3;
      ctx.beginPath();
      ctx.moveTo(Math.cos(ang) * e.radius * 0.3, Math.sin(ang) * e.radius * 0.3);
      ctx.lineTo(Math.cos(ang + 0.4) * e.radius * 0.7, Math.sin(ang + 0.4) * e.radius * 0.7);
      ctx.stroke();
    }
    // Lava cracks
    ctx.strokeStyle = 'rgba(255,150,50,0.4)';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(-8, -e.radius * 0.5);
    ctx.lineTo(0, 0);
    ctx.lineTo(8, e.radius * 0.5);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(e.radius * 0.3, -e.radius * 0.4);
    ctx.lineTo(0, 5);
    ctx.lineTo(-e.radius * 0.3, e.radius * 0.3);
    ctx.stroke();
    // Glowing core
    const cGrad = ctx.createRadialGradient(0, 0, 2, 0, 0, e.radius * 0.35);
    cGrad.addColorStop(0, 'rgba(255,150,50,0.5)');
    cGrad.addColorStop(1, 'rgba(255,100,0,0)');
    ctx.fillStyle = cGrad;
    ctx.beginPath();
    ctx.arc(0, 0, e.radius * 0.35, 0, Math.PI * 2);
    ctx.fill();
    // Eyes
    ctx.fillStyle = '#fbbf24';
    ctx.shadowColor = '#fbbf24';
    ctx.shadowBlur = 6;
    ctx.beginPath();
    ctx.arc(-10, -10, 4, 0, Math.PI * 2);
    ctx.arc(10, -10, 4, 0, Math.PI * 2);
    ctx.fill();
    ctx.shadowBlur = 0;
  } else {
    ctx.arc(0, 0, e.radius, 0, Math.PI * 2);
    ctx.fillStyle = color;
    ctx.fill();
  }

  ctx.shadowBlur = 0;

  // HP bar for tough enemies
  if (e.hp < e.maxHp && (e.isBoss || e.maxHp > 30)) {
    const barW = e.radius * 2.4;
    const barH = e.isBoss ? 7 : 5;
    const barY = -e.radius - 14;
    ctx.fillStyle = 'rgba(0,0,0,0.7)';
    roundRect(ctx, -barW / 2 - 1, barY - 1, barW + 2, barH + 2, 3);
    ctx.fill();
    const hpPct = e.hp / e.maxHp;
    const hpColor = hpPct > 0.5 ? '#ef4444' : hpPct > 0.25 ? '#f97316' : '#dc2626';
    const hpGrad = ctx.createLinearGradient(-barW / 2, 0, barW / 2, 0);
    hpGrad.addColorStop(0, lightenColor(hpColor, 20));
    hpGrad.addColorStop(1, hpColor);
    ctx.fillStyle = hpGrad;
    roundRect(ctx, -barW / 2, barY, barW * hpPct, barH, 3);
    ctx.fill();
  }

  ctx.restore();
}

function drawProjectile(ctx: CanvasRenderingContext2D, p: Projectile, time: number) {
  ctx.save();
  ctx.translate(p.pos.x, p.pos.y);

  // Trail glow
  const trailGrad = ctx.createRadialGradient(0, 0, 1, 0, 0, p.radius * 4);
  trailGrad.addColorStop(0, hexToRgba(p.color, 0.45));
  trailGrad.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.fillStyle = trailGrad;
  ctx.beginPath();
  ctx.arc(0, 0, p.radius * 4, 0, Math.PI * 2);
  ctx.fill();

  // Core
  ctx.shadowColor = p.color;
  ctx.shadowBlur = 15;
  const coreGrad = ctx.createRadialGradient(0, 0, 0, 0, 0, p.radius);
  coreGrad.addColorStop(0, '#fff');
  coreGrad.addColorStop(0.3, lightenColor(p.color, 40));
  coreGrad.addColorStop(1, p.color);
  ctx.beginPath();
  ctx.arc(0, 0, p.radius, 0, Math.PI * 2);
  ctx.fillStyle = coreGrad;
  ctx.fill();
  ctx.restore();
}

function drawParticle(ctx: CanvasRenderingContext2D, p: Particle) {
  const alpha = p.lifetime / p.maxLifetime;
  ctx.save();
  ctx.globalAlpha = alpha;

  const glowR = p.size * alpha * 2.5;
  const pGrad = ctx.createRadialGradient(p.pos.x, p.pos.y, 0, p.pos.x, p.pos.y, glowR);
  pGrad.addColorStop(0, p.color);
  pGrad.addColorStop(0.4, hexToRgba(p.color, 0.35 * alpha));
  pGrad.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.fillStyle = pGrad;
  ctx.beginPath();
  ctx.arc(p.pos.x, p.pos.y, glowR, 0, Math.PI * 2);
  ctx.fill();

  ctx.fillStyle = '#fff';
  ctx.beginPath();
  ctx.arc(p.pos.x, p.pos.y, p.size * alpha * 0.5, 0, Math.PI * 2);
  ctx.fill();
  ctx.restore();
}

function drawPowerUp(ctx: CanvasRenderingContext2D, pu: PowerUp, time: number) {
  ctx.save();
  ctx.translate(pu.pos.x, pu.pos.y);

  const pulse = 1 + Math.sin(time * 4) * 0.15;
  const bob = Math.sin(time * 3) * 4;
  ctx.translate(0, bob);

  const colorMap: Record<string, string> = {
    speed: COLORS.speedPU,
    'triple-shot': COLORS.triplePU,
    shield: COLORS.shieldPU,
    heal: COLORS.healPU,
  };
  const color = colorMap[pu.type] || '#fff';

  // Ground glow
  ctx.save();
  ctx.translate(0, pu.radius + 6 - bob);
  ctx.beginPath();
  ctx.ellipse(0, 0, pu.radius * 1.5, 5, 0, 0, Math.PI * 2);
  ctx.fillStyle = hexToRgba(color, 0.2);
  ctx.fill();
  ctx.restore();

  // Outer glow
  const outerGrad = ctx.createRadialGradient(0, 0, pu.radius * 0.3, 0, 0, pu.radius * 2.5);
  outerGrad.addColorStop(0, hexToRgba(color, 0.25));
  outerGrad.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.fillStyle = outerGrad;
  ctx.beginPath();
  ctx.arc(0, 0, pu.radius * 2.5, 0, Math.PI * 2);
  ctx.fill();

  // Rotating sparkles
  for (let i = 0; i < 5; i++) {
    const a = time * 2.5 + (i / 5) * Math.PI * 2;
    const sr = pu.radius * 1.5 * pulse;
    const sx = Math.cos(a) * sr;
    const sy = Math.sin(a) * sr;
    ctx.fillStyle = `rgba(255,255,255,${0.35 + Math.sin(time * 5 + i) * 0.2})`;
    ctx.beginPath();
    ctx.arc(sx, sy, 2, 0, Math.PI * 2);
    ctx.fill();
  }

  // Main orb
  ctx.shadowColor = color;
  ctx.shadowBlur = 18;
  const orbGrad = ctx.createRadialGradient(-2, -2, 1, 0, 0, pu.radius * pulse);
  orbGrad.addColorStop(0, '#fff');
  orbGrad.addColorStop(0.25, lightenColor(color, 40));
  orbGrad.addColorStop(1, color);
  ctx.beginPath();
  ctx.arc(0, 0, pu.radius * pulse, 0, Math.PI * 2);
  ctx.fillStyle = orbGrad;
  ctx.fill();
  ctx.shadowBlur = 0;

  const iconMap: Record<string, string> = {
    speed: '💨',
    'triple-shot': '🔥',
    shield: '🛡️',
    heal: '💚',
  };
  ctx.font = '14px serif';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText(iconMap[pu.type] || '?', 0, 0);
  ctx.restore();
}

// ---- Utility ----

function roundRect(ctx: CanvasRenderingContext2D, x: number, y: number, w: number, h: number, r: number) {
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.lineTo(x + w - r, y);
  ctx.quadraticCurveTo(x + w, y, x + w, y + r);
  ctx.lineTo(x + w, y + h - r);
  ctx.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
  ctx.lineTo(x + r, y + h);
  ctx.quadraticCurveTo(x, y + h, x, y + h - r);
  ctx.lineTo(x, y + r);
  ctx.quadraticCurveTo(x, y, x + r, y);
  ctx.closePath();
}

function hexToRgba(hex: string, alpha: number): string {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return `rgba(${r},${g},${b},${alpha})`;
}

function lightenColor(hex: string, amount: number): string {
  const r = Math.min(255, parseInt(hex.slice(1, 3), 16) + amount);
  const g = Math.min(255, parseInt(hex.slice(3, 5), 16) + amount);
  const b = Math.min(255, parseInt(hex.slice(5, 7), 16) + amount);
  return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
}

function darkenColor(hex: string, amount: number): string {
  const r = Math.max(0, parseInt(hex.slice(1, 3), 16) - amount);
  const g = Math.max(0, parseInt(hex.slice(3, 5), 16) - amount);
  const b = Math.max(0, parseInt(hex.slice(5, 7), 16) - amount);
  return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
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
