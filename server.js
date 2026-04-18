// KINK is not Kahoot - Servidor Node.js com Socket.IO
const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const path = require('path');
const cors = require('cors');

// Inicializar Firebase Admin (apenas para persistência final)
const admin = require('firebase-admin');

// Verificar se existe service account key (opcional, pode ser removido se não usar)
let db = null;
try {
    const serviceAccount = require('./serviceAccountKey.json');
    admin.initializeApp({
        credential: admin.credential.cert(serviceAccount)
    });
    db = admin.firestore();
    console.log('✅ Firebase Admin inicializado');
} catch (error) {
    console.log('⚠️ Firebase Admin não configurado (serviceAccountKey.json não encontrado)');
    console.log('   O jogo funcionará sem persistência no Firestore');
}

// Configuração do Express
const app = express();
const server = http.createServer(app);
const io = new Server(server, {
    cors: {
        origin: "*",
        methods: ["GET", "POST"]
    },
    transports: ['websocket', 'polling']
});

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname))); // Servir arquivos estáticos (HTML, CSS, JS)

// ============================================
// ROTAS HTTP
// ============================================

// Rota principal
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

// Rota para health check
app.get('/health', (req, res) => {
    res.json({
        status: 'online',
        timestamp: new Date().toISOString(),
        rooms: activeRooms.size,
        players: Array.from(activeRooms.values()).reduce((sum, room) => sum + room.players.size, 0)
    });
});

// ============================================
// GERENCIAMENTO DE SALAS (CONTAINERS)
// ============================================

// Estrutura de dados em memória
const activeRooms = new Map();      // roomId -> GameRoom
const roomCodeMap = new Map();      // code -> roomId
const playerSocketMap = new Map();   // playerId -> socketId

// Classe GameRoom (Container)
class GameRoom {
    constructor(roomId, code, quizData, creatorSocketId, creatorName, creatorId) {
        this.id = roomId;
        this.code = code;
        this.quiz = quizData;
        this.creatorSocketId = creatorSocketId;
        this.creatorId = creatorId;
        this.creatorName = creatorName;
        this.players = new Map();           // socketId -> { id, name, avatar, score }
        this.status = 'waiting';             // waiting, active, reading, answering, finished
        this.currentQuestionIndex = 0;
        this.currentQuestion = null;
        this.questionStartTime = null;
        this.answers = new Map();             // playerId -> { answer, responseTime, isCorrect, points }
        this.scores = new Map();              // playerId -> totalScore
        this.timers = {
            reading: null,
            answering: null
        };
        this.createdAt = Date.now();
    }

    addPlayer(socketId, playerData) {
        this.players.set(socketId, {
            id: playerData.id,
            name: playerData.name,
            avatar: playerData.avatar,
            score: 0,
            socketId: socketId
        });
        this.scores.set(playerData.id, 0);
        playerSocketMap.set(playerData.id, socketId);
        console.log(`👤 Jogador ${playerData.name} entrou na sala ${this.code}`);
        return this.getPlayersList();
    }

    removePlayer(socketId) {
        const player = this.players.get(socketId);
        if (player) {
            this.players.delete(socketId);
            playerSocketMap.delete(player.id);
            console.log(`👋 Jogador ${player.name} saiu da sala ${this.code}`);
            return player;
        }
        return null;
    }

    getPlayersList() {
        return Array.from(this.players.values()).map(p => ({
            id: p.id,
            name: p.name,
            avatar: p.avatar,
            score: p.score
        }));
    }

    getRanking() {
        const ranking = [];
        for (const [playerId, score] of this.scores) {
            let playerName = playerId;
            for (const [socketId, player] of this.players) {
                if (player.id === playerId) {
                    playerName = player.name;
                    break;
                }
            }
            ranking.push({
                playerId: playerId,
                playerName: playerName,
                score: score,
                avatar: this.players.get(this.getSocketIdByPlayerId(playerId))?.avatar || 'avatar1'
            });
        }
        ranking.sort((a, b) => b.score - a.score);
        return ranking;
    }

