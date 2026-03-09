import React, { useState, useEffect, useCallback } from 'react';
import { ShipType, GameScreen } from '../game/types';
import type { MapDifficulty } from '../game/maps';
import { loadMeta, saveMeta, MetaProgress, ALL_MILESTONES } from '../game/meta';
import { RoomInfo } from '../game/multiplayer';
import { useAuth } from '../hooks/useAuth';
import AuthScreen from '../components/game/AuthScreen';
import MainMenu from '../components/game/MainMenu';
import ClassSelect from '../components/game/ClassSelect';
import HowToPlay from '../components/game/HowToPlay';
import Leaderboard from '../components/game/Leaderboard';
import GameCanvas from '../components/game/GameCanvas';
import MapSelect from '../components/game/MapSelect';
import PlasmaShop from '../components/game/PlasmaShop';
import MultiplayerLobby from '../components/game/MultiplayerLobby';
import CoopGameCanvas from '../components/game/CoopGameCanvas';
import Achievements from '../components/game/Achievements';

const Index = () => {
  const { user, loading, username, signUp, signIn, signOut, saveProgress, loadProgress } = useAuth();
  const [screen, setScreen] = useState<GameScreen>('menu');
  const [playerClass, setPlayerClass] = useState<ShipType>('phantom');
  const [mapId, setMapId] = useState<string>('neon-grid');
  const [mapDifficulty, setMapDifficulty] = useState<MapDifficulty>('medium');
  const [gameKey, setGameKey] = useState(0);
  const [meta, setMeta] = useState<MetaProgress>(loadMeta());
  const [coopRoom, setCoopRoom] = useState<RoomInfo | null>(null);
  const [peerClass, setPeerClass] = useState<ShipType>('interceptor');
  const [synced, setSynced] = useState(false);

  // Load progress from cloud on login
  useEffect(() => {
    if (user && !synced) {
      loadProgress().then(cloudMeta => {
        if (cloudMeta) {
          // Merge: take whichever has more progress
          const local = loadMeta();
          const merged = (cloudMeta.stats?.totalRuns || 0) >= (local.stats?.totalRuns || 0) ? cloudMeta : local;
          // Ensure defaults
          const final: MetaProgress = {
            ...merged,
            unlockedShips: merged.unlockedShips || ['phantom', 'interceptor', 'titan'],
            unlockedMaps: merged.unlockedMaps || ['neon-grid'],
            unlockedAbilities: merged.unlockedAbilities || [],
            milestones: merged.milestones || {},
            achievements: merged.achievements || {},
            permBonuses: merged.permBonuses || {},
          };
          saveMeta(final);
          setMeta(final);
        }
        setSynced(true);
      });
    }
  }, [user, synced, loadProgress]);

  // Save to cloud whenever meta changes
  const updateMeta = useCallback((newMeta: MetaProgress) => {
    saveMeta(newMeta);
    setMeta(newMeta);
    if (user) saveProgress(newMeta);
  }, [user, saveProgress]);

  const refreshMeta = () => {
    const m = loadMeta();
    setMeta(m);
    if (user) saveProgress(m);
  };

  const handleAuth = async (mode: 'login' | 'signup', email: string, password: string, name?: string) => {
    if (mode === 'signup') {
      return signUp(email, password, name || 'Piloto');
    }
    return signIn(email, password);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen" style={{ background: '#000008' }}>
        <div className="text-[#0ff] font-mono text-xl animate-pulse">Carregando...</div>
      </div>
    );
  }

  if (!user) {
    return <AuthScreen onAuth={handleAuth} />;
  }

  const handleClassSelect = (cls: ShipType) => { setPlayerClass(cls); setScreen('map-select'); };
  const handleMapSelect = (id: string, difficulty: MapDifficulty) => {
    setMapId(id); setMapDifficulty(difficulty); setGameKey(k => k + 1); setScreen('playing');
  };
  const handleMenu = () => { refreshMeta(); setScreen('menu'); };

  const handleStartCoop = (room: RoomInfo, mId: string, difficulty: MapDifficulty, myClass: ShipType, theirClass: ShipType) => {
    setCoopRoom(room); setMapId(mId); setMapDifficulty(difficulty);
    setPlayerClass(myClass); setPeerClass(theirClass);
    setGameKey(k => k + 1); setScreen('playing');
  };

  if (screen === 'menu') {
    return (
      <MainMenu
        plasma={meta.plasma} stats={meta.stats}
        milestones={ALL_MILESTONES.filter(m => meta.milestones[m.id])}
        onPlay={() => { setCoopRoom(null); setScreen('class-select'); }}
        onLeaderboard={() => setScreen('leaderboard')}
        onHowToPlay={() => setScreen('how-to-play')}
        onShop={() => setScreen('shop')}
        onMultiplayer={() => setScreen('multiplayer-lobby')}
        onAchievements={() => setScreen('achievements')}
        username={username}
        onLogout={signOut}
      />
    );
  }

  if (screen === 'achievements') {
    return <Achievements unlocked={meta.milestones} onBack={() => setScreen('menu')} />;
  }

  if (screen === 'multiplayer-lobby') {
    return <MultiplayerLobby unlockedShips={meta.unlockedShips} onStartCoop={handleStartCoop} onBack={() => setScreen('menu')} />;
  }

  if (screen === 'shop') {
    return <PlasmaShop meta={meta} onUpdate={updateMeta} onBack={() => setScreen('menu')} />;
  }

  if (screen === 'class-select') {
    return <ClassSelect onSelect={handleClassSelect} onBack={() => setScreen('menu')} unlockedShips={meta.unlockedShips || ['phantom', 'interceptor', 'titan']} />;
  }

  if (screen === 'map-select') {
    return <MapSelect unlockedMaps={meta.unlockedMaps} onSelect={handleMapSelect} onBack={() => setScreen('class-select')} />;
  }

  if (screen === 'how-to-play') return <HowToPlay onBack={() => setScreen('menu')} />;
  if (screen === 'leaderboard') return <Leaderboard onBack={() => setScreen('menu')} />;

  if (coopRoom) {
    return <CoopGameCanvas key={gameKey} playerClass={playerClass} peerClass={peerClass} mapId={mapId} mapDifficulty={mapDifficulty} room={coopRoom} onMenu={handleMenu} />;
  }

  return <GameCanvas key={gameKey} playerClass={playerClass} mapId={mapId} mapDifficulty={mapDifficulty} onMenu={handleMenu} />;
};

export default Index;
