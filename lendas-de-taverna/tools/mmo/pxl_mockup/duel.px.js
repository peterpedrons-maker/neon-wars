// Mockup: Guerreiro (jogador) e Grunk (chefe da floresta) em pixel art, com animação própria por habilidade.
pal({ k: "#1a1220",
  a: "#3a4250", s: "#5a6676", S: "#9aa6b8", z: "#e0e8f4",                 // aço
  R: "#c83c3c", r: "#7a2230", q: "#f06060",                               // vermelho (pluma, tabardo)
  v: "#e0a878", V: "#a8704c",                                             // pele humana
  b: "#3e2416", B: "#6a4026", N: "#9a6a3c",                               // couro
  j: "#a8902c", J: "#e8d070", h: "#fff2b0",                               // ouro
  i: "#244a24", I: "#3e7a30", l: "#6cb042", L: "#a4e070",                 // goblin
  w: "#d8c890", W: "#948058", y: "#ffe060", m: "#a02020",
  c: "#4a2a1c", C: "#7a4a30", T: "#a8a8b0", n: "#f0f0f8", o: "#ff9a3c", g: "#7a5a3a" })
ramps("kaSz", "kiIlL", "kbBN", "kcCg")
const R = Math.PI / 180, R0 = Math.round, lerp = (a, b, u) => a + (b - a) * u
const OX = 30, GY = 64, W = 96, H = 72
function limb(c, a, b, w, col) { c.line(R0(a[0]), R0(a[1]), R0(b[0]), R0(b[1]), col, Math.max(1, Math.round(w))) }
const fk = (x, y, L, a, K) => [x + L * K * Math.sin(a * R), y + L * K * Math.cos(a * R)]
function keyed(KEYS, t, hard) {
  for (let i = 0; i < KEYS.length - 1; i++) {
    const [t0, a] = KEYS[i], [t1, b] = KEYS[i + 1]
    if (t >= t0 && t <= t1) { let u = (t - t0) / (t1 - t0); u = (hard && hard.includes(i)) ? u * u : u * u * (3 - 2 * u); const r = {}; for (const k in a) r[k] = typeof a[k] === "number" ? lerp(a[k], b[k], u) : (u < .5 ? a[k] : b[k]); return r }
  }
  return { ...KEYS[KEYS.length - 1][1] }
}
// ---------------- GUERREIRO ----------------
sprite("_whead", `
  ..rr.......
  .rRRr.sSSs.
  rRRq.sSSSSs
  .rR.sSSSSSSs
  ..rsSSSSSSzs
  ...sSSkkkkSs
  ...sSSSSSSSs
  ...sSsSSSSs.
  ....vvVsSs..
  .....vVVss..`)
sprite("_wshield", `
  ..jjjj..
  .jJJJJj.
  jJRRRRJj
  jJRhhRJj
  jJRhhRJj
  jJRRRRJj
  .jJJJJj.
  ..jjjj..`)
