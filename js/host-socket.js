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
            createRoomBtn.addEventListener('click', () => {
                if (!this.quizId) {
                    Utils.showToast('Quiz não identificado', 'error');
                    return;
                }
                const creatorName = auth.currentUser?.displayName || auth.currentUser?.email;
                const creatorId = auth.currentUser?.uid;
                
                console.log('🎮 Criando sala para quiz:', this.quizId);
                Utils.showToast('Criando sala...', 'info');
                
                window.socketClient.createRoom(this.quizId, creatorName, creatorId, (response) => {
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
        console.log('🎯 showRankingModalWithDistribution chamado com data:', data);

        // Extrair dados
        const ranking = data.ranking?.slice(0, 5) || [];
        const results = data.results || [];
        const currentQuestion = this.currentQuestion;
        const options = currentQuestion?.options || [];
        const correctAnswerIndex = currentQuestion?.correct;

        // Contar quantos jogadores escolheram cada opção
        const choiceCount = new Array(options.length).fill(0);
        results.forEach(r => {
            if (r.answer !== undefined && r.answer !== null && r.answer >= 0 && r.answer < options.length) {
                choiceCount[r.answer]++;
            }
        });
        const totalAnswers = results.length;

        // Gerar HTML da distribuição de respostas
        let distributionHTML = '';
        if (options.length > 0 && totalAnswers > 0) {
            distributionHTML = `
                <div style="margin-top: 1.5rem; text-align: left;">
                    <h3 style="color: #4ecdc4; margin-bottom: 1rem; font-size: 1rem;">📊 Distribuição de Respostas</h3>
                    <div style="background: rgba(0,0,0,0.3); border-radius: 12px; padding: 1rem;">
            `;
            options.forEach((opt, i) => {
                const count = choiceCount[i];
                const percentage = totalAnswers > 0 ? Math.round((count / totalAnswers) * 100) : 0;
                const isCorrect = (i === correctAnswerIndex);
                const barColor = isCorrect ? '#48bb78' : '#ff6b6b';
                
                distributionHTML += `
                    <div style="margin-bottom: 12px;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 4px; font-size: 0.85rem;">
                            <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
                                <span style="font-weight: bold; background: rgba(0,0,0,0.5); padding: 2px 8px; border-radius: 20px;">${String.fromCharCode(65 + i)}</span>
                                <span style="word-break: break-word;">${Utils.escapeHtml(opt)}</span>
                                ${isCorrect ? '<span style="color: #48bb78; font-size: 0.7rem;">✅ Correta</span>' : ''}
                            </div>
                            <span style="font-weight: bold;">${count} (${percentage}%)</span>
                        </div>
                        <div style="background: #2d3748; height: 8px; border-radius: 4px; overflow: hidden;">
                            <div style="background: ${barColor}; width: ${percentage}%; height: 100%; border-radius: 4px;"></div>
                        </div>
                    </div>
                `;
            });
            distributionHTML += `
                    </div>
                </div>
            `;
        } else if (options.length > 0) {
            distributionHTML = `
                <div style="margin-top: 1.5rem; text-align: left;">
                    <h3 style="color: #4ecdc4; margin-bottom: 1rem; font-size: 1rem;">📊 Distribuição de Respostas</h3>
                    <div style="background: rgba(0,0,0,0.3); border-radius: 12px; padding: 1rem;">
                        <p style="text-align: center; opacity: 0.7;">Aguardando respostas...</p>
                    </div>
                </div>
            `;
        }

        // Criar modal
        const modal = document.createElement('div');
        modal.className = 'modal ranking-modal-host';
        modal.style.display = 'block';
        modal.style.zIndex = '10000';
        modal.innerHTML = `
            <div class="modal-content" style="max-width: 580px; text-align: center; max-height: 80vh; overflow-y: auto;">
                <h2 style="color: #ff6b6b; margin-bottom: 1rem;">🏆 Ranking Parcial 🏆</h2>
                <div style="margin: 1rem 0;">
                    ${ranking.map((player, index) => `
                        <div style="display: flex; justify-content: space-between; padding: 0.8rem; border-bottom: 1px solid rgba(255,255,255,0.1);">
                            <span style="font-weight: bold; font-size: 1.2rem;">${index + 1}º</span>
                            <span>${Utils.getAvatarEmoji(player.avatar)} ${Utils.escapeHtml(player.playerName)}</span>
                            <span style="color: #ff6b6b; font-weight: bold;">${player.score || 0} pts</span>
                        </div>
                    `).join('')}
                </div>
                ${distributionHTML}
                <div style="margin: 1rem 0; font-size: 0.9rem; opacity: 0.7;">
                    Resposta correta: ${data.correctAnswer || 'Não disponível'}
                </div>
                <button id="closeRankingBtn" class="btn btn-primary" style="margin-top: 1rem;">Continuar</button>
            </div>
        `;

        // Adicionar ao DOM
        document.body.appendChild(modal);
        console.log('✅ Modal adicionado ao DOM');

        // Fechar ao clicar no botão
        const closeBtn = modal.querySelector('#closeRankingBtn');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                modal.remove();
                console.log('Modal removido');
            });
        }

        // Fechar ao clicar fora
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
                console.log('Modal removido (clique fora)');
            }
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

    showFinalRanking(ranking) {
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.style.display = 'block';
        
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
                <h2 style="color: #ff6b6b; margin-bottom: 1rem;">🏆 Ranking Final 🏆</h2>
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
            container.innerHTML = '<p style="color: var(--color-text-secondary); text-align: center;">Sem dados de respostas</p>';
            return;
        }

        let html = '<div class="stats-container">';
        
        // Encontrar maior valor para escala
        const maxCount = Math.max(
            ...Object.values(stats).map(s => s.count || 1),
            1
        );
        
        // Desenhar barra para cada opção
        Object.entries(stats).forEach(([option, data]) => {
            const barWidth = (data.count / maxCount) * 100;
            const isCorrect = data.isCorrect;
            const correctClass = isCorrect ? 'correct-answer' : '';
            const correctBadge = isCorrect ? '✅' : '';
            
            html += `
                <div class="stat-row ${correctClass}">
                    <div class="stat-label">
                        <span class="option-letter">${option}</span>
                        <span class="option-text">${data.label ? data.label.substring(0, 30) : 'N/A'}</span>
                    </div>
                    <div class="stat-bar-wrapper">
                        <div class="stat-bar" style="width: ${barWidth}%"></div>
                    </div>
                    <div class="stat-count">
                        <span class="count-number">${data.count}</span>
                        <span class="count-percent">${data.percentage}%</span>
                    </div>
                    <div class="stat-correct">${correctBadge}</div>
                </div>
            `;
        });
        
        html += '</div>';
        container.innerHTML = html;
        
        console.log('📊 Gráfico de estatísticas exibido');
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