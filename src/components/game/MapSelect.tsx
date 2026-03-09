import React, { useState } from 'react';
import { ALL_MAPS } from '../../game/maps';
import type { MapDifficulty } from '../../game/maps';
import { playClick, playHover, playBack } from '../../game/audio';

interface MapSelectProps {
  unlockedMaps: string[];
  onSelect: (mapId: string, difficulty: MapDifficulty) => void;
  onBack: () => void;
}

const mapOrder = ['neon-grid', 'inferno', 'void', 'crystal', 'singularity', 'foundry'];

const difficultyOptions: Array<{ id: MapDifficulty; label: string; hint: string }> = [
  { id: 'easy', label: 'Fácil', hint: 'Mais tranquilo' },
  { id: 'medium', label: 'Médio', hint: 'Padrão' },
  { id: 'hard', label: 'Difícil', hint: 'Bem puxado' },
];

const MapSelect: React.FC<MapSelectProps> = ({ unlockedMaps, onSelect, onBack }) => {
  const [difficulty, setDifficulty] = useState<MapDifficulty>('medium');

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-[#000008] text-[#e0e8ff] select-none p-4">
      <h2
        className="text-3xl md:text-4xl font-bold mb-4"
        style={{ fontFamily: 'Orbitron, monospace', color: '#0ff', textShadow: '0 0 20px rgba(0,255,255,0.4)' }}
      >
        Selecione o Mapa
      </h2>

      {/* Difficulty selector */}
      <div className="flex items-center gap-2 mb-8">
        {difficultyOptions.map(opt => (
          <button
            key={opt.id}
            onClick={() => { playClick(); setDifficulty(opt.id); }}
            onMouseEnter={playHover}
            className="px-4 py-2 rounded-lg font-mono text-sm font-bold border transition-all duration-200"
            style={{
              background: difficulty === opt.id ? 'rgba(255,255,255,0.08)' : 'rgba(255,255,255,0.03)',
              borderColor: difficulty === opt.id ? '#ffff00' : 'rgba(255,255,255,0.12)',
              color: difficulty === opt.id ? '#ffff00' : '#6080aa',
              boxShadow: difficulty === opt.id ? '0 0 18px rgba(255,255,0,0.18)' : 'none',
            }}
            title={opt.hint}
          >
            {opt.label}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
        {mapOrder.map(id => {
          const map = ALL_MAPS[id];
          if (!map) return null;
          const unlocked = unlockedMaps.includes(id);

          return (
            <button
              key={id}
              onClick={() => { if (unlocked) { playClick(); onSelect(id, difficulty); } }}
              onMouseEnter={() => { if (unlocked) playHover(); }}
              disabled={!unlocked}
              className="flex flex-col items-center p-6 rounded-xl border transition-all duration-200 hover:scale-105 active:scale-95 w-64 font-mono disabled:opacity-40 disabled:hover:scale-100"
              style={{
                borderColor: unlocked ? map.borderColor + '40' : 'rgba(100,100,100,0.2)',
                background: unlocked ? map.bgColor : 'rgba(20,20,30,0.8)',
                boxShadow: unlocked ? `0 4px 20px ${map.borderColor}20` : 'none',
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
        onClick={() => { playBack(); onBack(); }}
        onMouseEnter={playHover}
        className="py-2 px-6 text-sm font-bold rounded-lg text-[#6080aa] border border-[#6080aa]/30 transition-all duration-200 hover:border-[#0ff] hover:text-[#0ff] font-mono"
        style={{ background: 'rgba(0,255,255,0.03)' }}
      >
        ← Voltar
      </button>
    </div>
  );
};

export default MapSelect;