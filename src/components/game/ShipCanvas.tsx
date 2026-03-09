import React, { useRef, useEffect } from 'react';
import { ShipType } from '../../game/types';
import { COLORS } from '../../game/constants';

interface ShipCanvasProps {
  shipType: ShipType;
  width?: number;
  height?: number;
  className?: string;
}

function hexToRgba(hex: string, a: number): string {
  if (!hex || hex[0] !== '#') return `rgba(255,255,255,${a})`;
  const r = parseInt(hex.slice(1, 3), 16) || 255;
  const g = parseInt(hex.slice(3, 5), 16) || 255;
  const b = parseInt(hex.slice(5, 7), 16) || 255;
  return `rgba(${r},${g},${b},${a})`;
}

const ShipCanvas: React.FC<ShipCanvasProps> = ({ shipType, width = 100, height = 72, className = '' }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animRef = useRef<number>(0);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    const dpr = 2;
    canvas.width = width * dpr;
    canvas.height = height * dpr;
    ctx.scale(dpr, dpr);

    const color = COLORS[shipType] || '#fff';
    const glow = COLORS[shipType + 'Glow'] || '#fff';

    function loop() {
      const time = Date.now() * 0.001;
      ctx!.clearRect(0, 0, width, height);
      const cx = width / 2, cy = height / 2;
      const r = Math.min(width, height) * 0.22; // ship radius

      // Background glow
      const bgGrad = ctx!.createRadialGradient(cx, cy, 3, cx, cy, Math.max(width, height) * 0.5);
      bgGrad.addColorStop(0, hexToRgba(color, 0.12));
      bgGrad.addColorStop(1, 'rgba(0,0,0,0)');
      ctx!.fillStyle = bgGrad;
      ctx!.fillRect(0, 0, width, height);

      ctx!.save();
      ctx!.translate(cx, cy);

      // Exhaust
      const thrustPulse = 0.5 + Math.sin(time * 18) * 0.3;
      const thrustLen = r * 1.2 + Math.sin(time * 15) * r * 0.2;
      ctx!.fillStyle = hexToRgba(color, thrustPulse * 0.35);
      ctx!.beginPath();
      ctx!.moveTo(-r * 0.4, -3); ctx!.lineTo(-r - thrustLen, 0); ctx!.lineTo(-r * 0.4, 3);
      ctx!.closePath(); ctx!.fill();
      ctx!.fillStyle = hexToRgba('#fff', thrustPulse * 0.5);
      ctx!.beginPath();
      ctx!.moveTo(-r * 0.35, -1.5); ctx!.lineTo(-r - thrustLen * 0.7, 0); ctx!.lineTo(-r * 0.35, 1.5);
      ctx!.closePath(); ctx!.fill();

      ctx!.shadowColor = color;
      ctx!.shadowBlur = 12;

      // === SHIP BODY - replicated from renderer.ts drawPlayer ===
      drawShipBody(ctx!, shipType, r, color, glow, time);

      // Cockpit glow
      const cockpitX = r * 0.4;
      const cockpitR = 2.5;
      const cockpitGrad = ctx!.createRadialGradient(cockpitX, 0, 0, cockpitX, 0, cockpitR + 3);
      cockpitGrad.addColorStop(0, '#ffffff');
      cockpitGrad.addColorStop(0.3, glow);
      cockpitGrad.addColorStop(1, hexToRgba(color, 0));
      ctx!.fillStyle = cockpitGrad;
      ctx!.beginPath(); ctx!.arc(cockpitX, 0, cockpitR + 1, 0, Math.PI * 2); ctx!.fill();

      ctx!.shadowBlur = 0;
      ctx!.restore();
      animRef.current = requestAnimationFrame(loop);
    }
    loop();
    return () => cancelAnimationFrame(animRef.current);
  }, [shipType, width, height]);

  return <canvas ref={canvasRef} style={{ width, height }} className={`pointer-events-none ${className}`} />;
};

