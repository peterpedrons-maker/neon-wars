import React, { useState } from 'react';
import { PlayerClass, LeaderboardEntry } from '../../game/types';

interface GameOverProps {
  score: number;
  wave: number;
  enemiesKilled: number;
  playerClass: PlayerClass;
  onRestart: () => void;
  onMenu: () => void;
}

const GameOver: React.FC<GameOverProps> = ({ score, wave, enemiesKilled, playerClass, onRestart, onMenu }) => {
  const [name, setName] = useState('');
  const [saved, setSaved] = useState(false);

  const saveScore = () => {
    if (!name.trim()) return;
    const entries: LeaderboardEntry[] = JSON.parse(localStorage.getItem('medieval-wars-lb') || '[]');
    entries.push({ name: name.trim(), score, wave, class: playerClass, date: new Date().toISOString() });
    entries.sort((a, b) => b.score - a.score);
    localStorage.setItem('medieval-wars-lb', JSON.stringify(entries.slice(0, 50)));
    setSaved(true);
  };

  return (
    <div className="absolute inset-0 flex flex-col items-center justify-center bg-black/80 z-20 select-none p-4">
      <div className="text-[#ef4444] text-5xl md:text-6xl font-bold mb-4" style={{ fontFamily: 'Georgia, serif', textShadow: '0 0 30px rgba(239,68,68,0.5)' }}>
        💀 Derrota
      </div>

      <div className="bg-[#1e1a2e] border-2 border-[#4a3a6e] rounded-xl p-6 mb-6 text-center">
        <div className="text-[#fbbf24] text-4xl font-bold font-mono mb-3">{score.toLocaleString()}</div>
        <div className="flex gap-6 text-[#94a3b8]">
          <div>Onda <span className="text-[#f1f5f9] font-bold">{wave}</span></div>
          <div>Inimigos <span className="text-[#f1f5f9] font-bold">{enemiesKilled}</span></div>
        </div>
      </div>

      {!saved ? (
        <div className="flex gap-2 mb-6">
          <input
            type="text"
            value={name}
            onChange={e => setName(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && saveScore()}
            placeholder="Seu nome..."
            maxLength={15}
            className="px-4 py-2 rounded-lg bg-[#08061a] border-2 border-[#4a3a6e] text-[#f1f5f9] placeholder-[#4a3a6e] focus:border-[#fbbf24] outline-none text-center w-48"
          />
          <button
            onClick={saveScore}
            className="px-4 py-2 rounded-lg bg-[#fbbf24] text-[#08061a] font-bold hover:bg-[#f59e0b] transition-colors"
          >
            Salvar
          </button>
        </div>
      ) : (
        <div className="text-[#34d399] mb-6 font-bold">✅ Pontuação salva!</div>
      )}

      <div className="flex gap-4">
        <button
          onClick={onRestart}
          className="py-3 px-8 text-lg font-bold rounded-lg bg-gradient-to-r from-[#7c3aed] to-[#a855f7] hover:from-[#8b5cf6] hover:to-[#c084fc] text-white border-2 border-[#a855f7] transition-all duration-200 hover:scale-105 active:scale-95"
          style={{ fontFamily: 'Georgia, serif' }}
        >
          ⚔️ Jogar Novamente
        </button>
        <button
          onClick={onMenu}
          className="py-3 px-8 text-lg font-bold rounded-lg bg-[#1e1a2e] hover:bg-[#2a2540] text-[#94a3b8] border-2 border-[#4a3a6e] transition-all duration-200"
          style={{ fontFamily: 'Georgia, serif' }}
        >
          Menu
        </button>
      </div>
    </div>
  );
};

export default GameOver;
