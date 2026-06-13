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
                showScreen('denied');
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

        auth.onAuthStateChanged((user) => {
            if (!user) return; // auth.js já redireciona para index.html

            if (user.email !== window.ADMIN_EMAIL) {
                showScreen('denied');
                return;
            }

            loadReports();
        });
    });
})();
