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
    const sides = 6;
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
    // Inner hex
    ctx.strokeStyle = hexToRgba(glow, 0.3); ctx.lineWidth = 1;
    ctx.beginPath();
    for (let i = 0; i <= sides; i++) {
      const a = (i / sides) * Math.PI * 2 - Math.PI / 6;
      const px = Math.cos(a) * r * 0.8;
      const py = Math.sin(a) * r * 0.8 * 0.85;
      if (i === 0) ctx.moveTo(px, py); else ctx.lineTo(px, py);
    }
    ctx.closePath(); ctx.stroke();
    // Triple guns
    for (const side of [-1, 0, 1]) {
      ctx.fillStyle = hexToRgba(color, 0.5);
      ctx.fillRect(r * 0.9, side * r * 0.35 - 1.5, r * 0.6, 3);
    }
    // Core
    const cp = 0.4 + Math.sin(time * 2) * 0.2;
    const cg = ctx.createRadialGradient(0, 0, 1, 0, 0, r * 0.5);
    cg.addColorStop(0, hexToRgba('#fff', cp));
    cg.addColorStop(0.3, hexToRgba(color, cp * 0.6));
    cg.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = cg;
    ctx.beginPath(); ctx.arc(0, 0, r * 0.5, 0, Math.PI * 2); ctx.fill();

  } else if (shipType === 'wraith') {
    const phase = 0.6 + Math.sin(time * 6) * 0.2;
    ctx.globalAlpha = phase;
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
    for (let i = 1; i <= 3; i++) {
      ctx.fillStyle = hexToRgba(color, 0.04 * (4 - i));
      ctx.beginPath(); ctx.arc(-i * 7, 0, r * 0.6, 0, Math.PI * 2); ctx.fill();
    }
    ctx.fillStyle = hexToRgba('#fff', 0.5 + Math.sin(time * 7) * 0.4);
    ctx.beginPath(); ctx.arc(r * 0.4, 0, 2, 0, Math.PI * 2); ctx.fill();
    ctx.globalAlpha = 1;

  } else if (shipType === 'sentinel') {
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
    // Shield arc
    const shp = 0.4 + Math.sin(time * 3) * 0.2;
    ctx.strokeStyle = hexToRgba(glow, shp); ctx.lineWidth = 2.5;
    ctx.beginPath(); ctx.arc(r * 0.5, 0, r * 0.8, -0.8, 0.8); ctx.stroke();
    ctx.strokeStyle = hexToRgba(glow, shp * 0.5); ctx.lineWidth = 1.5;
    ctx.beginPath(); ctx.arc(r * 0.5, 0, r * 1.0, -0.6, 0.6); ctx.stroke();
    // Reactor
    const sg = ctx.createRadialGradient(-r * 0.1, 0, 0, -r * 0.1, 0, r * 0.35);
    sg.addColorStop(0, hexToRgba('#fff', 0.5));
    sg.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = sg;
    ctx.beginPath(); ctx.arc(-r * 0.1, 0, r * 0.35, 0, Math.PI * 2); ctx.fill();

  } else if (shipType === 'tempest') {
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
    // Lightning arcs
    const lp = 0.3 + Math.sin(time * 12) * 0.3;
    ctx.strokeStyle = hexToRgba('#fff', lp); ctx.lineWidth = 0.8;
    ctx.beginPath();
    ctx.moveTo(r * 1.5, -r * 0.1);
    ctx.lineTo(r * 0.8, -r * 0.25 + Math.sin(time * 20) * 2);
    ctx.lineTo(r * 0.3, -r * 0.1 + Math.sin(time * 25) * 1.5);
    ctx.lineTo(-r * 0.2, -r * 0.2);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(r * 1.5, r * 0.1);
    ctx.lineTo(r * 0.8, r * 0.25 + Math.sin(time * 22) * 2);
    ctx.lineTo(r * 0.3, r * 0.1 + Math.sin(time * 27) * 1.5);
    ctx.lineTo(-r * 0.2, r * 0.2);
    ctx.stroke();

  } else if (shipType === 'venom') {
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
    // Drip particles
    for (let i = 0; i < 4; i++) {
      const dy = Math.sin(time * 3 + i * 1.5) * r * 0.3 + r * 0.4;
      const dx = -r * 0.3 + i * r * 0.2;
      ctx.fillStyle = hexToRgba(color, 0.3 + Math.sin(time * 4 + i) * 0.2);
      ctx.beginPath(); ctx.arc(dx, dy, 1.5, 0, Math.PI * 2); ctx.fill();
    }
    // Toxic eye
    ctx.fillStyle = hexToRgba('#fff', 0.6);
    ctx.beginPath(); ctx.arc(r * 0.4, -r * 0.1, 2, 0, Math.PI * 2); ctx.fill();
    ctx.fillStyle = hexToRgba(color, 0.8);
    ctx.beginPath(); ctx.arc(r * 0.4, -r * 0.1, 1, 0, Math.PI * 2); ctx.fill();

  } else if (shipType === 'nova_ship') {
    const starPulse = 1 + Math.sin(time * 4) * 0.06;
    ctx.save(); ctx.scale(starPulse, starPulse);
    ctx.beginPath();
    for (let i = 0; i < 8; i++) {
      const a = (i / 8) * Math.PI * 2 - Math.PI / 2;
      const outerR = i % 2 === 0 ? r * 1.4 : r * 0.6;
      if (i === 0) ctx.moveTo(Math.cos(a) * outerR, Math.sin(a) * outerR);
      else ctx.lineTo(Math.cos(a) * outerR, Math.sin(a) * outerR);
    }
    ctx.closePath();
    ctx.fillStyle = hexToRgba(color, 0.15); ctx.fill();
    ctx.strokeStyle = color; ctx.lineWidth = 1.5; ctx.stroke();
    ctx.restore();
    // Energy orb
    const op = 0.5 + Math.sin(time * 5) * 0.3;
    const ng = ctx.createRadialGradient(0, 0, 0, 0, 0, r * 0.5);
    ng.addColorStop(0, hexToRgba('#fff', op));
    ng.addColorStop(0.5, hexToRgba(color, op * 0.5));
    ng.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = ng;
    ctx.beginPath(); ctx.arc(0, 0, r * 0.5, 0, Math.PI * 2); ctx.fill();
    // Ring
    const rp = (time * 1.5) % 1;
    ctx.strokeStyle = hexToRgba(color, (1 - rp) * 0.3); ctx.lineWidth = 1;
    ctx.beginPath(); ctx.arc(0, 0, r * 0.5 + rp * r, 0, Math.PI * 2); ctx.stroke();

  } else if (shipType === 'chronos') {
    ctx.beginPath();
    ctx.arc(0, 0, r * 1.1, 0, Math.PI * 2);
    ctx.fillStyle = hexToRgba(color, 0.12); ctx.fill();
    ctx.strokeStyle = color; ctx.lineWidth = 1.5; ctx.stroke();
    // Clock hands
    ctx.strokeStyle = hexToRgba('#fff', 0.7); ctx.lineWidth = 1.2;
    ctx.beginPath(); ctx.moveTo(0, 0);
    ctx.lineTo(Math.cos(time * 2) * r * 0.8, Math.sin(time * 2) * r * 0.8);
    ctx.stroke();
    ctx.strokeStyle = hexToRgba(glow, 0.5); ctx.lineWidth = 0.8;
    ctx.beginPath(); ctx.moveTo(0, 0);
    ctx.lineTo(Math.cos(time * 8) * r * 0.5, Math.sin(time * 8) * r * 0.5);
    ctx.stroke();
    // Hour markers
    for (let i = 0; i < 12; i++) {
      const a = (i / 12) * Math.PI * 2;
      ctx.fillStyle = hexToRgba(glow, 0.5);
      ctx.beginPath(); ctx.arc(Math.cos(a) * r * 0.95, Math.sin(a) * r * 0.95, 1, 0, Math.PI * 2); ctx.fill();
    }
    // Nose pointer
    ctx.fillStyle = hexToRgba(color, 0.8);
    ctx.beginPath();
    ctx.moveTo(r * 1.5, 0);
    ctx.lineTo(r * 1.1, -r * 0.15);
    ctx.lineTo(r * 1.1, r * 0.15);
    ctx.closePath(); ctx.fill();

  } else if (shipType === 'leviathan') {
    ctx.beginPath();
    ctx.moveTo(r * 1.8, 0);
    ctx.bezierCurveTo(r * 1.2, -r * 0.7, r * 0.2, -r * 0.9, -r * 0.4, -r * 0.7);
    ctx.bezierCurveTo(-r * 0.8, -r * 0.5, -r * 1.0, -r * 0.2, -r * 1.0, 0);
    ctx.bezierCurveTo(-r * 1.0, r * 0.2, -r * 0.8, r * 0.5, -r * 0.4, r * 0.7);
    ctx.bezierCurveTo(r * 0.2, r * 0.9, r * 1.2, r * 0.7, r * 1.8, 0);
    ctx.closePath();
    ctx.fillStyle = hexToRgba(color, 0.2); ctx.fill();
    ctx.strokeStyle = color; ctx.lineWidth = 2.5; ctx.stroke();
    // Ridges
    for (let i = 0; i < 4; i++) {
      ctx.strokeStyle = hexToRgba(glow, 0.2); ctx.lineWidth = 1;
      ctx.beginPath(); ctx.ellipse(r * 0.6 - i * r * 0.35, 0, r * 0.15, r * 0.5, 0, 0, Math.PI * 2); ctx.stroke();
    }
    // Maw
    const mp = 0.4 + Math.sin(time * 3) * 0.2;
    ctx.fillStyle = hexToRgba('#fff', mp);
    ctx.beginPath(); ctx.arc(r * 1.4, 0, r * 0.25, 0, Math.PI * 2); ctx.fill();

  } else if (shipType === 'raptor') {
    ctx.beginPath();
    ctx.moveTo(r * 2.5, 0);
    ctx.lineTo(r * 0.5, -r * 0.2);
    ctx.lineTo(-r * 0.2, -r * 0.4);
    ctx.lineTo(-r * 0.5, -r * 0.15);
    ctx.lineTo(-r * 0.5, r * 0.15);
    ctx.lineTo(-r * 0.2, r * 0.4);
    ctx.lineTo(r * 0.5, r * 0.2);
    ctx.closePath();
    ctx.fillStyle = hexToRgba(color, 0.12); ctx.fill();
    ctx.strokeStyle = color; ctx.lineWidth = 1; ctx.stroke();
    // Speed streaks
    ctx.strokeStyle = hexToRgba(color, 0.3); ctx.lineWidth = 0.6;
    for (let i = -2; i <= 2; i++) {
      const len = 12 + Math.sin(time * 15 + i * 4) * 4;
      ctx.beginPath(); ctx.moveTo(-r * 0.5, i * 2); ctx.lineTo(-r - len, i * 2.5); ctx.stroke();
    }
    // Nose
    ctx.fillStyle = hexToRgba('#fff', 0.7 + Math.sin(time * 10) * 0.2);
    ctx.beginPath(); ctx.arc(r * 2.2, 0, 1, 0, Math.PI * 2); ctx.fill();

  } else if (shipType === 'oracle') {
    ctx.beginPath();
    ctx.moveTo(r * 1.6, 0);
    ctx.quadraticCurveTo(r * 0.5, -r * 0.7, -r * 0.3, -r * 0.5);
    ctx.quadraticCurveTo(-r * 0.6, 0, -r * 0.3, r * 0.5);
    ctx.quadraticCurveTo(r * 0.5, r * 0.7, r * 1.6, 0);
    ctx.closePath();
    ctx.fillStyle = hexToRgba(color, 0.12); ctx.fill();
    ctx.strokeStyle = color; ctx.lineWidth = 1.5; ctx.stroke();
    // Third eye
    const es = 0.7 + Math.sin(time * 4) * 0.15;
    ctx.fillStyle = hexToRgba('#fff', 0.6 * es);
    ctx.beginPath(); ctx.ellipse(r * 0.3, 0, r * 0.35, r * 0.2 * es, 0, 0, Math.PI * 2); ctx.fill();
    ctx.fillStyle = hexToRgba(color, 0.8);
    ctx.beginPath(); ctx.arc(r * 0.3, 0, r * 0.12, 0, Math.PI * 2); ctx.fill();
    ctx.fillStyle = '#fff';
    ctx.beginPath(); ctx.arc(r * 0.3, 0, r * 0.05, 0, Math.PI * 2); ctx.fill();
    // Runes
    for (let i = 0; i < 6; i++) {
      const a = time * 2 + (i / 6) * Math.PI * 2;
      ctx.fillStyle = hexToRgba(glow, 0.3 + Math.sin(time * 5 + i) * 0.2);
      ctx.beginPath(); ctx.arc(Math.cos(a) * r * 1.3, Math.sin(a) * r * 1.3, 1.5, 0, Math.PI * 2); ctx.fill();
    }

  } else if (shipType === 'pyro') {
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
    // Flame wreath
    for (let i = 0; i < 8; i++) {
      const a = (i / 8) * Math.PI * 2 + time * 4;
      const flameR = r * 1.1 + Math.sin(time * 10 + i * 2) * r * 0.2;
      const fx = Math.cos(a) * flameR;
      const fy = Math.sin(a) * flameR;
      ctx.fillStyle = hexToRgba(i % 2 === 0 ? '#ff4400' : '#ffaa00', 0.3 + Math.sin(time * 8 + i) * 0.2);
      ctx.beginPath(); ctx.arc(fx, fy, 2 + Math.sin(time * 12 + i) * 1, 0, Math.PI * 2); ctx.fill();
    }
    // Flame glow at nose
    const fp = 0.4 + Math.sin(time * 8) * 0.3;
    const fg = ctx.createRadialGradient(r * 1.2, 0, 0, r * 1.2, 0, r * 0.6);
    fg.addColorStop(0, hexToRgba('#ffaa00', fp));
    fg.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = fg;
    ctx.beginPath(); ctx.arc(r * 1.2, 0, r * 0.6, 0, Math.PI * 2); ctx.fill();

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
