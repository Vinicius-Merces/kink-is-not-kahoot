// Painel do Professor - Versão Socket.IO (com criação manual de sala)
class HostSocketManager {
    constructor() {
        this.roomId = null;
        this.roomCode = null;
        this.quiz = null;
        this.quizId = null;
        this.players = [];
        this.ranking = [];
        this.currentQuestionIndex = 0;
        this.currentQuestion = null;
        this.status = 'waiting';
        this.timerInterval = null;
        this.isGameActive = false;
        this.init();
    }

    async init() {
        const urlParams = new URLSearchParams(window.location.search);
        this.quizId = urlParams.get('quizId');

        auth.onAuthStateChanged(async (user) => {
            if (!user) {
                window.location.href = 'index.html';
                return;
            }
            this.waitForSocketConnection();
        });
    }

    waitForSocketConnection() {
        if (window.socketClient && window.socketClient.connected) {
            this.setupSocketListeners();
            this.updateUI();
        } else {
            const checkConnection = setInterval(() => {
                if (window.socketClient && window.socketClient.connected) {
                    clearInterval(checkConnection);
                    this.setupSocketListeners();
                    this.updateUI();
                }
            }, 100);
            
            setTimeout(() => {
                clearInterval(checkConnection);
                if (!window.socketClient || !window.socketClient.connected) {
                    Utils.showToast('Erro de conexão com o servidor', 'error');
                    setTimeout(() => window.location.href = 'my-quizzes.html', 2000);
                }
            }, 5000);
        }
    }

    setupSocketListeners() {
        window.socketClient.on('room-created', (data) => {
            if (data && data.success) {
                console.log('🏠 Sala criada com sucesso!');
                this.roomId = data.roomId;
                this.roomCode = data.roomCode;
                this.loadQuizData();
                this.updateUIAfterCreation();
                Utils.showToast(`Sala criada! Código: ${data.roomCode}`, 'success');
            } else {
                Utils.showToast(data?.error || 'Erro ao criar sala', 'error');
            }
        });

        window.socketClient.on('player-joined', (data) => {
            this.players = data.players;
            this.updatePlayersList();
            Utils.showToast(`${data.playerName || 'Um jogador'} entrou na sala!`, 'info');
        });

        window.socketClient.on('player-left', (data) => {
            this.players = data.players;
            this.updatePlayersList();
        });

        window.socketClient.on('quiz-started', (data) => {
            this.status = 'active';
            this.isGameActive = true;
            Utils.showToast(`Quiz iniciado! ${data.totalPlayers} jogadores participando.`, 'success');
            const startGameBtn = document.getElementById('startGameBtn');
            const questionControls = document.getElementById('questionControls');
            if (startGameBtn) startGameBtn.style.display = 'none';
            if (questionControls) questionControls.style.display = 'block';
        });

        window.socketClient.on('reading-phase', (data) => {
            this.status = 'reading';
            this.currentQuestion = data.question;
            this.currentQuestionIndex = data.question?.index || 0;
            this.updateReadingPhase();
        });

        window.socketClient.on('answering-phase', (data) => {
            this.status = 'answering';
            this.updateAnsweringPhase(data);
        });

        window.socketClient.on('question-result', (data) => {
            console.log('📊 Evento question-result recebido:', data);
            this.ranking = data.ranking;
            this.updateRanking();
            
            // ✅ NOVO: Exibir gráfico de estatísticas
            if (data.stats) {
                this.displayAnswerStatistics(data.stats, data.correctAnswer);
            }
            
            // ✅ NOVO: Mostrar resposta correta e explicação
            if (data.correctAnswerText || data.explanation) {
                this.showCorrectAnswerFeedback(data.correctAnswer, data.correctAnswerText, data.explanation);
            }
            
            this.showRankingModalWithDistribution(data);
            
            const totalAnswers = data.results?.length || 0;
            const correctAnswers = data.results?.filter(r => r.isCorrect).length || 0;
            const accuracy = totalAnswers > 0 ? (correctAnswers / totalAnswers * 100).toFixed(1) : 0;
            const answersCountElem = document.getElementById('answersCount');
            const accuracyRateElem = document.getElementById('accuracyRate');
            if (answersCountElem) answersCountElem.textContent = totalAnswers;
            if (accuracyRateElem) accuracyRateElem.textContent = `${accuracy}%`;
        });

        window.socketClient.on('game-finished', (data) => {
            this.isGameActive = false;
            this.showFinalRanking(data.ranking);
        });

        window.socketClient.on('ranking-update', (data) => {
            this.ranking = data.ranking;
            this.updateRanking();
        });

        window.socketClient.on('error', (data) => {
            Utils.showToast(data.message, 'error');
        });
    }

