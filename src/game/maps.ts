// Map System - Visual themes + unique hazards

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
    hazards: [{ type: 'crystal_shard', spawnChance: 0.5, maxActive: 6 }],
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
