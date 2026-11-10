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
  const f = null
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


// ---- frente e costas ----
sprite("_wfront", `
  ....RR.....
  ...RRRR....
  ..sSSSSSs..
  .sSSzzSSSs.
  .sSkkkkkSs.
  .sSSSSSSSs.
  .sSSvvvSSs.
  ..sSSvSSs..
  ...ssSss...`)
sprite("_wback", `
  ....RR.....
  ...RRRR....
  ..sSSSSSs..
  .sSSzzSSSs.
  .sSSSSSSSs.
  .sSSSSSSSs.
  .sSRRRRRSs.
  ..sSRRRSs..
  ...ssSss...`)
function frontback(c, p, back) {
  const cx = OX + 21, bob = p.bob || 0, ly = (p.ly || 0), ry = -(p.ly || 0), sw = p.sw || 0
  const hy = GY - 30 + bob
  // pernas
  for (const [dx, off, col] of [[-3, ly, "S"], [3, ry, "s"]]) {
    const top = hy + 16 + (off > 0 ? 0 : 0), len = 12 - Math.max(0, -off)
    c.rect(cx + dx - 2, R0(top), 4, R0(len + Math.max(0, off)), col); c.vline(cx + dx - 2, R0(top), R0(len), "z")
    c.rect(cx + dx - 3, R0(GY - 3 + Math.min(0, off)), 6, 3, "b"); c.hline(cx + dx - 3, R0(GY - 3 + Math.min(0, off)), 6, "B")
  }
  // braços (balançam ao contrário)
  c.rect(cx - 9, R0(hy + 7 + sw), 3, 9, "s"); c.rect(cx + 7, R0(hy + 7 - sw), 3, 9, "a"); c.ellipse(cx - 8, R0(hy + 17 + sw), 2, 2, "v"); c.ellipse(cx + 8, R0(hy + 17 - sw), 2, 2, "v")
  if (!back) { limb(c, [cx - 8, hy + 17 + sw], [cx - 8, hy + 8 + sw], 1, "T") } else c.stamp("_wshield", cx + 5, R0(hy + 9 - sw))
  // tronco
  c.ellipse(cx, hy + 11, 7.5, 8, "s"); c.ellipse(cx - 1, hy + 10, 6, 6.6, "S"); c.ellipse(cx - 2, hy + 8, 2.4, 2.6, "z")
  if (!back) { c.poly([cx - 2, hy + 13, cx + 2, hy + 13, cx + 3, hy + 22, cx - 3, hy + 22], "R"); c.poly([cx - 2, hy + 13, cx, hy + 13, cx - 1, hy + 22, cx - 3, hy + 22], "q") }
  c.rect(cx - 7, R0(hy + 15), 14, 2, "b"); c.hline(cx - 7, R0(hy + 15), 14, "B"); if (!back) c.rect(cx - 1, R0(hy + 15), 3, 2, "j")
  // ombreiras
  c.ellipse(cx - 7, hy + 6, 3.2, 3, "S"); c.ellipse(cx + 7, hy + 6, 3.2, 3, "s"); c.px(cx - 8, hy + 5, "z")
  c.stamp(back ? "_wback" : "_wfront", cx - 5, R0(hy - 9))
}
const fbwalk = (t) => { const ph = t * Math.PI * 2; return { bob: -Math.abs(Math.cos(ph)) * 1.2, ly: Math.sin(ph) * 3, sw: Math.sin(ph) * 2 } }
anim("w_front", { w: W, h: H, frames: 8, fps: 10, outline: "k" }, (c) => frontback(c, fbwalk(c.phase), false))
anim("w_back", { w: W, h: H, frames: 8, fps: 10, outline: "k" }, (c) => frontback(c, fbwalk(c.phase), true))
