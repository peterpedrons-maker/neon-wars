import React, { useState } from 'react';
import { ShipType, GameScreen } from '../game/types';
import type { MapDifficulty } from '../game/maps';
import { loadMeta, MetaProgress, ALL_MILESTONES } from '../game/meta';
import { RoomInfo } from '../game/multiplayer';
import MainMenu from '../components/game/MainMenu';
import ClassSelect from '../components/game/ClassSelect';
import HowToPlay from '../components/game/HowToPlay';
import Leaderboard from '../components/game/Leaderboard';
import GameCanvas from '../components/game/GameCanvas';
import MapSelect from '../components/game/MapSelect';
import PlasmaShop from '../components/game/PlasmaShop';
import MultiplayerLobby from '../components/game/MultiplayerLobby';
import CoopGameCanvas from '../components/game/CoopGameCanvas';

const Index = () => {
  const [screen, setScreen] = useState<GameScreen>('menu');
  const [playerClass, setPlayerClass] = useState<ShipType>('phantom');
  const [mapId, setMapId] = useState<string>('neon-grid');
  const [mapDifficulty, setMapDifficulty] = useState<MapDifficulty>('medium');
  const [gameKey, setGameKey] = useState(0);
  const [meta, setMeta] = useState<MetaProgress>(loadMeta());

  // Coop state
  const [coopRoom, setCoopRoom] = useState<RoomInfo | null>(null);
  const [peerClass, setPeerClass] = useState<ShipType>('interceptor');

  const refreshMeta = () => setMeta(loadMeta());

  const handleClassSelect = (cls: ShipType) => {
    setPlayerClass(cls);
    setScreen('map-select');
  };

  const handleMapSelect = (id: string, difficulty: MapDifficulty) => {
    setMapId(id);
    setMapDifficulty(difficulty);
    setGameKey(k => k + 1);
    setScreen('playing');
  };

  const handleMenu = () => {
    refreshMeta();
    setScreen('menu');
  };

  const handleStartCoop = (
    room: RoomInfo,
    mId: string,
    difficulty: MapDifficulty,
    myClass: ShipType,
    theirClass: ShipType,
  ) => {
    setCoopRoom(room);
    setMapId(mId);
    setMapDifficulty(difficulty);
    setPlayerClass(myClass);
    setPeerClass(theirClass);
    setGameKey(k => k + 1);
    setScreen('playing');
  };

  if (screen === 'menu') {
    return (
      <MainMenu
        plasma={meta.plasma}
        stats={meta.stats}
        milestones={ALL_MILESTONES.filter(m => meta.milestones[m.id])}
        onPlay={() => { setCoopRoom(null); setScreen('class-select'); }}
        onLeaderboard={() => setScreen('leaderboard')}
        onHowToPlay={() => setScreen('how-to-play')}
        onShop={() => setScreen('shop')}
        onMultiplayer={() => setScreen('multiplayer-lobby')}
      />
    );
  }

  if (screen === 'multiplayer-lobby') {
    return (
      <MultiplayerLobby
        unlockedShips={meta.unlockedShips}
        onStartCoop={handleStartCoop}
        onBack={() => setScreen('menu')}
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
    return <ClassSelect onSelect={handleClassSelect} onBack={() => setScreen('menu')} unlockedShips={meta.unlockedShips || ['phantom', 'interceptor', 'titan', 'spectre']} />;
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

  // Coop mode
  if (coopRoom) {
    return (
      <CoopGameCanvas
        key={gameKey}
        playerClass={playerClass}
        peerClass={peerClass}
        mapId={mapId}
        mapDifficulty={mapDifficulty}
        room={coopRoom}
        onMenu={handleMenu}
      />
    );
  }

  return (
    <GameCanvas
      key={gameKey}
      playerClass={playerClass}
      mapId={mapId}
      mapDifficulty={mapDifficulty}
      onMenu={handleMenu}
    />
  );
};

export default Index;
