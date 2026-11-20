"""Mini-motor de música do Hearthblade: partitura em código -> instrumentos REAIS amostrados (GeneralUser GS, via tinysoundfont) -> reverb -> .ogg.
Preparar: git clone https://github.com/mrbumpy409/GeneralUser-GS /tmp/aud/dl/GeneralUser-GS ; python3 -m pip install --no-deps tinysoundfont
(o SF2 pode ser outro caminho com a variável SF2). Usado por abertura_mmo.py (título, criação, cutscene, sfx)."""
import os, random, subprocess, numpy as np
import tinysoundfont as T
SR = 44100
SF2 = os.environ.get('SF2', '/tmp/aud/dl/GeneralUser-GS/GeneralUser-GS.sf2')
_N = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
def n(s):
    i = 1; acc = 0
    while i < len(s) and s[i] in '#b': acc += 1 if s[i] == '#' else -1; i += 1
    return 12 * (int(s[i:]) + 1) + _N[s[0]] + acc
def triad(name, octv=3):
    """'Dm','Bb','F#m','A' -> [raiz, terça, quinta] no oitavo dado (raiz = nota mais grave)"""
    i = 1; acc = 0
    while i < len(name) and name[i] in '#b': acc += 1 if name[i] == '#' else -1; i += 1
    r = 12 * (octv + 1) + _N[name[0]] + acc
    minor = name[i:i + 1] == 'm'
    return [r, r + (3 if minor else 4), r + 7]
class Score:
    def __init__(s, bpm, seed=1):
        s.bpm = bpm; s.ev = []; s.chs = {}; s.rnd = random.Random(seed)
    def inst(s, ch, prog, bank=0, vol=100, pan=64, drums=False):
        s.chs[ch] = (prog, bank, vol, pan, drums)
    def note(s, ch, beat, dur, midi, vel=80, jit=0.0, vj=0):
        t = beat * 60 / s.bpm + (s.rnd.uniform(-jit, jit) if jit else 0); t = max(0.0, t)
        v = max(1, min(127, int(vel + (s.rnd.randint(-vj, vj) if vj else 0))))
        s.ev.append((t, 1, ch, midi, v)); s.ev.append((t + max(.02, dur) * 60 / s.bpm, 0, ch, midi, 0))
    def seq(s, ch, start, notes, vel=80, legato=1.0, **k):
        """notes = [('D4',2),('F4',1),(None,1)...] em tempos; devolve o tempo final"""
        b = start
        for nm, d in notes:
            if nm is not None:
                s.note(ch, b, d * legato, n(nm), vel + (5 if b % 4 == 0 else 0), jit=.008, vj=4, **k)
            b += d
        return b
    def render(s, beats, tail=4.0, gain=-3.0):
        syn = T.Synth(samplerate=SR, gain=gain)
        sf = syn.sfload(SF2)
        for ch, (prog, bank, vol, pan, dr) in s.chs.items():
            syn.program_select(ch, sf, bank, prog, dr)
            syn.control_change(ch, 7, vol); syn.control_change(ch, 10, pan)
        total = int((beats * 60 / s.bpm + tail) * SR)
        out = np.zeros((total, 2), np.float32); cur = 0
        for t, on, ch, midi, v in sorted(s.ev, key=lambda e: (e[0], e[1])):
            pos = min(total, int(t * SR))
            if pos > cur:
                out[cur:pos] = np.frombuffer(syn.generate(pos - cur), np.float32).reshape(-1, 2); cur = pos
            if on: syn.noteon(ch, midi, v)
            else: syn.noteoff(ch, midi)
        if cur < total: out[cur:] = np.frombuffer(syn.generate(total - cur), np.float32).reshape(-1, 2)
        return out
def reverb(x, secs=3.0, wet=.3, pre=.025, seed=5):
    rng = np.random.default_rng(seed); L = int(secs * SR)
    t = np.arange(L) / SR; env = np.exp(-t * (6.9 / secs))
    ir = np.stack([rng.standard_normal(L) * env for _ in range(2)], 1)
    k = np.ones(24) / 24                                  # escurece a cauda (filtro passa-baixa simples)
    ir = np.stack([np.convolve(ir[:, c], k, 'same') for c in range(2)], 1)
    ir = np.vstack([np.zeros((int(pre * SR), 2)), ir]); ir /= np.sqrt((ir ** 2).sum())
    N = 1
    while N < len(x) + len(ir): N *= 2
    y = np.stack([np.fft.irfft(np.fft.rfft(x[:, c], N) * np.fft.rfft(ir[:, c], N), N)[:len(x)] for c in range(2)], 1)
    return (x * (1 - wet) + y * wet * 2.2).astype(np.float32)
def loopify(x, loop_len):
    """costura a cauda no começo para o loop ficar contínuo"""
    tail = x[loop_len:]; x = x[:loop_len].copy(); m = min(len(tail), len(x)); x[:m] += tail[:m]; return x
def tone(x, lp=9000, hp=55):
    N = 1
    while N < len(x): N *= 2
    f = np.fft.rfftfreq(N, 1 / SR); m = np.ones_like(f)
    m[f > lp] = 1 / (1 + ((f[f > lp] - lp) / 3000) ** 2); m[f < hp] = (f[f < hp] / hp) ** 2
    return np.stack([np.fft.irfft(np.fft.rfft(x[:, c], N) * m, N)[:len(x)] for c in range(2)], 1).astype(np.float32)
def normalize(x, rms_db=-21.0, peak=.97):
    r = np.sqrt((x ** 2).mean()) + 1e-9; x = x * (10 ** (rms_db / 20) / r)
    return (np.tanh(x / peak) * peak).astype(np.float32)
def fade(x, a=.01, b=.02):
    x = x.copy(); na, nb = int(a * SR), int(b * SR)
    if na: x[:na] *= np.linspace(0, 1, na)[:, None]
    if nb: x[-nb:] *= np.linspace(1, 0, nb)[:, None]
    return x
def save(x, path, q=4):
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '-', '-c:a', 'libvorbis', '-q:a', str(q), path], stdin=subprocess.PIPE)
    p.communicate(np.clip(x, -1, 1).astype('<f4').tobytes()); return path
def report(x):
    r = np.sqrt((x ** 2).mean()); pk = np.abs(x).max()
    return 'rms %.1f dB, pico %.2f, %.1f s' % (20 * np.log10(r + 1e-9), pk, len(x) / SR)
