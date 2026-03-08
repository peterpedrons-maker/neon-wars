import React from 'react';
import { Player } from '../../game/types';
import { ALL_ABILITIES } from '../../game/abilities';
import { useIsMobile } from '../../hooks/use-mobile';

interface PeerInfo {
  hp: number;
  maxHp: number;
  alive: boolean;
  shipClass: string;
  label: string;
}

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
  enemiesKilled?: number;
  enemiesKilledThisWave?: number;
  coopPeers?: PeerInfo[];
}

const abilityMap = Object.fromEntries(ALL_ABILITIES.map(a => [a.id, a]));

const SHIP_COLORS: Record<string, string> = {
  phantom: '#bf5af2', interceptor: '#00e5ff', titan: '#ff6b00',
  spectre: '#9040ff', valkyrie: '#ff1493', juggernaut: '#ff4500',
};

const HUD: React.FC<HUDProps> = ({
  player, wave, score, specialReady, combo, comboMultiplier, comboTimer,
  level, xp, xpToNext, equippedWeapons, weaponSlots, abilityLevels,
  enemiesKilled = 0, enemiesKilledThisWave = 0, coopPeers,
}) => {
  const isMobile = useIsMobile();
  const specialPct = player.specialTimer > 0
    ? ((player.specialCooldown - player.specialTimer) / player.specialCooldown) * 100
    : 100;

  const xpPct = xpToNext > 0 ? Math.min(100, (xp / xpToNext) * 100) : 0;

  const activePassives = Object.entries(abilityLevels)
    .filter(([id, lv]) => lv > 0 && abilityMap[id]?.category === 'passive')
    .map(([id, lv]) => ({ ...abilityMap[id], lv }));

  const s = isMobile ? 1.3 : 1;
  const fs = (base: number) => `${Math.round(base * s)}px`;

  return (
    <div className="absolute inset-0 pointer-events-none select-none z-10" style={{ fontFamily: "'Segoe UI', monospace" }}>
      
      {/* ===== TOP BAR ===== */}
      <div className="absolute top-0 left-0 right-0" style={{
        padding: isMobile ? '10px 10px 40px' : '8px 12px 40px',
        background: 'linear-gradient(to bottom, rgba(0,0,0,0.9) 0%, rgba(0,0,0,0.5) 55%, transparent 100%)',
      }}>
        
        <div className="flex items-start justify-between" style={{ gap: isMobile ? 6 : 12 }}>
          {/* LEFT: HP + SP + Stats */}
          <div className="flex flex-col shrink-0" style={{ gap: isMobile ? 5 : 5, minWidth: 0 }}>
            {/* Ship class badge */}
            <div className="flex items-center" style={{ gap: 4 }}>
              <span style={{
                fontSize: fs(10), fontWeight: 900, padding: '1px 6px', borderRadius: 4,
                background: `${SHIP_COLORS[player.class] || '#fff'}22`,
                border: `1px solid ${SHIP_COLORS[player.class] || '#fff'}55`,
                color: SHIP_COLORS[player.class] || '#fff',
                textTransform: 'uppercase' as const, letterSpacing: '0.1em',
              }}>{player.class}</span>
              <span style={{ fontSize: fs(10), fontWeight: 700, color: '#6080aa' }}>
                DMG: {player.damage}
              </span>
            </div>
            {/* HP hearts */}
            <div className="flex items-center" style={{ gap: isMobile ? 4 : 6 }}>
              <span style={{ fontSize: fs(15), fontWeight: 900, color: '#ff4060', textShadow: '0 0 8px rgba(255,64,96,0.6)' }}>HP</span>
              <div className="flex" style={{ gap: isMobile ? 3 : 4 }}>
                {Array.from({ length: player.maxHp }).map((_, i) => (
                  <div key={i} style={{
                    width: isMobile ? 20 : 18, height: isMobile ? 18 : 16, borderRadius: 3,
                    background: i < player.hp ? 'linear-gradient(to bottom, #ff4060, #cc2040)' : 'rgba(255,255,255,0.08)',
                    boxShadow: i < player.hp ? '0 0 10px rgba(255,64,96,0.7), inset 0 1px 0 rgba(255,255,255,0.2)' : 'none',
                    border: i < player.hp ? '1px solid rgba(255,100,120,0.5)' : '1px solid rgba(255,255,255,0.06)',
                  }} />
                ))}
              </div>
            </div>
            {/* SP bar */}
            <div className="flex items-center" style={{ gap: isMobile ? 4 : 6 }}>
              <span style={{
                fontSize: fs(15), fontWeight: 900,
                color: specialReady ? '#bf5af2' : '#5a2080',
                textShadow: specialReady ? '0 0 8px rgba(191,90,242,0.6)' : 'none',
              }}>SP</span>
              <div style={{
                width: isMobile ? 100 : 90, height: isMobile ? 14 : 12,
                borderRadius: 99, overflow: 'hidden',
                background: 'rgba(255,255,255,0.08)', border: '1px solid rgba(191,90,242,0.35)',
              }}>
                <div style={{
                  height: '100%', borderRadius: 99, width: `${specialPct}%`,
                  background: specialReady ? 'linear-gradient(90deg, #bf5af2, #e080ff)' : 'linear-gradient(90deg, #3a1060, #5a2080)',
                  boxShadow: specialReady ? '0 0 12px #bf5af2, 0 0 4px #e080ff' : 'none',
                  transition: 'width 0.15s',
                }} />
              </div>
              {specialReady && (
                <span style={{ fontSize: fs(10), fontWeight: 900, color: '#e080ff', textShadow: '0 0 6px #bf5af2' }}>READY</span>
              )}
            </div>
            {/* Kill counter */}
            <div className="flex items-center" style={{ gap: 6 }}>
              <span style={{ fontSize: fs(10), fontWeight: 700, color: '#ff4060' }}>💀 {enemiesKilled}</span>
              <span style={{ fontSize: fs(9), fontWeight: 600, color: '#6080aa' }}>({enemiesKilledThisWave} esta wave)</span>
            </div>
            {/* Active effects */}
            <div className="flex" style={{ gap: 4 }}>
              {player.shieldTimer > 0 && (
                <span style={{ fontSize: fs(11), padding: '1px 5px', borderRadius: 5, fontWeight: 800, background: 'rgba(0,255,255,0.2)', color: '#0ff', border: '1px solid rgba(0,255,255,0.4)' }}>🛡️ {Math.ceil(player.shieldTimer)}s</span>
              )}
              {player.tripleTimer > 0 && (
                <span style={{ fontSize: fs(11), padding: '1px 5px', borderRadius: 5, fontWeight: 800, background: 'rgba(255,20,147,0.2)', color: '#ff1493', border: '1px solid rgba(255,20,147,0.4)' }}>3× {Math.ceil(player.tripleTimer)}s</span>
              )}
              {player.speedBoostTimer > 0 && (
                <span style={{ fontSize: fs(11), padding: '1px 5px', borderRadius: 5, fontWeight: 800, background: 'rgba(0,229,255,0.2)', color: '#00e5ff', border: '1px solid rgba(0,229,255,0.4)' }}>⚡ {Math.ceil(player.speedBoostTimer)}s</span>
              )}
            </div>
          </div>

          {/* CENTER: Wave + Combo */}
          <div className="flex flex-col items-center shrink-0">
            <div style={{
              padding: isMobile ? '5px 16px' : '4px 14px', borderRadius: 99,
              fontSize: fs(15), fontWeight: 900, letterSpacing: '0.1em',
              background: 'rgba(0,255,255,0.15)', border: '2px solid rgba(0,255,255,0.45)',
              color: '#0ff', textShadow: '0 0 10px rgba(0,255,255,0.5)',
            }}>
              WAVE {wave}
            </div>
            {combo > 1 && comboTimer > 0 && (
              <div className="flex items-center" style={{ gap: 6, marginTop: 4 }}>
                <span style={{
                  fontSize: fs(22), fontWeight: 900,
                  color: comboMultiplier >= 8 ? '#ff1493' : comboMultiplier >= 4 ? '#ffff00' : '#0ff',
                  textShadow: `0 0 12px ${comboMultiplier >= 8 ? '#ff1493' : comboMultiplier >= 4 ? '#ffff00' : '#0ff'}`,
                }}>×{comboMultiplier}</span>
                <div style={{ width: 50, height: 6, borderRadius: 99, overflow: 'hidden', background: 'rgba(255,255,255,0.12)' }}>
                  <div style={{
                    height: '100%', borderRadius: 99,
                    width: `${(comboTimer / 2) * 100}%`,
                    background: comboMultiplier >= 8 ? '#ff1493' : comboMultiplier >= 4 ? '#ffff00' : '#0ff',
                  }} />
                </div>
              </div>
            )}
          </div>

          {/* RIGHT: Score + Level + XP */}
          <div className="flex flex-col items-end shrink-0">
            {coopPeers && coopPeers.length > 0 && (
              <div style={{ fontSize: fs(9), fontWeight: 700, color: '#0ff', opacity: 0.8, marginBottom: -2 }}>
                PONTUAÇÃO COMPARTILHADA
              </div>
            )}
            <div style={{
              fontSize: fs(24), fontWeight: 900, fontVariantNumeric: 'tabular-nums',
              color: '#ffff00', textShadow: '0 0 12px rgba(255,255,0,0.5)', letterSpacing: '0.5px',
            }}>
              {score.toLocaleString()}
            </div>
            <div className="flex items-center" style={{ gap: 6, marginTop: 2 }}>
              <span style={{ fontSize: fs(16), fontWeight: 900, color: '#bf5af2', textShadow: '0 0 8px rgba(191,90,242,0.5)' }}>
                LV {level}
              </span>
            </div>
            <div style={{
              marginTop: 4, width: isMobile ? 120 : 110, height: isMobile ? 12 : 10,
              borderRadius: 99, overflow: 'hidden',
              background: 'rgba(255,255,255,0.08)', border: '1px solid rgba(191,90,242,0.3)',
            }}>
              <div style={{
                height: '100%', borderRadius: 99, width: `${xpPct}%`,
                background: 'linear-gradient(90deg, #bf5af2, #e080ff)',
                boxShadow: '0 0 8px rgba(191,90,242,0.5)', transition: 'width 0.15s',
              }} />
            </div>
            <span style={{ fontSize: fs(11), marginTop: 2, fontWeight: 700, color: 'rgba(191,90,242,0.8)' }}>
              {xp}/{xpToNext} XP
            </span>

            {/* Coop peer HP bars */}
            {coopPeers && coopPeers.length > 0 && (
              <div className="flex flex-col" style={{ gap: 3, marginTop: 6 }}>
                {coopPeers.map((p, i) => {
                  const pColor = SHIP_COLORS[p.shipClass] || '#39ff14';
                  const hpPct = p.maxHp > 0 ? Math.max(0, (p.hp / p.maxHp) * 100) : 0;
                  return (
                    <div key={i} className="flex items-center" style={{ gap: 4 }}>
                      <span style={{ fontSize: fs(9), fontWeight: 900, color: pColor }}>{p.label}</span>
                      <div style={{
                        width: isMobile ? 60 : 50, height: 6, borderRadius: 99, overflow: 'hidden',
                        background: 'rgba(255,255,255,0.06)', border: `1px solid ${pColor}44`,
                      }}>
                        <div style={{
                          height: '100%', borderRadius: 99, width: `${hpPct}%`,
                          background: p.alive ? pColor : '#333',
                          transition: 'width 0.2s',
                        }} />
                      </div>
                      <span style={{ fontSize: fs(8), color: p.alive ? '#aaa' : '#ff4060', fontWeight: 700 }}>
                        {p.alive ? `${p.hp}/${p.maxHp}` : 'DEAD'}
                      </span>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* ===== BOTTOM BAR: Weapons + Passives ===== */}
      <div className="absolute left-0 right-0" style={{
        bottom: 0,
        padding: isMobile ? '32px 10px 70px' : '32px 12px 12px',
        background: 'linear-gradient(to top, rgba(0,0,0,0.85) 0%, rgba(0,0,0,0.35) 55%, transparent 100%)',
      }}>
        <div className="flex items-end justify-between" style={{ gap: 12 }}>
          {/* Weapon slots */}
          <div className="flex" style={{ gap: isMobile ? 6 : 6 }}>
            {Array.from({ length: weaponSlots }).map((_, i) => {
              const weaponId = equippedWeapons[i];
              const ability = weaponId ? abilityMap[weaponId] : null;
              const lv = weaponId ? (abilityLevels[weaponId] || 0) : 0;
              const sz = isMobile ? 50 : 46;
              return (
                <div key={i} className="relative">
                  <div className="flex items-center justify-center" style={{
                    width: sz, height: sz, borderRadius: 10,
                    background: ability ? 'rgba(255,100,0,0.18)' : 'rgba(255,255,255,0.03)',
                    border: `2px solid ${ability ? 'rgba(255,100,0,0.55)' : 'rgba(255,255,255,0.08)'}`,
                    boxShadow: ability ? '0 0 10px rgba(255,100,0,0.25), inset 0 0 8px rgba(255,100,0,0.1)' : 'none',
                  }}>
                    {ability ? (
                      <span style={{ fontSize: fs(22) }}>{ability.icon}</span>
                    ) : (
                      <span style={{ fontSize: fs(12), color: '#333' }}>—</span>
                    )}
                  </div>
                  {lv > 0 && (
                    <div className="absolute flex items-center justify-center" style={{
                      top: -6, right: -6, width: 20, height: 20, borderRadius: 99,
                      fontSize: 11, fontWeight: 900,
                      background: 'linear-gradient(135deg, #ff8c00, #ff6b00)', color: '#000',
                      boxShadow: '0 0 8px rgba(255,107,0,0.5)',
                    }}>
                      {lv}
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          {/* Passive icons */}
          {activePassives.length > 0 && (
            <div className="flex flex-wrap justify-end" style={{ gap: 4, maxWidth: '55%' }}>
              {activePassives.map(p => (
                <div key={p.id} className="relative">
                  <div className="flex items-center justify-center" style={{
                    width: isMobile ? 42 : 38, height: isMobile ? 42 : 38, borderRadius: 8,
                    background: 'rgba(0,255,255,0.1)', border: '1px solid rgba(0,255,255,0.3)',
                    boxShadow: '0 0 8px rgba(0,255,255,0.12)',
                  }}>
                    <span style={{ fontSize: fs(18) }}>{p.icon}</span>
                  </div>
                  <div className="absolute flex items-center justify-center" style={{
                    top: -4, right: -4, width: 18, height: 18, borderRadius: 99,
                    fontSize: 10, fontWeight: 900, background: '#0ff', color: '#000',
                  }}>
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
