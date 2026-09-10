import React, { useEffect, useState } from 'react';
import { useLanguage } from '../../game/i18n';
import { playClick } from '../../game/audio';

const DISMISS_KEY = 'neonwars_install_dismissed_at';
const DISMISS_DAYS = 7;
const AUTO_SHOW_DELAY_MS = 1200;

interface BeforeInstallPromptEvent extends Event {
  prompt: () => Promise<void>;
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>;
}

function isStandalone() {
  return (
    window.matchMedia('(display-mode: standalone)').matches ||
    window.matchMedia('(display-mode: fullscreen)').matches ||
    (window.navigator as unknown as { standalone?: boolean }).standalone === true
  );
}

function isIOS() {
  return /iPad|iPhone|iPod/.test(navigator.userAgent) && !('MSStream' in window);
}

function wasRecentlyDismissed() {
  const raw = localStorage.getItem(DISMISS_KEY);
  if (!raw) return false;
  const days = (Date.now() - Number(raw)) / (1000 * 60 * 60 * 24);
  return days < DISMISS_DAYS;
}

/**
 * Shows an install prompt automatically shortly after the app loads —
 * like a native app-store installer would — rather than waiting on the
 * browser's own `beforeinstallprompt` timing, which is gated by opaque
 * engagement heuristics and may not fire on a first visit at all.
 *
 * If the native event does arrive (immediately, or while this is already
 * showing) the CTA upgrades to a real "Instalar" button wired to it;
 * otherwise it falls back to manual instructions for the platform.
 */
const InstallPrompt: React.FC = () => {
  const { t } = useLanguage();
  const [deferredEvent, setDeferredEvent] = useState<BeforeInstallPromptEvent | null>(null);
  const [visible, setVisible] = useState(false);
  const [eligible] = useState(() => !isStandalone() && !wasRecentlyDismissed());

  useEffect(() => {
    if (!eligible) return;

    const onBeforeInstall = (e: Event) => {
      e.preventDefault();
      setDeferredEvent(e as BeforeInstallPromptEvent);
      setVisible(true);
    };
    const onInstalled = () => {
      setVisible(false);
      setDeferredEvent(null);
    };

    window.addEventListener('beforeinstallprompt', onBeforeInstall);
    window.addEventListener('appinstalled', onInstalled);

    const timer = setTimeout(() => setVisible(true), AUTO_SHOW_DELAY_MS);

    return () => {
      window.removeEventListener('beforeinstallprompt', onBeforeInstall);
      window.removeEventListener('appinstalled', onInstalled);
      clearTimeout(timer);
    };
  }, [eligible]);

  const dismiss = () => {
    playClick();
    localStorage.setItem(DISMISS_KEY, String(Date.now()));
    setVisible(false);
  };

  const install = async () => {
    playClick();
    if (!deferredEvent) return;
    await deferredEvent.prompt();
    const choice = await deferredEvent.userChoice;
    if (choice.outcome !== 'accepted') {
      localStorage.setItem(DISMISS_KEY, String(Date.now()));
    }
    setDeferredEvent(null);
    setVisible(false);
  };

  if (!visible) return null;

  const bodyText = deferredEvent
    ? t('install_body')
    : isIOS()
      ? <>{t('install_ios_body')} <span style={{ color: '#0ff' }}>⎋</span> {t('install_ios_step')}</>
      : t('install_generic_body');

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center px-4" style={{ background: 'rgba(0,0,8,0.75)' }}>
      <div className="w-full max-w-sm rounded-2xl p-6 text-center font-mono"
        style={{ background: '#050516', border: '1px solid rgba(0,255,255,0.35)', boxShadow: '0 0 40px rgba(0,255,255,0.15)' }}>
        <div className="text-4xl mb-3">🚀</div>
        <h2 className="text-lg font-bold mb-2" style={{ color: '#0ff', textShadow: '0 0 10px rgba(0,255,255,0.5)' }}>
          {t('install_title')}
        </h2>

        <p className="text-sm text-[#a0b0d0] mb-5 leading-relaxed">{bodyText}</p>

        <div className="flex flex-col gap-2">
          {deferredEvent && (
            <button onClick={install}
              className="py-3 px-6 text-base font-bold rounded-lg text-white transition-all active:scale-95"
              style={{ background: 'linear-gradient(135deg, rgba(0,229,255,0.25), rgba(191,90,242,0.25))', border: '1px solid #0ff', boxShadow: '0 0 15px rgba(0,255,255,0.25)' }}>
              {t('install_button')}
            </button>
          )}
          <button onClick={dismiss}
            className="py-2 px-6 text-sm text-[#6080aa] hover:text-[#0ff] transition-colors">
            {t('install_later')}
          </button>
        </div>
      </div>
    </div>
  );
};

export default InstallPrompt;
