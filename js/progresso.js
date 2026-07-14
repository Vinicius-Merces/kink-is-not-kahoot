// Meu Progresso — dashboard consolidado de desempenho nos simulados e trilhas
(function () {
    const PASS_SCORE = 70;
    const LEVEL_LABELS = { iniciante: 'Iniciante', medio: 'Médio', avancado: 'Avançado' };

    // Totais de capítulos por trilha (para a barra de leitura)
    const TRILHA_TOTALS = {
        'saa-c03': { label: 'SAA-C03 · Solutions Architect', total: 21, url: 'trilha-saa.html' },
        'dva-c02': { label: 'DVA-C02 · Developer', total: 14, url: 'trilha-dva.html' },
        'dea-c01': { label: 'DEA-C01 · Data Engineer', total: 17, url: 'trilha-dea.html' }
    };

    // certId -> certCode (o StudyProgress é indexado por certCode)
    const CERT_CODE = { 'saa-c03': 'SAA-C03', 'dva-c02': 'DVA-C02', 'dea-c01': 'DEA-C01', 'clf-c02': 'CLF-C02' };

    const content = document.getElementById('progressoContent');
    let allAttempts = [];
    let currentCert = 'all';

    async function loadProgress() {
        const user = auth.currentUser;
        if (!user) return;
        try {
            const token = await user.getIdToken();
            const res = await fetch('/api/simulado/history?include=breakdowns', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            const data = await res.json();
            if (!data.success) throw new Error(data.error || 'Erro ao carregar progresso');
            allAttempts = (data.attempts || []).filter(a => a.mode !== 'live-host');
            render();
        } catch (error) {
            console.error('Erro ao carregar progresso:', error);
            content.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">⚠️</div>
                    <h3>Não foi possível carregar seu progresso</h3>
                    <p>Recarregue a página e tente novamente.</p>
                </div>`;
        }
    }

    function render() {
        if (allAttempts.length === 0) {
            content.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">🌱</div>
                    <h3>Seu progresso começa no primeiro simulado</h3>
                    <p>Faça um simulado para ver aqui sua evolução, os domínios e temas a reforçar, e o avanço nas trilhas.</p>
                    <a href="simulados.html" class="btn btn-primary btn-large">🚀 Fazer meu primeiro simulado</a>
                </div>`;
            return;
        }

        // Ordena do mais antigo para o mais novo (evolução temporal)
        const chronological = [...allAttempts].sort((a, b) =>
            new Date(a.createdAt || 0) - new Date(b.createdAt || 0));

        const certsPresent = Array.from(new Set(allAttempts.map(a => a.certId).filter(Boolean)));
        const filtered = currentCert === 'all'
            ? chronological
            : chronological.filter(a => a.certId === currentCert);

        content.innerHTML = `
            ${renderCertFilter(certsPresent)}
            ${renderStatCards(filtered)}
            ${renderEvolutionChart(filtered)}
            ${renderDomainAggregate(filtered)}
            ${renderWeakTopics(filtered)}
            ${renderTrilhaProgress()}
        `;

        // liga os filtros
        content.querySelectorAll('.cert-filter-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                currentCert = btn.dataset.cert;
                render();
            });
        });
    }

    function renderCertFilter(certsPresent) {
        if (certsPresent.length < 2) return '';
        const btn = (id, label) =>
            `<button class="cert-filter-btn ${currentCert === id ? 'active' : ''}" data-cert="${id}">${label}</button>`;
        return `
            <div class="cert-filter">
                ${btn('all', 'Todas')}
                ${certsPresent.map(id => btn(id, (CERT_CODE[id] || id))).join('')}
            </div>`;
    }

    function renderStatCards(attempts) {
        const count = attempts.length;
        const best = attempts.reduce((m, a) => Math.max(m, a.score || 0), 0);
        const last5 = attempts.slice(-5);
        const avg5 = last5.length
            ? Math.round(last5.reduce((s, a) => s + (a.score || 0), 0) / last5.length)
            : 0;
        // getStreak() retorna { current, longest } — exibir só o numero atual
        const streakData = window.StudyProgress ? window.StudyProgress.getStreak() : null;
        const streak = (streakData && typeof streakData === 'object')
            ? (streakData.current || 0)
            : (streakData || 0);
        const passed = attempts.filter(a => (a.score || 0) >= PASS_SCORE).length;

        const card = (icon, value, label, cls = '') =>
            `<div class="stat-card ${cls}">
                <div class="stat-icon">${icon}</div>
                <div class="stat-value">${value}</div>
                <div class="stat-label">${label}</div>
            </div>`;

        return `
            <div class="stat-cards">
                ${card('📝', count, count === 1 ? 'simulado feito' : 'simulados feitos')}
                ${card('🏆', best + '%', 'melhor pontuação', best >= PASS_SCORE ? 'good' : '')}
                ${card('📈', avg5 + '%', 'média (últimas 5)', avg5 >= PASS_SCORE ? 'good' : 'weak')}
                ${card('✅', passed, passed === 1 ? 'aprovação' : 'aprovações', passed > 0 ? 'good' : '')}
                ${card('🔥', streak, streak === 1 ? 'dia de sequência' : 'dias de sequência')}
            </div>`;
    }

    function renderEvolutionChart(attempts) {
        if (attempts.length < 2) {
            return `<div class="form-card">
                <h3>📈 Evolução da pontuação</h3>
                <p class="progress-hint">Faça pelo menos 2 simulados para ver sua curva de evolução aqui.</p>
            </div>`;
        }
        // últimas 20 tentativas para não poluir
        const pts = attempts.slice(-20);
        const W = 640, H = 220, padL = 36, padR = 16, padT = 16, padB = 34;
        const innerW = W - padL - padR, innerH = H - padT - padB;
        const n = pts.length;
        const x = i => padL + (n === 1 ? innerW / 2 : (i / (n - 1)) * innerW);
        const y = v => padT + innerH - (v / 100) * innerH;

        const cut = y(PASS_SCORE);
        const linePath = pts.map((a, i) => `${i === 0 ? 'M' : 'L'} ${x(i).toFixed(1)} ${y(a.score || 0).toFixed(1)}`).join(' ');
        const dots = pts.map((a, i) => {
            const good = (a.score || 0) >= PASS_SCORE;
            return `<circle cx="${x(i).toFixed(1)}" cy="${y(a.score || 0).toFixed(1)}" r="4"
                        fill="${good ? '#2dd4bf' : '#ff6b6b'}"><title>${a.score}% — ${(CERT_CODE[a.certId] || '')} ${LEVEL_LABELS[a.level] || ''}</title></circle>`;
        }).join('');
        const gridY = [0, 25, 50, 75, 100].map(v =>
            `<line x1="${padL}" y1="${y(v)}" x2="${W - padR}" y2="${y(v)}" stroke="#ffffff12"/>
             <text x="${padL - 8}" y="${y(v) + 4}" fill="#8892a6" font-size="12" text-anchor="end">${v}</text>`).join('');

        return `
            <div class="form-card">
                <h3>📈 Evolução da pontuação <small>(últimos ${n})</small></h3>
                <svg class="evolution-chart" viewBox="0 0 ${W} ${H}" role="img" aria-label="Gráfico de evolução da pontuação nos simulados">
                    ${gridY}
                    <line x1="${padL}" y1="${cut}" x2="${W - padR}" y2="${cut}" stroke="#ffd166" stroke-dasharray="5 4" stroke-width="1.5"/>
                    <text x="${W - padR}" y="${cut - 6}" fill="#ffd166" font-size="12" text-anchor="end">meta ${PASS_SCORE}%</text>
                    <path d="${linePath}" fill="none" stroke="#cdd3de" stroke-width="2"/>
                    ${dots}
                </svg>
            </div>`;
    }

    function renderDomainAggregate(attempts) {
        const agg = new Map(); // domainName -> {correct,total}
        attempts.forEach(a => (a.domainBreakdown || []).forEach(d => {
            const cur = agg.get(d.name) || { correct: 0, total: 0 };
            cur.correct += d.correct || 0;
            cur.total += d.total || 0;
            agg.set(d.name, cur);
        }));
        if (agg.size === 0) return '';

        const rows = Array.from(agg.entries())
            .map(([name, s]) => ({ name, score: s.total ? Math.round((s.correct / s.total) * 100) : 0, ...s }))
            .sort((a, b) => a.score - b.score);

        return `
            <div class="form-card">
                <h3>🧭 Desempenho por domínio <small>(acumulado)</small></h3>
                <div class="domain-breakdown">
                    ${rows.map(d => `
                        <div class="domain-result-row">
                            <div class="domain-result-header">
                                <span>${Utils.escapeHtml(d.name)}</span>
                                <span>${d.correct}/${d.total} — ${d.score}%</span>
                            </div>
                            <div class="domain-bar-track">
                                <div class="domain-bar-fill ${d.score >= PASS_SCORE ? 'good' : 'bad'}" style="width:${d.score}%"></div>
                            </div>
                        </div>`).join('')}
                </div>
            </div>`;
    }

    function renderWeakTopics(attempts) {
        const agg = new Map(); // topicId -> {name,correct,total}
        attempts.forEach(a => (a.topicBreakdown || []).forEach(t => {
            const cur = agg.get(t.id) || { name: t.name, correct: 0, total: 0 };
            cur.correct += t.correct || 0;
            cur.total += t.total || 0;
            agg.set(t.id, cur);
        }));
        // Só temas com amostra relevante (>=3 questões acumuladas)
        const weak = Array.from(agg.entries())
            .map(([id, s]) => ({ id, ...s, score: s.total ? Math.round((s.correct / s.total) * 100) : 0 }))
            .filter(t => t.total >= 3 && t.score < PASS_SCORE)
            .sort((a, b) => a.score - b.score)
            .slice(0, 8);

        if (weak.length === 0) {
            return `<div class="form-card">
                <h3>🎯 Temas a reforçar</h3>
                <p class="progress-hint">Nenhum tema com aproveitamento abaixo de ${PASS_SCORE}% (com amostra suficiente). Continue assim! 🎉</p>
            </div>`;
        }

        const certForLink = currentCert !== 'all' ? currentCert : null;
        return `
            <div class="form-card">
                <h3>🎯 Temas a reforçar <small>(seus pontos mais fracos)</small></h3>
                <p class="progress-hint">Ordenados do pior aproveitamento para o melhor. Clique para praticar exatamente esse tema.</p>
                <div class="topic-breakdown">
                    ${weak.map(t => {
                        const cert = certForLink || guessCertForTopic(t.id, attempts);
                        const link = cert
                            ? `<a class="topic-practice-link" href="simulados.html?cert=${encodeURIComponent(cert)}&topic=${encodeURIComponent(t.id)}&n=10">🎯 Praticar</a>`
                            : '';
                        return `<div class="topic-result-chip weak">
                            <span class="topic-chip-name">${Utils.escapeHtml(t.name)}</span>
                            <span class="topic-chip-score">${t.correct}/${t.total} — ${t.score}%</span>
                            ${link}
                        </div>`;
                    }).join('')}
                </div>
            </div>`;
    }

    // Quando o filtro é "Todas", tenta descobrir a que cert o tema pertence
    // olhando de qual tentativa ele veio (o primeiro match serve como link).
    function guessCertForTopic(topicId, attempts) {
        for (const a of attempts) {
            if ((a.topicBreakdown || []).some(t => t.id === topicId) && a.certId) return a.certId;
        }
        return null;
    }

    function renderTrilhaProgress() {
        if (!window.StudyProgress) return '';
        const cards = Object.entries(TRILHA_TOTALS).map(([id, info]) => {
            const code = CERT_CODE[id];
            let done = 0;
            try {
                const set = window.StudyProgress.getCompletedSet(id);
                done = set ? set.size : 0;
            } catch (_) { done = 0; }
            const pct = info.total ? Math.round((done / info.total) * 100) : 0;
            return `
                <div class="trilha-progress-row">
                    <div class="domain-result-header">
                        <span><a href="${info.url}" class="trilha-progress-link">${Utils.escapeHtml(info.label)}</a></span>
                        <span>${done}/${info.total} caps — ${pct}%</span>
                    </div>
                    <div class="domain-bar-track">
                        <div class="domain-bar-fill ${pct >= 100 ? 'good' : ''}" style="width:${pct}%"></div>
                    </div>
                </div>`;
        }).join('');

        return `
            <div class="form-card">
                <h3>📚 Progresso nas trilhas <small>(capítulos concluídos)</small></h3>
                ${cards}
            </div>`;
    }

    // Inicialização
    let initialized = false;
    auth.onAuthStateChanged((user) => {
        if (user && !initialized) {
            initialized = true;
            loadProgress();
        }
    });
})();
