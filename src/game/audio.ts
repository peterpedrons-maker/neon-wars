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
    const dur = big ? 0.5 : 0.2;
    const vol = big ? 0.12 : 0.07;
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

// ===== PROCEDURAL SYNTHWAVE MUSIC ENGINE =====
// Full synthwave track with proper song structure, fills, transitions, and evolving layers

// Chord progressions in semitone intervals from root (minor key)
// Each progression has 4 chords, each chord is an array of semitone offsets
const PROGRESSIONS = [
  // i - VI - III - VII (classic synthwave)
  [[0, 3, 7, 12], [8, 12, 15, 20], [3, 7, 10, 15], [10, 14, 17, 22]],
  // i - iv - VI - V (emotional)
  [[0, 3, 7, 12], [5, 8, 12, 17], [8, 12, 15, 20], [7, 11, 14, 19]],
  // i - VII - VI - VII (driving)
  [[0, 3, 7, 12], [10, 14, 17, 22], [8, 12, 15, 20], [10, 14, 17, 22]],
  // i - III - VII - iv (melancholic)
  [[0, 3, 7, 12], [3, 7, 10, 15], [10, 14, 17, 22], [5, 8, 12, 17]],
  // i - v - VI - iv (dark pop)
  [[0, 3, 7, 12], [7, 10, 14, 19], [8, 12, 15, 20], [5, 8, 12, 17]],
  // vi - IV - I - V reinterpreted in minor context
  [[0, 3, 7, 14], [5, 9, 12, 17], [3, 7, 12, 19], [7, 11, 14, 19]],
];

let musicTimers: number[] = [];
let currentChordIndex = 0;
let currentProgIndex = 0;
let measureCount = 0;
let currentKey = 33; // A1 MIDI base for deep bass
let sectionCount = 0;
let compressor: DynamicsCompressorNode | null = null;
let reverbGain: GainNode | null = null;

function midiToFreq(midi: number): number {
  return 440 * Math.pow(2, (midi - 69) / 12);
}

// Simple reverb using feedback delay
function createReverb(ctx: AudioContext, output: AudioNode): GainNode {
  const wet = ctx.createGain();
  wet.gain.value = 0.15;
  
  const delays = [0.03, 0.07, 0.11, 0.17];
  const feedbacks = [0.3, 0.25, 0.2, 0.15];
  
  for (let i = 0; i < delays.length; i++) {
    const delay = ctx.createDelay(0.5);
    delay.delayTime.value = delays[i];
    const fb = ctx.createGain();
    fb.gain.value = feedbacks[i];
    const filter = ctx.createBiquadFilter();
    filter.type = 'lowpass';
    filter.frequency.value = 2000 - i * 300;
    
    wet.connect(delay).connect(filter).connect(fb).connect(delay);
    filter.connect(output);
  }
  
  return wet;
}

