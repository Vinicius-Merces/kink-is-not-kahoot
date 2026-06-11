// Gera novas questões para os simulados AWS usando a API do Gemini, em lotes,
// respeitando a proporção de domínios de cada certificação/nível.
//
// As questões geradas NÃO são gravadas direto em data/exams/ — ficam em
// scripts/question-generator/output/{certId}-{level}.generated.json para
// revisão. Depois de revisar, rode merge.js para incorporá-las às pools.
//
// Uso:
//   node generate.js --dry-run                                  (mostra o plano, sem chamar a API)
//   node generate.js --certs=clf-c02 --levels=iniciante         (gera só essa pool)
//   node generate.js --target=240 --batch=10 --delay=15000      (parâmetros completos)
//
// Variáveis de ambiente (definir em .env na raiz do projeto):
//   GEMINI_API_KEY  - obrigatória (exceto em --dry-run)
//   GEMINI_MODEL    - opcional (padrão: gemini-2.5-flash)
const fs = require('fs');
const path = require('path');
require('dotenv').config({ path: path.join(__dirname, '..', '..', '.env') });

const { GoogleGenAI } = require('@google/genai');

const { listPools, loadPool, getNextSeqNumber, computePlan } = require('./lib/pools');
const { LEVEL_LABELS, ID_PREFIXES, FOCUS_TOPICS } = require('./lib/topics');
const { QUESTION_BATCH_SCHEMA, buildSystemInstruction, buildPrompt } = require('./lib/prompt');

const OUTPUT_DIR = path.join(__dirname, 'output');

function parseArgs(argv) {
    const args = {};
    for (const arg of argv) {
        const m = /^--([^=]+)(?:=(.*))?$/.exec(arg);
        if (!m) continue;
        args[m[1]] = m[2] === undefined ? true : m[2];
    }
    return args;
}

const args = parseArgs(process.argv.slice(2));

const TARGET_TOTAL = parseInt(args.target, 10) || 240;
const BATCH_SIZE = Math.max(1, parseInt(args.batch, 10) || 10);
const DELAY_MS = Math.max(0, parseInt(args.delay, 10) || 15000);
const MAX_RETRIES = Math.max(1, parseInt(args.retries, 10) || 3);
const MODEL = args.model || process.env.GEMINI_MODEL || 'gemini-2.5-flash';
const DRY_RUN = !!args['dry-run'];

const certsFilter = args.certs ? String(args.certs).split(',').map(s => s.trim()) : null;
const levelsFilter = args.levels ? String(args.levels).split(',').map(s => s.trim()) : null;
const domainsFilter = args.domains ? String(args.domains).split(',').map(s => s.trim()) : null;

