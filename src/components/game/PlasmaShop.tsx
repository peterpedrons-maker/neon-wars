import React, { useState } from 'react';
import { MetaProgress, saveMeta } from '../../game/meta';

export interface ShopItem {
  id: string;
  name: string;
  description: string;
  icon: string;
  cost: number;
  maxPurchases: number;
  category: 'weapon_slot' | 'permanent_stat' | 'weapon_unlock';
  apply: (meta: MetaProgress) => void;
  purchased: (meta: MetaProgress) => number;
}

const SHOP_ITEMS: ShopItem[] = [
  // Weapon slots
  {
    id: 'slot_4', name: '+1 Slot de Arma', description: 'Equipe até 4 armas por run',
    icon: '🔫', cost: 100, maxPurchases: 1, category: 'weapon_slot',
    apply: (m) => { m.weaponSlots = Math.max(m.weaponSlots, 4); },
    purchased: (m) => m.weaponSlots >= 4 ? 1 : 0,
  },
  {
    id: 'slot_5', name: '+1 Slot de Arma', description: 'Equipe até 5 armas por run',
    icon: '🔫', cost: 300, maxPurchases: 1, category: 'weapon_slot',
    apply: (m) => { m.weaponSlots = Math.max(m.weaponSlots, 5); },
    purchased: (m) => m.weaponSlots >= 5 ? 1 : 0,
  },
  {
    id: 'slot_6', name: '+1 Slot de Arma', description: 'Equipe até 6 armas por run',
    icon: '🔫', cost: 600, maxPurchases: 1, category: 'weapon_slot',
    apply: (m) => { m.weaponSlots = Math.max(m.weaponSlots, 6); },
    purchased: (m) => m.weaponSlots >= 6 ? 1 : 0,
  },
  // Weapon unlocks
  {
    id: 'unlock_frost_nova', name: 'Frost Nova', description: 'Desbloqueia a arma Frost Nova no level up',
    icon: '❄️', cost: 80, maxPurchases: 1, category: 'weapon_unlock',
    apply: (m) => { if (!m.unlockedAbilities.includes('frost_nova')) m.unlockedAbilities.push('frost_nova'); },
    purchased: (m) => m.unlockedAbilities.includes('frost_nova') ? 1 : 0,
  },
  {
    id: 'unlock_missile_barrage', name: 'Missile Barrage', description: 'Desbloqueia mísseis teleguiados automáticos',
    icon: '🚀', cost: 120, maxPurchases: 1, category: 'weapon_unlock',
    apply: (m) => { if (!m.unlockedAbilities.includes('missile_barrage')) m.unlockedAbilities.push('missile_barrage'); },
    purchased: (m) => m.unlockedAbilities.includes('missile_barrage') ? 1 : 0,
  },
  {
    id: 'unlock_plasma_field', name: 'Plasma Field', description: 'Desbloqueia zonas de plasma no chão',
    icon: '🟣', cost: 150, maxPurchases: 1, category: 'weapon_unlock',
    apply: (m) => { if (!m.unlockedAbilities.includes('plasma_field')) m.unlockedAbilities.push('plasma_field'); },
    purchased: (m) => m.unlockedAbilities.includes('plasma_field') ? 1 : 0,
  },
  {
    id: 'unlock_lightning_ring', name: 'Lightning Ring', description: 'Desbloqueia raios automáticos periódicos',
    icon: '⚡', cost: 150, maxPurchases: 1, category: 'weapon_unlock',
    apply: (m) => { if (!m.unlockedAbilities.includes('lightning_ring')) m.unlockedAbilities.push('lightning_ring'); },
    purchased: (m) => m.unlockedAbilities.includes('lightning_ring') ? 1 : 0,
  },
  {
    id: 'unlock_flame_trail', name: 'Flame Trail', description: 'Desbloqueia rastro de fogo ao mover',
    icon: '🔥', cost: 120, maxPurchases: 1, category: 'weapon_unlock',
    apply: (m) => { if (!m.unlockedAbilities.includes('flame_trail')) m.unlockedAbilities.push('flame_trail'); },
    purchased: (m) => m.unlockedAbilities.includes('flame_trail') ? 1 : 0,
  },
  // Permanent stats
  {
    id: 'perm_hp', name: '+1 HP Máximo', description: 'Começa cada run com +1 HP',
    icon: '❤️', cost: 80, maxPurchases: 5, category: 'permanent_stat',
    apply: (m) => { m.permBonuses = m.permBonuses || {}; m.permBonuses.hp = (m.permBonuses.hp || 0) + 1; },
    purchased: (m) => m.permBonuses?.hp || 0,
  },
  {
    id: 'perm_damage', name: '+10% Dano Base', description: 'Bônus de dano permanente para todas as runs',
    icon: '⚔️', cost: 100, maxPurchases: 5, category: 'permanent_stat',
    apply: (m) => { m.permBonuses = m.permBonuses || {}; m.permBonuses.damage = (m.permBonuses.damage || 0) + 0.1; },
    purchased: (m) => Math.round((m.permBonuses?.damage || 0) / 0.1),
  },
  {
    id: 'perm_speed', name: '+5% Velocidade', description: 'Move mais rápido desde o início',
    icon: '🏃', cost: 60, maxPurchases: 5, category: 'permanent_stat',
    apply: (m) => { m.permBonuses = m.permBonuses || {}; m.permBonuses.speed = (m.permBonuses.speed || 0) + 0.05; },
    purchased: (m) => Math.round((m.permBonuses?.speed || 0) / 0.05),
  },
  {
    id: 'perm_magnet', name: '+20% XP Magnet', description: 'Coleta XP de mais longe desde o início',
    icon: '🧲', cost: 50, maxPurchases: 5, category: 'permanent_stat',
    apply: (m) => { m.permBonuses = m.permBonuses || {}; m.permBonuses.magnet = (m.permBonuses.magnet || 0) + 0.2; },
    purchased: (m) => Math.round((m.permBonuses?.magnet || 0) / 0.2),
  },
  {
    id: 'perm_armor', name: '+10% Redução Dano', description: 'Recebe menos dano permanentemente',
    icon: '🛡️', cost: 120, maxPurchases: 3, category: 'permanent_stat',
    apply: (m) => { m.permBonuses = m.permBonuses || {}; m.permBonuses.armor = (m.permBonuses.armor || 0) + 0.1; },
    purchased: (m) => Math.round((m.permBonuses?.armor || 0) / 0.1),
  },
  {
    id: 'perm_plasma_mult', name: '+10% Plasma Ganho', description: 'Ganha mais plasma por run',
    icon: '💎', cost: 200, maxPurchases: 5, category: 'permanent_stat',
    apply: (m) => { m.permBonuses = m.permBonuses || {}; m.permBonuses.plasmaMultiplier = (m.permBonuses.plasmaMultiplier || 0) + 0.1; },
    purchased: (m) => Math.round((m.permBonuses?.plasmaMultiplier || 0) / 0.1),
  },
];

