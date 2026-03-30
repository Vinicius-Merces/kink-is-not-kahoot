// Player - Tela do Aluno (VERSÃO FINAL - Casada com Host + Pódio)
class PlayerManager {
    constructor() {
        this.roomCode = null;
        this.room = null;
        this.playerId = null;
        this.playerName = null;
        this.playerAvatar = null;
        this.currentQuestion = null;
        this.questionStartTime = null;
        this.hasAnswered = false;
        this.currentScreen = 'joinScreen';
        this.roomUnsubscribe = null;
        this.scoresUnsubscribe = null;
        this.readingTimer = null;
        this.answerTimer = null;
        this.init();
    }

    async init() {
        const urlParams = new URLSearchParams(window.location.search);
        this.roomCode = urlParams.get('code');
        if (this.roomCode) {
            document.getElementById('roomCodeInput').value = this.roomCode;
            await this.checkRoom();
        }
        this.setupEventListeners();
        this.loadAvatars();
        this.createAllDynamicScreens();
    }

    createAllDynamicScreens() {
        const container = document.querySelector('.player-container');

        // Loading Screen
        if (!document.getElementById('loadingScreen')) {
            container.insertAdjacentHTML('beforeend', `
                <div id="loadingScreen" class="player-screen">
                    <div class="loading-card">
                        <h2>🔄 Carregando Quiz...</h2>
                        <div class="loading-spinner"><div class="spinner"></div></div>
                        <p>Preparando perguntas...</p>
                        <div class="loading-timer"><span id="loadingTimer">5</span>s</div>
                    </div>
                </div>
            `);
        }

        // Reading Screen
        if (!document.getElementById('readingScreen')) {
            container.insertAdjacentHTML('beforeend', `
                <div id="readingScreen" class="player-screen">
                    <div class="reading-card">
                        <h2>📖 Leia atentamente</h2>
                        <div class="question-reading">
                            <p id="readingQuestionText" style="font-size: 1.35rem; line-height: 1.4;"></p>
                        </div>
                        <div class="reading-timer">
                            <div class="timer-circle"><span id="readingTimer">5</span></div>
                            <p>segundos</p>
                        </div>
                    </div>
                </div>
            `);
        }

        // Ranking Parcial
        if (!document.getElementById('rankingScreen')) {
            container.insertAdjacentHTML('beforeend', `
                <div id="rankingScreen" class="player-screen">
                    <div class="ranking-card">
                        <h2>🏆 Ranking Parcial 🏆</h2>
                        <div id="rankingListModal" class="ranking-list-modal"></div>
                        <div id="answerFeedback" class="feedback-message" style="margin-top: 1.5rem; display: none;"></div>
                        <p style="margin-top: 2rem; opacity: 0.8; text-align:center;">Aguardando próxima pergunta...</p>
                    </div>
                </div>
            `);
        }

        // Final Screen (Pódio)
        if (!document.getElementById('finalScreen')) {
            container.insertAdjacentHTML('beforeend', `
                <div id="finalScreen" class="player-screen">
                    <div class="final-card">
                        <h2>🏆 Quiz Finalizado! 🏆</h2>
                        <div id="finalPodium" class="podium"></div>
                        <div id="finalRankingList" class="ranking-list-large"></div>
                        <button id="exitGameBtn" class="btn btn-primary">Sair</button>
                    </div>
                </div>
            `);
        }
    }

    setupEventListeners() {
        document.getElementById('checkRoomBtn').addEventListener('click', () => this.checkRoom());
        document.getElementById('joinGameBtn').addEventListener('click', () => this.joinGame());
        const exitBtn = document.getElementById('exitGameBtn');
        if (exitBtn) exitBtn.addEventListener('click', () => window.location.href = 'index.html');
    }

