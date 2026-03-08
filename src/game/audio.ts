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
    // Heavy bass cannon
    
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
// Dark synthwave/retrowave that evolves continuously

// Multiple chord progressions to cycle through (minor key, cinematic feel)
const PROGRESSIONS = [
  // Am - F - C - G (epic)
  [[0, 3, 7], [5, 9, 12], [3, 7, 10], [7, 11, 14]],
  // Am - Dm - E - Am (dark)
  [[0, 3, 7], [5, 8, 12], [7, 11, 14], [0, 3, 7]],
  // Am - G - F - E (descending tension)
  [[0, 3, 7], [7, 10, 14], [5, 8, 12], [4, 7, 11]],
  // Am - C - Dm - F (dreamy)
  [[0, 3, 7], [3, 7, 10], [5, 8, 12], [5, 9, 12]],
  // Fm - Ab - Eb - Bb (dark cinematic)
  [[0, 3, 7], [3, 6, 10], [7, 10, 14], [2, 5, 9]],
];

let musicTimers: number[] = [];
let currentChordIndex = 0;
let currentProgIndex = 0;
let measureCount = 0;
let currentKey = 40; // E2 MIDI base
let sectionCount = 0; // tracks song sections for variety

function midiToFreq(midi: number): number {
  return 440 * Math.pow(2, (midi - 69) / 12);
}

