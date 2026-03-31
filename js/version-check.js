// Version Control com Service Worker
class VersionManager {
    constructor() {
        this.currentVersion = null;
        this.swRegistered = false;
        this.init();
    }

    async init() {
        // Carregar versão do localStorage
        this.currentVersion = localStorage.getItem('kink_version');

        // Registrar Service Worker
        if ('serviceWorker' in navigator) {
            try {
                const registration = await navigator.serviceWorker.register('/sw.js');
                this.swRegistered = true;
                console.log('✅ Service Worker registrado');

                // Verificar atualizações do Service Worker
                registration.addEventListener('updatefound', () => {
                    const newWorker = registration.installing;
                    newWorker.addEventListener('statechange', () => {
                        if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                            this.showUpdateNotification();
                        }
                    });
                });
            } catch (error) {
                console.error('❌ Service Worker registration failed:', error);
            }
        }

        // Verificar versão
        await this.checkVersion();

        // Verificar periodicamente
        setInterval(() => this.checkVersion(), 5 * 60 * 1000);
    }

    async checkVersion() {
        try {
            const response = await fetch('/version.json?t=' + Date.now());
            const data = await response.json();

            if (!this.currentVersion || this.currentVersion !== data.version) {
                console.log(`🔄 Nova versão: ${data.version}`);

                // Salvar versão
                localStorage.setItem('kink_version', data.version);
                localStorage.setItem('kink_latest_version', data.version);
                localStorage.setItem('kink_last_changelog', JSON.stringify(data.changelog));

                // Notificar Service Worker
                if (this.swRegistered && navigator.serviceWorker.controller) {
                    navigator.serviceWorker.controller.postMessage({
                        type: 'NEW_VERSION',
                        version: data.version
                    });
                }

                this.showUpdateNotification(data);
            }
        } catch (error) {
            console.error('Erro ao verificar versão:', error);
        }
    }

    showUpdateNotification(versionData) {
        // Verificar se o usuário já adiou esta atualização
        const deferred = localStorage.getItem('kink_update_deferred');
        const deferredVersion = localStorage.getItem('kink_update_deferred_version');

        if (deferred && deferredVersion === versionData.version) {
            const deferTime = parseInt(deferred);
            if (Date.now() - deferTime < 24 * 60 * 60 * 1000) {
                return; // Não mostrar por 24h
            }
        }

        // Criar notificação
        const notification = document.createElement('div');
        notification.className = 'update-notification';
        notification.innerHTML = `
            <div class="update-content">
                <span class="update-icon">🚀</span>
                <div class="update-text">
                    <strong>Nova versão disponível!</strong>
                    <small>Versão ${versionData.version}</small>
                </div>
                <div class="update-actions">
                    <button class="update-now">Atualizar</button>
                    <button class="update-later">Agora não</button>
                </div>
            </div>
        `;

        document.body.appendChild(notification);

        // Animação de entrada
        setTimeout(() => notification.classList.add('show'), 100);

        // Botões
        notification.querySelector('.update-now').addEventListener('click', () => {
            this.forceReload();
        });

        notification.querySelector('.update-later').addEventListener('click', () => {
            notification.remove();
            localStorage.setItem('kink_update_deferred', Date.now().toString());
            localStorage.setItem('kink_update_deferred_version', versionData.version);
        });

        // Auto-fechar após 10 segundos
        setTimeout(() => {
            if (notification.parentNode) {
                notification.classList.remove('show');
                setTimeout(() => notification.remove(), 300);
            }
        }, 10000);
    }

    forceReload() {
        // Limpar cache
        if ('caches' in window) {
            caches.keys().then(names => {
                names.forEach(name => caches.delete(name));
            });
        }

        // Forçar reload
        window.location.reload(true);
    }
}

// Inicializar
document.addEventListener('DOMContentLoaded', () => {
    window.versionManager = new VersionManager();
});