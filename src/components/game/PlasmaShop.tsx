import React, { useState } from 'react';
import { MetaProgress, saveMeta } from '../../game/meta';
import { playClick, playHover, playBack, playPurchase, playError } from '../../game/audio';
import { SHIP_ICONS, ABILITY_ICONS, UI_ICONS } from '../../game/icons';

export interface ShopItem {
  id: string;
  name: string;
  description: string;
  icon: string;
  cost: number;
  maxPurchases: number;
  category: 'weapon_slot' | 'permanent_stat' | 'weapon_unlock' | 'ship_unlock' | 'permanent_passive';
  apply: (meta: MetaProgress) => void;
  purchased: (meta: MetaProgress) => number;
}

const SHOP_ITEMS: ShopItem[] = [
  // === SHIP UNLOCKS ===
  { id: 'unlock_spectre', name: 'Spectre', description: 'Nave furtiva com teleporte. Alta velocidade, baixa vida.', icon: '🌀', cost: 200, maxPurchases: 1, category: 'ship_unlock', apply: (m) => { if (!m.unlockedShips.includes('spectre')) m.unlockedShips.push('spectre'); }, purchased: (m) => m.unlockedShips.includes('spectre') ? 1 : 0 },
  { id: 'unlock_valkyrie', name: 'Valkyrie', description: 'Guerreira alada com tiro duplo e chuva de lanças.', icon: '🦅', cost: 300, maxPurchases: 1, category: 'ship_unlock', apply: (m) => { if (!m.unlockedShips.includes('valkyrie')) m.unlockedShips.push('valkyrie'); }, purchased: (m) => m.unlockedShips.includes('valkyrie') ? 1 : 0 },
  { id: 'unlock_juggernaut', name: 'Juggernaut', description: 'Fortaleza indestrutível. 5 HP base, dano massivo.', icon: '🛡️', cost: 500, maxPurchases: 1, category: 'ship_unlock', apply: (m) => { if (!m.unlockedShips.includes('juggernaut')) m.unlockedShips.push('juggernaut'); }, purchased: (m) => m.unlockedShips.includes('juggernaut') ? 1 : 0 },
  { id: 'unlock_sentinel', name: 'Sentinel', description: 'Tanque com barreira. Especial: Escudo + reflexão.', icon: '🏰', cost: 350, maxPurchases: 1, category: 'ship_unlock', apply: (m) => { if (!m.unlockedShips.includes('sentinel')) m.unlockedShips.push('sentinel'); }, purchased: (m) => m.unlockedShips.includes('sentinel') ? 1 : 0 },
  { id: 'unlock_venom', name: 'Venom', description: 'Envenenador com tiros tóxicos persistentes.', icon: '🐍', cost: 400, maxPurchases: 1, category: 'ship_unlock', apply: (m) => { if (!m.unlockedShips.includes('venom')) m.unlockedShips.push('venom'); }, purchased: (m) => m.unlockedShips.includes('venom') ? 1 : 0 },
  { id: 'unlock_nova_ship', name: 'Nova', description: 'Poder bruto. Especial: Supernova devastadora.', icon: '💫', cost: 450, maxPurchases: 1, category: 'ship_unlock', apply: (m) => { if (!m.unlockedShips.includes('nova_ship')) m.unlockedShips.push('nova_ship'); }, purchased: (m) => m.unlockedShips.includes('nova_ship') ? 1 : 0 },
  { id: 'unlock_leviathan', name: 'Leviathan', description: 'Colosso devorador. 8 HP, dano extremo.', icon: '🐉', cost: 600, maxPurchases: 1, category: 'ship_unlock', apply: (m) => { if (!m.unlockedShips.includes('leviathan')) m.unlockedShips.push('leviathan'); }, purchased: (m) => m.unlockedShips.includes('leviathan') ? 1 : 0 },
  { id: 'unlock_oracle', name: 'Oracle', description: 'Tiros rastreadores inteligentes.', icon: '🔮', cost: 400, maxPurchases: 1, category: 'ship_unlock', apply: (m) => { if (!m.unlockedShips.includes('oracle')) m.unlockedShips.push('oracle'); }, purchased: (m) => m.unlockedShips.includes('oracle') ? 1 : 0 },
  { id: 'unlock_pyro', name: 'Pyro', description: 'Lança-chamas devastador de curto alcance.', icon: '🔥', cost: 350, maxPurchases: 1, category: 'ship_unlock', apply: (m) => { if (!m.unlockedShips.includes('pyro')) m.unlockedShips.push('pyro'); }, purchased: (m) => m.unlockedShips.includes('pyro') ? 1 : 0 },
  // === WEAPON SLOTS ===
  { id: 'slot_4', name: '+1 Slot de Arma', description: 'Equipe até 4 armas por run', icon: '🔫', cost: 100, maxPurchases: 1, category: 'weapon_slot', apply: (m) => { m.weaponSlots = Math.max(m.weaponSlots, 4); }, purchased: (m) => m.weaponSlots >= 4 ? 1 : 0 },
  { id: 'slot_5', name: '+1 Slot de Arma', description: 'Equipe até 5 armas por run', icon: '🔫', cost: 300, maxPurchases: 1, category: 'weapon_slot', apply: (m) => { m.weaponSlots = Math.max(m.weaponSlots, 5); }, purchased: (m) => m.weaponSlots >= 5 ? 1 : 0 },
  { id: 'slot_6', name: '+1 Slot de Arma', description: 'Equipe até 6 armas por run', icon: '🔫', cost: 600, maxPurchases: 1, category: 'weapon_slot', apply: (m) => { m.weaponSlots = Math.max(m.weaponSlots, 6); }, purchased: (m) => m.weaponSlots >= 6 ? 1 : 0 },
  // === WEAPON UNLOCKS ===
  { id: 'unlock_frost_nova', name: 'Frost Nova', description: 'Desbloqueia a arma Frost Nova no level up', icon: '❄️', cost: 80, maxPurchases: 1, category: 'weapon_unlock', apply: (m) => { if (!m.unlockedAbilities.includes('frost_nova')) m.unlockedAbilities.push('frost_nova'); }, purchased: (m) => m.unlockedAbilities.includes('frost_nova') ? 1 : 0 },
  { id: 'unlock_missile_barrage', name: 'Missile Barrage', description: 'Mísseis teleguiados automáticos', icon: '🚀', cost: 120, maxPurchases: 1, category: 'weapon_unlock', apply: (m) => { if (!m.unlockedAbilities.includes('missile_barrage')) m.unlockedAbilities.push('missile_barrage'); }, purchased: (m) => m.unlockedAbilities.includes('missile_barrage') ? 1 : 0 },
  { id: 'unlock_plasma_field', name: 'Plasma Field', description: 'Zonas de plasma no chão', icon: '🟣', cost: 150, maxPurchases: 1, category: 'weapon_unlock', apply: (m) => { if (!m.unlockedAbilities.includes('plasma_field')) m.unlockedAbilities.push('plasma_field'); }, purchased: (m) => m.unlockedAbilities.includes('plasma_field') ? 1 : 0 },
  { id: 'unlock_lightning_ring', name: 'Lightning Ring', description: 'Raios automáticos periódicos', icon: '⚡', cost: 150, maxPurchases: 1, category: 'weapon_unlock', apply: (m) => { if (!m.unlockedAbilities.includes('lightning_ring')) m.unlockedAbilities.push('lightning_ring'); }, purchased: (m) => m.unlockedAbilities.includes('lightning_ring') ? 1 : 0 },
  { id: 'unlock_flame_trail', name: 'Flame Trail', description: 'Rastro de fogo ao mover', icon: '🔥', cost: 120, maxPurchases: 1, category: 'weapon_unlock', apply: (m) => { if (!m.unlockedAbilities.includes('flame_trail')) m.unlockedAbilities.push('flame_trail'); }, purchased: (m) => m.unlockedAbilities.includes('flame_trail') ? 1 : 0 },
  { id: 'unlock_chain_lightning', name: 'Chain Lightning', description: 'Raios que saltam entre inimigos ao matar', icon: '🔗', cost: 180, maxPurchases: 1, category: 'weapon_unlock', apply: (m) => { if (!m.unlockedAbilities.includes('chain_lightning')) m.unlockedAbilities.push('chain_lightning'); }, purchased: (m) => m.unlockedAbilities.includes('chain_lightning') ? 1 : 0 },
  { id: 'unlock_orbital', name: 'Orbital Drones', description: 'Drones que orbitam e danificam inimigos', icon: '🛸', cost: 100, maxPurchases: 1, category: 'weapon_unlock', apply: (m) => { if (!m.unlockedAbilities.includes('orbital')) m.unlockedAbilities.push('orbital'); }, purchased: (m) => m.unlockedAbilities.includes('orbital') ? 1 : 0 },
  // === PERMANENT STATS ===
  { id: 'perm_hp', name: '+1 HP Máximo', description: 'Começa cada run com +1 HP', icon: '❤️', cost: 80, maxPurchases: 5, category: 'permanent_stat', apply: (m) => { m.permBonuses = m.permBonuses || {}; m.permBonuses.hp = (m.permBonuses.hp || 0) + 1; }, purchased: (m) => m.permBonuses?.hp || 0 },
  { id: 'perm_damage', name: '+10% Dano Base', description: 'Bônus de dano permanente', icon: '⚔️', cost: 100, maxPurchases: 5, category: 'permanent_stat', apply: (m) => { m.permBonuses = m.permBonuses || {}; m.permBonuses.damage = (m.permBonuses.damage || 0) + 0.1; }, purchased: (m) => Math.round((m.permBonuses?.damage || 0) / 0.1) },
  { id: 'perm_speed', name: '+5% Velocidade', description: 'Move mais rápido desde o início', icon: '🏃', cost: 60, maxPurchases: 5, category: 'permanent_stat', apply: (m) => { m.permBonuses = m.permBonuses || {}; m.permBonuses.speed = (m.permBonuses.speed || 0) + 0.05; }, purchased: (m) => Math.round((m.permBonuses?.speed || 0) / 0.05) },
  { id: 'perm_magnet', name: '+20% XP Magnet', description: 'Coleta XP de mais longe', icon: '🧲', cost: 50, maxPurchases: 5, category: 'permanent_stat', apply: (m) => { m.permBonuses = m.permBonuses || {}; m.permBonuses.magnet = (m.permBonuses.magnet || 0) + 0.2; }, purchased: (m) => Math.round((m.permBonuses?.magnet || 0) / 0.2) },
  { id: 'perm_armor', name: '+10% Redução Dano', description: 'Recebe menos dano permanentemente', icon: '🛡️', cost: 120, maxPurchases: 3, category: 'permanent_stat', apply: (m) => { m.permBonuses = m.permBonuses || {}; m.permBonuses.armor = (m.permBonuses.armor || 0) + 0.1; }, purchased: (m) => Math.round((m.permBonuses?.armor || 0) / 0.1) },
  { id: 'perm_plasma_mult', name: '+10% Plasma Ganho', description: 'Ganha mais plasma por run', icon: '💎', cost: 200, maxPurchases: 5, category: 'permanent_stat', apply: (m) => { m.permBonuses = m.permBonuses || {}; m.permBonuses.plasmaMultiplier = (m.permBonuses.plasmaMultiplier || 0) + 0.1; }, purchased: (m) => Math.round((m.permBonuses?.plasmaMultiplier || 0) / 0.1) },
  // === PERMANENT PASSIVES ===
  { id: 'perm_regen', name: 'Regeneração', description: 'Regenera 1 HP a cada 30s em todas as runs', icon: '💚', cost: 250, maxPurchases: 3, category: 'permanent_passive', apply: (m) => { m.permBonuses = m.permBonuses || {}; (m.permBonuses as any).regenLevel = ((m.permBonuses as any).regenLevel || 0) + 1; }, purchased: (m) => (m.permBonuses as any)?.regenLevel || 0 },
  { id: 'perm_crit', name: 'Precisão Crítica', description: '+5% de chance de crítico em todas as runs', icon: '🎯', cost: 180, maxPurchases: 5, category: 'permanent_passive', apply: (m) => { m.permBonuses = m.permBonuses || {}; (m.permBonuses as any).critBonus = ((m.permBonuses as any).critBonus || 0) + 0.05; }, purchased: (m) => Math.round(((m.permBonuses as any)?.critBonus || 0) / 0.05) },
  { id: 'perm_luck', name: 'Fortuna', description: '+5% chance de drop de power-up em todas as runs', icon: '🍀', cost: 150, maxPurchases: 5, category: 'permanent_passive', apply: (m) => { m.permBonuses = m.permBonuses || {}; (m.permBonuses as any).luckBonus = ((m.permBonuses as any).luckBonus || 0) + 0.05; }, purchased: (m) => Math.round(((m.permBonuses as any)?.luckBonus || 0) / 0.05) },
  { id: 'perm_xp', name: 'Experiência+', description: '+10% XP ganho em todas as runs', icon: '📖', cost: 160, maxPurchases: 5, category: 'permanent_passive', apply: (m) => { m.permBonuses = m.permBonuses || {}; (m.permBonuses as any).xpBonusPerm = ((m.permBonuses as any).xpBonusPerm || 0) + 0.1; }, purchased: (m) => Math.round(((m.permBonuses as any)?.xpBonusPerm || 0) / 0.1) },
  { id: 'perm_dodge', name: 'Evasão Instintiva', description: '+3% chance de esquivar dano em todas as runs', icon: '💨', cost: 220, maxPurchases: 5, category: 'permanent_passive', apply: (m) => { m.permBonuses = m.permBonuses || {}; (m.permBonuses as any).dodgeBonus = ((m.permBonuses as any).dodgeBonus || 0) + 0.03; }, purchased: (m) => Math.round(((m.permBonuses as any)?.dodgeBonus || 0) / 0.03) },
];

