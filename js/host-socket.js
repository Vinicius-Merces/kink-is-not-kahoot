// Painel do Professor - Versão Socket.IO
class HostSocketManager {
    constructor() {
        this.roomId = null;
        this.roomCode = null;
        this.quiz = null;
        this.players = [];
        this.ranking = [];
        this.currentQuestionIndex = 0;
        this.currentQuestion = null;
        this.status = 'waiting';
        this.timerInterval = null;
        this.init();
    }

    async init() {
        // Pegar roomId da URL
        const urlParams = new URLSearchParams(window.location.search);
        this.roomId = urlParams.get('room');
        
        if (!this.roomId) {
            Utils.showToast('Sala não encontrada', 'error');
            setTimeout(() => window.location.href = 'my-quizzes.html', 2000);
            return;
        }

        // Aguardar autenticação
        auth.onAuthStateChanged(async (user) => {
            if (!user) {
                window.location.href = 'index.html';
                return;
            }

            // Aguardar socket client estar pronto
            if (window.socketClient && window.socketClient.connected) {
                this.setupSocketListeners();
                this.requestRoomState();
            } else {
                // Aguardar conexão do socket
                const checkConnection = setInterval(() => {
                    if (window.socketClient && window.socketClient.connected) {
                        clearInterval(checkConnection);
                        this.setupSocketListeners();
                        this.requestRoomState();
                    }
                }, 100);
            }
        });
    }

    requestRoomState() {
        socketClient.emit('get-room-state', { roomId: this.roomId }, (response) => {
            if (response && response.success) {
                this.roomCode = response.roomCode;
                this.quiz = response.quiz;
                this.players = response.players || [];
                this.ranking = response.ranking || [];
                this.updateUI();
                this.updatePlayersList();
                this.updateRanking();
            } else {
                Utils.showToast('Erro ao carregar estado da sala', 'error');
            }
        });
    }

    setupSocketListeners() {
        // Confirmar que entrou na sala
        socketClient.on('room-joined', (data) => {
            console.log('🏠 Conectado à sala:', data);
            this.roomCode = data.roomCode;
            this.quiz = data.quiz;
            this.players = data.players || [];
            this.updateUI();
            this.updatePlayersList();
        });

        // Jogador entrou
        socketClient.on('player-joined', (data) => {
            this.players = data.players;
            this.updatePlayersList();
            Utils.showToast(`${data.playerName || 'Um jogador'} entrou na sala!`, 'info');
        });

        // Jogador saiu
        socketClient.on('player-left', (data) => {
            this.players = data.players;
            this.updatePlayersList();
        });

        // Quiz iniciado
        socketClient.on('quiz-started', (data) => {
            this.status = 'active';
            Utils.showToast(`Quiz iniciado! ${data.totalPlayers} jogadores participando.`, 'success');
            document.getElementById('startGameBtn').style.display = 'none';
            document.getElementById('questionControls').style.display = 'block';
        });

        // Fase de leitura
        socketClient.on('reading-phase', (data) => {
            this.status = 'reading';
            this.currentQuestion = data.question;
            this.updateReadingPhase();
        });

        // Fase de respostas
        socketClient.on('answering-phase', (data) => {
            this.status = 'answering';
            this.updateAnsweringPhase(data);
        });

        // Resultado da pergunta
        socketClient.on('question-result', (data) => {
            this.ranking = data.ranking;
            this.updateRanking();
            this.showRankingModal(data);
            
            // Atualizar estatísticas
            const totalAnswers = data.results?.length || 0;
            const correctAnswers = data.results?.filter(r => r.isCorrect).length || 0;
            const accuracy = totalAnswers > 0 ? (correctAnswers / totalAnswers * 100).toFixed(1) : 0;
            
            document.getElementById('answersCount').textContent = totalAnswers;
            document.getElementById('accuracyRate').textContent = `${accuracy}%`;
        });

        // Jogo finalizado
        socketClient.on('game-finished', (data) => {
            this.showFinalRanking(data.ranking);
        });

        // Atualização de ranking (tempo real)
        socketClient.on('ranking-update', (data) => {
            this.ranking = data.ranking;
            this.updateRanking();
        });

        // Erro
        socketClient.on('error', (data) => {
            Utils.showToast(data.message, 'error');
        });
    }

