import React, { useState, useEffect, useRef } from 'react';
import { ShipType } from '../../game/types';
import { 
  RoomInfo, createRoom, joinRoom, connectToRoom, 
  leaveRoom, sendStartGame, CoopPlayerState, CoopGameSync 
} from '../../game/multiplayer';

interface MultiplayerLobbyProps {
  unlockedShips: string[];
  onStartCoop: (room: RoomInfo, mapId: string, playerClass: ShipType, peerClass: ShipType) => void;
  onBack: () => void;
}

const SHIP_INFO: Record<string, { name: string; icon: string; color: string }> = {
  phantom: { name: 'Phantom', icon: '👻', color: '#bf5af2' },
  interceptor: { name: 'Interceptor', icon: '⚡', color: '#00e5ff' },
  titan: { name: 'Titan', icon: '🛡️', color: '#ff6b00' },
  spectre: { name: 'Spectre', icon: '🌀', color: '#9040ff' },
  valkyrie: { name: 'Valkyrie', icon: '⚔️', color: '#ff1493' },
  juggernaut: { name: 'Juggernaut', icon: '💪', color: '#ff4500' },
};

const MAPS = [
  { id: 'neon-grid', name: 'Neon Grid', color: '#0ff' },
  { id: 'inferno', name: 'Inferno', color: '#ff6b00' },
  { id: 'void', name: 'Void', color: '#9040ff' },
  { id: 'crystal', name: 'Crystal', color: '#00e5ff' },
];

