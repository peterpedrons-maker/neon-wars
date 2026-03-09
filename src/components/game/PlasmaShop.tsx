import React, { useState, useEffect } from 'react';
import { MetaProgress, saveMeta } from '../../game/meta';
import { playClick, playHover, playBack, playPurchase, playError, startShopMusic, stopShopMusic } from '../../game/audio';
import { UI_ICONS, SHOP_ICONS, WEAPON_ICONS } from '../../game/icons';
import ShipCanvas from './ShipCanvas';
import { ShipType } from '../../game/types';
import { useLanguage } from '../../game/i18n';

export interface ShopItem {
  id: string;
  name: string;
  description: string;
  icon?: string;
  emoji?: string;
  cost: number;
  maxPurchases: number;
  category: 'weapon_slot' | 'permanent_stat' | 'weapon_unlock' | 'ship_unlock' | 'permanent_passive' | 'base_weapon' | 'elemental_weapon';
  apply: (meta: MetaProgress) => void;
  purchased: (meta: MetaProgress) => number;
  badge?: string;
  badgeColor?: string;
}

function getWeaponLevel(meta: MetaProgress, id: string): number {
  return (meta as any).weaponUpgrades?.[id] ?? 0;
}
function setWeaponLevel(meta: MetaProgress, id: string, level: number) {
  if (!(meta as any).weaponUpgrades) (meta as any).weaponUpgrades = {};
  (meta as any).weaponUpgrades[id] = level;
}

interface PlasmaShopProps {
  meta: MetaProgress;
  onUpdate: (meta: MetaProgress) => void;
  onBack: () => void;
}

type ShopCategory = 'all' | 'base_weapon' | 'elemental_weapon' | 'ship_unlock' | 'weapon_slot' | 'permanent_stat' | 'permanent_passive';