    // ✅ NOVO: Calcular estatísticas de respostas por opção
    getQuestionStatistics() {
        const stats = {};
        
        if (!this.currentQuestion || !this.currentQuestion.options) {
            return stats;
        }
        
        // Criar entrada para cada opção
        this.currentQuestion.options.forEach((option, index) => {
            const optionLabel = String.fromCharCode(65 + index); // A, B, C, D...
            stats[optionLabel] = {
                label: option,
                count: 0,
                percentage: 0,
                isCorrect: this.currentQuestion.correct === optionLabel || this.currentQuestion.correct === index
            };
        });
        
        // Contar quantos escolheram cada opção
        console.log(`📊 Contando respostas. Total de respostas: ${this.answers.size}`);
        for (const [playerId, answerData] of this.answers) {
            const answer = answerData.answer;
            console.log(`  - Jogador ${playerId} respondeu: ${answer} (tipo: ${typeof answer})`);
            
            // Converter número para letra se necessário
            let answerKey = answer;
            if (typeof answer === 'number') {
                answerKey = String.fromCharCode(65 + answer); // 0 -> A, 1 -> B, etc
            }
            
            if (stats[answerKey]) {
                stats[answerKey].count++;
                console.log(`    ✅ Contabilizado: ${answerKey} agora tem ${stats[answerKey].count}`);
            } else {
                console.log(`    ❌ Chave inválida: ${answerKey}`);
            }
        }
        
        // Calcular percentual
        const totalAnswers = this.answers.size;
        if (totalAnswers > 0) {
            Object.keys(stats).forEach(option => {
                stats[option].percentage = Math.round(
                    (stats[option].count / totalAnswers) * 100
                );
            });
        }
        
        console.log(`📊 Stats finais:`, stats);
        return stats;
    }

    // ✅ NOVO: Obter feedback para um aluno específico
    getAnswerFeedback(playerId) {
        const answer = this.answers.get(playerId);
        if (!answer) return null;
        
        return {
            isCorrect: answer.isCorrect,
            points: answer.points,
            yourAnswer: answer.answer,
            correctAnswer: this.currentQuestion.correct,
            explanation: this.currentQuestion.explanation || '',
            responseTime: answer.responseTime
        };
    }

    getSocketIdByPlayerId(playerId) {
        for (const [socketId, player] of this.players) {
            if (player.id === playerId) return socketId;
        }
        return null;
    }

    async startGame() {
        if (this.status !== 'waiting') return { success: false, error: 'Jogo já iniciado' };
        
        this.status = 'active';
        console.log(`🎮 Jogo iniciado na sala ${this.code}`);
        
        // Notificar todos os jogadores
        io.to(this.id).emit('quiz-started', {
            totalPlayers: this.players.size,
            totalQuestions: this.quiz.questions.length
        });
        
        return { success: true };
    }

    async startQuestion(questionIndex) {
        if (questionIndex >= this.quiz.questions.length) {
            await this.endGame();
            return { finished: true };
        }

        this.currentQuestionIndex = questionIndex;
        this.currentQuestion = this.quiz.questions[questionIndex];
        this.answers.clear();
        this.status = 'reading';

        const timeLimit = this.currentQuestion.timeLimit || 30;

        console.log(`📖 Fase de leitura - Pergunta ${questionIndex + 1}: ${this.currentQuestion.text.substring(0, 50)}...`);

        // Enviar fase de leitura para todos
        io.to(this.id).emit('reading-phase', {
            question: {
                index: questionIndex,
                text: this.currentQuestion.text,
                timeLimit: timeLimit
            },
            readingTime: 5
        });

        // Timer para leitura (5s)
        this.timers.reading = setTimeout(() => {
            this.startAnsweringPhase();
        }, 5000);

        return {
            success: true,
            question: {
                index: questionIndex,
                text: this.currentQuestion.text,
                timeLimit: timeLimit
            },
            readingTime: 5
        };
    }

    startAnsweringPhase() {
        if (this.status !== 'reading') return;

        this.status = 'answering';
        this.questionStartTime = Date.now();
        const timeLimit = this.currentQuestion.timeLimit || 30;

        console.log(`⚡ Fase de respostas - ${timeLimit}s para responder`);

        // Enviar fase de respostas para todos
        io.to(this.id).emit('answering-phase', {
            timeLimit: timeLimit,
            options: this.currentQuestion.options
        });

        // Timer para finalizar pergunta
        this.timers.answering = setTimeout(() => {
            this.finishQuestion();
        }, timeLimit * 1000);
    }

