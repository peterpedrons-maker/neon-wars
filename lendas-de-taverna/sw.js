const CACHE = 'hearthblade-v4';
const CORE = ['./', './index.html', './manifest.json'];

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
  const isCore = req.mode === 'navigate' || CORE.some(p => req.url.endsWith(p.replace('./', '')));
  if (isCore) {
    e.respondWith(
      fetch(req, { cache: 'no-store' })
        .then(res => { if (res.ok) caches.open(CACHE).then(c => c.put(req, res.clone())); return res; })
        .catch(() => caches.match(req))
    );
    return;
  }

  // assets (sprites, fontes etc.) mudam pouco: cache-first com atualização
  // em segundo plano é seguro aqui e deixa a batalha mais rápida pra carregar.
  e.respondWith(
    caches.open(CACHE).then(async c => {
      const cached = await c.match(req);
      const fresh = fetch(req).then(res => { if (res.ok) c.put(req, res.clone()); return res; }).catch(() => cached);
      return cached || fresh;
    })
  );
});
