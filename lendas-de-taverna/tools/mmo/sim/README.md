# Simulação de equilíbrio (modo MMO)
- `sim.js <classe> <min> [nível] [zona]` roda o jogo no navegador (Playwright) em tempo acelerado e imprime nível, mortes, vida média, **vida perdida por abate** e **tempo por abate**.
- `calib.sh` mede 8 níveis (1 a 60); `calib_fit.py '<medidas>' '<BAL atual>'` calcula a correção e ajusta as curvas `BAL` do `index.html`.
- Alvo (curva de dificuldade): ≈7 % de vida por abate no início → ≈37 % no endgame; tempo por abate 5 s → 13,5 s.
