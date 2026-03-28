// Painel do Professor - Gerenciamento de sala ao vivo
class HostManager {
    constructor() {
        this.roomId = null;
        this.room = null;
        this.quiz = null;
        this.currentQuestionIndex = 0;
        this.readingTimer = null;
        this.answerTimer = null;
        this.playersUnsubscribe = null;
        this.rankingUnsubscribe = null;
        this.roomUnsubscribe = null;
        this.isProcessing = false;
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
            this.currentQuestionIndex = this.room.currentQuestionIndex || 0;
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
        } else if (this.room.status === 'reading') {
            this.updateReadingPhase();
        } else if (this.room.status === 'answering') {
            this.updateAnsweringPhase();
        }
    }

    updateCurrentQuestionDisplay() {
        const display = document.getElementById('currentQuestionDisplay');
        if (this.currentQuestionIndex < this.quiz.questions.length) {
            const question = this.quiz.questions[this.currentQuestionIndex];
            display.innerHTML = `<div class="current-question"><strong>Pergunta ${this.currentQuestionIndex + 1}/${this.quiz.questions.length}</strong><p>${Utils.escapeHtml(question.text)}</p><small>Tempo limite: ${question.timeLimit || 30}s</small></div>`;
        } else {
            display.innerHTML = '<p class="placeholder">Quiz finalizado!</p>';
        }
    }

    startGame() {
        if (this.room.status !== 'waiting') return;
        
        console.log('🎮 Iniciando quiz...');
        
        db.collection('rooms').doc(this.roomId).update({ 
            status: 'active', 
            currentQuestionIndex: 0 
        });
        
        Utils.showToast('Jogo iniciado! Clique em "Iniciar Pergunta" para começar', 'success');
    }

    async startCurrentQuestion() {
        if (this.isProcessing) return;
        if (this.currentQuestionIndex >= this.quiz.questions.length) {
            this.endGame();
            return;
        }
        
        this.isProcessing = true;
        const currentQuestion = this.quiz.questions[this.currentQuestionIndex];
        const timeLimit = currentQuestion.timeLimit || 30;
        
        console.log(`\n🎯 ========== PERGUNTA ${this.currentQuestionIndex + 1} ==========`);
        console.log(`   ${currentQuestion.text}`);
        console.log(`   Tempo para responder: ${timeLimit}s`);
        
        // Atualizar status para leitura
        await db.collection('rooms').doc(this.roomId).update({
            status: 'reading',
            currentQuestionData: {
                text: currentQuestion.text,
                options: currentQuestion.options,
                timeLimit: timeLimit,
                correct: currentQuestion.correct,
                readingTime: 5
            },
            currentQuestionIndex: this.currentQuestionIndex
        });
        
        Utils.showToast(`Pergunta ${this.currentQuestionIndex + 1} - Leia a pergunta!`, 'info');
        
        // Aguardar 5 segundos de leitura
        await new Promise(resolve => {
            this.readingTimer = setTimeout(resolve, 5000);
        });
        
        // Fase de respostas
        await db.collection('rooms').doc(this.roomId).update({
            status: 'answering',
            currentQuestionStartTime: firebase.firestore.FieldValue.serverTimestamp()
        });
        
        Utils.showToast(`Respondam! Você tem ${timeLimit} segundos!`, 'info');
        
        // Aguardar tempo de resposta
        await new Promise(resolve => {
            this.answerTimer = setTimeout(resolve, timeLimit * 1000);
        });
        
        // Finalizar pergunta e calcular pontuação
        await this.finishQuestion();
        this.isProcessing = false;
    }
    
    updateReadingPhase() {
        const display = document.getElementById('currentQuestionDisplay');
        const question = this.quiz.questions[this.currentQuestionIndex];
        display.innerHTML = `
            <div class="current-question" style="background: rgba(78, 205, 196, 0.2);">
                <strong>📖 Leia a pergunta (5s)</strong>
                <p style="font-size: 1.2rem; margin-top: 1rem;">${Utils.escapeHtml(question.text)}</p>
                <small>As opções aparecerão em breve...</small>
            </div>
        `;
        document.getElementById('questionTimer').style.display = 'none';
    }
    
    updateAnsweringPhase() {
        const display = document.getElementById('currentQuestionDisplay');
        const question = this.quiz.questions[this.currentQuestionIndex];
        display.innerHTML = `
            <div class="current-question">
                <strong>⚡ Responda agora!</strong>
                <p>${Utils.escapeHtml(question.text)}</p>
                <small>Tempo limite: ${question.timeLimit || 30}s</small>
            </div>
        `;
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
        
        if (this.answerTimer) clearInterval(this.answerTimer);
        
        this.answerTimer = setInterval(() => {
            timeLeft--;
            timerSeconds.textContent = Math.max(0, timeLeft);
            if (timerBar) timerBar.style.width = `${Math.max(0, (timeLeft / limit) * 100)}%`;
            if (timeLeft <= 0) {
                clearInterval(this.answerTimer);
            }
        }, 1000);
    }

    async finishQuestion() {
        if (this.readingTimer) clearTimeout(this.readingTimer);
        if (this.answerTimer) clearInterval(this.answerTimer);
        
        const question = this.quiz.questions[this.currentQuestionIndex];
        const timeLimit = question.timeLimit || 30;
        
        console.log(`\n🏁 ========== FINALIZANDO PERGUNTA ${this.currentQuestionIndex + 1} ==========`);
        
        // Buscar todas as respostas
        const answersSnapshot = await db.collection(`rooms/${this.roomId}/answers`)
            .where('questionIndex', '==', this.currentQuestionIndex)
            .get();
        
        const answers = [];
        answersSnapshot.forEach(doc => answers.push({ id: doc.id, ...doc.data() }));
        
        console.log(`   Total de respostas: ${answers.length}`);
        
        let correctCount = 0;
        
        // Calcular pontuação para cada resposta
        for (const answer of answers) {
            const isCorrect = (answer.answer === question.correct);
            let points = 0;
            
            if (isCorrect) {
                let responseTime = answer.responseTime || timeLimit;
                responseTime = Math.min(responseTime, timeLimit);
                const timeRemaining = Math.max(0, timeLimit - responseTime);
                points = Math.floor(1000 * (timeRemaining / timeLimit));
                points = Math.min(1000, Math.max(0, points));
                
                console.log(`   ✅ ${answer.playerName}: ACERTOU! Tempo: ${responseTime.toFixed(2)}s -> ${points} pts`);
                correctCount++;
            } else {
                console.log(`   ❌ ${answer.playerName}: ERROU! 0 pts`);
            }
            
            // Atualizar resposta
            await db.collection(`rooms/${this.roomId}/answers`).doc(answer.id).update({
                points: points,
                isCorrect: isCorrect,
                calculatedAt: firebase.firestore.FieldValue.serverTimestamp()
            });
            
            // Atualizar pontuação do jogador
            const playerScoreRef = db.collection(`rooms/${this.roomId}/scores`).doc(answer.playerId);
            const playerScoreDoc = await playerScoreRef.get();
            const currentScore = playerScoreDoc.exists ? playerScoreDoc.data().totalScore || 0 : 0;
            
            await playerScoreRef.set({
                playerId: answer.playerId,
                playerName: answer.playerName,
                avatar: answer.avatar,
                totalScore: currentScore + points,
                updatedAt: firebase.firestore.FieldValue.serverTimestamp()
            }, { merge: true });
        }
        
        // Estatísticas
        const totalAnswers = answers.length;
        const accuracy = totalAnswers > 0 ? (correctCount / totalAnswers * 100).toFixed(1) : 0;
        
        document.getElementById('answersCount').textContent = totalAnswers;
        document.getElementById('accuracyRate').textContent = `${accuracy}%`;
        
        console.log(`\n📊 ESTATÍSTICAS:`);
        console.log(`   Acertos: ${correctCount}/${totalAnswers} (${accuracy}%)`);
        console.log(`=========================================\n`);
        
        // Mostrar ranking parcial
        await this.showRankingModal();
        
        // Atualizar status da sala para aguardar próxima pergunta
        await db.collection('rooms').doc(this.roomId).update({ 
            status: 'active' 
        });
        
        // Resetar UI
        document.getElementById('questionTimer').style.display = 'none';
        document.getElementById('startQuestionBtn').style.display = 'block';
        document.getElementById('nextQuestionBtn').style.display = 'none';
        
        Utils.showToast(`Pergunta finalizada! ${correctCount}/${totalAnswers} acertos`, 'info');
    }
    
    async showRankingModal() {
        // Buscar ranking atual
        const scoresSnapshot = await db.collection(`rooms/${this.roomId}/scores`)
            .orderBy('totalScore', 'desc')
            .limit(5)
            .get();
        
        const rankings = [];
        scoresSnapshot.forEach(doc => rankings.push({ id: doc.id, ...doc.data() }));
        
        if (rankings.length === 0) return;
        
        return new Promise((resolve) => {
            const modal = document.createElement('div');
            modal.className = 'modal';
            modal.style.display = 'block';
            modal.innerHTML = `
                <div class="modal-content" style="max-width: 500px; text-align: center;">
                    <h2 style="color: #ff6b6b; margin-bottom: 1rem;">🏆 Ranking Parcial 🏆</h2>
                    <div style="margin: 1rem 0;">
                        ${rankings.map((player, index) => `
                            <div style="display: flex; justify-content: space-between; padding: 0.8rem; border-bottom: 1px solid rgba(255,255,255,0.1);">
                                <span style="font-weight: bold; font-size: 1.2rem;">${index + 1}º</span>
                                <span>${Utils.getAvatarEmoji(player.avatar)} ${Utils.escapeHtml(player.playerName)}</span>
                                <span style="color: #ff6b6b; font-weight: bold;">${player.totalScore || 0} pts</span>
                            </div>
                        `).join('')}
                    </div>
                    <button id="continueBtn" class="btn btn-primary btn-large" style="margin-top: 1rem;">
                        ➡️ Próxima Pergunta
                    </button>
                </div>
            `;
            
            document.body.appendChild(modal);
            
            const continueBtn = modal.querySelector('#continueBtn');
            const closeModal = () => {
                modal.remove();
                resolve();
            };
            
            continueBtn.addEventListener('click', closeModal);
            modal.addEventListener('click', (e) => {
                if (e.target === modal) closeModal();
            });
        });
    }

    async nextQuestion() {
        const nextIndex = this.currentQuestionIndex + 1;
        
        console.log(`🔄 Avançando para pergunta ${nextIndex + 1}...`);
        
        if (nextIndex >= this.quiz.questions.length) {
            this.endGame();
            return;
        }
        
        this.currentQuestionIndex = nextIndex;
        
        // Atualizar sala com nova pergunta
        await db.collection('rooms').doc(this.roomId).update({ 
            currentQuestionIndex: nextIndex, 
            status: 'active' 
        });
        
        // Resetar botões e mostrar próxima pergunta
        document.getElementById('startQuestionBtn').style.display = 'block';
        document.getElementById('nextQuestionBtn').style.display = 'none';
        
        this.updateCurrentQuestionDisplay();
        
        Utils.showToast(`Preparando pergunta ${nextIndex + 1}...`, 'info');
    }

    async endGame() {
        await db.collection('rooms').doc(this.roomId).update({ 
            status: 'finished', 
            active: false, 
            endedAt: firebase.firestore.FieldValue.serverTimestamp() 
        });
        
        console.log(`\n🏆 QUIZ FINALIZADO! 🏆`);
        
        // Mostrar ranking final
        await this.showFinalRanking();
        
        document.getElementById('startQuestionBtn').style.display = 'none';
        document.getElementById('nextQuestionBtn').style.display = 'none';
        document.getElementById('startGameBtn').style.display = 'none';
        Utils.showToast('Quiz finalizado! Obrigado a todos!', 'success');
    }
    
    async showFinalRanking() {
        const scoresSnapshot = await db.collection(`rooms/${this.roomId}/scores`)
            .orderBy('totalScore', 'desc')
            .limit(10)
            .get();
        
        const rankings = [];
        scoresSnapshot.forEach(doc => rankings.push({ id: doc.id, ...doc.data() }));
        
        if (rankings.length === 0) return;
        
        return new Promise((resolve) => {
            const modal = document.createElement('div');
            modal.className = 'modal';
            modal.style.display = 'block';
            modal.innerHTML = `
                <div class="modal-content" style="max-width: 500px; text-align: center;">
                    <h2 style="color: #ff6b6b; margin-bottom: 1rem;">🏆 Ranking Final 🏆</h2>
                    <div style="margin: 1rem 0; max-height: 400px; overflow-y: auto;">
                        ${rankings.map((player, index) => `
                            <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.8rem; border-bottom: 1px solid rgba(255,255,255,0.1);">
                                <div style="display: flex; align-items: center; gap: 0.5rem;">
                                    <span style="font-size: 1.2rem; font-weight: bold; width: 40px;">${index + 1}º</span>
                                    <span style="font-size: 1.5rem;">${Utils.getAvatarEmoji(player.avatar)}</span>
                                    <span>${Utils.escapeHtml(player.playerName)}</span>
                                </div>
                                <span style="color: #ff6b6b; font-weight: bold; font-size: 1.2rem;">${player.totalScore || 0} pts</span>
                            </div>
                        `).join('')}
                    </div>
                    <button id="closeFinalRankingBtn" class="btn btn-primary btn-large" style="margin-top: 1rem;">Fechar</button>
                </div>
            `;
            
            document.body.appendChild(modal);
            
            const closeBtn = modal.querySelector('#closeFinalRankingBtn');
            closeBtn.addEventListener('click', () => {
                modal.remove();
                resolve();
            });
            
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    modal.remove();
                    resolve();
                }
            });
        });
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
        if (this.readingTimer) clearTimeout(this.readingTimer);
        if (this.answerTimer) clearInterval(this.answerTimer);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.hostManager = new HostManager();
    window.addEventListener('beforeunload', () => { if (window.hostManager) window.hostManager.cleanup(); });
});