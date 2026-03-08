import React from 'react';
import { PlayerClass } from '../../game/types';

interface MainMenuProps {
  onPlay: () => void;
  onLeaderboard: () => void;
  onHowToPlay: () => void;
}

const MainMenu: React.FC<MainMenuProps> = ({ onPlay, onLeaderboard, onHowToPlay }) => {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-[#08061a] text-[#f1f5f9] select-none">
      {/* Title */}
      <div className="mb-12 text-center">
        <h1 className="text-6xl md:text-8xl font-bold tracking-wider mb-2"
            style={{ fontFamily: 'Georgia, serif', textShadow: '0 0 40px rgba(168,85,247,0.4), 0 4px 8px rgba(0,0,0,0.8)' }}>
          <span className="text-[#fbbf24]">⚔️</span> Medieval Wars
        </h1>
        <p className="text-xl md:text-2xl text-[#94a3b8] italic" style={{ fontFamily: 'Georgia, serif' }}>
          Arena de Sobrevivência Fantasy
        </p>
      </div>

      {/* Decorative divider */}
      <div className="w-48 h-px bg-gradient-to-r from-transparent via-[#5a3a28] to-transparent mb-10" />

      {/* Menu buttons */}
      <div className="flex flex-col gap-4 w-72">
        <button
          onClick={onPlay}
          className="py-4 px-8 text-xl font-bold rounded-lg bg-gradient-to-r from-[#8B4513] to-[#A0522D] hover:from-[#A0522D] hover:to-[#CD853F] text-[#f5e6d3] border-2 border-[#CD853F] transition-all duration-200 hover:scale-105 hover:shadow-[0_0_20px_rgba(205,133,63,0.4)] active:scale-95"
          style={{ fontFamily: 'Georgia, serif' }}
        >
          ⚔️ Jogar
        </button>
        <button
          onClick={onLeaderboard}
          className="py-3 px-8 text-lg font-bold rounded-lg bg-[#2a1810] hover:bg-[#3a2820] text-[#f1c40f] border-2 border-[#5a3a28] transition-all duration-200 hover:border-[#f1c40f] hover:shadow-[0_0_15px_rgba(241,196,15,0.2)]"
          style={{ fontFamily: 'Georgia, serif' }}
        >
          🏆 Leaderboard
        </button>
        <button
          onClick={onHowToPlay}
          className="py-3 px-8 text-lg font-bold rounded-lg bg-[#2a1810] hover:bg-[#3a2820] text-[#8a7a6a] border-2 border-[#5a3a28] transition-all duration-200 hover:border-[#8a7a6a]"
          style={{ fontFamily: 'Georgia, serif' }}
        >
          📜 Como Jogar
        </button>
      </div>

      {/* Footer */}
      <div className="mt-16 text-sm text-[#5a3a28]">
        WASD + Mouse • Touch Friendly
      </div>
    </div>
  );
};

export default MainMenu;
