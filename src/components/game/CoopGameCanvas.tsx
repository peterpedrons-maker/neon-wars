import React, { useRef, useEffect, useCallback, useState } from 'react';
import { GameState, InputState, ShipType } from '../../game/types';
import { Ability } from '../../game/abilities';
import { createPlayer } from '../../game/entities';
import { createInitialState, updateGame, startWave } from '../../game/engine';
import { renderGame, getScale, getOffset, resetCamera } from '../../game/renderer';
import { useIsMobile } from '../../hooks/use-mobile';
import { loadMeta, endRun, MetaProgress } from '../../game/meta';
import { RoomInfo, sendPlayerState, sendGameSync, CoopPlayerState, CoopGameSync, connectToRoom, leaveRoom, sendLevelUp, sendUpgradeDone } from '../../game/multiplayer';
import { CLASS_STATS } from '../../game/constants';
import HUD from './HUD';
import LevelUpScreen from './LevelUpScreen';
import GameOver from './GameOver';
import TouchControls from './TouchControls';

interface CoopGameCanvasProps {
  playerClass: ShipType;
  peerClass: ShipType;
  mapId: string;
  room: RoomInfo;
  onMenu: () => void;
}

const MAX_PARTICLES = 150; // Reduced for coop performance

const CoopGameCanvas: React.FC<CoopGameCanvasProps> = ({ playerClass, peerClass, mapId, room, onMenu }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const stateRef = useRef<GameState | null>(null);
  const inputRef = useRef<InputState>({ moveX: 0, moveY: 0, aimX: 1, aimY: 0, shooting: false, special: false });
  const keysRef = useRef<Set<string>>(new Set());
  const frameRef = useRef<number>(0);
  const lastTimeRef = useRef<number>(0);
  const metaRef = useRef<MetaProgress>(loadMeta());
  const isMobile = useIsMobile();
  const [, forceUpdate] = useState(0);
  const [runResult, setRunResult] = useState<{ plasma: number; newMilestones: any[] } | null>(null);

  // Upgrade sync state
  const [showUpgrade, setShowUpgrade] = useState(false);
  const [myUpgradeDone, setMyUpgradeDone] = useState(false);
  const [peerUpgradeDone, setPeerUpgradeDone] = useState(false);
  const [waitingForPeer, setWaitingForPeer] = useState(false);
  const upgradeResumeRef = useRef(false);

  // Peer state
  const peerStateRef = useRef<CoopPlayerState>({ x: 0, y: 0, angle: 0, hp: 3, maxHp: 3, alive: true, shipClass: peerClass, shieldTimer: 0, invincibleTimer: 0, shooting: false });
  const syncTimerRef = useRef(0);

  // Init game state
  useEffect(() => {
    const meta = loadMeta();
    metaRef.current = meta;
    const player = createPlayer(playerClass);
    stateRef.current = createInitialState(player, mapId, meta.weaponSlots);
    startWave(stateRef.current);
    setRunResult(null);
    setShowUpgrade(false);
    setMyUpgradeDone(false);
    setPeerUpgradeDone(false);
    setWaitingForPeer(false);
    forceUpdate(n => n + 1);

    const ch = connectToRoom(room, {
      onPeerJoin: () => {},
      onPeerLeave: () => {},
      onPeerState: (ps) => {
        peerStateRef.current = ps;
        if (stateRef.current) {
          const peerStats = CLASS_STATS[ps.shipClass as ShipType] || CLASS_STATS.phantom;
          stateRef.current.coopPeer = {
            pos: { x: ps.x, y: ps.y },
            angle: ps.angle,
            alive: ps.alive,
            shipClass: ps.shipClass,
            shooting: ps.shooting,
            attackTimer: stateRef.current.coopPeer?.attackTimer ?? 0,
            attackCooldown: peerStats.attackCooldown,
            damage: peerStats.damage,
          };
        }
      },
      onGameSync: (sync) => {
        if (!room.isHost && stateRef.current) {
          stateRef.current.wave = sync.wave;
          stateRef.current.score = sync.score;
          stateRef.current.xp = sync.xp;
          stateRef.current.level = sync.level;
          stateRef.current.xpToNext = sync.xpToNext;
          stateRef.current.enemies = sync.enemies.map(e => ({
            pos: { x: e.x, y: e.y }, vel: { x: 0, y: 0 }, radius: e.radius, alive: e.alive,
            type: e.type as any, hp: e.hp, maxHp: e.maxHp, damage: 10, speed: 0, score: 0,
            attackTimer: 0, attackCooldown: 1, isBoss: e.radius >= 25, flashTimer: 0,
          }));
          stateRef.current.projectiles = sync.projectiles.map(p => ({
            pos: { x: p.x, y: p.y }, vel: { x: p.vx, y: p.vy }, radius: 4, alive: p.alive,
            damage: 10, fromPlayer: p.fromPlayer, lifetime: 2, color: p.color,
          }));
        }
      },
      onStartGame: () => {},
      onCountdown: () => {},
      onConfirm: () => {},
      onLobbyState: () => {},
      onChat: () => {},
      onLevelUp: (_level: number) => {
        // Peer leveled up - show upgrade screen for us too
        if (stateRef.current && stateRef.current.screen === 'playing') {
          setShowUpgrade(true);
          setMyUpgradeDone(false);
          setPeerUpgradeDone(false);
          setWaitingForPeer(false);
          stateRef.current.screen = 'upgrade';
        }
      },
      onUpgradeDone: () => {
        setPeerUpgradeDone(true);
      },
    });

    return () => { leaveRoom(); };
  }, [playerClass, mapId]);

  // When both players have chosen upgrades, resume game
  useEffect(() => {
    if (myUpgradeDone && peerUpgradeDone && showUpgrade) {
      setShowUpgrade(false);
      setWaitingForPeer(false);
      if (stateRef.current) {
        stateRef.current.screen = 'playing';
      }
      forceUpdate(n => n + 1);
    }
  }, [myUpgradeDone, peerUpgradeDone, showUpgrade]);

  // Keyboard
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

  // Mouse
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

  // Resize
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
    let prevLevel = 0;
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

      prevLevel = stateRef.current.level;
      const prevScreen = stateRef.current.screen;

      // Guest: skip enemy spawning/AI (host syncs enemies)
      if (!room.isHost) {
        stateRef.current.waveEnemiesRemaining = 0;
      }
      updateGame(stateRef.current, inputRef.current, dt);

      // Cap particles for performance
      if (stateRef.current.particles.length > MAX_PARTICLES) {
        stateRef.current.particles = stateRef.current.particles.slice(-MAX_PARTICLES);
      }

      forceUpdate(n => n + 1);

      // Detect level up -> broadcast and show upgrade for both
      if (stateRef.current.screen === 'upgrade' && prevScreen === 'playing') {
        sendLevelUp(stateRef.current.level);
        setShowUpgrade(true);
        setMyUpgradeDone(false);
        setPeerUpgradeDone(false);
        setWaitingForPeer(false);
      }

      // Send our state to peer
      syncTimerRef.current -= dt;
      if (syncTimerRef.current <= 0) {
        syncTimerRef.current = 0.05;
        const p = stateRef.current.player;
        sendPlayerState({
          x: p.pos.x, y: p.pos.y, angle: p.angle,
          hp: p.hp, maxHp: p.maxHp, alive: p.alive,
          shipClass: playerClass, shieldTimer: p.shieldTimer,
          invincibleTimer: p.invincibleTimer, shooting: inputRef.current.shooting,
        });

        // Host sends game sync
        if (room.isHost) {
          sendGameSync({
            enemies: stateRef.current.enemies.filter(e => e.alive).map(e => ({
              x: e.pos.x, y: e.pos.y, type: e.type, hp: e.hp, maxHp: e.maxHp, radius: e.radius, alive: e.alive,
            })),
            projectiles: stateRef.current.projectiles.filter(p => p.alive).slice(0, 50).map(p => ({
              x: p.pos.x, y: p.pos.y, vx: p.vel.x, vy: p.vel.y, fromPlayer: p.fromPlayer, color: p.color, alive: p.alive,
            })),
            wave: stateRef.current.wave,
            score: stateRef.current.score,
            xp: stateRef.current.xp,
            level: stateRef.current.level,
            xpToNext: stateRef.current.xpToNext,
            hostPlayer: {
              x: stateRef.current.player.pos.x, y: stateRef.current.player.pos.y,
              angle: stateRef.current.player.angle, hp: stateRef.current.player.hp,
              maxHp: stateRef.current.player.maxHp, alive: stateRef.current.player.alive,
              shipClass: playerClass, shieldTimer: stateRef.current.player.shieldTimer,
              invincibleTimer: stateRef.current.player.invincibleTimer, shooting: inputRef.current.shooting,
            },
          });
        }
      }

      if (stateRef.current.screen !== prevScreen) {
        if (stateRef.current.screen === 'game-over' && !endRunHandled) {
          endRunHandled = true;
          const s = stateRef.current;
          const result = endRun(metaRef.current, s.score, s.wave, s.enemiesKilled, s.bossesKilled, s.maxCombo, playerClass);
          setRunResult(result);
        }
      }

      // Render
      const canvas = canvasRef.current;
      if (!canvas) return;
      const ctx = canvas.getContext('2d');
      if (!ctx) return;
      renderGame(ctx, stateRef.current, canvas.width, canvas.height);
    };
    frameRef.current = requestAnimationFrame(loop);
    return () => cancelAnimationFrame(frameRef.current);
  }, [isMobile, playerClass, room.isHost]);

  const handleUpgrade = useCallback((ability: Ability) => {
    if (!stateRef.current) return;
    ability.apply(stateRef.current);
    stateRef.current.abilityLevels[ability.id] = (stateRef.current.abilityLevels[ability.id] || 0) + 1;
    if (ability.category === 'weapon' && !stateRef.current.equippedWeapons.includes(ability.id)) {
      stateRef.current.equippedWeapons.push(ability.id);
    }
    setMyUpgradeDone(true);
    sendUpgradeDone();
    setWaitingForPeer(true);
    // Don't resume yet - wait for peer
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
    setShowUpgrade(false);
    setMyUpgradeDone(false);
    setPeerUpgradeDone(false);
    setWaitingForPeer(false);
    forceUpdate(n => n + 1);
  }, [playerClass, mapId]);

  const state = stateRef.current;

  return (
    <div className="relative w-screen h-screen overflow-hidden bg-[#08061a]">
      <canvas ref={canvasRef} className="block w-full h-full" />

      {/* Coop indicator */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 mt-1 px-3 py-0.5 rounded-full font-mono text-xs font-bold z-20"
        style={{ background: 'rgba(57,255,20,0.15)', border: '1px solid rgba(57,255,20,0.3)', color: '#39ff14' }}>
        🎮 COOP • {room.roomCode}
      </div>

      {state && state.screen === 'playing' && (
        <HUD
          player={state.player} wave={state.wave} score={state.score}
          specialReady={state.player.specialTimer <= 0}
          combo={state.combo} comboMultiplier={state.comboMultiplier} comboTimer={state.comboTimer}
          level={state.level} xp={state.xp} xpToNext={state.xpToNext}
          equippedWeapons={state.equippedWeapons} weaponSlots={state.weaponSlots}
          abilityLevels={state.abilityLevels}
        />
      )}

      {state && state.screen === 'upgrade' && showUpgrade && !myUpgradeDone && (
        <LevelUpScreen level={state.level} abilityLevels={state.abilityLevels}
          equippedWeapons={state.equippedWeapons} weaponSlots={state.weaponSlots}
          unlockedAbilities={metaRef.current.unlockedAbilities} onSelect={handleUpgrade}
        />
      )}

      {/* Waiting for peer to choose upgrade */}
      {state && state.screen === 'upgrade' && myUpgradeDone && !peerUpgradeDone && (
        <div className="absolute inset-0 flex flex-col items-center justify-center bg-black/80 z-20 select-none">
          <div className="text-2xl font-bold font-mono animate-pulse" style={{ color: '#39ff14', textShadow: '0 0 20px rgba(57,255,20,0.5)' }}>
            ⏳ Outro Jogador Selecionando Upgrade...
          </div>
          <p className="text-sm font-mono mt-2" style={{ color: '#6080aa' }}>Aguardando P2 escolher</p>
        </div>
      )}

      {state && state.screen === 'game-over' && (
        <GameOver score={state.score} wave={state.wave} enemiesKilled={state.enemiesKilled}
          playerClass={playerClass} plasmaEarned={runResult?.plasma ?? 0}
          newMilestones={runResult?.newMilestones ?? []} onRestart={handleRestart} onMenu={() => { leaveRoom(); onMenu(); }}
        />
      )}

      {isMobile && state && state.screen === 'playing' && (
        <TouchControls onInput={handleTouchInput} onSpecial={handleTouchSpecial} />
      )}
    </div>
  );
};

export default CoopGameCanvas;
