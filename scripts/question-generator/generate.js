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
//   node generate.js --target=240 --batch=15 --delay=15000      (parâmetros completos)
//
// O plano Free do Gemini tem dois limites: por minuto (RPM) e por dia (RPD).
// O delay entre chamadas cuida do RPM. Se a API retornar "quota exceeded"
// do tipo "PerDay", o script PARA imediatamente (não adianta tentar de novo
// no mesmo dia) e pode ser retomado no dia seguinte de onde parou.
//
// Variáveis de ambiente (definir em .env na raiz do projeto):
//   GEMINI_API_KEY  - obrigatória (exceto em --dry-run)
//   GEMINI_MODEL    - opcional (padrão: gemini-2.5-flash)
const fs = require('fs');
const path = require('path');
require('dotenv').config({ path: path.join(__dirname, '..', '..', '.env') });

const { GoogleGenAI } = require('@google/genai');

const { listPools, loadPool, getNextSeqNumber, computePlan } = require('./lib/pools');
const { LEVEL_LABELS, ID_PREFIXES, pickFocusTopics } = require('./lib/topics');
const { QUESTION_BATCH_SCHEMA, buildSystemInstruction, buildPrompt } = require('./lib/prompt');
const { validateQuestions, convertQuestion } = require('./lib/convert');

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
const BATCH_SIZE = Math.max(1, parseInt(args.batch, 10) || 15);
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

// Lançado quando a cota DIÁRIA do modelo se esgota (não adianta tentar de
// novo no mesmo dia - precisa parar e retomar depois que a cota resetar).
class DailyQuotaExceededError extends Error {}

// Extrai informações úteis do erro retornado pelo SDK do Gemini:
// - retryDelaySeconds: tempo sugerido pela própria API antes de tentar de novo
// - isDailyQuota: true se o erro for de cota por DIA (RPD), não por minuto (RPM)
function parseApiError(error) {
    let parsed;
    try {
        parsed = JSON.parse(error.message);
    } catch (_) {
        return { message: error.message, retryDelaySeconds: null, isDailyQuota: false };
    }

    const err = parsed && parsed.error;
    if (!err) return { message: error.message, retryDelaySeconds: null, isDailyQuota: false };

    let retryDelaySeconds = null;
    let isDailyQuota = false;
    for (const detail of err.details || []) {
        if (detail['@type'] === 'type.googleapis.com/google.rpc.RetryInfo' && detail.retryDelay) {
            const m = /^([\d.]+)s$/.exec(detail.retryDelay);
            if (m) retryDelaySeconds = parseFloat(m[1]);
        }
        if (detail['@type'] === 'type.googleapis.com/google.rpc.QuotaFailure') {
            for (const v of detail.violations || []) {
                if (v.quotaId && /PerDay/i.test(v.quotaId)) isDailyQuota = true;
            }
        }
    }

    return { message: err.message || error.message, retryDelaySeconds, isDailyQuota };
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
                    temperature: 0.3,
                    responseMimeType: 'application/json',
                    responseSchema: QUESTION_BATCH_SCHEMA
                }
            });

            const data = JSON.parse(response.text);
            const valid = validateQuestions(data.questions);
            if (valid.length === 0) throw new Error('Nenhuma questão válida retornada pelo modelo');
            return valid;
        } catch (error) {
            const info = parseApiError(error);

            if (info.isDailyQuota) {
                throw new DailyQuotaExceededError(info.message);
            }

            console.error(`     ⚠️ tentativa ${attempt}/${MAX_RETRIES} falhou: ${info.message}`);
            if (attempt < MAX_RETRIES) {
                const wait = info.retryDelaySeconds != null
                    ? Math.ceil(info.retryDelaySeconds * 1000) + 1000
                    : DELAY_MS;
                await sleep(wait);
            }
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
        try {
            await processPool(certId, level, filePath);
        } catch (error) {
            if (error instanceof DailyQuotaExceededError) {
                console.log(`\n⏸️  Cota DIÁRIA do modelo "${MODEL}" esgotada: ${error.message}`);
                console.log('   O progresso já foi salvo em output/. A cota da Google reseta a cada 24h.');
                console.log('   Rode "node generate.js" novamente amanhã para continuar de onde parou.');
                return;
            }
            throw error;
        }
    }

    console.log(DRY_RUN ? '\n✅ Plano exibido (dry-run, nada foi gerado).' : '\n✅ Concluído. Revise output/ e rode merge.js para incorporar às pools.');
}

main().catch(error => {
    console.error('❌ Erro inesperado:', error);
    process.exit(1);
});
