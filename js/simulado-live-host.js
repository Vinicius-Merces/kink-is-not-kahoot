// Simulado ao Vivo - Modo Professor (criação de sala, controle de votação e resultado da turma)
(function () {
    const LEVEL_LABELS = {
        iniciante: 'Iniciante',
        medio: 'Médio',
        avancado: 'Avançado'
    };

    const PASS_SCORE = 70;
    const LETTERS = ['A', 'B', 'C', 'D', 'E', 'F'];

    let session = null;          // resposta de simulado:create-room (inclui roomCode, certCode, domains, etc.)
    let currentIndex = -1;       // pergunta atualmente em votação no servidor
    let totalQuestions = 0;
    let players = [];
    let viewingIndex = null;     // pergunta que o professor está visualizando no momento
    let answeredIndices = new Set();
    let listenersSetup = false;
    let currentQuestionData = null; // última pergunta renderizada (para o report de erro)

    // ============================================
    // Utilidades
    // ============================================
    function ensureSocket(callback) {
        if (window.socketClient && window.socketClient.connected) {
            callback();
            return;
        }
        const interval = setInterval(() => {
            if (window.socketClient && window.socketClient.connected) {
                clearInterval(interval);
                callback();
            }
        }, 200);
        setTimeout(() => clearInterval(interval), 10000);
    }

    function getDomainName(domainId) {
        const domain = (session?.domains || []).find(d => d.id === domainId);
        return domain ? domain.name : domainId;
    }

    // ============================================
    // Criação da sala
    // ============================================
    async function createRoom(certId, level, numQuestions) {
        const user = auth.currentUser;
        if (!user) {
            Utils.showToast('Faça login para criar uma sala de simulado ao vivo', 'warning');
            return;
        }

        const btn = document.getElementById('createLiveRoomBtn');
        if (btn) {
            btn.disabled = true;
            btn.textContent = '⏳ Criando sala...';
        }

        const idToken = await user.getIdToken();

        ensureSocket(() => {
            socketClient.createLiveSimuladoRoom(certId, level, numQuestions, user.displayName || 'Professor', user.uid, idToken, (response) => {
                if (btn) {
                    btn.disabled = false;
                    btn.textContent = '🎓 Criar Sala ao Vivo';
                }

                if (!response || !response.success) {
                    Utils.showToast(response?.error || 'Erro ao criar sala de simulado', 'error');
                    return;
                }

                session = response;
                currentIndex = -1;
                viewingIndex = null;
                totalQuestions = response.totalQuestions;
                players = [];
                answeredIndices.clear();

                setupSocketListeners();
                showRoomScreen();
            });
        });
    }

    function setupSocketListeners() {
        if (listenersSetup) return;
        listenersSetup = true;

        socketClient.on('simulado:player-joined', (data) => {
            players = data.players || players;
            updatePlayersUI();
        });

        socketClient.on('simulado:player-left', (data) => {
            players = data.players || players;
            updatePlayersUI();
        });

        socketClient.on('simulado:teacher-update', (data) => {
            handleTeacherUpdate(data);
        });

        socketClient.on('simulado:session-result', (data) => {
            renderFinalResult(data);
            window.showSimuladoScreen('liveResultScreen');
        });
    }

    // ============================================
    // Tela de sala (sala de espera)
    // ============================================
    function showRoomScreen() {
        document.getElementById('liveRoomCode').textContent = session.roomCode;
        document.getElementById('liveCertInfo').textContent =
            `${session.certCode} • ${LEVEL_LABELS[session.level] || session.level} • ${session.totalQuestions} perguntas`;
        updatePlayersUI();
        window.showSimuladoScreen('liveHostScreen');
    }

    function renderPlayersList(container) {
        if (!container) return;
        if (players.length === 0) {
            container.innerHTML = '<p class="placeholder">Nenhum aluno conectado ainda</p>';
            return;
        }
        container.innerHTML = players.map(p => `
            <div class="player-item-mini">
                <span class="player-avatar-mini">${p.avatar || '👤'}</span>
                <span>${Utils.escapeHtml(p.name)}</span>
            </div>
        `).join('');
    }

    function updatePlayersUI() {
        renderPlayersList(document.getElementById('livePlayersList'));
        renderPlayersList(document.getElementById('liveControlPlayersList'));
        ['liveHostPlayerCount', 'liveControlPlayerCount'].forEach(id => {
            const el = document.getElementById(id);
            if (el) el.textContent = players.length;
        });
    }

    document.getElementById('copyLiveLinkBtn').addEventListener('click', () => {
        const link = `${window.location.origin}/player.html?code=${session.roomCode}`;
        Utils.copyToClipboard(link);
    });

    document.getElementById('cancelLiveRoomBtn').addEventListener('click', () => {
        if (!confirm('Cancelar esta sala de simulado ao vivo?')) return;
        socketClient.endLiveSimuladoSession(() => {
            resetLiveState();
            window.showSimuladoScreen('selectionScreen');
        });
    });

    document.getElementById('startLiveSessionBtn').addEventListener('click', () => {
        const btn = document.getElementById('startLiveSessionBtn');
        btn.disabled = true;
        socketClient.startLiveSimuladoSession((response) => {
            btn.disabled = false;
            if (!response || !response.success) {
                Utils.showToast(response?.error || 'Erro ao iniciar sessão', 'error');
                return;
            }
            renderQuestionDots();
            window.showSimuladoScreen('liveControlScreen');
        });
    });

    // ============================================
    // Tela de controle (votação ao vivo)
    // ============================================
    function renderQuestionDots() {
        const container = document.getElementById('liveControlQuestionDots');
        container.innerHTML = Array.from({ length: totalQuestions }, (_, i) => `
            <button type="button" class="exam-dot" data-index="${i}" title="Pergunta ${i + 1}" aria-label="Pergunta ${i + 1}">${i + 1}</button>
        `).join('');

        container.querySelectorAll('.exam-dot').forEach(dot => {
            dot.addEventListener('click', () => {
                gotoQuestion(parseInt(dot.dataset.index, 10));
            });
        });
    }

    function updateQuestionDots() {
        const dots = document.querySelectorAll('#liveControlQuestionDots .exam-dot');
        dots.forEach((dot, i) => {
            const answered = answeredIndices.has(i);
            dot.classList.toggle('answered', answered);
            dot.classList.toggle('current', i === viewingIndex);
            dot.classList.toggle('live', i === currentIndex && i !== viewingIndex);
            if (i === viewingIndex) {
                dot.setAttribute('aria-current', 'true');
            } else {
                dot.removeAttribute('aria-current');
            }
            dot.setAttribute('aria-label', `Pergunta ${i + 1}${answered ? ' (respondida)' : ''}`);
        });
    }

    function handleTeacherUpdate(data) {
        const shouldFollow = (viewingIndex === null) || (viewingIndex === currentIndex) || (viewingIndex === data.index);

        players = data.players || players;
        currentIndex = data.index;
        totalQuestions = data.total;

        if (data.result) answeredIndices.add(data.index);
        else answeredIndices.delete(data.index);

        if (shouldFollow) {
            viewingIndex = data.index;
            renderQuestionState(data);
        }

        updatePlayersUI();
        updateQuestionDots();
    }

    function gotoQuestion(index) {
        socketClient.gotoLiveSimuladoQuestion(index, (response) => {
            if (!response || !response.success) {
                Utils.showToast(response?.error || 'Erro ao revisar pergunta', 'error');
                return;
            }

            viewingIndex = index;
            players = response.players || players;
            if (response.result) answeredIndices.add(index);

            renderQuestionState(response);
            updatePlayersUI();
            updateQuestionDots();
        });
    }

    function renderQuestionState(data) {
        currentQuestionData = data;
        document.getElementById('liveControlCertBadge').textContent =
            `${session.certCode} • ${LEVEL_LABELS[session.level] || session.level}`;
        document.getElementById('liveControlProgress').textContent = `Pergunta ${data.index + 1} de ${data.total}`;
        document.getElementById('liveControlProgressFill').style.width = `${Math.round(((data.index + 1) / data.total) * 100)}%`;
        document.getElementById('liveControlDomainTag').textContent = getDomainName(data.domain);
        document.getElementById('liveControlQuestionText').textContent = data.text;

        renderOptionsList(data);

        const voteProgressEl = document.getElementById('liveControlVoteProgress');
        const resultsEl = document.getElementById('liveControlResults');

        if (data.status === 'voting') {
            voteProgressEl.style.display = 'block';
            voteProgressEl.textContent = `🗳️ ${data.votedCount} de ${data.totalPlayers} alunos votaram`;
            resultsEl.style.display = 'none';
        } else if (data.result) {
            voteProgressEl.style.display = 'none';
            resultsEl.style.display = 'block';
            renderResultBars(data);
        } else {
            voteProgressEl.style.display = 'none';
            resultsEl.style.display = 'none';
        }

        const revoteBtn = document.getElementById('liveRevoteBtn');
        const advanceBtn = document.getElementById('liveAdvanceBtn');
        const backBtn = document.getElementById('liveBackToCurrentBtn');

        revoteBtn.style.display = (data.status === 'closed' && data.index <= currentIndex) ? 'inline-flex' : 'none';

        const isViewingCurrent = data.index === currentIndex;
        backBtn.style.display = isViewingCurrent ? 'none' : 'inline-flex';

        if (isViewingCurrent) {
            const isLastClosed = data.status === 'closed' && data.index >= data.total - 1;
            advanceBtn.style.display = isLastClosed ? 'none' : 'inline-flex';
            advanceBtn.textContent = data.status === 'closed' ? 'Próxima Pergunta ➡' : 'Avançar (encerrar votação) ➡';
        } else {
            advanceBtn.style.display = 'none';
        }
    }

    function renderOptionsList(data) {
        const container = document.getElementById('liveControlOptions');
        container.innerHTML = data.options.map((opt, i) => {
            let cls = 'live-option';
            if (i === data.correct) cls += ' live-option-correct';
            if (data.result && data.result.winningOption === i) {
                cls += data.result.isCorrect ? ' live-option-class-correct' : ' live-option-class-wrong';
            }

            const percentBadge = data.result ? `<span class="live-option-percent">${data.result.percentages[i]}%</span>` : '';
            const correctBadge = i === data.correct ? '<span class="live-option-badge">✅ Gabarito</span>' : '';

            return `
                <div class="${cls}">
                    <span class="exam-option-letter">${LETTERS[i]}</span>
                    <span class="exam-option-text">${Utils.escapeHtml(opt)}</span>
                    ${correctBadge}
                    ${percentBadge}
                </div>
            `;
        }).join('');
    }

    function renderResultBars(data) {
        const result = data.result;
        const container = document.getElementById('liveControlResultBars');
        container.innerHTML = result.percentages.map((percent, i) => {
            const isCorrect = i === data.correct;
            return `
                <div class="stat-row ${isCorrect ? 'correct-answer' : ''}">
                    <div class="stat-label">
                        <div class="option-letter">${LETTERS[i]}</div>
                    </div>
                    <div class="stat-bar-wrapper">
                        <div class="stat-bar" style="width: ${percent}%"></div>
                    </div>
                    <div class="stat-count">
                        <span class="count-number">${result.voteCounts[i]}</span>
                        <span class="count-percent">${percent}%</span>
                    </div>
                    <div class="stat-correct">${isCorrect ? '✅' : ''}</div>
                </div>
            `;
        }).join('');

        const feedback = document.getElementById('liveControlResultFeedback');
        if (result.totalVotes === 0) {
            feedback.textContent = 'Nenhum aluno votou nesta pergunta.';
        } else if (result.isCorrect) {
            feedback.textContent = `✅ A turma acertou! A maioria escolheu a opção ${LETTERS[result.winningOption]}.`;
        } else {
            feedback.textContent = `❌ A turma errou. A maioria escolheu a opção ${LETTERS[result.winningOption]}, mas a correta é a ${LETTERS[data.correct]}.`;
        }

        const explanationEl = document.getElementById('liveControlExplanation');
        if (data.explanation) {
            explanationEl.style.display = 'block';
            explanationEl.innerHTML = `<strong>Explicação:</strong> ${Utils.escapeHtml(data.explanation)}`;
        } else {
            explanationEl.style.display = 'none';
        }
    }

    document.getElementById('liveAdvanceBtn').addEventListener('click', () => {
        socketClient.advanceLiveSimulado((response) => {
            if (!response || !response.success) {
                Utils.showToast(response?.error || 'Erro ao avançar', 'error');
            }
        });
    });

    document.getElementById('liveRevoteBtn').addEventListener('click', () => {
        if (!confirm('Repetir a votação desta pergunta? O resultado anterior será substituído.')) return;
        socketClient.revoteLiveSimulado(viewingIndex, (response) => {
            if (!response || !response.success) {
                Utils.showToast(response?.error || 'Erro ao repetir votação', 'error');
                return;
            }
            Utils.showToast('Nova votação iniciada para a turma!', 'success');
        });
    });

    document.getElementById('liveBackToCurrentBtn').addEventListener('click', () => {
        gotoQuestion(currentIndex);
    });

    document.getElementById('liveControlReportBtn').addEventListener('click', () => {
        if (!currentQuestionData || !session) return;
        window.ReportQuestion.open({
            source: 'live-host',
            certCode: session.certCode,
            level: session.level,
            domain: currentQuestionData.domain,
            questionIndex: currentQuestionData.index,
            questionText: currentQuestionData.text,
            options: currentQuestionData.options,
            reporterName: auth.currentUser?.displayName || 'Professor'
        });
    });

    document.getElementById('liveEndSessionBtn').addEventListener('click', () => {
        if (!confirm('Encerrar o simulado para todos os alunos? O resultado final será calculado e salvo no seu histórico.')) return;

        const btn = document.getElementById('liveEndSessionBtn');
        btn.disabled = true;
        socketClient.endLiveSimuladoSession((response) => {
            btn.disabled = false;
            if (!response || !response.success) {
                Utils.showToast(response?.error || 'Erro ao encerrar simulado', 'error');
            }
        });
    });

    // ============================================
    // Tela de resultado final
    // ============================================
    function renderFinalResult(data) {
        const percent = data.score;
        document.getElementById('liveResultScorePercent').textContent = `${percent}%`;

        const circle = document.getElementById('liveResultScoreCircle');
        circle.classList.remove('pass', 'fail');
        circle.classList.add(percent >= PASS_SCORE ? 'pass' : 'fail');

        document.getElementById('liveResultTitle').textContent =
            percent >= PASS_SCORE ? '🎉 Turma Aprovada!' : '📚 A turma precisa estudar mais!';
        document.getElementById('liveResultSubtitle').textContent =
            `${data.correctCount} de ${data.totalQuestions} corretas — ${data.certCode} ` +
            `(${LEVEL_LABELS[data.level] || data.level}) • ${data.participantsCount} aluno(s) • Pontuação mínima de referência: ${PASS_SCORE}%.`;

        const breakdown = document.getElementById('liveResultDomainBreakdown');
        breakdown.innerHTML = data.domainBreakdown.map(domain => `
            <div class="domain-result-row">
                <div class="domain-result-header">
                    <span>${Utils.escapeHtml(domain.name)} <small>(peso ${Math.round(domain.weight * 100)}%)</small></span>
                    <span>${domain.correct}/${domain.total} — ${domain.score}%</span>
                </div>
                <div class="domain-bar-track">
                    <div class="domain-bar-fill ${domain.score >= PASS_SCORE ? 'good' : 'bad'}" style="width: ${domain.score}%"></div>
                </div>
            </div>
        `).join('');

        const reviewList = document.getElementById('liveResultReviewList');
        reviewList.innerHTML = data.review.map((item, i) => {
            const optionsHtml = item.options.map((opt, optIndex) => {
                let cls = 'review-option';
                if (optIndex === item.correct) cls += ' correct-answer';
                if (optIndex === item.yourAnswer && optIndex !== item.correct) cls += ' your-wrong-answer';
                if (optIndex === item.yourAnswer && optIndex === item.correct) cls += ' your-correct-answer';

                const percentBadge = item.totalVotes > 0
                    ? `<span class="live-option-percent">${item.percentages[optIndex]}%</span>`
                    : '';

                return `
                    <div class="${cls}">
                        <span class="exam-option-letter">${LETTERS[optIndex]}</span>
                        <span class="exam-option-text">${Utils.escapeHtml(opt)}</span>
                        ${percentBadge}
                    </div>
                `;
            }).join('');

            return `
                <div class="review-item ${item.isCorrect ? 'correct' : 'incorrect'}">
                    <div class="review-question-header">
                        <span class="review-index">Pergunta ${i + 1}</span>
                        <span class="review-status">${item.isCorrect ? '✅ Turma acertou' : '❌ Turma errou'}</span>
                    </div>
                    <p class="review-question-text">${Utils.escapeHtml(item.text)}</p>
                    <div class="review-options">
                        ${optionsHtml}
                        ${item.totalVotes === 0 ? '<p class="review-no-answer">Nenhum aluno votou nesta pergunta.</p>' : ''}
                    </div>
                    ${item.explanation ? `<div class="review-explanation"><strong>Explicação:</strong> ${Utils.escapeHtml(item.explanation)}</div>` : ''}
                </div>
            `;
        }).join('');
    }

    function resetLiveState() {
        session = null;
        currentIndex = -1;
        viewingIndex = null;
        totalQuestions = 0;
        players = [];
        answeredIndices.clear();
    }

    document.getElementById('restartLiveSimuladoBtn').addEventListener('click', () => {
        resetLiveState();
        window.showSimuladoScreen('selectionScreen');
    });

    window.SimuladoLiveHost = { createRoom };
})();
