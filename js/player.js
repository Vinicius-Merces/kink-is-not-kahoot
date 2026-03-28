// Player - Tela do Aluno
class PlayerManager {
    constructor() {
        this.roomCode = null;
        this.room = null;
        this.quiz = null;
        this.playerId = null;
        this.playerName = null;
        this.playerAvatar = null;
        this.currentQuestion = null;
        this.questionStartTime = null;
        this.hasAnswered = false;
        this.roomUnsubscribe = null;
        this.scoresUnsubscribe = null;
        this.init();
    }

    async init() {
        const urlParams = new URLSearchParams(window.location.search);
        this.roomCode = urlParams.get('code');
        if (this.roomCode) {
            document.getElementById('roomCodeInput').value = this.roomCode;
            await this.checkRoom();
        }
        this.setupEventListeners();
        this.loadAvatars();
    }

    setupEventListeners() {
        document.getElementById('checkRoomBtn')?.addEventListener('click', () => this.checkRoom());
        document.getElementById('joinGameBtn')?.addEventListener('click', () => this.joinGame());
        document.getElementById('exitGameBtn')?.addEventListener('click', () => window.location.href = 'index.html');
    }

    async checkRoom() {
        const code = document.getElementById('roomCodeInput').value.toUpperCase();
        if (code.length !== 6) {
            Utils.showToast('Código inválido', 'warning');
            return;
        }

        try {
            const roomDoc = await db.collection('rooms').doc(code).get();
            if (!roomDoc.exists) {
                Utils.showToast('Sala não encontrada', 'error');
                return;
            }
            this.room = roomDoc.data();
            this.showScreen('profileScreen');
        } catch (error) {
            Utils.showToast('Erro ao buscar sala', 'error');
        }
    }

    loadAvatars() {
        const grid = document.getElementById('avatarGrid');
        if (!grid) return;
        const avatars = ['avatar1', 'avatar2', 'avatar3', 'avatar4', 'avatar5', 'avatar6', 'avatar7', 'avatar8'];
        grid.innerHTML = avatars.map(id => `
            <div class="avatar-option" data-id="${id}">
                ${Utils.getAvatarEmoji(id)}
            </div>
        `).join('');

        grid.querySelectorAll('.avatar-option').forEach(opt => {
            opt.addEventListener('click', () => {
                grid.querySelectorAll('.avatar-option').forEach(o => o.classList.remove('selected'));
                opt.classList.add('selected');
                this.playerAvatar = opt.dataset.id;
            });
        });
    }

    async joinGame() {
        this.playerName = document.getElementById('nicknameInput').value.trim();
        if (!this.playerName || !this.playerAvatar) {
            Utils.showToast('Escolha um nome e um avatar', 'warning');
            return;
        }

        this.playerId = Utils.generateId();
        const playerRef = db.collection('rooms').doc(this.room.id).collection('players').doc(this.playerId);

        await playerRef.set({
            id: this.playerId,
            name: this.playerName,
            avatar: this.playerAvatar,
            totalScore: 0,
            status: 'ready',
            joinedAt: firebase.firestore.FieldValue.serverTimestamp()
        });

        this.showScreen('waitingScreen');
        this.setupRoomListener();
    }

    setupRoomListener() {
        this.roomUnsubscribe = db.collection('rooms').doc(this.room.id)
            .onSnapshot(doc => {
                const roomData = doc.data();
                if (!roomData) return;
                
                console.log('📡 Status recebido:', roomData.status);
                this.handleRoomUpdate(roomData);
            });
    }

    handleRoomUpdate(roomData) {
        const prevStatus = this.room?.status;
        this.room = roomData;
        const index = roomData.currentQuestionIndex || 0;
        this.currentQuestion = roomData.questions[index];

        switch(roomData.status) {
            case 'loading':
                this.showScreen('loadingScreen');
                break;
            
            case 'active':
                // Se saiu de answering para active, mostra ranking parcial
                if (prevStatus === 'answering' || this.hasAnswered) {
                    this.showRankingScreen();
                } else {
                    this.showScreen('waitingScreen');
                }
                break;

            case 'reading':
                this.hasAnswered = false;
                this.showReadingScreen();
                break;

            case 'answering':
                if (!this.hasAnswered) {
                    this.showQuestionScreen();
                }
                break;

            case 'finished':
                this.showFinalScreen();
                break;
        }
    }

    showReadingScreen() {
        this.showScreen('readingScreen');
        const questionEl = document.getElementById('readingQuestionText');
        if (questionEl) questionEl.textContent = this.currentQuestion.text;
    }

    showQuestionScreen() {
        this.showScreen('questionScreen');
        const textEl = document.getElementById('questionText');
        const optionsEl = document.getElementById('optionsGrid');
        
        if (textEl) textEl.textContent = this.currentQuestion.text;
        if (optionsEl) {
            optionsEl.innerHTML = this.currentQuestion.options.map((opt, i) => `
                <button class="option-btn" onclick="playerManager.submitAnswer(${i})">
                    ${Utils.escapeHtml(opt)}
                </button>
            `).join('');
        }
        
        this.questionStartTime = Date.now();
    }

    async submitAnswer(optionIndex) {
        if (this.hasAnswered) return;
        this.hasAnswered = true;

        const timeTaken = (Date.now() - this.questionStartTime) / 1000;
        const isCorrect = optionIndex === this.currentQuestion.correctOption;
        const points = Utils.calculatePoints(
            Math.max(0, this.currentQuestion.timeLimit - timeTaken),
            this.currentQuestion.timeLimit,
            isCorrect
        );

        // Feedback visual imediato
        this.showScreen('resultScreen');
        const resText = document.getElementById('resultText');
        const ptsText = document.getElementById('pointsEarned');
        
        if (resText) {
            resText.textContent = isCorrect ? '✅ CORRETO!' : '❌ INCORRETO';
            resText.className = isCorrect ? 'result-correct' : 'result-wrong';
        }
        if (ptsText) ptsText.textContent = `+${points} pontos`;

        // Salvar no Firestore
        await db.collection('rooms').doc(this.room.id).collection('answers').add({
            playerId: this.playerId,
            questionIndex: this.room.currentQuestionIndex,
            isCorrect,
            points,
            timestamp: firebase.firestore.FieldValue.serverTimestamp()
        });

        if (points > 0) {
            await db.collection('rooms').doc(this.room.id).collection('players').doc(this.playerId).update({
                totalScore: firebase.firestore.FieldValue.increment(points)
            });
        }
    }

    async showRankingScreen() {
        this.showScreen('rankingScreen');
        const list = document.getElementById('rankingList');
        if (!list) return;

        const snapshot = await db.collection('rooms').doc(this.room.id)
            .collection('players')
            .orderBy('totalScore', 'desc')
            .limit(5)
            .get();

        list.innerHTML = '';
        snapshot.forEach((doc, i) => {
            const p = doc.data();
            list.innerHTML += `
                <div class="ranking-item ${p.id === this.playerId ? 'is-me' : ''}">
                    <span>${i+1}º ${Utils.getAvatarEmoji(p.avatar)} ${Utils.escapeHtml(p.name)}</span>
                    <span>${p.totalScore} pts</span>
                </div>`;
        });
    }

    showScreen(screenId) {
        document.querySelectorAll('.player-screen').forEach(s => s.classList.remove('active'));
        const target = document.getElementById(screenId);
        if (target) target.classList.add('active');
    }

    async showFinalScreen() {
        this.showScreen('finalScreen');
        // Lógica similar ao ranking parcial para o ranking final...
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.playerManager = new PlayerManager();
});