function scheduleNextMeasure() {
  if (!musicPlaying || !audioCtx) return;
  const ctx = audioCtx;
  const now = ctx.currentTime;
  const bpm = 128;
  const beatDur = 60 / bpm;
  const measureDur = beatDur * 4;
  const sixteenth = beatDur / 4;
  
  // Song structure: 8-measure sections
  const isNewSection = measureCount > 0 && measureCount % 8 === 0;
  if (isNewSection) {
    sectionCount++;
    currentProgIndex = sectionCount % PROGRESSIONS.length;
    // Key changes every 32 measures (keeps it fresh but not jarring)
    if (measureCount % 32 === 0) {
      const keys = [33, 35, 38, 40, 31, 36, 28]; // A1, B1, D2, E2, G1, C2, E1
      currentKey = keys[(sectionCount / 4 | 0) % keys.length];
    }
  }
  
  const prog = PROGRESSIONS[currentProgIndex];
  const chord = prog[currentChordIndex % prog.length];
  const nextChord = prog[(currentChordIndex + 1) % prog.length];
  
  // Section feel cycles: intro(0) → build(1) → drop(2) → breakdown(3)
  const sectionFeel = sectionCount % 4;
  const measureInSection = measureCount % 8;
  const isFillMeasure = measureInSection === 7; // last measure = fill/transition
  
  // Setup master chain
  if (!musicGain) {
    musicGain = ctx.createGain();
    musicGain.gain.value = 0.06;
    compressor = ctx.createDynamicsCompressor();
    compressor.threshold.value = -18;
    compressor.knee.value = 8;
    compressor.ratio.value = 4;
    compressor.attack.value = 0.003;
    compressor.release.value = 0.15;
    musicGain.connect(compressor).connect(ctx.destination);
    reverbGain = createReverb(ctx, musicGain);
  }
  
  const masterVol = 0.05 + musicIntensity * 0.008;
  musicGain.gain.setValueAtTime(masterVol, now);

  // ============ KICK DRUM ============
  const kickPattern = sectionFeel === 3 
    ? (isFillMeasure ? [0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5] : [0, 2]) // breakdown: sparse or build fill
    : [0, 1, 2, 3]; // four-on-the-floor
    
  for (const beat of kickPattern) {
    const t = now + beat * beatDur;
    // Sub layer
    const sub = ctx.createOscillator();
    const subG = ctx.createGain();
    sub.type = 'sine';
    sub.frequency.setValueAtTime(150, t);
    sub.frequency.exponentialRampToValueAtTime(35, t + 0.15);
    subG.gain.setValueAtTime(0.18, t);
    subG.gain.exponentialRampToValueAtTime(0.001, t + 0.2);
    sub.connect(subG).connect(musicGain!);
    sub.start(t); sub.stop(t + 0.21);
    
    // Click transient
    const click = ctx.createOscillator();
    const clickG = ctx.createGain();
    const clickF = ctx.createBiquadFilter();
    click.type = 'square';
    click.frequency.setValueAtTime(4000, t);
    click.frequency.exponentialRampToValueAtTime(200, t + 0.015);
    clickF.type = 'bandpass';
    clickF.frequency.value = 3000;
    clickF.Q.value = 1;
    clickG.gain.setValueAtTime(0.06, t);
    clickG.gain.exponentialRampToValueAtTime(0.001, t + 0.02);
    click.connect(clickF).connect(clickG).connect(musicGain!);
    click.start(t); click.stop(t + 0.03);
    
    // Punch body
    const body = ctx.createOscillator();
    const bodyG = ctx.createGain();
    body.type = 'sine';
    body.frequency.setValueAtTime(80, t);
    body.frequency.exponentialRampToValueAtTime(40, t + 0.08);
    bodyG.gain.setValueAtTime(0.12, t);
    bodyG.gain.exponentialRampToValueAtTime(0.001, t + 0.1);
    body.connect(bodyG).connect(musicGain!);
    body.start(t); body.stop(t + 0.11);
  }

  // ============ CLAP/SNARE on 2 & 4 ============
  if (sectionFeel !== 0 || measureInSection >= 4) {
    const snareBeats = isFillMeasure && sectionFeel === 1 
      ? [1, 2, 2.5, 3, 3.25, 3.5, 3.75] // build fill
      : [1, 3];
      
    for (const beat of snareBeats) {
      const t = now + beat * beatDur;
      // Noise burst (multiple detuned oscillators)
      for (let j = 0; j < 4; j++) {
        const n = ctx.createOscillator();
        const ng = ctx.createGain();
        const nf = ctx.createBiquadFilter();
        n.type = 'sawtooth';
        n.frequency.setValueAtTime(150 + Math.random() * 400, t);
        n.detune.setValueAtTime(Math.random() * 2400 - 1200, t);
        nf.type = 'bandpass';
        nf.frequency.value = 3000 + Math.random() * 2000;
        nf.Q.value = 0.5;
        ng.gain.setValueAtTime(0.03, t);
        ng.gain.exponentialRampToValueAtTime(0.001, t + 0.1 + Math.random() * 0.03);
        n.connect(nf).connect(ng).connect(musicGain!);
        if (reverbGain) ng.connect(reverbGain);
        n.start(t); n.stop(t + 0.15);
      }
      // Snare body tone
      const sb = ctx.createOscillator();
      const sbg = ctx.createGain();
      sb.type = 'sine';
      sb.frequency.setValueAtTime(220, t);
      sb.frequency.exponentialRampToValueAtTime(120, t + 0.04);
      sbg.gain.setValueAtTime(0.06, t);
      sbg.gain.exponentialRampToValueAtTime(0.001, t + 0.06);
      sb.connect(sbg).connect(musicGain!);
      sb.start(t); sb.stop(t + 0.07);
    }
  }

  // ============ HI-HATS ============
  {
    const hatPatterns: number[][] = [
      [1,0,1,0, 1,0,1,0, 1,0,1,0, 1,0,1,0],       // straight 8ths
      [1,0,1,1, 0,1,0,1, 1,0,1,1, 0,1,0,1],       // syncopated
      [1,1,1,1, 1,1,1,1, 1,1,1,1, 1,1,1,1],       // 16ths (intense)
      [1,0,0,1, 0,0,1,0, 0,1,0,0, 1,0,0,1],       // sparse groove
    ];
    const pIdx = sectionFeel === 2 ? 2 : sectionFeel === 3 ? 3 : sectionFeel === 1 ? 1 : 0;
    const pattern = hatPatterns[pIdx];
    
    for (let i = 0; i < 16; i++) {
      if (!pattern[i]) continue;
      const t = now + i * sixteenth;
      const isOpen = (i === 4 || i === 12) && sectionFeel >= 1;
      
      const osc = ctx.createOscillator();
      const g = ctx.createGain();
      const f = ctx.createBiquadFilter();
      osc.type = 'square';
      osc.frequency.setValueAtTime(8000 + Math.random() * 4000, t);
      f.type = 'highpass';
      f.frequency.value = 7000;
      
      const dur = isOpen ? 0.08 : 0.02;
      const vol = isOpen ? 0.018 : 0.012;
      g.gain.setValueAtTime(vol, t);
      g.gain.exponentialRampToValueAtTime(0.001, t + dur);
      
      osc.connect(f).connect(g).connect(musicGain!);
      osc.start(t); osc.stop(t + dur + 0.01);
    }
  }

  // ============ DEEP BASS LINE ============
  {
    // Bass patterns per section feel
    const bassPatterns: number[][] = [
      [0, -1, -1, -1, 0, -1, 2, -1],           // simple (intro)
      [0, -1, 0, -1, 0, 0, -1, 0],             // pumping (build)
      [0, 0, -1, 0, 0, -1, 0, 0, -1, 0, 0, -1, 0, 0, -1, 0], // driving 16ths (drop)
      [0, -1, -1, -1, -1, -1, -1, -1, 0, -1, -1, -1, -1, -1, -1, -1], // sparse (breakdown)
    ];
    
    const bp = bassPatterns[sectionFeel];
    const stepDur = sectionFeel === 2 || sectionFeel === 3 ? sixteenth : beatDur / 2;
    
    for (let i = 0; i < bp.length; i++) {
      if (bp[i] === -1) continue;
      const t = now + i * stepDur;
      
      // Root note of current chord
      const bassNote = currentKey + chord[0];
      const freq = midiToFreq(bassNote);
      
      const osc1 = ctx.createOscillator();
      const osc2 = ctx.createOscillator();
      const osc3 = ctx.createOscillator();
      const g = ctx.createGain();
      const f = ctx.createBiquadFilter();
      
      osc1.type = 'sawtooth';
      osc2.type = 'sawtooth';
      osc3.type = 'square';
      osc1.frequency.setValueAtTime(freq, t);
      osc2.frequency.setValueAtTime(freq * 1.003, t); // detune for width
      osc3.frequency.setValueAtTime(freq * 0.997, t);
      
      f.type = 'lowpass';
      // Filter envelope - opens on attack then closes
      const filterBase = 200 + musicIntensity * 80;
      const filterPeak = filterBase + 800;
      f.frequency.setValueAtTime(filterPeak, t);
      f.frequency.exponentialRampToValueAtTime(filterBase, t + stepDur * 0.6);
      f.Q.setValueAtTime(6, t);
      
      const dur = Math.min(stepDur * 0.85, 0.35);
      g.gain.setValueAtTime(0, t);
      g.gain.linearRampToValueAtTime(0.2, t + 0.005);
      g.gain.setValueAtTime(0.16, t + dur * 0.3);
      g.gain.exponentialRampToValueAtTime(0.001, t + dur);
      
      osc1.connect(f);
      osc2.connect(f);
      osc3.connect(f);
      f.connect(g).connect(musicGain!);
      osc1.start(t); osc1.stop(t + dur + 0.01);
      osc2.start(t); osc2.stop(t + dur + 0.01);
      osc3.start(t); osc3.stop(t + dur + 0.01);
      
      // Sub bass layer (pure sine one octave down)
      const subBass = ctx.createOscillator();
      const subG = ctx.createGain();
      subBass.type = 'sine';
      subBass.frequency.setValueAtTime(freq / 2, t);
      subG.gain.setValueAtTime(0.12, t);
      subG.gain.exponentialRampToValueAtTime(0.001, t + dur);
      subBass.connect(subG).connect(musicGain!);
      subBass.start(t); subBass.stop(t + dur + 0.01);
    }
  }

  // ============ SYNTH PAD (lush, wide, evolving) ============
  if (sectionFeel !== 2 || measureInSection < 4) {
    const padVol = sectionFeel === 3 ? 0.06 : sectionFeel === 0 ? 0.05 : 0.035;
    
    for (let ci = 0; ci < chord.length; ci++) {
      const noteFreq = midiToFreq(currentKey + 12 + chord[ci]);
      
      // 5 detuned oscillators for super-saw pad
      for (let d = -2; d <= 2; d++) {
        const osc = ctx.createOscillator();
        const g = ctx.createGain();
        const f = ctx.createBiquadFilter();
        
        osc.type = d === 0 ? 'sine' : (Math.abs(d) === 1 ? 'triangle' : 'sawtooth');
        osc.frequency.setValueAtTime(noteFreq * (1 + d * 0.003), now);
        
        f.type = 'lowpass';
        // Slow filter sweep across the measure
        const fBase = 400 + musicIntensity * 100;
        const fMod = Math.sin(measureCount * 0.15 + ci * 0.5) * 200;
        f.frequency.setValueAtTime(fBase + fMod, now);
        f.frequency.linearRampToValueAtTime(fBase + fMod + 150, now + measureDur * 0.5);
        f.frequency.linearRampToValueAtTime(fBase + fMod, now + measureDur);
        
        const vol = padVol / 5;
        g.gain.setValueAtTime(0, now);
        g.gain.linearRampToValueAtTime(vol, now + measureDur * 0.15);
        g.gain.setValueAtTime(vol * 0.9, now + measureDur * 0.7);
        g.gain.exponentialRampToValueAtTime(0.001, now + measureDur + 0.1);
        
        osc.connect(f).connect(g).connect(musicGain!);
        if (reverbGain) g.connect(reverbGain);
        osc.start(now); osc.stop(now + measureDur + 0.15);
      }
    }
  }

  // ============ ARPEGGIOS ============
  if (sectionFeel === 1 || sectionFeel === 2) {
    // Multiple arp patterns for variety
    const arpOctavePatterns = [
      [0, 0, 1, 1, 2, 2, 1, 1, 0, 0, 1, 1, 2, 2, 1, 0],  // ascending wave
      [2, 1, 0, 1, 2, 1, 0, 1, 2, 0, 1, 2, 0, 1, 2, 1],  // descending bounce
      [0, 2, 1, 0, 2, 1, 0, 2, 1, 0, 2, 1, 0, 1, 2, 0],  // skip pattern
    ];
    const arpNoteIndices = [
      [0, 1, 2, 3, 2, 1, 0, 3, 0, 1, 2, 3, 2, 1, 0, 3],
      [0, 2, 1, 3, 0, 2, 1, 3, 0, 2, 1, 3, 0, 2, 1, 3],
      [3, 2, 1, 0, 3, 2, 1, 0, 3, 1, 0, 2, 3, 1, 0, 2],
    ];
    
    const patIdx = (sectionCount + measureCount) % arpOctavePatterns.length;
    const octPattern = arpOctavePatterns[patIdx];
    const notePattern = arpNoteIndices[patIdx];
    const arpSteps = sectionFeel === 2 ? 16 : (measureInSection >= 4 ? 16 : 8);
    
    for (let i = 0; i < arpSteps; i++) {
      const chordNote = chord[notePattern[i] % chord.length];
      const octShift = octPattern[i] * 12;
      const noteFreq = midiToFreq(currentKey + 24 + chordNote + octShift);
      const t = now + i * sixteenth;
      
      const osc = ctx.createOscillator();
      const osc2 = ctx.createOscillator();
      const g = ctx.createGain();
      const f = ctx.createBiquadFilter();
      
      // PWM-like sound with detuned pair
      osc.type = 'sawtooth';
      osc2.type = 'sawtooth';
      osc.frequency.setValueAtTime(noteFreq, t);
      osc2.frequency.setValueAtTime(noteFreq * 1.005, t);
      
      f.type = 'lowpass';
      f.frequency.setValueAtTime(2000 + musicIntensity * 300, t);
      f.frequency.exponentialRampToValueAtTime(800, t + sixteenth * 0.85);
      f.Q.setValueAtTime(2, t);
      
      const vol = 0.02 + musicIntensity * 0.004;
      // Accent every 4th note
      const accent = i % 4 === 0 ? 1.3 : 1.0;
      g.gain.setValueAtTime(0, t);
      g.gain.linearRampToValueAtTime(vol * accent, t + 0.003);
      g.gain.exponentialRampToValueAtTime(0.001, t + sixteenth * 0.85);
      
      osc.connect(f);
      osc2.connect(f);
      f.connect(g).connect(musicGain!);
      if (reverbGain && i % 2 === 0) g.connect(reverbGain);
      osc.start(t); osc.stop(t + sixteenth);
      osc2.start(t); osc2.stop(t + sixteenth);
    }
  }

  // ============ LEAD MELODY (drop sections, high intensity) ============
  if (sectionFeel === 2 && musicIntensity >= 2) {
    // Generate melodic phrases based on chord tones + passing tones
    const scaleNotes = [0, 2, 3, 5, 7, 8, 10, 12, 14, 15, 17, 19]; // natural minor extended
    const melodyRhythms = [
      // [step, duration_in_16ths]
      [[0, 2], [2, 1], [3, 1], [4, 2], [6, 2], [8, 2], [10, 1], [11, 1], [12, 3]],
      [[0, 3], [3, 1], [4, 2], [6, 1], [7, 1], [8, 4], [12, 2], [14, 2]],
      [[0, 1], [1, 1], [2, 2], [4, 1], [5, 1], [6, 2], [8, 3], [11, 1], [12, 4]],
      [[0, 4], [4, 2], [6, 2], [8, 1], [9, 1], [10, 1], [11, 1], [12, 4]],
    ];
    
    const melIdx = (sectionCount * 3 + measureCount) % melodyRhythms.length;
    const rhythm = melodyRhythms[melIdx];
    
    // Generate melody notes using chord tones and scale
    const seed = (measureCount * 7 + sectionCount * 13) & 0xFFFF;
    
    for (let i = 0; i < rhythm.length; i++) {
      const [step, durSteps] = rhythm[i];
      const t = now + step * sixteenth;
      const dur = durSteps * sixteenth;
      
      // Pick note: prefer chord tones, occasionally use scale passing tones
      const noteChoice = ((seed + i * 31) % 12);
      let note: number;
      if (noteChoice < 7) {
        note = chord[noteChoice % chord.length]; // chord tone
      } else {
        note = scaleNotes[((seed + i * 17) % scaleNotes.length)]; // scale tone
      }
      
      const noteFreq = midiToFreq(currentKey + 36 + note); // high octave
      
      const osc = ctx.createOscillator();
      const osc2 = ctx.createOscillator();
      const g = ctx.createGain();
      const f = ctx.createBiquadFilter();
      
      osc.type = 'square';
      osc2.type = 'sawtooth';
      osc.frequency.setValueAtTime(noteFreq, t);
      osc2.frequency.setValueAtTime(noteFreq * 1.002, t);
      
      // Vibrato on longer notes
      if (durSteps >= 3) {
        const vibStart = t + dur * 0.3;
        const lfo = ctx.createOscillator();
        const lfoG = ctx.createGain();
        lfo.type = 'sine';
        lfo.frequency.value = 5.5;
        lfoG.gain.value = noteFreq * 0.008;
        lfo.connect(lfoG).connect(osc.frequency);
        lfo.connect(lfoG).connect(osc2.frequency);
        lfo.start(vibStart); lfo.stop(t + dur);
      }
      
      f.type = 'lowpass';
      f.frequency.setValueAtTime(3000 + musicIntensity * 500, t);
      f.frequency.exponentialRampToValueAtTime(1500, t + dur * 0.8);
      f.Q.value = 1;
      
      const vol = 0.025 + musicIntensity * 0.003;
      g.gain.setValueAtTime(0, t);
      g.gain.linearRampToValueAtTime(vol, t + 0.008);
      if (durSteps >= 2) {
        g.gain.setValueAtTime(vol * 0.8, t + dur * 0.5);
      }
      g.gain.exponentialRampToValueAtTime(0.001, t + dur * 0.95);
      
      osc.connect(f);
      osc2.connect(f);
      f.connect(g).connect(musicGain!);
      if (reverbGain) g.connect(reverbGain);
      osc.start(t); osc.stop(t + dur + 0.01);
      osc2.start(t); osc2.stop(t + dur + 0.01);
    }
  }

  // ============ TRANSITION EFFECTS ============
  if (isFillMeasure) {
    // Riser sweep on build sections
    if (sectionFeel === 1 || sectionFeel === 3) {
      const riser = ctx.createOscillator();
      const rG = ctx.createGain();
      const rF = ctx.createBiquadFilter();
      riser.type = 'sawtooth';
      riser.frequency.setValueAtTime(200, now);
      riser.frequency.exponentialRampToValueAtTime(2000, now + measureDur);
      rF.type = 'bandpass';
      rF.frequency.setValueAtTime(400, now);
      rF.frequency.exponentialRampToValueAtTime(4000, now + measureDur);
      rF.Q.value = 3;
      rG.gain.setValueAtTime(0, now);
      rG.gain.linearRampToValueAtTime(0.04, now + measureDur * 0.8);
      rG.gain.exponentialRampToValueAtTime(0.001, now + measureDur);
      riser.connect(rF).connect(rG).connect(musicGain!);
      riser.start(now); riser.stop(now + measureDur + 0.01);
    }
    
    // Crash on drop transitions
    if (sectionFeel === 1) {
      const t = now + measureDur - 0.01;
      for (let j = 0; j < 3; j++) {
        const crash = ctx.createOscillator();
        const cg = ctx.createGain();
        crash.type = 'sawtooth';
        crash.frequency.setValueAtTime(5000 + Math.random() * 5000, t);
        crash.detune.setValueAtTime(Math.random() * 2400, t);
        cg.gain.setValueAtTime(0.03, t);
        cg.gain.exponentialRampToValueAtTime(0.001, t + 0.5);
        crash.connect(cg).connect(musicGain!);
        crash.start(t); crash.stop(t + 0.55);
      }
    }
  }

  // ============ AMBIENT TEXTURE (breakdown sections) ============
  if (sectionFeel === 3) {
    // Filtered noise wash
    const washOsc = ctx.createOscillator();
    const washG = ctx.createGain();
    const washF = ctx.createBiquadFilter();
    washOsc.type = 'sawtooth';
    washOsc.frequency.setValueAtTime(40 + Math.random() * 20, now);
    washOsc.detune.setValueAtTime(1200, now);
    washF.type = 'bandpass';
    washF.frequency.setValueAtTime(300, now);
    washF.frequency.linearRampToValueAtTime(800, now + measureDur * 0.5);
    washF.frequency.linearRampToValueAtTime(300, now + measureDur);
    washF.Q.value = 0.5;
    washG.gain.setValueAtTime(0.015, now);
    washG.gain.setValueAtTime(0.015, now + measureDur * 0.8);
    washG.gain.exponentialRampToValueAtTime(0.001, now + measureDur);
    washOsc.connect(washF).connect(washG).connect(musicGain!);
    if (reverbGain) washG.connect(reverbGain);
    washOsc.start(now); washOsc.stop(now + measureDur + 0.01);
  }

  currentChordIndex = (currentChordIndex + 1) % prog.length;
  measureCount++;
  
  const nextTime = (measureDur - 0.05) * 1000;
  const timer = window.setTimeout(scheduleNextMeasure, nextTime);
  musicTimers.push(timer);
}

export function startMusic() {
  if (musicPlaying) return;
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
