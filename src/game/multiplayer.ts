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
  enemies: Array<{ x: number; y: number; type: string; hp: number; maxHp: number; radius: number; alive: boolean }>;
  projectiles: Array<{ x: number; y: number; vx: number; vy: number; fromPlayer: boolean; color: string; alive: boolean }>;
  wave: number;
  score: number;
  hostPlayer: CoopPlayerState;
}

export interface LobbyState {
  shipClass: string;
  mapId: string;
  playerId: string;
  isHost: boolean;
}

export interface ChatMessage {
  from: string;
  text: string;
  isHost: boolean;
  timestamp: number;
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

export interface RoomCallbacks {
  onPeerJoin: () => void;
  onPeerLeave: () => void;
  onPeerState: (state: CoopPlayerState) => void;
  onGameSync: (sync: CoopGameSync) => void;
  onStartGame: (data: { mapId: string; hostClass: string }) => void;
  onCountdown: (count: number) => void;
  onConfirm: () => void;
  onLobbyState: (state: LobbyState) => void;
  onChat: (msg: ChatMessage) => void;
}

export function connectToRoom(
  room: RoomInfo,
  callbacks: RoomCallbacks,
): RealtimeChannel {
  if (channel) {
    supabase.removeChannel(channel);
  }

  channel = supabase.channel(`neonwars_${room.roomCode}`, {
    config: { broadcast: { self: false } },
  });

  channel
    .on('broadcast', { event: 'player_join' }, ({ payload }) => {
      callbacks.onPeerJoin();
      // When we receive a join, send back an ack so the other side knows we're here
      channel!.send({ type: 'broadcast', event: 'player_ack', payload: { playerId: room.playerId, isHost: room.isHost } });
    })
    .on('broadcast', { event: 'player_ack' }, () => {
      // Receiving an ack means the other player is already in the room
      callbacks.onPeerJoin();
    })
    .on('broadcast', { event: 'player_leave' }, () => callbacks.onPeerLeave())
    .on('broadcast', { event: 'player_state' }, ({ payload }) => callbacks.onPeerState(payload as CoopPlayerState))
    .on('broadcast', { event: 'game_sync' }, ({ payload }) => callbacks.onGameSync(payload as CoopGameSync))
    .on('broadcast', { event: 'start_game' }, ({ payload }) => callbacks.onStartGame(payload as { mapId: string; hostClass: string }))
    .on('broadcast', { event: 'countdown' }, ({ payload }) => callbacks.onCountdown((payload as any).count))
    .on('broadcast', { event: 'guest_confirm' }, () => callbacks.onConfirm())
    .on('broadcast', { event: 'lobby_state' }, ({ payload }) => callbacks.onLobbyState(payload as LobbyState))
    .on('broadcast', { event: 'chat' }, ({ payload }) => callbacks.onChat(payload as ChatMessage))
    .subscribe((status) => {
      if (status === 'SUBSCRIBED') {
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

export function sendCountdown(count: number) {
  if (!channel) return;
  channel.send({ type: 'broadcast', event: 'countdown', payload: { count } });
}

export function sendGuestConfirm() {
  if (!channel) return;
  channel.send({ type: 'broadcast', event: 'guest_confirm', payload: {} });
}

export function sendLobbyState(state: LobbyState) {
  if (!channel) return;
  channel.send({ type: 'broadcast', event: 'lobby_state', payload: state });
}

export function sendChat(msg: ChatMessage) {
  if (!channel) return;
  channel.send({ type: 'broadcast', event: 'chat', payload: msg });
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