    submitAnswer(playerId, answer, responseTime) {
        if (this.status !== 'answering') {
            return { success: false, error: 'Não é hora de responder' };
        }

        if (this.answers.has(playerId)) {
            return { success: false, error: 'Você já respondeu' };
        }

        const isCorrect = (answer === this.currentQuestion.correct);
        let points = 0;

        if (isCorrect) {
            const timeLimit = this.currentQuestion.timeLimit || 30;
            const timeRemaining = Math.max(0, timeLimit - responseTime);
            points = Math.floor(1000 * (timeRemaining / timeLimit));
            points = Math.min(1000, Math.max(0, points));
        }

        this.answers.set(playerId, {
            answer: answer,
            responseTime: responseTime,
            isCorrect: isCorrect,
            points: points
        });

        console.log(`📝 ${playerId} respondeu: ${isCorrect ? '✅ Acertou' : '❌ Errou'} (${responseTime.toFixed(1)}s) - ${points}pts`);

        // Verificar se todos já responderam
        if (this.answers.size === this.players.size && this.players.size > 0) {
            console.log(`🎉 Todos os ${this.players.size} jogadores responderam!`);
            if (this.timers.answering) {
                clearTimeout(this.timers.answering);
                this.finishQuestion();
            }
        }

        // ✅ NOVO: Retornar feedback completo
        return { 
            success: true, 
            points: points, 
            isCorrect: isCorrect,
            yourAnswer: answer,
            correctAnswer: this.currentQuestion.correct,
            explanation: this.currentQuestion.explanation || ''
        };
    }

    finishQuestion() {
        if (this.status !== 'answering') return;

        console.log(`🏁 Finalizando pergunta ${this.currentQuestionIndex + 1}`);

        // Limpar timers
        if (this.timers.reading) clearTimeout(this.timers.reading);
        if (this.timers.answering) clearTimeout(this.timers.answering);

        // Calcular pontuações
        const results = [];
        for (const [playerId, answer] of this.answers) {
            const currentScore = this.scores.get(playerId) || 0;
            const newScore = currentScore + answer.points;
            this.scores.set(playerId, newScore);

            // Atualizar no objeto player também
            for (const [socketId, player] of this.players) {
                if (player.id === playerId) {
                    player.score = newScore;
                    break;
                }
            }

            results.push({
                playerId: playerId,
                answer: answer.answer,           // ← IMPORTANTE: para a distribuição de respostas
                points: answer.points,
                isCorrect: answer.isCorrect,
                totalScore: newScore
            });
        }

        // Para jogadores que não responderam
        for (const [socketId, player] of this.players) {
            if (!this.answers.has(player.id)) {
                results.push({
                    playerId: player.id,
                    answer: null,
                    points: 0,
                    isCorrect: false,
                    totalScore: this.scores.get(player.id) || 0
                });
            }
        }

        // Gerar ranking
        const ranking = this.getRanking();
        
        // ✅ NOVO: Obter estatísticas de resposta
        const questionStats = this.getQuestionStatistics();

        // Enviar resultado para todos
        io.to(this.id).emit('question-result', {
            questionIndex: this.currentQuestionIndex,
            results: results,
            ranking: ranking,
            correctAnswer: this.currentQuestion.correct,
            correctAnswerText: this.currentQuestion.options[this.currentQuestion.correct] || this.currentQuestion.correct,
            explanation: this.currentQuestion.explanation || '',
            stats: questionStats  // ✅ NOVO: Gráfico de respostas
        });

        // Enviar atualização do ranking
        io.to(this.id).emit('ranking-update', { ranking: ranking });

        this.status = 'active';

        return { ranking: ranking };
    }

    async nextQuestion() {
        if (this.timers.reading) clearTimeout(this.timers.reading);
        if (this.timers.answering) clearTimeout(this.timers.answering);

        const nextIndex = this.currentQuestionIndex + 1;

        if (nextIndex >= this.quiz.questions.length) {
            await this.endGame();
            return { finished: true };
        }

        return await this.startQuestion(nextIndex);
    }

    async endGame() {
        if (this.timers.reading) clearTimeout(this.timers.reading);
        if (this.timers.answering) clearTimeout(this.timers.answering);

        this.status = 'finished';
        const ranking = this.getRanking();

        console.log(`🏆 Jogo finalizado na sala ${this.code}`);
        console.log('Ranking final:', ranking.slice(0, 5));

        // Persistir resultados no Firestore (se disponível)
        if (db) {
            try {
                const roomRef = db.collection('rooms').doc(this.id);
                await roomRef.set({
                    code: this.code,
                    quizId: this.quiz.id,
                    quizTitle: this.quiz.title,
                    creatorId: this.creatorId,
                    creatorName: this.creatorName,
                    createdAt: admin.firestore.FieldValue.serverTimestamp(),
                    finishedAt: admin.firestore.FieldValue.serverTimestamp(),
                    players: Array.from(this.players.values()).map(p => ({
                        id: p.id,
                        name: p.name,
                        avatar: p.avatar,
                        score: p.score
                    })),
                    ranking: ranking,
                    totalPlayers: this.players.size
                }, { merge: true });
                console.log(`✅ Resultados salvos no Firestore para sala ${this.id}`);
            } catch (error) {
                console.error('❌ Erro ao salvar resultados:', error);
            }
        }

        io.to(this.id).emit('game-finished', { ranking: ranking });

        return { ranking: ranking };
    }

