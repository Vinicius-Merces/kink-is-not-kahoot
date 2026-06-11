// Importa um lote de questões geradas MANUALMENTE (copiado/colado do chat
// web do Gemini, ver show-prompt.js) para o mesmo arquivo de staging usado
// por generate.js, para depois rodar merge.js normalmente.
//
// Uso:
//   node import.js --certs=clf-c02 --levels=avancado --domain=cloud-concepts --file=resposta.json
//   (ou sem --file, cole o JSON via stdin e finalize com Ctrl+Z + Enter no Windows)
const fs = require('fs');
const path = require('path');

const { listPools, loadPool, getNextSeqNumber, computePlan } = require('./lib/pools');
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

function readStdin() {
    return new Promise((resolve, reject) => {
        let data = '';
        process.stdin.setEncoding('utf-8');
        process.stdin.on('data', chunk => { data += chunk; });
        process.stdin.on('end', () => resolve(data));
        process.stdin.on('error', reject);
    });
}

// O Gemini às vezes envolve o JSON em ```json ... ``` mesmo quando pedimos
// para não fazer isso - removemos essa cerca antes de fazer o parse.
function stripCodeFence(text) {
    const trimmed = text.trim();
    const m = /^```(?:json)?\s*([\s\S]*?)\s*```$/.exec(trimmed);
    return m ? m[1] : trimmed;
}

async function main() {
    const args = parseArgs(process.argv.slice(2));

    if (!args.certs || !args.levels || !args.domain) {
        console.error('Uso: node import.js --certs=<certId> --levels=<level> --domain=<domainId> --file=<resposta.json>');
        process.exit(1);
    }

    const raw = args.file
        ? fs.readFileSync(args.file, 'utf-8')
        : await readStdin();

    let parsed;
    try {
        parsed = JSON.parse(stripCodeFence(raw));
    } catch (error) {
        console.error('❌ Não foi possível interpretar o JSON colado:', error.message);
        process.exit(1);
    }

    const rawQuestions = Array.isArray(parsed) ? parsed : parsed.questions;
    const valid = validateQuestions(rawQuestions);
    const invalidCount = (Array.isArray(rawQuestions) ? rawQuestions.length : 0) - valid.length;

    if (valid.length === 0) {
        console.error('❌ Nenhuma questão válida encontrada no JSON colado (verifique o formato).');
        process.exit(1);
    }

    const [poolInfo] = listPools({ certsFilter: [args.certs], levelsFilter: [args.levels] });
    if (!poolInfo) {
        console.error(`Pool não encontrada para certs=${args.certs} levels=${args.levels}`);
        process.exit(1);
    }
    const pool = loadPool(poolInfo.filePath);

    if (!fs.existsSync(OUTPUT_DIR)) fs.mkdirSync(OUTPUT_DIR, { recursive: true });
    const stagedPath = path.join(OUTPUT_DIR, `${args.certs}-${args.levels}.generated.json`);
    const staged = fs.existsSync(stagedPath)
        ? JSON.parse(fs.readFileSync(stagedPath, 'utf-8'))
        : { certId: args.certs, level: args.levels, certCode: pool.certCode, certName: pool.certName, questions: [] };

    const combined = [...pool.questions, ...staged.questions];

    const certPrefix = args.certs.slice(0, 3);
    const levelPrefix = { iniciante: 'ini', medio: 'med', avancado: 'avc' }[args.levels] || args.levels.slice(0, 3);
    const idPrefix = `${certPrefix}-${levelPrefix}`;
    let nextNum = getNextSeqNumber(combined);

    let added = 0;
    for (const rawQ of valid) {
        const converted = convertQuestion(rawQ, args.domain, idPrefix, nextNum);
        if (!converted) continue;
        staged.questions.push(converted);
        combined.push(converted);
        nextNum++;
        added++;
    }

    fs.writeFileSync(stagedPath, JSON.stringify(staged, null, 2) + '\n', 'utf-8');

    console.log(`✅ ${added} questões importadas para ${path.relative(process.cwd(), stagedPath)}`);
    if (invalidCount > 0) console.log(`⚠️  ${invalidCount} questões do JSON colado foram ignoradas (formato inválido).`);

    const plan = computePlan(pool.domains, combined, parseInt(args.target, 10) || 240);
    const domainPlan = plan.find(p => p.domainId === args.domain);
    if (domainPlan) {
        console.log(`   [${args.domain}] meta=${domainPlan.target}  existem=${domainPlan.existingCount}  faltam=${domainPlan.needed}`);
    }
}

main();
