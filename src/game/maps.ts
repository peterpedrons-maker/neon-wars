import type { EnemyType } from './types';

export type MapDifficulty = 'easy' | 'medium' | 'hard';

export interface MapDifficultySettings {
  enemyHpMult: number; enemyDamageMult: number; enemySpeedMult: number;
  spawnRateMult: number; hazardRateMult: number;
}

export interface GameMap {
  id: string; name: string; description: string; icon: string;
  bgColor: string; gridColor: string; gridAlpha: number; borderColor: string;
  ambientParticleColor: string; fogColor: string;
  difficulties: Record<MapDifficulty, MapDifficultySettings>;
  hazards: MapHazard[];
  // Map-specific content
  regularEnemies: EnemyType[];
  bossEnemy: EnemyType;
  order: number; // difficulty order (higher = harder)
}

export type HazardType = 'lava_pool' | 'black_hole' | 'ice_zone' | 'crystal_shard' | 'void_rift' | 'acid_pool' | 'lightning_strike' | 'gravity_well' | 'warp_portal' | 'prism_beam';

export interface MapHazard {
  type: HazardType; spawnChance: number; maxActive: number;
}

function diff(e: number, m: number, h: number): Record<MapDifficulty, MapDifficultySettings> {
  return {
    easy:   { enemyHpMult: 0.9*e, enemyDamageMult: 0.9*e, enemySpeedMult: 0.95, spawnRateMult: 0.9, hazardRateMult: 0.85 },
    medium: { enemyHpMult: m, enemyDamageMult: m, enemySpeedMult: 1+m*0.03, spawnRateMult: m, hazardRateMult: m },
    hard:   { enemyHpMult: h, enemyDamageMult: h, enemySpeedMult: 1+h*0.1, spawnRateMult: 1+h*0.15, hazardRateMult: h },
  };
}

