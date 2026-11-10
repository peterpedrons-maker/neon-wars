// Rei dos Ratos v3: partes principais desenhadas em grade (cabeça, coroa, punho), corpo por primitivas, membros por esqueleto, 3 ataques.
pal({ k: "#1a1220",
  d: "#4a3a34", f: "#7a634f", F: "#a68a6c", L: "#c9ad88",
  p: "#a0606a", P: "#d89a9a", Q: "#f0c4c0",
  o: "#4c4a1e", O: "#7a7432", y: "#a49c4e",
  g: "#505854", G: "#8a9088",
  b: "#3e2416", B: "#6a4026",
  j: "#a8902c", J: "#e8d070",
  c: "#4a2a1c", C: "#7a4a30", r: "#a85a2c",
  t: "#585650", T: "#9c9a90", u: "#d0cec0",
  e: "#b4ff60", E: "#2c5a1c", w: "#f0e2a8", W: "#b8a468", s: "#7a808e", S: "#b8bece", n: "#e8e8f0", h: "#ffe9a0", m: "#6a1a24" })
ramps("kdfFL", "kpPQ", "koOy", "kgG", "kbB", "kcCr", "ktTu")

// ---- partes desenhadas à mão ----
sprite("_head", `
  .....dffff..........
  ..dd.dfFFFFfff......
  .dPPdfFFFFFFFFff....
  .dPQPfFFFFFFFFFFff..
  .dPQPfFFFFFFFEEFFFff
  ..dPPfFFFFFFEeeEFFFfP
  ...dfFFFFFFFFEEFFFFFfPP
  ...dffFFFFFFFFFFFFFFfPQ
  ....dffFFFFFFFFFFFFFffP
  .....dffFFFFFFFFFFffww.
  ......dffffFFFFFfffwW..
  .......dddffffffff.....`)
sprite("_head_open", `
  .....dffff..........
  ..dd.dfFFFFfff......
  .dPPdfFFFFFFFFff....
  .dPQPfFFFFFFFFFFff..
  .dPQPfFFFFFFFEEFFFff
  ..dPPfFFFFFFEeeEFFFfP
  ...dfFFFFFFFFEEFFFFFfPP
  ...dffFFFFFFFFFFFFFFfPQ
  ....dffFFFFFFFFFFFFww.P
  .....dffFFFFFFFFFFfwWmm
  ......dfffFFFFFFffmmmmm
  .......dffmmmmmmmmmmmm.
  ........dfffwWpppppwWf.
  .........dffffffffwf...`)
sprite("_crown", `
  .u.....u....u..
  .u.....u....u..
  .u..u..u..u.u..
  .uu.u..uu.u.uu.
  TTTTTTTTTTTTTTT
  TuTTTuTTTuTTTuT
  tTTTTTjjTTTTTTt
  ttttttjJtttttt.`)
sprite("_fist", `
  .dff.
  dfFFf
  dfFLf
  dfFFf
  .dff.`)
sprite("_cap", `
  .jJj.
  jJhJj
  .jJj.`)

