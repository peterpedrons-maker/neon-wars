import React, { useState, useEffect, useRef, useCallback } from 'react';
import { ShipType } from '../../game/types';
import { 
  RoomInfo, createRoom, joinRoom, connectToRoom, 
  leaveRoom, sendStartGame, sendCountdown, sendGuestConfirm,
  sendLobbyState, sendChat, LobbyState, ChatMessage,
  CoopPlayerState, CoopGameSync 
} from '../../game/multiplayer';

interface MultiplayerLobbyProps {
  unlockedShips: string[];
  onStartCoop: (
    room: RoomInfo,
    mapId: string,
    difficulty: import('../../game/maps').MapDifficulty,
    playerClass: ShipType,
    peerClass: ShipType,
  ) => void;
  onBack: () => void;
}

const SHIP_INFO: Record<string, { name: string; desc: string; stats: string; color: string; glow: string }> = {
  phantom: { name: 'Phantom', desc: 'Nave ágil com disparos energéticos.', stats: 'DMG: 15 | VEL: Média', color: '#bf5af2', glow: '#e0b0ff' },
  interceptor: { name: 'Interceptor', desc: 'Ultra veloz com tiro rápido.', stats: 'DMG: 10 | VEL: Alta', color: '#00e5ff', glow: '#80f0ff' },
  titan: { name: 'Titan', desc: 'Nave pesada com ataque devastador.', stats: 'DMG: 28 | VEL: Baixa', color: '#ff6b00', glow: '#ffaa55' },
  spectre: { name: 'Spectre', desc: 'Nave furtiva com dano alto.', stats: 'DMG: 20 | VEL: Alta', color: '#9040ff', glow: '#c090ff' },
  valkyrie: { name: 'Valkyrie', desc: 'Guerreira com tiro rápido e HP extra.', stats: 'DMG: 12 | VEL: Média-Alta', color: '#ff1493', glow: '#ff80b0' },
  juggernaut: { name: 'Juggernaut', desc: 'Fortaleza indestrutível.', stats: 'DMG: 35 | VEL: Muito Baixa', color: '#ff4500', glow: '#ff8040' },
};

const MAPS = [
  { id: 'neon-grid', name: 'Neon Grid', color: '#0ff' },
  { id: 'inferno', name: 'Inferno', color: '#ff6b00' },
  { id: 'void', name: 'Void', color: '#9040ff' },
  { id: 'crystal', name: 'Crystal', color: '#00e5ff' },
];

function hexToRgba(hex: string, a: number): string {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return `rgba(${r},${g},${b},${a})`;
}

