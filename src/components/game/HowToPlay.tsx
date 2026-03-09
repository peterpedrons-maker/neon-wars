import React from 'react';
import { playBack, playHover } from '../../game/audio';

interface HowToPlayProps {
  onBack: () => void;
}

const HowToPlay: React.FC<HowToPlayProps> = ({ onBack }) => {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-[#000008] text-[#e0e8ff] select-none p-4">
      <h2 className="text-4xl font-bold mb-2 font-mono" style={{ color: '#0ff', textShadow: '0 0 20px rgba(0,255,255,0.3)' }}>
        📡 Como Jogar
      </h2>
      <div className="w-48 h-px bg-gradient-to-r from-transparent via-[#0ff] to-transparent mb-8" />

      <div className="max-w-lg space-y-6 text-left">
        <section>
          <h3 className="text-xl font-bold mb-2 font-mono" style={{ color: '#0ff' }}>🖥️ Desktop</h3>
          <ul className="space-y-1 text-[#6080aa]">
            <li><span className="text-[#e0e8ff] font-mono">WASD</span> — Mover nave</li>
            <li><span className="text-[#e0e8ff] font-mono">Mouse</span> — Mirar</li>
            <li><span className="text-[#e0e8ff] font-mono">Clique Esquerdo</span> — Disparar</li>
            <li><span className="text-[#e0e8ff] font-mono">Espaço / Clique Direito</span> — Habilidade Especial</li>
          </ul>
        </section>

        <section>
          <h3 className="text-xl font-bold mb-2 font-mono" style={{ color: '#0ff' }}>📱 Mobile</h3>
          <ul className="space-y-1 text-[#6080aa]">
            <li><span className="text-[#e0e8ff]">Joystick Esquerdo</span> — Mover</li>
            <li><span className="text-[#e0e8ff]">Joystick Direito</span> — Mirar e Disparar</li>
            <li><span className="text-[#e0e8ff]">Botão ✨</span> — Habilidade Especial</li>
          </ul>
        </section>

        <section>
          <h3 className="text-xl font-bold mb-2 font-mono" style={{ color: '#0ff' }}>⚡ Power-ups</h3>
          <ul className="space-y-1 text-[#6080aa]">
            <li>⚡ <span className="text-[#e0e8ff]">Velocidade</span> — Propulsão acelerada</li>
            <li>◆ <span className="text-[#e0e8ff]">Tiro Triplo</span> — Disparo em leque</li>
            <li>◯ <span className="text-[#e0e8ff]">Escudo</span> — Bloqueia o próximo golpe</li>
            <li>+ <span className="text-[#e0e8ff]">Reparo</span> — Recupera HP</li>
          </ul>
        </section>

        <section>
          <h3 className="text-xl font-bold mb-2 font-mono" style={{ color: '#0ff' }}>⚠️ Dica</h3>
          <p className="text-[#6080aa]">
            A cada 5 waves um <span className="font-bold" style={{ color: '#ff0040' }}>Boss</span> aparece!
            Colete power-ups e escolha upgrades entre as waves.
          </p>
        </section>
      </div>

      <button
        onClick={onBack}
        className="mt-8 text-[#6080aa] hover:text-[#0ff] transition-colors text-lg font-mono"
      >
        ← Voltar
      </button>
    </div>
  );
};

export default HowToPlay;
