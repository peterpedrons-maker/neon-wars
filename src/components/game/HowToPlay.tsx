import React from 'react';

interface HowToPlayProps {
  onBack: () => void;
}

const HowToPlay: React.FC<HowToPlayProps> = ({ onBack }) => {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-[#1a0e0a] text-[#f5e6d3] select-none p-4">
      <h2 className="text-4xl font-bold mb-2" style={{ fontFamily: 'Georgia, serif', textShadow: '0 0 20px rgba(241,196,15,0.3)' }}>
        📜 Como Jogar
      </h2>
      <div className="w-48 h-px bg-gradient-to-r from-transparent via-[#5a3a28] to-transparent mb-8" />

      <div className="max-w-lg space-y-6 text-left">
        <section>
          <h3 className="text-xl font-bold text-[#f1c40f] mb-2" style={{ fontFamily: 'Georgia, serif' }}>🖥️ Desktop</h3>
          <ul className="space-y-1 text-[#8a7a6a]">
            <li><span className="text-[#f5e6d3] font-mono">WASD</span> — Mover</li>
            <li><span className="text-[#f5e6d3] font-mono">Mouse</span> — Mirar</li>
            <li><span className="text-[#f5e6d3] font-mono">Clique Esquerdo</span> — Atacar</li>
            <li><span className="text-[#f5e6d3] font-mono">Espaço / Clique Direito</span> — Habilidade Especial</li>
          </ul>
        </section>

        <section>
          <h3 className="text-xl font-bold text-[#f1c40f] mb-2" style={{ fontFamily: 'Georgia, serif' }}>📱 Mobile</h3>
          <ul className="space-y-1 text-[#8a7a6a]">
            <li><span className="text-[#f5e6d3]">Joystick Esquerdo</span> — Mover</li>
            <li><span className="text-[#f5e6d3]">Joystick Direito</span> — Mirar e Atacar</li>
            <li><span className="text-[#f5e6d3]">Botão ✨</span> — Habilidade Especial</li>
          </ul>
        </section>

        <section>
          <h3 className="text-xl font-bold text-[#f1c40f] mb-2" style={{ fontFamily: 'Georgia, serif' }}>⚡ Power-ups</h3>
          <ul className="space-y-1 text-[#8a7a6a]">
            <li>💨 <span className="text-[#f5e6d3]">Velocidade</span> — Movimento acelerado</li>
            <li>🔥 <span className="text-[#f5e6d3]">Tiro Triplo</span> — Ataque em leque</li>
            <li>🛡️ <span className="text-[#f5e6d3]">Escudo</span> — Bloqueia o próximo golpe</li>
            <li>💚 <span className="text-[#f5e6d3]">Cura</span> — Recupera vida</li>
          </ul>
        </section>

        <section>
          <h3 className="text-xl font-bold text-[#f1c40f] mb-2" style={{ fontFamily: 'Georgia, serif' }}>👾 Dica</h3>
          <p className="text-[#8a7a6a]">
            A cada 5 ondas um <span className="text-[#e74c3c] font-bold">Boss</span> aparece! 
            Colete power-ups e escolha upgrades sabiamente entre as ondas.
          </p>
        </section>
      </div>

      <button
        onClick={onBack}
        className="mt-8 text-[#8a7a6a] hover:text-[#f5e6d3] transition-colors text-lg"
        style={{ fontFamily: 'Georgia, serif' }}
      >
        ← Voltar
      </button>
    </div>
  );
};

export default HowToPlay;
