// Roguelike Meta-Progression System
// Persisted in localStorage across runs

import { ShipType } from './types';

export interface Milestone {
  id: string;
  name: string;
  description: string;
  icon: string;
  requirement: (stats: RunStats) => boolean;
  reward: UnlockReward;
  unlocked: boolean;
}

export interface UnlockReward {
  type: 'ship' | 'map' | 'ability' | 'passive_slot' | 'weapon_slot';
  id: string;
  name: string;
}

export interface RunStats {
  totalKills: number;
  totalRuns: number;
  highestWave: number;
  highestScore: number;
  totalPlasma: number;
  totalXpCollected: number;
  bossesKilled: number;
  maxCombo: number;
  classesPlayed: string[];
}

export interface MetaProgress {
  plasma: number;          // persistent currency
  totalPlasma: number;     // lifetime earned
  stats: RunStats;
  unlockedShips: string[];
  unlockedMaps: string[];
  unlockedAbilities: string[];
  milestones: Record<string, boolean>;
  weaponSlots: number;     // starts at 3, can be upgraded
}

const DEFAULT_META: MetaProgress = {
  plasma: 0,
  totalPlasma: 0,
  stats: {
    totalKills: 0,
    totalRuns: 0,
    highestWave: 0,
    highestScore: 0,
    totalPlasma: 0,
    totalXpCollected: 0,
    bossesKilled: 0,
    maxCombo: 0,
    classesPlayed: [],
  },
  unlockedShips: ['phantom', 'interceptor', 'titan'],
  unlockedMaps: ['neon-grid'],
  unlockedAbilities: [],
  milestones: {},
  weaponSlots: 3,
};

const STORAGE_KEY = 'neonwars_meta';

export function loadMeta(): MetaProgress {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) {
      const parsed = JSON.parse(raw);
      return { ...DEFAULT_META, ...parsed, stats: { ...DEFAULT_META.stats, ...parsed.stats } };
    }
  } catch {}
  return { ...DEFAULT_META };
}

export function saveMeta(meta: MetaProgress) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(meta));
  } catch {}
}

export function calculatePlasmaEarned(score: number, wave: number, kills: number, bossKills: number): number {
  return Math.floor(score * 0.01 + wave * 5 + kills * 0.5 + bossKills * 20);
}

export function endRun(
  meta: MetaProgress,
  score: number,
  wave: number,
  kills: number,
  bossKills: number,
  maxCombo: number,
  shipClass: ShipType,
): { plasma: number; newMilestones: Milestone[] } {
  const plasmaEarned = calculatePlasmaEarned(score, wave, kills, bossKills);
  
  meta.plasma += plasmaEarned;
  meta.totalPlasma += plasmaEarned;
  meta.stats.totalKills += kills;
  meta.stats.totalRuns++;
  meta.stats.highestWave = Math.max(meta.stats.highestWave, wave);
  meta.stats.highestScore = Math.max(meta.stats.highestScore, score);
  meta.stats.totalPlasma += plasmaEarned;
  meta.stats.bossesKilled += bossKills;
  meta.stats.maxCombo = Math.max(meta.stats.maxCombo, maxCombo);
  if (!meta.stats.classesPlayed.includes(shipClass)) {
    meta.stats.classesPlayed.push(shipClass);
  }

  // Check milestones
  const newMilestones: Milestone[] = [];
  for (const m of ALL_MILESTONES) {
    if (!meta.milestones[m.id] && m.requirement(meta.stats)) {
      meta.milestones[m.id] = true;
      m.unlocked = true;
      newMilestones.push(m);
      
      // Apply reward
      switch (m.reward.type) {
        case 'ship':
          if (!meta.unlockedShips.includes(m.reward.id)) meta.unlockedShips.push(m.reward.id);
          break;
        case 'map':
          if (!meta.unlockedMaps.includes(m.reward.id)) meta.unlockedMaps.push(m.reward.id);
          break;
        case 'ability':
          if (!meta.unlockedAbilities.includes(m.reward.id)) meta.unlockedAbilities.push(m.reward.id);
          break;
        case 'weapon_slot':
          meta.weaponSlots = Math.min(6, meta.weaponSlots + 1);
          break;
      }
    }
  }

  saveMeta(meta);
  return { plasma: plasmaEarned, newMilestones };
}

export const ALL_MILESTONES: Milestone[] = [
  {
    id: 'first_blood',
    name: 'Primeiro Sangue',
    description: 'Mate 10 inimigos no total',
    icon: '🩸',
    requirement: (s) => s.totalKills >= 10,
    reward: { type: 'ability', id: 'frost_nova', name: 'Frost Nova' },
    unlocked: false,
  },
  {
    id: 'survivor',
    name: 'Sobrevivente',
    description: 'Chegue à wave 5',
    icon: '🛡️',
    requirement: (s) => s.highestWave >= 5,
    reward: { type: 'map', id: 'inferno', name: 'Mapa Inferno' },
    unlocked: false,
  },
  {
    id: 'slayer_100',
    name: 'Caçador',
    description: 'Mate 100 inimigos no total',
    icon: '⚔️',
    requirement: (s) => s.totalKills >= 100,
    reward: { type: 'ability', id: 'missile_barrage', name: 'Missile Barrage' },
    unlocked: false,
  },
  {
    id: 'boss_hunter',
    name: 'Caça-Chefe',
    description: 'Mate 3 bosses',
    icon: '👑',
    requirement: (s) => s.bossesKilled >= 3,
    reward: { type: 'ability', id: 'plasma_field', name: 'Plasma Field' },
    unlocked: false,
  },
  {
    id: 'combo_master',
    name: 'Combo Master',
    description: 'Alcance combo de 20',
    icon: '🔥',
    requirement: (s) => s.maxCombo >= 20,
    reward: { type: 'ability', id: 'lightning_ring', name: 'Lightning Ring' },
    unlocked: false,
  },
  {
    id: 'wave_10',
    name: 'Veterano',
    description: 'Chegue à wave 10',
    icon: '🌟',
    requirement: (s) => s.highestWave >= 10,
    reward: { type: 'map', id: 'void', name: 'Mapa Void' },
    unlocked: false,
  },
  {
    id: 'all_ships',
    name: 'Piloto Versátil',
    description: 'Jogue com todas as 3 naves',
    icon: '🚀',
    requirement: (s) => s.classesPlayed.length >= 3,
    reward: { type: 'ability', id: 'flame_trail', name: 'Flame Trail' },
    unlocked: false,
  },
  {
    id: 'slayer_500',
    name: 'Exterminador',
    description: 'Mate 500 inimigos no total',
    icon: '💀',
    requirement: (s) => s.totalKills >= 500,
    reward: { type: 'weapon_slot', id: 'slot_4', name: '+1 Slot de Arma' },
    unlocked: false,
  },
  {
    id: 'wave_15',
    name: 'Lenda',
    description: 'Chegue à wave 15',
    icon: '⭐',
    requirement: (s) => s.highestWave >= 15,
    reward: { type: 'map', id: 'crystal', name: 'Mapa Crystal' },
    unlocked: false,
  },
  {
    id: 'score_10k',
    name: 'Pontuação Épica',
    description: 'Faça 10.000 pontos em uma run',
    icon: '🏆',
    requirement: (s) => s.highestScore >= 10000,
    reward: { type: 'weapon_slot', id: 'slot_5', name: '+1 Slot de Arma' },
    unlocked: false,
  },
];
