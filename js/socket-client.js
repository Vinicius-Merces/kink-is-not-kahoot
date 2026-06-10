// Cliente Socket.IO - KINK is not Kahoot
class SocketClient {
    constructor() {
        this.socket = null;
        this.connected = false;
        this.roomId = null;
        this.role = null; // 'host' ou 'player'
        this.playerId = null;
        this.eventHandlers = new Map();
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.init();
    }

    init() {
        // Tentar conectar imediatamente
        this.connect();
    }

    connect() {
        // Configurar Socket.IO com opções de reconexão
        this.socket = io({
            transports: ['websocket', 'polling'],
            reconnection: true,
            reconnectionAttempts: this.maxReconnectAttempts,
            reconnectionDelay: 1000,
            reconnectionDelayMax: 5000,
            timeout: 20000
        });

        this.socket.on('connect', () => {
            console.log('🔌 Conectado ao servidor Socket.IO');
            this.connected = true;
            this.reconnectAttempts = 0;
            
            // Emitir evento de pronto
            this.emit('client-ready', { timestamp: Date.now() });
        });

        this.socket.on('connect_error', (error) => {
            console.error('❌ Erro de conexão Socket.IO:', error.message);
            this.connected = false;
        });

        this.socket.on('disconnect', (reason) => {
            console.log(`🔌 Desconectado do servidor: ${reason}`);
            this.connected = false;
        });

        this.socket.on('reconnect_attempt', (attempt) => {
            console.log(`🔄 Tentativa de reconexão ${attempt}/${this.maxReconnectAttempts}`);
            this.reconnectAttempts = attempt;
        });

        this.socket.on('reconnect', () => {
            console.log('✅ Reconectado ao servidor');
            this.connected = true;
        });

        this.socket.on('reconnect_failed', () => {
            console.error('❌ Falha na reconexão após várias tentativas');
            this.connected = false;
        });

        // Registrar listeners dinâmicos
        this.socket.onAny((event, ...args) => {
            // Log apenas para eventos não são heartbeat/ping
            if (!event.startsWith('ping') && !event.startsWith('pong')) {
                console.log(`📡 Evento recebido: ${event}`, args[0]);
            }
            if (this.eventHandlers.has(event)) {
                this.eventHandlers.get(event).forEach(callback => {
                    try {
                        callback(...args);
                    } catch (error) {
                        console.error(`❌ Erro no handler do evento ${event}:`, error);
                    }
                });
            }
        });
    }

    // Registrar listener para evento
    on(event, callback) {
        if (!this.eventHandlers.has(event)) {
            this.eventHandlers.set(event, []);
        }
        this.eventHandlers.get(event).push(callback);
        return this;
    }

    // Remover listener
    off(event, callback) {
        if (this.eventHandlers.has(event)) {
            const handlers = this.eventHandlers.get(event);
            if (callback) {
                const index = handlers.indexOf(callback);
                if (index !== -1) handlers.splice(index, 1);
            } else {
                this.eventHandlers.delete(event);
            }
        }
        return this;
    }

    // Remover todos os listeners
    removeAllListeners() {
        this.eventHandlers.clear();
        return this;
    }

    // Emitir evento com callback opcional
    emit(event, data, callback) {
        if (!this.socket) {
            console.error('❌ Socket não conectado');
            if (callback) callback({ success: false, error: 'Socket não conectado' });
            return;
        }
        
        if (!this.connected) {
            console.warn(`⚠️ Emitindo evento "${event}" enquanto desconectado`);
        }
        
        this.socket.emit(event, data, callback);
    }

    // ============================================
    // MÉTODOS DO HOST
    // ============================================

    // Criar sala (host)
    createRoom(quizId, creatorName, creatorId, callback) {
        console.log(`🏠 Criando sala: quiz=${quizId}, criador=${creatorName}`);
        this.emit('create-room', { quizId, creatorName, creatorId }, (response) => {
            if (response && response.success) {
                this.roomId = response.roomId;
                this.role = 'host';
                console.log('✅ Sala criada com sucesso!');
                console.log(`   Código: ${response.roomCode}`);
                console.log(`   RoomId: ${response.roomId}`);
            } else {
                console.error('❌ Erro ao criar sala:', response?.error);
            }
            if (callback) callback(response);
        });
    }

    // Obter estado da sala (host/player)
    getRoomState(roomId, callback) {
        console.log(`📊 Solicitando estado da sala: ${roomId}`);
        this.emit('get-room-state', { roomId }, (response) => {
            if (callback) callback(response);
        });
    }

    // ============================================
    // MÉTODOS DO PLAYER
    // ============================================

    // Verificar se sala existe (player)
    checkRoom(roomCode, callback) {
        this.emit('check-room', { roomCode }, (response) => {
            if (callback) callback(response);
        });
    }

    // Entrar em sala (player)
    joinRoom(roomCode, playerId, playerName, playerAvatar, callback) {
        console.log(`👤 Entrando na sala: ${roomCode} como ${playerName}`);
        this.emit('join-room', { roomCode, playerId, playerName, playerAvatar }, (response) => {
            if (response && response.success) {
                this.roomId = response.roomId;
                this.role = 'player';
                this.playerId = playerId;
                console.log('✅ Entrou na sala com sucesso!');
                console.log(`   Quiz: ${response.quiz?.title}`);
            } else {
                console.error('❌ Erro ao entrar na sala:', response?.error);
            }
            if (callback) callback(response);
        });
    }

