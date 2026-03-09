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

  const s = isMobile ? 1.1 : 1;
  const fs = (base: number) => `${Math.round(base * s)}px`;

  const heartW = isMobile ? 20 : 22;
  const heartH = isMobile ? 18 : 20;

  return (
    <div className="absolute inset-0 pointer-events-none select-none z-10" style={{ fontFamily: "'Segoe UI', monospace" }}>
      
      {/* ===== TOP BAR ===== */}
      <div className="absolute top-0 left-0 right-0" style={{
        padding: isMobile ? '12px 12px 44px' : '10px 14px 44px',
        background: 'linear-gradient(to bottom, rgba(0,0,0,0.92) 0%, rgba(0,0,0,0.55) 55%, transparent 100%)',
      }}>
        
        <div className="flex items-start justify-between" style={{ gap: isMobile ? 8 : 14 }}>
          {/* LEFT: HP + SP + Stats */}
          <div className="flex flex-col shrink-0" style={{ gap: isMobile ? 6 : 6, minWidth: 0 }}>
            {/* Ship class badge */}
            <div className="flex items-center" style={{ gap: 6 }}>
              <span style={{
                fontSize: fs(12), fontWeight: 900, padding: '2px 8px', borderRadius: 5,
                background: `${SHIP_COLORS[player.class] || '#fff'}33`,
                border: `1px solid ${SHIP_COLORS[player.class] || '#fff'}66`,
                color: SHIP_COLORS[player.class] || '#fff',
                textTransform: 'uppercase' as const, letterSpacing: '0.12em',
              }}>{player.class}</span>
              <span style={{ fontSize: fs(11), fontWeight: 700, color: '#8090bb' }}>
                DMG: {player.damage}
              </span>
            </div>

            {/* HP hearts - BIGGER and more visible */}
            <div className="flex items-center" style={{ gap: isMobile ? 6 : 7 }}>
              <span style={{ fontSize: fs(17), fontWeight: 900, color: '#ff4060', textShadow: '0 0 10px rgba(255,64,96,0.7)' }}>HP</span>
              <div className="flex" style={{ gap: isMobile ? 4 : 5 }}>
                {Array.from({ length: player.maxHp }).map((_, i) => (
                  <div key={i} style={{
                    width: heartW, height: heartH, borderRadius: 4,
                    background: i < player.hp
                      ? 'linear-gradient(to bottom, #ff5070, #cc2040)'
                      : 'rgba(255,255,255,0.06)',
                    boxShadow: i < player.hp
                      ? '0 0 12px rgba(255,64,96,0.8), inset 0 2px 0 rgba(255,255,255,0.25)'
                      : 'inset 0 0 4px rgba(255,255,255,0.05)',
                    border: i < player.hp
                      ? '1.5px solid rgba(255,120,140,0.6)'
                      : '1.5px solid rgba(255,255,255,0.08)',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                  }}>
                    {i < player.hp && (
                      <span style={{ fontSize: isMobile ? 14 : 12, filter: 'drop-shadow(0 0 3px rgba(255,64,96,0.8))' }}>❤️</span>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* SP bar - bigger */}
            <div className="flex items-center" style={{ gap: isMobile ? 6 : 7 }}>
              <span style={{
                fontSize: fs(17), fontWeight: 900,
                color: specialReady ? '#bf5af2' : '#5a2080',
                textShadow: specialReady ? '0 0 10px rgba(191,90,242,0.7)' : 'none',
              }}>SP</span>
              <div style={{
                width: isMobile ? 120 : 110, height: isMobile ? 16 : 14,
                borderRadius: 99, overflow: 'hidden',
                background: 'rgba(255,255,255,0.08)', border: '1.5px solid rgba(191,90,242,0.4)',
              }}>
                <div style={{
                  height: '100%', borderRadius: 99, width: `${specialPct}%`,
                  background: specialReady ? 'linear-gradient(90deg, #bf5af2, #e080ff)' : 'linear-gradient(90deg, #3a1060, #5a2080)',
                  boxShadow: specialReady ? '0 0 14px #bf5af2, 0 0 6px #e080ff' : 'none',
                  transition: 'width 0.15s',
                }} />
              </div>
              {specialReady && (
                <span style={{ fontSize: fs(12), fontWeight: 900, color: '#e080ff', textShadow: '0 0 8px #bf5af2', animation: 'pulse 1s infinite' }}>⚡ READY</span>
              )}
            </div>

            {/* Kill counter */}
            <div className="flex items-center" style={{ gap: 6 }}>
              <span style={{ fontSize: fs(12), fontWeight: 700, color: '#ff4060' }}>💀 {enemiesKilled}</span>
              <span style={{ fontSize: fs(10), fontWeight: 600, color: '#6080aa' }}>({enemiesKilledThisWave} esta wave)</span>
            </div>

            {/* Active effects - bigger badges */}
            <div className="flex" style={{ gap: 5 }}>
              {player.shieldTimer > 0 && (
                <span style={{ fontSize: fs(13), padding: '2px 7px', borderRadius: 6, fontWeight: 800, background: 'rgba(0,255,255,0.2)', color: '#0ff', border: '1.5px solid rgba(0,255,255,0.5)' }}>🛡️ {Math.ceil(player.shieldTimer)}s</span>
              )}
              {player.tripleTimer > 0 && (
                <span style={{ fontSize: fs(13), padding: '2px 7px', borderRadius: 6, fontWeight: 800, background: 'rgba(255,20,147,0.2)', color: '#ff1493', border: '1.5px solid rgba(255,20,147,0.5)' }}>3× {Math.ceil(player.tripleTimer)}s</span>
              )}
              {player.speedBoostTimer > 0 && (
                <span style={{ fontSize: fs(13), padding: '2px 7px', borderRadius: 6, fontWeight: 800, background: 'rgba(0,229,255,0.2)', color: '#00e5ff', border: '1.5px solid rgba(0,229,255,0.5)' }}>⚡ {Math.ceil(player.speedBoostTimer)}s</span>
              )}
            </div>
          </div>

          {/* CENTER: Wave + Combo */}
          <div className="flex flex-col items-center shrink-0">
            <div style={{
              padding: isMobile ? '6px 18px' : '5px 16px', borderRadius: 99,
              fontSize: fs(17), fontWeight: 900, letterSpacing: '0.12em',
              background: 'rgba(0,255,255,0.18)', border: '2px solid rgba(0,255,255,0.5)',
              color: '#0ff', textShadow: '0 0 12px rgba(0,255,255,0.6)',
            }}>
              WAVE {wave}
            </div>
            {combo > 1 && comboTimer > 0 && (
              <div className="flex items-center" style={{ gap: 6, marginTop: 5 }}>
                <span style={{
                  fontSize: fs(26), fontWeight: 900,
                  color: comboMultiplier >= 8 ? '#ff1493' : comboMultiplier >= 4 ? '#ffff00' : '#0ff',
                  textShadow: `0 0 14px ${comboMultiplier >= 8 ? '#ff1493' : comboMultiplier >= 4 ? '#ffff00' : '#0ff'}`,
                }}>×{comboMultiplier}</span>
                <div style={{ width: 55, height: 7, borderRadius: 99, overflow: 'hidden', background: 'rgba(255,255,255,0.12)' }}>
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
              <div style={{ fontSize: fs(10), fontWeight: 700, color: '#0ff', opacity: 0.8, marginBottom: -2 }}>
                PONTUAÇÃO COMPARTILHADA
              </div>
            )}
            <div style={{
              fontSize: fs(28), fontWeight: 900, fontVariantNumeric: 'tabular-nums',
              color: '#ffff00', textShadow: '0 0 14px rgba(255,255,0,0.6)', letterSpacing: '0.5px',
            }}>
              {score.toLocaleString()}
            </div>
            <div className="flex items-center" style={{ gap: 6, marginTop: 3 }}>
              <span style={{ fontSize: fs(18), fontWeight: 900, color: '#bf5af2', textShadow: '0 0 10px rgba(191,90,242,0.6)' }}>
                LV {level}
              </span>
            </div>
            <div style={{
              marginTop: 5, width: isMobile ? 130 : 120, height: isMobile ? 14 : 12,
              borderRadius: 99, overflow: 'hidden',
              background: 'rgba(255,255,255,0.08)', border: '1.5px solid rgba(191,90,242,0.35)',
            }}>
              <div style={{
                height: '100%', borderRadius: 99, width: `${xpPct}%`,
                background: 'linear-gradient(90deg, #bf5af2, #e080ff)',
                boxShadow: '0 0 10px rgba(191,90,242,0.5)', transition: 'width 0.15s',
              }} />
            </div>
            <span style={{ fontSize: fs(12), marginTop: 2, fontWeight: 700, color: 'rgba(191,90,242,0.85)' }}>
              {xp}/{xpToNext} XP
            </span>

            {/* Coop peer HP bars */}
            {coopPeers && coopPeers.length > 0 && (
              <div className="flex flex-col" style={{ gap: 4, marginTop: 8 }}>
                {coopPeers.map((p, i) => {
                  const pColor = SHIP_COLORS[p.shipClass] || '#39ff14';
                  const hpPct = p.maxHp > 0 ? Math.max(0, (p.hp / p.maxHp) * 100) : 0;
                  return (
                    <div key={i} className="flex items-center" style={{ gap: 5 }}>
                      <span style={{ fontSize: fs(10), fontWeight: 900, color: pColor }}>{p.label}</span>
                      <div style={{
                        width: isMobile ? 65 : 55, height: 8, borderRadius: 99, overflow: 'hidden',
                        background: 'rgba(255,255,255,0.06)', border: `1.5px solid ${pColor}55`,
                      }}>
                        <div style={{
                          height: '100%', borderRadius: 99, width: `${hpPct}%`,
                          background: p.alive ? pColor : '#333',
                          transition: 'width 0.2s',
                        }} />
                      </div>
                      <span style={{ fontSize: fs(9), color: p.alive ? '#aaa' : '#ff4060', fontWeight: 700 }}>
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
        padding: isMobile ? '36px 12px 74px' : '36px 14px 14px',
        background: 'linear-gradient(to top, rgba(0,0,0,0.9) 0%, rgba(0,0,0,0.4) 55%, transparent 100%)',
      }}>
        <div className="flex items-end justify-between" style={{ gap: 14 }}>
          {/* Weapon slots - MUCH BIGGER with labels */}
          <div className="flex" style={{ gap: isMobile ? 8 : 7 }}>
            {Array.from({ length: weaponSlots }).map((_, i) => {
              const weaponId = equippedWeapons[i];
              const ability = weaponId ? abilityMap[weaponId] : null;
              const lv = weaponId ? (abilityLevels[weaponId] || 0) : 0;
              const sz = isMobile ? 46 : 54;
              return (
                <div key={i} className="relative flex flex-col items-center">
                  <div className="flex items-center justify-center" style={{
                    width: sz, height: sz, borderRadius: 12,
                    background: ability ? 'rgba(255,100,0,0.2)' : 'rgba(255,255,255,0.03)',
                    border: `2px solid ${ability ? 'rgba(255,100,0,0.6)' : 'rgba(255,255,255,0.08)'}`,
                    boxShadow: ability ? '0 0 14px rgba(255,100,0,0.3), inset 0 0 10px rgba(255,100,0,0.12)' : 'none',
                  }}>
                    {ability ? (
                      <span style={{ fontSize: fs(28), filter: 'drop-shadow(0 0 4px rgba(255,100,0,0.5))' }}>{ability.icon}</span>
                    ) : (
                      <span style={{ fontSize: fs(16), color: '#333' }}>—</span>
                    )}
                  </div>
                  {/* Weapon name label */}
                  {ability && (
                    <span style={{
                      fontSize: isMobile ? 8 : 7, fontWeight: 800, color: '#ff8c00',
                      textShadow: '0 0 4px rgba(255,100,0,0.4)',
                      maxWidth: sz + 4, overflow: 'hidden', textOverflow: 'ellipsis',
                      whiteSpace: 'nowrap', textAlign: 'center', marginTop: 2,
                    }}>
                      {ability.name}
                    </span>
                  )}
                  {lv > 0 && (
                    <div className="absolute flex items-center justify-center" style={{
                      top: -7, right: -7, width: 22, height: 22, borderRadius: 99,
                      fontSize: 12, fontWeight: 900,
                      background: 'linear-gradient(135deg, #ff8c00, #ff6b00)', color: '#000',
                      boxShadow: '0 0 10px rgba(255,107,0,0.6)',
                      border: '1.5px solid rgba(255,200,100,0.5)',
                    }}>
                      {lv}
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          {/* Passive icons - BIGGER with labels */}
          {activePassives.length > 0 && (
            <div className="flex flex-wrap justify-end" style={{ gap: 6, maxWidth: '55%' }}>
              {activePassives.map(p => (
                <div key={p.id} className="relative flex flex-col items-center">
                  <div className="flex items-center justify-center" style={{
                    width: isMobile ? 40 : 44, height: isMobile ? 40 : 44, borderRadius: 10,
                    background: 'rgba(0,255,255,0.12)', border: '1.5px solid rgba(0,255,255,0.4)',
                    boxShadow: '0 0 10px rgba(0,255,255,0.15)',
                  }}>
                    <span style={{ fontSize: fs(22), filter: 'drop-shadow(0 0 3px rgba(0,255,255,0.5))' }}>{p.icon}</span>
                  </div>
                  {/* Passive name */}
                  <span style={{
                    fontSize: isMobile ? 7 : 6, fontWeight: 800, color: '#0ff',
                    maxWidth: isMobile ? 50 : 44, overflow: 'hidden', textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap', textAlign: 'center', marginTop: 1,
                  }}>
                    {p.name}
                  </span>
                  <div className="absolute flex items-center justify-center" style={{
                    top: -5, right: -5, width: 20, height: 20, borderRadius: 99,
                    fontSize: 11, fontWeight: 900, background: '#0ff', color: '#000',
                    border: '1.5px solid rgba(0,200,255,0.5)',
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