// Player - Tela do Aluno
class PlayerManager {
    constructor() {
        this.roomCode = null;
        this.room = null;
        this.quiz = null;
        this.playerId = null;
        this.playerName = null;
        this.playerAvatar = null;
        this.currentQuestion = null;
        this.questionStartTime = null;
        this.hasAnswered = false;
        this.readingTimer = null;
        this.answerTimer = null;
        this.roomUnsubscribe = null;
        this.scoresUnsubscribe = null;
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
    }

    setupEventListeners() {
        const checkRoomBtn = document.getElementById('checkRoomBtn');
        if (checkRoomBtn) checkRoomBtn.addEventListener('click', () => this.checkRoom());
        const joinGameBtn = document.getElementById('joinGameBtn');
        if (joinGameBtn) joinGameBtn.addEventListener('click', () => this.joinGame());
        const exitGameBtn = document.getElementById('exitGameBtn');
        if (exitGameBtn) exitGameBtn.addEventListener('click', () => window.location.href = 'index.html');
        
        const roomCodeInput = document.getElementById('roomCodeInput');
        if (roomCodeInput) roomCodeInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') this.checkRoom(); });
        const playerNameInput = document.getElementById('playerName');
        if (playerNameInput) playerNameInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') this.joinGame(); });
    }

    loadAvatars() {
        const avatars = [
            { id: 'avatar1', emoji: '🐱', name: 'Gato' }, { id: 'avatar2', emoji: '🐶', name: 'Cachorro' },
            { id: 'avatar3', emoji: '🦊', name: 'Raposa' }, { id: 'avatar4', emoji: '🐼', name: 'Panda' },
            { id: 'avatar5', emoji: '🐨', name: 'Koala' }, { id: 'avatar6', emoji: '🐸', name: 'Sapo' },
            { id: 'avatar7', emoji: '🐙', name: 'Polvo' }, { id: 'avatar8', emoji: '🦄', name: 'Unicórnio' }
        ];
        const grid = document.getElementById('avatarsGrid');
        if (!grid) return;
        grid.innerHTML = avatars.map(avatar => `<div class="avatar-option" data-avatar="${avatar.id}"><div class="avatar-emoji">${avatar.emoji}</div><div class="avatar-name">${avatar.name}</div></div>`).join('');
        const firstAvatar = document.querySelector('.avatar-option');
        if (firstAvatar) {
            firstAvatar.classList.add('selected');
            this.playerAvatar = 'avatar1';
        }
        document.querySelectorAll('.avatar-option').forEach(option => {
            option.addEventListener('click', () => {
                document.querySelectorAll('.avatar-option').forEach(opt => opt.classList.remove('selected'));
                option.classList.add('selected');
                this.playerAvatar = option.dataset.avatar;
            });
        });
    }

    async checkRoom() {
        const codeInput = document.getElementById('roomCodeInput');
        const code = codeInput.value.toUpperCase().trim();
        if (!code || code.length !== 6) {
            Utils.showToast('Por favor, insira um código válido de 6 caracteres', 'warning');
            return;
        }
        try {
            const snapshot = await db.collection('rooms').where('code', '==', code).where('active', '==', true).get();
            if (snapshot.empty) {
                Utils.showToast('Sala não encontrada ou já encerrada', 'error');
                return;
            }
            this.room = { id: snapshot.docs[0].id, ...snapshot.docs[0].data() };
            this.roomCode = code;
            const quizDoc = await db.collection('quizzes').doc(this.room.quizId).get();
            this.quiz = { id: quizDoc.id, ...quizDoc.data() };
            this.showScreen('profileScreen');
        } catch (error) {
            Utils.showToast('Erro ao verificar sala', 'error');
        }
    }

