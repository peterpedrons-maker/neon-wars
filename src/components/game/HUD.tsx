import React from 'react';
import { Player } from '../../game/types';
import { ALL_ABILITIES } from '../../game/abilities';

interface HUDProps {
  player: Player;
  wave: number;
  score: number;
  specialReady: boolean;
  combo: number;
  comboMultiplier: number;
  comboTimer: number;
  level: number;
  xp: number;
  xpToNext: number;
  equippedWeapons: string[];
  weaponSlots: number;
  abilityLevels: Record<string, number>;
}

const abilityMap = Object.fromEntries(ALL_ABILITIES.map(a => [a.id, a]));

const HUD: React.FC<HUDProps> = ({
  player, wave, score, specialReady, combo, comboMultiplier, comboTimer,
  level, xp, xpToNext, equippedWeapons, weaponSlots, abilityLevels,
}) => {
  const specialPct = player.specialTimer > 0
    ? ((player.specialCooldown - player.specialTimer) / player.specialCooldown) * 100
    : 100;

  // Collect active passives
  const activePassives = Object.entries(abilityLevels)
    .filter(([id, lv]) => lv > 0 && abilityMap[id]?.category === 'passive')
    .map(([id, lv]) => ({ ...abilityMap[id], lv }));

  return (
    <div className="absolute inset-x-0 top-0 pointer-events-none select-none z-10">
      {/* Top bar background */}
      <div className="px-3 py-2 flex justify-between items-start"
        style={{ background: 'linear-gradient(to bottom, rgba(0,0,0,0.7) 0%, rgba(0,0,0,0.3) 70%, transparent 100%)' }}>
        
        {/* LEFT: HP + Special + Active effects */}
        <div className="flex flex-col gap-1.5 min-w-0">
          {/* HP bar */}
          <div className="flex items-center gap-1.5">
            <span className="text-xs font-mono font-bold" style={{ color: '#ff4060', textShadow: '0 0 6px rgba(255,64,96,0.5)' }}>HP</span>
            <div className="flex gap-0.5">
              {Array.from({ length: player.maxHp }).map((_, i) => (
                <div key={i} className="w-4 h-3 rounded-sm transition-all duration-150" style={{
                  background: i < player.hp
                    ? 'linear-gradient(to bottom, #ff4060, #cc2040)'
                    : 'rgba(255,255,255,0.06)',
                  boxShadow: i < player.hp ? '0 0 6px rgba(255,64,96,0.5)' : 'none',
                }} />
              ))}
            </div>
            <span className="text-[10px] font-mono" style={{ color: '#ff4060' }}>{player.hp}/{player.maxHp}</span>
          </div>

          {/* Special bar */}
          <div className="flex items-center gap-1.5">
            <span className="text-xs font-mono font-bold" style={{ color: '#bf5af2', textShadow: '0 0 6px rgba(191,90,242,0.4)' }}>SP</span>
            <div className="w-20 md:w-28 h-2.5 rounded-full overflow-hidden" style={{ background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(191,90,242,0.2)' }}>
              <div className="h-full rounded-full transition-all duration-200" style={{
                width: `${specialPct}%`,
                background: specialReady
                  ? 'linear-gradient(90deg, #bf5af2, #e080ff)'
                  : 'linear-gradient(90deg, #5a2080, #7a40a0)',
                boxShadow: specialReady ? '0 0 8px #bf5af2' : 'none',
              }} />
            </div>
            <span className="text-[10px] font-mono" style={{ color: specialReady ? '#bf5af2' : '#5a2080' }}>
              {specialReady ? 'READY' : `${Math.ceil(player.specialTimer)}s`}
            </span>
          </div>

          {/* Active effects */}
          <div className="flex gap-1">
            {player.shieldTimer > 0 && <span className="text-xs px-1 rounded" style={{ background: 'rgba(0,255,255,0.15)', color: '#0ff' }}>🛡️</span>}
            {player.tripleTimer > 0 && <span className="text-xs px-1 rounded" style={{ background: 'rgba(255,20,147,0.15)', color: '#ff1493' }}>3x</span>}
            {player.speedBoostTimer > 0 && <span className="text-xs px-1 rounded" style={{ background: 'rgba(0,255,255,0.15)', color: '#0ff' }}>⚡</span>}
          </div>
        </div>

        {/* CENTER: Wave + Combo */}
        <div className="text-center flex flex-col items-center">
          <div className="px-3 py-0.5 rounded-full font-bold font-mono text-sm"
            style={{ background: 'rgba(0,255,255,0.1)', border: '1px solid rgba(0,255,255,0.2)', color: '#0ff', textShadow: '0 0 8px rgba(0,255,255,0.4)' }}>
            WAVE {wave}
          </div>
          {combo > 1 && comboTimer > 0 && (
            <div className="mt-1 flex flex-col items-center">
              <span className="text-lg font-bold font-mono animate-pulse" style={{
                color: comboMultiplier >= 8 ? '#ff1493' : comboMultiplier >= 4 ? '#ffff00' : '#0ff',
                textShadow: `0 0 10px ${comboMultiplier >= 8 ? '#ff1493' : comboMultiplier >= 4 ? '#ffff00' : '#0ff'}`,
              }}>
                ×{comboMultiplier}
              </span>
              <div className="w-12 h-1 rounded-full overflow-hidden" style={{ background: 'rgba(255,255,255,0.1)' }}>
                <div className="h-full rounded-full transition-all duration-100" style={{
                  width: `${(comboTimer / 2) * 100}%`,
                  background: comboMultiplier >= 8 ? '#ff1493' : comboMultiplier >= 4 ? '#ffff00' : '#0ff',
                }} />
              </div>
            </div>
          )}
        </div>

        {/* RIGHT: Score + Level */}
        <div className="text-right flex flex-col items-end">
          <div className="text-xl font-bold font-mono" style={{ color: '#ffff00', textShadow: '0 0 8px rgba(255,255,0,0.3)' }}>
            {score.toLocaleString()}
          </div>
          <div className="flex items-center gap-1.5 mt-1">
            <span className="text-xs font-mono font-bold" style={{ color: '#bf5af2' }}>LV {level}</span>
            <div className="w-16 md:w-20 h-2 rounded-full overflow-hidden" style={{ background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(191,90,242,0.2)' }}>
              <div className="h-full rounded-full transition-all duration-150" style={{
                width: `${(xp / xpToNext) * 100}%`,
                background: 'linear-gradient(90deg, #bf5af2, #e080ff)',
                boxShadow: '0 0 4px #bf5af2',
              }} />
            </div>
          </div>
        </div>
      </div>

      {/* Bottom: Weapon Slots + Passive Icons */}
      <div className="absolute bottom-0 left-0 right-0 px-3 pb-3 flex justify-between items-end"
        style={{ background: 'linear-gradient(to top, rgba(0,0,0,0.5) 0%, rgba(0,0,0,0.2) 60%, transparent 100%)' }}>
        
        {/* Weapon slots */}
        <div className="flex gap-1.5">
          {Array.from({ length: weaponSlots }).map((_, i) => {
            const weaponId = equippedWeapons[i];
            const ability = weaponId ? abilityMap[weaponId] : null;
            const lv = weaponId ? (abilityLevels[weaponId] || 0) : 0;
            return (
              <div key={i} className="flex flex-col items-center">
                <div className="w-10 h-10 md:w-12 md:h-12 rounded-lg flex items-center justify-center relative"
                  style={{
                    background: ability ? 'rgba(255,100,0,0.12)' : 'rgba(255,255,255,0.03)',
                    border: `1.5px solid ${ability ? 'rgba(255,100,0,0.4)' : 'rgba(255,255,255,0.08)'}`,
                    boxShadow: ability ? '0 0 8px rgba(255,100,0,0.15)' : 'none',
                  }}>
                  {ability ? (
                    <span className="text-lg md:text-xl">{ability.icon}</span>
                  ) : (
                    <span className="text-[10px] font-mono" style={{ color: '#303050' }}>—</span>
                  )}
                  {lv > 0 && (
                    <div className="absolute -top-1 -right-1 w-4 h-4 rounded-full flex items-center justify-center text-[8px] font-bold font-mono"
                      style={{ background: '#ff6b00', color: '#000' }}>
                      {lv}
                    </div>
                  )}
                </div>
                <span className="text-[8px] font-mono mt-0.5 max-w-[48px] truncate text-center"
                  style={{ color: ability ? '#ff6b00' : '#303050' }}>
                  {ability ? ability.name : `Slot ${i + 1}`}
                </span>
              </div>
            );
          })}
        </div>

        {/* Passive icons */}
        {activePassives.length > 0 && (
          <div className="flex gap-1 flex-wrap justify-end max-w-[50%]">
            {activePassives.map(p => (
              <div key={p.id} className="w-8 h-8 rounded-md flex items-center justify-center relative"
                style={{
                  background: 'rgba(0,255,255,0.08)',
                  border: '1px solid rgba(0,255,255,0.2)',
                }}>
                <span className="text-sm">{p.icon}</span>
                <div className="absolute -top-1 -right-1 w-3.5 h-3.5 rounded-full flex items-center justify-center text-[7px] font-bold font-mono"
                  style={{ background: '#0ff', color: '#000' }}>
                  {p.lv}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default HUD;
