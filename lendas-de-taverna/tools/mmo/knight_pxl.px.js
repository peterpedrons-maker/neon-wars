// Guerreiro no estilo da referência (sprite pequeno, poucos tons, poses-chave à mão, contorno escuro)
pal({ k: "#1a1420",
  a: "#4a4652", s: "#8a868e", S: "#c4c0c6", z: "#f4f2f4",
  r: "#6a1626", R: "#c0283c", q: "#e85868", P: "#e0c8c8", p: "#b09898",
  b: "#2e2a34", c: "#5e5a68", n: "#f8f8ff", g: "#b8a050", d: "#8a7430", e: "#2a6aff" })
sprite("_helm", `
  ..aSSSSa..
  .aSzzSSsa.
  .aSzSSSsa.
  .aSSSSSsa.
  .aSkkkkkka
  .aSSSSSsa.
  .aSSSSSsa.
  .aSsSkSkSa
  .aSSSSSsa.
  ..aSSSsa..
  ...aaaaa..`)
sprite("_torso", `
  .aSSSSSsa.
  aSzSSSSssa
  aSzSSRrSsa
  aSSSSRrSsa
  aSSSSRrSsa
  .aSSSRrsa.
  .abbbbbba.
  ..bgggdb..`)
sprite("_skirt", `
  rRrRrRrRrR
  .RrRrRrRr.
  ..R.rR.r..`)
sprite("_shield", `
  ..ssssss..
  .sSSSSSSs.
  sSPPPRRRRs
  sPPPPRRRRs
  sPPPPRRRqs
  .sPPRRRqs.
  .sPPRRqqs.
  ..sPRRqs..
  ...sRRs...
  ....ss....`)
sprite("_boot", `
  bbbb.
  cbbbb
  bbbbbb`)
