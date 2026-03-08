import { GameState, Player, Enemy, Projectile, Particle, PowerUp } from './types';
import { COLORS, ARENA_W, ARENA_H, WARRIOR_ATTACK_RANGE } from './constants';

export function renderGame(ctx: CanvasRenderingContext2D, state: GameState, canvasW: number, canvasH: number) {
  const scale = Math.min(canvasW / ARENA_W, canvasH / ARENA_H);
  const offsetX = (canvasW - ARENA_W * scale) / 2;
  const offsetY = (canvasH - ARENA_H * scale) / 2;

  ctx.save();

  // Screen shake
  if (state.shakeTimer > 0) {
    const sx = (Math.random() - 0.5) * state.shakeIntensity;
    const sy = (Math.random() - 0.5) * state.shakeIntensity;
    ctx.translate(sx, sy);
  }

  // Clear
  ctx.fillStyle = COLORS.bg;
  ctx.fillRect(0, 0, canvasW, canvasH);

  ctx.translate(offsetX, offsetY);
  ctx.scale(scale, scale);

  // Arena floor
  ctx.fillStyle = COLORS.arena;
  ctx.fillRect(0, 0, ARENA_W, ARENA_H);

  // Grid
  ctx.strokeStyle = COLORS.grid;
  ctx.lineWidth = 1;
  for (let x = 0; x <= ARENA_W; x += 50) {
    ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, ARENA_H); ctx.stroke();
  }
  for (let y = 0; y <= ARENA_H; y += 50) {
    ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(ARENA_W, y); ctx.stroke();
  }

  // Arena border (stone wall)
  ctx.strokeStyle = COLORS.arenaBorder;
  ctx.lineWidth = 6;
  ctx.strokeRect(3, 3, ARENA_W - 6, ARENA_H - 6);
  ctx.strokeStyle = COLORS.arenaBorderLight;
  ctx.lineWidth = 2;
  ctx.strokeRect(6, 6, ARENA_W - 12, ARENA_H - 12);

  // Power-ups
  state.powerUps.forEach(pu => { if (pu.alive) drawPowerUp(ctx, pu); });

  // Projectiles
  state.projectiles.forEach(p => { if (p.alive) drawProjectile(ctx, p); });

  // Enemies
  state.enemies.forEach(e => { if (e.alive) drawEnemy(ctx, e); });

  // Player
  if (state.player.alive) drawPlayer(ctx, state.player);

  // Particles (on top)
  state.particles.forEach(p => drawParticle(ctx, p));

  ctx.restore();
}

function drawPlayer(ctx: CanvasRenderingContext2D, p: Player) {
  ctx.save();
  ctx.translate(p.pos.x, p.pos.y);

  // Glow
  const glowColor = p.class === 'mage' ? COLORS.mageGlow
    : p.class === 'archer' ? COLORS.archerGlow : COLORS.warriorGlow;
  const baseColor = p.class === 'mage' ? COLORS.mage
    : p.class === 'archer' ? COLORS.archer : COLORS.warrior;

  // Shield effect
  if (p.shieldTimer > 0) {
    ctx.beginPath();
    ctx.arc(0, 0, p.radius + 8, 0, Math.PI * 2);
    ctx.strokeStyle = `rgba(52, 152, 219, ${0.5 + Math.sin(Date.now() * 0.01) * 0.3})`;
    ctx.lineWidth = 2;
    ctx.stroke();
  }

  // Invincibility flash
  if (p.invincibleTimer > 0 && Math.floor(Date.now() / 80) % 2 === 0) {
    ctx.globalAlpha = 0.5;
  }

  // Glow
  ctx.shadowColor = glowColor;
  ctx.shadowBlur = 15;

  // Body
  ctx.beginPath();
  ctx.arc(0, 0, p.radius, 0, Math.PI * 2);
  ctx.fillStyle = baseColor;
  ctx.fill();

  // Direction indicator
  ctx.beginPath();
  ctx.moveTo(Math.cos(p.angle) * p.radius * 1.5, Math.sin(p.angle) * p.radius * 1.5);
  ctx.lineTo(Math.cos(p.angle + 2.5) * p.radius * 0.5, Math.sin(p.angle + 2.5) * p.radius * 0.5);
  ctx.lineTo(Math.cos(p.angle - 2.5) * p.radius * 0.5, Math.sin(p.angle - 2.5) * p.radius * 0.5);
  ctx.closePath();
  ctx.fillStyle = glowColor;
  ctx.fill();

  // Warrior melee range indicator
  if (p.class === 'warrior' && p.attackTimer > p.attackCooldown * 0.5) {
    ctx.beginPath();
    ctx.arc(0, 0, WARRIOR_ATTACK_RANGE, p.angle - 0.8, p.angle + 0.8);
    ctx.strokeStyle = `rgba(230, 126, 34, 0.6)`;
    ctx.lineWidth = 3;
    ctx.stroke();
  }

  ctx.shadowBlur = 0;
  ctx.globalAlpha = 1;

  // Class icon
  ctx.font = `${p.radius}px serif`;
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  const icon = p.class === 'mage' ? '🔮' : p.class === 'archer' ? '🏹' : '⚔️';
  ctx.fillText(icon, 0, 0);

  ctx.restore();
}

