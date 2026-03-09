import React, { useState, useEffect } from 'react';
import { MetaProgress, saveMeta } from '../../game/meta';
import { playClick, playHover, playBack, playPurchase, playError, startShopMusic, stopShopMusic } from '../../game/audio';
import { UI_ICONS, SHOP_ICONS, WEAPON_ICONS } from '../../game/icons';
import ShipCanvas from './ShipCanvas';
import { ShipType } from '../../game/types';

export interface ShopItem {
  id: string;
  name: string;
  description: string;
  icon?: string; // image src (preferred)
  emoji?: string; // fallback emoji
  cost: number;
  maxPurchases: number;
  category: 'weapon_slot' | 'permanent_stat' | 'weapon_unlock' | 'ship_unlock' | 'permanent_passive' | 'base_weapon' | 'elemental_weapon';
  apply: (meta: MetaProgress) => void;
  purchased: (meta: MetaProgress) => number;
  badge?: string;
  badgeColor?: string;
}

// ─── Helper: read/write weapon upgrade levels on meta ───────────────────────
function getWeaponLevel(meta: MetaProgress, id: string): number {
  return (meta as any).weaponUpgrades?.[id] ?? 0;
}
function setWeaponLevel(meta: MetaProgress, id: string, level: number) {
  if (!(meta as any).weaponUpgrades) (meta as any).weaponUpgrades = {};
  (meta as any).weaponUpgrades[id] = level;
}

