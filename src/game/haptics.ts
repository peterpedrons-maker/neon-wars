const STORAGE_KEY = 'neonwars_haptics_enabled';

function isSupported() {
  return typeof navigator !== 'undefined' && typeof navigator.vibrate === 'function';
}

export function isHapticsEnabled(): boolean {
  if (!isSupported()) return false;
  const v = localStorage.getItem(STORAGE_KEY);
  return v === null ? true : v === '1';
}

export function setHapticsEnabled(enabled: boolean) {
  localStorage.setItem(STORAGE_KEY, enabled ? '1' : '0');
}

function vibrate(pattern: number | number[]) {
  if (!isHapticsEnabled()) return;
  try {
    navigator.vibrate(pattern);
  } catch {
    // Some browsers throw if called outside a user gesture context; ignore.
  }
}

export const haptics = {
  hit: () => vibrate(12),
  playerDamaged: () => vibrate(35),
  playerDeath: () => vibrate([0, 60, 40, 90]),
  levelUp: () => vibrate([0, 20, 40, 20]),
  bossKill: () => vibrate([0, 50, 60, 50, 60, 90]),
  waveComplete: () => vibrate(25),
  milestone: () => vibrate([0, 15, 30, 15]),
};
