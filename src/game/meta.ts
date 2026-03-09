// Roguelike Meta-Progression System
import { ShipType } from './types';

export interface Milestone {
  id: string; name: string; description: string; icon: string;
  requirement: (stats: RunStats) => boolean;
  reward: UnlockReward; unlocked: boolean;
}

export interface UnlockReward {
  type: 'ship' | 'map' | 'ability' | 'passive_slot' | 'weapon_slot';
  id: string; name: string;
}

export interface RunStats {
  totalKills: number; totalRuns: number; highestWave: number; highestScore: number;
  totalPlasma: number; totalXpCollected: number; bossesKilled: number; maxCombo: number;
  classesPlayed: string[];
}

export interface PermBonuses {
  hp?: number; damage?: number; speed?: number; magnet?: number;
  armor?: number; plasmaMultiplier?: number;
}

export interface MetaProgress {
  plasma: number; totalPlasma: number; stats: RunStats;
  unlockedShips: string[]; unlockedMaps: string[];
  unlockedAbilities: string[]; milestones: Record<string, boolean>;
  weaponSlots: number; permBonuses?: PermBonuses;
  achievements?: Record<string, boolean>;
}

const DEFAULT_META: MetaProgress = {
  plasma: 0, totalPlasma: 0,
  stats: { totalKills: 0, totalRuns: 0, highestWave: 0, highestScore: 0, totalPlasma: 0, totalXpCollected: 0, bossesKilled: 0, maxCombo: 0, classesPlayed: [] },
  unlockedShips: ['phantom', 'interceptor', 'titan'],
  unlockedMaps: ['neon-grid'],
  unlockedAbilities: [], milestones: {}, weaponSlots: 3, permBonuses: {},
  achievements: {},
};

const STORAGE_KEY = 'neonwars_meta';

export function loadMeta(): MetaProgress {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) {
      const parsed = JSON.parse(raw);
      return { ...DEFAULT_META, ...parsed, stats: { ...DEFAULT_META.stats, ...parsed.stats }, achievements: { ...parsed.achievements } };
    }
  } catch {}
  return { ...DEFAULT_META };
}

export function saveMeta(meta: MetaProgress) {
  try { localStorage.setItem(STORAGE_KEY, JSON.stringify(meta)); } catch {}
}

// REDUCED plasma formula - ~40% less than before
export function calculatePlasmaEarned(score: number, wave: number, kills: number, bossKills: number): number {
  return Math.floor(score * 0.005 + wave * 3 + kills * 0.25 + bossKills * 12);
}

export function endRun(
  meta: MetaProgress, score: number, wave: number, kills: number,
  bossKills: number, maxCombo: number, shipClass: ShipType,
): { plasma: number; newMilestones: Milestone[] } {
  const plasmaMultBonus = 1 + (meta.permBonuses?.plasmaMultiplier || 0);
  const plasmaEarned = Math.floor(calculatePlasmaEarned(score, wave, kills, bossKills) * plasmaMultBonus);
  
  meta.plasma += plasmaEarned;
  meta.totalPlasma += plasmaEarned;
  meta.stats.totalKills += kills;
  meta.stats.totalRuns++;
  meta.stats.highestWave = Math.max(meta.stats.highestWave, wave);
  meta.stats.highestScore = Math.max(meta.stats.highestScore, score);
  meta.stats.totalPlasma += plasmaEarned;
  meta.stats.bossesKilled += bossKills;
  meta.stats.maxCombo = Math.max(meta.stats.maxCombo, maxCombo);
  if (!meta.stats.classesPlayed.includes(shipClass)) meta.stats.classesPlayed.push(shipClass);

  const newMilestones: Milestone[] = [];
  for (const m of ALL_MILESTONES) {
    if (!meta.milestones[m.id] && m.requirement(meta.stats)) {
      meta.milestones[m.id] = true;
      m.unlocked = true;
      newMilestones.push(m);
      switch (m.reward.type) {
        case 'ship': if (!meta.unlockedShips.includes(m.reward.id)) meta.unlockedShips.push(m.reward.id); break;
        case 'map': if (!meta.unlockedMaps.includes(m.reward.id)) meta.unlockedMaps.push(m.reward.id); break;
        case 'ability': if (!meta.unlockedAbilities.includes(m.reward.id)) meta.unlockedAbilities.push(m.reward.id); break;
        case 'weapon_slot': meta.weaponSlots = Math.min(6, meta.weaponSlots + 1); break;
      }
    }
  }

  saveMeta(meta);
  return { plasma: plasmaEarned, newMilestones };
}

