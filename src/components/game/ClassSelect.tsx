import React, { useRef, useEffect } from 'react';
import { ShipType } from '../../game/types';
import { COLORS } from '../../game/constants';
import { playClick, playHover, playBack } from '../../game/audio';
import { SHIP_ICONS } from '../../game/icons';

interface ClassSelectProps {
  onSelect: (cls: ShipType) => void;
  onBack: () => void;
  unlockedShips?: string[];
}

const ships: { id: ShipType; name: string; desc: string; stats: string; type: 'ranged' | 'melee' | 'special' }[] = [
  { id: 'phantom', name: 'Phantom', desc: 'Nave ágil com disparos energéticos. Especial: Nova de plasma.', stats: 'DMG: 15 | VEL: Média', type: 'ranged' },
  { id: 'interceptor', name: 'Interceptor', desc: 'Ultra veloz com tiro rápido. Especial: Lock-on barrage.', stats: 'DMG: 10 | VEL: Alta', type: 'ranged' },
  { id: 'titan', name: 'Titan', desc: 'Ataque devastador em área. Especial: Onda de choque.', stats: 'DMG: 28 | VEL: Baixa', type: 'melee' },
  { id: 'spectre', name: 'Spectre', desc: 'Furtiva com teleporte. Especial: Teleporte + explosão.', stats: 'DMG: 20 | VEL: Alta', type: 'ranged' },
  { id: 'valkyrie', name: 'Valkyrie', desc: 'Guerreira alada, tiro duplo. Especial: Chuva de lanças.', stats: 'DMG: 12 | VEL: Média+', type: 'ranged' },
  { id: 'juggernaut', name: 'Juggernaut', desc: 'Fortaleza indestrutível. Especial: Campo de destruição.', stats: 'DMG: 35 | VEL: Lenta', type: 'melee' },
  { id: 'wraith', name: 'Wraith', desc: 'Fantasma que cria clones sombrios. Especial: Invisibilidade + clones.', stats: 'DMG: 18 | VEL: Alta', type: 'ranged' },
  { id: 'sentinel', name: 'Sentinel', desc: 'Tanque com barreira protetora. Especial: Escudo + reflexão.', stats: 'DMG: 22 | VEL: Baixa', type: 'ranged' },
  { id: 'tempest', name: 'Tempest', desc: 'Controlador de ventos. Especial: Tornado que puxa inimigos.', stats: 'DMG: 14 | VEL: Alta', type: 'ranged' },
  { id: 'venom', name: 'Venom', desc: 'Envenenador com tiros tóxicos. Especial: Nuvem venenosa.', stats: 'DMG: 16 | VEL: Média', type: 'special' },
  { id: 'nova_ship', name: 'Nova', desc: 'Poder destrutivo bruto. Especial: Supernova massiva.', stats: 'DMG: 30 | VEL: Média-', type: 'special' },
  { id: 'chronos', name: 'Chronos', desc: 'Manipulador do tempo. Especial: Congela todos os inimigos.', stats: 'DMG: 13 | VEL: Média', type: 'special' },
  { id: 'leviathan', name: 'Leviathan', desc: 'Colosso devorador. Especial: Devora e se cura.', stats: 'DMG: 40 | VEL: Lenta', type: 'melee' },
  { id: 'raptor', name: 'Raptor', desc: 'O mais veloz. Tiro ultra-rápido. Especial: Blitz dash.', stats: 'DMG: 11 | VEL: Máxima', type: 'ranged' },
  { id: 'oracle', name: 'Oracle', desc: 'Tiros rastreadores. Especial: Marca todos os inimigos.', stats: 'DMG: 12 | VEL: Média', type: 'special' },
  { id: 'pyro', name: 'Pyro', desc: 'Lança-chamas devastador. Especial: Anel de fogo.', stats: 'DMG: 20 | VEL: Média-', type: 'special' },
];

function hexToRgba(hex: string, a: number): string {
  if (!hex || hex[0] !== '#') return `rgba(255,255,255,${a})`;
  const r = parseInt(hex.slice(1, 3), 16) || 255;
  const g = parseInt(hex.slice(3, 5), 16) || 255;
  const b = parseInt(hex.slice(5, 7), 16) || 255;
  return `rgba(${r},${g},${b},${a})`;
}

