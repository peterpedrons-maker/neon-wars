import React, { useMemo } from 'react';
import { Ability, getRandomAbilities } from '../../game/abilities';

interface LevelUpScreenProps {
  level: number;
  abilityLevels: Record<string, number>;
  onSelect: (ability: Ability) => void;
}

const LevelUpScreen: React.FC<LevelUpScreenProps> = ({ level, abilityLevels, onSelect }) => {
  const abilities = useMemo(() => getRandomAbilities(3, abilityLevels), [level]);

  return (
    <div className="absolute inset-0 flex flex-col items-center justify-center bg-black/80 z-20 select-none p-4">
      <div
        className="text-3xl md:text-4xl font-bold mb-1 font-mono animate-pulse"
        style={{ color: '#ffff00', textShadow: '0 0 20px rgba(255,255,0,0.6)' }}
      >
        LEVEL UP! 🎉
      </div>
      <p className="text-[#6080aa] mb-2 text-sm font-mono">Nível {level}</p>
      <p className="text-[#8090bb] mb-6 text-base font-mono">Escolha uma habilidade:</p>

      <div className="flex flex-col md:flex-row gap-4">
        {abilities.map(a => {
          const currentLv = abilityLevels[a.id] || 0;
          return (
            <button
              key={a.id}
              onClick={() => onSelect(a)}
              className="flex flex-col items-center p-5 rounded-xl border transition-all duration-200 hover:scale-105 active:scale-95 w-52 font-mono"
              style={{
                borderColor: 'rgba(0,255,255,0.2)',
                background: 'rgba(0,0,20,0.95)',
                boxShadow: '0 4px 20px rgba(0,0,0,0.5)',
              }}
              onMouseEnter={e => {
                (e.currentTarget as HTMLElement).style.borderColor = '#0ff';
                (e.currentTarget as HTMLElement).style.boxShadow = '0 0 25px rgba(0,255,255,0.3)';
              }}
              onMouseLeave={e => {
                (e.currentTarget as HTMLElement).style.borderColor = 'rgba(0,255,255,0.2)';
                (e.currentTarget as HTMLElement).style.boxShadow = '0 4px 20px rgba(0,0,0,0.5)';
              }}
            >
              <span className="text-4xl mb-2">{a.icon}</span>
              <h3 className="text-lg font-bold mb-1" style={{ color: '#0ff' }}>
                {a.name}
              </h3>
              <p className="text-xs text-[#6080aa] text-center mb-2">{a.description}</p>
              <div className="flex gap-1">
                {Array.from({ length: a.maxLevel }).map((_, i) => (
                  <div
                    key={i}
                    className="w-2 h-2 rounded-full"
                    style={{
                      background: i <= currentLv ? '#0ff' : '#1a2040',
                      boxShadow: i <= currentLv ? '0 0 4px #0ff' : 'none',
                    }}
                  />
                ))}
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
};

export default LevelUpScreen;
