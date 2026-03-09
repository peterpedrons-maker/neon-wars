import type { EnemyType } from './types';

// Synthesized retro arcade sound effects + procedural music using Web Audio API

let audioCtx: AudioContext | null = null;
let musicGain: GainNode | null = null;
let musicPlaying = false;
let musicIntensity = 1;

// ===== GAME MUSIC ROUTING (map + boss themes) =====

type MelodyStep = [number, number]; // [scaleIndex, durationIn16ths]

type KickStyle = 'four' | 'half' | 'broken' | 'dnb';

type HatStyle = 'tight' | 'dense' | 'shuffle';

interface MusicProfile {
  id: string;
  bpm: number;
  keyCycle: number[]; // MIDI roots
  keyChangeEveryMeasures: number;
  progressions: number[][][][]; // pool of chord progressions
  melodyPhrases: Array<Array<MelodyStep>>;
  scale: number[];
  bassRhythms: number[][];
  masterGain: number;
  kickStyle?: KickStyle;
  hatStyle?: HatStyle;
  sectionFeelOverride?: number; // when set, forces a specific "sectionFeel" in scheduleNextMeasure
}

let activeMapId = 'neon-grid';
let activeBossType: EnemyType | null = null;

let currentProfile: MusicProfile | null = null;
let pendingProfile: MusicProfile | null = null;
let pendingProfileReset = false;

function queueProfileSwitch(profile: MusicProfile) {
  if (currentProfile?.id === profile.id) return;
  pendingProfile = profile;
  pendingProfileReset = true;
}

export function setMapMusic(mapId: string) {
  activeMapId = mapId;
  if (!activeBossType) {
    const p = getActiveGameProfile();
    queueProfileSwitch(p);
  }
}

export function setBossMusic(bossType: EnemyType | null) {
  if (activeBossType === bossType) return;
  activeBossType = bossType;
  const p = getActiveGameProfile();
  queueProfileSwitch(p);
}

function getCtx(): AudioContext {
  if (!audioCtx) {
    audioCtx = new AudioContext();
  }
  if (audioCtx.state === 'suspended') {
    audioCtx.resume();
  }
  return audioCtx;
}

export function initAudio() {
  getCtx();
}

// ===== SOUND EFFECTS =====

export function playShoot(pitch: number = 800) {
  try {
    const ctx = getCtx();
    const osc = ctx.createOscillator();
    const osc2 = ctx.createOscillator();
    const osc3 = ctx.createOscillator();
    const gain = ctx.createGain();
    const filter = ctx.createBiquadFilter();
    const dist = ctx.createWaveShaper();
    
    // Subtle distortion for crunch
    const curve = new Float32Array(256);
    for (let i = 0; i < 256; i++) { const x = (i / 128) - 1; curve[i] = (Math.PI + 3) * x / (Math.PI + 3 * Math.abs(x)); }
    dist.curve = curve;
    
    osc.type = 'square';
    osc.frequency.setValueAtTime(pitch, ctx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(pitch * 0.25, ctx.currentTime + 0.12);
    osc2.type = 'sine';
    osc2.frequency.setValueAtTime(pitch * 1.5, ctx.currentTime);
    osc2.frequency.exponentialRampToValueAtTime(200, ctx.currentTime + 0.07);
    osc3.type = 'triangle';
    osc3.frequency.setValueAtTime(pitch * 0.5, ctx.currentTime);
    osc3.frequency.exponentialRampToValueAtTime(100, ctx.currentTime + 0.1);
    filter.type = 'lowpass';
    filter.frequency.setValueAtTime(4000, ctx.currentTime);
    filter.frequency.exponentialRampToValueAtTime(400, ctx.currentTime + 0.12);
    filter.Q.setValueAtTime(2, ctx.currentTime);
    gain.gain.setValueAtTime(0.08, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.12);
    osc.connect(dist);
    osc2.connect(filter);
    osc3.connect(filter);
    dist.connect(filter);
    filter.connect(gain).connect(ctx.destination);
    osc.start(ctx.currentTime); osc.stop(ctx.currentTime + 0.12);
    osc2.start(ctx.currentTime); osc2.stop(ctx.currentTime + 0.07);
    osc3.start(ctx.currentTime); osc3.stop(ctx.currentTime + 0.1);
  } catch {}
}

export function playShootPhantom() {
  try {
    const ctx = getCtx();
    const osc = ctx.createOscillator();
    const osc2 = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = 'sine';
    osc.frequency.setValueAtTime(900, ctx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(400, ctx.currentTime + 0.12);
    osc2.type = 'triangle';
    osc2.frequency.setValueAtTime(1200, ctx.currentTime);
    osc2.frequency.exponentialRampToValueAtTime(300, ctx.currentTime + 0.08);
    osc2.detune.setValueAtTime(20, ctx.currentTime);
    gain.gain.setValueAtTime(0.06, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.12);
    osc.connect(gain).connect(ctx.destination);
    osc2.connect(gain);
    osc.start(ctx.currentTime); osc.stop(ctx.currentTime + 0.12);
    osc2.start(ctx.currentTime); osc2.stop(ctx.currentTime + 0.08);
  } catch {}
}

export function playShootInterceptor() {
  try {
    const ctx = getCtx();
    for (let i = 0; i < 2; i++) {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = 'square';
      osc.frequency.setValueAtTime(1400 + i * 200, ctx.currentTime + i * 0.02);
      osc.frequency.exponentialRampToValueAtTime(400, ctx.currentTime + i * 0.02 + 0.05);
      gain.gain.setValueAtTime(0.04, ctx.currentTime + i * 0.02);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + i * 0.02 + 0.05);
      osc.connect(gain).connect(ctx.destination);
      osc.start(ctx.currentTime + i * 0.02);
      osc.stop(ctx.currentTime + i * 0.02 + 0.05);
    }
  } catch {}
}

export function playShootTitan() {
  try {
    const ctx = getCtx();
    const osc = ctx.createOscillator();
    const osc2 = ctx.createOscillator();
    const noise = ctx.createOscillator();
    const gain = ctx.createGain();
    const noiseGain = ctx.createGain();
    osc.type = 'sawtooth';
    osc.frequency.setValueAtTime(120, ctx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(40, ctx.currentTime + 0.2);
    osc2.type = 'square';
    osc2.frequency.setValueAtTime(80, ctx.currentTime);
    osc2.frequency.exponentialRampToValueAtTime(30, ctx.currentTime + 0.18);
    noise.type = 'sawtooth';
    noise.frequency.setValueAtTime(60 + Math.random() * 40, ctx.currentTime);
    noise.detune.setValueAtTime(1200, ctx.currentTime);
    gain.gain.setValueAtTime(0.1, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.2);
    noiseGain.gain.setValueAtTime(0.05, ctx.currentTime);
    noiseGain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.15);
    osc.connect(gain).connect(ctx.destination);
    osc2.connect(gain);
    noise.connect(noiseGain).connect(ctx.destination);
    osc.start(ctx.currentTime); osc.stop(ctx.currentTime + 0.2);
    osc2.start(ctx.currentTime); osc2.stop(ctx.currentTime + 0.18);
    noise.start(ctx.currentTime); noise.stop(ctx.currentTime + 0.15);
  } catch {}
}

export function playExplosion(big: boolean = false) {
  try {
    const ctx = getCtx();
    const dur = big ? 0.6 : 0.25;
    const vol = big ? 0.14 : 0.08;
    
    // Sub impact thump
    const sub = ctx.createOscillator();
    const subG = ctx.createGain();
    sub.type = 'sine';
    sub.frequency.setValueAtTime(big ? 80 : 100, ctx.currentTime);
    sub.frequency.exponentialRampToValueAtTime(20, ctx.currentTime + dur * 0.6);
    subG.gain.setValueAtTime(vol * 1.3, ctx.currentTime);
    subG.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + dur * 0.7);
    sub.connect(subG).connect(ctx.destination);
    sub.start(ctx.currentTime); sub.stop(ctx.currentTime + dur * 0.8);
    
    // Noise burst layers
    for (let i = 0; i < (big ? 5 : 3); i++) {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      const filter = ctx.createBiquadFilter();
      osc.type = i % 2 === 0 ? 'sawtooth' : 'square';
      osc.frequency.setValueAtTime(60 + Math.random() * 120, ctx.currentTime + i * 0.012);
      osc.frequency.exponentialRampToValueAtTime(12 + Math.random() * 10, ctx.currentTime + dur);
      osc.detune.setValueAtTime(Math.random() * 400 - 200, ctx.currentTime);
      filter.type = 'lowpass';
      filter.frequency.setValueAtTime(big ? 3000 : 2000, ctx.currentTime);
      filter.frequency.exponentialRampToValueAtTime(80, ctx.currentTime + dur);
      filter.Q.setValueAtTime(1.5, ctx.currentTime);
      gain.gain.setValueAtTime(vol * 0.7, ctx.currentTime + i * 0.012);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + dur);
      osc.connect(filter).connect(gain).connect(ctx.destination);
      osc.start(ctx.currentTime + i * 0.012);
      osc.stop(ctx.currentTime + dur + i * 0.012);
    }
    
    if (big) {
      // Metallic ring
      const ring = ctx.createOscillator();
      const rg = ctx.createGain();
      const rf = ctx.createBiquadFilter();
      ring.type = 'sine';
      ring.frequency.setValueAtTime(350, ctx.currentTime);
      ring.frequency.exponentialRampToValueAtTime(60, ctx.currentTime + 0.4);
      rf.type = 'bandpass';
      rf.frequency.value = 200;
      rf.Q.value = 5;
      rg.gain.setValueAtTime(0.06, ctx.currentTime);
      rg.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.4);
      ring.connect(rf).connect(rg).connect(ctx.destination);
      ring.start(ctx.currentTime); ring.stop(ctx.currentTime + 0.45);
      
      // Crackle tail
      for (let j = 0; j < 3; j++) {
        const cr = ctx.createOscillator();
        const cg = ctx.createGain();
        cr.type = 'sawtooth';
        cr.frequency.setValueAtTime(2000 + Math.random() * 3000, ctx.currentTime + 0.15 + j * 0.06);
        cr.detune.setValueAtTime(Math.random() * 2400, ctx.currentTime);
        cg.gain.setValueAtTime(0.02, ctx.currentTime + 0.15 + j * 0.06);
        cg.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.3 + j * 0.06);
        cr.connect(cg).connect(ctx.destination);
        cr.start(ctx.currentTime + 0.15 + j * 0.06); cr.stop(ctx.currentTime + 0.35 + j * 0.06);
      }
    }
  } catch {}
}

