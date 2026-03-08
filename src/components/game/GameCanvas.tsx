import React, { useRef, useEffect, useCallback, useState } from 'react';
import { GameState, InputState, ShipType } from '../../game/types';
import { Ability } from '../../game/abilities';
import { createPlayer } from '../../game/entities';
import { createInitialState, updateGame, startWave } from '../../game/engine';
import { renderGame, getScale, getOffset, resetCamera } from '../../game/renderer';
import { ARENA_W, ARENA_H } from '../../game/constants';
import { useIsMobile } from '../../hooks/use-mobile';
import { loadMeta, saveMeta, endRun, MetaProgress } from '../../game/meta';
import HUD from './HUD';
import LevelUpScreen from './LevelUpScreen';
import GameOver from './GameOver';
import TouchControls from './TouchControls';

interface GameCanvasProps {
  playerClass: ShipType;
  mapId: string;
  onMenu: () => void;
}

const GameCanvas: React.FC<GameCanvasProps> = ({ playerClass, mapId, onMenu }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const stateRef = useRef<GameState | null>(null);
  const inputRef = useRef<InputState>({ moveX: 0, moveY: 0, aimX: 1, aimY: 0, shooting: false, special: false });
  const keysRef = useRef<Set<string>>(new Set());
  const frameRef = useRef<number>(0);
  const lastTimeRef = useRef<number>(0);
  const metaRef = useRef<MetaProgress>(loadMeta());
  const isMobile = useIsMobile();
  const [, forceUpdate] = React.useState(0);
  const [runResult, setRunResult] = useState<{ plasma: number; newMilestones: any[] } | null>(null);

  // Init game state
  useEffect(() => {
    const meta = loadMeta();
    metaRef.current = meta;
    const player = createPlayer(playerClass);
    stateRef.current = createInitialState(player, mapId, meta.weaponSlots);
    startWave(stateRef.current);
    setRunResult(null);
    forceUpdate(n => n + 1);
  }, [playerClass, mapId]);

  // Keyboard input
  useEffect(() => {
    const onKeyDown = (e: KeyboardEvent) => {
      keysRef.current.add(e.key.toLowerCase());
      if (e.key === ' ') { e.preventDefault(); inputRef.current.special = true; }
    };
    const onKeyUp = (e: KeyboardEvent) => {
      keysRef.current.delete(e.key.toLowerCase());
      if (e.key === ' ') inputRef.current.special = false;
    };
    window.addEventListener('keydown', onKeyDown);
    window.addEventListener('keyup', onKeyUp);
    return () => { window.removeEventListener('keydown', onKeyDown); window.removeEventListener('keyup', onKeyUp); };
  }, []);

  // Mouse input
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const onMouseMove = (e: MouseEvent) => {
      const rect = canvas.getBoundingClientRect();
      const scale = getScale(canvas.width, canvas.height);
      const offset = getOffset(canvas.width, canvas.height);
      const mx = (e.clientX - rect.left) * (canvas.width / rect.width);
      const my = (e.clientY - rect.top) * (canvas.height / rect.height);
      const worldX = (mx - offset.x) / scale;
      const worldY = (my - offset.y) / scale;
      if (stateRef.current) {
        const p = stateRef.current.player;
        inputRef.current.aimX = worldX - p.pos.x;
        inputRef.current.aimY = worldY - p.pos.y;
      }
    };
    const onMouseDown = (e: MouseEvent) => {
      if (e.button === 0) inputRef.current.shooting = true;
      if (e.button === 2) { e.preventDefault(); inputRef.current.special = true; }
    };
    const onMouseUp = (e: MouseEvent) => {
      if (e.button === 0) inputRef.current.shooting = false;
      if (e.button === 2) inputRef.current.special = false;
    };
    const onContext = (e: MouseEvent) => e.preventDefault();
    canvas.addEventListener('mousemove', onMouseMove);
    canvas.addEventListener('mousedown', onMouseDown);
    canvas.addEventListener('mouseup', onMouseUp);
    canvas.addEventListener('contextmenu', onContext);
    return () => {
      canvas.removeEventListener('mousemove', onMouseMove);
      canvas.removeEventListener('mousedown', onMouseDown);
      canvas.removeEventListener('mouseup', onMouseUp);
      canvas.removeEventListener('contextmenu', onContext);
    };
  }, []);

  // Resize canvas
  useEffect(() => {
    const resize = () => {
      const canvas = canvasRef.current;
      if (!canvas) return;
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    resize();
    window.addEventListener('resize', resize);
    return () => window.removeEventListener('resize', resize);
  }, []);

  // Game loop
  useEffect(() => {
    let endRunHandled = false;
    const loop = (time: number) => {
      frameRef.current = requestAnimationFrame(loop);
      if (!stateRef.current) return;
      const dt = lastTimeRef.current ? Math.min((time - lastTimeRef.current) / 1000, 0.05) : 0.016;
      lastTimeRef.current = time;

      const keys = keysRef.current;
      let mx = 0, my = 0;
      if (keys.has('w') || keys.has('arrowup')) my -= 1;
      if (keys.has('s') || keys.has('arrowdown')) my += 1;
      if (keys.has('a') || keys.has('arrowleft')) mx -= 1;
      if (keys.has('d') || keys.has('arrowright')) mx += 1;
      const len = Math.hypot(mx, my);
      if (len > 0 && !isMobile) {
        inputRef.current.moveX = mx / len;
        inputRef.current.moveY = my / len;
      } else if (!isMobile && len === 0) {
        inputRef.current.moveX = 0;
        inputRef.current.moveY = 0;
      }

      const prevScreen = stateRef.current.screen;
      updateGame(stateRef.current, inputRef.current, dt);

      if (stateRef.current.screen !== prevScreen) {
        forceUpdate(n => n + 1);
        // Handle end of run
        if (stateRef.current.screen === 'game-over' && !endRunHandled) {
          endRunHandled = true;
          const s = stateRef.current;
          const result = endRun(
            metaRef.current, s.score, s.wave, s.enemiesKilled,
            s.bossesKilled, s.maxCombo, playerClass
          );
          setRunResult(result);
        }
      }

      const canvas = canvasRef.current;
      if (!canvas) return;
      const ctx = canvas.getContext('2d');
      if (!ctx) return;
      renderGame(ctx, stateRef.current, canvas.width, canvas.height);
    };
    frameRef.current = requestAnimationFrame(loop);
    return () => cancelAnimationFrame(frameRef.current);
  }, [isMobile, playerClass]);

  const handleUpgrade = useCallback((ability: Ability) => {
    if (!stateRef.current) return;
    ability.apply(stateRef.current);
    stateRef.current.abilityLevels[ability.id] = (stateRef.current.abilityLevels[ability.id] || 0) + 1;
    // Track weapon slots
    if (ability.category === 'weapon' && !stateRef.current.equippedWeapons.includes(ability.id)) {
      stateRef.current.equippedWeapons.push(ability.id);
    }
    stateRef.current.screen = 'playing';
    forceUpdate(n => n + 1);
  }, []);

  const handleTouchInput = useCallback((partial: Partial<InputState>) => {
    Object.assign(inputRef.current, partial);
  }, []);

  const handleTouchSpecial = useCallback(() => {
    inputRef.current.special = true;
    setTimeout(() => { inputRef.current.special = false; }, 100);
  }, []);

  const handleRestart = useCallback(() => {
    resetCamera();
    const meta = loadMeta();
    metaRef.current = meta;
    const player = createPlayer(playerClass);
    stateRef.current = createInitialState(player, mapId, meta.weaponSlots);
    startWave(stateRef.current);
    setRunResult(null);
    forceUpdate(n => n + 1);
  }, [playerClass, mapId]);

  const state = stateRef.current;

  return (
    <div className="relative w-screen h-screen overflow-hidden bg-[#08061a]">
      <canvas ref={canvasRef} className="block w-full h-full" />

      {state && state.screen === 'playing' && (
        <HUD
          player={state.player}
          wave={state.wave}
          score={state.score}
          specialReady={state.player.specialTimer <= 0}
          combo={state.combo}
          comboMultiplier={state.comboMultiplier}
          comboTimer={state.comboTimer}
          level={state.level}
          xp={state.xp}
          xpToNext={state.xpToNext}
          equippedWeapons={state.equippedWeapons}
          weaponSlots={state.weaponSlots}
          abilityLevels={state.abilityLevels}
        />
      )}

      {state && state.screen === 'upgrade' && (
        <LevelUpScreen
          level={state.level}
          abilityLevels={state.abilityLevels}
          equippedWeapons={state.equippedWeapons}
          weaponSlots={state.weaponSlots}
          unlockedAbilities={metaRef.current.unlockedAbilities}
          onSelect={handleUpgrade}
        />
      )}

      {state && state.screen === 'game-over' && (
        <GameOver
          score={state.score}
          wave={state.wave}
          enemiesKilled={state.enemiesKilled}
          playerClass={playerClass}
          plasmaEarned={runResult?.plasma ?? 0}
          newMilestones={runResult?.newMilestones ?? []}
          onRestart={handleRestart}
          onMenu={onMenu}
        />
      )}

      {isMobile && state && state.screen === 'playing' && (
        <TouchControls onInput={handleTouchInput} onSpecial={handleTouchSpecial} />
      )}
    </div>
  );
};

export default GameCanvas;