function drawShipPreview(ctx: CanvasRenderingContext2D, shipType: ShipType, w: number, h: number, time: number) {
  ctx.clearRect(0, 0, w, h);
  const info = SHIP_INFO[shipType];
  if (!info) return;
  const color = info.color;
  const glow = info.glow;
  const cx = w / 2;
  const cy = h / 2;
  const r = 18;

  const bgGrad = ctx.createRadialGradient(cx, cy, 5, cx, cy, 80);
  bgGrad.addColorStop(0, hexToRgba(color, 0.15));
  bgGrad.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.fillStyle = bgGrad;
  ctx.fillRect(0, 0, w, h);

  ctx.save();
  ctx.translate(cx, cy);

  const thrustPulse = 0.6 + Math.sin(time * 18) * 0.3;
  const thrustLen = 18;
  const exhaustSpread = shipType === 'titan' || shipType === 'juggernaut' ? 6 : shipType === 'phantom' ? 4 : 3;
  
  for (let i = -1; i <= 1; i += 2) {
    const oy = i * exhaustSpread;
    ctx.fillStyle = hexToRgba(color, thrustPulse * 0.4);
    ctx.beginPath();
    ctx.moveTo(-r * 0.4, oy - 3);
    ctx.quadraticCurveTo(-r - thrustLen * 0.7, oy, -r - thrustLen, oy);
    ctx.quadraticCurveTo(-r - thrustLen * 0.7, oy, -r * 0.4, oy + 3);
    ctx.closePath(); ctx.fill();
    ctx.fillStyle = hexToRgba('#ffffff', thrustPulse * 0.7);
    ctx.beginPath();
    ctx.moveTo(-r * 0.35, oy - 1.2);
    ctx.lineTo(-r - thrustLen * 0.5, oy);
    ctx.lineTo(-r * 0.35, oy + 1.2);
    ctx.closePath(); ctx.fill();
  }

  ctx.shadowColor = color;
  ctx.shadowBlur = 20 + Math.sin(time * 3) * 6;

  if (shipType === 'phantom') {
    ctx.beginPath();
    ctx.moveTo(r * 1.8, 0);
    ctx.lineTo(r * 0.6, -r * 0.25); ctx.lineTo(r * 0.1, -r * 0.35);
    ctx.lineTo(-r * 0.3, -r * 1.2); ctx.lineTo(-r * 0.7, -r * 1.0);
    ctx.lineTo(-r * 0.55, -r * 0.25); ctx.lineTo(-r * 0.7, -r * 0.15);
    ctx.lineTo(-r * 0.7, r * 0.15); ctx.lineTo(-r * 0.55, r * 0.25);
    ctx.lineTo(-r * 0.7, r * 1.0); ctx.lineTo(-r * 0.3, r * 1.2);
    ctx.lineTo(r * 0.1, r * 0.35); ctx.lineTo(r * 0.6, r * 0.25);
    ctx.closePath();
    ctx.fillStyle = hexToRgba(color, 0.15); ctx.fill();
    ctx.strokeStyle = color; ctx.lineWidth = 1.5; ctx.stroke();
    ctx.strokeStyle = hexToRgba(glow, 0.5); ctx.lineWidth = 0.8;
    ctx.beginPath();
    ctx.moveTo(r * 0.3, -r * 0.2); ctx.lineTo(-r * 0.4, -r * 0.9);
    ctx.moveTo(r * 0.3, r * 0.2); ctx.lineTo(-r * 0.4, r * 0.9);
    ctx.stroke();
    const wingPulse = 0.5 + Math.sin(time * 4) * 0.3;
    ctx.fillStyle = hexToRgba(glow, wingPulse);
    ctx.beginPath(); ctx.arc(-r * 0.3, -r * 1.15, 1.5, 0, Math.PI * 2); ctx.fill();
    ctx.beginPath(); ctx.arc(-r * 0.3, r * 1.15, 1.5, 0, Math.PI * 2); ctx.fill();
  } else if (shipType === 'interceptor') {
    ctx.beginPath();
    ctx.moveTo(r * 2.0, 0);
    ctx.lineTo(r * 0.8, -r * 0.2); ctx.lineTo(r * 0.3, -r * 0.35);
    ctx.lineTo(-r * 0.2, -r * 0.3); ctx.lineTo(-r * 0.5, -r * 0.15);
    ctx.lineTo(-r * 0.5, r * 0.15); ctx.lineTo(-r * 0.2, r * 0.3);
    ctx.lineTo(r * 0.3, r * 0.35); ctx.lineTo(r * 0.8, r * 0.2);
    ctx.closePath();
    ctx.fillStyle = hexToRgba(color, 0.12); ctx.fill();
    ctx.strokeStyle = color; ctx.lineWidth = 1.2; ctx.stroke();
    for (const side of [-1, 1]) {
      ctx.beginPath();
      ctx.moveTo(r * 0.4, side * r * 0.35); ctx.lineTo(-r * 0.1, side * r * 0.7);
      ctx.lineTo(-r * 0.6, side * r * 0.65); ctx.lineTo(-r * 0.4, side * r * 0.35);
      ctx.closePath();
      ctx.fillStyle = hexToRgba(color, 0.1); ctx.fill();
      ctx.strokeStyle = color; ctx.lineWidth = 1; ctx.stroke();
    }
    ctx.fillStyle = hexToRgba('#ffffff', 0.6 + Math.sin(time * 8) * 0.3);
    ctx.beginPath(); ctx.arc(r * 1.8, 0, 1, 0, Math.PI * 2); ctx.fill();
  } else if (shipType === 'titan') {
    ctx.beginPath();
    ctx.moveTo(r * 1.5, 0);
    ctx.lineTo(r * 0.6, -r * 0.45); ctx.lineTo(r * 0.1, -r * 0.6);
    ctx.lineTo(-r * 0.3, -r * 0.7); ctx.lineTo(-r * 0.5, -r * 1.3);
    ctx.lineTo(-r * 0.8, -r * 1.1); ctx.lineTo(-r * 0.65, -r * 0.5);
    ctx.lineTo(-r * 0.8, -r * 0.25); ctx.lineTo(-r * 0.8, r * 0.25);
    ctx.lineTo(-r * 0.65, r * 0.5); ctx.lineTo(-r * 0.8, r * 1.1);
    ctx.lineTo(-r * 0.5, r * 1.3); ctx.lineTo(-r * 0.3, r * 0.7);
    ctx.lineTo(r * 0.1, r * 0.6); ctx.lineTo(r * 0.6, r * 0.45);
    ctx.closePath();
    ctx.fillStyle = hexToRgba(color, 0.18); ctx.fill();
    ctx.strokeStyle = color; ctx.lineWidth = 2; ctx.stroke();
    const cannonPulse = 0.4 + Math.sin(time * 3) * 0.2;
    ctx.fillStyle = hexToRgba(glow, cannonPulse);
    ctx.beginPath(); ctx.arc(r * 1.3, 0, 2.5, 0, Math.PI * 2); ctx.fill();
  } else if (shipType === 'spectre') {
    const phase = Math.sin(time * 5) * 0.15;
    ctx.globalAlpha = 0.85 + phase;
    ctx.beginPath();
    ctx.moveTo(r * 2.0, 0);
    ctx.quadraticCurveTo(r * 1.2, -r * 0.5, r * 0.2, -r * 0.6);
    ctx.lineTo(-r * 0.4, -r * 0.8);
    ctx.quadraticCurveTo(-r * 0.7, -r * 0.4, -r * 0.6, 0);
    ctx.quadraticCurveTo(-r * 0.7, r * 0.4, -r * 0.4, r * 0.8);
    ctx.lineTo(r * 0.2, r * 0.6);
    ctx.quadraticCurveTo(r * 1.2, r * 0.5, r * 2.0, 0);
    ctx.closePath();
    ctx.fillStyle = hexToRgba(color, 0.12); ctx.fill();
    ctx.strokeStyle = color; ctx.lineWidth = 1.2; ctx.stroke();
    ctx.strokeStyle = hexToRgba(glow, 0.4 + Math.sin(time * 8) * 0.3);
    ctx.lineWidth = 0.6; ctx.setLineDash([3, 4]);
    ctx.beginPath();
    ctx.moveTo(r * 1.5, -r * 0.15); ctx.lineTo(-r * 0.3, -r * 0.6);
    ctx.moveTo(r * 1.5, r * 0.15); ctx.lineTo(-r * 0.3, r * 0.6);
    ctx.stroke(); ctx.setLineDash([]);
    const ghostPulse = 0.5 + Math.sin(time * 6) * 0.4;
    ctx.fillStyle = hexToRgba(glow, ghostPulse);
    ctx.beginPath(); ctx.arc(r * 0.3, 0, 2, 0, Math.PI * 2); ctx.fill();
    ctx.globalAlpha = 1;
  } else if (shipType === 'valkyrie') {
    ctx.beginPath();
    ctx.moveTo(r * 1.8, 0);
    ctx.lineTo(r * 0.5, -r * 0.3); ctx.lineTo(r * 0.1, -r * 0.4);
    ctx.lineTo(-r * 0.2, -r * 1.4); ctx.lineTo(-r * 0.5, -r * 1.2);
    ctx.lineTo(-r * 0.3, -r * 0.35); ctx.lineTo(-r * 0.6, -r * 0.2);
    ctx.lineTo(-r * 0.6, r * 0.2); ctx.lineTo(-r * 0.3, r * 0.35);
    ctx.lineTo(-r * 0.5, r * 1.2); ctx.lineTo(-r * 0.2, r * 1.4);
    ctx.lineTo(r * 0.1, r * 0.4); ctx.lineTo(r * 0.5, r * 0.3);
    ctx.closePath();
    ctx.fillStyle = hexToRgba(color, 0.15); ctx.fill();
    ctx.strokeStyle = color; ctx.lineWidth = 1.5; ctx.stroke();
    const spearPulse = 0.5 + Math.sin(time * 5) * 0.3;
    ctx.strokeStyle = hexToRgba(glow, spearPulse); ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(-r * 0.2, -r * 1.4); ctx.lineTo(r * 0.3, -r * 0.2);
    ctx.moveTo(-r * 0.2, r * 1.4); ctx.lineTo(r * 0.3, r * 0.2);
    ctx.stroke();
    ctx.fillStyle = hexToRgba('#ffffff', spearPulse);
    ctx.beginPath(); ctx.arc(-r * 0.2, -r * 1.35, 1.8, 0, Math.PI * 2); ctx.fill();
    ctx.beginPath(); ctx.arc(-r * 0.2, r * 1.35, 1.8, 0, Math.PI * 2); ctx.fill();
  } else if (shipType === 'juggernaut') {
    const sides = 6;
    ctx.beginPath();
    for (let i = 0; i <= sides; i++) {
      const a = (i / sides) * Math.PI * 2 - Math.PI / 6;
      const rr = r * 1.3;
      const px = Math.cos(a) * rr;
      const py = Math.sin(a) * rr * 0.85;
      if (i === 0) ctx.moveTo(px, py); else ctx.lineTo(px, py);
    }
    ctx.closePath();
    ctx.fillStyle = hexToRgba(color, 0.2); ctx.fill();
    ctx.strokeStyle = color; ctx.lineWidth = 2.5; ctx.stroke();
    ctx.strokeStyle = hexToRgba(glow, 0.3); ctx.lineWidth = 1;
    ctx.beginPath();
    for (let i = 0; i <= sides; i++) {
      const a = (i / sides) * Math.PI * 2 - Math.PI / 6;
      const rr = r * 0.8;
      const px = Math.cos(a) * rr;
      const py = Math.sin(a) * rr * 0.85;
      if (i === 0) ctx.moveTo(px, py); else ctx.lineTo(px, py);
    }
    ctx.closePath(); ctx.stroke();
    const corePulse = 0.4 + Math.sin(time * 2) * 0.2;
    const coreGrad = ctx.createRadialGradient(0, 0, 0, 0, 0, r * 0.5);
    coreGrad.addColorStop(0, hexToRgba('#ffffff', corePulse));
    coreGrad.addColorStop(0.5, hexToRgba(color, corePulse * 0.5));
    coreGrad.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = coreGrad;
    ctx.beginPath(); ctx.arc(0, 0, r * 0.5, 0, Math.PI * 2); ctx.fill();
    for (const side of [-1, 0, 1]) {
      ctx.fillStyle = hexToRgba(glow, 0.5);
      ctx.fillRect(r * 0.8, side * r * 0.35 - 1, r * 0.6, 2);
    }
  }

  const cockpitPulse = 0.4 + Math.sin(time * 2) * 0.15;
  ctx.fillStyle = hexToRgba('#ffffff', cockpitPulse);
  ctx.beginPath(); ctx.arc(r * 0.4, 0, 2, 0, Math.PI * 2); ctx.fill();
  ctx.restore();
}

