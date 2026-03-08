import React from 'react';
import { PlayerClass } from '../../game/types';

interface ClassSelectProps {
  onSelect: (cls: PlayerClass) => void;
  onBack: () => void;
}

const classes: { id: PlayerClass; name: string; icon: string; desc: string; stats: string }[] = [
  { id: 'mage', name: 'Mago', icon: '🔮', desc: 'Lança projéteis mágicos à distância. Especial: Nova arcana em todas as direções.', stats: 'HP: 80 | DMG: 15 | VEL: Média' },
  { id: 'archer', name: 'Arqueiro', icon: '🏹', desc: 'Dispara flechas rápidas. Especial: Chuva de flechas nos inimigos próximos.', stats: 'HP: 70 | DMG: 10 | VEL: Alta' },
  { id: 'warrior', name: 'Guerreiro', icon: '⚔️', desc: 'Ataque corpo-a-corpo devastador. Especial: Redemoinho de lâminas.', stats: 'HP: 120 | DMG: 25 | VEL: Baixa' },
];

const classColors: Record<PlayerClass, string> = {
  mage: '#9b59b6',
  archer: '#27ae60',
  warrior: '#e67e22',
};

const ClassSelect: React.FC<ClassSelectProps> = ({ onSelect, onBack }) => {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-[#1a0e0a] text-[#f5e6d3] select-none p-4">
      <h2 className="text-4xl md:text-5xl font-bold mb-2" style={{ fontFamily: 'Georgia, serif', textShadow: '0 0 20px rgba(241,196,15,0.3)' }}>
        Escolha sua Classe
      </h2>
      <div className="w-48 h-px bg-gradient-to-r from-transparent via-[#5a3a28] to-transparent mb-8" />

      <div className="flex flex-col md:flex-row gap-6 mb-8">
        {classes.map(cls => (
          <button
            key={cls.id}
            onClick={() => onSelect(cls.id)}
            className="flex flex-col items-center p-6 rounded-xl border-2 transition-all duration-300 hover:scale-105 active:scale-95 w-64"
            style={{
              borderColor: classColors[cls.id],
              background: `linear-gradient(180deg, rgba(42,24,16,0.9) 0%, rgba(26,14,10,0.95) 100%)`,
              boxShadow: `0 0 20px ${classColors[cls.id]}33`,
            }}
            onMouseEnter={e => {
              (e.currentTarget as HTMLElement).style.boxShadow = `0 0 30px ${classColors[cls.id]}66`;
            }}
            onMouseLeave={e => {
              (e.currentTarget as HTMLElement).style.boxShadow = `0 0 20px ${classColors[cls.id]}33`;
            }}
          >
            <span className="text-5xl mb-3">{cls.icon}</span>
            <h3 className="text-2xl font-bold mb-2" style={{ color: classColors[cls.id], fontFamily: 'Georgia, serif' }}>
              {cls.name}
            </h3>
            <p className="text-sm text-[#8a7a6a] text-center mb-3">{cls.desc}</p>
            <p className="text-xs font-mono" style={{ color: classColors[cls.id] }}>{cls.stats}</p>
          </button>
        ))}
      </div>

      <button
        onClick={onBack}
        className="text-[#8a7a6a] hover:text-[#f5e6d3] transition-colors text-lg"
        style={{ fontFamily: 'Georgia, serif' }}
      >
        ← Voltar
      </button>
    </div>
  );
};

export default ClassSelect;
