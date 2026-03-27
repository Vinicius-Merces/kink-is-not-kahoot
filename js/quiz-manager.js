// Gerenciador de Quizzes - CRUD completo
class QuizManager {
    constructor() {
        this.currentUser = null;
        this.currentQuiz = null;
        this.questions = [];
        this.setupAuthListener();
    }

    setupAuthListener() {
        auth.onAuthStateChanged((user) => {
            this.currentUser = user;
            console.log('🔐 Auth state changed:', user ? user.displayName : 'null');
            if (user && window.location.pathname.includes('my-quizzes.html')) {
                console.log('📋 Usuário logado, carregando quizzes...');
                this.loadUserQuizzes();
            }
        });
    }

    async loadUserQuizzes() {
        if (!this.currentUser) {
            console.log('⚠️ Nenhum usuário logado');
            return [];
        }
        
        try {
            console.log('🔍 Buscando quizzes para UID:', this.currentUser.uid);
            const snapshot = await db.collection('quizzes')
                .where('creatorId', '==', this.currentUser.uid)
                .orderBy('createdAt', 'desc')
                .get();
            
            console.log('📊 Total de quizzes encontrados:', snapshot.size);
            
            const quizzes = [];
            snapshot.forEach(doc => {
                const data = doc.data();
                console.log('📄 Quiz carregado:', doc.id, '->', data.title);
                quizzes.push({ id: doc.id, ...data });
            });
            
            console.log('📦 Quizzes processados:', quizzes.length);
            this.renderQuizzesList(quizzes);
            this.updateStats(quizzes);
            return quizzes;
        } catch (error) {
            console.error('❌ Erro ao carregar quizzes:', error);
            console.error('Detalhes do erro:', error.code, error.message);
            Utils.showToast('Erro ao carregar quizzes: ' + error.message, 'error');
            
            // Mostrar mensagem de erro na tela
            const grid = document.getElementById('quizzesGrid');
            if (grid) {
                grid.innerHTML = `
                    <div class="empty-state" style="border-left: 4px solid #ff6b6b;">
                        <div class="empty-icon">⚠️</div>
                        <h3>Erro ao carregar quizzes</h3>
                        <p>${error.message}</p>
                        <button onclick="location.reload()" class="btn btn-primary" style="margin-top: 1rem;">
                            🔄 Tentar novamente
                        </button>
                    </div>
                `;
            }
            return [];
        }
    }

