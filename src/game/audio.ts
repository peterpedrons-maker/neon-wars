// Synthesized retro arcade sound effects + procedural music using Web Audio API

let audioCtx: AudioContext | null = null;
let musicGain: GainNode | null = null;
let musicPlaying = false;
let musicIntensity = 1;

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
    const gain = ctx.createGain();
    const filter = ctx.createBiquadFilter();
    
    osc.type = 'square';
    osc.frequency.setValueAtTime(pitch, ctx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(pitch * 0.3, ctx.currentTime + 0.1);
    
    osc2.type = 'sine';
    osc2.frequency.setValueAtTime(pitch * 1.5, ctx.currentTime);
    osc2.frequency.exponentialRampToValueAtTime(200, ctx.currentTime + 0.06);
    
    filter.type = 'lowpass';
    filter.frequency.setValueAtTime(3000, ctx.currentTime);
    filter.frequency.exponentialRampToValueAtTime(500, ctx.currentTime + 0.1);
    
    gain.gain.setValueAtTime(0.07, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.1);
    
    osc.connect(filter);
    osc2.connect(filter);
    filter.connect(gain).connect(ctx.destination);
    
    osc.start(ctx.currentTime); osc.stop(ctx.currentTime + 0.1);
    osc2.start(ctx.currentTime); osc2.stop(ctx.currentTime + 0.06);
  } catch {}
}

export function playShootPhantom() {
  try {
    const ctx = getCtx();
    // Ethereal plasma shot
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
    // Rapid twin laser
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
    // Heavy bass cannon
    const osc = ctx.createOscillator();
    const osc2 = ctx.createOscillator();
    const noise = ctx.createOscillator();
    const gain = ctx.createGain();
    const noiseGain = ctx.createGain();
    const dist = ctx.createWaveShaperNode ? ctx.createWaveShaper() : null;
    
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
    const dur = big ? 0.5 : 0.2;
    const vol = big ? 0.12 : 0.07;
    
    // Layered noise explosion
    for (let i = 0; i < (big ? 4 : 3); i++) {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      const filter = ctx.createBiquadFilter();
      
      osc.type = i % 2 === 0 ? 'sawtooth' : 'square';
      osc.frequency.setValueAtTime(80 + Math.random() * 100, ctx.currentTime + i * 0.015);
      osc.frequency.exponentialRampToValueAtTime(15 + Math.random() * 15, ctx.currentTime + dur);
      osc.detune.setValueAtTime(Math.random() * 200 - 100, ctx.currentTime);
      
      filter.type = 'lowpass';
      filter.frequency.setValueAtTime(2000, ctx.currentTime);
      filter.frequency.exponentialRampToValueAtTime(100, ctx.currentTime + dur);
      
      gain.gain.setValueAtTime(vol, ctx.currentTime + i * 0.015);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + dur);
      
      osc.connect(filter).connect(gain).connect(ctx.destination);
      osc.start(ctx.currentTime + i * 0.015);
      osc.stop(ctx.currentTime + dur + i * 0.015);
    }
    
    // Tonal hit on top
    if (big) {
      const hit = ctx.createOscillator();
      const hg = ctx.createGain();
      hit.type = 'sine';
      hit.frequency.setValueAtTime(250, ctx.currentTime);
      hit.frequency.exponentialRampToValueAtTime(40, ctx.currentTime + 0.3);
      hg.gain.setValueAtTime(0.08, ctx.currentTime);
      hg.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.3);
      hit.connect(hg).connect(ctx.destination);
      hit.start(ctx.currentTime); hit.stop(ctx.currentTime + 0.3);
    }
  } catch {}
}

