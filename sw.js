// Service Worker - KINK is not Kahoot
const CACHE_NAME = 'kink-cache-v2';

// ============================================
// URLs que NUNCA devem ser cacheadas
// ============================================
const NEVER_CACHE = [
    '/socket.io/',
    '/socket.io/socket.io.js',
    '/js/host-socket.js',
    '/js/player-socket.js',
    '/js/socket-client.js',
    '/js/version-check.js',
    '/version.json',
    'firestore.googleapis.com',
    'identitytoolkit.googleapis.com',
    'googleapis.com',
    'gstatic.com'
];

// ============================================
// URLs que podem ser cacheadas (estáticas)
// ============================================
const STATIC_CACHE = [
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
    '/js/music-player.js',
    '/assets/'
];

// ============================================
// Verificar se URL deve ser ignorada
// ============================================
function shouldNeverCache(url) {
    return NEVER_CACHE.some(pattern => url.includes(pattern));
}

// ============================================
// Instalação
// ============================================
self.addEventListener('install', event => {
    console.log('Service Worker instalando...');
    event.waitUntil(
        caches.open(CACHE_NAME).then(cache => {
            console.log('Cache aberto, adicionando arquivos estáticos...');
            return cache.addAll(STATIC_CACHE.filter(url => url !== '/'));
        }).catch(err => console.log('Erro ao adicionar cache:', err))
    );
    self.skipWaiting(); // Forçar ativação imediata
});

// ============================================
// Ativação - limpar caches antigos
// ============================================
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
    self.clients.claim(); // Tomar controle imediato
});

// ============================================
// Interceptar requisições
// ============================================
self.addEventListener('fetch', event => {
    const url = event.request.url;
    
    // Ignorar completamente requisições que não devem ser cacheadas
    if (shouldNeverCache(url)) {
        console.log('🔓 Ignorando cache para:', url.split('?')[0]);
        event.respondWith(fetch(event.request));
        return;
    }
    
    // Para requisições que podem ser cacheadas, tentar cache primeiro
    event.respondWith(
        caches.match(event.request).then(response => {
            if (response) {
                // Cache hit - retorna do cache
                console.log('📦 Cache hit:', url.split('?')[0]);
                return response;
            }
            
            // Cache miss - busca da rede
            console.log('🌐 Fetch:', url.split('?')[0]);
            return fetch(event.request).then(networkResponse => {
                // Verificar se é uma resposta válida
                if (!networkResponse || networkResponse.status !== 200) {
                    return networkResponse;
                }
                
                // Clonar para cache
                const responseToCache = networkResponse.clone();
                caches.open(CACHE_NAME).then(cache => {
                    cache.put(event.request, responseToCache);
                });
                
                return networkResponse;
            });
        })
    );
});

// ============================================
// Mensagens do cliente
// ============================================
self.addEventListener('message', event => {
    if (event.data.type === 'NEW_VERSION') {
        console.log('🔄 Nova versão detectada, limpando cache...');
        caches.delete(CACHE_NAME).then(() => {
            console.log('✅ Cache limpo');
        });
    }
});