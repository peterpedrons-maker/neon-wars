import React from 'react';
import { playBack, playHover } from '../../game/audio';
import { LeaderboardEntry, ShipType } from '../../game/types';

interface LeaderboardProps {
  onBack: () => void;
}

const shipIcons: Record<ShipType, string> = { phantom: '👻', interceptor: '⚡', titan: '💥', spectre: '🌀', valkyrie: '🦅', juggernaut: '🛡️' };

const Leaderboard: React.FC<LeaderboardProps> = ({ onBack }) => {
  const entries: LeaderboardEntry[] = JSON.parse(localStorage.getItem('neon-wars-lb') || '[]');

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-[#000008] text-[#e0e8ff] select-none p-4">
      <h2 className="text-4xl font-bold mb-2 font-mono" style={{ color: '#ffff00', textShadow: '0 0 20px rgba(255,255,0,0.4)' }}>
        🏆 Leaderboard
      </h2>
      <div className="w-48 h-px bg-gradient-to-r from-transparent via-[#ffff00] to-transparent mb-6" />

      <div className="w-full max-w-md">
        {entries.length === 0 ? (
          <p className="text-center text-[#6080aa] text-lg font-mono">Nenhum score ainda. Jogue para aparecer aqui!</p>
        ) : (
          <div className="space-y-2">
            {entries.slice(0, 15).map((e, i) => (
              <div key={i} className={`flex items-center justify-between p-3 rounded-lg border font-mono ${i < 3 ? 'border-[#ffff0055]' : 'border-[#203050]'}`}
                   style={{ background: i < 3 ? 'rgba(255,255,0,0.03)' : 'rgba(0,0,20,0.5)' }}>
                <div className="flex items-center gap-3">
                  <span className={`text-lg font-bold w-8 ${i === 0 ? 'text-[#ffff00]' : i === 1 ? 'text-[#c0c0c0]' : i === 2 ? 'text-[#ff6b00]' : 'text-[#203050]'}`}>
                    #{i + 1}
                  </span>
                  <span>{shipIcons[e.class]}</span>
                  <span className="font-bold">{e.name}</span>
                </div>
                <div className="text-right">
                  <div className="font-bold font-mono" style={{ color: '#ffff00' }}>{e.score.toLocaleString()}</div>
                  <div className="text-xs text-[#6080aa]">Wave {e.wave}</div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <button
        onClick={() => { playBack(); onBack(); }}
        onMouseEnter={playHover}
        className="mt-8 text-[#6080aa] hover:text-[#0ff] transition-colors text-lg font-mono"
      >
        ← Voltar
      </button>
    </div>
  );
};

export default Leaderboard;
