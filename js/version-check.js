// Version Control - KINK is not Kahoot
class VersionManager {
    constructor() {
        this.currentVersion = null;
        this.init();
    }

    async init() {
        this.currentVersion = localStorage.getItem('kink_version');
        await this.checkVersion();
        setInterval(() => this.checkVersion(), 5 * 60 * 1000);
    }

    async checkVersion() {
        try {
            const response = await fetch('/version.json?t=' + Date.now());
            const data = await response.json();

            if (!this.currentVersion || this.currentVersion !== data.version) {
                console.log(`🔄 Nova versão: ${data.version}`);
                localStorage.setItem('kink_version', data.version);
                this.showUpdateNotification(data);
            }
        } catch (error) {
            console.error('Erro ao verificar versão:', error);
        }
    }

    showUpdateNotification(versionData) {
        // Verifica se o usuário já adiou esta versão
        const deferred = localStorage.getItem('kink_update_deferred');
        const deferredVersion = localStorage.getItem('kink_update_deferred_version');
        if (deferred && deferredVersion === versionData.version) {
            const deferTime = parseInt(deferred);
            if (Date.now() - deferTime < 24 * 60 * 60 * 1000) return;
        }

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
        setTimeout(() => notification.classList.add('show'), 100);

        notification.querySelector('.update-now').addEventListener('click', () => {
            this.forceReload();
        });
        notification.querySelector('.update-later').addEventListener('click', () => {
            notification.remove();
            localStorage.setItem('kink_update_deferred', Date.now().toString());
            localStorage.setItem('kink_update_deferred_version', versionData.version);
        });
    }

    forceReload() {
        // Limpa caches (opcional)
        if ('caches' in window) {
            caches.keys().then(names => {
                names.forEach(name => caches.delete(name));
            });
        }
        // Força reload ignorando cache
        window.location.reload(true);
    }
}

// Inicializar
document.addEventListener('DOMContentLoaded', () => {
    window.versionManager = new VersionManager();
});