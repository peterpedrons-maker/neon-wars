/* Gera assets/ui-icons/*.png (silhuetas brancas pixeladas 32x32) a partir do pacote
   npm @iconify-json/game-icons (game-icons.net, CC BY 3.0).
   Uso: npm i @iconify-json/game-icons playwright && node tools/build_icons.cjs
   A lista de ícones vem de tools/icons.json (nome do ícone por uso). */
const fs = require('fs'), path = require('path');
const { chromium } = require('playwright');
const SET = require('@iconify-json/game-icons/icons.json').icons;
const names = [...new Set(Object.values(require('./icons.json')).flatMap(g => Object.values(g)))];
const out = path.join(__dirname, '..', 'assets', 'ui-icons');
fs.mkdirSync(out, { recursive: true });
(async () => {
  const b = await chromium.launch(), p = await b.newPage();
  await p.setContent('<canvas id=c width=32 height=32></canvas>');
  for (const n of names) {
    if (!SET[n]) { console.error('faltando:', n); process.exitCode = 1; continue; }
    const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">${SET[n].body.split('currentColor').join('#fff')}</svg>`;
    const b64 = await p.evaluate(async s => {
      const img = new Image(); img.src = 'data:image/svg+xml;utf8,' + encodeURIComponent(s); await img.decode();
      const c = document.getElementById('c'), g = c.getContext('2d'); g.clearRect(0, 0, 32, 32);
      g.imageSmoothingEnabled = true; g.drawImage(img, 0, 0, 32, 32);
      const d = g.getImageData(0, 0, 32, 32);
      for (let i = 0; i < d.data.length; i += 4) { d.data[i] = d.data[i + 1] = d.data[i + 2] = 255; d.data[i + 3] = d.data[i + 3] > 100 ? 255 : 0; }
      g.putImageData(d, 0, 0); return c.toDataURL('image/png').split(',')[1];
    }, svg);
    fs.writeFileSync(path.join(out, n + '.png'), Buffer.from(b64, 'base64'));
  }
  await b.close(); console.log(names.length, 'ícones em', out);
})();
