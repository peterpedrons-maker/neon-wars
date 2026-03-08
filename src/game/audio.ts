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
    const osc3 = ctx.createOscillator();
    const gain = ctx.createGain();
    const filter = ctx.createBiquadFilter();
    const dist = ctx.createWaveShaperNode();
    
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

// ===== HIGH-ENERGY ARCADE MUSIC ENGINE =====
// Inspired by Top Gear, Geometry Wars — fast, melodic, pumping

const PROGS = [
  // i-VI-III-VII (classic driving)
  [[0,3,7],[8,12,15],[3,7,10],[10,14,17]],
  // i-iv-VII-III (energetic)
  [[0,3,7],[5,8,12],[10,14,17],[3,7,10]],
  // i-VII-VI-V (heroic descent)
  [[0,3,7],[10,14,17],[8,12,15],[7,11,14]],
  // i-III-iv-VII (epic build)
  [[0,3,7],[3,7,10],[5,8,12],[10,14,17]],
  // vi-IV-I-V pop power
  [[0,3,7],[5,9,12],[7,11,14],[2,5,9]],
];

// Catchy melody patterns (scale degree indices into minor pentatonic + extras)
const MELODY_PHRASES = [
  // Top Gear inspired: fast runs + held notes
  [[0,2],[2,1],[4,1],[7,2],[5,1],[4,1],[2,2],[0,2],[4,1],[7,1],[9,2],[7,2]],
  // Geometry Wars: pulsing staccato + sweeps
  [[7,1],[7,1],[5,1],[4,1],[2,2],[0,1],[2,1],[4,2],[7,1],[9,1],[12,2],[7,2]],
  // Racing anthem: ascending power
  [[0,1],[2,1],[4,2],[7,1],[9,1],[12,2],[9,1],[7,1],[4,2],[2,1],[0,1]],
  // Intense chase
  [[12,1],[9,1],[7,2],[5,1],[4,1],[2,1],[0,1],[2,2],[4,1],[7,1],[9,2],[12,2]],
  // Triumphant
  [[0,3],[4,1],[7,2],[12,2],[9,1],[7,1],[4,2],[0,1],[2,1],[4,1],[7,3]],
  // Funky groove
  [[0,1],[0,1],[4,1],[5,1],[7,2],[4,1],[2,1],[0,2],[7,1],[9,1],[7,1],[4,1]],
];

// Bass rhythms (16th note grid, 1=hit 0=rest)
const BASS_RHYTHMS = [
  [1,0,0,1,0,0,1,0,1,0,0,1,0,0,1,0], // syncopated driving
  [1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0], // straight 8ths
  [1,0,0,1,0,1,0,0,1,0,0,1,0,1,0,0], // funky
  [1,1,0,1,1,0,1,0,1,1,0,1,1,0,1,0], // galloping
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
  wet.gain.value = 0.18;
  const delays = [0.025, 0.055, 0.09, 0.14, 0.2];
  const feedbacks = [0.35, 0.3, 0.25, 0.2, 0.15];
  for (let i = 0; i < delays.length; i++) {
    const delay = ctx.createDelay(0.5);
    delay.delayTime.value = delays[i];
    const fb = ctx.createGain();
    fb.gain.value = feedbacks[i];
    const filter = ctx.createBiquadFilter();
    filter.type = 'lowpass';
    filter.frequency.value = 3000 - i * 400;
    wet.connect(delay).connect(filter).connect(fb).connect(delay);
    filter.connect(output);
  }
  return wet;
}

