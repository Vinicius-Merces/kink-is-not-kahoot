// Service Worker - KINK is not Kahoot
const CACHE_NAME = 'kink-cache-v2'; // Aumente a versão do cache sempre que mudar
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
    '/js/music-player.js',
    // Novos arquivos Socket.IO (NÃO são cacheados - serão ignorados)
    // '/js/socket-client.js',
    // '/js/host-socket.js',
    // '/js/player-socket.js',
    // '/socket.io/socket.io.js' (dinâmico, não cachear)
];

// Lista de URLs que NÃO devem ser interceptadas pelo SW
const ignoreUrls = [
    '/socket.io/',
    '/js/socket-client.js',
    '/js/host-socket.js',
    '/js/player-socket.js',
    '/version.json',
    '/socket.io/socket.io.js'
];

// Instalação
self.addEventListener('install', event => {
    console.log('Service Worker instalando...');
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                console.log('Cache aberto, adicionando arquivos estáticos');
                return cache.addAll(urlsToCache);
            })
    );
});

// Ativação - limpa caches antigos
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
    const url = event.request.url;

    // Ignorar URLs que devem ser tratadas diretamente pelo servidor
    if (ignoreUrls.some(ignore => url.includes(ignore))) {
        console.log('SW ignorando requisição:', url);
        event.respondWith(fetch(event.request));
        return;
    }

    // Para outras requisições, tenta cache primeiro, depois rede
    event.respondWith(
        caches.match(event.request)
            .then(response => {
                if (response) {
                    // Retorna do cache
                    return response;
                }

                // Clona a requisição para fazer fetch
                const fetchRequest = event.request.clone();

                return fetch(fetchRequest).then(response => {
                    // Verifica se a resposta é válida
                    if (!response || response.status !== 200 || response.type !== 'basic') {
                        return response;
                    }

                    // Clona a resposta para cache
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
        console.log('Nova versão detectada, limpando cache...');
        // Limpa o cache para forçar atualização
        caches.delete(CACHE_NAME).then(() => {
            console.log('Cache limpo. Recarregue a página.');
        });
    }
});