// ─── BASE WEAPONS (always visible, upgradeable 5 levels) ─────────────────────
const BASE_WEAPON_ITEMS: ShopItem[] = [
  {
    id: 'upg_orbitals', name: 'Orbital Drones', description: '+1 drone orbital que causa dano ao contato',
    icon: WEAPON_ICONS.orbitals, cost: 60, maxPurchases: 5, category: 'base_weapon',
    apply: (m) => { setWeaponLevel(m, 'orbitals', getWeaponLevel(m, 'orbitals') + 1); },
    purchased: (m) => getWeaponLevel(m, 'orbitals'), badge: 'BASE',
  },
  {
    id: 'upg_aura', name: 'Neon Aura', description: 'Aura de dano ao redor da nave',
    icon: WEAPON_ICONS.aura, cost: 70, maxPurchases: 5, category: 'base_weapon',
    apply: (m) => { setWeaponLevel(m, 'aura', getWeaponLevel(m, 'aura') + 1); },
    purchased: (m) => getWeaponLevel(m, 'aura'), badge: 'BASE',
  },
  {
    id: 'upg_chain', name: 'Raio Cadeia', description: 'Eliminar inimigo causa dano em cadeia',
    icon: WEAPON_ICONS.chain, cost: 80, maxPurchases: 5, category: 'base_weapon',
    apply: (m) => { setWeaponLevel(m, 'chain', getWeaponLevel(m, 'chain') + 1); },
    purchased: (m) => getWeaponLevel(m, 'chain'), badge: 'BASE',
  },
  {
    id: 'upg_multishot', name: 'Multi-Tiro', description: '+1 projétil por disparo',
    icon: WEAPON_ICONS.multishot, cost: 90, maxPurchases: 3, category: 'base_weapon',
    apply: (m) => { setWeaponLevel(m, 'multishot', getWeaponLevel(m, 'multishot') + 1); },
    purchased: (m) => getWeaponLevel(m, 'multishot'), badge: 'BASE',
  },
  {
    id: 'upg_explosion', name: 'Proj. Explosivo', description: 'Projéteis explodem ao acertar',
    icon: WEAPON_ICONS.explosion, cost: 100, maxPurchases: 4, category: 'base_weapon',
    apply: (m) => { setWeaponLevel(m, 'explosion', getWeaponLevel(m, 'explosion') + 1); },
    purchased: (m) => getWeaponLevel(m, 'explosion'), badge: 'BASE',
  },
  {
    id: 'upg_homing', name: 'Auto-Mira', description: 'Chance de projéteis perseguirem inimigos',
    icon: WEAPON_ICONS.homing, cost: 90, maxPurchases: 5, category: 'base_weapon',
    apply: (m) => { setWeaponLevel(m, 'homing', getWeaponLevel(m, 'homing') + 1); },
    purchased: (m) => getWeaponLevel(m, 'homing'), badge: 'BASE',
  },
  {
    id: 'upg_piercing_rounds', name: 'Balas Perfurantes', description: 'Projéteis atravessam inimigos',
    icon: WEAPON_ICONS.piercing_rounds, cost: 80, maxPurchases: 4, category: 'base_weapon',
    apply: (m) => { setWeaponLevel(m, 'piercing_rounds', getWeaponLevel(m, 'piercing_rounds') + 1); },
    purchased: (m) => getWeaponLevel(m, 'piercing_rounds'), badge: 'BASE',
  },
  {
    id: 'upg_ricochet_rounds', name: 'Ricochete', description: 'Projéteis ricocheteiam em outro alvo',
    icon: WEAPON_ICONS.ricochet_rounds, cost: 80, maxPurchases: 4, category: 'base_weapon',
    apply: (m) => { setWeaponLevel(m, 'ricochet_rounds', getWeaponLevel(m, 'ricochet_rounds') + 1); },
    purchased: (m) => getWeaponLevel(m, 'ricochet_rounds'), badge: 'BASE',
  },
  {
    id: 'upg_ion_beam', name: 'Ion Beam', description: 'Feixe periódico na direção da mira',
    icon: WEAPON_ICONS.ion_beam, cost: 110, maxPurchases: 5, category: 'base_weapon',
    apply: (m) => { setWeaponLevel(m, 'ion_beam', getWeaponLevel(m, 'ion_beam') + 1); },
    purchased: (m) => getWeaponLevel(m, 'ion_beam'), badge: 'BASE',
  },
  {
    id: 'upg_shockwave_emitter', name: 'Shockwave', description: 'Explosão periódica ao redor da nave',
    icon: WEAPON_ICONS.shockwave_emitter, cost: 110, maxPurchases: 5, category: 'base_weapon',
    apply: (m) => { setWeaponLevel(m, 'shockwave_emitter', getWeaponLevel(m, 'shockwave_emitter') + 1); },
    purchased: (m) => getWeaponLevel(m, 'shockwave_emitter'), badge: 'BASE',
  },
  {
    id: 'upg_sentry_drones', name: 'Sentry Drones', description: 'Drones automáticos disparam nos inimigos',
    icon: WEAPON_ICONS.sentry_drones, cost: 100, maxPurchases: 5, category: 'base_weapon',
    apply: (m) => { setWeaponLevel(m, 'sentry_drones', getWeaponLevel(m, 'sentry_drones') + 1); },
    purchased: (m) => getWeaponLevel(m, 'sentry_drones'), badge: 'BASE',
  },
];