function ShipCanvas({ shipType }: { shipType: ShipType }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animRef = useRef<number>(0);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    const w = 140, h = 100;
    canvas.width = w * 2; canvas.height = h * 2;
    ctx.scale(2, 2);
    const color = COLORS[shipType] || '#fff';
    const glow = COLORS[shipType + 'Glow'] || '#fff';
    function loop() {
      const time = Date.now() * 0.001;
      ctx!.clearRect(0, 0, w, h);
      const cx = w / 2, cy = h / 2, r = 16;
      // Background glow
      const bgGrad = ctx!.createRadialGradient(cx, cy, 5, cx, cy, 70);
      bgGrad.addColorStop(0, hexToRgba(color, 0.15));
      bgGrad.addColorStop(1, 'rgba(0,0,0,0)');
      ctx!.fillStyle = bgGrad;
      ctx!.fillRect(0, 0, w, h);
      ctx!.save();
      ctx!.translate(cx, cy);
      // Exhaust
      const thrustPulse = 0.6 + Math.sin(time * 18) * 0.3;
      ctx!.fillStyle = hexToRgba(color, thrustPulse * 0.4);
      ctx!.beginPath();
      ctx!.moveTo(-r * 0.4, -3); ctx!.lineTo(-r - 15, 0); ctx!.lineTo(-r * 0.4, 3);
      ctx!.closePath(); ctx!.fill();
      ctx!.fillStyle = hexToRgba('#fff', thrustPulse * 0.6);
      ctx!.beginPath();
      ctx!.moveTo(-r * 0.35, -1); ctx!.lineTo(-r - 10, 0); ctx!.lineTo(-r * 0.35, 1);
      ctx!.closePath(); ctx!.fill();
      // Generic ship shape
      ctx!.shadowColor = color; ctx!.shadowBlur = 15;
      ctx!.beginPath();
      ctx!.moveTo(r * 1.6, 0);
      ctx!.lineTo(r * 0.3, -r * 0.8);
      ctx!.lineTo(-r * 0.5, -r * 0.6);
      ctx!.lineTo(-r * 0.6, 0);
      ctx!.lineTo(-r * 0.5, r * 0.6);
      ctx!.lineTo(r * 0.3, r * 0.8);
      ctx!.closePath();
      ctx!.fillStyle = hexToRgba(color, 0.15); ctx!.fill();
      ctx!.strokeStyle = color; ctx!.lineWidth = 1.5; ctx!.stroke();
      // Core
      const p = 0.4 + Math.sin(time * 3) * 0.2;
      ctx!.fillStyle = hexToRgba(glow, p);
      ctx!.beginPath(); ctx!.arc(r * 0.3, 0, 2, 0, Math.PI * 2); ctx!.fill();
      ctx!.shadowBlur = 0;
      ctx!.restore();
      animRef.current = requestAnimationFrame(loop);
    }
    loop();
    return () => cancelAnimationFrame(animRef.current);
  }, [shipType]);

  return <canvas ref={canvasRef} style={{ width: 140, height: 100 }} className="pointer-events-none" />;
}

const TYPE_BADGES: Record<string, { label: string; color: string }> = {
  ranged: { label: 'RANGED', color: '#0ff' },
  melee: { label: 'MELEE', color: '#ff6b00' },
  special: { label: 'SPECIAL', color: '#bf5af2' },
};

const ClassSelect: React.FC<ClassSelectProps> = ({ onSelect, onBack, unlockedShips }) => {
  const unlocked = unlockedShips || ['phantom', 'interceptor', 'titan'];

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-[#000008] text-[#e0e8ff] select-none p-4">
      <h2 className="text-3xl md:text-4xl font-bold mb-2" style={{ fontFamily: 'Orbitron, monospace', textShadow: '0 0 30px rgba(0,255,255,0.3)' }}>
        Escolha sua Nave
      </h2>
      <div className="w-48 h-px bg-gradient-to-r from-transparent via-[#0ff] to-transparent mb-6" />

      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-2.5 mb-6 max-w-7xl max-h-[70vh] overflow-y-auto pr-1"
        style={{ scrollbarWidth: 'thin', scrollbarColor: '#0ff33 transparent' }}>
        {ships.map(s => {
          const isLocked = !unlocked.includes(s.id);
          const color = COLORS[s.id] || '#fff';
          const badge = TYPE_BADGES[s.type];
          return (
            <button key={s.id}
              onClick={() => { if (!isLocked) { playClick(); onSelect(s.id); } }}
              onMouseEnter={() => { if (!isLocked) playHover(); }}
              disabled={isLocked}
              className="flex flex-col items-center p-3 rounded-xl border transition-all duration-200 hover:scale-105 active:scale-95 w-44 relative"
              style={{
                borderColor: isLocked ? '#333' : color,
                background: 'linear-gradient(180deg, rgba(0,0,8,0.95), rgba(0,0,20,0.98))',
                boxShadow: isLocked ? 'none' : `0 0 20px ${color}33, inset 0 0 15px ${color}11`,
                opacity: isLocked ? 0.35 : 1,
                cursor: isLocked ? 'not-allowed' : 'pointer',
              }}>
              {isLocked && (
                <div className="absolute top-1.5 right-1.5 text-[9px] px-1.5 py-0.5 rounded font-bold font-mono"
                  style={{ background: 'rgba(255,64,96,0.2)', color: '#ff4060' }}>🔒</div>
              )}
              <div className="absolute top-1.5 left-1.5 text-[8px] px-1 py-0.5 rounded font-bold font-mono"
                style={{ background: badge.color + '22', color: badge.color }}>
                {badge.label}
              </div>
              <ShipCanvas shipType={s.id} />
              <h3 className="text-sm font-bold mb-0.5" style={{ color: isLocked ? '#555' : color, fontFamily: 'Orbitron, monospace' }}>
                {s.name}
              </h3>
              <p className="text-[9px] text-[#6080aa] text-center mb-1 leading-tight">{s.desc}</p>
              <p className="text-[8px] font-mono" style={{ color: isLocked ? '#444' : color }}>{s.stats}</p>
            </button>
          );
        })}
      </div>

      <button onClick={() => { playBack(); onBack(); }} onMouseEnter={playHover}
        className="text-[#6080aa] hover:text-[#0ff] transition-colors text-lg font-mono">
        ← Voltar
      </button>
    </div>
  );
};

export default ClassSelect;
