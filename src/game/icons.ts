// Game Icon Imports - AI-generated icons for upgrades, abilities, shop, and achievements
import upgradeShield from '@/assets/icons/upgrade-shield.png';
import upgradeDamage from '@/assets/icons/upgrade-damage.png';
import upgradeSpeed from '@/assets/icons/upgrade-speed.png';
import upgradeFirerate from '@/assets/icons/upgrade-firerate.png';
import upgradeHeal from '@/assets/icons/upgrade-heal.png';
import plasmaCrystal from '@/assets/icons/plasma-crystal.png';
import achievementTrophy from '@/assets/icons/achievement-trophy.png';

// Original ability icons (kept for backward compat)
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

// Achievement icons
import achFirstKill from '@/assets/icons/ach-first-kill.png';
import achWave from '@/assets/icons/ach-wave.png';
import achScore from '@/assets/icons/ach-score.png';
import achCombo from '@/assets/icons/ach-combo.png';
import achKills from '@/assets/icons/ach-kills.png';
import achBoss from '@/assets/icons/ach-boss.png';
import achShips from '@/assets/icons/ach-ships.png';
import achExplore from '@/assets/icons/ach-explore.png';
import achNodmg from '@/assets/icons/ach-nodmg.png';
import achStar from '@/assets/icons/ach-star.png';
import achDiamond from '@/assets/icons/ach-diamond.png';
import achEye from '@/assets/icons/ach-eye.png';
import achRuns from '@/assets/icons/ach-runs.png';
import achPlasma from '@/assets/icons/ach-plasma.png';

// NEW AI-Generated Weapon Icons
import weaponOrbitals from '@/assets/icons/weapon-orbitals.png';
import weaponAura from '@/assets/icons/weapon-aura.png';
import weaponChain from '@/assets/icons/weapon-chain.png';
import weaponMultishot from '@/assets/icons/weapon-multishot.png';
import weaponExplosion from '@/assets/icons/weapon-explosion.png';
import weaponHoming from '@/assets/icons/weapon-homing.png';
import weaponPiercing from '@/assets/icons/weapon-piercing.png';
import weaponRicochet from '@/assets/icons/weapon-ricochet.png';
import weaponIonBeam from '@/assets/icons/weapon-ionbeam.png';
import weaponShockwave from '@/assets/icons/weapon-shockwave.png';
import weaponSentry from '@/assets/icons/weapon-sentry.png';
import weaponIceBeam from '@/assets/icons/weapon-icebeam.png';
import weaponBoomerang from '@/assets/icons/weapon-boomerang.png';
import weaponHeavyCannon from '@/assets/icons/weapon-heavycannon.png';
import weaponAcidSpray from '@/assets/icons/weapon-acidspray.png';
import weaponGravityWell from '@/assets/icons/weapon-gravitywell.png';
import weaponTeslaCoil from '@/assets/icons/weapon-teslacoil.png';
import weaponVoidRift from '@/assets/icons/weapon-voidrift.png';
import weaponFrostNova from '@/assets/icons/weapon-frostnova.png';
import weaponMissile from '@/assets/icons/weapon-missile.png';
import weaponPlasmaField from '@/assets/icons/weapon-plasmafield.png';
import weaponLightningRing from '@/assets/icons/weapon-lightningring.png';
import weaponFlameTrail from '@/assets/icons/weapon-flametrail.png';
import weaponChainLightning from '@/assets/icons/weapon-chainlightning.png';

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

// Weapon icons by ability ID
export const WEAPON_ICONS: Record<string, string> = {
  orbitals: weaponOrbitals,
  aura: weaponAura,
  chain: weaponChain,
  multishot: weaponMultishot,
  explosion: weaponExplosion,
  homing: weaponHoming,
  piercing_rounds: weaponPiercing,
  ricochet_rounds: weaponRicochet,
  ion_beam: weaponIonBeam,
  shockwave_emitter: weaponShockwave,
  sentry_drones: weaponSentry,
  frost_nova: weaponFrostNova,
  missile_barrage: weaponMissile,
  plasma_field: weaponPlasmaField,
  lightning_ring: weaponLightningRing,
  flame_trail: weaponFlameTrail,
  chain_lightning_weapon: weaponChainLightning,
  ice_beam: weaponIceBeam,
  boomerang: weaponBoomerang,
  heavy_cannon: weaponHeavyCannon,
  acid_spray: weaponAcidSpray,
  gravity_well: weaponGravityWell,
  tesla_coil: weaponTeslaCoil,
  void_rift: weaponVoidRift,
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

// Get icon for a specific achievement based on its ID
export function getAchievementIcon(achId: string): string | null {
  if (achId.includes('first_kill')) return achFirstKill;
  if (achId.includes('nodmg')) return achNodmg;
  if (achId.includes('kill') || achId.includes('genocida') || achId.includes('apocalipse') || achId.includes('exterminador')) return achKills;
  if (achId.includes('wave') || achId.includes('sobrevivente')) return achWave;
  if (achId.includes('score')) return achScore;
  if (achId.includes('combo') || achId.includes('frenesi')) return achCombo;
  if (achId.includes('boss') || achId.includes('caçador')) return achBoss;
  if (achId.includes('ship') || achId.includes('piloto') || achId.includes('almirante') || achId.includes('frotas')) return achShips;
  if (achId.includes('_play') || achId.includes('explorador')) return achExplore;
  if (achId.includes('runs') || achId.includes('persistente')) return achRuns;
  if (achId.includes('plasma') || achId.includes('magnata')) return achPlasma;
  if (achId.includes('lenda') || achId.includes('lendário')) return achStar;
  if (achId.includes('deus') || achId.includes('transcendente')) return achDiamond;
  if (achId.includes('mestre') || achId.includes('imortal') || achId.includes('elite')) return achEye;
  if (achId.includes('destruidor')) return achCombo;
  if (achId.includes('veterano')) return achStar;
  if (achId.includes('dominador')) return achScore;
  return null;
}
