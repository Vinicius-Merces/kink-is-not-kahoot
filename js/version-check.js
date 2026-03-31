// Version Control - KINK is not Kahoot (Sem Service Worker)
class VersionManager {
    constructor() {
        this.currentVersion = null;
        this.latestVersion = null;
        this.init();
    }

    async init() {
        // Carregar versão do localStorage (corrigido)
        this.currentVersion = localStorage.getItem('kink_version');
        console.log(`📌 Versão atual armazenada: ${this.currentVersion || 'nenhuma'}`);
        await this.checkVersion();
        
        // Verificar periodicamente (a cada 5 minutos)
        setInterval(() => this.checkVersion(), 5 * 60 * 1000);
    }

    async checkVersion() {
        try {
            const response = await fetch('/version.json?t=' + Date.now());
            if (!response.ok) {
                console.warn('⚠️ Não foi possível verificar versão');
                return;
            }
            
            const data = await response.json();
            this.latestVersion = data.version;

            // CORREÇÃO: Comparar com a versão salva no localStorage
            const storedVersion = localStorage.getItem('kink_version');
            
            if (!storedVersion || storedVersion !== this.latestVersion) {
                console.log(`🔄 Nova versão detectada: ${this.latestVersion} (atual: ${storedVersion || 'nenhuma'})`);
                
                // Salvar a nova versão IMEDIATAMENTE para não mostrar novamente
                localStorage.setItem('kink_version', this.latestVersion);
                this.currentVersion = this.latestVersion;
                
                // Verificar se o usuário já adiou esta versão (por 24h)
                const deferred = localStorage.getItem('kink_update_deferred');
                const deferredVersion = localStorage.getItem('kink_update_deferred_version');
                
                if (deferred && deferredVersion === this.latestVersion) {
                    const deferTime = parseInt(deferred);
                    if (Date.now() - deferTime < 24 * 60 * 60 * 1000) {
                        console.log('⏰ Atualização adiada por 24h');
                        return;
                    }
                }
                
                this.showUpdateNotification(data);
            } else {
                console.log(`✅ Versão atual: ${this.currentVersion}`);
            }
        } catch (error) {
            console.error('❌ Erro ao verificar versão:', error);
        }
    }

    showUpdateNotification(versionData) {
        // Remover notificação existente se houver
        const existing = document.querySelector('.update-notification');
        if (existing) existing.remove();

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
                    <button class="update-now">Atualizar agora</button>
                    <button class="update-later">Agora não</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => notification.classList.add('show'), 100);
        
        notification.querySelector('.update-now').addEventListener('click', () => {
            this.forceHardReload();
        });
        
        notification.querySelector('.update-later').addEventListener('click', () => {
            notification.remove();
            localStorage.setItem('kink_update_deferred', Date.now().toString());
            localStorage.setItem('kink_update_deferred_version', versionData.version);
        });
        
        setTimeout(() => {
            if (notification.parentNode) {
                notification.classList.remove('show');
                setTimeout(() => notification.remove(), 300);
            }
        }, 15000);
    }

    forceHardReload() {
        console.log('🔄 Forçando recarga completa...');
        
        // Limpar apenas a deferência, manter a versão
        localStorage.removeItem('kink_update_deferred');
        localStorage.removeItem('kink_update_deferred_version');
        
        // Forçar recarga ignorando cache
        const url = new URL(window.location.href);
        url.searchParams.set('v', Date.now());
        window.location.href = url.toString();
    }
}

// Inicializar
document.addEventListener('DOMContentLoaded', () => {
    window.versionManager = new VersionManager();
});