    loadQuizData() {
        if (!this.roomId) return;
        window.socketClient.getRoomState(this.roomId, (response) => {
            if (response && response.success) {
                this.quiz = response.quiz;
                this.updateUIAfterCreation();
            }
        });
    }

    updateUI() {
        const createRoomSection = document.getElementById('createRoomSection');
        const gameControlsSection = document.getElementById('gameControlsSection');
        if (createRoomSection) createRoomSection.style.display = 'block';
        if (gameControlsSection) gameControlsSection.style.display = 'none';
        
        const createRoomBtn = document.getElementById('createRoomBtn');
        if (createRoomBtn && !createRoomBtn.hasListener) {
            createRoomBtn.addEventListener('click', async () => {
                if (!this.quizId) {
                    Utils.showToast('Quiz não identificado', 'error');
                    return;
                }
                const creatorName = auth.currentUser?.displayName || auth.currentUser?.email;
                const creatorId = auth.currentUser?.uid;
                const idToken = auth.currentUser ? await auth.currentUser.getIdToken() : null;

                console.log('🎮 Criando sala para quiz:', this.quizId);
                Utils.showToast('Criando sala...', 'info');

                window.socketClient.createRoom(this.quizId, creatorName, creatorId, idToken, (response) => {
                    if (response && response.success) {
                        this.roomId = response.roomId;
                        this.roomCode = response.roomCode;
                        this.loadQuizData();
                        this.updateUIAfterCreation();
                        Utils.showToast(`Sala criada! Código: ${response.roomCode}`, 'success');
                    } else {
                        Utils.showToast(response?.error || 'Erro ao criar sala', 'error');
                    }
                });
            });
            createRoomBtn.hasListener = true;
        }
    }

    updateUIAfterCreation() {
        const createRoomSection = document.getElementById('createRoomSection');
        const gameControlsSection = document.getElementById('gameControlsSection');
        if (createRoomSection) createRoomSection.style.display = 'none';
        if (gameControlsSection) gameControlsSection.style.display = 'block';
        
        const roomCodeElem = document.getElementById('roomCode');
        if (roomCodeElem) roomCodeElem.textContent = this.roomCode || 'XXXXXX';
        
        const quizInfoElem = document.getElementById('quizInfo');
        if (quizInfoElem && this.quiz) {
            quizInfoElem.innerHTML = `<strong>Quiz:</strong> ${this.quiz.title || 'Carregando...'} | <strong>Perguntas:</strong> ${this.quiz.questions?.length || 0}`;
        }
        
        this.setupButtons();
    }

