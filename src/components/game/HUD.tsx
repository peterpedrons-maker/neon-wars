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

  const xpPct = xpToNext > 0 ? Math.min(100, (xp / xpToNext) * 100) : 0;

  const activePassives = Object.entries(abilityLevels)
    .filter(([id, lv]) => lv > 0 && abilityMap[id]?.category === 'passive')
    .map(([id, lv]) => ({ ...abilityMap[id], lv }));

  return (
    <div className="absolute inset-0 pointer-events-none select-none z-10" style={{ fontFamily: "'Segoe UI', monospace" }}>
      
      {/* ===== TOP BAR ===== */}
      <div className="absolute top-0 left-0 right-0 px-3 pt-2 pb-10"
        style={{ background: 'linear-gradient(to bottom, rgba(0,0,0,0.85) 0%, rgba(0,0,0,0.4) 55%, transparent 100%)' }}>
        
        <div className="flex items-start justify-between gap-3">
          {/* LEFT: HP hearts + SP bar */}
          <div className="flex flex-col gap-1.5 min-w-0 shrink-0">
            {/* HP hearts */}
            <div className="flex items-center gap-1.5">
              <span className="text-sm font-bold tracking-wide" style={{ color: '#ff4060', textShadow: '0 0 6px rgba(255,64,96,0.5)' }}>HP</span>
              <div className="flex gap-1">
                {Array.from({ length: player.maxHp }).map((_, i) => (
                  <div key={i} className="rounded-sm" style={{
                    width: 16,
                    height: 14,
                    background: i < player.hp
                      ? 'linear-gradient(to bottom, #ff4060, #cc2040)'
                      : 'rgba(255,255,255,0.08)',
                    boxShadow: i < player.hp ? '0 0 8px rgba(255,64,96,0.6), inset 0 1px 0 rgba(255,255,255,0.2)' : 'none',
                    border: i < player.hp ? '1px solid rgba(255,100,120,0.4)' : '1px solid rgba(255,255,255,0.06)',
                  }} />
                ))}
              </div>
            </div>
            {/* SP bar */}
            <div className="flex items-center gap-1.5">
              <span className="text-sm font-bold tracking-wide" style={{ color: specialReady ? '#bf5af2' : '#5a2080', textShadow: specialReady ? '0 0 6px rgba(191,90,242,0.5)' : 'none' }}>SP</span>
              <div className="rounded-full overflow-hidden" style={{ width: 80, height: 10, background: 'rgba(255,255,255,0.08)', border: '1px solid rgba(191,90,242,0.3)' }}>
                <div className="h-full rounded-full" style={{
                  width: `${specialPct}%`,
                  background: specialReady ? 'linear-gradient(90deg, #bf5af2, #e080ff)' : 'linear-gradient(90deg, #3a1060, #5a2080)',
                  boxShadow: specialReady ? '0 0 10px #bf5af2, 0 0 4px #e080ff' : 'none',
                  transition: 'width 0.15s',
                }} />
              </div>
            </div>
            {/* Active effects */}
            <div className="flex gap-1.5 mt-0.5">
              {player.shieldTimer > 0 && <span className="text-xs px-1.5 py-0.5 rounded-md font-bold" style={{ background: 'rgba(0,255,255,0.2)', color: '#0ff', border: '1px solid rgba(0,255,255,0.3)' }}>🛡️</span>}
              {player.tripleTimer > 0 && <span className="text-xs px-1.5 py-0.5 rounded-md font-bold" style={{ background: 'rgba(255,20,147,0.2)', color: '#ff1493', border: '1px solid rgba(255,20,147,0.3)' }}>3×</span>}
              {player.speedBoostTimer > 0 && <span className="text-xs px-1.5 py-0.5 rounded-md font-bold" style={{ background: 'rgba(0,229,255,0.2)', color: '#00e5ff', border: '1px solid rgba(0,229,255,0.3)' }}>⚡</span>}
            </div>
          </div>

          {/* CENTER: Wave + Combo */}
          <div className="flex flex-col items-center shrink-0">
            <div className="px-4 py-1 rounded-full text-sm font-black tracking-wider"
              style={{ background: 'rgba(0,255,255,0.12)', border: '1px solid rgba(0,255,255,0.35)', color: '#0ff', textShadow: '0 0 8px rgba(0,255,255,0.4)' }}>
              WAVE {wave}
            </div>
            {combo > 1 && comboTimer > 0 && (
              <div className="mt-1 flex items-center gap-1.5">
                <span className="text-lg font-black" style={{
                  color: comboMultiplier >= 8 ? '#ff1493' : comboMultiplier >= 4 ? '#ffff00' : '#0ff',
                  textShadow: `0 0 10px ${comboMultiplier >= 8 ? '#ff1493' : comboMultiplier >= 4 ? '#ffff00' : '#0ff'}`,
                }}>×{comboMultiplier}</span>
                <div className="rounded-full overflow-hidden" style={{ width: 40, height: 4, background: 'rgba(255,255,255,0.12)' }}>
                  <div className="h-full rounded-full" style={{
                    width: `${(comboTimer / 2) * 100}%`,
                    background: comboMultiplier >= 8 ? '#ff1493' : comboMultiplier >= 4 ? '#ffff00' : '#0ff',
                  }} />
                </div>
              </div>
            )}
          </div>

          {/* RIGHT: Score + Level + XP bar */}
          <div className="flex flex-col items-end shrink-0">
            <div className="text-xl font-black tabular-nums" style={{ color: '#ffff00', textShadow: '0 0 10px rgba(255,255,0,0.4)', letterSpacing: '0.5px' }}>
              {score.toLocaleString()}
            </div>
            <div className="flex items-center gap-1.5 mt-0.5">
              <span className="text-sm font-black" style={{ color: '#bf5af2', textShadow: '0 0 6px rgba(191,90,242,0.4)' }}>LV {level}</span>
            </div>
            <div className="mt-1 rounded-full overflow-hidden" style={{ width: 100, height: 8, background: 'rgba(255,255,255,0.08)', border: '1px solid rgba(191,90,242,0.2)' }}>
              <div className="h-full rounded-full" style={{
                width: `${xpPct}%`,
                background: 'linear-gradient(90deg, #bf5af2, #e080ff)',
                boxShadow: '0 0 6px rgba(191,90,242,0.4)',
                transition: 'width 0.15s',
              }} />
            </div>
            <span className="text-[10px] mt-0.5 font-bold" style={{ color: 'rgba(191,90,242,0.7)' }}>{xp}/{xpToNext} XP</span>
          </div>
        </div>
      </div>

      {/* ===== BOTTOM BAR: Weapons + Passives ===== */}
      <div className="absolute bottom-0 left-0 right-0 px-3 pb-3 pt-8"
        style={{ background: 'linear-gradient(to top, rgba(0,0,0,0.8) 0%, rgba(0,0,0,0.3) 55%, transparent 100%)' }}>
        
        <div className="flex items-end justify-between gap-3">
          {/* Weapon slots */}
          <div className="flex gap-1.5">
            {Array.from({ length: weaponSlots }).map((_, i) => {
              const weaponId = equippedWeapons[i];
              const ability = weaponId ? abilityMap[weaponId] : null;
              const lv = weaponId ? (abilityLevels[weaponId] || 0) : 0;
              return (
                <div key={i} className="relative">
                  <div className="flex items-center justify-center rounded-lg"
                    style={{
                      width: 44,
                      height: 44,
                      background: ability ? 'rgba(255,100,0,0.15)' : 'rgba(255,255,255,0.03)',
                      border: `2px solid ${ability ? 'rgba(255,100,0,0.5)' : 'rgba(255,255,255,0.08)'}`,
                      boxShadow: ability ? '0 0 8px rgba(255,100,0,0.2), inset 0 0 8px rgba(255,100,0,0.1)' : 'none',
                    }}>
                    {ability ? (
                      <span className="text-xl">{ability.icon}</span>
                    ) : (
                      <span className="text-xs" style={{ color: '#333' }}>—</span>
                    )}
                  </div>
                  {lv > 0 && (
                    <div className="absolute -top-1.5 -right-1.5 rounded-full flex items-center justify-center font-black"
                      style={{ width: 18, height: 18, fontSize: 10, background: 'linear-gradient(135deg, #ff8c00, #ff6b00)', color: '#000', boxShadow: '0 0 6px rgba(255,107,0,0.5)' }}>
                      {lv}
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          {/* Passive icons */}
          {activePassives.length > 0 && (
            <div className="flex gap-1 flex-wrap justify-end" style={{ maxWidth: '50%' }}>
              {activePassives.map(p => (
                <div key={p.id} className="relative">
                  <div className="flex items-center justify-center rounded-md"
                    style={{
                      width: 36,
                      height: 36,
                      background: 'rgba(0,255,255,0.08)',
                      border: '1px solid rgba(0,255,255,0.25)',
                      boxShadow: '0 0 6px rgba(0,255,255,0.1)',
                    }}>
                    <span className="text-base">{p.icon}</span>
                  </div>
                  <div className="absolute -top-1 -right-1 rounded-full flex items-center justify-center font-black"
                    style={{ width: 16, height: 16, fontSize: 9, background: '#0ff', color: '#000' }}>
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
