import React, { useState } from 'react';
import { PlayerClass, GameScreen } from '../game/types';
import MainMenu from '../components/game/MainMenu';
import ClassSelect from '../components/game/ClassSelect';
import HowToPlay from '../components/game/HowToPlay';
import Leaderboard from '../components/game/Leaderboard';
import GameCanvas from '../components/game/GameCanvas';

const Index = () => {
  const [screen, setScreen] = useState<GameScreen>('menu');
  const [playerClass, setPlayerClass] = useState<PlayerClass>('mage');
  const [gameKey, setGameKey] = useState(0);

  const handleClassSelect = (cls: PlayerClass) => {
    setPlayerClass(cls);
    setGameKey(k => k + 1);
    setScreen('playing');
  };

  if (screen === 'menu') {
    return (
      <MainMenu
        onPlay={() => setScreen('class-select')}
        onLeaderboard={() => setScreen('leaderboard')}
        onHowToPlay={() => setScreen('how-to-play')}
      />
    );
  }

  if (screen === 'class-select') {
    return <ClassSelect onSelect={handleClassSelect} onBack={() => setScreen('menu')} />;
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
      onMenu={() => setScreen('menu')}
    />
  );
};

export default Index;