export function playCombo(multiplier: number) {
  try {
    const ctx = getCtx();
    const baseFreq = 500 + multiplier * 60;
    for (let i = 0; i < 4; i++) {
      const osc = ctx.createOscillator();
      const osc2 = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = 'sine';
      osc2.type = 'triangle';
      const freq = baseFreq + i * 180;
      osc.frequency.setValueAtTime(freq, ctx.currentTime + i * 0.035);
      osc2.frequency.setValueAtTime(freq * 2, ctx.currentTime + i * 0.035);
      gain.gain.setValueAtTime(0.05, ctx.currentTime + i * 0.035);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + i * 0.035 + 0.12);
      osc.connect(gain).connect(ctx.destination);
      osc2.connect(gain);
      osc.start(ctx.currentTime + i * 0.035); osc.stop(ctx.currentTime + i * 0.035 + 0.12);
      osc2.start(ctx.currentTime + i * 0.035); osc2.stop(ctx.currentTime + i * 0.035 + 0.12);
    }
  } catch {}
}

export function playPowerUp() {
  try {
    const ctx = getCtx();
    // Magical ascending chime
    const notes = [500, 700, 900, 1200, 1500];
    notes.forEach((freq, i) => {
      const osc = ctx.createOscillator();
      const osc2 = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = 'sine';
      osc2.type = 'triangle';
      osc.frequency.setValueAtTime(freq, ctx.currentTime + i * 0.04);
      osc2.frequency.setValueAtTime(freq * 2, ctx.currentTime + i * 0.04);
      gain.gain.setValueAtTime(0.07, ctx.currentTime + i * 0.04);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + i * 0.04 + 0.2);
      osc.connect(gain).connect(ctx.destination);
      osc2.connect(gain);
      osc.start(ctx.currentTime + i * 0.04); osc.stop(ctx.currentTime + i * 0.04 + 0.2);
      osc2.start(ctx.currentTime + i * 0.04); osc2.stop(ctx.currentTime + i * 0.04 + 0.2);
    });
    // Sparkle shimmer
    const shimmer = ctx.createOscillator();
    const sg = ctx.createGain();
    shimmer.type = 'sine';
    shimmer.frequency.setValueAtTime(3000, ctx.currentTime + 0.15);
    shimmer.frequency.exponentialRampToValueAtTime(1500, ctx.currentTime + 0.4);
    sg.gain.setValueAtTime(0.03, ctx.currentTime + 0.15);
    sg.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.4);
    shimmer.connect(sg).connect(ctx.destination);
    shimmer.start(ctx.currentTime + 0.15); shimmer.stop(ctx.currentTime + 0.42);
  } catch {}
}

export function playSpecial() {
  try {
    const ctx = getCtx();
    for (let i = 0; i < 6; i++) {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = i % 2 === 0 ? 'sine' : 'square';
      osc.frequency.setValueAtTime(200 + i * 180, ctx.currentTime + i * 0.025);
      osc.frequency.exponentialRampToValueAtTime(60, ctx.currentTime + 0.35);
      gain.gain.setValueAtTime(0.05, ctx.currentTime + i * 0.025);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.35);
      osc.connect(gain).connect(ctx.destination);
      osc.start(ctx.currentTime + i * 0.025);
      osc.stop(ctx.currentTime + 0.4);
    }
  } catch {}
}

export function playHit() {
  try {
    const ctx = getCtx();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = 'square';
    osc.frequency.setValueAtTime(250, ctx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(80, ctx.currentTime + 0.05);
    gain.gain.setValueAtTime(0.05, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.05);
    osc.connect(gain).connect(ctx.destination);
    osc.start(ctx.currentTime); osc.stop(ctx.currentTime + 0.05);
  } catch {}
}

export function playDamage() {
  try {
    const ctx = getCtx();
    const osc = ctx.createOscillator();
    const osc2 = ctx.createOscillator();
    const osc3 = ctx.createOscillator();
    const gain = ctx.createGain();
    const filter = ctx.createBiquadFilter();
    osc.type = 'sawtooth';
    osc.frequency.setValueAtTime(400, ctx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(35, ctx.currentTime + 0.3);
    osc2.type = 'square';
    osc2.frequency.setValueAtTime(250, ctx.currentTime);
    osc2.frequency.exponentialRampToValueAtTime(25, ctx.currentTime + 0.25);
    osc3.type = 'sawtooth';
    osc3.frequency.setValueAtTime(180, ctx.currentTime);
    osc3.frequency.exponentialRampToValueAtTime(20, ctx.currentTime + 0.2);
    osc3.detune.setValueAtTime(600, ctx.currentTime);
    filter.type = 'lowpass';
    filter.frequency.setValueAtTime(2500, ctx.currentTime);
    filter.frequency.exponentialRampToValueAtTime(200, ctx.currentTime + 0.25);
    gain.gain.setValueAtTime(0.11, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.3);
    osc.connect(filter);
    osc2.connect(filter);
    osc3.connect(filter);
    filter.connect(gain).connect(ctx.destination);
    osc.start(ctx.currentTime); osc.stop(ctx.currentTime + 0.3);
    osc2.start(ctx.currentTime); osc2.stop(ctx.currentTime + 0.25);
    osc3.start(ctx.currentTime); osc3.stop(ctx.currentTime + 0.2);
  } catch {}
}

export function playGameOver() {
  try {
    const ctx = getCtx();
    const notes = [500, 420, 350, 260, 180, 100, 60];
    notes.forEach((freq, i) => {
      const osc = ctx.createOscillator();
      const osc2 = ctx.createOscillator();
      const osc3 = ctx.createOscillator();
      const gain = ctx.createGain();
      const filter = ctx.createBiquadFilter();
      osc.type = 'sine';
      osc2.type = 'triangle';
      osc3.type = 'sawtooth';
      osc.frequency.setValueAtTime(freq, ctx.currentTime + i * 0.2);
      osc2.frequency.setValueAtTime(freq * 0.5, ctx.currentTime + i * 0.2);
      osc3.frequency.setValueAtTime(freq * 0.25, ctx.currentTime + i * 0.2);
      osc3.detune.setValueAtTime(50, ctx.currentTime + i * 0.2);
      filter.type = 'lowpass';
      filter.frequency.setValueAtTime(2000, ctx.currentTime + i * 0.2);
      filter.frequency.exponentialRampToValueAtTime(300, ctx.currentTime + i * 0.2 + 0.4);
      gain.gain.setValueAtTime(0.09, ctx.currentTime + i * 0.2);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + i * 0.2 + 0.4);
      osc.connect(filter);
      osc2.connect(filter);
      osc3.connect(filter);
      filter.connect(gain).connect(ctx.destination);
      osc.start(ctx.currentTime + i * 0.2); osc.stop(ctx.currentTime + i * 0.2 + 0.4);
      osc2.start(ctx.currentTime + i * 0.2); osc2.stop(ctx.currentTime + i * 0.2 + 0.4);
      osc3.start(ctx.currentTime + i * 0.2); osc3.stop(ctx.currentTime + i * 0.2 + 0.4);
    });
    // Final sub rumble
    const sub = ctx.createOscillator();
    const sg = ctx.createGain();
    sub.type = 'sine';
    sub.frequency.setValueAtTime(40, ctx.currentTime + 1.2);
    sub.frequency.exponentialRampToValueAtTime(15, ctx.currentTime + 2.0);
    sg.gain.setValueAtTime(0.12, ctx.currentTime + 1.2);
    sg.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 2.0);
    sub.connect(sg).connect(ctx.destination);
    sub.start(ctx.currentTime + 1.2); sub.stop(ctx.currentTime + 2.1);
  } catch {}
}

