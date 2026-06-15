// Service worker mínimo: habilita o "Adicionar à tela inicial" no Android/iOS
// e dá uma sobrevida offline básica, sem interferir no Socket.io/APIs.
const CACHE_NAME = 'kink-cache-v1';

const PRECACHE_URLS = [
    '/',
    '/manifest.json',
    '/images/icons/icon-192.png',
    '/images/icons/icon-512.png'
];

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => cache.addAll(PRECACHE_URLS))
            .then(() => self.skipWaiting())
    );
});

self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys()
            .then((keys) => Promise.all(
                keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))
            ))
            .then(() => self.clients.claim())
    );
});

self.addEventListener('fetch', (event) => {
    const { request } = event;

    if (request.method !== 'GET' || new URL(request.url).origin !== self.location.origin) {
        return;
    }

    // Socket.io e chamadas de API seguem direto pra rede (tempo real, sem cache)
    if (request.url.includes('/socket.io/') || request.url.includes('/api/')) {
        return;
    }

    event.respondWith(
        fetch(request)
            .then((response) => {
                const responseClone = response.clone();
                caches.open(CACHE_NAME).then((cache) => cache.put(request, responseClone));
                return response;
            })
            .catch(() => caches.match(request))
    );
});