const KW = 0.7
function warrior(c, p) {
  const lean = p.lean || 0, dx = p.dx || 0, dy = p.dy || 0
  const hx = OX + 20 + dx
  const feet = Math.max(...[[p.hF, p.kF], [p.hN, p.kN]].map(([hd, kn]) => { const k = fk(0, 0, 12, hd, KW), a = fk(k[0], k[1], 12, hd - kn, KW); return a[1] }))
  const hy = GY - feet - 1 + (p.bob || 0) * KW + dy
  if (!dy) c.ellipse(hx + 2, GY + 1, 11, 1, "g"); else c.ellipse(hx + 2, GY + 1, 7, 1, "g")
  const leg = (hip, hd, kn, near) => {
    const k = fk(hip[0], hip[1], 12, hd, KW), a = fk(k[0], k[1], 12, hd - kn, KW)
    limb(c, hip, k, 5 * KW + 1, near ? "S" : "s"); limb(c, k, a, 4 * KW + 1, near ? "s" : "a")
    limb(c, [hip[0] - 1, hip[1]], [k[0] - 1, k[1]], 1, near ? "z" : "S")
    c.ellipse(k[0], k[1], 2, 2, near ? "S" : "s")
    const fo = [a[0] + 3.4, a[1] + .6]; limb(c, a, fo, 3, "b"); c.px(R0(fo[0]) + 1, R0(fo[1]), "B")
  }
  leg([hx, hy], p.hF, p.kF, false)
  const shF = [hx + 4 + lean * KW * .4, hy - 14]
  // escudo no braço longe (atrás do corpo, ou na frente se shieldFront)
  const eF = fk(shF[0], shF[1], 8, -p.aF, KW), hF = fk(eF[0], eF[1], 8, -p.aF + 20, KW)
  limb(c, shF, eF, 3, "a"); limb(c, eF, hF, 3, "a")
  if (!p.shieldFront) c.stamp("_wshield", R0(hF[0]) - 4, R0(hF[1]) - 4)
  const bx = hx + 1 + lean * KW * .4, by = hy - 9
  // torso: couraça
  c.ellipse(bx, by, 7, 9, "s"); c.ellipse(bx - 1, by - 1, 5.4, 7.4, "S"); c.ellipse(bx - 2, by - 3, 2.2, 3, "z")
  c.ellipse(bx + 5, by, 1.6, 7, "a")
  c.rect(R0(bx) - 6, R0(by) + 6, 12, 3, "b"); c.hline(R0(bx) - 6, R0(by) + 6, 12, "B"); c.rect(R0(bx) - 1, R0(by) + 6, 3, 3, "j")
  c.poly([bx - 5, by + 9, bx + 5, by + 9, bx + 4, by + 15, bx, by + 13, bx - 4, by + 15], "R"); c.poly([bx - 5, by + 9, bx, by + 9, bx - 1, by + 13, bx - 4, by + 14], "q")
  // cabeça (elmo com pluma)
  c.stamp("_whead", R0(bx) - 3, R0(by) - 20 + R0(p.hb || 0))
  leg([hx + 1, hy], p.hN, p.kN, true)
  // ombreira e braço da espada
  const sh = [hx + 2 + lean * KW * .4, hy - 14], e = fk(sh[0], sh[1], 8, -p.aN, KW), hd = fk(e[0], e[1], 8, -p.aN + (p.bend || 22), KW)
  limb(c, sh, e, 4, "S"); limb(c, e, hd, 3.4, "s"); c.ellipse(sh[0], sh[1] - 1, 3.4, 3, "S"); c.px(R0(sh[0]) - 1, R0(sh[1]) - 2, "z")
  const sa = p.sword, s0 = fk(hd[0], hd[1], -3, sa, KW), s1 = fk(hd[0], hd[1], 25, sa, KW)
  limb(c, s0, fk(hd[0], hd[1], 1, sa, KW), 2, "b"); limb(c, fk(hd[0], hd[1], 1, sa, KW), s1, 2, "T"); limb(c, fk(hd[0] - .5, hd[1] - .5, 1, sa, KW), [s1[0] - .5, s1[1] - .5], 1, "n")
  const g = fk(hd[0], hd[1], 2, sa, KW), pr = [Math.cos(sa * R) * 3, -Math.sin(sa * R) * 3]; limb(c, [g[0] - pr[0], g[1] - pr[1]], [g[0] + pr[0], g[1] + pr[1]], 1, "J")
  c.ellipse(hd[0], hd[1], 1.8, 1.6, "v")
  if (p.shieldFront) c.stamp("_wshield", R0(hd[0]) + 2, R0(hd[1]) - 6)
  const f = p.fx
  if (f) {
    const tx = R0(s1[0]), ty = R0(s1[1])
    if (f.k === "power") { for (let i = 0; i < 7; i++) { const an = (-90 + i * 30) * R; c.line(tx, ty, R0(tx + Math.cos(an) * (5 + 9 * f.a)), R0(ty + Math.sin(an) * (4 + 7 * f.a)), i % 2 ? "n" : "h", 1) } c.ellipse(tx, GY, 5 + 12 * f.a, 1 + 2 * f.a, "n", true) }
    if (f.k === "spin") { const cx = R0(bx), cy = R0(by); for (let i = 0; i < 3; i++) c.ellipse(cx, cy, 26 - i * 3, 12 - i * 2, i ? "S" : "n", true); }
    if (f.k === "shake") { c.ellipse(R0(hx) + 24, GY, 8 + 28 * f.a, 1 + 4 * f.a, "n", true); c.ellipse(R0(hx) + 24, GY, 4 + 20 * f.a, 1 + 3 * f.a, "o", true); for (let i = 0; i < 6; i++) c.px(R0(hx) + 14 + i * 5, GY - R0(3 * Math.sin(i + f.a * 6)) - 1, "g") }
    if (f.k === "roar") { c.ellipse(R0(bx), R0(by), 10 + 18 * f.a, 14 + 16 * f.a, "o", true); c.ellipse(R0(bx), R0(by), 6 + 12 * f.a, 9 + 11 * f.a, "h", true) }
  }
}
const WREST = { hN: 12, kN: 14, hF: -10, kF: 12, aN: 6, aF: 8, sword: 150, bend: 20, lean: 1, bob: 0, dx: 0, dy: 0 }
const wwalk = (t) => { const ph = t * Math.PI * 2, h = 28 * Math.sin(ph); return { ...WREST, hN: h, hF: -h, kN: 8 + 30 * Math.max(0, Math.sin(ph + Math.PI / 2)), kF: 8 + 30 * Math.max(0, -Math.sin(ph + Math.PI / 2)), aN: 8 + h * .1, aF: -h * .6, bob: -Math.abs(Math.cos(ph)) * 1.4, sword: 140 + h * .2 } }
const widle = (t) => { const b = Math.sin(t * Math.PI * 2); return { ...WREST, bob: -b * .7, hb: b * .5 } }
const POWER = [[0, WREST], [.3, { ...WREST, hN: 8, kN: 26, hF: -18, kF: 22, aN: -150, aF: 30, sword: 190, bend: 14, lean: -4, bob: 2 }], [.46, { ...WREST, hN: 8, kN: 14, hF: -22, kF: 10, aN: -165, aF: 40, sword: 200, bend: 8, lean: -6, bob: -1 }],
  [.6, { ...WREST, hN: 30, kN: 40, hF: -32, kF: 10, aN: -55, aF: 40, sword: 55, bend: 14, lean: 6, bob: 3, dx: 3 }], [.78, { ...WREST, hN: 30, kN: 40, hF: -32, kF: 10, aN: -60, aF: 44, sword: 48, bend: 14, lean: 7, bob: 3.5, dx: 3 }], [1, WREST]]
