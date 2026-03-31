// Version Control - KINK is not Kahoot
class VersionManager {
    constructor() {
        this.currentVersion = null;
        this.init();
    }

    async init() {
        this.currentVersion = localStorage.getItem('kink_version');
        await this.checkVersion();
        
        // Registrar Service Worker APÓS a página carregar
        if ('serviceWorker' in navigator && window.location.protocol === 'https:') {
            window.addEventListener('load', () => {
                navigator.serviceWorker.register('/sw.js')
                    .then(reg => console.log('✅ Service Worker registrado'))
                    .catch(err => console.log('❌ Service Worker falhou:', err));
            });
        }
    }

    async checkVersion() {
        try {
            const response = await fetch('/version.json?t=' + Date.now());
            const data = await response.json();

            if (!this.currentVersion || this.currentVersion !== data.version) {
                console.log(`🔄 Nova versão: ${data.version}`);
                localStorage.setItem('kink_version', data.version);
                
                // Notificar Service Worker
                if (navigator.serviceWorker.controller) {
                    navigator.serviceWorker.controller.postMessage({
                        type: 'NEW_VERSION',
                        version: data.version
                    });
                }
                
                this.showUpdateNotification(data);
            }
        } catch (error) {
            console.error('❌ Erro ao verificar versão:', error);
        }
    }

    showUpdateNotification(versionData) {
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
            localStorage.removeItem('kink_version');
            window.location.reload(true);
        });
        
        notification.querySelector('.update-later').addEventListener('click', () => {
            notification.remove();
        });
        
        setTimeout(() => {
            if (notification.parentNode) {
                notification.classList.remove('show');
                setTimeout(() => notification.remove(), 300);
            }
        }, 10000);
    }
}

// Inicializar
document.addEventListener('DOMContentLoaded', () => {
    window.versionManager = new VersionManager();
});