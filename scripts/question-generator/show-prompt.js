// Imprime um prompt pronto para colar no chat web do Gemini (AI Studio /
// gemini.google.com), para gerar manualmente um lote de questões quando a
// cota diária da API estiver esgotada.
//
// Depois de colar o prompt no chat e copiar a resposta JSON do Gemini, use
// "node import.js" para validar e incorporar essas questões ao pipeline
// (mesmos arquivos de staging usados por generate.js / merge.js).
//
// Uso:
//   node show-prompt.js --certs=clf-c02 --levels=avancado --domain=cloud-concepts
//   node show-prompt.js --certs=clf-c02 --levels=avancado --domain=cloud-concepts --count=15
const path = require('path');

const { listPools, loadPool, computePlan } = require('./lib/pools');
const { LEVEL_LABELS, pickFocusTopics } = require('./lib/topics');
const { buildManualPrompt } = require('./lib/prompt');

const OUTPUT_DIR = path.join(__dirname, 'output');
const fs = require('fs');

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

if (!args.certs || !args.levels || !args.domain) {
    console.error('Uso: node show-prompt.js --certs=<certId> --levels=<level> --domain=<domainId> [--count=15]');
    process.exit(1);
}

const COUNT = Math.max(1, parseInt(args.count, 10) || 15);

const [pool] = listPools({ certsFilter: [args.certs], levelsFilter: [args.levels] });
if (!pool) {
    console.error(`Pool não encontrada para certs=${args.certs} levels=${args.levels}`);
    process.exit(1);
}

const data = loadPool(pool.filePath);

const stagedPath = path.join(OUTPUT_DIR, `${args.certs}-${args.levels}.generated.json`);
const stagedQuestions = fs.existsSync(stagedPath)
    ? JSON.parse(fs.readFileSync(stagedPath, 'utf-8')).questions
    : [];

const combined = [...data.questions, ...stagedQuestions];

const plan = computePlan(data.domains, combined, parseInt(args.target, 10) || 240);
const domainPlan = plan.find(p => p.domainId === args.domain);
if (!domainPlan) {
    console.error(`Domínio "${args.domain}" não encontrado. Domínios disponíveis: ${plan.map(p => p.domainId).join(', ')}`);
    process.exit(1);
}

const existingForDomain = combined.filter(q => q.domain === args.domain);
const existingTexts = existingForDomain.map(q => q.text).slice(-25);
const batchIndex = Math.floor(existingForDomain.length / COUNT);
const count = Math.min(COUNT, Math.max(1, domainPlan.needed));
const focusTopics = pickFocusTopics(args.domain, batchIndex, count);

const manualPrompt = buildManualPrompt({
    certCode: data.certCode,
    certName: data.certName,
    levelLabel: LEVEL_LABELS[args.levels] || args.levels,
    domainName: domainPlan.domainName,
    count,
    existingTexts,
    focusTopics
});

console.log(`# ${data.certCode} - ${args.levels} - ${domainPlan.domainName}`);
console.log(`# meta=${domainPlan.target}  existem=${domainPlan.existingCount}  faltam=${domainPlan.needed}  pedindo=${count}`);
console.log('# Cole o prompt abaixo no chat do Gemini (aistudio.google.com ou gemini.google.com).');
console.log('# Depois, salve a resposta JSON em um arquivo e rode:');
console.log(`#   node import.js --certs=${args.certs} --levels=${args.levels} --domain=${args.domain} --file=resposta.json`);
console.log('');
console.log('================ PROMPT (copiar a partir daqui) ================');
console.log(manualPrompt);
console.log('================ FIM DO PROMPT ================');