    loadAvatars() {
        const avatars = [
            { id: 'avatar1', emoji: '🐱' }, { id: 'avatar2', emoji: '🐶' }, { id: 'avatar3', emoji: '🦊' },
            { id: 'avatar4', emoji: '🐼' }, { id: 'avatar5', emoji: '🐨' }, { id: 'avatar6', emoji: '🐸' },
            { id: 'avatar7', emoji: '🐙' }, { id: 'avatar8', emoji: '🦄' }
        ];
        const grid = document.getElementById('avatarsGrid');
        grid.innerHTML = avatars.map(a => `
            <div class="avatar-option" data-avatar="${a.id}">
                <div class="avatar-emoji">${a.emoji}</div>
            </div>
        `).join('');

        document.querySelector('.avatar-option').classList.add('selected');
        this.playerAvatar = 'avatar1';

        document.querySelectorAll('.avatar-option').forEach(opt => {
            opt.addEventListener('click', () => {
                document.querySelectorAll('.avatar-option').forEach(o => o.classList.remove('selected'));
                opt.classList.add('selected');
                this.playerAvatar = opt.dataset.avatar;
            });
        });
    }

    async checkRoom() {
        const code = document.getElementById('roomCodeInput').value.toUpperCase().trim();
        if (code.length !== 6) {
            Utils.showToast('Código inválido', 'warning');
            return;
        }
        try {
            const snapshot = await db.collection('rooms').where('code', '==', code).where('active', '==', true).get();
            if (snapshot.empty) {
                Utils.showToast('Sala não encontrada ou encerrada', 'error');
                return;
            }
            this.room = { id: snapshot.docs[0].id, ...snapshot.docs[0].data() };
            this.roomCode = code;
            this.showScreen('profileScreen');
        } catch (e) {
            Utils.showToast('Erro ao verificar sala', 'error');
        }
    }

    async joinGame() {
        const name = document.getElementById('playerName').value.trim();
        if (!name || !this.playerAvatar) {
            Utils.showToast('Nome e avatar são obrigatórios', 'warning');
            return;
        }
        this.playerId = Utils.generateId();
        this.playerName = name;
        try {
            await db.collection(`rooms/${this.room.id}/players`).doc(this.playerId).set({
                id: this.playerId, name: name, avatar: this.playerAvatar,
                joinedAt: firebase.firestore.FieldValue.serverTimestamp(), status: 'ready'
            });
            await db.collection(`rooms/${this.room.id}/scores`).doc(this.playerId).set({
                playerId: this.playerId, playerName: name, avatar: this.playerAvatar, totalScore: 0
            });
            this.showScreen('waitingScreen');
            document.getElementById('waitingRoomCode').textContent = this.roomCode;
            this.setupGameListeners();
        } catch (error) {
            Utils.showToast('Erro ao entrar na sala', 'error');
        }
    }

    setupGameListeners() {
        this.roomUnsubscribe = db.collection('rooms').doc(this.room.id).onSnapshot((doc) => {
            if (doc.exists) this.handleRoomUpdate(doc.data());
        });

        this.scoresUnsubscribe = db.collection(`rooms/${this.room.id}/scores`)
            .orderBy('totalScore', 'desc')
            .onSnapshot((snapshot) => {
                if (this.currentScreen === 'rankingScreen' || this.currentScreen === 'finalScreen') {
                    this.updateRankingModal(snapshot);
                }
            });
    }

    handleRoomUpdate(roomData) {
        this.room = { ...this.room, ...roomData };
        console.log(`📡 Status recebido: ${roomData.status} | Tela: ${this.currentScreen}`);

        switch (roomData.status) {
            case 'loading':
                this.showLoadingScreen();
                break;
            case 'reading':
                this.handleReadingPhase(roomData);
                break;
            case 'answering':
                this.handleAnsweringPhase(roomData);
                break;
            case 'active':
                if (this.currentScreen === 'questionScreen' || this.currentScreen === 'readingScreen') {
                    this.showRankingAfterQuestion();
                } else {
                    this.showScreen('waitingScreen');
                }
                break;
            case 'finished':
                this.showFinalScreen();
                break;
        }
    }

    showLoadingScreen() {
        this.showScreen('loadingScreen');
    }