export const ALL_MAPS: Record<string, GameMap> = {
  'neon-grid': {
    id: 'neon-grid', name: 'Neon Grid', description: 'Arena clássica neon', icon: '🌐', order: 1,
    bgColor: '#000008', gridColor: '0,255,255', gridAlpha: 0.04, borderColor: '#0ff',
    ambientParticleColor: '#0ff', fogColor: 'rgba(0,0,8,0.4)',
    difficulties: diff(1, 1, 1.25),
    hazards: [],
    regularEnemies: [],
    bossEnemy: 'mothership',
  },
  inferno: {
    id: 'inferno', name: 'Inferno', description: 'Poças de lava surgem aleatoriamente', icon: '🔥', order: 2,
    bgColor: '#0a0200', gridColor: '255,80,0', gridAlpha: 0.03, borderColor: '#ff4500',
    ambientParticleColor: '#ff6b00', fogColor: 'rgba(10,2,0,0.4)',
    difficulties: diff(1.05, 1.05, 1.35),
    hazards: [{ type: 'lava_pool', spawnChance: 0.6, maxActive: 5 }],
    regularEnemies: ['fire_elemental'],
    bossEnemy: 'lava_dragon',
  },
  void: {
    id: 'void', name: 'Void', description: 'Buracos negros puxam tudo ao redor', icon: '🕳️', order: 3,
    bgColor: '#030008', gridColor: '150,0,255', gridAlpha: 0.03, borderColor: '#8000ff',
    ambientParticleColor: '#bf5af2', fogColor: 'rgba(3,0,8,0.5)',
    difficulties: diff(1.1, 1.1, 1.4),
    hazards: [{ type: 'black_hole', spawnChance: 0.4, maxActive: 3 }],
    regularEnemies: ['void_ghost'],
    bossEnemy: 'void_lord',
  },
  crystal: {
    id: 'crystal', name: 'Crystal Cavern', description: 'Cristais refletem projéteis', icon: '💎', order: 4,
    bgColor: '#000808', gridColor: '0,200,200', gridAlpha: 0.05, borderColor: '#00e5ff',
    ambientParticleColor: '#00e5ff', fogColor: 'rgba(0,8,8,0.3)',
    difficulties: diff(1.08, 1.08, 1.35),
    hazards: [{ type: 'crystal_shard', spawnChance: 0.5, maxActive: 6 }],
    regularEnemies: ['crystal_golem'],
    bossEnemy: 'crystal_giant',
  },
  arctic: {
    id: 'arctic', name: 'Arctic Wastes', description: 'Gelo congela e retarda tudo', icon: '❄️', order: 5,
    bgColor: '#000a10', gridColor: '100,200,255', gridAlpha: 0.04, borderColor: '#44ccff',
    ambientParticleColor: '#88ddff', fogColor: 'rgba(0,10,16,0.4)',
    difficulties: diff(1.1, 1.1, 1.4),
    hazards: [{ type: 'ice_zone', spawnChance: 0.5, maxActive: 4 }],
    regularEnemies: ['ice_walker'],
    bossEnemy: 'frost_titan',
  },
  nebula: {
    id: 'nebula', name: 'Nebula', description: 'Nuvens cósmicas escondem horrores', icon: '🌌', order: 6,
    bgColor: '#050010', gridColor: '100,50,200', gridAlpha: 0.025, borderColor: '#9966ff',
    ambientParticleColor: '#9966ff', fogColor: 'rgba(5,0,16,0.55)',
    difficulties: diff(1.15, 1.15, 1.45),
    hazards: [{ type: 'void_rift', spawnChance: 0.4, maxActive: 3 }],
    regularEnemies: ['nebula_shade'],
    bossEnemy: 'cosmic_horror',
  },
  toxic: {
    id: 'toxic', name: 'Toxic Swamp', description: 'Poças ácidas corroem tudo', icon: '☠️', order: 7,
    bgColor: '#020800', gridColor: '100,200,0', gridAlpha: 0.03, borderColor: '#66ff00',
    ambientParticleColor: '#88ff00', fogColor: 'rgba(2,8,0,0.4)',
    difficulties: diff(1.15, 1.15, 1.45),
    hazards: [{ type: 'acid_pool', spawnChance: 0.6, maxActive: 5 }],
    regularEnemies: ['acid_slime'],
    bossEnemy: 'plague_lord',
  },
  storm: {
    id: 'storm', name: 'Storm Nexus', description: 'Raios caem do céu constantemente', icon: '⛈️', order: 8,
    bgColor: '#040408', gridColor: '200,200,50', gridAlpha: 0.035, borderColor: '#ffff44',
    ambientParticleColor: '#ffff44', fogColor: 'rgba(4,4,8,0.4)',
    difficulties: diff(1.2, 1.2, 1.5),
    hazards: [{ type: 'lightning_strike', spawnChance: 0.7, maxActive: 4 }],
    regularEnemies: ['storm_drone'],
    bossEnemy: 'thunder_god',
  },
  graveyard: {
    id: 'graveyard', name: 'Graveyard', description: 'Os mortos se levantam novamente', icon: '💀', order: 9,
    bgColor: '#040804', gridColor: '80,150,80', gridAlpha: 0.03, borderColor: '#44ff88',
    ambientParticleColor: '#668866', fogColor: 'rgba(4,8,4,0.5)',
    difficulties: diff(1.2, 1.2, 1.5),
    hazards: [],
    regularEnemies: ['undead_risen'],
    bossEnemy: 'lich_king',
  },
  singularity: {
    id: 'singularity', name: 'Singularity', description: 'Void hardcore com gravidade brutal', icon: '🌀', order: 10,
    bgColor: '#02000a', gridColor: '120,40,255', gridAlpha: 0.025, borderColor: '#a855f7',
    ambientParticleColor: '#a855f7', fogColor: 'rgba(2,0,10,0.55)',
    difficulties: diff(1.2, 1.2, 1.6),
    hazards: [{ type: 'black_hole', spawnChance: 0.65, maxActive: 5 }],
    regularEnemies: ['void_ghost'],
    bossEnemy: 'vortex',
  },
  foundry: {
    id: 'foundry', name: 'Foundry', description: 'Fábrica incandescente cheia de lava', icon: '🏭', order: 11,
    bgColor: '#080100', gridColor: '255,120,0', gridAlpha: 0.028, borderColor: '#ff6b00',
    ambientParticleColor: '#ff6b00', fogColor: 'rgba(8,1,0,0.45)',
    difficulties: diff(1.25, 1.25, 1.55),
    hazards: [{ type: 'lava_pool', spawnChance: 0.75, maxActive: 7 }],
    regularEnemies: ['fire_elemental'],
    bossEnemy: 'lava_dragon',
  },
  nexus: {
    id: 'nexus', name: 'Nexus', description: 'Portais de warp distorcem o espaço', icon: '🌀', order: 12,
    bgColor: '#080008', gridColor: '200,0,200', gridAlpha: 0.03, borderColor: '#ff00ff',
    ambientParticleColor: '#ff44ff', fogColor: 'rgba(8,0,8,0.45)',
    difficulties: diff(1.3, 1.3, 1.6),
    hazards: [{ type: 'warp_portal', spawnChance: 0.5, maxActive: 3 }],
    regularEnemies: ['warp_drone'],
    bossEnemy: 'nexus_guardian',
  },
  aurora: {
    id: 'aurora', name: 'Aurora', description: 'Beleza mortal com feixes prismáticos', icon: '🌈', order: 13,
    bgColor: '#040008', gridColor: '200,100,200', gridAlpha: 0.04, borderColor: '#ff66aa',
    ambientParticleColor: '#ff88ff', fogColor: 'rgba(4,0,8,0.35)',
    difficulties: diff(1.3, 1.3, 1.6),
    hazards: [{ type: 'prism_beam', spawnChance: 0.5, maxActive: 3 }],
    regularEnemies: ['prism_shard'],
    bossEnemy: 'aurora_phoenix',
  },
  'magma-core': {
    id: 'magma-core', name: 'Magma Core', description: 'O coração ardente do planeta', icon: '🌋', order: 14,
    bgColor: '#0a0000', gridColor: '255,80,0', gridAlpha: 0.03, borderColor: '#ff6600',
    ambientParticleColor: '#ff4400', fogColor: 'rgba(10,0,0,0.5)',
    difficulties: diff(1.35, 1.35, 1.7),
    hazards: [{ type: 'lava_pool', spawnChance: 0.8, maxActive: 8 }],
    regularEnemies: ['magma_wurm'],
    bossEnemy: 'core_titan',
  },
  quantum: {
    id: 'quantum', name: 'Quantum Realm', description: 'A realidade se dobra e se quebra', icon: '⚛️', order: 15,
    bgColor: '#000410', gridColor: '50,100,255', gridAlpha: 0.035, borderColor: '#4488ff',
    ambientParticleColor: '#4488ff', fogColor: 'rgba(0,4,16,0.45)',
    difficulties: diff(1.4, 1.4, 1.75),
    hazards: [{ type: 'gravity_well', spawnChance: 0.5, maxActive: 4 }, { type: 'warp_portal', spawnChance: 0.3, maxActive: 2 }],
    regularEnemies: ['quantum_shifter'],
    bossEnemy: 'reality_breaker',
  },
  abyss: {
    id: 'abyss', name: 'The Abyss', description: 'O vazio final. Não há escapatória.', icon: '🕳️', order: 16,
    bgColor: '#010002', gridColor: '40,0,80', gridAlpha: 0.02, borderColor: '#440088',
    ambientParticleColor: '#220044', fogColor: 'rgba(1,0,2,0.6)',
    difficulties: diff(1.5, 1.5, 1.9),
    hazards: [{ type: 'black_hole', spawnChance: 0.7, maxActive: 5 }, { type: 'void_rift', spawnChance: 0.5, maxActive: 3 }],
    regularEnemies: ['abyss_horror'],
    bossEnemy: 'void_emperor',
  },
};

