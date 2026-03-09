import React, { useState } from 'react';
import {
  ALL_ACHIEVEMENTS, Achievement, AchievementDifficulty,
  DIFFICULTY_COLORS, DIFFICULTY_LABELS,
} from '../../game/achievements';
import { playClick, playHover, playBack } from '../../game/audio';

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

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-[#000008] text-[#e0e8ff] select-none p-4">
      <h1 className="text-4xl md:text-5xl font-bold mb-2 font-mono" style={{ color: '#ffd700', textShadow: '0 0 30px rgba(255,215,0,0.4)' }}>
        🏆 CONQUISTAS
      </h1>

      <div className="flex items-center gap-2 mb-4 py-2 px-5 rounded-lg" style={{ background: 'rgba(255,215,0,0.1)', border: '1px solid rgba(255,215,0,0.25)' }}>
        <span className="font-mono font-bold text-lg" style={{ color: '#ffd700' }}>{totalUnlocked}</span>
        <span className="font-mono text-xs text-[#6080aa]">/ {total} desbloqueadas</span>
      </div>

      {/* Progress bar */}
      <div className="w-64 h-2 rounded-full mb-4" style={{ background: 'rgba(255,255,255,0.05)' }}>
        <div className="h-full rounded-full transition-all" style={{
          width: `${(totalUnlocked / total) * 100}%`,
          background: 'linear-gradient(90deg, #ffd700, #ff8800)',
          boxShadow: '0 0 10px rgba(255,215,0,0.4)',
        }} />
      </div>

      {/* Tabs */}
      <div className="flex flex-wrap gap-1.5 mb-4 justify-center">
        {TABS.map(t => (
          <button key={t.key}
            onClick={() => { playClick(); setTab(t.key); }}
            onMouseEnter={playHover}
            className="px-2.5 py-1 rounded-lg font-mono text-xs font-bold transition-all"
            style={{
              background: tab === t.key ? `${t.color}22` : 'rgba(255,255,255,0.03)',
              border: `1px solid ${tab === t.key ? t.color + '88' : 'rgba(255,255,255,0.08)'}`,
              color: tab === t.key ? t.color : '#6080aa',
            }}>
            {t.label}
          </button>
        ))}
      </div>

      {/* Achievement grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-2 max-w-6xl w-full mb-6 max-h-[58vh] overflow-y-auto pr-1"
        style={{ scrollbarWidth: 'thin', scrollbarColor: '#ffd70033 transparent' }}>
        {filtered.map(a => {
          const isUnlocked = unlocked[a.id];
          const diffColor = DIFFICULTY_COLORS[a.difficulty];
          return (
            <div key={a.id}
              className="flex flex-col items-center p-3 rounded-xl border transition-all font-mono relative"
              style={{
                background: isUnlocked ? `${diffColor}08` : 'rgba(0,0,20,0.9)',
                borderColor: isUnlocked ? diffColor + '44' : 'rgba(255,255,255,0.05)',
                opacity: isUnlocked ? 1 : 0.5,
              }}>
              {/* Difficulty badge */}
              <div className="absolute top-1.5 right-1.5 text-[8px] px-1 py-0.5 rounded font-bold"
                style={{ background: diffColor + '22', color: diffColor }}>
                {DIFFICULTY_LABELS[a.difficulty]}
              </div>
              {isUnlocked && (
                <div className="absolute top-1.5 left-1.5 text-[9px] px-1 py-0.5 rounded font-bold"
                  style={{ background: 'rgba(0,255,100,0.2)', color: '#00ff64' }}>✓</div>
              )}
              <span className="text-2xl mb-1">{a.icon}</span>
              <h3 className="text-[10px] font-bold mb-0.5 text-center" style={{ color: isUnlocked ? diffColor : '#555' }}>
                {a.name}
              </h3>
              <p className="text-[8px] text-[#6080aa] text-center leading-tight">{a.description}</p>
              {a.mapId && (
                <span className="text-[7px] mt-1 px-1 rounded" style={{ background: 'rgba(0,255,255,0.1)', color: '#0ff' }}>
                  {a.mapId}
                </span>
              )}
            </div>
          );
        })}
      </div>

      <button onClick={() => { playBack(); onBack(); }} onMouseEnter={playHover}
        className="py-2.5 px-6 text-base font-bold rounded-lg text-[#6080aa] border border-[#6080aa]/30 transition-all duration-200 hover:border-[#0ff] hover:text-[#0ff] font-mono"
        style={{ background: 'rgba(0,255,255,0.03)' }}>
        ← Voltar
      </button>
    </div>
  );
};

export default Achievements;
