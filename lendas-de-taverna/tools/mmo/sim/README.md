# Simulação de equilíbrio (Hearthblade)
Rodar com o servidor estático na raiz do repositório (`python3 -m http.server 8760`).
- `sim.js <classe> <min> [nível] [zona] [perfil]` roda o jogo em tempo acelerado (Playwright) e imprime nível, mortes, vida média, **vida perdida por abate** e **tempo por abate**. Perfis de equipamento: `med` (drops normais), `good` (raro, +4) e `bis` (Épico+, +10, tier alto).
- `calib.sh` mede níveis 5 a 60 com o perfil de equipamento esperado em cada fase (médio no começo, quase perfeito no endgame).
- `knots.py '<medidas>' '<K atual>' [amortecimento]` calcula os novos multiplicadores de vida/ataque dos monstros por nível (tabela `BAL.K` do `index.html`).
- Alvo: ≈7 % de vida por abate no início → ≈37 % no endgame com equipamento quase perfeito; tempo por abate 5 s → 13,5 s.