export const ALL_MILESTONES: Milestone[] = [
  { id: 'first_blood', name: 'Primeiro Sangue', description: 'Mate 10 inimigos no total', icon: '🩸',
    requirement: (s) => s.totalKills >= 10, reward: { type: 'ability', id: 'frost_nova', name: 'Frost Nova' }, unlocked: false },
  { id: 'survivor', name: 'Sobrevivente', description: 'Chegue à wave 5', icon: '🛡️',
    requirement: (s) => s.highestWave >= 5, reward: { type: 'map', id: 'inferno', name: 'Mapa Inferno' }, unlocked: false },
  { id: 'slayer_100', name: 'Caçador', description: 'Mate 100 inimigos', icon: '⚔️',
    requirement: (s) => s.totalKills >= 100, reward: { type: 'ability', id: 'missile_barrage', name: 'Missile Barrage' }, unlocked: false },
  { id: 'boss_hunter', name: 'Caça-Chefe', description: 'Mate 3 bosses', icon: '👑',
    requirement: (s) => s.bossesKilled >= 3, reward: { type: 'ability', id: 'plasma_field', name: 'Plasma Field' }, unlocked: false },
  { id: 'combo_master', name: 'Combo Master', description: 'Combo de 20', icon: '🔥',
    requirement: (s) => s.maxCombo >= 20, reward: { type: 'ability', id: 'lightning_ring', name: 'Lightning Ring' }, unlocked: false },
  { id: 'wave_10', name: 'Veterano', description: 'Wave 10', icon: '🌟',
    requirement: (s) => s.highestWave >= 10, reward: { type: 'map', id: 'void', name: 'Mapa Void' }, unlocked: false },
  { id: 'all_ships_3', name: 'Piloto Versátil', description: 'Jogue com 3 naves', icon: '🚀',
    requirement: (s) => s.classesPlayed.length >= 3, reward: { type: 'ability', id: 'flame_trail', name: 'Flame Trail' }, unlocked: false },
  { id: 'slayer_500', name: 'Exterminador', description: 'Mate 500 inimigos', icon: '💀',
    requirement: (s) => s.totalKills >= 500, reward: { type: 'weapon_slot', id: 'slot_4', name: '+1 Slot' }, unlocked: false },
  { id: 'wave_15', name: 'Lenda', description: 'Wave 15', icon: '⭐',
    requirement: (s) => s.highestWave >= 15, reward: { type: 'map', id: 'crystal', name: 'Crystal' }, unlocked: false },
  { id: 'score_10k', name: 'Pontuação Épica', description: '10.000 pontos', icon: '🏆',
    requirement: (s) => s.highestScore >= 10000, reward: { type: 'weapon_slot', id: 'slot_5', name: '+1 Slot' }, unlocked: false },
  // New milestones for new content
  { id: 'wave_8', name: 'Explorador Ártico', description: 'Wave 8', icon: '❄️',
    requirement: (s) => s.highestWave >= 8, reward: { type: 'map', id: 'arctic', name: 'Arctic' }, unlocked: false },
  { id: 'boss_5', name: 'Matador de Bosses', description: '5 bosses mortos', icon: '⚔️',
    requirement: (s) => s.bossesKilled >= 5, reward: { type: 'map', id: 'nebula', name: 'Nebula' }, unlocked: false },
  { id: 'kills_200', name: 'Destruidor', description: '200 kills', icon: '💥',
    requirement: (s) => s.totalKills >= 200, reward: { type: 'map', id: 'toxic', name: 'Toxic Swamp' }, unlocked: false },
  { id: 'wave_12', name: 'Tempestade', description: 'Wave 12', icon: '⛈️',
    requirement: (s) => s.highestWave >= 12, reward: { type: 'map', id: 'storm', name: 'Storm Nexus' }, unlocked: false },
  { id: 'score_5k', name: 'Pontuação Sólida', description: '5.000 pontos', icon: '📊',
    requirement: (s) => s.highestScore >= 5000, reward: { type: 'map', id: 'graveyard', name: 'Graveyard' }, unlocked: false },
  { id: 'wave_18', name: 'Guerreiro Elite', description: 'Wave 18', icon: '🌠',
    requirement: (s) => s.highestWave >= 18, reward: { type: 'map', id: 'singularity', name: 'Singularity' }, unlocked: false },
  { id: 'kills_1000', name: 'Genocida', description: '1000 kills', icon: '☠️',
    requirement: (s) => s.totalKills >= 1000, reward: { type: 'map', id: 'foundry', name: 'Foundry' }, unlocked: false },
  { id: 'boss_8', name: 'Caçador Supremo', description: '8 bosses', icon: '👑',
    requirement: (s) => s.bossesKilled >= 8, reward: { type: 'map', id: 'nexus', name: 'Nexus' }, unlocked: false },
  { id: 'wave_22', name: 'Ascensão', description: 'Wave 22', icon: '✨',
    requirement: (s) => s.highestWave >= 22, reward: { type: 'map', id: 'aurora', name: 'Aurora' }, unlocked: false },
  { id: 'score_25k', name: 'Pontuação Lendária', description: '25.000 pontos', icon: '💎',
    requirement: (s) => s.highestScore >= 25000, reward: { type: 'map', id: 'magma-core', name: 'Magma Core' }, unlocked: false },
  { id: 'wave_25', name: 'Transcendente', description: 'Wave 25', icon: '🔮',
    requirement: (s) => s.highestWave >= 25, reward: { type: 'map', id: 'quantum', name: 'Quantum' }, unlocked: false },
  { id: 'score_50k', name: 'Pontuação Divina', description: '50.000 pontos', icon: '🌌',
    requirement: (s) => s.highestScore >= 50000, reward: { type: 'map', id: 'abyss', name: 'The Abyss' }, unlocked: false },
  // Ship unlock milestones
  { id: 'ships_5', name: 'Colecionador', description: 'Jogue com 5 naves', icon: '🚀',
    requirement: (s) => s.classesPlayed.length >= 5, reward: { type: 'ship', id: 'wraith', name: 'Wraith' }, unlocked: false },
  { id: 'kills_300', name: 'Veterano de Guerra', description: '300 kills', icon: '🎖️',
    requirement: (s) => s.totalKills >= 300, reward: { type: 'ship', id: 'tempest', name: 'Tempest' }, unlocked: false },
  { id: 'combo_15', name: 'Combo Expert', description: 'Combo 15', icon: '🔗',
    requirement: (s) => s.maxCombo >= 15, reward: { type: 'ship', id: 'raptor', name: 'Raptor' }, unlocked: false },
  { id: 'boss_12', name: 'Caçador Lendário', description: '12 bosses', icon: '⚔️',
    requirement: (s) => s.bossesKilled >= 12, reward: { type: 'ship', id: 'chronos', name: 'Chronos' }, unlocked: false },
];