    getState() {
        return {
            id: this.id,
            code: this.code,
            quiz: {
                id: this.quiz.id,
                title: this.quiz.title,
                questions: this.quiz.questions
            },
            players: this.getPlayersList(),
            ranking: this.getRanking(),
            status: this.status,
            currentQuestionIndex: this.currentQuestionIndex
        };
    }
}

// ============================================
// UTILITÁRIOS
// ============================================

function generateRoomCode() {
    const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ0123456789';
    let code = '';
    for (let i = 0; i < 6; i++) {
        code += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return code;
}

function generateRoomId() {
    return Date.now().toString(36) + Math.random().toString(36).substr(2, 8);
}

// ============================================
// EVENTOS SOCKET.IO
// ============================================

io.on('connection', (socket) => {
    console.log(`🔌 Cliente conectado: ${socket.id}`);

    // Criar nova sala (professor)
    socket.on('create-room', async (data, callback) => {
        try {
            const { quizId, creatorName, creatorId } = data;
            
            if (!quizId) {
                callback({ success: false, error: 'Quiz ID não fornecido' });
                return;
            }

            // Buscar quiz no Firestore (se disponível)
            let quiz = null;
            if (db) {
                const quizDoc = await db.collection('quizzes').doc(quizId).get();
                if (quizDoc.exists) {
                    quiz = { id: quizDoc.id, ...quizDoc.data() };
                }
            }

            // Se não tiver Firestore ou quiz não encontrado, usar dados mock
            if (!quiz) {
                console.log('⚠️ Usando quiz mock para teste');
                quiz = {
                    id: quizId,
                    title: 'Quiz de Teste',
                    questions: [
                        {
                            text: 'Qual é o modelo de precificação da AWS que permite pagar pelos recursos conforme o uso?',
                            options: ['Pay-as-you-go', 'Reserved', 'Spot', 'Dedicated'],
                            correct: 0,
                            timeLimit: 30
                        }
                    ]
                };
            }

            const roomCode = generateRoomCode();
            const roomId = generateRoomId();

            const room = new GameRoom(roomId, roomCode, quiz, socket.id, creatorName, creatorId);
            activeRooms.set(roomId, room);
            roomCodeMap.set(roomCode, roomId);

            socket.join(roomId);
            socket.roomId = roomId;
            socket.role = 'host';

            console.log(`🏠 Sala criada: ${roomCode} (${roomId}) por ${creatorName}`);

            callback({
                success: true,
                roomId: roomId,
                roomCode: roomCode,
                quiz: {
                    id: quiz.id,
                    title: quiz.title,
                    questions: quiz.questions.length
                }
            });
        } catch (error) {
            console.error('Erro ao criar sala:', error);
            callback({ success: false, error: error.message });
        }
    });

    // Verificar se sala existe (aluno)
    socket.on('check-room', (data, callback) => {
        const { roomCode } = data;
        const roomId = roomCodeMap.get(roomCode);
        
        if (!roomId || !activeRooms.has(roomId)) {
            callback({ exists: false });
            return;
        }
        
        const room = activeRooms.get(roomId);
        callback({
            exists: true,
            roomId: roomId,
            quizTitle: room.quiz.title,
            totalQuestions: room.quiz.questions.length
        });
    });

    // Entrar em sala (aluno)
    socket.on('join-room', (data, callback) => {
        try {
            const { roomCode, playerId, playerName, playerAvatar } = data;
            const roomId = roomCodeMap.get(roomCode);

            if (!roomId || !activeRooms.has(roomId)) {
                callback({ success: false, error: 'Sala não encontrada' });
                return;
            }

            const room = activeRooms.get(roomId);
            
            if (room.status === 'finished') {
                callback({ success: false, error: 'Jogo já encerrado' });
                return;
            }

            socket.join(roomId);
            socket.roomId = roomId;
            socket.playerId = playerId;
            socket.role = 'player';

            const players = room.addPlayer(socket.id, {
                id: playerId,
                name: playerName,
                avatar: playerAvatar
            });

            // Notificar o host sobre novo jogador
            io.to(roomId).emit('player-joined', {
                players: players,
                totalPlayers: room.players.size,
                playerName: playerName
            });

            console.log(`👤 ${playerName} entrou na sala ${roomCode}`);

            callback({
                success: true,
                roomId: roomId,
                quiz: {
                    title: room.quiz.title,
                    totalQuestions: room.quiz.questions.length
                }
            });
        } catch (error) {
            console.error('Erro ao entrar na sala:', error);
            callback({ success: false, error: error.message });
        }
    });

    // Obter estado da sala
    socket.on('get-room-state', (data, callback) => {
        const room = activeRooms.get(data.roomId);
        if (!room) {
            callback({ success: false, error: 'Sala não encontrada' });
            return;
        }
        callback({ success: true, ...room.getState() });
    });

    // Iniciar quiz (host)
    socket.on('start-quiz', async (data, callback) => {
        const room = activeRooms.get(socket.roomId);
        if (!room) {
            callback({ success: false, error: 'Sala não encontrada' });
            return;
        }

        if (socket.role !== 'host') {
            callback({ success: false, error: 'Apenas o host pode iniciar o quiz' });
            return;
        }

        if (room.players.size === 0) {
            callback({ success: false, error: 'Não há jogadores na sala' });
            return;
        }

        const result = await room.startGame();
        callback(result);
    });

    // Iniciar pergunta (host)
    socket.on('start-question', async (data, callback) => {
        const room = activeRooms.get(socket.roomId);
        if (!room) {
            callback({ success: false, error: 'Sala não encontrada' });
            return;
        }

        if (socket.role !== 'host') {
            callback({ success: false, error: 'Apenas o host pode iniciar perguntas' });
            return;
        }

        const result = await room.startQuestion(room.currentQuestionIndex);
        callback(result);
    });

    // Responder pergunta (aluno)
    socket.on('submit-answer', (data, callback) => {
        const room = activeRooms.get(socket.roomId);
        if (!room) {
            callback({ success: false, error: 'Sala não encontrada' });
            return;
        }

        const { answer, responseTime } = data;
        const result = room.submitAnswer(socket.playerId, answer, responseTime);
        callback(result);
    });

    // Próxima pergunta (host)
    socket.on('next-question', async (data, callback) => {
        const room = activeRooms.get(socket.roomId);
        if (!room) {
            callback({ success: false, error: 'Sala não encontrada' });
            return;
        }

        if (socket.role !== 'host') {
            callback({ success: false, error: 'Apenas o host pode avançar' });
            return;
        }

        const result = await room.nextQuestion();
        callback(result);
    });

    // Finalizar jogo (host)
    socket.on('end-game', async (data, callback) => {
        const room = activeRooms.get(socket.roomId);
        if (!room) {
            callback({ success: false, error: 'Sala não encontrada' });
            return;
        }

        const result = await room.endGame();
        
        // Limpar sala após encerrar
        setTimeout(() => {
            activeRooms.delete(room.id);
            roomCodeMap.delete(room.code);
            console.log(`🗑️ Sala ${room.code} removida da memória`);
        }, 60000); // Remove após 1 minuto
        
        callback(result);
    });

    // Desconexão
    socket.on('disconnect', () => {
        console.log(`🔌 Cliente desconectado: ${socket.id}`);

        const room = activeRooms.get(socket.roomId);
        if (room) {
            if (socket.role === 'host') {
                // Host desconectou, encerrar sala
                console.log(`🏠 Host desconectou, encerrando sala ${room.code}`);
                room.endGame();
                activeRooms.delete(room.id);
                roomCodeMap.delete(room.code);
            } else {
                // Jogador desconectou
                const player = room.removePlayer(socket.id);
                if (player) {
                    io.to(room.id).emit('player-left', {
                        playerId: player.id,
                        players: room.getPlayersList(),
                        totalPlayers: room.players.size
                    });
                }
            }
        }
    });
});

// ============================================
// INICIALIZAÇÃO
// ============================================

const PORT = process.env.PORT || 80;

server.listen(PORT, '0.0.0.0', () => {
    console.log(`
    🔥 KINK is not Kahoot Server 🔥
    =================================
    🚀 Servidor rodando na porta ${PORT}
    📡 WebSocket: ws://localhost:${PORT}
    🌐 Frontend: http://localhost:${PORT}
    📁 Diretório: ${__dirname}
    =================================
    `);
});

// Graceful shutdown
process.on('SIGTERM', () => {
    console.log('🛑 Recebido SIGTERM, encerrando servidor...');
    server.close(() => {
        console.log('✅ Servidor encerrado');
        process.exit(0);
    });
});