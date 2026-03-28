// Painel do Professor - Gerenciamento de sala ao vivo
class HostManager {
    constructor() {
        this.roomId = null;
        this.room = null;
        this.currentQuestionIndex = 0;
        this.readingTimer = null;
        this.answerTimer = null;
        this.playersUnsubscribe = null;
        this.rankingUnsubscribe = null;
        this.roomUnsubscribe = null;
        this.answersUnsubscribe = null;
        this.isProcessing = false;
        this.isFinishing = false;
        this.totalPlayers = 0;
        this.answeredPlayers = new Set();
        this.init();
    }

    async init() {
        const urlParams = new URLSearchParams(window.location.search);
        this.roomId = urlParams.get('room');
        if (!this.roomId) {
            Utils.showToast('Sala não encontrada', 'error');
            setTimeout(() => window.location.href = 'my-quizzes.html', 2000);
            return;
        }

        auth.onAuthStateChanged(async (user) => {
            if (!user) {
                window.location.href = 'index.html';
                return;
            }
            await this.loadRoom();
            this.setupListeners();
        });
    }

    async loadRoom() {
        try {
            const roomDoc = await db.collection('rooms').doc(this.roomId).get();
            if (!roomDoc.exists) {
                Utils.showToast('Sala não encontrada', 'error');
                window.location.href = 'my-quizzes.html';
                return;
            }
            this.room = roomDoc.data();
            this.renderRoomInfo();
        } catch (error) {
            console.error("Erro ao carregar sala:", error);
        }
    }

    setupListeners() {
        // Monitorar jogadores
        this.playersUnsubscribe = db.collection('rooms').doc(this.roomId).collection('players')
            .onSnapshot(snapshot => {
                this.totalPlayers = snapshot.size;
                this.updatePlayersList(snapshot);
            });

        // Monitorar a própria sala para mudanças de status/pergunta
        this.roomUnsubscribe = db.collection('rooms').doc(this.roomId)
            .onSnapshot(doc => {
                const data = doc.data();
                if (data) {
                    this.room = data;
                    this.currentQuestionIndex = data.currentQuestionIndex || 0;
                    this.updateUIStatus(data.status);
                }
            });

        // Eventos de botões
        document.getElementById('startQuizBtn')?.addEventListener('click', () => this.startGame());
        document.getElementById('nextQuestionBtn')?.addEventListener('click', () => this.nextQuestion());
        document.getElementById('finishQuizBtn')?.addEventListener('click', () => this.finishQuiz());
        document.getElementById('startQuestionBtn')?.addEventListener('click', () => this.startQuestionReading());
    }

    async startGame() {
        if (this.room.status !== 'waiting') return;
        
        console.log('🎮 Iniciando quiz - fase de loading...');
        
        try {
            // 1. Ativa estado de loading para todos
            await db.collection('rooms').doc(this.roomId).update({
                status: 'loading',
                currentQuestionIndex: 0
            });

            Utils.showToast('Preparando quiz...', 'info');

            // 2. Aguarda 5 segundos para garantir que os players viram a tela de loading
            await new Promise(resolve => setTimeout(resolve, 5000));

            // 3. Muda para active para mostrar o botão de "Iniciar Pergunta"
            await db.collection('rooms').doc(this.roomId).update({
                status: 'active'
            });
            
            Utils.showToast('Pronto! Clique em Iniciar Pergunta.', 'success');
        } catch (error) {
            console.error("Erro ao iniciar jogo:", error);
        }
    }

    async startQuestionReading() {
        if (this.isProcessing) return;
        this.isProcessing = true;

        const question = this.room.questions[this.currentQuestionIndex];
        
        try {
            // Limpa respostas da rodada anterior no Firestore se necessário
            this.answeredPlayers.clear();
            
            // Define status como READING (tempo para o aluno ler a pergunta)
            await db.collection('rooms').doc(this.roomId).update({
                status: 'reading',
                currentQuestionStartTime: null // Só começa a contar no answering
            });

            console.log('📖 Fase de leitura iniciada (5s)');
            
            // Timer de 5 segundos de leitura
            let timeLeft = 5;
            this.updateTimerDisplay(timeLeft, 'Leitura...');

            this.readingTimer = setInterval(async () => {
                timeLeft--;
                this.updateTimerDisplay(timeLeft, 'Leitura...');
                
                if (timeLeft <= 0) {
                    clearInterval(this.readingTimer);
                    await this.startAnsweringPhase(question);
                }
            }, 1000);

        } catch (error) {
            console.error("Erro ao iniciar leitura:", error);
            this.isProcessing = false;
        }
    }

    async startAnsweringPhase(question) {
        const startTime = firebase.firestore.Timestamp.now();
        
        await db.collection('rooms').doc(this.roomId).update({
            status: 'answering',
            currentQuestionStartTime: startTime
        });

        console.log('⚡ Fase de respostas iniciada');
        this.isProcessing = false;

        let timeLeft = question.timeLimit || 30;
        this.updateTimerDisplay(timeLeft, 'Respondendo!');

        this.answerTimer = setInterval(() => {
            timeLeft--;
            this.updateTimerDisplay(timeLeft, 'Respondendo!');
            
            if (timeLeft <= 0 || this.answeredPlayers.size >= this.totalPlayers) {
                this.stopQuestion();
            }
        }, 1000);

        // Listen para respostas em tempo real
        this.setupAnswersListener();
    }

