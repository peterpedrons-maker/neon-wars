import React from 'react';
import { Player } from '../../game/types';

interface HUDProps {
  player: Player;
  wave: number;
  score: number;
  specialReady: boolean;
}

const HUD: React.FC<HUDProps> = ({ player, wave, score, specialReady }) => {
  const hpPct = (player.hp / player.maxHp) * 100;
  const specialPct = player.specialTimer > 0
    ? ((player.specialCooldown - player.specialTimer) / player.specialCooldown) * 100
    : 100;

  return (
    <div className="absolute top-0 left-0 right-0 pointer-events-none select-none p-3 flex justify-between items-start z-10">
      {/* Left: HP */}
      <div className="flex flex-col gap-1">
        <div className="flex items-center gap-2">
          <span className="text-lg">
            {player.class === 'mage' ? '🔮' : player.class === 'archer' ? '🏹' : '⚔️'}
          </span>
          <div className="w-36 md:w-48 h-4 bg-[#450a0a] rounded-full overflow-hidden border border-[#4a3a6e]">
            <div
              className="h-full transition-all duration-200 rounded-full"
              style={{
                width: `${hpPct}%`,
                background: hpPct > 50 ? 'linear-gradient(90deg, #27ae60, #2ecc71)' :
                  hpPct > 25 ? 'linear-gradient(90deg, #f39c12, #e67e22)' :
                  'linear-gradient(90deg, #e74c3c, #c0392b)',
              }}
            />
          </div>
          <span className="text-xs text-[#f5e6d3] font-mono">{player.hp}/{player.maxHp}</span>
        </div>

        {/* Special */}
        <div className="flex items-center gap-2">
          <span className="text-sm">✨</span>
          <div className="w-24 md:w-32 h-2.5 bg-[#2a1830] rounded-full overflow-hidden border border-[#5a3a58]">
            <div
              className="h-full transition-all duration-200 rounded-full"
              style={{
                width: `${specialPct}%`,
                background: specialReady ? '#9b59b6' : '#6c3483',
              }}
            />
          </div>
          <span className="text-xs text-[#8a7a6a]">{specialReady ? 'PRONTO' : `${Math.ceil(player.specialTimer)}s`}</span>
        </div>

        {/* Active effects */}
        <div className="flex gap-1 mt-1">
          {player.shieldTimer > 0 && <span className="text-sm animate-pulse">🛡️</span>}
          {player.tripleTimer > 0 && <span className="text-sm animate-pulse">🔥</span>}
          {player.speedBoostTimer > 0 && <span className="text-sm animate-pulse">💨</span>}
        </div>
      </div>

      {/* Center: Wave */}
      <div className="text-center">
        <div className="text-[#f1c40f] text-sm font-bold" style={{ fontFamily: 'Georgia, serif', textShadow: '0 0 10px rgba(241,196,15,0.5)' }}>
          ONDA {wave}
        </div>
      </div>

      {/* Right: Score */}
      <div className="text-right">
        <div className="text-[#f1c40f] text-xl font-bold font-mono" style={{ textShadow: '0 0 10px rgba(241,196,15,0.4)' }}>
          {score.toLocaleString()}
        </div>
        <div className="text-xs text-[#8a7a6a]">pontos</div>
      </div>
    </div>
  );
};

export default HUD;
