// Version Control - KINK is not Kahoot
class VersionManager {
    constructor() {
        this.currentVersion = localStorage.getItem('kink_version');
        this.checkInterval = null;
        this.init();
    }

    async init() {
        await this.checkVersion();
        // Verificar a cada 3 minutos
        this.checkInterval = setInterval(() => this.checkVersion(), 3 * 60 * 1000);
    }

    async checkVersion() {
        try {
            const response = await fetch('/version.json?t=' + Date.now(), {
                cache: 'no-store'
            });
            if (!response.ok) return;

            const data = await response.json();
            const latest = data.version;
            const stored = localStorage.getItem('kink_version');

            if (!stored) {
                localStorage.setItem('kink_version', latest);
                return;
            }

            if (stored !== latest) {
                console.log(`🔄 Nova versão: ${latest} (atual: ${stored})`);

                const deferred = localStorage.getItem('kink_update_deferred_version');
                const deferredAt = parseInt(localStorage.getItem('kink_update_deferred_at') || '0');
                const within24h = Date.now() - deferredAt < 24 * 60 * 60 * 1000;

                if (deferred === latest && within24h) {
                    console.log('⏰ Atualização adiada');
                    return;
                }

                this.showUpdateNotification(data);
            }
        } catch (e) {
            // Silencioso
        }
    }

    showUpdateNotification(versionData) {
        const existing = document.querySelector('.update-notification');
        if (existing) existing.remove();

        const notification = document.createElement('div');
        notification.className = 'update-notification';
        notification.innerHTML = `
            <div class="update-content">
                <span class="update-icon">🚀</span>
                <div class="update-text">
                    <strong>Atualização disponível</strong>
                    <small>v${versionData.version} — clique para aplicar</small>
                </div>
                <div class="update-actions">
                    <button class="update-now">Atualizar</button>
                    <button class="update-later">Depois</button>
                </div>
            </div>
        `;

        document.body.appendChild(notification);
        setTimeout(() => notification.classList.add('show'), 100);

        notification.querySelector('.update-now').addEventListener('click', () => {
            localStorage.setItem('kink_version', versionData.version);
            localStorage.removeItem('kink_update_deferred_version');
            localStorage.removeItem('kink_update_deferred_at');
            this.forceHardReload();
        });

        notification.querySelector('.update-later').addEventListener('click', () => {
            localStorage.setItem('kink_update_deferred_version', versionData.version);
            localStorage.setItem('kink_update_deferred_at', Date.now().toString());
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 400);
        });

        setTimeout(() => {
            if (notification.parentNode) {
                notification.classList.remove('show');
                setTimeout(() => notification.remove(), 400);
            }
        }, 20000);
    }

    forceHardReload() {
        if ('caches' in window) {
            caches.keys().then(keys => {
                keys.forEach(key => caches.delete(key));
            });
        }
        const url = new URL(window.location.href);
        url.searchParams.delete('v');
        url.searchParams.set('_bust', Date.now());
        window.location.replace(url.toString());
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.versionManager = new VersionManager();
});
