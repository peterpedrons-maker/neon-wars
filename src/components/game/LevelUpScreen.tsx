import React, { useMemo, useEffect } from 'react';
import { Ability, getRandomAbilities } from '../../game/abilities';
import { playClick, playHover, playLevelUp } from '../../game/audio';
import { ABILITY_ICONS } from '../../game/icons';
import { useLanguage } from '../../game/i18n';

interface LevelUpScreenProps {
  level: number;
  abilityLevels: Record<string, number>;
  equippedWeapons: string[];
  weaponSlots: number;
  unlockedAbilities: string[];
  onSelect: (ability: Ability) => void;
}

const LevelUpScreen: React.FC<LevelUpScreenProps> = ({ level, abilityLevels, equippedWeapons, weaponSlots, unlockedAbilities, onSelect }) => {
  const { t } = useLanguage();
  const abilities = useMemo(() => getRandomAbilities(3, abilityLevels, weaponSlots, equippedWeapons, unlockedAbilities), [level]);

  useEffect(() => { playLevelUp(); }, []);

  return (
    <div className="absolute inset-0 flex flex-col items-center justify-center bg-black/80 z-20 select-none p-4">
      <div className="text-3xl md:text-4xl font-bold mb-1 font-mono animate-pulse"
        style={{ color: '#ffff00', textShadow: '0 0 20px rgba(255,255,0,0.6)' }}>
        {t('level_up')}
      </div>
      <p className="text-[#6080aa] mb-1 text-sm font-mono">{t('level_label')} {level}</p>
      <p className="text-[#8090bb] mb-1 text-xs font-mono">
        🔫 {t('weapons_slots')}: {equippedWeapons.length}/{weaponSlots} slots
      </p>
      <p className="text-[#8090bb] mb-4 text-base font-mono">{t('choose_ability')}</p>

      <div className="flex flex-col md:flex-row gap-4">
        {abilities.map(a => {
          const currentLv = abilityLevels[a.id] || 0;
          const isWeapon = a.category === 'weapon';
          const isNewWeapon = isWeapon && !equippedWeapons.includes(a.id);
          const borderHue = isWeapon ? 'rgba(255,100,0,0.2)' : 'rgba(0,255,255,0.2)';
          
          return (
            <button
              key={a.id}
              onClick={() => { playClick(); onSelect(a); }}
              onMouseEnter={playHover}
              className="flex flex-col items-center p-5 rounded-xl border transition-all duration-200 hover:scale-105 active:scale-95 w-52 font-mono"
              style={{
                borderColor: borderHue,
                background: 'rgba(0,0,20,0.95)',
                boxShadow: '0 4px 20px rgba(0,0,0,0.5)',
              }}
              onMouseLeave={e => {
                (e.currentTarget as HTMLElement).style.borderColor = borderHue;
                (e.currentTarget as HTMLElement).style.boxShadow = '0 4px 20px rgba(0,0,0,0.5)';
              }}
            >
              <div className="flex items-center gap-1 mb-1">
                <span className="text-[9px] px-1.5 py-0.5 rounded font-bold" style={{
                  background: isWeapon ? 'rgba(255,100,0,0.2)' : 'rgba(0,255,255,0.2)',
                  color: isWeapon ? '#ff6b00' : '#0ff',
                }}>
                  {isWeapon ? t('weapon_tag') : t('passive_tag')}
                </span>
                {isNewWeapon && (
                  <span className="text-[9px] px-1.5 py-0.5 rounded font-bold" style={{
                    background: 'rgba(255,255,0,0.2)', color: '#ffff00',
                  }}>
                    {t('new_tag')}
                  </span>
                )}
              </div>
              {ABILITY_ICONS[a.id] ? (
                <img src={ABILITY_ICONS[a.id]} alt={a.name} className="w-12 h-12 object-contain mb-2" />
              ) : (
                <span className="text-4xl mb-2">{a.icon}</span>
              )}
              <h3 className="text-lg font-bold mb-1" style={{ color: isWeapon ? '#ff6b00' : '#0ff' }}>
                {a.name}
              </h3>
              <p className="text-xs text-[#6080aa] text-center mb-2">{a.description}</p>
              <div className="flex gap-1">
                {Array.from({ length: a.maxLevel }).map((_, i) => (
                  <div key={i} className="w-2 h-2 rounded-full" style={{
                    background: i <= currentLv ? (isWeapon ? '#ff6b00' : '#0ff') : '#1a2040',
                    boxShadow: i <= currentLv ? `0 0 4px ${isWeapon ? '#ff6b00' : '#0ff'}` : 'none',
                  }} />
                ))}
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
};

export default LevelUpScreen;
