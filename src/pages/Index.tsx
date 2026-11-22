import React, { useState, useCallback } from 'react';
import { ShipType, GameScreen } from '../game/types';
import type { MapDifficulty } from '../game/maps';
import { loadMeta, saveMeta, MetaProgress, ALL_MILESTONES } from '../game/meta';
import MainMenu from '../components/game/MainMenu';
import ClassSelect from '../components/game/ClassSelect';
import HowToPlay from '../components/game/HowToPlay';
import Leaderboard from '../components/game/Leaderboard';
import GameCanvas from '../components/game/GameCanvas';
import MapSelect from '../components/game/MapSelect';
import PlasmaShop from '../components/game/PlasmaShop';
import Achievements from '../components/game/Achievements';

const Index = () => {
  const [screen, setScreen] = useState<GameScreen>('menu');
  const [playerClass, setPlayerClass] = useState<ShipType>('phantom');
  const [mapId, setMapId] = useState<string>('neon-grid');
  const [mapDifficulty, setMapDifficulty] = useState<MapDifficulty>('medium');
  const [gameKey, setGameKey] = useState(0);
  const [meta, setMeta] = useState<MetaProgress>(loadMeta());

  // Progresso salvo só no aparelho (localStorage); sem conta nem nuvem.
  const updateMeta = useCallback((newMeta: MetaProgress) => {
    saveMeta(newMeta);
    setMeta(newMeta);
  }, []);

  const refreshMeta = () => { setMeta(loadMeta()); };

  const handleClassSelect = (cls: ShipType) => { setPlayerClass(cls); setScreen('map-select'); };
  const handleMapSelect = (id: string, difficulty: MapDifficulty) => {
    setMapId(id); setMapDifficulty(difficulty); setGameKey(k => k + 1); setScreen('playing');
  };
  const handleMenu = () => { refreshMeta(); setScreen('menu'); };

  if (screen === 'menu') {
    return (
      <MainMenu
        plasma={meta.plasma} stats={meta.stats}
        milestones={ALL_MILESTONES.filter(m => meta.milestones[m.id])}
        onPlay={() => setScreen('class-select')}
        onLeaderboard={() => setScreen('leaderboard')}
        onHowToPlay={() => setScreen('how-to-play')}
        onShop={() => setScreen('shop')}
        onAchievements={() => setScreen('achievements')}
      />
    );
  }

  if (screen === 'achievements') {
    return <Achievements unlocked={meta.milestones} onBack={() => setScreen('menu')} />;
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

  return <GameCanvas key={gameKey} playerClass={playerClass} mapId={mapId} mapDifficulty={mapDifficulty} onMenu={handleMenu} />;
};

export default Index;