    handleReadingPhase(roomData) {
        const qData = roomData.currentQuestionData;
        if (!qData) return;

        this.currentQuestion = {
            index: roomData.currentQuestionIndex,
            text: qData.text,
            options: qData.options,
            timeLimit: qData.timeLimit,
            correct: qData.correct
        };

        this.hasAnswered = false;
        this.showScreen('readingScreen');
        document.getElementById('readingQuestionText').textContent = this.currentQuestion.text;

        let timeLeft = 5;
        const timerEl = document.getElementById('readingTimer');
        if (timerEl) timerEl.textContent = timeLeft;

        if (this.readingTimer) clearInterval(this.readingTimer);
        this.readingTimer = setInterval(() => {
            timeLeft--;
            if (timerEl) timerEl.textContent = timeLeft;
            if (timeLeft <= 0) clearInterval(this.readingTimer);
        }, 1000);
    }

    handleAnsweringPhase(roomData) {
        const qData = roomData.currentQuestionData;
        if (!qData) return;

        this.currentQuestion = {
            index: roomData.currentQuestionIndex,
            text: qData.text,
            options: qData.options,
            timeLimit: qData.timeLimit,
            correct: qData.correct
        };

        this.questionStartTime = new Date();
        this.hasAnswered = false;

        if (this.readingTimer) clearInterval(this.readingTimer);

        this.showScreen('questionScreen');
        this.displayQuestion();
        this.startQuestionTimer();
    }