    async joinGame() {
        const nameInput = document.getElementById('playerName');
        const name = nameInput.value.trim();
        if (!name) {
            Utils.showToast('Por favor, digite seu nome', 'warning');
            return;
        }
        if (!this.playerAvatar) {
            Utils.showToast('Por favor, escolha um avatar', 'warning');
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
                playerId: this.playerId, playerName: name, avatar: this.playerAvatar,
                totalScore: 0, answers: {}, joinedAt: firebase.firestore.FieldValue.serverTimestamp()
            });
            this.showScreen('waitingScreen');
            document.getElementById('waitingRoomCode').textContent = this.roomCode;
            this.setupGameListeners();
        } catch (error) {
            Utils.showToast('Erro ao entrar no jogo', 'error');
        }
    }

    setupGameListeners() {
        this.roomUnsubscribe = db.collection('rooms').doc(this.room.id).onSnapshot((doc) => {
            if (!doc.exists) {
                Utils.showToast('Sala encerrada', 'info');
                window.location.href = 'index.html';
                return;
            }
            this.handleRoomUpdate(doc.data());
        });
        this.scoresUnsubscribe = db.collection(`rooms/${this.room.id}/scores`).orderBy('totalScore', 'desc').onSnapshot((snapshot) => {
            if (this.currentScreen === 'finalScreen') this.updateFinalRanking(snapshot);
            else if (this.currentScreen === 'waitingScreen') this.updateWaitingPlayers(snapshot);
            else if (this.currentScreen === 'rankingScreen') this.updateRankingModal(snapshot);
            else if (this.currentScreen === 'questionScreen') this.updateCurrentScore();
        });
    }
    
    updateCurrentScore() {
        const scoreRef = db.collection(`rooms/${this.room.id}/scores`).doc(this.playerId);
        scoreRef.get().then(doc => {
            if (doc.exists) {
                const currentScoreElem = document.getElementById('currentScore');
                if (currentScoreElem) {
                    currentScoreElem.textContent = doc.data().totalScore || 0;
                }
            }
        });
    }

    handleRoomUpdate(roomData) {
        this.room = { ...this.room, ...roomData };
        
        if (roomData.status === 'loading') {
            this.showLoadingScreen();
        } else if (roomData.status === 'reading') {
            this.handleReadingPhase(roomData);
        } else if (roomData.status === 'answering') {
            this.handleAnsweringPhase(roomData);
        } else if (roomData.status === 'active' && this.currentScreen === 'questionScreen') {
            // Mostrar ranking após a pergunta
            this.showRankingAfterQuestion();
        } else if (roomData.status === 'active' && this.currentScreen === 'rankingScreen') {
            this.closeRankingModal();
            this.showScreen('waitingScreen');
        } else if (roomData.status === 'finished') {
            this.showFinalScreen();
        }
    }

    showLoadingScreen() {
        this.showScreen('loadingScreen');
        this.createLoadingScreen();
        
        let timeLeft = 5;
        const timerSpan = document.getElementById('loadingTimer');
        const loadingInterval = setInterval(() => {
            timeLeft--;
            if (timerSpan) timerSpan.textContent = timeLeft;
            if (timeLeft <= 0) {
                clearInterval(loadingInterval);
            }
        }, 1000);
    }

    createLoadingScreen() {
        if (document.getElementById('loadingScreen')) return;
        
        const loadingHTML = `
            <div id="loadingScreen" class="player-screen">
                <div class="loading-card">
                    <h2>🔄 Carregando Quiz...</h2>
                    <div class="loading-spinner" style="margin: 1rem auto;">
                        <div class="spinner"></div>
                    </div>
                    <p>Preparando perguntas e sistema...</p>
                    <div class="loading-timer">
                        <span id="loadingTimer">5</span>s
                    </div>
                </div>
            </div>
        `;
        
        const container = document.querySelector('.player-container');
        container.insertAdjacentHTML('beforeend', loadingHTML);
    }

    handleReadingPhase(roomData) {
        if (this.currentScreen === 'questionScreen') return;
        
        const questionData = roomData.currentQuestionData;
        if (!questionData) return;
        
        this.currentQuestion = {
            index: roomData.currentQuestionIndex,
            text: questionData.text,
            options: questionData.options,
            timeLimit: questionData.timeLimit,
            correct: questionData.correct
        };
        
        this.hasAnswered = false;
        this.showScreen('readingScreen');
        this.createReadingScreen();
        
        document.getElementById('readingQuestionText').textContent = this.currentQuestion.text;
        
        let timeLeft = 5;
        const timerSpan = document.getElementById('readingTimer');
        timerSpan.textContent = timeLeft;
        
        if (this.readingTimer) clearInterval(this.readingTimer);
        
        this.readingTimer = setInterval(() => {
            timeLeft--;
            if (timerSpan) timerSpan.textContent = timeLeft;
            if (timeLeft <= 0) {
                clearInterval(this.readingTimer);
            }
        }, 1000);
    }
    
    createReadingScreen() {
        if (document.getElementById('readingScreen')) return;
        
        const readingHTML = `
            <div id="readingScreen" class="player-screen">
                <div class="reading-card">
                    <h2>📖 Leia a pergunta</h2>
                    <div class="question-reading">
                        <p id="readingQuestionText" style="font-size: 1.3rem; margin: 1rem 0;"></p>
                    </div>
                    <div class="reading-timer">
                        <div class="timer-circle" id="readingTimerCircle">
                            <span id="readingTimer">5</span>
                        </div>
                        <p>Segundos para responder</p>
                    </div>
                </div>
            </div>
        `;
        
        const container = document.querySelector('.player-container');
        container.insertAdjacentHTML('beforeend', readingHTML);
    }

    handleAnsweringPhase(roomData) {
        if (this.currentScreen === 'questionScreen') return;
        
        const questionData = roomData.currentQuestionData;
        if (!questionData) return;
        
        this.currentQuestion = {
            index: roomData.currentQuestionIndex,
            text: questionData.text,
            options: questionData.options,
            timeLimit: questionData.timeLimit,
            correct: questionData.correct
        };
        
        this.questionStartTime = new Date();
        this.hasAnswered = false;
        
        if (this.readingTimer) clearInterval(this.readingTimer);
        if (this.answerTimer) clearInterval(this.answerTimer);
        
        this.showScreen('questionScreen');
        this.displayQuestion();
        this.startQuestionTimer();
        
        console.log(`🎯 Pergunta ${this.currentQuestion.index + 1} iniciada!`);
    }

    displayQuestion() {
        document.getElementById('questionText').textContent = this.currentQuestion.text;
        const optionsGrid = document.getElementById('optionsGrid');
        const letters = ['A', 'B', 'C', 'D', 'E', 'F'];
        optionsGrid.innerHTML = this.currentQuestion.options.map((option, index) => `
            <button class="option-btn" data-option="${index}">
                <div class="option-letter">${letters[index]}</div>
                <div class="option-text">${Utils.escapeHtml(option)}</div>
            </button>
        `).join('');
        
        document.querySelectorAll('.option-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                if (!this.hasAnswered) this.submitAnswer(parseInt(btn.dataset.option));
            });
        });
    }

    startQuestionTimer() {
        const timerCircle = document.getElementById('timerCircle');
        const timerValue = document.getElementById('timerValue');
        let timeLeft = this.currentQuestion.timeLimit;
        timerValue.textContent = timeLeft;
        
        this.answerTimer = setInterval(() => {
            timeLeft--;
            timerValue.textContent = Math.max(0, timeLeft);
            if (timeLeft <= 5) timerCircle.style.animation = 'pulse 0.5s infinite';
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
        const timeLimit = this.currentQuestion.timeLimit;
        const isCorrect = (selectedOption === this.currentQuestion.correct);
        
        let previewPoints = 0;
        if (isCorrect && selectedOption !== null) {
            const timeRemaining = Math.max(0, timeLimit - responseTime);
            previewPoints = Math.floor(1000 * (timeRemaining / timeLimit));
            previewPoints = Math.min(1000, Math.max(0, previewPoints));
        }
        
        console.log(`📤 ${this.playerName}: ${isCorrect ? 'ACERTOU' : 'ERROU'} em ${responseTime.toFixed(2)}s`);
        
        try {
            await db.collection(`rooms/${this.room.id}/answers`).doc(`${this.currentQuestion.index}_${this.playerId}`).set({
                playerId: this.playerId,
                playerName: this.playerName,
                avatar: this.playerAvatar,
                questionIndex: this.currentQuestion.index,
                answer: selectedOption,
                isCorrect: isCorrect,
                responseTime: responseTime,
                timestamp: firebase.firestore.FieldValue.serverTimestamp()
            });
            
            const currentScoreElem = document.getElementById('currentScore');
            if (currentScoreElem) {
                const currentScore = parseInt(currentScoreElem.textContent) || 0;
                currentScoreElem.textContent = currentScore + previewPoints;
            }
            
            this.showQuestionFeedback(isCorrect, previewPoints, this.currentQuestion.options[this.currentQuestion.correct]);
            
            document.querySelectorAll('.option-btn').forEach(btn => {
                btn.disabled = true;
                btn.classList.add('disabled');
            });
            
        } catch (error) {
            console.error('Erro ao enviar resposta:', error);
            Utils.showToast('Erro ao enviar resposta', 'error');
        }
    }

    showQuestionFeedback(isCorrect, points, correctAnswer) {
        const feedbackDiv = document.getElementById('feedbackMessage');
        const resultIcon = isCorrect ? '✅' : '❌';
        const message = isCorrect 
            ? `Correto! +${points} pontos!` 
            : `Errou! A resposta correta era: ${correctAnswer}`;
        
        feedbackDiv.innerHTML = `
            <div class="feedback ${isCorrect ? 'correct' : 'incorrect'}">
                <span class="feedback-icon">${resultIcon}</span>
                <span class="feedback-text">${message}</span>
            </div>
        `;
        
        feedbackDiv.style.display = 'block';
        
        setTimeout(() => {
            feedbackDiv.style.display = 'none';
        }, 3000);
    }

    showRankingAfterQuestion() {
        this.showScreen('rankingScreen');
        this.createRankingScreen();
    }

    createRankingScreen() {
        if (document.getElementById('rankingScreen')) return;
        
        const rankingHTML = `
            <div id="rankingScreen" class="player-screen">
                <div class="ranking-card">
                    <h2>🏆 Ranking Parcial 🏆</h2>
                    <div id="rankingListModal" class="ranking-list-modal"></div>
                    <div class="next-question-timer">
                        Aguardando próxima pergunta...
                    </div>
                </div>
            </div>
        `;
        
        const container = document.querySelector('.player-container');
        container.insertAdjacentHTML('beforeend', rankingHTML);
    }

    updateRankingModal(snapshot) {
        const listDiv = document.getElementById('rankingListModal');
        if (!listDiv) return;
        
        const rankings = [];
        snapshot.forEach(doc => rankings.push({ id: doc.id, ...doc.data() }));
        
        listDiv.innerHTML = rankings.slice(0, 5).map((player, index) => `
            <div class="ranking-item ${player.playerId === this.playerId ? 'current-player' : ''}">
                <div class="ranking-position">${index + 1}º</div>
                <div class="player-info">
                    <span class="player-avatar">${Utils.getAvatarEmoji(player.avatar)}</span>
                    <span>${Utils.escapeHtml(player.playerName)}</span>
                </div>
                <div class="ranking-score">${player.totalScore || 0} pts</div>
            </div>
        `).join('');
    }
    
    closeRankingModal() {
        this.showScreen('waitingScreen');
    }

    async showFinalScreen() {
        if (this.readingTimer) clearInterval(this.readingTimer);
        if (this.answerTimer) clearInterval(this.answerTimer);
        
        this.showScreen('finalScreen');
        const scoresSnapshot = await db.collection(`rooms/${this.room.id}/scores`).orderBy('totalScore', 'desc').limit(10).get();
        const rankings = [];
        scoresSnapshot.forEach(doc => rankings.push({ id: doc.id, ...doc.data() }));
        this.updateFinalRanking(rankings);
    }

    updateFinalRanking(rankings) {
        const list = document.getElementById('finalRankingList');
        if (!list) return;
        if (rankings.length === 0) {
            list.innerHTML = '<p class="placeholder">Nenhum jogador</p>';
            return;
        }
        list.innerHTML = rankings.map((player, index) => `
            <div class="ranking-item ${player.playerId === this.playerId ? 'current-player' : ''}">
                <div class="ranking-position">${index + 1}º</div>
                <div class="player-info">
                    <span class="player-avatar">${Utils.getAvatarEmoji(player.avatar)}</span>
                    <span>${Utils.escapeHtml(player.playerName)}</span>
                </div>
                <div class="ranking-score">${player.totalScore || 0} pts</div>
            </div>
        `).join('');
    }

    updateWaitingPlayers(snapshot) {
        const list = document.getElementById('waitingPlayersList');
        if (!list) return;
        const players = [];
        snapshot.forEach(doc => players.push({ id: doc.id, ...doc.data() }));
        if (players.length === 0) {
            list.innerHTML = '<p class="placeholder">Aguardando jogadores...</p>';
            return;
        }
        list.innerHTML = players.map(player => `<div class="player-item-mini"><span class="player-avatar-mini">${Utils.getAvatarEmoji(player.avatar)}</span><span>${Utils.escapeHtml(player.playerName)}</span></div>`).join('');
    }

    showScreen(screenId) {
        this.currentScreen = screenId;
        document.querySelectorAll('.player-screen').forEach(screen => screen.classList.remove('active'));
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
    window.addEventListener('beforeunload', () => { if (window.playerManager) window.playerManager.cleanup(); });
});