    updateUI() {
        // Exibir código da sala
        const roomCodeElem = document.getElementById('roomCode');
        if (roomCodeElem && this.roomCode) {
            roomCodeElem.textContent = this.roomCode;
        } else if (roomCodeElem && this.roomId) {
            roomCodeElem.textContent = this.roomId.substring(0, 6).toUpperCase();
        }

        // Exibir informações do quiz
        const quizInfoElem = document.getElementById('quizInfo');
        if (quizInfoElem && this.quiz) {
            quizInfoElem.innerHTML = `<strong>Quiz:</strong> ${this.quiz.title || 'Carregando...'} | <strong>Perguntas:</strong> ${this.quiz.questions?.length || 0}`;
        }
        
        // Botões
        const copyBtn = document.getElementById('copyCodeBtn');
        if (copyBtn) {
            copyBtn.addEventListener('click', () => {
                const code = this.roomCode || this.roomId?.substring(0, 6).toUpperCase() || '';
                navigator.clipboard.writeText(code);
                Utils.showToast('Código copiado!', 'success');
            });
        }
        
        const shareBtn = document.getElementById('shareRoomBtn');
        if (shareBtn) {
            shareBtn.addEventListener('click', () => {
                const code = this.roomCode || this.roomId?.substring(0, 6).toUpperCase() || '';
                const url = `${window.location.origin}/player.html?code=${code}`;
                navigator.clipboard.writeText(url);
                Utils.showToast('Link copiado! Compartilhe com seus alunos', 'success');
            });
        }
        
        const startGameBtn = document.getElementById('startGameBtn');
        if (startGameBtn) {
            startGameBtn.addEventListener('click', () => {
                socketClient.startQuiz((response) => {
                    if (!response || !response.success) {
                        Utils.showToast(response?.error || 'Erro ao iniciar quiz', 'error');
                    }
                });
            });
        }
        
        const startQuestionBtn = document.getElementById('startQuestionBtn');
        if (startQuestionBtn) {
            startQuestionBtn.addEventListener('click', () => {
                socketClient.startQuestion((response) => {
                    if (!response || !response.success) {
                        if (response?.finished) {
                            Utils.showToast('Quiz finalizado!', 'info');
                        } else {
                            Utils.showToast(response?.error || 'Erro ao iniciar pergunta', 'error');
                        }
                    }
                });
            });
        }
        
        const nextQuestionBtn = document.getElementById('nextQuestionBtn');
        if (nextQuestionBtn) {
            nextQuestionBtn.addEventListener('click', () => {
                socketClient.nextQuestion((response) => {
                    if (response && response.finished) {
                        this.endGame();
                    }
                });
            });
        }
        
        const endGameBtn = document.getElementById('endGameBtn');
        if (endGameBtn) {
            endGameBtn.addEventListener('click', () => {
                if (confirm('Tem certeza que deseja encerrar o quiz?')) {
                    socketClient.endGame();
                }
            });
        }
    }

    updatePlayersList() {
        const list = document.getElementById('playersList');
        const count = document.getElementById('playersCount');
        
        if (!list) return;
        
        if (!this.players || this.players.length === 0) {
            list.innerHTML = '<p class="placeholder">Aguardando jogadores...</p>';
            if (count) count.textContent = '0';
            return;
        }
        
        list.innerHTML = this.players.map(player => `
            <div class="player-item">
                <div class="player-info">
                    <span class="player-avatar">${Utils.getAvatarEmoji(player.avatar)}</span>
                    <span>${Utils.escapeHtml(player.name)}</span>
                </div>
                <div class="player-score">${player.score || 0} pts</div>
            </div>
        `).join('');
        
        if (count) count.textContent = this.players.length;
    }

    updateRanking() {
        const list = document.getElementById('rankingList');
        if (!list) return;
        
        if (!this.ranking || this.ranking.length === 0) {
            list.innerHTML = '<p class="placeholder">Aguardando respostas...</p>';
            return;
        }
        
        list.innerHTML = this.ranking.slice(0, 10).map((player, index) => `
            <div class="ranking-item">
                <div class="ranking-position">${index + 1}º</div>
                <div class="player-info">
                    <span>${Utils.escapeHtml(player.playerName)}</span>
                </div>
                <div class="ranking-score">${player.score || 0} pts</div>
            </div>
        `).join('');
    }

    updateReadingPhase() {
        const display = document.getElementById('currentQuestionDisplay');
        if (!display) return;
        
        display.innerHTML = `
            <div class="current-question" style="background: rgba(78, 205, 196, 0.2);">
                <strong>📖 Leia a pergunta (5s)</strong>
                <p style="font-size: 1.2rem; margin-top: 1rem;">${Utils.escapeHtml(this.currentQuestion?.text || '')}</p>
                <small>As opções aparecerão em breve...</small>
            </div>
        `;
        
        const timerDisplay = document.getElementById('questionTimer');
        if (timerDisplay) timerDisplay.style.display = 'none';
        
        const startBtn = document.getElementById('startQuestionBtn');
        const nextBtn = document.getElementById('nextQuestionBtn');
        if (startBtn) startBtn.style.display = 'none';
        if (nextBtn) nextBtn.style.display = 'none';
    }