// ShipCanvas as a proper component
const ShipCanvas: React.FC<{ shipType: ShipType }> = ({ shipType }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animRef = useRef<number>(0);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    const w = 160, h = 120;
    canvas.width = w * 2; canvas.height = h * 2;
    ctx.scale(2, 2);
    function loop() {
      const time = Date.now() * 0.001;
      drawShipPreview(ctx!, shipType, w, h, time);
      animRef.current = requestAnimationFrame(loop);
    }
    loop();
    return () => cancelAnimationFrame(animRef.current);
  }, [shipType]);

  return <canvas ref={canvasRef} style={{ width: 160, height: 120 }} className="pointer-events-none" />;
};

// ── Chat Component ──
const LobbyChat: React.FC<{ 
  messages: ChatMessage[]; 
  onSend: (text: string) => void;
  isHost: boolean;
}> = ({ messages, onSend, isHost }) => {
  const [input, setInput] = useState('');
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const quickMessages = ['GG!', 'Vamos!', 'Cuidado!', 'Pronto!', '👍', '🔥'];

  const handleSend = () => {
    const text = input.trim();
    if (!text) return;
    onSend(text);
    setInput('');
  };

  return (
    <div className="flex flex-col rounded-xl overflow-hidden" 
      style={{ background: 'rgba(0,0,20,0.8)', border: '1px solid rgba(0,255,255,0.15)', height: 220 }}>
      <div className="px-3 py-1.5 text-[10px] font-mono font-bold tracking-wider"
        style={{ background: 'rgba(0,255,255,0.06)', color: '#0ff', borderBottom: '1px solid rgba(0,255,255,0.1)' }}>
        💬 CHAT
      </div>
      <div ref={scrollRef} className="flex-1 overflow-y-auto px-3 py-2 space-y-1" style={{ fontSize: 12 }}>
        {messages.length === 0 && (
          <div className="text-[#334] font-mono text-[10px] text-center mt-4">Nenhuma mensagem ainda...</div>
        )}
        {messages.map((m, i) => (
          <div key={i} className="flex gap-1.5 items-start">
            <span className="font-bold font-mono text-[10px] shrink-0" 
              style={{ color: m.isHost ? '#0ff' : '#bf5af2' }}>
              {m.isHost ? 'HOST' : 'P2'}:
            </span>
            <span className="text-[#c0c8e0] font-mono text-[11px] break-all">{m.text}</span>
          </div>
        ))}
      </div>
      {/* Quick messages */}
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
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => { if (e.key === 'Enter') handleSend(); }}
          placeholder="Digite..."
          maxLength={100}
          className="flex-1 py-1.5 px-3 rounded-lg text-xs font-mono bg-transparent border"
          style={{ borderColor: 'rgba(255,255,255,0.1)', color: '#c0c8e0' }}
        />
        <button onClick={handleSend}
          className="px-3 py-1.5 rounded-lg text-xs font-mono font-bold"
          style={{ background: 'rgba(0,255,255,0.1)', color: '#0ff', border: '1px solid rgba(0,255,255,0.2)' }}>
          ➤
        </button>
      </div>
    </div>
  );
};