interface PlasmaShopProps {
  meta: MetaProgress;
  onUpdate: (meta: MetaProgress) => void;
  onBack: () => void;
}

type ShopCategory = 'all' | 'ship_unlock' | 'weapon_slot' | 'weapon_unlock' | 'permanent_stat' | 'permanent_passive';

const PlasmaShop: React.FC<PlasmaShopProps> = ({ meta, onUpdate, onBack }) => {
  const [selectedCat, setSelectedCat] = useState<ShopCategory>('all');
  const [flash, setFlash] = useState<string | null>(null);

  const filtered = selectedCat === 'all' ? SHOP_ITEMS : SHOP_ITEMS.filter(i => i.category === selectedCat);

  const handleBuy = (item: ShopItem) => {
    const count = item.purchased(meta);
    if (count >= item.maxPurchases) return;
    if (meta.plasma < item.cost) { playError(); return; }
    playPurchase();
    meta.plasma -= item.cost;
    item.apply(meta);
    saveMeta(meta);
    onUpdate({ ...meta });
    setFlash(item.id);
    setTimeout(() => setFlash(null), 400);
  };

  const catButtons: { key: ShopCategory; label: string; icon: string }[] = [
    { key: 'all', label: 'Tudo', icon: '🛒' },
    { key: 'ship_unlock', label: 'Naves', icon: '🚀' },
    { key: 'weapon_slot', label: 'Slots', icon: '🔫' },
    { key: 'weapon_unlock', label: 'Armas', icon: '⚔️' },
    { key: 'permanent_stat', label: 'Stats', icon: '📈' },
    { key: 'permanent_passive', label: 'Passivas', icon: '🍀' },
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
            {c.icon} {c.label}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-2.5 max-w-6xl w-full mb-6 max-h-[58vh] overflow-y-auto pr-1"
        style={{ scrollbarWidth: 'thin', scrollbarColor: '#bf5af233 transparent' }}>
        {filtered.map(item => {
          const count = item.purchased(meta);
          const maxed = count >= item.maxPurchases;
          const canAfford = meta.plasma >= item.cost;
          const isFlashing = flash === item.id;
          const isShip = item.category === 'ship_unlock';
          const isPassive = item.category === 'permanent_passive';

          return (
            <button key={item.id}
              onClick={() => handleBuy(item)}
              onMouseEnter={playHover}
              disabled={maxed || !canAfford}
              className="flex flex-col items-center p-3 rounded-xl border transition-all duration-200 font-mono relative overflow-hidden"
              style={{
                background: isFlashing ? 'rgba(191,90,242,0.2)' : maxed ? 'rgba(0,255,100,0.03)' : 'rgba(0,0,20,0.9)',
                borderColor: maxed ? 'rgba(0,255,100,0.2)' : isShip ? 'rgba(255,100,0,0.3)' : isPassive ? 'rgba(0,255,200,0.2)' : canAfford ? 'rgba(191,90,242,0.2)' : 'rgba(255,255,255,0.05)',
                opacity: maxed ? 0.6 : canAfford ? 1 : 0.5,
                cursor: maxed || !canAfford ? 'not-allowed' : 'pointer',
                transform: isFlashing ? 'scale(1.05)' : 'scale(1)',
              }}>
              {maxed && (
                <div className="absolute top-1.5 right-1.5 text-[9px] px-1 py-0.5 rounded font-bold" style={{ background: 'rgba(0,255,100,0.2)', color: '#00ff64' }}>✓</div>
              )}
              {isShip && !maxed && (
                <div className="absolute top-1.5 left-1.5 text-[9px] px-1 py-0.5 rounded font-bold" style={{ background: 'rgba(255,100,0,0.2)', color: '#ff6b00' }}>NAVE</div>
              )}
              {isPassive && !maxed && (
                <div className="absolute top-1.5 left-1.5 text-[9px] px-1 py-0.5 rounded font-bold" style={{ background: 'rgba(0,255,200,0.15)', color: '#00ffc8' }}>PASSIVA</div>
              )}
              <span className="text-2xl mb-1">{item.icon}</span>
              <h3 className="text-[11px] font-bold mb-0.5" style={{ color: maxed ? '#00ff64' : '#e0e8ff' }}>{item.name}</h3>
              <p className="text-[9px] text-[#6080aa] text-center mb-1.5 leading-tight">{item.description}</p>
              
              {item.maxPurchases > 1 && (
                <div className="flex gap-0.5 mb-1">
                  {Array.from({ length: item.maxPurchases }).map((_, i) => (
                    <div key={i} className="w-1.5 h-1.5 rounded-full" style={{
                      background: i < count ? '#bf5af2' : '#1a2040',
                      boxShadow: i < count ? '0 0 4px #bf5af2' : 'none',
                    }} />
                  ))}
                </div>
              )}
              
              {!maxed && (
                <div className="flex items-center gap-1">
                  <span className="text-[10px]">⚡</span>
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