    displayQuestion() {
        document.getElementById('questionText').textContent = this.currentQuestion.text;
        const grid = document.getElementById('optionsGrid');
        const letters = ['A','B','C','D','E','F'];

        grid.innerHTML = this.currentQuestion.options.map((opt, i) => `
            <button class="option-btn" data-option="${i}">
                <div class="option-letter">${letters[i]}</div>
                <div class="option-text">${Utils.escapeHtml(opt)}</div>
            </button>
        `).join('');

        grid.querySelectorAll('.option-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                if (!this.hasAnswered) this.submitAnswer(parseInt(btn.dataset.option));
            });
        });
    }

    startQuestionTimer() {
        const timerValue = document.getElementById('timerValue');
        let timeLeft = this.currentQuestion.timeLimit;

        if (this.answerTimer) clearInterval(this.answerTimer);

        this.answerTimer = setInterval(() => {
            timeLeft--;
            timerValue.textContent = Math.max(0, timeLeft);
            if (timeLeft <= 0) {
                clearInterval(this.answerTimer);
                if (!this.hasAnswered) this.submitAnswer(null);
            }
        }, 1000);
    }

    async submitAnswer(selectedOption) {
        if (this.hasAnswered) return;
        this.hasAnswered = true;
        if (this.answerTimer) clearInterval(this.answerTimer);

        const responseTime = (new Date() - this.questionStartTime) / 1000;
        const isCorrect = selectedOption === this.currentQuestion.correct;

        this.currentQuestion.lastAnswerCorrect = isCorrect;

        try {
            await db.collection(`rooms/${this.room.id}/answers`)
                .doc(`${this.currentQuestion.index}_${this.playerId}`)
                .set({
                    playerId: this.playerId,
                    playerName: this.playerName,
                    avatar: this.playerAvatar,
                    questionIndex: this.currentQuestion.index,
                    answer: selectedOption,
                    responseTime: responseTime,
                    isCorrect: isCorrect,
                    timestamp: firebase.firestore.FieldValue.serverTimestamp()
                });

            document.querySelectorAll('.option-btn').forEach(btn => {
                btn.disabled = true;
                btn.classList.add('disabled');
                if (parseInt(btn.dataset.option) === selectedOption) btn.style.borderColor = '#ff6b6b';
            });
        } catch (error) {
            console.error('Erro ao enviar resposta:', error);
        }
    }

    showRankingAfterQuestion() {
        this.showScreen('rankingScreen');
        this.showAnswerFeedback();
        setTimeout(() => this.updateRankingFromFirestore(), 300);
    }

    showAnswerFeedback() {
        const feedbackDiv = document.getElementById('answerFeedback');
        if (!feedbackDiv || !this.currentQuestion) return;

        const isCorrect = this.currentQuestion.lastAnswerCorrect;

        feedbackDiv.innerHTML = isCorrect 
            ? `<div class="feedback correct">✅ Parabéns! Você acertou!</div>`
            : `<div class="feedback incorrect">❌ Você errou esta pergunta</div>`;

        feedbackDiv.style.display = 'block';
    }

    async updateRankingFromFirestore() {
        const container = document.getElementById('rankingListModal');
        if (!container) return;

        try {
            const snapshot = await db.collection(`rooms/${this.room.id}/scores`)
                .orderBy('totalScore', 'desc')
                .limit(10)
                .get();

            const rankings = [];
            snapshot.forEach(doc => rankings.push(doc.data()));

            container.innerHTML = rankings.map((player, index) => `
                <div class="ranking-item ${player.playerId === this.playerId ? 'current-player' : ''}">
                    <div class="ranking-position">${index + 1}º</div>
                    <div class="player-info">
                        <span class="player-avatar">${Utils.getAvatarEmoji(player.avatar)}</span>
                        <span>${Utils.escapeHtml(player.playerName)}</span>
                    </div>
                    <div class="ranking-score">${player.totalScore || 0} pts</div>
                </div>
            `).join('');
        } catch (err) {
            console.error(err);
        }
    }

    updateRankingModal(snapshot) {
        this.updateRankingFromFirestore();
    }

    async showFinalScreen() {
        this.showScreen('finalScreen');
        const snapshot = await db.collection(`rooms/${this.room.id}/scores`)
            .orderBy('totalScore', 'desc')
            .limit(10)
            .get();

        this.updateFinalPodium(snapshot);
    }

    updateFinalPodium(snapshot) {
        const container = document.getElementById('finalPodium');
        const rankings = [];
        snapshot.forEach(doc => rankings.push(doc.data()));

        let html = `<h3 style="color:#ff6b6b; margin-bottom:1rem;">Pódio Final</h3>`;

        if (rankings[0]) html += `<div style="font-size:2.2rem; margin:1rem 0;">🥇 ${Utils.getAvatarEmoji(rankings[0].avatar)} ${rankings[0].playerName} — ${rankings[0].totalScore} pts</div>`;
        if (rankings[1]) html += `<div style="font-size:1.8rem; margin:0.8rem 0;">🥈 ${Utils.getAvatarEmoji(rankings[1].avatar)} ${rankings[1].playerName} — ${rankings[1].totalScore} pts</div>`;
        if (rankings[2]) html += `<div style="font-size:1.5rem; margin:0.8rem 0;">🥉 ${Utils.getAvatarEmoji(rankings[2].avatar)} ${rankings[2].playerName} — ${rankings[2].totalScore} pts</div>`;

        if (container) container.innerHTML = html;

        // Ranking completo abaixo do pódio
        const fullList = document.getElementById('finalRankingList');
        if (fullList) {
            fullList.innerHTML = rankings.map((p, i) => `
                <div class="ranking-item ${p.playerId === this.playerId ? 'current-player' : ''}">
                    <div class="ranking-position">${i+1}º</div>
                    <div class="player-info">
                        <span class="player-avatar">${Utils.getAvatarEmoji(p.avatar)}</span>
                        <span>${Utils.escapeHtml(p.playerName)}</span>
                    </div>
                    <div class="ranking-score">${p.totalScore || 0} pts</div>
                </div>
            `).join('');
        }
    }

    showScreen(screenId) {
        this.currentScreen = screenId;
        document.querySelectorAll('.player-screen').forEach(s => s.classList.remove('active'));
        const screen = document.getElementById(screenId);
        if (screen) screen.classList.add('active');
    }

    cleanup() {
        if (this.roomUnsubscribe) this.roomUnsubscribe();
        if (this.scoresUnsubscribe) this.scoresUnsubscribe();
        if (this.readingTimer) clearInterval(this.readingTimer);
        if (this.answerTimer) clearInterval(this.answerTimer);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.playerManager = new PlayerManager();
    window.addEventListener('beforeunload', () => window.playerManager?.cleanup());
});