const wpower = (t) => { const p = keyed(POWER, t, [2]); if (t > .6 && t < .86) p.fx = { k: "power", a: (t - .6) / .26 }; return p }
const wslash = (t) => { const KEYS = [[0, WREST], [.3, { ...WREST, hN: 14, kN: 20, aN: 70, sword: 250, bend: 10, lean: -3, bob: 1 }], [.55, { ...WREST, hN: 26, kN: 30, hF: -26, aN: -75, sword: 95, bend: 8, lean: 5, bob: 2, dx: 2 }], [1, WREST]]; return keyed(KEYS, t) }
const wspin = (t) => { const a = t * 360 * 1.0; const p = { ...WREST, aN: -80, bend: 0, sword: 90 + a, hN: 6, kN: 22, hF: -10, kF: 22, lean: 0, bob: -Math.abs(Math.sin(t * Math.PI * 2)) * 2, dx: 0, aF: -80 }; if (t > .12 && t < .9) p.fx = { k: "spin" }; return p }
const wshake = (t) => { const KEYS = [[0, WREST], [.3, { ...WREST, hN: 6, kN: 22, hF: -14, kF: 22, aN: -150, sword: 190, bend: 10, lean: -4, bob: 0, dy: -5 }], [.5, { ...WREST, hN: 6, kN: 22, hF: -14, kF: 22, aN: -150, sword: 190, bend: 10, lean: -4, bob: 0, dy: -9 }], [.62, { ...WREST, hN: 20, kN: 40, hF: -20, kF: 30, aN: -30, sword: 20, bend: 16, lean: 8, bob: 6, dx: 2 }], [.8, { ...WREST, hN: 20, kN: 40, hF: -20, kF: 30, aN: -30, sword: 20, bend: 16, lean: 8, bob: 6, dx: 2 }], [1, WREST]]; const p = keyed(KEYS, t, [2]); if (t > .62 && t < .95) p.fx = { k: "shake", a: (t - .62) / .33 }; return p }
const wroar = (t) => { const KEYS = [[0, WREST], [.35, { ...WREST, aN: -150, sword: 180, bend: 0, lean: -5, hb: -1, bob: 1 }], [.7, { ...WREST, aN: -150, sword: 180, bend: 0, lean: -6, hb: -1, bob: 1 }], [1, WREST]]; const p = keyed(KEYS, t); if (t > .3 && t < .95) p.fx = { k: "roar", a: Math.min(1, (t - .3) / .5) }; return p }
const whurt = (t) => ({ ...WREST, lean: -6 * Math.sin(t * Math.PI), dx: -3 * Math.sin(t * Math.PI), hN: 16, kN: 20, aN: 20 })
const wdodge = (t) => ({ ...WREST, hN: 30, kN: 70, hF: 0, kF: 80, aN: 20, aF: 0, sword: 120, lean: 8, dy: -Math.sin(t * Math.PI) * 16 })
const WA = (n, f, fr, fps) => anim(n, { w: W, h: H, frames: fr, fps: fps || 14, outline: "k" }, (c) => warrior(c, f(c.phase)))
WA("w_walk", wwalk, 12, 12); WA("w_idle", widle, 8, 6); WA("w_slash", wslash, 12); WA("w_power", wpower, 18); WA("w_spin", wspin, 16); WA("w_shake", wshake, 18); WA("w_roar", wroar, 16); WA("w_hurt", whurt, 6); WA("w_dodge", wdodge, 10)

