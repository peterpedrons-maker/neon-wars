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

  if (p.invincibleTimer > 0 && Math.floor(Date.now() / 80) % 2 === 0) {
    ctx.globalAlpha = 0.5;
  }

  ctx.shadowColor = glowColor;
  ctx.shadowBlur = 20 + Math.sin(time * 3) * 5;

  // --- ANIMATION STATE ---
  const walkSpeed = Math.hypot(p.vel?.x || 0, p.vel?.y || 0);
  const isWalking = walkSpeed > 10;
  const walkCycle = isWalking ? time * 10 : 0;
  const bob = isWalking ? Math.sin(walkCycle * 1.2) * 2.5 : Math.sin(time * 2) * 0.5; // idle breathe
  const legSwing = isWalking ? Math.sin(walkCycle) * 0.5 : 0;
  const armSwingIdle = Math.sin(time * 1.5) * 0.05; // subtle idle sway

  // Attack animation progress (0 = no attack, 1 = peak of attack)
  const atkRatio = p.attackTimer / p.attackCooldown;
  const atkProgress = atkRatio > 0.5 ? (atkRatio - 0.5) * 2 : 0; // first half is swing
  const atkRetract = atkRatio > 0 && atkRatio <= 0.5 ? (0.5 - atkRatio) * 2 : 0; // second half returns
  const atkAnim = atkProgress > 0 ? atkProgress : -atkRetract * 0.3;

  // Body lean when walking
  const bodyLean = isWalking ? Math.sin(walkCycle * 0.6) * 0.03 : 0;

  ctx.save();
  ctx.rotate(p.angle + bodyLean);

  // --- CLASS COLORS ---
  let skinColor = '#f5d0a9';
  let hairColor = '#4a2c0a';
  let tunicColor = '#6b21a8';
  let tunicLight = '#9333ea';
  let pantsColor = '#3b0764';
  let bootColor = '#44403c';
  let capeColor = '#7c3aed';

  if (p.class === 'archer') {
    tunicColor = '#065f46'; tunicLight = '#059669'; pantsColor = '#064e3b';
    bootColor = '#78350f'; hairColor = '#b45309'; capeColor = '#047857';
  } else if (p.class === 'warrior') {
    tunicColor = '#78350f'; tunicLight = '#92400e'; pantsColor = '#451a03';
    bootColor = '#292524'; hairColor = '#1c1917'; capeColor = '#dc2626';
  }

  // Cape (behind body) with movement physics
  const capeWind = isWalking ? Math.sin(time * 5) * 4 : Math.sin(time * 1.5) * 1;
  ctx.fillStyle = capeColor;
  ctx.beginPath();
  ctx.moveTo(-5, -2);
  ctx.quadraticCurveTo(-14 - capeWind, 8, -10 - capeWind * 0.5, 18 + bob * 0.5);
  ctx.lineTo(2, 18 + bob * 0.5);
  ctx.quadraticCurveTo(-2, 6, -5, -2);
  ctx.fill();
  ctx.fillStyle = darkenColor(capeColor, 30);
  ctx.beginPath();
  ctx.moveTo(-4, 2);
  ctx.quadraticCurveTo(-12 - capeWind * 0.7, 10, -8 - capeWind * 0.3, 16 + bob * 0.3);
  ctx.lineTo(0, 16 + bob * 0.3);
  ctx.quadraticCurveTo(-1, 8, -4, 2);
  ctx.fill();

  // Left leg (back)
  ctx.save();
  ctx.translate(-3, 10);
  ctx.rotate(-legSwing);
  ctx.fillStyle = pantsColor;
  ctx.fillRect(-2.5, 0, 5, 10);
  // Knee highlight
  ctx.fillStyle = lightenColor(pantsColor, 15);
  ctx.fillRect(-1.5, 4, 3, 2);
  ctx.fillStyle = bootColor;
  roundRect(ctx, -3, 8, 6, 4, 1.5);
  ctx.fill();
  // Boot detail
  ctx.strokeStyle = 'rgba(255,255,255,0.1)';
  ctx.lineWidth = 0.5;
  ctx.beginPath(); ctx.moveTo(-3, 10); ctx.lineTo(3, 10); ctx.stroke();
  ctx.restore();

  // Right leg (front)
  ctx.save();
  ctx.translate(3, 10);
  ctx.rotate(legSwing);
  ctx.fillStyle = pantsColor;
  ctx.fillRect(-2.5, 0, 5, 10);
  ctx.fillStyle = lightenColor(pantsColor, 15);
  ctx.fillRect(-1.5, 4, 3, 2);
  ctx.fillStyle = bootColor;
  roundRect(ctx, -3, 8, 6, 4, 1.5);
  ctx.fill();
  ctx.strokeStyle = 'rgba(255,255,255,0.1)';
  ctx.lineWidth = 0.5;
  ctx.beginPath(); ctx.moveTo(-3, 10); ctx.lineTo(3, 10); ctx.stroke();
  ctx.restore();

  // Torso
  ctx.fillStyle = tunicColor;
  roundRect(ctx, -7, -4 + bob, 14, 16, 3);
  ctx.fill();
  ctx.fillStyle = tunicLight;
  ctx.fillRect(-1.5, -2 + bob, 3, 12);
  // Shoulder pads
  if (p.class === 'warrior') {
    ctx.fillStyle = '#57534e';
    ctx.beginPath();
    ctx.ellipse(-8, -2 + bob, 4, 3, -0.2, 0, Math.PI * 2);
    ctx.ellipse(8, -2 + bob, 4, 3, 0.2, 0, Math.PI * 2);
    ctx.fill();
    ctx.strokeStyle = 'rgba(255,255,255,0.1)';
    ctx.lineWidth = 0.5;
    ctx.stroke();
  }
  // Belt
  ctx.fillStyle = '#78350f';
  ctx.fillRect(-7, 8 + bob, 14, 3);
  ctx.fillStyle = '#fbbf24';
  ctx.beginPath();
  ctx.arc(0, 9.5 + bob, 2, 0, Math.PI * 2);
  ctx.fill();

  // Left arm (back arm - follows walk)
  const leftArmSwing = isWalking ? Math.sin(walkCycle) * 0.4 : armSwingIdle;
  ctx.save();
  ctx.translate(-8, -1 + bob);
  ctx.rotate(leftArmSwing);
  ctx.fillStyle = tunicColor;
  roundRect(ctx, -3, 0, 5, 12, 2);
  ctx.fill();
  ctx.fillStyle = skinColor;
  ctx.beginPath();
  ctx.arc(-0.5, 13, 3, 0, Math.PI * 2);
  ctx.fill();
  ctx.restore();

  // Right arm + weapon (ATTACK ARM)
  const weaponArmBase = isWalking ? -Math.sin(walkCycle) * 0.3 : -armSwingIdle;
  ctx.save();
  ctx.translate(8, -1 + bob);

  if (p.class === 'warrior') {
    // Warrior: big overhead swing arc
    const swingAngle = atkAnim > 0 ? -Math.PI * 0.8 * atkAnim : weaponArmBase + atkAnim * 0.5;
    ctx.rotate(swingAngle);
    // Upper arm
    ctx.fillStyle = tunicColor;
    roundRect(ctx, -2, 0, 5, 12, 2);
    ctx.fill();
    ctx.fillStyle = skinColor;
    ctx.beginPath();
    ctx.arc(0.5, 13, 3, 0, Math.PI * 2);
    ctx.fill();
    // Sword with trail effect during attack
    ctx.save();
    ctx.translate(0.5, 13);
    const swordRotate = atkAnim > 0 ? -0.3 : 0;
    ctx.rotate(swordRotate);
    // Sword blade
    const swordGrad = ctx.createLinearGradient(0, 8, 0, -12);
    swordGrad.addColorStop(0, '#aaa');
    swordGrad.addColorStop(0.5, '#e8e8e8');
    swordGrad.addColorStop(1, '#ccc');
    ctx.fillStyle = swordGrad;
    ctx.beginPath();
    ctx.moveTo(1, 8); ctx.lineTo(2.5, -4); ctx.lineTo(1, -10);
    ctx.lineTo(-1, -10); ctx.lineTo(-2.5, -4); ctx.lineTo(-1, 8);
    ctx.closePath();
    ctx.fill();
    // Edge highlight
    ctx.strokeStyle = 'rgba(255,255,255,0.5)';
    ctx.lineWidth = 0.5;
    ctx.beginPath(); ctx.moveTo(0, -9); ctx.lineTo(0, 7); ctx.stroke();
    // Guard
    ctx.fillStyle = '#a0522d';
    ctx.fillRect(-5, 8, 10, 3);
    ctx.fillStyle = '#5c3a1e';
    ctx.fillRect(-1.5, 11, 3, 6);
    ctx.fillStyle = '#ef4444';
    ctx.beginPath(); ctx.arc(0, 18, 2.5, 0, Math.PI * 2); ctx.fill();
    // Attack trail glow
    if (atkAnim > 0) {
      ctx.shadowColor = '#f97316';
      ctx.shadowBlur = 15 * atkAnim;
      ctx.strokeStyle = `rgba(253,186,116,${0.6 * atkAnim})`;
      ctx.lineWidth = 3;
      ctx.beginPath();
      ctx.moveTo(0, -10); ctx.lineTo(0, 6);
      ctx.stroke();
      ctx.shadowBlur = 0;
    }
    ctx.restore();
  } else if (p.class === 'archer') {
    // Archer: draw-back bow animation
    const drawBack = atkAnim > 0 ? atkAnim * 8 : 0;
    const releaseSnap = atkRetract > 0 ? Math.sin(atkRetract * Math.PI) * 2 : 0;
    ctx.rotate(weaponArmBase);
    ctx.fillStyle = tunicColor;
    roundRect(ctx, -2, 0, 5, 12, 2);
    ctx.fill();
    ctx.fillStyle = skinColor;
    ctx.beginPath();
    ctx.arc(0.5, 13, 3, 0, Math.PI * 2);
    ctx.fill();
    // Bow
    ctx.save();
    ctx.translate(0.5, 6);
    const bowFlex = 1 + drawBack * 0.02;
    ctx.strokeStyle = '#78350f';
    ctx.lineWidth = 2.5;
    ctx.beginPath();
    ctx.arc(5, 0, 14 * bowFlex, -1.2, 1.2);
    ctx.stroke();
    // Bowstring (pulled back when attacking)
    ctx.strokeStyle = 'rgba(220,220,220,0.8)';
    ctx.lineWidth = 0.8;
    const stringPull = drawBack + releaseSnap;
    ctx.beginPath();
    ctx.moveTo(5 + Math.cos(-1.2) * 14 * bowFlex, Math.sin(-1.2) * 14 * bowFlex);
    ctx.lineTo(2 - stringPull, 0);
    ctx.lineTo(5 + Math.cos(1.2) * 14 * bowFlex, Math.sin(1.2) * 14 * bowFlex);
    ctx.stroke();
    // Arrow (visible when drawing)
    if (atkAnim > 0 || drawBack > 0) {
      ctx.save();
      ctx.translate(2 - stringPull, 0);
      // Arrow shaft
      ctx.strokeStyle = '#78350f';
      ctx.lineWidth = 1.2;
      ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(16, 0); ctx.stroke();
      // Arrowhead
      ctx.fillStyle = '#94a3b8';
      ctx.beginPath();
      ctx.moveTo(18, 0); ctx.lineTo(14, -2.5); ctx.lineTo(14, 2.5);
      ctx.closePath();
      ctx.fill();
      // Fletching
      ctx.fillStyle = '#dc2626';
      ctx.beginPath();
      ctx.moveTo(0, 0); ctx.lineTo(-3, -2); ctx.lineTo(-2, 0);
      ctx.moveTo(0, 0); ctx.lineTo(-3, 2); ctx.lineTo(-2, 0);
      ctx.fill();
      ctx.restore();
    }
    // Release flash
    if (atkRetract > 0.5) {
      ctx.fillStyle = `rgba(34,211,238,${(atkRetract - 0.5) * 0.6})`;
      ctx.beginPath();
      ctx.arc(16, 0, 6, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.restore();
  } else {
    // Mage: staff thrust + magic burst
    const castThrust = atkAnim > 0 ? atkAnim * 0.4 : 0;
    ctx.rotate(weaponArmBase - castThrust);
    ctx.fillStyle = tunicColor;
    roundRect(ctx, -2, 0, 5, 12, 2);
    ctx.fill();
    ctx.fillStyle = skinColor;
    ctx.beginPath();
    ctx.arc(0.5, 13, 3, 0, Math.PI * 2);
    ctx.fill();
    // Staff
    ctx.save();
    ctx.translate(0.5, 6);
    const staffExtend = atkAnim > 0 ? -atkAnim * 4 : 0;
    ctx.strokeStyle = '#5c3a1e';
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(0, 12); ctx.lineTo(0, -10 + staffExtend);
    ctx.stroke();
    // Staff head ornament
    ctx.fillStyle = '#78350f';
    ctx.beginPath();
    ctx.moveTo(-3, -8 + staffExtend); ctx.lineTo(0, -12 + staffExtend);
    ctx.lineTo(3, -8 + staffExtend);
    ctx.closePath();
    ctx.fill();
    // Crystal orb
    const orbY = -13 + staffExtend;
    const orbPulse = 1 + (atkAnim > 0 ? atkAnim * 0.4 : Math.sin(time * 3) * 0.1);
    const orbGrad = ctx.createRadialGradient(0, orbY, 1, 0, orbY, 6 * orbPulse);
    orbGrad.addColorStop(0, '#fff');
    orbGrad.addColorStop(0.3, '#c084fc');
    orbGrad.addColorStop(1, '#7c3aed');
    ctx.beginPath();
    ctx.arc(0, orbY, 6 * orbPulse, 0, Math.PI * 2);
    ctx.fillStyle = orbGrad;
    ctx.fill();
    // Magic burst during attack
    if (atkAnim > 0) {
      ctx.shadowColor = '#a855f7';
      ctx.shadowBlur = 20 * atkAnim;
      ctx.beginPath();
      ctx.arc(0, orbY, 6 * orbPulse, 0, Math.PI * 2);
      ctx.fill();
      // Magic sparkles radiating out
      for (let i = 0; i < 6; i++) {
        const sparkAngle = time * 8 + (i / 6) * Math.PI * 2;
        const sparkDist = 8 + atkAnim * 12;
        const sx = Math.cos(sparkAngle) * sparkDist;
        const sy = orbY + Math.sin(sparkAngle) * sparkDist;
        ctx.fillStyle = `rgba(216,180,254,${0.7 * atkAnim})`;
        ctx.beginPath();
        ctx.arc(sx, sy, 1.5 * atkAnim, 0, Math.PI * 2);
        ctx.fill();
      }
      ctx.shadowBlur = 0;
    }
    // Sparkle on orb
    ctx.fillStyle = `rgba(255,255,255,${0.6 + Math.sin(time * 5) * 0.3})`;
    ctx.beginPath();
    ctx.arc(-1.5, orbY - 2, 1.2, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
  }
  ctx.restore(); // right arm

  // Head
  ctx.save();
  ctx.translate(0, -10 + bob);
  // Head bob during attack
  const headTilt = atkAnim > 0 ? atkAnim * 0.1 : 0;
  ctx.rotate(headTilt);

  ctx.fillStyle = skinColor;
  ctx.fillRect(-2.5, 3, 5, 4);
  ctx.fillStyle = skinColor;
  ctx.beginPath();
  ctx.arc(0, -2, 8, 0, Math.PI * 2);
  ctx.fill();
  ctx.fillStyle = hairColor;
  ctx.beginPath();
  ctx.arc(0, -3, 8.5, -Math.PI, -0.1);
  ctx.fill();

  if (p.class === 'mage') {
    ctx.fillStyle = '#6b21a8';
    ctx.beginPath();
    ctx.moveTo(-10, -4); ctx.lineTo(0, -22); ctx.lineTo(10, -4);
    ctx.closePath();
    ctx.fill();
    ctx.fillStyle = '#581c87';
    ctx.beginPath();
    ctx.ellipse(0, -4, 13, 4, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = '#fbbf24';
    ctx.fillRect(-8, -6, 16, 2);
    ctx.font = '7px serif';
    ctx.textAlign = 'center';
    ctx.fillText('★', 0, -13);
  } else if (p.class === 'archer') {
    ctx.fillStyle = '#065f46';
    ctx.beginPath();
    ctx.arc(0, -3, 9.5, -Math.PI, 0);
    ctx.lineTo(9.5, 0);
    ctx.quadraticCurveTo(10, -2, 8, -3);
    ctx.lineTo(-8, -3);
    ctx.quadraticCurveTo(-10, -2, -9.5, 0);
    ctx.closePath();
    ctx.fill();
    ctx.beginPath();
    ctx.moveTo(-3, -11); ctx.lineTo(-8, -16); ctx.lineTo(2, -12);
    ctx.closePath();
    ctx.fillStyle = '#047857';
    ctx.fill();
  } else {
    ctx.fillStyle = '#57534e';
    ctx.beginPath();
    ctx.arc(0, -3, 9, -Math.PI, 0.1);
    ctx.fill();
    ctx.strokeStyle = '#78716c';
    ctx.lineWidth = 2.5;
    ctx.beginPath();
    ctx.arc(0, -3, 9, -2.8, -0.3);
    ctx.stroke();
    ctx.fillStyle = '#57534e';
    ctx.fillRect(-1.5, -6, 3, 8);
    ctx.fillStyle = '#a8a29e';
    ctx.beginPath();
    ctx.moveTo(-7, -8); ctx.lineTo(-10, -16); ctx.lineTo(-5, -10);
    ctx.closePath();
    ctx.fill();
    ctx.beginPath();
    ctx.moveTo(7, -8); ctx.lineTo(10, -16); ctx.lineTo(5, -10);
    ctx.closePath();
    ctx.fill();
  }

  // Eyes - squint during attack
  const eyeH = atkAnim > 0.3 ? 1.2 : 2;
  ctx.fillStyle = '#fff';
  ctx.beginPath();
  ctx.ellipse(-3, -2, 2.5, eyeH, 0, 0, Math.PI * 2);
  ctx.ellipse(3, -2, 2.5, eyeH, 0, 0, Math.PI * 2);
  ctx.fill();
  const eyeColor = p.class === 'mage' ? '#a855f7' : p.class === 'archer' ? '#22d3ee' : '#f97316';
  ctx.fillStyle = eyeColor;
  ctx.beginPath();
  ctx.arc(-2.5, -2, 1.3, 0, Math.PI * 2);
  ctx.arc(3.5, -2, 1.3, 0, Math.PI * 2);
  ctx.fill();
  ctx.fillStyle = '#000';
  ctx.beginPath();
  ctx.arc(-2.5, -2, 0.7, 0, Math.PI * 2);
  ctx.ac(3.5, -2, 0.7, 0, Math.PI * 2);
  ctx.fill();
  // Battle cry mouth during attack
  if (atkAnim > 0.5) {
    ctx.fillStyle = '#5c3a1e';
    ctx.beginPath();
    ctx.ellipse(0, 2.5, 2.5 * atkAnim, 2 * atkAnim, 0, 0, Math.PI * 2);
    ctx.fill();
  } else {
    ctx.strokeStyle = '#a0522d';
    ctx.lineWidth = 0.8;
    ctx.beginPath();
    ctx.arc(0, 2, 2.5, 0.2, Math.PI - 0.2);
    ctx.stroke();
  }
  ctx.restore(); // head

  ctx.restore(); // angle rotation

  // Mage orbiting runes
  if (p.class === 'mage') {
    for (let i = 0; i < 3; i++) {
      const a = time * 1.5 + (i / 3) * Math.PI * 2;
      const runeSpeed = atkAnim > 0 ? 3 : 1;
      const ox = Math.cos(a * runeSpeed) * (p.radius + 10);
      const oy = Math.sin(a * runeSpeed) * (p.radius + 10);
      ctx.beginPath();
      ctx.arc(ox, oy, 2.5 + atkAnim * 2, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(216,180,254,${0.5 + Math.sin(time * 3 + i) * 0.3})`;
      ctx.fill();
    }
  }

  // Warrior melee arc with slash VFX
  if (p.class === 'warrior' && p.attackTimer > p.attackCooldown * 0.4) {
    const slashProg = (p.attackTimer / p.attackCooldown - 0.4) / 0.6;
    ctx.save();
    ctx.rotate(p.angle);
    // Slash arc
    const arcStart = -1.0 + (1 - slashProg) * 1.5;
    const arcEnd = arcStart + 1.2;
    ctx.beginPath();
    ctx.moveTo(0, 0);
    ctx.arc(0, 0, WARRIOR_ATTACK_RANGE, arcStart, arcEnd);
    ctx.closePath();
    const slashGrad = ctx.createRadialGradient(0, 0, p.radius, 0, 0, WARRIOR_ATTACK_RANGE);
    slashGrad.addColorStop(0, `rgba(249,115,22,${0.6 * slashProg})`);
    slashGrad.addColorStop(1, 'rgba(249,115,22,0)');
    ctx.fillStyle = slashGrad;
    ctx.fill();
    // Bright slash edge
    ctx.beginPath();
    ctx.arc(0, 0, WARRIOR_ATTACK_RANGE * 0.95, arcStart, arcEnd);
    ctx.strokeStyle = `rgba(253,224,170,${0.8 * slashProg})`;
    ctx.lineWidth = 3;
    ctx.stroke();
    // Spark particles along edge
    for (let i = 0; i < 4; i++) {
      const sa = arcStart + (arcEnd - arcStart) * (i / 3);
      const sr = WARRIOR_ATTACK_RANGE * (0.7 + Math.random() * 0.3);
      ctx.fillStyle = `rgba(255,220,120,${0.5 * slashProg})`;
      ctx.beginPath();
      ctx.arc(Math.cos(sa) * sr, Math.sin(sa) * sr, 2 * slashProg, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.restore();
  }

  // Archer: arrow trail VFX
  if (p.class === 'archer' && atkRetract > 0.3) {
    ctx.save();
    ctx.rotate(p.angle);
    const trailAlpha = (atkRetract - 0.3) * 1.4;
    ctx.strokeStyle = `rgba(34,211,238,${trailAlpha * 0.4})`;
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(p.radius, 0);
    ctx.lineTo(p.radius + 30 * trailAlpha, 0);
    ctx.stroke();
    ctx.fillStyle = `rgba(34,211,238,${trailAlpha * 0.3})`;
    ctx.beginPath();
    ctx.arc(p.radius + 15 * trailAlpha, 0, 4 * trailAlpha, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
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

  const walkBob = Math.sin(time * 8) * 1.5;

  if (e.type === 'slime') {
    // Slime stays blob-shaped
    const wobble = Math.sin(time * 4) * 3;
    ctx.beginPath();
    ctx.ellipse(0, 2 + wobble * 0.3, e.radius + wobble * 0.6, e.radius * 0.75 - wobble * 0.3, 0, 0, Math.PI * 2);
    const slimeGrad = ctx.createRadialGradient(-4, -3, 2, 0, 0, e.radius);
    slimeGrad.addColorStop(0, lightenColor(color, 60));
    slimeGrad.addColorStop(0.4, color);
    slimeGrad.addColorStop(1, darkenColor(color, 40));
    ctx.fillStyle = slimeGrad;
    ctx.fill();
    ctx.beginPath();
    ctx.ellipse(-e.radius * 0.3, -e.radius * 0.2, e.radius * 0.3, e.radius * 0.18, -0.3, 0, Math.PI * 2);
    ctx.fillStyle = 'rgba(255,255,255,0.4)';
    ctx.fill();
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
    // Bat stays winged creature
    const wingFlap = Math.sin(time * 14) * 0.5;
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
    const batGrad = ctx.createRadialGradient(0, 0, 1, 0, 0, e.radius * 0.6);
    batGrad.addColorStop(0, lightenColor(color, 30));
    batGrad.addColorStop(1, darkenColor(color, 30));
    ctx.beginPath();
    ctx.ellipse(0, 0, e.radius * 0.6, e.radius * 0.8, 0, 0, Math.PI * 2);
    ctx.fillStyle = batGrad;
    ctx.fill();
    ctx.fillStyle = '#ff4444';
    ctx.shadowColor = '#ff4444';
    ctx.shadowBlur = 6;
    ctx.beginPath();
    ctx.arc(-3, -2, 2, 0, Math.PI * 2);
    ctx.arc(3, -2, 2, 0, Math.PI * 2);
    ctx.fill();
    ctx.shadowBlur = 0;
    ctx.fillStyle = '#fff';
    ctx.beginPath();
    ctx.moveTo(-2, 2); ctx.lineTo(-1, 5); ctx.lineTo(0, 2);
    ctx.moveTo(0, 2); ctx.lineTo(1, 5); ctx.lineTo(2, 2);
    ctx.fill();
  } else if (e.type === 'skeleton') {
    drawHumanoidEnemy(ctx, e, time, {
      skinColor: '#d4d4d8',
      tunicColor: '#57534e',
      tunicLight: '#78716c',
      pantsColor: '#44403c',
      bootColor: '#292524',
      headDraw: (cx) => {
        // Skull
        cx.fillStyle = '#e8e8e8';
        cx.beginPath();
        cx.arc(0, -2, 8, 0, Math.PI * 2);
        cx.fill();
        // Cracks
        cx.strokeStyle = 'rgba(0,0,0,0.2)';
        cx.lineWidth = 0.5;
        cx.beginPath();
        cx.moveTo(-2, -8); cx.lineTo(0, -2); cx.lineTo(3, -6);
        cx.stroke();
        // Eye sockets
        cx.fillStyle = '#1e1b4b';
        cx.beginPath();
        cx.ellipse(-3.5, -3, 2.5, 3, 0, 0, Math.PI * 2);
        cx.ellipse(3.5, -3, 2.5, 3, 0, 0, Math.PI * 2);
        cx.fill();
        // Red eyes
        cx.fillStyle = '#ef4444';
        cx.shadowColor = '#ef4444';
        cx.shadowBlur = 5;
        cx.beginPath();
        cx.arc(-3.5, -3, 1.2, 0, Math.PI * 2);
        cx.arc(3.5, -3, 1.2, 0, Math.PI * 2);
        cx.fill();
        cx.shadowBlur = 0;
        // Jaw
        cx.strokeStyle = '#94a3b8';
        cx.lineWidth = 1;
        cx.beginPath();
        cx.arc(0, 3, 4, 0.1, Math.PI - 0.1);
        cx.stroke();
        // Teeth
        for (let t = -3; t <= 3; t += 2) {
          cx.fillStyle = '#e8e8e8';
          cx.fillRect(t - 0.5, 2, 1, 2);
        }
      },
      weaponDraw: (cx) => {
        // Rusty sword
        cx.fillStyle = '#a8a29e';
        cx.beginPath();
        cx.moveTo(1, 8); cx.lineTo(2, -2); cx.lineTo(0, -6);
        cx.lineTo(-2, -2); cx.lineTo(-1, 8);
        cx.closePath();
        cx.fill();
        cx.fillStyle = '#5c3a1e';
        cx.fillRect(-4, 8, 8, 2.5);
        cx.fillRect(-1, 10, 2, 5);
      }
    });
  } else if (e.type === 'dark-knight') {
    drawHumanoidEnemy(ctx, e, time, {
      skinColor: '#334155',
      tunicColor: '#1e293b',
      tunicLight: '#334155',
      pantsColor: '#0f172a',
      bootColor: '#020617',
      headDraw: (cx) => {
        // Dark helmet
        cx.fillStyle = '#1e293b';
        cx.beginPath();
        cx.arc(0, -2, 9, 0, Math.PI * 2);
        cx.fill();
        // Helmet plate
        cx.fillStyle = '#334155';
        cx.beginPath();
        cx.arc(0, -3, 9.5, -Math.PI, 0);
        cx.fill();
        // Ridge
        cx.strokeStyle = '#475569';
        cx.lineWidth = 2;
        cx.beginPath();
        cx.arc(0, -3, 9, -2.5, -0.5);
        cx.stroke();
        // Visor slit - glowing red
        cx.fillStyle = '#ef4444';
        cx.shadowColor = '#ef4444';
        cx.shadowBlur = 10;
        cx.fillRect(-6, -3, 12, 2.5);
        cx.shadowBlur = 0;
        // Horns
        cx.fillStyle = '#1e293b';
        cx.beginPath();
        cx.moveTo(-7, -8); cx.lineTo(-11, -18); cx.lineTo(-4, -9);
        cx.closePath();
        cx.fill();
        cx.beginPath();
        cx.moveTo(7, -8); cx.lineTo(11, -18); cx.lineTo(4, -9);
        cx.closePath();
        cx.fill();
        // Nose guard
        cx.fillStyle = '#334155';
        cx.fillRect(-1.5, -5, 3, 7);
      },
      weaponDraw: (cx) => {
        // Dark greatsword
        cx.fillStyle = '#475569';
        cx.beginPath();
        cx.moveTo(2, 6); cx.lineTo(3, -8); cx.lineTo(0, -14);
        cx.lineTo(-3, -8); cx.lineTo(-2, 6);
        cx.closePath();
        cx.fill();
        cx.strokeStyle = 'rgba(239,68,68,0.3)';
        cx.lineWidth = 1;
        cx.beginPath();
        cx.moveTo(0, -12); cx.lineTo(0, 4);
        cx.stroke();
        cx.fillStyle = '#1e293b';
        cx.fillRect(-6, 6, 12, 3);
        cx.fillRect(-1.5, 9, 3, 6);
        cx.fillStyle = '#ef4444';
        cx.beginPath();
        cx.arc(0, 16, 2, 0, Math.PI * 2);
        cx.fill();
      }
    });
  } else if (e.type === 'dragon') {
    // Dragon stays as a large creature, but more detailed
    const r = e.radius;
    // Body
    ctx.beginPath();
    ctx.ellipse(0, 0, r, r * 0.8, 0, 0, Math.PI * 2);
    const drGrad = ctx.createRadialGradient(-r * 0.3, -r * 0.3, r * 0.1, 0, 0, r);
    drGrad.addColorStop(0, '#fca5a5');
    drGrad.addColorStop(0.4, color);
    drGrad.addColorStop(1, '#7f1d1d');
    ctx.fillStyle = drGrad;
    ctx.fill();
    // Wings
    const wingFlap = Math.sin(time * 5) * 0.3;
    ctx.fillStyle = darkenColor(color, 20);
    ctx.beginPath();
    ctx.moveTo(-r * 0.4, -r * 0.2);
    ctx.quadraticCurveTo(-r * 1.8, -r * (1.2 + wingFlap), -r * 2.2, r * 0.1);
    ctx.quadraticCurveTo(-r * 1, r * 0.3, -r * 0.4, 0);
    ctx.fill();
    ctx.beginPath();
    ctx.moveTo(r * 0.4, -r * 0.2);
    ctx.quadraticCurveTo(r * 1.8, -r * (1.2 + wingFlap), r * 2.2, r * 0.1);
    ctx.quadraticCurveTo(r * 1, r * 0.3, r * 0.4, 0);
    ctx.fill();
    // Wing membrane lines
    ctx.strokeStyle = 'rgba(255,200,100,0.15)';
    ctx.lineWidth = 0.5;
    for (let i = 0; i < 3; i++) {
      const f = 0.3 + i * 0.25;
      ctx.beginPath();
      ctx.moveTo(-r * 0.4, -r * 0.1);
      ctx.quadraticCurveTo(-r * 1.5 * f, -r * (0.8 + wingFlap) * f, -r * 2 * f, r * 0.1 * f);
      ctx.stroke();
      ctx.beginPath();
      ctx.moveTo(r * 0.4, -r * 0.1);
      ctx.quadraticCurveTo(r * 1.5 * f, -r * (0.8 + wingFlap) * f, r * 2 * f, r * 0.1 * f);
      ctx.stroke();
    }
    // Head
    ctx.fillStyle = lightenColor(color, 15);
    ctx.beginPath();
    ctx.ellipse(0, -r * 0.5, r * 0.5, r * 0.4, 0, 0, Math.PI * 2);
    ctx.fill();
    // Horns
    ctx.fillStyle = '#fbbf24';
    ctx.beginPath();
    ctx.moveTo(-r * 0.3, -r * 0.7); ctx.lineTo(-r * 0.5, -r * 1.2); ctx.lineTo(-r * 0.15, -r * 0.75);
    ctx.closePath();
    ctx.fill();
    ctx.beginPath();
    ctx.moveTo(r * 0.3, -r * 0.7); ctx.lineTo(r * 0.5, -r * 1.2); ctx.lineTo(r * 0.15, -r * 0.75);
    ctx.closePath();
    ctx.fill();
    // Eyes
    ctx.fillStyle = '#fbbf24';
    ctx.shadowColor = '#fbbf24';
    ctx.shadowBlur = 8;
    ctx.beginPath();
    ctx.ellipse(-r * 0.2, -r * 0.55, 3, 2.5, 0, 0, Math.PI * 2);
    ctx.ellipse(r * 0.2, -r * 0.55, 3, 2.5, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = '#000';
    ctx.shadowBlur = 0;
    ctx.beginPath();
    ctx.ellipse(-r * 0.2, -r * 0.55, 1, 2.5, 0, 0, Math.PI * 2);
    ctx.ellipse(r * 0.2, -r * 0.55, 1, 2.5, 0, 0, Math.PI * 2);
    ctx.fill();
    // Snout
    ctx.fillStyle = lightenColor(color, 25);
    ctx.beginPath();
    ctx.ellipse(0, -r * 0.35, r * 0.25, r * 0.15, 0, 0, Math.PI * 2);
    ctx.fill();
    // Nostrils with fire glow
    ctx.fillStyle = `rgba(255,150,30,${0.4 + Math.sin(time * 6) * 0.2})`;
    ctx.beginPath();
    ctx.arc(-r * 0.1, -r * 0.35, 2, 0, Math.PI * 2);
    ctx.arc(r * 0.1, -r * 0.35, 2, 0, Math.PI * 2);
    ctx.fill();
    // Tail
    ctx.strokeStyle = darkenColor(color, 10);
    ctx.lineWidth = 4;
    ctx.beginPath();
    ctx.moveTo(0, r * 0.6);
    ctx.quadraticCurveTo(r * 0.8, r * 1.2, r * 0.3 + Math.sin(time * 3) * 5, r * 1.6);
    ctx.stroke();
    // Scale pattern on body
    ctx.strokeStyle = 'rgba(255,200,100,0.12)';
    ctx.lineWidth = 0.5;
    for (let i = 0; i < 5; i++) {
      ctx.beginPath();
      ctx.arc(0, 0, r * (0.3 + i * 0.14), 0, Math.PI * 2);
      ctx.stroke();
    }
  } else if (e.type === 'lich') {
    drawHumanoidEnemy(ctx, e, time, {
      skinColor: '#c084fc',
      tunicColor: '#3b0764',
      tunicLight: '#581c87',
      pantsColor: '#1e0338',
      bootColor: '#0c0118',
      headDraw: (cx) => {
        // Skull face
        cx.fillStyle = '#e9d5ff';
        cx.beginPath();
        cx.arc(0, -2, 8, 0, Math.PI * 2);
        cx.fill();
        // Crown
        cx.fillStyle = '#581c87';
        for (let i = -2; i <= 2; i++) {
          cx.beginPath();
          cx.moveTo(i * 3.5 - 2, -8);
          cx.lineTo(i * 3.5, -15);
          cx.lineTo(i * 3.5 + 2, -8);
          cx.closePath();
          cx.fill();
        }
        cx.fillRect(-9, -9, 18, 3);
        // Crown gems
        cx.fillStyle = '#a855f7';
        cx.shadowColor = '#a855f7';
        cx.shadowBlur = 4;
        cx.beginPath();
        cx.arc(0, -13, 1.5, 0, Math.PI * 2);
        cx.arc(-7, -13, 1.2, 0, Math.PI * 2);
        cx.arc(7, -13, 1.2, 0, Math.PI * 2);
        cx.fill();
        cx.shadowBlur = 0;
        // Hollow eyes
        cx.fillStyle = '#3b0764';
        cx.beginPath();
        cx.ellipse(-3.5, -3, 2.5, 3.5, 0, 0, Math.PI * 2);
        cx.ellipse(3.5, -3, 2.5, 3.5, 0, 0, Math.PI * 2);
        cx.fill();
        // Purple glow eyes
        cx.fillStyle = '#a855f7';
        cx.shadowColor = '#a855f7';
        cx.shadowBlur = 8;
        cx.beginPath();
        cx.arc(-3.5, -3, 1.5, 0, Math.PI * 2);
        cx.arc(3.5, -3, 1.5, 0, Math.PI * 2);
        cx.fill();
        cx.shadowBlur = 0;
      },
      weaponDraw: (cx) => {
        // Lich staff
        cx.strokeStyle = '#3b0764';
        cx.lineWidth = 2.5;
        cx.beginPath();
        cx.moveTo(0, 16); cx.lineTo(0, -8);
        cx.stroke();
        // Skull on staff top
        cx.fillStyle = '#e9d5ff';
        cx.beginPath();
        cx.arc(0, -10, 4, 0, Math.PI * 2);
        cx.fill();
        cx.fillStyle = '#a855f7';
        cx.shadowColor = '#a855f7';
        cx.shadowBlur = 8;
        cx.beginPath();
        cx.arc(-1.5, -11, 1, 0, Math.PI * 2);
        cx.arc(1.5, -11, 1, 0, Math.PI * 2);
        cx.fill();
        cx.shadowBlur = 0;
      }
    });
    // Soul wisps around lich
    for (let i = 0; i < 5; i++) {
      const ang = time * 2 + (i / 5) * Math.PI * 2;
      const dist = e.radius + 10 + Math.sin(time * 3 + i) * 3;
      const ox = Math.cos(ang) * dist;
      const oy = Math.sin(ang) * dist;
      ctx.beginPath();
      ctx.arc(ox, oy, 3, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(196,132,252,${0.4 + Math.sin(time * 4 + i) * 0.25})`;
      ctx.fill();
    }
  } else if (e.type === 'golem') {
    // Golem: massive rocky humanoid
    const r = e.radius;
    const rockColor = color;
    // Legs (thick pillars)
    ctx.fillStyle = darkenColor(rockColor, 20);
    roundRect(ctx, -r * 0.5, r * 0.2, r * 0.4, r * 0.7, 3);
    ctx.fill();
    roundRect(ctx, r * 0.1, r * 0.2, r * 0.4, r * 0.7, 3);
    ctx.fill();
    // Body (massive boulder torso)
    const bodyGrad = ctx.createRadialGradient(-r * 0.2, -r * 0.2, r * 0.1, 0, 0, r * 0.8);
    bodyGrad.addColorStop(0, lightenColor(rockColor, 30));
    bodyGrad.addColorStop(0.5, rockColor);
    bodyGrad.addColorStop(1, darkenColor(rockColor, 40));
    ctx.fillStyle = bodyGrad;
    ctx.beginPath();
    ctx.ellipse(0, -r * 0.1, r * 0.7, r * 0.55, 0, 0, Math.PI * 2);
    ctx.fill();
    // Rocky cracks
    ctx.strokeStyle = 'rgba(0,0,0,0.2)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(-r * 0.3, -r * 0.4); ctx.lineTo(0, 0); ctx.lineTo(r * 0.3, r * 0.3);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(r * 0.2, -r * 0.3); ctx.lineTo(0, r * 0.1);
    ctx.stroke();
    // Lava cracks glow
    ctx.strokeStyle = 'rgba(255,150,50,0.5)';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(-r * 0.2, -r * 0.3); ctx.lineTo(0, -r * 0.05); ctx.lineTo(r * 0.15, r * 0.2);
    ctx.stroke();
    // Glowing core
    const cGrad = ctx.createRadialGradient(0, -r * 0.1, 2, 0, -r * 0.1, r * 0.25);
    cGrad.addColorStop(0, 'rgba(255,150,50,0.6)');
    cGrad.addColorStop(1, 'rgba(255,100,0,0)');
    ctx.fillStyle = cGrad;
    ctx.beginPath();
    ctx.arc(0, -r * 0.1, r * 0.25, 0, Math.PI * 2);
    ctx.fill();
    // Arms (massive boulders)
    ctx.fillStyle = darkenColor(rockColor, 10);
    ctx.beginPath();
    ctx.ellipse(-r * 0.8, 0, r * 0.3, r * 0.45, 0.2, 0, Math.PI * 2);
    ctx.fill();
    ctx.beginPath();
    ctx.ellipse(r * 0.8, 0, r * 0.3, r * 0.45, -0.2, 0, Math.PI * 2);
    ctx.fill();
    // Fists
    ctx.fillStyle = darkenColor(rockColor, 25);
    ctx.beginPath();
    ctx.arc(-r * 0.85, r * 0.4, r * 0.2, 0, Math.PI * 2);
    ctx.arc(r * 0.85, r * 0.4, r * 0.2, 0, Math.PI * 2);
    ctx.fill();
    // Head (small boulder on top)
    ctx.fillStyle = lightenColor(rockColor, 10);
    ctx.beginPath();
    ctx.arc(0, -r * 0.55, r * 0.35, 0, Math.PI * 2);
    ctx.fill();
    // Eyes
    ctx.fillStyle = '#fbbf24';
    ctx.shadowColor = '#fbbf24';
    ctx.shadowBlur = 8;
    ctx.beginPath();
    ctx.arc(-r * 0.15, -r * 0.58, 3.5, 0, Math.PI * 2);
    ctx.arc(r * 0.15, -r * 0.58, 3.5, 0, Math.PI * 2);
    ctx.fill();
    ctx.shadowBlur = 0;
    // Mouth crack
    ctx.strokeStyle = 'rgba(255,150,50,0.4)';
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(-r * 0.12, -r * 0.42); ctx.lineTo(0, -r * 0.38); ctx.lineTo(r * 0.12, -r * 0.42);
    ctx.stroke();
  } else {
    // Fallback: circle
    ctx.beginPath();
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

// Helper to draw humanoid enemies (skeleton, dark-knight, lich)
interface HumanoidStyle {
  skinColor: string;
  tunicColor: string;
  tunicLight: string;
  pantsColor: string;
  bootColor: string;
  headDraw: (ctx: CanvasRenderingContext2D) => void;
  weaponDraw?: (ctx: CanvasRenderingContext2D) => void;
}

function drawHumanoidEnemy(ctx: CanvasRenderingContext2D, e: Enemy, time: number, style: HumanoidStyle) {
  const bob = Math.sin(time * 8) * 1.5;
  const legSwing = Math.sin(time * 8) * 0.35;
  const armSwing = Math.sin(time * 8) * 0.25;
  const s = e.radius / 14; // scale factor based on enemy radius

  // Left leg
  ctx.save();
  ctx.translate(-3 * s, 8 * s);
  ctx.rotate(-legSwing);
  ctx.fillStyle = style.pantsColor;
  ctx.fillRect(-2.5 * s, 0, 5 * s, 10 * s);
  ctx.fillStyle = style.bootColor;
  roundRect(ctx, -3 * s, 8 * s, 6 * s, 4 * s, 1.5 * s);
  ctx.fill();
  ctx.restore();

  // Right leg
  ctx.save();
  ctx.translate(3 * s, 8 * s);
  ctx.rotate(legSwing);
  ctx.fillStyle = style.pantsColor;
  ctx.fillRect(-2.5 * s, 0, 5 * s, 10 * s);
  ctx.fillStyle = style.bootColor;
  roundRect(ctx, -3 * s, 8 * s, 6 * s, 4 * s, 1.5 * s);
  ctx.fill();
  ctx.restore();

  // Torso
  ctx.fillStyle = style.tunicColor;
  roundRect(ctx, -7 * s, -4 * s + bob, 14 * s, 14 * s, 3 * s);
  ctx.fill();
  ctx.fillStyle = style.tunicLight;
  ctx.fillRect(-1.5 * s, -2 * s + bob, 3 * s, 10 * s);

  // Left arm
  ctx.save();
  ctx.translate(-8 * s, -1 * s + bob);
  ctx.rotate(armSwing);
  ctx.fillStyle = style.tunicColor;
  roundRect(ctx, -3 * s, 0, 5 * s, 11 * s, 2 * s);
  ctx.fill();
  ctx.fillStyle = style.skinColor;
  ctx.beginPath();
  ctx.arc(-0.5 * s, 12 * s, 3 * s, 0, Math.PI * 2);
  ctx.fill();
  ctx.restore();

  // Right arm + weapon
  ctx.save();
  ctx.translate(8 * s, -1 * s + bob);
  ctx.rotate(-armSwing);
  ctx.fillStyle = style.tunicColor;
  roundRect(ctx, -2 * s, 0, 5 * s, 11 * s, 2 * s);
  ctx.fill();
  ctx.fillStyle = style.skinColor;
  ctx.beginPath();
  ctx.arc(0.5 * s, 12 * s, 3 * s, 0, Math.PI * 2);
  ctx.fill();
  if (style.weaponDraw) {
    ctx.save();
    ctx.translate(0.5 * s, 12 * s);
    ctx.scale(s, s);
    style.weaponDraw(ctx);
    ctx.restore();
  }
  ctx.restore();

  // Neck
  ctx.fillStyle = style.skinColor;
  ctx.fillRect(-2.5 * s, -8 * s + bob, 5 * s, 5 * s);

  // Head
  ctx.save();
  ctx.translate(0, -12 * s + bob);
  ctx.scale(s, s);
  style.headDraw(ctx);
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