const K = 0.62, GY = 64, OX = 22
const R = Math.PI / 180
const fk = (x, y, L, a) => [x + L * K * Math.sin(a * R), y + L * K * Math.cos(a * R)]
const R0 = Math.round
const lerp = (a, b, u) => a + (b - a) * u
function limb(c, a, b, w, col) { c.line(R0(a[0]), R0(a[1]), R0(b[0]), R0(b[1]), col, Math.max(1, Math.round(w))) }
function leg(c, hip, hd, kn, near) {
  const k = fk(hip[0], hip[1], 11, hd), a = fk(k[0], k[1], 11, hd - kn)
  const m = near ? "f" : "d", h = near ? "F" : "f"
  limb(c, hip, k, 6.4 * K, m); limb(c, k, a, 4.6 * K, m)
  limb(c, [hip[0] - 1, hip[1]], [k[0] - 1, k[1]], 2, h); limb(c, [k[0] - 1, k[1] + 1], [a[0] - 1, a[1]], 1, h)
  const fo = [a[0] + 3.4, a[1] + 0.8]; limb(c, a, fo, 3, m); c.px(R0(fo[0]) + 1, R0(fo[1]) + 1, "k"); c.px(R0(fo[0]) + 1, R0(fo[1]) - 1, "k")
  if (near) { c.hline(R0(k[0]) - 1, R0(k[1]) + 3, 3, "s"); c.px(R0(k[0]) - 1, R0(k[1]) + 3, "S") }
}
function tipOf(p) {   // ponta do cano (para rastro)
  const hx = OX + 22 + (p.dx || 0), feetY = 0
  return null
}
function pose(c, p) {
  const lean = p.lean || 0, dx = p.dx || 0
  const hx = OX + 22 + dx
  const feet = Math.max(...[[p.hF, p.kF], [p.hN, p.kN]].map(([hd, kn]) => { const k = fk(0, 0, 11, hd), a = fk(k[0], k[1], 11, hd - kn); return a[1] }))
  const hy = GY - feet - 1 + (p.bob || 0) * K

  const tw = (p.tail || 0) * K
  limb(c, [hx - 5, hy + 1], [hx - 11, hy + 4 + tw], 2, "P"); limb(c, [hx - 11, hy + 4 + tw], [hx - 16, hy + 2 - tw], 1.5, "P"); limb(c, [hx - 16, hy + 2 - tw], [hx - 20, hy + 5 - tw * .5], 1, "P")
  leg(c, [hx, hy], p.hF, p.kF, false)
  const sh = [hx + 5 + lean * K * .5, hy - 14], eF = fk(sh[0], sh[1], 8, -p.aF), hF = fk(eF[0], eF[1], 8, -p.aF + 22)
  limb(c, sh, eF, 3, "d"); limb(c, eF, hF, 2.4, "d"); c.ellipse(hF[0], hF[1], 1.6, 1.5, "d")
  const bx = hx + 1 + lean * K * .4, by = hy - 8
  // corpo: pelo em 4 tons, sombra à direita, barriga rosada
  c.ellipse(bx, by, 9, 8.5, "f"); c.ellipse(bx - 1, by - 1, 7, 7, "F"); c.ellipse(bx - 3, by - 3, 3, 2.6, "L")
  c.ellipse(bx + 7, by + 1, 2.2, 6, "d")
  c.ellipse(bx + 1, by + 3, 6, 6, "P"); c.ellipse(bx, by + 2, 4, 4, "Q"); c.ellipse(bx + 5, by + 3, 2, 4, "p")
  c.poly([bx - 6, by + 5, bx + 7, by + 5, bx + 6, by + 12, bx + 3, by + 9, bx, by + 13, bx - 3, by + 9, bx - 6, by + 11], "g")
  c.poly([bx - 6, by + 5, bx, by + 5, bx - 1, by + 10, bx - 4, by + 9], "G")
  c.rect(R0(bx - 8), R0(by + 3), 16, 2, "b"); c.hline(R0(bx - 8), R0(by + 3), 16, "B"); c.stamp("_cap", R0(bx) - 1, R0(by) + 2)
  // manto de trapos com remendo
  c.poly([bx - 9, by - 9, bx - 2, by - 14, bx + 8, by - 13, bx + 10, by - 7, bx + 6, by - 4, bx + 3, by - 7, bx + 1, by - 2, bx - 2, by - 4, bx - 5, by + 0, bx - 8, by - 2], "O")
  c.poly([bx - 9, by - 9, bx - 2, by - 14, bx + 2, by - 13, bx - 4, by - 7, bx - 8, by - 2], "y")
  c.poly([bx + 6, by - 4, bx + 10, by - 7, bx + 8, by - 3], "o"); c.rect(R0(bx - 6), R0(by - 9), 4, 3, "y"); c.hline(R0(bx - 6), R0(by - 7), 4, "O"); c.px(R0(bx) - 5, R0(by) - 8, "o")
  c.ellipse(bx + 7, by - 6, 1.4, 1.4, "O")
  // cabeça e coroa (grades)
  const open = p.mouth || 0, th = p.hdx || 0, tv = p.hdy || 0
  const hxh = R0(bx + 1 + th + (p.hb ? 0 : 0)), hyh = R0(by - 19 + (p.hb || 0) + tv)
  limb(c, [bx + 2, by - 7], [hxh + 7, hyh + 8], 6, "f"); limb(c, [bx + 1, by - 8], [hxh + 6, hyh + 7], 3, "F")
  c.stamp(open ? "_head_open" : "_head", hxh, hyh)
  c.stamp("_crown", hxh + 1, hyh - 6)
  leg(c, [hx + 1, hy], p.hN, p.kN, true)
  // braço perto, braçadeira, punho e cano
  const sh2 = [hx + 2 + lean * K * .5, hy - 14], e = fk(sh2[0], sh2[1], 8, -p.aN), hd = fk(e[0], e[1], 8, -p.aN + (p.bend || 26))
  limb(c, sh2, e, 3.4, "f"); limb(c, e, hd, 3, "f"); limb(c, [sh2[0] - 1, sh2[1]], [e[0] - 1, e[1]], 1, "F")
  const mm = [(e[0] + hd[0]) / 2, (e[1] + hd[1]) / 2]; c.ellipse(mm[0], mm[1], 2.2, 1.8, "s"); c.px(R0(mm[0]) - 1, R0(mm[1]) - 1, "S")
  const ca = p.club, c0 = fk(hd[0], hd[1], -6, ca), c1 = fk(hd[0], hd[1], 22, ca)
  limb(c, c0, c1, 3.4, "C"); limb(c, c0, fk(hd[0], hd[1], 9, ca), 2, "c"); limb(c, [c0[0] - .5, c0[1] - .5], [c1[0] - .5, c1[1] - .5], 1, "r")
  for (const q of [13, 17, 20]) { const n = fk(hd[0], hd[1], q, ca); c.px(R0(n[0]) + 2, R0(n[1]) - 1, "n"); c.px(R0(n[0]) - 2, R0(n[1]) + 1, "s") }
  c.stamp("_fist", R0(hd[0]) - 2, R0(hd[1]) - 2)
  // efeitos
  const fx = p.fx
  if (fx) {
    if (fx.kind === "smash") {
      const tx = R0(c1[0]), ty = R0(c1[1]), a = fx.a
      for (let i = 0; i < 6; i++) { const an = (-80 + i * 32) * R; c.line(tx, ty, R0(tx + Math.cos(an) * (6 + 8 * a)), R0(ty + Math.sin(an) * (4 + 6 * a)), i % 2 ? "n" : "J", 1) }
      c.ellipse(tx, GY, 6 + 12 * a, 1 + 2 * a, "u", true)
    } else if (fx.kind === "sweep") {
      for (let i = 0; i < fx.trail.length; i++) { const [x0, y0, x1, y1] = fx.trail[i]; c.line(R0(x0), R0(y0), R0(x1), R0(y1), i < 1 ? "n" : (i < 2 ? "S" : "s"), 1) }
    } else if (fx.kind === "cast") {
      const cx = R0(bx), cy = R0(by); for (let i = 0; i < 3; i++) c.ellipse(cx, GY - 2, 8 + 22 * fx.a - i * 4, 2 + 5 * fx.a - i, i ? "e" : "n", true)
      for (let i = 0; i < 6; i++) c.px(cx - 14 + i * 6, GY - 2 - R0(10 * fx.a * Math.abs(Math.sin(i * 1.3 + fx.a * 4))), "e")
    } else if (fx.kind === "plague") {
      const tx = R0(c1[0]), ty = R0(c1[1]); c.ellipse(tx, GY, 6 + 16 * fx.a, 1 + 3 * fx.a, "e", true); c.ellipse(tx, GY, 3 + 9 * fx.a, 1 + 2 * fx.a, "n", true)
      for (let i = 0; i < 8; i++) { const an = (-150 + i * 30) * R; c.px(R0(tx + Math.cos(an) * (4 + 12 * fx.a)), R0(ty + Math.sin(an) * (3 + 8 * fx.a)), "e") }
    } else if (fx.kind === "dig") {
      for (let i = 0; i < 9; i++) c.px(hx - 8 + i * 3, GY - R0(1 + 6 * fx.a * Math.abs(Math.sin(i * 1.9))), i % 2 ? "f" : "d")
      c.ellipse(hx + 3, GY, 6 + 14 * fx.a, 1 + 3 * fx.a, "g", true)
    } else if (fx.kind === "bite") {
      const sx = hxh + 22, sy = hyh + 8
      for (let i = 0; i < 5; i++) { const an = (-60 + i * 30) * R; c.line(sx, sy, R0(sx + Math.cos(an) * 7), R0(sy + Math.sin(an) * 7), i % 2 ? "n" : "h", 1) }
    }
  }
  return { c1 }
}
const walk = (t) => { const ph = t * Math.PI * 2, hN = 30 * Math.sin(ph); return { hN, hF: -hN, kN: 6 + 34 * Math.max(0, Math.sin(ph + Math.PI / 2)), kF: 6 + 34 * Math.max(0, -Math.sin(ph + Math.PI / 2)), aN: 10 + hN * .15, aF: -hN * .7, club: 70 + hN * .2, bob: -Math.abs(Math.cos(ph)) * 1.6, lean: 1, tail: Math.sin(ph) * 2, hb: Math.sin(ph * 2) * .6 } }
const idle = (t) => { const b = Math.sin(t * Math.PI * 2); return { hN: 10, kN: 14, hF: -8, kF: 12, aN: 8, aF: 4, club: 72, bob: -b * .8, lean: 1, tail: b * 1.5, hb: b * .8 } }
function keyed(KEYS, t, hard) {
  for (let i = 0; i < KEYS.length - 1; i++) {
    const [t0, a] = KEYS[i], [t1, b] = KEYS[i + 1]
    if (t >= t0 && t <= t1) { let u = (t - t0) / (t1 - t0); u = (hard && hard.includes(i)) ? u * u : u * u * (3 - 2 * u); const r = {}; for (const k in a) r[k] = typeof a[k] === "number" ? lerp(a[k], b[k], u) : (u < .5 ? a[k] : b[k]); return r }
  }
  return { ...KEYS[KEYS.length - 1][1] }
}
const REST = { hN: 14, kN: 16, hF: -14, kF: 14, aN: 8, aF: 6, club: 72, bend: 26, lean: 1, bob: 0, tail: 0, dx: 0, hdx: 0, hdy: 0, mouth: 0 }
// 1) PANCADA: cano por cima da cabeça
const SMASH = [[0, REST], [.22, { ...REST, hN: 8, kN: 30, hF: -20, kF: 28, aN: -40, aF: 30, club: 150, bend: 30, lean: -3, bob: 1.5, tail: 2 }],
  [.42, { ...REST, hN: 6, kN: 10, hF: -24, kF: 10, aN: -140, aF: 60, club: 200, bend: 14, lean: -5, bob: -1, tail: 3 }],
  [.56, { ...REST, hN: 34, kN: 44, hF: -36, kF: 10, aN: -50, aF: 40, club: 60, bend: 18, lean: 5, bob: 3, tail: -2, dx: 3 }],
  [.72, { ...REST, hN: 34, kN: 44, hF: -36, kF: 10, aN: -56, aF: 44, club: 52, bend: 18, lean: 6, bob: 3.5, tail: -3, dx: 3 }], [1, REST]]
