import React, { useMemo } from 'react';
import { Upgrade } from '../../game/types';
import { getRandomUpgrades } from '../../game/upgrades';

interface UpgradeScreenProps {
  wave: number;
  onSelect: (upgrade: Upgrade) => void;
}

const UpgradeScreen: React.FC<UpgradeScreenProps> = ({ wave, onSelect }) => {
  const upgrades = useMemo(() => getRandomUpgrades(3), [wave]);

  return (
    <div className="absolute inset-0 flex flex-col items-center justify-center bg-black/70 z-20 select-none p-4">
      <div className="text-[#f1c40f] text-3xl md:text-4xl font-bold mb-2" style={{ fontFamily: 'Georgia, serif', textShadow: '0 0 20px rgba(241,196,15,0.5)' }}>
        Onda {wave} Completa! 🎉
      </div>
      <p className="text-[#8a7a6a] mb-8 text-lg">Escolha uma melhoria:</p>

      <div className="flex flex-col md:flex-row gap-4">
        {upgrades.map(u => (
          <button
            key={u.id}
            onClick={() => onSelect(u)}
            className="flex flex-col items-center p-6 rounded-xl border-2 border-[#5a3a28] bg-[#2a1810] hover:border-[#f1c40f] hover:bg-[#3a2820] transition-all duration-200 hover:scale-105 active:scale-95 w-56"
            style={{ boxShadow: '0 4px 20px rgba(0,0,0,0.5)' }}
          >
            <span className="text-4xl mb-3">{u.icon}</span>
            <h3 className="text-xl font-bold text-[#f1c40f] mb-2" style={{ fontFamily: 'Georgia, serif' }}>
              {u.name}
            </h3>
            <p className="text-sm text-[#8a7a6a] text-center">{u.description}</p>
          </button>
        ))}
      </div>
    </div>
  );
};

export default UpgradeScreen;
