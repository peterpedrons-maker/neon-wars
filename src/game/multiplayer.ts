// Multiplayer system using Supabase Realtime Broadcast
import { supabase } from '@/integrations/supabase/client';
import { RealtimeChannel } from '@supabase/supabase-js';

export interface RoomInfo {
  roomCode: string;
  isHost: boolean;
  playerId: string;
}

export interface CoopPlayerState {
  x: number;
  y: number;
  angle: number;
  hp: number;
  maxHp: number;
  alive: boolean;
  shipClass: string;
  shieldTimer: number;
  invincibleTimer: number;
  shooting: boolean;
}

export interface CoopGameSync {
  // Host sends full lightweight state
  enemies: Array<{ x: number; y: number; type: string; hp: number; maxHp: number; radius: number; alive: boolean }>;
  projectiles: Array<{ x: number; y: number; vx: number; vy: number; fromPlayer: boolean; color: string; alive: boolean }>;
  wave: number;
  score: number;
  hostPlayer: CoopPlayerState;
}

let channel: RealtimeChannel | null = null;
let currentRoom: RoomInfo | null = null;

function generateRoomCode(): string {
  const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
  let code = '';
  for (let i = 0; i < 5; i++) code += chars[Math.floor(Math.random() * chars.length)];
  return code;
}

function generatePlayerId(): string {
  return 'p_' + Math.random().toString(36).substring(2, 10);
}

export function createRoom(): RoomInfo {
  const room: RoomInfo = {
    roomCode: generateRoomCode(),
    isHost: true,
    playerId: generatePlayerId(),
  };
  currentRoom = room;
  return room;
}

export function joinRoom(roomCode: string): RoomInfo {
  const room: RoomInfo = {
    roomCode: roomCode.toUpperCase(),
    isHost: false,
    playerId: generatePlayerId(),
  };
  currentRoom = room;
  return room;
}

export function connectToRoom(
  room: RoomInfo,
  onPeerJoin: () => void,
  onPeerLeave: () => void,
  onPeerState: (state: CoopPlayerState) => void,
  onGameSync: (sync: CoopGameSync) => void,
  onStartGame: (data: { mapId: string; hostClass: string }) => void,
): RealtimeChannel {
  if (channel) {
    supabase.removeChannel(channel);
  }

  channel = supabase.channel(`neonwars_${room.roomCode}`, {
    config: { broadcast: { self: false } },
  });

  channel
    .on('broadcast', { event: 'player_join' }, () => onPeerJoin())
    .on('broadcast', { event: 'player_leave' }, () => onPeerLeave())
    .on('broadcast', { event: 'player_state' }, ({ payload }) => onPeerState(payload as CoopPlayerState))
    .on('broadcast', { event: 'game_sync' }, ({ payload }) => onGameSync(payload as CoopGameSync))
    .on('broadcast', { event: 'start_game' }, ({ payload }) => onStartGame(payload as { mapId: string; hostClass: string }))
    .subscribe((status) => {
      if (status === 'SUBSCRIBED') {
        // Announce ourselves
        channel!.send({ type: 'broadcast', event: 'player_join', payload: { playerId: room.playerId, isHost: room.isHost } });
      }
    });

  return channel;
}

export function sendPlayerState(state: CoopPlayerState) {
  if (!channel) return;
  channel.send({ type: 'broadcast', event: 'player_state', payload: state });
}

export function sendGameSync(sync: CoopGameSync) {
  if (!channel) return;
  channel.send({ type: 'broadcast', event: 'game_sync', payload: sync });
}

export function sendStartGame(mapId: string, hostClass: string) {
  if (!channel) return;
  channel.send({ type: 'broadcast', event: 'start_game', payload: { mapId, hostClass } });
}

export function leaveRoom() {
  if (channel) {
    channel.send({ type: 'broadcast', event: 'player_leave', payload: { playerId: currentRoom?.playerId } });
    supabase.removeChannel(channel);
    channel = null;
  }
  currentRoom = null;
}

export function getCurrentRoom(): RoomInfo | null {
  return currentRoom;
}
