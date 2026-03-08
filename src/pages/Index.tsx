import React, { useState } from 'react';
import { ShipType, GameScreen } from '../game/types';
import { loadMeta, saveMeta, MetaProgress, ALL_MILESTONES } from '../game/meta';
import { ALL_MAPS } from '../game/maps';
import MainMenu from '../components/game/MainMenu';
import ClassSelect from '../components/game/ClassSelect';
import HowToPlay from '../components/game/HowToPlay';
import Leaderboard from '../components/game/Leaderboard';
import GameCanvas from '../components/game/GameCanvas';
import MapSelect from '../components/game/MapSelect';
import PlasmaShop from '../components/game/PlasmaShop';

const Index = () => {
  const [screen, setScreen] = useState<GameScreen>('menu');
  const [playerClass, setPlayerClass] = useState<ShipType>('phantom');
  const [mapId, setMapId] = useState<string>('neon-grid');
  const [gameKey, setGameKey] = useState(0);
  const [meta, setMeta] = useState<MetaProgress>(loadMeta());

  const refreshMeta = () => setMeta(loadMeta());

  const handleClassSelect = (cls: ShipType) => {
    setPlayerClass(cls);
    setScreen('map-select');
  };

  const handleMapSelect = (id: string) => {
    setMapId(id);
    setGameKey(k => k + 1);
    setScreen('playing');
  };

  const handleMenu = () => {
    refreshMeta();
    setScreen('menu');
  };

  if (screen === 'menu') {
    return (
      <MainMenu
        plasma={meta.plasma}
        stats={meta.stats}
        milestones={ALL_MILESTONES.filter(m => meta.milestones[m.id])}
        onPlay={() => setScreen('class-select')}
        onLeaderboard={() => setScreen('leaderboard')}
        onHowToPlay={() => setScreen('how-to-play')}
        onShop={() => setScreen('shop')}
      />
    );
  }

  if (screen === 'shop') {
    return (
      <PlasmaShop
        meta={meta}
        onUpdate={(m) => setMeta(m)}
        onBack={() => setScreen('menu')}
      />
    );
  }

  if (screen === 'class-select') {
    return <ClassSelect onSelect={handleClassSelect} onBack={() => setScreen('menu')} />;
  }

  if (screen === 'map-select') {
    return (
      <MapSelect
        unlockedMaps={meta.unlockedMaps}
        onSelect={handleMapSelect}
        onBack={() => setScreen('class-select')}
      />
    );
  }

  if (screen === 'how-to-play') {
    return <HowToPlay onBack={() => setScreen('menu')} />;
  }

  if (screen === 'leaderboard') {
    return <Leaderboard onBack={() => setScreen('menu')} />;
  }

  return (
    <GameCanvas
      key={gameKey}
      playerClass={playerClass}
      mapId={mapId}
      onMenu={handleMenu}
    />
  );
};

export default Index;
