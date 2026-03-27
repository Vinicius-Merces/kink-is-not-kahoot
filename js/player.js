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
        this.timerInterval = null;
        this.nextTimerInterval = null;
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
        });
    }

    handleRoomUpdate(roomData) {
        this.room = { ...this.room, ...roomData };
        if (roomData.status === 'question_active') this.handleQuestionStart(roomData);
        else if (roomData.status === 'active' && this.currentScreen === 'questionScreen') this.showResultScreen();
        else if (roomData.status === 'finished') this.showFinalScreen();
    }

    async handleQuestionStart(roomData) {
        if (this.currentScreen === 'questionScreen') return;
        
        const currentIndex = roomData.currentQuestionIndex;
        const questionData = roomData.currentQuestionData;
        if (!questionData) return;
        
        this.currentQuestion = {
            index: currentIndex,
            text: questionData.text,
            options: questionData.options,
            timeLimit: questionData.timeLimit,
            correct: questionData.correct
        };
        
        this.questionStartTime = new Date(); // Registrar momento exato
        this.hasAnswered = false;
        
        if (this.timerInterval) clearInterval(this.timerInterval);
        
        this.showScreen('questionScreen');
        this.displayQuestion();
        this.startQuestionTimer();
        
        console.log(`🎯 Pergunta ${currentIndex + 1} iniciada!`);
        console.log(`   Tempo limite: ${this.currentQuestion.timeLimit}s`);
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
        
        this.timerInterval = setInterval(() => {
            timeLeft--;
            timerValue.textContent = Math.max(0, timeLeft);
            if (timeLeft <= 5) timerCircle.style.animation = 'pulse 0.5s infinite';
            if (timeLeft <= 0) {
                clearInterval(this.timerInterval);
                if (!this.hasAnswered) this.submitAnswer(null);
            }
        }, 1000);
    }

    async submitAnswer(selectedOption) {
        if (this.hasAnswered) return;
        this.hasAnswered = true;
        
        if (this.timerInterval) clearInterval(this.timerInterval);
        
        // Calcular tempo de resposta em segundos
        const responseTime = (new Date() - this.questionStartTime) / 1000;
        const timeLimit = this.currentQuestion.timeLimit;
        const isCorrect = (selectedOption === this.currentQuestion.correct);
        
        // Calcular pontos (o host vai recalcular, mas mostramos uma prévia)
        let previewPoints = 0;
        if (isCorrect && selectedOption !== null) {
            const timeRemaining = Math.max(0, timeLimit - responseTime);
            previewPoints = Math.floor(1000 * (timeRemaining / timeLimit));
            previewPoints = Math.min(1000, Math.max(0, previewPoints));
        }
        
        console.log(`\n📤 RESPOSTA ENVIADA:`);
        console.log(`   Jogador: ${this.playerName}`);
        console.log(`   Resposta: ${selectedOption !== null ? String.fromCharCode(65 + selectedOption) : 'Nenhuma'}`);
        console.log(`   Correta: ${isCorrect ? 'SIM' : 'NÃO'}`);
        console.log(`   Tempo: ${responseTime.toFixed(2)}s / ${timeLimit}s`);
        console.log(`   Pontos (prévia): ${previewPoints}`);
        
        try {
            // Salvar resposta no Firestore
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
            
            console.log(`✅ Resposta salva com sucesso!`);
            
            // Atualizar pontuação local (prévia visual)
            const currentScoreElem = document.getElementById('currentScore');
            if (currentScoreElem) {
                const currentScore = parseInt(currentScoreElem.textContent) || 0;
                currentScoreElem.textContent = currentScore + previewPoints;
            }
            
            // Mostrar feedback visual
            this.showQuestionFeedback(isCorrect, previewPoints, this.currentQuestion.options[this.currentQuestion.correct]);
            
            // Desabilitar opções
            document.querySelectorAll('.option-btn').forEach(btn => {
                btn.disabled = true;
                btn.classList.add('disabled');
            });
            
        } catch (error) {
            console.error('❌ Erro ao enviar resposta:', error);
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

    showResultScreen() {
        if (this.nextTimerInterval) clearInterval(this.nextTimerInterval);
        this.showScreen('resultScreen');
        let timeLeft = 5;
        const nextTimerSpan = document.getElementById('nextTimer');
        this.nextTimerInterval = setInterval(() => {
            timeLeft--;
            if (nextTimerSpan) nextTimerSpan.textContent = timeLeft;
            if (timeLeft <= 0) {
                clearInterval(this.nextTimerInterval);
                this.showScreen('waitingScreen');
            }
        }, 1000);
    }

    async showFinalScreen() {
        if (this.timerInterval) clearInterval(this.timerInterval);
        if (this.nextTimerInterval) clearInterval(this.nextTimerInterval);
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
        document.getElementById(screenId).classList.add('active');
    }

    cleanup() {
        if (this.roomUnsubscribe) this.roomUnsubscribe();
        if (this.scoresUnsubscribe) this.scoresUnsubscribe();
        if (this.timerInterval) clearInterval(this.timerInterval);
        if (this.nextTimerInterval) clearInterval(this.nextTimerInterval);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.playerManager = new PlayerManager();
    window.addEventListener('beforeunload', () => { if (window.playerManager) window.playerManager.cleanup(); });
});