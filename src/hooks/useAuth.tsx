import { useState, useEffect, useCallback, createContext, useContext, ReactNode } from 'react';
import { supabase } from '@/integrations/supabase/client';
import type { User, Session } from '@supabase/supabase-js';
import { MetaProgress } from '@/game/meta';

interface AuthContextType {
  user: User | null;
  session: Session | null;
  loading: boolean;
  username: string;
  signUp: (email: string, password: string, username: string) => Promise<{ error: string | null }>;
  signIn: (email: string, password: string) => Promise<{ error: string | null }>;
  signOut: () => Promise<void>;
  saveProgress: (meta: MetaProgress) => Promise<void>;
  loadProgress: () => Promise<MetaProgress | null>;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(true);
  const [username, setUsername] = useState('Piloto');

  useEffect(() => {
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session);
      setUser(session?.user ?? null);
      if (session?.user) {
        setTimeout(() => {
          supabase.from('profiles').select('username').eq('id', session.user.id).single()
            .then(({ data }) => { if (data?.username) setUsername(data.username); });
        }, 0);
      }
      setLoading(false);
    });

    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
      setUser(session?.user ?? null);
      if (session?.user) {
        supabase.from('profiles').select('username').eq('id', session.user.id).single()
          .then(({ data }) => { if (data?.username) setUsername(data.username); });
      }
      setLoading(false);
    });

    return () => subscription.unsubscribe();
  }, []);

  const signUp = async (email: string, password: string, name: string) => {
    const { error } = await supabase.auth.signUp({
      email, password,
      options: { data: { username: name }, emailRedirectTo: window.location.origin }
    });
    return { error: error?.message ?? null };
  };

  const signIn = async (email: string, password: string) => {
    const { error } = await supabase.auth.signInWithPassword({ email, password });
    return { error: error?.message ?? null };
  };

  const signOut = async () => {
    await supabase.auth.signOut();
    setUser(null);
    setSession(null);
    setUsername('Piloto');
  };

  const saveProgress = useCallback(async (meta: MetaProgress) => {
    if (!user) return;
    const { data: existing } = await supabase.from('game_progress').select('id').eq('user_id', user.id).single();
    if (existing) {
      await supabase.from('game_progress').update({ progress: meta as any, updated_at: new Date().toISOString() }).eq('user_id', user.id);
    } else {
      await supabase.from('game_progress').insert({ user_id: user.id, progress: meta as any });
    }
  }, [user]);

  const loadProgress = useCallback(async (): Promise<MetaProgress | null> => {
    if (!user) return null;
    const { data } = await supabase.from('game_progress').select('progress').eq('user_id', user.id).single();
    return data?.progress as unknown as MetaProgress | null;
  }, [user]);

  return (
    <AuthContext.Provider value={{ user, session, loading, username, signUp, signIn, signOut, saveProgress, loadProgress }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
