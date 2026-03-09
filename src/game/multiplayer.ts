// Multiplayer system using Supabase Realtime Broadcast
import { supabase } from '@/integrations/supabase/client';
import { RealtimeChannel } from '@supabase/supabase-js';

export interface RoomInfo {
  roomCode: string;
  isHost: boolean;
  playerId: string;
  isPublic?: boolean;
}

export interface CoopPlayerState {
  x: number;
  y: number;
  angle: number;
  hp: number;
  maxHp: number;
  alive: boolean;
  dead: boolean;
  shipClass: string;
  shieldTimer: number;
  invincibleTimer: number;
  shooting: boolean;
  playerId?: string;
  playerLabel?: string;
  emote?: { text: string; timer: number };
}

export interface CoopGameSync {
  enemies: Array<{ x: number; y: number; type: string; hp: number; maxHp: number; radius: number; alive: boolean }>;
  projectiles: Array<{ x: number; y: number; vx: number; vy: number; fromPlayer: boolean; color: string; alive: boolean }>;
  wave: number;
  score: number;
  xp: number;
  level: number;
  xpToNext: number;
  hostPlayer: CoopPlayerState;
  playerCount?: number;
}

export interface LobbyState {
  shipClass: string;
  mapId: string;
  playerId: string;
  isHost: boolean;
  playerLabel?: string;
}

export interface ChatMessage {
  from: string;
  text: string;
  isHost: boolean;
  timestamp: number;
}

export interface PublicRoomInfo {
  id: string;
  room_code: string;
  host_name: string;
  host_ship: string;
  map_id: string;
  player_count: number;
  max_players: number;
  status: string;
  created_at: string;
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

export function createRoom(isPublic: boolean = false): RoomInfo {
  const room: RoomInfo = {
    roomCode: generateRoomCode(),
    isHost: true,
    playerId: generatePlayerId(),
    isPublic,
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

// Public room management
export async function createPublicRoom(hostName: string, hostShip: string, mapId: string, roomCode: string): Promise<void> {
  await supabase.from('public_rooms').insert({
    room_code: roomCode,
    host_name: hostName,
    host_ship: hostShip,
    map_id: mapId,
    player_count: 1,
    max_players: 6,
    status: 'waiting',
  });
}

export async function fetchPublicRooms(): Promise<PublicRoomInfo[]> {
  const { data } = await supabase
    .from('public_rooms')
    .select('*')
    .eq('status', 'waiting')
    .lt('player_count', 6)
    .order('created_at', { ascending: false })
    .limit(20);
  return (data || []) as PublicRoomInfo[];
}

export async function updatePublicRoomPlayerCount(roomCode: string, count: number): Promise<void> {
  await supabase.from('public_rooms').update({ player_count: count, updated_at: new Date().toISOString() }).eq('room_code', roomCode);
}

export async function setPublicRoomStatus(roomCode: string, status: string): Promise<void> {
  await supabase.from('public_rooms').update({ status, updated_at: new Date().toISOString() }).eq('room_code', roomCode);
}

export async function deletePublicRoom(roomCode: string): Promise<void> {
  await supabase.from('public_rooms').delete().eq('room_code', roomCode);
}

export interface RoomCallbacks {
  onPeerJoin: (playerId?: string) => void;
  onPeerLeave: (playerId?: string) => void;
  onPeerState: (state: CoopPlayerState) => void;
  onGameSync: (sync: CoopGameSync) => void;
  onStartGame: (data: { mapId: string; hostClass: string }) => void;
  onCountdown: (count: number) => void;
  onConfirm: (playerId?: string) => void;
  onLobbyState: (state: LobbyState) => void;
  onChat: (msg: ChatMessage) => void;
  onLevelUp: (level: number) => void;
  onUpgradeDone: () => void;
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
      callbacks.onPeerJoin(payload?.playerId);
      channel!.send({ type: 'broadcast', event: 'player_ack', payload: { playerId: room.playerId, isHost: room.isHost } });
    })
    .on('broadcast', { event: 'player_ack' }, ({ payload }) => {
      callbacks.onPeerJoin(payload?.playerId);
    })
    .on('broadcast', { event: 'player_leave' }, ({ payload }) => callbacks.onPeerLeave(payload?.playerId))
    .on('broadcast', { event: 'player_state' }, ({ payload }) => callbacks.onPeerState(payload as CoopPlayerState))
    .on('broadcast', { event: 'game_sync' }, ({ payload }) => callbacks.onGameSync(payload as CoopGameSync))
    .on('broadcast', { event: 'start_game' }, ({ payload }) => callbacks.onStartGame(payload as { mapId: string; hostClass: string }))
    .on('broadcast', { event: 'countdown' }, ({ payload }) => callbacks.onCountdown((payload as any).count))
    .on('broadcast', { event: 'guest_confirm' }, ({ payload }) => callbacks.onConfirm((payload as any)?.playerId))
    .on('broadcast', { event: 'lobby_state' }, ({ payload }) => callbacks.onLobbyState(payload as LobbyState))
    .on('broadcast', { event: 'chat' }, ({ payload }) => callbacks.onChat(payload as ChatMessage))
    .on('broadcast', { event: 'level_up' }, ({ payload }) => callbacks.onLevelUp((payload as any).level))
    .on('broadcast', { event: 'upgrade_done' }, () => callbacks.onUpgradeDone())
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

export function sendGuestConfirm(playerId?: string) {
  if (!channel) return;
  channel.send({ type: 'broadcast', event: 'guest_confirm', payload: { playerId } });
}

export function sendLobbyState(state: LobbyState) {
  if (!channel) return;
  channel.send({ type: 'broadcast', event: 'lobby_state', payload: state });
}

export function sendChat(msg: ChatMessage) {
  if (!channel) return;
  channel.send({ type: 'broadcast', event: 'chat', payload: msg });
}

export function sendLevelUp(level: number) {
  if (!channel) return;
  channel.send({ type: 'broadcast', event: 'level_up', payload: { level } });
}

export function sendUpgradeDone() {
  if (!channel) return;
  channel.send({ type: 'broadcast', event: 'upgrade_done', payload: {} });
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
