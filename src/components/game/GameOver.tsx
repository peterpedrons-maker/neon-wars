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
      <div className="text-[#e74c3c] text-5xl md:text-6xl font-bold mb-4" style={{ fontFamily: 'Georgia, serif', textShadow: '0 0 30px rgba(231,76,60,0.5)' }}>
        💀 Derrota
      </div>

      <div className="bg-[#2a1810] border-2 border-[#5a3a28] rounded-xl p-6 mb-6 text-center">
        <div className="text-[#f1c40f] text-4xl font-bold font-mono mb-3">{score.toLocaleString()}</div>
        <div className="flex gap-6 text-[#8a7a6a]">
          <div>Onda <span className="text-[#f5e6d3] font-bold">{wave}</span></div>
          <div>Inimigos <span className="text-[#f5e6d3] font-bold">{enemiesKilled}</span></div>
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
            className="px-4 py-2 rounded-lg bg-[#1a0e0a] border-2 border-[#5a3a28] text-[#f5e6d3] placeholder-[#5a3a28] focus:border-[#f1c40f] outline-none text-center w-48"
          />
          <button
            onClick={saveScore}
            className="px-4 py-2 rounded-lg bg-[#f1c40f] text-[#1a0e0a] font-bold hover:bg-[#f39c12] transition-colors"
          >
            Salvar
          </button>
        </div>
      ) : (
        <div className="text-[#27ae60] mb-6 font-bold">✅ Pontuação salva!</div>
      )}

      <div className="flex gap-4">
        <button
          onClick={onRestart}
          className="py-3 px-8 text-lg font-bold rounded-lg bg-gradient-to-r from-[#8B4513] to-[#A0522D] hover:from-[#A0522D] hover:to-[#CD853F] text-[#f5e6d3] border-2 border-[#CD853F] transition-all duration-200 hover:scale-105 active:scale-95"
          style={{ fontFamily: 'Georgia, serif' }}
        >
          ⚔️ Jogar Novamente
        </button>
        <button
          onClick={onMenu}
          className="py-3 px-8 text-lg font-bold rounded-lg bg-[#2a1810] hover:bg-[#3a2820] text-[#8a7a6a] border-2 border-[#5a3a28] transition-all duration-200"
          style={{ fontFamily: 'Georgia, serif' }}
        >
          Menu
        </button>
      </div>
    </div>
  );
};

export default GameOver;
