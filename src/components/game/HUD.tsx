import React from 'react';
import { Player } from '../../game/types';

interface HUDProps {
  player: Player;
  wave: number;
  score: number;
  specialReady: boolean;
  combo: number;
  comboMultiplier: number;
  comboTimer: number;
}

const shipIcons: Record<string, string> = { phantom: '👻', interceptor: '⚡', titan: '💥' };

const HUD: React.FC<HUDProps> = ({ player, wave, score, specialReady, combo, comboMultiplier, comboTimer }) => {
  const specialPct = player.specialTimer > 0
    ? ((player.specialCooldown - player.specialTimer) / player.specialCooldown) * 100
    : 100;

  const shipColor = player.class === 'phantom' ? '#bf5af2' : player.class === 'interceptor' ? '#00e5ff' : '#ff6b00';

  return (
    <div className="absolute top-0 left-0 right-0 pointer-events-none select-none p-3 flex justify-between items-start z-10">
      {/* Left: Hearts + Special */}
      <div className="flex flex-col gap-1">
        <div className="flex items-center gap-2">
          <span className="text-lg">{shipIcons[player.class] || '🚀'}</span>
          {/* Hearts */}
          <div className="flex gap-1">
            {Array.from({ length: player.maxHp }).map((_, i) => (
              <span
                key={i}
                className="text-2xl transition-all duration-200"
                style={{
                  filter: i < player.hp ? 'drop-shadow(0 0 6px #ff0040)' : 'grayscale(1) opacity(0.3)',
                  transform: i < player.hp ? 'scale(1)' : 'scale(0.8)',
                }}
              >
                {i < player.hp ? '❤️' : '🖤'}
              </span>
            ))}
          </div>
        </div>

        {/* Special */}
        <div className="flex items-center gap-2">
          <span className="text-sm">✨</span>
          <div className="w-24 md:w-32 h-2 bg-[#0a0020] rounded-full overflow-hidden border border-[#bf5af233]">
            <div
              className="h-full transition-all duration-200 rounded-full"
              style={{
                width: `${specialPct}%`,
                background: specialReady ? '#bf5af2' : '#5a2080',
                boxShadow: specialReady ? '0 0 8px #bf5af2' : 'none',
              }}
            />
          </div>
          <span className="text-xs text-[#6080aa] font-mono">{specialReady ? 'READY' : `${Math.ceil(player.specialTimer)}s`}</span>
        </div>

        {/* Active effects */}
        <div className="flex gap-1 mt-1">
          {player.shieldTimer > 0 && <span className="text-sm animate-pulse" style={{ textShadow: '0 0 8px #0ff' }}>◯</span>}
          {player.tripleTimer > 0 && <span className="text-sm animate-pulse" style={{ textShadow: '0 0 8px #ff1493' }}>◆</span>}
          {player.speedBoostTimer > 0 && <span className="text-sm animate-pulse" style={{ textShadow: '0 0 8px #0ff' }}>⚡</span>}
        </div>
      </div>

      {/* Center: Wave + Combo */}
      <div className="text-center">
        <div className="text-sm font-bold font-mono" style={{ color: '#0ff', textShadow: '0 0 10px rgba(0,255,255,0.5)' }}>
          WAVE {wave}
        </div>
        {combo > 1 && comboTimer > 0 && (
          <div className="mt-1">
            <span
              className="text-lg font-bold font-mono animate-pulse"
              style={{
                color: comboMultiplier >= 8 ? '#ff1493' : comboMultiplier >= 4 ? '#ffff00' : '#0ff',
                textShadow: `0 0 12px ${comboMultiplier >= 8 ? '#ff1493' : comboMultiplier >= 4 ? '#ffff00' : '#0ff'}`,
              }}
            >
              ×{comboMultiplier}
            </span>
            <div className="w-16 h-1 mx-auto mt-0.5 bg-[#0a0020] rounded-full overflow-hidden">
              <div
                className="h-full rounded-full transition-all duration-100"
                style={{
                  width: `${(comboTimer / 2) * 100}%`,
                  background: comboMultiplier >= 8 ? '#ff1493' : comboMultiplier >= 4 ? '#ffff00' : '#0ff',
                }}
              />
            </div>
          </div>
        )}
      </div>

      {/* Right: Score */}
      <div className="text-right">
        <div className="text-xl font-bold font-mono" style={{ color: '#ffff00', textShadow: '0 0 10px rgba(255,255,0,0.4)' }}>
          {score.toLocaleString()}
        </div>
        <div className="text-xs text-[#6080aa] font-mono">score</div>
      </div>
    </div>
  );
};

export default HUD;