// 2) VARRIDA: cano horizontal, o corpo gira
const SWEEP = [[0, REST], [.25, { ...REST, hN: 4, kN: 24, hF: -26, kF: 24, aN: 80, aF: -20, club: -75, bend: 10, lean: -4, bob: 1.5, tail: 3, dx: -2 }],
  [.40, { ...REST, hN: 4, kN: 26, hF: -28, kF: 26, aN: 90, aF: -26, club: -88, bend: 6, lean: -6, bob: 2, tail: 4, dx: -3 }],
  [.58, { ...REST, hN: 30, kN: 40, hF: -34, kF: 12, aN: -70, aF: 50, club: 100, bend: 8, lean: 6, bob: 2, tail: -3, dx: 4 }],
  [.74, { ...REST, hN: 30, kN: 40, hF: -34, kF: 12, aN: -80, aF: 56, club: 112, bend: 6, lean: 7, bob: 2.5, tail: -4, dx: 5 }], [1, REST]]
// 3) MORDIDA: agacha, investe com a cabeça
const BITE = [[0, REST], [.25, { ...REST, hN: 22, kN: 52, hF: -20, kF: 48, aN: 40, aF: 10, club: 20, bend: 22, lean: -6, bob: 4, tail: 3, dx: -3, hdx: -2, hdy: 1 }],
  [.45, { ...REST, hN: 40, kN: 28, hF: -30, kF: 14, aN: 30, aF: -10, club: 30, bend: 22, lean: 8, bob: 3, tail: -3, dx: 8, hdx: 9, hdy: 3, mouth: 1 }],
  [.60, { ...REST, hN: 40, kN: 28, hF: -30, kF: 14, aN: 30, aF: -10, club: 30, bend: 22, lean: 8, bob: 3, tail: -2, dx: 9, hdx: 10, hdy: 3, mouth: 0 }],
  [.80, { ...REST, hN: 24, kN: 22, hF: -20, kF: 16, aN: 14, aF: 4, club: 60, bend: 24, lean: 3, bob: 1, tail: 1, dx: 4, hdx: 4, hdy: 1 }], [1, REST]]