// ---------------- GRUNK ----------------
sprite("_ghead", `
  ....iiI.........
  ..iiIllIii......
  .iIlLllllIIi....
  iIlIlllLlllIIi..
  iIlllllllyyllIi.
  .iIlllllyyymlIIi
  ..iIlllllllllllIii
  ..iIIllllllllLllIIi
  ...iIllllllllLlllIi
  ...iIIlllllwllwlIi.
  ....iIIllllwWlwWi..
  .....iiIIIIllllii..
  ......iiiIIIIIii...`)
sprite("_gear", `
  ..iI.
  .iIlI
  iIlLI
  iIllI
  .iIlI
  ..iIi`)
const KG = 0.8
function grunk(c, p) {
  const lean = p.lean || 0, dx = p.dx || 0, dy = p.dy || 0
  const hx = OX + 22 + dx
  const feet = Math.max(...[[p.hF, p.kF], [p.hN, p.kN]].map(([hd, kn]) => { const k = fk(0, 0, 9, hd, KG), a = fk(k[0], k[1], 9, hd - kn, KG); return a[1] }))
  const hy = GY - feet - 1 + (p.bob || 0) * KG + dy
  c.ellipse(hx + 4, GY + 1, 15, 1.4, "g")
  const leg = (hip, hd, kn, near) => { const k = fk(hip[0], hip[1], 9, hd, KG), a = fk(k[0], k[1], 9, hd - kn, KG); limb(c, hip, k, 7 * KG, near ? "l" : "I"); limb(c, k, a, 6 * KG, near ? "l" : "I"); limb(c, [hip[0] - 1, hip[1]], [k[0] - 1, k[1]], 2, near ? "L" : "l"); const fo = [a[0] + 4, a[1] + 1]; limb(c, a, fo, 4, near ? "I" : "i"); c.px(R0(fo[0]) + 2, R0(fo[1]), "w") }
  leg([hx - 1, hy], p.hF, p.kF, false)
  const shF = [hx + 6 + lean * KG * .4, hy - 11], eF = fk(shF[0], shF[1], 9, -p.aF, KG), hF = fk(eF[0], eF[1], 9, -p.aF + 20, KG)
  limb(c, shF, eF, 4, "I"); limb(c, eF, hF, 3.6, "I"); c.ellipse(hF[0], hF[1], 2.2, 2, "I")
  const bx = hx + 2 + lean * KG * .4, by = hy - 8
  c.ellipse(bx, by, 11, 10, "I"); c.ellipse(bx - 1, by - 1, 9, 8.4, "l"); c.ellipse(bx - 3, by - 3, 3.4, 3, "L")
  c.ellipse(bx + 1, by + 3, 7, 6.4, "L"); c.ellipse(bx - 1, by + 2, 4, 4, "L")
  // armadura de couro com tachas e cinto de ossos
  c.poly([bx - 10, by - 6, bx + 2, by - 11, bx + 9, by - 5, bx + 4, by + 1, bx - 4, by + 1, bx - 9, by - 1], "B"); c.poly([bx - 10, by - 6, bx + 2, by - 11, bx + 3, by - 8, bx - 6, by - 1, bx - 9, by - 1], "N")
  for (const [px, py] of [[-6, -4], [-1, -7], [4, -5], [-3, -2]]) c.px(R0(bx + px), R0(by + py), "h")
  c.rect(R0(bx) - 10, R0(by) + 4, 20, 3, "b"); c.hline(R0(bx) - 10, R0(by) + 4, 20, "B"); for (let i = 0; i < 5; i++) c.vline(R0(bx) - 8 + i * 4, R0(by) + 5, 3, "w")
  c.poly([bx - 6, by + 7, bx + 6, by + 7, bx + 5, by + 12, bx, by + 10, bx - 5, by + 12], "c")
  c.stamp("_ghead", R0(bx) + 1 + (p.hdx || 0), R0(by) - 20 + R0(p.hb || 0) + (p.hdy || 0)); c.stamp("_gear", R0(bx) - 3 + (p.hdx || 0), R0(by) - 21 + R0(p.hb || 0) + (p.hdy || 0))
  leg([hx + 2, hy], p.hN, p.kN, true)
  const sh = [hx + 3 + lean * KG * .4, hy - 11], e = fk(sh[0], sh[1], 9, -p.aN, KG), hd = fk(e[0], e[1], 9, -p.aN + (p.bend || 20), KG)
  limb(c, sh, e, 5, "l"); limb(c, e, hd, 4.4, "l"); limb(c, [sh[0] - 1, sh[1]], [e[0] - 1, e[1]], 1, "L"); c.ellipse(sh[0], sh[1] - 1, 4, 3.4, "N")
  const ca = p.club, c0 = fk(hd[0], hd[1], -6, ca, KG), c1 = fk(hd[0], hd[1], 27, ca, KG)
  limb(c, c0, c1, 5.4, "C"); limb(c, c0, fk(hd[0], hd[1], 10, ca, KG), 3, "c"); limb(c, [c0[0] - .8, c0[1] - .8], [c1[0] - .8, c1[1] - .8], 1, "g")
  for (const q of [14, 18, 22, 26]) { const n = fk(hd[0], hd[1], q, ca, KG); c.px(R0(n[0]) + 3, R0(n[1]) - 1, "T"); c.px(R0(n[0]) - 3, R0(n[1]) + 1, "T"); c.px(R0(n[0]), R0(n[1]) - 3, "n") }
  c.ellipse(hd[0], hd[1], 2.4, 2.2, "l")
  const f = p.fx
  if (f && f.k === "slam") { const tx = R0(c1[0]), ty = R0(c1[1]); c.ellipse(tx, GY, 6 + 22 * f.a, 1 + 3 * f.a, "o", true); c.ellipse(tx, GY, 3 + 14 * f.a, 1 + 2 * f.a, "h", true); for (let i = 0; i < 7; i++) c.px(tx - 18 + i * 6, GY - R0(5 * Math.sin(i * 1.7 + f.a * 5)) - 1, "g") }
}
const GREST = { hN: 10, kN: 18, hF: -10, kF: 18, aN: 6, aF: 8, club: 150, bend: 20, lean: 2, bob: 0, dx: 0, dy: 0, hdx: 0, hdy: 0 }
const gwalk = (t) => { const ph = t * Math.PI * 2, h = 26 * Math.sin(ph); return { ...GREST, hN: h, hF: -h, kN: 12 + 24 * Math.max(0, Math.sin(ph + Math.PI / 2)), kF: 12 + 24 * Math.max(0, -Math.sin(ph + Math.PI / 2)), aN: 10 + h * .15, aF: -h * .6, bob: -Math.abs(Math.cos(ph)) * 2, club: 140 + h * .3 } }
const gidle = (t) => { const b = Math.sin(t * Math.PI * 2); return { ...GREST, bob: -b * 1.0, hb: b * .6, hdy: b * .3 } }
const SLAM = [[0, GREST], [.3, { ...GREST, hN: 6, kN: 34, hF: -16, kF: 34, aN: -140, aF: 30, club: 200, bend: 16, lean: -5, bob: 3 }], [.5, { ...GREST, hN: 6, kN: 18, hF: -20, kF: 14, aN: -165, aF: 50, club: 205, bend: 8, lean: -8, bob: -1 }],
  [.62, { ...GREST, hN: 32, kN: 44, hF: -30, kF: 14, aN: -55, aF: 40, club: 55, bend: 16, lean: 8, bob: 4, dx: 3 }], [.82, { ...GREST, hN: 32, kN: 44, hF: -30, kF: 14, aN: -60, aF: 44, club: 50, bend: 16, lean: 9, bob: 4.5, dx: 3 }], [1, GREST]]
