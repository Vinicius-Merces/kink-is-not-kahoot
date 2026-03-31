// Service Worker - KINK is not Kahoot
const CACHE_NAME = 'kink-cache-v1';
const urlsToCache = [
    '/',
    '/index.html',
    '/host.html',
    '/player.html',
    '/create-quiz.html',
    '/my-quizzes.html',
    '/css/style.css',
    '/css/components.css',
    '/css/player.css',
    '/js/firebase-config.js',
    '/js/auth.js',
    '/js/utils.js',
    '/js/quiz-manager.js',
    '/js/create-quiz.js',
    '/js/socket-client.js',
    '/js/host-socket.js',
    '/js/player-socket.js',
    '/js/music-player.js'
];

// Instalação
self.addEventListener('install', event => {
    console.log('Service Worker instalando...');
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                console.log('Cache aberto');
                return cache.addAll(urlsToCache);
            })
    );
});

// Ativação
self.addEventListener('activate', event => {
    console.log('Service Worker ativado');
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cache => {
                    if (cache !== CACHE_NAME) {
                        console.log('Deletando cache antigo:', cache);
                        return caches.delete(cache);
                    }
                })
            );
        })
    );
});

// Interceptar requisições
self.addEventListener('fetch', event => {
    event.respondWith(
        caches.match(event.request)
            .then(response => {
                // Cache hit - retorna do cache
                if (response) {
                    return response;
                }

                // Clona a requisição
                const fetchRequest = event.request.clone();

                return fetch(fetchRequest).then(response => {
                    // Verifica se é uma resposta válida
                    if (!response || response.status !== 200 || response.type !== 'basic') {
                        return response;
                    }

                    // Clona a resposta
                    const responseToCache = response.clone();

                    caches.open(CACHE_NAME)
                        .then(cache => {
                            cache.put(event.request, responseToCache);
                        });

                    return response;
                });
            })
    );
});

// Mensagens do cliente
self.addEventListener('message', event => {
    if (event.data.type === 'NEW_VERSION') {
        console.log('Nova versão detectada:', event.data.version);
        // Forçar atualização do cache
        caches.delete(CACHE_NAME).then(() => {
            console.log('Cache limpo para nova versão');
        });
    }
});