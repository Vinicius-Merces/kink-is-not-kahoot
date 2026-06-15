// Registra o service worker para permitir instalar o KINK como app
// na tela inicial do Android/iOS (PWA).
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js').catch((err) => {
            console.warn('Falha ao registrar service worker:', err);
        });
    });
}
