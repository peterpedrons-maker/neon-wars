// Map System - Visual themes + unique hazards

export type MapDifficulty = 'easy' | 'medium' | 'hard';

export interface MapDifficultySettings {
  enemyHpMult: number;
  enemyDamageMult: number;
  enemySpeedMult: number;
  spawnRateMult: number;   // >1 = more spawns
  hazardRateMult: number;  // >1 = more hazards
}

export interface GameMap {
  id: string;
  name: string;
  description: string;
  icon: string;
  // Visual theme
  bgColor: string;
  gridColor: string;
  gridAlpha: number;
  borderColor: string;
  ambientParticleColor: string;
  fogColor: string;
  // Difficulties (same map, multiple challenges)
  difficulties: Record<MapDifficulty, MapDifficultySettings>;
  // Hazards
  hazards: MapHazard[];
}

export type HazardType = 'lava_pool' | 'black_hole' | 'ice_zone' | 'crystal_shard' | 'void_rift';

export interface MapHazard {
  type: HazardType;
  spawnChance: number; // per wave
  maxActive: number;
}

export const ALL_MAPS: Record<string, GameMap> = {
  'neon-grid': {
    id: 'neon-grid',
    name: 'Neon Grid',
    description: 'A arena clássica neon',
    icon: '🌐',
    bgColor: '#000008',
    gridColor: '0,255,255',
    gridAlpha: 0.04,
    borderColor: '#0ff',
    ambientParticleColor: '#0ff',
    fogColor: 'rgba(0,0,8,0.4)',
    difficulties: {
      easy: { enemyHpMult: 0.9, enemyDamageMult: 0.9, enemySpeedMult: 0.95, spawnRateMult: 0.9, hazardRateMult: 0.9 },
      medium: { enemyHpMult: 1, enemyDamageMult: 1, enemySpeedMult: 1, spawnRateMult: 1, hazardRateMult: 1 },
      hard: { enemyHpMult: 1.25, enemyDamageMult: 1.25, enemySpeedMult: 1.12, spawnRateMult: 1.18, hazardRateMult: 1.05 },
    },
    hazards: [],
  },
  'inferno': {
    id: 'inferno',
    name: 'Inferno',
    description: 'Poças de lava surgem aleatoriamente',
    icon: '🔥',
    bgColor: '#0a0200',
    gridColor: '255,80,0',
    gridAlpha: 0.03,
    borderColor: '#ff4500',
    ambientParticleColor: '#ff6b00',
    fogColor: 'rgba(10,2,0,0.4)',
    difficulties: {
      easy: { enemyHpMult: 0.95, enemyDamageMult: 0.9, enemySpeedMult: 0.95, spawnRateMult: 0.92, hazardRateMult: 0.85 },
      medium: { enemyHpMult: 1.05, enemyDamageMult: 1.05, enemySpeedMult: 1.02, spawnRateMult: 1.05, hazardRateMult: 1 },
      hard: { enemyHpMult: 1.35, enemyDamageMult: 1.35, enemySpeedMult: 1.12, spawnRateMult: 1.25, hazardRateMult: 1.2 },
    },
    hazards: [{ type: 'lava_pool', spawnChance: 0.6, maxActive: 5 }],
  },
  'void': {
    id: 'void',
    name: 'Void',
    description: 'Buracos negros puxam tudo ao redor',
    icon: '🕳️',
    bgColor: '#030008',
    gridColor: '150,0,255',
    gridAlpha: 0.03,
    borderColor: '#8000ff',
    ambientParticleColor: '#bf5af2',
    fogColor: 'rgba(3,0,8,0.5)',
    difficulties: {
      easy: { enemyHpMult: 0.95, enemyDamageMult: 0.95, enemySpeedMult: 0.98, spawnRateMult: 0.95, hazardRateMult: 0.9 },
      medium: { enemyHpMult: 1.1, enemyDamageMult: 1.1, enemySpeedMult: 1.05, spawnRateMult: 1.08, hazardRateMult: 1.05 },
      hard: { enemyHpMult: 1.4, enemyDamageMult: 1.4, enemySpeedMult: 1.18, spawnRateMult: 1.3, hazardRateMult: 1.25 },
    },
    hazards: [{ type: 'black_hole', spawnChance: 0.4, maxActive: 3 }],
  },
  'crystal': {
    id: 'crystal',
    name: 'Crystal Cavern',
    description: 'Cristais refletem projéteis',
    icon: '💎',
    bgColor: '#000808',
    gridColor: '0,200,200',
    gridAlpha: 0.05,
    borderColor: '#00e5ff',
    ambientParticleColor: '#00e5ff',
    fogColor: 'rgba(0,8,8,0.3)',
    difficulties: {
      easy: { enemyHpMult: 0.95, enemyDamageMult: 0.95, enemySpeedMult: 0.98, spawnRateMult: 0.95, hazardRateMult: 0.9 },
      medium: { enemyHpMult: 1.08, enemyDamageMult: 1.08, enemySpeedMult: 1.03, spawnRateMult: 1.05, hazardRateMult: 1 },
      hard: { enemyHpMult: 1.35, enemyDamageMult: 1.35, enemySpeedMult: 1.14, spawnRateMult: 1.25, hazardRateMult: 1.15 },
    },
    hazards: [{ type: 'crystal_shard', spawnChance: 0.5, maxActive: 6 }],
  },
  'singularity': {
    id: 'singularity',
    name: 'Singularity',
    description: 'Void hardcore com gravidade brutal',
    icon: '🌀',
    bgColor: '#02000a',
    gridColor: '120,40,255',
    gridAlpha: 0.025,
    borderColor: '#a855f7',
    ambientParticleColor: '#a855f7',
    fogColor: 'rgba(2,0,10,0.55)',
    difficulties: {
      easy: { enemyHpMult: 1.0, enemyDamageMult: 1.0, enemySpeedMult: 1.0, spawnRateMult: 1.0, hazardRateMult: 1.0 },
      medium: { enemyHpMult: 1.2, enemyDamageMult: 1.2, enemySpeedMult: 1.08, spawnRateMult: 1.15, hazardRateMult: 1.3 },
      hard: { enemyHpMult: 1.6, enemyDamageMult: 1.6, enemySpeedMult: 1.22, spawnRateMult: 1.45, hazardRateMult: 1.7 },
    },
    hazards: [{ type: 'black_hole', spawnChance: 0.65, maxActive: 5 }],
  },
  'foundry': {
    id: 'foundry',
    name: 'Foundry',
    description: 'Fábrica incandescente cheia de lava',
    icon: '🏭',
    bgColor: '#080100',
    gridColor: '255,120,0',
    gridAlpha: 0.028,
    borderColor: '#ff6b00',
    ambientParticleColor: '#ff6b00',
    fogColor: 'rgba(8,1,0,0.45)',
    difficulties: {
      easy: { enemyHpMult: 0.95, enemyDamageMult: 0.95, enemySpeedMult: 0.98, spawnRateMult: 0.95, hazardRateMult: 1.0 },
      medium: { enemyHpMult: 1.1, enemyDamageMult: 1.1, enemySpeedMult: 1.05, spawnRateMult: 1.1, hazardRateMult: 1.25 },
      hard: { enemyHpMult: 1.45, enemyDamageMult: 1.45, enemySpeedMult: 1.15, spawnRateMult: 1.3, hazardRateMult: 1.6 },
    },
    hazards: [{ type: 'lava_pool', spawnChance: 0.75, maxActive: 7 }],
  },
};

