// Report de Erro em Questões de Simulado - KINK is not Kahoot
// Modal compartilhado entre o simulado solo, o painel do professor e o player ao vivo.
(function () {
    const MODAL_ID = 'reportQuestionModal';
    let currentContext = null;

    function ensureModal() {
        let modal = document.getElementById(MODAL_ID);
        if (modal) return modal;

        modal = document.createElement('div');
        modal.id = MODAL_ID;
        modal.className = 'modal';
        modal.setAttribute('role', 'dialog');
        modal.setAttribute('aria-modal', 'true');
        modal.setAttribute('aria-labelledby', 'reportQuestionTitle');
        modal.innerHTML = `
            <div class="modal-content">
                <button class="close" type="button" aria-label="Fechar">&times;</button>
                <h2 id="reportQuestionTitle">🚩 Reportar erro na pergunta</h2>
                <p class="report-question-preview" id="reportQuestionPreview"></p>
                <form id="reportQuestionForm">
                    <textarea id="reportQuestionMessage" placeholder="Descreva o problema (ex: opção correta errada, texto confuso, explicação incorreta)..." maxlength="1000"></textarea>
                    <div class="modal-buttons">
                        <button type="submit" class="btn btn-primary">Enviar report</button>
                        <button type="button" class="btn btn-outline" id="reportQuestionCancel">Cancelar</button>
                    </div>
                </form>
            </div>
        `;
        document.body.appendChild(modal);

        modal.querySelector('.close').addEventListener('click', close);
        modal.querySelector('#reportQuestionCancel').addEventListener('click', close);
        modal.addEventListener('click', (event) => {
            if (event.target === modal) close();
        });
        modal.querySelector('#reportQuestionForm').addEventListener('submit', handleSubmit);

        return modal;
    }

    function close() {
        const modal = document.getElementById(MODAL_ID);
        if (modal) modal.style.display = 'none';
        currentContext = null;
    }

    async function getAuthHeader() {
        try {
            const user = window.firebase && firebase.auth ? firebase.auth().currentUser : null;
            if (!user) return null;
            const token = await user.getIdToken();
            return `Bearer ${token}`;
        } catch (error) {
            return null;
        }
    }

    async function handleSubmit(event) {
        event.preventDefault();
        if (!currentContext) return;

        const submitBtn = event.target.querySelector('button[type="submit"]');
        const textarea = document.getElementById('reportQuestionMessage');
        const message = textarea.value.trim();
        const originalLabel = submitBtn.textContent;

        submitBtn.disabled = true;
        submitBtn.textContent = 'Enviando...';

        try {
            const headers = { 'Content-Type': 'application/json' };
            const authHeader = await getAuthHeader();
            if (authHeader) headers['Authorization'] = authHeader;

            const res = await fetch('/api/simulado/report', {
                method: 'POST',
                headers,
                body: JSON.stringify({ ...currentContext, message })
            });

            const data = await res.json();
            if (data.success) {
                Utils.showToast('Obrigado! Seu report foi enviado.', 'success');
                close();
            } else {
                Utils.showToast(data.error || 'Erro ao enviar report', 'error');
            }
        } catch (error) {
            console.error('Erro ao enviar report:', error);
            Utils.showToast('Erro ao enviar report. Tente novamente.', 'error');
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = originalLabel;
        }
    }

    function open(context) {
        currentContext = context || {};
        const modal = ensureModal();

        const text = currentContext.questionText || '';
        document.getElementById('reportQuestionPreview').textContent =
            text.length > 160 ? `${text.slice(0, 160)}…` : text;
        document.getElementById('reportQuestionMessage').value = '';

        modal.style.display = 'block';
        document.getElementById('reportQuestionMessage').focus();
    }

    window.ReportQuestion = { open };
})();
