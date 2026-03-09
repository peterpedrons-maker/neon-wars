import React, { useState, useEffect, useRef, useCallback } from 'react';
import { ShipType } from '../../game/types';
import { 
  RoomInfo, createRoom, joinRoom, connectToRoom, 
  leaveRoom, sendStartGame, sendCountdown, sendGuestConfirm,
  sendLobbyState, sendChat, LobbyState, ChatMessage,
  CoopPlayerState, CoopGameSync,
  createPublicRoom, fetchPublicRooms, updatePublicRoomPlayerCount,
  setPublicRoomStatus, deletePublicRoom, PublicRoomInfo,
} from '../../game/multiplayer';
import { playClick, playHover, playBack } from '../../game/audio';
import ShipCanvas from './ShipCanvas';

interface MultiplayerLobbyProps {
  unlockedShips: string[];
  username?: string;
  onStartCoop: (
    room: RoomInfo,
    mapId: string,
    difficulty: import('../../game/maps').MapDifficulty,
    playerClass: ShipType,
    peerClasses: ShipType[],
    totalPlayers: number,
  ) => void;
  onBack: () => void;
}

const SHIP_INFO: Record<string, { name: string; color: string }> = {
  phantom: { name: 'Phantom', color: '#bf5af2' },
  interceptor: { name: 'Interceptor', color: '#00e5ff' },
  titan: { name: 'Titan', color: '#ff6b00' },
  spectre: { name: 'Spectre', color: '#9040ff' },
  valkyrie: { name: 'Valkyrie', color: '#ff1493' },
  juggernaut: { name: 'Juggernaut', color: '#ff4500' },
  wraith: { name: 'Wraith', color: '#00ff88' },
  sentinel: { name: 'Sentinel', color: '#4488ff' },
  tempest: { name: 'Tempest', color: '#88ffff' },
  venom: { name: 'Venom', color: '#44ff00' },
  nova_ship: { name: 'Nova', color: '#ff8800' },
  chronos: { name: 'Chronos', color: '#8888ff' },
  leviathan: { name: 'Leviathan', color: '#ff2244' },
  raptor: { name: 'Raptor', color: '#ffff00' },
  oracle: { name: 'Oracle', color: '#ff44ff' },
  pyro: { name: 'Pyro', color: '#ff4400' },
};

const MAPS = [
  { id: 'neon-grid', name: 'Neon Grid', color: '#0ff' },
  { id: 'inferno', name: 'Inferno', color: '#ff6b00' },
  { id: 'void', name: 'Void', color: '#9040ff' },
  { id: 'crystal', name: 'Crystal', color: '#00e5ff' },
];

