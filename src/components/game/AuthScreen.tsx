import React, { useState } from 'react';
import { useLanguage } from '../../game/i18n';

interface AuthScreenProps {
  onAuth: (mode: 'login' | 'signup', email: string, password: string, username?: string) => Promise<{ error: string | null }>;
}

const AuthScreen: React.FC<AuthScreenProps> = ({ onAuth }) => {
  const { t, lang, setLang } = useLanguage();
  const [mode, setMode] = useState<'login' | 'signup'>('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [username, setUsername] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    if (mode === 'signup' && username.trim().length < 2) {
      setError(t('pilot_name_error'));
      setLoading(false);
      return;
    }

    const result = await onAuth(mode, email, password, username);
    setLoading(false);

    if (result.error) {
      setError(result.error);
    } else if (mode === 'signup') {
      setSuccess(t('signup_success'));
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen select-none"
      style={{ background: 'radial-gradient(ellipse at center, #000020 0%, #000008 100%)' }}>
      
      {/* Language toggle */}
      <button onClick={() => setLang(lang === 'pt' ? 'en' : 'pt')}
        className="absolute top-4 right-4 px-3 py-1.5 rounded-lg font-mono text-xs font-bold transition-all hover:scale-105 z-10"
        style={{ background: 'rgba(0,255,255,0.08)', border: '1px solid rgba(0,255,255,0.25)', color: '#0ff' }}>
        {t('language')}
      </button>

      <div className="mb-8 text-center">
        <h1 className="text-5xl md:text-7xl font-bold tracking-wider mb-2"
          style={{ fontFamily: 'Orbitron, monospace', textShadow: '0 0 40px rgba(0,255,255,0.4), 0 0 80px rgba(0,255,255,0.15)' }}>
          <span style={{ color: '#0ff' }}>NEON</span> <span style={{ color: '#ff1493' }}>WARS</span>
        </h1>
        <p className="text-lg text-[#6080aa] font-mono">{t('auth_subtitle')}</p>
      </div>

      <div className="w-full max-w-sm mx-4 rounded-2xl p-6 relative overflow-hidden"
        style={{
          background: 'linear-gradient(180deg, rgba(0,10,30,0.95), rgba(0,0,15,0.98))',
          border: '1px solid rgba(0,255,255,0.15)',
          boxShadow: '0 0 40px rgba(0,255,255,0.08), inset 0 0 30px rgba(0,255,255,0.03)',
        }}>
        
        <div className="flex mb-6 rounded-lg overflow-hidden" style={{ border: '1px solid rgba(0,255,255,0.1)' }}>
          {(['login', 'signup'] as const).map(m => (
            <button key={m} onClick={() => { setMode(m); setError(''); setSuccess(''); }}
              className="flex-1 py-2.5 text-sm font-bold font-mono transition-all"
              style={{
                background: mode === m ? 'rgba(0,255,255,0.1)' : 'transparent',
                color: mode === m ? '#0ff' : '#405070',
                borderBottom: mode === m ? '2px solid #0ff' : '2px solid transparent',
              }}>
              {m === 'login' ? t('login') : t('signup')}
            </button>
          ))}
        </div>

        <form onSubmit={handleSubmit} className="flex flex-col gap-3">
          {mode === 'signup' && (
            <div>
              <label className="text-[10px] font-mono text-[#6080aa] uppercase tracking-wider mb-1 block">{t('pilot_name')}</label>
              <input type="text" value={username} onChange={e => setUsername(e.target.value)}
                placeholder={t('pilot_name_placeholder')}
                className="w-full px-3 py-2.5 rounded-lg font-mono text-sm text-[#e0e8ff] placeholder-[#304060] outline-none transition-all focus:ring-1"
                style={{ background: 'rgba(0,10,30,0.8)', border: '1px solid rgba(0,255,255,0.1)' }}
                required minLength={2} maxLength={20} />
            </div>
          )}

          <div>
            <label className="text-[10px] font-mono text-[#6080aa] uppercase tracking-wider mb-1 block">{t('email')}</label>
            <input type="email" value={email} onChange={e => setEmail(e.target.value)}
              placeholder={t('email_placeholder')}
              className="w-full px-3 py-2.5 rounded-lg font-mono text-sm text-[#e0e8ff] placeholder-[#304060] outline-none"
              style={{ background: 'rgba(0,10,30,0.8)', border: '1px solid rgba(0,255,255,0.1)' }}
              required />
          </div>

          <div>
            <label className="text-[10px] font-mono text-[#6080aa] uppercase tracking-wider mb-1 block">{t('password')}</label>
            <input type="password" value={password} onChange={e => setPassword(e.target.value)}
              placeholder="••••••••"
              className="w-full px-3 py-2.5 rounded-lg font-mono text-sm text-[#e0e8ff] placeholder-[#304060] outline-none"
              style={{ background: 'rgba(0,10,30,0.8)', border: '1px solid rgba(0,255,255,0.1)' }}
              required minLength={6} />
          </div>

          {error && (
            <div className="text-xs font-mono px-3 py-2 rounded-lg" style={{ background: 'rgba(255,64,96,0.1)', color: '#ff4060', border: '1px solid rgba(255,64,96,0.2)' }}>
              ⚠️ {error}
            </div>
          )}

          {success && (
            <div className="text-xs font-mono px-3 py-2 rounded-lg" style={{ background: 'rgba(0,255,100,0.1)', color: '#00ff64', border: '1px solid rgba(0,255,100,0.2)' }}>
              ✅ {success}
            </div>
          )}

          <button type="submit" disabled={loading}
            className="mt-2 py-3 px-6 text-base font-bold rounded-lg text-white font-mono transition-all duration-200 hover:scale-105 active:scale-95 disabled:opacity-50"
            style={{
              background: 'linear-gradient(135deg, rgba(0,229,255,0.25), rgba(191,90,242,0.25))',
              border: '1px solid #0ff',
              boxShadow: '0 0 20px rgba(0,255,255,0.2), inset 0 0 15px rgba(0,255,255,0.08)',
            }}>
            {loading ? t('processing') : mode === 'login' ? t('login_btn') : t('signup_btn')}
          </button>
        </form>
      </div>

      <div className="mt-6 text-xs text-[#203050] font-mono">{t('cloud_save')}</div>
    </div>
  );
};

export default AuthScreen;
