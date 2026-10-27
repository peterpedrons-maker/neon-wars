/* Gera assets/status/*.png (ícones coloridos 48x48, com contorno escuro) a partir do game-icons.net
   (pacote npm @iconify-json/game-icons, CC BY 3.0). Cor e ícone de cada status ficam em STATUS_ICONS.
   Uso: npm i @iconify-json/game-icons playwright && node tools/build_status_icons.cjs */
const fs = require('fs'), path = require('path');
const { chromium } = require('playwright');
const SET = require('@iconify-json/game-icons/icons.json').icons;
const STATUS_ICONS = {
  veneno:['poison-bottle','#7fd35a'], queimadura:['flame','#ff8a3a'], sangramento:['bleeding-wound','#e0483a'],
  atordoado:['star-swirl','#ffd34a'], preso:['spider-web','#c9a46a'], lento:['snail','#8fb8f0'], gelado:['snowflake-1','#9fe6ff'],
  medo:['screaming','#c79bf0'], provocado:['angry-eyes','#ff7a5a'], abalado:['cracked-shield','#d98fe0'],
  enfraquecido:['broken-arrow','#c9b99a'], marcado:['target-arrows','#ff6a58'], cego:['sight-disabled','#b4b4b4'],
  fortalecido:['biceps','#ffb347'], protegido:['shield','#79a8ec'], escudo:['magic-shield','#cfe0ff'],
  regeneracao:['regeneration','#6cc35e'], veloz:['winged-leg','#7fe0d0'], foco:['bullseye','#f3e08a'],
  inabalavel:['rock','#e9b949'], furtivo:['hidden','#a8a8c8'], inspirado:['sparkles','#79c8ff'],
};
const out = path.join(__dirname, '..', 'assets', 'status');
fs.mkdirSync(out, { recursive: true });
(async () => {
  const b = await chromium.launch(), p = await b.newPage();
  await p.setContent('<canvas id=c width=48 height=48></canvas>');
  for (const [id, [icon, col]] of Object.entries(STATUS_ICONS)) {
    if (!SET[icon]) { console.error('faltando:', icon); process.exitCode = 1; continue; }
    const mk = fill => `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">${SET[icon].body.split('currentColor').join(fill)}</svg>`;
    const b64 = await p.evaluate(async ([dark, light, base]) => {
      const load = async s => { const i = new Image(); i.src = 'data:image/svg+xml;utf8,' + encodeURIComponent(s); await i.decode(); return i; };
      const [iD, iC] = await Promise.all([load(dark), load(base)]);
      const c = document.getElementById('c'), g = c.getContext('2d'); g.clearRect(0, 0, 48, 48); g.imageSmoothingEnabled = true;
      // contorno escuro: a silhueta escura deslocada em volta, depois o ícone colorido por cima
      for (const [dx, dy] of [[-2,0],[2,0],[0,-2],[0,2],[-1.5,-1.5],[1.5,-1.5],[-1.5,1.5],[1.5,1.5]]) g.drawImage(iD, 4 + dx, 4 + dy, 40, 40);
      g.drawImage(iC, 4, 4, 40, 40);
      // brilho em cima (degradê claro → cor) só onde o ícone existe
      g.globalCompositeOperation = 'source-atop';
      const gr = g.createLinearGradient(0, 4, 0, 44); gr.addColorStop(0, light); gr.addColorStop(0.55, 'rgba(255,255,255,0)');
      g.fillStyle = gr; g.fillRect(0, 0, 48, 48); g.globalCompositeOperation = 'source-over';
      return c.toDataURL('image/png').split(',')[1];
    }, [mk('#150d08'), 'rgba(255,255,255,0.55)', mk(col)]);
    fs.writeFileSync(path.join(out, id + '.png'), Buffer.from(b64, 'base64'));
  }
  await b.close(); console.log(Object.keys(STATUS_ICONS).length, 'ícones em', out);
})();