// ─── ELEMENTAL WEAPONS (always visible, upgradeable) ─────────────────────────
const ELEMENTAL_WEAPON_ITEMS: ShopItem[] = [
  {
    id: 'upg_frost_nova', name: 'Frost Nova', description: 'Explosão que congela inimigos próximos',
    icon: WEAPON_ICONS.frost_nova, cost: 90, maxPurchases: 5, category: 'elemental_weapon',
    apply: (m) => { setWeaponLevel(m, 'frost_nova', getWeaponLevel(m, 'frost_nova') + 1); },
    purchased: (m) => getWeaponLevel(m, 'frost_nova'), badge: 'GELO', badgeColor: '#00cfff',
  },
  {
    id: 'upg_missile_barrage', name: 'Missile Barrage', description: 'Mísseis teleguiados automáticos',
    icon: WEAPON_ICONS.missile_barrage, cost: 120, maxPurchases: 5, category: 'elemental_weapon',
    apply: (m) => { setWeaponLevel(m, 'missile_barrage', getWeaponLevel(m, 'missile_barrage') + 1); },
    purchased: (m) => getWeaponLevel(m, 'missile_barrage'), badge: 'MÍSSIL', badgeColor: '#ff6b00',
  },
  {
    id: 'upg_plasma_field', name: 'Plasma Field', description: 'Zonas de plasma no chão',
    icon: WEAPON_ICONS.plasma_field, cost: 130, maxPurchases: 4, category: 'elemental_weapon',
    apply: (m) => { setWeaponLevel(m, 'plasma_field', getWeaponLevel(m, 'plasma_field') + 1); },
    purchased: (m) => getWeaponLevel(m, 'plasma_field'), badge: 'PLASMA', badgeColor: '#bf5af2',
  },
  {
    id: 'upg_lightning_ring', name: 'Lightning Ring', description: 'Raios automáticos atingem inimigos',
    icon: WEAPON_ICONS.lightning_ring, cost: 130, maxPurchases: 5, category: 'elemental_weapon',
    apply: (m) => { setWeaponLevel(m, 'lightning_ring', getWeaponLevel(m, 'lightning_ring') + 1); },
    purchased: (m) => getWeaponLevel(m, 'lightning_ring'), badge: 'RAIO', badgeColor: '#ffe033',
  },
  {
    id: 'upg_flame_trail', name: 'Flame Trail', description: 'Rastro de fogo ao se mover',
    icon: WEAPON_ICONS.flame_trail, cost: 110, maxPurchases: 4, category: 'elemental_weapon',
    apply: (m) => { setWeaponLevel(m, 'flame_trail', getWeaponLevel(m, 'flame_trail') + 1); },
    purchased: (m) => getWeaponLevel(m, 'flame_trail'), badge: 'FOGO', badgeColor: '#ff4400',
  },
  {
    id: 'upg_chain_lightning_weapon', name: 'Raio Cadeia+', description: 'Raios que saltam entre inimigos',
    icon: WEAPON_ICONS.chain_lightning_weapon, cost: 140, maxPurchases: 5, category: 'elemental_weapon',
    apply: (m) => { setWeaponLevel(m, 'chain_lightning_weapon', getWeaponLevel(m, 'chain_lightning_weapon') + 1); },
    purchased: (m) => getWeaponLevel(m, 'chain_lightning_weapon'), badge: 'ARC', badgeColor: '#33aaff',
  },
  {
    id: 'upg_ice_beam', name: 'Raio de Gelo', description: 'Congela inimigos com slow prolongado',
    icon: WEAPON_ICONS.ice_beam, cost: 120, maxPurchases: 5, category: 'elemental_weapon',
    apply: (m) => { setWeaponLevel(m, 'ice_beam', getWeaponLevel(m, 'ice_beam') + 1); },
    purchased: (m) => getWeaponLevel(m, 'ice_beam'), badge: 'SLOW', badgeColor: '#00d4ff',
  },
  {
    id: 'upg_boomerang', name: 'Bumerangue', description: 'Projétil que retorna, atingindo duas vezes',
    icon: WEAPON_ICONS.boomerang, cost: 110, maxPurchases: 5, category: 'elemental_weapon',
    apply: (m) => { setWeaponLevel(m, 'boomerang', getWeaponLevel(m, 'boomerang') + 1); },
    purchased: (m) => getWeaponLevel(m, 'boomerang'), badge: 'VOLTA', badgeColor: '#cc88ff',
  },
  {
    id: 'upg_heavy_cannon', name: 'Canhão Pesado', description: 'Disparo lento mas devastador',
    icon: WEAPON_ICONS.heavy_cannon, cost: 150, maxPurchases: 5, category: 'elemental_weapon',
    apply: (m) => { setWeaponLevel(m, 'heavy_cannon', getWeaponLevel(m, 'heavy_cannon') + 1); },
    purchased: (m) => getWeaponLevel(m, 'heavy_cannon'), badge: 'PODER', badgeColor: '#ff6600',
  },
  {
    id: 'upg_acid_spray', name: 'Spray Ácido', description: 'Ácido que causa dano contínuo (DoT)',
    icon: WEAPON_ICONS.acid_spray, cost: 110, maxPurchases: 4, category: 'elemental_weapon',
    apply: (m) => { setWeaponLevel(m, 'acid_spray', getWeaponLevel(m, 'acid_spray') + 1); },
    purchased: (m) => getWeaponLevel(m, 'acid_spray'), badge: 'ÁCIDO', badgeColor: '#44ff44',
  },
  {
    id: 'upg_gravity_well', name: 'Poço Gravitacional', description: 'Zones que puxam e esmagam inimigos',
    icon: WEAPON_ICONS.gravity_well, cost: 160, maxPurchases: 4, category: 'elemental_weapon',
    apply: (m) => { setWeaponLevel(m, 'gravity_well', getWeaponLevel(m, 'gravity_well') + 1); },
    purchased: (m) => getWeaponLevel(m, 'gravity_well'), badge: 'GRAV', badgeColor: '#aa44ff',
  },
  {
    id: 'upg_tesla_coil', name: 'Bobina Tesla', description: 'Arcos elétricos automáticos entre inimigos',
    icon: WEAPON_ICONS.tesla_coil, cost: 130, maxPurchases: 5, category: 'elemental_weapon',
    apply: (m) => { setWeaponLevel(m, 'tesla_coil', getWeaponLevel(m, 'tesla_coil') + 1); },
    purchased: (m) => getWeaponLevel(m, 'tesla_coil'), badge: 'TESLA', badgeColor: '#44aaff',
  },
  {
    id: 'upg_void_rift', name: 'Fenda do Vazio', description: 'Portais que sugam e destroem inimigos',
    icon: WEAPON_ICONS.void_rift, cost: 180, maxPurchases: 4, category: 'elemental_weapon',
    apply: (m) => { setWeaponLevel(m, 'void_rift', getWeaponLevel(m, 'void_rift') + 1); },
    purchased: (m) => getWeaponLevel(m, 'void_rift'), badge: 'VAZIO', badgeColor: '#9900cc',
  },
];