export function playWaveComplete() {
  try {
    const ctx = getCtx();
    // Triumphant fanfare
    const notes = [500, 600, 750, 900, 1100, 1400];
    notes.forEach((freq, i) => {
      const osc = ctx.createOscillator();
      const osc2 = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = i < 3 ? 'sine' : 'triangle';
      osc2.type = 'square';
      osc.frequency.setValueAtTime(freq, ctx.currentTime + i * 0.06);
      osc2.frequency.setValueAtTime(freq * 0.5, ctx.currentTime + i * 0.06);
      gain.gain.setValueAtTime(0.08, ctx.currentTime + i * 0.06);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + i * 0.06 + 0.3);
      osc.connect(gain).connect(ctx.destination);
      osc2.connect(gain);
      osc.start(ctx.currentTime + i * 0.06);
      osc.stop(ctx.currentTime + i * 0.06 + 0.3);
      osc2.start(ctx.currentTime + i * 0.06);
      osc2.stop(ctx.currentTime + i * 0.06 + 0.3);
    });
    // Shimmering tail
    const shim = ctx.createOscillator();
    const sg = ctx.createGain();
    shim.type = 'sine';
    shim.frequency.setValueAtTime(2000, ctx.currentTime + 0.3);
    shim.frequency.exponentialRampToValueAtTime(800, ctx.currentTime + 0.7);
    sg.gain.setValueAtTime(0.04, ctx.currentTime + 0.3);
    sg.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.7);
    shim.connect(sg).connect(ctx.destination);
    shim.start(ctx.currentTime + 0.3); shim.stop(ctx.currentTime + 0.72);
  } catch {}
}

// ===== UI SOUND EFFECTS =====

