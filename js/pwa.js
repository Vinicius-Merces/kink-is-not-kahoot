// Registra o service worker para permitir instalar o KINK como app
// na tela inicial do Android/iOS (PWA).
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js').catch((err) => {
            console.warn('Falha ao registrar service worker:', err);
        });
    });
}

// Banner de instalação ("Adicionar à tela inicial")
(function () {
    const DISMISS_KEY = 'kink-pwa-banner-dismissed';

    const isStandalone = window.matchMedia('(display-mode: standalone)').matches
        || window.navigator.standalone === true;

    if (isStandalone || sessionStorage.getItem(DISMISS_KEY)) return;

    function createBanner({ icon, title, text, actionLabel, onAction }) {
        const banner = document.createElement('div');
        banner.className = 'pwa-install-banner';
        banner.setAttribute('role', 'dialog');
        banner.setAttribute('aria-live', 'polite');

        const iconEl = document.createElement('div');
        iconEl.className = 'pwa-install-icon';
        iconEl.setAttribute('aria-hidden', 'true');
        iconEl.textContent = icon;
        banner.appendChild(iconEl);

        const textWrap = document.createElement('div');
        textWrap.className = 'pwa-install-text';

        const strong = document.createElement('strong');
        strong.textContent = title;
        textWrap.appendChild(strong);

        const p = document.createElement('p');
        p.textContent = text;
        textWrap.appendChild(p);

        banner.appendChild(textWrap);

        if (actionLabel && onAction) {
            const actionBtn = document.createElement('button');
            actionBtn.type = 'button';
            actionBtn.className = 'pwa-install-action';
            actionBtn.textContent = actionLabel;
            actionBtn.addEventListener('click', () => {
                onAction();
                banner.remove();
            });
            banner.appendChild(actionBtn);
        }

        const closeBtn = document.createElement('button');
        closeBtn.type = 'button';
        closeBtn.className = 'pwa-install-close';
        closeBtn.setAttribute('aria-label', 'Fechar');
        closeBtn.textContent = '✕';
        closeBtn.addEventListener('click', () => {
            sessionStorage.setItem(DISMISS_KEY, '1');
            banner.remove();
        });
        banner.appendChild(closeBtn);

        document.body.appendChild(banner);
        return banner;
    }

    // Android/Chrome desktop: usa o prompt nativo de instalação
    window.addEventListener('beforeinstallprompt', (event) => {
        event.preventDefault();
        createBanner({
            icon: '📲',
            title: 'Instale o KINK',
            text: 'Adicione à tela inicial para abrir como um app, com acesso rápido.',
            actionLabel: 'Instalar',
            onAction: () => event.prompt()
        });
    });

    // iOS Safari não dispara beforeinstallprompt - mostra instruções manuais
    const ua = window.navigator.userAgent;
    const isIos = /iphone|ipad|ipod/i.test(ua);
    const isOtherBrowser = /crios|fxios|edgios|opios/i.test(ua);

    if (isIos && !isOtherBrowser) {
        createBanner({
            icon: '📲',
            title: 'Instale o KINK',
            text: 'Toque em Compartilhar e depois em "Adicionar à Tela de Início".'
        });
    }
})();
