import React from 'react';
import { ShipType } from '../../game/types';

interface MainMenuProps {
  onPlay: () => void;
  onLeaderboard: () => void;
  onHowToPlay: () => void;
}

const MainMenu: React.FC<MainMenuProps> = ({ onPlay, onLeaderboard, onHowToPlay }) => {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-[#000008] text-[#e0e8ff] select-none">
      {/* Title */}
      <div className="mb-12 text-center">
        <h1 className="text-6xl md:text-8xl font-bold tracking-wider mb-2"
            style={{ fontFamily: 'Orbitron, monospace', textShadow: '0 0 40px rgba(0,255,255,0.4), 0 0 80px rgba(0,255,255,0.15)' }}>
          <span style={{ color: '#0ff' }}>NEON</span> <span style={{ color: '#ff1493' }}>WARS</span>
        </h1>
        <p className="text-xl md:text-2xl text-[#6080aa] font-mono">
          Arena de Sobrevivência Cósmica
        </p>
      </div>

      {/* Decorative divider */}
      <div className="w-48 h-px bg-gradient-to-r from-transparent via-[#0ff] to-transparent mb-10" />

      {/* Menu buttons */}
      <div className="flex flex-col gap-4 w-72">
        <button
          onClick={onPlay}
          className="py-4 px-8 text-xl font-bold rounded-lg text-white border transition-all duration-200 hover:scale-105 active:scale-95 font-mono"
          style={{
            background: 'linear-gradient(135deg, rgba(0,229,255,0.2), rgba(191,90,242,0.2))',
            borderColor: '#0ff',
            boxShadow: '0 0 20px rgba(0,255,255,0.3), inset 0 0 15px rgba(0,255,255,0.1)',
          }}
        >
          🚀 Jogar
        </button>
        <button
          onClick={onLeaderboard}
          className="py-3 px-8 text-lg font-bold rounded-lg text-[#ffff00] border border-[#ffff00]/30 transition-all duration-200 hover:border-[#ffff00] hover:shadow-[0_0_15px_rgba(255,255,0,0.2)] font-mono"
          style={{ background: 'rgba(255,255,0,0.05)' }}
        >
          🏆 Leaderboard
        </button>
        <button
          onClick={onHowToPlay}
          className="py-3 px-8 text-lg font-bold rounded-lg text-[#6080aa] border border-[#6080aa]/30 transition-all duration-200 hover:border-[#0ff] hover:text-[#0ff] font-mono"
          style={{ background: 'rgba(0,255,255,0.03)' }}
        >
          📡 Como Jogar
        </button>
      </div>

      {/* Footer */}
      <div className="mt-16 text-sm text-[#203050] font-mono">
        WASD + Mouse • Touch Friendly
      </div>
    </div>
  );
};

export default MainMenu;
