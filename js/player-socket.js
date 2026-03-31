// Player - Tela do Aluno - Versão Socket.IO
class PlayerSocketManager {
    constructor() {
        this.roomCode = null;
        this.roomId = null;
        this.playerId = null;
        this.playerName = null;
        this.playerAvatar = null;
        this.currentQuestion = null;
        this.questionStartTime = null;
        this.hasAnswered = false;
        this.totalScore = 0;
        this.correctStreak = 0;          // Sequência de acertos consecutivos
        this.currentScreen = 'joinScreen';
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
        this.setupSocketListeners();
        this.createAllScreens();
        this.updatePlayerInfoDisplay();   // Atualiza nome/avatar na tela
    }

    createAllScreens() {
        this.createReadingScreen();
        this.createRankingScreen();
    }

    updatePlayerInfoDisplay() {
        // Atualiza nome e avatar no topo da tela (se os elementos existirem)
        const playerNameElem = document.getElementById('playerNameDisplay');
        const playerAvatarElem = document.getElementById('playerAvatarDisplay');
        if (playerNameElem) playerNameElem.textContent = this.playerName || '---';
        if (playerAvatarElem) playerAvatarElem.innerHTML = Utils.getAvatarEmoji(this.playerAvatar) || '👤';
        
        // Atualiza a pontuação
        const currentScoreElem = document.getElementById('currentScore');
        if (currentScoreElem) currentScoreElem.textContent = this.totalScore;
        
        // Atualiza sequência de acertos
        this.updateStreakDisplay();
    }

    updateStreakDisplay() {
        const streakElem = document.getElementById('streakDisplay');
        if (streakElem) {
            if (this.correctStreak > 0) {
                streakElem.innerHTML = '🔥'.repeat(Math.min(this.correctStreak, 5));
                streakElem.style.display = 'inline-block';
            } else {
                streakElem.innerHTML = '';
                streakElem.style.display = 'none';
            }
        }
    }

    setupSocketListeners() {
        if (!window.socketClient) {
            console.error('❌ Socket client não disponível');
            return;
        }

        socketClient.on('reading-phase', (data) => {
            console.log('📖 Fase de leitura:', data);
            this.handleReadingPhase(data);
        });

        socketClient.on('answering-phase', (data) => {
            console.log('⚡ Fase de respostas:', data);
            this.handleAnsweringPhase(data);
        });

        socketClient.on('question-result', (data) => {
            console.log('🏆 Resultado da pergunta:', data);
            this.handleQuestionResult(data);
        });

        socketClient.on('ranking-update', (data) => {
            console.log('📊 Ranking atualizado:', data);
            this.updateRanking(data.ranking);
        });

        socketClient.on('game-finished', (data) => {
            console.log('🏁 Jogo finalizado:', data);
            this.showFinalRanking(data.ranking);
        });

        socketClient.on('score-update', (data) => {
            console.log('💰 Pontuação atualizada:', data);
            if (data.playerId === this.playerId) {
                this.totalScore = data.totalScore;
                this.updatePlayerInfoDisplay();
            }
        });

        socketClient.on('error', (data) => {
            Utils.showToast(data.message, 'error');
        });
    }