function scheduleNextMeasure() {
  if (!musicPlaying || !audioCtx) return;
  const ctx = audioCtx;
  const now = ctx.currentTime;
  const bpm = 130 + musicIntensity * 5;
  const beatDur = 60 / bpm;
  const measureDur = beatDur * 4;
  
  // Change progression every 8 measures
  if (measureCount > 0 && measureCount % 8 === 0) {
    sectionCount++;
    // Switch progression
    currentProgIndex = sectionCount % PROGRESSIONS.length;
    // Key modulation every 16 measures for freshness
    if (measureCount % 16 === 0) {
      const keys = [38, 40, 43, 45, 47, 35, 42]; // various minor roots
      currentKey = keys[sectionCount % keys.length];
    }
  }
  
  const prog = PROGRESSIONS[currentProgIndex];
  const chord = prog[currentChordIndex % prog.length];
  
  if (!musicGain) {
    musicGain = ctx.createGain();
    musicGain.gain.value = 0.04;
    musicGain.connect(ctx.destination);
  }
  musicGain.gain.value = 0.03 + musicIntensity * 0.004;
  
  // Determine "section feel" based on sectionCount for variety
  const sectionFeel = sectionCount % 4; // 0=minimal, 1=building, 2=intense, 3=breakdown
  
  // === KICK DRUM ===
  const kickBeats = sectionFeel === 3 ? [0] : [0, 2]; // half-time on breakdowns
  for (const beat of kickBeats) {
    const t = now + beat * beatDur;
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.type = 'sine';
    osc.frequency.setValueAtTime(160, t);
    osc.frequency.exponentialRampToValueAtTime(28, t + 0.12);
    gain.gain.setValueAtTime(0.1 + musicIntensity * 0.012, t);
    gain.gain.exponentialRampToValueAtTime(0.001, t + 0.18);
    osc.connect(gain).connect(musicGain!);
    osc.start(t); osc.stop(t + 0.18);
    // Kick click layer
    const click = ctx.createOscillator();
    const cg = ctx.createGain();
    click.type = 'square';
    click.frequency.setValueAtTime(1200, t);
    click.frequency.exponentialRampToValueAtTime(100, t + 0.02);
    cg.gain.setValueAtTime(0.03, t);
    cg.gain.exponentialRampToValueAtTime(0.001, t + 0.02);
    click.connect(cg).connect(musicGain!);
    click.start(t); click.stop(t + 0.03);
  }
  
  // === SNARE on beats 2 and 4 ===
  if (sectionFeel !== 0) {
    for (const beat of [1, 3]) {
      const t = now + beat * beatDur;
      // Noise-like snare
      for (let j = 0; j < 2; j++) {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(200 + Math.random() * 100, t);
        osc.detune.setValueAtTime(Math.random() * 1200, t);
        gain.gain.setValueAtTime(0.025, t);
        gain.gain.exponentialRampToValueAtTime(0.001, t + 0.08);
        osc.connect(gain).connect(musicGain!);
        osc.start(t); osc.stop(t + 0.08);
      }
      // Snare body
      const body = ctx.createOscillator();
      const bg = ctx.createGain();
      body.type = 'sine';
      body.frequency.setValueAtTime(180, t);
      body.frequency.exponentialRampToValueAtTime(100, t + 0.05);
      bg.gain.setValueAtTime(0.04, t);
      bg.gain.exponentialRampToValueAtTime(0.001, t + 0.06);
      body.connect(bg).connect(musicGain!);
      body.start(t); body.stop(t + 0.07);
    }
  }
  
  // === BASS LINE ===
  // Different bass patterns per section
  const bassRhythms = [
    [0, 2],              // simple halves
    [0, 1.5, 2, 3.5],   // syncopated
    [0, 0.75, 1.5, 2, 2.75, 3.5], // driving 
    [0, 3],              // sparse breakdown
  ];
  const bassRhythm = bassRhythms[sectionFeel];
  const bassOctave = currentKey;
  
  for (const beatPos of bassRhythm) {
    const t = now + beatPos * beatDur;
    const bassNote = bassOctave + chord[0];
    const bassFreq = midiToFreq(bassNote);
    
    const osc = ctx.createOscillator();
    const osc2 = ctx.createOscillator();
    const gain = ctx.createGain();
    const filter = ctx.createBiquadFilter();
    
    osc.type = 'sawtooth';
    osc2.type = 'square';
    osc.frequency.setValueAtTime(bassFreq, t);
    osc2.frequency.setValueAtTime(bassFreq * 0.998, t); // slight detune
    
    filter.type = 'lowpass';
    const filterSweep = 300 + musicIntensity * 80 + Math.sin(measureCount * 0.4) * 100;
    filter.frequency.setValueAtTime(filterSweep, t);
    filter.Q.setValueAtTime(4, t);
    
    const dur = Math.min(beatDur * 0.85, 0.4);
    gain.gain.setValueAtTime(0, t);
    gain.gain.linearRampToValueAtTime(0.18, t + 0.01);
    gain.gain.setValueAtTime(0.15, t + dur * 0.5);
    gain.gain.exponentialRampToValueAtTime(0.001, t + dur);
    
    osc.connect(filter);
    osc2.connect(filter);
    filter.connect(gain).connect(musicGain!);
    osc.start(t); osc.stop(t + dur + 0.01);
    osc2.start(t); osc2.stop(t + dur + 0.01);
  }
  
  // === PAD CHORD (lush with detuned layers) ===
  const padVol = sectionFeel === 2 ? 0.035 : 0.05 + musicIntensity * 0.005;
  for (const interval of chord) {
    const noteFreq = midiToFreq(currentKey + 12 + interval);
    
    // 3 detuned oscillators for thick pad
    for (let d = -1; d <= 1; d++) {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      const filter = ctx.createBiquadFilter();
      
      osc.type = d === 0 ? 'sine' : 'triangle';
      osc.frequency.setValueAtTime(noteFreq * (1 + d * 0.004), now);
      
      filter.type = 'lowpass';
      filter.frequency.setValueAtTime(600 + musicIntensity * 120 + Math.sin(measureCount * 0.2 + d) * 150, now);
      
      gain.gain.setValueAtTime(0, now);
      gain.gain.linearRampToValueAtTime(padVol / 3, now + measureDur * 0.2);
      gain.gain.setValueAtTime(padVol / 3, now + measureDur * 0.65);
      gain.gain.exponentialRampToValueAtTime(0.001, now + measureDur + 0.05);
      
      osc.connect(filter).connect(gain).connect(musicGain!);
      osc.start(now); osc.stop(now + measureDur + 0.1);
    }
  }
  
  // === ARPEGGIOS (sections 1,2 and high intensity) ===
  if ((sectionFeel === 1 || sectionFeel === 2) && musicIntensity >= 1) {
    // Many different arp patterns
    const arpPatterns = [
      [0, 1, 2, 1, 0, 2, 1, 2, 0, 1, 2, 0, 1, 0, 2, 1],
      [2, 1, 0, 2, 1, 0, 1, 2, 0, 2, 1, 0, 2, 1, 0, 1],
      [0, 0, 1, 2, 2, 1, 0, 1, 2, 2, 0, 1, 1, 2, 0, 0],
      [0, 2, 0, 1, 2, 0, 2, 1, 0, 1, 2, 1, 0, 2, 1, 0],
      [1, 0, 2, 0, 1, 2, 0, 2, 1, 0, 2, 1, 0, 1, 2, 0],
    ];
    const arpPattern = arpPatterns[(measureCount + sectionCount) % arpPatterns.length];
    const sixteenthDur = beatDur / 4;
    const arpSteps = sectionFeel === 2 ? 16 : 8;
    
    for (let i = 0; i < arpSteps; i++) {
      const noteIdx = arpPattern[i % arpPattern.length];
      const octaveShift = (i >= 8) ? 12 : 0;
      const noteFreq = midiToFreq(currentKey + 24 + chord[noteIdx] + octaveShift);
      const t = now + i * sixteenthDur;
      
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      const filter = ctx.createBiquadFilter();
      
      // Alternate waveforms per section for variety
      const waves: OscillatorType[] = ['square', 'triangle', 'sawtooth'];
      osc.type = waves[(sectionCount + Math.floor(i / 4)) % waves.length];
      osc.frequency.setValueAtTime(noteFreq, t);
      
      filter.type = 'lowpass';
      filter.frequency.setValueAtTime(1500 + musicIntensity * 200, t);
      filter.frequency.exponentialRampToValueAtTime(600, t + sixteenthDur * 0.9);
      
      const vol = 0.025 + musicIntensity * 0.004;
      gain.gain.setValueAtTime(0, t);
      gain.gain.linearRampToValueAtTime(vol, t + 0.005);
      gain.gain.exponentialRampToValueAtTime(0.001, t + sixteenthDur * 0.9);
      
      osc.connect(filter).connect(gain).connect(musicGain!);
      osc.start(t); osc.stop(t + sixteenthDur);
    }
  }
  
  // === HI-HATS (varied patterns) ===
  if (sectionFeel !== 3 || musicIntensity >= 3) {
    const hatPatterns = [
      [1, 0, 1, 0, 1, 0, 1, 0],    // straight 8ths
      [1, 0, 1, 1, 0, 1, 0, 1],    // syncopated
      [1, 1, 0, 1, 1, 0, 1, 1],    // busy
      [1, 0, 0, 1, 0, 0, 1, 0],    // sparse
      [1, 1, 1, 0, 1, 1, 0, 1],    // driving
    ];
    const hatPattern = hatPatterns[(measureCount + sectionCount * 2) % hatPatterns.length];
    const eighthDur = beatDur / 2;
    
    for (let i = 0; i < 8; i++) {
      if (!hatPattern[i]) continue;
      const t = now + i * eighthDur;
      const isOpen = (i === 2 || i === 6) && sectionFeel >= 1;
      
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      const filter = ctx.createBiquadFilter();
      
      osc.type = 'square';
      osc.frequency.setValueAtTime(7000 + Math.random() * 3000, t);
      filter.type = 'highpass';
      filter.frequency.setValueAtTime(6000, t);
      
      const hatDur = isOpen ? 0.06 : 0.025;
      const hatVol = isOpen ? 0.015 : 0.01;
      gain.gain.setValueAtTime(hatVol, t);
      gain.gain.exponentialRampToValueAtTime(0.001, t + hatDur);
      
      osc.connect(filter).connect(gain).connect(musicGain!);
      osc.start(t); osc.stop(t + hatDur + 0.01);
    }
  }
  
  // === LEAD MELODY (occasional, adds musicality) ===
  if (sectionFeel === 2 && musicIntensity >= 3 && measureCount % 2 === 0) {
    const melodies = [
      [0, 2, 3, 5, 7, 5, 3, 2],
      [7, 5, 3, 2, 0, 2, 3, 5],
      [0, 3, 7, 5, 3, 7, 10, 7],
      [3, 5, 7, 10, 7, 5, 3, 0],
    ];
    const melody = melodies[(sectionCount + measureCount) % melodies.length];
    const eighthDur = beatDur / 2;
    
    for (let i = 0; i < melody.length; i++) {
      const noteFreq = midiToFreq(currentKey + 24 + melody[i]);
      const t = now + i * eighthDur;
      
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(noteFreq, t);
      // Slight vibrato
      osc.frequency.setValueAtTime(noteFreq, t + eighthDur * 0.3);
      osc.frequency.linearRampToValueAtTime(noteFreq * 1.01, t + eighthDur * 0.6);
      osc.frequency.linearRampToValueAtTime(noteFreq, t + eighthDur * 0.8);
      
      gain.gain.setValueAtTime(0, t);
      gain.gain.linearRampToValueAtTime(0.03, t + 0.01);
      gain.gain.exponentialRampToValueAtTime(0.001, t + eighthDur * 0.9);
      
      osc.connect(gain).connect(musicGain!);
      osc.start(t); osc.stop(t + eighthDur);
    }
  }
  
  currentChordIndex = (currentChordIndex + 1) % prog.length;
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
    currentProgIndex = 0;
    measureCount = 0;
    sectionCount = 0;
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
  musicIntensity = Math.min(5, Math.max(1, Math.floor(wave / 2) + 1));
}
