// Simulados AWS - Seleção, execução e correção de simulados de certificação
(function () {
    const CERT_ICONS = {
        'clf-c02': '☁️',
        'saa-c03': '🏗️',
        'dva-c02': '👨‍💻'
    };

    const LEVEL_LABELS = {
        iniciante: 'Iniciante',
        medio: 'Médio',
        avancado: 'Avançado'
    };

    const PASS_SCORE = 70;

    let certifications = [];
    let selectedCertId = null;
    let selectedLevel = null;
    let selectedMode = 'solo'; // 'solo' ou 'live' (Modo Professor)
    let selectedFeedbackMode = 'exam'; // 'exam' (correção só no final) ou 'study' (feedback a cada pergunta)

    // Estado do simulado em andamento
    let currentSimulado = null; // { simuladoId, certCode, certName, level, domains, questions, totalQuestions }
    let userAnswers = {};
    let questionFeedback = {}; // questionId -> { isCorrect, correct, explanation } (Modo Estudo)
    let currentQuestionIndex = 0;

    const SCREEN_IDS = {
        selection: 'selectionScreen',
        exam: 'examScreen',
        result: 'resultScreen'
    };

    function showScreen(nameOrId) {
        const targetId = SCREEN_IDS[nameOrId] || nameOrId;
        document.querySelectorAll('.simulado-screen').forEach(el => el.classList.remove('active'));
        const target = document.getElementById(targetId);
        if (target) target.classList.add('active');
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
    window.showSimuladoScreen = showScreen;

    // ============================================
    // Carregamento de certificações
    // ============================================
    async function loadCertifications() {
        try {
            const res = await fetch('/api/simulado/certifications');
            const data = await res.json();
            if (!data.success) throw new Error('Falha ao carregar certificações');
            certifications = data.certifications;
            renderCertGrid();
        } catch (error) {
            console.error('Erro ao carregar certificações:', error);
            document.getElementById('certGrid').innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">⚠️</div>
                    <h3>Não foi possível carregar os simulados</h3>
                    <p>Recarregue a página e tente novamente.</p>
                </div>
            `;
        }
    }

    function renderCertGrid() {
        const grid = document.getElementById('certGrid');
        grid.innerHTML = certifications.map(cert => `
            <div class="cert-card" data-cert-id="${cert.id}">
                <div class="cert-icon">${CERT_ICONS[cert.id] || '📘'}</div>
                <h3>${cert.shortName}</h3>
                <p class="cert-code">${cert.code}</p>
            </div>
        `).join('');

        grid.querySelectorAll('.cert-card').forEach(card => {
            card.addEventListener('click', () => selectCertification(card.dataset.certId));
        });
    }

    function selectCertification(certId) {
        selectedCertId = certId;
        document.querySelectorAll('.cert-card').forEach(card => {
            card.classList.toggle('selected', card.dataset.certId === certId);
        });

        const cert = certifications.find(c => c.id === certId);
        document.getElementById('configCertName').textContent = `Configurar Simulado — ${cert.shortName}`;
        renderLevelSelector(cert);

        const defaultLevel = cert.levels.find(l => l.totalQuestions > 0) || cert.levels[0];
        selectLevel(cert, defaultLevel.id);

        document.getElementById('simuladoConfig').style.display = 'block';
        document.getElementById('simuladoConfig').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    function renderLevelSelector(cert) {
        const container = document.getElementById('levelSelector');
        container.innerHTML = cert.levels.map(level => `
            <button type="button" class="level-btn" data-level-id="${level.id}" ${level.totalQuestions === 0 ? 'disabled' : ''}>
                ${LEVEL_LABELS[level.id] || level.id}
                <small>${level.totalQuestions} perguntas</small>
            </button>
        `).join('');

        container.querySelectorAll('.level-btn').forEach(btn => {
            btn.addEventListener('click', () => selectLevel(cert, btn.dataset.levelId));
        });
    }

    function selectLevel(cert, levelId) {
        selectedLevel = levelId;
        document.querySelectorAll('.level-btn').forEach(btn => {
            btn.classList.toggle('selected', btn.dataset.levelId === levelId);
        });

        const level = cert.levels.find(l => l.id === levelId);
        renderDomainPreview(level);

        const max = Math.max(1, Math.min(80, level.totalQuestions || 1));
        const range = document.getElementById('numQuestionsRange');
        range.max = max;
        range.value = Math.min(20, max);
        document.getElementById('maxQuestionsLabel').textContent = max;
        document.getElementById('numQuestionsValue').textContent = range.value;
    }

    function renderDomainPreview(level) {
        const container = document.getElementById('domainPreview');
        if (!level.domains || level.domains.length === 0) {
            container.innerHTML = '<p class="placeholder">Nenhum domínio configurado para este nível ainda</p>';
            return;
        }
        container.innerHTML = `
            <h4>Distribuição de domínios (proporção oficial do exame)</h4>
            ${level.domains.map(domain => `
                <div class="domain-bar-row">
                    <span class="domain-bar-label">${Utils.escapeHtml(domain.name)}</span>
                    <div class="domain-bar-track">
                        <div class="domain-bar-fill" style="width: ${Math.round(domain.weight * 100)}%"></div>
                    </div>
                    <span class="domain-bar-percent">${Math.round(domain.weight * 100)}%</span>
                </div>
            `).join('')}
        `;
    }

    document.getElementById('numQuestionsRange').addEventListener('input', (e) => {
        document.getElementById('numQuestionsValue').textContent = e.target.value;
    });

    // ============================================
    // Alternância de modo (Solo / Professor ao vivo)
    // ============================================
    document.querySelectorAll('#simuladoModeToggle .mode-toggle-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            selectedMode = btn.dataset.mode;
            document.querySelectorAll('#simuladoModeToggle .mode-toggle-btn').forEach(b => b.classList.toggle('selected', b === btn));
            document.getElementById('startSimuladoBtn').style.display = selectedMode === 'solo' ? '' : 'none';
            document.getElementById('createLiveRoomBtn').style.display = selectedMode === 'live' ? '' : 'none';
            document.getElementById('feedbackModeToggle').style.display = selectedMode === 'solo' ? '' : 'none';
            document.getElementById('feedbackModeHint').style.display = selectedMode === 'solo' ? '' : 'none';
        });
    });

    // ============================================
    // Alternância de feedback (Modo Prova / Modo Estudo)
    // ============================================
    document.querySelectorAll('#feedbackModeToggle .mode-toggle-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            selectedFeedbackMode = btn.dataset.feedbackMode;
            document.querySelectorAll('#feedbackModeToggle .mode-toggle-btn').forEach(b => b.classList.toggle('selected', b === btn));
        });
    });

    // ============================================
    // Iniciar Simulado
    // ============================================
    document.getElementById('startSimuladoBtn').addEventListener('click', async () => {
        if (!selectedCertId || !selectedLevel) return;

        const user = auth.currentUser;
        if (!user) {
            Utils.showToast('Faça login para iniciar um simulado', 'warning');
            return;
        }

        const numQuestions = parseInt(document.getElementById('numQuestionsRange').value, 10);
        const btn = document.getElementById('startSimuladoBtn');
        btn.disabled = true;
        btn.textContent = '⏳ Preparando simulado...';

        try {
            const token = await user.getIdToken();
            const res = await fetch('/api/simulado/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ certId: selectedCertId, level: selectedLevel, numQuestions })
            });

            const data = await res.json();
            if (!data.success) throw new Error(data.error || 'Erro ao iniciar simulado');

            currentSimulado = data;
            userAnswers = {};
            questionFeedback = {};
            currentQuestionIndex = 0;

            startExam();
        } catch (error) {
            console.error('Erro ao iniciar simulado:', error);
            Utils.showToast(error.message || 'Erro ao iniciar simulado', 'error');
        } finally {
            btn.disabled = false;
            btn.textContent = '🚀 Iniciar Simulado';
        }
    });

    // ============================================
    // Criar Sala de Simulado ao Vivo (Modo Professor)
    // ============================================
    document.getElementById('createLiveRoomBtn').addEventListener('click', () => {
        if (!selectedCertId || !selectedLevel) return;
        const numQuestions = parseInt(document.getElementById('numQuestionsRange').value, 10);
        window.SimuladoLiveHost.createRoom(selectedCertId, selectedLevel, numQuestions);
    });

    // ============================================
    // Tela do Simulado
    // ============================================
    function startExam() {
        document.getElementById('examCertBadge').textContent =
            `${currentSimulado.certCode} • ${LEVEL_LABELS[currentSimulado.level] || currentSimulado.level}`;
        renderQuestionDots();
        renderQuestion(0);
        showScreen('exam');
    }

    function renderQuestionDots() {
        const container = document.getElementById('examQuestionDots');
        container.innerHTML = currentSimulado.questions.map((q, i) => `
            <button type="button" class="exam-dot" data-index="${i}" title="Pergunta ${i + 1}" aria-label="Pergunta ${i + 1}">${i + 1}</button>
        `).join('');

        container.querySelectorAll('.exam-dot').forEach(dot => {
            dot.addEventListener('click', () => {
                renderQuestion(parseInt(dot.dataset.index, 10));
            });
        });
    }

    function updateQuestionDots() {
        const dots = document.querySelectorAll('#examQuestionDots .exam-dot');
        dots.forEach((dot, i) => {
            const question = currentSimulado.questions[i];
            const answered = Object.prototype.hasOwnProperty.call(userAnswers, question.id);
            dot.classList.toggle('answered', answered);
            dot.classList.toggle('current', i === currentQuestionIndex);
            if (i === currentQuestionIndex) {
                dot.setAttribute('aria-current', 'true');
            } else {
                dot.removeAttribute('aria-current');
            }
            dot.setAttribute('aria-label', `Pergunta ${i + 1}${answered ? ' (respondida)' : ''}`);
        });
    }

    function renderQuestion(index) {
        const total = currentSimulado.questions.length;
        const question = currentSimulado.questions[index];
        currentQuestionIndex = index;

        const domain = currentSimulado.domains.find(d => d.id === question.domain);
        document.getElementById('examDomainTag').textContent = domain ? domain.name : question.domain;
        document.getElementById('examQuestionText').textContent = question.text;

        const progressPercent = Math.round(((index + 1) / total) * 100);
        document.getElementById('examProgressFill').style.width = `${progressPercent}%`;
        document.getElementById('examProgressLabel').textContent = `Pergunta ${index + 1} de ${total}`;

        const optionsContainer = document.getElementById('examOptions');
        const selectedAnswer = userAnswers[question.id];
        const feedback = selectedFeedbackMode === 'study' ? questionFeedback[question.id] : null;

        optionsContainer.innerHTML = question.options.map((option, i) => {
            let cls = 'exam-option';
            if (feedback) {
                cls += ' disabled';
                if (i === feedback.correct) cls += ' correct-answer';
                if (i === selectedAnswer && i !== feedback.correct) cls += ' your-wrong-answer';
                if (i === selectedAnswer && i === feedback.correct) cls += ' your-correct-answer';
            } else if (selectedAnswer === i) {
                cls += ' selected';
            }
            return `
                <button type="button" class="${cls}" data-option-index="${i}" ${feedback ? 'disabled' : ''}>
                    <span class="exam-option-letter">${String.fromCharCode(65 + i)}</span>
                    <span class="exam-option-text">${Utils.escapeHtml(option)}</span>
                </button>
            `;
        }).join('');

        optionsContainer.querySelectorAll('.exam-option').forEach(optionBtn => {
            optionBtn.addEventListener('click', async () => {
                const optionIndex = parseInt(optionBtn.dataset.optionIndex, 10);
                userAnswers[question.id] = optionIndex;

                if (selectedFeedbackMode === 'study') {
                    await checkAnswer(question.id, optionIndex);
                }

                renderQuestion(currentQuestionIndex);
            });
        });

        const feedbackBox = document.getElementById('examFeedback');
        if (feedback) {
            feedbackBox.className = `exam-feedback ${feedback.isCorrect ? 'correct' : 'incorrect'}`;
            feedbackBox.innerHTML = `
                <div class="exam-feedback-title">${feedback.isCorrect ? '✅ Resposta correta!' : '❌ Resposta incorreta'}</div>
                ${feedback.explanation ? `<p>${Utils.escapeHtml(feedback.explanation)}</p>` : ''}
            `;
            feedbackBox.style.display = 'block';
        } else {
            feedbackBox.style.display = 'none';
            feedbackBox.innerHTML = '';
        }

        document.getElementById('prevQuestionBtn').disabled = index === 0;

        const nextBtn = document.getElementById('nextQuestionBtn');
        nextBtn.style.visibility = index === total - 1 ? 'hidden' : 'visible';

        updateQuestionDots();
    }

    document.getElementById('prevQuestionBtn').addEventListener('click', () => {
        if (currentQuestionIndex > 0) renderQuestion(currentQuestionIndex - 1);
    });

    document.getElementById('nextQuestionBtn').addEventListener('click', () => {
        if (currentQuestionIndex < currentSimulado.questions.length - 1) renderQuestion(currentQuestionIndex + 1);
    });

    // Verifica a resposta de uma pergunta (Modo Estudo: feedback imediato)
    async function checkAnswer(questionId, answerIndex) {
        const user = auth.currentUser;
        if (!user) return;

        try {
            const token = await user.getIdToken();
            const res = await fetch(`/api/simulado/${currentSimulado.simuladoId}/check`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ questionId, answer: answerIndex })
            });

            const data = await res.json();
            if (!data.success) throw new Error(data.error || 'Erro ao verificar resposta');

            questionFeedback[questionId] = data;
        } catch (error) {
            console.error('Erro ao verificar resposta:', error);
            Utils.showToast(error.message || 'Erro ao verificar resposta', 'error');
        }
    }

    document.getElementById('examReportBtn').addEventListener('click', () => {
        const question = currentSimulado.questions[currentQuestionIndex];
        window.ReportQuestion.open({
            source: 'solo',
            certCode: currentSimulado.certCode,
            level: currentSimulado.level,
            domain: question.domain,
            questionId: question.id,
            questionText: question.text,
            options: question.options
        });
    });

    // ============================================
    // Finalizar Simulado
    // ============================================
    document.getElementById('finishExamBtn').addEventListener('click', () => {
        const total = currentSimulado.questions.length;
        const answered = Object.keys(userAnswers).length;
        const modal = document.getElementById('confirmFinishModal');

        if (answered < total) {
            document.getElementById('confirmFinishMessage').textContent =
                `Você respondeu ${answered} de ${total} perguntas. Perguntas não respondidas serão consideradas incorretas. Deseja finalizar mesmo assim?`;
        } else {
            document.getElementById('confirmFinishMessage').textContent =
                `Você respondeu todas as ${total} perguntas. Deseja finalizar o simulado?`;
        }

        modal.style.display = 'block';
    });

    document.getElementById('confirmFinishNo').addEventListener('click', () => {
        document.getElementById('confirmFinishModal').style.display = 'none';
    });

    document.getElementById('confirmFinishYes').addEventListener('click', async () => {
        document.getElementById('confirmFinishModal').style.display = 'none';
        await submitSimulado();
    });

    async function submitSimulado() {
        const user = auth.currentUser;
        if (!user) {
            Utils.showToast('Sessão expirada. Faça login novamente.', 'error');
            return;
        }

        const finishBtn = document.getElementById('finishExamBtn');
        finishBtn.disabled = true;
        finishBtn.textContent = '⏳ Corrigindo simulado...';

        try {
            const token = await user.getIdToken();
            const res = await fetch(`/api/simulado/${currentSimulado.simuladoId}/submit`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ answers: userAnswers })
            });

            const data = await res.json();
            if (!data.success) throw new Error(data.error || 'Erro ao corrigir simulado');

            renderResults(data);
            showScreen('result');
        } catch (error) {
            console.error('Erro ao finalizar simulado:', error);
            Utils.showToast(error.message || 'Erro ao finalizar simulado', 'error');
        } finally {
            finishBtn.disabled = false;
            finishBtn.textContent = '🏁 Finalizar Simulado';
        }
    }

    // ============================================
    // Tela de Resultado
    // ============================================
    function renderResults(result) {
        const percent = result.score;
        document.getElementById('resultScorePercent').textContent = `${percent}%`;

        const circle = document.getElementById('resultScoreCircle');
        circle.classList.remove('pass', 'fail');
        circle.classList.add(percent >= PASS_SCORE ? 'pass' : 'fail');

        const title = document.getElementById('resultTitle');
        const subtitle = document.getElementById('resultSubtitle');
        title.textContent = percent >= PASS_SCORE ? '🎉 Aprovado!' : '📚 Continue estudando!';
        subtitle.textContent =
            `${result.correctCount} de ${result.totalQuestions} corretas — ${result.certCode} ` +
            `(${LEVEL_LABELS[result.level] || result.level}). Pontuação mínima de referência: ${PASS_SCORE}%.`;

        const breakdown = document.getElementById('domainBreakdown');
        breakdown.innerHTML = result.domainBreakdown.map(domain => `
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

        const reviewList = document.getElementById('reviewList');
        reviewList.innerHTML = result.review.map((item, i) => {
            const optionsHtml = item.options.map((opt, optIndex) => {
                let cls = 'review-option';
                if (optIndex === item.correct) cls += ' correct-answer';
                if (optIndex === item.yourAnswer && optIndex !== item.correct) cls += ' your-wrong-answer';
                if (optIndex === item.yourAnswer && optIndex === item.correct) cls += ' your-correct-answer';
                return `
                    <div class="${cls}">
                        <span class="exam-option-letter">${String.fromCharCode(65 + optIndex)}</span>
                        <span class="exam-option-text">${Utils.escapeHtml(opt)}</span>
                    </div>
                `;
            }).join('');

            return `
                <div class="review-item ${item.isCorrect ? 'correct' : 'incorrect'}">
                    <div class="review-question-header">
                        <span class="review-index">Pergunta ${i + 1}</span>
                        <span class="review-status">${item.isCorrect ? '✅ Correta' : '❌ Incorreta'}</span>
                    </div>
                    <p class="review-question-text">${Utils.escapeHtml(item.text)}</p>
                    <div class="review-options">
                        ${optionsHtml}
                        ${item.yourAnswer === null ? '<p class="review-no-answer">Você não respondeu esta pergunta.</p>' : ''}
                    </div>
                    ${item.explanation ? `<div class="review-explanation"><strong>Explicação:</strong> ${Utils.escapeHtml(item.explanation)}</div>` : ''}
                </div>
            `;
        }).join('');
    }

    document.getElementById('restartSimuladoBtn').addEventListener('click', () => {
        currentSimulado = null;
        userAnswers = {};
        questionFeedback = {};
        currentQuestionIndex = 0;
        document.getElementById('simuladoConfig').style.display = 'none';
        document.querySelectorAll('.cert-card').forEach(card => card.classList.remove('selected'));
        selectedCertId = null;
        selectedLevel = null;
        showScreen('selection');
    });

    // ============================================
    // Inicialização
    // ============================================
    loadCertifications();
})();
