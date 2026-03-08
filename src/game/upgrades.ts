import { Upgrade, Player } from './types';

const ALL_UPGRADES: Upgrade[] = [
  {
    id: 'hp_up',
    name: 'Vitalidade',
    description: '+20 vida máxima e cura total',
    icon: '❤️',
    apply: (p: Player) => { p.maxHp += 20; p.hp = p.maxHp; },
  },
  {
    id: 'dmg_up',
    name: 'Força',
    description: '+25% de dano',
    icon: '⚔️',
    apply: (p: Player) => { p.damage = Math.floor(p.damage * 1.25); },
  },
  {
    id: 'speed_up',
    name: 'Agilidade',
    description: '+15% de velocidade',
    icon: '💨',
    apply: (p: Player) => { p.speed *= 1.15; },
  },
  {
    id: 'attack_speed',
    name: 'Frenesi',
    description: '-20% cooldown de ataque',
    icon: '🔥',
    apply: (p: Player) => { p.attackCooldown *= 0.8; },
  },
  {
    id: 'special_cd',
    name: 'Arcano',
    description: '-25% cooldown especial',
    icon: '✨',
    apply: (p: Player) => { p.specialCooldown *= 0.75; },
  },
  {
    id: 'regen',
    name: 'Regeneração',
    description: 'Recupera 30 HP',
    icon: '💚',
    apply: (p: Player) => { p.hp = Math.min(p.maxHp, p.hp + 30); },
  },
  {
    id: 'armor',
    name: 'Armadura',
    description: '+30 vida máxima',
    icon: '🛡️',
    apply: (p: Player) => { p.maxHp += 30; p.hp += 30; },
  },
  {
    id: 'critical',
    name: 'Crítico',
    description: '+35% de dano',
    icon: '💀',
    apply: (p: Player) => { p.damage = Math.floor(p.damage * 1.35); },
  },
];

export function getRandomUpgrades(count: number): Upgrade[] {
  const shuffled = [...ALL_UPGRADES].sort(() => Math.random() - 0.5);
  return shuffled.slice(0, count);
}
