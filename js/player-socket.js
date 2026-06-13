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
        this.correctStreak = 0;
        this.currentScreen = 'joinScreen';
        this.readingTimer = null;
        this.answerTimer = null;
        this.correctCount = 1; // ✅ NOVO: quantas respostas a pergunta atual exige
        this.selectedOptions = new Set(); // ✅ NOVO: seleção em perguntas de múltipla escolha
        this.roomType = 'quiz'; // 'quiz' ou 'simulado' (modo professor ao vivo)
        this.simuladoVoted = false;
        this.simuladoCurrentIndex = null;
        this.simuladoTotalQuestions = null;
        this.simuladoCertCode = null;
        this.simuladoLevel = null;
        this.simuladoCurrentQuestion = null;
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
        this.createPlayerHeader();
        this.updatePlayerInfoDisplay();
    }

    createPlayerHeader() {
        if (document.getElementById('playerHeader')) return;

        const headerHTML = `
            <div id="playerHeader" style="position:fixed;top:0;left:0;right:0;background:rgba(15,15,15,0.95);padding:12px 20px;display:flex;align-items:center;justify-content:space-between;z-index:9999;border-bottom:2px solid #ff6b6b;box-shadow:0 2px 10px rgba(0,0,0,0.5);">
                <div style="display:flex;align-items:center;gap:12px;">
                    <span id="playerHeaderAvatar" style="font-size:2rem;"></span>
                    <div>
                        <div id="playerHeaderName" style="font-weight:700;font-size:1.1rem;"></div>
                        <div id="playerHeaderScore" style="color:#ff6b6b;font-size:1.25rem;font-weight:bold;">0 pts</div>
                    </div>
                </div>
                <div id="playerStreak" style="font-size:2rem;display:flex;align-items:center;gap:4px;"></div>
            </div>`;

        document.body.insertAdjacentHTML('afterbegin', headerHTML);
    }

    updatePlayerInfoDisplay() {
        const avatarElem = document.getElementById('playerHeaderAvatar');
        const nameElem = document.getElementById('playerHeaderName');
        const scoreElem = document.getElementById('playerHeaderScore');
        const streakElem = document.getElementById('playerStreak');
        
        if (avatarElem) avatarElem.textContent = Utils.getAvatarEmoji(this.playerAvatar) || '👤';
        if (nameElem) nameElem.textContent = this.playerName || '---';
        if (scoreElem) scoreElem.textContent = `${this.totalScore} pts`;
        
        if (streakElem) {
            if (this.correctStreak >= 2) {
                streakElem.innerHTML = '🔥'.repeat(Math.min(this.correctStreak, 6)) + ` <span style="font-size:1.1rem;">${this.correctStreak}x</span>`;
            } else {
                streakElem.textContent = '';
            }
        }
    }

    createAllScreens() {
        this.createReadingScreen();
        this.createRankingScreen();
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

        socketClient.on('error', (data) => {
            Utils.showToast(data.message, 'error');
        });

        // ============================================
        // Simulado Modo Professor (votação ao vivo)
        // ============================================

        socketClient.on('simulado:question', (data) => {
            console.log('📝 Pergunta do simulado ao vivo:', data);
            this.handleSimuladoQuestion(data);
        });

        socketClient.on('simulado:vote-progress', (data) => {
            this.updateSimuladoVoteProgress(data);
        });

        socketClient.on('simulado:vote-closed', (data) => {
            console.log('📊 Votação encerrada:', data);
            this.handleSimuladoVoteClosed(data);
        });

        socketClient.on('simulado:player-joined', (data) => {
            this.updateWaitingPlayersList(data.players);
        });

        socketClient.on('simulado:player-left', (data) => {
            this.updateWaitingPlayersList(data.players);
        });

        socketClient.on('simulado:session-finished', () => {
            console.log('🏁 Simulado ao vivo encerrado');
            this.showScreen('simuladoFinalScreen');
        });
    }

    setupEventListeners() {
        const checkRoomBtn = document.getElementById('checkRoomBtn');
        if (checkRoomBtn) checkRoomBtn.addEventListener('click', () => this.checkRoom());
        
        const joinGameBtn = document.getElementById('joinGameBtn');
        if (joinGameBtn) joinGameBtn.addEventListener('click', () => this.joinGame());
        
        const exitGameBtn = document.getElementById('exitGameBtn');
        if (exitGameBtn) exitGameBtn.addEventListener('click', () => window.location.href = 'index.html');

        const exitSimuladoBtn = document.getElementById('exitSimuladoBtn');
        if (exitSimuladoBtn) exitSimuladoBtn.addEventListener('click', () => window.location.href = 'index.html');

        const simuladoReportBtn = document.getElementById('simuladoReportBtn');
        if (simuladoReportBtn) simuladoReportBtn.addEventListener('click', () => {
            if (!this.simuladoCurrentQuestion) return;
            const data = this.simuladoCurrentQuestion;
            window.ReportQuestion.open({
                source: 'live-player',
                certCode: this.simuladoCertCode,
                level: this.simuladoLevel,
                domain: data.domain,
                questionIndex: data.index,
                questionText: data.text,
                options: data.options,
                reporterName: this.playerName
            });
        });

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
            <div class="avatar-option" data-avatar="${avatar.id}" role="button" tabindex="0" aria-pressed="false" aria-label="Avatar ${avatar.name}">
                <div class="avatar-emoji" aria-hidden="true">${avatar.emoji}</div>
                <div class="avatar-name">${avatar.name}</div>
            </div>
        `).join('');

        const firstAvatar = document.querySelector('.avatar-option');
        if (firstAvatar) {
            firstAvatar.classList.add('selected');
            firstAvatar.setAttribute('aria-pressed', 'true');
            this.playerAvatar = 'avatar1';
        }

        document.querySelectorAll('.avatar-option').forEach(option => {
            const selectAvatar = () => {
                document.querySelectorAll('.avatar-option').forEach(opt => {
                    opt.classList.remove('selected');
                    opt.setAttribute('aria-pressed', 'false');
                });
                option.classList.add('selected');
                option.setAttribute('aria-pressed', 'true');
                this.playerAvatar = option.dataset.avatar;
                this.updatePlayerInfoDisplay();
            };
            option.addEventListener('click', selectAvatar);
            option.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    selectAvatar();
                }
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
                this.roomType = response.type || 'quiz';
                this.simuladoTotalQuestions = response.totalQuestions || null;

                const infoElem = document.getElementById('profileRoomInfo');
                if (infoElem) {
                    if (this.roomType === 'simulado') {
                        infoElem.textContent = `📝 Simulado ao vivo: ${response.certName || response.certCode} • ${response.totalQuestions} perguntas`;
                        infoElem.style.display = 'block';
                    } else {
                        infoElem.style.display = 'none';
                    }
                }

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
        if (this.roomType === 'simulado') {
            socketClient.joinLiveSimuladoRoom(this.roomCode, this.playerId, this.playerName, this.playerAvatar, (response) => {
                if (response && response.success) {
                    this.roomId = response.roomId;
                    this.simuladoTotalQuestions = response.totalQuestions;
                    this.simuladoCertCode = response.certCode;
                    this.simuladoLevel = response.level;
                    this.showSimuladoWaitingScreen();
                    Utils.showToast('Entrou no simulado! Aguardando o professor...', 'success');
                } else {
                    Utils.showToast(response?.error || 'Erro ao entrar no simulado', 'error');
                }
            });
            return;
        }

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

    // ============================================
    // Simulado Modo Professor (votação ao vivo)
    // ============================================

    showSimuladoWaitingScreen() {
        const title = document.getElementById('waitingTitle');
        const subtitle = document.getElementById('waitingSubtitle');
        if (title) title.textContent = 'Aguardando o Professor';
        if (subtitle) subtitle.textContent = 'O simulado vai começar em breve...';
        document.getElementById('waitingRoomCode').textContent = this.roomCode;
        this.showScreen('waitingScreen');
    }

    updateWaitingPlayersList(players) {
        const list = document.getElementById('waitingPlayersList');
        if (!list) return;

        if (!players || players.length === 0) {
            list.innerHTML = '<p class="placeholder">Aguardando alunos...</p>';
            return;
        }

        list.innerHTML = players.map(p => `
            <div class="player-item-mini" role="listitem">
                <span class="player-avatar-mini" aria-hidden="true">${Utils.getAvatarEmoji(p.avatar)}</span>
                <span>${Utils.escapeHtml(p.name)}</span>
            </div>
        `).join('');
    }

    handleSimuladoQuestion(data) {
        this.simuladoCurrentIndex = data.index;
        this.simuladoTotalQuestions = data.total;
        this.simuladoCurrentQuestion = data;
        this.simuladoVoted = false;

        const progressBadge = document.getElementById('simuladoProgressBadge');
        if (progressBadge) progressBadge.textContent = `Pergunta ${data.index + 1} de ${data.total}`;

        const questionTextElem = document.getElementById('simuladoQuestionText');
        if (questionTextElem) questionTextElem.textContent = data.text;

        const optionsGrid = document.getElementById('simuladoOptionsGrid');
        const letters = ['A', 'B', 'C', 'D', 'E', 'F'];
        optionsGrid.innerHTML = data.options.map((option, index) => `
            <button class="option-btn" data-option="${index}" aria-label="Opção ${letters[index]}: ${Utils.escapeHtml(option)}">
                <div class="option-letter" aria-hidden="true">${letters[index]}</div>
                <div class="option-text">${Utils.escapeHtml(option)}</div>
            </button>
        `).join('');
        optionsGrid.style.display = 'grid';

        optionsGrid.querySelectorAll('.option-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                if (!this.simuladoVoted) this.submitSimuladoVote(parseInt(btn.dataset.option, 10));
            });
        });

        const statusElem = document.getElementById('simuladoVoteStatus');
        if (statusElem) statusElem.style.display = 'none';

        const resultsElem = document.getElementById('simuladoResultsContainer');
        if (resultsElem) resultsElem.style.display = 'none';

        this.updateSimuladoVoteProgress({ voted: 0, total: 0 });

        this.showScreen('simuladoVoteScreen');
    }

    submitSimuladoVote(optionIndex) {
        if (this.simuladoVoted) return;
        this.simuladoVoted = true;

        document.querySelectorAll('#simuladoOptionsGrid .option-btn').forEach((btn, index) => {
            btn.disabled = true;
            btn.classList.add('disabled');
            if (index === optionIndex) btn.classList.add('selected');
        });

        const statusElem = document.getElementById('simuladoVoteStatus');
        if (statusElem) {
            statusElem.textContent = '✅ Voto registrado! Aguardando os colegas...';
            statusElem.style.display = 'block';
        }

        socketClient.voteLiveSimulado(optionIndex, (result) => {
            if (!result || !result.success) {
                Utils.showToast(result?.error || 'Erro ao registrar voto', 'error');
                this.simuladoVoted = false;
                document.querySelectorAll('#simuladoOptionsGrid .option-btn').forEach((btn, index) => {
                    btn.disabled = false;
                    btn.classList.remove('disabled');
                    if (index === optionIndex) btn.classList.remove('selected');
                });
                if (statusElem) statusElem.style.display = 'none';
            }
        });
    }

    updateSimuladoVoteProgress(data) {
        if (this.currentScreen !== 'simuladoVoteScreen') return;
        const elem = document.getElementById('simuladoVoteProgress');
        if (elem) elem.textContent = `${data.voted} de ${data.total} votaram`;
    }

    handleSimuladoVoteClosed(data) {
        if (this.currentScreen !== 'simuladoVoteScreen' || data.index !== this.simuladoCurrentIndex) return;

        const optionsGrid = document.getElementById('simuladoOptionsGrid');
        if (optionsGrid) optionsGrid.style.display = 'none';

        const statusElem = document.getElementById('simuladoVoteStatus');
        if (statusElem) statusElem.style.display = 'none';

        const letters = ['A', 'B', 'C', 'D', 'E', 'F'];
        const barsContainer = document.getElementById('simuladoResultsBars');
        if (barsContainer) {
            barsContainer.innerHTML = data.percentages.map((percent, index) => `
                <div class="stat-row">
                    <div class="stat-label">
                        <div class="option-letter">${letters[index]}</div>
                    </div>
                    <div class="stat-bar-wrapper">
                        <div class="stat-bar" style="width: ${percent}%"></div>
                    </div>
                    <div class="stat-count">
                        <span class="count-percent">${percent}%</span>
                    </div>
                </div>
            `).join('');
        }

        const resultsElem = document.getElementById('simuladoResultsContainer');
        if (resultsElem) resultsElem.style.display = 'block';
    }

    handleReadingPhase(data) {
        if (this.currentScreen === 'questionScreen') return;
        
        // ✅ NOVO: Fechar ranking automaticamente
        const rankingModal = document.querySelector('.ranking-modal');
        if (rankingModal) {
            rankingModal.remove();
        }
        
        this.currentQuestion = data.question;
        this.currentQuestion.pointsMultiplier = data.pointsMultiplier || 1;
        this.hasAnswered = false;

        this.showScreen('readingScreen');

        const readingTextElem = document.getElementById('readingQuestionText');
        if (readingTextElem) {
            readingTextElem.textContent = this.currentQuestion.text;
        }

        this.updateMultiplierBadge('readingMultiplierBadge');

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
                    <div style="text-align: center; margin: 0.5rem 0;">
                        <span id="readingMultiplierBadge" class="multiplier-badge" style="display:none;"></span>
                    </div>
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

    // ✅ NOVO: Mostra/esconde o badge "🔥 Vale Nx!" quando a pergunta tem multiplicador > 1
    updateMultiplierBadge(elementId) {
        const badge = document.getElementById(elementId);
        if (!badge) return;

        const multiplier = this.currentQuestion?.pointsMultiplier || 1;
        if (multiplier > 1) {
            badge.textContent = `🔥 Vale ${multiplier}x!`;
            badge.style.display = 'inline-flex';
        } else {
            badge.style.display = 'none';
        }
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

    handleAnsweringPhase(data) {
        if (this.currentScreen === 'questionScreen') return;
        
        if (!this.currentQuestion) {
            console.warn('⚠️ Nenhuma pergunta atual para responder');
            return;
        }
        
        this.currentQuestion.options = data.options;
        this.currentQuestion.timeLimit = data.timeLimit;
        this.currentQuestion.pointsMultiplier = data.pointsMultiplier || 1;
        this.correctCount = data.correctCount || 1;

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

        this.updateMultiplierBadge('questionMultiplierBadge');

        const optionsGrid = document.getElementById('optionsGrid');
        if (!optionsGrid) return;

        const letters = ['A', 'B', 'C', 'D', 'E', 'F'];
        const multiSelect = this.correctCount > 1;
        this.selectedOptions = new Set();

        optionsGrid.innerHTML = this.currentQuestion.options.map((option, index) => `
            <button class="option-btn" data-option="${index}"${multiSelect ? ' role="checkbox" aria-checked="false"' : ''} aria-label="Opção ${letters[index]}: ${Utils.escapeHtml(option)}">
                <div class="option-letter" aria-hidden="true">${letters[index]}</div>
                <div class="option-text">${Utils.escapeHtml(option)}</div>
            </button>
        `).join('');

        const feedbackMessage = document.getElementById('feedbackMessage');

        if (multiSelect) {
            document.querySelectorAll('.option-btn').forEach(btn => {
                btn.addEventListener('click', () => {
                    if (!this.hasAnswered) this.toggleOptionSelection(btn);
                });
            });

            if (feedbackMessage) {
                feedbackMessage.innerHTML = `
                    <p id="multiSelectHint">Selecione ${this.correctCount} respostas (marcadas: 0/${this.correctCount})</p>
                    <button id="confirmAnswerBtn" class="btn btn-primary" disabled>✅ Confirmar Resposta</button>
                `;

                const confirmBtn = document.getElementById('confirmAnswerBtn');
                if (confirmBtn) {
                    confirmBtn.addEventListener('click', () => {
                        if (!this.hasAnswered && this.selectedOptions.size > 0) {
                            this.submitAnswer(Array.from(this.selectedOptions));
                        }
                    });
                }
            }
        } else {
            if (feedbackMessage) feedbackMessage.innerHTML = '';

            document.querySelectorAll('.option-btn').forEach(btn => {
                btn.addEventListener('click', () => {
                    if (!this.hasAnswered) this.submitAnswer(parseInt(btn.dataset.option));
                });
            });
        }
    }

    // ✅ NOVO: Alterna a seleção de uma opção em perguntas de múltipla escolha
    toggleOptionSelection(btn) {
        const index = parseInt(btn.dataset.option);

        if (this.selectedOptions.has(index)) {
            this.selectedOptions.delete(index);
            btn.classList.remove('selected');
            btn.setAttribute('aria-checked', 'false');
        } else {
            this.selectedOptions.add(index);
            btn.classList.add('selected');
            btn.setAttribute('aria-checked', 'true');
        }

        const hint = document.getElementById('multiSelectHint');
        if (hint) {
            hint.textContent = `Selecione ${this.correctCount} respostas (marcadas: ${this.selectedOptions.size}/${this.correctCount})`;
        }

        const confirmBtn = document.getElementById('confirmAnswerBtn');
        if (confirmBtn) {
            confirmBtn.disabled = this.selectedOptions.size === 0;
        }
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

        // ✅ Normaliza para array: número → [número], array → mantém, null/undefined → []
        let answerArr;
        if (Array.isArray(selectedOption)) {
            answerArr = selectedOption;
        } else if (selectedOption === null || selectedOption === undefined) {
            answerArr = [];
        } else {
            answerArr = [selectedOption];
        }

        if (window.socketClient && window.socketClient.connected) {
            socketClient.submitAnswer(answerArr, responseTime, (result) => {
                // Não atualiza UI aqui, aguarda question-result
            });
        } else {
            Utils.showToast('Conexão perdida com o servidor', 'error');
        }

        // Desabilitar opções imediatamente
        document.querySelectorAll('.option-btn').forEach(btn => {
            btn.disabled = true;
            btn.classList.add('disabled');
        });

        const confirmBtn = document.getElementById('confirmAnswerBtn');
        if (confirmBtn) confirmBtn.disabled = true;
    }

    handleQuestionResult(data) {
        // Atualizar pontuação com o valor final do servidor
        const myResult = data.results?.find(r => r.playerId === this.playerId);
        if (myResult) {
            this.totalScore = myResult.totalScore;
            // Atualizar streak com base no resultado
            if (myResult.isCorrect) {
                this.correctStreak++;
            } else {
                this.correctStreak = 0;  // ✅ CORREÇÃO: Resetar streak ao errar
            }
            this.updatePlayerInfoDisplay();
        }

        // ✅ NOVO: Montar feedback (acerto/erro, explicação, resposta correta e distribuição)
        const feedbackHtml = this.buildAnswerFeedbackHtml(data);

        // Mostrar ranking junto com o feedback
        this.showRankingModal(data.ranking, feedbackHtml);

        // Voltar para tela de espera após 4 segundos
        setTimeout(() => {
            this.showScreen('waitingScreen');
        }, 4000);
    }

    // ✅ NOVO: Monta o HTML de feedback (acerto/erro, explicação, resposta correta e distribuição de respostas)
    buildAnswerFeedbackHtml(data) {
        if (!this.currentQuestion) return '';

        const myResult = data.results?.find(r => r.playerId === this.playerId);
        if (!myResult) return '';

        const isCorrect = myResult.isCorrect;
        const points = myResult.points || 0;

        let html = `
            <div class="answer-feedback ${isCorrect ? 'correct' : 'incorrect'}">
                <div class="feedback-icon">${isCorrect ? '✅' : '❌'}</div>
                <div class="feedback-title">
                    ${isCorrect ? 'Resposta Correta!' : 'Resposta Incorreta'}
                </div>
                <div class="feedback-points">
                    ${isCorrect ? `+${points} pontos` : '0 pontos'}
                </div>
        `;

        // ✅ Mostrar explicação se existir
        if (data.explanation) {
            html += `
                <div class="feedback-explanation">
                    <strong>Explicação:</strong><br>
                    ${Utils.escapeHtml(data.explanation)}
                </div>
            `;
        }

        // ✅ Mostrar resposta correta (letra(s))
        html += `
                <div class="feedback-hint">
                    Resposta correta: <strong>${Utils.escapeHtml(data.correctAnswerLabel || '')}</strong>
                </div>
            </div>
        `;

        // ✅ NOVO: Distribuição de respostas (% por opção, destacando a correta e a minha)
        html += this.renderAnswerDistribution(data.stats, myResult.answer);

        return html;
    }

    // ✅ NOVO: Renderiza a distribuição de respostas (% por opção), destacando a correta e a minha
    renderAnswerDistribution(stats, myAnswerIndices) {
        if (!stats || Object.keys(stats).length === 0) return '';

        const letters = ['A', 'B', 'C', 'D', 'E', 'F'];
        const myIndices = Array.isArray(myAnswerIndices) ? myAnswerIndices : [];

        const rows = Object.entries(stats).map(([letter, stat]) => {
            const isMine = myIndices.includes(letters.indexOf(letter));

            return `
                <div class="stat-row ${stat.isCorrect ? 'correct-answer' : ''}">
                    <div class="stat-label">
                        <div class="option-letter">${letter}</div>
                        ${isMine ? '<span aria-hidden="true" title="Sua resposta">👈</span>' : ''}
                    </div>
                    <div class="stat-bar-wrapper">
                        <div class="stat-bar" style="width: ${stat.percentage}%"></div>
                    </div>
                    <div class="stat-count">
                        <span class="count-number">${stat.count}</span>
                        <span class="count-percent">${stat.percentage}%</span>
                    </div>
                </div>
            `;
        }).join('');

        return `
            <div class="stats-container" style="margin-top: 1.5rem;" aria-live="polite">
                <h3 style="margin: 0 0 0.5rem; font-size: 1rem; color: #fff; text-align: center;">📊 Distribuição de Respostas</h3>
                ${rows}
            </div>
        `;
    }

    showRankingModal(ranking, feedbackHtml = '') {
        const topRanking = ranking?.slice(0, 10) || [];
        const existingModal = document.querySelector('.ranking-modal');
        if (existingModal) existingModal.remove();

        const medals = ['🥇', '🥈', '🥉'];
        const posColors = ['#FFD700', '#C0C0C0', '#CD7F32'];

        const rankingHTML = topRanking.map((player, index) => {
            const avatar = Utils.getAvatarEmoji(player.avatar);
            const medal = medals[index] || null;
            const posColor = posColors[index] || 'rgba(78,205,196,0.7)';
            const isTop3 = index < 3;
            const isMine = player.playerId === this.playerId;
            const bgGradient = isMine
                ? 'rgba(78,205,196,0.2), rgba(78,205,196,0.1)'
                : index === 0
                ? 'rgba(255,215,0,0.15), rgba(15,52,96,0.5)'
                : index === 1
                ? 'rgba(192,192,192,0.12), rgba(15,52,96,0.5)'
                : index === 2
                ? 'rgba(205,127,50,0.12), rgba(15,52,96,0.5)'
                : 'rgba(15,52,96,0.3), rgba(15,52,96,0.3)';

            return `
                <div style="
                    display: flex; align-items: center; gap: 10px;
                    padding: ${isTop3 ? '12px 14px' : '9px 14px'};
                    margin-bottom: 7px;
                    background: linear-gradient(135deg, ${bgGradient});
                    border: 1px solid ${isMine ? 'rgba(78,205,196,0.5)' : isTop3 ? posColor + '44' : 'rgba(78,205,196,0.08)'};
                    border-radius: 10px;
                ">
                    <div style="min-width:30px; text-align:center;">
                        ${medal
                            ? `<span style="font-size:${isTop3 ? '1.4rem' : '1.1rem'};">${medal}</span>`
                            : `<span style="font-size:0.8rem; font-weight:700; color:rgba(255,255,255,0.4);">${index + 1}º</span>`}
                    </div>
                    <div style="font-size:${isTop3 ? '1.8rem' : '1.4rem'}; flex-shrink:0;">${avatar}</div>
                    <div style="flex:1; text-align:left; min-width:0;">
                        <div style="font-weight:${isMine ? '900' : '600'}; font-size:${isTop3 ? '0.95rem' : '0.83rem'}; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; color:${isMine ? '#4ecdc4' : '#fff'};">
                            ${Utils.escapeHtml(player.playerName)}${isMine ? ' 👈' : ''}
                        </div>
                    </div>
                    <div style="text-align:right; flex-shrink:0;">
                        <div style="font-weight:900; font-size:${isTop3 ? '1rem' : '0.88rem'}; color:${isMine ? '#4ecdc4' : posColor};">
                            ${(player.score || 0).toLocaleString()}
                        </div>
                        <div style="font-size:0.6rem; color:rgba(255,255,255,0.3);">pts</div>
                    </div>
                </div>
            `;
        }).join('');

        const modal = document.createElement('div');
        modal.className = 'modal ranking-modal';
        modal.style.cssText = 'display:block; z-index:10000;';
        modal.setAttribute('role', 'dialog');
        modal.setAttribute('aria-modal', 'true');
        modal.setAttribute('aria-labelledby', 'partialRankingModalTitle');
        modal.innerHTML = `
            <div class="modal-content" style="
                max-width: 460px; text-align: center;
                max-height: 88vh; overflow-y: auto;
                background: linear-gradient(135deg, rgba(10,30,60,0.98), rgba(15,25,50,0.98));
                border: 1px solid rgba(78,205,196,0.25);
                border-radius: 20px; padding: 1.5rem;
            ">
                ${feedbackHtml ? `<div style="margin-bottom: 1.2rem;">${feedbackHtml}</div>` : ''}
                <div style="margin-bottom: 1.2rem;">
                    <div style="font-size:2rem; margin-bottom:0.2rem;" aria-hidden="true">🏆</div>
                    <h2 id="partialRankingModalTitle" style="
                        background: linear-gradient(135deg, #FFD700, #ff6b6b);
                        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                        font-size: 1.2rem; font-weight: 900; margin: 0;
                    ">Ranking Parcial</h2>
                </div>
                <div>${rankingHTML}</div>
                <button id="closeRankingBtn" class="btn btn-success" style="margin-top:1.2rem; padding:0.6rem 1.8rem;">
                    Continuar
                </button>
            </div>
        `;

        document.body.appendChild(modal);

        modal.querySelector('#closeRankingBtn').addEventListener('click', () => modal.remove());
        modal.addEventListener('click', (e) => { if (e.target === modal) modal.remove(); });
    }

    updateRanking(ranking) {
        const rankingList = document.getElementById('finalRankingList');
        if (rankingList && this.currentScreen === 'finalScreen') {
            this.updateFinalRanking(ranking);
        }
        
        const modalList = document.getElementById('rankingListModal');
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
            <div class="ranking-item ${player.playerId === this.playerId ? 'current-player' : ''}" role="listitem">
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

document.addEventListener('DOMContentLoaded', () => {
    console.log('🎮 Inicializando PlayerSocketManager...');
    window.playerManager = new PlayerSocketManager();
    window.addEventListener('beforeunload', () => {
        if (window.playerManager) window.playerManager.cleanup();
    });
});