let ai = null;
if (!DRY_RUN) {
    const apiKey = process.env.GEMINI_API_KEY;
    if (!apiKey) {
        console.error('❌ Defina GEMINI_API_KEY no arquivo .env na raiz do projeto (ou use --dry-run).');
        process.exit(1);
    }
    ai = new GoogleGenAI({ apiKey });
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

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

// Seleciona um subconjunto rotativo de tópicos de foco para variar os lotes
function pickFocusTopics(domainId, batchIndex, count) {
    const topics = FOCUS_TOPICS[domainId];
    if (!topics || topics.length === 0) return [];
    const size = Math.min(count, topics.length, 6);
    const start = (batchIndex * size) % topics.length;
    const picked = [];
    for (let i = 0; i < size; i++) {
        picked.push(topics[(start + i) % topics.length]);
    }
    return picked;
}

async function generateBatch(opts) {
    const systemInstruction = buildSystemInstruction(opts.certCode, opts.certName);
    const prompt = buildPrompt(opts);

    for (let attempt = 1; attempt <= MAX_RETRIES; attempt++) {
        try {
            const response = await ai.models.generateContent({
                model: MODEL,
                contents: prompt,
                config: {
                    systemInstruction,
                    temperature: 0.4,
                    responseMimeType: 'application/json',
                    responseSchema: QUESTION_BATCH_SCHEMA
                }
            });

            const data = JSON.parse(response.text);
            const valid = validateQuestions(data.questions);
            if (valid.length === 0) throw new Error('Nenhuma questão válida retornada pelo modelo');
            return valid;
        } catch (error) {
            console.error(`     ⚠️ tentativa ${attempt}/${MAX_RETRIES} falhou: ${error.message}`);
            if (attempt < MAX_RETRIES) await sleep(DELAY_MS);
        }
    }

    console.error('     ❌ desistindo deste lote.');
    return [];
}

function loadStaged(stagedPath, pool, certId, level) {
    if (fs.existsSync(stagedPath)) {
        return JSON.parse(fs.readFileSync(stagedPath, 'utf-8'));
    }
    return { certId, level, certCode: pool.certCode, certName: pool.certName, questions: [] };
}

function saveStaged(stagedPath, staged) {
    fs.writeFileSync(stagedPath, JSON.stringify(staged, null, 2) + '\n', 'utf-8');
}

async function processPool(certId, level, filePath) {
    const pool = loadPool(filePath);
    const stagedPath = path.join(OUTPUT_DIR, `${certId}-${level}.generated.json`);
    const staged = loadStaged(stagedPath, pool, certId, level);

    const combined = [...pool.questions, ...staged.questions];
    const plan = computePlan(pool.domains, combined, TARGET_TOTAL);

    console.log(`\n=== ${pool.certCode} (${certId}) - ${level} ===`);
    console.log(`Total atual: ${pool.questions.length} | em staging: ${staged.questions.length} | meta da pool: ${TARGET_TOTAL}`);
    for (const p of plan) {
        console.log(`  ${p.domainId.padEnd(28)} meta=${p.target}  existem=${p.existingCount}  faltam=${p.needed}`);
    }

    if (DRY_RUN) return;

    const idPrefix = `${certId.slice(0, 3)}-${ID_PREFIXES[level]}`;
    let nextNum = getNextSeqNumber(combined);
    const levelLabel = LEVEL_LABELS[level] || level;

    for (const p of plan) {
        if (domainsFilter && !domainsFilter.includes(p.domainId)) continue;

        let remaining = p.needed;
        let batchIndex = 0;

        while (remaining > 0) {
            const count = Math.min(BATCH_SIZE, remaining);
            const existingTexts = combined
                .filter(q => q.domain === p.domainId)
                .map(q => q.text)
                .slice(-25);
            const focusTopics = pickFocusTopics(p.domainId, batchIndex, count);

            console.log(`  -> [${p.domainId}] gerando ${count} questões (faltam ${remaining})...`);

            const generated = await generateBatch({
                certCode: pool.certCode,
                certName: pool.certName,
                levelLabel,
                domainName: p.domainName,
                count,
                existingTexts,
                focusTopics
            });

            let added = 0;
            for (const raw of generated) {
                const converted = convertQuestion(raw, p.domainId, idPrefix, nextNum);
                if (!converted) continue;
                staged.questions.push(converted);
                combined.push(converted);
                nextNum++;
                remaining--;
                added++;
            }

            saveStaged(stagedPath, staged);
            console.log(`     +${added} válidas salvas em ${path.relative(process.cwd(), stagedPath)} (faltam ${remaining})`);

            batchIndex++;
            if (remaining > 0) await sleep(DELAY_MS);
        }
    }
}

async function main() {
    if (!fs.existsSync(OUTPUT_DIR)) fs.mkdirSync(OUTPUT_DIR, { recursive: true });

    const pools = listPools({ certsFilter, levelsFilter });
    if (pools.length === 0) {
        console.log('Nenhuma pool encontrada com os filtros informados.');
        return;
    }

    for (const { certId, level, filePath } of pools) {
        await processPool(certId, level, filePath);
    }

    console.log(DRY_RUN ? '\n✅ Plano exibido (dry-run, nada foi gerado).' : '\n✅ Concluído. Revise output/ e rode merge.js para incorporar às pools.');
}

main().catch(error => {
    console.error('❌ Erro inesperado:', error);
    process.exit(1);
});
