// Painel do Professor - Gerenciamento de sala ao vivo
class HostManager {
    constructor() {
        this.roomId = null;
        this.room = null;
        this.quiz = null;
        this.currentQuestion = null;
        this.questionStartTime = null;
        this.timerInterval = null;
        this.playersUnsubscribe = null;
        this.rankingUnsubscribe = null;
        this.roomUnsubscribe = null;
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
            this.room = { id: roomDoc.id, ...roomDoc.data() };
            if (this.room.creatorId !== auth.currentUser.uid) {
                Utils.showToast('Você não é o criador desta sala', 'error');
                window.location.href = 'my-quizzes.html';
                return;
            }
            const quizDoc = await db.collection('quizzes').doc(this.room.quizId).get();
            this.quiz = { id: quizDoc.id, ...quizDoc.data() };
            this.updateUI();
        } catch (error) {
            Utils.showToast('Erro ao carregar sala', 'error');
        }
    }

    setupListeners() {
        this.roomUnsubscribe = db.collection('rooms').doc(this.roomId)
            .onSnapshot((doc) => {
                if (doc.exists) {
                    this.room = { id: doc.id, ...doc.data() };
                    this.updateRoomStatus();
                }
            });
        this.playersUnsubscribe = db.collection(`rooms/${this.roomId}/players`)
            .onSnapshot((snapshot) => {
                const players = [];
                snapshot.forEach(doc => players.push({ id: doc.id, ...doc.data() }));
                this.updatePlayersList(players);
            });
        this.rankingUnsubscribe = db.collection(`rooms/${this.roomId}/scores`)
            .orderBy('totalScore', 'desc')
            .onSnapshot((snapshot) => {
                const rankings = [];
                snapshot.forEach(doc => rankings.push({ id: doc.id, ...doc.data() }));
                this.updateRanking(rankings);
            });
    }

    updateUI() {
        const roomCodeElem = document.getElementById('roomCode');
        if (roomCodeElem) roomCodeElem.textContent = this.room.code;
        
        const quizInfoElem = document.getElementById('quizInfo');
        if (quizInfoElem) quizInfoElem.innerHTML = `<strong>Quiz:</strong> ${this.quiz.title} | <strong>Perguntas:</strong> ${this.quiz.questions.length}`;
        
        const copyBtn = document.getElementById('copyCodeBtn');
        if (copyBtn) copyBtn.addEventListener('click', () => {
            navigator.clipboard.writeText(this.room.code);
            Utils.showToast('Código copiado!', 'success');
        });
        
        const shareBtn = document.getElementById('shareRoomBtn');
        if (shareBtn) shareBtn.addEventListener('click', () => {
            const url = `${window.location.origin}/player.html?code=${this.room.code}`;
            navigator.clipboard.writeText(url);
            Utils.showToast('Link copiado! Compartilhe com seus alunos', 'success');
        });
        
        const startGameBtn = document.getElementById('startGameBtn');
        const startQuestionBtn = document.getElementById('startQuestionBtn');
        const nextQuestionBtn = document.getElementById('nextQuestionBtn');
        const endGameBtn = document.getElementById('endGameBtn');
        
        if (startGameBtn) startGameBtn.addEventListener('click', () => this.startGame());
        if (startQuestionBtn) startQuestionBtn.addEventListener('click', () => this.startCurrentQuestion());
        if (nextQuestionBtn) nextQuestionBtn.addEventListener('click', () => this.nextQuestion());
        if (endGameBtn) endGameBtn.addEventListener('click', () => this.endGame());
    }

    updateRoomStatus() {
        const questionControls = document.getElementById('questionControls');
        const startGameBtn = document.getElementById('startGameBtn');
        if (this.room.status === 'waiting') {
            startGameBtn.style.display = 'block';
            questionControls.style.display = 'none';
        } else if (this.room.status === 'active') {
            startGameBtn.style.display = 'none';
            questionControls.style.display = 'block';
            this.updateCurrentQuestionDisplay();
        } else if (this.room.status === 'question_active') {
            this.startTimer();
        }
    }

    updateCurrentQuestionDisplay() {
        const display = document.getElementById('currentQuestionDisplay');
        const currentIndex = this.room.currentQuestionIndex;
        if (currentIndex < this.quiz.questions.length) {
            const question = this.quiz.questions[currentIndex];
            display.innerHTML = `<div class="current-question"><strong>Pergunta ${currentIndex + 1}/${this.quiz.questions.length}</strong><p>${Utils.escapeHtml(question.text)}</p><small>Tempo limite: ${question.timeLimit || 30}s</small></div>`;
        } else {
            display.innerHTML = '<p class="placeholder">Quiz finalizado!</p>';
        }
    }

    startGame() {
        if (this.room.status !== 'waiting') return;
        db.collection('rooms').doc(this.roomId).update({ status: 'active', currentQuestionIndex: 0 });
        Utils.showToast('Jogo iniciado! Prepare-se para a primeira pergunta', 'success');
    }

    async startCurrentQuestion() {
        const currentIndex = this.room.currentQuestionIndex;
        if (currentIndex >= this.quiz.questions.length) {
            this.endGame();
            return;
        }
        const question = this.quiz.questions[currentIndex];
        await db.collection('rooms').doc(this.roomId).update({
            status: 'question_active',
            currentQuestionStartTime: firebase.firestore.FieldValue.serverTimestamp(),
            currentQuestionData: {
                text: question.text,
                options: question.options,
                timeLimit: question.timeLimit || 30,
                correct: question.correct
            }
        });
        document.getElementById('startQuestionBtn').style.display = 'none';
        document.getElementById('nextQuestionBtn').style.display = 'block';
        Utils.showToast(`Pergunta ${currentIndex + 1} iniciada!`, 'info');
        this.startTimer(question.timeLimit || 30);
    }

    startTimer(limit = 30) {
        const timerDisplay = document.getElementById('questionTimer');
        const timerSeconds = document.getElementById('timerSeconds');
        const timerBar = document.querySelector('.timer-bar');
        timerDisplay.style.display = 'block';
        let timeLeft = limit;
        timerSeconds.textContent = timeLeft;
        if (timerBar) timerBar.style.width = '100%';
        this.timerInterval = setInterval(() => {
            timeLeft--;
            timerSeconds.textContent = Math.max(0, timeLeft);
            if (timerBar) timerBar.style.width = `${Math.max(0, (timeLeft / limit) * 100)}%`;
            if (timeLeft <= 0) {
                clearInterval(this.timerInterval);
                this.finishQuestion();
            }
        }, 1000);
        setTimeout(() => {
            if (this.room.status === 'question_active') this.finishQuestion();
        }, limit * 1000);
    }

    async finishQuestion() {
        if (this.timerInterval) clearInterval(this.timerInterval);
        const currentIndex = this.room.currentQuestionIndex;
        const question = this.quiz.questions[currentIndex];
        const answersSnapshot = await db.collection(`rooms/${this.roomId}/answers`).where('questionIndex', '==', currentIndex).get();
        const answers = [];
        answersSnapshot.forEach(doc => answers.push({ id: doc.id, ...doc.data() }));
        
        for (const answer of answers) {
            const isCorrect = answer.answer === question.correct;
            const timeSpent = answer.responseTime || 0;
            const timeLimit = question.timeLimit || 30;
            let points = 0;
            if (isCorrect) {
                const speedBonus = Math.max(0, (timeLimit - timeSpent) / timeLimit);
                points = Math.floor(1000 * speedBonus);
            }
            const playerScoreRef = db.collection(`rooms/${this.roomId}/scores`).doc(answer.playerId);
            const playerScoreDoc = await playerScoreRef.get();
            if (playerScoreDoc.exists) {
                const currentScore = playerScoreDoc.data().totalScore || 0;
                await playerScoreRef.update({
                    totalScore: currentScore + points,
                    [`answers.q${currentIndex}`]: { points: points, correct: isCorrect, time: timeSpent },
                    updatedAt: firebase.firestore.FieldValue.serverTimestamp()
                });
            } else {
                await playerScoreRef.set({
                    playerId: answer.playerId,
                    playerName: answer.playerName,
                    avatar: answer.avatar,
                    totalScore: points,
                    [`answers.q${currentIndex}`]: { points: points, correct: isCorrect, time: timeSpent },
                    updatedAt: firebase.firestore.FieldValue.serverTimestamp()
                });
            }
        }
        const totalAnswers = answers.length;
        const correctAnswers = answers.filter(a => a.answer === question.correct).length;
        const accuracy = totalAnswers > 0 ? (correctAnswers / totalAnswers * 100).toFixed(1) : 0;
        document.getElementById('answersCount').textContent = totalAnswers;
        document.getElementById('accuracyRate').textContent = `${accuracy}%`;
        await db.collection('rooms').doc(this.roomId).update({ status: 'active' });
        Utils.showToast(`Pergunta finalizada! ${correctAnswers}/${totalAnswers} acertos`, 'info');
    }

    async nextQuestion() {
        const nextIndex = this.room.currentQuestionIndex + 1;
        if (nextIndex >= this.quiz.questions.length) {
            this.endGame();
            return;
        }
        await db.collection('rooms').doc(this.roomId).update({ currentQuestionIndex: nextIndex, status: 'active' });
        document.getElementById('startQuestionBtn').style.display = 'block';
        document.getElementById('nextQuestionBtn').style.display = 'none';
        document.getElementById('questionTimer').style.display = 'none';
        this.updateCurrentQuestionDisplay();
        Utils.showToast(`Preparando pergunta ${nextIndex + 1}...`, 'info');
    }

    async endGame() {
        if (this.timerInterval) clearInterval(this.timerInterval);
        await db.collection('rooms').doc(this.roomId).update({ status: 'finished', active: false, endedAt: firebase.firestore.FieldValue.serverTimestamp() });
        Utils.showToast('Quiz finalizado! Obrigado a todos os participantes!', 'success');
        document.getElementById('startQuestionBtn').style.display = 'none';
        document.getElementById('nextQuestionBtn').style.display = 'none';
        document.getElementById('startGameBtn').style.display = 'none';
    }

    updatePlayersList(players) {
        const list = document.getElementById('playersList');
        const count = document.getElementById('playersCount');
        if (!list) return;
        if (players.length === 0) {
            list.innerHTML = '<p class="placeholder">Aguardando jogadores...</p>';
            count.textContent = '0';
            return;
        }
        list.innerHTML = players.map(player => `<div class="player-item"><div class="player-info"><span class="player-avatar">${Utils.getAvatarEmoji(player.avatar)}</span><span>${Utils.escapeHtml(player.name)}</span></div><div class="player-status">${player.status === 'ready' ? '✓' : '⏳'}</div></div>`).join('');
        count.textContent = players.length;
    }

    updateRanking(rankings) {
        const list = document.getElementById('rankingList');
        if (!list) return;
        if (rankings.length === 0) {
            list.innerHTML = '<p class="placeholder">Aguardando respostas...</p>';
            return;
        }
        list.innerHTML = rankings.slice(0, 10).map((player, index) => `<div class="ranking-item"><div class="ranking-position">${index + 1}º</div><div class="player-info"><span class="player-avatar">${Utils.getAvatarEmoji(player.avatar)}</span><span>${Utils.escapeHtml(player.playerName)}</span></div><div class="ranking-score">${player.totalScore || 0} pts</div></div>`).join('');
    }

    cleanup() {
        if (this.playersUnsubscribe) this.playersUnsubscribe();
        if (this.rankingUnsubscribe) this.rankingUnsubscribe();
        if (this.roomUnsubscribe) this.roomUnsubscribe();
        if (this.timerInterval) clearInterval(this.timerInterval);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.hostManager = new HostManager();
    window.addEventListener('beforeunload', () => { if (window.hostManager) window.hostManager.cleanup(); });
});