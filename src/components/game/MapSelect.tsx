import React from 'react';
import { ALL_MAPS, GameMap } from '../../game/maps';

interface MapSelectProps {
  unlockedMaps: string[];
  onSelect: (mapId: string) => void;
  onBack: () => void;
}

const mapOrder = ['neon-grid', 'inferno', 'void', 'crystal'];

const MapSelect: React.FC<MapSelectProps> = ({ unlockedMaps, onSelect, onBack }) => {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-[#000008] text-[#e0e8ff] select-none p-4">
      <h2
        className="text-3xl md:text-4xl font-bold mb-8"
        style={{ fontFamily: 'Orbitron, monospace', color: '#0ff', textShadow: '0 0 20px rgba(0,255,255,0.4)' }}
      >
        Selecione o Mapa
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
        {mapOrder.map(id => {
          const map = ALL_MAPS[id];
          if (!map) return null;
          const unlocked = unlockedMaps.includes(id);

          return (
            <button
              key={id}
              onClick={() => unlocked && onSelect(id)}
              disabled={!unlocked}
              className="flex flex-col items-center p-6 rounded-xl border transition-all duration-200 hover:scale-105 active:scale-95 w-64 font-mono disabled:opacity-40 disabled:hover:scale-100"
              style={{
                borderColor: unlocked ? map.borderColor + '40' : 'rgba(100,100,100,0.2)',
                background: unlocked ? map.bgColor : 'rgba(20,20,30,0.8)',
                boxShadow: unlocked ? `0 4px 20px ${map.borderColor}20` : 'none',
              }}
              onMouseEnter={e => {
                if (!unlocked) return;
                (e.currentTarget as HTMLElement).style.borderColor = map.borderColor;
                (e.currentTarget as HTMLElement).style.boxShadow = `0 0 25px ${map.borderColor}40`;
              }}
              onMouseLeave={e => {
                (e.currentTarget as HTMLElement).style.borderColor = unlocked ? map.borderColor + '40' : 'rgba(100,100,100,0.2)';
                (e.currentTarget as HTMLElement).style.boxShadow = unlocked ? `0 4px 20px ${map.borderColor}20` : 'none';
              }}
            >
              <span className="text-4xl mb-2">{unlocked ? map.icon : '🔒'}</span>
              <h3 className="text-lg font-bold mb-1" style={{ color: unlocked ? map.borderColor : '#404060' }}>
                {map.name}
              </h3>
              <p className="text-xs text-[#6080aa] text-center">
                {unlocked ? map.description : 'Complete milestones para desbloquear'}
              </p>
              {unlocked && map.hazards.length > 0 && (
                <div className="mt-2 text-[10px] px-2 py-0.5 rounded" style={{ background: 'rgba(255,100,0,0.15)', color: '#ff6b00' }}>
                  ⚠️ Hazards ativos
                </div>
              )}
            </button>
          );
        })}
      </div>

      <button
        onClick={onBack}
        className="py-2 px-6 text-sm font-bold rounded-lg text-[#6080aa] border border-[#6080aa]/30 transition-all duration-200 hover:border-[#0ff] hover:text-[#0ff] font-mono"
        style={{ background: 'rgba(0,255,255,0.03)' }}
      >
        ← Voltar
      </button>
    </div>
  );
};

export default MapSelect;