export function playCombo(multiplier: number) {
  try {
    const ctx = getCtx();
    const baseFreq = 500 + multiplier * 60;
    // Ascending arpeggio with harmonics
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
    // Sparkling ascending sweep
    const osc = ctx.createOscillator();
    const osc2 = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = 'sine';
    osc2.type = 'triangle';
    osc.frequency.setValueAtTime(400, ctx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(1400, ctx.currentTime + 0.2);
    osc.frequency.exponentialRampToValueAtTime(900, ctx.currentTime + 0.35);
    osc2.frequency.setValueAtTime(800, ctx.currentTime);
    osc2.frequency.exponentialRampToValueAtTime(2000, ctx.currentTime + 0.15);
    osc2.frequency.exponentialRampToValueAtTime(1200, ctx.currentTime + 0.3);
    gain.gain.setValueAtTime(0.08, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.35);
    osc.connect(gain).connect(ctx.destination);
    osc2.connect(gain);
    osc.start(ctx.currentTime); osc.stop(ctx.currentTime + 0.35);
    osc2.start(ctx.currentTime); osc2.stop(ctx.currentTime + 0.3);
  } catch {}
}

export function playSpecial() {
  try {
    const ctx = getCtx();
    // Dramatic whoosh + tone burst
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
    // Harsh distorted hit
    const osc = ctx.createOscillator();
    const osc2 = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = 'sawtooth';
    osc.frequency.setValueAtTime(350, ctx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(40, ctx.currentTime + 0.25);
    osc2.type = 'square';
    osc2.frequency.setValueAtTime(200, ctx.currentTime);
    osc2.frequency.exponentialRampToValueAtTime(30, ctx.currentTime + 0.2);
    gain.gain.setValueAtTime(0.1, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.25);
    osc.connect(gain).connect(ctx.destination);
    osc2.connect(gain);
    osc.start(ctx.currentTime); osc.stop(ctx.currentTime + 0.25);
    osc2.start(ctx.currentTime); osc2.stop(ctx.currentTime + 0.2);
  } catch {}
}

export function playGameOver() {
  try {
    const ctx = getCtx();
    const notes = [500, 420, 350, 260, 180, 100];
    notes.forEach((freq, i) => {
      const osc = ctx.createOscillator();
      const osc2 = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = 'sine';
      osc2.type = 'triangle';
      osc.frequency.setValueAtTime(freq, ctx.currentTime + i * 0.18);
      osc2.frequency.setValueAtTime(freq * 0.5, ctx.currentTime + i * 0.18);
      gain.gain.setValueAtTime(0.08, ctx.currentTime + i * 0.18);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + i * 0.18 + 0.35);
      osc.connect(gain).connect(ctx.destination);
      osc2.connect(gain);
      osc.start(ctx.currentTime + i * 0.18); osc.stop(ctx.currentTime + i * 0.18 + 0.35);
      osc2.start(ctx.currentTime + i * 0.18); osc2.stop(ctx.currentTime + i * 0.18 + 0.35);
    });
  } catch {}
}

export function playWaveComplete() {
  try {
    const ctx = getCtx();
    const notes = [500, 600, 750, 900, 1100];
    notes.forEach((freq, i) => {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = i < 3 ? 'sine' : 'triangle';
      osc.frequency.setValueAtTime(freq, ctx.currentTime + i * 0.07);
      gain.gain.setValueAtTime(0.07, ctx.currentTime + i * 0.07);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + i * 0.07 + 0.25);
      osc.connect(gain).connect(ctx.destination);
      osc.start(ctx.currentTime + i * 0.07);
      osc.stop(ctx.currentTime + i * 0.07 + 0.25);
    });
  } catch {}
}

// ===== PROCEDURAL BACKGROUND MUSIC =====
// Evolving synthwave that changes over time to avoid repetition

// Musical scales and chord progressions
const SCALE_MINOR = [0, 2, 3, 5, 7, 8, 10]; // Natural minor
const CHORD_PROG = [
  [0, 3, 7],    // i
  [5, 8, 12],   // iv
  [3, 7, 10],   // III
  [7, 10, 14],  // v
  [0, 3, 7],    // i
  [8, 12, 15],  // VI
  [5, 8, 12],   // iv
  [10, 14, 17], // VII
];

