import { Upgrade, Player } from './types';

const ALL_UPGRADES: Upgrade[] = [
  {
    id: 'hp_up',
    name: 'Hull Reforço',
    description: '+20 HP máximo e reparo total',
    icon: '🛡️',
    apply: (p: Player) => { p.maxHp += 20; p.hp = p.maxHp; },
  },
  {
    id: 'dmg_up',
    name: 'Canhão Turbo',
    description: '+25% de dano',
    icon: '⚡',
    apply: (p: Player) => { p.damage = Math.floor(p.damage * 1.25); },
  },
  {
    id: 'speed_up',
    name: 'Propulsor',
    description: '+15% de velocidade',
    icon: '🚀',
    apply: (p: Player) => { p.speed *= 1.15; },
  },
  {
    id: 'attack_speed',
    name: 'Cadência',
    description: '-20% cooldown de tiro',
    icon: '🔥',
    apply: (p: Player) => { p.attackCooldown *= 0.8; },
  },
  {
    id: 'special_cd',
    name: 'Núcleo Quântico',
    description: '-25% cooldown especial',
    icon: '✨',
    apply: (p: Player) => { p.specialCooldown *= 0.75; },
  },
  {
    id: 'regen',
    name: 'Nano-reparo',
    description: 'Recupera 30 HP',
    icon: '💚',
    apply: (p: Player) => { p.hp = Math.min(p.maxHp, p.hp + 30); },
  },
  {
    id: 'armor',
    name: 'Blindagem',
    description: '+30 HP máximo',
    icon: '🔰',
    apply: (p: Player) => { p.maxHp += 30; p.hp += 30; },
  },
  {
    id: 'critical',
    name: 'Overcharge',
    description: '+35% de dano',
    icon: '💥',
    apply: (p: Player) => { p.damage = Math.floor(p.damage * 1.35); },
  },
];

export function getRandomUpgrades(count: number): Upgrade[] {
  const shuffled = [...ALL_UPGRADES].sort(() => Math.random() - 0.5);
  return shuffled.slice(0, count);
}
