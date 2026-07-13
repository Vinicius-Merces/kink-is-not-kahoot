// Painel Admin - lista e gerencia reports de questões com erro
(function () {
    const STATUS_LABELS = { open: '🚩 Aberto', resolved: '✅ Resolvido' };
    const LETTERS = ['A', 'B', 'C', 'D', 'E', 'F'];

    let allReports = [];
    let currentFilter = 'open';

    const screens = {
        loading: document.getElementById('adminLoadingScreen'),
        denied: document.getElementById('adminDeniedScreen'),
        reports: document.getElementById('adminReportsScreen')
    };

    /**
     * Explica POR QUE o acesso foi negado, em vez de mostrar só um 🚫.
     * Consulta o servidor, que é a autoridade real, e mostra as duas visões.
     */
    async function mostrarDiagnostico(user) {
        const box = document.getElementById('adminDiag');
        if (!box) return;

        const linhas = [
            `<strong>Você está logado como:</strong> <code>${user.email || '(sem e-mail)'}</code>`,
            `<strong>O painel espera:</strong> <code>${window.ADMIN_EMAIL || '(não definido)'}</code>`
        ];

        try {
            const token = await user.getIdToken();
            const res = await fetch('/api/admin/whoami', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            const d = await res.json();

            linhas.push(`<strong>O servidor te vê como:</strong> <code>${d.email || '(nulo)'}</code>`);

            if (d.firebaseAdminReady === false) {
                linhas.push(
                    '<p class="admin-diag-cause">⚠️ <strong>Causa provável:</strong> o Firebase Admin ' +
                    'não inicializou no servidor. Sem ele, o back-end não consegue ler seu e-mail ' +
                    'do token e nega tudo. Verifique a variável de ambiente ' +
                    '<code>FIREBASE_SERVICE_ACCOUNT_BASE64</code> no SquareCloud.</p>'
                );
            } else if (d.isAdmin) {
                linhas.push(
                    '<p class="admin-diag-cause">ℹ️ O <strong>servidor te reconhece como admin</strong>, ' +
                    'mas o front-end barrou. Provável divergência entre o e-mail em ' +
                    '<code>js/auth.js</code> e o do <code>server.js</code>.</p>'
                );
            }
        } catch (e) {
            linhas.push('<p class="admin-diag-cause">⚠️ Não foi possível consultar o servidor.</p>');
        }

        box.innerHTML = linhas.join('<br>');
        box.hidden = false;
    }

    /** Preview do rebrand: alterna o iframe entre a marca nova e a atual. */
    function iniciarPreviewRebrand() {
        const painel = document.getElementById('rebrandPreview');
        if (!painel || !window.Brand) return;

        const B = window.Brand;

        // Depois da virada o preview perde a razão de existir.
        if (B.isLive()) { painel.remove(); return; }

        const dateEl = document.getElementById('previewDate');
        if (dateEl) dateEl.textContent = B.cutoverLabel();

        const cd = document.getElementById('previewCountdown');
        if (cd) {
            const d = B.daysUntilCutover();
            cd.textContent = d === 0 ? 'É hoje.' : `Faltam ${d} ${d === 1 ? 'dia' : 'dias'}.`;
        }

        const frame = document.getElementById('rebrandFrame');
        const link = document.getElementById('previewOpenLink');

        painel.querySelectorAll('.preview-tab').forEach(btn => {
            btn.addEventListener('click', () => {
                painel.querySelectorAll('.preview-tab').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                const url = `index.html?brand=${btn.dataset.brand}`;
                if (frame) frame.src = url;
                if (link) link.href = url;
            });
        });
    }

    function showScreen(name) {
        Object.values(screens).forEach(el => el && el.classList.remove('active'));
        if (screens[name]) screens[name].classList.add('active');
    }

    function formatDate(isoString) {
        if (!isoString) return '';
        return new Date(isoString).toLocaleString('pt-BR', {
            day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit'
        });
    }

    async function loadReports() {
        try {
            const token = await auth.currentUser.getIdToken();
            const res = await fetch('/api/admin/reports', {
                headers: { 'Authorization': `Bearer ${token}` }
            });

            if (res.status === 403) {
                await mostrarDiagnostico(auth.currentUser);
                showScreen('denied');
                return;
            }

            // 503 = o SERVIDOR está mal configurado (Firebase Admin não subiu).
            // Não é falta de permissão sua — e a distinção importa.
            if (res.status === 503) {
                const d = await res.json().catch(() => ({}));
                showScreen('reports');   // mantém o preview do rebrand visível
                document.getElementById('adminReportsList').innerHTML = `
                    <div class="admin-diag">
                        <strong>⚙️ Configuração do servidor pendente</strong><br>
                        ${Utils.escapeHtml(d.error || 'Firebase Admin não inicializado.')}
                        <p class="admin-diag-cause">
                            O servidor não consegue validar credenciais sem a chave do Firebase, então
                            recusa as rotas de admin (falha fechada — o correto).<br><br>
                            <strong>Como resolver:</strong> no painel do SquareCloud, defina a variável de
                            ambiente <code>FIREBASE_SERVICE_ACCOUNT_BASE64</code>
                            (gere o valor com <code>node scripts/print-firebase-env.js</code>) e reinicie a aplicação.
                            <br><br>
                            O preview do rebrand abaixo não depende disso e continua funcionando.
                        </p>
                    </div>`;
                return;
            }

            const data = await res.json();
            if (!data.success) throw new Error(data.error || 'Erro ao carregar reports');

            allReports = data.reports || [];
            renderReports();
            showScreen('reports');
        } catch (error) {
            console.error('Erro ao carregar reports:', error);
            Utils.showToast('Erro ao carregar reports', 'error');
            showScreen('reports');
            document.getElementById('adminReportsList').innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">⚠️</div>
                    <h3>Não foi possível carregar os reports</h3>
                    <p>Recarregue a página e tente novamente.</p>
                </div>
            `;
        }
    }

    function renderReports() {
        const container = document.getElementById('adminReportsList');
        const filtered = currentFilter === 'all'
            ? allReports
            : allReports.filter(r => (r.status || 'open') === currentFilter);

        if (filtered.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">📭</div>
                    <h3>Nenhum report aqui</h3>
                    <p>${currentFilter === 'open' ? 'Nenhuma pergunta foi reportada com erro até agora.' : 'Nada para mostrar com esse filtro.'}</p>
                </div>
            `;
            return;
        }

        container.innerHTML = filtered.map(report => {
            const status = report.status || 'open';

            const optionsHtml = Array.isArray(report.options) && report.options.length
                ? `<ul class="admin-report-options">${report.options.map((opt, i) => `
                    <li>${LETTERS[i] || (i + 1)}. ${Utils.escapeHtml(opt)}</li>
                `).join('')}</ul>`
                : '';

            const metaParts = [report.source, report.certCode, report.level]
                .filter(Boolean)
                .map(part => Utils.escapeHtml(part))
                .join(' · ');

            return `
                <div class="admin-report-card status-${status}" data-id="${report.id}">
                    <div class="admin-report-header">
                        <span class="admin-report-status status-${status}">${STATUS_LABELS[status] || Utils.escapeHtml(status)}</span>
                        ${metaParts ? `<span class="admin-report-meta">${metaParts}</span>` : ''}
                        <span class="admin-report-date">${formatDate(report.createdAt)}</span>
                    </div>

                    <p class="admin-report-question">${Utils.escapeHtml(report.questionText || '')}</p>
                    ${optionsHtml}
                    ${report.domain ? `<p class="admin-report-domain">📂 Domínio: ${Utils.escapeHtml(report.domain)}</p>` : ''}
                    ${report.message ? `<div class="admin-report-message"><strong>Mensagem do usuário:</strong><br>${Utils.escapeHtml(report.message)}</div>` : ''}

                    <div class="admin-report-reporter">
                        Reportado por: ${Utils.escapeHtml(report.reporterName || report.reporterEmail || 'Anônimo')}
                    </div>

                    <div class="admin-report-actions">
                        ${status === 'open'
                            ? `<button class="btn btn-outline btn-small admin-resolve-btn">✅ Marcar como resolvido</button>`
                            : `<button class="btn btn-outline btn-small admin-reopen-btn">↩️ Reabrir</button>`}
                        <button class="btn btn-danger btn-small admin-delete-btn">🗑️ Excluir</button>
                    </div>
                </div>
            `;
        }).join('');

        container.querySelectorAll('.admin-resolve-btn').forEach(btn => {
            btn.addEventListener('click', () => updateReportStatus(btn.closest('.admin-report-card').dataset.id, 'resolved'));
        });
        container.querySelectorAll('.admin-reopen-btn').forEach(btn => {
            btn.addEventListener('click', () => updateReportStatus(btn.closest('.admin-report-card').dataset.id, 'open'));
        });
        container.querySelectorAll('.admin-delete-btn').forEach(btn => {
            btn.addEventListener('click', () => deleteReport(btn.closest('.admin-report-card').dataset.id));
        });
    }

    async function updateReportStatus(id, status) {
        try {
            const token = await auth.currentUser.getIdToken();
            const res = await fetch(`/api/admin/reports/${id}`, {
                method: 'PATCH',
                headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
                body: JSON.stringify({ status })
            });
            const data = await res.json();
            if (!data.success) throw new Error(data.error || 'Erro ao atualizar report');

            const report = allReports.find(r => r.id === id);
            if (report) report.status = status;
            renderReports();
            Utils.showToast(status === 'resolved' ? 'Report marcado como resolvido' : 'Report reaberto', 'success');
        } catch (error) {
            console.error('Erro ao atualizar report:', error);
            Utils.showToast('Erro ao atualizar report', 'error');
        }
    }

    async function deleteReport(id) {
        if (!confirm('Excluir este report permanentemente?')) return;

        try {
            const token = await auth.currentUser.getIdToken();
            const res = await fetch(`/api/admin/reports/${id}`, {
                method: 'DELETE',
                headers: { 'Authorization': `Bearer ${token}` }
            });
            const data = await res.json();
            if (!data.success) throw new Error(data.error || 'Erro ao excluir report');

            allReports = allReports.filter(r => r.id !== id);
            renderReports();
            Utils.showToast('Report excluído', 'success');
        } catch (error) {
            console.error('Erro ao excluir report:', error);
            Utils.showToast('Erro ao excluir report', 'error');
        }
    }

    document.addEventListener('DOMContentLoaded', () => {
        document.querySelectorAll('.admin-filter-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.admin-filter-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                currentFilter = btn.dataset.filter;
                renderReports();
            });
        });

        const refreshBtn = document.getElementById('adminRefreshBtn');
        if (refreshBtn) refreshBtn.addEventListener('click', loadReports);

        iniciarPreviewRebrand();

        auth.onAuthStateChanged(async (user) => {
            if (!user) return; // auth.js já redireciona para index.html

            // Comparação tolerante (o servidor já fazia assim; o frontend não).
            // Diferença de maiúscula ou espaço sobrando não deve barrar o admin.
            const meu = (user.email || '').trim().toLowerCase();
            const esperado = (window.ADMIN_EMAIL || '').trim().toLowerCase();

            if (!esperado) {
                // ADMIN_EMAIL não carregou (ordem de scripts) — não bloqueia às cegas:
                // deixa o servidor decidir, que é a autoridade real.
                console.warn('[admin] window.ADMIN_EMAIL indefinido — validando pelo servidor');
            } else if (meu !== esperado) {
                await mostrarDiagnostico(user);
                showScreen('denied');
                return;
            }

            loadReports();
        });
    });
})();
