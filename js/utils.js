// Utilitários Gerais - KINK is not Kahoot
class Utils {
    static formatTime(seconds) {
        return `${Math.floor(seconds)}s`;
    }
    
    static formatDate(timestamp) {
        if (!timestamp) return 'Data inválida';
        try {
            const date = timestamp.toDate ? timestamp.toDate() : new Date(timestamp);
            return date.toLocaleDateString('pt-BR');
        } catch (error) {
            console.error('Erro ao formatar data:', error);
            return 'Data inválida';
        }
    }
    
    static generateId() {
        return Date.now().toString(36) + Math.random().toString(36).substr(2, 8);
    }
    
    static shuffleArray(array) {
        const newArray = [...array];
        for (let i = newArray.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [newArray[i], newArray[j]] = [newArray[j], newArray[i]];
        }
        return newArray;
    }
    
    static showToast(message, type = 'info') {
        // Remover toasts antigos se houver muitos
        const existingToasts = document.querySelectorAll('.toast');
        if (existingToasts.length > 3) {
            existingToasts[0].remove();
        }
        
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        document.body.appendChild(toast);
        
        // Forçar reflow para animação
        toast.offsetHeight;
        
        setTimeout(() => toast.classList.add('show'), 10);
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => {
                if (toast.parentNode) toast.remove();
            }, 300);
        }, 3000);
    }
    
    static calculatePoints(timeRemaining, timeLimit, isCorrect) {
        if (!isCorrect) return 0;
        const percentage = Math.max(0, Math.min(1, timeRemaining / timeLimit));
        return Math.floor(1000 * percentage);
    }
    
    static getAvatarEmoji(avatarId) {
        const avatars = {
            'avatar1': '🐱',
            'avatar2': '🐶',
            'avatar3': '🦊',
            'avatar4': '🐼',
            'avatar5': '🐨',
            'avatar6': '🐸',
            'avatar7': '🐙',
            'avatar8': '🦄'
        };
        return avatars[avatarId] || '👤';
    }
    
    static getRandomAvatar() {
        const avatars = ['avatar1', 'avatar2', 'avatar3', 'avatar4', 'avatar5', 'avatar6', 'avatar7', 'avatar8'];
        return avatars[Math.floor(Math.random() * avatars.length)];
    }
    
    static escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    // Novos utilitários para facilitar o desenvolvimento
    static debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
    
    static throttle(func, limit) {
        let inThrottle;
        return function(...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }
    
    static copyToClipboard(text) {
        navigator.clipboard.writeText(text).then(() => {
            this.showToast('Copiado para a área de transferência!', 'success');
        }).catch(() => {
            this.showToast('Erro ao copiar', 'error');
        });
    }
    
    static getTimeRemaining(limit, startTime) {
        const elapsed = (Date.now() - startTime) / 1000;
        return Math.max(0, limit - elapsed);
    }
    
    static formatDuration(seconds) {
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    }
}

// Estilos do toast
if (!document.querySelector('#toast-styles')) {
    const toastStyles = document.createElement('style');
    toastStyles.id = 'toast-styles';
    toastStyles.textContent = `
        .toast {
            position: fixed;
            bottom: 20px;
            right: 20px;
            padding: 12px 20px;
            border-radius: 10px;
            background: rgba(0, 0, 0, 0.9);
            backdrop-filter: blur(10px);
            color: white;
            z-index: 10000;
            transform: translateX(400px);
            transition: transform 0.3s ease;
            font-size: 14px;
            font-family: 'Montserrat', sans-serif;
            pointer-events: none;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
            border-left: 4px solid;
        }
        .toast.show { transform: translateX(0); }
        .toast-success { background: rgba(72, 187, 120, 0.95); border-left-color: #38a169; }
        .toast-error { background: rgba(245, 101, 101, 0.95); border-left-color: #e53e3e; }
        .toast-warning { background: rgba(237, 137, 54, 0.95); border-left-color: #dd6b20; }
        .toast-info { background: rgba(66, 153, 225, 0.95); border-left-color: #3182ce; }
        
        @media (max-width: 768px) {
            .toast {
                bottom: 10px;
                right: 10px;
                left: 10px;
                transform: translateY(100px);
                text-align: center;
            }
            .toast.show { transform: translateY(0); }
        }
    `;
    document.head.appendChild(toastStyles);
}

// Exportar para uso global
window.Utils = Utils;