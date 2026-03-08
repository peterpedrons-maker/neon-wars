import React from 'react';
import { ShipType } from '../../game/types';

interface ClassSelectProps {
  onSelect: (cls: ShipType) => void;
  onBack: () => void;
}

const ships: { id: ShipType; name: string; icon: string; desc: string; stats: string }[] = [
  { id: 'phantom', name: 'Phantom', icon: '👻', desc: 'Nave ágil com disparos energéticos. Especial: Nova de plasma em todas as direções.', stats: 'HP: 80 | DMG: 15 | VEL: Média' },
  { id: 'interceptor', name: 'Interceptor', icon: '⚡', desc: 'Ultra veloz com tiro rápido. Especial: Barragem lock-on nos inimigos próximos.', stats: 'HP: 65 | DMG: 10 | VEL: Alta' },
  { id: 'titan', name: 'Titan', icon: '💥', desc: 'Nave pesada com ataque devastador em área. Especial: Onda de choque massiva.', stats: 'HP: 130 | DMG: 28 | VEL: Baixa' },
];

const shipColors: Record<ShipType, string> = {
  phantom: '#bf5af2',
  interceptor: '#00e5ff',
  titan: '#ff6b00',
};

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
            <span className="text-5xl mb-3">{s.icon}</span>
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
