const functions = require('firebase-functions');
const admin = require('firebase-admin');

// Inicializar Firebase Admin
admin.initializeApp();
const db = admin.firestore();

// ============================================
// 1. FUNÇÃO: CALCULAR PONTUAÇÃO DA RESPOSTA
// ============================================
exports.calculateScore = functions.firestore
    .document('rooms/{roomId}/answers/{answerId}')
    .onCreate(async (snap, context) => {
        const { roomId, answerId } = context.params;
        const answerData = snap.data();
        
        console.log(`📝 Nova resposta recebida na sala ${roomId}`);
        console.log(`   Jogador: ${answerData.playerName}`);
        console.log(`   Pergunta: ${answerData.questionIndex}`);
        
        try {
            // Buscar informações da sala
            const roomDoc = await db.collection('rooms').doc(roomId).get();
            if (!roomDoc.exists) {
                console.log('❌ Sala não encontrada');
                return null;
            }
            
            const room = roomDoc.data();
            
            // Buscar o quiz
            const quizDoc = await db.collection('quizzes').doc(room.quizId).get();
            if (!quizDoc.exists) {
                console.log('❌ Quiz não encontrado');
                return null;
            }
            
            const quiz = quizDoc.data();
            const question = quiz.questions[answerData.questionIndex];
            
            if (!question) {
                console.log('❌ Pergunta não encontrada');
                return null;
            }
            
            // Calcular pontuação
            const isCorrect = (answerData.answer === question.correct);
            let points = 0;
            
            if (isCorrect) {
                const timeLimit = question.timeLimit || 30;
                const responseTime = Math.min(answerData.responseTime || timeLimit, timeLimit);
                const speedBonus = Math.max(0, (timeLimit - responseTime) / timeLimit);
                points = Math.floor(1000 * speedBonus);
                points = Math.max(0, Math.min(1000, points));
                
                console.log(`✅ Resposta correta! ${points} pontos (tempo: ${responseTime}s)`);
            } else {
                console.log(`❌ Resposta errada! 0 pontos`);
            }
            
            // Atualizar resposta
            await snap.ref.update({
                points: points,
                isCorrect: isCorrect,
                calculatedAt: admin.firestore.FieldValue.serverTimestamp()
            });
            
            // Atualizar pontuação do jogador
            const scoreRef = db.collection('rooms').doc(roomId)
                .collection('scores').doc(answerData.playerId);
            
            const scoreDoc = await scoreRef.get();
            const currentScore = scoreDoc.exists ? scoreDoc.data().totalScore || 0 : 0;
            const newScore = currentScore + points;
            
            await scoreRef.set({
                playerId: answerData.playerId,
                playerName: answerData.playerName,
                avatar: answerData.avatar,
                totalScore: newScore,
                [`answers.q${answerData.questionIndex}`]: {
                    points: points,
                    correct: isCorrect,
                    time: answerData.responseTime,
                    answer: answerData.answer
                },
                updatedAt: admin.firestore.FieldValue.serverTimestamp()
            }, { merge: true });
            
            console.log(`🏆 ${answerData.playerName}: ${newScore} pontos`);
            return { success: true, points: points };
            
        } catch (error) {
            console.error('❌ Erro:', error);
            return null;
        }
    });

// ============================================
// 2. FUNÇÃO: FINALIZAR PERGUNTA AUTOMATICAMENTE
// ============================================
exports.autoFinishQuestion = functions.firestore
    .document('rooms/{roomId}')
    .onUpdate(async (change, context) => {
        const { roomId } = context.params;
        const before = change.before.data();
        const after = change.after.data();
        
        if (after.status === 'question_active' && before.status !== 'question_active') {
            const timeLimit = after.currentQuestionData?.timeLimit || 30;
            console.log(`⏰ Timer iniciado: ${timeLimit}s para pergunta ${after.currentQuestionIndex}`);
            
            await new Promise(resolve => setTimeout(resolve, timeLimit * 1000));
            
            const roomNow = await db.collection('rooms').doc(roomId).get();
            const roomData = roomNow.data();
            
            if (roomData && roomData.status === 'question_active') {
                await db.collection('rooms').doc(roomId).update({
                    status: 'active'
                });
                
                // Estatísticas
                const answersSnapshot = await db.collection('rooms')
                    .doc(roomId)
                    .collection('answers')
                    .where('questionIndex', '==', roomData.currentQuestionIndex)
                    .get();
                
                const totalAnswers = answersSnapshot.size;
                let correctAnswers = 0;
                answersSnapshot.forEach(doc => {
                    if (doc.data().isCorrect) correctAnswers++;
                });
                
                console.log(`⏰ Pergunta finalizada! Acertos: ${correctAnswers}/${totalAnswers}`);
            }
        }
        return null;
    });