let musicTimers: number[] = [];
let currentChordIndex = 0;
let bassNoteIndex = 0;
let measureCount = 0;
let currentKey = 40; // E2 MIDI base

function midiToFreq(midi: number): number {
  return 440 * Math.pow(2, (midi - 69) / 12);
}

function getScaleNote(degree: number): number {
  const octave = Math.floor(degree / 7);
  const note = SCALE_MINOR[degree % 7];
  return currentKey + octave * 12 + note;
}

function scheduleNextMeasure() {
  if (!musicPlaying || !audioCtx) return;
  const ctx = audioCtx;
  const now = ctx.currentTime;
  const bpm = 128 + musicIntensity * 8;
  const beatDur = 60 / bpm;
  const measureDur = beatDur * 4;
  
  // Evolve key every 16 measures
  if (measureCount > 0 && measureCount % 16 === 0) {
    const shifts = [0, 5, 7, -2, 3, -5];
    currentKey = 40 + shifts[Math.floor(Math.random() * shifts.length)];
  }
  
  // Get current chord
  const chord = CHORD_PROG[currentChordIndex % CHORD_PROG.length];
  
  if (!musicGain) {
    musicGain = ctx.createGain();
    musicGain.gain.value = 0.035;
    musicGain.connect(ctx.destination);
  }
  musicGain.gain.value = 0.025 + musicIntensity * 0.003;
  
  // === BASS LINE (evolving pattern) ===
  const bassPatterns = [
    [0, -1, 0, 2],      // steady
    [0, 0, 3, 2],       // ascending
    [0, 4, 2, 0],       // bouncy
    [0, -1, 2, 5],      // wide
  ];
  const bassPattern = bassPatterns[(measureCount >> 2) % bassPatterns.length];
  
  for (let beat = 0; beat < 4; beat++) {
    const bassNote = getScaleNote(chord[0] / 2 + bassPattern[beat]);
    const bassFreq = midiToFreq(bassNote);
    const t = now + beat * beatDur;
    
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    const filter = ctx.createBiquadFilter();
    
    osc.type = 'sawtooth';
    osc.frequency.setValueAtTime(bassFreq, t);
    filter.type = 'lowpass';
    filter.frequency.setValueAtTime(400 + musicIntensity * 50, t);
    gain.gain.setValueAtTime(0, t);
    gain.gain.linearRampToValueAtTime(0.15, t + 0.02);
    gain.gain.exponentialRampToValueAtTime(0.001, t + beatDur * 0.9);
    
    osc.connect(filter).connect(gain).connect(musicGain!);
    osc.start(t); osc.stop(t + beatDur);
  }
  
  // === PAD CHORD (long evolving tones) ===
  const padVol = 0.04 + musicIntensity * 0.005;
  for (const interval of chord) {
    const noteFreq = midiToFreq(currentKey + 12 + interval);
    const osc = ctx.createOscillator();
    const osc2 = ctx.createOscillator();
    const gain = ctx.createGain();
    const filter = ctx.createBiquadFilter();
    
    osc.type = 'sine';
    osc2.type = 'triangle';
    osc.frequency.setValueAtTime(noteFreq, now);
    osc2.frequency.setValueAtTime(noteFreq * 1.003, now); // slight detune for width
    filter.type = 'lowpass';
    filter.frequency.setValueAtTime(800 + musicIntensity * 100 + Math.sin(measureCount * 0.3) * 200, now);
    
    gain.gain.setValueAtTime(0, now);
    gain.gain.linearRampToValueAtTime(padVol, now + measureDur * 0.15);
    gain.gain.setValueAtTime(padVol, now + measureDur * 0.7);
    gain.gain.exponentialRampToValueAtTime(0.001, now + measureDur);
    
    osc.connect(filter);
    osc2.connect(filter);
    filter.connect(gain).connect(musicGain!);
    osc.start(now); osc.stop(now + measureDur + 0.1);
    osc2.start(now); osc2.stop(now + measureDur + 0.1);
  }
  
  // === ARPEGGIOS (only at higher intensity, varying patterns) ===
  if (musicIntensity >= 2) {
    const arpPatterns = [
      [0, 1, 2, 1, 0, 2, 1, 0],
      [0, 2, 1, 2, 0, 1, 2, 1],
      [2, 1, 0, 1, 2, 0, 1, 2],
      [0, 1, 0, 2, 1, 0, 2, 1],
    ];
    const arpPattern = arpPatterns[(measureCount + Math.floor(measureCount / 4)) % arpPatterns.length];
    const eighthDur = beatDur / 2;
    
    for (let i = 0; i < 8; i++) {
      const noteIdx = arpPattern[i];
      const noteFreq = midiToFreq(currentKey + 24 + chord[noteIdx]);
      const t = now + i * eighthDur;
      
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = (measureCount % 8 < 4) ? 'square' : 'triangle';
      osc.frequency.setValueAtTime(noteFreq, t);
      
      const vol = 0.03 + (musicIntensity - 2) * 0.005;
      gain.gain.setValueAtTime(0, t);
      gain.gain.linearRampToValueAtTime(vol, t + 0.01);
      gain.gain.exponentialRampToValueAtTime(0.001, t + eighthDur * 0.85);
      
      osc.connect(gain).connect(musicGain!);
      osc.start(t); osc.stop(t + eighthDur);
    }
  }
  
  // === HI-HAT pattern (higher intensities) ===
  if (musicIntensity >= 3) {
    const hatPatterns = [
      [1, 0, 1, 0, 1, 0, 1, 1],
      [1, 1, 0, 1, 1, 0, 1, 0],
      [1, 0, 1, 1, 0, 1, 0, 1],
    ];
    const hatPattern = hatPatterns[measureCount % hatPatterns.length];
    
    for (let i = 0; i < 8; i++) {
      if (!hatPattern[i]) continue;
      const t = now + i * (beatDur / 2);
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = 'square';
      osc.frequency.setValueAtTime(8000 + Math.random() * 2000, t);
      gain.gain.setValueAtTime(0.012, t);
      gain.gain.exponentialRampToValueAtTime(0.001, t + 0.03);
      osc.connect(gain).connect(musicGain!);
      osc.start(t); osc.stop(t + 0.04);
    }
  }
  
  // === KICK DRUM (on beats 1 and 3) ===
  for (const beat of [0, 2]) {
    const t = now + beat * beatDur;
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = 'sine';
    osc.frequency.setValueAtTime(150, t);
    osc.frequency.exponentialRampToValueAtTime(30, t + 0.1);
    gain.gain.setValueAtTime(0.08 + musicIntensity * 0.01, t);
    gain.gain.exponentialRampToValueAtTime(0.001, t + 0.15);
    osc.connect(gain).connect(musicGain!);
    osc.start(t); osc.stop(t + 0.15);
  }
  
  currentChordIndex = (currentChordIndex + 1) % CHORD_PROG.length;
  measureCount++;
  
  // Schedule next measure
  const nextTime = (measureDur - 0.1) * 1000;
  const timer = window.setTimeout(scheduleNextMeasure, nextTime);
  musicTimers.push(timer);
}

export function startMusic() {
  if (musicPlaying) return;
  try {
    getCtx();
    musicPlaying = true;
    musicGain = null;
    currentChordIndex = 0;
    measureCount = 0;
    currentKey = 40;
    scheduleNextMeasure();
  } catch {}
}

export function stopMusic() {
  musicPlaying = false;
  musicTimers.forEach(t => clearTimeout(t));
  musicTimers = [];
  if (musicGain) {
    try { musicGain.gain.linearRampToValueAtTime(0, audioCtx!.currentTime + 0.5); } catch {}
  }
}

export function setMusicIntensity(wave: number) {
  // Intensity 1-5 based on wave progression
  musicIntensity = Math.min(5, Math.max(1, Math.floor(wave / 2) + 1));
}