    setupAnswersListener() {
        if (this.answersUnsubscribe) this.answersUnsubscribe();
        
        this.answersUnsubscribe = db.collection('rooms').doc(this.roomId)
            .collection('answers')
            .where('questionIndex', '==', this.currentQuestionIndex)
            .onSnapshot(snapshot => {
                snapshot.docChanges().forEach(change => {
                    if (change.type === 'added') {
                        this.answeredPlayers.add(change.doc.data().playerId);
                        this.updateAnsweredCount();
                    }
                });
            });
    }

    async stopQuestion() {
        clearInterval(this.answerTimer);
        if (this.answersUnsubscribe) this.answersUnsubscribe();
        
        await db.collection('rooms').doc(this.roomId).update({
            status: 'active' // Volta para active para mostrar ranking e botão de próxima
        });

        this.showRoundRanking();
    }

    async nextQuestion() {
        const nextIndex = this.currentQuestionIndex + 1;
        
        if (nextIndex >= this.room.questions.length) {
            this.finishQuiz();
            return;
        }

        await db.collection('rooms').doc(this.roomId).update({
            currentQuestionIndex: nextIndex,
            status: 'active'
        });
        
        // Esconde modal de ranking se houver
        document.getElementById('rankingModal').style.display = 'none';
    }

    async finishQuiz() {
        await db.collection('rooms').doc(this.roomId).update({
            status: 'finished'
        });
    }

    // Métodos de UI resumidos (baseados no seu original)
    updateUIStatus(status) {
        const startBtn = document.getElementById('startQuizBtn');
        const nextBtn = document.getElementById('nextQuestionBtn');
        const startQuestionBtn = document.getElementById('startQuestionBtn');
        const lobbySection = document.getElementById('lobbySection');
        const gameSection = document.getElementById('gameSection');

        if (status === 'waiting') {
            if (lobbySection) lobbySection.style.display = 'block';
            if (gameSection) gameSection.style.display = 'none';
        } else {
            if (lobbySection) lobbySection.style.display = 'none';
            if (gameSection) gameSection.style.display = 'block';
        }

        // Controle de botões conforme status
        if (startBtn) startBtn.style.display = status === 'waiting' ? 'block' : 'none';
        if (startQuestionBtn) startQuestionBtn.style.display = status === 'active' ? 'block' : 'none';
        if (nextBtn) nextBtn.style.display = 'none'; // Só aparece após a pergunta
    }

    updateTimerDisplay(time, label) {
        const timerEl = document.getElementById('timerDisplay');
        if (timerEl) timerEl.innerHTML = `<span>${label}</span> <strong>${time}s</strong>`;
    }

    updateAnsweredCount() {
        const el = document.getElementById('answersCount');
        if (el) el.textContent = `${this.answeredPlayers.size} / ${this.totalPlayers}`;
    }

    renderRoomInfo() {
        const titleEl = document.getElementById('quizTitle');
        const codeEl = document.getElementById('roomCodeDisplay');
        if (titleEl) titleEl.textContent = this.room.quizTitle;
        if (codeEl) codeEl.textContent = this.room.id;
    }

    updatePlayersList(snapshot) {
        const list = document.getElementById('playersList');
        const count = document.getElementById('playersCount');
        if (!list) return;
        const players = [];
        snapshot.forEach(doc => players.push(doc.data()));
        list.innerHTML = players.map(player => `
            <div class="player-card">
                <div class="player-avatar">${Utils.getAvatarEmoji(player.avatar)}</div>
                <div class="player-name"><span>${Utils.escapeHtml(player.name)}</span></div>
            </div>`).join('');
        count.textContent = players.length;
    }

    async showRoundRanking() {
        // Lógica para buscar scores e exibir no modal do host
        const snapshot = await db.collection('rooms').doc(this.roomId).collection('players').orderBy('totalScore', 'desc').limit(5).get();
        const rankings = [];
        snapshot.forEach(doc => rankings.push(doc.data()));
        this.updateRanking(rankings);
        
        const modal = document.getElementById('rankingModal');
        if (modal) modal.style.display = 'block';
        
        const nextBtn = document.getElementById('nextQuestionBtn');
        if (nextBtn) nextBtn.style.display = 'block';
    }

    updateRanking(rankings) {
        const list = document.getElementById('rankingList');
        if (!list) return;
        list.innerHTML = rankings.map((player, index) => `
            <div class="ranking-item">
                <div class="ranking-position">${index + 1}º</div>
                <div class="player-info">
                    <span class="player-avatar">${Utils.getAvatarEmoji(player.avatar)}</span>
                    <span>${Utils.escapeHtml(player.playerName || player.name)}</span>
                </div>
                <div class="ranking-score">${player.totalScore || 0} pts</div>
            </div>`).join('');
    }

    cleanup() {
        if (this.playersUnsubscribe) this.playersUnsubscribe();
        if (this.roomUnsubscribe) this.roomUnsubscribe();
        if (this.answersUnsubscribe) this.answersUnsubscribe();
        if (this.readingTimer) clearInterval(this.readingTimer);
        if (this.answerTimer) clearInterval(this.answerTimer);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.hostManager = new HostManager();
});