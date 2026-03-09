import React, { useEffect } from 'react';
import { ShipType } from '../../game/types';
import { COLORS } from '../../game/constants';
import { playClick, playHover, playBack, startSelectMusic, stopSelectMusic } from '../../game/audio';
import ShipCanvas from './ShipCanvas';

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
              <ShipCanvas shipType={s.id} width={120} height={86} />
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