const attack1 = (t) => { const p = keyed(SMASH, t, [2]); if (t >= .56 && t <= .8) p.fx = { kind: "smash", a: (t - .56) / .24 }; return p }
const attack2 = (t) => { const p = keyed(SWEEP, t); if (t >= .5 && t <= .78) { const trail = []; for (let i = 1; i <= 3; i++) { const q = keyed(SWEEP, t - i * .02), r = keyed(SWEEP, t - (i - 1) * .02); trail.push([...tipXY(q), ...tipXY(r)]) } p.fx = { kind: "sweep", trail } } return p }
const attack3 = (t) => { const p = keyed(BITE, t); if (t >= .46 && t <= .66) p.fx = { kind: "bite" }; return p }
function tipXY(p) {   // ponta do cano para o rastro da varrida
  const lean = p.lean || 0, dx = p.dx || 0, hx = OX + 22 + dx
  const feet = Math.max(...[[p.hF, p.kF], [p.hN, p.kN]].map(([hd, kn]) => { const k = fk(0, 0, 11, hd), a = fk(k[0], k[1], 11, hd - kn); return a[1] }))
  const hy = GY - feet - 1 + (p.bob || 0) * K, sh2 = [hx + 2 + lean * K * .5, hy - 14], e = fk(sh2[0], sh2[1], 8, -p.aN), hd = fk(e[0], e[1], 8, -p.aN + (p.bend || 26))
  return fk(hd[0], hd[1], 22, p.club)
}
const hurt = (t) => ({ ...REST, lean: -6 * Math.sin(t * Math.PI), dx: -3 * Math.sin(t * Math.PI), hdx: -2, hdy: 1, mouth: 1, aN: 24, club: 110 })
const die = (t) => { const u = Math.min(1, t * 1.25); return { ...REST, lean: -8 * u, dx: -6 * u, bob: 6 * u, kN: 18 + 50 * u, kF: 18 + 50 * u, hN: 14 + 16 * u, hF: -14 - 16 * u, hdy: 8 * u, hdx: -3 * u, aN: 30 + 20 * u, club: 90 - 50 * u, mouth: u > .4 ? 1 : 0 } }
const CAST = [[0, REST], [.3, { ...REST, aN: -150, club: 200, bend: 4, lean: -4, mouth: 1, hdy: -1, bob: 1 }], [.75, { ...REST, aN: -150, club: 200, bend: 4, lean: -5, mouth: 1, hdy: -1, bob: 1 }], [1, REST]]
const cast = (t) => { const p = keyed(CAST, t); if (t > .3 && t < .95) p.fx = { kind: "cast", a: Math.min(1, (t - .3) / .5) }; return p }
const plague = (t) => { const p = keyed(SMASH, t, [2]); if (t >= .56 && t <= .8) p.fx = { kind: "plague", a: (t - .56) / .24 }; return p }
const DIG = [[0, REST], [.3, { ...REST, hN: 30, kN: 60, hF: -30, kF: 60, aN: 30, club: 40, lean: 6, bob: 6, mouth: 1 }], [.7, { ...REST, hN: 40, kN: 76, hF: -40, kF: 76, aN: 40, club: 30, lean: 8, bob: 11, hdy: 4, mouth: 1 }], [1, { ...REST, hN: 40, kN: 76, hF: -40, kF: 76, aN: 40, club: 30, lean: 8, bob: 14, hdy: 6 }]]
const dig = (t) => { const p = keyed(DIG, t); p.fx = { kind: "dig", a: t }; return p }
const W = 96, H = 72
anim("rat_hurt", { w: W, h: H, frames: 6, fps: 14, outline: "k" }, (c) => pose(c, hurt(c.phase)))
anim("rat_die", { w: W, h: H, frames: 14, fps: 14, outline: "k" }, (c) => pose(c, die(c.phase)))
anim("rat_cast", { w: W, h: H, frames: 16, fps: 14, outline: "k" }, (c) => pose(c, cast(c.phase)))
anim("rat_plague", { w: W, h: H, frames: 18, fps: 14, outline: "k" }, (c) => pose(c, plague(c.phase)))
anim("rat_dig", { w: W, h: H, frames: 14, fps: 14, outline: "k" }, (c) => pose(c, dig(c.phase)))
anim("rat_walk", { w: W, h: H, frames: 12, fps: 12, outline: "k" }, (c) => pose(c, walk(c.phase)))
anim("rat_idle", { w: W, h: H, frames: 8, fps: 6, outline: "k" }, (c) => pose(c, idle(c.phase)))
anim("rat_atk1", { w: W, h: H, frames: 18, fps: 14, outline: "k" }, (c) => pose(c, attack1(c.phase)))
anim("rat_atk2", { w: W, h: H, frames: 18, fps: 14, outline: "k" }, (c) => pose(c, attack2(c.phase)))
anim("rat_atk3", { w: W, h: H, frames: 18, fps: 14, outline: "k" }, (c) => pose(c, attack3(c.phase)))