const MultiplayerLobby: React.FC<MultiplayerLobbyProps> = ({ unlockedShips, onStartCoop, onBack }) => {
  const [mode, setMode] = useState<'choose' | 'hosting' | 'joining'>('choose');
  const [room, setRoom] = useState<RoomInfo | null>(null);
  const [joinCode, setJoinCode] = useState('');
  const [peerConnected, setPeerConnected] = useState(false);
  const [selectedShip, setSelectedShip] = useState<ShipType>('phantom');
  const [selectedMap, setSelectedMap] = useState('neon-grid');
  const [peerShip, setPeerShip] = useState<ShipType>('interceptor');
  const [status, setStatus] = useState('');
  const channelRef = useRef<any>(null);

  useEffect(() => {
    return () => { leaveRoom(); };
  }, []);

  const handleCreate = () => {
    const newRoom = createRoom();
    setRoom(newRoom);
    setMode('hosting');
    setStatus('Aguardando jogador...');

    channelRef.current = connectToRoom(
      newRoom,
      () => { setPeerConnected(true); setStatus('Jogador conectado!'); },
      () => { setPeerConnected(false); setStatus('Jogador desconectou'); },
      (state: CoopPlayerState) => { setPeerShip(state.shipClass as ShipType); },
      () => {},
      () => {},
    );
  };

  const handleJoin = () => {
    if (joinCode.length < 3) return;
    const newRoom = joinRoom(joinCode);
    setRoom(newRoom);
    setMode('joining');
    setStatus('Conectando...');

    channelRef.current = connectToRoom(
      newRoom,
      () => { setPeerConnected(true); setStatus('Conectado ao host!'); },
      () => { setPeerConnected(false); setStatus('Host desconectou'); },
      (state: CoopPlayerState) => { setPeerShip(state.shipClass as ShipType); },
      () => {},
      (data) => {
        // Host started the game
        if (room) {
          onStartCoop(newRoom, data.mapId, selectedShip, data.hostClass as ShipType);
        }
      },
    );
  };

  const handleStart = () => {
    if (!room || !peerConnected) return;
    sendStartGame(selectedMap, selectedShip);
    onStartCoop(room, selectedMap, selectedShip, peerShip);
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-[#000008] text-[#e0e8ff] select-none px-4">
      <h1 className="text-4xl md:text-5xl font-bold mb-2 font-mono"
        style={{ textShadow: '0 0 30px rgba(0,255,255,0.4)', color: '#0ff' }}>
        🎮 Multiplayer Coop
      </h1>
      <p className="text-[#6080aa] font-mono mb-8">Jogue com um amigo online!</p>

      {mode === 'choose' && (
        <div className="flex flex-col gap-4 w-72">
          <button onClick={handleCreate}
            className="py-4 px-8 text-lg font-bold rounded-lg text-white border transition-all hover:scale-105 font-mono"
            style={{ background: 'linear-gradient(135deg, rgba(0,229,255,0.2), rgba(191,90,242,0.2))', borderColor: '#0ff', boxShadow: '0 0 20px rgba(0,255,255,0.3)' }}>
            🏠 Criar Sala
          </button>
          <div className="flex gap-2">
            <input
              value={joinCode}
              onChange={e => setJoinCode(e.target.value.toUpperCase())}
              placeholder="CÓDIGO"
              maxLength={5}
              className="flex-1 py-3 px-4 text-lg font-bold rounded-lg text-center font-mono bg-transparent border"
              style={{ borderColor: '#bf5af2', color: '#bf5af2' }}
            />
            <button onClick={handleJoin}
              className="py-3 px-6 text-lg font-bold rounded-lg text-[#bf5af2] border border-[#bf5af2]/50 transition-all hover:border-[#bf5af2] font-mono"
              style={{ background: 'rgba(191,90,242,0.1)' }}>
              Entrar
            </button>
          </div>
          <button onClick={onBack}
            className="py-3 px-8 text-lg font-bold rounded-lg text-[#6080aa] border border-[#6080aa]/30 transition-all hover:border-[#0ff] hover:text-[#0ff] font-mono mt-4"
            style={{ background: 'rgba(0,255,255,0.03)' }}>
            ← Voltar
          </button>
        </div>
      )}

      {(mode === 'hosting' || mode === 'joining') && (
        <div className="flex flex-col items-center gap-4 w-full max-w-md">
          {/* Room code */}
          {room && (
            <div className="text-center mb-2">
              <div className="text-xs font-mono text-[#6080aa] mb-1">CÓDIGO DA SALA</div>
              <div className="text-4xl font-black font-mono tracking-[0.3em] py-2 px-6 rounded-lg"
                style={{ color: '#0ff', background: 'rgba(0,255,255,0.08)', border: '2px solid rgba(0,255,255,0.3)', textShadow: '0 0 15px rgba(0,255,255,0.5)' }}>
                {room.roomCode}
              </div>
            </div>
          )}

          {/* Status */}
          <div className="flex items-center gap-2 py-2 px-4 rounded-full font-mono text-sm"
            style={{ background: peerConnected ? 'rgba(57,255,20,0.1)' : 'rgba(255,255,0,0.1)', border: `1px solid ${peerConnected ? 'rgba(57,255,20,0.3)' : 'rgba(255,255,0,0.3)'}`, color: peerConnected ? '#39ff14' : '#ffff00' }}>
            <span className="w-2 h-2 rounded-full" style={{ background: peerConnected ? '#39ff14' : '#ffff00', boxShadow: `0 0 6px ${peerConnected ? '#39ff14' : '#ffff00'}` }} />
            {status}
          </div>

          {/* Ship selection */}
          <div className="w-full mt-4">
            <div className="text-xs font-mono text-[#6080aa] mb-2 text-center">SUA NAVE</div>
            <div className="grid grid-cols-3 gap-2">
              {unlockedShips.map(id => {
                const info = SHIP_INFO[id];
                if (!info) return null;
                return (
                  <button key={id} onClick={() => setSelectedShip(id as ShipType)}
                    className="py-2 px-2 rounded-lg font-mono text-sm font-bold transition-all"
                    style={{
                      background: selectedShip === id ? `${info.color}22` : 'rgba(255,255,255,0.02)',
                      border: `2px solid ${selectedShip === id ? info.color : 'rgba(255,255,255,0.08)'}`,
                      color: selectedShip === id ? info.color : '#6080aa',
                      boxShadow: selectedShip === id ? `0 0 12px ${info.color}40` : 'none',
                    }}>
                    <span className="text-xl">{info.icon}</span>
                    <div className="text-[10px] mt-1">{info.name}</div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Map selection (host only) */}
          {mode === 'hosting' && (
            <div className="w-full mt-2">
              <div className="text-xs font-mono text-[#6080aa] mb-2 text-center">MAPA</div>
              <div className="grid grid-cols-2 gap-2">
                {MAPS.map(m => (
                  <button key={m.id} onClick={() => setSelectedMap(m.id)}
                    className="py-2 px-3 rounded-lg font-mono text-sm font-bold transition-all"
                    style={{
                      background: selectedMap === m.id ? `${m.color}15` : 'rgba(255,255,255,0.02)',
                      border: `2px solid ${selectedMap === m.id ? m.color : 'rgba(255,255,255,0.08)'}`,
                      color: selectedMap === m.id ? m.color : '#6080aa',
                    }}>
                    {m.name}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Peer info */}
          {peerConnected && (
            <div className="flex items-center gap-2 py-2 px-4 rounded-lg font-mono text-sm mt-2"
              style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.08)' }}>
              <span className="text-lg">{SHIP_INFO[peerShip]?.icon || '?'}</span>
              <span style={{ color: SHIP_INFO[peerShip]?.color || '#fff' }}>{SHIP_INFO[peerShip]?.name || 'Unknown'}</span>
              <span className="text-[#39ff14] text-xs ml-2">ONLINE</span>
            </div>
          )}

          {/* Action buttons */}
          <div className="flex gap-3 mt-4">
            <button onClick={() => { leaveRoom(); setMode('choose'); setPeerConnected(false); }}
              className="py-3 px-6 text-sm font-bold rounded-lg text-[#ff4060] border border-[#ff4060]/30 font-mono transition-all hover:border-[#ff4060]"
              style={{ background: 'rgba(255,64,96,0.05)' }}>
              Sair
            </button>
            {mode === 'hosting' && (
              <button onClick={handleStart} disabled={!peerConnected}
                className="py-3 px-8 text-lg font-bold rounded-lg text-white border font-mono transition-all hover:scale-105 disabled:opacity-30 disabled:hover:scale-100"
                style={{ background: 'linear-gradient(135deg, rgba(0,229,255,0.2), rgba(191,90,242,0.2))', borderColor: '#0ff', boxShadow: peerConnected ? '0 0 20px rgba(0,255,255,0.3)' : 'none' }}>
                🚀 Iniciar
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default MultiplayerLobby;