    setupButtons() {
        const copyBtn = document.getElementById('copyCodeBtn');
        if (copyBtn && !copyBtn.hasListener) {
            copyBtn.addEventListener('click', () => {
                Utils.copyToClipboard(this.roomCode || '');
            });
            copyBtn.hasListener = true;
        }
        
        const shareBtn = document.getElementById('shareRoomBtn');
        if (shareBtn && !shareBtn.hasListener) {
            shareBtn.addEventListener('click', () => {
                const url = `${window.location.origin}/player.html?code=${this.roomCode}`;
                Utils.copyToClipboard(url);
                Utils.showToast('Link copiado! Compartilhe com seus alunos', 'success');
            });
            shareBtn.hasListener = true;
        }
        
        const startGameBtn = document.getElementById('startGameBtn');
        if (startGameBtn && !startGameBtn.hasListener) {
            startGameBtn.addEventListener('click', () => {
                window.socketClient.startQuiz((response) => {
                    if (!response || !response.success) {
                        Utils.showToast(response?.error || 'Erro ao iniciar quiz', 'error');
                    }
                });
            });
            startGameBtn.hasListener = true;
        }
        
        const startQuestionBtn = document.getElementById('startQuestionBtn');
        if (startQuestionBtn && !startQuestionBtn.hasListener) {
            startQuestionBtn.addEventListener('click', () => {
                window.socketClient.startQuestion((response) => {
                    if (!response || !response.success) {
                        if (response?.finished) {
                            Utils.showToast('Quiz finalizado!', 'info');
                        } else {
                            Utils.showToast(response?.error || 'Erro ao iniciar pergunta', 'error');
                        }
                    }
                });
            });
            startQuestionBtn.hasListener = true;
        }
        
        const nextQuestionBtn = document.getElementById('nextQuestionBtn');
        if (nextQuestionBtn && !nextQuestionBtn.hasListener) {
            nextQuestionBtn.addEventListener('click', () => {
                // Fechar modal de ranking antes de ir para próxima
                const modal = document.getElementById('rankingModal');
                if (modal) modal.style.display = 'none';
                const overlay = document.getElementById('rankingOverlay');
                if (overlay) overlay.style.display = 'none';
                
                window.socketClient.nextQuestion((response) => {
                    if (response && response.finished) {
                        this.endGame();
                    }
                });
            });
            nextQuestionBtn.hasListener = true;
        }
        
        const endGameBtn = document.getElementById('endGameBtn');
        if (endGameBtn && !endGameBtn.hasListener) {
            endGameBtn.addEventListener('click', () => {
                if (confirm('Tem certeza que deseja encerrar o quiz?')) {
                    window.socketClient.endGame();
                }
            });
            endGameBtn.hasListener = true;
        }
    }

