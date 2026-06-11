// Schema de resposta e construção dos prompts enviados ao Gemini
const { Type } = require('@google/genai');

// Schema de UM lote de questões. O modelo (cert/nível/domínio) e a numeração
// final dos IDs são controlados pelo script, não pelo Gemini.
const QUESTION_BATCH_SCHEMA = {
    type: Type.OBJECT,
    properties: {
        questions: {
            type: Type.ARRAY,
            items: {
                type: Type.OBJECT,
                properties: {
                    question: { type: Type.STRING },
                    answerOptions: {
                        type: Type.ARRAY,
                        items: {
                            type: Type.OBJECT,
                            properties: {
                                text: { type: Type.STRING },
                                rationale: { type: Type.STRING },
                                isCorrect: { type: Type.BOOLEAN }
                            },
                            required: ['text', 'rationale', 'isCorrect']
                        }
                    },
                    hint: { type: Type.STRING }
                },
                required: ['question', 'answerOptions', 'hint']
            }
        }
    },
    required: ['questions']
};

function buildSystemInstruction(certCode, certName) {
    return [
        'Você é um Engenheiro de IA e Arquiteto de Soluções AWS, especialista em educação técnica e em exames de certificação.',
        `Seu papel é gerar questões de múltipla escolha INÉDITAS, tecnicamente precisas e atualizadas para simulados da certificação ${certName} (${certCode}).`,
        '',
        'Regras obrigatórias para CADA questão:',
        '1. O enunciado ("question") deve ser claro, em português do Brasil, e sempre que fizer sentido apresentar um cenário realista de negócio ou de arquitetura.',
        '2. Devem existir EXATAMENTE 4 alternativas em "answerOptions", sendo apenas UMA com "isCorrect": true.',
        '3. As alternativas incorretas ("distratores") devem citar serviços ou conceitos REAIS da AWS, plausíveis e com nomes/escopos parecidos ao da resposta correta, exigindo compreensão real e não decoreba.',
        '4. Cada alternativa (correta ou incorreta) deve ter uma "rationale" própria, explicando tecnicamente por que ela está certa ou por que está errada.',
        '5. O campo "hint" deve trazer uma dica curta (1 frase) que ajude o aluno a raciocinar sobre o tema, sem entregar a resposta.',
        '6. Não repita o tema central de nenhuma questão já existente informada no prompt.',
        '7. Use nomenclatura oficial e atualizada dos serviços AWS.',
        '',
        'Responda SOMENTE em JSON, seguindo rigorosamente o schema fornecido.'
    ].join('\n');
}

function buildPrompt({ certName, certCode, levelLabel, domainName, count, existingTexts, focusTopics }) {
    const lines = [];
    lines.push(`Gere exatamente ${count} questões INÉDITAS de múltipla escolha para um simulado da certificação ${certName} (${certCode}).`);
    lines.push(`Nível de dificuldade: ${levelLabel}.`);
    lines.push(`Domínio do exame: "${domainName}".`);

    if (focusTopics && focusTopics.length > 0) {
        lines.push('');
        lines.push('Para variar os temas, distribua as questões entre os tópicos abaixo (não precisa usar todos, nem nessa ordem, e pode combinar mais de um por questão quando fizer sentido):');
        for (const topic of focusTopics) lines.push(`- ${topic}`);
    }

    if (existingTexts && existingTexts.length > 0) {
        lines.push('');
        lines.push('As questões a seguir JÁ EXISTEM no banco. NÃO crie novas questões com o mesmo tema central, cenário ou pergunta-chave delas (mas pode abordar o mesmo serviço sob outro ângulo):');
        existingTexts.forEach((t, i) => lines.push(`${i + 1}. ${t}`));
    }

    return lines.join('\n');
}

module.exports = { QUESTION_BATCH_SCHEMA, buildSystemInstruction, buildPrompt };
