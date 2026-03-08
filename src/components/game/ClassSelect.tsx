import React, { useRef, useEffect } from 'react';
import { ShipType } from '../../game/types';

interface ClassSelectProps {
  onSelect: (cls: ShipType) => void;
  onBack: () => void;
}

const ships: { id: ShipType; name: string; desc: string; stats: string; locked?: boolean }[] = [
  { id: 'phantom', name: 'Phantom', desc: 'Nave ágil com disparos energéticos. Especial: Nova de plasma em todas as direções.', stats: 'DMG: 15 | VEL: Média' },
  { id: 'interceptor', name: 'Interceptor', desc: 'Ultra veloz com tiro rápido. Especial: Barragem lock-on nos inimigos próximos.', stats: 'DMG: 10 | VEL: Alta' },
  { id: 'titan', name: 'Titan', desc: 'Nave pesada com ataque devastador em área. Especial: Onda de choque massiva.', stats: 'DMG: 28 | VEL: Baixa' },
  { id: 'spectre', name: 'Spectre', desc: 'Nave furtiva com dano alto e pouca vida. Especial: Teleporte + explosão fantasma.', stats: 'DMG: 20 | VEL: Alta' },
  { id: 'valkyrie', name: 'Valkyrie', desc: 'Guerreira alada com tiro rápido e HP extra. Especial: Chuva de lanças energéticas.', stats: 'DMG: 12 | VEL: Média-Alta' },
  { id: 'juggernaut', name: 'Juggernaut', desc: 'Fortaleza indestrutível. Lenta mas devastadora. Especial: Campo de destruição total.', stats: 'DMG: 35 | VEL: Muito Baixa' },
];

const shipColors: Record<string, string> = {
  phantom: '#bf5af2',
  interceptor: '#00e5ff',
  titan: '#ff6b00',
  spectre: '#9040ff',
  valkyrie: '#ff1493',
  juggernaut: '#ff4500',
};

const shipGlows: Record<string, string> = {
  phantom: '#e0b0ff',
  interceptor: '#80f0ff',
  titan: '#ffaa55',
  spectre: '#c090ff',
  valkyrie: '#ff80b0',
  juggernaut: '#ff8040',
};

function hexToRgba(hex: string, a: number): string {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return `rgba(${r},${g},${b},${a})`;
}

