// 🏆 Neon Wars - Achievement System
// Achievements divided by difficulty: Easy, Moderate, Hard, Extreme
// Organized by map and global

export type AchievementDifficulty = 'easy' | 'moderate' | 'hard' | 'extreme';

export interface Achievement {
  id: string;
  name: string;
  description: string;
  icon: string;
  difficulty: AchievementDifficulty;
  mapId?: string; // if map-specific
  check: (ctx: AchievementContext) => boolean;
}

export interface AchievementContext {
  score: number;
  wave: number;
  kills: number;
  bossKills: number;
  maxCombo: number;
  shipClass: string;
  mapId: string;
  damageTaken: number;
  timePlayed: number;
  totalKills: number;
  totalRuns: number;
  highestWave: number;
  highestScore: number;
  totalPlasma: number;
  classesPlayed: string[];
}

// ===== GLOBAL ACHIEVEMENTS =====
const GLOBAL_ACHIEVEMENTS: Achievement[] = [
  // Easy
  { id: 'g_first_kill', name: 'Primeiro Abate', description: 'Elimine seu primeiro inimigo', icon: '🗡️', difficulty: 'easy', check: c => c.kills >= 1 },
  { id: 'g_wave_3', name: 'Iniciante', description: 'Chegue à wave 3', icon: '🌊', difficulty: 'easy', check: c => c.wave >= 3 },
  { id: 'g_score_1k', name: 'Pontuação Decente', description: 'Faça 1.000 pontos', icon: '📊', difficulty: 'easy', check: c => c.score >= 1000 },
  { id: 'g_combo_5', name: 'Combo Iniciante', description: 'Alcance combo de 5', icon: '🔗', difficulty: 'easy', check: c => c.maxCombo >= 5 },
  { id: 'g_10_runs', name: 'Persistente', description: 'Complete 10 runs', icon: '🔄', difficulty: 'easy', check: c => c.totalRuns >= 10 },
  // Moderate
  { id: 'g_wave_10', name: 'Veterano', description: 'Chegue à wave 10', icon: '⭐', difficulty: 'moderate', check: c => c.wave >= 10 },
  { id: 'g_score_10k', name: 'Pontuação Épica', description: 'Faça 10.000 pontos', icon: '🏆', difficulty: 'moderate', check: c => c.score >= 10000 },
  { id: 'g_combo_15', name: 'Combo Killer', description: 'Alcance combo de 15', icon: '🔥', difficulty: 'moderate', check: c => c.maxCombo >= 15 },
  { id: 'g_3_ships', name: 'Piloto Versátil', description: 'Jogue com 3 naves diferentes', icon: '🚀', difficulty: 'moderate', check: c => c.classesPlayed.length >= 3 },
  { id: 'g_boss_3', name: 'Caça-Chefes', description: 'Derrote 3 bosses no total', icon: '👑', difficulty: 'moderate', check: c => c.bossKills >= 3 },
  { id: 'g_kills_500', name: 'Exterminador', description: 'Elimine 500 inimigos no total', icon: '💀', difficulty: 'moderate', check: c => c.totalKills >= 500 },
  // Hard
  { id: 'g_wave_20', name: 'Elite', description: 'Chegue à wave 20', icon: '🌟', difficulty: 'hard', check: c => c.wave >= 20 },
  { id: 'g_score_50k', name: 'Lendário', description: 'Faça 50.000 pontos', icon: '💎', difficulty: 'hard', check: c => c.score >= 50000 },
  { id: 'g_combo_30', name: 'Frenesi', description: 'Alcance combo de 30', icon: '⚡', difficulty: 'hard', check: c => c.maxCombo >= 30 },
  { id: 'g_6_ships', name: 'Almirante', description: 'Jogue com 6 naves diferentes', icon: '🎖️', difficulty: 'hard', check: c => c.classesPlayed.length >= 6 },
  { id: 'g_boss_10', name: 'Matador de Titãs', description: 'Derrote 10 bosses no total', icon: '⚔️', difficulty: 'hard', check: c => c.bossKills >= 10 },
  { id: 'g_kills_2000', name: 'Genocida Cósmico', description: 'Elimine 2000 inimigos no total', icon: '☠️', difficulty: 'hard', check: c => c.totalKills >= 2000 },
  // Extreme
  { id: 'g_wave_30', name: 'Imortal', description: 'Chegue à wave 30', icon: '👁️', difficulty: 'extreme', check: c => c.wave >= 30 },
  { id: 'g_score_100k', name: 'Transcendente', description: 'Faça 100.000 pontos', icon: '🌌', difficulty: 'extreme', check: c => c.score >= 100000 },
  { id: 'g_combo_50', name: 'Combo Divino', description: 'Alcance combo de 50', icon: '💫', difficulty: 'extreme', check: c => c.maxCombo >= 50 },
  { id: 'g_10_ships', name: 'Mestre de Frotas', description: 'Jogue com 10 naves diferentes', icon: '🏅', difficulty: 'extreme', check: c => c.classesPlayed.length >= 10 },
  { id: 'g_kills_5000', name: 'Apocalipse', description: 'Elimine 5000 inimigos no total', icon: '🔮', difficulty: 'extreme', check: c => c.totalKills >= 5000 },
  { id: 'g_plasma_10k', name: 'Magnata Plasmático', description: 'Acumule 10.000 plasma no total', icon: '⚡', difficulty: 'extreme', check: c => c.totalPlasma >= 10000 },
];