// ─── SHIPS, SLOTS, PERMANENT STATS (unchanged) ───────────────────────────────
const OTHER_SHOP_ITEMS: ShopItem[] = [
  // === SHIP UNLOCKS ===
  { id: 'unlock_spectre', name: 'Spectre', description: 'Nave furtiva com teleporte. Alta velocidade, baixa vida.', emoji: '🌀', cost: 200, maxPurchases: 1, category: 'ship_unlock', apply: (m) => { if (!m.unlockedShips.includes('spectre')) m.unlockedShips.push('spectre'); }, purchased: (m) => m.unlockedShips.includes('spectre') ? 1 : 0 },
  { id: 'unlock_valkyrie', name: 'Valkyrie', description: 'Guerreira alada com tiro duplo e chuva de lanças.', emoji: '🦅', cost: 300, maxPurchases: 1, category: 'ship_unlock', apply: (m) => { if (!m.unlockedShips.includes('valkyrie')) m.unlockedShips.push('valkyrie'); }, purchased: (m) => m.unlockedShips.includes('valkyrie') ? 1 : 0 },
  { id: 'unlock_juggernaut', name: 'Juggernaut', description: 'Fortaleza indestrutível. 5 HP base, dano massivo.', emoji: '🛡️', cost: 500, maxPurchases: 1, category: 'ship_unlock', apply: (m) => { if (!m.unlockedShips.includes('juggernaut')) m.unlockedShips.push('juggernaut'); }, purchased: (m) => m.unlockedShips.includes('juggernaut') ? 1 : 0 },
  { id: 'unlock_sentinel', name: 'Sentinel', description: 'Tanque com barreira. Especial: Escudo + reflexão.', emoji: '🏰', cost: 350, maxPurchases: 1, category: 'ship_unlock', apply: (m) => { if (!m.unlockedShips.includes('sentinel')) m.unlockedShips.push('sentinel'); }, purchased: (m) => m.unlockedShips.includes('sentinel') ? 1 : 0 },
  { id: 'unlock_venom', name: 'Venom', description: 'Envenenador com tiros tóxicos persistentes.', emoji: '🐍', cost: 400, maxPurchases: 1, category: 'ship_unlock', apply: (m) => { if (!m.unlockedShips.includes('venom')) m.unlockedShips.push('venom'); }, purchased: (m) => m.unlockedShips.includes('venom') ? 1 : 0 },
  { id: 'unlock_nova_ship', name: 'Nova', description: 'Poder bruto. Especial: Supernova devastadora.', emoji: '💫', cost: 450, maxPurchases: 1, category: 'ship_unlock', apply: (m) => { if (!m.unlockedShips.includes('nova_ship')) m.unlockedShips.push('nova_ship'); }, purchased: (m) => m.unlockedShips.includes('nova_ship') ? 1 : 0 },
  { id: 'unlock_leviathan', name: 'Leviathan', description: 'Colosso devorador. 8 HP, dano extremo.', emoji: '🐉', cost: 600, maxPurchases: 1, category: 'ship_unlock', apply: (m) => { if (!m.unlockedShips.includes('leviathan')) m.unlockedShips.push('leviathan'); }, purchased: (m) => m.unlockedShips.includes('leviathan') ? 1 : 0 },
  { id: 'unlock_oracle', name: 'Oracle', description: 'Tiros rastreadores inteligentes.', emoji: '🔮', cost: 400, maxPurchases: 1, category: 'ship_unlock', apply: (m) => { if (!m.unlockedShips.includes('oracle')) m.unlockedShips.push('oracle'); }, purchased: (m) => m.unlockedShips.includes('oracle') ? 1 : 0 },
  { id: 'unlock_pyro', name: 'Pyro', description: 'Lança-chamas devastador de curto alcance.', emoji: '🔥', cost: 350, maxPurchases: 1, category: 'ship_unlock', apply: (m) => { if (!m.unlockedShips.includes('pyro')) m.unlockedShips.push('pyro'); }, purchased: (m) => m.unlockedShips.includes('pyro') ? 1 : 0 },
  // === WEAPON SLOTS ===
  { id: 'slot_4', name: '+1 Slot de Arma', description: 'Equipe até 4 armas por run', emoji: '🔫', cost: 100, maxPurchases: 1, category: 'weapon_slot', apply: (m) => { m.weaponSlots = Math.max(m.weaponSlots, 4); }, purchased: (m) => m.weaponSlots >= 4 ? 1 : 0 },
  { id: 'slot_5', name: '+1 Slot de Arma', description: 'Equipe até 5 armas por run', emoji: '🔫', cost: 300, maxPurchases: 1, category: 'weapon_slot', apply: (m) => { m.weaponSlots = Math.max(m.weaponSlots, 5); }, purchased: (m) => m.weaponSlots >= 5 ? 1 : 0 },
  { id: 'slot_6', name: '+1 Slot de Arma', description: 'Equipe até 6 armas por run', emoji: '🔫', cost: 600, maxPurchases: 1, category: 'weapon_slot', apply: (m) => { m.weaponSlots = Math.max(m.weaponSlots, 6); }, purchased: (m) => m.weaponSlots >= 6 ? 1 : 0 },
  // === PERMANENT STATS ===
  { id: 'perm_hp', name: '+1 HP Máximo', description: 'Começa cada run com +1 HP', emoji: '❤️', cost: 80, maxPurchases: 5, category: 'permanent_stat', apply: (m) => { m.permBonuses = m.permBonuses || {}; m.permBonuses.hp = (m.permBonuses.hp || 0) + 1; }, purchased: (m) => m.permBonuses?.hp || 0 },
  { id: 'perm_damage', name: '+10% Dano Base', description: 'Bônus de dano permanente', emoji: '⚔️', cost: 100, maxPurchases: 5, category: 'permanent_stat', apply: (m) => { m.permBonuses = m.permBonuses || {}; m.permBonuses.damage = (m.permBonuses.damage || 0) + 0.1; }, purchased: (m) => Math.round((m.permBonuses?.damage || 0) / 0.1) },
  { id: 'perm_speed', name: '+5% Velocidade', description: 'Move mais rápido desde o início', emoji: '🏃', cost: 60, maxPurchases: 5, category: 'permanent_stat', apply: (m) => { m.permBonuses = m.permBonuses || {}; m.permBonuses.speed = (m.permBonuses.speed || 0) + 0.05; }, purchased: (m) => Math.round((m.permBonuses?.speed || 0) / 0.05) },
  { id: 'perm_magnet', name: '+20% XP Magnet', description: 'Coleta XP de mais longe', emoji: '🧲', cost: 50, maxPurchases: 5, category: 'permanent_stat', apply: (m) => { m.permBonuses = m.permBonuses || {}; m.permBonuses.magnet = (m.permBonuses.magnet || 0) + 0.2; }, purchased: (m) => Math.round((m.permBonuses?.magnet || 0) / 0.2) },
  { id: 'perm_armor', name: '+10% Redução Dano', description: 'Recebe menos dano permanentemente', emoji: '🛡️', cost: 120, maxPurchases: 3, category: 'permanent_stat', apply: (m) => { m.permBonuses = m.permBonuses || {}; m.permBonuses.armor = (m.permBonuses.armor || 0) + 0.1; }, purchased: (m) => Math.round((m.permBonuses?.armor || 0) / 0.1) },
  { id: 'perm_plasma_mult', name: '+10% Plasma Ganho', description: 'Ganha mais plasma por run', emoji: '💎', cost: 200, maxPurchases: 5, category: 'permanent_stat', apply: (m) => { m.permBonuses = m.permBonuses || {}; m.permBonuses.plasmaMultiplier = (m.permBonuses.plasmaMultiplier || 0) + 0.1; }, purchased: (m) => Math.round((m.permBonuses?.plasmaMultiplier || 0) / 0.1) },
  // === PERMANENT PASSIVES ===
  { id: 'perm_regen', name: 'Regeneração', description: 'Regenera 1 HP a cada 30s em todas as runs', emoji: '💚', cost: 250, maxPurchases: 3, category: 'permanent_passive', apply: (m) => { m.permBonuses = m.permBonuses || {}; (m.permBonuses as any).regenLevel = ((m.permBonuses as any).regenLevel || 0) + 1; }, purchased: (m) => (m.permBonuses as any)?.regenLevel || 0 },
  { id: 'perm_crit', name: 'Precisão Crítica', description: '+5% de chance de crítico em todas as runs', emoji: '🎯', cost: 180, maxPurchases: 5, category: 'permanent_passive', apply: (m) => { m.permBonuses = m.permBonuses || {}; (m.permBonuses as any).critBonus = ((m.permBonuses as any).critBonus || 0) + 0.05; }, purchased: (m) => Math.round(((m.permBonuses as any)?.critBonus || 0) / 0.05) },
  { id: 'perm_luck', name: 'Fortuna', description: '+5% chance de drop de power-up', emoji: '🍀', cost: 150, maxPurchases: 5, category: 'permanent_passive', apply: (m) => { m.permBonuses = m.permBonuses || {}; (m.permBonuses as any).luckBonus = ((m.permBonuses as any).luckBonus || 0) + 0.05; }, purchased: (m) => Math.round(((m.permBonuses as any)?.luckBonus || 0) / 0.05) },
  { id: 'perm_xp', name: 'Experiência+', description: '+10% XP ganho em todas as runs', emoji: '📖', cost: 160, maxPurchases: 5, category: 'permanent_passive', apply: (m) => { m.permBonuses = m.permBonuses || {}; (m.permBonuses as any).xpBonusPerm = ((m.permBonuses as any).xpBonusPerm || 0) + 0.1; }, purchased: (m) => Math.round(((m.permBonuses as any)?.xpBonusPerm || 0) / 0.1) },
  { id: 'perm_dodge', name: 'Evasão Instintiva', description: '+3% chance de esquivar dano', emoji: '💨', cost: 220, maxPurchases: 5, category: 'permanent_passive', apply: (m) => { m.permBonuses = m.permBonuses || {}; (m.permBonuses as any).dodgeBonus = ((m.permBonuses as any).dodgeBonus || 0) + 0.03; }, purchased: (m) => Math.round(((m.permBonuses as any)?.dodgeBonus || 0) / 0.03) },
];

