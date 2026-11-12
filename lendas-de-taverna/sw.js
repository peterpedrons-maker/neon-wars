const CACHE = 'hearthblade-v9';
const CORE = ['./', './index.html', './mmo/', './manifest.json'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(CORE)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET' || new URL(req.url).origin !== self.location.origin) return;

  // index.html (e qualquer navegação) é o arquivo único que carrega TODO o
  // código do jogo — servir uma cópia velha dele escondia correções já
  // publicadas (bug real: o jogo foi atualizado várias vezes e quem já
  // tinha instalado continuava vendo a versão de antes). Por isso o
  // documento principal é sempre buscado da rede primeiro; só cai pro
  // cache se estiver offline de verdade.
  // código (html/js) e dados (json): rede primeiro, MAS com limite de tempo — em rede ruim o jogo não pode ficar esperando
  // para sempre (era isso que travava o "Continuar"); passou do limite, usa a cópia guardada.
  const path = new URL(req.url).pathname;
  const isCode = req.mode === 'navigate' || /\.(html|js|json|css)$/.test(path) || CORE.some(p => req.url.endsWith(p.replace('./', '')));
  if (isCode) {
    e.respondWith((async () => {
      const cache = await caches.open(CACHE);
      const cached = await cache.match(req);
      const net = fetch(req, { cache: 'no-cache' }).then(res => { if (res.ok) cache.put(req, res.clone()); return res; });
      if (!cached) return net;
      return Promise.race([net.catch(() => cached), new Promise(r => setTimeout(() => r(cached), 3500))]);
    })());
    return;
  }

  // assets pesados (imagens, sons, fontes): cache primeiro (abre instantâneo, sem baixar de novo) e atualiza em segundo plano
  e.respondWith(
    caches.open(CACHE).then(async c => {
      const cached = await c.match(req);
      const fresh = fetch(req).then(res => { if (res.ok) c.put(req, res.clone()); return res; }).catch(() => cached);
      return cached || fresh;
    })
  );
});