// ============================================
// 3. FUNÇÃO: LIMPAR SALAS ANTIGAS (diária)
// ============================================
exports.cleanOldRooms = functions.pubsub
    .schedule('0 0 * * *')
    .timeZone('America/Sao_Paulo')
    .onRun(async () => {
        console.log('🧹 Limpando salas antigas...');
        
        const cutoffDate = new Date();
        cutoffDate.setHours(cutoffDate.getHours() - 24);
        
        try {
            const roomsSnapshot = await db.collection('rooms')
                .where('createdAt', '<', cutoffDate)
                .where('active', '==', false)
                .get();
            
            let deletedCount = 0;
            
            for (const roomDoc of roomsSnapshot.docs) {
                const roomId = roomDoc.id;
                const batch = db.batch();
                
                const players = await db.collection('rooms').doc(roomId).collection('players').get();
                const answers = await db.collection('rooms').doc(roomId).collection('answers').get();
                const scores = await db.collection('rooms').doc(roomId).collection('scores').get();
                
                players.forEach(doc => batch.delete(doc.ref));
                answers.forEach(doc => batch.delete(doc.ref));
                scores.forEach(doc => batch.delete(doc.ref));
                batch.delete(roomDoc.ref);
                
                await batch.commit();
                deletedCount++;
            }
            
            console.log(`✅ ${deletedCount} salas removidas`);
        } catch (error) {
            console.error('❌ Erro:', error);
        }
        return null;
    });

// ============================================
// 4. FUNÇÃO: ATUALIZAR RANKING
// ============================================
exports.onScoreUpdate = functions.firestore
    .document('rooms/{roomId}/scores/{playerId}')
    .onWrite(async (change, context) => {
        const { roomId } = context.params;
        
        const scoresSnapshot = await db.collection('rooms')
            .doc(roomId)
            .collection('scores')
            .orderBy('totalScore', 'desc')
            .limit(10)
            .get();
        
        const ranking = [];
        scoresSnapshot.forEach(doc => {
            ranking.push({
                playerId: doc.id,
                playerName: doc.data().playerName,
                avatar: doc.data().avatar,
                totalScore: doc.data().totalScore
            });
        });
        
        await db.collection('rooms').doc(roomId).update({
            ranking: ranking,
            lastRankingUpdate: admin.firestore.FieldValue.serverTimestamp()
        });
        
        return null;
    });

// ============================================
// 5. FUNÇÃO: PREVENIR RESPOSTAS DUPLICADAS
// ============================================
exports.preventDuplicateAnswers = functions.firestore
    .document('rooms/{roomId}/answers/{answerId}')
    .onCreate(async (snap, context) => {
        const { roomId } = context.params;
        const answerData = snap.data();
        
        const existingAnswers = await db.collection('rooms')
            .doc(roomId)
            .collection('answers')
            .where('playerId', '==', answerData.playerId)
            .where('questionIndex', '==', answerData.questionIndex)
            .get();
        
        if (existingAnswers.size > 1) {
            const answers = existingAnswers.docs;
            answers.sort((a, b) => {
                const aTime = a.data().timestamp?.toDate() || new Date(0);
                const bTime = b.data().timestamp?.toDate() || new Date(0);
                return aTime - bTime;
            });
            
            for (let i = 1; i < answers.length; i++) {
                await answers[i].ref.delete();
            }
            console.log(`🗑️ Resposta duplicada removida para ${answerData.playerName}`);
        }
        return null;
    });

