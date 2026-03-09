import React, { useMemo } from 'react';
import { Upgrade } from '../../game/types';
import { getRandomUpgrades } from '../../game/upgrades';
import { UPGRADE_ICONS } from '../../game/icons';

interface UpgradeScreenProps {
  wave: number;
  onSelect: (upgrade: Upgrade) => void;
}

const UpgradeScreen: React.FC<UpgradeScreenProps> = ({ wave, onSelect }) => {
  const upgrades = useMemo(() => getRandomUpgrades(3), [wave]);

  return (
    <div className="absolute inset-0 flex flex-col items-center justify-center bg-black/75 z-20 select-none p-4">
      <div className="text-3xl md:text-4xl font-bold mb-2 font-mono" style={{ color: '#ffff00', textShadow: '0 0 20px rgba(255,255,0,0.5)' }}>
        Wave {wave} Completa! 🎉
      </div>
      <p className="text-[#6080aa] mb-8 text-lg font-mono">Escolha um upgrade:</p>

      <div className="flex flex-col md:flex-row gap-4">
        {upgrades.map(u => (
          <button
            key={u.id}
            onClick={() => onSelect(u)}
            className="flex flex-col items-center p-6 rounded-xl border transition-all duration-200 hover:scale-105 active:scale-95 w-56 font-mono"
            style={{
              borderColor: 'rgba(0,255,255,0.2)',
              background: 'rgba(0,0,20,0.9)',
              boxShadow: '0 4px 20px rgba(0,0,0,0.5)',
            }}
            onMouseEnter={e => {
              (e.currentTarget as HTMLElement).style.borderColor = '#0ff';
              (e.currentTarget as HTMLElement).style.boxShadow = '0 0 25px rgba(0,255,255,0.2)';
            }}
            onMouseLeave={e => {
              (e.currentTarget as HTMLElement).style.borderColor = 'rgba(0,255,255,0.2)';
              (e.currentTarget as HTMLElement).style.boxShadow = '0 4px 20px rgba(0,0,0,0.5)';
            }}
          >
            <span className="text-4xl mb-3">{u.icon}</span>
            <h3 className="text-xl font-bold mb-2" style={{ color: '#0ff' }}>
              {u.name}
            </h3>
            <p className="text-sm text-[#6080aa] text-center">{u.description}</p>
          </button>
        ))}
      </div>
    </div>
  );
};

export default UpgradeScreen;