// Chat Component
const LobbyChat: React.FC<{ 
  messages: ChatMessage[]; onSend: (text: string) => void; isHost: boolean;
}> = ({ messages, onSend, isHost }) => {
  const [input, setInput] = useState('');
  const scrollRef = useRef<HTMLDivElement>(null);
  useEffect(() => { if (scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight; }, [messages]);
  const quickMessages = ['GG!', 'Vamos!', 'Cuidado!', 'Pronto!', '👍', '🔥'];
  const handleSend = () => { const t = input.trim(); if (!t) return; onSend(t); setInput(''); };

  return (
    <div className="flex flex-col rounded-xl overflow-hidden" 
      style={{ background: 'rgba(0,0,20,0.8)', border: '1px solid rgba(0,255,255,0.15)', height: 200 }}>
      <div className="px-3 py-1 text-[10px] font-mono font-bold tracking-wider"
        style={{ background: 'rgba(0,255,255,0.06)', color: '#0ff', borderBottom: '1px solid rgba(0,255,255,0.1)' }}>
        💬 CHAT
      </div>
      <div ref={scrollRef} className="flex-1 overflow-y-auto px-3 py-2 space-y-1" style={{ fontSize: 12 }}>
        {messages.length === 0 && <div className="text-[#334] font-mono text-[10px] text-center mt-4">Sem mensagens...</div>}
        {messages.map((m, i) => (
          <div key={i} className="flex gap-1.5 items-start">
            <span className="font-bold font-mono text-[10px] shrink-0" style={{ color: m.isHost ? '#0ff' : '#bf5af2' }}>
              {m.from.slice(0, 6)}:
            </span>
            <span className="text-[#c0c8e0] font-mono text-[11px] break-all">{m.text}</span>
          </div>
        ))}
      </div>
      <div className="flex gap-1 px-2 py-1 flex-wrap" style={{ borderTop: '1px solid rgba(255,255,255,0.05)' }}>
        {quickMessages.map(qm => (
          <button key={qm} onClick={() => onSend(qm)}
            className="px-2 py-0.5 rounded text-[10px] font-mono transition-all hover:scale-105"
            style={{ background: 'rgba(255,255,255,0.05)', color: '#6080aa', border: '1px solid rgba(255,255,255,0.08)' }}>
            {qm}
          </button>
        ))}
      </div>
      <div className="flex gap-1 p-2" style={{ borderTop: '1px solid rgba(255,255,255,0.05)' }}>
        <input value={input} onChange={e => setInput(e.target.value)}
          onKeyDown={e => { if (e.key === 'Enter') handleSend(); }}
          placeholder="Digite..." maxLength={100}
          className="flex-1 py-1.5 px-3 rounded-lg text-xs font-mono bg-transparent border"
          style={{ borderColor: 'rgba(255,255,255,0.1)', color: '#c0c8e0' }} />
        <button onClick={handleSend} className="px-3 py-1.5 rounded-lg text-xs font-mono font-bold"
          style={{ background: 'rgba(0,255,255,0.1)', color: '#0ff', border: '1px solid rgba(0,255,255,0.2)' }}>➤</button>
      </div>
    </div>
  );
};

const MultiplayerLobby: React.FC<MultiplayerLobbyProps> = ({ unlockedShips, username, onStartCoop, onBack }) => {
  const [mode, setMode] = useState<'choose' | 'lobby' | 'browse'>('choose');
  const [room, setRoom] = useState<RoomInfo | null>(null);
  const [joinCode, setJoinCode] = useState('');
  const [connectedPeers, setConnectedPeers] = useState<Map<string, { ship: ShipType; label: string }>>(new Map());
  const [selectedShip, setSelectedShip] = useState<ShipType>('phantom');
  const [selectedMap, setSelectedMap] = useState('neon-grid');
  const [status, setStatus] = useState('');
  const [countdown, setCountdown] = useState<number | null>(null);
  const [waitingConfirm, setWaitingConfirm] = useState<{ mapId: string; hostClass: string } | null>(null);
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [publicRooms, setPublicRooms] = useState<PublicRoomInfo[]>([]);
  const [loadingRooms, setLoadingRooms] = useState(false);
  
  const peerConnected = connectedPeers.size > 0;
  const totalPlayers = 1 + connectedPeers.size;
  const channelRef = useRef<any>(null);
  const countdownRef = useRef<NodeJS.Timeout | null>(null);
  const startDataRef = useRef<{ mapId: string; hostClass: string } | null>(null);
  const selectedShipRef = useRef(selectedShip);
  const selectedMapRef = useRef(selectedMap);
  const connectedPeersRef = useRef(connectedPeers);
  const roomRef = useRef(room);
  selectedShipRef.current = selectedShip;
  selectedMapRef.current = selectedMap;
  connectedPeersRef.current = connectedPeers;
  roomRef.current = room;

  useEffect(() => {
    return () => { 
      leaveRoom(); 
      if (countdownRef.current) clearInterval(countdownRef.current);
    };
  }, []);

  // Broadcast lobby state when ship/map changes
  useEffect(() => {
    if (!room || !peerConnected) return;
    sendLobbyState({
      shipClass: selectedShip,
      mapId: selectedMap,
      playerId: room.playerId,
      isHost: room.isHost,
      playerLabel: room.isHost ? 'HOST' : `P${totalPlayers}`,
    });
  }, [selectedShip, selectedMap, room, peerConnected, totalPlayers]);

  const handleSendChat = useCallback((text: string) => {
    if (!roomRef.current) return;
    const msg: ChatMessage = { from: roomRef.current.playerId, text, isHost: roomRef.current.isHost, timestamp: Date.now() };
    setChatMessages(prev => [...prev, msg]);
    sendChat(msg);
  }, []);

  const loadPublicRooms = useCallback(async () => {
    setLoadingRooms(true);
    const rooms = await fetchPublicRooms();
    setPublicRooms(rooms);
    setLoadingRooms(false);
  }, []);

  const getPeerClasses = (): ShipType[] => {
    return Array.from(connectedPeersRef.current.values()).map(p => p.ship);
  };

  const setupRoom = (newRoom: RoomInfo) => {
    setRoom(newRoom);
    setMode('lobby');
    setChatMessages([]);
    setConnectedPeers(new Map());
    setStatus(newRoom.isHost ? 'Aguardando jogadores... (máx 6)' : 'Conectando...');

    channelRef.current = connectToRoom(newRoom, {
      onPeerJoin: (peerId?: string) => { 
        if (!peerId) return;
        setConnectedPeers(prev => {
          const next = new Map(prev);
          if (!next.has(peerId)) {
            next.set(peerId, { ship: 'phantom' as ShipType, label: `P${next.size + 2}` });
          }
          return next;
        });
        setStatus(`${connectedPeersRef.current.size + 1} jogadores conectados`);
        sendLobbyState({
          shipClass: selectedShipRef.current,
          mapId: selectedMapRef.current,
          playerId: newRoom.playerId,
          isHost: newRoom.isHost,
        });
        // Update public room player count
        if (newRoom.isPublic && newRoom.isHost) {
          updatePublicRoomPlayerCount(newRoom.roomCode, connectedPeersRef.current.size + 1);
        }
      },
      onPeerLeave: (peerId?: string) => {
        if (!peerId) return;
        setConnectedPeers(prev => {
          const next = new Map(prev);
          next.delete(peerId);
          return next;
        });
        setStatus(connectedPeersRef.current.size > 0 ? `${connectedPeersRef.current.size} jogadores` : 'Aguardando jogadores...');
        if (newRoom.isPublic && newRoom.isHost) {
          updatePublicRoomPlayerCount(newRoom.roomCode, Math.max(1, connectedPeersRef.current.size));
        }
      },
      onPeerState: (state: CoopPlayerState) => {
        if (state.playerId) {
          setConnectedPeers(prev => {
            const next = new Map(prev);
            const existing = next.get(state.playerId!);
            next.set(state.playerId!, { ship: state.shipClass as ShipType, label: existing?.label || `P${next.size + 1}` });
            return next;
          });
        }
      },
      onGameSync: () => {},
      onStartGame: (data) => {
        if (!newRoom.isHost) setWaitingConfirm(data);
      },
      onCountdown: (count: number) => {
        setCountdown(count);
        if (count <= 0) {
          const sd = startDataRef.current;
          if (sd) {
            const pClasses = getPeerClasses();
            const total = 1 + pClasses.length;
            onStartCoop(newRoom, sd.mapId, 'medium', selectedShipRef.current, pClasses, total);
          }
        }
      },
      onConfirm: () => {
        // Any guest confirmed
        if (newRoom.isHost) {
          setStatus('Jogadores confirmaram! Iniciando...');
          let count = 5;
          setCountdown(count);
          sendCountdown(count);
          countdownRef.current = setInterval(() => {
            count--;
            setCountdown(count);
            sendCountdown(count);
            if (count <= 0) {
              clearInterval(countdownRef.current!);
              countdownRef.current = null;
              if (newRoom.isPublic) setPublicRoomStatus(newRoom.roomCode, 'playing');
              const pClasses = getPeerClasses();
              onStartCoop(newRoom, selectedMapRef.current, 'medium', selectedShipRef.current, pClasses, 1 + pClasses.length);
            }
          }, 1000);
        }
      },
      onLobbyState: (state: LobbyState) => {
        if (state.playerId) {
          setConnectedPeers(prev => {
            const next = new Map(prev);
            next.set(state.playerId, { ship: state.shipClass as ShipType, label: state.playerLabel || `P${next.size + 1}` });
            return next;
          });
        }
        if (state.isHost) setSelectedMap(state.mapId);
      },
      onChat: (msg: ChatMessage) => setChatMessages(prev => [...prev, msg]),
      onLevelUp: () => {},
      onUpgradeDone: () => {},
    });
  };

  const handleCreate = (isPublic: boolean = false) => {
    const newRoom = createRoom(isPublic);
    if (isPublic) {
      createPublicRoom(username || 'Piloto', selectedShip, selectedMap, newRoom.roomCode);
    }
    setupRoom(newRoom);
  };

  const handleJoin = () => {
    if (joinCode.length < 3) return;
    setupRoom(joinRoom(joinCode));
  };

  const handleJoinPublic = (roomCode: string) => {
    setupRoom(joinRoom(roomCode));
  };

  const handleGuestConfirm = () => {
    if (!waitingConfirm || !room) return;
    startDataRef.current = waitingConfirm;
    setWaitingConfirm(null);
    sendGuestConfirm(room.playerId);
    setStatus('Aguardando contagem...');
  };

  const handleStart = () => {
    if (!room || !peerConnected) return;
    sendStartGame(selectedMap, selectedShip);
    setStatus('Aguardando confirmação dos jogadores...');
  };

  const handleLeave = () => {
    if (room?.isPublic && room.isHost) deletePublicRoom(room.roomCode);
    leaveRoom();
    setMode('choose');
    setConnectedPeers(new Map());
    setCountdown(null);
    setWaitingConfirm(null);
    setChatMessages([]);
    setRoom(null);
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-[#000008] text-[#e0e8ff] select-none px-4">
      <h1 className="text-4xl md:text-5xl font-bold mb-2 font-mono"
        style={{ textShadow: '0 0 30px rgba(0,255,255,0.4)', color: '#0ff' }}>
        🎮 Multiplayer Coop
      </h1>
      <p className="text-[#6080aa] font-mono mb-6">Até 6 jogadores online!</p>

      {/* COUNTDOWN OVERLAY */}
      {countdown !== null && countdown > 0 && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80">
          <div className="flex flex-col items-center">
            <div className="text-8xl font-black font-mono animate-pulse"
              style={{ color: '#0ff', textShadow: '0 0 60px rgba(0,255,255,0.8)' }}>{countdown}</div>
            <div className="text-xl font-mono mt-4" style={{ color: '#6080aa' }}>Preparando batalha...</div>
          </div>
        </div>
      )}

      {/* GUEST CONFIRMATION */}
      {waitingConfirm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80">
          <div className="flex flex-col items-center gap-4 p-8 rounded-2xl"
            style={{ background: 'rgba(0,0,20,0.95)', border: '2px solid rgba(0,255,255,0.3)' }}>
            <div className="text-2xl font-bold font-mono" style={{ color: '#0ff' }}>🚀 Host quer iniciar!</div>
            <div className="flex gap-4 mt-2">
              <button onClick={handleGuestConfirm}
                className="py-3 px-8 text-lg font-bold rounded-lg text-white border font-mono"
                style={{ background: 'rgba(57,255,20,0.2)', borderColor: '#39ff14' }}>✅ Confirmar</button>
              <button onClick={() => setWaitingConfirm(null)}
                className="py-3 px-6 text-sm font-bold rounded-lg text-[#ff4060] border border-[#ff4060]/30 font-mono">❌ Recusar</button>
            </div>
          </div>
        </div>
      )}

      {mode === 'choose' && (
        <div className="flex flex-col gap-4 w-80">
          <button onClick={() => handleCreate(false)}
            className="py-4 px-8 text-lg font-bold rounded-lg text-white border transition-all hover:scale-105 font-mono"
            style={{ background: 'linear-gradient(135deg, rgba(0,229,255,0.2), rgba(191,90,242,0.2))', borderColor: '#0ff' }}>
            🏠 Criar Sala Privada
          </button>
          <button onClick={() => handleCreate(true)}
            className="py-4 px-8 text-lg font-bold rounded-lg text-white border transition-all hover:scale-105 font-mono"
            style={{ background: 'linear-gradient(135deg, rgba(57,255,20,0.2), rgba(0,229,255,0.2))', borderColor: '#39ff14' }}>
            🌐 Criar Sala Pública
          </button>
          <button onClick={() => { setMode('browse'); loadPublicRooms(); }}
            className="py-4 px-8 text-lg font-bold rounded-lg text-white border transition-all hover:scale-105 font-mono"
            style={{ background: 'linear-gradient(135deg, rgba(255,200,0,0.15), rgba(255,100,0,0.15))', borderColor: '#ffcc00' }}>
            🔍 Buscar Salas Públicas
          </button>
          <div className="flex gap-2">
            <input value={joinCode} onChange={e => setJoinCode(e.target.value.toUpperCase())}
              placeholder="CÓDIGO" maxLength={5}
              className="flex-1 py-3 px-4 text-lg font-bold rounded-lg text-center font-mono bg-transparent border"
              style={{ borderColor: '#bf5af2', color: '#bf5af2' }} />
            <button onClick={handleJoin}
              className="py-3 px-6 text-lg font-bold rounded-lg text-[#bf5af2] border border-[#bf5af2]/50 font-mono"
              style={{ background: 'rgba(191,90,242,0.1)' }}>Entrar</button>
          </div>
          <button onClick={onBack}
            className="py-3 px-8 text-lg font-bold rounded-lg text-[#6080aa] border border-[#6080aa]/30 font-mono mt-4 hover:text-[#0ff]"
            style={{ background: 'rgba(0,255,255,0.03)' }}>← Voltar</button>
        </div>
      )}

      {/* PUBLIC ROOM BROWSER */}
      {mode === 'browse' && (
        <div className="flex flex-col items-center gap-4 w-full max-w-2xl">
          <div className="flex gap-3 items-center mb-2">
            <span className="font-mono text-sm" style={{ color: '#6080aa' }}>
              {loadingRooms ? 'Carregando...' : `${publicRooms.length} sala(s) encontrada(s)`}
            </span>
            <button onClick={loadPublicRooms} className="px-3 py-1 rounded text-xs font-mono font-bold"
              style={{ background: 'rgba(0,255,255,0.1)', color: '#0ff', border: '1px solid rgba(0,255,255,0.2)' }}>
              🔄 Atualizar
            </button>
          </div>
          
          <div className="w-full space-y-2 max-h-[50vh] overflow-y-auto">
            {publicRooms.length === 0 && !loadingRooms && (
              <div className="text-center py-8 font-mono text-[#6080aa]">
                Nenhuma sala pública disponível. Crie uma!
              </div>
            )}
            {publicRooms.map(pr => (
              <button key={pr.id} onClick={() => { playClick(); handleJoinPublic(pr.room_code); }}
                className="w-full flex items-center gap-4 p-4 rounded-xl border transition-all hover:scale-[1.02]"
                style={{ background: 'rgba(0,0,20,0.9)', border: '1px solid rgba(0,255,255,0.15)' }}>
                <div className="w-10 h-10 rounded-lg flex items-center justify-center"
                  style={{ background: `${SHIP_INFO[pr.host_ship]?.color || '#0ff'}15` }}>
                  <ShipCanvas shipType={pr.host_ship as ShipType} width={36} height={28} />
                </div>
                <div className="flex-1 text-left">
                  <div className="font-mono font-bold text-sm" style={{ color: '#e0e8ff' }}>{pr.host_name}</div>
                  <div className="font-mono text-[10px]" style={{ color: '#6080aa' }}>
                    {MAPS.find(m => m.id === pr.map_id)?.name || pr.map_id}
                  </div>
                </div>
                <div className="text-right">
                  <div className="font-mono text-sm font-bold" style={{ color: pr.player_count >= 5 ? '#ff4060' : '#39ff14' }}>
                    {pr.player_count}/{pr.max_players}
                  </div>
                  <div className="font-mono text-[10px]" style={{ color: '#6080aa' }}>jogadores</div>
                </div>
                <div className="font-mono text-xs px-3 py-1 rounded"
                  style={{ background: 'rgba(0,255,255,0.1)', color: '#0ff', border: '1px solid rgba(0,255,255,0.2)' }}>
                  Entrar
                </div>
              </button>
            ))}
          </div>

          <button onClick={() => { playBack(); setMode('choose'); }}
            className="py-3 px-8 text-sm font-bold rounded-lg text-[#6080aa] border border-[#6080aa]/30 font-mono hover:text-[#0ff]"
            style={{ background: 'rgba(0,255,255,0.03)' }}>← Voltar</button>
        </div>
      )}

      {mode === 'lobby' && (
        <div className="flex flex-col items-center gap-4 w-full max-w-4xl">
          {/* Room code + status */}
          <div className="flex items-center gap-6 flex-wrap justify-center">
            {room && (
              <div className="text-center">
                <div className="text-[10px] font-mono text-[#6080aa] mb-1">
                  {room.isPublic ? '🌐 SALA PÚBLICA' : '🔒 SALA PRIVADA'}
                </div>
                <div className="text-3xl font-black font-mono tracking-[0.3em] py-1.5 px-5 rounded-lg"
                  style={{ color: '#0ff', background: 'rgba(0,255,255,0.08)', border: '2px solid rgba(0,255,255,0.3)' }}>
                  {room.roomCode}
                </div>
              </div>
            )}
            <div className="flex items-center gap-2 py-2 px-4 rounded-full font-mono text-sm"
              style={{ background: peerConnected ? 'rgba(57,255,20,0.1)' : 'rgba(255,255,0,0.1)', 
                border: `1px solid ${peerConnected ? 'rgba(57,255,20,0.3)' : 'rgba(255,255,0,0.3)'}`,
                color: peerConnected ? '#39ff14' : '#ffff00' }}>
              <span className="w-2 h-2 rounded-full" style={{ background: peerConnected ? '#39ff14' : '#ffff00' }} />
              {totalPlayers}/6 jogadores • {status}
            </div>
          </div>

          {/* Main layout */}
          <div className="flex gap-4 w-full flex-col lg:flex-row">
            {/* Left: Ship selection */}
            <div className="flex-1 flex flex-col gap-3">
              <div className="text-[10px] font-mono text-[#6080aa] text-center tracking-wider">
                {room?.isHost ? '👑 HOST — SUA NAVE' : '🎮 SUA NAVE'}
              </div>
              <div className="grid grid-cols-3 md:grid-cols-4 gap-2">
                {(unlockedShips.length > 0 ? unlockedShips : ['phantom', 'interceptor', 'titan']).map(id => {
                  const info = SHIP_INFO[id];
                  if (!info) return null;
                  const isSelected = selectedShip === id;
                  return (
                    <button key={id} onClick={() => setSelectedShip(id as ShipType)}
                      className="flex flex-col items-center p-2 rounded-xl border transition-all hover:scale-105"
                      style={{
                        borderColor: isSelected ? info.color : 'rgba(255,255,255,0.06)',
                        background: isSelected ? `${info.color}10` : 'rgba(0,0,8,0.95)',
                        boxShadow: isSelected ? `0 0 15px ${info.color}33` : 'none',
                      }}>
                      {SHIP_ICONS[id] ? (
                        <img src={SHIP_ICONS[id]} alt={info.name} className="w-12 h-12 object-contain" />
                      ) : (
                        <div className="w-12 h-12 rounded-full" style={{ background: `${info.color}30` }} />
                      )}
                      <span className="text-[10px] font-bold font-mono mt-1" style={{ color: isSelected ? info.color : '#6080aa' }}>
                        {info.name}
                      </span>
                    </button>
                  );
                })}
              </div>

              {/* Connected peers */}
              {connectedPeers.size > 0 && (
                <div className="mt-2">
                  <div className="text-[10px] font-mono text-[#6080aa] text-center tracking-wider mb-1">
                    🎮 OUTROS JOGADORES ({connectedPeers.size})
                  </div>
                  <div className="grid grid-cols-2 gap-2">
                    {Array.from(connectedPeers.entries()).map(([pid, peer], i) => (
                      <div key={pid} className="flex items-center gap-2 py-2 px-3 rounded-xl"
                        style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.08)' }}>
                        {SHIP_ICONS[peer.ship] ? (
                          <img src={SHIP_ICONS[peer.ship]} alt="" className="w-8 h-8 object-contain" />
                        ) : (
                          <div className="w-8 h-8 rounded-full" style={{ background: `${SHIP_INFO[peer.ship]?.color || '#fff'}30` }} />
                        )}
                        <div>
                          <span className="font-bold font-mono text-xs" style={{ color: SHIP_INFO[peer.ship]?.color || '#fff' }}>
                            {SHIP_INFO[peer.ship]?.name || 'Unknown'}
                          </span>
                          <span className="text-[#39ff14] text-[10px] ml-1 font-mono">P{i + 2}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Right: Map + Chat */}
            <div className="w-full lg:w-80 flex flex-col gap-3">
              <div>
                <div className="text-[10px] font-mono text-[#6080aa] text-center tracking-wider mb-1">
                  🗺️ MAPA {!room?.isHost && '(host escolhe)'}
                </div>
                <div className="grid grid-cols-2 gap-2">
                  {MAPS.map(m => (
                    <button key={m.id}
                      onClick={() => { if (room?.isHost) { playClick(); setSelectedMap(m.id); } }}
                      disabled={!room?.isHost}
                      className="py-2 px-3 rounded-lg font-mono text-sm font-bold transition-all"
                      style={{
                        background: selectedMap === m.id ? `${m.color}15` : 'rgba(255,255,255,0.02)',
                        border: `2px solid ${selectedMap === m.id ? m.color : 'rgba(255,255,255,0.08)'}`,
                        color: selectedMap === m.id ? m.color : '#6080aa',
                        opacity: !room?.isHost && selectedMap !== m.id ? 0.4 : 1,
                        cursor: room?.isHost ? 'pointer' : 'default',
                      }}>
                      {m.name}
                    </button>
                  ))}
                </div>
              </div>
              <LobbyChat messages={chatMessages} onSend={handleSendChat} isHost={room?.isHost ?? false} />
            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-3 mt-2">
            <button onClick={() => { playBack(); handleLeave(); }}
              className="py-3 px-6 text-sm font-bold rounded-lg text-[#ff4060] border border-[#ff4060]/30 font-mono">Sair</button>
            {room?.isHost && (
              <button onClick={() => { playClick(); handleStart(); }} disabled={!peerConnected || countdown !== null}
                className="py-3 px-8 text-lg font-bold rounded-lg text-white border font-mono transition-all hover:scale-105 disabled:opacity-30"
                style={{ background: 'linear-gradient(135deg, rgba(0,229,255,0.2), rgba(191,90,242,0.2))', borderColor: '#0ff' }}>
                🚀 Iniciar ({totalPlayers} jogadores)
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default MultiplayerLobby;