    // ============================================
    // MÉTODOS DO JOGO (Host e Player)
    // ============================================

    // Iniciar quiz (host)
    startQuiz(callback) {
        console.log('🎮 Iniciando quiz...');
        this.emit('start-quiz', {}, (response) => {
            if (response && !response.success) {
                console.error('❌ Erro ao iniciar quiz:', response?.error);
            } else {
                console.log('✅ Quiz iniciado!');
            }
            if (callback) callback(response);
        });
    }

    // Iniciar pergunta (host)
    startQuestion(callback) {
        console.log('📢 Iniciando pergunta...');
        this.emit('start-question', {}, (response) => {
            if (callback) callback(response);
        });
    }

    // Responder pergunta (player)
    submitAnswer(answer, responseTime, callback) {
        console.log(`📝 Respondendo pergunta: opção ${answer} em ${responseTime.toFixed(2)}s`);
        this.emit('submit-answer', { answer, responseTime }, (response) => {
            if (callback) callback(response);
        });
    }

    // Próxima pergunta (host)
    nextQuestion(callback) {
        console.log('⏩ Avançando para próxima pergunta...');
        this.emit('next-question', {}, (response) => {
            if (callback) callback(response);
        });
    }

    // Finalizar jogo (host)
    endGame(callback) {
        console.log('🏁 Finalizando jogo...');
        this.emit('end-game', {}, (response) => {
            if (callback) callback(response);
        });
    }

    // ============================================
    // MÉTODOS DO SIMULADO AO VIVO (Modo Professor)
    // ============================================

    // Criar sala de simulado ao vivo (professor)
    createLiveSimuladoRoom(certId, level, numQuestions, creatorName, creatorId, callback) {
        console.log(`📝 Criando simulado ao vivo: ${certId}/${level} (${numQuestions} perguntas)`);
        this.emit('simulado:create-room', { certId, level, numQuestions, creatorName, creatorId }, (response) => {
            if (response && response.success) {
                this.roomId = response.roomId;
                this.role = 'host';
                console.log('✅ Sala de simulado criada!');
                console.log(`   Código: ${response.roomCode}`);
            } else {
                console.error('❌ Erro ao criar sala de simulado:', response?.error);
            }
            if (callback) callback(response);
        });
    }

    // Entrar em sala de simulado ao vivo (aluno)
    joinLiveSimuladoRoom(roomCode, playerId, playerName, playerAvatar, callback) {
        console.log(`👤 Entrando no simulado ao vivo: ${roomCode} como ${playerName}`);
        this.emit('simulado:join-room', { roomCode, playerId, playerName, playerAvatar }, (response) => {
            if (response && response.success) {
                this.roomId = response.roomId;
                this.role = 'player';
                this.playerId = playerId;
                console.log('✅ Entrou no simulado ao vivo com sucesso!');
            } else {
                console.error('❌ Erro ao entrar no simulado ao vivo:', response?.error);
            }
            if (callback) callback(response);
        });
    }

    // Iniciar sessão de votação (professor)
    startLiveSimuladoSession(callback) {
        console.log('🎮 Iniciando sessão de simulado ao vivo...');
        this.emit('simulado:start-session', {}, (response) => {
            if (callback) callback(response);
        });
    }

    // Avançar para a próxima pergunta (professor)
    advanceLiveSimulado(callback) {
        console.log('⏩ Avançando pergunta do simulado ao vivo...');
        this.emit('simulado:advance', {}, (response) => {
            if (callback) callback(response);
        });
    }

    // Repetir votação de uma pergunta já apresentada (professor)
    revoteLiveSimulado(index, callback) {
        console.log(`🔁 Repetindo votação da pergunta ${index + 1}...`);
        this.emit('simulado:revote', { index }, (response) => {
            if (callback) callback(response);
        });
    }

    // Revisar uma pergunta já apresentada, sem afetar os alunos (professor)
    gotoLiveSimuladoQuestion(index, callback) {
        this.emit('simulado:goto-question', { index }, (response) => {
            if (callback) callback(response);
        });
    }

    // Votar na pergunta atual (aluno)
    voteLiveSimulado(optionIndex, callback) {
        console.log(`🗳️ Votando na opção ${optionIndex}`);
        this.emit('simulado:vote', { optionIndex }, (response) => {
            if (callback) callback(response);
        });
    }

    // Encerrar sessão de simulado ao vivo (professor)
    endLiveSimuladoSession(callback) {
        console.log('🏁 Encerrando simulado ao vivo...');
        this.emit('simulado:end-session', {}, (response) => {
            if (callback) callback(response);
        });
    }

    // Desconectar
    disconnect() {
        if (this.socket) {
            console.log('🔌 Desconectando Socket.IO...');
            this.socket.disconnect();
        }
    }

    // Reconectar manualmente
    reconnect() {
        if (this.socket && !this.connected) {
            console.log('🔄 Tentando reconectar manualmente...');
            this.socket.connect();
        }
    }
}

// Inicializar quando o DOM estiver pronto
let socketClient = null;

document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Inicializando Socket Client...');
    socketClient = new SocketClient();
    window.socketClient = socketClient;
});

// Exportar para uso global (caso necessário)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SocketClient;
}