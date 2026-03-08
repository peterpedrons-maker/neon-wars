import { GameState, Player, Enemy, Projectile, Particle, PowerUp } from './types';
import { COLORS, ARENA_W, ARENA_H, WARRIOR_ATTACK_RANGE } from './constants';

// Cached textures
let floorPattern: CanvasPattern | null = null;
let floorPatternCanvas: HTMLCanvasElement | null = null;
let torchFlicker = 0;

function createFloorPattern(ctx: CanvasRenderingContext2D): CanvasPattern | null {
  if (floorPattern && floorPatternCanvas) return floorPattern;
  const tile = document.createElement('canvas');
  tile.width = 50;
  tile.height = 50;
  const tc = tile.getContext('2d')!;
  
  // Stone tile base
  tc.fillStyle = '#2a1810';
  tc.fillRect(0, 0, 50, 50);
  
  // Stone texture noise
  for (let i = 0; i < 40; i++) {
    const x = Math.random() * 50;
    const y = Math.random() * 50;
    const s = Math.random() * 3 + 1;
    const a = Math.random() * 0.08;
    tc.fillStyle = Math.random() > 0.5 ? `rgba(255,220,180,${a})` : `rgba(0,0,0,${a * 1.5})`;
    tc.fillRect(x, y, s, s);
  }
  
  // Tile grooves
  tc.strokeStyle = 'rgba(0,0,0,0.25)';
  tc.lineWidth = 1.5;
  tc.strokeRect(1, 1, 48, 48);
  tc.strokeStyle = 'rgba(255,220,180,0.05)';
  tc.lineWidth = 0.5;
  tc.strokeRect(2, 2, 46, 46);
  
  // Occasional cracks
  if (Math.random() > 0.6) {
    tc.strokeStyle = 'rgba(0,0,0,0.15)';
    tc.lineWidth = 0.5;
    tc.beginPath();
    tc.moveTo(10 + Math.random() * 15, 10 + Math.random() * 10);
    tc.lineTo(25 + Math.random() * 10, 25 + Math.random() * 10);
    tc.lineTo(30 + Math.random() * 15, 35 + Math.random() * 10);
    tc.stroke();
  }
  
  floorPatternCanvas = tile;
  floorPattern = ctx.createPattern(tile, 'repeat');
  return floorPattern;
}

export function renderGame(ctx: CanvasRenderingContext2D, state: GameState, canvasW: number, canvasH: number) {
  const scale = Math.min(canvasW / ARENA_W, canvasH / ARENA_H);
  const offsetX = (canvasW - ARENA_W * scale) / 2;
  const offsetY = (canvasH - ARENA_H * scale) / 2;
  const time = Date.now() * 0.001;
  torchFlicker = Math.sin(time * 5) * 0.1 + Math.sin(time * 7.3) * 0.05 + Math.sin(time * 13.1) * 0.03;

  ctx.save();

  // Screen shake
  if (state.shakeTimer > 0) {
    const sx = (Math.random() - 0.5) * state.shakeIntensity;
    const sy = (Math.random() - 0.5) * state.shakeIntensity;
    ctx.translate(sx, sy);
  }

  // Clear with dark vignette bg
  ctx.fillStyle = '#0a0604';
  ctx.fillRect(0, 0, canvasW, canvasH);

  ctx.translate(offsetX, offsetY);
  ctx.scale(scale, scale);

  // Arena floor with stone pattern
  const pattern = createFloorPattern(ctx);
  if (pattern) {
    ctx.fillStyle = pattern;
  } else {
    ctx.fillStyle = COLORS.arena;
  }
  ctx.fillRect(0, 0, ARENA_W, ARENA_H);

  // Ambient floor glow around player
  if (state.player.alive) {
    const classGlow = state.player.class === 'mage' ? 'rgba(155,89,182,0.06)'
      : state.player.class === 'archer' ? 'rgba(39,174,96,0.06)' : 'rgba(230,126,34,0.06)';
    const grad = ctx.createRadialGradient(state.player.pos.x, state.player.pos.y, 20, state.player.pos.x, state.player.pos.y, 200);
    grad.addColorStop(0, classGlow);
    grad.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, ARENA_W, ARENA_H);
  }

  // Torch lights at corners
  drawTorchLight(ctx, 30, 30, time);
  drawTorchLight(ctx, ARENA_W - 30, 30, time + 1);
  drawTorchLight(ctx, 30, ARENA_H - 30, time + 2);
  drawTorchLight(ctx, ARENA_W - 30, ARENA_H - 30, time + 3);

  // Wall / border
  drawStoneWall(ctx, time);

  // Power-ups
  state.powerUps.forEach(pu => { if (pu.alive) drawPowerUp(ctx, pu, time); });

  // Projectiles
  state.projectiles.forEach(p => { if (p.alive) drawProjectile(ctx, p, time); });

  // Enemy shadows
  state.enemies.forEach(e => { if (e.alive) drawShadow(ctx, e.pos.x, e.pos.y, e.radius); });

  // Player shadow
  if (state.player.alive) drawShadow(ctx, state.player.pos.x, state.player.pos.y, state.player.radius);

  // Enemies
  state.enemies.forEach(e => { if (e.alive) drawEnemy(ctx, e, time); });

  // Player
  if (state.player.alive) drawPlayer(ctx, state.player, time);

  // Particles (on top)
  state.particles.forEach(p => drawParticle(ctx, p));

  // Vignette overlay
  drawVignette(ctx);

  ctx.restore();
}