export interface ActiveHazard {
  type: HazardType;
  pos: { x: number; y: number };
  radius: number;
  lifetime: number;
  maxLifetime: number;
  damage: number;
  pullStrength?: number;
}

export function createHazard(type: HazardType, arenaW: number, arenaH: number): ActiveHazard {
  const margin = 100;
  const pos = {
    x: margin + Math.random() * (arenaW - margin * 2),
    y: margin + Math.random() * (arenaH - margin * 2),
  };

  switch (type) {
    case 'lava_pool':
      return { type, pos, radius: 40 + Math.random() * 30, lifetime: 20, maxLifetime: 20, damage: 1 };
    case 'black_hole':
      return { type, pos, radius: 25, lifetime: 15, maxLifetime: 15, damage: 0, pullStrength: 80 };
    case 'crystal_shard':
      return { type, pos, radius: 15, lifetime: 30, maxLifetime: 30, damage: 0 };
    case 'ice_zone':
      return { type, pos, radius: 50, lifetime: 18, maxLifetime: 18, damage: 0 };
    case 'void_rift':
      return { type, pos, radius: 35, lifetime: 12, maxLifetime: 12, damage: 1 };
    default:
      return { type, pos, radius: 30, lifetime: 15, maxLifetime: 15, damage: 0 };
  }
}