    // ========== RANKING COM DISTRIBUIÇÃO DE RESPOSTAS ==========
    showRankingModalWithDistribution(data) {
        const ranking = data.ranking?.slice(0, 10) || [];
        const medals = ['🥇', '🥈', '🥉'];
        const posColors = ['#FFD700', '#C0C0C0', '#CD7F32'];

        const rankingHTML = ranking.map((player, index) => {
            const avatar = Utils.getAvatarEmoji(player.avatar);
            const medal = medals[index] || null;
            const posColor = posColors[index] || 'rgba(78,205,196,0.7)';
            const isTop3 = index < 3;
            const bgGradient = index === 0
                ? 'rgba(255,215,0,0.15), rgba(15,52,96,0.6)'
                : index === 1
                ? 'rgba(192,192,192,0.15), rgba(15,52,96,0.6)'
                : index === 2
                ? 'rgba(205,127,50,0.15), rgba(15,52,96,0.6)'
                : 'rgba(15,52,96,0.3), rgba(15,52,96,0.3)';

            return `
                <div style="
                    display: flex; align-items: center; gap: 12px;
                    padding: ${isTop3 ? '14px 16px' : '10px 16px'};
                    margin-bottom: 8px;
                    background: linear-gradient(135deg, ${bgGradient});
                    border: 1px solid ${isTop3 ? posColor + '55' : 'rgba(78,205,196,0.1)'};
                    border-radius: 12px;
                ">
                    <div style="min-width: 36px; text-align: center;">
                        ${medal
                            ? `<span style="font-size:${isTop3 ? '1.6rem' : '1.2rem'};">${medal}</span>`
                            : `<span style="font-size:0.85rem; font-weight:700; color:rgba(255,255,255,0.4);">${index + 1}º</span>`}
                    </div>
                    <div style="font-size:${isTop3 ? '2rem' : '1.5rem'}; flex-shrink:0;">${avatar}</div>
                    <div style="flex:1; text-align:left; min-width:0;">
                        <div style="font-weight:700; font-size:${isTop3 ? '1rem' : '0.88rem'}; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">
                            ${Utils.escapeHtml(player.playerName)}
                        </div>
                    </div>
                    <div style="text-align:right; flex-shrink:0;">
                        <div style="font-weight:900; font-size:${isTop3 ? '1.1rem' : '0.95rem'}; color:${posColor};">
                            ${(player.score || 0).toLocaleString()}
                        </div>
                        <div style="font-size:0.62rem; color:rgba(255,255,255,0.35);">pontos</div>
                    </div>
                </div>
            `;
        }).join('');

        const modal = document.createElement('div');
        modal.className = 'modal ranking-modal-host';
        modal.style.cssText = 'display:block; z-index:10000;';
        modal.setAttribute('role', 'dialog');
        modal.setAttribute('aria-modal', 'true');
        modal.setAttribute('aria-labelledby', 'rankingModalTitle');
        modal.innerHTML = `
            <div class="modal-content" style="
                max-width: 520px; text-align: center;
                max-height: 88vh; overflow-y: auto;
                background: linear-gradient(135deg, rgba(10,30,60,0.98), rgba(15,25,50,0.98));
                border: 1px solid rgba(78,205,196,0.25);
                border-radius: 20px; padding: 2rem;
            ">
                <div style="margin-bottom: 1.5rem;">
                    <div style="font-size: 2.5rem; margin-bottom: 0.3rem;" aria-hidden="true">🏆</div>
                    <h2 id="rankingModalTitle" style="
                        background: linear-gradient(135deg, #FFD700, #ff6b6b);
                        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                        font-size: 1.4rem; font-weight: 900; margin: 0;
                    ">Ranking da Rodada</h2>
                    <p style="color:rgba(255,255,255,0.4); font-size:0.8rem; margin-top:4px;">
                        Pergunta ${(data.questionIndex || 0) + 1}
                    </p>
                </div>
                <div>${rankingHTML}</div>
                <button id="closeRankingBtn" class="btn btn-success" style="margin-top:1.5rem; padding:0.7rem 2rem;">
                    Próxima Pergunta ▶
                </button>
            </div>
        `;

        document.body.appendChild(modal);

        const closeBtn = modal.querySelector('#closeRankingBtn');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => modal.remove());
        }
        modal.addEventListener('click', (e) => {
            if (e.target === modal) modal.remove();
        });
    }

    // ========== MÉTODOS AUXILIARES ==========
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
            <div class="player-item" role="listitem">
                <div class="player-info">
                    <span class="player-avatar" aria-hidden="true">${Utils.getAvatarEmoji(player.avatar)}</span>
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
            <div class="ranking-item" role="listitem">
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

    showFinalRanking(ranking) {
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.style.display = 'block';
        modal.setAttribute('role', 'dialog');
        modal.setAttribute('aria-modal', 'true');
        modal.setAttribute('aria-labelledby', 'finalRankingModalTitle');

        let podiumHTML = '';
        if (ranking.length >= 1) {
            podiumHTML += `<div style="font-size: 1.8rem; margin: 1rem 0;">🥇 ${Utils.escapeHtml(ranking[0].playerName)} — ${ranking[0].score} pts</div>`;
        }
        if (ranking.length >= 2) {
            podiumHTML += `<div style="font-size: 1.4rem; margin: 0.5rem 0;">🥈 ${Utils.escapeHtml(ranking[1].playerName)} — ${ranking[1].score} pts</div>`;
        }
        if (ranking.length >= 3) {
            podiumHTML += `<div style="font-size: 1.2rem; margin: 0.5rem 0;">🥉 ${Utils.escapeHtml(ranking[2].playerName)} — ${ranking[2].score} pts</div>`;
        }

        modal.innerHTML = `
            <div class="modal-content" style="max-width: 500px; text-align: center;">
                <h2 id="finalRankingModalTitle" style="color: #ff6b6b; margin-bottom: 1rem;">🏆 Ranking Final 🏆</h2>
                ${podiumHTML}
                <div style="margin: 1rem 0; max-height: 400px; overflow-y: auto;">
                    ${ranking.map((player, index) => `
                        <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.8rem; border-bottom: 1px solid rgba(255,255,255,0.1);">
                            <div style="display: flex; align-items: center; gap: 0.5rem;">
                                <span style="font-weight: bold; width: 40px;">${index + 1}º</span>
                                <span>${Utils.escapeHtml(player.playerName)}</span>
                            </div>
                            <span style="color: #ff6b6b; font-weight: bold;">${player.score || 0} pts</span>
                        </div>
                    `).join('')}
                </div>
                <button id="closeFinalRankingBtn" class="btn btn-primary" style="margin-top: 1rem;">Fechar</button>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        const closeBtn = modal.querySelector('#closeFinalRankingBtn');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                modal.remove();
                window.location.href = 'my-quizzes.html';
            });
        }
        
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

    // ✅ NOVO: Exibir gráfico de estatísticas de respostas
    displayAnswerStatistics(stats, correctAnswer) {
        const container = document.getElementById('answerStatsChart');
        if (!container) return;

        container.innerHTML = '';
        
        if (!stats || Object.keys(stats).length === 0) {
            container.innerHTML = '<p style="color: #888; text-align: center; padding: 20px;">Sem dados de respostas</p>';
            return;
        }

        let html = '<div style="display: flex; flex-direction: column; gap: 16px;">';
        
        const maxCount = Math.max(...Object.values(stats).map(s => s.count || 0), 1);
        
        Object.entries(stats).forEach(([option, data]) => {
            const barWidth = (data.count / maxCount) * 100 || 0;
            const isCorrect = data.isCorrect;
            const bgColor = isCorrect ? 'rgba(78, 205, 196, 0.15)' : 'rgba(100, 100, 100, 0.1)';
            const borderColor = isCorrect ? 'rgba(78, 205, 196, 0.4)' : 'rgba(100, 100, 100, 0.2)';
            const barColor = isCorrect ? 'linear-gradient(90deg, #4ecdc4, #45b3aa)' : 'linear-gradient(90deg, #ff6b6b, #ff5252)';
            const badge = isCorrect ? '✅' : '';
            
            html += `
                <div style="background: ${bgColor}; border: 1px solid ${borderColor}; border-radius: 8px; padding: 12px; ">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <div style="display: flex; align-items: center; gap: 10px; flex: 1; min-width: 0;">
                            <span style="font-size: 18px; background: linear-gradient(135deg, #ff6b6b, #ff5252); width: 32px; height: 32px; border-radius: 6px; display: flex; align-items: center; justify-content: center; color: #fff; font-weight: bold; flex-shrink: 0;">${option}</span>
                            <div style="min-width: 0; flex: 1;">
                                <div style="color: #fff; font-weight: 500; font-size: 13px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${data.label || 'N/A'}</div>
                            </div>
                        </div>
                        <div style="text-align: right; margin-left: 10px;">
                            <div style="color: #fff; font-weight: bold; font-size: 16px;">${data.count}</div>
                            <div style="color: #aaa; font-size: 11px;">${data.percentage}%</div>
                        </div>
                        <span style="margin-left: 8px; font-size: 16px;">${badge}</span>
                    </div>
                    <div style="background: rgba(0,0,0,0.3); height: 24px; border-radius: 4px; overflow: hidden; position: relative;">
                        <div style="background: ${barColor}; height: 100%; width: ${barWidth}%; transition: width 0.5s ease; display: flex; align-items: center; justify-content: flex-end; padding-right: 6px;">
                            ${barWidth > 20 ? `<span style="color: #fff; font-weight: bold; font-size: 12px;">${data.percentage}%</span>` : ''}
                        </div>
                        ${barWidth <= 20 && data.percentage > 0 ? `<span style="position: absolute; right: 6px; top: 50%; transform: translateY(-50%); color: #fff; font-weight: bold; font-size: 12px;">${data.percentage}%</span>` : ''}
                    </div>
                </div>
            `;
        });
        
        html += '</div>';
        container.innerHTML = html;
        console.log('📊 Gráfico atualizado com sucesso', stats);
    }

    // ✅ NOVO: Mostrar resposta correta e explicação
    showCorrectAnswerFeedback(correctOption, correctAnswerText, explanation) {
        const feedbackElement = document.getElementById('correctAnswerFeedback');
        if (!feedbackElement) return;
        
        let html = `
            <div class="correct-answer-display">
                <div class="check-icon">✅</div>
                <div class="correct-text">Resposta Correta: <strong>${correctOption}</strong></div>
        `;
        
        if (correctAnswerText) {
            html += `<div class="correct-answer-detail">${correctAnswerText}</div>`;
        }
        
        if (explanation) {
            html += `<div class="explanation"><strong>Explicação:</strong><br>${explanation}</div>`;
        }
        
        html += '</div>';
        feedbackElement.innerHTML = html;
        
        console.log('💡 Feedback da resposta correta exibido');
    }

    cleanup() {
        if (this.timerInterval) clearInterval(this.timerInterval);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    console.log('🎮 Inicializando HostSocketManager...');
    window.hostManager = new HostSocketManager();
    window.addEventListener('beforeunload', () => {
        if (window.hostManager) window.hostManager.cleanup();
    });
});