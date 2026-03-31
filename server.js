// KINK is not Kahoot - Servidor Node.js com Socket.IO
const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const cors = require('cors');
const path = require('path');

// Inicializar Firebase Admin (apenas para persistência final)
const admin = require('firebase-admin');
const serviceAccount = require('./serviceAccountKey.json'); // Você precisará baixar do Firebase Console

admin.initializeApp({
    credential: admin.credential.cert(serviceAccount)
});
const db = admin.firestore();

// Configuração do Express
const app = express();
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname))); // Servir arquivos estáticos

// Servidor HTTP + Socket.IO
const server = http.createServer(app);
const io = new Server(server, {
    cors: {
        origin: "*",
        methods: ["GET", "POST"]
    }
});

// ============================================
// GERENCIAMENTO DE SALAS (CONTAINERS)
// ============================================

// Estrutura de dados em memória
const activeRooms = new Map();      // roomId -> GameRoom
const roomCodeMap = new Map();      // code -> roomId

// Classe GameRoom (Container)
class GameRoom {
    constructor(roomId, code, quizData, creatorSocketId, creatorName) {
        this.id = roomId;
        this.code = code;
        this.quiz = quizData;
        this.creatorSocketId = creatorSocketId;
        this.creatorName = creatorName;
        this.players = new Map();           // socketId -> { id, name, avatar, score }
        this.status = 'waiting';             // waiting, reading, answering, finished
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
        console.log(`👤 Jogador ${playerData.name} entrou na sala ${this.code}`);
    }

    removePlayer(socketId) {
        const player = this.players.get(socketId);
        if (player) {
            this.players.delete(socketId);
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

    async startGame() {
        this.status = 'active';
        console.log(`🎮 Jogo iniciado na sala ${this.code}`);
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

        console.log(`📖 Fase de leitura - Pergunta ${questionIndex + 1}: ${this.currentQuestion.text.substring(0, 50)}...`);

        // Timer para leitura (5s)
        this.timers.reading = setTimeout(() => {
            this.startAnsweringPhase();
        }, 5000);

        return {
            success: true,
            question: {
                index: questionIndex,
                text: this.currentQuestion.text,
                timeLimit: this.currentQuestion.timeLimit || 30
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

        // Timer para finalizar pergunta
        this.timers.answering = setTimeout(() => {
            this.finishQuestion();
        }, timeLimit * 1000);

        // Emitir evento para todos da sala
        io.to(this.id).emit('answering-phase', {
            timeLimit: timeLimit,
            options: this.currentQuestion.options
        });
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

        return { success: true, points: points, isCorrect: isCorrect };
    }

    finishQuestion() {
        if (this.status !== 'answering') return;

        console.log(`🏁 Finalizando pergunta ${this.currentQuestionIndex + 1}`);

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
                points: answer.points,
                isCorrect: answer.isCorrect,
                totalScore: newScore
            });
        }

        // Gerar ranking
        const ranking = this.getRanking();

        // Emitir resultado para todos
        io.to(this.id).emit('question-result', {
            questionIndex: this.currentQuestionIndex,
            results: results,
            ranking: ranking,
            correctAnswer: this.currentQuestion.options[this.currentQuestion.correct]
        });

        this.status = 'active';

        return { ranking: ranking };
    }

    getRanking() {
        const ranking = [];
        for (const [playerId, score] of this.scores) {
            // Buscar nome do jogador
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
                score: score
            });
        }
        ranking.sort((a, b) => b.score - a.score);
        return ranking;
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
        console.log('Ranking final:', ranking);

        // Persistir resultados no Firestore
        try {
            const roomRef = db.collection('rooms').doc(this.id);
            await roomRef.set({
                code: this.code,
                quizId: this.quiz.id,
                quizTitle: this.quiz.title,
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
            });

            console.log(`✅ Resultados salvos no Firestore para sala ${this.id}`);
        } catch (error) {
            console.error('❌ Erro ao salvar resultados:', error);
        }

        io.to(this.id).emit('game-finished', { ranking: ranking });

        return { ranking: ranking };
    }
}

// ============================================
// EVENTOS SOCKET.IO
// ============================================

io.on('connection', (socket) => {
    console.log(`🔌 Cliente conectado: ${socket.id}`);

    // Criar nova sala
    socket.on('create-room', async (data, callback) => {
        try {
            const { quizId, creatorName } = data;
            
            // Buscar quiz no Firestore
            const quizDoc = await db.collection('quizzes').doc(quizId).get();
            if (!quizDoc.exists) {
                callback({ success: false, error: 'Quiz não encontrado' });
                return;
            }

            const quiz = { id: quizDoc.id, ...quizDoc.data() };
            const roomCode = generateRoomCode();
            const roomId = generateRoomId();

            const room = new GameRoom(roomId, roomCode, quiz, socket.id, creatorName);
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

            room.addPlayer(socket.id, {
                id: playerId,
                name: playerName,
                avatar: playerAvatar
            });

            // Notificar o host sobre novo jogador
            io.to(roomId).emit('player-joined', {
                players: room.getPlayersList(),
                totalPlayers: room.players.size
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

        await room.startGame();
        io.to(room.id).emit('quiz-started', {
            totalPlayers: room.players.size,
            totalQuestions: room.quiz.questions.length
        });

        callback({ success: true });
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
// INICIALIZAÇÃO
// ============================================

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
    console.log(`Servidor rodando na porta ${PORT}`);
});

server.listen(PORT, () => {
    console.log(`
    🔥 KINK is not Kahoot Server 🔥
    🚀 Servidor rodando na porta ${PORT}
    📡 WebSocket: ws://localhost:${PORT}
    🌐 Frontend: http://localhost:${PORT}
    `);
});