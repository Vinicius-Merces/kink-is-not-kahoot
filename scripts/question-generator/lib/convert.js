// Validação e conversão de questões no formato QUESTION_BATCH_SCHEMA
// (retornado pela API ou colado manualmente do chat do Gemini) para o
// formato usado em data/exams/*.json.

// Mantém apenas questões com exatamente 4 alternativas e 1 correta
function validateQuestions(list) {
    if (!Array.isArray(list)) return [];
    return list.filter(q => {
        if (!q || typeof q.question !== 'string' || !q.question.trim()) return false;
        if (!Array.isArray(q.answerOptions) || q.answerOptions.length !== 4) return false;
        const correctCount = q.answerOptions.filter(o => o && o.isCorrect === true).length;
        if (correctCount !== 1) return false;
        if (q.answerOptions.some(o => !o.text || !o.rationale)) return false;
        return true;
    });
}

// Converte o formato retornado pelo Gemini para o formato usado em data/exams/*.json
function convertQuestion(raw, domainId, idPrefix, seqNumber) {
    const correctIndex = raw.answerOptions.findIndex(o => o.isCorrect === true);
    if (correctIndex === -1) return null;

    return {
        id: `${idPrefix}-${String(seqNumber).padStart(3, '0')}`,
        domain: domainId,
        text: raw.question.trim(),
        options: raw.answerOptions.map(o => o.text.trim()),
        correct: correctIndex,
        explanation: raw.answerOptions[correctIndex].rationale.trim(),
        hint: (raw.hint || '').trim(),
        optionRationales: raw.answerOptions.map(o => (o.rationale || '').trim())
    };
}

module.exports = { validateQuestions, convertQuestion };