    renderQuizzesList(quizzes) {
        const grid = document.getElementById('quizzesGrid');
        if (!grid) {
            console.error('❌ Elemento quizzesGrid não encontrado no DOM');
            return;
        }

        console.log('🎨 Renderizando lista com', quizzes.length, 'quizzes');

        if (!quizzes || quizzes.length === 0) {
            console.log('📭 Nenhum quiz encontrado, exibindo estado vazio');
            grid.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">📚</div>
                    <h3>Nenhum quiz criado ainda</h3>
                    <p>Clique no botão acima para criar seu primeiro quiz</p>
                    <button onclick="window.location.href='create-quiz.html'" class="btn btn-primary" style="margin-top: 1rem;">
                        🎯 Criar Meu Primeiro Quiz
                    </button>
                </div>
            `;
            return;
        }

        grid.innerHTML = quizzes.map(quiz => {
            const questionCount = quiz.questions?.length || 0;
            const timesPlayed = quiz.timesPlayed || 0;
            const createdAt = Utils.formatDate(quiz.createdAt);
            const title = Utils.escapeHtml(quiz.title);
            const description = Utils.escapeHtml(quiz.description || 'Sem descrição');
            
            return `
            <div class="quiz-card" data-quiz-id="${quiz.id}">
                <div class="quiz-actions">
                    <button class="btn-icon edit-quiz" data-id="${quiz.id}" title="Editar">✏️</button>
                    <button class="btn-icon delete-quiz" data-id="${quiz.id}" title="Excluir">🗑️</button>
                    <button class="btn-icon play-quiz" data-id="${quiz.id}" title="Jogar">🎮</button>
                </div>
                <h3>${title}</h3>
                <p>${description}</p>
                <div class="quiz-stats">
                    <span>📊 ${questionCount} ${questionCount === 1 ? 'pergunta' : 'perguntas'}</span>
                    <span>🎯 ${timesPlayed} ${timesPlayed === 1 ? 'jogada' : 'jogadas'}</span>
                    <span>📅 ${createdAt}</span>
                </div>
            </div>
        `}).join('');

        // Adicionar event listeners
        document.querySelectorAll('.edit-quiz').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                console.log('✏️ Editando quiz:', btn.dataset.id);
                window.location.href = `create-quiz.html?edit=${btn.dataset.id}`;
            });
        });
        
        document.querySelectorAll('.delete-quiz').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                console.log('🗑️ Deletando quiz:', btn.dataset.id);
                this.confirmDeleteQuiz(btn.dataset.id);
            });
        });
        
        document.querySelectorAll('.play-quiz').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                console.log('🎮 Iniciando sessão do quiz:', btn.dataset.id);
                this.startQuizSession(btn.dataset.id);
            });
        });
        
        document.querySelectorAll('.quiz-card').forEach(card => {
            card.addEventListener('click', () => {
                const quizId = card.dataset.quizId;
                console.log('👁️ Visualizando quiz:', quizId);
                window.location.href = `create-quiz.html?view=${quizId}`;
            });
        });
        
        console.log('✅ Lista renderizada com sucesso! Total de cards:', document.querySelectorAll('.quiz-card').length);
    }

    updateStats(quizzes) {
        const totalQuizzes = quizzes.length;
        const totalQuestions = quizzes.reduce((sum, q) => sum + (q.questions?.length || 0), 0);
        const totalPlays = quizzes.reduce((sum, q) => sum + (q.timesPlayed || 0), 0);
        
        const totalQuizzesElem = document.getElementById('totalQuizzes');
        const totalQuestionsElem = document.getElementById('totalQuestions');
        const totalPlaysElem = document.getElementById('totalPlays');
        
        if (totalQuizzesElem) totalQuizzesElem.textContent = totalQuizzes;
        if (totalQuestionsElem) totalQuestionsElem.textContent = totalQuestions;
        if (totalPlaysElem) totalPlaysElem.textContent = totalPlays;
        
        console.log('📊 Estatísticas atualizadas:', { totalQuizzes, totalQuestions, totalPlays });
    }

    async confirmDeleteQuiz(quizId) {
        const modal = document.getElementById('confirmModal');
        if (!modal) {
            console.error('❌ Modal de confirmação não encontrado');
            return;
        }
        
        const messageElem = document.getElementById('confirmMessage');
        if (messageElem) {
            messageElem.textContent = 'Tem certeza que deseja excluir este quiz? Esta ação não pode ser desfeita.';
        }
        
        modal.style.display = 'block';
        
        const confirmYes = document.getElementById('confirmYes');
        const confirmNo = document.getElementById('confirmNo');
        
        if (!confirmYes || !confirmNo) {
            console.error('❌ Botões do modal não encontrados');
            modal.style.display = 'none';
            return;
        }
        
        const handleYes = async () => {
            console.log('✅ Confirmação de exclusão para quiz:', quizId);
            await this.deleteQuiz(quizId);
            modal.style.display = 'none';
            cleanup();
        };
        
        const handleNo = () => {
            console.log('❌ Exclusão cancelada para quiz:', quizId);
            modal.style.display = 'none';
            cleanup();
        };
        
        const cleanup = () => {
            confirmYes.removeEventListener('click', handleYes);
            confirmNo.removeEventListener('click', handleNo);
        };
        
        confirmYes.addEventListener('click', handleYes);
        confirmNo.addEventListener('click', handleNo);
    }

    async deleteQuiz(quizId) {
        if (!this.currentUser) {
            console.error('❌ Usuário não autenticado para deletar quiz');
            return;
        }
        
        try {
            console.log('🗑️ Deletando quiz:', quizId);
            await db.collection('quizzes').doc(quizId).delete();
            console.log('✅ Quiz deletado com sucesso:', quizId);
            Utils.showToast('Quiz excluído com sucesso!', 'success');
            await this.loadUserQuizzes();
        } catch (error) {
            console.error('❌ Erro ao deletar quiz:', error);
            Utils.showToast('Erro ao deletar quiz: ' + error.message, 'error');
        }
    }

    async startQuizSession(quizId) {
        try {
            console.log('🎮 Iniciando sessão do quiz:', quizId);
            const quizDoc = await db.collection('quizzes').doc(quizId).get();
            if (!quizDoc.exists) {
                console.error('❌ Quiz não encontrado:', quizId);
                Utils.showToast('Quiz não encontrado', 'error');
                return;
            }
            
            const quiz = { id: quizDoc.id, ...quizDoc.data() };
            console.log('📚 Quiz carregado:', quiz.title);
            
            const roomCode = generateRoomCode();
            const roomId = Utils.generateId();
            
            const room = {
                id: roomId,
                quizId: quizId,
                code: roomCode,
                creatorId: this.currentUser.uid,
                creatorName: this.currentUser.displayName || this.currentUser.email,
                status: 'waiting',
                currentQuestionIndex: 0,
                currentQuestionStartTime: null,
                players: {},
                createdAt: firebase.firestore.FieldValue.serverTimestamp(),
                active: true,
                quizTitle: quiz.title
            };
            
            console.log('🏠 Criando sala:', roomId, 'código:', roomCode);
            await db.collection('rooms').doc(roomId).set(room);
            await db.collection('quizzes').doc(quizId).update({
                timesPlayed: firebase.firestore.FieldValue.increment(1)
            });
            
            console.log('✅ Sala criada, redirecionando para host...');
            window.location.href = `host.html?room=${roomId}`;
        } catch (error) {
            console.error('❌ Erro ao iniciar sessão:', error);
            Utils.showToast('Erro ao iniciar sessão: ' + error.message, 'error');
        }
    }

    async loadQuizForEdit(quizId) {
        try {
            console.log('📝 Carregando quiz para edição:', quizId);
            const quizDoc = await db.collection('quizzes').doc(quizId).get();
            if (!quizDoc.exists) {
                Utils.showToast('Quiz não encontrado', 'error');
                return null;
            }
            const quiz = { id: quizDoc.id, ...quizDoc.data() };
            this.currentQuiz = quiz;
            this.questions = quiz.questions || [];
            console.log('✅ Quiz carregado:', quiz.title, 'com', this.questions.length, 'perguntas');
            return quiz;
        } catch (error) {
            console.error('❌ Erro ao carregar quiz:', error);
            Utils.showToast('Erro ao carregar quiz', 'error');
            return null;
        }
    }

    async saveCurrentQuiz() {
        const title = document.getElementById('quizTitle')?.value;
        const description = document.getElementById('quizDescription')?.value;
        const randomize = document.getElementById('randomizeQuestions')?.checked || false;
        const showCorrect = document.getElementById('showCorrectAnswer')?.checked || false;

        if (!title) {
            Utils.showToast('Por favor, insira um título para o quiz', 'warning');
            return false;
        }
        if (this.questions.length === 0) {
            Utils.showToast('Adicione pelo menos uma pergunta ao quiz', 'warning');
            return false;
        }

        for (let i = 0; i < this.questions.length; i++) {
            const q = this.questions[i];
            if (!q.text || q.text.trim() === '') {
                Utils.showToast(`Pergunta ${i + 1} está vazia`, 'warning');
                return false;
            }
            if (!q.options || q.options.length < 2) {
                Utils.showToast(`Pergunta ${i + 1} precisa ter pelo menos 2 opções`, 'warning');
                return false;
            }
            if (q.correct === undefined || q.correct === null) {
                Utils.showToast(`Pergunta ${i + 1} precisa ter uma resposta correta marcada`, 'warning');
                return false;
            }
        }

        const quizData = {
            title: title,
            description: description,
            questions: this.questions,
            settings: { randomizeQuestions: randomize, showCorrectAnswer: showCorrect, defaultTimeLimit: 30 },
            updatedAt: firebase.firestore.FieldValue.serverTimestamp()
        };

        try {
            if (this.currentQuiz && this.currentQuiz.id) {
                console.log('📝 Atualizando quiz:', this.currentQuiz.id);
                await this.updateQuiz(this.currentQuiz.id, quizData);
                return true;
            } else {
                console.log('📝 Criando novo quiz...');
                const newQuiz = await this.createQuiz(quizData);
                if (newQuiz) {
                    window.location.href = 'my-quizzes.html';
                    return true;
                }
                return false;
            }
        } catch (error) {
            console.error('❌ Erro ao salvar quiz:', error);
            Utils.showToast('Erro ao salvar quiz: ' + error.message, 'error');
            return false;
        }
    }

    async createQuiz(quizData) {
        if (!this.currentUser) {
            Utils.showToast('Você precisa estar logado', 'error');
            return null;
        }
        
        try {
            const quizId = Utils.generateId();
            console.log('🆕 Criando quiz com ID:', quizId);
            
            const quiz = {
                id: quizId,
                title: quizData.title,
                description: quizData.description || '',
                creatorId: this.currentUser.uid,
                creatorName: this.currentUser.displayName || this.currentUser.email,
                createdAt: firebase.firestore.FieldValue.serverTimestamp(),
                updatedAt: firebase.firestore.FieldValue.serverTimestamp(),
                questions: quizData.questions || [],
                settings: {
                    randomizeQuestions: quizData.randomizeQuestions || false,
                    showCorrectAnswer: quizData.showCorrectAnswer || true,
                    defaultTimeLimit: quizData.defaultTimeLimit || 30
                },
                timesPlayed: 0,
                tags: quizData.tags || []
            };
            
            await db.collection('quizzes').doc(quizId).set(quiz);
            console.log('✅ Quiz criado com sucesso:', quizId);
            Utils.showToast('Quiz criado com sucesso!', 'success');
            return quiz;
        } catch (error) {
            console.error('❌ Erro ao criar quiz:', error);
            Utils.showToast('Erro ao criar quiz: ' + error.message, 'error');
            return null;
        }
    }

    async updateQuiz(quizId, quizData) {
        if (!this.currentUser) return null;
        try {
            console.log('📝 Atualizando quiz:', quizId);
            await db.collection('quizzes').doc(quizId).update({
                ...quizData,
                updatedAt: firebase.firestore.FieldValue.serverTimestamp()
            });
            console.log('✅ Quiz atualizado com sucesso:', quizId);
            Utils.showToast('Quiz atualizado com sucesso!', 'success');
            return true;
        } catch (error) {
            console.error('❌ Erro ao atualizar quiz:', error);
            Utils.showToast('Erro ao atualizar quiz: ' + error.message, 'error');
            return false;
        }
    }
}

// Inicializar quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', () => {
    console.log('📄 DOM carregado, iniciando QuizManager...');
    window.quizManager = new QuizManager();
    
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', async () => {
            console.log('🚪 Usuário solicitou logout');
            await auth.signOut();
            window.location.href = 'index.html';
        });
    }
    
    const createNewQuiz = document.getElementById('createNewQuiz');
    if (createNewQuiz) {
        createNewQuiz.addEventListener('click', () => {
            console.log('➕ Criar novo quiz clicado');
            window.location.href = 'create-quiz.html';
        });
    }
    
    // Botões de salvar e cancelar são tratados no create-quiz.js
    console.log('✅ QuizManager inicializado com sucesso!');
});