const ALL_SHOP_ITEMS: ShopItem[] = [...BASE_WEAPON_ITEMS, ...ELEMENTAL_WEAPON_ITEMS, ...OTHER_SHOP_ITEMS];

interface PlasmaShopProps {
  meta: MetaProgress;
  onUpdate: (meta: MetaProgress) => void;
  onBack: () => void;
}

type ShopCategory = 'all' | 'base_weapon' | 'elemental_weapon' | 'ship_unlock' | 'weapon_slot' | 'permanent_stat' | 'permanent_passive';

const PlasmaShop: React.FC<PlasmaShopProps> = ({ meta, onUpdate, onBack }) => {
  const [selectedCat, setSelectedCat] = useState<ShopCategory>('all');
  const [flash, setFlash] = useState<string | null>(null);

  const filtered = selectedCat === 'all' ? ALL_SHOP_ITEMS : ALL_SHOP_ITEMS.filter(i => i.category === selectedCat);

  const handleBuy = (item: ShopItem) => {
    const count = item.purchased(meta);
    if (count >= item.maxPurchases) return;
    if (meta.plasma < item.cost) { playError(); return; }
    playPurchase();
    const newMeta = { ...meta };
    newMeta.plasma -= item.cost;
    item.apply(newMeta);
    saveMeta(newMeta);
    onUpdate(newMeta);
    setFlash(item.id);
    setTimeout(() => setFlash(null), 400);
  };

  const catButtons: { key: ShopCategory; label: string; emoji: string }[] = [
    { key: 'all', label: 'Tudo', emoji: '🛒' },
    { key: 'base_weapon', label: 'Armas Base', emoji: '🔱' },
    { key: 'elemental_weapon', label: 'Elementais', emoji: '⚡' },
    { key: 'ship_unlock', label: 'Naves', emoji: '🚀' },
    { key: 'weapon_slot', label: 'Slots', emoji: '🔫' },
    { key: 'permanent_stat', label: 'Stats', emoji: '📈' },
    { key: 'permanent_passive', label: 'Passivas', emoji: '🍀' },
  ];

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-[#000008] text-[#e0e8ff] select-none p-4">
      <h1 className="text-4xl md:text-5xl font-bold mb-2 font-mono" style={{ color: '#bf5af2', textShadow: '0 0 30px rgba(191,90,242,0.4)' }}>
        ⚡ PLASMA SHOP
      </h1>
      
      <div className="flex items-center gap-2 mb-4 py-2 px-5 rounded-lg" style={{ background: 'rgba(191,90,242,0.15)', border: '1px solid rgba(191,90,242,0.3)' }}>
        <img src={UI_ICONS.plasma} alt="Plasma" className="w-7 h-7 object-contain" />
        <span className="font-mono font-bold text-2xl" style={{ color: '#bf5af2' }}>{meta.plasma}</span>
        <span className="font-mono text-sm text-[#6080aa]">Plasma</span>
      </div>

      <div className="flex flex-wrap gap-1.5 mb-4 justify-center">
        {catButtons.map(c => (
          <button key={c.key}
            onClick={() => { playClick(); setSelectedCat(c.key); }}
            onMouseEnter={playHover}
            className="px-2.5 py-1 rounded-lg font-mono text-xs font-bold transition-all"
            style={{
              background: selectedCat === c.key ? 'rgba(191,90,242,0.25)' : 'rgba(255,255,255,0.03)',
              border: `1px solid ${selectedCat === c.key ? 'rgba(191,90,242,0.6)' : 'rgba(255,255,255,0.08)'}`,
              color: selectedCat === c.key ? '#bf5af2' : '#6080aa',
            }}>
            {c.emoji} {c.label}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-2 max-w-7xl w-full mb-6 max-h-[60vh] overflow-y-auto pr-1"
        style={{ scrollbarWidth: 'thin', scrollbarColor: '#bf5af233 transparent' }}>
        {filtered.map(item => {
          const count = item.purchased(meta);
          const maxed = count >= item.maxPurchases;
          const canAfford = meta.plasma >= item.cost;
          const isFlashing = flash === item.id;
          const isShip = item.category === 'ship_unlock';
          const isBase = item.category === 'base_weapon';
          const isElemental = item.category === 'elemental_weapon';

          const badgeColor = item.badgeColor ?? (
            isBase ? '#0af' :
            isShip ? '#ff6b00' :
            item.category === 'permanent_passive' ? '#00ffc8' :
            '#bf5af2'
          );
          const badge = item.badge ?? (isBase ? 'BASE' : isShip ? 'NAVE' : item.category === 'permanent_passive' ? 'PASSIVA' : null);

          return (
            <button key={item.id}
              onClick={() => handleBuy(item)}
              onMouseEnter={playHover}
              disabled={maxed || !canAfford}
              className="flex flex-col items-center p-2.5 rounded-xl border transition-all duration-200 font-mono relative overflow-hidden"
              style={{
                background: isFlashing ? 'rgba(191,90,242,0.2)' : maxed ? 'rgba(0,255,100,0.03)' : 'rgba(0,0,20,0.9)',
                borderColor: maxed ? 'rgba(0,255,100,0.2)' : isElemental ? `${badgeColor}44` : isBase ? 'rgba(0,170,255,0.25)' : isShip ? 'rgba(255,100,0,0.3)' : canAfford ? 'rgba(191,90,242,0.2)' : 'rgba(255,255,255,0.05)',
                opacity: maxed ? 0.65 : canAfford ? 1 : 0.5,
                cursor: maxed || !canAfford ? 'not-allowed' : 'pointer',
                transform: isFlashing ? 'scale(1.05)' : 'scale(1)',
              }}>
              {maxed && (
                <div className="absolute top-1 right-1 text-[8px] px-1 py-0.5 rounded font-bold" style={{ background: 'rgba(0,255,100,0.2)', color: '#00ff64' }}>✓ MAX</div>
              )}
              {badge && !maxed && (
                <div className="absolute top-1 left-1 text-[7px] px-1 py-0.5 rounded font-bold" style={{ background: `${badgeColor}22`, color: badgeColor }}>{badge}</div>
              )}
              
              <div className="mt-3 mb-1">
                {isShip ? (
                  <ShipCanvas shipType={item.id.replace('unlock_', '') as ShipType} width={52} height={38} />
                ) : item.icon ? (
                  <img src={item.icon} alt={item.name} className="w-10 h-10 object-contain" />
                ) : (
                  <span className="text-2xl">{item.emoji}</span>
                )}
              </div>
              
              <h3 className="text-[10px] font-bold mb-0.5 text-center leading-tight" style={{ color: maxed ? '#00ff64' : '#e0e8ff' }}>{item.name}</h3>
              <p className="text-[8px] text-[#6080aa] text-center mb-1 leading-tight line-clamp-2">{item.description}</p>
              
              {item.maxPurchases > 1 && (
                <div className="flex gap-0.5 mb-1 flex-wrap justify-center">
                  {Array.from({ length: Math.min(item.maxPurchases, 10) }).map((_, i) => (
                    <div key={i} className="w-1.5 h-1.5 rounded-full" style={{
                      background: i < count ? (isElemental ? badgeColor : '#bf5af2') : '#1a2040',
                      boxShadow: i < count ? `0 0 4px ${isElemental ? badgeColor : '#bf5af2'}` : 'none',
                    }} />
                  ))}
                </div>
              )}
              
              {!maxed && (
                <div className="flex items-center gap-1">
                  <img src={UI_ICONS.plasma} alt="" className="w-3 h-3 object-contain" />
                  <span className="text-[10px] font-bold" style={{ color: canAfford ? '#bf5af2' : '#ff4060' }}>{item.cost}</span>
                </div>
              )}
            </button>
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

export default PlasmaShop;
