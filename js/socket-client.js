// Cliente Socket.IO - KINK is not Kahoot
class SocketClient {
    constructor() {
        this.socket = null;
        this.connected = false;
        this.roomId = null;
        this.role = null; // 'host' ou 'player'
        this.playerId = null;
        this.eventHandlers = new Map();
    }

    connect() {
        // Conectar ao servidor
        this.socket = io({
            transports: ['websocket'],
            reconnection: true,
            reconnectionAttempts: 5,
            reconnectionDelay: 1000
        });

        this.socket.on('connect', () => {
            console.log('🔌 Conectado ao servidor Socket.IO');
            this.connected = true;
            this.emit('ready');
        });

        this.socket.on('disconnect', () => {
            console.log('🔌 Desconectado do servidor');
            this.connected = false;
        });

        // Registrar listeners dinâmicos
        this.socket.onAny((event, ...args) => {
            console.log(`📡 Evento recebido: ${event}`, args[0]);
            if (this.eventHandlers.has(event)) {
                this.eventHandlers.get(event).forEach(callback => callback(...args));
            }
        });
    }

    // Registrar listener para evento
    on(event, callback) {
        if (!this.eventHandlers.has(event)) {
            this.eventHandlers.set(event, []);
        }
        this.eventHandlers.get(event).push(callback);
    }

    // Remover listener
    off(event, callback) {
        if (this.eventHandlers.has(event)) {
            const handlers = this.eventHandlers.get(event);
            const index = handlers.indexOf(callback);
            if (index !== -1) handlers.splice(index, 1);
        }
    }

    // Emitir evento com callback
    emit(event, data, callback) {
        if (!this.socket) {
            console.error('Socket não conectado');
            return;
        }
        this.socket.emit(event, data, callback);
    }

    // Criar sala (host)
    createRoom(quizId, creatorName, callback) {
        this.emit('create-room', { quizId, creatorName }, (response) => {
            if (response.success) {
                this.roomId = response.roomId;
                this.role = 'host';
                console.log('🏠 Sala criada:', response.roomCode);
            }
            if (callback) callback(response);
        });
    }

    // Entrar em sala (player)
    joinRoom(roomCode, playerId, playerName, playerAvatar, callback) {
        this.emit('join-room', { roomCode, playerId, playerName, playerAvatar }, (response) => {
            if (response.success) {
                this.roomId = response.roomId;
                this.role = 'player';
                this.playerId = playerId;
                console.log('👤 Entrou na sala:', roomCode);
            }
            if (callback) callback(response);
        });
    }

    // Iniciar quiz (host)
    startQuiz(callback) {
        this.emit('start-quiz', {}, callback);
    }

    // Iniciar pergunta (host)
    startQuestion(callback) {
        this.emit('start-question', {}, callback);
    }

    // Responder pergunta (player)
    submitAnswer(answer, responseTime, callback) {
        this.emit('submit-answer', { answer, responseTime }, callback);
    }

    // Próxima pergunta (host)
    nextQuestion(callback) {
        this.emit('next-question', {}, callback);
    }

    // Finalizar jogo (host)
    endGame(callback) {
        this.emit('end-game', {}, callback);
    }

    // Desconectar
    disconnect() {
        if (this.socket) {
            this.socket.disconnect();
        }
    }
}

// Inicializar quando o DOM estiver pronto
let socketClient = null;

document.addEventListener('DOMContentLoaded', () => {
    socketClient = new SocketClient();
    socketClient.connect();
    window.socketClient = socketClient;
});