    setupEventListeners() {
        const checkRoomBtn = document.getElementById('checkRoomBtn');
        if (checkRoomBtn) checkRoomBtn.addEventListener('click', () => this.checkRoom());
        
        const joinGameBtn = document.getElementById('joinGameBtn');
        if (joinGameBtn) joinGameBtn.addEventListener('click', () => this.joinGame());
        
        const exitGameBtn = document.getElementById('exitGameBtn');
        if (exitGameBtn) exitGameBtn.addEventListener('click', () => window.location.href = 'index.html');
        
        const roomCodeInput = document.getElementById('roomCodeInput');
        if (roomCodeInput) roomCodeInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.checkRoom();
        });
        
        const playerNameInput = document.getElementById('playerName');
        if (playerNameInput) playerNameInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.joinGame();
        });
    }

    loadAvatars() {
        const avatars = [
            { id: 'avatar1', emoji: '🐱', name: 'Gato' },
            { id: 'avatar2', emoji: '🐶', name: 'Cachorro' },
            { id: 'avatar3', emoji: '🦊', name: 'Raposa' },
            { id: 'avatar4', emoji: '🐼', name: 'Panda' },
            { id: 'avatar5', emoji: '🐨', name: 'Koala' },
            { id: 'avatar6', emoji: '🐸', name: 'Sapo' },
            { id: 'avatar7', emoji: '🐙', name: 'Polvo' },
            { id: 'avatar8', emoji: '🦄', name: 'Unicórnio' }
        ];
        
        const grid = document.getElementById('avatarsGrid');
        if (!grid) return;
        
        grid.innerHTML = avatars.map(avatar => `
            <div class="avatar-option" data-avatar="${avatar.id}">
                <div class="avatar-emoji">${avatar.emoji}</div>
                <div class="avatar-name">${avatar.name}</div>
            </div>
        `).join('');
        
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
                this.updatePlayerInfoDisplay();
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
        
        if (!window.socketClient || !window.socketClient.connected) {
            Utils.showToast('Aguardando conexão com o servidor...', 'warning');
            const checkConnection = setInterval(() => {
                if (window.socketClient && window.socketClient.connected) {
                    clearInterval(checkConnection);
                    this.doCheckRoom(code);
                }
            }, 100);
            setTimeout(() => clearInterval(checkConnection), 5000);
            return;
        }
        
        this.doCheckRoom(code);
    }
    
    doCheckRoom(code) {
        socketClient.checkRoom(code, (response) => {
            if (response && response.exists) {
                this.roomCode = code;
                this.roomId = response.roomId;
                this.showScreen('profileScreen');
            } else {
                Utils.showToast('Sala não encontrada ou já encerrada', 'error');
            }
        });
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
        this.updatePlayerInfoDisplay();
        
        if (!window.socketClient || !window.socketClient.connected) {
            Utils.showToast('Aguardando conexão com o servidor...', 'warning');
            const checkConnection = setInterval(() => {
                if (window.socketClient && window.socketClient.connected) {
                    clearInterval(checkConnection);
                    this.doJoinGame();
                }
            }, 100);
            setTimeout(() => clearInterval(checkConnection), 5000);
            return;
        }
        
        this.doJoinGame();
    }
    
    doJoinGame() {
        socketClient.joinRoom(this.roomCode, this.playerId, this.playerName, this.playerAvatar, (response) => {
            if (response && response.success) {
                this.roomId = response.roomId;
                this.showScreen('waitingScreen');
                document.getElementById('waitingRoomCode').textContent = this.roomCode;
                Utils.showToast('Entrou na sala! Aguardando o início do jogo...', 'success');
            } else {
                Utils.showToast(response?.error || 'Erro ao entrar na sala', 'error');
            }
        });
    }

    handleReadingPhase(data) {
        if (this.currentScreen === 'questionScreen') return;
        
        this.currentQuestion = data.question;
        this.hasAnswered = false;
        
        this.showScreen('readingScreen');
        
        const readingTextElem = document.getElementById('readingQuestionText');
        if (readingTextElem) {
            readingTextElem.textContent = this.currentQuestion.text;
        }
        
        let timeLeft = data.readingTime || 5;
        const timerSpan = document.getElementById('readingTimer');
        if (timerSpan) timerSpan.textContent = timeLeft;
        
        if (this.readingTimer) clearInterval(this.readingTimer);
        this.readingTimer = setInterval(() => {
            timeLeft--;
            if (timerSpan) timerSpan.textContent = Math.max(0, timeLeft);
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
                        <p>Segundos para ler</p>
                    </div>
                </div>
            </div>
        `;
        
        const container = document.querySelector('.player-container');
        container.insertAdjacentHTML('beforeend', readingHTML);
    }

    createRankingScreen() {
        if (document.getElementById('rankingScreen')) return;
        
        const rankingHTML = `
            <div id="rankingScreen" class="player-screen">
                <div class="ranking-card">
                    <h2>🏆 Ranking Parcial 🏆</h2>
                    <div id="rankingModalList" class="ranking-list-modal"></div>
                    <div class="next-question-timer">
                        Aguardando próxima pergunta...
                    </div>
                </div>
            </div>
        `;
        
        const container = document.querySelector('.player-container');
        container.insertAdjacentHTML('beforeend', rankingHTML);
    }

    handleAnsweringPhase(data) {
        if (this.currentScreen === 'questionScreen') return;
        
        if (!this.currentQuestion) {
            console.warn('⚠️ Nenhuma pergunta atual para responder');
            return;
        }
        
        this.currentQuestion.options = data.options;
        this.currentQuestion.timeLimit = data.timeLimit;
        
        this.questionStartTime = new Date();
        this.hasAnswered = false;
        
        if (this.readingTimer) clearInterval(this.readingTimer);
        if (this.answerTimer) clearInterval(this.answerTimer);
        
        this.showScreen('questionScreen');
        this.displayQuestion();
        this.startQuestionTimer();
    }

    displayQuestion() {
        const questionTextElem = document.getElementById('questionText');
        if (questionTextElem) {
            questionTextElem.textContent = this.currentQuestion.text;
        }
        
        const optionsGrid = document.getElementById('optionsGrid');
        if (!optionsGrid) return;
        
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
            if (timeLeft <= 5 && timerCircle) {
                timerCircle.style.animation = 'pulse 0.5s infinite';
            }
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
        
        if (window.socketClient && window.socketClient.connected) {
            socketClient.submitAnswer(selectedOption, responseTime, (result) => {
                if (result && result.success) {
                    this.totalScore += result.points;
                    // Atualiza sequência de acertos
                    if (result.isCorrect) {
                        this.correctStreak++;
                    } else {
                        this.correctStreak = 0;
                    }
                    this.updatePlayerInfoDisplay();
                    this.showQuestionFeedback(result.isCorrect, result.points);
                } else if (result && result.error) {
                    Utils.showToast(result.error, 'error');
                }
            });
        } else {
            Utils.showToast('Conexão perdida com o servidor', 'error');
        }
        
        // Desabilitar opções
        document.querySelectorAll('.option-btn').forEach(btn => {
            btn.disabled = true;
            btn.classList.add('disabled');
        });
    }

    showQuestionFeedback(isCorrect, points) {
        const feedbackDiv = document.getElementById('feedbackMessage');
        const resultIcon = isCorrect ? '✅' : '❌';
        const message = isCorrect 
            ? `Correto! +${points} pontos!` 
            : `Errou! 0 pontos`;
        
        if (feedbackDiv) {
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
    }

    handleQuestionResult(data) {
        // Atualizar pontuação com o valor final (pode ter vindo do servidor)
        const myResult = data.results?.find(r => r.playerId === this.playerId);
        if (myResult) {
            this.totalScore = myResult.totalScore;
            // Atualizar sequência de acertos com o resultado final
            this.correctStreak = myResult.isCorrect ? this.correctStreak : 0;
            this.updatePlayerInfoDisplay();
        }
        
        // Mostrar ranking
        this.showRankingModal(data.ranking);
        
        // Voltar para tela de espera após 3 segundos
        setTimeout(() => {
            this.showScreen('waitingScreen');
        }, 3000);
    }

    showRankingModal(ranking) {
        const topRanking = ranking?.slice(0, 5) || [];
        
        const existingModal = document.querySelector('.ranking-modal');
        if (existingModal) existingModal.remove();
        
        const modal = document.createElement('div');
        modal.className = 'modal ranking-modal';
        modal.style.display = 'block';
        modal.innerHTML = `
            <div class="modal-content" style="max-width: 500px; text-align: center;">
                <h2 style="color: #ff6b6b; margin-bottom: 1rem;">🏆 Ranking Parcial 🏆</h2>
                <div style="margin: 1rem 0; max-height: 300px; overflow-y: auto;">
                    ${topRanking.map((player, index) => `
                        <div style="display: flex; justify-content: space-between; padding: 0.8rem; border-bottom: 1px solid rgba(255,255,255,0.1);">
                            <span style="font-weight: bold; font-size: 1.2rem;">${index + 1}º</span>
                            <span>${Utils.escapeHtml(player.playerName)}</span>
                            <span style="color: #ff6b6b; font-weight: bold;">${player.score || 0} pts</span>
                        </div>
                    `).join('')}
                </div>
                <button id="closeRankingBtn" class="btn btn-primary" style="margin-top: 1rem;">Continuar</button>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        const closeBtn = modal.querySelector('#closeRankingBtn');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                modal.remove();
            });
        }
        
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
    }

    updateRanking(ranking) {
        const rankingList = document.getElementById('finalRankingList');
        if (rankingList && this.currentScreen === 'finalScreen') {
            this.updateFinalRanking(ranking);
        }
        
        const modalList = document.getElementById('rankingModalList');
        if (modalList && this.currentScreen === 'rankingScreen') {
            const topRanking = ranking?.slice(0, 5) || [];
            modalList.innerHTML = topRanking.map((player, index) => `
                <div class="ranking-item ${player.playerId === this.playerId ? 'current-player' : ''}">
                    <div class="ranking-position">${index + 1}º</div>
                    <div class="player-info">
                        <span>${Utils.escapeHtml(player.playerName)}</span>
                    </div>
                    <div class="ranking-score">${player.score || 0} pts</div>
                </div>
            `).join('');
        }
    }

    showFinalRanking(ranking) {
        this.showScreen('finalScreen');
        this.updateFinalRanking(ranking);
    }

    updateFinalRanking(ranking) {
        const list = document.getElementById('finalRankingList');
        if (!list) return;
        
        if (!ranking || ranking.length === 0) {
            list.innerHTML = '<p class="placeholder">Nenhum jogador</p>';
            return;
        }
        
        list.innerHTML = ranking.map((player, index) => `
            <div class="ranking-item ${player.playerId === this.playerId ? 'current-player' : ''}">
                <div class="ranking-position">${index + 1}º</div>
                <div class="player-info">
                    <span>${Utils.escapeHtml(player.playerName)}</span>
                </div>
                <div class="ranking-score">${player.score || 0} pts</div>
            </div>
        `).join('');
    }

    showScreen(screenId) {
        this.currentScreen = screenId;
        const screens = document.querySelectorAll('.player-screen');
        screens.forEach(screen => screen.classList.remove('active'));
        const targetScreen = document.getElementById(screenId);
        if (targetScreen) {
            targetScreen.classList.add('active');
            console.log(`🖥️ Tela alterada para: ${screenId}`);
        } else {
            console.warn(`⚠️ Tela não encontrada: ${screenId}`);
        }
    }

    cleanup() {
        if (this.readingTimer) clearInterval(this.readingTimer);
        if (this.answerTimer) clearInterval(this.answerTimer);
        const modal = document.querySelector('.ranking-modal');
        if (modal) modal.remove();
    }
}

// Inicializar
document.addEventListener('DOMContentLoaded', () => {
    console.log('🎮 Inicializando PlayerSocketManager...');
    window.playerManager = new PlayerSocketManager();
    window.addEventListener('beforeunload', () => {
        if (window.playerManager) window.playerManager.cleanup();
    });
});