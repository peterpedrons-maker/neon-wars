import React, { useEffect } from 'react';
import { RunStats, Milestone } from '../../game/meta';
import { initAudio, startMenuMusic, stopMenuMusic, playClick, playHover } from '../../game/audio';
import { UI_ICONS } from '../../game/icons';

interface MainMenuProps {
  plasma: number;
  stats: RunStats;
  milestones: Milestone[];
  onPlay: () => void;
  onLeaderboard: () => void;
  onHowToPlay: () => void;
  onShop: () => void;
  onMultiplayer: () => void;
  onAchievements: () => void;
  username?: string;
  onLogout?: () => void;
}

const MainMenu: React.FC<MainMenuProps> = ({ plasma, stats, milestones, onPlay, onLeaderboard, onHowToPlay, onShop, onMultiplayer, onAchievements, username, onLogout }) => {
  useEffect(() => {
    initAudio();
    startMenuMusic();
    return () => { stopMenuMusic(); };
  }, []);

  const handleClick = (fn: () => void) => { playClick(); fn(); };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-[#000008] text-[#e0e8ff] select-none">
      <div className="mb-8 text-center">
        <h1 className="text-6xl md:text-8xl font-bold tracking-wider mb-2"
            style={{ fontFamily: 'Orbitron, monospace', textShadow: '0 0 40px rgba(0,255,255,0.4), 0 0 80px rgba(0,255,255,0.15)' }}>
          <span style={{ color: '#0ff' }}>NEON</span> <span style={{ color: '#ff1493' }}>WARS</span>
        </h1>
        <p className="text-xl md:text-2xl text-[#6080aa] font-mono">Arena de Sobrevivência Cósmica</p>
      </div>

      <div className="flex items-center gap-2 mb-4 py-2 px-5 rounded-lg" style={{ background: 'rgba(191,90,242,0.1)', border: '1px solid rgba(191,90,242,0.25)' }}>
        <img src={UI_ICONS.plasma} alt="Plasma" className="w-6 h-6 object-contain" />
        <span className="font-mono font-bold text-lg" style={{ color: '#bf5af2' }}>{plasma}</span>
        <span className="font-mono text-xs text-[#6080aa]">Plasma</span>
      </div>

      {stats.totalRuns > 0 && (
        <div className="flex gap-4 mb-6 text-xs font-mono text-[#405070]">
          <span>Runs: {stats.totalRuns}</span>
          <span>Kills: {stats.totalKills}</span>
          <span>Best Wave: {stats.highestWave}</span>
          <span>Best Score: {stats.highestScore.toLocaleString()}</span>
        </div>
      )}

      {milestones.length > 0 && (
        <div className="flex gap-1 mb-6">
          {milestones.slice(-6).map(m => (
            <div key={m.id} title={m.name} className="text-lg cursor-default">{m.icon}</div>
          ))}
          {milestones.length > 6 && (
            <span className="text-xs text-[#405070] font-mono self-center ml-1">+{milestones.length - 6}</span>
          )}
        </div>
      )}

      <div className="w-48 h-px bg-gradient-to-r from-transparent via-[#0ff] to-transparent mb-8" />

      <div className="flex flex-col gap-3 w-72">
        <button onClick={() => handleClick(onPlay)} onMouseEnter={playHover}
          className="py-4 px-8 text-xl font-bold rounded-lg text-white border transition-all duration-200 hover:scale-105 active:scale-95 font-mono"
          style={{ background: 'linear-gradient(135deg, rgba(0,229,255,0.2), rgba(191,90,242,0.2))', borderColor: '#0ff', boxShadow: '0 0 20px rgba(0,255,255,0.3), inset 0 0 15px rgba(0,255,255,0.1)' }}>
          🚀 Jogar
        </button>
        <button onClick={() => handleClick(onMultiplayer)} onMouseEnter={playHover}
          className="py-3 px-8 text-lg font-bold rounded-lg text-[#39ff14] border border-[#39ff14]/30 transition-all hover:border-[#39ff14] hover:shadow-[0_0_15px_rgba(57,255,20,0.3)] font-mono"
          style={{ background: 'rgba(57,255,20,0.05)' }}>
          🎮 Multiplayer Coop
        </button>
        <button onClick={() => handleClick(onShop)} onMouseEnter={playHover}
          className="py-3 px-8 text-lg font-bold rounded-lg text-[#bf5af2] border border-[#bf5af2]/30 transition-all hover:border-[#bf5af2] hover:shadow-[0_0_15px_rgba(191,90,242,0.3)] font-mono"
          style={{ background: 'rgba(191,90,242,0.05)' }}>
          ⚡ Loja de Plasma
        </button>
        <button onClick={() => handleClick(onAchievements)} onMouseEnter={playHover}
          className="py-3 px-8 text-lg font-bold rounded-lg text-[#ffd700] border border-[#ffd700]/30 transition-all hover:border-[#ffd700] hover:shadow-[0_0_15px_rgba(255,215,0,0.3)] font-mono"
          style={{ background: 'rgba(255,215,0,0.05)' }}>
          🏆 Conquistas
        </button>
        <button onClick={() => handleClick(onLeaderboard)} onMouseEnter={playHover}
          className="py-2.5 px-8 text-base font-bold rounded-lg text-[#ffff00] border border-[#ffff00]/30 transition-all hover:border-[#ffff00] hover:shadow-[0_0_15px_rgba(255,255,0,0.2)] font-mono"
          style={{ background: 'rgba(255,255,0,0.05)' }}>
          📊 Leaderboard
        </button>
        <button onClick={() => handleClick(onHowToPlay)} onMouseEnter={playHover}
          className="py-2.5 px-8 text-base font-bold rounded-lg text-[#6080aa] border border-[#6080aa]/30 transition-all hover:border-[#0ff] hover:text-[#0ff] font-mono"
          style={{ background: 'rgba(0,255,255,0.03)' }}>
          📡 Como Jogar
        </button>
      </div>

      {username && (
        <div className="mt-4 flex items-center gap-3">
          <span className="text-xs font-mono text-[#6080aa]">👤 {username}</span>
          {onLogout && (
            <button onClick={() => { playClick(); onLogout(); }}
              className="text-xs font-mono text-[#ff4060] hover:text-[#ff6080] transition-colors">
              Sair
            </button>
          )}
        </div>
      )}
      <div className="mt-4 text-sm text-[#203050] font-mono">WASD + Mouse • Touch Friendly</div>
    </div>
  );
};

export default MainMenu;
