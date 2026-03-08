import React from 'react';
import { LeaderboardEntry, PlayerClass } from '../../game/types';

interface LeaderboardProps {
  onBack: () => void;
}

const classIcons: Record<PlayerClass, string> = { mage: '🔮', archer: '🏹', warrior: '⚔️' };

const Leaderboard: React.FC<LeaderboardProps> = ({ onBack }) => {
  const entries: LeaderboardEntry[] = JSON.parse(localStorage.getItem('medieval-wars-lb') || '[]');

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-[#1a0e0a] text-[#f5e6d3] select-none p-4">
      <h2 className="text-4xl font-bold mb-2 text-[#f1c40f]" style={{ fontFamily: 'Georgia, serif', textShadow: '0 0 20px rgba(241,196,15,0.4)' }}>
        🏆 Leaderboard
      </h2>
      <div className="w-48 h-px bg-gradient-to-r from-transparent via-[#5a3a28] to-transparent mb-6" />

      <div className="w-full max-w-md">
        {entries.length === 0 ? (
          <p className="text-center text-[#8a7a6a] text-lg">Nenhuma pontuação ainda. Jogue para aparecer aqui!</p>
        ) : (
          <div className="space-y-2">
            {entries.slice(0, 15).map((e, i) => (
              <div key={i} className={`flex items-center justify-between p-3 rounded-lg border ${i < 3 ? 'border-[#f1c40f] bg-[#2a1810]' : 'border-[#5a3a28] bg-[#1a0e0a]'}`}>
                <div className="flex items-center gap-3">
                  <span className={`text-lg font-bold w-8 ${i === 0 ? 'text-[#f1c40f]' : i === 1 ? 'text-[#bdc3c7]' : i === 2 ? 'text-[#cd6133]' : 'text-[#5a3a28]'}`}>
                    #{i + 1}
                  </span>
                  <span>{classIcons[e.class]}</span>
                  <span className="font-bold">{e.name}</span>
                </div>
                <div className="text-right">
                  <div className="text-[#f1c40f] font-bold font-mono">{e.score.toLocaleString()}</div>
                  <div className="text-xs text-[#8a7a6a]">Onda {e.wave}</div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <button
        onClick={onBack}
        className="mt-8 text-[#8a7a6a] hover:text-[#f5e6d3] transition-colors text-lg"
        style={{ fontFamily: 'Georgia, serif' }}
      >
        ← Voltar
      </button>
    </div>
  );
};

export default Leaderboard;
