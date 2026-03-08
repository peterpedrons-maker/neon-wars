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

  const activePassives = Object.entries(abilityLevels)
    .filter(([id, lv]) => lv > 0 && abilityMap[id]?.category === 'passive')
    .map(([id, lv]) => ({ ...abilityMap[id], lv }));

  return (
    <div className="absolute inset-0 pointer-events-none select-none z-10" style={{ fontFamily: 'monospace' }}>
      
      {/* ===== TOP BAR ===== */}
      <div className="absolute top-0 left-0 right-0 px-2 pt-1.5 pb-8"
        style={{ background: 'linear-gradient(to bottom, rgba(0,0,0,0.75) 0%, rgba(0,0,0,0.3) 60%, transparent 100%)' }}>
        
        <div className="flex items-start justify-between gap-2">
          {/* LEFT: HP + SP stacked */}
          <div className="flex flex-col gap-1 min-w-0 shrink-0">
            {/* HP hearts */}
            <div className="flex items-center gap-1">
              <span className="text-[10px] font-bold w-5" style={{ color: '#ff4060' }}>HP</span>
              <div className="flex gap-[2px]">
                {Array.from({ length: player.maxHp }).map((_, i) => (
                  <div key={i} className="w-3 h-2.5 rounded-[2px]" style={{
                    background: i < player.hp
                      ? 'linear-gradient(to bottom, #ff4060, #cc2040)'
                      : 'rgba(255,255,255,0.06)',
                    boxShadow: i < player.hp ? '0 0 4px rgba(255,64,96,0.4)' : 'none',
                  }} />
                ))}
              </div>
            </div>
            {/* SP bar */}
            <div className="flex items-center gap-1">
              <span className="text-[10px] font-bold w-5" style={{ color: specialReady ? '#bf5af2' : '#5a2080' }}>SP</span>
              <div className="w-16 h-2 rounded-full overflow-hidden" style={{ background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(191,90,242,0.2)' }}>
                <div className="h-full rounded-full" style={{
                  width: `${specialPct}%`,
                  background: specialReady ? 'linear-gradient(90deg, #bf5af2, #e080ff)' : '#5a2080',
                  boxShadow: specialReady ? '0 0 6px #bf5af2' : 'none',
                  transition: 'width 0.15s',
                }} />
              </div>
            </div>
          </div>

          {/* CENTER: Wave + Combo */}
          <div className="flex flex-col items-center shrink-0">
            <div className="px-2.5 py-0.5 rounded-full text-[11px] font-bold"
              style={{ background: 'rgba(0,255,255,0.1)', border: '1px solid rgba(0,255,255,0.25)', color: '#0ff' }}>
              WAVE {wave}
            </div>
            {combo > 1 && comboTimer > 0 && (
              <div className="mt-0.5 flex items-center gap-1">
                <span className="text-sm font-bold" style={{
                  color: comboMultiplier >= 8 ? '#ff1493' : comboMultiplier >= 4 ? '#ffff00' : '#0ff',
                  textShadow: `0 0 6px ${comboMultiplier >= 8 ? '#ff1493' : comboMultiplier >= 4 ? '#ffff00' : '#0ff'}`,
                }}>×{comboMultiplier}</span>
                <div className="w-8 h-1 rounded-full overflow-hidden" style={{ background: 'rgba(255,255,255,0.1)' }}>
                  <div className="h-full rounded-full" style={{
                    width: `${(comboTimer / 2) * 100}%`,
                    background: comboMultiplier >= 8 ? '#ff1493' : comboMultiplier >= 4 ? '#ffff00' : '#0ff',
                  }} />
                </div>
              </div>
            )}
          </div>

          {/* RIGHT: Score + Level */}
          <div className="flex flex-col items-end shrink-0">
            <div className="text-base font-bold" style={{ color: '#ffff00', textShadow: '0 0 6px rgba(255,255,0,0.3)' }}>
              {score.toLocaleString()}
            </div>
            <div className="flex items-center gap-1">
              <span className="text-[10px] font-bold" style={{ color: '#bf5af2' }}>LV{level}</span>
              <div className="w-12 h-1.5 rounded-full overflow-hidden" style={{ background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(191,90,242,0.15)' }}>
                <div className="h-full rounded-full" style={{
                  width: `${(xp / xpToNext) * 100}%`,
                  background: 'linear-gradient(90deg, #bf5af2, #e080ff)',
                  transition: 'width 0.1s',
                }} />
              </div>
            </div>
          </div>
        </div>

        {/* Active effects row (below top bar, inline) */}
        <div className="flex gap-1 mt-1 ml-1">
          {player.shieldTimer > 0 && <span className="text-[10px] px-1 rounded" style={{ background: 'rgba(0,255,255,0.15)', color: '#0ff' }}>🛡️</span>}
          {player.tripleTimer > 0 && <span className="text-[10px] px-1 rounded" style={{ background: 'rgba(255,20,147,0.15)', color: '#ff1493' }}>3x</span>}
          {player.speedBoostTimer > 0 && <span className="text-[10px] px-1 rounded" style={{ background: 'rgba(0,229,255,0.15)', color: '#00e5ff' }}>⚡</span>}
        </div>
      </div>

      {/* ===== BOTTOM BAR: Weapons + Passives ===== */}
      <div className="absolute bottom-0 left-0 right-0 px-2 pb-2 pt-6"
        style={{ background: 'linear-gradient(to top, rgba(0,0,0,0.65) 0%, rgba(0,0,0,0.2) 60%, transparent 100%)' }}>
        
        <div className="flex items-end justify-between gap-2">
          {/* Weapon slots - left aligned */}
          <div className="flex gap-1">
            {Array.from({ length: weaponSlots }).map((_, i) => {
              const weaponId = equippedWeapons[i];
              const ability = weaponId ? abilityMap[weaponId] : null;
              const lv = weaponId ? (abilityLevels[weaponId] || 0) : 0;
              return (
                <div key={i} className="relative">
                  <div className="w-9 h-9 rounded-lg flex items-center justify-center"
                    style={{
                      background: ability ? 'rgba(255,100,0,0.1)' : 'rgba(255,255,255,0.02)',
                      border: `1px solid ${ability ? 'rgba(255,100,0,0.35)' : 'rgba(255,255,255,0.06)'}`,
                    }}>
                    {ability ? (
                      <span className="text-base">{ability.icon}</span>
                    ) : (
                      <span className="text-[9px]" style={{ color: '#252540' }}>—</span>
                    )}
                  </div>
                  {lv > 0 && (
                    <div className="absolute -top-1 -right-1 w-3.5 h-3.5 rounded-full flex items-center justify-center text-[7px] font-bold"
                      style={{ background: '#ff6b00', color: '#000' }}>
                      {lv}
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          {/* Passive icons - right aligned, compact */}
          {activePassives.length > 0 && (
            <div className="flex gap-[3px] flex-wrap justify-end" style={{ maxWidth: '45%' }}>
              {activePassives.map(p => (
                <div key={p.id} className="relative">
                  <div className="w-7 h-7 rounded-md flex items-center justify-center"
                    style={{
                      background: 'rgba(0,255,255,0.06)',
                      border: '1px solid rgba(0,255,255,0.15)',
                    }}>
                    <span className="text-xs">{p.icon}</span>
                  </div>
                  <div className="absolute -top-0.5 -right-0.5 w-3 h-3 rounded-full flex items-center justify-center text-[6px] font-bold"
                    style={{ background: '#0ff', color: '#000' }}>
                    {p.lv}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default HUD;