const R0 = Math.round
function limb(c, a, b, w, col) { c.line(R0(a[0]), R0(a[1]), R0(b[0]), R0(b[1]), col, w) }
// pernas por pose: [joelho, tornozelo] relativos ao quadril
const LEGS = {
  P1: { n: [[4, 6], [8, 12]], f: [[-3, 6], [-8, 10]] },
  P2: { n: [[3, 6], [3, 12]], f: [[-2, 8], [-9, 6]] },
  P3: { n: [[1, 6], [0, 12]], f: [[5, 3], [2, 8]] },
}
const SEQ = [["P1", 0], ["P2", 0], ["P3", 0], ["P1", 1], ["P2", 1], ["P3", 1]]
const BOB = [1, 2, 0, 1, 2, 0]
function blade(c, h, t) {   // lâmina de 2 px com realce + guarda + cabo
  c.line(R0(h[0]), R0(h[1]), R0(t[0]), R0(t[1]), "n", 1); c.line(R0(h[0]), R0(h[1]) + 1, R0(t[0]), R0(t[1]) + 1, "S", 1)
  const dx = t[0] - h[0], dy = t[1] - h[1], L = Math.hypot(dx, dy) || 1, ux = dx / L, uy = dy / L
  const gx = h[0] + ux * 2, gy = h[1] + uy * 2; c.line(R0(gx - uy * 3), R0(gy + ux * 3), R0(gx + uy * 3), R0(gy - ux * 3), "g", 1)
  c.px(R0(h[0] - ux), R0(h[1] - uy), "d")
}
function legs(c, hip, N, Fr) {
  const leg = (kn, an, near) => {
    const k = [hip[0] + kn[0], hip[1] + kn[1]], a = [hip[0] + an[0], hip[1] + an[1]]
    limb(c, hip, k, 3, near ? "S" : "c"); limb(c, k, a, 3, near ? "s" : "a")
    limb(c, [hip[0] - 1, hip[1]], [k[0] - 1, k[1]], 1, near ? "z" : "s"); c.px(k[0], k[1], near ? "z" : "s")
    c.stamp("_boot", a[0] - 2, a[1] - 1)
  }
  return { far: () => leg(Fr[0], Fr[1], false), near: () => leg(N[0], N[1], true) }
}
function body(c, hip, dx, dy, shY) {
  c.stamp("_torso", hip[0] - 5, hip[1] - 14); c.stamp("_skirt", hip[0] - 5, hip[1] - 3); c.stamp("_helm", hip[0] - 5 + dx, hip[1] - 24 + dy)
}
function knight(c, i) {
  const [pn, sw] = SEQ[i], L = LEGS[pn], hip = [30, 31 + BOB[i]], N = sw ? L.f : L.n, Fr = sw ? L.n : L.f, lg = legs(c, hip, N, Fr)
  lg.far()
  const hand = [hip[0] - 6, hip[1] - 7 + (i % 3 === 1 ? 1 : 0)]
  limb(c, [hip[0] - 2, hip[1] - 14], hand, 2, "s"); blade(c, hand, [hand[0] - 15, hand[1] - 6 + (i % 3 === 2 ? -1 : 0)])
  body(c, hip, i % 3 === 1 ? 1 : 0, 0); lg.near()
  c.stamp("_shield", hip[0] + 1, hip[1] - 17 + (i % 3 === 1 ? 1 : 0))
}
const STAND = { n: [[2, 6], [2, 12]], f: [[-2, 6], [-4, 12]] }
function idle(c, i) {
  const b = [0, 1, 1, 0][i], hip = [30, 31 + b], lg = legs(c, hip, STAND.n, STAND.f); lg.far()
  const hand = [hip[0] - 5, hip[1] - 6]; limb(c, [hip[0] - 2, hip[1] - 14], hand, 2, "s"); blade(c, hand, [hand[0] - 14, hand[1] - 7])
  body(c, hip, 0, [0, 0, 1, 1][i]); lg.near(); c.stamp("_shield", hip[0] + 1, hip[1] - 17 + (i > 1 ? 1 : 0))
}
// ataque: espada acima da cabeça e para baixo, à frente
const AT = [
  { hand: [-6, -7], tip: [-21, -13], leg: LEGS.P2, dx: 0 },
  { hand: [-5, -16], tip: [-12, -31], leg: { n: [[3, 6], [3, 12]], f: [[-3, 6], [-6, 12]] }, dx: -1 },
  { hand: [1, -23], tip: [-3, -39], leg: { n: [[4, 6], [5, 12]], f: [[-3, 6], [-7, 12]] }, dx: -1 },
  { hand: [8, -15], tip: [22, -11], leg: { n: [[5, 6], [9, 12]], f: [[-3, 6], [-9, 12]] }, dx: 1 },
  { hand: [11, -8], tip: [25, 3], leg: { n: [[5, 6], [10, 12]], f: [[-3, 6], [-9, 12]] }, dx: 2, fx: 1 },
  { hand: [4, -8], tip: [-6, -13], leg: LEGS.P2, dx: 0 }]
function attack(c, i) {
  const A = AT[i], hip = [30, 31 + (i === 3 || i === 4 ? 2 : 0)], lg = legs(c, hip, A.leg.n, A.leg.f); lg.far()
  const hand = [hip[0] + A.hand[0], hip[1] + A.hand[1]], tip = [hip[0] + A.tip[0], hip[1] + A.tip[1]]
  const front = i >= 2 && i <= 4
  if (!front) { limb(c, [hip[0] - 2, hip[1] - 14], hand, 2, "s"); blade(c, hand, tip) }
  body(c, hip, A.dx, i === 3 || i === 4 ? 1 : 0); lg.near()
  if (front) { limb(c, [hip[0] + 1, hip[1] - 13], hand, 2, "s"); blade(c, hand, tip) }
  c.stamp("_shield", hip[0] + 1 + (i >= 3 ? 1 : 0), hip[1] - 17 + (i >= 3 ? 1 : 0))
  if (A.fx) { const tx = R0(tip[0]), ty = R0(tip[1]); for (let k = 0; k < 6; k++) { const an = (-100 + k * 36) * Math.PI / 180; c.line(tx, ty, R0(tx + Math.cos(an) * 6), R0(ty + Math.sin(an) * 5), k % 2 ? "n" : "g", 1) } }
}
anim("k_run", { w: 64, h: 52, frames: 6, fps: 12, outline: "k" }, (c) => knight(c, c.frame))
anim("k_idle", { w: 64, h: 52, frames: 4, fps: 4, outline: "k" }, (c) => idle(c, c.frame))
anim("k_atk", { w: 64, h: 52, frames: 6, fps: 9, outline: "k" }, (c) => attack(c, c.frame))
