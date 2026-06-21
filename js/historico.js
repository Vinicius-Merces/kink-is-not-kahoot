// Histórico de Simulados - lista de tentativas e revisão detalhada de cada uma
(function () {
    const LEVEL_LABELS = {
        iniciante: 'Iniciante',
        medio: 'Médio',
        avancado: 'Avançado'
    };

    const PASS_SCORE = 70;

    const screens = {
        list: document.getElementById('historyListScreen'),
        detail: document.getElementById('historyDetailScreen')
    };

    function showScreen(name) {
        Object.values(screens).forEach(el => el.classList.remove('active'));
        screens[name].classList.add('active');
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    function formatDate(isoString) {
        if (!isoString) return '';
        return new Date(isoString).toLocaleString('pt-BR', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    // ============================================
    // Lista de tentativas
    // ============================================
    async function loadHistory() {
        const user = auth.currentUser;
        if (!user) return;

        try {
            const token = await user.getIdToken();
            const res = await fetch('/api/simulado/history', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            const data = await res.json();
            if (!data.success) throw new Error(data.error || 'Erro ao carregar histórico');
            renderHistoryList(data.attempts);
        } catch (error) {
            console.error('Erro ao carregar histórico:', error);
            document.getElementById('historyList').innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">⚠️</div>
                    <h3>Não foi possível carregar seu histórico</h3>
                    <p>Recarregue a página e tente novamente.</p>
                </div>
            `;
        }
    }

    function renderHistoryList(attempts) {
        const container = document.getElementById('historyList');

        if (!attempts || attempts.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">📭</div>
                    <h3>Nenhuma tentativa ainda</h3>
                    <p>Faça um simulado para começar a construir seu histórico.</p>
                    <a href="simulados.html" class="btn btn-primary">🚀 Ir para Simulados</a>
                </div>
            `;
            return;
        }

        container.innerHTML = attempts.map(attempt => `
            <div class="history-card ${attempt.score >= PASS_SCORE ? 'pass' : 'fail'}" data-attempt-id="${attempt.id}">
                <div class="history-card-score">
                    <span>${attempt.score}%</span>
                </div>
                <div class="history-card-info">
                    <h3>${Utils.escapeHtml(attempt.certCode)} <small>(${LEVEL_LABELS[attempt.level] || attempt.level})</small></h3>
                    <p>${Utils.escapeHtml(attempt.certName)}</p>
                    <p class="history-card-meta">${attempt.correctCount}/${attempt.totalQuestions} corretas • ${formatDate(attempt.createdAt)}</p>
                    ${attempt.mode === 'live' ? `<span class="history-live-badge">🎓 Modo Professor • Sala ${Utils.escapeHtml(attempt.roomCode || '')} • ${attempt.participantsCount || 0} aluno(s)</span>` : ''}
                </div>
                <button type="button" class="btn btn-outline">Ver detalhes</button>
            </div>
        `).join('');

        container.querySelectorAll('.history-card').forEach(card => {
            card.addEventListener('click', () => loadAttemptDetail(card.dataset.attemptId));
        });
    }

    // ============================================
    // Detalhe de uma tentativa
    // ============================================
    async function loadAttemptDetail(attemptId) {
        const user = auth.currentUser;
        if (!user) return;

        try {
            const token = await user.getIdToken();
            const res = await fetch(`/api/simulado/history/${attemptId}`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            const data = await res.json();
            if (!data.success) throw new Error(data.error || 'Erro ao carregar detalhe da tentativa');
            renderDetail(data.attempt);
            showScreen('detail');
        } catch (error) {
            console.error('Erro ao carregar detalhe da tentativa:', error);
            Utils.showToast(error.message || 'Erro ao carregar detalhe da tentativa', 'error');
        }
    }

    function renderDetail(attempt) {
        const isLive = attempt.mode === 'live';
        const percent = attempt.score;
        document.getElementById('detailScorePercent').textContent = `${percent}%`;

        const circle = document.getElementById('detailScoreCircle');
        circle.classList.remove('pass', 'fail');
        circle.classList.add(percent >= PASS_SCORE ? 'pass' : 'fail');

        const title = document.getElementById('detailTitle');
        const subtitle = document.getElementById('detailSubtitle');
        title.textContent = percent >= PASS_SCORE
            ? (isLive ? '🎉 Turma Aprovada!' : '🎉 Aprovado!')
            : (isLive ? '📚 A turma precisa estudar mais!' : '📚 Continue estudando!');
        subtitle.textContent = isLive
            ? `${attempt.correctCount} de ${attempt.totalQuestions} corretas — ${attempt.certCode} ` +
              `(${LEVEL_LABELS[attempt.level] || attempt.level}) • Sala ${attempt.roomCode || ''} • ${attempt.participantsCount || 0} aluno(s) • ${formatDate(attempt.createdAt)}. Pontuação mínima de referência: ${PASS_SCORE}%.`
            : `${attempt.correctCount} de ${attempt.totalQuestions} corretas — ${attempt.certCode} ` +
              `(${LEVEL_LABELS[attempt.level] || attempt.level}) • ${formatDate(attempt.createdAt)}. Pontuação mínima de referência: ${PASS_SCORE}%.`;

        const breakdown = document.getElementById('detailDomainBreakdown');
        breakdown.innerHTML = attempt.domainBreakdown.map(domain => {
            const needsReview = domain.score < PASS_SCORE;
            const review = needsReview && window.StudyProgress
                ? window.StudyProgress.getReviewChapters(attempt.certCode, domain.id)
                : null;

            const reviewLinksHtml = review
                ? `<div class="domain-review-links">
                        📖 Revisar:
                        ${review.chapters.map(capNum => `<a href="${review.trilhaUrl}#cap${capNum}" class="domain-review-link">Cap. ${capNum}</a>`).join('')}
                   </div>`
                : '';

            return `
                <div class="domain-result-row">
                    <div class="domain-result-header">
                        <span>${Utils.escapeHtml(domain.name)} <small>(peso ${Math.round(domain.weight * 100)}%)</small></span>
                        <span>${domain.correct}/${domain.total} — ${domain.score}%</span>
                    </div>
                    <div class="domain-bar-track">
                        <div class="domain-bar-fill ${domain.score >= PASS_SCORE ? 'good' : 'bad'}" style="width: ${domain.score}%"></div>
                    </div>
                    ${reviewLinksHtml}
                </div>
            `;
        }).join('');

        const reviewList = document.getElementById('detailReviewList');
        reviewList.innerHTML = attempt.review.map((item, i) => {
            const optionsHtml = item.options.map((opt, optIndex) => {
                let cls = 'review-option';
                if (optIndex === item.correct) cls += ' correct-answer';
                if (optIndex === item.yourAnswer && optIndex !== item.correct) cls += ' your-wrong-answer';
                if (optIndex === item.yourAnswer && optIndex === item.correct) cls += ' your-correct-answer';

                const percentBadge = (isLive && item.totalVotes > 0)
                    ? `<span class="live-option-percent">${item.percentages[optIndex]}%</span>`
                    : '';

                return `
                    <div class="${cls}">
                        <span class="exam-option-letter">${String.fromCharCode(65 + optIndex)}</span>
                        <span class="exam-option-text">${Utils.escapeHtml(opt)}</span>
                        ${percentBadge}
                    </div>
                `;
            }).join('');

            const noAnswerHtml = isLive
                ? (item.totalVotes === 0 ? '<p class="review-no-answer">Nenhum aluno votou nesta pergunta.</p>' : '')
                : (item.yourAnswer === null ? '<p class="review-no-answer">Você não respondeu esta pergunta.</p>' : '');

            const statusLabel = isLive
                ? (item.isCorrect ? '✅ Turma acertou' : '❌ Turma errou')
                : (item.isCorrect ? '✅ Correta' : '❌ Incorreta');

            return `
                <div class="review-item ${item.isCorrect ? 'correct' : 'incorrect'}">
                    <div class="review-question-header">
                        <span class="review-index">Pergunta ${i + 1}</span>
                        <span class="review-status">${statusLabel}</span>
                    </div>
                    <p class="review-question-text">${Utils.escapeHtml(item.text)}</p>
                    <div class="review-options">
                        ${optionsHtml}
                        ${noAnswerHtml}
                    </div>
                    ${item.explanation ? `<div class="review-explanation"><strong>Explicação:</strong> ${Utils.escapeHtml(item.explanation)}</div>` : ''}
                </div>
            `;
        }).join('');
    }

    document.getElementById('backToHistoryBtn').addEventListener('click', () => {
        showScreen('list');
    });

    // ============================================
    // Inicialização
    // ============================================
    let initialized = false;
    auth.onAuthStateChanged((user) => {
        if (user && !initialized) {
            initialized = true;
            loadHistory();
        }
    });
})();