function drawShadow(ctx: CanvasRenderingContext2D, x: number, y: number, radius: number) {
  ctx.save();
  ctx.beginPath();
  ctx.ellipse(x, y + radius * 0.6, radius * 0.9, radius * 0.35, 0, 0, Math.PI * 2);
  ctx.fillStyle = 'rgba(0,0,0,0.35)';
  ctx.fill();
  ctx.restore();
}

function drawTorchLight(ctx: CanvasRenderingContext2D, x: number, y: number, time: number) {
  const flicker = 0.85 + Math.sin(time * 6) * 0.08 + Math.sin(time * 9.7) * 0.05;
  const r = 120 * flicker;
  const grad = ctx.createRadialGradient(x, y, 5, x, y, r);
  grad.addColorStop(0, `rgba(255,160,50,${0.15 * flicker})`);
  grad.addColorStop(0.4, `rgba(255,100,20,${0.06 * flicker})`);
  grad.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.fillStyle = grad;
  ctx.fillRect(x - r, y - r, r * 2, r * 2);

  // Torch flame
  ctx.save();
  ctx.translate(x, y);
  const fSize = 4 + Math.sin(time * 10) * 1.5;
  const grad2 = ctx.createRadialGradient(0, -2, 1, 0, -2, fSize);
  grad2.addColorStop(0, 'rgba(255,230,100,0.9)');
  grad2.addColorStop(0.5, 'rgba(255,120,20,0.6)');
  grad2.addColorStop(1, 'rgba(255,60,0,0)');
  ctx.fillStyle = grad2;
  ctx.beginPath();
  ctx.arc(0, -2, fSize, 0, Math.PI * 2);
  ctx.fill();
  ctx.restore();
}

function drawStoneWall(ctx: CanvasRenderingContext2D, time: number) {
  const wallW = 8;
  
  // Outer dark border
  ctx.strokeStyle = '#1a0e08';
  ctx.lineWidth = wallW + 4;
  ctx.strokeRect(-2, -2, ARENA_W + 4, ARENA_H + 4);

  // Main wall gradient
  const wallGrad = ctx.createLinearGradient(0, 0, 0, ARENA_H);
  wallGrad.addColorStop(0, '#6a4a30');
  wallGrad.addColorStop(0.5, '#5a3a28');
  wallGrad.addColorStop(1, '#4a2a18');
  ctx.strokeStyle = wallGrad;
  ctx.lineWidth = wallW;
  ctx.strokeRect(wallW / 2, wallW / 2, ARENA_W - wallW, ARENA_H - wallW);

  // Inner highlight
  ctx.strokeStyle = 'rgba(160,120,80,0.3)';
  ctx.lineWidth = 1;
  ctx.strokeRect(wallW + 1, wallW + 1, ARENA_W - wallW * 2 - 2, ARENA_H - wallW * 2 - 2);

  // Stone block marks on wall
  ctx.strokeStyle = 'rgba(0,0,0,0.3)';
  ctx.lineWidth = 1;
  for (let x = 0; x < ARENA_W; x += 40) {
    ctx.beginPath();
    ctx.moveTo(x, 0); ctx.lineTo(x, wallW);
    ctx.moveTo(x, ARENA_H - wallW); ctx.lineTo(x, ARENA_H);
    ctx.stroke();
  }
  for (let y = 0; y < ARENA_H; y += 40) {
    ctx.beginPath();
    ctx.moveTo(0, y); ctx.lineTo(wallW, y);
    ctx.moveTo(ARENA_W - wallW, y); ctx.lineTo(ARENA_W, y);
    ctx.stroke();
  }
}

