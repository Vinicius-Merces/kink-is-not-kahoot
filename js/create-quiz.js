// Gerenciador de criação/edição de quizzes

// Normaliza question.correct (número legado ou array) para sempre retornar um array de índices
function normalizeCorrect(correct) {
    if (Array.isArray(correct)) return correct;
    if (correct === undefined || correct === null) return [];
    return [correct];
}

class QuizEditor {
    constructor() {
        console.log('🔧 QuizEditor instanciado');
        this.questions = [];
        this.editingQuestionIndex = null;
        this.quizId = null;
        this.isEditMode = false;
        this.init();
    }

    async init() {
        console.log('🔧 QuizEditor inicializando...');
        
        // Aguardar autenticação
        auth.onAuthStateChanged(async (user) => {
            console.log('📡 Auth state changed:', user ? user.displayName : 'null');
            
            if (!user) {
                Utils.showToast('Você precisa estar logado', 'warning');
                setTimeout(() => window.location.href = 'index.html', 1500);
                return;
            }

            const urlParams = new URLSearchParams(window.location.search);
            this.quizId = urlParams.get('edit') || urlParams.get('view');
            console.log('📝 Quiz ID:', this.quizId || 'Novo quiz');

            if (this.quizId) {
                this.isEditMode = true;
                await this.loadQuiz();
            }

            this.setupEventListeners();
            this.renderQuestions();
            console.log('✅ QuizEditor pronto');
        });
    }

    async loadQuiz() {
        try {
            const quizDoc = await db.collection('quizzes').doc(this.quizId).get();
            if (!quizDoc.exists) {
                Utils.showToast('Quiz não encontrado', 'error');
                setTimeout(() => window.location.href = 'my-quizzes.html', 1500);
                return;
            }
            
            const quiz = { id: quizDoc.id, ...quizDoc.data() };
            
            // Verificar permissão
            if (quiz.creatorId !== auth.currentUser.uid) {
                Utils.showToast('Você não tem permissão para editar este quiz', 'error');
                setTimeout(() => window.location.href = 'my-quizzes.html', 1500);
                return;
            }
            
            // Preencher formulário
            const titleInput = document.getElementById('quizTitle');
            const descriptionInput = document.getElementById('quizDescription');
            const randomizeCheckbox = document.getElementById('randomizeQuestions');
            const showCorrectCheckbox = document.getElementById('showCorrectAnswer');
            
            if (titleInput) titleInput.value = quiz.title || '';
            if (descriptionInput) descriptionInput.value = quiz.description || '';
            if (randomizeCheckbox) randomizeCheckbox.checked = quiz.settings?.randomizeQuestions || false;
            if (showCorrectCheckbox) showCorrectCheckbox.checked = quiz.settings?.showCorrectAnswer !== false;
            
            this.questions = quiz.questions || [];
            this.renderQuestions();
            Utils.showToast('Quiz carregado para edição', 'success');
        } catch (error) {
            console.error('Erro ao carregar quiz:', error);
            Utils.showToast('Erro ao carregar quiz: ' + error.message, 'error');
        }
    }

