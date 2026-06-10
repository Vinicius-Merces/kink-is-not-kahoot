// KINK is not Kahoot - Servidor Node.js com Socket.IO
require('dotenv').config();

const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const path = require('path');
const fs = require('fs');
const cors = require('cors');

// Inicializar Firebase Admin (apenas para persistência final)
const admin = require('firebase-admin');

// Credenciais via variável de ambiente (produção) ou arquivo local (dev)
// FIREBASE_SERVICE_ACCOUNT_BASE64 é o formato recomendado: evita problemas
// de parsing em paineis que nao aceitam espacos/aspas em variaveis de ambiente.
let db = null;
try {
    let serviceAccount;
    if (process.env.FIREBASE_SERVICE_ACCOUNT_BASE64) {
        const json = Buffer.from(process.env.FIREBASE_SERVICE_ACCOUNT_BASE64, 'base64').toString('utf-8');
        serviceAccount = JSON.parse(json);
    } else if (process.env.FIREBASE_SERVICE_ACCOUNT) {
        serviceAccount = JSON.parse(process.env.FIREBASE_SERVICE_ACCOUNT);
    } else {
        serviceAccount = require('./serviceAccountKey.json');
    }
    admin.initializeApp({
        credential: admin.credential.cert(serviceAccount)
    });
    db = admin.firestore();
    console.log('✅ Firebase Admin inicializado');
} catch (error) {
    console.log('⚠️ Firebase Admin não configurado (defina FIREBASE_SERVICE_ACCOUNT_BASE64 ou crie serviceAccountKey.json)');
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

// ✅ Cache busting: arquivos estáticos com cache controlado
// CSS e JS ficam sem cache, assets (imagens, sons) ficam em cache longo
app.use((req, res, next) => {
    const url = req.url;
    if (url.match(/\.(css|js)$/)) {
        res.setHeader('Cache-Control', 'no-cache, no-store, must-revalidate');
        res.setHeader('Pragma', 'no-cache');
        res.setHeader('Expires', '0');
    } else if (url.match(/\.(mp3|ogg|wav|png|jpg|jpeg|gif|svg|ico|woff|woff2)$/)) {
        res.setHeader('Cache-Control', 'public, max-age=604800'); // 7 dias para assets
    }
    next();
});

app.use(express.static(path.join(__dirname)));

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
// SIMULADOS AWS (módulo de provas práticas)
// ============================================

const CERTIFICATIONS = {
    'clf-c02': {
        code: 'CLF-C02',
        name: 'AWS Certified Cloud Practitioner',
        shortName: 'Cloud Practitioner',
        levels: ['iniciante', 'medio', 'avancado']
    },
    'saa-c03': {
        code: 'SAA-C03',
        name: 'AWS Certified Solutions Architect - Associate',
        shortName: 'Solutions Architect Associate',
        levels: ['iniciante', 'medio', 'avancado']
    },
    'dva-c02': {
        code: 'DVA-C02',
        name: 'AWS Certified Developer - Associate',
        shortName: 'Developer Associate',
        levels: ['iniciante', 'medio', 'avancado']
    }
};

const MAX_SIMULADO_QUESTIONS = 80;

// Carrega as pools de perguntas (cert x nível) em memória
const examPools = new Map(); // chave: "certId:level" -> { certCode, certName, level, domains, questions }

function loadExamPools() {
    for (const [certId, cert] of Object.entries(CERTIFICATIONS)) {
        for (const level of cert.levels) {
            const filePath = path.join(__dirname, 'data', 'exams', certId, `${level}.json`);
            try {
                const raw = fs.readFileSync(filePath, 'utf-8');
                const pool = JSON.parse(raw);
                examPools.set(`${certId}:${level}`, pool);
            } catch (error) {
                console.log(`⚠️ Pool de simulado não encontrada: ${certId}/${level} (${error.message})`);
            }
        }
    }
    console.log(`📚 ${examPools.size} pools de simulado carregadas`);
}

loadExamPools();

function shuffleArray(array) {
    const arr = [...array];
    for (let i = arr.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [arr[i], arr[j]] = [arr[j], arr[i]];
    }
    return arr;
}

// Seleciona `numQuestions` perguntas da pool respeitando a proporção de pesos dos domínios
function sampleQuestionsByDomain(pool, numQuestions) {
    const totalAvailable = pool.questions.length;
    const n = Math.min(numQuestions, totalAvailable);

    const byDomain = new Map();
    for (const domain of pool.domains) {
        byDomain.set(domain.id, shuffleArray(pool.questions.filter(q => q.domain === domain.id)));
    }

    // Alocação proporcional pelo método dos maiores restos
    const allocations = pool.domains.map(domain => {
        const raw = domain.weight * n;
        return { id: domain.id, weight: domain.weight, count: Math.floor(raw), remainder: raw - Math.floor(raw) };
    });

    let allocated = allocations.reduce((sum, a) => sum + a.count, 0);
    let remaining = n - allocated;

    const byRemainder = [...allocations].sort((a, b) => b.remainder - a.remainder);
    for (let i = 0; i < remaining; i++) {
        byRemainder[i % byRemainder.length].count++;
    }

    // Limita pela disponibilidade real de cada domínio e redistribui o excedente
    let leftover = 0;
    for (const alloc of allocations) {
        const available = byDomain.get(alloc.id).length;
        if (alloc.count > available) {
            leftover += alloc.count - available;
            alloc.count = available;
        }
    }

    while (leftover > 0) {
        const candidates = allocations
            .filter(a => byDomain.get(a.id).length > a.count)
            .sort((a, b) => b.weight - a.weight);
        if (candidates.length === 0) break;
        for (const candidate of candidates) {
            if (leftover === 0) break;
            candidate.count++;
            leftover--;
        }
    }

    const selected = [];
    for (const alloc of allocations) {
        selected.push(...byDomain.get(alloc.id).slice(0, alloc.count));
    }

    return shuffleArray(selected);
}

// Remove resposta correta e explicação antes de enviar ao cliente
function sanitizeQuestion(question) {
    return {
        id: question.id,
        domain: question.domain,
        text: question.text,
        options: question.options
    };
}

// Sessões de simulado em andamento (em memória)
const activeSimulados = new Map(); // simuladoId -> { userId, certId, level, certName, domains, questions, startedAt }

// Histórico de tentativas (apenas quando Firebase Admin não está configurado)
const devSimuladoHistory = new Map(); // uid -> [{ id, certId, certCode, certName, level, totalQuestions, correctCount, score, domainBreakdown, review, createdAt }]

const SIMULADO_TTL_MS = 2 * 60 * 60 * 1000; // 2 horas

function cleanupExpiredSimulados() {
    const now = Date.now();
    for (const [id, simulado] of activeSimulados) {
        if (now - simulado.startedAt > SIMULADO_TTL_MS) {
            activeSimulados.delete(id);
        }
    }
}

setInterval(cleanupExpiredSimulados, 30 * 60 * 1000);

function generateSimuladoId() {
    return 'sim_' + Date.now().toString(36) + Math.random().toString(36).substr(2, 8);
}

// Verifica o token de autenticação Firebase enviado no header Authorization: Bearer <token>
async function getAuthenticatedUser(req) {
    const authHeader = req.headers.authorization || '';
    const match = authHeader.match(/^Bearer (.+)$/);
    if (!match) return null;

    const token = match[1];

    // Sem Firebase Admin configurado (ambiente de desenvolvimento): aceita qualquer token presente
    if (!db) {
        return { uid: 'dev-user', email: 'dev@local', name: 'Usuário (dev)' };
    }

    try {
        return await admin.auth().verifyIdToken(token);
    } catch (error) {
        return null;
    }
}

// Lista certificações, níveis disponíveis, domínios e tamanho das pools
app.get('/api/simulado/certifications', (req, res) => {
    const certifications = Object.entries(CERTIFICATIONS).map(([id, cert]) => ({
        id,
        code: cert.code,
        name: cert.name,
        shortName: cert.shortName,
        levels: cert.levels.map(level => {
            const pool = examPools.get(`${id}:${level}`);
            return {
                id: level,
                totalQuestions: pool ? pool.questions.length : 0,
                domains: pool ? pool.domains : []
            };
        })
    }));

    res.json({ success: true, maxQuestions: MAX_SIMULADO_QUESTIONS, certifications });
});

// Inicia um simulado: seleciona perguntas respeitando a proporção de domínios e oculta gabaritos
app.post('/api/simulado/start', async (req, res) => {
    const user = await getAuthenticatedUser(req);
    if (!user) {
        return res.status(401).json({ success: false, error: 'Faça login para iniciar um simulado' });
    }

    const { certId, level, numQuestions } = req.body || {};

    const cert = CERTIFICATIONS[certId];
    if (!cert || !cert.levels.includes(level)) {
        return res.status(400).json({ success: false, error: 'Certificação ou nível inválido' });
    }

    const pool = examPools.get(`${certId}:${level}`);
    if (!pool || pool.questions.length === 0) {
        return res.status(404).json({ success: false, error: 'Pool de perguntas não disponível para essa combinação' });
    }

    const requested = parseInt(numQuestions, 10);
    if (!Number.isInteger(requested) || requested < 1) {
        return res.status(400).json({ success: false, error: 'Número de perguntas inválido' });
    }

    const total = Math.min(requested, MAX_SIMULADO_QUESTIONS, pool.questions.length);
    const questions = sampleQuestionsByDomain(pool, total);

    const simuladoId = generateSimuladoId();
    activeSimulados.set(simuladoId, {
        userId: user.uid,
        certId,
        level,
        certCode: pool.certCode,
        certName: pool.certName,
        domains: pool.domains,
        questions,
        startedAt: Date.now()
    });

    console.log(`📝 Simulado iniciado: ${simuladoId} (${pool.certCode} / ${level} / ${questions.length} perguntas) por ${user.uid}`);

    res.json({
        success: true,
        simuladoId,
        certCode: pool.certCode,
        certName: pool.certName,
        level,
        domains: pool.domains,
        totalQuestions: questions.length,
        questions: questions.map(sanitizeQuestion)
    });
});

// Corrige um simulado e devolve pontuação geral, por domínio e revisão completa
app.post('/api/simulado/:id/submit', async (req, res) => {
    const user = await getAuthenticatedUser(req);
    if (!user) {
        return res.status(401).json({ success: false, error: 'Faça login para enviar o simulado' });
    }

    const simulado = activeSimulados.get(req.params.id);
    if (!simulado) {
        return res.status(404).json({ success: false, error: 'Simulado não encontrado ou expirado' });
    }

    if (simulado.userId !== user.uid) {
        return res.status(403).json({ success: false, error: 'Esse simulado não pertence a este usuário' });
    }

    const answers = (req.body && req.body.answers) || {};

    let correctCount = 0;
    const domainStats = new Map();
    for (const domain of simulado.domains) {
        domainStats.set(domain.id, { id: domain.id, name: domain.name, total: 0, correct: 0 });
    }

    const review = simulado.questions.map(question => {
        const userAnswer = Object.prototype.hasOwnProperty.call(answers, question.id) ? answers[question.id] : null;
        const isCorrect = userAnswer === question.correct;
        if (isCorrect) correctCount++;

        const stats = domainStats.get(question.domain);
        if (stats) {
            stats.total++;
            if (isCorrect) stats.correct++;
        }

        return {
            id: question.id,
            domain: question.domain,
            text: question.text,
            options: question.options,
            correct: question.correct,
            yourAnswer: userAnswer,
            isCorrect,
            explanation: question.explanation || ''
        };
    });

    const totalQuestions = simulado.questions.length;
    const score = totalQuestions > 0 ? Math.round((correctCount / totalQuestions) * 100) : 0;

    const domainBreakdown = simulado.domains.map(domain => {
        const stats = domainStats.get(domain.id) || { total: 0, correct: 0 };
        return {
            id: domain.id,
            name: domain.name,
            weight: domain.weight,
            total: stats.total,
            correct: stats.correct,
            score: stats.total > 0 ? Math.round((stats.correct / stats.total) * 100) : 0
        };
    });

    activeSimulados.delete(req.params.id);

    // Persiste a tentativa no histórico do usuário
    const attemptData = {
        certId: simulado.certId,
        certCode: simulado.certCode,
        certName: simulado.certName,
        level: simulado.level,
        totalQuestions,
        correctCount,
        score,
        domainBreakdown,
        review
    };

    let attemptId = null;
    try {
        if (db) {
            const docRef = await db.collection('users').doc(user.uid).collection('simuladoAttempts').add({
                ...attemptData,
                createdAt: admin.firestore.FieldValue.serverTimestamp()
            });
            attemptId = docRef.id;
        } else {
            attemptId = generateSimuladoId();
            const userHistory = devSimuladoHistory.get(user.uid) || [];
            userHistory.unshift({ id: attemptId, ...attemptData, createdAt: new Date().toISOString() });
            devSimuladoHistory.set(user.uid, userHistory);
        }
    } catch (error) {
        console.error('⚠️ Erro ao salvar histórico do simulado:', error);
    }

    console.log(`✅ Simulado finalizado: ${req.params.id} - ${correctCount}/${totalQuestions} (${score}%) por ${user.uid}`);

    res.json({
        success: true,
        attemptId,
        certCode: simulado.certCode,
        certName: simulado.certName,
        level: simulado.level,
        totalQuestions,
        correctCount,
        score,
        domainBreakdown,
        review
    });
});

// Lista o histórico de simulados do usuário autenticado (resumo, mais recente primeiro)
app.get('/api/simulado/history', async (req, res) => {
    const user = await getAuthenticatedUser(req);
    if (!user) {
        return res.status(401).json({ success: false, error: 'Faça login para ver seu histórico' });
    }

    try {
        let attempts;
        if (db) {
            const snapshot = await db.collection('users').doc(user.uid).collection('simuladoAttempts')
                .orderBy('createdAt', 'desc')
                .get();
            attempts = snapshot.docs.map(doc => {
                const data = doc.data();
                return {
                    id: doc.id,
                    certId: data.certId,
                    certCode: data.certCode,
                    certName: data.certName,
                    level: data.level,
                    totalQuestions: data.totalQuestions,
                    correctCount: data.correctCount,
                    score: data.score,
                    createdAt: data.createdAt ? data.createdAt.toDate().toISOString() : null
                };
            });
        } else {
            const userHistory = devSimuladoHistory.get(user.uid) || [];
            attempts = userHistory.map(({ domainBreakdown, review, ...summary }) => summary);
        }

        res.json({ success: true, attempts });
    } catch (error) {
        console.error('⚠️ Erro ao buscar histórico de simulados:', error);
        res.status(500).json({ success: false, error: 'Erro ao buscar histórico' });
    }
});

// Retorna o detalhe completo (breakdown + revisão) de uma tentativa específica
app.get('/api/simulado/history/:attemptId', async (req, res) => {
    const user = await getAuthenticatedUser(req);
    if (!user) {
        return res.status(401).json({ success: false, error: 'Faça login para ver seu histórico' });
    }

    try {
        if (db) {
            const docRef = db.collection('users').doc(user.uid).collection('simuladoAttempts').doc(req.params.attemptId);
            const doc = await docRef.get();
            if (!doc.exists) {
                return res.status(404).json({ success: false, error: 'Tentativa não encontrada' });
            }
            const data = doc.data();
            return res.json({
                success: true,
                attempt: {
                    id: doc.id,
                    certId: data.certId,
                    certCode: data.certCode,
                    certName: data.certName,
                    level: data.level,
                    totalQuestions: data.totalQuestions,
                    correctCount: data.correctCount,
                    score: data.score,
                    domainBreakdown: data.domainBreakdown,
                    review: data.review,
                    createdAt: data.createdAt ? data.createdAt.toDate().toISOString() : null
                }
            });
        }

        const userHistory = devSimuladoHistory.get(user.uid) || [];
        const attempt = userHistory.find(a => a.id === req.params.attemptId);
        if (!attempt) {
            return res.status(404).json({ success: false, error: 'Tentativa não encontrada' });
        }
        res.json({ success: true, attempt });
    } catch (error) {
        console.error('⚠️ Erro ao buscar detalhe do simulado:', error);
        res.status(500).json({ success: false, error: 'Erro ao buscar detalhe da tentativa' });
    }
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

        // ✅ Validar formato da resposta e do tempo de resposta vindos do cliente
        const optionsCount = this.currentQuestion.options?.length || 0;
        const isValidAnswer = answer === null ||
            (Number.isInteger(answer) && answer >= 0 && answer < optionsCount);
        if (!isValidAnswer) {
            return { success: false, error: 'Resposta inválida' };
        }

        const timeLimit = this.currentQuestion.timeLimit || 30;
        const isValidResponseTime = typeof responseTime === 'number' && Number.isFinite(responseTime);
        const safeResponseTime = isValidResponseTime ? Math.max(0, responseTime) : timeLimit;

        const isCorrect = (answer === this.currentQuestion.correct);
        let points = 0;

        if (isCorrect) {
            const timeRemaining = Math.max(0, timeLimit - safeResponseTime);
            points = Math.floor(1000 * (timeRemaining / timeLimit));
            points = Math.min(1000, Math.max(0, points));
        }

        this.answers.set(playerId, {
            answer: answer,
            responseTime: safeResponseTime,
            isCorrect: isCorrect,
            points: points
        });

        console.log(`📝 ${playerId} respondeu: ${isCorrect ? '✅ Acertou' : '❌ Errou'} (${safeResponseTime.toFixed(1)}s) - ${points}pts`);

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

        if (db) {
            try {
                // Salvar sessão do jogo
                await db.collection('rooms').doc(this.id).set({
                    code: this.code,
                    quizId: this.quiz.id,
                    quizTitle: this.quiz.title,
                    creatorId: this.creatorId,
                    creatorName: this.creatorName,
                    createdAt: admin.firestore.FieldValue.serverTimestamp(),
                    finishedAt: admin.firestore.FieldValue.serverTimestamp(),
                    players: Array.from(this.players.values()).map(p => ({
                        id: p.id, name: p.name, avatar: p.avatar, score: p.score
                    })),
                    ranking: ranking,
                    totalPlayers: this.players.size
                }, { merge: true });

                // ✅ CORRIGIDO: Incrementar timesPlayed individualmente por quiz
                await db.collection('quizzes').doc(this.quiz.id).update({
                    timesPlayed: admin.firestore.FieldValue.increment(1),
                    lastPlayedAt: admin.firestore.FieldValue.serverTimestamp()
                });

                console.log(`✅ timesPlayed incrementado para quiz ${this.quiz.id}`);
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

        // ✅ Evitar reiniciar a pergunta enquanto leitura/resposta já está em andamento
        if (room.status !== 'active') {
            callback({ success: false, error: 'Pergunta já em andamento' });
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

        // ✅ Evitar avançar enquanto a pergunta atual ainda está em andamento
        if (room.status !== 'active') {
            callback({ success: false, error: 'Pergunta já em andamento' });
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
        const room = activeRooms.get(socket.roomId);
        if (room) {
            if (socket.role === 'host') {
                console.log(`🏠 Host desconectou, encerrando sala ${room.code}`);
                room.endGame();
                activeRooms.delete(room.id);
                roomCodeMap.delete(room.code);
                // ✅ CORRIGIDO: Limpar playerSocketMap dos jogadores da sala
                for (const [, player] of room.players) {
                    playerSocketMap.delete(player.id);
                }
            } else {
                const player = room.removePlayer(socket.id);
                if (player) {
                    // ✅ CORRIGIDO: Limpar entrada do playerSocketMap
                    playerSocketMap.delete(player.id);
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