// ============================================
// 6. FUNÇÃO: GERAR RELATÓRIO DO QUIZ
// ============================================
exports.generateQuizReport = functions.firestore
    .document('rooms/{roomId}')
    .onUpdate(async (change, context) => {
        const { roomId } = context.params;
        const after = change.after.data();
        const before = change.before.data();
        
        if (after.status === 'finished' && before.status !== 'finished') {
            console.log(`📊 Gerando relatório para sala ${roomId}`);
            
            try {
                const scoresSnapshot = await db.collection('rooms')
                    .doc(roomId)
                    .collection('scores')
                    .orderBy('totalScore', 'desc')
                    .get();
                
                const players = [];
                scoresSnapshot.forEach(doc => {
                    players.push({
                        playerId: doc.id,
                        playerName: doc.data().playerName,
                        totalScore: doc.data().totalScore
                    });
                });
                
                const quizDoc = await db.collection('quizzes').doc(after.quizId).get();
                const quiz = quizDoc.data();
                
                await db.collection('reports').doc(roomId).set({
                    roomId: roomId,
                    quizTitle: quiz?.title || 'Quiz desconhecido',
                    quizId: after.quizId,
                    createdAt: admin.firestore.FieldValue.serverTimestamp(),
                    totalPlayers: players.length,
                    players: players,
                    finishedAt: after.endedAt || admin.firestore.FieldValue.serverTimestamp()
                });
                
                console.log(`✅ Relatório gerado! ${players.length} jogadores`);
            } catch (error) {
                console.error('❌ Erro:', error);
            }
        }
        return null;
    });

// ============================================
// 7. FUNÇÃO: NOTIFICAÇÃO DE PARTICIPAÇÃO
// ============================================
exports.notifyHighParticipation = functions.firestore
    .document('rooms/{roomId}/players/{playerId}')
    .onCreate(async (snap, context) => {
        const { roomId } = context.params;
        
        const playersSnapshot = await db.collection('rooms')
            .doc(roomId)
            .collection('players')
            .get();
        
        const playerCount = playersSnapshot.size;
        
        if (playerCount === 5 || playerCount === 10 || playerCount === 20) {
            console.log(`🎉 Sala ${roomId} atingiu ${playerCount} jogadores!`);
            
            const roomDoc = await db.collection('rooms').doc(roomId).get();
            const room = roomDoc.data();
            
            if (room) {
                console.log(`   Quiz: ${room.quizTitle}`);
                console.log(`   Total jogadores: ${playerCount}`);
            }
        }
        return null;
    });

// ============================================
// 8. FUNÇÃO: BACKUP AUTOMÁTICO (semanal)
// ============================================
exports.backupImportantQuizzes = functions.pubsub
    .schedule('0 0 * * 0')
    .timeZone('America/Sao_Paulo')
    .onRun(async () => {
        console.log('💾 Iniciando backup de quizzes...');
        
        try {
            const quizzesSnapshot = await db.collection('quizzes')
                .where('timesPlayed', '>=', 10)
                .get();
            
            const backups = [];
            for (const doc of quizzesSnapshot.docs) {
                backups.push({
                    quizId: doc.id,
                    quizData: doc.data(),
                    backedUpAt: admin.firestore.FieldValue.serverTimestamp()
                });
            }
            
            if (backups.length > 0) {
                await db.collection('backups').doc(`backup_${Date.now()}`).set({
                    quizzes: backups,
                    totalQuizzes: backups.length,
                    createdAt: admin.firestore.FieldValue.serverTimestamp()
                });
                console.log(`✅ Backup concluído! ${backups.length} quizzes salvos.`);
            } else {
                console.log('ℹ️ Nenhum quiz elegível para backup');
            }
        } catch (error) {
            console.error('❌ Erro no backup:', error);
        }
        return null;
    });

// Exportar funções adicionais para debug
exports.healthCheck = functions.https.onRequest(async (req, res) => {
    res.status(200).json({
        status: 'healthy',
        timestamp: new Date().toISOString(),
        functions: [
            'calculateScore',
            'autoFinishQuestion',
            'cleanOldRooms',
            'onScoreUpdate',
            'preventDuplicateAnswers',
            'generateQuizReport',
            'notifyHighParticipation',
            'backupImportantQuizzes'
        ]
    });
});