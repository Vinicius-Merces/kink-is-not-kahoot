// KINK is not Kahoot - Servidor Node.js com Socket.IO
require('dotenv').config();

const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const path = require('path');
const fs = require('fs');
const cors = require('cors');
const rateLimit = require('express-rate-limit');

// Inicializar Firebase Admin (apenas para persistência final)
const { initializeApp, cert } = require('firebase-admin/app');
const { getFirestore, FieldValue } = require('firebase-admin/firestore');
const { getAuth } = require('firebase-admin/auth');

// Credenciais via variável de ambiente (produção) ou arquivo local (dev)
// FIREBASE_SERVICE_ACCOUNT_BASE64 é o formato recomendado: evita problemas
// de parsing em paineis que nao aceitam espacos/aspas em variaveis de ambiente.
let db = null;
let auth = null;
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
    initializeApp({
        credential: cert(serviceAccount)
    });
    db = getFirestore();
    auth = getAuth();
    console.log('✅ Firebase Admin inicializado');
} catch (error) {
    console.log('⚠️ Firebase Admin não configurado (defina FIREBASE_SERVICE_ACCOUNT_BASE64 ou crie serviceAccountKey.json)');
    console.log('   O jogo funcionará sem persistência no Firestore');
}

// E-mail do administrador: único usuário com acesso ao painel /admin.html e às rotas /api/admin/*
const ADMIN_EMAIL = 'vmerces24@gmail.com';

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

// 🔒 Bloqueia acesso via HTTP a arquivos internos do servidor (código-fonte, configs,
// credenciais e banco de questões com gabarito) que não fazem parte do frontend público.
const STATIC_BLOCKLIST = [
    /^\/server\.js$/i,
    /^\/package(-lock)?\.json$/i,
    /^\/update-version\.js$/i,
    /^\/squarecloud\.app$/i,
    /^\/serviceAccountKey\.json$/i,
    /^\/data(\/|$)/i,
    /^\/scripts(\/|$)/i,
    /^\/node_modules(\/|$)/i
];

app.use((req, res, next) => {
    if (STATIC_BLOCKLIST.some(pattern => pattern.test(req.path))) {
        return res.status(404).send('Not found');
    }
    next();
});

// 🔒 Rate limiting de rotas sensíveis (evita spam/abuso de endpoints da API)
const reportLimiter = rateLimit({
    windowMs: 10 * 60 * 1000, // 10 minutos
    max: 10,
    standardHeaders: true,
    legacyHeaders: false,
    message: { success: false, error: 'Muitos reports enviados. Tente novamente em alguns minutos.' }
});

const simuladoActionLimiter = rateLimit({
    windowMs: 15 * 60 * 1000, // 15 minutos
    max: 60,
    standardHeaders: true,
    legacyHeaders: false,
    message: { success: false, error: 'Muitas requisições. Tente novamente em alguns minutos.' }
});

