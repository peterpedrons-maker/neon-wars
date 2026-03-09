// Game Icon Imports - AI-generated icons for all ships, upgrades, and abilities
import shipPhantom from '@/assets/icons/ship-phantom.png';
import shipInterceptor from '@/assets/icons/ship-interceptor.png';
import shipTitan from '@/assets/icons/ship-titan.png';
import shipSpectre from '@/assets/icons/ship-spectre.png';
import shipValkyrie from '@/assets/icons/ship-valkyrie.png';
import shipJuggernaut from '@/assets/icons/ship-juggernaut.png';
import shipWraith from '@/assets/icons/ship-wraith.png';
import shipSentinel from '@/assets/icons/ship-sentinel.png';
import shipTempest from '@/assets/icons/ship-tempest.png';
import shipVenom from '@/assets/icons/ship-venom.png';
import shipNova from '@/assets/icons/ship-nova.png';
import shipChronos from '@/assets/icons/ship-chronos.png';
import shipLeviathan from '@/assets/icons/ship-leviathan.png';
import shipRaptor from '@/assets/icons/ship-raptor.png';
import shipOracle from '@/assets/icons/ship-oracle.png';
import shipPyro from '@/assets/icons/ship-pyro.png';

import upgradeShield from '@/assets/icons/upgrade-shield.png';
import upgradeDamage from '@/assets/icons/upgrade-damage.png';
import upgradeSpeed from '@/assets/icons/upgrade-speed.png';
import upgradeFirerate from '@/assets/icons/upgrade-firerate.png';
import upgradeHeal from '@/assets/icons/upgrade-heal.png';
import plasmaCrystal from '@/assets/icons/plasma-crystal.png';
import achievementTrophy from '@/assets/icons/achievement-trophy.png';

import abilityFrostNova from '@/assets/icons/ability-frost-nova.png';
import abilityMissile from '@/assets/icons/ability-missile.png';
import abilityLightning from '@/assets/icons/ability-lightning.png';
import abilityFlameTrail from '@/assets/icons/ability-flame-trail.png';
import abilityPlasmaField from '@/assets/icons/ability-plasma-field.png';
import abilityChainLightning from '@/assets/icons/ability-chain-lightning.png';
import abilityOrbital from '@/assets/icons/ability-orbital.png';

// Shop-specific icons
import shopWeaponSlot from '@/assets/icons/shop-weapon-slot.png';
import shopHp from '@/assets/icons/shop-hp.png';
import shopDamage from '@/assets/icons/shop-damage.png';
import shopSpeed from '@/assets/icons/shop-speed.png';
import shopMagnet from '@/assets/icons/shop-magnet.png';
import shopArmor from '@/assets/icons/shop-armor.png';
import shopPlasmaMult from '@/assets/icons/shop-plasma-mult.png';
import shopRegen from '@/assets/icons/shop-regen.png';
import shopCrit from '@/assets/icons/shop-crit.png';
import shopLuck from '@/assets/icons/shop-luck.png';
import shopXp from '@/assets/icons/shop-xp.png';
import shopDodge from '@/assets/icons/shop-dodge.png';

export const SHIP_ICONS: Record<string, string> = {
  phantom: shipPhantom,
  interceptor: shipInterceptor,
  titan: shipTitan,
  spectre: shipSpectre,
  valkyrie: shipValkyrie,
  juggernaut: shipJuggernaut,
  wraith: shipWraith,
  sentinel: shipSentinel,
  tempest: shipTempest,
  venom: shipVenom,
  nova_ship: shipNova,
  chronos: shipChronos,
  leviathan: shipLeviathan,
  raptor: shipRaptor,
  oracle: shipOracle,
  pyro: shipPyro,
};

export const UPGRADE_ICONS: Record<string, string> = {
  hp_up: upgradeShield,
  dmg_up: upgradeDamage,
  speed_up: upgradeSpeed,
  attack_speed: upgradeFirerate,
  special_cd: abilityPlasmaField,
  regen: upgradeHeal,
  armor: upgradeShield,
  critical: upgradeDamage,
};

export const ABILITY_ICONS: Record<string, string> = {
  frost_nova: abilityFrostNova,
  missile_barrage: abilityMissile,
  plasma_field: abilityPlasmaField,
  lightning_ring: abilityLightning,
  flame_trail: abilityFlameTrail,
  chain_lightning: abilityChainLightning,
  orbital: abilityOrbital,
};

export const SHOP_ICONS: Record<string, string> = {
  weapon_slot: shopWeaponSlot,
  perm_hp: shopHp,
  perm_damage: shopDamage,
  perm_speed: shopSpeed,
  perm_magnet: shopMagnet,
  perm_armor: shopArmor,
  perm_plasma_mult: shopPlasmaMult,
  perm_regen: shopRegen,
  perm_crit: shopCrit,
  perm_luck: shopLuck,
  perm_xp: shopXp,
  perm_dodge: shopDodge,
};

export const UI_ICONS = {
  plasma: plasmaCrystal,
  trophy: achievementTrophy,
};
