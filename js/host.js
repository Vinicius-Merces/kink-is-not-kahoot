class HostManager {
    constructor() {
        this.roomId = null;
        this.room = null;
        this.currentQuestionIndex = 0;
        this.totalPlayers = 0;
        this.answeredPlayers = new Set();
        
        // Timers e Listeners
        this.readingTimer = null;
        this.answerTimer = null;
        this.playersUnsubscribe = null;
        this.roomUnsubscribe = null;
        this.rankingUnsubscribe = null;
        this.answersUnsubscribe = null;

        this.init();
    }

    async init() {
        const urlParams = new URLSearchParams(window.location.search);
        this.roomId = urlParams.get('room');

        if (!this.roomId) {
            Utils.showToast('ID da sala não encontrado!', 'error');
            return;
        }

        auth.onAuthStateChanged(async (user) => {
            if (!user) {
                window.location.href = 'index.html';
                return;
            }
            await this.loadRoom();
            this.setupListeners();
            this.setupButtonEvents();
        });
    }

    async loadRoom() {
        try {
            const roomDoc = await db.collection('rooms').doc(this.roomId).get();
            if (!roomDoc.exists) {
                Utils.showToast('Sala não encontrada!', 'error');
                return;
            }
            this.room = roomDoc.data();
            this.renderInitialUI();
        } catch (error) {
            console.error("Erro ao carregar sala:", error);
        }
    }

    renderInitialUI() {
        document.getElementById('roomCode').textContent = this.room.code;
        document.getElementById('quizTitleDisplay').textContent = this.room.quizTitle;
        document.getElementById('totalQNumber').textContent = this.room.questions.length;
    }

    setupListeners() {
        // Monitorar Sala
        this.roomUnsubscribe = db.collection('rooms').doc(this.roomId).onSnapshot(doc => {
            if (doc.exists) this.room = doc.data();
        });

        // Monitorar Jogadores
        this.playersUnsubscribe = db.collection('rooms').doc(this.roomId).collection('players')
            .onSnapshot(snapshot => {
                const players = [];
                snapshot.forEach(d => players.push({id: d.id, ...d.data()}));
                this.totalPlayers = players.length;
                this.renderPlayers(players);
            });

        // Monitorar Ranking
        this.rankingUnsubscribe = db.collection('rooms').doc(this.roomId).collection('rankings')
            .orderBy('totalScore', 'desc').limit(10)
            .onSnapshot(snapshot => {
                const rankings = [];
                snapshot.forEach(d => rankings.push(d.data()));
                this.renderRanking(rankings);
            });
    }

    setupButtonEvents() {
        document.getElementById('startGameBtn')?.addEventListener('click', () => this.startGame());
        document.getElementById('startQuestionBtn')?.addEventListener('click', () => this.startQuestionReading());
        document.getElementById('nextQuestionBtn')?.addEventListener('click', () => this.nextQuestion());
        document.getElementById('copyCodeBtn')?.addEventListener('click', () => {
            navigator.clipboard.writeText(this.room.code);
            Utils.showToast('Código copiado!');
        });
    }

    // --- LÓGICA DE JOGO ---

    async startGame() {
        // Fase de Transição (Loading) para sincronizar todos os dispositivos
        await db.collection('rooms').doc(this.roomId).update({
            status: 'loading',
            active: true
        });
        
        document.getElementById('lobbyControls').style.display = 'none';
        document.getElementById('gameControls').style.display = 'block';
        document.getElementById('currentQNumber').textContent = "1";
    }

    async startQuestionReading() {
        const question = this.room.questions[this.currentQuestionIndex];
        this.answeredPlayers.clear();
        document.getElementById('answersCount').textContent = "0";

        // Muda para fase de LEITURA (Trava os botões no player por 5s)
        await db.collection('rooms').doc(this.roomId).update({
            status: 'reading',
            currentQuestionIndex: this.currentQuestionIndex,
            currentQuestionStartTime: firebase.firestore.FieldValue.serverTimestamp()
        });

        document.getElementById('startQuestionBtn').style.display = 'none';
        this.showQuestionPreview(question);

        // Timer de 5 segundos de leitura antes de liberar a resposta
        setTimeout(() => this.startAnsweringPhase(question.timeLimit), 5000);
    }

    async startAnsweringPhase(timeLimit) {
        await db.collection('rooms').doc(this.roomId).update({ status: 'answering' });
        this.startTimer(timeLimit);
        
        // Listener para contar respostas em tempo real
        this.answersUnsubscribe = db.collection('rooms').doc(this.roomId).collection('answers')
            .where('questionIndex', '==', this.currentQuestionIndex)
            .onSnapshot(snap => {
                this.answeredPlayers = new Set();
                snap.forEach(d => this.answeredPlayers.add(d.id));
                document.getElementById('answersCount').textContent = this.answeredPlayers.size;
                
                // Se todos responderam, encerra o timer
                if (this.totalPlayers > 0 && this.answeredPlayers.size >= this.totalPlayers) {
                    this.endQuestion();
                }
            });
    }

    startTimer(seconds) {
        let timeLeft = seconds;
        const timerEl = document.getElementById('hostTimer');
        const secondsEl = document.getElementById('timerSeconds');
        
        timerEl.style.display = 'flex';
        secondsEl.textContent = timeLeft;

        if (this.answerTimer) clearInterval(this.answerTimer);
        this.answerTimer = setInterval(() => {
            timeLeft--;
            secondsEl.textContent = timeLeft;
            if (timeLeft <= 0) this.endQuestion();
        }, 1000);
    }

    async endQuestion() {
        clearInterval(this.answerTimer);
        if (this.answersUnsubscribe) this.answersUnsubscribe();
        
        await db.collection('rooms').doc(this.roomId).update({ status: 'leaderboard' });
        
        document.getElementById('hostTimer').style.display = 'none';
        document.getElementById('nextQuestionBtn').style.display = 'block';
    }

    async nextQuestion() {
        this.currentQuestionIndex++;
        
        if (this.currentQuestionIndex >= this.room.questions.length) {
            this.finishGame();
        } else {
            document.getElementById('nextQuestionBtn').style.display = 'none';
            document.getElementById('startQuestionBtn').style.display = 'block';
            document.getElementById('currentQNumber').textContent = this.currentQuestionIndex + 1;
            await db.collection('rooms').doc(this.roomId).update({ status: 'idle' });
        }
    }

    async finishGame() {
        await db.collection('rooms').doc(this.roomId).update({ status: 'finished' });
        document.getElementById('gameControls').style.display = 'none';
        document.getElementById('finishControls').style.display = 'block';
    }

    // --- RENDERIZAÇÃO ---

    showQuestionPreview(question) {
        const display = document.getElementById('currentQuestionDisplay');
        display.innerHTML = `
            <div class="preview-box">
                <h4>${question.text}</h4>
                <div class="preview-options">
                    ${question.options.map((opt, i) => `<div class="opt ${i === question.correctAnswer ? 'correct' : ''}">${opt}</div>`).join('')}
                </div>
            </div>
        `;
    }

    renderPlayers(players) {
        const list = document.getElementById('playersList');
        document.getElementById('playersCount').textContent = players.length;
        list.innerHTML = players.map(p => `
            <div class="player-badge">
                <span>${Utils.getAvatarEmoji(p.avatar)}</span>
                <small>${Utils.escapeHtml(p.playerName)}</small>
            </div>
        `).join('');
    }

    renderRanking(rankings) {
        const list = document.getElementById('rankingList');
        list.innerHTML = rankings.map((r, i) => `
            <div class="ranking-item">
                <span>${i+1}º ${r.playerName}</span>
                <strong>${r.totalScore}</strong>
            </div>
        `).join('');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.hostManager = new HostManager();
});