// ===== MAP-SPECIFIC ACHIEVEMENTS =====
function mapAchievements(mapId: string, mapName: string, bossName: string): Achievement[] {
  return [
    // Easy
    { id: `${mapId}_play`, name: `Explorador: ${mapName}`, description: `Jogue uma partida em ${mapName}`, icon: '🗺️', difficulty: 'easy', mapId, check: c => c.mapId === mapId && c.wave >= 1 },
    { id: `${mapId}_wave5`, name: `Sobrevivente: ${mapName}`, description: `Chegue à wave 5 em ${mapName}`, icon: '🛡️', difficulty: 'easy', mapId, check: c => c.mapId === mapId && c.wave >= 5 },
    // Moderate
    { id: `${mapId}_wave10`, name: `Veterano: ${mapName}`, description: `Chegue à wave 10 em ${mapName}`, icon: '⭐', difficulty: 'moderate', mapId, check: c => c.mapId === mapId && c.wave >= 10 },
    { id: `${mapId}_boss`, name: `Caçador: ${bossName}`, description: `Derrote ${bossName} em ${mapName}`, icon: '👑', difficulty: 'moderate', mapId, check: c => c.mapId === mapId && c.bossKills >= 1 },
    { id: `${mapId}_score5k`, name: `Dominador: ${mapName}`, description: `Faça 5.000 pontos em ${mapName}`, icon: '🏆', difficulty: 'moderate', mapId, check: c => c.mapId === mapId && c.score >= 5000 },
    // Hard
    { id: `${mapId}_wave15`, name: `Lenda: ${mapName}`, description: `Chegue à wave 15 em ${mapName}`, icon: '🌟', difficulty: 'hard', mapId, check: c => c.mapId === mapId && c.wave >= 15 },
    { id: `${mapId}_nodmg3`, name: `Intocável: ${mapName}`, description: `Chegue à wave 3 sem tomar dano em ${mapName}`, icon: '💨', difficulty: 'hard', mapId, check: c => c.mapId === mapId && c.wave >= 3 && c.damageTaken === 0 },
    { id: `${mapId}_combo20`, name: `Destruidor: ${mapName}`, description: `Combo de 20 em ${mapName}`, icon: '🔥', difficulty: 'hard', mapId, check: c => c.mapId === mapId && c.maxCombo >= 20 },
    // Extreme
    { id: `${mapId}_wave25`, name: `Mestre: ${mapName}`, description: `Chegue à wave 25 em ${mapName}`, icon: '👁️', difficulty: 'extreme', mapId, check: c => c.mapId === mapId && c.wave >= 25 },
    { id: `${mapId}_score25k`, name: `Deus: ${mapName}`, description: `Faça 25.000 pontos em ${mapName}`, icon: '💎', difficulty: 'extreme', mapId, check: c => c.mapId === mapId && c.score >= 25000 },
  ];
}

const MAP_BOSS_NAMES: Record<string, [string, string]> = {
  'neon-grid': ['Neon Grid', 'Mothership'],
  inferno: ['Inferno', 'Lava Dragon'],
  void: ['Void', 'Void Lord'],
  crystal: ['Crystal Cavern', 'Crystal Giant'],
  arctic: ['Arctic Wastes', 'Frost Titan'],
  nebula: ['Nebula', 'Cosmic Horror'],
  toxic: ['Toxic Swamp', 'Plague Lord'],
  storm: ['Storm Nexus', 'Thunder God'],
  graveyard: ['Graveyard', 'Lich King'],
  singularity: ['Singularity', 'Vortex'],
  foundry: ['Foundry', 'Lava Dragon'],
  nexus: ['Nexus', 'Nexus Guardian'],
  aurora: ['Aurora', 'Aurora Phoenix'],
  'magma-core': ['Magma Core', 'Core Titan'],
  quantum: ['Quantum Realm', 'Reality Breaker'],
  abyss: ['The Abyss', 'Void Emperor'],
};

export const ALL_ACHIEVEMENTS: Achievement[] = [
  ...GLOBAL_ACHIEVEMENTS,
  ...Object.entries(MAP_BOSS_NAMES).flatMap(([mapId, [mapName, bossName]]) =>
    mapAchievements(mapId, mapName, bossName)
  ),
];

export function checkAchievements(
  unlocked: Record<string, boolean>,
  ctx: AchievementContext,
): Achievement[] {
  const newlyUnlocked: Achievement[] = [];
  for (const a of ALL_ACHIEVEMENTS) {
    if (unlocked[a.id]) continue;
    if (a.check(ctx)) {
      unlocked[a.id] = true;
      newlyUnlocked.push(a);
    }
  }
  return newlyUnlocked;
}

export const DIFFICULTY_COLORS: Record<AchievementDifficulty, string> = {
  easy: '#39ff14',
  moderate: '#ffff00',
  hard: '#ff6b00',
  extreme: '#ff0040',
};

export const DIFFICULTY_LABELS: Record<AchievementDifficulty, string> = {
  easy: 'Fácil',
  moderate: 'Moderada',
  hard: 'Difícil',
  extreme: 'Extrema',
};