// Sorted map order by difficulty
export const MAP_ORDER = Object.values(ALL_MAPS).sort((a, b) => a.order - b.order).map(m => m.id);

export interface ActiveHazard {
  type: HazardType; pos: { x: number; y: number };
  radius: number; lifetime: number; maxLifetime: number;
  damage: number; pullStrength?: number;
}

export function createHazard(type: HazardType, arenaW: number, arenaH: number): ActiveHazard {
  const margin = 100;
  const pos = {
    x: margin + Math.random() * (arenaW - margin * 2),
    y: margin + Math.random() * (arenaH - margin * 2),
  };
  switch (type) {
    case 'lava_pool':         return { type, pos, radius: 40 + Math.random() * 30, lifetime: 20, maxLifetime: 20, damage: 1 };
    case 'black_hole':        return { type, pos, radius: 25, lifetime: 15, maxLifetime: 15, damage: 0, pullStrength: 80 };
    case 'crystal_shard':     return { type, pos, radius: 15, lifetime: 30, maxLifetime: 30, damage: 0 };
    case 'ice_zone':          return { type, pos, radius: 50, lifetime: 18, maxLifetime: 18, damage: 0 };
    case 'void_rift':         return { type, pos, radius: 35, lifetime: 12, maxLifetime: 12, damage: 1 };
    case 'acid_pool':         return { type, pos, radius: 35 + Math.random() * 25, lifetime: 22, maxLifetime: 22, damage: 1 };
    case 'lightning_strike':  return { type, pos, radius: 20, lifetime: 0.5, maxLifetime: 0.5, damage: 3 };
    case 'gravity_well':      return { type, pos, radius: 30, lifetime: 15, maxLifetime: 15, damage: 0, pullStrength: 60 };
    case 'warp_portal':       return { type, pos, radius: 25, lifetime: 10, maxLifetime: 10, damage: 0 };
    case 'prism_beam':        return { type, pos, radius: 15, lifetime: 8, maxLifetime: 8, damage: 2 };
    default:                  return { type, pos, radius: 30, lifetime: 15, maxLifetime: 15, damage: 0 };
  }
}