function drawVignette(ctx: CanvasRenderingContext2D) {
  const grad = ctx.createRadialGradient(ARENA_W / 2, ARENA_H / 2, ARENA_W * 0.25, ARENA_W / 2, ARENA_H / 2, ARENA_W * 0.7);
  grad.addColorStop(0, 'rgba(0,0,0,0)');
  grad.addColorStop(1, 'rgba(0,0,0,0.4)');
  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, ARENA_W, ARENA_H);
}

function drawPlayer(ctx: CanvasRenderingContext2D, p: Player, time: number) {
  ctx.save();
  ctx.translate(p.pos.x, p.pos.y);

  const glowColor = p.class === 'mage' ? COLORS.mageGlow
    : p.class === 'archer' ? COLORS.archerGlow : COLORS.warriorGlow;
  const baseColor = p.class === 'mage' ? COLORS.mage
    : p.class === 'archer' ? COLORS.archer : COLORS.warrior;

  // Shield effect
  if (p.shieldTimer > 0) {
    ctx.beginPath();
    ctx.arc(0, 0, p.radius + 10, 0, Math.PI * 2);
    const shieldAlpha = 0.3 + Math.sin(time * 4) * 0.15;
    const shGrad = ctx.createRadialGradient(0, 0, p.radius, 0, 0, p.radius + 10);
    shGrad.addColorStop(0, `rgba(52,152,219,${shieldAlpha})`);
    shGrad.addColorStop(1, `rgba(52,152,219,0)`);
    ctx.fillStyle = shGrad;
    ctx.fill();
    ctx.beginPath();
    ctx.arc(0, 0, p.radius + 9, 0, Math.PI * 2);
    ctx.strokeStyle = `rgba(100,200,255,${0.4 + Math.sin(time * 6) * 0.2})`;
    ctx.lineWidth = 1.5;
    ctx.setLineDash([4, 4]);
    ctx.lineDashOffset = time * 30;
    ctx.stroke();
    ctx.setLineDash([]);
  }

  // Invincibility flash
  if (p.invincibleTimer > 0 && Math.floor(Date.now() / 80) % 2 === 0) {
    ctx.globalAlpha = 0.5;
  }

  // Outer glow
  ctx.shadowColor = glowColor;
  ctx.shadowBlur = 20 + Math.sin(time * 3) * 5;

  // Body with gradient
  const bodyGrad = ctx.createRadialGradient(-3, -3, 2, 0, 0, p.radius);
  bodyGrad.addColorStop(0, lightenColor(baseColor, 40));
  bodyGrad.addColorStop(0.7, baseColor);
  bodyGrad.addColorStop(1, darkenColor(baseColor, 30));
  ctx.beginPath();
  ctx.arc(0, 0, p.radius, 0, Math.PI * 2);
  ctx.fillStyle = bodyGrad;
  ctx.fill();

  // Inner ring
  ctx.beginPath();
  ctx.arc(0, 0, p.radius * 0.7, 0, Math.PI * 2);
  ctx.strokeStyle = `rgba(255,255,255,0.15)`;
  ctx.lineWidth = 1;
  ctx.stroke();

  // Direction indicator (weapon)
  ctx.save();
  ctx.rotate(p.angle);
  if (p.class === 'warrior') {
    // Sword shape
    ctx.beginPath();
    ctx.moveTo(p.radius * 1.6, 0);
    ctx.lineTo(p.radius * 0.8, -3);
    ctx.lineTo(p.radius * 0.6, -5);
    ctx.lineTo(p.radius * 0.6, 5);
    ctx.lineTo(p.radius * 0.8, 3);
    ctx.closePath();
    ctx.fillStyle = '#c0c0c0';
    ctx.fill();
    ctx.strokeStyle = '#888';
    ctx.lineWidth = 0.5;
    ctx.stroke();
    // Guard
    ctx.fillStyle = '#8B4513';
    ctx.fillRect(p.radius * 0.5, -6, 4, 12);
  } else if (p.class === 'archer') {
    // Arrow
    ctx.beginPath();
    ctx.moveTo(p.radius * 1.8, 0);
    ctx.lineTo(p.radius * 1.4, -2);
    ctx.lineTo(p.radius * 0.6, 0);
    ctx.lineTo(p.radius * 1.4, 2);
    ctx.closePath();
    ctx.fillStyle = '#8B4513';
    ctx.fill();
    // Bow arc
    ctx.beginPath();
    ctx.arc(0, 0, p.radius * 1.1, -0.6, 0.6);
    ctx.strokeStyle = '#8B4513';
    ctx.lineWidth = 2;
    ctx.stroke();
  } else {
    // Staff orb
    ctx.beginPath();
    ctx.arc(p.radius * 1.3, 0, 4, 0, Math.PI * 2);
    const orbGrad = ctx.createRadialGradient(p.radius * 1.3, 0, 1, p.radius * 1.3, 0, 4);
    orbGrad.addColorStop(0, '#fff');
    orbGrad.addColorStop(0.5, glowColor);
    orbGrad.addColorStop(1, baseColor);
    ctx.fillStyle = orbGrad;
    ctx.fill();
    // Staff
    ctx.beginPath();
    ctx.moveTo(p.radius * 1.1, 0);
    ctx.lineTo(p.radius * 0.3, 0);
    ctx.strokeStyle = '#8B4513';
    ctx.lineWidth = 2;
    ctx.stroke();
  }
  ctx.restore();

  // Warrior melee range indicator
  if (p.class === 'warrior' && p.attackTimer > p.attackCooldown * 0.5) {
    ctx.beginPath();
    ctx.arc(0, 0, WARRIOR_ATTACK_RANGE, p.angle - 0.8, p.angle + 0.8);
    const slashGrad = ctx.createRadialGradient(0, 0, p.radius, 0, 0, WARRIOR_ATTACK_RANGE);
    slashGrad.addColorStop(0, 'rgba(230,126,34,0.5)');
    slashGrad.addColorStop(1, 'rgba(230,126,34,0)');
    ctx.strokeStyle = slashGrad;
    ctx.lineWidth = 4;
    ctx.stroke();
    // Slash arc fill
    ctx.beginPath();
    ctx.moveTo(0, 0);
    ctx.arc(0, 0, WARRIOR_ATTACK_RANGE, p.angle - 0.8, p.angle + 0.8);
    ctx.closePath();
    ctx.fillStyle = 'rgba(255,160,50,0.12)';
    ctx.fill();
  }

  ctx.shadowBlur = 0;
  ctx.globalAlpha = 1;

  // Class icon (smaller, subtle)
  ctx.font = `${p.radius * 0.7}px serif`;
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  const icon = p.class === 'mage' ? '🔮' : p.class === 'archer' ? '🏹' : '⚔️';
  ctx.fillText(icon, 0, 0);

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
    const auraR = e.radius + 15 + Math.sin(time * 3) * 5;
    const aGrad = ctx.createRadialGradient(0, 0, e.radius, 0, 0, auraR);
    aGrad.addColorStop(0, hexToRgba(color, 0.3));
    aGrad.addColorStop(0.5, hexToRgba(color, 0.1));
    aGrad.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = aGrad;
    ctx.beginPath();
    ctx.arc(0, 0, auraR, 0, Math.PI * 2);
    ctx.fill();

    // Rotating runes
    ctx.save();
    ctx.rotate(time * 0.5);
    ctx.strokeStyle = hexToRgba(color, 0.2);
    ctx.lineWidth = 1;
    for (let i = 0; i < 6; i++) {
      const a = (i / 6) * Math.PI * 2;
      const rx = Math.cos(a) * (e.radius + 8);
      const ry = Math.sin(a) * (e.radius + 8);
      ctx.beginPath();
      ctx.arc(rx, ry, 2, 0, Math.PI * 2);
      ctx.stroke();
    }
    ctx.restore();
  }

  // Entity body with gradient
  ctx.beginPath();
  if (e.type === 'slime') {
    // Jelly blob
    const wobble = Math.sin(time * 4) * 2;
    ctx.ellipse(0, 2 + wobble * 0.3, e.radius + wobble * 0.5, e.radius * 0.75 - wobble * 0.3, 0, 0, Math.PI * 2);
    const slimeGrad = ctx.createRadialGradient(-3, -2, 2, 0, 0, e.radius);
    slimeGrad.addColorStop(0, lightenColor(color, 50));
    slimeGrad.addColorStop(0.5, color);
    slimeGrad.addColorStop(1, darkenColor(color, 30));
    ctx.fillStyle = slimeGrad;
    ctx.fill();
    // Shine
    ctx.beginPath();
    ctx.ellipse(-e.radius * 0.3, -e.radius * 0.2, e.radius * 0.25, e.radius * 0.15, -0.3, 0, Math.PI * 2);
    ctx.fillStyle = 'rgba(255,255,255,0.3)';
    ctx.fill();
  } else if (e.type === 'bat') {
    // Animated wings
    const wingFlap = Math.sin(time * 12) * 0.4;
    ctx.save();
    // Left wing
    ctx.beginPath();
    ctx.moveTo(0, 0);
    ctx.quadraticCurveTo(-e.radius * 1.2, -e.radius * (1 + wingFlap), -e.radius * 1.5, e.radius * 0.2);
    ctx.quadraticCurveTo(-e.radius * 0.8, e.radius * 0.3, 0, 0);
    ctx.fillStyle = color;
    ctx.fill();
    // Right wing
    ctx.beginPath();
    ctx.moveTo(0, 0);
    ctx.quadraticCurveTo(e.radius * 1.2, -e.radius * (1 + wingFlap), e.radius * 1.5, e.radius * 0.2);
    ctx.quadraticCurveTo(e.radius * 0.8, e.radius * 0.3, 0, 0);
    ctx.fill();
    // Body
    ctx.beginPath();
    ctx.ellipse(0, 0, e.radius * 0.5, e.radius * 0.7, 0, 0, Math.PI * 2);
    ctx.fillStyle = darkenColor(color, 20);
    ctx.fill();
    // Eyes
    ctx.fillStyle = '#ff4444';
    ctx.beginPath();
    ctx.arc(-3, -2, 1.5, 0, Math.PI * 2);
    ctx.arc(3, -2, 1.5, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
  } else if (e.type === 'skeleton') {
    // Skeleton with bones look
    ctx.arc(0, 0, e.radius, 0, Math.PI * 2);
    const skelGrad = ctx.createRadialGradient(-2, -2, 1, 0, 0, e.radius);
    skelGrad.addColorStop(0, '#f0ede8');
    skelGrad.addColorStop(0.6, color);
    skelGrad.addColorStop(1, '#8a8578');
    ctx.fillStyle = skelGrad;
    ctx.fill();
    // Eye sockets
    ctx.fillStyle = '#2a1810';
    ctx.beginPath();
    ctx.ellipse(-3, -2, 2, 2.5, 0, 0, Math.PI * 2);
    ctx.ellipse(3, -2, 2, 2.5, 0, 0, Math.PI * 2);
    ctx.fill();
    // Red eye glow
    ctx.fillStyle = 'rgba(255,50,50,0.6)';
    ctx.beginPath();
    ctx.arc(-3, -2, 1, 0, Math.PI * 2);
    ctx.arc(3, -2, 1, 0, Math.PI * 2);
    ctx.fill();
  } else if (e.type === 'dark-knight') {
    ctx.arc(0, 0, e.radius, 0, Math.PI * 2);
    const dkGrad = ctx.createRadialGradient(-3, -3, 2, 0, 0, e.radius);
    dkGrad.addColorStop(0, '#4a5568');
    dkGrad.addColorStop(0.5, color);
    dkGrad.addColorStop(1, '#1a202c');
    ctx.fillStyle = dkGrad;
    ctx.fill();
    // Armor highlight
    ctx.beginPath();
    ctx.arc(0, 0, e.radius * 0.8, -Math.PI * 0.3, Math.PI * 0.3);
    ctx.strokeStyle = 'rgba(200,200,220,0.2)';
    ctx.lineWidth = 2;
    ctx.stroke();
    // Visor slit
    ctx.fillStyle = '#e74c3c';
    ctx.fillRect(-5, -2, 10, 2);
  } else if (e.type === 'dragon') {
    ctx.arc(0, 0, e.radius, 0, Math.PI * 2);
    const drGrad = ctx.createRadialGradient(-5, -5, 3, 0, 0, e.radius);
    drGrad.addColorStop(0, '#ff6b6b');
    drGrad.addColorStop(0.5, color);
    drGrad.addColorStop(1, '#8b0000');
    ctx.fillStyle = drGrad;
    ctx.fill();
    // Scale pattern
    ctx.strokeStyle = 'rgba(255,200,100,0.15)';
    ctx.lineWidth = 0.5;
    for (let i = 0; i < 5; i++) {
      ctx.beginPath();
      ctx.arc(0, 0, e.radius * (0.3 + i * 0.15), 0, Math.PI * 2);
      ctx.stroke();
    }
    // Fire breath glow
    const fbGrad = ctx.createRadialGradient(e.radius * 0.5, 0, 2, e.radius * 0.5, 0, 15);
    fbGrad.addColorStop(0, 'rgba(255,200,50,0.4)');
    fbGrad.addColorStop(1, 'rgba(255,100,0,0)');
    ctx.fillStyle = fbGrad;
    ctx.beginPath();
    ctx.arc(e.radius * 0.5, 0, 15, 0, Math.PI * 2);
    ctx.fill();
  } else if (e.type === 'lich') {
    ctx.arc(0, 0, e.radius, 0, Math.PI * 2);
    const lGrad = ctx.createRadialGradient(-3, -5, 2, 0, 0, e.radius);
    lGrad.addColorStop(0, '#a855f7');
    lGrad.addColorStop(0.5, color);
    lGrad.addColorStop(1, '#2d1a4e');
    ctx.fillStyle = lGrad;
    ctx.fill();
    // Soul particles orbiting
    for (let i = 0; i < 4; i++) {
      const ang = time * 2 + (i / 4) * Math.PI * 2;
      const ox = Math.cos(ang) * (e.radius + 5);
      const oy = Math.sin(ang) * (e.radius + 5);
      ctx.beginPath();
      ctx.arc(ox, oy, 2, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(168,85,247,${0.4 + Math.sin(time * 4 + i) * 0.2})`;
      ctx.fill();
    }
  } else if (e.type === 'golem') {
    // Rocky body
    ctx.arc(0, 0, e.radius, 0, Math.PI * 2);
    const gGrad = ctx.createRadialGradient(-5, -5, 3, 0, 0, e.radius);
    gGrad.addColorStop(0, '#a0a0a0');
    gGrad.addColorStop(0.5, color);
    gGrad.addColorStop(1, '#4a4a4a');
    ctx.fillStyle = gGrad;
    ctx.fill();
    // Crack lines
    ctx.strokeStyle = 'rgba(255,150,50,0.3)';
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(-5, -e.radius * 0.5);
    ctx.lineTo(0, 0);
    ctx.lineTo(5, e.radius * 0.5);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(e.radius * 0.3, -e.radius * 0.4);
    ctx.lineTo(0, 3);
    ctx.lineTo(-e.radius * 0.3, e.radius * 0.3);
    ctx.stroke();
    // Glowing core
    const cGrad = ctx.createRadialGradient(0, 0, 2, 0, 0, e.radius * 0.4);
    cGrad.addColorStop(0, 'rgba(255,150,50,0.4)');
    cGrad.addColorStop(1, 'rgba(255,100,0,0)');
    ctx.fillStyle = cGrad;
    ctx.beginPath();
    ctx.arc(0, 0, e.radius * 0.4, 0, Math.PI * 2);
    ctx.fill();
  } else {
    ctx.arc(0, 0, e.radius, 0, Math.PI * 2);
    ctx.fillStyle = color;
    ctx.fill();
  }

  // Enemy icon (only for simpler enemies without detailed art)
  ctx.shadowBlur = 0;
  if (e.isBoss) {
    const iconMap: Record<string, string> = {
      dragon: '🐉',
      lich: '👻',
      golem: '🪨',
    };
    ctx.font = `${Math.min(e.radius * 0.6, 20)}px serif`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(iconMap[e.type] || '👹', 0, 0);
  }

  // HP bar for tough enemies
  if (e.hp < e.maxHp && (e.isBoss || e.maxHp > 30)) {
    const barW = e.radius * 2.2;
    const barH = e.isBoss ? 6 : 4;
    const barY = -e.radius - 10;
    // Background
    ctx.fillStyle = 'rgba(0,0,0,0.6)';
    roundRect(ctx, -barW / 2 - 1, barY - 1, barW + 2, barH + 2, 2);
    ctx.fill();
    // Health
    const hpPct = e.hp / e.maxHp;
    const hpColor = hpPct > 0.5 ? '#e74c3c' : hpPct > 0.25 ? '#e67e22' : '#c0392b';
    const hpGrad = ctx.createLinearGradient(-barW / 2, 0, barW / 2, 0);
    hpGrad.addColorStop(0, lightenColor(hpColor, 20));
    hpGrad.addColorStop(1, hpColor);
    ctx.fillStyle = hpGrad;
    roundRect(ctx, -barW / 2, barY, barW * hpPct, barH, 2);
    ctx.fill();
  }

  ctx.restore();
}

function drawProjectile(ctx: CanvasRenderingContext2D, p: Projectile, time: number) {
  ctx.save();
  ctx.translate(p.pos.x, p.pos.y);
  
  // Trail glow
  const trailGrad = ctx.createRadialGradient(0, 0, 1, 0, 0, p.radius * 3);
  trailGrad.addColorStop(0, hexToRgba(p.color, 0.4));
  trailGrad.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.fillStyle = trailGrad;
  ctx.beginPath();
  ctx.arc(0, 0, p.radius * 3, 0, Math.PI * 2);
  ctx.fill();

  // Core
  ctx.shadowColor = p.color;
  ctx.shadowBlur = 12;
  const coreGrad = ctx.createRadialGradient(0, 0, 0, 0, 0, p.radius);
  coreGrad.addColorStop(0, '#fff');
  coreGrad.addColorStop(0.4, lightenColor(p.color, 30));
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
  
  // Glow
  const glowR = p.size * alpha * 2;
  const pGrad = ctx.createRadialGradient(p.pos.x, p.pos.y, 0, p.pos.x, p.pos.y, glowR);
  pGrad.addColorStop(0, p.color);
  pGrad.addColorStop(0.5, hexToRgba(p.color, 0.3 * alpha));
  pGrad.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.fillStyle = pGrad;
  ctx.beginPath();
  ctx.arc(p.pos.x, p.pos.y, glowR, 0, Math.PI * 2);
  ctx.fill();

  // Core
  ctx.fillStyle = '#fff';
  ctx.beginPath();
  ctx.arc(p.pos.x, p.pos.y, p.size * alpha * 0.4, 0, Math.PI * 2);
  ctx.fill();
  ctx.restore();
}

function drawPowerUp(ctx: CanvasRenderingContext2D, pu: PowerUp, time: number) {
  ctx.save();
  ctx.translate(pu.pos.x, pu.pos.y);

  const pulse = 1 + Math.sin(time * 4) * 0.12;
  const bob = Math.sin(time * 3) * 3;
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
  ctx.translate(0, pu.radius + 5 - bob);
  ctx.beginPath();
  ctx.ellipse(0, 0, pu.radius * 1.2, 4, 0, 0, Math.PI * 2);
  ctx.fillStyle = hexToRgba(color, 0.15);
  ctx.fill();
  ctx.restore();

  // Outer glow
  const outerGrad = ctx.createRadialGradient(0, 0, pu.radius * 0.5, 0, 0, pu.radius * 2);
  outerGrad.addColorStop(0, hexToRgba(color, 0.2));
  outerGrad.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.fillStyle = outerGrad;
  ctx.beginPath();
  ctx.arc(0, 0, pu.radius * 2, 0, Math.PI * 2);
  ctx.fill();

  // Rotating sparkles
  for (let i = 0; i < 4; i++) {
    const a = time * 2 + (i / 4) * Math.PI * 2;
    const sr = pu.radius * 1.3 * pulse;
    const sx = Math.cos(a) * sr;
    const sy = Math.sin(a) * sr;
    ctx.fillStyle = `rgba(255,255,255,${0.3 + Math.sin(time * 5 + i) * 0.15})`;
    ctx.beginPath();
    ctx.arc(sx, sy, 1.5, 0, Math.PI * 2);
    ctx.fill();
  }

  // Main orb
  ctx.shadowColor = color;
  ctx.shadowBlur = 15;
  const orbGrad = ctx.createRadialGradient(-2, -2, 1, 0, 0, pu.radius * pulse);
  orbGrad.addColorStop(0, '#fff');
  orbGrad.addColorStop(0.3, lightenColor(color, 30));
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
  ctx.font = '12px serif';
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
  return Math.min(canvasW / ARENA_W, canvasH / ARENA_H);
}

export function getOffset(canvasW: number, canvasH: number) {
  const scale = getScale(canvasW, canvasH);
  return {
    x: (canvasW - ARENA_W * scale) / 2,
    y: (canvasH - ARENA_H * scale) / 2,
  };
}