function drawShipPreview(ctx: CanvasRenderingContext2D, shipType: ShipType, w: number, h: number, time: number) {
  ctx.clearRect(0, 0, w, h);
  
  const color = shipColors[shipType];
  const glow = shipGlows[shipType];
  const cx = w / 2;
  const cy = h / 2;
  const r = 18;

  // Background glow
  const bgGrad = ctx.createRadialGradient(cx, cy, 5, cx, cy, 80);
  bgGrad.addColorStop(0, hexToRgba(color, 0.15));
  bgGrad.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.fillStyle = bgGrad;
  ctx.fillRect(0, 0, w, h);

  ctx.save();
  ctx.translate(cx, cy);

  // Engine exhaust
  const thrustPulse = 0.6 + Math.sin(time * 18) * 0.3;
  const thrustLen = 18;
  const exhaustSpread = shipType === 'titan' ? 6 : shipType === 'phantom' ? 4 : 3;
  
  for (let i = -1; i <= 1; i += 2) {
    const oy = i * exhaustSpread;
    ctx.fillStyle = hexToRgba(color, thrustPulse * 0.4);
    ctx.beginPath();
    ctx.moveTo(-r * 0.4, oy - 3);
    ctx.quadraticCurveTo(-r - thrustLen * 0.7, oy, -r - thrustLen, oy);
    ctx.quadraticCurveTo(-r - thrustLen * 0.7, oy, -r * 0.4, oy + 3);
    ctx.closePath(); ctx.fill();
    ctx.fillStyle = hexToRgba('#ffffff', thrustPulse * 0.7);
    ctx.beginPath();
    ctx.moveTo(-r * 0.35, oy - 1.2);
    ctx.lineTo(-r - thrustLen * 0.5, oy);
    ctx.lineTo(-r * 0.35, oy + 1.2);
    ctx.closePath(); ctx.fill();
  }

  ctx.shadowColor = color;
  ctx.shadowBlur = 20 + Math.sin(time * 3) * 6;

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
    ctx.strokeStyle = hexToRgba(glow, 0.5); ctx.lineWidth = 0.8;
    ctx.beginPath();
    ctx.moveTo(r * 0.3, -r * 0.2); ctx.lineTo(-r * 0.4, -r * 0.9);
    ctx.moveTo(r * 0.3, r * 0.2); ctx.lineTo(-r * 0.4, r * 0.9);
    ctx.stroke();
    const wingPulse = 0.5 + Math.sin(time * 4) * 0.3;
    ctx.fillStyle = hexToRgba(glow, wingPulse);
    ctx.beginPath(); ctx.arc(-r * 0.3, -r * 1.15, 1.5, 0, Math.PI * 2); ctx.fill();
    ctx.beginPath(); ctx.arc(-r * 0.3, r * 1.15, 1.5, 0, Math.PI * 2); ctx.fill();
    ctx.strokeStyle = hexToRgba(color, 0.3); ctx.lineWidth = 0.6;
    ctx.beginPath(); ctx.moveTo(r * 1.2, 0); ctx.lineTo(-r * 0.5, 0); ctx.stroke();
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
    for (const side of [-1, 1]) {
      ctx.beginPath();
      ctx.moveTo(r * 0.4, side * r * 0.35);
      ctx.lineTo(-r * 0.1, side * r * 0.7);
      ctx.lineTo(-r * 0.6, side * r * 0.65);
      ctx.lineTo(-r * 0.4, side * r * 0.35);
      ctx.closePath();
      ctx.fillStyle = hexToRgba(color, 0.1); ctx.fill();
      ctx.strokeStyle = color; ctx.lineWidth = 1; ctx.stroke();
      ctx.fillStyle = hexToRgba(glow, 0.4 + Math.sin(time * 6 + side) * 0.2);
      ctx.beginPath(); ctx.arc(-r * 0.3, side * r * 0.55, 1.5, 0, Math.PI * 2); ctx.fill();
    }
    ctx.strokeStyle = hexToRgba(glow, 0.6); ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(r * 1.0, -r * 0.1); ctx.lineTo(r * 0.5, -r * 0.5);
    ctx.moveTo(r * 1.0, r * 0.1); ctx.lineTo(r * 0.5, r * 0.5);
    ctx.stroke();
    ctx.fillStyle = hexToRgba('#ffffff', 0.6 + Math.sin(time * 8) * 0.3);
    ctx.beginPath(); ctx.arc(r * 1.8, 0, 1, 0, Math.PI * 2); ctx.fill();
  } else {
    // Titan
    ctx.beginPath();
    ctx.moveTo(r * 1.5, 0);
    ctx.lineTo(r * 0.6, -r * 0.45);
    ctx.lineTo(r * 0.1, -r * 0.6);
    ctx.lineTo(-r * 0.3, -r * 0.7);
    ctx.lineTo(-r * 0.5, -r * 1.3);
    ctx.lineTo(-r * 0.8, -r * 1.1);
    ctx.lineTo(-r * 0.65, -r * 0.5);
    ctx.lineTo(-r * 0.8, -r * 0.25);
    ctx.lineTo(-r * 0.8, r * 0.25);
    ctx.lineTo(-r * 0.65, r * 0.5);
    ctx.lineTo(-r * 0.8, r * 1.1);
    ctx.lineTo(-r * 0.5, r * 1.3);
    ctx.lineTo(-r * 0.3, r * 0.7);
    ctx.lineTo(r * 0.1, r * 0.6);
    ctx.lineTo(r * 0.6, r * 0.45);
    ctx.closePath();
    ctx.fillStyle = hexToRgba(color, 0.18); ctx.fill();
    ctx.strokeStyle = color; ctx.lineWidth = 2; ctx.stroke();
    // Armor plates
    ctx.strokeStyle = hexToRgba(glow, 0.3); ctx.lineWidth = 0.8;
    ctx.beginPath();
    ctx.moveTo(r * 0.8, -r * 0.15); ctx.lineTo(-r * 0.3, -r * 0.55);
    ctx.moveTo(r * 0.8, r * 0.15); ctx.lineTo(-r * 0.3, r * 0.55);
    ctx.stroke();
    // Cannon glow
    const cannonPulse = 0.4 + Math.sin(time * 3) * 0.2;
    ctx.fillStyle = hexToRgba(glow, cannonPulse);
    ctx.beginPath(); ctx.arc(r * 1.3, 0, 2.5, 0, Math.PI * 2); ctx.fill();
  }

  // Cockpit glow
  const cockpitPulse = 0.4 + Math.sin(time * 2) * 0.15;
  ctx.fillStyle = hexToRgba('#ffffff', cockpitPulse);
  ctx.beginPath(); ctx.arc(r * 0.4, 0, 2, 0, Math.PI * 2); ctx.fill();

  ctx.restore();
}