const adminLimiter = rateLimit({
    windowMs: 5 * 60 * 1000, // 5 minutos
    max: 120,
    standardHeaders: true,
    legacyHeaders: false,
    message: { success: false, error: 'Muitas requisições. Tente novamente em alguns minutos.' }
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

// Persiste uma tentativa de simulado (solo ou ao vivo) no histórico do usuário
async function persistSimuladoAttempt(uid, attemptData) {
    let attemptId = null;
    try {
        if (db) {
            const docRef = await db.collection('users').doc(uid).collection('simuladoAttempts').add({
                ...attemptData,
                createdAt: FieldValue.serverTimestamp()
            });
            attemptId = docRef.id;
        } else {
            attemptId = generateSimuladoId();
            const userHistory = devSimuladoHistory.get(uid) || [];
            userHistory.unshift({ id: attemptId, ...attemptData, createdAt: new Date().toISOString() });
            devSimuladoHistory.set(uid, userHistory);
        }
    } catch (error) {
        console.error('⚠️ Erro ao salvar histórico do simulado:', error);
    }
    return attemptId;
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
        return await auth.verifyIdToken(token);
    } catch (error) {
        return null;
    }
}

// Verifica o ID token do Firebase enviado por eventos de Socket.IO (ex: criação de salas),
// para não confiar em creatorId/creatorName enviados livremente pelo cliente.
async function verifySocketIdToken(idToken) {
    if (!idToken || typeof idToken !== 'string') return null;

    // Sem Firebase Admin configurado (ambiente de desenvolvimento): aceita qualquer token presente
    if (!db) {
        return { uid: 'dev-user', email: 'dev@local', name: 'Usuário (dev)' };
    }

    try {
        return await auth.verifyIdToken(idToken);
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
app.post('/api/simulado/start', simuladoActionLimiter, async (req, res) => {
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
app.post('/api/simulado/:id/submit', simuladoActionLimiter, async (req, res) => {
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

    const attemptId = await persistSimuladoAttempt(user.uid, attemptData);

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
                    mode: data.mode || 'solo',
                    roomCode: data.roomCode || null,
                    participantsCount: data.participantsCount || null,
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
                    mode: data.mode || 'solo',
                    roomCode: data.roomCode || null,
                    participantsCount: data.participantsCount || null,
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

// Reports de questões com possível erro (não exige login - alunos do modo ao vivo não têm conta)
const devQuestionReports = []; // usado apenas quando Firebase Admin não está configurado

app.post('/api/simulado/report', reportLimiter, async (req, res) => {
    const { source, certCode, level, domain, questionId, questionIndex, questionText, options, message, reporterName } = req.body || {};

    if (!questionText || typeof questionText !== 'string' || !questionText.trim()) {
        return res.status(400).json({ success: false, error: 'Dados da pergunta inválidos' });
    }

    const user = await getAuthenticatedUser(req);

    const report = {
        source: typeof source === 'string' ? source.slice(0, 40) : 'unknown',
        certCode: typeof certCode === 'string' ? certCode.slice(0, 20) : null,
        level: typeof level === 'string' ? level.slice(0, 20) : null,
        domain: typeof domain === 'string' ? domain.slice(0, 100) : null,
        questionId: typeof questionId === 'string' ? questionId.slice(0, 100) : null,
        questionIndex: Number.isInteger(questionIndex) ? questionIndex : null,
        questionText: questionText.slice(0, 2000),
        options: Array.isArray(options) ? options.slice(0, 10).map(o => String(o).slice(0, 500)) : [],
        message: typeof message === 'string' ? message.slice(0, 1000) : '',
        reporterName: typeof reporterName === 'string' ? reporterName.slice(0, 80) : null,
        reporterUid: user ? user.uid : null,
        reporterEmail: user ? user.email : null,
        status: 'open'
    };

    try {
        if (db) {
            await db.collection('questionReports').add({
                ...report,
                createdAt: FieldValue.serverTimestamp()
            });
        } else {
            const id = `dev-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
            devQuestionReports.push({ id, ...report, createdAt: new Date().toISOString() });
            if (devQuestionReports.length > 200) devQuestionReports.shift();
        }
    } catch (error) {
        console.error('⚠️ Erro ao salvar report de questão:', error);
        return res.status(500).json({ success: false, error: 'Erro ao registrar o report' });
    }

    console.log(`🚩 Report de questão recebido (${report.source} / ${report.certCode || '?'} / ${report.level || '?'}): ${report.questionText.slice(0, 80)}`);

    res.json({ success: true });
});

// Verifica se a requisição pertence ao administrador (único e-mail definido em ADMIN_EMAIL)
async function requireAdmin(req, res) {
    const user = await getAuthenticatedUser(req);
    if (!user || (user.email || '').toLowerCase() !== ADMIN_EMAIL.toLowerCase()) {
        res.status(403).json({ success: false, error: 'Acesso restrito ao administrador' });
        return null;
    }
    return user;
}

// Lista os reports de questões com erro (painel admin)
app.get('/api/admin/reports', adminLimiter, async (req, res) => {
    if (!(await requireAdmin(req, res))) return;

    try {
        let reports;
        if (db) {
            const snapshot = await db.collection('questionReports').orderBy('createdAt', 'desc').limit(300).get();
            reports = snapshot.docs.map(doc => {
                const data = doc.data();
                return {
                    id: doc.id,
                    ...data,
                    createdAt: data.createdAt?.toDate ? data.createdAt.toDate().toISOString() : null
                };
            });
        } else {
            reports = devQuestionReports.slice().reverse();
        }
        res.json({ success: true, reports });
    } catch (error) {
        console.error('⚠️ Erro ao buscar reports:', error);
        res.status(500).json({ success: false, error: 'Erro ao buscar reports' });
    }
});

// Atualiza o status de um report (ex: marcar como resolvido)
app.patch('/api/admin/reports/:id', adminLimiter, async (req, res) => {
    if (!(await requireAdmin(req, res))) return;

    const { status } = req.body || {};
    if (status !== 'open' && status !== 'resolved') {
        return res.status(400).json({ success: false, error: 'Status inválido' });
    }

    try {
        if (db) {
            await db.collection('questionReports').doc(req.params.id).update({ status });
        } else {
            const report = devQuestionReports.find(r => r.id === req.params.id);
            if (!report) return res.status(404).json({ success: false, error: 'Report não encontrado' });
            report.status = status;
        }
        res.json({ success: true });
    } catch (error) {
        console.error('⚠️ Erro ao atualizar report:', error);
        res.status(500).json({ success: false, error: 'Erro ao atualizar report' });
    }
});

// Exclui permanentemente um report
app.delete('/api/admin/reports/:id', adminLimiter, async (req, res) => {
    if (!(await requireAdmin(req, res))) return;

    try {
        if (db) {
            await db.collection('questionReports').doc(req.params.id).delete();
        } else {
            const index = devQuestionReports.findIndex(r => r.id === req.params.id);
            if (index === -1) return res.status(404).json({ success: false, error: 'Report não encontrado' });
            devQuestionReports.splice(index, 1);
        }
        res.json({ success: true });
    } catch (error) {
        console.error('⚠️ Erro ao excluir report:', error);
        res.status(500).json({ success: false, error: 'Erro ao excluir report' });
    }
});

// ============================================
// GERENCIAMENTO DE SALAS (CONTAINERS)
// ============================================

// Estrutura de dados em memória
const activeRooms = new Map();      // roomId -> GameRoom
const roomCodeMap = new Map();      // code -> roomId
const playerSocketMap = new Map();   // playerId -> socketId

// Salas de Simulado Modo Professor (votação ao vivo)
const activeLiveSimulados = new Map(); // roomId -> LiveSimuladoRoom
const liveSimuladoCodeMap = new Map(); // code -> roomId

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
                    createdAt: FieldValue.serverTimestamp(),
                    finishedAt: FieldValue.serverTimestamp(),
                    players: Array.from(this.players.values()).map(p => ({
                        id: p.id, name: p.name, avatar: p.avatar, score: p.score
                    })),
                    ranking: ranking,
                    totalPlayers: this.players.size
                }, { merge: true });

                // ✅ CORRIGIDO: Incrementar timesPlayed individualmente por quiz
                await db.collection('quizzes').doc(this.quiz.id).update({
                    timesPlayed: FieldValue.increment(1),
                    lastPlayedAt: FieldValue.serverTimestamp()
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

// Classe LiveSimuladoRoom (Simulado Modo Professor - votação ao vivo)
class LiveSimuladoRoom {
    constructor(roomId, code, simuladoData, creatorSocketId, creatorName, creatorId) {
        this.id = roomId;
        this.code = code;
        this.certId = simuladoData.certId;
        this.certCode = simuladoData.certCode;
        this.certName = simuladoData.certName;
        this.level = simuladoData.level;
        this.domains = simuladoData.domains;
        this.questions = simuladoData.questions; // perguntas completas (com gabarito) - nunca enviadas aos alunos
        this.creatorSocketId = creatorSocketId;
        this.creatorId = creatorId;
        this.creatorName = creatorName;
        this.players = new Map();              // socketId -> { id, name, avatar, socketId }
        this.status = 'waiting';                 // waiting | voting | closed | finished
        this.currentQuestionIndex = -1;
        this.votes = new Map();                  // playerId -> optionIndex (pergunta atual)
        this.questionResults = new Map();        // questionIndex -> { voteCounts, percentages, totalVotes, winningOption, isCorrect }
        this.createdAt = Date.now();
    }

    addPlayer(socketId, playerData) {
        this.players.set(socketId, {
            id: playerData.id,
            name: playerData.name,
            avatar: playerData.avatar,
            socketId: socketId
        });
        playerSocketMap.set(playerData.id, socketId);
        return this.getPlayersList();
    }

    removePlayer(socketId) {
        const player = this.players.get(socketId);
        if (player) {
            this.players.delete(socketId);
            playerSocketMap.delete(player.id);
            this.votes.delete(player.id);
            return player;
        }
        return null;
    }

    getPlayersList() {
        return Array.from(this.players.values()).map(p => ({ id: p.id, name: p.name, avatar: p.avatar }));
    }

    getCurrentQuestion() {
        return this.questions[this.currentQuestionIndex] || null;
    }

    getSanitizedQuestion(index) {
        const question = this.questions[index];
        if (!question) return null;
        return {
            index,
            total: this.questions.length,
            domain: question.domain,
            text: question.text,
            options: question.options
        };
    }

    // Abre uma pergunta para votação (zera os votos e o resultado anterior dela)
    openQuestion(index) {
        if (index < 0 || index >= this.questions.length) return null;

        this.currentQuestionIndex = index;
        this.votes.clear();
        this.questionResults.delete(index); // uma nova votação substitui o resultado anterior
        this.status = 'voting';

        const question = this.getSanitizedQuestion(index);
        io.to(this.id).emit('simulado:question', question);
        this.emitVoteProgress();
        this.emitTeacherUpdate();

        return question;
    }

    emitVoteProgress() {
        io.to(this.id).emit('simulado:vote-progress', {
            voted: this.votes.size,
            total: this.players.size
        });
    }

    // Registra o voto de um aluno; encerra a votação automaticamente quando todos já votaram
    castVote(playerId, optionIndex) {
        if (this.status !== 'voting') {
            return { success: false, error: 'A votação desta pergunta já foi encerrada' };
        }

        const question = this.getCurrentQuestion();
        const optionsCount = question?.options?.length || 0;
        if (!Number.isInteger(optionIndex) || optionIndex < 0 || optionIndex >= optionsCount) {
            return { success: false, error: 'Resposta inválida' };
        }

        this.votes.set(playerId, optionIndex);
        this.emitVoteProgress();

        if (this.players.size > 0 && this.votes.size >= this.players.size) {
            this.closeVoting();
        }

        return { success: true };
    }

    // Apura os votos da pergunta atual e define a resposta da turma
    closeVoting() {
        if (this.status !== 'voting') return this.questionResults.get(this.currentQuestionIndex) || null;

        const question = this.getCurrentQuestion();
        const voteCounts = new Array(question.options.length).fill(0);
        for (const optionIndex of this.votes.values()) {
            if (voteCounts[optionIndex] !== undefined) voteCounts[optionIndex]++;
        }

        const totalVotes = this.votes.size;
        let winningOption = 0;
        let maxVotes = -1;
        voteCounts.forEach((count, idx) => {
            if (count > maxVotes) {
                maxVotes = count;
                winningOption = idx;
            }
        });

        const percentages = voteCounts.map(count => totalVotes > 0 ? Math.round((count / totalVotes) * 100) : 0);

        const result = {
            voteCounts,
            percentages,
            totalVotes,
            winningOption: totalVotes > 0 ? winningOption : null,
            isCorrect: totalVotes > 0 && winningOption === question.correct
        };

        this.questionResults.set(this.currentQuestionIndex, result);
        this.status = 'closed';

        // Alunos veem apenas a distribuição de votos, sem indicar qual opção está correta
        io.to(this.id).emit('simulado:vote-closed', {
            index: this.currentQuestionIndex,
            percentages,
            totalVotes
        });

        this.emitTeacherUpdate();

        return result;
    }

    // Avança para a próxima pergunta (encerrando a votação atual se necessário)
    advance() {
        if (this.status === 'voting') this.closeVoting();

        const nextIndex = this.currentQuestionIndex + 1;
        if (nextIndex >= this.questions.length) {
            return { finished: true };
        }

        this.openQuestion(nextIndex);
        return { finished: false, index: nextIndex };
    }

    // Reabre uma pergunta já apresentada para uma nova votação (substitui o resultado anterior)
    revote(index) {
        if (index < 0 || index > this.currentQuestionIndex) {
            return { success: false, error: 'Pergunta inválida para repetir votação' };
        }
        this.openQuestion(index);
        return { success: true };
    }

    // Estado de uma pergunta para a tela do professor (revisão, sem afetar os alunos)
    getTeacherQuestionState(index) {
        const question = this.questions[index];
        if (!question) return null;

        const isCurrent = index === this.currentQuestionIndex;
        const result = this.questionResults.get(index) || null;

        return {
            index,
            total: this.questions.length,
            domain: question.domain,
            text: question.text,
            options: question.options,
            correct: question.correct,
            explanation: question.explanation || '',
            status: isCurrent ? this.status : (result ? 'closed' : 'pending'),
            votedCount: isCurrent ? this.votes.size : (result ? result.totalVotes : 0),
            totalPlayers: this.players.size,
            result
        };
    }

    emitTeacherUpdate() {
        io.to(this.creatorSocketId).emit('simulado:teacher-update', {
            ...this.getTeacherQuestionState(this.currentQuestionIndex),
            players: this.getPlayersList()
        });
    }

    // Encerra a sessão: calcula o desempenho da turma e registra no histórico do professor
    async endSession() {
        if (this.currentQuestionIndex === -1) {
            this.status = 'finished';
            io.to(this.id).emit('simulado:session-finished', {});
            return null;
        }

        if (this.status === 'voting') this.closeVoting();
        this.status = 'finished';

        const domainStats = new Map();
        for (const domain of this.domains) {
            domainStats.set(domain.id, { id: domain.id, name: domain.name, total: 0, correct: 0 });
        }

        let correctCount = 0;
        const review = this.questions.map((question, index) => {
            const result = this.questionResults.get(index) || null;
            const classAnswer = result ? result.winningOption : null;
            const isCorrect = result ? result.isCorrect : false;
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
                yourAnswer: classAnswer,
                isCorrect,
                explanation: question.explanation || '',
                voteCounts: result ? result.voteCounts : [],
                percentages: result ? result.percentages : [],
                totalVotes: result ? result.totalVotes : 0
            };
        });

        const totalQuestions = this.questions.length;
        const score = totalQuestions > 0 ? Math.round((correctCount / totalQuestions) * 100) : 0;

        const domainBreakdown = this.domains.map(domain => {
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

        const attemptData = {
            certId: this.certId,
            certCode: this.certCode,
            certName: this.certName,
            level: this.level,
            mode: 'live',
            roomCode: this.code,
            participantsCount: this.players.size,
            totalQuestions,
            correctCount,
            score,
            domainBreakdown,
            review
        };

        const attemptId = await persistSimuladoAttempt(this.creatorId, attemptData);

        const resultPayload = { attemptId, ...attemptData };

        io.to(this.id).emit('simulado:session-finished', {});
        io.to(this.creatorSocketId).emit('simulado:session-result', resultPayload);

        return resultPayload;
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

const VALID_AVATARS = ['avatar1', 'avatar2', 'avatar3', 'avatar4', 'avatar5', 'avatar6', 'avatar7', 'avatar8'];

// Valida e normaliza os dados enviados por um aluno ao entrar em uma sala (join-room / simulado:join-room)
function sanitizePlayerJoinData(data) {
    const { roomCode, playerId, playerName, playerAvatar } = data || {};

    if (typeof roomCode !== 'string' || !roomCode.trim()) return null;
    if (typeof playerId !== 'string' || !playerId.trim()) return null;

    const safeName = typeof playerName === 'string' && playerName.trim()
        ? playerName.trim().slice(0, 30)
        : 'Jogador';

    const safeAvatar = VALID_AVATARS.includes(playerAvatar) ? playerAvatar : 'avatar1';

    return {
        roomCode: roomCode.trim(),
        playerId: playerId.trim().slice(0, 64),
        playerName: safeName,
        playerAvatar: safeAvatar
    };
}

// Registra um handler de evento garantindo que "callback" seja sempre uma função
// e capturando erros (síncronos ou de promises) — um payload malformado (ex: evento
// emitido sem dados/callback por um cliente malicioso) não pode mais derrubar o servidor.
function safeOn(socket, event, handler) {
    socket.on(event, (data, callback) => {
        const safeCallback = typeof callback === 'function' ? callback : () => {};
        try {
            const result = handler(data, safeCallback);
            if (result && typeof result.catch === 'function') {
                result.catch((error) => {
                    console.error(`⚠️ Erro no evento "${event}":`, error);
                    safeCallback({ success: false, error: 'Erro interno do servidor' });
                });
            }
        } catch (error) {
            console.error(`⚠️ Erro no evento "${event}":`, error);
            safeCallback({ success: false, error: 'Erro interno do servidor' });
        }
    });
}

// ============================================
// EVENTOS SOCKET.IO
// ============================================

io.on('connection', (socket) => {
    console.log(`🔌 Cliente conectado: ${socket.id}`);

    // Criar nova sala (professor)
    safeOn(socket, 'create-room', async (data, callback) => {
        try {
            const { quizId, creatorName, idToken } = data || {};

            if (!quizId || typeof quizId !== 'string') {
                callback({ success: false, error: 'Quiz ID não fornecido' });
                return;
            }

            // creatorId nunca é aceito do cliente: usa o uid verificado pelo ID token (ou null se anônimo)
            const verifiedUser = await verifySocketIdToken(idToken);
            const creatorId = verifiedUser ? verifiedUser.uid : null;
            const safeCreatorName = typeof creatorName === 'string' && creatorName.trim()
                ? creatorName.slice(0, 100)
                : 'Anônimo';

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

            const room = new GameRoom(roomId, roomCode, quiz, socket.id, safeCreatorName, creatorId);
            activeRooms.set(roomId, room);
            roomCodeMap.set(roomCode, roomId);

            socket.join(roomId);
            socket.roomId = roomId;
            socket.role = 'host';

            console.log(`🏠 Sala criada: ${roomCode} (${roomId}) por ${safeCreatorName}`);

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
    safeOn(socket, 'check-room', (data, callback) => {
        const { roomCode } = data || {};

        const roomId = roomCodeMap.get(roomCode);
        if (roomId && activeRooms.has(roomId)) {
            const room = activeRooms.get(roomId);
            callback({
                exists: true,
                type: 'quiz',
                roomId: roomId,
                quizTitle: room.quiz.title,
                totalQuestions: room.quiz.questions.length
            });
            return;
        }

        const liveRoomId = liveSimuladoCodeMap.get(roomCode);
        if (liveRoomId && activeLiveSimulados.has(liveRoomId)) {
            const liveRoom = activeLiveSimulados.get(liveRoomId);
            callback({
                exists: true,
                type: 'simulado',
                roomId: liveRoomId,
                certCode: liveRoom.certCode,
                certName: liveRoom.certName,
                level: liveRoom.level,
                totalQuestions: liveRoom.questions.length
            });
            return;
        }

        callback({ exists: false });
    });

    // Entrar em sala (aluno)
    safeOn(socket, 'join-room', (data, callback) => {
        try {
            const joinData = sanitizePlayerJoinData(data);
            if (!joinData) {
                callback({ success: false, error: 'Dados inválidos' });
                return;
            }
            const { roomCode, playerId, playerName, playerAvatar } = joinData;
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
    safeOn(socket, 'get-room-state', (data, callback) => {
        const room = activeRooms.get((data || {}).roomId);
        if (!room) {
            callback({ success: false, error: 'Sala não encontrada' });
            return;
        }
        callback({ success: true, ...room.getState() });
    });

    // Iniciar quiz (host)
    safeOn(socket, 'start-quiz', async (data, callback) => {
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
    safeOn(socket, 'start-question', async (data, callback) => {
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
    safeOn(socket, 'submit-answer', (data, callback) => {
        const room = activeRooms.get(socket.roomId);
        if (!room) {
            callback({ success: false, error: 'Sala não encontrada' });
            return;
        }

        const { answer, responseTime } = data || {};
        const result = room.submitAnswer(socket.playerId, answer, responseTime);
        callback(result);
    });

    // Próxima pergunta (host)
    safeOn(socket, 'next-question', async (data, callback) => {
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
    safeOn(socket, 'end-game', async (data, callback) => {
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

    // ============================================
    // SIMULADO MODO PROFESSOR (votação ao vivo)
    // ============================================

    // Criar sala de simulado ao vivo (professor)
    safeOn(socket, 'simulado:create-room', async (data, callback) => {
        try {
            const { certId, level, numQuestions, creatorName, idToken } = data || {};

            // O resultado fica gravado no histórico do professor (users/{uid}/simuladoAttempts),
            // então creatorId precisa ser o uid verificado pelo ID token - nunca o valor enviado pelo cliente.
            const verifiedUser = await verifySocketIdToken(idToken);
            if (!verifiedUser) {
                callback({ success: false, error: 'Sessão expirada. Faça login novamente para criar uma sala de simulado.' });
                return;
            }
            const creatorId = verifiedUser.uid;
            const safeCreatorName = typeof creatorName === 'string' && creatorName.trim()
                ? creatorName.slice(0, 100)
                : (verifiedUser.name || verifiedUser.email || 'Professor');

            const cert = CERTIFICATIONS[certId];
            if (!cert || !cert.levels.includes(level)) {
                callback({ success: false, error: 'Certificação ou nível inválido' });
                return;
            }

            const pool = examPools.get(`${certId}:${level}`);
            if (!pool || pool.questions.length === 0) {
                callback({ success: false, error: 'Pool de perguntas não disponível para essa combinação' });
                return;
            }

            const requested = parseInt(numQuestions, 10);
            if (!Number.isInteger(requested) || requested < 1) {
                callback({ success: false, error: 'Número de perguntas inválido' });
                return;
            }

            const total = Math.min(requested, MAX_SIMULADO_QUESTIONS, pool.questions.length);
            const questions = sampleQuestionsByDomain(pool, total);

            const roomCode = generateRoomCode();
            const roomId = generateRoomId();

            const room = new LiveSimuladoRoom(roomId, roomCode, {
                certId,
                certCode: pool.certCode,
                certName: pool.certName,
                level,
                domains: pool.domains,
                questions
            }, socket.id, safeCreatorName, creatorId);

            activeLiveSimulados.set(roomId, room);
            liveSimuladoCodeMap.set(roomCode, roomId);

            socket.join(roomId);
            socket.roomId = roomId;
            socket.role = 'host';
            socket.simuladoMode = true;

            console.log(`📝 Sala de simulado ao vivo criada: ${roomCode} (${roomId}) por ${safeCreatorName}`);

            callback({
                success: true,
                roomId,
                roomCode,
                certCode: pool.certCode,
                certName: pool.certName,
                level,
                domains: pool.domains,
                totalQuestions: questions.length
            });
        } catch (error) {
            console.error('Erro ao criar sala de simulado:', error);
            callback({ success: false, error: error.message });
        }
    });

    // Entrar em sala de simulado ao vivo (aluno)
    safeOn(socket, 'simulado:join-room', (data, callback) => {
        try {
            const joinData = sanitizePlayerJoinData(data);
            if (!joinData) {
                callback({ success: false, error: 'Dados inválidos' });
                return;
            }
            const { roomCode, playerId, playerName, playerAvatar } = joinData;
            const roomId = liveSimuladoCodeMap.get(roomCode);

            if (!roomId || !activeLiveSimulados.has(roomId)) {
                callback({ success: false, error: 'Sala não encontrada' });
                return;
            }

            const room = activeLiveSimulados.get(roomId);

            if (room.status === 'finished') {
                callback({ success: false, error: 'Simulado já encerrado' });
                return;
            }

            socket.join(roomId);
            socket.roomId = roomId;
            socket.playerId = playerId;
            socket.role = 'player';
            socket.simuladoMode = true;

            room.addPlayer(socket.id, {
                id: playerId,
                name: playerName,
                avatar: playerAvatar
            });

            io.to(roomId).emit('simulado:player-joined', {
                players: room.getPlayersList(),
                totalPlayers: room.players.size,
                playerName
            });
            room.emitVoteProgress();
            room.emitTeacherUpdate();

            console.log(`👤 ${playerName} entrou na sala de simulado ${roomCode}`);

            callback({
                success: true,
                roomId,
                certCode: room.certCode,
                certName: room.certName,
                level: room.level,
                totalQuestions: room.questions.length
            });

            // Se a votação da pergunta atual já está aberta, envia direto para quem entrou agora
            if (room.status === 'voting') {
                socket.emit('simulado:question', room.getSanitizedQuestion(room.currentQuestionIndex));
            }
        } catch (error) {
            console.error('Erro ao entrar na sala de simulado:', error);
            callback({ success: false, error: error.message });
        }
    });

    // Iniciar sessão de simulado ao vivo (professor)
    safeOn(socket, 'simulado:start-session', (data, callback) => {
        const room = activeLiveSimulados.get(socket.roomId);
        if (!room) {
            callback({ success: false, error: 'Sala não encontrada' });
            return;
        }
        if (socket.role !== 'host') {
            callback({ success: false, error: 'Apenas o professor pode iniciar a sessão' });
            return;
        }
        if (room.status !== 'waiting') {
            callback({ success: false, error: 'Sessão já iniciada' });
            return;
        }
        if (room.players.size === 0) {
            callback({ success: false, error: 'Não há alunos na sala' });
            return;
        }

        room.openQuestion(0);
        callback({ success: true });
    });

    // Avançar para a próxima pergunta (professor)
    safeOn(socket, 'simulado:advance', (data, callback) => {
        const room = activeLiveSimulados.get(socket.roomId);
        if (!room) {
            callback({ success: false, error: 'Sala não encontrada' });
            return;
        }
        if (socket.role !== 'host') {
            callback({ success: false, error: 'Apenas o professor pode avançar' });
            return;
        }
        if (room.status === 'waiting' || room.status === 'finished') {
            callback({ success: false, error: 'Sessão não está em andamento' });
            return;
        }

        const result = room.advance();
        callback({ success: true, ...result });
    });

    // Repetir votação de uma pergunta já apresentada (professor)
    safeOn(socket, 'simulado:revote', (data, callback) => {
        const room = activeLiveSimulados.get(socket.roomId);
        if (!room) {
            callback({ success: false, error: 'Sala não encontrada' });
            return;
        }
        if (socket.role !== 'host') {
            callback({ success: false, error: 'Apenas o professor pode repetir a votação' });
            return;
        }

        const { index } = data || {};
        if (!Number.isInteger(index)) {
            callback({ success: false, error: 'Pergunta inválida para repetir votação' });
            return;
        }
        const result = room.revote(index);
        callback(result);
    });

    // Revisar uma pergunta já apresentada, sem alterar o que os alunos veem (professor)
    safeOn(socket, 'simulado:goto-question', (data, callback) => {
        const room = activeLiveSimulados.get(socket.roomId);
        if (!room) {
            callback({ success: false, error: 'Sala não encontrada' });
            return;
        }
        if (socket.role !== 'host') {
            callback({ success: false, error: 'Apenas o professor pode revisar perguntas' });
            return;
        }

        const { index } = data || {};
        if (!Number.isInteger(index)) {
            callback({ success: false, error: 'Pergunta inválida' });
            return;
        }
        const state = room.getTeacherQuestionState(index);
        if (!state) {
            callback({ success: false, error: 'Pergunta inválida' });
            return;
        }

        callback({ success: true, ...state, players: room.getPlayersList() });
    });

    // Registrar voto (aluno)
    safeOn(socket, 'simulado:vote', (data, callback) => {
        const room = activeLiveSimulados.get(socket.roomId);
        if (!room) {
            callback({ success: false, error: 'Sala não encontrada' });
            return;
        }
        if (socket.role !== 'player') {
            callback({ success: false, error: 'Apenas alunos podem votar' });
            return;
        }

        const { optionIndex } = data || {};
        const result = room.castVote(socket.playerId, optionIndex);
        callback(result);
    });

    // Encerrar sessão de simulado ao vivo (professor)
    safeOn(socket, 'simulado:end-session', async (data, callback) => {
        const room = activeLiveSimulados.get(socket.roomId);
        if (!room) {
            callback({ success: false, error: 'Sala não encontrada' });
            return;
        }
        if (socket.role !== 'host') {
            callback({ success: false, error: 'Apenas o professor pode encerrar a sessão' });
            return;
        }

        const result = await room.endSession();

        // Limpar sala após encerrar
        setTimeout(() => {
            for (const [, player] of room.players) {
                playerSocketMap.delete(player.id);
            }
            activeLiveSimulados.delete(room.id);
            liveSimuladoCodeMap.delete(room.code);
            console.log(`🗑️ Sala de simulado ${room.code} removida da memória`);
        }, 60000);

        callback({ success: true, result });
    });

    // Desconexão
    socket.on('disconnect', () => {
        if (socket.simuladoMode) {
            const liveRoom = activeLiveSimulados.get(socket.roomId);
            if (liveRoom) {
                if (socket.role === 'host') {
                    console.log(`📝 Professor desconectou, encerrando simulado ao vivo ${liveRoom.code}`);
                    liveRoom.endSession();
                    for (const [, player] of liveRoom.players) {
                        playerSocketMap.delete(player.id);
                    }
                    activeLiveSimulados.delete(liveRoom.id);
                    liveSimuladoCodeMap.delete(liveRoom.code);
                } else {
                    const player = liveRoom.removePlayer(socket.id);
                    if (player) {
                        io.to(liveRoom.id).emit('simulado:player-left', {
                            playerId: player.id,
                            players: liveRoom.getPlayersList(),
                            totalPlayers: liveRoom.players.size
                        });
                        liveRoom.emitVoteProgress();
                        liveRoom.emitTeacherUpdate();

                        // Evita que a pergunta fique travada esperando o voto de quem saiu
                        if (liveRoom.status === 'voting' && liveRoom.players.size > 0 && liveRoom.votes.size >= liveRoom.players.size) {
                            liveRoom.closeVoting();
                        }
                    }
                }
            }
            return;
        }

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