export function playClick() {
  try {
    const ctx = getCtx();
    const osc = ctx.createOscillator();
    const osc2 = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = 'sine';
    osc.frequency.setValueAtTime(1200, ctx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(800, ctx.currentTime + 0.06);
    osc2.type = 'triangle';
    osc2.frequency.setValueAtTime(2400, ctx.currentTime);
    osc2.frequency.exponentialRampToValueAtTime(1600, ctx.currentTime + 0.04);
    gain.gain.setValueAtTime(0.06, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.08);
    osc.connect(gain).connect(ctx.destination);
    osc2.connect(gain);
    osc.start(ctx.currentTime); osc.stop(ctx.currentTime + 0.08);
    osc2.start(ctx.currentTime); osc2.stop(ctx.currentTime + 0.06);
  } catch {}
}

export function playHover() {
  try {
    const ctx = getCtx();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = 'sine';
    osc.frequency.setValueAtTime(1800, ctx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(1400, ctx.currentTime + 0.03);
    gain.gain.setValueAtTime(0.02, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.04);
    osc.connect(gain).connect(ctx.destination);
    osc.start(ctx.currentTime); osc.stop(ctx.currentTime + 0.04);
  } catch {}
}

export function playBack() {
  try {
    const ctx = getCtx();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = 'sine';
    osc.frequency.setValueAtTime(600, ctx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(400, ctx.currentTime + 0.1);
    gain.gain.setValueAtTime(0.05, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.1);
    osc.connect(gain).connect(ctx.destination);
    osc.start(ctx.currentTime); osc.stop(ctx.currentTime + 0.1);
  } catch {}
}

export function playPurchase() {
  try {
    const ctx = getCtx();
    const notes = [800, 1000, 1300, 1600];
    notes.forEach((freq, i) => {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(freq, ctx.currentTime + i * 0.05);
      gain.gain.setValueAtTime(0.06, ctx.currentTime + i * 0.05);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + i * 0.05 + 0.12);
      osc.connect(gain).connect(ctx.destination);
      osc.start(ctx.currentTime + i * 0.05); osc.stop(ctx.currentTime + i * 0.05 + 0.12);
    });
  } catch {}
}

export function playError() {
  try {
    const ctx = getCtx();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = 'square';
    osc.frequency.setValueAtTime(200, ctx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(100, ctx.currentTime + 0.15);
    gain.gain.setValueAtTime(0.04, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.15);
    osc.connect(gain).connect(ctx.destination);
    osc.start(ctx.currentTime); osc.stop(ctx.currentTime + 0.15);
  } catch {}
}

export function playLevelUp() {
  try {
    const ctx = getCtx();
    const notes = [600, 800, 1000, 1200, 1500, 1800];
    notes.forEach((freq, i) => {
      const osc = ctx.createOscillator();
      const osc2 = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = 'sine';
      osc2.type = 'triangle';
      osc.frequency.setValueAtTime(freq, ctx.currentTime + i * 0.06);
      osc2.frequency.setValueAtTime(freq * 1.5, ctx.currentTime + i * 0.06);
      gain.gain.setValueAtTime(0.07, ctx.currentTime + i * 0.06);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + i * 0.06 + 0.25);
      osc.connect(gain).connect(ctx.destination);
      osc2.connect(gain);
      osc.start(ctx.currentTime + i * 0.06); osc.stop(ctx.currentTime + i * 0.06 + 0.25);
      osc2.start(ctx.currentTime + i * 0.06); osc2.stop(ctx.currentTime + i * 0.06 + 0.25);
    });
    // Shimmer
    const shim = ctx.createOscillator();
    const sg = ctx.createGain();
    shim.type = 'sine';
    shim.frequency.setValueAtTime(4000, ctx.currentTime + 0.25);
    shim.frequency.exponentialRampToValueAtTime(2000, ctx.currentTime + 0.6);
    sg.gain.setValueAtTime(0.03, ctx.currentTime + 0.25);
    sg.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.6);
    shim.connect(sg).connect(ctx.destination);
    shim.start(ctx.currentTime + 0.25); shim.stop(ctx.currentTime + 0.62);
  } catch {}
}

export function playNavigate() {
  try {
    const ctx = getCtx();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = 'sine';
    osc.frequency.setValueAtTime(900, ctx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(1200, ctx.currentTime + 0.06);
    gain.gain.setValueAtTime(0.04, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.08);
    osc.connect(gain).connect(ctx.destination);
    osc.start(ctx.currentTime); osc.stop(ctx.currentTime + 0.08);
  } catch {}
}

// ===== PREMIUM MUSIC ENGINE =====
// Multi-layered electronic music with proper song structure, FM synthesis, sidechaining

// --- Chord progressions (MIDI intervals from root) ---
const PROGS = [
  // Cinematic minor: i - bVI - bIII - bVII
  [[0,3,7,10],[8,12,15,19],[3,7,10,14],[10,14,17,21]],
  // Dark driving: i - iv - v - bVII
  [[0,3,7,10],[5,8,12,15],[7,10,14,17],[10,14,17,21]],
  // Euphoric trance: i - bVII - bVI - v
  [[0,3,7,12],[10,14,17,22],[8,12,15,20],[7,10,14,19]],
  // Epic build: i - bIII - iv - bVII
  [[0,3,7,12],[3,7,10,15],[5,8,12,17],[10,14,17,22]],
  // Synthwave: i - bVI - iv - v
  [[0,3,7,10],[8,12,15,19],[5,8,12,17],[7,10,14,17]],
  // Aggressive: i - bII - bVII - i(8va)
  [[0,3,7,10],[1,5,8,13],[10,14,17,22],[12,15,19,24]],
  // Extended Journey 1: i - v - bVI - bIII
  [[0,3,7,10],[7,10,14,19],[8,12,15,20],[3,7,10,15]],
  // Extended Journey 2: iv - i - bVII - bVI
  [[5,8,12,17],[0,3,7,12],[10,14,17,21],[8,12,15,19]],
];

// Catchy melody phrases [scaleIndex, durationIn16ths]
const MELODY_PHRASES = [
  // Soaring anthem
  [[0,2],[4,2],[7,4],[5,2],[4,2],[2,4],[0,2],[2,2],[4,4],[7,4]],
  // Driving staccato
  [[7,1],[7,1],[5,1],[4,1],[2,2],[0,1],[2,1],[4,2],[7,1],[9,1],[12,3],[7,2]],
  // Call and response
  [[0,2],[2,2],[4,4],[0,0],[7,2],[5,2],[4,4],[0,0]],
  // Ascending power
  [[0,1],[2,1],[4,2],[5,1],[7,1],[9,2],[7,1],[5,1],[4,2],[2,1],[0,1]],
  // Heroic leap
  [[0,3],[7,1],[12,2],[9,2],[7,1],[5,1],[4,2],[2,1],[0,1],[4,3]],
  // Funky groove
  [[0,1],[0,1],[4,1],[5,1],[7,2],[4,1],[2,1],[0,2],[7,1],[9,1],[7,1],[4,1]],
  // Emotional descent
  [[12,3],[9,1],[7,2],[5,2],[4,1],[2,1],[0,4],[2,2],[4,2]],
  // Trance gate
  [[7,1],[0,0],[7,1],[0,0],[5,1],[0,0],[4,1],[0,0],[2,1],[0,0],[4,1],[0,0],[7,1],[0,0],[9,1],[0,0]],
  // Cyberpunk run
  [[0,1],[12,1],[0,1],[10,1],[0,1],[9,1],[0,1],[7,1],[0,1],[5,1],[0,1],[4,1],[0,1],[2,1],[0,2]],
  // Mystic drift
  [[4,4],[7,2],[9,2],[12,4],[14,4],[12,2],[9,2],[7,8]],
];

// Bass patterns (16th note grid)
const BASS_RHYTHMS = [
  [1,0,0,1,0,0,1,0,1,0,0,1,0,0,1,0],
  [1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0],
  [1,0,0,1,0,1,0,0,1,0,0,1,0,1,0,0],
  [1,1,0,1,1,0,1,0,1,1,0,1,1,0,1,0],
  [1,0,0,0,1,0,0,1,0,0,1,0,0,0,1,0],
  [1,0,1,1,0,1,0,1,1,0,1,1,0,1,0,1], // Syncopated
  [1,0,0,0,0,0,1,0,0,0,1,0,0,0,0,0], // Sparse deep
];

let musicTimers: number[] = [];
let currentChordIndex = 0;
let currentProgIndex = 0;
let measureCount = 0;
let currentKey = 33;
let sectionCount = 0;
let compressor: DynamicsCompressorNode | null = null;
let reverbGain: GainNode | null = null;

function midiToFreq(midi: number): number {
  return 440 * Math.pow(2, (midi - 69) / 12);
}

function createReverb(ctx: AudioContext, output: AudioNode): GainNode {
  const wet = ctx.createGain();
  wet.gain.value = 0.22;
  const delays = [0.023, 0.041, 0.067, 0.097, 0.137, 0.191];
  const feedbacks = [0.4, 0.35, 0.3, 0.25, 0.2, 0.15];
  for (let i = 0; i < delays.length; i++) {
    const delay = ctx.createDelay(0.5);
    delay.delayTime.value = delays[i];
    const fb = ctx.createGain();
    fb.gain.value = feedbacks[i];
    const filter = ctx.createBiquadFilter();
    filter.type = 'lowpass';
    filter.frequency.value = 4000 - i * 500;
    wet.connect(delay).connect(filter).connect(fb).connect(delay);
    filter.connect(output);
  }
  return wet;
}

// FM synthesis helper
function playFMNote(ctx: AudioContext, dest: AudioNode, carrierFreq: number, modRatio: number, modDepth: number, t: number, dur: number, vol: number, type: OscillatorType = 'sine') {
  const carrier = ctx.createOscillator();
  const modulator = ctx.createOscillator();
  const modGain = ctx.createGain();
  const envGain = ctx.createGain();
  
  modulator.frequency.setValueAtTime(carrierFreq * modRatio, t);
  modGain.gain.setValueAtTime(modDepth, t);
  modGain.gain.exponentialRampToValueAtTime(modDepth * 0.1 + 1, t + dur * 0.8);
  modulator.connect(modGain).connect(carrier.frequency);
  
  carrier.type = type;
  carrier.frequency.setValueAtTime(carrierFreq, t);
  envGain.gain.setValueAtTime(0, t);
  envGain.gain.linearRampToValueAtTime(vol, t + 0.003);
  envGain.gain.exponentialRampToValueAtTime(0.001, t + dur);
  
  carrier.connect(envGain).connect(dest);
  carrier.start(t); carrier.stop(t + dur + 0.01);
  modulator.start(t); modulator.stop(t + dur + 0.01);
}

// ===== MAP / BOSS MUSIC PROFILES =====

const SCALES = {
  naturalMinor: [0, 2, 3, 5, 7, 8, 10, 12, 14, 15, 17, 19, 20, 22, 24],
  phrygian: [0, 1, 3, 5, 7, 8, 10, 12, 13, 15, 17, 19, 20, 22, 24],
  harmonicMinor: [0, 2, 3, 5, 7, 8, 11, 12, 14, 15, 17, 19, 20, 23, 24],
  mixolydian: [0, 2, 4, 5, 7, 9, 10, 12, 14, 16, 17, 19, 21, 22, 24],
  wholeTone: [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24],
  diminished: [0, 1, 3, 4, 6, 7, 9, 10, 12, 13, 15, 16, 18, 19, 21, 22, 24],
} as const;

const MAP_MUSIC_PROFILES: Record<string, MusicProfile> = {
  'neon-grid': {
    id: 'map:neon-grid',
    bpm: 138,
    keyCycle: [33, 36, 38, 40],
    keyChangeEveryMeasures: 64,
    progressions: [PROGS[4], PROGS[2], PROGS[0]], // synthwave + trance + cinematic
    melodyPhrases: [MELODY_PHRASES[8], MELODY_PHRASES[1], MELODY_PHRASES[0], MELODY_PHRASES[5]],
    scale: SCALES.naturalMinor,
    bassRhythms: [BASS_RHYTHMS[0], BASS_RHYTHMS[2], BASS_RHYTHMS[5]],
    masterGain: 0.030,
    kickStyle: 'four',
    hatStyle: 'tight',
  },
  inferno: {
    id: 'map:inferno',
    bpm: 152,
    keyCycle: [31, 34, 36, 38],
    keyChangeEveryMeasures: 48,
    progressions: [PROGS[5], PROGS[1], PROGS[6]], // aggressive + driving
    melodyPhrases: [MELODY_PHRASES[3], MELODY_PHRASES[7], MELODY_PHRASES[1]],
    scale: SCALES.phrygian,
    bassRhythms: [BASS_RHYTHMS[5], BASS_RHYTHMS[3], BASS_RHYTHMS[1]],
    masterGain: 0.032,
    kickStyle: 'broken',
    hatStyle: 'dense',
  },
  void: {
    id: 'map:void',
    bpm: 128,
    keyCycle: [28, 31, 33, 26],
    keyChangeEveryMeasures: 64,
    progressions: [PROGS[5], PROGS[0], PROGS[7]],
    melodyPhrases: [MELODY_PHRASES[6], MELODY_PHRASES[9], MELODY_PHRASES[2]],
    scale: SCALES.diminished,
    bassRhythms: [BASS_RHYTHMS[6], BASS_RHYTHMS[0]],
    masterGain: 0.028,
    kickStyle: 'half',
    hatStyle: 'shuffle',
  },
  crystal: {
    id: 'map:crystal',
    bpm: 142,
    keyCycle: [35, 38, 40, 43],
    keyChangeEveryMeasures: 64,
    progressions: [PROGS[2], PROGS[3], PROGS[7]],
    melodyPhrases: [MELODY_PHRASES[0], MELODY_PHRASES[4], MELODY_PHRASES[9]],
    scale: SCALES.mixolydian,
    bassRhythms: [BASS_RHYTHMS[2], BASS_RHYTHMS[0], BASS_RHYTHMS[4]],
    masterGain: 0.030,
    kickStyle: 'four',
    hatStyle: 'tight',
  },
  singularity: {
    id: 'map:singularity',
    bpm: 168,
    keyCycle: [33, 36, 38, 40],
    keyChangeEveryMeasures: 32,
    progressions: [PROGS[5], PROGS[1], PROGS[6]],
    melodyPhrases: [MELODY_PHRASES[8], MELODY_PHRASES[3], MELODY_PHRASES[1]],
    scale: SCALES.diminished,
    bassRhythms: [BASS_RHYTHMS[1], BASS_RHYTHMS[5], BASS_RHYTHMS[3]],
    masterGain: 0.034,
    kickStyle: 'dnb',
    hatStyle: 'dense',
  },
  foundry: {
    id: 'map:foundry',
    bpm: 156,
    keyCycle: [30, 33, 35, 37],
    keyChangeEveryMeasures: 48,
    progressions: [PROGS[1], PROGS[5], PROGS[6]],
    melodyPhrases: [MELODY_PHRASES[5], MELODY_PHRASES[3], MELODY_PHRASES[7]],
    scale: SCALES.harmonicMinor,
    bassRhythms: [BASS_RHYTHMS[3], BASS_RHYTHMS[5], BASS_RHYTHMS[0]],
    masterGain: 0.032,
    kickStyle: 'broken',
    hatStyle: 'shuffle',
  },
};

const DEFAULT_BOSS_PROFILE: MusicProfile = {
  id: 'boss:generic',
  bpm: 172,
  keyCycle: [31, 33],
  keyChangeEveryMeasures: 16,
  progressions: [PROGS[5], PROGS[6]],
  melodyPhrases: [MELODY_PHRASES[8], MELODY_PHRASES[1], MELODY_PHRASES[3]],
  scale: SCALES.diminished,
  bassRhythms: [BASS_RHYTHMS[1], BASS_RHYTHMS[5]],
  masterGain: 0.036,
  kickStyle: 'dnb',
  hatStyle: 'dense',
  sectionFeelOverride: 4,
};

const BOSS_MUSIC_PROFILES: Partial<Record<EnemyType, MusicProfile>> = {
  mothership: { ...DEFAULT_BOSS_PROFILE, id: 'boss:mothership', bpm: 158, scale: SCALES.wholeTone, progressions: [PROGS[2], PROGS[5]] },
  vortex: { ...DEFAULT_BOSS_PROFILE, id: 'boss:vortex', bpm: 176, scale: SCALES.diminished, progressions: [PROGS[5], PROGS[1]] },
  colossus: { ...DEFAULT_BOSS_PROFILE, id: 'boss:colossus', bpm: 148, kickStyle: 'half', hatStyle: 'tight', scale: SCALES.naturalMinor, progressions: [PROGS[3], PROGS[0]] },
  fire_elemental: { ...DEFAULT_BOSS_PROFILE, id: 'boss:fire_elemental', bpm: 162, scale: SCALES.harmonicMinor, progressions: [PROGS[6], PROGS[1]] },
  lava_dragon: { ...DEFAULT_BOSS_PROFILE, id: 'boss:lava_dragon', bpm: 166, scale: SCALES.phrygian, progressions: [PROGS[5], PROGS[6]] },
  void_lord: { ...DEFAULT_BOSS_PROFILE, id: 'boss:void_lord', bpm: 184, scale: SCALES.diminished, progressions: [PROGS[5], PROGS[7]] },
  crystal_giant: { ...DEFAULT_BOSS_PROFILE, id: 'boss:crystal_giant', bpm: 154, hatStyle: 'tight', scale: SCALES.mixolydian, progressions: [PROGS[2], PROGS[3]] },
};

function getActiveGameProfile(): MusicProfile {
  if (activeBossType) {
    return BOSS_MUSIC_PROFILES[activeBossType] ?? DEFAULT_BOSS_PROFILE;
  }
  return MAP_MUSIC_PROFILES[activeMapId] ?? MAP_MUSIC_PROFILES['neon-grid'];
}

function hardResetMusicState(profile: MusicProfile) {
  currentProfile = profile;
  pendingProfile = null;
  pendingProfileReset = false;

  currentChordIndex = 0;
  currentProgIndex = 0;
  measureCount = 0;
  sectionCount = 0;
  currentKey = profile.keyCycle[0] ?? 33;
}

function scheduleNextMeasure() {
  if (!musicPlaying || !audioCtx) return;

  const desired = pendingProfileReset && pendingProfile
    ? pendingProfile
    : (currentProfile ?? getActiveGameProfile());

  if (!currentProfile || pendingProfileReset) {
    hardResetMusicState(desired);
  }

  const profile = currentProfile!;

  const ctx = audioCtx;
  const now = ctx.currentTime;
  const bpm = profile.bpm;
  const beatDur = 60 / bpm;
  const measureDur = beatDur * 4;
  const sixteenth = beatDur / 4;

  const isNewSection = measureCount > 0 && measureCount % 16 === 0;
  if (isNewSection) {
    sectionCount++;
    currentProgIndex = sectionCount % profile.progressions.length;
  }

  if (measureCount > 0 && measureCount % profile.keyChangeEveryMeasures === 0) {
    const kIdx = Math.floor(measureCount / profile.keyChangeEveryMeasures) % profile.keyCycle.length;
    currentKey = profile.keyCycle[kIdx] ?? currentKey;
  }

  const prog = profile.progressions[currentProgIndex];
  const chord = prog[currentChordIndex % prog.length];

  const sectionFeel = profile.sectionFeelOverride ?? (sectionCount % 7);
  const measureInSection = measureCount % 16;
  const isFillMeasure = measureInSection === 15 || measureInSection === 7;
  const intensity = musicIntensity;

  if (!musicGain) {
    musicGain = ctx.createGain();
    musicGain.gain.value = profile.masterGain;
    compressor = ctx.createDynamicsCompressor();
    compressor.threshold.value = -12;
    compressor.knee.value = 4;
    compressor.ratio.value = 6;
    compressor.attack.value = 0.001;
    compressor.release.value = 0.08;
    musicGain.connect(compressor).connect(ctx.destination);
    reverbGain = createReverb(ctx, musicGain);
  }

  const masterVol = (0.05 + intensity * 0.012) * 0.5;
  musicGain.gain.setValueAtTime(masterVol, now);

  // ============ KICK (punchy, layered) ============
  const kickBeats = sectionFeel === 3
    ? (isFillMeasure ? [0, 0.5, 1, 1.5, 2, 2.5, 3, 3.25, 3.5, 3.75] : [0, 2])
    : sectionFeel === 4
    ? [0, 0.75, 1, 2, 2.75, 3]
    : [0, 1, 2, 3];

  for (const beat of kickBeats) {
    const t = now + beat * beatDur;
    // Sub thump
    const sub = ctx.createOscillator();
    const subG = ctx.createGain();
    sub.type = 'sine';
    sub.frequency.setValueAtTime(160, t);
    sub.frequency.exponentialRampToValueAtTime(35, t + 0.15);
    subG.gain.setValueAtTime(0.25, t);
    subG.gain.exponentialRampToValueAtTime(0.001, t + 0.2);
    sub.connect(subG).connect(musicGain!);
    sub.start(t); sub.stop(t + 0.21);

    // Click transient
    const click = ctx.createOscillator();
    const clickG = ctx.createGain();
    click.type = 'square';
    click.frequency.setValueAtTime(8000, t);
    click.frequency.exponentialRampToValueAtTime(200, t + 0.008);
    clickG.gain.setValueAtTime(0.09, t);
    clickG.gain.exponentialRampToValueAtTime(0.001, t + 0.012);
    click.connect(clickG).connect(musicGain!);
    click.start(t); click.stop(t + 0.015);

    // Body (FM)
    const body = ctx.createOscillator();
    const bodyMod = ctx.createOscillator();
    const bodyModG = ctx.createGain();
    const bodyG = ctx.createGain();
    bodyMod.frequency.setValueAtTime(280, t);
    bodyModG.gain.setValueAtTime(200, t);
    bodyModG.gain.exponentialRampToValueAtTime(1, t + 0.06);
    bodyMod.connect(bodyModG).connect(body.frequency);
    body.type = 'sine';
    body.frequency.setValueAtTime(90, t);
    body.frequency.exponentialRampToValueAtTime(40, t + 0.08);
    bodyG.gain.setValueAtTime(0.18, t);
    bodyG.gain.exponentialRampToValueAtTime(0.001, t + 0.1);
    body.connect(bodyG).connect(musicGain!);
    body.start(t); body.stop(t + 0.11);
    bodyMod.start(t); bodyMod.stop(t + 0.11);
  }

  // ============ SNARE (layered noise + tone) ============
  if (sectionFeel !== 0 || measureInSection >= 3) {
    const snareBeats = isFillMeasure && sectionFeel === 1
      ? [1, 2, 2.5, 3, 3.25, 3.5, 3.75]
      : isFillMeasure
      ? [1, 2.5, 3, 3.5, 3.75]
      : sectionFeel === 4
      ? [1, 2.5, 3]
      : [1, 3];

    for (const beat of snareBeats) {
      const t = now + beat * beatDur;
      // Noise body
      for (let j = 0; j < 6; j++) {
        const n = ctx.createOscillator();
        const ng = ctx.createGain();
        const nf = ctx.createBiquadFilter();
        n.type = j % 2 === 0 ? 'sawtooth' : 'square';
        n.frequency.setValueAtTime(100 + Math.random() * 600, t);
        n.detune.setValueAtTime(Math.random() * 2400 - 1200, t);
        nf.type = 'bandpass';
        nf.frequency.value = 4000 + Math.random() * 3000;
        nf.Q.value = 0.3;
        ng.gain.setValueAtTime(0.032, t);
        ng.gain.exponentialRampToValueAtTime(0.001, t + 0.08 + Math.random() * 0.04);
        n.connect(nf).connect(ng).connect(musicGain!);
        if (reverbGain && j === 0) ng.connect(reverbGain);
        n.start(t); n.stop(t + 0.15);
      }
      // Tone body
      const sb = ctx.createOscillator();
      const sbg = ctx.createGain();
      sb.type = 'sine';
      sb.frequency.setValueAtTime(280, t);
      sb.frequency.exponentialRampToValueAtTime(120, t + 0.04);
      sbg.gain.setValueAtTime(0.09, t);
      sbg.gain.exponentialRampToValueAtTime(0.001, t + 0.06);
      sb.connect(sbg).connect(musicGain!);
      sb.start(t); sb.stop(t + 0.07);
    }
  }

  // ============ HI-HATS (dynamic patterns) ============
  {
    const hatPatterns: number[][] = [
      [1,0,1,0, 1,0,1,0, 1,0,1,0, 1,0,1,0],
      [1,0,1,1, 0,1,1,0, 1,0,1,1, 0,1,1,0],
      [1,1,1,1, 1,1,1,1, 1,1,1,1, 1,1,1,1],
      [1,0,0,1, 0,1,0,1, 1,0,0,1, 0,1,0,1],
      [1,1,0,1, 0,1,1,0, 1,1,0,1, 0,1,1,1], // shuffle
    ];
    const pIdx = Math.min(sectionFeel, hatPatterns.length - 1);
    const pattern = hatPatterns[pIdx];

    for (let i = 0; i < 16; i++) {
      if (!pattern[i]) continue;
      const t = now + i * sixteenth;
      const isOpen = (i === 4 || i === 12) && sectionFeel >= 1;
      const isAccent = i % 4 === 0;
      const osc = ctx.createOscillator();
      const g = ctx.createGain();
      const f = ctx.createBiquadFilter();
      osc.type = 'square';
      osc.frequency.setValueAtTime(8000 + Math.random() * 6000, t);
      f.type = 'highpass';
      f.frequency.value = 7000;
      const dur = isOpen ? 0.1 : 0.015;
      const vol = isOpen ? 0.025 : (isAccent ? 0.016 : 0.011);
      g.gain.setValueAtTime(vol, t);
      g.gain.exponentialRampToValueAtTime(0.001, t + dur);
      osc.connect(f).connect(g).connect(musicGain!);
      osc.start(t); osc.stop(t + dur + 0.01);
    }
  }

  // ============ BASS (supersaw sub + harmonic) ============
  {
    const bpIdx = (sectionCount + sectionFeel) % BASS_RHYTHMS.length;
    const bp = sectionFeel === 3
      ? [1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0]
      : BASS_RHYTHMS[bpIdx];

    for (let i = 0; i < 16; i++) {
      if (!bp[i]) continue;
      const t = now + i * sixteenth;
      const bassNote = currentKey + chord[0];
      const octJump = (i === 8 || i === 12) && (sectionFeel === 2 || sectionFeel === 4) ? 12 : 0;
      const freq = midiToFreq(bassNote + octJump);

      // Detuned saw stack (fatter bass)
      for (let d = -2; d <= 2; d++) {
        const osc = ctx.createOscillator();
        const g = ctx.createGain();
        const f = ctx.createBiquadFilter();
        osc.type = d === 0 ? 'sawtooth' : (Math.abs(d) === 1 ? 'sawtooth' : 'square');
        osc.frequency.setValueAtTime(freq * (1 + d * 0.005), t);
        f.type = 'lowpass';
        const fPeak = 400 + intensity * 150;
        f.frequency.setValueAtTime(fPeak + 800, t);
        f.frequency.exponentialRampToValueAtTime(fPeak, t + sixteenth * 0.7);
        f.Q.setValueAtTime(4, t);
        const vol = 0.05;
        g.gain.setValueAtTime(0, t);
        g.gain.linearRampToValueAtTime(vol, t + 0.003);
        g.gain.exponentialRampToValueAtTime(0.001, t + sixteenth * 0.82);
        osc.connect(f).connect(g).connect(musicGain!);
        osc.start(t); osc.stop(t + sixteenth);
      }

      // Deep sub sine
      const subB = ctx.createOscillator();
      const subBG = ctx.createGain();
      subB.type = 'sine';
      subB.frequency.setValueAtTime(freq / 2, t);
      subBG.gain.setValueAtTime(0.16, t);
      subBG.gain.exponentialRampToValueAtTime(0.001, t + sixteenth * 0.7);
      subB.connect(subBG).connect(musicGain!);
      subB.start(t); subB.stop(t + sixteenth);
    }
  }

  // ============ SYNTH PADS (lush, wide stereo feel) ============
  if (sectionFeel === 0 || sectionFeel === 3 || (sectionFeel === 2 && measureInSection >= 5)) {
    const padVol = sectionFeel === 3 ? 0.04 : 0.03;
    for (let ci = 0; ci < chord.length; ci++) {
      const noteFreq = midiToFreq(currentKey + 12 + chord[ci]);
      // 5 detuned oscillators for supersaw pad
      for (let d = -2; d <= 2; d++) {
        const osc = ctx.createOscillator();
        const g = ctx.createGain();
        const f = ctx.createBiquadFilter();
        osc.type = d === 0 ? 'sine' : (Math.abs(d) === 1 ? 'triangle' : 'sawtooth');
        osc.frequency.setValueAtTime(noteFreq * (1 + d * 0.005), now);
        // LFO on detuned voices for movement
        if (Math.abs(d) >= 2) {
          const lfo = ctx.createOscillator();
          const lfoG = ctx.createGain();
          lfo.frequency.value = 0.3 + d * 0.1;
          lfoG.gain.value = noteFreq * 0.003;
          lfo.connect(lfoG).connect(osc.frequency);
          lfo.start(now); lfo.stop(now + measureDur + 0.2);
        }
        f.type = 'lowpass';
        const fBase = 600 + intensity * 150;
        f.frequency.setValueAtTime(fBase, now);
        f.frequency.linearRampToValueAtTime(fBase + 300, now + measureDur * 0.5);
        f.frequency.linearRampToValueAtTime(fBase, now + measureDur);
        const vol = padVol / 5;
        g.gain.setValueAtTime(0, now);
        g.gain.linearRampToValueAtTime(vol, now + measureDur * 0.12);
        g.gain.setValueAtTime(vol * 0.85, now + measureDur * 0.75);
        g.gain.exponentialRampToValueAtTime(0.001, now + measureDur + 0.1);
        osc.connect(f).connect(g).connect(musicGain!);
        if (reverbGain) g.connect(reverbGain);
        osc.start(now); osc.stop(now + measureDur + 0.15);
      }
    }
  }

  // ============ ARPEGGIOS (sparkling, evolving) ============
  if (sectionFeel >= 1) {
    const arpPatterns = [
      [0,1,2,3,0,1,2,3, 2,3,0,1,2,3,0,1],
      [0,2,1,3,0,2,1,3, 3,1,2,0,3,1,2,0],
      [3,2,1,0,3,2,1,0, 0,1,2,3,0,1,2,3],
      [0,1,2,1,0,1,2,3, 2,1,0,1,2,3,2,1],
    ];
    const octShifts = [
      [0,0,0,1,1,1,2,2, 2,1,1,1,0,0,0,1],
      [0,1,2,2,1,0,0,1, 2,2,1,0,0,1,2,1],
      [2,2,1,1,0,0,1,1, 2,2,1,1,0,0,1,1],
    ];
    const patIdx = (sectionCount + measureCount) % arpPatterns.length;
    const octIdx = (sectionCount + measureCount) % octShifts.length;
    const arpP = arpPatterns[patIdx];
    const octP = octShifts[octIdx];
    const steps = (sectionFeel === 2 || sectionFeel === 4) ? 16 : (measureInSection >= 4 ? 16 : 8);

    for (let i = 0; i < steps; i++) {
      const chordNote = chord[arpP[i] % chord.length];
      const oct = (octP[i] || 0) * 12;
      const noteFreq = midiToFreq(currentKey + 24 + chordNote + oct);
      const t = now + i * sixteenth;

      // Detuned saw pair
      const osc = ctx.createOscillator();
      const osc2 = ctx.createOscillator();
      const g = ctx.createGain();
      const f = ctx.createBiquadFilter();
      osc.type = 'sawtooth';
      osc2.type = 'sawtooth';
      osc.frequency.setValueAtTime(noteFreq, t);
      osc2.frequency.setValueAtTime(noteFreq * 1.007, t);
      f.type = 'lowpass';
      f.frequency.setValueAtTime(3000 + intensity * 500, t);
      f.frequency.exponentialRampToValueAtTime(800, t + sixteenth * 0.8);
      f.Q.setValueAtTime(3.5, t);
      const vol = 0.02 + intensity * 0.004;
      const accent = i % 4 === 0 ? 1.5 : (i % 2 === 0 ? 1.15 : 1.0);
      g.gain.setValueAtTime(0, t);
      g.gain.linearRampToValueAtTime(vol * accent, t + 0.002);
      g.gain.exponentialRampToValueAtTime(0.001, t + sixteenth * 0.8);
      osc.connect(f);
      osc2.connect(f);
      f.connect(g).connect(musicGain!);
      if (reverbGain && i % 4 === 0) g.connect(reverbGain);
      osc.start(t); osc.stop(t + sixteenth);
      osc2.start(t); osc2.stop(t + sixteenth);
    }
  }

  // ============ LEAD MELODY (FM synthesis, expressive) ============
  if ((sectionFeel === 2 || sectionFeel === 4 || (sectionFeel === 1 && measureInSection >= 4)) && intensity >= 1) {
    const minorScale = [0, 2, 3, 5, 7, 8, 10, 12, 14, 15, 17, 19, 20, 22, 24];
    const phraseIdx = (sectionCount * 3 + measureCount) % MELODY_PHRASES.length;
    const phrase = MELODY_PHRASES[phraseIdx];

    let step = 0;
    for (let i = 0; i < phrase.length; i++) {
      const [noteIdx, durSteps] = phrase[i];
      if (durSteps === 0) { step++; continue; } // rest
      if (step >= 16) break;
      const t = now + step * sixteenth;
      const dur = durSteps * sixteenth;
      const scaleDeg = noteIdx % minorScale.length;
      const note = minorScale[scaleDeg];
      const noteFreq = midiToFreq(currentKey + 36 + note);

      // Layer 1: Square lead
      const osc = ctx.createOscillator();
      const osc2 = ctx.createOscillator();
      const g = ctx.createGain();
      const f = ctx.createBiquadFilter();

      osc.type = 'square';
      osc2.type = 'sawtooth';
      osc.frequency.setValueAtTime(noteFreq, t);
      osc2.frequency.setValueAtTime(noteFreq * 1.004, t);

      // Vibrato on held notes
      if (durSteps >= 3) {
        const lfo = ctx.createOscillator();
        const lfoG = ctx.createGain();
        lfo.type = 'sine';
        lfo.frequency.value = 5.5;
        lfoG.gain.value = noteFreq * 0.012;
        lfo.connect(lfoG).connect(osc.frequency);
        lfo.connect(lfoG).connect(osc2.frequency);
        lfo.start(t + dur * 0.3); lfo.stop(t + dur);
      }

      // Portamento
      if (durSteps === 1 && i < phrase.length - 1 && phrase[i + 1][1] > 0) {
        const nextNote = minorScale[phrase[i + 1][0] % minorScale.length];
        const nextFreq = midiToFreq(currentKey + 36 + nextNote);
        osc.frequency.linearRampToValueAtTime(nextFreq, t + dur * 0.85);
        osc2.frequency.linearRampToValueAtTime(nextFreq * 1.004, t + dur * 0.85);
      }

      f.type = 'lowpass';
      f.frequency.setValueAtTime(5000 + intensity * 800, t);
      f.frequency.exponentialRampToValueAtTime(2000, t + dur * 0.6);
      f.Q.value = 1.2;

      const vol = 0.028 + intensity * 0.005;
      g.gain.setValueAtTime(0, t);
      g.gain.linearRampToValueAtTime(vol, t + 0.004);
      if (durSteps >= 2) {
        g.gain.setValueAtTime(vol * 0.82, t + dur * 0.4);
      }
      g.gain.exponentialRampToValueAtTime(0.001, t + dur * 0.9);

      osc.connect(f);
      osc2.connect(f);
      f.connect(g).connect(musicGain!);
      if (reverbGain) g.connect(reverbGain);
      osc.start(t); osc.stop(t + dur + 0.02);
      osc2.start(t); osc2.stop(t + dur + 0.02);

      // Layer 2: FM bell on accents
      if (i % 3 === 0 && durSteps >= 2) {
        playFMNote(ctx, musicGain!, noteFreq * 2, 3, noteFreq * 0.8, t, dur * 0.5, 0.01);
      }

      // Layer 3: Sub octave for warmth
      const subLead = ctx.createOscillator();
      const subG = ctx.createGain();
      subLead.type = 'sine';
      subLead.frequency.setValueAtTime(noteFreq * 0.5, t);
      subG.gain.setValueAtTime(vol * 0.4, t);
      subG.gain.exponentialRampToValueAtTime(0.001, t + dur * 0.7);
      subLead.connect(subG).connect(musicGain!);
      subLead.start(t); subLead.stop(t + dur + 0.01);

      step += durSteps;
    }
  }

  // ============ COUNTER-MELODY (harmony layer) ============
  if ((sectionFeel === 2 || sectionFeel === 4) && intensity >= 2 && measureInSection % 2 === 0) {
    const counterNotes = [chord[Math.min(2, chord.length-1)], chord[0], chord[Math.min(1, chord.length-1)], chord[Math.min(2, chord.length-1)]];
    for (let i = 0; i < 4; i++) {
      const t = now + i * beatDur;
      const noteFreq = midiToFreq(currentKey + 48 + counterNotes[i]);
      playFMNote(ctx, musicGain!, noteFreq, 2, noteFreq * 0.3, t, beatDur * 0.7, 0.015, 'triangle');
    }
  }

  // ============ RISERS & TRANSITIONS ============
  if (isFillMeasure) {
    if (sectionFeel === 1 || sectionFeel === 3) {
      // Supersaw riser
      for (let d = -1; d <= 1; d++) {
        const riser = ctx.createOscillator();
        const rG = ctx.createGain();
        const rF = ctx.createBiquadFilter();
        riser.type = 'sawtooth';
        riser.frequency.setValueAtTime(100 + d * 3, now);
        riser.frequency.exponentialRampToValueAtTime(4000 + d * 30, now + measureDur);
        riser.detune.setValueAtTime(d * 10, now);
        riser.detune.linearRampToValueAtTime(d * 10 + 1200, now + measureDur);
        rF.type = 'bandpass';
        rF.frequency.setValueAtTime(200, now);
        rF.frequency.exponentialRampToValueAtTime(8000, now + measureDur);
        rF.Q.value = 1.5;
        rG.gain.setValueAtTime(0, now);
        rG.gain.linearRampToValueAtTime(0.04, now + measureDur * 0.9);
        rG.gain.exponentialRampToValueAtTime(0.001, now + measureDur);
        riser.connect(rF).connect(rG).connect(musicGain!);
        riser.start(now); riser.stop(now + measureDur + 0.01);
      }
    }

    // Crash cymbal
    if (sectionFeel === 1 || sectionFeel === 3) {
      const t = now + measureDur - 0.01;
      for (let j = 0; j < 5; j++) {
        const crash = ctx.createOscillator();
        const cg = ctx.createGain();
        crash.type = 'sawtooth';
        crash.frequency.setValueAtTime(4000 + Math.random() * 7000, t);
        crash.detune.setValueAtTime(Math.random() * 3600, t);
        cg.gain.setValueAtTime(0.03, t);
        cg.gain.exponentialRampToValueAtTime(0.001, t + 0.7);
        crash.connect(cg).connect(musicGain!);
        crash.start(t); crash.stop(t + 0.75);
      }
    }

    // Sub impact before drops
    if (sectionFeel === 3) {
      const impact = ctx.createOscillator();
      const ig = ctx.createGain();
      impact.type = 'sine';
      impact.frequency.setValueAtTime(50, now + measureDur - 0.2);
      impact.frequency.exponentialRampToValueAtTime(18, now + measureDur);
      ig.gain.setValueAtTime(0, now + measureDur - 0.2);
      ig.gain.linearRampToValueAtTime(0.25, now + measureDur - 0.02);
      ig.gain.exponentialRampToValueAtTime(0.001, now + measureDur + 0.4);
      impact.connect(ig).connect(musicGain!);
      impact.start(now + measureDur - 0.2); impact.stop(now + measureDur + 0.45);
    }
  }

  // ============ AMBIENT TEXTURE (breakdowns) ============
  if (sectionFeel === 3) {
    // Granular-style texture
    for (let i = 0; i < 3; i++) {
      const washOsc = ctx.createOscillator();
      const washG = ctx.createGain();
      const washF = ctx.createBiquadFilter();
      washOsc.type = 'sawtooth';
      washOsc.frequency.setValueAtTime(30 + Math.random() * 30 + i * 15, now + i * 0.3);
      washOsc.detune.setValueAtTime(1200 + i * 200, now);
      washF.type = 'bandpass';
      washF.frequency.setValueAtTime(200 + i * 100, now);
      washF.frequency.linearRampToValueAtTime(1000 + i * 200, now + measureDur * 0.5);
      washF.frequency.linearRampToValueAtTime(200 + i * 100, now + measureDur);
      washF.Q.value = 0.3;
      washG.gain.setValueAtTime(0.012, now + i * 0.3);
      washG.gain.exponentialRampToValueAtTime(0.001, now + measureDur);
      washOsc.connect(washF).connect(washG).connect(musicGain!);
      if (reverbGain) washG.connect(reverbGain);
      washOsc.start(now + i * 0.3); washOsc.stop(now + measureDur + 0.01);
    }
  }

  // ============ ENERGY STABS (drop power chords) ============
  if ((sectionFeel === 2 || sectionFeel === 4) && (measureInSection === 0 || measureInSection === 4)) {
    for (let ci = 0; ci < chord.length; ci++) {
      const noteFreq = midiToFreq(currentKey + 24 + chord[ci]);
      for (let d = -2; d <= 2; d++) {
        const osc = ctx.createOscillator();
        const g = ctx.createGain();
        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(noteFreq * (1 + d * 0.01), now);
        g.gain.setValueAtTime(0.035, now);
        g.gain.exponentialRampToValueAtTime(0.001, now + beatDur * 0.35);
        osc.connect(g).connect(musicGain!);
        osc.start(now); osc.stop(now + beatDur * 0.4);
      }
    }
  }

  // ============ PLUCK LAYER (climax sections) ============
  if (sectionFeel === 4 && measureInSection % 2 === 1) {
    const pluckNotes = [chord[0], chord[1], chord[2], chord[0]+12];
    for (let i = 0; i < 4; i++) {
      const t = now + i * beatDur + beatDur * 0.5;
      const noteFreq = midiToFreq(currentKey + 36 + pluckNotes[i % pluckNotes.length]);
      playFMNote(ctx, musicGain!, noteFreq, 5, noteFreq * 1.5, t, beatDur * 0.3, 0.02);
    }
  }

  currentChordIndex = (currentChordIndex + 1) % prog.length;
  measureCount++;

  const nextTime = (measureDur - 0.05) * 1000;
  const timer = window.setTimeout(scheduleNextMeasure, nextTime);
  musicTimers.push(timer);
}

function stopProceduralGameOnly() {
  musicTimers.forEach(t => clearTimeout(t));
  musicTimers = [];
  if (musicGain && audioCtx) {
    try { musicGain.gain.linearRampToValueAtTime(0, audioCtx.currentTime + 0.25); } catch {}
  }
  musicGain = null;
}

export function startMusic() {
  if (musicPlaying) return;

  // Ensure menu music (procedural or MP3) is stopped before starting gameplay music.
  stopMenuMusic();

  try {
    getCtx();
    musicPlaying = true;

    // Start procedural immediately as a fallback (and for instant feedback),
    // then swap to MP3 once it finishes loading.
    musicGain = null;
    compressor = null;
    reverbGain = null;
    currentChordIndex = 0;
    currentProgIndex = 0;
    measureCount = 0;
    sectionCount = 0;
    currentKey = 33;
    scheduleNextMeasure();

    void ensureMp3Buffer().then(buf => {
      if (!buf) return;
      if (!musicPlaying) return;
      stopProceduralGameOnly();
      startMp3Game(buf);
    });
  } catch {}
}

export function stopMusic() {
  musicPlaying = false;
  stopProceduralGameOnly();
  stopMp3Game();
}

export function setMusicIntensity(wave: number) {
  musicIntensity = Math.min(5, Math.max(1, Math.floor(wave / 2) + 1));

  // If MP3 is active, apply subtle intensity via filter + playback rate.
  if (mp3GameSource && mp3GameFilter && audioCtx) {
    try {
      const ctx = audioCtx;
      const i = musicIntensity;
      mp3GameFilter.frequency.setTargetAtTime(7000 + i * 1500, ctx.currentTime, 0.15);
      mp3GameSource.playbackRate.setTargetAtTime(1 + (i - 1) * 0.02, ctx.currentTime, 0.15);
    } catch {}
  }
}

// ===== MENU MUSIC (Atmospheric synthwave, rich and moody) =====
let menuMusicPlaying = false;
let menuTimers: number[] = [];
let menuGain: GainNode | null = null;
let menuMeasure = 0;

  const MENU_CHORDS = [
    [[0,3,7,10,14], [8,12,15,19,22], [3,7,10,14,17], [10,14,17,21,24]],
    [[0,3,7,10,14], [5,8,12,15,19], [8,12,15,19,22], [7,11,14,17,22]],
    [[0,4,7,11,14], [5,9,12,16,19], [7,11,14,17,22], [3,7,10,14,17]],
    [[5,8,12,15,19], [0,3,7,10,14], [10,14,17,21,24], [8,12,15,19,22]], // Expanded progression
    [[3,7,10,14,17], [10,14,17,21,24], [5,8,12,15,19], [7,11,14,17,22]], // Mystic progression
  ];

function scheduleMenuMeasure() {
  if (!menuMusicPlaying || !audioCtx) return;
  const ctx = audioCtx;
  const now = ctx.currentTime;
  const bpm = 85;
  const beatDur = 60 / bpm;
  const measureDur = beatDur * 4;
  const key = 33;

  if (!menuGain) {
    menuGain = ctx.createGain();
    menuGain.gain.value = 0.05;
    menuGain.connect(ctx.destination);
  }

  // Slower tempo for more atmospheric feel
  const progIdx = Math.floor(menuMeasure / 4) % MENU_CHORDS.length;
  const prog = MENU_CHORDS[progIdx];
  const chord = prog[menuMeasure % prog.length];
  
  // Modulate key every 16 measures for variety
  const currentKey = key + (Math.floor(menuMeasure / 16) % 3) * 2;

  // Lush pad (7 voices supersaw)
  for (let ci = 0; ci < Math.min(chord.length, 5); ci++) {
    const noteFreq = midiToFreq(currentKey + 12 + chord[ci]);
    for (let d = -3; d <= 3; d++) {
      const osc = ctx.createOscillator();
      const g = ctx.createGain();
      const f = ctx.createBiquadFilter();
      osc.type = Math.abs(d) <= 1 ? 'sine' : (Math.abs(d) === 2 ? 'triangle' : 'sawtooth');
      osc.frequency.setValueAtTime(noteFreq * (1 + d * 0.004), now);
      // Slow LFO on outer voices
      if (Math.abs(d) >= 2) {
        const lfo = ctx.createOscillator();
        const lg = ctx.createGain();
        lfo.frequency.value = 0.15 + d * 0.05;
        lg.gain.value = noteFreq * 0.003;
        lfo.connect(lg).connect(osc.frequency);
        lfo.start(now); lfo.stop(now + measureDur + 0.2);
      }
      f.type = 'lowpass';
      f.frequency.setValueAtTime(500, now);
      f.frequency.linearRampToValueAtTime(900, now + measureDur * 0.4);
      f.frequency.linearRampToValueAtTime(500, now + measureDur);
      const vol = 0.008;
      g.gain.setValueAtTime(0, now);
      g.gain.linearRampToValueAtTime(vol, now + measureDur * 0.15);
      g.gain.setValueAtTime(vol * 0.8, now + measureDur * 0.7);
      g.gain.exponentialRampToValueAtTime(0.001, now + measureDur + 0.1);
      osc.connect(f).connect(g).connect(menuGain!);
      osc.start(now); osc.stop(now + measureDur + 0.15);
    }
  }

  // Gentle arpeggio with delay feel
  const arpPattern = [0, 2, 1, 3, 0, 3, 1, 2, 0, 2, 3, 1];
  for (let i = 0; i < 8; i++) {
    const chordNote = chord[arpPattern[i % arpPattern.length] % chord.length];
    const oct = (i % 4 === 0 ? 12 : 0);
    const noteFreq = midiToFreq(currentKey + 24 + chordNote + oct);
    const t = now + i * (beatDur / 2);
    
    const osc = ctx.createOscillator();
    const g = ctx.createGain();
    const f = ctx.createBiquadFilter();
    osc.type = 'triangle';
    osc.frequency.setValueAtTime(noteFreq, t);
    f.type = 'lowpass';
    f.frequency.setValueAtTime(2000, t);
    f.frequency.exponentialRampToValueAtTime(500, t + beatDur * 0.45);
    g.gain.setValueAtTime(0, t);
    g.gain.linearRampToValueAtTime(0.018, t + 0.004);
    g.gain.exponentialRampToValueAtTime(0.001, t + beatDur * 0.48);
    osc.connect(f).connect(g).connect(menuGain!);
    osc.start(t); osc.stop(t + beatDur * 0.5);
    
    // Echo repeat
    const t2 = t + beatDur * 0.375;
    const oe = ctx.createOscillator();
    const ge = ctx.createGain();
    const fe = ctx.createBiquadFilter();
    oe.type = 'sine';
    oe.frequency.setValueAtTime(noteFreq, t2);
    fe.type = 'lowpass';
    fe.frequency.value = 1200;
    ge.gain.setValueAtTime(0, t2);
    ge.gain.linearRampToValueAtTime(0.008, t2 + 0.003);
    ge.gain.exponentialRampToValueAtTime(0.001, t2 + beatDur * 0.3);
    oe.connect(fe).connect(ge).connect(menuGain!);
    oe.start(t2); oe.stop(t2 + beatDur * 0.35);
  }

  // Warm sub bass
  const bassFreq = midiToFreq(currentKey + chord[0]);
  const bass = ctx.createOscillator();
  const bg = ctx.createGain();
  bass.type = 'sine';
  bass.frequency.setValueAtTime(bassFreq, now);
  bg.gain.setValueAtTime(0.05, now);
  bg.gain.exponentialRampToValueAtTime(0.001, now + measureDur * 0.75);
  bass.connect(bg).connect(menuGain!);
  bass.start(now); bass.stop(now + measureDur);

  // Atmospheric texture every other measure
  if (menuMeasure % 2 === 0) {
    const tex = ctx.createOscillator();
    const tg = ctx.createGain();
    const tf = ctx.createBiquadFilter();
    tex.type = 'sawtooth';
    tex.frequency.setValueAtTime(40, now);
    tex.detune.setValueAtTime(1200, now);
    tf.type = 'bandpass';
    tf.frequency.setValueAtTime(300, now);
    tf.frequency.linearRampToValueAtTime(800, now + measureDur * 0.5);
    tf.frequency.linearRampToValueAtTime(300, now + measureDur);
    tf.Q.value = 0.5;
    tg.gain.setValueAtTime(0.01, now);
    tg.gain.exponentialRampToValueAtTime(0.001, now + measureDur);
    tex.connect(tf).connect(tg).connect(menuGain!);
    tex.start(now); tex.stop(now + measureDur + 0.01);
  }

  menuMeasure++;
  const timer = window.setTimeout(scheduleMenuMeasure, (measureDur - 0.05) * 1000);
  menuTimers.push(timer);
}

function stopProceduralMenuOnly() {
  menuTimers.forEach(t => clearTimeout(t));
  menuTimers = [];
  if (menuGain && audioCtx) {
    try { menuGain.gain.linearRampToValueAtTime(0, audioCtx.currentTime + 0.25); } catch {}
  }
  menuGain = null;
}

export function startMenuMusic() {
  if (menuMusicPlaying || musicPlaying) return;
  try {
    getCtx();
    menuMusicPlaying = true;

    // Start procedural immediately as fallback, then swap to MP3 once available.
    menuGain = null;
    menuMeasure = 0;
    scheduleMenuMeasure();

    void ensureMp3Buffer().then(buf => {
      if (!buf) return;
      if (!menuMusicPlaying || musicPlaying) return;
      stopProceduralMenuOnly();
      startMp3Menu(buf);
    });
  } catch {}
}

export function stopMenuMusic() {
  menuMusicPlaying = false;
  stopProceduralMenuOnly();
  stopMp3Menu();
}