function ShipCanvas({ shipType }: { shipType: ShipType }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animRef = useRef<number>(0);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const w = 160;
    const h = 120;
    canvas.width = w * 2;
    canvas.height = h * 2;
    ctx.scale(2, 2);

    function loop() {
      const time = Date.now() * 0.001;
      drawShipPreview(ctx!, shipType, w, h, time);
      animRef.current = requestAnimationFrame(loop);
    }
    loop();

    return () => cancelAnimationFrame(animRef.current);
  }, [shipType]);

  return (
    <canvas
      ref={canvasRef}
      style={{ width: 160, height: 120 }}
      className="pointer-events-none"
    />
  );
}

const ClassSelect: React.FC<ClassSelectProps> = ({ onSelect, onBack }) => {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-[#000008] text-[#e0e8ff] select-none p-4">
      <h2 className="text-4xl md:text-5xl font-bold mb-2" style={{ fontFamily: 'Orbitron, monospace', textShadow: '0 0 30px rgba(0,255,255,0.3)' }}>
        Escolha sua Nave
      </h2>
      <div className="w-48 h-px bg-gradient-to-r from-transparent via-[#0ff] to-transparent mb-8" />

      <div className="flex flex-col md:flex-row gap-6 mb-8">
        {ships.map(s => (
          <button
            key={s.id}
            onClick={() => onSelect(s.id)}
            className="flex flex-col items-center p-6 rounded-xl border transition-all duration-300 hover:scale-105 active:scale-95 w-64"
            style={{
              borderColor: shipColors[s.id],
              background: `linear-gradient(180deg, rgba(0,0,8,0.95) 0%, rgba(0,0,20,0.98) 100%)`,
              boxShadow: `0 0 25px ${shipColors[s.id]}33, inset 0 0 20px ${shipColors[s.id]}11`,
            }}
            onMouseEnter={e => {
              (e.currentTarget as HTMLElement).style.boxShadow = `0 0 40px ${shipColors[s.id]}66, inset 0 0 30px ${shipColors[s.id]}22`;
            }}
            onMouseLeave={e => {
              (e.currentTarget as HTMLElement).style.boxShadow = `0 0 25px ${shipColors[s.id]}33, inset 0 0 20px ${shipColors[s.id]}11`;
            }}
          >
            <ShipCanvas shipType={s.id} />
            <h3 className="text-2xl font-bold mb-2" style={{ color: shipColors[s.id], fontFamily: 'Orbitron, monospace' }}>
              {s.name}
            </h3>
            <p className="text-sm text-[#6080aa] text-center mb-3">{s.desc}</p>
            <p className="text-xs font-mono" style={{ color: shipColors[s.id] }}>{s.stats}</p>
          </button>
        ))}
      </div>

      <button
        onClick={onBack}
        className="text-[#6080aa] hover:text-[#0ff] transition-colors text-lg font-mono"
      >
        ← Voltar
      </button>
    </div>
  );
};

export default ClassSelect;