function scheduleNextMeasure() {
  if (!musicPlaying || !audioCtx) return;
  const ctx = audioCtx;
  const now = ctx.currentTime;
  const bpm = 145; // Fast like Top Gear!
  const beatDur = 60 / bpm;
  const measureDur = beatDur * 4;
  const sixteenth = beatDur / 4;

  const isNewSection = measureCount > 0 && measureCount % 8 === 0;
  if (isNewSection) {
    sectionCount++;
    currentProgIndex = sectionCount % PROGS.length;
    if (measureCount % 24 === 0) {
      const keys = [33, 35, 38, 40, 36, 31, 28, 43];
      currentKey = keys[(sectionCount / 3 | 0) % keys.length];
    }
  }

  const prog = PROGS[currentProgIndex];
  const chord = prog[currentChordIndex % prog.length];
  const sectionFeel = sectionCount % 4; // 0=intro, 1=build, 2=drop, 3=breakdown
  const measureInSection = measureCount % 8;
  const isFillMeasure = measureInSection === 7;
  const intensity = musicIntensity;

  if (!musicGain) {
    musicGain = ctx.createGain();
    musicGain.gain.value = 0.065;
    compressor = ctx.createDynamicsCompressor();
    compressor.threshold.value = -15;
    compressor.knee.value = 6;
    compressor.ratio.value = 5;
    compressor.attack.value = 0.002;
    compressor.release.value = 0.1;
    musicGain.connect(compressor).connect(ctx.destination);
    reverbGain = createReverb(ctx, musicGain);
  }

  const masterVol = 0.055 + intensity * 0.01;
  musicGain.gain.setValueAtTime(masterVol, now);

  // ============ KICK ============
  const kickBeats = sectionFeel === 3
    ? (isFillMeasure ? [0, 0.25, 0.5, 0.75, 1, 1.25, 1.5, 1.75, 2, 2.25, 2.5, 2.75, 3, 3.25, 3.5, 3.75] : [0, 2])
    : [0, 1, 2, 3];

  for (const beat of kickBeats) {
    const t = now + beat * beatDur;
    // Punchy sub
    const sub = ctx.createOscillator();
    const subG = ctx.createGain();
    sub.type = 'sine';
    sub.frequency.setValueAtTime(180, t);
    sub.frequency.exponentialRampToValueAtTime(38, t + 0.12);
    subG.gain.setValueAtTime(0.22, t);
    subG.gain.exponentialRampToValueAtTime(0.001, t + 0.18);
    sub.connect(subG).connect(musicGain!);
    sub.start(t); sub.stop(t + 0.19);

    // Hard click
    const click = ctx.createOscillator();
    const clickG = ctx.createGain();
    click.type = 'square';
    click.frequency.setValueAtTime(6000, t);
    click.frequency.exponentialRampToValueAtTime(300, t + 0.01);
    clickG.gain.setValueAtTime(0.08, t);
    clickG.gain.exponentialRampToValueAtTime(0.001, t + 0.015);
    click.connect(clickG).connect(musicGain!);
    click.start(t); click.stop(t + 0.02);

    // Body punch
    const body = ctx.createOscillator();
    const bodyG = ctx.createGain();
    body.type = 'sine';
    body.frequency.setValueAtTime(100, t);
    body.frequency.exponentialRampToValueAtTime(42, t + 0.06);
    bodyG.gain.setValueAtTime(0.15, t);
    bodyG.gain.exponentialRampToValueAtTime(0.001, t + 0.08);
    body.connect(bodyG).connect(musicGain!);
    body.start(t); body.stop(t + 0.09);
  }

  // ============ SNARE on 2 & 4 ============
  if (sectionFeel !== 0 || measureInSection >= 2) {
    const snareBeats = isFillMeasure && sectionFeel === 1
      ? [1, 2, 2.5, 3, 3.25, 3.5, 3.75]
      : isFillMeasure
      ? [1, 2.5, 3, 3.5, 3.75]
      : [1, 3];

    for (const beat of snareBeats) {
      const t = now + beat * beatDur;
      for (let j = 0; j < 5; j++) {
        const n = ctx.createOscillator();
        const ng = ctx.createGain();
        const nf = ctx.createBiquadFilter();
        n.type = 'sawtooth';
        n.frequency.setValueAtTime(120 + Math.random() * 500, t);
        n.detune.setValueAtTime(Math.random() * 2400 - 1200, t);
        nf.type = 'bandpass';
        nf.frequency.value = 3500 + Math.random() * 2500;
        nf.Q.value = 0.4;
        ng.gain.setValueAtTime(0.035, t);
        ng.gain.exponentialRampToValueAtTime(0.001, t + 0.09 + Math.random() * 0.03);
        n.connect(nf).connect(ng).connect(musicGain!);
        if (reverbGain) ng.connect(reverbGain);
        n.start(t); n.stop(t + 0.14);
      }
      const sb = ctx.createOscillator();
      const sbg = ctx.createGain();
      sb.type = 'sine';
      sb.frequency.setValueAtTime(250, t);
      sb.frequency.exponentialRampToValueAtTime(130, t + 0.03);
      sbg.gain.setValueAtTime(0.08, t);
      sbg.gain.exponentialRampToValueAtTime(0.001, t + 0.05);
      sb.connect(sbg).connect(musicGain!);
      sb.start(t); sb.stop(t + 0.06);
    }
  }

  // ============ HI-HATS (fast & energetic) ============
  {
    const hatPatterns: number[][] = [
      [1,0,1,0, 1,0,1,0, 1,0,1,0, 1,0,1,0],
      [1,0,1,1, 0,1,1,0, 1,0,1,1, 0,1,1,0],
      [1,1,1,1, 1,1,1,1, 1,1,1,1, 1,1,1,1], // 16ths!
      [1,0,0,1, 0,1,0,1, 1,0,0,1, 0,1,0,1],
    ];
    const pIdx = sectionFeel === 2 ? 2 : sectionFeel === 1 ? 1 : sectionFeel === 3 ? 3 : 0;
    const pattern = hatPatterns[pIdx];

    for (let i = 0; i < 16; i++) {
      if (!pattern[i]) continue;
      const t = now + i * sixteenth;
      const isOpen = (i === 4 || i === 12) && sectionFeel >= 1;
      const osc = ctx.createOscillator();
      const g = ctx.createGain();
      const f = ctx.createBiquadFilter();
      osc.type = 'square';
      osc.frequency.setValueAtTime(9000 + Math.random() * 5000, t);
      f.type = 'highpass';
      f.frequency.value = 8000;
      const dur = isOpen ? 0.09 : 0.018;
      const vol = isOpen ? 0.022 : 0.014;
      g.gain.setValueAtTime(vol, t);
      g.gain.exponentialRampToValueAtTime(0.001, t + dur);
      osc.connect(f).connect(g).connect(musicGain!);
      osc.start(t); osc.stop(t + dur + 0.01);
    }
  }

  // ============ BASS LINE (driving, fat, syncopated) ============
  {
    const bpIdx = (sectionCount + (sectionFeel === 2 ? 1 : 0)) % BASS_RHYTHMS.length;
    const bp = sectionFeel === 3
      ? [1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0]
      : BASS_RHYTHMS[bpIdx];

    for (let i = 0; i < 16; i++) {
      if (!bp[i]) continue;
      const t = now + i * sixteenth;
      const bassNote = currentKey + chord[0];
      // Occasional octave jump for energy
      const octJump = (i === 8 || i === 12) && sectionFeel === 2 ? 12 : 0;
      const freq = midiToFreq(bassNote + octJump);

      // Triple-osc fat bass
      for (let d = -1; d <= 1; d++) {
        const osc = ctx.createOscillator();
        const g = ctx.createGain();
        const f = ctx.createBiquadFilter();
        osc.type = d === 0 ? 'sawtooth' : 'square';
        osc.frequency.setValueAtTime(freq * (1 + d * 0.004), t);
        f.type = 'lowpass';
        const fPeak = 350 + intensity * 120;
        f.frequency.setValueAtTime(fPeak + 600, t);
        f.frequency.exponentialRampToValueAtTime(fPeak, t + sixteenth * 0.7);
        f.Q.setValueAtTime(5, t);
        const vol = 0.065;
        g.gain.setValueAtTime(0, t);
        g.gain.linearRampToValueAtTime(vol, t + 0.004);
        g.gain.exponentialRampToValueAtTime(0.001, t + sixteenth * 0.8);
        osc.connect(f).connect(g).connect(musicGain!);
        osc.start(t); osc.stop(t + sixteenth);
      }

      // Sub sine
      const subB = ctx.createOscillator();
      const subBG = ctx.createGain();
      subB.type = 'sine';
      subB.frequency.setValueAtTime(freq / 2, t);
      subBG.gain.setValueAtTime(0.14, t);
      subBG.gain.exponentialRampToValueAtTime(0.001, t + sixteenth * 0.75);
      subB.connect(subBG).connect(musicGain!);
      subB.start(t); subB.stop(t + sixteenth);
    }
  }

  // ============ SYNTH PAD (warm, wide) ============
  if (sectionFeel === 0 || sectionFeel === 3 || (sectionFeel === 2 && measureInSection >= 4)) {
    const padVol = sectionFeel === 3 ? 0.045 : 0.035;
    for (let ci = 0; ci < chord.length; ci++) {
      const noteFreq = midiToFreq(currentKey + 12 + chord[ci]);
      for (let d = -2; d <= 2; d++) {
        const osc = ctx.createOscillator();
        const g = ctx.createGain();
        const f = ctx.createBiquadFilter();
        osc.type = d === 0 ? 'sine' : (Math.abs(d) === 1 ? 'triangle' : 'sawtooth');
        osc.frequency.setValueAtTime(noteFreq * (1 + d * 0.004), now);
        f.type = 'lowpass';
        const fBase = 500 + intensity * 120;
        f.frequency.setValueAtTime(fBase, now);
        f.frequency.linearRampToValueAtTime(fBase + 200, now + measureDur * 0.5);
        f.frequency.linearRampToValueAtTime(fBase, now + measureDur);
        const vol = padVol / 5;
        g.gain.setValueAtTime(0, now);
        g.gain.linearRampToValueAtTime(vol, now + measureDur * 0.1);
        g.gain.setValueAtTime(vol * 0.85, now + measureDur * 0.75);
        g.gain.exponentialRampToValueAtTime(0.001, now + measureDur + 0.1);
        osc.connect(f).connect(g).connect(musicGain!);
        if (reverbGain) g.connect(reverbGain);
        osc.start(now); osc.stop(now + measureDur + 0.15);
      }
    }
  }

  // ============ ARPEGGIOS (fast, sparkling, Top Gear style) ============
  if (sectionFeel >= 1) {
    const arpPatterns = [
      [0,1,2,0,1,2,0,1, 2,0,1,2,0,1,2,0],
      [0,2,1,0,2,1,0,2, 1,0,2,1,0,2,1,0],
      [2,1,0,2,1,0,2,1, 0,2,1,0,2,1,0,2],
      [0,1,2,1,0,1,2,1, 0,1,2,1,0,1,2,1],
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
    const steps = sectionFeel === 2 ? 16 : (measureInSection >= 4 ? 16 : 8);

    for (let i = 0; i < steps; i++) {
      const chordNote = chord[arpP[i] % chord.length];
      const oct = (octP[i] || 0) * 12;
      const noteFreq = midiToFreq(currentKey + 24 + chordNote + oct);
      const t = now + i * sixteenth;

      const osc = ctx.createOscillator();
      const osc2 = ctx.createOscillator();
      const g = ctx.createGain();
      const f = ctx.createBiquadFilter();
      osc.type = 'sawtooth';
      osc2.type = 'sawtooth';
      osc.frequency.setValueAtTime(noteFreq, t);
      osc2.frequency.setValueAtTime(noteFreq * 1.006, t);
      f.type = 'lowpass';
      f.frequency.setValueAtTime(2500 + intensity * 400, t);
      f.frequency.exponentialRampToValueAtTime(900, t + sixteenth * 0.8);
      f.Q.setValueAtTime(3, t);
      const vol = 0.022 + intensity * 0.005;
      const accent = i % 4 === 0 ? 1.4 : (i % 2 === 0 ? 1.1 : 1.0);
      g.gain.setValueAtTime(0, t);
      g.gain.linearRampToValueAtTime(vol * accent, t + 0.002);
      g.gain.exponentialRampToValueAtTime(0.001, t + sixteenth * 0.8);
      osc.connect(f);
      osc2.connect(f);
      f.connect(g).connect(musicGain!);
      if (reverbGain && i % 3 === 0) g.connect(reverbGain);
      osc.start(t); osc.stop(t + sixteenth);
      osc2.start(t); osc2.stop(t + sixteenth);
    }
  }

  // ============ LEAD MELODY (catchy, memorable, Top Gear / Geometry Wars) ============
  if ((sectionFeel === 2 || (sectionFeel === 1 && measureInSection >= 4)) && intensity >= 1) {
    const minorScale = [0, 2, 3, 5, 7, 8, 10, 12, 14, 15, 17, 19, 20, 22, 24];
    const phraseIdx = (sectionCount * 2 + measureCount) % MELODY_PHRASES.length;
    const phrase = MELODY_PHRASES[phraseIdx];

    let step = 0;
    for (let i = 0; i < phrase.length; i++) {
      const [noteIdx, durSteps] = phrase[i];
      if (step >= 16) break;
      const t = now + step * sixteenth;
      const dur = durSteps * sixteenth;
      const scaleDeg = noteIdx % minorScale.length;
      const note = minorScale[scaleDeg];
      const noteFreq = midiToFreq(currentKey + 36 + note);

      // Bright lead: square + saw
      const osc = ctx.createOscillator();
      const osc2 = ctx.createOscillator();
      const osc3 = ctx.createOscillator();
      const g = ctx.createGain();
      const f = ctx.createBiquadFilter();

      osc.type = 'square';
      osc2.type = 'sawtooth';
      osc3.type = 'sine'; // sub harmonics for warmth
      osc.frequency.setValueAtTime(noteFreq, t);
      osc2.frequency.setValueAtTime(noteFreq * 1.003, t);
      osc3.frequency.setValueAtTime(noteFreq * 0.5, t);

      // Vibrato on held notes
      if (durSteps >= 3) {
        const lfo = ctx.createOscillator();
        const lfoG = ctx.createGain();
        lfo.type = 'sine';
        lfo.frequency.value = 6;
        lfoG.gain.value = noteFreq * 0.01;
        lfo.connect(lfoG).connect(osc.frequency);
        lfo.connect(lfoG).connect(osc2.frequency);
        lfo.start(t + dur * 0.25); lfo.stop(t + dur);
      }

      // Portamento on fast notes
      if (durSteps === 1 && i < phrase.length - 1) {
        const nextNote = minorScale[phrase[i + 1][0] % minorScale.length];
        const nextFreq = midiToFreq(currentKey + 36 + nextNote);
        osc.frequency.linearRampToValueAtTime(nextFreq, t + dur * 0.9);
        osc2.frequency.linearRampToValueAtTime(nextFreq * 1.003, t + dur * 0.9);
      }

      f.type = 'lowpass';
      f.frequency.setValueAtTime(4000 + intensity * 600, t);
      f.frequency.exponentialRampToValueAtTime(2000, t + dur * 0.7);
      f.Q.value = 1.5;

      const vol = 0.03 + intensity * 0.004;
      g.gain.setValueAtTime(0, t);
      g.gain.linearRampToValueAtTime(vol, t + 0.005);
      if (durSteps >= 2) {
        g.gain.setValueAtTime(vol * 0.85, t + dur * 0.4);
      }
      g.gain.exponentialRampToValueAtTime(0.001, t + dur * 0.92);

      osc.connect(f);
      osc2.connect(f);
      osc3.connect(f);
      f.connect(g).connect(musicGain!);
      if (reverbGain) g.connect(reverbGain);
      osc.start(t); osc.stop(t + dur + 0.01);
      osc2.start(t); osc2.stop(t + dur + 0.01);
      osc3.start(t); osc3.stop(t + dur + 0.01);

      step += durSteps;
    }
  }

  // ============ COUNTER-MELODY / HARMONY (adds depth at high intensity) ============
  if (sectionFeel === 2 && intensity >= 3 && measureInSection % 2 === 0) {
    const counterNotes = [chord[2], chord[0], chord[1], chord[2]];
    for (let i = 0; i < 4; i++) {
      const t = now + i * beatDur;
      const noteFreq = midiToFreq(currentKey + 48 + counterNotes[i]);
      const osc = ctx.createOscillator();
      const g = ctx.createGain();
      const f = ctx.createBiquadFilter();
      osc.type = 'triangle';
      osc.frequency.setValueAtTime(noteFreq, t);
      f.type = 'lowpass';
      f.frequency.value = 2500;
      g.gain.setValueAtTime(0, t);
      g.gain.linearRampToValueAtTime(0.018, t + 0.01);
      g.gain.exponentialRampToValueAtTime(0.001, t + beatDur * 0.7);
      osc.connect(f).connect(g).connect(musicGain!);
      if (reverbGain) g.connect(reverbGain);
      osc.start(t); osc.stop(t + beatDur);
    }
  }

  // ============ RISERS & TRANSITIONS ============
  if (isFillMeasure) {
    if (sectionFeel === 1 || sectionFeel === 3) {
      // White noise riser
      const riser = ctx.createOscillator();
      const rG = ctx.createGain();
      const rF = ctx.createBiquadFilter();
      riser.type = 'sawtooth';
      riser.frequency.setValueAtTime(150, now);
      riser.frequency.exponentialRampToValueAtTime(3000, now + measureDur);
      riser.detune.setValueAtTime(0, now);
      riser.detune.linearRampToValueAtTime(1200, now + measureDur);
      rF.type = 'bandpass';
      rF.frequency.setValueAtTime(300, now);
      rF.frequency.exponentialRampToValueAtTime(6000, now + measureDur);
      rF.Q.value = 2;
      rG.gain.setValueAtTime(0, now);
      rG.gain.linearRampToValueAtTime(0.05, now + measureDur * 0.85);
      rG.gain.exponentialRampToValueAtTime(0.001, now + measureDur);
      riser.connect(rF).connect(rG).connect(musicGain!);
      riser.start(now); riser.stop(now + measureDur + 0.01);

      // Second riser (octave up)
      const riser2 = ctx.createOscillator();
      const r2G = ctx.createGain();
      riser2.type = 'square';
      riser2.frequency.setValueAtTime(300, now);
      riser2.frequency.exponentialRampToValueAtTime(5000, now + measureDur);
      r2G.gain.setValueAtTime(0, now);
      r2G.gain.linearRampToValueAtTime(0.02, now + measureDur * 0.9);
      r2G.gain.exponentialRampToValueAtTime(0.001, now + measureDur);
      riser2.connect(r2G).connect(musicGain!);
      riser2.start(now); riser2.stop(now + measureDur + 0.01);
    }

    // Crash cymbal into drop
    if (sectionFeel === 1) {
      const t = now + measureDur - 0.01;
      for (let j = 0; j < 4; j++) {
        const crash = ctx.createOscillator();
        const cg = ctx.createGain();
        crash.type = 'sawtooth';
        crash.frequency.setValueAtTime(5000 + Math.random() * 6000, t);
        crash.detune.setValueAtTime(Math.random() * 3000, t);
        cg.gain.setValueAtTime(0.035, t);
        cg.gain.exponentialRampToValueAtTime(0.001, t + 0.6);
        crash.connect(cg).connect(musicGain!);
        crash.start(t); crash.stop(t + 0.65);
      }
    }

    // Reverse impact before drops
    if (sectionFeel === 3) {
      const impact = ctx.createOscillator();
      const ig = ctx.createGain();
      impact.type = 'sine';
      impact.frequency.setValueAtTime(40, now + measureDur - 0.15);
      impact.frequency.exponentialRampToValueAtTime(20, now + measureDur);
      ig.gain.setValueAtTime(0, now + measureDur - 0.15);
      ig.gain.linearRampToValueAtTime(0.2, now + measureDur - 0.02);
      ig.gain.exponentialRampToValueAtTime(0.001, now + measureDur + 0.3);
      impact.connect(ig).connect(musicGain!);
      impact.start(now + measureDur - 0.15); impact.stop(now + measureDur + 0.35);
    }
  }

  // ============ AMBIENT TEXTURE (breakdowns) ============
  if (sectionFeel === 3) {
    const washOsc = ctx.createOscillator();
    const washG = ctx.createGain();
    const washF = ctx.createBiquadFilter();
    washOsc.type = 'sawtooth';
    washOsc.frequency.setValueAtTime(35 + Math.random() * 25, now);
    washOsc.detune.setValueAtTime(1200, now);
    washF.type = 'bandpass';
    washF.frequency.setValueAtTime(250, now);
    washF.frequency.linearRampToValueAtTime(900, now + measureDur * 0.5);
    washF.frequency.linearRampToValueAtTime(250, now + measureDur);
    washF.Q.value = 0.4;
    washG.gain.setValueAtTime(0.018, now);
    washG.gain.exponentialRampToValueAtTime(0.001, now + measureDur);
    washOsc.connect(washF).connect(washG).connect(musicGain!);
    if (reverbGain) washG.connect(reverbGain);
    washOsc.start(now); washOsc.stop(now + measureDur + 0.01);
  }

  // ============ ENERGY STABS (drop accents, Geometry Wars vibes) ============
  if (sectionFeel === 2 && (measureInSection === 0 || measureInSection === 4)) {
    // Power chord stab on beat 1
    for (let ci = 0; ci < chord.length; ci++) {
      const noteFreq = midiToFreq(currentKey + 24 + chord[ci]);
      for (let d = -1; d <= 1; d++) {
        const osc = ctx.createOscillator();
        const g = ctx.createGain();
        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(noteFreq * (1 + d * 0.008), now);
        g.gain.setValueAtTime(0.04, now);
        g.gain.exponentialRampToValueAtTime(0.001, now + beatDur * 0.4);
        osc.connect(g).connect(musicGain!);
        osc.start(now); osc.stop(now + beatDur * 0.45);
      }
    }
  }

  currentChordIndex = (currentChordIndex + 1) % prog.length;
  measureCount++;

  const nextTime = (measureDur - 0.05) * 1000;
  const timer = window.setTimeout(scheduleNextMeasure, nextTime);
  musicTimers.push(timer);
}

export function startMusic() {
  if (musicPlaying) return;
  stopMenuMusic();
  try {
    getCtx();
    musicPlaying = true;
    musicGain = null;
    compressor = null;
    reverbGain = null;
    currentChordIndex = 0;
    currentProgIndex = 0;
    measureCount = 0;
    sectionCount = 0;
    currentKey = 33;
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

// ===== MENU MUSIC (chill, atmospheric synthwave) =====
let menuMusicPlaying = false;
let menuTimers: number[] = [];
let menuGain: GainNode | null = null;
let menuMeasure = 0;

const MENU_CHORDS = [
  [[0,3,7,12], [8,12,15,20], [3,7,10,15], [10,14,17,22]],
  [[0,3,7,12], [5,8,12,17], [8,12,15,20], [7,11,14,19]],
];

function scheduleMenuMeasure() {
  if (!menuMusicPlaying || !audioCtx) return;
  const ctx = audioCtx;
  const now = ctx.currentTime;
  const bpm = 90;
  const beatDur = 60 / bpm;
  const measureDur = beatDur * 4;
  const sixteenth = beatDur / 4;

  if (!menuGain) {
    menuGain = ctx.createGain();
    menuGain.gain.value = 0.05;
    menuGain.connect(ctx.destination);
  }

  const prog = MENU_CHORDS[menuMeasure % MENU_CHORDS.length];
  const chord = prog[menuMeasure % prog.length];
  const key = 33;

  // Warm pad
  for (let ci = 0; ci < chord.length; ci++) {
    const noteFreq = midiToFreq(key + 12 + chord[ci]);
    for (let d = -2; d <= 2; d++) {
      const osc = ctx.createOscillator();
      const g = ctx.createGain();
      const f = ctx.createBiquadFilter();
      osc.type = d === 0 ? 'sine' : (Math.abs(d) === 1 ? 'triangle' : 'sawtooth');
      osc.frequency.setValueAtTime(noteFreq * (1 + d * 0.003), now);
      f.type = 'lowpass';
      f.frequency.setValueAtTime(600, now);
      f.frequency.linearRampToValueAtTime(800, now + measureDur * 0.5);
      f.frequency.linearRampToValueAtTime(600, now + measureDur);
      const vol = 0.012;
      g.gain.setValueAtTime(0, now);
      g.gain.linearRampToValueAtTime(vol, now + measureDur * 0.15);
      g.gain.setValueAtTime(vol * 0.8, now + measureDur * 0.7);
      g.gain.exponentialRampToValueAtTime(0.001, now + measureDur + 0.1);
      osc.connect(f).connect(g).connect(menuGain!);
      osc.start(now); osc.stop(now + measureDur + 0.15);
    }
  }

  // Gentle arpeggio
  const arpPattern = [0, 2, 1, 0, 2, 1, 0, 2];
  for (let i = 0; i < 8; i++) {
    const chordNote = chord[arpPattern[i] % chord.length];
    const oct = (i % 3 === 0 ? 12 : 0);
    const noteFreq = midiToFreq(key + 24 + chordNote + oct);
    const t = now + i * (beatDur / 2);
    const osc = ctx.createOscillator();
    const g = ctx.createGain();
    const f = ctx.createBiquadFilter();
    osc.type = 'triangle';
    osc.frequency.setValueAtTime(noteFreq, t);
    f.type = 'lowpass';
    f.frequency.setValueAtTime(1500, t);
    f.frequency.exponentialRampToValueAtTime(600, t + beatDur * 0.4);
    g.gain.setValueAtTime(0, t);
    g.gain.linearRampToValueAtTime(0.015, t + 0.005);
    g.gain.exponentialRampToValueAtTime(0.001, t + beatDur * 0.45);
    osc.connect(f).connect(g).connect(menuGain!);
    osc.start(t); osc.stop(t + beatDur * 0.5);
  }

  // Soft sub bass
  const bassFreq = midiToFreq(key + chord[0]);
  const bass = ctx.createOscillator();
  const bg = ctx.createGain();
  bass.type = 'sine';
  bass.frequency.setValueAtTime(bassFreq, now);
  bg.gain.setValueAtTime(0.04, now);
  bg.gain.exponentialRampToValueAtTime(0.001, now + measureDur * 0.8);
  bass.connect(bg).connect(menuGain!);
  bass.start(now); bass.stop(now + measureDur);

  menuMeasure++;
  const timer = window.setTimeout(scheduleMenuMeasure, (measureDur - 0.05) * 1000);
  menuTimers.push(timer);
}

export function startMenuMusic() {
  if (menuMusicPlaying || musicPlaying) return;
  try {
    getCtx();
    menuMusicPlaying = true;
    menuGain = null;
    menuMeasure = 0;
    scheduleMenuMeasure();
  } catch {}
}

export function stopMenuMusic() {
  menuMusicPlaying = false;
  menuTimers.forEach(t => clearTimeout(t));
  menuTimers = [];
  if (menuGain) {
    try { menuGain.gain.linearRampToValueAtTime(0, audioCtx!.currentTime + 0.5); } catch {}
  }
}
