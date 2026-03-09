import React, { useState, useEffect } from 'react';
import {
  ALL_ACHIEVEMENTS, Achievement, AchievementDifficulty,
  DIFFICULTY_COLORS, DIFFICULTY_LABELS,
} from '../../game/achievements';
import { playClick, playHover, playBack, startAchievementsMusic, stopAchievementsMusic } from '../../game/audio';
import { getAchievementIcon } from '../../game/icons';

interface AchievementsProps {
  unlocked: Record<string, boolean>;
  onBack: () => void;
}

const TABS: { key: 'all' | 'global' | AchievementDifficulty; label: string; color: string }[] = [
  { key: 'all', label: 'Todas', color: '#0ff' },
  { key: 'global', label: 'Globais', color: '#bf5af2' },
  { key: 'easy', label: 'Fácil', color: DIFFICULTY_COLORS.easy },
  { key: 'moderate', label: 'Moderada', color: DIFFICULTY_COLORS.moderate },
  { key: 'hard', label: 'Difícil', color: DIFFICULTY_COLORS.hard },
  { key: 'extreme', label: 'Extrema', color: DIFFICULTY_COLORS.extreme },
];

const Achievements: React.FC<AchievementsProps> = ({ unlocked, onBack }) => {
  const [tab, setTab] = useState<string>('all');

  const filtered = ALL_ACHIEVEMENTS.filter(a => {
    if (tab === 'all') return true;
    if (tab === 'global') return !a.mapId;
    return a.difficulty === tab;
  });

  const totalUnlocked = ALL_ACHIEVEMENTS.filter(a => unlocked[a.id]).length;
  const total = ALL_ACHIEVEMENTS.length;
  const pct = Math.round((totalUnlocked / total) * 100);

  // Group by difficulty for "all" tab
  const grouped = tab === 'all' ? {
    easy: filtered.filter(a => a.difficulty === 'easy'),
    moderate: filtered.filter(a => a.difficulty === 'moderate'),
    hard: filtered.filter(a => a.difficulty === 'hard'),
    extreme: filtered.filter(a => a.difficulty === 'extreme'),
  } : null;

  const renderAchievement = (a: Achievement) => {
    const isUnlocked = unlocked[a.id];
    const diffColor = DIFFICULTY_COLORS[a.difficulty];
    const iconSrc = getAchievementIcon(a.id);

    return (
      <div key={a.id}
        className="flex items-center gap-3 p-3 rounded-xl border transition-all font-mono"
        style={{
          background: isUnlocked
            ? `linear-gradient(135deg, ${diffColor}08, ${diffColor}04)`
            : 'rgba(0,0,20,0.7)',
          borderColor: isUnlocked ? diffColor + '44' : 'rgba(255,255,255,0.05)',
          opacity: isUnlocked ? 1 : 0.55,
        }}>
        {/* Icon */}
        <div className="w-10 h-10 shrink-0 rounded-lg flex items-center justify-center"
          style={{ background: isUnlocked ? `${diffColor}15` : 'rgba(255,255,255,0.03)' }}>
          {iconSrc ? (
            <img src={iconSrc} alt="" className="w-8 h-8 object-contain" style={{ filter: isUnlocked ? 'none' : 'grayscale(1) brightness(0.4)' }} />
          ) : (
            <span className="text-xl" style={{ filter: isUnlocked ? 'none' : 'grayscale(1)' }}>{a.icon}</span>
          )}
        </div>

        {/* Info */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-0.5">
            <h3 className="text-xs font-bold truncate" style={{ color: isUnlocked ? diffColor : '#555' }}>
              {a.name}
            </h3>
            {isUnlocked && (
              <span className="text-[8px] px-1 py-0.5 rounded font-bold shrink-0"
                style={{ background: 'rgba(0,255,100,0.15)', color: '#00ff64' }}>✓</span>
            )}
          </div>
          <p className="text-[9px] text-[#6080aa] leading-tight truncate">{a.description}</p>
        </div>

        {/* Badges */}
        <div className="flex flex-col items-end gap-1 shrink-0">
          <span className="text-[7px] px-1.5 py-0.5 rounded font-bold"
            style={{ background: diffColor + '18', color: diffColor }}>
            {DIFFICULTY_LABELS[a.difficulty]}
          </span>
          {a.mapId && (
            <span className="text-[7px] px-1 py-0.5 rounded"
              style={{ background: 'rgba(0,255,255,0.08)', color: '#0ff' }}>
              {a.mapId}
            </span>
          )}
        </div>
      </div>
    );
  };

  const renderSection = (title: string, items: Achievement[], color: string) => {
    const sectionUnlocked = items.filter(a => unlocked[a.id]).length;
    return (
      <div key={title} className="mb-4">
        <div className="flex items-center gap-2 mb-2 px-1">
          <div className="w-2 h-2 rounded-full" style={{ background: color, boxShadow: `0 0 6px ${color}` }} />
          <span className="text-xs font-bold font-mono" style={{ color }}>{title}</span>
          <span className="text-[10px] font-mono text-[#6080aa]">{sectionUnlocked}/{items.length}</span>
          <div className="flex-1 h-px" style={{ background: `${color}22` }} />
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-1.5">
          {items.map(renderAchievement)}
        </div>
      </div>
    );
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-[#000008] text-[#e0e8ff] select-none p-4">
      <h1 className="text-3xl md:text-4xl font-bold mb-2 font-mono" style={{ color: '#ffd700', textShadow: '0 0 30px rgba(255,215,0,0.4)' }}>
        🏆 CONQUISTAS
      </h1>

      {/* Stats bar */}
      <div className="flex items-center gap-4 mb-3">
        <div className="flex items-center gap-2 py-1.5 px-4 rounded-lg" style={{ background: 'rgba(255,215,0,0.08)', border: '1px solid rgba(255,215,0,0.2)' }}>
          <span className="font-mono font-bold text-lg" style={{ color: '#ffd700' }}>{totalUnlocked}</span>
          <span className="font-mono text-xs text-[#6080aa]">/ {total}</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-32 h-2.5 rounded-full overflow-hidden" style={{ background: 'rgba(255,255,255,0.05)' }}>
            <div className="h-full rounded-full transition-all duration-500" style={{
              width: `${pct}%`,
              background: 'linear-gradient(90deg, #ffd700, #ff8800)',
              boxShadow: '0 0 8px rgba(255,215,0,0.4)',
            }} />
          </div>
          <span className="font-mono text-xs font-bold" style={{ color: '#ffd700' }}>{pct}%</span>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex flex-wrap gap-1.5 mb-4 justify-center">
        {TABS.map(t => (
          <button key={t.key}
            onClick={() => { playClick(); setTab(t.key); }}
            onMouseEnter={playHover}
            className="px-3 py-1.5 rounded-lg font-mono text-xs font-bold transition-all"
            style={{
              background: tab === t.key ? `${t.color}22` : 'rgba(255,255,255,0.03)',
              border: `1px solid ${tab === t.key ? t.color + '88' : 'rgba(255,255,255,0.08)'}`,
              color: tab === t.key ? t.color : '#6080aa',
              boxShadow: tab === t.key ? `0 0 10px ${t.color}22` : 'none',
            }}>
            {t.label}
          </button>
        ))}
      </div>

      {/* Achievement list */}
      <div className="w-full max-w-3xl max-h-[60vh] overflow-y-auto pr-1"
        style={{ scrollbarWidth: 'thin', scrollbarColor: '#ffd70033 transparent' }}>
        {grouped ? (
          <>
            {renderSection('⚡ Fácil', grouped.easy, DIFFICULTY_COLORS.easy)}
            {renderSection('⭐ Moderada', grouped.moderate, DIFFICULTY_COLORS.moderate)}
            {renderSection('🔥 Difícil', grouped.hard, DIFFICULTY_COLORS.hard)}
            {renderSection('💀 Extrema', grouped.extreme, DIFFICULTY_COLORS.extreme)}
          </>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-1.5">
            {filtered.map(renderAchievement)}
          </div>
        )}
      </div>

      <button onClick={() => { playBack(); onBack(); }} onMouseEnter={playHover}
        className="mt-4 py-2.5 px-6 text-base font-bold rounded-lg text-[#6080aa] border border-[#6080aa]/30 transition-all duration-200 hover:border-[#0ff] hover:text-[#0ff] font-mono"
        style={{ background: 'rgba(0,255,255,0.03)' }}>
        ← Voltar
      </button>
    </div>
  );
};

export default Achievements;
