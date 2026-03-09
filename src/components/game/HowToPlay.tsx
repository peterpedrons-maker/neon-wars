import React, { useEffect } from 'react';
import { playBack, playHover, startHowToPlayMusic, stopHowToPlayMusic } from '../../game/audio';
import { useLanguage } from '../../game/i18n';

interface HowToPlayProps {
  onBack: () => void;
}

const HowToPlay: React.FC<HowToPlayProps> = ({ onBack }) => {
  const { t } = useLanguage();
  useEffect(() => { startHowToPlayMusic(); return () => { stopHowToPlayMusic(); }; }, []);
  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-[#000008] text-[#e0e8ff] select-none p-4">
      <h2 className="text-4xl font-bold mb-2 font-mono" style={{ color: '#0ff', textShadow: '0 0 20px rgba(0,255,255,0.3)' }}>
        {t('htp_title')}
      </h2>
      <div className="w-48 h-px bg-gradient-to-r from-transparent via-[#0ff] to-transparent mb-8" />

      <div className="max-w-lg space-y-6 text-left">
        <section>
          <h3 className="text-xl font-bold mb-2 font-mono" style={{ color: '#0ff' }}>{t('htp_desktop')}</h3>
          <ul className="space-y-1 text-[#6080aa]">
            <li><span className="text-[#e0e8ff] font-mono">WASD</span> — {t('htp_move')}</li>
            <li><span className="text-[#e0e8ff] font-mono">Mouse</span> — {t('htp_aim')}</li>
            <li><span className="text-[#e0e8ff] font-mono">{t('htp_shoot')}</span> — Click</li>
            <li><span className="text-[#e0e8ff] font-mono">Space / Right Click</span> — {t('htp_special')}</li>
          </ul>
        </section>

        <section>
          <h3 className="text-xl font-bold mb-2 font-mono" style={{ color: '#0ff' }}>{t('htp_mobile')}</h3>
          <ul className="space-y-1 text-[#6080aa]">
            <li><span className="text-[#e0e8ff]">Joystick L</span> — {t('htp_move_joystick')}</li>
            <li><span className="text-[#e0e8ff]">Joystick R</span> — {t('htp_aim_joystick')}</li>
            <li><span className="text-[#e0e8ff]">✨</span> — {t('htp_special_btn')}</li>
          </ul>
        </section>

        <section>
          <h3 className="text-xl font-bold mb-2 font-mono" style={{ color: '#0ff' }}>{t('htp_powerups')}</h3>
          <ul className="space-y-1 text-[#6080aa]">
            <li>⚡ <span className="text-[#e0e8ff]">{t('htp_speed')}</span> — {t('htp_speed_desc')}</li>
            <li>◆ <span className="text-[#e0e8ff]">{t('htp_triple')}</span> — {t('htp_triple_desc')}</li>
            <li>◯ <span className="text-[#e0e8ff]">{t('htp_shield')}</span> — {t('htp_shield_desc')}</li>
            <li>+ <span className="text-[#e0e8ff]">{t('htp_repair')}</span> — {t('htp_repair_desc')}</li>
          </ul>
        </section>

        <section>
          <h3 className="text-xl font-bold mb-2 font-mono" style={{ color: '#0ff' }}>{t('htp_tip_title')}</h3>
          <p className="text-[#6080aa]">{t('htp_tip')}</p>
        </section>
      </div>

      <button
        onClick={() => { playBack(); onBack(); }}
        onMouseEnter={playHover}
        className="mt-8 text-[#6080aa] hover:text-[#0ff] transition-colors text-lg font-mono"
      >
        {t('back')}
      </button>
    </div>
  );
};

export default HowToPlay;
