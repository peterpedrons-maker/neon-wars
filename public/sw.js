const CACHE_NAME = 'neon-wars-v2';

self.addEventListener('install', (event) => {
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET' || new URL(req.url).origin !== self.location.origin) return;

  const isDocument = req.mode === 'navigate' || req.headers.get('accept')?.includes('text/html');

  if (isDocument) {
    // Network-first for HTML documents: always serve the latest deploy
    // when online, so a new push is visible on next load instead of
    // being masked by a stale cached copy indefinitely. Falls back to
    // cache only when offline.
    event.respondWith(
      fetch(req)
        .then((res) => {
          if (res.ok) {
            const clone = res.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(req, clone));
          }
          return res;
        })
        .catch(() => caches.match(req))
    );
    return;
  }

  // Cache-first for everything else (hashed build assets, images, etc.)
  // — their filenames change when their content does, so a stale cache
  // entry isn't a concern, and this is what keeps the game playable
  // offline once it's been opened at least once.
  event.respondWith(
    caches.match(req).then((cached) => {
      if (cached) return cached;
      return fetch(req)
        .then((res) => {
          if (res.ok) {
            const clone = res.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(req, clone));
          }
          return res;
        })
        .catch(() => cached);
    })
  );
});