interface PlasmaShopProps {
  meta: MetaProgress;
  onUpdate: (meta: MetaProgress) => void;
  onBack: () => void;
}

const PlasmaShop: React.FC<PlasmaShopProps> = ({ meta, onUpdate, onBack }) => {
  const [selectedCat, setSelectedCat] = useState<'all' | 'weapon_slot' | 'weapon_unlock' | 'permanent_stat'>('all');
  const [flash, setFlash] = useState<string | null>(null);

  const filtered = selectedCat === 'all' ? SHOP_ITEMS : SHOP_ITEMS.filter(i => i.category === selectedCat);

  const handleBuy = (item: ShopItem) => {
    const count = item.purchased(meta);
    if (count >= item.maxPurchases) return;
    if (meta.plasma < item.cost) return;
    meta.plasma -= item.cost;
    item.apply(meta);
    saveMeta(meta);
    onUpdate({ ...meta });
    setFlash(item.id);
    setTimeout(() => setFlash(null), 400);
  };

  const catButtons: { key: typeof selectedCat; label: string; icon: string }[] = [
    { key: 'all', label: 'Tudo', icon: '🛒' },
    { key: 'weapon_slot', label: 'Slots', icon: '🔫' },
    { key: 'weapon_unlock', label: 'Armas', icon: '⚔️' },
    { key: 'permanent_stat', label: 'Stats', icon: '📈' },
  ];

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-[#000008] text-[#e0e8ff] select-none p-4">
      {/* Header */}
      <h1
        className="text-4xl md:text-5xl font-bold mb-2 font-mono"
        style={{ color: '#bf5af2', textShadow: '0 0 30px rgba(191,90,242,0.4)' }}
      >
        ⚡ PLASMA SHOP
      </h1>
      
      {/* Plasma balance */}
      <div className="flex items-center gap-2 mb-6 py-2 px-5 rounded-lg"
        style={{ background: 'rgba(191,90,242,0.15)', border: '1px solid rgba(191,90,242,0.3)' }}>
        <span className="text-xl">⚡</span>
        <span className="font-mono font-bold text-2xl" style={{ color: '#bf5af2' }}>{meta.plasma}</span>
        <span className="font-mono text-sm text-[#6080aa]">Plasma</span>
      </div>

      {/* Category filter */}
      <div className="flex gap-2 mb-6">
        {catButtons.map(c => (
          <button
            key={c.key}
            onClick={() => setSelectedCat(c.key)}
            className="px-3 py-1.5 rounded-lg font-mono text-sm font-bold transition-all"
            style={{
              background: selectedCat === c.key ? 'rgba(191,90,242,0.25)' : 'rgba(255,255,255,0.03)',
              border: `1px solid ${selectedCat === c.key ? 'rgba(191,90,242,0.6)' : 'rgba(255,255,255,0.08)'}`,
              color: selectedCat === c.key ? '#bf5af2' : '#6080aa',
            }}
          >
            {c.icon} {c.label}
          </button>
        ))}
      </div>

      {/* Items grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3 max-w-5xl w-full mb-8 max-h-[55vh] overflow-y-auto pr-1"
        style={{ scrollbarWidth: 'thin', scrollbarColor: '#bf5af233 transparent' }}>
        {filtered.map(item => {
          const count = item.purchased(meta);
          const maxed = count >= item.maxPurchases;
          const canAfford = meta.plasma >= item.cost;
          const isFlashing = flash === item.id;

          return (
            <button
              key={item.id}
              onClick={() => handleBuy(item)}
              disabled={maxed || !canAfford}
              className="flex flex-col items-center p-4 rounded-xl border transition-all duration-200 font-mono relative overflow-hidden"
              style={{
                background: isFlashing ? 'rgba(191,90,242,0.2)' : maxed ? 'rgba(0,255,100,0.03)' : 'rgba(0,0,20,0.9)',
                borderColor: maxed ? 'rgba(0,255,100,0.2)' : canAfford ? 'rgba(191,90,242,0.2)' : 'rgba(255,255,255,0.05)',
                opacity: maxed ? 0.6 : canAfford ? 1 : 0.5,
                cursor: maxed || !canAfford ? 'not-allowed' : 'pointer',
                transform: isFlashing ? 'scale(1.05)' : 'scale(1)',
              }}
            >
              {maxed && (
                <div className="absolute top-2 right-2 text-[10px] px-1.5 py-0.5 rounded font-bold"
                  style={{ background: 'rgba(0,255,100,0.2)', color: '#00ff64' }}>
                  COMPRADO
                </div>
              )}
              <span className="text-3xl mb-2">{item.icon}</span>
              <h3 className="text-sm font-bold mb-1" style={{ color: maxed ? '#00ff64' : '#e0e8ff' }}>{item.name}</h3>
              <p className="text-[10px] text-[#6080aa] text-center mb-2 leading-tight">{item.description}</p>
              
              {/* Progress dots */}
              {item.maxPurchases > 1 && (
                <div className="flex gap-1 mb-2">
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
                  <span className="text-xs">⚡</span>
                  <span className="text-xs font-bold" style={{ color: canAfford ? '#bf5af2' : '#ff4060' }}>{item.cost}</span>
                </div>
              )}
            </button>
          );
        })}
      </div>

      {/* Back */}
      <button
        onClick={onBack}
        className="py-3 px-8 text-lg font-bold rounded-lg text-[#6080aa] border border-[#6080aa]/30 transition-all duration-200 hover:border-[#0ff] hover:text-[#0ff] font-mono"
        style={{ background: 'rgba(0,255,255,0.03)' }}
      >
        ← Voltar
      </button>
    </div>
  );
};

export default PlasmaShop;