const gslam = (t) => { const p = keyed(SLAM, t, [2]); if (t > .62 && t < .92) p.fx = { k: "slam", a: (t - .62) / .3 }; return p }
const ghurt = (t) => ({ ...GREST, lean: -7 * Math.sin(t * Math.PI), dx: -4 * Math.sin(t * Math.PI), hdx: -2, hdy: 2, aN: 30, club: 120 })
const gstun = (t) => ({ ...GREST, lean: -3, hdy: 4, hdx: -1, aN: 40, club: 100, bob: 2 + Math.sin(t * 12) * .8, kN: 24, kF: 24 })
const gdie = (t) => { const u = Math.min(1, t * 1.3); return { ...GREST, lean: -10 * u, dx: -8 * u, dy: 0, bob: 6 * u, kN: 18 + 60 * u, kF: 18 + 60 * u, hdy: 8 * u, hdx: -3 * u, aN: 40 + 20 * u, club: 90 - 40 * u } }
const GA = (n, f, fr, fps) => anim(n, { w: W, h: H, frames: fr, fps: fps || 14, outline: "k" }, (c) => grunk(c, f(c.phase)))
GA("g_walk", gwalk, 12, 10); GA("g_idle", gidle, 8, 6); GA("g_slam", gslam, 20); GA("g_hurt", ghurt, 6); GA("g_stun", gstun, 8); GA("g_die", gdie, 14)