// ── Main Lobby ──
const MultiplayerLobby: React.FC<MultiplayerLobbyProps> = ({ unlockedShips, onStartCoop, onBack }) => {
  const [mode, setMode] = useState<'choose' | 'lobby'>('choose');
  const [room, setRoom] = useState<RoomInfo | null>(null);
  const [joinCode, setJoinCode] = useState('');
  const [peerConnected, setPeerConnected] = useState(false);
  const [selectedShip, setSelectedShip] = useState<ShipType>('phantom');
  const [selectedMap, setSelectedMap] = useState('neon-grid');
  const [peerShip, setPeerShip] = useState<ShipType>('interceptor');
  const [status, setStatus] = useState('');
  const [countdown, setCountdown] = useState<number | null>(null);
  const [waitingConfirm, setWaitingConfirm] = useState<{ mapId: string; hostClass: string } | null>(null);
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  
  const channelRef = useRef<any>(null);
  const countdownRef = useRef<NodeJS.Timeout | null>(null);
  const startDataRef = useRef<{ mapId: string; hostClass: string } | null>(null);
  const selectedShipRef = useRef(selectedShip);
  const selectedMapRef = useRef(selectedMap);
  const peerShipRef = useRef(peerShip);
  const roomRef = useRef(room);
  selectedShipRef.current = selectedShip;
  selectedMapRef.current = selectedMap;
  peerShipRef.current = peerShip;
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
    });
  }, [selectedShip, selectedMap, room, peerConnected]);

  const handleSendChat = useCallback((text: string) => {
    if (!roomRef.current) return;
    const msg: ChatMessage = {
      from: roomRef.current.playerId,
      text,
      isHost: roomRef.current.isHost,
      timestamp: Date.now(),
    };
    setChatMessages(prev => [...prev, msg]);
    sendChat(msg);
  }, []);

  const setupRoom = (newRoom: RoomInfo) => {
    setRoom(newRoom);
    setMode('lobby');
    setChatMessages([]);
    setStatus(newRoom.isHost ? 'Aguardando jogador...' : 'Conectando...');

    channelRef.current = connectToRoom(newRoom, {
      onPeerJoin: () => { 
        setPeerConnected(true); 
        setStatus(newRoom.isHost ? 'Jogador conectado!' : 'Conectado ao host!');
        // Send our lobby state immediately
        sendLobbyState({
          shipClass: selectedShipRef.current,
          mapId: selectedMapRef.current,
          playerId: newRoom.playerId,
          isHost: newRoom.isHost,
        });
      },
      onPeerLeave: () => { setPeerConnected(false); setStatus('Jogador desconectou'); },
      onPeerState: (state: CoopPlayerState) => { setPeerShip(state.shipClass as ShipType); },
      onGameSync: () => {},
      onStartGame: (data) => {
        // Guest receives start request
        if (!newRoom.isHost) {
          setWaitingConfirm(data);
        }
      },
      onCountdown: (count: number) => {
        setCountdown(count);
        if (count <= 0) {
          const sd = startDataRef.current;
          if (sd) {
            onStartCoop(newRoom, sd.mapId, 'medium', selectedShipRef.current, sd.hostClass as ShipType);
          }
        }
      },
      onConfirm: () => {
        if (newRoom.isHost) {
          // Guest confirmed! Start countdown
          setStatus('Jogador confirmou! Iniciando...');
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
              onStartCoop(newRoom, selectedMapRef.current, selectedShipRef.current, peerShipRef.current);
            }
          }, 1000);
        }
      },
      onLobbyState: (state: LobbyState) => {
        // Receive peer's lobby state
        setPeerShip(state.shipClass as ShipType);
        if (state.isHost) {
          // Guest receives host's map selection
          setSelectedMap(state.mapId);
        }
      },
      onChat: (msg: ChatMessage) => {
        setChatMessages(prev => [...prev, msg]);
      },
      onLevelUp: () => {},
      onUpgradeDone: () => {},
    });
  };

  const handleCreate = () => setupRoom(createRoom());

  const handleJoin = () => {
    if (joinCode.length < 3) return;
    setupRoom(joinRoom(joinCode));
  };

  const handleGuestConfirm = () => {
    if (!waitingConfirm || !room) return;
    startDataRef.current = waitingConfirm;
    setWaitingConfirm(null);
    sendGuestConfirm();
    setStatus('Aguardando contagem...');
  };

  const handleGuestDecline = () => {
    setWaitingConfirm(null);
  };

  const handleStart = () => {
    if (!room || !peerConnected) return;
    sendStartGame(selectedMap, selectedShip);
    setStatus('Aguardando confirmação do jogador...');
  };

  const handleLeave = () => {
    leaveRoom();
    setMode('choose');
    setPeerConnected(false);
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
      <p className="text-[#6080aa] font-mono mb-6">Jogue com um amigo online!</p>

      {/* COUNTDOWN OVERLAY */}
      {countdown !== null && countdown > 0 && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80">
          <div className="flex flex-col items-center">
            <div className="text-8xl font-black font-mono animate-pulse"
              style={{ color: '#0ff', textShadow: '0 0 60px rgba(0,255,255,0.8)' }}>
              {countdown}
            </div>
            <div className="text-xl font-mono mt-4" style={{ color: '#6080aa' }}>
              Preparando batalha...
            </div>
          </div>
        </div>
      )}

      {/* GUEST CONFIRMATION DIALOG */}
      {waitingConfirm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80">
          <div className="flex flex-col items-center gap-4 p-8 rounded-2xl"
            style={{ background: 'rgba(0,0,20,0.95)', border: '2px solid rgba(0,255,255,0.3)', boxShadow: '0 0 40px rgba(0,255,255,0.2)' }}>
            <div className="text-2xl font-bold font-mono" style={{ color: '#0ff' }}>
              🚀 Host quer iniciar!
            </div>
            <div className="text-sm font-mono text-[#6080aa]">
              Mapa: <span style={{ color: MAPS.find(m => m.id === waitingConfirm.mapId)?.color || '#fff' }}>
                {MAPS.find(m => m.id === waitingConfirm.mapId)?.name || waitingConfirm.mapId}
              </span>
            </div>
            <div className="flex gap-4 mt-2">
              <button onClick={handleGuestConfirm}
                className="py-3 px-8 text-lg font-bold rounded-lg text-white border font-mono transition-all hover:scale-105"
                style={{ background: 'linear-gradient(135deg, rgba(57,255,20,0.2), rgba(0,229,255,0.2))', borderColor: '#39ff14', boxShadow: '0 0 20px rgba(57,255,20,0.3)' }}>
                ✅ Confirmar
              </button>
              <button onClick={handleGuestDecline}
                className="py-3 px-6 text-sm font-bold rounded-lg text-[#ff4060] border border-[#ff4060]/30 font-mono transition-all hover:border-[#ff4060]"
                style={{ background: 'rgba(255,64,96,0.05)' }}>
                ❌ Recusar
              </button>
            </div>
          </div>
        </div>
      )}

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

      {mode === 'lobby' && (
        <div className="flex flex-col items-center gap-4 w-full max-w-4xl">
          {/* Room code + status */}
          <div className="flex items-center gap-6 flex-wrap justify-center">
            {room && (
              <div className="text-center">
                <div className="text-[10px] font-mono text-[#6080aa] mb-1">CÓDIGO DA SALA</div>
                <div className="text-3xl font-black font-mono tracking-[0.3em] py-1.5 px-5 rounded-lg"
                  style={{ color: '#0ff', background: 'rgba(0,255,255,0.08)', border: '2px solid rgba(0,255,255,0.3)', textShadow: '0 0 15px rgba(0,255,255,0.5)' }}>
                  {room.roomCode}
                </div>
              </div>
            )}
            <div className="flex items-center gap-2 py-2 px-4 rounded-full font-mono text-sm"
              style={{ background: peerConnected ? 'rgba(57,255,20,0.1)' : 'rgba(255,255,0,0.1)', border: `1px solid ${peerConnected ? 'rgba(57,255,20,0.3)' : 'rgba(255,255,0,0.3)'}`, color: peerConnected ? '#39ff14' : '#ffff00' }}>
              <span className="w-2 h-2 rounded-full" style={{ background: peerConnected ? '#39ff14' : '#ffff00', boxShadow: `0 0 6px ${peerConnected ? '#39ff14' : '#ffff00'}` }} />
              {status}
            </div>
          </div>

          {/* Main layout: two columns + chat */}
          <div className="flex gap-4 w-full flex-col lg:flex-row">
            {/* Left column: Players */}
            <div className="flex-1 flex flex-col gap-3">
              {/* YOUR SHIP */}
              <div className="text-[10px] font-mono text-[#6080aa] text-center tracking-wider">
                {room?.isHost ? '👑 HOST — SUA NAVE' : '🎮 PLAYER 2 — SUA NAVE'}
              </div>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                {(unlockedShips && unlockedShips.length > 0 ? unlockedShips : ['phantom', 'interceptor', 'titan', 'spectre']).map(id => {
                  const info = SHIP_INFO[id];
                  if (!info) return null;
                  const isSelected = selectedShip === id;
                  return (
                    <button key={id} onClick={() => setSelectedShip(id as ShipType)}
                      className="flex flex-col items-center p-2 rounded-xl border transition-all duration-300 hover:scale-105 active:scale-95"
                      style={{
                        borderColor: isSelected ? info.color : 'rgba(255,255,255,0.06)',
                        background: `linear-gradient(180deg, rgba(0,0,8,0.95) 0%, rgba(0,0,20,0.98) 100%)`,
                        boxShadow: isSelected ? `0 0 20px ${info.color}33, inset 0 0 15px ${info.color}11` : 'none',
                      }}>
                      <ShipCanvas shipType={id as ShipType} />
                      <h3 className="text-xs font-bold font-mono" style={{ color: isSelected ? info.color : '#6080aa' }}>
                        {info.name}
                      </h3>
                      <p className="text-[8px] text-[#6080aa] text-center leading-tight">{info.desc}</p>
                    </button>
                  );
                })}
              </div>

              {/* PEER SHIP */}
              {peerConnected && (
                <div className="mt-2">
                  <div className="text-[10px] font-mono text-[#6080aa] text-center tracking-wider mb-1">
                    {room?.isHost ? '🎮 PLAYER 2' : '👑 HOST'}
                  </div>
                  <div className="flex items-center justify-center gap-3 py-3 px-5 rounded-xl"
                    style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.08)' }}>
                    <ShipCanvas shipType={peerShip} />
                    <div>
                      <span className="font-bold font-mono text-sm" style={{ color: SHIP_INFO[peerShip]?.color || '#fff' }}>
                        {SHIP_INFO[peerShip]?.name || 'Unknown'}
                      </span>
                      <span className="text-[#39ff14] text-xs ml-2 font-mono">ONLINE</span>
                      <p className="text-[9px] text-[#6080aa] font-mono mt-0.5">{SHIP_INFO[peerShip]?.stats}</p>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Right column: Map + Chat */}
            <div className="w-full lg:w-80 flex flex-col gap-3">
              {/* Map selection */}
              <div>
                <div className="text-[10px] font-mono text-[#6080aa] text-center tracking-wider mb-1">
                  🗺️ MAPA {!room?.isHost && '(escolhido pelo host)'}
                </div>
                <div className="grid grid-cols-2 gap-2">
                  {MAPS.map(m => (
                    <button key={m.id} 
                      onClick={() => { if (room?.isHost) setSelectedMap(m.id); }}
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

              {/* Chat */}
              <LobbyChat 
                messages={chatMessages} 
                onSend={handleSendChat}
                isHost={room?.isHost ?? false}
              />
            </div>
          </div>

          {/* Action buttons */}
          <div className="flex gap-3 mt-2">
            <button onClick={handleLeave}
              className="py-3 px-6 text-sm font-bold rounded-lg text-[#ff4060] border border-[#ff4060]/30 font-mono transition-all hover:border-[#ff4060]"
              style={{ background: 'rgba(255,64,96,0.05)' }}>
              Sair
            </button>
            {room?.isHost && (
              <button onClick={handleStart} disabled={!peerConnected || countdown !== null}
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
