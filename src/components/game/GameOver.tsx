import React, { useState } from 'react';
import { ShipType, LeaderboardEntry } from '../../game/types';
import { Milestone } from '../../game/meta';

interface GameOverProps {
  score: number;
  wave: number;
  enemiesKilled: number;
  playerClass: ShipType;
  plasmaEarned: number;
  newMilestones: Milestone[];
  onRestart: () => void;
  onMenu: () => void;
}

const GameOver: React.FC<GameOverProps> = ({ score, wave, enemiesKilled, playerClass, plasmaEarned, newMilestones, onRestart, onMenu }) => {
  const [name, setName] = useState('');
  const [saved, setSaved] = useState(false);

  const saveScore = () => {
    if (!name.trim()) return;
    const entries: LeaderboardEntry[] = JSON.parse(localStorage.getItem('neon-wars-lb') || '[]');
    entries.push({ name: name.trim(), score, wave, class: playerClass, date: new Date().toISOString() });
    entries.sort((a, b) => b.score - a.score);
    localStorage.setItem('neon-wars-lb', JSON.stringify(entries.slice(0, 50)));
    setSaved(true);
  };

  return (
    <div className="absolute inset-0 flex flex-col items-center justify-center bg-black/85 z-20 select-none p-4">
      <div className="text-5xl md:text-6xl font-bold mb-4 font-mono" style={{ color: '#ff0040', textShadow: '0 0 30px rgba(255,0,64,0.5)' }}>
        DESTROYED
      </div>

      <div className="rounded-xl p-6 mb-4 text-center border" style={{ background: 'rgba(0,0,20,0.9)', borderColor: 'rgba(0,255,255,0.2)' }}>
        <div className="text-4xl font-bold font-mono mb-3" style={{ color: '#ffff00', textShadow: '0 0 15px rgba(255,255,0,0.4)' }}>{score.toLocaleString()}</div>
        <div className="flex gap-6 text-[#6080aa] font-mono mb-3">
          <div>Wave <span className="text-[#0ff] font-bold">{wave}</span></div>
          <div>Kills <span className="text-[#39ff14] font-bold">{enemiesKilled}</span></div>
        </div>
        {/* Plasma earned */}
        <div className="flex items-center justify-center gap-2 py-2 px-4 rounded-lg" style={{ background: 'rgba(191,90,242,0.15)', border: '1px solid rgba(191,90,242,0.3)' }}>
          <span className="text-xl">⚡</span>
          <span className="font-mono font-bold" style={{ color: '#bf5af2' }}>+{plasmaEarned} Plasma</span>
        </div>
      </div>

      {/* New milestones */}
      {newMilestones.length > 0 && (
        <div className="mb-4 flex flex-col gap-2">
          {newMilestones.map(m => (
            <div key={m.id} className="flex items-center gap-3 py-2 px-4 rounded-lg animate-pulse" style={{ background: 'rgba(255,255,0,0.1)', border: '1px solid rgba(255,255,0,0.3)' }}>
              <span className="text-2xl">{m.icon}</span>
              <div>
                <div className="font-mono font-bold text-sm" style={{ color: '#ffff00' }}>🏆 {m.name}</div>
                <div className="font-mono text-xs text-[#6080aa]">Desbloqueado: {m.reward.name}</div>
              </div>
            </div>
          ))}
        </div>
      )}

      {!saved ? (
        <div className="flex gap-2 mb-6">
          <input
            type="text"
            value={name}
            onChange={e => setName(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && saveScore()}
            placeholder="Callsign..."
            maxLength={15}
            className="px-4 py-2 rounded-lg bg-[#000010] border text-[#e0e8ff] placeholder-[#203050] focus:border-[#0ff] outline-none text-center w-48 font-mono"
            style={{ borderColor: 'rgba(0,255,255,0.3)' }}
          />
          <button
            onClick={saveScore}
            className="px-4 py-2 rounded-lg font-bold font-mono transition-colors"
            style={{ background: 'rgba(255,255,0,0.2)', color: '#ffff00', border: '1px solid rgba(255,255,0,0.4)' }}
          >
            Salvar
          </button>
        </div>
      ) : (
        <div className="mb-6 font-bold font-mono" style={{ color: '#39ff14', textShadow: '0 0 10px rgba(57,255,20,0.4)' }}>✅ Score saved!</div>
      )}

      <div className="flex gap-4">
        <button
          onClick={onRestart}
          className="py-3 px-8 text-lg font-bold rounded-lg text-white border transition-all duration-200 hover:scale-105 active:scale-95 font-mono"
          style={{
            background: 'linear-gradient(135deg, rgba(0,229,255,0.2), rgba(191,90,242,0.2))',
            borderColor: '#0ff',
            boxShadow: '0 0 15px rgba(0,255,255,0.2)',
          }}
        >
          🚀 Jogar Novamente
        </button>
        <button
          onClick={onMenu}
          className="py-3 px-8 text-lg font-bold rounded-lg text-[#6080aa] border border-[#6080aa]/30 transition-all duration-200 hover:border-[#0ff] hover:text-[#0ff] font-mono"
          style={{ background: 'rgba(0,255,255,0.03)' }}
        >
          Menu
        </button>
      </div>
    </div>
  );
};

export default GameOver;