function drawEnemy(ctx: CanvasRenderingContext2D, e: Enemy) {
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

  // Boss glow
  if (e.isBoss) {
    ctx.shadowColor = color;
    ctx.shadowBlur = 20;
  }

  ctx.beginPath();
  if (e.type === 'slime') {
    // Blob shape
    ctx.ellipse(0, 2, e.radius, e.radius * 0.75, 0, 0, Math.PI * 2);
  } else if (e.type === 'bat') {
    // Wings
    ctx.moveTo(0, -e.radius * 0.5);
    ctx.lineTo(-e.radius * 1.5, -e.radius);
    ctx.lineTo(-e.radius * 0.5, 0);
    ctx.lineTo(-e.radius * 1.2, e.radius * 0.5);
    ctx.lineTo(0, e.radius * 0.3);
    ctx.lineTo(e.radius * 1.2, e.radius * 0.5);
    ctx.lineTo(e.radius * 0.5, 0);
    ctx.lineTo(e.radius * 1.5, -e.radius);
    ctx.closePath();
  } else {
    ctx.arc(0, 0, e.radius, 0, Math.PI * 2);
  }
  ctx.fillStyle = color;
  ctx.fill();

  // Enemy icon
  const iconMap: Record<string, string> = {
    skeleton: '💀',
    slime: '🟢',
    bat: '🦇',
    'dark-knight': '🗡️',
    dragon: '🐉',
    lich: '👻',
    golem: '🪨',
  };

  ctx.shadowBlur = 0;
  ctx.font = `${Math.min(e.radius, 20)}px serif`;
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText(iconMap[e.type] || '👹', 0, 0);

  // HP bar for tough enemies
  if (e.hp < e.maxHp && (e.isBoss || e.maxHp > 30)) {
    const barW = e.radius * 2;
    const barH = 4;
    const barY = -e.radius - 8;
    ctx.fillStyle = COLORS.healthBg;
    ctx.fillRect(-barW / 2, barY, barW, barH);
    ctx.fillStyle = COLORS.health;
    ctx.fillRect(-barW / 2, barY, barW * (e.hp / e.maxHp), barH);
  }

  ctx.restore();
}

function drawProjectile(ctx: CanvasRenderingContext2D, p: Projectile) {
  ctx.save();
  ctx.translate(p.pos.x, p.pos.y);
  ctx.shadowColor = p.color;
  ctx.shadowBlur = 8;
  ctx.beginPath();
  ctx.arc(0, 0, p.radius, 0, Math.PI * 2);
  ctx.fillStyle = p.color;
  ctx.fill();
  ctx.restore();
}

function drawParticle(ctx: CanvasRenderingContext2D, p: Particle) {
  const alpha = p.lifetime / p.maxLifetime;
  ctx.save();
  ctx.globalAlpha = alpha;
  ctx.fillStyle = p.color;
  ctx.beginPath();
  ctx.arc(p.pos.x, p.pos.y, p.size * alpha, 0, Math.PI * 2);
  ctx.fill();
  ctx.restore();
}

function drawPowerUp(ctx: CanvasRenderingContext2D, pu: PowerUp) {
  ctx.save();
  ctx.translate(pu.pos.x, pu.pos.y);

  const pulse = 1 + Math.sin(Date.now() * 0.005) * 0.15;

  const colorMap: Record<string, string> = {
    speed: COLORS.speedPU,
    'triple-shot': COLORS.triplePU,
    shield: COLORS.shieldPU,
    heal: COLORS.healPU,
  };

  ctx.shadowColor = colorMap[pu.type] || '#fff';
  ctx.shadowBlur = 12;

  ctx.beginPath();
  ctx.arc(0, 0, pu.radius * pulse, 0, Math.PI * 2);
  ctx.fillStyle = colorMap[pu.type] || '#fff';
  ctx.globalAlpha = 0.7;
  ctx.fill();

  ctx.globalAlpha = 1;
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