function drawShipBody(ctx: CanvasRenderingContext2D, shipType: ShipType, r: number, color: string, glow: string, time: number) {
  if (shipType === 'phantom') {
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
    ctx.fillStyle = hexToRgba(color, 0.15); ctx.fill();
    ctx.strokeStyle = color; ctx.lineWidth = 1.5; ctx.stroke();
    // Wing energy lines
    const ep = 0.4 + Math.sin(time * 4) * 0.3;
    ctx.strokeStyle = hexToRgba(glow, ep); ctx.lineWidth = 0.8;
    ctx.beginPath();
    ctx.moveTo(r * 0.3, -r * 0.2); ctx.lineTo(-r * 0.4, -r * 0.9);
    ctx.moveTo(r * 0.3, r * 0.2); ctx.lineTo(-r * 0.4, r * 0.9);
    ctx.stroke();
    // Wing tip lights
    const wp = 0.5 + Math.sin(time * 4) * 0.3;
    ctx.fillStyle = hexToRgba(glow, wp);
    ctx.beginPath(); ctx.arc(-r * 0.3, -r * 1.15, 1.5 + wp, 0, Math.PI * 2); ctx.fill();
    ctx.beginPath(); ctx.arc(-r * 0.3, r * 1.15, 1.5 + wp, 0, Math.PI * 2); ctx.fill();

  } else if (shipType === 'interceptor') {
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
    ctx.fillStyle = hexToRgba(color, 0.12); ctx.fill();
    ctx.strokeStyle = color; ctx.lineWidth = 1.2; ctx.stroke();
    // Twin boom nacelles
    for (const side of [-1, 1]) {
      ctx.beginPath();
      ctx.moveTo(r * 0.4, side * r * 0.35);
      ctx.lineTo(-r * 0.1, side * r * 0.7);
      ctx.lineTo(-r * 0.6, side * r * 0.65);
      ctx.lineTo(-r * 0.4, side * r * 0.35);
      ctx.closePath();
      ctx.fillStyle = hexToRgba(color, 0.1); ctx.fill();
      ctx.strokeStyle = color; ctx.lineWidth = 1; ctx.stroke();
      const np = 0.4 + Math.sin(time * 6 + side) * 0.2;
      ctx.fillStyle = hexToRgba(glow, np);
      ctx.beginPath(); ctx.arc(-r * 0.3, side * r * 0.55, 1.5, 0, Math.PI * 2); ctx.fill();
    }
    // Canards
    ctx.strokeStyle = hexToRgba(glow, 0.6); ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(r * 1.0, -r * 0.1); ctx.lineTo(r * 0.5, -r * 0.5);
    ctx.moveTo(r * 1.0, r * 0.1); ctx.lineTo(r * 0.5, r * 0.5);
    ctx.stroke();
    // Nose
    ctx.fillStyle = hexToRgba('#fff', 0.6 + Math.sin(time * 8) * 0.3);
    ctx.beginPath(); ctx.arc(r * 1.8, 0, 1.2, 0, Math.PI * 2); ctx.fill();

  } else if (shipType === 'titan') {
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
    ctx.fillStyle = hexToRgba(color, 0.18); ctx.fill();
    ctx.strokeStyle = color; ctx.lineWidth = 2; ctx.stroke();
    // Armor lines
    ctx.strokeStyle = hexToRgba(glow, 0.25); ctx.lineWidth = 0.8;
    ctx.beginPath();
    ctx.moveTo(r * 0.4, -r * 0.35); ctx.lineTo(-r * 0.7, -r * 0.35);
    ctx.moveTo(r * 0.4, r * 0.35); ctx.lineTo(-r * 0.7, r * 0.35);
    ctx.stroke();
    // Gun barrels
    for (const side of [-1, 1]) {
      ctx.fillStyle = hexToRgba(color, 0.4);
      ctx.fillRect(r * 0.8, side * r * 0.25 - 1.5, r * 0.5, 3);
      ctx.strokeStyle = color; ctx.lineWidth = 0.8;
      ctx.strokeRect(r * 0.8, side * r * 0.25 - 1.5, r * 0.5, 3);
    }
    // Wing tip nodes
    const ap = 0.3 + Math.sin(time * 2) * 0.15;
    ctx.fillStyle = hexToRgba(glow, ap);
    ctx.beginPath(); ctx.arc(-r * 0.3, -r * 1.0, 2, 0, Math.PI * 2); ctx.fill();
    ctx.beginPath(); ctx.arc(-r * 0.3, r * 1.0, 2, 0, Math.PI * 2); ctx.fill();

  } else if (shipType === 'spectre') {
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
    ctx.fillStyle = hexToRgba(color, 0.12); ctx.fill();
    ctx.strokeStyle = color; ctx.lineWidth = 1.2; ctx.stroke();
    // Phase dashes
    ctx.strokeStyle = hexToRgba(glow, 0.4 + Math.sin(time * 8) * 0.3);
    ctx.lineWidth = 0.7;
    ctx.setLineDash([4, 5]);
    ctx.beginPath();
    ctx.moveTo(r * 1.5, -r * 0.15); ctx.lineTo(-r * 0.3, -r * 0.65);
    ctx.moveTo(r * 1.5, r * 0.15); ctx.lineTo(-r * 0.3, r * 0.65);
    ctx.stroke();
    ctx.setLineDash([]);
    // Ghost trail
    for (let i = 1; i <= 3; i++) {
      ctx.fillStyle = hexToRgba(color, 0.08 * (4 - i));
      ctx.beginPath(); ctx.arc(-i * 6, 0, r * 0.4, 0, Math.PI * 2); ctx.fill();
    }
    // Eye
    const gp = 0.5 + Math.sin(time * 6) * 0.4;
    ctx.fillStyle = hexToRgba('#fff', gp);
    ctx.beginPath(); ctx.arc(r * 0.3, 0, 2, 0, Math.PI * 2); ctx.fill();
    ctx.globalAlpha = 1;

  } else if (shipType === 'valkyrie') {
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
    ctx.fillStyle = hexToRgba(color, 0.15); ctx.fill();
    ctx.strokeStyle = color; ctx.lineWidth = 1.5; ctx.stroke();
    // Spear energy
    const sp = 0.5 + Math.sin(time * 5) * 0.3;
    ctx.strokeStyle = hexToRgba(glow, sp); ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(-r * 0.2, -r * 1.4); ctx.lineTo(r * 0.3, -r * 0.2);
    ctx.moveTo(-r * 0.2, r * 1.4); ctx.lineTo(r * 0.3, r * 0.2);
    ctx.stroke();
    // Wing tip gems
    for (const sy of [-1, 1]) {
      ctx.fillStyle = hexToRgba('#fff', sp);
      ctx.beginPath(); ctx.arc(-r * 0.2, sy * r * 1.35, 2, 0, Math.PI * 2); ctx.fill();
    }
    // Dual emitters
    ctx.fillStyle = hexToRgba(color, 0.6 + Math.sin(time * 10) * 0.3);
    ctx.beginPath(); ctx.arc(r * 1.6, -r * 0.08, 1.5, 0, Math.PI * 2); ctx.fill();
    ctx.beginPath(); ctx.arc(r * 1.6, r * 0.08, 1.5, 0, Math.PI * 2); ctx.fill();

  } else if (shipType === 'juggernaut') {
    // === JUGGERNAUT: Heavy armored hex fortress with rotating shield plates ===
    const sides = 6;
    // Outer rotating armor plates
    ctx.save(); ctx.rotate(time * 0.3);
    for (let i = 0; i < sides; i++) {
      const a = (i / sides) * Math.PI * 2;
      const plateAlpha = 0.15 + Math.sin(time * 2 + i) * 0.08;
      ctx.fillStyle = hexToRgba(color, plateAlpha);
      ctx.beginPath();
      const px = Math.cos(a) * r * 1.5;
      const py = Math.sin(a) * r * 1.5;
      ctx.save(); ctx.translate(px, py); ctx.rotate(a);
      ctx.fillRect(-r * 0.25, -r * 0.08, r * 0.5, r * 0.16);
      ctx.strokeStyle = hexToRgba(glow, 0.3); ctx.lineWidth = 0.5;
      ctx.strokeRect(-r * 0.25, -r * 0.08, r * 0.5, r * 0.16);
      ctx.restore();
    }
    ctx.restore();
    // Main body hex
    ctx.beginPath();
    for (let i = 0; i <= sides; i++) {
      const a = (i / sides) * Math.PI * 2 - Math.PI / 6;
      const px = Math.cos(a) * r * 1.3;
      const py = Math.sin(a) * r * 1.3 * 0.85;
      if (i === 0) ctx.moveTo(px, py); else ctx.lineTo(px, py);
    }
    ctx.closePath();
    ctx.fillStyle = hexToRgba(color, 0.2); ctx.fill();
    ctx.strokeStyle = color; ctx.lineWidth = 2.5; ctx.stroke();
    // Inner hex with energy pulse
    const innerPulse = 0.3 + Math.sin(time * 3) * 0.15;
    ctx.strokeStyle = hexToRgba(glow, innerPulse); ctx.lineWidth = 1;
    ctx.beginPath();
    for (let i = 0; i <= sides; i++) {
      const a = (i / sides) * Math.PI * 2 - Math.PI / 6;
      const px = Math.cos(a) * r * 0.8;
      const py = Math.sin(a) * r * 0.8 * 0.85;
      if (i === 0) ctx.moveTo(px, py); else ctx.lineTo(px, py);
    }
    ctx.closePath(); ctx.stroke();
    // Cross beams
    ctx.strokeStyle = hexToRgba(glow, 0.15); ctx.lineWidth = 0.6;
    ctx.beginPath();
    ctx.moveTo(-r * 0.8, 0); ctx.lineTo(r * 0.8, 0);
    ctx.moveTo(0, -r * 0.7); ctx.lineTo(0, r * 0.7);
    ctx.stroke();
    // Triple guns with heat glow
    for (const side of [-1, 0, 1]) {
      ctx.fillStyle = hexToRgba(color, 0.5);
      ctx.fillRect(r * 0.9, side * r * 0.35 - 1.5, r * 0.6, 3);
      ctx.strokeStyle = color; ctx.lineWidth = 0.8;
      ctx.strokeRect(r * 0.9, side * r * 0.35 - 1.5, r * 0.6, 3);
      // Muzzle glow
      const mz = 0.3 + Math.sin(time * 6 + side * 2) * 0.2;
      ctx.fillStyle = hexToRgba('#fff', mz);
      ctx.beginPath(); ctx.arc(r * 1.5, side * r * 0.35, 1.5, 0, Math.PI * 2); ctx.fill();
    }
    // Core reactor with spinning energy
    const cp = 0.4 + Math.sin(time * 2) * 0.2;
    const cg = ctx.createRadialGradient(0, 0, 1, 0, 0, r * 0.5);
    cg.addColorStop(0, hexToRgba('#fff', cp));
    cg.addColorStop(0.3, hexToRgba(color, cp * 0.6));
    cg.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = cg;
    ctx.beginPath(); ctx.arc(0, 0, r * 0.5, 0, Math.PI * 2); ctx.fill();
    // Vertex energy nodes
    for (let i = 0; i < sides; i++) {
      const a = (i / sides) * Math.PI * 2 - Math.PI / 6;
      const nx = Math.cos(a) * r * 1.25;
      const ny = Math.sin(a) * r * 1.25 * 0.85;
      const np = 0.3 + Math.sin(time * 3 + i) * 0.15;
      ctx.fillStyle = hexToRgba(glow, np);
      ctx.beginPath(); ctx.arc(nx, ny, 2, 0, Math.PI * 2); ctx.fill();
      const ng = ctx.createRadialGradient(nx, ny, 0, nx, ny, 5);
      ng.addColorStop(0, hexToRgba(glow, np * 0.4));
      ng.addColorStop(1, 'rgba(0,0,0,0)');
      ctx.fillStyle = ng;
      ctx.beginPath(); ctx.arc(nx, ny, 5, 0, Math.PI * 2); ctx.fill();
    }

  } else if (shipType === 'wraith') {
    // === WRAITH: Ghostly phase ship with spectral wings and afterimages ===
    const phase = 0.6 + Math.sin(time * 6) * 0.2;
    ctx.globalAlpha = phase;
    // Spectral wing extensions
    for (const sy of [-1, 1]) {
      ctx.fillStyle = hexToRgba(color, 0.06);
      ctx.beginPath();
      ctx.moveTo(r * 0.2, sy * r * 0.3);
      ctx.quadraticCurveTo(-r * 0.3, sy * r * 1.2, -r * 0.8, sy * r * 0.8);
      ctx.quadraticCurveTo(-r * 0.5, sy * r * 0.4, r * 0.2, sy * r * 0.3);
      ctx.fill();
      ctx.strokeStyle = hexToRgba(color, 0.15); ctx.lineWidth = 0.5;
      ctx.stroke();
    }
    // Main body
    ctx.beginPath();
    ctx.moveTo(r * 1.8, 0);
    ctx.bezierCurveTo(r * 1.0, -r * 0.6, -r * 0.2, -r * 0.8, -r * 0.6, -r * 0.5);
    ctx.lineTo(-r * 0.7, 0);
    ctx.lineTo(-r * 0.6, r * 0.5);
    ctx.bezierCurveTo(-r * 0.2, r * 0.8, r * 1.0, r * 0.6, r * 1.8, 0);
    ctx.closePath();
    ctx.fillStyle = hexToRgba(color, 0.1); ctx.fill();
    ctx.setLineDash([5, 4]);
    ctx.strokeStyle = color; ctx.lineWidth = 1.5; ctx.stroke();
    ctx.setLineDash([]);
    // Ghost trail copies with fade
    for (let i = 1; i <= 4; i++) {
      const ta = 0.06 * (5 - i);
      ctx.fillStyle = hexToRgba(color, ta);
      ctx.beginPath();
      ctx.moveTo(r * 1.8 - i * 7, 0);
      ctx.bezierCurveTo(r - i * 7, -r * 0.4, -r * 0.1 - i * 3, -r * 0.5, -r * 0.5 - i * 3, 0);
      ctx.bezierCurveTo(-r * 0.1 - i * 3, r * 0.5, r - i * 7, r * 0.4, r * 1.8 - i * 7, 0);
      ctx.closePath(); ctx.fill();
    }
    // Core eye with pulsing iris
    const eyePulse = 0.5 + Math.sin(time * 7) * 0.4;
    const eyeGrad = ctx.createRadialGradient(r * 0.4, 0, 0, r * 0.4, 0, r * 0.25);
    eyeGrad.addColorStop(0, hexToRgba('#fff', eyePulse));
    eyeGrad.addColorStop(0.4, hexToRgba(color, eyePulse * 0.6));
    eyeGrad.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = eyeGrad;
    ctx.beginPath(); ctx.arc(r * 0.4, 0, r * 0.25, 0, Math.PI * 2); ctx.fill();
    ctx.fillStyle = hexToRgba('#fff', eyePulse * 0.8);
    ctx.beginPath(); ctx.arc(r * 0.4, 0, 2, 0, Math.PI * 2); ctx.fill();
    // Spectral particles
    for (let i = 0; i < 5; i++) {
      const pa = time * 1.5 + (i / 5) * Math.PI * 2;
      const px = Math.cos(pa) * r * 1.0 + (Math.random() - 0.5) * 2;
      const py = Math.sin(pa) * r * 0.6;
      ctx.fillStyle = hexToRgba(color, 0.2 + Math.sin(time * 4 + i) * 0.15);
      ctx.beginPath(); ctx.arc(px, py, 1, 0, Math.PI * 2); ctx.fill();
    }
    ctx.globalAlpha = 1;

  } else if (shipType === 'sentinel') {
    // === SENTINEL: Shield-bearing fortress with layered defense arcs ===
    // Outer defense ring
    ctx.strokeStyle = hexToRgba(glow, 0.12); ctx.lineWidth = 0.5;
    ctx.beginPath(); ctx.arc(r * 0.3, 0, r * 1.4, -1.2, 1.2); ctx.stroke();
    // Main body
    ctx.beginPath();
    ctx.moveTo(r * 1.2, 0);
    ctx.lineTo(r * 0.4, -r * 0.5);
    ctx.lineTo(-r * 0.3, -r * 0.7);
    ctx.lineTo(-r * 0.8, -r * 0.5);
    ctx.lineTo(-r * 0.8, r * 0.5);
    ctx.lineTo(-r * 0.3, r * 0.7);
    ctx.lineTo(r * 0.4, r * 0.5);
    ctx.closePath();
    ctx.fillStyle = hexToRgba(color, 0.18); ctx.fill();
    ctx.strokeStyle = color; ctx.lineWidth = 2; ctx.stroke();
    // Armor plating detail
    ctx.strokeStyle = hexToRgba(glow, 0.15); ctx.lineWidth = 0.5;
    ctx.beginPath();
    ctx.moveTo(r * 0.2, -r * 0.4); ctx.lineTo(-r * 0.6, -r * 0.4);
    ctx.moveTo(r * 0.2, r * 0.4); ctx.lineTo(-r * 0.6, r * 0.4);
    ctx.moveTo(-r * 0.1, -r * 0.55); ctx.lineTo(-r * 0.1, r * 0.55);
    ctx.stroke();
    // Triple shield arcs with energy
    const shP = 0.4 + Math.sin(time * 3) * 0.2;
    for (let i = 0; i < 3; i++) {
      const arcAlpha = shP * (1 - i * 0.25);
      const arcR = r * (0.8 + i * 0.2);
      const arcWidth = 2.5 - i * 0.5;
      ctx.strokeStyle = hexToRgba(i === 0 ? '#fff' : glow, arcAlpha); ctx.lineWidth = arcWidth;
      ctx.beginPath(); ctx.arc(r * 0.5, 0, arcR, -0.8 + i * 0.1, 0.8 - i * 0.1); ctx.stroke();
    }
    // Shield node dots
    for (const sy of [-1, 1]) {
      const nodeA = 0.8 * sy;
      const nx = r * 0.5 + Math.cos(nodeA) * r * 0.8;
      const ny = Math.sin(nodeA) * r * 0.8;
      ctx.fillStyle = hexToRgba('#fff', shP);
      ctx.beginPath(); ctx.arc(nx, ny, 1.5, 0, Math.PI * 2); ctx.fill();
    }
    // Inner reactor with spinning ring
    ctx.save(); ctx.rotate(time * 1.5);
    ctx.strokeStyle = hexToRgba(color, 0.3); ctx.lineWidth = 0.8;
    ctx.beginPath(); ctx.ellipse(-r * 0.1, 0, r * 0.25, r * 0.15, 0, 0, Math.PI * 2); ctx.stroke();
    ctx.restore();
    const sGrad = ctx.createRadialGradient(-r * 0.1, 0, 0, -r * 0.1, 0, r * 0.35);
    sGrad.addColorStop(0, hexToRgba('#fff', 0.5));
    sGrad.addColorStop(0.5, hexToRgba(color, 0.2));
    sGrad.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = sGrad;
    ctx.beginPath(); ctx.arc(-r * 0.1, 0, r * 0.35, 0, Math.PI * 2); ctx.fill();

  } else if (shipType === 'tempest') {
    // === TEMPEST: Wind/lightning ship with electric arcs and speed trails ===
    // Electric field around ship
    for (let i = 0; i < 6; i++) {
      const arcA = time * 8 + i * 1.2;
      const arcR = r * 1.0 + Math.sin(time * 10 + i) * r * 0.3;
      const ax1 = Math.cos(arcA) * arcR;
      const ay1 = Math.sin(arcA) * arcR * 0.5;
      const ax2 = Math.cos(arcA + 0.5) * arcR * 0.8;
      const ay2 = Math.sin(arcA + 0.5) * arcR * 0.5;
      ctx.strokeStyle = hexToRgba('#fff', 0.15 + Math.sin(time * 15 + i) * 0.1);
      ctx.lineWidth = 0.5;
      ctx.beginPath(); ctx.moveTo(ax1, ay1); ctx.lineTo(ax2, ay2); ctx.stroke();
    }
    // Main body
    ctx.beginPath();
    ctx.moveTo(r * 2.2, 0);
    ctx.lineTo(r * 0.5, -r * 0.3);
    ctx.lineTo(-r * 0.1, -r * 0.5);
    ctx.lineTo(-r * 0.5, -r * 0.3);
    ctx.lineTo(-r * 0.4, 0);
    ctx.lineTo(-r * 0.5, r * 0.3);
    ctx.lineTo(-r * 0.1, r * 0.5);
    ctx.lineTo(r * 0.5, r * 0.3);
    ctx.closePath();
    ctx.fillStyle = hexToRgba(color, 0.12); ctx.fill();
    ctx.strokeStyle = color; ctx.lineWidth = 1.2; ctx.stroke();
    // Internal energy channels
    ctx.strokeStyle = hexToRgba(glow, 0.2); ctx.lineWidth = 0.4;
    ctx.beginPath();
    ctx.moveTo(r * 1.5, 0); ctx.lineTo(-r * 0.3, 0);
    ctx.moveTo(r * 0.3, -r * 0.25); ctx.lineTo(-r * 0.3, -r * 0.4);
    ctx.moveTo(r * 0.3, r * 0.25); ctx.lineTo(-r * 0.3, r * 0.4);
    ctx.stroke();
    // Lightning arcs along body - more complex zigzag
    const arcPulse = 0.3 + Math.sin(time * 12) * 0.3;
    ctx.strokeStyle = hexToRgba('#fff', arcPulse); ctx.lineWidth = 0.8;
    for (const sy of [-1, 1]) {
      ctx.beginPath();
      ctx.moveTo(r * 1.8, sy * r * 0.05);
      const segments = 5;
      for (let i = 1; i <= segments; i++) {
        const fx = r * 1.8 - (i / segments) * r * 2.2;
        const fy = sy * (r * 0.1 + Math.sin(time * 20 + i * 3 + sy) * r * 0.15);
        ctx.lineTo(fx, fy);
      }
      ctx.stroke();
    }
    // Speed afterimage
    for (let i = 1; i <= 3; i++) {
      ctx.fillStyle = hexToRgba(color, 0.06 * (4 - i));
      ctx.beginPath(); ctx.ellipse(-i * 6, 0, r * 0.4, r * 0.15, 0, 0, Math.PI * 2); ctx.fill();
    }
    // Nose charge
    const noseP = 0.5 + Math.sin(time * 10) * 0.3;
    ctx.fillStyle = hexToRgba('#fff', noseP);
    ctx.beginPath(); ctx.arc(r * 2.0, 0, 1.5, 0, Math.PI * 2); ctx.fill();
    const noseG = ctx.createRadialGradient(r * 2.0, 0, 0, r * 2.0, 0, r * 0.3);
    noseG.addColorStop(0, hexToRgba(color, noseP * 0.4));
    noseG.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = noseG;
    ctx.beginPath(); ctx.arc(r * 2.0, 0, r * 0.3, 0, Math.PI * 2); ctx.fill();

  } else if (shipType === 'venom') {
    // === VENOM: Organic poison ship with tendrils and toxic aura ===
    // Toxic aura
    const auraP = 0.08 + Math.sin(time * 2) * 0.04;
    const auraG = ctx.createRadialGradient(0, 0, r * 0.5, 0, 0, r * 1.5);
    auraG.addColorStop(0, hexToRgba(color, auraP));
    auraG.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = auraG;
    ctx.beginPath(); ctx.arc(0, 0, r * 1.5, 0, Math.PI * 2); ctx.fill();
    // Main body - organic curves
    ctx.beginPath();
    ctx.moveTo(r * 1.6, 0);
    ctx.quadraticCurveTo(r * 0.8, -r * 0.5, 0, -r * 0.6);
    ctx.quadraticCurveTo(-r * 0.5, -r * 0.5, -r * 0.6, -r * 0.2);
    ctx.quadraticCurveTo(-r * 0.7, 0, -r * 0.6, r * 0.2);
    ctx.quadraticCurveTo(-r * 0.5, r * 0.5, 0, r * 0.6);
    ctx.quadraticCurveTo(r * 0.8, r * 0.5, r * 1.6, 0);
    ctx.closePath();
    ctx.fillStyle = hexToRgba(color, 0.15); ctx.fill();
    ctx.strokeStyle = color; ctx.lineWidth = 1.5; ctx.stroke();
    // Organic tendrils extending from body
    for (let i = 0; i < 6; i++) {
      const tAngle = (i / 6) * Math.PI * 2 + Math.sin(time * 2) * 0.2;
      const tLen = r * 0.8 + Math.sin(time * 3 + i * 1.5) * r * 0.3;
      const tx = Math.cos(tAngle) * tLen;
      const ty = Math.sin(tAngle) * tLen;
      const tAlpha = 0.2 + Math.sin(time * 4 + i) * 0.1;
      ctx.strokeStyle = hexToRgba(color, tAlpha); ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(Math.cos(tAngle) * r * 0.4, Math.sin(tAngle) * r * 0.4);
      ctx.quadraticCurveTo(
        Math.cos(tAngle + 0.3) * tLen * 0.6, Math.sin(tAngle + 0.3) * tLen * 0.6,
        tx, ty
      );
      ctx.stroke();
      // Tendril tip drip
      ctx.fillStyle = hexToRgba(color, tAlpha * 1.5);
      ctx.beginPath(); ctx.arc(tx, ty, 1.5, 0, Math.PI * 2); ctx.fill();
    }
    // Drip particles falling
    for (let i = 0; i < 5; i++) {
      const dy = ((time * 30 + i * 40) % (r * 2)) - r;
      const dx = -r * 0.4 + i * r * 0.2 + Math.sin(time * 2 + i) * 2;
      const dAlpha = 0.3 * (1 - Math.abs(dy) / r);
      if (dAlpha > 0) {
        ctx.fillStyle = hexToRgba(color, dAlpha);
        ctx.beginPath(); ctx.arc(dx, dy, 1, 0, Math.PI * 2); ctx.fill();
      }
    }
    // Compound eyes
    for (const ey of [-0.15, 0.1]) {
      ctx.fillStyle = hexToRgba('#fff', 0.6);
      ctx.beginPath(); ctx.arc(r * 0.4, ey * r, 2, 0, Math.PI * 2); ctx.fill();
      ctx.fillStyle = hexToRgba(color, 0.8);
      ctx.beginPath(); ctx.arc(r * 0.4, ey * r, 1, 0, Math.PI * 2); ctx.fill();
    }

  } else if (shipType === 'nova_ship') {
    // === NOVA: Pulsing star with expanding energy rings ===
    // Outer energy ring pulsing
    const ringP = (time * 2) % 1;
    ctx.strokeStyle = hexToRgba(color, (1 - ringP) * 0.2); ctx.lineWidth = 1.5;
    ctx.beginPath(); ctx.arc(0, 0, r * 0.6 + ringP * r * 1.2, 0, Math.PI * 2); ctx.stroke();
    const ringP2 = ((time * 2 + 0.5) % 1);
    ctx.strokeStyle = hexToRgba(glow, (1 - ringP2) * 0.15); ctx.lineWidth = 1;
    ctx.beginPath(); ctx.arc(0, 0, r * 0.6 + ringP2 * r * 1.2, 0, Math.PI * 2); ctx.stroke();
    // Star shape with rotation
    const starPulse = 1 + Math.sin(time * 4) * 0.06;
    ctx.save(); ctx.scale(starPulse, starPulse); ctx.rotate(time * 0.5);
    // Outer star rays (longer)
    ctx.beginPath();
    for (let i = 0; i < 12; i++) {
      const a = (i / 12) * Math.PI * 2;
      const outerR = i % 2 === 0 ? r * 1.5 : r * 0.7;
      if (i === 0) ctx.moveTo(Math.cos(a) * outerR, Math.sin(a) * outerR);
      else ctx.lineTo(Math.cos(a) * outerR, Math.sin(a) * outerR);
    }
    ctx.closePath();
    ctx.fillStyle = hexToRgba(color, 0.08); ctx.fill();
    ctx.strokeStyle = hexToRgba(color, 0.3); ctx.lineWidth = 0.5; ctx.stroke();
    // Inner star (main)
    ctx.beginPath();
    for (let i = 0; i < 8; i++) {
      const a = (i / 8) * Math.PI * 2;
      const outerR = i % 2 === 0 ? r * 1.2 : r * 0.5;
      if (i === 0) ctx.moveTo(Math.cos(a) * outerR, Math.sin(a) * outerR);
      else ctx.lineTo(Math.cos(a) * outerR, Math.sin(a) * outerR);
    }
    ctx.closePath();
    ctx.fillStyle = hexToRgba(color, 0.15); ctx.fill();
    ctx.strokeStyle = color; ctx.lineWidth = 1.5; ctx.stroke();
    ctx.restore();
    // Inner energy orb with layers
    const op = 0.5 + Math.sin(time * 5) * 0.3;
    const ng = ctx.createRadialGradient(0, 0, 0, 0, 0, r * 0.5);
    ng.addColorStop(0, hexToRgba('#fff', op));
    ng.addColorStop(0.3, hexToRgba(glow, op * 0.6));
    ng.addColorStop(0.6, hexToRgba(color, op * 0.3));
    ng.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = ng;
    ctx.beginPath(); ctx.arc(0, 0, r * 0.5, 0, Math.PI * 2); ctx.fill();
    // Orbiting energy dots
    for (let i = 0; i < 4; i++) {
      const oa = time * 3 + (i / 4) * Math.PI * 2;
      const ox = Math.cos(oa) * r * 0.9;
      const oy = Math.sin(oa) * r * 0.9;
      ctx.fillStyle = hexToRgba('#fff', 0.4 + Math.sin(time * 6 + i) * 0.2);
      ctx.beginPath(); ctx.arc(ox, oy, 1.5, 0, Math.PI * 2); ctx.fill();
    }

  } else if (shipType === 'chronos') {
    // === CHRONOS: Clockwork time ship with multiple rings and gears ===
    // Outer time ring
    ctx.strokeStyle = hexToRgba(color, 0.15); ctx.lineWidth = 1;
    ctx.beginPath(); ctx.arc(0, 0, r * 1.4, 0, Math.PI * 2); ctx.stroke();
    // Minute markers on outer ring
    for (let i = 0; i < 60; i++) {
      const a = (i / 60) * Math.PI * 2;
      const inner = i % 5 === 0 ? r * 1.25 : r * 1.3;
      ctx.strokeStyle = hexToRgba(glow, i % 5 === 0 ? 0.4 : 0.15); ctx.lineWidth = i % 5 === 0 ? 1 : 0.3;
      ctx.beginPath();
      ctx.moveTo(Math.cos(a) * inner, Math.sin(a) * inner);
      ctx.lineTo(Math.cos(a) * r * 1.38, Math.sin(a) * r * 1.38);
      ctx.stroke();
    }
    // Main body circle
    ctx.beginPath(); ctx.arc(0, 0, r * 1.1, 0, Math.PI * 2);
    ctx.fillStyle = hexToRgba(color, 0.12); ctx.fill();
    ctx.strokeStyle = color; ctx.lineWidth = 1.5; ctx.stroke();
    // Inner gear ring
    ctx.save(); ctx.rotate(-time * 1.5);
    ctx.beginPath();
    for (let i = 0; i < 16; i++) {
      const a = (i / 16) * Math.PI * 2;
      const gr = i % 2 === 0 ? r * 0.65 : r * 0.55;
      if (i === 0) ctx.moveTo(Math.cos(a) * gr, Math.sin(a) * gr);
      else ctx.lineTo(Math.cos(a) * gr, Math.sin(a) * gr);
    }
    ctx.closePath();
    ctx.strokeStyle = hexToRgba(glow, 0.3); ctx.lineWidth = 0.8; ctx.stroke();
    ctx.restore();
    // Clock hands - hour
    ctx.strokeStyle = hexToRgba('#fff', 0.7); ctx.lineWidth = 1.5;
    ctx.beginPath(); ctx.moveTo(0, 0);
    ctx.lineTo(Math.cos(time * 2) * r * 0.8, Math.sin(time * 2) * r * 0.8);
    ctx.stroke();
    // Minute hand
    ctx.strokeStyle = hexToRgba(glow, 0.5); ctx.lineWidth = 1;
    ctx.beginPath(); ctx.moveTo(0, 0);
    ctx.lineTo(Math.cos(time * 8) * r * 0.55, Math.sin(time * 8) * r * 0.55);
    ctx.stroke();
    // Second hand (fast)
    ctx.strokeStyle = hexToRgba(color, 0.3); ctx.lineWidth = 0.5;
    ctx.beginPath(); ctx.moveTo(0, 0);
    ctx.lineTo(Math.cos(time * 30) * r * 0.95, Math.sin(time * 30) * r * 0.95);
    ctx.stroke();
    // Center pivot
    ctx.fillStyle = hexToRgba('#fff', 0.7);
    ctx.beginPath(); ctx.arc(0, 0, 2, 0, Math.PI * 2); ctx.fill();
    // Hour markers
    for (let i = 0; i < 12; i++) {
      const a = (i / 12) * Math.PI * 2;
      const mp = 0.4 + Math.sin(time * 3 + i) * 0.2;
      ctx.fillStyle = hexToRgba(glow, mp);
      ctx.beginPath(); ctx.arc(Math.cos(a) * r * 0.95, Math.sin(a) * r * 0.95, 1.5, 0, Math.PI * 2); ctx.fill();
    }
    // Nose pointer
    ctx.fillStyle = hexToRgba(color, 0.8);
    ctx.beginPath();
    ctx.moveTo(r * 1.7, 0);
    ctx.lineTo(r * 1.1, -r * 0.2);
    ctx.lineTo(r * 1.1, r * 0.2);
    ctx.closePath(); ctx.fill();
    ctx.strokeStyle = color; ctx.lineWidth = 0.8; ctx.stroke();

  } else if (shipType === 'leviathan') {
    // === LEVIATHAN: Massive whale-like beast with segmented armor ===
    // Ambient dread aura
    const dreadG = ctx.createRadialGradient(0, 0, r * 0.5, 0, 0, r * 1.8);
    dreadG.addColorStop(0, hexToRgba(color, 0.08));
    dreadG.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = dreadG;
    ctx.beginPath(); ctx.arc(0, 0, r * 1.8, 0, Math.PI * 2); ctx.fill();
    // Main body
    ctx.beginPath();
    ctx.moveTo(r * 1.8, 0);
    ctx.bezierCurveTo(r * 1.2, -r * 0.7, r * 0.2, -r * 0.9, -r * 0.4, -r * 0.7);
    ctx.bezierCurveTo(-r * 0.8, -r * 0.5, -r * 1.0, -r * 0.2, -r * 1.0, 0);
    ctx.bezierCurveTo(-r * 1.0, r * 0.2, -r * 0.8, r * 0.5, -r * 0.4, r * 0.7);
    ctx.bezierCurveTo(r * 0.2, r * 0.9, r * 1.2, r * 0.7, r * 1.8, 0);
    ctx.closePath();
    ctx.fillStyle = hexToRgba(color, 0.2); ctx.fill();
    ctx.strokeStyle = color; ctx.lineWidth = 2.5; ctx.stroke();
    // Segmented armor ridges with energy
    for (let i = 0; i < 5; i++) {
      const rx = r * 0.8 - i * r * 0.35;
      const ridgeP = 0.15 + Math.sin(time * 2 + i * 0.8) * 0.08;
      ctx.strokeStyle = hexToRgba(glow, ridgeP); ctx.lineWidth = 1;
      ctx.beginPath(); ctx.ellipse(rx, 0, r * 0.12, r * 0.55, 0, 0, Math.PI * 2); ctx.stroke();
      // Ridge glow
      ctx.fillStyle = hexToRgba(color, ridgeP * 0.3);
      ctx.beginPath(); ctx.ellipse(rx, 0, r * 0.08, r * 0.4, 0, 0, Math.PI * 2); ctx.fill();
    }
    // Dorsal spine
    ctx.strokeStyle = hexToRgba(glow, 0.2); ctx.lineWidth = 0.8;
    ctx.beginPath();
    ctx.moveTo(r * 1.0, -r * 0.05);
    for (let i = 0; i < 8; i++) {
      const sx = r * 1.0 - i * r * 0.25;
      const sy = -r * 0.05 - Math.sin(time * 3 + i) * r * 0.05;
      ctx.lineTo(sx, sy);
    }
    ctx.stroke();
    // Maw with pulsing energy and teeth
    const mawPulse = 0.4 + Math.sin(time * 3) * 0.2;
    const mawG = ctx.createRadialGradient(r * 1.4, 0, 0, r * 1.4, 0, r * 0.4);
    mawG.addColorStop(0, hexToRgba('#fff', mawPulse));
    mawG.addColorStop(0.3, hexToRgba(color, mawPulse * 0.5));
    mawG.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = mawG;
    ctx.beginPath(); ctx.arc(r * 1.4, 0, r * 0.4, 0, Math.PI * 2); ctx.fill();
    // Teeth
    for (let i = -2; i <= 2; i++) {
      const ty = i * r * 0.12;
      ctx.fillStyle = hexToRgba('#fff', 0.5);
      ctx.beginPath();
      ctx.moveTo(r * 1.6, ty);
      ctx.lineTo(r * 1.8, ty * 0.5);
      ctx.lineTo(r * 1.6, ty * 0.3);
      ctx.closePath(); ctx.fill();
    }
    // Eyes
    for (const sy of [-1, 1]) {
      ctx.fillStyle = hexToRgba(color, 0.8);
      ctx.beginPath(); ctx.arc(r * 0.8, sy * r * 0.35, 2, 0, Math.PI * 2); ctx.fill();
      ctx.fillStyle = hexToRgba('#fff', 0.5);
      ctx.beginPath(); ctx.arc(r * 0.8, sy * r * 0.35, 1, 0, Math.PI * 2); ctx.fill();
    }

  } else if (shipType === 'raptor') {
    // === RAPTOR: Ultra-sleek needle with speed streaks and afterburners ===
    // Speed distortion lines behind
    const streakAlpha = 0.3;
    ctx.strokeStyle = hexToRgba(color, streakAlpha); ctx.lineWidth = 0.6;
    for (let i = -3; i <= 3; i++) {
      const len = 15 + Math.sin(time * 15 + i * 4) * 5;
      ctx.beginPath(); ctx.moveTo(-r * 0.5, i * 1.8); ctx.lineTo(-r - len, i * 2.2); ctx.stroke();
    }
    // Streamlined body
    ctx.beginPath();
    ctx.moveTo(r * 2.5, 0);
    ctx.lineTo(r * 0.8, -r * 0.15);
    ctx.lineTo(r * 0.3, -r * 0.25);
    ctx.lineTo(-r * 0.1, -r * 0.45);
    ctx.lineTo(-r * 0.4, -r * 0.35);
    ctx.lineTo(-r * 0.5, -r * 0.15);
    ctx.lineTo(-r * 0.5, r * 0.15);
    ctx.lineTo(-r * 0.4, r * 0.35);
    ctx.lineTo(-r * 0.1, r * 0.45);
    ctx.lineTo(r * 0.3, r * 0.25);
    ctx.lineTo(r * 0.8, r * 0.15);
    ctx.closePath();
    ctx.fillStyle = hexToRgba(color, 0.12); ctx.fill();
    ctx.strokeStyle = color; ctx.lineWidth = 1; ctx.stroke();
    // Speed-reactive energy channel along body
    const flowP = 0.3 + Math.sin(time * 8) * 0.2;
    ctx.strokeStyle = hexToRgba(glow, flowP); ctx.lineWidth = 0.6;
    ctx.beginPath();
    ctx.moveTo(r * 2.0, 0); ctx.lineTo(-r * 0.3, 0);
    ctx.stroke();
    // Wing detail
    ctx.strokeStyle = hexToRgba(glow, 0.3); ctx.lineWidth = 0.5;
    ctx.beginPath();
    ctx.moveTo(r * 0.1, -r * 0.3); ctx.lineTo(-r * 0.3, -r * 0.4);
    ctx.moveTo(r * 0.1, r * 0.3); ctx.lineTo(-r * 0.3, r * 0.4);
    ctx.stroke();
    // Dual afterburner nozzles
    for (const sy of [-1, 1]) {
      const nozP = 0.4 + Math.sin(time * 12 + sy * 2) * 0.2;
      ctx.fillStyle = hexToRgba(color, nozP);
      ctx.beginPath(); ctx.arc(-r * 0.4, sy * r * 0.25, 2, 0, Math.PI * 2); ctx.fill();
    }
    // Nose light with halo
    const nP = 0.7 + Math.sin(time * 10) * 0.2;
    ctx.fillStyle = hexToRgba('#fff', nP);
    ctx.beginPath(); ctx.arc(r * 2.3, 0, 1.5, 0, Math.PI * 2); ctx.fill();
    const nG = ctx.createRadialGradient(r * 2.3, 0, 0, r * 2.3, 0, r * 0.3);
    nG.addColorStop(0, hexToRgba(color, nP * 0.3));
    nG.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = nG;
    ctx.beginPath(); ctx.arc(r * 2.3, 0, r * 0.3, 0, Math.PI * 2); ctx.fill();
    // Speed afterimage
    for (let i = 1; i <= 4; i++) {
      ctx.fillStyle = hexToRgba(color, 0.04 * (5 - i));
      ctx.beginPath(); ctx.ellipse(-i * 5, 0, r * 0.3, r * 0.1, 0, 0, Math.PI * 2); ctx.fill();
    }

  } else if (shipType === 'oracle') {
    // === ORACLE: Mystical eye/diamond with orbiting runes and third eye ===
    // Outer mystical ring
    ctx.save(); ctx.rotate(time * 0.8);
    ctx.strokeStyle = hexToRgba(glow, 0.15); ctx.lineWidth = 0.5;
    ctx.beginPath(); ctx.arc(0, 0, r * 1.5, 0, Math.PI * 2); ctx.stroke();
    // Arcane symbols on ring
    for (let i = 0; i < 8; i++) {
      const a = (i / 8) * Math.PI * 2;
      const sx = Math.cos(a) * r * 1.5;
      const sy = Math.sin(a) * r * 1.5;
      ctx.fillStyle = hexToRgba(glow, 0.2 + Math.sin(time * 3 + i) * 0.15);
      ctx.beginPath(); ctx.arc(sx, sy, 1.5, 0, Math.PI * 2); ctx.fill();
      // Connecting lines to center
      ctx.strokeStyle = hexToRgba(glow, 0.05); ctx.lineWidth = 0.3;
      ctx.beginPath(); ctx.moveTo(sx, sy); ctx.lineTo(0, 0); ctx.stroke();
    }
    ctx.restore();
    // Main diamond body
    ctx.beginPath();
    ctx.moveTo(r * 1.6, 0);
    ctx.quadraticCurveTo(r * 0.5, -r * 0.7, -r * 0.3, -r * 0.5);
    ctx.quadraticCurveTo(-r * 0.6, 0, -r * 0.3, r * 0.5);
    ctx.quadraticCurveTo(r * 0.5, r * 0.7, r * 1.6, 0);
    ctx.closePath();
    ctx.fillStyle = hexToRgba(color, 0.12); ctx.fill();
    ctx.strokeStyle = color; ctx.lineWidth = 1.5; ctx.stroke();
    // Internal mystical pattern
    ctx.strokeStyle = hexToRgba(glow, 0.15); ctx.lineWidth = 0.4;
    ctx.beginPath();
    ctx.moveTo(r * 1.0, 0); ctx.lineTo(-r * 0.1, -r * 0.35);
    ctx.lineTo(-r * 0.1, r * 0.35); ctx.closePath(); ctx.stroke();
    // Third eye - multi-layered
    const es = 0.7 + Math.sin(time * 4) * 0.15;
    // Eye white
    ctx.fillStyle = hexToRgba('#fff', 0.5 * es);
    ctx.beginPath(); ctx.ellipse(r * 0.3, 0, r * 0.4, r * 0.22 * es, 0, 0, Math.PI * 2); ctx.fill();
    ctx.strokeStyle = hexToRgba(color, 0.4); ctx.lineWidth = 0.8;
    ctx.beginPath(); ctx.ellipse(r * 0.3, 0, r * 0.4, r * 0.22 * es, 0, 0, Math.PI * 2); ctx.stroke();
    // Iris
    ctx.fillStyle = hexToRgba(color, 0.8);
    ctx.beginPath(); ctx.arc(r * 0.3, 0, r * 0.15, 0, Math.PI * 2); ctx.fill();
    // Pupil
    ctx.fillStyle = '#000';
    ctx.beginPath(); ctx.arc(r * 0.3, 0, r * 0.07, 0, Math.PI * 2); ctx.fill();
    // Eye highlight
    ctx.fillStyle = hexToRgba('#fff', 0.8);
    ctx.beginPath(); ctx.arc(r * 0.35, -r * 0.04, r * 0.04, 0, Math.PI * 2); ctx.fill();
    // Orbiting runes (closer, more visible)
    for (let i = 0; i < 6; i++) {
      const a = time * 2 + (i / 6) * Math.PI * 2;
      const ox = Math.cos(a) * r * 1.1;
      const oy = Math.sin(a) * r * 1.1;
      const rp = 0.35 + Math.sin(time * 5 + i) * 0.2;
      ctx.fillStyle = hexToRgba(glow, rp);
      ctx.beginPath(); ctx.arc(ox, oy, 2, 0, Math.PI * 2); ctx.fill();
      const rg = ctx.createRadialGradient(ox, oy, 0, ox, oy, 4);
      rg.addColorStop(0, hexToRgba(glow, rp * 0.3));
      rg.addColorStop(1, 'rgba(0,0,0,0)');
      ctx.fillStyle = rg;
      ctx.beginPath(); ctx.arc(ox, oy, 4, 0, Math.PI * 2); ctx.fill();
    }

  } else if (shipType === 'pyro') {
    // === PYRO: Flame-wreathed ship with dynamic fire effects ===
    // Outer fire ring
    for (let i = 0; i < 12; i++) {
      const a = (i / 12) * Math.PI * 2 + time * 3;
      const flameR = r * 1.3 + Math.sin(time * 8 + i * 2) * r * 0.25;
      const fx = Math.cos(a) * flameR;
      const fy = Math.sin(a) * flameR;
      const fSize = 2.5 + Math.sin(time * 12 + i) * 1.5;
      const fAlpha = 0.25 + Math.sin(time * 6 + i) * 0.15;
      // Fire gradient blob
      const fGrad = ctx.createRadialGradient(fx, fy, 0, fx, fy, fSize * 2);
      fGrad.addColorStop(0, hexToRgba(i % 3 === 0 ? '#fff' : i % 3 === 1 ? '#ffaa00' : '#ff4400', fAlpha));
      fGrad.addColorStop(1, 'rgba(0,0,0,0)');
      ctx.fillStyle = fGrad;
      ctx.beginPath(); ctx.arc(fx, fy, fSize * 2, 0, Math.PI * 2); ctx.fill();
      ctx.fillStyle = hexToRgba(i % 2 === 0 ? '#ff4400' : '#ffaa00', fAlpha);
      ctx.beginPath(); ctx.arc(fx, fy, fSize, 0, Math.PI * 2); ctx.fill();
    }
    // Heat haze
    const hazeG = ctx.createRadialGradient(0, 0, r * 0.3, 0, 0, r * 1.5);
    hazeG.addColorStop(0, hexToRgba('#ff6600', 0.06));
    hazeG.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = hazeG;
    ctx.beginPath(); ctx.arc(0, 0, r * 1.5, 0, Math.PI * 2); ctx.fill();
    // Main body
    ctx.beginPath();
    ctx.moveTo(r * 1.6, 0);
    ctx.lineTo(r * 0.5, -r * 0.4);
    ctx.lineTo(-r * 0.3, -r * 0.5);
    ctx.lineTo(-r * 0.6, -r * 0.2);
    ctx.lineTo(-r * 0.6, r * 0.2);
    ctx.lineTo(-r * 0.3, r * 0.5);
    ctx.lineTo(r * 0.5, r * 0.4);
    ctx.closePath();
    ctx.fillStyle = hexToRgba(color, 0.15); ctx.fill();
    ctx.strokeStyle = color; ctx.lineWidth = 1.5; ctx.stroke();
    // Internal heat lines
    ctx.strokeStyle = hexToRgba('#ffaa00', 0.2); ctx.lineWidth = 0.5;
    ctx.beginPath();
    ctx.moveTo(r * 0.8, 0); ctx.lineTo(-r * 0.3, 0);
    ctx.moveTo(r * 0.3, -r * 0.3); ctx.lineTo(-r * 0.2, -r * 0.4);
    ctx.moveTo(r * 0.3, r * 0.3); ctx.lineTo(-r * 0.2, r * 0.4);
    ctx.stroke();
    // Nose flamethrower with intense glow
    const flamePulse = 0.5 + Math.sin(time * 8) * 0.3;
    const fGr = ctx.createRadialGradient(r * 1.4, 0, 0, r * 1.4, 0, r * 0.8);
    fGr.addColorStop(0, hexToRgba('#fff', flamePulse * 0.5));
    fGr.addColorStop(0.2, hexToRgba('#ffaa00', flamePulse * 0.4));
    fGr.addColorStop(0.5, hexToRgba('#ff4400', flamePulse * 0.2));
    fGr.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = fGr;
    ctx.beginPath(); ctx.arc(r * 1.4, 0, r * 0.8, 0, Math.PI * 2); ctx.fill();

  } else {
    // Fallback generic diamond
    ctx.beginPath();
    ctx.moveTo(r * 1.5, 0);
    ctx.lineTo(0, -r * 0.8);
    ctx.lineTo(-r * 0.8, 0);
    ctx.lineTo(0, r * 0.8);
    ctx.closePath();
    ctx.fillStyle = hexToRgba(color, 0.15); ctx.fill();
    ctx.strokeStyle = color; ctx.lineWidth = 1.5; ctx.stroke();
  }
}

export default ShipCanvas;
