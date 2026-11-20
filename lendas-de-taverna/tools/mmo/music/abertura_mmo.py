"""Trilhas da abertura do Hearthblade: título, criação de personagem, cutscene (loop sombrio + amanhecer) e efeitos da cutscene.
Instrumentos reais (GeneralUser GS). Uso: python3 abertura_mmo.py [titulo|criacao|abertura|amanhecer|sfx|all]  -> out/*.ogg
Copiar para lendas-de-taverna/assets/audio/music (musicas) e assets/audio/sfx (cut_*.ogg)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib2 import *
OUT = os.environ.get('OUT', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')); os.makedirs(OUT, exist_ok=True)

def arp(sc, ch, b, tones, vel, pat=(0, 1, 2, 3, 2, 1, 2, 1), step=.5, dur=.9, octs=12):
    t = [tones[0], tones[1], tones[2], tones[0] + octs]
    for k, i in enumerate(pat): sc.note(ch, b + k * step, dur, t[i], vel - (6 if k % 2 else 0) + (4 if k == 0 else 0), jit=.006, vj=4)
def pad(sc, ch, b, tones, d, vel, shift=0):
    for t in tones: sc.note(ch, b, d, t + shift, vel, jit=.03, vj=3)

# ============================ TÍTULO — Ré menor, 76 bpm, 32 compassos (loop) ============================
def titulo():
    sc = Score(76, seed=7)
    for c, p, v, pn in [(0, 60, 100, 60), (1, 48, 88, 64), (2, 52, 78, 64), (3, 46, 96, 50), (4, 47, 104, 64), (5, 42, 100, 58), (6, 73, 92, 78), (7, 14, 86, 64), (8, 40, 96, 70), (10, 43, 90, 64), (11, 61, 92, 64)]:
        sc.inst(c, p, vol=v, pan=pn)
    CH = ['Dm', 'Dm', 'Bb', 'A',  'Dm', 'Bb', 'F', 'C', 'Dm', 'Bb', 'Gm', 'A',  'Gm', 'Dm', 'Bb', 'F', 'Gm', 'Dm', 'A', 'A',
          'Bb', 'F', 'Gm', 'Dm', 'Bb', 'C', 'A', 'A',  'Dm', 'Bb', 'Gm', 'A']
    LV = lambda i: 44 if i < 4 else 58 if i < 12 else 70 if i < 20 else 88 if i < 28 else 48          # dinâmica por seção
    for i, c in enumerate(CH):
        b = i * 4; tn = triad(c, 3); lv = LV(i); r = tn[0]
        if c == 'A': tn = [tn[0], tn[0] + 4, tn[0] + 7]
        pad(sc, 1, b, tn, 4.0, int(lv * .8))                                           # cordas
        sc.note(5, b, 4.0, r - 12 if r - 12 >= 36 else r, int(lv * .95), jit=.01)      # violoncelo (raiz)
        if i >= 4: sc.note(10, b, 4.0, r - 24 if r - 24 >= 28 else r - 12, int(lv * .7))  # contrabaixo
        if i < 4 or i >= 12: pad(sc, 2, b, [t + 12 for t in tn], 4.0, int(lv * .55))   # coro
        if i < 2 or 4 <= i < 28 or i >= 28: arp(sc, 3, b, [t + 12 for t in tn], int(lv * .85 + 10), dur=.95)  # harpa
        if 4 <= i < 12: sc.note(4, b, .9, r - 12 if r - 12 >= 36 else r, 90) if i % 2 == 0 else None          # tímpano espaçado
        if 12 <= i < 20:
            sc.note(4, b, .8, r - 12 if r - 12 >= 36 else r, 92); sc.note(4, b + 2, .8, r - 12 if r - 12 >= 36 else r, 80)
        if 20 <= i < 28:
            for bt, vv in [(0, 104), (1.5, 78), (2, 96), (3, 80), (3.5, 88)]: sc.note(4, b + bt, .5, r - 12 if r - 12 >= 36 else r, vv)
            pad(sc, 11, b, [t + 12 for t in tn], 4.0, int(lv * .62))                  # metais cheios no clímax
        if i in (0, 12, 20, 28): sc.note(7, b, 6, n('D5') if c not in ('Bb', 'Gm') else r + 24, 70)   # sino tubular
    # --- melodia A (trompa) ---
    A = [('D4', 2), ('F4', 1), ('A4', 1), ('Bb4', 2), ('A4', 1), ('G4', 1), ('A4', 2), ('F4', 1), ('C5', 1), ('E5', 2), ('D5', 1), ('C5', 1),
         ('D5', 2), ('A4', 1), ('F4', 1), ('G4', 1), ('Bb4', 1), ('D5', 2), ('Bb4', 2), ('A4', 1), ('G4', 1), ('C#5', 2), ('E5', 1), ('A4', 1)]
    sc.seq(0, 16, A, 72, .97)
    sc.seq(6, 32, [('D5', 2), ('F5', 1), ('A5', 1)], 0) if False else None
    # --- melodia B (violinos + flauta uma oitava acima) ---
    B = [('G4', 1), ('Bb4', 1), ('D5', 2), ('F5', 2), ('E5', 1), ('D5', 1), ('Bb4', 1), ('D5', 1), ('F5', 2), ('A4', 1), ('C5', 1), ('F5', 2),
         ('G5', 2), ('F5', 1), ('D5', 1), ('E5', 1), ('F5', 1), ('A5', 2), ('G5', 1), ('E5', 1), ('C#5', 1), ('E5', 1), ('A4', 4)]
    sc.seq(8, 48, B, 84, .97)
    sc.seq(6, 48, [(nm, d) for nm, d in B], 60, .95)
    # --- melodia C (tema em triunfo: trompa + flauta + violinos) ---
    C = [('D5', 1), ('F5', 1), ('Bb5', 2), ('A5', 2), ('F5', 1), ('C5', 1), ('G5', 2), ('Bb5', 1), ('A5', 1), ('F5', 3), ('D5', 1),
         ('D5', 1), ('F5', 1), ('Bb5', 2), ('C6', 2), ('B5', 1), ('C6', 1), ('A5', 1), ('G5', 1), ('E5', 1), ('C#5', 1), ('E5', 4)]
    sc.seq(0, 80, [(nm, d) for nm, d in C], 96, .98); sc.seq(6, 80, C, 82, .96); sc.seq(8, 80, C, 78, .97)
    # --- saída suave (flauta) para o loop ---
    sc.seq(6, 112, [('A4', 4), ('G4', 2), ('F4', 2), ('D4', 4), ('C#5', 4)], 54, .98)
    sc.seq(0, 112, [('D4', 4), ('F4', 2), ('D4', 2), ('Bb3', 4), ('E4', 4)], 52, .98)
    x = sc.render(128, tail=5)
    x = reverb(x, 3.2, .3); x = loopify(x, int(128 * 60 / 76 * SR)); x = tone(x, 12000, 50)
    return normalize(x, -20.5)

# ============================ CRIAÇÃO — Sol maior, 72 bpm, 24 compassos (loop) ============================
def criacao():
    sc = Score(72, seed=11)
    for c, p, v, pn in [(0, 24, 100, 56), (1, 73, 98, 74), (2, 46, 94, 50), (3, 48, 70, 64), (4, 42, 96, 60), (5, 9, 80, 70), (6, 68, 92, 70), (10, 52, 62, 64)]:
        sc.inst(c, p, vol=v, pan=pn)
    CH = ['G', 'D', 'Em', 'C', 'G', 'D', 'C', 'D',   'Em', 'C', 'G', 'D', 'Em', 'C', 'D', 'D',   'G', 'D', 'Em', 'C', 'Am', 'D', 'G', 'G']
    for i, c in enumerate(CH):
        b = i * 4; tn = triad(c, 3); r = tn[0]; lv = 58 if i < 8 else 64 if i < 16 else 70
        arp(sc, 0, b, tn, lv + 10, pat=(0, 2, 1, 3, 1, 2, 1, 2), step=.5, dur=1.2)                      # violão de nylon
        pad(sc, 3, b, [t + 12 for t in tn], 4.0, int(lv * .5))                                              # cordas suaves
        sc.note(4, b, 3.9, r - 12 if r - 12 >= 36 else r, int(lv * .9))                                     # violoncelo
        if i % 2 == 0: arp(sc, 2, b + 2, [t + 24 for t in tn], lv - 4, pat=(0, 1, 2, 3), step=.5, dur=1.2)   # harpa cintilante
        if i >= 16: pad(sc, 10, b, [t + 12 for t in tn], 4.0, int(lv * .5))
        if i in (7, 15, 23): sc.note(5, b + 3, 1.0, tn[2] + 24, 66)                                         # glockenspiel
    FA = [('B4', 2), ('D5', 1), ('B4', 1), ('A4', 2), ('F#4', 1), ('A4', 1), ('G4', 2), ('B4', 1), ('E5', 1), ('E5', 2), ('D5', 1), ('C5', 1),
          ('B4', 1), ('D5', 1), ('G5', 2), ('F#5', 2), ('E5', 1), ('D5', 1), ('E5', 2), ('D5', 1), ('C5', 1), ('A4', 3), ('F#4', 1)]
    sc.seq(1, 0, FA, 78, .96)
    FB = [('B4', 1), ('E5', 1), ('G5', 2), ('G5', 2), ('E5', 1), ('C5', 1), ('D5', 2), ('B4', 1), ('D5', 1), ('A4', 1), ('D5', 1), ('F#5', 2),
          ('G5', 2), ('F#5', 1), ('E5', 1), ('E5', 2), ('G5', 1), ('E5', 1), ('D5', 2), ('F#5', 1), ('A5', 1), ('F#5', 4)]
    sc.seq(6, 32, FB, 80, .96)
    FC = [('B4', 2), ('D5', 1), ('B4', 1), ('A4', 2), ('F#4', 1), ('A4', 1), ('G4', 2), ('B4', 1), ('E5', 1), ('E5', 2), ('D5', 1), ('C5', 1),
          ('E5', 2), ('C5', 1), ('A4', 1), ('F#5', 2), ('A4', 1), ('D5', 1), ('B4', 2), ('D5', 2), ('G4', 4)]
    sc.seq(1, 64, FC, 82, .96); sc.seq(5, 64, [(a, d) for a, d in FC], 58, .9)
    x = sc.render(96, tail=4)
    x = reverb(x, 2.6, .26); x = loopify(x, int(96 * 60 / 72 * SR)); x = tone(x, 11000, 60)
    return normalize(x, -21.5)

# ============================ CUTSCENE — Ré menor, 52 bpm, 24 compassos (loop sombrio) ============================
def abertura():
    sc = Score(52, seed=3)
    for c, p, v, pn in [(0, 19, 92, 64), (1, 53, 86, 64), (2, 44, 80, 64), (3, 42, 104, 60), (4, 14, 90, 64), (5, 46, 92, 52), (6, 47, 100, 64), (7, 69, 98, 72), (8, 8, 90, 72), (10, 48, 78, 64)]:
        sc.inst(c, p, vol=v, pan=pn)
    CH = ['Dm', 'Dm', 'Bb', 'A',  'Dm', 'Gm', 'Bb', 'A',  'Dm', 'Gm', 'Bb', 'A',  'Dm', 'C', 'Bb', 'A',  'Dm', 'Gm', 'Bb', 'A',  'Gm', 'Dm', 'Bb', 'A']
    for i, c in enumerate(CH):
        b = i * 4; tn = triad(c, 3); r = tn[0]
        if c == 'A': tn = [tn[0], tn[0] + 4, tn[0] + 7]
        lv = 38 if i < 4 else 48 if i < 20 else 36
        pad(sc, 1, b, [t + 12 for t in tn], 4.0, int(lv * .8))                           # coro (oohs)
        pad(sc, 2, b, tn, 4.0, int(lv * .9))                                              # cordas em tremolo
        if i % 2 == 0: sc.note(0, b, 7.9, r - 12 if r - 12 >= 36 else r, int(lv + 12))    # órgão de igreja (pedal)
        if i % 2 == 0: sc.note(6, b, .9, r - 12 if r - 12 >= 36 else r, 64); sc.note(6, b + 1.1, .8, r - 12 if r - 12 >= 36 else r, 48)   # coração
        if i % 4 == 0: sc.note(4, b, 6, r + 24 if r + 24 < 84 else r + 12, 52)           # sino tubular
        if i % 4 == 2: arp(sc, 5, b, [t + 12 for t in tn], 44, pat=(0, 1, 2, 3), step=1.0, dur=2.0)  # harpa esparsa
        if i >= 12 and i % 4 == 3: sc.note(8, b + 2, 1.5, tn[2] + 24, 42); sc.note(8, b + 3.2, 1.0, tn[0] + 24, 36)   # celesta
    sc.seq(3, 16, [('D3', 3), ('F3', 1), ('G3', 2), ('F3', 1), ('E3', 1), ('Bb3', 3), ('A3', 1), ('C#4', 4)], 80, 1.0)                 # violoncelo solo
    sc.seq(7, 32, [('A4', 2), ('G4', 1), ('F4', 1), ('Bb4', 2), ('A4', 2), ('D5', 3), ('C5', 1), ('C#5', 2), ('E5', 2)], 72, 1.0)     # corne inglês
    sc.seq(3, 48, [('A3', 2), ('F3', 1), ('D3', 1), ('E3', 2), ('G3', 2), ('D3', 2), ('F3', 2), ('E3', 4)], 82, 1.0)
    sc.seq(7, 64, [('F4', 2), ('E4', 1), ('D4', 1), ('G4', 2), ('F4', 2), ('Bb4', 3), ('A4', 1), ('C#5', 2), ('A4', 2)], 70, 1.0)
    sc.seq(3, 80, [('G3', 3), ('Bb3', 1), ('A3', 2), ('F3', 2), ('D3', 8)], 74, 1.0)
    x = sc.render(96, tail=6)
    x = reverb(x, 4.4, .38); x = loopify(x, int(96 * 60 / 52 * SR)); x = tone(x, 8000, 45)
    return normalize(x, -22)

# ============================ AMANHECER — Ré maior, 66 bpm, ~22 s (toca uma vez, quando a câmera sobrevoa Brumavale) ============================
def amanhecer():
    sc = Score(66, seed=5)
    for c, p, v, pn in [(0, 60, 104, 58), (1, 48, 92, 64), (2, 52, 84, 64), (3, 46, 98, 52), (4, 47, 104, 64), (5, 42, 100, 60), (6, 73, 92, 78), (7, 14, 90, 64), (8, 61, 96, 64), (10, 43, 90, 64)]:
        sc.inst(c, p, vol=v, pan=pn)
    CH = ['Dm', 'A', 'Bm', 'G', 'D', 'D']
    for i, c in enumerate(CH):
        b = i * 4; tn = triad(c, 3); r = tn[0]; lv = 40 + i * 9
        if c == 'A': tn = [tn[0], tn[0] + 4, tn[0] + 7]
        if c == 'D': tn = [tn[0], tn[0] + 4, tn[0] + 7]
        pad(sc, 1, b, [t + 12 for t in tn], 4.0, min(100, int(lv * .9)))
        sc.note(5, b, 4.0, r - 12 if r - 12 >= 36 else r, min(100, lv + 14)); sc.note(10, b, 4.0, r - 24 if r - 24 >= 28 else r - 12, int(lv * .8))
        if i >= 2: pad(sc, 2, b, [t + 12 for t in tn], 4.0, int(lv * .8))
        arp(sc, 3, b, [t + 12 for t in tn], min(100, lv + 8), dur=1.0)
        if i >= 3: sc.note(4, b, .8, r - 12 if r - 12 >= 36 else r, 90); sc.note(4, b + 2, .7, r - 12 if r - 12 >= 36 else r, 76)
        if i >= 3: pad(sc, 8, b, [t + 12 for t in tn], 4.0, int(lv * .6))
    sc.note(7, 20, 7, n('D5'), 72)
    sc.seq(0, 0, [('A4', 2), ('D5', 2), ('C#5', 2), ('E5', 2), ('D5', 2), ('F#5', 2), ('G5', 2), ('F#5', 1), ('E5', 1), ('F#5', 3), ('D5', 1), ('D5', 4)], 90, .98)
    sc.seq(6, 8, [('D5', 2), ('F#5', 2), ('G5', 2), ('F#5', 1), ('E5', 1), ('A5', 3), ('F#5', 1), ('F#5', 4)], 80, .96)
    x = sc.render(24, tail=7)
    x = reverb(x, 4.0, .34); x = tone(x, 12000, 50)
    return fade(normalize(x, -20.5), .02, 2.2)

# ============================ EFEITOS DA CUTSCENE ============================
def sfx_marca():            # a marca brilha: celesta/glockenspiel subindo + coro + harpa
    sc = Score(96, seed=2)
    for c, p, v, pn in [(0, 8, 100, 60), (1, 9, 86, 68), (2, 52, 78, 64), (3, 46, 96, 52), (4, 14, 80, 64)]: sc.inst(c, p, vol=v, pan=pn)
    for k, m in enumerate(['D5', 'F#5', 'A5', 'D6', 'F#6', 'A6']): sc.note(0, k * .22, 2.0, n(m), 78 - k * 3); sc.note(1, k * .22 + .03, 1.6, n(m) - 12, 62)
    for t in triad('D', 4): sc.note(2, 0, 3.5, t, 70)
    for k, m in enumerate(['D4', 'A4', 'D5', 'F#5']): sc.note(3, 1.2 + k * .25, 2.0, n(m), 70)
    sc.note(4, 2.4, 4, n('D6'), 60)
    x = reverb(sc.render(4, tail=2.5), 3.0, .4); return fade(normalize(x, -19), .004, 1.6)
def sfx_queda():            # o Escolhido caiu: timpano + sino grave + coro menor
    sc = Score(60, seed=4)
    for c, p, v, pn in [(0, 47, 110, 64), (1, 14, 90, 64), (2, 52, 80, 64), (3, 43, 100, 64)]: sc.inst(c, p, vol=v, pan=pn)
    sc.note(0, 0, 2, n('D2'), 120); sc.note(0, .05, 2, n('A1'), 110); sc.note(1, 0, 6, n('D3'), 90); sc.note(1, .02, 6, n('Bb3'), 70)
    for t in triad('Dm', 3): sc.note(2, .3, 4.5, t + 12, 66)
    sc.note(3, 0, 5, n('D1'), 100)
    x = reverb(sc.render(4, tail=3), 4.0, .45); return fade(normalize(x, -18.5), .003, 2.0)
def sfx_sino():             # o sino da torre de Brumavale: três badaladas
    sc = Score(40, seed=6)
    sc.inst(0, 14, vol=104, pan=64); sc.inst(1, 14, vol=70, pan=60)
    for k in range(3): sc.note(0, k * 2.8, 6, n('D4') if k != 1 else n('A3'), 92 - k * 6); sc.note(1, k * 2.8 + .02, 6, n('D5') if k != 1 else n('A4'), 52)
    x = reverb(sc.render(7, tail=3.5), 3.4, .4); return fade(normalize(x, -21), .005, 2.5)

if __name__ == '__main__':
    want = sys.argv[1:] or ['all']; A = 'all' in want
    jobs = [('titulo', titulo, 'titulo_mmo.ogg', 4), ('criacao', criacao, 'criacao.ogg', 4), ('abertura', abertura, 'abertura.ogg', 4), ('amanhecer', amanhecer, 'amanhecer.ogg', 4),
            ('sfx', sfx_marca, 'cut_marca.ogg', 5), ('sfx', sfx_queda, 'cut_queda.ogg', 5), ('sfx', sfx_sino, 'cut_sino.ogg', 5)]
    for k, fn, f, q in jobs:
        if A or k in want:
            x = fn(); print(f, report(x)); save(x, os.path.join(OUT, f), q)