const PlasmaShop: React.FC<PlasmaShopProps> = ({ meta, onUpdate, onBack }) => {
  const { t, lang } = useLanguage();
  const [selectedCat, setSelectedCat] = useState<ShopCategory>('all');
  const [flash, setFlash] = useState<string | null>(null);

  useEffect(() => { startShopMusic(); return () => { stopShopMusic(); }; }, []);

  // Build shop items with translations
  const BASE_WEAPON_ITEMS: ShopItem[] = [
    { id: 'upg_orbitals', name: 'Orbital Drones', description: t('shop_orbital_desc'), icon: WEAPON_ICONS.orbitals, cost: 60, maxPurchases: 5, category: 'base_weapon', apply: (m) => { setWeaponLevel(m, 'orbitals', getWeaponLevel(m, 'orbitals') + 1); }, purchased: (m) => getWeaponLevel(m, 'orbitals'), badge: t('badge_base') },
    { id: 'upg_aura', name: 'Neon Aura', description: t('shop_aura_desc'), icon: WEAPON_ICONS.aura, cost: 70, maxPurchases: 5, category: 'base_weapon', apply: (m) => { setWeaponLevel(m, 'aura', getWeaponLevel(m, 'aura') + 1); }, purchased: (m) => getWeaponLevel(m, 'aura'), badge: t('badge_base') },
    { id: 'upg_chain', name: lang === 'pt' ? 'Raio Cadeia' : 'Chain Ray', description: t('shop_chain_desc'), icon: WEAPON_ICONS.chain, cost: 80, maxPurchases: 5, category: 'base_weapon', apply: (m) => { setWeaponLevel(m, 'chain', getWeaponLevel(m, 'chain') + 1); }, purchased: (m) => getWeaponLevel(m, 'chain'), badge: t('badge_base') },
    { id: 'upg_multishot', name: 'Multi-Shot', description: t('shop_multishot_desc'), icon: WEAPON_ICONS.multishot, cost: 90, maxPurchases: 3, category: 'base_weapon', apply: (m) => { setWeaponLevel(m, 'multishot', getWeaponLevel(m, 'multishot') + 1); }, purchased: (m) => getWeaponLevel(m, 'multishot'), badge: t('badge_base') },
    { id: 'upg_explosion', name: lang === 'pt' ? 'Proj. Explosivo' : 'Explosive Proj.', description: t('shop_explosion_desc'), icon: WEAPON_ICONS.explosion, cost: 100, maxPurchases: 4, category: 'base_weapon', apply: (m) => { setWeaponLevel(m, 'explosion', getWeaponLevel(m, 'explosion') + 1); }, purchased: (m) => getWeaponLevel(m, 'explosion'), badge: t('badge_base') },
    { id: 'upg_homing', name: lang === 'pt' ? 'Auto-Mira' : 'Auto-Aim', description: t('shop_homing_desc'), icon: WEAPON_ICONS.homing, cost: 90, maxPurchases: 5, category: 'base_weapon', apply: (m) => { setWeaponLevel(m, 'homing', getWeaponLevel(m, 'homing') + 1); }, purchased: (m) => getWeaponLevel(m, 'homing'), badge: t('badge_base') },
    { id: 'upg_piercing_rounds', name: lang === 'pt' ? 'Balas Perfurantes' : 'Piercing Rounds', description: t('shop_piercing_desc'), icon: WEAPON_ICONS.piercing_rounds, cost: 80, maxPurchases: 4, category: 'base_weapon', apply: (m) => { setWeaponLevel(m, 'piercing_rounds', getWeaponLevel(m, 'piercing_rounds') + 1); }, purchased: (m) => getWeaponLevel(m, 'piercing_rounds'), badge: t('badge_base') },
    { id: 'upg_ricochet_rounds', name: lang === 'pt' ? 'Ricochete' : 'Ricochet', description: t('shop_ricochet_desc'), icon: WEAPON_ICONS.ricochet_rounds, cost: 80, maxPurchases: 4, category: 'base_weapon', apply: (m) => { setWeaponLevel(m, 'ricochet_rounds', getWeaponLevel(m, 'ricochet_rounds') + 1); }, purchased: (m) => getWeaponLevel(m, 'ricochet_rounds'), badge: t('badge_base') },
    { id: 'upg_ion_beam', name: 'Ion Beam', description: t('shop_ion_desc'), icon: WEAPON_ICONS.ion_beam, cost: 110, maxPurchases: 5, category: 'base_weapon', apply: (m) => { setWeaponLevel(m, 'ion_beam', getWeaponLevel(m, 'ion_beam') + 1); }, purchased: (m) => getWeaponLevel(m, 'ion_beam'), badge: t('badge_base') },
    { id: 'upg_shockwave_emitter', name: 'Shockwave', description: t('shop_shockwave_desc'), icon: WEAPON_ICONS.shockwave_emitter, cost: 110, maxPurchases: 5, category: 'base_weapon', apply: (m) => { setWeaponLevel(m, 'shockwave_emitter', getWeaponLevel(m, 'shockwave_emitter') + 1); }, purchased: (m) => getWeaponLevel(m, 'shockwave_emitter'), badge: t('badge_base') },
    { id: 'upg_sentry_drones', name: 'Sentry Drones', description: t('shop_sentry_desc'), icon: WEAPON_ICONS.sentry_drones, cost: 100, maxPurchases: 5, category: 'base_weapon', apply: (m) => { setWeaponLevel(m, 'sentry_drones', getWeaponLevel(m, 'sentry_drones') + 1); }, purchased: (m) => getWeaponLevel(m, 'sentry_drones'), badge: t('badge_base') },
  ];

  const ELEMENTAL_WEAPON_ITEMS: ShopItem[] = [
    { id: 'upg_frost_nova', name: 'Frost Nova', description: t('shop_frost_desc'), icon: WEAPON_ICONS.frost_nova, cost: 90, maxPurchases: 5, category: 'elemental_weapon', apply: (m) => { setWeaponLevel(m, 'frost_nova', getWeaponLevel(m, 'frost_nova') + 1); }, purchased: (m) => getWeaponLevel(m, 'frost_nova'), badge: t('badge_ice'), badgeColor: '#00cfff' },
    { id: 'upg_missile_barrage', name: 'Missile Barrage', description: t('shop_missile_desc'), icon: WEAPON_ICONS.missile_barrage, cost: 120, maxPurchases: 5, category: 'elemental_weapon', apply: (m) => { setWeaponLevel(m, 'missile_barrage', getWeaponLevel(m, 'missile_barrage') + 1); }, purchased: (m) => getWeaponLevel(m, 'missile_barrage'), badge: t('badge_missile'), badgeColor: '#ff6b00' },
    { id: 'upg_plasma_field', name: 'Plasma Field', description: t('shop_plasma_field_desc'), icon: WEAPON_ICONS.plasma_field, cost: 130, maxPurchases: 4, category: 'elemental_weapon', apply: (m) => { setWeaponLevel(m, 'plasma_field', getWeaponLevel(m, 'plasma_field') + 1); }, purchased: (m) => getWeaponLevel(m, 'plasma_field'), badge: t('badge_plasma'), badgeColor: '#bf5af2' },
    { id: 'upg_lightning_ring', name: 'Lightning Ring', description: t('shop_lightning_desc'), icon: WEAPON_ICONS.lightning_ring, cost: 130, maxPurchases: 5, category: 'elemental_weapon', apply: (m) => { setWeaponLevel(m, 'lightning_ring', getWeaponLevel(m, 'lightning_ring') + 1); }, purchased: (m) => getWeaponLevel(m, 'lightning_ring'), badge: t('badge_lightning'), badgeColor: '#ffe033' },
    { id: 'upg_flame_trail', name: 'Flame Trail', description: t('shop_flame_desc'), icon: WEAPON_ICONS.flame_trail, cost: 110, maxPurchases: 4, category: 'elemental_weapon', apply: (m) => { setWeaponLevel(m, 'flame_trail', getWeaponLevel(m, 'flame_trail') + 1); }, purchased: (m) => getWeaponLevel(m, 'flame_trail'), badge: t('badge_fire'), badgeColor: '#ff4400' },
    { id: 'upg_chain_lightning_weapon', name: lang === 'pt' ? 'Raio Cadeia+' : 'Chain Lightning+', description: t('shop_chain_lightning_desc'), icon: WEAPON_ICONS.chain_lightning_weapon, cost: 140, maxPurchases: 5, category: 'elemental_weapon', apply: (m) => { setWeaponLevel(m, 'chain_lightning_weapon', getWeaponLevel(m, 'chain_lightning_weapon') + 1); }, purchased: (m) => getWeaponLevel(m, 'chain_lightning_weapon'), badge: t('badge_arc'), badgeColor: '#33aaff' },
    { id: 'upg_ice_beam', name: lang === 'pt' ? 'Raio de Gelo' : 'Ice Beam', description: t('shop_ice_beam_desc'), icon: WEAPON_ICONS.ice_beam, cost: 120, maxPurchases: 5, category: 'elemental_weapon', apply: (m) => { setWeaponLevel(m, 'ice_beam', getWeaponLevel(m, 'ice_beam') + 1); }, purchased: (m) => getWeaponLevel(m, 'ice_beam'), badge: t('badge_slow'), badgeColor: '#00d4ff' },
    { id: 'upg_boomerang', name: lang === 'pt' ? 'Bumerangue' : 'Boomerang', description: t('shop_boomerang_desc'), icon: WEAPON_ICONS.boomerang, cost: 110, maxPurchases: 5, category: 'elemental_weapon', apply: (m) => { setWeaponLevel(m, 'boomerang', getWeaponLevel(m, 'boomerang') + 1); }, purchased: (m) => getWeaponLevel(m, 'boomerang'), badge: t('badge_return'), badgeColor: '#cc88ff' },
    { id: 'upg_heavy_cannon', name: lang === 'pt' ? 'Canhão Pesado' : 'Heavy Cannon', description: t('shop_heavy_cannon_desc'), icon: WEAPON_ICONS.heavy_cannon, cost: 150, maxPurchases: 5, category: 'elemental_weapon', apply: (m) => { setWeaponLevel(m, 'heavy_cannon', getWeaponLevel(m, 'heavy_cannon') + 1); }, purchased: (m) => getWeaponLevel(m, 'heavy_cannon'), badge: t('badge_power'), badgeColor: '#ff6600' },
    { id: 'upg_acid_spray', name: lang === 'pt' ? 'Spray Ácido' : 'Acid Spray', description: t('shop_acid_desc'), icon: WEAPON_ICONS.acid_spray, cost: 110, maxPurchases: 4, category: 'elemental_weapon', apply: (m) => { setWeaponLevel(m, 'acid_spray', getWeaponLevel(m, 'acid_spray') + 1); }, purchased: (m) => getWeaponLevel(m, 'acid_spray'), badge: t('badge_acid'), badgeColor: '#44ff44' },
    { id: 'upg_gravity_well', name: lang === 'pt' ? 'Poço Gravitacional' : 'Gravity Well', description: t('shop_gravity_desc'), icon: WEAPON_ICONS.gravity_well, cost: 160, maxPurchases: 4, category: 'elemental_weapon', apply: (m) => { setWeaponLevel(m, 'gravity_well', getWeaponLevel(m, 'gravity_well') + 1); }, purchased: (m) => getWeaponLevel(m, 'gravity_well'), badge: t('badge_grav'), badgeColor: '#aa44ff' },
    { id: 'upg_tesla_coil', name: lang === 'pt' ? 'Bobina Tesla' : 'Tesla Coil', description: t('shop_tesla_desc'), icon: WEAPON_ICONS.tesla_coil, cost: 130, maxPurchases: 5, category: 'elemental_weapon', apply: (m) => { setWeaponLevel(m, 'tesla_coil', getWeaponLevel(m, 'tesla_coil') + 1); }, purchased: (m) => getWeaponLevel(m, 'tesla_coil'), badge: t('badge_tesla'), badgeColor: '#44aaff' },
    { id: 'upg_void_rift', name: lang === 'pt' ? 'Fenda do Vazio' : 'Void Rift', description: t('shop_void_desc'), icon: WEAPON_ICONS.void_rift, cost: 180, maxPurchases: 4, category: 'elemental_weapon', apply: (m) => { setWeaponLevel(m, 'void_rift', getWeaponLevel(m, 'void_rift') + 1); }, purchased: (m) => getWeaponLevel(m, 'void_rift'), badge: t('badge_void'), badgeColor: '#9900cc' },
  ];

  const OTHER_SHOP_ITEMS: ShopItem[] = [
    // Ships
    { id: 'unlock_spectre', name: 'Spectre', description: t('shop_spectre_desc'), emoji: '🌀', cost: 200, maxPurchases: 1, category: 'ship_unlock', apply: (m) => { if (!m.unlockedShips.includes('spectre')) m.unlockedShips.push('spectre'); }, purchased: (m) => m.unlockedShips.includes('spectre') ? 1 : 0 },
    { id: 'unlock_valkyrie', name: 'Valkyrie', description: t('shop_valkyrie_desc'), emoji: '🦅', cost: 300, maxPurchases: 1, category: 'ship_unlock', apply: (m) => { if (!m.unlockedShips.includes('valkyrie')) m.unlockedShips.push('valkyrie'); }, purchased: (m) => m.unlockedShips.includes('valkyrie') ? 1 : 0 },
    { id: 'unlock_juggernaut', name: 'Juggernaut', description: t('shop_juggernaut_desc'), emoji: '🛡️', cost: 500, maxPurchases: 1, category: 'ship_unlock', apply: (m) => { if (!m.unlockedShips.includes('juggernaut')) m.unlockedShips.push('juggernaut'); }, purchased: (m) => m.unlockedShips.includes('juggernaut') ? 1 : 0 },
    { id: 'unlock_sentinel', name: 'Sentinel', description: t('shop_sentinel_desc'), emoji: '🏰', cost: 350, maxPurchases: 1, category: 'ship_unlock', apply: (m) => { if (!m.unlockedShips.includes('sentinel')) m.unlockedShips.push('sentinel'); }, purchased: (m) => m.unlockedShips.includes('sentinel') ? 1 : 0 },
    { id: 'unlock_venom', name: 'Venom', description: t('shop_venom_desc'), emoji: '🐍', cost: 400, maxPurchases: 1, category: 'ship_unlock', apply: (m) => { if (!m.unlockedShips.includes('venom')) m.unlockedShips.push('venom'); }, purchased: (m) => m.unlockedShips.includes('venom') ? 1 : 0 },
    { id: 'unlock_nova_ship', name: 'Nova', description: t('shop_nova_desc'), emoji: '💫', cost: 450, maxPurchases: 1, category: 'ship_unlock', apply: (m) => { if (!m.unlockedShips.includes('nova_ship')) m.unlockedShips.push('nova_ship'); }, purchased: (m) => m.unlockedShips.includes('nova_ship') ? 1 : 0 },
    { id: 'unlock_leviathan', name: 'Leviathan', description: t('shop_leviathan_desc'), emoji: '🐉', cost: 600, maxPurchases: 1, category: 'ship_unlock', apply: (m) => { if (!m.unlockedShips.includes('leviathan')) m.unlockedShips.push('leviathan'); }, purchased: (m) => m.unlockedShips.includes('leviathan') ? 1 : 0 },
    { id: 'unlock_oracle', name: 'Oracle', description: t('shop_oracle_desc'), emoji: '🔮', cost: 400, maxPurchases: 1, category: 'ship_unlock', apply: (m) => { if (!m.unlockedShips.includes('oracle')) m.unlockedShips.push('oracle'); }, purchased: (m) => m.unlockedShips.includes('oracle') ? 1 : 0 },
    { id: 'unlock_pyro', name: 'Pyro', description: t('shop_pyro_desc'), emoji: '🔥', cost: 350, maxPurchases: 1, category: 'ship_unlock', apply: (m) => { if (!m.unlockedShips.includes('pyro')) m.unlockedShips.push('pyro'); }, purchased: (m) => m.unlockedShips.includes('pyro') ? 1 : 0 },
    // Slots
    { id: 'slot_4', name: '+1 Weapon Slot', description: lang === 'pt' ? 'Equipe até 4 armas por run' : 'Equip up to 4 weapons per run', emoji: '🔫', cost: 100, maxPurchases: 1, category: 'weapon_slot', apply: (m) => { m.weaponSlots = Math.max(m.weaponSlots, 4); }, purchased: (m) => m.weaponSlots >= 4 ? 1 : 0 },
    { id: 'slot_5', name: '+1 Weapon Slot', description: lang === 'pt' ? 'Equipe até 5 armas por run' : 'Equip up to 5 weapons per run', emoji: '🔫', cost: 300, maxPurchases: 1, category: 'weapon_slot', apply: (m) => { m.weaponSlots = Math.max(m.weaponSlots, 5); }, purchased: (m) => m.weaponSlots >= 5 ? 1 : 0 },
    { id: 'slot_6', name: '+1 Weapon Slot', description: lang === 'pt' ? 'Equipe até 6 armas por run' : 'Equip up to 6 weapons per run', emoji: '🔫', cost: 600, maxPurchases: 1, category: 'weapon_slot', apply: (m) => { m.weaponSlots = Math.max(m.weaponSlots, 6); }, purchased: (m) => m.weaponSlots >= 6 ? 1 : 0 },
    // Stats
    { id: 'perm_hp', name: t('shop_hp_name'), description: t('shop_hp_desc'), emoji: '❤️', cost: 80, maxPurchases: 5, category: 'permanent_stat', apply: (m) => { m.permBonuses = m.permBonuses || {}; m.permBonuses.hp = (m.permBonuses.hp || 0) + 1; }, purchased: (m) => m.permBonuses?.hp || 0 },
    { id: 'perm_damage', name: t('shop_damage_name'), description: t('shop_damage_desc'), emoji: '⚔️', cost: 100, maxPurchases: 5, category: 'permanent_stat', apply: (m) => { m.permBonuses = m.permBonuses || {}; m.permBonuses.damage = (m.permBonuses.damage || 0) + 0.1; }, purchased: (m) => Math.round((m.permBonuses?.damage || 0) / 0.1) },
    { id: 'perm_speed', name: t('shop_speed_name'), description: t('shop_speed_desc'), emoji: '🏃', cost: 60, maxPurchases: 5, category: 'permanent_stat', apply: (m) => { m.permBonuses = m.permBonuses || {}; m.permBonuses.speed = (m.permBonuses.speed || 0) + 0.05; }, purchased: (m) => Math.round((m.permBonuses?.speed || 0) / 0.05) },
    { id: 'perm_magnet', name: t('shop_magnet_name'), description: t('shop_magnet_desc'), emoji: '🧲', cost: 50, maxPurchases: 5, category: 'permanent_stat', apply: (m) => { m.permBonuses = m.permBonuses || {}; m.permBonuses.magnet = (m.permBonuses.magnet || 0) + 0.2; }, purchased: (m) => Math.round((m.permBonuses?.magnet || 0) / 0.2) },
    { id: 'perm_armor', name: t('shop_armor_name'), description: t('shop_armor_desc'), emoji: '🛡️', cost: 120, maxPurchases: 3, category: 'permanent_stat', apply: (m) => { m.permBonuses = m.permBonuses || {}; m.permBonuses.armor = (m.permBonuses.armor || 0) + 0.1; }, purchased: (m) => Math.round((m.permBonuses?.armor || 0) / 0.1) },
    { id: 'perm_plasma_mult', name: t('shop_plasma_mult_name'), description: t('shop_plasma_mult_desc'), emoji: '💎', cost: 200, maxPurchases: 5, category: 'permanent_stat', apply: (m) => { m.permBonuses = m.permBonuses || {}; m.permBonuses.plasmaMultiplier = (m.permBonuses.plasmaMultiplier || 0) + 0.1; }, purchased: (m) => Math.round((m.permBonuses?.plasmaMultiplier || 0) / 0.1) },
    // Passives
    { id: 'perm_regen', name: t('shop_regen_name'), description: t('shop_regen_desc'), emoji: '💚', cost: 250, maxPurchases: 3, category: 'permanent_passive', apply: (m) => { m.permBonuses = m.permBonuses || {}; (m.permBonuses as any).regenLevel = ((m.permBonuses as any).regenLevel || 0) + 1; }, purchased: (m) => (m.permBonuses as any)?.regenLevel || 0 },
    { id: 'perm_crit', name: t('shop_crit_name'), description: t('shop_crit_desc'), emoji: '🎯', cost: 180, maxPurchases: 5, category: 'permanent_passive', apply: (m) => { m.permBonuses = m.permBonuses || {}; (m.permBonuses as any).critBonus = ((m.permBonuses as any).critBonus || 0) + 0.05; }, purchased: (m) => Math.round(((m.permBonuses as any)?.critBonus || 0) / 0.05) },
    { id: 'perm_luck', name: t('shop_luck_name'), description: t('shop_luck_desc'), emoji: '🍀', cost: 150, maxPurchases: 5, category: 'permanent_passive', apply: (m) => { m.permBonuses = m.permBonuses || {}; (m.permBonuses as any).luckBonus = ((m.permBonuses as any).luckBonus || 0) + 0.05; }, purchased: (m) => Math.round(((m.permBonuses as any)?.luckBonus || 0) / 0.05) },
    { id: 'perm_xp', name: t('shop_xp_name'), description: t('shop_xp_desc'), emoji: '📖', cost: 160, maxPurchases: 5, category: 'permanent_passive', apply: (m) => { m.permBonuses = m.permBonuses || {}; (m.permBonuses as any).xpBonusPerm = ((m.permBonuses as any).xpBonusPerm || 0) + 0.1; }, purchased: (m) => Math.round(((m.permBonuses as any)?.xpBonusPerm || 0) / 0.1) },
    { id: 'perm_dodge', name: t('shop_dodge_name'), description: t('shop_dodge_desc'), emoji: '💨', cost: 220, maxPurchases: 5, category: 'permanent_passive', apply: (m) => { m.permBonuses = m.permBonuses || {}; (m.permBonuses as any).dodgeBonus = ((m.permBonuses as any).dodgeBonus || 0) + 0.03; }, purchased: (m) => Math.round(((m.permBonuses as any)?.dodgeBonus || 0) / 0.03) },
  ];

  const ALL_SHOP_ITEMS: ShopItem[] = [...BASE_WEAPON_ITEMS, ...ELEMENTAL_WEAPON_ITEMS, ...OTHER_SHOP_ITEMS];
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

  const catButtons: { key: ShopCategory; labelKey: string; emoji: string }[] = [
    { key: 'all', labelKey: 'shop_all', emoji: '🛒' },
    { key: 'base_weapon', labelKey: 'shop_base_weapons', emoji: '🔱' },
    { key: 'elemental_weapon', labelKey: 'shop_elemental', emoji: '⚡' },
    { key: 'ship_unlock', labelKey: 'shop_ships', emoji: '🚀' },
    { key: 'weapon_slot', labelKey: 'shop_slots', emoji: '🔫' },
    { key: 'permanent_stat', labelKey: 'shop_stats', emoji: '📈' },
    { key: 'permanent_passive', labelKey: 'shop_passives', emoji: '🍀' },
  ];

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-[#000008] text-[#e0e8ff] select-none p-4">
      <h1 className="text-4xl md:text-5xl font-bold mb-2 font-mono" style={{ color: '#bf5af2', textShadow: '0 0 30px rgba(191,90,242,0.4)' }}>
        {t('shop_title')}
      </h1>
      
      <div className="flex items-center gap-2 mb-4 py-2 px-5 rounded-lg" style={{ background: 'rgba(191,90,242,0.15)', border: '1px solid rgba(191,90,242,0.3)' }}>
        <img src={UI_ICONS.plasma} alt="Plasma" className="w-7 h-7 object-contain" />
        <span className="font-mono font-bold text-2xl" style={{ color: '#bf5af2' }}>{meta.plasma}</span>
        <span className="font-mono text-sm text-[#6080aa]">{t('plasma')}</span>
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
            {c.emoji} {t(c.labelKey as any)}
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

          const badgeColor = item.badgeColor ?? (isBase ? '#0af' : isShip ? '#ff6b00' : item.category === 'permanent_passive' ? '#00ffc8' : '#bf5af2');
          const badge = item.badge ?? (isBase ? t('badge_base') : isShip ? t('badge_nave') : item.category === 'permanent_passive' ? t('badge_passiva') : null);

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
        {t('back')}
      </button>
    </div>
  );
};

export default PlasmaShop;