    updateAnsweringPhase(data) {
        const display = document.getElementById('currentQuestionDisplay');
        if (!display) return;
        
        display.innerHTML = `
            <div class="current-question">
                <strong>⚡ Responda agora!</strong>
                <p>${Utils.escapeHtml(this.currentQuestion?.text || '')}</p>
                <small>Tempo limite: ${data.timeLimit}s</small>
            </div>
        `;
        
        this.startTimer(data.timeLimit);
        
        const startBtn = document.getElementById('startQuestionBtn');
        const nextBtn = document.getElementById('nextQuestionBtn');
        if (startBtn) startBtn.style.display = 'none';
        if (nextBtn) nextBtn.style.display = 'block';
    }

    startTimer(limit) {
        const timerDisplay = document.getElementById('questionTimer');
        const timerSeconds = document.getElementById('timerSeconds');
        const timerBar = document.querySelector('.timer-bar');
        
        if (timerDisplay) timerDisplay.style.display = 'block';
        
        let timeLeft = limit;
        if (timerSeconds) timerSeconds.textContent = timeLeft;
        if (timerBar) timerBar.style.width = '100%';
        
        if (this.timerInterval) clearInterval(this.timerInterval);
        
        this.timerInterval = setInterval(() => {
            timeLeft--;
            if (timerSeconds) timerSeconds.textContent = Math.max(0, timeLeft);
            if (timerBar) timerBar.style.width = `${Math.max(0, (timeLeft / limit) * 100)}%`;
            if (timeLeft <= 0) {
                clearInterval(this.timerInterval);
            }
        }, 1000);
    }

    showRankingModal(data) {
        const ranking = data.ranking?.slice(0, 5) || [];
        
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.style.display = 'block';
        modal.innerHTML = `
            <div class="modal-content" style="max-width: 500px; text-align: center;">
                <h2 style="color: #ff6b6b; margin-bottom: 1rem;">🏆 Ranking Parcial 🏆</h2>
                <div style="margin: 1rem 0;">
                    ${ranking.map((player, index) => `
                        <div style="display: flex; justify-content: space-between; padding: 0.8rem; border-bottom: 1px solid rgba(255,255,255,0.1);">
                            <span style="font-weight: bold; font-size: 1.2rem;">${index + 1}º</span>
                            <span>${Utils.escapeHtml(player.playerName)}</span>
                            <span style="color: #ff6b6b; font-weight: bold;">${player.score || 0} pts</span>
                        </div>
                    `).join('')}
                </div>
                <div style="margin: 1rem 0; font-size: 0.9rem; opacity: 0.7;">
                    Resposta correta: ${data.correctAnswer || 'Não disponível'}
                </div>
                <button id="closeRankingBtn" class="btn btn-primary" style="margin-top: 1rem;">Continuar</button>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        const closeBtn = modal.querySelector('#closeRankingBtn');
        closeBtn.addEventListener('click', () => {
            modal.remove();
        });
        
        // Fechar ao clicar fora
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
    }

    showFinalRanking(ranking) {
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.style.display = 'block';
        modal.innerHTML = `
            <div class="modal-content" style="max-width: 500px; text-align: center;">
                <h2 style="color: #ff6b6b; margin-bottom: 1rem;">🏆 Ranking Final 🏆</h2>
                <div style="margin: 1rem 0; max-height: 400px; overflow-y: auto;">
                    ${ranking.map((player, index) => `
                        <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.8rem; border-bottom: 1px solid rgba(255,255,255,0.1);">
                            <div style="display: flex; align-items: center; gap: 0.5rem;">
                                <span style="font-size: 1.2rem; font-weight: bold; width: 40px;">${index + 1}º</span>
                                <span>${Utils.escapeHtml(player.playerName)}</span>
                            </div>
                            <span style="color: #ff6b6b; font-weight: bold; font-size: 1.2rem;">${player.score || 0} pts</span>
                        </div>
                    `).join('')}
                </div>
                <button id="closeFinalRankingBtn" class="btn btn-primary" style="margin-top: 1rem;">Fechar</button>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        const closeBtn = modal.querySelector('#closeFinalRankingBtn');
        closeBtn.addEventListener('click', () => {
            modal.remove();
            window.location.href = 'my-quizzes.html';
        });
        
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
                window.location.href = 'my-quizzes.html';
            }
        });
    }

    endGame() {
        const startBtn = document.getElementById('startQuestionBtn');
        const nextBtn = document.getElementById('nextQuestionBtn');
        const gameBtn = document.getElementById('startGameBtn');
        const endBtn = document.getElementById('endGameBtn');
        
        if (startBtn) startBtn.style.display = 'none';
        if (nextBtn) nextBtn.style.display = 'none';
        if (gameBtn) gameBtn.style.display = 'none';
        if (endBtn) endBtn.style.display = 'none';
        
        Utils.showToast('Quiz finalizado!', 'success');
    }

    cleanup() {
        if (this.timerInterval) clearInterval(this.timerInterval);
    }
}

// Inicializar quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', () => {
    window.hostManager = new HostSocketManager();
    window.addEventListener('beforeunload', () => {
        if (window.hostManager) window.hostManager.cleanup();
    });
});