const { chromium } = require('playwright'); const fs = require('fs');
const mode = process.argv[2] || 'farm', secs = +(process.argv[3] || 40), pow = +(process.argv[4] || 8), hpm = +(process.argv[5] || 8);
(async () => {
  const b = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await b.newPage({ viewport: { width: 390, height: 844 } });
  p.on('pageerror', () => {});
  await p.goto('http://localhost:8760/index.html'); await p.waitForTimeout(2200);
  const click = async (t) => { const el = await p.$(`text=${t}`); if (el) { await el.click({ force: true }).catch(() => {}); await p.waitForTimeout(800); } };
  await click('NOVO HERÓI'); await click('Avançar'); await click('Avançar');
  await p.fill('input', 'Teste'); await click('CRIAR HERÓI'); await p.waitForTimeout(1800);
  const data = await p.evaluate(async ({ mode, secs, pow, hpm }) => {
    const r = Math.round, o1 = v => Math.round(v * 10) / 10;
    if (mode === 'town') { await new Promise(res => setTimeout(res, 1500)); } else {
    if (mode === 'boss') arenaStart(5, false); else enterDungeon(5);
    await new Promise(res => setTimeout(res, 4500)); }
    G.hero.pow *= pow; G.hero.maxhp *= hpm; G.hero.hp = G.hero.maxhp;
    if (mode === 'boss') { for (let k = 0; k < 40; k++) __mmo.update(1 / 60); if (!G.boss) { G.phase = 'farm'; __mmo.spawnBoss(); } }
    let nid = 1; const frames = []; const hp0 = G.hero.maxhp;
    const prim = (o, keys) => { const q = {}; for (const k of keys) { const v = o[k]; if (v !== undefined && v !== null && typeof v !== 'object' && typeof v !== 'function') q[k] = typeof v === 'number' ? Math.round(v * 100) / 100 : v; } return q; };
    const ROUTE = [[1,0,.5],[1,0,1],[0,1,.5],[0,1,1],[-1,0,1],[0,-1,.5],[1,0,1]];
    for (let i = 0; i < 60 * secs; i++) {
      if (mode === 'town') { const seg = ROUTE[Math.floor(i / 60 / 2.2) % ROUTE.length]; G.joy.x = seg[0]; G.joy.y = seg[1]; G.joy.m = seg[2]; }
      __mmo.update(1 / 60);
      if (i % 2) continue;
      const h = G.hero;
      const F = { t: o1(G.t), ph: G.phase, hero: { ...prim(h, ['x', 'y', 'row', 'state', 'animT', 'hp', 'maxhp', 'flash', 'hurtT', 'inv', 'cd', 'run', 'rk']), act: h.act ? prim(h.act, ['t', 'dur', 'hit', 'done']) : null, dod: h.dod ? prim(h.dod, ['t', 'dur', 'dx', 'dy', 'type']) : null }, mobs: [], zones: [], mp: [], pr: [], fl: [], loot: [] };
      for (const m of G.mobs) { if (!m.__id) m.__id = nid++; F.mobs.push({ id: m.__id, ...prim(m, ['x', 'y', 'row', 'state', 'animT', 'hp', 'maxhp', 'flash', 'dead', 'deadT', 'name', 'elite', 'flipX']), atlas: m.T && m.T.atlas, fam: m.T && m.T.fam, boss: m === G.boss ? 1 : 0, act: m.act ? prim(m.act, ['t', 'dur', 'done']) : null }); }
      for (const z of G.zones) F.zones.push(prim(z, ['shape', 'x', 'y', 'r', 'a', 'w', 'len', 'warn', 't', 'done', 'col', 'pc', 'ang', 'arc', 'r0', 'r1']));
      for (const q of (G.mprojs || [])) F.mp.push(prim(q, ['x', 'y', 'vx', 'vy', 'col', 'r', 'kind']));
      for (const q of (G.projs || [])) F.pr.push(prim(q, ['x', 'y', 'vx', 'vy', 'col', 'r', 'kind']));
      for (const q of (G.floats || [])) F.fl.push(prim(q, ['kd', 'x', 'y', 't', 'col', 'size', 'life', 'max']));
      for (const q of (G.loot || [])) F.loot.push({ ...prim(q, ['x', 'y', 'fly', 't', 'rest', 'h']), rar: q.it && q.it.rar, ic: q.it && q.it.icon });
      F.boss = G.boss ? { hp: G.boss.hp, maxhp: G.boss.maxhp } : null;
      frames.push(F);
      if (mode === 'boss' && G.boss && G.boss.dead && i > 60) { for (let k = 0; k < 90; k++) { __mmo.update(1 / 60); if (k % 2 === 0) { frames.push({ ...F, t: o1(G.t) }); } } break; }
    }
    return { frames, map: G.map, cam: G.cam && { x: G.cam.x, y: G.cam.y } };
  }, { mode, secs, pow, hpm });
  fs.writeFileSync(`trace_${mode}.json`, JSON.stringify(data)); console.log(mode, data.frames.length, data.map);
  await b.close();
})();