    setupEventListeners() {
        console.log('🔧 Configurando event listeners...');

        // Adicionar pergunta
        const addBtn = document.getElementById('addQuestionBtn');
        if (addBtn) {
            addBtn.addEventListener('click', () => this.openQuestionModal());
        } else {
            console.error('❌ addQuestionBtn não encontrado');
        }

        // Fechar modal (X)
        const closeModal = document.querySelector('#questionModal .close');
        if (closeModal) {
            closeModal.addEventListener('click', () => this.closeModal());
        }

        // Cancelar no modal
        const cancelModal = document.getElementById('cancelQuestionBtn');
        if (cancelModal) {
            cancelModal.addEventListener('click', () => this.closeModal());
        }

        // Formulário da pergunta
        const questionForm = document.getElementById('questionForm');
        if (questionForm) {
            questionForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.saveQuestion();
            });
        }

        // Adicionar opção
        const addOptionBtn = document.getElementById('addOptionBtn');
        if (addOptionBtn) {
            addOptionBtn.addEventListener('click', () => this.addOption());
        }

        // Botão Salvar Quiz
        const saveQuizBtn = document.getElementById('saveQuizBtn');
        if (saveQuizBtn) {
            console.log('✅ Botão Salvar Quiz encontrado');
            saveQuizBtn.addEventListener('click', async (e) => {
                e.preventDefault();
                console.log('💾 Botão Salvar clicado');
                
                // Desabilitar botão durante salvamento
                saveQuizBtn.disabled = true;
                const originalText = saveQuizBtn.textContent;
                saveQuizBtn.textContent = '💾 Salvando...';
                
                const success = await this.saveQuiz();
                
                if (success) {
                    console.log('✅ Quiz salvo com sucesso!');
                    Utils.showToast('Quiz salvo com sucesso!', 'success');
                    setTimeout(() => {
                        window.location.href = 'my-quizzes.html';
                    }, 1500);
                } else {
                    console.log('❌ Erro ao salvar quiz');
                    saveQuizBtn.disabled = false;
                    saveQuizBtn.textContent = originalText;
                }
            });
        } else {
            console.error('❌ Botão saveQuizBtn não encontrado');
        }

        // Botão Cancelar (principal)
        const cancelBtn = document.getElementById('cancelBtn');
        if (cancelBtn) {
            console.log('✅ Botão Cancelar encontrado');
            cancelBtn.addEventListener('click', () => {
                console.log('❌ Cancelar clicado');
                window.location.href = 'my-quizzes.html';
            });
        } else {
            console.error('❌ Botão cancelBtn não encontrado');
        }

        // Botão logout (se existir)
        const logoutBtn = document.getElementById('logoutBtn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', async () => {
                await auth.signOut();
                window.location.href = 'index.html';
            });
        }

        console.log('✅ Event listeners configurados');
    }

    openQuestionModal(questionIndex = null) {
        this.editingQuestionIndex = questionIndex;
        const modal = document.getElementById('questionModal');
        const modalTitle = document.getElementById('modalTitle');
        
        if (modalTitle) {
            modalTitle.textContent = questionIndex !== null ? 'Editar Pergunta' : 'Nova Pergunta';
        }

        if (questionIndex !== null && this.questions[questionIndex]) {
            this.loadQuestionToForm(this.questions[questionIndex]);
        } else {
            this.clearForm();
        }

        if (modal) modal.style.display = 'block';
    }

    clearForm() {
        const questionText = document.getElementById('questionText');
        const timeLimit = document.getElementById('timeLimit');
        const readingTime = document.getElementById('readingTime');
        const pointsMultiplier = document.getElementById('pointsMultiplier');
        const optionsList = document.getElementById('optionsList');

        if (questionText) questionText.value = '';
        if (timeLimit) timeLimit.value = '30';
        if (readingTime) readingTime.value = '5';
        if (pointsMultiplier) pointsMultiplier.value = '1';
        if (optionsList) optionsList.innerHTML = '';

        // Adicionar 4 opções vazias
        for (let i = 0; i < 4; i++) {
            this.addOption();
        }

        // Resetar checkboxes de resposta correta
        const checkboxes = document.querySelectorAll('input[name="correctOption"]');
        checkboxes.forEach(checkbox => checkbox.checked = false);
    }

    loadQuestionToForm(question) {
        const questionText = document.getElementById('questionText');
        const timeLimit = document.getElementById('timeLimit');
        const readingTime = document.getElementById('readingTime');
        const pointsMultiplier = document.getElementById('pointsMultiplier');
        const optionsList = document.getElementById('optionsList');

        if (questionText) questionText.value = question.text;
        if (timeLimit) timeLimit.value = question.timeLimit || 30;
        if (readingTime) readingTime.value = question.readingTime ?? 5;
        if (pointsMultiplier) pointsMultiplier.value = question.pointsMultiplier || 1;
        if (optionsList) optionsList.innerHTML = '';

        const correctIndices = normalizeCorrect(question.correct);

        question.options.forEach((option, index) => {
            const optionDiv = this.createOptionElement(index);
            const input = optionDiv.querySelector('.option-text');
            if (input) input.value = option;

            const checkbox = optionDiv.querySelector('input[type="checkbox"]');
            if (checkbox) {
                checkbox.value = index;
                if (correctIndices.includes(index)) {
                    checkbox.checked = true;
                }
            }

            if (optionsList) optionsList.appendChild(optionDiv);
        });
    }

    addOption() {
        const optionsList = document.getElementById('optionsList');
        if (!optionsList) return;
        
        const optionCount = optionsList.children.length;
        const optionDiv = this.createOptionElement(optionCount);
        optionsList.appendChild(optionDiv);
    }

    createOptionElement(index) {
        const div = document.createElement('div');
        div.className = 'option-item';
        div.innerHTML = `
            <input type="text" class="option-text" placeholder="Opção ${String.fromCharCode(65 + index)}" required>
            <label class="radio-label">
                <input type="checkbox" name="correctOption" value="${index}"> Correta
            </label>
            <button type="button" class="remove-option" onclick="this.parentElement.remove()">🗑️</button>
        `;
        return div;
    }

    saveQuestion() {
        const questionText = document.getElementById('questionText')?.value.trim();
        const timeLimit = parseInt(document.getElementById('timeLimit')?.value || '30');

        let readingTime = parseInt(document.getElementById('readingTime')?.value ?? '5');
        if (Number.isNaN(readingTime)) readingTime = 5;
        readingTime = Math.min(60, Math.max(0, readingTime));

        let pointsMultiplier = parseInt(document.getElementById('pointsMultiplier')?.value || '1');
        if (![1, 2, 3].includes(pointsMultiplier)) pointsMultiplier = 1;

        if (!questionText) {
            Utils.showToast('Por favor, digite a pergunta', 'warning');
            return;
        }

        // Coletar opções
        const options = [];
        const optionInputs = document.querySelectorAll('#optionsList .option-text');

        optionInputs.forEach((input, idx) => {
            const value = input.value.trim();
            if (value) {
                options.push(value);
            }
        });

        // Verificar opções corretas (pode marcar mais de uma)
        const correctIndices = [];
        const checkboxes = document.querySelectorAll('input[name="correctOption"]');
        checkboxes.forEach((checkbox, idx) => {
            if (checkbox.checked && idx < options.length) {
                correctIndices.push(idx);
            }
        });

        if (options.length < 2) {
            Utils.showToast('Adicione pelo menos 2 opções de resposta', 'warning');
            return;
        }

        if (correctIndices.length === 0) {
            Utils.showToast('Marque ao menos uma resposta correta', 'warning');
            return;
        }

        const question = {
            id: Utils.generateId(),
            text: questionText,
            options: options,
            correct: correctIndices,
            timeLimit: timeLimit,
            readingTime: readingTime,
            pointsMultiplier: pointsMultiplier
        };

        if (this.editingQuestionIndex !== null) {
            this.questions[this.editingQuestionIndex] = question;
            Utils.showToast('Pergunta atualizada!', 'success');
        } else {
            this.questions.push(question);
            Utils.showToast('Pergunta adicionada!', 'success');
        }

        this.renderQuestions();
        this.closeModal();
    }

    renderQuestions() {
        const container = document.getElementById('questionsList');
        if (!container) return;
        
        if (this.questions.length === 0) {
            container.innerHTML = `
                <div class="empty-questions">
                    <p>📝 Nenhuma pergunta adicionada ainda</p>
                    <p>Clique no botão acima para começar a criar seu quiz</p>
                </div>
            `;
            return;
        }
        
        container.innerHTML = this.questions.map((question, index) => {
            const correctLabels = normalizeCorrect(question.correct)
                .map(i => String.fromCharCode(65 + i))
                .join(', ');
            const multiplier = question.pointsMultiplier || 1;

            return `
            <div class="question-item" data-index="${index}">
                <div class="question-text">
                    <span class="question-number-badge">${index + 1}</span>
                    <span>${Utils.escapeHtml(question.text)}</span>
                </div>
                <div class="question-meta">
                    <span>📝 ${question.options.length} opções</span>
                    <span>⏱️ Resposta: ${question.timeLimit}s</span>
                    <span>📖 Leitura: ${question.readingTime ?? 5}s</span>
                    <span>✅ Resposta${correctLabels.includes(',') ? 's' : ''} correta${correctLabels.includes(',') ? 's' : ''}: ${correctLabels}</span>
                    ${multiplier > 1 ? `<span>🔥 Vale ${multiplier}x</span>` : ''}
                </div>
                <div class="question-actions">
                    <button class="edit-question" data-index="${index}">✏️ Editar</button>
                    <button class="delete-question" data-index="${index}">🗑️ Excluir</button>
                </div>
            </div>
        `;
        }).join('');

        // Adicionar event listeners
        document.querySelectorAll('.edit-question').forEach(btn => {
            btn.addEventListener('click', () => {
                const index = parseInt(btn.dataset.index);
                this.openQuestionModal(index);
            });
        });
        
        document.querySelectorAll('.delete-question').forEach(btn => {
            btn.addEventListener('click', () => {
                if (confirm('Tem certeza que deseja excluir esta pergunta?')) {
                    const index = parseInt(btn.dataset.index);
                    this.questions.splice(index, 1);
                    this.renderQuestions();
                    Utils.showToast('Pergunta excluída!', 'success');
                }
            });
        });
    }

    async saveQuiz() {
        const title = document.getElementById('quizTitle')?.value.trim();
        const description = document.getElementById('quizDescription')?.value.trim();
        const randomize = document.getElementById('randomizeQuestions')?.checked || false;
        const showCorrect = document.getElementById('showCorrectAnswer')?.checked || false;

        if (!title) {
            Utils.showToast('Por favor, insira um título para o quiz', 'warning');
            return false;
        }
        
        if (this.questions.length === 0) {
            Utils.showToast('Adicione pelo menos uma pergunta ao quiz', 'warning');
            return false;
        }

        // Validação individual das perguntas
        for (let i = 0; i < this.questions.length; i++) {
            const q = this.questions[i];
            if (!q.text || q.text.trim() === '') {
                Utils.showToast(`Pergunta ${i + 1} está vazia`, 'warning');
                return false;
            }
            if (!q.options || q.options.length < 2) {
                Utils.showToast(`Pergunta ${i + 1} precisa ter pelo menos 2 opções`, 'warning');
                return false;
            }
            if (!Array.isArray(q.correct) || q.correct.length === 0) {
                Utils.showToast(`Pergunta ${i + 1} precisa ter uma resposta correta marcada`, 'warning');
                return false;
            }
        }

        const quizData = {
            title: title,
            description: description,
            questions: this.questions,
            settings: {
                randomizeQuestions: randomize,
                showCorrectAnswer: showCorrect,
                defaultTimeLimit: 30
            },
            updatedAt: firebase.firestore.FieldValue.serverTimestamp()
        };

        try {
            if (this.isEditMode && this.quizId) {
                // Atualizar quiz existente
                await db.collection('quizzes').doc(this.quizId).update(quizData);
                Utils.showToast('Quiz atualizado com sucesso!', 'success');
                return true;
            } else {
                // Criar novo quiz
                const quizId = Utils.generateId();
                await db.collection('quizzes').doc(quizId).set({
                    ...quizData,
                    id: quizId,
                    creatorId: auth.currentUser.uid,
                    creatorName: auth.currentUser.displayName || auth.currentUser.email,
                    createdAt: firebase.firestore.FieldValue.serverTimestamp(),
                    timesPlayed: 0
                });
                Utils.showToast('Quiz criado com sucesso!', 'success');
                return true;
            }
        } catch (error) {
            console.error('Erro ao salvar quiz:', error);
            Utils.showToast('Erro ao salvar quiz: ' + error.message, 'error');
            return false;
        }
    }

    closeModal() {
        const modal = document.getElementById('questionModal');
        if (modal) modal.style.display = 'none';
        this.editingQuestionIndex = null;
    }
}

// Inicializar quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', () => {
    console.log('📄 DOM carregado, iniciando QuizEditor...');
    window.quizEditor = new QuizEditor();
});